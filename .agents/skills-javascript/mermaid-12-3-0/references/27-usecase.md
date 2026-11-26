# Use case diagrams

Keyword: `usecase-beta` (beta, v12.0.0+). Each statement goes on its own physical line. Since v12.0.0 use case diagrams default to the `redux-color` theme, `neo` look, and ELK layout.

Sources: `docs/syntax/usecase.md` at mermaid@12.3.0.

## Actors and use cases

```mermaid
usecase-beta
direction LR
actor Customer("Customer")
systemBoundary "Order system"
  Checkout("Place order")
end
Customer --> Checkout
```

- `direction TD|TB|BT|LR|RL`.
- Actors: `actor Name` or `actor Name("Label")` — actors are **never inferred** from a relationship; they require an `actor` declaration.
- Use cases: `Name("Label")` (ellipse) or `Name[Label]` (rectangle); a quoted declaration `"Reset password"` gets a deterministic id (`Reset_password`).
- Identifiers match `[A-Za-z0-9_]+`; endpoints may appear before their declaration.
- Actor variants: `@{ type: hollow }`, `@{ type: awesome }`, `@{ icon: "fa:user" }` (icon packs must be registered; missing icons fall back).
- Business elements: `@{ business: true }` (normal/hollow actors and ellipse use cases only).
- Stereotypes: one visible `<<...>>` after metadata (e.g. `actor SalesAgent("Sales agent")@{ business: true } <<Employee>>`).

## System boundaries

`systemBoundary <id>["Title"]@{ … }:::<classes>` … `end`. Default boundary type is `rect`; `@{ type: package }` renders a package tab. Boundaries are one level deep and contain only actor/use case declarations, blank lines, and `%%` comments; relationships stay at top level. An element belongs to at most one boundary.

## Relationships

- Associations: `-->`, `<--`, `--`, `--o`, `o--`, `--x`, `x--` (seven solid forms; marker direction/type preserved). Labels: `User -- "label" --> Login`.
- Include/extend: `Checkout ..> : include Payment`, `ApplyCoupon ..> : extend Checkout` — rendered with UML `«include»`/`«extend»` labels; both endpoints must be use cases.
- Generalization: `Admin --|> Person` (specialized → general); two actors or two use cases.
- Edge IDs: `Customer opens@-- "starts checkout" ---> Checkout`; styleable via `classDef`/`class`/`style` and `opens@{ animation: fast }` / `animate: false`.
- Extra dashes increase minimum length on point/reversed-point/markerless solid associations only.

## Notes, JSON tables, styling

- `note for Login "`Requires an **active session**`"` attaches a note (Markdown strings allowed). Notes are ordinary graph nodes — their placement follows the layout.
- JSON nodes/tables, `classDef`/`class`, and colors are documented in the docs sections "JSON tables", "Styling", "Colors" (per-element colour rotation included).
- `accTitle`/`accDescr` for accessibility (docs "Accessibility").

## Verified examples

Actor collaboration and system boundaries — see all-examples "Use Case Diagram" section for the full verified blocks (basic use cases, boundaries, actor collaboration).

## PlantUML migration

The docs include a "Migrating from PlantUML" section listing constructs that parse but mean something else — consult it when converting.
