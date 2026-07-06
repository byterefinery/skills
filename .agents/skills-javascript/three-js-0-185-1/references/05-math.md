# Math

## Vector2

```js
const v = new THREE.Vector2( x, y );
v.set( x, y );
v.copy( source );
v.clone();
v.add( v2 );           // v += v2
v.sub( v2 );           // v -= v2
v.multiply( v2 );      // component-wise
v.divide( v2 );
v.multiplyScalar( s );
v.addScaledVector( v2, s ); // v += v2 * s
v.dot( v2 );
v.cross( v2 );         // Returns scalar (2D cross product)
v.length();
v.lengthSq();
v.normalize();
v.distanceTo( v2 );
v.distanceToSquared( v2 );
v.angle();             // Angle in radians from +X axis
v.lerp( v2, t );
v.lerpVectors( v1, v2, t );
v.applyMatrix3( m );
v.applyMatrix4( m );   // Perspective divide
v.project( camera );   // World to NDC
v.unproject( camera ); // NDC to world
v.onAxis( axis );
v.floor();
v.ceil();
v.round();
v.roundToZero();
v.truncate( maxDistance );
v.setLength( length );
v.rotateAround( center, angle );
v.reflect( normal );
v.min( v2 );           // Component-wise min
v.max( v2 );           // Component-wise max
v.clamp( min, max );
v.clampLength( min, max );
v.randomDirection();
```

## Vector3

```js
const v = new THREE.Vector3( x, y, z );
// All Vector2 methods plus:
v.cross( v2 );              // Vector cross product (modifies v)
v.crossVectors( a, b );     // v = a × b
v.projectOnVector( v2 );
v.projectOnPlane( planeNormal );
v.rejectFromPlane( planeNormal );
v.dot( v2 );
v.setFromMatrixColumn( m, index );
v.setFromMatrixPosition( m ); // Extract translation
v.setFromMatrixScale( m );
v.applyQuaternion( q );
v.applyMatrix4( m );
v.transformDirection( m );   // For direction vectors (no translation)
v.applyEuler( euler );
v.applyAxisAngle( axis, angle );
```

## Vector4

```js
const v = new THREE.Vector4( x, y, z, w );
v.applyMatrix4( m );
v.setComponent( index, value );
v.getComponent( index );
```

## Matrix3 / Matrix4

```js
const m = new THREE.Matrix4();
m.identity();
m.copy( source );
m.clone();
m.multiply( m2 );            // m *= m2
m.premultiply( m2 );         // m = m2 * m
m.multiplyScalar( s );
m.determinant();
m.invert();                  // May fail for singular matrices
m.transpose();
m.equals( m2 );

// Transformations
m.makeTranslation( x, y, z );
m.makeRotationX( theta );
m.makeRotationY( theta );
m.makeRotationZ( theta );
m.makeRotationFromQuaternion( q );
m.makeRotationFromEuler( euler );
m.makeScale( x, y, z );
m.makeRotationAxis( axis, angle );

// Composition
m.compose( position, quaternion, scale );
m.decompose( position, quaternion, scale );

// Projection
m.makePerspective( left, right, top, bottom, near, far );
m.makeFrustum( left, right, top, bottom, near, far );
m.makeOrthographic( left, right, top, bottom, near, far );

// LookAt
m.lookAt( eye, target, up );

// Extraction
m.getPosition( target );
m.getRotation( targetQuaternion );
m.getScale( targetVector );
m.getMaxScaleOnAxis();

// Element access
m.elements;           // Float64Array of 16 elements (column-major)
m.set( n11, n12, ... ); // Set all 16 elements
m.setFromArray( array );
m.toArray( array, arrayOffset );

// Matrix3 (for normals, UV transforms)
const m3 = new THREE.Matrix3();
m3.getNormalMatrix();     // From Matrix4
m3.multiply( m2 );
m3.invert();
```

## Quaternion

```js
const q = new THREE.Quaternion();
q.identity();
q.set( x, y, z, w );
q.copy( source );
q.clone();
q.multiply( q2 );
q.premultiply( q2 );
q.slerp( q2, t );         // Spherical interpolation
q.slerpQuaternions( q1, q2, t );
q.rotateTowards( target, step );
q.angleTo( q2 );
q.shortestPathQuaternions( q1, q2 );

// From other representations
q.setFromEuler( euler );
q.setFromAxisAngle( axis, angle );
q.setFromRotationMatrix( m );
q.setFromUnitVectors( vFrom, vTo );

// Application
q.multiplyVectors( v );   // Rotate vector by quaternion
```

**Prefer quaternions over Euler for interpolation** — avoids gimbal lock and produces smooth rotations.

## Euler

```js
const euler = new THREE.Euler( x, y, z, order );
// order: 'XYZ' (default), 'YXZ', 'ZXY', 'ZYX', 'YZX', 'XZY'
euler.setFromQuaternion( q, order );
euler.setFromRotationMatrix( m, order );
```

**Rotation order matters:**
- `'XYZ'` — default, good for general objects
- `'YXZ'` — camera-like (pitch, yaw, roll), reduces gimbal lock risk
- `'YXY'`, `'ZXZ'` — for specific mechanical joints

## Color

```js
const color = new THREE.Color();
color.set( 0xff0000 );            // Hex
color.set( '#ff0000' );           // CSS hex
color.set( 'red' );               // CSS named color
color.set( 'rgb(255, 0, 0)' );    // CSS rgb
color.set( 'hsl(0, 100%, 50%)' ); // CSS hsl
color.setRGB( r, g, b );          // Linear [0, 1]
color.setScalar( s );             // Grayscale
color.setHex( hex );

// Manipulation
color.clone();
color.copy( source );
color.lerp( color2, t );
color.lerpColors( c1, c2, t );
color.offsetHSL( h, s, l );
color.multiply( color2 );
color.multiplyScalar( s );
color.add( color2 );
color.sub( color2 );
color.dot( color2 );
color.equals( color2 );

// Conversion
color.getHex();
color.getHexString();
color.getStyle();                 // CSS string
color.getCSSColorSpace();
color.convertSRGBToLinear();
color.convertLinearToSRGB();

// Three.js color space conversion
THREE.ColorManagement.convert( color, sourceSpace, targetSpace );
```

## MathUtils

```js
THREE.MathUtils.degToRad( degrees );
THREE.MathUtils.radToDeg( radians );
THREE.MathUtils.degToRad = Math.PI / 180;  // DEG2RAD constant
THREE.MathUtils.radToDeg = 180 / Math.PI;  // RAD2DEG constant

THREE.MathUtils.clamp( value, min, max );
THREE.MathUtils.clamp01( value );
THREE.MathUtils.euclideanModulo( x, m );
THREE.MathUtils.lerp( x, y, t );
THREE.MathUtils.mapLinear( value, inputMin, inputMax, outputMin, outputMax );
THREE.MathUtils.smoothstep( value, min, max );
THREE.MathUtils.randFloat( min, max );
THREE.MathUtils.randFloatSpread( spread );
THREE.MathUtils.seedRandom( seed ); // Seeded random

// Generate UUID
THREE.MathUtils.generateUUID();
```

## Ray

```js
const ray = new THREE.Ray( origin, direction );
ray.at( t, target );              // Point on ray at distance t
ray.lookAt( v );                   // Point ray at vector
ray.recast( t );                   // Set origin to point at t
ray.closestPointToPoint( point, target );
ray.distanceToPoint( point );
ray.intersectPlane( plane, target );
ray.isIntersectionSphere( sphere );
ray.intersectSphere( sphere, target );
ray.intersectTriangle( a, b, c, backfaceCulling, target );
```

## Plane

```js
const plane = new THREE.Plane( normal, constant );
// Or: new THREE.Plane( a, b, c, d ) for ax + by + cz + d = 0
plane.setFromNormalAndCoplanarPoint( normal, point );
plane.setFromCoplanarPoints( a, b, c );
plane.normal;
plane.constant;
plane.distanceToPoint( point );
plane.distanceToSphere( sphere );
plane.projectPoint( point, target );
plane.intersectLine( line, target );
plane.intersectRay( ray, target );
plane.applyMatrix4( m );
plane.copySign( plane2 ); // Make normals point in same direction
```

## Box2 / Box3

```js
// 2D bounding box
const box2 = new THREE.Box2();
box2.setFromPoints( points );
box2.isEmpty();
box2.min; box2.max;
box2.getCenter( target );
box2.getSize( target );
box2.intersectsBox( box2 );
box2.containsPoint( point );
box2.containsBox( box2 );
box2.clone();
box2.copy( source );
box2.union( box2 );
box2.intersect( box2 );
box2.expandByPoint( point );
box2.expandByVector( size );
box2.expandByScalar( scalar );

// 3D bounding box
const box3 = new THREE.Box3();
box3.setFromObject( object );
box3.getBoundingSphere( sphere );
box3.intersectsSphere( sphere );
box3.intersectsBox( box3 );
box3.containsPoint( point );
box3.containsBox( box3 );
box3.intersectsRay( ray );
box3.getSize( target );
```

## Sphere

```js
const sphere = new THREE.Sphere( center, radius );
sphere.intersectsSphere( sphere2 );
sphere.intersectsBox( box3 );
sphere.containsPoint( point );
sphere.isEmpty();
sphere.getBoundingBox( box3 );
```

## Frustum

```js
const frustum = new THREE.Frustum();
frustum.setFromProjectionMatrix( matrix );
frustum.intersectsSphere( sphere );
frustum.containsPoint( point );
frustum.planes; // Array of 6 Plane
```

## Triangle

```js
const triangle = new THREE.Triangle( a, b, c );
triangle.getArea();
triangle.getMidpoint( target );
triangle.getNormal( target );
triangle.getPlane( plane );
triangle.containsPoint( point );
triangle.intersectsSphere( sphere );
triangle.closestPointToPoint( point, target );
triangle.barycoordFromPoint( point, target );
triangle.sign(); // Winding sign
```
