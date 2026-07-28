# Genies

Genies provide interfaces to LLMs for advanced chunking (used by `SlumberChunker`) and other tasks. All genies implement the `BaseGenie` interface.

---

## BaseGenie Interface

```python
from chonkie import BaseGenie

# All genies support:
genie.generate(prompt: str) -> str           # text generation
genie.generate_json(prompt: str) -> dict     # JSON-structured output
```

---

## OpenAIGenie

```python
from chonkie import OpenAIGenie

genie = OpenAIGenie(
    model="gpt-4o",
    api_key="sk-...",
    base_url=None,         # override for compatible APIs
)

# Use with SlumberChunker
from chonkie import SlumberChunker
chunker = SlumberChunker(genie=genie, chunk_size=2048)
chunks = chunker("Long document text...")
```

**Compatible APIs:** Any OpenAI-compatible endpoint works by setting `base_url`:

```python
# OpenRouter
genie = OpenAIGenie(
    model="meta-llama/llama-4-maverick",
    base_url="https://openrouter.ai/api/v1",
    api_key="your_openrouter_key",
)

# Local Ollama
genie = OpenAIGenie(
    model="llama3",
    base_url="http://localhost:11434/v1",
    api_key="not-needed",
)
```

---

## AzureOpenAIGenie

```python
from chonkie import AzureOpenAIGenie

genie = AzureOpenAIGenie(
    model="gpt-4",
    api_key="your_key",
    azure_endpoint="https://your-resource.openai.azure.com/",
    api_version="2024-02-01",
)
```

---

## GeminiGenie

```python
from chonkie import GeminiGenie

genie = GeminiGenie(
    model="gemini-2.0-flash",
    api_key="your_key",     # or set GEMINI_API_KEY env var
)
```

Default genie for `SlumberChunker` when no genie is provided.

---

## GroqGenie

```python
from chonkie import GroqGenie

genie = GroqGenie(
    model="llama-3.3-70b-versatile",
    api_key="your_key",
)
```

Fast inference on Groq hardware.

---

## CerebrasGenie

```python
from chonkie import CerebrasGenie

genie = CerebrasGenie(
    model="llama3.3-70b",
    api_key="your_key",
)
```

Fastest inference on Cerebras wafer-scale hardware.

---

## Usage with SlumberChunker

```python
from chonkie import SlumberChunker, OpenAIGenie, GeminiGenie

# With OpenAI
genie = OpenAIGenie(model="gpt-4o-mini", api_key="sk-...")
chunker = SlumberChunker(genie=genie, chunk_size=1024)
chunks = chunker("Your document text...")

# With Gemini (default)
# Set GEMINI_API_KEY env var
chunker = SlumberChunker(chunk_size=1024)  # auto-uses GeminiGenie
```
