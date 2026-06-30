# Resources Reference

Resources handle icons, illustrations, and other visual assets in infographics. The framework provides built-in protocols for loading resources and a custom loader API for extending support.

## Resource Configuration

In data, the `icon` and `illus` properties configure resources:

```
data
  items
    - icon <ResourceConfig or string>
      illus <ResourceConfig or string>
```

## Built-in Protocols

### 1. Data URI (Inline SVG)

Embed SVG directly without any loader registration:

```
data
  items
    - icon data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg">...</svg>
```

### 2. Base64 Images

PNG, JPEG, GIF, etc. as base64:

```
data
  items
    - icon data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...
```

### 3. Remote URL

Use the `ref:remote` protocol:

```
data
  items
    - icon ref:remote:svg:https://example.com/icon.svg
    - illus ref:remote:https://example.com/banner.png
```

> When `fmt` is omitted, format is inferred from URL or Content-Type.

> **Warning**: Remote resources require CORS headers on the server.

### 4. Search Icon

Use AntV's icon search service:

```
data
  items
    - icon ref:search:svg:computer network
```

## ResourceConfig Object

```ts
interface ResourceConfig {
  source: 'inline' | 'remote' | 'search' | 'custom';
  format?: 'svg' | 'image' | string;     // Fallback format hint
  encoding?: 'raw' | 'data-uri' | 'base64';
  data: string;                           // inline content / URL / search term / custom payload
  scene?: 'icon' | 'illus';              // Framework auto-fills current field's scene
  [key: string]: any;                    // Custom extension
}
```

## Custom Resource Loader

Register a loader to fetch resources from your own service:

```ts
import {
  registerResourceLoader,
  loadSVGResource,
  loadImageBase64Resource,
  loadRemoteResource,
} from '@antv/infographic';

registerResourceLoader(async (config) => {
  const { data, scene = 'icon' } = config;

  // Load SVG from your server
  const response = await fetch(`https://your-api.com/assets?type=${scene}&id=${data}`);
  const svgString = await response.text();

  // Convert to framework-friendly resource object
  return loadSVGResource(svgString);
});
```

### Helper Functions

#### loadSVGResource()

Converts an SVG string into a usable resource object.

```ts
// Supports <svg> tags
const svg1 = '<svg xmlns="http://www.w3.org/2000/svg">...</svg>';
loadSVGResource(svg1); // auto-converted

// Supports <symbol> tags
const svg2 = '<symbol id="icon-star">...</symbol>';
loadSVGResource(svg2); // usable as-is

// Returns null on parsing failure
const resource = loadSVGResource(svgString);
if (!resource) {
  console.error('SVG parsing failed');
}
```

#### loadImageBase64Resource()

Converts a Base64 image (PNG, JPEG, GIF) into an SVG resource. Returns a Promise.

```ts
const resource = await loadImageBase64Resource(base64String);
```

#### loadRemoteResource()

Loads an SVG resource from a remote URL.

```ts
const resource = await loadRemoteResource('https://example.com/icon.svg');
```

### Iconify Example

```ts
registerResourceLoader(async (config) => {
  const { data, scene = 'icon' } = config;
  let url;

  if (scene === 'icon') {
    url = `https://api.iconify.design/${data}.svg`;
  } else {
    url = `https://raw.githubusercontent.com/balazser/undraw-svg-collection/refs/heads/main/svgs/${data}.svg`;
  }

  const response = await fetch(url);
  const svgString = await response.text();
  return loadSVGResource(svgString);
});
```

## Best Practices

### 1. Single Loader Instance

`registerResourceLoader` **replaces** the previous loader. Handle all resource types within one registration:

```ts
registerResourceLoader(async (config) => {
  if (config.scene === 'icon') {
    return await loadIcon(config.data);
  }
  if (config.scene === 'illus') {
    return await loadIllus(config.data);
  }
  if (typeof config.data === 'string' && config.data.startsWith('img:')) {
    return loadImageBase64Resource(await fetchImageAsBase64(config.data.slice(4)));
  }
  return null;
});
```

### 2. Cache Optimization

```ts
const cache = new Map<string, string>();

registerResourceLoader(async (config) => {
  const { data, scene } = config;
  const key = `${scene || 'default'}:${data}`;

  if (cache.has(key)) {
    return loadSVGResource(cache.get(key)!);
  }

  const svgString = await fetchFromYourServer(scene, data);
  cache.set(key, svgString);
  return loadSVGResource(svgString);
});
```

### 3. Error Handling

Return fallback resources when loading fails:

```ts
registerResourceLoader(async (config) => {
  try {
    const svgString = await fetchFromYourServer(config.data);
    return loadSVGResource(svgString);
  } catch (error) {
    console.warn(`Resource load failed: ${config.scene}:${config.data}`, error);
    return loadSVGResource(getPlaceholderSVG(config.scene));
  }
});

function getPlaceholderSVG(scene?: string): string {
  if (scene === 'icon') return '<svg><!-- icon placeholder --></svg>';
  if (scene === 'illus') return '<svg><!-- illustration placeholder --></svg>';
  return '<svg><!-- default placeholder --></svg>';
}
```

### 4. Preloading Resources

```ts
async function preloadResources(data) {
  const entries = [];
  data.items.forEach((item) => {
    if (item.icon) entries.push({ scene: 'icon', id: item.icon });
    if (item.illus) entries.push({ scene: 'illus', id: item.illus });
  });
  await Promise.all(entries.map(({ scene, id }) => fetchFromYourServer(scene, id)));
}

await preloadResources(data);
const infographic = new Infographic({ container: '#container' });
infographic.render(syntax);
```

## Considerations

- **Asynchronous loading** — resources load in parallel and don't block rendering. Slow resources may appear with a delay.
- **CORS required** — remote URLs need proper cross-origin headers.
- **Font CDN needs CORS + caching** — ensure font resources support CORS and caching for stable rendering.
- **Use readable resource identifiers** — prefer `icon: 'user-profile'` over `icon: 'res001'`.
- **Keep a unified protocol** — use consistent resource naming across your project.
