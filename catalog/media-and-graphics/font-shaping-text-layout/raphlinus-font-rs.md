# font-rs

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Font shaping and text layout](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust (optional C SSE3 intrinsics module)` · `Apache-2.0` · 🔴 abandoned

> Small Rust TrueType glyph rasterizer (dense accumulation buffer plus prefix sum); 2016 author numbers claim 4-7.6x over FreeType 2.6.5.

| | |
|---|---|
| **Beats** | FreeType 2.6.5 (glyph rasterization), per search snippets of the author's post; freetype-go is mentioned qualitatively in the README |
| **Claimed result** | Repo README: 'extremely promising performance compared with Freetype and freetype-go', no numbers. Snippet only (the author's Medium post 'Inside the fastest font renderer in the world', 2016, is blocked): with the SIMD speedup about 7.6x faster than FreeType 2.6.5 at larger sizes (the post notes 42 px/em as the xxhdpi Android default), over 4x faster at 12 pixels/em, and over 6x at 12 pixels/em on a CJK typeface. |
| **Workload** | Time to render the glyph 'g' from Roboto Regular at sizes from 1 to 200 pixels/em with an accumulation-buffer rasterizer (libart-style exact area coverage) and an optional SSE3 cumulative-sum step (methodology from search snippets of the blocked Medium post). The repo's own benches render glyph 200 of NotoMono-Regular at 10-400 px and a synthetic shape, font-rs only. |
| **Metric** | throughput |
| **Hardware** | 2.9 GHz Xeon E5-2690 (search snippet only) |
| **Adoption** | 774 stars; algorithm lineage of fontdue and ab_glyph_rasterizer |
| **Last commit** | 2020-09-05 |
| **Links** | [repository](https://github.com/raphlinus/font-rs) · [benchmark](https://medium.com/@raphlinus/inside-the-fastest-font-renderer-in-the-world-75ae5270c445) |

## Verdict

Snippet only: the author's 2016 post timed rendering the glyph 'g' from Roboto Regular at 1-200 px/em on a 2.9 GHz Xeon E5-2690 against FreeType 2.6.5 and reports about 7.6x faster at larger sizes with the SIMD accumulate, over 4x at 12 px/em and over 6x at 12 px/em on a CJK face. FreeType's load flags and hinting mode, the compilers and the harness could not be checked (the post and the freetype-devel threads are blocked), and the repo's benches time font-rs alone; the measured code was the 2016 C SSE3 accumulate, which master replaced with a Rust std::arch port in 2018.

## Use it when

- Learning, porting or vendoring the original dense accumulation rasterizer: src/raster.rs plus src/accumulate.rs are about 230 lines of Apache-2.0 Rust excluding tests, and fontdue, ab_glyph_rasterizer and golang.org/x/image/vector follow the same design.
- Rasterizing grayscale coverage masks for a glyph atlas from trusted TrueType (glyf) fonts at integer pixel sizes, in Rust, with zero crate dependencies.
- Larger glyph sizes, where the author's snippet-only 2016 numbers show the widest gap to FreeType (about 7.6x with the SIMD accumulate).
- As a reference implementation when writing a C++ rasterizer: the algorithm is short enough to port directly, and FreeType's own GSoC 2022 'dense' module (branch gsoc-anurag-2022-final, src/dense) is a C port of it.

## Skip it when

- Untrusted or user-supplied fonts: parse() unwraps missing head/maxp tables and slices table offsets without range checks, so malformed files panic (issues #12 'Out-of-bounds path nodes shouldn't panic' and #44 'Potential wrapping add' are still open).
- CFF/CFF2 OpenType, variable fonts, colour or bitmap glyphs, or code points above U+FFFF (only cmap format 4 is read; lookup_glyph_id returns None above 0xFFFF).
- Small UI text that needs hinting or LCD subpixel rendering, or text that needs fractional sizes or subpixel x positions (size is a u32 and the glyph origin is snapped to whole pixels).
- Projects that need a maintained dependency: last commit 2020-09-05, 9 open issues, 3 open PRs, and the crates.io release (0.1.3, 2018-07-09, 8,212 downloads, one reverse dependency) predates the Rust SIMD port, the metrics API and the out-of-bounds fixes on master.
- Expecting the 2016 gap against current FreeType: FreeType's smooth rasterizer was sped up afterwards (2.11, 2021, per search snippets), and no current head-to-head numbers are public.

## How it is fast

It is an accumulation-buffer (signed-area) scanline rasterizer in the libart/FreeType-smooth family, but instead of sorting cells into a sparse structure it writes exact-area coverage deltas for every line segment straight into a dense f32 array (Raster::draw_line, about 100 lines in src/raster.rs), which avoids branch mispredictions. Quadratic Beziers are flattened into n evenly spaced line segments with n derived from the curve's deviation (not recursive subdivision). One prefix-sum pass then turns the deltas into 8-bit coverage; the optional 'sse' feature does that four floats at a time with shift-and-add, min, truncating convert and a byte shuffle. Glyph parsing is pull-style iterators over the raw glyf data, so no point or curve arrays are allocated.

## Compared with alternatives

Pick font-rs only to study or vendor the original \~230-line rasterizer core; for an application, fontdue (same accumulation design, maintained, TrueType and OpenType, its own latency plots against FreeType) is the better choice, and ttf-parser is the better choice if you only need outlines to feed your own rasterizer.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | none (Cargo.toml lists no dependencies; the 'sse' feature uses std::arch on master, while the crates.io 0.1.3 release still builds the C SSE module through build.rs) |
| **Minimum toolchain** | Stable Rust for the library (CI built and tested on stable, beta and nightly; Cargo.toml has no edition, so edition 2015); nightly Rust for the benches (#![feature(test)]). No rust-version is declared. |
| **Platforms** | any for the scalar build; the 'sse' feature is x86/x86-64 only, chosen at compile time with no runtime CPU detection (issue #29 open), and uses _mm_shuffle_epi8, an SSSE3 instruction despite the feature name |
| **Thread safety** | not documented; from the source, Font borrows the font bytes immutably and render_glyph(&self) allocates a fresh Raster per call, with no shared mutable state |
| **Drop-in for the baseline** | no |

## Gotchas

- The 'sse' accumulate does unaligned 4-float loads up to 3 floats past the end of its input slice; it stays inside the allocation only because Raster::new pads its buffer by 4 floats. accumulate() is public, and its own unit tests call it on unpadded Vecs of length 1-7, so those tests read past the allocation (undefined behaviour in Rust; not behind the published numbers).
- The library prints to stdout: render_glyph prints 'glyph N error' and returns None for empty glyphs such as the space, and 'unhandled glyph case' for empty compound components.
- Compound glyphs are rendered recursively with no depth limit, and only the ARGS_ARE_XY_VALUES component form is handled (a TODO in src/font.rs); a font with cyclic components would recurse until the stack overflows.
- Coverage is scaled by 255 and truncated (issue #13 suggests 256-epsilon), and the SIMD and scalar prefix sums add in a different order, so 'sse' and non-'sse' builds are not guaranteed bit-identical; the unit tests only check hand-picked inputs.

## Known shortcomings

- Rust library (language-filter mismatch). The only numbers (7.6x vs FreeType 2.6.5 at larger sizes, over 4x at 12 px/em, Xeon E5-2690) come from a 2016 Medium post seen only in search snippets (blocked here); the repo's benches time font-rs alone.
- Numbers remain snippet-only (Medium and lists.gnu.org blocked) and describe the 2016 C SSE3 accumulate module; master swapped to Rust std::arch in 2018 and crates.io 0.1.3 (2018-07-09) predates the Rust SIMD port, the metrics API and the 2020 out-of-bounds fix. The SSE accumulate loads up to 3 floats past the slice end (safe only through the Raster +4 padding; the crate's own tests read past the allocation, undefined behaviour); parse() panics on malformed fonts (#12, #44 open); prints to stdout; unbounded compound-glyph recursion; cmap format 4 only; integer pixel sizes; uses SSSE3 _mm_shuffle_epi8 without runtime detection (#29).

## Caveats and trade-offs

Numbers are snippet only: the Medium post (2016) could not be opened, so whether FreeType ran with hinting, which load flags it used and what exactly was timed could not be checked. The repo's benches (benches/glyph.rs: font.render_glyph(200, size) on NotoMono-Regular; benches/raster.rs: a synthetic line/quad shape) only time font-rs and need nightly Rust (#![feature(test)]); there is no FreeType harness in the repo. Search snippets (not opened) say FreeType's smooth rasterizer was sped up afterwards (FreeType 2.11, 2021) and that a FreeType GSoC project ported font-rs as a 'dense' rasterizer module that was faster than 'smooth' only on some hard fonts and sizes, so the 2016 gap is likely much smaller today. Cargo.toml still points at github.com/google/font-rs. Last commit 2020-09-05; the README calls the code rough and not ready for prime time.

TrueType (quadratic) outlines only, no CFF; no hinting; README says 'basically not ready for prime time' and the code is rough. Rust, so C++ use needs FFI; the SIMD cumulative-sum module is C.

## Maintenance

Abandoned (last commit 2020-09-05, crates.io release from 2018) and self-described as not production-ready, but Apache-2.0, dependency-free and small enough to vendor or port.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The only numbers (about 7.6x faster than FreeType 2.6.5 at larger sizes with SIMD, over 4x at 12 px/em, over 6x at 12 px/em on a CJK face, 2.9 GHz Xeon E5-2690) come from search snippets of the author's Medium post, which is blocked here; the repo's benches (benches/glyph.rs, benches/raster.rs) time font-rs alone and never run FreeType, so the evidence is first-party and not reproducible from public code: C (snippet only).
- **Verifier notes:** Rust library (optional C SSE3 module): language-filter mismatch for a C++ catalog, kept as Rust per the record. Metadata checked on github.com: Apache-2.0, 774 stars, not archived, not a fork, last commit 2020-09-05 (abandoned is right). benchmark_url set to the Medium post found by WebSearch; it was not opened (medium.com blocked), so it is not in urls_opened; lists.nongnu.org and mail-archive.com threads on the FreeType comparison were also blocked.
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `workload`, `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/raphlinus/font-rs>
  - <https://github.com/raphlinus/font-rs/commits>
  - <https://raw.githubusercontent.com/raphlinus/font-rs/HEAD/README.md>
  - <https://raw.githubusercontent.com/raphlinus/font-rs/HEAD/benches/glyph.rs>
  - <https://raw.githubusercontent.com/raphlinus/font-rs/HEAD/benches/raster.rs>
  - <https://raw.githubusercontent.com/raphlinus/font-rs/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/raphlinus/font-rs/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/raphlinus/font-rs>
  - <https://github.com/raphlinus/font-rs/commits>
  - <https://github.com/raphlinus/font-rs/issues?q=is%3Aissue>
  - <https://github.com/raphlinus/font-rs/pulls?q=is%3Apr>
  - <https://github.com/raphlinus/font-rs/issues/44>
  - <https://github.com/raphlinus/font-rs/issues/36>
  - <https://github.com/raphlinus/font-rs/issues/46>
  - <https://github.com/raphlinus/font-rs/tree/master/examples>
  - <https://raw.githubusercontent.com/raphlinus/font-rs/HEAD/README.md>
  - <https://raw.githubusercontent.com/raphlinus/font-rs/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/raphlinus/font-rs/HEAD/CONTRIBUTING.md>
  - <https://raw.githubusercontent.com/raphlinus/font-rs/HEAD/.travis.yml>
  - <https://raw.githubusercontent.com/raphlinus/font-rs/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/raphlinus/font-rs/HEAD/src/raster.rs>
  - <https://raw.githubusercontent.com/raphlinus/font-rs/HEAD/src/accumulate.rs>
  - <https://raw.githubusercontent.com/raphlinus/font-rs/HEAD/src/geom.rs>
  - <https://raw.githubusercontent.com/raphlinus/font-rs/HEAD/src/font.rs>
  - <https://raw.githubusercontent.com/raphlinus/font-rs/HEAD/benches/glyph.rs>
  - <https://raw.githubusercontent.com/raphlinus/font-rs/HEAD/benches/raster.rs>
  - <https://crates.io/api/v1/crates/font-rs>
  - <https://crates.io/api/v1/crates/font-rs/reverse_dependencies?per_page=20>
  - <https://github.com/freetype/freetype/branches/all?query=anurag>
  - <https://github.com/freetype/freetype/tree/gsoc-anurag-2022-final/src/dense>
  - <https://github.com/freetype/freetype/commits/gsoc-anurag-2022-docs>
  - <https://github.com/golang/go/issues/16904>
  - <https://raw.githubusercontent.com/golang/image/master/vector/vector.go>
  - <https://raw.githubusercontent.com/golang/image/master/vector/raster_floating.go>
  - <https://raw.githubusercontent.com/golang/image/master/vector/acc_amd64.go>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/raphlinus/font-rs`) · [data/wave10/enrich/raw/github_com_raphlinus_font_rs.json](../../../data/wave10/enrich/raw/github_com_raphlinus_font_rs.json) (enrichment confidence 0.7)

</details>
