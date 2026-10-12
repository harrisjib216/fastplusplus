# iOverlay (Rust polygon boolean overlay engine)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟢 active

> Rust 2D polygon boolean engine (union/intersect/difference/xor, offsetting) that outscales Clipper2 on very large, intersection-heavy inputs.

| | |
|---|---|
| **Beats** | Clipper2 (C++ polygon clipping library, v1.4.0); also Boost.Geometry (Boost 1.86.0) |
| **Claimed result** | Performance Comparison page (seconds; 3 GHz 6-Core Intel Core i5; iOverlay Rust v1.9.0 multithreading on/off, iOverlay Swift v1.13.0, Clipper2 C++ v1.4.0, Boost C++ 1.86.0). Checkerboard test, 8,384,513 squares: Rust mt on 33.742 s, Rust mt off 38.640 s, Clipper2 644.338 s, about 19.1x (mt on) and 16.7x (mt off) faster (derived from page data); at 2,095,105 squares 7.94 s / 9.29 s versus 73.31 s. Not Overlap, 8,384,513 squares: 9.60 s / 13.51 s versus 167.97 s (17.5x / 12.4x, derived). Windows, 8,388,608: 12.06 s / 15.48 s versus 265.39 s (22.0x / 17.1x, derived). Spiral, 1,048,576: 3.23 s / 3.19 s versus 259.87 s (about 80x, derived). Lines Net 4096: 7.70 s / 7.51 s versus 45.93 s (about 6x, derived). Nested Squares 65,536: 2.20 s / 4.03 s versus 3502.23 s for Clipper2. Clipper2 is as fast or faster on small inputs (for example Checkerboard 481 squares 1.017 ms versus 1.117 ms; Lines Net up to 256; Spiral up to 1024). Boost is far slower where it ran (Checkerboard 32,513 squares 412.6 s versus 0.092 s for Rust mt off) and has no results for the largest sizes. The repo README chart separately reports iOverlay-internal relative times only (Apple M4, 24 GB, geometric mean, i32 multithreading off = 1.00x: i16 off 0.92x, i64 off 1.30x, i16 on 0.85x, i32 on 0.86x, i64 on 1.08x). |
| **Workload** | Checkerboard polygon boolean-operation test with up to 8,384,513 squares, iOverlay (Rust, multithreading feature on) versus Clipper2, as reported in the project's performance comparison page. |
| **Metric** | latency |
| **Hardware** | Comparison page: 3 GHz 6-Core Intel Core i5, 40 GB 2667 MHz DDR4 (exact CPU model not given). Repo README relative-time chart: Apple M4, 24 GB. |
| **Compiler and flags** | Benchmark apps in iShape-Rust/iOverlayPerformance: ClipperApp/build.sh runs cmake -DCMAKE_BUILD_TYPE=Release (CMake default Release flags, C++17, Clipper2 sources compiled in); BoostApp CMakeLists sets C++17 and no build type; iOverlayAppRust/Cargo.toml release profile opt-level 3, lto false, codegen-units 1. Compiler names and versions (C++ and Rust) not stated. |
| **Adoption** | 211 stars, 18 forks; i_overlay crate 9.0 million total downloads and 4.2 million recent downloads on crates.io (API read 2026-10-02); README says it powers polygon boolean operations in georust/geo |
| **Last commit** | 2026-09-24 |
| **Links** | [repository](https://github.com/iShape-Rust/iOverlay) · [benchmark](https://ishape-rust.github.io/iShape-js/overlay/performance/performance.html) |

## Verdict

First-party comparison page: iOverlay Rust v1.9.0 versus Clipper2 C++ v1.4.0 (and Boost 1.86) on six synthetic grid tests, on a '3 GHz 6-Core Intel Core i5' with no compiler named; single-thread iOverlay is 16.7x faster on 8,384,513 checkerboard squares (38.6 s vs 644.3 s), 12.4x on Not Overlap, 17.1x on Windows, 6.1x on Lines Net 4096, 81x on Spiral 1M and 869x on Nested Squares 65,536 (ratios derived from page data), while Clipper2 wins or ties at small sizes. The numbers are for an old iOverlay release (current 9.0.0) and Boost's build type is unset.

## Use it when

- Rust (or WASM/Swift via the iShape bindings) code that needs polygon booleans on large inputs: hundreds of thousands to millions of edges with dense intersections, where the comparison page shows 2.5x (130k squares) to 17x (8.4M squares) over Clipper2 single-threaded.
- Deeply nested or spiral-like inputs, where Clipper2 degraded sharply on the comparison page (Nested Squares 65,536: 4.03 s vs 3502 s; Spiral 1M: 3.19 s vs 260 s).
- Unioning many shapes at once (simplify_shape) instead of chaining pairwise overlays.
- Pipelines that want deterministic integer-grid results or OGC-valid output (OverlayOptions::ogc()), or that already use georust/geo, whose boolean ops are built on it.
- no_std targets: the crate is #![no_std] with alloc.

## Skip it when

- Small inputs: on the comparison page Clipper2 is equal or faster at a few hundred to about a thousand elements (Checkerboard 481 squares 1.017 ms vs 1.117 ms; Lines Net 64: 0.75 ms vs 1.01 ms; Spiral 1024: 2.94 ms vs 3.57 ms).
- C++ codebases wanting a supported library: there is no C/C++ API; iShape-ffi is an undocumented staticlib bridge (0 stars, built against sibling-repo paths) aimed at the Swift binding.
- Workloads needing exact arithmetic or no snapping: results are rounded to an integer grid and intersections are snapped within a growing radius (Precision setting), so vertices can move slightly.
- Integer inputs outside -2^(N-2)..2^(N-2)-1 for the chosen engine: the integer APIs do not check the bound, and overflow gives wrong results.
- Risk-averse production use without your own tests: 2026 issues include panics (#88 i16 Frag overflow, #91 hole binding), a Frag strategy dropping a filled region (#87), an infinite loop in buffering (#37) and non-OGC union output (#57); all are closed, but they show the edge-case surface.

## How it is fast

All geometry runs on integer coordinates: segments are sorted (i_key_sort, parallel radix-style sort when allowed), coincident edges merged, then split at intersections by one of three solvers chosen by size: an all-pairs list below about 4,000 segments, a sweep over an interval tree of expiring segments (i_tree SegExpTree), or, above 16,000 segments, a grid of vertical strips where each strip is split independently (in parallel with rayon when the allow_multithreading feature is on). Intersections are snapped with a growing snap radius and the split repeats until stable, after which winding counts are filled and contours extracted from the graph. The comparison page's large factors over Clipper2 appear where Clipper2's run time grows much faster than linearly with intersection count.

## Compared with alternatives

Pick iOverlay over clipper2next (a C++ Clipper2 fork with about 1.6x geometric-mean gain) when inputs are large and intersection-dense enough to hit Clipper2's super-linear growth and a Rust dependency is acceptable; stay with clipper2next or Clipper2 for C++ drop-in use and small polygons. For offsetting with true arcs pick CavalierContours, and for GEOS-compatible unions in Python/WASM pipelines qdgeo is the closer fit.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | i_float, i_shape, i_tree, i_key_sort (same author); rayon optional via allow_multithreading; optional glam and serde features |
| **Minimum toolchain** | Rust 1.88 (edition 2024) for i_overlay 9.0.0 |
| **Platforms** | any Rust target; #![no_std] + alloc; WASM via iShape-js; multithreading needs rayon (std) |
| **Thread safety** | not documented; operations take owned or borrowed inputs and build their own overlay object, and Overlay objects are reused through &mut self, so one object per thread |
| **Drop-in for the baseline** | no |

## Gotchas

- Multithreading is off by default; you must enable the allow_multithreading Cargo feature, and parallel sorting kicks in only above par_sort_min_size (32,768 by default). Issue #65 (closed) reported the feature not enabling parallel sort in i_key_sort.
- Default float conversion uses the i32 engine with a conservative coordinate budget; pick i64 (overlay_as::&lt;i64&gt; or FloatOverlay::&lt;_, i64&gt;) when bounds or precision demand it, and expect i64 to be about 30 percent slower (README chart).
- Polygon offsetting assumes valid input (no self-intersections, CCW outer and CW holes); run simplify_shape first otherwise. Integer-math miter joins clip corners sharper than 5 degrees.
- Infallible float APIs panic on non-finite or out-of-range coordinates; the fixed-scale APIs return errors instead.

## Known shortcomings

- Tier C: the performance page (verified from its source in iShape-Rust/iShape-js docs, github.io blocked) gives the CPU only as '3 GHz 6-Core Intel Core i5' and names no compiler; baselines are Clipper2 v1.4.0 and Boost 1.86. crates.io shows 9.0M downloads.
- No C/C++ API: iShape-ffi is an undocumented 0-star staticlib bridge that builds from sibling paths. The measured version is v1.9.0 while the crate is now 9.0.0. Clipper2 ties or wins below about 1k elements. 2026 correctness issues, all closed: #87 Frag strategy dropped a filled region, #88 i16 overflow panic, #91 hole-binding panic, #37 buffer infinite loop. The integer APIs do not check coordinate range.

## Caveats and trade-offs

Rust library (C++ is only the baseline). The comparison page lives on ishape-rust.github.io, which is EGRESS_BLOCKED; its numbers were read from the page's checked-in mdBook output at iShape-Rust/iShape-js docs/overlay/performance/performance.html via raw.githubusercontent.com. First-party benchmark by the iOverlay author: the CPU is described only as '3 GHz 6-Core Intel Core i5', no compiler or toolchain is named, BoostApp sets no CMake build type, and ClipperApp also carries a cmake-build-debug directory, so it is not established that every baseline ran an optimised build (build.sh does request Release for Clipper2). Clipper2 runs single-threaded; the 'mt on' column uses iOverlay's multithreading, while 'mt off' is the fair single-thread comparison (16.7x on the largest checkerboard). The measured versions are old: iOverlay Rust v1.9.0 (crates.io 2024-11-20) versus current 9.0.0, and Clipper2 v1.4.0; the perf app now builds iOverlay from a local path, so the published table may not match the code in the repo today. Clipper2 is equal or faster on small inputs and on Lines Net/Spiral up to about a thousand elements; the large factors come from asymptotic behaviour on adversarial synthetic grids, not typical GIS data. Boost results stop at mid sizes. The repo README chart itself shows only internal engine variants (multithreading cuts relative time by about 8 to 17 percent on average). OpenROAD discussion #5864 (opened by the search agent, written by the iOverlay author) separately claims xOverlay is 10-20x faster than Boost.Polygon in most benchmarks; not verified here.

Rust crate, so usable from C++ only through an FFI layer (the API offers a flat, FFI-friendly shape hierarchy). Integer (i16/i32/i64) and float (f32/f64) engines; the large-input gain depends on the allow_multithreading Cargo feature (rayon). Also offers slicing, clipping, offsetting and spatial predicates.

## Maintenance

Actively maintained (last commit 2026-09-24, 940 commits, every listed issue closed), dual MIT/Apache-2.0, 9.0M crates.io downloads and the boolean engine inside georust/geo; usable from C++ only through your own FFI layer.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The Performance Comparison page (read from its source in iShape-Rust/iShape-js docs/) times iOverlay against Clipper2 v1.4.0 and Boost 1.86 on six tests using the public iShape-Rust/iOverlayPerformance code, but the CPU is given only as '3 GHz 6-Core Intel Core i5' and no compiler is named, so it is first-party with partial methodology: C.
- **Verifier notes:** Benchmark page now verified from its source in iShape-Rust/iShape-js (github.io itself blocked); the 33.7 s versus 644.3 s figures match the Checkerboard row exactly. Tier stays C (CPU model and compiler missing); crates.io shows 9.0M downloads, so the 'over 5 million' usage line was corrected. Last commit 2026-09-24, MIT OR Apache-2.0 confirmed.
- **Fields the verifier corrected:** `claimed_speedup`, `baseline`, `compiler_and_flags`, `hardware`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/iShape-Rust/iOverlay>
  - <https://github.com/iShape-Rust/iOverlay/commits>
  - <https://raw.githubusercontent.com/iShape-Rust/iOverlay/HEAD/iOverlay/README.md>
  - <https://raw.githubusercontent.com/iShape-Rust/iShape-js/HEAD/docs/overlay/performance/performance.html>
  - <https://github.com/iShape-Rust/iOverlayPerformance>
  - <https://github.com/iShape-Rust/iOverlayPerformance/tree/main/ClipperApp>
  - <https://raw.githubusercontent.com/iShape-Rust/iOverlayPerformance/HEAD/ClipperApp/CMakeLists.txt>
  - <https://raw.githubusercontent.com/iShape-Rust/iOverlayPerformance/HEAD/ClipperApp/build.sh>
  - <https://raw.githubusercontent.com/iShape-Rust/iOverlayPerformance/HEAD/ClipperApp/run.sh>
  - <https://raw.githubusercontent.com/iShape-Rust/iOverlayPerformance/HEAD/BoostApp/CMakeLists.txt>
  - <https://raw.githubusercontent.com/iShape-Rust/iOverlayPerformance/HEAD/iOverlayAppRust/Cargo.toml>
  - <https://crates.io/api/v1/crates/i_overlay>
- **Sources the enricher read:**
  - <https://github.com/iShape-Rust/iOverlay>
  - <https://raw.githubusercontent.com/iShape-Rust/iOverlay/HEAD/README.md>
  - <https://raw.githubusercontent.com/iShape-Rust/iOverlay/HEAD/iOverlay/README.md>
  - <https://raw.githubusercontent.com/iShape-Rust/iOverlay/HEAD/iOverlay/Cargo.toml>
  - <https://raw.githubusercontent.com/iShape-Rust/iShape-js/HEAD/docs/overlay/performance/performance.html>
  - <https://github.com/iShape-Rust/iOverlay/tree/main/iOverlay/src>
  - <https://github.com/iShape-Rust/iOverlay/tree/main/iOverlay/src/split>
  - <https://github.com/iShape-Rust/iOverlay/tree/main/iOverlay/src/core>
  - <https://raw.githubusercontent.com/iShape-Rust/iOverlay/HEAD/iOverlay/src/lib.rs>
  - <https://raw.githubusercontent.com/iShape-Rust/iOverlay/HEAD/iOverlay/src/core/solver.rs>
  - <https://raw.githubusercontent.com/iShape-Rust/iOverlay/HEAD/iOverlay/src/split/solver.rs>
  - <https://raw.githubusercontent.com/iShape-Rust/iOverlay/HEAD/iOverlay/src/split/solver_fragment.rs>
  - <https://raw.githubusercontent.com/iShape-Rust/iOverlay/HEAD/iOverlay/src/split/solver_tree.rs>
  - <https://raw.githubusercontent.com/iShape-Rust/iOverlay/HEAD/iOverlay/src/split/solver_list.rs>
  - <https://raw.githubusercontent.com/iShape-Rust/iOverlay/HEAD/iOverlay/src/split/grid_layout.rs>
  - <https://github.com/iShape-Rust/iOverlay/issues?q=is%3Aissue>
  - <https://github.com/iShape-Rust/iOverlay/blob/main/CONTRIBUTING.md>
  - <https://github.com/iShape-Rust>
  - <https://github.com/iShape-Rust/iShape-ffi>
  - <https://raw.githubusercontent.com/iShape-Rust/iShape-ffi/HEAD/README.md>
  - <https://raw.githubusercontent.com/iShape-Rust/iShape-ffi/HEAD/Cargo.toml>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/ishape-rust/ioverlay`) · [data/wave8/enrich/raw/github_com_ishape_rust_ioverlay.json](../../../data/wave8/enrich/raw/github_com_ishape_rust_ioverlay.json) (enrichment confidence 0.7)

</details>
