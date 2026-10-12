# TBLIS (Tensor-Based Library Instantiation Software)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [BLAS and LAPACK](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> Native tensor-contraction library on BLIS kernels; beats transpose-plus-GEMM (NumPy/MKL einsum) on strided and permuted contractions.

| | |
|---|---|
| **Beats** | BLAS-based tensor contraction (TTGT: transpose plus GEMM). In the independent tblis-rs benchmark this is NumPy einsum backed by Intel MKL, alongside PyTorch (CPU). |
| **Claimed result** | Independent tblis-rs README (AMD Ryzen 7945HX, 16 cores, FP64 tensors of shape 96^4), TBLIS vs NumPy (MKL) vs PyTorch CPU. Contiguous: abxy,xycd-&gt;abcd 1.90 s vs 2.13 s vs 1.98 s; axyz,ybzx-&gt;ab 120.7 vs 207.7 vs 211.1 ms; axby,yacx-&gt;abc 124.1 ms vs 29.7 s vs 179.2 ms. TBLIS loses on axyz,xyzb-&gt;ab (132.3 vs 63.1 vs 63.4 ms) and on SYRK-shaped axyz,bxyz-&gt;ab (96.9 vs 293.2 vs 37.4 ms). Strided (stride 128): abxy,xycd-&gt;abcd 2.02 s vs 7.30 s vs 2.10 s; axyz,xyzb-&gt;ab 133.1 vs 776.8 vs 204.4 ms. That is about 1.1x (contiguous GEMM-shaped) to 5.8x (strided) over NumPy/MKL and 1.0-1.8x over PyTorch where TBLIS wins (derived from page data). The TBLIS wiki itself claims only 'essentially zero overhead compared to matrix multiplication'. |
| **Workload** | Tensor contraction (a multi-dimensional generalisation of GEMM) done natively with BLIS-style micro-kernels, without the explicit tensor transpositions that a GEMM-based approach needs. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 7945HX, 16 cores (independent tblis-rs benchmark) |
| **Adoption** | 145 stars, 39 forks; wrapped by tblis-rs (Rust) and pytblis (Python) |
| **Last commit** | 2025-11-21 |
| **Links** | [repository](https://github.com/MatthewsResearchGroup/tblis) · [benchmark](https://github.com/restgroup/tblis-rs) |

## Verdict

In the independent tblis-rs README (AMD Ryzen 7945HX, 16 cores, FP64 tensors of shape 96^4, compiler and threads unstated), TBLIS beat NumPy einsum on MKL by about 1.1x on contiguous GEMM-shaped contractions and up to 5.8x on strided ones, and beat PyTorch CPU by 1.0-1.8x where it won; it lost 2x to MKL/PyTorch on plain contiguous GEMM shapes and 2.6x to PyTorch on a SYRK shape.

## Use it when

- Contractions whose index order would force large transposes before a GEMM, such as axyz,ybzx-&gt;ab or batched axby,yacx-&gt;abc (about 1.7x and 1.4x faster than PyTorch CPU in the tblis-rs table).
- Tensors that live in strided, non-contiguous memory (sub-blocks of larger arrays): 2.0 s vs 7.3 s for NumPy/MKL on a strided 96^4 GEMM-shaped contraction.
- Quantum chemistry and tensor-network codes (coupled cluster and similar) that need many differently-permuted contractions without extra workspace for transposed copies.
- Projects that want a C ABI usable from C++, Python (pytblis) or Rust (tblis-rs).

## Skip it when

- Contractions that already map to a contiguous GEMM: in tblis-rs, axyz,xyzb-&gt;ab took 132 ms vs 63 ms for MKL and PyTorch, and the SYRK-shaped axyz,bxyz-&gt;ab took 97 ms vs 37 ms for PyTorch.
- Apple Silicon/ARM with the 2.0 code line: issue #76 reports a 4x slowdown on an M3 Pro (0.73 s to 2.93 s) and 1.3x on an i7-4770K between an April 2023 commit and the August 2025 one.
- Applications that already run their own thread pool or a second OpenMP runtime: issue #80 reports 2.0 beta's performance collapsing under oversubscription (time spent in a BLIS barrier), and issue #47 covers multiple OpenMP runtimes in one process.
- Code relying on conjugated operands in tblis_tensor_add or on tblis_scalar abs/conj/sqrt: open issues #86, #87 and #88 (2026) report wrong results.
- Windows (not supported per the wiki; Cygwin only 'probably') or GPUs (CPU only).

## How it is fast

It applies the BLIS GEMM structure (cache-blocked loops, packing into contiguous panels, register-blocked micro-kernels) directly to tensors: the packing step gathers tensor elements through their native strides, so no transposed copy of the whole operand is formed as in transpose-transpose-GEMM-transpose (TTGT). This is the algorithm of Matthews, 'High-Performance Tensor Contraction without Transposition' (SIAM J. Sci. Comput. 40(1) C1-C24, 2018); GETT/TCCG from Springer and Bientinesi is the concurrent related approach. Version 2.0 is rebuilt as a BLIS 2.0 plugin, so it uses BLIS's micro-kernels and architecture configurations, with its own TCI threading layer.

## Compared with alternatives

Pick TBLIS over Eigen's Tensor module or a hand-written reshape plus BLAS/MKL GEMM when contractions are permuted or strided, since it skips the transposed copies. tblis-strassen is a research code built on TBLIS that adds Strassen (up to 1.3x per its README); TBLIS is the maintained base library.

## Integration

| | |
|---|---|
| **Form** | static lib \| shared lib |
| **Dependencies** | BLIS 2.0 (found via find_package/pkg-config or fetched at a pinned commit), bundled git submodules TCI, MArray and stl_ext; optional hwloc and memkind |
| **Minimum toolchain** | C++20 compiler and CMake 3.23 for the 2.0 code on master (the wiki's GCC 4.8+/autotools notes describe 1.x); GCC 15/16 builds need a newer BLIS (issue #90) |
| **Platforms** | Linux and macOS; x86-64 and other architectures BLIS supports (BLIS_CONFIG_FAMILY auto); no Windows |
| **Thread safety** | not documented; threading via TCI (OpenMP or pthreads) with tblis_set_num_threads and a tblis_comm argument on every call; see issues #47 and #80 |
| **Drop-in for the baseline** | no |

## Gotchas

- The 2.0 line on master (BLIS plugin) and the wiki's build instructions (1.x autotools, --enable-config=haswell etc.) disagree; clone with git submodule update --init --recursive and build with -DCMAKE_BUILD_TYPE=Release (tblis-rs warns about this).
- Issue #85: BLIS headers cannot be included alongside TBLIS headers, which bites projects that also call BLIS directly.
- Mixed-sign strides can abort tblis_tensor_mult with an are_compatible assertion (issue #81); a std::bad_array_new_length crash is also open (#82).
- The project publishes no benchmark numbers of its own; the only table found is a third-party wrapper's laptop run with no compiler or thread settings, using a 2.0-era commit (9b95712).

## Known shortcomings

- Independent tblis-rs numbers (Ryzen 7945HX) show wins only on strided/transpose-heavy contractions (1.1-5.8x vs MKL, derived); loses \~2x on plain GEMM-shaped contiguous cases and 2.6x vs PyTorch on SYRK; tensor contraction, an edge case for blas-lapack.
- Open 2026 wrong-result issues #86/#87/#88 (conjugated tensor_add, tblis_scalar abs/conj/sqrt); #76: 2.0 code is 4x slower on M3 Pro and 1.3x on i7-4770K vs a 2023 commit (tblis-rs benchmarked a 2.0-era commit); #80 oversubscription collapse; crashes #81 (mixed-sign strides abort), #82; stale 1.x build docs.

## Caveats and trade-offs

The project's own pages (README, wiki home and Research pages) give no benchmark numbers. The numbers come from an independent wrapper author's laptop run (tblis-rs README) that states no compiler, flags or thread settings. There, TBLIS is about 2x slower than MKL/PyTorch on plain GEMM-shaped contiguous contractions and 2.6x slower than PyTorch on a SYRK-shaped one. The wrapper author says TBLIS 'may probably not the best choice' for contractions that map to GEMM. The 200-1000x gaps on batched and trace contractions come from NumPy einsum falling back to a non-BLAS path, so they are not a fair TTGT comparison. The SISC 2018 paper (arXiv 1607.00291) could not be opened (arxiv.org and epubs.siam.org are egress-blocked), so its TTGT comparison numbers, CPU and compiler are unverified.

C and C++ interfaces (tblis.h header in the repo); builds on BLIS-style kernels and its own threading; the wiki lists build/usage pages. Tensor operations only, not a drop-in BLAS replacement.

## Maintenance

Active but slow to respond (last commit 2025-11-21; 2.0 is still a beta pre-release next to stable v1.3.0, with 18 open issues including several 2026 wrong-result reports); BSD-3-Clause and a C library, so straightforward to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** The recorded wiki page has no numbers, but the independent tblis-rs README (a Rust wrapper by a different group) tables TBLIS against NumPy einsum backed by MKL and against PyTorch CPU on an AMD Ryzen 7945HX. TBLIS wins most strided and transposition-heavy contractions there. The same page cites the method paper as peer-reviewed (SIAM J. Sci. Comput. 40(1) C1-C24, 2018, DOI 10.1137/16M108968X). No compiler, flags or harness path is given, so not A.
- **Verifier notes:** Kept at B on the strength of an independent measurement plus the peer-reviewed SISC 2018 publication (venue confirmed only through the citation on the tblis-rs README). benchmark_url was moved to the tblis-rs README, the only opened page with numbers. Metadata was checked on github.com: BSD-3-Clause, 145 stars, 39 forks, not a fork, last master commit 2025-11-21 (active). A retier check could fill the paper's numbers, CPU and compiler if arxiv.org/abs/1607.00291 becomes reachable.
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `claimed_speedup`, `hardware`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/MatthewsResearchGroup/tblis>
  - <https://github.com/MatthewsResearchGroup/tblis/commits>
  - <https://github.com/MatthewsResearchGroup/tblis/wiki>
  - <https://github.com/MatthewsResearchGroup/tblis/wiki/Research>
  - <https://github.com/MatthewsResearchGroup/tblis/wiki/Implementation>
  - <https://raw.githubusercontent.com/MatthewsResearchGroup/tblis/HEAD/README.md>
  - <https://raw.githubusercontent.com/MatthewsResearchGroup/tblis/HEAD/LICENSE>
  - <https://github.com/restgroup/tblis-rs>
  - <https://raw.githubusercontent.com/restgroup/tblis-rs/HEAD/readme.md>
- **Sources the enricher read:**
  - <https://github.com/MatthewsResearchGroup/tblis>
  - <https://github.com/MatthewsResearchGroup/tblis/issues>
  - <https://github.com/MatthewsResearchGroup/tblis/issues/76>
  - <https://github.com/MatthewsResearchGroup/tblis/issues/80>
  - <https://github.com/MatthewsResearchGroup/tblis/issues/81>
  - <https://github.com/MatthewsResearchGroup/tblis/issues/87>
  - <https://github.com/MatthewsResearchGroup/tblis/releases>
  - <https://raw.githubusercontent.com/MatthewsResearchGroup/tblis/HEAD/README.md>
  - <https://raw.githubusercontent.com/MatthewsResearchGroup/tblis/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/MatthewsResearchGroup/tblis/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/MatthewsResearchGroup/tblis/HEAD/configure.ac>
  - <https://raw.githubusercontent.com/MatthewsResearchGroup/tblis/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/MatthewsResearchGroup/tblis/HEAD/tblis-version>
  - <https://raw.githubusercontent.com/MatthewsResearchGroup/tblis/HEAD/blis-git-tag>
  - <https://raw.githubusercontent.com/MatthewsResearchGroup/tblis/HEAD/tblis.h>
  - <https://raw.githubusercontent.com/MatthewsResearchGroup/tblis/HEAD/tblis/tblis.h>
  - <https://raw.githubusercontent.com/MatthewsResearchGroup/tblis/HEAD/tblis/frame/base/thread.h>
  - <https://raw.githubusercontent.com/wiki/MatthewsResearchGroup/tblis/Home.md>
  - <https://raw.githubusercontent.com/wiki/MatthewsResearchGroup/tblis/Building.md>
  - <https://raw.githubusercontent.com/wiki/MatthewsResearchGroup/tblis/C-Interface.md>
  - <https://raw.githubusercontent.com/wiki/MatthewsResearchGroup/tblis/CXX-Interface.md>
  - <https://raw.githubusercontent.com/wiki/MatthewsResearchGroup/tblis/Tensor-Operations.md>
  - <https://raw.githubusercontent.com/wiki/MatthewsResearchGroup/tblis/Implementation.md>
  - <https://raw.githubusercontent.com/wiki/MatthewsResearchGroup/tblis/Threading.md>
  - <https://raw.githubusercontent.com/wiki/MatthewsResearchGroup/tblis/Research.md>
  - <https://raw.githubusercontent.com/restgroup/tblis-rs/HEAD/readme.md>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/matthewsresearchgroup/tblis`) · [data/wave8/enrich/raw/github_com_matthewsresearchgroup_tblis.json](../../../data/wave8/enrich/raw/github_com_matthewsresearchgroup_tblis.json) (enrichment confidence 0.75)

</details>
