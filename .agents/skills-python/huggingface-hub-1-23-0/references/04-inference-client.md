# InferenceClient

`InferenceClient` runs inference against models deployed on the Hub. It supports serverless (free, rate-limited) and dedicated providers. `AsyncInferenceClient` provides the same API with async/await.

```python
from huggingface_hub import InferenceClient, AsyncInferenceClient

client = InferenceClient(token="hf_...")
async_client = AsyncInferenceClient(token="hf_...")

# Or with a specific provider
client = InferenceClient(
    token="hf_...",
    provider="hf-inference",     # default serverless
    # provider="together",       # Together AI
    # provider="fireworks-ai",   # Fireworks AI
    # provider="deepinfra",      # DeepInfra
    # provider="voyage",         # Voyage AI
    # provider="sambanova",      # SambaNova
    # provider="novita",         # Novita AI
    # provider="featherless-ai", # Featherless AI
    # provider="groq",           # Groq
    # provider="openai",         # OpenAI
    # provider="replicate",      # Replicate
    # provider="cerebras",       # Cerebras
    # provider="scaleway",       # Scaleway
    # provider="fal-ai",         # fal.ai
    # provider="publicai",       # PublicAI
    # provider="zai-org",        # Z.AI
    # provider="nscale",         # Nscale
    # provider="ovhcloud",       # OVHcloud
    # provider="wavespeed",      # Wavespeed
)
```

## Chat completion (OpenAI-compatible)

```python
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is quantum computing?"},
]

# Single response
response = client.chat_completion(
    messages,
    model="meta-llama/Llama-3.3-70B-Instruct",
    max_tokens=512,
    temperature=0.7,
    top_p=0.9,
    stop=["\n\nHuman:"],
    seed=42,
)
print(response.choices[0].message.content)
print(response.usage)  # input_tokens, output_tokens, total_tokens

# Streaming
for chunk in client.chat_completion(messages, stream=True, model="..."):
    print(chunk.choices[0].delta.content, end="", flush=True)

# With tools
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"},
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                },
                "required": ["location"],
            },
        },
    }
]
response = client.chat_completion(
    messages,
    tools=tools,
    tool_choice="auto",  # "auto" | "none" | "required" | {"type": "function", "function": {"name": "get_weather"}}
    model="...",
)

# JSON schema response format
response = client.chat_completion(
    messages,
    response_format={"type": "json_schema", "json_schema": {...}},
    model="...",
)
```

### Response types

| Type | Description |
|---|---|
| `ChatCompletionOutput` | Non-streaming response with `choices`, `usage`, `id`, `model` |
| `ChatCompletionStreamOutput` | Streaming chunk with `choices` (delta), `usage` |
| `ChatCompletionOutputMessage` | Contains `content`, `tool_calls`, `role`, `refusal` |
| `ChatCompletionOutputToolCall` | Contains `id`, `type`, `function` (name + arguments) |

## Text generation

```python
# Basic
output = client.text_generation(
    "Continue: The quick brown fox",
    model="bigscience/bloom",
    max_new_tokens=50,
    temperature=0.7,
    top_k=50,
    top_p=0.95,
    repetition_penalty=1.1,
    stop=["\n"],
    truncate=512,
    watermark=True,
    return_full_text=False,
    seed=42,
    details=True,        # return token details
    decoder_input_details=False,
    watermarked=True,
)

# Streaming
for token in client.text_generation("Hello", stream=True, model="..."):
    print(token, end="", flush=True)
```

## Feature extraction (embeddings)

```python
import numpy as np

embeddings = client.feature_extraction(
    "The cat sat on the mat",
    model="sentence-transformers/all-MiniLM-L6-v2",
)
# Returns numpy array: shape (1, seq_len, hidden_dim) or (1, hidden_dim)

# Batch
embeddings = client.feature_extraction(
    ["Text one", "Text two", "Text three"],
    model="...",
)
```

## Fill mask

```python
result = client.fill_mask(
    "The cat sat on the [MASK].",
    model="bert-base-uncased",
)
for option in result:
    print(option.score, option.token, option.sequence)
```

## Text classification

```python
result = client.text_classification(
    "I love this product!",
    model="distilbert-base-uncased-finetuned-sst-2-english",
)
for label in result:
    print(label.label, label.score)
```

## Text2Text generation

```python
result = client.text2text_generation(
    "Translate English to French: Hello, how are you?",
    model="Helsinki-NLP/opus-mt-en-fr",
    max_new_tokens=50,
)
```

## Summarization

```python
result = client.summarization(
    "Long text to summarize here...",
    model="facebook/bart-large-cnn",
    max_new_tokens=50,
    min_new_tokens=25,
)
```

## Translation

```python
result = client.translation(
    "Hello, how are you?",
    model="Helsinki-NLP/opus-mt-en-fr",
)
```

## Zero-shot classification

```python
result = client.zero_shot_classification(
    "The cat sat on the mat.",
    candidates=["animal", "technology", "politics"],
    model="facebook/bart-large-mnli",
    multi_label=True,
)
for label, score in zip(result.labels, result.scores):
    print(label, score)
```

## Token classification (NER)

```python
result = client.token_classification(
    "My name is Sarah and I live in New York.",
    model="dbmdz/bert-large-cased-finetuned-conll03-english",
    aggregation_strategy="simple",  # "none" | "simple" | "first" | "average" | "max"
)
for entity in result:
    print(entity.entity_group, entity.word, entity.score)
```

## Question answering

```python
result = client.question_answering(
    question="What is the capital of France?",
    context="Paris is the capital and largest city of France.",
    model="deepset/roberta-base-squad2",
)
print(result.answer, result.score, result.start, result.end)
```

## Sentence similarity

```python
result = client.sentence_similarity(
    "The cat sat on the mat.",
    other_sentences=[
        "The cat sat on the chair.",
        "The dog played in the park.",
        "A feline was seated on a rug.",
    ],
    model="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
)
for score in result:
    print(score)
```

## Table question answering

```python
result = client.table_question_answering(
    table={"headers": ["Name", "Age", "City"], "data": [["Alice", 30, "Paris"], ["Bob", 25, "London"]]},
    query="How old is Alice?",
    model="google/tapas-base-finetuned-wtq",
)
print(result.answer, result.coordinates, result.cells)
```

## Document question answering

```python
from PIL import Image

image = Image.open("document.png")
result = client.document_question_answering(
    image,
    question="What is the total amount?",
    model="impira/layoutlm-document-qa",
)
print(result.answer, result.score, result.words)
```

## Image classification

```python
from PIL import Image

image = Image.open("cat.jpg")
result = client.image_classification(image, model="google/vit-base-patch16-224")
for label in result:
    print(label.label, label.score)
```

## Image segmentation

```python
result = client.image_segmentation(
    image,
    model="facebook/detr-resnet-50-panoptic",
)
for segment in result:
    print(segment.label, segment.score)
    # segment.mask is a PIL Image
```

## Object detection

```python
result = client.object_detection(
    image,
    model="facebook/detr-resnet-50",
)
for obj in result:
    print(obj.label, obj.score, obj.box)  # box: {xmin, ymin, xmax, ymax}
```

## Image-to-text (captioning)

```python
result = client.image_to_text(image, model="nlpconnect/vit-gpt2-image-captioning")
print(result)  # string
```

## Text-to-image

```python
image = client.text_to_image(
    "A beautiful sunset over the ocean",
    model="stabilityai/stable-diffusion-xl-base-1.0",
    width=1024,
    height=1024,
    guidance_scale=7.5,
    negative_prompt="blurry, low quality",
    seed=42,
)
image.save("output.png")
```

## Image-to-image

```python
result = client.image_to_image(
    image,
    prompt="Make it look like a painting",
    model="timbrooks/instruct-pix2pix",
)
result.save("output.png")
```

## Depth estimation

```python
result = client.depth_estimation(image, model="Intel/dpt-large")
# Returns PIL Image (depth map)
```

## Image-to-video

```python
video = client.image_to_video(
    image,
    model="ali-vilab/text-to-video-ms-1.7b",
)
# Returns bytes (video file)
```

## Text-to-video

```python
video = client.text_to_video(
    "A cat walking on the beach",
    model="ali-vilab/text-to-video-ms-1.7b",
)
```

## Image-text-to-video

```python
video = client.image_text_to_video(
    image,
    prompt="Animate this image",
    model=".../image-to-video",
)
```

## Automatic speech recognition

```python
result = client.automatic_speech_recognition(
    "/path/to/audio.wav",
    model="openai/whisper-large-v3",
)
print(result)  # string

# With chunks
result = client.automatic_speech_recognition(
    "/path/to/audio.wav",
    model="openai/whisper-large-v3",
    generate_kwargs={"chunk_length_s": 30},
)
```

## Text-to-speech

```python
audio = client.text_to_speech(
    "Hello, world!",
    model="espnet/kan-bayashi_ljspeech_vits",
)
# Returns bytes (audio file)
```

## Text-to-audio

```python
audio = client.text_to_audio(
    "A bird singing in a forest",
    model="facebook/audio-gen-medium",
)
# Returns bytes (audio file)
```

## Audio classification

```python
result = client.audio_classification(
    "/path/to/audio.wav",
    model="superb/hubert-large-superb-er",
)
for label in result:
    print(label.label, label.score)
```

## Audio-to-audio

```python
result = client.audio_to_audio(
    "/path/to/audio.wav",
    model="speechbrain/sepformer-wsj007",
)
for output in result:
    # output.audio is bytes
    # output.label is the track name
    pass
```

## Visual question answering

```python
result = client.visual_question_answering(
    image,
    question="What animal is this?",
    model="dandelin/vilt-b32-finetuned-vqa",
)
for answer in result:
    print(answer.score, answer.answer)
```

## Zero-shot image classification

```python
result = client.zero_shot_image_classification(
    image,
    candidates=["cat", "dog", "bird", "fish"],
    model="openai/clip-vit-large-patch14-336",
    multi_label=True,
)
for label, score in zip(result.labels, result.scores):
    print(label, score)
```

## Health check and endpoint info

```python
# Check if model is available
healthy = client.health_check(model="bert-base-uncased")

# Get endpoint info
info = client.get_endpoint_info(model="bert-base-uncased")
print(info)
```

## Content input types

`InferenceClient` accepts content in multiple formats:

| Type | Description |
|---|---|
| `str` | File path (local) or URL |
| `bytes` | Raw binary data |
| `Path` | Path object |
| `BinaryIO` | File-like object |
| `PIL.Image.Image` | PIL image (for vision tasks) |
| `np.ndarray` | NumPy array (for audio/embedding tasks) |

The client auto-detects the type and handles encoding.

## Providers

Set `provider` in the constructor to route inference to a specific provider:

```python
client = InferenceClient(token="hf_...", provider="together")
```

Available providers: `hf-inference` (default), `together`, `fireworks-ai`, `deepinfra`, `voyage`, `sambanova`, `novita`, `featherless-ai`, `groq`, `openai`, `replicate`, `cerebras`, `scaleway`, `fal-ai`, `publicai`, `zai-org`, `nscale`, `ovhcloud`, `wavespeed`.

Not all tasks are supported by all providers. Check the [provider documentation](https://huggingface.co/docs/huggingface_hub/en/guides/inference) for compatibility.

## AsyncInferenceClient

Same API as `InferenceClient`, all methods are async:

```python
from huggingface_hub import AsyncInferenceClient

async with AsyncInferenceClient(token="hf_...") as client:
    response = await client.chat_completion(messages, model="...")
    async for chunk in client.chat_completion(messages, stream=True, model="..."):
        print(chunk.choices[0].delta.content, end="", flush=True)
```

## MCP Agent

```python
from huggingface_hub import Agent, MCPClient

# MCP-based agent for inference
agent = Agent(
    model="meta-llama/Llama-3.3-70B-Instruct",
    provider="hf-inference",
)
```
