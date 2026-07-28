# Chunkers

All chunkers inherit from `BaseChunker` and implement:
- `chunk(text: str) -> list[Chunk]` — chunk a single text
- `chunk_batch(texts: Sequence[str], show_progress=True) -> list[list[Chunk]]` — batch chunking
- `achunk(text: str) -> list[Chunk]` — async single
- `achunk_batch(texts: Sequence[str]) -> list[list[Chunk]]` — async batch
- `chunk_document(document: Document) -> Document` — chunk a Document, propagating metadata
- `__call__(text, show_progress=True)` — callable shorthand

All chunkers are registered in the `ComponentRegistry` via `@chunker("alias")` decorator, so they can be used in pipelines by alias string.

---

## TokenChunker (`"token"`)

Splits text into fixed-size token chunks with optional overlap.

```python
from chonkie import TokenChunker

chunker = TokenChunker(
    tokenizer="character",      # default: "character"
    chunk_size=2048,            # max tokens per chunk
    chunk_overlap=0,            # int (absolute) or float (fraction of chunk_size)
)
chunks = chunker("Text to chunk...")
```

**Parameters:**
- `tokenizer` — string identifier or TokenizerProtocol (default: `"character"`)
- `chunk_size` — max tokens per chunk (default: 2048)
- `chunk_overlap` — overlap tokens. Int = absolute count; float = fraction of `chunk_size` (default: 0)

**Batch API:** `chunk_batch(texts, batch_size=1, show_progress_bar=True)` — processes in configurable batches.

---

## SentenceChunker (`"sentence"`)

Splits text at sentence boundaries, respecting token limits per chunk.

```python
from chonkie import SentenceChunker

chunker = SentenceChunker(
    tokenizer="character",
    chunk_size=2048,
    chunk_overlap=0,
    min_sentences_per_chunk=1,
    min_characters_per_sentence=12,
    delim=[". ", "! ", "? ", "\n"],   # sentence delimiters
    include_delim="prev",             # "prev" or "next"
)
```

**Parameters:**
- `delim` — sentence boundary delimiters (default: `[". ", "! ", "? ", "\n"]`)
- `include_delim` — attach delimiter to `"prev"` (current) or `"next"` chunk (default: `"prev"`)
- `min_sentences_per_chunk` — minimum sentences per chunk (default: 1)
- `min_characters_per_sentence` — minimum chars to count as a sentence (default: 12)

**Recipe:** `SentenceChunker.from_recipe(name="default", lang="en")` — loads language-specific delimiters from the Chonkie Hub.

---

## RecursiveChunker (`"recursive"`)

Recursively splits text using hierarchical rules (paragraphs → sentences → punctuation → whitespace → tokens).

```python
from chonkie import RecursiveChunker, RecursiveRules, RecursiveLevel

# Default rules (5 levels)
chunker = RecursiveChunker(
    tokenizer="character",
    chunk_size=2048,
    min_characters_per_chunk=24,
)

# Custom rules
rules = RecursiveRules(levels=[
    RecursiveLevel(delimiters=["\n\n", "\n"]),
    RecursiveLevel(delimiters=[". ", "! ", "? "]),
    RecursiveLevel(whitespace=True),
])
chunker = RecursiveChunker(rules=rules, chunk_size=512)
```

**Parameters:**
- `rules` — `RecursiveRules` instance (default: 5-level hierarchy)
- `chunk_size` — max tokens per chunk (default: 2048)
- `min_characters_per_chunk` — minimum chars before a chunk is emitted (default: 24)

**Recipe:** `RecursiveChunker.from_recipe(name="default", lang="en")` — loads language-specific rules.

**Default rule levels:**
1. Paragraphs: `delimiters=["\n\n", "\r\n", "\n", "\r"]`
2. Sentences: `delimiters=[". ", "! ", "? "]`
3. Punctuation: `delimiters=["{", "}", '"', "[", "]", "<", ">", "(", ")", ":", ";", ",", "—", "|", "~", "-", "...", "`", "'"]`
4. Words: `whitespace=True`
5. Tokens: no delimiters (falls through to tokenizer encode/split/decode)

---

## SemanticChunker (`"semantic"`)

Uses embedding-based peak detection to find semantic topic boundaries. Requires `chonkie[semantic]`.

```python
from chonkie import SemanticChunker

chunker = SemanticChunker(
    embedding_model="minishlab/potion-base-32M",  # default
    threshold=0.8,              # similarity threshold (0-1)
    chunk_size=2048,
    similarity_window=3,        # sentences to consider for similarity
    min_sentences_per_chunk=1,
    delim=[". ", "! ", "? ", "\n"],
    skip_window=0,              # merge non-consecutive similar groups (0=disabled)
    filter_window=5,            # Savitzky-Golay filter window
    filter_polyorder=3,         # polynomial order
    filter_tolerance=0.2,       # tolerance for peak detection
)
```

**Parameters:**
- `embedding_model` — string model name or `BaseEmbeddings` instance (default: `"minishlab/potion-base-32M"`)
- `threshold` — semantic similarity threshold; lower = more chunks (default: 0.8)
- `similarity_window` — number of sentences in the comparison window (default: 3)
- `skip_window` — merge similar groups separated by N chunks (default: 0, disabled)
- `filter_window` / `filter_polyorder` / `filter_tolerance` — Savitzky-Golay filter params for smoother boundary detection

**Algorithm:** Splits text into sentences → computes window embeddings → compares window to next sentence embedding → finds local minima (topic shifts) via Savitzky-Golay filter → splits at minima below threshold.

**Recipe:** `SemanticChunker.from_recipe(name="default", lang="en")`.

---

## LateChunker (`"late"`)

Recursive chunking with late interaction embeddings. Returns chunks with `.embedding` already populated. Requires `chonkie[st]`.

```python
from chonkie import LateChunker

chunker = LateChunker(
    embedding_model="nomic-ai/modernbert-embed-base",  # default
    chunk_size=2048,
    min_characters_per_chunk=24,
)
chunks = chunker("Document text...")
# chunks[0].embedding is a numpy array
```

**Parameters:**
- `embedding_model` — string model name or `SentenceTransformerEmbeddings` (default: `"nomic-ai/modernbert-embed-base"`)
- `chunk_size` — max tokens per chunk (default: 2048)
- `rules` — `RecursiveRules` (default: standard 5-level)
- `min_characters_per_chunk` — minimum chars (default: 24)

**Algorithm:** Recursive split → embed full text at token level via sentence-transformers → average-pool token embeddings per chunk → attach as `.embedding`.

**Recipe:** `LateChunker.from_recipe(name="default", lang="en")`.

---

## CodeChunker (`"code"`)

Splits code into structurally meaningful chunks using tree-sitter AST parsing. Requires `chonkie[code]`.

```python
from chonkie import CodeChunker

chunker = CodeChunker(
    chunk_size=2048,
    language="python",          # or "auto"
    include_nodes=False,
)
chunks = chunker("def hello():\n    print('world')")
```

**Parameters:**
- `language` — specific language (e.g., `"python"`, `"javascript"`, `"rust"`) or `"auto"` (default: `"auto"`)
- `chunk_size` — target chunk size in tokens (default: 2048)
- `include_nodes` — whether to include AST node metadata (default: False)

**Auto-detection:** When `language="auto"`, tries shebang detection first, then trial-parsing with all downloaded grammars (picks fewest errors + most structure).

**MarkdownDocument support:** When chunking a `MarkdownDocument`, processes code blocks individually using language hints from fenced code blocks.

---

## NeuralChunker (`"neural"`)

Uses a token-classification model to predict split points. Requires `chonkie[neural]`.

```python
from chonkie import NeuralChunker

chunker = NeuralChunker(
    model="mirth/chonky_distilbert_base_uncased_1",  # default
    device_map="auto",
    min_characters_per_chunk=10,
)
chunks = chunker("Text to chunk...")
```

**Parameters:**
- `model` — model name or pre-loaded model (default: `"mirth/chonky_distilbert_base_uncased_1"`)
- `device_map` — `"auto"`, `"cpu"`, `"cuda"` (default: `"auto"`)
- `min_characters_per_chunk` — minimum chars per chunk (default: 10)
- `stride` — model stride override (auto from model config)

**Supported models:**
- `mirth/chonky_distilbert_base_uncased_1` (stride: 256)
- `mirth/chonky_modernbert_base_1` (stride: 512)
- `mirth/chonky_modernbert_large_1` (stride: 512)

---

## SlumberChunker (`"slumber"`)

Uses an LLM to find semantically meaningful split points. Also known as AgenticChunker.

```python
from chonkie import SlumberChunker, OpenAIGenie

genie = OpenAIGenie(model="gpt-4o", api_key="sk-...")
chunker = SlumberChunker(
    genie=genie,
    chunk_size=2048,
    candidate_size=128,         # candidate sub-chunk size for LLM evaluation
    min_characters_per_chunk=24,
    extract_mode="auto",        # "text", "json", or "auto"
    max_retries=3,
)
chunks = chunker("Long document text...")
```

**Parameters:**
- `genie` — `BaseGenie` instance (default: `GeminiGenie()` using `GEMINI_API_KEY`)
- `chunk_size` — max tokens per chunk (default: 2048)
- `candidate_size` — size of candidate sub-chunks for LLM evaluation (default: 128)
- `extract_mode` — `"text"`, `"json"`, or `"auto"` (default: `"auto"`)
- `max_retries` — retry count on LLM parse failures (default: 3)

**Algorithm:** Splits text into candidate sub-chunks → sends batches to LLM with prompt asking for first topic-shift index → merges candidates up to split point → recurses on remainder.

---

## TableChunker (`"table"`)

Chunks markdown tables by rows or character count.

```python
from chonkie import TableChunker

# Row-based (default)
chunker = TableChunker(tokenizer="row", chunk_size=3)

# Character-based
chunker = TableChunker(tokenizer="character", chunk_size=512)
```

**Parameters:**
- `tokenizer` — `"row"` for row-based chunking, or any other tokenizer (default: `"row"`)
- `chunk_size` — max rows (with `"row"`) or tokens (with other tokenizers) per chunk (default: 3)

**Supports:** Markdown tables and HTML tables. For HTML tables, extracts `<tr>` rows via string search (no regex, avoids ReDoS).

---

## FastChunker (`"fast"`)

SIMD-accelerated byte-based chunking at 100+ GB/s. No tokenizer dependency.

```python
from chonkie import FastChunker

chunker = FastChunker(
    chunk_size=4096,            # bytes, not tokens
    delimiters="\n.?",          # single-byte delimiter chars
    prefix=False,               # put delimiter at start of next chunk
    consecutive=False,          # split at start of consecutive runs
    forward_fallback=False,     # search forward if no delimiter in window
)
chunks = chunker("Text to chunk...")
# Note: chunk.token_count is always 0
```

**Parameters:**
- `chunk_size` — target chunk size in **bytes** (default: 4096)
- `delimiters` — single-byte delimiter characters (default: `"\n.?"`)
- `pattern` — multi-byte pattern to split on (overrides `delimiters`)
- `prefix` — put delimiter at start of next chunk instead of end of current (default: False)
- `consecutive` — split at start of consecutive delimiter runs (default: False)
- `forward_fallback` — search forward for delimiter if none found in backward window (default: False)

**Note:** Does not call `BaseChunker.__init__()`. Has no tokenizer. `chunk.token_count` is always 0.

---

## TeraflopAIChunker (`"teraflopai"`)

Uses the TeraflopAI Segmentation API for domain-specific text segmentation.

```python
from chonkie import TeraflopAIChunker

chunker = TeraflopAIChunker(
    api_key="your_api_key",     # or set TERAFLOPAI_API_KEY env var
    chunk_size=2048,
    chunk_overlap=0,
)
chunks = chunker("Text to chunk...")
```

**Parameters:**
- `api_key` — TeraflopAI API key (or `TERAFLOPAI_API_KEY` env var)
- `chunk_size` — max tokens per chunk (default: 2048)
- `chunk_overlap` — overlap tokens (default: 0)
