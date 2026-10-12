# ISpMV

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Sparse matrices and solvers](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `MIT (interfaces, examples, benchmarks) plus proprietary ISpMV Binary License for compiled core` · 🟢 active

> Closed-binary GPU SpMV SDK with per-matrix plans; 1.3-2.2x faster than cuSPARSE SpMV on H100 (fp64).

| | |
|---|---|
| **Beats** | cuSPARSE SpMV (CUDA 13 / cuSPARSE 12.8.6.72) |
| **Claimed result** | Geometric-mean execution-time speedup over cuSPARSE ALG2 (cusparseSpMV), preprocessing excluded, fp64, H100 PCIe: SpMV(1,0) 2.17x Mittelmann (20.25 vs 43.85 us), 1.64x MIPLIB nnz&gt;10M (141.54 vs 232.66 us), 1.31x SuiteSparse nnz&gt;10M (211.03 vs 275.97 us); SpMV(alpha,beta) 2.22x / 1.60x / 1.30x. Over cuSPARSE SpMVOp ALG1/ALG2: 1.38-1.69x. |
| **Workload** | GPU SpMV (fp64, alpha/beta variants, A and A^T) over 49 Mittelmann, 18 MIPLIB and 33 SuiteSparse large matrices on H100 PCIe. |
| **Metric** | throughput |
| **Hardware** | NVIDIA H100 PCIe 80GB, CUDA 13.4.2 |
| **Adoption** | 1 star |
| **Last commit** | 2026-09-30 |
| **Links** | [repository](https://github.com/PolyU-IOR/ISpMV) · [benchmark](https://github.com/PolyU-IOR/ISpMV/blob/main/benchmarks/README.md) |

## Verdict

First-party benchmark on one H100 PCIe (CUDA 13.4.2, cuSPARSE 12.8.6.72), fp64, 100 matrices x 2 orientations x 2 scalar modes, preprocessing excluded. Geometric-mean steady-state time vs cusparseSpMV ALG2 is 2.17x lower on Mittelmann, 1.64x on large MIPLIB and 1.31x on large SuiteSparse; vs cusparseSpMVOp ALG1/ALG2 it is 1.38-1.69x lower. Host compiler, flags and CPU are not stated.

## Use it when

- Iterative fp64 solvers (PDLP-style LP/QP, Krylov methods) on an NVIDIA GPU that apply the same sparsity pattern thousands of times
- LP/MIP constraint matrices like those in Mittelmann and MIPLIB, where the published gain over cuSPARSE ALG2 is largest (1.6-2.2x)
- Non-commercial research or internal evaluation: that is all the binary license allows without written permission
- A100, H100/H200, B200, RTX 4090 or RTX 5090 (sm_80-sm_120) on Linux x86-64 with CUDA 13

## Skip it when

- Commercial or production use without a separate agreement: the ISpMV Binary License limits the core to internal evaluation and non-commercial research, and you may not redistribute the .so
- One-off or few SpMVs per matrix: 37-110 ms of preprocessing (geometric mean) wipes out a gain of tens to hundreds of microseconds per call
- FP32, complex, 64-bit indices, device-pointer scalars or CPU execution: all unsupported
- Anything that needs auditable or patchable source: the core is closed, and runtime validation covers only H100 PCIe
- Risk-averse deployments: v0.1.0 is a single-commit repo from late September 2026 with one star

## How it is fast

Not documented in technical terms: the core source is private. The docs say plan preparation analyses the matrix on the GPU and picks a representation and kernel from the matrix structure and the device's reported resources (SM count, cache, launch limits). The work is classic inspector-executor: you pay 37-110 ms of matrix-specific preprocessing up front so each later SpMV runs faster.

## Compared with alternatives

Pick it over merge-spmv or CSR5 when you are on a current NVIDIA GPU, reuse one matrix many times, and can accept a closed non-commercial binary. merge-spmv and CSR5 are open, copyable source but target 2015-16 hardware. Ginkgo or AMGCL fit better when you need a full open solver stack rather than a faster SpMV kernel.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | CUDA 13 runtime, cuBLAS 13; CMake &gt;= 3.24 for find_package(ISpMV ... COMPONENTS runtime) |
| **Minimum toolchain** | C++17 compiler, CUDA 13; no CUDA compiler needed to link |
| **Platforms** | Linux x86-64 only; NVIDIA sm_80/86/89/90/100/120, no PTX fallback (other GPUs return UNSUPPORTED) |
| **Thread safety** | Submit a plan from one host thread at a time; a Device handle may be shared by concurrent plan preparations on the same GPU |
| **Drop-in for the baseline** | partial: same operation as cusparseSpMV on CSR, but a different API (Plan object, separate A/A^T plans, host scalars only) |

## Gotchas

- With copy_device_matrix=0 the plan borrows your CSR arrays, so they must stay immutable and allocated until the plan is released. Plan destruction does not synchronize.
- Changing sparsity, dimensions or device requires a new plan. Changing only values per call is possible via apply_with_values, which bypasses value-dependent representations.
- deterministic=1 (the default) gives bitwise-reproducible results only for the same plan, GPU and build. In the published benchmark, 24 of 400 cases (six SuiteSparse matrices) failed the forward-error criterion; all four methods failed those same cases.
- Plan preparation cannot be captured in a CUDA graph, and graph-captured pointers and scalars are fixed. ispmv_version() returns the ABI major, not the SDK version.

## Known shortcomings

- Core is a closed binary; speedups exclude 37-110 ms preprocessing per direction; 1 star, one commit; no host compiler, flags or CPU.
- LICENSE-BINARY.txt limits the core to internal evaluation and non-commercial research, no redistribution of the .so; validated only on H100 PCIe; fp64 with 32-bit indices only; 24 of 400 cases failed forward-error check (all methods).

## Caveats and trade-offs

Core is a closed binary under the ISpMV Binary License (source private); only interfaces, examples and the benchmark client are MIT. Speedups exclude ISpMV preprocessing, which costs 37-110 ms per direction (geometric mean), so it pays off only for repeated SpMV with a fixed matrix. Host compiler, flags and CPU not stated. Results include directions that failed the numerical criterion (README says the same failures occur for the baselines). Brand-new repo (single commit, v0.1.0 on 2026-09-30). Baseline cuSPARSE is not on the list.

Needs a one-time GPU preprocessing plan per matrix (37-110 ms geometric mean per direction); NVIDIA GPU only; core is a closed binary SDK.

## Maintenance

Actively released (v0.1.0, single public commit) but reference-only: the core is a proprietary binary licensed for evaluation and non-commercial research, and only the interfaces, examples and benchmark client are MIT.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party benchmarks/README.md table compares against cuSPARSE ALG2 and cuSPARSE SpMVOp ALG1/ALG2 on H100 PCIe with CUDA/cuSPARSE versions and protocol; the benchmark client is public but the core is a closed binary and no host compiler, flags or CPU are stated, so C.
- **Verifier notes:** Re-opened the benchmark page and checked the speedups row by row: the search agent's 2.17x / 1.64x / 1.31x figures match the cuSPARSE ALG2 column for SpMV(1,0). usability 'reference' kept (the core is not copyable). The search agent's note that the numbers were unverified can now be dropped.
- **Fields the verifier corrected:** `claimed_speedup`, `last_commit`, `maintenance_status`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/PolyU-IOR/ISpMV/blob/main/benchmarks/README.md>
  - <https://raw.githubusercontent.com/PolyU-IOR/ISpMV/HEAD/benchmarks/README.md>
  - <https://raw.githubusercontent.com/PolyU-IOR/ISpMV/HEAD/README.md>
  - <https://raw.githubusercontent.com/PolyU-IOR/ISpMV/HEAD/LICENSE>
  - <https://github.com/PolyU-IOR/ISpMV>
  - <https://github.com/PolyU-IOR/ISpMV/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/PolyU-IOR/ISpMV/HEAD/README.md>
  - <https://raw.githubusercontent.com/PolyU-IOR/ISpMV/HEAD/benchmarks/README.md>
  - <https://raw.githubusercontent.com/PolyU-IOR/ISpMV/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/PolyU-IOR/ISpMV/HEAD/LICENSE-BINARY.txt>
  - <https://raw.githubusercontent.com/PolyU-IOR/ISpMV/HEAD/docs/API.md>
  - <https://raw.githubusercontent.com/PolyU-IOR/ISpMV/HEAD/docs/HARDWARE.md>
  - <https://raw.githubusercontent.com/PolyU-IOR/ISpMV/HEAD/docs/LIMITATIONS.md>
  - <https://raw.githubusercontent.com/PolyU-IOR/ISpMV/HEAD/docs/VALIDATION.md>
  - <https://github.com/PolyU-IOR/ISpMV>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/polyu-ior/ispmv`) · [data/wave8/enrich/raw/github_com_polyu_ior_ispmv.json](../../../data/wave8/enrich/raw/github_com_polyu_ior_ispmv.json) (enrichment confidence 0.7)

</details>
