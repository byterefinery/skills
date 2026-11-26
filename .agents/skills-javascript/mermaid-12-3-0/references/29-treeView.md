# Tree views

Keyword: `treeView-beta` (beta). Directory-like trees with file/folder icons, connector lines, and annotations.

Sources: `docs/syntax/treeView.md` at mermaid@12.3.0.

## Indentation input

Structure comes from indentation. Directories get a trailing `/` (render bold). Labels may be bare or quoted (spaces need quotes). Icons are hidden by default — enable with `showIcons` config or per-node `icon()`.

```
treeView-beta
    my-project/
        src/
            index.js
        package.json
        README.md
```

## Box-drawing input

Alternatively use box-drawing characters (`├──`, `└──`, `│`, heavy variants `┣━━`, `┗━━`, `┃`) — auto-detected, no extra keyword:

```mermaid
treeView-beta
├── src/
│   ├── index.ts
│   └── utils.ts
├── package.json
└── README.md
```

## Annotations

- `:::highlight` (or `:::class`) highlights nodes.
- `icon(logos:react)` sets a per-node icon.
- `## description` appends an inline description after the label.

```mermaid
treeView-beta
├── src/
│   ├── App.tsx :::highlight icon(logos:react) ## main component
│   └── index.ts ## entry point
├── .env ## environment variables
└── README.md
```

Project file structure, shared drive with quoted names, annotations, file-type icons via config maps, and unicode icons — see all-examples "TreeView" section for the full verified blocks.
