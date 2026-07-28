# Other Language Bindings

## Java

### Installation

Maven Central is not supported. Use Gradle with manual JAR download:

```groovy
repositories {
    mavenCentral()
    flatDir { dirs 'lib' }
}

task downloadUSearchJar {
    doLast {
        def version = '2.26.0'
        def url = "https://github.com/unum-cloud/USearch/releases/download/v${version}/usearch-${version}.jar"
        def file = file("lib/usearch-${version}.jar")
        file.parentFile.mkdirs()
        if (!file.exists()) {
            new URL(url).withInputStream { i ->
                file.withOutputStream { it << i }
            }
        }
    }
}

compileJava.dependsOn downloadUSearchJar

dependencies {
    implementation name: 'usearch', version: '2.26.0', ext: 'jar'
}
```

The fat JAR contains native builds for Linux, Windows, macOS, and Android.

### Quickstart

```java
import cloud.unum.usearch.Index;

try (Index index = new Index.Config()
        .metric(Index.Metric.COSINE)
        .quantization(Index.Quantization.FLOAT32)
        .dimensions(3)
        .capacity(100)
        .build()) {

    float[] vector = {0.1f, 0.2f, 0.3f};
    index.add(42L, vector);

    long[] keys = index.search(new float[]{0.1f, 0.2f, 0.3f}, 10);
    for (long key : keys) {
        System.out.println("Found key: " + key);
    }
}
```

### Multiple Data Types

```java
// Double precision
try (Index index = new Index.Config()
        .metric("cos")
        .dimensions(3)
        .quantization("f64")
        .build()) {

    double[] vector = {0.1, 0.2, 0.3};
    index.add(42L, vector);

    double[] buffer = new double[3];
    index.getInto(42L, buffer);  // Memory-efficient retrieval
}

// Byte precision (i8)
try (Index index = new Index.Config()
        .metric("cos")
        .dimensions(3)
        .quantization("i8")
        .build()) {

    byte[] vector = {10, 20, 30};
    index.add(42L, vector);
}
```

### Batch Operations

```java
// 3 vectors concatenated in one call
float[] batchVectors = {1.0f, 2.0f, 3.0f, 4.0f, 5.0f, 6.0f};
index.add(100L, batchVectors);  // Keys: 100, 101, 102
System.out.println("Index size: " + index.size());  // 3
```

### Concurrent Operations

```java
ExecutorService executor = Executors.newFixedThreadPool(8);

CompletableFuture<Void>[] tasks = new CompletableFuture[4];
for (int t = 0; t < 4; t++) {
    final int threadId = t;
    tasks[t] = CompletableFuture.runAsync(() -> {
        for (int i = 0; i < 1000; i++) {
            long key = threadId * 1000L + i;
            float[] vector = generateRandomVector(4);
            index.add(key, vector);
        }
    }, executor);
}
CompletableFuture.allOf(tasks).join();
executor.shutdown();
```

---

## Go

### Installation

**Linux:** Download `.deb` from releases:
```sh
wget https://github.com/unum-cloud/USearch/releases/download/v2.26.0/usearch_linux_<arch>_2.26.0.deb
dpkg -i usearch_linux_<arch>_2.26.0.deb
```

**macOS:** Download `.zip`:
```sh
wget https://github.com/unum-cloud/USearch/releases/download/v2.26.0/usearch_macos_<arch>_2.26.0.zip
unzip usearch_macos_<arch>_2.26.0.zip
sudo mv libusearch_c.dylib /usr/local/lib && sudo mv usearch.h /usr/local/include
```

**Windows:** Run `winlibinstaller.bat` from the repository.

Then:
```sh
go get github.com/unum-cloud/usearch/golang
```

### Quickstart

```go
package main

import (
    "fmt"
    "runtime"
    usearch "github.com/unum-cloud/usearch/golang"
)

func main() {
    conf := usearch.DefaultConfig(3)
    conf.Quantization = usearch.F32
    index, err := usearch.NewIndex(conf)
    if err != nil {
        panic(err)
    }
    defer index.Destroy()

    err = index.Reserve(100)
    _ = index.ChangeThreadsAdd(uint(runtime.NumCPU()))

    for i := 0; i < 100; i++ {
        err = index.Add(usearch.Key(i), []float32{float32(i), float32(i + 1), float32(i + 2)})
    }

    keys, distances, err := index.Search([]float32{0.0, 1.0, 2.0}, 3)
    fmt.Println(keys, distances)
}
```

> Always call `Reserve(capacity)` before the first write.

### Filtered Search

```go
handler := &usearch.FilteredSearchHandler{
    Callback: func(key usearch.Key, handler *usearch.FilteredSearchHandler) int {
        if key % 2 == 0 {
            return 1  // Accept even keys
        }
        return 0  // Reject odd keys
    },
    Data: nil,
}

keys, distances, err := index.FilteredSearch(queryVector, 10, handler)
```

### Exact Search

```go
keys, distances, err := usearch.ExactSearch(
    dataset, queries,
    datasetSize, queryCount,
    vectorDims*4, vectorDims*4,  // Strides in bytes
    vectorDims, usearch.Cosine,
    maxResults, 0,  // 0 threads = auto
)
```

### Concurrency

```go
const numWorkers = 10
_ = index.ChangeThreadsSearch(numWorkers)

var wg sync.WaitGroup
for i := 0; i < numWorkers; i++ {
    wg.Add(1)
    go func() {
        defer wg.Done()
        keys, distances, err := index.Search(queryVector, 10)
    }()
}
wg.Wait()
```

---

## C# (.NET)

### Installation

```sh
dotnet add package Cloud.Unum.USearch
```

### Quickstart

```csharp
using System.Diagnostics;
using Cloud.Unum.USearch;

using var index = new USearchIndex(
    metricKind: MetricKind.Cos,
    quantization: ScalarKind.Float32,
    dimensions: 3,
    connectivity: 16,
    expansionAdd: 128,
    expansionSearch: 64
);

var vector = new float[] { 0.2f, 0.6f, 0.4f };
index.Add(42, vector);
int matches = index.Search(vector, 10, out ulong[] keys, out float[] distances);

Trace.Assert(index.Size() == 1);
Trace.Assert(keys[0] == 42);
Trace.Assert(distances[0] <= 0.001f);
```

### Serialization

```csharp
index.Save("index.usearch");

// Load (copy into memory)
using var loaded = new USearchIndex("index.usearch");

// View (memory-map, read-only)
using var viewed = new USearchIndex("index.usearch", view: true);
```

### Batch Operations

```csharp
using var index = new USearchIndex(MetricKind.Cos, ScalarKind.Float32, dimensions: 3);

int n = 100;
ulong[] keys = Enumerable.Range(0, n).Select(i => (ulong)i).ToArray();
float[][] vectors = Enumerable.Range(0, n)
    .Select(_ => Enumerable.Range(0, 3)
        .Select(__ => (float)new Random().NextDouble() * 0.3f)
        .ToArray())
    .ToArray();

index.Add(keys, vectors);
int matches = index.Search(vectors[0], 10, out ulong[] foundKeys, out float[] foundDistances);
```

---

## Swift

Swift bindings wrap the C API. Available as a Swift Package or direct source inclusion.

### Key Files

- `USearchIndex.swift` — main wrapper
- `USearchIndex+Sugar.swift` — convenience extensions
- `Util.swift` — helper utilities

### Usage

```swift
import USearch

let index = USearchIndex(
    metric: .cosine,
    scalar: .float32,
    dimensions: 3
)

index.reserve(capacity: 100)
index.add(key: 42, vector: [0.2, 0.6, 0.4])

let results = index.search(vector: [0.2, 0.6, 0.4], count: 10)
```

See [`ashvardanian/SwiftSemanticSearch`](https://github.com/ashvardanian/SwiftSemanticSearch) for a complete iOS semantic search demo.

---

## Objective-C

Objective-C bindings are provided via `USearchObjective.mm` and the `include/` directory.

```objc
#import "USearchObjective.h"

USearchIndex *index = [[USearchIndex alloc]
    initWithMetric:USearchMetricCosine
    scalar:USearchScalarFloat32
    dimensions:3];

[index reserveCapacity:100];
[index addKey:42 vector:@[@0.2, @0.6, @0.4]];

USearchResults *results = [index searchVector:@[@0.2, @0.6, @0.4] count:10];
```

---

## Feature Matrix by Language

| Feature | C++ | Python | C | Rust | JS | Java | Go | C# | Swift | ObjC |
|---------|-----|--------|---|------|----|----|----|----|----|----|
| Add/search/remove | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Save/load/view | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| User-defined metrics | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Batch operations | ❌ | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| Filter predicates | ✅ | ❌ | ✅ | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| Joins | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Variable-length vectors | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| 4B+ capacities (`uint40_t`) | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Clustering | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
