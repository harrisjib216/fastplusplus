# small_gicp

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only C++17 point-cloud registration (ICP/GICP/VGICP) and voxel downsampling; beats PCL VoxelGrid, PCL GICP and fast_gicp.

| | |
|---|---|
| **Beats** | PCL pcl::VoxelGrid (voxel downsampling) and pcl::GICP / fast_gicp::GICP (registration) |
| **Claimed result** | Single-threaded small_gicp::voxelgrid_sampling about 1.3x faster than pcl::VoxelGrid; multi-threaded voxelgrid_sampling_tbb (6 threads) about 3.2x faster than pcl::VoxelGrid; single-thread small_gicp::GICP about 2.4x and 1.9x faster than pcl::GICP and fast_gicp::GICP; multi-threaded kd-tree construction up to 4x faster than its own single-thread version (README says 6x), and the single-thread kd-tree is about equal to nanoflann. |
| **Workload** | Voxel-grid downsampling of KITTI 00 LiDAR scans, and GICP odometry over KITTI 00, compared with PCL and fast_gicp; also kd-tree construction compared across its own single- and multi-threaded variants (all nanoflann-based). |
| **Metric** | throughput |
| **Hardware** | Not stated for the downsampling or GICP benchmarks (AMD 5995WX is mentioned only in a struck-through kd-tree note) |
| **Adoption** | 1.0k stars; vcpkg port small-gicp; JOSS 2024 paper (doi 10.21105/joss.06948) |
| **Last commit** | 2026-09-29 |
| **Links** | [repository](https://github.com/koide3/small_gicp) · [benchmark](https://github.com/koide3/small_gicp/blob/master/BENCHMARK.md) |

## Verdict

First-party KITTI 00 runs (BENCHMARK.md and README, plots only): single-thread voxel downsampling about 1.3x faster than pcl::VoxelGrid and 3.2x with 6 TBB threads; single-thread GICP odometry about 2.4x faster than pcl::GICP and 1.9x faster than fast_gicp::GICP with near-identical accuracy (APE 6.096 vs fast_gicp 6.118 vs pcl_gicp 6.451); parallel kd-tree build up to 4x (BENCHMARK.md) or 6x (README) over its own single-thread build, which is about nanoflann speed. CPU, compiler and flags are not stated (only a struck-through AMD 5995WX remark); scripts are public, the CMake default is Release without -march=native.

## Use it when

- LiDAR odometry or scan matching that already uses pcl::GeneralizedIterativeClosestPoint or fast_gicp on the CPU and wants a faster, mostly source-compatible replacement.
- Voxel downsampling of large scans, including fine resolutions where pcl::VoxelGrid fails (README: 0.5 mm voxels on a 1000 m-wide cloud) and you want exact per-voxel means rather than pcl::ApproximateVoxelGrid's spurious points.
- Multi-core machines: downsampling, kd-tree build, covariance estimation and the registration reduction are all parallel (OpenMP or TBB).
- Python pipelines that need GICP/VGICP without PCL (pip install small_gicp; works on NumPy and Open3D data).
- Scan-to-scan odometry that reuses preprocessed clouds and trees across successive alignments (swapSourceAndTarget, preprocess_points).

## Skip it when

- Low-overlap registration with a tight correspondence distance: it runs an unbounded nearest-neighbour search and only then rejects by max_dist_sq, and a user measured it slower than Open3D's radius-limited search on \~10% overlap data (issue #134, open).
- GPU pipelines: no GPU code is included (fast_gicp's CUDA VGICP/NDT have not been ported; issue #80).
- General computational geometry or spatial indexing: it is a registration toolkit, not a Boost.Geometry/CGAL/GEOS replacement, and its kd-tree offers kNN only (no radius search in kdtree.hpp).
- Workflows needing bit-identical, deterministic downsampling with threads: the OpenMP/TBB voxel functions can return up to 10% more points than the single-thread one, varying run to run.
- ROS Noetic's stock PCL or any PCL older than 1.11 (boost::shared_ptr), which the PCL interface does not support (README; issue #33).

## How it is fast

Voxel downsampling packs each point's three integer voxel coordinates (fast floor) into one 63-bit key (21 bits per axis), sorts (key, index) pairs (parallel quicksort in the OpenMP/TBB variants) and averages each run, so no hash map is needed. The kd-tree is a from-scratch nanoflann-style median-split tree (std::nth_element on the widest axis) whose recursive build runs as OpenMP or TBB tasks, with fixed-size compile-time kNN result buffers. Registration linearizes one GICP factor per source point (Mahalanobis weight from the inverse of the fused target and rotated source covariances) and sums the 6x6 normal equations with an OpenMP or TBB parallel reduction; a TBB flow-graph odometry pipeline scales to about 128 threads.

## Compared with alternatives

It is the only catalogued sibling that does point-cloud registration and voxel downsampling; for plain kNN or radius search pick nanoflann (which its own single-thread kd-tree roughly matches) or PicoTree, and pick small_gicp when you need the whole parallel registration pipeline or a faster PCL GICP.

## Integration

| | |
|---|---|
| **Form** | header-only (optional compiled helper library, shared by default, and a pybind11 Python module) |
| **Dependencies** | Eigen 3 (CMake downloads 3.4.0 if missing); bundled nanoflann-derived kd-tree and Sophus-derived Lie utilities; optional OpenMP, Intel TBB, PCL &gt;= 1.11; fmt for tests, examples and benchmarks |
| **Minimum toolchain** | C++17, CMake 3.16; Python &gt;= 3.7 for the bindings |
| **Platforms** | Linux, macOS and Windows (CI for all three); PyPI wheels for manylinux x86-64 and aarch64, macOS 14+, Windows 64-bit; SSE/SSE2 baseline unless BUILD_WITH_MARCH_NATIVE=ON |
| **Thread safety** | Parallelism is internal via num_threads arguments and OMP/TBB variants; concurrent use of shared objects from caller threads is not documented. On MSVC, OpenMP kd-tree construction is compiled out (single-threaded) because task-based OpenMP caused memory errors with Eigen. |
| **Drop-in for the baseline** | partial — RegistrationPCL is a pcl::Registration subclass with mostly the same interface as pcl::GICP, but voxelgrid_sampling_\* are free functions rather than a pcl::Filter, and fast_gicp users must switch APIs |

## Gotchas

- BUILD_WITH_MARCH_NATIVE gives about 1.1x but crashes unless every linked library (Eigen users, PCL) is built with -march=native; it is off by default for that reason (BENCHMARK.md). Open issue #108 reports an Eigen unaligned-array assertion in the basic example.
- Voxel coordinates must fit 21 bits per axis (for 1 cm voxels, coordinates within about ±10.5 km); out-of-range points are dropped with one std::cerr line per point. By my reading of downsampling_omp.hpp, an out-of-range point that starts a 1024-point block is still emitted in the parallel variant.
- align() re-orthonormalizes the rotation of init_T since the fix for issue #127 (incremental registration into a Gaussian voxel map drifted to non-orthogonal rotations and NaN after \~40 clouds; closed 2026-09-29); use a current commit for long incremental runs. It only warns, and still runs, when a cloud has 10 points or fewer.
- Input point types must expose homogeneous 4D coordinates with w = 1: downsampling divides each voxel sum by its w component to get the mean.

## Known shortcomings

- JOSS paper restates first-party bullets; kd-tree gain stated as 4x/6x/6x vs nanoflann; point-cloud registration, an edge case for geometry-spatial.
- Open #134: unbounded nearest-neighbour search with rejection afterwards, measured slower than Open3D on \~10%-overlap data. #127 (non-orthogonal rotation then NaN after \~40 incremental clouds) fixed 2026-09-29. Threaded downsampling is nondeterministic (up to 10% more points); by code reading the OMP variant still outputs an out-of-range point when one starts a 1024-point block.

## Caveats and trade-offs

Baselines are PCL and fast_gicp, not Boost.Geometry, CGAL or GEOS, so it fits the geometry-spatial category only loosely (point-cloud spatial operations). Its kd-tree is nanoflann-derived and README says the single-thread build is about equal to nanoflann. The multi-thread kd-tree gain is stated three ways: BENCHMARK.md 'up to 4x' over its own single-thread build, README 'up to 6x' over the single-thread version, and the JOSS paper source (docs/paper.md) 'up to 6x faster than that of nanoflann'. Benchmark scripts are public, but CPU, compiler and flags are not stated for the PCL comparisons, and only KITTI 00 was used. The JOSS paper repeats the README bullets and adds no independent measurement.

Depends on Eigen; optional TBB or OpenMP; bundles nanoflann and Sophus; Python bindings. Aimed at LiDAR point-cloud registration and downsampling, not general geometry. The README warns against -march=native unless every linked library uses it (about 1.1x gain).

## Maintenance

Actively maintained (last commit 2026-09-29, version 1.0.1), MIT-licensed, on PyPI, with a JOSS 2024 paper; a single main author (Kenji Koide, AIST) and 24 open issues, several labelled bug (performance reports #89, #118, #134; build issues #90, #104).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** BENCHMARK.md gives first-party KITTI 00 results against pcl::VoxelGrid (1.3x single-thread, 3.2x with 6 TBB threads) and pcl::GICP / fast_gicp::GICP (2.4x / 1.9x), with public scripts (scripts/run_downsampling_benchmark.sh, run_odometry_benchmark.sh, src/benchmark/). No CPU model (only a struck-through AMD 5995WX remark), compiler or flags are stated for these runs, beyond CMake defaulting to Release and -march=native being off by default, so it is C. The JOSS 2024 paper (source docs/paper.md) only repeats the same first-party bullets, and JOSS reviews software, not benchmarks, so it does not lift the tier to B.
- **Verifier notes:** All quoted ratios appear verbatim in BENCHMARK.md and in the README Benchmark section. The vcpkg port named in stars_or_usage was not checked (the repo page does not mention it). joss.theoj.org is egress-blocked, so the paper was read from its source file in the repo.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/koide3/small_gicp/HEAD/BENCHMARK.md>
  - <https://raw.githubusercontent.com/koide3/small_gicp/HEAD/README.md>
  - <https://raw.githubusercontent.com/koide3/small_gicp/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/koide3/small_gicp/HEAD/docs/paper.md>
  - <https://raw.githubusercontent.com/koide3/small_gicp/HEAD/scripts/run_odometry_benchmark.sh>
  - <https://raw.githubusercontent.com/koide3/small_gicp/HEAD/CMakeLists.txt>
  - <https://github.com/koide3/small_gicp>
  - <https://github.com/koide3/small_gicp/commits/master>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/koide3/small_gicp/HEAD/README.md>
  - <https://raw.githubusercontent.com/koide3/small_gicp/HEAD/BENCHMARK.md>
  - <https://raw.githubusercontent.com/koide3/small_gicp/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/koide3/small_gicp/HEAD/docs/paper.md>
  - <https://raw.githubusercontent.com/koide3/small_gicp/HEAD/package.xml>
  - <https://raw.githubusercontent.com/koide3/small_gicp/HEAD/pyproject.toml>
  - <https://raw.githubusercontent.com/koide3/small_gicp/HEAD/include/small_gicp/util/downsampling.hpp>
  - <https://raw.githubusercontent.com/koide3/small_gicp/HEAD/include/small_gicp/util/downsampling_omp.hpp>
  - <https://raw.githubusercontent.com/koide3/small_gicp/HEAD/include/small_gicp/util/downsampling_tbb.hpp>
  - <https://raw.githubusercontent.com/koide3/small_gicp/HEAD/include/small_gicp/util/fast_floor.hpp>
  - <https://raw.githubusercontent.com/koide3/small_gicp/HEAD/include/small_gicp/ann/kdtree.hpp>
  - <https://raw.githubusercontent.com/koide3/small_gicp/HEAD/include/small_gicp/ann/kdtree_omp.hpp>
  - <https://raw.githubusercontent.com/koide3/small_gicp/HEAD/include/small_gicp/ann/knn_result.hpp>
  - <https://raw.githubusercontent.com/koide3/small_gicp/HEAD/include/small_gicp/ann/traits.hpp>
  - <https://raw.githubusercontent.com/koide3/small_gicp/HEAD/include/small_gicp/ann/incremental_voxelmap.hpp>
  - <https://raw.githubusercontent.com/koide3/small_gicp/HEAD/include/small_gicp/registration/registration.hpp>
  - <https://raw.githubusercontent.com/koide3/small_gicp/HEAD/include/small_gicp/factors/gicp_factor.hpp>
  - <https://github.com/koide3/small_gicp/issues>
  - <https://github.com/koide3/small_gicp/issues?q=is%3Aissue+label%3Abug>
  - <https://github.com/koide3/small_gicp/issues/89>
  - <https://github.com/koide3/small_gicp/issues/118>
  - <https://github.com/koide3/small_gicp/issues/127>
  - <https://github.com/koide3/small_gicp/issues/134>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/koide3/small_gicp`) · [data/wave8/enrich/raw/github_com_koide3_small_gicp.json](../../../data/wave8/enrich/raw/github_com_koide3_small_gicp.json) (enrichment confidence 0.8)

</details>
