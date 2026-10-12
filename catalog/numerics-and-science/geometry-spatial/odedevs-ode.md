# ODE (Open Dynamics Engine)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-3-Clause OR LGPL-2.1-or-later` · 🟢 active

> Long-lived C/C++ rigid-body dynamics engine with joints and built-in collision; Gazebo's fork ran slightly faster than Bullet in OSRF benchmarks.

| | |
|---|---|
| **Beats** | Bullet Physics (through Gazebo-classic's Bullet plugin); the same benchmark also runs DART and Simbody |
| **Claimed result** | ROSCon 2014 slide 16 (Benchmark 3, object stacking), time ratio real/sim: ODE 0.4, Bullet 0.5, DART 1.1, Simbody &gt;100 (ODE about 1.25x faster than Bullet, derived from page data). Result CSV test_results/BENCHMARK_boxes_model_count.csv (timeRatio, dt 0.0005): 1 box ODE 0.101879 vs Bullet 0.127279 (collision flag 0) and 0.109099 vs 0.129334 (flag 1); 101 boxes ODE 1.3357 vs Bullet 1.4384 (flag 1, 1.08x derived) but ODE 1.58186 vs Bullet 1.47622 (flag 0, ODE about 7% slower). |
| **Workload** | Time ratio (wall-clock time divided by simulated time, lower is faster; the inverse of the usual real-time factor) of rigid-body simulation inside Gazebo-classic: a stack of boxes with large inertia ratio (Benchmark 3, object stacking, ROSCon 2014 slide 16), and free-floating 1x4x9 boxes (Benchmark 1), 1 to 101 boxes in steps of 20, 10 s simulated at 0.0005 s step (Simbody at 0.001 s). |
| **Metric** | throughput |
| **Adoption** | 30 stars on the new GitHub home (project moved from Bitbucket odedevs/ode in 2026); physics backend supported by Gazebo-classic |
| **Last commit** | 2026-08-07 |
| **Links** | [repository](https://github.com/odedevs/ode) · [benchmark](https://raw.githubusercontent.com/scpeters/benchmark/HEAD/pdf/roscon2014_scpeters.pdf) |

## Verdict

Inside Gazebo-classic with OSRF's bundled ODE fork (not upstream), the ROSCon 2014 stacking slide reports a real-to-simulated time ratio of 0.4 for ODE vs 0.5 for Bullet, with no parameters given. The 2015 free-floating boxes CSV (0.0005 s step, 10 s simulated, one run per configuration, CPU and compiler unstated) has ODE faster in 10 of 12 configurations (1 box 0.102 vs 0.127) but slower at 81 and 101 boxes without collision shapes (101 boxes 1.582 vs 1.476), and the boxes never collide.

## Use it when

- Robot simulation with articulated mechanisms and a modest number of bodies (the benchmarks cover 1 to 101 boxes), especially if you already target Gazebo-classic, whose default engine is ODE.
- Embedding a stable, dependency-free physics library behind a C API in C or C++ code, with a choice of single or double precision and a BSD-3-Clause licence option.
- Interactive or near-real-time simulation where a fixed QuickStep iteration count (20 by default upstream, 50 under Gazebo's SDF defaults) is preferred to exact contact forces.
- Stacks and resting contact combined with auto-disable, the case the QuickStep documentation names as its strength.

## Skip it when

- Accuracy-critical contact: the QuickStep docs warn of poor accuracy for near-singular systems (high friction, strong motors, legged robots standing on the ground), and in the ROSCon 2014 stacking test Bullet showed lower stack position error than ODE.
- Very large collision scenes: hash-space collide2 recomputes and discards its hash table and degrades to O(n^2) (issue #34, open since 2014), and nested hash spaces with about 531,000 boxes hit an assertion in collision_space.cpp (issue #93, August 2026).
- Convex-heavy or heightfield-heavy scenes: open issues report too few convex-convex contact points (#56) and small spheres falling through convex heightfield edges (#71).
- When you need the benchmarked behaviour: the published numbers come from Gazebo's 2014-era fork with OSRF solver changes, while upstream has since changed QuickStep threading, constraint ordering and the box-plane collider.
- Reduced (generalized) coordinates for long kinematic chains: ODE uses maximal coordinates and relies on the iterative constraint solver to hold joints together, whereas Simbody and DART use generalized coordinates.

## How it is fast

dWorldQuickStep is an iterative projected Gauss-Seidel/SOR LCP solver whose cost is linear in constraint rows times a fixed iteration count (O(m\*N) time, O(m) memory) instead of the Dantzig big-matrix solve in dWorldStep, trading accuracy for bounded per-step cost. Bodies are grouped into islands that can be stepped on separate threads through ODE's threading interface, resting bodies can be auto-disabled, and broadphase uses simple, hash, quadtree or sweep-and-prune spaces. The Gazebo fork that was benchmarked added OSRF's own solver changes (inertia-ratio reduction, partial warm starting) described in the SIMPAR 2014 paper.

## Compared with alternatives

Pick ODE over Jolt Physics (the other catalogued rigid-body engine, faster than Bullet via Ammo.js only in a mixed result) when you need ODE's articulated-joint set, a plain C API, double precision or Gazebo-classic compatibility; for collision or distance queries alone, Coal (HPP-FCL) is the catalogued GJK option.

## Integration

| | |
|---|---|
| **Form** | shared lib (default BUILD_SHARED_LIBS=ON) or static lib |
| **Dependencies** | none required; bundles OPCODE, GIMPACT, libccd and OU; OpenGL and GLU only for the demos and DrawStuff |
| **Minimum toolchain** | CMake 3.10+; a C/C++ compiler (GCC, Clang, MSVC, MinGW); the build was set to C++11 in April 2026 (commit for #91) |
| **Platforms** | Windows (MSVC, MSYS2), Linux, macOS per the CI badges; 32- and 64-bit; single or double precision (double by default on 64-bit) |
| **Thread safety** | Call dInitODE2 and then dAllocateODEDataForThread in every thread that uses ODE; separate worlds can run in parallel; threaded collision of separate spaces needs the ODE_WITH_OU build option (TLS caches); with threaded stepping, body callbacks may be called from several threads |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw in the free-floating boxes benchmark (scpeters/benchmark boxes.cc at commit 55c3b05): boxes are spawned 1.8 m apart along y in a blank world with no ground plane and identical initial velocities, so they never touch; the 'collision' rows only add collision shapes to the broadphase and no contact is ever solved (the linear position error 0.0245 equals the analytic semi-implicit Euler error 0.5\*g\*dt\*t). Each configuration ran once, and ODE's own with/without-collision pairs differ by up to 18% in the wrong direction at 81 and 101 boxes, noise as large as the ODE-Bullet gap.
- What the box timings mostly measure is Gazebo's per-step overhead: one box costs about 51 us per step with ODE and 64 us with Bullet, while the marginal cost per extra box is similar (about 7.4 vs 6.7 us without collision shapes, 6.1 vs 6.5 us with them; derived from page data). The authors' Multibody 2015 slides summarise accuracy versus computational time as 'comparable', and the stacking slide (0.4 vs 0.5) states no stack size, step size or iteration count and has no CSV.
- Every number measures OSRF's ODE fork bundled in Gazebo-classic, not odedevs/ode: upstream defaults QuickStep to 20 iterations (Gazebo's SDF default is 50), keeps warm starting compiled out (#define WARM_STARTING commented in quickstep.cpp), has no inertia-ratio reduction, and since 2025 runs LCP solving single-threaded by default.
- dxHashSpace::collide() deliberately faults the host program when a scene is large enough to overflow its integer cell counters (2017 changelog), so check space sizing; a threaded-job data race (issue #70) was fixed only in July 2020, so use 0.16.2 or later when stepping with threads.

## Known shortcomings

- Gazebo-classic benchmark by OSRF (slide 16 and CSV): Gazebo always builds its bundled deps/opende fork, so the numbers measure OSRF's fork rather than upstream odedevs/ode; small mixed win (10 of 12 rows, 4-25% time ratio real/sim vs Bullet), no CPU or flags.
- Enricher: boxes.cc (commit 55c3b05) spawns boxes 1.8 m apart in a blank world with the same velocities, so no contact is ever solved and the timings are mostly Gazebo per-step overhead (51 vs 64 us at 1 box, similar marginal cost per box); each config ran once and ODE's own collision on/off pairs differ by up to 18% the wrong way, as big as the ODE-Bullet gap; the authors' Multibody 2015 slides call the engines 'comparable'. Upstream differs from the Gazebo fork (20 vs 50 iterations, warm start compiled out, no inertia-ratio reduction). Open issues #34 (hash space O(n^2)), #93 (assert at about 531k geoms).

## Caveats and trade-offs

The benchmark ran inside Gazebo-classic, which always builds and links its own bundled ODE copy (gazebo-classic deps/opende, headers gazebo/ode/ode.h, unconditional add_subdirectory(opende)); the slides themselves mention features only 'in our fork of ODE'. The measured ODE is therefore OSRF's Gazebo fork, not upstream odedevs/ode, and the measurer (Steven Peters, OSRF) maintains that fork, so this is not an independent measurement of this repo. Both engines run through Gazebo-classic wrappers, so Gazebo overhead is included. Repo scpeters/benchmark has 16 stars; no CPU model, compiler or flags are stated; results are dated about 2014-2015 (ROSCon 2014, Multibody 2015). The slide numbers are rounded to one decimal and sit next to a stack-position-error plot in which Bullet's error is lower than ODE's for top-link masses of 1 to 1000 kg, so the stacking speed result is not accuracy-matched. In the free-floating boxes CSV the accuracy columns of ODE and Bullet are close (same linear position error, angular momentum error 0.00643 vs 0.00626, energy error 0.00623 vs 0.00679). Result is mixed and small: ODE is faster than Bullet in 10 of 12 box-count configurations (by about 4 to 25%) but about 3.5 to 7% slower at 81 and 101 boxes with collision flag 0. The peer-reviewed Erez et al. ICRA 2015 comparison of Bullet, Havok, MuJoCo, ODE and PhysX and the Boeing and Braunl engine comparison exist but could not be opened (hosts blocked). ODE's own site (ode.org) was blocked and its README gives only the words 'fast, flexible, robust' with no numbers.

Maximal-coordinates rigid-body engine with impulse/iterative (quickstep) contact solver and built-in collision detection; favours speed and stability over physical accuracy; the benchmark's accuracy columns show ODE and Bullet at similar error levels for the box test (energy error 0.0062 vs 0.0068 for one box).

## Maintenance

Maintained but slow-moving: last tag 0.16.6 (2025-01-16), repository moved to GitHub in April 2026 with 26 open issues migrated, latest commit 2026-08-07; dual BSD-3-Clause/LGPL-2.1+ and dependency-free so easy to vendor, but its only speed evidence is a 2014-2015 measurement of Gazebo's fork in which the timed boxes never collide.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** ROSCon 2014 slide 16 and the CSV in scpeters/benchmark (Apache-2.0, 16 stars) show the time ratio numbers, and the harness is public, but no CPU model, compiler or flags are given, it is a conference talk not a peer-reviewed paper, and it was run by OSRF, which maintains the ODE fork it measured; C.
- **Verifier notes:** Slide 16 (0.4 vs Bullet 0.5) and all CSV numbers verified (101 boxes flag 0: ODE 1.58186 vs Bullet 1.47622, ODE slower). New shortcoming: Gazebo-classic always builds its bundled deps/opende fork, so the numbers measure OSRF's ODE fork, not upstream odedevs/ode (Topaz fork precedent; already C). Metadata checked: BSD-3-Clause OR LGPL-2.1-or-later, 30 stars, not archived, last commit 2026-08-07; the 2026 Bitbucket-to-GitHub move date was not independently checked.
- **Fields the verifier corrected:** `workload`, `caveats`
- **Shortcomings recorded by:** OSRF Gazebo benchmark (verifier); enricher harness reading
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/scpeters/benchmark/HEAD/pdf/roscon2014_scpeters.pdf>
  - <https://raw.githubusercontent.com/scpeters/benchmark/HEAD/test_results/BENCHMARK_boxes_model_count.csv>
  - <https://github.com/scpeters/benchmark>
  - <https://github.com/odedevs/ode>
  - <https://github.com/odedevs/ode/commits>
  - <https://github.com/gazebosim/gazebo-classic/tree/gazebo11/deps/opende>
  - <https://raw.githubusercontent.com/gazebosim/gazebo-classic/gazebo11/deps/CMakeLists.txt>
  - <https://raw.githubusercontent.com/gazebosim/gazebo-classic/gazebo11/gazebo/physics/ode/ode_inc.h>
- **Sources the enricher read:**
  - <https://github.com/odedevs/ode>
  - <https://github.com/odedevs/ode/commits/master>
  - <https://github.com/odedevs/ode/tags>
  - <https://github.com/odedevs/ode/issues>
  - <https://github.com/odedevs/ode/issues/93>
  - <https://github.com/odedevs/ode/issues/34>
  - <https://raw.githubusercontent.com/odedevs/ode/HEAD/README.md>
  - <https://raw.githubusercontent.com/odedevs/ode/HEAD/CHANGELOG.txt>
  - <https://raw.githubusercontent.com/odedevs/ode/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/odedevs/ode/HEAD/include/ode/objects.h>
  - <https://raw.githubusercontent.com/odedevs/ode/HEAD/include/ode/odeinit.h>
  - <https://raw.githubusercontent.com/odedevs/ode/HEAD/include/ode/threading.h>
  - <https://raw.githubusercontent.com/odedevs/ode/HEAD/ode/src/quickstep.cpp>
  - <https://raw.githubusercontent.com/odedevs/ode/HEAD/ode/src/step.cpp>
  - <https://github.com/scpeters/benchmark/tree/master>
  - <https://github.com/scpeters/benchmark/tree/master/test_results>
  - <https://github.com/scpeters/benchmark/tree/master/pdf>
  - <https://github.com/scpeters/benchmark/commits/master/test_results/BENCHMARK_boxes_model_count.csv>
  - <https://raw.githubusercontent.com/scpeters/benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/scpeters/benchmark/HEAD/pdf/roscon2014_scpeters.pdf>
  - <https://raw.githubusercontent.com/scpeters/benchmark/HEAD/pdf/multibody2015_scpeters.pdf>
  - <https://raw.githubusercontent.com/scpeters/benchmark/HEAD/pdf/simpar2014.pdf>
  - <https://raw.githubusercontent.com/scpeters/benchmark/HEAD/test_results/BENCHMARK_boxes_model_count.csv>
  - <https://raw.githubusercontent.com/scpeters/benchmark/HEAD/test_results/BENCHMARK_boxes_dt.csv>
  - <https://raw.githubusercontent.com/scpeters/benchmark/HEAD/boxes.cc>
  - <https://raw.githubusercontent.com/scpeters/benchmark/HEAD/boxes.hh>
  - <https://raw.githubusercontent.com/scpeters/benchmark/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/scpeters/benchmark/55c3b05/boxes.cc>
  - <https://raw.githubusercontent.com/gazebosim/sdformat/sdf9/sdf/1.6/physics.sdf>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/odedevs/ode`) · [data/wave8/enrich/raw/github_com_odedevs_ode.json](../../../data/wave8/enrich/raw/github_com_odedevs_ode.json) (enrichment confidence 0.75)

</details>
