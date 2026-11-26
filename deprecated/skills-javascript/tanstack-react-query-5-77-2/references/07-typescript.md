# TypeScript

## Contents

- [Version notes](#version-notes)
- [Type inference](#type-inference)
- [Type narrowing](#type-narrowing)
- [Typing errors](#typing-errors)
- [Typing meta](#typing-meta)
- [Typing query and mutation keys](#typing-query-and-mutation-keys)
- [Typing query options](#typing-query-options)
- [Typing query functions](#typing-query-functions)
- [skipToken](#skiptoken)

## Version notes

- TypeScript **4.7+** is the minimum (an important inference fix landed in 4.7)
- Type changes in the library are treated as **non-breaking** and ship in patch releases — lock the package version and expect type refinements between patches
- The runtime public API follows strict semver; types do not

## Type inference

Generics flow from `queryFn` through to the result — no annotations needed when the fetch function is properly typed:

```tsx
const { data } = useQuery({
  queryKey: ['test'],
  queryFn: () => Promise.resolve(5),
})
//        ^? const data: number | undefined

const fetchGroups = (): Promise<Group[]> =>
  axios.get('/groups').then((response) => response.data)

const { data } = useQuery({ queryKey: ['groups'], queryFn: fetchGroups })
//      ^? const data: Group[] | undefined
```

With `select`, `data` is typed as the select's return. Most HTTP clients return `any` by default — extract a properly typed fetch function first, or inference collapses to `any`.

## Type narrowing

The query result is a **discriminated union** over `status` and the boolean flags — checking `isSuccess` (or `status === 'success'`) narrows `data` from `TData | undefined` to `TData`, and checking `isError` narrows `error`.

## Typing errors

`error` defaults to `Error`. Options, in increasing order of specificity:

1. **Global registration** (recommended) — augment the `Register` interface once and every call site inherits it, with inference intact:

```tsx
import '@tanstack/react-query'

declare module '@tanstack/react-query' {
  interface Register {
    defaultError: AxiosError
  }
}

const { error } = useQuery({ queryKey: ['groups'], queryFn: fetchGroups })
//      ^? const error: AxiosError | null
```

2. **Narrowing at the call site** — for subclasses like `AxiosError` without a global:

```tsx
if (axios.isAxiosError(error)) {
  // error: AxiosError
}
```

3. Explicit generics on the hook — works but disables inference for the other generics, so prefer the first two.

Avoid throwing non-`Error` values.

## Typing meta

`meta` is `Record<string, unknown>` by default; register a global `Meta` type (it must extend `Record<string, unknown>`) to keep `meta` consistent and type-safe across queries and mutations:

```tsx
interface MyMeta extends Record<string, unknown> {
  tag: 'admin' | 'public'
}

declare module '@tanstack/react-query' {
  interface Register {
    queryMeta: MyMeta
    mutationMeta: MyMeta
  }
}
```

## Typing query and mutation keys

Register global key types (they must extend `Array`) to give every `queryKey`/`mutationKey` a typed first element across the whole library:

```tsx
type QueryKey = ['dashboard' | 'marketing', ...ReadonlyArray<unknown>]

declare module '@tanstack/react-query' {
  interface Register {
    queryKey: QueryKey
    mutationKey: QueryKey
  }
}
```

## Typing query options

Inlined options infer automatically. When options are **extracted into a function** to share between `useQuery` and `queryClient.prefetchQuery`/`getQueryData`, plain function return types lose the inference — wrap them in the `queryOptions` helper:

```tsx
import { queryOptions } from '@tanstack/react-query'

function groupOptions(id: number) {
  return queryOptions({
    queryKey: ['groups', id],
    queryFn: () => fetchGroups(id),
    staleTime: 5 * 1000,
  })
}

useQuery(groupOptions(1))
useSuspenseQuery(groupOptions(5))
queryClient.prefetchQuery(groupOptions(23))
const data = queryClient.getQueryData(groupOptions(42).queryKey)
//     ^? const data: Group[] | undefined   — the key knows its queryFn
```

- `infiniteQueryOptions(...)` is the equivalent for infinite queries
- Component-level overrides keep inference: `useQuery({ ...groupOptions(1), select: (d) => d.groupName })` — `data` becomes the select's return type

## Typing query functions

`queryFn` is typed as `(context: QueryFunctionContext) => Promise<TData>`. When writing standalone fetch functions, type their return (e.g. `(): Promise<Group[]>`) rather than relying on `fetch`/`axios` inference, which yields `any` without annotation. Destructure `queryKey` from the context to keep the function reusable across components:

```tsx
function fetchTodoList({ queryKey }: { queryKey: ['todos', { status: string; page: number }] }) {
  const [, { status, page }] = queryKey
  return getTodos({ status, page })
}
```

## skipToken

For TypeScript, `skipToken` (imported from `@tanstack/react-query`) is the type-safe alternative to `enabled: false` when the *function itself* depends on the condition:

```tsx
const { data } = useQuery({
  queryKey: ['todos', filter],
  queryFn: filter ? () => fetchTodos(filter) : skipToken,
})
```

The query stays disabled (and type-safe) while the token is passed. `refetch()` does not work while a query is disabled by `skipToken`.
