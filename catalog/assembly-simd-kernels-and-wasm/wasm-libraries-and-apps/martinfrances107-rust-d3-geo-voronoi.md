# d3_geo_voronoi_rs (rust_d3_geo_voronoi)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly libraries and apps](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust compiled to WebAssembly (wasm-pack)` · `MIT` · 🟢 active

> Rust port of d3-geo-voronoi (spherical Delaunay/Voronoi); its wasm canvas demo draws frames about 1.95x faster than the JS original.

| | |
|---|---|
| **Beats** | d3-geo-voronoi (the original JavaScript library, github.com/Fil/d3-geo-voronoi), run on an equivalent benchmark web page |
| **Claimed result** | JavaScript renders 600 points in 16 ms at the tuned 60 fps setting; the Rust version does the same workload in 8.165 ms (README: 'a factor 1.95 speedup'), and renders 1220 points in 16 ms, 'an increase of just under 2'. |
| **Workload** | Frames-per-second style browser benchmark: Delaunay/Voronoi mesh of random points on a sphere rendered each frame; points rendered within a 16 ms frame budget. |
| **Metric** | throughput |
| **Compiler and flags** | wasm-pack via webpack (@wasm-tool/wasm-pack-plugin), 'npm run build' (webpack.production.config.js) in benchmark/; workspace release profile lto = true, codegen-units = 1; no rustc version or target-feature flags stated |
| **Adoption** | 8 stars, 1 fork; crates.io d3_geo_voronoi_rs 43,266 downloads (375 recent), version 0.10.7 |
| **Last commit** | 2026-01-03 |
| **Links** | [repository](https://github.com/martinfrances107/rust_d3_geo_voronoi) · [benchmark](https://github.com/martinfrances107/rust_d3_geo_voronoi) |

## Verdict

In the author's own browser test (browser and hardware unstated, 2023), the JS d3-geo-voronoi canvas page needed about 16 ms per frame to draw 600 random points' Voronoi cells on a rotating orthographic globe, while the Rust/wasm port drew the same scene in 8.165 ms (1.95x) and fitted 1220 points in 16 ms; only the per-frame projection and drawing are timed, not the diagram construction.

## Use it when

- Rust or Rust-to-wasm code that needs spherical Voronoi cells or Delaunay meshes for a few hundred to a few thousand points, e.g. drawing them on a rotating globe on a canvas.
- Porting a d3-geo-voronoi visualisation to Rust while keeping its method names (polygons, triangles, mesh, links, hull, find).
- Native Rust tools that render spherical Voronoi diagrams to SVG through d3_geo_rs (the profile_target binary and the criterion bench draw 600 and 6000 cells this way).
- Animated browser globes where the JS page misses a 16 ms frame budget: the author's page fit 1220 points per frame against 600 for JS.

## Skip it when

- JavaScript projects that just want a faster npm drop-in: the README documents no npm or wasm package, so you must write your own wasm-bindgen wrapper the way benchmark/src/lib.rs does.
- f32 workloads: the README says cells break (some take up the whole sphere) unless T is f64.
- Hard inputs that need a robust hull: the README lists a failing test, 'geoVoronoi.hull does not break on difficult polygons'.
- Contours: contour.js and its tests are not ported.
- Multithreaded or web-worker sharing of one diagram: Delaunay holds Rc fields and a boxed non-Send closure, so the Voronoi value cannot cross threads.

## How it is fast

It uses the same algorithm as the JavaScript library: points are projected, triangulated with a planar Delaunay (d3_delaunay_rs over delaunator), and circumcenters, cell polygons, neighbours, mesh, hull and the Urquhart graph are all computed once at construction. The speed difference is plain compilation to wasm with f64 math and no garbage collector (the README's own explanation), not a new algorithm; the benchmarked frame is mostly d3_geo_rs orthographic projection, clipping and resampling plus canvas drawing.

## Compared with alternatives

No catalogued sibling covers spherical Voronoi or Delaunay, so pick it whenever you need that geometry in Rust or wasm; contour-wasm (1.3x to 2.0x over MarchingSquares.js isoBands) is the nearest geographic wasm entry and is the one to use for contour bands, which this port lacks.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | d3_geo_rs 3.1.3, d3_delaunay_rs 0.11.3, geo 0.31, geo-types 0.7.17, delaunator 1, approx, num-traits, float_next_after; the workspace build patches geo/geo-types to the author's cyclic_match git branch and delaunator to its git master |
| **Minimum toolchain** | Rust 2021 edition; no rust-version declared on crates.io (MSRV not documented); benchmark needs wasm-pack, webpack 5 and npm |
| **Platforms** | any Rust target; the demo targets wasm32-unknown-unknown with getrandom's wasm_js backend |
| **Thread safety** | not documented; Voronoi/Delaunay contain Rc and a Box&lt;dyn Fn&gt; without Send, so they are single-threaded only |
| **Drop-in for the baseline** | partial — method names follow d3-geo-voronoi, but it is a Rust API (TryFrom&lt;Geometry&gt;, FeatureCollection from d3_geo_rs) with no published JS binding |

## Gotchas

- The benchmark does not time the Voronoi computation: both pages build the diagram once on slider change (update() in Rust, gen_points() in JS) and time only the per-frame render: polygons() rebuilt from cached Delaunay data, orthographic projection with rotation, path generation and canvas fill/stroke of every cell and point. The 1.95x therefore reflects mostly d3_geo_rs path/projection code plus identical canvas work, not this crate's triangulation.
- The comparison is first-party on both sides: the JS benchmark page in Fil/d3-geo-voronoi (benchmark/sphereCanvas.html) was contributed by the same author (PRs #31, #43, #45) and loads an unpinned d3@7 from unpkg; no browser, CPU, run count or variance is given for the 8.165 ms figure, and the Rust timer also includes the clearRect call that the JS timer excludes (a small bias against Rust).
- README build steps say cd benchmark\www, but package.json now sits directly in benchmark/; the JS page now lives at benchmark/sphereCanvas.html, not src/benchmark/. The JS page's slider stops at 1000 points while the Rust page goes to 6000.
- The numbers date from 2023-08-20 (when issue #2 'Restore benchmark' was closed) and were not re-measured for 0.10.x; issue #1 (open since 2023-04-03) notes the demo re-sends the same colour strings to JS each frame instead of interning them.

## Known shortcomings

- Numbers from 2023-08-20 (b8979d0), not re-measured; no CPU or browser stated; the whole pipeline includes canvas drawing; MIT only in Cargo.toml, no LICENSE file; the hull test fails.
- The Voronoi/Delaunay construction is never timed: both pages build it once on slider change and time only the per-frame polygons() plus d3_geo_rs projection/path plus canvas fill/stroke, so the 1.95x mostly reflects d3_geo_rs and identical canvas work. The JS page (Fil/d3-geo-voronoi benchmark/sphereCanvas.html) is also by the same author (PRs #31, #43, #45) with d3@7 unpinned; the Rust timer includes clearRect, the JS timer excludes it; Voronoi holds Rc, so it is not Send.

## Caveats and trade-offs

Single author measurement with no CPU, browser, run counts or variance. The 8.165 ms / 1.95x figures were written in the README on 2023-08-20 (commit b8979d0 'Update performance report'; before that the README said 11 ms, a 31% speedup) and have not been re-measured for the current 0.10.x code. The benchmark renders a Delaunay mesh to canvas each frame, so the comparison covers the whole pipeline (Rust ports of d3-geo and d3-delaunay plus canvas drawing), not just the Voronoi step. README build instructions point to benchmark/www, which no longer exists (package.json now sits in benchmark/), and to d3-geo-voronoi src/benchmark/sphereCanvas.html, whereas the JS repo's benchmark is now in a top-level benchmark/ directory. README notes a failing test ('geoVoronoi.hull does not break on difficult polygons') and that the demo only works with f64 (f32 breaks cell integrity). Licence is MIT only via Cargo.toml (workspace.package license = "MIT"); the repository has no LICENSE file. Workspace patches geo/geo-types to the author's own git branch and delaunator to its unpublished master.

Port is incomplete (contour.js not ported); README says the demo works only with f64 because f32 breaks cell integrity.

## Maintenance

Lightly active single-author port (latest crates.io release 0.10.7 on 2025-07-24, about 43,000 downloads, 8 stars, no GitHub releases); MIT declared in Cargo.toml without a LICENSE file (the benchmark's package.json says MIT OR Apache-2.0), usable from Rust if you stay on f64.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** README Performance Profiling section gives the author's own browser-benchmark result (JS 600 points in 16 ms vs Rust/wasm same workload in 8.165 ms, 1.95x; 1220 points in 16 ms) against a port of d3-geo-voronoi's benchmark page; benchmark code is public (benchmark/) but no CPU, browser, Rust flags or run counts are stated, so C.
- **Verifier notes:** Numbers match the README; tier C stands. Shortcomings to record: no hardware or browser stated, numbers from 2023 not re-measured, whole-pipeline including canvas rendering, no LICENSE file (MIT declared in Cargo.toml), failing hull test, stale build instructions.
- **Fields the verifier corrected:** `stars_or_usage`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-120 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/martinfrances107/rust_d3_geo_voronoi>
  - <https://github.com/martinfrances107/rust_d3_geo_voronoi/commits/main>
  - <https://github.com/martinfrances107/rust_d3_geo_voronoi/commits/main/README.md>
  - <https://github.com/martinfrances107/rust_d3_geo_voronoi/tree/main/benchmark>
  - <https://raw.githubusercontent.com/martinfrances107/rust_d3_geo_voronoi/HEAD/README.md>
  - <https://raw.githubusercontent.com/martinfrances107/rust_d3_geo_voronoi/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/martinfrances107/rust_d3_geo_voronoi/HEAD/lib/Cargo.toml>
  - <https://raw.githubusercontent.com/martinfrances107/rust_d3_geo_voronoi/HEAD/benchmark/Cargo.toml>
  - <https://raw.githubusercontent.com/martinfrances107/rust_d3_geo_voronoi/HEAD/benchmark/package.json>
  - <https://raw.githubusercontent.com/martinfrances107/rust_d3_geo_voronoi/HEAD/benchmark/README.md>
  - <https://raw.githubusercontent.com/martinfrances107/rust_d3_geo_voronoi/b8979d0/README.md>
  - <https://raw.githubusercontent.com/martinfrances107/rust_d3_geo_voronoi/689f1f1/README.md>
  - <https://github.com/Fil/d3-geo-voronoi>
  - <https://crates.io/api/v1/crates/d3_geo_voronoi_rs>
- **Sources the enricher read:**
  - <https://github.com/martinfrances107/rust_d3_geo_voronoi>
  - <https://github.com/martinfrances107/rust_d3_geo_voronoi/issues?q=is%3Aissue>
  - <https://github.com/martinfrances107/rust_d3_geo_voronoi/issues/1>
  - <https://github.com/martinfrances107/rust_d3_geo_voronoi/tree/main/lib/src>
  - <https://github.com/martinfrances107/rust_d3_geo_voronoi/tree/main/lib/src/voronoi>
  - <https://raw.githubusercontent.com/martinfrances107/rust_d3_geo_voronoi/HEAD/README.md>
  - <https://raw.githubusercontent.com/martinfrances107/rust_d3_geo_voronoi/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/martinfrances107/rust_d3_geo_voronoi/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/martinfrances107/rust_d3_geo_voronoi/HEAD/todo.md>
  - <https://raw.githubusercontent.com/martinfrances107/rust_d3_geo_voronoi/HEAD/.cargo/config.toml>
  - <https://raw.githubusercontent.com/martinfrances107/rust_d3_geo_voronoi/HEAD/lib/Cargo.toml>
  - <https://raw.githubusercontent.com/martinfrances107/rust_d3_geo_voronoi/HEAD/lib/src/lib.rs>
  - <https://raw.githubusercontent.com/martinfrances107/rust_d3_geo_voronoi/HEAD/lib/src/voronoi/mod.rs>
  - <https://raw.githubusercontent.com/martinfrances107/rust_d3_geo_voronoi/HEAD/lib/src/voronoi/polygons.rs>
  - <https://raw.githubusercontent.com/martinfrances107/rust_d3_geo_voronoi/HEAD/lib/src/delaunay/mod.rs>
  - <https://raw.githubusercontent.com/martinfrances107/rust_d3_geo_voronoi/HEAD/lib/benches/draw.rs>
  - <https://raw.githubusercontent.com/martinfrances107/rust_d3_geo_voronoi/HEAD/profile_target/src/main.rs>
  - <https://raw.githubusercontent.com/martinfrances107/rust_d3_geo_voronoi/HEAD/benchmark/Cargo.toml>
  - <https://raw.githubusercontent.com/martinfrances107/rust_d3_geo_voronoi/HEAD/benchmark/package.json>
  - <https://raw.githubusercontent.com/martinfrances107/rust_d3_geo_voronoi/HEAD/benchmark/README.md>
  - <https://raw.githubusercontent.com/martinfrances107/rust_d3_geo_voronoi/HEAD/benchmark/index.html>
  - <https://raw.githubusercontent.com/martinfrances107/rust_d3_geo_voronoi/HEAD/benchmark/js/index.ts>
  - <https://raw.githubusercontent.com/martinfrances107/rust_d3_geo_voronoi/HEAD/benchmark/src/lib.rs>
  - <https://raw.githubusercontent.com/martinfrances107/rust_d3_geo_voronoi/HEAD/benchmark/webpack.config.js>
  - <https://raw.githubusercontent.com/martinfrances107/rust_d3_geo_voronoi/HEAD/benchmark/webpack.production.config.js>
  - <https://raw.githubusercontent.com/martinfrances107/rust_d3_geo/HEAD/lib/src/path/path2d_endpoint.rs>
  - <https://raw.githubusercontent.com/Fil/d3-geo-voronoi/HEAD/benchmark/sphereCanvas.html>
  - <https://raw.githubusercontent.com/Fil/d3-geo-voronoi/HEAD/src/voronoi.js>
  - <https://raw.githubusercontent.com/Fil/d3-geo-voronoi/HEAD/package.json>
  - <https://github.com/Fil/d3-geo-voronoi/commits/main/benchmark/sphereCanvas.html>
  - <https://crates.io/api/v1/crates/d3_geo_voronoi_rs>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/martinfrances107/rust_d3_geo_voronoi`) · [data/wave13/enrich/raw/github_com_martinfrances107_rust_d3_geo_voronoi.json](../../../data/wave13/enrich/raw/github_com_martinfrances107_rust_d3_geo_voronoi.json) (enrichment confidence 0.75)

</details>
