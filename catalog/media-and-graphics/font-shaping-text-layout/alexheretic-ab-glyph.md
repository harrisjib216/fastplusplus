# ab_glyph

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Font shaping and text layout](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0` · 🟢 active

> Pure-Rust glyph loading, scaling, positioning and rasterization crate; rewrite of rusttype with cheaper per-glyph layout, especially for CFF fonts.

| | |
|---|---|
| **Beats** | rusttype 0.9 (Rust OpenType/TrueType glyph layout and rasterization crate, which describes itself as a pure Rust alternative to FreeType) |
| **Claimed result** | layout_a_sentence exo2-ttf: ab-glyph 11.1us vs rusttype 17.3us (1.56x faster per the table); exo2-otf: ab-glyph 11.1us vs rusttype 98.1us (8.85x faster per the table). README text: 'faster than rusttype using .ttf fonts & much faster for .otf fonts'. |
| **Workload** | Criterion benchmark layout_a_sentence: laying out the glyphs of one sentence into a paragraph with the exo2 font, as .ttf and as .otf. |
| **Metric** | latency |
| **Adoption** | 454 stars, 27 forks; ab_glyph crate about 45.2 million crates.io downloads (10.9 million recent), version 0.2.32 |
| **Last commit** | 2026-08-30 |
| **Links** | [repository](https://github.com/alexheretic/ab-glyph) · [benchmark](https://raw.githubusercontent.com/alexheretic/ab-glyph/main/glyph/README.md) |

## Verdict

First-party Criterion runs from May 2020 (ab_glyph 0.1 against rusttype 0.9; rustc version, flags and CPU not stated) laid out one 225-character sentence with Exo2 Light at 25 px: 11.1 us vs 17.3 us for .ttf (1.56x) and 11.1 us vs 98.1 us for .otf (8.85x); the first README version (2020-05-08) also showed an OpenSans-Italic .ttf row at 19.3 vs 25.3 us (1.31x) that was removed three days later in 'Simplify bench comparison'. The two harnesses do different work: rusttype's layout computes a pixel bounding box per glyph (a stored glyf bbox read for .ttf, a full CFF outline pass for .otf in ttf-parser 0.5/0.6) while ab_glyph defers it and additionally wraps lines at 600 px, so the ratio measures work avoided by ab_glyph's API rather than the same computation done faster.

## Use it when

- Rust code that needs char-to-glyph mapping, advances, simple kerning and coverage rasterization of individual glyphs (game UIs, GPU text atlases via glyph_brush, plotting and image libraries such as plotters and imageproc already depend on it).
- Migrating from rusttype 0.9, especially with CFF .otf fonts: layout cost no longer depends on outline complexity (the 2020 table shows ab_glyph at 11.1 us for both the Exo2 .ttf and .otf, rusttype at 17.3 us and 98.1 us).
- no_std or wasm targets: CI builds both crates for thumbv6m-none-eabi (no default features, libm) and wasm32-unknown-unknown; FontArc works on no_std targets with pointer atomics since 0.2.32.
- Left-to-right scripts without contextual shaping, where per-pair kerning from a legacy 'kern' table (or none) is acceptable.
- When you want a widely deployed, small-dependency crate: about 45.2 million crates.io downloads and 269 reverse dependencies.

## Skip it when

- Complex scripts, ligatures, mark positioning or any OpenType feature: there is no GSUB/GPOS support (issue #74 'OTF feature tags' open since 2023-02); use HarfBuzz/HarfRust or a layout stack such as Parley or cosmic-text.
- Fonts that kern only through GPOS (common in modern OpenType fonts): `kern` reads only the legacy 'kern' table subtables, so those pairs come back unkerned.
- Raw rasterization throughput is the bottleneck: sibling entries report faster pure-Rust rasterizers (fontdue's own plots versus ab_glyph 0.2.3; TiTanF's README medians put Fontdue ahead of ab_glyph at 10-160 px). There is no hinting, so small-size output will not match FreeType hinted rendering.
- Supply-chain policies that block unmaintained dependencies: ttf-parser, its parsing backend, is flagged RUSTSEC-2026-0192 (informational, unmaintained, 2026-06-28); the Skrifa port (PR #122) is a draft, needs a breaking release, and its author measured it slower (about 70 us TrueType and 90 us CFF vs about 55 us with ttf-parser on the layout-and-outline benchmark).
- C or C++ projects: it is a Rust crate with no C API; calling it from C++ requires your own FFI layer.

## How it is fast

Mostly API design: layout yields lightweight `Glyph` values and defers outlining and bounding boxes until `outline_glyph`/`glyph_bounds`, whereas rusttype 0.9's `positioned()` computed a pixel bounding box for every glyph during layout via ttf-parser `glyph_bounding_box`, which for CFF fonts runs the full charstring outliner (ttf-parser 0.5/0.6 read the stored glyf bbox for .ttf but outlined CFF glyphs) - this is where the large .otf gap comes from. Since 0.2.12 it also pre-parses the Unicode cmap and horizontal kern subtables once at font load (owned_ttf_parser `PreParsedSubtables`), which the changelog credits with 25-30% faster layout benchmarks. The rasterizer is a font-rs-derived signed-area accumulation rasterizer: line segments add signed coverage deltas into a float buffer and one running-sum pass (`for_each_pixel`) produces coverage; quadratics are flattened by a deviation-based segment count and cubics by stb_truetype-style recursive midpoint subdivision. Line drawing is the same scalar code compiled with `#[target_feature(enable = "avx2")]` and `sse4.2` and chosen once at runtime (compiler auto-vectorization, no hand-written intrinsics).

## Compared with alternatives

Pick ab_glyph over fontdue or TiTanF when you need CFF .otf and variable-font support, no_std, and compatibility with the glyph_brush/imageproc/plotters ecosystem, accepting a slower rasterizer by those projects' own measurements; it is a higher-level glyph API than Fontations' skrifa or ttf-parser (which it builds on), and it does no shaping, so Parley or a HarfBuzz port is the choice once text needs real OpenType layout.

## Integration

| | |
|---|---|
| **Form** | crate (ab_glyph plus the separately published ab_glyph_rasterizer) |
| **Dependencies** | owned_ttf_parser 0.25 (wraps ttf-parser), ab_glyph_rasterizer 0.1 (no dependencies); optional libm for no_std |
| **Minimum toolchain** | Latest stable Rust only (README policy; no rust-version field in Cargo.toml); edition 2021 |
| **Platforms** | any Rust target; CI tests on ubuntu-latest (x86-64) and builds thumbv6m-none-eabi (no_std + libm) and wasm32-unknown-unknown; runtime AVX2/SSE4.2 dispatch for line drawing on x86/x86_64 with the std feature |
| **Thread safety** | FontArc wraps `Arc<dyn Font + Send + Sync>` for sharing a font across threads; each `OutlinedGlyph::draw` call builds its own Rasterizer, so drawing holds no shared mutable state. No further thread-safety documentation. |
| **Drop-in for the baseline** | partial - same author and concepts as rusttype, but a different API: no Font::layout iterator, no PositionedGlyph with pixel bounds, no gpu_cache; ports need code changes |

## Gotchas

- Coverage values are not clamped: since ab_glyph_rasterizer 0.1.5 a value of 1.0 or more means fully covered. Open issue #121 (2025-08-20) reports tiny non-zero coverage (about 1.6e-7) outside glyphs from floating-point cancellation in draw_line_scalar, visible as shadows when glyphs are drawn repeatedly; the reporter's workaround rounds coverage.
- Out-of-bounds panics in draw_line_scalar were fixed in three rounds (rasterizer 0.1.3, 0.1.9 in 2025-06, 0.1.10 in 2025-08); make sure the lockfile has ab_glyph_rasterizer 0.1.10 or later.
- `OutlinedGlyph::draw` allocates a fresh width x height float buffer for every call; cache rasterized glyphs (as glyph_brush does) rather than redrawing per frame.
- Missing characters map silently to GlyphId(0) (.notdef) rather than returning None; some `Font` default methods return None or 0.0 where fonts lack data (issue #99 open).

## Known shortcomings

- Off-baseline (rusttype, not FreeType or HarfBuzz); the README critcmp table (1.56x TTF, 8.85x OTF) dates from May 2020 with no rustc, CPU or machine stated, the current dev/benches/layout.rs no longer includes rusttype, and the rusttype bench does single-line layout while ab-glyph also wraps.

## Caveats and trade-offs

Baseline is rusttype 0.9, the crate ab_glyph replaced (same author added .otf support to rusttype), not HarfBuzz or FreeType; off the category's C/C++ baselines and the README does not compare with FreeType. Numbers are first-party and dated May 2020 (README notes performance has likely improved since); rustc version, CPU and machine are not stated; the workspace Cargo.toml currently sets [profile.bench] lto = "thin". The current dev/benches/layout.rs benchmarks ab_glyph only, so the rusttype column cannot be re-run from this repo; rusttype's own dev/benches/layout.rs (redox-os/rusttype mirror) has matching layout_a_sentence (exo2-ttf/otf) benches. The two harnesses are not identical: rusttype's bench calls font.layout (single line, kerning and advance) while ab-glyph's calls dev::layout_paragraph (kerning, advance plus wrapping at 600 px), so ab-glyph does slightly more work per glyph. Layout only; glyph rasterization speed is not compared. Both libraries do simple positioning, not OpenType shaping (no ligatures or GSUB/GPOS).

Rust crate (callable from C++ only through FFI). Loads, scales, positions and rasterizes glyphs; it does no complex-script shaping, so it is not a HarfBuzz replacement. no_std supported with libm. Rasterization comes from the companion ab_glyph_rasterizer crate, which is inspired by font-rs and stb_truetype.

## Maintenance

Apache-2.0 and copyable; last release ab_glyph 0.2.32 on 2025-09-28 with only lint, CI and test-hash commits since (latest 2026-08-30), so effectively in maintenance mode while the unmaintained ttf-parser backend awaits the draft Skrifa port.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** glyph/README.md carries a critcmp-style table (ab-glyph 11.1us vs rusttype 0.9 17.3us ttf, 98.1us otf; ratios 1.56 and 8.85 printed on the page) from May 2020 Criterion runs; the rusttype side matches rusttype's own dev/benches/layout.rs (same sentence, Exo2 fonts), but rustc version, CPU and machine are never stated and the current ab-glyph dev/benches/layout.rs no longer includes a rusttype run, so first-party with partial methodology.
- **Verifier notes:** Numbers and ratios match the README exactly; metadata (Apache-2.0, last commit 2026-08-30, active, not a fork) verified on github.com and glyph/Cargo.toml. Keep as an off-baseline Rust entry with the rusttype-only comparison flagged.
- **Fields the verifier corrected:** `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/alexheretic/ab-glyph/main/glyph/README.md>
  - <https://raw.githubusercontent.com/alexheretic/ab-glyph/main/README.md>
  - <https://raw.githubusercontent.com/alexheretic/ab-glyph/main/Cargo.toml>
  - <https://raw.githubusercontent.com/alexheretic/ab-glyph/main/dev/Cargo.toml>
  - <https://raw.githubusercontent.com/alexheretic/ab-glyph/main/dev/benches/layout.rs>
  - <https://raw.githubusercontent.com/alexheretic/ab-glyph/main/dev/benches/layout_draw.rs>
  - <https://raw.githubusercontent.com/alexheretic/ab-glyph/main/dev/src/lib.rs>
  - <https://raw.githubusercontent.com/alexheretic/ab-glyph/main/dev/src/layout.rs>
  - <https://raw.githubusercontent.com/alexheretic/ab-glyph/main/glyph/Cargo.toml>
  - <https://raw.githubusercontent.com/redox-os/rusttype/master/dev/benches/layout.rs>
  - <https://raw.githubusercontent.com/redox-os/rusttype/master/dev/Cargo.toml>
  - <https://raw.githubusercontent.com/redox-os/rusttype/master/Cargo.toml>
  - <https://raw.githubusercontent.com/redox-os/rusttype/master/README.md>
  - <https://github.com/alexheretic/ab-glyph>
  - <https://github.com/alexheretic/ab-glyph/commits/main>
  - <https://crates.io/api/v1/crates/ab_glyph>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/alexheretic/ab-glyph/main/README.md>
  - <https://raw.githubusercontent.com/alexheretic/ab-glyph/main/glyph/README.md>
  - <https://raw.githubusercontent.com/alexheretic/ab-glyph/main/Cargo.toml>
  - <https://raw.githubusercontent.com/alexheretic/ab-glyph/main/glyph/Cargo.toml>
  - <https://raw.githubusercontent.com/alexheretic/ab-glyph/main/rasterizer/Cargo.toml>
  - <https://raw.githubusercontent.com/alexheretic/ab-glyph/main/rasterizer/README.md>
  - <https://raw.githubusercontent.com/alexheretic/ab-glyph/main/dev/Cargo.toml>
  - <https://raw.githubusercontent.com/alexheretic/ab-glyph/main/dev/benches/layout.rs>
  - <https://raw.githubusercontent.com/alexheretic/ab-glyph/main/dev/benches/layout_draw.rs>
  - <https://raw.githubusercontent.com/alexheretic/ab-glyph/main/dev/benches/rasterize.rs>
  - <https://raw.githubusercontent.com/alexheretic/ab-glyph/main/dev/benches/font_method.rs>
  - <https://raw.githubusercontent.com/alexheretic/ab-glyph/main/dev/src/layout.rs>
  - <https://raw.githubusercontent.com/alexheretic/ab-glyph/main/dev/src/lib.rs>
  - <https://raw.githubusercontent.com/alexheretic/ab-glyph/main/glyph/CHANGELOG.md>
  - <https://raw.githubusercontent.com/alexheretic/ab-glyph/main/rasterizer/CHANGELOG.md>
  - <https://raw.githubusercontent.com/alexheretic/ab-glyph/main/glyph/src/lib.rs>
  - <https://raw.githubusercontent.com/alexheretic/ab-glyph/main/glyph/src/ttfp.rs>
  - <https://raw.githubusercontent.com/alexheretic/ab-glyph/main/glyph/src/ttfp/outliner.rs>
  - <https://raw.githubusercontent.com/alexheretic/ab-glyph/main/glyph/src/font.rs>
  - <https://raw.githubusercontent.com/alexheretic/ab-glyph/main/glyph/src/outlined.rs>
  - <https://raw.githubusercontent.com/alexheretic/ab-glyph/main/glyph/src/font_arc.rs>
  - <https://raw.githubusercontent.com/alexheretic/ab-glyph/main/glyph/src/scale.rs>
  - <https://raw.githubusercontent.com/alexheretic/ab-glyph/main/rasterizer/src/lib.rs>
  - <https://raw.githubusercontent.com/alexheretic/ab-glyph/main/rasterizer/src/raster.rs>
  - <https://raw.githubusercontent.com/alexheretic/ab-glyph/main/.github/workflows/ci.yml>
  - <https://raw.githubusercontent.com/alexheretic/ab-glyph/394f70f/glyph/README.md>
  - <https://raw.githubusercontent.com/alexheretic/ab-glyph/394f70f/dev/benches/layout.rs>
  - <https://raw.githubusercontent.com/alexheretic/ab-glyph/394f70f/dev/Cargo.toml>
  - <https://raw.githubusercontent.com/alexheretic/ab-glyph/537037b/glyph/README.md>
  - <https://raw.githubusercontent.com/alexheretic/ab-glyph/537037b/dev/benches/layout.rs>
  - <https://github.com/alexheretic/ab-glyph/commits/main/glyph/README.md>
  - <https://github.com/alexheretic/ab-glyph/commits/main>
  - <https://github.com/alexheretic/ab-glyph/issues>
  - <https://github.com/alexheretic/ab-glyph/issues/121>
  - <https://github.com/alexheretic/ab-glyph/issues/125>
  - <https://github.com/alexheretic/ab-glyph/pulls?q=is%3Apr>
  - <https://github.com/alexheretic/ab-glyph/pull/122>
  - <https://raw.githubusercontent.com/redox-os/rusttype/master/dev/benches/layout.rs>
  - <https://raw.githubusercontent.com/redox-os/rusttype/master/Cargo.toml>
  - <https://raw.githubusercontent.com/redox-os/rusttype/master/CHANGELOG.md>
  - <https://raw.githubusercontent.com/redox-os/rusttype/master/src/lib.rs>
  - <https://raw.githubusercontent.com/redox-os/rusttype/master/src/font.rs>
  - <https://raw.githubusercontent.com/harfbuzz/ttf-parser/master/src/lib.rs>
  - <https://raw.githubusercontent.com/harfbuzz/ttf-parser/v0.6.0/src/lib.rs>
  - <https://raw.githubusercontent.com/harfbuzz/ttf-parser/v0.5.0/src/lib.rs>
  - <https://raw.githubusercontent.com/alexheretic/owned-ttf-parser/main/src/preparse.rs>
  - <https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/ttf-parser/RUSTSEC-2026-0192.md>
  - <https://crates.io/api/v1/crates/ab_glyph>
  - <https://crates.io/api/v1/crates/ab_glyph/reverse_dependencies?per_page=15>
  - <https://raw.githubusercontent.com/alexheretic/ab-glyph/main/glyph/src/glyph.rs>
  - <https://raw.githubusercontent.com/alexheretic/ab-glyph/main/glyph/src/variable.rs>
  - <https://raw.githubusercontent.com/alexheretic/ab-glyph/main/rasterizer/src/geometry.rs>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/alexheretic/ab-glyph`) · [data/wave10/enrich/raw/github_com_alexheretic_ab_glyph.json](../../../data/wave10/enrich/raw/github_com_alexheretic_ab_glyph.json) (enrichment confidence 0.8)

</details>
