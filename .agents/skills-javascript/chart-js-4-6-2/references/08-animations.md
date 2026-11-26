# Animations

Charts animate out of the box. Animation configuration has three keys, configurable at chart options, `datasets[type]`, or `overrides[type]` (under `defaults` or `options`):

- `animation` — main animation configuration
- `animations` — per-property animation collections
- `transitions` — mode-specific animation configurations

## animation (options.animation)

| Name | Default | Description |
|---|---|---|
| `duration` | 1000 | Milliseconds |
| `easing` | 'easeOutQuart' | Easing function |
| `delay` | undefined | Delay before start |
| `loop` | undefined | true = loop endlessly |
| `onProgress` / `onComplete` | null | Callbacks receiving `{chart, currentStep, initial, numSteps}` |

These keys are scriptable. Defaults can be overridden in `options.animation`, `dataset.animation`, `tooltip.animation`.

## animations (options.animations)

Each entry configures which element properties animate and how: `properties` (defaults to the key name), `type` ('number', 'color', 'boolean' — only really needed for color), `from`, `to`, `fn` (custom interpolator).

Default collections: `numbers` → properties `['x', 'y', 'borderWidth', 'radius', 'tension']`; `colors` → `['color', 'borderColor', 'backgroundColor']` (both usually overridden by dataset controllers).

## transitions (options.transitions)

Core modes: `'active'`, `'hide'`, `'reset'`, `'resize'`, `'show'`; custom transitions are used by passing a custom mode to `chart.update(mode)`.

Default transitions:

| Mode | Setting | Description |
|---|---|---|
| 'active' | animation.duration = 400 | Hover animations |
| 'resize' | animation.duration = 0 | No animation on resize |
| 'show' | animations.colors from transparent + animations.visible duration 0 | Fade in when dataset shown |
| 'hide' | animations.colors to transparent + animations.visible easeInExpo | Fade out when dataset hidden |

## Disabling Animation

Set the node to `false` (transitions instead use `duration: 0`):

```js
chart.options.animation = false;                 // all animations
chart.options.animations.colors = false;         // one collection
chart.options.animations.x = false;              // one property
chart.options.transitions.active.animation.duration = 0;  // one transition
chart.update('none');                            // one update, no animation
```

## Easing Functions

`linear`, `easeInQuad`/`easeOutQuad`/`easeInOutQuad`, same pattern for `Cubic`, `Quart`, `Quint`, `Sine`, `Expo`, `Circ`, `Elastic`, `Back`, `Bounce` — 31 functions total, after Robert Penner's easing equations.
