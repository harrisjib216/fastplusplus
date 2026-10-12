# JavaScript-vs-WebAssembly-Comparative-Analysis (Rust wasm matrix multiply)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [AssemblyScript and WebAssembly languages](README.md)</sub>

**Tier C** (first-party claim) · Study only · `Rust` · `no license` · 🟢 active

> Master's-thesis harness timing a naive Rust-to-WebAssembly matrix multiply against the same JavaScript loop in Chromium.

| | |
|---|---|
| **Beats** | JavaScript matrix multiplication (same naive i-k-j loop over Float32Array, TypeScript served by the Vite dev server) in Chromium via Playwright; the matrix sweeps were run only in Chromium (npm scripts exist only for sweep:\*-matrix:chromium); Firefox scripts exist only for the particle demo |
| **Claimed result** | Matrix multiply, median of 20 reps per size, Chromium, JS vs WASM in ms: 64x64 0.50 vs 0.50 (1.00x), 128x128 3.45 vs 2.20 (1.57x), 256x256 28.85 vs 15.65 (1.84x), 512x512 218.05 vs 136.10 (1.60x). On means (matrix_js_vs_wasm.csv) the speedups are 1.49x, 1.69x, 1.46x and 1.50x. P95 in WASM is 57-61% lower at n&lt;=128 but 28-31% higher at n&gt;=256. Particle physics step 1.7-2.8x faster in WASM, but frame rate is equal (about 60 FPS, GPU bound; frame-time ratio 1.01-1.10x). |
| **Workload** | n x n matrix multiplication (64 to 512) and a particle-physics rendering demo, written in parallel in JavaScript and Rust (wasm-pack, wasm-bindgen, web target), automated with Playwright. |
| **Metric** | latency |
| **Compiler and flags** | wasm-pack build --target web --release (QUICKSTART asks for Rust &gt;= 1.90.0, wasm-pack &gt;= 0.13.1); no [profile.release] overrides in wasm-kernels/Cargo.toml or kernels/matrix/Cargo.toml, so Cargo release defaults (opt-level 3) plus wasm-pack's default wasm-opt pass; no simd128 target feature. JS side is TypeScript served unminified by the Vite 5 dev server; Playwright ^1.56 bundled Chromium, version not stated. |
| **Adoption** | 0 stars, 1 commit |
| **Last commit** | 2025-11-30 |
| **Links** | [repository](https://github.com/Chankse/JavaScript-vs-WebAssembly-Comparative-Analysis) · [benchmark](https://github.com/Chankse/JavaScript-vs-WebAssembly-Comparative-Analysis) |

## Verdict

Medians of 20 timed calls per page load in Playwright's bundled Chromium (version, CPU and OS not stated): JavaScript 3.45, 28.85 and 218.05 ms versus Rust wasm (wasm-pack --release, no SIMD) 2.20, 15.65 and 136.10 ms at n = 128, 256 and 512, i.e. 1.57x, 1.84x and 1.60x; equal at n = 64; means give 1.46-1.69x. The WASM inputs were not the seeded matrices because of the pointer bug, and results were never cross-checked.

## Use it when

- As a reference data point for scalar, non-SIMD Rust wasm versus plain JavaScript on a naive matmul in Chromium: about 1.5-1.8x on medians at n = 128 to 512, none at n = 64.
- As a starting template for a Playwright-driven browser benchmark (seeded inputs, query-string parameters, a __dumpResults() hook), after fixing the bridge described under gotchas.
- To show that a GPU-bound frame loop (PixiJS particles at about 60 FPS) hides a 1.7-2.8x faster physics step.

## Skip it when

- As a library: there is no licence (the README says academic and educational purposes only), no API beyond a demo kernel, one commit, 0 stars.
- As evidence of WASM tail latency: the 'P95' column is the slowest of the 20 reps, not a 95th percentile, so it mostly measures the first, cold call.
- For real matrix work: the naive scalar triple loop is far from a blocked, SIMD or BLAS kernel; jeromewu/wasm-perf shows wasm SIMD reaching about 23x over JavaScript on a similar task.
- For cross-browser conclusions: the matrix sweeps exist only for Chromium, and no CPU, OS or browser version is recorded (docs/ENV.md is linked but missing).

## How it is fast

No special technique: both sides run the same scalar O(n^3) loop with no SIMD (no simd128 target feature, no .cargo config). Any gain comes from Rust/LLVM ahead-of-time code at opt-level 3 plus wasm-opt versus V8's JIT. Plausible contributors, not analysed in the repo, are that the wasm loop does f32 arithmetic while JavaScript computes in f64 and rounds on each Float32Array store, and that V8 typed-array accesses keep their own bounds checks.

## Compared with alternatives

Pick it over jeromewu/wasm-perf (Emscripten SIMD intrinsics, Node.js) or azeemba/wasm-runtime-performance (boost::graph Floyd-Warshall) when you want an in-browser, Playwright-automated, scalar Rust-versus-JavaScript data point. Those siblings measure SIMD or library-level gains, while this one isolates plain AOT-versus-JIT codegen on the same loop, with the data-input bug caveat.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | Rust with wasm-bindgen 0.2 and wasm-pack; Node.js with Vite 5, TypeScript 5.6, Playwright ^1.56; PixiJS 8 for the rendering demo; Python with pandas, numpy and matplotlib for charts |
| **Minimum toolchain** | Rust 1.90.0+, wasm-pack 0.13.1+, Node.js 18+ (per QUICKSTART.md) |
| **Platforms** | Any browser with WebAssembly; the matrix results come from Playwright's bundled Chromium only |
| **Thread safety** | Single-threaded; kernel state lives in thread_local RefCell globals, one matrix set per instance |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness bug: apps/wasm-matrix/src/wasm-bridge.ts calls the raw instance export set_a/set_b(ptr: \*const f32, len) with the Float32Array itself ('buf as any as number'); JavaScript's ToInt32 turns the array into NaN and then 0, so Rust's slice::from_raw_parts reads n\*n floats from linear-memory address 0 (UB on a null pointer) instead of the seeded matrices. With Rust's stack-first wasm layout that region is probably mostly zeroed stack (inference). The WASM side therefore multiplies different data, and nothing checks C against the JavaScript result (only C[0] is read as a 'checksum'). Timing is probably still representative because the loop does the same n^3 scalar multiply-adds, but the 'identical computation' claim fails.
- The 'P95' metric is sorted[floor(reps\*0.95)], which for 20 reps (and for 5) is index reps-1, the maximum. matrix_charts.py then averages these per-run maxima. The README's 'WASM 28-31% higher P95 at n&gt;=256 due to cache pressure' therefore compares cold first calls; the likelier cause (inference) is that V8 runs the first long wasm call in its Liftoff baseline tier with no on-stack replacement, while JavaScript can tier up mid-loop, which fits WASM's max/median ratio of 2.6-3.2x against 1.3x for JavaScript.
- Each page load times all 20 reps with no warm-up separation, so medians include JIT and Liftoff tier-up effects. The n=64 row aggregates runs with different rep counts (reps column 12.5) and sits at performance.now()'s roughly 0.1 ms coarsened resolution, so its 1.00x median and 1.49x mean are both noise.
- Raw per-run JSON is gitignored; only aggregated CSV and Markdown are committed, so the number of runs per size cannot be checked.

## Known shortcomings

- Harness bug: wasm-bridge.ts casts a Float32Array to a raw pointer, so the Rust kernel copies its inputs from address 0 rather than the seeded matrices and the result is never checked against JavaScript (same work on zero data); no CPU or browser version, no licence (reference); matrix runs are Chromium only; README figures are medians (means 1.46-1.69x).
- Enricher: confirms the verifier's bug (wasm-bridge.ts passes a Float32Array as a raw pointer that coerces to 0, so Rust reads from address 0 and the result is never checked against JS); the 'P95' is sorted[floor(reps\*0.95)], index 19 of 20, so it is the maximum sample and measures the cold first call; the README's 'cache pressure' explanation for worse WASM P95 at n&gt;=256 is unsupported (likely V8 Liftoff first call without wasm OSR, inference); the n=64 row mixes rep counts with timer-resolution noise.

## Caveats and trade-offs

Harness bug: apps/wasm-matrix/src/wasm-bridge.ts passes the JS Float32Array to the Rust set_a/set_b(ptr: \*const f32, len) exports via a 'buf as any as number' cast, so the pointer coerces to 0 and Rust copies len floats from linear-memory address 0 (UB on a null pointer in Rust) instead of the seeded matrices; the WASM side therefore multiplies different (probably mostly zero) data and its result is never compared with the JS result (only C[0] is read as a 'checksum'). The loop does the same n^3 scalar f32 multiply-adds, so timing is probably still representative, but the 'identical computation' claim does not hold. Other caveats: academic single-commit repo (master's thesis, Nov 2025); no licence (README says code is for academic and educational purposes), so reference only; CPU, OS and browser versions not given and docs/ENV.md is linked but missing; raw per-run results are gitignored, only aggregated CSV/MD are committed; each page load times 20 reps with no warm-up separation (JIT tier-up included); the 64x64 row sits at the 0.1 ms timer granularity; README figures are medians, means give 1.46-1.69x; naive O(n^3) kernel only, no SIMD on either side.

Needs a Rust toolchain and wasm-pack build step; large-matrix tail latency was worse in WASM (cache pressure per the author); GPU-bound workloads show no gain.

## Maintenance

Single-commit master's-thesis snapshot (2025-11-30, 0 stars, no issues) with no licence, so reference only. Useful as a reproducible-looking browser harness once the set_a/set_b bridge is fixed (pass a pointer into wasm memory, or take &[f32] and use the wasm-bindgen glue as the particle bridge does).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The README Results Summary and results/figures/matrix/matrix_results_table.md and matrix_js_vs_wasm.csv carry the JS-vs-WASM matrix numbers, and the harness is public (apps/js-matrix, apps/wasm-matrix, wasm-kernels/kernels/matrix/src/lib.rs, tools/bench-runner/matrix-sweep.mjs). No CPU model, OS, or Chromium/V8 version is stated anywhere (docs/ENV.md is linked but absent from the repo), so it is first-party with partial methodology: tier C.
- **Verifier notes:** Numbers on the page match the record (README table equals results/figures/matrix/matrix_results_table.md; medians). Shortcomings to record: WASM bridge passes a typed array as a raw pointer, so the Rust kernel reads its inputs from address 0 and multiplies different data than JS (result unchecked); no hardware or browser versions; no licence; single-commit thesis repo; matrix sweeps Chromium only.
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-66 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/Chankse/JavaScript-vs-WebAssembly-Comparative-Analysis>
  - <https://github.com/Chankse/JavaScript-vs-WebAssembly-Comparative-Analysis/commits>
  - <https://github.com/Chankse/JavaScript-vs-WebAssembly-Comparative-Analysis/tree/master/results/figures>
  - <https://github.com/Chankse/JavaScript-vs-WebAssembly-Comparative-Analysis/tree/master/results/figures/matrix>
  - <https://raw.githubusercontent.com/Chankse/JavaScript-vs-WebAssembly-Comparative-Analysis/HEAD/README.md>
  - <https://raw.githubusercontent.com/Chankse/JavaScript-vs-WebAssembly-Comparative-Analysis/master/QUICKSTART.md>
  - <https://raw.githubusercontent.com/Chankse/JavaScript-vs-WebAssembly-Comparative-Analysis/master/package.json>
  - <https://raw.githubusercontent.com/Chankse/JavaScript-vs-WebAssembly-Comparative-Analysis/master/wasm-kernels/Cargo.toml>
  - <https://raw.githubusercontent.com/Chankse/JavaScript-vs-WebAssembly-Comparative-Analysis/HEAD/wasm-kernels/kernels/matrix/Cargo.toml>
  - <https://raw.githubusercontent.com/Chankse/JavaScript-vs-WebAssembly-Comparative-Analysis/master/wasm-kernels/kernels/matrix/src/lib.rs>
  - <https://raw.githubusercontent.com/Chankse/JavaScript-vs-WebAssembly-Comparative-Analysis/master/apps/wasm-matrix/src/wasm-bridge.ts>
  - <https://raw.githubusercontent.com/Chankse/JavaScript-vs-WebAssembly-Comparative-Analysis/master/apps/wasm-matrix/src/main.ts>
  - <https://raw.githubusercontent.com/Chankse/JavaScript-vs-WebAssembly-Comparative-Analysis/master/apps/js-matrix/src/main.ts>
  - <https://raw.githubusercontent.com/Chankse/JavaScript-vs-WebAssembly-Comparative-Analysis/HEAD/apps/js-matrix/src/matmul.ts>
  - <https://raw.githubusercontent.com/Chankse/JavaScript-vs-WebAssembly-Comparative-Analysis/HEAD/tools/bench-runner/index.mjs>
  - <https://raw.githubusercontent.com/Chankse/JavaScript-vs-WebAssembly-Comparative-Analysis/master/tools/bench-runner/matrix-sweep.mjs>
  - <https://raw.githubusercontent.com/Chankse/JavaScript-vs-WebAssembly-Comparative-Analysis/master/results/figures/matrix/matrix_agg.csv>
  - <https://raw.githubusercontent.com/Chankse/JavaScript-vs-WebAssembly-Comparative-Analysis/master/results/figures/matrix/matrix_js_vs_wasm.csv>
  - <https://raw.githubusercontent.com/Chankse/JavaScript-vs-WebAssembly-Comparative-Analysis/master/results/figures/matrix/matrix_results_table.md>
  - <https://raw.githubusercontent.com/Chankse/JavaScript-vs-WebAssembly-Comparative-Analysis/master/results/figures/matrix/p95_compact_summary.md>
- **Sources the enricher read:**
  - <https://github.com/Chankse/JavaScript-vs-WebAssembly-Comparative-Analysis>
  - <https://github.com/Chankse/JavaScript-vs-WebAssembly-Comparative-Analysis/commits>
  - <https://github.com/Chankse/JavaScript-vs-WebAssembly-Comparative-Analysis/issues>
  - <https://github.com/Chankse/JavaScript-vs-WebAssembly-Comparative-Analysis/tree/master/wasm-kernels>
  - <https://raw.githubusercontent.com/Chankse/JavaScript-vs-WebAssembly-Comparative-Analysis/master/README.md>
  - <https://raw.githubusercontent.com/Chankse/JavaScript-vs-WebAssembly-Comparative-Analysis/master/QUICKSTART.md>
  - <https://raw.githubusercontent.com/Chankse/JavaScript-vs-WebAssembly-Comparative-Analysis/master/package.json>
  - <https://raw.githubusercontent.com/Chankse/JavaScript-vs-WebAssembly-Comparative-Analysis/master/vite.config.ts>
  - <https://raw.githubusercontent.com/Chankse/JavaScript-vs-WebAssembly-Comparative-Analysis/master/wasm-kernels/Cargo.toml>
  - <https://raw.githubusercontent.com/Chankse/JavaScript-vs-WebAssembly-Comparative-Analysis/master/wasm-kernels/kernels/matrix/Cargo.toml>
  - <https://raw.githubusercontent.com/Chankse/JavaScript-vs-WebAssembly-Comparative-Analysis/master/wasm-kernels/kernels/matrix/src/lib.rs>
  - <https://raw.githubusercontent.com/Chankse/JavaScript-vs-WebAssembly-Comparative-Analysis/master/apps/wasm-matrix/src/wasm-bridge.ts>
  - <https://raw.githubusercontent.com/Chankse/JavaScript-vs-WebAssembly-Comparative-Analysis/master/apps/wasm-matrix/src/main.ts>
  - <https://raw.githubusercontent.com/Chankse/JavaScript-vs-WebAssembly-Comparative-Analysis/master/apps/wasm-matrix/src/seeded-rng.ts>
  - <https://raw.githubusercontent.com/Chankse/JavaScript-vs-WebAssembly-Comparative-Analysis/master/apps/wasm-matrix/index.html>
  - <https://raw.githubusercontent.com/Chankse/JavaScript-vs-WebAssembly-Comparative-Analysis/master/apps/js-matrix/src/main.ts>
  - <https://raw.githubusercontent.com/Chankse/JavaScript-vs-WebAssembly-Comparative-Analysis/master/apps/js-matrix/src/matmul.ts>
  - <https://raw.githubusercontent.com/Chankse/JavaScript-vs-WebAssembly-Comparative-Analysis/master/apps/wasm-rendering/src/wasm-bridge.ts>
  - <https://raw.githubusercontent.com/Chankse/JavaScript-vs-WebAssembly-Comparative-Analysis/master/apps/shared/seeded-rng.ts>
  - <https://raw.githubusercontent.com/Chankse/JavaScript-vs-WebAssembly-Comparative-Analysis/master/tools/bench-runner/index.mjs>
  - <https://raw.githubusercontent.com/Chankse/JavaScript-vs-WebAssembly-Comparative-Analysis/master/tools/bench-runner/matrix-sweep.mjs>
  - <https://raw.githubusercontent.com/Chankse/JavaScript-vs-WebAssembly-Comparative-Analysis/master/tools/charts/matrix_charts.py>
  - <https://raw.githubusercontent.com/Chankse/JavaScript-vs-WebAssembly-Comparative-Analysis/master/results/figures/matrix/matrix_agg.csv>
  - <https://raw.githubusercontent.com/Chankse/JavaScript-vs-WebAssembly-Comparative-Analysis/master/results/figures/matrix/matrix_js_vs_wasm.csv>
  - <https://raw.githubusercontent.com/Chankse/JavaScript-vs-WebAssembly-Comparative-Analysis/master/results/figures/matrix/matrix_results_table.md>
  - <https://raw.githubusercontent.com/Chankse/JavaScript-vs-WebAssembly-Comparative-Analysis/master/results/figures/matrix/p95_compact_summary.md>
  - https://raw.githubusercontent.com/Chankse/JavaScript-vs-WebAssembly-Comparative-Analysis/master/docs/ENV.md (404)
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/chankse/javascript-vs-webassembly-comparative-analysis`) · [data/wave13/enrich/raw/github_com_chankse_javascript_vs_webassembly_comparative_analysis.json](../../../data/wave13/enrich/raw/github_com_chankse_javascript_vs_webassembly_comparative_analysis.json) (enrichment confidence 0.6)

</details>
