# C++/JavaScript Interop — Emscripten 6.0.1

## Table of Contents

- [Calling C from JavaScript](#calling-c-from-javascript)
- [Calling JavaScript from C/C++](#calling-javascript-from-cc)
- [Embind (C++ Bindings)](#embind-c-bindings)
- [emscripten::val (JS from C++)](#emscriptenval-js-from-c)
- [Memory Access from JavaScript](#memory-access-from-javascript)
- [JS Library Files](#js-library-files)
- [Function Pointers and addFunction](#function-pointers-and-addfunction)
- [Function Signatures](#function-signatures)
- [Environment Variables](#environment-variables)
- [Emnapi (Node-API)](#emnapi-node-api)

## Calling C from JavaScript

### ccall — One-Shot Call

```javascript
var result = Module.ccall(
  'function_name',   // C function name (no underscore)
  'number',          // return type: 'number', 'string', 'array', or null
  ['number', 'string'], // argument types
  [42, 'hello']      // argument values
);
```

Export with `-sEXPORTED_RUNTIME_METHODS=ccall` if used from external scripts or console.

### cwrap — Reusable Wrapper

```javascript
// Create wrapper
var my_func = Module.cwrap('my_func', 'number', ['number', 'string']);

// Call multiple times
my_func(10, 'hello');
my_func(20, 'world');
```

### Direct Function Calls

Functions are accessible with underscore prefix. No type conversion — pass primitives directly:

```javascript
// Direct call (fastest)
Module._my_function(42);

// With string argument (manual conversion)
var ptr = Module.stringToNewUTF8('hello');
Module._takes_string(ptr);
Module._free(ptr);  // Always free!

// With return string
var resultPtr = Module._returns_string();
var str = Module.UTF8ToString(resultPtr);
// Do NOT free strings returned from C — they are managed by the runtime
```

### Type Mapping

| C Type | JavaScript ccall/cwrap Type |
|--------|--------------------------|
| `int`, `float`, `double`, `pointer` | `'number'` |
| `char*` (string) | `'string'` |
| `void` | `null` |
| Array/TypedArray | `'array'` |

### Embind Exports

Embind-bound functions are accessed directly on Module without underscore prefix:

```javascript
Module.lerp(1, 2, 0.5);
var obj = new Module.MyClass(10, 'hello');
obj.method();
obj.delete();  // Free C++ object
```

## Calling JavaScript from C/C++

### EM_ASM — Inline JavaScript

```c
#include <emscripten.h>

// No return, no args
EM_ASM(alert('hello'));

// With args ($0, $1, etc.)
EM_ASM({
  console.log('value: ' + $0 + ', text: ' + UTF8ToString($1));
}, 42, "hello");

// Return int
int x = EM_ASM_INT({ return $0 + 1; }, 100);

// Return double
double d = EM_ASM_DOUBLE({ return Math.sin($0); }, 3.14);

// Return pointer
char* str = (char*)EM_ASM_PTR({
  return stringToNewUTF8('hello from JS');
});
free(str);  // Must free!
```

**Important**: Use single quotes inside `EM_ASM` blocks. Double quotes cause C preprocessor issues.

### EM_JS — Declare JS Functions in C

```c
// Declare a JS function callable from C
EM_JS(void, js_alert, (const char* msg), {
  alert(UTF8ToString(msg));
});

EM_JS(int, js_get_value, (), {
  return 42;
});

EM_JS(char*, js_get_string, (), {
  return stringToNewUTF8('hello from JS');
});

// Usage
int main() {
  js_alert("Hello!");
  int val = js_get_value();
  char* str = js_get_string();
  printf("%s\n", str);
  free(str);  // Must free stringToNewUTF8 results!
  return 0;
}
```

### EM_ASYNC_JS — Async JS Functions (requires Asyncify)

```c
#include <emscripten.h>

EM_ASYNC_JS(int, do_fetch, (const char* url), {
  out("fetching...");
  const response = await fetch(UTF8ToString(url));
  const text = await response.text();
  out("got response");
  return 42;
});

int main() {
  // This blocks until the fetch completes (Asyncify handles suspension)
  do_fetch("http://example.com");
  printf("fetch done\n");
  return 0;
}
```

### MAIN_THREAD_EM_ASM — Proxy to Main Thread

For use in pthreads to call JS on the main browser thread:

```c
// Synchronous proxy (blocks until main thread completes)
MAIN_THREAD_EM_ASM({
  document.getElementById('output').textContent = 'hello';
});

int result = MAIN_THREAD_EM_ASM_INT({
  return window.innerWidth;
});

// Async proxy (fire-and-forget)
MAIN_THREAD_ASYNC_EM_ASM({
  console.log('ran on main thread');
});
```

### emscripten_run_script

```c
#include <emscripten.h>

// Execute arbitrary JS (uses eval)
emscripten_run_script("console.log('hello')");

// With return value
int result = emscripten_run_script_int("2 + 2");

// Returns string (shared buffer — copy if needed)
char* str = emscripten_run_script_string("JSON.stringify({a: 1})");
```

## Embind (C++ Bindings)

### Basic Setup

```cpp
#include <emscripten/bind.h>

using namespace emscripten;

float lerp(float a, float b, float t) {
    return (1 - t) * a + t * b;
}

EMSCRIPTEN_BINDINGS(my_module) {
    function("lerp", &lerp);
}
```

Compile with `-lembind`. Access from JS: `Module.lerp(1, 2, 0.5)`.

### Binding Classes

```cpp
class MyClass {
public:
    MyClass(int x, std::string y) : x(x), y(y) {}
    void incrementX() { ++x; }
    int getX() const { return x; }
    void setX(int x_) { x = x_; }
    static std::string getString(const MyClass& inst) { return inst.y; }
private:
    int x;
    std::string y;
};

EMSCRIPTEN_BINDINGS(my_class) {
    class_<MyClass>("MyClass")
        .constructor<int, std::string>()
        .function("incrementX", &MyClass::incrementX)
        .property("x", &MyClass::getX, &MyClass::setX)
        .class_function("getString", &MyClass::getString)
        ;
}
```

JS usage:
```javascript
var obj = new Module.MyClass(10, "hello");
obj.incrementX();
console.log(obj.x);  // 11
obj.x = 20;
Module.MyClass.getString(obj);  // "hello"
obj.delete();  // Free C++ object
```

### Memory Management

- **Always call `.delete()`** on C++ objects created or returned from JS
- Use `try/finally` to guarantee cleanup:

```javascript
function myFunc() {
    const obj = new Module.MyClass;
    try {
        obj.method();
        if (condition) return;  // early return
        riskyOperation();
    } finally {
        obj.delete();  // Always called
    }
}
```

- Use `using` for automatic cleanup (Explicit Resource Management):

```javascript
using obj = new Module.MyClass;
obj.method();
// obj.delete() called automatically at end of scope
```

### Reference Counting and Cloning

```javascript
const obj = new Module.MyClass;  // refCount = 1
asyncProcess(obj.clone(), 5000); // refCount = 2
obj.delete();                     // refCount = 1
// After asyncProcess: refCount = 0 → object deleted
```

### Return Value Policies

```cpp
EMSCRIPTEN_BINDINGS(module) {
    // Default: copy for value/ref, not allowed for pointer
    function("createData", &createData);

    // Take ownership: JS owns the object, must delete
    function("createOwned", &createOwned, return_value_policy::take_ownership());

    // Reference: C++ owns, don't delete from JS
    function("getReference", &getReference, return_value_policy::reference());
}
```

| Return Type | Default | take_ownership | reference |
|------------|---------|---------------|-----------|
| Value (`T`) | copy, JS must delete | move, JS must delete | not allowed |
| Reference (`T&`) | copy, JS must delete | move, JS must delete | none, C++ owns |
| Pointer (`T*`) | not allowed | none, JS must delete | none, C++ owns |

### Raw Pointers

```cpp
function("passThrough", &passThrough, allow_raw_pointers());
function("create", &create, return_value_policy::take_ownership());
```

### Smart Pointers

```cpp
EMSCRIPTEN_BINDINGS(smart_ptrs) {
    class_<C>("C")
        .smart_ptr_constructor("C", &std::make_shared<C>)
        ;
}
```

### Value Types (No Manual Memory Management)

```cpp
struct Point2f { float x; float y; };
struct Person { std::string name; int age; };

EMSCRIPTEN_BINDINGS(values) {
    value_array<Point2f>("Point2f")
        .element(&Point2f::x)
        .element(&Point2f::y);

    value_object<Person>("Person")
        .field("name", &Person::name)
        .field("age", &Person::age);

    function("findPerson", &findPersonAtLocation);
}
```

JS: `var person = Module.findPerson([10.2, 156.5]);` — no `.delete()` needed.

### Enums

```cpp
enum class Color { RED, GREEN, BLUE };

EMSCRIPTEN_BINDINGS(enums) {
    enum_<Color>("Color")
        .value("RED", Color::RED)
        .value("GREEN", Color::GREEN)
        .value("BLUE", Color::BLUE);
}
```

JS: `Module.Color.RED`, `Module.Color.GREEN`

### Constants

```cpp
EMSCRIPTEN_BINDINGS(constants) {
    constant("MAX_SIZE", MAX_SIZE);
}
```

JS: `Module.MAX_SIZE`

### Overloaded Functions

```cpp
struct HasOverloads {
    void foo();
    void foo(int i);
    void foo(float f) const;
};

EMSCRIPTEN_BINDINGS(overloads) {
    class_<HasOverloads>("HasOverloads")
        .function("foo", select_overload<void()>(&HasOverloads::foo))
        .function("foo_int", select_overload<void(int)>(&HasOverloads::foo))
        .function("foo_float", select_overload<void(float)const>(&HasOverloads::foo));
}
```

### Deriving C++ Classes in JavaScript

```cpp
struct Interface {
    virtual ~Interface() {}
    virtual void invoke(const std::string& str) = 0;
};

struct InterfaceWrapper : public wrapper<Interface> {
    EMSCRIPTEN_WRAPPER(InterfaceWrapper);
    void invoke(const std::string& str) {
        return call<void>("invoke", str);
    }
};

EMSCRIPTEN_BINDINGS(interface) {
    class_<Interface>("Interface")
        .function("invoke", &Interface::invoke, pure_virtual())
        .allow_subclass<InterfaceWrapper>("InterfaceWrapper");
}
```

JS:
```javascript
// Extend (subclass)
var Derived = Module.Interface.extend("Interface", {
    invoke: function(str) { console.log(str); }
});
var instance = new Derived();

// Implement (use existing JS object)
var obj = { invoke: function(str) { console.log(str); } };
var iface = Module.Interface.implement(obj);
```

### Base Classes

```cpp
EMSCRIPTEN_BINDINGS(base) {
    class_<Base>("Base");
    class_<Derived, base<Base>>("Derived");
}
```

### Embind with STL Types

```cpp
EMSCRIPTEN_BINDINGS(stl) {
    register_vector<int>("VectorInt");
    register_map<int, std::string>("MapIntString");
    register_optional<std::string>();

    function("getVector", &getVector);
    function("getMap", &getMap);
    function("getOptional", &getOptional);
}
```

### TypeScript Definitions

```bash
emcc -lembind app.cpp --emit-tsd interface.d.ts
```

### Custom val Types in TypeScript

```cpp
EMSCRIPTEN_DECLARE_VAL_TYPE(CallbackType);

EMSCRIPTEN_BINDINGS(custom) {
    register_type<CallbackType>("(message: string) => void");
    // Named alias: register_type<CallbackType>("Callback", "(message: string) => void");
}
```

## emscripten::val (JS from C++)

`val` transliterates JavaScript code to C++. Call JS objects, read/write properties, coerce to C++ types.

```cpp
#include <emscripten/val.h>
using namespace emscripten;

// Access global
val window = val::global("window");
val document = val::global("document");

// Call methods
val element = document.call<val>("getElementById", "output");
element.call<void>("setAttribute", "class", "active");

// Set/get properties
element.set("textContent", "Hello");
val text = element["textContent"].as<std::string>();

// Create new objects
val arr = val::array();
arr.call<void>("push", val(1));
arr.call<void>("push", val(2));

// Call constructors
val AudioContext = val::global("AudioContext");
val context = AudioContext.new_();

// Convert to C++ types
bool b = val.as<bool>();
int i = val.as<int>();
double d = val.as<double>();
std::string s = val.as<std::string>();

// Create val from C++
val v1 = val(true);
val v2 = val(42);
val v3 = val(3.14);
val v4 = val(std::string("hello"));
val v5 = val::undefined();
val v6 = val::null();
```

### Web Audio API Example

```cpp
#include <emscripten/val.h>
using namespace emscripten;

int main() {
    val AudioContext = val::global("AudioContext");
    if (!AudioContext.as<bool>()) {
        AudioContext = val::global("webkitAudioContext");
    }

    val context = AudioContext.new_();
    val oscillator = context.call<val>("createOscillator");

    oscillator.set("type", val("triangle"));
    oscillator["frequency"].set("value", val(261.63));

    oscillator.call<void>("connect", context["destination"]);
    oscillator.call<void>("start", 0);
}
```

### val::await (Asyncify)

```cpp
// Await a JS Promise from C++
val result = myObject.call<val>("asyncMethod").await();
```

### Built-in Type Conversions

| C++ Type | JavaScript Type |
|----------|----------------|
| `void` | undefined |
| `bool` | true/false |
| `int`, `float`, `double` | Number |
| `int64_t`, `uint64_t` | BigInt (requires `-sWASM_BIGINT`) |
| `std::string` | String, ArrayBuffer, or TypedArray |
| `std::wstring` | String (UTF-16) |
| `emscripten::val` | anything |

## Memory Access from JavaScript

### getValue / setValue

```javascript
// Read from Wasm memory
var value = Module.getValue(ptr, 'i32');    // 32-bit int
var value = Module.getValue(ptr, 'i8');     // 8-bit int
var value = Module.getValue(ptr, 'float');  // 32-bit float
var value = Module.getValue(ptr, 'double'); // 64-bit float
var value = Module.getValue(ptr, '*');      // pointer

// Write to Wasm memory
Module.setValue(ptr, 42, 'i32');
Module.setValue(ptr, 3.14, 'double');
```

### Direct HEAP Access

```javascript
// Copy data into Wasm memory
var buf = Module._malloc(data.length * data.BYTES_PER_ELEMENT);
Module.HEAPU8.set(data, buf);
Module.ccall('process_data', 'number', ['number'], [buf]);
Module._free(buf);

// Read string from Wasm memory
var str = Module.UTF8ToString(ptr);

// Convert JS string to C string (allocates — must free)
var ptr = Module.stringToNewUTF8('hello');
Module._takes_string(ptr);
Module._free(ptr);
```

### Memory Growth Warning

With `-sALLOW_MEMORY_GROWTH`, `HEAPU8`, `HEAPF32`, etc. are refreshed automatically. But any `subarray()` views you hold become stale:

```javascript
// BAD — view may be stale after memory growth
var view = HEAPU8.subarray(x, y);
maybeGrowMemory();
view[0];  // May return undefined (stale view)

// GOOD — recreate view after potential growth
var view = HEAPU8.subarray(x, y);
maybeGrowMemory();
view = HEAPU8.subarray(x, y);  // Fresh view
view[0];  // Safe
```

## JS Library Files

Implement C APIs in JavaScript using `--js-library`:

```javascript
// mylib.js
addToLibrary({
    my_function: function() {
        alert('hello from JS library');
    },
    my_function__deps: ['$stringToUTF8'],
});
```

```c
// In C code
extern void my_function(void);

int main() {
    my_function();
    return 0;
}
```

```bash
emcc app.c --js-library mylib.js -o app.js
```

### Handling Closures in Libraries

Use `__postset` for self-replacing functions:

```javascript
addToLibrary({
    $init__postset: '_init();',
    $init: function() {
        var count = 0;
        _get_count = function() { return count; };
        _increment = function() { ++count; };
    },
    get_count: function() {},
    get_count__deps: ['$init'],
    increment: function() {},
    increment__deps: ['$init'],
});
```

## Function Pointers and addFunction

```javascript
// Create a JS function pointer callable from C
var signature = 'vi';  // void(int)
var funcPtr = Module.addFunction(function(x) {
    console.log('called with', x);
}, signature);

// Pass to C
Module.ccall('takes_callback', 'null', ['number'], [funcPtr]);

// Remove when done
Module.removeFunction(funcPtr);
```

Build with `-sALLOW_TABLE_GROWTH` to allow dynamic function table growth.

## Function Signatures

For `addFunction` and JS library `__sig` annotations:

| Character | Type |
|-----------|------|
| `v` | void |
| `i` | i32 (32-bit int) |
| `j` | i64 (64-bit int) |
| `f` | f32 (32-bit float) |
| `d` | f64 (64-bit double) |
| `p` | pointer (i32 or i64 depending on MEMORY64) |

Example: `'vi'` = `void(int)`, `'dii'` = `double(int, int)`, `'v'` = `void()`.

## Environment Variables

Set via `ENV` object (must be set before runtime starts, e.g., in `preRun`):

```javascript
Module.preRun = () => {
    ENV.MY_VAR = "/path/to/data";
    ENV.PATH = "/usr/local/bin:/usr/bin";
};

// Unset a variable
Module.preRun = () => {
    ENV.LANG = undefined;
};
```

## Emnapi (Node-API)

For porting Node-API addons to WebAssembly, use [Emnapi](https://github.com/toyobayashi/emnapi), an unofficial Node-API implementation for Emscripten. Allows compiling the same binding code to both Node.js native addon and WebAssembly.
