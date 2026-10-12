# FT-BLAS

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [BLAS and LAPACK](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `GPL-3.0` · 🔴 abandoned

> Research double-precision BLAS for AVX-512 Intel CPUs with built-in soft-error checks; paper reports small wins over OpenBLAS, BLIS, MKL.

| | |
|---|---|
| **Beats** | OpenBLAS, BLIS, Intel MKL |
| **Claimed result** | Up to 22.14% faster than OpenBLAS, 21.70% than BLIS, 3.50% than MKL |
| **Workload** | Level-1/2/3 BLAS with online fault tolerance on Skylake/Cascade Lake |
| **Metric** | throughput |
| **Hardware** | Intel Gold 5122 Skylake, Xeon W-2255 Cascade Lake |
| **Compiler and flags** | icc 19.0 -O3 |
| **Adoption** | 7 stars |
| **Last commit** | 2023-02-28 |
| **Links** | [repository](https://github.com/yzhaiustc/ftblas) · [benchmark](https://arxiv.org/pdf/2104.00897) |

## Verdict

The peer-reviewed ICS '21 paper reports FT-BLAS (including its fault-tolerant variants) up to 22.14% faster than OpenBLAS, 21.70% faster than BLIS and 3.50% faster than Intel MKL across routines from all three BLAS levels, built with icc 19.0 -O3 on an Intel Xeon Gold 5122 (Skylake) and a Xeon W-2255 (Cascade Lake), with fault-tolerance overhead under 3% while errors were injected. These are best-case 'up to' figures, and the repository's test programs time only FT-BLAS itself, so the comparison is not reproducible from the repo.

## Use it when

- Research or evaluation of soft-error-tolerant linear algebra on Intel Skylake-SP / Cascade Lake class CPUs with AVX-512.
- Studying or borrowing a compact, readable AVX-512 DGEMM (Goto blocking + 24x8 assembly micro-kernel) or DMR-in-assembly level-1 kernels as a starting point for your own code, under GPL-3.0 terms.
- Single-node, double-precision, column-major, non-transposed GEMM/DOT/AXPY workloads where you can test that your exact call shapes are supported.

## Skip it when

- As a production replacement for OpenBLAS, MKL or BLIS: many argument combinations are unimplemented (cblas_dgemm accepts only ColMajor NoTrans/NoTrans; dsymm only Left/Lower; dtrsm and dtrmm only Left/Lower/NoTrans) and the library calls exit(-1) on anything else.
- Code that relies on alpha == 0 semantics: the dgemm, dsymm, dtrmm and dtrsm wrappers return immediately when alpha is 0, leaving C unscaled by beta (or B not zeroed), which violates the BLAS specification.
- Anyone who needs the fault tolerance to actually protect results: in the released DGEMM the checksum comparison and correction code is commented out, and the fault-tolerant DDOT on a detected mismatch only prints a message and returns a truncated (wrong) dot product instead of recomputing.
- Non-AVX-512 CPUs, AMD/ARM machines, complex or most single-precision routines, or multithreaded BLAS: CMake hard-codes -march=skylake-avx512 and the DGEMM/DDOT sources contain no threading.
- Closed-source or permissively licensed products: the code is GPL-3.0.

## How it is fast

The non-FT kernels are Goto-style blocked GEMM (A/B packing into 4 KiB-aligned buffers, KC=384, 24x8 AVX-512 micro-kernel in inline assembly with software prefetch) and unrolled AVX2/AVX-512 assembly loops for level-1/2. For fault tolerance, the paper uses a hybrid scheme: dual modular redundancy (each FMA issued twice into separate registers and compared with vpcmpeqd/vmovmskpd) for memory-bound level-1/2, where the duplicate instructions hide behind memory stalls, and algorithm-based fault tolerance (row/column checksums of A, B and C) for level-3, with the checksum updates fused into the packing routines so they cost almost no extra memory traffic.

## Compared with alternatives

Pick FT-BLAS only when soft-error tolerance on x86 is the research question, since no catalogued sibling offers it; for plain speed on CPUs, BLASFEO or LibShalom (small matrices) and GEMMFIP or Eigen (general sizes) are complete, maintained and permissively licensed, and CLBlast is the GPU option.

## Integration

| | |
|---|---|
| **Form** | static lib (CMake add_library without SHARED; builds libSrcFuncs plus test binaries) |
| **Dependencies** | none beyond libm and libpthread; CMake passes -fopenmp |
| **Minimum toolchain** | C++11, CMake 3.17; GCC/Clang-style inline assembly (AT&T syntax) and AVX-512 intrinsics; the paper used icc 19.0 -O3 |
| **Platforms** | x86-64 Linux with AVX-512F (Skylake-SP, Cascade Lake or newer Intel); -march=skylake-avx512 is hard-coded |
| **Thread safety** | not documented; DGEMM allocates its packing buffers per call with aligned_alloc and uses no globals in the code read, but no statement exists |
| **Drop-in for the baseline** | partial — exports CBLAS names and enums for the supported subset, so simple ColMajor double-precision code can relink against it, but unsupported cases abort the process, alpha==0 handling is wrong, several output pointers are declared const, and its cblas.h clashes with OpenBLAS/MKL headers |

## Gotchas

- Unsupported layout/transpose/side combinations and bad leading dimensions call printf then exit(-1) or exit(-2) from inside the library instead of returning an error code.
- Each DGEMM call allocates about 32 MB of packing buffers (384x1152 and 384x9216 doubles) and frees them on return, which hurts repeated small calls.
- The fault-tolerant DGEMM compares checksums against an absolute threshold of 1e-2 (in commented-out code), which would false-alarm on large-magnitude data and miss small errors if re-enabled.
- The top-level CMake overwrites CMAKE_CXX_FLAGS with CMAKE_C_FLAGS plus its own flags, so CXX flags passed by the user are dropped.

## Known shortcomings

- Code now public (GPL-3.0) but no benchmark code for the paper's numbers in the repo; abandoned (last commit 2023-02-28), 7 stars.
- Correctness bug: dgemm/dsymm/dtrmm/dtrsm wrappers return early when alpha==0, so C is not scaled by beta (or B not zeroed), breaking the BLAS spec; unsupported cases (dgemm supports only ColMajor NoTrans/NoTrans) call exit(-1) inside the library.
- Fault-tolerance claim not reproducible from the repo: FT DGEMM's checksum verify/correct code is commented out and FT DDOT only prints and returns a truncated wrong result on a detected error; the repo has no harness comparing against OpenBLAS/BLIS/MKL; -march=skylake-avx512 hard-coded; GPL-3.0.

## Caveats and trade-offs

Gains are 'up to' figures from the paper; code was released later at github.com/yzhaiustc/ftblas (GPL-3.0, linked from ftblas.org), mainly double precision; last commit 2023-02-28; the benchmark harness for the paper's numbers was not confirmed in the repo

Adds fault tolerance at 0.35-3.10% overhead

## Maintenance

Abandoned research code (last commit 2023-02-28, 7 stars, no releases); GPL-3.0 with an OpenBLAS license file included, usable for study or experiments but not production-ready.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed ICS '21 paper reports up to 22.14% over OpenBLAS, 21.70% over BLIS and 3.50% over MKL on Skylake Gold 5122 / Cascade Lake W-2255 with icc 19.0 -O3; the code is now public but no benchmark harness was confirmed in it, so not A.
- **Verifier notes:** The code was released after the paper: set repo_url to https://github.com/yzhaiustc/ftblas (repo_url is not a correction field; repo language not checked). The ICS'21 numbers match the record.
- **Fields the verifier corrected:** `license`, `usability`, `last_commit`, `maintenance_status`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/abs/2104.00897>
  - <https://github.com/yzhaiustc/ftblas>
  - <https://www.ftblas.org/>
  - <https://github.com/yzhaiustc/ftblas/commits>
  - <https://raw.githubusercontent.com/yzhaiustc/ftblas/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/yzhaiustc/ftblas>
  - <https://github.com/yzhaiustc/ftblas/commits/main>
  - <https://github.com/yzhaiustc/ftblas/tree/main/src>
  - <https://github.com/yzhaiustc/ftblas/tree/main/licenses>
  - <https://raw.githubusercontent.com/yzhaiustc/ftblas/HEAD/README.md>
  - <https://raw.githubusercontent.com/yzhaiustc/ftblas/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/yzhaiustc/ftblas/HEAD/src/CMakeLists.txt>
  - <https://raw.githubusercontent.com/yzhaiustc/ftblas/HEAD/include/CMakeLists.txt>
  - <https://raw.githubusercontent.com/yzhaiustc/ftblas/HEAD/test/CMakeLists.txt>
  - <https://raw.githubusercontent.com/yzhaiustc/ftblas/HEAD/test/test_dgemm.cpp>
  - <https://raw.githubusercontent.com/yzhaiustc/ftblas/HEAD/test/test_ddot.cpp>
  - <https://raw.githubusercontent.com/yzhaiustc/ftblas/HEAD/include/cblas.h>
  - <https://raw.githubusercontent.com/yzhaiustc/ftblas/HEAD/include/ftblas.h>
  - <https://raw.githubusercontent.com/yzhaiustc/ftblas/HEAD/src/cblas_dgemm.cpp>
  - <https://raw.githubusercontent.com/yzhaiustc/ftblas/HEAD/src/cblas_ddot.cpp>
  - <https://raw.githubusercontent.com/yzhaiustc/ftblas/HEAD/src/cblas_dgemv.cpp>
  - <https://raw.githubusercontent.com/yzhaiustc/ftblas/HEAD/src/cblas_dtrsm.cpp>
  - <https://raw.githubusercontent.com/yzhaiustc/ftblas/HEAD/src/cblas_dsymm.cpp>
  - <https://raw.githubusercontent.com/yzhaiustc/ftblas/HEAD/src/cblas_dtrmm.cpp>
  - <https://raw.githubusercontent.com/yzhaiustc/ftblas/HEAD/src/dgemm_avx512.cpp>
  - <https://raw.githubusercontent.com/yzhaiustc/ftblas/HEAD/src/dgemm_avx512_ft.cpp>
  - <https://raw.githubusercontent.com/yzhaiustc/ftblas/HEAD/src/ddot_avx2_ft.cpp>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `paper:ft-blas`) · [data/wave8/enrich/raw/paper_ft_blas.json](../../../data/wave8/enrich/raw/paper_ft_blas.json) (enrichment confidence 0.75)

</details>
