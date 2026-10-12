# xerg (xtreme-grep, Rust parallel grep)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Strings and text](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Rust` · `MIT` · 🟢 active

> Small Rust learning-project grep (xerg) that searches files in parallel with rayon; claims 17.7-33.7x over macOS system grep on a target/ directory.

| | |
|---|---|
| **Beats** | system grep (implementation and version not stated; the test environment is macOS, so probably BSD grep) |
| **Claimed result** | README and PERFORMANCE_ANALYSIS.md ('Final Performance Validation', 2025-11-13): large dataset (target/ directory) system grep 28,122 ms vs xerg 1,590 ms (17.7x) and xerg -x 835 ms (33.7x); single file (src/main.rs) 4.0 ms vs 3.0 ms (README: 25% speedup; PERFORMANCE_ANALYSIS: 1.33x); src/ set of about 8 files 3.0 ms vs 3.0 ms (parity) and -x 4.0 ms (slower). The README's mode table contradicts the main table (default '23x', CPU 650% and 690%). |
| **Workload** | Search one pattern (not stated) over a Rust target/ build directory, over src/main.rs, and over src/ (about 8 files) with system grep and with xerg; timings at 1 ms resolution; the grep command line and number of runs are not published. |
| **Metric** | throughput |
| **Hardware** | 'macOS, Multi-core system' (README); 'MacBook with full-power mode enabled' (PERFORMANCE_ANALYSIS.md); CPU model not stated |
| **Compiler and flags** | 'Release builds' (README); Cargo.toml has no [profile.release] section, so default cargo release settings (opt-level 3, no LTO); rustc version not stated; grep version and flags not stated. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Why it wins** | README: parallel multi-core file scanning (CPU use about 484% to 745% vs about 96% for grep). |
| **Adoption** | 3 stars; 142 crates.io downloads (xerg 0.2.1) |
| **Last commit** | 2025-11-14 |
| **Links** | [repository](https://github.com/yinkam/xtreme-grep) · [benchmark](https://raw.githubusercontent.com/yinkam/xtreme-grep/HEAD/README.md) |

## Verdict

First-party, single-environment timings on an unnamed multi-core MacBook against 'system grep' (version and flags unstated, most likely macOS BSD grep) with an unstated pattern: on a Rust target/ directory 28,122 ms for grep vs 1,590 ms for xerg default and 835 ms for xerg -x, with near-identical 3-4 ms results on one file and on src/. The work is unequal (parallel vs single-threaded, binary lines and hidden directories skipped by xerg), so the ratio does not measure faster matching.

## Use it when

- Reading a compact (about 1,000 lines) example of rayon-parallel file search in Rust, which is what the project calls itself: a Pragmatic AI Labs bootcamp learning project.
- Ad-hoc interactive searches of UTF-8 source trees on a multi-core machine where coloured, per-file grouped output is wanted and grep flags are not.
- Comparisons against BSD grep on macOS, the only baseline it was measured against.

## Skip it when

- Any scripted or grep-compatible use: ANSI colour codes are always emitted (default red, no --color=never or auto), even with -x into a pipe, and the -x format puts a space after the line-number colon.
- Searching binaries, build output or non-UTF-8 text: multi-file mode silently drops every line that is not valid UTF-8 without running the regex on it, and a single file of up to 100 MB that is not valid UTF-8 fails with an error instead of being searched.
- When you need case-insensitive or inverted matching, counts, file lists or fixed strings: none of these flags exist yet.
- When ripgrep (catalogued in wave 11) is available: it does the same parallel walk with binary detection, .gitignore handling, full flags and published benchmarks.
- Huge result sets in default mode: results are queued in an unbounded channel and printed only after every file has been searched.

## How it is fast

Data parallelism: walkdir collects the file list, then a global rayon pool of cores-1 threads spawns one task per file, which accounts for the 484-745% CPU use reported against grep's \~96%. Matching uses the Rust regex crate (finite-automata engine with literal prefilters, not PCRE). Single files skip the pool and are read with fs::read_to_string (up to 7 MB) or memmap2 (7-100 MB); multi-file runs stream each file with BufReader::lines().

## Compared with alternatives

Practically never for production: ripgrep (wave 11) covers the same parallel search with correct binary and encoding handling, and fastgrep and zrep in this category at least benchmark against named GNU grep 3.12. xerg only makes sense as a short, readable teaching example of rayon-based search.

## Integration

| | |
|---|---|
| **Form** | crate (CLI binary `xerg`; the lib exposes run, run_xtreme and search_files) |
| **Dependencies** | clap, rayon, regex (default features off: std, perf, unicode-perl), walkdir, memmap2, num_cpus |
| **Minimum toolchain** | Rust edition 2024, so Rust 1.85 or newer; no rust-version declared |
| **Platforms** | Any Rust std target in principle; README results are macOS only |
| **Thread safety** | Not applicable to the CLI; the binary builds a global rayon pool of cores-1 threads, and the lib's search functions run on whatever global rayon pool the host process has |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw behind the 17.7x/33.7x numbers: on the target/ directory xerg skips hidden directories (target/\*/.fingerprint) and drops every non-UTF-8 line of the binary artefacts without regex-matching it, while grep scans every byte single-threaded; in -x mode the stats line hard-codes skipped:0, so the dropped lines are invisible. Pattern, grep command line, grep version (macOS ships BSD grep), CPU model and run count are not published; the 1 ms-resolution timings with a CPU% column look like one run of zsh's time builtin (inference). The single-file and src/ rows (4.0 vs 3.0 ms, 3.0 vs 3.0 ms) are within that resolution.
- benches/performance.rs does contain a grep head-to-head (contrary to the verifier note), but it calls xerg's search functions in-process while spawning grep with Command::output() on every iteration, so only grep pays process start-up and pipe capture; its default-mode runner also never prints results.
- The regex crate is built without the unicode-case feature, so any (?i) pattern in the default Unicode mode fails to compile and xerg panics on Regex::new(pattern).unwrap() (read from Cargo.toml and regex-syntax translate.rs, not executed); invalid patterns also panic. The README's 'PCRE support' claim is wrong: no backreferences or lookaround.
- The README's two tables disagree (17.7x vs '23x' for default mode, CPU 484% vs 650%); the '23x' and 6.5-6.9 core figures are from the 0.2.0 changelog and predate the 0.2.1 rewrite.

## Known shortcomings

- Unequal work: skips non-UTF-8 lines and hidden directories, so the target/ binaries are mostly unsearched; parallel against single-threaded grep; no grep command, pattern, version or CPU; the README tables disagree (17.7x vs 23x).
- Unequal work on target/: non-UTF-8 lines are dropped without matching, hidden directories are skipped, -x stats hard-code skipped:0, and the parallel run is compared with single-threaded grep; benches/performance.rs runs xerg in-process but spawns grep every iteration. The regex is built without unicode-case, so (?i) patterns should panic (read from code, not run); ANSI colour codes are always printed. Idle since 2025-11-14.

## Caveats and trade-offs

The work differs from grep's: in multi-file mode xerg reads each file with BufReader::lines() and silently skips every line that is not valid UTF-8 without running the regex on it (src/search/xtreme.rs and default.rs), so the binary artefacts that fill a target/ directory are largely not searched, while grep scans every byte; the crawler (walkdir) also skips hidden files and directories such as the .fingerprint directories under target/debug and target/release. On top of that the win is parallelism (rayon scope; 484% to 745% CPU vs about 96% for grep). Pattern, grep implementation and version (probably BSD grep on macOS), CPU model and run count are not stated, the README's two tables disagree (17.7x vs '23x'), and there is no comparison with ripgrep (listed in wave 11), which does the same parallel work. The README's 'PCRE support' claim is wrong: it uses the Rust regex crate. Tiny learning project from a bootcamp (3 stars, 142 crates.io downloads). The speed-up is not attributable to the language. [retier] Unequal work on target/: non-UTF-8 lines are dropped without matching, hidden directories are skipped, -x stats hard-code skipped:0, and the parallel run is compared with single-threaded grep; benches/performance.rs runs xerg in-process but spawns grep every iteration. The regex is built without unicode-case, so (?i) patterns should panic (read from code); ANSI colour codes are always printed. Idle since 2025-11-14.

PCRE-style regex rather than POSIX; different output format (pretty mode by default, -x for raw file:line:content); not a strict drop-in.

## Maintenance

MIT-licensed bootcamp learning project with 3 stars, 51 commits and 142 crates.io downloads; no release or commit since 0.2.1 on 2025-11-14, and the record's 'active' status is stale; the speed claim deserves D-level weight given unequal work and an unpublished harness.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now D.
- **Tier reason:** First-party README and PERFORMANCE_ANALYSIS.md table against system grep with no published grep command, pattern, grep version, CPU model or run count; the repo's Criterion benches measure only xerg's internal file readers, not grep.
- **Retiered** C to D: Enricher: xerg drops non-UTF-8 lines without matching and skips hidden directories on a target/ tree of binaries, runs in-process against a grep spawned every iteration, and parallel against single-threaded grep; no like-for-like row remains: C to D.
- **Verifier notes:** Numbers match the README and PERFORMANCE_ANALYSIS.md. Main shortcomings for the record: unequal work (non-UTF-8 lines and hidden directories skipped, so binary build output is mostly not searched), parallel vs single-threaded grep, no published grep command, pattern, version or CPU, and internally inconsistent README tables; it could fall to D if an enricher shows the target/ comparison is dominated by skipped binary content.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `workload`, `caveats`, `stars_or_usage`
- **Shortcomings recorded by:** verifier batch-104 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/yinkam/xtreme-grep/HEAD/README.md>
  - <https://raw.githubusercontent.com/yinkam/xtreme-grep/HEAD/PERFORMANCE_ANALYSIS.md>
  - <https://raw.githubusercontent.com/yinkam/xtreme-grep/HEAD/Makefile>
  - <https://raw.githubusercontent.com/yinkam/xtreme-grep/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/yinkam/xtreme-grep/HEAD/src/search/crawler.rs>
  - <https://raw.githubusercontent.com/yinkam/xtreme-grep/HEAD/src/search/default.rs>
  - <https://raw.githubusercontent.com/yinkam/xtreme-grep/HEAD/src/search/reader.rs>
  - <https://raw.githubusercontent.com/yinkam/xtreme-grep/HEAD/src/search/xtreme.rs>
  - <https://raw.githubusercontent.com/yinkam/xtreme-grep/HEAD/src/lib.rs>
  - <https://github.com/yinkam/xtreme-grep>
  - <https://github.com/yinkam/xtreme-grep/commits>
  - <https://github.com/yinkam/xtreme-grep/tree/main/src>
  - <https://github.com/yinkam/xtreme-grep/tree/main/src/search>
  - <https://crates.io/api/v1/crates/xerg>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/yinkam/xtreme-grep/HEAD/README.md>
  - <https://raw.githubusercontent.com/yinkam/xtreme-grep/HEAD/PERFORMANCE_ANALYSIS.md>
  - <https://raw.githubusercontent.com/yinkam/xtreme-grep/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/yinkam/xtreme-grep/HEAD/Makefile>
  - <https://raw.githubusercontent.com/yinkam/xtreme-grep/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/yinkam/xtreme-grep/HEAD/src/main.rs>
  - <https://raw.githubusercontent.com/yinkam/xtreme-grep/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/yinkam/xtreme-grep/HEAD/src/search/mod.rs>
  - <https://raw.githubusercontent.com/yinkam/xtreme-grep/HEAD/src/search/crawler.rs>
  - <https://raw.githubusercontent.com/yinkam/xtreme-grep/HEAD/src/search/default.rs>
  - <https://raw.githubusercontent.com/yinkam/xtreme-grep/HEAD/src/search/reader.rs>
  - <https://raw.githubusercontent.com/yinkam/xtreme-grep/HEAD/src/search/xtreme.rs>
  - <https://raw.githubusercontent.com/yinkam/xtreme-grep/HEAD/src/output/highlighter.rs>
  - <https://raw.githubusercontent.com/yinkam/xtreme-grep/HEAD/src/output/colors.rs>
  - <https://raw.githubusercontent.com/yinkam/xtreme-grep/HEAD/src/output/result.rs>
  - <https://raw.githubusercontent.com/yinkam/xtreme-grep/HEAD/src/output/mod.rs>
  - <https://raw.githubusercontent.com/yinkam/xtreme-grep/HEAD/benches/performance.rs>
  - <https://github.com/yinkam/xtreme-grep>
  - <https://crates.io/api/v1/crates/xerg>
  - <https://raw.githubusercontent.com/rust-lang/regex/master/Cargo.toml>
  - <https://raw.githubusercontent.com/rust-lang/regex/master/regex-syntax/src/hir/translate.rs>
  - <https://raw.githubusercontent.com/rust-lang/regex/master/regex-syntax/src/unicode.rs>
  - <https://raw.githubusercontent.com/rust-lang/regex/master/regex-syntax/src/hir/mod.rs>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/yinkam/xtreme-grep`) · [data/wave14/enrich/raw/github_com_yinkam_xtreme_grep.json](../../../data/wave14/enrich/raw/github_com_yinkam_xtreme_grep.json) (enrichment confidence 0.8)

</details>
