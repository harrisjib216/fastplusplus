# madmann91/bvh

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only C++20 binary BVH builder and ray traverser; its chart shows it faster than nanort and Fast-BVH, but slower than Embree.

| | |
|---|---|
| **Beats** | nanort and Fast-BVH (Embree 3.13 also compared and is faster) |
| **Claimed result** | Values read off the README chart (approximate): BVH v2 (medium) builds in about 150 ms and renders in about 275 ms vs nanort about 360 ms build / 645 ms render and Fast-BVH about 460 ms build / 1225 ms render (about 2.3x and 4.5x faster render, derived from page data); Embree 3.13 is faster than all BVH presets (about 70 ms build, 170 ms render). |
| **Workload** | BVH build time and primary-ray render time (1 spp at 720p) on one unnamed .obj scene, comparing BVH v2 presets (low/medium/high) and BVH v1 builders with Embree 3.13, nanort (2022-08-01, 28bebb8f) and Fast-BVH (2020-03-30, e5366678). The chart does not name the scene (the README's Blend Swap credit is for the example render image). |
| **Metric** | build-time |
| **Adoption** | 1.2k stars |
| **Last commit** | 2026-09-21 |
| **Links** | [repository](https://github.com/madmann91/bvh) · [benchmark](https://github.com/madmann91/bvh) |

## Verdict

One README chart (chart.png) compares build time and 1-spp 720p primary-ray render time on one unnamed .obj scene. Readings, approximate: v2 medium about 150 ms build and 275 ms render; nanort about 360 and 645; Fast-BVH about 460 and 1225; Embree 3.13 about 70 and 170. That makes v2 roughly 2.3x faster than nanort and 4.5x faster than Fast-BVH at rendering (derived from page data), but slower than Embree. No CPU, compiler, flags, thread count or scene is given. test/benchmark.cpp times only this library: it builds with a thread pool sized to hardware_concurrency and renders single-threaded. The harness used for Embree, nanort and Fast-BVH is not in the repo.

## Use it when

- CPU ray tracers, path tracers or visibility queries that need a small dependency-free BVH (standard library only), and where Embree's size or license model is unwanted.
- Replacing nanort or Fast-BVH: the README chart shows faster build and roughly 2-4x faster primary-ray render than both.
- Choosing your own trade-off between build time and traversal quality per scene (Low, Medium, High), for example a quick rebuild for animated geometry and High for static scenes.
- Non-ray queries on a BVH (box overlap, custom culling, 2D or 4D bounding boxes, float or double), using traverse_top_down with your own inner-node and leaf callbacks.
- C projects that only need the high-level build and intersect functions, through the optional C API (BVH_BUILD_C_API).

## Skip it when

- Peak performance: Embree 3.13 beats every preset on the README chart (about 70 ms build and 170 ms render, against about 150 ms and 275 ms for v2 medium), and TinyBVH reports beating both.
- Packet or wide-BVH (BVH4 or BVH8) SIMD traversal and GPU traversal: the nodes are binary and the traversal is single-ray (the GPU question is issue #92).
- Toolchains without C++20 (it uses std::span and defaulted comparison operators) or with CMake older than 3.21.
- Packaging that needs versioned releases: there is no tagged v2 release, and issue #116 asks for one for Debian.
- Frequent incremental insert or remove: there is refit but no dynamic insertion, so topology changes mean a rebuild (asked in issues #94 and #85).

## How it is fast

Low quality uses Wald's binned SAH builder. Medium and High use a full sweep SAH builder single-threaded, or, with a thread pool and at least 1,024 primitives, Ganestam et al.'s mini-tree builder with pruning. High then runs Meister and Bittner's parallel reinsertion optimizer to raise tree quality. Nodes are compact binary nodes with siblings stored next to each other and one packed index (first child or primitive plus primitive count). Traversal visits the nearer child first and orders box tests by ray octant, uses FMA-based slab tests (Ize's robust variant is optional) and a fixed-size stack; shadow rays can use SATO ordering.

## Compared with alternatives

TinyBVH is the closer competitor and claims to beat both Embree and this library on build time, so prefer it for top speed or wide BVHs. Pick madmann91/bvh for a clean, modern-C++ API with multiple builders, arbitrary dimensions and scalar types, serialization and a C API. ArborX and Coal are for spatial queries and collision on a different scale.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none beyond the C++ standard library (Threads::Threads linked for the std::thread-based pool); optional C API library |
| **Minimum toolchain** | C++20 (CMake target sets CXX_STANDARD 20), CMake 3.21+ |
| **Platforms** | any (portable C++; GCC, Clang and MSVC force-inline macros in platform.h) |
| **Thread safety** | Not documented. A built Bvh is plain std::vector data and intersect() is const with a caller-owned stack, so concurrent read-only traversal with one stack per thread looks safe from the source. Builders take a ThreadPool that defaults to std::thread::hardware_concurrency() threads. |
| **Drop-in for the baseline** | no |

## Gotchas

- SmallStack&lt;Index, N&gt; (the benchmark uses N = 64) checks overflow only with assert(), so a BVH deeper than N overflows silently in release builds. Issue #108 (December 2025) asks what depth is safe and has no visible answer; use GrowingStack or size the stack to the tree depth.
- Leaves hold ranges into bvh.prim_ids, not your primitive order. Either index through prim_ids or permute your primitives after building, which the benchmark's --permute_prims option does.
- The README is out of date in places: it says -DENABLE_TESTING=ON and -DBVH_STATIC_LINK_STDLIB_C_API=ON, but CMakeLists uses CTest's BUILD_TESTING and BVH_C_API_STATIC_LINK_STDLIB, and the snippet's target_link_library should be target_link_libraries.
- Past bugs fixed upstream: ReinsertionOptimizer could loop forever (#84), extract_bvh could use a stale pointer (#81), and a span went out of range below 3 dimensions (#106). Pin a commit that includes these fixes.

## Known shortcomings

- Embree 3.13 beats it on build and render; competitor harness not in the repo; scene unnamed.
- Embree is faster and TinyBVH claims to beat both. SmallStack overflow is checked only by assert, so it overflows silently in release (#108 open, unanswered). README CMake flag names differ from CMakeLists. Chart gives no thread count; the repo benchmark uses hardware_concurrency threads.

## Caveats and trade-offs

Numbers are only in a chart image (chart.png): no CPU, compiler, flags, thread count or scene named. test/benchmark.cpp benchmarks only this library; the harness used for Embree, nanort and Fast-BVH is not in the repo. Competitor versions on the chart date it to 2022 or later. It beats the simple header-only libraries (nanort, Fast-BVH) but not the real incumbent Embree, which is faster on both build and render. Ray-tracing BVH is only loosely within geometry-spatial; none of this category's named baselines (Boost.Geometry, CGAL, GEOS, R-trees) is compared.

Header-only C++20 BVH construction and traversal, multiple builders (sweep SAH, binned SAH, multithreaded), C API, serialization; does not reach Embree's speed.

## Maintenance

Actively maintained (last commit 2026-09-21, 1.2k stars, 438 commits) and MIT-licensed. It is header-only and easy to vendor, but has no tagged v2 release, so pin a commit.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** README Performance section is a single chart (chart.png) of build and 1spp@720p render times vs Embree 3.13, nanort and Fast-BVH; the record's approximate readings match the chart, but no CPU, compiler, flags, thread count or scene is stated and the competitor harness is not in the repo, so first-party C.
- **Verifier notes:** Chart readings checked: v2 medium about 150 ms build / 275 ms render, nanort about 360/645, Fast-BVH about 460/1225, Embree 3.13 about 70/170. Metadata checked on github.com: 1.2k stars, MIT (LICENSE.txt), not a fork, last commit 2026-09-21.
- **Fields the verifier corrected:** `workload`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://github.com/madmann91/bvh>
  - <https://github.com/madmann91/bvh/commits>
  - <https://raw.githubusercontent.com/madmann91/bvh/HEAD/README.md>
  - <https://raw.githubusercontent.com/madmann91/bvh/HEAD/chart.png>
  - <https://raw.githubusercontent.com/madmann91/bvh/HEAD/LICENSE.txt>
  - <https://raw.githubusercontent.com/madmann91/bvh/HEAD/test/benchmark.cpp>
- **Sources the enricher read:**
  - <https://github.com/madmann91/bvh>
  - <https://raw.githubusercontent.com/madmann91/bvh/HEAD/README.md>
  - <https://raw.githubusercontent.com/madmann91/bvh/HEAD/CMakeLists.txt>
  - <https://github.com/madmann91/bvh/tree/master/src/bvh/v2>
  - <https://raw.githubusercontent.com/madmann91/bvh/HEAD/src/bvh/v2/CMakeLists.txt>
  - <https://raw.githubusercontent.com/madmann91/bvh/HEAD/src/bvh/v2/default_builder.h>
  - <https://raw.githubusercontent.com/madmann91/bvh/HEAD/src/bvh/v2/bvh.h>
  - <https://raw.githubusercontent.com/madmann91/bvh/HEAD/src/bvh/v2/node.h>
  - <https://raw.githubusercontent.com/madmann91/bvh/HEAD/src/bvh/v2/index.h>
  - <https://raw.githubusercontent.com/madmann91/bvh/HEAD/src/bvh/v2/stack.h>
  - <https://raw.githubusercontent.com/madmann91/bvh/HEAD/src/bvh/v2/mini_tree_builder.h>
  - <https://raw.githubusercontent.com/madmann91/bvh/HEAD/src/bvh/v2/thread_pool.h>
  - <https://raw.githubusercontent.com/madmann91/bvh/HEAD/src/bvh/v2/platform.h>
  - <https://raw.githubusercontent.com/madmann91/bvh/HEAD/src/bvh/v2/executor.h>
  - <https://raw.githubusercontent.com/madmann91/bvh/HEAD/src/bvh/v2/reinsertion_optimizer.h>
  - <https://raw.githubusercontent.com/madmann91/bvh/HEAD/test/benchmark.cpp>
  - <https://raw.githubusercontent.com/madmann91/bvh/HEAD/test/simple_example.cpp>
  - <https://github.com/madmann91/bvh/issues?q=is%3Aissue>
  - <https://github.com/madmann91/bvh/issues/108>
  - <https://github.com/madmann91/bvh/issues/116>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/madmann91/bvh`) · [data/wave8/enrich/raw/github_com_madmann91_bvh.json](../../../data/wave8/enrich/raw/github_com_madmann91_bvh.json) (enrichment confidence 0.8)

</details>
