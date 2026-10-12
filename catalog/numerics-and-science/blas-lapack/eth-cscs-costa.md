# COSTA (communication-optimal distributed matrix redistribution and transpose; ScaLAPACK pxgemr2d/pxtran replacement)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [BLAS and LAPACK](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> MPI library for redistributing and transposing distributed matrices; link-time replacement for ScaLAPACK pdgemr2d/pdtran, 2-21x faster than MKL's.

| | |
|---|---|
| **Beats** | Intel MKL ScaLAPACK v19.1 pdgemr2d (matrix redistribution between block-cyclic layouts) |
| **Claimed result** | README chart data labels (docs/costa-same.svg and docs/costa-diff.svg, rendered locally; time in ms, COSTA vs MKL). Same layout: n=20000 14 vs 292; 40000 56 vs 1100; 60000 128 vs 2487; 80000 208 vs 4402; 100000 324 vs 6702 (chart caption '\~20x faster'; ratios 19.4x to 21.2x derived from page data). Different layouts: n=20000 188 vs 406; 40000 702 vs 1987; 60000 1608 vs 4579; 80000 2900 vs 8012; 100000 4557 vs 12737 (chart caption 'up to 3x faster'; ratios 2.2x to 2.9x derived from page data). README overview text also says it 'outperforms other scalapack implementations by orders of magnitude in some cases'. |
| **Workload** | pdgemr2d redistribution of square double-precision matrices with n = 20000 to 100000 between block-cyclic layouts, once with identical layouts (128x128 blocks) and once with different block sizes (36x36 to 128x128), on 8 Piz Daint nodes of 36 cores each with 16 MPI ranks (4x4 grid); COSTA run without rank relabelling and without memory pools. |
| **Metric** | latency |
| **Hardware** | Piz Daint (Cray XC40, CSCS), 8 nodes x 36 cores, 16 MPI ranks as a 4x4 grid; the CPU model is not stated on the page. |
| **Compiler and flags** | Not stated for the benchmark. CMakeLists.txt adds -funroll-loops (or -Munroll) and a build_type.cmake default that was not read; MKL ScaLAPACK v19.1 is named as the baseline; the MPI implementation and compiler are not given. |
| **Adoption** | 14 stars, 8 forks; used by COSMA, which is used by CP2K (README) |
| **Last commit** | 2026-09-14 |
| **Links** | [repository](https://github.com/eth-cscs/COSTA) · [benchmark](https://github.com/eth-cscs/COSTA) |

## Verdict

First-party README charts (from the public miniapps/pxgemr2d_miniapp.cpp, which times COSTA and ScaLAPACK in one binary) compare pdgemr2d on square double matrices against Intel MKL ScaLAPACK v19.1, on 8 Piz Daint (Cray XC40) nodes with 16 MPI ranks in a 4x4 grid, without rank relabelling or memory pools: with the same 128x128 block-cyclic layout on both sides, 14 vs 292 ms at n=20000 up to 324 vs 6702 ms at n=100000 (about 19-21x); with 36x36 to 128x128 blocks, 188 vs 406 ms up to 4557 vs 12737 ms (2.2-2.9x). Compiler, flags, MPI library, CPU model and which repetition is plotted are not stated. The peer-reviewed ISC 2021 paper (also compared against Cray LibSci, per search snippets; its abstract says COSTA 'outperforms the best available ScaLAPACK redistribute and transpose routines multiple times') could not be opened here.

## Use it when

- ScaLAPACK codes (CP2K-style quantum chemistry, dense eigen/linear-solver pipelines) that call pdgemr2d or pdtran/pztranc often enough to show up in profiles: relink against costa_scalapack and the calls switch over with no code changes.
- Changing block sizes or process grids between solver stages (for example 36x36 to 128x128 blocks), where the README shows 2.2x-2.9x over MKL ScaLAPACK pdgemr2d at n=20000-100000 on 16 ranks.
- Moving data between a custom or irregular distribution (FFT slabs, application-owned panels) and a block-cyclic layout, which ScaLAPACK's routines cannot express.
- Several matrices that must be redistributed at the same moment: transformer::schedule() plus one transform() sends them in one communication round.
- Codes that can pick their own target rank assignment and want the communication-volume-minimising relabelling.

## Skip it when

- Single-node or shared-memory transposes and copies: COSTA needs MPI 3 and runs the full message machinery; an in-place or tiled shared-memory transpose (transpose-scale, HPTT) fits better.
- Memory-tight runs: each call packs data into temporary send and receive buffers, and batching several layouts in one round makes those messages, and the memory they need, larger.
- Tall-skinny row-to-column reshuffles: issue #10 reported only about 1.5 Gb/s for costa::transform() on a 200000 x 600 matrix (2 Piz Daint nodes, 1 rank and 12 threads each); it was closed in January 2023 with no fix or explanation shown on the page.
- Expecting 'orders of magnitude' in general: the published charts show about 20x only when source and target layouts are identical (a case where nothing needs to move), and 2.2x-2.9x when block sizes actually change.
- Builds for Windows/MSVC or other non-GCC-compatible compilers: transform.cpp uses variable-length arrays (a GNU extension), and past issues show build breaks on Cray, Stampede2, nvc++ and in cross-compilation.

## How it is fast

It works out the exact block-to-block overlap between the source and target grids, packs everything bound for each rank into a single message with OpenMP-parallel packing (applying alpha/beta, cache-blocked transpose and conjugation during the copy), posts all MPI_Irecv/MPI_Isend nonblocking, copies rank-local blocks while messages are in flight, and unpacks each message as soon as MPI_Waitany returns it. Data already on the right rank never touches MPI. Optionally it suggests an MPI rank relabelling, computed from the communication-volume graph by a greedy pass over edges sorted by volume, so that layouts differing only by a rank permutation need no communication at all. The README benchmarks did not use relabelling.

## Compared with alternatives

COSTA is the layout-conversion layer under COSMA (the catalog's communication-optimal pdgemm replacement), so use COSMA or SPLA when the bottleneck is the multiply itself and COSTA when it is pdgemr2d/pdtran or moving data between custom and block-cyclic layouts. For transposes within one node, HPTT or transpose-scale are the right tools; COSTA only pays off across MPI ranks.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | MPI 3 and OpenMP (required); a ScaLAPACK (MKL, Cray LibSci, NVPL or custom via SCALAPACK_ROOT) only for the wrapper libraries; cxxopts and semiprof are fetched by CMake only for the miniapps, tests and profiling. Search results list a conda-forge package (costa-scalapack); a request to add COSTA 2.1 to Spack (issue #11) is closed. |
| **Minimum toolchain** | C++14 (target_compile_features cxx_std_14); CMake 3.22 per CMakeLists.txt (INSTALL.md still says 3.12); Release build by default plus -funroll-loops (or -Munroll for NVHPC). |
| **Platforms** | Linux HPC systems with MPI (Cray XC/EX, NVHPC toolchains); CMake has macOS rpath handling; Windows not documented. The only published benchmark machine is Piz Daint (Cray XC40). |
| **Thread safety** | Not documented. transform() is a collective over the union communicator, and packing uses a process-wide per-type workspace singleton (memory::get_costa_context_instance), so concurrent transforms from several threads of one rank are unsafe in practice (inferred from source). It uses OpenMP internally and checks omp_in_parallel() before spawning threads in the transpose kernel. |
| **Drop-in for the baseline** | partial — for ScaLAPACK's p?gemr2d and p?tran/p?tranu/p?tranc, linking costa_scalapack before ScaLAPACK swaps in COSTA with no source changes; COSTA is not a BLAS/LAPACK kernel and provides no other ScaLAPACK routines. |

## Gotchas

- Link order is the whole switch: if ScaLAPACK appears before costa_scalapack on the link line, the vendor routine silently wins. Use costa_prefixed_scalapack if you want both versions side by side.
- Each wrapper call builds the union of A's and C's communicators with MPI_Comm_create_group on MPI_COMM_WORLD, and costa_pxgemr2d.cpp never frees it (no MPI_Comm_free in the files read). Programs that call pdgemr2d thousands of times should watch for communicator-handle exhaustion.
- The native transform() takes the layouts by non-const reference and temporarily transposes the initial layout object in place, undoing it afterwards. Do not share a layout object across threads during a call.
- Release v2.3.1 is marked deprecated: its beta==0 handling had a bug that v2.3.2 fixed (beta==0 or alpha==0 must overwrite the destination). Pin v2.3.2 or later.

## Known shortcomings

- Tier C: first-party pdgemr2d charts against MKL ScaLAPACK 19.1 on 8 Piz Daint nodes, with no compiler, flags or CPU model stated. The ISC21 paper (arXiv 2106.06601) could not be opened; paper-access retier candidate (likely B).
- The about 20x figure appears only when source and target layouts are identical; a real reshuffle is 2.2-2.9x. Issue #10 (1.5 Gb/s on a 200000x600 transform) closed with no fix shown. The ScaLAPACK wrapper creates a union communicator per call with no MPI_Comm_free seen; a global per-type workspace singleton makes it not thread-safe. v2.3.1 is deprecated (beta == 0 bug). CMake minimum is 3.22 while INSTALL.md says 3.12.

## Caveats and trade-offs

The baseline is MKL's ScaLAPACK redistribution routine pdgemr2d, not a BLAS or LAPACK kernel, so it only loosely fits the blas-lapack baselines. The identical-layout case (about 20x) most likely reflects MKL's slow generic path when no data needs to move (my inference, not stated by the authors). The charts are first-party; MKL and MPI settings, the compiler, flags and CPU model are not stated, and the README does not say which repetition or statistic is plotted (the miniapp's n_rep default is 2 and it prints every repetition's time in ms for both COSTA and ScaLAPACK). The benchmark code is public (miniapps/pxgemr2d_miniapp.cpp, pxtran_miniapp.cpp). The peer-reviewed paper (Kabic, Pintarelli, Kozhevnikov, VandeVondele, ISC 2021, Springer LNCS pp. 217-236; arXiv 2106.06601) is cited in the README but could not be opened (Springer and arXiv are blocked in this session); a check that can open it should consider B and whether its numbers match the README charts. 'Orders of magnitude' in the README overview is not shown by these charts (largest ratio about 21x). Numbers were read from the chart data labels.

Needs MPI 3 and OpenMP and CMake 3.12 or newer. Drop-in ScaLAPACK wrappers (pdgemr2d, pstran, pdtran, pctranu/c and complex variants) take effect when COSTA is linked before ScaLAPACK. Handles arbitrary irregular layouts, not only block-cyclic, and can transform several layouts in one communication round at the cost of larger messages and more memory. Optional rank relabelling can remove communication entirely when layouts differ only by a rank permutation (not used in these charts).

## Maintenance

Actively maintained by ETH Zurich/CSCS (v2.3.3 released 2026-09-14 with an nvc++ build fix; one open issue, about empty install directories) and BSD-3-Clause, with production use through COSMA in CP2K, which makes it a low-risk relink for ScaLAPACK users.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README Performance Results section and its charts (docs/costa-same.svg, docs/costa-diff.svg, rendered here) show first-party pdgemr2d times for COSTA vs MKL ScaLAPACK v19.1 on 8 Piz Daint nodes, produced by the public miniapps/pxgemr2d_miniapp.cpp, which runs both COSTA and ScaLAPACK in one binary. No compiler, flags or CPU model is stated, so not A; the peer-reviewed ISC21 paper (Springer LNCS, arXiv 2106.06601) could not be opened, so B is not confirmed.
- **Verifier notes:** All ten COSTA/MKL data labels in the record match the rendered charts exactly, and the derived ratios (19.4x-21.2x same layout, 2.2x-2.9x different layouts) are correct. Paper-access retier candidate (likely B). Metadata verified: BSD-3-Clause, 14 stars, 8 forks, not a fork, not archived, last commit 2026-09-14 (v2.3.3), active.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/eth-cscs/COSTA>
  - <https://github.com/eth-cscs/COSTA/commits>
  - <https://raw.githubusercontent.com/eth-cscs/COSTA/HEAD/README.md>
  - <https://raw.githubusercontent.com/eth-cscs/COSTA/HEAD/docs/costa-same.svg>
  - <https://raw.githubusercontent.com/eth-cscs/COSTA/HEAD/docs/costa-diff.svg>
  - <https://raw.githubusercontent.com/eth-cscs/COSTA/HEAD/miniapps/pxgemr2d_miniapp.cpp>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/eth-cscs/COSTA/HEAD/README.md>
  - <https://raw.githubusercontent.com/eth-cscs/COSTA/HEAD/INSTALL.md>
  - <https://raw.githubusercontent.com/eth-cscs/COSTA/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/eth-cscs/COSTA/HEAD/cmake/build_type.cmake>
  - <https://raw.githubusercontent.com/eth-cscs/COSTA/HEAD/src/costa/CMakeLists.txt>
  - <https://raw.githubusercontent.com/eth-cscs/COSTA/HEAD/src/costa/grid2grid/transform.cpp>
  - <https://raw.githubusercontent.com/eth-cscs/COSTA/HEAD/src/costa/grid2grid/communication_data.cpp>
  - <https://raw.githubusercontent.com/eth-cscs/COSTA/HEAD/src/costa/grid2grid/ranks_reordering.cpp>
  - <https://raw.githubusercontent.com/eth-cscs/COSTA/HEAD/src/costa/grid2grid/memory_utils.hpp>
  - <https://raw.githubusercontent.com/eth-cscs/COSTA/HEAD/src/costa/pxgemr2d/costa_pxgemr2d.cpp>
  - <https://raw.githubusercontent.com/eth-cscs/COSTA/HEAD/src/costa/pxgemr2d/pxgemr2d.cpp>
  - <https://raw.githubusercontent.com/eth-cscs/COSTA/HEAD/src/costa/scalapack.cpp>
  - <https://raw.githubusercontent.com/eth-cscs/COSTA/HEAD/miniapps/pxgemr2d_miniapp.cpp>
  - <https://github.com/eth-cscs/COSTA/issues?q=is%3Aissue>
  - <https://github.com/eth-cscs/COSTA/issues/10>
  - <https://github.com/eth-cscs/COSTA/releases>
  - WebSearch snippets for https://arxiv.org/abs/2106.06601 and https://link.springer.com/chapter/10.1007/978-3-030-78713-4_12 (not opened; arXiv and Springer are egress-blocked)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/eth-cscs/costa`) · [data/wave8/enrich/raw/github_com_eth_cscs_costa.json](../../../data/wave8/enrich/raw/github_com_eth_cscs_costa.json) (enrichment confidence 0.8)

</details>
