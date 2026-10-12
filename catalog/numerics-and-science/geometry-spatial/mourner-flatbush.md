# Flatbush

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `JavaScript` · `ISC` · 🟢 active

> Static packed Hilbert R-tree for 2D boxes in JavaScript, stored in one ArrayBuffer; billed as faster and leaner than RBush.

| | |
|---|---|
| **Beats** | RBush (dynamic JavaScript R-tree; counts as an R-tree baseline) |
| **Claimed result** | README says Flatbush is similar to RBush with 'Faster indexing and search, with much lower memory footprint'; no RBush timings or ratio appear on the page. Flatbush-only numbers ('node bench.js' on a MacBook Pro M1 Pro, Node v24): index 1,000,000 rectangles 109ms; 100 searches 10% area 64ms; 1000 searches 1% area 66ms; 10000 searches 0.1% area 150ms; 10000 searches 0.01% area 51ms; 10000 searches 0.001% area 31ms; 10000 searches of 1 neighbor 30ms; 10000 searches of 100 neighbors 127ms; 1 search of 1,000,000 neighbors 84ms. |
| **Workload** | Static packed Hilbert R-tree over 1,000,000 random rectangles: index build plus bounding-box and k-nearest-neighbour searches (README table is Flatbush-only). |
| **Metric** | throughput |
| **Hardware** | MacBook Pro (M1 Pro) |
| **Compiler and flags** | Node v24 (README); no other settings stated |
| **Adoption** | 1.6k stars |
| **Last commit** | 2026-07-08 |
| **Links** | [repository](https://github.com/mourner/flatbush) · [benchmark](https://github.com/mourner/flatbush) |

## Verdict

The only numbers are Flatbush's own (node bench.js, MacBook Pro M1 Pro, Node v24, 1,000,000 seeded random boxes, nodeSize 16, 10 runs): index 109 ms, 1,000 searches of 1% area 66 ms, 10,000 1-NN queries 30 ms, and one 1,000,000-neighbour query 84 ms. bench.js never imports RBush, and RBush's own table (Node 6.2.2, 2012 laptop) is not comparable. The 'faster than RBush' claim is qualitative (tier D). The one third-party comparison found, Bokeh PR #7583 (2018), shows its 1k-500k point profiling only as a graph.

## Use it when

- Static data sets of 10^5 to 10^8 boxes or points (map features, chart glyphs, mesh triangles) that are built once and queried many times
- Browser or Node code that needs to move an index between workers without copying, or share one read-only index via SharedArrayBuffer
- Shipping a precomputed index as a compact binary file; the same layout is readable from Rust (geo-index, ABI compatible) and C++ (chusitoo/flatbush accepts JS-encoded buffers)
- Hit-testing and viewport culling in visualization libraries; Bokeh adopted it in place of RBush for large scatter plots (PR #7583, 2018)
- As the reference design to port: the README lists C++, Rust, C#, Python and Dart ports

## Skip it when

- Data that changes: there is no insert or remove, so every change means a full rebuild; RBush is the dynamic option
- C++ code: this is JavaScript; use the C++ port chusitoo/flatbush or a native index (Boost.Geometry rtree, nanoflann, tidwall rtree.c)
- Indexes near 2 GB: issue #67 (open) reports a 100M-item Float32Array index at 1.9 GB and asks for a way past the 2 GB buffer limit
- Exact nearest geometry: neighbors() ranks by distance to bounding boxes, in coordinate units; for lon/lat data the README points to the geoflatbush extension
- When you need a measured speed-up over RBush: the repo's benchmark times Flatbush alone, so the 'faster' claim is unquantified

## How it is fast

finish() computes a Hilbert value for each box centre on a 65,536 x 65,536 grid (the bit-twiddling Hilbert function from rawrunprotected/hilbert_curves), sorts only as far as node boundaries with an iterative quicksort, and packs nodes bottom-up (a packed Hilbert R-tree, nodeSize 16 by default). Boxes and child indices sit in flat typed arrays (Float64Array by default, Uint16/Uint32 indices), so there are no per-node objects for the garbage collector and scans are sequential in memory. search() emits a whole subtree as one contiguous leaf range without further tests once a node lies fully inside the query box, and neighbors() is a best-first traversal on a FlatQueue binary heap with a tightened bound when k = 1.

## Compared with alternatives

Pick Flatbush over RBush when the data is static and you want lower memory use and a transferable buffer; use KDBush instead for points only. In Rust, or for Python bindings, use geo-index (ABI-compatible port, \~2x faster construction than rstar on its own benchmark); in C++ use chusitoo/flatbush or nanoflann/GeoToolbox KdBoxTree, which have baseline numbers.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | flatqueue ^3.1.0 (priority queue, same author) |
| **Minimum toolchain** | ES module package ("type": "module") plus a UMD browser bundle and TypeScript typings; no engines field in package.json; README benchmark run on Node v24 |
| **Platforms** | any JavaScript runtime with typed arrays (browsers, Node); SharedArrayBuffer sharing needs a runtime that allows it |
| **Thread safety** | Read-only after finish(); the buffer can be shared with workers and wrapped with Flatbush.from() in each. Each instance keeps one internal priority queue for neighbors(), so do not call neighbors() on the same instance from inside its own filter callback |
| **Drop-in for the baseline** | no |

## Gotchas

- add() must be called exactly numItems times before finish(), which throws otherwise; search() and neighbors() throw until finish() has run
- A non-default ArrayType (Float32Array, Int32Array) stores coordinates by ordinary typed-array conversion with no outward rounding, so stored boxes can be slightly smaller than the originals and hits on box edges can be missed
- Many duplicate boxes overflowed the call stack in the old recursive sort (issues #61 and #69, the latter reported through Bokeh); the current code sorts with an explicit stack (package 4.6.2); older bundled copies may still crash
- Serialized data carries format version 3 and Flatbush.from() rejects other versions; byteOffset must be 8-byte aligned. Before June 2026 the README's search rows understated the query area by 4x (issue #62)

## Known shortcomings

- JavaScript, not callable from C++. The RBush comparison is qualitative and bench.js never runs RBush. C++ port: chusitoo/flatbush.
- Tier D stands: bench.js times only Flatbush itself; the Bokeh PR #7583 (2018) Flatbush vs RBush profiling is a graph with no numbers. JavaScript. Issue #67 (open): about 2 GB index cap. The old recursive sort overflowed the stack on duplicate boxes (#61, #69); 4.6.2 uses an explicit stack. Search rows were understated 4x before June 2026 (#62).

## Caveats and trade-offs

The speed-up over RBush is a qualitative README claim: the benchmark table has only a flatbush column and bench.js imports only ./index.js (seeded mulberry32 data, nodeSize 16, 10 repetitions), never RBush. RBush's own README performance table dates from Node 6.2.2 on a mid-2012 MacBook Pro and compares RBush with an older RTree, so no fair Flatbush/RBush ratio can be derived from the two pages. Not C++ and not compared with Boost.Geometry or CGAL. The README lists C++ ports (chusitoo/flatbush; IMQS/flatbush, no longer maintained) and Rust/C#/Python/Dart ports. Kept as a tier D entry because of notability (1.6k stars).

Static index: no add or remove after finish(). The whole index is one ArrayBuffer (transferable between threads, storable as a compact binary file). JavaScript only; the README lists ports for C++, Rust, C# and Python (a C++ port exists as chusitoo/flatbush) and a Rust port with ABI compatibility (geo-index, already catalogued).

## Maintenance

Active: version 4.6.2, 196 commits, 1.6k stars, last commit 2026-07-08, 5 open issues. ISC-licensed, a single 519-line index.js with one small dependency, so it is easy to vendor or port.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification D, tier now D.
- **Tier reason:** The README's speed-up over RBush is qualitative ('Faster indexing and search'); its benchmark table and bench.js measure Flatbush alone, so there are no baseline numbers and the comparison is D.
- **Verifier notes:** Numbers on the page match the record but are Flatbush-only; tier D for the RBush claim confirmed. Metadata checked: ISC, 1.6k stars, last commit 2026-07-08, not a fork. JavaScript; its C++ port chusitoo/flatbush is a possible seed lead.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/mourner/flatbush/HEAD/README.md>
  - <https://github.com/mourner/flatbush>
  - <https://github.com/mourner/flatbush/commits>
  - <https://raw.githubusercontent.com/mourner/flatbush/HEAD/bench.js>
  - <https://raw.githubusercontent.com/mourner/rbush/HEAD/README.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/mourner/flatbush/HEAD/README.md>
  - <https://raw.githubusercontent.com/mourner/flatbush/HEAD/bench.js>
  - <https://raw.githubusercontent.com/mourner/flatbush/HEAD/index.js>
  - <https://raw.githubusercontent.com/mourner/flatbush/HEAD/package.json>
  - <https://github.com/mourner/flatbush>
  - <https://github.com/mourner/flatbush/issues?q=is%3Aissue>
  - <https://github.com/mourner/flatbush/issues/69>
  - <https://github.com/mourner/flatbush/issues/67>
  - <https://raw.githubusercontent.com/chusitoo/flatbush/HEAD/README.md>
  - <https://github.com/bokeh/bokeh/issues/7582>
  - <https://github.com/bokeh/bokeh/pull/7583>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/mourner/flatbush`) · [data/wave8/enrich/raw/github_com_mourner_flatbush.json](../../../data/wave8/enrich/raw/github_com_mourner_flatbush.json) (enrichment confidence 0.75)

</details>
