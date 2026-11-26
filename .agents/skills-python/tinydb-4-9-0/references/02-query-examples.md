# TinyDB 4.9.0 — Query Examples

All examples from the official v4.9.0 documentation (`docs/getting-started.rst`, `docs/usage.rst`).

## Two ways to build queries

### Query object (ORM-style)

```python
from tinydb import Query

User = Query()
db.search(User.name == 'John')
db.search(User.birthday.year == 1990)
```

### `where()` shorthand

```python
from tinydb import where

db.search(where('field') == 'value')   # shorthand for Query()['field'] == 'value'
db.search(where('birthday').year == 1900)
db.search(where('birthday')['year'] == 1900)
```

### Dict access for non-identifier field names

```python
# User.country-code is invalid Python:
db.search(User['country-code'] == 'foo')
```

### Transform a field with `map` before comparison

```python
from unidecode import unidecode
db.search(User.name.map(unidecode) == 'Jose')  # matches 'José' etc.
db.search(User.age.map(lambda x: x + x) == 44)
```

`map()` can also transform the whole document and then access new keys:

```python
rekey = lambda x: {'y': x['a'], 'z': x['b']}
db.search(Query().map(rekey).z == 10)
```

## Basic comparisons

```python
# More possible comparisons: != < > <= >=
db.search(Fruit.type == 'peach')
db.search(Fruit.count > 5)
```

Comparisons support **literal values only** on the right-hand side. Field-to-field comparisons (`Query().a == Query().b`) are not supported — use a callable predicate:

```python
db.search(lambda doc: doc.get('a') == doc.get('b'))
```

## Existence, regex, custom tests

```python
import re

# Field exists
db.search(User.name.exists())

# Regex — the whole field must match; flags supported
db.search(User.name.matches('[aZ]*'))
db.search(User.name.matches('John', flags=re.IGNORECASE))

# Regex — any part of the field matches
db.search(User.name.search('b+'))

# Custom test
db.search(User.name.test(lambda s: s == 'John'))

# Custom test with parameters
def test_func(val, m, n):
    return m <= val <= n

db.search(User.age.test(test_func, 0, 21))
db.search(User.age.test(test_func, 21, 99))
```

## Fragment queries

Find documents that contain a given dict of fields:

```python
# Whole-document fragment
db.search(Query().fragment({'foo': True, 'bar': False}))

# Fragment under a specific field
db.search(Query().field.fragment({'foo': True, 'bar': False}))
```

## Lists — `any`, `all`, `one_of`

Setup:

```python
db.insert({'name': 'user1', 'groups': ['user']})
db.insert({'name': 'user2', 'groups': ['admin', 'user']})
db.insert({'name': 'user3', 'groups': ['sudo', 'user']})
```

### Value lists

```python
# At least one value from the list present
db.search(User.groups.any(['admin', 'sudo']))
# -> user2, user3

# All values from the list present
db.search(User.groups.all(['admin', 'user']))
# -> user2
```

### Nested queries (field holds a list of dicts)

Setup:

```python
Group = Query()
Permission = Query()
groups = db.table('groups')
groups.insert({'name': 'user',  'permissions': [{'type': 'read'}]})
groups.insert({'name': 'sudo',  'permissions': [{'type': 'read'}, {'type': 'sudo'}]})
groups.insert({'name': 'admin', 'permissions': [{'type': 'read'}, {'type': 'write'}, {'type': 'sudo'}]})
```

```python
# Group has a permission with type 'read' (any)
groups.search(Group.permissions.any(Permission.type == 'read'))
# -> user, sudo, admin

# Group has ONLY permission 'read' (all)
groups.search(Group.permissions.all(Permission.type == 'read'))
# -> user
```

`any` = at least one element matches; `all` = every element matches.

### Field value contained in a list

```python
db.search(User.name.one_of(['jane', 'john']))
```

## Combining queries

```python
# NOT — operand must be parenthesized
db.search(~(User.name == 'John'))

# AND
db.search((User.name == 'John') & (User.age <= 30))

# OR
db.search((User.name == 'John') | (User.name == 'Bob'))
```

Python's `&`/`|`/`~` have higher precedence than comparison operators — `~User.name == 'John'` parses as `(~User.name) == 'John'`. Always parenthesize each operand.

### Dynamic query composition

Use the no-op query as a starting point:

```python
base = Query().noop()
if name:
    base = base & (User.name == name)
if age:
    base = base & (User.age >= age)
db.search(base)
```

## Callable predicates

Any callable `doc -> bool` works as a query — useful for field-to-field logic:

```python
db.search(lambda doc: doc.get('a') == doc.get('b'))
```

Mark a predicate non-cacheable to skip the query cache:

```python
def my_query(doc):
    return doc.get('foo') == 'bar'

my_query.is_cacheable = lambda: False
db.search(my_query)
```

Callables passed to query APIs execute in-process and must never be derived from untrusted or user-controlled input.

## Recap table

| Query | Meaning |
|---|---|
| `Query().field.exists()` | Field exists |
| `Query().field.matches(regex)` | Whole field matches regex |
| `Query().field.search(regex)` | Substring of field matches regex |
| `Query().field.test(func, *args)` | `func(value, *args)` is `True` |
| `Query().field.any(query \| list)` | At least one element matches |
| `Query().field.all(query \| list)` | All elements match |
| `Query().field.one_of(list)` | Field value in list |
| `Query().fragment(document)` | Document contains fields |
| `Query().field.map(fn)` | Transform field/document, then compare |
| `Query().noop()` | Always-True, for composition |
| `~(query)` | NOT |
| `(q1) & (q2)` | AND |
| `(q1) \| (q2)` | OR |
