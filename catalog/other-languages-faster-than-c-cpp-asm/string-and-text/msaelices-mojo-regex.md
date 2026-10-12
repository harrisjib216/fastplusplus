# mojo-regex (Mojo regular expression library)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Strings and text](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Mojo` · `MIT` · 🟢 active

> Pure-Mojo regex library with a re-like API and hybrid DFA/lazy-DFA/NFA engines; first-party micro-benchmarks claim wins over CPython re and Rust regex.

| | |
|---|---|
| **Beats** | CPython 3.12 re module (C implementation) and the Rust regex crate |
| **Claimed result** | Page (mojo-regex 0.13.0, comparison.md): Mojo vs Python re geomean 24.54x over 76 shared benchmarks (Mojo wins 74, Python 1); Mojo vs Rust regex geomean 3.47x over 71 rows as printed, but 13 of those rows use a different input, pattern or operation on the Rust side, and the matched-input geomean over the remaining 58 rows is 2.77x (derived from page data). CHANGELOG v0.20.0: the Mojo 1.0 build is about 13% slower than the published v0.13.0. |
| **Workload** | 80 regex micro-benchmarks (literals, alternations, phone-number DFA patterns, is_match, findall) with pre-compiled patterns, 500 ms target runtime per case, median timing. |
| **Metric** | latency |
| **Compiler and flags** | Mojo 0.26.2 stable, default optimisation (benchmarks run with mojo run); CPython 3.12 re (build flags of the interpreter not stated); Rust regex 1.10 with Cargo profile.release opt-level 3, lto = true, codegen-units = 1, RUSTFLAGS -C target-cpu=native (benchmarks/rust/Cargo.toml, run_comparison_with_rust.sh). rustc version not stated. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Why it wins** | Hybrid DFA, NFA, PikeVM and lazy-DFA engine chosen per pattern; an optional compile-time API builds the DFA in Mojo's comptime interpreter so matching needs no runtime compilation, pattern hashing or cache lookup (README). |
| **Adoption** | 18 stars |
| **Last commit** | 2026-09-01 |
| **Links** | [repository](https://github.com/msaelices/mojo-regex) · [benchmark](https://raw.githubusercontent.com/msaelices/mojo-regex/HEAD/benchmarks/results/comparison.md) |

## Verdict

The claim comes from the first-party comparison.md: mojo-regex 0.13.0 on Mojo 0.26.2 (default optimisation) against CPython 3.12 re and Rust regex 1.10 (opt-level 3, LTO, codegen-units 1, target-cpu=native), with pre-compiled patterns and median timing over 500 ms, on an unnamed CPU. It reports geomeans of 24.54x vs re over 76 rows and 3.47x vs Rust over 71 rows. Dropping rows where the harnesses do different work leaves about 14.7x vs re (70 rows) and about 2.8x vs Rust (58 rows), both derived from page data.

## Use it when

- Mojo code that needs regular expressions and whose patterns fit the supported subset: ASCII classes, \d, \w, \s, bounded quantifiers, alternation, groups and anchors.
- Extraction and validation loops over ASCII text, such as phone numbers, dates, serial IDs and emails. On the matched-input rows, findall was about 5-60x faster than CPython re and about 1.1-8x faster than Rust regex.
- Short inputs where per-call overhead dominates, such as validating single fields. The comptime API measured 36 vs 53 ns per call against the runtime API on a short literal search.
- Porting Python re code to Mojo, since the function names and sub() group syntax are close to re's.

## Skip it when

- Patterns that need case-insensitivity, non-greedy quantifiers, \b, lookaround, named groups, Unicode classes, multiline or dot-all modes, or the negated shorthands \S, \D and \W.
- Untrusted patterns or inputs: complex patterns fall back to a backtracking NFA, and ReDoS protection is still an open issue (#31).
- Multi-threaded programs: the compiled-regex cache and the one-slot sub() cache are process-global with no locking, and the source warns that concurrent sub() calls can apply the wrong template.
- Production code that needs stability. The project is a 0.x release with several wrong-match bugs fixed in 2026 (#114, #120, #39 state corruption, DFA parser bugs that 'silently returned zero matches' before v0.8.0), an open double-free at process exit (#97) and constant churn from Mojo toolchain upgrades.
- Throughput-critical use of the current release. CHANGELOG v0.20.0 reports the Mojo 1.0 build as about 13% slower by geomean than v0.13.0, the version behind the published table, and advises staying on v0.13.0 / Mojo 0.26.x for performance.

## How it is fast

HybridMatcher classifies each pattern at compile time and routes it to one engine. Simple patterns go to a DFA with SIMD character-class matchers (nibble lookup tables, vectorised range checks) and a two-byte memchr-style literal scan. Large or nested alternations go to a lazy DFA built from a PikeVM program, with a SIMD first-byte prefilter. \$-anchored patterns use a OnePass NFA, and everything else uses a backtracking NFA with two-way literal prefiltering. Leading or trailing `.*` gets an rfind or two-way shortcut, guarded by a no-newline check. findall on patterns with a rare required byte (the `@` in an email, the `-` in a phone number) memchr-scans for that byte and backs up to a candidate start. Compiled patterns are cached in a process-global dict keyed by pattern hash, and the comptime API removes that hash and probe as well (about 17 ns per call, CHANGELOG).

## Compared with alternatives

Use mojo-regex only from Mojo code whose patterns fit its subset. Elsewhere, the Rust regex sibling is the engine it is measured against: on rows with matched inputs it trails mojo-regex by about 2.8x geomean on these micro-benchmarks, but it is faster per byte on the long literal-scan rows and has the full syntax. Ferroni is the choice when Oniguruma syntax compatibility matters.

## Integration

| | |
|---|---|
| **Form** | module (Mojo package installed with pixi from the conda channel) |
| **Dependencies** | none beyond the Mojo standard library (pyyaml only for the optional mojopkg build feature) |
| **Minimum toolchain** | Mojo ==1.0.0 exactly (pinned in pixi.toml for v0.21.0). The published benchmarks used v0.13.0 on Mojo 0.26.2. |
| **Platforms** | linux-64 and osx-arm64 (pixi.toml) |
| **Thread safety** | Not thread-safe. The global pattern cache and the sub() identity cache are process-global with no locking (matcher.mojo comment: 'concurrent sub() calls from different threads can race and produce a torn state'). |
| **Drop-in for the baseline** | partial — the function names follow Python re (match_first for re.match, search, findall, sub, split), but it is a Mojo API with a smaller syntax, no flags and ASCII-only classes, and it does not replace re inside Python |

## Gotchas

- Harness flaw in the Rust column (new finding): in 13 of the 71 Mojo-vs-Rust rows, benchmarks/rust/src/bench_engine.rs and lib.rs time a different input, pattern or operation from the Mojo harness. (1) literal_match_short and literal_match_long put 'hello' 10x deeper in Rust's text (offsets 10,001 and 100,001 vs 1,000 and 10,000), so Rust scans 10x more bytes; per byte, Rust is about 2.5x and 1.4x faster (derived), not 4.1x and 7.3x slower. (2) range_lowercase, range_digits and predefined_digits run on Rust's 'abc123XYZ' text, where the match is 3 bytes at offset 0 or 3, against Mojo's 10,000-letter text, so Rust's 3.1-3.8x 'wins' are artifacts too. (3) group_alternation times (a|b)\* in Rust vs (a|b) in Mojo, match_all_simple times 'a' on alphabet text vs 'hello' on medium_text, and literal_prefix_short times hello.\*world vs hello.\*. (4) literal_prefix_long, required_literal_short, no_literal_baseline and alternation_common_prefix give Rust texts 10-50x shorter (SHORT_TEXT x10 vs x100, x100 vs x1000, EMAIL_TEXT x1 vs x50), and the last two time find_iter().collect() against Mojo's single anchored match_first. (5) wildcard_match_any is the '.\*' shortcut below. On the 58 rows whose inputs and operations match, the Mojo-vs-Rust geomean is about 2.77x (Mojo faster on 49, Rust on 8; derived from page data), not 3.47x.
- Correctness bug behind the wildcard_match_any row: HybridMatcher special-cases a pattern that is exactly '.\*' (matcher.mojo _is_wildcard_match_any). match_first, match_next and match_all then return one Match covering the rest of the text without running a regex or checking for newlines, and is_match returns true. On text containing '\n', results therefore differ from re, where '.' stops at a newline. The bench text has no newline, so the 5,454x (Python) and 45,718x (Rust) ratios time a constant return. The leading and trailing '.\*' fast paths in nfa.mojo do check text.find("\n") == -1.
- Python-column caveats: the five is_match rows time Mojo's short-circuit bool against bool(re.match(...)), which runs the full greedy match over about 10,000 characters (7,434-18,013x). Python's nanosecond rows sit on a CPython call-overhead floor of roughly 120-160 ns (alternation_simple 123.9 ns, anchor_start 129.9 ns). Mojo samples are at least 10 ms against 1 ms for Python and Rust, and the Mojo harness has no black_box. Without the is_match and wildcard rows, the geomean vs re is about 14.7x over 70 rows (derived).
- Stale and noisy numbers: comparison.md was last refreshed on 2026-05-01 for v0.13.0 on Mojo 0.26.2 and names no CPU. The v0.13.0 changelog says that run's Rust numbers came from 'a fresher Rust toolchain (\~1.5x faster than the v0.12.0 measurement)', so the baseline moved between runs. The README's 'beats Rust on 61%' does not match comparison.md (59 of 71 rows, 83%).

## Known shortcomings

- Extreme rows are not the same work: the is_match rows short-circuit a bool against Python's full greedy re.match, wildcard_match_any hits a '.\*' string special case in src/regex/matcher.mojo that returns the whole text without running a regex, and no_literal_baseline and alternation_common_prefix time a single Mojo match against Rust find_iter; without those rows about 14.7x vs Python and 2.6x vs Rust (derived); Python timings include interpreter call overhead; no hardware stated.
- Harness flaw: the Rust harness (bench_engine.rs, lib.rs) uses a different input, pattern or operation from Mojo on 13 of 71 rows: literal_match_short/long bury 'hello' 10x deeper for Rust (Rust about 2.5x/1.4x faster per byte); range_lowercase, range_digits and predefined_digits match 3 bytes at offset 0-3 on Rust's text, so Rust's 3 wins are artefacts; group_alternation uses (a|b)\* vs (a|b); match_all_simple 'a' vs 'hello'; texts 10-50x shorter on 4 more rows. The matched-input geomean against Rust is 2.77x over 58 rows, not 3.47x (derived). The '.\*' shortcut returns the whole text across newlines (correctness bug). CHANGELOG v0.20.0: the Mojo 1.0 build is about 13% slower than the published v0.13.0.

## Caveats and trade-offs

First-party, hardware not stated, so tier C. Several extreme rows compare different work: (1) the five is_match_\* rows time Mojo's bool-only is_match, which can stop after the first matching character, against Python's bool(pattern.match(text)), which runs the full greedy match over a 10,000-character input (7,434x to 18,013x); (2) wildcard_match_any hits a pattern-string special case in src/regex/matcher.mojo (_is_wildcard_match_any: pattern == ".\*" returns Match(0, start, len(text)) without scanning), so no regex runs; that shortcut also ignores newlines, which '.' should not match, and is only correct here because the test text has none (stb-zip/Pipa-style row, 5,454x vs Python and 45,718x vs Rust); (3) no_literal_baseline and alternation_common_prefix time Mojo match_first (one anchored match) against Rust find_iter().collect() over the whole 6,000-character text (844.7x and 177.9x). The Mojo harness has no black_box equivalent, so sub-2 ns rows are at loop-overhead level and may be partly hoisted (not confirmable without running). The Python column includes CPython interpreter call overhead (roughly 100+ ns per call), which dominates nanosecond rows, so it is not a clean measurement of the C sre engine; Rust regex is not a C/C++ baseline. The compile-time (comptime) API is not used in the comparison table. comparison.md was produced with Mojo 0.26.2 while the code now targets Mojo 1.0.0. Missing features (case-insensitive, non-greedy, word boundaries, lookaround, named groups) mean the engine supports a smaller regex language than re or Rust regex. Rows missing from one side are blank. [retier] The Rust harness (bench_engine.rs, lib.rs) uses a different input, pattern or operation from Mojo on 13 of 71 rows: literal_match_short/long bury 'hello' 10x deeper for Rust (Rust about 2.5x/1.4x faster per byte); range_lowercase, range_digits and predefined_digits match 3 bytes at offset 0-3 on Rust's text, so Rust's 3 wins are artefacts; group_alternation uses (a|b)\* vs (a|b); match_all_simple 'a' vs 'hello'; texts 10-50x shorter on 4 more rows. The '.\*' shortcut returns the whole text across newlines (correctness bug).

Missing features: named groups, case-insensitive matching, non-greedy quantifiers, word boundaries, Unicode character classes, multiline and dot-all modes, lookaround and negated shorthand classes (\S, \D, \W). Invalid patterns can fail the build when used with the compile-time API.

## Maintenance

Active single-maintainer 0.x project (v0.21.0, last commit 2026-09-01, MIT, 18 stars) that tracks Mojo releases closely. It is copyable, but it is pinned to Mojo ==1.0.0, ships only for linux-64 and osx-arm64, and its own changelog says the current Mojo 1.0 build is about 13% slower than the build behind the published numbers.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification C, tier now C.
- **Tier reason:** First-party comparison.md with public harnesses (benchmarks/bench_engine.mojo, benchmarks/python/bench_engine.py, benchmarks/rust/src/bench_engine.rs) and tool versions, but no CPU or hardware is named, so not A; tier stays C. The headline geomean is overstated by rows where the three harnesses do different work.
- **Verifier notes:** Numbers on comparison.md match the record exactly and the geomeans reproduce (24.54x, 3.47x). Main shortcomings: is_match rows compare short-circuit bool against Python's full greedy re.match; wildcard_match_any is a '.\*' string special case that returns the whole text without running a regex and is wrong for text containing newlines; two Rust rows time findall against Mojo's single match; Python timings include interpreter overhead; no hardware. Derived geomean without those rows is about 14.7x vs Python and 2.6x vs Rust.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-105 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/msaelices/mojo-regex/HEAD/benchmarks/results/comparison.md>
  - <https://raw.githubusercontent.com/msaelices/mojo-regex/HEAD/README.md>
  - <https://github.com/msaelices/mojo-regex>
  - <https://github.com/msaelices/mojo-regex/tree/main/benchmarks>
  - <https://github.com/msaelices/mojo-regex/tree/main/benchmarks/python>
  - <https://github.com/msaelices/mojo-regex/tree/main/benchmarks/rust>
  - <https://github.com/msaelices/mojo-regex/tree/main/src/regex>
  - <https://github.com/msaelices/mojo-regex/commits/main>
  - <https://raw.githubusercontent.com/msaelices/mojo-regex/HEAD/benchmarks/bench_engine.mojo>
  - <https://raw.githubusercontent.com/msaelices/mojo-regex/HEAD/benchmarks/README.md>
  - <https://raw.githubusercontent.com/msaelices/mojo-regex/HEAD/benchmarks/BENCHMARKING_GUIDE.md>
  - <https://raw.githubusercontent.com/msaelices/mojo-regex/HEAD/benchmarks/run_comparison_with_rust.sh>
  - <https://raw.githubusercontent.com/msaelices/mojo-regex/HEAD/benchmarks/run_comparison_with_python.sh>
  - <https://raw.githubusercontent.com/msaelices/mojo-regex/HEAD/benchmarks/python/bench_engine.py>
  - <https://raw.githubusercontent.com/msaelices/mojo-regex/HEAD/benchmarks/rust/Cargo.toml>
  - <https://raw.githubusercontent.com/msaelices/mojo-regex/HEAD/benchmarks/rust/src/bench_engine.rs>
  - <https://raw.githubusercontent.com/msaelices/mojo-regex/HEAD/src/regex/matcher.mojo>
- **Sources the enricher read:**
  - <https://github.com/msaelices/mojo-regex/commits/main>
  - <https://github.com/msaelices/mojo-regex/commits/main/benchmarks/results/comparison.md>
  - <https://github.com/msaelices/mojo-regex/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/msaelices/mojo-regex/HEAD/README.md>
  - <https://raw.githubusercontent.com/msaelices/mojo-regex/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/msaelices/mojo-regex/HEAD/CONTRIBUTING.md>
  - <https://raw.githubusercontent.com/msaelices/mojo-regex/HEAD/pixi.toml>
  - <https://raw.githubusercontent.com/msaelices/mojo-regex/HEAD/benchmarks/README.md>
  - <https://raw.githubusercontent.com/msaelices/mojo-regex/HEAD/benchmarks/results/comparison.md>
  - <https://raw.githubusercontent.com/msaelices/mojo-regex/HEAD/benchmarks/bench_engine.mojo>
  - <https://raw.githubusercontent.com/msaelices/mojo-regex/HEAD/benchmarks/python/bench_engine.py>
  - <https://raw.githubusercontent.com/msaelices/mojo-regex/HEAD/benchmarks/rust/src/bench_engine.rs>
  - <https://raw.githubusercontent.com/msaelices/mojo-regex/HEAD/benchmarks/rust/src/lib.rs>
  - <https://raw.githubusercontent.com/msaelices/mojo-regex/HEAD/benchmarks/rust/Cargo.toml>
  - <https://raw.githubusercontent.com/msaelices/mojo-regex/HEAD/benchmarks/run_comparison_with_rust.sh>
  - <https://raw.githubusercontent.com/msaelices/mojo-regex/HEAD/benchmarks/run_comparison_with_python.sh>
  - <https://raw.githubusercontent.com/msaelices/mojo-regex/HEAD/src/regex/matcher.mojo>
  - <https://raw.githubusercontent.com/msaelices/mojo-regex/HEAD/src/regex/nfa.mojo>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/msaelices/mojo-regex`) · [data/wave14/enrich/raw/github_com_msaelices_mojo_regex.json](../../../data/wave14/enrich/raw/github_com_msaelices_mojo_regex.json) (enrichment confidence 0.8)

</details>
