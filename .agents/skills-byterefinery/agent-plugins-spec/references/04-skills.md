# Skills in Plugins

## Format

Agent Skills MUST conform to the [Agent Skills specification](https://agentskills.io/specification). That specification is the source of truth for `SKILL.md` format, frontmatter fields, and directory layout (`scripts/`, `references/`, `assets/`).

Agent Plugins defines how skills are *discovered* within a plugin, not the skill format itself or how clients expose skills to users or models.

## Discovery

- Fixed location: `skills/`
- Each immediate child directory containing `SKILL.md` (resolving to a regular file) is one skill
- Clients MUST NOT recursively search deeper descendants for additional skills

## Invalid skills

If a discovered skill does not conform to the Agent Skills specification, the client MUST skip that skill and continue loading other skills and component types. The client SHOULD report the invalid skill.

## Example layout

```text
skills/
└── deploy/
    ├── SKILL.md          # name: deploy
    ├── scripts/
    │   └── rollback.sh
    └── references/
        └── runbook.md
```

## Key points

- Skills inside plugins follow the standard Agent Skills format exactly
- The plugin manifest (`plugin.json`) does not declare skills inline
- Skill discovery is purely filesystem-based from the fixed `skills/` directory
- One broken skill does not affect other skills or component types
