# Popups and Tooltips

## Popup

Display content in a popup bubble.

### Creation

```js
// Standalone
const popup = L.popup(options).setLatLng([lat, lng]).setContent('Hello').openOn(map);

// With latlng in constructor
const popup = L.popup([lat, lng], { content: 'Hello' }).openOn(map);

// Bound to a layer
marker.bindPopup('Hello').openPopup();

// Map shortcut
map.openPopup('Hello', [lat, lng]);
```

### Options

| Option | Default | Description |
|---|---|---|
| `pane` | `'popupPane'` | Map pane |
| `offset` | `[0, 7]` | Position offset |
| `maxWidth` | `300` | Maximum width in pixels |
| `minWidth` | `50` | Minimum width in pixels |
| `maxHeight` | `null` | Max height (scrollable if exceeded) |
| `autoPan` | `true` | Pan map to fit popup |
| `autoPanPaddingTopLeft` | `null` | Top-left autopan margin |
| `autoPanPaddingBottomRight` | `null` | Bottom-right autopan margin |
| `autoPanPadding` | `[5, 5]` | Default autopan padding |
| `keepInView` | `false` | Prevent panning popup off screen |
| `closeButton` | `true` | Show close button |
| `autoClose` | `true` | Close when another popup opens |
| `closeOnEscapeKey` | `true` | Close on ESC |
| `closeOnClick` | `*` | Close on map click (defaults to map option) |
| `className` | `''` | Custom CSS class |

### Methods

```js
popup.setLatLng([lat, lng]);
popup.getLatLng();              // → LatLng
popup.setContent(content);      // String, HTMLElement, or function
popup.getContent();             // → current content
popup.setDirection(direction);  // 'top', 'bottom', 'right'
popup.openOn(map);
popup.close();
popup.isOpen();                 // → Boolean
popup.update();                 // Force reposition/update
popup.toggle(layer);
popup.getElement();             // → HTMLElement
popup.getPane();                // → HTMLElement
```

### Map Methods

```js
map.openPopup(popup);
map.openPopup(content, [lat, lng], options);
map.closePopup(popup);
```

### Events

```js
// On map
map.on('popupopen', e => { e.popup; });
map.on('popupclose', e => { e.popup; });
map.on('autopanstart', e => {});

// On layer
marker.on('popupopen', e => { e.popup; });
marker.on('popupclose', e => { e.popup; });
```

## Tooltip

Small text label, typically shown on hover.

### Creation

```js
// Standalone
L.tooltip().setLatLng([lat, lng]).setContent('Hello').addTo(map);

// Bound to a layer
marker.bindTooltip('Hover text').openTooltip();
```

### Options

| Option | Default | Description |
|---|---|---|
| `pane` | `'tooltipPane'` | Map pane |
| `offset` | `[0, 0]` | Position offset |
| `direction` | `'auto'` | `'auto'`, `'top'`, `'bottom'`, `'left'`, `'right'`, `'center'` |
| `permanent` | `false` | Always visible (not just on hover) |
| `sticky` | `false` | Follow mouse cursor |
| `opacity` | `0.9` | Container opacity |
| `className` | `''` | Custom CSS class |

### Methods

```js
tooltip.setLatLng([lat, lng]);
tooltip.getLatLng();            // → LatLng
tooltip.setContent(content);    // String, HTMLElement, or function
tooltip.openOn(map);
tooltip.close();
tooltip.update();
tooltip.toggle(layer);
tooltip.setOpacity(opacity);
tooltip.getElement();           // → HTMLElement
```

### Map Methods

```js
map.openTooltip(tooltip);
map.openTooltip(content, [lat, lng], options);
map.closeTooltip(tooltip);
```

### Events

```js
// On map
map.on('tooltipopen', e => { e.tooltip; });
map.on('tooltipclose', e => { e.tooltip; });

// On layer
marker.on('tooltipopen', e => { e.tooltip; });
marker.on('tooltipclose', e => { e.tooltip; });
```

## Content Functions

Both Popup and Tooltip accept functions as content. The function receives the layer:

```js
marker.bindPopup(layer => {
	return `<b>${layer.feature.properties.name}</b>`;
});

marker.bindTooltip(layer => {
	return layer.getLatLng().toString();
});
```
