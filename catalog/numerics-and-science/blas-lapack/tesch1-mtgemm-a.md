# MTGEMM-A

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [BLAS and LAPACK](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🟢 active

> SME2 FP32/FP64 GEMM for Apple M4 Pro, rebuilt from the MpGEMM paper: 1.18-1.26x Apple Accelerate on the paper's workloads.

| | |
|---|---|
| **Beats** | Apple Accelerate sgemm/dgemm (also OpenBLAS develop and 0.3.34, Eigen master, LIBXSMM, KleidiAI) |
| **Claimed result** | FP32 geomean 2777 vs 2363 GFLOPS for Accelerate on the paper's 24 column-major workloads at default threading (1.18x; 1.17x row-major); one thread, paper's 24 workloads: 1421 vs 1196 (1.19x column-major) and 1416 vs 1124 (1.26x row-major); squares 512-4096 one thread only 1.04x-1.06x; 1.25x row-major / 1.19x column-major vs Accelerate in the paper-comparison table (fp64 1.29x one thread); 3.70x faster than OpenBLAS 0.3.34 (row-major), 2.20x faster than LIBXSMM (column-major) and 1.67x faster than KleidiAI (one thread); Eigen master 1044 GFLOPS vs 2777 at default threading. |
| **Workload** | FP32/FP64 GEMM on Apple M4 Pro using Arm SME2: the paper's 24 workloads and square sizes 512-4096, row- and column-major, one thread and default threading, geometric mean GFLOPS. |
| **Metric** | throughput |
| **Hardware** | Apple M4 Pro, 8 performance cores in two clusters of 4 (two SME units, SVL 512 bits), 48 GB |
| **Compiler and flags** | Apple clang 21 (macOS 27.0), -std=c++17 -O3 -DNDEBUG -march=armv8.6-a+sme2+sme-f64f64 |
| **Adoption** | 0 stars |
| **Last commit** | 2026-09-29 |
| **Links** | [repository](https://github.com/tesch1/MTGEMM-A) · [benchmark](https://github.com/tesch1/MTGEMM-A) |

## Verdict

Setup: Apple M4 Pro (8 P-cores, two SME units, SVL 512, macOS 27.0), Apple clang 21 with -O3 -march=armv8.6-a+sme2+sme-f64f64, minimum of five 50 ms trials on a shared machine (load 1.5-5.6). FP32 geometric mean over the paper's 24 workloads: 1421 vs 1196 GFLOPS for Accelerate on one thread column-major (1.19x), 1416 vs 1124 row-major (1.26x) and 2777 vs 2363 at default threading (1.18x); squares 512-4096 on one thread gain only 1.04-1.06x. In the same harness it is 2.20x LIBXSMM, 1.67x KleidiAI and 3.70x Homebrew OpenBLAS 0.3.34, which falls back to NEON at M=4096.

## Use it when

- FP32 or FP64 GEMM on an Apple M4/M4 Pro where you want to beat Accelerate. On one thread over the paper's 24 workloads it is 1.19x column-major and 1.26x row-major; at default threading it is 1.18x. FP64 row-major on one thread is 1.29x.
- Skinny and irregular shapes. With K=4096, one side 4-32 and the other two at 4096 it is 1.2-2.4x Accelerate on one thread. At K=25600 with M=N=80-200 it is 1.18-1.63x.
- Mid-size problems from 192^3 to 512^3 with threads=0. It brings in the second SME unit from 2^22 multiply-adds, where Accelerate waits until about 512^3 (1.2-2.0x).
- You need a BLAS-like alpha/beta/leading-dimension interface and one binary that dispatches across M2-M4 (SME, AMX or reference loop).
- A readable SME GEMM reference: the core is about 740 lines, with an ablation table per design element. It was used to port SME GEMM into Eigen and OpenBLAS.

## Skip it when

- Tiny problems. Squares below 64^3 run at 0.16-0.9x Accelerate and the 4x4 corner at 0.5x. Matrix-vector cases (one side = 1) run at 0.4x.
- K=512 with one side of 32 or less and the other of 512 or more, where it is at 0.6-0.9x on one thread.
- Transposed operands, complex types, mixed precision (FP16/BF16/INT8) or other BLAS/LAPACK routines. Only no-transpose real GEMM is implemented.
- Non-Apple SME2 hardware or another vector length. The code uses macOS APIs (pthread QoS, sysctl) and SVL-512 constants, and the AMX backend does not run on M1.
- Large squares on one thread only. The gain there is 1.04-1.06x, inside the few-percent noise of a shared machine.

## How it is fast

It uses Goto/BLIS six-loop blocking, with mc/nc/kc chosen by the paper's analytical model: an 8 MB L2 budget, a TLB bound and the best compute-to-memory ratio. Under it sits a 16x64 FP32 (8x64 FP64) micro-kernel that issues four FMOPA outer products into four ZA tiles per A vector. A is transposed while packing through the ZA array, and B is packed online during the first pass. All full-width loads and stores use SME2 four-register (x4) forms. The project's additions over the paper are core-side prfm pldl2keep prefetch of A, B and C into the L2 that the SME unit reads (1.12x row-major, 1.20x column-major) and four-row MOVA vg4 moves for C tiles and A packing. An optional second thread drives the second P-cluster's SME unit (1.95x scaling).

## Compared with alternatives

Pick it over MaxMulSK when you need FP64, alpha/beta, leading dimensions, column-major input or both M4 Pro SME units, all from published code: MaxMulSK is FP32, single-threaded and row-major, and its fastest kernel is unpublished. Against MPGEMM (github.com/mpgemm/MPGEMM, MIT), the README says no MpGEMM code was found and compares only with the paper's chart numbers (1.06x/1.10x on one thread). That repository is now public, so run a side-by-side test before choosing.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | None for the library (macOS system headers). Accelerate is used by the tests and benchmarks. LIBXSMM, KleidiAI, Eigen, OpenBLAS and Google Benchmark are fetched only for the comparison targets. |
| **Minimum toolchain** | C++17; Apple clang with SME2 support (results with Apple clang 21) and -march=armv8.6-a+sme2+sme-f64f64 |
| **Platforms** | macOS on Apple M4 family (SME2, SVL 512, FEAT_SME_F64F64); AMX backend for M2/M3 (incl. Vision Pro), not M1; portable reference loop elsewhere |
| **Thread safety** | Not documented. In the code the packing buffers are thread_local, and two-thread mode uses one process-wide worker thread behind a static mutex, so concurrent two-thread calls from different threads serialize. |
| **Drop-in for the baseline** | partial: the argument list mirrors cblas_sgemm/dgemm without the transpose flags, but the names differ (mt_sgemm/mt_dgemm) and it exports no BLAS symbols |

## Gotchas

- The default mt_options has threads=1, so a call with opt=nullptr runs on one SME unit. The README's 'default threading' figures need threads=0 (two threads from 2^22 multiply-adds) or threads=2.
- Two-thread mode starts a persistent worker that is never joined and spins for 200 us after each call while the caller busy-waits. macOS cannot pin threads, so both threads can land on one SME unit, and threads=2 has no small-size fallback.
- Dimensions and leading dimensions are int (32-bit). The thread_local packing buffer stays allocated between calls in every thread that calls the library.
- The mt_options.prof setting gives wrong results by design (profiling only). The AMX backend relies on undocumented instructions (corsix/amx encodings), which a future OS or chip could remove.

## Known shortcomings

- Run on a shared machine (minimum of 5 trials); slower below 64^3; independent reimplementation of the MpGEMM (ARM SME) design, not a duplicate.
- README says no MpGEMM code exists, now false (github.com/mpgemm/MPGEMM, MIT); opt=nullptr runs one thread (the 'default threading' figures need threads=0); macOS only (pthread QoS, sysctl).

## Caveats and trade-offs

Reproduction of the paper arXiv:2512.21473 (MpGEMM, whose authors released no code), by a single author, measured on one shared machine (one-minute load 1.5-5.6 during final runs; minimum of five trials, which the README says is a few percent more favourable than the paper's mean) with an 8 P-core M4 Pro vs the paper's 10 P-core; at default threading it is slower than Accelerate (below 0.9x) on 10 of 484 grid shapes and below 64^3 (0.17x-0.9x); the win on squares 512-4096 on one thread is only 4-6%; the Accelerate version is not stated beyond macOS 27.0; the OpenBLAS 0.3.34 figure in the LIBXSMM/KleidiAI comparison is one Homebrew-build measurement that falls back to NEON at M=4096; OpenBLAS develop's own SME kernels reach 0.50x-0.78x of MTGEMM-A on one thread; macOS cannot pin the two worker threads to separate SME clusters; no-transpose GEMM only. The repo also carries an OpenBLAS port (branch sme2-gemm of the author's OpenBLAS fork, not yet submitted) and an Eigen SME GEMM backend developed from this code. Wave 8 leads.md already lists this repo as a candidate for the MpGEMM paper entry. [retier] The MpGEMM authors' code is now public at github.com/mpgemm/MPGEMM (MIT), so 'authors released no code' is stale.

Apple M4-family (SME2) only for the SME backend; an AMX backend covers M2/M3-class chips; no transposed operands (computes C = alpha A B + beta C only); GEMM only, not full BLAS; macOS cannot pin threads to an SME cluster so two-thread results depend on scheduling.

## Maintenance

Active (51 commits, last 2026-09-29), MIT and small enough to vendor, but a 0-star single-author reproduction measured on one machine. Its tests run 2304 option combinations and 900 random cases against a double-precision reference.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** README 'Results in short' and the LIBXSMM/KleidiAI/OpenBLAS table give geometric-mean GFLOPS vs Accelerate, OpenBLAS 0.3.34, Eigen, LIBXSMM and KleidiAI; benchmark code is public (bench/bench.cpp, bench/bench_ext.cpp, bench/bench_eigen.cpp, bench/bench_openblas.cpp, bench/run_all.sh), Makefile flags -std=c++17 -O3 -DNDEBUG -march=armv8.6-a+sme2+sme-f64f64, Apple clang 21 on macOS 27.0, Apple M4 Pro.
- **Verifier notes:** All quoted numbers match the README (KleidiAI ratio is 1.67x, rounded to 1.7x in the record). Metadata checked on github.com: MIT, 0 stars, not a fork, 51 commits, last 2026-09-29. Independent re-implementation of paper:mpgemm-arm-sme (tier C, no code), not a wrapper or port of it, so not a duplicate; the orchestrator may want to cross-link the two.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/tesch1/MTGEMM-A>
  - <https://github.com/tesch1/MTGEMM-A/commits>
  - <https://raw.githubusercontent.com/tesch1/MTGEMM-A/HEAD/README.md>
  - <https://raw.githubusercontent.com/tesch1/MTGEMM-A/HEAD/Makefile>
  - <https://raw.githubusercontent.com/tesch1/MTGEMM-A/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/tesch1/MTGEMM-A>
  - <https://raw.githubusercontent.com/tesch1/MTGEMM-A/HEAD/README.md>
  - <https://raw.githubusercontent.com/tesch1/MTGEMM-A/HEAD/Makefile>
  - <https://raw.githubusercontent.com/tesch1/MTGEMM-A/HEAD/include/mtgemm.h>
  - <https://raw.githubusercontent.com/tesch1/MTGEMM-A/HEAD/src/mtgemm.cpp>
  - <https://raw.githubusercontent.com/tesch1/MTGEMM-A/HEAD/src/threads.cpp>
  - <https://raw.githubusercontent.com/tesch1/MTGEMM-A/HEAD/src/dispatch.cpp>
  - <https://github.com/mpgemm/MPGEMM>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/tesch1/mtgemm-a`) · [data/wave8/enrich/raw/github_com_tesch1_mtgemm_a.json](../../../data/wave8/enrich/raw/github_com_tesch1_mtgemm_a.json) (enrichment confidence 0.85)

</details>
