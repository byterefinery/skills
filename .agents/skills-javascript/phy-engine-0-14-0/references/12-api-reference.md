# API Reference

## phy (Engine Instance)

### Initialization

| Method | Description |
|--------|-------------|
| `phy.init(options)` | Initialize physics engine backend |
| `phy.set(options)` | Configure global simulation settings |
| `phy.start(options)` | Begin physics simulation |
| `phy.ready()` | Trigger ready callback |

### Animation Loop

| Method | Description |
|--------|-------------|
| `phy.doStep(stamp)` | Gate physics step to configured FPS |
| `phy.step()` | Sync visual objects with physics state |

### Object Management

| Method | Description |
|--------|-------------|
| `phy.add(options)` | Add object to simulation. Returns Object3D. |
| `phy.adds(array)` | Add multiple objects. |
| `phy.remove(name|array)` | Remove object(s) from simulation. |
| `phy.removes(array)` | Remove multiple objects. |
| `phy.change(options|array)` | Change properties of existing object(s). |
| `phy.changes(array)` | Batch property changes. |
| `phy.byName(name)` | Look up object by name. Returns Object3D or null. |

### Physics Control

| Method | Description |
|--------|-------------|
| `phy.pause(true/false)` | Pause/resume simulation. |
| `phy.getPause()` | Get pause state. |
| `phy.reset(callback)` | Full reset, calls callback when done. |
| `phy.clear(callback)` | Alias for reset. |
| `phy.dispose()` | Full cleanup, terminates worker. |
| `phy.explosion(position, radius, force)` | Apply radial impulse to all bodies. |

### Collision

| Method | Description |
|--------|-------------|
| `phy.activeContact()` | Enable contact data flow. |
| `phy.addCollision(options)` | Add collision monitoring for a body. |
| `phy.removeCollision(name)` | Remove collision monitoring. |

### Vehicles

| Method | Description |
|--------|-------------|
| `phy.vehicle(options)` | Create vehicle (RayCar, Kart, Helicopter). |

### Characters

| Method | Description |
|--------|-------------|
| `phy.autoRagdoll(options)` | Create automatic ragdoll from skeleton. |

### Camera

| Method | Description |
|--------|-------------|
| `phy.setControl(controls)` | Set camera controls reference. |
| `phy.getControl()` | Get camera controls. |
| `phy.follow(name|Object3D, options)` | Start following a target. |
| `phy.getCamera(options)` | Get camera object. |
| `phy.setCamera(options)` | Move camera. |
| `phy.getCurrentCharacterPosition()` | Get follow target position. |

### Input

| Method | Description |
|--------|-------------|
| `phy.setKey(index, value)` | Set key state. |
| `phy.getKey()` | Get key state object. |
| `phy.getUser()` | Get user input reference. |
| `phy.control(name)` | Take/release control of character/vehicle. |
| `phy.takeControl(name)` | Alias for control. |

### Timing

| Method | Description |
|--------|-------------|
| `phy.getTime()` | Current timestamp. |
| `phy.readTime(t)` | Format timestamp as readable string. |
| `phy.getDelta()` | Delta time for current frame. |
| `phy.getElapsedTime()` | Total elapsed simulation time. |
| `phy.getDelta2()` | Physics engine delta time. |
| `phy.getElapsedTime2()` | Physics engine elapsed time. |
| `phy.setTimeout(fn, time, single)` | Internal timeout (respects pause). |
| `phy.cleartimout()` | Clear internal timeout. |

### Performance

| Method | Description |
|--------|-------------|
| `phy.getFps()` | Current FPS (string). |
| `phy.getMs()` | Current step time in ms (string). |
| `phy.getGpu()` | GPU usage percentage (string). |
| `phy.getSetting()` | Current settings object. |
| `phy.getTimeTest()` | Get timing test data. |

### Materials

| Method | Description |
|--------|-------------|
| `phy.material(options)` | Create a material. |
| `phy.addMaterial(material, direct)` | Register a material. |
| `phy.getMaterial(name)` | Get material by name. |
| `phy.getMat(name)` | Alias for getMaterial. |
| `phy.getMatRef()` | Get material manager reference. |
| `phy.getMaterialList()` | Get all registered materials. |
| `phy.changeRenderMode(mode)` | Change render mode. |
| `phy.useRealLight(options)` | Enable real lighting. |
| `phy.setExtendShader(fn)` | Set shader extension function. |
| `phy.directIntensity(value)` | Set direct light intensity. |
| `phy.setEnvmapIntensity(value)` | Set envmap intensity. |

### Textures

| Method | Description |
|--------|-------------|
| `phy.texture(options)` | Load a texture. |
| `phy.texture2(options)` | Async texture loading. |
| `phy.getTexture(name, options)` | Get cached texture. |

### Resources (Pool)

| Method | Description |
|--------|-------------|
| `phy.load(urls, callback, path, msg)` | Load resources. |
| `phy.get(name, type)` | Get cached resource. |
| `phy.getMesh(obj, keepMaterial, multiMaterialGroup)` | Extract mesh from GLB. |
| `phy.getGlb(obj, keepMaterial, multiMaterialGroup)` | Extract GLB data. |
| `phy.getGlbMaterial(obj)` | Extract materials from GLB. |
| `phy.getGroup(obj)` | Get group from resource. |
| `phy.getScript(name)` | Get cached script. |
| `phy.preload(urls, callback)` | Preload avatar resources. |
| `phy.setDracoPath(src)` | Set Draco decoder path. |
| `phy.addMorph(model, morph, normal, relative)` | Add morph targets. |
| `phy.applyMorph(modelName, meshes, normal, relative)` | Apply morph targets. |
| `phy.poolDispose()` | Dispose pool resources. |

### Geometry

| Method | Description |
|--------|-------------|
| `phy.getGeometryRef(options, body, material)` | Get geometry reference for body. |

### Scene

| Method | Description |
|--------|-------------|
| `phy.getScene()` | Get phy_scene group. |
| `phy.setContent(scene)` | Set parent three.js scene. |
| `phy.resize({ h, w })` | Resize viewport. |
| `phy.makeView()` | Create view. |

### Debug

| Method | Description |
|--------|-------------|
| `phy.addDebuger()` | Add debug visualization. |
| `phy.removeDebuger()` | Remove debug visualization. |
| `phy.debugMode(bool)` | Enable/disable debug mode. |
| `phy.setDebugMode(bool)` | Alias for debugMode. |

### Mouse

| Method | Description |
|--------|-------------|
| `phy.activeMouse(controller, mode)` | Activate mouse interaction. |
| `phy.mouseMode(mode, options)` | Set mouse interaction mode. |
| `phy.getMouse()` | Get mouse reference. |

### Particles

| Method | Description |
|--------|-------------|
| `phy.initParticleEngine()` | Initialize particle system. |
| `phy.addParticle(options)` | Add particle emitter. |
| `phy.getParticle(name)` | Get particle emitter by name. |

### Soft Bodies

| Method | Description |
|--------|-------------|
| `phy.addSoftSolver(options)` | Add soft body solver. |
| `phy.updateSoftSolver()` | Update all soft solvers. |
| `phy.clearSoftSolver()` | Clear all soft solvers. |

### UI

| Method | Description |
|--------|-------------|
| `phy.addButton(options)` | Add UI button. |
| `phy.addText(options)` | Add text field. |
| `phy.clearText()` | Clear all text fields. |
| `phy.addGrass(options)` | Add grass visualization. |

### Misc

| Method | Description |
|--------|-------------|
| `phy.morph(obj, name, value)` | Set morph target influence. |
| `phy.screenshot()` | Take screenshot (opens new window). |
| `phy.getBreaker()` | Get fracture/breaker tool. |
| `phy.setColorChecker(mesh)` | Set color checker reference. |
| `phy.getColorChecker()` | Get color checker reference. |
| `phy.addSpeech(text)` | Add speech recognition. |
| `phy.clearSpeech()` | Clear speech recognition. |
| `phy.addEnvmap(options)` | Add environment map. |
| `phy.setMaxFps(value)` | Set max FPS. |
| `phy.setMaxAnisotropy(value)` | Set max anisotropy. |
| `phy.setRenderer(renderer)` | Set three.js renderer. |
| `phy.setPrevUpdate(fn)` | Set pre-update callback. |
| `phy.setPostUpdate(fn)` | Set post-update callback. |
| `phy.setAzimut(fn)` | Set azimuth function. |
| `phy.getAzimut()` | Get current azimuth. |
| `phy.addWiggle(options)` | Add wiggle effect. |
| `phy.disposeTmp()` | Dispose temporary meshes/textures. |
| `phy.clearGarbage()` | Clear garbage collection list. |
| `phy.clearBody()` | Clear all bodies. |
| `phy.clearInstance()` | Clear all instanced meshes. |
| `phy.getBodyRef()` | Get body manager reference. |
| `phy.getCharacterRef()` | Get character manager reference. |
| `phy.getAllBody(name)` | Get all body list. |
| `phy.getTransform(body)` | Get body transform (position, up, right, forward). |

## phy.set() Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `fps` | Number | `60` | Physics step frequency |
| `substep` | Number | `1` | Substeps per frame |
| `gravity` | Array | `[0, -9.81, 0]` | Gravity vector |
| `fixe` | Boolean | `true` | Fixed timestep |
| `full` | Boolean | `false` | Full velocity tracking |
| `worldScale` | Number | `1` | World scale factor |
| `jointVisible` | Boolean | `false` | Show joint debug |
| `key` | Boolean | — | Enable key input |

## phy.add() Body Options

| Option | Type | Description |
|--------|------|-------------|
| `name` | String | Object name (auto-generated if omitted) |
| `type` | String | Shape type (box, sphere, cylinder, capsule, etc.) |
| `size` | Array | Dimensions `[x, y, z]` or `[radius]` for sphere |
| `pos` | Array | Position `[x, y, z]` |
| `rot` | Array | Euler rotation in degrees `[x, y, z]` |
| `quat` | Array | Quaternion `[x, y, z, w]` |
| `mass` | Number | Explicit mass |
| `density` | Number | Density (mass = density × volume) |
| `kinematic` | Boolean | Kinematic body |
| `sleep` | Boolean | Start sleeping |
| `visible` | Boolean | Show visual mesh |
| `shadow` | Boolean | Cast/receive shadows |
| `material` | String/Material | Material name or THREE.Material |
| `ray` | Boolean | Enable raycasting |
| `collision` | Boolean | Participate in collisions |
| `mesh` | Object3D | Replace visual with custom mesh |
| `meshPos` | Array | Custom mesh position offset |
| `meshRot` | Array | Custom mesh rotation |
| `meshScale` | Array/Number | Custom mesh scale |
| `instance` | String | Instance group name |
| `breakable` | Boolean | Enable fracture |
| `breakOption` | Array | Fracture parameters |
| `radius` | Number | Chamfer radius for box/cylinder |
| `seg` | Number | Segment count for cylinder/capsule |
| `helper` | Boolean | Show helper visualization |
| `hcolor` | Array | Helper color |
| `hcolor2` | Array | Helper highlight color |
| `shapes` | Array | Sub-shapes for compound bodies |
| `shape` | BufferGeometry | Geometry for convex/mesh bodies |
| `massCenter` | Array | Center of mass offset |
| `renderOrder` | Number | Render order |
| `unicMat` | Boolean | Clone material uniquely |
| `randomColor` | Boolean | Random color for instances |
| `speedMat` | Boolean | Color by velocity for instances |
| `sizeByInstance` | Boolean | Vary size per instance |
| `autoUV` | Boolean | Auto-generate UVs |
| `wake` | Boolean | Wake from sleep |
| `getVelocity` | Boolean | Track velocity |
| `flags` | Number | PhysX collision flags |
| `mask` | Number | Oimo/Havok collision mask |
| `solver` | String | Associate with articulation solver |
| `bone` | String | Bone reference |
| `id` | Number | Custom ID |
| `parent` | String/Object3D | Parent object |
| `onlyMakeMesh` | Boolean | Create mesh only, no physics |
| `debug` | Boolean | Debug mode |
| `auto` | Boolean | Auto matrix update |
| `nofullmat` | Boolean | Don't apply material to all children |
| `noClone` | Boolean | Don't clone mesh |
| `bounce` | Number | Restitution (alias for restitution) |
| `restitution` | Number | Bounce restitution |

## phy.add() Joint Options

| Option | Type | Description |
|--------|------|-------------|
| `type` | String | Joint type (hinge, prismatic, etc.) |
| `mode` | String | Joint mode (alias for type) |
| `b1` | String/Object3D | First body |
| `b2` | String/Object3D | Second body |
| `pos1` | Array | Local anchor on body1 |
| `pos2` | Array | Local anchor on body2 |
| `axis1` | Array | Rotation axis on body1 |
| `axis2` | Array | Rotation axis on body2 |
| `quat1` | Array | Quaternion orientation on body1 |
| `quat2` | Array | Quaternion orientation on body2 |
| `worldAnchor` | Array | World-space anchor point |
| `worldAxis` | Array | World-space axis |
| `worldQuat` | Array | World-space quaternion |
| `limit` | Array | Joint limits |
| `lm` | Array | Alias for limit |
| `visible` | Boolean | Show debug visualization |

## phy.add() Ray Options

| Option | Type | Description |
|--------|------|-------------|
| `type` | String | `'ray'` |
| `begin` | Array | Start point |
| `end` | Array | End point |
| `parent` | String/Object3D | Parent body |
| `callback` | Function | Hit callback |
| `visible` | Boolean | Show ray line |
| `noRotation` | Boolean | Ignore parent rotation |

## phy.add() Contact Options

| Option | Type | Description |
|--------|------|-------------|
| `type` | String | `'contact'` |
| `b1` | String | First body name |
| `b2` | String | Second body name |
| `always` | Boolean | Callback even when not in contact |
| `callback` | Function | Contact callback |
| `ignore` | Array | Bodies to ignore |

## phy.add() Vehicle Options

| Option | Type | Description |
|--------|------|-------------|
| `type` | String | `'vehicle'` |
| `mass` | Number | Total mass |
| `size` | Array | Chassis size |
| `massCenter` | Array | Center of mass |
| `chassisPos` | Array | Chassis visual offset |
| `numWheel` | Number | Number of wheels (2 or 4) |
| `radius` | Number | Front wheel radius |
| `radiusBack` | Number | Rear wheel radius |
| `deep` | Number | Front wheel depth |
| `deepBack` | Number | Rear wheel depth |
| `wPos` | Array | Wheel positions |
| `maxSteering` | Number | Max steering angle |
| `incSteering` | Number | Steering increment |
| `s_travel` | Number | Suspension travel |
| `chassisMesh` | Object3D | Chassis visual |
| `wheelMesh` | Object3D | Wheel visual |
| `suspensionMesh` | Object3D | Suspension visual |
| `brakeMesh` | Object3D | Brake disc visual |
| `chassisShape` | BufferGeometry | Custom chassis shape |
| `meshScale` | Number | Visual scale |
| `ray` | Boolean | Enable raycasting |
| `debug` | Boolean | Debug mode |

## phy.add() Character Options

| Option | Type | Description |
|--------|------|-------------|
| `type` | String | `'character'` |
| `radius` | Number | Character radius |
| `height` | Number | Character height |
| `floating` | Boolean | Enable floating mode |
| `useImpulse` | Boolean | Use impulse movement |
| `isPlayer` | Boolean | Mark as player |
| `autoLOD` | Boolean | Automatic LOD |
| `mesh` | Object3D | Character model |

## phy.add() Terrain Options

| Option | Type | Description |
|--------|------|-------------|
| `type` | String | `'terrain'` |
| `size` | Array | `[width, depth]` |
| `heightData` | Float32Array | Height values |
| `sample` | Number | Grid resolution |
| `zone` | Number | Collision margin |
| `material` | Material | Terrain material |

## phy.add() Solver Options

| Option | Type | Description |
|--------|------|-------------|
| `type` | String | `'solver'` |
| `needData` | Boolean | Enable data feedback |

## phy.add() Soft Body Options

| Option | Type | Description |
|--------|------|-------------|
| `type` | String | `softCloth`, `softRope`, `softMesh`, etc. |
| `size` | Array | Dimensions |
| `div` | Array | Cloth divisions `[x, z]` |
| `numSeg` | Number | Rope segments |
| `radius` | Number | Rope radius |
| `numRad` | Number | Rope radial segments |
| `shape` | BufferGeometry | Geometry for mesh types |
| `start` | Array | Rope start point |
| `end` | Array | Rope end point |
| `path` | Curve | Custom rope path |
