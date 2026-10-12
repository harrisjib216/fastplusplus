# cuBool (sparse Boolean linear algebra on CUDA)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Sparse matrices and solvers](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++ (CUDA)` · `MIT` · 🟢 active

> CUDA library of sparse Boolean-semiring matrix and vector operations; Boolean SpGEMM runs 1.3-16x faster than CPU SuiteSparse:GraphBLAS.

| | |
|---|---|
| **Beats** | SuiteSparse on CPU (README does not say which package; GraphBLAS likely) |
| **Claimed result** | SpBench README table, time in ms, cuBool vs SuiteSparse for M\*M: 23.2 vs 257.6 on amazon0312 (about 11x, derived from page data), 33.3 vs 369.5 on amazon-2008 (11x), 41.8 vs 673.3 on web-Google (16x), 18.1 vs 66.6 on roadNet-PA (3.7x), 1.9 vs 7.9 on wing (4.2x), 35.3 vs 90.9 on netherlands_osm (2.6x), 2.4 vs 3.1 on luxembourg_osm (1.3x); element-wise addition 11.4 vs 37.2 on amazon0312 (3.3x) and 24.8 vs 77.5 on web-Google (3.1x). |
| **Workload** | Boolean sparse matrix-matrix multiplication M\*M and element-wise addition M+M^2 on 10 SuiteSparse graphs (62K to 2.2M rows), SpBench harness, operation time only with data already resident. |
| **Metric** | latency |
| **Hardware** | Intel Core i7-6700 3.40 GHz, 64 GB DDR4, NVIDIA GeForce GTX 1070 8 GB, Ubuntu 20.04 |
| **Compiler and flags** | GCC (version not stated), CUDA toolkit (version not stated), CMake Release build per the SpBench README; SpBench benchmark code is public |
| **Adoption** | 27 stars |
| **Last commit** | 2025-11-17 |
| **Links** | [repository](https://github.com/SparseLinearAlgebra/cuBool) · [benchmark](https://github.com/EgorOrachyov/SpBench) |

## Verdict

The authors' SpBench harness, also used for their IPDPS Workshops 2021 (GrAPL) paper, times only the operation, with data already resident and an average of 10 runs. It compares cuBool on a GTX 1070 with SuiteSparse:GraphBLAS on the host's 4-core i7-6700 (SuiteSparse version and thread count not stated; GCC and CUDA versions not stated). Boolean M\*M was 11x faster on amazon0312, 16x on web-Google, 3.7x on roadNet-PA and 1.3x on luxembourg_osm, and M+M^2 addition about 3x faster on web graphs (ratios derived from page data).

## Use it when

- Graph reachability, transitive closure, RPQ/CFPQ or parsing algorithms that reduce to repeated Boolean SpGEMM on an NVIDIA GPU
- Web and co-purchase graphs of about 0.4-0.9M rows with 5-8 non-zeros per row (amazon0312, amazon-2008, web-Google), where M\*M produces 14-30M non-zeros; there cuBool's mxm beat SuiteSparse by 11-16x and also beat cuSPARSE and CUSP
- Memory-tight GPU work: without stored values cuBool used 165-241 MB on the large mxm cases, against 897-1717 MB for CUSP
- Prototyping in Python (pycubool) on a laptop with the CPU fallback, then running the same code on a CUDA server

## Skip it when

- Anything beyond the Boolean semiring (numeric SpGEMM, min-plus, masks, user-defined monoids); use full GraphBLAS (SuiteSparse:GraphBLAS, GraphBLAST, or the authors' successor spla)
- Road-network or very sparse, low-degree matrices: there clBool's mxm was faster, and for element-wise add CUSP and cuSPARSE beat cuBool on every road matrix (roadNet-PA 16.9 ms vs CUSP 11.2 ms)
- Small matrices: on luxembourg_osm (115K rows) mxm was 2.4 ms vs 3.1 ms for SuiteSparse and 1.7 ms for cuSPARSE, and GPU memory never went below about 91 MB while SuiteSparse used 22 MB on wing
- Non-NVIDIA or non-Linux platforms: only Ubuntu 20.04 is tested, and Windows and macOS are still listed as 'coming soon'
- Linear-system solving: despite its category, it has no factorization or iterative solver

## How it is fast

Matrices are stored as value-less CSR (row offsets plus uint32 column indices only), so a matrix takes (m + nnz) x 4 bytes of GPU memory. Multiplication uses nsparse, a Boolean adaptation of the Nagasaka, Nukada and Matsuoka (ICPP 2017) hash-table SpGEMM, which bins rows by work and keeps memory use low. Element-wise addition uses GPU Merge Path (Green, McColl, Bader) with dynamic load balancing and a two-pass size-then-fill scheme. The baseline is a 4-core CPU, so most of the gap is GPU versus CPU; the paper shows a smaller gain over generic GPU libraries that treat floats as truth values.

## Compared with alternatives

Pick cuBool over GraphBLAST or ALP/GraphBLAS when the whole algorithm is Boolean and runs on one NVIDIA GPU, so value-less CSR and a Boolean-specialised SpGEMM pay off. For other semirings or for AMD and Intel GPUs, prefer the same group's spla (OpenCL) or GraphBLAST.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | CUDA toolkit with Thrust/CUB and the vendored nsparse-um SpGEMM (header-only, under deps/); googletest only for tests; Python 3 for pycubool |
| **Minimum toolchain** | C++17 host code, CUDA standard 14, CMake 3.15+, GCC; the README's tested path is CUDA 10.1 with GCC 8 (newer combinations not documented) |
| **Platforms** | Linux x86-64 with an NVIDIA GPU (tested Ubuntu 20.04, GTX 1070); CPU sequential fallback anywhere it builds |
| **Thread safety** | not documented; the library keeps one process-global backend (a static shared_ptr set in cuBool_Initialize, with no visible locking), so assume one thread drives it |
| **Drop-in for the baseline** | partial — the GraphBLAS-style C API covers Boolean MxM, MxV, VxM and EWiseAdd/Mult, but the function names and types differ from the GraphBLAS C API, so code written for SuiteSparse:GraphBLAS must be ported |

## Gotchas

- Indices are uint32 (cuBool_Index), so dimensions and nnz must stay below 2^32
- The pycubool PyPI wheel (1.2.0, last upload 2021-06-11) ships a prebuilt .so; open issue #13 (2022, labelled bug) reports that this .so lacks cuBool_Matrix_EWiseMult and that source builds fail with 'limits and CUB' errors on newer toolchains; open issue #14 says pycubool tries to load its own log file as the shared library
- The README advises replacing the system gcc/g++ symlinks with GCC 8 to match CUDA 10; on a modern system, set CC, CXX and CUDAHOSTCXX instead
- cuBool_Finalize fails if objects are still alive unless you initialised with CUBOOL_HINT_RELAXED_FINALIZE (the Python wrapper relies on that hint)

## Known shortcomings

- The peer-reviewed IPDPSW 2021 (GrAPL) paper calls its own comparison 'not entirely fair': GTX 1070 GPU vs SuiteSparse:GraphBLAS on a 4-core CPU, thread count not stated; on road matrices CUSP and cuSPARSE beat cuBool for element-wise add; GCC and CUDA versions not stated.
- Commits since 2021 are CI/docs/format only; pycubool last released 1.2.0 (2021-06-11). Open #13: prebuilt .so lacks cuBool_Matrix_EWiseMult and source build fails with CUB/limits errors. Open #14: pycubool loads its own log as a library. Global backend with no lock. Boolean SpGEMM only, no solver.

## Caveats and trade-offs

Shootout (SpBench) written by cuBool's own author in 2021 (last SpBench commit 2021-09-04); the same tables are in the authors' peer-reviewed IPDPSW 2021 paper (https://github.com/YaccConstructor/articles/blob/master/2021/GRAPL/Sparse_Boolean_Algebra_on_GPGPU/Sparse_Boolean_Algebra_on_GPGPU.pdf), which reports each result as an average of 10 runs and says 'the comparison is not entirely fair'. It compares a GTX 1070 GPU against SuiteSparse:GraphBLAS on a 4-core i7-6700; SuiteSparse version and thread count are not stated. On road networks cuBool's mxm is slower than clBool and on luxembourg_osm also slower than cuSPARSE (2.4 vs 1.7 ms); its margin over SuiteSparse there is only 1.3-3.7x. For element-wise add, CUSP and cuSPARSE beat cuBool on every road matrix (roadNet-PA 16.9 ms vs CUSP 11.2 ms), as the paper itself notes. SuiteSparse here is the GraphBLAS component, not CHOLMOD or UMFPACK, so this is not a solver comparison. Minor table drift: web-Google SuiteSparse add is 77.2 ms in the paper vs 77.5 ms in the SpBench README.

Boolean semiring only; needs an NVIDIA GPU (OpenCL sibling clBool/SPbLA exists); Python bindings (pycubool); GPU memory 91 to 241 MB in the table, while SuiteSparse used 22 MB on the smallest matrix.

## Maintenance

MIT-licensed and listed as active (last commit 2025-11-17), but every commit since mid-2021 touches CI, docs or formatting, and the last PyPI release is 1.2.0 from June 2021, so treat it as a finished research library that you may need to patch for current CUDA.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Upgraded from C: the same mxm and add tables appear in the peer-reviewed paper 'SPbLA: The Library of GPGPU-Powered Sparse Boolean Linear Algebra Operations' (IEEE IPDPS Workshops 2021, GrAPL), linked from the cuBool README. Benchmark code (EgorOrachyov/SpBench) and CPU model are public, but GCC and CUDA versions are unstated, so not A.
- **Verifier notes:** All claimed numbers match SpBench README rows 1, 2, 3, 4, 8 (mxm) and 2, 4 (add); 16x and 11x ratios are correctly marked derived. Upgraded to B on the IPDPSW 2021 paper (venue confirmed via WebSearch result for IEEE Xplore document 9460674; the PDF itself carries no venue line). MIT license, 27 stars, last commit 2025-11-17 confirmed.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/EgorOrachyov/SpBench/HEAD/README.md>
  - <https://raw.githubusercontent.com/SparseLinearAlgebra/cuBool/HEAD/README.md>
  - <https://raw.githubusercontent.com/YaccConstructor/articles/master/2021/GRAPL/Sparse_Boolean_Algebra_on_GPGPU/Sparse_Boolean_Algebra_on_GPGPU.pdf>
  - <https://github.com/SparseLinearAlgebra/cuBool>
  - <https://github.com/SparseLinearAlgebra/cuBool/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/SparseLinearAlgebra/cuBool/HEAD/README.md>
  - <https://raw.githubusercontent.com/SparseLinearAlgebra/cuBool/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/SparseLinearAlgebra/cuBool/HEAD/cubool/CMakeLists.txt>
  - <https://raw.githubusercontent.com/SparseLinearAlgebra/cuBool/HEAD/cubool/include/cubool/cubool.h>
  - <https://raw.githubusercontent.com/SparseLinearAlgebra/cuBool/HEAD/cubool/sources/cuda/cuda_matrix_multiply.cu>
  - <https://raw.githubusercontent.com/SparseLinearAlgebra/cuBool/HEAD/cubool/sources/core/library.cpp>
  - <https://raw.githubusercontent.com/SparseLinearAlgebra/cuBool/HEAD/deps/nsparse-um/CMakeLists.txt>
  - <https://raw.githubusercontent.com/SparseLinearAlgebra/cuBool/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/EgorOrachyov/SpBench/HEAD/README.md>
  - <https://raw.githubusercontent.com/YaccConstructor/articles/master/2021/GRAPL/Sparse_Boolean_Algebra_on_GPGPU/Sparse_Boolean_Algebra_on_GPGPU.pdf>
  - <https://github.com/SparseLinearAlgebra/cuBool>
  - <https://github.com/SparseLinearAlgebra/cuBool/issues?q=is%3Aissue>
  - <https://github.com/SparseLinearAlgebra/cuBool/issues/13>
  - <https://github.com/SparseLinearAlgebra/cuBool/commits/master>
  - <https://pypi.org/pypi/pycubool/json>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/sparselinearalgebra/cubool`) · [data/wave8/enrich/raw/github_com_sparselinearalgebra_cubool.json](../../../data/wave8/enrich/raw/github_com_sparselinearalgebra_cubool.json) (enrichment confidence 0.8)

</details>
