# PhysX

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `BSD-3-Clause` · 🔴 abandoned

> NVIDIA's frozen 2018 PhysX 3.4 rigid-body and scene-query SDK; one forum user timed PhysX capsule sweeps 6-19x faster than Bullet's.

| | |
|---|---|
| **Beats** | Bullet Physics |
| **Claimed result** | Snippet only, unverified (gamedev.net forum post, page blocked): capsule sweeps onto a triangle-mesh terrain, 1 capsule 0.132 ms (PhysX) vs 0.757 ms (Bullet); 100 capsules 3.790 ms (PhysX) vs 73.388 ms (Bullet); the poster summarises Bullet as costing about 10 times more (ratios about 5.7x and 19.4x, derived from the snippet numbers). |
| **Workload** | Collision queries only: swept capsules cast downward onto a static terrain triangle mesh, 1 capsule and 100 capsules at random positions, time per query batch. |
| **Metric** | latency |
| **Adoption** | 2.4k stars (PhysX-3.4 repo); widely embedded in game engines (usage not verified here) |
| **Last commit** | 2018-12-05 |
| **Links** | [repository](https://github.com/NVIDIAGameWorks/PhysX-3.4) |

## Verdict

One forum user swept capsules downward onto a triangle-mesh terrain through a common wrapper and reported 0.132 ms vs 0.757 ms for one capsule and 3.790 ms vs 73.388 ms for 100 capsules (PhysX vs Bullet, about 5.7x and 19.4x, derived from the snippet numbers); the engine versions, CPU, compiler, flags and date are unknown and the thread itself could not be opened. No measurement of this repository's PhysX 3.4 code against Bullet was found.

## Use it when

- Maintaining an existing game or engine already built on PhysX 3.4 (for example older Unreal Engine 4 versions) where swapping the physics layer is not an option.
- Sweep- and raycast-heavy gameplay code (character controllers, vehicle suspension sweeps, camera collision) against large static triangle meshes, if you opt in to the BVH34 midphase on an SSE2 platform.
- Projects that want a BSD-3-licensed, battle-tested rigid-body SDK covering Windows, Linux, macOS, Android and iOS from one source tree and can live with a 2018 code base.
- Experiments with GPU rigid bodies or the GPU broad phase on NVIDIA hardware (SM 3.0 or later) using the bundled prebuilt GPU libraries.

## Skip it when

- New projects: the repository was last changed on 2018-12-05 and its pinned issue #100 sends users to PhysX 4 (NVIDIAGameWorks/PhysX), whose README in turn points all new projects to PhysX 5 at NVIDIA-Omniverse/PhysX.
- If you need a measured speed advantage: the only evidence is one forum user's timings that are probably years older than this code, with versions, hardware and build settings unknown; nothing in this repo benchmarks PhysX against Bullet.
- If you need the GPU path from source or on non-NVIDIA hardware: the GPU rigid-body code ships only as prebuilt binaries (for example libPhysX3Gpu_x64.so under Bin/linux64) and requires CUDA.
- Builds on modern toolchains: the source ships hand-made Visual Studio 2013/2015/2017 solutions and per-platform makefiles (no CMake); release notes list GCC 4.8 on Ubuntu 16.04 as the tested Linux setup.
- Workloads that need the batched-query API: PxBatchQuery is deprecated in 3.4 and an open issue (#142) asks how to batch many raycasts without it.

## How it is fast

Scene queries go through two levels: a pruner over actor bounds (dynamic AABB trees by default for both static and dynamic objects) and a per-mesh midphase tree. PhysX 3.4 added the BVH34 midphase, a quantized bounding-volume tree (BV4) with precomputed node sorting and an SSE 'swizzled slabs' node layout (PEEL's release notes, by a PhysX engineer, say PhysX 3.4 includes an Opcode2-based mesh format); its capsule sweep code is compiled only for Intel-family SIMD builds. The default midphase is still the older BVH33 R-tree (4-wide transposed, quantized pages). Contact generation defaults to PCM (persistent contact manifold, GJK-based distance) and the broad phase offers SAP, MBP (multi box pruning) and a GPU variant.

## Compared with alternatives

Against the catalogued Bullet Physics, pick PhysX when your work is dominated by sweeps and raycasts against large static meshes and you can use its cooked BVH34 meshes, but take the newer PhysX 5 repository rather than this 3.4 snapshot. For a new multi-core game engine the catalogued Jolt Physics is the maintained choice, and for robotics distance and collision queries Coal (HPP-FCL) has its own measured GJK advantage.

## Integration

| | |
|---|---|
| **Form** | static or shared libs built from the bundled Visual Studio solutions or makefiles (PhysX_3.4/Source/compiler); GPU module as prebuilt shared libraries |
| **Dependencies** | PxShared (in the repo); CUDA-capable NVIDIA driver only for the optional GPU features; APEX 1.4 is optional and deprecated |
| **Minimum toolchain** | Visual Studio 2013, 2015 or 2017 (vc12, vc14, vc15 projects); GCC 4.8 tested on Ubuntu 16.04; Xcode 10.1 for macOS and iOS; Android NDK r13b |
| **Platforms** | Windows (32/64-bit), Linux (32/64-bit), macOS, iOS, Android ARM; console builds are under NDA and not on GitHub; BVH34 midphase needs SSE2; GPU features need an NVIDIA GPU and driver (SM 3.0+ for GPU rigid bodies and the GPU broad phase; Linux GPU support is 64-bit only) |
| **Thread safety** | Concurrent scene queries are allowed; PxSceneFlag::eREQUIRE_RW_LOCK makes the scene enforce PxScene::lockRead/lockWrite, and a thread flushing query updates (flushQueryUpdates, or the first query after changes) holds a write lock on the query structure that stalls other querying threads |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness and provenance flaw: the only numbers come from the gamedev.net thread 'Efficiency : Bullet much slower than PhysX?' (topic 600114, blocked here; read through search snippets). Its topic number and a reply asking whether hardware acceleration was on in both engines suggest a PhysX 2.x or 3.0-era test (inference, not confirmed), so it likely did not measure the PhysX 3.4 code in this repo. The poster used a triangle-mesh terrain in Bullet, and a reply suggested btHeightfieldTerrainShape instead.
- Bullet's shipped build settings are a known handicap in engine comparisons: PEEL's release notes (by a PhysX engineer) say Bullet 2.81's shipped optimization settings 'seem sub-optimal' and that his comparison rebuilt Bullet with PhysX's settings; the forum test's Bullet build flags are unknown.
- The faster BVH34 midphase is not the default: PxCookingParams::midphaseDesc defaults to eINVALID, which falls back to BVH33, so meshes must be cooked with PxMeshMidPhase::eBVH34 to get it, and BVH34 is limited to SSE2 platforms. A November 2018 fix covers raycasts failing on binary-deserialized BVH34 meshes, so older 3.4 builds have that bug.
- Open issue #126 (March 2020, no reply): non-blocking vehicle suspension sweeps return several hits with different normals at the seam between two heightfields or two static meshes, making wheels bump; the repo has 50 open issues, several of them crashes (#113, #134, #141, #143), and none are being answered.

## Known shortcomings

- The only source is a gamedev.net thread (600114, blocked) seen as search snippets (capsule sweeps 0.132 vs 0.757 ms Bullet) in which a reply questions the Bullet setup (triangle mesh vs heightfield); versions and hardware unknown; Bullet is not a geometry-spatial baseline. Downgraded C to D.
- Enricher: the gamedev.net thread (topic 600114) is still blocked and its topic number and 'hardware acceleration' reply point to a PhysX 2.x/3.0-era test, so probably not this repo's 3.4 code; Bullet used a triangle mesh, not a heightfield, and PEEL release notes (by a PhysX engineer) say Bullet 2.81 shipped with sub-optimal build settings; the faster BVH34 midphase is not the default (eINVALID falls back to BVH33, BVH34 SSE2-only); GPU code is prebuilt binaries only; repo frozen 2018-12-05 (issue #100 points to PhysX 4 and then NVIDIA-Omniverse/PhysX); open #126 (suspension sweeps return several hits at heightfield seams).

## Caveats and trade-offs

Evidence is WebSearch snippets only. The source is a gamedev.net forum thread, 'Efficiency : Bullet much slower than PhysX?' (https://www.gamedev.net/forums/topic/600114-efficiency-bullet-much-slower-than-physx/), which was EGRESS_BLOCKED, so the date, PhysX and Bullet versions, hardware, compiler and flags are unknown; the thread is probably old and likely predates the PhysX 3.4 code in this repo. A search summary of the same thread also mentions 500 capsules at 488 ms (Bullet) vs 43 ms (PhysX) and a reply questioning the setup (whether hardware acceleration was on in both engines, and whether Bullet's btHeightfieldTerrainShape should have been used instead of a triangle-mesh shape); snippet only, unverified. It is one user's forum anecdote of sweep (raycast-style) queries on a mesh, not rigid-body stepping. The peer-reviewed Erez, Tassa and Todorov ICRA 2015 comparison of Bullet, Havok, MuJoCo, ODE and PhysX exists (homes.cs.washington.edu PDF, blocked here; no GitHub copy found); its search summary says no engine wins overall and gaming engines do best on gaming-style tests, so it was not used for a speedup claim. Pierre Terdiman's PEEL ships no results, the Gazebo benchmark does not include PhysX, and the PhysX-3.4 README has no performance text. Bullet is not among the geometry-spatial baselines (Boost.Geometry, CGAL, GEOS, R-trees), and a physics engine fits that category only loosely through its collision queries. The repo is the 2018 PhysX 3.4 snapshot (last commit 2018-12-05, BSD-3-Clause per README); newer PhysX releases live elsewhere and were not opened.

Full rigid-body, articulation, cloth and vehicle SDK with an optional NVIDIA-only CUDA GPU path; large code base. This repo is PhysX 3.4 with the deprecated APEX SDK; the README points cloth, destruction, particle and turbulence users to NvCloth, Blast, FleX and Flow.

## Maintenance

Abandoned since 2018-12-05 (30 commits, superseded by PhysX 4 and then PhysX 5 at NVIDIA-Omniverse/PhysX), BSD-3-Clause only from the December 2018 3.4.2 release, and the speed evidence is a forum anecdote that probably predates this code, so it stays at tier D; consider pointing the entry at the maintained PhysX 5 repository if better evidence is found.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification C, tier now D.
- **Tier reason:** benchmark_url is null and the only source, the gamedev.net forum thread 'Efficiency : Bullet much slower than PhysX?', is EGRESS_BLOCKED; the numbers survive only as WebSearch snippets, and the repo README has no performance text, so per the null-benchmark rule the record cannot stay above D.
- **Verifier notes:** Downgraded C to D: no openable benchmark page; the forum thread is blocked and its numbers come from search snippets, with a reply in the same thread questioning the Bullet setup. Not rejected: PhysX is notable (2.4k stars on this repo, 297 forks, widely embedded). Metadata checked on github.com: BSD-3-Clause license text in README, not archived, last commit 2018-12-05, abandoned. If kept, record shortcomings: forum anecdote only, versions/hardware unknown, possible Bullet misuse (triangle mesh instead of heightfield), off-baseline for geometry-spatial.
- **Fields the verifier corrected:** `baseline_in_list`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** forum snippets (verifier downgrade); enricher w8 pair-036
- **Pages the verifier opened:**
  - <https://github.com/NVIDIAGameWorks/PhysX-3.4>
  - <https://github.com/NVIDIAGameWorks/PhysX-3.4/commits>
  - <https://raw.githubusercontent.com/NVIDIAGameWorks/PhysX-3.4/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/NVIDIAGameWorks/PhysX-3.4>
  - <https://github.com/NVIDIAGameWorks/PhysX-3.4/commits/master>
  - <https://github.com/NVIDIAGameWorks/PhysX-3.4/issues>
  - <https://github.com/NVIDIAGameWorks/PhysX-3.4/issues/100>
  - <https://github.com/NVIDIAGameWorks/PhysX-3.4/issues/126>
  - <https://github.com/NVIDIAGameWorks/PhysX-3.4/tree/master/PhysX_3.4>
  - <https://github.com/NVIDIAGameWorks/PhysX-3.4/tree/master/PhysX_3.4/Bin>
  - <https://github.com/NVIDIAGameWorks/PhysX-3.4/tree/master/PhysX_3.4/Bin/linux64>
  - <https://github.com/NVIDIAGameWorks/PhysX-3.4/tree/master/PhysX_3.4/Source/compiler>
  - <https://github.com/NVIDIAGameWorks/PhysX-3.4/tree/master/PhysX_3.4/Source/GeomUtils/src/mesh>
  - <https://raw.githubusercontent.com/NVIDIAGameWorks/PhysX-3.4/HEAD/README.md>
  - <https://raw.githubusercontent.com/NVIDIAGameWorks/PhysX-3.4/HEAD/PhysX_3.4/release_notes.html>
  - <https://raw.githubusercontent.com/NVIDIAGameWorks/PhysX-3.4/HEAD/PhysX_3.4/platform_readme.html>
  - <https://raw.githubusercontent.com/NVIDIAGameWorks/PhysX-3.4/HEAD/PhysX_3.4/Include/PxPhysicsAPI.h>
  - <https://raw.githubusercontent.com/NVIDIAGameWorks/PhysX-3.4/HEAD/PhysX_3.4/Include/PxScene.h>
  - <https://raw.githubusercontent.com/NVIDIAGameWorks/PhysX-3.4/HEAD/PhysX_3.4/Include/PxSceneDesc.h>
  - <https://raw.githubusercontent.com/NVIDIAGameWorks/PhysX-3.4/HEAD/PhysX_3.4/Include/PxQueryFiltering.h>
  - <https://raw.githubusercontent.com/NVIDIAGameWorks/PhysX-3.4/HEAD/PhysX_3.4/Include/geometry/PxTriangleMesh.h>
  - <https://raw.githubusercontent.com/NVIDIAGameWorks/PhysX-3.4/HEAD/PhysX_3.4/Include/cooking/PxCooking.h>
  - <https://raw.githubusercontent.com/NVIDIAGameWorks/PhysX-3.4/HEAD/PhysX_3.4/Include/cooking/PxMidphaseDesc.h>
  - <https://raw.githubusercontent.com/NVIDIAGameWorks/PhysX-3.4/HEAD/PhysX_3.4/Include/cooking/PxBVH34MidphaseDesc.h>
  - <https://raw.githubusercontent.com/NVIDIAGameWorks/PhysX-3.4/HEAD/PhysX_3.4/Source/GeomUtils/src/mesh/GuBV4_CapsuleSweep.cpp>
  - <https://raw.githubusercontent.com/NVIDIAGameWorks/PhysX-3.4/HEAD/PhysX_3.4/Source/GeomUtils/src/mesh/GuBV4Settings.h>
  - <https://raw.githubusercontent.com/NVIDIAGameWorks/PhysX-3.4/HEAD/PhysX_3.4/Source/GeomUtils/src/mesh/GuRTree.h>
  - <https://github.com/NVIDIAGameWorks/PhysX>
  - <https://github.com/Pierre-Terdiman/PEEL>
  - <https://github.com/Pierre-Terdiman/PEEL/tree/master/PEEL>
  - <https://github.com/Pierre-Terdiman/PEEL/tree/master/PEEL/Docs>
  - <https://raw.githubusercontent.com/Pierre-Terdiman/PEEL/HEAD/PEEL/Release%20notes.txt>
  - <https://raw.githubusercontent.com/Pierre-Terdiman/PEEL/HEAD/PEEL/Docs/PEEL%20User%20Manual%201.1.pdf>
  - https://www.gamedev.net/forums/topic/600114-efficiency-bullet-much-slower-than-physx/ (fetch failed: ENOTFOUND, blocked)
  - WebSearch: "Bullet much slower than PhysX" gamedev.net capsule sweep triangle mesh (snippets)
  - WebSearch: PEEL Terdiman PhysX 3.4 vs Bullet scene query sweep benchmark results github (snippets)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/nvidiagameworks/physx-3.4`) · [data/wave8/enrich/raw/github_com_nvidiagameworks_physx_3_4.json](../../../data/wave8/enrich/raw/github_com_nvidiagameworks_physx_3_4.json) (enrichment confidence 0.6)

</details>
