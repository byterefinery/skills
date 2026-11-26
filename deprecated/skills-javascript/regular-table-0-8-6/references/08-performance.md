# Performance

regular-table is designed for high-performance rendering of large datasets. Understanding its performance characteristics helps optimize real-world usage.

## getDrawFPS

Measure rendering performance:

```javascript
const stats = table.getDrawFPS();
// {
//   avg: 8.5,           // average ms per frame
//   real_fps: 58.8,     // actual frames per second
//   virtual_fps: 117.6, // theoretical max fps
//   num_frames: 59,     // frames since last call
//   elapsed: 1000       // ms since last call
// }
```

Each call to `getDrawFPS()` resets the internal counter. Use it in a timer for continuous monitoring:

```javascript
setInterval(() => {
  const { real_fps, avg } = table.getDrawFPS();
  console.log(`${real_fps} fps, ${avg}ms/frame`);
}, 1000);
```

## Performance Factors

### DataListener Speed

The `DataListener` callback is called on every viewport change. Slow callbacks block rendering.

```javascript
// Fast: direct array access
function fastListener(x0, y0, x1, y1) {
  return {
    num_rows: DATA[0].length,
    num_columns: DATA.length,
    data: DATA.slice(x0, x1).map((col) => col.slice(y0, y1)),
  };
}

// Slow: network request per viewport
function slowListener(x0, y0, x1, y1) {
  return fetch(`/api/data?x0=${x0}&y0=${y0}&x1=${x1}&y1=${y1}`).then(r => r.json());
}
```

For async backends, consider caching responses or using a Web Worker to avoid blocking the main thread.

### Style Listener Overhead

`addStyleListener()` callbacks run on every render. Heavy DOM queries degrade scroll performance.

```javascript
// Expensive: queries all cells
table.addStyleListener(() => {
  for (const td of table.querySelectorAll("td")) {
    // complex logic for every cell
  }
});

// Better: only query relevant cells
table.addStyleListener(() => {
  for (const td of table.querySelectorAll("td.highlight")) {
    // only process highlighted cells
  }
});
```

### Cell Content Complexity

Simple text cells render fastest. Complex HTML content slows down rendering:

```javascript
// Fast: plain text
data: [["Hello", "World"]],

// Slower: HTML elements
data: [[document.createElement("div"), document.createElement("span")]],

// Slowest: complex nested elements
data: [[createComplexWidget()]],
```

## Optimization Strategies

### 1. Set row_height

Avoid auto-measurement overhead:

```javascript
return {
  num_rows: 1000000,
  num_columns: 20,
  data: /* ... */,
  row_height: 25,
};
```

### 2. Use virtual_mode: "both"

Default mode virtualizes both axes, keeping DOM node count minimal:

```javascript
table.setDataListener(listener, { virtual_mode: "both" });
```

### 3. Minimize Style Listeners

Fewer style listeners mean less work per render:

```javascript
// Combine multiple style operations into one listener
table.addStyleListener(() => {
  for (const td of table.querySelectorAll("td")) {
    const meta = table.getMeta(td);
    // Apply all styles in one pass
    if (meta.value < 0) td.classList.add("negative");
    if (meta.y % 2 === 0) td.classList.add("zebra");
  }
});
```

### 4. Use preserve_state

When updating data, preserve scroll position and column sizes:

```javascript
table.setDataListener(newListener, { preserve_state: true });
```

### 5. Batch Data Updates

Avoid calling `draw()` repeatedly:

```javascript
// Bad: multiple draws
data[0][0] = 1;
table.draw();
data[0][1] = 2;
table.draw();

// Good: single draw after all updates
data[0][0] = 1;
data[0][1] = 2;
table.draw();
```

### 6. Web Worker for Heavy Computation

Offload data processing to a Web Worker:

```javascript
const worker = new Worker("data-worker.js");

table.setDataListener((x0, y0, x1, y1) => {
  return new Promise((resolve) => {
    worker.postMessage({ x0, y0, x1, y1 });
    worker.once("message", (e) => resolve(e.data));
  });
});
```

## Large Dataset Patterns

### Billion-Row Simulation

Generate data on-the-fly without storing it:

```javascript
const NUM_ROWS = 2_000_000_000;
const NUM_COLUMNS = 1000;

table.setDataListener((x0, y0, x1, y1) => ({
  num_rows: NUM_ROWS,
  num_columns: NUM_COLUMNS,
  data: Array.from({ length: x1 - x0 }, (_, dx) =>
    Array.from({ length: y1 - y0 }, (_, dy) => {
      const x = x0 + dx;
      const y = y0 + dy;
      return generateValue(x, y);
    })
  ),
}));
```

### Paginated Backend

```javascript
table.setDataListener(async (x0, y0, x1, y1) => {
  const response = await fetch(`/api/data`, {
    method: "POST",
    body: JSON.stringify({ x0, y0, x1, y1 }),
  });
  return response.json();
});
```

### Cached Data Model

```javascript
const cache = new Map();

table.setDataListener(async (x0, y0, x1, y1) => {
  const key = `${x0},${y0},${x1},${y1}`;
  if (cache.has(key)) {
    return cache.get(key);
  }

  const data = await fetchData(x0, y0, x1, y1);
  cache.set(key, data);

  // Evict old entries if cache grows too large
  if (cache.size > 100) {
    cache.delete(cache.keys().next().value);
  }

  return data;
});
```

## Memory Considerations

- **Virtual mode keeps DOM minimal** — with `virtual_mode: "both"`, only visible cells exist in the DOM regardless of dataset size.
- **DataListener should not accumulate state** — avoid storing references to large objects in closure variables.
- **Call `clear()` on disposal** — `table.clear()` frees internal state. Call it when the table is no longer needed.
- **Style listener closures** — avoid capturing large objects in style listener closures, as they are retained for the lifetime of the listener.

## Benchmarking

```javascript
const start = performance.now();
await table.draw();
const elapsed = performance.now() - start;
console.log(`Draw took ${elapsed.toFixed(2)}ms`);
```

For continuous monitoring:

```javascript
const fpsMonitor = setInterval(() => {
  const { real_fps, avg } = table.getDrawFPS();
  if (real_fps < 30) {
    console.warn(`Low FPS: ${real_fps}, avg: ${avg}ms`);
  }
}, 5000);
```

## Gotchas

- **`getDrawFPS()` resets on call** — each invocation clears the frame counter. Call at fixed intervals for accurate measurement.
- **First `draw()` is slower** — initial render includes column width measurement and layout calculation. Subsequent draws are faster.
- **Async DataListener blocks rendering** — the table waits for the Promise to resolve before rendering. Slow network calls directly impact perceived performance.
- **Too many style listeners hurt scroll** — each listener runs on every render. Keep the total number low and each callback fast.
- **`virtual_mode: "none"` with large data** — renders all cells in the DOM, causing memory and performance issues. Only use for small tables.
