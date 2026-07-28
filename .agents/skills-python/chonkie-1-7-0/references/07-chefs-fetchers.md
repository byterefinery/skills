# Chefs & Fetchers

Chefs preprocess text into `Document` objects. Fetchers load data from sources. Both are pipeline components.

---

## TextChef (`"text"`)

Basic text processing — reads files or parses raw text into `Document`.

```python
from chonkie import TextChef

chef = TextChef()

# From file
doc = chef.process("/path/to/file.txt")      # Document

# From raw text
doc = chef.parse("Raw text content...")      # Document

# Batch
docs = chef.process_batch(["file1.txt", "file2.txt"])  # list[Document]

# Callable
doc = chef("/path/to/file.txt")
docs = chef(["file1.txt", "file2.txt"])
```

---

## MarkdownChef (`"markdown"`)

Parses markdown into `MarkdownDocument` with structured code blocks, tables, and images.

```python
from chonkie import MarkdownChef

chef = MarkdownChef(tokenizer="character")

# From file
doc = chef.process("/path/to/file.md")       # MarkdownDocument

# From raw text
doc = chef.parse("# Header\n\nSome text...") # MarkdownDocument

# Access structured elements
for code_block in doc.code:
    print(f"Language: {code_block.language}, Content: {code_block.content[:50]}...")

for table in doc.tables:
    print(f"Table at {table.start_index}-{table.end_index}")

for image in doc.images:
    print(f"Image: {image.alt_text} -> {image.src}")
```

`MarkdownDocument` extends `Document` with:
- `code: list[MarkdownCode]` — fenced code blocks with language, content, indices
- `tables: list[MarkdownTable]` — pipe-style tables with content and indices
- `images: list[MarkdownImage]` — `![alt](src)` references with alt text, src, indices

---

## TableChef (`"table"`)

Processes CSV/Excel files into `MarkdownDocument`. Requires `chonkie[table]`.

```python
from chonkie import TableChef

chef = TableChef()
doc = chef.process("/path/to/file.csv")      # MarkdownDocument
doc = chef.process("/path/to/file.xlsx")     # MarkdownDocument
```

Uses `pandas`, `tabulate`, `openpyxl`, `lxml` for parsing.

---

## MistralOCR (`"mistral"`)

Extracts text from images/PDFs via Mistral OCR API. Vision component. Requires `chonkie[mistral]`.

```python
from chonkie import MistralOCR

ocr = MistralOCR(model="mistral-ocr-latest", api_key="your_key")
text = ocr.process("/path/to/image.png")     # str
texts = ocr.process_batch(["img1.png", "img2.png"])  # list[str]
```

Used in pipelines via `.see_with("mistral", model="mistral-ocr-latest")`.

---

## LiteParse (`"liteparse"`)

Extracts text from documents via LiteParse API. Requires `chonkie[liteparse]`.

```python
from chonkie import LiteParse

parser = LiteParse(api_key="your_key")
text = parser.process("/path/to/document.pdf")  # str
```

---

## FileFetcher (`"file"`)

Loads text from files and directories.

```python
from chonkie import FileFetcher

fetcher = FileFetcher()

# Single file
result = fetcher.fetch(path="document.txt")

# Directory with extension filter
result = fetcher.fetch(dir="./docs", ext=[".txt", ".md"])
```

**Parameters:**
- `path` — single file path
- `dir` — directory path (returns multiple files)
- `ext` — list of extensions to filter (e.g., `[".txt", ".md"]`)

---

## Pipeline Usage

```python
from chonkie import Pipeline

# Text file
doc = (
    Pipeline()
    .fetch_from("file", path="document.txt")
    .process_with("text")
    .chunk_with("recursive", chunk_size=512)
    .run()
)

# Markdown with code-aware chunking
doc = (
    Pipeline()
    .fetch_from("file", path="readme.md")
    .process_with("markdown")
    .chunk_with("code", chunk_size=1024)
    .run()
)

# Directory
docs = (
    Pipeline()
    .fetch_from("file", dir="./docs", ext=[".txt", ".md"])
    .process_with("text")
    .chunk_with("recursive", chunk_size=512)
    .run()
)

# OCR + chunking
doc = (
    Pipeline()
    .fetch_from("file", path="scanned.pdf")
    .see_with("mistral", model="mistral-ocr-latest")
    .chunk_with("recursive", chunk_size=512)
    .run()
)
```

## BaseChef

Abstract base class with `read(path)` for file reading and `_set_source_filename(doc, path)` for metadata.

## BaseFetcher

Abstract base class with `fetch(**kwargs)` and `afetch(**kwargs)` async variant.
