# Post-Processing

## WebGL: EffectComposer

The `EffectComposer` chains post-processing passes. WebGL-only.

### Setup

```js
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';

const composer = new EffectComposer( renderer );

// Render the scene
const renderPass = new RenderPass( scene, camera );
composer.addPass( renderPass );

// Color space / tone mapping (REQUIRED for correct output)
const outputPass = new OutputPass();
composer.addPass( outputPass );

// Render
function animate() {
	requestAnimationFrame( animate );
	composer.render(); // NOT renderer.render()
}
```

### Available Passes

```js
// Rendering
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';
import { SavePass } from 'three/addons/postprocessing/SavePass.js';
import { MaskPass, ClearMaskPass } from 'three/addons/postprocessing/MaskPass.js';
import { ClearPass } from 'three/addons/postprocessing/ClearPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';

// Effects
import { BloomPass } from 'three/addons/postprocessing/BloomPass.js';
import { BokehPass } from 'three/addons/postprocessing/BokehPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { FXAAPass } from 'three/addons/postprocessing/FXAAPass.js';
import { SMAAPass } from 'three/addons/postprocessing/SMAAPass.js';
import { SSAOPass } from 'three/addons/postprocessing/SSAOPass.js';
import { GTAOPass } from 'three/addons/postprocessing/GTAOPass.js';
import { SSAARenderPass } from 'three/addons/postprocessing/SSAARenderPass.js';
import { SAOPass } from 'three/addons/postprocessing/SAOPass.js';

// Filters
import { AfterimagePass } from 'three/addons/postprocessing/AfterimagePass.js';
import { BloomPass } from 'three/addons/postprocessing/BloomPass.js';
import { DotScreenPass } from 'three/addons/postprocessing/DotScreenPass.js';
import { FilmPass } from 'three/addons/postprocessing/FilmPass.js';
import { GlitchPass } from 'three/addons/postprocessing/GlitchPass.js';
import { HalftonePass } from 'three/addons/postprocessing/HalftonePass.js';
import { LUTPass } from 'three/addons/postprocessing/LUTPass.js';
import { OutlinePass } from 'three/addons/postprocessing/OutlinePass.js';
import { RenderPixelatedPass } from 'three/addons/postprocessing/RenderPixelatedPass.js';
import { RenderTransitionPass } from 'three/addons/postprocessing/RenderTransitionPass.js';

// Shaders for ShaderPass
import { CopyShader } from 'three/addons/shaders/CopyShader.js';
import { BrightnessContrastShader } from 'three/addons/shaders/BrightnessContrastShader.js';
import { ColorCorrectionShader } from 'three/addons/shaders/ColorCorrectionShader.js';
import { ColorifyShader } from 'three/addons/shaders/ColorifyShader.js';
import { ConvolutionShader } from 'three/addons/shaders/ConvolutionShader.js';
import { DepthLimitedBlurShader } from 'three/addons/shaders/DepthLimitedBlurShader.js';
import { ExposureShader } from 'three/addons/shaders/ExposureShader.js';
import { GammaCorrectionShader } from 'three/addons/shaders/GammaCorrectionShader.js';
import { HorizontalBlurShader } from 'three/addons/shaders/HorizontalBlurShader.js';
import { VerticalBlurShader } from 'three/addons/shaders/VerticalBlurShader.js';
import { HueSaturationShader } from 'three/addons/shaders/HueSaturationShader.js';
import { LuminosityShader } from 'three/addons/shaders/LuminosityShader.js';
import { LuminosityHighPassShader } from 'three/addons/shaders/LuminosityHighPassShader.js';
import { SADAdaptationShader } from 'three/addons/shaders/SADAdaptationShader.js';
import { SobelOperatorShader } from 'three/addons/shaders/SobelOperatorShader.js';
import { TechnicolorShader } from 'three/addons/shaders/TechnicolorShader.js';
import { VelocityBlurShader } from 'three/addons/shaders/VelocityBlurShader.js';
```

### Common Passes

#### Bloom

```js
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';

const bloomPass = new UnrealBloomPass(
	new THREE.Vector2( window.innerWidth, window.innerHeight ),
	1.0,    // strength
	0.4,    // radius
	0.85    // threshold
);
composer.addPass( bloomPass );
```

#### FXAA (Anti-aliasing)

```js
import { FXAAPass } from 'three/addons/postprocessing/FXAAPass.js';

const fxaaPass = new FXAAPass( window.innerWidth, window.innerHeight );
composer.addPass( fxaaPass );
```

#### SSAO

```js
import { SSAOPass } from 'three/addons/postprocessing/SSAOPass.js';

const ssaoPass = new SSAOPass( scene, camera, window.innerWidth, window.innerHeight );
ssaoPass.kernelRadius = 16;
ssaoPass.minDistance = 0.005;
ssaoPass.maxDistance = 0.1;
composer.addPass( ssaoPass );
```

#### Outline

```js
import { OutlinePass } from 'three/addons/postprocessing/OutlinePass.js';

const outlinePass = new OutlinePass(
	new THREE.Vector2( window.innerWidth, window.innerHeight ),
	scene,
	camera
);
outlinePass.edgeStrength = 3.0;
outlinePass.edgeGlow = 0.0;
outlinePass.edgeThickness = 1.0;
outlinePass.pulsePeriod = 0;
outlinePass.visibleEdgeColor.set( 0xffffff );
outlinePass.hiddenEdgeColor.set( 0x000000 );

// Add objects to outline
outlinePass.selectedObjects = [ mesh ];
composer.addPass( outlinePass );
```

#### Custom Shader Pass

```js
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';

const customPass = new ShaderPass( {
	uniforms: {
		tDiffuse: { value: null },
		time: { value: 0 },
	},
	vertexShader: `
		varying vec2 vUv;
		void main() {
			vUv = uv;
			gl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 );
		}
	`,
	fragmentShader: `
		uniform sampler2D tDiffuse;
		uniform float time;
		varying vec2 vUv;
		void main() {
			vec4 color = texture2D( tDiffuse, vUv );
			gl_FragColor = color;
		}
	`,
} );
composer.addPass( customPass );
```

### Pass Properties

```js
pass.enabled = true;       // Enable/disable pass
pass.needsSwap = true;     // Whether pass writes to screen (last pass = true)
pass.renderToScreen = false;
```

### Mask Pass

```js
import { MaskPass, ClearMaskPass } from 'three/addons/postprocessing/MaskPass.js';

// Apply following passes only to masked objects
const maskPass = new MaskPass( scene, camera );
maskPass.clear = true;
maskPass.featherEpsilon = 0.01;
maskPass.featherOffset = 0.01;
composer.addPass( maskPass );

// Add passes that only affect masked region
composer.addPass( someEffectPass );

// Clear mask
const clearMask = new ClearMaskPass();
composer.addPass( clearMask );
```

## WebGPU: RenderPipeline

Node-based post-processing for WebGPURenderer.

```js
import { WebGPURenderer, RenderPipeline, pass } from 'three/webgpu';

const renderer = new WebGPURenderer();
const renderPipeline = new RenderPipeline( renderer );

// Scene pass
const scenePass = pass( scene, camera );

// Chain effects (node-based)
import { bloom, fxaa, toneMapping } from 'three/tsl';

const output = renderOutput( scenePass );
renderPipeline.outputNode = output;
```

### RenderPipeline Properties

```js
renderPipeline.outputNode = node;        // Final output node
renderPipeline.outputColorTransform = true; // Auto tone mapping + color space
renderPipeline.needsUpdate = true;       // Set when output changes
```

### Post-Processing Utils (TSL)

```js
import {
	postProcessing,
	viewport,
	viewportTexture,
	viewportDepthTexture,
	screenUV,
} from 'three/tsl';
```

## Post-Processing Gotchas

- **`OutputPass` is required** — without it, colors are in linear space and look washed out. Always add it as the last pass.
- **Call `composer.render()`, not `renderer.render()`** — mixing causes double rendering.
- **`ShaderPass` needs `tDiffuse`** — the input texture uniform is `tDiffuse`. The pass handles it automatically when using `ShaderPass`.
- **Pass order matters** — effects are applied in order. Bloom before FXAA, for example.
- **`EffectComposer` is WebGL-only** — it uses `WebGLRenderTarget`. For WebGPU, use `RenderPipeline`.
- **Resize handling** — update composer on window resize: `composer.setSize( width, height )`.
- **`OutlinePass.selectedObjects`** — must be an array of `Object3D`. Empty array = no outlines.
- **Performance** — each pass adds a full-screen quad render. Minimize passes. Use `pass.enabled = false` to skip without removing.
- **`SMAAPass` needs search/image files** — provide the path: `smaaPass.search = 'path/to/smaaSearch.png'`.
