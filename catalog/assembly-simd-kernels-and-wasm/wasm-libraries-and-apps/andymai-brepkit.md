# brepkit

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly libraries and apps](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Rust` · `AGPL-3.0-only` · 🟢 active

> Pure-Rust B-rep CAD kernel for native and wasm; README claims 3.4-252x over OCCT-in-wasm on tiny primitive operations.

| | |
|---|---|
| **Beats** | occt-wasm 3.8.3 (OCCT compiled to wasm) with a double-build defect in every two-operand boolean, fixed in occt-wasm 5.5.1 (PR #383, 2026-10-03) |
| **Claimed result** | brepkit (wasm) vs OCCT (wasm): fuse(box,box) x10 0.43 ms vs 44.9 ms (103x); cut(box,cylinder) x10 19.2 vs 64.9 ms (3.4x); box+chamfer 0.10 vs 5.6 ms (55x); box+fillet 0.33 vs 6.1 ms (18x); intersect(box,sphere) x10 0.23 vs 59.1 ms (252x); multi-boolean 4.6 vs 30.3 ms (6.6x); mesh sphere 6.2 vs 49.4 ms (7.9x); volume x100 0.18 vs 9.8 ms (54x); exportSTEP x10 0.85 vs 14.3 ms (17x). |
| **Workload** | Nine B-rep CAD operations on small test solids in single-threaded Node.js: fuse of two boxes, box minus cylinder, box chamfer, box fillet, box-sphere intersect, 16-hole multi-boolean, sphere tessellation, box volume, STEP export; median of 5 iterations after 2 warm-ups, every row output-verified before timing. |
| **Metric** | latency |
| **Hardware** | Linux x86_64, CPU model not stated |
| **Compiler and flags** | Rust 1.88+, cargo build -p brepkit-wasm --target wasm32-unknown-unknown --release (wasm-opt settings not stated). The current occt-wasm README states its build: emcc -O3 -flto -fwasm-exceptions with WASM SIMD (-msimd128, no relaxed SIMD), then wasm-opt -O4 --converge --gufa; it does not say whether the benchmarked 3.8.3 release (published 2026-08-03) used the same flags. Released npm packages exact-pinned in the brepkit-bench package.json and lockfile: brepkit-wasm 3.0.0, occt-wasm 3.8.3, brepjs 18.120.0, tsx 4.23.1; Node 20+. |
| **Adoption** | 32 stars; npm package brepkit-wasm, crate brepkit-operations |
| **Last commit** | 2026-10-11 |
| **Links** | [repository](https://github.com/andymai/brepkit) · [benchmark](https://github.com/andymai/brepkit) |

## Verdict

brepjs 18.120.0 drove brepkit-wasm 3.0.0 and occt-wasm 3.8.3 (OCCT V8.0.1 via Emscripten) in single-threaded Node on Linux x86-64 (CPU not stated), taking the median of 5 runs after 2 warm-ups with every result volume-checked. brepkit led on all nine rows, from 3.4x (box minus cylinder) to 252x (box-sphere intersect). The OCCT side computed each boolean twice (fixed in occt-wasm 5.5.1), and the largest ratios come from brepkit's closed-form shortcuts for contained and box-sphere inputs, so the general-boolean advantage is nearer 1-1.7x (derived from page data).

## Use it when

- Parametric CAD in the browser or Node (configurators and generators like the author's Gridfinity layout tool) built mostly from boxes, cylinders and spheres with booleans, fillets and chamfers, where OCCT-in-wasm feels slow. On the author's 26-scenario Gridfinity generator suite (issue #1517, August 2026) brepkit took 0.63-0.69x of occt-wasm's aggregate time and was faster on 24 of 26 scenarios.
- Rust projects that want exact B-rep modelling with no C++ toolchain, no `unsafe` (denied by lint) and a Result-returning API.
- Chained booleans on analytic geometry, where keeping cylinders as cylinders keeps the face count low (README: a nine-step compound boolean settles at 72 faces).
- Open-source (AGPL-compatible) applications, or teams willing to buy the commercial licence. For permissive terms, pin a release up to 2.129.x (MIT OR Apache-2.0).

## Skip it when

- Closed-source products without the commercial licence: 3.0.0 and later are AGPL-3.0-only, and contributions need a signed CLA.
- Workloads that need OCCT's breadth: IGES is experimental (analytic surfaces skipped on export, planar placeholders on import), there are no colours, layers, materials or PMI in exchange, PLY import is missing from the wasm API, and general torus booleans have known gaps.
- Hard boolean configurations (coincident faces, coaxial analytic surfaces, razor-thin geometry, very high face counts): these fall back to a mesh boolean that tessellates curved faces and is not guaranteed watertight (README Known Limitations).
- Workloads of general-position booleans if you are expecting the headline 100x+. The one table row that exercises the general engine (box minus corner cylinder) shows 3.4x, measured against an OCCT build that computed every boolean twice (see gotchas).
- Teams that need a stable API: the version went from 3.0.0 (early August 2026) to 4.1.49 (2026-10-11). In August 2026 the author's own generator suite still had 137-154 failures (non-watertight meshes, a 3.13x wrong volume, a panic, timeouts) until brepkit-wasm 3.2.36.

## How it is fast

The kernel classifies each operand analytically (box, cylinder, cone, sphere, torus) before running the general boolean. Closed-form shortcuts then handle identical solids, containment (the result is a copy of one operand), axis-aligned box pairs (AABB algebra), the box-sphere octant intersect, coaxial cylinders, cones and tori, concentric spheres, and disjoint fuse or cut (shell merge or copy). Only inputs that miss every shortcut reach the pave-filler General Fuse pipeline. Volume uses exact formulas for primitives and a polygon divergence integral for all-planar solids, so nothing is tessellated. Native builds also mesh faces in parallel with rayon. The wasm build is single-threaded.

## Compared with alternatives

No CAD kernel is catalogued among the wasm siblings. Like ywasm and Loro against Yjs, it is a Rust-to-wasm replacement for a heavier incumbent engine, but pick it only when you need exact B-rep solid modelling in JS or Rust. For hashing, CRDTs or data processing the siblings (hash-wasm, Loro, DuckDB-Wasm) are the relevant entries.

## Integration

| | |
|---|---|
| **Form** | crate (Cargo workspace published as brepkit-operations, brepkit-topology, brepkit-io and others, all at one version) or npm module brepkit-wasm (wasm-bindgen) |
| **Dependencies** | Pure Rust: robust, thiserror, log, rayon, smallvec, bitflags, serde/serde_json, quick-xml and zip (I/O), wasm-bindgen 0.2.129 for the wasm crate; no C or C++ dependencies |
| **Minimum toolchain** | Rust 1.88 (edition 2024); the npm package needs only a wasm-capable JS runtime |
| **Platforms** | Any Rust target; wasm32-unknown-unknown for the npm build (single-threaded); native builds parallelise per-face meshing |
| **Thread safety** | Single-owner: operations take `&mut Topology`, and a `BrepKernel` wasm instance is not reentrant. Issue #1517 recorded 'recursive use of an object' errors after an aborted boolean left the wasm borrow flag stuck (fixed via #1520). |
| **Drop-in for the baseline** | partial: through brepjs, OCCT (occt-wasm) and brepkit are interchangeable backends behind one TypeScript API; direct OCCT C++ or opencascade.js code must be rewritten |

## Gotchas

- Baseline defect: occt-wasm 3.8.3, the benchmarked OCCT build, constructed `BRepAlgoAPI_Fuse/Cut/Common op(a, b)` and then called `op.Build()`. The constructor already builds, so every two-operand boolean in the OCCT column ran twice. The same author fixed this in occt-wasm 5.5.1 (PR #383, 2026-10-03), which reports 2.0-3.8x faster booleans and a CI 'fuse x10' of 35.98 ms vs 67.04 ms. The fuse, cut, intersect and multi-boolean rows are therefore inflated. Halving the OCCT time gives roughly 52x, 1.7x, 126x and 3.3x (derived from page data). At PR #383's 3.8x upper bound the cut row is about parity. The brepkit-bench harness and README table were last updated 2026-08-07 and still pin 3.8.3.
- Shortcut rows: in fuse(box, box) the 5 mm box is contained in the 10 mm box, so brepkit's containment shortcut just copies the larger box. In intersect(box, sphere) the sphere is centred on a box corner, which is exactly the 'box-sphere octant' closed-form shortcut. In the multi-boolean row, 12 of 16 cylinders are disjoint and take the disjoint-cut copy path. OCCT runs its full General Fuse algorithm on all of these, so the 103x and 252x figures measure classification shortcuts, not brepkit's boolean engine.
- The volume(box) row hits an exact all-planar polygon integral, while OCCT's BRepGProp runs generic integration. The export row writes one box. Neither predicts complex parts.
- The harness never releases shapes on either side (occt-wasm frees only on release() or kernel disposal, and brepkit's arena grows until checkpoint/restore), so long sessions need explicit memory management.

## Known shortcomings

- No CPU model; the same author built the occt-wasm baseline and brepjs; the fuse row unions a contained box (trivial); the tested package versions have since been superseded. Harness andymai/brepkit-bench checks each row's output before timing.
- Enricher: the benchmarked OCCT baseline occt-wasm 3.8.3 builds every two-operand boolean twice (BRepAlgoAPI_Fuse op(a,b) then op.Build()), fixed by the same author in occt-wasm 5.5.1 (PR #383, 2026-10-03, booleans 2.0-3.8x faster), so the fuse, cut, intersect and multi-boolean rows are inflated (roughly 52x, 1.7x, 126x and 3.3x derived; the cut row is about parity at the 3.8x bound); the fuse row hits brepkit's containment shortcut and the intersect row a closed-form box-sphere octant shortcut, and 12 of 16 multi-boolean tools take the disjoint-cut copy path, so only the cut row exercises the general boolean engine; brepkit-bench is untouched since 2026-08-07 and still pins 3.8.3; issue #1517's real workload (gridfinity suite) shows 0.63-0.69x of occt-wasm time, also against the pre-fix baseline. Retiered to D.

## Caveats and trade-offs

First-party numbers: brepkit, the OCCT wasm baseline (occt-wasm) and the brepjs adapter used by both sides all come from the same author. CPU model not stated in the README (the harness prints it at run time but the published table omits it). Workloads are tiny primitives: the fuse row unions a box with a smaller box fully contained in it (touching three faces), so a containment fast path can dominate the 103x figure; volume(box) x100 measures an analytic box. Boolean and STEP rows are batches of ten. No native OCCT baseline; the brepkit native column has no OCCT counterpart. Numbers are for brepkit-wasm 3.0.0 and occt-wasm 3.8.3, both since superseded (4.1.49 and 5.7.0 on npm, 2026-10-11). The adapter paths are thin on both sides (direct k.fuse/k.cut/getVolume calls in brepjs src/kernel/occtWasm and src/kernel/brepkit), so adapter overhead looks comparable. Dual licence: AGPL-3.0-only or commercial from 3.0.0 on; versions through 2.129.x were MIT OR Apache-2.0. [retier] OCCT booleans ran twice per operation in the benchmarked baseline; fuse and intersect rows hit brepkit special cases; issue #1517's gridfinity workload shows 0.63-0.69x of occt-wasm time against the same pre-fix baseline

Different kernel, not a port of OCCT: feature coverage is narrower (IGES is experimental, PLY import not exposed in wasm). AGPL-3.0-only with a commercial licence for proprietary embedding and a contributor licence agreement; versions through 2.129.x were MIT OR Apache-2.0. Native Rust build is faster still than the wasm build.

## Maintenance

Very active (about 2,040 commits, last commit 2026-10-11, crate and npm version 4.1.49) and copyable under AGPL-3.0-only or a commercial licence. The published benchmark is two months stale and is still measured against an occt-wasm build with a double-build defect that the same author has since fixed.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now D.
- **Tier reason:** The brepkit README Performance table carries every claimed number (brepkit-wasm 3.0.0 vs occt-wasm 3.8.3, measured 2026-08-07), and the harness is public (andymai/brepkit-bench bench.ts, exact-pinned package.json and lockfile, output-verified rows, median of 5 after 2 warm-ups), but no CPU model is stated and the brepkit-wasm wasm-opt settings are not given, so it cannot be A. All three pieces (brepkit, occt-wasm, brepjs adapter) are by the same author, so first-party C.
- **Retiered** C to D: Enricher (2026-10-12): crippled baseline with no valid measurement. The benchmarked occt-wasm 3.8.3 constructs BRepAlgoAPI_Fuse/Cut/Common op(a, b) and then calls op.Build(), so every two-operand boolean in the OCCT column ran twice (fixed by the same author in occt-wasm 5.5.1, PR #383, 2026-10-03, booleans 2.0-3.8x faster); the fuse and intersect rows additionally hit brepkit shortcuts (containment copy, closed-form box-sphere octant) and 12 of 16 multi-boolean tools take the disjoint-cut copy path, so only the cut row exercises the general boolean engine and that row is about parity at PR #383's bound; brepkit-bench still pins 3.8.3.
- **Verifier notes:** Numbers match the README table exactly; harness andymai/brepkit-bench/bench.ts verifies each row's volume (closed-form or cross-kernel) before timing, so no fast-but-wrong rows. Main shortcomings: same-author baseline build, no CPU model, trivial primitive workloads (fuse row is a contained-tool union), superseded package versions. Repo: 32 stars, 2,040 commits, last commit 2026-10-11, AGPL-3.0-only, not a fork.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`, `baseline`
- **Shortcomings recorded by:** verifier batch-105 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/andymai/brepkit/HEAD/README.md>
  - <https://github.com/andymai/brepkit>
  - <https://github.com/andymai/brepkit/commits/main>
  - <https://raw.githubusercontent.com/andymai/brepkit-bench/HEAD/README.md>
  - <https://raw.githubusercontent.com/andymai/brepkit-bench/HEAD/package.json>
  - <https://raw.githubusercontent.com/andymai/brepkit-bench/HEAD/package-lock.json>
  - <https://raw.githubusercontent.com/andymai/brepkit-bench/HEAD/bench.ts>
  - <https://github.com/andymai/occt-wasm>
  - <https://github.com/andymai/brepjs>
  - <https://github.com/andymai/brepjs/tree/main/src/kernel>
  - <https://github.com/andymai/brepjs/tree/main/src/kernel/occtWasm>
  - <https://github.com/andymai/brepjs/tree/main/src/kernel/brepkit>
  - <https://raw.githubusercontent.com/andymai/brepjs/main/src/kernel/occtWasm/booleanOps.ts>
  - <https://raw.githubusercontent.com/andymai/brepjs/main/src/kernel/brepkit/booleanOps.ts>
  - <https://raw.githubusercontent.com/andymai/brepjs/main/src/kernel/occtWasm/measureOps.ts>
  - <https://raw.githubusercontent.com/andymai/brepjs/main/src/kernel/brepkit/measureOps.ts>
  - <https://registry.npmjs.org/occt-wasm>
  - <https://registry.npmjs.org/brepkit-wasm>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/andymai/brepkit/HEAD/README.md>
  - <https://raw.githubusercontent.com/andymai/brepkit/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/andymai/brepkit/HEAD/LICENSE>
  - <https://github.com/andymai/brepkit/tree/main/crates/operations/src/boolean>
  - <https://raw.githubusercontent.com/andymai/brepkit/HEAD/crates/operations/src/boolean/mod.rs>
  - <https://raw.githubusercontent.com/andymai/brepkit/HEAD/crates/operations/src/boolean/classify.rs>
  - <https://raw.githubusercontent.com/andymai/brepkit/HEAD/crates/operations/src/boolean/assembly.rs>
  - <https://raw.githubusercontent.com/andymai/brepkit/HEAD/crates/operations/src/boolean/types.rs>
  - <https://crates.io/api/v1/crates/brepkit-operations/3.0.0/download>
  - <https://crates.io/api/v1/crates/brepkit-algo/3.0.0/download>
  - <https://crates.io/api/v1/crates/brepkit-wasm/3.0.0/download>
  - <https://github.com/andymai/brepkit/issues?q=is%3Aissue+bug>
  - <https://github.com/andymai/brepkit/issues/1517>
  - <https://raw.githubusercontent.com/andymai/brepkit-bench/HEAD/README.md>
  - <https://raw.githubusercontent.com/andymai/brepkit-bench/HEAD/bench.ts>
  - <https://raw.githubusercontent.com/andymai/brepkit-bench/HEAD/package.json>
  - <https://github.com/andymai/brepkit-bench/commits/main>
  - <https://raw.githubusercontent.com/andymai/brepjs/main/src/kernel/occtWasm/booleanOps.ts>
  - <https://raw.githubusercontent.com/andymai/brepjs/main/src/kernel/brepkit/booleanOps.ts>
  - <https://raw.githubusercontent.com/andymai/brepjs/main/src/kernel/occtWasm/measureOps.ts>
  - <https://raw.githubusercontent.com/andymai/brepjs/main/src/kernel/brepkit/measureOps.ts>
  - <https://registry.npmjs.org/brepjs/-/brepjs-18.120.0.tgz>
  - <https://github.com/andymai/occt-wasm>
  - <https://github.com/andymai/occt-wasm/tree/main/facade>
  - <https://github.com/andymai/occt-wasm/tree/main/facade/src>
  - <https://github.com/andymai/occt-wasm/tree/main/facade/generated>
  - <https://raw.githubusercontent.com/andymai/occt-wasm/HEAD/facade/src/kernel.cpp>
  - <https://raw.githubusercontent.com/andymai/occt-wasm/HEAD/facade/generated/kernel.cpp>
  - <https://raw.githubusercontent.com/andymai/occt-wasm/v3.8.3/facade/generated/kernel.cpp>
  - <https://raw.githubusercontent.com/andymai/occt-wasm/HEAD/CHANGELOG.md>
  - <https://github.com/andymai/occt-wasm/pull/383>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/andymai/brepkit`) · [data/wave13/enrich/raw/github_com_andymai_brepkit.json](../../../data/wave13/enrich/raw/github_com_andymai_brepkit.json) (enrichment confidence 0.8)

</details>
