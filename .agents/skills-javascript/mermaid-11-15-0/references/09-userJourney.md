# User Journey Diagrams

User journey diagrams map the experience of a user through a process, with tasks scored by satisfaction.

## Declaration

```mermaid
journey
```

## Basic Journey

Define title, task count, and actor sections with scored tasks.

```mermaid
journey
    title My Day
    section Go to work
      Make tea: 5: Me
      Go upstairs: 3: Me
      Do work: 1: Me
    section Go home
      Stop by grocer: 4: Me
      Go home: 5: Me
      Make dinner: 1: Me
```

## Multiple Actors

Add multiple actors to a single journey.

```mermaid
journey
    title Team Workflow
    section Planning
      Review backlog: 5: PM, Dev
      Estimate tasks: 3: Dev
    section Execution
      Code feature: 4: Dev
      Review PR: 3: Senior
      Deploy: 2: DevOps
```

## Section Grouping

Use sections to group related phases.

```mermaid
journey
    title Shopping Experience
    section Online
      Browse products: 5: Customer
      Add to cart: 4: Customer
      Checkout: 3: Customer
    section Delivery
      Track order: 4: Customer
      Receive package: 5: Customer
```
