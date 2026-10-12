# zspell

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Strings and text](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0` · 🟡 stale

> Pure-Rust Hunspell-format spellchecker that pre-expands affixes for near-constant 47-63 ns word checks, about 4-27x faster than Hunspell on en_US.

| | |
|---|---|
| **Beats** | Hunspell and Nuspell (C++) through the-mikedavis/ffi-dictionaries |
| **Claimed result** | helix-editor/spellbook docs/compare.md (2024-11-13 table at ca13e83): check_word 'earth' zspell 46.86 ns vs Hunspell 212.30 ns and Nuspell 126.97 ns; 'EARTH' 52.63 ns vs Hunspell 1,426.46 ns; about 4.5-27x faster than Hunspell (derived from page data) |
| **Workload** | No Hunspell or Nuspell comparison found. The README says that, with compiled word lists held in memory (about 20 MiB), zspell 'tends to outperform other spellcheckers'. The repo's benches/ directory holds Criterion microbenchmarks of internal choices (Vec, BTreeSet, std HashSet, hashbrown HashSet for word lookup; slice contains vs binary_search; parser tests) from 2022-2023. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 5900X (recorded in benches/results/v0.4.1-16-g72dc016_2023-10-30_0539.bench for the internal microbenchmarks) |
| **Compiler and flags** | Criterion 0.5 via cargo bench --features unstable-bench; the 2023-10-30 result file records rustc 1.75.0-nightly (e5cfc5547 2023-10-28). |
| **Kind** | library or program |
| **Same algorithm as the baseline** | not stated |
| **Same optimization level** | not stated |
| **Why it wins** | README: optimized for the common case that most checked words are correct, with whole compiled word lists held in memory (about 20 MiB); no measurement backs it. |
| **Adoption** | 63 stars, 4 forks; crate zspell 0.5.5 (139,500 crates.io downloads); no GitHub releases |
| **Last commit** | 2024-07-09 |
| **Links** | [repository](https://github.com/pluots/zspell) · [benchmark](https://github.com/pluots/zspell) |

## Verdict

Independent numbers exist that the record missed: Spellbook's docs/compare.md (helix-editor/spellbook, written by Spellbook's author on 2024-11-13) times zspell check_word on the stock en_US dictionary at 46.86 ns ('earth'), 50.51 ns ('Earth'), 52.63 ns ('EARTH'), 54.52 ns ('unearth'), 61.13 ns ('unearthed') and 62.47 ns ('reearth', misspelled), against Hunspell at 212.30, 827.88, 1,426.46, 288.74, 448.48 and 1,175.15 ns and Nuspell at 126.97, 513.78, 280.78, 924.66, 534.85 and 520.51 ns in the same-format libtest table (Hunspell and Nuspell called through Rust FFI from the-mikedavis/ffi-dictionaries), so about 4.5x to 27x faster than Hunspell (derived from page data); hardware, compiler and zspell version are not stated, the zspell benchmark code was not found in that repository, and zspell fails the compound and number cases.

## Use it when

- Checking large volumes of mostly correct text against a simple dictionary such as en_US, where per-word latency matters and tens of MB of RAM are acceptable.
- Rust or Python programs that want a no-unsafe, no-C-dependency checker for Hunspell-format dictionaries without linking libhunspell.
- Stemming and morphological lookups (entry API returning stems and morph info) on dictionaries whose affix rules zspell expands correctly.
- Long-running processes that build the dictionary once and amortize the expansion cost over many checks.

## Skip it when

- Morphologically rich dictionaries: the Spellbook author reports pt_BR (312,000 stems, 47 prefixes, 57 suffixes) ran over six minutes and past 100 GB of memory before being killed, versus about 100 ms for Spellbook.
- When you need suggestions, compound words (COMPOUNDRULE, e.g. en_US '20000th') or numbers ('8675,309.0'); these are missing or unstable.
- Memory-constrained or short-lived processes: en_US peaks at about 57 MB of heap against about 3.2 MB for Hunspell and 4.2 MB for Nuspell (DHAT, Spellbook compare doc).
- Languages with stacked suffixes such as French: open issue #116 reports 'répondez' and 'projections' wrongly rejected because multiple suffix stripping does not work.
- Projects that need an active upstream: no commits since 2024-07-09 (dependency bumps; last release 0.5.5 on 2024-06-13).

## How it is fast

At build time it applies every prefix and suffix rule to every stem and stores all resulting surface forms in hashbrown hash maps (main, nosuggest and forbidden word lists), so a check is a few hash lookups of the word and its lowercase form instead of Hunspell's runtime affix stripping and flag checks. The README frames this as optimizing for the common case that most words are correct and that a compiled word list fits in memory (about 20 MiB by its estimate). The library is #![forbid(unsafe_code)].

## Compared with alternatives

Pick Spellbook (also Rust, measured against Hunspell and Nuspell, with suggestions, compounds and about 2 MB peak heap) by default; pick zspell only when you check en_US-like dictionaries in bulk, want the stem and morph entry API, CLI or Python bindings, and can spend tens of MB for its flat 47-63 ns checks (faster than Spellbook's 2024 figures of 66-540 ns on the same words).

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | cfg-if, dirs, hashbrown, itertools, lazy_static, regex, stringmetrics, sys-locale, unicode-segmentation, visibility, xxhash-rust |
| **Minimum toolchain** | Rust 1.65 for the library (README MSRV); the CLI and test runner track newer Rust |
| **Platforms** | any Rust target (pure safe Rust); prebuilt CLI binaries and Python wheels for common platforms |
| **Thread safety** | Not documented; the check methods take &self and dict.rs has no RefCell or Mutex, so a built Dictionary should be shareable across threads |
| **Drop-in for the baseline** | partial — reads the same .aff/.dic files as Hunspell, but has a Rust API, no Hunspell C/C++ API, no compounds and no stable suggestions |

## Gotchas

- Speed is bought with eager affix expansion: build time and memory scale with stems times applicable affixes, which is fine for en_US (about 57 MB peak) and unusable for pt_BR (over 100 GB before being killed, per Spellbook's compare doc).
- check_word allocates a lowercase String on every call and only tries the word as given and its full lowercase form; it does not implement Hunspell's capitalization rules beyond that (for example all-caps forms of mixed-case entries are not mapped back to title case).
- The current Spellbook compare doc mixes runs: its Hunspell, Nuspell and Spellbook table was re-measured with Criterion on 2026-06-07 (commit 09013cf), while the ZSpell table is the 2024-11-13 libtest ns/iter run, and the current table's word_with_suffix row uses 'earthed' where the ZSpell row uses 'earthly'. Compare ZSpell only against the 2024 table (commit ca13e83 or 781c609).
- zspell's own benches/findings.md times internal collection choices only, and its Vec row is internally inconsistent (a miss, which must scan the whole list, is listed at 1.91 us against 594 us for a hit), so it says nothing about speed against Hunspell.

## Known shortcomings

- 'Tends to outperform' has no numbers and no named baseline; the benches only time internal hash sets. 63 stars, stale since 2024-07-09.
- Enricher: independent numbers exist in helix-editor/spellbook docs/compare.md (2024-11-13, by the Spellbook author, Hunspell and Nuspell through ffi-dictionaries): zspell check_word 'earth' 46.86 ns vs Hunspell 212.30 and Nuspell 126.97, 'EARTH' 52.63 vs Hunspell 1,426.46, about 4.5-27x over Hunspell (derived from page data); no hardware, compiler or zspell version. The current compare.md re-ran the other engines with Criterion in 2026-06 while the zspell table is still the 2024 run, so use the table at ca13e83. Costs: 57 MB peak heap vs Hunspell 3.2 MB; pt_BR ran over 6 minutes and 100 GB before being killed; no compounds; stacked suffixes rejected (#116). Raised from D to C.

## Caveats and trade-offs

The lead said numbers exist only against Spellbook; neither the zspell README, benches/findings.md nor the Spellbook README (helix-editor/spellbook) contains a Hunspell or Nuspell timing for zspell, and Spellbook's README only cites zspell as the basis of its .dic/.aff parser. A WebSearch snippet (snippet only) shows the old zspell 0.1.x docs on docs.rs claiming about 40-50 ns per word on an average laptop, again with no comparison against another checker. Not notable by star count (63); kept at D at the orchestrator's request. License is the repo's LICENSE file (Apache-2.0 header, Cargo license-file), and dictionary and test-suite files carry other licenses (Hunspell tests under MPL, dictionaries under various licenses), so usability is arguably mixed for the data. Last commit 2024-07-09 (dependency bumps; last release commit 2024-06-13), stale. [retier] Enricher: hardware, compiler and zspell version unstated; the current compare.md re-ran the other engines in 2026-06 while the zspell row is the 2024 run, so only the ca13e83 table is like-for-like; 57 MB peak heap vs Hunspell 3.2 MB; pt_BR exceeded 6 minutes and 100 GB; no compounds; stacked suffixes rejected (#116).

Hunspell-format dictionaries only, no compound-word handling, suggestions are work in progress (README feature table); Python bindings (zspell-py) in beta.

## Maintenance

Stale since 2024-07-09 (last release 0.5.5) but Apache-2.0 and small; the record's 'no comparison found' is superseded by Spellbook's independent 2024 measurement (a retier above D looks justified, capped by the unstated hardware and the unpublished zspell bench), while its memory blow-up on complex dictionaries and missing compounds or suggestions limit it to en_US-like bulk checking.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification D, tier now C.
- **Tier reason:** The README Performance section only says zspell 'tends to outperform other spellcheckers' with no numbers or named baseline; benches/findings.md times internal collection choices (hashbrown HashSet contains 279 ns vs std HashSet 530 ns), not Hunspell or Nuspell.
- **Retiered** D to C: Raised from D to C: numbers exist in the Spellbook author's docs/compare.md (2024-11-13, Hunspell and Nuspell through ffi-dictionaries), but no hardware, compiler or zspell version is stated and the author maintains a competing library.
- **Verifier notes:** Kept at D under the keep-and-document rule: no measured comparison against Hunspell or Nuspell (shortcoming: unbacked 'tends to outperform' claim, low notability, stale since 2024-07). Metadata (Apache-2.0, 2024-07-09, stale) confirmed.
- **Fields the verifier corrected:** `stars_or_usage`, `caveats`, `claimed_speedup`, `baseline`
- **Shortcomings recorded by:** verifier batch-115 (wave 14 seed pass, 2026-10-13); enricher (seed pass, 2026-10-13)
- **Pages the verifier opened:**
  - <https://github.com/pluots/zspell>
  - <https://github.com/pluots/zspell/commits>
  - <https://raw.githubusercontent.com/pluots/zspell/HEAD/README.md>
  - <https://raw.githubusercontent.com/pluots/zspell/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/pluots/zspell/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/pluots/zspell/HEAD/benches/findings.md>
  - <https://raw.githubusercontent.com/helix-editor/spellbook/HEAD/README.md>
  - <https://crates.io/api/v1/crates/zspell>
- **Sources the enricher read:**
  - <https://github.com/pluots/zspell>
  - <https://raw.githubusercontent.com/pluots/zspell/HEAD/README.md>
  - <https://raw.githubusercontent.com/pluots/zspell/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/pluots/zspell/HEAD/benches/findings.md>
  - <https://raw.githubusercontent.com/pluots/zspell/HEAD/zspell/Cargo.toml>
  - <https://raw.githubusercontent.com/pluots/zspell/HEAD/zspell/src/lib.rs>
  - <https://raw.githubusercontent.com/pluots/zspell/HEAD/zspell/src/dict.rs>
  - <https://raw.githubusercontent.com/pluots/zspell/HEAD/zspell/benches/datastructure.rs>
  - <https://github.com/pluots/zspell/issues?q=is%3Aissue>
  - <https://github.com/pluots/zspell/issues/116>
  - <https://github.com/pluots/zspell/issues/89>
  - <https://github.com/pluots/zspell/commits/main>
  - <https://raw.githubusercontent.com/helix-editor/spellbook/HEAD/README.md>
  - <https://raw.githubusercontent.com/helix-editor/spellbook/HEAD/docs/internals.md>
  - <https://raw.githubusercontent.com/helix-editor/spellbook/HEAD/docs/compare.md>
  - <https://raw.githubusercontent.com/helix-editor/spellbook/781c609/docs/compare.md>
  - <https://raw.githubusercontent.com/helix-editor/spellbook/ca13e83/docs/compare.md>
  - <https://github.com/helix-editor/spellbook/commits/master/docs/compare.md>
  - <https://github.com/helix-editor/spellbook/commit/09013cf>
  - <https://github.com/the-mikedavis/ffi-dictionaries/tree/main/benches>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/pluots/zspell`) · [data/wave14/enrich/raw/github_com_pluots_zspell.json](../../../data/wave14/enrich/raw/github_com_pluots_zspell.json) (enrichment confidence 0.65)

</details>
