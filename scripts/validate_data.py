#!/usr/bin/env python3
"""Validate resource and vehicle YAML files against JSON Schema."""

from __future__ import annotations

import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "data" / "schemas"
RESOURCES_DIR = ROOT / "data" / "resources"
VEHICLES_DIR = ROOT / "data" / "vehicles"

SKIP_NAMES = {"_index.yaml", "_template.yaml"}


def load_schema(name: str) -> dict:
    path = SCHEMAS / name
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) if path.suffix in {".yaml", ".yml"} else __import__("json").load(fh)


def build_registry() -> Registry:
    registry = Registry()
    for schema_file in SCHEMAS.glob("*.schema.json"):
        data = __import__("json").loads(schema_file.read_text(encoding="utf-8"))
        registry = registry.with_resource(
            data.get("$id", schema_file.as_uri()),
            Resource.from_contents(data, default_specification=DRAFT202012),
        )
    return registry


def iter_data_files(directory: Path):
    if not directory.exists():
        return
    for path in sorted(directory.rglob("*.yaml")):
        if path.name in SKIP_NAMES:
            continue
        yield path
    for path in sorted(directory.rglob("*.yml")):
        if path.name in SKIP_NAMES:
            continue
        yield path


def validate_file(path: Path, validator: Draft202012Validator) -> list[str]:
    errors: list[str] = []
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return [f"{path}: YAML parse error: {exc}"]
    if data is None:
        return [f"{path}: empty document"]
    if not isinstance(data, dict):
        return [f"{path}: expected mapping at root"]
    for err in sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path)):
        loc = ".".join(str(p) for p in err.absolute_path) or "<root>"
        errors.append(f"{path}: {loc}: {err.message}")
    return errors


def main() -> int:
    resource_schema = __import__("json").loads(
        (SCHEMAS / "resource.schema.json").read_text(encoding="utf-8")
    )
    vehicle_schema = __import__("json").loads(
        (SCHEMAS / "vehicle.schema.json").read_text(encoding="utf-8")
    )
    registry = build_registry()
    resource_validator = Draft202012Validator(resource_schema, registry=registry)
    vehicle_validator = Draft202012Validator(vehicle_schema, registry=registry)

    all_errors: list[str] = []
    resource_files = list(iter_data_files(RESOURCES_DIR))
    vehicle_files = list(iter_data_files(VEHICLES_DIR))

    if not resource_files and not vehicle_files:
        print("No resource/vehicle YAML files found to validate.", file=sys.stderr)
        return 1

    for path in resource_files:
        all_errors.extend(validate_file(path, resource_validator))
    for path in vehicle_files:
        all_errors.extend(validate_file(path, vehicle_validator))

    if all_errors:
        print("Validation failed:", file=sys.stderr)
        for line in all_errors:
            print(f"  - {line}", file=sys.stderr)
        return 1

    print(
        f"OK: validated {len(resource_files)} resource(s) and "
        f"{len(vehicle_files)} vehicle(s)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
