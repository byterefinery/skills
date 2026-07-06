# Auto-Animate Reference

Auto-animate automatically transitions matching elements between consecutive slides. Elements are matched by `data-id` attribute. Position, scale, and CSS properties animate smoothly.

## Basic Usage

Both slides need `data-auto-animate`. Elements with matching `data-id` are animated:

```html
<section data-auto-animate>
  <h2 data-id="title">Hello</h2>
  <div data-id="box" style="background:cyan;width:50px;height:50px"></div>
</section>
<section data-auto-animate>
  <h2 data-id="title" style="color:red; margin-top: 100px">Hello</h2>
  <div data-id="box" style="background:magenta;width:150px;height:100px"></div>
</section>
```

## What Gets Animated

### Position and Scale

Position (top/left/right/bottom) and size (width/height) are matched separately — no need to include them in `autoAnimateStyles`.

### CSS Properties

By default, these CSS properties are animated:
- `opacity`, `color`, `background-color`
- `padding`, `font-size`, `line-height`, `letter-spacing`
- `border-width`, `border-color`, `border-radius`
- `outline`, `outline-offset`

Extend via config: `autoAnimateStyles: ['opacity', 'transform', …]`

## Per-Slide Attributes

### Easing

```html
<section data-auto-animate data-auto-animate-easing="cubic-bezier(0.770, 0.000, 0.175, 1.000)">
```

Any valid CSS easing function. Default: `ease`.

### Duration

```html
<section data-auto-animate data-auto-animate-duration="2">
```

Duration in seconds. Default: `1.0`.

### Unmatched Elements

```html
<section data-auto-animate data-auto-animate-unmatched="fade">
```

Controls how elements without a match are handled. Values:
- `fade` — fade in/out unmatched elements
- `none` — no animation for unmatched elements
- `pop` — pop in effect

Default: controlled by `autoAnimateUnmatched` config (default `true` = fade).

## Per-Element Attributes

### Delay

```html
<div data-id="box1" data-auto-animate-delay="0">
<div data-id="box2" data-auto-animate-delay="0.1">
<div data-id="box3" data-auto-animate-delay="0.2">
```

Stagger animations with `data-auto-animate-delay` (seconds).

## Grouping with `data-auto-animate-id`

Use `data-auto-animate-id` to create separate auto-animate sequences. Elements are only matched between slides sharing the same group ID:

```html
<section data-auto-animate data-auto-animate-id="a">
  <h3>A1</h3>
</section>
<section data-auto-animate data-auto-animate-id="a">
  <h3>A1</h3>
  <h3>A2</h3>
</section>
<section data-auto-animate data-auto-animate-id="b">
  <h3>B1</h3>
</section>
<section data-auto-animate data-auto-animate-id="b">
  <h3>B1</h3>
  <h3>B2</h3>
</section>
```

Slides with different `data-auto-animate-id` values don't animate between each other, even if consecutive.

## Restart

```html
<section data-auto-animate data-auto-animate-restart>
```

Force the auto-animation to restart even when navigating backwards. By default, animations only run when moving forward.

## Code Block Auto-Animation

Combine auto-animate with code line highlights:

```html
<section data-auto-animate>
  <h2 data-id="title">Step 1</h2>
  <pre data-id="code"><code data-line-numbers class="hljs" data-trim>
    function Example() {
      const [count, setCount] = useState(0);
    }
  </code></pre>
</section>
<section data-auto-animate>
  <h2 data-id="title">Step 2</h2>
  <pre data-id="code"><code data-line-numbers class="hljs" data-trim>
    function Example() {
      const [count, setCount] = useState(0);
      return (
        <div>...</div>
      );
    }
  </code></pre>
</section>
```

The code block animates its content, and line highlights can change between steps.

## List Item Swapping

Auto-animate works with list items by matching content order:

```html
<section data-auto-animate>
  <ul>
    <li>One</li>
    <li>Two</li>
    <li>Three</li>
  </ul>
</section>
<section data-auto-animate>
  <ul>
    <li>Two</li>
    <li>One</li>
    <li>Three</li>
  </ul>
</section>
```

Items animate to their new positions.

## Custom Matcher

Provide a custom matching function:

```js
Reveal.initialize({
  autoAnimateMatcher: (elements, currentIndex, nextIndex) => {
    // Return array of { from: element, to: element } pairs
  }
});
```

## Vertical Stacks

Auto-animate works within vertical stacks. Each vertical slide can have `data-auto-animate`:

```html
<section>
  <section data-auto-animate>
    <div data-id="box" style="left: 0">A</div>
  </section>
  <section data-auto-animate>
    <div data-id="box" style="left: 25%">A</div>
  </section>
  <section data-auto-animate>
    <div data-id="box" style="left: 50%">A</div>
  </section>
</section>
```

## Scroll View

Auto-animate triggers on scroll in scroll view mode (`view: 'scroll'`). Elements animate as they enter the viewport.

## Reset

Programmatically reset all auto-animation state:

```js
// Navigate to a slide without data-auto-animate to reset
// Or call Reveal.sync() after DOM changes
```
