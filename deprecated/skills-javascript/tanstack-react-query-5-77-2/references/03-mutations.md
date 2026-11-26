# Mutations

## Contents

- [useMutation](#usemutation)
- [Mutation states](#mutation-states)
- [mutate and mutateAsync](#mutate-and-mutateasync)
- [Resetting mutation state](#resetting-mutation-state)
- [Lifecycle callbacks](#lifecycle-callbacks)
- [Invalidation from mutations](#invalidation-from-mutations)
- [Updates from mutation responses](#updates-from-mutation-responses)
- [Optimistic updates](#optimistic-updates)
- [Global mutation hooks](#global-mutation-hooks)

## useMutation

```tsx
const mutation = useMutation({
  mutationFn,        // (variables) => Promise<TData>
  mutationKey,       // for filtering/defaults
  retry, retryDelay, networkMode, gcTime, meta, scope, throwOnError,
  onMutate, onError, onSuccess, onSettled,
}, queryClient?)
```

Mutations are for creating/updating/deleting data or other server side-effects. Unlike queries they are **not cached across components** and run only when `mutate` is called.

## Mutation states

- `isIdle` / `status === 'idle'` — fresh or reset
- `isPending` / `status === 'pending'` — running
- `isError` / `status === 'error'` — `error` is available
- `isSuccess` / `status === 'success'` — `data` is available

Result fields also include `data`, `error`, `failureCount`, `failureReason`, `isPaused`, `variables`, `submittedAt`, `mutate`, `mutateAsync`, `reset`.

```tsx
const mutation = useMutation({ mutationFn: (newTodo) => axios.post('/todos', newTodo) })

<button disabled={mutation.isPending} onClick={() => mutation.mutate({ title: 'Do laundry' })}>
  {mutation.isPending ? 'Adding...' : 'Add Todo'}
</button>
{mutation.isError && <div>{mutation.error.message}</div>}
```

## mutate and mutateAsync

- `mutate(variables, { onSuccess, onError, onSettled })` — fire and forget; per-call callbacks run in addition to the hook-level ones
- `mutateAsync(variables, options)` — returns the promise, so you can `await` it in an event handler:

```tsx
const onSubmit = async (event) => {
  event.preventDefault()
  await mutation.mutateAsync(new FormData(event.target))
  // safe to close the dialog, navigate, etc.
}
```

`variables` is a single argument — pass one object. Note `mutate` is async: in React ≤ 16 you cannot pass it directly to an event handler (event pooling); wrap it.

## Resetting mutation state

`mutation.reset()` clears `data`, `error` and returns the mutation to `idle` — useful for dismissing an error or clearing a success message after the user acts on it.

## Lifecycle callbacks

Callbacks receive `(data | error | undefined, variables, context)`:

```tsx
useMutation({
  mutationFn: addTodo,
  onMutate: async (variables) => {
    // runs before mutationFn; may return a `context` object used by later callbacks
  },
  onError: (error, variables, context) => {},
  onSuccess: (data, variables, context) => {},
  onSettled: (data | error, error, variables, context) => {},
})
```

- If a callback returns a promise, it is awaited before the next stage runs
- `onSettled` always runs (success or error)
- Queries do **not** have these callbacks in v5 — only mutations do

## Invalidation from mutations

The standard write-then-refresh pattern — invalidate affected key prefixes in `onSuccess`:

```tsx
const queryClient = useQueryClient()

const mutation = useMutation({
  mutationFn: addTodo,
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['todos'] })
    queryClient.invalidateQueries({ queryKey: ['reminders'] })
  },
})
```

Invalidation marks matching queries stale (overriding `staleTime`) and refetches any that are currently rendered, in the background. Any callback can drive invalidation (`onMutate`, `onError`, `onSettled`) when the timing suits.

## Updates from mutation responses

When a mutation **updates** an object and the server returns the new object, skip the refetch and write it straight into the cache with `setQueryData`:

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

Cache updates must be **immutable** — never mutate a cached object in place; it "works" until it subtly breaks. The updater form `setQueryData(key, (old) => ...)` is the safe default.

## Optimistic updates

Combine `onMutate` (write the optimistic value + capture a rollback context) with `onError` (rollback):

```tsx
const mutation = useMutation({
  mutationFn: updateTodo,
  onMutate: async (variables) => {
    queryClient.cancelQueries({ queryKey: ['todos'] })          // avoid racing overwrites
    const previousTodos = queryClient.getQueryData(['todos'])
    queryClient.setQueryData(['todos'], (todos) =>               // apply optimistically
      todos.map((t) => (t.id === variables.id ? { ...t, ...variables } : t)))
    return { previousTodos }                                     // rollback context
  },
  onError: (_err, _variables, context) => {
    queryClient.setQueryData(['todos'], context?.previousTodos)  // roll back
  },
  onSettled: () => {
    queryClient.invalidateQueries({ queryKey: ['todos'] })       // guarantee convergence
  },
})
```

Guidance on when to use what:

- **Optimistic updates** — best for single-object updates where the response is slow or the change is near-certain; the UI never waits
- **Invalidation** — best for list insertions/deletions or anything that may change other rows; simpler and self-correcting
- **`setQueryData` from the response** — best when the mutation response already contains the new object

## Global mutation hooks

- `useIsMutating(filters?)` — count of in-flight mutations (optionally filtered by `mutationKey`, `exact`, `status`, `predicate`); handy for a global save indicator
- `useMutationState({ filters, select })` — array of `{ mutation, state }` pairs for custom mutation dashboards
- `queryClient.isMutating(filters)` — imperative equivalent
- `queryClient.resumePausedMutations()` — continue mutations that were paused offline (call on reconnect; also the default when using `networkMode: 'online'` and the `onlineManager`)
- `queryClient.setMutationDefaults(['todos'], {...})` — per-key defaults
