"""The dependency audit must fail closed without concealing its raw finding."""

from copy import deepcopy
from datetime import date
import hashlib
import json
from pathlib import Path

import pytest

from ci import check_dependency_audit as gate


@pytest.fixture
def audit_case(tmp_path):
    for directory in ("lexnlp", "scripts"):
        (tmp_path / directory).mkdir()
    (tmp_path / "lexnlp" / "example.py").write_text("def extract(text):\n    return text\n")
    description = "Caller-controlled model persistence bypasses the NLTK file sandbox."
    report = {"dependencies": [
        {"name": "nltk", "version": "3.10.3", "vulns": [{
            "id": "PYSEC-2026-3740", "aliases": ["GHSA-8mgp-746c-j5xp", "CVE-2026-81726"],
            "fix_versions": [], "description": description,
        }]},
        {"name": "requests", "version": "2.34.2", "vulns": []},
    ], "fixes": []}
    policy = {"schema_version": 1, "exceptions": [{
        "package": "nltk", "version": "3.10.3", "advisory_ids": sorted(gate.KNOWN_IDS),
        "dependency_is_vulnerable": True, "justification": "vulnerable_code_not_in_execute_path",
        "reviewed_on": "2026-09-30", "expires_on": "2026-10-30",
        "source_sha256": gate.source_sha256(tmp_path),
        "description_sha256": hashlib.sha256(description.encode()).hexdigest(),
        "scope": "Reviewed extraction API paths", "residual_risk": "Direct NLTK persistence remains vulnerable",
        "evidence": [{"path": "lexnlp/example.py", "detail": "Text inference only"}],
    }]}
    return report, policy, tmp_path


def check(case, exit_code=1, requirements="nltk==3.10.3\nrequests==2.34.2\n", today=date(2026, 9, 30)):
    report, policy, root = case
    return gate.evaluate(report, exit_code, requirements, policy, root, today)


@pytest.mark.parametrize("identifier", sorted(gate.KNOWN_IDS))
def test_exact_disposition_recognizes_each_advisory_alias_and_preserves_raw_report(audit_case, identifier):
    report, _policy, _root = audit_case
    report["dependencies"][0]["vulns"][0]["id"] = identifier
    original = deepcopy(report)
    result = check(audit_case)
    assert result["status"] == "passed_with_reviewed_product_disposition"
    assert result["known_vulnerable_dependencies"][0]["dependency_is_vulnerable"] is True
    assert report == original


def test_clean_complete_report_passes_without_a_disposition(audit_case):
    report, policy, _root = audit_case
    report["dependencies"][0]["vulns"] = []
    policy["exceptions"] = []
    assert check(audit_case, exit_code=0)["known_vulnerable_dependencies"] == []


@pytest.mark.parametrize("mutation", [
    lambda report: report["dependencies"].pop(),
    lambda report: report["dependencies"].append(deepcopy(report["dependencies"][0])),
    lambda report: report["dependencies"][1].update(skip_reason="PyPI API unavailable"),
    lambda report: report["dependencies"][1].pop("vulns"),
    lambda report: report["dependencies"][1].update(version="2.34.1"),
    lambda report: report.update(fixes=[{"name": "nltk"}]),
    lambda report: report.pop("dependencies"),
    lambda report: report.update(error="API request failed"),
])
def test_partial_skipped_malformed_or_mismatched_audits_fail(audit_case, mutation):
    mutation(audit_case[0])
    with pytest.raises(gate.AuditGateError):
        check(audit_case)


@pytest.mark.parametrize("dependency, change", [
    (0, {"id": "GHSA-different-finding"}),
    (0, {"aliases": ["GHSA-different-finding"]}),
    (0, {"fix_versions": ["3.10.4"]}),
    (0, {"description": "A revised advisory now affects inference."}),
    (0, {"aliases": "GHSA-8mgp-746c-j5xp"}),
    (0, {"fix_versions": None}),
    (1, {"id": "GHSA-8mgp-746c-j5xp"}),
])
def test_other_findings_changed_scope_and_available_fixes_fail(audit_case, dependency, change):
    report = audit_case[0]
    if dependency == 1:
        report["dependencies"][1]["vulns"] = [deepcopy(report["dependencies"][0]["vulns"][0])]
    report["dependencies"][dependency]["vulns"][0].update(change)
    with pytest.raises(gate.AuditGateError):
        check(audit_case)


def test_duplicate_findings_are_not_silently_disposed(audit_case):
    vulnerabilities = audit_case[0]["dependencies"][0]["vulns"]
    vulnerabilities.append(deepcopy(vulnerabilities[0]))
    with pytest.raises(gate.AuditGateError):
        check(audit_case)


@pytest.mark.parametrize("exit_code", [0, 2, -1, True])
def test_network_collection_failures_and_inconsistent_status_fail(audit_case, exit_code):
    with pytest.raises(gate.AuditGateError):
        check(audit_case, exit_code=exit_code)


@pytest.mark.parametrize("change", [
    {"package": "other-package"}, {"version": "3.10.2"},
    {"dependency_is_vulnerable": False}, {"justification": "ignore"},
    {"reviewed_on": "2026-10-01"}, {"expires_on": "2026-12-30"},
    {"advisory_ids": ["GHSA-other"]}, {"expires_on": "not-a-date"},
    {"description_sha256": ""},
    {"advisory_ids": sorted(gate.KNOWN_IDS) + ["GHSA-8mgp-746c-j5xp"]},
    {"scope": []}, {"residual_risk": True}, {"evidence": "trust me"},
    {"evidence": [{"path": "missing.py", "detail": "Not inspected"}]},
])
def test_policy_cannot_widen_identity_scope_or_review_window(audit_case, change):
    audit_case[1]["exceptions"][0].update(change)
    with pytest.raises(gate.AuditGateError):
        check(audit_case)


def test_disposition_expires_at_start_of_expiry_date(audit_case):
    with pytest.raises(gate.AuditGateError, match="expired"):
        check(audit_case, today=date(2026, 10, 30))


def test_new_or_changed_runtime_code_requires_new_reachability_review(audit_case):
    (audit_case[2] / "lexnlp" / "new.py").write_text("from nltk.parse import TransitionParser\n")
    with pytest.raises(gate.AuditGateError, match="source changed"):
        check(audit_case)


def test_new_nltk_version_requires_retiring_old_disposition(audit_case):
    audit_case[0]["dependencies"][0].update(version="3.10.4", vulns=[])
    with pytest.raises(gate.AuditGateError, match="version changed"):
        check(audit_case, exit_code=0, requirements="nltk==3.10.4\nrequests==2.34.2\n")


def test_requirement_markers_select_exact_auditing_interpreter_inventory():
    requirements = "nltk==3.10.3\nrequests==2.34.2; python_version >= '3.10'\nold==1; python_version < '3'\n"
    assert gate.expected_dependencies(requirements) == {"nltk": "3.10.3", "requests": "2.34.2"}


@pytest.mark.parametrize("requirements", ["", "nltk>=3.10.3", "nltk==3.*", "nltk==3.10.3\nnltk==3.10.3"])
def test_empty_or_non_exact_dependency_exports_fail(requirements):
    with pytest.raises(gate.AuditGateError):
        gate.expected_dependencies(requirements)


@pytest.mark.parametrize("contents", [None, "not json", '{"dependencies": []}'])
def test_missing_or_malformed_raw_report_fails_cli(tmp_path: Path, contents):
    report = tmp_path / "report.json"
    if contents is not None:
        report.write_text(contents)
    status = tmp_path / "status.txt"
    status.write_text("1\n")
    requirements = tmp_path / "requirements.txt"
    requirements.write_text("nltk==3.10.3\n")
    policy = tmp_path / "policy.json"
    policy.write_text(json.dumps({"schema_version": 1, "exceptions": []}))
    assert gate.main(["--audit-json", str(report), "--audit-exit-code-file", str(status),
                      "--requirements", str(requirements), "--policy", str(policy)]) == 1
