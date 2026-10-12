# fast-grapheme-segmenter

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [Unicode and UTF-8](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟢 active

> Forward-only Rust UAX #29 grapheme segmenter: 1.3-2.1x faster than ICU4X's icu_segmenter at splitting, 2.7-36x at counting.

| | |
|---|---|
| **Beats** | icu_segmenter 2.3.0 (ICU4X grapheme cluster segmenter) and unicode-segmentation 1.13.3 (the common Rust crate) |
| **Claimed result** | README tables, this crate vs icu4x vs unicode-segmentation: counting clusters English 0.05 us vs 1.82 us vs 3.40 us (35.7x and 66.6x), Russian 0.42 vs 2.31 vs 3.77 us (5.4x, 8.9x), Hindi 0.47 vs 1.27 vs 5.01 us (2.7x, 10.6x), emoji 0.35 vs 1.06 vs 2.52 us (3.0x, 7.2x), source code 0.21 vs 2.74 vs 6.05 us (13.1x, 28.9x); collecting every cluster English 1.24 vs 2.28 vs 4.76 us (1.8x, 3.8x), Hindi 1.04 vs 1.33 vs 5.29 us (1.3x, 5.1x), source code 2.20 vs 2.99 vs 7.33 us (1.4x, 3.3x). |
| **Workload** | UAX #29 extended grapheme cluster segmentation of about 300-byte samples in nine corpora (English, Russian, Arabic, Hindi, Japanese, Korean, Mandarin, emoji, source code), three modes: counting clusters, collecting every cluster, collecting offsets; criterion. |
| **Metric** | latency |
| **Hardware** | 'x86_64 Linux' only (no CPU model) |
| **Compiler and flags** | Not stated. Cargo.toml has no [profile.bench] or [profile.release] override, so cargo's default bench profile applies; edition 2024 implies Rust 1.85 or later; rustc version and target-cpu are not given. |
| **Adoption** | 6 stars, 0 forks, 20 commits; crates.io: 42 total downloads, versions 0.0.0, 0.1.0 and 0.1.1 all published 2026-09-17 (crates.io API, 2026-10-03) |
| **Last commit** | 2026-09-17 |
| **Links** | [repository](https://github.com/cometkim/fast-grapheme-segmenter) · [benchmark](https://github.com/cometkim/fast-grapheme-segmenter) |

## Verdict

The author's criterion harness (benches/graphemes.rs) timed \~300-byte UDHR, emoji and Rust-source samples in nine corpora on an unnamed x86_64 Linux machine, with cargo's default bench profile and an unstated rustc. Counting was 2.7x (Hindi) to 35.7x (pure-ASCII English) faster than icu_segmenter 2.3.0 and 7.2x-66.6x faster than unicode-segmentation 1.13.3; collecting cluster slices or start offsets was 1.3x-2.1x faster than icu_segmenter and 2.6x-5.5x faster than unicode-segmentation. Between the first README (commit cf97507) and the current one (d31274d) the crate's code did not change, yet its own times moved by up to 45% (Russian count 0.29 to 0.42 us, Korean collect 0.75 to 0.93 us). The tables also predate 0.1.1's iterator change, so read the ratios as roughly +/-30%.

## Use it when

- Rust code that counts user-perceived characters (length limits, truncation, column counts), especially on ASCII-heavy text, where count_graphemes is close to a SWAR byte count (0.05 us for the \~290-byte English sample).
- Forward-only iteration over short strings (hundreds of bytes) where unicode-segmentation is used today: the README shows 2.6x-5.5x faster cluster and offset collection, and forward call sites map one to one.
- no_std, embedded or wasm targets that need current Unicode 17 rules: no dependencies, #![forbid(unsafe_code)], about 19 KB of tables, and a wasm/ build of about 41 KB with UTF-16 entry points for JavaScript hosts.
- Code that must agree with ICU4X on segmentation without ICU4X's data-provider stack: tests/conformance.rs checks agreement with icu_segmenter on every GraphemeBreakTest.txt case and on 20,000 random rule-stress strings, and CI runs cargo test.

## Skip it when

- C or C++ projects: this is a Rust crate with no published C header. The wasm/ crate exports a plain C ABI (fgs_count_utf8, fgs_boundaries_utf8 and others), but it is unpublished (publish = false) and only built and documented for wasm32. For C++, the catalogued uni-algo needs no FFI.
- Editors and rope-based text that need backward motion, seeking from an arbitrary offset or chunked input: there is no DoubleEndedIterator and no GraphemeCursor equivalent, so use unicode-segmentation or icu_segmenter.
- Word, sentence or line breaking, or locale tailoring: use icu_segmenter.
- Dependencies that must be mature: the crate is one author's port, published 2026-09-17 (versions 0.0.0, 0.1.0 and 0.1.1 the same day), with 43 crates.io downloads and no reverse dependencies as of 2026-10-04.
- Mostly non-ASCII text where the count speedup is the reason to switch: against icu_segmenter the count lead falls to 2.7x (Hindi) to 5.9x (Japanese), and splitting is only 1.3x faster on Russian and Hindi.

## How it is fast

Category lookup is tiered. A single byte load from flat per-codepoint tables covers U+0000-U+309F, U+A660-U+ABFF and U+1F000-U+1FAFF. Arithmetic covers CJK through Vai, Hangul syllables (LV every 28th code point) and the variation selectors, and a binary search over packed ranges covers the rest. Every pairwise UAX #29 rule is folded at compile time into a 256-byte PAIR_MASK table indexed by (before &lt;&lt; 4 | after), and the context that GB9c (Indic conjuncts), GB11 (emoji ZWJ) and GB12/13 (flag parity) need is packed into one u8 state, so each boundary decision is one AND against a table byte. count_graphemes adds a SWAR path: when at least half of the first 64 bytes are printable ASCII, it finds printable-ASCII runs 8 bytes at a time with zero-byte bit tricks and adds each run's length in one step. That path produces the 35.7x English count, because the English sample is a single printable-ASCII run. The iterators use a lazily armed one-byte shortcut for adjacent printable-ASCII pairs.

## Compared with alternatives

Within the catalog it is the Rust choice for grapheme-only work. Pick ICU4X when you need word or line segmentation, backward iteration or locale data, and pick the same author's unicode-segmenter in JavaScript, ugrapheme in Python, or uni-algo in C++ (which also beats ICU on grapheme and word breaks) for those languages.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | none (dev-dependencies only: criterion 0.8, icu_segmenter 2.3.0, unicode-segmentation 1.13.3) |
| **Minimum toolchain** | Not declared (no rust-version in Cargo.toml). Edition 2024 needs Rust 1.85+, and tables.rs calls u32::is_multiple_of, which implies Rust 1.87+ (inferred). CI tests stable only. |
| **Platforms** | Any Rust target, including no_std and wasm32. Scalar code only, with no SIMD intrinsics; the SWAR words are read with u64::from_le_bytes, so it is endian-neutral. |
| **Thread safety** | Not documented. These are pure functions and iterators over a borrowed &str or &[u16], with no global mutable state and only static tables, so they are usable from any thread (inferred from the source). |
| **Drop-in for the baseline** | partial — covers the forward subset of unicode-segmentation's graphemes/grapheme_indices without the is_extended argument, and has no reverse iteration or GraphemeCursor. Against icu_segmenter, grapheme_boundaries yields cluster start offsets only, whereas segment_str also yields 0 and the final length. |

## Gotchas

- The README timings were measured before commit 0bdcd1f (released as 0.1.1). That commit removed the iterators' 64-byte ASCII sample from Driver::new and arms the ASCII shortcut lazily, after 'perf regressions observed in real-world use cases' where callers rebuild an iterator for each cluster. The collect-cluster and collect-offset tables were not re-run on the shipped code.
- count_graphemes still picks its path from a 64-byte head sample. Text that starts ASCII-heavy and then turns non-ASCII pays a word-at-a-time run scan in every gap, and text that starts non-ASCII never takes the bulk path. Both paths are correct; only speed changes.
- In count mode the crate's dedicated count function runs against the baselines' iterator .count(), because neither baseline has a count API. The 35.7x and 66.6x English figures therefore measure the SWAR ASCII shortcut on a pure printable-ASCII sample, not faster rule evaluation.
- The Unicode 17.0 tables are compiled in, so a Unicode upgrade needs a new crate release (scripts/unicode.py regenerates them). In the UTF-16 API, each lone surrogate becomes U+FFFD as its own cluster, which is ICU4X's policy.

## Known shortcomings

- Rust crate (language-filter mismatch; 42 crates.io downloads, all commits 2026-09-17). README tables match benches/graphemes.rs but the machine is only 'x86_64 Linux' with no CPU or rustc version; the baseline is icu_segmenter 2.3.0 (ICU4X) plus unicode-segmentation, not ICU4C. Unicode segmentation, moved to wave 3's unicode-utf8 category.
- README tables predate commit 0bdcd1f (0.1.1, lazy ASCII arming in iterators) and the collect and offset tables were never re-run on the shipped code; the same crate code was measured twice (README cf97507 versus d31274d) with its own times moving up to 45% (Russian count 0.29 to 0.42 us). Count mode pits a dedicated SWAR count function against the baselines' iterator .count(), and the 35.7x English figure is a pure printable-ASCII sample. Crate two weeks old (43 downloads, no reverse dependencies); minimum Rust 1.87 inferred from u32::is_multiple_of but not declared.

## Caveats and trade-offs

Rust crate, not C or C++: outside the default C++ language filter. The baseline is ICU4X's Rust icu_segmenter 2.3.0 (a recognisable Unicode incumbent, but not ICU4C) and the unicode-segmentation crate; this crate's README does not benchmark against Intl.Segmenter, which it only names as the behaviour it replicates. First-party numbers from benches/graphemes.rs (criterion) on 'x86_64 Linux' with no CPU model, rustc version or flags. The samples are about 300 bytes each (UDHR text in eight languages, an emoji string and a Rust snippet), so start-up costs weigh heavily. The headline 35.7x/66.6x is the count-only English path, where printable ASCII is consumed 8 bytes at a time with SWAR masks; in the collect-every-cluster mode the lead over icu_segmenter is 1.3x to 2.0x, and 1.4x to 2.1x when collecting offsets. Forward-only: no backward iteration, seeking or chunked input. The README claims agreement with icu_segmenter on Unicode 17 GraphemeBreakTest.txt and 20,000 pseudo-random strings (tests/conformance.rs, not run here). The repo and crate are about two weeks old (all 20 commits and all three releases on 2026-09-17); it is a port of cometkim/unicode-segmenter by the same author. Category: Unicode text segmentation (wave 3's unicode-utf8 category), not font shaping or layout.

Forward-only grapheme segmentation (UAX #29) only: no word, sentence or line breaking, no bidi. Rust crate, not callable from C++ without an FFI layer. Direct port of the author's JavaScript unicode-segmenter, which compresses the Unicode tables.

## Maintenance

Active but brand-new: one author, all 20 commits and three releases on 2026-09-17, and no issues yet (one open Renovate PR). MIT-licensed, about 1,100 lines plus generated tables, no unsafe and no dependencies, so it is easy to vendor or pin.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** Every claimed number matches the README tables, which come from the public criterion harness benches/graphemes.rs (criterion 0.8, icu_segmenter 2.3.0 and unicode-segmentation 1.13.3 as dev-dependencies in Cargo.toml), but the page states only 'x86_64 Linux': no CPU model, no rustc version, no flags. First-party with partial methodology is C; the &gt;50x count-mode figure against unicode-segmentation would also be capped at C with flags unstated.
- **Verifier notes:** Numbers verified against the README and benches/graphemes.rs; C stands. The orchestrator's note that this compares against Intl.Segmenter does not hold: the bench compares against icu_segmenter (ICU4X) and unicode-segmentation in Rust. Recategorise to Unicode text processing (unicode-utf8); the language key may need a decision override.
- **Fields the verifier corrected:** `compiler_and_flags`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/cometkim/fast-grapheme-segmenter>
  - <https://github.com/cometkim/fast-grapheme-segmenter/commits/main>
  - <https://github.com/cometkim/fast-grapheme-segmenter/tree/main/benches>
  - <https://github.com/cometkim/fast-grapheme-segmenter/tree/main/wasm>
  - <https://raw.githubusercontent.com/cometkim/fast-grapheme-segmenter/HEAD/README.md>
  - <https://raw.githubusercontent.com/cometkim/fast-grapheme-segmenter/HEAD/benches/graphemes.rs>
  - <https://raw.githubusercontent.com/cometkim/fast-grapheme-segmenter/HEAD/Cargo.toml>
  - <https://crates.io/api/v1/crates/fast-grapheme-segmenter>
- **Sources the enricher read:**
  - <https://github.com/cometkim/fast-grapheme-segmenter>
  - <https://github.com/cometkim/fast-grapheme-segmenter/commits/main>
  - <https://github.com/cometkim/fast-grapheme-segmenter/commits/main/README.md>
  - <https://github.com/cometkim/fast-grapheme-segmenter/commits/main/src/lib.rs>
  - <https://github.com/cometkim/fast-grapheme-segmenter/commit/0bdcd1f026190692f5b1cc27c0b58e4b009f1c26>
  - <https://github.com/cometkim/fast-grapheme-segmenter/commit/d31274d0ac1ea824c1de13e670a12440c56711ee>
  - <https://github.com/cometkim/fast-grapheme-segmenter/issues?q=is%3Aissue>
  - <https://github.com/cometkim/fast-grapheme-segmenter/pulls?q=is%3Apr>
  - <https://raw.githubusercontent.com/cometkim/fast-grapheme-segmenter/HEAD/README.md>
  - <https://raw.githubusercontent.com/cometkim/fast-grapheme-segmenter/cf9750752cefb1d242a66ba153e560896cd41861/README.md>
  - <https://raw.githubusercontent.com/cometkim/fast-grapheme-segmenter/cf9750752cefb1d242a66ba153e560896cd41861/Cargo.toml>
  - <https://raw.githubusercontent.com/cometkim/fast-grapheme-segmenter/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/cometkim/fast-grapheme-segmenter/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/cometkim/fast-grapheme-segmenter/HEAD/benches/graphemes.rs>
  - <https://raw.githubusercontent.com/cometkim/fast-grapheme-segmenter/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/cometkim/fast-grapheme-segmenter/HEAD/src/tables.rs>
  - <https://raw.githubusercontent.com/cometkim/fast-grapheme-segmenter/HEAD/tests/conformance.rs>
  - <https://raw.githubusercontent.com/cometkim/fast-grapheme-segmenter/HEAD/scripts/unicode.py>
  - <https://raw.githubusercontent.com/cometkim/fast-grapheme-segmenter/HEAD/.github/workflows/ci.yml>
  - <https://raw.githubusercontent.com/cometkim/fast-grapheme-segmenter/HEAD/wasm/Cargo.toml>
  - <https://raw.githubusercontent.com/cometkim/fast-grapheme-segmenter/HEAD/wasm/build.sh>
  - <https://raw.githubusercontent.com/cometkim/fast-grapheme-segmenter/HEAD/wasm/src/lib.rs>
  - <https://raw.githubusercontent.com/cometkim/fast-grapheme-segmenter/HEAD/LICENSE>
  - <https://crates.io/api/v1/crates/fast-grapheme-segmenter>
  - <https://crates.io/api/v1/crates/fast-grapheme-segmenter/reverse_dependencies>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/cometkim/fast-grapheme-segmenter`) · [data/wave10/enrich/raw/github_com_cometkim_fast_grapheme_segmenter.json](../../../data/wave10/enrich/raw/github_com_cometkim_fast_grapheme_segmenter.json) (enrichment confidence 0.75)

</details>
