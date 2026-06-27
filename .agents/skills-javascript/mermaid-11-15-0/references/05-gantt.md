# Gantt Charts

Gantt charts visualize project schedules with tasks, durations, dependencies, and milestones.

## Declaration

```mermaid
gantt
```

## Basic Tasks and Dates

Define title, axis format, and tasks with start dates. Use `section` to group.

```mermaid
gantt
    title Project Timeline
    dateFormat  YYYY-MM-DD
    section Phase 1
    Requirements     :a1, 2024-01-01, 14d
    Design           :a2, after a1, 10d
    section Phase 2
    Development      :a3, after a2, 21d
    Testing          :a4, after a3, 7d
```

## Milestones

Milestones are zero-duration tasks marked with `milestone`.

```mermaid
gantt
    title Release Plan
    dateFormat  YYYY-MM-DD
    section Planning
    Kickoff         :ms1, milestone, 2024-03-01, 0d
    Requirements    :a1, 2024-03-01, 14d
    section Execution
    Development     :a2, after a1, 30d
    Launch          :ms2, milestone, after a2, 0d
```

## Excluding Weekends and Holidays

Use `excludes` to skip weekends or specific dates.

```mermaid
gantt
    title Working Days Only
    dateFormat  YYYY-MM-DD
    excludes    weekends
    section Sprint
    Task A       :a1, 2024-06-01, 5d
    Task B       :a2, after a1, 3d
```

## Active and Completed Tasks

Mark tasks as done with `done` or partially complete with `crit`.

```mermaid
gantt
    title Task Status
    dateFormat  YYYY-MM-DD
    section Team Alpha
    Completed task   :done, des1, 2024-01-01, 5d
    Active task      :active, des2, 2024-01-06, 3d
    Future task      :des3, after des2, 5d
```

## Dependencies and Parallel Tasks

Chain tasks with `after` and run parallel tracks.

```mermaid
gantt
    title Dependency Chain
    dateFormat  YYYY-MM-DD
    section Frontend
    UI Design     :a1, 2024-02-01, 10d
    UI Build      :a2, after a1, 15d
    section Backend
    API Design    :b1, 2024-02-01, 8d
    API Build     :b2, after b1, 12d
    section Integration
    Merge         :c1, after a2 and b2, 5d
```

## Custom Axis Formats

Control date display with `axisFormat`.

```mermaid
gantt
    title Monthly View
    dateFormat  YYYY-MM
    axisFormat  %b %Y
    section Q1
    Jan tasks   :a1, 2024-01, 31d
    Feb tasks   :a2, 2024-02, 29d
```
