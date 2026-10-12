# Laser (GEMM)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [BLAS and LAPACK](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Nim` · `Apache-2.0` · 🟡 stale

> Nim BLAS-style GEMM with strided and int32/int64 support; roughly at parity with OpenBLAS, not reliably faster.

| | |
|---|---|
| **Beats** | OpenBLAS |
| **Claimed result** | README: 'It reaches 98% of OpenBLAS speed on float64 when multithreaded and 102% when single-threaded; 97% of OpenBLAS speed on float32 when multithreaded and 99% when single-threaded.' The recorded run in gemm_bench_float32.nim (1920x1920x1920, OpenMP, i9-9980XE) shows Laser 1874.1 GFLOP/s vs OpenBLAS 1732.2 GFLOP/s (about 1.08x, derived from page data) and MKL-DNN JIT AVX512 1737.3 GFLOP/s; the recorded run in gemm_bench_float64.nim (960x960x960, OpenMP) shows Laser 441.5 vs OpenBLAS 543.4 GFLOP/s by mean time (about 0.81x, derived from page data), though Laser's minimum time is lower (2.232 vs 2.910 ms) and its stddev is high (5.1 ms on a 4.0 ms mean). |
| **Workload** | Strided multithreaded and single-threaded float32/float64 matrix multiplication relative to OpenBLAS (benchmark program benchmarks/gemm in the repo). |
| **Metric** | throughput |
| **Hardware** | Intel Core i9-9980XE (Skylake-X, 18 cores) overclocked to 4.1 GHz all-core turbo, 4.0 GHz AVX, 3.5 GHz AVX-512 (bench file comments) |
| **Compiler and flags** | nim cpp -r -d:release -d:danger -d:openmp (from the float32 bench file); Nim version, backend C++ compiler and OpenBLAS version not stated |
| **Adoption** | 295 stars, 14 forks, 401 commits |
| **Last commit** | 2024-01-04 |
| **Links** | [repository](https://github.com/mratsim/laser) · [benchmark](https://raw.githubusercontent.com/mratsim/laser/HEAD/benchmarks/gemm/gemm_bench_float32.nim) |

## Verdict

The README claims 97-102% of OpenBLAS speed (float32 and float64, single- and multi-threaded) without stating sizes or versions. Recorded runs in the bench files on an overclocked 18-core i9-9980XE (nim cpp -d:release -d:danger -d:openmp, OpenBLAS version unstated) give Laser 1874 vs OpenBLAS 1732 GFLOP/s by mean time at 1920^3 float32, but 442 vs 543 at 960^3 float64, and the author's later open issue #40 reports about 1011 vs 1499 GFLOP/s at 1920^3; this is parity at best, not a speedup.

## Use it when

- Nim code, or Arraymancer users, who want a GEMM with no external BLAS dependency that lands within a few percent of OpenBLAS on large square float32/float64 matrices on x86-64.
- Strided or sliced operands (for example A[0::2, :] during cross-validation) that you want to multiply without materialising a contiguous copy first.
- Integer GEMM (int32, int64) with SSE2/SSE4.1/AVX2/AVX-512 kernels on x86, which most BLAS libraries do not provide.
- As readable reference code for a macro-generated, BLIS-style micro-kernel design that is easy to extend to a new SIMD set.

## Skip it when

- You want a faster BLAS from C++: the README claims only 97-102% of OpenBLAS, the author's open issue #40 later measured about 1011 vs 1499 GFLOP/s for OpenBLAS at 1920^3, and there is no BLAS ABI, so using it means compiling Nim and exporting a C function.
- ARM/aarch64 or any non-x86 target: there is no NEON micro-kernel (marked TODO in gemm_tiling.nim), so other architectures get the generic scalar kernel.
- Small matrices or many repeated calls: there is no small-GEMM path or pre-packing (both listed as future work in the README), and every call allocates fresh pack buffers sized kc x N for B plus one mc x kc block per M tile for A.
- Multi-socket servers or CPUs whose caches differ from the author's desktop: block sizes are hard-coded and N is not partitioned per socket; issue #10 (December 2018, dual Xeon Gold 6154, 2304^3) recorded Intel MKL at 4 TFLOPS against Laser at 600 GFLOPS.
- Anything needing a stable, packaged dependency: the README calls the library unstable and in heavy development, it was never published on nimble, and the repository has been idle since January 2024.

## How it is fast

It follows the Goto/BLIS blocking scheme: for each kc slice of K it packs a kc x N panel of B, each OpenMP thread packs its own mc x kc block of A, and a GEBP macro-kernel drives a register-blocked mr x nr micro-kernel over the packed data. The micro-kernels are emitted by a Nim macro (ukernel_generator) from SIMD intrinsic templates for SSE, SSE2, SSE4.1, AVX, AVX+FMA, AVX2 and AVX-512, and the kernel is picked at runtime with cpuinfo. Parallelism is OpenMP over the ic (M) loop, enabled only when M\*N\*K exceeds a per-kernel threshold. Blocking sizes are fixed constants (mc = 768 bytes / sizeof(T), kc = 2048 bytes / sizeof(T)), and N is not split at all (nc = N).

## Compared with alternatives

Pick Laser only inside Nim or Arraymancer, or when you need integer or arbitrarily strided GEMM on x86. For raw speed from C or C++, use OpenBLAS itself, Eigen, or BLASFEO for small matrices; Octavian.jl is the closest pure-language GEMM sibling and publishes larger measured wins over OpenBLAS.

## Integration

| | |
|---|---|
| **Form** | source-drop (Nim modules; not published on nimble) |
| **Dependencies** | Nim compiler plus a C or C++ backend compiler; bundled Facebook cpuinfo (BSD-2-Clause) for x86 feature detection; OpenMP (enabled with -d:openmp) for multithreading |
| **Minimum toolchain** | Nim &gt;= 0.19.2 per laser.nimble; the benchmark was built with nim cpp -d:release -d:danger -d:openmp. Compatibility with current Nim releases is not documented. |
| **Platforms** | x86 and x86-64 with SIMD kernels from SSE to AVX-512 chosen at runtime; other architectures fall back to a generic kernel |
| **Thread safety** | not documented; each gemm_strided call allocates its own pack buffers (newTiles), and the call itself parallelises internally with OpenMP |
| **Drop-in for the baseline** | no |

## Gotchas

- Multithreading only exists when built with -d:openmp; otherwise the OpenMP templates fall back to plain loops. In open issue #23 a user's 100 x 1000^3 run took 5.4 s wall at 99% CPU against 1.84 s for NumPy.
- Argument order is M, N, K followed by alpha, then each matrix as pointer, row stride, column stride; issue #23 asks for this to be documented, and the README does not spell it out.
- Open issue #22 reports a clang build error ('always_inline function _mm256_setzero_pd requires target feature xsave') when compiling gemm_strided, with no reply.
- The author notes 'strange OpenMP interferences' between Laser and OpenBLAS in one process (issue #40), and the recorded benchmark runs use 10 samples with a standard deviation as large as the mean time, so single-run comparisons swing either way.

## Known shortcomings

- README says parity but its bench files disagree (float32 1.08x faster than OpenBLAS, float64 0.81x); Nim.
- Not faster than OpenBLAS on current code: the author's own open issue #40 shows \~1011 vs \~1499 GFLOP/s at 1920^3 (unexplained regression), contradicting the README's 97-102% claim. Issue #10: dual Xeon 6154, MKL 4 TFLOPS vs Laser 600 GFLOPS. No NEON kernel; Clang build error (#22). Arraymancer vendors a maintained copy of the GEMM (src/arraymancer/laser).

## Caveats and trade-offs

Essentially parity with OpenBLAS: the README's only win is 2% (float64, single thread); one recorded float32 multithreaded run shows Laser about 8% ahead of OpenBLAS, while the recorded float64 multithreaded run shows it about 19% behind by mean time. Each run uses 10 samples on one overclocked desktop CPU, with OpenBLAS version and compiler versions unstated. Written in Nim (C++ backend), not a drop-in BLAS ABI. The value is the int32/int64 GEMM and strided-matrix support. Last commit January 2024.

Nim library (CPU backend of Arraymancer) with its own multithreaded BLAS-like gemm: supports strided matrices and int32/int64 SIMD gemm (SSE2, AVX2), extendable to NEON/AVX512. Nim API, not a BLAS ABI; usable from C++ only through Nim's C backend.

## Maintenance

Stale since January 2024 and never released on nimble, but Apache-2.0 and small enough to vendor; Arraymancer vendors this GEMM under src/arraymancer/laser, which still received commits from 2024 to January 2026.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party numbers: README states 97-102% of OpenBLAS, and the bench files (benchmarks/gemm/gemm_bench_float32.nim, gemm_bench_float64.nim) record runs on an overclocked i9-9980XE with the nim command line, but the Nim version, backend C++ compiler and OpenBLAS version are not stated, so C.
- **Verifier notes:** README text matches the record. Recorded bench-file runs found and added; they disagree in direction between float32 and float64. Apache-2.0, 295 stars, last commit 2024-01-04 confirmed (stale).
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/mratsim/laser/HEAD/README.md>
  - <https://raw.githubusercontent.com/mratsim/laser/HEAD/LICENSE>
  - <https://github.com/mratsim/laser/tree/master/benchmarks/gemm>
  - <https://raw.githubusercontent.com/mratsim/laser/HEAD/benchmarks/gemm/gemm_bench_float32.nim>
  - <https://raw.githubusercontent.com/mratsim/laser/HEAD/benchmarks/gemm/gemm_bench_float64.nim>
  - <https://github.com/mratsim/laser>
  - <https://github.com/mratsim/laser/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/mratsim/laser/HEAD/README.md>
  - <https://raw.githubusercontent.com/mratsim/laser/HEAD/laser.nimble>
  - <https://raw.githubusercontent.com/mratsim/laser/HEAD/benchmarks/gemm/gemm_bench_float32.nim>
  - <https://raw.githubusercontent.com/mratsim/laser/HEAD/benchmarks/gemm/gemm_bench_float64.nim>
  - <https://raw.githubusercontent.com/mratsim/laser/HEAD/laser/primitives/matrix_multiplication/gemm.nim>
  - <https://raw.githubusercontent.com/mratsim/laser/HEAD/laser/primitives/matrix_multiplication/gemm_tiling.nim>
  - <https://raw.githubusercontent.com/mratsim/laser/HEAD/laser/primitives/matrix_multiplication/gemm_ukernel_dispatch.nim>
  - <https://raw.githubusercontent.com/mratsim/laser/HEAD/laser/openmp.nim>
  - <https://github.com/mratsim/laser>
  - <https://github.com/mratsim/laser/tree/master/laser/primitives/matrix_multiplication>
  - <https://github.com/mratsim/laser/issues?q=is%3Aissue+gemm>
  - <https://github.com/mratsim/laser/issues/40>
  - <https://github.com/mratsim/laser/issues/23>
  - <https://github.com/mratsim/laser/issues/22>
  - <https://github.com/mratsim/laser/issues/10>
  - <https://raw.githubusercontent.com/mratsim/Arraymancer/HEAD/src/arraymancer/laser/primitives/matrix_multiplication/gemm.nim>
  - <https://github.com/mratsim/Arraymancer/commits/master/src/arraymancer/laser>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/mratsim/laser`) · [data/wave8/enrich/raw/github_com_mratsim_laser.json](../../../data/wave8/enrich/raw/github_com_mratsim_laser.json) (enrichment confidence 0.75)

</details>
