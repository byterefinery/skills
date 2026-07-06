# Particles

## ParticleContainer

High-performance particle rendering. Can handle 100,000+ particles.

### Key Differences from v7

- Uses `Particle` objects, not `Sprites`
- Particles stored in `particleChildren` array, not `children`
- No bounds calculation — must provide `boundsArea`
- No filters, no children nesting, no events on individual particles
- Configurable dynamic properties for per-frame updates

### Creation

```ts
import { ParticleContainer, Particle } from 'pixi.js';

// Basic
const container = new ParticleContainer({
    texture: particleTexture,
    boundsArea: new Rectangle(0, 0, 800, 600),
    dynamicProperties: {
        position: true,   // Update positions each frame
        rotation: true,   // Update rotations each frame
        color: false,     // Static colors
        vertex: false,    // Static vertices
        uvs: false,       // Static UVs
    },
});

// With initial particles
const container = new ParticleContainer({
    texture: particleTexture,
    particles: [
        new Particle({ texture: particleTexture, x: 100, y: 100 }),
        new Particle({ texture: particleTexture, x: 200, y: 200 }),
    ],
    boundsArea: new Rectangle(0, 0, 800, 600),
});
```

### Particle

Lightweight particle object (not a display object).

```ts
interface IParticle {
    x: number;        // Position X
    y: number;        // Position Y
    scaleX: number;   // Scale X (default: 1)
    scaleY: number;   // Scale Y (default: 1)
    anchorX: number;  // Anchor X (0-1, default: 0.5)
    anchorY: number;  // Anchor Y (0-1, default: 0.5)
    rotation: number; // Rotation in radians
    color: number;    // Color as ABGR (default: 0xFFFFFFFF)
    texture: Texture; // Particle texture
}

// Create particle
const particle = new Particle({
    texture: particleTexture,
    x: 100,
    y: 100,
    scaleX: 2,
    scaleY: 2,
    anchorX: 0.5,
    anchorY: 0.5,
    rotation: Math.PI / 4,
    color: 0xFF0000FF, // ABGR format: alpha, blue, green, red
});
```

### Managing Particles

```ts
// Add particles
container.addParticle(particle);
container.addParticle(p1, p2, p3);

// Remove particles
container.removeParticle(particle);
container.removeParticle(p1, p2);

// Direct array access (faster)
container.particleChildren.push(particle);
container.particleChildren.pop();

// Update particle properties
particle.x += 1;
particle.y += 2;
particle.rotation += 0.1;
particle.color = 0xFFFFFFFF;

// Bulk update in render loop
app.ticker.add(() => {
    const particles = container.particleChildren;
    for (let i = 0; i < particles.length; i++) {
        const p = particles[i];
        p.x += p.velocityX;
        p.y += p.velocityY;
        p.rotation += p.angularVelocity;
        p.life -= 1;
    }
});
```

### Dynamic Properties

Control which properties update each frame:

```ts
interface ParticleProperties {
    vertex?: boolean;   // Dynamic mesh deformation (default: false)
    position?: boolean; // Dynamic positions (default: true)
    rotation?: boolean; // Dynamic rotation (default: false)
    uvs?: boolean;      // Dynamic texture coordinates (default: false)
    color?: boolean;    // Dynamic colors (default: false)
}

// Only position updates
container.dynamicProperties = {
    position: true,
    rotation: false,
    vertex: false,
    uvs: false,
    color: false,
};

// All dynamic
container.dynamicProperties = {
    position: true,
    rotation: true,
    vertex: true,
    uvs: true,
    color: true,
};
```

### Bounds Area

ParticleContainer doesn't calculate bounds — you must provide them:

```ts
// Set bounds area
container.boundsArea = new Rectangle(0, 0, 800, 600);

// Or in constructor
const container = new ParticleContainer({
    boundsArea: new Rectangle(0, 0, 800, 600),
    // ...
});
```

### Custom Shader

```ts
const container = new ParticleContainer({
    texture: particleTexture,
    shader: customParticleShader,
    boundsArea: new Rectangle(0, 0, 800, 600),
});
```

### Particle System Pattern

```ts
class ParticleSystem {
    private container: ParticleContainer;
    private pool: Particle[] = [];
    private active: Particle[] = [];

    constructor(texture: Texture, maxParticles: number) {
        this.container = new ParticleContainer({
            texture,
            boundsArea: new Rectangle(0, 0, 800, 600),
            dynamicProperties: {
                position: true,
                rotation: true,
                color: true,
            },
        });

        // Pre-allocate particles
        for (let i = 0; i < maxParticles; i++) {
            this.pool.push(new Particle({ texture }));
        }
    }

    emit(x: number, y: number, count: number) {
        for (let i = 0; i < count; i++) {
            const particle = this.pool.pop();
            if (!particle) break;

            particle.x = x;
            particle.y = y;
            particle.scaleX = 1;
            particle.scaleY = 1;
            particle.rotation = Math.random() * Math.PI * 2;
            particle.color = 0xFFFFFFFF;

            // Custom properties
            (particle as any).velocityX = (Math.random() - 0.5) * 10;
            (particle as any).velocityY = (Math.random() - 0.5) * 10;
            (particle as any).life = 1;
            (particle as any).decay = 0.01 + Math.random() * 0.02;

            this.active.push(particle);
            this.container.addParticle(particle);
        }
    }

    update() {
        for (let i = this.active.length - 1; i >= 0; i--) {
            const p = this.active[i];
            const life = (p as any).life;

            p.x += (p as any).velocityX;
            p.y += (p as any).velocityY;
            p.rotation += 0.1;

            (p as any).life -= (p as any).decay;

            if ((p as any).life <= 0) {
                this.container.removeParticle(p);
                this.active.splice(i, 1);
                this.pool.push(p);
            }
        }
    }

    get containerRef(): ParticleContainer {
        return this.container;
    }
}

// Usage
const system = new ParticleSystem(particleTexture, 1000);
app.stage.addChild(system.containerRef);

app.ticker.add(() => {
    system.update();
});

// Emit on click
app.stage.eventMode = 'static';
app.stage.on('pointerdown', (e) => {
    system.emit(e.global.x, e.global.y, 50);
});
```

## Particle Performance Tips

- **Use `boundsArea`** — required for correct rendering
- **Minimize dynamic properties** — only enable what changes per frame
- **Object pooling** — reuse Particle objects instead of creating/destroying
- **Direct array access** — `particleChildren` array is faster than add/remove methods
- **Single texture** — all particles should share the same base texture
- **No filters** — ParticleContainer doesn't support filters
- **No children** — ParticleContainer can't have child containers
- **Pre-allocate** — create particles upfront, reuse from pool
- **Batch-friendly** — all particles with same texture batch into one draw call
- **Use `roundPixels: true`** for crisp particle rendering
