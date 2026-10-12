# TinyBVH

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only C++ BVH builder and ray tracer; author's benchmark shows faster SAH builds and single-ray traversal than Embree.

| | |
|---|---|
| **Beats** | Intel Embree (also madmann91/bvh) |
| **Claimed result** | README chart (approximate readings from bar chart): Sponza 263k-tri 'fast build' BVH build \~6.7 ms vs Embree \~17.5 ms and Madmann91 \~13 ms (\~2.6x vs Embree, derived from page data); single-core CPU traversal nearest-hit \~16 vs Embree \~6.2 and MM91 \~2.3 MRay/s; any-hit \~36 vs Embree \~23.5 MRay/s. Author calls results 'preliminary'. |
| **Workload** | SAH BVH build (Crytek Sponza, 263k triangles) and single-core single-ray nearest-hit/any-hit traversal on CPU vs Embree and madmann91/bvh; separately GPU traversal up to 5 billion rays/s on Sponza (RTX 5080 laptop, no baseline). |
| **Metric** | build-time |
| **Adoption** | 1.2k stars |
| **Last commit** | 2026-09-25 |
| **Links** | [repository](https://github.com/jbikker/tinybvh) · [benchmark](https://github.com/jbikker/tinybvh) |

## Verdict

The author's preliminary chart, produced with the public tiny_bvh_benchmark.cpp (built per build.bat with g++ -std=c++20 -mavx2 -mfma -Ofast; Windows-only harness; CPU model not published), measures Crytek Sponza (263k triangles): a 'fast build' takes \~6.7 ms vs Embree 4 at \~17.5 ms and madmann91/bvh at \~13 ms (\~2.6x vs Embree, derived from page data). Single-core single-ray traversal reaches \~16 vs \~6.2 (Embree) vs \~2.3 (madmann91) MRay/s for nearest hit and \~36 vs \~23.5 MRay/s for any hit. The harness tilts some comparisons: TinyBVH traces an SBVH BVH4 optimized for 100 iterations while Embree's build quality for the chart is not stated; Embree's timing loop resets tfar to 1e30 instead of each ray's tmax (this matters for the AO ray set, whose tmax is 5% of scene size); madmann91 creates a new thread pool inside every timed build. An earlier README, still in the wjakob fork, said Embree beat TinyBVH on any-hit rays.

## Use it when

- CPU ray casting against static or rigidly instanced triangle meshes (visibility, AO, baking, picking, path tracing) when you want one dependency-free header instead of linking Embree and TBB.
- Frequent rebuilds of meshes in the 100k-1M triangle range: the author measures a \~6.7 ms SAH build for the 263k-triangle Sponza. Refit is the cheaper option for small deformations with a fixed triangle count.
- Building BVHs on the CPU for your own GPU traversal (CWBVH, Aila-Laine BVH_GPU, BVH4_GPU) in OpenCL, compute shaders or WebGPU without vendor ray-tracing APIs.
- Targets where shipping one header is simpler than shipping Embree: WASM/Emscripten (SIMD128), Android/Apple NEON, plus double-precision BVHs (BVH_Double, BVH4_Double).

## Skip it when

- Spatial queries this category's baselines serve: point k-NN, box range queries, polygon predicates and GIS geometry. TinyBVH answers ray and sphere-overlap queries over triangles and AABBs only.
- Workloads that need Embree's wider primitive set (curves/hair, subdivision surfaces, motion blur), none of which is in TinyBVH's feature list.
- Code that must not be terminated by a library: fatal errors (NaN in a ray, empty mesh, rebuilding a non-rebuildable BVH) call exit(1) unless you install a handler that throws.
- x86 builds without -mavx2 -mfma, and 32-bit x86, RISC-V or PowerPC: the SIMD builder and the BVH4_CPU/BVH8_CPU kernels compile out, leaving scalar code.
- Projects that need a frozen API: in September 2026 alone the header was split into several files and ray directions stopped being normalized, and correctness issues remain open (#301, #291).

## How it is fast

The default build is a binned SAH builder (8 bins) with AVX or NEON bin evaluation, run on a process-wide std::thread pool for meshes of 50k+ triangles. The fastest CPU layout, BVH4_CPU, follows the WiVe design (Fuetterling et al., HPG 2017): 128-byte 4-wide nodes with child bounds in SoA form and a precomputed per-octant child order, kernels templated on the ray-direction signs, FMA slab tests, and leaves of 4 triangles tested together with SIMD. Optional quality passes are SBVH spatial splits (Stich et al. 2009), pre-splitting and tree-rotation optimization (Bittner et al. 2013), which lower SAH cost at the price of build time. There is also a 64-ray bundle (packet) traversal path (WiVeC) for coherent rays.

## Compared with alternatives

Pick TinyBVH when the query is ray-triangle intersection (nearest or any hit) over large meshes, on the CPU or GPU. The catalogued siblings answer other questions: nanoflann, tidwall/rtree.c, THST and GeoToolbox for point k-NN and box range queries, TG for 2D polygon predicates, and Manifold, MeshLib or trueform for mesh booleans and mesh processing.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (tiny_ocl.h and OpenCL are needed only for the GPU examples) |
| **Minimum toolchain** | C++17 by default (threaded builds); C++14 with NO_THREADED_BUILDS; the repo's CMake and build.bat use C++20. GCC, clang, MSVC and Emscripten are supported. |
| **Platforms** | x86-64 (SSE4.2/AVX/AVX2+FMA kernels, scalar fallback without them), aarch64 NEON, WASM SIMD128; scalar code on any other C++17 target |
| **Thread safety** | Intersect and IsOccluded are const, and the author's benchmark traces one BVH from many threads. Builds use a process-wide std::thread pool, or your own spawn/barrier/parallel_for hooks in BVHContext. Concurrent builds are not documented; VoxelSet::Set is marked 'not thread-safe'. |
| **Drop-in for the baseline** | no |

## Gotchas

- Every BVH::Intersect call runs VALIDATE_RAY, so one NaN in a ray's origin, direction or t ends the process with exit(1). Call tinybvh_set_fatal_error_handler with a handler that throws if you need to recover.
- On x86, compiling without -mavx2 -mfma only prints a warning and defines TINYBVH_NO_SIMD, so the program silently falls back to scalar code. The fast layouts need AVX2+FMA; CMake passes -march=native and build.bat passes -mavx2 -mfma.
- Since PR #296 (merged 2026-09-23), ray directions are used as given, so hit.t scales with |D|; define NORMALIZE_RAY_DIR for the old behaviour. Input vertices are float4, with w as padding that is sometimes reused (for example for triangle color).
- BVH_GPU::ConvertFrom ignores vertex indices (issue #301, open; still at tiny_bvh_base.h line 4650 at HEAD), so indexed meshes give wrong GPU geometry in that layout. Traversal kernels use fixed stacks (TINYBVH_STACK_SIZE 128, doubled for wide layouts) with no bounds check in the hot loop, and a stack overflow on the San Miguel scene in BVH4_CPU conversion was reported (#300).

## Known shortcomings

- Author calls results 'preliminary'; numbers read off a chart; only single-ray traversal compared, not Embree's packet/stream paths; Embree is not a listed category baseline; no CPU, compiler or flags.
- Benchmark tilts against rivals: Embree's timing loop resets tfar to 1e30 instead of each ray's tmax (matters for the AO set, tmax = 5% of scene size); madmann91 builds create a new thread pool inside every timed build; TinyBVH traces an SBVH BVH4 optimized for 100 iterations while Embree's build quality is not stated.
- An earlier README (still in the wjakob fork) said Embree beat TinyBVH on any-hit rays; the current chart shows TinyBVH \~36 vs Embree \~23.5 MRay/s. Flags are public in build.bat (g++ -std=c++20 -mavx2 -mfma -Ofast) but the harness is Windows-only and names no CPU, so it stays C.
- Correctness bug: BVH_GPU::ConvertFrom ignores vertex indices (issue #301, open, still at HEAD), so indexed meshes get wrong GPU geometry.
- Robustness: a NaN ray or any fatal error calls exit(1); traversal stacks are fixed-size with no bounds check (stack overflow on San Miguel reported in #300).
- Possibly the wrong category: ray-tracing acceleration structure, not a Boost.Geometry/CGAL/GEOS workload.

## Caveats and trade-offs

Author labels results 'preliminary' and notes single-ray traversal is only a small part of Embree (Embree's packet/stream paths not compared). Chart numbers are bar readings; no CPU model, compiler or flags given. Baseline Embree is a ray-tracing incumbent, not one of the category's listed baselines (Boost.Geometry/CGAL/GEOS).

Header-only, no dependencies; AVX2/NEON wide BVH kernels; single-ray traversal only, a small part of Embree.

## Maintenance

Very active (v1.9.0, last commit 2026-09-25, 1,753 commits, 34 contributors, 1.2k stars), MIT-licensed and used in Remedy Northlight, SideFX Houdini and EA SEED Gigi; it is easy to vendor, but pin a commit because layouts and semantics still change.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification D, tier now C.
- **Tier reason:** README chart (images/perfgraphs.png) gives first-party numbers against Embree and madmann91/bvh, produced by the public tiny_bvh_benchmark.cpp, which builds both baselines; no CPU model, compiler or flags are stated for the CPU chart, so it is C, not A. Upgraded from D because the chart does carry numeric axes.
- **Verifier notes:** Benchmark code: tiny_bvh_benchmark.cpp (Experiment entries for EMBREE and MADMANN91). Widely used (Remedy Northlight, Houdini). Metadata confirmed: MIT, 1.2k stars, last commit 2026-09-25, not archived/fork. Shortcoming to record: off-category baseline, no hardware/flags.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/jbikker/tinybvh>
  - <https://github.com/jbikker/tinybvh/commits>
  - <https://raw.githubusercontent.com/jbikker/tinybvh/HEAD/README.md>
  - <https://raw.githubusercontent.com/jbikker/tinybvh/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/jbikker/tinybvh/HEAD/images/perfgraphs.png>
  - <https://raw.githubusercontent.com/jbikker/tinybvh/HEAD/tiny_bvh_benchmark.cpp>
- **Sources the enricher read:**
  - <https://github.com/jbikker/tinybvh>
  - <https://github.com/jbikker/tinybvh/commits>
  - <https://github.com/jbikker/tinybvh/issues?q=is%3Aissue>
  - <https://github.com/jbikker/tinybvh/issues/299>
  - <https://github.com/jbikker/tinybvh/issues/300>
  - <https://github.com/jbikker/tinybvh/issues/301>
  - <https://github.com/jbikker/tinybvh/pull/294>
  - <https://github.com/jbikker/tinybvh/pull/296>
  - <https://github.com/wjakob/tinybvh>
  - <https://raw.githubusercontent.com/jbikker/tinybvh/HEAD/README.md>
  - <https://raw.githubusercontent.com/jbikker/tinybvh/HEAD/tiny_bvh.h>
  - <https://raw.githubusercontent.com/jbikker/tinybvh/HEAD/tiny_bvh_base.h>
  - <https://raw.githubusercontent.com/jbikker/tinybvh/HEAD/tiny_bvh_x86_float.h>
  - <https://raw.githubusercontent.com/jbikker/tinybvh/HEAD/tiny_bvh_benchmark.cpp>
  - <https://raw.githubusercontent.com/jbikker/tinybvh/HEAD/images/perfgraphs.png>
  - <https://raw.githubusercontent.com/jbikker/tinybvh/HEAD/images/cpu_vs_gpu.png>
  - <https://raw.githubusercontent.com/jbikker/tinybvh/HEAD/build.bat>
  - <https://raw.githubusercontent.com/jbikker/tinybvh/HEAD/build_debug.bat>
  - <https://raw.githubusercontent.com/jbikker/tinybvh/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/jbikker/tinybvh/HEAD/benchmark/acc_struc.cpp>
  - <https://raw.githubusercontent.com/jbikker/tinybvh/HEAD/benchmark/experiment.cpp>
  - <https://raw.githubusercontent.com/jbikker/tinybvh/HEAD/benchmark/experiment.h>
  - <https://raw.githubusercontent.com/jbikker/tinybvh/HEAD/benchmark/headers.h>
  - <https://raw.githubusercontent.com/jbikker/tinybvh/HEAD/benchmark/tools.cpp>
  - <https://raw.githubusercontent.com/jbikker/tinybvh/HEAD/benchmark/tiny_bvh.cpp>
  - <https://raw.githubusercontent.com/jbikker/tinybvh/HEAD/benchmark/ray_distribution.cpp>
  - <https://raw.githubusercontent.com/jbikker/tinybvh/HEAD/benchmark/ray_distribution.h>
  - <https://raw.githubusercontent.com/jbikker/tinybvh/HEAD/benchmark/primitive_set.cpp>
  - <https://raw.githubusercontent.com/madmann91/bvh/HEAD/src/bvh/v2/thread_pool.h>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/jbikker/tinybvh`) · [data/wave8/enrich/raw/github_com_jbikker_tinybvh.json](../../../data/wave8/enrich/raw/github_com_jbikker_tinybvh.json) (enrichment confidence 0.75)

</details>
