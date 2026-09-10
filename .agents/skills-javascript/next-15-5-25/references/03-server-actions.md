# Server Actions

Server Actions (Server Functions) let you execute server-side code from the client without writing an API endpoint. Mark a function with the `'use server'` directive; it gets a stable reference that can be passed to the client as a prop.

## Basics

```ts
// app/lib/actions.ts
'use server'
import { revalidatePath } from 'next/cache'

export async function createPost(formData: FormData) {
  // runs only on the server
  await save(formData)
  revalidatePath('/posts')
}
```

- Put actions in their own file (a file with `'use server'` at the top is entirely server-only) or mark individual functions.
- Only exported functions can be called; they can be async.
- Call sites: Client Components via `form action={createPost}` or an event handler; a Server Component can pass an action to a Client Component's `form` or as a prop.
- The argument and return values must be serializable (FormData, primitives, JSON-able data).
- `experimental.serverActions` config can cap `bodySizeLimit` (default 1MB) and add `allowedOrigins` for cross-origin (e.g. proxied) action calls.

## Forms

```tsx
import { createPost } from '@/lib/actions'
export default function Page() {
  return (
    <form action={createPost}>
      <input name="title" />
      <button>Create</button>
    </form>
  )
}
```

- `FormData` is passed automatically. For non-form inputs, wrap in a function that builds FormData.
- **`useActionState`** (React 19; the old `useFormState` is deprecated) reads the form's state and pending flag:

```tsx
'use client'
import { useActionState } from 'react'

async function createPost(prevState: ActionState, formData: FormData) {
  'use server'
  try {
    await save(formData)
    return { ok: true }
  } catch (e) {
    return { ok: false, message: 'Something went wrong' }
  }
}

export function Form() {
  const [state, formAction, pending] = useActionState(createPost, { ok: false })
  return (
    <form action={formAction}>
      {state.ok ? <p>Saved</p> : <p>{state.message}</p>}
      <button disabled={pending}>{pending ? 'Saving…' : 'Save'}</button>
    </form>
  )
}
```

- **`useOptimistic(state, action)`** renders a predicted state while an action is in flight.
- **`<Form>` from `next/form`** (15.5) wraps `<form>` to add client-side navigation and loading-UI prefetching for forms that update the URL (e.g. search): `<Form action="/search"><input name="q" /></Form>` navigates to `/search?q=…` without a full page load; Server Actions work in it too.
- Error handling: return state on failure (above), throw for boundary-level errors, or catch in the action and surface a message. Never leak stack traces to the UI.

## Revalidating after mutations

Call inside the action, in this order (redirect throws — put revalidation first):

```ts
import { revalidatePath, revalidateTag } from 'next/cache'
import { redirect } from 'next/navigation'

export async function createPost(formData: FormData) {
  'use server'
  await save(formData)
  revalidatePath('/posts')       // by path; type 'layout' | 'page' | 'router' optional
  revalidateTag('posts')          // by cache tag, if you tag your fetches
  redirect('/posts')
}
```

- `revalidatePath` invalidates the Full Route Cache for that path and the client Router Cache (so the UI updates immediately).
- `revalidateTag` only clears matching Data Cache entries; the route re-renders on the next request.
- Setting/deleting a cookie inside a Server Action also re-renders the current page on the server, so the UI reflects the new value.
- From a plain Client Component (outside a form), call `router.refresh()` after an action to refetch the route.
- For work that must not block the response (logging, analytics, webhooks), schedule it with `after(() => ...)` from `next/server` (stable since 15.1); it runs after the response is sent and does not make the route dynamic.

## Client navigation hooks (`next/navigation`)

| Hook | Use |
|---|---|
| `useRouter()` | `push`, `replace`, `prefetch`, `back`, `forward`, `refresh` |
| `usePathname()` | Current path |
| `useParams()` | Current route params (client tree) |
| `useSearchParams()` | Read-only query string — **wrap the component in `<Suspense>`** in static routes |
| `redirect(url)` | Throw-based navigation, server or client |
| `notFound()` | Throw-based 404; nearest `not-found.tsx` renders |
| `forbidden()` / `unauthorized()` | Throw-based 403/401 (experimental, needs `experimental.authInterrupts: true`; file conventions `forbidden.tsx` / `unauthorized.tsx`) |

## Gotchas

- Actions are not API routes: no HTTP verbs, no CORS, called only from your app.
- A file exporting actions cannot also import client-only modules (DOM, browser APIs).
- `useActionState`'s first argument is the *action*; the form must use the returned `formAction`, not the raw action.
- Actions run in the Node.js runtime by default; they cannot use `cookies.set` with an Edge-only API shape (use the Next.js `cookies()` from `next/headers`, which is async in 15).
- After `redirect()`, nothing below it runs — no `revalidatePath` after the redirect.
