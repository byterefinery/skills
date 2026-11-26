# Auto-Animate

reveal.js 6.0.2 Auto-Animate automatically animates matching elements between consecutive slides (source: `examples/auto-animate.html`, `demo.html`, `js/controllers/autoanimate.js`, `js/config.ts`).

## Basics

- Add `data-auto-animate` to each slide in the sequence (both slides of a pair need it)
- Elements are matched across slides by `data-id` when present, or by their position in the slide otherwise (e.g. list items swap without any ids)
- Animatable CSS properties come from `autoAnimateStyles` (default: opacity, color, background-color, padding, font-size, line-height, letter-spacing, border-width, border-color, border-radius, outline, outline-offset). Position and scale are matched separately, so you do not need to list top/left/width/height/margin

## Per-slide attributes

| Attribute | Purpose |
|---|---|
| `data-auto-animate-easing` | CSS easing, e.g. `cubic-bezier(0.770, 0.000, 0.175, 1.000)` |
| `data-auto-animate-unmatched` | How to treat elements that have no match, e.g. `"fade"` fades them out |
| `data-auto-animate-id` | Names an animation sequence; slides sharing the same value form one sequence so independent sequences do not animate into each other |
| `data-auto-animate-restart` | On the later slide of a pair, restart the animation from the previous slide instead of continuing from the last-seen state |

## Per-element attributes

| Attribute | Purpose |
|---|---|
| `data-auto-animate-delay` | Delay in seconds before this element starts animating (e.g. `"0.1"`) |
| `data-id` | Identity used to match the element across slides |

## Config (global)

| Option | Default |
|---|---|
| `autoAnimate` | `true` |
| `autoAnimateMatcher` | `null` (custom element matcher function) |
| `autoAnimateEasing` | `'ease'` |
| `autoAnimateDuration` | `1.0` (seconds) |
| `autoAnimateUnmatched` | `true` |
| `autoAnimateStyles` | see Basics above |

## Notes

- Works inside vertical stacks (each slide of the stack gets `data-auto-animate`)
- Works in the scroll view, where animations trigger on scroll (`examples/scroll.html`)
- Code blocks with `data-line-numbers` inside auto-animate slides step their line highlights as fragments
- `data-auto-animate-restart` is checked on the physically later slide of the pair when deciding whether to animate
