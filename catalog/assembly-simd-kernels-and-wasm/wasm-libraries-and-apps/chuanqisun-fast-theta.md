# fast-theta

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly libraries and apps](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `WebAssembly text (WAT), TypeScript` · `MIT` · 🟢 active

> Tiny npm package: hand-written WAT f32x4 SIMD dot product and cosine similarity, faster than JS cosine libraries on Float32Array input.

| | |
|---|---|
| **Beats** | cos-similarity, fast-cosine-similarity and compute-cosine-similarity (JavaScript npm packages) |
| **Claimed result** | README row 'fast-theta (pre-normalized)', a bare dot product, vs full cosine similarity in the JS libraries. 384 dims: 3.3M ops/s vs cos-similarity 1.8M (1.8x), fast-cosine-similarity 1.4M (2.4x), compute-cosine-similarity 503K (6.6x). 768 dims: 2.6M vs 1.1M, 847K, 260K. 1536 dims: 1.8M vs 597K (3.0x), 414K (4.3x), 134K (13x) (ratios derived from page data). The like-for-like 'fast-theta (with normalize)' row is measured by the repo's bench but not published. |
| **Workload** | Similarity of two random vectors at 384, 768 and 1536 dimensions in Node.js via vitest bench (src/__tests__/cosine.bench.ts); fast-theta gets Float32Array inputs (copied into wasm memory each call), the JS libraries get number[] arrays. The browser page bench/index.html compares only against an inline JS cosine function, not the npm libraries. |
| **Metric** | throughput |
| **Compiler and flags** | Hand-written WAT compiled with the repo's compile-wat step; f32x4 SIMD, 4x unrolled with independent accumulators |
| **Adoption** | 1 star; npm package fast-theta |
| **Last commit** | 2026-02-27 |
| **Links** | [repository](https://github.com/chuanqisun/fast-theta) · [benchmark](https://github.com/chuanqisun/fast-theta) |

## Verdict

The README reports vitest bench numbers in Node on an unstated CPU and Node version: fast-theta's dot-only path on pre-normalized Float32Array reached 3.3M/2.6M/1.8M ops/s at 384/768/1536 dims, against 1.8M/1.1M/597K for cos-similarity 2.0.0 and slower figures for fast-cosine-similarity 1.2.2 and compute-cosine-similarity 1.1.0, all computing full cosine on number[] input. Re-running the published 0.2.0 package on Node 22.22.0 (Intel Xeon 2.10 GHz cloud vCPU, isolated process per row, best of 5) reproduced the shape: 4.29M vs cos-similarity 2.25M at 384 dims and 2.47M vs 0.51M at 1536. The like-for-like {normalize: true} row was 1.3x and 2.2x faster, a plain JS dot product on the same pre-normalized Float32Array reached 2.06-2.92M and 0.62-0.72M ops/s, and number[] input made fast-theta 7-20x slower than the baselines (numbers measured in this enrichment, not by the project).

## Use it when

- Brute-force similarity over embedding vectors (384 to 1536 dims and up) kept as Float32Array and normalized once at insert time, where each query is many dot products.
- Browser or Node code that wants WASM SIMD speed without a build step or native addon; the whole package is a 2.4 KB ESM file plus a UMD build.
- Larger dimensions: in this enrichment's Node 22 runs the dot-only path was 3.3-4x faster than a plain JS dot-product loop at 1536 dims, but only 1.5-2x at 384 dims.

## Skip it when

- Inputs held as plain number[] arrays: each call converts them with new Float32Array(...), and in this enrichment that made getSimilarity 7-20x slower than cos-similarity on the same number[] input (0.11M vs 2.25M ops/s at 384 dims, 0.07M vs 0.51M at 1536), the opposite of the README claim.
- Code that feeds the result to Math.acos to get an angle (the package's name): f32 rounding returned self-similarities above 1 (up to 1.00000036) for 594 of 2,000 normalized random vectors, which gives NaN unless you clamp.
- Callers that need f64 accuracy or validation: the JS baselines accumulate in doubles and two of them check types and lengths; fast-theta returns f32 and does neither.
- Runtimes without WebAssembly SIMD (older Safari before 16.4, old Node): there is no scalar fallback, so module instantiation fails.
- Large-scale k-NN search: it compares one pair per call with a JS-to-WASM copy each time; a batched or indexed vector library avoids the per-call copy (the author points to Eigen DB for kNN).

## How it is fast

The kernel is about 200 lines of hand-written WebAssembly text using 128-bit f32x4 multiply and add, unrolled 4x with four independent accumulators (16 floats per iteration) and a scalar tail, embedded as a sub-1 KB base64 module. Pre-normalizing once lets each comparison be a single dot-product pass instead of the three running sums a cosine needs. Each call still copies both vectors into a module-global WebAssembly.Memory with Float32Array.set, so the README's 'zero-copy' wording is inaccurate.

## Compared with alternatives

Like kmeans-wasm (wasm k-means vs skmeans) and hash-wasm (wasm hashing vs pure-JS hash libraries), it replaces a pure-JS npm numeric routine with WASM; pick fast-theta only for single-pair cosine or dot products on Float32Array embeddings, where it is the smallest option (under 1 KB of WASM, no dependencies).

## Integration

| | |
|---|---|
| **Form** | npm module (ESM and UMD builds with the WASM inlined as base64) |
| **Dependencies** | none at runtime |
| **Minimum toolchain** | Any JS runtime with WebAssembly SIMD (fixed-width 128-bit) support, e.g. Node 16.4+, Chrome 91+, Firefox 89+, Safari 16.4+; building from source needs wabt and vite |
| **Platforms** | any WebAssembly-SIMD-capable browser or Node.js |
| **Thread safety** | Module-global WebAssembly memory reused by every call; safe in single-threaded JS, so each worker gets its own instance |
| **Drop-in for the baseline** | partial — getSimilarity(a, b, {normalize: true}) gives a cosine similarity like cos-similarity(a, b), but in f32, with no length check and a different signature; the default call is only a dot product |

## Gotchas

- Mismatched lengths fail silently or throw, depending on order: dims comes from the first vector, so after an earlier call with longer vectors, getSimilarity(ones(8), ones(4)) returned 8 in this enrichment (stale wasm memory filled the missing half; zero-padding would give 4), while getSimilarity(ones(4), ones(8)) throws 'RangeError: offset is out of bounds'.
- The README headline row is the dot-only path on pre-normalized Float32Array input, compared with full cosine similarity in the JS libraries on number[] input. The fair 'with normalize' row is in the repo's bench but missing from the README; in this enrichment it was 1.3x cos-similarity at 384 dims (2.89M vs 2.25M ops/s) and 2.2x at 1536 (1.13M vs 0.51M).
- A zero vector is left unnormalized and gives similarity 0 rather than NaN or an error; fast-cosine-similarity throws ZeroVectorError in the same case.
- Most of the code was written by GitHub Copilot agent PRs (#1 for the core library, #2 for number[] support) over two days in February 2026; there is no LICENSE file in the repo, only "license": "MIT" in package.json and on npm.

## Known shortcomings

- The published row is a bare dot product (f32) while the baselines compute a full cosine (f64); the repo bench also times a fair "with normalize" row that the README leaves out; 1 star, MIT only in package.json.
- Enricher (ran npm 0.2.0 on Node 22.22.0, Xeon 2.10 GHz vCPU): the fair {normalize:true} row is only 1.3x over cosine similarity at 384 dims and 2.2x at 1536; number[] input is 7-20x slower than the baselines (0.11M vs 2.25M ops/s at 384); self-similarity exceeds 1 for 594 of 2,000 vectors so acos gives NaN; mismatched lengths read stale wasm memory (ones(8) dot ones(4) = 8) or throw RangeError; the 'zero-copy' claim is false; code mostly from Copilot PRs.

## Caveats and trade-offs

The headline row measures a bare dot product on pre-normalized vectors, while the JS libraries compute a full cosine similarity including both norms, so the comparison is not like for like; the repo's own bench also times 'fast-theta (with normalize)', the fair row, but the README omits it. fast-theta accumulates in f32 while the JS libraries use f64 doubles, so results differ in precision. No CPU, browser or Node version stated; baseline versions appear only as devDependency ranges (compute-cosine-similarity ^1.1.0, cos-similarity ^2.0.0, fast-cosine-similarity ^1.2.2) plus the lockfile. Licence MIT is declared in package.json and on npm (0.2.0) but the repo has no LICENSE file. 1 star, 25 commits.

Needs WebAssembly SIMD. Vectors must be normalized first (normalize() call) for the headline number. Wasm binary under 1 KB embedded as base64.

## Maintenance

Small single-author npm package (0.2.0, published 2026-02-27; 25 commits, 1 star, no activity since): MIT per package.json, small enough to copy as one WAT file, and correct for equal-length Float32Array inputs, but treat it as a Float32Array-only helper.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The README Performance table carries every claimed number; the benchmark code is public (src/__tests__/cosine.bench.ts, vitest bench) but no CPU, Node or browser version is stated, so first-party C.
- **Verifier notes:** Numbers match the README; the benchmark is real but the published row is dot-product-only against full-cosine baselines (normalisation work skipped), f32 vs f64, and the fair 'with normalize' result is withheld. Low notability (1 star). Last commit 2026-02-27 (branch master), MIT via package.json only, not a fork.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-105 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/chuanqisun/fast-theta/HEAD/README.md>
  - <https://raw.githubusercontent.com/chuanqisun/fast-theta/HEAD/package.json>
  - <https://raw.githubusercontent.com/chuanqisun/fast-theta/HEAD/LICENSE>
  - <https://github.com/chuanqisun/fast-theta>
  - <https://github.com/chuanqisun/fast-theta/commits>
  - <https://github.com/chuanqisun/fast-theta/tree/master/bench>
  - <https://github.com/chuanqisun/fast-theta/tree/master/src>
  - <https://github.com/chuanqisun/fast-theta/tree/master/src/__tests__>
  - <https://raw.githubusercontent.com/chuanqisun/fast-theta/master/bench/index.html>
  - <https://raw.githubusercontent.com/chuanqisun/fast-theta/master/src/index.ts>
  - <https://raw.githubusercontent.com/chuanqisun/fast-theta/master/src/cosine.wat>
  - <https://raw.githubusercontent.com/chuanqisun/fast-theta/master/vitest.config.ts>
  - <https://raw.githubusercontent.com/chuanqisun/fast-theta/master/CHANGELOG.md>
  - <https://raw.githubusercontent.com/chuanqisun/fast-theta/master/src/__tests__/cosine.bench.ts>
  - <https://registry.npmjs.org/fast-theta>
- **Sources the enricher read:**
  - <https://github.com/chuanqisun/fast-theta>
  - <https://github.com/chuanqisun/fast-theta/commits/master>
  - <https://raw.githubusercontent.com/chuanqisun/fast-theta/master/README.md>
  - <https://raw.githubusercontent.com/chuanqisun/fast-theta/master/package.json>
  - <https://raw.githubusercontent.com/chuanqisun/fast-theta/master/package-lock.json>
  - <https://raw.githubusercontent.com/chuanqisun/fast-theta/master/LICENSE>
  - <https://raw.githubusercontent.com/chuanqisun/fast-theta/master/src/index.ts>
  - <https://raw.githubusercontent.com/chuanqisun/fast-theta/master/src/cosine.wat>
  - <https://raw.githubusercontent.com/chuanqisun/fast-theta/master/src/__tests__/cosine.bench.ts>
  - <https://raw.githubusercontent.com/chuanqisun/fast-theta/master/bench/index.html>
  - <https://raw.githubusercontent.com/chuanqisun/fast-theta/master/vitest.config.ts>
  - <https://raw.githubusercontent.com/chuanqisun/fast-theta/master/CHANGELOG.md>
  - <https://raw.githubusercontent.com/chuanqisun/fast-theta/master/tsconfig.json>
  - <https://registry.npmjs.org/fast-theta>
  - <https://registry.npmjs.org/fast-theta/-/fast-theta-0.2.0.tgz>
  - <https://registry.npmjs.org/cos-similarity/-/cos-similarity-2.0.0.tgz>
  - <https://registry.npmjs.org/fast-cosine-similarity/-/fast-cosine-similarity-1.2.2.tgz>
  - <https://registry.npmjs.org/compute-cosine-similarity/-/compute-cosine-similarity-1.1.0.tgz>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/chuanqisun/fast-theta`) · [data/wave13/enrich/raw/github_com_chuanqisun_fast_theta.json](../../../data/wave13/enrich/raw/github_com_chuanqisun_fast_theta.json) (enrichment confidence 0.8)

</details>
