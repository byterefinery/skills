#!/usr/bin/env python3
"""okf — Open Knowledge Format (OKF v0.2) bundle tooling.

Deterministic CLI for creating, reading, validating, and maintaining
OKF knowledge bundles. Subcommands map to the functions described in
the OKF reference_agent and web_ingestion instruction prompts.

Usage:
    okf.sh create <concept_id> [--type TYPE] [--title TITLE] [--description DESC] [--resource URI] [--tags TAG1,TAG2]
    okf.sh read <concept_id> [--bundle BUNDLE_DIR]
    okf.sh write <concept_id> --frontmatter <yaml> --body <markdown> [--bundle BUNDLE_DIR]
    okf.sh list [--bundle BUNDLE_DIR] [--json]
    okf.sh fetch <url> [--output FILE] [--format md|html|links|json]
    okf.sh crawl <seed_url...> [--max-pages N] [--allowed-hosts HOST1,HOST2] [--output DIR] [--bundle BUNDLE_DIR]
    okf.sh validate [--bundle BUNDLE_DIR] [--strict] [--json]
    okf.sh index [--bundle BUNDLE_DIR] [--dir DIR] [--force]
    okf.sh info <concept_id> [--bundle BUNDLE_DIR] [--json]
    okf.sh log [--bundle BUNDLE_DIR] [--add "action: message"]
"""

import argparse
import csv
import io
import json
import os
import re
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
import html as html_mod
import datetime
import mimetypes

# ── User agents (Safari — rarely blocked) ───────────────────────────

UA_IPHONE = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7_8 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) "
    "Version/26.0 Mobile/15E148 Safari/604.1"
)
UA_MAC = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 15_7_7) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) "
    "Version/26.0 Safari/605.1.15"
)
UA_DESKTOP = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/131.0.0.0 Safari/537.36"
)
USER_AGENTS = [UA_IPHONE, UA_MAC, UA_DESKTOP]

# ── Reserved filenames ──────────────────────────────────────────────

RESERVED_FILES = {"index.md", "log.md"}

# ── YAML helpers (no external deps) ─────────────────────────────────

YAML_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)^---\s*$", re.DOTALL | re.MULTILINE)


def parse_yaml_simple(text):
    """Minimal YAML parser for OKF frontmatter. Handles scalars, lists, and one-level mappings."""
    result = {}
    current_key = None
    current_list = None
    current_mapping = None
    lines = text.split("\n")

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # Check indentation level
        indent = len(line) - len(line.lstrip())

        if indent == 0:
            # Top-level key
            if ":" in stripped:
                key, _, value = stripped.partition(":")
                key = key.strip()
                value = value.strip()
                if value:
                    result[key] = parse_yaml_value(value)
                    current_key = None
                    current_list = None
                    current_mapping = None
                elif stripped.endswith(":"):
                    # Could be list or mapping
                    current_key = key
                    current_list = None
                    current_mapping = None
                    result[key] = None
                else:
                    current_key = key
                    current_list = None
                    current_mapping = None
                    result[key] = None
        elif indent > 0 and current_key:
            if stripped.startswith("- "):
                # List item
                if current_list is None:
                    current_list = []
                    result[current_key] = current_list
                item_value = stripped[2:].strip()
                if item_value.startswith("{") and item_value.endswith("}"):
                    # Inline mapping in list
                    current_list.append(parse_inline_mapping(item_value))
                else:
                    current_list.append(parse_yaml_value(item_value))
            elif ":" in stripped and current_mapping is not None:
                # Nested mapping
                if result.get(current_key) is None:
                    result[current_key] = {}
                k, _, v = stripped.partition(":")
                result[current_key][k.strip()] = parse_yaml_value(v.strip())
            elif ":" in stripped:
                # Could be start of nested mapping
                if result.get(current_key) is None or isinstance(result.get(current_key), dict):
                    if result.get(current_key) is None:
                        result[current_key] = {}
                    k, _, v = stripped.partition(":")
                    result[current_key][k.strip()] = parse_yaml_value(v.strip())

    return result


def parse_yaml_value(value):
    """Parse a single YAML scalar value."""
    if not value:
        return None
    # Remove quotes
    if (value.startswith('"') and value.endswith('"')) or \
       (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    # Boolean
    if value.lower() in ("true", "yes"):
        return True
    if value.lower() in ("false", "no"):
        return False
    # None
    if value.lower() in ("null", "~"):
        return None
    # Integer
    try:
        return int(value)
    except ValueError:
        pass
    # Float
    try:
        return float(value)
    except ValueError:
        pass
    # Inline list [a, b, c]
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [parse_yaml_value(v.strip()) for v in inner.split(",")]
    # Inline mapping {a: b, c: d}
    if value.startswith("{") and value.endswith("}"):
        return parse_inline_mapping(value)
    return value


def parse_inline_mapping(text):
    """Parse {key: value, key: value} inline YAML mapping."""
    text = text.strip()
    if text.startswith("{"):
        text = text[1:]
    if text.endswith("}"):
        text = text[:-1]
    result = {}
    # Split by comma, but respect nested braces
    parts = split_inline_parts(text)
    for part in parts:
        part = part.strip()
        if ":" in part:
            k, _, v = part.partition(":")
            result[k.strip()] = parse_yaml_value(v.strip())
    return result


def split_inline_parts(text):
    """Split by comma, respecting nested braces and brackets."""
    parts = []
    depth = 0
    current = []
    for ch in text:
        if ch in ("{", "["):
            depth += 1
            current.append(ch)
        elif ch in ("}", "]"):
            depth -= 1
            current.append(ch)
        elif ch == "," and depth == 0:
            parts.append("".join(current))
            current = []
        else:
            current.append(ch)
    if current:
        parts.append("".join(current))
    return parts


def serialize_yaml(data, indent=0):
    """Serialize a dict to YAML string (simple subset)."""
    lines = []
    prefix = " " * indent
    for key, value in data.items():
        if value is None:
            lines.append(f"{prefix}{key}:")
        elif isinstance(value, dict):
            # Check if simple enough for inline
            if all(not isinstance(v, (dict, list)) for v in value.values()):
                inline = ", ".join(f"{k}: {format_yaml_scalar(v)}" for k, v in value.items())
                lines.append(f"{prefix}{key}: {{{inline}}}")
            else:
                lines.append(f"{prefix}{key}:")
                lines.append(serialize_yaml(value, indent + 2))
        elif isinstance(value, list):
            if not value:
                lines.append(f"{prefix}{key}: []")
            elif all(isinstance(v, str) for v in value):
                # Simple list of strings
                items = ", ".join(f"'{v}'" if "," in v else str(v) for v in value)
                lines.append(f"{prefix}{key}: [{items}]")
            else:
                lines.append(f"{prefix}{key}:")
                for item in value:
                    if isinstance(item, dict):
                        inline = ", ".join(f"{k}: {format_yaml_scalar(v)}" for k, v in item.items())
                        lines.append(f"{prefix}  - {{{inline}}}")
                    else:
                        lines.append(f"{prefix}  - {format_yaml_scalar(item)}")
        else:
            lines.append(f"{prefix}{key}: {format_yaml_scalar(value)}")
    return "\n".join(lines)


def format_yaml_scalar(value):
    """Format a scalar value for YAML output."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, str):
        # Quote if contains special chars
        if any(ch in value for ch in (":", "#", "{", "}", "[", "]", ",", "&", "*", "?", "|", "-", "<", ">", "=", "!", "%", "@", "`")):
            if "\n" in value:
                return "|\n" + "\n".join(f"  {line}" for line in value.split("\n"))
            return f'"{value}"'
        return value
    return str(value)


# ── Frontmatter extraction ──────────────────────────────────────────

def extract_frontmatter(text):
    """Extract YAML frontmatter and body from a markdown file."""
    m = YAML_FRONTMATTER_RE.match(text)
    if m:
        raw = m.group(1)
        body = text[m.end():].lstrip("\n")
        try:
            fm = parse_yaml_simple(raw)
        except Exception:
            fm = {}
        return fm, body, raw
    return {}, text.strip(), ""


def build_document(frontmatter, body):
    """Build a complete OKF concept document from frontmatter dict and body string."""
    yaml_str = serialize_yaml(frontmatter)
    return f"---\n{yaml_str}\n---\n\n{body.lstrip()}\n"


# ── URL fetching (stdlib only, Safari user agents) ──────────────────

def fetch_url_content(url, timeout=30):
    """Fetch a URL and return (html_text, final_url, status).

    Uses Safari user agents and follows redirects.
    """
    import random
    ua = random.choice(USER_AGENTS)

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": ua,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "identity",
            "Connection": "keep-alive",
        },
    )

    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=timeout) as resp:
            data = resp.read().decode("utf-8", errors="replace")
            final_url = resp.url
            return data, final_url, 200
    except urllib.error.HTTPError as e:
        return "", url, e.code
    except urllib.error.URLError as e:
        return "", url, 0
    except TimeoutError:
        return "", url, 0


def html_to_markdown(html_text):
    """Convert HTML to markdown-like text using stdlib only."""
    content = html_mod.unescape(html_text)

    replacements = [
        (r"<h1[^>]*>(.*?)</h1>", r"\n\n# \1\n\n"),
        (r"<h2[^>]*>(.*?)</h2>", r"\n\n## \1\n\n"),
        (r"<h3[^>]*>(.*?)</h3>", r"\n\n### \1\n\n"),
        (r"<h4[^>]*>(.*?)</h4>", r"\n\n#### \1\n\n"),
        (r"<h5[^>]*>(.*?)</h5>", r"\n\n##### \1\n\n"),
        (r"<h6[^>]*>(.*?)</h6>", r"\n\n###### \1\n\n"),
        (r"<p[^>]*>(.*?)</p>", r"\n\n\1\n\n"),
        (r"<br\s*/?>", r"\n"),
        (r"<li[^>]*>(.*?)</li>", r"  - \1\n"),
        (r"<a[^>]*href=\"([^\"]*?)\"[^>]*>(.*?)</a>", r"\2 (\1)"),
        (r"<strong[^>]*>(.*?)</strong>", r"**\1**"),
        (r"<b[^>]*>(.*?)</b>", r"**\1**"),
        (r"<em[^>]*>(.*?)</em>", r"*\1*"),
        (r"<i[^>]*>(.*?)</i>", r"*\1*"),
        (r"<code[^>]*>(.*?)</code>", r"`\1`"),
        (r"<pre[^>]*>(.*?)</pre>", r"\n\n```\n\1\n```\n\n"),
        (r"<table[^>]*>(.*?)</table>", r"\n\n\1\n\n"),
        (r"<th[^>]*>(.*?)</th>", r"| **\1** |"),
        (r"<td[^>]*>(.*?)</td>", r"| \1 |"),
        (r"<tr[^>]*>", r"\n"),
    ]

    for pat, repl in replacements:
        content = re.sub(pat, repl, content, flags=re.DOTALL | re.IGNORECASE)

    # Strip HTML comments
    content = re.sub(r"<!--.*?-->", "", content, flags=re.DOTALL)
    # Strip remaining tags
    content = re.sub(r"<[^>]+>", "", content)
    # Collapse whitespace
    content = re.sub(r"[ \t]+", " ", content)
    content = re.sub(r"\n{3,}", "\n\n", content)
    return content.strip()


def extract_links(html_text, base_url=""):
    """Extract all href links from HTML, returning absolute URLs."""
    links = set()
    link_re = re.compile(r'<a[^>]*href=["\']([^"\']*)["\'][^>]*>', re.IGNORECASE)
    parsed_base = urllib.parse.urlparse(base_url)

    for m in link_re.finditer(html_text):
        href = m.group(1).strip()
        if not href or href.startswith(("#", "javascript:", "mailto:", "tel:", "data:")):
            continue
        # Resolve relative URLs
        if not href.startswith(("http://", "https://", "//")):
            href = urllib.parse.urljoin(base_url, href)
        # Remove fragment
        href = href.split("#")[0]
        links.add(href)

    return sorted(links)


# ── Bundle operations ───────────────────────────────────────────────

def resolve_bundle_dir(bundle_arg=None):
    """Resolve bundle directory path."""
    if bundle_arg:
        return os.path.abspath(bundle_arg)
    # Default: find .agents/skills or current dir
    return os.getcwd()


def find_concepts(bundle_dir, recursive=True):
    """Find all concept .md files in a bundle directory.

    Returns list of (relative_path, concept_id) tuples.
    Skips reserved files (index.md, log.md).
    """
    concepts = []
    for root, dirs, files in os.walk(bundle_dir):
        # Skip hidden directories
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for fname in sorted(files):
            if not fname.endswith(".md"):
                continue
            if fname in RESERVED_FILES:
                continue
            full_path = os.path.join(root, fname)
            rel_path = os.path.relpath(full_path, bundle_dir)
            concept_id = rel_path[:-3]  # Remove .md
            concepts.append((rel_path, concept_id))
        if not recursive:
            break
    return concepts


def read_existing_doc(concept_id, bundle_dir):
    """read_existing_doc(concept_id) — Read an existing concept document.

    Returns (frontmatter_dict, body_text, raw_frontmatter_yaml) or (None, None, None).
    """
    path = os.path.join(bundle_dir, concept_id + ".md")
    if not os.path.isfile(path):
        return None, None, None
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    fm, body, raw = extract_frontmatter(text)
    return fm, body, raw


def write_concept_doc(concept_id, frontmatter, body, bundle_dir, validate_doc=True):
    """write_concept_doc(concept_id, frontmatter, body) — Write or update a concept document.

    Validates required fields and preserves existing content on update.
    Returns dict with status and any warnings.
    """
    result = {"status": "ok", "concept_id": concept_id, "warnings": []}

    # Validate required fields
    if not frontmatter.get("type"):
        result["status"] = "error"
        result["error"] = "Missing required frontmatter field: type"
        return result

    # Check for existing doc (augmentation mode)
    existing_fm, existing_body, _ = read_existing_doc(concept_id, bundle_dir)
    if existing_fm is not None:
        # Augmentation: preserve existing keys
        if "type" not in frontmatter:
            frontmatter["type"] = existing_fm.get("type")
        if "title" not in frontmatter:
            frontmatter["title"] = existing_fm.get("title")
        if "resource" not in frontmatter:
            frontmatter["resource"] = existing_fm.get("resource")
        # Merge tags
        if "tags" in frontmatter and "tags" in existing_fm:
            existing_tags = existing_fm.get("tags") or []
            new_tags = frontmatter.get("tags") or []
            if isinstance(existing_tags, list) and isinstance(new_tags, list):
                merged = list(dict.fromkeys(existing_tags + new_tags))
                frontmatter["tags"] = merged
        # Merge sources
        if "sources" in frontmatter and "sources" in existing_fm:
            existing_sources = existing_fm.get("sources") or []
            new_sources = frontmatter.get("sources") or []
            if isinstance(existing_sources, list) and isinstance(new_sources, list):
                existing_ids = {s.get("id") for s in existing_sources if isinstance(s, dict)}
                merged = list(existing_sources)
                for src in new_sources:
                    if isinstance(src, dict) and src.get("id") not in existing_ids:
                        merged.append(src)
                frontmatter["sources"] = merged
        # Preserve body headings
        if existing_body:
            existing_headings = re.findall(r"^#{1,6}\s+.+$", existing_body, re.MULTILINE)
            new_headings = re.findall(r"^#{1,6}\s+.+$", body, re.MULTILINE)
            for eh in existing_headings:
                if eh not in new_headings:
                    result["warnings"].append(f"Existing heading '{eh}' not preserved in new body")

    # Set generated timestamp if not present
    if "generated" not in frontmatter:
        now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        frontmatter["generated"] = {"by": "okf_tool/1.0", "at": now}

    # Build and write
    doc = build_document(frontmatter, body)
    out_path = os.path.join(bundle_dir, concept_id + ".md")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(doc)

    result["path"] = out_path
    return result


def list_concepts(bundle_dir):
    """list_concepts() — List all concepts in a bundle.

    Returns list of dicts with id, path, type, title, description.
    """
    concepts = find_concepts(bundle_dir)
    result = []
    for rel_path, concept_id in concepts:
        fm, _, _ = read_existing_doc(concept_id, bundle_dir)
        result.append({
            "id": concept_id,
            "path": rel_path,
            "type": fm.get("type", ""),
            "title": fm.get("title", ""),
            "description": fm.get("description", ""),
            "tags": fm.get("tags", []),
            "status": fm.get("status", "stable"),
        })
    return result


def get_concept_info(concept_id, bundle_dir):
    """info(concept_id) — Get detailed info about a concept."""
    fm, body, raw = read_existing_doc(concept_id, bundle_dir)
    if fm is None:
        return None

    info = {
        "id": concept_id,
        "path": concept_id + ".md",
        "frontmatter": fm,
        "body_lines": len(body.split("\n")) if body else 0,
        "body_words": len(body.split()) if body else 0,
        "headings": re.findall(r"^#{1,6}\s+.+$", body or "", re.MULTILINE),
    }
    return info


# ── Validation ──────────────────────────────────────────────────────

def validate_bundle(bundle_dir, strict=False):
    """validate() — Validate an OKF bundle for conformance.

    Returns (errors, warnings) lists.
    """
    errors = []
    warnings = []

    concepts = find_concepts(bundle_dir)

    if not concepts:
        warnings.append("No concept documents found in bundle")

    for rel_path, concept_id in concepts:
        path = os.path.join(bundle_dir, rel_path)
        try:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
        except Exception as e:
            errors.append(f"{rel_path}: cannot read file: {e}")
            continue

        fm, body, raw = extract_frontmatter(text)

        # Check frontmatter present
        if not fm:
            errors.append(f"{rel_path}: no valid YAML frontmatter found")
            continue

        # Check required type field
        if not fm.get("type"):
            errors.append(f"{rel_path}: missing required field 'type'")

        # Type validation
        type_val = fm.get("type", "")
        if type_val and not isinstance(type_val, str):
            errors.append(f"{rel_path}: 'type' must be a string")

        # Description validation
        desc = fm.get("description", "")
        if desc:
            if isinstance(desc, str) and len(desc) > 1024:
                warnings.append(f"{rel_path}: description exceeds 1024 chars")
            if isinstance(desc, str) and re.search(r"<[^>]+>", desc):
                warnings.append(f"{rel_path}: description contains HTML/XML tags")

        # Status validation
        status = fm.get("status")
        if status and status not in ("draft", "stable", "deprecated"):
            warnings.append(f"{rel_path}: invalid status '{status}' (expected draft|stable|deprecated)")

        # stale_after validation
        stale = fm.get("stale_after")
        if stale:
            try:
                datetime.datetime.strptime(str(stale), "%Y-%m-%d")
            except ValueError:
                warnings.append(f"{rel_path}: stale_after is not YYYY-MM-DD format")

        # sources validation
        sources = fm.get("sources")
        if sources:
            if not isinstance(sources, list):
                warnings.append(f"{rel_path}: sources should be a list")
            else:
                for i, src in enumerate(sources):
                    if isinstance(src, dict) and not src.get("resource"):
                        warnings.append(f"{rel_path}: sources[{i}] missing required 'resource'")

        # Body check
        if not body or not body.strip():
            warnings.append(f"{rel_path}: empty body")

    # Check for index.md at root (informational)
    index_path = os.path.join(bundle_dir, "index.md")
    if not os.path.isfile(index_path):
        warnings.append("No index.md at bundle root (optional but recommended)")

    return errors, warnings


# ── Index generation ────────────────────────────────────────────────

def generate_index(bundle_dir, target_dir=None, force=False):
    """index() — Generate index.md for a directory.

    Returns the generated content.
    """
    if target_dir is None:
        target_dir = bundle_dir

    concepts = find_concepts(target_dir, recursive=False)
    subdirs = []
    for entry in sorted(os.listdir(target_dir)):
        full = os.path.join(target_dir, entry)
        if os.path.isdir(full) and not entry.startswith("."):
            subdirs.append(entry)

    lines = []
    current_type = None

    # Group by type
    for rel_path, concept_id in concepts:
        fm, _, _ = read_existing_doc(concept_id, bundle_dir)
        ctype = fm.get("type", "Unknown")
        if ctype != current_type:
            current_type = ctype
            lines.append(f"## {current_type}")
            lines.append("")
        title = fm.get("title", concept_id.split("/")[-1])
        desc = fm.get("description", "")
        fname = rel_path.split("/")[-1]
        if desc:
            lines.append(f"* [{title}]({fname}) - {desc}")
        else:
            lines.append(f"* [{title}]({fname})")
    lines.append("")

    # Subdirectories
    if subdirs:
        lines.append("## Subdirectories")
        lines.append("")
        for sd in subdirs:
            lines.append(f"* [{sd}]({sd}/) - {sd} concepts")
        lines.append("")

    return "\n".join(lines)


# ── Crawl ───────────────────────────────────────────────────────────

def crawl_urls(seed_urls, max_pages=10, allowed_hosts=None, bundle_dir=None):
    """crawl() — Fetch seed URLs, follow relevant links, return fetched pages.

    Returns list of {url, markdown, links, title, status} dicts.
    """
    fetched = []
    to_fetch = list(seed_urls)
    seen = set()

    # Resolve allowed hosts
    if allowed_hosts is None:
        allowed_hosts = set()
        for url in seed_urls:
            parsed = urllib.parse.urlparse(url)
            allowed_hosts.add(parsed.hostname or "")

    def is_allowed(url):
        parsed = urllib.parse.urlparse(url)
        host = parsed.hostname or ""
        return host in allowed_hosts

    def is_worth_following(url, title=""):
        """Heuristic: skip nav, footer, marketing, login pages."""
        skip_patterns = [
            r"/login", r"/signin", r"/signup", r"/register",
            r"/about", r"/contact", r"/privacy", r"/terms",
            r"/cookie", r"/faq", r"/changelog", r"/roadmap",
            r"getting-started", r"quickstart", r"tutorial",
            r"/blog", r"/news", r"/press",
        ]
        lower_url = url.lower()
        lower_title = title.lower()
        for pat in skip_patterns:
            if pat in lower_url or pat in lower_title:
                return False
        return True

    while to_fetch and len(fetched) < max_pages:
        url = to_fetch.pop(0)
        if url in seen:
            continue
        seen.add(url)

        html_text, final_url, status = fetch_url_content(url)
        if not html_text or status != 200:
            fetched.append({
                "url": url,
                "markdown": "",
                "links": [],
                "title": "",
                "status": status,
                "error": f"HTTP {status}" if status else "fetch failed",
            })
            continue

        markdown = html_to_markdown(html_text)
        links = extract_links(html_text, final_url)

        # Extract title from HTML
        title_match = re.search(r"<title[^>]*>(.*?)</title>", html_text, re.IGNORECASE | re.DOTALL)
        title = html_mod.unescape(title_match.group(1).strip()) if title_match else ""

        fetched.append({
            "url": final_url,
            "markdown": markdown,
            "links": links,
            "title": title,
            "status": status,
        })

        # Queue relevant links for next round
        for link in links:
            if link not in seen and is_allowed(link) and is_worth_following(link):
                to_fetch.append(link)

    return fetched


# ── Scaffolding ─────────────────────────────────────────────────────

def scaffold_concept(concept_id, bundle_dir, type_name="Reference", title="",
                     description="", resource="", tags=None):
    """create() — Scaffold a new concept document with minimal frontmatter."""
    fm = {"type": type_name}
    if title:
        fm["title"] = title
    if description:
        fm["description"] = description
    if resource:
        fm["resource"] = resource
    if tags:
        fm["tags"] = tags if isinstance(tags, list) else [t.strip() for t in tags.split(",")]

    body = f"# {title or type_name}\n\n"
    if description:
        body += f"{description}\n\n"

    result = write_concept_doc(concept_id, fm, body, bundle_dir)
    return result


# ── Log ─────────────────────────────────────────────────────────────

def append_log(bundle_dir, dir_path=None, entry=None):
    """log() — Append an entry to log.md."""
    if dir_path is None:
        dir_path = bundle_dir
    log_path = os.path.join(dir_path, "log.md")

    existing = ""
    if os.path.isfile(log_path):
        with open(log_path, "r", encoding="utf-8") as f:
            existing = f.read()

    today = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")

    lines = []
    if not existing.strip():
        lines.append("# Directory Update Log")
        lines.append("")

    if entry:
        # Parse "action: message" format
        if ": " in entry:
            action, _, message = entry.partition(": ")
            lines.append(f"## {today}")
            lines.append(f"* **{action.strip()}**: {message.strip()}")
            lines.append("")
        else:
            lines.append(f"## {today}")
            lines.append(f"* {entry}")
            lines.append("")

    content = existing.rstrip() + "\n" + "\n".join(lines) + "\n"
    with open(log_path, "w", encoding="utf-8") as f:
        f.write(content)
    return log_path


# ── CLI ─────────────────────────────────────────────────────────────

def cmd_create(args):
    """Scaffold a new concept document."""
    bundle_dir = resolve_bundle_dir(args.bundle)
    tags = [t.strip() for t in args.tags.split(",")] if args.tags else None
    result = scaffold_concept(
        args.concept_id, bundle_dir,
        type_name=args.type, title=args.title,
        description=args.description, resource=args.resource, tags=tags,
    )
    if result["status"] == "ok":
        print(f"Created: {result['path']}")
        for w in result.get("warnings", []):
            print(f"  warning: {w}", file=sys.stderr)
    else:
        print(f"Error: {result.get('error', 'unknown')}", file=sys.stderr)
        sys.exit(1)


def cmd_read(args):
    """Read an existing concept document."""
    bundle_dir = resolve_bundle_dir(args.bundle)
    fm, body, raw = read_existing_doc(args.concept_id, bundle_dir)
    if fm is None:
        print(f"Error: concept not found: {args.concept_id}", file=sys.stderr)
        sys.exit(1)
    if args.format == "frontmatter":
        print(serialize_yaml(fm))
    elif args.format == "body":
        print(body)
    elif args.format == "json":
        print(json.dumps({"frontmatter": fm, "body": body}, indent=2, ensure_ascii=False))
    else:
        # Full document
        print(build_document(fm, body))


def cmd_write(args):
    """Write or update a concept document."""
    bundle_dir = resolve_bundle_dir(args.bundle)

    # Parse frontmatter YAML
    frontmatter = parse_yaml_simple(args.frontmatter)

    # Body: read from file or use provided text
    body = args.body
    if args.body_file:
        with open(args.body_file, "r", encoding="utf-8") as f:
            body = f.read()

    result = write_concept_doc(args.concept_id, frontmatter, body, bundle_dir)
    if result["status"] == "ok":
        print(f"Written: {result['path']}")
        for w in result.get("warnings", []):
            print(f"  warning: {w}", file=sys.stderr)
    else:
        print(f"Error: {result.get('error', 'unknown')}", file=sys.stderr)
        sys.exit(1)


def cmd_list(args):
    """List all concepts in a bundle."""
    bundle_dir = resolve_bundle_dir(args.bundle)
    concepts = list_concepts(bundle_dir)

    if args.json:
        print(json.dumps(concepts, indent=2, ensure_ascii=False))
    elif not concepts:
        print("No concepts found.")
    else:
        for c in concepts:
            title = c.get("title") or c["id"]
            desc = c.get("description", "")
            tag_str = f" [{', '.join(c['tags'])}]" if c.get("tags") else ""
            print(f"  {c['id']:<40} {c['type']:<25} {title}{tag_str}")
            if desc:
                print(f"    {desc}")


def cmd_fetch(args):
    """Fetch a URL and output as markdown, HTML, links, or JSON."""
    html_text, final_url, status = fetch_url_content(args.url)

    if status != 200:
        print(f"Error: HTTP {status} fetching {args.url}", file=sys.stderr)
        sys.exit(1)

    if args.format == "html":
        output = html_text
    elif args.format == "links":
        links = extract_links(html_text, args.url)
        output = "\n".join(links)
    elif args.format == "json":
        markdown = html_to_markdown(html_text)
        links = extract_links(html_text, args.url)
        title_match = re.search(r"<title[^>]*>(.*?)</title>", html_text, re.IGNORECASE | re.DOTALL)
        title = html_mod.unescape(title_match.group(1).strip()) if title_match else ""
        output = json.dumps({
            "url": final_url,
            "title": title,
            "markdown": markdown,
            "links": links,
            "status": status,
        }, indent=2, ensure_ascii=False)
    else:
        output = html_to_markdown(html_text)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Written to {args.output}", file=sys.stderr)
    else:
        print(output)


def cmd_crawl(args):
    """Crawl seed URLs, extract content, optionally write as OKF concepts."""
    bundle_dir = resolve_bundle_dir(args.bundle) if args.bundle else None
    allowed_hosts = [h.strip() for h in args.allowed_hosts.split(",")] if args.allowed_hosts else None

    pages = crawl_urls(args.seed_urls, max_pages=args.max_pages,
                       allowed_hosts=allowed_hosts, bundle_dir=bundle_dir)

    if args.format == "json":
        print(json.dumps(pages, indent=2, ensure_ascii=False))
    elif args.format == "links":
        all_links = set()
        for p in pages:
            all_links.update(p.get("links", []))
        print("\n".join(sorted(all_links)))
    else:
        # Summary
        print(f"Fetched {len(pages)} pages (budget: {args.max_pages})")
        for p in pages:
            status = p.get("status", "?")
            title = p.get("title", "(no title)")
            url = p.get("url", "")
            link_count = len(p.get("links", []))
            if status != 200:
                print(f"  [{status}] {url} — {p.get('error', '')}")
            else:
                print(f"  [200] {title}")
                print(f"        {url} ({link_count} links)")

        # Write as concepts if output dir given
        if args.output and bundle_dir:
            for i, p in enumerate(pages):
                if p.get("status") != 200:
                    continue
                slug = urllib.parse.quote(p.get("title", f"page-{i}").lower().replace(" ", "-"))
                slug = re.sub(r"[^a-z0-9\-]", "", slug)[:64]
                concept_id = os.path.join(args.output, slug)

                fm = {
                    "type": "Reference",
                    "title": p.get("title", ""),
                    "description": "",
                    "resource": p.get("url", ""),
                    "sources": [{"id": "web-page", "resource": p.get("url", ""), "title": p.get("title", "")}],
                }
                body = p.get("markdown", "")
                result = write_concept_doc(concept_id, fm, body, bundle_dir)
                if result["status"] == "ok":
                    print(f"  Written: {result['path']}")


def cmd_validate(args):
    """Validate an OKF bundle."""
    bundle_dir = resolve_bundle_dir(args.bundle)
    errors, warnings = validate_bundle(bundle_dir, strict=args.strict)

    if args.json:
        print(json.dumps({
            "bundle": bundle_dir,
            "errors": errors,
            "warnings": warnings,
            "valid": len(errors) == 0,
        }, indent=2))
    else:
        if errors:
            print(f"Errors ({len(errors)}):")
            for e in errors:
                print(f"  ✗ {e}")
        if warnings:
            print(f"Warnings ({len(warnings)}):")
            for w in warnings:
                print(f"  ⚠ {w}")
        if not errors and not warnings:
            print("Bundle is valid with no warnings.")
        elif not errors:
            print(f"\nBundle is valid ({len(warnings)} warning(s)).")
        else:
            print(f"\nValidation failed ({len(errors)} error(s), {len(warnings)} warning(s)).")
            if args.strict:
                sys.exit(1)
            if errors:
                sys.exit(1)


def cmd_index(args):
    """Generate index.md for a directory."""
    bundle_dir = resolve_bundle_dir(args.bundle)
    target_dir = args.dir if args.dir else bundle_dir

    content = generate_index(bundle_dir, target_dir, force=args.force)

    index_path = os.path.join(target_dir, "index.md")
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Written to {args.output}", file=sys.stderr)
    else:
        if os.path.isfile(index_path) and not args.force:
            print(f"{index_path} already exists (use --force to overwrite)", file=sys.stderr)
            print(content)
        else:
            with open(index_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Written: {index_path}")


def cmd_info(args):
    """Show info about a concept."""
    bundle_dir = resolve_bundle_dir(args.bundle)
    info = get_concept_info(args.concept_id, bundle_dir)

    if info is None:
        print(f"Error: concept not found: {args.concept_id}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(info, indent=2, ensure_ascii=False))
    else:
        fm = info["frontmatter"]
        print(f"Concept: {info['id']}")
        print(f"Type:    {fm.get('type', '(none)')}")
        print(f"Title:   {fm.get('title', '(none)')}")
        print(f"Desc:    {fm.get('description', '(none)')}")
        print(f"Resource: {fm.get('resource', '(none)')}")
        tags = fm.get("tags", [])
        if tags:
            print(f"Tags:    {', '.join(str(t) for t in tags)}")
        status = fm.get("status", "stable")
        print(f"Status:  {status}")
        gen = fm.get("generated")
        if gen:
            print(f"Generated: {gen.get('by', '?')} at {gen.get('at', '?')}")
        verified = fm.get("verified")
        if verified:
            print(f"Verified:  {json.dumps(verified)}")
        sources = fm.get("sources")
        if sources:
            print(f"Sources:   {len(sources)} entries")
        print(f"Body:    {info['body_lines']} lines, {info['body_words']} words")
        if info.get("headings"):
            print(f"Headings:")
            for h in info["headings"]:
                print(f"  {h}")


def cmd_log(args):
    """Append entry to log.md."""
    bundle_dir = resolve_bundle_dir(args.bundle)
    if args.add:
        path = append_log(bundle_dir, entry=args.add)
        print(f"Appended to: {path}")
    else:
        log_path = os.path.join(bundle_dir, "log.md")
        if os.path.isfile(log_path):
            with open(log_path, "r", encoding="utf-8") as f:
                print(f.read())
        else:
            print("No log.md found.", file=sys.stderr)
            sys.exit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="okf",
        description="Open Knowledge Format (OKF v0.2) bundle tooling.",
    )
    subparsers = parser.add_subparsers(dest="command", help="Subcommand")

    # ── create ──────────────────────────────────────────────────────
    p_create = subparsers.add_parser("create", help="Scaffold a new concept document")
    p_create.add_argument("concept_id", help="Concept ID (relative path without .md)")
    p_create.add_argument("--type", default="Reference", help="Concept type (default: Reference)")
    p_create.add_argument("--title", default="", help="Display title")
    p_create.add_argument("--description", "-d", default="", help="One-line description")
    p_create.add_argument("--resource", "-r", default="", help="Canonical URI")
    p_create.add_argument("--tags", default="", help="Comma-separated tags")
    p_create.add_argument("--bundle", "-b", default=None, help="Bundle root directory")
    p_create.set_defaults(func=cmd_create)

    # ── read ────────────────────────────────────────────────────────
    p_read = subparsers.add_parser("read", help="Read an existing concept")
    p_read.add_argument("concept_id", help="Concept ID")
    p_read.add_argument("--format", "-f", choices=["full", "frontmatter", "body", "json"],
                        default="full", help="Output format")
    p_read.add_argument("--bundle", "-b", default=None, help="Bundle root directory")
    p_read.set_defaults(func=cmd_read)

    # ── write ───────────────────────────────────────────────────────
    p_write = subparsers.add_parser("write", help="Write or update a concept")
    p_write.add_argument("concept_id", help="Concept ID")
    p_write.add_argument("--frontmatter", required=True, help="YAML frontmatter text")
    p_write.add_argument("--body", default="", help="Body markdown text")
    p_write.add_argument("--body-file", help="Read body from file")
    p_write.add_argument("--bundle", "-b", default=None, help="Bundle root directory")
    p_write.set_defaults(func=cmd_write)

    # ── list ────────────────────────────────────────────────────────
    p_list = subparsers.add_parser("list", help="List all concepts in a bundle")
    p_list.add_argument("--bundle", "-b", default=None, help="Bundle root directory")
    p_list.add_argument("--json", "-j", action="store_true", help="Output as JSON")
    p_list.set_defaults(func=cmd_list)

    # ── fetch ───────────────────────────────────────────────────────
    p_fetch = subparsers.add_parser("fetch", help="Fetch a URL as markdown/HTML/links")
    p_fetch.add_argument("url", help="URL to fetch")
    p_fetch.add_argument("--format", "-f", choices=["md", "html", "links", "json"],
                         default="md", help="Output format")
    p_fetch.add_argument("--output", "-o", help="Output file path")
    p_fetch.set_defaults(func=cmd_fetch)

    # ── crawl ───────────────────────────────────────────────────────
    p_crawl = subparsers.add_parser("crawl", help="Crawl seed URLs, extract content")
    p_crawl.add_argument("seed_urls", nargs="+", help="Seed URLs to start from")
    p_crawl.add_argument("--max-pages", "-n", type=int, default=10, help="Max pages to fetch")
    p_crawl.add_argument("--allowed-hosts", default="", help="Comma-separated allowed hosts")
    p_crawl.add_argument("--output", "-o", help="Output dir for concepts (relative to bundle)")
    p_crawl.add_argument("--bundle", "-b", default=None, help="Bundle root directory")
    p_crawl.add_argument("--format", "-f", choices=["summary", "json", "links"],
                         default="summary", help="Output format")
    p_crawl.set_defaults(func=cmd_crawl)

    # ── validate ────────────────────────────────────────────────────
    p_val = subparsers.add_parser("validate", help="Validate bundle conformance")
    p_val.add_argument("--bundle", "-b", default=None, help="Bundle root directory")
    p_val.add_argument("--strict", "-s", action="store_true", help="Exit non-zero on warnings")
    p_val.add_argument("--json", "-j", action="store_true", help="Output as JSON")
    p_val.set_defaults(func=cmd_validate)

    # ── index ───────────────────────────────────────────────────────
    p_idx = subparsers.add_parser("index", help="Generate index.md")
    p_idx.add_argument("--bundle", "-b", default=None, help="Bundle root directory")
    p_idx.add_argument("--dir", "-d", default=None, help="Target directory")
    p_idx.add_argument("--force", action="store_true", help="Overwrite existing index.md")
    p_idx.add_argument("--output", "-o", help="Output file path")
    p_idx.set_defaults(func=cmd_index)

    # ── info ────────────────────────────────────────────────────────
    p_info = subparsers.add_parser("info", help="Show concept info")
    p_info.add_argument("concept_id", help="Concept ID")
    p_info.add_argument("--bundle", "-b", default=None, help="Bundle root directory")
    p_info.add_argument("--json", "-j", action="store_true", help="Output as JSON")
    p_info.set_defaults(func=cmd_info)

    # ── log ─────────────────────────────────────────────────────────
    p_log = subparsers.add_parser("log", help="View or append to log.md")
    p_log.add_argument("--bundle", "-b", default=None, help="Bundle root directory")
    p_log.add_argument("--add", "-a", help="Append entry (format: 'Action: message')")
    p_log.set_defaults(func=cmd_log)

    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
