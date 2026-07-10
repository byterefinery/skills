# Collision and Contact

## Collision Detection

phy-engine supports two collision detection modes:

1. **Collision groups** — filter which bodies collide with each other using engine-specific flags/masks
2. **Contact pairs** — explicit monitoring of contact between two specific bodies

## Active Contact

Contact events require `phy.activeContact()` to be called first:

```js
phy.activeContact();
```

This enables contact data flow from the physics backend. Call it after `phy.set()` and before adding contact pairs.

## Contact Pairs

Monitor contact between two specific bodies:

```js
phy.add({
    type: 'contact',
    name: 'myContact',
    b1: 'bodyA',           // first body
    b2: 'bodyB',           // second body (or null for all contacts with b1)
    always: true,          // call callback even when not in contact
    callback: onContact,   // contact callback
});
```

### Contact Data

```js
function onContact(data) {
    if (data.hit) {
        console.log(`Contact at ${data.point}`);
        console.log(`Normal: ${data.normal}`);
    }
}

// data shape:
// {
//     hit: false,
//     point: [0, 0, 0],
//     normal: [0, 0, 0],
// }
```

### Multiple Contacts

When a body has multiple contacts per frame, the reflow system batches them:

```js
// Access batched contacts via reflow
const contacts = phy.reflow.contact['bodyName'];
// contacts is an array of contact data objects
```

## Collision Callbacks on Bodies

Attach a collision callback directly to a body:

```js
phy.addCollision({
    name: 'player',
    vs: ['enemy', 'hazard'],    // bodies to check against
    ignore: ['friend'],          // bodies to ignore
    callback: (contactData) => {
        // handle collision
    },
});
```

Or use event dispatch:

```js
const body = phy.byName('player');
body.addEventListener('collision', (event) => {
    console.log('Hit:', event.data);
});
```

## Collision Filtering

### Universal (All Engines)

```js
// Disable all collisions for a body
phy.add({ type: 'box', size: [1, 1, 1], collision: false });
```

### PhysX

```js
// Collision flags (bitmask)
phy.add({ type: 'box', size: [1, 1, 1], flags: 0 });  // no collision
```

### Oimo

```js
// Collision mask
phy.add({ type: 'box', size: [1, 1, 1], mask: 0 });  // no collision
```

### Havok

```js
// Collision mask
phy.add({ type: 'box', size: [1, 1, 1], mask: 32 }); // no collision
```

## Removing Collision Monitoring

```js
phy.removeCollision('player');
```

## Engine Support

| Feature | PhysX | Havok | Oimo | Jolt | Ammo | Rapier |
|---------|-------|-------|------|------|------|--------|
| Contact pairs | ✓ | ✓ | ✓ | — | — | — |
| Collision callback | ✓ | ✓ | ✓ | — | — | — |
| Collision filtering | flags | mask | mask | — | — | — |

Contact pairs and collision callbacks are only available on PhysX, Havok, and Oimo.

## Gotchas

- **Call `activeContact()` before adding contacts** — otherwise contact data won't flow.
- **Contact callbacks fire every frame** — check `data.hit` to distinguish contact vs no-contact.
- **`always: true`** — callback fires even when bodies are not touching (useful for continuous monitoring).
- **`vs` can be a single name or array** — `vs: 'enemy'` or `vs: ['enemy', 'hazard']`.
- **`ignore` can be a single name or array** — `ignore: 'friend'` or `ignore: ['friend', 'ally']`.
- **`removeCollision()`** removes the monitoring but doesn't affect physical collision behavior.
