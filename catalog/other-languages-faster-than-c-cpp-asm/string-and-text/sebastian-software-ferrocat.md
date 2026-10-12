# ferrocat (Rust Gettext PO catalog engine)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Strings and text](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0 OR MIT` · 🟢 active

> Rust Gettext PO parser and catalog merge/update engine; first-party runs merge a 10k-message catalog about 56x faster than GNU msgmerge.

| | |
|---|---|
| **Beats** | GNU msgmerge (gettext-tools 1.0, C), run as a separate process per iteration |
| **Claimed result** | README table (10k-message catalog, Apple M1 Ultra, median MiB/s, commit c3caa27): update with new strings 291 MiB/s vs GNU msgmerge 4.8 MiB/s (about 61x); merge_catalog 6.94 ms vs 391.6 ms (about 56x). The 'full catalog update' row (150 MiB/s, about 33x; README 'roughly 31x') is struck: at c3caa27 update_catalog dropped all '#,' flags and turned translator comments into '#.', so it measured lossy work (fixed in d057d1d, 3.1.0, never re-measured). |
| **Workload** | Merge or update a 10,000-message Gettext PO catalog with freshly extracted messages, file to file (parse existing and new files, merge by exact identity, serialise). |
| **Metric** | throughput |
| **Hardware** | Apple M1 Ultra, 64 GB RAM, macOS arm64 (report environment block); 2 warmup and 5 measured samples per scenario. |
| **Compiler and flags** | Ferrocat: rustc 1.95.0-nightly (842bd5be2 2026-01-29), workspace release profile lto = fat, codegen-units = 1 (default opt-level 3), ferrocat 2.2.0 at commit c3caa27. msgmerge: GNU gettext-tools 1.0 binary from the host, invoked as 'msgmerge --no-wrap --quiet --no-fuzzy-matching existing.po template.pot' with stdout captured; its compiler and build flags are not stated. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Why it wins** | README: byte-oriented scanning and move-not-clone catalog paths in the merge; the update benchmark parses both files, merges and serialises. |
| **Adoption** | 0 stars, 0 forks (525 commits); ferrocat crate 7,706 downloads on crates.io (latest 3.4.2, 2026-08-06) |
| **Last commit** | 2026-10-05 |
| **Links** | [repository](https://github.com/sebastian-software/ferrocat) · [benchmark](https://raw.githubusercontent.com/sebastian-software/ferrocat/HEAD/benchmark/results/gettext-workflows-ecosystem-v1-c3caa27.json) |

## Verdict

First-party ferrocat-bench reports at commit c3caa27 (Apple M1 Ultra, macOS, rustc 1.95.0-nightly with fat LTO; GNU gettext-tools 1.0 msgmerge from the host with unknown build flags; 2 warm-up and 5 measured samples) on a synthetic 10,000-message PO update. merge_catalog took 6.94 ms per merge against 391.6 ms for 'msgmerge --no-wrap --quiet --no-fuzzy-matching' after subtracting a 7 ms process start-up baseline (about 56x). The higher-level update_catalog_file took 11.85 ms against 392.9 ms (about 33x), but that build dropped PO flags and translator comments, which the harness did not check.

## Use it when

- Build or CI steps that merge freshly extracted messages into many large UTF-8 PO catalogs and currently shell out to msgmerge once per locale, and that can call a Rust API (or wrap one in a small tool).
- Exact-identity updates (msgctxt + msgid) where you already run msgmerge with --no-fuzzy-matching or do not want fuzzy guesses.
- Rust or Palamedes (JS/TS via its palamedes-node bridge) i18n pipelines that also need ICU MessageFormat checks, coverage or audit reports and runtime artifacts from the same catalog model.
- Teams that want git-merge-friendly catalog storage (FCL, one entry per line) next to PO.

## Skip it when

- You rely on msgmerge's fuzzy matching (its default) to carry translations over to changed msgids: Ferrocat merges by exact identity only, by design.
- Catalogs in legacy charsets (ISO-8859-x, EUC, etc.): inputs are Rust &str, so they must be UTF-8 already. msgmerge converts charsets through iconv.
- You need a command-line drop-in for msgmerge or msgcat in shell scripts or Makefiles: there is no documented merge subcommand, and the GNU options (--previous, --compendium, --backup, wrapping) have no direct equivalents.
- Versions before 3.1.0 (PR #276) on hand-edited catalogs: the catalog-layer update dropped #, flags such as fuzzy and no-wrap and rewrote translator comments as extracted comments.
- Risk-averse production use: 0 stars, a single vendor, about 7.7k crates.io downloads, and frequent breaking changes even in minor releases (a yanked 3.0.0; Unreleased already has breaking changes).

## How it is fast

The parser scans bytes, not characters. It finds structural bytes with memchr, memchr2 and memchr3 (SIMD in the memchr crate) and has a hand-written NEON path on aarch64 for finding escapable bytes. A borrowed parser hands out Cow&lt;str&gt; slices of the input, so unescaped fields are never copied. The merge moves message payloads instead of cloning them and avoids throwaway sets and buffers; most of these were allocation-cutting commits in 3.1.0, including c3caa27 itself. GNU msgmerge, by contrast, reads both files through its general multibyte-aware PO lexer in a fresh process. The speed-up comes from the design of the parser and merge, not from the choice of Rust.

## Compared with alternatives

No other Gettext/PO tool is catalogued in string-and-text, so the choice is Ferrocat versus GNU gettext itself. Ferroni (the same vendor's Oniguruma port) and the text-processing CLIs listed there solve different problems; pick Ferrocat when the job is catalog merging, auditing or compiling.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | ferrocat-po: memchr, smallvec, rustc-hash; the default 'catalog' feature adds ferrocat-icu, icu_locale, icu_plurals, serde, serde_json, sha2 and tempfile. Use default-features = false for the parser, serializer and merge_catalog only. |
| **Minimum toolchain** | Rust 1.94.0 (MSRV), edition 2024; the benchmark was built with rustc 1.95.0-nightly, fat LTO, codegen-units = 1 |
| **Platforms** | any Rust target; the explicit NEON scan path is aarch64-only and other targets fall back to memchr; the prebuilt CLI archive is x86_64-unknown-linux-musl only |
| **Thread safety** | not documented (the merge and parse functions are free functions over borrowed strings and return owned output) |
| **Drop-in for the baseline** | partial: it does the same exact-identity merge as 'msgmerge --no-fuzzy-matching' and its output passes the same message digest, but it is a Rust API rather than a CLI, handles UTF-8 only, has no fuzzy matching, and orders and formats the output its own way (merge output was about 7% larger than msgmerge's). |

## Gotchas

- Harness flaw behind the 'Full catalog update' row (150 MiB/s, 11.85 ms vs msgmerge 392.9 ms adjusted, about 33x, the README's 'roughly 31x'): at the measured commit c3caa27, CanonicalMessage had no flags field. import_message_from_po ignored item.flags and folded translator (#) comments into the extracted-comment list, and export wrote them back as #. lines. So every #, fuzzy and #, c-format flag in the fixture's existing.po was dropped (each of the 10,000 entries carries one or the other), and fuzzy translations came out as active ones; msgmerge keeps them. This was fixed after the measurement in d057d1d (issue #271, PR #276, released in 3.1.0), and the published numbers were not re-measured.
- The benchmark's 'same semantic digest' check (PoSemanticSummary) compares only headers, msgctxt, msgid, msgid_plural, msgstr and the obsolete bit, with items sorted. Flags, translator or extracted comments, references and output order are not checked, which is why the dropped flags passed. The low-level merge_catalog row (6.94 ms vs 391.6 ms, about 56x) is not affected: merge.rs at c3caa27 keeps translator comments and writes a merged flags line.
- The fixture is synthetic, generated by crates/ferrocat-bench/src/fixtures.rs: an ASCII-leaning German UI catalog with 10,000 entries; every fifth active message is missing from the template (so it becomes obsolete) and 1,000 new messages are added. The ferrocat side is timed on in-memory strings in a loop of 20-35 iterations; msgmerge is timed as one fresh process per sample (5 samples) that reads two files and writes to a pipe, and a 7 ms empty-run time is subtracted.
- The reports label the build 'ferrocat@2.2.0', but commit c3caa27 is post-3.0.1 3.1.0 development code. The MiB/s figures count output bytes, so implementations that write more output score higher at the same speed.

## Known shortcomings

- README cells come from the c3caa27 reports (merge about 56x, update about 33x by time); the harness runs msgmerge with --no-fuzzy-matching and subtracts empty-run startup; msgmerge flags unknown; ferrocat reads in-memory strings while msgmerge reads files; MiB/s counts output bytes; 0 stars.
- Harness flaw: at benchmarked commit c3caa27 the catalog-layer update_catalog dropped all '#,' flags (fuzzy, c-format) and turned translator comments into '#.', so the 'full catalog update' row (150 MiB/s, about 33x; README 'roughly 31x' vs msgmerge) measured lossy code in which fuzzy entries came out active; fixed later in d057d1d (issue #271, PR #276, 3.1.0) and never re-measured. The bench digest (PoSemanticSummary) checks only headers, msgctxt, msgid, msgid_plural, msgstr and obsolete, so the drop went unnoticed. The merge_catalog row (6.94 ms vs 391.6 ms, about 56x) is unaffected (merge.rs keeps comments and flags). Synthetic fixture, UTF-8 only, no fuzzy matching, no msgmerge-style CLI, 0 stars; the report label says 2.2.0 though the code is post-3.0.1.

## Caveats and trade-offs

First-party benchmark, one machine; msgmerge build flags unknown, so optimisation levels cannot be compared. The harness is fairer than it first looks: msgmerge runs with --no-fuzzy-matching (exact identity, like ferrocat), every implementation's output has the same semantic digest per fixture, and the published msgmerge MiB/s subtracts a header-only empty-run baseline (about 7 ms) to remove process start-up. Remaining asymmetries: ferrocat reads the template and existing catalog from in-memory strings inside the timed loop while msgmerge reads two files and writes to a pipe from a fresh process; MiB/s counts output bytes, and ferrocat's merge output is about 7% larger per operation than msgmerge's (2,115,311 vs 1,971,324 bytes), so the merge MiB/s ratio (61x) overstates the time ratio (56x); the README full-update cell (150 MiB/s) comes from a different report than the msgmerge cell. Numbers were measured on ferrocat 2.2.0; the current release is 3.4.2. Zero stars, so the project is unproven in the field. The speed-up is design (byte-oriented scanning, move-not-clone merge paths) against a general GNU tool, not a language-level effect. [retier] At benchmarked commit c3caa27 the catalog-layer update_catalog dropped all '#,' flags (fuzzy, c-format) and turned translator comments into '#.', so the full-update row measured lossy code in which fuzzy entries came out active; the bench digest checks only headers, msgctxt, msgid, msgid_plural, msgstr and obsolete, so the drop went unnoticed. Synthetic fixture, UTF-8 only, no fuzzy matching, no msgmerge-style CLI; the report label says 2.2.0 though the code is post-3.0.1.

Rust-native API only (no first-party C or other host bindings); ICU MessageFormat and FCL catalog modes go beyond what msgmerge does.

## Maintenance

Active (last commit 2026-10-05, crate 3.4.2 from 2026-08-06, MIT OR Apache-2.0) and easy to adopt as a crate, but it has 0 stars and a single vendor, and the published msgmerge numbers predate the 3.1.0 fix that made the high-level update keep fuzzy and other flags. Treat the 56x merge figure as the credible one and the 31x full-update figure as unverified for the current code.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party benchmark with public harness code (crates/ferrocat-bench/src/compare/operations.rs) and checked-in JSON reports naming rustc and the CPU (Apple M1 Ultra), but msgmerge's build flags and compiler are not stated, so not A; no independent measurement, so not B.
- **Verifier notes:** Confirm C. README numbers come from the c3caa27 reports, not the a84e6fb report the record cites; benchmark_url and claimed_speedup corrected (merge about 56x, update about 33x by time). Record's caveats about fuzzy matching and process start-up were wrong (harness uses --no-fuzzy-matching and subtracts an empty-run baseline). Shortcomings: first-party, msgmerge flags unknown, in-memory vs file I/O asymmetry, output-byte MiB/s metric, 0 stars.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-103 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/sebastian-software/ferrocat/HEAD/benchmark/results/gettext-workflows-ecosystem-v1-a84e6fb.json>
  - <https://raw.githubusercontent.com/sebastian-software/ferrocat/HEAD/benchmark/results/gettext-workflows-ecosystem-v1-c3caa27.json>
  - <https://raw.githubusercontent.com/sebastian-software/ferrocat/HEAD/benchmark/results/catalog-order-default-v1-c3caa27.json>
  - <https://raw.githubusercontent.com/sebastian-software/ferrocat/HEAD/benchmark/published-numbers.json>
  - <https://raw.githubusercontent.com/sebastian-software/ferrocat/HEAD/README.md>
  - <https://raw.githubusercontent.com/sebastian-software/ferrocat/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/sebastian-software/ferrocat/HEAD/crates/ferrocat-bench/src/compare/operations.rs>
  - <https://raw.githubusercontent.com/sebastian-software/ferrocat/HEAD/crates/ferrocat-bench/src/compare.rs>
  - <https://github.com/sebastian-software/ferrocat>
  - <https://github.com/sebastian-software/ferrocat/commits/main>
  - <https://github.com/sebastian-software/ferrocat/tree/main/benchmark/results>
  - <https://github.com/sebastian-software/ferrocat/tree/main/crates/ferrocat-bench/src>
  - <https://crates.io/api/v1/crates/ferrocat>
- **Sources the enricher read:**
  - <https://github.com/sebastian-software/ferrocat>
  - <https://raw.githubusercontent.com/sebastian-software/ferrocat/HEAD/README.md>
  - <https://raw.githubusercontent.com/sebastian-software/ferrocat/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/sebastian-software/ferrocat/HEAD/benchmark/published-numbers.json>
  - <https://raw.githubusercontent.com/sebastian-software/ferrocat/HEAD/benchmark/results/gettext-workflows-ecosystem-v1-c3caa27.json>
  - <https://raw.githubusercontent.com/sebastian-software/ferrocat/HEAD/benchmark/results/catalog-order-default-v1-c3caa27.json>
  - <https://raw.githubusercontent.com/sebastian-software/ferrocat/HEAD/crates/ferrocat-bench/src/compare/operations.rs>
  - <https://raw.githubusercontent.com/sebastian-software/ferrocat/HEAD/crates/ferrocat-bench/src/compare.rs>
  - <https://raw.githubusercontent.com/sebastian-software/ferrocat/HEAD/crates/ferrocat-bench/src/compare/semantic_digest.rs>
  - <https://raw.githubusercontent.com/sebastian-software/ferrocat/HEAD/crates/ferrocat-bench/src/fixtures.rs>
  - <https://raw.githubusercontent.com/sebastian-software/ferrocat/HEAD/crates/ferrocat-po/Cargo.toml>
  - <https://raw.githubusercontent.com/sebastian-software/ferrocat/HEAD/crates/ferrocat/CHANGELOG.md>
  - <https://raw.githubusercontent.com/sebastian-software/ferrocat/c3caa274664a992410d654fc0ac072c042af9e6d/crates/ferrocat-po/src/api/catalog.rs>
  - <https://raw.githubusercontent.com/sebastian-software/ferrocat/c3caa274664a992410d654fc0ac072c042af9e6d/crates/ferrocat-po/src/api/export.rs>
  - <https://raw.githubusercontent.com/sebastian-software/ferrocat/c3caa274664a992410d654fc0ac072c042af9e6d/crates/ferrocat-po/src/merge.rs>
  - <https://raw.githubusercontent.com/sebastian-software/ferrocat/c3caa274664a992410d654fc0ac072c042af9e6d/crates/ferrocat-po/src/scan.rs>
  - <https://raw.githubusercontent.com/sebastian-software/ferrocat/c3caa274664a992410d654fc0ac072c042af9e6d/crates/ferrocat-po/src/lib.rs>
  - <https://github.com/sebastian-software/ferrocat/tree/c3caa274664a992410d654fc0ac072c042af9e6d/crates/ferrocat-po/src>
  - <https://github.com/sebastian-software/ferrocat/commit/c3caa274664a992410d654fc0ac072c042af9e6d>
  - <https://github.com/sebastian-software/ferrocat/commit/d057d1d82d64cbf07ca752d18f623e4b28f23ddb>
  - <https://github.com/sebastian-software/ferrocat/commits/c3caa274664a992410d654fc0ac072c042af9e6d>
  - <https://github.com/sebastian-software/ferrocat/issues/271>
  - <https://github.com/sebastian-software/ferrocat/issues?q=is%3Aissue>
  - <https://crates.io/api/v1/crates/ferrocat>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/sebastian-software/ferrocat`) · [data/wave14/enrich/raw/github_com_sebastian_software_ferrocat.json](../../../data/wave14/enrich/raw/github_com_sebastian_software_ferrocat.json) (enrichment confidence 0.8)

</details>
