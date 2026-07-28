# Utilities

Utility and helper classes for layout, spacing, and text alignment.

## Flex helpers

```css
.flex              { display: flex; }
.flex-col          { flex-direction: column; }
.items-center      { align-items: center; }
.justify-center    { justify-content: center; }
.justify-between   { justify-content: space-between; }
.justify-end       { justify-content: flex-end; }
```

## Stack layouts

```css
.hstack            { display: flex; align-items: center; gap: var(--space-3); flex-wrap: wrap; }
.vstack            { display: flex; flex-direction: column; gap: var(--space-3); }
```

`.hstack` and `.vstack` are the primary layout helpers — use them instead of raw flex for consistent gaps.

## Gap spacing

```css
.gap-1             { gap: var(--space-1); }    /* 0.25rem */
.gap-2             { gap: var(--space-2); }    /* 0.5rem */
.gap-4             { gap: var(--space-4); }    /* 1rem */
.gap-6             { gap: var(--space-6); }    /* 1.5rem */
```

## Margins (block axis)

```css
.mt-2              { margin-block-start: var(--space-2); }
.mt-4              { margin-block-start: var(--space-4); }
.mt-6              { margin-block-start: var(--space-6); }
.mt-8              { margin-block-start: var(--space-8); }

.mb-2              { margin-block-end: var(--space-2); }
.mb-4              { margin-block-end: var(--space-4); }
.mb-6              { margin-block-end: var(--space-6); }
.mb-8              { margin-block-end: var(--space-8); }
```

## Padding

```css
.p-4               { padding: var(--space-4); }
```

## Width

```css
.w-100             { width: 100%; }
```

## Text alignment

```css
.align-left        { text-align: start; }
.align-center      { text-align: center; }
.align-right       { text-align: end; }
```

## Text color

```css
.text-light        { color: var(--muted-foreground); }
.text-lighter      { color: var(--faint-foreground); }
```

## Unstyled list

```css
:is(ul, ol).unstyled { list-style: none; padding: 0; }
```

## Unstyled link

```css
a.unstyled { color: inherit; text-decoration: none; }
a.unstyled:hover { color: var(--primary); }
```

## Space scale

```css
--space-1:  0.25rem
--space-2:  0.5rem
--space-3:  0.75rem
--space-4:  1rem
--space-5:  1.25rem
--space-6:  1.5rem
--space-8:  2rem
--space-10: 2.5rem
--space-12: 3rem
--space-14: 3.5rem
--space-16: 4rem
--space-18: 4.5rem
```

## Border radius

```css
--radius-small:  0.125rem
--radius-medium: 0.375rem
--radius-large:  0.75rem
--radius-full:   9999px
```

## Shadows

```css
--shadow-small:  0 1px 2px 0 rgb(0 0 0 / 0.05)
--shadow-medium: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)
--shadow-large:  0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)
```

## Transitions

```css
--transition-fast: 120ms cubic-bezier(0.4, 0, 0.2, 1)
--transition:      200ms cubic-bezier(0.4, 0, 0.2, 1)
```

## Z-index

```css
--z-dropdown: 50
--z-modal:    200
```
