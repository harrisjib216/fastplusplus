# RBush

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `JavaScript` · `MIT` · 🟢 active

> JavaScript 2D R-tree for rectangles and points with bulk loading; beats the older imbcmdth RTree JavaScript library.

| | |
|---|---|
| **Beats** | imbcmdth RTree (older JavaScript R-tree library) |
| **Claimed result** | README table (RBush vs old RTree): insert 1M items one by one 3.18 s vs 7.83 s (2.5x); 1000 searches of 0.01% area 0.03 s vs 0.93 s (30x); 1% area 0.35 s vs 2.27 s (6.5x); 10% area 2.18 s vs 9.53 s (4.4x); remove 1000 items 0.02 s vs 1.18 s (50x); bulk-insert 1M items 1.25 s (6.7x, no bulk insert in the old library). |
| **Workload** | 1M uniformly distributed rectangles of \~0.01% area, maxEntries 16: one-by-one insert, searches of 0.01%, 1% and 10% area, one-by-one removal, bulk insert. |
| **Metric** | throughput |
| **Hardware** | Retina MacBook Pro 15 (mid-2012); CPU model not stated |
| **Compiler and flags** | Node.js v6.2.2. The README cites debug/perf.js; that path is gone, and the current bench/perf.js (npm run perf) times only RBush, not the old RTree. |
| **Adoption** | 2.8k stars, 253 forks |
| **Last commit** | 2026-04-03 |
| **Links** | [repository](https://github.com/mourner/rbush) · [benchmark](https://github.com/mourner/rbush) |

## Verdict

The README table is a first-party run on Node.js v6.2.2 on a mid-2012 Retina MacBook Pro (CPU model not given) with 1M random rectangles of \~0.01% area and maxEntries 16: one-by-one insert 3.18 s vs 7.83 s for imbcmdth's old RTree, 1000 searches at 0.01%/1%/10% area 0.03/0.35/2.18 s vs 0.93/2.27/9.53 s, removing 1000 items 0.02 s vs 1.18 s (about 59x, derived from page data, printed as 50x), and bulk insert of 1M items 1.25 s (the printed 6.7x does not follow from the table; 7.83/1.25 is about 6.3x, derived from page data). The script the README cites (debug/perf.js) is now bench/perf.js and times RBush alone, so the baseline column cannot be reproduced from the repo.

## Use it when

- JavaScript/TypeScript maps, data visualisation, canvas or game code that needs bounding-box queries over 2D rectangles that are inserted and removed over time.
- Batch indexing of roughly 10^4 to 10^6 rectangles with load() (README: bulk insertion \~2-3x faster than one-by-one, and queries \~20-30% faster afterwards).
- Building an index on a Node.js server and sending it to browsers via toJSON()/fromJSON() with the same maxEntries.
- Incremental bulk updates where each batch is spatially clustered (STLT grafting works well for clustered data per the README).

## Skip it when

- Static point sets: the README itself points to kdbush, which indexes points 5-8x faster than RBush.
- C or C++ projects: this is a JavaScript library and its benchmark is JS versus JS; use a native sibling instead.
- 3D or higher-dimensional data, or nearest-neighbour queries without the extra rbush-knn package (RBush is 2D bounding-box search only).
- Bulk-inserting scattered data into an existing tree: the README warns this makes query performance worse.
- Rapidly moving objects: there is no update operation, only remove plus insert (issue #28, open since 2015); and CommonJS-only environments, since v4+ is ESM only.

## How it is fast

Single inserts use a non-recursive R-tree insertion with the R\*-tree split heuristics only (split axis by minimum total margin, split index by minimum overlap then area), skipping R\*-tree forced reinsertion, which the author found too slow in JS. Bulk loading is OMT (Overlap Minimizing Top-down) packing: items are partitioned into roughly square tiles with a multi-select built on Floyd-Rivest quickselect, filling nodes to target height; bulk insertion into a non-empty tree uses Small-Tree-Large-Tree (the new batch is built as a subtree and grafted in). Search is iterative with an explicit stack and copies a whole subtree without per-item tests when the query box contains a node's box; deletion uses free-at-empty (no reinsertion on underflow).

## Compared with alternatives

Among catalogued siblings, pick RBush over KDBush only when you index rectangles or need insert/remove (KDBush is static points and, per RBush's own README, 5-8x faster at that); the native siblings (tidwall/rtree.c, PH-tree, GeoToolbox KdBoxTree) and the Rust geo-index are the choice outside JavaScript.

## Integration

| | |
|---|---|
| **Form** | module (npm ES module; also a UMD browser bundle rbush.min.js exposing a global RBush) |
| **Dependencies** | quickselect ^3.0.0 |
| **Minimum toolchain** | An ES-module JavaScript environment (RBush v4+ dropped CommonJS); IE11 needs transpiling per the README |
| **Platforms** | any JavaScript runtime (modern browsers, Node.js) |
| **Thread safety** | not documented (plain single-threaded JavaScript object graph; no locking) |
| **Drop-in for the baseline** | no |

## Gotchas

- remove() matches by object reference by default; with a custom equals function the item you pass must still carry the original bounding box, because the traversal only descends into nodes whose box contains the item's box (index.js remove(); open issue #95).
- fromJSON() trusts its input and requires the same maxEntries as the exporting tree; the README's import example still uses the old rbush(9) factory call, while v4 is a class (new RBush(9)).
- maxEntries is clamped to at least 4 and minimum fill is 40%; higher maxEntries speeds insertion and slows search (README default 9, benchmark used 16).
- search() allocates and returns a fresh array per call, and load() copies the input array (data.slice()) before partitioning it.

## Known shortcomings

- Cited perf script is now bench/perf.js and runs RBush only, so the old-RTree column is not reproducible; Node 6.2.2 on a 2012 laptop; JavaScript.
- JavaScript, not callable from C++. Current README recommends only kdbush, not Flatbush. Bulk-insert '6.7x' does not follow from the table (7.83/1.25 is \~6.3x, derived from page data). README fromJSON example still uses the old rbush(9) call.

## Caveats and trade-offs

The numbers are from Node 6.2.2 on a 2012 laptop and compare against an old JavaScript R-tree (imbcmdth/RTree), not a C/C++ library or Boost.Geometry. The benchmark script the README names now lives at bench/perf.js and runs RBush alone, so the baseline column cannot be reproduced from the repo. The CPU model is missing. The table predates RBush v4. The baseline is another R-tree implementation, so this shows algorithm tuning (R\*-tree split, OMT bulk load) rather than a win over a major incumbent. Some README ratios are rounded loosely (remove: 1.18 s vs 0.02 s is about 59x on the page data, printed as 50x).

2D only; R-tree with OMT bulk loading and STLT bulk insertion, R\*-tree style split; mutable (insert, remove). README recommends kdbush (static points) and Flatbush (static rectangles) for faster static indexes.

## Maintenance

Maintained (last commit 2026-04-03, a dev-dependency update; last functional release v4.0.1 per package.json), MIT-licensed, a single \~500-line source file with one dependency, so easy to vendor; 8 open issues, all enhancements or questions.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README Performance table is a first-party run against imbcmdth's old RTree on Node.js v6.2.2 on a mid-2012 Retina MacBook Pro, with no CPU model. The script it cites (debug/perf.js, now bench/perf.js) times only RBush, so the old-RTree column cannot be reproduced from the repo: C.
- **Verifier notes:** Every number in the record matches the README Performance table verbatim. Metadata from github.com: MIT (LICENSE file and package.json), 2.8k stars, 301 commits, last commit 2026-04-03 ('update dev deps'), not a fork or archived. The last functional release was v4.0.1 (Aug 2024).
- **Fields the verifier corrected:** `compiler_and_flags`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://github.com/mourner/rbush>
  - <https://github.com/mourner/rbush/commits/main>
  - <https://raw.githubusercontent.com/mourner/rbush/HEAD/README.md>
  - <https://raw.githubusercontent.com/mourner/rbush/HEAD/package.json>
  - <https://raw.githubusercontent.com/mourner/rbush/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/mourner/rbush/HEAD/bench/perf.js>
- **Sources the enricher read:**
  - <https://github.com/mourner/rbush>
  - <https://github.com/mourner/rbush/issues>
  - <https://github.com/mourner/rbush/issues/95>
  - <https://github.com/mourner/rbush/issues/28>
  - <https://raw.githubusercontent.com/mourner/rbush/HEAD/README.md>
  - <https://raw.githubusercontent.com/mourner/rbush/HEAD/package.json>
  - <https://raw.githubusercontent.com/mourner/rbush/HEAD/index.js>
  - <https://raw.githubusercontent.com/mourner/rbush/HEAD/bench/perf.js>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/mourner/rbush`) · [data/wave8/enrich/raw/github_com_mourner_rbush.json](../../../data/wave8/enrich/raw/github_com_mourner_rbush.json) (enrichment confidence 0.85)

</details>
