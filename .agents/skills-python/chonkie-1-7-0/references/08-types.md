# Types

Core data types used throughout Chonkie.

---

## Chunk

```python
from chonkie import Chunk

chunk = Chunk(
    text="The text content of this chunk",
    start_index=0,            # character offset in original text
    end_index=50,             # character offset (exclusive)
    token_count=10,           # number of tokens
    context=None,             # optional context string (from OverlapRefinery)
    embedding=None,           # optional numpy array (from EmbeddingsRefinery/LateChunker)
    metadata={},              # arbitrary dict; merged from Document.metadata
)
```

**Attributes:**
- `id` — auto-generated UUID with `"chnk_"` prefix
- `text` — the chunk text content
- `start_index` / `end_index` — character offsets in the original document
- `token_count` — number of tokens (from the chunker's tokenizer)
- `context` — optional context string (set by `OverlapRefinery`)
- `embedding` — optional numpy array (set by `EmbeddingsRefinery` or `LateChunker`)
- `metadata` — arbitrary dict; `BaseChunker.chunk_document()` merges `Document.metadata` into each chunk (chunk keys override on conflict)

**Methods:**
- `__len__()` — returns `len(chunk.text)`
- `__str__()` — returns `chunk.text`
- `__iter__()` — iterates over characters of `chunk.text`
- `__getitem__(index)` — `chunk.text[index]`
- `to_dict()` — serialize to dict (converts numpy embedding to list)
- `from_dict(data)` — deserialize from dict
- `copy()` — deep copy

---

## Document

```python
from chonkie import Document

doc = Document(
    content="Full document text...",
    chunks=[],                # populated by chunkers
    metadata={"source": "file.txt"},
)
```

**Attributes:**
- `id` — auto-generated UUID with `"doc_"` prefix
- `content` — full text content
- `chunks` — list of `Chunk` objects (populated by `chunk_document()`)
- `metadata` — arbitrary dict; propagated to chunks during chunking

---

## RecursiveLevel

Defines splitting rules at one level of the recursive chunker hierarchy.

```python
from chonkie import RecursiveLevel

# By delimiters
level = RecursiveLevel(
    delimiters=["\n\n", "\n"],
    include_delim="prev",     # "prev" (attach to current) or "next" (attach to next)
)

# By whitespace
level = RecursiveLevel(whitespace=True)

# By regex pattern
level = RecursiveLevel(
    pattern=r"\b[A-Z][a-z]+\b",
    pattern_mode="split",     # "split" (split on match) or "extract" (extract matches)
)

# Token-level fallback (no delimiters, no whitespace)
level = RecursiveLevel()
```

**Attributes:**
- `delimiters` — string or list of strings; mutually exclusive with `whitespace` and `pattern`
- `whitespace` — split on spaces; mutually exclusive with `delimiters` and `pattern`
- `include_delim` — `"prev"` or `"next"`; controls delimiter attachment
- `pattern` — regex pattern; mutually exclusive with `delimiters` and `whitespace`
- `pattern_mode` — `"split"` or `"extract"`

**Recipe:** `RecursiveLevel.from_recipe(name="default", lang="en")` — loads from Chonkie Hub.

---

## RecursiveRules

Container for hierarchical splitting levels.

```python
from chonkie import RecursiveRules, RecursiveLevel

# Default (5 levels: paragraphs → sentences → punctuation → words → tokens)
rules = RecursiveRules()

# Custom
rules = RecursiveRules(levels=[
    RecursiveLevel(delimiters=["\n\n", "\n"]),
    RecursiveLevel(delimiters=[". ", "! ", "? "]),
    RecursiveLevel(whitespace=True),
])

# From dict
rules = RecursiveRules.from_dict({
    "levels": [
        {"delimiters": ["\n\n"]},
        {"whitespace": True},
    ]
})

# To dict
rules.to_dict()

# From recipe
rules = RecursiveRules.from_recipe(name="default", lang="en")
```

**Default levels:**
1. Paragraphs: `delimiters=["\n\n", "\r\n", "\n", "\r"]`
2. Sentences: `delimiters=[". ", "! ", "? "]`
3. Punctuation: `delimiters=["{", "}", '"', "[", "]", "<", ">", "(", ")", ":", ";", ",", "—", "|", "~", "-", "...", "`", "'"]`
4. Words: `whitespace=True`
5. Tokens: `RecursiveLevel()` (no delimiters — falls through to tokenizer)

---

## Sentence

```python
from chonkie import Sentence

sentence = Sentence(
    text="This is a sentence.",
    start_index=0,
    end_index=19,
    token_count=5,
)
```

Used internally by `SentenceChunker` and `SemanticChunker`.

---

## MarkdownDocument

Extends `Document` with structured markdown elements.

```python
from chonkie import MarkdownDocument, MarkdownCode, MarkdownTable, MarkdownImage

# Created by MarkdownChef
doc = MarkdownChef().process("file.md")

# Access structured elements
for code in doc.code:       # list[MarkdownCode]
    print(code.language, code.content, code.start_index, code.end_index)

for table in doc.tables:    # list[MarkdownTable]
    print(table.content, table.start_index, table.end_index)

for image in doc.images:    # list[MarkdownImage]
    print(image.alt_text, image.src, image.start_index, image.end_index)
```

---

## LanguageConfig

Configuration for language-specific chunking behavior (used internally by recipes).

---

## MergeRule / SplitRule

Used by `CodeChunker` for tree-sitter AST processing.
