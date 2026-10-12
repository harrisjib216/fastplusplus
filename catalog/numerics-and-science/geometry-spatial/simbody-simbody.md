# Simbody

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Featherstone-style O(n) multibody dynamics library; measured slower than ODE and Bullet for free boxes, so a not-faster entry.

| | |
|---|---|
| **Beats** | ODE and Bullet Physics, through Gazebo-classic's ODE and Bullet plugins (DART was measured in the same run) |
| **Claimed result** | No clear speed advantage over ODE or Bullet; Simbody is slower from 21 boxes up. Time ratio, 101 boxes (CSV): Simbody 1.84 (collision 0) and 1.87 (collision 1) vs ODE 1.58 and 1.34 vs Bullet 1.48 and 1.44, although Simbody ran with a 0.001 s step and ODE and Bullet with 0.0005 s; 1 box: Simbody 0.124 and 0.126 vs ODE 0.102 and 0.109 vs Bullet 0.127 and 0.129 (Simbody about 3% ahead of Bullet only there, and with half as many steps). ROSCon 2014 object-stacking slide, real/sim: ODE 0.4, Bullet 0.5, DART 1.1, Simbody &gt;100. Simbody was faster than DART in the box test: 101 boxes 1.84 vs 4.37 (about 2.4x, derived from page data) and 1.87 vs 7.23 (about 3.9x, derived). |
| **Workload** | Time ratio (wall-clock seconds per simulated second, timeRatio = wallTime / simTime over 10 s of simulated time; lower is faster) in Gazebo-classic: free-floating 1x4x9 boxes, 1 to 101 boxes, with collision off and on; a time-step sweep (0.0001 to 0.001 s, 1 box); plus an object-stacking scene with a large inertia ratio (ROSCon 2014 slide). |
| **Metric** | throughput |
| **Adoption** | 2.6k stars; the physics engine behind OpenSim and an option in Gazebo |
| **Last commit** | 2026-09-28 |
| **Links** | [repository](https://github.com/simbody/simbody) · [benchmark](https://raw.githubusercontent.com/scpeters/benchmark/HEAD/test_results/BENCHMARK_boxes_model_count.csv) |

## Verdict

The Gazebo maintainers' benchmark (scpeters/benchmark boxes.cc, results committed 2015) ran free-floating boxes through Gazebo-classic plugins: at 101 boxes Simbody's wall/sim time ratio was 1.84 to 1.87 against ODE 1.34 to 1.58 and Bullet 1.44 to 1.48 (Simbody at twice the step size), and at equal step size it was about 2.3x slower than ODE; a stacking scene ran over 100x real time against 0.4 for ODE. It beat DART only (1.84 vs 4.37). No CPU, compiler or flags were stated.

## Use it when

- Long articulated chains and closed loops (musculoskeletal models, robot arms, legged robots) where drift-free generalized coordinates and implicit joint damping matter more than raw steps per second.
- Biomechanics work that already uses OpenSim, or molecular multibody models in the MMB style with thousands of bodies linked by joints.
- Simulations that need error-controlled accuracy (variable-step Runge-Kutta, Merson or error-controlled semi-explicit Euler) rather than a fixed game-engine step.
- Mixed forward/inverse dynamics, prescribed motion or optimization (gradient, interior point, CMA-ES) around one dynamics model.

## Skip it when

- Many free bodies or piles: in the Gazebo boxes benchmark Simbody's time ratio at 101 boxes was 1.84 to 1.87 against ODE 1.34 to 1.58 and Bullet 1.44 to 1.48, even with twice the step size.
- Stiff contact and stacking: the ROSCon 2014 stacking scene ran at more than 100x real time per simulated second, against 0.4 for ODE and 0.5 for Bullet (compliant contact with variable steps).
- Real-time game physics with fixed steps and rigid impulse contact: Jolt Physics, PhysX or Bullet fit that shape better.
- Projects that cannot take a LAPACK/BLAS dependency or a compiled shared-library build (no header-only option).
- Toolchains stuck below C++20 if you track master: the CHANGELOG for 3.9 (in development) raises the required level from C++11 to C++20; the 3.8 release (May 2025) still targets C++11.

## How it is fast

Its speed argument is algorithmic: O(n) recursive (Featherstone-style) forward dynamics in internal coordinates, so an n-joint chain needs no constraint solve and has no joint drift, unlike maximal-coordinate engines (ODE, Bullet) that solve 6n coordinates plus constraints. No project page gives speed numbers for this; the only cross-engine measurement found (Gazebo maintainers, 2014-2015) covers free-floating boxes and a stacking scene, which do not exercise that advantage. Release builds use -O2 (CMake forces it; an optional -m&lt;instruction set&gt; via BUILD_INST_SET).

## Compared with alternatives

Pick Simbody over ODE or Jolt Physics when the model is an articulated mechanism (skeleton, robot) where generalized coordinates, drift-free joints and error-controlled accuracy matter; for many free bodies, stacking or game-style real-time contact, ODE, Bullet or Jolt Physics were faster in every measurement found.

## Integration

| | |
|---|---|
| **Form** | shared lib (three libraries: SimTKcommon, SimTKmath, Simbody; static build optional) |
| **Dependencies** | LAPACK 3.6.0+ and BLAS; optional FreeGLUT, Xi and Xmu for the visualizer; CMake 3.21+ to build |
| **Minimum toolchain** | README: GCC 4.9+, Clang 3.4+, Apple Clang 8+, VS 2015/2017/2019 (3.8 release); master (3.9 in development) requires C++20 per CHANGELOG |
| **Platforms** | Windows, macOS, Linux, FreeBSD; packaged in apt, Homebrew, Conda and vcpkg; no SIMD requirement |
| **Thread safety** | not documented as a whole; System and State are separate objects, the CHANGELOG lists a ParallelExecutor, parallelizable forces and a mutex state lock, and the CMA-ES optimizer is multithreaded |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw behind the equal-step numbers: Gazebo-classic's Simbody plugin hard-codes SimTK::SemiExplicitEuler2Integrator (integratorType is a TODO, not read from SDF), an error-controlled integrator that takes two half-steps plus one full step per step for Richardson error estimates. Simbody's own header says it 'needs to run at twice the step size' for performance equal to the fixed-step method that ODE and Bullet use, so the 2.3x gap at dt 0.0005 (time ratio 0.259 vs ODE 0.112) is largely the integrator choice; Simbody's fixed-step SemiExplicitEulerIntegrator was never measured.
- At the step sizes the benchmark treats as equal accuracy (Simbody 0.001 s, others 0.0005 s, all at 0.0245 max position error) Simbody is about equal at 1 box (0.124 vs ODE 0.102, Bullet 0.127) and 16 to 40% slower than ODE at 21 to 101 boxes (derived from page data). Each row is a single run with no CPU, compiler or flags, and timing goes through Gazebo's world-&gt;Step, so Gazebo overhead is included.
- The CSVs were last committed on 2015-06-29; boxes.cc was rewritten in 2024 (dynamic SDF generation, then MCAP logging of every step's pose and twist inside the timed loop), so rerunning today's harness measures something different from the published numbers.
- Debug builds are more than 10x slower (README); link only optimized (Release or RelWithDebInfo) libraries when timing.

## Known shortcomings

- Not faster: in the scpeters/benchmark Gazebo-classic CSV (2014-2015, no compiler, flags or CPU) Simbody is slower than ODE and Bullet at 101 boxes (1.84/1.87 vs 1.58/1.34 and 1.48/1.44 s) and beats only DART; at the same step size (dt 0.0005) it is about 2.3x slower than ODE (derived from page data); its 0.001 s step was chosen to match accuracy. Kept as a documented not-faster entry.
- Harness flaw in the Gazebo-classic physics benchmark: SimbodyPhysics.cc hard-codes SemiExplicitEuler2Integrator, an error-controlled integrator that takes two substeps per step (Simbody's own header says it must run at twice the step size to match fixed-step Euler), so the 2.3x equal-dt loss to ODE comes mostly from the integrator choice and Simbody's fixed-step integrator was never measured. At equal-accuracy steps Simbody is still 16-40% slower than ODE from 21 to 101 boxes. The CSVs date from 2015; boxes.cc was rewritten in 2024 and now logs MCAP inside the timed loop, so a rerun would not reproduce them.

## Caveats and trade-offs

The README's only performance words are 'high-performance' and O(n) generalized-coordinate dynamics (no numbers), and no reachable benchmark shows Simbody faster than ODE or Bullet; this record documents that it was measured slower or at best equal, so it belongs as a not-faster entry. The measurements come from the Gazebo maintainers' physics benchmark (https://github.com/scpeters/benchmark, Apache-2.0, boxes.cc with GoogleTest and CMake against Gazebo 6; slides pdf/roscon2014_scpeters.pdf and pdf/multibody2015_scpeters.pdf from ROSCon 2014 and ECCOMAS Multibody 2015), results dated about 2014 to 2015 with no CPU model, compiler or flags (the 2015 slides themselves list 'run timing benchmarks on same hardware' as an open item), and the engines run through Gazebo-classic wrappers, so Gazebo overhead is included. Simbody ran with a 0.001 s step and ODE and Bullet with 0.0005 s; the Multibody 2015 slides say this was deliberate ('timestep chosen to give equal accuracy (larger timestep for simbody)', since Simbody takes an extra half-step to estimate error), and the CSV shows the same max position error (0.0245) for all three at those settings. At equal step size Simbody is much slower: in BENCHMARK_boxes_dt.csv (1 box, collision on, complex model, dt 0.0005) Simbody's time ratio is 0.259 vs ODE 0.112 and Bullet 0.129, about 2.3x slower than ODE (derived from page data), though with half the position error (0.01225 vs 0.0245). The 2015 slides summarise accuracy versus computational time as 'comparable'. The stacking slide (real/sim: ODE 0.4, Bullet 0.5, DART 1.1, Simbody &gt;100) gives no explanation or accuracy pairing. Simbody's strengths (O(n) multibody dynamics, accuracy for articulated systems) were not what this speed test targets; the Simbody paper and theory manual were not reachable. The only speed win in this data is over DART, which is not the category baseline. [retier] Gazebo-classic SimbodyPhysics.cc hard-codes SemiExplicitEuler2Integrator (error-controlled, two substeps per step; Simbody's header says it needs twice the step size to match fixed-step Euler), so the 2.3x equal-dt loss to ODE is mostly integrator choice; at equal-accuracy steps Simbody is 16-40% slower than ODE (21 to 101 boxes). 2015 CSVs; boxes.cc rewritten in 2024 (logs MCAP inside the timed loop), not reproducible.

Generalized (internal) coordinates with O(n) forward dynamics, so articulated chains have no constraint drift and implicit joint damping; it suits biomechanics and long chains rather than piles of free bodies. Contact is a compliant, force-based model with variable step size, which is slower for stiff stacking.

## Maintenance

Actively maintained (last commit 2026-09-28, release 3.8 in May 2025, 3.9 in development), Apache-2.0 and widely packaged, so easy to adopt for articulated-body work, but it is catalogued as a not-faster entry against ODE and Bullet.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The Gazebo maintainers' public benchmark (scpeters/benchmark boxes.cc, results in test_results/BENCHMARK_boxes_model_count.csv and BENCHMARK_boxes_dt.csv) compares Simbody with ODE, Bullet and DART, but states no compiler, flags or CPU model, so it cannot be A; it is an independent measurement but shows no win over ODE or Bullet (only over DART), so it stays at C as a documented not-faster entry.
- **Verifier notes:** All numbers in claimed_speedup match the CSV rows (Simbody 1.84/1.87 vs ODE 1.58/1.34, Bullet 1.48/1.44, DART 4.37/7.23 at 101 boxes; 1-box rows and the ROSCon stacking slide also match). Shortcomings to record: not faster than ODE or Bullet (slower from 21 boxes up, about 2.3x slower than ODE at equal step size, roughly equal at equal accuracy), stacking scene over 100x real time vs 0.4 for ODE, no compiler/flags/CPU, 2014-2015 Gazebo-classic wrapper measurements. Metadata checked: Apache-2.0, 2.6k stars, 496 forks, not archived, last commit 2026-09-28 (active).
- **Fields the verifier corrected:** `workload`, `caveats`
- **Shortcomings recorded by:** scpeters/benchmark CSV (verifier, not faster); enricher (wave 8)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/scpeters/benchmark/HEAD/test_results/BENCHMARK_boxes_model_count.csv>
  - <https://raw.githubusercontent.com/scpeters/benchmark/HEAD/test_results/BENCHMARK_boxes_dt.csv>
  - <https://raw.githubusercontent.com/scpeters/benchmark/HEAD/pdf/roscon2014_scpeters.pdf>
  - <https://raw.githubusercontent.com/scpeters/benchmark/HEAD/pdf/multibody2015_scpeters.pdf>
  - <https://raw.githubusercontent.com/scpeters/benchmark/HEAD/pdf/simpar2014.pdf>
  - <https://raw.githubusercontent.com/scpeters/benchmark/HEAD/pdf/timeRatioDtComplex.pdf>
  - <https://raw.githubusercontent.com/scpeters/benchmark/HEAD/pdf/modelCountTimeCollision.pdf>
  - <https://github.com/scpeters/benchmark>
  - <https://github.com/scpeters/benchmark/tree/master/pdf>
  - <https://github.com/scpeters/benchmark/tree/master/test_results>
  - <https://github.com/simbody/simbody>
  - <https://github.com/simbody/simbody/commits>
- **Sources the enricher read:**
  - <https://github.com/simbody/simbody>
  - <https://github.com/simbody/simbody/commits>
  - <https://github.com/simbody/simbody/issues?q=is%3Aissue+performance>
  - <https://github.com/simbody/simbody/issues/640>
  - <https://raw.githubusercontent.com/simbody/simbody/HEAD/README.md>
  - <https://raw.githubusercontent.com/simbody/simbody/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/simbody/simbody/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/simbody/simbody/HEAD/CMakePresets.json>
  - <https://raw.githubusercontent.com/simbody/simbody/HEAD/SimTKmath/Integrators/include/simmath/SemiExplicitEuler2Integrator.h>
  - <https://raw.githubusercontent.com/simbody/simbody/HEAD/SimTKmath/Integrators/include/simmath/SemiExplicitEulerIntegrator.h>
  - <https://raw.githubusercontent.com/gazebosim/gazebo-classic/gazebo11/gazebo/physics/simbody/SimbodyPhysics.cc>
  - <https://raw.githubusercontent.com/scpeters/benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/scpeters/benchmark/HEAD/boxes.cc>
  - <https://raw.githubusercontent.com/scpeters/benchmark/HEAD/test_results/BENCHMARK_boxes_model_count.csv>
  - <https://raw.githubusercontent.com/scpeters/benchmark/HEAD/test_results/BENCHMARK_boxes_dt.csv>
  - <https://raw.githubusercontent.com/scpeters/benchmark/HEAD/pdf/roscon2014_scpeters.pdf>
  - <https://raw.githubusercontent.com/scpeters/benchmark/HEAD/pdf/multibody2015_scpeters.pdf>
  - <https://github.com/scpeters/benchmark/commits/master/boxes.cc>
  - <https://github.com/scpeters/benchmark/commits/master/test_results/BENCHMARK_boxes_model_count.csv>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/simbody/simbody`) · [data/wave8/enrich/raw/github_com_simbody_simbody.json](../../../data/wave8/enrich/raw/github_com_simbody_simbody.json) (enrichment confidence 0.75)

</details>
