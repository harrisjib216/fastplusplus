# Manifold

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Apache-2.0 C++ mesh-boolean kernel with guaranteed manifold output; 2.5-6.9x faster than CGAL corefinement on 1.3M-triangle spheres.

| | |
|---|---|
| **Beats** | CGAL Nef/PMP mesh booleans (and OpenSCAD's CGAL backend) |
| **Claimed result** | Third-party axiolid benchmark, two icospheres of 1,310,720 triangles each: A-B Manifold 2,816.2 ms vs CGAL 13,368.2 ms (4.7x); union 3,462.5 vs 23,922.9 ms (6.9x); intersection 2,248.7 vs 5,602.2 ms (2.5x) (ratios derived from page data). Smaller subdivisions show 2.6-5.6x. On a Menger sponge only Manifold completed past depth 1 (CGAL corefinement failed). Author's blog: single-thread 'an order of magnitude faster' than OpenSCAD fast-csg, GPU '100-1,000 times faster than the current OpenSCAD release'. |
| **Workload** | Mesh booleans (union, intersection, A-B) of two overlapping icospheres from 5,120 to 1,310,720 triangles per operand, plus Menger-sponge and wall-with-openings cases (axiolid cross-kernel benchmark); author's blog: sphere differences and Menger sponge vs OpenSCAD+CGAL. |
| **Metric** | latency |
| **Hardware** | 20-core host (model not stated) |
| **Compiler and flags** | default Release flags (compiler not stated) |
| **Adoption** | 2.2k stars; used by OpenSCAD and others |
| **Last commit** | 2026-09-30 |
| **Links** | [repository](https://github.com/elalish/manifold) · [benchmark](https://github.com/axiolid/benchmarks) |

## Verdict

The third-party axiolid/benchmarks harness (a Rust driver over a C++ shim) times Manifold v3.5.1 against CGAL Polygon_mesh_processing corefine_and_compute_\* with the Exact_predicates_exact_constructions_kernel on two overlapping icospheres. At 1,310,720 triangles per operand: union 3,462.5 vs 23,922.9 ms, intersection 2,248.7 vs 5,602.2 ms, A-B 2,816.2 vs 13,368.2 ms (2.5-6.9x, derived from page data); results are checked by the volume identity |A u B| + |A n B| = |A| + |B|. The timed call includes building each library's mesh and computing the volume, on a '20-core host' with the compiler unstated and best of 1 rep. Manifold was built with default CMake flags, which leave MANIFOLD_PAR off, so it most likely ran single-threaded.

## Use it when

- Booleans on closed triangle meshes of 10^3 to a few 10^6 triangles where exact-kernel CGAL corefinement takes seconds: a 1.31M-triangle sphere pair union took 3.46 s vs 23.9 s for CGAL in the axiolid harness
- Many chained or many-cutter booleans (Menger sponges, walls with thousands of openings): in axiolid's Menger test CGAL corefinement failed past depth 1, while Manifold finished depth 4 (58,947 cutters) in 25.8 s
- Code-CAD, 3D-printing, game-engine or web tools that need watertight output, a permissive Apache-2.0 licence and Python/JS/WASM bindings
- Pipelines that must carry UVs, normals, colours or material IDs through booleans

## Skip it when

- Results that need exact rational coordinates or proven geometric validity: only manifold topology is guaranteed, and the wiki calls geometric validity a goal without a formal proof. CGAL with an exact kernel stays the reference.
- Non-manifold, open or self-overlapping input such as raw scans or STL soups: construction returns NotManifold, and the wiki says self-overlaps within one mesh cannot be removed yet. Repair the input first, or use MeshLib's voxel mode.
- Current master on coincident surfaces with different triangulations: open issue #1857 reports a 584-triangle union going from 0.01 s to 17 s after PR #1790 (RecursiveEdgeSwap churn in RemoveDegenerates). Pin a release and benchmark your own models.
- Maximum boolean speed on large scans when the licence allows it: in MeshLib's own benchmark Manifold was about 3x slower than MeshLib on a 2M-triangle union
- Curved B-rep/NURBS CAD: the boolean works only on flat triangles, so OpenCascade remains the tool for B-rep

## How it is fast

It follows Julian Smith's dissertation: double-precision geometry with symbolic perturbation (the 'shadow' tests in boolean3.cpp) breaks exact ties, so each topological question is answered once and reused. The output is manifold by construction without the exact-constructions arithmetic that CGAL's robust path pays for. A BVH broad phase (a collider over Morton-sorted face boxes) cuts Smith's O(n^2) triangle-pair test to O(n log n). Boolean operators build a lazy CSG tree that is flattened into batched booleans when the result is requested. With MANIFOLD_PAR=ON the kernels run on TBB parallel for/scan/merge-sort above a 10^4-element threshold and fall back to serial code below it.

## Compared with alternatives

Pick Manifold over MeshLib (faster in its vendor's benchmark, but under a non-commercial licence) when you need a permissive, embeddable boolean kernel with guaranteed manifold output and broad language bindings. Pick MeshLib for messy scans if its licence fits, and look at trueform for its wider CGAL-beating mesh ops. HXT, gDel3D and the spatial indexes (nanoflann, rtree.c, KdBoxTree, THST, TG) solve different problems.

## Integration

| | |
|---|---|
| **Form** | static lib \| shared lib |
| **Dependencies** | none required; optional oneTBB (MANIFOLD_PAR=ON) for parallelism, nanobind (Python), Emscripten (WASM), GTest, Assimp, Tracy. Also packaged via vcpkg, PyPI manifold3d and npm manifold-3d. |
| **Minimum toolchain** | C++17, CMake 3.18+; tested with GCC, LLVM/Clang and MSVC |
| **Platforms** | Linux, macOS, Windows (static build recommended; issue #1859 says the Windows ARM64 package is missing in 3.5.4), WebAssembly (serial only; MANIFOLD_PAR under Emscripten is not recommended because of possible memory corruption) |
| **Thread safety** | Manifold objects behave as immutable values: header comments describe const methods being used concurrently from other threads, with lazy CSG evaluation guarded by a per-node mutex. Internal parallelism comes from TBB only when built with MANIFOLD_PAR=ON. |
| **Drop-in for the baseline** | no |

## Gotchas

- MANIFOLD_PAR defaults to OFF, so a plain CMake build is single-threaded; turn on TBB yourself, and avoid MANIFOLD_USE_BUILTIN_TBB next to another TBB copy (the README warns it 'may cause performance issues or crash')
- Booleans are lazy and report errors through Status() (NotManifold, NonFiniteVertex, ResultTooLarge, Cancelled and others), not through exceptions unless MANIFOLD_DEBUG is set, so the cost and any failure surface at GetMeshGL()/Volume()/Status()
- Open issue #1870 (3.5.4, Windows): constructing from small non-manifold MeshGL64 input crashes intermittently with an access violation (0xC0000005), suspected to be an uninitialised or out-of-bounds read during validation. Treat untrusted meshes with care.
- Exporting to STL loses manifoldness on re-import; the README recommends 3MF or glTF with EXT_mesh_manifold. Issue #1706 also reports sliver triangles from booleans on near-coincident inputs.

## Known shortcomings

- Evidence from a competitor's 0-star unlicensed repo (axiolid); CPU and compiler not stated; single run; parallel Manifold vs serial CGAL.
- Benchmark setup: MANIFOLD_PAR defaults OFF and the axiolid comparison was built with default flags, so Manifold most likely ran serial (the 'TBB-parallel vs serial CGAL' caveat looks wrong); CGAL side used EPECK and the timed call includes mesh build + Volume. CUDA backend removed, TBB only.
- Open bugs: #1870 intermittent access violation 0xC0000005 constructing from a small non-manifold MeshGL64 (3.5.4, Windows; possible out-of-bounds/uninitialized read, memory safety); #1857 boolean regression on master since PR #1790 (584-triangle union 0.01 s to 17 s); #1706 sliver triangles.

## Caveats and trade-offs

Evidence is from a 0-star repo of a competing kernel (axiolid, no LICENSE file), with CPU model and compiler unstated and best of 1 rep; Manifold's own README gives no numbers. Manifold was built with TBB parallelism on a 20-core host versus serial CGAL. Blog baseline is OpenSCAD (CGAL-based), not CGAL directly. Axiolid's own analytic box path beats Manifold on axis-aligned Menger cases, which is not a general boolean. [retier] MANIFOLD_PAR defaults OFF and the axiolid comparison used default flags, so Manifold most likely ran serial (not TBB-parallel); CGAL side used EPECK and its timed call includes mesh build + Volume. CUDA backend removed; TBB only.

Guarantees manifold output; TBB parallel (optionally CUDA); uses robust floating point rather than exact arithmetic.

## Maintenance

Very active (about 2.3k stars, 3.5.x releases, used by OpenSCAD and Blender) and copyable under Apache-2.0. The CUDA/GPU backend cited in older material is gone; TBB is now the only parallel backend.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Independent third-party harness (axiolid/benchmarks, Rust + cpp/shim.cpp, public) times Manifold v3.5.1 against CGAL PMP corefinement with correctness oracles; sphere A-B at 1.31M tris/operand: manifold 2816.2 ms vs cgal 13368.2 ms. CPU model and compiler are not stated ('20-core host', default Release flags), so not A.
- **Verifier notes:** Numbers verified in axiolid/benchmarks README (Sphere-sphere section). Metadata matches: Apache-2.0, 2.2k stars, last commit 2026-09-30. Blog numbers not re-opened.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/axiolid/benchmarks>
  - <https://raw.githubusercontent.com/axiolid/benchmarks/HEAD/README.md>
  - <https://github.com/elalish/manifold>
  - <https://raw.githubusercontent.com/elalish/manifold/HEAD/README.md>
  - <https://github.com/elalish/manifold/commits>
- **Sources the enricher read:**
  - <https://github.com/elalish/manifold>
  - <https://raw.githubusercontent.com/elalish/manifold/HEAD/README.md>
  - <https://raw.githubusercontent.com/elalish/manifold/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/elalish/manifold/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/elalish/manifold/HEAD/include/manifold/manifold.h>
  - <https://raw.githubusercontent.com/elalish/manifold/HEAD/include/manifold/common.h>
  - <https://raw.githubusercontent.com/elalish/manifold/HEAD/src/parallel.h>
  - <https://raw.githubusercontent.com/elalish/manifold/HEAD/src/impl.h>
  - <https://raw.githubusercontent.com/elalish/manifold/HEAD/src/boolean3.cpp>
  - <https://raw.githubusercontent.com/elalish/manifold/HEAD/src/boolean_result.cpp>
  - <https://github.com/elalish/manifold/wiki/Manifold-Library>
  - <https://github.com/elalish/manifold/issues?q=is%3Aissue+is%3Aopen>
  - <https://github.com/elalish/manifold/issues?q=is%3Aissue+is%3Aopen+label%3Abug>
  - <https://github.com/elalish/manifold/issues/1857>
  - <https://github.com/elalish/manifold/issues/1870>
  - <https://github.com/elalish/manifold/releases>
  - <https://raw.githubusercontent.com/axiolid/benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/axiolid/benchmarks/HEAD/cpp/shim.cpp>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/elalish/manifold`) · [data/wave8/enrich/raw/github_com_elalish_manifold.json](../../../data/wave8/enrich/raw/github_com_elalish_manifold.json) (enrichment confidence 0.75)

</details>
