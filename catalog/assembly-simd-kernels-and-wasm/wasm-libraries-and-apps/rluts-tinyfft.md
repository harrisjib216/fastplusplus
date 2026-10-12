# tinyfft (rluts/tinyfft)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly libraries and apps](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟢 active

> no_std Rust radix-4 FFT shipped as 16 KB SIMD wasm; 1.2-1.4x fft.js complex-FFT throughput in Node.

| | |
|---|---|
| **Beats** | fft.js (pure JavaScript, f64) |
| **Claimed result** | Round trip with persistent plans (bench/README.md sample run, Apple Silicon, Node 25): tinyfft SIMD \~124 vs fft.js \~97 MSamples/s at N=1024 (\~1.28x) and \~79 vs \~57 at N=65536 (\~1.39x); forward \~250 vs \~207 at N=1024 (\~1.21x) and \~159 vs \~115 at N=65536 (\~1.38x), but \~262 vs \~258 at N=256 (a tie); ratios derived from page data. The scalar build (\~91 and \~43 MSamples/s round trip) is slower than fft.js at both sizes. |
| **Workload** | 1D complex FFT round trip throughput at N=1024 and N=65536 with persistent plans, SIMD and scalar wasm builds against fft.js. |
| **Metric** | throughput |
| **Hardware** | Apple Silicon (chip not stated), Node 25 |
| **Compiler and flags** | Rust (version not stated) for wasm32-unknown-unknown with -C target-feature=+simd128 (.cargo/config.toml); release profile opt-level=3, lto=true, codegen-units=1, panic=abort; wasm-opt -O3; scalar variant built with -C target-feature=-simd128 (bench/build-scalar.mjs); bench/run.mjs with 150 ms warmup and 500 ms measurement; Node 25 |
| **Adoption** | 1 star |
| **Last commit** | 2026-07-26 |
| **Links** | [repository](https://github.com/rluts/tinyfft) · [benchmark](https://github.com/rluts/tinyfft#benchmarks) |

## Verdict

First-party sample run of bench/run.mjs on Node 25 and an unnamed Apple Silicon machine; the Rust version is not stated (release profile opt-level 3, LTO, codegen-units 1, wasm-opt -O3). With persistent plans, the simd128 build did \~124 vs \~97 MSamples/s complex round trip at N=1024 and \~79 vs \~57 at N=65536 against fft.js 4.x (pure JS, f64). Forward was \~250 vs \~207 at N=1024 and \~262 vs \~258 (a tie) at N=256. The scalar wasm build lost to fft.js at every size. Ratios are derived from page data.

## Use it when

- Repeated same-size complex FFTs that reuse one plan (STFT, spectrograms, FFT convolution or overlap-add) in a browser, Node or Deno, at N of about 1024 to 65536, where the sample run measured 1.2-1.4x over fft.js
- Workloads where f32 precision is enough: audio analysis, visualisation, image filtering
- When bundle size and dependencies matter: one \~16 KB wasm with no runtime dependencies and the same code path in every engine
- Small 2D transforms (up to about 512x512 with the default 8 MiB arena) for frequency-domain image filtering, if convenience matters more than speed (the 2D path is not plan-cached or benchmarked)

## Skip it when

- You need double precision or high dynamic range: f32 only, and the README gives round-trip relative error of about 1e-4 to 1e-3 (fft.js is f64, \~1e-14)
- Real-valued input such as audio frames: there is no real-to-complex transform, while fft.js's realTransform is claimed 25-40% faster than its complex transform, which could erase the 1.2-1.4x margin (not measured by the project)
- Non-power-of-two lengths, or N above 2^18: plans are bump-allocated from a fixed 8 MiB arena at about 28 bytes per point, so larger sizes need ARENA_BYTES edited and a rebuild
- Runtimes without wasm SIMD: only the simd128 build ships on npm, and the bench-only scalar build is slower than fft.js at every size
- Small transforms (N=256 forward was a tie, \~262 vs \~258 MSamples/s) or one-shot calls, which rebuild the cos/sin and permutation tables on every call

## How it is fast

It runs an iterative Cooley-Tukey radix-4 FFT, with one leading radix-2 stage when log2 N is odd, on a planar (split real/imag) layout. Each wasm simd128 step does four consecutive butterflies with contiguous v128 loads and stores and vertical f32x4 complex multiplies, with no shuffles. plan1d precomputes the all-stage twiddle table and the base-4 digit-reversal map once and folds the permutation into the de-interleave gather, so a transform costs one gather, the butterfly stages and one re-interleave. Working in f32 also moves half the bytes of fft.js's f64 arrays, which helps most at N=65536.

## Compared with alternatives

No other FFT is catalogued in this wasm category. Essentia.js includes FFTs inside a large audio-analysis toolkit, and Ubique (nalgebra in wasm) targets linear algebra, so pick tinyfft when you only need a small power-of-two f32 complex FFT. For f64 or arbitrary lengths, compile RustFFT (wave 8 fft entry, optional wasm SIMD) to wasm yourself.

## Integration

| | |
|---|---|
| **Form** | module (npm package: ESM JS wrapper + raw .wasm); the repo is also a no_std Rust crate (cdylib/rlib) |
| **Dependencies** | none at runtime; the Rust build uses the libm crate; binaryen wasm-opt is optional |
| **Minimum toolchain** | Node &gt;= 18 (package.json engines); building needs Rust with the wasm32-unknown-unknown target (version not documented; the source uses &raw mut, stable since Rust 1.82); the runtime needs wasm simd128 |
| **Platforms** | any WebAssembly engine with simd128 (browsers, Node, Deno, edge runtimes per README); the SIMD kernel exists only for wasm32, and host Rust builds use the scalar path |
| **Thread safety** | Not thread-safe within one instance: a single static mut bump arena per wasm instance, documented single-threaded; load a separate TinyFft instance per worker |
| **Drop-in for the baseline** | no |

## Gotchas

- Plans live in a fixed 8 MiB bump arena per instance: fft.reset() invalidates every existing plan and view, and mark()/release() frees only in LIFO order. plan2d does not cache tables: fft_2d_in_place calls the one-shot fft_in_place for every row and column, rebuilding the twiddle and permutation tables each time, so 2D throughput will not match the 1D plan numbers.
- Robustness bug in src/lib.rs: total_twiddle_len (also used by fft_in_place) shifts `size <<= 2` on 32-bit wasm usize. For n = 2^30 or 2^31 the shift wraps to 0, so `while size <= n` never ends. The TypeScript isPow2 check lets those sizes through, so plan1d(2\*\*30) hangs instead of throwing an arena error. Sizes that fit the arena are not affected. plan1d(1) throws a misleading 'fft_plan_create failed ... (arena ...)' error because the plan path rejects n &lt; 2.
- Harness review (bench/run.mjs): the forward rows re-seed tinyfft's buffer with a 2N-float copy each iteration and fft.js pays nothing similar, which biases against tinyfft. The round-trip rows are copy-free on both sides. fft.js is called through its documented complex transform() on plain Arrays. Correctness is checked against a naive DFT at N=256 before timing. I found no flaw that inflates tinyfft's numbers. The remaining caveats: f32 against f64, one sample run of 500 ms per cell with no repeats or variance, and an unnamed Apple Silicon chip.
- The Rust unit tests run only on the host (scalar path); the SIMD kernel is exercised only by the Node smoke test (N=16), vitest and the benchmark's N=256 check.

## Known shortcomings

- Modest 1.2-1.4x, f32 against f64 fft.js, the only comparator; N=256 forward is a tie and the scalar build loses; chip unstated.
- Harness sound, no inflation: the round trip is copy-free on both sides, the re-seed copy in the forward rows hurts tinyfft only, and output is checked against a naive DFT at N = 256. Caveats: f32 vs f64, one sample run, chip unnamed, no real-input FFT (fft.js realTransform claims 25-40% faster). Bug in src/lib.rs: total_twiddle_len's 'size &lt;&lt;= 2' wraps on a 32-bit usize, so plan1d(2\*\*30) or plan1d(2\*\*31) loops forever; plan2d is not plan-cached (rebuilds cos/sin per row) and 2D is not benchmarked; the 8 MiB arena caps a 1D plan at N = 2^18.

## Caveats and trade-offs

First-party sample run on one unnamed Apple Silicon machine; modest gains (about 1.2-1.4x, a tie at N=256 forward). tinyfft is f32 while fft.js is f64 (round-trip error \~1e-7 vs \~1e-14), so precision differs; the bench README says so. Only fft.js is benchmarked although the bench describes 'popular JS/WASM FFT libraries'; no other wasm FFT (for example a pffft or KissFFT wasm build) is compared. The forward loop includes a 2N-float re-seed copy for tinyfft that fft.js does not pay. The scalar wasm build loses to fft.js, so the win depends on wasm SIMD. The live browser benchmark is on rluts.github.io (blocked here, not opened). 1 star, created mid-2026.

Single-precision f32 only, in-place, planar real/imag layout (helpers interleave/magnitudes provided); \~16 KB wasm. Unrelated to the older C tinyfft already catalogued.

## Maintenance

Young single-author project, active: 28 commits, last on 2026-07-26, npm 0.2.1 (first published 2026-05-08), 1 star, no issues filed. It is MIT and about 1,150 lines of Rust including tests, so it is easy to vendor. The benchmark harness is sound; its biases (f32 against f64, a re-seed copy on tinyfft's side only) are documented in bench/README.md. It has a minor hang bug for plan sizes 2^30 and 2^31.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party sample run in README.md and bench/README.md (round-trip N=1024 \~124 vs \~97, N=65536 \~79 vs \~57 MSamples/s against fft.js) with public bench code (bench/run.mjs) and public build flags, but the hardware is only 'Apple Silicon' and the rustc version is not stated, so not A.
- **Verifier notes:** Numbers match README and bench/README.md; bench/run.mjs verifies both backends against a naive DFT at N=256 before timing and the round-trip loop is copy-free on both sides, so the evidence is valid but modest. Metadata confirmed: MIT, 1 star, last commit 2026-07-26.
- **Fields the verifier corrected:** `compiler_and_flags`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-88 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/rluts/tinyfft>
  - <https://github.com/rluts/tinyfft/commits>
  - <https://raw.githubusercontent.com/rluts/tinyfft/HEAD/README.md>
  - <https://raw.githubusercontent.com/rluts/tinyfft/HEAD/bench/README.md>
  - <https://raw.githubusercontent.com/rluts/tinyfft/HEAD/bench/run.mjs>
  - <https://raw.githubusercontent.com/rluts/tinyfft/HEAD/bench/package.json>
  - <https://raw.githubusercontent.com/rluts/tinyfft/HEAD/package.json>
  - <https://raw.githubusercontent.com/rluts/tinyfft/HEAD/.cargo/config.toml>
  - <https://raw.githubusercontent.com/rluts/tinyfft/HEAD/Cargo.toml>
- **Sources the enricher read:**
  - <https://github.com/rluts/tinyfft>
  - <https://github.com/rluts/tinyfft/tree/main/src>
  - <https://github.com/rluts/tinyfft/commits>
  - <https://github.com/rluts/tinyfft/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/rluts/tinyfft/HEAD/README.md>
  - <https://raw.githubusercontent.com/rluts/tinyfft/HEAD/bench/README.md>
  - <https://raw.githubusercontent.com/rluts/tinyfft/HEAD/bench/run.mjs>
  - <https://raw.githubusercontent.com/rluts/tinyfft/HEAD/bench/build-scalar.mjs>
  - <https://raw.githubusercontent.com/rluts/tinyfft/HEAD/bench/package.json>
  - <https://raw.githubusercontent.com/rluts/tinyfft/HEAD/package.json>
  - <https://raw.githubusercontent.com/rluts/tinyfft/HEAD/.cargo/config.toml>
  - <https://raw.githubusercontent.com/rluts/tinyfft/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/rluts/tinyfft/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/rluts/tinyfft/HEAD/ts/index.ts>
  - <https://raw.githubusercontent.com/rluts/tinyfft/HEAD/ts/build.mjs>
  - <https://raw.githubusercontent.com/rluts/tinyfft/HEAD/ts/smoke-test.mjs>
  - <https://raw.githubusercontent.com/rluts/tinyfft/HEAD/.github/workflows/ci.yml>
  - <https://registry.npmjs.org/tinyfft>
  - <https://github.com/indutny/fft.js>
  - <https://github.com/JorenSix/pffft.wasm>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/rluts/tinyfft`) · [data/wave13/enrich/raw/github_com_rluts_tinyfft.json](../../../data/wave13/enrich/raw/github_com_rluts_tinyfft.json) (enrichment confidence 0.8)

</details>
