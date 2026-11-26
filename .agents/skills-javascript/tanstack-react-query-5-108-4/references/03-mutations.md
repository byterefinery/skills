# Mutations

`useMutation` performs writes and server side-effects (create/update/delete):

```tsx
const mutation = useMutation({
  mutationFn: (newTodo) => axios.post('/todos', newTodo),
})

{mutation.isPending && <span>Adding todo...</span>}
{mutation.isError && <div>Error: {mutation.error.message}</div>}
{mutation.isSuccess && <div>Todo added!</div>}

<button onClick={() => mutation.mutate({ id: new Date(), title: 'Do Laundry' })}>
  Create Todo
</button>
```

## States

- `isIdle` / `status: 'idle'` — fresh or reset
- `isPending` / `status: 'pending'` — running
- `isError` / `status: 'error'` — `error` available
- `isSuccess` / `status: 'success'` — `data` available

Other useful result properties: `variables` (what was passed to `mutate`), `submittedAt` (timestamp). `mutate(variables, options?)` accepts one variable or object.

## mutate, mutateAsync, reset

- `mutate` — fire and forget (it is asynchronous, so in React 16 and earlier you cannot pass it directly to an event handler due to event pooling; wrap it in a function)
- `mutateAsync` — returns a promise that resolves on success or rejects on error; use it to compose side effects

```tsx
try {
  const todo = await mutation.mutateAsync(todo)
} catch (error) {
  console.error(error)
}
```

- `reset()` — clears `error` and `data`, returning the mutation to idle

## Per-call callbacks and consecutive mutations

You can pass `onSuccess` / `onError` / `onSettled` as the second argument to `mutate` for component-specific side effects (they do not run if the component unmounts first):

```tsx
mutate(todo, {
  onSuccess: (data, variables, onMutateResult, context) => { /* fires second */ },
})
```

With consecutive `mutate` calls, per-call callbacks fire **only once, for the last mutation** (the observer is resubscribed on each call), whereas `useMutation`-level handlers fire for every call. Fulfillment order may differ from call order when `mutationFn` is async.

## Lifecycle callbacks

```tsx
useMutation({
  mutationFn: addTodo,
  onMutate: (variables, context) => { /* about to run; may return a context value */ },
  onError: (error, variables, onMutateResult, context) => {},
  onSuccess: (data, variables, onMutateResult, context) => {},
  onSettled: (data, error, variables, onMutateResult, context) => {},
})
```

- Callbacks that return a promise are awaited before the next callback runs
- `onMutate` may return a value (the "onMutate result") passed to `onError` / `onSettled` — the standard rollback context
- Returning a promise from `onSuccess` keeps the mutation in `pending` until the promise resolves (useful: `onSettled: () => queryClient.invalidateQueries(...)` keeps `isPending` true until the refetch finishes)
- `context.client` is the `QueryClient`

## mutationKey and mutation scopes

- `mutationKey` — a key for the mutation, usable in filters (`useIsMutating`, `useMutationState`, `queryClient.isMutating`) to find mutations by identity
- `scope: { id }` — by default all mutations run **in parallel**, even repeated calls of the same mutation. Mutations sharing the same `scope.id` run **serially**: a new one starts `paused` while another in that scope is in flight, then resumes when its turn comes

## Retry and offline behavior

- Mutations do **not** retry by default; set `retry: 3` (or a function) to enable
- Mutations that fail because the device is offline are retried **in the same order** when the device reconnects

## Invalidating queries from mutations

The standard pattern — invalidate related reads when a write succeeds, so they refetch in the background:

```tsx
const queryClient = useQueryClient()

const mutation = useMutation({
  mutationFn: addTodo,
  onSuccess: async () => {
    // single query
    await queryClient.invalidateQueries({ queryKey: ['todos'] })
    // multiple queries
    await Promise.all([
      queryClient.invalidateQueries({ queryKey: ['todos'] }),
      queryClient.invalidateQueries({ queryKey: ['reminders'] }),
    ])
  },
})
```

Invalidation marks matching queries stale (overriding `staleTime`) and refetches the ones currently observed. Any callback (`onSuccess`, `onSettled`, ...) can do this.

## Updating the cache from the mutation response

When a mutation returns the updated object, write it straight into the cache with `setQueryData` instead of refetching:

```tsx
const useMutateTodo = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: editTodo,
    onSuccess: (data, variables) => {
      queryClient.setQueryData(['todo', { id: variables.id }], data)
    },
  })
}
```

Updates must be **immutable** — never mutate the object you read from the cache in place; return a new object:

```tsx
queryClient.setQueryData(['posts', { id }], (oldData) =>
  oldData ? { ...oldData, title: 'my new post title' } : oldData,
)
```

## Optimistic updates

Two approaches:

### Via the UI (simpler)

Render the in-flight `variables` directly while the mutation is pending, and invalidate on settle:

```tsx
const addTodoMutation = useMutation({
  mutationFn: (newTodo: string) => axios.post('/api/data', { text: newTodo }),
  onSettled: () => queryClient.invalidateQueries({ queryKey: ['todos'] }),
})

// in the list UI
{addTodoMutation.isPending && (
  <li style={{ opacity: 0.5 }}>{addTodoMutation.variables}</li>
)}
```

If the mutation and the query live in different components, read pending mutations with `useMutationState`:

```tsx
const variables = useMutationState<string>({
  filters: { mutationKey: ['addTodo'], status: 'pending' },
  select: (mutation) => mutation.state.variables,
})
```

`variables` is an array (several mutations can run concurrently); `mutation.state.submittedAt` gives a unique key per mutation.

### Via the cache (multiple consumers)

`onMutate` returns the rollback context; `onError` rolls back; `onSettled` refetches:

```tsx
const queryClient = useQueryClient()

useMutation({
  mutationFn: updateTodo,
  onMutate: async (newTodo, context) => {
    // 1. Cancel outgoing refetches so they don't overwrite the update
    await context.client.cancelQueries({ queryKey: ['todos'] })
    // 2. Snapshot the previous value
    const previousTodos = context.client.getQueryData(['todos'])
    // 3. Optimistically update
    context.client.setQueryData(['todos'], (old) => [...old, newTodo])
    // 4. Return the snapshot for rollback
    return { previousTodos }
  },
  onError: (err, newTodo, onMutateResult, context) => {
    context.client.setQueryData(['todos'], onMutateResult.previousTodos)
  },
  onSettled: () => context.client.invalidateQueries({ queryKey: ['todos'] }),
})
```

Rule of thumb: one consumer → update the UI from `variables` (no rollback to manage); many consumers → update the cache.

## Persisted / offline mutations

Mutations can be dehydrated and resumed later (e.g. after a page reload):

```tsx
const state = dehydrate(queryClient)   // include paused mutations
hydrate(queryClient, state)            // on startup
queryClient.resumePausedMutations()    // resume paused mutations
```

Technical limitation: only mutation **state** is persisted — functions are not serializable. If the component that triggered the mutation is not mounted after hydration, `resumePausedMutations` fails with `No mutationFn found`. Provide a default function so paused mutations can resume:

```tsx
queryClient.setMutationDefaults(['todos'], {
  mutationFn: ({ id, data }) => api.updateTodo(id, data),
})
```

The `@tanstack/react-query-persist-client` plugin (`PersistQueryClientProvider`) wires this up with storage persisters; call `resumePausedMutations` in its `onSuccess` after the initial restore (see 04 for persistence details).
