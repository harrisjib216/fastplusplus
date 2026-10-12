# MeshLib

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `Proprietary non-commercial/educational license (AMV Consulting, LLC); commercial license sold separately` · 🟢 active

> Source-available C++ mesh-processing SDK whose triangle-mesh booleans run tens of times faster than CGAL's exact booleans.

| | |
|---|---|
| **Beats** | CGAL (also Manifold, libigl, MCut and 5 others) |
| **Claimed result** | Nefertiti (2M triangles) union: 47x faster than CGAL, 2.9x faster than Manifold, 153x faster than Blender; on the dental scan CGAL hangs while MeshLib finishes in \~44 ms |
| **Workload** | Mesh union of 2M-triangle Nefertiti models; dental scan of 280K triangles with defects. |
| **Metric** | latency |
| **Hardware** | Apple M5 MacBook Air, macOS 26 |
| **Adoption** | 826 stars |
| **Last commit** | 2026-10-01 |
| **Links** | [repository](https://github.com/MeshInspector/MeshLib) · [benchmark](https://meshlib.io/blog/comparing-3d-boolean-libraries/) |

## Verdict

MeshInspector's own 2026 blog benchmark tested MeshLib 3.1.3.249 against CGAL, Manifold, MCut, CinoLib, libigl, Rhino and Blender via trimesh on an Apple M5 MacBook Air (10-core, 32 GB, macOS 26), taking the minimum of 10 runs with I/O excluded and default threading; compiler and flags are not stated. Union on 2M-triangle Nefertiti meshes: 0.09 s MeshLib, 0.27 s Manifold, 4.4 s CGAL (about 47x), 14 s Blender. On a degenerate dental scan MeshLib took 0.04 s while CGAL hung and MCut failed. The raw data is on a SharePoint link, and the post says the benchmark source 'will be opened publicly later'.

## Use it when

- Booleans on large scanned triangle meshes (10^5 to several 10^6 triangles), where CGAL takes seconds or hangs: 0.09 s vs CGAL's 4.4 s on a 2M-triangle union in the vendor benchmark
- Inputs with many near-coplanar faces or degeneracies (dental/medical scans) that make exact-arithmetic CGAL stall
- Non-commercial, academic or evaluation work, or a team prepared to buy the commercial licence
- Pipelines that also need repair, decimation, offsetting or voxel/SDF operations from the same SDK, from C++, Python or C#

## Skip it when

- Commercial or redistributed software without a paid licence: the LICENSE grants only a terminable non-commercial/evaluation/educational licence and forbids modification and transfer
- Work that needs provable exactness or exact rational output coordinates: CGAL's Nef/corefinement with an exact kernel stays the reference there
- Non-manifold input: the half-edge structure cannot represent most non-manifold situations, so such meshes need repair first or the voxel mode
- A small permissive dependency: Manifold (Apache-2.0) was only about 3x slower on the Nefertiti union and about as fast on the dental scan in the same benchmark

## How it is fast

It works in floating point on a half-edge mesh. Degenerate configurations are handled by exact predicates (orient3d) on coordinates converted to integers, with Simulation of Simplicity (Edelsbrunner-Mücke) breaking ties. This avoids CGAL's rational/lazy-exact arithmetic, which the vendor blames for CGAL being 10-100x slower and hanging on near-coplanar faces. The work runs multi-threaded by default (the benchmark used default threading on a 10-core M5), and an AABB tree for intersection search is built once as pre-computation.

## Compared with alternatives

None of the catalogued siblings (TG, gDel3D, HXT, GeoToolbox KdBoxTree, nanoflann, tidwall rtree.c) does mesh booleans; MeshLib is the catalogue's mesh-CSG entry. Pick it when the task is a boolean on a large triangle mesh and the licence fits; otherwise look at Manifold.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | a large SDK with many third-party dependencies (not enumerated here); prebuilt packages via pip install meshlib, dotnet add package MeshLib and npm @meshinspector/meshlib, and C++ per the vendor's installation guide |
| **Minimum toolchain** | not documented in the pages read |
| **Platforms** | Windows, macOS, Linux (Ubuntu/Debian, Fedora/RHEL), WebAssembly |
| **Thread safety** | not documented; booleans are internally multi-threaded by default |
| **Drop-in for the baseline** | no |

## Gotchas

- Failures come back as an invalid BooleanResult with errorString, not as exceptions, so always check result.valid()
- Floating-point classification bugs still turn up: PR #6861 fixed Union silently dropping a whole mesh when two meshes only touch (DifferenceBA gave negative volume), fixed with exact integer orient3d probing
- Vendor timings vary across MeshLib's own pages: the boolean feature page lists a 1.2 s Nefertiti union, the 2026 blog 0.09 s with 3.1.3.249 on an M5. Benchmark your own version
- Blender and Rhino give different (still watertight) results on self-intersecting input, so speed comparisons across libraries are not always like for like

## Known shortcomings

- Vendor blog (company sells MeshLib); compiler and flags not stated; benchmark source 'will be opened publicly later'; non-commercial/education license from AMV Consulting (reference only).
- Blog says dental scan is \~500K triangles (record said 280K); blog both says inputs/runners are open source and that source 'will be opened later'; MeshLib's own feature page gives 1.2 s Nefertiti union vs the blog's 0.09 s (inconsistent vendor numbers); PR #6861 recently fixed Union dropping a mesh when meshes only touch; LICENSE is a terminable non-commercial trial that forbids modification.

## Caveats and trade-offs

Vendor blog from the company selling the product; benchmark source code not yet public (inputs, runners' outputs and timing JSON on a SharePoint link); compiler and flags not stated; default threading (multi-threaded). Source-available, non-commercial license: must not be copied. 47x/153x gains with unstated flags.

Multithreaded, CUDA for some ops; half-edge manifold-by-construction; bindings for C, C#, Python, WASM.

## Maintenance

Very active (commits daily, about 826 stars, versioned releases), but source-available under a non-commercial/evaluation licence. It is reference-only for this catalogue and must not be copied into commercial code.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** Vendor blog with first-party numbers vs CGAL, Manifold, Blender on an Apple M5 with min-of-10 methodology, but the blog says benchmark source code 'will be opened publicly later' and compiler/flags are not stated.
- **Verifier notes:** License file is a non-commercial trial/education agreement, so usability 'reference' stands. Last commit read from the commits page.
- **Fields the verifier corrected:** `claimed_speedup`, `license`, `caveats`
- **Pages the verifier opened:**
  - <https://meshlib.io/blog/comparing-3d-boolean-libraries/>
  - <https://github.com/MeshInspector/MeshLib>
  - <https://github.com/MeshInspector/MeshLib/commits>
  - <https://raw.githubusercontent.com/MeshInspector/MeshLib/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://meshlib.io/blog/comparing-3d-boolean-libraries/>
  - <https://github.com/MeshInspector/MeshLib>
  - <https://raw.githubusercontent.com/MeshInspector/MeshLib/HEAD/LICENSE>
  - <https://meshlib.io/feature/mesh-boolean/>
  - <https://meshlib.io/documentation/ExampleMeshBoolean.html>
  - <https://github.com/MeshInspector/MeshLib/pull/6861>
  - <https://polydera.com/algorithms/python-mesh-boolean-libraries-2026>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/meshinspector/meshlib`) · [data/wave8/enrich/raw/github_com_meshinspector_meshlib.json](../../../data/wave8/enrich/raw/github_com_meshinspector_meshlib.json) (enrichment confidence 0.7)

</details>
