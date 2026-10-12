# fast_gicp (FastGICP / FastVGICP / FastVGICPCuda)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-3-Clause` · 🟡 stale

> PCL-compatible multithreaded GICP and voxelized GICP (CPU and CUDA); about 6-9x faster than PCL GICP on 8 cores.

| | |
|---|---|
| **Beats** | PCL pcl::GeneralizedIterativeClosestPoint (GICP); also PCL NormalDistributionsTransform (NDT) |
| **Claimed result** | README table, i9-9900K + RTX 2080 Ti: pcl_gicp single 127.508 ms, 100 times 12549.4 ms (fitness 0.204892); pcl_ndt single 53.5904 ms, 100 times 5467.16 ms; fgicp_st (single thread) 111.324 ms / 10662.7 ms; fgicp_mt 20.1602 ms / 1585 ms (fitness 0.204412); vgicp_mt 18.1106 ms / 1381 ms; vgicp_cuda (parallel_kdtree) 15.9587 ms / 1451.85 ms; vgicp_cuda (gpu_rbf_kernel) 5.91508 ms / 590.725 ms (fitness 0.20557). Derived from page data versus pcl_gicp: fgicp_mt 6.3x (single) and 7.9x (100 runs); vgicp_mt 7.0x and 9.1x; vgicp_cuda rbf kernel 21.6x and 21.2x; single-threaded fgicp_st only 1.15x and 1.18x. README headline rates: FastGICP \~40 FPS, FastGICPSingleThread \~15 FPS, FastVGICP \~70 FPS, FastVGICPCuda \~120 FPS, NDTCuda \~500 FPS. |
| **Workload** | Registering one pair of point-cloud scans (target 17,249 points, source 17,518 points after a 0.1 m approximate voxel grid) with GICP-family methods; wall time of a single alignment and of 100 repeated alignments, with fitness score reported. |
| **Metric** | latency |
| **Hardware** | Core i9-9900K, GeForce RTX 2080 Ti |
| **Compiler and flags** | CMakeLists.txt sets CMAKE_BUILD_TYPE Release (CMake default Release flags) and adds OpenMP flags; no -march option seen. Compiler name and version not stated (README says tested on Ubuntu 18.04/20.04 with CUDA 11.1). |
| **Adoption** | 1.7k stars, 374 forks |
| **Last commit** | 2025-04-24 |
| **Links** | [repository](https://github.com/koide3/fast_gicp) · [benchmark](https://github.com/koide3/fast_gicp) |

## Verdict

Own-repo benchmark (src/align.cpp) on one KITTI-style scan pair (17,249 and 17,518 points after a 0.1 m approximate voxel grid), Core i9-9900K plus RTX 2080 Ti, PCL version and compiler not stated: PCL GICP 127.5 ms per alignment vs FastGICP multithreaded 20.2 ms (about 6.3x), FastVGICP multithreaded 18.1 ms (about 7.0x), VGICP CUDA RBF kernel 5.9 ms (about 21.6x), and single-threaded FastGICP 111.3 ms (about 1.15x), ratios derived from page data. small_gicp's KITTI 00 benchmark by the same author implies single-threaded fast_gicp::GICP is about 1.26x faster than pcl::GICP (2.4x / 1.9x, derived from page data), with lower drift (RPE(100) 1.212 vs 2.424).

## Use it when

- Existing PCL code calls pcl::GeneralizedIterativeClosestPoint and you want a near drop-in speedup on a multi-core x86 CPU (the README shows 20 ms vs 128 ms per scan pair at about 17k points on an i9-9900K).
- Frame-to-frame LiDAR odometry where the previous frame's covariances can be reused: the benchmark's reuse mode cuts 100 fgicp_mt alignments from 1585 ms to 1018 ms.
- You have an NVIDIA GPU and need CUDA registration (FastVGICPCuda at 5.9 ms per pair with the RBF-kernel covariances and 16.0 ms with the CPU kd-tree; NDTCuda). The author's successor small_gicp ships no GPU implementation.
- You are stuck on an older PCL that still uses boost::shared_ptr (the headers switch at PCL 1.10). small_gicp's PCL interface needs PCL 1.11 or newer.
- Python prototyping on numpy arrays through pygicp.

## Skip it when

- New CPU-only projects: the author's small_gicp (already catalogued) is reported 1.9x faster single-threaded than fast_gicp::GICP on KITTI 00, scales better with threads, is header-only with Eigen as its only hard dependency, and is actively maintained.
- Single-core or thread-constrained targets: single-threaded FastGICP is only about 1.15x faster than PCL GICP in the README. Issue #145 reports multithreaded GICP and VGICP running slower than single-threaded on an i9-13900KF under WSL/Docker (100 runs: 12,986 vs 9,945 ms and 16,300 vs 7,514 ms).
- Large initial misalignment: like any ICP-family local method it needs a good initial guess; issue #169 reports failure under large rotation, and #135 reports a score that drifts over time.
- Projects that cannot take PCL, Boost and OpenMP, or a CUDA toolchain plus the nvbio submodule (tested only with CUDA 11.1 on Ubuntu 18.04/20.04). Windows builds are not documented, and issue #158 (cannot build fast_gicp.lib) is open.
- You need upstream fixes: the last commit is 2025-04-24 and 69 issues are open, including #148, which claims the Levenberg-Marquardt gain-ratio (rho) formula in step_lm() is wrong and has no maintainer reply.

## How it is fast

The CPU code parallelizes per-point work with OpenMP: nearest-neighbor correspondence search, covariance estimation (k=20 neighbors, PLANE regularization via SVD) and Hessian/gradient accumulation into per-thread buffers. Each class solves a Gauss-Newton or Levenberg-Marquardt problem on SE(3) (LM by default, at most 64 iterations). VGICP (Koide et al., ICRA 2021) replaces the per-point kd-tree search with a lookup in a hash map of Gaussian voxels (1.0 m default resolution, DIRECT1 neighborhood), each voxel aggregating the target-point distributions. Covariances are cached per input cloud and can be carried over with swapSourceAndTarget() in odometry. The CUDA build moves voxel mapping, correspondences and derivatives to the GPU; covariances come from a CPU parallel kd-tree, GPU brute force, or an approximate RBF-kernel estimate.

## Compared with alternatives

Choose fast_gicp over small_gicp only when you need its CUDA paths (FastVGICPCuda, NDTCuda) or must stay on a pre-1.11 PCL; otherwise small_gicp is faster, lighter and maintained. Neither competes with nanoflann or ikd-Tree, which are neighbor-search structures rather than registration solvers.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | PCL, Eigen3, Boost (hash and format headers, normally pulled in with PCL), OpenMP; README also lists Sophus and nvbio, which are git submodules under thirdparty/ along with Eigen; optional CUDA (BUILD_VGICP_CUDA=ON) builds an extra libfast_vgicp_cuda with cuBLAS; optional pybind11 for pygicp |
| **Minimum toolchain** | Not documented beyond CMake 3.10; CMakeLists.txt sets no C++ standard and forces CMAKE_BUILD_TYPE Release; tested on Ubuntu 18.04/20.04 with CUDA 11.1; builds as a ROS1 catkin or ROS2 ament package or as plain CMake |
| **Platforms** | Linux (x86-64 tested in the README benchmark); macOS via Homebrew libomp per the README; Windows not documented; the CUDA classes need an NVIDIA GPU |
| **Thread safety** | Not documented. Each registration object caches covariances, correspondences and the voxel map as mutable members and runs its own OpenMP team, so use one instance per thread. |
| **Drop-in for the baseline** | partial: derives from pcl::Registration, so generic align() code works, but it is not a pcl::GeneralizedIterativeClosestPoint subclass, uses its own defaults (LM optimizer, 64 max iterations, k=20, PLANE regularization) and its own setters (setNumThreads, setRegularizationMethod, setResolution), and results differ slightly (fitness 0.2044 vs 0.2049 in the README). |

## Gotchas

- The thread count defaults to omp_get_max_threads(); the README itself notes that fewer threads can be faster on some machines, so set setNumThreads explicitly and measure.
- Covariance caching is keyed on the cloud pointer: setInputSource/setInputTarget return early when given the same pointer. If you modify a cloud in place, call clearSource()/clearTarget() first (the benchmark does), or stale covariances are used.
- The output cloud passed to align() must be a different object from the source and target clouds; issue #133 reports covariance computation failing with an index error otherwise.
- CPU FastVGICP with NeighborSearchMethod::DIRECT_RADIUS (supported only by the CUDA class) hits the default branch of neighbor_offsets(), which prints 'unsupported neighbor search method' and calls abort(). The GPU_RBF_KERNEL covariance mode needs a hand-tuned kernel width and is described in align.cpp as 'extremely fast but maybe a bit inaccurate'.

## Known shortcomings

- Tier C: the README benchmark (Core i9-9900K + RTX 2080 Ti, produced by the public src/align.cpp) names no compiler. Last commit 2025-04-24, stale; the same author's successor small_gicp is already listed and is the maintained choice.
- Single-threaded it is only about 1.15x vs PCL GICP; issue #145 shows the multithreaded path slower than single-threaded on an i9-13900KF under WSL/Docker; 69 open issues including #148 (LM rho formula claimed wrong, no maintainer reply); stale since 2025-04-24. The VGICP ICRA 2021 paper (staff.aist.go.jp blocked) is known only from a snippet: PCL GICP 201 ms, single-threaded GICP 189 ms, VGICP 156 ms, multithreaded 68/50 ms, GPU 6 ms.

## Caveats and trade-offs

Tier would be A except that the compiler is never named and the flags come only from the CMake Release default plus OpenMP, so it stays C (own-repo benchmark with partial methodology). Benchmark code is public (src/align.cpp) but the README shows a single scan pair (data/251370668.pcd vs 251371071.pcd) on one machine. Most of the speedup comes from multithreading and GPU use against PCL's default single-threaded GICP/NDT: fgicp_mt and vgicp_mt both run with omp_get_max_threads() (FastGICP's constructor default; align.cpp leaves setNumThreads(8) commented out), and the thread count actually used on the 8-core/16-thread i9-9900K is not printed. Single-threaded fgicp_st is only about 1.15x faster than pcl_gicp. The PCL version is not stated; iteration and convergence settings are each class's defaults and were not verified to be identical; pcl_ndt reaches a worse fitness (0.2296) than the GICP variants (about 0.204), so it is a different algorithm rather than a like-for-like baseline. align.cpp also prints ndt_cuda rows that the README output omits. The ICRA 2021 VGICP paper was not opened. The README badges and install commands still point to SMRT-AIST/fast_gicp (the copyright holder), and the README now announces small_gicp (already listed as koide3/small_gicp) as the faster successor library. Last commit 2025-04-24 (over 12 months).

Drop-in PCL registration interface, but depends on PCL, Eigen, OpenMP, Sophus and (for CUDA) nvbio. VGICP is a voxelized approximation of GICP and the GPU rbf-kernel covariance mode is described in the source as 'extremely fast but maybe a bit inaccurate' (its fitness score 0.20557 is the worst in the table). README notes that using fewer threads than the maximum can be faster in some environments. The author's newer small_gicp (already on the known list) is stated in the README to be twice as fast as fast_gicp.

## Maintenance

Stale since 2025-04-24 with 69 open issues, and the author points users to small_gicp; BSD-3-Clause and usable, but plan to own any fixes you need.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** README Benchmark section shows pcl_gicp and pcl_ndt against fgicp/vgicp variants on a Core i9-9900K + RTX 2080 Ti, produced by the public src/align.cpp; CMakeLists.txt forces CMAKE_BUILD_TYPE Release plus OpenMP, but the compiler is never named, so it cannot be A and stays first-party C.
- **Verifier notes:** Benchmark table, hardware line and BSD-3-Clause license verified from the README, LICENSE, CMakeLists.txt and src/align.cpp; github.com page shows 1.7k stars, 374 forks, not archived, not a fork; last commit 2025-04-24 (stale). Separate project from the already-listed successor koide3/small_gicp, so not a duplicate, but worth cross-linking.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier; same author's small_gicp BENCHMARK.md (KITTI 00) implies single-threaded fast_gicp::GICP about 1.26x faster than pcl::GICP (2.4 vs 1.9, derived from page data) with lower drift (RPE(100) 1.212 vs 2.424)
- **Pages the verifier opened:**
  - <https://github.com/koide3/fast_gicp>
  - <https://github.com/koide3/fast_gicp/commits>
  - <https://raw.githubusercontent.com/koide3/fast_gicp/HEAD/README.md>
  - <https://raw.githubusercontent.com/koide3/fast_gicp/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/koide3/fast_gicp/HEAD/src/align.cpp>
  - <https://raw.githubusercontent.com/koide3/fast_gicp/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/koide3/fast_gicp/HEAD/include/fast_gicp/gicp/impl/fast_gicp_impl.hpp>
- **Sources the enricher read:**
  - <https://github.com/koide3/fast_gicp>
  - <https://raw.githubusercontent.com/koide3/fast_gicp/HEAD/README.md>
  - <https://raw.githubusercontent.com/koide3/fast_gicp/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/koide3/fast_gicp/HEAD/package.xml>
  - <https://raw.githubusercontent.com/koide3/fast_gicp/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/koide3/fast_gicp/HEAD/setup.py>
  - <https://raw.githubusercontent.com/koide3/fast_gicp/HEAD/src/align.cpp>
  - <https://raw.githubusercontent.com/koide3/fast_gicp/HEAD/include/fast_gicp/gicp/fast_gicp.hpp>
  - <https://raw.githubusercontent.com/koide3/fast_gicp/HEAD/include/fast_gicp/gicp/fast_vgicp.hpp>
  - <https://raw.githubusercontent.com/koide3/fast_gicp/HEAD/include/fast_gicp/gicp/fast_vgicp_voxel.hpp>
  - <https://raw.githubusercontent.com/koide3/fast_gicp/HEAD/include/fast_gicp/gicp/fast_vgicp_cuda.hpp>
  - <https://raw.githubusercontent.com/koide3/fast_gicp/HEAD/include/fast_gicp/gicp/lsq_registration.hpp>
  - <https://raw.githubusercontent.com/koide3/fast_gicp/HEAD/include/fast_gicp/gicp/gicp_settings.hpp>
  - <https://raw.githubusercontent.com/koide3/fast_gicp/HEAD/include/fast_gicp/gicp/impl/fast_gicp_impl.hpp>
  - <https://raw.githubusercontent.com/koide3/fast_gicp/HEAD/include/fast_gicp/gicp/impl/fast_vgicp_impl.hpp>
  - <https://raw.githubusercontent.com/koide3/fast_gicp/HEAD/include/fast_gicp/gicp/impl/lsq_registration_impl.hpp>
  - <https://github.com/koide3/fast_gicp/tree/master/thirdparty>
  - <https://github.com/koide3/fast_gicp/issues?q=is%3Aissue>
  - <https://github.com/koide3/fast_gicp/issues/145>
  - <https://github.com/koide3/fast_gicp/issues/133>
  - <https://github.com/koide3/fast_gicp/issues/148>
  - <https://raw.githubusercontent.com/koide3/small_gicp/HEAD/README.md>
  - <https://raw.githubusercontent.com/koide3/small_gicp/HEAD/BENCHMARK.md>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/koide3/fast_gicp`) · [data/wave8/enrich/raw/github_com_koide3_fast_gicp.json](../../../data/wave8/enrich/raw/github_com_koide3_fast_gicp.json) (enrichment confidence 0.8)

</details>
