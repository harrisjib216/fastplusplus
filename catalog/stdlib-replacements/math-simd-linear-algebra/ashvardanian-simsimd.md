# NumKong (formerly SimSIMD)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Math, SIMD and linear algebra](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Header-only SIMD kernel library beating GCC's auto-vectorized f16 loops in dot product and distance metrics 20-118x.

| | |
|---|---|
| **Beats** | hand-written C++ dot-product/reduction loop, semantically equivalent to std::inner_product / std::transform_reduce, auto-vectorized by GCC 12 -O3 |
| **Claimed result** | f16 kernels vs GCC-12-compiled auto-vectorized f16 loop: Inner Product 31x, Cosine Distance 20x, Euclidean Distance^2 36x, Jensen-Shannon Divergence 118x |
| **Workload** | Half-precision (f16) inner product, cosine distance, squared Euclidean distance, and Jensen-Shannon divergence over vectors, single-threaded, on Intel Sapphire Rapids |
| **Metric** | throughput |
| **Hardware** | Intel Sapphire Rapids (blog: 2022-generation AWS 4-core instance; exact SKU not stated), single-threaded |
| **Compiler and flags** | GCC 12; README gives no flags, but the author's blog post (ashvardanian.com/posts/gcc-12-vs-avx512fp16) says -O3 -march=native -ffast-math |
| **Adoption** | 1.9k stars |
| **Last commit** | 2026-09-01 |
| **Links** | [repository](https://github.com/ashvardanian/SimSIMD) · [benchmark](https://github.com/ashvardanian/SimSIMD/blob/main/README.md) |

## Verdict

On Intel Sapphire Rapids, single-threaded, NumKong's f16 kernels beat a scalar f16 loop auto-vectorized by GCC 12 (-O3 -march=native -ffast-math per the author's blog; flags not stated in the README itself) by 31x (inner product), 20x (cosine distance), 36x (squared Euclidean distance), and 118x (Jensen-Shannon divergence), per the README's first-party 'Auto-Vectorization & Loop Unrolling' table. This is not a benchmark against a literal std::inner_product/std::transform_reduce call.

## Use it when

- Single- or half-precision (f16/bf16/e4m3) dot product, cosine distance, squared Euclidean, or Jensen-Shannon divergence over vectors, where GCC/Clang auto-vectorization of a scalar loop is the realistic alternative
- Need mixed-precision accumulation (f16-&gt;f32, i8-&gt;i32) to avoid the silent overflow a naive same-type reduction would hit
- Cross-platform kernels wanted from one header-only source: x86 (AVX2/AVX-512), Arm (NEON/SVE), RISC-V, WASM
- Caller already manages its own threading and wants a numerics layer with no hidden thread pool
- Small binary footprint matters (Python wheels, npm, Rust crates) versus linking a full BLAS

## Skip it when

- Need a literal drop-in for std::inner_product/std::transform_reduce call sites — the API differs and requires rewriting
- f32-only workloads on GCC: GCC already auto-vectorizes plain float loops reasonably well (3,810 K/s in the README's own f32 row), so the large multipliers shown are f16-specific, not universal
- Trigonometric/element-wise kernels (sin/cos/atan): the README only benchmarks those against NumKong's own scalar reimplementation, not against std::sin/cos, so no verified std:: comparison exists for that portion
- Extreme-magnitude inputs through the serial fallback path: open bug (#384) shows nk_euclidean_f64_serial returns 0 after fp64 overflow
- Need C++ exceptions for error handling: the library passes by pointer and does not throw

## How it is fast

Runtime CPU-feature dispatch selects a kernel per architecture (AVX-512-FP16, F16C, SVE, VNNI, AMX/SME) instead of relying on the compiler to auto-vectorize a scalar loop, and low-precision types get algorithmic transforms (lookup tables, algebraic domain shifts, widened-accumulator FMA) that scalar auto-vectorization does not synthesize. Masked loads (e.g. _mm512_maskz_loadu_ps, svld1_f32) replace the usual unrolled-body-plus-scalar-tail pattern, so remainder elements run the same arithmetic path as the SIMD body. The library deliberately avoids source-level loop unrolling, leaning on out-of-order execution and register renaming instead, to control binary size and compile time across 1,500+ kernel endpoints.

## Compared with alternatives

Pick NumKong over the trig-focused siblings (SLEEF, FABE13-HX, fmath, VDT, fast_math_cpp, trigno_simd_cpp) when the workload is dot-product/distance/reduction linear algebra rather than elementwise transcendental functions, since those all target std::sin/cos/exp/log while NumKong's verified numbers here cover inner product, cosine distance, squared Euclidean, and JS divergence. Pick Axiom or LibRapid instead when a tensor/array-expression API is wanted rather than a flat kernel-call API.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none for the core C/C++ headers; pthreads (via CMake's Threads package) for optional threading helpers |
| **Minimum toolchain** | C++20 for the C++ layer, C99 for the C layer (include/README.md); CMake for prebuilt/shared-lib builds |
| **Platforms** | x86-64 (SSE/AVX2/AVX-512/F16C/VNNI), Arm (NEON/SVE, AMX/SME on supporting chips), RISC-V, LoongArch, Power, WebAssembly; Linux, macOS, Windows, Android for the C/C++ package |
| **Thread safety** | No hidden thread pool; the library does not own threads. nk_configure_thread() must be called once per thread before using AMX-accelerated ops. Designed to compose with caller-managed std::thread, ForkUnion, or any external scheduler (README 'Threading Model' / 'Parallelism & Multi-Threading'). |
| **Drop-in for the baseline** | false — different function surface (nk_\* C functions / C++ template wrappers), not call-compatible with std::inner_product/std::transform_reduce |

## Gotchas

- Open bug: nk_euclidean_f64_serial returns 0 instead of the correct distance after fp64 overflow on extreme-magnitude inputs (issue #384, reproduced on v7.8.2)
- macOS arm64 Python wheel reported loading a second libomp runtime and crashing alongside PyTorch (issue #373), despite the core README's 'no hidden thread pool' claim — appears tied to an optional/bundled component, not the header-only C++ core
- nk.moments reported \~30x slower on N-D arrays than on a flattened 1D view of the same data (issue #336) — memory layout matters for the reduction kernels
- No exceptions: errors are communicated by return value/pointer, not C++ exceptions

## Caveats and trade-offs

Baseline is GCC-12 auto-vectorized scalar C loops (built with -ffast-math per the author's blog), not a literal std:: facility call. Exact CPU SKU not given, and the README table does not name the benchmark code, so tier stays C. The 118x JS-divergence figure matches the blog's 118.84x (avx512_f16 vs serial_f16 at 1536d, where the serial baseline calls libc logf). The repo was renamed from SimSIMD to NumKong, and github.com/ashvardanian/SimSIMD now redirects to ashvardanian/NumKong. [retier] Baseline is GCC-12 auto-vectorized scalar C loops (built with -ffast-math per the author's blog), not a literal std:: facility call. Exact CPU SKU not given (Intel Sapphire Rapids, single-threaded), and the README table does not name the benchmark code, so tier stays C. The 118x JS-divergence figure matches the blog's 118.84x (avx512_f16 vs serial_f16 at 1536d, where the serial baseline calls libc logf). The repo was renamed from SimSIMD to NumKong (github.com/ashvardanian/SimSIMD redirects). The NumKong README also publishes first-party library tables (NumPy 2.4 + OpenBLAS, PyTorch 2.10 + MKL, JAX 0.9): dot product 2048-d f32 7.1 gso/s vs NumPy 1.5, PyTorch 0.6 and JAX 0.4; f64 5.8 vs 2.0; f16 11.5 vs NumPy 0.2 and PyTorch 0.5; i8 14.8 vs NumPy 1.1 (overflowing); matmul 2048x2048 i8 1279 gso/s vs PyTorch+MKL 50.0 and e5m2 398 vs 0.4, but it is slower on f64 (8.6 vs 65.5 NumPy+OpenBLAS and 68.2 PyTorch+MKL), f32 (37.7 vs 140 and 145) and bf16 (458 vs 851 PyTorch); no flags and no exact CPU model for those tables either.

The comparison baseline is GCC's auto-vectorization of a plain scalar loop written in the project's own bench harness, not literally a call through &lt;numeric&gt;'s std::transform_reduce/std::inner_product, so the baseline match is inferred rather than exact; library trades a very large API surface (2000+ kernels across 15+ numeric types) and wider mixed-precision accumulators for speed; repo also publishes a much larger benchmark table for its element-wise trigonometric kernels (sin/cos/atan), but those are only benchmarked against the project's own non-SIMD 'serial' reimplementation of the same SLEEF-derived algorithm rather than against std::sin/cos/&lt;cmath&gt;, so that portion was deliberately excluded from this entry

## Maintenance

Actively maintained (default-branch HEAD commit 2026-09-01, \~1,894 stars, not archived) and Apache-2.0 licensed; the header-only C/C++ core is copyable/vendorable on its own. The project renamed from SimSIMD to NumKong, and github.com/ashvardanian/SimSIMD now redirects to github.com/ashvardanian/NumKong.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** README section 'Auto-Vectorization & Loop Unrolling' has a first-party table (GCC 12 f32 / GCC 12 f16 / NumKong f16) with 31x/20x/36x/118x f16 improvements on Sapphire Rapids; exact CPU SKU not given, and the README does not state flags or link the benchmark code for this table. Flags (-O3 -march=native -ffast-math) appear only in the author's blog post, so it cannot reach A. First-party, so C.
- **Verifier notes:** The numbers match the README table verbatim. The repo now resolves to ashvardanian/NumKong (Apache-2.0, 1,893 stars, not archived). The default-branch head is 2026-09-01; pushed_at 2026-09-23 is from a non-default branch. The orchestrator may want repo_url updated to the NumKong URL.
- **Fields the verifier corrected:** `last_commit`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/ashvardanian/SimSIMD/blob/main/README.md>
  - <https://github.com/ashvardanian/SimSIMD>
  - <https://github.com/ashvardanian/NumKong>
  - <https://github.com/ashvardanian/NumKong/blob/main/bench/bench_cross_serial.cpp>
  - <https://ashvardanian.com/posts/gcc-12-vs-avx512fp16/>
- **Sources the enricher read:**
  - <https://github.com/ashvardanian/NumKong>
  - <https://github.com/ashvardanian/NumKong/blob/main/README.md>
  - <https://github.com/ashvardanian/NumKong/blob/main/include/README.md>
  - <https://github.com/ashvardanian/NumKong/issues/384>
  - <https://github.com/ashvardanian/NumKong/issues/356>
  - <https://github.com/ashvardanian/NumKong/issues/358>
  - <https://github.com/ashvardanian/NumKong/issues/360>
  - <https://github.com/ashvardanian/NumKong/issues/373>
  - <https://github.com/ashvardanian/NumKong/issues/371>
  - <https://github.com/ashvardanian/NumKong/issues/333>
  - <https://github.com/ashvardanian/NumKong/issues/336>
  - <https://github.com/ashvardanian/NumKong/commits/main>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/ashvardanian/simsimd`) · [data/wave1/enrich/raw/github_com_ashvardanian_simsimd.json](../../../data/wave1/enrich/raw/github_com_ashvardanian_simsimd.json) (enrichment confidence 0.65)

</details>
