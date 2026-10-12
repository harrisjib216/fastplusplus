# Coal (HPP-FCL)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> FCL hard fork (formerly HPP-FCL) with rewritten and Nesterov/Polyak-accelerated GJK/EPA; narrow-phase convex queries several times faster than FCL, libccd and Bullet.

| | |
|---|---|
| **Beats** | FCL (Flexible Collision Library) GJK; also Bullet GJK and libccd (MPR and GJK) |
| **Claimed result** | README: the accelerated GJK variants 'largely outperform by a large margin (from 5x up to 15x times faster)'. Medians read from the README box plot (log scale, approximate, derived from page data): Nesterov about 1.1 us, Polyak about 1.2 us, Coal vanilla GJK about 1.6 us; libccd MPR and GJK about 4.2 us; FCL GJK about 9.5 us; Bullet GJK about 17 us. That puts Nesterov at about 3.8x over libccd, 8.6x over FCL and 15x over Bullet, and vanilla Coal GJK at about 6x over FCL (derived from page data). Against libccd the medians do not reach the README's lower bound of 5x. |
| **Workload** | Narrow-phase convex collision and distance queries: per-query time distribution (microseconds, log scale) of Coal's GJK, Polyak-accelerated GJK and Nesterov-accelerated GJK versus FCL, Bullet and libccd. |
| **Metric** | latency |
| **Adoption** | 645 stars, 157 forks; README lists Pinocchio, IfcOpenShell, Crocoddyl, TSID, HPP, Jiminy, ocs2 and Simple as users; on conda-forge and PyPI |
| **Last commit** | 2026-09-30 |
| **Links** | [repository](https://github.com/coal-library/coal) · [benchmark](https://github.com/coal-library/coal) |

## Verdict

A README box plot (log scale; hardware, compiler and shape set not stated) gives per-query GJK median times of about 1.1 us (Nesterov), 1.2 us (Polyak) and 1.6 us (vanilla Coal), against about 4.2 us for libccd, 9.5 us for FCL and 17 us for Bullet. That is roughly 8.6x over FCL and 3.8x over libccd for the accelerated variant (derived from page data). The underlying GJK++ T-RO 2024 paper claims only up to 2x over the prior state of the art, since that comparison is against vanilla GJK.

## Use it when

- Many convex-vs-convex collision or distance queries per step (robot links against convex hulls or primitives) where FCL's or libccd's GJK is the hot spot; the README chart puts Coal's Nesterov GJK at about 1.1 us median against about 9.5 us for FCL and 4.2 us for libccd.
- Simulation, MPC or motion-planning loops with temporal coherence, where cached GJK guesses and support hints carry over between consecutive queries.
- You need a distance lower bound when there is no collision, safety margins, or contact patches for contact-rich simulation; FCL does not provide these.
- Stacks already built on Pinocchio, Crocoddyl, HPP or TSID, which depend on Coal and ship it on conda-forge, PyPI and ROS.

## Skip it when

- Broad-phase-heavy scenes of triangle-mesh BVHs: a third-party report (issue #857, GCC 11 -O3, Eigen 3.4) measured Coal 3.0.2's broad phase at 1.71-1.87x slower than FCL 0.6.1 and pairwise distance at 1.08-1.13x slower, with single-pair narrow phase about equal.
- Large non-convex mesh-vs-mesh overlap: issue #649 profiles EPA::reset allocations at 1.3 s of a 2.4 s coal::overlap between 5,000- and 4,200-vertex meshes, and the reporter found FCL 0.7 faster there. The issue is still open.
- Lightweight or embedded builds: it needs Eigen, Boost (serialization, filesystem) and assimp, with octomap and qhull optional, and builds as a shared library.
- When you need audited benchmark numbers: the 5-15x chart states no hardware, compiler or shape set, and against libccd the median gap is about 3.8x, not 5x.
- General computational geometry (polygon booleans, triangulation, spatial indexing): Coal is a narrow-phase collision library, not a CGAL, Boost.Geometry or GEOS replacement.

## How it is fast

Coal replaces FCL's libccd-based narrow phase with its own GJK (Van den Bergen-style convergence by default, with duality-gap or hybrid criteria available) and EPA. Its GJK++ work (IEEE T-RO 2024) treats GJK as a Frank-Wolfe method and adds Polyak and Nesterov momentum (GJKVariant::PolyakAcceleration / NesterovAcceleration), which the README and the paper say gives up to about 2x over vanilla GJK. Support-function hints, cached or AABB-based initial guesses (GJKInitialGuess::CachedGuess / BoundingVolumeGuess) and early stop on a distance threshold cut iterations further when queries repeat, as they do in simulation and planning loops.

## Compared with alternatives

None of the catalogued geometry siblings does rigid-body collision. Of the ones that come close, trueform and Manifold do mesh booleans and queries, and TinyBVH and madmann91/bvh do ray-tracing BVHs. Pick Coal when the workload is GJK/EPA distance and contact between convex robot geometry.

## Integration

| | |
|---|---|
| **Form** | shared lib (CMake via jrl-cmakemodules; conda-forge, PyPI 'coal', ROS package, Docker image) |
| **Dependencies** | Eigen3, Boost (serialization, filesystem; Boost.Log only with COAL_ENABLE_LOGGING), assimp; optional octomap &gt;= 1.8, qhull, Tracy; Python bindings need eigenpy/Boost.Python or nanobind |
| **Minimum toolchain** | C++17 (CHECK_MINIMAL_CXX_STANDARD(17 ENFORCE)), CMake 3.22+ |
| **Platforms** | Linux, macOS and Windows per CI and packaging (Windows support credited in the README); no ISA-specific requirement documented |
| **Thread safety** | Not documented. Free coal::collide/distance calls take caller-owned request and result objects. A ComputeCollision functor holds a mutable GJKSolver, so give each thread its own functor. |
| **Drop-in for the baseline** | partial: FCL-like request/result API and the broad phase is FCL 0.7's, but it uses the coal:: namespace, Eigen-based types (Vec3s, Transform3s) and different shape classes, so FCL code must be ported |

## Gotchas

- The accelerated GJK is opt-in: CollisionRequest defaults to gjk_variant = DefaultGJK and gjk_initial_guess = DefaultGuess, so you must set NesterovAcceleration (and ideally CachedGuess) to get the headline numbers.
- BoundingVolumeGuess silently needs computeLocalAABB() to have been called on both shapes (header warning).
- The Box support function used a function-local static inflation factor, so box query results depended on which query ran first in the process (issue #894, fixed by #895 in Sept 2026, listed as unreleased after 3.0.4). The effect is a relative 1e-10 inflation, but results were order-dependent.
- Reuse CollisionResult only after calling clear(), and note that penetration_depth excludes the security margin (README example).

## Known shortcomings

- Hard fork of FCL (is_fork_of set); README '5x-15x' is overstated vs libccd (chart medians about 3.8x); chart probably from the GJK++ T-RO 2024 paper, unreadable here (possible B on retier).
- Box support function used a function-local static, so box results depended on query order (#894, fixed by #895 in Sept 2026, not in a release after 3.0.4; \~1e-10 relative effect). Third-party issue #857 (GCC 11 -O3): broad phase 1.71-1.87x slower than FCL 0.6.1 on triangle-mesh BVHs; single pair about equal. #649: EPA::reset allocations take 1.3 s of a 2.4 s mesh overlap. Accelerated GJK is opt-in (default DefaultGJK); GJK++ paper claims up to 2x over vanilla GJK.

## Caveats and trade-offs

The evidence is one README chart, labelled with the pre-2024 'HPP-FCL' name. It states no hardware, compiler, flags, shapes or harness, and no benchmark code for the cross-library comparison is linked. The RSS 2022 artifact repo lmontaut/collision-detection-benchmark (g++ 9.4/12.1 and clang++ 13.0.1, no CPU or flags) covers only vanilla vs Nesterov GJK inside HPP-FCL. The cross-library figure is probably from the GJK++ paper (IEEE T-RO 2024, hal-04070039), which I could not open. The README's '5x' lower bound overstates the gap to libccd (about 3.8x at the median). The baseline FCL is Coal's own ancestor, and none of the category's list (Boost.Geometry, CGAL, GEOS, R-tree) is compared. Narrow-phase collision detection is only loosely 'geometry-spatial'.

Python bindings; adds safety margins, contact points and patches, serialization (Boost.Serialization), more shape types (height fields, capsules, ellipsoids). Narrow-phase focus; the project descends from FCL (renamed from HPP-FCL in 2024).

## Maintenance

Actively developed by Inria and LAAS-CNRS (3,877 commits, last commit 2026-09-30, release 3.0.4 in June 2026) and BSD-3-Clause, but a heavy dependency set means you link it rather than vendor it.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README has a box-plot chart (doc/images/coal-vs-the-rest-of-the-world.png) of per-query GJK times for Coal against libccd, FCL and Bullet, plus a '5x up to 15x' sentence. It states no hardware, compiler, flags or harness. The RSS 2022 artifact repo (lmontaut/collision-detection-benchmark) compares only vanilla and Nesterov GJK inside HPP-FCL, not FCL, libccd or Bullet. The chart probably comes from the authors' peer-reviewed GJK++ paper (IEEE T-RO 2024), but I could not open it to confirm, so it stays C.
- **Verifier notes:** The chart medians in the record match my own reading of the image. The README's 5x-15x is accurate only against FCL and Bullet; against libccd it is about 3.8x. I could not reach the GJK++ T-RO paper (hal.science, arxiv.org and simple-robotics.github.io are egress-blocked); if a later check confirms it contains this figure with stated hardware, the entry could move to B. BSD-3-Clause (LICENSE text), last commit 2026-09-30 and not a GitHub fork confirmed.
- **Fields the verifier corrected:** `claimed_speedup`, `is_fork_of`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/coal-library/coal/HEAD/README.md>
  - <https://raw.githubusercontent.com/coal-library/coal/HEAD/doc/images/coal-vs-the-rest-of-the-world.png>
  - <https://raw.githubusercontent.com/coal-library/coal/HEAD/LICENSE>
  - <https://github.com/coal-library/coal>
  - <https://github.com/coal-library/coal/commits>
  - <https://github.com/lmontaut/collision-detection-benchmark>
  - <https://github.com/RobotLocomotion/drake/issues/24964>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/coal-library/coal/HEAD/README.md>
  - <https://raw.githubusercontent.com/coal-library/coal/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/coal-library/coal/HEAD/package.xml>
  - <https://raw.githubusercontent.com/coal-library/coal/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/coal-library/coal/HEAD/include/coal/data_types.h>
  - <https://raw.githubusercontent.com/coal-library/coal/HEAD/include/coal/narrowphase/gjk.h>
  - <https://raw.githubusercontent.com/coal-library/coal/HEAD/include/coal/collision_data.h>
  - <https://raw.githubusercontent.com/coal-library/coal/HEAD/include/coal/collision.h>
  - <https://github.com/coal-library/coal>
  - <https://github.com/coal-library/coal/issues?q=is%3Aissue+GJK>
  - <https://github.com/coal-library/coal/issues/857>
  - <https://github.com/coal-library/coal/issues/894>
  - <https://github.com/coal-library/coal/issues/649>
  - <https://github.com/RobotLocomotion/drake/issues/24964>
  - WebSearch: GJK++ Leveraging Acceleration Methods for Faster Collision Detection (result snippets: researchgate, dl.acm.org/doi/10.1109/TRO.2024.3386370)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/coal-library/coal`) · [data/wave8/enrich/raw/github_com_coal_library_coal.json](../../../data/wave8/enrich/raw/github_com_coal_library_coal.json) (enrichment confidence 0.75)

</details>
