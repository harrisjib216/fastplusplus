# GeoRepair (geo-repair)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0` · 🟢 active

> Rust crate (with a C API) for OGC validity checks and ST_MakeValid-style repair; faster than GEOS on most invalid-input classes.

| | |
|---|---|
| **Beats** | GEOS 3.14.1 (conda-forge libgeos, MSVC build) makeValid / UnaryUnion |
| **Claimed result** | README (real-world table updated 2026-09-26; synthetic table refreshed 2026-09-18 from the v0.14.5 measurement set): real-world validation of 1.58M polygons 2.1 s (1.3 us/poly) vs GEOS 3.0 s (1.9 us/poly), 1.4x; full pass 3.6 s vs 3.0 s (0.83x, GEOS faster). Synthetic rows (parallel batch; ratio = GEOS/GeoRepair): valid polygon 4v 4.8x, invalid bowtie 4v 25x, invalid bowtie 1000v 8.0x, collapsed 1000v 5.5x, zero-length line 45x, zigzag ls 500v 43x, dense self ls 1000v 120x; star-burst and spoke rows reach 5632x-12573x. GEOS is faster on valid polygon 10000v (0.37x), spaghetti 500v (0.56x), large coord 1e12 1000v (0.08x), self-int ls 1000v (0.05x) and arrange valid 500v (0.25x). docs/BENCHMARKS.md (tables dated 2026-08-07): real-world validation 2.47 s vs 3.46 s (1.40x), full pass 4.05 s vs 3.49 s (0.86x). Its synthetic rows differ from the README: valid polygon 4v 2.78x, invalid bowtie 4v 21.78x, zero-length line 38.82x, valid polygon 10000v 0.31x, spaghetti 0.63-0.65x, large coord 1e12 2.38x. It says GeoRepair wins 73 of 91 cases. |
| **Workload** | Validation and repair (ST_MakeValid equivalent) of 1,579,030 polygon parts from a production GeoPackage, plus synthetic cases (valid polygons, bowties, collapsed rings, near-collinear, large coordinates, linestrings) of 4 to 10,000 vertices; parallel batch. |
| **Metric** | throughput |
| **Hardware** | Intel i5-12400F (6C/12T), Windows 10 |
| **Compiler and flags** | Rust bench and release profiles: lto=fat, codegen-units=1, panic=unwind; mimalloc global allocator (a default feature); edition 2024, MSRV 1.88. The rustc version used for the runs is not stated. Windows x86_64. GEOS is conda-forge 3.14.1: docs/BENCHMARKS.md says an MSVC build, serial per call, no LTO, while docs/GEOS-SETUP.md calls the conda build LLVM-optimized. |
| **Adoption** | 1 star; very new |
| **Last commit** | 2026-09-27 |
| **Links** | [repository](https://github.com/Wolren/GeoRepair) · [benchmark](https://github.com/Wolren/GeoRepair/blob/HEAD/docs/BENCHMARKS.md) |

## Verdict

First-party runs on an Intel i5-12400F under Windows 10 (Rust release profile with fat LTO, mimalloc, 12-thread Rayon batch; rustc version not stated) against conda-forge GEOS 3.14.1, MSVC build, serial per call but driven concurrently from Rayon in the same process. Validation of 1.58M production polygons was 1.4x faster than GEOS and the full repair pass was 0.83x. Synthetic rows range from 0.05x to over 9,000x, and BENCHMARKS.md counts 73 wins in 91 cases. The production dataset is not public.

## Use it when

- Bulk cleaning of messy GIS polygons before overlay or loading into PostGIS/GeoPackage, where many inputs are invalid (bowties, collapsed rings, star or spoke shapes, overlapping MultiPolygon parts): the author measures 5-25x on bowtie/collapsed rows and hundreds of times on spoke and star-burst rows.
- Repairing self-intersecting linework (zigzag, dense self-overlap, spiral): 10-120x against GEOS UnaryUnion in the author's tables.
- Rust pipelines on geo/geoarrow/wkb data that need a validity gate without linking GEOS, including no_std and WASM builds.
- Validation-only passes over large mostly-valid datasets, where it measured about 1.4x GEOS (2.1 s vs 3.0 s on 1.58M polygons, 12 threads).

## Skip it when

- Mostly valid, large polygons or linestrings: GEOS is faster on valid polygons of 100 vertices or more (down to 0.31-0.37x at 10,000 vertices) and on valid linestrings of 10-500 vertices.
- Full validate-and-repair passes on mostly valid data: GEOS was faster on the 1.58M-polygon real-world full pass (3.0 s vs 3.6 s).
- Dense random-walk 'spaghetti' rings, self-intersecting linestrings of 100+ vertices and large-coordinate (1e12) rings, where GEOS wins by 1.5x to 20x in the README table.
- You need exact GEOS isValid parity: the eps-class tolerance (1e-12 x ring scale) rejects 213 GEOS-valid XML-suite cases, mostly orientation, and repair returns an empty GeometryCollection when it cannot certify the output.
- You want a stable dependency: the crate is labelled experimental, 0.x with breaking changes expected, 1 star, and correctness fixes for shipped invalid output landed as recently as 2026-09-27.

## How it is fast

The default Structure strategy follows GEOS makeValid's shape (planar graph extraction, face walking, winding-number assembly), but puts a cheap fast-path gate first: a fused duplicate/basic-form/envelope scan, a monotone-chain plus grid self-intersection test, and fast floating-point orientation that escalates to Shewchuk exact predicates only inside a 32-ulp collinear band. Inputs that pass the gate skip noding entirely. Noding uses a radix-sorted sweep and an R-tree (brute force only up to 128 edges). A CDT-based Arrange strategy (spade) is the fallback. Batches run in parallel over Rayon with mimalloc as the global allocator.

## Compared with alternatives

None of the catalogued siblings does validity repair: TG speeds up GEOS predicates (intersects, point-in-polygon) and qdgeo speeds up GEOS overlay and buffer, but both assume valid input. Use GeoRepair as the cleaning step in front of them, or in place of GEOS makeValid when the batch has many invalid shapes.

## Integration

| | |
|---|---|
| **Form** | crate (also cdylib/staticlib with a C header via the ffi feature, and a PyPI wheel) |
| **Dependencies** | geo 0.33, robust, spade (CDT), rstar, rayon, mimalloc (default, C allocator), rusqlite with bundled SQLite (default io-gpkg feature), plus smaller crates; GEOS only for the opt-in benchmarks |
| **Minimum toolchain** | Rust 1.88 (edition 2024); simd-portable needs nightly |
| **Platforms** | x86-64 and aarch64 on Windows/Linux/macOS; WASM32 and no_std without parallelism or file I/O |
| **Thread safety** | Batch APIs are internally parallel (Rayon). The C API is documented as panic-safe with per-item error codes; thread-safety of concurrent calls is not documented. |
| **Drop-in for the baseline** | partial — same job as GEOS isValid/makeValid (and UnaryUnion for linework) but a different API and a stricter, tolerance-based validity contract; from C++ you go through WKB/WKT buffers, not GEOS geometry objects. |

## Gotchas

- The default features install mimalloc as the process-wide #[global_allocator] and pull in bundled SQLite; turn off default features if you embed it in a larger Rust binary or need the proj feature (sqlite3 link conflict).
- The README, docs/BENCHMARKS.md and the crate docs give different numbers for the same rows (for example overlap mp 186-318x in the README vs 6.85-10.34x in BENCHMARKS.md, which calls \~200x figures a WKT round-trip artifact; lib.rs still says 1.16x on the real-world set).
- The spade-based Arrange (CDT) path may panic on degenerate input (all-collinear exterior rings, coordinates near f64::MAX); the release profile keeps panic=unwind so panics are caught and the C API reports them as an error code.
- GeometryCollection cross-component intersections and Z/M consistency are not validated; Cargo's description calls the crate a 'rewritten GEOS/JTS repair module', and the provenance of any ported logic is not documented.

## Known shortcomings

- No rustc version; the 1.58M-polygon GeoPackage is gitignored, so the real-world rows are not reproducible; README overlap/dense-grid 183-318x contradicts BENCHMARKS.md 4-14x, which calls \~200x a WKT round-trip artifact; the latest commit fixes repair output that shipped with crossings; Rust.
- Rust crate; callable from C++ only through the ffi feature (include/geo_repair.h). Three docs give three different real-world speedups (README 1.4x, BENCHMARKS.md 1.40x on other timings, lib.rs 1.16x). Experimental 0.x; default features install mimalloc as the global allocator. Correctness fixes for shipped invalid output on 2026-09-26 and 09-27; nightly fuzzing keeps finding contract breaches. Described as a rewritten GEOS/JTS repair module with undocumented provenance (GEOS is LGPL).

## Caveats and trade-offs

Mixed results: GeoRepair loses on large valid polygons, valid linestrings of 10 or more vertices, spaghetti geometry, large coordinates, self-intersecting linestrings and the full real-world pass. The GeoRepair column is a 12-thread Rayon batch; GEOS runs serially per call but is driven concurrently through Rayon in the same process. Before 2026-08-07 the GEOS columns went through a WKT round trip that inflated wins 30-500x. The README's 2026-09-18 table still shows overlap mp 186-318x and dense grid 183-250x, while BENCHMARKS.md gives 6.85-10.34x and 4.23-13.63x for the same rows and calls \~200x figures an artifact. That contradiction is unexplained. The production GeoPackage behind the real-world rows is gitignored and not public (only benches/real_world/alaska.\* is committed). The validator uses an eps-class tolerance, not GEOS exact-zero, and diverges from GEOS on 213 XML-suite cases. Line rows compare against GEOS UnaryUnion, not makeValid. The crate is labelled experimental: the latest commit (2026-09-27) fixes MultiPolygon repair output that shipped crossings. All numbers are first-party, and sub-microsecond rows are dispatch noise per the authors.

Specialised to geometry validation and repair, not a general GEOS replacement. Rayon parallel batch API; Structure strategy mirrors GEOS ST_MakeValid, Arrange strategy is a CDT fallback. Built-in WKB/WKT/batch I/O. Passes the GEOS XML validation suite per README.

## Maintenance

Very active (last commit 2026-09-27, nightly fuzzing that keeps finding contract breaches), Apache-2.0, but 1 star and self-described as experimental with breaking 0.x releases.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification A, tier now C.
- **Tier reason:** The bench code is public (benches/bench.rs and benches/real_world.rs, GEOS linked via the bench-geos-system feature, commands in docs/GEOS-SETUP.md). The Cargo bench/release profiles set lto=fat and codegen-units=1, and the CPU (i5-12400F) and GEOS 3.14.1 are stated. But no rustc version is given (only MSRV 1.88), and the 1.58M-polygon production GeoPackage is gitignored, so the headline real-world rows cannot be reproduced. That makes it first-party with partial methodology: C, not A.
- **Verifier notes:** The real-world numbers in the record match BENCHMARKS.md, but its synthetic ratios come from the newer README table, not BENCHMARKS.md, so I rewrote claimed_speedup to name both sources. Shortcomings worth recording: a private real-world dataset, no rustc version, and README and BENCHMARKS.md disagreeing by about 20x on the overlap and dense-grid rows. Metadata checked on github.com: Apache-2.0, 1 star, not a fork or archived, 318 commits, last commit 2026-09-27.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://github.com/Wolren/GeoRepair>
  - <https://github.com/Wolren/GeoRepair/commits>
  - <https://github.com/Wolren/GeoRepair/commits/HEAD/docs/BENCHMARKS.md>
  - <https://github.com/Wolren/GeoRepair/commits/HEAD/README.md>
  - <https://raw.githubusercontent.com/Wolren/GeoRepair/HEAD/docs/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/Wolren/GeoRepair/HEAD/README.md>
  - <https://raw.githubusercontent.com/Wolren/GeoRepair/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/Wolren/GeoRepair/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/Wolren/GeoRepair/HEAD/docs/GEOS-SETUP.md>
  - <https://raw.githubusercontent.com/Wolren/GeoRepair/HEAD/benches/bench.rs>
  - <https://raw.githubusercontent.com/Wolren/GeoRepair/HEAD/.gitignore>
- **Sources the enricher read:**
  - <https://github.com/Wolren/GeoRepair/commits>
  - <https://github.com/Wolren/GeoRepair/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/Wolren/GeoRepair/HEAD/README.md>
  - <https://raw.githubusercontent.com/Wolren/GeoRepair/HEAD/docs/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/Wolren/GeoRepair/HEAD/docs/GEOS-SETUP.md>
  - <https://raw.githubusercontent.com/Wolren/GeoRepair/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/Wolren/GeoRepair/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/Wolren/GeoRepair/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/Wolren/GeoRepair/HEAD/include/geo_repair.h>
  - <https://raw.githubusercontent.com/Wolren/GeoRepair/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/Wolren/GeoRepair/HEAD/.gitignore>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/wolren/georepair`) · [data/wave8/enrich/raw/github_com_wolren_georepair.json](../../../data/wave8/enrich/raw/github_com_wolren_georepair.json) (enrichment confidence 0.75)

</details>
