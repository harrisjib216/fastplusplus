# cbk (Compact Batch Kernels)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [BLAS and LAPACK](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Batched QR, Cholesky and unpivoted LDL^T solves for thousands of small matrices in interleaved layout; beats per-matrix LAPACKE and matches or beats MKL compact.

| | |
|---|---|
| **Beats** | Intel MKL compact kernels (mkl_dgeqrf_compact, mkl_dpotrf_compact, mkl_dtrsm_compact pipeline) and per-matrix LAPACKE (LAPACKE_dgels, LAPACKE_dposv, LAPACKE_dgeqrf) |
| **Claimed result** | QR solve (1000 matrices, n=10..120, 1 RHS): cbk gels 2.7x geometric mean over LAPACKE_dgels (1.5x at n=100) and cbk-batch 1.25x over MKL-batch; at 64 RHS the gels win drops to 1.3x and cbk-batch to 1.12x over MKL. SPD solve (512 matrices, 1 RHS): fused compact solve 2-9x over LAPACKE_dposv at orders 8-48, 1.4-2.2x at 60-105, geometric mean 1.7x, level with MKL's compact pipeline (0.9-1.0x geomean). |
| **Workload** | Batched QR, Cholesky and unpivoted LDL^T factorizations and solves for pools of many small double-precision matrices (n=10..120) in the compact interleaved layout, one thread. |
| **Metric** | throughput |
| **Hardware** | '4-core AVX-512 container' (CPU model not stated) |
| **Compiler and flags** | gcc -O3 -march=native (CMake Release); MKL compact paths linked against sequential MKL, all paths driven with the same thread count |
| **Adoption** | 1 star |
| **Last commit** | 2026-09-15 |
| **Links** | [repository](https://github.com/ivan-pi/cbk) · [benchmark](https://github.com/ivan-pi/cbk/blob/main/examples/BENCHMARKS.md) |

## Verdict

First-party, labelled 'indicative', on a '4-core AVX-512 container' (CPU model not named), gcc -O3 -march=native, sequential MKL for its compact kernels and LAPACKE, all paths given the same thread count, and pack/unpack not timed. One-call gels was 2.7x faster than LAPACKE_dgels (geomean over n=10..120, 1000 matrices, 1 RHS; 1.3x at 64 RHS), and the open three-step chain beat MKL's compact chain by 1.12-1.25x. The fused SPD solve ran 2-9x faster than LAPACKE_dposv at orders 8-48 and only matched MKL's compact pipeline (0.9-1.0x geomean).

## Use it when

- Thousands of independent same-sized dense systems of order roughly 8-120 (per-element FEM/DG blocks, small least-squares fits, Kalman updates, batched local solves) on x86-64 with AVX2 or AVX-512
- You already use MKL's Compact API (mkl_?geqrf_compact, mkl_?potrf_compact) and need the missing pieces: apply/form Q, a Cholesky or LDL^T solve, or a one-call batched gels
- SPD or diagonally dominant / well-behaved symmetric indefinite systems, where unpivoted Cholesky or LDL^T is numerically safe
- One-RHS or few-RHS solves: the gels win over per-matrix LAPACKE_dgels is 2.7x geomean at nrhs=1 and narrows to 1.3x at nrhs=64
- You want a dependency-free library (only CMake &gt;= 3.28 and a C++17 GCC/Clang) that you can build with -march=native

## Skip it when

- Matrices of order above about 128: per-matrix LAPACK pulls ahead from roughly n=128-168 (0.25x at n=256 for the SPD solve) because the compact kernels are unblocked
- Matrices that need pivoting: there is no column-pivoted QR, the LDL^T is unpivoted (no Bunch-Kaufman), and rank deficiency or a non-SPD input is not reported (that lane silently becomes Inf/NaN)
- Badly scaled or ill-conditioned inputs: there is no LAPACK dlarfg-style overflow/underflow rescaling (listed as a known limitation)
- Mixed sizes, complex numbers or GPUs: one size per call, real s/d only, CPU only
- Production code that needs a long track record: v0.2.0 (2026-09-15), 1 star, mostly written by Claude models with human review per the README, and the API is still changing (0.2.0 broke ?ormqr's signature)

## How it is fast

It uses SIMD across matrices instead of within one: V independent factorizations run in lockstep, one vector lane per matrix, so small n never starves the vector unit and no lane masks are needed. The kernels are vectorized unblocked LAPACK algorithms (geqr2 with a branch-free larfg, potf2, a square-root-free potf2 for LDL^T, a register-tiled blocked LDL^T update), written once with GNU vector types and lowered to SSE, AVX or AVX-512. The fused drivers (?posv, ?sysvnp, ?gels) factor and solve each group of V matrices while it is still in cache instead of streaming the pool through separate passes. OpenMP threads the loop over groups.

## Compared with alternatives

Pick cbk over BLASFEO when you have many independent small systems of one size to factor or solve at once; BLASFEO speeds up one small matrix at a time (panel-major, chained operations such as Riccati recursions) and offers more of BLAS/LAPACK. The small-GEMM siblings (LibShalom, IAAT) cover only matrix multiply, not factorizations.

## Integration

| | |
|---|---|
| **Form** | static lib (shared with -DBUILD_SHARED_LIBS=ON); CMake package cbk::cbk |
| **Dependencies** | none for the library (OpenMP optional); tests need LAPACKE + CBLAS (OpenBLAS, Netlib, Accelerate via accelerate-lapacke, or MKL); benchmarks and the MKL-style API need Intel MKL |
| **Minimum toolchain** | C++17 GCC or Clang (GNU vector extensions; icpx also handled), CMake &gt;= 3.28; tested with GCC and Clang on x86-64 Linux, plus a macOS CI job |
| **Platforms** | Any target GCC/Clang can lower vector types for (SSE, AVX, AVX-512, non-x86 extensions per the CHANGELOG); performance documented only on an unnamed AVX-512 x86-64 machine |
| **Thread safety** | Reentrant (state is caller-owned); each routine forks an OpenMP team over groups only when there are at least two groups and enough work, and runs serially when called from inside a caller's parallel region unless nested parallelism is enabled; results do not depend on the thread count |
| **Drop-in for the baseline** | partial: names and argument orders follow LAPACK and MKL compact, but the data must be in compact interleaved layout; the MKL-style layer is a true drop-in companion to MKL's compact routines, not a replacement for per-matrix LAPACKE calls |

## Gotchas

- Build with -march=native (or an explicit -m flag): the library sets no -march, so a default build emits baseline SSE2 while MKL dispatches AVX-512 at runtime. Building from your own build system also needs -fno-math-errno, or the vector square root turns into scalar libm calls.
- Workspace is not checked: an undersized lwork in the MKL-style compact routines is an out-of-bounds write, and under MKL's threaded layer MKL's own ?geqrf_compact sizes its workspace per thread.
- Align buffers to 64 bytes: unaligned bases still work but cost up to \~40% on small sizes. Issue #34 (clang 18 with AVX segfaulting on 16-byte-aligned buffers) was closed by PR #35, and cbk.h now says the loads and stores never fault.
- The upper-triangle LDL^T convention is A = U^T D U, the transpose of LAPACK ?sytrf's A = U D U^T. The docs also disagree on the OpenMP gate (cbk.h says about 2e5 flops, threading.md and building.md say 5e4).

## Known shortcomings

- Baseline LAPACKE is MKL's own (building.md); no CPU model; no lwork check, so a short workspace causes an out-of-bounds write (documented).
- Docs disagree on the OpenMP gate (cbk.h 2e5 flops vs threading.md 5e4); clang AVX segfault #34 fixed by PR #35; tested against MKL 2020.4 only; no pack/unpack helpers in the portable API.

## Caveats and trade-offs

Hardware is not identified beyond '4-core AVX-512 container', so tier C; the benchmark page labels the runs 'indicative'; pack/unpack time is excluded from the timed region; per-matrix LAPACK wins from about n=128-168 (0.25x at n=256) and at nrhs=64 is level or ahead at several sizes (0.85-0.95x at n=80 and 120); SPD solve only matches MKL compact. The benchmarks build only with -DCBK_WITH_MKL=ON, under which the per-matrix LAPACKE baseline is MKL's own LAPACKE (sequential MKL) per docs/building.md. Compact routines do not check lwork, so an undersized workspace is an out-of-bounds write (documented). The README states most of the library, tests and benchmarks were written by Claude models with human review.

Needs the compact (interleaved) layout and packing; many small matrices only; the win disappears for larger matrices; unpivoted LDL^T (no Bunch-Kaufman pivoting); optional MKL-compatible API layer; GCC/Clang vector extensions, OpenMP over groups of V matrices.

## Maintenance

Actively developed (v0.2.0 released 2026-09-15, 316 commits, one open feature issue for rank-revealing QR) and Apache-2.0, so it is copyable. It is young, has a single maintainer, and the CHANGELOG lists testing only on x86-64 Linux against Intel MKL 2020.4.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party BENCHMARKS.md with public benchmark programs (bench_qr_compact, bench_posv_compact) and gcc -O3 -march=native, but the hardware is only a '4-core AVX-512 container' with no CPU model, so not A.
- **Verifier notes:** All numbers in claimed_speedup match examples/BENCHMARKS.md; the Notes section also gives 2.8x geomean for gels vs LAPACKE_dgels at 4 threads (7.7x at n=10, 1.4x at n=120). Metadata verified: Apache-2.0, 1 star, last commit 2026-09-15.
- **Fields the verifier corrected:** `caveats`
- **Pages the verifier opened:**
  - <https://github.com/ivan-pi/cbk>
  - <https://github.com/ivan-pi/cbk/commits/main>
  - <https://raw.githubusercontent.com/ivan-pi/cbk/HEAD/README.md>
  - <https://raw.githubusercontent.com/ivan-pi/cbk/HEAD/examples/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/ivan-pi/cbk/HEAD/docs/building.md>
- **Sources the enricher read:**
  - <https://github.com/ivan-pi/cbk>
  - <https://raw.githubusercontent.com/ivan-pi/cbk/HEAD/README.md>
  - <https://raw.githubusercontent.com/ivan-pi/cbk/HEAD/examples/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/ivan-pi/cbk/HEAD/docs/building.md>
  - <https://raw.githubusercontent.com/ivan-pi/cbk/HEAD/docs/threading.md>
  - <https://raw.githubusercontent.com/ivan-pi/cbk/HEAD/docs/layout.md>
  - <https://raw.githubusercontent.com/ivan-pi/cbk/HEAD/docs/README.md>
  - <https://raw.githubusercontent.com/ivan-pi/cbk/HEAD/docs/cbk_dsytrfnp_compact_design.md>
  - <https://raw.githubusercontent.com/ivan-pi/cbk/HEAD/include/cbk.h>
  - <https://raw.githubusercontent.com/ivan-pi/cbk/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ivan-pi/cbk/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/ivan-pi/cbk/HEAD/LICENSE>
  - <https://github.com/ivan-pi/cbk/issues?q=is%3Aissue>
  - <https://github.com/ivan-pi/cbk/issues/34>
  - <https://github.com/ivan-pi/cbk/pull/35>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/ivan-pi/cbk`) · [data/wave8/enrich/raw/github_com_ivan_pi_cbk.json](../../../data/wave8/enrich/raw/github_com_ivan_pi_cbk.json) (enrichment confidence 0.8)

</details>
