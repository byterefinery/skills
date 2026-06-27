# Mindmaps

Mindmaps display hierarchical information radiating from a central topic.

## Declaration

```mermaid
mindmap
    root
        Plans
```

## Basic Structure

Root node with indented children. Use `root` or any identifier for the center.

```mermaid
mindmap
    root
        Plans
            Trip
                Hotel
                Flight
        Ideas
            Feature A
            Feature B
```

## Root Labeling

Label the root node explicitly.

```mermaid
mindmap
    root((Project))
        Research
            Market Analysis
            User Interviews
        Design
            Wireframes
            Prototypes
        Development
            Frontend
            Backend
```

## Shapes and Icons

Use shape brackets: `([square])`, `[(hexagon)]`, `([default])`, `([four point star])`. Add emoji icons.

```mermaid
mindmap
    root
        Plans
            id[Trip]
                Hotel
                Flight
        Ideas
            id2(Feature A)
            id3[Feature B]
```

## Markdown in Labels

Support bold, italic, and links inside labels.

```mermaid
mindmap
    root
        **Important task**
        *Subtask*
        Normal node
```
