# libmsdf

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Font shaping and text layout](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟢 active

> Rust/wgpu SDF and MSDF text renderer whose WGSL compute shader generates MSDF glyphs at runtime; no speed data versus msdfgen.

| | |
|---|---|
| **Beats** | msdfgen (CPU MSDF generator; the lead's msdfgl was not compared either); neither is in the listed HarfBuzz/FreeType baselines |
| **Claimed result** | None. No timings, fps or speed ratios appear in the README, Cargo.toml, tests or shader sources read. The README only says the compute-shader MSDF generation matches the CPU msdfgen baseline. |
| **Workload** | Runtime MSDF glyph generation in a WGSL compute shader versus the CPU msdfgen bake: the repository compares output accuracy (median-of-channels within tolerance), not speed. |
| **Metric** | other |
| **Hardware** | README: GPU tests run headless on Metal (no model given) |
| **Adoption** | 0 stars, 60 commits, oldest visible commit 2026-08-12 on the commits page |
| **Last commit** | 2026-09-26 |
| **Links** | [repository](https://github.com/tmzt/libmsdf) |

## Verdict

No speed was measured. The only comparison is the output-parity test compute_matches_cpu_baseline: Roboto 'A', 'o', 'g', '5' and '#' at 48 px cells with a 6.0 px range, compute shader versus msdfgen via the msdfgen crate, scored on channel medians in the near-outline band. Recorded mean deviations are 0.0009 ('o'), 0.030 ('g'), 0.033 ('5'), 0.066 ('A') and 0.114 ('#'); pass thresholds are mean at most 0.13, at most 35% of texels beyond 0.125 and coverage IoU at least 0.98, on headless Metal with no GPU model given.

## Use it when

- Rust apps on wgpu that target wasm32/WebGPU and want MSDF text, where the msdfgen C++ FFI cannot be built.
- Generating glyph cells on demand in a browser instead of downloading baked atlases (a code comment puts a style's baked cells at about 290 KiB gzipped against a 13 KiB face).
- Small UI scenes, such as highbay's node graph, that mix SDF shapes and text and fit in one full-screen pass.
- As a reference: the 221-line, MIT/Apache-licensed msdf_compute.wgsl is self-contained enough to port to another engine.

## Skip it when

- When you need a measured speedup over msdfgen: none exists; msdfgl publishes numbers, this crate does not.
- Corner-heavy glyphs that need fields close to msdfgen's: the parity test allows a mean channel-median deviation up to 0.13 and up to 35% of near-outline texels off by more than 0.125, and the code comments record 0.114 for '#'.
- Large scenes: the fragment shader loops over every draw command (MAX_DRAW_CMDS 4096) for every pixel, with only a vertical-band reject for text and no tiling or binning.
- Production dependencies: Cargo.toml has publish = false (git dependency only), the repo has 0 stars and first commits from August 2026, the public API carries highbay-specific items (HIGHBAY_ICONS, PHASE_STATUS), and the README still says wgpu 29 although Cargo.toml uses 30.0.1.
- Shaping-heavy text: TextShaper wraps rustybuzz 0.20 (the archived HarfBuzz port, per the sigilbuzz sibling entry) and re-parses the face with rustybuzz::Face::from_slice on every shape call.

## How it is fast

No performance claim is made, so there is no speedup technique to credit. The runtime generator extracts and colours edges on the CPU (msdfgen edgeColoringSimple scheme, 3.0 angle threshold), then a WGSL kernel runs one thread per texel in 8x8 workgroups and loops over every edge: quadratics are flattened into 8 segments and cubics into 16, each channel takes the pseudo-distance of its nearest edge by true distance, and the sign comes from a nonzero-winding ray test. That is brute force, O(texels x edges x segments), with no spatial acceleration and no error-correction pass. Its value is where it runs (on the GPU, including wasm32/WebGPU where the msdfgen C++ FFI cannot build), not a measured speed advantage.

## Compared with alternatives

Pick it over msdfgl (OpenGL compute MSDF, with published timings against msdfgen) only when you are on wgpu or WebGPU in Rust and need runtime MSDF on wasm32. Pick fontdue or ab_glyph instead for CPU coverage rasterisation, where this crate offers nothing measured.

## Integration

| | |
|---|---|
| **Form** | crate (unpublished; Cargo git dependency) |
| **Dependencies** | wgpu 30.0.1, bytemuck, log, rustybuzz 0.20, ttf-parser 0.25, unicode-segmentation 1.13; build-time naga 30.0.1 (validates the three WGSL shaders); optional cpu-bake adds msdfgen 0.2 (C++ FFI) and ttf-parser 0.18 |
| **Minimum toolchain** | Rust edition 2024 (rustc 1.85 or newer); cpu-bake needs a C++ toolchain, and on macOS the LLVM codegen backend because the Cranelift dev profile fails to link msdfgen symbols |
| **Platforms** | native wgpu backends (GPU tests documented only on headless Metal) and wasm32 WebGPU; the CPU msdfgen bake is native only |
| **Thread safety** | not documented; renderers borrow a caller-owned wgpu Device and Queue, and AtlasManager stores boxed FnMut eviction hooks without a Send bound, so it cannot move across threads. The crate is #![forbid(unsafe_code)]. |
| **Drop-in for the baseline** | no |

## Gotchas

- 'Matches the CPU msdfgen baseline' means median-of-channels within loose tolerances on five Roboto glyphs at 48 px. Edge colouring differs from msdfgen, so individual channels are not comparable, and corners diverge because the compute path extrapolates pseudo-distance from a flattened polyline.
- A plain cargo test does not exercise the compute path: GPU tests need --features gpu-tests (plus cpu-bake for the msdfgen comparison) and the LLVM backend, and they print 'SKIP: no GPU adapter' and pass when no adapter is found.
- Each generate_cell or generate_into_texture call creates three new buffers and a bind group and submits its own command buffer, so bulk atlas generation is not batched.
- Fixed caps: 4096 draw commands, 4096 glyph-table entries and 8 texture layers per renderer; glyph ids are u16, and styled faces are addressed through a prefixed glyph id.

## Known shortcomings

- Tier D: an output-parity claim against msdfgen with no timings anywhere; PLAN.md is a 404 and the README names wgpu 29 while Cargo.toml pins 30.0.1. Kept under the keep-and-document rule.
- Enricher (e128, 2026-10-05): tier D stands, no timings anywhere. The parity claim is loose: tests/compute_msdf.rs allows a mean median deviation of 0.13 with 35% of texels beyond 0.125 ('#' at 0.114). Brute-force per-texel edge loop with no batching; the fragment shader loops over all draw commands per pixel; publish = false in Cargo.toml; GPU tests skip-pass when no adapter is present.

## Caveats and trade-offs

Tier D with nothing to measure: the README's only claim is that runtime compute-shader MSDF generation matches the CPU msdfgen baseline (output parity, not speed); PLAN.md, which the README cites, returns 404 on raw.githubusercontent.com; there is no benchmark directory. The CPU msdfgen reference path uses the msdfgen Rust crate (C++ FFI) behind the off-by-default cpu-bake feature and cannot build for wasm32; GPU tests are behind the gpu-tests feature and need the LLVM backend on macOS. README still says wgpu 29 while Cargo.toml was bumped to wgpu 30.0.1 on 2026-09-26. Very new (oldest commit on the first commits page is 2026-08-12, with older pages), zero stars and forks, Cargo.toml has publish = false, extracted from the matter-stream render crates. Not notable by the tier D rule; kept under the keep-and-document rule because the seed pass asked for a record per listed project.

wgpu 30 SDF primitive and MSDF text renderer with rustybuzz shaping; runs native and wasm32/WebGPU; the CPU msdfgen path is optional (cpu-bake feature, C++ FFI, cannot build for wasm32). The runtime generator is the only way to get MSDF on wasm32.

## Maintenance

Active (last commit 2026-09-26, 60 commits since August 2026) and MIT OR Apache-2.0, but unpublished, single-author and tied to highbay, so vendoring the WGSL shader is safer than depending on the crate.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification D, tier now D.
- **Tier reason:** No benchmark_url and no timing, fps or speed ratio anywhere reachable: the README only says the runtime WGSL compute-shader MSDF generation matches the CPU msdfgen baseline (an output-parity claim), Cargo.toml gates the msdfgen comparison behind the cpu-bake and gpu-tests features, and no commit message on the first commits page mentions benchmarks or performance.
- **Verifier notes:** The prompt's not-notable-tier-d rule would reject this, but there is no invalid or fabricated evidence, so per the orchestrator's keep-and-document rule it is confirmed at D with the shortcomings stated. License MIT OR Apache-2.0 confirmed in Cargo.toml and both LICENSE files; last commit 2026-09-26 confirmed; the 60-commit count was not rechecked.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** none
- **Pages the verifier opened:**
  - <https://github.com/tmzt/libmsdf>
  - <https://github.com/tmzt/libmsdf/commits/main>
  - <https://raw.githubusercontent.com/tmzt/libmsdf/HEAD/README.md>
  - <https://raw.githubusercontent.com/tmzt/libmsdf/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/tmzt/libmsdf/HEAD/LICENSE-MIT>
  - <https://raw.githubusercontent.com/tmzt/libmsdf/HEAD/LICENSE-APACHE>
  - <https://raw.githubusercontent.com/tmzt/libmsdf/HEAD/PLAN.md>
- **Sources the enricher read:**
  - <https://github.com/tmzt/libmsdf>
  - <https://github.com/tmzt/libmsdf/commits/main>
  - <https://github.com/tmzt/libmsdf/tree/main/src/gpu>
  - <https://github.com/tmzt/libmsdf/tree/main/src/font>
  - <https://github.com/tmzt/libmsdf/tree/main/tests>
  - <https://github.com/tmzt/libmsdf/tree/main/examples>
  - <https://raw.githubusercontent.com/tmzt/libmsdf/HEAD/README.md>
  - <https://raw.githubusercontent.com/tmzt/libmsdf/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/tmzt/libmsdf/HEAD/build.rs>
  - <https://raw.githubusercontent.com/tmzt/libmsdf/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/tmzt/libmsdf/HEAD/src/gpu/mod.rs>
  - <https://raw.githubusercontent.com/tmzt/libmsdf/HEAD/src/gpu/compute.rs>
  - <https://raw.githubusercontent.com/tmzt/libmsdf/HEAD/src/gpu/msdf_compute.wgsl>
  - <https://raw.githubusercontent.com/tmzt/libmsdf/HEAD/src/gpu/sdf_render.wgsl>
  - <https://raw.githubusercontent.com/tmzt/libmsdf/HEAD/src/font/outline.rs>
  - <https://raw.githubusercontent.com/tmzt/libmsdf/HEAD/src/font/atlas.rs>
  - <https://raw.githubusercontent.com/tmzt/libmsdf/HEAD/src/font/shaper.rs>
  - <https://raw.githubusercontent.com/tmzt/libmsdf/HEAD/src/font/manager.rs>
  - <https://raw.githubusercontent.com/tmzt/libmsdf/HEAD/tests/compute_msdf.rs>
  - <https://raw.githubusercontent.com/tmzt/libmsdf/HEAD/examples/bake_atlas.rs>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/tmzt/libmsdf`) · [data/wave10/enrich/raw/github_com_tmzt_libmsdf.json](../../../data/wave10/enrich/raw/github_com_tmzt_libmsdf.json) (enrichment confidence 0.7)

</details>
