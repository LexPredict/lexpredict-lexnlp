#!/usr/bin/env python3
"""Audit pytest skip markers.

Policy:
- New pytest skip markers must include a nearby annotation:
  `skip-audit: issue=... expires=YYYY-MM-DD`
- Existing markers can be grandfathered via an allowlist file.
"""

from __future__ import annotations

import argparse
import ast
import datetime as dt
import hashlib
import re
import subprocess
import sys
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Set, Tuple

ANNOTATION_RE = re.compile(
    r"skip-audit:\s*issue=(?P<issue>\S+)\s+expires=(?P<expires>\d{4}-\d{2}-\d{2})"
)
MARKER_NAMES = {"skip", "skipif", "xfail"}
LOOKBACK_LINES = 2


@dataclass(frozen=True)
class Marker:
    path: Path
    line: int
    col: int
    kind: str
    expression: str

    @property
    def key(self) -> str:
        # Legacy allowlist key (deprecated): line-number based.
        return f"{self.path.as_posix()}:{self.line}:{self.kind}"

    @property
    def stable_key(self) -> str:
        # Stable allowlist key: resilient to line movements and formatting changes
        # outside the marker expression itself.
        digest = hashlib.sha256(self.expression.encode("utf-8")).hexdigest()[:12]
        return f"{self.path.as_posix()}:{self.kind}:sha256={digest}"


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fail if unapproved pytest skip markers are present."
    )
    script_path = Path(__file__).resolve()
    default_repo_root = script_path.parent.parent
    parser.add_argument(
        "--repo-root",
        default=str(default_repo_root),
        help="Repository root path (default: %(default)s)",
    )
    parser.add_argument(
        "--allowlist",
        default="ci/skip_audit_allowlist.txt",
        help="Allowlist path (relative to repo root unless absolute).",
    )
    parser.add_argument(
        "--print-markers",
        action="store_true",
        help="Print detected skip markers and exit (useful for allowlisting).",
    )
    return parser.parse_args(argv)


def marker_kind(node: ast.AST) -> Optional[str]:
    if not isinstance(node, ast.Attribute):
        return None
    if node.attr not in MARKER_NAMES:
        return None
    mark_parent = node.value
    if (
        isinstance(mark_parent, ast.Attribute)
        and mark_parent.attr == "mark"
        and isinstance(mark_parent.value, ast.Name)
        and mark_parent.value.id == "pytest"
    ):
        return node.attr
    return None


def list_python_files(repo_root: Path) -> List[Path]:
    try:
        result = subprocess.run(
            ["git", "ls-files", "*.py"],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return sorted(path for path in repo_root.rglob("*.py") if ".git" not in path.parts)

    files = []
    for line in result.stdout.splitlines():
        relative_path = line.strip()
        if not relative_path:
            continue
        files.append(repo_root / relative_path)
    return sorted(files)


def collect_markers(repo_root: Path) -> Tuple[List[Marker], List[str]]:
    markers: List[Marker] = []
    parse_errors: List[str] = []

    for file_path in list_python_files(repo_root):
        relative_path = file_path.relative_to(repo_root)
        try:
            source = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            parse_errors.append(
                f"{relative_path.as_posix()}: failed to decode as UTF-8 ({exc})"
            )
            continue

        try:
            with warnings.catch_warnings():
                # Older files can emit parser-level invalid escape warnings;
                # they are unrelated to skip marker policy and should not fail the audit.
                warnings.simplefilter("ignore", SyntaxWarning)
                tree = ast.parse(source, filename=str(relative_path))
        except SyntaxError as exc:
            parse_errors.append(
                f"{relative_path.as_posix()}:{exc.lineno}: syntax error while parsing ({exc.msg})"
            )
            continue

        parents: Dict[int, ast.AST] = {}
        for parent in ast.walk(tree):
            for child in ast.iter_child_nodes(parent):
                parents[id(child)] = parent

        seen: Set[Tuple[int, int, str]] = set()
        for node in ast.walk(tree):
            kind: Optional[str] = None
            if isinstance(node, ast.Call):
                kind = marker_kind(node.func)
            elif isinstance(node, ast.Attribute):
                kind = marker_kind(node)
                parent = parents.get(id(node))
                if isinstance(parent, ast.Call) and parent.func is node:
                    kind = None

            if kind is None:
                continue

            key = (node.lineno, node.col_offset, kind)
            if key in seen:
                continue
            seen.add(key)

            expression = ast.get_source_segment(source, node) or kind
            markers.append(
                Marker(
                    path=relative_path,
                    line=node.lineno,
                    col=node.col_offset,
                    kind=kind,
                    expression=" ".join(expression.split()),
                )
            )

    markers.sort(key=lambda marker: (marker.path.as_posix(), marker.line, marker.col))
    return markers, parse_errors


def load_allowlist(allowlist_path: Path) -> Set[str]:
    if not allowlist_path.exists():
        return set()
    entries: Set[str] = set()
    for raw_line in allowlist_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        entries.add(line)
    return entries


def find_annotation(lines: Sequence[str], marker_line: int) -> Optional[re.Match[str]]:
    start = max(1, marker_line - LOOKBACK_LINES)
    for line_number in range(marker_line, start - 1, -1):
        line = lines[line_number - 1]
        match = ANNOTATION_RE.search(line)
        if match:
            return match
    return None


def main(argv: Sequence[str]) -> int:
    args = parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    allowlist_path = Path(args.allowlist)
    if not allowlist_path.is_absolute():
        allowlist_path = (repo_root / allowlist_path).resolve()

    allowlist = load_allowlist(allowlist_path)
    markers, parse_errors = collect_markers(repo_root)

    if parse_errors:
        print("skip-audit: parse errors detected", file=sys.stderr)
        for parse_error in parse_errors:
            print(f"  - {parse_error}", file=sys.stderr)
        return 1

    if args.print_markers:
        for marker in markers:
            print(f"{marker.key} stable={marker.stable_key} expr={marker.expression}")
        return 0

    files_cache: Dict[Path, List[str]] = {}
    today = dt.date.today()
    violations: List[str] = []
    allowlisted_count = 0

    for marker in markers:
        if marker.key in allowlist or marker.stable_key in allowlist:
            allowlisted_count += 1
            continue

        lines = files_cache.setdefault(
            marker.path, (repo_root / marker.path).read_text(encoding="utf-8").splitlines()
        )
        annotation_match = find_annotation(lines, marker.line)
        display_id = f"{marker.path.as_posix()}:{marker.line}:{marker.kind}"
        if annotation_match is None:
            violations.append(
                f"{display_id} missing annotation `skip-audit: issue=... expires=YYYY-MM-DD`"
            )
            continue

        expires_raw = annotation_match.group("expires")
        try:
            expires_date = dt.date.fromisoformat(expires_raw)
        except ValueError:
            violations.append(f"{display_id} has invalid expires date: {expires_raw}")
            continue

        if expires_date < today:
            violations.append(
                f"{display_id} has expired annotation (expires={expires_raw}, today={today.isoformat()})"
            )

    if violations:
        print("skip-audit: policy violations found", file=sys.stderr)
        for violation in violations:
            print(f"  - {violation}", file=sys.stderr)
        print(
            (
                "skip-audit: either add a valid annotation near each marker or update "
                f"{allowlist_path.relative_to(repo_root).as_posix()} for approved legacy markers."
            ),
            file=sys.stderr,
        )
        return 1

    print(
        "skip-audit: OK "
        f"(markers={len(markers)}, allowlisted={allowlisted_count}, "
        f"annotated_new={len(markers) - allowlisted_count})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
