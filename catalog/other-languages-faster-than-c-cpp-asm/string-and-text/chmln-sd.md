# sd (find and replace CLI)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Strings and text](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟢 active

> Rust find-and-replace CLI (regex crate, JS/Python-style syntax); several times faster than GNU sed on regex-heavy substitutions.

| | |
|---|---|
| **Beats** | sed, both sed -E and plain sed (GNU sed implied by the \w and \+ BRE extensions in the commands; version and locale not stated) |
| **Claimed result** | README, hyperfine means: simple replacement on about 1.5 GB JSON: sed -E 2.338 s, sed 2.365 s, sd 0.997 s (about 2.35x). The regex row (sed 11.3 s vs sd 0.942 s, 11.93x) is struck: the quoted "\$1\$1" expanded to an empty string under sh -c, so sd deleted every word while sed doubled every word (issue #52). An independent 2019 run with correct quoting: sd -p 12.6 s vs GNU sed 37.5-39.3 s on 120 MB (MacBook Pro 2015 i5), about 3x. 1M lines (about 36 MB): sd -A 'foo' 125.6 ms vs sed 316.4 ms; default line-by-line sd 357.0 ms (slower than sed), a stale row from c79546a whose follow-up commit cites 106 ms vs sed 120 ms from a different run. |
| **Workload** | Replace '"' with "'" across about 1.5 GB of JSON files (\*.json), regex (\w+) -&gt; \$1\$1 on one \~55 MB JSON file (both printed to /dev/null), and literal foo -&gt; qux plus regex '(\w+) world' replacement on a 1M-line \~36 MB file comparing sd's line-by-line default (#328, 2026) and across (-A) modes with sed. |
| **Metric** | throughput |
| **Compiler and flags** | Not stated. At the 2018-12-31 benchmark commit (7ba1ac4) Cargo.toml set the release profile to opt-level = 3, lto = true; the sed build is unstated. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Adoption** | 7.4k stars; 512,307 crates.io downloads; packaged in most distributions (repology badge) |
| **Last commit** | 2026-02-25 |
| **Links** | [repository](https://github.com/chmln/sd) · [benchmark](https://github.com/chmln/sd) |

## Verdict

The README's large-file tables are 2018 hyperfine runs of sd 0.4.0-era code (commit 324fd1c) against GNU sed with no hardware, sed version or locale: 0.997 s vs 2.338 s on \~1.5 GB of JSON and 0.942 s vs 11.3 s on a 55 MB JSON, the latter with sd's replacement shell-expanded to an empty string. The only independent figure found (issue #52, 2019, MacBook Pro 2015 i5, 120 MB) is about 3x faster than GNU sed, and the 2026 1M-line table has -A mode 2.5x faster than sed on a literal while the default mode was slower at the time.

## Use it when

- Ad hoc or scripted single substitutions where you want PCRE/JavaScript-style regex (\d, \w, (?P&lt;name&gt;...), \$1) without sed's escaping, delimiter and BRE/ERE rules.
- Regex-heavy rewrites with classes and capture groups on large text or JSON files, where the Rust regex engine beats GNU sed's glibc regex (independent 2019 run: about 3x on a 120 MB JSON with (\w+) -&gt; \$1\$1).
- Literal or regex replacement across many files with -A (master) or the released 1.0.0, which process files in parallel with rayon and write each file atomically via a temp file and rename.
- Streaming stdin (for example journalctl -f | sd ...) with bounded memory on master's default line-by-line mode (README: 3 MB peak RSS vs 74 MB for -A on a 36 MB file).

## Skip it when

- Anything beyond one s///g: sed addresses and ranges, hold space, multiple -e expressions, delete/insert commands, or existing scripts that rely on POSIX BRE/ERE syntax.
- Patterns that need backreferences or look-around; the Rust regex crate does not implement them.
- Plain literal substitutions piped through stdout in the default line-by-line mode: the README table has sd 357.0 ms vs sed 316.4 ms on 1M lines, and every output line is a separate write(2) because Rust's stdout is line-buffered even when redirected.
- Many large files with -A on master: all inputs are read fully into memory and all replaced outputs are held before any file is written; the released 1.0.0 maps whole files (memory issues #96 and #154 were only closed by unreleased #328).
- When you need the behaviour the README documents from a package: crates.io and distributions ship 1.0.0 (2023-11-08), which has no line-by-line mode and no -A flag.

## How it is fast

Matching is done by the Rust regex crate (regex::bytes, 1.10.2 in Cargo.lock), a finite-automata engine with worst-case O(m\*n) search that omits backreferences and look-around, while GNU sed uses glibc's POSIX regex engine; the large regex gaps are an engine-against-engine difference whose size also depends on sed's locale, which no benchmark states. Replacement is one pass appending into a single output buffer and returns the input borrowed when nothing matches. With -A each input is read whole and multiple files are replaced in parallel with rayon; the default mode reads 8 KB chunks and runs the regex once per line, which the README puts at about 2-3x slower than -A.

## Compared with alternatives

Pick sd over RustyBox's sed applet or awkrs when the job is one regex or literal substitution and you want Rust regex syntax rather than sed or awk compatibility; inside a Rust program use the regex crate (catalogued separately), the engine sd wraps, directly.

## Integration

| | |
|---|---|
| **Form** | crate (CLI binary installed with cargo install sd; master also splits out an sd library crate and an unpublished sd-cli binary crate) |
| **Dependencies** | regex 1.10, rayon 1.8, thiserror, tempfile; clap 4.4 for the CLI (released 1.0.0 also uses memmap2) |
| **Minimum toolchain** | Rust 1.86, edition 2024 on master; Rust 1.70 for the released 1.0.0 |
| **Platforms** | any Rust target; Windows supported since 0.5.0; master adds aarch64 Linux and Windows ARM64 release builds |
| **Thread safety** | CLI tool; with -A (and in 1.0.0 in-place mode) files are processed in parallel by rayon; library thread-safety not documented |
| **Drop-in for the baseline** | partial — covers only sed's s/find/replace/g, with different regex syntax (\$1 instead of \1, no backreferences in patterns) and in-place editing whenever files are given (sed needs -i) |

## Gotchas

- Harness flaw: the README's 11.93x regex row is invalid as printed. hyperfine runs each command through sh -c, so the double-quoted "\$1\$1" expands to an empty string and sd deleted every word while sed doubled every word (open issue #52 since 2019). The measured 2018 code (324fd1c) also ran the unescape crate over each whole output, decoding JSON escapes such as \" and \n that sed left alone (fixed in 0.4.2). With correct quoting, an independent 2019 run (sd -p, 120 MB, MacBook Pro 2015 i5) measured 12.6 s vs GNU sed 37.5-39.3 s, about 3x.
- The README's line-by-line table (default sd 357.0 ms, slower than sed) was measured at commit c79546a, before the chunked-read commit fcdb8b3 in the same PR, whose message reports 106 ms vs sed 120 ms and 33 ms for -A from a different run; the README was never updated. The 0.997 s for \~1.5 GB of JSON is hard to reconcile with the 2018 code, which copied every output into a VecDeque&lt;char&gt; for the unescape pass (an inference, not reproduced). Re-running the README commands with current sd edits the inputs in place, and the \$1\$1 command empties every word of dump.json on its first warmup.
- Default line-by-line mode changes semantics: -n LIMIT applies per line although --help says per file (the limit tests all pass -A), \n and other multi-line patterns need -A, and -f w rebuilds the regex builder, dropping flags given before it (for example -f iw loses case-insensitivity) and multi-line mode.
- On master, in-place writes no longer keep the file owner: the fchown code from #326 sits in sd/src/output.rs, which lib.rs never declares as a module, so the CHANGELOG entry does not apply to the compiled binary.

## Known shortcomings

- The 1.5 GB and 55 MB tables are sd 0.4.0 runs from 2018-12-31 that no longer reproduce (since 0.6.0 the README commands rewrite their inputs in place); the current default mode is slower than sed on a literal (357.0 vs 316.4 ms); the regex wins are Rust regex against glibc regex.
- Harness flaw: the README's 11.93x regex row is invalid as printed. hyperfine runs commands through sh -c, so the double-quoted "\$1\$1" expands to an empty string: sd deleted every word while sed doubled every word (issue #52, open since 2019). The benchmarked 2018 code (324fd1c) also ran the unescape crate over the whole output, decoding JSON escapes, so its output differed from sed's (fixed in 0.4.2); 0.997 s for about 1.5 GB is hard to square with its VecDeque&lt;char&gt; pass (inference). An independent 2019 run with correct quoting gave sd -p 12.6 s against GNU sed 37.5-39.3 s on 120 MB (MacBook Pro 2015 i5), about 3x. The README's line-by-line table (357.0 ms, slower than sed) is stale, measured at c79546a before fcdb8b3 in the same PR, whose message cites 106 ms vs sed 120 ms and -A 33 ms from a different run. Default mode does one write(2) per line; -n applies per line, not per file; -f w drops earlier flags; master's in-place path drops the owner (fchown never compiled); crates.io and distributions ship 1.0.0 (2023) without -A.

## Caveats and trade-offs

First-party README numbers with no CPU, OS, sed version, locale or build flags; the 1.5 GB JSON corpus and the 55 MB dump.json are not provided. The two large-file tables were added on 2018-12-31 (commit 324fd1c; identical numbers at 7ba1ac4, Cargo version 0.4.0) and never re-run; the 2018 hyperfine command lists two commands while the table has three rows, and the current README's command lines (with --warmup 3) were rewritten after the measurement. In 2018 a file argument printed to stdout, but since sd 0.6.0 (2019-06-15) a file list implies in-place modification, so re-running the README commands with current sd rewrites the inputs (the (\w+) -&gt; \$1\$1 case doubles every word on each hyperfine iteration) and cannot reproduce the table. The line-by-line tables (2026-02-25, #328) measure unreleased master code (latest crates.io release is 1.0.0 of 2023-11-08), give no input method, and show default-mode sd slower than sed on a literal replacement (357.0 vs 316.4 ms). The large regex gaps (11.9x, 7.8x derived) compare the Rust regex crate with glibc regex, an engine difference that also depends on sed's locale. The README itself calls its syntax examples cherry-picked. [retier] The 11.93x regex row is invalid as printed (sh -c expanded "\$1\$1" to an empty string: sd deleted every word, sed doubled every word; issue #52 open since 2019). The benchmarked 2018 code (324fd1c) ran the unescape crate over the whole output, decoding JSON escapes, so its output differed from sed's (fixed in 0.4.2). The line-by-line table row (357.0 ms) is stale, measured before fcdb8b3 in the same PR. Default mode does one write(2) per line; -n applies per line; -f w drops earlier flags; master's in-place path drops the owner; crates.io and distributions ship 1.0.0 (2023) without -A.

Different syntax (JavaScript/Python-style regex, \$1 captures), not a full sed (no scripting, addresses or hold space). Default line-by-line mode keeps memory at 3 MB; across mode (-A) is faster but used 74 MB peak RSS on the 36 MB test.

## Maintenance

Active (last commit 2026-02-25) and MIT-licensed, but the README documents unreleased master while crates.io and distributions ship 1.0.0 from 2023, and its headline 11.93x regex row is invalid as printed (shell-expanded \$1\$1 made sd delete words while sed doubled them, open issue #52), with an independent rerun showing about 3x.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** README hyperfine tables compare sd with sed using printed command lines, but give no CPU, OS, sed version, locale, build flags or input data, and the two large-file tables date from 2018-12-31 (commit 324fd1c, sd 0.4.0 code); first-party, so C.
- **Verifier notes:** Numbers match the README; tier C stays. The big-file numbers are 2018 measurements of sd 0.4.0, and the printed commands now edit the input files in place with current sd, so they do not reproduce. The current default mode loses to sed on a literal replacement, and the regex wins are Rust regex against glibc regex.
- **Fields the verifier corrected:** `baseline`, `compiler_and_flags`, `workload`, `stars_or_usage`, `caveats`, `claimed_speedup`
- **Shortcomings recorded by:** verifier batch-13 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/chmln/sd>
  - <https://github.com/chmln/sd/commits>
  - <https://github.com/chmln/sd/commits/master/README.md>
  - <https://github.com/chmln/sd/tree/7ba1ac4/src>
  - <https://raw.githubusercontent.com/chmln/sd/HEAD/README.md>
  - <https://raw.githubusercontent.com/chmln/sd/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/chmln/sd/7ba1ac4/README.md>
  - <https://raw.githubusercontent.com/chmln/sd/7ba1ac4/Cargo.toml>
  - <https://raw.githubusercontent.com/chmln/sd/7ba1ac4/src/input.rs>
  - <https://raw.githubusercontent.com/chmln/sd/7ba1ac4/src/app.rs>
  - <https://raw.githubusercontent.com/chmln/sd/7ba1ac4/src/main.rs>
  - <https://crates.io/api/v1/crates/sd>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/chmln/sd/HEAD/README.md>
  - <https://raw.githubusercontent.com/chmln/sd/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/chmln/sd/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/chmln/sd/HEAD/Cargo.lock>
  - <https://raw.githubusercontent.com/chmln/sd/HEAD/sd/Cargo.toml>
  - <https://raw.githubusercontent.com/chmln/sd/HEAD/sd-cli/Cargo.toml>
  - <https://raw.githubusercontent.com/chmln/sd/HEAD/sd/src/lib.rs>
  - <https://raw.githubusercontent.com/chmln/sd/HEAD/sd/src/input.rs>
  - <https://raw.githubusercontent.com/chmln/sd/HEAD/sd/src/output.rs>
  - <https://raw.githubusercontent.com/chmln/sd/HEAD/sd/src/error.rs>
  - <https://raw.githubusercontent.com/chmln/sd/HEAD/sd/src/unescape.rs>
  - <https://raw.githubusercontent.com/chmln/sd/HEAD/sd/src/replacer/mod.rs>
  - <https://raw.githubusercontent.com/chmln/sd/HEAD/sd/src/replacer/validate.rs>
  - <https://raw.githubusercontent.com/chmln/sd/HEAD/sd/src/replacer/tests.rs>
  - <https://raw.githubusercontent.com/chmln/sd/HEAD/sd-cli/src/main.rs>
  - <https://raw.githubusercontent.com/chmln/sd/HEAD/sd-cli/src/cli.rs>
  - <https://raw.githubusercontent.com/chmln/sd/HEAD/sd-cli/tests/cli.rs>
  - <https://github.com/chmln/sd/pull/328>
  - <https://github.com/chmln/sd/pull/328/commits>
  - <https://github.com/chmln/sd/commit/fcdb8b3>
  - <https://raw.githubusercontent.com/chmln/sd/c79546a/README.md>
  - <https://raw.githubusercontent.com/chmln/sd/c79546a/sd/src/lib.rs>
  - <https://raw.githubusercontent.com/chmln/sd/c79546a/sd-cli/src/main.rs>
  - <https://raw.githubusercontent.com/chmln/sd/7ba1ac4/Cargo.toml>
  - <https://raw.githubusercontent.com/chmln/sd/7ba1ac4/src/input.rs>
  - <https://raw.githubusercontent.com/chmln/sd/7ba1ac4/src/main.rs>
  - <https://raw.githubusercontent.com/chmln/sd/7ba1ac4/src/app.rs>
  - <https://raw.githubusercontent.com/chmln/sd/7ba1ac4/src/utils.rs>
  - <https://raw.githubusercontent.com/chmln/sd/7ba1ac4/README.md>
  - <https://raw.githubusercontent.com/chmln/sd/324fd1c/src/input.rs>
  - <https://raw.githubusercontent.com/chmln/sd/324fd1c/README.md>
  - <https://github.com/chmln/sd/commit/324fd1c>
  - <https://github.com/chmln/sd/commits/324fd1c>
  - <https://crates.io/api/v1/crates/unescape/0.1.0/download>
  - <https://crates.io/api/v1/crates/sd>
  - <https://crates.io/api/v1/crates/sd-cli>
  - <https://raw.githubusercontent.com/chmln/sd/v1.0.0/Cargo.toml>
  - <https://raw.githubusercontent.com/chmln/sd/v1.0.0/src/main.rs>
  - <https://raw.githubusercontent.com/chmln/sd/v1.0.0/src/input.rs>
  - <https://raw.githubusercontent.com/chmln/sd/v1.0.0/src/replacer/mod.rs>
  - <https://github.com/chmln/sd/issues?q=is%3Aissue+slow+OR+performance+OR+memory+OR+benchmark>
  - <https://github.com/chmln/sd/issues/52>
  - <https://github.com/chmln/sd/commits/master>
  - <https://raw.githubusercontent.com/rust-lang/regex/master/README.md>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/chmln/sd`) · [data/wave14/enrich/raw/github_com_chmln_sd.json](../../../data/wave14/enrich/raw/github_com_chmln_sd.json) (enrichment confidence 0.8)

</details>
