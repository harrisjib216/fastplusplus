# contour-wasm

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly libraries and apps](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `AGPL-3.0-or-later` · 🟡 stale

> Rust port of MarchingSquares.js isobands, plus isolines, compiled to WebAssembly; README shows 1.3-2x faster than the JS original.

| | |
|---|---|
| **Beats** | MarchingSquares.js isoBands (pure JavaScript, used internally by turf-isobands) |
| **Claimed result** | 5,307 points / 23 intervals: 16 ms vs 12 ms; 17,608 / 15: 25 vs 15 ms; 336,960 / 14: 369 vs 186 ms; 1,010,880 / 14: 832 vs 492 ms (about 1.3x to 2.0x faster, derived from page data). |
| **Workload** | Isoband computation on grids of 5,307 to 1,010,880 points with 14 to 23 intervals; the sizes match the cases in example/index.html (volcano 87x61 = 5,307 points, dem_big 336,960 points, dem_big concatenated three times 1,010,880 points; derived from page data). One cold call per library per case in the browser, timed with performance.now(). |
| **Metric** | latency |
| **Compiler and flags** | wasm-pack build; Cargo.toml [profile.release] opt-level = 3; wraps the contour 0.12.1 and contour-isobands 0.4.3 crates. Browser and wasm-bindgen versions for the benchmark not stated. |
| **Adoption** | 5 stars; npm package contour-wasm |
| **Last commit** | 2024-03-11 |
| **Links** | [repository](https://github.com/mthh/contour-wasm) · [benchmark](https://github.com/mthh/contour-wasm) |

## Verdict

The README table compares MarchingSquaresJS.isoBands with contour-wasm isobands: 16 vs 12 ms (volcano, 87x61, 23 break values), 25 vs 15 ms (pot_pop_fr, 142x124, 15), 369 vs 186 ms (dem_big, 336,960 points, 14) and 832 vs 492 ms (dem_big stacked three times, 1,010,880 points), which is 1.33x to 1.98x (derived from page data). Each number is one cold browser call timed with performance.now() in example/index.html; the browser, hardware, crate versions and baseline version are not stated, and the quadtree setting and timed work differ between the sides.

## Use it when

- Browser maps or dashboards that need filled contour bands (isobands) as GeoJSON from rasters such as DEMs or interpolated surfaces, at roughly 0.3-1M cells, where the README shows about 2x over MarchingSquares.js.
- Replacing turf-isobands or MarchingSquares.js when contouring is the bottleneck and you also want valid polygons with holes assigned and RFC 7946 ring orientation instead of loose rings.
- Output directly in geographic or projected coordinates via x_origin/x_step instead of grid indices.
- Projects already under AGPL, the same licence as MarchingSquares.js, so switching does not change licence obligations.

## Skip it when

- Closed-source apps that cannot meet AGPL-3.0-or-later; if you only need isolines, the underlying contour crate is MIT OR Apache-2.0 and can be wrapped directly.
- Small grids or one-off calls: on the 5,307-point case the gain was only 1.3x (16 vs 12 ms), and each call pays async wasm init once plus a full input copy and GeoJSON serialisation into JS objects.
- Noisy rasters with thousands of small rings per band: polygon reconstruction tests every ring against every other ring (quadratic per band), work the JS baseline does not do.
- Large grids with many bands where multicore matters: the wasm build is single-threaded and does not expose par_contours.
- Need for an actively maintained package: no commits since 2024-03-11, npm 0.5.0, 5 stars, and it pins contour 0.12.1 while 0.13.1 exists.

## How it is fast

The algorithm is the same marching-squares isoband tracing as the JavaScript baseline (cell classification per band, saddle disambiguation, edge-following path tracing, optional quadtree that skips cells whose min/max cannot touch the band). The speedup comes from running it as Rust compiled to wasm with opt-level 3: typed f64 grids, a cell grid allocated once and reused across bands, FxHashMap edge tables. No SIMD or threads are used; contour-isobands' rayon `parallel` feature is not enabled in the wasm build.

## Compared with alternatives

No sibling does contouring: d3_geo_voronoi_rs computes spherical Voronoi diagrams, and Clipper2-WASM and brepkit do polygon booleans and CAD. Pick contour-wasm to turn grids into isoband or isoline GeoJSON, and pair it with Clipper2-WASM if the bands then need clipping.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none at runtime beyond the bundled wasm-bindgen glue; building needs Rust and wasm-pack with contour 0.12.1, contour-isobands 0.4.3, geojson 0.24, serde-wasm-bindgen 0.6.1 |
| **Minimum toolchain** | Rust 2021 edition plus wasm-pack to rebuild; consumers need WebAssembly support. The npm package.json has a `module` entry and `sideEffects` list, the shape of wasm-pack's default bundler target, so a bundler that handles .wasm imports is needed. |
| **Platforms** | wasm32 in browsers (README tests with headless Firefox); Node.js use not documented |
| **Thread safety** | not documented; single-threaded wasm module |
| **Drop-in for the baseline** | partial: same algorithm and band semantics, but a different signature (flat array plus width/height and break values instead of a 2D array with lowerBound/bandWidth arrays) and GeoJSON output instead of path arrays |

## Gotchas

- Benchmark harness (example/index.html): one cold performance.now() run per library per case, no browser or hardware stated, and asymmetric. The wasm timer includes the Float64Array copy of the input, GeoJSON polygon and hole reconstruction, serde-wasm-bindgen conversion and a console.log of the result, and it runs with use_quad_tree false. The JS timer excludes the reshaping of the input into row arrays and runs MarchingSquares.js with its quadtree on, returning only raw rings. The asymmetries favour the baseline, so the 1.3-2.0x is likely conservative but noisy. The page loads ./marchingsquares-isobands.min.js and ../pkg, neither of which is committed (404; example/ holds only index.html and three JSON datasets), so the run cannot be reproduced from the repo and the baseline version is unknown.
- Possible hole-assignment bug (read in contour-isobands src/isobands.rs, not reproduced): rings are sorted by `area.abs() as u64`, and the area is computed after x_step/y_step scaling. With sub-unit steps such as degrees, most areas truncate to 0, so the smallest-first order is lost. The code comment says correct hole assignment for nested polygon-with-hole cases depends on that order, so holes may attach to the wrong polygon in geographic coordinates.
- `intervals` are break values, not band counts: n values give n-1 bands. Every band but the last is half-open, using a 1e-13 offset on the upper bound. The README's 'number of intervals' column counts break values (e.g. 15 values = 14 bands for the 17,608-point grid).
- The wrapper defaults use_quad_tree to true (the crate's own default is false). isolines always uses smoothing (hard-coded `true`). Errors such as a data length that does not equal width\*height, fewer than 2 thresholds or PolygonReconstructionError come back as thrown JsError. NaN/no-data handling is not documented.

## Known shortcomings

- 1.3-2.0x over MarchingSquares.js from one cold run each in example/index.html, with the quadtree on for the JavaScript side and off for the wasm side; AGPL only in Cargo.toml, no LICENSE file; a wasm wrapper of the author's contour-isobands crate. Stale since 2024-03-11.
- Harness asymmetries all favour the JS baseline, so the 1.3-2.0x is likely conservative: the wasm timer includes the input copy, GeoJSON building and a console.log with the quadtree off, while the JS timer excludes input reshaping and runs with the quadtree on. The vendored marchingsquares-isobands.min.js and ../pkg are not committed (404), so the run is not reproducible and the baseline version is unknown. Possible contour-isobands hole-assignment bug: the sort key 'area.abs() as u64' is taken after x_step scaling, so ordering is lost with sub-unit steps (from code, not reproduced); polygon reconstruction is quadratic in ring count per band.

## Caveats and trade-offs

Micro-benchmark in the README with no hardware, browser or Node version and no link to the timing code; the matching code in example/index.html times a single cold call per library with no warm-up or repetition. The two sides run with different options: contour-wasm is called with use_quad_tree: false while MarchingSquaresJS.isoBands runs with its quadtree enabled (noQuadTree: false), and the wasm timed region also includes the Float64Array copy and a console.log of the result, so the comparison is not like for like (both asymmetries handicap contour-wasm). The vendored marchingsquares-isobands.min.js version is not stated. Speedup is 1.3x on the smallest input and 1.7x to 2.0x on larger ones. No commits since 2024-03-11. Licence AGPL-3.0-or-later is declared only in Cargo.toml and npm metadata; the repo has no LICENSE file.

AGPL-3.0-or-later (from Cargo.toml) restricts embedding in closed web apps. Rust compiled with wasm-pack; needs async wasm initialisation. Isobands and isolines only.

## Maintenance

Stale since 2024-03-11 (npm 0.5.0, 25 commits, 5 stars, one author), but it is a 114-line wrapper over the author's contour and contour-isobands crates, easy to rebuild against newer versions; AGPL-3.0-or-later is declared only in Cargo.toml and npm metadata, with no LICENSE file in the repo.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The README micro-benchmark table shows the four claimed rows against MarchingSquaresJS.isoBands; the timing code appears to be example/index.html (single performance.now() call per case in a browser), with no hardware, browser or runtime stated, so first-party C.
- **Verifier notes:** Numbers match the README (16 vs 12, 25 vs 15, 369 vs 186, 832 vs 492 ms; ratios 1.33x to 1.98x derived). Shortcomings: single cold run, no environment, mismatched quadtree option between sides, stale since 2024-03-11, licence only in package metadata. The algorithm lives in the author's contour-isobands crate; if that crate is listed elsewhere, treat this as its wasm wrapper. 5 stars, 25 commits, not a fork; npm contour-wasm 0.5.0 (2024-03-11, AGPL-3.0-or-later).
- **Fields the verifier corrected:** `compiler_and_flags`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-105 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/mthh/contour-wasm/HEAD/README.md>
  - <https://raw.githubusercontent.com/mthh/contour-wasm/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/mthh/contour-wasm/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/mthh/contour-wasm/main/example/index.html>
  - <https://github.com/mthh/contour-wasm>
  - <https://github.com/mthh/contour-wasm/commits>
  - <https://github.com/mthh/contour-wasm/tree/main/example>
  - <https://registry.npmjs.org/contour-wasm>
- **Sources the enricher read:**
  - <https://github.com/mthh/contour-wasm>
  - <https://github.com/mthh/contour-wasm/commits/main>
  - <https://github.com/mthh/contour-wasm/tree/main/example>
  - <https://raw.githubusercontent.com/mthh/contour-wasm/HEAD/README.md>
  - <https://raw.githubusercontent.com/mthh/contour-wasm/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/mthh/contour-wasm/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/mthh/contour-wasm/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/mthh/contour-wasm/HEAD/example/index.html>
  - <https://raw.githubusercontent.com/mthh/contour-wasm/HEAD/example/pot_pop_fr.json>
  - <https://raw.githubusercontent.com/mthh/contour-wasm/HEAD/example/volcano.json>
  - https://raw.githubusercontent.com/mthh/contour-wasm/HEAD/example/dem_big.json (first 400 bytes)
  - https://raw.githubusercontent.com/mthh/contour-wasm/HEAD/example/marchingsquares-isobands.min.js (404)
  - https://raw.githubusercontent.com/mthh/contour-wasm/HEAD/LICENSE (404)
  - https://raw.githubusercontent.com/mthh/contour-wasm/HEAD/package.json (404)
  - <https://registry.npmjs.org/contour-wasm>
  - <https://crates.io/api/v1/crates/contour-isobands>
  - <https://crates.io/api/v1/crates/contour>
  - <https://raw.githubusercontent.com/mthh/contour-isobands-rs/HEAD/README.md>
  - <https://raw.githubusercontent.com/mthh/contour-isobands-rs/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/mthh/contour-isobands-rs/HEAD/Cargo.toml>
  - <https://github.com/mthh/contour-isobands-rs/tree/main/src>
  - <https://raw.githubusercontent.com/mthh/contour-isobands-rs/HEAD/src/isobands.rs>
  - <https://raw.githubusercontent.com/mthh/contour-isobands-rs/HEAD/src/quadtree.rs>
  - <https://raw.githubusercontent.com/mthh/contour-isobands-rs/HEAD/src/polygons.rs>
  - <https://raw.githubusercontent.com/mthh/contour-isobands-rs/HEAD/src/contains.rs>
  - <https://github.com/mthh/contour-isobands-rs/issues?q=is%3Aissue>
  - <https://github.com/mthh/contour-isobands-rs/issues/2>
  - <https://raw.githubusercontent.com/RaumZeit/MarchingSquares.js/HEAD/README.md>
  - <https://registry.npmjs.org/marchingsquares>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/mthh/contour-wasm`) · [data/wave13/enrich/raw/github_com_mthh_contour_wasm.json](../../../data/wave13/enrich/raw/github_com_mthh_contour_wasm.json) (enrichment confidence 0.7)

</details>
