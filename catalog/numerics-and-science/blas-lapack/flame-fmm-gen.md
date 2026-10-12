# fmm-gen (Generating Families of Practical Fast Matrix Multiplication Algorithms)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [BLAS and LAPACK](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Python (code generator emitting C)` · `BSD-3-Clause` · 🔴 abandoned

> Python generator for Strassen-like DGEMM variants that fuse the extra additions into BLIS-style packing and micro-kernels; claims wins over conventional GEMM.

| | |
|---|---|
| **Beats** | Conventional GEMM. The public harness (the test driver emitted by meta/misc_gen.py) times the generated Strassen-like routine against the project's own BLIS-style dgemm (bl_dgemm in common/dgemm/my_dgemm.c, built on the same AVX 8x4 micro-kernel) and prints the effective GFLOPS of both. MKL is linked (-DUSE_BLAS, -mkl=parallel) only for bl_dgemm_ref. Whether the IPDPS 2017 paper also compared against BLIS or MKL dgemm could not be checked. |
| **Claimed result** | README abstract: 'Our implementations demonstrate a performance benefit over conventional GEMM on single core and multi-core systems.' No numeric speedup appears on any opened page. |
| **Workload** | Generated Strassen-like fast matrix multiplication (20+ algorithm variants, multi-level, arbitrary matrix sizes and shapes) with the matrix additions fused into GEMM packing and micro-kernels, run on single-core and multicore systems and compared with a performance model. |
| **Metric** | throughput |
| **Hardware** | Maverick supercomputer at TACC (fmm_artifact.pdf; CPU model not stated on any opened page) |
| **Compiler and flags** | icc/icpc 15.0.3 with the GCC 4.9.3 standard library (fmm_artifact.pdf); -O3 -openmp -mavx -fPIC -DUSE_BLAS, linked with -mkl=parallel (common/make.inc.files/make.intel.inc with COMPILER_OPT_LEVEL=O3 from common/sourceme.sh) |
| **Adoption** | 12 stars, 7 forks |
| **Last commit** | 2017-07-07 |
| **Links** | [repository](https://github.com/flame/fmm-gen) · [benchmark](https://github.com/flame/fmm-gen) |

## Verdict

Only a qualitative claim was readable: the README and artifact say the generated FMM implementations 'demonstrate a performance benefit over conventional GEMM on single core and multi-core systems', and the public harness times the generated routine against the project's own BLISlab dgemm built on the same AVX 8x4 micro-kernel (icc 15.0.3, -O3 -mavx, TACC Maverick). A search-result snippet of the arXiv version (page not opened) gives the test machine as a dual-socket Intel Xeon E5-2680 v2 (Ivy Bridge) at 3.54 GHz on one core and 3.10 GHz on ten, and says the comparison included a BLIS-based DGEMM and Intel MKL DGEMM; no numbers were seen.

## Use it when

- Studying or prototyping Strassen-like DGEMM inside a BLIS-style GEMM, including choosing among 20+ algorithms by size and shape with the included performance model.
- Large double-precision products on hardware close to the paper's (an AVX Ivy Bridge-class Xeon), where the authors report gains over conventional GEMM on one core and on ten cores.
- Non-square and rank-k-like shapes, where the paper argues that fusing additions into packing helps compared with buffer-based Strassen implementations.
- As a reference design when building fused FMM into your own GEMM (the sibling tblis-strassen applies the same idea to tensor contraction).

## Skip it when

- As a production BLAS: double precision only, no alpha/beta or transposes, generated per algorithm, and no packaging.
- On current CPUs without retuning: the micro-kernels are AVX inline assembly (vmulpd/vaddpd, no FMA) with an 8x4 register block and Ivy Bridge cache blocking (MC=96, KC=256, NC=4096), so today's BLIS, OpenBLAS or MKL kernels with FMA or AVX-512 have a higher peak than the in-repo baseline the generated code was compared with.
- When accuracy matters more than a modest speedup: Strassen-like algorithms have weaker error bounds than classical GEMM, and this repo documents no stability testing.
- When you need published numbers: none appear in the repo, and the paper (cs.utexas.edu, arxiv.org) was unreachable from this environment.
- When you need maintained code: the last commit was 2017-07-07, the scripts are Python 2.7, and paths for TACC Maverick and SLURM are hard-coded.

## How it is fast

Each fast algorithm is a [U,V,W] coefficient triple, and multi-level algorithms (including mixed shapes such as &lt;2,2,2&gt; then &lt;3,2,3&gt;) are built with Kronecker products of those triples. Instead of forming the sums of submatrices in temporary buffers, the 'ABC' variant folds the A and B sums into the GEMM packing routines and the C updates into generated micro-kernels, so there is no extra workspace and less memory traffic; 'AB' and 'naive' variants are also generated for comparison. Parallelism reuses GEMM's own loop-level data parallelism instead of task parallelism, and a performance model predicts which algorithm suits a given size and shape.

## Compared with alternatives

Pick fmm-gen over fast-matmul (Benson and Ballard) when you want the additions fused into GEMM packing with no extra workspace and plain data parallelism, and you are willing to own the GEMM kernel; fast-matmul layers fast algorithms on a vendor dgemm and ships measured timings against MKL. For tensor contractions use tblis-strassen, from the same group.

## Integration

| | |
|---|---|
| **Form** | source-drop (Python 2.7 code generator emitting C99 plus AVX inline assembly; builds a static and shared library per generated algorithm) |
| **Dependencies** | Python 2.7; Intel icc/icpc 15+ by default (sourceme.sh sets BLISLAB_USE_INTEL=true; a GNU make include is also selectable); OpenMP; Intel MKL linked when BLISLAB_USE_BLAS=true (only for the bl_dgemm_ref reference path); SLURM optional |
| **Minimum toolchain** | C99 compiler with AVX and OpenMP; artifact used icc/icpc 15.0.3 with GCC 4.9.3; Python 2.7 |
| **Platforms** | x86-64 with AVX (artifact: 'x86-64 processor that supports AVX instructions'); Linux or macOS per the artifact description; no ARM or other kernels |
| **Thread safety** | not documented; the multithreaded build reads its thread count from the BLISLAB_IC_NT environment variable and OMP_NUM_THREADS |
| **Drop-in for the baseline** | no |

## Gotchas

- The in-repo GEMM requires C and ldc to be aligned (my_dgemm.c: 'C must be aligned', 'ldc must also be aligned'); the test driver pads ldc to a multiple of 8 and allocates n+4 columns, so pass C the same way.
- The test driver accumulates C += A\*B over three timed repeats for both routines and reports min-time effective GFLOPS, with the FMM run first and the conventional run second on the same inputs.
- control.py builds with os.system('source sourceme.sh; make ...'), which runs under /bin/sh; where /bin/sh is dash (Debian, Ubuntu) `source` fails, and sourceme.sh hard-codes BLAS_DIR=/u/jianyu/blis and OMP_NUM_THREADS=10.
- The make include uses -openmp and -mkl=parallel, flags of the classic Intel compilers; current oneAPI icx and GCC need different flags.

## Known shortcomings

- No number on any reachable page (IPDPS 2017 paper blocked here); the public harness times FMM against its own BLISlab dgemm (common/dgemm/my_dgemm.c), not MKL/BLIS; icc 15.0.3 -O3 -mavx on TACC Maverick, no CPU model; retier candidate once the paper is reachable.
- Still no numbers reachable from this session. Kernels are AVX without FMA, 8x4, tuned for Ivy Bridge; build uses `source` via /bin/sh (fails on dash); Python 2.7. Follow-up: the paper (arXiv 1611.01120) names dual-socket Xeon E5-2680 v2 with BLIS and MKL DGEMM baselines, so a B/A retier is possible where arxiv.org is reachable.

## Caveats and trade-offs

No numbers were seen: the IPDPS 2017 paper (Huang, Rice, Matthews, van de Geijn), which holds all the measurements, is on egress-blocked hosts (cs.utexas.edu, arxiv.org 1611.01120). The repo's artifact description gives icc 15.0.3 and 'Maverick supercomputer at TACC' but no CPU model, and says only that relative effective-GFLOPS trends should match the paper's curves. The public test driver compares against the authors' own BLISlab-style dgemm, not against a vendor BLAS. It is a research code generator (Python 2.7 scripts emitting C with AVX inline assembly, SLURM/Maverick paths hard-coded in config.py and sourceme.sh). There have been no commits since 2017-07-07. arbenson/fast-matmul is catalogued separately and is a different code base.

Python scripts generate and compile C code per algorithm and partition (OpenMP, config.py and SLURM scripts for cluster runs). Fast matrix multiplication trades numerical stability and extra additions for fewer multiplications, and only helps above some matrix size; no BLAS-compatible drop-in interface is shown.

## Maintenance

Abandoned since 2017-07-07 (12 stars, no open issues) and BSD-3-Clause; usable as a reference design or for generating kernels to retune, not as a library to link.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification B, tier now D.
- **Tier reason:** No number appears on any page I could open: the README and fmm_artifact.pdf only say the generated FMM shows 'a performance benefit over conventional GEMM'. The IPDPS 2017 paper (the only source of numbers) is hosted on cs.utexas.edu and arxiv.org, both egress-blocked here. The public harness (the test driver emitted by meta/misc_gen.py) does time the generated FMM against a conventional dgemm, and compiler and flags are public, but with no numbers and no CPU model the tier cannot stay above D.
- **Verifier notes:** Downgraded B to D because no page with numbers could be opened. A retier check to B (or A if the paper names the CPU model) is worth running once arxiv.org/abs/1611.01120 or the IPDPS paper can be reached. Metadata was checked on github.com: BSD-3-Clause (LICENSE text), 12 stars, 7 forks, not a fork, not archived, last commit 2017-07-07, so 'abandoned' is correct. Kept rather than rejected because it is the public artifact of a peer-reviewed IPDPS paper.
- **Fields the verifier corrected:** `baseline`, `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://github.com/flame/fmm-gen>
  - <https://github.com/flame/fmm-gen/commits>
  - <https://github.com/flame/fmm-gen/tree/master>
  - <https://github.com/flame/fmm-gen/tree/master/common>
  - <https://github.com/flame/fmm-gen/tree/master/meta>
  - <https://github.com/flame/fmm-gen/tree/master/common/test>
  - <https://github.com/flame/fmm-gen/tree/master/common/make.inc.files>
  - <https://raw.githubusercontent.com/flame/fmm-gen/HEAD/README.md>
  - <https://raw.githubusercontent.com/flame/fmm-gen/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/flame/fmm-gen/HEAD/fmm_artifact.pdf>
  - <https://raw.githubusercontent.com/flame/fmm-gen/HEAD/common/make.inc.files/make.intel.inc>
  - <https://raw.githubusercontent.com/flame/fmm-gen/HEAD/common/make.inc.files/make.inc>
  - <https://raw.githubusercontent.com/flame/fmm-gen/HEAD/common/sourceme.sh>
  - <https://raw.githubusercontent.com/flame/fmm-gen/HEAD/meta/misc_gen.py>
  - <https://raw.githubusercontent.com/flame/fmm-gen/HEAD/common/dgemm/bl_dgemm_ref.c>
  - <https://raw.githubusercontent.com/flame/fmm-gen/HEAD/common/dgemm/my_dgemm.c>
- **Sources the enricher read:**
  - <https://github.com/flame/fmm-gen>
  - <https://github.com/flame/fmm-gen/tree/master/meta>
  - <https://github.com/flame/fmm-gen/issues>
  - <https://raw.githubusercontent.com/flame/fmm-gen/HEAD/README.md>
  - <https://raw.githubusercontent.com/flame/fmm-gen/HEAD/fmm_artifact.pdf>
  - <https://raw.githubusercontent.com/flame/fmm-gen/HEAD/meta/misc_gen.py>
  - <https://raw.githubusercontent.com/flame/fmm-gen/HEAD/meta/control.py>
  - <https://raw.githubusercontent.com/flame/fmm-gen/HEAD/meta/config.py>
  - <https://raw.githubusercontent.com/flame/fmm-gen/HEAD/meta/abc_micro_kernel_gen.py>
  - <https://raw.githubusercontent.com/flame/fmm-gen/HEAD/common/sourceme.sh>
  - <https://raw.githubusercontent.com/flame/fmm-gen/HEAD/common/make.inc.files/make.intel.inc>
  - <https://raw.githubusercontent.com/flame/fmm-gen/HEAD/common/dgemm/my_dgemm.c>
  - <https://raw.githubusercontent.com/flame/fmm-gen/HEAD/common/include/bl_config.h>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/flame/fmm-gen`) · [data/wave8/enrich/raw/github_com_flame_fmm_gen.json](../../../data/wave8/enrich/raw/github_com_flame_fmm_gen.json) (enrichment confidence 0.65)

</details>
