# Block Diagrams

Block diagrams give full layout control over component positioning using a grid-based approach.

## Declaration

```mermaid
block
    A B C
```

## Basic Blocks

List blocks on one line for horizontal layout. Use `columns N` to define grid width.

```mermaid
block
    columns 3
    A["Input"]
    B["Process"]
    C["Output"]
    A --> B --> C
```

## Nested Blocks (Containers)

Group blocks inside named containers with `block:end`.

```mermaid
block
    columns 1
    Input["User Input"]
    block:Backend
        Auth["Auth"]
        API["API Server"]
        DB[("Database")]
    end
    Output["Response"]
    Input --> Backend
    Backend --> Output
```

## Block Shapes

Use flowchart-style shape syntax: `id[rect]`, `id(round)`, `id{diamond}`, `id((circle))`.

```mermaid
block
    columns 1
    db(("Database"))
    blockArrow<["flow"]>(down)
    block:App
        A["Frontend"]
        B("Backend")
    end
    App --> db
```

## Styling and Links

Apply styles and define connections between blocks.

```mermaid
block
    columns 1
    A["Web Server"]
    B["API Gateway"]
    C["Service A"]
    D["Service B"]
    A --> B
    B --> C
    B --> D
    style A fill:#4a90d9,color:#fff
    style B fill:#7ed321,color:#000
```

## Arrows and Spacing

Use arrow blocks for visual flow indicators. Add `space` for gaps.

```mermaid
block
    columns 1
    Start["Start"]
    blockArrow1<[" "]>(down)
    Process["Processing"]
    space
    blockArrow2<[" "]>(down)
    Result["Result"]
    Start --> Process --> Result
```
