# geo-index (packed immutable R-tree and k-d tree)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0 OR MIT` · 🟢 active

> Packed, immutable 2D R-tree and k-d tree crate (Rust port of flatbush/kdbush); builds about 2x faster than rstar bulk_load.

| | |
|---|---|
| **Beats** | rstar (georust dynamic R-tree, bulk_load) |
| **Claimed result** | README: construction is \~2x faster than rstar and search is \~33% faster. Numbers: construction geo-index hilbert 80.891 ms vs rstar bulk 159.34 ms; STRTree 116.52 ms; search 116.41 us (flatbush-style) vs rstar 153.62 us; with the rayon feature STRTree construction drops to 72.099 ms. |
| **Workload** | Criterion benchmark on one bounding-box dataset (benches/bounds.raw): bulk construction of an R-tree from boxes, and a bounding-box search, geo-index (Hilbert-sorted packed tree) vs rstar::RTree::bulk_load. |
| **Metric** | throughput |
| **Compiler and flags** | cargo bench --bench rtree (Criterion); rustc version, profile and flags not stated |
| **Adoption** | 200 stars, 18 forks; used under the hood in geoarrow-rs (per the README) |
| **Last commit** | 2026-09-15 |
| **Links** | [repository](https://github.com/georust/geo-index) · [benchmark](https://github.com/georust/geo-index) |

## Verdict

One first-party Criterion run (benches/rtree.rs) on a single bundled box dataset (benches/bounds.raw) shows Hilbert-packed construction at 80.9 ms vs 159.3 ms for rstar bulk_load (1.97x, derived from page data) and one fixed bounding-box query at 116.4 us vs 153.6 us (1.32x, derived from page data); CPU, rustc version and build profile are not stated. The rstar build closure also clones its input Vec inside the timed loop, and per GitHub's blame view the README timings date from a 2023 'Quick bench' commit, so they predate the v0.3.2 search optimization and do not name the rstar version used.

## Use it when

- Static 2D box or point sets (map features, tile footprints, GeoArrow geometries) built once and queried many times from Rust or Python
- Bulk construction is on the critical path: the README run builds a Hilbert-packed tree in 80.9 ms vs 159.3 ms for rstar::RTree::bulk_load on the same boxes
- You need to persist an index or pass it across an FFI/process boundary without serialization: the single-buffer flatbush layout reopens zero-copy and is readable by flatbush/kdbush in JS
- Memory must be predictable: RTreeMetadata gives the exact byte size for a given item count and node size before you build
- Nearest-neighbor ranking with your own metric (Manhattan, spherical with valid bounds) via neighbors_with_callbacks, without pulling in the geo crate

## Skip it when

- Data that changes after build: there is no insert or delete, so every update means a full rebuild; rstar supports dynamic updates
- 3D or higher-dimensional data: only two dimensions are indexed
- Coordinates outside i8/u8/i16/u16/i32/u32/f32/f64 (no u64/i64), or data containing NaN, which the docs say may panic
- You want the tree to hold and return your objects: queries return insertion indexes and you keep the collection yourself
- You need k-nearest queries on the k-d tree: KDTree offers range and within (radius) only; kNN for the k-d tree is an open issue (#97)

## How it is fast

Construction is a bulk pack: item centers are mapped onto a 65,536 x 65,536 grid and sorted by Hilbert curve value (the threadlocalmutex bit-twiddling Hilbert function), or by sort-tile-recursive, and then parent boxes are computed bottom-up so every node is full except the last on each level. Sorting only has to order whole node-sized blocks (k_block_sort_by with select_nth_unstable_by), not the full array. Boxes and indices sit in flat contiguous arrays, so search is a breadth-first scan of 4-value box runs with no pointer chasing; the search loop skips bounds checks with get_unchecked, which a code comment credits with up to 30%. The optional rayon feature parallelizes the STR y-sort (STR construction 116.5 ms to 72.1 ms in the README).

## Compared with alternatives

Pick it over KDBush or RBush when you are in Rust or Python rather than JavaScript but still want the flatbush/kdbush buffer format, and it adds a box R-tree that KDBush lacks. Pick GeoToolbox KdBoxTree or ArborX instead for 3D+ data or C++ code, and tidwall/rtree.c or Boost R\*-tree when the data must be updated in place.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | bytemuck, float_next_after, geo-traits 0.3, num-traits, thiserror, tinyvec; optional rayon (parallel STR sort) and geo 0.31 (use-geo_0_31 feature for geometry distance APIs) |
| **Minimum toolchain** | Rust 1.75 (rust-version in Cargo.toml), edition 2021 |
| **Platforms** | any platform Rust targets; no SIMD or architecture-specific code seen. Python bindings published on PyPI as geoindex-rs |
| **Thread safety** | not documented. The built RTree/KDTree is an immutable Vec&lt;u8&gt; plus metadata and queries take &self, so concurrent reads look safe, but the docs do not say so |
| **Drop-in for the baseline** | partial: replaces rstar::RTree::bulk_load plus envelope-intersection and nearest-neighbor queries for static 2D data, but with a different API (builder with a preset item count, index-returning queries) and no insert/remove or custom object types |

## Gotchas

- RTreeIndex::neighbors(x, y, max_results, max_distance) ranks by squared Euclidean distance and compares that against max_distance without squaring it (upstream flatbush squares maxDistance), so pass the squared radius there; neighbors_with_distance with EuclideanDistance takes a plain radius
- RTreeBuilder::new takes the exact item count up front and finish() asserts that exactly that many boxes were added
- The README calls it safe Rust, but the hot search loop uses unsafe get_unchecked, and RTreeRef::new_unchecked skips buffer validation; use try_new for untrusted buffers
- Open issue #148: KDTree::within uses x^2 + y^2 &lt;= r^2, which loses precision for extremely small coordinates and radii (e.g. 1e-308)

## Known shortcomings

- One query only; the rstar timed loop includes a Vec clone; Rust port of the flatbush/kdbush layout.
- README bench numbers come from a 2023 'Quick bench' commit, before the v0.3.2 search optimization; rstar version then unstated. RTreeIndex::neighbors compares squared distance to an unsquared max_distance (flatbush squares it). README says safe Rust but search uses unsafe get_unchecked. Open #148: KDTree within loses precision for tiny values. Rust; no C ABI.

## Caveats and trade-offs

The author says it is just one benchmark and recommends benchmarking on your own data. Hardware, dataset size and compiler settings are not stated. A static packed index is compared against a dynamic R-tree's bulk load, which is not like-for-like on features (rstar supports updates). Search is one fixed bounding-box query (-112.007, 40.634, -111.921, 40.694) on one dataset, so the 33% figure rests on one query; the bench does assert that both return the same result count. The rstar construction closure clones the input Vec (rect_vec.to_vec()) inside the timed loop, while geo-index builds from a borrowed slice, which adds a copy to rstar's time. The rstar dev-dependency is 0.12. The bench labels geo-index runs 'flatbush' because the tree is a Rust port of mourner's flatbush and kdbush layouts. Derived from page data: construction 1.97x, search 1.32x.

Trees are immutable (no insert or delete after build), fully packed single-buffer layout with ABI-stable memory shared with Python and the flatbush/kdbush JavaScript libraries. Hilbert and STR sort methods. Also ships a k-d tree.

## Maintenance

Active (v0.4.0 released 2026-09-09, last commit 2026-09-15, now under the georust org), dual MIT/Apache-2.0 licensed and published on crates.io and PyPI, with recent fixes for stack overflows, empty-tree panics and kNN distance bugs.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README's Criterion output compares geo-index construction and search against rstar::RTree::bulk_load, and the code is public (benches/rtree.rs reading benches/bounds.raw). No CPU, rustc version or flags are stated (Cargo.toml has no profile override), so it is first-party with partial methodology: C.
- **Verifier notes:** Every number matches the README Benchmarks section. Metadata from github.com: MIT OR Apache-2.0 (Cargo.toml), 200 stars, 100 commits, last commit 2026-09-15 (v0.4.0), not a fork or archived. geo-index ports the flatbush/kdbush memory layout, and KDBush (JS) is in this same wave. It is a separate implementation in another language, not a wrapper, so I did not file it as a duplicate.
- **Fields the verifier corrected:** `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://github.com/georust/geo-index>
  - <https://github.com/georust/geo-index/commits/main>
  - <https://raw.githubusercontent.com/georust/geo-index/HEAD/README.md>
  - <https://raw.githubusercontent.com/georust/geo-index/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/georust/geo-index/HEAD/benches/rtree.rs>
- **Sources the enricher read:**
  - <https://github.com/georust/geo-index>
  - <https://github.com/georust/geo-index/tree/main/src/rtree>
  - <https://github.com/georust/geo-index/issues>
  - <https://github.com/georust/geo-index/issues/148>
  - <https://github.com/georust/geo-index/blame/main/README.md>
  - <https://raw.githubusercontent.com/georust/geo-index/HEAD/README.md>
  - <https://raw.githubusercontent.com/georust/geo-index/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/georust/geo-index/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/georust/geo-index/HEAD/benches/rtree.rs>
  - <https://raw.githubusercontent.com/georust/geo-index/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/georust/geo-index/HEAD/src/rtree/mod.rs>
  - <https://raw.githubusercontent.com/georust/geo-index/HEAD/src/rtree/builder.rs>
  - <https://raw.githubusercontent.com/georust/geo-index/HEAD/src/rtree/index.rs>
  - <https://raw.githubusercontent.com/georust/geo-index/HEAD/src/rtree/trait.rs>
  - <https://raw.githubusercontent.com/georust/geo-index/HEAD/src/rtree/sort/hilbert.rs>
  - <https://raw.githubusercontent.com/georust/geo-index/HEAD/src/rtree/sort/str.rs>
  - <https://raw.githubusercontent.com/georust/geo-index/HEAD/src/kdtree/mod.rs>
  - <https://raw.githubusercontent.com/mourner/flatbush/HEAD/index.js>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/georust/geo-index`) · [data/wave8/enrich/raw/github_com_georust_geo_index.json](../../../data/wave8/enrich/raw/github_com_georust_geo_index.json) (enrichment confidence 0.8)

</details>
