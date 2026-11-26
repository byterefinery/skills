# TypeScript

The library is written in TypeScript with strong inference — usually no annotations needed.

Support notes:

- v5 requires TypeScript 4.7+; the library tracks the DefinitelyTyped support window (TypeScript 5.7+ at this release)
- Type changes are considered **non-breaking** and ship as **patch** releases — lock the package to a specific patch and upgrade expecting type fixes between releases
- The non-type public API follows strict semver

## Type inference

`data` is inferred from the `queryFn` return type (and from `select` when present):

```tsx
const { data } = useQuery({
  queryKey: ['test'],
  queryFn: () => Promise.resolve(5),
}) // data: number | undefined

const { data } = useQuery({
  queryKey: ['test'],
  queryFn: () => Promise.resolve(5),
  select: (data) => data.toString(),
}) // data: string | undefined
```

Most fetch libraries return `any` by default — extract a typed function:

```tsx
const fetchGroups = (): Promise<Group[]> =>
  axios.get('/groups').then((response) => response.data)

const { data } = useQuery({ queryKey: ['groups'], queryFn: fetchGroups })
// data: Group[] | undefined
```

## Type narrowing

The query result is a discriminated union keyed on `status` and the derived booleans:

```tsx
const { data, isSuccess } = useQuery({ queryKey: ['test'], queryFn: () => Promise.resolve(5) })
if (isSuccess) {
  data // number
}
```

## Error typing

`error` defaults to `Error`. To throw non-`Error` values, pass the generic explicitly (this disables inference for the other generics):

```tsx
useQuery<Group[], string>({ queryKey: ['groups'], queryFn: fetchGroups })
// error: string | null
```

Prefer type narrowing for subclasses (e.g. `axios.isAxiosError(error)`), or register a global error type:

```tsx
import '@tanstack/react-query'

declare module '@tanstack/react-query' {
  interface Register {
    defaultError: unknown // forces explicit narrowing at call sites
  }
}
```

## Register augmentation

Augment the `Register` interface (must `import '@tanstack/react-query'` in the file):

- `defaultError` — global error type (see above)
- `queryMeta` / `mutationMeta` — global `meta` types; must extend `Record<string, unknown>`
- `queryKey` / `mutationKey` — global key types (e.g. `['dashboard' | 'marketing', ...ReadonlyArray<unknown>]`); must extend `Array` so keys stay arrays

```tsx
declare module '@tanstack/react-query' {
  interface Register {
    queryKey: QueryKey
    mutationKey: QueryKey
    queryMeta: MyMeta
    mutationMeta: MyMeta
  }
}
```

## queryOptions / infiniteQueryOptions / mutationOptions

Inlined options in `useQuery` infer automatically. When you extract options into a shared function, wrap them in the helper to keep inference (and to make the `queryKey` know its `queryFn`):

```ts
import { queryOptions } from '@tanstack/react-query'

function groupOptions(id: number) {
  return queryOptions({
    queryKey: ['groups', id],
    queryFn: () => fetchGroups(id),
    staleTime: 5 * 1000,
  })
}

// all of these work and keep types:
useQuery(groupOptions(1))
useSuspenseQuery(groupOptions(5))
useQueries({ queries: [groupOptions(1), groupOptions(2)] })
queryClient.query(groupOptions(23))
queryClient.setQueryData(groupOptions(42).queryKey, newGroups)
const data = queryClient.getQueryData(groupOptions(42).queryKey) // Group[] | undefined
```

- `infiniteQueryOptions` — same for infinite queries
- `mutationOptions` — same for mutations; the result works in `useMutation`, `useIsMutating`, `queryClient.isMutating`
- At the call site you can still override options (e.g. spread + a per-component `select`); `query.data` is then the `select` return type
- `queryOptions` inference does **not** apply to `queryClient.getQueriesData` (heterogeneous array of tuples — data is `unknown` unless you annotate: `getQueriesData<Group[]>(...)`)

## Known limitations

- `useQueries` with an **inline `select`** on a query object cannot infer the `select`'s `data` argument from that object's `queryFn` — it falls back to `unknown`. Annotate the `select` parameter explicitly or define the query with `queryOptions` first.
- `placeholderData` in `useQueries` does not receive `previousData` (dynamic arrays may change shape).

## skipToken

Type-safe disabling (see 02): `queryFn: cond ? fn : skipToken` — the options type keeps the `data` type from the enabled branch. Remember `refetch()` does not work with `skipToken`.
