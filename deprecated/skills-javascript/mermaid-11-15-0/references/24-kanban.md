# Kanban Boards

Kanban diagrams visualize workflow stages with tasks in columns.

## Declaration

```mermaid
kanban
    todo[Todo]
        task1[Task description]
```

## Basic Kanban

Define columns with `id[Title]` and tasks indented beneath.

```mermaid
kanban
    backlog[Backlog]
        research[User research]
        analysis[Competitor analysis]
    doing[In Progress]
        wireframes[Wireframes]
        api[API design]
    done[Done]
        kickoff[Project kickoff]
```

## With Metadata

Add ticket, assignee, and priority with `@{ key: value }`.

```mermaid
kanban
    todo[Todo]
        t1[Update Database]@{ ticket: MC-2037, assigned: Alice, priority: High }
        t2[Fix Login Bug]@{ ticket: MC-2038, assigned: Bob, priority: Very High }
    doing[In Progress]
        t3[Build Dashboard]@{ assigned: Carol }
    review[Code Review]
        t4[Review PR #42]@{ assigned: Dave, priority: Low }
```

## Ticket References

Link tasks to external ticket systems.

```mermaid
kanban
    sprint1[Sprint 1]
        a1[Login Page]@{ ticket: PROJ-101, assigned: frontend }
        a2[Auth API]@{ ticket: PROJ-102, assigned: backend }
    sprint2[Sprint 2]
        b1[Dashboard]@{ ticket: PROJ-103, assigned: frontend }
        b2[Notifications]@{ ticket: PROJ-104, assigned: backend }
```
