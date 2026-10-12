# Intel Parallel STL

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Thread pools and work stealing](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `Apache-2.0 WITH LLVM-exception` · 🟢 active

> Intel's C++17 parallel algorithms (now oneDPL; libstdc++'s &lt;execution&gt;): std::reduce(par) on oneTBB beats serial std::accumulate \~98x.

| | |
|---|---|
| **Beats** | std::accumulate (serial, libstdc++ 12) |
| **Claimed result** | AWS Graviton4 c8g.metal-24xl: std::reduce&lt;par&gt;/f32 1950894 ns (550.384 GB/s) versus std::accumulate/f32 192162701 ns (5.58767 GB/s), about 98x (derived from page data); f64 1959062 ns versus 192266754 ns, about 98x (derived from page data). AWS Zen4 m7a.metal-48xl: std::reduce&lt;par, f32&gt; 2913596 ns versus std::accumulate&lt;f32&gt; 219734340 ns, about 75x (derived from page data). |
| **Workload** | Sum of a 1 GiB array of 268435456 floats, all set to 1.0f, using std::reduce(std::execution::par, first, last, T(0), std::plus&lt;T&gt;) versus serial std::accumulate, both from GCC 12's libstdc++. libstdc++'s &lt;execution&gt; uses its bundled Parallel STL with the oneTBB backend. The f64 rows accumulate the same float array into a double. Google Benchmark with MinTime 10 s and UseRealTime; the error is checked against the expected sum. |
| **Metric** | throughput |
| **Hardware** | AWS Graviton4 c8g.metal-24xl (Google Benchmark reports 96 x 2000 MHz; single NUMA node) for the headline row. AWS Zen4 m7a.metal-48xl (192 x 3701.95 MHz reported; dual-socket per the README's observation; exact CPU SKU not stated) for the second row. |
| **Compiler and flags** | GCC 12 (stated in the README for the Graviton4 and Zen4 runs). CMake Release build: CMAKE_CXX_FLAGS_RELEASE becomes '-O3 -DNDEBUG -O2', and the last -O wins, so the build is -O2. For GNU compilers CMakeLists.txt sets CMAKE_CXX_FLAGS to CMAKE_GCC_FLAGS ('-march=native -fopenmp'), so those flags do apply; tags v0.1.0, v0.2.0, v0.3.0, v0.4.0, v0.5.3 and HEAD v0.7.2 all use the same logic. oneTBB is fetched from uxlfoundation/oneTBB branch master (unpinned), and USE_INTEL_TBB defaults to ON on Linux without CUDA. Google Benchmark v1.9.1. |
| **Adoption** | 777 stars and 122 forks on uxlfoundation/oneDPL, which github.com/intel/parallelstl now serves. Intel contributed its Parallel STL to GCC 9's libstdc++ as the implementation of the C++17 parallel algorithms (Phoronix 'GCC 9 libstdc++ Lands The C++17 Parallel Algorithms Implementation From Intel' and the gcc.gnu.org libstdc++ RFC of November 2017; WebSearch snippets only). |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/intel/parallelstl) · [benchmark](https://github.com/ashvardanian/ParallelReductionsBenchmark) |

## Verdict

In ashvardanian/ParallelReductionsBenchmark (Google Benchmark, MinTime 10 s, real time, GCC 12, effective -O2 -march=native -fopenmp, oneTBB master), std::reduce(std::execution::par) from libstdc++'s bundled Parallel STL summed a 1 GiB float array in 1.95 ms versus 192 ms for serial std::accumulate on a 96-core AWS Graviton4 c8g.metal-24xl (about 98x, derived from page data), and 2.91 ms versus 220 ms on a Zen4 m7a.metal-48xl (about 75x); intel/parallelstl and oneDPL themselves were not built or measured.

## Use it when

- Large contiguous arrays (millions of elements and up) of arithmetic types where a single std::accumulate or std::transform is memory- or latency-bound and many cores sit idle.
- Existing standard C++17 code on GCC 11+ or Clang with libstdc++ that can gain parallelism by adding std::execution::par and linking oneTBB, with no new dependency in the source.
- Codebases already shipping oneTBB or the oneAPI toolchain, where oneDPL's oneapi::dpl::execution policies also give an OpenMP backend and SYCL device offload behind one API.
- Floating-point sums where a strict left fold is not required and reassociated, chunked reduction is acceptable (it is also more accurate than a single float accumulator for long arrays).

## Skip it when

- Small or frequent calls where task-dispatch cost dominates: the benchmark never timed std::reduce(par) on tiny inputs, and on the 1 GiB sum on 96-core Graviton4 hand-written OpenMP (1.90 ms) and Fork Union (1.89 ms) already matched or beat it (1.95 ms), so a lighter fork-join pool loses nothing on large inputs.
- Builds without oneTBB: libstdc++ selects the TBB backend only if &lt;tbb/tbb.h&gt; is found by __has_include and otherwise silently uses its serial backend, so the same code compiles and runs single-threaded.
- GCC 9 or 10 with oneTBB 2021 or newer: libstdc++'s bundled backend still uses the removed tbb::task API and fails to compile (Intel community and Slicer forum reports, snippet only); GCC 11+ is needed.
- Code that needs bit-for-bit reproducible float results: libstdc++ uses tbb::parallel_reduce, not tbb::parallel_deterministic_reduce, so rounding of float sums can depend on how the range was split.
- MSVC STL or libc++ users: the measured code is libstdc++'s copy; those standard libraries ship their own parallel algorithms, which were not compared.

## How it is fast

In libstdc++ 12, std::reduce(par) becomes __parallel_transform_reduce, a tbb::parallel_reduce over a blocked_range with grain size 3 inside tbb::this_task_arena::isolate; each oneTBB worker reduces its chunk and partial sums are joined pairwise, so a 1 GiB sum spreads across all cores and reaches memory bandwidth. With par_unseq the per-chunk brick is __simd_transform_reduce, a loop under '#pragma omp simd reduction(+)'; with par the brick is a serial std::transform_reduce. Most of the measured gain is core count, not a cleverer kernel: a single-thread 8-accumulator loop is already 5x faster than std::accumulate on the same machine.

## Compared with alternatives

Pick it when you want parallelism through the standard algorithm API with no scheduler code of your own and can link oneTBB; poolSTL gives the same std-style calls header-only without TBB and beat std::execution::par on some algorithms, and Fork Union matched its 1 GiB reduction time on Graviton4 in the same benchmark while needing explicit fork-join code.

## Integration

| | |
|---|---|
| **Form** | header-only (libstdc++ &lt;execution&gt;, or oneDPL's include/oneapi/dpl) plus the oneTBB shared library for the parallel backend |
| **Dependencies** | oneTBB (libtbb) for the TBB backend; oneDPL alternatively accepts an OpenMP 4.5 compiler as backend; SYCL 2020 compiler only for device policies |
| **Minimum toolchain** | C++17; GCC 11+ for libstdc++'s backend with oneTBB 2021+ (GCC 9-10 need TBB 2018-2020); oneDPL documents C++17, OpenMP 4.0 SIMD support and CMake 3.11 (Linux) / 3.20 (Windows) |
| **Platforms** | any platform oneTBB supports (measured on x86-64 Zen4 and aarch64 Graviton4); device policies need a SYCL backend |
| **Thread safety** | Standard parallel-algorithm rules: element access functions run concurrently and must be data-race free under par; oneTBB's global scheduler is shared across concurrent calls |
| **Drop-in for the baseline** | partial: std::reduce(std::execution::par, ...) replaces std::accumulate with one argument added, but it may reassociate the operation (results change for non-associative ops and float rounding) and needs -ltbb; oneDPL uses its own oneapi::dpl::execution namespace |

## Gotchas

- Silent serial fallback: libstdc++ 12 c++config defines _GLIBCXX_USE_TBB_PAR_BACKEND as __has_include(&lt;tbb/tbb.h&gt;), so a missing include path gives _PSTL_PAR_BACKEND_SERIAL with no warning; check that the binary links libtbb.
- The headline 98x compares against a serial std::accumulate whose float accumulator is wrong (error 93.75 percent: it stops growing at 2^24) and whose strict left fold is latency-bound; the unrolled single-thread loop is already 5.05x faster on Graviton4 (derived from page data), so parallelism contributes about 19.5x.
- Benchmark harness quirks: Graviton4 rows report 548-568 GB/s, above one socket's 537.6 GB/s DRAM peak, so part of the 1 GiB buffer is served from the 192 MB of L2 plus 36 MB L3 across repeated iterations; the all-1.0f input can detect dropped elements but not reassociation error; CMakeLists defines USE_INTEL_TBB=0 when the option is off while reduce_cpu.hpp tests '#if defined(USE_INTEL_TBB)', so the TBB headers are included even in builds that disable TBB.
- oneDPL execution policies parallelize only with random-access iterators; other iterator categories run serially (oneDPL guide).

## Known shortcomings

- ashvardanian/ParallelReductionsBenchmark measured libstdc++'s vendored PSTL on oneTBB (std::reduce par vs serial std::accumulate, about 98x Graviton4, 75x Zen4 derived from page data), not intel/parallelstl itself, whose repo is archived in favour of oneDPL; the tie is lineage only (Intel's contribution to GCC 9, snippet only). The std::accumulate baseline is latency-bound (an unrolled serial loop is already 5.05x faster); fork_union and OpenMP match or beat std::reduce par; reported 550-568 GB/s exceeds Graviton4's 537.6 GB/s DRAM peak (cache effect); oneTBB master unpinned, single runs, benchmark repo has no LICENSE, DGX par f64 rows error 100%. Build flags do apply (CMakeLists.txt copies CMAKE_GCC_FLAGS), effective -O2.
- Enricher: libstdc++'s c++config silently falls back to the serial backend when tbb/tbb.h is missing; the GCC 9/10 backend fails to compile with oneTBB 2021+ (snippet only); the f32 std::accumulate baseline gives a wrong answer (93.75% error) and an unrolled loop alone is 5x; the reduction uses tbb::parallel_reduce, not the deterministic variant; the harness CMake defines USE_INTEL_TBB=0 while the code tests #if defined(USE_INTEL_TBB) (std::reduce rows unaffected).

## Caveats and trade-offs

Indirect evidence: the benchmark runs libstdc++'s bundled &lt;execution&gt; implementation (a vendored copy of Intel's Parallel STL as contributed to GCC 9, backed by oneTBB). It does not build intel/parallelstl or oneDPL, and oneDPL's oneapi::dpl::execution policies were not measured. The baseline is a serial std::accumulate, whose strict left fold makes it latency-bound on the floating-point add chain, not memory-bound. On Graviton4 the single-thread unrolled/f32 loop (38034000 ns) is already 5.05x faster than std::accumulate/f32 (derived from page data), so 96-core parallelism accounts for only about 19.5x of the 98x (derived from page data). A std::reduce(seq) or unrolled serial baseline would show a far smaller gain. On Graviton4, hand-written OpenMP (neon/f32/openmp 1901684 ns) and fork_union (neon/f32/av::fork_union 1890173 ns; serial/f32/av::fork_union 1889686 ns) match or beat std::reduce&lt;par&gt;/f32 at 1950894 ns. The Graviton4 rows report 550 to 568 GB/s, above the 537.6 GB/s theoretical DRAM peak of one Graviton4 socket (12 channels of DDR5-5600; WikiChip and The Next Platform, snippet only). Repeated iterations over the 1 GiB buffer are therefore partly served from the 96 x 2 MB L2 and 36 MB L3, and absolute bandwidth is slightly inflated. std::accumulate&lt;f32&gt; shows 93.75 percent error because a float accumulator stops growing at 2^24; the f64 row is accurate. The README tables are single hand-pasted runs with no variance reported. oneTBB master is not pinned, and fork_union is fetched from its main branch. The benchmark repository has no LICENSE file. The DGX-H100 rows were not used: CUDA machines default USE_INTEL_TBB to OFF, so the backend is unclear, and that table's std::reduce&lt;par, f64&gt; and &lt;par_unseq, f64&gt; rows show error,%=100 (wrong result). The Zen4 table dates from the May 2024 README refresh and uses older row labels. The Graviton4 table was added in May 2025 and its std::reduce labels match the current reduce_bench.cpp. No comparison against MSVC STL, libc++ parallel algorithms or GNU parallel mode.

Parallel backend needs oneTBB at link time. The standalone intel/parallelstl repository now serves the oneDPL repository (oneAPI DPC++ Library, Apache-2.0 with LLVM exceptions), which targets SYCL devices and needs the oneAPI toolchain for the device parts.

## Maintenance

Actively maintained as oneDPL under the UXL Foundation (last commit 2026-10-06; release notes top out at 2022.14.0; Apache-2.0 WITH LLVM-exception) and shipped inside every libstdc++ since GCC 9, so it is copyable; libstdc++'s vendored copy lags oneDPL and is tied to the GCC release.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification A, tier now A.
- **Tier reason:** The README of ashvardanian/ParallelReductionsBenchmark shows std::reduce&lt;par&gt; next to serial std::accumulate. The benchmark code is public (reduce_bench.cpp registering stl_par_reduce_gt and stl_accumulate_gt from reduce_cpu.hpp; Google Benchmark, MinTime 10 s, real time, result error checked). The README states GCC 12 and names the CPU (AWS Graviton4 c8g.metal-24xl), and CMakeLists.txt holds the flags. The runner is a third party, not Intel. The measured code is libstdc++'s bundled copy of Intel's Parallel STL on oneTBB, so the tie to this repository rests on lineage.
- **Verifier notes:** Every claimed number matches the README exactly; the ratios are correctly marked as derived. The record's flag caveat was wrong: for GCC, CMakeLists.txt copies CMAKE_GCC_FLAGS into CMAKE_CXX_FLAGS, so -march=native -fopenmp do apply. Shortcomings to record: the measured code is libstdc++'s vendored Parallel STL rather than intel/parallelstl or oneDPL; the latency-bound serial baseline yields 5x from unrolling alone; fork_union and OpenMP match or beat it; oneTBB master is unpinned; reported bandwidth exceeds the DRAM peak; single runs; the benchmark repo has no license.
- **Fields the verifier corrected:** `compiler_and_flags`, `workload`, `hardware`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-59 (wave 11); enricher w11 pair-026
- **Pages the verifier opened:**
  - <https://github.com/ashvardanian/ParallelReductionsBenchmark>
  - <https://raw.githubusercontent.com/ashvardanian/ParallelReductionsBenchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/ashvardanian/ParallelReductionsBenchmark/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ashvardanian/ParallelReductionsBenchmark/HEAD/reduce_bench.cpp>
  - <https://raw.githubusercontent.com/ashvardanian/ParallelReductionsBenchmark/HEAD/reduce_cpu.hpp>
  - <https://raw.githubusercontent.com/ashvardanian/ParallelReductionsBenchmark/v0.4.0/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ashvardanian/ParallelReductionsBenchmark/v0.5.3/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ashvardanian/ParallelReductionsBenchmark/v0.1.0/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ashvardanian/ParallelReductionsBenchmark/v0.2.0/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ashvardanian/ParallelReductionsBenchmark/v0.3.0/CMakeLists.txt>
  - <https://github.com/ashvardanian/ParallelReductionsBenchmark/commits/main>
  - <https://github.com/ashvardanian/ParallelReductionsBenchmark/commits/main/CMakeLists.txt>
  - <https://github.com/ashvardanian/ParallelReductionsBenchmark/commits/main/README.md>
  - <https://github.com/ashvardanian/ParallelReductionsBenchmark/tags>
  - <https://github.com/intel/parallelstl>
  - <https://github.com/uxlfoundation/oneDPL/commits>
- **Sources the enricher read:**
  - <https://github.com/intel/parallelstl>
  - <https://raw.githubusercontent.com/intel/parallelstl/HEAD/README.md>
  - <https://raw.githubusercontent.com/uxlfoundation/oneDPL/HEAD/README.md>
  - <https://github.com/uxlfoundation/oneDPL/tree/main/documentation/library_guide>
  - <https://raw.githubusercontent.com/uxlfoundation/oneDPL/main/documentation/library_guide/introduction.rst>
  - <https://raw.githubusercontent.com/uxlfoundation/oneDPL/main/documentation/library_guide/macros.rst>
  - <https://raw.githubusercontent.com/uxlfoundation/oneDPL/main/documentation/library_guide/parallel_api_main.rst>
  - <https://raw.githubusercontent.com/uxlfoundation/oneDPL/main/documentation/library_guide/overview.rst>
  - <https://raw.githubusercontent.com/uxlfoundation/oneDPL/main/documentation/library_guide/cmake_support.rst>
  - <https://raw.githubusercontent.com/uxlfoundation/oneDPL/main/documentation/release_notes.rst>
  - <https://github.com/uxlfoundation/oneDPL/commits/main>
  - <https://github.com/uxlfoundation/oneDPL/issues?q=is%3Aissue+reduce+performance+tbb>
  - <https://raw.githubusercontent.com/ashvardanian/ParallelReductionsBenchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/ashvardanian/ParallelReductionsBenchmark/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ashvardanian/ParallelReductionsBenchmark/HEAD/reduce_bench.cpp>
  - <https://raw.githubusercontent.com/ashvardanian/ParallelReductionsBenchmark/HEAD/reduce_cpu.hpp>
  - <https://raw.githubusercontent.com/gcc-mirror/gcc/releases/gcc-12/libstdc++-v3/include/bits/c++config>
  - <https://raw.githubusercontent.com/gcc-mirror/gcc/releases/gcc-12/libstdc++-v3/include/pstl/pstl_config.h>
  - <https://raw.githubusercontent.com/gcc-mirror/gcc/releases/gcc-12/libstdc++-v3/include/pstl/parallel_backend.h>
  - <https://raw.githubusercontent.com/gcc-mirror/gcc/releases/gcc-12/libstdc++-v3/include/pstl/parallel_backend_tbb.h>
  - <https://raw.githubusercontent.com/gcc-mirror/gcc/releases/gcc-12/libstdc++-v3/include/pstl/numeric_impl.h>
  - <https://raw.githubusercontent.com/gcc-mirror/gcc/releases/gcc-12/libstdc++-v3/include/pstl/unseq_backend_simd.h>
  - https://discourse.slicer.org/t/current-tbb-2021-is-not-supported-by-gcc-9-or-10-with-std-execution/24282 (WebSearch snippet only)
  - https://community.intel.com/t5/Intel-oneAPI-Math-Kernel-Library/Include-MKL-header-file-with-oneapi-DPL-TBB-error/m-p/1347309 (WebSearch snippet only)
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/intel/parallelstl`) · [data/wave11/enrich/raw/github_com_intel_parallelstl.json](../../../data/wave11/enrich/raw/github_com_intel_parallelstl.json) (enrichment confidence 0.5)

</details>
