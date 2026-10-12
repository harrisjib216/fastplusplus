# Parley

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Font shaping and text layout](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Rust` · `Apache-2.0 OR MIT` · 🟢 active

> Pure-Rust rich-text layout (fallback, bidi, shaping, line breaking); 2.4-9x faster than cosmic-text on paragraph-per-layout workloads.

| | |
|---|---|
| **Beats** | cosmic-text 0.19.0 (pop-os/cosmic-text), the established Rust rich-text shaping and layout library (bevy_text, iced, COSMIC); both shape with HarfRust, but different versions: cosmic-text 0.19.0 pulls harfrust 0.5.2 while parley 0.11.1 pulls harfrust 0.12.0 (flui spike Cargo.lock). Not a C/C++ incumbent such as HarfBuzz with FreeType or Pango. |
| **Claimed result** | flui PR 1276 (merged 2026-09-23), docs/research/text-stack-2026.md, final (third) pass, 10,000-line documents, one parley Layout per paragraph, cold cache, median of 5 (cosmic-text vs parley): latin 4255 vs 781 ms (5.4x), arabic 3070 vs 1258 ms (2.4x), arabic_mixed 4474 vs 961 ms (4.7x), cjk 5120 vs 566 ms (9.0x), emoji_zwj 3083 vs 782 ms (3.9x), devanagari 3246 vs 1075 ms (3.0x): 2.4x-9.0x faster (the PR summary still quotes 2.4x-8.4x from an earlier pass), and 1.2x-4.2x less shaping-attributable memory. Single paragraph: warm 0.07-0.14 ms vs 0.32-0.49 ms, cold 6.1-6.6 ms vs 6.9-7.6 ms. When a whole document is handed to one parley Layout, parley is far slower (devanagari 10,000 lines: 78,782 ms vs cosmic-text 3,265 ms). massive PR 154 (merged 2026-09-15), docs/adr/0005-dual-shaping-engines-cosmic-text-and-parley.md (criterion, bundled JetBrains Mono 13 px, M-series Mac, warm cache): single ASCII cluster cosmic-text 1.8 us vs parley 2.1 us (cosmic-text \~16% faster); full mixed line parley 28 us vs cosmic-text 137 us (\~4.8x); full-screen throughput parley \~2x; fallback stress parley \~2.7x; cold start with a fresh font database parley 61 us vs cosmic-text 36 ms (\~600x in parley's favour, caused by cosmic-text's FontSystem construction). |
| **Workload** | flui spike: shape and lay out six corpora (Latin, pure-RTL Arabic, Arabic plus Latin bidi, CJK, ZWJ emoji, Devanagari) as one short paragraph and as the paragraph repeated to 10,000 lines, cold and warm backend caches, 5 reps each, one process per run, requesting the SansSerif generic from macOS system fonts at 16 px with unbounded width (no --max-width, so no wrapping inside a line); parley 0.11.1 vs cosmic-text 0.19.0. massive: criterion terminal workloads (single cluster, full mixed line, 50-line full screen, fallback stress, cold start) with bundled JetBrains Mono 13 px. |
| **Metric** | throughput |
| **Hardware** | flui PR 1276: macOS on Apple Silicon (arm64), a shared dev machine with no concurrent builds; exact chip not stated. massive PR 154: 'M-series Mac'. |
| **Compiler and flags** | flui spike: cargo build --release (default release opt-level, [profile.release] debug = true), CARGO_BUILD_JOBS=6 CARGO_INCREMENTAL=0; rustc version not stated (crate MSRVs 1.88/1.89, flui workspace MSRV 1.97). massive: criterion, flags not stated. |
| **Adoption** | 750 stars |
| **Last commit** | 2026-10-02 |
| **Links** | [repository](https://github.com/linebender/parley) · [benchmark](https://github.com/vanyastaff/flui/pull/1276) |

## Verdict

An independent downstream project (flui PR 1276) ran a public harness: parley 0.11.1 vs cosmic-text 0.19.0, release build, macOS on Apple Silicon (chip and rustc not stated), system SansSerif at 16 px, no wrapping, 5 runs each. On 10,000-line documents (one Layout per paragraph, cold) parley was 2.4x-9.0x faster (latin 781 vs 4255 ms, cjk 566 vs 5120 ms); recomputing from the checked-in measurements.jsonl shows warm runs are within 3% of cold (2.5x-8.9x), and each large run is about 10,000 times a warm single paragraph. Separately, massive's criterion bench (M-series Mac, JetBrains Mono 13 px) found parley ahead on mixed lines (4.8x), full screens (2x) and fallback stress (2.7x), behind by 16% on a single cluster, and about 600x faster at cold start.

## Use it when

- A Rust UI or document renderer that lays out many independent paragraphs: in flui's spike (Apple Silicon, parley 0.11.1 vs cosmic-text 0.19.0) one Layout per paragraph was 2.4x (Arabic) to 9.0x (CJK) faster over 10,000 lines.
- Repeated warm layout of short UI strings: a single warm paragraph took 0.07-0.14 ms against cosmic-text's 0.32-0.48 ms in the same data, 2.3-6.8x faster (derived from page data).
- Mixed-script or fallback-heavy text such as Latin with embedded Arabic, CJK or emoji, where massive's criterion bench shows parley about 4.8x faster on a full mixed line and 2.7x on fallback stress.
- Apps that create a font database often or need a fast cold start: massive measured parley 61 us vs cosmic-text 36 ms for a fresh font database, because cosmic-text's FontSystem construction dominates.
- Projects already on the Linebender or Bevy stack (Vello, Xilem/Masonry, Blitz; bevy_text moved from cosmic-text to parley in PR 22879, merged 2026-02-11).

## Skip it when

- Handing one Layout a whole multi-paragraph document of a single script on released 0.11.1: shaping is quadratic in item length (devanagari 10,000 lines took 78,782 ms vs cosmic-text 3,265 ms in flui's scaling study). Split on newlines yourself, or wait for a release that includes PR 801 (merged 2026-09-09 to main, not in 0.11.1).
- Terminal-style glyph-at-a-time work: cosmic-text was about 16% faster on a single ASCII cluster in massive's criterion bench.
- C or C++ code bases: there is no C API, so HarfBuzz with FreeType, ICU or Pango stay the native choice.
- Teams that need API stability: four minor releases (0.8 to 0.11, each semver-breaking for a 0.x crate) shipped in 2026, and main queues more breaking changes (Cluster now spans a grapheme cluster, LineMetrics ascent/descent/leading removed).
- Long Arabic paragraphs with wrapping, until someone checks it: flui issue 931 relays an unaudited floem report of parley being 93% slower on Arabic wrap, and the flui spike never exercised wrapping.

## How it is fast

Shaping goes through HarfRust with per-Shaper LRU caches (16 entries each) for shaper data, variation instances and shape plans, plus a reused UnicodeBuffer, so repeated runs in the same font skip plan construction. Text is itemised by script, bidi level and style, and each item is split into runs only where grapheme clusters change font, so a uniform paragraph is shaped in a few large calls. LayoutContext keeps allocations across layouts. Nobody has profiled where the gap to cosmic-text 0.19.0 comes from, and the two used different HarfRust versions (0.12.0 vs 0.5.2) in the flui test, so part of the gap may be the shaper itself.

## Compared with alternatives

The other catalogued font entries are shapers (sigilbuzz, rustybuzz-wasm, text-shaper, SixLabors.Fonts), rasterizers (fontdue, font-rs, TiTanF) or a typesetter (Typst). Pick Parley when you need full paragraph layout in Rust: fallback, bidi, line breaking, alignment and editing. Draw the glyphs with a separate renderer; the repo's examples use swash, tiny-skia and Vello CPU.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | fontique (font enumeration and fallback; CoreText via objc2 on Apple, fontconfig on Linux/FreeBSD, platform backends on Windows and Android), parley_engine, parlance, HarfRust 0.12, Skrifa/read-fonts, ICU4X 2.x (segmenter, properties, normalizer), hashbrown, smallvec, linebender_resource_handle |
| **Minimum toolchain** | Rust 1.88 (edition 2024) |
| **Platforms** | macOS/iOS, Windows, Linux, FreeBSD and Android with system fonts (default 'system' feature); no_std plus alloc with the 'libm' feature and caller-supplied fonts |
| **Thread safety** | Not documented beyond the API shape: FontContext and LayoutContext are passed as &mut, so each thread needs its own pair or external locking. |
| **Drop-in for the baseline** | no |

## Gotchas

- Dictionary-based line breaking for CJK, Thai, Khmer, Lao and Myanmar is behind the off-by-default 'complex-scripts' feature; without it those scripts break at every character.
- Layout.break_all_lines(None) means unbounded width, and align() takes no width (since 0.9 it aligns to max_advance or to the longest line), so code ported from older versions can silently misalign.
- Main is churning: issue 763 recorded a 20x regression in GlyphRunIter::next on unreleased main (fixed by PR 764 before any release), so benchmark a pinned version, not a git dependency.
- The catalogued speedups compare against cosmic-text only, at unbounded width, using a single paragraph repeated 10,000 times; glyph counts differ by 3.2% on the emoji ZWJ corpus, and no one checked whether the system-font fallback produced tofu on either side.

## Known shortcomings

- Rust text layout (language-filter mismatch) measured against cosmic-text 0.19.0, a Rust-ecosystem incumbent rather than a C/C++ one. Tier B on an independent public harness (flui tools/text-spike at e30ab7194 plus raw measurements.jsonl; medians 2.4x-9.0x) with no rustc version or exact Apple Silicon chip. No line wrapping (unbounded width); harfrust 0.12.0 vs 0.5.2; Parley is 24x slower when given one whole-document Layout (78,782 vs 3,265 ms). The record had misread the massive ADR 0005 cold-start comparison: Parley wins there (61 us vs 36 ms).
- The large-corpus run is one paragraph repeated 10,000 times, so it is about 10,000 warm per-paragraph layouts (warm within 3% of cold, 2.5-8.9x). Released 0.11.1 has a quadratic single-Layout path (fixed on main by PR 801, merged 2026-09-09, unreleased), and main carried a 20x GlyphRunIter regression (issue 763) before release; the complex-scripts feature is off by default, so CJK and Thai break per character.

## Caveats and trade-offs

Third-party measurements by two downstream projects (flui and massive), not by the Parley authors and not peer reviewed. Rust, so it does not match the catalog's default C++ language filter. Baseline cosmic-text is a recognisable Rust-ecosystem incumbent but not a C/C++ one (HarfBuzz with FreeType, Pango); the two libraries use different HarfRust versions (0.5.2 vs 0.12.0), so part of the gap may come from the newer shaper rather than Parley's own code. The flui harness lays out at unbounded width, so line wrapping is not exercised; it requests system fonts by generic family and did not check fallback quality (tofu glyphs would still count); glyph counts differ on emoji_zwj (-3.19%) and arabic_mixed (-0.25%). The flui PR, co-authored with an AI assistant, went through three correction rounds (a quadratic cost when the whole document is one parley Layout, 78,782 ms vs 3,265 ms on 10,000 Devanagari lines; a memory-retention asymmetry; mismatched font generics and a destruction boundary inside the timer); the earlier 30-38x memory figures are superseded. The massive benchmark source (mt benches/terminal_shaping.rs) was not found in the massive repository, and there cosmic-text wins the single-cluster hot path by about 16%. flui issue 931 relays an unaudited floem report of parley being '93% slower on Arabic wrap'. Neither measurement covers rasterization.

Rust-only (not callable from C++ without bindings). Depends on Fontique, HarfRust, Skrifa and ICU4X. Larger binary than fontdue-style rasterizers (a separate PR measured +40% binary size when replacing fontdue with parley and swash). cosmic-text starts faster cold (FontSystem construction) and wins the single-cluster hot path.

## Maintenance

Actively developed by Linebender (last commit 2026-10-02; latest crates.io release 0.11.1 on 2026-08-16, about 3.5M all-time downloads), Apache-2.0 OR MIT, pre-1.0 with breaking changes in most releases.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now B.
- **Tier reason:** Upgraded from C: an independent downstream project (flui, not linebender) measured parley against cosmic-text with a public harness (tools/text-spike/src/main.rs, parley_backend.rs, cosmic_backend.rs, scripts/run_measurements.sh at commit e30ab7194) and checked in the raw 240-point results/measurements.jsonl, from which the verifier recomputed every large-size median and ratio exactly (e.g. latin 4255 vs 781 ms, cjk 5120 vs 566 ms). Not A because the rustc version and exact CPU model are not stated (macOS on Apple Silicon only; release profile with debug = true).
- **Verifier notes:** Upgraded C to B per the 'independent measurement' rule (precedent: wave 9 fdeflate and jtkukunas/zlib); the orchestrator may prefer to hold it at C because flui is a downstream research PR rather than a well-known suite. The record's claim that cosmic-text wins cold start by \~600x is a misreading of massive ADR 0005: parley is \~600x faster there (61 us vs 36 ms). Metadata checked on github.com: Apache-2.0 OR MIT, 750 stars, last commit 2026-10-02, not archived; language Rust is correct (verify.py does not apply 'language' from corrections).
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/vanyastaff/flui/pull/1276>
  - <https://raw.githubusercontent.com/vanyastaff/flui/HEAD/docs/research/text-stack-2026.md>
  - <https://raw.githubusercontent.com/vanyastaff/flui/e30ab7194d50ac1c11ffe17c59230958d2fbeecd/tools/text-spike/Cargo.toml>
  - <https://raw.githubusercontent.com/vanyastaff/flui/e30ab7194d50ac1c11ffe17c59230958d2fbeecd/tools/text-spike/Cargo.lock>
  - <https://raw.githubusercontent.com/vanyastaff/flui/e30ab7194d50ac1c11ffe17c59230958d2fbeecd/tools/text-spike/src/main.rs>
  - <https://raw.githubusercontent.com/vanyastaff/flui/e30ab7194d50ac1c11ffe17c59230958d2fbeecd/tools/text-spike/src/parley_backend.rs>
  - <https://raw.githubusercontent.com/vanyastaff/flui/e30ab7194d50ac1c11ffe17c59230958d2fbeecd/tools/text-spike/src/cosmic_backend.rs>
  - <https://raw.githubusercontent.com/vanyastaff/flui/e30ab7194d50ac1c11ffe17c59230958d2fbeecd/tools/text-spike/scripts/run_measurements.sh>
  - <https://raw.githubusercontent.com/vanyastaff/flui/e30ab7194d50ac1c11ffe17c59230958d2fbeecd/tools/text-spike/scripts/aggregate.py>
  - <https://raw.githubusercontent.com/vanyastaff/flui/e30ab7194d50ac1c11ffe17c59230958d2fbeecd/tools/text-spike/results/measurements.jsonl>
  - <https://github.com/vanyastaff/flui/issues/931>
  - <https://github.com/pragmatrix/massive/pull/154>
  - <https://github.com/pragmatrix/massive/pull/154/files>
  - <https://raw.githubusercontent.com/pragmatrix/massive/HEAD/docs/adr/0005-dual-shaping-engines-cosmic-text-and-parley.md>
  - <https://github.com/linebender/parley>
  - <https://github.com/linebender/parley/commits/main>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/linebender/parley/HEAD/README.md>
  - <https://raw.githubusercontent.com/linebender/parley/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/linebender/parley/HEAD/parley/Cargo.toml>
  - <https://raw.githubusercontent.com/linebender/parley/HEAD/parley/src/lib.rs>
  - <https://raw.githubusercontent.com/linebender/parley/HEAD/parley/src/shape/mod.rs>
  - <https://raw.githubusercontent.com/linebender/parley/HEAD/parley_engine/src/shape/mod.rs>
  - <https://raw.githubusercontent.com/linebender/parley/HEAD/parley_engine/src/shape/shaper.rs>
  - <https://raw.githubusercontent.com/linebender/parley/HEAD/parley_engine/src/shape/cache.rs>
  - <https://raw.githubusercontent.com/linebender/parley/HEAD/parley_engine/src/lib.rs>
  - <https://raw.githubusercontent.com/linebender/parley/HEAD/parley_engine/Cargo.toml>
  - <https://raw.githubusercontent.com/linebender/parley/HEAD/parley_bench/Cargo.toml>
  - <https://raw.githubusercontent.com/linebender/parley/HEAD/parley_bench/README.md>
  - <https://raw.githubusercontent.com/linebender/parley/HEAD/fontique/Cargo.toml>
  - <https://raw.githubusercontent.com/linebender/parley/HEAD/CHANGELOG.md>
  - <https://github.com/linebender/parley/issues?q=is%3Aissue+performance>
  - <https://github.com/linebender/parley/issues?q=quadratic>
  - <https://github.com/linebender/parley/pull/801>
  - <https://github.com/linebender/parley/issues/763>
  - <https://crates.io/api/v1/crates/parley/versions>
  - <https://crates.io/api/v1/crates/parley>
  - <https://raw.githubusercontent.com/vanyastaff/flui/e30ab7194d50ac1c11ffe17c59230958d2fbeecd/tools/text-spike/Cargo.toml>
  - <https://raw.githubusercontent.com/vanyastaff/flui/e30ab7194d50ac1c11ffe17c59230958d2fbeecd/tools/text-spike/src/main.rs>
  - <https://raw.githubusercontent.com/vanyastaff/flui/e30ab7194d50ac1c11ffe17c59230958d2fbeecd/tools/text-spike/src/parley_backend.rs>
  - <https://raw.githubusercontent.com/vanyastaff/flui/e30ab7194d50ac1c11ffe17c59230958d2fbeecd/tools/text-spike/src/cosmic_backend.rs>
  - <https://raw.githubusercontent.com/vanyastaff/flui/e30ab7194d50ac1c11ffe17c59230958d2fbeecd/tools/text-spike/scripts/run_measurements.sh>
  - <https://raw.githubusercontent.com/vanyastaff/flui/e30ab7194d50ac1c11ffe17c59230958d2fbeecd/tools/text-spike/results/measurements.jsonl>
  - <https://raw.githubusercontent.com/vanyastaff/flui/HEAD/docs/research/text-stack-2026.md>
  - <https://github.com/bevyengine/bevy/pull/22879>
  - <https://github.com/bevyengine/bevy/pull/23012>
  - <https://github.com/gpui-ce/gpui-ce/pull/253>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/linebender/parley`) · [data/wave10/enrich/raw/github_com_linebender_parley.json](../../../data/wave10/enrich/raw/github_com_linebender_parley.json) (enrichment confidence 0.7)

</details>
