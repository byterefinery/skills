"""OKF (Open Knowledge Format) bundle management tool.

Implements the functions referenced by OKF reference_agent and web_ingestion_agent
prompts: list_concepts, read_existing_doc, write_concept_doc, plus utilities for
validation, index generation, link extraction, token estimation, and multi-concept
ingestion.

Document I/O only — fetching URLs, searching the web, and converting PDF/Office
files to markdown are handled by other skills (webfetch, websearch, markdown).

Usage:
    okf.sh <command> --bundle <path> [options]

Commands:
    create-bundle   Create a new empty bundle directory
    list-concepts   List all concepts in a bundle
    read-doc        Read an existing concept document
    write-doc       Write or update a concept document
    ingest          Ingest markdown, split into multiple concepts
    extract-links   Extract cross-links from a markdown document
    validate        Validate a bundle or single concept for OKF conformance
    index           Generate or update an index.md file
    tokens          Estimate token count of a document or bundle
"""

import argparse
import datetime
import json
import os
import re
import signal
import sys
import textwrap
import unicodedata
from pathlib import Path

# Ignore SIGPIPE — handles `cmd | head -N` gracefully
signal.signal(signal.SIGPIPE, signal.SIG_DFL)

try:
    _UTC = datetime.UTC
except AttributeError:
    _UTC = datetime.timezone.utc


# ---------------------------------------------------------------------------
# YAML subset parser / serializer (stdlib only)
# ---------------------------------------------------------------------------

def _split_top_level_commas(s):
    """Split string on commas at nesting depth 0 (outside {}, [], quotes)."""
    parts = []
    current = []
    depth = 0
    in_quote = None
    i = 0
    while i < len(s):
        ch = s[i]
        if in_quote:
            current.append(ch)
            if ch == '\\' and i + 1 < len(s):
                i += 1
                current.append(s[i])
            elif ch == in_quote:
                in_quote = None
        elif ch in ('"', "'"):
            in_quote = ch
            current.append(ch)
        elif ch in ('{', '['):
            depth += 1
            current.append(ch)
        elif ch in ('}', ']'):
            depth = max(0, depth - 1)
            current.append(ch)
        elif ch == ',' and depth == 0:
            parts.append(''.join(current).strip())
            current = []
        else:
            current.append(ch)
        i += 1
    remainder = ''.join(current).strip()
    if remainder:
        parts.append(remainder)
    return parts


def _strip_yaml_tag(s):
    """Remove YAML type tags like !!str, !!float, !!int, !!bool."""
    return re.sub(r'^!!(str|float|int|bool|binary|yaml):', '', s.strip())


def yaml_parse_value(raw):
    """Parse a YAML scalar, inline mapping, or inline list value."""
    if not raw or not raw.strip():
        return ''
    s = raw.strip()
    # Quoted strings
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        inner = s[1:-1]
        if s.startswith('"'):
            inner = inner.replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')
        return inner
    # Inline mapping
    if s.startswith('{') and s.endswith('}'):
        inner = s[1:-1].strip()
        if not inner:
            return {}
        result = {}
        for pair in _split_top_level_commas(inner):
            if ':' not in pair:
                continue
            k, v = pair.split(':', 1)
            result[yaml_parse_value(k.strip())] = yaml_parse_value(v.strip())
        return result
    # Inline list
    if s.startswith('[') and s.endswith(']'):
        inner = s[1:-1].strip()
        if not inner:
            return []
        return [yaml_parse_value(item) for item in _split_top_level_commas(inner)]
    # YAML type tag
    s = _strip_yaml_tag(s)
    # Booleans
    if s.lower() in ('true', 'yes'):
        return True
    if s.lower() in ('false', 'no'):
        return False
    # Null
    if s.lower() in ('null', '~', ''):
        return None
    # Integer
    if re.match(r'^-?\d+$', s):
        return int(s)
    # Float
    if re.match(r'^-?\d+\.\d+$', s):
        return float(s)
    return s


def yaml_parse(text):
    """Parse a YAML document string into a Python object.

    Handles: mappings, lists, nested mappings, inline {maps} and [lists],
    quoted strings, scalars. Does NOT handle multi-line strings, anchors,
    or other advanced YAML features.
    """
    lines = text.split('\n')
    filtered = []
    for line in lines:
        stripped = line.rstrip()
        if stripped.lstrip().startswith('#'):
            continue
        if stripped.strip():
            filtered.append(stripped)
    if not filtered:
        return {}
    first = filtered[0].lstrip()
    if first.startswith('- '):
        return _parse_list(filtered, 0, 0)[0]
    return _parse_mapping(filtered, 0, 0)[0]


def _parse_list(lines, idx, base_indent):
    result = []
    while idx < len(lines):
        line = lines[idx]
        stripped = line.lstrip()
        indent = len(line) - len(stripped)
        if indent < base_indent:
            break
        if indent > base_indent:
            break
        if not stripped.startswith('- '):
            break
        item_text = stripped[2:]
        if item_text.startswith('{') and item_text.endswith('}'):
            result.append(yaml_parse_value(item_text))
            idx += 1
        elif ':' in item_text and not item_text.startswith('['):
            key, val = item_text.split(':', 1)
            key = key.strip()
            val = val.strip()
            entry = {}
            if val:
                entry[key] = yaml_parse_value(val)
            else:
                entry[key] = None
            child_indent = indent + 2
            idx += 1
            while idx < len(lines):
                cline = lines[idx]
                cstripped = cline.lstrip()
                cindent = len(cline) - len(cstripped)
                if cindent < child_indent:
                    break
                if cindent == child_indent and cstripped.startswith('- '):
                    break
                if cindent >= child_indent and ':' in cstripped:
                    ck, cv = cstripped.split(':', 1)
                    entry[ck.strip()] = yaml_parse_value(cv)
                    idx += 1
                else:
                    idx += 1
            result.append(entry)
        else:
            result.append(yaml_parse_value(item_text))
            idx += 1
    return result, idx


def _parse_mapping(lines, idx, base_indent):
    result = {}
    while idx < len(lines):
        line = lines[idx]
        stripped = line.lstrip()
        indent = len(line) - len(stripped)
        if indent < base_indent:
            break
        if indent > base_indent:
            idx += 1
            continue
        if stripped.startswith('- '):
            break
        if ':' not in stripped:
            idx += 1
            continue
        key, val = stripped.split(':', 1)
        key = key.strip()
        val = val.strip()
        if val.startswith('{') and val.endswith('}'):
            result[key] = yaml_parse_value(val)
            idx += 1
        elif val.startswith('[') and val.endswith(']'):
            result[key] = yaml_parse_value(val)
            idx += 1
        elif val:
            result[key] = yaml_parse_value(val)
            idx += 1
        else:
            if idx + 1 < len(lines):
                next_line = lines[idx + 1]
                next_stripped = next_line.lstrip()
                next_indent = len(next_line) - len(next_stripped)
                if next_indent > indent and next_stripped.startswith('- '):
                    lst, new_idx = _parse_list(lines, idx + 1, next_indent)
                    result[key] = lst
                    idx = new_idx
                elif next_indent > indent and ':' in next_stripped:
                    sub, new_idx = _parse_mapping(lines, idx + 1, next_indent)
                    result[key] = sub
                    idx = new_idx
                else:
                    result[key] = ''
                    idx += 1
            else:
                result[key] = ''
                idx += 1
    return result, idx


def yaml_serialize(obj, indent=0):
    """Serialize a Python object to a YAML string (subset)."""
    prefix = '  ' * indent
    if obj is None:
        return 'null'
    if isinstance(obj, bool):
        return 'true' if obj else 'false'
    if isinstance(obj, int):
        return str(obj)
    if isinstance(obj, float):
        return str(obj)
    if isinstance(obj, str):
        if (any(ch in obj for ch in ':{}[]#&*!|>\"\'%@`')
                or obj.startswith('- ')
                or obj in ('null', 'true', 'false', 'yes', 'no')
                or obj.isdigit()
                or (obj.replace('.', '', 1).isdigit() and '.' in obj)):
            escaped = obj.replace('\\', '\\\\').replace('"', '\\"')
            return f'"{escaped}"'
        return obj
    if isinstance(obj, list):
        if not obj:
            return '[]'
        if all(isinstance(item, (str, int, float, bool)) for item in obj):
            return '[' + ', '.join(yaml_serialize(item, indent) for item in obj) + ']'
        lines = []
        for item in obj:
            if isinstance(item, dict):
                # Use multi-line format for list-of-mappings (matches OKF style)
                first = True
                for k, v in item.items():
                    val_str = yaml_serialize(v, 0)
                    if first:
                        lines.append(f'{prefix}- {k}: {val_str}')
                        first = False
                    else:
                        lines.append(f'{prefix}  {k}: {val_str}')
            else:
                lines.append(f'{prefix}- {yaml_serialize(item, indent)}')
        return '\n'.join(lines)
    if isinstance(obj, dict):
        if not obj:
            return '{}'
        # Use inline { } format for small dicts with simple scalar values
        if len(obj) <= 4 and all(isinstance(v, (str, int, float, bool, type(None))) for v in obj.values()):
            inline = ', '.join(f'{k}: {yaml_serialize(v, 0)}' for k, v in obj.items())
            return '{' + inline + '}'
        lines = []
        for k, v in obj.items():
            val_str = yaml_serialize(v, indent + 1)
            # If value spans multiple lines, put it on the next line
            if '\n' in val_str:
                lines.append(f'{prefix}{k}:')
                lines.append(val_str)
            else:
                lines.append(f'{prefix}{k}: {val_str}')
        return '\n'.join(lines)
    return str(obj)


# ---------------------------------------------------------------------------
# Frontmatter I/O
# ---------------------------------------------------------------------------

def parse_frontmatter(text):
    """Extract and parse YAML frontmatter from a markdown document.

    Returns (frontmatter_dict, body_string) or ({}, full_text) if no frontmatter.
    """
    text = text.lstrip('\n')
    if not text.startswith('---'):
        return {}, text
    end = text.find('---', 3)
    if end == -1:
        return {}, text
    yaml_text = text[3:end].strip()
    body = text[end + 3:].strip()
    try:
        fm = yaml_parse(yaml_text)
        if not isinstance(fm, dict):
            fm = {'_raw': fm}
    except Exception:
        fm = {'_parse_error': yaml_text}
    return fm, body


def serialize_frontmatter(fm):
    """Serialize a frontmatter dict to a YAML string."""
    return yaml_serialize(fm)


def build_document(fm, body):
    """Build a complete OKF concept document from frontmatter dict and body string."""
    parts = ['---']
    if fm:
        parts.append(serialize_frontmatter(fm))
    parts.append('---')
    if body:
        parts.append(body)
    return '\n'.join(parts) + '\n'


# ---------------------------------------------------------------------------
# Slug generation
# ---------------------------------------------------------------------------

def to_slug(text, max_len=64):
    """Convert text to a URL-safe slug (lowercase, hyphenated)."""
    # Normalize unicode
    text = unicodedata.normalize('NFKD', text)
    # Lowercase
    text = text.lower()
    # Replace non-alphanumeric with hyphens
    text = re.sub(r'[^a-z0-9\u00c0-\u024f-]', '-', text)
    # Collapse multiple hyphens
    text = re.sub(r'-+', '-', text)
    # Strip leading/trailing hyphens
    text = text.strip('-')
    # Truncate
    if len(text) > max_len:
        text = text[:max_len].rstrip('-')
    return text


# ---------------------------------------------------------------------------
# Bundle operations
# ---------------------------------------------------------------------------

RESERVED_FILES = {'index.md', 'log.md'}


def list_concepts(bundle_path):
    """List all concept documents in a bundle directory.

    Returns a list of dicts with keys: id, path, type, title, description.
    Concept ID is the relative path with .md suffix removed.
    """
    bundle = Path(bundle_path).resolve()
    if not bundle.is_dir():
        print(f"Error: '{bundle_path}' is not a directory", file=sys.stderr)
        sys.exit(1)
    concepts = []
    for md_file in sorted(bundle.rglob('*.md')):
        name = md_file.name
        rel = md_file.relative_to(bundle)
        if name in RESERVED_FILES:
            continue
        concept_id = str(rel)[: -3]  # strip .md
        try:
            text = md_file.read_text(encoding='utf-8')
            fm, _ = parse_frontmatter(text)
        except Exception:
            fm = {}
        concepts.append({
            'id': concept_id,
            'path': str(rel),
            'type': fm.get('type', ''),
            'title': fm.get('title', ''),
            'description': fm.get('description', ''),
        })
    return concepts


def read_existing_doc(concept_id, bundle_path):
    """Read an existing concept document by its concept ID.

    Returns dict with keys: id, frontmatter, body, raw.
    Returns None if the document does not exist.
    """
    bundle = Path(bundle_path).resolve()
    doc_path = bundle / (concept_id + '.md')
    if not doc_path.is_file():
        return None
    raw = doc_path.read_text(encoding='utf-8')
    fm, body = parse_frontmatter(raw)
    return {
        'id': concept_id,
        'frontmatter': fm,
        'body': body,
        'raw': raw,
    }


def write_concept_doc(concept_id, frontmatter, body, bundle_path, dry_run=False):
    """Write or update a concept document.

    Creates parent directories as needed. Validates that type is present.
    Auto-fills generated field if missing.

    Returns the document path written (or None if dry_run).
    """
    if not isinstance(frontmatter, dict):
        print(f"Error: frontmatter must be a dict, got {type(frontmatter).__name__}", file=sys.stderr)
        sys.exit(1)
    if not frontmatter.get('type'):
        print("Error: frontmatter must include a 'type' field", file=sys.stderr)
        sys.exit(1)
    if 'generated' not in frontmatter:
        frontmatter['generated'] = {
            'by': 'okf_tool/okf',
            'at': datetime.datetime.now(_UTC).strftime('%Y-%m-%dT%H:%M:%SZ'),
        }
    bundle = Path(bundle_path).resolve()
    doc_path = bundle / (concept_id + '.md')
    doc_path.parent.mkdir(parents=True, exist_ok=True)
    doc_text = build_document(frontmatter, body)
    if dry_run:
        print(doc_text, end='')
        return None
    doc_path.write_text(doc_text, encoding='utf-8')
    return str(doc_path.relative_to(bundle))


# ---------------------------------------------------------------------------
# Multi-concept ingestion
# ---------------------------------------------------------------------------

def split_at_h1(body):
    """Split markdown body at H1 headings (# ...).

    Returns list of (heading_text, section_body) tuples.
    If no H1 headings, returns single tuple with empty heading.
    """
    sections = []
    lines = body.split('\n')
    current_heading = None
    current_lines = []
    in_fence = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith('```'):
            in_fence = not in_fence
            current_lines.append(line)
            continue
        if in_fence:
            current_lines.append(line)
            continue

        m = re.match(r'^#\s+(.+)$', line)
        if m:
            # Save previous section
            if current_heading is not None:
                sections.append((current_heading, '\n'.join(current_lines)))
            current_heading = m.group(1).strip()
            current_lines = []
        else:
            current_lines.append(line)

    # Save last section
    if current_heading is not None:
        sections.append((current_heading, '\n'.join(current_lines)))
    elif current_lines:
        sections.append(('untitled', '\n'.join(current_lines)))

    return sections


def extract_description(body, max_chars=200):
    """Extract a one-line description from body text.

    Takes the first meaningful sentence or first line of prose.
    """
    # Remove frontmatter if present
    fm, clean_body = parse_frontmatter(body)
    text = clean_body if clean_body else body

    # Strip headings
    text = re.sub(r'^#+\s+.+$', '', text, flags=re.MULTILINE)
    # Strip code blocks
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    # Strip horizontal rules
    text = re.sub(r'^---+$', '', text, flags=re.MULTILINE)

    # Get first meaningful line
    for line in text.split('\n'):
        line = line.strip()
        if line and not line.startswith(('```', '#', '-', '*', '[', '---')):
            # Truncate to max_chars
            if len(line) > max_chars:
                line = line[:max_chars].rsplit(' ', 1)[0] + '...'
            return line
    return ''


def ingest_markdown(text, bundle_path, concept_type='Document', output_dir='documents',
                    source_id=None, source_resource=None, source_title=None, dry_run=False):
    """Ingest markdown text, split at H1 headings, write as multiple concepts.

    Returns list of concept IDs written.
    """
    # Strip existing frontmatter
    fm, body = parse_frontmatter(text)

    # Split at H1 headings
    sections = split_at_h1(body)

    if not sections:
        print("Warning: no content to ingest", file=sys.stderr)
        return []

    bundle = Path(bundle_path).resolve()
    bundle.mkdir(parents=True, exist_ok=True)
    output_dir_path = bundle / output_dir
    output_dir_path.mkdir(parents=True, exist_ok=True)

    written = []
    all_concepts = []
    slug_counts = {}  # Track slug occurrences for deduplication

    for heading_text, section_body in sections:
        # Generate concept ID with deduplication
        slug = to_slug(heading_text)
        if not slug:
            slug = 'untitled'
        slug_counts[slug] = slug_counts.get(slug, 0) + 1
        if slug_counts[slug] > 1:
            slug = f"{slug}-{slug_counts[slug]}"
        concept_id = f"{output_dir}/{slug}"

        # Clean up section body
        section_body = section_body.strip()
        if not section_body:
            continue

        # Extract description
        description = extract_description(section_body)

        # Build frontmatter
        concept_fm = {
            'type': concept_type,
            'title': heading_text,
        }
        if description:
            concept_fm['description'] = description
        if source_resource:
            concept_fm['resource'] = source_resource

        # Build sources
        sources = []
        if source_resource:
            src = {'id': source_id or to_slug(source_resource), 'resource': source_resource}
            if source_title:
                src['title'] = source_title
            sources.append(src)
        if sources:
            concept_fm['sources'] = sources

        # Add cross-links to siblings
        all_concepts.append((concept_id, heading_text))

    # Now write all concepts with cross-links
    for concept_id, heading_text in all_concepts:
        # Find the section body for this concept
        section_body = ''
        for h, b in sections:
            if to_slug(h) == to_slug(heading_text):
                section_body = b.strip()
                break

        if not section_body:
            continue

        description = extract_description(section_body)

        concept_fm = {
            'type': concept_type,
            'title': heading_text,
        }
        if description:
            concept_fm['description'] = description
        if source_resource:
            concept_fm['resource'] = source_resource

        sources = []
        if source_resource:
            src = {'id': source_id or to_slug(source_resource), 'resource': source_resource}
            if source_title:
                src['title'] = source_title
            sources.append(src)
        if sources:
            concept_fm['sources'] = sources

        # Prepend H1 heading to body (validator expects it)
        body_with_heading = f'# {heading_text}\n\n{section_body}' if section_body else f'# {heading_text}\n'

        # Add cross-links section
        siblings = [(cid, ht) for cid, ht in all_concepts if cid != concept_id]
        if siblings:
            cross_links = '\n\n# Related\n\n'
            for sid, stitle in siblings:
                # Compute relative path
                rel = Path(sid).relative_to(Path(concept_id).parent)
                cross_links += f'- [{stitle}]({rel}.md)\n'
            body_with_heading = body_with_heading + cross_links

        path = write_concept_doc(concept_id, concept_fm, body_with_heading, bundle_path, dry_run=dry_run)
        if path:
            written.append(concept_id)
        elif dry_run:
            written.append(concept_id)

    return written


# ---------------------------------------------------------------------------
# Link extraction
# ---------------------------------------------------------------------------

def extract_links(text):
    """Extract markdown links from text.

    Returns list of dicts: {text, target, line}.
    Skips links inside fenced code blocks.
    """
    links = []
    in_fence = False
    for i, line in enumerate(text.split('\n'), 1):
        stripped = line.strip()
        if stripped.startswith('```'):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for m in re.finditer(r'\[([^\]]+)\]\(([^)]+)\)', line):
            links.append({'text': m.group(1), 'target': m.group(2), 'line': i})
    return links


def extract_external_urls(text):
    """Extract external URLs from markdown text (http/https links only)."""
    urls = []
    in_fence = False
    for line in text.split('\n'):
        stripped = line.strip()
        if stripped.startswith('```'):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for m in re.finditer(r'\[([^\]]*)\]\((https?://[^)]+)\)', line):
            urls.append({'text': m.group(1) or m.group(2), 'url': m.group(2)})
        for m in re.finditer(r'(https?://\S+)', line):
            url = m.group(1).rstrip(')')
            urls.append({'text': url, 'url': url})
    return urls


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_concept(fm, body, concept_id=None, doc_path=None):
    """Validate a single concept's frontmatter and body.

    Returns list of (severity, message) tuples. severity: 'error' or 'warn'.
    """
    issues = []
    if not isinstance(fm, dict):
        issues.append(('error', 'Frontmatter is not a YAML mapping'))
        return issues
    if not fm.get('type'):
        issues.append(('error', "Missing required 'type' field"))
    elif not isinstance(fm['type'], str):
        issues.append(('error', "'type' must be a string"))
    if fm.get('title') and not isinstance(fm['title'], str):
        issues.append(('error', "'title' must be a string"))
    if fm.get('description') and not isinstance(fm['description'], str):
        issues.append(('error', "'description' must be a string"))
    if fm.get('resource') and not isinstance(fm['resource'], str):
        issues.append(('error', "'resource' must be a string"))
    if fm.get('tags'):
        if isinstance(fm['tags'], list):
            for t in fm['tags']:
                if not isinstance(t, str):
                    issues.append(('warn', f"Tag {t!r} is not a string"))
        elif not isinstance(fm['tags'], str):
            issues.append(('warn', "'tags' should be a list or comma-separated string"))
    if fm.get('status') and fm['status'] not in ('draft', 'stable', 'deprecated'):
        issues.append(('warn', f"'status' value '{fm['status']}' is not one of: draft, stable, deprecated"))
    if fm.get('stale_after'):
        try:
            datetime.date.fromisoformat(str(fm['stale_after']))
        except (ValueError, TypeError):
            issues.append(('warn', "'stale_after' should be a YYYY-MM-DD date"))
    if fm.get('sources'):
        if not isinstance(fm['sources'], list):
            issues.append(('error', "'sources' must be a list"))
        else:
            for i, src in enumerate(fm['sources']):
                if not isinstance(src, dict):
                    issues.append(('error', f"sources[{i}] must be a mapping"))
                    continue
                if not src.get('resource'):
                    issues.append(('error', f"sources[{i}] missing required 'resource'"))
    if fm.get('generated'):
        gen = fm['generated']
        if isinstance(gen, dict) and not gen.get('by'):
            issues.append(('warn', "'generated' should include 'by' (actor) field"))
    if fm.get('verified'):
        verified = fm['verified'] if isinstance(fm['verified'], list) else [fm['verified']]
        for i, v in enumerate(verified):
            if isinstance(v, dict) and not v.get('by'):
                issues.append(('warn', f"verified[{i}] should include 'by' (actor) field"))
    if body and not re.search(r'^#\s+', body, re.MULTILINE):
        issues.append(('warn', 'Body has no level-1 heading'))
    label = concept_id or (str(doc_path) if doc_path else 'unknown')
    if issues:
        return issues
    return [('info', 'OK')]


def validate_bundle(bundle_path):
    """Validate all concepts in a bundle.

    Returns list of (concept_id, [(severity, message), ...]).
    """
    results = []
    for concept in list_concepts(bundle_path):
        doc = read_existing_doc(concept['id'], bundle_path)
        if doc:
            issues = validate_concept(doc['frontmatter'], doc['body'], concept['id'])
            results.append((concept['id'], issues))
    return results


# ---------------------------------------------------------------------------
# Index generation
# ---------------------------------------------------------------------------

def generate_index(bundle_path, output=None):
    """Generate an index.md file for a bundle directory.

    Groups concepts by their immediate subdirectory (or 'root' for top-level).
    Returns the generated markdown text.
    """
    bundle = Path(bundle_path).resolve()
    concepts = list_concepts(str(bundle))
    groups = {}
    for c in concepts:
        parts = c['id'].split('/')
        if len(parts) > 1:
            group = parts[0]
        else:
            group = 'root'
        groups.setdefault(group, []).append(c)
    lines = []
    for group in sorted(groups.keys()):
        if group == 'root':
            lines.append('# Concepts')
        else:
            lines.append(f'# {group.title().replace("-", " ")}')
        lines.append('')
        for c in groups[group]:
            title = c.get('title') or c['id'].split('/')[-1].replace('-', ' ').title()
            desc = f' — {c["description"]}' if c.get('description') else ''
            rel_path = c['path']
            if group != 'root':
                rel_path = c['id'].split('/', 1)[1] + '.md'
            lines.append(f'* [{title}]({rel_path}){desc}')
        lines.append('')
    return '\n'.join(lines)


# ---------------------------------------------------------------------------
# Token estimation
# ---------------------------------------------------------------------------

def estimate_tokens(text):
    """Rough token estimate: ~4 chars per token for English text.

    More accurate than word count, cheaper than actual tokenization.
    """
    if not text:
        return 0
    return max(1, len(text) // 4)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _print_json(data):
    """Print data as formatted JSON."""
    print(json.dumps(data, indent=2, ensure_ascii=False, default=str))


def cmd_create_bundle(args):
    bundle = Path(args.bundle).resolve()
    bundle.mkdir(parents=True, exist_ok=True)
    if args.version:
        index = f'---\nokf_version: "{args.version}"\n---\n\n'
        index += f'# {args.name or "OKF Bundle"}\n\n'
        (bundle / 'index.md').write_text(index, encoding='utf-8')
        print(f"Created bundle at {bundle} (OKF v{args.version})")
    else:
        print(f"Created bundle at {bundle}")


def cmd_list_concepts(args):
    concepts = list_concepts(args.bundle)
    if args.json:
        _print_json(concepts)
    else:
        if not concepts:
            print("No concepts found.")
            return
        for c in concepts:
            title = c.get('title') or c['id'].split('/')[-1]
            ctype = c.get('type', '?')
            print(f"  {c['id']:<40s} {ctype:<25s} {title}")
        print(f"\n{len(concepts)} concept(s)")


def cmd_read_doc(args):
    doc = read_existing_doc(args.concept, args.bundle)
    if doc is None:
        print(f"Error: concept '{args.concept}' not found", file=sys.stderr)
        sys.exit(1)
    if args.json:
        _print_json({'id': doc['id'], 'frontmatter': doc['frontmatter'], 'body': doc['body']})
    elif args.frontmatter:
        print(serialize_frontmatter(doc['frontmatter']))
    elif args.body:
        print(doc['body'])
    else:
        print(doc['raw'], end='')


def cmd_write_doc(args):
    fm = {}
    if args.frontmatter_file:
        with open(args.frontmatter_file) as f:
            fm = yaml_parse(f.read())
    elif args.frontmatter:
        fm = yaml_parse(args.frontmatter)
    if args.type and 'type' not in fm:
        fm['type'] = args.type
    body = ''
    if args.body == '-':
        body = sys.stdin.read()
    elif args.body:
        body = args.body
    elif args.body_stdin:
        body = sys.stdin.read()
    if args.json_fm and args.frontmatter_file:
        with open(args.frontmatter_file) as f:
            fm = json.load(f)
    elif args.json_fm and args.frontmatter:
        fm = json.loads(args.frontmatter)
    if not fm.get('type'):
        print("Error: 'type' field is required in frontmatter", file=sys.stderr)
        sys.exit(1)
    path = write_concept_doc(args.concept, fm, body, args.bundle, dry_run=args.dry_run)
    if args.dry_run:
        pass
    else:
        print(f"Written: {path}")


def cmd_ingest(args):
    if args.file:
        text = Path(args.file).read_text(encoding='utf-8')
    elif args.body == '-':
        text = sys.stdin.read()
    elif args.body:
        text = args.body
    else:
        text = sys.stdin.read()

    source_id = args.source_id
    source_resource = args.resource
    source_title = args.title

    written = ingest_markdown(
        text,
        bundle_path=args.bundle,
        concept_type=args.type,
        output_dir=args.output_dir,
        source_id=source_id,
        source_resource=source_resource,
        source_title=source_title,
        dry_run=args.dry_run,
    )

    if args.json:
        _print_json({'written': written, 'count': len(written)})
    else:
        if not written:
            print("No concepts written.")
            return
        for cid in written:
            print(f"  {cid}")
        print(f"\n{len(written)} concept(s) written")


def cmd_extract_links(args):
    if args.file:
        text = Path(args.file).read_text(encoding='utf-8')
    else:
        text = sys.stdin.read()
    links = extract_links(text)
    if args.json:
        _print_json(links)
    else:
        if not links:
            print("No links found.")
            return
        for link in links:
            print(f"  L{link['line']:>4}: [{link['text']}]({link['target']})")
        print(f"\n{len(links)} link(s)")


def cmd_validate(args):
    if args.file:
        text = Path(args.file).read_text(encoding='utf-8')
        fm, body = parse_frontmatter(text)
        issues = validate_concept(fm, body, doc_path=args.file)
        for sev, msg in issues:
            tag = 'ERROR' if sev == 'error' else ('WARN' if sev == 'warn' else 'INFO')
            print(f"  [{tag}] {msg}")
    elif args.bundle:
        results = validate_bundle(args.bundle)
        total_errors = 0
        total_warns = 0
        for cid, issues in results:
            has_error = False
            for sev, msg in issues:
                if sev == 'error':
                    has_error = True
                    total_errors += 1
                elif sev == 'warn':
                    total_warns += 1
                if args.verbose or sev in ('error', 'warn'):
                    if sev == 'info':
                        print(f"  [OK]   {cid}")
                    else:
                        tag = 'ERROR' if sev == 'error' else 'WARN'
                        print(f"  [{tag}] {cid}: {msg}")
            if not has_error and not args.verbose:
                print(f"  [OK]   {cid}")
        print(f"\n{len(results)} concept(s), {total_errors} error(s), {total_warns} warning(s)")
        if total_errors > 0:
            sys.exit(1)
    else:
        print("Error: specify --bundle or --file", file=sys.stderr)
        sys.exit(1)


def cmd_index(args):
    index_text = generate_index(args.bundle)
    if args.output:
        Path(args.output).write_text(index_text, encoding='utf-8')
        print(f"Written: {args.output}")
    else:
        print(index_text, end='')


def cmd_tokens(args):
    if args.file:
        text = Path(args.file).read_text(encoding='utf-8')
        count = estimate_tokens(text)
        print(f"{args.file}: ~{count} tokens ({len(text)} chars)")
    elif args.bundle:
        total = 0
        for c in list_concepts(args.bundle):
            doc = read_existing_doc(c['id'], args.bundle)
            if doc:
                count = estimate_tokens(doc['raw'])
                total += count
                if args.verbose:
                    print(f"  {c['id']:<40s} ~{count:>6} tokens")
        print(f"\nTotal: ~{total} tokens")
    else:
        text = sys.stdin.read()
        count = estimate_tokens(text)
        print(f"~{count} tokens ({len(text)} chars)")


def main():
    parser = argparse.ArgumentParser(
        prog='okf.sh',
        description='OKF (Open Knowledge Format) bundle management tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
            Examples:
              %(prog)s create-bundle --bundle ./my-bundle --version 0.2
              %(prog)s list-concepts --bundle ./bundle
              %(prog)s read-doc --bundle ./bundle --concept documents/report
              %(prog)s write-doc --bundle ./bundle --concept documents/report --type Document --body - < body.md
              %(prog)s ingest --bundle ./bundle --file ./large-doc.md --type Document
              %(prog)s extract-links --file ./bundle/documents/report.md
              %(prog)s validate --bundle ./bundle
              %(prog)s index --bundle ./bundle --output ./bundle/index.md
              %(prog)s tokens --bundle ./bundle --verbose
        """),
    )
    sub = parser.add_subparsers(dest='command', help='Command to run')

    # create-bundle
    p_cb = sub.add_parser('create-bundle', help='Create a new empty bundle directory')
    p_cb.add_argument('--bundle', required=True, help='Bundle directory path')
    p_cb.add_argument('--version', help='OKF version to declare (e.g. 0.2)')
    p_cb.add_argument('--name', help='Bundle display name')

    # list-concepts
    p_list = sub.add_parser('list-concepts', help='List all concepts in a bundle')
    p_list.add_argument('--bundle', required=True, help='Bundle directory path')
    p_list.add_argument('--json', action='store_true', help='Output as JSON')

    # read-doc
    p_read = sub.add_parser('read-doc', help='Read an existing concept document')
    p_read.add_argument('--bundle', required=True, help='Bundle directory path')
    p_read.add_argument('--concept', required=True, help='Concept ID (relative path without .md)')
    p_read.add_argument('--json', action='store_true', help='Output as JSON')
    p_read.add_argument('--frontmatter', action='store_true', help='Output frontmatter only (YAML)')
    p_read.add_argument('--body', action='store_true', help='Output body only')

    # write-doc
    p_write = sub.add_parser('write-doc', help='Write or update a concept document')
    p_write.add_argument('--bundle', required=True, help='Bundle directory path')
    p_write.add_argument('--concept', required=True, help='Concept ID (relative path without .md)')
    p_write.add_argument('--type', help='Concept type (required if not in frontmatter)')
    p_write.add_argument('--frontmatter', help='Frontmatter as YAML string')
    p_write.add_argument('--frontmatter-file', help='Frontmatter from YAML file')
    p_write.add_argument('--json-fm', action='store_true', help='Parse frontmatter as JSON instead of YAML')
    p_write.add_argument('--body', help='Body as string, or "-" to read from stdin')
    p_write.add_argument('--body-stdin', action='store_true', help='Read body from stdin')
    p_write.add_argument('--dry-run', action='store_true', help='Print document without writing')

    # ingest
    p_ingest = sub.add_parser('ingest', help='Ingest markdown, split into multiple concepts')
    p_ingest.add_argument('--bundle', required=True, help='Bundle directory path')
    p_ingest.add_argument('--file', help='Input markdown file (or use --body -)')
    p_ingest.add_argument('--body', help='Body as string, or "-" to read from stdin')
    p_ingest.add_argument('--type', default='Document', help='Concept type (default: Document)')
    p_ingest.add_argument('--output-dir', default='documents', help='Output directory within bundle (default: documents)')
    p_ingest.add_argument('--resource', help='Source resource URI')
    p_ingest.add_argument('--title', help='Source title')
    p_ingest.add_argument('--source-id', help='Source ID for provenance')
    p_ingest.add_argument('--dry-run', action='store_true', help='Print documents without writing')
    p_ingest.add_argument('--json', action='store_true', help='Output as JSON')

    # extract-links
    p_links = sub.add_parser('extract-links', help='Extract cross-links from a document')
    p_links.add_argument('--file', help='File to extract links from (default: stdin)')
    p_links.add_argument('--json', action='store_true', help='Output as JSON')

    # validate
    p_val = sub.add_parser('validate', help='Validate bundle or single concept')
    p_val.add_argument('--bundle', help='Bundle directory path')
    p_val.add_argument('--file', help='Single file to validate')
    p_val.add_argument('--verbose', '-v', action='store_true', help='Show all messages including OK')

    # index
    p_idx = sub.add_parser('index', help='Generate index.md for a bundle directory')
    p_idx.add_argument('--bundle', required=True, help='Bundle directory path')
    p_idx.add_argument('--output', '-o', help='Output file path (default: stdout)')

    # tokens
    p_tok = sub.add_parser('tokens', help='Estimate token count')
    p_tok.add_argument('--file', help='Single file to estimate')
    p_tok.add_argument('--bundle', help='Bundle directory (estimates all concepts)')
    p_tok.add_argument('--verbose', '-v', action='store_true', help='Show per-file breakdown')

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    commands = {
        'create-bundle': cmd_create_bundle,
        'list-concepts': cmd_list_concepts,
        'read-doc': cmd_read_doc,
        'write-doc': cmd_write_doc,
        'ingest': cmd_ingest,
        'extract-links': cmd_extract_links,
        'validate': cmd_validate,
        'index': cmd_index,
        'tokens': cmd_tokens,
    }
    commands[args.command](args)


if __name__ == '__main__':
    main()
