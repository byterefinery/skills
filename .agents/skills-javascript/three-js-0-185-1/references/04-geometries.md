# Geometries

## BufferGeometry

Core geometry class. Stores vertex data in typed arrays (buffers) for efficient GPU transfer.

### Creating Custom Geometry

```js
const geometry = new THREE.BufferGeometry();

// Positions: 3 floats per vertex
const positions = new Float32Array( [
	// Triangle 1
	-1, -1,  1,
	 1, -1,  1,
	 1,  1,  1,
	// Triangle 2
	-1, -1,  1,
	 1,  1,  1,
	-1,  1,  1,
] );
geometry.setAttribute( 'position', new THREE.BufferAttribute( positions, 3 ) );

// UVs: 2 floats per vertex
const uvs = new Float32Array( [
	0, 0,
	1, 0,
	1, 1,
	0, 0,
	1, 1,
	0, 1,
] );
geometry.setAttribute( 'uv', new THREE.BufferAttribute( uvs, 2 ) );

// Normals: 3 floats per vertex
const normals = new Float32Array( [
	0, 0, 1,  0, 0, 1,  0, 0, 1,
	0, 0, 1,  0, 0, 1,  0, 0, 1,
] );
geometry.setAttribute( 'normal', new THREE.BufferAttribute( normals, 3 ) );

// Indices (optional, for shared vertices)
const indices = new Uint16Array( [
	0, 1, 2,  0, 2, 3,  0, 3, 4,  1, 2, 5,  2, 3, 5,  3, 4, 5
] );
geometry.setIndex( indices );

// Compute derived data
geometry.computeVertexNormals();
geometry.computeBoundingBox();
geometry.computeBoundingSphere();
```

### BufferAttribute Types

```js
// Standard attributes
new THREE.BufferAttribute( array, itemSize );
new THREE.BufferAttribute( array, itemSize, normalized );

// Typed variants (optimized)
new THREE.Float32BufferAttribute( array, itemSize );
new THREE.Float16BufferAttribute( array, itemSize );
new THREE.Uint16BufferAttribute( array, itemSize );
new THREE.Uint32BufferAttribute( array, itemSize );
new THREE.Int16BufferAttribute( array, itemSize );
new THREE.Int32BufferAttribute( array, itemSize );
new THREE.Uint8BufferAttribute( array, itemSize );
new THREE.Uint8ClampedBufferAttribute( array, itemSize );
new THREE.Int8BufferAttribute( array, itemSize );

// GLBufferAttribute — GPU-only buffer (no CPU readback)
new THREE.GLBufferAttribute( type, size, usage );

// Usage hints
THREE.StaticDrawUsage   // Set once, used many times
THREE.DynamicDrawUsage  // Updated frequently
THREE.StreamDrawUsage   // Updated every frame
```

### InterleavedBufferAttribute

Multiple attributes sharing a single buffer (cache-friendly):

```js
const buffer = new THREE.InterleavedBuffer(
	new Float32Array( [
		// position (3) + normal (3) + uv (2) = 8 floats per vertex
		-1, -1,  1,  0, 0, 1,  0, 0,
		 1, -1,  1,  0, 0, 1,  1, 0,
		 1,  1,  1,  0, 0, 1,  1, 1,
		-1,  1,  1,  0, 0, 1,  0, 1,
	] ),
	8  // stride
);

geometry.setAttribute( 'position', new THREE.InterleavedBufferAttribute( buffer, 3, 0 ) );
geometry.setAttribute( 'normal', new THREE.InterleavedBufferAttribute( buffer, 3, 12 ) );
geometry.setAttribute( 'uv', new THREE.InterleavedBufferAttribute( buffer, 2, 24 ) );
```

### Custom Attributes

```js
// Add custom attribute (accessible in shaders as attribute/myAttr)
const colors = new Float32Array( [
	1, 0, 0,
	0, 1, 0,
	0, 0, 1,
] );
geometry.setAttribute( 'color', new THREE.BufferAttribute( colors, 3 ) );

// In ShaderMaterial vertex shader:
// attribute vec3 color;
// varying vec3 vColor;
// void main() { vColor = color; ... }
```

## Built-in Geometries

```js
// Primitives
new THREE.BoxGeometry( width, height, depth, wSegs, hSegs, dSegs );
new THREE.SphereGeometry( radius, wSegs, hSegs );
new THREE.PlaneGeometry( width, height, wSegs, hSegs );
new THREE.CircleGeometry( radius, segs, thetaStart, thetaLength );
new THREE.ConeGeometry( radius, height, segs, hSegs, openEnded );
new THREE.CylinderGeometry( rTop, rBottom, height, segs, hSegs, openEnded );
new THREE.TorusGeometry( radius, tube, rSegs, tSegs, arc );
new THREE.TorusKnotGeometry( radius, tube, segs, tSegs, p, q );
new THREE.CapsuleGeometry( radius, length, capSegs, radSegs );
new THREE.RingGeometry( innerRadius, outerRadius, segs, thetaSegs );

// Polyhedra
new THREE.DodecahedronGeometry( radius, detail );
new THREE.IcosahedronGeometry( radius, detail );
new THREE.OctahedronGeometry( radius, detail );
new THREE.TetrahedronGeometry( radius, detail );

// Advanced
new THREE.ExtrudeGeometry( shape, options );
new THREE.LatheGeometry( points, segs, thetaStart, thetaLength );
new THREE.ShapeGeometry( shape, curveSegs );
new THREE.TubeGeometry( path, segs, radius, radiusSegs, closed );
new THREE.PolyhedronGeometry( vertices, indices, radius, detail );

// Derived
new THREE.EdgesGeometry( geometry, thresholdAngle );
new THREE.WireframeGeometry( geometry );
```

## InstancedBufferGeometry

For rendering many copies of the same geometry with per-instance transforms:

```js
const geometry = new THREE.InstancedBufferGeometry();
geometry.index = referenceGeometry.index;
geometry.attributes.position = referenceGeometry.attributes.position;
geometry.attributes.normal = referenceGeometry.attributes.normal;

// Per-instance attribute
const offsets = new Float32Array( count * 3 );
for ( let i = 0; i < count; i ++ ) {
	offsets[ i * 3 + 0 ] = Math.random() * 10 - 5;
	offsets[ i * 3 + 1 ] = Math.random() * 10 - 5;
	offsets[ i * 3 + 2 ] = Math.random() * 10 - 5;
}
geometry.setAttribute( 'offset', new THREE.BufferAttribute( offsets, 3 ) );
geometry.instanceCount = count;
```

## InstancedMesh

High-level instancing API:

```js
const mesh = new THREE.InstancedMesh( geometry, material, count );

// Set per-instance transform
const matrix = new THREE.Matrix4();
for ( let i = 0; i < count; i ++ ) {
	matrix.setPosition( x, y, z );
	mesh.setMatrixAt( i, matrix );
}
mesh.instanceMatrix.needsUpdate = true;

// Set per-instance color
const color = new THREE.Color();
for ( let i = 0; i < count; i ++ ) {
	color.setHSL( i / count, 1.0, 0.5 );
	mesh.setColorAt( i, color );
}
// Requires material.vertexColors = true

// Raycasting returns .instanceId
const intersects = raycaster.intersectObject( mesh );
if ( intersects.length > 0 ) {
	const id = intersects[ 0 ].instanceId;
}
```

## Geometry Gotchas

- **Attributes are immutable after first render** — do not change itemSize, array length, or type. Create a new BufferAttribute and replace it: `geometry.setAttribute( 'position', newAttr )`.
- **Call `needsUpdate = true`** — after modifying attribute data in-place: `geometry.attributes.position.needsUpdate = true`.
- **Index buffer type** — if vertex count exceeds 65535, use `Uint32BufferAttribute` for indices.
- **Dispose geometry** — `geometry.dispose()` frees GPU buffers. Always dispose when removing objects.
- **`computeVertexNormals`** — must be called after modifying positions. Use `vertexNormalsNeedUpdate = true` for partial updates.
- **`LineDashedMaterial`** — requires `geometry.computeLineDistances()` before rendering.
- **Geometry merging** — use `BufferGeometryUtils.mergeGeometries()` from addons for combining geometries.
