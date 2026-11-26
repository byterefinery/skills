# Post-Processing

Two systems exist: `EffectComposer` (WebGL, pass-based, in `three/addons`) and `RenderPipeline` (WebGPU build, node-based, in `three/webgpu`).

## WebGL: EffectComposer

```js
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';

const composer = new EffectComposer( renderer );

// Render the scene
const renderPass = new RenderPass( scene, camera );
composer.addPass( renderPass );

// Tone mapping + color space conversion (add as last pass)
const outputPass = new OutputPass();
composer.addPass( outputPass );

// Render — use composer.render(), NOT renderer.render()
renderer.setAnimationLoop( () => composer.render() );
```

### Available Passes

All from `three/addons/postprocessing/`:

```
RenderPass, ShaderPass, SavePass, MaskPass, ClearMaskPass, ClearPass, OutputPass,
BloomPass, BokehPass, UnrealBloomPass, FXAAPass, SMAAPass, SSAOPass,
GTAOPass, SSAARenderPass, SAOPass,
AfterimagePass, DotScreenPass, FilmPass, GlitchPass, HalftonePass,
LUTPass, OutlinePass, RenderPixelatedPass, RenderTransitionPass
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

#### FXAA

```js
import { FXAAPass } from 'three/addons/postprocessing/FXAAPass.js';
composer.addPass( new FXAAPass() );
```

#### SMAA

```js
import { SMAAPass } from 'three/addons/postprocessing/SMAAPass.js';
composer.addPass( new SMAAPass() ); // search/image textures are bundled
```

#### SSAO

```js
import { SSAOPass } from 'three/addons/postprocessing/SSAOPass.js';

// ( scene, camera, width = 512, height = 512, kernelSize = 32 )
const ssaoPass = new SSAOPass( scene, camera, window.innerWidth, window.innerHeight );
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
outlinePass.selectedObjects = [ mesh ];
composer.addPass( outlinePass );
```

#### LUT (Color Grading)

```js
import { LUTPass } from 'three/addons/postprocessing/LUTPass.js';
import { LUTCubeLoader } from 'three/addons/loaders/LUTCubeLoader.js';

const lutPass = new LUTPass( { lut: null } ); // options object; set lutPass.lut later
const loader = new LUTCubeLoader();
loader.load( 'lookups/Filmic.cube', ( lut ) => {
	lutPass.lut = lut;
} );
composer.addPass( lutPass );
```

#### Custom Shader Pass

```js
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';

// ShaderPass takes a shader object { uniforms, vertexShader, fragmentShader }
const customPass = new ShaderPass( MyShader );
composer.addPass( customPass );
```

`ShaderPass` wires the input texture into the `tDiffuse` uniform automatically.

### Pass Properties

```js
pass.enabled = true;        // Enable/disable pass
pass.needsSwap = true;      // Swap read/write buffers after the pass
```

### Masking

```js
import { MaskPass, ClearMaskPass } from 'three/addons/postprocessing/MaskPass.js';

// Render only masked objects into the mask, then run passes, then clear
const maskPass = new MaskPass( scene, camera );
composer.addPass( maskPass );
composer.addPass( someEffectPass );
composer.addPass( new ClearMaskPass() );
```

## WebGPU: RenderPipeline

Node-based post-processing for `WebGPURenderer`. Pattern from the official `webgpu_postprocessing.html` example:

```js
import * as THREE from 'three/webgpu';
import { pass } from 'three/tsl';
import { dotScreen } from 'three/addons/tsl/display/DotScreenNode.js';
import { rgbShift } from 'three/addons/tsl/display/RGBShiftNode.js';

const renderer = new THREE.WebGPURenderer();
renderer.setPixelRatio( window.devicePixelRatio );
renderer.setSize( window.innerWidth, window.innerHeight );
renderer.setAnimationLoop( animate );
document.body.appendChild( renderer.domElement );

const renderPipeline = new THREE.RenderPipeline( renderer );

const scenePass = pass( scene, camera );
const sceneColor = scenePass.getTextureNode().toInspector( 'Scene Color' );

// Chain TSL effect nodes
const dotScreenPass = dotScreen( sceneColor, 1.57, 0.3 );
const rgbShiftPass = rgbShift( dotScreenPass, 0.001 );

renderPipeline.outputNode = rgbShiftPass;

// In animate(): renderPipeline.render();
```

`PostProcessing` is a deprecated alias of `RenderPipeline` (renamed since r183) — use `RenderPipeline`.

### TSL Display Nodes for Post-Processing

From `three/addons/tsl/display/` (a selection):

```js
import { bloom } from 'three/addons/tsl/display/BloomNode.js';
// bloom( node, strength, radius, threshold )

import { fxaa } from 'three/addons/tsl/display/FXAANode.js';
import { outline } from 'three/addons/tsl/display/OutlineNode.js';
import { ssao } from 'three/addons/tsl/display/SSAONode.js';
import { ssr } from 'three/addons/tsl/display/SSRNode.js';
import { ssgi } from 'three/addons/tsl/display/SSGINode.js';
import { motionBlur } from 'three/addons/tsl/display/MotionBlur.js';
import { lensflare } from 'three/addons/tsl/display/LensflareNode.js';
```

Also in `display/`: `afterImage`, `anaglyphPass`, `bilateralBlur`, `bleachBypass`, `chromaticAberration`, `crt`, `depthAwareBlend`, `denoise`, `film`, `godrays`, `lut3D`, `oITPass`, `pixelationPass`, `recurrentDenoise`, `retroPass`, `smaa`, `ssaaPass`, `taau`, `trAA`, `temporalReproject`, `transition`, `boxBlur`, `hashBlur`, `radialBlur`, `lensDirt`, `shape`.

## Post-Processing Gotchas

- **`OutputPass` is required for EffectComposer** — without it, tone mapping and sRGB conversion are skipped and output looks washed out.
- **Call `composer.render()`, not `renderer.render()`** — mixing both causes double rendering.
- **Resize handling** — update the composer on window resize: `composer.setSize( width, height )`.
- **`EffectComposer` is WebGL-only** — for WebGPU use `RenderPipeline` with TSL nodes.
- **Pass order matters** — effects apply in order (e.g., AO before bloom, FXAA last).
- **Performance** — each pass is a full-screen pass; keep the chain short and disable unused passes with `pass.enabled = false`.
- **`ShaderPass` input is `tDiffuse`** — custom fragment shaders must sample `tDiffuse`.
