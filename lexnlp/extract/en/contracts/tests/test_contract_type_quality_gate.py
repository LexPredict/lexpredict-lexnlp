import hashlib
from pathlib import Path

import pytest

from scripts.contract_type_quality_gate import verify_fixture_sha256


def test_verify_fixture_sha256_rejects_tampering(tmp_path: Path):
    fixture = tmp_path / "fixture.csv"
    fixture.write_bytes(b"trusted")
    expected = hashlib.sha256(fixture.read_bytes()).hexdigest()
    fixture.write_bytes(b"tampered")

    with pytest.raises(ValueError, match="Fixture SHA-256 mismatch"):
        verify_fixture_sha256(fixture, expected)
