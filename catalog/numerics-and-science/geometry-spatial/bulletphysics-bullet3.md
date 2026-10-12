# Bullet Physics (bullet3)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Zlib` · 🟢 active

> Zlib-licensed C++ rigid/soft-body physics and collision SDK (PyBullet's core); beat DART and Simbody inside Gazebo-classic, not ODE.

| | |
|---|---|
| **Beats** | DART (also Simbody; ODE for comparison) |
| **Claimed result** | Gazebo-classic boxes benchmark: Bullet about 3.0x faster than DART 4.3.4 with collisions off (flag 0); the 5.0x flag-1 figure rests on DART's missing broadphase and bug dart#424; Bullet is slower than ODE in 10 of 12 rows and only 1.04x faster at 81 boxes. |
| **Workload** | Gazebo-classic free-floating rigid boxes benchmark (1x4x9 boxes tumbling, 1 to 101 boxes in steps of 20, collision flag 0 and 1): ratio of wall-clock time to simulated time (timeRatio, lower is faster) for 10 s simulated at a 0.0005 s step (Simbody at 0.001 s), engine selected inside Gazebo-classic. |
| **Metric** | throughput |
| **Adoption** | 14.8k stars; used in games, VFX, robotics (PyBullet) and Gazebo |
| **Last commit** | 2026-10-09 |
| **Links** | [repository](https://github.com/bulletphysics/bullet3) · [benchmark](https://raw.githubusercontent.com/scpeters/benchmark/HEAD/test_results/BENCHMARK_boxes_model_count.csv) |

## Verdict

In OSRF's 2015 Gazebo-classic boxes benchmark (single runs, 10 s simulated at 0.0005 s steps, CPU, compiler and engine versions unstated) Bullet's wall/sim time ratio at 101 boxes was 1.44-1.48 against DART 4.3.4's 4.37-7.23 (3.0x to 5.0x), Simbody's 1.84-1.87 (Simbody at a 0.001 s step) and ODE's 1.34-1.58; the boxes never collide, and DART's large gap comes largely from its Gazebo collision path having no broadphase. ROSCon 2014's stacking slide gives ODE 0.4, Bullet 0.5, DART 1.1, Simbody over 100 with no parameters.

## Use it when

- Games, VR and interactive tools that need a mature, permissively licensed (zlib) rigid-body plus collision library with convex, mesh and compound shapes and a long track record.
- Robotics and RL prototyping from Python via PyBullet (pip wheels, 3.2.7 released 2025-01-30), including URDF/SDF loading and Featherstone multibodies.
- Scenes with tens to a hundred-plus free bodies inside Gazebo-classic where you would otherwise run DART or Simbody: in the 2015 boxes data Bullet was 1.08x to 5.0x faster than DART and 1.25x to 1.30x faster than Simbody at 81 to 101 boxes.
- Projects that want soft bodies, vehicles or GPU-experimental collision (OpenCL pipeline) in the same codebase as rigid bodies.

## Skip it when

- If ODE is an option: in the same Gazebo benchmark ODE was faster in 10 of 12 box rows (1 box 0.102 vs 0.127 time ratio) and in the ROSCon 2014 stacking slide (0.4 vs 0.5); Bullet led only at 81 and 101 boxes without collision shapes, by about 4% and 7%.
- Single small scenes where per-step overhead dominates: in the single-box step-size sweep Bullet was slower than ODE at every step size (0.129 vs 0.112 at 0.0005 s) and only about 8% faster than DART.
- Large new game or multi-core projects: the catalogued Jolt Physics beats Bullet (via Ammo.js) on settled scenes, and Bullet's multithreaded build has open reports of mutex contention in the collision algorithm pool (#4347) and release-mode crashes (#4292).
- If you need active upstream support: the issue tracker is closed to support questions (README), with 268 open issues and 165 open PRs; the last merged code PRs date from 2024-04-09.
- Stiff articulated robots in maximal coordinates: joint damping is explicit in Gazebo's Bullet path (ROSCon 2014 slide), so stability needs small steps; use btMultiBody or a generalized-coordinate engine instead.

## How it is fast

The rigid-body path is an iterative sequential-impulse (projected Gauss-Seidel) constraint solver with a fixed iteration count, so cost per step grows roughly linearly with contacts and bodies; broadphase uses a dynamic AABB tree (btDbvtBroadphase, the one Gazebo-classic's plugin selects), and simulation islands let resting groups sleep. An optional multithreaded world (btDiscreteDynamicsWorldMt with OpenMP, TBB or PPL task schedulers) solves islands in parallel. In the benchmark the advantage over DART is mostly scaling: Bullet's marginal cost was about 6.5-6.7 us per extra box per step against DART's 21-35 us (derived from page data), while the fixed per-step cost through Gazebo was similar (about 64 us vs 68-71 us).

## Compared with alternatives

Pick Bullet over ODE when you need soft bodies, convex and concave mesh collision, Featherstone multibodies or PyBullet, accepting that ODE was a little faster in the same Gazebo benchmark; over Simbody when per-step speed for many free bodies matters more than generalized-coordinate accuracy. For a new multi-core game engine, Jolt Physics is the catalogued faster rigid-body choice.

## Integration

| | |
|---|---|
| **Form** | static lib by default (BUILD_SHARED_LIBS OFF); shared lib optional; vcpkg port and pip wheel (pybullet) |
| **Dependencies** | none for the core libraries (LinearMath, BulletCollision, BulletDynamics, BulletSoftBody); OpenGL only for the example browser; optional OpenMP, TBB or PPL for multithreading; Python for PyBullet |
| **Minimum toolchain** | a C++03 compiler per the README; CMake 3.5+ (or the bundled premake4) |
| **Platforms** | Windows, Linux, macOS, iOS, Android per the README; single precision by default (USE_DOUBLE_PRECISION option); SSE is auto-enabled only for 32-bit-float MSVC builds and x86 macOS, NEON only for clang on Apple ARM |
| **Thread safety** | Single-threaded by default; build with BULLET2_MULTITHREADING (BT_THREADSAFE) and use btDiscreteDynamicsWorldMt with a task scheduler (OpenMP, TBB or PPL, up to 64 threads) for parallel island solving; btMutex helpers called from code compiled without BT_THREADSAFE race (btThreads.h warning) |
| **Drop-in for the baseline** | partial: inside Gazebo-classic it is a one-flag engine swap (gazebo -e bullet), but as a library its API is unrelated to DART's, and it uses maximal rather than generalized coordinates |

## Gotchas

- Harness flaw: in scpeters/benchmark boxes.cc (commit 55c3b05, the code behind the 2015 CSV) every box gets the same initial linear and angular velocity and spawns 1.8 m apart along y in a blank world, so the boxes never touch; the 'collision 1' rows only add shapes to the broadphase and no contact is solved. Each configuration ran once, with no CPU, compiler, flags, or Bullet version recorded, and timing goes through Gazebo's world-&gt;Step, so Gazebo's roughly 50-70 us fixed per-step overhead is a large share of every row.
- Baseline handicap: the DART rows are DART 4.3.4 (dart issue #424, opened by the benchmark author in June 2015) with a known angular momentum conservation bug (relative error 2.2 to 2.5 in every tumbling-box DART row against 0.006 for Bullet), and the authors' Multibody 2015 slides say DART's collision checker in Gazebo 'doesn't use a broadphase'. That explains DART's superlinear scaling and why adding never-touching collision shapes slows DART by 1.65x at 101 boxes while Bullet is unchanged; the headline 5.0x over DART (flag 1) is mostly that missing broadphase, and the 3.0x with flag 0 is the cleaner figure.
- Linux builds get no SSE by default: btScalar.h defines BT_USE_SSE only for float MSVC builds and x86 macOS, so a GCC/Clang build on Linux (as Gazebo on Ubuntu used) runs scalar vector math unless you define it yourself; double-precision builds never get SSE.
- CVE-2025-8854 (stack-based overflow in the VHACD OFF-file parser LoadOFF, reachable through PyBullet's vhacd; reported as affecting versions up to 3.25, snippet-only via a search) affects the tools, not the core dynamics; avoid feeding untrusted mesh files to the VHACD utilities on old versions.

## Known shortcomings

- Downgraded within C: Gazebo-classic boxes benchmark shows Simbody faster at 1 box (half the steps) and the 81-box win over ODE is 1.04x, not 1.07x; slower than ODE in 10 of 12 rows and in stacking; no CPU, compiler or engine versions; Gazebo overhead included. Shares its benchmark with the ODE and Simbody entries.
- Enricher: scpeters boxes.cc@55c3b05 spawns boxes 1.8 m apart with identical velocities so they never touch ('collision 1' rows add broadphase shapes only), one run per row, Gazebo per-step overhead (about 64 us) dominates; the DART rows are DART 4.3.4 with the angular-momentum bug dart#424 (relative error 2.2-2.5) and, per the authors' 2015 Multibody slides, DART's Gazebo collision checker has no broadphase, so the 5.0x (flag 1) figure is a crippled baseline and 3.0x (flag 0) is the cleaner figure; ODE is faster than Bullet in most rows. Linux builds get no SSE by default (btScalar.h); CVE-2025-8854 in VHACD LoadOFF (snippet); maintenance mode, last code PRs 2024-04-09.

## Caveats and trade-offs

Numbers are from a third-party Gazebo-classic benchmark by OSRF engineers (repo scpeters/benchmark, Apache-2.0, 16 stars; README asks for Gazebo 6 or later and states no compiler, flags, CPU, or Bullet/DART versions) and the ROSCon 2014 slides (pdf/roscon2014_scpeters.pdf), roughly 2014-2015 vintage; Bullet runs through Gazebo-classic's Bullet plugin, so Gazebo overhead is included and the measured Bullet is whatever version Gazebo linked then, not the current bullet3 tree. The wins are over DART and Simbody, not over ODE (Gazebo's default engine): ODE is faster than Bullet in 10 of 12 box configurations and in the stacking test (0.4 vs 0.5); Bullet wins only at 81 and 101 boxes with collision flag 0, by about 4% and 7%. Simbody beats Bullet at 1 box (about 3%) even with a 0.001 s step against 0.0005 s, so the Simbody rows are not step-matched; DART's angular momentum error in the same CSV is 2.36521 against 0.00626 for Bullet, so the DART rows are not accuracy-matched either. Same benchmark source as the catalog's ODE and Simbody entries. The bullet3 README and docs carry no benchmark numbers of their own. A search summary (snippet only) of Erez, Tassa and Todorov, ICRA 2015 (Bullet, Havok, MuJoCo, ODE, PhysX) says no gaming engine led clearly on speed; the paper itself was blocked. Last commits 2026-10-09 are README-only; the last non-README change is 2025-10-22 (add pyproject.toml), the last code PR merges 2024-04-09. [retier] Boxes never touch (spawned 1.8 m apart with identical velocities); one run per row; Gazebo per-step overhead about 64 us dominates; Linux builds have no SSE by default; maintenance mode since 2024-04.

Maximal-coordinate rigid-body solver with impulse contacts and explicit joint damping (ROSCon 2014 slide), so stiff articulated robots need small steps; broad feature set (soft bodies, vehicles, PyBullet bindings). The GitHub issue tracker is closed to support questions (README).

## Maintenance

Maintenance mode: recent commits are README and packaging changes (last 2026-10-09, pyproject.toml 2025-10-22), the last code PRs merged 2024-04-09 and the issue tracker is closed to support questions, but it is zlib-licensed, dependency-free and widely packaged (vcpkg, pip) so easy to adopt; its only speed evidence is a 2015 third-party Gazebo benchmark whose boxes never collide and whose DART baseline lacked a broadphase and had a momentum bug, which argues for tier D or for re-baselining the entry on ODE, where Bullet is not faster.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification C, tier now C.
- **Tier reason:** Third-party Gazebo-classic benchmark (scpeters/benchmark boxes test, CSV test_results/BENCHMARK_boxes_model_count.csv and pdf/roscon2014_scpeters.pdf) with public code but no CPU model, compiler, flags or engine versions, from a 16-star repo that is not a well-known suite; same evidence and tier as the catalog's ODE and Simbody entries.
- **Verifier notes:** Real third-party numbers that match the CSV, but the claim overstated two details: Bullet is not faster than Simbody in all 12 configurations (Simbody wins at 1 box, both collision flags) and the 81-box win over ODE is about 1.04x, not 1.07x; tier stays C. Shortcomings: slower than ODE (Gazebo's default) in 10 of 12 box rows and in stacking; no CPU, compiler, flags or engine versions; Gazebo overhead included; DART and Simbody rows not accuracy- or step-matched. Not a duplicate; shares its benchmark with the ODE and Simbody entries.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-175 (wave 8); enricher w8 pair-026
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/scpeters/benchmark/HEAD/test_results/BENCHMARK_boxes_model_count.csv>
  - <https://raw.githubusercontent.com/scpeters/benchmark/HEAD/pdf/roscon2014_scpeters.pdf>
  - <https://github.com/scpeters/benchmark>
  - <https://github.com/bulletphysics/bullet3>
  - <https://github.com/bulletphysics/bullet3/commits>
- **Sources the enricher read:**
  - <https://github.com/bulletphysics/bullet3>
  - <https://github.com/bulletphysics/bullet3/commits/master>
  - <https://github.com/bulletphysics/bullet3/issues?q=is%3Aissue+is%3Aopen+performance>
  - <https://raw.githubusercontent.com/bulletphysics/bullet3/HEAD/README.md>
  - <https://raw.githubusercontent.com/bulletphysics/bullet3/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/bulletphysics/bullet3/HEAD/VERSION>
  - <https://raw.githubusercontent.com/bulletphysics/bullet3/HEAD/setup.py>
  - <https://raw.githubusercontent.com/bulletphysics/bullet3/HEAD/src/LinearMath/btScalar.h>
  - <https://raw.githubusercontent.com/bulletphysics/bullet3/HEAD/src/LinearMath/btThreads.h>
  - <https://raw.githubusercontent.com/bulletphysics/bullet3/HEAD/src/BulletDynamics/Dynamics/btDiscreteDynamicsWorldMt.h>
  - <https://pypi.org/pypi/pybullet/json>
  - <https://raw.githubusercontent.com/scpeters/benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/scpeters/benchmark/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/scpeters/benchmark/HEAD/boxes.cc>
  - <https://raw.githubusercontent.com/scpeters/benchmark/55c3b05/boxes.cc>
  - <https://raw.githubusercontent.com/scpeters/benchmark/HEAD/test_results/BENCHMARK_boxes_model_count.csv>
  - <https://raw.githubusercontent.com/scpeters/benchmark/HEAD/test_results/BENCHMARK_boxes_dt.csv>
  - <https://raw.githubusercontent.com/scpeters/benchmark/HEAD/pdf/roscon2014_scpeters.pdf>
  - <https://raw.githubusercontent.com/scpeters/benchmark/HEAD/pdf/multibody2015_scpeters.pdf>
  - <https://raw.githubusercontent.com/gazebosim/gazebo-classic/gazebo11/gazebo/physics/bullet/BulletPhysics.cc>
  - <https://github.com/dartsim/dart/issues/424>
  - WebSearch: bullet3 bulletphysics CVE vulnerability heap buffer overflow (snippets for CVE-2025-8854)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/bulletphysics/bullet3`) · [data/wave8/enrich/raw/github_com_bulletphysics_bullet3.json](../../../data/wave8/enrich/raw/github_com_bulletphysics_bullet3.json) (enrichment confidence 0.75)

</details>
