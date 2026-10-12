# uutils coreutils (Rust sort, nl, expand, base64)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Strings and text](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟢 active

> Rust reimplementation of GNU coreutils; release notes claim faster sort, base64, expand and nl than GNU, without a published harness.

| | |
|---|---|
| **Beats** | GNU coreutils sort, base64, expand and nl (C) |
| **Claimed result** | 0.3.0 release notes (dated 24 October on the page; year not shown), 'Compared to GNU': sort 3.72x faster for regular sorting and 1.46x faster for numeric sorting, base64 1.20x faster, expand 1.80x faster, unexpand 1.50x faster, nl 1.57x faster, fold 1.19x faster, uniq -c 1.13x faster. The same notes' changelog says 'fold: improve the performances - now same as GNU', contradicting the 1.19x highlight. Release 0.11.0 (31 Aug) adds join '2.5x faster than GNU', attributed in the notes to skipping the locale comparison. Releases 0.8.0, 0.9.0, 0.10.0 and 0.12.0 carry no GNU-relative figures. |
| **Workload** | Release-note comparison of individual utilities against GNU coreutils; workloads, input sizes and hardware are not given. |
| **Metric** | throughput |
| **Compiler and flags** | Not stated for the comparisons. Repository [profile.release] uses lto = "fat", codegen-units = 1, panic = "abort"; GNU coreutils version and build flags unknown. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | not stated |
| **Same optimization level** | not stated |
| **Adoption** | 24.2k stars, 2.1k forks; used by default in Ubuntu 25.10 (docs/src/performance.md) |
| **Last commit** | 2026-10-11 |
| **Links** | [repository](https://github.com/uutils/coreutils) · [benchmark](https://github.com/uutils/coreutils/releases/tag/0.3.0) |

## Verdict

The only GNU-relative figures are first-party release-note highlights: 0.3.0 (24 October, year not shown, released when the GNU test reference moved to coreutils 9.8) claims sort 3.72x faster for default sorting and 1.46x for numeric, expand 1.80x, nl 1.57x, unexpand 1.50x, base64 1.20x, fold 1.19x and uniq -c 1.13x, and 0.11.0 (31 August 2026) claims join 2.5x; no hardware, inputs, locale, thread count, GNU version or build flags are given. Outside spot checks in the issue tracker are mixed: plain release sort on /usr/share/dict/words was 1.5x faster than GNU, while sort -m and -z were 7.7x and 13.7x slower.

## Use it when

- Scripts that must behave the same on Linux, macOS, Windows and WASI with GNU-style options.
- Large in-memory sort jobs on many-core machines, plain whole-line keys, release or PGO build: an outside user measured 100.2 ms against GNU's 152.4 ms on /usr/share/dict/words (issue #13193).
- Bulk base64 encoding or decoding of large files on SIMD-capable CPUs, where base64-simd does the work.
- Systems that already ship it by default (Ubuntu 25.10 and later), where checking the GNU-relative claims for your own workload is cheap with the hyperfine recipe in docs/src/performance.md.

## Skip it when

- sort -m on already sorted input or sort -z: the same outside run measured GNU 7.66x and 13.72x faster (issue #13193, closed with no fix recorded).
- Pipelines that depend on glibc's exact collation order in UTF-8 locales: uutils collates with ICU4X, and an April 2026 guide warns of divergence under en_US.UTF-8 (search snippet only); use LC_ALL=C for both.
- Scripts that exercise rare GNU options or edge cases: release 0.12.0 still fails 21 GNU tests (653 pass).
- Utilities with open slower-than-GNU issues: date (#14750), factor (#11439, 'extremely slower'), mktemp (#11064), echo (#10852), cat (#10832) and true startup (#11340).
- Debug builds, which ran 10x slower than GNU sort in issue #13193 and about 48x slower in issue #11258.

## How it is fast

sort runs its in-memory sort on rayon (par_sort_unstable_by, or par_sort_by for -s and -u) with a thread pool sized from --parallel or std::thread::available_parallelism, parses -n keys once per line, and in UTF-8 locales computes an ICU4X collation sort key once per line (compute_sort_key_utf8, Shifted and Quaternary to mimic GNU) so comparisons are plain byte compares. base64 uses the base64-simd crate (switched in PR #8578, September 2025). expand writes buffers with no tab, backspace or carriage return straight through, without per-character processing. Since August 2026 the release binaries are built with PGO trained on exactly the claimed utilities (util/build-pgo.sh); docs/src/performance.md credits PGO with -17% on sort and -22% to -29% on nl, fold and uniq -c.

## Compared with alternatives

Pick uutils when you want the whole GNU-compatible tool set, the same across platforms; single-purpose siblings such as hck or tuc (cut), huniq or runiq (sort | uniq), cw or wz (wc) and rust-sort are faster at their one job but change the interface or semantics. RustyBox is the other multi-tool Rust userland in the catalog, but uutils targets GNU option compatibility and is the one Ubuntu ships.

## Integration

| | |
|---|---|
| **Form** | crate (multicall CLI binary `coreutils`; per-utility uu_\* crates with a uumain entry point) |
| **Dependencies** | sort: rayon, memchr, foldhash, bigdecimal, ICU4X (icu_collator, icu_decimal, icu_datetime) through uucore; base64: base64-simd and data-encoding through uucore; optional OpenSSL libcrypto for the checksum utilities (feature openssl); libselinux and libclang only for SELinux tools. |
| **Minimum toolchain** | Rust 1.88.0 (workspace rust-version); tested against stable, beta and nightly. |
| **Platforms** | Linux, macOS, FreeBSD and other BSDs, Windows, WASI (sort runs single-threaded on WASI); musl and glibc release binaries. |
| **Thread safety** | Not applicable (command-line processes); sort uses a global rayon pool sized by --parallel, defaulting to all available cores. |
| **Drop-in for the baseline** | partial — designed as a GNU coreutils drop-in and default on Ubuntu since 25.10, but 21 GNU tests still fail in 0.12.0 and UTF-8 collation comes from ICU4X, not glibc |

## Gotchas

- No harness behind the numbers: the 0.3.0 'Compared to GNU' list (sort 3.72x and 1.46x, expand 1.80x, nl 1.57x, unexpand 1.50x, base64 1.20x, fold 1.19x, uniq -c 1.13x) and the 0.11.0 join 2.5x give no hardware, input, locale, thread count or GNU version, and the in-tree Divan and CodSpeed benches time uutils against itself. The same 0.3.0 changelog says 'fold: improve the performances - now same as GNU', which contradicts the 1.19x line.
- Unequal settings are easy to hit: uutils sort uses every available core unless --parallel is given, collates UTF-8 locales with precomputed ICU4X keys while C and C.UTF-8 use byte comparison, and shipped binaries since August 2026 are PGO-trained on sort, sort -n, nl, fold, expand, unexpand, uniq -c, join and base64. expand copies tab-free buffers straight through, so a tab-free test file measures a copy loop. Pin LC_ALL, --parallel and the build type before comparing.
- Pathological regressions have appeared after release-note speedups: issue #11258 measured `sort` of about 100 million random integers under en_US.UTF-8 at 51m38s against GNU's 1m47s (about 29x slower); it was closed by PR #11412, though the reporter was not sure it was fixed. In issue #8574, base64 0.1.0 was 7.9x slower than GNU on 4 GB files (19.556 s vs 2.461 s, i7-13620H) before the base64-simd switch.
- Issue #9213 (still open) reports base64 --decode reading all of stdin first (about 325 MB peak against GNU's 1 MB on a 500 MB stream); current src/uu/base32/src/base_common.rs streams every format except Base58, so this looks fixed in code even though the issue is open.

## Known shortcomings

- Only the 0.3.0 release notes' 'Compared to GNU' percentages (sort 3.72x/1.46x, base64 1.20x, expand 1.80x, unexpand 1.50x, nl 1.57x, fold 1.19x, uniq -c 1.13x, join 2.5x from 0.11.0 by skipping locale comparison) with no hardware, input, locale, GNU version or build flags; the fold figure contradicts itself; the base64 win comes from the base64-simd crate; Phoronix reports cksum up to 17x slower than GNU.
- No harness behind the release-note numbers; the in-tree benches compare uutils with itself. Unequal-setting traps: sort uses all cores via available_parallelism, ICU4X collation keys in UTF-8, release binaries are PGO-trained since August 2026 on exactly the claimed utilities, and expand passes tab-free buffers straight through. Outside runs: #13193 plain sort 1.5x faster but -m 7.66x and -z 13.72x slower; #11258 sort about 29x slower in en_US.UTF-8 (closed, fix unconfirmed); #8574 base64 0.1.0 7.9x slower before base64-simd; #9213 still open though the code now streams.

## Caveats and trade-offs

No numbers in the README; the only figures are release-note highlights with no hardware, build profile, input size, locale or GNU version, so they cannot be reproduced from the page. docs/src/performance.md and src/uu/sort/BENCHMARKING.md give hyperfine recipes (and warn that locale matters a lot for sort) but no results; the in-tree CodSpeed/Divan benches compare uutils with itself, not GNU. base64 speed comes from the base64-simd crate (SIMD library, Cargo.toml), sort uses rayon, and the 0.11.0 join gain is attributed to skipping the locale comparison, so equal-work comparisons with GNU are not established. Search snippets (Phoronix, September 2025; not opened) reported Ubuntu 25.10 regressions: cksum up to 17x slower than GNU on some large files and sort never finishing on very large single-line files. A conference demo reported by an earlier search snippet showed a debug build only 1.45x faster than GNU sort and a release build about 6x (not verified here). [retier] No harness behind the release-note numbers; the in-tree benches compare uutils with itself. sort uses all cores via available_parallelism, collation keys come from ICU4X in UTF-8, release binaries are PGO-trained since August 2026 on exactly the claimed utilities, and expand passes tab-free buffers straight through. Outside runs: #13193 plain sort 1.5x faster but -m 7.66x and -z 13.72x slower; #11258 sort about 29x slower in en_US.UTF-8 (closed, fix unconfirmed); #8574 base64 0.1.0 7.9x slower before base64-simd.

Not a full GNU drop-in yet (search snippets report roughly 500 of 600 GNU tests passing; not checked). Cross-platform including Windows.

## Maintenance

Very active (last commit 2026-10-11, release 0.12.0 on 17 September 2026, 24.2k stars), MIT-licensed and the Ubuntu default since 25.10; treat the speedups as unreproduced first-party claims and benchmark your own workload with LC_ALL, --parallel and the build type pinned.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The 0.3.0 release notes list 'Compared to GNU' speedups (sort 3.72x/1.46x, base64 1.20x, expand 1.80x, unexpand 1.50x, nl 1.57x, fold 1.19x, uniq -c 1.13x) with no hardware, input, GNU version or build profile; Phoronix and heise relay the project's figures rather than measuring (snippet only), so first-party tier C.
- **Verifier notes:** Large, notable project; claim is first-party release-note highlights only, tier C. Shortcomings: no methodology (hardware, inputs, locale, GNU version), fold figure self-contradictory, base64 win from base64-simd SIMD crate and join win from skipping locale comparison (not same work or not language-level), some utilities reported slower than GNU (cksum up to 17x, snippet only). Not a language-level claim.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-37 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/uutils/coreutils>
  - <https://github.com/uutils/coreutils/commits/main>
  - <https://github.com/uutils/coreutils/releases/tag/0.3.0>
  - <https://github.com/uutils/coreutils/releases>
  - <https://github.com/uutils/coreutils/releases/tag/0.11.0>
  - <https://raw.githubusercontent.com/uutils/coreutils/HEAD/README.md>
  - <https://raw.githubusercontent.com/uutils/coreutils/HEAD/docs/src/performance.md>
  - <https://raw.githubusercontent.com/uutils/coreutils/HEAD/src/uu/sort/BENCHMARKING.md>
  - <https://raw.githubusercontent.com/uutils/coreutils/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/uutils/coreutils/HEAD/src/uucore/Cargo.toml>
  - <https://raw.githubusercontent.com/uutils/coreutils/HEAD/src/uu/sort/Cargo.toml>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/uutils/coreutils/HEAD/README.md>
  - <https://raw.githubusercontent.com/uutils/coreutils/HEAD/docs/src/performance.md>
  - <https://raw.githubusercontent.com/uutils/coreutils/HEAD/src/uu/sort/BENCHMARKING.md>
  - <https://raw.githubusercontent.com/uutils/coreutils/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/uutils/coreutils/HEAD/src/uu/sort/Cargo.toml>
  - <https://raw.githubusercontent.com/uutils/coreutils/HEAD/src/uu/base64/Cargo.toml>
  - <https://raw.githubusercontent.com/uutils/coreutils/HEAD/src/uucore/Cargo.toml>
  - <https://raw.githubusercontent.com/uutils/coreutils/HEAD/src/uu/sort/src/sort.rs>
  - <https://raw.githubusercontent.com/uutils/coreutils/HEAD/src/uucore/src/lib/features/i18n/collator.rs>
  - <https://raw.githubusercontent.com/uutils/coreutils/HEAD/util/build-pgo.sh>
  - <https://raw.githubusercontent.com/uutils/coreutils/HEAD/src/uu/expand/src/expand.rs>
  - <https://raw.githubusercontent.com/uutils/coreutils/HEAD/src/uu/expand/benches/expand_bench.rs>
  - <https://raw.githubusercontent.com/uutils/coreutils/HEAD/src/uucore/src/lib/features/benchmark.rs>
  - <https://raw.githubusercontent.com/uutils/coreutils/HEAD/src/uu/base32/src/base_common.rs>
  - <https://github.com/uutils/coreutils/releases/tag/0.3.0>
  - <https://github.com/uutils/coreutils/releases>
  - <https://github.com/uutils/coreutils/commits/main/util/build-pgo.sh>
  - <https://github.com/uutils/coreutils/issues?q=is%3Aissue%20slower%20than%20GNU>
  - <https://github.com/uutils/coreutils/issues/9213>
  - <https://github.com/uutils/coreutils/issues/11258>
  - <https://github.com/uutils/coreutils/issues/13193>
  - <https://github.com/uutils/coreutils/issues/8574>
  - WebSearch: Phoronix benchmark Rust coreutils uutils vs GNU coreutils sort base64 performance 2026 (snippets of phoronix.com Rust-Coreutils-0.3-Released, Rust-Coreutils-0.2.2, Ubuntu-Rust-Coreutils-Perf and computingforgeeks.com ubuntu-2604-rust-coreutils-guide; pages not opened)
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/uutils/coreutils`) · [data/wave14/enrich/raw/github_com_uutils_coreutils.json](../../../data/wave14/enrich/raw/github_com_uutils_coreutils.json) (enrichment confidence 0.6)

</details>
