# Entity-Relationship Diagrams

ER diagrams model database schemas with entities, attributes, keys, and relationship cardinality.

## Declaration

```mermaid
erDiagram
```

## Basic Entities and Relationships

Define entities with `{}`. Relationships use `||--o{` (one-to-many), `|--|{` (many-to-one), etc.

```mermaid
erDiagram
    CUSTOMER ||--o{ ORDER : places
    ORDER ||--|{ LINE-ITEM : contains
    CUSTOMER }|--|{ DELIVERY-ADDRESS : uses
```

## Attributes and Keys

List attributes inside entity blocks. Mark primary keys with `PK` and foreign keys with `FK`.

```mermaid
erDiagram
    CUSTOMER {
        int id PK
        string name
        string email
    }
    ORDER {
        int id PK
        int customer_id FK
        date order_date
        decimal total
    }
```

## Cardinality Notation

`||` = exactly one, `|o` = zero or one, `}{` = one or more, `o{` = zero or more.

```mermaid
erDiagram
    AUTHOR ||--o{ BOOK : writes
    BOOK }o--o{ GENRE : belongs_to
    PUBLISHER |o--o{ BOOK : publishes
```

## Data Types

Mermaid supports common SQL types: `int`, `string`, `boolean`, `date`, `datetime`, `decimal`, `enum`.

```mermaid
erDiagram
    PRODUCT {
        int id PK
        string name
        decimal price
        boolean in_stock
        date created_at
        enum status FK
    }
    STATUS {
        string value PK
        string label
    }
```

## Many-to-Many Relationships

Use junction entities for many-to-many.

```mermaid
erDiagram
    STUDENT }|--|{ ENROLLMENT : has
    COURSE }|--|{ ENROLLMENT : has
    ENROLLMENT {
        int id PK
        int student_id FK
        int course_id FK
        date enrolled_on
    }
```
