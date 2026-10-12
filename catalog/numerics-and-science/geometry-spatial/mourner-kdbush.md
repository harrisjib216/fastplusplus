# KDBush

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `JavaScript` · `ISC` · 🟢 active

> JavaScript static 2D point index (flat kd-tree in one ArrayBuffer); its author says it indexes points 5-8x faster than RBush.

| | |
|---|---|
| **Beats** | RBush (JavaScript R-tree) |
| **Claimed result** | RBush README: 'kdbush ... performs point indexing 5-8x faster than RBush'. KDBush README: 'Faster indexing and search, with lower memory footprint' versus RBush, with no numbers in the text. |
| **Workload** | Static 2D point indexing (flat KD-tree in one array buffer) versus RBush R-tree point indexing and range/radius queries. |
| **Metric** | throughput |
| **Adoption** | 713 stars, 75 forks |
| **Last commit** | 2026-05-19 |
| **Links** | [repository](https://github.com/mourner/kdbush) · [benchmark](https://github.com/mourner/rbush) |

## Verdict

The only number is a one-line first-party claim in the RBush README, by the author of both libraries, that kdbush 'performs point indexing 5-8x faster than RBush'. It gives no workload, Node version or hardware. kdbush's own bench.js builds an index of 1M Uint32 points and times 10,000 small box and 10,000 small radius queries, but it runs kdbush alone, never RBush, and publishes no results.

## Use it when

- Browser or Node code that indexes a large fixed set of 2D points (map markers, clustering input, hit-testing) and then runs many small box or radius queries.
- Integer or grid coordinates, where Int32Array or Uint32Array storage shrinks the index and speeds it up.
- Building the index in a Web Worker and handing it to the main thread without copying (postMessage with a transferable ArrayBuffer, KDBush.from on the other side), or sharing it through a SharedArrayBuffer.
- Saving a prebuilt index to a file and loading it back with KDBush.from, without rebuilding.
- Point-only datasets where Flatbush would also work: the README says KDBush uses about 2x less memory than Flatbush for points.

## Skip it when

- Data that changes after indexing: there is no insert or remove, so every change means a full rebuild. RBush is the dynamic option.
- Rectangles, polygons or other extents: use Flatbush (static) or RBush (dynamic).
- k-nearest-neighbour queries: the core library offers only box and radius queries. kNN with great-circle distances is in the separate mourner/geokdbush extension.
- 3D or higher-dimensional points: 2D only (3D support is an open feature request, issue #38).
- Native C++ code: this is JavaScript. The official C++11 port (mourner/kdbush.hpp) was archived in June 2026; nanoflann covers k-D point search in C++.

## How it is fast

finish() kd-sorts the coordinate and id arrays in place: it recursively places the median on alternating axes with Floyd-Rivest selection and stops at leaves of nodeSize points (default 64), which are scanned linearly. The tree is implicit (no node objects or pointers). Ids and coordinates live in typed arrays inside a single ArrayBuffer, with Uint16 ids under 65,536 points and a coordinate type you choose (Int32Array or Uint32Array is smaller and faster than the Float64 default). Queries walk the tree iteratively with a preallocated Uint32Array stack, and withinInto can write into a caller-supplied typed array so queries allocate nothing.

## Compared with alternatives

Pick KDBush over RBush when the points are static and points-only, which is where the 5-8x indexing claim applies. Pick geo-index (its Rust port of this layout) or nanoflann in native code, and nanoflann or a C++ kd-tree if you need kNN or more than two dimensions.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none (npm package kdbush; ES module, plus UMD bundles kdbush.js and kdbush.min.js that expose a KDBush global) |
| **Minimum toolchain** | Any engine with ES modules and typed arrays; package.json declares no engines field. TypeScript types (index.d.ts) are generated from JSDoc at publish. |
| **Platforms** | any JavaScript runtime (browsers, Node.js); SharedArrayBuffer sharing requires a runtime that exposes it |
| **Thread safety** | Not documented. A finished index is read-only and can be shared across workers through a SharedArrayBuffer (README). Within one realm, range and within use a module-level scratch stack (STACK), which is safe only because JavaScript runs single-threaded per realm. |
| **Drop-in for the baseline** | partial — it replaces RBush only for static point sets, and the API differs: preallocated count, add then finish, and queries that return insertion indices instead of items. |

## Gotchas

- finish() throws unless exactly numItems points were added, so the count must be known before you start.
- Queries return indices in the order the tree was traversed, not insertion order. Issue #42 (order changing after a rebuild) was closed without a fix.
- Range bounds are inclusive on all sides, and radius queries compare squared Euclidean distance on raw coordinates. For latitude and longitude that is planar distance, not geodesic (geokdbush handles geographic kNN).
- The serialized header stores the raw nodeSize argument as a Uint16, while the build clamps it to 2..65535. A nodeSize above 65535 would therefore serialize a different leaf size than the one used to build, and KDBush.from would rebuild a mismatched index. Keep nodeSize at the default 64 or another small value.

## Known shortcomings

- The 5-8x is one line in the RBush README and bench.js times kdbush only; JavaScript.
- JavaScript library, not callable from C++; its C++ port mourner/kdbush.hpp was archived 2026-06. The 5-8x claim is one first-party line in the RBush README and bench.js never runs RBush. Minor bug: header stores raw nodeSize as Uint16 while build clamps to 65535, so KDBush.from with nodeSize &gt;65535 gives a mismatched tree.

## Caveats and trade-offs

The 5-8x figure is a one-line claim in RBush's README, written by the author of both libraries, with no workload, hardware or code reference. kdbush's bench.js times only kdbush (no RBush run) and publishes no numbers. The comparison is against a JavaScript R-tree, not a native library. KDBush is static and points-only, while RBush is dynamic and indexes rectangles.

Points only (no rectangles), static (cannot add or remove after indexing), single ArrayBuffer storage; Flatbush is the rectangle equivalent and KDBush uses about 2x less memory than Flatbush for points.

## Maintenance

Active (v4.1.0, last commit 2026-05-19, 713 stars), ISC-licensed and about 300 lines of dependency-free JavaScript, so easy to vendor; it is JavaScript, not C++, and the official C++ port is archived.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The only number is the one-line first-party claim in the same author's RBush README that kdbush 'performs point indexing 5-8x faster than RBush'. It gives no workload, hardware or Node version. kdbush's bench.js times kdbush alone (1M Uint32 points, 10,000 bbox and radius queries) and publishes no results. Numbers without methodology: C.
- **Verifier notes:** Claim text verified verbatim in the RBush README; the KDBush README says only 'Faster indexing and search, with lower memory footprint' compared with RBush. Metadata from github.com: ISC (LICENSE file and package.json), 713 stars, 64 commits, last commit 2026-05-19 (v4.1.0), not a fork or archived. geo-index (also in wave 8) is a Rust port of this layout.
- **Fields the verifier corrected:** `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://github.com/mourner/kdbush>
  - <https://github.com/mourner/kdbush/commits/main>
  - <https://raw.githubusercontent.com/mourner/kdbush/HEAD/README.md>
  - <https://raw.githubusercontent.com/mourner/kdbush/HEAD/bench.js>
  - <https://raw.githubusercontent.com/mourner/kdbush/HEAD/package.json>
  - <https://raw.githubusercontent.com/mourner/kdbush/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/mourner/rbush/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/mourner/kdbush>
  - <https://github.com/mourner/kdbush/issues?q=is%3Aissue>
  - <https://github.com/mourner/kdbush/issues/4>
  - <https://github.com/mourner/kdbush/issues/42>
  - <https://raw.githubusercontent.com/mourner/kdbush/HEAD/README.md>
  - <https://raw.githubusercontent.com/mourner/kdbush/HEAD/index.js>
  - <https://raw.githubusercontent.com/mourner/kdbush/HEAD/bench.js>
  - <https://raw.githubusercontent.com/mourner/kdbush/HEAD/package.json>
  - <https://raw.githubusercontent.com/mourner/kdbush/HEAD/test.js>
  - <https://raw.githubusercontent.com/mourner/rbush/HEAD/README.md>
  - <https://github.com/mourner/kdbush.hpp>
  - <https://github.com/mourner/geokdbush>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/mourner/kdbush`) · [data/wave8/enrich/raw/github_com_mourner_kdbush.json](../../../data/wave8/enrich/raw/github_com_mourner_kdbush.json) (enrichment confidence 0.8)

</details>
