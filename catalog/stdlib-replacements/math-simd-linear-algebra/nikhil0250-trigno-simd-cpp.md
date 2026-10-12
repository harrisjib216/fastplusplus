# trigno_simd_cpp (SIMD trigonometric approximations, Goyal & Arora)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Math, SIMD and linear algebra](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Piecewise rational sin/cos/tan approximation using AVX2 FMA plus a fast inverse-sqrt hack; beats scalar libm sin/cos/tan.

| | |
|---|---|
| **Beats** | &lt;cmath&gt; std::sin, std::cos, std::tan |
| **Claimed result** | Mean speed-up ratio (std_time/observed_time) vs inbuilt: sin 5.49x, cos 5.52x, tan 4.44x |
| **Workload** | 1000 random double-precision angles in [-1e6, 1e6] (fixed seed 2024873), each evaluated 1e5 times; wall-clock execution time of proposed piecewise SIMD sin/cos/tan vs inbuilt C++ std::sin/cos/tan |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 5900HX (8 cores/16 threads, 3301 MHz max as reported), 2x16 GB (32 GB) DDR 3200 MHz, Windows 10 Home Single Language 64-bit |
| **Compiler and flags** | g++ -std=c++17 -mavx2 -mfma -O3 -march=native |
| **Adoption** | 7 stars |
| **Last commit** | 2026-01-29 |
| **Links** | [repository](https://github.com/Nikhil0250/trigno_simd_cpp) · [benchmark](https://arxiv.org/pdf/2502.10831) |

## Verdict

arXiv 2502.10831 (Goyal & Arora) measured mean speed-up vs 'inbuilt' std::sin/cos/tan of 5.49x/5.52x/4.44x over 1000 random angles in [-1e6, 1e6] (seed 2024873), each called 1e5 times through a function pointer, built with g++ -std=c++17 -mavx2 -mfma -O3 -march=native on an AMD Ryzen 9 5900HX under Windows/MinGW-w64. This is scalar per-call latency against the MinGW CRT libm, not glibc, and not array/batch throughput.

## Use it when

- Scalar sin/cos/tan calls where \~3-4 significant digits (max rel error \~0.004; tan max abs error 0.27 near asymptotes) is acceptable, e.g. graphics, audio, game logic, DSP.
- x86-64 targets with AVX2+FMA, or FPGA/HLS synthesis (vitis_hls_code/ ships Vitis HLS variants of the same algorithm).
- Call sites currently latency-bound on libm sin/cos/tan, willing to trade IEEE correctness for \~4.4-5.5x fewer cycles per call.
- OK vendoring a handful of .h/.cpp files directly, since there is no packaged library to link.

## Skip it when

- Need IEEE-correctly-rounded or tightly error-bounded trig (scientific/numeric code checked against std::sin/cos/tan).
- Need real batch/vector throughput over arrays of independent angles: the public API is one angle in, one double out, with no array entry point despite internal AVX2 use.
- Angles very near odd multiples of pi/2 for tan: the function returns +infinity via explicit masking rather than a precise blow-up value.
- Non-x86 targets or CPUs without AVX2/FMA: no scalar or portable fallback is present in the source.
- Need a mature, widely-used dependency: 7 stars, single first-party arXiv preprint (not peer-reviewed), no CI/tests, no install target.

## How it is fast

Replaces libm's accurate but branchy range reduction and polynomial/CORDIC evaluation with a cheap piecewise rational fit: angle reduction picks 1 of 7 precomputed coefficient sets (SinHelperParams/CosHelperParams/TanHelperParams), then computes (linear numerator) \* fastInverseSqrt(quadratic denominator) via AVX2 FMA (_mm256_fmadd_pd). The reciprocal-sqrt step uses a Quake III-style fast inverse square root (magic constant 0x5fe6eb50c7b537a9 plus one Newton-Raphson refinement) instead of hardware division or sqrt, trading accuracy for fewer cycles.

## Compared with alternatives

Pick this over SLEEF or VDT only if you specifically want this piecewise-rational-plus-fast-inverse-sqrt technique or its FPGA/HLS variant; SLEEF gives true 4-wide vectorized libm replacements with selectable ulp accuracy, and VDT is an older, better-documented scalar libm-vs-SIMD comparison with wider function coverage — both are more mature (more usage, tests) than this 7-star single-paper repo.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (only &lt;immintrin.h&gt; AVX2/FMA compiler intrinsics) |
| **Minimum toolchain** | C++17; g++ (developed/tested with MinGW-w64 g++ on Windows; CMakeLists.txt requires CMake &gt;=3.10) |
| **Platforms** | x86-64 with AVX2 and FMA (uses __m256d/_mm256_\* intrinsics); separate Vitis HLS C++ sources exist for FPGA synthesis in vitis_hls_code/ |
| **Thread safety** | not documented; the three parameter tables (sinparams/cosparams/tanparams) are read-only after static initialization and the functions hold no other shared state, so concurrent calls look safe by inspection |
| **Drop-in for the baseline** | partial — same double(double) signature as std::sin/cos/tan, but not numerically interchangeable (max rel error \~0.004 for sin/cos, tan max abs error 0.27 near asymptotes; not IEEE correctly rounded) |

## Gotchas

- Each call broadcasts the single scalar angle into all 4 AVX2 lanes and reads back only lane 0 — SIMD width is not used to batch multiple angles, so the reported per-call speedup may not translate into per-element throughput on arrays.
- tan() near odd multiples of pi/2 is special-cased to return +infinity via an AVX2 compare/blend, not computed from the rational approximation.
- Uses a Quake-style fast inverse square root (bit-hack + 1 Newton-Raphson step) in place of sqrt/division, an extra approximation layer on top of the rational fit.
- No CMake install or library target — the build only produces a benchmark executable (bin/trigno_benchmark.exe), so consumers copy the include/ and relevant src/ files into their own project.

## Caveats and trade-offs

First-party arXiv preprint (cs.MS, Feb 2025), not peer-reviewed. The functions are low-accuracy approximations: the paper reports max abs error 1.5e-3 for sin/cos and 0.27 for tan (max rel error \~3.7e-3 to 6.4e-3), so they are not drop-in replacements for std::sin/cos/tan. The authors' own SIMD Taylor-5 variant was faster (5.83x sin). The benchmark times 1e5 repeated calls on the same single angle through a function pointer (scalar per-call latency, not array throughput). The toolchain is MinGW-w64 g++ on Windows (README: 'MinGW Makefiles'), so the libm under test is the Windows/MinGW CRT, not glibc. The paper calls the baseline 'inbuilt C++ functions' and the code passes ::sin/::cos/::tan. The repo has 7 stars.

Approximate (piecewise rational sin/cos with max relative error \~0.004; tan max absolute error \~0.27 near asymptotes vs 148+ for a degree-9 Taylor baseline); not IEEE correctly-rounded; internally uses a fast inverse-square-root (FISR) hack in place of sqrt/division; the published API is scalar (one angle in, one double out) even though the implementation uses AVX2/FMA internally, so real batched throughput may differ from the reported per-call microbenchmark

## Maintenance

Actively maintained (last commit 2026-01-29 added tan asymptote masking) and Apache-2.0 licensed, but only 7 stars, no CI/tests, and no packaged library target — usability is 'copyable' source, not a dependency to pull in.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** arXiv 2502.10831 Tables 1-3 give mean speed-up ratios of 5.49 (sin), 5.52 (cos) and 4.44 (tan) vs inbuilt functions. The paper states g++ -std=c++17 -mavx2 -mfma -O3 -march=native and an AMD Ryzen 9 5900HX. The benchmark code is public at src/benchmark.cpp (seed 2024873, 1000 angles in [-1e6,1e6], 1e5 iterations), and CMakeLists.txt uses the same flags. That meets every A criterion.
- **Verifier notes:** Numbers and methodology verified against the PDF and the repo. Tier A stands under the rubric, but the accuracy gap (\~3 significant digits) makes this an approximation-vs-exact comparison. The 'throughput' metric label is really per-call latency (metric is not a correctable field).
- **Fields the verifier corrected:** `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/pdf/2502.10831>
  - <https://github.com/Nikhil0250/trigno_simd_cpp>
  - <https://github.com/Nikhil0250/trigno_simd_cpp/blob/main/src/benchmark.cpp>
  - <https://github.com/Nikhil0250/trigno_simd_cpp/blob/main/CMakeLists.txt>
- **Sources the enricher read:**
  - <https://github.com/Nikhil0250/trigno_simd_cpp>
  - <https://github.com/Nikhil0250/trigno_simd_cpp/blob/main/README.md>
  - <https://github.com/Nikhil0250/trigno_simd_cpp/blob/main/CMakeLists.txt>
  - <https://github.com/Nikhil0250/trigno_simd_cpp/blob/main/include/proposed_trigno.h>
  - <https://github.com/Nikhil0250/trigno_simd_cpp/blob/main/src/proposed_trigno.cpp>
  - <https://github.com/Nikhil0250/trigno_simd_cpp/blob/main/LICENSE>
  - <https://arxiv.org/html/2502.10831v1>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/nikhil0250/trigno_simd_cpp`) · [data/wave1/enrich/raw/github_com_nikhil0250_trigno_simd_cpp.json](../../../data/wave1/enrich/raw/github_com_nikhil0250_trigno_simd_cpp.json) (enrichment confidence 0.72)

</details>
