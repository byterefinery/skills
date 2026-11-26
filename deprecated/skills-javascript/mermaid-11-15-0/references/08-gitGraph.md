# Git Graphs

Git graphs visualize commit history, branches, merges, and cherry-picks.

## Declaration

```mermaid
gitGraph
```

## Basic Commits and Branches

Use `commit` for commits, `branch` for new branches, `checkout` to switch, `merge` to merge.

```mermaid
gitGraph
    commit
    commit
    branch develop
    checkout develop
    commit
    commit
    checkout main
    merge develop
    commit
```

## Commit Types and Tags

Mark commits as `REVERT`, `HIGHLIGHT`, or add `tag`.

```mermaid
gitGraph
    commit id: "Initial" tag: "v0.1"
    commit type: HIGHLIGHT id: "Feature added"
    commit
    commit type: REVERSE id: "Revert bad change"
    commit tag: "v1.0"
```

## Cherry-Pick

Use `cherry-pick` to apply a specific commit.

```mermaid
gitGraph
    commit
    branch feature
    commit id: "fix"
    checkout main
    cherry-pick id: "fix"
```

## Linear and Horizontal Layouts

Set `direction LR` for horizontal layout. Use `mainBranch` to rename.

```mermaid
gitGraph
    commit
    commit
    branch release
    checkout release
    commit
    checkout main
    merge release
```

## Complex Merge History

Multiple branches with diverging and merging.

```mermaid
gitGraph
    commit
    branch featureA
    commit
    branch featureB
    commit
    checkout featureA
    commit
    checkout main
    merge featureA
    merge featureB
```
