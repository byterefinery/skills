# Treemaps

Keyword: `treemap-beta` (plain `treemap` works too). Hierarchical data as nested rectangles; size proportional to value.

Sources: `docs/syntax/treemap.md` at mermaid@12.3.0.

## Syntax

- Section/parent nodes: quoted text `"Section Name"`.
- Leaf nodes: `"Leaf Name": value`.
- Hierarchy by indentation (spaces or tabs).
- Styling: `:::class` suffix on nodes; `classDef class1 fill:red,color:blue,stroke:#FFD600;`.

```mermaid
treemap-beta
"Category A"
    "Item A1": 10
    "Item A2": 20
"Category B"
    "Item B1": 15
    "Item B2": 25
```

Hierarchical with styling (docs):

```mermaid
treemap-beta
"Products"
    "Electronics"
        "Phones": 50
        "Computers": 30
        "Accessories": 20
    "Clothing"
        "Men's": 40
        "Women's": 40
```

Styling example:

```mermaid
treemap-beta
"Section 1"
    "Leaf 1.1": 12
    "Section 1.2":::class1
      "Leaf 1.2.1": 12
"Section 2"
    "Leaf 2.1": 20:::class1
    "Leaf 2.2": 25
    "Leaf 2.3": 12

classDef class1 fill:red,color:blue,stroke:#FFD600;
```

Monthly household budget and disk usage with styling — see all-examples "Treemap" section for the full verified blocks.
