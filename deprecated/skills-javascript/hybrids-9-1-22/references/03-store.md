# Store

## Table of Contents

- [Model Definitions](#model-definitions)
- [Store Factory](#store-factory)
- [Storage Configuration](#storage-configuration)
- [Store Actions](#store-actions)
- [State Guards](#state-guards)
- [Drafts](#drafts)
- [Validation](#validation)
- [Relations](#relations)
- [Offline Caching](#offline-caching)
- [Observation](#observation)
- [Singleton Models](#singleton-models)
- [Enumerable Models](#enumerable-models)
- [List Models](#list-models)
- [Nested Models](#nested-models)
- [Record Models](#record-models)

---

## Model Definitions

Models are plain objects that describe the shape of data entities:

```js
import { store } from "hybrids";

const User = {
  id: true,               // enumerable — has unique identifiers
  firstName: "",
  lastName: "",
  email: "",
  age: 0,
  active: false,
};
```

### Property Types

| Type | Behavior |
|---|---|
| `string` (`""`) | Default empty string, coerced via `String()` |
| `number` (`0`) | Default 0, coerced via `Number()` |
| `boolean` (`false`) | Default false, coerced via `Boolean()` |
| `object` | Nested model or plain object |
| `array` | Array of primitives or nested models |
| `function` | Computed property, receives model instance |

### Computed Properties

```js
const User = {
  id: true,
  firstName: "",
  lastName: "",
  fullName: (model) => `${model.firstName} ${model.lastName}`,
};
```

---

## Store Factory

The `store()` function creates a component property descriptor that connects a model to a component:

```js
import { define, store, html } from "hybrids";

const UserDetail = define({
  tag: "user-detail",
  user: store(User),                    // enumerable model
  users: store([User]),                 // list of models
  config: store(AppConfig),             // singleton model
  render: ({ user, users, config }) => html`...`,
});
```

### Options

```js
// With id from host property
user: store(User, { id: "userId" }),

// With id from function
user: store(User, { id: (host) => host.params.id }),

// Draft mode
user: store(User, { draft: true }),
```

---

## Storage Configuration

Connect models to external data sources using `store.connect` (a Symbol):

```js
const User = {
  id: true,
  name: "",
  email: "",
  [store.connect]: {
    get: (id) => fetch(`/api/users/${id}`).then(r => r.json()),
    set: (id, values) => fetch(`/api/users/${id}`, {
      method: "PUT",
      body: JSON.stringify(values),
    }).then(r => r.json()),
    list: () => fetch("/api/users").then(r => r.json()),
  },
};
```

### Storage Methods

| Method | Required | Description |
|---|---|---|
| `get(id)` | Yes (unless `loose`) | Fetch a single entity by id. Returns `T \| null \| Promise<T \| null>` |
| `set(id, values, keys)` | No | Save entity. Returns `T \| null \| Promise<T \| null>` |
| `list(id)` | No | Fetch a list of entities. Returns `T[] \| Promise<T[]>` |
| `observe(id, model, lastModel)` | No | Called after each storage operation |

### Storage Options

| Option | Default | Description |
|---|---|---|
| `cache` | `true` | Caching strategy: `true` (until invalidated), `false`/`0` (no cache), `number` (ms TTL) |
| `offline` | `false` | Offline caching via localStorage: `true` (30 days), `number` (ms threshold) |
| `loose` | `false` | If true, `get` can return `null` without errors; model is optional |

### Memory Storage (Default)

Without `[store.connect]`, models use in-memory storage:

```js
const Settings = {
  theme: "light",
  language: "en",
  // No storage — values are managed in memory
};
```

---

## Store Actions

### store.get()

Fetch a model instance:

```js
import { store } from "hybrids";

// Enumerable model — requires id
const user = store.get(User, "123");

// Singleton — no id
const settings = store.get(Settings);

// List — optional id for grouping
const users = store.get([User]);
const activeUsers = store.get([User], "active");
```

### store.set()

Save values to storage:

```js
// Update existing
store.set(user, { name: "New Name" });

// Create new (enumerable)
store.set(User, { name: "New User", email: "new@example.com" });

// Delete
store.set(user, null);
```

Returns a `Promise<M>`.

### store.sync()

Synchronously update a model (no storage call):

```js
const updated = store.sync(user, { name: "New Name" });
// Returns the model immediately, no Promise
```

### store.clear()

Invalidate cached data:

```js
// Clear single instance
store.clear(user);

// Clear all instances of a model
store.clear(User);
store.clear([User]);

// Clear without deleting cache entries
store.clear(user, false);
```

---

## State Guards

Every model instance has an internal state machine: `pending` → `ready` or `error`.

### store.pending()

Returns the pending Promise or `false` if ready:

```js
// Single model
const promise = store.pending(user);
if (promise) {
  promise.then((resolvedUser) => /* use resolvedUser */);
}

// Multiple models
const promise = store.pending(user, settings);
if (promise) {
  promise.then(([resolvedUser, resolvedSettings]) => /* ... */);
}
```

In templates:

```js
html`
  ${store.pending(user) && html`<span>Loading...</span>`}
  ${!store.pending(user) && html`<span>${user.name}</span>`}
`
```

### store.error()

Check for errors:

```js
// Any error
if (store.error(user)) { /* handle error */ }

// Specific validation error
const nameError = store.error(user, "name");
```

### store.ready()

Check if model(s) are fully loaded:

```js
// Single
if (store.ready(user)) { /* safe to access properties */ }

// Multiple
if (store.ready(user, settings, config)) { /* all loaded */ }
```

In templates:

```js
html`
  ${store.pending(user) && `Loading...`}
  ${store.error(user) && `Error: ${store.error(user).message}`}
  ${store.ready(user) && html`<p>${user.firstName} ${user.lastName}</p>`}
`
```

### Important

Accessing properties of a model in `pending` or `error` state throws. Always guard:

```js
// BAD — throws if pending
html`<p>${user.name}</p>`

// GOOD
html`
  ${store.ready(user) && html`<p>${user.name}</p>`}
`
```

---

## Drafts

Draft mode enables optimistic UI updates with automatic rollback on failure:

```js
const UserEditor = define({
  tag: "user-editor",
  user: store(User, { draft: true, id: "userId" }),

  save: async (host) => {
    await store.submit(host.user, { name: host.user.name });
  },

  render: ({ user, save }) => html`
    <input value="${user.name}" oninput="${html.set('user', 'name')}"/>
    ${store.pending(user) && `Saving...`}
    ${store.error(user) && `Error!`}
    <button onclick="${save}">Save</button>
  `,
});
```

### How Drafts Work

1. The draft starts as a copy of the current model data
2. Changes are applied locally (optimistic update)
3. `store.submit(draft, values)` sends changes to storage
4. On success: draft syncs with the saved data
5. On failure: error state is set, draft retains local changes

### store.submit()

```js
// Submit current draft values
store.submit(draft);

// Submit with additional values
store.submit(draft, { extraField: "value" });
```

Returns a `Promise<M>` that resolves on success or rejects on failure.

---

## Validation

Add validation to model properties using `store.value()`:

```js
const User = {
  id: true,
  email: store.value("", /^[^\s@]+@[^\s@]+\.[^\s@]+$/, "Invalid email"),
  age: store.value(0, (v) => v >= 0 || "Age must be positive"),
  name: store.value("", (v) => v.length >= 2 || "Too short"),
};
```

### Validation Function

```js
store.value(defaultValue, validate, errorMessage);
```

- `validate` can be a `RegExp` or a function `(value, key, model) => true | undefined | string | Error`
- Returning `true` or `undefined` means valid
- Returning a string or throwing sets the error message
- `store.required` is a built-in validator: `!!value || "${key} is required"`

### Checking Errors

```js
// Any error
store.error(model);

// Specific field error
store.error(model, "email");

// All validation errors (null key)
const hasValidationErrors = store.error(model, null);
```

---

## Relations

### Nested Objects (Non-enumerable)

Plain object properties create nested models:

```js
const Address = {
  street: "",
  city: "",
  zip: "",
};

const User = {
  id: true,
  name: "",
  address: Address,  // nested object
};

const user = store.get(User, "1");
console.log(user.address.city);  // nested access
```

### Nested Enumerable Models

Reference other enumerable models:

```js
const Post = {
  id: true,
  title: "",
  author: Author,  // reference to another enumerable model
};

const post = store.get(Post, "1");
const author = post.author;  // auto-resolved Author instance
```

### Array of Primitives

```js
const Tagged = {
  id: true,
  tags: [],           // default array
  roles: [String],    // coerced to strings
  scores: [Number],   // coerced to numbers
  flags: [Boolean],   // coerced to booleans
};
```

### Array of Enumerable Models

```js
const User = {
  id: true,
  name: "",
  posts: [Post],                  // array of Post models
  recentPosts: [Post, { loose: true }],  // loose: items can be missing
};
```

---

## Offline Caching

Enable offline persistence via localStorage:

```js
const User = {
  id: true,
  name: "",
  [store.connect]: {
    get: (id) => fetch(`/api/users/${id}`).then(r => r.json()),
    offline: true,               // 30 days default
    // offline: 1000 * 60 * 60,  // 1 hour
  },
};
```

- Data is stored in localStorage under a hashed key
- On load, offline data is returned immediately while fresh data fetches
- Stale entries are automatically cleaned up based on the threshold
- Nested models with offline caching inherit the parent's offline behavior

---

## Observation

Watch for model changes globally:

```js
import { store } from "hybrids";

const unsubscribe = store.observe(User, (id, model, lastModel) => {
  console.log(`User ${id} changed`, model, lastModel);
});

// Later:
unsubscribe();
```

Also available as a storage option:

```js
[store.connect]: {
  get: (id) => fetch(...),
  observe: (id, model, lastModel) => { /* ... */ },
}
```

---

## Singleton Models

Models without `id: true` are singletons (one instance):

```js
const AppConfig = {
  theme: "light",
  language: "en",
  [store.connect]: {
    get: () => fetch("/api/config").then(r => r.json()),
    set: (id, values) => fetch("/api/config", {
      method: "PUT",
      body: JSON.stringify(values),
    }).then(r => r.json()),
  },
};

// Usage
const config = store.get(AppConfig);  // no id needed
```

---

## Enumerable Models

Models with `id: true` support multiple instances:

```js
const User = {
  id: true,
  name: "",
};

const user1 = store.get(User, "1");
const user2 = store.get(User, "2");
```

- IDs are strings (auto-generated UUIDs for new entities without explicit id)
- `toString()` returns the id
- Models are frozen (immutable)

---

## List Models

Arrays of enumerable models:

```js
const UserList = define({
  tag: "user-list",
  users: store([User]),              // all users
  activeUsers: store([User], { id: "active" }),  // grouped list
  render: ({ users }) => html`
    <ul>
      ${store.ready(users) && users.map(user => html`<li>${user.name}</li>`)}
    </ul>
  `,
});
```

The storage must support `list()`:

```js
[store.connect]: {
  list: () => fetch("/api/users").then(r => r.json()),
}
```

---

## Record Models

Index models by a property value using `store.record()`:

```js
const User = {
  id: true,
  slug: "",
  profile: store.record({
    bio: "",
    avatar: "",
  }),
};
```

This creates a map-like structure where `user.profile[slug]` gives access to the nested record.

---

## store.ref()

Lazy initialization for default values:

```js
const Model = {
  id: true,
  items: store.ref(() => [1, 2, 3]),  // called once per instance
};
```
