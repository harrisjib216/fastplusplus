# kigumi

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only, exact, multithreaded mesh Booleans for open, closed and non-manifold meshes; beats CGAL corefinement.

| | |
|---|---|
| **Beats** | CGAL Polygon_mesh_processing corefinement ('coref.'); also libigl igl::copyleft::cgal::mesh_boolean (CGAL exact), geogram, Manifold, MCUT |
| **Claimed result** | README table (seconds): Closed: CGAL coref. 27.2 vs kigumi 4.6 sequential (about 5.9x, derived) and 1.1 parallel; libigl (CGAL exact) 39.3. Open: coref. 3.2 vs kigumi 2.4 sequential (about 1.3x, derived) and 0.6 parallel. Open and closed, and non-manifold: CGAL coref. FAILED, kigumi 1.0/0.4 and 0.5/0.1 s. Manifold is faster on closed meshes (1.3 s sequential, 0.2 s parallel) but approximate. |
| **Workload** | Boolean intersection of two triangle meshes, excluding I/O, on four generated mesh pairs (open, open and closed, closed, non-manifold); wall-clock seconds. |
| **Metric** | latency |
| **Hardware** | MacBook Pro 14-inch (M4, 2024), 16-core CPU |
| **Compiler and flags** | Homebrew Clang 22.1.1; CMake Release via ./run configure (-DCMAKE_BUILD_TYPE=Release, so CMake's default -O3 -DNDEBUG; benches/\*/CMakeLists.txt add only warning flags); benches need -DKIGUMI_BUILD_BENCHES=ON; CGAL and the other dependencies are pinned by the vcpkg submodule (b42535f) |
| **Adoption** | 54 stars |
| **Last commit** | 2026-08-31 |
| **Links** | [repository](https://github.com/unageek/kigumi) · [benchmark](https://github.com/unageek/kigumi) |

## Verdict

Intersection of two generated mesh pairs on a 16-core MacBook Pro 14-inch M4 (2024, M4 Max-class), built with Homebrew Clang 22.1.1 in CMake Release, excluding I/O. kigumi took 4.6 s single-threaded and 1.1 s parallel on the closed case vs 27.2 s for CGAL PMP corefinement with EPECK and 39.3 s for libigl's CGAL-exact mesh_boolean. On the open case it took 2.4 s vs 3.2 s. These are first-party numbers from a single machine.

## Use it when

- You need exact (EPECK) Booleans and CGAL's corefinement is too slow: closed case 27.2 s (CGAL) vs 4.6 s sequential and 1.1 s parallel in the author's run.
- Inputs are open surfaces (terrain, water surface) or non-manifold meshes, where CGAL corefinement, libigl, Manifold and MCUT all FAILED in the README table and kigumi finished in 0.1-2.4 s.
- You want many Boolean results from the same pair: the builder does the expensive mixing once and each operator call only extracts faces.
- Per-face attributes (material IDs, labels) must survive the operation.
- Multi-core desktops or servers: the code scales by thread count (KIGUMI_NUM_THREADS or a Threading_context).

## Skip it when

- Closed, manifold meshes where approximate results are acceptable: Manifold was faster (1.3 s sequential, 0.2 s parallel vs 4.6 s and 1.1 s) in the same table.
- Inputs with degenerate faces or self-intersections: the README says the result is undefined and may crash or produce broken meshes; Corefine throws 'mesh has self-intersections'.
- Proprietary binaries without a CGAL commercial licence: it needs CGAL's 2D Triangulations package (GPL or commercial) as well as the LGPL kernel, so the MIT label does not make the whole stack permissive.
- Projects that cannot take C++20 plus Boost, CGAL and fast_float as dependencies.
- You need a mature, widely deployed engine: 54 stars, version 0.1.0 in vcpkg.json, one maintainer; issue #33 reports a wrong union fixed by nudging the meshes, and issue #28 reports a 273 s run with no visible resolution.

## How it is fast

It implements an optimized version of Barki, Guennebaud and Foufou (2015), 'Exact, robust, and efficient regularized Booleans on general 3D meshes'. An AABB tree finds candidate face pairs. Intersections are found symbolically (which triangle features cross) before any exact point is built, intersected faces are re-triangulated with a CGAL constrained Delaunay triangulation, and faces are classified locally and then by propagating tags across connected components, so only one exact point-in-soup test is needed per component. Every stage (pair finding, symbolic intersection, exact-point evaluation, triangulation, global classification) runs on std::threads that pull work items from a shared atomic index; the README shows 4.6 s sequential vs 1.1 s parallel on the closed case.

## Compared with alternatives

Pick kigumi over Manifold, MeshLib or trueform when you need exact results or have open or non-manifold inputs. Manifold is several times faster on closed manifold meshes but approximate and fails on the other cases. Hob3l is narrower: it targets OpenSCAD CSG export.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | CGAL (2D and 3D Linear Geometry Kernel, 2D Triangulations), Boost (container, container_hash, endian, iterator, range, unordered), fast_float; the repo pins all of them through a vcpkg submodule |
| **Minimum toolchain** | C++20 (CMAKE_CXX_STANDARD 20, designated initializers); CMake 3.18+; build docs exist for Windows, macOS (Xcode 16 plus Homebrew LLVM) and Ubuntu |
| **Platforms** | any platform CGAL and Boost support; documented builds for Windows, macOS and Ubuntu |
| **Thread safety** | Internally multithreaded with std::thread. The thread count lives in a thread_local Threading_context (default hardware_concurrency); concurrent calls from user threads are not documented. |
| **Drop-in for the baseline** | partial — uses CGAL kernels and exact arithmetic like PMP corefinement, but takes kigumi Region/Triangle_soup inputs rather than CGAL Surface_mesh, and the operator set and region semantics differ. |

## Gotchas

- Corefine.h prints progress lines ('Finding face pairs...', 'Triangulating...') to std::cout unconditionally, so a library user gets stdout noise.
- Open meshes must be clipped by a common convex region; otherwise you get the FIRST/SECOND_MESH_PARTIALLY_INTERSECTS warning and results can be wrong (see issue #33). Check builder.warnings().
- Inconsistently oriented inputs make the builder throw std::runtime_error, and faces with more than three vertices are read as triangle fans.
- The README table predates the 2026-07-20 Autorefinement change, and it gives no mesh sizes or CGAL version; the input meshes are generated by tools/gen_bench_meshes.sh.

## Known shortcomings

- MIT code but needs LGPL/GPL CGAL (GPL obligation applies); benchmark table predates the Jul 2026 autorefinement change.
- Needs C++20 plus Boost, CGAL and fast_float, so header-only still pulls heavy dependencies; CGAL parts are GPL (licence question #35 closed without reply). Corefine.h prints progress to std::cout unconditionally. Open unanswered issue #33: wrong union with a partial-intersection warning; #28: 273 s run, closed with no visible fix.

## Caveats and trade-offs

The README states neither mesh sizes nor library versions, although the input meshes are in meshes/ and the CGAL and libigl versions are pinned by the vcpkg submodule. The README's build steps do not show the -DKIGUMI_BUILD_BENCHES=ON switch the benchmarks need. The 'Open' sequential gain over CGAL is only 1.3x. Manifold beats kigumi on closed meshes but is approximate, and geogram (5.5 s) is the only other tool that handles the open-and-closed case. A '16-core CPU' in a 14-inch M4 MacBook Pro means the M4 Max, not the base M4. The benchmarks ran on a single machine, and the table predates the 2026-07-20 'Autorefinement' change (the last 'Update benchmarks' commit is from 2026-03-19). kigumi's own code is MIT, but it needs CGAL's kernel (LGPL) and 2D Triangulations (GPL or commercial), so a binary that uses it carries GPL obligations unless CGAL is licensed commercially.

Header-only; needs a CGAL-compatible kernel and 2D triangulation (LGPL and GPL-or-commercial CGAL packages), so using it brings CGAL's license terms. Exact predicates and constructions, open/closed/non-manifold meshes, nested regions, per-face data. Inputs must be free of degenerate faces and self-intersections. Based on Barki et al. 2015 with optimizations.

## Maintenance

Maintained by one author (MIT, 54 stars, last commit 2026-08-31, Autorefinement added 2026-07-20). It is copyable, but any shipped binary carries CGAL's GPL obligations unless CGAL is licensed commercially.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** The README table compares kigumi against CGAL corefinement and states the compiler (Homebrew Clang 22.1.1) and the CPU (MacBook Pro 14-inch M4, 16-core). The benchmark code is public: benches/kigumi/main.cc and benches/corefinement/main.cc both use the EPECK kernel and time only the Boolean call, tools/run_benches.sh and tools/gen_bench_meshes.sh drive them, and the input meshes are in meshes/. The documented ./run configure pins -DCMAKE_BUILD_TYPE=Release, which is the same standard as the ryu and fast_double_parser A precedents.
- **Verifier notes:** All README numbers match. I changed usability from mixed to copyable because every part is under an OSI license (MIT code, with LGPL/GPL CGAL dependencies) and nothing is unlicensed; the GPL obligation is in caveats. MIT, 54 stars, last commit 2026-08-31 and not a fork all confirmed.
- **Fields the verifier corrected:** `usability`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/unageek/kigumi/HEAD/README.md>
  - <https://raw.githubusercontent.com/unageek/kigumi/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/unageek/kigumi/HEAD/tools/run_benches.sh>
  - <https://raw.githubusercontent.com/unageek/kigumi/HEAD/tools/gen_bench_meshes.sh>
  - <https://raw.githubusercontent.com/unageek/kigumi/HEAD/tools/bench_methods.txt>
  - <https://raw.githubusercontent.com/unageek/kigumi/HEAD/run>
  - <https://raw.githubusercontent.com/unageek/kigumi/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/unageek/kigumi/HEAD/benches/CMakeLists.txt>
  - <https://raw.githubusercontent.com/unageek/kigumi/HEAD/benches/corefinement/CMakeLists.txt>
  - <https://raw.githubusercontent.com/unageek/kigumi/HEAD/benches/corefinement/main.cc>
  - <https://raw.githubusercontent.com/unageek/kigumi/HEAD/benches/kigumi/CMakeLists.txt>
  - <https://raw.githubusercontent.com/unageek/kigumi/HEAD/benches/kigumi/main.cc>
  - <https://raw.githubusercontent.com/unageek/kigumi/HEAD/vcpkg.json>
  - <https://raw.githubusercontent.com/unageek/kigumi/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/unageek/kigumi/HEAD/docs/build-macos.md>
  - <https://github.com/unageek/kigumi>
  - <https://github.com/unageek/kigumi/commits>
  - <https://github.com/unageek/kigumi/tree/main/meshes>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/unageek/kigumi/HEAD/README.md>
  - <https://raw.githubusercontent.com/unageek/kigumi/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/unageek/kigumi/HEAD/vcpkg.json>
  - <https://raw.githubusercontent.com/unageek/kigumi/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/unageek/kigumi/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/unageek/kigumi/HEAD/docs/build-macos.md>
  - <https://raw.githubusercontent.com/unageek/kigumi/HEAD/tools/run_benches.sh>
  - <https://raw.githubusercontent.com/unageek/kigumi/HEAD/tools/bench_methods.txt>
  - <https://raw.githubusercontent.com/unageek/kigumi/HEAD/benches/kigumi/main.cc>
  - <https://raw.githubusercontent.com/unageek/kigumi/HEAD/benches/corefinement/main.cc>
  - <https://github.com/unageek/kigumi/tree/main/include/kigumi>
  - <https://raw.githubusercontent.com/unageek/kigumi/HEAD/include/kigumi/Boolean_region_builder.h>
  - <https://raw.githubusercontent.com/unageek/kigumi/HEAD/include/kigumi/Region.h>
  - <https://raw.githubusercontent.com/unageek/kigumi/HEAD/include/kigumi/Corefine.h>
  - <https://raw.githubusercontent.com/unageek/kigumi/HEAD/include/kigumi/Autorefine.h>
  - <https://raw.githubusercontent.com/unageek/kigumi/HEAD/include/kigumi/Classify_faces_globally.h>
  - <https://raw.githubusercontent.com/unageek/kigumi/HEAD/include/kigumi/Find_possibly_intersecting_faces.h>
  - <https://raw.githubusercontent.com/unageek/kigumi/HEAD/include/kigumi/Triangulation.h>
  - <https://raw.githubusercontent.com/unageek/kigumi/HEAD/include/kigumi/parallel_do.h>
  - <https://raw.githubusercontent.com/unageek/kigumi/HEAD/include/kigumi/threading.h>
  - <https://raw.githubusercontent.com/unageek/kigumi/HEAD/include/kigumi/Context.h>
  - <https://raw.githubusercontent.com/unageek/kigumi/HEAD/include/kigumi/Warnings.h>
  - <https://github.com/unageek/kigumi/issues?q=is%3Aissue>
  - <https://github.com/unageek/kigumi/issues/28>
  - <https://github.com/unageek/kigumi/issues/33>
  - <https://github.com/unageek/kigumi/issues/35>
  - <https://github.com/unageek/kigumi/commits>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/unageek/kigumi`) · [data/wave8/enrich/raw/github_com_unageek_kigumi.json](../../../data/wave8/enrich/raw/github_com_unageek_kigumi.json) (enrichment confidence 0.8)

</details>
