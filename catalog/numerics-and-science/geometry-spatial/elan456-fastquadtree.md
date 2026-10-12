# fastquadtree

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟢 active

> Rust-core Python quadtree for points and boxes; NumPy-return path about 35x faster than Rtree, 4.5x than Shapely STRtree.

| | |
|---|---|
| **Beats** | Rtree (Python wrapper of libspatialindex R-tree) and Shapely STRtree (GEOS); also PyQtree and other Python quadtrees |
| **Claimed result** | docs/benchmark.md (500,000 points, 500 queries): total time fastquadtree numpy path 0.068 s (build 0.052, query 0.017), list path 0.285 s (build 0.054, query 0.231), Shapely STRtree 0.309 s (build 0.200, query 0.110), Rtree 2.351 s (build 1.805, query 0.546), PyQtree 2.909 s. That is 42.52x vs PyQtree (numpy path) and 10.20x (list path). Derived from page data: about 34.6x faster total than Rtree on the numpy path and 8.2x on the list path; against Shapely STRtree, 4.5x total on the numpy path but only 1.08x on the list path, and STRtree's query time (0.110 s) beats the list path's (0.231 s). The drop-in pyqtree shim takes 1.127 s vs 11.647 s for the original pyqtree (10.333x). |
| **Workload** | Build 500,000 points and run 500 range queries; total time per library, Python spatial indexes (bounds 0-1000, max 128 points per node, max depth 16). |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 7 3700X (16 threads), 31.3 GB RAM, CachyOS Linux |
| **Compiler and flags** | CPython 3.14.5. The Rust engine is built via PyO3/maturin with a Cargo.toml release profile of opt-level=3, lto=thin, codegen-units=1, panic=abort. The rustc version is not stated (MSRV 1.89). |
| **Adoption** | 33 stars |
| **Last commit** | 2026-06-22 |
| **Links** | [repository](https://github.com/Elan456/fastquadtree) · [benchmark](https://github.com/Elan456/fastquadtree/blob/main/docs/benchmark.md) |

## Verdict

The first-party cross-library benchmark (CPython 3.14.5, AMD Ryzen 7 3700X, CachyOS; rustc version not stated) builds 500,000 random integer points in a 1000x1000 box (so many duplicates) and runs 500 random windows, many of them large, taking the median of 3 repeats. Totals: fastquadtree query_np 0.068 s, list path 0.285 s, Shapely STRtree 0.309 s, Rtree 2.351 s and PyQtree 2.909 s, so about 34.6x over Rtree and 4.5x over STRtree with NumPy returns (derived from page data). Rtree was built by stream bulk-loading 1x1 boxes from a Python generator, STRtree's build time includes converting the Python list to NumPy and Shapely points, and query cost is dominated by materializing results.

## Use it when

- Python programs that index many 2D points or boxes and run many window queries, especially with NumPy arrays on both sides (insert_many_np in, query_np out)
- Replacing pyqtree without code changes: the shim measured 1.127 s versus 11.647 s for the original on 500,000 items and 500 queries
- Games and simulations (pygame broadphase culling, moving-object collision) with frequent inserts and deletes inside known fixed bounds
- Caching or sharing a prebuilt index across processes: rebuilding 1M points from bytes took 7.1 ms versus 88.8 ms to reinsert them
- Pyodide/WebAssembly or ARM targets: wheels exist for manylinux x86_64/aarch64/armv7l, macOS universal2, Windows amd64 and Pyodide wasm32

## Skip it when

- C++ or Rust consumers: it is a Python extension with no documented C/C++ or Rust API (a Rust API request, issue #11, was closed without a visible answer)
- When results must come back as Python lists: the list path's query time (0.231 s) loses to Shapely STRtree (0.110 s) and total time is only about 1.08x better (derived from page data)
- Data that can fall outside the initial root bounds: bounds are fixed, out-of-bounds inserts are rejected, and dynamic root bounds (issue #17) were closed as not planned
- Large-k nearest-neighbour queries: nearest_neighbors(k) reruns a full single-nearest search k times while excluding already-picked IDs, so cost grows with k
- Polygons or exact geometry predicates: only points and axis-aligned boxes are indexed; use Shapely STRtree or GEOS for geometry-level tests

## How it is fast

The tree is a plain pointer-based region quadtree in Rust: leaves hold up to capacity items in a Vec, then split into four children (Box&lt;[QuadTree; 4]&gt;) down to a dtype-dependent max depth, and deletes merge underfull nodes locally. Range queries walk the tree iteratively with a SmallVec stack and switch to report-all mode for nodes fully inside the window, which skips per-item tests. Queries release the GIL and collect results into flat Rust vectors, and query_np hands them back as NumPy arrays instead of building per-hit Python tuples; most of the speedup over pure-Python quadtrees and over the list path comes from avoiding Python object creation. The release build uses opt-level 3, thin LTO, codegen-units=1 and panic=abort.

## Compared with alternatives

The catalogued siblings are C++/Rust/JS libraries (nanoflann, PH-tree, KDBush, RBush, geo-index), none callable from Python as a drop-in; pick fastquadtree when you are in Python and need a mutable point/box index with NumPy I/O. Pick geo-index or a C++ kd-tree such as nanoflann for static data in compiled code.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none at runtime (NumPy optional, for the \*_np methods); Rust build dependencies: pyo3 0.28 (abi3-py39), numpy 0.28, smallvec, wincode, num-traits |
| **Minimum toolchain** | Python 3.9+ (CPython, abi3 wheels); building from source needs Rust 1.89+ and maturin |
| **Platforms** | Prebuilt wheels for Linux x86_64/aarch64/armv7l (manylinux_2_28), macOS x86_64/arm64, Windows amd64, Pyodide wasm32; no SIMD-specific code |
| **Thread safety** | not documented; queries release the GIL, and PyO3's per-call borrow checking means a mutation from another thread during a query should raise an error rather than corrupt the tree (inferred from the bindings, not stated) |
| **Drop-in for the baseline** | partial — fastquadtree.pyqtree.Index is a drop-in for PyQtree, but the API differs from Rtree (libspatialindex) and Shapely STRtree |

## Gotchas

- The default dtype is f32, so large projected or geographic coordinates lose precision; pass dtype='f64' when you need it
- With dtype i32 or i64, squared distances in nearest-neighbour search are computed in the coordinate type itself. The release profile does not enable overflow checks, so i32 trees should return wrong neighbours once distances exceed about 46,340 units (from reading geom.rs and Cargo.toml, not tested)
- insert_many raises TypeError on NumPy input, so you must call insert_many_np explicitly. Containment is half-open (min inclusive, max exclusive), so points exactly on the max edge of the root bounds are rejected
- Serialized blobs are version-sensitive: data written by bincode-based releases (v2.2 and earlier) cannot be loaded by current wincode-based ones, and from_bytes enforces a 64 MiB preallocation limit unless you raise it

## Known shortcomings

- Vs Shapely STRtree only 4.5x on the numpy path and 1.08x on the list path; Python package.
- Python-only package (Rust core, no C++ or Rust API), so not callable from C++. Possible correctness bug from code reading (untested): i32/i64 kNN computes squared distances in the coordinate type without overflow checks in release, so i32 should give wrong neighbours past \~46,340 units. kNN reruns 1-NN k times. Rtree baseline was stream bulk-loaded (record caveat said one-by-one inserts). Bench points are integers on a 1000x1000 grid (many duplicates) and timing is dominated by result materialization.

## Caveats and trade-offs

First-party Python benchmark. The best number uses the numpy return path; the list path, which is comparable to Rtree's list returns, is much slower and loses to Shapely STRtree on query time. The Shapely STRtree row uses numpy points and returns. Both sides include Python call overhead, and Rtree inserts go one at a time through ctypes. The rustc version is not stated. Only 500 queries are run, on uniform point data rather than extended geometries.

Python package with a Rust core; point and rectangle quadtree with numpy bulk paths, optional object tracking, serialization to bytes. Quadtree rather than R-tree: no balanced bulk-loading guarantees.

## Maintenance

Active single-maintainer project (v2.4.2 on PyPI 2026-06-22, 303 commits, 33 stars, 7 issues all closed), MIT-licensed, with 100% test coverage claimed; usable from Python only.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party Python benchmark against PyQtree, Rtree (libspatialindex) and Shapely STRtree (GEOS). The code is public (benchmarks/cross_library_bench.py with benchmarks/quadtree_bench/main.py), and the CPU (Ryzen 7 3700X) and CPython 3.14.5 are stated. Cargo.toml gives the release profile, but the rustc version is not stated, so it is not A.
- **Verifier notes:** Every number in the record matches docs/benchmark.md (the README carries the same table). I added the Shapely STRtree comparison, the only native incumbent that is close: fastquadtree wins only on the numpy path. Metadata checked on github.com: MIT, 33 stars, 2 forks, not a fork or archived, 303 commits, last commit 2026-06-22.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://github.com/Elan456/fastquadtree>
  - <https://github.com/Elan456/fastquadtree/commits/main>
  - <https://raw.githubusercontent.com/Elan456/fastquadtree/main/docs/benchmark.md>
  - <https://raw.githubusercontent.com/Elan456/fastquadtree/main/README.md>
  - <https://raw.githubusercontent.com/Elan456/fastquadtree/main/LICENSE>
  - <https://raw.githubusercontent.com/Elan456/fastquadtree/main/Cargo.toml>
  - <https://raw.githubusercontent.com/Elan456/fastquadtree/main/benchmarks/cross_library_bench.py>
  - <https://raw.githubusercontent.com/Elan456/fastquadtree/main/pyproject.toml>
- **Sources the enricher read:**
  - <https://github.com/Elan456/fastquadtree>
  - <https://github.com/Elan456/fastquadtree/tree/main/src>
  - <https://github.com/Elan456/fastquadtree/tree/main/benchmarks/quadtree_bench>
  - <https://github.com/Elan456/fastquadtree/issues?q=is%3Aissue>
  - <https://github.com/Elan456/fastquadtree/issues/11>
  - <https://github.com/Elan456/fastquadtree/issues/17>
  - <https://raw.githubusercontent.com/Elan456/fastquadtree/main/README.md>
  - <https://raw.githubusercontent.com/Elan456/fastquadtree/main/docs/benchmark.md>
  - <https://raw.githubusercontent.com/Elan456/fastquadtree/main/Cargo.toml>
  - <https://raw.githubusercontent.com/Elan456/fastquadtree/main/pyproject.toml>
  - <https://raw.githubusercontent.com/Elan456/fastquadtree/main/LICENSE>
  - <https://raw.githubusercontent.com/Elan456/fastquadtree/main/src/lib.rs>
  - <https://raw.githubusercontent.com/Elan456/fastquadtree/main/src/quadtree.rs>
  - <https://raw.githubusercontent.com/Elan456/fastquadtree/main/src/rect_quadtree.rs>
  - <https://raw.githubusercontent.com/Elan456/fastquadtree/main/src/geom.rs>
  - <https://raw.githubusercontent.com/Elan456/fastquadtree/main/benchmarks/cross_library_bench.py>
  - <https://raw.githubusercontent.com/Elan456/fastquadtree/main/benchmarks/quadtree_bench/engines.py>
  - <https://raw.githubusercontent.com/Elan456/fastquadtree/main/benchmarks/quadtree_bench/runner.py>
  - <https://raw.githubusercontent.com/Elan456/fastquadtree/main/benchmarks/quadtree_bench/main.py>
  - <https://pypi.org/pypi/fastquadtree/json>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/elan456/fastquadtree`) · [data/wave8/enrich/raw/github_com_elan456_fastquadtree.json](../../../data/wave8/enrich/raw/github_com_elan456_fastquadtree.json) (enrichment confidence 0.75)

</details>
