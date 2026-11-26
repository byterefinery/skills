# Kanban diagrams

Keyword: `kanban`. Tasks moving through workflow stages.

Sources: `docs/syntax/kanban.md` at mermaid@12.3.0.

## Syntax

- Columns: `columnId[Column Title]` (id optional — a bare title also works).
- Tasks under a column, indented: `taskId[Task Description]` or bare `[Description]`.
- Task metadata: `@{ key: value, ... }` with supported keys:
  - `assigned` — responsible person
  - `ticket` — ticket/issue number
  - `priority` — `Very High` | `High` | `Low` | `Very Low`

```mermaid
kanban
todo[Todo]
  id3[Update Database Function]@{ ticket: MC-2037, assigned: 'knsv', priority: 'High' }
```

Config: `kanban: { ticketBaseUrl: 'https://…/browse/#TICKET#' }` — `#TICKET#` is replaced with the task's ticket value to build the link.

## Verified examples

Full board (docs):

```mermaid
---
config:
  kanban:
    ticketBaseUrl: 'https://mermaidchart.atlassian.net/browse/#TICKET#'
---
kanban
  Todo
    [Create Documentation]
    docs[Create Blog about the new diagram]
  [In progress]
    id6[Create renderer so that it works in all cases. We also add some extra text here for testing purposes. And some more just for the extra flare.]
  id9[Ready for deploy]
    id8[Design grammar]@{ assigned: 'knsv' }
  id10[Ready for test]
    id4[Create parsing tests]@{ ticket: MC-2038, assigned: 'K.Sveidqvist', priority: 'High' }
    id66[last item]@{ priority: 'Very Low', assigned: 'knsv' }
  id11[Done]
    id5[define getData]
    id3[Update DB function]@{ ticket: MC-2037, assigned: knsv, priority: 'High' }
  id12[Can't reproduce]
    id3[Weird flickering in Firefox]
```

## Gotchas

- Priority values are case-sensitive strings: `Very High`, `High`, `Low`, `Very Low`.
