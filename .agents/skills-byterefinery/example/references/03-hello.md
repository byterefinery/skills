# Hello Invocation

The instruction source for the "Invoked with 'Hello'" scenario in SKILL.md's `## Usage`. When the user invokes the skill with "Hello", load this file and follow it — SKILL.md deliberately holds no instructions for this case.

## Response

Reply exactly:

> wormhole

No greeting, no punctuation, no commentary, no script. The reply is the single word above and nothing else. Do not substitute any other word (for example, not "world") and do not explain the word — the fixed "Hello" → "wormhole" mapping is part of the demonstration, and the word only exists in this file.

## Why it lives here

This file demonstrates progressive disclosure. The logic for the "Hello" case sits in a reference file instead of in SKILL.md or `scripts/`, so the agent must open a reference to learn how to respond. The fixed "Hello" → "wormhole" mapping is part of the demonstration.
