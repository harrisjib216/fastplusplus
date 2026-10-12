# trueform

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `PolyForm-Noncommercial-1.0.0` · 🟢 active

> Header-only C++17 mesh-processing library (booleans, intersection curves, spatial trees, remeshing) that the vendor measures 2-233x faster than CGAL, libigl, MeshLib and nanoflann.

| | |
|---|---|
| **Beats** | CGAL (EPICK kernel; also libigl, MeshLib, VTK, nanoflann, Coal/FCL) |
| **Claimed result** | README table: mesh-mesh curves 2x1M 7 ms, 233x vs CGAL EPICK; connected components 1M 15 ms, 10x vs CGAL; boundary paths 12 ms, 11x vs CGAL; decimation 50% 72 ms, 50x vs CGAL edge_collapse; boolean union 2x1M 28 ms, 6x vs MeshLib; self-intersection 78 ms, 37x vs libigl EPECK; ICP 93x and principal curvatures 55x vs libigl; isocontours 38x vs VTK; k-NN 1.7 us, 3x vs nanoflann; mesh-mesh distance 2x vs Coal OBBRSS. |
| **Workload** | Mesh geometry ops on 1M-triangle meshes: mesh-mesh intersection curves (2x1M), connected components, boundary paths, 50% decimation, boolean union vs MeshLib, k-NN vs nanoflann. |
| **Metric** | latency |
| **Hardware** | Apple M4 Max, 16 threads |
| **Compiler and flags** | Clang -O3 -march=native |
| **Adoption** | 132 stars |
| **Last commit** | 2026-09-22 |
| **Links** | [repository](https://github.com/polydera/trueform) · [benchmark](https://github.com/polydera/trueform) |

## Verdict

Vendor-run benchmarks on an Apple M4 Max (16 threads, Clang -O3 -march=native) use the repo's benchmarks/ suite, which FetchContents CGAL 6.0.1 (with CGAL_LINKED_WITH_TBB), libigl 2.5.0, nanoflann 1.5.5, FCL 0.7.0, geogram 1.9.4 and Coal at its unpinned 'devel' branch, and reports the mean (curves, booleans, k-NN) or minimum (decimation, components) of 10 samples. The committed data at 1M polygons: union 27.8 ms vs CGAL corefinement 2,339 ms (about 84x, derived from page data) and MeshLib 161.5 ms (5.8x); k-NN on 512,872 points at k=10, 1.5 us (OBB/OBBRSS) vs nanoflann 4.5 us; mesh-mesh distance 0.20 ms (OBBRSS) vs Coal 0.47 ms. No MeshLib benchmark code is in the repo, so the 6x MeshLib figure cannot be reproduced from it, and the curves and boolean ratios exclude trueform's tree and topology build but include CGAL's.

## Use it when

- Interactive or batch booleans and intersection curves on 10^5 to 10^6-triangle meshes on a multi-core machine: about 28 ms for a 2x1M union and 7 ms for 2x1M intersection curves on 16 M4 Max threads, with the tree already built
- Repeated collision, distance or CSG queries against rigidly moving copies of the same mesh, where one prebuilt tree is reused through a tf::frame tag
- Pipelines that hold geometry in flat arrays (C++ buffers, NumPy, browser TypedArrays) and want many operations from one library without converting to a half-edge type
- Messy real-world meshes (non-manifold flaps, near-coincident walls): the 0.10.0 release notes report 1000/1000 closed, manifold results on the vendor's 1000-pair real-world corpus
- Non-commercial, academic or evaluation work, or a team that will buy XLAB's commercial licence

## Skip it when

- Commercial, production or revenue-generating use without a paid agreement: the only public licence is PolyForm Noncommercial 1.0.0, which is not OSI-approved
- Results that need exact rational output coordinates or provable exactness on the original floats (CGAL EPECK/Nef): trueform is exact on its integer lattice (float input maps to int32, double to int64), then rounds output back to float, and a non-zero tolerance moves vertices
- Single-threaded or TBB-free environments: the headline numbers use 16 threads, and oneTBB is a hard dependency
- One-off operations on meshes you will not query again: the repo's boolean and curve benchmarks build the AABB tree and topology outside the timer, so a cold call costs more than the headline figure
- Code that needs a stable API: the library is 0.x and recent releases removed flags and reorganised modules (0.10.0 'module map (breaking)', 0.10.5 removed the resolve_\* flags)

## How it is fast

Coordinates are scaled onto an int32/int64 lattice, and every orientation and intersection predicate is evaluated in exact integer arithmetic. This avoids CGAL's lazy/rational number types while still classifying contacts into five canonical types (VV, VE, VF, EE, EF) and arranging each cut face in its own plane; disagreeing observations are resolved by 'topological aggregation', a majority vote within a manifold-edge-connected unit (Sajovic and Knez, arXiv 2607.15905). Most algorithms run in parallel on oneTBB (parallel union-find for components, partitioned edge collapse for decimation, k-ring quadric fitting for curvature) and allocate through a vendored mimalloc. Spatial trees are built once and reused under a rigid-transform tag, so a moving operand does not need a new tree.

## Compared with alternatives

Against MeshLib (also source-available non-commercial, and trueform's boolean baseline), pick trueform for its wider set of composable primitives on raw arrays and reusable trees under rigid motion; pick Manifold when the licence must be permissive (Apache-2.0), and nanoflann for a permissive point k-NN index, even though trueform's OBB/OBBRSS trees beat it about 3x on single queries.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | oneTBB (required); mimalloc 3.5.1 fetched and linked statically by default (TF_USE_MIMALLOC=OFF falls back to operator new); optional precompiled C++ facade (TF_BUILD_CPP), VTK integration; pip, Conan, NuGet and npm packages |
| **Minimum toolchain** | C++17, CMake 3.16+; the benchmark suite builds as C++20; CI tests use Clang on Linux |
| **Platforms** | Linux, macOS and Windows (pip wheels built on all three, NuGet for Visual Studio), plus WebAssembly via npm @polydera/trueform; portable C++, -march=native only in the benchmarks |
| **Thread safety** | not documented; algorithms parallelise internally with oneTBB (issue #5 still tracks wrapping the remaining direct tbb:: calls) |
| **Drop-in for the baseline** | no |

## Gotchas

- Benchmarks are not like for like. In benchmarks/intersect and benchmarks/arrangement, trueform's AABB tree, face_membership and manifold_edge_link are built before timing, and the second operand is the same mesh under a rotation frame sharing that tree. CGAL's timed surface_intersection / corefine_and_compute_union call builds its own structures, and for the union it also copies both 1M-face Surface_meshes. trueform's own data puts one 1M-polygon AABB build at about 7.4 ms.
- Correctness fixes are recent. v0.10.5 (Sep 2026) fixed N-operand 'within' builds that assigned every domain to operand 0 (shipped in 0.10.3-0.10.4), self-intersection split points placed on another operand's edges, and undefined behaviour from misaligned float loads in the binary STL reader. 0.10.0 fixed issue #21 (fit_similarity_alignment returned a scale n times too small). Pin a version and keep regression tests.
- A system mimalloc must be built with MI_OVERRIDE=OFF and MI_ENABLE_LARGE_PAGES=0. Upstream's large-page default made a 16-thread process retain memory without bound (324 MB vs 156 MB over 200 graph builds), and ASAN builds force mimalloc off.
- OBJ/STL path readers memory-map the file, so it must not change during the read

## Known shortcomings

- Vendor-run benchmark (kept at A because code, compiler, flags and CPU are public: the vendor-blog rule covers unreproducible blog numbers); 16 threads vs serial baselines; PolyForm noncommercial license (reference only).
- Benchmarks not like-for-like: trueform's tree and topology are built before the timer and the second operand is a rotated view sharing that tree, while CGAL's timed call builds its own structures (and copies both meshes for union), so the 233x curve and union ratios are inflated; 16 threads vs mostly serial baselines.
- MeshLib 6x claim has no benchmark code in the repo; Coal pinned to an unpinned devel branch; correctness bugs fixed in v0.10.5 (Sep 2026): N-operand within builds lost operand membership (shipped 0.10.3-0.10.4) and the binary STL reader had UB from misaligned loads; vendor-run (XLAB sells a commercial licence).

## Caveats and trade-offs

Vendor-run benchmark (Polydera/XLAB sells a commercial license). Parallel (16 threads, TBB) vs mostly serial baselines. Dual license: PolyForm-Noncommercial-1.0.0 (non-OSI) or paid commercial, so reference only. Methodology page trueform.polydera.com/cpp/benchmarks gave no figures when opened by the search agent; benchmarks/ directory listing blocked by robots, CMakeLists read via raw.githubusercontent.com. [retier] trueform's trees/topology are built before the timer and shared with the rotated second operand while CGAL builds its structures inside the timed call; 16 threads vs mostly serial baselines; MeshLib 6x claim has no benchmark code; correctness fixes in v0.10.5 postdate the numbers.

Header-only C++17 with Python/TS bindings; multithreaded (16 threads) versus presumably serial CGAL; exact predicates.

## Maintenance

Very active (v0.10.5 released 2026-09-21, last commit 2026-09-22, about 146 stars, nearly all commits by one author at XLAB/Polydera), but dual-licensed PolyForm Noncommercial or paid commercial. It is reference-only for this catalogue and cannot be copied into commercial code.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** Upgrade: the README table states Apple M4 Max, 16 threads, Clang -O3 -march=native, and the repo carries public benchmark code (benchmarks/CMakeLists.txt with run_benchmarks.cpp and spatial/topology/intersect/remesh suites that FetchContent CGAL v6.0.1, libigl, FCL, Coal, geogram, VTK). Code, compiler, flags and CPU model are all present.
- **Retiered** A to C: Vendor-run benchmarks (XLAB sells a commercial licence) that are not like-for-like: trueform's acceleration structures are built outside the timer and shared by the rotated second operand while CGAL's timed call builds its own and copies both meshes; correctness fixes (v0.10.5, Sep 2026) postdate the published numbers. Vendor rule and unequal-work precedent (tcFFT) give C.
- **Verifier notes:** Tier raised C-&gt;A on reproducibility (code+compiler+flags+CPU); orchestrator may retier to C under the vendor-evidence rule if it applies to vendor-run repo benchmarks. Metadata matches: 132 stars, last commit 2026-09-22.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/polydera/trueform>
  - <https://raw.githubusercontent.com/polydera/trueform/HEAD/README.md>
  - <https://raw.githubusercontent.com/polydera/trueform/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/polydera/trueform/HEAD/benchmarks/CMakeLists.txt>
  - <https://github.com/polydera/trueform/commits>
- **Sources the enricher read:**
  - <https://github.com/polydera/trueform>
  - <https://raw.githubusercontent.com/polydera/trueform/HEAD/README.md>
  - <https://raw.githubusercontent.com/polydera/trueform/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/polydera/trueform/HEAD/COMMERCIAL.md>
  - <https://raw.githubusercontent.com/polydera/trueform/HEAD/RELEASE_NOTES.md>
  - <https://raw.githubusercontent.com/polydera/trueform/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/polydera/trueform/HEAD/benchmarks/CMakeLists.txt>
  - <https://raw.githubusercontent.com/polydera/trueform/HEAD/benchmarks/run_benchmarks.cpp>
  - <https://raw.githubusercontent.com/polydera/trueform/HEAD/benchmarks/common/timing.hpp>
  - <https://raw.githubusercontent.com/polydera/trueform/HEAD/benchmarks/intersect/mesh_mesh_curves-cgal-impl.cpp>
  - <https://raw.githubusercontent.com/polydera/trueform/HEAD/benchmarks/intersect/mesh_mesh_curves-tf-impl.cpp>
  - <https://raw.githubusercontent.com/polydera/trueform/HEAD/benchmarks/arrangement/boolean-tf-impl.cpp>
  - <https://raw.githubusercontent.com/polydera/trueform/HEAD/benchmarks/arrangement/boolean-cgal-impl.cpp>
  - <https://raw.githubusercontent.com/polydera/trueform/HEAD/benchmarks/remesh/decimation-cgal-impl.cpp>
  - <https://raw.githubusercontent.com/polydera/trueform/HEAD/benchmarks/remesh/decimation-tf-impl.cpp>
  - <https://raw.githubusercontent.com/polydera/trueform/HEAD/benchmarks/topology/connected_components-cgal-impl.cpp>
  - <https://raw.githubusercontent.com/polydera/trueform/HEAD/benchmarks/topology/connected_components-tf-impl.cpp>
  - <https://raw.githubusercontent.com/polydera/trueform/HEAD/benchmarks/spatial/point_cloud-knn-tf-impl.cpp>
  - <https://raw.githubusercontent.com/polydera/trueform/HEAD/benchmarks/spatial/point_cloud-knn-nanoflann-impl.cpp>
  - <https://raw.githubusercontent.com/polydera/trueform/HEAD/docs/benchmarks/boolean.json>
  - <https://raw.githubusercontent.com/polydera/trueform/HEAD/docs/benchmarks/point_cloud_knn.json>
  - <https://raw.githubusercontent.com/polydera/trueform/HEAD/docs/benchmarks/mesh_mesh_closest_point.json>
  - <https://raw.githubusercontent.com/polydera/trueform/HEAD/docs/benchmarks/isocontours.json>
  - <https://raw.githubusercontent.com/polydera/trueform/HEAD/docs/benchmarks/polygons_build_tree.json>
  - <https://raw.githubusercontent.com/polydera/trueform/HEAD/docs/content/cpp/3.benchmarks.md>
  - <https://raw.githubusercontent.com/polydera/trueform/HEAD/docs/content/cpp/6.about/1.research.md>
  - <https://raw.githubusercontent.com/polydera/trueform/HEAD/docs/content/cpp/1.getting-started/2.installation.md>
  - <https://raw.githubusercontent.com/polydera/trueform/HEAD/include/trueform/exact_coordinate_converter.hpp>
  - <https://raw.githubusercontent.com/polydera/trueform/HEAD/.github/workflows/tests.yml>
  - <https://raw.githubusercontent.com/polydera/trueform/HEAD/.github/workflows/build-python.yml>
  - <https://github.com/polydera/trueform/tree/main/benchmarks>
  - <https://github.com/polydera/trueform/tree/main/benchmarks/intersect>
  - <https://github.com/polydera/trueform/tree/main/include/trueform>
  - <https://github.com/polydera/trueform/tree/main/python>
  - <https://github.com/polydera/trueform/tree/main/docs>
  - <https://github.com/polydera/trueform/tree/main/docs/benchmarks>
  - <https://github.com/polydera/trueform/issues?q=is%3Aissue>
  - <https://github.com/polydera/trueform/commits/main>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/polydera/trueform`) · [data/wave8/enrich/raw/github_com_polydera_trueform.json](../../../data/wave8/enrich/raw/github_com_polydera_trueform.json) (enrichment confidence 0.75)

</details>
