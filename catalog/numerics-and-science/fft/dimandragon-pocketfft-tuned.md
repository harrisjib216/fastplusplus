# pocketfft-tuned (benchmark-driven PocketFFT fork)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [FFT](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> Header-only PocketFFT fork with AVX float 1-D codelets: 2.4x upstream, 1.35x FFTW_ESTIMATE on 1-D c2c; loses to FFTW_MEASURE.

| | |
|---|---|
| **Beats** | FFTW3 FFTW_ESTIMATE, upstream PocketFFT (ref 32424d2) and KissFFT; the fork is slower than FFTW_MEASURE and KFR |
| **Claimed result** | SIMD build, median ratio other/tuned (tuned wins/ratios): 1-D c2c 2.40x vs upstream PocketFFT (1258/1260), 1.35x vs FFTW_ESTIMATE (813/1260), 4.63x vs KissFFT (952/990), 3.25x vs meow_fft; 1-D r2c 2.50x and c2r 2.75x vs upstream, 1.45x and 1.44x vs FFTW_ESTIMATE; 2-D c2c 6.43x vs FFTW_ESTIMATE; 3-D r2c 1.13x vs FFTW_MEASURE and 1.99x vs KFR. Slower than FFTW_MEASURE (0.71x on 1-D c2c) and KFR (0.49x on 1-D c2c). 2-D and 3-D versus upstream PocketFFT are about 1.0x. In the no-SIMD build the gain over upstream is 1.12x (1-D c2c) to 1.67x (c2r). |
| **Workload** | Randomized interleaved Google Benchmark sweep, 90 iterations per scenario, taskset -c 2: 14 mixed 1-D sizes (4096 to 1048576 including primes and near-primes), five 2-D shapes (256x256 to 1024x1024) and four 3-D shapes (64^3 to 128x128x64); c2c, r2c and c2r. Ratio is other implementation CPU ns over tuned fork CPU ns. |
| **Metric** | latency |
| **Compiler and flags** | SIMD build: g++ -O3 -march=native -std=c++20 plus about 15 opt-in tuning macros (POCKETFFT_TUNED_DEFINES); no-SIMD build: clang++ -O3 with vectorization off (benchmarking-fft Makefile). FFTW 3.3.10 built from the release tarball; KFR 7 built with clang++ C++20. |
| **Adoption** | 0 stars |
| **Last commit** | 2026-06-27 |
| **Links** | [repository](https://github.com/Dimandragon/pocketfft-tuned) · [benchmark](https://raw.githubusercontent.com/Dimandragon/benchmarking-fft/main/results/full-machine-bench-2026-06-26-randomized-90iter/summary.md) |

## Verdict

The author's randomized, CPU-pinned (taskset -c 2) Google Benchmark sweep ran 90 iterations per scenario in single precision. Makefile defaults: g++ -O3 -march=native -std=c++20 for the SIMD build, clang++ with vectorization off and FFTW_NO_SIMD for the no-SIMD build, FFTW 3.3.10 built from source; CPU model not stated, workstation not quiet. Median 1-D c2c times: 2.40x faster than upstream PocketFFT 32424d2 and 1.35x faster than FFTW_ESTIMATE, but 0.71x of FFTW_MEASURE and 0.49x of KFR; 2-D/3-D were about even with upstream.

## Use it when

- You already call PocketFFT (or vendor its header) for single-precision 1-D c2c/r2c/c2r on x86 with AVX and want a median 2.4-2.75x speedup without changing the API
- You cannot use GPL FFTW and your alternative is FFTW_ESTIMATE-quality planning: the fork beat FFTW_ESTIMATE in 813 of 1260 1-D c2c pairs (median 1.35x) and 447 of 450 2-D c2c pairs (median 6.43x)
- Real-input float transforms at awkward lengths such as 131071 or 315392 points, where it was the fastest of all tested libraries in the 2026-06-26 snapshot
- Float 3-D r2c in a BSD header-only package: median 1.13x over FFTW_MEASURE and 1.99x over KFR in the snapshot

## Skip it when

- You can use FFTW with FFTW_MEASURE/PATIENT plans, or KFR: they won most 1-D cases (fork median 0.71x and 0.49x on 1-D c2c), and FFTW_MEASURE was 6.06x faster at N=4096
- Double or long double, ARM/NEON, or x86 builds without AVX: the new codelets handle only float and need AVX, so these builds run almost entirely upstream code. They were not benchmarked, except for the scalar no-SIMD float build (1.12x to 1.67x over upstream)
- 2-D and 3-D workloads: medians against upstream PocketFFT are 0.98x to 1.04x, so the fork adds risk for no measured gain
- 1-D lengths below 4096: the sweep's smallest size was 4096, so nothing smaller was measured
- Code that needs a supported library: one author, 0 stars, no releases or tags, and the README calls the numbers a local snapshot from a noisy workstation

## How it is fast

It adds hand-written AVX intrinsics codelets for complex&lt;float&gt; radix-2/3/4/8 passes and for the real radf4/radb4 passes, some with AVX2/FMA variants. Upstream PocketFFT vectorizes only across lines of multi-D arrays, so its 1-D path is scalar. Power-of-two c2c plans also get fused radix-4x4 middle stages and blocked/batched terminal stages. Selected mixed-radix lengths get measured factorization and dispatch choices, and float prime lengths choose between Rader (computed internally in double) and Bluestein. A change was promoted only after paired randomized benchmark runs, pass-level probes and correctness checks.

## Compared with alternatives

Pick it over upstream PocketFFT (mreineck/pocketfft) when the hot path is 1-D float on AVX x86 and you want the same API; for multi-D or double precision upstream is equivalent and better tested. Pick FFTW (MEASURE planning), KFR or Admiral when raw 1-D speed matters more than a BSD header-only drop-in.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none beyond the C++ standard library and threads (multi-threading can be disabled with POCKETFFT_NO_MULTITHREADING) |
| **Minimum toolchain** | C++17 in practice: the header's guard checks only for C++11 and the README still says 'strictly C++11', but the header uses if constexpr in 15 places. The benchmarks build it with g++ -O3 -march=native -std=c++20. |
| **Platforms** | Any C++ platform. The tuned 1-D SIMD paths need x86 AVX (some AVX2/FMA) and float; other targets fall back to upstream PocketFFT code paths. |
| **Thread safety** | Not documented in the README. In the source, the optional plan cache is mutex-guarded and plans are shared via shared_ptr; the opt-in split8 cached buffer is a per-plan buffer behind a mutex, so concurrent calls that share such a plan serialize. |
| **Drop-in for the baseline** | partial — drop-in for upstream PocketFFT's C++ header (same namespace and signatures); not API-compatible with FFTW or KissFFT |

## Gotchas

- The published SIMD run also defined about 15 opt-in macros (POCKETFFT_TUNED_DEFINES in the benchmarking-fft Makefile, e.g. POCKETFFT_C2C_POWER2_FUSED_PASS4X4 and ..._SPLIT8_TILE256_CACHED_BUFFER). A plain #include does not get them, and by default they only engage at N &gt;= 1,048,576 (some at 32M+). Copy those defines to reproduce the published configuration.
- Codelets are chosen at compile time from __AVX__/__AVX2__/__FMA__, with no runtime CPU dispatch: build with -mavx2 (or at least -mavx) or -march=native, or you get scalar 1-D code, and a binary built that way will not run on CPUs without AVX
- Plan caching is off unless POCKETFFT_CACHE_SIZE is set (the benchmarks use 16); without it every 1-D call re-plans, which hurts repeated small transforms
- With POCKETFFT_C2C_POWER2_SPLIT8_TILE256_CACHED_BUFFER, each cached plan keeps a length-N complex&lt;float&gt; scratch array alive (256 MiB at N=32M)

## Known shortcomings

- Benchmark-driven fork of PocketFFT (listed separately); kept as its own entry because its tuning and numbers are its own, but it may fold under PocketFFT.
- Fork of PocketFFT; the new AVX codelets handle float only and the benchmarks are float only, so double and NEON users get essentially upstream code. README and header guard claim C++11 but the header uses if constexpr in 15 places (C++17 in practice). Flags are stated in the benchmarking-fft Makefile (corrected); CPU model still not stated.

## Caveats and trade-offs

First-party benchmark by the fork author. CPU model is not stated; the workstation was not quiet (ASLR on, load average often above idle) and the author calls the numbers a local snapshot. The fork loses to FFTW_MEASURE and KFR on most 1-D cases and to upstream on some 2-D/3-D cases. MKL is not in the harness. Fork changes performance-relevant code, so it is reported here, but the orchestrator may fold it under PocketFFT. Floating-point precision of the runs is not stated in the README.

Header-only C++11 like PocketFFT; the tuning targets hot 1-D paths (large power-of-two c2c terminal stages, fused pass4x4, split8 buffering, measured dispatch for selected mixed radix). Keeps PocketFFT features (float/double/long double, multi-dimensional, DCT/DST, Bluestein).

## Maintenance

Active single-author fork (226 commits, last 2026-06-27, 0 stars, no releases). BSD-3-Clause and header-only, so easy to vendor, but treat it as experimental until its changes reach upstream.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The summary.md from the fork author's public benchmarking-fft harness (randomized, 90 iterations, raw CSV/JSON published) compares against upstream PocketFFT, FFTW3, KFR and KissFFT, but neither the CPU model nor the compiler and flags are stated (CXX/CXXFLAGS come from the environment), so C.
- **Verifier notes:** All quoted ratios match summary.md and the benchmarking-fft README. BSD-3-Clause, 0 stars, last commit 2026-06-27 confirmed; GitHub does not mark it as a fork, but its README says it starts from the GitLab PocketFFT. The orchestrator may fold it under PocketFFT (mreineck/pocketfft is already filed in wave 8).
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/Dimandragon/benchmarking-fft/main/results/full-machine-bench-2026-06-26-randomized-90iter/summary.md>
  - <https://raw.githubusercontent.com/Dimandragon/benchmarking-fft/main/README.md>
  - <https://raw.githubusercontent.com/Dimandragon/pocketfft-tuned/HEAD/README.md>
  - <https://github.com/Dimandragon/pocketfft-tuned>
  - <https://github.com/Dimandragon/pocketfft-tuned/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/Dimandragon/pocketfft-tuned/HEAD/README.md>
  - <https://raw.githubusercontent.com/Dimandragon/pocketfft-tuned/HEAD/pocketfft_hdronly.h>
  - <https://raw.githubusercontent.com/Dimandragon/pocketfft-tuned/HEAD/meson.build>
  - <https://github.com/Dimandragon/pocketfft-tuned>
  - <https://github.com/Dimandragon/pocketfft-tuned/commits>
  - <https://github.com/Dimandragon/benchmarking-fft>
  - <https://raw.githubusercontent.com/Dimandragon/benchmarking-fft/main/README.md>
  - <https://raw.githubusercontent.com/Dimandragon/benchmarking-fft/main/results/full-machine-bench-2026-06-26-randomized-90iter/summary.md>
  - <https://raw.githubusercontent.com/Dimandragon/benchmarking-fft/main/Makefile>
  - <https://raw.githubusercontent.com/Dimandragon/benchmarking-fft/main/1d.cpp>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/dimandragon/pocketfft-tuned`) · [data/wave8/enrich/raw/github_com_dimandragon_pocketfft_tuned.json](../../../data/wave8/enrich/raw/github_com_dimandragon_pocketfft_tuned.json) (enrichment confidence 0.75)

</details>
