# regexr (Rust regex engine with x86-64/ARM64 JIT)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [Regex engines](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟢 active

> Pure-Rust regex engine with lookarounds, backreferences and an x86-64/AArch64 JIT; claims up to 4x over the regex crate.

| | |
|---|---|
| **Beats** | regex crate (Rust); PCRE2 with JIT as the second comparison |
| **Claimed result** | benches/competitors.rs (criterion, results gitignored, no hardware or rustc version): same-semantics rows url_extraction 1.95-1.99x and html_tags 1.33-1.43x over the regex crate, email about 1.0x; the log_parsing 3.91-4.09x headline compares regexr's ASCII \d, \w and \b against the regex crate's Unicode classes, and unicode_letters is not comparable (regexr's \w+ skips non-Latin words). Loses to PCRE2 JIT on url_extraction and unicode_letters; non-JIT path 0.80-0.87x of regex. |
| **Workload** | Regex matching benchmarks (log parsing, URL extraction, Unicode letters, HTML tags, word boundary, email validation, alternation) reported as speedup relative to the regex crate. |
| **Metric** | throughput |
| **Compiler and flags** | cargo bench with criterion 0.8 (benches/competitors.rs, --features full for JIT); default bench profile, rustc version not stated; regex 1.13, fancy-regex 0.19, pcre2 crate 0.2 |
| **Adoption** | 27 stars, 1 fork; crates.io regexr 0.6.0, about 36k downloads (20.8k recent) |
| **Last commit** | 2026-09-28 |
| **Links** | [repository](https://github.com/ml-rust/regexr) · [benchmark](https://raw.githubusercontent.com/ml-rust/regexr/HEAD/README.md) |

## Verdict

First-party criterion runs (regex 1.13, pcre2 crate 0.2, fancy-regex 0.19; CPU, rustc and PCRE2 version not stated) report regexr-jit at 3.91-4.09x the regex crate on log parsing and 1.33-1.99x on HTML tag and URL extraction, with pcre2-jit faster on URLs and Unicode text; the log-parsing and Unicode rows compare ASCII regexr against Unicode regex, and the table dates from the 2025-12 initial commit.

## Use it when

- Rust tokenizer or pre-tokenizer code that runs GPT-style split patterns with lookaheads such as \s+(?!\S), where the regex crate refuses the pattern and fancy-regex has no JIT.
- You want PCRE-like features (lookaround, backreferences, \X grapheme clusters) with only a cargo dependency, including on wasm32 (interpreted engines only there).
- Hot capture-heavy patterns over ASCII data where you would otherwise write ASCII classes for the regex crate anyway; enable features = ["full"] and jit(true) and measure.
- You need backreference searches to stop under a step budget (backtrack_limit, try_find) rather than hang.

## Skip it when

- General-purpose matching: the README itself says to use the regex crate for 99% of uses, and the non-JIT engine is 0.80-0.87x of regex on log_parsing, url_extraction and html_tags in its own table.
- Code that relies on Unicode \w, \d or \b: regexr makes them ASCII-only unless you add (?u), unlike the regex crate, so the same pattern string silently matches less on non-ASCII text.
- Correctness-critical use where match semantics must equal the regex crate or PCRE2: every release from 0.2 to 0.6.0 (2026-09-28) fixed wrong-match bugs (DFA longest-instead-of-leftmost-first, JIT DFA giving up early, lazy-DFA cache flush dropping matches, lookbehind errors).
- Short-lived regexes matched a few times: JIT compile cost is not amortized (the docs say so), and patterns with large Unicode classes do better on the lazy DFA than the JIT.
- Possessive quantifiers, atomic groups or variable-width lookbehind are needed: they are rejected or only fixed-width is supported.

## How it is fast

Picks one of several engines per pattern: bit-parallel Shift-Or for small NFAs (64 states or fewer), lazy and eager DFAs, a PikeVM, a tagged NFA and a one-pass capture engine for captures, and a budgeted backtracker for backreferences. With the jit feature, the DFA, Shift-Or, tagged NFA, one-pass and backtracking engines are emitted as native code through dynasm. Literal prefilters (memchr, a custom AVX2 Teddy for 2-8 literals, aho-corasick for larger sets, NEON on AArch64 since 0.3.2) skip to candidate positions, and optimize_prefixes merges large literal alternations into a trie.

## Compared with alternatives

Pick regexr when you are in Rust, need lookarounds or backreferences in a tokenizer pattern and cannot link PCRE2; for plain throughput on Rust the regex crate stays the default, and for large multi-pattern rule sets Hyperscan, or for RE2-semantics engines rejit and re2jit, are the better-measured choices.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | memchr 2.8, aho-corasick 1.1; optional dynasm and dynasmrt 5.1 for the jit feature (no C library) |
| **Minimum toolchain** | Rust 1.83 (rust-version in Cargo.toml), edition 2021 |
| **Platforms** | any Rust target for the interpreted engines including wasm32-unknown-unknown; JIT on x86-64 (Linux, macOS, Windows) and AArch64 (Linux, macOS); AVX2 prefilters on x86-64, NEON literal prefilter on AArch64 |
| **Thread safety** | Regex is shareable across threads: lazy state sits behind RwLock (docs/architecture.md), and 0.5.0 stopped concurrent searches on one Regex from serializing on a shared lazy DFA. |
| **Drop-in for the baseline** | partial: method names and Match/Captures types follow the regex crate, but \w, \d and \b default to ASCII, backtracking for backreferences is budgeted, possessive and atomic groups are rejected, and the crate is a different type, so it is a code change, not a Cargo swap |

## Gotchas

- Harness flaw behind the headline: benches/competitors.rs passes the same pattern string to every engine, but regexr (and the pcre2 crate without UTF/UCP) treat \d, \w and \b as ASCII while the regex crate treats them as Unicode (\w is about 140,000 codepoints; the regex docs recommend (?-u:\w) when ASCII suffices). The 3.91-4.09x log_parsing row ((\d{4}-\d{2}-\d{2}) ... \[(\w+)\] (.+)) therefore compares ASCII regexr against Unicode regex, and on unicode_letters regexr's \w+ skips the Cyrillic, CJK, Arabic, Hebrew and Greek words the regex crate matches, so the engines produce different results. The harness never checks that match counts agree.
- The README table has not changed since the initial commit (2025-12-01): the alternation row was timed on log data that, by the current test_data.rs's own comment, contained no lowercase error/warning/critical/fatal at all (a rejection scan, not a search), and all rows predate the 0.1.x to 0.6.0 correctness fixes, several of which moved patterns to different engines.
- Results are not committed (benches/results is gitignored) and no CPU, rustc or PCRE2 version is given; criterion runs use sample_size 10, 1 s measurement and inputs of only 1 KB to 100 KB.
- docs/features.md lists \w as [a-zA-Z0-9_] in one section and shows \w+ matching 'café' as 'Unicode word characters' in another; the source (src/hir/builder.rs) gates Unicode \w, \d and \b on (?u).

## Known shortcomings

- Fair criterion harness (benches/competitors.rs) but results are gitignored with no hardware or rustc version; loses to PCRE2 JIT on url_extraction and unicode_letters, and the non-JIT path runs at 0.80-0.87x of the regex crate. Rust; moved to regex-engines where its baselines (regex crate, PCRE2 JIT) are listed.
- Enricher: regexr defaults \d, \w and \b to ASCII (src/hir/builder.rs, Flags.unicode=false since the initial commit) while the regex crate defaults them to Unicode, and benches/competitors.rs passes the same pattern to every engine, so the headline log_parsing 3.91-4.09x is ASCII regexr against Unicode regex and on unicode_letters regexr's \w+ (like pcre2 without UTF/UCP) skips Cyrillic, CJK, Arabic, Hebrew and Greek words that regex matches; the harness never cross-checks match counts. The README table is unchanged since the 2025-12-01 initial commit, the alternation row was timed on log data with zero lowercase matches (a rejection scan, per the test_data.rs comment), and all rows predate wrong-match fixes in 0.1.x-0.6.0 (DFA leftmost-first, JIT DFA early give-up, lazy-DFA cache flush dropping matches). Valid same-semantics rows: url_extraction 1.95-1.99x, html_tags 1.33-1.43x, email about 1.0x.

## Caveats and trade-offs

Benchmark code is public (benches/competitors.rs, run_benchmarks.sh prints CPU and rustc but the results are gitignored), yet the README states no hardware or toolchain and the table is undated. The JIT loses to PCRE2 JIT on url_extraction and unicode_letters and ties regex on email_validation and alternation; the non-JIT engine is slower than regex on several patterns, and the README itself recommends the regex crate for 99% of uses. Better filed under regex-engines (wave 3), whose baselines are PCRE2 and Rust regex; it is a regex JIT, not a language JIT, and none of the jits baselines (PyPy, LuaJIT, V8, HotSpot) apply. [retier] regexr defaults \d, \w and \b to ASCII (Flags.unicode=false) while the regex crate defaults to Unicode and the harness passes one pattern to every engine without cross-checking match counts, so the headline and unicode rows are not like for like. The README table is unchanged since the 2025-12-01 initial commit, the alternation row timed a rejection scan, and all rows predate wrong-match fixes in 0.1.x-0.6.0 (DFA leftmost-first, JIT DFA early give-up, lazy-DFA cache flush). Rust; filed under regex-engines.

Adds lookarounds, backreferences and JIT without a C dependency; the non-JIT engine only matches regex crate speed; JIT is disabled on WASM; no C API mentioned; built for LLM tokenizer patterns.

## Maintenance

Actively maintained (0.6.0 released 2026-09-28, about 36k crates.io downloads, MIT OR Apache-2.0), but the match engine is still settling: each recent release fixes wrong-match bugs, and the only published speed numbers are an undated pre-0.1 table with a semantic mismatch on its headline row.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** README speedup table versus the regex crate and PCRE2 JIT comes from public criterion code (benches/competitors.rs, same captures work per engine), but results are not committed (benches/results is gitignored) and no CPU model or rustc version is stated, so not A; first-party, so C.
- **Verifier notes:** Numbers match the README; fair same-work criterion harness but no hardware/toolchain and no committed results, so C. Suggest category override to regex-engines (there Rust regex and PCRE2 are listed baselines, making baseline_in_list true). Not a duplicate of any listed project. Shortcomings: loses to PCRE2 JIT on 2 of 7 rows, non-JIT slower than regex, no hardware stated.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`, `stars_or_usage`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/ml-rust/regexr/HEAD/README.md>
  - <https://github.com/ml-rust/regexr>
  - <https://github.com/ml-rust/regexr/commits>
  - <https://github.com/ml-rust/regexr/tree/main/benches>
  - <https://github.com/ml-rust/regexr/tree/main/scripts>
  - <https://raw.githubusercontent.com/ml-rust/regexr/HEAD/benches/competitors.rs>
  - <https://raw.githubusercontent.com/ml-rust/regexr/HEAD/benches/README.md>
  - <https://raw.githubusercontent.com/ml-rust/regexr/HEAD/benches/SUMMARY.md>
  - <https://raw.githubusercontent.com/ml-rust/regexr/HEAD/benches/run_benchmarks.sh>
  - <https://raw.githubusercontent.com/ml-rust/regexr/HEAD/benches/.gitignore>
  - <https://raw.githubusercontent.com/ml-rust/regexr/HEAD/Cargo.toml>
  - <https://crates.io/api/v1/crates/regexr>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/ml-rust/regexr/HEAD/README.md>
  - <https://raw.githubusercontent.com/ml-rust/regexr/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/ml-rust/regexr/HEAD/benches/competitors.rs>
  - <https://raw.githubusercontent.com/ml-rust/regexr/HEAD/benches/README.md>
  - <https://raw.githubusercontent.com/ml-rust/regexr/HEAD/benches/SUMMARY.md>
  - <https://raw.githubusercontent.com/ml-rust/regexr/HEAD/benches/run_benchmarks.sh>
  - <https://raw.githubusercontent.com/ml-rust/regexr/HEAD/benches/.gitignore>
  - <https://raw.githubusercontent.com/ml-rust/regexr/HEAD/benches/utils/test_data.rs>
  - <https://raw.githubusercontent.com/ml-rust/regexr/HEAD/benches/utils/mod.rs>
  - <https://raw.githubusercontent.com/ml-rust/regexr/HEAD/docs/features.md>
  - <https://raw.githubusercontent.com/ml-rust/regexr/HEAD/docs/architecture.md>
  - <https://raw.githubusercontent.com/ml-rust/regexr/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/ml-rust/regexr/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/ml-rust/regexr/HEAD/src/parser/mod.rs>
  - <https://raw.githubusercontent.com/ml-rust/regexr/HEAD/src/parser/ast.rs>
  - <https://raw.githubusercontent.com/ml-rust/regexr/HEAD/src/parser/atom.rs>
  - <https://raw.githubusercontent.com/ml-rust/regexr/HEAD/src/parser/state.rs>
  - <https://raw.githubusercontent.com/ml-rust/regexr/HEAD/src/parser/group.rs>
  - <https://raw.githubusercontent.com/ml-rust/regexr/HEAD/src/hir/mod.rs>
  - <https://raw.githubusercontent.com/ml-rust/regexr/HEAD/src/hir/builder.rs>
  - <https://github.com/ml-rust/regexr/tree/main/src/hir>
  - <https://github.com/ml-rust/regexr/commits/main/README.md>
  - <https://raw.githubusercontent.com/ml-rust/regexr/4df80e2/README.md>
  - <https://raw.githubusercontent.com/ml-rust/regexr/7bbdc28/README.md>
  - <https://raw.githubusercontent.com/ml-rust/regexr/8924231/README.md>
  - <https://raw.githubusercontent.com/ml-rust/regexr/4df80e2/benches/utils/test_data.rs>
  - <https://raw.githubusercontent.com/ml-rust/regexr/4df80e2/benches/competitors.rs>
  - <https://raw.githubusercontent.com/ml-rust/regexr/4df80e2/src/hir/builder.rs>
  - <https://raw.githubusercontent.com/ml-rust/regexr/4df80e2/src/parser/ast.rs>
  - <https://github.com/ml-rust/regexr/issues?q=is%3Aissue>
  - <https://github.com/ml-rust/regexr/issues/3>
  - <https://raw.githubusercontent.com/rust-lang/regex/master/src/lib.rs>
  - <https://crates.io/api/v1/crates/regexr>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/ml-rust/regexr`) · [data/wave12/enrich/raw/github_com_ml_rust_regexr.json](../../../data/wave12/enrich/raw/github_com_ml_rust_regexr.json) (enrichment confidence 0.7)

</details>
