# ALBUS

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Sparse matrices and solvers](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Research OpenMP+AVX2 double-precision CSR SpMV kernel with nonzero-balanced thread split; paper reports beating MKL, CSR5 and Merge.

| | |
|---|---|
| **Beats** | Intel MKL SpMV (oneAPI 2021); also CSR5 and merge-based SpMV |
| **Claimed result** | README quotes the FGCS 2021 abstract: on dual-socket Xeon E5-2670 v3, regular matrices average 1.59x / 1.32x / 1.48x (up to 2.53x / 2.22x / 2.31x) over CSR5 / Merge / MKL; irregular matrices average 1.38x / 1.42x / 2.44x (up to 2.33x / 2.24x / 5.37x) over CSR5 / Merge / MKL. README per-matrix table (Xeon Gold 6242 dual socket, GFlops): rma10 ALBUS 94.52 vs CSR5 42.05 vs CVR 65.84; mac_econ_fwd500 68.56 vs 25.33 vs 40.79; webbase-1M 34.14 vs 21.92 vs 22.13; ALBUS loses to CVR on cant, ins2 and pdb1HYS. |
| **Workload** | Double-precision CSR SpMV (GFlops) on 40 SuiteSparse/UF matrices (20 regular, 20 irregular) on dual-socket Xeon CPUs, OpenMP plus AVX2. |
| **Metric** | throughput |
| **Hardware** | README table: dual-socket Intel Xeon Gold 6242 (2x16 cores). Abstract numbers: dual-socket Xeon E5-2670 v3. The README also lists a dual-socket Xeon Silver 4110 test platform. |
| **Compiler and flags** | Both Makefiles (ALBUS(OpenMP) and ALBUS(OpenMP+AVX2)): icpc -g -w -fno-alias -qopt-report -qopt-report-phase=all -mbranches-within-32B-boundaries -falign-double -inline-calloc -falign-loops=8 -xCORE-AVX2 -fopenmp -O3. The README's example shows an older 'icpc -xCORE-AVX2 -qopt-prefetch=3 -fopenmp -O3'. A commented g++ alternative uses -march=native -mavx -mavx2 -fopenmp -O3. The icpc version is not stated. |
| **Adoption** | 17 stars; paper: Bian et al., Future Generation Computer Systems 116 (2021) 371-392 |
| **Last commit** | 2022-04-04 |
| **Links** | [repository](https://github.com/nulidangxueshen/ALBUS) · [benchmark](https://github.com/nulidangxueshen/ALBUS) |

## Verdict

The FGCS 2021 paper abstract (quoted in the README) reports, on a dual-socket Xeon E5-2670 v3 with 20 regular and 20 irregular UF matrices, average speedups of 1.48x over MKL on regular and 2.44x on irregular matrices (up to 2.31x and 5.37x), plus 1.32-1.59x over CSR5 and Merge; the README's own table, on a dual Xeon Gold 6242 with icpc -O3 -xCORE-AVX2, gives ALBUS vs CSR5 vs CVR GFlops only (e.g. rma10 94.5 vs 42.1 vs 65.8) with empty MKL and Merge columns. Timing excludes the partition step and comes from repeated cache-warm iterations; the comparison harnesses for MKL, CSR5 and Merge are not in the repo.

## Use it when

- Multi-threaded double-precision SpMV on x86 CPUs with AVX2/FMA where the matrix is already in CSR and you cannot afford a format conversion (CSR5, CVR and SPC5 all need one).
- Matrices with skewed row lengths (web, social and circuit graphs such as webbase-1M, web-Stanford, scircuit) where row-split OpenMP CSR loses to load imbalance.
- Iterative solvers that reuse one matrix and thread count for many products, so the one-off partition is amortized (it is cheap anyway).
- As a short, readable reference for nonzero-balanced CSR SpMV to port into your own code.

## Skip it when

- You need a library: there is no build target, versioning, tests beyond a printout check, or API beyond two inline functions; MKL's CSR SpMV or merge-spmv are better-supported options.
- Single precision, complex values, transposed products, y = alpha\*A\*x + beta\*y or SpMM: only real double y = A\*x is implemented.
- Non-x86 targets or CPUs without AVX2/FMA (use the OpenMP-only variant, which loses the SIMD part), and matrices with 2^31 or more nonzeros (int indices).
- Inputs that may contain Inf or NaN: the 3-remainder SIMD paths load one value past the row and multiply it by zero, so a non-finite neighbor value turns the row into NaN (see gotchas).
- Production use without your own testing: abandoned since April 2022, no issues filed, and the MKL and Merge speedups are only in the paper abstract.

## How it is fast

The nonzeros are split into equal contiguous chunks per OpenMP thread (binary search over row_ptr finds each chunk's start row and offset), so a thread may start and end mid-row; the partial sums of the boundary rows go to a small per-thread buffer and are added serially after the parallel region. This is nonzero-based load balancing in the spirit of CSR5 and merge-based SpMV, but it keeps plain CSR and the partition costs only O(threads log rows). Inside each row the AVX2 variant gathers x values with _mm256_set_pd and accumulates with FMA, with specialized paths for rows of 1-4 nonzeros, software prefetch and Intel unroll pragmas.

## Compared with alternatives

Pick ALBUS over CSR5, CVR or SPC5 when you must keep plain CSR with no format conversion and target AVX2 CPUs; its README table shows it ahead of CSR5 on all 28 matrices and ahead of CVR on 25 of 28 on a dual Xeon Gold 6242. merge-spmv also keeps CSR (merge-path partition) and has an SC'16 evaluation over 4,201 matrices, and SPC5 is the catalogued choice for AVX-512 or SVE.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | OpenMP; AVX2 and FMA intrinsics for the AVX2 variant |
| **Minimum toolchain** | not documented; Makefiles target Intel icpc (version not stated) with a commented-out g++ line (-march=native -mavx -mavx2 -fopenmp -O3); code uses the register keyword (removed in C++17) and Intel-specific pragmas |
| **Platforms** | x86-64 with AVX2+FMA for the SIMD variant; the OpenMP-only variant is portable C++ |
| **Thread safety** | not documented; SPMV_DOU opens its own OpenMP parallel region and writes a shared mid_ans scratch buffer, so concurrent calls need separate scratch, and the partition is computed for omp_get_max_threads() at albus_balance time and must be recomputed if the thread count changes |
| **Drop-in for the baseline** | partial: takes standard 0-based CSR arrays (int row_ptr/col_idx, double values) like MKL's CSR SpMV, but it is a copy-in kernel with its own call signature, requires an output array of nrows+1 entries and a per-thread scratch buffer, and supports only y = A\*x |

## Gotchas

- Memory-safety and NaN edge case: for rows whose length is 3 or leaves remainder 3 mod 4, the kernel does a full _mm_load_pd/_mm256_load_pd that reads one double past the row (past the end of mtx_val for the last row) and multiplies it by a zero lane; the over-read is out of bounds for the last row, and a neighboring Inf/NaN value yields NaN.
- The _mm256_load_pd/_mm_load_pd calls are aligned loads at row starts that are not generally 32-byte aligned; this only works when the compiler folds them into VEX memory operands (as at -O3), so a -O0 or different-compiler build can fault.
- The benchmark ignores the iterations argument: ReadFile sets it to 4\*min(200000, max(100, 2^34/nnz)) for both warm-up and timed loops on the same matrix and vector, so mid-size matrices run cache-warm; the README's dense 2048x2048 example implies about 457 GB/s of matrix traffic (derived from page data: 4,194,304 nonzeros x 12 bytes in 0.110 ms).
- The built-in correctness check accepts up to 1% relative error per row against serial CSR, and the Matrix Market reader keeps only the real part of complex files and treats anything but 'symmetric' (e.g. hermitian, skew-symmetric) as general.

## Known shortcomings

- Preprocessing excluded from timing; real Makefile flags differ from the README example; paper unreachable here (sciencedirect blocked).
- Record corrected: ALBUS uses plain CSR with no format conversion; preprocessing is only a thread partition. Correctness: rows of length 3 or 3 mod 4 read one double past the row (out of bounds on the last row; a neighbouring Inf/NaN turns the row into NaN); aligned SIMD loads at unaligned row starts. Check accepts 1% error. Bench ignores the iterations argument and runs cache-warm (README dense example works out to \~457 GB/s, derived from page data).

## Caveats and trade-offs

Peer-reviewed paper but the authors' own benchmark. The MKL column of the README table is empty, so the MKL ratios appear only in the paper abstract (the paper itself was not reachable: sciencedirect.com is blocked here). The README table (Xeon Gold 6242) and the abstract (E5-2670 v3) use different CPUs. ALBUS loses to CVR on cant, ins2 and pdb1HYS in the README table. main.cpp runs the albus_balance preprocessing outside the timed loop, after a warm-up of the same number of iterations, so the GFlops exclude preprocessing. No comparison harness for MKL, CSR5 or Merge is in the repo. MKL is not one of SuiteSparse, Eigen sparse or PETSc. Hardware is 2014-2019 era and the repo has been idle since April 2022 (README edits). [retier] ALBUS uses plain CSR with no format conversion; preprocessing is only a thread partition. Kernel reads one double past rows of length 3 mod 4; repo bench runs cache-warm and ignores the iterations argument.

Research code (main.cpp plus headers, not a packaged library); needs a conversion/preprocessing step into the ALBUS format; AVX2-oriented and built with the Intel compiler; OpenMP and OpenMP+AVX2 variants.

## Maintenance

Abandoned since 2022-04-04 (README edits) but MIT-licensed and a few hundred lines, so it is easy to vendor as a reference kernel after fixing the tail over-read and aligned loads.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed (Future Generation Computer Systems 116, 2021) speedups vs MKL, CSR5 and Merge are quoted in the README's abstract. ALBUS code and Makefiles are public, but the harnesses for MKL, CSR5 and Merge are not in the repo, and the MKL column of the README table is empty, so it falls short of A.
- **Verifier notes:** README numbers and abstract ratios match the record exactly. Fixed the flags (the actual Makefiles differ from the README's example) and noted that preprocessing is excluded from the timing. Metadata confirmed: MIT, 17 stars, not a fork, last commit 2022-04-04 (abandoned, &gt;3 years before today).
- **Fields the verifier corrected:** `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://github.com/nulidangxueshen/ALBUS>
  - <https://github.com/nulidangxueshen/ALBUS/commits/master>
  - <https://raw.githubusercontent.com/nulidangxueshen/ALBUS/HEAD/README.md>
  - <https://raw.githubusercontent.com/nulidangxueshen/ALBUS/HEAD/ALBUS%28OpenMP%2BAVX2%29/Makefile>
  - <https://raw.githubusercontent.com/nulidangxueshen/ALBUS/HEAD/ALBUS%28OpenMP%2BAVX2%29/main.cpp>
  - <https://raw.githubusercontent.com/nulidangxueshen/ALBUS/HEAD/ALBUS%28OpenMP%29/Makefile>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/nulidangxueshen/ALBUS/HEAD/README.md>
  - <https://raw.githubusercontent.com/nulidangxueshen/ALBUS/HEAD/ALBUS%28OpenMP%2BAVX2%29/main.cpp>
  - <https://raw.githubusercontent.com/nulidangxueshen/ALBUS/HEAD/ALBUS%28OpenMP%2BAVX2%29/Makefile>
  - <https://raw.githubusercontent.com/nulidangxueshen/ALBUS/HEAD/ALBUS%28OpenMP%2BAVX2%29/Albus_spmv.h>
  - <https://raw.githubusercontent.com/nulidangxueshen/ALBUS/HEAD/ALBUS%28OpenMP%2BAVX2%29/Storage_format.h>
  - <https://raw.githubusercontent.com/nulidangxueshen/ALBUS/HEAD/ALBUS%28OpenMP%29/Albus_spmv.h>
  - <https://github.com/nulidangxueshen/ALBUS/issues?q=is%3Aissue>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/nulidangxueshen/albus`) · [data/wave8/enrich/raw/github_com_nulidangxueshen_albus.json](../../../data/wave8/enrich/raw/github_com_nulidangxueshen_albus.json) (enrichment confidence 0.8)

</details>
