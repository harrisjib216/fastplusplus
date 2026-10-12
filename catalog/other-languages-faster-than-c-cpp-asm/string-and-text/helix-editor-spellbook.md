# Spellbook (Rust Hunspell-format spellchecker, rewrite of Nuspell)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Strings and text](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MPL-2.0` · 🟢 active

> Rust rewrite of Nuspell that checks Hunspell-format dictionaries; 1.5-8x faster single-word check() than Nuspell and Hunspell on en_US.

| | |
|---|---|
| **Beats** | Hunspell and Nuspell (C++), single-word check() |
| **Claimed result** | check(): 'earth' 42.82 ns vs Hunspell 197.25 ns and Nuspell 125.89 ns; '8675,309.0' 14.14 ns vs 220.89 and 112.92 ns; 'light-weight-like' 779.06 ns vs 4,329.10 and 1,248.90 ns; 'unearthed' 264.98 ns vs 405.81 and 521.53 ns. Not faster on every row: compound word '20000th' 676.08 ns vs Nuspell 656.35 ns (Hunspell 3,204.10 ns). DHAT total allocation for one check: Spellbook 2,580,386 bytes in 44,741 blocks vs Nuspell 4,437,599 bytes in 50,419 blocks and Hunspell 3,325,493 bytes in 90,736 blocks. |
| **Workload** | Criterion median time to check one word against the stock en_US dictionary for ten word shapes (in-dictionary, number, prefix and suffix stripping, title and upper case, hyphen breaks, compound), plus a Valgrind DHAT heap total for checking one word. |
| **Metric** | latency |
| **Compiler and flags** | Spellbook: cargo bench with Criterion 0.8 (benches/check.rs). Hunspell and Nuspell: vendored C++ sources compiled by the cc crate in the-mikedavis/ffi-dictionaries build.rs with no explicit opt_level or flags, nightly Rust toolchain (rust-toolchain.toml), timed with libtest #[bench]. Under cargo bench the bench profile inherits release opt-level 3, which the cc crate passes as -O3, so both sides are probably optimised at level 3 without -march (inferred from Cargo and cc defaults; not stated). No compiler versions or CPU stated. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | not stated |
| **Why it wins** | Per the author: Spellbook uses hashbrown (SIMD group probing) with foldhash for the stem table where Nuspell rolls its own hash table with std::hash; Rust's standard library string search and equality are well optimised; small-string and small-slice optimisations cut memory. The author labels the string-search point a suspicion and does not profile it. |
| **Adoption** | 148 stars |
| **Last commit** | 2026-07-11 |
| **Links** | [repository](https://github.com/helix-editor/spellbook) · [benchmark](https://raw.githubusercontent.com/helix-editor/spellbook/HEAD/docs/compare.md) |

## Verdict

Author-run Criterion medians (June 2026 table) for single-word check() on the stock en_US dictionary: Spellbook 42.82 ns vs Nuspell 125.89 ns and Hunspell 197.25 ns for 'earth', 14.14 vs 112.92 and 220.89 ns for a number, 779 vs 1,249 and 4,329 ns for 'light-weight-like', and a tie with Nuspell on the compound '20000th' (676 vs 656 ns). The C++ libraries were vendored and built by the cc crate (probably -O3 under cargo bench) and called through a thin FFI shim; no CPU, compiler version or flags are stated, and the C++ columns came from a harness that is not published in its current form.

## Use it when

- Spell checking inside a Rust program (editor, LSP server, linter, CLI) with existing Hunspell dictionaries, where per-word check latency matters: tens to hundreds of ns per en_US word.
- Replacing a Hunspell or Nuspell FFI binding to drop the C++ toolchain and ICU dependency; the crate needs only hashbrown (plus foldhash by default) and works no_std with alloc.
- Memory-sensitive hosts: the author's DHAT run shows about 2.6 MB total allocated to load en_US and check one word vs 4.4 MB for Nuspell and 3.3 MB for Hunspell, with 947 live blocks at peak vs about 50,000-90,000.
- Dictionaries with large affix tables (fr_FR, de_DE) on 0.4.2 or later, where issue #15 reports fr check() at 46.82 ns vs Hunspell 268.84 ns and Nuspell 184.69 ns.

## Skip it when

- You need phonetic suggestions (Hunspell PHONE tables): not implemented, suggest() mirrors Nuspell.
- Dictionaries with complex compounding directives: the README says these 'may work less well', the project calls itself alpha, and a Dutch compound word panicked on a UTF-8 boundary until a March 2026 fix (issue #12).
- Compound-heavy checking where you already use Nuspell: the only compound row (en_US '20000th') is 676 ns vs Nuspell 656 ns, so no gain there.
- Suggestion-heavy workloads on versions before 0.4.2: issue #15 measured fr_FR suggestions at 1.47 s vs Hunspell 243 ms before the affix and ICONV fixes; suggest() speed is not in the published comparison.
- You need a stable API or a C/C++ interface: the README warns of breaking changes to any part of the API and MSRV.

## How it is fast

The stem table is a hash multimap (HashBag) built on hashbrown's HashTable (SwissTable-style SIMD group probing) with foldhash by default, where Nuspell rolls its own table hashed with std::hash. Stems and flag sets use 'German string' (Umbra) small-string and small-slice layouts with inline storage, flags are NonZeroU16 in sorted boxed slices searched by binary search, and affixes sit in a sorted table indexed by first character and binary-searched (Nuspell's trick). The author did not profile the C++ side; the string-search explanation is labelled a suspicion.

## Compared with alternatives

No other spellchecker is catalogued; the nearest siblings are Rust rewrites of C++ text tools (jieba-rs, Vibrato, Vaporetto), so pick Spellbook whenever the task is Hunspell-dictionary spell checking from Rust. Compared with ZSpell (in Spellbook's own doc, not catalogued), Spellbook supports compounds, numbers and suggestions and loads pt_BR in about 100 ms, where ZSpell's affix expansion gives near-constant 47-62 ns checks but 83 MB of allocations for en_US.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | hashbrown (&gt;=0.15, no default features); foldhash optional and on by default (default-hasher feature) |
| **Minimum toolchain** | Rust 1.70 (rust-version in Cargo.toml), edition 2021 |
| **Platforms** | any target with alloc (no_std, no platform-specific code documented) |
| **Thread safety** | check() and suggest() take &self and the benchmarks share one Dictionary through a static Lazy, so it is Sync for a Sync hasher; add() and remove_stem() need &mut self. Not otherwise documented. |
| **Drop-in for the baseline** | partial — reads the same Hunspell .aff/.dic files and aims for Nuspell-identical results, but it is a Rust API (dictionary passed as strings, not paths); C/C++ users would need their own FFI. |

## Gotchas

- Harness flaw: the published C++ harness does not match the published numbers. the-mikedavis/ffi-dictionaries (last commit 2026-04-14) still times Hunspell and Nuspell with nightly libtest #[bench] and uses 'earthly' for word_with_suffix, yet the June 2026 compare.md (commit 09013cf, 'bench: Migrate to criterion') labels every column a Criterion median for 'earthed', and the C++ word_with_suffix figures rose from 236.94/141.47 ns (the Nov 2024 'earthly' table) to 353.01/273.76 ns. The C++ columns therefore came from an unpublished local harness and cannot be reproduced from public code; issue #15's fr_FR C++ figures likewise have no published bench.
- The Nov 2024 version of the table had the Nuspell and Spellbook uppercase ('EARTH') and word_with_prefix ('unearth') values apparently swapped (Nuspell 280.78 ns uppercase and 924.66 ns prefix, now 882.94 and 283.38 ns); copies quoted from that version are wrong.
- The DHAT totals are for a whole example binary that loads en_US and checks 'hello', so they compare dictionary-load memory, not per-check allocation.
- Uses unsafe for the Umbra string/slice layouts, in-place UTF-8 byte edits (sharp-s handling, suggestion swaps) and unchecked indexing in the ngram suggester; words over 360 bytes (MAX_WORD_LEN) are rejected without checking, as in Nuspell.

## Known shortcomings

- The word_with_suffix row times 'earthly' in the C++ benches but 'earthed' in Spellbook; different harnesses (Criterion vs libtest); the compound row is not faster than Nuspell; C++ -O3 only inferred from cc crate defaults; the win comes from hashbrown/foldhash data structures, not Rust codegen.
- Harness flaw: the published C++ harness is not the one behind the published numbers. the-mikedavis/ffi-dictionaries (last commit 2026-04-14) still times Hunspell and Nuspell with nightly libtest #[bench] on 'earthly', while compare.md of 2026-06-07 (09013cf) labels every column a Criterion median for 'earthed' and the C++ word_with_suffix row rose from 236.94/141.47 ns to 353.01/273.76 ns, so the C++ columns came from an unpublished local harness and are not reproducible. The November 2024 table had the Nuspell and Spellbook EARTH and unearth rows swapped. DHAT totals are dictionary load plus one check, not per check. The compound word '20000th' ties Nuspell; pre-0.4.2 fr_FR suggest took 1.47 s against Hunspell's 243 ms (issue #15).

## Caveats and trade-offs

First-party numbers, CPU and compiler versions not stated, so tier C. The two sides use different harnesses (Criterion median vs nightly libtest #[bench]); the C++ side is called through an FFI shim (Nuspell_spell/Hunspell_spell taking a const char\*) with c"word" literals, a small per-call cost. The word_with_suffix row is not apples to apples: the table labels it 'earthed' for all three, but ffi-dictionaries benches/nuspell-check.rs and hunspell-check.rs time 'earthly' (a literal stem that short-circuits on lookup), while Spellbook's benches/check.rs times 'earthed' with a comment on that difference. Not faster on every row: compound_word '20000th' 676.08 ns vs Nuspell 656.35 ns. Spellbook is mainly a rewrite of Nuspell, so the gain is from data-structure choices (hashbrown and foldhash vs Nuspell's own hash table with std::hash, compact stem and flagset representation), not Rust codegen; the author labels the string-search explanation a suspicion and did not profile. The ffi-dictionaries harness is GPL-3.0 and has 1 star. Only en_US is in the comparison table (check.rs also benches fr_FR, without a C++ comparison). [retier] The published C++ harness (the-mikedavis/ffi-dictionaries, last commit 2026-04-14, libtest #[bench] on 'earthly') does not match the published numbers (compare.md 2026-06-07 labels every column a Criterion median for 'earthed'; the C++ word_with_suffix row rose from 236.94/141.47 ns to 353.01/273.76 ns), so the C++ columns came from an unpublished local harness. The November 2024 table had the Nuspell and Spellbook EARTH and unearth rows swapped; DHAT totals are dictionary load plus one check; '20000th' ties Nuspell; pre-0.4.2 fr_FR suggest 1.47 s vs Hunspell 243 ms (issue #15).

Only check() is benchmarked; the author says dictionary load and suggestion matter less and does not measure them. Hunspell-format dictionaries. Rust crate; the repo ships no benchmark of its own against Hunspell, the C++ numbers come from a separate FFI harness.

## Maintenance

Active (0.4.2 released 2026-06-03, last commit 2026-07-11, about 203k crates.io downloads), MPL-2.0 and self-described alpha with an unstable API; usable today for en_US-class dictionaries, while the C++ comparison is first-party and its current C++ harness is unpublished.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** docs/compare.md is first-party; benchmark code is public (benches/check.rs and the-mikedavis/ffi-dictionaries benches/\*-check.rs) but no CPU, compiler version or flags are stated, so C.
- **Verifier notes:** All claimed numbers (check() rows and DHAT totals) match docs/compare.md. Metadata confirmed: MPL-2.0, 148 stars, last commit 2026-07-11, active. Shortcomings: no CPU or compiler versions; word_with_suffix row mixes 'earthly' (C++ benches) with 'earthed' (Spellbook bench); different harnesses; compound row not faster than Nuspell; C++ -O3 only inferred from cc crate defaults.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-105 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/helix-editor/spellbook/HEAD/docs/compare.md>
  - <https://raw.githubusercontent.com/helix-editor/spellbook/HEAD/README.md>
  - <https://raw.githubusercontent.com/helix-editor/spellbook/HEAD/benches/check.rs>
  - <https://raw.githubusercontent.com/helix-editor/spellbook/HEAD/Cargo.toml>
  - <https://github.com/helix-editor/spellbook>
  - <https://github.com/helix-editor/spellbook/commits/master>
  - <https://github.com/the-mikedavis/ffi-dictionaries>
  - <https://github.com/the-mikedavis/ffi-dictionaries/tree/main/benches>
  - <https://raw.githubusercontent.com/the-mikedavis/ffi-dictionaries/HEAD/benches/nuspell-check.rs>
  - <https://raw.githubusercontent.com/the-mikedavis/ffi-dictionaries/HEAD/benches/hunspell-check.rs>
  - <https://raw.githubusercontent.com/the-mikedavis/ffi-dictionaries/HEAD/build.rs>
  - <https://raw.githubusercontent.com/the-mikedavis/ffi-dictionaries/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/the-mikedavis/ffi-dictionaries/HEAD/rust-toolchain.toml>
  - <https://raw.githubusercontent.com/the-mikedavis/ffi-dictionaries/HEAD/vendor/nuspell/src/interface.cxx>
  - <https://raw.githubusercontent.com/the-mikedavis/ffi-dictionaries/HEAD/src/lib.rs>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/helix-editor/spellbook/HEAD/README.md>
  - <https://raw.githubusercontent.com/helix-editor/spellbook/HEAD/docs/compare.md>
  - <https://raw.githubusercontent.com/helix-editor/spellbook/781c609/docs/compare.md>
  - <https://raw.githubusercontent.com/helix-editor/spellbook/HEAD/docs/internals.md>
  - <https://raw.githubusercontent.com/helix-editor/spellbook/HEAD/benches/check.rs>
  - <https://raw.githubusercontent.com/helix-editor/spellbook/c7f2d78/benches/check.rs>
  - <https://raw.githubusercontent.com/helix-editor/spellbook/247bc4d/benches/check.rs>
  - <https://raw.githubusercontent.com/helix-editor/spellbook/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/helix-editor/spellbook/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/helix-editor/spellbook/HEAD/src/checker.rs>
  - <https://raw.githubusercontent.com/helix-editor/spellbook/HEAD/src/aff.rs>
  - <https://raw.githubusercontent.com/helix-editor/spellbook/HEAD/src/hash_bag.rs>
  - <https://github.com/helix-editor/spellbook/commits/master/docs/compare.md>
  - <https://github.com/helix-editor/spellbook/commits/master/benches/check.rs>
  - <https://github.com/helix-editor/spellbook/commit/09013cf>
  - <https://github.com/helix-editor/spellbook/issues?q=is%3Aissue>
  - <https://github.com/helix-editor/spellbook/issues/15>
  - <https://github.com/helix-editor/spellbook/issues/12>
  - <https://crates.io/api/v1/crates/spellbook>
  - <https://raw.githubusercontent.com/the-mikedavis/ffi-dictionaries/HEAD/README.md>
  - <https://raw.githubusercontent.com/the-mikedavis/ffi-dictionaries/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/the-mikedavis/ffi-dictionaries/HEAD/build.rs>
  - <https://raw.githubusercontent.com/the-mikedavis/ffi-dictionaries/HEAD/rust-toolchain.toml>
  - <https://raw.githubusercontent.com/the-mikedavis/ffi-dictionaries/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/the-mikedavis/ffi-dictionaries/HEAD/benches/nuspell-check.rs>
  - <https://raw.githubusercontent.com/the-mikedavis/ffi-dictionaries/HEAD/benches/hunspell-check.rs>
  - <https://raw.githubusercontent.com/the-mikedavis/ffi-dictionaries/HEAD/vendor/nuspell/src/interface.cxx>
  - <https://raw.githubusercontent.com/the-mikedavis/ffi-dictionaries/HEAD/vendor/nuspell/src/dictionary.cxx>
  - <https://raw.githubusercontent.com/the-mikedavis/ffi-dictionaries/HEAD/vendor/hunspell/src/hunspell.cxx>
  - <https://github.com/the-mikedavis/ffi-dictionaries/commits/main>
  - <https://github.com/the-mikedavis/ffi-dictionaries/branches>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/helix-editor/spellbook`) · [data/wave14/enrich/raw/github_com_helix_editor_spellbook.json](../../../data/wave14/enrich/raw/github_com_helix_editor_spellbook.json) (enrichment confidence 0.75)

</details>
