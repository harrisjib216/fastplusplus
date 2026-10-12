# CVR (Compressed Vectorization-oriented sparse Row)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Sparse matrices and solvers](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `MIT` · 🟡 stale

> CGO 2018 AVX-512 SpMV format for Xeon Phi Knights Landing that beats MKL CSR SpMV, especially on scale-free graphs.

| | |
|---|---|
| **Beats** | Intel MKL CSR SpMV; also MKL CSR(I) inspector-executor, ESB, VHCC and CSR5 |
| **Claimed result** | Paper (CGO 2018, PDF in repo): on scale-free matrices CVR is up to 40x (2.84x on average) faster than MKL and up to 1.70x (1.33x on average) faster than the best existing approach. On HPC matrices it is up to 17x (1.22x on average in the introduction, 1.24x in Section 7.1) faster than MKL and up to 1.57x (1.10x on average) faster than the best existing approach. Peak per-matrix ratios over MKL: wiki-talk 39.53x, ins2 17.58x. Table 3 domain averages, GFlop/s CVR vs MKL: web graph 7.28 vs 2.92, routing 17.11 vs 2.73, road 9.57 vs 4.24. |
| **Workload** | Double-precision SpMV (1000 iterations, best SMT thread count per method) on 58 sparse matrices from SNAP and the SuiteSparse collection: 30 scale-free and 28 HPC matrices, on Xeon Phi Knights Landing with MCDRAM in flat mode. |
| **Metric** | throughput |
| **Hardware** | Intel Xeon Phi 7250 (Knights Landing, 68 cores, 16 GB MCDRAM + 96 GB DDR4), CentOS 7.3 |
| **Compiler and flags** | Intel C/C++ compiler 17.04, flags -MIC-AVX512 -O3 |
| **Adoption** | 24 stars; CGO 2018 artifact repository |
| **Last commit** | 2024-02-12 |
| **Links** | [repository](https://github.com/puckbee/CVR) · [benchmark](https://raw.githubusercontent.com/puckbee/CVR/HEAD/CVR-%20Efficient%20Vectorization%20of%20SpMV%20on%20X86%20Processors.pdf) |

## Verdict

On a Xeon Phi 7250 (68 cores, MCDRAM flat mode, icpc 17.04 -O3, 1000 iterations, best SMT thread count per method), double-precision CVR SpMV averaged 2.84x MKL CSR (up to 39.53x on wiki-talk) on 30 scale-free matrices and 1.22-1.24x MKL (up to 17.58x on ins2) on 28 HPC matrices, and 1.33x / 1.10x over the best of CSR(I), ESB, VHCC and CSR5; these are the authors' own peer-reviewed numbers.

## Use it when

- You still run Xeon Phi Knights Landing (AVX-512 MIC, MCDRAM in flat mode) and need double-precision SpMV on power-law matrices: web graphs, social, wiki, routing and FSM matrices, where the paper's domain averages were 2.5-6.3x MKL.
- Iterative solvers or graph kernels running tens to thousands of SpMVs on the same matrix, where CVR's low conversion cost (often under ten iterations to amortize, per the paper) matters.
- Matrices with many very short rows (for example ins2 at 4 nnz/row, 17.58x over MKL), where row-per-lane packing keeps all 8 lanes busy.
- As a reference design for row-per-SIMD-lane SpMV with feeding and stealing, to port to current AVX-512 Xeons, ARM SVE or GPUs (the authors planned a CUDA/OpenCL port that never appeared in the repo).

## Skip it when

- Any non-KNL machine: the artifact appendix says CVR 'only supports Xeon Phi currently', the Makefile hard-codes icpc -xMIC-AVX512, and Intel has discontinued both KNL and the classic icpc compiler.
- Wide, short-and-fat matrices with hundreds or thousands of nonzeros per row (connectus, 12month1, rail4284 in the paper), where VHCC's 2D jagged partition beat CVR.
- Regular FEM/HPC matrices where you already use MKL or CSR5: the paper's HPC average is only 1.24x over MKL and 1.10x over the next best format.
- Single precision, complex values, transposed products or multi-vector SpMM: the build is double-only (FLOAT_TYPE fixed to double) and only y = A\*x is implemented.
- Production use: research code with leftover debug printing, a single 2018 code drop, no tests beyond the built-in result check, and no issues or maintainer activity since then.

## How it is fast

Each SIMD lane owns one row at a time (8 lanes for double on AVX-512), so a single 512-bit fused multiply-add advances 8 rows at once and the per-row reduction disappears; when a lane's row ends, a 'tracker' is fed the next non-empty row, and once rows run out, empty trackers steal nonzeros from longer ones to keep lanes balanced. Conversion records (position, write-back row) pairs in a rec vector so results are written to y at the right point during the streaming kernel. Processing many rows together improves reuse of x; the paper reports an order-of-magnitude lower L2 miss ratio than the other formats and the cheapest conversion (median 2.14 MKL-iterations to amortize on scale-free matrices, versus 5.36 for CSR5 and 49-2,653 for CSR(I), ESB and VHCC).

## Compared with alternatives

Choose CVR over CSR5 or merge-spmv only on Knights Landing with scale-free matrices, where the paper measured 1.33x average over the best competitor (usually CSR5); on current AVX-512 or ARM SVE CPUs, SPC5 (maintained, block-based, MKL baseline) or CSR5/merge-spmv (portable, CPU and GPU) are the practical picks, and ALBUS targets MKL on regular matrices on Haswell-era Xeons.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | OpenMP; Intel C/C++ compiler 17 with AVX-512; numactl to place data in MCDRAM; Intel MKL only for the prebuilt comparison binaries |
| **Minimum toolchain** | icpc 17.04 (-O3 -xMIC-AVX512 -qopenmp); building with GCC or Clang is not documented |
| **Platforms** | x86-64 Xeon Phi Knights Landing only (AVX-512F/PF/ER, MCDRAM flat mode); Linux (CentOS 7.3 tested) |
| **Thread safety** | not documented; the kernel spreads one matrix over OpenMP threads and merges rows split between threads with omp atomic adds |
| **Drop-in for the baseline** | no |

## Gotchas

- Conversion allocates a second copy of values and int32 column indices (nnz entries each) plus a rec array of about 2 x numRows ints, so memory is roughly double the CSR footprint while both exist; all indices are 32-bit, and a kernel comment notes the padded tail uses column 0 with value 0.
- The kernel uses _mm512_permute4f128_epi32 and _mm512_i32logather_pd and the Intel-specific '#pragma noprefetch', which tie it to the Intel classic compiler; expect porting work before it compiles elsewhere.
- The printed throughput is nnz divided by time, i.e. one flop per nonzero rather than the usual 2\*nnz, so its GFlop/s figures are half what most SpMV papers would report for the same time.
- The MKL, CSR(I) and ESB comparison programs ship only as binaries (sources withheld over licensing), and every method's SMT thread count was tuned separately, so the baseline side cannot be audited or rebuilt.

## Known shortcomings

- MKL/CSR-I/ESB comparison harness ships as binaries only (sources withheld); needs KNL hardware; paper is inconsistent (intro: HPC avg 1.22x over MKL, Section 7.1: 1.24x).
- Paper appendix says it 'only supports Xeon Phi currently'; needs the discontinued icpc compiler (Intel-only intrinsics). Printed GFlops count 1 flop per nonzero, half the usual 2. MKL, CSR(I) and ESB baselines ship as binaries only.

## Caveats and trade-offs

Peer-reviewed with a public CVR artifact (spmv.cpp, Makefile, run scripts), but the MKL, CSR(I) and ESB comparison programs are binaries only (the authors withheld the sources over licensing), so the baseline side cannot be inspected or rebuilt. The code supports only Knights Landing (AVX-512 MIC, icpc 17, MCDRAM in flat mode), which Intel discontinued, so the numbers cannot be reproduced on current hardware without porting. Numbers are the authors' own; the best SMT thread count and parameters were picked per method. The intro (1.22x) and Section 7.1 (1.24x) disagree on the HPC average over MKL. The README contains no numbers. MKL is not one of SuiteSparse, Eigen sparse or PETSc. Dormant since August 2018 apart from a February 2024 README edit.

Needs a one-time conversion from CSR to the CVR format; the paper reports the lowest preprocessing overhead among the compared formats but scale-free matrices still need many iterations to amortize it for some competitors. Written for AVX-512 (Knights Landing); building the comparison binaries needs MKL. SpMV kernel only, not a solver.

## Maintenance

Dormant since 2018 apart from a 2024 README edit (24 stars, MIT), so it is copyable but effectively frozen to discontinued Knights Landing hardware and the Intel classic compiler.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification A, tier now B.
- **Tier reason:** Peer-reviewed CGO 2018 paper (PDF in the repo, with an artifact appendix) that states compiler (icpc 17.04, -MIC-AVX512 -O3) and CPU (Xeon Phi 7250). Not A, because the MKL baseline harness ships only as a prebuilt binary (solutions_for_comparison/bin; the README says the MKL, CSR-I and ESB sources are withheld), so the benchmark code against the named baseline is not public.
- **Verifier notes:** Numbers verified in the paper PDF (abstract, Section 1, Table 3, Section 7.1). Downgraded A to B only because the MKL baseline harness is binary-only. Metadata confirmed: MIT, 24 stars, not a fork, last commit 2024-02-12 (stale).
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://github.com/puckbee/CVR>
  - <https://github.com/puckbee/CVR/commits/master>
  - <https://github.com/puckbee/CVR/tree/master/solutions_for_comparison>
  - <https://raw.githubusercontent.com/puckbee/CVR/HEAD/README.md>
  - <https://raw.githubusercontent.com/puckbee/CVR/HEAD/CVR-%20Efficient%20Vectorization%20of%20SpMV%20on%20X86%20Processors.pdf>
- **Sources the enricher read:**
  - <https://github.com/puckbee/CVR>
  - <https://github.com/puckbee/CVR/issues?q=is%3Aissue>
  - <https://github.com/puckbee/CVR/pulls>
  - <https://raw.githubusercontent.com/puckbee/CVR/HEAD/README.md>
  - <https://raw.githubusercontent.com/puckbee/CVR/HEAD/Makefile>
  - <https://raw.githubusercontent.com/puckbee/CVR/HEAD/spmv.cpp>
  - <https://raw.githubusercontent.com/puckbee/CVR/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/puckbee/CVR/HEAD/CVR-%20Efficient%20Vectorization%20of%20SpMV%20on%20X86%20Processors.pdf>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/puckbee/cvr`) · [data/wave8/enrich/raw/github_com_puckbee_cvr.json](../../../data/wave8/enrich/raw/github_com_puckbee_cvr.json) (enrichment confidence 0.82)

</details>
