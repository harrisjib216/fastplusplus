# OpSparse (optimized GPU SpGEMM framework)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Sparse matrices and solvers](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Research CUDA hash-based SpGEMM (C = A\*B, CSR, FP64) for V100; paper reports 7.35x average over cuSPARSE.

| | |
|---|---|
| **Beats** | cuSPARSE SpGEMM, nsparse and spECK |
| **Claimed result** | OpSparse achieves on average 7.35x (up to 27.8x), 1.43x (up to 1.81x) and 1.52x (up to 2.04x) speedups over cuSPARSE, nsparse and spECK, respectively (snippet only). |
| **Workload** | Sparse general matrix-matrix multiplication (SpGEMM, C = A\*A) on an NVIDIA Tesla V100 over 26 commonly used matrices (paper abstract per search result); the repo harness downloads webbase-1M and has reg_opsparse, reg_cusparse, nsparse and spECK drivers. |
| **Metric** | throughput |
| **Hardware** | NVIDIA Tesla V100, CUDA 11.2, Ubuntu 18.04 LTS (README 'Tested environment'); CPU model not stated |
| **Compiler and flags** | nvcc -O3 -arch=compute_70 -code=sm_70 -Xcompiler -fopenmp (OpSparse/Makefile); CUDA 11.2 |
| **Adoption** | 16 stars, 4 forks, 9 commits |
| **Last commit** | 2022-08-23 |
| **Links** | [repository](https://github.com/lorentzbf/OpSparse) · [benchmark](https://arxiv.org/abs/2206.07244) |

## Verdict

Per the IEEE Access 2022 abstract (search snippets; the paper was not opened), on 26 common SuiteSparse matrices on a Tesla V100 with CUDA 11.2, OpSparse averages 7.35x (up to 27.8x) over cuSPARSE SpGEMM, 1.43x (up to 1.81x) over nsparse and 1.52x (up to 2.04x) over spECK, in FP64. The repo holds the harness (reg_opsparse, reg_cusparse, nvcc -O3 sm_70) but no result files, and later third-party studies find smaller margins or spECK ahead.

## Use it when

- Repeated SpGEMM (A\*A, A\*P, Galerkin products in AMG setup, graph algorithms) on a Volta-class GPU, where cuSPARSE SpGEMM time dominates
- FP64 CSR matrices with 32-bit indices and up to about 2^31 nonzeros in C
- As a reference implementation or starting point when writing your own binned hash SpGEMM, since the kernels are short and readable
- Benchmark studies: the repo already wires cuSPARSE, nsparse and spECK drivers to the same matrix loader

## Skip it when

- On A100/H100-class GPUs, where independent results put it behind spECK: Ocean (ICS 2026, 337 matrices on A100) reports 2.6x over OpSparse but only 1.4x over spECK
- When you need FP32, complex, 64-bit indices, or a C = alpha\*A\*B + beta\*C API: values are hard-wired to double and indices to int
- Production code that needs a maintained library: 9 commits, last one 2022-08-23, no tests, and the result check against cuSPARSE is commented out in the drivers
- Non-NVIDIA hardware or non-x86 hosts: CUDA only, and the timer reads rdtsc and the CPUID leaf 0x16 base frequency
- Turing-class GPUs (64 KB shared-memory limit per block): the large-row kernels request 98,304 bytes of dynamic shared memory

## How it is fast

Rows are binned by an upper bound on their output size (8 bins, ranges sized for about 1.2x hash-table headroom). Each bin then runs a kernel sized to it: a partial warp of 4 threads per row with a 32-slot table for tiny rows, thread-block shared-memory hash tables of 512 to 8192 slots, a 96 KB dynamic-shared-memory kernel, and a global-memory hash fallback for rows that overflow. The hash tables use linear probing with atomicCAS and a multiplicative hash (column \* 107), and each row's output is put in column order by an in-block counting sort. Per the paper abstract, the other gains come from fewer hash-table accesses, packing all metadata into one combined allocation, and overlapping cudaMalloc of C with kernel execution across 8 streams.

## Compared with alternatives

Pick spECK (GPUPeople/spECK) by default: on the third-party sets found (Ocean on A100; the ACM study cited in the record's caveats, which puts OpSparse at 4.91x and spECK at 5.67x average over cuSPARSE) it is as fast or faster. OpSparse is the more compact code to adapt. TileSpGEMM reports beating spECK on 94 of 142 matrices, and Kokkos Kernels SpGEMM is the maintained, portable choice.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | CUDA toolkit (tested 11.2) with cuSPARSE and CUB, OpenMP (host flop count), CUDA samples headers on the include path |
| **Minimum toolchain** | nvcc from CUDA 11.x (tested 11.2) with g++; Makefile hard-codes -arch=compute_70 -code=sm_70 |
| **Platforms** | NVIDIA GPUs, sm_70 (V100) as shipped; x86-64 host for the rdtsc-based timer |
| **Thread safety** | not documented; each call creates and destroys its own 8 CUDA streams and device buffers through a Meta object, so share neither Meta nor CSR objects across host threads |
| **Drop-in for the baseline** | partial — computes the same product as cusparseSpGEMM but through its own CSR/Meta classes and an opsparse(A, B, C, meta, timing) call; you would wrap or extract the kernels |

## Gotchas

- The Makefile embeds only sm_70 SASS (no PTX), so the binaries will not run on Ampere or Hopper until you change GENCODE
- Meta::release frees host memory from malloc with delete[] (combined_mem), which is undefined behaviour; fix it before embedding
- CUDA errors throw std::exception after printing; there is no error-code API
- The cuSPARSE driver times cusparseCreate/cusparseDestroy and buffer allocation inside every call (the OpSparse timing also includes its own allocations), which can inflate the cuSPARSE baseline on small matrices

## Known shortcomings

- Peer-reviewed IEEE Access maxima only; one MIT LICENSE covers bundled nsparse/spECK code.
- The drivers have the cuSPARSE result check commented out, and the cuSPARSE timed loop includes cusparseCreate/Destroy and the buffer malloc on every call, inflating the baseline. Meta::release frees malloc memory with delete[] (undefined behaviour). The Makefile builds sm_70 SASS only with no PTX, so no A100/H100 run without edits; the 96 KB shared-memory kernels fail on Turing; the timer is x86 rdtsc plus CPUID 0x16.

## Caveats and trade-offs

Numbers come from the abstract of the IEEE Access 2022 paper (arXiv 2206.07244) as quoted in search results; the paper itself was not opened (arxiv, ieeexplore and hkust.edu.hk hosts are egress-blocked). The 'up to' figures (27.8x, 1.81x, 2.04x) were confirmed by this verifier's search; the averages (7.35x, 1.43x, 1.52x) come from the search agent's snippet. A later third-party study ('Optimizing General Sparse Matrix-Matrix Multiplication on the GPU', ACM) reports average speedups over cuSPARSE of 4.91x for OpSparse versus 5.67x for spECK and 3.47x for TileSpGEMM, so the authors' figure is on the favourable end and spECK can be faster in other matrix sets. Single-GPU (V100, CUDA 11.2) results; host CPU not stated. The repo bundles nsparse and spECK copies for the comparison; the single MIT LICENSE lists their copyright holders (Tokyo Institute of Technology, Mathias Parger), and cuSPARSE is only called through its API. Last commit 2022.

CUDA GPU only; the repo bundles OpSparse together with copies of parts of cuSPARSE, nsparse and spECK code as comparison harnesses, so the MIT LICENSE may not cover every bundled file; execution instructions live in sub-directory readmes; matrix download script fetches webbase-1M.

## Maintenance

Abandoned since August 2022 (9 commits, no issues filed); MIT-licensed, including the bundled nsparse and spECK copies, and small enough to vendor, but last known to work only with CUDA 11.2 on V100.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now B.
- **Tier reason:** Upgraded from C: the work is peer reviewed (IEEE Access vol. 10, 2022, pp. 85960-85974, per the README bibtex) and a search result quoting its abstract gives up to 27.8x, 1.81x and 2.04x over cuSPARSE, nsparse and spECK on 26 matrices on a Tesla V100. B rests on venue plus abstract per earlier precedents; the paper (arxiv, ieeexplore, hkust pages) is blocked here. The repo has the harness (OpSparse/src/reg_opsparse.cu, reg_cusparse.cu; nvcc -O3 -arch=compute_70 -code=sm_70) but no host CPU model, so not A.
- **Verifier notes:** Usability corrected to copyable: the top-level MIT LICENSE covers OpSparse and the bundled nsparse/spECK sources, and the cuSPARSE harness only calls the library. Metadata: 16 stars, 4 forks, 9 commits, last commit 2022-08-23 (abandoned). benchmark_url set to the arXiv preprint of the IEEE Access paper (not opened; blocked).
- **Fields the verifier corrected:** `benchmark_url`, `compiler_and_flags`, `usability`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier; independent: Ocean (ICS 2026, arXiv 2604.19004, CornellHPC/Ocean-SpGEMM) on A100 over 337 matrices is 1.4x over spECK and 2.6x over OpSparse, so spECK is ahead of OpSparse there (snippet confirms averages 7.35x / 1.43x / 1.52x)
- **Pages the verifier opened:**
  - <https://github.com/lorentzbf/OpSparse>
  - <https://github.com/lorentzbf/OpSparse/commits>
  - <https://raw.githubusercontent.com/lorentzbf/OpSparse/HEAD/readme.md>
  - <https://raw.githubusercontent.com/lorentzbf/OpSparse/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/lorentzbf/OpSparse/HEAD/OpSparse/readme.md>
  - <https://raw.githubusercontent.com/lorentzbf/OpSparse/HEAD/OpSparse/Makefile>
  - <https://raw.githubusercontent.com/lorentzbf/OpSparse/HEAD/OpSparse/src/reg_cusparse.cu>
  - <https://raw.githubusercontent.com/lorentzbf/OpSparse/HEAD/nsparse/readme.md>
  - <https://raw.githubusercontent.com/lorentzbf/OpSparse/HEAD/spECK/readme.md>
  - <https://raw.githubusercontent.com/lorentzbf/OpSparse/HEAD/download_matrix.sh>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/lorentzbf/OpSparse/HEAD/readme.md>
  - <https://raw.githubusercontent.com/lorentzbf/OpSparse/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/lorentzbf/OpSparse/HEAD/OpSparse/readme.md>
  - <https://raw.githubusercontent.com/lorentzbf/OpSparse/HEAD/OpSparse/Makefile>
  - <https://raw.githubusercontent.com/lorentzbf/OpSparse/HEAD/download_matrix.sh>
  - <https://github.com/lorentzbf/OpSparse/tree/main/OpSparse>
  - <https://github.com/lorentzbf/OpSparse/tree/main/OpSparse/src>
  - <https://github.com/lorentzbf/OpSparse/tree/main/OpSparse/inc>
  - <https://raw.githubusercontent.com/lorentzbf/OpSparse/main/OpSparse/src/opsparse.cu>
  - <https://raw.githubusercontent.com/lorentzbf/OpSparse/main/OpSparse/src/reg_opsparse.cu>
  - <https://raw.githubusercontent.com/lorentzbf/OpSparse/main/OpSparse/src/reg_cusparse.cu>
  - <https://raw.githubusercontent.com/lorentzbf/OpSparse/main/OpSparse/src/Meta.cu>
  - <https://raw.githubusercontent.com/lorentzbf/OpSparse/main/OpSparse/src/Timings.cu>
  - <https://raw.githubusercontent.com/lorentzbf/OpSparse/main/OpSparse/src/CSR.cu>
  - <https://raw.githubusercontent.com/lorentzbf/OpSparse/main/OpSparse/inc/kernel_wrapper.cuh>
  - <https://raw.githubusercontent.com/lorentzbf/OpSparse/main/OpSparse/inc/symbolic.cuh>
  - <https://raw.githubusercontent.com/lorentzbf/OpSparse/main/OpSparse/inc/numeric.cuh>
  - <https://raw.githubusercontent.com/lorentzbf/OpSparse/main/OpSparse/inc/binning.cuh>
  - <https://raw.githubusercontent.com/lorentzbf/OpSparse/main/OpSparse/inc/define.h>
  - <https://raw.githubusercontent.com/lorentzbf/OpSparse/main/OpSparse/inc/cuda_common.h>
  - <https://raw.githubusercontent.com/lorentzbf/OpSparse/main/OpSparse/inc/cusparse_spgemm.h>
  - <https://raw.githubusercontent.com/lorentzbf/OpSparse/main/OpSparse/inc/Meta.h>
  - <https://raw.githubusercontent.com/lorentzbf/OpSparse/main/OpSparse/inc/CSR.h>
  - <https://raw.githubusercontent.com/lorentzbf/OpSparse/main/OpSparse/inc/setup.cuh>
  - <https://github.com/lorentzbf/OpSparse/issues?q=is%3Aissue>
  - https://deepai.org/publication/opsparse-a-highly-optimized-framework-for-sparse-general-matrix-multiplication-on-gpus (EGRESS_BLOCKED)
  - <https://github.com/CornellHPC/Ocean-SpGEMM>
  - WebSearch snippets: arXiv 2206.07244 abstract; Ocean ICS 2026 (arXiv 2604.19004) abstract
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/lorentzbf/opsparse`) · [data/wave8/enrich/raw/github_com_lorentzbf_opsparse.json](../../../data/wave8/enrich/raw/github_com_lorentzbf_opsparse.json) (enrichment confidence 0.6)

</details>
