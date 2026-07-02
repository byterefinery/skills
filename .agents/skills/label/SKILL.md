---
name: label
description: Logical time marker. Use when you need a named point of reference in the conversation that other skills or messages can anchor to. Like a label in C/C++ — a place you can jump back to.
---

# label

## Overview

Creates a named marker at the current point in the conversation. Other skills, messages, or instructions can reference it by name to anchor context, restore state, or branch logic. Think of it as a C/C++ label — purely a reference point, no behavior attached.

## Usage

Set a label by naming it `label: checkpoint-alpha` or `label: 123-xyz-ABC`.

Labels are resolved in order — nearest matching label wins. They carry no data, only position.
