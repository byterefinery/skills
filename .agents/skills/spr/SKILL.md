---
name: spr
description: Compress text into Sparse Priming Representations (SPR) or decompress SPRs back to full text. Supports PDF/Office input via markdown conversion. Use when the user wants to compress content into SPR format, decompress/expand SPRs, or needs token-efficient knowledge representations for LLM context.
metadata:
  tags:
    - meta
    - knowledge
    - spr
---

# spr

## Overview

Sparse Priming Representation (SPR) is a technique for compressing complex ideas, memories, or concepts into a minimal set of keywords, phrases, or statements. This enables language models or subject matter experts to quickly reconstruct the original idea with minimal context. SPR mimics the natural human process of recalling and recombining sparse memory representations, facilitating efficient knowledge storage and retrieval.

SPRs are the most token-efficient way to convey complex concepts to models for in-context learning. Compress huge blocks of information — company data, chat logs, specific events, or whatever — into SPRs, store the SPR, and feed it to the LLM at inference instead of the raw human-readable data.

## Theory

LLMs are a kind of deep neural network. They have been demonstrated to embed knowledge, abilities, and concepts, ranging from reasoning to planning, and even to theory of mind. These are called latent abilities and latent content, collectively referred to as **latent space**.

The latent space of an LLM can be activated with the correct series of words as inputs, which will create a useful internal state of the neural network. This is not unlike how the right shorthand cues can prime a human mind to think in a certain way. Like human minds, LLMs are **associative** — you only need to use the correct associations to "prime" another model to think in the same way.

Human memory is known for its efficiency in storing and recalling information in a highly compressed and contextually relevant manner. Our brains often store memories as sparse, interconnected representations that can be quickly combined, modified, and recalled when needed. SPR leverages this insight by focusing on reducing information to its most essential elements while retaining the context required for accurate reconstruction.

## Compression

When the user provides content to compress into an SPR:

### Input Handling

- **PDF or Office files** — use the `markdown` skill to convert the input file to markdown first. Then compress the resulting markdown text into an SPR. The output file should use the basename of the original input with suffix `-compressed` and extension `.md` (e.g., `report.pdf` → `report-compressed.md`).
- **Large text files** — input files can be very long. Read the input linearly from start to finish and incrementally update the compressed SPR. Use the `read` tool with `offset`/`limit` to process the file in sequential segments. After each segment, update the running SPR — add new primings, refine existing ones, merge overlapping concepts, and discard redundant material. This streaming approach lets earlier context inform how later content is compressed, preserving cross-section associations that chunk-and-merge would lose. The output file should use the basename of the input with suffix `-compressed` and extension `.md` (e.g., `notes.txt` → `notes-compressed.md`).
- **Multi-lingual documents** — keep the compressed SPR output in the original multi-lingual text. Do not translate any section into a single language. Preserve each section's original language in the primings verbatim. When the document switches languages, note the language change explicitly (e.g., "[lang:de]", "[lang:ja]") so the decompressor reproduces the same language pattern. Never normalize all content into one language — language choice carries semantic weight in legal terms, technical jargon, and cultural references.
- **Document type awareness** — recognize the genre of the input (legal documents, financial reports, development documentation, technical specs, chat logs, etc.) and encode genre-specific conventions in the SPR. Legal documents need clause structure, defined terms, and obligation language; financial documents need numerical relationships, reporting periods, and material figures; development docs need API signatures, data models, type definitions, and workflow sequences. Encode the genre itself as a priming so the decompressor knows what kind of document to reconstruct.
- **Text prompt** — compress the text directly into an SPR and output the result as text.

### Compression Methodology

Render the input as a distilled list of succinct statements, assertions, associations, concepts, analogies, and metaphors. The idea is to capture as much, conceptually, as possible but with as few words as possible. Write it in a way that makes sense to you, as the future audience will be another language model, not a human. Use complete sentences.

Preserve the most important sections of the document — definitions, key terms, critical data points, core arguments, structural anchors, and any section carrying heavy conceptual weight. Ensure these are fully captured in the SPR, even at the cost of brevity in lighter sections. Do not drop important sections to save tokens; the decompressor needs them.

When a section contains table or structured data, explicitly note that it was table data in the primings. Specify: the table's purpose, column names and count, row count, key values or trends, and any relationships between columns. For example: "Table: quarterly revenue by region — 4 columns (Quarter, EMEA, APAC, Americas), 12 rows (Q1 2022–Q4 2025), key trend: APAC overtakes EMEA in Q3 2024." This lets the decompressor reconstruct the tabular structure rather than flattening it into prose.

### Compression Rules

1. **Distill to essentials** — reduce information to its most critical elements while preserving the context needed for accurate reconstruction.
2. **Use complete sentences** — each priming must be a full sentence, not fragments.
3. **Write for an LLM audience** — the output is meant to prime another model, not to be read by a human. Prioritize associative triggers over readability.
4. **Capture conceptual density** — maximize the amount of conceptual information per token. Use metaphors, analogies, and associations that activate latent space efficiently.
5. **Preserve reconstruction context** — include enough context that the decompressor can faithfully reconstruct the original idea, even if details must be inferred.
6. **Order matters** — arrange primings so that earlier statements set up associations for later ones, building a coherent mental model progressively.
7. **Preserve multi-lingual context** — keep primings in the original language of each section. Note language switches. Never normalize all content into a single language.

## Decompression

When the user provides an SPR to decompress:

### Input Handling

- **PDF or Office files** — use the `markdown` skill to convert the input file to markdown first. Then decompress the SPR content found in the resulting markdown. The output file should use the basename of the original input with suffix `-decompressed` and extension `.md` (e.g., `report-compressed.pdf` → `report-decompressed.md`).
- **Large SPR files** — iteratively and intelligently read the SPR file in chunks so it fits within context.
- **Multi-lingual SPRs** — reproduce the original multi-lingual context. Each section should be decompressed in the same language it was originally compressed from. Follow language cues embedded in the primings. Use the `read` tool with `offset`/`limit` to process segments. Decompress each chunk, then stitch the results into a single coherent output, resolving any cross-chunk references or repeated context. The output file should use the basename of the input with suffix `-decompressed` and extension `.md` (e.g., `notes-compressed.md` → `notes-decompressed.md`).
- **Text prompt** — decompress the SPR directly and output the result as text.

### Decompression Methodology

Use the primings given to you to fully unpack and articulate the concept. Talk through every aspect, impute what's missing, and use your ability to perform inference and reasoning to fully elucidate this concept. The output should be in the form of the original article, document, or material.

Go from compressed state to decompressed by following each priming and expanding it into full prose. Use the SPR's structural cues — section markers, language tags, table descriptors, genre hints — to guide reconstruction. The primings are instructions for how to rebuild the original; treat them as a blueprint, not as the final text.

### Decompression Rules

1. **Expand fully** — unpack every priming into its complete meaning. Do not leave anything implied or abbreviated.
2. **Impute missing details** — use inference and reasoning to fill in gaps that the SPR left implicit. The goal is faithful reconstruction, not literal translation.
3. **Maintain original structure** — reconstruct the output in the form of the original article, document, or material that the SPR was derived from.
4. **Talk through every aspect** — cover all dimensions of the concept, not just the surface-level meaning. Explore implications, connections, and nuances.
5. **Use complete prose** — the decompressed output should be natural, readable text suitable for human consumption, unlike the compressed SPR which targets LLM latent space.
6. **Reproduce multi-lingual context** — decompress each section in its original language. Preserve code-switching patterns and language-specific conventions. Follow language markers in the SPR primings. The output must match the multi-lingual pattern of the original document.
7. **Reconstruct tables** — when a priming describes table data (column names, row count, key trends), recreate it as a proper Markdown table. Use the column headers and row count from the priming as the skeleton, then fill in values using inference from the surrounding primings. If exact values are not in the SPR, reconstruct plausible values consistent with the described trends and relationships.
8. **Reconstruct structured data** — for lists, enumerations, code blocks, or other structured elements noted in the SPR, recreate the original structure. If the priming says "enumerated list of 5 compliance requirements," output a numbered list with full prose for each item.
9. **Follow genre cues** — if the SPR encodes a document genre (legal, financial, technical), match the decompressed output to that genre's conventions. Legal text uses defined terms and obligation language; financial text uses reporting periods and material figures; technical docs use API signatures and type definitions.

## Gotchas

- **SPRs are not summaries** — they are associative primings designed to activate latent space in another model. A summary preserves readability; an SPR preserves reconstructability. Do not confuse the two.
- **Compression loses literal detail** — the SPR captures conceptual essence, not verbatim content. Decompression requires inference to fill gaps. This is by design, not a bug.
- **Quality depends on specificity** — vague primings produce vague reconstructions. When compressing, be precise about the associations you encode. When decompressing, lean into the associations and expand them fully.
- **Iterative refinement helps** — if the decompressed output misses key details, the SPR may need additional primings. Compression is sometimes an iterative process to find the right balance of brevity and fidelity.
- **No scripts involved** — this skill operates entirely through text instructions. Compression and decompression are performed directly by the LLM following the methodology above.
- **Iterative reading for large files** — always use `read` with `offset`/`limit` to process files that won't fit in context in one pass. For compression, chunk → compress each chunk → merge SPRs into one coherent output. For decompression, chunk → decompress each chunk → stitch results together. Remove redundancy and resolve cross-chunk references in the merge step.
- **Output naming convention** — compressed outputs get `-compressed` suffix, decompressed outputs get `-decompressed` suffix, appended to the input file's basename before the extension (e.g., `report.pdf` → `report-compressed.md`, `notes-compressed.md` → `notes-decompressed.md`).
- **Multi-lingual content carries meaning in its language** — language choice is not incidental. Legal terms, technical jargon, and cultural references often lose precision when translated. Keep primings in the original language; note switches explicitly.
- **Incremental compression beats chunk-and-merge for very long files** — reading linearly and updating a running SPR lets you carry forward context from earlier sections. Chunk-and-merge works but risks losing cross-section associations. The incremental approach produces a more coherent SPR.
- **Table data needs explicit markers** — without noting that a section was tabular, the decompressor will flatten it into prose. Always specify structure (columns, rows, key trends) when compressing tables. When decompressing, use these markers to rebuild proper Markdown tables — the priming's column/row description is the skeleton, surrounding primings provide the values.
- **SPR output stays multi-lingual** — the compressed file itself should be in the original languages of the source, not translated. Language tags (`[lang:xx]`) mark switches for the decompressor. Never produce a mono-lingual SPR from a multi-lingual source.
- **Genre cues guide reconstruction** — encoding the document genre in the SPR (e.g., "Genre: German employment contract") tells the decompressor what conventions, structure, and register to use when rebuilding the full text.
