# Utilities

## L.Util

Core utility functions.

### Object

```js
L.Util.extend(dest, src);       // Shallow merge src into dest
L.Util.setOptions(obj, options); // Set options, merge with defaults
L.Util.stamp(obj);              // → unique ID (adds _leaflet_id)
L.Util.invokeEach(objs, method, context, ...args); // Call method on each
```

### Array

```js
L.Util.isArray(obj);            // → Boolean
L.Util.indexOf(arr, obj);       // → index
```

### Function

```js
L.Util.bind(fn, context, ...args);  // Bind function to context
L.Util.falseFn();                 // No-op function
```

### String

```js
L.Util.template(str, data);     // Template substitution (used for tile URLs)
L.Util.formatNum(1.234567, 2);  // → '1.23'
```

### Misc

```js
L.Util.requestAnimFrame(fn, context, preserveContext);  // → requestID
L.Util.cancelAnimFrame(id);                                // Cancel animation frame
L.Util.wrapNum(num, range, includeMax);  // Wrap number to range
```

## L.DomUtil

DOM manipulation helpers.

### Element Creation

```js
L.DomUtil.create(tagName, className, parent);  // → HTMLElement
L.DomUtil.get(id);                              // → HTMLElement (by ID or element)
L.DomUtil.remove(element);                      // Remove from DOM
L.DomUtil.empty(container);                     // Remove all children
```

### Class Manipulation

```js
L.DomUtil.addClass(element, name);
L.DomUtil.removeClass(element, name);
L.DomUtil.hasClass(element, name);  // → Boolean
```

### Positioning

```js
L.DomUtil.setPosition(element, point, skipTransition);
L.DomUtil.getPosition(element);     // → Point
L.DomUtil.getScale(element);        // → { x, y, boundingBox }
L.DomUtil.setTransform(element, offset, scale);  // CSS transform
```

### Styling

```js
L.DomUtil.getStyle(element, styleName);  // → computed style value
L.DomUtil.setOpacity(element, opacity);
L.DomUtil.testElement(element, props);   // Test CSS property support
L.DomUtil.getTranslateString(pos);       // → CSS transform string
```

### Z-Index

```js
L.DomUtil.toFront(element);
L.DomUtil.toBack(element);
```

### Misc

```js
L.DomUtil.disableImageDrag();         // Prevent image drag
L.DomUtil.disableTextSelection();
L.DomUtil.enableTextSelection();
L.DomUtil.preventOutline(fn);         // Prevent outline on focus
L.DomUtil.getSizedParentNode(element); // → nearest sized ancestor
```

### Feature Detection

```js
L.DomUtil.TRANSITION        // → 'transition' or 'WebkitTransition'
L.DomUtil.TRANSFORM         // → 'transform' or 'webkitTransform'
L.DomUtil.CSS_TRANSFORM_3D  // → Boolean
L.DomUtil.CSS_3DTRANSFORMS  // → Boolean
L.DomUtil.IE6               // → Boolean
L.DomUtil.IE7               // → Boolean
L.DomUtil.IE8               // → Boolean
L.DomUtil.IE9               // → Boolean
L.DomUtil.IE11              // → Boolean
L.DomUtil.opera             // → Boolean
L.DomUtil.touch             // → 'touchstart' (or false)
L.DomUtil.pointer           // → 'pointerdown' (or false)
L.DomUtil.pouch             // → Boolean (touch + pointer)
L.DomUtil.retina            // → Boolean
L.DomUtil.svg               // → Boolean
L.DomUtil.vml               // → Boolean
L.DomUtil.animationEnd      // → event name or false
L.DomUtil.userSelectCSS     // → CSS rules or empty
L.DomUtil.outlineCSS        // → CSS rules or empty
L.DomUtil.outlineNone       // → function or empty
L.DomUtil.transitionEnd     // → 'transitionend' or 'webkitTransitionEnd'
```

## L.Browser

Browser detection (computed once at load time).

```js
L.Browser.android
L.Browser.android23
L.Browser.androidChrome
L.Browser.edge
L.Browser.firefox
L.Browser.safari
L.Browser.webkit
L.Browser.gecko
L.Browseropera
L.Browser.mobileOpera
L.Browser.chrome
L.Browser.win
L.Browser.mac
L.Browser.linux
L.Browser.edge12
L.Browser.any3d
L.Browser.boundingClientRect
L.Browser.boxshadow
L.Browser.touch
L.Browser.mobile
L.Browser.retina
L.Browser.ielt9
L.Browser.ie
L.Browser.edge
L.Browser.safari
L.Browser.chrome
L.Browser.firefox
L.Browser.airplay
L.Browser.inlineSvg
L.Browser.nativeSvg
```

## L.LineUtil

Line geometry utilities.

```js
L.LineUtil.isFlat(latlngs);              // → Boolean (single ring)
L.LineUtil.closestPointOnSegment(p, p1, p2);
L.LineUtil.pointToSegmentDistance(p, p1, p2);
L.LineUtil.segmentIntersectSegment(a1, a2, b1, b2);
L.LineUtil.polylineCenter(ring, crs);    // → LatLng (centroid)
L.LineUtil.simplify(points, tolerance);  // Douglas-Peucker simplification
L.LineUtil.clipSegment(a, b, bounds, useClipCode, round);
L.LineUtil._flat(latlngs);               // Internal flat check
```

## L.PolyUtil

Polygon geometry utilities.

```js
L.PolyUtil.clipPolygon(ring, bounds, useClipCode);
L.PolyUtil.pointInPolygon(point, polygonPoints);  // → Boolean
```
