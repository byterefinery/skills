# Arbitrary Values

Arbitrary values let you use any value with Tailwind utilities using bracket notation `[...]`.

## Basic Syntax

```html
<div class="w-[200px]">  /* width: 200px */
<div class="text-[#bada55]">  /* color: #bada55 */
<div class="bg-[url('/img.png')]">  /* background-image: url(...) */
```

## Common Patterns

### Colors

```html
<div class="text-[#bada55]">
<div class="bg-[rgb(255,0,0)]">
<div class="bg-[oklch(70%_0.15_145)]">
<div class="border-[color:var(--my-color)]">
```

### Dimensions

```html
<div class="w-[200px]">
<div class="h-[100vh]">
<div class="max-w-[90ch]">
<div class="min-h-[300px]">
```

### Spacing

```html
<div class="m-[10px]">
<div class="p-[2%]">
<div class="mt-[-10px]">
<div class="gap-[1rem]">
```

### Fonts

```html
<p class="font-[Inter]">
<p class="text-[15px]">
<p class="leading-[1.4]">
<p class="tracking-[0.05em]">
```

### Borders

```html
<div class="border-[3px]">
<div class="border-[2px_dashed_#ccc]">
<div class="rounded-[12px]">
```

### Shadows

```html
<div class="shadow-[0_4px_6px_-1px_rgba(0,0,0,0.1)]">
<div class="inset-shadow-[0_2px_4px_rgba(0,0,0,0.2)]">
```

### Transforms

```html
<div class="rotate-[13deg]">
<div class="scale-[1.02]">
<div class="skew-x-[3deg]">
<div class="translate-x-[15%]">
```

### Transitions

```html
<div class="duration-[200ms]">
<div class="delay-[100ms]">
<div class="ease-[cubic-bezier(0.4,0,0.2,1)]">
```

### Filters

```html
<div class="blur-[10px]">
<div class="brightness-[1.2]">
<div class="contrast-[0.8]">
```

### Backgrounds

```html
<div class="bg-[url('/img.png')]">
<div class="bg-[linear-gradient(45deg,red,blue)]">
<div class="bg-[length:200px_100px]">
<div class="bg-[position:center_top]">
```

### Grid

```html
<div class="grid-cols-[200px_minmax(0,1fr)_100px]">
<div class="grid-rows-[auto_1fr_auto]">
<div class="col-span-[2]">
```

## Arbitrary Properties

Use `[#property]:value` syntax for any CSS property:

```html
<div class="[text-shadow:0_2px_4px_rgba(0,0,0,0.3)]">
<div class="[backdrop-filter:blur(10px)]">
<div class="[animation-duration:300ms]">
<div class="[--my-custom-prop:10px]">
```

For properties with special characters, use the `[#...]` form:

```html
<div class="[text-wrap:balance]">
<div class="[word-break:break-word]">
```

## Arbitrary Variants

Use `[@selector]:` for any CSS selector:

```html
<div class="[&:nth-child(3)]:text-red-500">
<div class="[&_>img]:rounded-lg">
<div class="[&_[data-active]]:font-bold">
<div class="[&::-webkit-scrollbar]:w-2">
```

The `&` represents the element itself. Use `*` for descendants.

### Complex Selectors

```html
<div class="[&:has(>input:checked)]:bg-green-50">
<div class="[&:not(:first-child)]:mt-4">
<div class="[&:is(:first,:last)]:font-bold">
<div class="[&>*:not(:last-child)]:mb-2">
```

## Data Type Hints

When the value type is ambiguous, provide a hint:

```html
<div class="text-[length:10px]">  /* force as font-size */
<div class="text-[color:#ff0000]">  /* force as color */
<div class="bg-[url:('/img.png')]">  /* force as URL */
<div class="border-[length:2px]">  /* force as border-width */
<div class="border-[color:red]">  /* force as border-color */
```

Available data types: `length`, `color`, `url`, `image`, `position`, `size`, `percentage`, `number`, `integer`, `angle`, `family-name`, `generic-name`, `absolute-size`, `relative-size`.

## Modifiers with Arbitrary Values

Combine arbitrary values with opacity modifiers:

```html
<div class="bg-[#ff0000]/50">  /* red at 50% opacity */
<div class="text-[var(--my-color)]/75">  /* custom color at 75% opacity */
```

## Fractional Values

Tailwind supports fractions natively for sizing:

```html
<div class="w-1/2">  /* width: 50% */
<div class="w-1/3">  /* width: 33.33% */
<div class="w-2/3">  /* width: 66.66% */
<div class="w-1/12">  /* width: 8.33% */
```

Fractions work with: `w-*`, `h-*`, `min-w-*`, `min-h-*`, `max-w-*`, `max-h-*`, `inset-*`, `translate-*`, `basis-*`.

## Calc Expressions

Use arbitrary values with calc:

```html
<div class="w-[calc(100%-4rem)]">
<div class="h-[calc(100vh-64px)]">
<div class="top-[calc(50%+1rem)]">
```

## CSS Variables in Arbitrary Values

Reference CSS custom properties:

```html
<div class="text-[var(--my-color)]">
<div class="bg-[var(--bg-gradient)]">
<div class="w-[var(--card-width)]">
```

## Patterns

### Dynamic Sizing

```html
<div class="w-[var(--sidebar-width)] min-w-[200px] max-w-[400px]">
```

### Custom Animations

```html
<div class="[animation:slide-in_0.3s_ease-out]">
```

### Complex Gradients

```html
<div class="bg-[conic-gradient(from_90deg_at_50%_50%,#000,transparent,#000)]">
```

### Responsive Arbitrary Values

```html
<div class="w-[200px] sm:w-[300px] md:w-[400px]">
```

### Arbitrary Values with Variants

```html
<div class="hover:bg-[#ff6600] focus:ring-[3px] focus:ring-[#0066ff]/50">
```
