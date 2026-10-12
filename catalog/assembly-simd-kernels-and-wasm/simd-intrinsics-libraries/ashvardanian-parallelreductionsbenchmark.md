# ParallelReductionsBenchmark

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [SIMD intrinsics libraries](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `no license` · 🟡 stale

> Educational benchmark of float-array sum kernels (unrolled, SIMD, threaded, GPU) against serial std::accumulate on a 1 GB array.

| | |
|---|---|
| **Beats** | std::accumulate (serial) |
| **Claimed result** | Single thread versus serial std::accumulate (libstdc++, GCC 12), 1 GB array of 1.0f, README tables. AWS Graviton4 c8g.metal-24xl: unrolled/f64 14.7387 GB/s vs std::accumulate/f64 5.58465 GB/s (about 2.6x, derived from page data, both exact); unrolled/f32 28.2311 GB/s, neon/f32 22.2544 GB/s and sve/f32 21.4542 GB/s vs std::accumulate/f32 5.58767 GB/s (about 5.1x, 4.0x and 3.8x, derived from page data). AWS Zen4 m7a.metal-48xl: unrolled&lt;f64&gt; 34.0189 GB/s and avx2&lt;f64&gt; 19.3258 GB/s vs std::accumulate&lt;f64&gt; 4.88389 GB/s (about 7.0x and 4.0x, derived from page data, exact); unrolled&lt;f32&gt; 35.1514, avx2&lt;f32&gt; 33.3195 and avx512&lt;f32interleaving&gt; 26.8351 GB/s vs std::accumulate&lt;f32&gt; 4.88655 GB/s (about 7.2x, 6.8x and 5.5x, derived from page data); avx2&lt;f32kahan&gt; 9.73619 GB/s, exact, about 2.0x std::accumulate (derived from page data). Nvidia DGX-H100 host: avx2&lt;f32&gt; 9.69112 vs std::accumulate&lt;f32&gt; 5.5322 GB/s (about 1.75x, derived from page data). Multithreaded std::reduce&lt;par&gt; (368.528 GB/s on Zen4, 550.384 GB/s on Graviton4) is libstdc++'s own parallel algorithm on oneTBB, not this repository's code. |
| **Workload** | Summing a 1 GB array (268,435,456 floats, all set to 1.0f by std::fill_n) with serial std::accumulate, an 8-accumulator unrolled loop, hand-written SSE/AVX2/AVX-512, NEON and SVE kernels, OpenMP, fork_union, Taskflow, std::reduce with execution policies, Thrust, CUB and CUDA kernels, reported in bytes/s with an error% column against the exact sum n. |
| **Metric** | throughput |
| **Hardware** | AWS Graviton4 (c8g.metal-24xl, 96 cores), AWS m7a.metal-48xl (AMD Zen4, 192 threads at 3701.95 MHz; CPU model string not printed), Nvidia DGX-H100 node (160 threads at 2100 MHz; CPU model not named), Apple M2 Pro |
| **Compiler and flags** | GCC 12 (NVCC 12.1 for the CUDA rows); CMakeLists.txt defaults to Release and appends -O2 to CMAKE_CXX_FLAGS_RELEASE (effective -O2) and sets -march=native -fopenmp for GCC; the Apple M2 Pro table names no compiler |
| **Adoption** | 119 stars |
| **Last commit** | 2025-07-22 |
| **Links** | [repository](https://github.com/ashvardanian/ParallelReductionsBenchmark) · [benchmark](https://github.com/ashvardanian/ParallelReductionsBenchmark) |

## Verdict

With GCC 12 at effective -O2 -march=native, one thread summing 1 GB of 1.0f: the plain 8-accumulator unrolled loop reaches 14.74 (f64) and 28.23 (f32) GB/s on Graviton4 and 34.02/35.15 GB/s on Zen4 m7a, against serial std::accumulate's 5.58 and 4.88 GB/s (about 2.6-7.2x, derived from page data; only f64 is exact). The single-accumulator AVX2/NEON/SVE kernels land between the two, and multithreaded libstdc++ std::reduce&lt;par&gt; on oneTBB (368-550 GB/s) is the fastest CPU row.

## Use it when

- Learning or teaching why a reassociating multi-accumulator loop beats std::accumulate by 2.6-7x on a memory-bound float sum (GCC 12, -O2 -march=native).
- Measuring the memory-bandwidth ceiling of a many-core box: the multithreaded rows reach 368-550 GB/s on Zen4 and Graviton4 with std::reduce&lt;par&gt; or fork_union.
- Comparing thread-pool dispatch latency on tiny inputs (PARALLEL_REDUCTIONS_LENGTH=1536): fork_union, Taskflow, OpenMP and std::thread, plus Rayon/Tokio/smol on the Rust side.
- Starting point for your own reduction when you need f64 or Kahan accumulation over more than 2^24 elements, and will write your own tests on non-uniform data.

## Skip it when

- As a dependency: there is no LICENSE file (raw LICENSE 404, none in the sidebar), no API and no package, so the code cannot legally be copied.
- Copying avx2_f64_t, avx512_f32unrolled_t or avx512_f32interleaving_t: all three return wrong sums on non-uniform input (see gotchas); the harness only ever feeds 1.0f, so the bugs never show in its error column.
- Summing more than 2^24 values into a float accumulator: every f32 row in the README is wrong by 50-94% because each lane saturates at 16,777,216.
- Expecting hand-written intrinsics to beat the compiler: on Zen4 and Graviton4 the plain unrolled loop is faster than the single-accumulator AVX2, NEON and SVE kernels.
- As a source of AVX-512 numbers: the Zen4 1 GB AVX-512 rows were measured on kernels that read only half the array.

## How it is fast

The single-thread gain over std::accumulate comes from breaking the serial floating-point add chain: std::accumulate must fold left to right, so each add waits for the previous one, while unrolled_gt keeps 8 independent accumulators that GCC can also vectorize. The hand-written kernels add SIMD lanes (one accumulator per kernel for SSE/AVX2/NEON/SVE, 2-16 ZMM accumulators with bidirectional traversal and non-temporal loads for AVX-512). Multicore variants split the array into cache-line-rounded per-core chunks with over-aligned partial sums, on huge pages and NUMA-bound memory.

## Compared with alternatives

Pick this over marcelcases/simd or Vectis when you care about a memory-bound 1 GB reduction across many backends (threads, std::reduce, CUDA/CUB) rather than an L1-resident single-core kernel. Vectis's scalar-4acc and -ffast-math rows are the better single-thread control, and EVE or VCL are the libraries to actually ship SIMD reductions with.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | Google Benchmark v1.9.1, fmt 11.1.2, Taskflow v3.10.0, fork_union (main), all fetched by CMake; oneTBB (master) by default on Linux without CUDA; optional libnuma, BLAS, CUDA Toolkit with CCCL, OpenCL. Rust bench: rayon, tokio, async-executor, fork_union 0.3.3, criterion 0.6 |
| **Minimum toolchain** | C++17 (CMAKE_CXX_STANDARD 17), CMake; README results use GCC 12 and NVCC 12.1; code uses std::hardware_destructive_interference_size unconditionally |
| **Platforms** | Linux primary (mmap huge pages, libnuma); macOS via Homebrew LLVM; x86-64 SSE/AVX2/AVX-512 kernels and aarch64 NEON/SVE kernels, compiled in only when -march=native is set (GCC and NVCC paths only); CUDA GPUs |
| **Thread safety** | Not documented; serial kernels are const functors over a const range, multithreaded wrappers own their pool and per-thread partial-sum slots and are not meant to be shared |
| **Drop-in for the baseline** | partial — kernels are functor classes over float const\* ranges that only sum float input; not a std::accumulate replacement, and unlicensed |

## Gotchas

- The harness fills the array with 1.0f and checks only against n, which hides three reduction bugs in current main (confirmed by a self-written transcription test on patterned data): avx2_f64_t's double _mm256_hadd_pd returns 2\*(lane0+lane1) and drops the upper 128-bit lane (1 instead of 16384 when only lane 3 is set); avx512_f32unrolled_t's combine adds fwd5/rev5 twice and drops fwd6/rev6 (20480 vs 16384); avx512_f32interleaving_t loads acc3 from it_begin+32 instead of +16 and acc4 from the same address as acc2, so it never reads every other 64-byte line, then drops acc4 and counts acc2 twice (0 vs 16384).
- The Zen4 1 GB table predates commit a301c39 (2025-01-24, 'Fix: Measuring AVX-512 throughput'): at 9a5a61a the AVX-512 kernels advanced 32 floats per 16-float ZMM load, so they read half the array while bytes/s credited all of it. The 50% error on every avx512 row is that skip, not f32 saturation, so avx512&lt;f32streamed&gt; 19.27, &lt;f32unrolled&gt; 22.28 and &lt;f32interleaving&gt; 26.84 GB/s are invalid. Only the small-array latency-hiding table was re-run after the fix.
- The f32 rows' error column comes from accumulator saturation at 2^24: std::accumulate&lt;f32&gt; 93.75%, unrolled/avx2 f32 50%, NEON/SVE 75%. Only f64, Kahan and std::reduce rows are exact, and the f64 SIMD rows are exact only because every lane holds the same value.
- The AVX-512 kernels use aligned and non-temporal loads at both ends (it_end - 16\*k), so both ends must be 64-byte aligned: lengths that are not a multiple of 16 floats can fault. USE_INTEL_TBB is defined as 0 or 1, so '#if defined(USE_INTEL_TBB)' always pulls in the oneTBB headers. Clang builds get no -march=native, so the AVX2 and AVX-512 kernels compile out.

## Known shortcomings

- Raised C to A on the Graviton4 table (GCC 12, CMake -O2 -march=native -fopenmp, reduce_bench.cpp public; same basis as the wave 11 Intel Parallel STL entry), but no LICENSE (reference); the std::accumulate baseline is latency-bound with no single-thread std::reduce row; hand-written AVX2/AVX-512/NEON/SVE kernels are slower than the plain unrolled loop on Zen4 and Graviton4; all f32 rows are 50-94% wrong (2^24 saturation) and only f64/Kahan rows are exact (f64 2.6x Graviton4, 7.0x Zen4); the multithreaded std::reduce figure belongs to libstdc++.
- Enricher: the harness fills the array with 1.0f and checks only against n, which hides three reduction bugs in current main (confirmed by a transcription test on patterned data): avx2_f64_t's double _mm256_hadd_pd drops the upper lane (1 instead of 16384), avx512_f32unrolled_t counts fwd5/rev5 twice and drops fwd6/rev6 (20480 vs 16384), avx512_f32interleaving_t skips every other 64-byte line and drops acc4 (0 vs 16384); the Zen4 1 GB AVX-512 rows (including the 26.84 GB/s interleaving figure) predate commit a301c39 'Fix: Measuring AVX-512 throughput' whose old kernels read half the array, so their 50% error is that skip, not saturation; unlicensed, reference only. Retiered to C.

## Caveats and trade-offs

This is an educational benchmark collection, not a reusable library, and it has no LICENSE file (raw LICENSE returns 404, no licence in the GitHub sidebar or Cargo.toml), so it is reference only. The baseline is std::accumulate, whose required left-to-right fold is latency-bound on the float add chain at -O2 without -ffast-math; most of the gain comes from reassociation with multiple accumulators, and no single-threaded std::reduce (or unseq) row is measured, which is the standard library's own reassociating alternative. Hand-written intrinsics do not beat the plain unrolled C++ loop in most tables: on Zen4 avx2&lt;f32&gt; 33.32, avx2&lt;f64&gt; 19.33 and avx512&lt;f32interleaving&gt; 26.84 GB/s are all below unrolled&lt;f32&gt; 35.15 / unrolled&lt;f64&gt; 34.02 GB/s, and on Graviton4 neon/f32 22.25 and sve/f32 21.45 GB/s are below unrolled/f32 28.23 GB/s, contradicting the README's statement that hand-written AVX2 beats auto-vectorization (it holds only on the DGX-H100 host). All f32 rows give wrong sums because the input is 2^28 ones and each f32 accumulator saturates at 2^24 (std::accumulate&lt;f32&gt; 93.75% error, unrolled&lt;f32&gt; 50%, neon/sve 75%); only f64 and Kahan rows are exact, and avx2&lt;f32kahan&gt; is about 2x std::accumulate on Zen4. The DGX-H100 table's std::reduce&lt;par, f64&gt; and &lt;par_unseq, f64&gt; rows report 100% error. The Zen4 and DGX tables use older row labels and predate the 2025 code. Single hand-pasted runs with no variance. The README's own conclusion is that multithreaded std::reduce is the CPU winner. [retier] Three kernels in current main return wrong sums on non-uniform data; Zen4 1 GB AVX-512 rows measured by pre-fix kernels that read half the array; no licence file

Educational benchmark harness rather than a drop-in library. Hand-written AVX2 and AVX-512 kernels are x86 only; NEON and SVE variants exist for Arm. Huge pages, NUMA and Kahan summation are handled by hand.

## Maintenance

Stale since 2025-07-22 (119 stars, not archived) and unlicensed, so it is reference only. The multi-accumulator f64 loop is sound teaching material, but avx2_f64_t, avx512_f32unrolled_t and avx512_f32interleaving_t give wrong sums on non-uniform data, and the Zen4 AVX-512 1 GB rows come from pre-fix kernels that read half the array.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** Upgraded C to A: the README's AWS Graviton4 c8g.metal-24xl section names the CPU (Graviton4) and compiler (GCC 12), the flags are in the public CMakeLists.txt (Release, effective -O2, plus -march=native -fopenmp for GCC), and the benchmark code is public (reduce_bench.cpp registering unrolled_gt, stl_accumulate_gt, neon and sve kernels from reduce_cpu.hpp; Google Benchmark, MinTime 10 s, real time, result error checked against n\*1.0). Same basis as the wave 11 intel/parallelstl entry, which was verified A on this README's Graviton4 table.
- **Retiered** A to C: Enricher (2026-10-12): numbers measured on code with correctness bugs. The harness fills the array with 1.0f and checks only against n, hiding wrong sums in avx2_f64_t (upper lane dropped), avx512_f32unrolled_t (accumulators double-counted and dropped) and avx512_f32interleaving_t (every other 64-byte line skipped, acc4 dropped); the Zen4 1 GB AVX-512 rows, including the 26.84 GB/s interleaving figure, predate commit a301c39 'Fix: Measuring AVX-512 throughput' whose kernels read half the array. Later-fixed-bug precedent; unlicensed, reference only.
- **Verifier notes:** All quoted numbers match the README; ratios corrected to be marked derived and extended with the exact f64 rows and the Graviton4 table, and the multithreaded std::reduce figure is attributed to libstdc++ rather than this repo. Shortcomings to record: no license (reference only), educational benchmark repo rather than a library, latency-bound std::accumulate baseline with no std::reduce single-thread row, hand-written SIMD kernels slower than the plain unrolled loop on Zen4 and Graviton4, all f32 rows wrong by 50-94% (only f64/Kahan exact), single runs. Overlap: the same README is the evidence behind the wave 11 intel/parallelstl entry (std::reduce&lt;par&gt;) and contains fork_union rows (wave 11 ashvardanian/fork_union); this record is distinct (its own kernels), not a duplicate. Metadata checked: 119 stars, not archived, last commit 2025-07-22 (stale).
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-41 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/ashvardanian/ParallelReductionsBenchmark>
  - <https://github.com/ashvardanian/ParallelReductionsBenchmark/commits/main>
  - <https://raw.githubusercontent.com/ashvardanian/ParallelReductionsBenchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/ashvardanian/ParallelReductionsBenchmark/main/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ashvardanian/ParallelReductionsBenchmark/main/reduce_bench.cpp>
  - <https://raw.githubusercontent.com/ashvardanian/ParallelReductionsBenchmark/main/reduce_cpu.hpp>
  - <https://raw.githubusercontent.com/ashvardanian/ParallelReductionsBenchmark/main/Cargo.toml>
  - <https://raw.githubusercontent.com/ashvardanian/ParallelReductionsBenchmark/main/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/ashvardanian/ParallelReductionsBenchmark>
  - <https://github.com/ashvardanian/ParallelReductionsBenchmark/commits/main/reduce_cpu.hpp>
  - <https://github.com/ashvardanian/ParallelReductionsBenchmark/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/ashvardanian/ParallelReductionsBenchmark/main/README.md>
  - <https://raw.githubusercontent.com/ashvardanian/ParallelReductionsBenchmark/main/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ashvardanian/ParallelReductionsBenchmark/main/reduce_bench.cpp>
  - <https://raw.githubusercontent.com/ashvardanian/ParallelReductionsBenchmark/main/reduce_cpu.hpp>
  - <https://raw.githubusercontent.com/ashvardanian/ParallelReductionsBenchmark/main/Cargo.toml>
  - <https://raw.githubusercontent.com/ashvardanian/ParallelReductionsBenchmark/main/LICENSE>
  - <https://raw.githubusercontent.com/ashvardanian/ParallelReductionsBenchmark/9a5a61a/reduce_cpu.hpp>
  - <https://raw.githubusercontent.com/ashvardanian/ParallelReductionsBenchmark/a301c39/reduce_cpu.hpp>
  - <https://raw.githubusercontent.com/ashvardanian/ParallelReductionsBenchmark/9a5a61a/README.md>
  - <https://raw.githubusercontent.com/ashvardanian/ParallelReductionsBenchmark/aeabdce/README.md>
  - <https://raw.githubusercontent.com/ashvardanian/ParallelReductionsBenchmark/a301c39/README.md>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/ashvardanian/parallelreductionsbenchmark`) · [data/wave13/enrich/raw/github_com_ashvardanian_parallelreductionsbenchmark.json](../../../data/wave13/enrich/raw/github_com_ashvardanian_parallelreductionsbenchmark.json) (enrichment confidence 0.85)

</details>
