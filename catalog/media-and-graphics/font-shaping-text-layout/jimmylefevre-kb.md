# kb_text_shape

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Font shaping and text layout](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `Zlib` · 🟢 active

> Single-header C library for Unicode segmentation and OpenType shaping; claimed faster than HarfBuzz, measured 2-160x slower independently.

| | |
|---|---|
| **Beats** | HarfBuzz |
| **Claimed result** | No speedup verified; flagged not-faster. HarfBuzz maintainer's run (discussion #5375, 2025-07-23, benchmark-shape, 'ot' shaper vs 'kbts' backend): Roboto-Regular en-thelittleprince.txt 9.11 ms vs 26.5 ms (HarfBuzz 2.9x faster); Roboto-Regular en-words.txt 11.3 ms vs 38.4 ms (3.3x); Amiri-Regular 40.6 ms vs 48.3 ms (kb about 20% slower); Gulzar-Regular Urdu 782 ms vs 5198 ms (kb 6.6x slower); Gulzar-Regular second text 24.9 ms vs 4021 ms (kb 160x slower); NotoSansDevanagari-Regular 25.3 ms vs 50.5 ms (kb 2x slower). Font loading (benchmark-font): Roboto 23.6 us vs 1000 us (40x), Gulzar 310 us vs 235,940 us (760x), NotoSansDevanagari 34.0 us vs 4,335 us (128x). The author's opposite claim (kb on average 4.5x faster than HarfBuzz on HarfBuzz's test suite plus own tests, Ryzen 9 5900HX, clang 20, Linux) is search-snippet only. |
| **Workload** | OpenType text segmentation and shaping; the author's claimed run used HarfBuzz's own test suite extended with the author's tests, while the HarfBuzz maintainer's run used Roboto-Regular (paragraphs and single words), Amiri-Regular (Arabic), Gulzar-Regular (Urdu and English) and NotoSansDevanagari-Regular (Hindi words). |
| **Metric** | throughput |
| **Hardware** | Author's claim (search snippet only): Ryzen 9 5900HX. HarfBuzz maintainer run: CPU not stated. |
| **Compiler and flags** | Author's claim (search snippet only): clang 20 on Linux, flags not stated. HarfBuzz maintainer run: compiler, flags and build type not stated (HarfBuzz perf/README.md gives meson debugoptimized as the default benchmark build). |
| **Adoption** | 1.2k stars |
| **Last commit** | 2026-10-02 |
| **Links** | [repository](https://github.com/JimmyLefevre/kb) · [benchmark](https://github.com/harfbuzz/harfbuzz/discussions/5375) |

## Verdict

The one opened independent comparison (HarfBuzz maintainer Behdad Esfahbod, discussion #5375, 2025-07-23, HarfBuzz's benchmark-shape and benchmark-font through its kbts backend; CPU, compiler, flags and kb version not stated) found kb slower everywhere: Roboto paragraph 26.5 vs 9.11 ms, Roboto words 38.4 vs 11.3 ms, Amiri 48.3 vs 40.6 ms, Gulzar Urdu 5198 vs 782 ms, Gulzar Latin 4021 vs 24.9 ms, Noto Devanagari 50.5 vs 25.3 ms, and font load 40x to 760x slower; that path converts HarfBuzz buffers and allocates kb glyph storage on every call (src/hb-kbts.cc), which taxes kb somewhat but cannot account for 6.6x to 160x gaps. The author's claim of 4.5x faster on average (HarfBuzz's test suite plus own tests, Ryzen 9 5900HX, clang 20, Linux) exists only in a search snippet with no harness, and no re-measurement of v2.06 ('Faster GSUB and GPOS feature culling'), v2.07 ('Performance improvements') or later versions was found.

## Use it when

- Games, editors-for-display, tools and embedded targets that want shaping plus segmentation from one Zlib-licensed header with no ICU, FriBidi, FreeType or HarfBuzz build, and are willing to give up speed for that.
- Programs that must control every allocation: contexts and scratchpads can be placed in caller memory, a custom allocator can be supplied, and KB_TEXT_SHAPE_NO_CRT drops the C runtime.
- Display-only rendering of complex scripts (Arabic, Indic v2 fonts, Khmer, Myanmar, Hangul and others) with a small, bundled and trusted font set loaded once at startup or shipped as prebuilt blobs.
- Prototyping a text pipeline where the README's model (segment, shape, then hand glyph IDs to stb_truetype or another rasterizer) is enough.

## Skip it when

- Throughput-critical shaping: the only reachable measurements put it behind HarfBuzz on every font tested (2.9x on a Roboto paragraph, 6.6x on Urdu Nastaliq, 160x on Latin text in Gulzar) and about 2x behind raqm/HarfBuzz in a user's test (kb issue #21).
- Untrusted or user-supplied fonts: the header says it provides no security guarantee, crash reports on real fonts were fixed during 2025-2026 (issues #43 NotoNastaliqUrdu, #44 SourceSerifVariable-Roman, #61 and #63 glyph insertion), and there is no fuzzing in the repository, unlike HarfBuzz's oss-fuzz coverage.
- Text editing, selection, cursor movement or text-extractable PDF: glyphs carry a source codepoint index, but there is no documented HarfBuzz-style cluster merging, explicit bidi control characters (embeddings, overrides, isolates) are not supported, hinting is unsupported, and there is no vertical layout (HarfBuzz's kbts backend rejects vertical directions; issue #64 asking how to do vertical text is open).
- Apps that open many fonts or large fonts on demand: each load copies the whole font into dirty memory and builds per-glyph-per-lookup bit matrices (Gulzar load plus one-character shape 235.9 ms against HarfBuzz's 0.31 ms).
- Dictionary-based word breaking (CJK), Indic1 fonts (e.g. 'beng' rather than 'bng2'), Zawgyi, the Syriac abbreviation mark, Windows 3.1 Arabic or Thai/Lao PUA fonts, which the header lists as unsupported.

## How it is fast

Font loading copies the font's tables into a private blob, byte-swaps them in place to native endianness, and precomputes bit matrices of glyph x lookup and glyph x lookup-subtable coverage, so during shaping one bit test decides whether a lookup or subtable can touch a glyph instead of walking coverage tables; each shape_config also builds a glyph x enabled-lookup matrix for the active feature set. Transient shaping state lives in contexts and scratchpads that the caller can size, place in its own memory (fixed-memory placement is supported) and reuse across calls. The cost is paid up front: building those matrices scales with glyphs x lookups, which fits the independent measurement of font loading 40x to 760x slower than HarfBuzz. kbts_LoadFont also accepts a prebuilt kbts blob, so that work can be done once and shipped.

## Compared with alternatives

It is the only C/C++ shaper in the category; the catalogued shaping siblings are Rust (Fontations, sigilbuzz, Parley), .NET (SixLabors.Fonts) or JavaScript (text-shaper, rustybuzz-wasm) and all measure against HarfBuzz or its ports. Pick kb over HarfBuzz only for a dependency-free single header with built-in segmentation and trusted fonts, not for speed.

## Integration

| | |
|---|---|
| **Form** | header-only (stb-style: define KB_TEXT_SHAPE_IMPLEMENTATION in one translation unit; KB_TEXT_SHAPE_STATIC for static linkage) |
| **Dependencies** | none (C runtime optional via KB_TEXT_SHAPE_NO_CRT with user KBTS_MALLOC, KBTS_FREE, KBTS_MEMSET, KBTS_MEMCPY) |
| **Minimum toolchain** | C99 or C++ (uses declare-anywhere, so not C89/VC6); GCC 15.2 reports unused-variable and enum-conditional warnings in the current header (issue #91, 2026-10-02), so -Werror builds need flags adjusted |
| **Platforms** | any: portable scalar C, with SSE2 used only for float rounding when available; MSVC, GCC and clang paths in the header |
| **Thread safety** | Header: a shape_config is immutable and can be shared among threads; a shape_scratchpad (and a shape_context) is mutable and must be per thread. HarfBuzz's kbts backend shares one kbts_font and config across threads and hands out per-thread scratchpads. |
| **Drop-in for the baseline** | no |

## Gotchas

- The font stack prefers the most recently pushed font, so fallbacks must be pushed first unless KBTS_SHAPE_CONTEXT_FLAG_FONT_PRIORITY_BOTTOM_TO_TOP is set.
- In the context API, kbts_glyph.UserIdOrCodepointIndex is always a codepoint index; your own user ID has to be read back through kbts_ShapeGetShapeCodepoint.
- With KB_TEXT_SHAPE_NO_CRT and no custom allocator, the default allocator returns 0; a custom KBTS_MALLOC must also return non-null for zero-size requests (open issue #73).
- The API has churned: v2.0 replaced the 1.x API, v2.07 changed kbts_ShapeDirect and struct layouts, and v2.28 added variation-aware \*2 entry points; HarfBuzz still pins v2.07 (commit ca6c962) while the header is at v2.28e.

## Known shortcomings

- Not faster than HarfBuzz: the author's 4.5x claim exists only in a search snippet of a blocked post, while HarfBuzz discussion #5375 has the HarfBuzz maintainer measuring kb_text_shape 2.9x to 160x slower at shaping and 40x to 760x slower at font load (harness perf/benchmark-shape.cc plus src/hb-kbts.cc; no CPU, compiler, flags or kb version), and kb issue #21 reports a third party seeing about 2x slower. Kept as a flagged entry (the author's number is unverified, not shown fabricated); kb is now v2.28e.
- Enricher (e110, 2026-10-05): not-faster flag stands at C. HarfBuzz main pins kb v2.07 (ca6c962) while the header is v2.28e; the kb version in the July 2025 run is unknown and the 2.06/2.07 changelog performance work was never re-measured. hb-kbts.cc allocates glyph storage per call, a small tax that cannot explain 6.6-160x gaps; font load builds glyph x lookup bit matrices, matching the 40-760x slower load. Record caveats were outdated: variable fonts added in v2.28, SourceSerifVariable crash fixed (issue #44 closed), crash issues #43, #61, #63 fixed; no fuzzing. Nothing new found on the author's 4.5x claim.

## Caveats and trade-offs

Disputed speed claim, kept as a flagged not-faster entry. A WebSearch snippet attributed to the author (X post and developer blog, unreachable here; mastodon.gamedev.place is egress-blocked) says kb is on average 4.5x faster than HarfBuzz at shaping on HarfBuzz's test suite extended with the author's tests, Ryzen 9 5900HX, clang 20, Linux; no per-test numbers or harness were found on any reachable page, and the kb README and header carry no benchmarks. The only opened comparison is by HarfBuzz maintainer Behdad Esfahbod (an interested party) on 2025-07-23 in harfbuzz discussion #5375, using HarfBuzz's public Google Benchmark harness (perf/benchmark-shape.cc, which iterates every compiled-in shaper; test fonts and texts listed in its default_tests) and the kbts backend (src/hb-kbts.cc, written by HarfBuzz's Khaled Hosny, enabled by meson option kbts; HarfBuzz 11.4.0 NEWS says it is 'purely for testing and performance evaluation'). That run found kb slower on every font (2x to 160x) and 40x to 760x slower at font loading, and reported crashes in the HarfBuzz test suite and an infinite loop or very slow run on SourceSerifVariable-Roman.ttf; CPU, compiler, flags and kb version were not stated, and timings go through HarfBuzz's buffer API wrapper. A third-party user (kb issue #21, 2025-07-13, libraqm harness, NotoSansArabic and NotoSans, 309 codepoints) also measured kb about 2x slower than raqm/HarfBuzz; the issue's 42 comments were not visible. kb is now v2.28e (2026-10-02), much newer than the July 2025 release measured, and HarfBuzz pins kb revision ca6c962 in subprojects/kbts.wrap, so re-running benchmark-shape with -Dkbts=enabled would settle the current state. Maintainer also notes no cluster information (display-only shaper) and no variable-font support. [retier] Disputed speed claim, kept as a flagged not-faster entry. A WebSearch snippet attributed to the author (X post and developer blog, unreachable here) says kb is on average 4.5x faster than HarfBuzz at shaping on HarfBuzz's test suite extended with the author's tests, Ryzen 9 5900HX, clang 20, Linux; no per-test numbers or harness were found on any reachable page, and the kb README and header carry no benchmarks. The only opened comparison is by HarfBuzz maintainer Behdad Esfahbod (an interested party) on 2025-07-23 in harfbuzz discussion #5375, using HarfBuzz's public Google Benchmark harness (perf/benchmark-shape.cc) and the kbts backend (src/hb-kbts.cc, enabled by meson option kbts; HarfBuzz 11.4.0 NEWS says it is 'purely for testing and performance evaluation'). That run found kb slower on every font (2x to 160x) and 40x to 760x slower at font loading; CPU, compiler, flags and kb version were not stated, and timings go through HarfBuzz's buffer API wrapper, whose hb-kbts.cc allocates glyph storage per call (a small tax that cannot explain the gaps). kb's font load builds glyph x lookup bit matrices, which matches the 40-760x slower load. A third-party user (kb issue #21, 2025-07-13, libraqm harness) also measured kb about 2x slower than raqm/HarfBuzz. HarfBuzz main pins kb v2.07 (ca6c962) in subprojects/kbts.wrap while the header is now v2.28e (2026-10-02); the 2.06/2.07 changelog lists performance work that was never re-measured. Variable fonts were added in v2.28 and the SourceSerifVariable-Roman infinite loop (issue #44) and crash issues #43, #61 and #63 are fixed; there is no fuzzing. kb provides no cluster information (display-only shaper).

Single-header C/C++ library (about 22k lines at announcement; header is v2.28e) that bundles Unicode segmentation and OpenType shaping with no dependencies. README says it does not handle rasterization, paragraph layout or system font loading. The header states it gives NO SECURITY GUARANTEE and must not be used on untrusted font files. HarfBuzz maintainer notes it copies whole font files into memory and lacks cluster information needed for cursor positioning, selection and editing.

## Maintenance

Actively developed (v2.28e, last commit 2026-10-02, 80 commits, about 1.2k stars, 13 open issues, frequent bug-fix releases) and Zlib-licensed, so easy to vendor, but it is a young, single-author shaper whose speed advantage is unproven.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The only speed win (author's 4.5x over HarfBuzz) exists only in a search snippet of an unreachable X/blog post, so C at most; the reachable independent measurement (HarfBuzz discussion #5375, Google Benchmark perf/benchmark-shape.cc with HarfBuzz's kbts shaper backend src/hb-kbts.cc) shows kb slower everywhere but states no CPU, compiler, flags or kb version and comes from the competing project's maintainer.
- **Verifier notes:** Discussion #5375 opened and its numbers recorded as the independent measurement (kb slower everywhere); the 4.5x claim is snippet-only and not fabricated as far as can be told, so no reject. Metadata (Zlib, 1.2k stars, last commit 2026-10-02, active, header v2.28e) verified.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** HarfBuzz maintainer run (discussion #5375)
- **Pages the verifier opened:**
  - <https://github.com/harfbuzz/harfbuzz/discussions/5375>
  - <https://github.com/JimmyLefevre/kb>
  - <https://github.com/JimmyLefevre/kb/commits/main>
  - <https://github.com/JimmyLefevre/kb/issues/21>
  - <https://github.com/JimmyLefevre/kb/commit/ca6c9624dd7c6b774e6cec9901f3d8d998d6f62a>
  - <https://raw.githubusercontent.com/JimmyLefevre/kb/main/kb_text_shape.h>
  - <https://raw.githubusercontent.com/JimmyLefevre/kb/main/LICENSE>
  - <https://raw.githubusercontent.com/harfbuzz/harfbuzz/main/perf/README.md>
  - <https://raw.githubusercontent.com/harfbuzz/harfbuzz/main/perf/benchmark-shape.cc>
  - <https://raw.githubusercontent.com/harfbuzz/harfbuzz/main/perf/meson.build>
  - <https://raw.githubusercontent.com/harfbuzz/harfbuzz/main/meson_options.txt>
  - <https://raw.githubusercontent.com/harfbuzz/harfbuzz/main/src/hb-kbts.cc>
  - <https://raw.githubusercontent.com/harfbuzz/harfbuzz/main/src/hb-shaper-list.hh>
  - <https://raw.githubusercontent.com/harfbuzz/harfbuzz/main/subprojects/kbts.wrap>
  - <https://raw.githubusercontent.com/harfbuzz/harfbuzz/main/NEWS>
  - <https://github.com/Ed94/TextRendering_Notes>
- **Sources the enricher read:**
  - <https://github.com/JimmyLefevre/kb>
  - <https://raw.githubusercontent.com/JimmyLefevre/kb/HEAD/README.md>
  - <https://raw.githubusercontent.com/JimmyLefevre/kb/HEAD/kb_text_shape.h>
  - <https://raw.githubusercontent.com/JimmyLefevre/kb/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/JimmyLefevre/kb/ca6c9624dd7c6b774e6cec9901f3d8d998d6f62a/kb_text_shape.h>
  - <https://github.com/JimmyLefevre/kb/commit/ca6c9624dd7c6b774e6cec9901f3d8d998d6f62a>
  - <https://github.com/JimmyLefevre/kb/issues?q=is%3Aissue>
  - <https://github.com/JimmyLefevre/kb/issues?q=is%3Aissue+is%3Aclosed>
  - <https://github.com/JimmyLefevre/kb/issues/21>
  - <https://github.com/JimmyLefevre/kb/issues/66>
  - <https://github.com/JimmyLefevre/kb/issues/91>
  - <https://github.com/harfbuzz/harfbuzz/discussions/5375>
  - <https://github.com/harfbuzz/harfbuzz/issues/6294>
  - <https://raw.githubusercontent.com/harfbuzz/harfbuzz/main/subprojects/kbts.wrap>
  - <https://raw.githubusercontent.com/harfbuzz/harfbuzz/main/src/hb-kbts.cc>
  - <https://raw.githubusercontent.com/harfbuzz/harfbuzz/main/NEWS>
  - <https://github.com/soypat/lefevre/>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/jimmylefevre/kb`) · [data/wave10/enrich/raw/github_com_jimmylefevre_kb.json](../../../data/wave10/enrich/raw/github_com_jimmylefevre_kb.json) (enrichment confidence 0.75)

</details>
