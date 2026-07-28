# Selectors

Cytoscape.js uses CSS-like selectors for querying elements. Selectors work on collections and can be used wherever a filter is accepted.

## Group Selectors

```
node        — matches all nodes
edge        — matches all edges
*           — matches all elements
```

## ID and Class

```
#id         — matches element by ID (e.g. #foo)
.className  — matches elements with class (e.g. .highlight)
```

## Data Attribute Selectors

### Existence

```
[name]      — data attribute is defined (not undefined; null counts as defined)
[^name]     — data attribute is undefined
[?name]     — data attribute is truthy
[!name]     — data attribute is falsey
```

### Comparison

```
[name = value]    — equals
[name != value]   — not equals
[name > value]    — greater than
[name >= value]   — greater or equal
[name < value]    — less than
[name <= value]   — less or equal
[name *= value]   — contains substring
[name ^= value]   — starts with
[name $= value]   — ends with
```

Strings must be quoted:

```
[name = "Jerry"]   — correct
[name = Jerry]     — wrong (treated as identifier)
```

### Operators

```
@   — case insensitive (e.g. [name @$= "ry"])
!   — negate (e.g. [name !$= "ry"])
```

### Nested Access

```
[name.0 = value]       — array element at index
[name.property = val]  — nested object property
```

### Metadata Brackets

```
[[degree > 2]]       — matches by degree
[[indegree > 1]]     — matches by in-degree
[[outdegree > 1]]    — matches by out-degree
```

## Compound Node Selectors

```
parent > child    — direct children (child selector)
parent child      — all descendants (descendant selector, space-separated)
$parent > child   — selects parent nodes instead of children (subject selector)
```

## State Pseudo-Classes

### Animation

```
:animated     — currently being animated
:unanimated   — not being animated
```

### Selection

```
:selected      — selected
:unselected    — not selected
:selectable    — selection state is mutable
:unselectable  — selection state is immutable
```

### Locking

```
:locked        — position is immutable
:unlocked      — position can change
```

### Visibility

```
:visible       — displayed and visible
:hidden        — display:none or visibility:hidden
:transparent   — opacity:0 (self or ancestors)
```

### Background Images

```
:backgrounding    — background image is loading
:nonbackgrounding — no image or image loaded
```

### User Interaction

```
:grabbed      — currently grabbed by user
:free         — not grabbed
:grabbable    — can be grabbed
:ungrabbable  — cannot be grabbed
:active       — user interaction (hover/drag)
:inactive     — no user interaction
:touch        — displayed in touch environment
```

### Graph Membership

```
:removed   — removed from graph
:inside    — present in graph
```

### Compound State

```
:parent      — has children
:childless   — no children
:child       — has a parent (alias: :nonorphan)
:orphan      — no parent
:compound    — alias for :parent; also matches edges connected to parents
```

### Edge Types

```
:loop    — source and target are the same node
:simple  — source and target are different
```

## Combining Selectors

### Comma (OR)

```
node#j, edge[source = "j"]
```

### Adjacent (AND)

```
node[weight >= 50][height < 180]
```

### Examples

```js
cy.$('node');                           // all nodes
cy.$('node#foo');                       // node with id 'foo'
cy.$('.active');                        // elements with class 'active'
cy.$('[weight > 50]');                  // high-weight elements
cy.$('[name = "Alice"]');               // string match
cy.$('[labels.0 = "Person"]');          // array element
cy.$('[name.first = "John"]');          // nested object
cy.$(':selected');                      // selected elements
cy.$(':visible');                       // visible elements
cy.$('node > node');                   // direct children
cy.$('node node');                     // all descendants
cy.$('$node > node');                  // parent nodes
cy.$('#a, #b, #c');                    // multiple IDs
cy.$('node[weight > 50]:visible');     // combined conditions
cy.$('[[degree > 2]]');                // metadata
```

## Escaping

Special characters in IDs and field names need escaping:

```js
cy.$('#some\\$funky\\@id');   // escape $ and @
cy.$('[id = "some$funky@id"]'); // alternative: use data selector
```

Characters to escape: `( ^ $ \ / ( ) | ? + * [ ] { } , . )`

## Filter Functions

Anywhere a selector string is accepted, a filter function can be used:

```js
cy.elements().filter(ele => ele.data('weight') > 50);
cy.$('#j').neighborhood(ele => ele.isEdge());
```

## Performance Notes

- ID selectors (`#id`) are O(1) — use them when you know the ID
- Data attribute selectors scan all elements — consider caching results
- State pseudo-classes are fast (check internal flags)
- Nested/compound selectors traverse the hierarchy
- For repeated queries, cache the resulting collection rather than re-querying
