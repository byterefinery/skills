# Hello Invocation

The instruction source for the "Invoked with 'Hello'" scenario in SKILL.md's `## Usage`. When the user invokes the skill with "Hello", load this file and follow it — SKILL.md deliberately holds no instructions for this case.

## Response

Reply exactly:

> world

No greeting, no punctuation, no commentary, no script. The reply is the single word above and nothing else.

## Why it lives here

This file demonstrates progressive disclosure. The logic for the "Hello" case sits in a reference file instead of in SKILL.md or `scripts/`, so the agent must open a reference to learn how to respond. The fixed "Hello" → "world" mapping is part of the demonstration.
