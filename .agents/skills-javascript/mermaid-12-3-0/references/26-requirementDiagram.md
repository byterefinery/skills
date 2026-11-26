# Requirement diagrams (SysML)

Keyword: `requirementDiagram`. Follows SysML v1.6 modeling specs. Since v12.0.0 requirement diagrams default to the `redux-color` theme, `neo` look, and ELK layout.

Sources: `docs/syntax/requirementDiagram.md` at mermaid@12.3.0.

## Syntax

```mermaid
requirementDiagram
    requirement test_req {
        id: 1
        text: the test text.
        risk: high
        verifymethod: test
    }

    element test_entity {
        type: simulation
    }

    test_entity - satisfies -> test_req
```

- `requirement <name> { id: …, text: …, risk: …, verifymethod: … }` — properties in the block (e.g. `id`, `text`, `risk`, `verifymethod`).
- `functionalRequirement` and other requirement types exist (docs "Requirement" section lists the accepted types).
- `element <name> { type: … }` — a system element (e.g. `type: simulation`, `type: service`).
- Markdown formatting is supported in text (docs "Markdown Formatting").
- Relationships: `<from> - <verb> -> <to>` — verbs include `satisfies`, `contains` (docs "Relationship" section lists the accepted verbs).

## Verified examples

Checkout example (docs):

```mermaid
requirementDiagram
  requirement checkout_req {
    id: 1
    text: Orders must be payable online.
    risk: high
    verifymethod: test
  }
  functionalRequirement payment_req {
    id: 1.1
    text: Card payments must be authorised.
    risk: high
    verifymethod: test
  }
  element checkout_service {
    type: service
  }
  checkout_req - contains -> payment_req
  checkout_service - satisfies -> payment_req
```

E-bike braking system — see all-examples "Requirement Diagram" section for the full verified block.

`direction TD`/`LR` etc. sets orientation (docs "Direction"). Styling via direct styles and `classDef`/`class` (docs "Styling").
