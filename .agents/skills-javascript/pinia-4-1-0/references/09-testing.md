# Testing Stores

Three things to handle: the `pinia` instance (stores cannot work without it), actions (often the most complex logic), and plugins (must be installed for tests too).

## Unit testing a store

Create a fresh pinia per test and make it active:

```js
import { setActivePinia, createPinia } from 'pinia'

describe('Counter Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })
  it('increments', () => {
    const counter = useCounterStore()
    expect(counter.n).toBe(0)
    counter.increment()
    expect(counter.n).toBe(1)
  })
})
```

**Plugins are not applied until pinia is installed in an App.** With plugins, create an empty app once:

```js
const app = createApp({})
beforeEach(() => {
  const pinia = createPinia().use(somePlugin)
  app.use(pinia)
  setActivePinia(pinia)
})
```

## Unit testing components — @pinia/testing

Install `@pinia/testing` and pass `createTestingPinia()` as a plugin when mounting:

```js
import { mount } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'

const wrapper = mount(Counter, {
  global: { plugins: [createTestingPinia()] },
})

const store = useSomeStore() // uses the testing pinia
store.name = 'my new name'   // state is directly manipulable
store.$patch({ name: 'new name' })
store.someAction()           // actions are stubbed by default
expect(store.someAction).toHaveBeenCalledTimes(1)
```

### Initial state

Pass `initialState` keyed by store id:

```js
createTestingPinia({
  initialState: {
    counter: { n: 20 },
  },
})
```

### Action stubbing

- `stubActions: false` — execute real actions (still spied).
- `stubActions: ['increment', 'reset']` — stub only those; others execute normally but are spied.
- `stubActions: (actionName, store) => boolean` — custom logic; evaluated once at store setup time with the initial state.
- An empty array means nothing is stubbed (same as `false`).
- You can also mock individual actions after creating the store: `store.increment.mockImplementation(() => {})`.

**Setup store limitation:** stubs replace actions on the store instance only. A setup action that calls another action via the closed-over function reference bypasses the stub. Route internal calls through the store (`useCounterStore().increment()`) to make them stubbable — or test the real implementation instead. Option stores have no limitation because internal calls go through `this`.

### Spy framework

With Jest or vitest `globals: true`, the spy function is detected automatically. Otherwise pass `createSpy` (e.g. `createSpy: vi.fn` or `createSpy: sinon.spy`).

### Mocking getters

Getters compute normally, but in tests they are **writable** — set a getter to any value, or set it to `undefined` to restore default behavior.

### Plugins

Pass plugins through `createTestingPinia({ plugins: [somePlugin] })` — do **not** use `testingPinia.use(MyPlugin)`.
