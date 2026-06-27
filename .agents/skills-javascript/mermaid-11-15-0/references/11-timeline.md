# Timeline Diagrams

Timelines display events chronologically with sections and directional layouts.

## Declaration

```mermaid
timeline
```

## Basic Timeline

Define title, sections (epochs), and events.

```mermaid
timeline
    title History of Computing
    1940s : ENIAC : First electronic computer
    1970s : Microprocessor : Intel 4004
    1990s : World Wide Web : Tim Berners-Lee
    2000s : Smartphones : iPhone
```

## Nested Sections

Group events within titled sections.

```mermaid
timeline
    title Project Milestones
    Q1 2024
        January : Kickoff meeting
        February : Requirements complete
    Q2 2024
        April : Design review
        June : Beta release
```

## Direction Control

Use `direction right` or `direction left` for horizontal timelines.

```mermaid
timeline
    title Product Launch
    direction right
    Pre-launch
        Marketing : Social media campaign
        Sales : Lead generation
    Launch Day
        Event : Press conference
        Support : Help desk ready
```

## Multiple Events per Section

List multiple events under a single section heading.

```mermaid
timeline
    title Web Technologies
    1990s
        HTML : First standard
        CSS : Styling introduced
        JavaScript : Dynamic pages
    2010s
        HTML5 : Modern standard
        React : Component model
```
