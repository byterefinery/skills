# Embeddings

Chonkie supports 16+ embedding providers through a unified `BaseEmbeddings` interface. `AutoEmbeddings` auto-detects and loads the right provider.

---

## BaseEmbeddings Interface

```python
embeddings.embed(text: str) -> np.ndarray           # single
embeddings.embed_batch(texts: list[str]) -> list[np.ndarray]  # batch
embeddings.similarity(a: np.ndarray, b: np.ndarray) -> float  # cosine
embeddings.get_tokenizer() -> TokenizerProtocol      # associated tokenizer
embeddings.dimension                                 # embedding dimension
```

## AutoEmbeddings

Factory that auto-detects provider from model string:

```python
from chonkie import AutoEmbeddings

# By model name (auto-matched via registry)
emb = AutoEmbeddings.get_embeddings("sentence-transformers/all-MiniLM-L6-v2")

# With provider:// prefix (explicit routing)
emb = AutoEmbeddings.get_embeddings("openai://text-embedding-3-small", api_key="sk-...")
emb = AutoEmbeddings.get_embeddings("cohere://embed-english-light-v3.0", api_key="...")
emb = AutoEmbeddings.get_embeddings("gemini://text-embedding-004")

# Pass existing BaseEmbeddings instance (passthrough)
emb = AutoEmbeddings.get_embeddings(existing_embeddings_instance)
```

**Resolution order for plain strings (no `://`):**
1. Registry match (checks provider keywords in model name)
2. Fallback to `SentenceTransformerEmbeddings(model_name)`

## Providers

| Provider / Alias | Class | Install | Example |
|-----------------|-------|---------|---------|
| `model2vec` | `Model2VecEmbeddings` | `chonkie[model2vec]` | `"minishlab/potion-base-32M"` |
| `sentence-transformers` | `SentenceTransformerEmbeddings` | `chonkie[st]` | `"all-MiniLM-L6-v2"` |
| `openai` | `OpenAIEmbeddings` | `chonkie[openai]` | `"openai://text-embedding-3-small"` |
| `azure-openai` | `AzureOpenAIEmbeddings` | `chonkie[azure-openai]` | Azure endpoint |
| `cohere` | `CohereEmbeddings` | `chonkie[cohere]` | `"cohere://embed-english-v3.0"` |
| `gemini` | `GeminiEmbeddings` | `chonkie[gemini]` | `"gemini://text-embedding-004"` |
| `jina` | `JinaEmbeddings` | `chonkie[jina]` | Jina API |
| `voyageai` | `VoyageAIEmbeddings` | `chonkie[voyageai]` | Voyage AI API |
| `litellm` | `LiteLLMEmbeddings` | `chonkie[litellm]` | 100+ models via LiteLLM |
| `catsu` | `CatsuEmbeddings` | `chonkie[catsu]` | Unified adapter, 11+ providers |
| `mistral` | `MistralEmbeddings` | `chonkie[catsu]` | Mistral API |
| `together` | `TogetherEmbeddings` | `chonkie[catsu]` | Together AI |
| `mixedbread` | `MixedbreadEmbeddings` | `chonkie[catsu]` | Mixedbread API |
| `nomic` | `NomicEmbeddings` | `chonkie[catsu]` | Nomic API |
| `deepinfra` | `DeepInfraEmbeddings` | `chonkie[catsu]` | DeepInfra API |
| `cloudflare` | `CloudflareEmbeddings` | `chonkie[catsu]` | Cloudflare Workers AI |

## Usage Patterns

```python
from chonkie import SentenceTransformerEmbeddings

# Direct instantiation
emb = SentenceTransformerEmbeddings(model="all-MiniLM-L6-v2")
vector = emb.embed("Hello world")           # numpy array
vectors = emb.embed_batch(["A", "B", "C"])  # list of numpy arrays
sim = emb.similarity(vectors[0], vectors[1]) # cosine similarity
dim = emb.dimension                          # e.g., 384

# In SemanticChunker
from chonkie import SemanticChunker
chunker = SemanticChunker(embedding_model="minishlab/potion-base-32M")

# In EmbeddingsRefinery
from chonkie import EmbeddingsRefinery
refinery = EmbeddingsRefinery(embedding_model="minishlab/potion-retrieval-32M")

# In LateChunker (requires sentence-transformers)
from chonkie import LateChunker
chunker = LateChunker(embedding_model="nomic-ai/modernbert-embed-base")
```

## Catsu Unified Adapter

`CatsuEmbeddings` provides a single interface for 11+ providers:

```python
from chonkie import CatsuEmbeddings

# Mistral
emb = CatsuEmbeddings(provider="mistral", model="mistral-embed", api_key="...")

# Together
emb = CatsuEmbeddings(provider="together", model="together-embed-multilingual", api_key="...")
```

## EmbeddingsRegistry

Internal registry that maps model names to provider classes. Supports `match()`, `get_provider()`, and `wrap()` methods.

---

## Late Embeddings (LateChunker)

`LateChunker` uses `SentenceTransformerEmbeddings.embed_as_tokens()` to get per-token embeddings, then average-pools them per chunk. This produces higher-quality chunk embeddings than simple text embedding.

```python
from chonkie import LateChunker

chunker = LateChunker(embedding_model="nomic-ai/modernbert-embed-base")
chunks = chunker("Document text...")
# chunks[0].embedding is a numpy array from late interaction
```
