# Behaviors

## Overview

Behaviors define shared gameplay logic between templates or rooms. They are composable — a template can use multiple behaviors, and behaviors can be shared across many templates.

## Behavior Types

- **Template behaviors** — applied to templates, affect copies
- **Room behaviors** — applied to rooms, affect room-level logic

## Behavior Fields

Behaviors can define custom fields that appear in template/room settings:

- Movement behavior: velocity field, flying flag
- Health behavior: max health, damage source filters
- Projectile behavior: shoot delay, damage range, projectile template

Fields become properties accessible as `this.fieldName`.

## Enumerations in Behaviors

Use enumerations as field types for dropdown menus in template/room settings:

```js
// Field type set to an Enumeration asset
// Dropdown shows enumeration variants
// Value is the enumeration's key
```

## Dynamic Add/Remove

```js
// Add behavior at runtime
behaviors.add(target, 'BehaviorName');

// Remove behavior at runtime
behaviors.remove(target, 'BehaviorName');

// Check if behavior exists
behaviors.has(target, 'BehaviorName'); // boolean
```

`target` is a room or template.

### Example: Boss Phase Change

```js
// When boss switches phases
behaviors.remove(this, 'Phase1_Attack');
behaviors.add(this, 'Phase2_Attack');
```

## Static vs Dynamic Behaviors

- **Dynamic behaviors** — can be added/removed at runtime
- **Static behaviors** — marked with ❄️ in IDE; code is statically embedded; cannot be removed at runtime

### Workaround for Static Behaviors

Add properties and `if` statements to control behavior execution:

```js
// In behavior's OnStep
if (!this.phase2Active) {
    // Phase 1 logic
} else {
    // Phase 2 logic
}
```

## Events in Behaviors

Behaviors use the same event system as templates:

- OnCreate, OnStep, OnDraw, OnDestroy
- Events marked with ❄️ are static (embedded, not removable)

## Gotchas

- **`behaviors.add/remove` only works for dynamic behaviors** — static behaviors (❄️) cannot be removed.
- **Static behaviors have embedded code** — their event code is baked into the template/room at export time.
- **Behavior fields become copy properties** — accessible as `this.fieldName` in copy events.
- **Enumerations produce dropdowns** — use enumeration assets for predefined options in template settings.
- **`behaviors.has()` checks runtime state** — returns whether behavior is currently applied.
- **Multiple behaviors compose** — a template can have any number of behaviors; all their events fire.
- **Behavior events run after template events** — template's own OnStep fires first, then behavior OnStep.
- **Room behaviors affect room events** — OnCreate, OnStep, OnDraw, OnLeave at room level.
- **Behavior removal is runtime only** — cannot change behavior composition in ct.js IDE at runtime.
- **`target` must be a room or template** — not a copy. Behaviors are added to the template definition, not individual copies.
