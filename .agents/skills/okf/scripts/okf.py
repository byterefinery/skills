#!/usr/bin/env -S uv run --script
#
# /// script
# requires-python = ">=3.10"
# dependencies = ["PyYAML", "yq"]
# ///
"""okf — Open Knowledge Format (OKF v0.2) bundle management."""

import argparse
import datetime
import os
import sys
from pathlib import Path

import yaml

# ── Known frontmatter keys ────────────────────────────────────────────

CONCEPT_KEYS = {
    # Required
    "type",
    # Recommended
    "title", "description", "resource", "tags",
    # Provenance
    "sources", "usage_window",
    # Trust
    "generated", "verified",
    # Lifecycle
    "status", "stale_after",
    # Attested Computation
    "runtime", "parameters", "computation", "executor", "attester",
}

SOURCES_ENTRY_KEYS = {
    "resource", "id", "title", "author",
    "usage_count", "last_modified", "location",
}

GENERATED_KEYS = {"by", "at"}
EXECUTOR_KEYS = {"resource", "receipt"}
ATTESTER_KEYS = {"resource"}
PARAMETER_KEYS = {"name", "type", "required"}

VALID_STATUSES = {"draft", "stable", "deprecated"}

RESERVED = {"index.md", "log.md"}


# ── Validation helpers ────────────────────────────────────────────────

def _parse_frontmatter(path):
    """Return (frontmatter_dict, body_text) or (None, error_string)."""
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as e:
        return None, f"cannot read file: {e}"

    if not text.startswith("---"):
        return None, "file does not start with '---'"

    try:
        parts = text.split("---", 2)
        # parts[0] is empty (before first ---), parts[1] is yaml, parts[2] is body
        if len(parts) < 3:
            return None, "missing closing '---' for frontmatter"
        fm = yaml.safe_load(parts[1])
        if fm is None:
            fm = {}
        return fm, parts[2]
    except yaml.YAMLError as e:
        return None, f"invalid YAML in frontmatter: {e}"


def _check_key(fm, key, required=False, expected_type=None, context=""):
    """Check a single key. Return list of (level, message) tuples."""
    issues = []
    ctx = f"{context}.{key}" if context else key

    if key not in fm:
        if required:
            issues.append(("ERROR", f"{ctx}: required field is missing"))
        return issues

    val = fm[key]
    if expected_type and not isinstance(val, expected_type):
        issues.append(("ERROR", f"{ctx}: expected {expected_type.__name__}, got {type(val).__name__}"))

    return issues


def _check_unknown_keys(fm, known, context=""):
    """Warn on unknown keys. Return list of (level, message)."""
    issues = []
    for key in fm:
        if key not in known:
            ctx = f"{context}.{key}" if context else str(key)
            issues.append(("WARN", f"{ctx}: unknown frontmatter key (allowed but not recognized)"))
    return issues


def validate_concept(path):
    """Validate a concept document. Return list of (level, message) and is_valid bool."""
    issues = []
    name = path.name

    fm, err = _parse_frontmatter(path)
    if fm is None:
        return [("ERROR", f"{name}: {err}")], False

    # Required: type
    if "type" not in fm:
        issues.append(("ERROR", f"{name}: 'type' is required"))
    elif not isinstance(fm["type"], str) or not fm["type"].strip():
        issues.append(("ERROR", f"{name}: 'type' must be a non-empty string"))

    # Recommended: title
    issues.extend(_check_key(fm, "title", expected_type=str, context=name))

    # Recommended: description
    issues.extend(_check_key(fm, "description", expected_type=str, context=name))

    # Recommended: resource
    issues.extend(_check_key(fm, "resource", expected_type=str, context=name))

    # Recommended: tags (list of strings)
    if "tags" in fm:
        if not isinstance(fm["tags"], list):
            issues.append(("ERROR", f"{name}.tags: expected list, got {type(fm['tags']).__name__}"))
        else:
            for i, t in enumerate(fm["tags"]):
                if not isinstance(t, str):
                    issues.append(("ERROR", f"{name}.tags[{i}]: expected string"))

    # Provenance: sources
    if "sources" in fm:
        src = fm["sources"]
        if not isinstance(src, list):
            issues.append(("ERROR", f"{name}.sources: expected list"))
        else:
            for i, entry in enumerate(src):
                if not isinstance(entry, dict):
                    issues.append(("ERROR", f"{name}.sources[{i}]: expected mapping"))
                    continue
                # resource required within entry
                if "resource" not in entry:
                    issues.append(("ERROR", f"{name}.sources[{i}].resource: required within sources entry"))
                elif not isinstance(entry["resource"], str):
                    issues.append(("ERROR", f"{name}.sources[{i}].resource: expected string"))
                # id
                if "id" in entry and not isinstance(entry["id"], str):
                    issues.append(("ERROR", f"{name}.sources[{i}].id: expected string"))
                # title
                if "title" in entry and not isinstance(entry["title"], str):
                    issues.append(("ERROR", f"{name}.sources[{i}].title: expected string"))
                # author
                if "author" in entry and not isinstance(entry["author"], str):
                    issues.append(("ERROR", f"{name}.sources[{i}].author: expected string"))
                # usage_count
                if "usage_count" in entry and not isinstance(entry["usage_count"], (int, float)):
                    issues.append(("ERROR", f"{name}.sources[{i}].usage_count: expected number"))
                # last_modified
                if "last_modified" in entry and not isinstance(entry["last_modified"], str):
                    issues.append(("ERROR", f"{name}.sources[{i}].last_modified: expected string (YYYY-MM-DD)"))
                # location
                if "location" in entry and not isinstance(entry["location"], dict):
                    issues.append(("ERROR", f"{name}.sources[{i}].location: expected mapping"))
                # unknown keys in sources entry
                for k in entry:
                    if k not in SOURCES_ENTRY_KEYS:
                        issues.append(("WARN", f"{name}.sources[{i}].{k}: unknown key in sources entry"))

    # usage_window
    if "usage_window" in fm:
        uw = fm["usage_window"]
        if not isinstance(uw, dict):
            issues.append(("ERROR", f"{name}.usage_window: expected mapping with 'from' and 'to'"))
        else:
            for k in ("from", "to"):
                if k in uw and not isinstance(uw[k], str):
                    issues.append(("ERROR", f"{name}.usage_window.{k}: expected string (YYYY-MM-DD)"))

    # Trust: generated
    if "generated" in fm:
        gen = fm["generated"]
        if not isinstance(gen, dict):
            issues.append(("ERROR", f"{name}.generated: expected mapping"))
        else:
            if "by" not in gen:
                issues.append(("ERROR", f"{name}.generated.by: required within 'generated'"))
            elif not isinstance(gen["by"], str):
                issues.append(("ERROR", f"{name}.generated.by: expected string (actor)"))
            if "at" in gen and not isinstance(gen["at"], (str, datetime.datetime)):
                issues.append(("ERROR", f"{name}.generated.at: expected string (ISO 8601)"))
            for k in gen:
                if k not in GENERATED_KEYS:
                    issues.append(("WARN", f"{name}.generated.{k}: unknown key"))

    # Trust: verified
    if "verified" in fm:
        ver = fm["verified"]
        # Can be a single mapping or a list
        if isinstance(ver, dict):
            ver = [ver]
        if not isinstance(ver, list):
            issues.append(("ERROR", f"{name}.verified: expected list or mapping"))
        else:
            for i, entry in enumerate(ver):
                if not isinstance(entry, dict):
                    issues.append(("ERROR", f"{name}.verified[{i}]: expected mapping"))
                    continue
                if "by" not in entry:
                    issues.append(("ERROR", f"{name}.verified[{i}].by: required within verified entry"))
                elif not isinstance(entry["by"], str):
                    issues.append(("ERROR", f"{name}.verified[{i}].by: expected string (actor)"))
                if "at" not in entry:
                    issues.append(("ERROR", f"{name}.verified[{i}].at: required within verified entry"))
                elif not isinstance(entry["at"], (str, datetime.datetime)):
                    issues.append(("ERROR", f"{name}.verified[{i}].at: expected string (ISO 8601)"))

    # Lifecycle: status
    if "status" in fm:
        if fm["status"] not in VALID_STATUSES:
            issues.append(("ERROR", f"{name}.status: must be one of {sorted(VALID_STATUSES)}, got '{fm['status']}'"))

    # Lifecycle: stale_after
    if "stale_after" in fm and not isinstance(fm["stale_after"], str):
        issues.append(("ERROR", f"{name}.stale_after: expected string (YYYY-MM-DD)"))

    # Attested Computation checks
    concept_type = fm.get("type", "")
    if concept_type == "Attested Computation":
        if "runtime" not in fm:
            issues.append(("ERROR", f"{name}.runtime: required for 'Attested Computation'"))
        elif not isinstance(fm["runtime"], str):
            issues.append(("ERROR", f"{name}.runtime: expected string"))

        # parameters
        if "parameters" in fm:
            params = fm["parameters"]
            if not isinstance(params, list):
                issues.append(("ERROR", f"{name}.parameters: expected list"))
            else:
                for i, p in enumerate(params):
                    if not isinstance(p, dict):
                        issues.append(("ERROR", f"{name}.parameters[{i}]: expected mapping"))
                        continue
                    if "name" not in p:
                        issues.append(("ERROR", f"{name}.parameters[{i}].name: required"))
                    if "type" not in p:
                        issues.append(("ERROR", f"{name}.parameters[{i}].type: required"))

        # computation
        if "computation" in fm and not isinstance(fm["computation"], str):
            issues.append(("ERROR", f"{name}.computation: expected string (path)"))

        # executor
        if "executor" in fm:
            ex = fm["executor"]
            if not isinstance(ex, dict):
                issues.append(("ERROR", f"{name}.executor: expected mapping"))
            else:
                if "resource" in ex and not isinstance(ex["resource"], str):
                    issues.append(("ERROR", f"{name}.executor.resource: expected string (path)"))
                if "receipt" in ex and not isinstance(ex["receipt"], list):
                    issues.append(("ERROR", f"{name}.executor.receipt: expected list"))
                for k in ex:
                    if k not in EXECUTOR_KEYS:
                        issues.append(("WARN", f"{name}.executor.{k}: unknown key"))

        # attester
        if "attester" in fm:
            at = fm["attester"]
            if not isinstance(at, dict):
                issues.append(("ERROR", f"{name}.attester: expected mapping"))
            else:
                if "resource" in at and not isinstance(at["resource"], str):
                    issues.append(("ERROR", f"{name}.attester.resource: expected string (path)"))
                for k in at:
                    if k not in ATTESTER_KEYS:
                        issues.append(("WARN", f"{name}.attester.{k}: unknown key"))

    # Unknown top-level keys
    issues.extend(_check_unknown_keys(fm, CONCEPT_KEYS, name))

    has_errors = any(level == "ERROR" for level, _ in issues)
    return issues, not has_errors


def validate_index(path, is_root=False):
    """Validate an index.md file. Return list of (level, message) and is_valid."""
    issues = []
    name = str(path.relative_to(path.anchor))

    text = path.read_text(encoding="utf-8")

    # index.md should have no frontmatter, except root may have okf_version
    if text.lstrip().startswith("---"):
        if is_root:
            fm, err = _parse_frontmatter(path)
            if fm is None:
                issues.append(("ERROR", f"{name}: {err}"))
                return issues, False
            # Only okf_version is permitted
            for k in fm:
                if k != "okf_version":
                    issues.append(("ERROR", f"{name}: frontmatter key '{k}' not allowed in index.md (only 'okf_version' is permitted at bundle root)"))
            if "okf_version" in fm and not isinstance(fm["okf_version"], str):
                issues.append(("ERROR", f"{name}.okf_version: expected string"))
        else:
            issues.append(("ERROR", f"{name}: index.md must not have frontmatter (only bundle-root index.md may carry 'okf_version')"))

    return issues, len([i for i in issues if i[0] == "ERROR"]) == 0


# ── CLI ───────────────────────────────────────────────────────────────

def cmd_validate(args):
    """Validate a bundle or individual files."""
    bundle = Path(args.bundle)
    if not bundle.is_dir():
        print(f"ERROR: '{args.bundle}' is not a directory", file=sys.stderr)
        return 1

    paths = args.files if args.files else []

    # If no specific files given, walk the bundle
    if not paths:
        paths = sorted(str(p.relative_to(bundle)) for p in bundle.rglob("*.md"))

    all_issues = {}  # path -> [(level, msg), ...]
    exit_code = 0

    for rel in paths:
        full = bundle / rel
        if not full.is_file():
            print(f"ERROR: {rel}: file not found")
            exit_code = 1
            continue

        name = full.name

        # log.md — skip, LLM-written
        if name == "log.md":
            all_issues[rel] = []
            continue

        # index.md — special validation
        if name == "index.md":
            is_root = (full.parent == bundle)
            issues, valid = validate_index(full, is_root=is_root)
        else:
            issues, valid = validate_concept(full)

        all_issues[rel] = issues
        if not valid:
            exit_code = 1

    # Report
    for rel in sorted(all_issues):
        issues = all_issues[rel]
        if not issues:
            print(f"VALID {rel}")
        else:
            for level, msg in issues:
                print(f"{level} {msg}")
            # Summary line
            errors = [i for i in issues if i[0] == "ERROR"]
            warns = [i for i in issues if i[0] == "WARN"]
            if errors:
                print(f"      -> {rel}: {len(errors)} error(s), {len(warns)} warning(s)")
            elif warns:
                print(f"      -> {rel}: VALID with {len(warns)} warning(s)")

    return exit_code


def main():
    parser = argparse.ArgumentParser(
        prog="okf",
        description="Open Knowledge Format (OKF v0.2) bundle management",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # validate
    vp = sub.add_parser("validate", help="Validate a bundle or individual files")
    vp.add_argument("--bundle", required=True, help="Path to the bundle root directory")
    vp.add_argument("files", nargs="*", help="Optional: relative paths inside the bundle to validate (default: all .md)")

    args = parser.parse_args()

    if args.command == "validate":
        sys.exit(cmd_validate(args))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
