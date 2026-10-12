# Kiddo (Rust k-d tree)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0 OR MIT` · 🟢 active

> Rust k-d tree for low-dimensional exact/approximate NN; 1.2-1.5x faster queries than nabo-rs; no C/C++ API.

| | |
|---|---|
| **Beats** | pykdtree, scipy.spatial.KDTree and sklearn KDTree (Python), nabo-rs and FNNTW (Rust); no C++ baseline (nanoflann, PCL, CGAL) is benchmarked |
| **Claimed result** | Derived from page data (all-benchmarks.json, 3-D f64, 1,000,000 points, Criterion mean in ns per 1,000-query iteration): Query Nearest 1: Kiddo_v5_immutable_dynamic 49,798 (Kiddo_v3_immutable 44,366) vs nabo 71,993 (about 1.45x), pykdtree 77,187 (about 1.55x), FNNTW 80,818, scipy 907,836 (about 18x), sklearn 1,911,706 (about 38x). Query Nearest 10: Kiddo_v3_std 109,819 vs nabo 131,085 (about 1.2x), pykdtree 199,638 (about 1.8x), scipy 2,227,477 (about 20x). Query Nearest 100: Kiddo_v5_immutable_dynamic 550,945 vs nabo 677,895 (about 1.2x), pykdtree 1,789,125 (about 3.2x). Construction is not faster: Kiddo_v5_immutable_dynamic 161.4 ms and Kiddo_v3_std 124.6 ms vs pykdtree 92.3 ms (scipy 294.8 ms). The scipy and sklearn ratios compare parallel against single-threaded code (see caveats). |
| **Workload** | Nearest-1/10/100, within-radius and construction on 100 to 10M points, 2-4 dimensions, f32/f64, 1,000 query points per Criterion iteration (companion repo sdd/kd-tree-comparison). The bench code generates uniform random points in the unit hypercube (rand::random, np.random.rand), although the Kiddo README says the points lie on a unit sphere. |
| **Metric** | latency |
| **Hardware** | Ryzen 5900X (12/24 core), 32 GB DDR4 3600 MHz (kd-tree-comparison Readme) |
| **Compiler and flags** | cargo criterion; rustc version and RUSTFLAGS not stated. The comparison Cargo.toml builds kiddo_v5 with the nightly-only 'simd' feature. |
| **Adoption** | 176 stars, 669 commits; crate kiddo v6.3.0 |
| **Last commit** | 2026-09-06 |
| **Links** | [repository](https://github.com/sdd/kiddo) · [benchmark](https://raw.githubusercontent.com/sdd/kd-tree-comparison/HEAD/all-benchmarks.json) |

## Verdict

The author's Criterion suite (sdd/kd-tree-comparison, Ryzen 5900X, 32 GB, rustc version and flags not stated) times 1,000 queries per iteration on uniform random points (not the unit sphere the README describes). For 1M 3-D f64 points, Kiddo v3/v5 nearest-1/10/100 is about 1.2-1.45x faster than nabo-rs and 1.5-3.2x faster than pykdtree, and construction is slower than pykdtree (derived from page data). The 18-38x over scipy and sklearn compares rayon-parallel queries with single-threaded ones. The repo has an FFI harness against nanoflann, ALGLIB and Pkd-tree, but no results from it were found on a reachable page (sdd.github.io is blocked), so there is no measured C++ comparison.

## Use it when

- Rust services and pipelines doing many nearest-neighbour or radius queries on static 2-D to 4-D point sets (geocoding, star-catalogue cross-matching, colour-palette lookup, simulation neighbourhoods)
- Prebuilt trees loaded from disk at startup: ImmutableKdTree with rkyv 0.8 supports zero-copy loading from memory-mapped files
- Batched query workloads on multi-core machines, where query_batch spreads the queries over rayon
- Periodic-boundary simulations (cosmology, molecular boxes) that need wrapped distance queries built in
- Integer or fixed-point coordinates, which most C++ k-d trees do not support directly

## Skip it when

- C or C++ projects: there is no C API or header, so you must write and maintain an FFI layer (the crate is out of this catalog's C/C++ scope)
- High-dimensional vectors (tens to thousands of dimensions): the README says plain k-d trees are the wrong structure there
- Heavy insert/delete churn: MutableKdTree does no dynamic rebalancing, and the README suggests periodic rebuilds
- When construction time dominates: on 1M 3-D f64 points Kiddo builds in 125-161 ms vs pykdtree's 92 ms in the author's suite
- Stable-only toolchains that need the fastest path: the SIMD stem strategies require nightly Rust, and v6 needs Rust 1.89+

## How it is fast

Interior 'stem' nodes are stored implicitly in a cache-friendly array layout (Eytzinger order, and in v6 the alternative 'Donnelly' block ordering with configurable prefetch) and points live in fixed-size leaf buckets, so descent is index arithmetic rather than pointer chasing. Leaf scans and, in the Donnelly SIMD strategies, descent, pruning and backtracking use hand-written AVX2, AVX-512, NEON and wasm simd128 kernels (the 'simd' feature needs nightly Rust). The immutable tree is balanced at construction, and batch queries and construction are parallelised over the rayon thread pool by default.

## Compared with alternatives

Pick Kiddo only if your code is Rust (or you will maintain an FFI shim) and you query static low-dimensional data in batches. For C++ use nanoflann, PicoTree or libnabo (whose Rust port nabo-rs Kiddo beats by 1.2-1.5x on queries); none of these C++ libraries appears in Kiddo's published results.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | Default features pull rayon (multi-threaded) and fixed; optional serde, rkyv 0.8, half (f16). The C++ competitor benches vendor nanoflann, ALGLIB and Pkd-tree behind a feature |
| **Minimum toolchain** | Rust 1.89 (v6 MSRV; v5 needs 1.85); 'simd' feature needs nightly |
| **Platforms** | any Rust target; SIMD kernels for x86-64 AVX2/AVX-512, aarch64 NEON and wasm32 simd128; disabling multi-threaded supports WASM, embedded and single-core targets |
| **Thread safety** | Queries take a shared reference and batch queries run on rayon by default; explicit Send/Sync guarantees are not documented in the README. Batch scheduling order is deliberately unspecified (results stay indexed by input position) |
| **Drop-in for the baseline** | no |

## Gotchas

- v6 (2026-07-27) is a near rewrite with a builder query API: v5 calls such as nearest_one and within must be ported, rkyv 0.7 support is gone, and every published comparison number is for v1-v5
- Many points sharing one coordinate on an axis have broken trees before: issue #475 (v5.3.2) reports MutableKdTree add panicking when 33 points share an axis value with bucket size 32. It is closed, but no fix is shown; test with your data or raise the bucket size
- Issue #474 (v5.3.2, rkyv feature) reported an unsound conversion that freed a 128-byte-aligned allocation with 8-byte alignment through safe API; closed, fix not confirmed. v6.0.1 also fixed several fuzzer-found SIMD over-pruning and construction bugs, so stay on the latest 6.x
- Batch queries are multi-threaded by default; a benchmark against single-threaded code (as the published scipy/sklearn comparisons do) measures threading, not the tree

## Known shortcomings

- Rust only with no C/C++ API, outside the C++ scope. Kiddo/nabo/FNNTW queries run rayon-parallel against single-threaded scipy/sklearn, so the 18-38x is mostly threading. Repo has a nanoflann FFI bench but no published results.
- No published C++ comparison. #475 (MutableKdTree add panics when many points share one axis value) and #474 (unsound memory free converting to the rkyv type) were reported on 5.3.2 and closed with the fix unconfirmed.

## Caveats and trade-offs

Rust library with no C/C++ API, so it is outside the catalog's C/C++ scope. No published numbers against nanoflann or any C++ library: the comparison repo tests only Rust and Python libraries. The Kiddo repo does have an FFI harness for nanoflann, ALGLIB and Pkd-tree (benches/profile_cpp_competitors.rs, charted by scripts/chart_cpp_competitor_results.py), but no results were found on any reachable page; the results site sdd.github.io is blocked. Parallel against serial: the Kiddo, nabo and FNNTW benches run the 1,000 queries per iteration with rayon par_iter on a 12-core/24-thread CPU, while scipy's KDTree.query is called with the default workers=1 (the bench comments 'workers=-1 makes this slower?') and sklearn's is single-threaded, so the 18-38x over scipy and sklearn mostly measures threading. pykdtree (a C extension) may use OpenMP, so it is the closest like-for-like competitor (about 1.5-3x on queries, slower on construction). At 1,000 queries per iteration (about 50-80 microseconds), rayon dispatch and Python call overheads are a sizeable share of each sample. Published numbers cover Kiddo v1-v5 (last updated 2024-12-04); the current release is v6.3.0. The README says the data lie on a unit sphere but the bench code uses uniform cube data. The author benchmarks his own library (disclosed). all-benchmarks.json has duplicate 'Query within radius' rows for Kiddo_v1 and Kiddo_v2 with different values. kd-tree-comparison's Cargo.toml builds kiddo_v5 with the nightly-only 'simd' feature.

Rust crate, not callable from C++ without FFI work, so it is outside the C++-first scope and flagged cross-language. Low-dimensional (2-4D) exact and approximate NN; ImmutableKdTree is best for static data, MutableKdTree has no dynamic rebalancing; batch queries multi-threaded by default (rayon); SIMD path needs nightly Rust.

## Maintenance

Actively maintained (v6.3.0 on 2026-09-06, CI, fuzzing, 176 stars), dual MIT/Apache-2.0 licensed; a strong choice in Rust, but outside the C/C++ scope with no C ABI.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The author's own Criterion suite (sdd/kd-tree-comparison benches/\*.rs, results in all-benchmarks.json) names the CPU (Ryzen 5900X) but not the rustc version or RUSTFLAGS, and the competitors are Python/Rust libraries, not the category's baselines, so C.
- **Verifier notes:** Out of scope by language (Rust, no C/C++ API); evidence judged anyway: same-row numbers in the record match all-benchmarks.json exactly. Shortcoming worth recording: the headline scipy/sklearn gaps compare rayon-parallel queries against single-threaded queries. Metadata confirmed: MIT OR Apache-2.0, 176 stars, 24 forks, 669 commits, v6.3.0, last commit 2026-09-06.
- **Fields the verifier corrected:** `workload`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier; enrichment
- **Pages the verifier opened:**
  - <https://github.com/sdd/kiddo>
  - <https://github.com/sdd/kiddo/commits/master>
  - <https://github.com/sdd/kiddo/tree/master/scripts>
  - <https://raw.githubusercontent.com/sdd/kiddo/HEAD/README.md>
  - <https://raw.githubusercontent.com/sdd/kiddo/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/sdd/kiddo/HEAD/benches/profile_cpp_competitors.rs>
  - <https://raw.githubusercontent.com/sdd/kiddo/HEAD/scripts/chart_cpp_competitor_results.py>
  - <https://raw.githubusercontent.com/sdd/kd-tree-comparison/HEAD/all-benchmarks.json>
  - <https://raw.githubusercontent.com/sdd/kd-tree-comparison/HEAD/Readme.md>
  - <https://raw.githubusercontent.com/sdd/kd-tree-comparison/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/sdd/kd-tree-comparison/HEAD/benches/nearest_one_pykdtree.rs>
  - <https://raw.githubusercontent.com/sdd/kd-tree-comparison/HEAD/benches/nearest_one_kiddo_v5_immutable.rs>
  - <https://raw.githubusercontent.com/sdd/kd-tree-comparison/HEAD/benches/nearest_one_nabo.rs>
  - <https://raw.githubusercontent.com/sdd/kd-tree-comparison/HEAD/benches/nearest_one_fnntw.rs>
  - <https://raw.githubusercontent.com/sdd/kd-tree-comparison/HEAD/benches/nearest_one_scipy.rs>
  - <https://raw.githubusercontent.com/sdd/kd-tree-comparison/HEAD/benches/nearest_one_sklearn.rs>
  - <https://raw.githubusercontent.com/sdd/kd-tree-comparison/HEAD/benches/nearest_n_kiddo_v3_std.rs>
  - <https://raw.githubusercontent.com/sdd/kd-tree-comparison/HEAD/benches/nearest_n_pykdtree.rs>
  - <https://github.com/sdd/kd-tree-comparison/commits>
- **Sources the enricher read:**
  - <https://github.com/sdd/kiddo>
  - <https://github.com/sdd/kiddo/issues?q=is%3Aissue>
  - <https://github.com/sdd/kiddo/issues/474>
  - <https://github.com/sdd/kiddo/issues/475>
  - <https://raw.githubusercontent.com/sdd/kiddo/HEAD/README.md>
  - <https://raw.githubusercontent.com/sdd/kiddo/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/sdd/kiddo/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/sdd/kiddo/HEAD/benches/profile_cpp_competitors.rs>
  - <https://raw.githubusercontent.com/sdd/kd-tree-comparison/HEAD/Readme.md>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/sdd/kiddo`) · [data/wave8/enrich/raw/github_com_sdd_kiddo.json](../../../data/wave8/enrich/raw/github_com_sdd_kiddo.json) (enrichment confidence 0.7)

</details>
