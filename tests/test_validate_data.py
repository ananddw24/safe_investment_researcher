"""Schema-validation tests: the repo's JSON Schemas accept conforming
records and reject the failure modes the guardrails care about
(unknown fields, missing provenance, off-enum values)."""

import subprocess
import sys

import pytest
import yaml
from conftest import ROOT, load_script
from jsonschema import Draft202012Validator

validate_data = load_script("validate_data")

VALID_RESOURCE = {
    "id": "us-test-resource",
    "title": "Test resource",
    "url": "https://example.gov/resource",
    "country": "US",
    "language": "en",
    "topics": ["budgeting"],
    "audience": ["general"],
    "source_type": "government-portal",
    "last_checked": "2026-10-01",
}

VALID_VEHICLE = {
    "id": "us-test-vehicle",
    "name": "Test vehicle",
    "country": "us",
    "category": "bank-deposit",
    "liquidity": "high",
    "risk_notes": "Principal in an insured deposit is protected up to the insurance limit; returns may lag inflation.",
    "literacy_angle": (
        "Explains how insured bank deposits work, what the insurance limit means, "
        "and when the money is accessible."
    ),
    "source_types": ["central-bank"],
    "status": "stub",
    "last_reviewed": "2026-10-01",
}


@pytest.fixture(scope="module")
def validators():
    registry = validate_data.build_registry()
    schemas = ROOT / "data" / "schemas"
    import json

    resource = Draft202012Validator(json.loads((schemas / "resource.schema.json").read_text()), registry=registry)
    vehicle = Draft202012Validator(json.loads((schemas / "vehicle.schema.json").read_text()), registry=registry)
    return resource, vehicle


def write_record(tmp_path, name, record):
    path = tmp_path / name
    path.write_text(yaml.safe_dump(record), encoding="utf-8")
    return path


def test_valid_records_pass(tmp_path, validators):
    resource_v, vehicle_v = validators
    assert validate_data.validate_file(write_record(tmp_path, "r.yaml", VALID_RESOURCE), resource_v) == []
    assert validate_data.validate_file(write_record(tmp_path, "v.yaml", VALID_VEHICLE), vehicle_v) == []


def test_unknown_field_rejected(tmp_path, validators):
    record = {**VALID_RESOURCE, "surprise_field": "x"}
    errors = validate_data.validate_file(write_record(tmp_path, "r.yaml", record), validators[0])
    assert errors and "surprise_field" in errors[0]


def test_missing_provenance_rejected(tmp_path, validators):
    record = {k: v for k, v in VALID_RESOURCE.items() if k != "last_checked"}
    errors = validate_data.validate_file(write_record(tmp_path, "r.yaml", record), validators[0])
    assert errors and "last_checked" in errors[0]


def test_off_enum_category_rejected(tmp_path, validators):
    record = {**VALID_VEHICLE, "category": "crypto-scheme"}
    errors = validate_data.validate_file(write_record(tmp_path, "v.yaml", record), validators[1])
    assert errors


def test_repo_data_validates_clean():
    """Smoke test: the shipped data passes the shipped validator (mirrors ci-data)."""
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "validate_data.py")],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    assert result.returncode == 0, result.stdout + result.stderr
