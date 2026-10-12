# libstats

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [SIMD intrinsics libraries](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> C++20 statistical-distributions library with runtime-dispatched SSE2/AVX/AVX2/AVX-512/NEON exp, log, erf and cos kernels that beat scalar libm loops.

| | |
|---|---|
| **Beats** | scalar loops over std::exp, std::log, std::erf and std::cos (platform libm); corvus v1.0.1 SIMD kernels on M1 as a second baseline |
| **Claimed result** | docs/SIMD_BENCHMARK_RESULTS.md 'Representative v1.5.x' primitive speedups over the scalar libm loop: AVX2+FMA VectorExp 3.4x, VectorLog 1.7x, VectorErf 2.5x, VectorCos 4.9x; NEON 2.1x, 1.8x, 8.0x, 3.0x; AVX-512 5.0x, 3.9x, 1.3x, 8.5x. Current v2.x NEON exp: 2.5-2.6x (was 2.1x) on a Mac Mini M1 after the table-gather kernel. corvus issue #43 (owner's own M1 table, ns per element at n = 1e6): libstats exp 1.0 vs corvus 4.6, log 1.7 vs 13.7, cos/sin 2.5 vs 4.1, erf 1.4 vs 2.3 (corvus later improved to exp 2.4, log 3.9, erf 1.8, cos/sin 2.6 ns). |
| **Workload** | tools/simd_verification primitive benchmark: 1,024-element double arrays (linspace inputs, exp over [-500, 500]), scalar std:: loop vs libstats VectorOps::vector_exp/log/erf/cos, 5 timed iterations after a warm-up; corvus issue #43 compares ns per element at n = 1e6 through libstats VectorOps. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-7820HQ (Kaby Lake, AVX2+FMA), Mac Mini Apple M1 (NEON) and AMD Ryzen 7 7445HS (Zen 4, AVX-512) are the validation machines; the v1.5.x primitive table does not say which machine produced which row. |
| **Compiler and flags** | Not stated for the primitive table; the doc says to use Release builds (cmake -DCMAKE_BUILD_TYPE=Release). The accuracy section mentions MSVC on the Windows Zen 4 machine and AppleClang on the Mac. |
| **Adoption** | 1 star; 715 commits; C++20 statistical-distributions library |
| **Last commit** | 2026-10-11 |
| **Links** | [repository](https://github.com/OldCrow/libstats) · [benchmark](https://github.com/OldCrow/libstats/blob/main/docs/SIMD_BENCHMARK_RESULTS.md) |

## Verdict

First-party tools/simd_verification runs (Release, 1,024 doubles, mean of 5 calls) report v1.5.x speedups over a scalar platform-libm loop of 3.4x/1.7x/2.5x/4.9x (exp/log/erf/cos, AVX2+FMA), 2.1x/1.8x/8.0x/3.0x (NEON) and 5.0x/3.9x/1.3x/8.5x (AVX-512), without saying which machine produced each row; the current NEON exp kernel measures 2.5-2.6x on a Mac Mini M1. In the author's corvus issue #43 (M1, AppleClang 21, n = 1e6) libstats v2.4.1 took 1.0/1.7/2.5/1.4 ns per element for exp/log/cos/erf against corvus 2.4/3.9/2.6/1.8 after its fixes.

## Use it when

- You evaluate densities, log-densities or CDFs of standard distributions over arrays of thousands to millions of doubles and want SIMD plus parallel dispatch without writing kernels
- You need vectorised double-precision exp/log/erf/cos at roughly 0.5-1 ULP on both x86-64 (AVX2 or AVX-512) and Apple Silicon NEON from one code base
- Batch statistical workloads replacing scipy.stats loops: the project's own N = 100k runs show 6-35x for several log-PDF and PDF paths (first-party)
- MIT-licensed code you can read and vendor kernels from: the derivation and divergence-audit documents explain each kernel's accuracy

## Skip it when

- You need correctly rounded results: the kernels are about 0.52-1 ULP; the same author's corvus keeps 0-ULP exp and log gates on NEON
- Single-precision (float) or scalar one-at-a-time calls: kernels are double-only array calls, and arrays shorter than one vector go through the scalar tail loop
- Distributions the doc lists as structural ceilings: Cauchy CDF 0.2x and von Mises CDF 0.1x of scipy on Zen 4, and Beta PDF/log-PDF lose under a parallel fork on every tier
- Streaming arrays far larger than cache: the doc's Zen 4 data show exp at 0.55 ns per element is memory-bound at 256K elements, so the 1,024-element speedups shrink
- You need a widely used dependency: one maintainer, 1 star, frequent releases (v2.4.1 current) and an open M1 throughput regression on the v2.5.0 work (issue #156)

## How it is fast

Each kernel processes 2 (NEON), 4 (AVX2) or 8 (AVX-512) doubles per instruction with FMA Horner evaluation: a SLEEF-derived 10-term polynomial exp and SLEEF xlog_u1 log on x86, a musl-derived rational erf, and a quadrant-reduction cos with a 4-part pi/2 split and degree-6 minimax cores. On NEON, exp is a 128-entry table plus order-5 polynomial derived from ARM optimized-routines (software gather via vld1q), and log and erf use clean-room table-plus-series kernels. Edge cases (overflow, infinities, |x| above 2^23 for cos) fall back to scalar std:: calls lane by lane.

## Compared with alternatives

Pick libstats over corvus (same author, standalone correctly rounded elementary functions built on Highway) when you want distribution-level batch PDF/CDF code and can accept about 1 ULP for faster NEON exp and log (1.0 vs 2.4 and 1.7 vs 3.9 ns per element on M1). Pick it over math_intrinsics or SIMD-math-prims when you need double precision with near-libm accuracy instead of float approximations.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | none required; optional TBB (Linux/Windows) or GCD (macOS) for the parallel paths |
| **Minimum toolchain** | C++20, CMake 3.25+; validated with AppleClang, MSVC, clang-cl and GCC |
| **Platforms** | x86-64 (SSE2 baseline, AVX, AVX2+FMA, AVX-512 with runtime dispatch), aarch64 NEON; Windows, macOS, Linux |
| **Thread safety** | VectorOps kernels are stateless noexcept functions; distribution objects document concurrent read access with thread-safe cache management |
| **Drop-in for the baseline** | partial — replaces a loop of std::exp/log/erf/cos with one array call, but results differ from libm by up to about 1 ULP and the kernels live in an internal arch namespace |

## Gotchas

- Harness flaw behind the v1.5.x VectorCos rows (AVX2 4.9x, NEON 3.0x, AVX-512 8.5x): those numbers were measured on cos kernels later replaced for accuracy bugs. The NEON source says the v1.4.0 Taylor kernel had about 6e8 ULP error inside [-2pi, 2pi] and sign errors near k\*pi/2 for |x| in the thousands, and issue #95 says x86 vector_cos was about 3e5 ULP. tools/simd_verification only tests [-4pi, 4pi] at a 1e-9 absolute tolerance, so it passed them. No current cos speedup over libm is published; the record's '7-term Horner cos' description is out of date.
- The NEON exp, log, erf and cos kernels were all replaced on or after 2026-07-19, so the whole v1.5.x NEON row (2.1x, 1.8x, 8.0x, 3.0x) describes earlier code; only NEON exp has a current figure (2.5-2.6x).
- Benchmark method: 1,024 cache-resident doubles, one warm-up, then the mean of 5 timed calls, scalar timed before SIMD, against whatever libm the platform ships (Apple libm, MSVC UCRT, glibc), with no compiler version in the table.
- Windows MSVC and clang-cl builds apply /arch:AVX512 or /arch:AVX2 (or -mavx512f/-mavx2) globally from the build machine unless LIBSTATS_PORTABLE=ON, so default Windows binaries are not portable to older CPUs.

## Known shortcomings

- The benchmark is a 1,024-element, 5-iteration mean with no compiler or flags and an unnamed libm; cos is looser than libm (1e-9 tolerance); the corvus baseline is a project of the same owner and is already listed.
- Enricher: the v1.5.x VectorCos rows (4.9x, 3.0x, 8.5x) were measured on cos kernels later replaced for accuracy bugs (the NEON v1.4.0 Taylor kernel had about 6e8 ULP error and sign errors near k\*pi/2, x86 about 3e5 ULP, issue #95); simd_verification tests only [-4pi, 4pi] at 1e-9 absolute tolerance, so both passed. All NEON v1.5.x kernels were replaced on 2026-07-19; only the NEON exp 2.5-2.6x is current.

## Caveats and trade-offs

Own-benchmark numbers on a tiny, cache-resident array (tools/simd_verification.cpp: TEST_SIZE 1024 doubles, one warm-up call, then the mean of TEST_ITERATIONS = 5 timed calls) with no compiler version or flags, so tier C. The v1.5.x table is labelled by the doc as historical and does not say which machine produced which row. The accuracy gap weakens the comparison: simd_verification accepts cos to 1e-9 (7-term polynomial, max error about 1e-10), so a 4.9x cos result is not like for like with libm. The libm baseline is whatever the build platform ships (MSVC UCRT, Apple libm, glibc), and glibc was not named. The corvus comparison is not independent: corvus is the same owner's (OldCrow) other project, issue #43 was opened and closed by that owner, and it compares libstats v2.4.1 against corvus v1.0.1; the owner declined to import the roughly 0.52 ULP libstats kernels into corvus because corvus exp and log keep correctly rounded (0-ULP) gates on NEON, and the issue closed on 2026-10-12 after corvus narrowed the gap (exp 2.4, log 3.9, erf 1.8, cos/sin 2.6 ns per element against libstats 1.0, 1.7, 1.4, 2.5). corvus's own PERFORMANCE document is the better reference for corvus vs libm. 1-star repository maintained by one author. [retier] Enricher: the v1.5.x VectorCos rows (4.9x, 3.0x, 8.5x) were measured on cos kernels later replaced for accuracy bugs (NEON v1.4.0 Taylor kernel about 6e8 ULP with sign errors near k\*pi/2, x86 about 3e5 ULP, issue #95); the verification tests cover only [-4pi, 4pi] at 1e-9 absolute tolerance. Only the NEON exp 2.5-2.6x row is current.

The SIMD kernels are internal to a statistical-distributions library (SSE2, AVX, AVX2, AVX-512, NEON; SLEEF-inspired exp/log, musl-style erf, a 7-term Horner cos), not a standalone libm replacement. Needs array-style batch calls. Kernel accuracy is looser than a correctly rounded libm.

## Maintenance

Actively developed (commits through 2026-10-11, v2.4.1 current release, CI and mpmath accuracy tests) and MIT-licensed, but a one-author, 1-star project whose published primitive speedups mostly predate the current kernels.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** docs/SIMD_BENCHMARK_RESULTS.md carries the v1.5.x primitive table (AVX2+FMA 3.4x/1.7x/2.5x/4.9x, NEON 2.1x/1.8x/8.0x/3.0x, AVX-512 5.0x/3.9x/1.3x/8.5x) and the NEON exp 2.1x to 2.5-2.6x row from tools/simd_verification (Release, Mac Mini M1); the benchmark code is public but the table names no compiler version, flags, or which CPU produced each v1.5.x row, so first-party tier C.
- **Verifier notes:** Record checks out: primitive speedups, NEON exp 2.5-2.6x, and corvus issue #43 numbers all match their sources; methodology is a 1,024-element, 5-iteration mean in tools/simd_verification.cpp. Shortcomings: tiny cache-resident workload, no compiler/flags, unnamed libm, looser accuracy than libm for cos, and the corvus baseline is the same author's project (corvus is already listed in wave 13).
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-127 (wave 13 seed pass, 2026-10-13); enricher (seed pass, 2026-10-13)
- **Pages the verifier opened:**
  - <https://github.com/OldCrow/libstats/blob/main/docs/SIMD_BENCHMARK_RESULTS.md>
  - <https://github.com/OldCrow/libstats>
  - <https://github.com/OldCrow/libstats/commits>
  - <https://github.com/OldCrow/libstats/blob/main/tools/simd_verification.cpp>
  - <https://github.com/OldCrow/corvus/issues/43>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/OldCrow/libstats/HEAD/README.md>
  - <https://raw.githubusercontent.com/OldCrow/libstats/HEAD/docs/SIMD_BENCHMARK_RESULTS.md>
  - <https://raw.githubusercontent.com/OldCrow/libstats/HEAD/tools/simd_verification.cpp>
  - <https://raw.githubusercontent.com/OldCrow/libstats/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/OldCrow/libstats/HEAD/cmake/CompilerFlags.cmake>
  - <https://raw.githubusercontent.com/OldCrow/libstats/HEAD/src/simd_avx2.cpp>
  - <https://raw.githubusercontent.com/OldCrow/libstats/HEAD/src/simd_neon.cpp>
  - <https://github.com/OldCrow/libstats/issues?q=is%3Aissue+cos>
  - <https://github.com/OldCrow/corvus/issues/43>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/oldcrow/libstats`) · [data/wave13/enrich/raw/github_com_oldcrow_libstats.json](../../../data/wave13/enrich/raw/github_com_oldcrow_libstats.json) (enrichment confidence 0.75)

</details>
