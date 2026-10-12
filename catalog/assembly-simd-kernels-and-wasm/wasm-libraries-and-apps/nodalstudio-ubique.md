# Ubique (nalgebra compiled to WebAssembly)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly libraries and apps](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust (nalgebra compiled to WebAssembly) with TypeScript on Deno` · `MIT` · 🟢 active

> MATLAB-style TypeScript math library with nalgebra-in-WebAssembly kernels; first-party runs show 4.6-26x faster than math.js.

| | |
|---|---|
| **Beats** | math.js (JavaScript numerical library) |
| **Claimed result** | README highlights vs math.js (scripts/benchmark.ts, Deno, one timed loop per test, no warm-up): matrix multiply (500x500) 13.05x and determinant (50x50) 26.04x, determinant (20x20) 12.27x and matrix inverse (20x20) 7.53x through the nalgebra wasm path; matrix add (100x100) 6.61x and transpose (100x100) 4.63x through plain TypeScript Array.map (no wasm or nalgebra involved, although the README attributes them to nalgebra compiled to WebAssembly); inv uses wasm only above 10x10. README_NPM says 'up to 20x' while the table shows 26.04x; 6 of the suite's 17 rows are shown. |
| **Workload** | Matrix and linear algebra operations: multiply 500x500, add and transpose 100x100, determinant 50x50 and 20x20, inverse 20x20. |
| **Metric** | latency |
| **Hardware** | Mac mini M1 |
| **Compiler and flags** | Cargo release profile opt-level="z", lto=true, codegen-units=1 (Cargo.toml), built with deno wasmbuild (jsr:@deno/wasmbuild); rustc, Deno and math.js versions not stated |
| **Adoption** | 5 stars |
| **Last commit** | 2026-05-18 |
| **Links** | [repository](https://github.com/NodalStudio/Ubique) · [benchmark](https://github.com/NodalStudio/Ubique) |

## Verdict

First-party README numbers on a Mac mini M1 against math.js (version unpinned in the CLI harness): 500x500 multiply 13.05x, 50x50 determinant 26.04x, 20x20 determinant 12.27x and 20x20 inverse 7.53x faster, all through nalgebra compiled to wasm at opt-level z, plus 100x100 add 6.61x and transpose 4.63x, which are plain TypeScript loops; the Deno and rustc versions and the run that produced the table are not stated.

## Use it when

- JavaScript or TypeScript code (Deno, Node.js or browser) that does dense float64 linear algebra on plain nested arrays and where math.js multiply, det or inv on 20x20 to 500x500 matrices is the bottleneck.
- Repeated determinants and inverses of medium matrices (20x20 to 50x50), where the first-party gains are largest (7.5x to 26x).
- You want MATLAB-like names plus statistics and quant-finance helpers in one MIT package whose only runtime dependency is dayjs.
- You want wasm-accelerated kernels without bundler configuration for a .wasm asset (the module is inlined).

## Skip it when

- You need math.js's wider feature set (BigNumber, fractions, units, sparse matrices, expression parsing); Ubique works on plain float64 numbers and arrays.
- Large matrices or throughput-critical numerics: the wasm is size-optimised, single-threaded and built without SIMD, and every call copies inputs in and outputs out; a SIMD or multithreaded wasm backend or native BLAS will be faster.
- Data with small-magnitude entries: det returns exactly 0 whenever |det| &lt; 1e-15 (absolute threshold in both detwasm and the JS fallback), so for example 0.01 times the 10x10 identity (det 1e-20) is reported as singular.
- Small inverses (n &lt;= 10) take the JavaScript linsolve path, not wasm, and the suite's 10x10 inverse row is not reported in the README, so no speedup is shown for that size.
- You need a widely used, battle-tested library: 5 stars, no GitHub issues filed, two maintainers, and the recent commits (May 2026) are benchmark-page work.

## How it is fast

Matrix multiply, determinant, inverse (only for n &gt; 10), mean, std, variance, z-score, covariance and LU call into a Rust cdylib (rs_lib/src/lib.rs) that uses nalgebra 0.33 DMatrix routines (dense product, LU determinant, try_inverse), exported through wasm-bindgen; inputs are flattened into a Float64Array, copied into wasm linear memory and the result is reshaped into nested arrays on return. Transpose and matrix add, two of the six README highlights, are plain TypeScript Array.map loops (lib/matarrs/transpose.ts, lib/elemop/plus.ts), so their 4.63x and 6.61x compare nested-array loops with math.js's generic transpose and add, not wasm. The wasm is built for size (opt-level "z", LTO, codegen-units 1) with no SIMD target feature set in the repo's Cargo files.

## Compared with alternatives

No sibling in this category is a general linear-algebra library: pick Ubique for MATLAB-style dense matrix and statistics functions on plain JS arrays, and the TensorFlow.js wasm backend when your data already lives in tensors or you need ML operators; kmeans-wasm and hash-wasm cover single kernels only.

## Integration

| | |
|---|---|
| **Form** | module (JSR @nodalstudio/ubique and npm ubique 1.0.2, ESM and CommonJS builds, wasm inlined in the JavaScript) |
| **Dependencies** | dayjs; rebuilding the wasm needs Rust with nalgebra 0.33.2 and wasm-bindgen 0.2.106 plus deno wasmbuild (the built rs_lib/pkg output is committed) |
| **Minimum toolchain** | Node.js 20.6+ for the jsr: specifier route (README); otherwise not documented. Any runtime with WebAssembly support |
| **Platforms** | any JavaScript runtime with WebAssembly (Deno, Node.js, browsers via esm.sh); wasm32 without SIMD |
| **Thread safety** | not documented; synchronous single-threaded functions |
| **Drop-in for the baseline** | no |

## Gotchas

- det uses an absolute cutoff: results with |det| &lt; 1e-15 are returned as 0 (rs_lib/src/lib.rs detwasm and lib/linalgebra/det.ts), so well-conditioned matrices with small entries look singular; math.js returns the actual value.
- Two of the six README highlights (Transpose 100x100 4.63x, Matrix Add 100x100 6.61x) do not use wasm or nalgebra at all, although the README attributes the gains to nalgebra compiled to WebAssembly; inv only uses wasm above 10x10.
- Harness flaws in scripts/benchmark.ts: one timed loop per test with no warmup (5 iterations for the 500x500 multiply), Ubique always timed first, math.js imported unversioned (npm:mathjs), runtime versions not recorded; the README shows 6 of the suite's 17 rows, and README_NPM says 'up to 20x' while its table shows 26.04x. The interactive browser benchmark the README links (scripts/assets/benchmark.html) pins mathjs@13.2.2 but loads '@bemayer/rubique@1.0.2' from JSR, a pre-rename package whose versions are all yanked (published 2025-10-12), so it does not measure the published @nodalstudio/ubique.
- Every wasm call flattens nested arrays into a Float64Array, copies them into wasm memory and rebuilds nested arrays from the result; this cost is included in the benchmark but dominates for tiny matrices, even though the code comments say wasm is used 'even for 2x2'.

## Known shortcomings

- Harness scripts/benchmark.ts exists but math.js is unpinned, there is no warmup and only 6 of 17 rows are reported; a rewrite of the maxto/ubique fork.
- Claim flaws: the README credits the gains to nalgebra compiled to wasm, but the Transpose 4.63x and Matrix Add 6.61x rows are plain TypeScript Array.map, and inv uses wasm only above 10x10. The interactive browser benchmark loads @bemayer/rubique@1.0.2 from JSR, all versions yanked, so the page does not measure the published @nodalstudio/ubique; README_NPM says 'up to 20x' while the table shows 26.04x. Correctness bug: det returns 0 when |det| &lt; 1e-15 (absolute cutoff in both the wasm and JS paths); the benchmark inputs do not hit it, so the numbers stand.

## Caveats and trade-offs

First-party numbers; GitHub lists the repo as a fork of maxto/ubique, and v1.0 is a full rewrite on nalgebra compiled to wasm. The harness is scripts/benchmark.ts: it imports npm:mathjs unversioned, times one loop per test (5 iterations for the 500x500 multiply, 50-200 elsewhere) on fresh random inputs with no warmup, and always times Ubique first. It checks results against math.js to 6 decimals. The README shows 6 highlight rows out of the suite's 17 (statistics rows and the 10x10/50x50/100x100 multiply and 10x10 inverse rows are not reported), so selective reporting is possible. The wasm is built for size (opt-level z) without SIMD flags. math.js is a generic pure-JS library, not a tuned JS linear-algebra baseline. The github.io interactive benchmark page could not be opened here. [retier] First-party numbers; GitHub lists the repo as a fork of maxto/ubique, and v1.0 is a full rewrite on nalgebra compiled to wasm. Harness flaws in scripts/benchmark.ts: it imports npm:mathjs unversioned, times one loop per test (5 iterations for the 500x500 multiply, 50-200 elsewhere) on fresh random inputs with no warm-up, always times Ubique first, and records no runtime versions; results are checked against math.js to 6 decimals. The README shows 6 of the suite's 17 rows (statistics rows and the 10x10/50x50/100x100 multiply and 10x10 inverse rows are not reported), and two of the six highlights (Transpose 4.63x, Matrix Add 6.61x) are plain TypeScript Array.map, not wasm. The interactive browser benchmark the README links (scripts/assets/benchmark.html) pins mathjs@13.2.2 but loads @bemayer/rubique@1.0.2 from JSR, a pre-rename package whose versions are all yanked, so it does not measure the published @nodalstudio/ubique. Every wasm call flattens nested arrays into a Float64Array, copies them into wasm memory and rebuilds nested arrays from the result (included in the timings; dominates for tiny matrices). The wasm is built for size (opt-level z) without SIMD flags. Correctness: det returns 0 when |det| &lt; 1e-15 (absolute cutoff in both the wasm and JS paths), so well-conditioned matrices with small entries look singular (the benchmark inputs do not hit it).

Data must be copied between JS and wasm memory, and the README gives no information about small sizes; published on JSR for Deno.

## Maintenance

Active but small (5 stars, 260 commits, last commit 2026-05-18, JSR and npm 1.0.2 published November 2025), MIT-licensed and easy to install; treat the speedups as first-party, re-measure at your sizes, and watch the det zero cutoff.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README highlights against math.js on a Mac mini M1; the harness is public (scripts/benchmark.ts, run by deno task benchmark) but the math.js version is unpinned and rustc/Deno versions are not stated, so not A.
- **Verifier notes:** The README numbers (13.05x, 6.61x, 4.63x, 26.04x, 7.53x, 12.27x on a Mac mini M1) match the record; the benchmark source exists at scripts/benchmark.ts, which the search agent missed. Shortcomings: unpinned math.js version, no warmup, single timed loop, only 6 of 17 suite rows reported, weak generic JS baseline, 5 stars. GitHub shows 'forked from maxto/ubique' (now a rewrite).
- **Fields the verifier corrected:** `is_fork_of`, `compared_against_cpp_std_directly`, `compiler_and_flags`, `caveats`, `claimed_speedup`
- **Shortcomings recorded by:** verifier batch-89 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/NodalStudio/Ubique>
  - <https://github.com/NodalStudio/Ubique/commits>
  - <https://github.com/NodalStudio/Ubique/tree/main/scripts>
  - <https://raw.githubusercontent.com/NodalStudio/Ubique/HEAD/README.md>
  - <https://raw.githubusercontent.com/NodalStudio/Ubique/HEAD/deno.json>
  - <https://raw.githubusercontent.com/NodalStudio/Ubique/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/NodalStudio/Ubique/HEAD/scripts/benchmark.ts>
- **Sources the enricher read:**
  - <https://github.com/NodalStudio/Ubique>
  - <https://github.com/NodalStudio/Ubique/commits/main>
  - <https://github.com/NodalStudio/Ubique/issues?q=is%3Aissue>
  - <https://github.com/NodalStudio/Ubique/tree/main/rs_lib/src>
  - <https://github.com/NodalStudio/Ubique/tree/main/lib>
  - <https://github.com/NodalStudio/Ubique/tree/main/lib/linalgebra>
  - <https://github.com/NodalStudio/Ubique/tree/main/lib/matarrs>
  - <https://github.com/NodalStudio/Ubique/tree/main/lib/elemop>
  - <https://github.com/NodalStudio/Ubique/tree/main/scripts/assets>
  - <https://raw.githubusercontent.com/NodalStudio/Ubique/HEAD/README.md>
  - <https://raw.githubusercontent.com/NodalStudio/Ubique/HEAD/README_NPM.md>
  - <https://raw.githubusercontent.com/NodalStudio/Ubique/HEAD/deno.json>
  - <https://raw.githubusercontent.com/NodalStudio/Ubique/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/NodalStudio/Ubique/HEAD/.gitignore>
  - <https://raw.githubusercontent.com/NodalStudio/Ubique/HEAD/rs_lib/Cargo.toml>
  - <https://raw.githubusercontent.com/NodalStudio/Ubique/HEAD/rs_lib/src/lib.rs>
  - <https://raw.githubusercontent.com/NodalStudio/Ubique/HEAD/index.ts>
  - <https://raw.githubusercontent.com/NodalStudio/Ubique/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/NodalStudio/Ubique/HEAD/scripts/benchmark.ts>
  - <https://raw.githubusercontent.com/NodalStudio/Ubique/HEAD/scripts/assets/benchmark.html>
  - <https://raw.githubusercontent.com/NodalStudio/Ubique/HEAD/scripts/assets/landing_script.js>
  - <https://raw.githubusercontent.com/NodalStudio/Ubique/HEAD/lib/matarrs/transpose.ts>
  - <https://raw.githubusercontent.com/NodalStudio/Ubique/HEAD/lib/elemop/plus.ts>
  - <https://raw.githubusercontent.com/NodalStudio/Ubique/HEAD/lib/elemop/mtimes.ts>
  - <https://raw.githubusercontent.com/NodalStudio/Ubique/HEAD/lib/linalgebra/det.ts>
  - <https://raw.githubusercontent.com/NodalStudio/Ubique/HEAD/lib/linalgebra/inv.ts>
  - <https://jsr.io/@nodalstudio/ubique/meta.json>
  - <https://jsr.io/@bemayer/rubique/meta.json>
  - <https://registry.npmjs.org/ubique>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/nodalstudio/ubique`) · [data/wave13/enrich/raw/github_com_nodalstudio_ubique.json](../../../data/wave13/enrich/raw/github_com_nodalstudio_ubique.json) (enrichment confidence 0.65)

</details>
