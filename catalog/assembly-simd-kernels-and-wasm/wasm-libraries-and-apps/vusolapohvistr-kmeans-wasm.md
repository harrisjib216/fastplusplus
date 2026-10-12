# kmeans-wasm

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly libraries and apps](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust (WebAssembly SIMD, simd128) with JavaScript wrapper` · `MIT` · 🟢 active

> Rust-to-WebAssembly k-means (Hamerly bounds, distinct-colour weighting) for colour quantisation and vectors; beats the naive JS skmeans.

| | |
|---|---|
| **Beats** | skmeans (JavaScript k-means library) |
| **Claimed result** | 10,000 points x 50 dims x 10 clusters 83.15 ms vs skmeans 1456.35 ms (17.5x); 100,000 random RGB pixels, 32 colours 247.03 vs 1677.87 ms (6.8x); photo blue-marble, 16 colours 109.24 vs 11133.62 ms (101.8x); small input 1,000 pixels, 2 colours 0.47 vs 0.41 ms (0.9x, slower) |
| **Workload** | k-means clustering of random RGB pixels, random multi-dimensional points and four real photographs for colour quantisation; median of five runs. |
| **Metric** | latency |
| **Hardware** | AMD Ryzen 5 9600X, Node.js 26.10.0 |
| **Compiler and flags** | Rust (edition 2024, rust-version 1.98 minimum; exact rustc version not stated) built with wasm-pack build --release --target nodejs; Cargo.toml [profile.release] opt-level = 3, lto = true, codegen-units = 1, panic = abort, strip; .cargo/config.toml rustflags -C target-feature=+simd128 for wasm32-unknown-unknown; wasm-opt -O4 --enable-simd --enable-bulk-memory --enable-nontrapping-float-to-int. Harness: js_bench/src/vector.ts, rgb.ts, images.ts (TypeScript, Node). |
| **Adoption** | 2 stars, 1 fork |
| **Last commit** | 2026-09-27 |
| **Links** | [repository](https://github.com/vusolapohvistr/kmeans-wasm) · [benchmark](https://github.com/vusolapohvistr/kmeans-wasm) |

## Verdict

First-party js_bench Node harnesses (Node.js 26.10.0, AMD Ryzen 5 9600X, release build with LTO, codegen-units 1, wasm-opt -O4 and +simd128) against skmeans 0.11.3, a plain-JS Lloyd k-means, both capped at 100 iterations with kmeans-wasm's threshold at 0: 10,000 points x 50 dims, k=10 83.15 vs 1456.35 ms (17.5x); 100,000 random RGB pixels, 32 colours 247.03 vs 1677.87 ms (6.8x); the 922,560-pixel blue-marble photo at 16 colours 109.24 vs 11133.62 ms (101.8x, skmeans a single sample); 1,000 pixels at k=2 0.47 vs 0.41 ms (0.9x, slower).

## Use it when

- Colour quantisation of photographs or canvas ImageData in a browser or Node: kmeans_rgba reads ImageData.data directly and apply_palette produces the RGBA output; on 6% to 46% distinct photos it ran 6x to 102x faster than skmeans.
- Replacing a naive Lloyd k-means in JavaScript (skmeans or hand-written) on low-dimensional data with k of 8 or more, where the README shows 5.7x to 17.5x on 10,000 to 100,000 points.
- Code that already consumes skmeans' result shape (centroids, idxs, test) and can adapt to a different argument order.
- The palette-mapping step alone: apply_palette was 1.1x to 2.1x faster than a Map-memoised JS nearest-colour loop with byte-identical output.

## Skip it when

- k=2 or small inputs: 1,000 pixels at k=2 was 0.9x (slower) and 100,000 pixels at k=2 1.1x; there is nothing for the bounds to skip.
- When the alternative is already a bounds-based or tree-based k-means (a JS Hamerly/Elkan port, or a native ML library): no such baseline was measured, and most of the reported gain is the algorithm rather than wasm.
- When you need deterministic results without monkey-patching Math.random, k-means++ seeding, a custom distance during clustering, mini-batch or streaming updates, or worker/thread parallelism; none is offered.
- Runtimes without wasm SIMD (Safari before 16.4, older Chrome/Firefox): the module requires simd128 and ships no scalar fallback.
- Projects that need a mature dependency: 2 stars, no issues filed, five releases (3.3.0 to 3.7.0) within four days, and the README says most code since 3.2.0 was written by AI assistants.

## How it is fast

The core is Hamerly's bounded Lloyd iteration: each point keeps an upper bound to its centroid and a lower bound to the runner-up, and the full k-centroid scan is skipped when the upper bound is below max(half the distance to the nearest other centroid, lower bound). The packed entry points first collapse the input to its distinct colours with occurrence weights in a fixed 2^18-slot open-addressing table (Celebi's weighted sort-means), which is exact for u8 data and shrinks real photographs 2x to 16x. Points and centroids sit in flat row-major f64 buffers and the squared distance uses an f64x2 simd128 kernel (fearless_simd). The k=2 rows, where bounds prune little, run level with the JS baseline (0.9x to 1.1x, derived from page data), so wasm plus SIMD alone adds little and the gain is algorithmic.

## Compared with alternatives

No other k-means library is catalogued in this category; the closest numeric siblings are Ubique (nalgebra in wasm vs math.js) and the TensorFlow.js wasm backend, so pick kmeans-wasm when the job is specifically clustering or palette extraction rather than general linear algebra or neural-network inference.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none at runtime (wasm-bindgen JS glue plus the .wasm); build uses wasm-bindgen, js-sys, rand, fearless_simd and getrandom crates |
| **Minimum toolchain** | Rust 1.98 (edition 2024) and wasm-pack to build; runtime needs WebAssembly SIMD (Chrome 91+, Firefox 89+, Safari 16.4+); dev tooling pins Node ^22.22.2, ^24.15.0 or &gt;=26 |
| **Platforms** | any WebAssembly runtime with simd128; the published npm package is the wasm-pack bundler target (ESM-only), while the benchmarks used a separate --target nodejs build |
| **Thread safety** | not documented; calls are synchronous on one wasm instance and there is no worker or threads support |
| **Drop-in for the baseline** | partial — kmeans(data, k, maxIter, threshold) returns skmeans' result shape, but the third argument is maxIter rather than skmeans' initial centroids, there is no seeding option or clustering distance callback, idxs is a Uint32Array, and test() returns an index instead of skmeans' {idx, centroid} |

## Gotchas

- Harness flaw: the real-image skmeans column (the 69x to 102x rows) is one measured run after one warm-up with an unpinned Math.random seed, while kmeans-wasm gets eight runs; the project's own AGENTS.md says single samples on that machine vary by up to 50% and that unpinned-seed comparisons compare two different initialisations. Neither harness logs the iteration count of either side, and once Hamerly converges its extra rounds cost only bound checks plus k^2 centroid distances, so the README's 'threshold 0 makes the speed-ups a floor' argument is weaker than stated.
- The convergence test compares the sum over all centroids of squared movement against an absolute threshold, so it scales with k and data range; kmeans() defaults to 0 (always runs maxIter) and the packed calls default to 0.1.
- Rows that are not plain JS Arrays (e.g. Float64Array) or non-numeric values hit unwrap() in kmeans() and abort as a wasm 'unreachable' trap (panic = abort) instead of the documented string error.
- Packed palettes truncate centroids with 'as u8' (floor, not round); k above the number of distinct colours repeats the last seed and returns duplicate palette entries. README tables before commit 0f53d6a (2026-09-27) measured a 256-colour repeating LCG pattern labelled random; the current tables are from the fixed mulberry32-style generator.

## Known shortcomings

- The win is mostly algorithmic (Hamerly bounds, distinct-colour dedup) against the naive JavaScript skmeans, whose image runs are single-sample; only a minimum rustc (1.98) is given; 2 stars, AI-written.
- Harness flaw: the real-image skmeans column (the 69x-102x rows) is one run after one warm-up with an unpinned Math.random seed while kmeans-wasm gets 8 runs; the project's own AGENTS.md says single samples vary 50% and unpinned seeds compare different initialisations. The win is mostly algorithmic (Hamerly bounds plus Celebi distinct-colour dedup) against a naive JS Lloyd baseline; the k = 2 rows at 0.9x-1.1x show wasm plus SIMD alone adds little. README tables before commit 0f53d6a measured a 256-colour LCG pattern labelled random (now fixed).

## Caveats and trade-offs

First-party; most of the code and the harness since v3.2.0 were written by AI assistants (README says so). The baseline skmeans is a naive Lloyd k-means in plain JavaScript that scans all n\*k distances every round, while kmeans-wasm uses Hamerly bounds and, for the packed RGB/RGBA entry points, collapses the input to its distinct colours with weights; most of the speed-up is algorithmic, not from wasm or SIMD, and the README says the image speed-up falls from 84x to 13x as the distinct-colour share grows. No stronger JS k-means (e.g. a bounds-based one) is compared. Small or k=2 cases are level or slower (1,000 pixels, 2 colours 0.9x; 100,000 pixels, 2 colours 1.1x). Real-image skmeans timings are one measured run after one warm-up. Seeds differ per run on both sides (random distinct input points vs skmeans kmrand), so the two sides can converge to different local minima; kmeans-wasm always runs all 100 iterations (threshold 0) while skmeans may stop early, which favours skmeans. 2 stars. [retier] First-party; most of the code and the harness since v3.2.0 were written by AI assistants (README says so). Harness flaw: the real-image skmeans column (the 69x to 102x rows) is one measured run after one warm-up with an unpinned Math.random seed while kmeans-wasm gets eight runs; the project's own AGENTS.md says single samples on that machine vary by up to 50% and that unpinned-seed comparisons compare two different initialisations; neither harness logs either side's iteration count. The baseline skmeans is a naive Lloyd k-means in plain JavaScript that scans all n\*k distances every round, while kmeans-wasm uses Hamerly bounds and, for the packed RGB/RGBA entry points, collapses the input to its distinct colours with weights, so most of the speed-up is algorithmic (the README says the image speed-up falls from 84x to 13x as the distinct-colour share grows) and the k = 2 rows at 0.9x-1.1x show wasm plus SIMD alone adds little; no stronger JS k-means was compared. README tables before commit 0f53d6a (2026-09-27) measured a 256-colour repeating LCG pattern labelled random. The convergence test scales with k and data range; non-Array rows abort as a wasm 'unreachable' trap; packed palettes truncate centroids with 'as u8' and k above the number of distinct colours returns duplicate entries.

Requires wasm SIMD (Chrome 91+, Firefox 89+, Safari 16.4+); small inputs and tiny cluster counts gain little or lose.

## Maintenance

Actively developed (v3.7.0 on npm 2026-09-27, 65 commits) and MIT-licensed with a small core, but tiny (2 stars), largely AI-written, and its photo speed-ups rest on single unpinned-seed skmeans samples against a naive JS baseline, so treat the large ratios as algorithmic and directional.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now C.
- **Tier reason:** README tables compare kmeans_rgb/kmeans against skmeans with the harness public in js_bench/src/vector.ts, rgb.ts and images.ts (same 100-iteration cap, threshold 0 so kmeans-wasm never exits early, skmeans' own kmrand seeding, inputs built outside the timer); build flags are public in Cargo.toml (release: opt-level 3, LTO, codegen-units 1, panic abort; wasm-opt -O4) and .cargo/config.toml (+simd128), and the CPU (AMD Ryzen 5 9600X) and runtime (Node.js 26.10.0) are stated. Only the exact rustc version is unpinned (rust-version 1.98 minimum).
- **Retiered** A to C: Enricher: the headline real-image rows (69x-102x) time the skmeans baseline once after one warm-up with an unpinned Math.random seed while kmeans-wasm gets eight runs, on a machine whose own AGENTS.md says single samples vary by up to 50% and unpinned seeds compare different initialisations; the win is mostly algorithmic (Hamerly bounds plus distinct-colour dedup against a naive Lloyd loop) and the pre-0f53d6a tables measured a 256-colour LCG pattern labelled random. Asymmetric sampling on the headline rows (LC and TensorFlow precedents): A to C.
- **Verifier notes:** README numbers match the record exactly (10,000 x 50 x 10: 83.15 vs 1456.35 ms, 17.5x; 100,000 RGB px, 32 colours 247.03 vs 1677.87 ms, 6.8x; blue-marble 16 colours 109.24 vs 11133.62 ms, 101.8x; 1,000 px 2 colours 0.47 vs 0.41 ms, 0.9x). Flags are public in the repo's build config, so A stands; record the shortcoming that the win is mostly algorithmic (Hamerly bounds plus distinct-colour dedup) against a naive JS baseline, with single-sample skmeans image runs and a tiny project (2 stars, AI-written). License MIT (LICENSE_MIT), last commit 2026-09-27 (release v3.7.0), not a fork.
- **Fields the verifier corrected:** `compiler_and_flags`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-80 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/vusolapohvistr/kmeans-wasm/HEAD/README.md>
  - <https://github.com/vusolapohvistr/kmeans-wasm>
  - <https://github.com/vusolapohvistr/kmeans-wasm/commits/main>
  - <https://github.com/vusolapohvistr/kmeans-wasm/tree/main/js_bench>
  - <https://github.com/vusolapohvistr/kmeans-wasm/tree/main/js_bench/src>
  - <https://github.com/vusolapohvistr/kmeans-wasm/tree/main/src>
  - <https://raw.githubusercontent.com/vusolapohvistr/kmeans-wasm/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/vusolapohvistr/kmeans-wasm/HEAD/.cargo/config.toml>
  - <https://raw.githubusercontent.com/vusolapohvistr/kmeans-wasm/HEAD/package.json>
  - <https://raw.githubusercontent.com/vusolapohvistr/kmeans-wasm/HEAD/js_bench/package.json>
  - <https://raw.githubusercontent.com/vusolapohvistr/kmeans-wasm/HEAD/js_bench/src/vector.ts>
  - <https://raw.githubusercontent.com/vusolapohvistr/kmeans-wasm/HEAD/js_bench/src/rgb.ts>
  - <https://raw.githubusercontent.com/vusolapohvistr/kmeans-wasm/HEAD/js_bench/src/images.ts>
  - <https://raw.githubusercontent.com/vusolapohvistr/kmeans-wasm/HEAD/src/kmeans_triangle.rs>
  - <https://raw.githubusercontent.com/vusolapohvistr/kmeans-wasm/HEAD/src/lib.rs>
- **Sources the enricher read:**
  - <https://github.com/vusolapohvistr/kmeans-wasm>
  - <https://github.com/vusolapohvistr/kmeans-wasm/commits/main>
  - <https://github.com/vusolapohvistr/kmeans-wasm/commit/0f53d6a>
  - <https://github.com/vusolapohvistr/kmeans-wasm/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/vusolapohvistr/kmeans-wasm/HEAD/README.md>
  - <https://raw.githubusercontent.com/vusolapohvistr/kmeans-wasm/HEAD/AGENTS.md>
  - <https://raw.githubusercontent.com/vusolapohvistr/kmeans-wasm/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/vusolapohvistr/kmeans-wasm/HEAD/.cargo/config.toml>
  - <https://raw.githubusercontent.com/vusolapohvistr/kmeans-wasm/HEAD/package.json>
  - <https://raw.githubusercontent.com/vusolapohvistr/kmeans-wasm/HEAD/js_bench/package.json>
  - <https://raw.githubusercontent.com/vusolapohvistr/kmeans-wasm/HEAD/js_bench/src/vector.ts>
  - <https://raw.githubusercontent.com/vusolapohvistr/kmeans-wasm/HEAD/js_bench/src/rgb.ts>
  - <https://raw.githubusercontent.com/vusolapohvistr/kmeans-wasm/HEAD/js_bench/src/images.ts>
  - <https://raw.githubusercontent.com/vusolapohvistr/kmeans-wasm/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/vusolapohvistr/kmeans-wasm/HEAD/src/kmeans_triangle.rs>
  - <https://raw.githubusercontent.com/vusolapohvistr/kmeans-wasm/HEAD/src/packed_histogram.rs>
  - <https://raw.githubusercontent.com/solzimer/skmeans/HEAD/main.js>
  - <https://raw.githubusercontent.com/solzimer/skmeans/HEAD/distance.js>
  - <https://raw.githubusercontent.com/solzimer/skmeans/HEAD/kinit.js>
  - <https://raw.githubusercontent.com/solzimer/skmeans/HEAD/package.json>
  - <https://registry.npmjs.org/kmeans-wasm>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/vusolapohvistr/kmeans-wasm`) · [data/wave13/enrich/raw/github_com_vusolapohvistr_kmeans_wasm.json](../../../data/wave13/enrich/raw/github_com_vusolapohvistr_kmeans_wasm.json) (enrichment confidence 0.75)

</details>
