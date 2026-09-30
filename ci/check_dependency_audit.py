#!/usr/bin/env python3
"""Enforce a complete strict audit with one explicit, expiring product disposition.

The raw pip-audit report remains unchanged. NLTK itself is still vulnerable;
this gate only records why the reviewed LexNLP API paths do not reach the
advisory's model-persistence operations.
"""

from __future__ import annotations

import argparse
from datetime import date, datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

from packaging.markers import default_environment
from packaging.requirements import Requirement
from packaging.utils import canonicalize_name


REPO_ROOT = Path(__file__).resolve().parents[1]
KNOWN_IDS = frozenset({"GHSA-8mgp-746c-j5xp", "CVE-2026-81726", "PYSEC-2026-3740"})


class AuditGateError(ValueError):
    """The report is incomplete or an applicable finding lacks a disposition."""


def source_sha256(repository: Path) -> str:
    """Bind the reachability review to all shipped and operational Python code."""
    digest = hashlib.sha256()
    paths = []
    for directory in ("lexnlp", "scripts"):
        root = repository / directory
        if not root.is_dir():
            raise AuditGateError(f"Missing reviewed source directory: {directory}")
        paths.extend(path for path in root.rglob("*.py") if "tests" not in path.relative_to(root).parts)
    for path in sorted(paths, key=lambda item: item.relative_to(repository).as_posix()):
        if path.is_symlink():
            raise AuditGateError(f"Reviewed source cannot be a symlink: {path}")
        digest.update(path.relative_to(repository).as_posix().encode("utf-8") + b"\0")
        digest.update(path.read_bytes() + b"\0")
    return digest.hexdigest()


def expected_dependencies(requirements: str) -> dict[str, str]:
    """Select every pinned runtime requirement for the auditing interpreter."""
    result = {}
    environment = default_environment()
    environment["extra"] = ""
    for line in requirements.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            requirement = Requirement(line)
        except ValueError as error:
            raise AuditGateError(f"Invalid exported runtime requirement: {line}") from error
        if requirement.marker and not requirement.marker.evaluate(environment):
            continue
        specifiers = list(requirement.specifier)
        if requirement.url or requirement.extras or len(specifiers) != 1:
            raise AuditGateError(f"Runtime requirement must have one exact version: {line}")
        specifier = specifiers[0]
        if specifier.operator != "==" or "*" in specifier.version:
            raise AuditGateError(f"Runtime requirement must have one exact version: {line}")
        name = canonicalize_name(requirement.name)
        if name in result:
            raise AuditGateError(f"Duplicate active runtime requirement: {name}")
        result[name] = specifier.version
    if not result:
        raise AuditGateError("The runtime dependency export is empty")
    return result


def reviewed_exception(policy: dict, repository: Path, today: date) -> dict | None:
    if not isinstance(policy, dict) or policy.get("schema_version") != 1:
        raise AuditGateError("Unsupported dependency disposition policy")
    exceptions = policy.get("exceptions")
    if not isinstance(exceptions, list) or len(exceptions) > 1:
        raise AuditGateError("Only the single reviewed NLTK advisory can have a disposition")
    if not exceptions:
        return None
    exception = exceptions[0]
    if not isinstance(exception, dict):
        raise AuditGateError("Malformed dependency disposition")
    if exception.get("package") != "nltk" or exception.get("version") != "3.10.3":
        raise AuditGateError("Disposition is restricted to nltk==3.10.3")
    ids = exception.get("advisory_ids")
    if (not isinstance(ids, list) or len(ids) != len(KNOWN_IDS)
            or not all(isinstance(item, str) for item in ids) or set(ids) != KNOWN_IDS):
        raise AuditGateError("Disposition must identify exactly the reviewed advisory and aliases")
    if exception.get("dependency_is_vulnerable") is not True:
        raise AuditGateError("Disposition must acknowledge the vulnerable dependency")
    if exception.get("justification") != "vulnerable_code_not_in_execute_path":
        raise AuditGateError("Unsupported applicability justification")
    try:
        reviewed = date.fromisoformat(exception["reviewed_on"])
        expires = date.fromisoformat(exception["expires_on"])
    except (KeyError, TypeError, ValueError) as error:
        raise AuditGateError("Missing or malformed disposition dates") from error
    if reviewed > today or not 0 < (expires - reviewed).days <= 30 or today >= expires:
        raise AuditGateError(f"Disposition is expired or outside its 30-day review window: {expires}")
    if exception.get("source_sha256") != source_sha256(repository):
        raise AuditGateError("LexNLP runtime/tool source changed; the applicability review must be renewed")
    if not isinstance(exception.get("description_sha256"), str) or len(exception["description_sha256"]) != 64:
        raise AuditGateError("Disposition must bind the reviewed advisory description")
    for field in ("scope", "residual_risk"):
        if not isinstance(exception.get(field), str) or not exception[field].strip():
            raise AuditGateError(f"Disposition lacks its reviewed {field}")
    evidence = exception.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        raise AuditGateError("Disposition lacks its reviewed evidence")
    for item in evidence:
        if (not isinstance(item, dict)
                or not all(isinstance(item.get(key), str) and item[key] for key in ("path", "detail"))):
            raise AuditGateError("Malformed applicability evidence")
        path = Path(item["path"])
        if path.is_absolute() or ".." in path.parts or not (repository / path).is_file():
            raise AuditGateError("Applicability evidence must refer to an existing repository file")
    return exception


def evaluate(report: dict, audit_exit_code: int, requirements: str, policy: dict,
             repository: Path, today: date | None = None) -> dict:
    """Fail closed on collection failures, changed code, and all other findings."""
    if type(audit_exit_code) is not int or audit_exit_code not in (0, 1):
        raise AuditGateError(f"Strict pip-audit did not complete normally: exit {audit_exit_code}")
    if not isinstance(report, dict) or set(report) != {"dependencies", "fixes"}:
        raise AuditGateError("Missing or unsupported raw pip-audit report")
    if not isinstance(report["dependencies"], list) or not isinstance(report["fixes"], list) or report["fixes"]:
        raise AuditGateError("Malformed audit report or unexpected automatic fixes")
    expected = expected_dependencies(requirements)
    exception = reviewed_exception(policy, repository, today or datetime.now(timezone.utc).date())
    actual = {}
    findings = []
    for dependency in report["dependencies"]:
        if not isinstance(dependency, dict) or "skip_reason" in dependency:
            raise AuditGateError("Strict audit skipped or failed to collect a dependency")
        if not all(isinstance(dependency.get(key), str) and dependency[key] for key in ("name", "version")):
            raise AuditGateError("Malformed audited dependency")
        name = canonicalize_name(dependency["name"])
        if name in actual:
            raise AuditGateError(f"Duplicate audited dependency: {name}")
        actual[name] = dependency["version"]
        vulnerabilities = dependency.get("vulns")
        if not isinstance(vulnerabilities, list):
            raise AuditGateError(f"Missing vulnerability results for {name}")
        for vulnerability in vulnerabilities:
            if not isinstance(vulnerability, dict) or not isinstance(vulnerability.get("id"), str):
                raise AuditGateError(f"Malformed vulnerability for {name}")
            aliases = vulnerability.get("aliases")
            fixes = vulnerability.get("fix_versions")
            description = vulnerability.get("description")
            if not isinstance(aliases, list) or not all(isinstance(item, str) for item in aliases):
                raise AuditGateError(f"Missing or malformed advisory aliases for {name}")
            if not isinstance(fixes, list) or not all(isinstance(item, str) for item in fixes):
                raise AuditGateError(f"Missing or malformed advisory fixes for {name}")
            identifiers = {vulnerability["id"], *aliases}
            if (not exception or name != exception["package"] or dependency["version"] != exception["version"]
                    or not identifiers <= KNOWN_IDS):
                raise AuditGateError(f"Unreviewed dependency vulnerability: {name} {vulnerability['id']}")
            if fixes:
                raise AuditGateError("A patched NLTK version is now available; upgrade instead of using the disposition")
            if (not isinstance(description, str)
                    or hashlib.sha256(description.encode("utf-8")).hexdigest() != exception["description_sha256"]):
                raise AuditGateError("Advisory description changed; its applicability must be reviewed again")
            findings.append({"package": name, "version": dependency["version"], "advisory": vulnerability["id"],
                             "expires_on": exception["expires_on"], "dependency_is_vulnerable": True})
    if actual != expected:
        raise AuditGateError("Raw audit dependency coverage/version differs from the active locked runtime export")
    if exception and actual.get("nltk") != exception["version"]:
        raise AuditGateError("NLTK version changed; remove or renew the exact-version disposition")
    if len(findings) > 1:
        raise AuditGateError("The raw audit contains duplicate or additional findings")
    if audit_exit_code != int(bool(findings)):
        raise AuditGateError("Strict audit exit code disagrees with its complete finding report")
    return {"status": "passed_with_reviewed_product_disposition" if findings else "passed",
            "audited_dependencies": len(actual), "known_vulnerable_dependencies": findings}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit-json", type=Path, required=True)
    parser.add_argument("--audit-exit-code-file", type=Path, required=True)
    parser.add_argument("--requirements", type=Path, required=True)
    parser.add_argument("--policy", type=Path, default=REPO_ROOT / "ci/dependency_audit_exceptions.json")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        result = evaluate(json.loads(args.audit_json.read_text(encoding="utf-8")),
                          int(args.audit_exit_code_file.read_text(encoding="ascii").strip()),
                          args.requirements.read_text(encoding="utf-8"),
                          json.loads(args.policy.read_text(encoding="utf-8")), REPO_ROOT)
    except (OSError, ValueError) as error:
        print(f"Dependency audit gate FAILED: {error}", file=sys.stderr)
        return 1
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"Dependency audit gate: {result['audited_dependencies']} locked runtime dependencies audited")
    for finding in result["known_vulnerable_dependencies"]:
        print(f"KNOWN VULNERABLE DEPENDENCY: {finding['package']}=={finding['version']} {finding['advisory']}; "
              f"reviewed non-applicability to LexNLP API paths expires {finding['expires_on']}. "
              f"Full strict audit finding remains in {args.audit_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
