#!/usr/bin/env -S uv run --script
#
# /// script
# requires-python = ">=3.10"
# dependencies = ["PyYAML"]
# ///
"""okf — Open Knowledge Format (OKF v0.2) bundle management.

Usage:
    okf.py visit   --bundle PATH --query "valid-on:2024-01-01 AND tag:finance"
    okf.py search  --bundle PATH --query "written-by:human" --json
    okf.py info    --bundle PATH concepts/revenue.md
    okf.py validate --bundle PATH [files...]
    okf.py create  --bundle PATH --type Metric --title "..."
    okf.py generate-index --bundle PATH
    okf.py list    --bundle PATH
"""

import argparse
import copy
import datetime
import json
import re
import sys
from pathlib import Path

import yaml

# ── Constants ─────────────────────────────────────────────────────────

CONCEPT_KEYS = {
    "type", "title", "description", "resource", "tags",
    "sources", "usage_window",
    "generated", "verified",
    "status", "stale_after",
    "runtime", "parameters", "computation", "executor", "attester",
    # Known extensions
    "coverage",
}

SOURCES_ENTRY_KEYS = {
    "resource", "id", "title", "author",
    "usage_count", "last_modified",
}

GENERATED_KEYS = {"by", "at"}
EXECUTOR_KEYS = {"resource", "receipt"}
ATTESTER_KEYS = {"resource"}
PARAMETER_KEYS = {"name", "type", "required"}

VALID_STATUSES = {"draft", "stable", "deprecated"}
RESERVED = {"index.md", "log.md"}


# ── Date helpers ──────────────────────────────────────────────────────

def _to_date(s):
    """Convert string or date to date. Return date or None."""
    if isinstance(s, datetime.date) and not isinstance(s, datetime.datetime):
        return s
    if isinstance(s, str):
        try:
            return datetime.date.fromisoformat(s)
        except (ValueError, TypeError):
            return None
    return None


def _to_datetime(s):
    """Convert string or datetime to datetime. Return datetime or None."""
    if isinstance(s, datetime.datetime):
        return s
    if isinstance(s, str):
        s = s.strip()
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        try:
            return datetime.datetime.fromisoformat(s)
        except (ValueError, TypeError):
            return None
    return None


def _is_date_valid(s):
    """Check if value is a valid date (string or date object)."""
    if isinstance(s, datetime.date) and not isinstance(s, datetime.datetime):
        return True
    return _to_date(s) is not None


def _is_iso8601_valid(s):
    """Check if value is a valid ISO 8601 datetime (string or datetime object)."""
    if isinstance(s, datetime.datetime):
        return True
    return _to_datetime(s) is not None


# ── Actor helpers ─────────────────────────────────────────────────────

def _actor_kind(actor):
    """Classify actor string: 'human', 'process', 'agent'."""
    if not isinstance(actor, str):
        return "unknown"
    actor = actor.strip()
    if actor.startswith("human:"):
        return "human"
    if actor.startswith("process:"):
        return "process"
    # producer/version pattern
    if "/" in actor:
        return "agent"
    return "unknown"


def _actor_matches(actor, kind_or_exact):
    """Check if actor matches a kind ('human'/'ai'/'process') or exact string."""
    if not isinstance(actor, str):
        return False
    # 'ai' matches non-human, non-process actors (agent/unknown)
    if kind_or_exact == "ai":
        return _actor_kind(actor) not in ("human", "process")
    if kind_or_exact in ("human", "process"):
        return _actor_kind(actor) == kind_or_exact
    # Exact match
    return actor.strip() == kind_or_exact.strip()


# ── Trust tier ────────────────────────────────────────────────────────

def _trust_tier(fm):
    """Derive trust tier from verified field."""
    ver = fm.get("verified")
    if ver is None:
        return "unverified"
    if isinstance(ver, dict):
        ver = [ver]
    if not isinstance(ver, list):
        return "unverified"
    for entry in ver:
        if isinstance(entry, dict) and _actor_kind(entry.get("by")) == "human":
            return "human-reviewed"
    return "machine-confirmed"


# ── Validity helpers ──────────────────────────────────────────────────

def _validity_window(fm):
    """Return (valid_from_date_or_None, valid_until_date_or_None, is_stable)."""
    status = fm.get("status", "stable")
    is_stable = status == "stable"

    valid_from = None
    gen_at = fm.get("generated", {})
    if isinstance(gen_at, dict):
        dt = _to_datetime(gen_at.get("at"))
        if dt:
            valid_from = dt.date()

    valid_until = None
    stale = fm.get("stale_after")
    d = _to_date(stale)
    if d:
        valid_until = d

    return valid_from, valid_until, is_stable


def _is_valid_on(fm, check_date):
    """Check if concept is valid on a specific date."""
    valid_from, valid_until, is_stable = _validity_window(fm)
    if not is_stable:
        return False
    if valid_from and check_date < valid_from:
        return False
    if valid_until and check_date >= valid_until:
        return False
    return True


def _is_not_stale(fm, check_date=None):
    """Check if concept is not stale on given date (default: today)."""
    if check_date is None:
        check_date = datetime.date.today()
    _, valid_until, is_stable = _validity_window(fm)
    if not is_stable:
        return False
    if valid_until is None:
        return True
    return check_date < valid_until


# ── Frontmatter parsing ──────────────────────────────────────────────

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
        if len(parts) < 3:
            return None, "missing closing '---' for frontmatter"
        fm = yaml.safe_load(parts[1])
        if fm is None:
            fm = {}
        return fm, parts[2]
    except yaml.YAMLError as e:
        return None, f"invalid YAML in frontmatter: {e}"


# ── Query engine ──────────────────────────────────────────────────────

class QueryError(Exception):
    pass


def _tokenize_query(expr):
    """Tokenize a query expression into atoms and operators."""
    tokens = []
    i = 0
    expr = expr.strip()
    while i < len(expr):
        if expr[i].isspace():
            i += 1
            continue
        # Parentheses
        if expr[i] == "(":
            tokens.append("(")
            i += 1
            continue
        if expr[i] == ")":
            tokens.append(")")
            i += 1
            continue
        # Standalone quoted string
        if expr[i] == '"':
            j = expr.index('"', i + 1)
            tokens.append(("ATOM", expr[i + 1:j]))
            i = j + 1
            continue
        # Word (may contain :, ~, -, /, @, ., _, numbers, commas)
        # But if we hit a quote mid-word, consume until closing quote
        j = i
        while j < len(expr) and not expr[j].isspace() and expr[j] not in "()":
            if expr[j] == '"':
                # Find closing quote
                close = expr.index('"', j + 1)
                j = close + 1
                continue
            j += 1
        word = expr[i:j]
        if word.upper() in ("AND", "OR", "NOT"):
            tokens.append(("OP", word.upper()))
        else:
            tokens.append(("ATOM", word))
        i = j
    return tokens


def _parse_query(tokens):
    """Parse tokens into an AST: (op, left, right) or (leaf, kind, value)."""
    pos = [0]  # mutable index

    def peek():
        if pos[0] < len(tokens):
            return tokens[pos[0]]
        return None

    def consume():
        tok = tokens[pos[0]]
        pos[0] += 1
        return tok

    def parse_or():
        left = parse_and()
        while peek() and peek() == ("OP", "OR"):
            consume()
            right = parse_and()
            left = ("OR", left, right)
        return left

    def parse_and():
        left = parse_not()
        while peek() and (peek() == ("OP", "AND") or (peek()[0] == "ATOM" if isinstance(peek(), tuple) else False)):
            if peek() == ("OP", "AND"):
                consume()
            elif peek()[0] == "ATOM":
                pass  # implicit AND
            else:
                break
            right = parse_not()
            left = ("AND", left, right)
        return left

    def parse_not():
        if peek() == ("OP", "NOT"):
            consume()
            operand = parse_not()
            return ("NOT", operand)
        return parse_primary()

    def parse_primary():
        tok = peek()
        if tok == "(":
            consume()
            node = parse_or()
            if peek() != ")":
                raise QueryError("missing closing ')'")
            consume()
            return node
        if tok and tok[0] == "ATOM":
            consume()
            return _make_leaf(tok[1])
        raise QueryError(f"unexpected token: {tok}")

    if not tokens:
        raise QueryError("empty query")

    return parse_or()


def _strip_quotes(s):
    """Strip outer quotes from a string value."""
    if isinstance(s, str) and len(s) >= 2 and s[0] == '"' and s[-1] == '"':
        return s[1:-1]
    return s


def _make_leaf(atom):
    """Convert an atom string into a leaf node."""
    # valid-on:DATE
    if atom.startswith("valid-on:"):
        date_str = atom[len("valid-on:"):]
        d = _to_date(date_str)
        if not d:
            raise QueryError(f"invalid date in valid-on: {date_str}")
        return ("LEAF", "valid-on", d)

    # valid-between:DATE,DATE
    if atom.startswith("valid-between:"):
        parts = atom[len("valid-between:"):].split(",")
        if len(parts) != 2:
            raise QueryError(f"valid-between requires two dates: {atom}")
        d1 = _to_date(parts[0].strip())
        d2 = _to_date(parts[1].strip())
        if not d1 or not d2:
            raise QueryError(f"invalid date in valid-between: {atom}")
        return ("LEAF", "valid-between", (d1, d2))

    # valid-from:DATE
    if atom.startswith("valid-from:"):
        d = _to_date(atom[len("valid-from:"):])
        if not d:
            raise QueryError(f"invalid date in valid-from")
        return ("LEAF", "valid-from", d)

    # valid-until:DATE
    if atom.startswith("valid-until:"):
        d = _to_date(atom[len("valid-until:"):])
        if not d:
            raise QueryError(f"invalid date in valid-until")
        return ("LEAF", "valid-until", d)

    # not-stale-on:DATE
    if atom.startswith("not-stale-on:"):
        d = _to_date(atom[len("not-stale-on:"):])
        if not d:
            raise QueryError(f"invalid date in not-stale-on")
        return ("LEAF", "not-stale-on", d)

    # not-stale
    if atom == "not-stale":
        return ("LEAF", "not-stale", None)

    # written-by:actor
    if atom.startswith("written-by:"):
        return ("LEAF", "written-by", _strip_quotes(atom[len("written-by:"):]))

    # reviewed-by:actor
    if atom.startswith("reviewed-by:"):
        return ("LEAF", "reviewed-by", _strip_quotes(atom[len("reviewed-by:"):]))

    # trust-tier:tier
    if atom.startswith("trust-tier:"):
        tier = atom[len("trust-tier:"):]
        if tier not in ("unverified", "machine-confirmed", "human-reviewed"):
            raise QueryError(f"invalid trust-tier: {tier}")
        return ("LEAF", "trust-tier", tier)

    # status:status
    if atom.startswith("status:"):
        status = atom[len("status:"):]
        if status not in VALID_STATUSES:
            raise QueryError(f"invalid status: {status}")
        return ("LEAF", "status", status)

    # type:type
    if atom.startswith("type:"):
        return ("LEAF", "type", _strip_quotes(atom[len("type:"):]))

    # tag:tag
    if atom.startswith("tag:"):
        return ("LEAF", "tag", _strip_quotes(atom[len("tag:"):]))

    # has:field
    if atom.startswith("has:"):
        return ("LEAF", "has", atom[len("has:"):])

    # runtime:runtime
    if atom.startswith("runtime:"):
        return ("LEAF", "runtime", _strip_quotes(atom[len("runtime:"):]))

    # generated.after:DATE / generated.before:DATE
    if atom.startswith("generated.after:"):
        d = _to_date(atom[len("generated.after:"):])
        if not d:
            raise QueryError(f"invalid date in generated.after")
        return ("LEAF", "generated.after", d)
    if atom.startswith("generated.before:"):
        d = _to_date(atom[len("generated.before:"):])
        if not d:
            raise QueryError(f"invalid date in generated.before")
        return ("LEAF", "generated.before", d)

    # verified.after:DATE / verified.before:DATE
    if atom.startswith("verified.after:"):
        d = _to_date(atom[len("verified.after:"):])
        if not d:
            raise QueryError(f"invalid date in verified.after")
        return ("LEAF", "verified.after", d)
    if atom.startswith("verified.before:"):
        d = _to_date(atom[len("verified.before:"):])
        if not d:
            raise QueryError(f"invalid date in verified.before")
        return ("LEAF", "verified.before", d)

    # source-modified.after:DATE / source-modified.before:DATE
    if atom.startswith("source-modified.after:"):
        d = _to_date(atom[len("source-modified.after:"):])
        if not d:
            raise QueryError(f"invalid date in source-modified.after")
        return ("LEAF", "source-modified.after", d)
    if atom.startswith("source-modified.before:"):
        d = _to_date(atom[len("source-modified.before:"):])
        if not d:
            raise QueryError(f"invalid date in source-modified.before")
        return ("LEAF", "source-modified.before", d)

    # source-author:actor
    if atom.startswith("source-author:"):
        return ("LEAF", "source-author", _strip_quotes(atom[len("source-author:"):]))

    # title~:pattern / desc~:pattern / body~:pattern
    if atom.startswith("title~:"):
        return ("LEAF", "title~", _strip_quotes(atom[len("title~:"):]))
    if atom.startswith("desc~:"):
        return ("LEAF", "desc~", _strip_quotes(atom[len("desc~:"):]))
    if atom.startswith("body~:"):
        return ("LEAF", "body~", _strip_quotes(atom[len("body~:"):]))

    raise QueryError(f"unknown query atom: {atom}")


def _eval_leaf(leaf_kind, leaf_value, fm, body):
    """Evaluate a single leaf against frontmatter + body."""
    if leaf_kind == "valid-on":
        return _is_valid_on(fm, leaf_value)

    if leaf_kind == "valid-between":
        d1, d2 = leaf_value
        # Valid for the full range: every day in [d1, d2) must be valid
        current = d1
        while current < d2:
            if not _is_valid_on(fm, current):
                return False
            current += datetime.timedelta(days=1)
        return True

    if leaf_kind == "valid-from":
        # Valid on some date >= leaf_value
        valid_from, _, is_stable = _validity_window(fm)
        if not is_stable:
            return False
        if valid_from and valid_from >= leaf_value:
            return True
        if valid_from is None:
            return True  # no from constraint, stable = valid from unknown past
        return False

    if leaf_kind == "valid-until":
        # Valid on some date <= leaf_value
        _, valid_until, is_stable = _validity_window(fm)
        if not is_stable:
            return False
        if valid_until and valid_until > leaf_value:
            return True
        if valid_until is None:
            return True  # never stale
        return False

    if leaf_kind == "not-stale":
        return _is_not_stale(fm)

    if leaf_kind == "not-stale-on":
        return _is_not_stale(fm, leaf_value)

    if leaf_kind == "written-by":
        gen = fm.get("generated", {})
        if not isinstance(gen, dict):
            return False
        return _actor_matches(gen.get("by"), leaf_value)

    if leaf_kind == "reviewed-by":
        ver = fm.get("verified")
        if ver is None:
            return False
        if isinstance(ver, dict):
            ver = [ver]
        if not isinstance(ver, list):
            return False
        return any(_actor_matches(e.get("by"), leaf_value) for e in ver if isinstance(e, dict))

    if leaf_kind == "trust-tier":
        return _trust_tier(fm) == leaf_value

    if leaf_kind == "status":
        return fm.get("status", "stable") == leaf_value

    if leaf_kind == "type":
        return fm.get("type", "") == leaf_value

    if leaf_kind == "tag":
        tags = fm.get("tags", [])
        if not isinstance(tags, list):
            return False
        return any(leaf_value.lower() == str(t).lower() for t in tags)

    if leaf_kind == "has":
        val = fm.get(leaf_value)
        if val is None:
            return False
        if isinstance(val, (list, dict)):
            return len(val) > 0
        return True

    if leaf_kind == "runtime":
        return fm.get("runtime", "") == leaf_value

    if leaf_kind == "generated.after":
        gen = fm.get("generated", {})
        if not isinstance(gen, dict):
            return False
        dt = _to_datetime(gen.get("at"))
        if not dt:
            return False
        return dt.date() > leaf_value

    if leaf_kind == "generated.before":
        gen = fm.get("generated", {})
        if not isinstance(gen, dict):
            return False
        dt = _to_datetime(gen.get("at"))
        if not dt:
            return False
        return dt.date() < leaf_value

    if leaf_kind == "verified.after":
        ver = fm.get("verified")
        if ver is None:
            return False
        if isinstance(ver, dict):
            ver = [ver]
        if not isinstance(ver, list):
            return False
        for e in ver:
            if isinstance(e, dict):
                dt = _to_datetime(e.get("at"))
                if dt and dt.date() > leaf_value:
                    return True
        return False

    if leaf_kind == "verified.before":
        ver = fm.get("verified")
        if ver is None:
            return False
        if isinstance(ver, dict):
            ver = [ver]
        if not isinstance(ver, list):
            return False
        for e in ver:
            if isinstance(e, dict):
                dt = _to_datetime(e.get("at"))
                if dt and dt.date() < leaf_value:
                    return True
        return False

    if leaf_kind == "source-modified.after":
        sources = fm.get("sources", [])
        if not isinstance(sources, list):
            return False
        for s in sources:
            if isinstance(s, dict):
                d = _to_date(s.get("last_modified"))
                if d and d > leaf_value:
                    return True
        return False

    if leaf_kind == "source-modified.before":
        sources = fm.get("sources", [])
        if not isinstance(sources, list):
            return False
        for s in sources:
            if isinstance(s, dict):
                d = _to_date(s.get("last_modified"))
                if d and d < leaf_value:
                    return True
        return False

    if leaf_kind == "source-author":
        sources = fm.get("sources", [])
        if not isinstance(sources, list):
            return False
        for s in sources:
            if isinstance(s, dict):
                if _actor_matches(s.get("author"), leaf_value):
                    return True
        return False

    if leaf_kind == "title~":
        title = fm.get("title", "")
        return leaf_value.lower() in str(title).lower()

    if leaf_kind == "desc~":
        desc = fm.get("description", "")
        return leaf_value.lower() in str(desc).lower()

    if leaf_kind == "body~":
        return leaf_value.lower() in body.lower() if body else False

    return False


def _eval_query(ast, fm, body):
    """Evaluate a query AST against frontmatter + body."""
    if ast[0] == "LEAF":
        return _eval_leaf(ast[1], ast[2], fm, body)

    op = ast[0]
    if op == "AND":
        return _eval_query(ast[1], fm, body) and _eval_query(ast[2], fm, body)
    if op == "OR":
        return _eval_query(ast[1], fm, body) or _eval_query(ast[2], fm, body)
    if op == "NOT":
        return not _eval_query(ast[1], fm, body)

    return False


def parse_query(expr):
    """Parse and return a query AST. Raises QueryError on bad syntax."""
    tokens = _tokenize_query(expr)
    if not tokens:
        raise QueryError("empty query")
    return _parse_query(tokens)


def match_query(fm, body, query_ast):
    """Evaluate a parsed query AST against frontmatter + body."""
    return _eval_query(query_ast, fm, body)


# ── Bundle walking ────────────────────────────────────────────────────

def walk_bundle(bundle_path):
    """Yield (relative_path, full_path, is_concept) for all .md files."""
    bundle = Path(bundle_path)
    for p in sorted(bundle.rglob("*.md")):
        rel = str(p.relative_to(bundle))
        is_concept = p.name not in RESERVED
        yield rel, p, is_concept


def load_concept(bundle_path, rel_path):
    """Load a concept: return (fm, body) or (None, error)."""
    full = Path(bundle_path) / rel_path
    return _parse_frontmatter(full)


# ── Validation ────────────────────────────────────────────────────────

def _check_key(fm, key, required=False, expected_type=None, context=""):
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
    issues = []
    for key in fm:
        if key not in known:
            ctx = f"{context}.{key}" if context else str(key)
            issues.append(("WARN", f"{ctx}: unknown frontmatter key (allowed but not recognized)"))
    return issues


def validate_concept(path):
    """Validate a concept document. Return (issues, is_valid)."""
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

    # Recommended fields
    issues.extend(_check_key(fm, "title", expected_type=str, context=name))
    issues.extend(_check_key(fm, "description", expected_type=str, context=name))
    issues.extend(_check_key(fm, "resource", expected_type=str, context=name))

    # tags
    if "tags" in fm:
        if not isinstance(fm["tags"], list):
            issues.append(("ERROR", f"{name}.tags: expected list, got {type(fm['tags']).__name__}"))
        else:
            for i, t in enumerate(fm["tags"]):
                if not isinstance(t, str):
                    issues.append(("ERROR", f"{name}.tags[{i}]: expected string"))

    # sources
    if "sources" in fm:
        src = fm["sources"]
        if not isinstance(src, list):
            issues.append(("ERROR", f"{name}.sources: expected list"))
        else:
            for i, entry in enumerate(src):
                if not isinstance(entry, dict):
                    issues.append(("ERROR", f"{name}.sources[{i}]: expected mapping"))
                    continue
                if "resource" not in entry:
                    issues.append(("ERROR", f"{name}.sources[{i}].resource: required within sources entry"))
                elif not isinstance(entry["resource"], str):
                    issues.append(("ERROR", f"{name}.sources[{i}].resource: expected string"))
                if "id" in entry and not isinstance(entry["id"], str):
                    issues.append(("ERROR", f"{name}.sources[{i}].id: expected string"))
                if "title" in entry and not isinstance(entry["title"], str):
                    issues.append(("ERROR", f"{name}.sources[{i}].title: expected string"))
                if "author" in entry and not isinstance(entry["author"], str):
                    issues.append(("ERROR", f"{name}.sources[{i}].author: expected string"))
                if "usage_count" in entry and not isinstance(entry["usage_count"], (int, float)):
                    issues.append(("ERROR", f"{name}.sources[{i}].usage_count: expected number"))
                if "last_modified" in entry:
                    if not _is_date_valid(entry["last_modified"]):
                        issues.append(("WARN", f"{name}.sources[{i}].last_modified: not a valid date"))
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
                if k in uw and not _is_date_valid(uw[k]):
                    issues.append(("WARN", f"{name}.usage_window.{k}: not a valid date"))

    # generated
    if "generated" in fm:
        gen = fm["generated"]
        if not isinstance(gen, dict):
            issues.append(("ERROR", f"{name}.generated: expected mapping"))
        else:
            if "by" not in gen:
                issues.append(("ERROR", f"{name}.generated.by: required within 'generated'"))
            elif not isinstance(gen["by"], str):
                issues.append(("ERROR", f"{name}.generated.by: expected string (actor)"))
            else:
                kind = _actor_kind(gen["by"])
                if kind == "unknown":
                    issues.append(("WARN", f"{name}.generated.by: does not match actor convention (human:*, process:*, or producer/version)"))
            if "at" in gen and not _is_iso8601_valid(gen["at"]):
                issues.append(("WARN", f"{name}.generated.at: not a valid ISO 8601 datetime"))
            for k in gen:
                if k not in GENERATED_KEYS:
                    issues.append(("WARN", f"{name}.generated.{k}: unknown key"))

    # verified
    if "verified" in fm:
        ver = fm["verified"]
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
                else:
                    kind = _actor_kind(entry["by"])
                    if kind == "unknown":
                        issues.append(("WARN", f"{name}.verified[{i}].by: does not match actor convention"))
                if "at" not in entry:
                    issues.append(("ERROR", f"{name}.verified[{i}].at: required within verified entry"))
                elif not _is_iso8601_valid(entry["at"]):
                    issues.append(("WARN", f"{name}.verified[{i}].at: not a valid ISO 8601 datetime"))

    # status
    if "status" in fm:
        if fm["status"] not in VALID_STATUSES:
            issues.append(("ERROR", f"{name}.status: must be one of {sorted(VALID_STATUSES)}, got '{fm['status']}'"))

    # stale_after
    if "stale_after" in fm and not _is_date_valid(fm["stale_after"]):
        issues.append(("WARN", f"{name}.stale_after: not a valid date"))

    # coverage (known extension)
    if "coverage" in fm:
        cov = fm["coverage"]
        if not isinstance(cov, list):
            issues.append(("ERROR", f"{name}.coverage: expected list"))
        else:
            for i, entry in enumerate(cov):
                if not isinstance(entry, dict):
                    issues.append(("ERROR", f"{name}.coverage[{i}]: expected mapping"))
                    continue
                if "source" not in entry:
                    issues.append(("ERROR", f"{name}.coverage[{i}].source: required within coverage entry"))
                elif not isinstance(entry["source"], str):
                    issues.append(("ERROR", f"{name}.coverage[{i}].source: expected string"))
                if "region" in entry and not isinstance(entry["region"], dict):
                    issues.append(("ERROR", f"{name}.coverage[{i}].region: expected mapping"))

    # Attested Computation
    concept_type = fm.get("type", "")
    if concept_type == "Attested Computation":
        if "runtime" not in fm:
            issues.append(("ERROR", f"{name}.runtime: required for 'Attested Computation'"))
        elif not isinstance(fm["runtime"], str):
            issues.append(("ERROR", f"{name}.runtime: expected string"))
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
        if "computation" in fm and not isinstance(fm["computation"], str):
            issues.append(("ERROR", f"{name}.computation: expected string (path)"))
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
    """Validate index.md. Return (issues, is_valid)."""
    issues = []
    name = str(path)

    text = path.read_text(encoding="utf-8")
    if text.lstrip().startswith("---"):
        if is_root:
            fm, err = _parse_frontmatter(path)
            if fm is None:
                issues.append(("ERROR", f"{name}: {err}"))
                return issues, False
            for k in fm:
                if k != "okf_version":
                    issues.append(("ERROR", f"{name}: frontmatter key '{k}' not allowed in index.md (only 'okf_version' at bundle root)"))
            if "okf_version" in fm and not isinstance(fm["okf_version"], str):
                issues.append(("ERROR", f"{name}.okf_version: expected string"))
        else:
            issues.append(("ERROR", f"{name}: index.md must not have frontmatter (only bundle-root may carry 'okf_version')"))

    return issues, len([i for i in issues if i[0] == "ERROR"]) == 0


# ── Derived info ──────────────────────────────────────────────────────

def concept_info(fm, body):
    """Build a dict of derived info for a concept."""
    valid_from, valid_until, is_stable = _validity_window(fm)
    tier = _trust_tier(fm)
    today = datetime.date.today()
    stale = not _is_not_stale(fm)

    gen_by = ""
    gen_at = ""
    gen = fm.get("generated", {})
    if isinstance(gen, dict):
        gen_by = gen.get("by", "")
        gen_at = gen.get("at", "")

    verifiers = []
    ver = fm.get("verified")
    if isinstance(ver, dict):
        ver = [ver]
    if isinstance(ver, list):
        for e in ver:
            if isinstance(e, dict):
                verifiers.append({"by": e.get("by", ""), "at": e.get("at", "")})

    sources_count = 0
    if isinstance(fm.get("sources"), list):
        sources_count = len(fm["sources"])

    return {
        "type": fm.get("type", ""),
        "title": fm.get("title", ""),
        "description": fm.get("description", ""),
        "status": fm.get("status", "stable"),
        "trust_tier": tier,
        "valid_from": str(valid_from) if valid_from else "unknown",
        "valid_until": str(valid_until) if valid_until else "never",
        "stale": stale,
        "generated_by": gen_by,
        "generated_at": gen_at,
        "verified": verifiers,
        "sources_count": sources_count,
        "tags": fm.get("tags", []),
    }


# ── Commands ──────────────────────────────────────────────────────────

def cmd_visit(args):
    bundle = Path(args.bundle).resolve()
    if not bundle.is_dir():
        print(f"ERROR: '{args.bundle}' is not a directory", file=sys.stderr)
        return 1

    query_ast = None
    if args.query:
        try:
            query_ast = parse_query(args.query)
        except QueryError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return 1

    output_mode = args.output or "paths"
    exit_code = 0
    results = []

    for rel, full, is_concept in walk_bundle(bundle):
        if not is_concept:
            continue
        fm, body = load_concept(bundle, rel)
        if fm is None:
            continue
        if query_ast and not match_query(fm, body or "", query_ast):
            continue
        results.append((rel, fm, body or ""))

    if output_mode == "paths":
        for rel, fm, body in results:
            print(rel)
    elif output_mode == "json":
        out = []
        for rel, fm, body in results:
            out.append({"path": rel, "frontmatter": fm})
        print(json.dumps(out, indent=2, default=str))
    elif output_mode == "frontmatter":
        for rel, fm, body in results:
            print("---")
            print(yaml.dump(fm, default_flow_style=False, sort_keys=False).rstrip())
            print("---")
    elif output_mode == "summary":
        _print_summary_table(results)

    return 0


def cmd_search(args):
    bundle = Path(args.bundle).resolve()
    if not bundle.is_dir():
        print(f"ERROR: '{args.bundle}' is not a directory", file=sys.stderr)
        return 1

    query_ast = None
    if args.query:
        try:
            query_ast = parse_query(args.query)
        except QueryError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return 1

    results = []
    for rel, full, is_concept in walk_bundle(bundle):
        if not is_concept:
            continue
        fm, body = load_concept(bundle, rel)
        if fm is None:
            continue
        if query_ast and not match_query(fm, body or "", query_ast):
            continue
        results.append((rel, fm, body or ""))

    if args.json:
        out = []
        for rel, fm, body in results:
            info = concept_info(fm, body)
            info["path"] = rel
            out.append(info)
        print(json.dumps(out, indent=2, default=str))
    else:
        _print_search_table(results)

    return 0


def cmd_info(args):
    bundle = Path(args.bundle).resolve()
    filepath = Path(args.file)
    if not filepath.is_absolute():
        filepath = bundle / filepath
    if not filepath.exists():
        print(f"ERROR: file not found: {args.file}", file=sys.stderr)
        return 1

    fm, body = _parse_frontmatter(filepath)
    if fm is None:
        print(f"ERROR: cannot parse frontmatter: {body}", file=sys.stderr)
        return 1

    info = concept_info(fm, body)

    if args.json:
        info["path"] = str(filepath)
        print(json.dumps(info, indent=2, default=str))
    elif args.validity:
        print(f"valid_from: {info['valid_from']}")
        print(f"valid_until: {info['valid_until']}")
        print(f"stale: {info['stale']}")
    elif args.trust_tier:
        print(info["trust_tier"])
    else:
        print(f"Type:         {info['type']}")
        print(f"Title:        {info['title']}")
        print(f"Description:  {info['description']}")
        print(f"Status:       {info['status']}")
        print(f"Trust tier:   {info['trust_tier']}")
        print(f"Valid from:   {info['valid_from']}")
        print(f"Valid until:  {info['valid_until']}")
        print(f"Stale:        {'yes' if info['stale'] else 'no'}")
        print(f"Written by:   {info['generated_by']}")
        if info['generated_at']:
            print(f"Written at:   {info['generated_at']}")
        if info['verified']:
            for v in info['verified']:
                print(f"Reviewed by:  {v['by']} ({v['at']})")
        else:
            print(f"Reviewed by:  (none)")
        print(f"Sources:      {info['sources_count']}")
        if info['tags']:
            print(f"Tags:         {', '.join(str(t) for t in info['tags'])}")

    return 0


def cmd_validate(args):
    bundle = Path(args.bundle).resolve()
    if not bundle.is_dir():
        print(f"ERROR: '{args.bundle}' is not a directory", file=sys.stderr)
        return 1

    paths = args.files if args.files else []
    if not paths:
        paths = sorted(str(p.relative_to(bundle)) for p in bundle.rglob("*.md"))

    all_issues = {}
    exit_code = 0

    for rel in paths:
        full = bundle / rel
        if not full.is_file():
            print(f"ERROR: {rel}: file not found")
            exit_code = 1
            continue

        name = full.name
        if name == "log.md":
            all_issues[rel] = []
            continue

        if name == "index.md":
            is_root = (full.parent == bundle)
            issues, valid = validate_index(full, is_root=is_root)
        else:
            issues, valid = validate_concept(full)

        all_issues[rel] = issues
        if not valid:
            exit_code = 1

    for rel in sorted(all_issues):
        issues = all_issues[rel]
        if not issues:
            print(f"VALID {rel}")
        else:
            for level, msg in issues:
                print(f"{level} {msg}")
            errors = [i for i in issues if i[0] == "ERROR"]
            warns = [i for i in issues if i[0] == "WARN"]
            if errors:
                print(f"      -> {rel}: {len(errors)} error(s), {len(warns)} warning(s)")
            elif warns:
                print(f"      -> {rel}: VALID with {len(warns)} warning(s)")

    return exit_code


def cmd_create(args):
    bundle = Path(args.bundle).resolve()
    if not bundle.is_dir():
        print(f"ERROR: '{args.bundle}' is not a directory", file=sys.stderr)
        return 1

    if args.init:
        # Create root index.md with okf_version
        index = bundle / "index.md"
        content = "---\nokf_version: \"0.2\"\n---\n\n"
        index.write_text(content, encoding="utf-8")
        print(f"Created {index}")
        return 0

    fm = {}
    if args.type:
        fm["type"] = args.type
    if args.title:
        fm["title"] = args.title
    if args.description:
        fm["description"] = args.description
    if args.tags:
        fm["tags"] = [t.strip() for t in args.tags.split(",")]
    if args.status:
        fm["status"] = args.status
    if args.stale_after:
        fm["stale_after"] = args.stale_after
    if args.runtime:
        fm["runtime"] = args.runtime

    # Parameters for Attested Computation
    if args.param:
        params = []
        for p in args.param:
            parts = p.split(":")
            if len(parts) == 3:
                params.append({"name": parts[0], "type": parts[1], "required": parts[2].lower() == "true"})
            else:
                params.append({"name": parts[0], "type": "string", "required": True})
        fm["parameters"] = params

    if not fm:
        fm["type"] = "Concept"

    # Generate filename from title or type
    if args.file:
        filename = args.file
    elif args.title:
        slug = re.sub(r"[^a-zA-Z0-9]+", "-", args.title.lower()).strip("-")
        filename = f"{slug}.md"
    else:
        slug = re.sub(r"[^a-zA-Z0-9]+", "-", fm["type"].lower()).strip("-")
        filename = f"{slug}.md"

    if not filename.endswith(".md"):
        filename += ".md"

    target = bundle / filename
    if target.exists():
        print(f"ERROR: {filename} already exists", file=sys.stderr)
        return 1

    body_lines = []
    if fm.get("type") == "Attested Computation":
        body_lines.append(f"# {fm.get('title', fm['type'])}\n")
        body_lines.append("\n# Computation\n")
        body_lines.append(f"    # {fm.get('runtime', 'python')} computation goes here\n")

    body = "\n".join(body_lines) if body_lines else ""

    content = "---\n" + yaml.dump(fm, default_flow_style=False, sort_keys=False).rstrip() + "\n---\n"
    if body:
        content += "\n" + body + "\n"

    target.write_text(content, encoding="utf-8")
    print(f"Created {target}")
    return 0


def cmd_generate_index(args):
    bundle = Path(args.bundle).resolve()
    if not bundle.is_dir():
        print(f"ERROR: '{args.bundle}' is not a directory", file=sys.stderr)
        return 1

    target_dir = bundle / args.dir if args.dir else bundle
    if not target_dir.is_dir():
        print(f"ERROR: directory not found: {target_dir}", file=sys.stderr)
        return 1

    # Collect concepts in this directory (not recursive)
    concepts = []
    subdirs = []

    for entry in sorted(target_dir.iterdir()):
        if entry.is_file() and entry.name.endswith(".md") and entry.name not in RESERVED:
            fm, body = _parse_frontmatter(entry)
            if fm is not None:
                # Apply query filter if given
                if args.query:
                    try:
                        query_ast = parse_query(args.query)
                    except QueryError as e:
                        print(f"ERROR: {e}", file=sys.stderr)
                        return 1
                    if not match_query(fm, body or "", query_ast):
                        continue
                rel = str(entry.relative_to(bundle))
                concepts.append((entry.name, rel, fm))
        elif entry.is_dir() and entry.name != "references":
            subdirs.append(entry.name)

    lines = []
    if concepts:
        lines.append("# Concepts\n")
        for fname, rel, fm in concepts:
            title = fm.get("title", fm.get("type", fname))
            desc = fm.get("description", "")
            link = fname
            line = f"* [{title}]({link})"
            if desc:
                line += f" — {desc}"
            lines.append(line)
        lines.append("")

    for sd in subdirs:
        subdir_index = target_dir / sd / "index.md"
        if subdir_index.exists():
            lines.append(f"* [{sd}]({sd}/) — subdirectory\n")

    if not lines:
        lines.append(f"# {target_dir.name}\n")
        lines.append("\nNo concepts in this directory.\n")

    index_path = target_dir / "index.md"
    index_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Generated {index_path}")
    return 0


def cmd_list(args):
    bundle = Path(args.bundle).resolve()
    if not bundle.is_dir():
        print(f"ERROR: '{args.bundle}' is not a directory", file=sys.stderr)
        return 1

    results = []
    for rel, full, is_concept in walk_bundle(bundle):
        if not is_concept:
            continue
        fm, body = load_concept(bundle, rel)
        if fm is None:
            continue
        results.append((rel, fm, body or ""))

    if args.json:
        out = []
        for rel, fm, body in results:
            info = concept_info(fm, body)
            info["path"] = rel
            out.append(info)
        print(json.dumps(out, indent=2, default=str))
    else:
        _print_list_table(results)

    return 0


def cmd_check_coverage(args):
    """Check source coverage of a bundle."""
    bundle = Path(args.bundle).resolve()
    if not bundle.is_dir():
        print(f"ERROR: '{args.bundle}' is not a directory", file=sys.stderr)
        return 1

    # Collect all coverage entries from all concepts
    all_coverage = []  # list of (path, coverage_entry)
    all_concepts = []

    for rel, full, is_concept in walk_bundle(bundle):
        if not is_concept:
            continue
        fm, body = load_concept(bundle, rel)
        if fm is None:
            continue
        all_concepts.append((rel, fm))
        cov = fm.get("coverage", [])
        if not isinstance(cov, list):
            continue
        for entry in cov:
            if isinstance(entry, dict):
                all_coverage.append((rel, entry))

    # Build coverage map: source -> set of regions -> [concept paths]
    coverage_map = {}  # source -> {region_str: [paths]}
    for rel, entry in all_coverage:
        source = entry.get("source", "")
        region = entry.get("region", {})
        region_str = _region_to_str(region)
        if source not in coverage_map:
            coverage_map[source] = {}
        if region_str not in coverage_map[source]:
            coverage_map[source][region_str] = []
        coverage_map[source][region_str].append(rel)

    # If --source-regions file given, check for gaps
    if args.source_regions:
        sr_path = Path(args.source_regions)
        if not sr_path.exists():
            print(f"ERROR: source regions file not found: {args.source_regions}", file=sys.stderr)
            return 1
        try:
            source_regions = json.loads(sr_path.read_text())
        except Exception as e:
            print(f"ERROR: cannot parse {args.source_regions}: {e}", file=sys.stderr)
            return 1
        _check_gaps(coverage_map, source_regions)
        return 0

    # Report mode
    report = args.report or "summary"

    if report == "summary":
        _print_coverage_summary(coverage_map, all_concepts)
    elif report == "gaps":
        _report_gaps(coverage_map, all_concepts)
    elif report == "overlaps":
        _report_overlaps(coverage_map)
    elif report == "json":
        _print_coverage_json(coverage_map, all_concepts)
    elif report == "uncovered":
        _report_uncovered(all_concepts)

    return 0


def _region_to_str(region):
    """Convert a region dict to a string key."""
    if not region:
        return "(unknown)"
    return json.dumps(region, sort_keys=True, default=str)


def _region_page_set(region):
    """Normalize a region to a frozenset of pages for comparison."""
    pages = _parse_region_pages(region)
    if pages:
        return frozenset(pages)
    slides = region.get("slides", [])
    if isinstance(slides, list):
        slide_set = set()
        for s in slides:
            s_str = str(s).strip()
            if "-" in s_str:
                parts = s_str.split("-")
                try:
                    slide_set.update(range(int(parts[0]), int(parts[1]) + 1))
                except ValueError:
                    pass
            else:
                try:
                    slide_set.add(int(s_str))
                except ValueError:
                    pass
        if slide_set:
            return frozenset(slide_set)
    return None


def _parse_region_pages(region):
    """Parse a region's pages into a set of page numbers."""
    pages = region.get("pages", [])
    result = set()
    if isinstance(pages, list):
        for p in pages:
            p_str = str(p).strip()
            if "-" in p_str:
                parts = p_str.split("-")
                try:
                    start = int(parts[0])
                    end = int(parts[1])
                    result.update(range(start, end + 1))
                except ValueError:
                    pass
            else:
                try:
                    result.add(int(p_str))
                except ValueError:
                    pass
    return result


def _print_coverage_summary(coverage_map, all_concepts):
    """Print a summary of coverage."""
    total_concepts = len(all_concepts)
    concepts_with_coverage = len(set(
        rel for rel, _ in [
            (rel, entry) for rel, fm in all_concepts
            for entry in fm.get("coverage", [])
        ]
    ))
    total_sources = len(coverage_map)
    total_regions = sum(len(regions) for regions in coverage_map.values())

    print(f"Concepts:              {total_concepts}")
    print(f"Concepts with coverage: {concepts_with_coverage}")
    print(f"Sources tracked:       {total_sources}")
    print(f"Region entries:        {total_regions}")

    if coverage_map:
        print()
        print("Coverage by source:")
        for source in sorted(coverage_map):
            regions = coverage_map[source]
            print(f"  {source}: {len(regions)} region(s)")

    # Show concepts without coverage
    covered = set()
    for rel, entry in [
        (rel, entry) for rel, fm in all_concepts
        for entry in fm.get("coverage", [])
    ]:
        if isinstance(entry, dict):
            covered.add(rel)
    uncovered = [rel for rel, _ in all_concepts if rel not in covered]
    if uncovered:
        print()
        print(f"Concepts without coverage ({len(uncovered)}):")
        for rel in uncovered:
            print(f"  {rel}")


def _report_gaps(coverage_map, all_concepts):
    """Report potential coverage gaps."""
    gaps_found = False
    for source in sorted(coverage_map):
        regions = coverage_map[source]
        all_pages = set()
        for region_str, paths in regions.items():
            try:
                region = json.loads(region_str)
                pages = _parse_region_pages(region)
                all_pages.update(pages)
            except (json.JSONDecodeError, TypeError):
                pass
        if not all_pages:
            continue
        min_page = min(all_pages)
        max_page = max(all_pages)
        missing = set(range(min_page, max_page + 1)) - all_pages
        if missing:
            print(f"GAP {source}: missing pages {sorted(missing)} (tracked: {min_page}-{max_page})")
            gaps_found = True
    if not gaps_found:
        print("No page-range gaps detected.")


def _report_overlaps(coverage_map):
    """Report overlapping coverage (same pages in multiple concepts)."""
    found = False
    for source in sorted(coverage_map):
        # Build page -> concepts map
        page_to_concepts = {}
        for region_str, paths in coverage_map[source].items():
            try:
                region = json.loads(region_str)
                pages = _parse_region_pages(region)
                for page in pages:
                    if page not in page_to_concepts:
                        page_to_concepts[page] = set()
                    for p in paths:
                        page_to_concepts[page].add(p)
            except (json.JSONDecodeError, TypeError):
                pass
        # Find pages covered by multiple concepts
        overlap_pages = {p: cs for p, cs in page_to_concepts.items() if len(cs) > 1}
        if overlap_pages:
            print(f"OVERLAP {source}: {len(overlap_pages)} page(s) covered by multiple concepts")
            for page in sorted(overlap_pages):
                print(f"  page {page}: {sorted(overlap_pages[page])}")
            found = True
    if not found:
        print("No overlapping coverage detected.")


def _report_uncovered(all_concepts):
    """Report concepts without coverage tracking."""
    uncovered = []
    for rel, fm in all_concepts:
        cov = fm.get("coverage")
        if not cov or (isinstance(cov, list) and len(cov) == 0):
            uncovered.append(rel)
    if uncovered:
        print(f"Concepts without coverage ({len(uncovered)}):")
        for rel in uncovered:
            print(f"  {rel}")
    else:
        print("All concepts have coverage tracking.")


def _print_coverage_json(coverage_map, all_concepts):
    """Print coverage as JSON."""
    out = {
        "coverage": {},
        "concepts": [],
    }
    for source, regions in sorted(coverage_map.items()):
        out["coverage"][source] = {
            region: paths for region, paths in sorted(regions.items())
        }
    for rel, fm in all_concepts:
        cov = fm.get("coverage", [])
        out["concepts"].append({
            "path": rel,
            "has_coverage": isinstance(cov, list) and len(cov) > 0,
            "coverage": cov if isinstance(cov, list) else [],
        })
    print(json.dumps(out, indent=2, default=str))


def _check_gaps(coverage_map, source_regions):
    """Check for uncovered regions against a source regions file."""
    # Build normalized page coverage per source
    source_pages = {}  # source -> set of covered pages
    for source, regions in coverage_map.items():
        all_pages = set()
        for region_str in regions:
            try:
                region = json.loads(region_str)
                pages = _parse_region_pages(region)
                all_pages.update(pages)
            except (json.JSONDecodeError, TypeError):
                pass
        if all_pages:
            source_pages[source] = all_pages

    # source_regions is a dict: {source: [region1, region2, ...]}
    gaps_found = False
    for source, expected_regions in sorted(source_regions.items()):
        covered = source_pages.get(source, set())
        for expected in expected_regions:
            expected_pages = _parse_region_pages(expected)
            if not expected_pages:
                continue
            uncovered = expected_pages - covered
            if uncovered:
                print(f"GAP {source}: pages {sorted(uncovered)} not covered")
                gaps_found = True
    if not gaps_found:
        print("All expected regions are covered.")


# ── Table output helpers ──────────────────────────────────────────────

def _print_list_table(results):
    """Print a compact table of all concepts."""
    headers = ["PATH", "TYPE", "STATUS", "STALE", "TRUST-TIER"]
    rows = []
    for rel, fm, body in results:
        info = concept_info(fm, body)
        rows.append([
            rel,
            info["type"],
            info["status"],
            "yes" if info["stale"] else "no",
            info["trust_tier"],
        ])
    _print_table(headers, rows)


def _print_search_table(results):
    """Print a search results table."""
    headers = ["PATH", "TYPE", "TITLE", "STATUS", "TRUST-TIER", "VALID-UNTIL"]
    rows = []
    for rel, fm, body in results:
        info = concept_info(fm, body)
        rows.append([
            rel,
            info["type"],
            info["title"] or "",
            info["status"],
            info["trust_tier"],
            info["valid_until"],
        ])
    _print_table(headers, rows)


def _print_summary_table(results):
    """Print a detailed summary table."""
    headers = ["PATH", "TYPE", "TITLE", "STATUS", "TRUST-TIER", "WRITTEN-BY", "VALID-FROM", "VALID-UNTIL"]
    rows = []
    for rel, fm, body in results:
        info = concept_info(fm, body)
        rows.append([
            rel,
            info["type"],
            info["title"] or "",
            info["status"],
            info["trust_tier"],
            info["generated_by"],
            info["valid_from"],
            info["valid_until"],
        ])
    _print_table(headers, rows)


def _print_table(headers, rows):
    """Print a simple aligned table."""
    if not rows:
        return
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))

    # Header
    header_line = "  ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
    print(header_line)
    print("  ".join("-" * col_widths[i] for i in range(len(headers))))

    # Rows
    for row in rows:
        line = "  ".join(str(row[i]).ljust(col_widths[i]) for i in range(len(headers)))
        print(line)


# ── CLI ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        prog="okf",
        description="Open Knowledge Format (OKF v0.2) bundle management",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # visit
    vp = sub.add_parser("visit", help="Walk bundle, yield concepts matching --query")
    vp.add_argument("--bundle", required=True, help="Bundle root directory")
    vp.add_argument("--query", required=True, help="Query expression")
    vp.add_argument("--output", choices=["paths", "json", "frontmatter", "summary"],
                    default="paths", help="Output format (default: paths)")

    # search
    sp = sub.add_parser("search", help="Search concepts with structured output")
    sp.add_argument("--bundle", required=True, help="Bundle root directory")
    sp.add_argument("--query", required=True, help="Query expression")
    sp.add_argument("--json", action="store_true", help="Output as JSON")

    # info
    ip = sub.add_parser("info", help="Inspect a single concept")
    ip.add_argument("--bundle", required=True, help="Bundle root directory")
    ip.add_argument("file", help="Path to concept file (absolute or relative to bundle)")
    ip.add_argument("--json", action="store_true", help="Output as JSON")
    ip.add_argument("--validity", action="store_true", help="Show only validity window")
    ip.add_argument("--trust-tier", action="store_true", help="Show only trust tier")

    # validate
    vlp = sub.add_parser("validate", help="Validate a bundle or individual files")
    vlp.add_argument("--bundle", required=True, help="Bundle root directory")
    vlp.add_argument("files", nargs="*", help="Relative paths to validate (default: all .md)")

    # create
    cp = sub.add_parser("create", help="Scaffold a new concept or bundle")
    cp.add_argument("--bundle", required=True, help="Bundle root directory")
    cp.add_argument("--type", help="Concept type (e.g. Metric, Policy, Attested Computation)")
    cp.add_argument("--title", help="Concept title")
    cp.add_argument("--description", help="Concept description")
    cp.add_argument("--tags", help="Comma-separated tags")
    cp.add_argument("--status", choices=sorted(VALID_STATUSES), help="Status")
    cp.add_argument("--stale-after", help="Stale after date (YYYY-MM-DD)")
    cp.add_argument("--runtime", help="Runtime (for Attested Computation)")
    cp.add_argument("--param", action="append", help="Parameter as name:type:required (e.g. year:integer:true)")
    cp.add_argument("--file", help="Output filename (default: derived from title)")
    cp.add_argument("--init", action="store_true", help="Create root index.md with okf_version")

    # generate-index
    gip = sub.add_parser("generate-index", help="Auto-generate index.md")
    gip.add_argument("--bundle", required=True, help="Bundle root directory")
    gip.add_argument("--dir", help="Target directory (default: bundle root)")
    gip.add_argument("--query", help="Only index concepts matching query")

    # list
    lp = sub.add_parser("list", help="List all concepts in a bundle")
    lp.add_argument("--bundle", required=True, help="Bundle root directory")
    lp.add_argument("--json", action="store_true", help="Output as JSON")

    # check-coverage
    ccp = sub.add_parser("check-coverage",
                         help="Check source coverage of a bundle")
    ccp.add_argument("--bundle", required=True, help="Bundle root directory")
    ccp.add_argument("--source-regions", help="JSON file of expected source regions")
    ccp.add_argument("--report", choices=["summary", "gaps", "overlaps", "uncovered", "json"],
                     default="summary", help="Report type (default: summary)")

    args = parser.parse_args()

    commands = {
        "visit": cmd_visit,
        "search": cmd_search,
        "info": cmd_info,
        "validate": cmd_validate,
        "create": cmd_create,
        "generate-index": cmd_generate_index,
        "list": cmd_list,
    }

    cmd = commands.get(args.command)
    if cmd:
        sys.exit(cmd(args))
    elif args.command == "check-coverage":
        sys.exit(cmd_check_coverage(args))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
