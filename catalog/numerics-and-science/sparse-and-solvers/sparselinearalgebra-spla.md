# spla (generalized sparse linear algebra, vendor-agnostic GPU)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Sparse matrices and solvers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> OpenCL GraphBLAS-style sparse linear algebra for Intel, AMD and Nvidia GPUs; on a GTX 1070 it beats CPU LAGraph/SuiteSparse on PageRank and SSSP.

| | |
|---|---|
| **Beats** | SuiteSparse:GraphBLAS through LAGraph (CPU) |
| **Claimed result** | README log-scale chart (docs/stats/rq1_rel.png) of speedup over LAGraph (SuiteSparse) on a 4-core i7-6700, with spla on a GTX 1070. Values are read off the axis, so approximate. PageRank about 7.5x (coAuthorsCiteseer) to about 50x (coPapersDBLP, com-Orkut) on 12 graphs. SSSP about 1.4x (indochina-2004) to about 23x (road_central). Triangle counting about 4x to 12x. BFS about 0.7x to 3.7x, slower than LAGraph on coAuthorsCiteseer, belgium_osm, com-Orkut and indochina-2004. In PageRank spla beats Gunrock on every graph but trails GraphBLAST on several (e.g. belgium_osm, roadNet-CA, cit-Patents). The second chart (docs/stats/rq3_int.png) runs spla on the integrated GPU of the same machine as LAGraph. There spla is slower than LAGraph on every BFS run (about 0.1x to 0.8x), on most SSSP runs, and on every TC run on the AMD Ryzen 9 7900X/GFX1036 (about 0.1x to 0.3x). It is faster for PageRank (about 2.7x to 11.6x on the i7/HD 530, about 0.8x to 4x on the Ryzen). The README's 'much faster than scipy or networkx' has no numbers behind it. |
| **Workload** | GraphBLAS-style graph algorithms (BFS, SSSP, PageRank, triangle counting) on 13 SuiteSparse/SNAP/LAW graphs (coAuthorsCiteseer up to road_central, indochina-2004 with 302M edges), spla on a GTX 1070 GPU versus LAGraph on the CPU of the same machine; also integrated Intel and AMD GPUs. |
| **Metric** | latency |
| **Hardware** | Ubuntu 20.04, Intel Core i7-6700 3.40GHz (4 cores), 64 GB DDR4, NVIDIA GeForce GTX 1070 8 GB (also Intel HD Graphics 530, AMD GFX1036, Intel Arc A770, AMD Vega Frontier Edition) |
| **Adoption** | 35 stars |
| **Last commit** | 2025-11-17 |
| **Links** | [repository](https://github.com/SparseLinearAlgebra/spla) · [benchmark](https://github.com/SparseLinearAlgebra/spla) |

## Verdict

First-party README charts compare spla on an Nvidia GTX 1070 against LAGraph (SuiteSparse:GraphBLAS) on the same machine's 4-core i7-6700, over 13 SuiteSparse/SNAP/LAW graphs (Ubuntu 20.04). Read off the log axis: PageRank about 7.5-50x, SSSP about 1.4-23x, TC about 4-12x, BFS about 0.7-3.7x. On integrated GPUs (Intel HD 530, AMD GFX1036) spla wins only PageRank. Compiler, flags and baseline versions are not stated.

## Use it when

- PageRank-style iterative SpMV on a discrete GPU: the README chart shows about 7.5x to 50x over LAGraph on a 4-core i7-6700 on 12 graphs, and spla beats Gunrock on every one.
- SSSP on large high-diameter graphs (road networks), where the chart shows up to about 23x (road_central) on a GTX 1070.
- Code that must run on Intel, AMD and Nvidia GPUs, including integrated ones, from one OpenCL code base instead of CUDA-only GraphBLAST or cuBool.
- Prototyping GraphBLAS-style algorithms with custom semirings from Python or C++, where runtime-compiled user operators matter more than peak speed.

## Skip it when

- Production use: the README says 'project under heavy development! Not ready for usage.', the CHANGELOG has no release entries, and PyPI's only pyspla release is 0.0.5 from 2022-08-17.
- BFS: the chart shows about 0.7x to 3.7x, and spla is slower than LAGraph on coAuthorsCiteseer, belgium_osm, com-Orkut and indochina-2004.
- Integrated GPUs with the CPU baseline on the same chip: spla loses to LAGraph on every BFS run, on most SSSP runs, and on every triangle-counting run on the Ryzen 9 7900X/GFX1036, and wins only PageRank.
- Graphs larger than GPU memory: RAM-to-VRAM streaming is an open feature request (#211), so the matrix must fit on the device.
- Sparse linear solvers or numerical linear algebra (factorizations, Krylov methods): spla is graph-analytics oriented and has none.

## How it is fast

Graph algorithms are written as masked sparse matrix-vector products over semirings and run as OpenCL kernels. For a sparse frontier, vxm uses expand-sort-compress: it counts products per row, prefix-sums the offsets, collects products, then runs a GPU sort-by-key and reduce-by-key. Masked mxv has a scalar kernel with early exit, which pulls only until a hit. User operators are pasted into the OpenCL source as #defines and functions, compiled at runtime and cached by a key, so custom semirings get fused kernels. Most of the headline gain is GPU memory bandwidth and parallelism against a 4-core CPU baseline.

## Compared with alternatives

Pick spla over GraphBLAST or cuBool when you need non-Nvidia or integrated GPUs, or PageRank-heavy work. GraphBLAST is CUDA-only, and cuBool is CUDA-only and Boolean-only (cuBool comes from the same SparseLinearAlgebra organisation). GraphBLAST beats spla's PageRank on several graphs (belgium_osm, roadNet-CA, cit-Patents). For CPU-only or production GraphBLAS work, ALP/GraphBLAS or SuiteSparse:GraphBLAS are far more mature.

## Integration

| | |
|---|---|
| **Form** | shared lib (libspla_&lt;arch&gt; built with CMake; C and C++ headers; pyspla Python package) |
| **Dependencies** | OpenCL 1.2 runtime and drivers (Khronos headers and ICD loader vendored as submodules; Apple's OpenCL framework on macOS), robin_hood and svector (vendored, private); cxxopts and gtest only for examples and tests |
| **Minimum toolchain** | C++17; CMake 3.15+; Ninja and Python 3.7+ for build.py; MSVC is the only supported compiler on Windows |
| **Platforms** | Linux (x64, riscv), Windows x64, macOS x64 and arm64. GPU acceleration on Intel, AMD and Nvidia through OpenCL; a CPU-only mode is available via set_force_no_acceleration. |
| **Thread safety** | not documented (the library uses a global Library instance with a selected accelerator, platform, device and queue count) |
| **Drop-in for the baseline** | false — GraphBLAS-like semantics but a different C++/C/Python API from the GraphBLAS C API used by SuiteSparse and LAGraph |

## Gotchas

- The headline chart compares a GTX 1070 GPU with LAGraph on a 4-core CPU. Compiler flags, LAGraph and SuiteSparse versions and thread counts are not given, and the harness for LAGraph, GraphBLAST and Gunrock is not in the repo; only spla's examples/ (bfs, sssp, pr, tc) are.
- The README text claims '1 BILLION edges ... without memory issues' and 'much faster than scipy or networkx', but no published numbers back either. The largest benchmarked graph has 302M edges (indochina-2004).
- OpenCL programs are built at first use (with -cl-std=CL1.2), so the first call of each operation and type combination pays a compile cost before the cache helps; exclude warm-up from timing.
- Not the same project as eth-cscs/spla (distributed GEMM), which is also catalogued; check the repo owner.

## Known shortcomings

- PageRank top is about 50x, not 65x; the omitted chart rq3_int.png shows spla slower than LAGraph on most BFS/SSSP/TC runs on integrated GPUs; LAGraph/GraphBLAST/Gunrock harness not in the repo.
- README says 'not ready for usage'; only PyPI release is pyspla 0.0.5 (2022); graphs must fit in VRAM (#211 open); the '1 billion edges' and 'faster than scipy/networkx' claims have no numbers. Name clash with eth-cscs/spla (a different, already catalogued project).

## Caveats and trade-offs

Numbers exist only as chart images (docs/stats/rq1_rel.png, rq3_int.png); all values are read off log or linear axes. The headline comparison is a GTX 1070 GPU against LAGraph on a 4-core CPU, not like for like. In the integrated-GPU comparison, where both run on one device, spla loses to LAGraph on most BFS, SSSP and TC runs and wins only PageRank. The harness for the LAGraph, GraphBLAST and Gunrock runs is not in the repo (only examples/), and compiler, flags, LAGraph/SuiteSparse versions and thread counts are not stated. The README says the project is under heavy development and not ready for usage.

GPU-resident sparse linear algebra with C/C++ API and Python bindings (PyPI). Runs on Intel, Nvidia and AMD GPUs including integrated ones. Graph-analytics oriented (GraphBLAS semirings), not a solver library. Needs a GPU to see the gains.

## Maintenance

Some activity (last commit 2025-11-17, 35 stars, 10 open issues, mostly feature requests) but self-described as not ready for use, with no releases beyond a 2022 pyspla 0.0.5. MIT-licensed, so research code is free to borrow.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification C, tier now C.
- **Tier reason:** First-party README charts only (docs/stats/rq1_rel.png and rq3_int.png): speedup over LAGraph (SuiteSparse) with machine configurations but no compiler or flags, and the harness that ran LAGraph, GraphBLAST and Gunrock is not in the repo. No peer-reviewed spla paper was found, so C. The verdict is downgrade because the PageRank range was overstated and the integrated-GPU chart, where spla loses to LAGraph on most BFS, SSSP and TC runs, was left out.
- **Verifier notes:** The BFS, SSSP and TC ranges match the chart. The PageRank top end (65x) appears to have been read from the axis limit or GraphBLAST's cit-Patents bar; spla's highest PR bar is about 50x. Shortcoming worth recording: the integrated-GPU chart shows spla slower than LAGraph on most non-PageRank runs. License MIT, 35 stars, 18 forks, last commit 2025-11-17 (active) confirmed.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://github.com/SparseLinearAlgebra/spla>
  - <https://github.com/SparseLinearAlgebra/spla/commits>
  - <https://raw.githubusercontent.com/SparseLinearAlgebra/spla/HEAD/README.md>
  - <https://raw.githubusercontent.com/SparseLinearAlgebra/spla/HEAD/docs/stats/rq1_rel.png>
  - <https://raw.githubusercontent.com/SparseLinearAlgebra/spla/HEAD/docs/stats/rq3_int.png>
  - <https://raw.githubusercontent.com/SparseLinearAlgebra/spla/HEAD/LICENSE.md>
- **Sources the enricher read:**
  - <https://github.com/SparseLinearAlgebra/spla>
  - <https://github.com/SparseLinearAlgebra/spla/issues>
  - <https://github.com/SparseLinearAlgebra/spla/tree/main/src/opencl>
  - <https://raw.githubusercontent.com/SparseLinearAlgebra/spla/HEAD/README.md>
  - <https://raw.githubusercontent.com/SparseLinearAlgebra/spla/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/SparseLinearAlgebra/spla/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/SparseLinearAlgebra/spla/HEAD/build.py>
  - <https://raw.githubusercontent.com/SparseLinearAlgebra/spla/HEAD/include/spla.hpp>
  - <https://raw.githubusercontent.com/SparseLinearAlgebra/spla/HEAD/include/spla.h>
  - <https://raw.githubusercontent.com/SparseLinearAlgebra/spla/HEAD/include/spla/algorithm.hpp>
  - <https://raw.githubusercontent.com/SparseLinearAlgebra/spla/HEAD/include/spla/library.hpp>
  - <https://raw.githubusercontent.com/SparseLinearAlgebra/spla/HEAD/include/spla/exec.hpp>
  - <https://raw.githubusercontent.com/SparseLinearAlgebra/spla/HEAD/src/opencl/cl_vxm.hpp>
  - <https://raw.githubusercontent.com/SparseLinearAlgebra/spla/HEAD/src/opencl/cl_mxv.hpp>
  - <https://raw.githubusercontent.com/SparseLinearAlgebra/spla/HEAD/src/opencl/cl_program_builder.cpp>
  - <https://pypi.org/pypi/pyspla/json>
  - <https://test.pypi.org/pypi/pyspla/json>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/sparselinearalgebra/spla`) · [data/wave8/enrich/raw/github_com_sparselinearalgebra_spla.json](../../../data/wave8/enrich/raw/github_com_sparselinearalgebra_spla.json) (enrichment confidence 0.75)

</details>
