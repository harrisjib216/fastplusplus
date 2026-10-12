# hypher

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Font shaping and text layout](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟢 active

> Allocation-free Rust Knuth-Liang hyphenator with patterns embedded as automata; about 2x faster per word than the hyphenation crate.

| | |
|---|---|
| **Beats** | hyphenation crate 0.8 (embedded Liang/Knuth patterns, the common Rust hyphenation library) |
| **Claimed result** | README table (Apple M1): hyphenating 'extensive' (English) 356 ns vs 698 ns for hyphenation; 'διαμερίσματα' (Greek) 503 ns vs 1121 ns; loading English patterns 0 us vs 151 us; loading Greek patterns 0 us vs 0.826 us. Speedups 1.96x English and 2.23x Greek (derived from page data). The hypher load figures are not measured: bench.rs has no hypher load benchmark, and 0 us reflects the design (embedded automata used in place, no decoding), while the hyphenation side times Standard::from_embedded deserialization. |
| **Workload** | Hyphenating one word (English 'extensive', Greek 'διαμερίσματα') and loading the English and Greek pattern sets, via a Criterion benchmark. |
| **Metric** | latency |
| **Hardware** | Apple M1 (ARM) |
| **Compiler and flags** | cargo bench (Criterion 0.3, harness = false) in bench/; rustc version and profile flags not stated |
| **Adoption** | 142 stars, 20 forks; 3.28M crates.io downloads (1.43M recent); hosted in the typst organisation |
| **Last commit** | 2026-09-17 |
| **Links** | [repository](https://github.com/typst/hypher) · [benchmark](https://github.com/typst/hypher) |

## Verdict

A first-party Criterion 0.3 run on an Apple M1 (rustc version and flags unstated) timed one word per call: 'extensive' with English patterns 356 ns vs 698 ns for hyphenation 0.8 (about 1.96x) and 'διαμερίσματα' with monotonic Greek 503 ns vs 1121 ns (about 2.23x, derived from page data); the 0 us load rows are a design property, not a timed run. The table dates from the first README commit (2022-03-06, before 0.1.0) and has not been re-run since the tries were pre-generated (October 2022) or the Bytes buffer changed (PR #20, 2025), and the baseline also does exception lookup, soft-hyphen handling and case realignment that hypher skips, so part of the gap is less work rather than a faster equivalent.

## Use it when

- Rust text layout or typesetting that hyphenates many short words with a language that can change per word: no dictionary handle to keep alive or cache (the reason it was written for Typst, per the author's 2022 post).
- Binaries that must embed patterns: English alone adds 27 KiB and all 48 languages about 1.1 MiB, against about 2.8 MB for hyphenation's embed_all (author's figures).
- no_std, WASM or start-up-sensitive tools where hyphenation's Standard::from_embedded cost (151 us for English in the README table) matters more than the per-word time.
- Permissive-licence products: only patterns under LPPL, MPL, MIT or BSD-3 style licences are included, and the crate itself is MIT OR Apache-2.0.

## Skip it when

- When TeX-exact output matters: the generator parses only \patterns{} and drops every \hyphenation{} exception block (open issues #24 and #17), so the 15 exceptions in hyph-en-us.tex (for example 'project' and 'present', which TeX leaves unbroken, and 'ta-ble') get pattern breaks instead; the hyphenation crate consults them.
- Languages or variants not compiled in: no de-1901, en-gb, Welsh, Irish, Kazakh, Romanian or GPL-only pattern sets (issues #22, #25, closed PR #7), and no way to load a pattern file at runtime (issue #11).
- C or C++ projects: there is no C API, so this needs a Rust toolchain plus your own extern "C" shim.
- Non-standard hyphenation (spelling changes at the break, as in hyphenation's Extended dictionaries for Hungarian and Catalan) or soft-hyphen-aware input: neither is supported.

## How it is fast

Liang's pattern algorithm run over a byte-level (UTF-8) trie that tests/generate.rs builds from each .tex file, suffix-compresses into a minimal acyclic automaton (identical subtrees merged) and encodes with variable-width (i8/i16/i24) relative target offsets and shared level slices packed as dist\*10+level in one byte. The encoded tries/\*.bin are include_bytes!'d and decoded lazily state by state during the walk, so nothing is deserialized at start-up; the level array lives in a 47-byte stack buffer for words up to 45 bytes, so the hot path allocates nothing. The baseline does more per call: it scans for soft hyphens, case-folds into a new string with realignment shifts, looks the word up in an exception HashMap and returns a Vec of breaks.

## Compared with alternatives

It is the only hyphenation library in this category; the layout siblings solve other steps (Parley shapes and lays out text, Typst is a full typesetter that depends on hypher through typst-layout per crates.io reverse dependencies), so use it alongside them when your own line breaker needs hyphenation points.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | none (no_std; optional alloc feature on by default) |
| **Minimum toolchain** | Rust 1.64 (rust-version in Cargo.toml, checked by the CI min-version job); CI tests on 1.88 |
| **Platforms** | any (pure safe Rust, no SIMD or platform code, #![forbid(unsafe_code)]) |
| **Thread safety** | Stateless: hyphenate reads only static embedded data, so concurrent calls are safe; Syllables borrows the input word. |
| **Drop-in for the baseline** | no |

## Gotchas

- Without the alloc feature, words longer than MAX_INLINE_SIZE (45 bytes in src/lib.rs; the README still says 41 and the 2022 post 39) panic instead of allocating.
- Lowercasing keeps a character unchanged when its lowercase form has a different UTF-8 length or expands to several chars (for example U+0130 or U+1E9E), so patterns stop matching around it; there is no Unicode normalization either, so NFD input with combining accents misses NFC patterns. The hyphenation crate refolds and realigns these cases and offers nfc/nfd features.
- Output is hyphenation segments under each language's left/right minima, not linguistic syllables: short words come back as one segment (issue #5), and French words with apostrophes can break right after the apostrophe (issue #13, open).
- Each language is a Cargo feature; the default 'full' feature embeds all 48, so pick features explicitly to keep binaries small.

## Known shortcomings

- Rust hyphenation crate (language-filter mismatch); text-layout primitive, not shaping. bench/bench.rs criterion run against the hyphenation 0.8 crate (Apple M1; rustc and flags unstated): 1.96x English, 2.23x Greek (derived); the '0 us load' is a design property, never timed. Baseline is the Rust-ecosystem incumbent (1.15M downloads).
- The README table dates from the first README commit (2022-03-06, before 0.1.0) and was never re-run after the tries were pre-generated (October 2022) or the Bytes change (PR #20). Not like-for-like: the hyphenation crate also scans soft hyphens, refolds case, looks up an exception HashMap and returns a Vec. hypher's generate.rs parses only \patterns{} and drops \hyphenation{} exceptions (issues #24 and #17 open; 15 en-us exceptions such as 'project' and 'present'), though hyph-de and hyph-el have none so the benchmark words agree. MAX_INLINE_SIZE is 45 in lib.rs while the README says 41.

## Caveats and trade-offs

Two single-word micro-benchmarks on one machine; Criterion source is public (bench/bench.rs) but the rustc version and flags are not stated and the README run is undated, so tier C. The word benchmarks do the same work on both sides (hyphenate one word with English and Greek patterns, drain the syllable or break iterator); hyphenation uses EnglishUS and GreekMono patterns. The pattern-loading rows are not a like-for-like measurement: hypher's 0 us is a design property, not a timed run. The baseline is the hyphenation crate (0.8.4, last released 2021-08-19, 1.15M crates.io downloads, 58 stars), the long-standing Rust Knuth-Liang hyphenation crate and a recognisable incumbent within Rust; it is not HarfBuzz, FreeType or ICU. Hyphenation is a text-layout step, not shaping. Pattern files in patterns/ carry their own licenses (LPPL, MPL, MIT, BSD-3) and are embedded into the binary.

Patterns are compiled into the binary as finite automata (zero load time, binary size grows with languages, e.g. English is a few tens of KiB); no_std and no dependencies; supports 48 languages; pattern files carry their own licences.

## Maintenance

Active (0.1.8 released 2026-09-17, 3.29M crates.io downloads, used by typst-layout and nine other crates), dual MIT/Apache-2.0 code with permissively licensed embedded patterns; copyable as a Rust crate, not from C++.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** README table compares hypher with the hyphenation crate on Apple M1, and the Criterion source is public (bench/bench.rs, bench/Cargo.toml: criterion 0.3, hyphenation 0.8 with embed_all), but the rustc version and profile flags are not stated and the run is undated; first-party, so C.
- **Verifier notes:** Numbers match the README; bench.rs times hypher::hyphenate against hyphenation::Standard::hyphenate on the same words. License MIT OR Apache-2.0 (Cargo.toml), not a fork, not archived, last commit 2026-09-17 (version bump to 0.1.8), active.
- **Fields the verifier corrected:** `claimed_speedup`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/typst/hypher/HEAD/README.md>
  - <https://github.com/typst/hypher>
  - <https://raw.githubusercontent.com/typst/hypher/HEAD/bench/Cargo.toml>
  - <https://raw.githubusercontent.com/typst/hypher/HEAD/bench/bench.rs>
  - <https://raw.githubusercontent.com/typst/hypher/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/typst/hypher/HEAD/src/lib.rs>
  - <https://github.com/typst/hypher/commits/main>
  - <https://crates.io/api/v1/crates/hypher>
  - <https://crates.io/api/v1/crates/hyphenation>
  - <https://github.com/tapeinosyne/hyphenation>
- **Sources the enricher read:**
  - <https://github.com/typst/hypher>
  - <https://raw.githubusercontent.com/typst/hypher/HEAD/README.md>
  - <https://raw.githubusercontent.com/typst/hypher/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/typst/hypher/HEAD/bench/Cargo.toml>
  - <https://raw.githubusercontent.com/typst/hypher/HEAD/bench/bench.rs>
  - <https://raw.githubusercontent.com/typst/hypher/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/typst/hypher/HEAD/src/lang.rs>
  - <https://raw.githubusercontent.com/typst/hypher/HEAD/tests/generate.rs>
  - <https://raw.githubusercontent.com/typst/hypher/HEAD/.github/workflows/ci.yml>
  - <https://raw.githubusercontent.com/typst/hypher/6b6c862/README.md>
  - <https://raw.githubusercontent.com/typst/hypher/c7395d6/README.md>
  - <https://raw.githubusercontent.com/typst/hypher/6b6c862/bench/bench.rs>
  - <https://github.com/typst/hypher/commits/main/README.md>
  - <https://github.com/typst/hypher/tree/main/src>
  - <https://github.com/typst/hypher/tree/main/tests>
  - <https://github.com/typst/hypher/issues?q=is%3Aissue>
  - <https://github.com/typst/hypher/pulls?q=is%3Apr>
  - <https://github.com/typst/hypher/issues/5>
  - <https://github.com/typst/hypher/issues/13>
  - <https://github.com/typst/hypher/issues/23>
  - <https://github.com/typst/hypher/issues/24>
  - <https://github.com/typst/hypher/issues/33>
  - <https://raw.githubusercontent.com/tapeinosyne/hyphenation/HEAD/README.md>
  - <https://raw.githubusercontent.com/tapeinosyne/hyphenation/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/tapeinosyne/hyphenation/HEAD/src/hyphenator.rs>
  - <https://github.com/laurmaedje/laurmaedje.github.io>
  - <https://github.com/laurmaedje/laurmaedje.github.io/tree/main/posts>
  - <https://raw.githubusercontent.com/laurmaedje/laurmaedje.github.io/main/posts/hypher.md>
  - <https://crates.io/api/v1/crates/hypher>
  - <https://crates.io/api/v1/crates/hypher/reverse_dependencies?per_page=20>
  - <https://raw.githubusercontent.com/typst/hypher/HEAD/patterns/hyph-en-us.tex>
  - <https://raw.githubusercontent.com/typst/hypher/HEAD/patterns/hyph-de-1996.tex>
  - <https://raw.githubusercontent.com/typst/hypher/HEAD/patterns/hyph-el-monoton.tex>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/typst/hypher`) · [data/wave10/enrich/raw/github_com_typst_hypher.json](../../../data/wave10/enrich/raw/github_com_typst_hypher.json) (enrichment confidence 0.8)

</details>
