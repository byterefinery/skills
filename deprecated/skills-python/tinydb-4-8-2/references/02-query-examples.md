# TinyDB 4.8.2 — Query Examples

## Basic Queries

### Equality

```python
from tinydb import TinyDB, Query

db = TinyDB('data.json')
Item = Query()

# Exact match
db.search(Item.name == 'Widget')
db.search(Item.price == 9.99)
db.search(Item.active == True)
db.search(Item.tags == ['sale', 'new'])
```

### Inequality and Ordering

```python
# Not equal
db.search(Item.price != 0)

# Ordering
db.search(Item.price > 10)
db.search(Item.price >= 10)
db.search(Item.price < 100)
db.search(Item.price <= 100)
```

### Field Existence

```python
# Field exists (any value, including None/False/empty)
db.search(Item.email.exists())

# Field does not exist
db.search(~Item.email.exists())
```

## Combining Queries

### AND

```python
# Both conditions must be true
db.search((Item.price > 10) & (Item.active == True))

# Chain multiple ANDs
db.search(
    (Item.category == 'electronics') &
    (Item.price < 500) &
    (Item.in_stock.exists())
)
```

### OR

```python
# Either condition can be true
db.search((Item.name == 'Widget') | (Item.name == 'Gadget'))

# Mix with AND — use parentheses
db.search(
    (Item.category == 'electronics') &
    ((Item.price < 100) | (Item.brand == 'Acme'))
)
```

### NOT

```python
# Negate a single condition
db.search(~(Item.status == 'deleted'))

# Negate a combined query (De Morgan)
db.search(~((Item.price > 100) & (Item.active == True)))
# Equivalent to:
db.search((Item.price <= 100) | (Item.active == False))
```

## Regex Queries

### matches() — Whole String Match

Uses `re.match()` — the pattern must match from the start of the string.

```python
# Name starts with 'A'
db.search(Item.name.matches(r'^A'))

# Email pattern
db.search(Item.email.matches(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'))

# Exact alphanumeric match
db.search(Item.code.matches(r'^\w+$'))

# With flags
import re
db.search(Item.name.matches(r'^hello', flags=re.IGNORECASE))
```

### search() — Substring Match

Uses `re.search()` — the pattern can match anywhere in the string.

```python
# Contains 'error' anywhere in the message
db.search(Item.message.search(r'error'))

# Ends with '.jpg'
db.search(Item.filename.search(r'\.jpg$'))

# Contains a digit
db.search(Item.code.search(r'\d'))
```

## Custom Test Functions

```python
# Simple test
db.search(Item.age.test(lambda x: x % 2 == 0))

# Test with additional arguments
def in_range(value, low, high):
    return low <= value <= high

db.search(Item.score.test(in_range, 50, 100))

# Complex validation
def is_valid_email(email):
    import re
    return bool(re.match(r'^[\w.+-]+@[\w-]+\.\w+$', email))

db.search(Item.email.test(is_valid_email))
```

**Warning**: Test functions must be deterministic. Non-deterministic functions (e.g., involving time, random, network calls) break the query cache.

## Collection Queries

### any() — At Least One Element Matches

```python
# Any element equals a value
db.search(Item.tags.any(['sale', 'clearance']))

# Any nested document matches a sub-query
db.search(Item.orders.any(Query().total > 100))

# Matches documents like:
# {'tags': ['new', 'sale']}  — 'sale' is in ['sale', 'clearance']
# {'orders': [{'total': 50}, {'total': 150}]}  — one order > 100
```

### all() — All Elements Match

```python
# All elements are in a value list
db.search(Item.tags.all(['sale']))

# All nested documents match a sub-query
db.search(Item.orders.all(Query().total > 0))

# Matches documents like:
# {'tags': ['sale', 'sale']}  — all tags are in ['sale']
# {'orders': [{'total': 50}, {'total': 100}]}  — all totals > 0
```

### one_of() — Field Value Is In A List

```python
# Field value is one of these
db.search(Item.status.one_of(['active', 'pending', 'review']))
db.search(Item.priority.one_of([1, 2, 3]))

# Equivalent to OR of equalities
db.search(
    (Item.status == 'active') |
    (Item.status == 'pending') |
    (Item.status == 'review')
)
```

## Nested Field Queries

```python
# Dot notation for nested access
db.search(Item.address.city == 'London')
db.search(Item.address.postal.code == 'SW1A')

# Bracket notation for keys with special characters
db.search(Item['log-in'] == True)
db.search(Item['data-count'] > 10)

# Mixed notation
db.search(Item.address['zip-code'] == 'SW1A 1AA')
```

Nested queries return `False` (not an error) when intermediate fields are missing or not dicts.

## Map — Transform Before Comparison

```python
# Double the value before comparing
db.search(Item.age.map(lambda x: x * 2) == 60)

# Uppercase before comparing
db.search(Item.name.map(str.upper) == 'ALICE')

# Length check
db.search(Item.tags.map(len) > 3)

# Math operations
db.search(Item.price.map(lambda x: round(x, 1)) == 9.9)
```

### Map — Transform Entire Document

`map()` can also transform the whole document, remapping keys:

```python
# Remap document keys
def rekey(doc):
    return {'y': doc['a'], 'z': doc['b']}

db.search(Query().map(rekey).z == 10)
# Matches: {'a': 5, 'b': 10}
```

**Note**: Queries using `map()` are not cacheable because callables can be mutable.

## Fragment — Match Multiple Fields

```python
# Match multiple fields at once (no path needed)
db.search(Query().fragment({'name': 'Alice', 'age': 30}))

# Partial match — only specified fields must match
db.search(Query().fragment({'status': 'active'}))
# Matches any document with status == 'active', regardless of other fields

# Fragment on nested fields (with path)
db.search(Query().doc.fragment({'a': 4, 'b': True}))
# Matches: {'doc': {'a': 4, 'b': True, 'c': 'yes'}}
```

## No-op — Dynamic Query Building

```python
# Start with a query that always matches
query = Query().noop()

# Conditionally add constraints
if name:
    query = query & (Item.name == name)
if min_price:
    query = query & (Item.price >= min_price)
if categories:
    query = query & Item.category.one_of(categories)

# Execute the composed query
results = db.search(query)
```

## Query Caching Behavior

```python
# Same query returns cached result
db.search(Item.name == 'Alice')  # computes, caches
db.search(Item.name == 'Alice')  # returns cached result

# Different query computes fresh
db.search(Item.name == 'Bob')  # computes, caches

# Write operation clears entire cache
db.insert({'name': 'Charlie'})  # cache cleared

# Non-cacheable queries always compute
db.search(Item.name.map(str.upper) == 'ALICE')  # not cached
db.search(Item.name.test(lambda x: len(x) > 3))  # not cached if function is unhashable

# Custom non-cacheable query
def live_check(doc):
    return some_remote_call(doc['id'])

# Mark as non-cacheable by not implementing __hash__ stably
```

## Lambda Queries

Any callable that accepts a document dict and returns bool works as a query:

```python
def my_query(doc):
    return doc.get('foo') == 'bar'

# Mark as non-cacheable (required for non-Query callables)
my_query.is_cacheable = lambda: False

db.search(my_query)  # works, never cached
```

Without `is_cacheable`, TinyDB assumes the query is cacheable and requires a stable `__hash__`. Lambda functions don't have a stable hash, so always set `is_cacheable` to return `False`.

## Custom Query Subclasses

Extend `Query` to add custom test methods:

```python
from tinydb import Query

class MyQuery(Query):
    def equal_double(self, rhs):
        return self._generate_test(
            lambda value: value == rhs * 2,
            ('equal_double', self._path, rhs)
        )

# Usage
Custom = MyQuery()
db.search(Custom.val.equal_double('42'))
# Matches: {'val': '4242'}
```

## Edge Cases

### Empty String and Zero

```python
# Empty string is a valid value
db.search(Item.name == '')

# Zero is falsy but distinct from missing
db.search(Item.count == 0)
# Does NOT match documents missing the 'count' field
```

### None Values

```python
# None equality
db.search(Item.optional == None)

# None in one_of
db.search(Item.status.one_of([None, 'pending', 'active']))
```

### Boolean Fields

```python
# Explicit True/False
db.search(Item.active == True)
db.search(Item.active == False)

# Avoid implicit truthiness
# This matches any truthy value, not just True:
# db.search(Item.active)  # WRONG — evaluates the Query object, not a comparison
```

### List and Dict Values

```python
# Exact list match (order matters)
db.search(Item.tags == ['a', 'b', 'c'])

# Exact dict match
db.search(Item.metadata == {'key': 'value'})

# For partial list/dict matching, use fragment or any/all
db.search(Query().fragment({'tags': ['a']}))  # matches if top-level has tags == ['a']
```

### Type Sensitivity

```python
# String vs integer — different types
db.search(Item.id == 1)       # matches int 1
db.search(Item.id == '1')     # matches string '1'

# Float vs int
db.search(Item.value == 1.0)  # matches 1.0, also 1 (Python equality)
```

### Custom Mapping Types

Any `collections.abc.Mapping` can be inserted, not just dicts:

```python
from collections.abc import Mapping

class CustomDoc(Mapping):
    def __init__(self, data):
        self.data = data
    def __getitem__(self, key):
        return self.data[key]
    def __iter__(self):
        return iter(self.data)
    def __len__(self):
        return len(self.data)

db.insert(CustomDoc({'int': 1, 'char': 'a'}))
# Accepted — converted to dict internally
```

### insert_multiple Gotchas

```python
# WRONG — single dict iterates over keys, not values
db.insert_multiple({'first': 'John', 'last': 'smith'})  # ValueError!

# RIGHT — wrap in a list
db.insert_multiple([{'first': 'John', 'last': 'smith'}])

# RIGHT — use a generator
db.insert_multiple({'int': i} for i in range(10))
```
