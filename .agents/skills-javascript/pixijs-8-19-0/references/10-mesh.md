# Mesh

## Mesh

Custom geometry rendering with shaders. Maximum flexibility for any 2D/3D visual.

### Core Components

Every Mesh needs three things:
1. **Geometry** — vertex positions, UVs, indices, colors, custom attributes
2. **Shader** — vertex + fragment shaders that process the geometry on GPU
3. **Texture** (optional) — texture sampled by the shader

### Creation

```ts
import { Mesh, MeshGeometry, Shader, GlProgram, GpuProgram, UniformGroup, Texture } from 'pixi.js';

// Geometry
const geometry = new MeshGeometry({
    positions: new Float32Array([
        // x, y, u, v, color(r,g,b,a)
        0, 0, 0, 0, 1, 1, 1, 1,
        100, 0, 1, 0, 1, 1, 1, 1,
        100, 100, 1, 1, 1, 1, 1, 1,
        0, 100, 0, 1, 1, 1, 1, 1,
    ]),
    indices: [0, 1, 2, 0, 2, 3], // Two triangles
});

// Shader (WebGL + WebGPU)
const shader = Shader.from({
    gl: {
        vertex: `
            attribute vec2 aPosition;
            attribute vec2 aUV;
            uniform mat3 uProjectionMatrix;
            uniform mat3 uTranslationMatrix;
            varying vec2 vUV;
            void main() {
                gl_Position = vec4((uProjectionMatrix * uTranslationMatrix * vec3(aPosition, 1.0)).xy, 0.0, 1.0);
                vUV = aUV;
            }
        `,
        fragment: `
            precision highp float;
            varying vec2 vUV;
            uniform sampler2D uTexture;
            void main() {
                gl_FragColor = texture2D(uTexture, vUV);
            }
        `,
    },
    gpu: {
        vertex: {
            source: `
                @vertex
                fn main(@builtin(position) position: vec4<f32>,
                         @location(0) uv: vec2<f32>) -> @builtin(position) vec4<f32> {
                    return position;
                }
            `,
            entryPoint: 'main',
        },
        fragment: {
            source: `
                @fragment
                fn main(@location(0) uv: vec2<f32>) -> @location(0) vec4<f32> {
                    return vec4<f32>(uv, 0.0, 1.0);
                }
            `,
            entryPoint: 'main',
        },
    },
    resources: {
        texture: {
            texture: myTexture.source,
            style: myTexture.style,
        },
    },
});

// Create mesh
const mesh = new Mesh({
    geometry,
    shader,
    texture: myTexture,
});

app.stage.addChild(mesh);
```

## MeshGeometry

Defines vertex data for mesh rendering.

```ts
import { MeshGeometry } from 'pixi.js';

const geometry = new MeshGeometry({
    // Required: vertex positions and UVs
    positions: new Float32Array([0, 0, 100, 0, 100, 100, 0, 100]),
    uvs: new Float32Array([0, 0, 1, 0, 1, 1, 0, 1]),

    // Optional: triangle indices
    indices: new Uint16Array([0, 1, 2, 0, 2, 3]),

    // Optional: per-vertex colors
    colors: new Float32Array([1, 1, 1, 1, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 1]),

    // Optional: topology (draw mode)
    topology: 'triangle-list', // 'point-list', 'line-list', 'line-strip', 'triangle-list', 'triangle-strip'

    // Optional: shrink buffers to fit data
    shrinkBuffersToFit: true,
});

// Update geometry
geometry.invalidate();

// Destroy
geometry.destroy();
```

### Interleaved Buffers

For better performance, interleave position + UV + color:

```ts
const geometry = new MeshGeometry({
    // Format: x, y, u, v, r, g, b, a (8 floats per vertex)
    positions: new Float32Array([
        0, 0, 0, 0, 1, 1, 1, 1,
        100, 0, 1, 0, 1, 1, 1, 1,
        100, 100, 1, 1, 1, 1, 1, 1,
        0, 100, 0, 1, 1, 1, 1, 1,
    ]),
    indices: [0, 1, 2, 0, 2, 3],
    size: 8, // 8 floats per vertex
});
```

## MeshPlane

Grid of quads — useful for water effects, terrain, etc.

```ts
import { MeshPlane, PlaneGeometry } from 'pixi.js';

// Simple creation
const mesh = new MeshPlane({
    texture: myTexture,
    width: 400,
    height: 300,
    verticesX: 10,  // Horizontal segments
    verticesY: 8,   // Vertical segments
});

// Manual geometry
const geometry = new PlaneGeometry({
    width: 400,
    height: 300,
    verticesX: 10,
    verticesY: 8,
});

const mesh = new Mesh({
    geometry,
    texture: myTexture,
});

// Animate vertices
app.ticker.add(() => {
    const positions = geometry.positions;
    for (let i = 0; i < positions.length; i += 2) {
        positions[i + 1] += Math.sin(Date.now() / 500 + positions[i] / 50) * 0.5;
    }
    geometry.invalidate();
});
```

## MeshRope

Chain of linked quads — useful for ropes, chains, tentacles.

```ts
import { MeshRope, RopeGeometry } from 'pixi.js';

// Define points
const points = [
    new Point(0, 0),
    new Point(100, 50),
    new Point(200, 0),
    new Point(300, 50),
    new Point(400, 0),
];

// Create rope
const mesh = new MeshRope({
    texture: ropeTexture,
    points,
});

// Animate points
app.ticker.add(() => {
    const time = Date.now() / 1000;
    for (let i = 0; i < points.length; i++) {
        points[i].y = Math.sin(time + i * 0.5) * 30;
    }
    mesh.geometry.invalidate();
});
```

## PerspectiveMesh

3D perspective projection on a plane.

```ts
import { PerspectiveMesh, PerspectivePlaneGeometry } from 'pixi.js';

const mesh = new PerspectiveMesh({
    texture: myTexture,
    width: 400,
    height: 300,
    verticesX: 20,
    verticesY: 20,
    camera: {
        position: new Point(0, 0, 500),
        target: new Point(0, 0, 0),
    },
});
```

## Custom Shaders

### Uniform Groups

```ts
import { UniformGroup } from 'pixi.js';

const uniforms = new UniformGroup({
    uTime: { value: 0, type: 'f32' },
    uResolution: { value: [800, 600], type: 'f32', size: 2 },
    uColor: { value: [1, 0, 0, 1], type: 'f32', size: 4 },
});

// Update uniform
uniforms.uniforms.uTime = Date.now() / 1000;
uniforms.update();
```

### Shader Resources

```ts
const shader = Shader.from({
    gl: { vertex, fragment },
    gpu: { vertex: { source, entryPoint }, fragment: { source, entryPoint } },
    resources: {
        // Texture resource
        myTexture: {
            texture: texture.source,
            style: texture.style,
        },
        // Uniform group
        myUniforms: new UniformGroup({
            uTime: { value: 0, type: 'f32' },
        }),
    },
});
```

### WebGL Shader

```ts
const shader = Shader.from({
    gl: {
        vertex: `
            attribute vec2 aPosition;
            attribute vec2 aUV;
            uniform mat3 uProjectionMatrix;
            uniform mat3 uTranslationMatrix;
            varying vec2 vUV;
            void main() {
                gl_Position = vec4((uProjectionMatrix * uTranslationMatrix *
                    vec3(aPosition, 1.0)).xy, 0.0, 1.0);
                vUV = aUV;
            }
        `,
        fragment: `
            precision highp float;
            varying vec2 vUV;
            uniform sampler2D uTexture;
            uniform float uTime;
            void main() {
                vec2 uv = vUV;
                uv.x += sin(uv.y * 10.0 + uTime) * 0.01;
                gl_FragColor = texture2D(uTexture, uv);
            }
        `,
    },
    resources: {
        myUniforms: new UniformGroup({
            uTime: { value: 0, type: 'f32' },
        }),
    },
});
```

### WebGPU Shader (WGSL)

```ts
const shader = Shader.from({
    gpu: {
        vertex: {
            source: `
                struct VertexInput {
                    @location(0) position: vec2<f32>,
                    @location(1) uv: vec2<f32>,
                }

                @vertex
                fn main(input: VertexInput) -> @builtin(position) vec4<f32> {
                    return vec4<f32>(input.position, 0.0, 1.0);
                }
            `,
            entryPoint: 'main',
        },
        fragment: {
            source: `
                @fragment
                fn main(@location(0) uv: vec2<f32>) -> @location(0) vec4<f32> {
                    return vec4<f32>(uv, 0.0, 1.0);
                }
            `,
            entryPoint: 'main',
        },
    },
});
```

## Mesh Performance Tips

- **Share geometry** — one MeshGeometry shared across multiple Meshes
- **Share shaders** — one Shader shared across multiple Meshes
- **Use interleaved buffers** — better cache coherence
- **Minimize vertex count** — only as many segments as needed
- **Use `topology: 'triangle-strip'`** for fewer indices
- **Call `geometry.invalidate()`** only when data changes
- **Use MeshPlane/MeshRope** instead of raw Mesh for common patterns
- **Avoid creating geometries in render loop** — reuse and update
