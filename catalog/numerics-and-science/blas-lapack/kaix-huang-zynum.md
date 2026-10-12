# Zynum

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [BLAS and LAPACK](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Zig` · `LGPL-3.0-or-later` · 🟢 active

> Zig BLAS 1-3 with CBLAS/Fortran ABI and SME kernels; about 2x OpenBLAS GEMM on Apple M5, roughly even with Accelerate.

| | |
|---|---|
| **Beats** | OpenBLAS 0.3.34 (also Apple Accelerate) |
| **Claimed result** | sgemm 1024x1024x1024: 1998.7 GFLOP/s vs OpenBLAS 472.6 and Accelerate 1924.8; dgemm sq1024: 556.5 vs OpenBLAS 252.4 and Accelerate 505.8 (gemm.csv). Median Zynum/OpenBLAS GFLOP/s ratio over all 168 cases is 2.15x (derived from page data), Zynum faster in 146 of 168 cases. Versus Accelerate the median ratio is 1.11x, with Zynum ahead in 100 of 168 cases (derived from page data) and behind on sgemm medians (0.93x). |
| **Workload** | GEMM GFLOP/s over 42 NN column-major shapes for each of sgemm/dgemm/cgemm/zgemm (168 cases), six interleaved fresh-process runs per library, on an Apple M5 with 10 threads. |
| **Metric** | throughput |
| **Hardware** | Apple M5, 10 logical CPUs, macOS 27.0 (feat_sme/sme2 detected) |
| **Compiler and flags** | Zig 0.16.0, zig build -Dcpu=baseline -Ddispatch=dynamic -Doptimize=ReleaseFast; OPENBLAS_NUM_THREADS=10 OPENBLAS_DYNAMIC=0; OpenBLAS 0.3.34 |
| **Adoption** | 0 stars, 0 forks, 42 commits, 0.0.1-beta, no releases |
| **Last commit** | 2026-09-23 |
| **Links** | [repository](https://github.com/kaix-huang/Zynum) · [benchmark](https://raw.githubusercontent.com/kaix-huang/Zynum/HEAD/docs/assets/benchmarks/current/gemm.csv) |

## Verdict

The author's fresh-process interleaved sweep on an Apple M5 (10 logical CPUs, macOS 27.0, Zig 0.16.0, -Dcpu=baseline -Ddispatch=dynamic ReleaseFast) over 42 NN column-major shapes per s/d/c/zgemm shows median 2.15x OpenBLAS 0.3.34 (10 threads), with Zynum faster in 146 of 168 cases, and median 1.11x Accelerate (faster in 100 of 168), e.g. sgemm 1024^3 1999 vs 473 (OpenBLAS) and 1925 (Accelerate) GFLOP/s; correctness is sampled only.

## Use it when

- Apple M4/M5-class Macs (SME/SME2) where you want a portable CBLAS/Fortran BLAS faster than OpenBLAS: median 2.15x GEMM GFLOP/s over OpenBLAS 0.3.34 across 168 cases on an M5
- Complex GEMM on Apple Silicon: cgemm and zgemm medians are 1.21x and 1.47x Accelerate in the published sweep (zgemm 1024^3: 598 vs 407 GFLOP/s)
- Medium-to-large square or rectangular GEMM (n of a few hundred to 1024) with all cores in use
- Zig projects that want a typed, bounds-checked BLAS API with no external dependencies

## Skip it when

- Small or irregular shapes (m, n about 31-129 with k about 31-33): Zynum runs at 0.16-0.22x Accelerate there, and m17_n2048_k257 sgemm is 107 vs 429 GFLOP/s (Accelerate) and 203 (OpenBLAS)
- Real sgemm/dgemm on macOS when Accelerate is available: medians are 0.92x and 0.99x of Accelerate
- x86-64 or Linux servers: AVX/AVX2/AVX-512 tiers exist but no native x86 performance numbers are published, and Windows correctness rows are pending
- Anything needing LAPACK, ILP64 (64-bit integer) BLAS, or a stable API: Level 1-3 only, 32-bit BLAS integers, 0.0.1-beta with dispatch policy subject to change
- Projects that cannot accept LGPL-3.0-or-later linking terms

## How it is fast

One library carries separately compiled ISA tiers (baseline, SVE2, SME, SME2, SME2p1, AVX, AVX2+FMA, AVX-512) and picks one at load time from sysctl/HWCAP/CPUID, so a baseline build still reaches Apple M4/M5 SME streaming outer-product kernels, the likely source of its 2-4x lead over OpenBLAS's NEON code on M5. GEMM goes through a catalog/tuning/planner layer that chooses among packed-panel, direct, vector-edge (GEMV-like) and, for complex, 3-real-multiply or 4-real-multiply plane decompositions per shape. Work is split across a persistent std.Io thread pool by disjoint output tiles; an Apple AMX route exists but is off unless built with -Dapple-amx=true.

## Compared with alternatives

Pick Zynum over GEMM-only Apple kernels such as sme-gemm, MaxMulSK or apple-bottom when you need a whole BLAS 1-3 library with CBLAS and Fortran ABI and complex types, not one fast GEMM; pick Apple Accelerate itself for real sgemm/dgemm or small shapes on macOS, and OpenBLAS or BLIS on x86.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | none at runtime (static and shared libraries are both built); Zig 0.16 to build; Python 3 for the benchmark tooling |
| **Minimum toolchain** | Zig 0.16.0 (minimum_zig_version in build.zig.zon); any C or Fortran compiler for consumers |
| **Platforms** | aarch64 macOS (benchmarked on Apple M5 with SME/SME2), aarch64 Linux (HWCAP detection, link-only CI row), x86-64 Linux and Windows (SSE2/AVX/AVX2/AVX-512 tiers, no published performance) |
| **Thread safety** | Process-wide thread pool with documented concurrent-caller, shutdown/restart and thread-cap tests; per-thread cached workspace; ZYNUM_MAXIMUM_THREADS must be set before the first call; call zynum_blas_shutdown() before dlclose |
| **Drop-in for the baseline** | partial — exports standard Fortran (dgemm_) and CBLAS (cblas_dgemm) symbols with 32-bit integers, so it replaces an LP64 OpenBLAS for BLAS 1-3, but it has no LAPACK, no ILP64 build, and no OpenBLAS-specific extensions |

## Gotchas

- Default thread count is the full CPU count; set ZYNUM_MAXIMUM_THREADS before the first BLAS call (later changes are ignored)
- CBLAS entry points silently return without touching outputs on invalid enum/layout arguments instead of calling xerbla
- Do not compile Fortran callers with -fdefault-integer-8: the BLAS integer is 32-bit
- The benchmark manifest (source.json, measured 2026-09-21) marks the measured working tree dirty on top of base revision 6a989d0, so the timed code is identified by content hashes rather than a commit

## Known shortcomings

- Benchmarks were run from a dirty tree (199 of 203 file hashes match HEAD).
- Runs 0.16-0.22x of Accelerate on small odd shapes (m \~31-129, k \~31-33); 32-bit BLAS ints only, no LAPACK; no x86 performance data; CBLAS silently ignores bad arguments.

## Caveats and trade-offs

Single host (Apple M5), measurements by the author. Zynum appears to dispatch SME/AArch64 kernels (feat_sme/feat_sme2 detected per gemm.csv.meta.json) while OpenBLAS 0.3.34 on M5 likely runs NEON kernels, which probably explains the 3.9x median sgemm gap; Accelerate (Apple's vendor BLAS) is the fairer comparator and Zynum is roughly even to slightly slower on sgemm/dgemm medians (0.93x and 0.99x of Accelerate's GFLOP/s) while ahead on cgemm (1.21x) and zgemm (1.47x) medians (derived from page data). Some shapes (e.g. m17_n2048_k257) are slower than both rivals (sgemm 107.2 vs Accelerate 429.1, OpenBLAS 203.5 GFLOP/s). The dataset is marked dirty (uncommitted working-tree sources hashed in source.json); at the time of checking, 199 of 203 manifest source hashes matched the files at HEAD, with build.zig, src/blas/runtime.zig, src/blas/core/matrix_matrix/structured_blocked.zig and src/blas/kernels/isolated/x86_64_structured_bridge.zig differing. Correctness is sampled-checked only, and the metadata reader reports a kernel_coverage_invalid_document diagnostic, so per-call kernel selection is not validated. Zynum runs its default thread policy (CPU count ceiling) while comparators are capped at 10 threads. Repo is weeks old (first commits page reaches back to 2026-08-10) with no external users. Level 2 timings include Python/ctypes overhead. Written in Zig with C (CBLAS) and Fortran ABIs, LGPL-3.0-or-later.

Zig-native BLAS exposing CBLAS and Fortran-ABI entry points plus C headers (include &lt;zynum/blas/cblas.h&gt;, link zynum_blas), so it is callable from C++. Needs Zig 0.16 to build. LGPL-3.0-or-later (GPL-3.0 text also shipped). Level 1-3 BLAS only; no LAPACK. Beta, API and dispatch policy may change.

## Maintenance

Weeks-old beta (0.0.1-beta, 42 commits, 0 stars, last commit 2026-09-23) under LGPL-3.0-or-later; usable for evaluation, but expect API and dispatch changes and verify on your own hardware.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** gemm.csv holds per-library GFLOP/s for Zynum, OpenBLAS 0.3.34 and Accelerate over 168 cases; benchmark code is public (bench/gemm_sweep.zig, bench/tools/run_gemm_sweep_isolated.py, reproduction commands in docs/performance/README.md), and source.json plus the performance guide state Zig 0.16.0, -Dcpu=baseline -Ddispatch=dynamic -Doptimize=ReleaseFast, OPENBLAS_NUM_THREADS=10 OPENBLAS_DYNAMIC=0, and Apple M5 hardware.
- **Verifier notes:** All quoted figures re-derived from gemm.csv: sq1024 sgemm 1998.7 vs OpenBLAS 472.6 and Accelerate 1924.8, dgemm 556.5 vs 252.4 and 505.8; median Zynum/OpenBLAS 2.15x with 146/168 wins; median vs Accelerate 1.11x with 100/168 wins. License LGPL-3.0 (LICENSE plus COPYING), last commit 2026-09-23, 0 stars confirmed on github.com.
- **Fields the verifier corrected:** `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/kaix-huang/Zynum/HEAD/docs/assets/benchmarks/current/gemm.csv>
  - <https://raw.githubusercontent.com/kaix-huang/Zynum/HEAD/docs/assets/benchmarks/current/source.json>
  - <https://raw.githubusercontent.com/kaix-huang/Zynum/HEAD/docs/assets/benchmarks/current/gemm.csv.meta.json>
  - <https://raw.githubusercontent.com/kaix-huang/Zynum/HEAD/docs/performance/README.md>
  - <https://raw.githubusercontent.com/kaix-huang/Zynum/HEAD/README.md>
  - <https://raw.githubusercontent.com/kaix-huang/Zynum/HEAD/LICENSE>
  - <https://github.com/kaix-huang/Zynum>
  - <https://github.com/kaix-huang/Zynum/commits>
- **Sources the enricher read:**
  - <https://github.com/kaix-huang/Zynum>
  - <https://github.com/kaix-huang/Zynum/issues>
  - <https://raw.githubusercontent.com/kaix-huang/Zynum/HEAD/README.md>
  - <https://raw.githubusercontent.com/kaix-huang/Zynum/HEAD/docs/performance/README.md>
  - <https://raw.githubusercontent.com/kaix-huang/Zynum/HEAD/docs/assets/benchmarks/current/gemm.csv>
  - <https://raw.githubusercontent.com/kaix-huang/Zynum/HEAD/docs/assets/benchmarks/current/gemm.csv.meta.json>
  - <https://raw.githubusercontent.com/kaix-huang/Zynum/HEAD/docs/assets/benchmarks/current/source.json>
  - <https://raw.githubusercontent.com/kaix-huang/Zynum/HEAD/build.zig.zon>
  - <https://raw.githubusercontent.com/kaix-huang/Zynum/HEAD/build.zig>
  - <https://raw.githubusercontent.com/kaix-huang/Zynum/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/kaix-huang/Zynum/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/kaix-huang/Zynum/HEAD/SECURITY.md>
  - <https://raw.githubusercontent.com/kaix-huang/Zynum/HEAD/docs/architecture.md>
  - <https://raw.githubusercontent.com/kaix-huang/Zynum/HEAD/docs/roadmap.md>
  - <https://raw.githubusercontent.com/kaix-huang/Zynum/HEAD/docs/users/README.md>
  - <https://raw.githubusercontent.com/kaix-huang/Zynum/HEAD/docs/development_and_usage.md>
  - <https://raw.githubusercontent.com/kaix-huang/Zynum/HEAD/docs/fortran_compatibility.md>
  - <https://raw.githubusercontent.com/kaix-huang/Zynum/HEAD/docs/common/gemm_optimization_notes.md>
  - <https://raw.githubusercontent.com/kaix-huang/Zynum/HEAD/docs/aarch64/gemm_aarch64_optimization_notes.md>
  - <https://raw.githubusercontent.com/kaix-huang/Zynum/HEAD/docs/x86_64/gemm_x86_64_optimization_notes.md>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/kaix-huang/zynum`) · [data/wave8/enrich/raw/github_com_kaix_huang_zynum.json](../../../data/wave8/enrich/raw/github_com_kaix_huang_zynum.json) (enrichment confidence 0.8)

</details>
