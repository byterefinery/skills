# Sequence Diagrams

Sequence diagrams model interactions between participants over time, showing message ordering and activation lifelines.

## Declaration

```mermaid
sequenceDiagram
```

## Participants and Messages

Use `->>` for synchronous (solid arrow) and `-` for return messages. Add participant labels with `participant`.

```mermaid
sequenceDiagram
    participant Alice
    participant Bob
    Alice->>Bob: Hello Bob, how are you?
    Bob-->>Alice: Great!
```

## Activations

Use `activate`/`deactivate` or the shorthand `autonumber`. The `over` keyword spans activations across participants.

```mermaid
sequenceDiagram
    participant A
    participant B
    activate A
    A->>B: Work request
    activate B
    B-->>A: Work done
    deactivate B
    deactivate A
```

## Loops and Conditions

Group messages with `loop`, `alt`/`else`, `opt`, `par` (parallel), and `break`.

```mermaid
sequenceDiagram
    participant Client
    participant Server
    loop Every 5 seconds
        Client->>Server: Ping
        Server-->>Client: Pong
    end
    opt If user is logged in
        Client->>Server: Fetch data
        Server-->>Client: Data
    end
```

## Autonumber and Notes

`autonumber` prefixes messages with sequential numbers. `note` adds annotations.

```mermaid
sequenceDiagram
    autonumber
    Alice->>Bob: Hello Bob, how are you?
    Note right of Bob: Bob thinks
    Bob-->>Alice: I am good thanks!
```

## Dotted and Async Messages

Use `-x` for destroyed messages, `--)` for async (open arrowhead).

```mermaid
sequenceDiagram
    Alice->>Bob: Call me
    Bob--)Alice: Async reply
    Alice-x Bob: Connection lost
```
