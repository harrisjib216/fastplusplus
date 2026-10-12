# Admiral

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [FFT](README.md)</sub>

**Tier A** (reproducible public benchmark) · Study only · `C++` · `BSD-3-Clause-Attribution` · 🟢 active

> Compiled C++20 SIMD FFT library (any size, 1-D/N-D, c2c/r2c/DCT); the author's sweep has it 1.34-1.43x faster than single-thread FFTW_MEASURE.

| | |
|---|---|
| **Beats** | FFTW 3 (FFTW_MEASURE, single thread; version and build flags of the system fftw3 not stated in the admiral repo, while the author's separate fft_bench uses FFTW 3.3.11); also ducc0 (commit c4dda23) |
| **Claimed result** | At 1 thread beats FFTW_MEASURE by 1.34x (1-D) and 1.43x (N-D), both precisions pooled; vs ducc0 at 1 thread 2.18x (f64) / 2.70x (f32) on 1-D, 1.12x / 1.41x on 2-D, 1.60x / 1.67x on 3-D; at 16 threads vs ducc0 2-D 1.27x / 1.58x and 3-D 2.67x / 3.53x. |
| **Workload** | Complex and real 1-D (19 lengths for the FFTW comparison, 61 for ducc0) and N-D (9 shapes for FFTW, 27 for ducc0) FFTs in float and double on a 16-core AVX-512 Xeon, timed with nanobench (min across repetitions) after an accuracy gate against a reference DFT. |
| **Metric** | latency |
| **Hardware** | Intel Xeon w5-3435X (16 physical cores, AVX-512) |
| **Compiler and flags** | GCC 14.2, CMake 'release' preset: CMAKE_BUILD_TYPE=Release (CMake's GCC default -O3 -DNDEBUG), ADM_TARGET_ARCH=native (-march=native), ADM_USE_FAST_MATH=ON (-ffast-math, the default), LTO off; sweep of 2026-08-24 per benchmark/README.md. FFTW is the system fftw3/fftw3f found via pkg-config, configure flags not stated. |
| **Adoption** | 0 stars, 0 forks, 188 commits (oldest commit on the first commits page 2026-09-11; the README sweep is dated 2026-08-24, so the history goes back further) |
| **Last commit** | 2026-09-29 |
| **Links** | [repository](https://github.com/DiamonDinoia/admiral) · [benchmark](https://github.com/DiamonDinoia/admiral) |

## Verdict

The author's 2026-08-24 sweep on a 16-core Xeon w5-3435X (GCC 14.2, Release, -march=native, -ffast-math; nanobench minimum time, each size accuracy-gated against a reference DFT) has single-thread Admiral at 1.34x (1-D) and 1.43x (N-D) the speed of system FFTW with FFTW_MEASURE. These are geomeans over 19 lengths and 9 shapes, both precisions pooled; FFTW's version and configure flags are not stated, and no per-size times are published. Against ducc0 c4dda23 it reports 2.18x/2.70x (f64/f32) at 1-D, but there the ducc0 arm allocates its output inside the timed region, so small-N 1-D ratios are inflated.

## Use it when

- Single-threaded 1-D or N-D complex FFTs in float or double on AVX-512 or AVX2 x86, where you can build with -march for the target
- Non-power-of-two and prime lengths that you would otherwise run through FFTW's generic paths: codelets up to 64 plus Rader/Bluestein keep them on SIMD code
- Moving existing FFTW complex-DFT code (fftw_plan_dft_\*, fftw_execute, fftw_execute_dft, fftwf_ mirror) by recompiling against &lt;admiral/fftw3.h&gt;
- Large 2-D/3-D transforms with 16 threads, where the author's sweep shows 2.67x (f64) to 3.53x (f32) over threaded ducc0 for 3-D
- Code that wants plan construction without a wisdom or tuning step (estimate mode is deterministic, and fully reproducible with ADM_MEASURE=OFF)

## Skip it when

- Large multi-threaded 1-D transforms: against threaded ducc0 at 16 threads the geomean swings from 0.33x to 1.82x by size (2M and 8M lose by about 3x), because the six-step split rejects some sizes
- Code that needs strict IEEE results: the default build adds -ffast-math (reassociation, flushed denormals), so turn ADM_USE_FAST_MATH off and expect less speed
- Code that needs FFTW's r2c/r2r, guru, split-complex, wisdom or fftw_plan_with_nthreads through the shim: these calls are not provided and do not compile
- Projects that need an OSI-approved license or a mature dependency: BSD-3-Clause-Attribution adds a required acknowledgment line, and the project has no stars, a single author, a 2026 history and an AI-assisted codebase by its own README
- Small build machines or quick CI: one engine translation unit peaks near 12 GB of RAM at AVX-512 native, and the README warns that compiles are long

## How it is fast

Butterfly codelets up to radix 64 are unrolled at compile time with poet and vectorized with xsimd, and a mixed-radix decimation-in-frequency (DIF) pass chain is scheduled over them. Awkward lengths go to Good-Thomas prime-factor, Rader (prime N) or Bluestein (chirp-z) routes. Out-of-cache sizes use Bailey's four-step algorithm with fused, cache-blocked transposes and non-temporal stores past about 2x L3. A fitted cost model picks the route at plan time (effort::estimate); effort::automatic also times the top candidates. A per-plan thread pool engages only above about 2^15 elements and sizes itself from modelled work plus measured wake cost.

## Compared with alternatives

Choose Admiral over PocketFFT (C++ branch) and ducc0 when you have AVX2/AVX-512 x86 and can build per-target: its own sweep has it 1.1-2.7x faster than ducc0 single-threaded. Choose it over FFTW when you want a permissive (attribution) license and a recompile-only shim for complex DFTs. VectorFFT (measured against MKL) or FFTW itself are the better choice when you need wisdom, the full guru API or results from someone other than the author.

## Integration

| | |
|---|---|
| **Form** | shared lib (also static lib), built with CMake 3.25+ |
| **Dependencies** | xsimd and poet (fetched by CPM at configure time); Catch2, ducc0, nanobench and optionally system fftw3/fftw3f only for tests and benchmarks |
| **Minimum toolchain** | C++20 by default (C++17 with -DADM_CXX_STANDARD=17; the two builds are not link-compatible); GCC 14+ or Clang 19+ recommended, older C++20 compilers work but generate slower code |
| **Platforms** | x86-64 measured (Xeon w5-3435X AVX-512, plus Ice Lake/Rome/Genoa in the author's fft_bench); default -march=native binaries are not portable (use ADM_TARGET_ARCH=x86-64-v3); thread pinning is Linux-only; other ISAs not documented |
| **Thread safety** | Documented: forward/inverse on one plan may be called from several threads (all scratch is per call), but pooled calls serialize, so use one plan per thread for throughput; with the FFTW shim, concurrent fftw_execute on one plan races on its planned output buffer, so use fftw_execute_dft with per-thread buffers |
| **Drop-in for the baseline** | partial: an FFTW shim covers only complex DFT planning/execution, the alloc helpers and the fftwf_ mirror; flags other than FFTW_ESTIMATE all map to a plan-time race, and failed plans return NULL with no reason |

## Gotchas

- nthreads=0 (auto) runs serial below about 32k elements; forcing 16 threads on shapes under about 16k elements is 0.7-1.0x of serial per the benchmark README
- effort::automatic/measure pick routes by timing, so plans can differ between runs and machines; one-shot functions always use estimate
- Span overloads validate sizes and throw admiral::error subclasses (size_error, unsupported_error, internal_error); pointer overloads trust the caller
- long double runs a scalar backend and is limited to plan, plan_r2c and the one-shots; there is no strided r2r, so an N-D DCT needs your own transposes

## Known shortcomings

- fft_bench is by the same owner, so not independent; builds with -ffast-math by default; the 1-D ducc0 test allocates and zero-fills a new output vector inside the timed loop, inflating the 2.18x/2.70x figures (the FFTW test is fair); BSD-3-Clause-Attribution is not OSI-approved, so reference.
- 16-thread 1-D vs ducc0 is 0.33x at some sizes; the FFTW shim covers complex DFT only.

## Caveats and trade-offs

Benchmark is run by the library author, and the same author (DiamonDinoia) wrote the fft_bench shootout repo, so that repo is not independent evidence. Only pooled ratios are published (FFTW: 19 1-D lengths and 9 N-D shapes, both precisions pooled), no per-size times. Admiral is built with -ffast-math by default (relaxed IEEE, flushed denormals), though every timed size is accuracy-gated against a reference DFT; FFTW's version and build flags (e.g. whether AVX-512 codelets were enabled) are not stated for the w5-3435X sweep. In bench_fft.cpp the 1-D ducc0 arm calls ducc0_forward_fft, which allocates and zero-fills a fresh output std::vector inside the timed lambda while Admiral reuses a preallocated buffer, so the 1-D ducc0 ratios (2.18x/2.70x) carry allocation overhead that matters most at small N; the N-D ducc0 arm and the FFTW arm use preallocated buffers. In the fft_bench plots (images only) Admiral is roughly tied with MKL and FFTW over much of the 1-D range single-threaded on Xeon Platinum 8362 and EPYC 9474F, with MKL ahead at small sizes on Intel, FFTW ahead at small sizes on AMD, Sleef ahead at mid and large sizes on EPYC 9474F, and multi-threaded MKL clearly ahead for large 1-D on the Intel node; that README marks its MKL-omp numbers for rome and genoa as invalid. 16-thread 1-D vs threaded ducc0 is mixed per benchmark/README.md (geomean 0.33x to 1.82x by size). Very new project; the README says much of the code and cost-model tuning was done with Claude and that the author does not claim the fastest FFT. License is BSD-3-Clause-Attribution (adds an acknowledgment clause naming the Admiral FFT library), which the SPDX license list marks as not OSI-approved, hence usability reference.

Needs C++20 (buildable at C++17 with -DADM_CXX_STANDARD=17); GCC 14+ or Clang 19+ recommended, older compilers generate worse code. Compile time is long (compiled codelets up to radix 64 via xsimd and poet). Default -march=native binaries are not portable. Three interfaces: C++, C and an FFTW-subset drop-in (&lt;admiral/fftw3.h&gt;). Any size and rank, float/double/long double; no wisdom files (cost model at effort::estimate, plan-time race at automatic). Threads stay serial below about 32k elements.

## Maintenance

Very active (last commit 2026-09-29; CI, codecov, Doxygen/Sphinx docs, 0 open issues). It is a one-author project with no adoption yet, and its BSD-3-Clause-Attribution license is not OSI-approved, so it is catalogued as reference rather than copyable.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** Benchmark code is public (benchmark/bench_fft.cpp, bench_nd.cpp, bench_harness.hpp; FFTW arm plans once with FFTW_MEASURE outside the timed loop), and benchmark/README.md states GCC 14.2, Xeon w5-3435X and the release preset, whose flags (Release, -march=native, -ffast-math by default) are public in CMakePresets.json and docs/build-options.md. Only pooled ratios are published, not per-size times, and the run is the author's own.
- **Verifier notes:** All headline numbers match README.md and benchmark/README.md. Usability changed to reference because BSD-3-Clause-Attribution is not OSI-approved (SPDX license-list-data 3.29.0: isOsiApproved false). fft_bench is by the same owner (DiamonDinoia) and lists Admiral at commit b2bf2d3, so it adds plots but no independence; I viewed three of its plots (1-D ST icelake and genoa, 1-D MT icelake) and they match the record's description.
- **Fields the verifier corrected:** `baseline`, `compiler_and_flags`, `usability`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/DiamonDinoia/admiral>
  - <https://github.com/DiamonDinoia/admiral/commits/master>
  - <https://raw.githubusercontent.com/DiamonDinoia/admiral/HEAD/README.md>
  - <https://raw.githubusercontent.com/DiamonDinoia/admiral/HEAD/benchmark/README.md>
  - <https://raw.githubusercontent.com/DiamonDinoia/admiral/HEAD/CMakePresets.json>
  - <https://raw.githubusercontent.com/DiamonDinoia/admiral/HEAD/docs/build-options.md>
  - <https://raw.githubusercontent.com/DiamonDinoia/admiral/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/DiamonDinoia/admiral/HEAD/benchmark/CMakeLists.txt>
  - <https://raw.githubusercontent.com/DiamonDinoia/admiral/HEAD/benchmark/bench_fft.cpp>
  - <https://raw.githubusercontent.com/DiamonDinoia/admiral/HEAD/benchmark/bench_harness.hpp>
  - <https://raw.githubusercontent.com/DiamonDinoia/admiral/HEAD/benchmark/bench_nd.cpp>
  - <https://raw.githubusercontent.com/DiamonDinoia/fft_bench/HEAD/README.md>
  - <https://raw.githubusercontent.com/DiamonDinoia/fft_bench/HEAD/fi/1d_c2c_st_icelake.png>
  - <https://raw.githubusercontent.com/DiamonDinoia/fft_bench/HEAD/fi/1d_c2c_st_genoa.png>
  - <https://raw.githubusercontent.com/DiamonDinoia/fft_bench/HEAD/fi/1d_c2c_mt_icelake.png>
  - <https://raw.githubusercontent.com/spdx/license-list-data/main/json/licenses.json>
- **Sources the enricher read:**
  - <https://github.com/DiamonDinoia/admiral>
  - <https://raw.githubusercontent.com/DiamonDinoia/admiral/HEAD/README.md>
  - <https://raw.githubusercontent.com/DiamonDinoia/admiral/HEAD/benchmark/README.md>
  - <https://raw.githubusercontent.com/DiamonDinoia/admiral/HEAD/docs/usage.md>
  - <https://raw.githubusercontent.com/DiamonDinoia/admiral/HEAD/docs/build-options.md>
  - <https://raw.githubusercontent.com/DiamonDinoia/admiral/HEAD/docs/README.md>
  - <https://raw.githubusercontent.com/DiamonDinoia/admiral/HEAD/docs/cpp-api.md>
  - <https://raw.githubusercontent.com/DiamonDinoia/admiral/HEAD/docs/install.md>
  - <https://raw.githubusercontent.com/DiamonDinoia/admiral/HEAD/include/admiral/admiral.hpp>
  - <https://raw.githubusercontent.com/DiamonDinoia/admiral/HEAD/include/admiral/fftw3.h>
  - <https://raw.githubusercontent.com/DiamonDinoia/admiral/HEAD/include/admiral/detail/plan.hpp>
  - <https://raw.githubusercontent.com/DiamonDinoia/admiral/HEAD/include/admiral/detail/rader.hpp>
  - <https://raw.githubusercontent.com/DiamonDinoia/admiral/HEAD/include/admiral/detail/bluestein.hpp>
  - <https://raw.githubusercontent.com/DiamonDinoia/admiral/HEAD/include/admiral/detail/good_thomas.hpp>
  - <https://raw.githubusercontent.com/DiamonDinoia/admiral/HEAD/include/admiral/detail/four_step_large.hpp>
  - <https://raw.githubusercontent.com/DiamonDinoia/admiral/HEAD/include/admiral/detail/dif_driver.hpp>
  - <https://raw.githubusercontent.com/DiamonDinoia/admiral/HEAD/LICENSE>
  - <https://github.com/DiamonDinoia/admiral/tree/master/src>
  - <https://github.com/DiamonDinoia/admiral/tree/master/include/admiral/detail>
  - <https://github.com/DiamonDinoia/admiral/issues>
  - <https://raw.githubusercontent.com/DiamonDinoia/fft_bench/HEAD/README.md>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/diamondinoia/admiral`) · [data/wave8/enrich/raw/github_com_diamondinoia_admiral.json](../../../data/wave8/enrich/raw/github_com_diamondinoia_admiral.json) (enrichment confidence 0.8)

</details>
