# Monorepo packages

All packages are npm-published (MIT) under the `@earendil-works/` scope. Repo: `packages/` in https://github.com/earendil-works/pi. Node ≥ 22.19.

## @earendil-works/pi-ai

Unified multi-provider LLM API: provider collections, automatic auth resolution, token/cost tracking, cross-provider handoffs, context serialization. Only tool-capable models are included (function calling is essential for agentic work).

- **`Models` collection** — `builtinModels()` registers every built-in provider; individual provider factories (`@earendil-works/pi-ai/providers/anthropic` etc.) for tree-shakable bundles. `models.getModel(provider, id)`, `models.stream(model, context)` (full event stream), `models.streamSimple` (simplified).
- **Context** — `{ systemPrompt, messages, tools }`; serializable and transferable between models mid-session (handoffs).
- **Tools** — TypeBox schemas (re-exported: `Type`, `Static`, `TSchema`); streaming partial JSON for tool args; argument validation.
- **Events** — `start`, `text_start/delta/end`, `thinking_start/delta/end`, `toolcall_start/delta/end`, `done`, `error`; `s.result()` yields the final message.
- **Thinking** — unified `streamSimple`/`completeSimple` interface; provider-specific options via `stream`/`complete`.
- **Auth** — provider-level resolution: OAuth credentials, API-key credentials, env vars; `getApiKey` callback for expiring tokens; header transforms.
- **Custom providers** — `createProvider({...})` with pluggable auth, model discovery, filtering, and streaming; call API implementations directly; OpenAI compatibility settings.
- **Faux provider** — deterministic fake provider for tests.
- **OAuth** — Vertex AI, CLI login flows, programmatic OAuth.
- **Browser usage** — works in browsers (proxy pattern); bundling notes for tree shaking.
- **Image input and generation.**

## @earendil-works/pi-agent-core

Stateful agent runtime: tool execution loop, event streaming, steering/follow-up queues.

```typescript
import { Agent } from "@earendil-works/pi-agent-core";
const agent = new Agent({
  initialState: { systemPrompt, model, tools, messages },
  streamFn: models.streamSimple.bind(models),
  convertToLlm: (msgs) => msgs.filter(/* ... */),   // AgentMessage[] → LLM Message[]
  transformContext: async (msgs, signal) => prune(msgs),
  toolExecution: "parallel",        // or "sequential"; per-tool executionMode overrides
  beforeToolCall, afterToolCall, shouldStopAfterTurn,
  steeringMode: "one-at-a-time", followUpMode: "one-at-a-time",
  sessionId, getApiKey, thinkingBudgets,
});
agent.subscribe(async (event, signal) => { /* events */ });
await agent.prompt("Hello!");
agent.steer(msg); agent.followUp(msg);
await agent.waitForIdle(); agent.abort();
```

- **AgentMessage vs LLM messages** — `AgentMessage` can include custom app-specific roles via declaration merging on `CustomAgentMessages`; `convertToLlm` filters/transforms before each LLM call. Flow: `AgentMessage[] → transformContext() → convertToLlm() → Message[] → LLM`.
- **Event sequence** — `agent_start` → per turn: `turn_start`, `message_start/update/end`, tool execution events, `turn_end` (repeats while LLM calls tools) → `agent_end`. Subscribers are awaited in registration order; `agent_end` listeners must finish before `waitForIdle()`/`prompt()` settle.
- **Parallel tool execution** (default) — sequential preflight, concurrent execution, `tool_execution_end` in completion order, toolResult messages in assistant source order. Any tool in the batch with `executionMode: "sequential"` forces the whole batch sequential.
- **`beforeToolCall`** (after arg validation; can block with `terminate: true`), **`afterToolCall`** (postprocess results), **`shouldStopAfterTurn`** (graceful stop after a completed turn, before queue polling).
- **Tools** — `AgentTool` with TypeBox params; **throw** on failure (never return errors as content); `terminate: true` hints (effective only when every result in the batch terminates).
- **Custom message types** — declaration merging + `convertToLlm` handling.
- **Low-level** — `agentLoop`/`agentLoopContinue` async iterators for direct control (observational; no barrier semantics — use the `Agent` class for that).
- **Proxy** — `streamProxy` for browser apps behind a backend.
- **Session backends** — in-memory and file backends in core; the SQLite backend is separate (below). `SessionSearch` contract returns `(sessionId, entryId)` hits as an `AsyncIterable` (backend extensions may add display data).
- `docs/harness.md` in the repo is the deep implementation spec (storage, conversation tree, operation state machine, recovery).

## @earendil-works/pi-tui

Minimal terminal UI framework: differential rendering, synchronized output (CSI 2026, no flicker), bracketed paste, component-based.

- **Renderers** — shared `TUI` interface; `TuiMainScreen` (main buffer, terminal scrollback) and `TuiAltScreen` (alternate buffer, application-owned scrolling, fixed-height viewport, mouse/trackpad/keyboard).
- **Components** — `Text`, `TruncatedText`, `Input`, `Editor`, `Markdown`, `Loader`, `SelectList`, `SettingsList`, `Spacer`, `Image` (Kitty/iTerm2 protocols), `Box`, `Container`, `VStack`, `HStack`, `ScrollView`.
- **API** — `addChild/removeChild`, `setFocus`, `start/stop`, `requestRender`, `addInputListener`, overlays, autocomplete, theme interfaces, `matchesKey`.
- **Layouts** — `VStack`/`HStack` allocate constrained regions in alt-screen; `ScrollView` owns one region (viewport semantics unavailable on main screen).
- Rebuilding on invalidation/theme change patterns are documented in `docs/tui.md`.

## @earendil-works/pi-client (experimental)

Transport-neutral client for remote pi sessions. `PiClient` exchanges length-prefixed CBOR messages through a `ByteTransport` interface (WebSocket, Unix socket, ...). No Node-specific imports at the root; `@earendil-works/pi-client/unix` exports the Unix-socket transport factory.

- `client.connect()`, `createSession({ cwd })`, `attachSession()`, `acquireSession({ mode: "exclusive" | "shared" })` → `SessionLease` (AsyncDisposable; exclusive fails while any lease exists, shared fails under exclusive).
- Server snapshots and successful response snapshots are authoritative; progress events never mutate snapshot state. `subscribe()` (snapshots), `onEvent()` (protocol events).
- No auto-reconnect (`reconnect()` manually). Errors: `PiDisconnectedError`, `PiSessionDetachedError`, `PiSessionOwnershipError`, `PiServerError`. `maxFrameLength` bounds payloads; treat peers as untrusted.

## @earendil-works/pi-protocol (experimental)

Runtime-neutral schemas, strict RFC 8949 CBOR subset, and byte-stream framing for the wire protocol. Wire layout: 4-byte big-endian length + definite-length CBOR item. First client message is always `hello` with `PROTOCOL_VERSION`; then correlated request/response + server event envelopes.

- `encodeClientMessage()`/`encodeServerMessage()` return complete framed `Uint8Array`s; incremental decoders handle arbitrary fragmentation/coalescing.
- Rejected: unknown object properties, tags, indefinite lengths, unsafe numbers, deep nesting, oversized values (defaults 16 MiB frames, 1M entries, 64 levels — configurable).
- `ProtocolValidationError` on schema/framing violations. No compatibility guarantees.

## @earendil-works/pi-server (experimental)

Session server core: `PiServer` composes transport listeners (`PiServerListener` — each must finish its own auth/authorization first) with a `PiServerService` you implement (`listSessions`, `listModels`, `createSession`, `openSession`). `@earendil-works/pi-server/unix` exports `createUnixServer()`/`createUnixListener()`; `@earendil-works/pi-server/testing` provides deterministic conformance tests. Bridges pi-ai domain objects to protocol DTOs (`toProtocolModelMetadata`, message adapters) with exhaustive union mapping. No standalone CLI or coding-agent service — the application supplies the service.

## @earendil-works/pi-telemetry

Vendor-neutral telemetry contracts: callback-based `TelemetryContext`/`TelemetrySpan`, `NOOP_TELEMETRY_CONTEXT`, reference `InMemoryTelemetryContext`, serializable schema definitions with inferred types, conformance tests. No exporter, no global state, no backend dependency — applications provide adapters (OTel, Sentry, logs).

## @earendil-works/pi-session-backend-sqlite-node

Node `node:sqlite` adapter for agent-core sessions: `SqliteSessionRepository` (lazily owns one shared connection), migrations, materialized views, and `createSqliteSessionSearch()` (optional FTS — table/triggers created lazily on first non-blank search, one-time rebuild, then trigger-synced).

## @earendil-works/pi-evals

Model-backed behavioral checks for pi workflows, built on `vitest-evals`. Adapts a real `AgentSession` to isolated temp project/agent dirs and attaches native Pi session artifacts.

```bash
npm run eval -- --provider openai --model gpt-5.6-sol   # or PI_PROVIDER/PI_MODEL env
npm run eval -- src/extensions.eval.ts -t "creates, reloads"
```

Write evals with `createPiCodingAgentHarness({ name, model, noTools, transformSystemPrompt, output })` + `describeEval`. Runs accept one prompt or a sequence of prompt/reload steps. Artifacts: `.eval/` dir with `runs.jsonl` index and `sessions/` JSONL attachments.

## Development from source

```bash
git clone https://github.com/earendil-works/pi-mono && cd pi-mono
npm install --ignore-scripts     # no lifecycle scripts
npm run build                    # refresh model data + build all packages
npm run build:offline            # reuse existing model data
npm run check                    # lint, format, type check
./test.sh                        # non-LLM tests
./pi-test.sh                     # run pi from sources (any cwd)
```

- Forking/rebranding: `piConfig` in `package.json` (`name`, `configDir`, `bin`) affects CLI banner, config paths, env var names.
- Package assets: use `src/config.ts` helpers (`getPackageDir`, `getThemeDir`), never `__dirname` — there are three execution modes (npm, standalone binary, tsx from source).
- Hidden `/debug` command writes `~/.pi/agent/pi-debug.log` (rendered TUI lines + last LLM messages).
- Standalone binaries: GitHub releases ship a SHA256SUMS-covered source archive; `./scripts/build-binaries.sh --offline-model-data --platform linux-x64 --out out` reproduces the official build (Bun-compiled executable).
- Supply chain: direct deps pinned exactly, `package-lock.json` is ground truth, lockfile commits gated behind `PI_ALLOW_LOCKFILE_CHANGE=1`, published CLI ships a generated `npm-shrinkwrap.json`.
