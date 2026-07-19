# API Reference

Summary of Vue 3.5.40 APIs organized by category.

## Table of Contents

- [Application API](#application-api)
- [Reactivity Core API](#reactivity-core-api)
- [Reactivity Advanced API](#reactivity-advanced-api)
- [Composition API: Lifecycle](#composition-api-lifecycle)
- [Composition API: Dependency Injection](#composition-api-dependency-injection)
- [Composition API: Helpers](#composition-api-helpers)
- [General API](#general-api)
- [Render Function API](#render-function-api)
- [Custom Renderer API](#custom-renderer-api)

## Application API

| API | Description |
|---|---|
| `createApp(RootComponent, props?)` | Creates an application instance |
| `createSSRApp(RootComponent, props?)` | Creates an SSR hydration app instance |
| `app.mount(rootContainer)` | Mounts the app to a DOM element or selector |
| `app.unmount()` | Unmounts the app, triggering unmount hooks |
| `app.onUnmount(callback)` | (3.5+) Callback on app unmount |
| `app.component(name, component?)` | Register/get global component |
| `app.directive(name, directive?)` | Register/get global directive |
| `app.mount(rootContainer)` | Mount to element/selector |
| `app.use(plugin, options?)` | Install a plugin |
| `app.mixin(mixin)` | Apply a mixin (affects all components) |
| `app.provide(key, value)` | Provide value to all descendant components |

### app.config

```ts
app.config.errorHandler = (err, instance, info) => {}
app.config.warnHandler = (msg, instance, trace) => {}
app.config.globalProperties = { $myHelper: () => {} }
app.config.optionMergeStrategies = { /* custom merge */ }
app.config.compilerOptions.isCustomElement = (tag) => customElements.get(tag)
app.config.compilerOptions.isNativeTag = (tag) => isHTMLTag(tag)
app.config.compilerOptions.isBuiltInComponent = (tag) => tag === 'Transition'
app.config.compilerOptions.delimiters = ['${', '}']
app.config.performance = false
app.config.unwrapInjectedRef = false
```

## Reactivity Core API

| API | Description |
|---|---|
| `ref(value)` | Creates a reactive ref with `.value` |
| `reactive(object)` | Creates a reactive proxy of an object |
| `computed(getter)` | Creates a readonly computed ref |
| `computed({ get, set })` | Creates a writable computed ref |
| `watch(source, callback, options?)` | Watches a source, calls callback on change |
| `watchEffect(effect, options?)` | Runs effect, auto-tracks dependencies |
| `watchPostEffect(effect)` | Alias of `watchEffect` with `flush: 'post'` |
| `watchSyncEffect(effect)` | Alias of `watchEffect` with `flush: 'sync'` |
| `onWatcherCleanup(cleanupFn)` | (3.5+) Register cleanup in watch/watchEffect |

## Reactivity Advanced API

| API | Description |
|---|---|
| `shallowRef(value)` | Shallow ref — only `.value` is reactive |
| `triggerRef(ref)` | Force trigger effects for a shallow ref |
| `shallowReactive(object)` | Only root-level reactivity |
| `shallowReadonly(object)` | Only root-level readonly |
| `readonly(object)` | Deep readonly proxy |
| `reactiveReadArray(ref)` | (3.5+) Read ref as reactive array |
| `isRef(value)` | Check if value is a ref |
| `isReactive(object)` | Check if object is a reactive proxy |
| `isReadonly(object)` | Check if object is readonly |
| `isShallow(object)` | Check if object is shallow reactive/readonly |
| `isProxy(object)` | Check if object is any kind of proxy |
| `toRef(object, key)` | Create a ref from an object property |
| `toRefs(object)` | Convert reactive object to plain object of refs |
| `toValue(getter)` | (3.3+) Normalize ref/getter/value |
| `unref(ref)` | Return `.value` if ref, else the value |
| `toRaw(proxy)` | Get original object from proxy |
| `markRaw(object)` | Mark object as never reactive |
| `customRef(factory)` | Create a custom ref with get/set control |
| `proxyRefs(object)` | Proxy object with auto-unwrapped refs |
| `effectScope()` | Create an effect scope for batch effect management |
| `onScopeDispose(callback)` | Register callback for scope disposal |

## Composition API: Lifecycle

| API | Description |
|---|---|
| `onMounted(callback)` | After component is mounted |
| `onUpdated(callback)` | After DOM is updated |
| `onUnmounted(callback)` | After component is unmounted |
| `onBeforeMount(callback)` | Before initial DOM creation |
| `onBeforeUpdate(callback)` | Before DOM re-render |
| `onBeforeUnmount(callback)` | Before component unmount |
| `onActivated(callback)` | Inside `<KeepAlive>`, on activation |
| `onDeactivated(callback)` | Inside `<KeepAlive>`, on deactivation |
| `onRenderTracked(event)` | Debugging: reactive dep tracked |
| `onRenderTriggered(event)` | Debugging: reactive dep triggered re-render |
| `onErrorCaptured(callback)` | Error captured from descendant |
| `onServerPrefetch(callback)` | Async data fetch during SSR |

## Composition API: Dependency Injection

| API | Description |
|---|---|
| `provide(key, value)` | Provide a value to descendants |
| `inject(key, defaultValue?, treatUndefinedAsMissing?)` | Inject a value from ancestor |
| `hasInjectionContext()` | Check if called within setup context |

## Composition API: Helpers

| API | Description |
|---|---|
| `useAttrs()` | Returns current component's attrs |
| `useSlots()` | Returns current component's slots |
| `useModel(props, name, options?)` | (3.4+) Programmatic v-model |
| `useTemplateRef(name)` | (3.5+) Typed template ref |
| `useId()` | (3.3+) Generate unique ID per app |

### Hydration Strategies (3.5+)

| API | Description |
|---|---|
| `hydrateOnIdle(cb)` | Hydrate when requestIdleCallback fires |
| `hydrateOnVisible(cb)` | Hydrate when element becomes visible |
| `hydrateOnMediaQuery(cb, query)` | Hydrate when media query matches |
| `hydrateOnInteraction(cb, events)` | Hydrate on user interaction |

## General API

| API | Description |
|---|---|
| `nextTick(callback?)` | Wait for next DOM update tick |
| `defineComponent(options)` | Type-safe component definition helper |
| `defineAsyncComponent(loader)` | Define an async component |
| `resolveComponent(name)` | (Runtime compiler) Resolve registered component |
| `resolveDirective(name)` | (Runtime compiler) Resolve registered directive |
| `withDirectives(element, directive)` | Apply custom directives in render functions |
| `withModifiers(handler, modifiers)` | Apply event modifiers in render functions |

## Render Function API

| API | Description |
|---|---|
| `h(type, props?, children?)` | Create a VNode |
| `cloneVNode(vnode, extraProps?)` | Clone a VNode |
| `mergeProps(a, b, ...)` | Merge props handling class/style/attrs |
| `isVNode(vnode)` | Check if value is a VNode |
| `createVNode(type, props?, children?)` | Create a VNode (same as h) |
| `createTextVNode(text)` | Create a text VNode |
| `createCommentVNode(text)` | Create a comment VNode |
| `createStaticVNode(html)` | Create a static VNode (raw HTML) |
| `createBlockVNode(type, props, children)` | Create a block tree root |
| `openBlock()` | Open a block tree for v-for optimization |
| `setupContext(slots, attrs, emit)` | Setup context for render functions |
| `Fragment` | VNode type for fragments |
| `Text` | VNode type for text nodes |
| `Comment` | VNode type for comment nodes |
| `Static` | VNode type for static content |
| `resolveDynamicComponent` | Resolve dynamic component by name/type |
| `resolveComponent` | Resolve globally registered component |
| `resolveDirective` | Resolve globally registered directive |
| `withDirectives` | Apply custom directives to VNode |
| `withModifiers` | Apply event modifiers to handler |

## Custom Renderer API

For building renderers targeting non-DOM environments (Canvas, terminal, etc.):

```js
import { createRenderer } from '@vue/runtime-core'

const { render, createApp } = createRenderer({
  // node ops
  insert(child, parent, anchor),
  remove(child),
  createElement(type, isCustom?, is),
  createText(text),
  createComment(text),
  setText(node, text),
  setElementText(node, text),
  parentNode(node),
  nextSibling(node),
  querySelector(selector),
  setScopeId(el, id),
  insertStaticContent(content, parent, anchor, ns, start, end),

  // patch props
  setProperty(el, key, value),
  setAttribute(el, key, value, namespace?),
})
```
