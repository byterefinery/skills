# Content Subsystem

## Overview

The content subsystem is a local database for structured game data. Define content types with schemas, create entries in ct.js IDE, and access data at runtime via `content.TypeName`.

## Content Types

Created in ct.js IDE: **Project → Content type editor**.

### Schema Fields

| Property | Description |
|---|---|
| Name | Property name used in code (e.g., `content.Quests`) |
| Readable name | Display name in IDE |
| Icon | Display icon in IDE |
| Schema | List of fields with types |

### Field Types

- `string` — text values
- `number` — numeric values
- `boolean` — true/false
- `template` — reference to a template (becomes template name string)
- `room` — reference to a room (becomes room name string)
- `texture` — reference to a texture (becomes texture name string)
- `sound` — reference to a sound
- `tandem` — reference to an emitter tandem
- Enumeration types — dropdown in IDE, value is enumeration key

### Field Options

- **Required** — must be filled in IDE
- **Array** — allows multiple values (list editor)

## Using Content Data

```js
// Access content type
content.Quests; // Array of quest entries

// Access specific entry
content.Quests[0].title;

// Search by field
var quest = content.Quests.find((q) => q.name === 'Main Quest');

// Filter by range
var items = content.loot.filter((item) => item.level >= 5 && item.level <= 10);
```

## Content Structure

Content types export as arrays of objects:

```js
content.loot = [
    { name: 'Sword', level: 3, damage: 15, template: 'Sword' },
    { name: 'Shield', level: 5, damage: 0, template: 'Shield' },
    // ...
];
```

Asset references become strings (the asset name):

```js
// If a field references template "Hero"
content.Quests[0].rewardTemplate; // "Hero"
```

## Gotchas

- **Asset references become strings** — template/room/texture fields store the asset name, not the object.
- **Content is read-only at runtime** — data is exported from ct.js IDE; cannot be modified in-game.
- **Arrays of fields** — enable "Array" checkbox for multi-value fields.
- **Enumeration values are keys** — not display names. Use the enumeration's key values in code.
- **`content.TypeName` is an array** — always iterate or index into it.
- **Schema changes are irreversible** — removing fields from a content schema is permanent.
- **Content types must be defined in IDE** — cannot create content types programmatically.
- **`content` namespace is flat** — all content types are direct properties: `content.Quests`, `content.Items`.
