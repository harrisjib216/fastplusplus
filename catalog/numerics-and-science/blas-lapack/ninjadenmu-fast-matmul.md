# fast_matmul (NinjadenMu; didactic BLIS-style SGEMM for Apple M4)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [BLAS and LAPACK](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C` · `no license` · 🟢 active

> Seven-step NEON SGEMM tutorial for Apple M4; single-thread ties NumPy/OpenBLAS, OpenMP version about 1.5x ahead.

| | |
|---|---|
| **Beats** | OpenBLAS as called through NumPy (float32 A @ B in scripts/openblas.py) |
| **Claimed result** | README text: the single-threaded BLIS-style implementation is 'comparable to an OpenBLAS build targeting Apple Silicon (with the difference being too small for me to reliably measure)' and the multi-threaded one is 'noticeably faster (probably due to better load balancing on my particular M4 spec)'; '\~200x faster (40x faster with just one thread)' is against the project's own naive loop, not OpenBLAS. Read by eye from plots/plot.png: single-threaded OpenBLAS reaches n=3100 at about 4.55 s cumulative versus single-threaded BLIS-style n=3000 at about 4.08 s, and the two curves overlap point for point (parity). Multi-threaded BLIS-style reaches n=4500 at about 4.08 s versus multi-threaded OpenBLAS n=4200 at about 4.7 s; cumulative time to reach n=4200 is about 3.1 s versus about 4.7 s, roughly 1.5x (derived from page data, read by eye). The per-step times at n=3000 (about 0.5 s) imply roughly 100-120 GFLOPS single-threaded for both sides (derived from page data, read by eye). |
| **Workload** | Square float32 matrix multiplication for n = 100, 200, 300, ... each run once until a cumulative 5 s budget is used (scripts/driver.py), custom BLIS-style code versus NumPy with OPENBLAS_NUM_THREADS=1 and with default threads. |
| **Metric** | throughput |
| **Hardware** | Apple M4 (README: 'my Apple M4'); core configuration and RAM not stated. |
| **Compiler and flags** | Makefile: clang -O3 -ffast-math -march=native (commented alternative -mcpu=apple-m4), OpenMP via Homebrew libomp, -fno-vectorize on the early didactic versions. The clang version is not stated and neither are the NumPy or OpenBLAS versions. |
| **Adoption** | 0 stars, 0 forks; same author as MuBLIS (which is already on the known list) |
| **Last commit** | 2026-07-29 |
| **Links** | [repository](https://github.com/NinjadenMu/fast_matmul) · [benchmark](https://github.com/NinjadenMu/fast_matmul) |

## Verdict

On one Apple M4 (core count unstated) with clang -O3 -ffast-math -march=native, the single-thread BLIS-style kernel tracks single-thread NumPy A @ B (unversioned OpenBLAS) point for point in a 'largest n reached within a cumulative 5 s' plot, and the OpenMP version reaches n=4200 in about 3.1 s versus about 4.7 s for multi-threaded NumPy, roughly 1.5x (derived from page data, read by eye). The harness favors the custom side (warm-up run and preallocated buffers there; NumPy timed once in a fresh process with the result allocated inside the timed region), takes one sample per n, and never compares against Accelerate.

## Use it when

- Learning how a single-core SGEMM goes from a naive i-j-k loop to near-OpenBLAS speed, one optimization per file, on an Apple Silicon Mac.
- Reading a compact, commented example of a 12x8 FP32 NEON micro-kernel with BLIS-style packing routines before writing your own.
- Experimenting with cache block sizes on M-series chips: mc, nc and kc are runtime environment variables and scripts/tuner.py searches them.
- Studying how OpenMP dynamic scheduling of the jr loop behaves on heterogeneous P/E-core Apple chips.

## Skip it when

- Any code you need to ship or copy: the repository has no LICENSE file, so default copyright applies.
- Real BLAS workloads: square n x n only, float32 only, column-major only, no transposes, no alpha/beta, no leading dimensions, no FP64 or complex.
- Peak FP32 on M4: the implied rate is roughly 100-120 GFLOPS per core on NEON, while OpenBLAS issue #6073 reports 1127-1185 GFLOPS single-thread for Apple Accelerate (AMX/SME) on an M4 Pro, about ten times more.
- Non-Arm targets: the kernels include arm_neon.h and the Makefile assumes Homebrew libomp, so x86 needs new AVX kernels and retuned block sizes (README).
- Anything needing checked numerics: the code is compiled with -ffast-math and the repository has no correctness test against a reference result.

## How it is fast

The last two stages follow the Goto/BLIS five-loop algorithm: jc/pc/ic loops cut B and A into nc x kc and mc x kc panels that are packed contiguously in micro-kernel access order (fewer TLB misses, full cache lines), and a 12x8 register-blocked micro-kernel keeps 24 NEON float32x4 accumulators live while doing kc rank-1 updates with vfmaq_n_f32 (FMA against a broadcast B scalar). The parallel stage splits the jr sliver loop across OpenMP threads with schedule(dynamic), which the author's commit says balances work between the M4's performance and efficiency cores better. Everything is built with clang -O3 -ffast-math -march=native and full unrolling pragmas.

## Compared with alternatives

Pick fast_matmul only for its stage-by-stage tutorial; for reusable routines take the same author's MuBLIS (config-driven BLIS-style library, GEMM 111.0 vs OpenBLAS 109.9 GFLOP/s single-thread on M4), and for top Apple M4 speed take MaxMulSK (Apache-2.0, about 123 GFLOP/s NEON and SME kernels near 2 TFLOP/s) or Accelerate.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | arm_neon.h; OpenMP (Homebrew libomp, located via brew --prefix) for the parallel stage; Python with NumPy, matplotlib and tqdm for the benchmark and tuner scripts |
| **Minimum toolchain** | clang (uses #pragma clang loop unroll(full) and -mllvm flags); C99 restrict; exact clang version not documented |
| **Platforms** | aarch64 with NEON; tested only on an Apple M4 under macOS |
| **Thread safety** | matmul_blis and matmul_parallel cache mc/nc/kc in function-static variables set on the first call without synchronization, so concurrent first calls race; after that each call allocates its own packing buffers. |
| **Drop-in for the baseline** | no |

## Gotchas

- Computes C += A\*B and assumes C starts at zero; utils/bench.c zeroes C once and then calls the kernel for a warm-up plus the timed runs without re-zeroing, so the benchmark never checks the result.
- Block sizes come from environment variables literally named mc, nc and kc (defaults 3300, 4096, 2048, checked only by assert), so an unrelated variable with one of those names changes behavior.
- Every call posix_memaligns packing buffers sized mc\*kc and nc\*kc floats (about 27 MB and 34 MB at the defaults) regardless of n, and leaks the A buffer if the B allocation fails.
- Rows or columns that do not fill a full 12x8 tile (for example the last 4 rows when n=100) fall back to an unpacked scalar triple loop, so sizes that are not multiples of 12 and 8 lose speed at the edges.

## Known shortcomings

- Tier C: single-thread parity with OpenBLAS and about 1.5x cumulative multi-thread, read by eye from plots/plot.png. The harness is asymmetric (warm-up only on the custom side, one sample per size, output allocated inside the timed NumPy call) and the OpenBLAS build behind NumPy is unknown; OpenBLAS issue #6073 shows Accelerate and SME-enabled OpenBLAS far faster on M4. No license, 0 stars.
- No LICENSE. The kernel computes C += A\*B, the bench never re-zeroes C and the repo has no correctness test. Block sizes are read from environment variables named mc/nc/kc; each call allocates about 61 MB of packing buffers whatever n is. The parallel win likely comes from P/E-core scheduling (commit 'dynamic balances between P/E cores better').

## Caveats and trade-offs

The benchmark treats the two sides unequally. The custom side runs ./bench with one untimed warm-up call and then one timed call on already-allocated, already-touched buffers (C is zeroed once before the warm-up and not re-zeroed; utils/bench.c). The baseline times a single NumPy A @ B call in a fresh Python process with no warm-up and with the result matrix allocated inside the timed region (scripts/openblas.py). There is one measurement per n, no repeats or variance, the metric is 'largest n within a cumulative time budget' rather than GFLOPS, and the custom code is built with -ffast-math. The README does not say which NumPy or OpenBLAS build was used; because OPENBLAS_NUM_THREADS=1 changes the baseline curve and the implied single-thread rate is about 110 GFLOPS, the baseline was evidently a NEON-path OpenBLAS rather than Apple Accelerate (inferred, not stated). OpenBLAS issue #6073 (2026-09-29, Apple M4 Pro, OpenBLAS develop 63d7f22) reports 707-766 GFLOPS single-thread OpenBLAS SGEMM and 1127-1185 GFLOPS for Accelerate, so the platform's fastest BLAS (Accelerate/SME) and SME-enabled OpenBLAS were not compared and would likely beat this NEON code by a wide margin. Parity is the only single-thread result, and the author attributes the multi-thread gap to load balancing on his particular M4, which may be a P/E-core scheduling artifact. Numbers are read by eye from the plot image. The author's deep-dive post on ninjadenmu.github.io is egress-blocked. No license (no LICENSE file, none in the GitHub sidebar).

Teaching code: float32 only, square matrices only, column-major, no transposes or alpha/beta and no BLAS interface. ARM NEON intrinsics (Apple Silicon only; the README says x86 needs retuned block sizes and AVX kernels). Fixed 12x8 register tile, cache block sizes tuned by scripts/tuner.py, OpenMP dynamic scheduling for the parallel version. No LICENSE file, so the code cannot be copied.

## Maintenance

Active hobby project (45 commits, last 2026-07-29, 0 stars) with no license, so read it rather than vendor it; Apple Silicon only.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** plots/plot.png (generated by scripts/driver.py, which times utils/bench.c against scripts/openblas.py, NumPy A @ B with and without OPENBLAS_NUM_THREADS=1) shows the record's readings, and the Makefile gives clang -O3 -ffast-math -march=native on an Apple M4. Held at C rather than A because the baseline build is unidentified (no NumPy or OpenBLAS version, no requirements file, no clang version) and the harness is asymmetric (warm-up only on the custom side, result allocation inside the timed region on the NumPy side, one sample per n), so the comparison is not fully reproducible.
- **Verifier notes:** Record is accurate: plot, scripts, Makefile, metadata (0 stars, 0 forks, 45 commits, last commit 2026-07-29, no license) all match. Kept at C because the baseline build is unidentified and the timing harness favors the custom side; the only win is multi-threaded and against an apparently NEON-only OpenBLAS, while Accelerate and SME-enabled OpenBLAS are several times faster on M4-class chips per OpenBLAS issue #6073.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/NinjadenMu/fast_matmul>
  - <https://github.com/NinjadenMu/fast_matmul/commits/main>
  - <https://raw.githubusercontent.com/NinjadenMu/fast_matmul/HEAD/README.md>
  - <https://raw.githubusercontent.com/NinjadenMu/fast_matmul/HEAD/Makefile>
  - <https://raw.githubusercontent.com/NinjadenMu/fast_matmul/HEAD/utils/bench.c>
  - <https://raw.githubusercontent.com/NinjadenMu/fast_matmul/HEAD/scripts/driver.py>
  - <https://raw.githubusercontent.com/NinjadenMu/fast_matmul/HEAD/scripts/openblas.py>
  - <https://raw.githubusercontent.com/NinjadenMu/fast_matmul/HEAD/plots/plot.png>
  - <https://github.com/OpenMathLib/OpenBLAS/issues/6073>
- **Sources the enricher read:**
  - <https://github.com/NinjadenMu/fast_matmul>
  - <https://github.com/NinjadenMu/fast_matmul/tree/main/src>
  - <https://github.com/NinjadenMu/fast_matmul/commits/main>
  - <https://raw.githubusercontent.com/NinjadenMu/fast_matmul/HEAD/README.md>
  - <https://raw.githubusercontent.com/NinjadenMu/fast_matmul/HEAD/Makefile>
  - <https://raw.githubusercontent.com/NinjadenMu/fast_matmul/HEAD/utils/bench.c>
  - <https://raw.githubusercontent.com/NinjadenMu/fast_matmul/HEAD/utils/env.c>
  - <https://raw.githubusercontent.com/NinjadenMu/fast_matmul/HEAD/include/matmul.h>
  - <https://raw.githubusercontent.com/NinjadenMu/fast_matmul/HEAD/src/matmul_blis.c>
  - <https://raw.githubusercontent.com/NinjadenMu/fast_matmul/HEAD/src/matmul_parallel.c>
  - <https://raw.githubusercontent.com/NinjadenMu/fast_matmul/HEAD/src/matmul_vectorized.c>
  - <https://raw.githubusercontent.com/NinjadenMu/fast_matmul/HEAD/scripts/driver.py>
  - <https://raw.githubusercontent.com/NinjadenMu/fast_matmul/HEAD/scripts/openblas.py>
  - <https://raw.githubusercontent.com/NinjadenMu/fast_matmul/HEAD/scripts/tuner.py>
  - <https://raw.githubusercontent.com/NinjadenMu/fast_matmul/HEAD/plots/plot.png>
  - https://raw.githubusercontent.com/NinjadenMu/fast_matmul/HEAD/LICENSE (404)
  - <https://github.com/UlasSertan/MaxMulSK>
  - https://github.com/OpenMathLib/OpenBLAS/issues/6073 (search result snippet only)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/ninjadenmu/fast_matmul`) · [data/wave8/enrich/raw/github_com_ninjadenmu_fast_matmul.json](../../../data/wave8/enrich/raw/github_com_ninjadenmu_fast_matmul.json) (enrichment confidence 0.8)

</details>
