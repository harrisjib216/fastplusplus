# Pathfinder 3

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [2D rasterizers](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Rust (with C bindings via cargo-c)` · `MIT OR Apache-2.0` · 🟢 active

> Rust GPU rasterizer for glyphs and vector paths (OpenGL, Metal, WebGL 2); claims to match or beat CPU rasterizers, with no numbers.

| | |
|---|---|
| **Beats** | Unnamed 'best CPU rasterizers' (README). FreeType, stb_truetype and font-rs are named as comparison points only in the 2017 Pathfinder 1 blog post (pcwalton.github.io), which is blocked here and is known only from a search snippet. |
| **Claimed result** | README: 'Even on lower-end GPUs, Pathfinder often matches or exceeds the performance of the best CPU rasterizers. The difference is particularly pronounced at large sizes, where Pathfinder regularly achieves multi-factor speedups.' No numbers. |
| **Workload** | GPU (OpenGL, Metal, WebGL) rasterization of font glyphs and vector paths with exact-coverage anti-aliasing, tiled and compute-based. |
| **Metric** | throughput |
| **Adoption** | 3.9k stars; developed for Mozilla Servo |
| **Last commit** | 2026-04-23 |
| **Links** | [repository](https://github.com/servo/pathfinder) |

## Verdict

There is no measurement against any baseline. The README claims Pathfinder 'often matches or exceeds' unnamed 'best CPU rasterizers', with 'multi-factor speedups' at large sizes. doc/architecture.md quotes only absolute Pathfinder 3 stage times for the Ghostscript tiger at 1600x1600 on an i7-7920HQ with Intel HD Graphics 630 (about 2.2 ms CPU tile/cull/pack, 2.6 ms GPU fill, 2.3 ms GPU shade). An independent 2019 write-up by Mozilla's Nicolas Silva says only that it is 'a good deal faster at rendering very large and complex SVG drawings than using a CPU rasterizer and uploading the result to a texture', also without numbers, so tier D stands.

## Use it when

- Rust apps, or C/C++ apps willing to link a Rust static library, that already render with OpenGL or Metal and draw large, zoomed or per-frame-transformed text and vector paths, where CPU rasterize-and-upload is the bottleneck.
- Complex SVG- or PDF-like scenes with heavy overlap, where tile occlusion culling skips hidden geometry.
- Text placed in 3D or VR scenes, or animated in size, where a glyph-atlas cache from a CPU rasterizer keeps getting invalidated.
- As a readable reference design for tiled GPU vector rendering with exact area coverage.

## Skip it when

- You need CPU bitmaps or a glyph atlas (headless servers, no GPU, software fallback): use FreeType, fontdue or font-rs. Reading pixels back from the GPU gives up the advantage.
- You need shaping or line layout: Pathfinder delegates that to skribo/HarfBuzz, and the record's category fit is approximate.
- You want a stable, versioned dependency: the crates.io releases of pathfinder_canvas, pathfinder_renderer and pathfinder_text are still 0.5.0 from 2020-04-17, and that pathfinder_renderer has no D3D11 compute mode at all (checked in the 0.5.0 crate source), so the compute path the README highlights needs a git dependency on main. The README itself says 'under heavy development and is incomplete'.
- C or C++ projects that want a native library: the C bindings are 'less complete' (README), produce a static library only, need a Rust toolchain plus cargo-c, and pin old dependencies (font-kit 0.6, usvg 0.9).
- Small UI text on low-end hardware, where the README itself only claims to 'often match' CPU rasterizers, or CPUs without SSE4.1 (see gotchas).

## How it is fast

Paths are cut into 16x16 tiles. Tiles that are entirely one solid colour are flagged, and tiles hidden behind them are culled before any GPU work, which avoids the overdraw of painter's-algorithm software renderers. Edges are rasterized into a 16-bit float coverage mask with exact trapezoidal area coverage (described as effectively 256xAA), and tiles are then shaded back to front from that mask. At the 'D3D9' level (OpenGL 3/WebGL 2) binning and tiling run on the CPU with SIMD (pathfinder_simd) and Rayon, pipelined with the GPU. At the 'D3D11' level (OpenGL 4.3, Metal) bin, fill and composite all run in GPU compute shaders. Because GPU fill parallelises across pixels while CPU rasterizer cost grows with pixel area, the claimed advantage is largest at large glyph sizes.

## Compared with alternatives

The other entries in this category are CPU glyph rasterizers (font-rs, fontdue, TiTanF) or, in msdfgl's case, GPU atlas generators. Pick Pathfinder only when glyphs are drawn directly on the GPU at large or changing sizes and transforms. Pick fontdue or font-rs for CPU bitmaps and atlases at UI sizes, and msdfgl for scalable atlas-based text. For general GPU vector rendering, Vello (rasterizers-2d) is the actively developed compute renderer with third-party measurements.

## Integration

| | |
|---|---|
| **Form** | crate (modular pathfinder_\* Rust crates); static lib with a C API via cargo-c |
| **Dependencies** | rayon, font-kit, skribo (HarfBuzz), usvg/resvg for SVG, gl or metal bindings, half, hashbrown and others; C build needs cargo-c |
| **Minimum toolchain** | not documented; Rust 2018 edition, CI builds on stable Rust; no rust-version declared on crates.io |
| **Platforms** | Needs a GPU: OpenGL 3.0+/ES 3.0+, WebGL 2 or Metal ('D3D9' level, CPU binning); compute 'D3D11' level needs OpenGL 4.3 or Metal. CPU side: x86-64 (SIMD paths assume SSE4.1) and aarch64 (CI cross-builds the simd and geometry crates) |
| **Thread safety** | not documented; scene building runs on a Rayon executor (SceneProxy), and rendering is tied to the caller's GL or Metal context |
| **Drop-in for the baseline** | no |

## Gotchas

- pathfinder_simd calls SSE4.1 intrinsics (_mm_floor_ps, _mm_ceil_ps, _mm_min_epi32, _mm_max_epi32, _mm_mullo_epi32) from safe APIs without a target-feature check, so pre-SSE4.1 x86 CPUs hit undefined behaviour or illegal-instruction crashes. Issues #502 (2022) and #588 (May 2026) are open with no fix.
- Which level you get is decided per device (RendererLevel::default_for_device): on WebGL 2 and other GL 3.x devices, tiling stays on the CPU, so very complex scenes can be CPU-bound (issue #228, 'High CPU overhead on very complex scenes').
- crates.io 0.5.0 (2020) and git main differ substantially (no compute mode in 0.5.0), so examples and docs on main may not match the published crates.
- Font hinting is limited to 'slight' hinting, and stem darkening is optional, so small-size output will not match FreeType's full hinting.

## Known shortcomings

- Tier D: README is qualitative, no named baseline or number in the repo; the 2017 blog post is blocked here and its source repo is 404. Rust library (language-filter mismatch). Kept as notable (3.9k stars, Servo).
- No number against any baseline (tier D): doc/architecture.md gives absolute tiger 1600x1600 timings (2.2, 2.6 and 2.3 ms on an i7-7920HQ with HD 630) with no comparison, and the nical 2019 post is qualitative. crates.io renderer, canvas and text crates are stuck at 0.5.0 (2020-04-17) without the D3D11 compute mode; recent activity is pathfinder_simd 0.5.6 upkeep; open SSE4.1 undefined-behaviour issues #502 and #588. Category moved to rasterizers-2d.

## Caveats and trade-offs

Qualitative claim with no named baseline and no numbers in the repo. The only numbers known are in the 2017 Pathfinder 1 blog post (pcwalton.github.io, blocked here; its source repo is not on GitHub), which predates Pathfinder 3; a search snippet calls that FreeType comparison chart dated and says FreeType has improved since. GPU-only (OpenGL 3+/ES 3+/WebGL 2/Metal), so it is not a drop-in replacement for a CPU rasterizer. The README still says 'under heavy development and is incomplete in various areas', and the C bindings are less complete than the Rust API. Commits from 2024 to 2026 are mostly build and SIMD fixes (last 2026-04-23), and the latest tags are preview-3 (2019) and pathfinder_simd-v0.5.4 (2024). Treat as a lead.

Needs a GPU and OpenGL 3.0+/ES 3.0+/WebGL 2/Metal; not a drop-in FreeType replacement (no hinting beyond slight hinting, no shaping). Callable from C or C++ through the C bindings, which the README calls less complete than the Rust API. README says it is under heavy development and incomplete.

## Maintenance

The repo is technically active (last commit 2026-04-23), but the activity is SIMD and build upkeep: the renderer has had no release since 0.5.0 in 2020, and the README still says it is under heavy development. MIT OR Apache-2.0 makes it easy to adopt from git main, but plan to own your fork.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification D, tier now D.
- **Tier reason:** The README makes only a qualitative claim ('often matches or exceeds the performance of the best CPU rasterizers ... multi-factor speedups' at large sizes) against unnamed CPU rasterizers. No benchmark numbers are in the repo (README, doc/architecture.md, site/index.html), so tier D.
- **Verifier notes:** Kept at tier D rather than rejected because the project is notable (3.9k stars, Mozilla Servo). It is Rust with C bindings, which does not match a C++ language filter. It is a GPU glyph and vector rasterizer, not a shaper or layout engine, so the category fit is approximate. Metadata confirmed: MIT OR Apache-2.0, last commit 2026-04-23, not archived, not a fork.
- **Fields the verifier corrected:** `baseline`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/servo/pathfinder/main/README.md>
  - <https://raw.githubusercontent.com/servo/pathfinder/main/site/index.html>
  - <https://raw.githubusercontent.com/servo/pathfinder/main/doc/architecture.md>
  - <https://github.com/servo/pathfinder>
  - <https://github.com/servo/pathfinder/commits/main>
  - <https://github.com/servo/pathfinder/tags>
  - <https://github.com/servo/pathfinder/tree/main/site>
  - <https://github.com/servo/pathfinder/tree/main/doc>
- **Sources the enricher read:**
  - <https://github.com/servo/pathfinder>
  - <https://raw.githubusercontent.com/servo/pathfinder/main/README.md>
  - <https://raw.githubusercontent.com/servo/pathfinder/main/Cargo.toml>
  - <https://raw.githubusercontent.com/servo/pathfinder/main/doc/architecture.md>
  - <https://raw.githubusercontent.com/servo/pathfinder/main/c/Cargo.toml>
  - <https://raw.githubusercontent.com/servo/pathfinder/main/c/src/lib.rs>
  - <https://raw.githubusercontent.com/servo/pathfinder/main/text/Cargo.toml>
  - <https://raw.githubusercontent.com/servo/pathfinder/main/text/src/lib.rs>
  - <https://raw.githubusercontent.com/servo/pathfinder/main/canvas/Cargo.toml>
  - <https://raw.githubusercontent.com/servo/pathfinder/main/renderer/Cargo.toml>
  - <https://raw.githubusercontent.com/servo/pathfinder/main/renderer/src/gpu/options.rs>
  - <https://raw.githubusercontent.com/servo/pathfinder/main/demo/common/src/lib.rs>
  - <https://raw.githubusercontent.com/servo/pathfinder/main/.github/workflows/main.yml>
  - <https://github.com/servo/pathfinder/tree/main/c>
  - <https://github.com/servo/pathfinder/tree/main/examples>
  - <https://github.com/servo/pathfinder/issues?q=is%3Aissue+slow+OR+performance+OR+benchmark>
  - <https://github.com/servo/pathfinder/issues/588>
  - <https://github.com/servo/pathfinder/issues/496>
  - <https://crates.io/api/v1/crates/pathfinder_canvas>
  - <https://crates.io/api/v1/crates/pathfinder_renderer>
  - <https://crates.io/api/v1/crates/pathfinder_simd>
  - <https://crates.io/api/v1/crates/pathfinder_text>
  - <https://crates.io/api/v1/crates/pathfinder_renderer/0.5.0/download>
  - <https://raw.githubusercontent.com/nical/nical.github.io/master/posts/a-look-at-pathfinder.html>
  - <https://github.com/nical/nical.github.io>
  - <https://github.com/intel/fastuidraw>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/servo/pathfinder`) · [data/wave10/enrich/raw/github_com_servo_pathfinder.json](../../../data/wave10/enrich/raw/github_com_servo_pathfinder.json) (enrichment confidence 0.75)

</details>
