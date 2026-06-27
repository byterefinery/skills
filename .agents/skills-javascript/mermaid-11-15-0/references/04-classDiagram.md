# Class Diagrams

Class diagrams model the static structure of a system using UML-style classes, interfaces, enums, and their relationships.

## Declaration

```mermaid
classDiagram
    class Animal
```

## Basic Classes with Attributes and Methods

Use `+` (public), `-` (private), `#` (protected), `~` (package). Prefix methods/attributes with type annotations.

```mermaid
classDiagram
    class Animal {
        +String name
        +int age
        +makeSound() void
        +move() void
    }
```

## Inheritance and Realization

`--|>` is inheritance (extends). `..|>` is realization (implements).

```mermaid
classDiagram
    class Animal
    class Dog
    class Cat
    class Pet
    Animal <|-- Dog
    Animal <|-- Cat
    Animal <|.. Pet
```

## Associations and Composition

`--` is association, `*--` is composition, `o--` is aggregation. Add multiplicity with `1`, `*`, `0..1`.

```mermaid
classDiagram
    class Order
    class Customer
    class Product
    Customer "1" --> "*" Order : places
    Order "*" --> "1..*" Product : includes
```

## Composition and Aggregation

Composition (filled diamond) vs aggregation (open diamond).

```mermaid
classDiagram
    class Car
    class Engine
    class Driver
    Car *-- Engine : has
    Car o-- Driver : driven by
```

## Interfaces

Use `<<interface>>` stereotype.

```mermaid
classDiagram
    class Painter {
        +paint() void
    }
    class PaintInterface <<interface>> {
        +getColor() String
    }
    PaintInterface <|.. Painter
```

## Enums and Namespaces

Enums use `<<enumeration>>`. Wrap classes in namespaces with `namespace`.

```mermaid
classDiagram
    class Color <<enumeration>> {
        RED
        GREEN
        BLUE
    }
    namespace MyNamespace {
        class MyClass
    }
```

## Notes and Annotations

Attach notes to classes.

```mermaid
classDiagram
    class Animal
    note for Animal "This is a base class"
```
