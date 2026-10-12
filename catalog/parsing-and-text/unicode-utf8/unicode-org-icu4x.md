# ICU4X

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [Unicode and UTF-8](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Unicode-3.0` · 🟢 active

> Unicode Consortium's Rust rewrite of ICU; a 2023 first-party post says its line and word segmenters beat ICU4C's break iterators by 19-52%.

| | |
|---|---|
| **Beats** | ICU4C (line break and word break iterators) |
| **Claimed result** | Snippet only (ICU4X 1.2 announcement, Unicode blog, 2023-04-17; quote confirmed by two separate search snippets, page not opened): 'line and word segmenters are 19.1% and 52.2% faster in non-complex scripts and 46.9% and 32.1% faster in Chinese than the equivalents in ICU4C, respectively'. The same post reports segmentation data 20.1% smaller than ICU4C's (60.7% smaller for line break). |
| **Workload** | Line and word segmentation (UAX #14 and UAX #29) of non-complex-script text and of Chinese text, ICU4X segmenter versus ICU4C equivalents. |
| **Metric** | throughput |
| **Adoption** | 1.9k stars; maintained by the Unicode Consortium |
| **Last commit** | 2026-10-02 |
| **Links** | [repository](https://github.com/unicode-org/icu4x) · [benchmark](https://blog.unicode.org/2023/04/icu4x-12-now-with-text-segmentation-and.html) |

## Verdict

The only number is from the Unicode blog's ICU4X 1.2 announcement (2023-04-17), known here only through search snippets: line and word segmentation 19.1% and 52.2% faster than ICU4C on non-complex scripts, and 46.9% and 32.1% faster on Chinese. It gives no hardware, compiler, ICU4C version, test text or method, and the repo has no ICU4C harness. Reading the code shows the Chinese word figure does not compare equal work. ICU4X 1.2's dictionary.rs already took the greedy longest match and ignored trie values, while ICU4C's CjkBreakEngine (dictbe.cpp) checks NFKC and runs a minimum-cost dynamic program. The 1.2 segmenter also predates later conformance fixes to line, sentence and word rules.

## Use it when

- Rust, WebAssembly, Dart or JS code that needs UAX #29 word, grapheme or sentence boundaries, or UAX #14 line breaking, without linking ICU4C and its separate data file. Compiled data is baked in, and the crate builds as no_std plus alloc.
- Text layout or browser-style line breaking that needs CSS options: LineBreakStrictness (strict, normal, loose, anywhere) and LineBreakWordOption (break-all, keep-all).
- Size-constrained builds with Thai, Lao, Khmer or Burmese text. The LSTM models replace per-language word dictionaries, and new_auto picks them.
- Input that is already UTF-8 or Latin-1. segment_str, segment_utf8 (which tolerates ill-formed input) and segment_latin1 run on those buffers directly, with no UTF-16 conversion and no UText wrapper.
- Projects that already use ICU4X for formatting, collation or normalization and want one Unicode-maintained stack.

## Skip it when

- When you need a current, measured win over ICU4C. The only ICU4C comparison is the 2023 first-party post about ICU4X 1.2. Correctness fixes have since changed the segmenter code: LB25/LB8a line rules (PR #4389, Dec 2023), Unicode 15.0 sentence rules, dictionary rewinding and word colon tailoring (both 2.3). Benchmark on your own text.
- Chinese or Japanese word segmentation where split quality matters, such as search indexing. Greedy longest match can split ambiguous text differently from ICU4C's cost-minimizing search, and the BudouX/phrase alternative is still an open issue (#1803).
- High-throughput Thai, Lao, Khmer or Burmese segmentation through new_auto. It loads the LSTM model, which the docs call more expensive at runtime than the dictionary; use new_dictionary when speed matters more than data size. Issue #7218 (open) reports double line-break opportunities around spaces in Khmer.
- C++ projects that cannot add a Rust/cargo build step. You must build the icu_capi library, every segment() call heap-allocates an iterator, and each boundary costs one FFI call that returns int32_t, so offsets past 2^31-1 come back as -1.
- Code that needs ICU4C BreakIterator features such as random access (preceding, following, isBoundary) or custom rule strings at runtime. No such methods appear in the segmenter sources read here: the iterators only move forward, and rules are fixed when the data is generated.

## How it is fast

Each code point's break property comes from one CodePointTrie lookup. Data generation compiles the segmentation rules into a pairwise break-state table (left property x right property), with intermediate states for rules that need lookahead, and the iterator walks it forward over native UTF-8, Latin-1 or UTF-16 with no UText layer. Data is baked into the binary as zero-copy zerovec structures, and locale tailoring is applied at runtime as a property-table override; per search snippets, the blog credits runtime tailoring for having fewer rule tables. Thai, Lao, Khmer and Burmese use either an LSTM model (the blog snippet says SIMD made inference about 3x faster than a naive version) or a Char16Trie dictionary, a port of ICU's UCharsTrie. Chinese and Japanese word breaking takes the longest dictionary match and ignores the dictionary's cost values. ICU4C's CjkBreakEngine instead runs an NFKC normalization check and a dynamic-programming minimum-cost search, so it does more work per character.

## Compared with alternatives

Pick ICU4X when you need line breaking with CSS options plus dictionary- or LSTM-based word segmentation for Southeast Asian and CJK scripts, maintained by the Unicode Consortium. For C++ word and grapheme iteration, uni-algo is header-only and measured 4.8x faster than ICU word breaking (11379.4 vs 2355.47 ms, derived from page data). For grapheme counting in Rust, fast-grapheme-segmenter benchmarks ICU4X's own grapheme segmenter as its slow baseline (1.82 us vs 0.05 us on English).

## Integration

| | |
|---|---|
| **Form** | crate (icu_segmenter, or the icu umbrella crate); static or shared library icu_capi with Diplomat C and C++ headers for other languages |
| **Dependencies** | icu_collections, icu_provider, zerovec, utf8_iter, smallvec, potential_utf; the default compiled_data feature adds icu_segmenter_data and icu_locale_fallback; the lstm feature adds core_maths |
| **Minimum toolchain** | Rust 1.88 (workspace rust-version for 2.3.x). The C++ headers use std::string_view and std::u16string_view, so C++17 or later (inferred; not stated in the files read). |
| **Platforms** | any Rust target, including wasm32 and no_std plus alloc; FFI for C, C++, JS (npm), Dart (pub.dev) |
| **Thread safety** | not documented in the files read. Segmenter objects are immutable after construction, and each segment_\* call returns its own iterator. |
| **Drop-in for the baseline** | no |

## Gotchas

- Choose the constructor deliberately. new_auto means LSTM for Southeast Asian scripts (plus the dictionary for Chinese and Japanese in the word segmenter). new_for_non_complex_scripts treats a Thai run as a single segment and, in the word segmenter, leaves Chinese and Japanese unsegmented. The line segmenter never loads a Chinese/Japanese dictionary, because UAX #14 rules handle CJK.
- Rule versions are pinned to the crate's data: the line segmenter defaults to UAX #14 for Unicode 15.1, with separate \*_17_\* constructors for 17.0. Boundaries can differ from the ICU4C version you compare against.
- The experimental _neo_ (V2 state-machine) constructors sit behind the unstable feature. Issue #8522 (Sept 2026, fixed by PR #8523) showed the V2 dictionary path dropping the final breakpoint, so keep them out of production.
- The upstream V1 iterator looks up the trie property twice per code point. The unmerged DioxusLabs/icu4x fork PRs #1 and #2 (Sept 2026) report 2.0-2.5x on ASCII prose without LTO but only about 1.1x with LTO, so turn on LTO before judging its speed.

## Known shortcomings

- Rust library with Diplomat-generated C++ headers (language-filter mismatch). Segmenter numbers (19.1% and 52.2% faster non-complex, 46.9% and 32.1% faster Chinese vs ICU4C) exist only in search snippets of the blocked Unicode blog; the repo has no ICU4C comparison (bench.rs is Rust-only, issue #66 open). Unicode segmentation, moved to wave 3's unicode-utf8 category.
- The only ICU4C number is still the 2023 blog snippet (ICU4X 1.2) and the Chinese word 32.1% figure compares unequal work: ICU4X's dictionary segmenter is a greedy longest match that ignores trie cost values (icu 1.2.0 dictionary.rs) while ICU4C's CjkBreakEngine does an NFKC check plus minimum-cost dynamic programming (dictbe.cpp); the 1.2 code predates conformance fixes (PR #4389 LB25/LB8a in December 2023, sentence 15.0, the 2.3 dictionary rewind and colon tailoring #7952). new_auto loads the LSTM model (slower than the dictionary); the V1 iterator does the trie lookup twice per code point; C++ use needs a Rust-built icu_capi with int32_t next(); Khmer issue #7218 open; neo V2 bug #8522 fixed.

## Caveats and trade-offs

Numbers appear only in search snippets of the blocked Unicode blog post; test data, hardware, compiler, ICU4C version and method are unknown, and they describe ICU4X 1.2 (2023), several major versions before the current 2.x code. The repo has no ICU4C comparison harness: components/segmenter/benches/bench.rs is a Rust-only criterion benchmark, issue #66 ('Performance testing against ICU4C', opened 2020-04-30) is still open without data, and in discussion #2948 (January 2023) maintainers said they had no up-to-date comparison numbers. The Unicode Consortium maintains both ICU4X and ICU4C, so the figures are first-party. Rust implementation; C++ use goes through Diplomat-generated headers (ffi/capi/bindings/cpp/icu4x/LineSegmenter.hpp, WordSegmenter.hpp) over the C ABI, whose overhead was not part of the quoted measurement, so it does not match the C++ language filter. Category fit: Unicode text segmentation (UAX #14 and #29, ICU baseline), not font shaping or rasterization.

Implemented in Rust with Diplomat-generated C and C++ headers (ffi/capi), so callable from C++ but needs a Rust-built library. Design goals are small, modular code and pluggable locale data. The segmenter covers grapheme, word, sentence and line breaking; normalizer, collator and other components also exist. The speed claim found concerns only the segmenter.

## Maintenance

Actively developed by the Unicode Consortium's ICU4X technical committee (2.3.x releases; 1.9k stars; 654 open issues). The Unicode-3.0 license is MIT-style and also covers the data, so it is copyable, but C++ use means shipping a Rust-built library.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The ICU4C comparison exists only on the Unicode blog's ICU4X 1.2 announcement (2023-04-17), which is egress-blocked here; two independent WebSearch snippets return the same quote (line 19.1% and word 52.2% faster in non-complex scripts, 46.9% and 32.1% in Chinese). The repo carries no ICU4C harness or numbers (components/segmenter/benches/bench.rs is criterion Rust-only; issue #66 'Performance testing against ICU4C' is still open with no data; discussion #2948 has no numbers). Snippet-only and first-party (Unicode maintains both libraries), so C.
- **Verifier notes:** Kept at C: quote confirmed via two WebSearch snippets but the blog stays blocked and the repo has no ICU4C numbers; benchmark_url now points to the blog post (found via search, not opened). Language stays Rust (C++ access via Diplomat headers in ffi/capi/bindings/cpp); it fails the default C++ language filter, so treat it as an any-language entry. Category for the orchestrator: Unicode segmentation, belongs in wave 3's unicode-utf8 category with the ICU baseline, not font-shaping-text-layout.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/unicode-org/icu4x>
  - <https://github.com/unicode-org/icu4x/commits/main>
  - <https://raw.githubusercontent.com/unicode-org/icu4x/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/unicode-org/icu4x/HEAD/components/segmenter/README.md>
  - <https://raw.githubusercontent.com/unicode-org/icu4x/HEAD/components/segmenter/benches/bench.rs>
  - <https://raw.githubusercontent.com/unicode-org/icu4x/HEAD/ffi/capi/bindings/cpp/icu4x/LineSegmenter.hpp>
  - <https://raw.githubusercontent.com/unicode-org/icu4x/HEAD/ffi/capi/bindings/cpp/icu4x/WordSegmenter.hpp>
  - <https://github.com/unicode-org/icu4x/discussions/2948>
  - <https://github.com/unicode-org/icu4x/issues/66>
  - <https://github.com/unicode-org/icu4x/discussions/3522>
- **Sources the enricher read:**
  - <https://github.com/unicode-org/icu4x>
  - <https://raw.githubusercontent.com/unicode-org/icu4x/HEAD/README.md>
  - <https://raw.githubusercontent.com/unicode-org/icu4x/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/unicode-org/icu4x/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/unicode-org/icu4x/HEAD/components/segmenter/README.md>
  - <https://raw.githubusercontent.com/unicode-org/icu4x/HEAD/components/segmenter/Cargo.toml>
  - <https://raw.githubusercontent.com/unicode-org/icu4x/HEAD/components/segmenter/src/lib.rs>
  - <https://raw.githubusercontent.com/unicode-org/icu4x/HEAD/components/segmenter/src/line.rs>
  - <https://raw.githubusercontent.com/unicode-org/icu4x/HEAD/components/segmenter/src/word.rs>
  - <https://raw.githubusercontent.com/unicode-org/icu4x/HEAD/components/segmenter/src/grapheme.rs>
  - <https://raw.githubusercontent.com/unicode-org/icu4x/HEAD/components/segmenter/src/rule_segmenter_v1.rs>
  - <https://raw.githubusercontent.com/unicode-org/icu4x/HEAD/components/segmenter/src/rule_segmenter_v2.rs>
  - <https://raw.githubusercontent.com/unicode-org/icu4x/HEAD/components/segmenter/src/complex/mod.rs>
  - <https://raw.githubusercontent.com/unicode-org/icu4x/HEAD/components/segmenter/src/complex/dictionary.rs>
  - <https://raw.githubusercontent.com/unicode-org/icu4x/HEAD/components/segmenter/src/complex/lstm/mod.rs>
  - <https://raw.githubusercontent.com/unicode-org/icu4x/HEAD/components/segmenter/benches/bench.rs>
  - <https://raw.githubusercontent.com/unicode-org/icu4x/icu@1.2.0/components/segmenter/src/dictionary.rs>
  - <https://raw.githubusercontent.com/unicode-org/icu4x/HEAD/ffi/capi/Cargo.toml>
  - <https://raw.githubusercontent.com/unicode-org/icu4x/HEAD/ffi/capi/bindings/cpp/icu4x/LineSegmenter.hpp>
  - <https://raw.githubusercontent.com/unicode-org/icu4x/HEAD/ffi/capi/bindings/cpp/icu4x/LineSegmenter.d.hpp>
  - <https://raw.githubusercontent.com/unicode-org/icu4x/HEAD/ffi/capi/bindings/cpp/icu4x/LineBreakIteratorUtf8.d.hpp>
  - <https://raw.githubusercontent.com/unicode-org/icu/main/icu4c/source/common/dictbe.cpp>
  - <https://github.com/unicode-org/icu4x/issues?q=is%3Aissue+segmenter+dictionary+ICU4C>
  - <https://github.com/unicode-org/icu4x/discussions/3522>
  - <https://github.com/unicode-org/icu4x/issues/8522>
  - <https://github.com/unicode-org/icu4x/pull/7952>
  - <https://github.com/unicode-org/icu4x/pull/4389>
  - <https://github.com/unicode-org/icu4x/pulls?q=is%3Apr+segmenter+author%3Anicoburns>
  - <https://github.com/DioxusLabs/icu4x/pull/1>
  - <https://github.com/DioxusLabs/icu4x/pull/2>
  - WebSearch: ICU4X segmenter performance compared ICU4C benchmark line word break (snippet of blog.unicode.org/2023/04, page not opened)
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/unicode-org/icu4x`) · [data/wave10/enrich/raw/github_com_unicode_org_icu4x.json](../../../data/wave10/enrich/raw/github_com_unicode_org_icu4x.json) (enrichment confidence 0.65)

</details>
