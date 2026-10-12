# webgpu-shaders-study (AssemblyScript SIMD particle loop vs JavaScript)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [AssemblyScript and WebAssembly languages](README.md)</sub>

**Tier C** (first-party claim) · Study only · `AssemblyScript (WebAssembly SIMD), Rust (WebAssembly SIMD), JavaScript, WGSL` · `no license` · 🟢 active

> Browser particle demo: the same 16-attractor loop in scalar JavaScript, AssemblyScript and Rust Wasm SIMD, and WebGPU.

| | |
|---|---|
| **Beats** | plain JavaScript loop on the CPU in the browser (V8 assumed, browser not stated) |
| **Claimed result** | Heavy mode on an Apple Silicon Mac: JavaScript 33 fps at 1M and 8 fps at 4M (no 16M figure); WASM AssemblyScript 40, 37 and 6 fps (about 1.2x at 1M and 4.6x at 4M, derived from page data); WASM Rust 60, 41 and 11 fps; WebGPU 60, 60 and \~48 fps. README: Rust's step is about 15% faster than AssemblyScript's in Light mode, more in Heavy |
| **Workload** | Particle simulation pulled toward the mouse, Heavy mode (16 attractors per particle), frames per second at 1M, 4M and 16M particles, same data copied to the GPU every frame in the JS and wasm demos |
| **Metric** | throughput |
| **Hardware** | Apple Silicon Mac (chip model not stated) |
| **Compiler and flags** | AssemblyScript ^0.28.20 (package.json devDependency): `asc 2-wasm/assembly/index.ts --outFile 2-wasm/build/sim.wasm --optimize --runtime stub --noAssert --enable simd`. Rust: cargo --release for wasm32-unknown-unknown with opt-level 3, lto, codegen-units 1, panic abort (2-wasm-rust/sim/Cargo.toml) and -C target-feature=+simd128 (.cargo/config.toml). Compiled .wasm files are checked in. Browser and JS engine not stated. |
| **Adoption** | 0 stars (single commit, 2026-10-09) |
| **Last commit** | 2026-10-09 |
| **Links** | [repository](https://github.com/anshullaikar/webgpu-shaders-study) · [benchmark](https://github.com/anshullaikar/webgpu-shaders-study) |

## Verdict

Heavy mode (16 attractors), unnamed Apple Silicon Mac and browser, whole-frame rates averaged over the last 30 requestAnimationFrame frames: scalar JavaScript 33 fps at 1M and 8 fps at 4M particles against AssemblyScript f32x4 Wasm (asc 0.28.20) 40 and 37 fps (about 1.2x and 4.6x, derived from page data), with Rust Wasm 60/41/11 and WebGPU 60/60/\~48 fps at 1M/4M/16M; every CPU variant includes the same WebGL upload and draw of at most 1M points.

## Use it when

- Learning or teaching where browser compute time goes: the same kernel side by side in JS, Wasm SIMD (AssemblyScript and Rust) and WebGPU, with a per-step CPU-time bar in each demo.
- Deciding whether a compute-heavy per-element f32 loop (about 16 divisions per element per frame) at 1M to 4M elements is worth porting from JavaScript to Wasm SIMD.
- As a template for loading an AssemblyScript or Rust (no wasm-bindgen) module through plain exports and sharing arrays with JavaScript via typed-array views into Wasm memory.

## Skip it when

- As code to vendor: the repository has no licence file, so reuse is not granted.
- If you need trustworthy numbers: the README reports only frame rates on an unnamed Apple Silicon Mac in an unnamed browser, capped at 60 fps, with no Light-mode figures and none of the per-step sim timings the HUD displays.
- If you are choosing AssemblyScript for speed: the project's own table has its Rust Wasm build ahead of AssemblyScript at every size (60/41/11 fps against 40/37/6) and the README puts Rust's step about 15% faster in Light mode.
- For millions of particles at interactive rates: only the WebGPU variant holds 60 fps at 4M (about 48 at 16M); every CPU variant also pays a CPU-to-GPU copy each frame.
- Browsers without Wasm SIMD (simd128) or WebGL 2.

## How it is fast

The AssemblyScript step (2-wasm/assembly/index.ts) keeps x, y, vx and vy as separate f32 arrays (structure of arrays) and updates 4 particles per instruction with f32x4 load, sub, mul, div and store, against JavaScript's scalar loop that does the same maths one particle at a time in f64. Built with asc 0.28.20 (binaryen 131 nightly per package-lock.json) using --optimize --noAssert --runtime stub, so there are no bounds checks or GC runtime in the hot loop. Most of the gap is therefore SIMD width plus f32 arithmetic, not AssemblyScript as a language.

## Compared with alternatives

Pick it over wasm-perf (Emscripten C SIMD matrix multiply against Node) or AutoZig (Zig SIMD image filter) when you want an in-browser, AssemblyScript-specific comparison that also shows the Rust Wasm and WebGPU alternatives on the same kernel; for measured, scriptable numbers those siblings' command-line benchmarks are easier to reproduce.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none at run time (any static HTTP server; npm start uses python3 -m http.server); rebuilding needs assemblyscript 0.28.20 (npm) and a Rust toolchain with the wasm32-unknown-unknown target |
| **Minimum toolchain** | AssemblyScript 0.28.20; Rust edition 2024 crate (Rust 1.85+); browser with Wasm SIMD and WebGL 2, WebGPU for demo 3 |
| **Platforms** | any desktop browser with Wasm simd128; measured only on an Apple Silicon Mac |
| **Thread safety** | single-threaded; both modules keep particle state in module globals (Rust uses static mut and documents the one-thread assumption) |
| **Drop-in for the baseline** | no |

## Gotchas

- The JavaScript baseline computes in f64 and rounds on each Float32Array store, while both Wasm builds compute in f32 SIMD, so trajectories differ slightly from the JS demo; the README's 'identical results' refers to AssemblyScript against Rust only.
- The AssemblyScript row is internally inconsistent (40 fps at 1M against 37 fps at 4M for four times the work, while JS and Rust scale with work), so the 1M reading, and the 1.2x ratio derived from it, is unreliable; the 4M pair (8 against 37 fps, about 4.6x) is the usable comparison and is a lower bound on the step-time ratio because both frames include the same 1M-point upload and draw.
- Harness flaw in shared/ui.js: changing the particle count clears the sample window but not lastFrame, so the first frame after a switch carries the whole allocation and re-seeding pause; the overview page shows whichever reading was saved last (saved at most once a second once 10 samples exist), so a reading taken soon after a switch understates fps.
- The AssemblyScript module uses --runtime stub with hand-managed pointers after __heap_base: memory grows but is never freed, and JavaScript must rebuild its typed-array views after every alloc because memory.grow replaces the buffer (wasm-demo.js does this).

## Known shortcomings

- Frame rates on an unnamed Apple Silicon Mac in an unnamed browser, no licence (reference), 1 commit, 0 stars; only 1.2x JavaScript at 1M particles with the gain mostly SIMD against scalar JavaScript; the AssemblyScript row scales oddly (40 fps at 1M, 37 fps at 4M).
- Enricher: shared/ui.js clears the sample window on a count change but not lastFrame, so the first window includes the allocation and seed stall and the overview keeps the last saved reading; the AssemblyScript 1M row (40 fps) is internally inconsistent, leaving the 4M pair (8 vs 37 fps, about 4.6x, a lower bound on the step-time ratio) as the only usable comparison; the JavaScript baseline computes in f64 and rounds per store while the Wasm builds compute in f32 SIMD; no licence file.

## Caveats and trade-offs

One-commit repository (2026-10-09) with a results table pasted into the README and no licence file; readings are requestAnimationFrame frame rates (capped at 60) averaged over the last 30 frames, not controlled timings, and include a WebGL upload and draw of up to 1M points shared by all CPU variants (the HUD also shows per-step sim ms, but those are not reported). The kernels are equivalent (same attractor maths over Float32Array data), but JS runs scalar f64 arithmetic while AssemblyScript runs 4-wide f32x4 SIMD, so the gap is mostly SIMD. The AssemblyScript row is internally inconsistent: 40 fps at 1M and 37 fps at 4M for four times the work, then 6 fps at 16M, so the 1M reading looks limited by something other than the simulation step. Browser, chip model and asc patch version are not stated (on a Mac the browser could be Safari's JavaScriptCore rather than V8); the JS 16M cell is blank. Counter-evidence from the same table: at 1M particles the AssemblyScript build is only 1.2x the JS loop, and Rust's wasm beats AssemblyScript at every size. No benchmark harness beyond the interactive pages; the overview page only stores each viewer's own readings in localStorage.

WASM path needs a full CPU copy to the GPU each frame; only the WebGPU demo keeps particles on the GPU; 16M particles draw 1M points only.

## Maintenance

Single-commit study repository (2026-10-09, 0 stars) with no licence file, so it is a reference to read rather than code to copy; both compiled .wasm files are checked in and contain the expected f32x4 SIMD instructions.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** README table of frame rates from the author's own interactive demos (1-javascript/main.js vs 2-wasm/assembly/index.ts via shared/wasm-demo.js) on an unnamed Apple Silicon Mac; build flags are public in package.json, but the chip model, browser/JS engine and run protocol are not stated, so first-party with partial methodology is C.
- **Verifier notes:** README numbers match the record; asc flags are in package.json (the record said they were not shown). Harness is symmetric (same physics, same upload and draw) but measures fps on an unnamed Apple Silicon Mac in an unnamed browser, and the AssemblyScript 1M/4M readings scale implausibly; keep tier C reference, no licence, 0 stars.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-119 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/anshullaikar/webgpu-shaders-study>
  - <https://github.com/anshullaikar/webgpu-shaders-study/commits>
  - <https://raw.githubusercontent.com/anshullaikar/webgpu-shaders-study/HEAD/README.md>
  - <https://raw.githubusercontent.com/anshullaikar/webgpu-shaders-study/HEAD/package.json>
  - <https://raw.githubusercontent.com/anshullaikar/webgpu-shaders-study/HEAD/.cargo/config.toml>
  - <https://raw.githubusercontent.com/anshullaikar/webgpu-shaders-study/HEAD/2-wasm-rust/sim/Cargo.toml>
  - <https://raw.githubusercontent.com/anshullaikar/webgpu-shaders-study/HEAD/2-wasm/assembly/index.ts>
  - <https://raw.githubusercontent.com/anshullaikar/webgpu-shaders-study/HEAD/1-javascript/main.js>
  - <https://raw.githubusercontent.com/anshullaikar/webgpu-shaders-study/HEAD/shared/wasm-demo.js>
  - <https://raw.githubusercontent.com/anshullaikar/webgpu-shaders-study/HEAD/shared/ui.js>
  - <https://raw.githubusercontent.com/anshullaikar/webgpu-shaders-study/HEAD/index.html>
- **Sources the enricher read:**
  - <https://github.com/anshullaikar/webgpu-shaders-study>
  - <https://github.com/anshullaikar/webgpu-shaders-study/commits>
  - <https://raw.githubusercontent.com/anshullaikar/webgpu-shaders-study/HEAD/README.md>
  - <https://raw.githubusercontent.com/anshullaikar/webgpu-shaders-study/HEAD/package.json>
  - <https://raw.githubusercontent.com/anshullaikar/webgpu-shaders-study/HEAD/package-lock.json>
  - <https://raw.githubusercontent.com/anshullaikar/webgpu-shaders-study/HEAD/.cargo/config.toml>
  - <https://raw.githubusercontent.com/anshullaikar/webgpu-shaders-study/HEAD/2-wasm-rust/sim/Cargo.toml>
  - <https://raw.githubusercontent.com/anshullaikar/webgpu-shaders-study/HEAD/2-wasm-rust/sim/src/lib.rs>
  - <https://raw.githubusercontent.com/anshullaikar/webgpu-shaders-study/HEAD/2-wasm/assembly/index.ts>
  - <https://raw.githubusercontent.com/anshullaikar/webgpu-shaders-study/HEAD/2-wasm/main.js>
  - <https://raw.githubusercontent.com/anshullaikar/webgpu-shaders-study/HEAD/2-wasm/index.html>
  - <https://raw.githubusercontent.com/anshullaikar/webgpu-shaders-study/HEAD/2-wasm-rust/main.js>
  - <https://raw.githubusercontent.com/anshullaikar/webgpu-shaders-study/HEAD/2-wasm/build/sim.wasm>
  - <https://raw.githubusercontent.com/anshullaikar/webgpu-shaders-study/HEAD/2-wasm-rust/build/sim.wasm>
  - <https://raw.githubusercontent.com/anshullaikar/webgpu-shaders-study/HEAD/1-javascript/main.js>
  - <https://raw.githubusercontent.com/anshullaikar/webgpu-shaders-study/HEAD/3-webgpu/main.js>
  - <https://raw.githubusercontent.com/anshullaikar/webgpu-shaders-study/HEAD/shared/wasm-demo.js>
  - <https://raw.githubusercontent.com/anshullaikar/webgpu-shaders-study/HEAD/shared/ui.js>
  - <https://raw.githubusercontent.com/anshullaikar/webgpu-shaders-study/HEAD/shared/webgl-points.js>
  - <https://raw.githubusercontent.com/anshullaikar/webgpu-shaders-study/HEAD/index.html>
  - https://raw.githubusercontent.com/anshullaikar/webgpu-shaders-study/HEAD/LICENSE (404)
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/anshullaikar/webgpu-shaders-study`) · [data/wave13/enrich/raw/github_com_anshullaikar_webgpu_shaders_study.json](../../../data/wave13/enrich/raw/github_com_anshullaikar_webgpu_shaders_study.json) (enrichment confidence 0.6)

</details>
