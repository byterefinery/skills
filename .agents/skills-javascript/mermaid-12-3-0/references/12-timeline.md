# Timelines

Keyword: `timeline`.

Sources: `docs/syntax/timeline.md`, `docs/syntax/all-examples.md` at mermaid@12.3.0.

## Syntax

`{time period} : {event}` — multiple events per period via extra colons or repeated `: event` lines. Time periods and events are plain text (not just numbers). First period on the left, last on the right; first event on top for a period, last at the bottom.

```mermaid
timeline
    title History of Social Media Platform
    2002 : LinkedIn
    2004 : Facebook : Google
    2005 : YouTube
    2006 : Twitter
```

## Sections

`section <name>` groups subsequent time periods (like gantt):

```mermaid
timeline
    title Timeline of Industrial Revolution
    section 17th-20th century
        Industry 1.0 : Machinery, Water power, Steam <br>power
        Industry 2.0 : Electricity, Internal combustion engine, Mass production
    section 21st century
        Industry 4.0 : Internet, Robotics, Internet of Things
        Industry 5.0 : Artificial intelligence, Big data, 3D printing
```

## Verified examples

Product roadmap with sections — see all-examples "Timeline Diagram" section for the full verified block.
