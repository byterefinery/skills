# Utility Functions

PocketFlow provides **no built-in utilities** — vendor-specific APIs belong in your code, not the framework. Below are example implementations to serve as starting points.

## LLM Wrappers

### OpenAI

```python
from openai import OpenAI

def call_llm(prompt):
    client = OpenAI(api_key="YOUR_API_KEY")
    r = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return r.choices[0].message.content
```

### Claude (Anthropic)

```python
from anthropic import Anthropic

def call_llm(prompt):
    client = Anthropic(api_key="YOUR_API_KEY")
    r = client.messages.create(
        model="claude-sonnet-4-0",
        messages=[{"role": "user", "content": prompt}]
    )
    return r.content[0].text
```

### Google Gemini

```python
from google import genai

def call_llm(prompt):
    client = genai.Client(api_key="GEMINI_API_KEY")
    response = client.models.generate_content(model="gemini-2.5-pro", contents=prompt)
    return response.text
```

### Azure OpenAI

```python
from openai import AzureOpenAI

def call_llm(prompt):
    client = AzureOpenAI(
        azure_endpoint="https://<RESOURCE>.openai.azure.com/",
        api_key="YOUR_API_KEY",
        api_version="2023-05-15"
    )
    r = client.chat.completions.create(model="<DEPLOYMENT>", messages=[{"role": "user", "content": prompt}])
    return r.choices[0].message.content
```

### Ollama (Local)

```python
from ollama import chat

def call_llm(prompt):
    response = chat(model="llama2", messages=[{"role": "user", "content": prompt}])
    return response.message.content
```

### DeepSeek

```python
from openai import OpenAI

def call_llm(prompt):
    client = OpenAI(api_key="YOUR_KEY", base_url="https://api.deepseek.com")
    r = client.chat.completions.create(model="deepseek-chat", messages=[{"role": "user", "content": prompt}])
    return r.choices[0].message.content
```

### Async LLM Wrapper

```python
async def call_llm_async(prompt):
    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key="YOUR_API_KEY")
    r = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return r.choices[0].message.content
```

### Improvements

- **Chat history**: Pass `messages` list instead of single prompt
- **Caching**: Use `@lru_cache` — but note it conflicts with Node retries (cached results don't change on retry)
- **Logging**: Log prompt and response for debugging

## Web Search

### Google Custom Search JSON API

```python
import requests

url = "https://www.googleapis.com/customsearch/v1"
params = {"key": API_KEY, "cx": CX_ID, "q": query}
results = requests.get(url, params=params).json()
```

### Brave Search API

```python
import requests

url = "https://api.search.brave.com/res/v1/web/search"
headers = {"X-Subscription-Token": SUBSCRIPTION_TOKEN}
params = {"q": query}
results = requests.get(url, headers=headers, params=params).json()
```

### SerpApi

```python
import requests

url = "https://serpapi.com/search"
params = {"engine": "google", "q": query, "api_key": API_KEY}
results = requests.get(url, params=params).json()
```

### DuckDuckGo (Free, Instant Answers only)

```python
import requests

url = "https://api.duckduckgo.com/"
params = {"q": query, "format": "json"}
results = requests.get(url, params=params).json()
```

## Visualization and Debugging

### Mermaid Generation

Recursively traverse the graph and generate Mermaid syntax:

```python
def build_mermaid(start):
    ids, visited, lines = {}, set(), ["graph LR"]
    ctr = 1
    def get_id(n):
        nonlocal ctr
        return ids[n] if n in ids else (ids.setdefault(n, f"N{ctr}"), (ctr := ctr + 1))[0]
    def link(a, b):
        lines.append(f"    {a} --> {b}")
    def walk(node, parent=None):
        if node in visited:
            return parent and link(parent, get_id(node))
        visited.add(node)
        if isinstance(node, Flow):
            node.start_node and parent and link(parent, get_id(node.start_node))
            lines.append(f"\n    subgraph sub_flow_{get_id(node)}[{type(node).__name__}]")
            node.start_node and walk(node.start_node)
            for nxt in node.successors.values():
                node.start_node and walk(nxt, get_id(node.start_node)) or walk(nxt)
            lines.append("    end\n")
        else:
            nid = get_id(node)
            lines.append(f"    {nid}['{type(node).__name__}']")
            parent and link(parent, nid)
            [walk(nxt, nid) for nxt in node.successors.values()]
    walk(start)
    return "\n".join(lines)
```

### Call Stack Debugging

```python
import inspect

def get_node_call_stack():
    stack = inspect.stack()
    node_names = []
    seen_ids = set()
    for frame_info in stack[1:]:
        local_vars = frame_info.frame.f_locals
        if 'self' in local_vars:
            caller_self = local_vars['self']
            if isinstance(caller_self, BaseNode) and id(caller_self) not in seen_ids:
                seen_ids.add(id(caller_self))
                node_names.append(type(caller_self).__name__)
    return node_names
```

## Text Chunking

### Naive (Fixed-Size)

```python
def fixed_size_chunk(text, chunk_size=100):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
```

### Sentence-Based

```python
import nltk

def sentence_based_chunk(text, max_sentences=2):
    sentences = nltk.sent_tokenize(text)
    return [" ".join(sentences[i:i+max_sentences]) for i in range(0, len(sentences), max_sentences)]
```

### Other Approaches

- **Paragraph-based**: Split by newlines
- **Semantic**: Use embeddings or topic modeling
- **Agentic**: Use an LLM to decide chunk boundaries

> Start with naive chunking and optimize later.

## Embedding

### OpenAI

```python
from openai import OpenAI
import numpy as np

client = OpenAI(api_key="YOUR_API_KEY")
response = client.embeddings.create(model="text-embedding-ada-002", input=text)
embedding = np.array(response.data[0].embedding, dtype=np.float32)
```

### Other Providers

| Provider | Key Library | Notes |
|---|---|---|
| Azure OpenAI | `openai` (azure mode) | Same API as OpenAI |
| Google Vertex AI | `vertexai` | `textembedding-gecko` model |
| AWS Bedrock | `boto3` | `amazon.titan-embed-text-v2` |
| Cohere | `cohere` | `co.embed(texts=[...])` |
| Hugging Face | `requests` | Inference API |
| Jina | `requests` | `jina-embeddings-v3` |

> Embedding is a micro-optimization compared to Flow Design. Start with the most convenient provider.

## Vector Databases

### FAISS (Local, Open-Source)

```python
import faiss
import numpy as np

index = faiss.IndexFlatL2(d=128)
data = np.random.random((1000, 128)).astype('float32')
index.add(data)

query = np.random.random((1, 128)).astype('float32')
D, I = index.search(query, k=5)
```

### Chroma (Local, Free)

```python
import chromadb

client = chromadb.Client()
coll = client.create_collection("my_collection")
coll.add(embeddings=[[0.1, 0.2, 0.3]], metadatas=[{"doc": "text1"}], ids=["id1"])
res = coll.query(query_embeddings=[[0.15, 0.25, 0.3]], n_results=2)
```

### Pinecone (Cloud)

```python
import pinecone

pinecone.init(api_key="YOUR_KEY", environment="YOUR_ENV")
index = pinecone.Index("my-index")
index.upsert([("id1", [0.1]*128), ("id2", [0.2]*128)])
response = index.query([[0.15]*128], top_k=3)
```

### Other Options

| Tool | Free Tier | Pricing |
|---|---|---|
| Qdrant | 1GB cloud | PAYG |
| Weaviate | 14-day sandbox | From $25/mo |
| Milvus | 5GB cloud | PAYG or $99/mo |
| Redis | 30MB | From $5/mo |

## Text-to-Speech

### Amazon Polly

```python
import boto3

polly = boto3.client("polly", region_name="us-east-1")
resp = polly.synthesize_speech(Text="Hello!", OutputFormat="mp3", VoiceId="Joanna")
with open("output.mp3", "wb") as f:
    f.write(resp["AudioStream"].read())
```

### Google Cloud TTS

```python
from google.cloud import texttospeech

client = texttospeech.TextToSpeechClient()
input_text = texttospeech.SynthesisInput(text="Hello!")
voice = texttospeech.VoiceSelectionParams(language_code="en-US")
audio_cfg = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
resp = client.synthesize_speech(input=input_text, voice=voice, audio_config=audio_cfg)
with open("output.mp3", "wb") as f:
    f.write(resp.audio_content)
```

### ElevenLabs

```python
import requests

api_key = "ELEVENLABS_KEY"
voice_id = "VOICE_ID"
url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
headers = {"xi-api-key": api_key, "Content-Type": "application/json"}
json_data = {"text": "Hello!", "voice_settings": {"stability": 0.75, "similarity_boost": 0.75}}
resp = requests.post(url, headers=headers, json=json_data)
with open("output.mp3", "wb") as f:
    f.write(resp.content)
```

### Other Options

| Service | Free Tier | Pricing |
|---|---|---|
| Azure TTS | 500K neural ongoing | ~$15/M |
| IBM Watson | 10K chars | ~$20/M |
