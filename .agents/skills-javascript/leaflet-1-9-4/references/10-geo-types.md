# Geo Types

## LatLng

Represents a geographic point.

### Creation

```js
L.latLng(50.5, 30.5);              // (lat, lng)
L.latLng(50.5, 30.5, 100);         // (lat, lng, alt)
L.latLng([50.5, 30.5]);            // Array
L.latLng([50.5, 30.5, 100]);       // Array with altitude
L.latLng({ lat: 50.5, lng: 30.5 }); // Object
L.latLng({ lat: 50.5, lon: 30.5 }); // Object with lon
```

All Leaflet methods accepting LatLng also accept `[lat, lng]` arrays and `{lat, lng}` objects.

### Properties

- `lat` — Latitude in degrees
- `lng` — Longitude in degrees
- `alt` — Altitude in meters (optional)

### Methods

```js
latlng.equals(other, maxMargin);   // → Boolean
latlng.toString(precision);        // → 'LatLng(50.5, 30.5)'
latlng.distanceTo(other);          // → meters (Spherical Law of Cosines)
latlng.wrap();                     // → new LatLng with lng wrapped to [-180, 180]
latlng.toBounds(sizeInMeters);     // → LatLngBounds (accuracy circle)
latlng.clone();                    // → new LatLng
```

## LatLngBounds

Rectangular geographic area.

### Creation

```js
L.latLngBounds(corner1, corner2);
L.latLngBounds([[40.712, -74.227], [40.774, -74.125]]);
L.latLngBounds([latlng1, latlng2, latlng3]); // From array of points
```

### Methods

```js
bounds.extend(latlng);           // Extend to include point
bounds.extend(otherBounds);      // Extend to include other bounds
bounds.pad(ratio);               // → padded LatLngBounds (e.g., 0.5 = 50% buffer)
bounds.getCenter();              // → LatLng
bounds.getSouthWest();           // → LatLng
bounds.getNorthEast();           // → LatLng
bounds.getNorthWest();           // → LatLng
bounds.getSouthEast();           // → LatLng
bounds.getSouth();               // → Number
bounds.getNorth();               // → Number
bounds.getWest();                // → Number
bounds.getEast();                // → Number
bounds.contains(other);          // → Boolean (LatLng or LatLngBounds)
bounds.intersects(other);        // → Boolean (share at least one point)
bounds.overlaps(other);          // → Boolean (intersection is an area)
bounds.toBBoxString();           // → 'sw_lng,sw_lat,ne_lng,ne_lat'
bounds.equals(other, maxMargin); // → Boolean
bounds.isValid();                // → Boolean
```

## Point

2D pixel coordinate.

### Creation

```js
L.point(x, y, round);
L.point([x, y]);
```

### Methods

```js
point.x, point.y
point.clone()
point.add(other)
point.subtract(other)
point.divideBy(num)
point.multiplyBy(num)
point.scaleBy(scale)          // Scale by [x, y]
point.scaleFrom(center, s)
point.unscaleFrom(center, s)
point.round()
point.floor()
point.ceil()
point.distanceTo(other)       // → Number
point.contains(other)         // → Boolean
point.equals(other)           // → Boolean
point.isValid()               // → Boolean (both coords finite)
```

## Bounds

Rectangular area in pixel coordinates.

### Creation

```js
L.bounds(corner1, corner2);
L.bounds([point1, point2]);
```

### Methods

```js
bounds.min, bounds.max
bounds.isValid()
bounds.contains(other)
bounds.getBounds()
bounds.getSize()              // → Point
bounds.getCenter()            // → Point
bounds.intersects(other)      // → Boolean
bounds.isOverlapping(other)   // → Boolean
bounds.extend(point)
bounds.pad(buffer)            // → padded Bounds
bounds.isInside(point, buffer)
```

## Transformation

Linear transformation: `[x, y] → [a*x + b, c*y + d]`.

```js
L.transformation(a, b, c, d);
transformation.transform(point, scale);
transformation.untransform(point, scale);
```

## CRS (Coordinate Reference System)

### Available CRS

| CRS | Description |
|---|---|
| `L.CRS.EPSG3857` | Spherical Mercator (Web Mercator) — default, used by OSM |
| `L.CRS.EPSG4326` | WGS 84 — geographic lat/lng |
| `L.CRS.EPSG3395` | World Mercator |
| `L.CRS.Simple` | Simple planar CRS — no projection, pixels as coordinates |

### Usage

```js
// Mercator (default)
const map = L.map('map', { crs: L.CRS.EPSG3857 });

// Geographic (tiles at lat/lng)
const map = L.map('map', { crs: L.CRS.EPSG4326 });

// Simple (no projection, e.g., image maps)
const map = L.map('map', { crs: L.CRS.Simple });
```

### CRS Methods

```js
crs.latLngToPoint(latlng, zoom);   // → Point
crs.pointToLatLng(point, zoom);    // → LatLng
crs.project(latlng);               // → Point (projected units)
crs.unproject(point);              // → LatLng
crs.scale(zoom);                   // → scale factor
crs.zoom(scale);                   // → zoom level
crs.getProjectedBounds(zoom);      // → Bounds
crs.distance(latlng1, latlng2);    // → distance
crs.wrapLatLng(latlng);            // → wrapped LatLng
crs.wrapLatLngBounds(bounds);      // → wrapped bounds
```

### CRS Properties

- `code` — WMS code (e.g., `'EPSG:3857'`)
- `wrapLng` — `[min, max]` longitude wrap range
- `wrapLat` — `[min, max]` latitude wrap range
- `infinite` — unbounded coordinate space

## Projections

| Projection | Description |
|---|---|
| `L.Projection.LonLat` | Simple lat/lng → linear |
| `L.Projection.Mercator` | Mercator projection |
| `L.Projection.SphericalMercator` | Spherical Mercator (used by EPSG3857) |
