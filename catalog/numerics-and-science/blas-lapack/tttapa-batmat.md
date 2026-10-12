# batmat (batched small-matrix linear algebra)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [BLAS and LAPACK](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `LGPL-3.0` · 🟢 active

> C++20 SIMD kernels for batches of same-shape small matrices (gemm, syrk, trsm, trtri, Cholesky); claims wins over per-matrix MKL, OpenBLAS and BLASFEO, with no published numbers.

| | |
|---|---|
| **Beats** | Intel MKL and OpenBLAS (per-matrix BLAS/LAPACK calls via the BLAS interface), BLASFEO |
| **Claimed result** | README gives no numbers: 'Batmat performs exceptionally well on matrices smaller than around 100x100 (that fit in the L2 cache), where it outperforms traditional scalar linear algebra libraries such as Intel MKL, OpenBLAS, and BLASFEO (especially for triangular or symmetric matrices).' |
| **Workload** | Batches (depth 8) of small dense matrices, sizes 1 to 1024, for gemm, syrk, trmm, trsm, trtri, potrf, syrk-potrf, QR and others, single-threaded (OMP_NUM_THREADS=1, taskset -c 0), batmat interleaved SIMD kernels versus per-matrix calls of BLAS libraries, BLASFEO and Eigen; benchmark source only, no published results. |
| **Metric** | throughput |
| **Compiler and flags** | GCC 14 or later required (Clang and ICX supported); SIMD flags come from the user's Conan profile (scripts/dev/profiles); benchmark target run with Google Benchmark --benchmark_min_time=0.1s, 3 repetitions, random interleaving. Actual flags of the author's runs are not published. |
| **Adoption** | 3 stars; linear-algebra backend of the Cyqlone optimal-control solver (kul-optec/cyqlone) |
| **Last commit** | 2026-06-15 |
| **Links** | [repository](https://github.com/tttapa/batmat) · [benchmark](https://github.com/tttapa/batmat) |

## Verdict

Nothing measured is published. The README says batmat beats Intel MKL, OpenBLAS and BLASFEO below about 100x100, especially for triangular and symmetric matrices. The repo's Google Benchmark harness (one core via taskset -c 0, OMP_NUM_THREADS=1, batch depth 8, sizes 1 to 1024) times batmat against per-matrix LAPACK/BLAS through guanaqo, per-matrix BLASFEO and Eigen LLT, but no CPU, compiler flags or result files are given. In the BLAS path the potrf loop calls PauseTiming/ResumeTiming around a copy for every matrix, which adds timer overhead to the baseline at tiny sizes. The Cyqlone paper abstract (search snippet only) says the batched routines 'significantly outperform BLAS and BLASFEO' for optimal-control-sized matrices, with no figures seen.

## Use it when

- Stage-wise structured problems such as Riccati recursions, multiple-shooting optimal control (its main user is the Cyqlone solver), batched Kalman filters or many small least-squares systems, where you have at least one SIMD width (4 or 8 doubles) of same-shape matrices per operation
- Matrices below roughly 100x100 (the README's L2-cache bound), especially triangular and symmetric work (potrf, syrk+potrf, trsm, trtri), where per-matrix BLAS/LAPACK calls are dominated by call overhead and poor vector utilization
- x86-64 builds with AVX2 or AVX-512 enabled through compiler flags and GCC 14+, Clang or ICX, where you control the toolchain and can ship ISA-specific binaries (Cyqlone ships separate AVX2 and AVX-512 builds)
- Code that can keep data in batmat's interleaved layout across a whole algorithm, so the cost of converting to and from ordinary column-major storage is paid once

## Skip it when

- Single matrices, or batches whose matrices have different sizes: the layout needs one shape per batch and pads the batch depth up to a multiple of the batch size
- Medium and large matrices: cache sizes are hard-coded (48 KiB L1, 512 KiB L2, 16 MiB L3, 8 cores, marked TODO), and gemmt, trmm and potrf have no cache blocking, so MKL or OpenBLAS are the better choice above about 100x100
- When you need a measured speedup: no result files, CPU model or numbers are published, and the harness compares batched kernels with per-matrix LAPACK/BLAS calls (MKL or OpenBLAS through guanaqo), per-matrix BLASFEO and Eigen LLT, not with MKL's compact/batched API
- MSVC, Apple Clang or locked-down toolchains: the SIMD layer needs libstdc++'s &lt;experimental/simd&gt; or the GSI-HPC simd library, the build uses Conan with recipes from the author's own remote, and CI covers only GCC 16 on Ubuntu x86-64
- Input that may not be positive definite: potrf returns void with no LAPACK-style info code, and pivots go unchecked into sqrt/rsqrt, so failures show up as NaN or inf (an optional regularization argument adds to the diagonal)

## How it is fast

Batch-wise vectorization: each SIMD lane holds a different matrix, so even a 3x3 Cholesky uses full vectors and has no horizontal shuffles or per-call dispatch overhead, and independent lanes expose instruction-level parallelism. Fully unrolled register-blocked micro-kernels (3x3 accumulator tiles on AVX2, 5x5 on AVX-512, 4x4 on NEON) are reached through compile-time lookup tables indexed by the remainder size, and several operations are fused (syrk+potrf, gemm with diagonal scaling). The Cholesky kernel computes sqrt and an rsqrt (hardware estimate plus Newton steps on AVX2 float and AVX-512) in parallel, so the pivot division leaves the critical path. Larger gemm calls fall back to BLIS-style cache tiling with packing of A and B.

## Compared with alternatives

Pick batmat over BLASFEO when you have many same-size matrices to process in lockstep rather than one small matrix at a time; BLASFEO has published per-matrix wins and a stable C API. cbk is the sibling with measured wins over MKL's compact (batched) kernels, the fair baseline batmat has not been publicly measured against, so prefer cbk's evidence if the routines you need overlap and batmat's C++20 API and fused Cholesky variants if they do not.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | guanaqo (the author's utility library, from his Conan remote); optional OpenMP (off by default) and GSI-HPC/simd; benchmarks also need Google Benchmark, hyhound, a BLAS/LAPACK (MKL in the dev profile), and optionally BLASFEO and Eigen |
| **Minimum toolchain** | C++20 (concepts, designated initializers, ranges); GCC 14+ per README, Clang (older versions need -o with_gsi_hpc_simd=True) or Intel ICX; CMake 3.24+; Conan recommended. Shared library is a Conan option |
| **Platforms** | x86-64 with AVX2 or AVX-512, ARM NEON (register sizes tuned on a Cortex-A53), generic fallback; the ISA is fixed at compile time from __AVX512F__/__AVX2__/__ARM_NEON with no runtime dispatch. Default instantiation is double only, with vector lengths 1, 4 and 8 on x86 |
| **Thread safety** | not documented for the linear-algebra routines (they are free functions on caller-owned views); the deprecated global thread pool helpers lock a mutex; OpenMP parallelism is opt-in via BATMAT_WITH_OPENMP |
| **Drop-in for the baseline** | no |

## Gotchas

- Dimension checks use BATMAT_ASSERT, which throws std::logic_error even in release builds, while kernel-level BATMAT_ASSUME conditions become [[assume]]/unreachable (undefined behavior if violated) under NDEBUG unless BATMAT_VERIFY_ASSUMPTIONS is on
- Results differ from LAPACK in the last bits: micro-kernels are built with -ffp-contract=fast, and Cholesky inverse pivots use rsqrt estimates refined by Newton steps (two for double and one for float on AVX-512, one for float on AVX2)
- SIMD flags come from your Conan profile; without them you get the generic 3x3 path. float support requires BATMAT_DTYPES to include it (default is double only), and every dtype/vector-length/storage-order combination is a separate instantiation, so build time and binary size grow
- Structure is explicit: potrf writes only the tril() part of the output, and the README example zeroes triu(L) with la::fill first. LGPL-3.0-or-later, and the Conan default is a static library, which brings LGPL relinking obligations

## Known shortcomings

- Verifier rejected as not notable at tier D: 3 stars and a speed claim without numbers.
- Claim has no numbers; baseline is per-matrix LAPACK/BLAS, not MKL compact. The BLAS potrf baseline loop calls PauseTiming/ResumeTiming for every matrix, adding timer overhead to the baseline at tiny n. potrf has no info code (NaN on non-positive-definite input). gemmt/trmm/potrf have no cache blocking; cache sizes are hard-coded.

## Caveats and trade-offs

The README states a win over MKL, OpenBLAS and BLASFEO but publishes no numbers, no CPU model and no result files (docs/ holds only logos and Doxygen config). The benchmark sources exist (benchmarks/\*.cpp, including benchmarks/mkl/potrf-mkl.cpp) and run the baselines as ordinary per-matrix calls (MKL dpotrf, guanaqo BLAS xgemm) rather than MKL's compact or batched APIs, so the comparison is batched-SIMD against non-batched calls. The Cyqlone paper (Pas and Patrinos, arXiv 2512.09058), whose abstract per a search snippet says batched routines 'significantly outperform BLAS and BLASFEO for the small matrices that arise in optimal control', and a Zenodo benchmark record could not be opened (arXiv and Zenodo blocked), so no numbers are recorded. Very new, 3 stars.

Data must be stored in an interleaved 'compact' layout (one SIMD lane per matrix of the batch), so it helps only when many same-sized small matrices are processed together (for example stages of an optimal control problem) and is not a drop-in replacement for single-matrix BLAS. Needs GCC 14+ (or Clang with the GSI-HPC simd library, or ICX), Conan and the guanaqo dependency. LGPL-3.0 licence. Routines include gemm, syrk, trmm, trsm, potrf, trtri and fused variants.

## Maintenance

Active but pre-1.0 (v0.0.24, last commit 2026-06-15, 743 commits, 3 stars, single maintainer); LGPL-3.0-or-later and copyable, but in practice tied to the author's Conan ecosystem (guanaqo, custom recipes), so expect API churn.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): reject; tier before verification D, tier now D.
- **Tier reason:** README only states that batmat 'outperforms traditional scalar linear algebra libraries such as Intel MKL, OpenBLAS, and BLASFEO' below about 100x100; benchmarks/ holds sources (gemm.cpp, potrf.cpp, syrk.cpp, trsm.cpp, mkl/ and others) but no result files, and the Cyqlone paper abstract (search snippet) gives no batmat numbers either.
- **Verifier notes:** Tier D with 3 stars and 0 forks, referenced only by its authors' own Cyqlone solver and paper (arXiv 2512.09058): not notable under the tier-D rule. Metadata confirmed: LGPL-3.0, last commit 2026-06-15 'Version 0.0.24'. If the orchestrator keeps it as a flagged lead, shortcoming: claim without numbers; harness compares batched SIMD kernels with per-matrix (non-batched, non-compact) MKL/BLAS calls.
- **Shortcomings recorded by:** verifier; enrichment
- **Pages the verifier opened:**
  - <https://github.com/tttapa/batmat>
  - <https://github.com/tttapa/batmat/commits>
  - <https://github.com/tttapa/batmat/tree/main/benchmarks>
- **Sources the enricher read:**
  - <https://github.com/tttapa/batmat>
  - <https://github.com/tttapa/batmat/tree/main/src>
  - <https://raw.githubusercontent.com/tttapa/batmat/main/README.md>
  - <https://raw.githubusercontent.com/tttapa/batmat/main/CMakeLists.txt>
  - <https://raw.githubusercontent.com/tttapa/batmat/main/conanfile.py>
  - <https://raw.githubusercontent.com/tttapa/batmat/main/LICENSE>
  - <https://raw.githubusercontent.com/tttapa/batmat/main/src/CMakeLists.txt>
  - <https://raw.githubusercontent.com/tttapa/batmat/main/src/batmat/include/batmat/linalg/gemm.hpp>
  - <https://raw.githubusercontent.com/tttapa/batmat/main/src/batmat/include/batmat/linalg/potrf.hpp>
  - <https://raw.githubusercontent.com/tttapa/batmat/main/src/batmat/include/batmat/linalg/micro-kernels/gemm.hpp>
  - <https://raw.githubusercontent.com/tttapa/batmat/main/src/batmat/include/batmat/linalg/micro-kernels/gemm.tpp>
  - <https://raw.githubusercontent.com/tttapa/batmat/main/src/batmat/include/batmat/linalg/micro-kernels/potrf.tpp>
  - <https://raw.githubusercontent.com/tttapa/batmat/main/src/batmat/include/batmat/linalg/structure.hpp>
  - <https://raw.githubusercontent.com/tttapa/batmat/main/src/batmat/include/batmat/linalg/simdify.hpp>
  - <https://raw.githubusercontent.com/tttapa/batmat/main/src/batmat/include/batmat/matrix/matrix.hpp>
  - <https://raw.githubusercontent.com/tttapa/batmat/main/src/batmat/include/batmat/matrix/layout.hpp>
  - <https://raw.githubusercontent.com/tttapa/batmat/main/src/batmat/include/batmat/matrix/storage.hpp>
  - <https://raw.githubusercontent.com/tttapa/batmat/main/src/batmat/include/batmat/simd.hpp>
  - <https://raw.githubusercontent.com/tttapa/batmat/main/src/batmat/include/batmat/dtypes.hpp>
  - <https://raw.githubusercontent.com/tttapa/batmat/main/src/batmat/include/batmat/assume.hpp>
  - <https://raw.githubusercontent.com/tttapa/batmat/main/src/batmat/include/batmat/thread-pool.hpp>
  - <https://raw.githubusercontent.com/tttapa/batmat/main/src/batmat/include/batmat/ops/rsqrt.hpp>
  - <https://raw.githubusercontent.com/tttapa/batmat/main/src/batmat/include/batmat/platform/platform.hpp>
  - <https://raw.githubusercontent.com/tttapa/batmat/main/src/batmat/include/batmat/platform/avx2.hpp>
  - <https://raw.githubusercontent.com/tttapa/batmat/main/src/batmat/include/batmat/platform/avx-512.hpp>
  - <https://raw.githubusercontent.com/tttapa/batmat/main/src/batmat/include/batmat/platform/neon.hpp>
  - <https://raw.githubusercontent.com/tttapa/batmat/main/src/batmat/include/batmat/platform/generic.hpp>
  - <https://raw.githubusercontent.com/tttapa/batmat/main/src/batmat/src/linalg/micro-kernels/Codegen.cmake>
  - <https://raw.githubusercontent.com/tttapa/batmat/main/benchmarks/CMakeLists.txt>
  - <https://raw.githubusercontent.com/tttapa/batmat/main/benchmarks/potrf.cpp>
  - <https://raw.githubusercontent.com/tttapa/batmat/main/benchmarks/gemm.cpp>
  - <https://raw.githubusercontent.com/tttapa/batmat/main/benchmarks/mkl/potrf-mkl.cpp>
  - <https://raw.githubusercontent.com/tttapa/batmat/main/.github/workflows/linux.yml>
  - <https://raw.githubusercontent.com/tttapa/batmat/main/scripts/dev/profiles/dev>
  - <https://raw.githubusercontent.com/tttapa/guanaqo/main/src/include/guanaqo/assume.hpp>
  - <https://raw.githubusercontent.com/kul-optec/cyqlone/HEAD/README.md>
  - WebSearch: 'Cyqlone Pas Patrinos batched linear algebra ... 2512.09058' (arxiv abstract snippet; arxiv.org and lacuna.tiptreesystems.com egress-blocked)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/tttapa/batmat`) · [data/wave8/enrich/raw/github_com_tttapa_batmat.json](../../../data/wave8/enrich/raw/github_com_tttapa_batmat.json) (enrichment confidence 0.65)

</details>
