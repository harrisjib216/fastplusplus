# Jolt Physics

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Multicore C++ rigid-body physics and collision library; as single-threaded wasm it beats Ammo.js (Bullet) once bodies sleep, not while they collide.

| | |
|---|---|
| **Beats** | Bullet Physics (via Ammo.js, the Emscripten build of Bullet) |
| **Claimed result** | Mixed. Jolt faster: settled and asleep boxes 0.09 ms vs 0.95 ms (about 10.6x, derived from page data); boxes and spheres with the spheres still rolling 3.46 ms vs 5.86 ms (about 1.7x, derived); boxes with collisionstart listeners, settled 1.13 ms vs 2.82 ms (about 2.5x, derived). Jolt slower or level: boxes falling and colliding 5.76 ms vs 4.16 ms (Jolt about 1.4x slower, derived); boxes and spheres falling 4.44 ms vs 4.33 ms; listeners, falling 6.81 ms vs 6.32 ms. PR text: Jolt's own step is about 20% slower than Ammo's while bodies are colliding (4.94 ms with no contact listener). |
| **Workload** | Rigid-body step time in ms per physics step (RigidBodyComponentSystem#step(1/60)) for 400 boxes or boxes and spheres dropped on a floor, run in Node.js, minimum of 5 runs, Jolt (single-threaded WebAssembly build from jolt-physics 1.1.0 npm) against Ammo.js inside the PlayCanvas engine. |
| **Metric** | latency |
| **Compiler and flags** | Jolt: the single-threaded wasm build from the jolt-physics 1.1.0 npm package (vendored in examples/assets/wasm/jolt of the PR). Ammo.js build and version, Node.js version and compiler flags not stated. |
| **Adoption** | 11.7k stars; used in Horizon Forbidden West and Death Stranding 2 |
| **Last commit** | 2026-10-04 |
| **Links** | [repository](https://github.com/jrouwe/JoltPhysics) · [benchmark](https://github.com/playcanvas/engine/pull/9581) |

## Verdict

PlayCanvas engine PR #9581 (open, third party) timed RigidBodyComponentSystem#step(1/60) in Node.js for 400 bodies, minimum of 5 runs, with Jolt as the single-threaded JoltPhysics.js 1.1.0 wasm build (Jolt v5.6.0, no WASM SIMD) against Ammo.js (version not stated): settled boxes 0.09 vs 0.95 ms, rolling spheres 3.46 vs 5.86 ms and settled boxes with listeners 1.13 vs 2.82 ms favour Jolt, while falling boxes 5.76 vs 4.16 ms, mixed falling 4.44 vs 4.33 ms and falling with listeners 6.81 vs 6.32 ms favour Ammo. No CPU, Node or Ammo version, compiler flags or benchmark script are published, and nothing native or multithreaded was measured.

## Use it when

- Native games or VR on multicore desktops and consoles with hundreds to thousands of bodies, especially worlds where most bodies come to rest (debris, props), so sleeping islands cost almost nothing.
- Engines that run collision queries, streaming of body batches or navigation-mesh work on other threads while the simulation steps; the body lock interface and background broad-phase rebuild are built for this.
- Lock-step or rollback networking that needs deterministic simulation: same binary gives identical results, and CROSS_PLATFORM_DETERMINISTIC makes it deterministic across compilers, OSes and architectures at about 8% cost.
- Web scenes through JoltPhysics.js where bodies spend most frames settled; in the PlayCanvas test the settled and rolling-sphere scenes ran 1.7x to 10.6x cheaper than Ammo.js (derived from page data).
- Large open worlds that need double precision (JPH_DOUBLE_PRECISION) or a Godot project, where Jolt is an integrated physics option.

## Skip it when

- Single-threaded WebAssembly scenes dominated by bodies falling and colliding: in PR #9581 Jolt was 1.4x slower than Ammo.js (5.76 vs 4.16 ms) and level in two other scenes, and the PlayCanvas adapter cannot use the multithreaded JoltPhysics.js build because that build does not work with JS callbacks or in Safari.
- Static-heavy server worlds configured naively: issue #1081 reports more than 200 ms per tick at about 10k static colliders where PhysX and Bepu stayed under 5 ms at 2 million (a search snippet attributes the reply to a broad-phase layer misconfiguration mixing static and dynamic bodies), so follow the static/moving layer split.
- Code that relies on Bullet behaviour or API: per the PlayCanvas port there is no rolling friction, angular velocity is capped near 47 rad/s by default, contact impulses are not reported directly, and friction/restitution combine by geometric mean and maximum unless overridden.
- When you need a proven speed lead over PhysX or Rapier: Pierre Terdiman's PEEL runs in discussion #327 found the Jolt and PhysX curves intersect and look 'pretty much the same' once settings are aligned, and the Godot Rapier plugin's own blog (search snippet only) reports Rapier faster on 3 of 5 scenes with Jolt crashing its joint grid.
- Robotics distance or contact queries without dynamics, where a narrow-phase library such as Coal is lighter.

## How it is fast

The step is split into jobs on a job system: islands of touching or constrained bodies are built and solved in parallel, and large islands are split (the PerformanceTest Pyramid scene exists to profile this). The broad phase is a per-layer quad tree whose 4-wide nodes are tested with one SIMD instruction; moving bodies widen nodes lock-free and a tight tree is rebuilt in the background during the step. Islands at rest go to sleep and drop out of the simulation entirely, which is where the PlayCanvas numbers show the 10x gap (0.09 vs 0.95 ms for 400 settled bodies). Math uses SSE2 to AVX-512 or NEON, and v5.6.0 added a cheaper friction model (average contact point, 15% faster on the Pyramid test per the release notes).

## Compared with alternatives

Pick Jolt over Coal when you need a full simulation (broad phase, solver, sleeping, constraints, characters, multithreaded stepping) rather than FCL-style distance and collision queries for robotics, and over BVH libraries such as madmann91/bvh or TinyBVH, which build ray-tracing hierarchies and simulate nothing.

## Integration

| | |
|---|---|
| **Form** | static lib by default (CMake; shared via JPH_BUILD_SHARED_LIBS), also npm jolt-physics (wasm, wasm-compat, asm and multithread flavours) |
| **Dependencies** | none beyond the C++ standard library; the v5.6.0 GPU compute and hair code (JPH_USE_DX12, JPH_USE_VK, JPH_USE_MTL, on by default) needs dxc and spirv-cross on macOS unless switched off |
| **Minimum toolchain** | C++17; Visual Studio 2022+, Clang 16+ or GCC 12+; CMake 3.20+; no RTTI or exceptions by default |
| **Platforms** | Windows x86/x64/ARM64, Linux x86/x64/ARM32/ARM64/RISC-V64/LoongArch64/PowerPC64LE, FreeBSD, Android, macOS, iOS, MinGW64, a console; x86 minimum SSE2, AArch64 NEON; WebAssembly via JoltPhysics.js |
| **Thread safety** | Documented: a locking BodyInterface (hashed mutex array) and a non-locking variant; no body or constraint access while PhysicsSystem::Update runs; contact, activation and step listeners are called from multiple threads in nondeterministic order. |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw that works against Jolt in the colliding rows: the PlayCanvas adapter always installs a ContactListenerJS whose OnContactValidate, OnContactAdded and OnContactPersisted cross from wasm into JavaScript for every contact manifold on every substep, to force Bullet's multiplicative friction and restitution (JoltPhysics.js 1.1.0 does not bind PhysicsSystem::SetCombineFriction or SetCombineRestitution; the PR puts this at about 0.8 ms of the 5.76 ms). It also gives every dynamic body LinearCast CCD, which the Ammo path does not use, and cuts the penetration slop from 2 cm to 5 mm. The 'wasm' flavour is built without WASM SIMD (the JoltPhysics.js README says only the multithreaded builds enable it). The numbers therefore measure a scalar, callback-laden wasm adapter, not native Jolt against native Bullet. The settled-row win is fair: the Ammo path leaves dynamic bodies with ACTIVE_TAG, so they can deactivate too.
- The default x86 CMake options turn on AVX2, AVX, SSE4.2, LZCNT, TZCNT, F16C and FMA, so a default build dies with illegal instructions on older CPUs; Build/README.md gives the flags to turn them off. Defines such as JPH_DEBUG_RENDERER, JPH_DOUBLE_PRECISION and the RTTI setting must match between Jolt and your code, or you get link errors or a RegisterTypes abort.
- Bodies do not wake when created or when a neighbour is removed, and Body::SetLinearVelocity does not wake a body (use BodyInterface::SetLinearVelocity or ActivateBodiesInAABox).
- JoltPhysics.js 1.1.0 pins Jolt v5.6.0, which predates unreleased fixes such as HeightFieldShape::SetHeights corrupting its bounding volume tree when the block count is not a power of 2, and a GJK CastShape case that returned the wrong contact point.

## Known shortcomings

- PlayCanvas PR #9581 (still open): single-threaded wasm jolt-physics 1.1.0 vs Ammo.js (Bullet), no CPU or versions; Jolt is faster asleep (0.09 vs 0.95 ms) but slower while colliding (5.76 vs 4.16 ms); issue #1081 reports it far slower than PhysX with many static colliders. The author's whitepaper (jrouwe.nl) was blocked. Poor fit for geometry-spatial.
- Enricher: the PlayCanvas adapter runs ContactListenerJS callbacks wasm-to-JS per contact per substep to force Bullet friction combine (about 0.8 ms per the PR; JoltPhysics.js binds no SetCombineFriction) and enables LinearCast CCD on every dynamic body (absent on the Ammo path), so the colliding rows cut against Jolt; the wasm build has no WASM SIMD and the multithreaded build cannot take JS callbacks. The settled-row 10x win is fair (Ammo bodies can deactivate too). JoltPhysics.js 1.1.0 pins Jolt v5.6.0. Lead: Rapier (dimforge, Rust; Godot blog snippet says faster than Jolt on 3 of 5 scenes).

## Caveats and trade-offs

The numbers come from a third-party pull request (PlayCanvas engine PR #9581 by willeastcott, opened 2026-09-28 and still open on 2026-10-07) that adds Jolt as a physics backend, not from Jolt's author. It names Node.js, 400 bodies and 'minimum of 5 runs' and says it uses the single-threaded wasm build from the jolt-physics 1.1.0 npm package, but gives no CPU, no Ammo.js or Node versions, no compiler or flags and no link to the benchmark script, so it is tier C. Both engines run as single-threaded WebAssembly, which says little about native C++ Jolt against native Bullet and does not exercise Jolt's multicore design. The headline win is mostly the sleeping case (settled bodies cost almost nothing in Jolt); while bodies are colliding Jolt is slower or level in 3 of 5 scenes, and the PR says Jolt's own step is about 20% slower than Ammo's (4.94 ms with no contact listener), with the per-contact callback adding about 0.8 ms. The stronger primary source is Jolt's own whitepaper 'Jolt Physics Multicore Scaling' (https://jrouwe.nl/jolt/JoltPhysicsMulticoreScaling.pdf, linked from the README and Docs/PerformanceTest.md; the repo ships the PerformanceTest app that produces such numbers), which compares Jolt's scaling with other engines; jrouwe.nl was EGRESS_BLOCKED again, so its numbers were not read, and a retier in an environment that can open it could reach A or B. Discussion #327 shows Pierre Terdiman's PEEL runs against PhysX 4.1.2 and 5.1.0 on an Intel i9 where the curves intersect and match once settings are aligned, so there is no single winner. Issue #1081 (opened 2024-04-29, closed, resolution not visible) reports Jolt tick times above 200 ms with 10k-20k static colliders where PhysX 4/5 and Bepu Physics 2 stay under 5 ms with 2 million, a workload where Jolt was far slower. The wave 8 categories have no physics-engine bucket; geometry-spatial (broad phase and collision) was chosen over the lead's guessed blas-lapack and the orchestrator may override. The lead's baseline 'ODE or Bullet' leaves ODE untested.

C++17, no RTTI or exceptions, depends only on the STL; job-system multithreading, optional cross-platform deterministic build, optional double precision for large worlds. A one-developer test in issue #1081 reports tick times above 200 ms once a world has about 10k static colliders, where PhysX and Bepuphysics2 stayed under 5 ms at 2 million (no hardware stated), so static-heavy worlds can be a weak spot.

## Maintenance

Very active (last commit 2026-10-04, v5.6.0 the latest release with further fixes unreleased, issues answered and closed quickly), MIT-licensed, 11.7k stars and shipped in Horizon Forbidden West and Death Stranding 2; the PlayCanvas backend that produced these numbers is still an open PR.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** PlayCanvas engine PR #9581 shows a table of ms per RigidBodyComponentSystem#step(1/60) for Jolt vs Ammo.js (Bullet compiled to WebAssembly) matching every number in the record, but gives no CPU, no Ammo.js or Node version, no flags and no benchmark script link; it is a third-party PR, not a benchmark suite, and Jolt's own multicore whitepaper (jrouwe.nl) could not be opened, so C.
- **Verifier notes:** Numbers in the record match the PR table exactly and its derived ratios are correct; metadata checked (11.7k stars, MIT, last commit 2026-10-04, not a fork or archived). Shortcomings: WASM-only, single-threaded, mixed result (Jolt slower while colliding), no hardware or versions for Ammo, open PR; Jolt's whitepaper on jrouwe.nl is the needed source for a retier. Category is a poor fit (no physics bucket).
- **Fields the verifier corrected:** `compiler_and_flags`, `workload`, `caveats`
- **Shortcomings recorded by:** PlayCanvas PR (verifier); enricher harness reading
- **Pages the verifier opened:**
  - <https://github.com/playcanvas/engine/pull/9581>
  - <https://github.com/jrouwe/JoltPhysics>
  - <https://github.com/jrouwe/JoltPhysics/commits>
  - <https://github.com/jrouwe/JoltPhysics/tree/master/Docs>
  - <https://raw.githubusercontent.com/jrouwe/JoltPhysics/master/Docs/PerformanceTest.md>
  - <https://raw.githubusercontent.com/jrouwe/JoltPhysics/master/README.md>
  - <https://github.com/jrouwe/JoltPhysics/discussions/327>
  - <https://github.com/jrouwe/joltphysics/issues/1081>
- **Sources the enricher read:**
  - <https://github.com/playcanvas/engine/pull/9581>
  - <https://github.com/playcanvas/engine/pull/9581/files>
  - <https://raw.githubusercontent.com/playcanvas/engine/feat/jolt-physics-backend/src/framework/physics/jolt/jolt-physics-world.js>
  - <https://raw.githubusercontent.com/playcanvas/engine/feat/jolt-physics-backend/src/framework/physics/jolt/jolt-physics-body.js>
  - <https://raw.githubusercontent.com/playcanvas/engine/feat/jolt-physics-backend/src/framework/physics/jolt/jolt-contacts.js>
  - <https://raw.githubusercontent.com/playcanvas/engine/feat/jolt-physics-backend/src/framework/physics/ammo/ammo-physics-world.js>
  - <https://raw.githubusercontent.com/jrouwe/JoltPhysics/master/README.md>
  - <https://raw.githubusercontent.com/jrouwe/JoltPhysics/master/Docs/PerformanceTest.md>
  - <https://raw.githubusercontent.com/jrouwe/JoltPhysics/master/Docs/Architecture.md>
  - <https://raw.githubusercontent.com/jrouwe/JoltPhysics/master/Docs/ReleaseNotes.md>
  - <https://raw.githubusercontent.com/jrouwe/JoltPhysics/master/Build/README.md>
  - <https://raw.githubusercontent.com/jrouwe/JoltPhysics/master/Build/CMakeLists.txt>
  - <https://raw.githubusercontent.com/jrouwe/JoltPhysics/master/Jolt/Core/Core.h>
  - <https://raw.githubusercontent.com/jrouwe/JoltPhysics.js/main/package.json>
  - <https://raw.githubusercontent.com/jrouwe/JoltPhysics.js/main/README.md>
  - <https://raw.githubusercontent.com/jrouwe/JoltPhysics.js/main/CMakeLists.txt>
  - <https://raw.githubusercontent.com/jrouwe/JoltPhysics.js/main/JoltJS.idl>
  - <https://github.com/jrouwe/JoltPhysics/issues/1081>
  - <https://github.com/jrouwe/JoltPhysics/discussions/327>
  - <https://github.com/jrouwe/JoltPhysics/issues?q=is%3Aissue+performance>
  - https://jrouwe.nl/jolt/JoltPhysicsMulticoreScaling.pdf (EGRESS_BLOCKED)
  - https://godot.rapier.rs/blog/v0-35-0 (EGRESS_BLOCKED; WebSearch snippet only)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/jrouwe/joltphysics`) · [data/wave8/enrich/raw/github_com_jrouwe_joltphysics.json](../../../data/wave8/enrich/raw/github_com_jrouwe_joltphysics.json) (enrichment confidence 0.75)

</details>
