# SixLabors.Fonts

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Font shaping and text layout](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C#` · `Six Labors Split License 1.0 (non-OSI: Apache-2.0 only for open-source or source-available use, transitive dependencies, non-profits and for-profits under 1M USD annual revenue; commercial license otherwise)` · 🟢 active

> Pure managed C# OpenType shaper and text layout engine; on .NET 10 it is within about 8% of native HarfBuzz overall, beating it on four of ten scripts.

| | |
|---|---|
| **Beats** | HarfBuzz via HarfBuzzSharp 14.2.1.1 (native HarfBuzz called from .NET, single-run text shaping) |
| **Claimed result** | PR #550 tables, .NET 10.0.10, mean time Fonts vs HarfBuzzSharp (ratio Fonts over HarfBuzz, derived from page data where the page gives only times): Latin 2.6744 vs 2.2843 us (1.17x); Arabic 4.9651 vs 3.9115 us (1.27x); Hebrew 4.5843 vs 4.6725 us (0.98x); Thai 4.2530 vs 3.9104 us (1.09x); Hangul 0.9258 vs 0.5645 us (1.64x); Devanagari 7.7347 vs 9.3177 us (0.83x); Khmer 4.1790 vs 3.7335 us (1.12x); Myanmar 25.2861 vs 22.9402 us (1.10x); Myanmar Zawgyi 0.7797 vs 0.8248 us (0.95x); Balinese 2.6941 vs 3.0572 us (0.88x). Faster on Devanagari (1.20x), Balinese (1.13x), Zawgyi (1.06x) and Hebrew (1.02x, near parity); slower on the other six, up to 1.64x slower on Hangul. The PR says seven of ten workloads are within 12% of HarfBuzz or faster; the release post reportedly counts three outright wins. On .NET 8.0.29 Fonts is faster only on Balinese (0.96x) and slower elsewhere (1.01x to 1.97x). Zero managed allocations per shape in steady state. |
| **Workload** | End-to-end shaping of one short text run per script (Latin, Arabic, Hebrew, Thai, Hangul, Devanagari, Khmer, Myanmar, Myanmar Zawgyi, Balinese), same font file bytes on both sides, BenchmarkDotNet on .NET 10. |
| **Metric** | latency |
| **Compiler and flags** | BenchmarkDotNet Gate job (3 launches, 5 warmup, 15 iterations, /p:DebugType=portable) on the host runtime, net10.0 target (also run on .NET 8.0.29 per the PR); HarfBuzzSharp 14.2.1.1 with OpenType font functions; BenchmarkDotNet version not stated on the PR |
| **Adoption** | 350 stars; managed text layout engine for the SixLabors.ImageSharp.Drawing stack |
| **Last commit** | 2026-09-17 |
| **Links** | [repository](https://github.com/SixLabors/Fonts) · [benchmark](https://github.com/SixLabors/Fonts/pull/550) |

## Verdict

First-party PR #550 (merged 2026-07-30, shipped in 3.1.0) runs the public ShapeTextBenchmark under the BenchmarkDotNet Gate job (3 launches, 5 warmup, 15 iterations); BenchmarkDotNet 0.15.8 is pinned in tests/Directory.Build.targets at the v3.1.0 tag, though the PR prints no version, CPU or OS. Each iteration shapes one short run per script (25 to 60 characters) from the same font file bytes with Fonts' ShapeRun versus HarfBuzzSharp 14.2.1.1 (Reset, AddUtf16, GuessSegmentProperties, Shape), summing advances. On .NET 10.0.10 Fonts takes 0.83x to 1.64x HarfBuzz's time, faster on Devanagari, Balinese, Zawgyi and Hebrew (barely). On .NET 8.0.29 only Balinese is faster. The HarfBuzz side pays about five managed-to-native calls per shape, which weighs most on the sub-microsecond Hangul and Zawgyi rows; the same string is reshaped every iteration, so both sides' glyph caches stay hot.

## Use it when

- .NET 8+ services or tools that must shape text with no native dependency: a pure managed assembly that is marked trimmable and needs no per-platform native assets.
- Complex-script text on .NET 10, where the vendor's run puts it ahead of HarfBuzzSharp: Devanagari 1.20x faster, Balinese 1.13x, Myanmar Zawgyi 1.06x, Hebrew at parity (1.02x).
- When you need more than shaping (bidi, line breaking, wrapping, measurement, hit testing, caret and selection geometry) from one library, rather than HarfBuzz plus ICU or FriBidi plus your own layout.
- High-volume shaping of many short runs, where you can keep one TextShapingBuffer per thread and want no GC pressure.
- Text rendering in the SixLabors ImageSharp.Drawing stack, which uses it as its text engine.

## Skip it when

- Native C or C++ code: it is a .NET library, not callable from C++ without hosting the CLR. Use HarfBuzz directly.
- Latin, Arabic or Hangul-heavy workloads where raw shaping latency matters: on .NET 10 it is 1.17x (Latin), 1.27x (Arabic) and 1.64x (Hangul) slower than HarfBuzzSharp, and about 1.08x slower across all ten scripts (geometric mean, derived from page data).
- On .NET 8 it wins only Balinese (0.96x) and is 1.01x to 1.97x slower on the rest (about 1.27x slower geometric mean, derived from page data).
- Fonts that depend on Apple AAT tables (morx, kerx): AAT shaping is not supported (issue #551, open).
- Companies with 1M USD or more annual revenue using it as a direct dependency in closed-source software: the Six Labors Split License then requires a paid commercial license.

## How it is fast

Shaping runs on a pooled ShapingScratch (borrowed per call from a scratch pool) and a caller-reused TextShapingBuffer, so the steady state allocates zero managed bytes. The internal ShapingBuffer keeps glyph records, a metrics stream and a positioning stream as parallel arrays, so the GSUB walks touch only narrow records. A 256-slot direct-mapped cache serves cmap glyph-id lookups and another serves glyph metrics. A glyph-set digest, an approximate membership filter like HarfBuzz's set digest, lets lookups that cannot match be skipped. PR #550 also lists per-lookup feature masks, streaming substitution in place of tail shifts on length changes, plan features collected once per plan, a cached USE decomposition table and direct lookup probes in the Indic shaper. The JIT matters a lot: the same code is 1.13x to 1.36x faster on .NET 10.0.10 than on .NET 8.0.29, while the HarfBuzzSharp rows gain only 1.04x to 1.12x (derived from page data).

## Compared with alternatives

No other .NET shaper is catalogued. Pick this when you are on .NET and want no native HarfBuzz. In Rust, Parley (layout on HarfRust) or sigilbuzz cover the same ground, and in JavaScript text-shaper or rustybuzz-wasm compare against harfbuzzjs rather than native HarfBuzz.

## Integration

| | |
|---|---|
| **Form** | NuGet package (managed assembly, SixLabors.Fonts) |
| **Dependencies** | none (the 3.1.3 nuspec lists no dependencies for its net8.0 asset) |
| **Minimum toolchain** | .NET 8 for the released 3.1.x packages (net8.0 asset); the main branch now targets net10.0 only, so building from main needs the .NET 10 SDK even though the README still says .NET 8 |
| **Platforms** | any platform with a .NET 8+ runtime (pure managed code, no native assets) |
| **Thread safety** | TextShapingBuffer is documented as not thread safe (use one per thread). TextShaper is static and takes pooled scratch state per call. An exception when rendering text concurrently with HintingMode.Standard (issue #484) was fixed in 2025. |
| **Drop-in for the baseline** | false: a different API (TextShapingBuffer plus TextShaper.ShapeRun returning ShapedGlyph), not hb_buffer/hb_shape; glyph ids and positions are meant to match HarfBuzz (PR #550 reports 4,851/4,851 HarfBuzz corpus cases passing), but the units and run order differ |

## Gotchas

- Units differ from HarfBuzz: ShapedGlyph advances and offsets are floats scaled by Font.Size / UnitsPerEm (point size, no DPI) in a Y-up system, while HarfBuzzSharp returns integer positions in the font's scale units. ShapeRun returns glyphs in reading order, while HarfBuzz emits right-to-left runs in visual order.
- The script is inferred from the text unless you set TextShapingBuffer.Script; Zawgyi text must be forced with ScriptClass.MyanmarZawgyi, just as HarfBuzz needs the Qaag script tag.
- The measured 3.1.0 code walked GPOS one glyph after every lookup instead of following the buffer cursor, so contextual positioning lookups could be reapplied to glyphs already consumed (seen with Segoe UI Emoji 1.70). PR #565 fixed this in 3.1.3 (2026-09-17). Use 3.1.3 or later; the fix was not re-benchmarked.
- Robustness against malformed fonts is recent: 2026 fixes cover IndexOutOfRangeException in cmap format 4 and GSUB lookup type 2 (#510, #514), OverflowException loading a collection (#534), and stack overflows on self-referential composite glyphs (#537) and cyclic COLRv1 paint graphs (#560). Treat untrusted fonts with care.

## Known shortcomings

- C# (language-filter mismatch); Six Labors Split License 1.0 (not OSI approved), reference only. Not faster overall: the full table (PR #550) shows .NET 10 wins on only 4 of 10 scripts (Devanagari 0.83x, Balinese 0.88x, Zawgyi 0.95x, Hebrew 0.98x) and losses on 6 (Hangul 1.64x slower); on .NET 8 it wins only Balinese. No CPU model; the HarfBuzzSharp side pays P/Invoke and GuessSegmentProperties.
- Not faster: on its own fair BenchmarkDotNet 0.15.8 harness (pinned at v3.1.0) SixLabors.Fonts is 1.08x slower than HarfBuzzSharp on .NET 10 and 1.27x slower on .NET 8 (geometric means, derived from page data); CPU and OS are unstated. The measured 3.1.0 had a GPOS cursor bug (contextual lookups reapplied to consumed glyphs, seen with Segoe UI Emoji; fixed in 3.1.3 by PR #565), not shown to touch the benchmark fonts. Main is now net10-only while NuGet 3.1.x targets net8.0; AAT shaping unsupported (#551).

## Caveats and trade-offs

First-party; numbers are on PR #550 (read through github.com) with no CPU model, OS or BenchmarkDotNet version, and the sixlabors.com release post was not opened (blocked). Not faster overall: on .NET 10 it beats HarfBuzz on three or four of ten scripts (Hebrew is near parity) and trails on six, up to 1.64x on Hangul and 1.27x on Arabic; on .NET 8 it wins only Balinese. Same work in principle (one short run of 25-60 characters per script, same font bytes, glyph advances summed), but the HarfBuzz side also pays several .NET-to-native interop calls and HarfBuzz's GuessSegmentProperties per iteration while Fonts is handed the direction, which weighs most on the sub-microsecond Hangul and Zawgyi runs. The baseline is native HarfBuzz through HarfBuzzSharp, a recognisable incumbent and in the list. The library is C#, not C++, and the non-OSI Split License makes it reference only.

Pure managed .NET shaper with no native dependency, so it ships to any .NET 8+ target; it covers GSUB/GPOS and complex scripts, but the glyph output is not guaranteed identical to HarfBuzz; the Six Labors Split License gives Apache-2.0 terms only to qualifying open-source use and requires a paid licence for other commercial use, so it is not an OSI licence (no SPDX id; license field left null).

## Maintenance

Active (3.0.0 on 2026-05-12, then 3.1.0 to 3.1.3 between 2026-08-11 and 2026-09-17 on NuGet; last commit 2026-09-17). It is reference only, because it is C# and under the non-OSI Six Labors Split License (Apache-2.0 only for open-source use, transitive use, non-profits and companies under 1M USD annual revenue).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** PR #550 on github.com (merged 2026-07-30, shipped in v3.1.0) carries full per-script tables of SixLabors.Fonts vs HarfBuzzSharp on .NET 8.0.29 and .NET 10.0.10, produced by the public ShapeTextBenchmark.cs under the Gate config, but it names no CPU model, OS or BenchmarkDotNet version; first-party, so C.
- **Verifier notes:** Found the full numbers on github.com PR #550, so the record no longer rests on a search snippet; the snippet's ratios match the PR's .NET 10 table. Repo: 350 stars, 79 forks, not a fork, not archived, last commit 2026-09-17 (active). The numbers were read through WebFetch's rendering of the PR page (consistent across three fetches), not the raw markdown.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `license`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/SixLabors/Fonts/HEAD/README.md>
  - <https://github.com/SixLabors/Fonts>
  - <https://raw.githubusercontent.com/SixLabors/Fonts/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/SixLabors/Fonts/HEAD/tests/SixLabors.Fonts.Benchmarks/SixLabors.Fonts.Benchmarks/ShapeTextBenchmark.cs>
  - <https://raw.githubusercontent.com/SixLabors/Fonts/HEAD/tests/SixLabors.Fonts.Benchmarks/SixLabors.Fonts.Benchmarks/Config.cs>
  - <https://raw.githubusercontent.com/SixLabors/Fonts/HEAD/tests/SixLabors.Fonts.Benchmarks/SixLabors.Fonts.Benchmarks/SixLabors.Fonts.Benchmarks.csproj>
  - <https://github.com/SixLabors/Fonts/commits/main/tests/SixLabors.Fonts.Benchmarks/SixLabors.Fonts.Benchmarks/ShapeTextBenchmark.cs>
  - <https://github.com/SixLabors/Fonts/releases>
  - <https://github.com/SixLabors/Fonts/pulls?q=is%3Apr+is%3Aclosed+shaping>
  - <https://github.com/SixLabors/Fonts/pull/550>
  - <https://github.com/SixLabors/Fonts/commits/main>
- **Sources the enricher read:**
  - <https://github.com/SixLabors/Fonts/pull/550>
  - <https://github.com/SixLabors/Fonts/pull/565>
  - <https://github.com/SixLabors/Fonts/tree/main/src/SixLabors.Fonts>
  - <https://github.com/SixLabors/Fonts/issues?q=is%3Aissue+sort%3Aupdated-desc>
  - <https://github.com/SixLabors/Fonts/pulls?q=is%3Apr+is%3Amerged+sort%3Aupdated-desc>
  - <https://github.com/SixLabors/Fonts/releases>
  - <https://raw.githubusercontent.com/SixLabors/Fonts/HEAD/README.md>
  - <https://raw.githubusercontent.com/SixLabors/Fonts/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/SixLabors/Fonts/HEAD/Directory.Build.props>
  - <https://raw.githubusercontent.com/SixLabors/Fonts/HEAD/src/SixLabors.Fonts/SixLabors.Fonts.csproj>
  - <https://raw.githubusercontent.com/SixLabors/Fonts/HEAD/src/SixLabors.Fonts/TextShaper.cs>
  - <https://raw.githubusercontent.com/SixLabors/Fonts/HEAD/src/SixLabors.Fonts/TextShapingBuffer.cs>
  - <https://raw.githubusercontent.com/SixLabors/Fonts/HEAD/src/SixLabors.Fonts/ShapingScratch.cs>
  - <https://raw.githubusercontent.com/SixLabors/Fonts/HEAD/src/SixLabors.Fonts/ShapingBuffer.cs>
  - <https://raw.githubusercontent.com/SixLabors/Fonts/HEAD/src/SixLabors.Fonts/ShapedGlyph.cs>
  - <https://raw.githubusercontent.com/SixLabors/Fonts/HEAD/tests/SixLabors.Fonts.Benchmarks/SixLabors.Fonts.Benchmarks/ShapeTextBenchmark.cs>
  - <https://raw.githubusercontent.com/SixLabors/Fonts/HEAD/tests/SixLabors.Fonts.Benchmarks/SixLabors.Fonts.Benchmarks/Config.cs>
  - <https://raw.githubusercontent.com/SixLabors/Fonts/HEAD/tests/SixLabors.Fonts.Benchmarks/SixLabors.Fonts.Benchmarks/SixLabors.Fonts.Benchmarks.csproj>
  - <https://raw.githubusercontent.com/SixLabors/Fonts/HEAD/tests/Directory.Build.targets>
  - <https://raw.githubusercontent.com/SixLabors/Fonts/HEAD/tests/Directory.Build.props>
  - <https://raw.githubusercontent.com/SixLabors/Fonts/v3.1.0/src/SixLabors.Fonts/SixLabors.Fonts.csproj>
  - <https://raw.githubusercontent.com/SixLabors/Fonts/v3.0.0/src/SixLabors.Fonts/SixLabors.Fonts.csproj>
  - <https://raw.githubusercontent.com/SixLabors/Fonts/v2.1.3/src/SixLabors.Fonts/SixLabors.Fonts.csproj>
  - <https://raw.githubusercontent.com/SixLabors/Fonts/v3.1.0/tests/Directory.Build.targets>
  - <https://raw.githubusercontent.com/SixLabors/Fonts/v3.1.0/tests/SixLabors.Fonts.Benchmarks/SixLabors.Fonts.Benchmarks/ShapeTextBenchmark.cs>
  - <https://raw.githubusercontent.com/SixLabors/Fonts/v3.1.0/tests/SixLabors.Fonts.Benchmarks/SixLabors.Fonts.Benchmarks/SixLabors.Fonts.Benchmarks.csproj>
  - <https://api.nuget.org/v3-flatcontainer/sixlabors.fonts/index.json>
  - <https://api.nuget.org/v3-flatcontainer/sixlabors.fonts/3.1.3/sixlabors.fonts.nuspec>
  - <https://api.nuget.org/v3/registration5-semver1/sixlabors.fonts/index.json>
  - <https://api.nuget.org/v3-flatcontainer/harfbuzzsharp/14.2.1.1/harfbuzzsharp.nuspec>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/sixlabors/fonts`) · [data/wave10/enrich/raw/github_com_sixlabors_fonts.json](../../../data/wave10/enrich/raw/github_com_sixlabors_fonts.json) (enrichment confidence 0.75)

</details>
