# fastgrep (Rust grep)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Strings and text](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0 OR MIT` · 🟢 active

> Rust parallel grep with a lazy on-disk trigram index; beats single-threaded GNU grep 3.12 on recursive searches by using every core.

| | |
|---|---|
| **Beats** | GNU grep 3.12 (C) |
| **Claimed result** | README benchmark table (warm trigram index, LC_ALL=C): -rn 'fn main' 8.82 ms vs GNU grep 32.99 ms (3.74x); -rc 'use ' 8.55 ms vs 84.75 ms (9.91x); -rni error 37.49 ms vs 82.57 ms (2.20x); -rn 'impl\s+Drop' 45.24 vs 73.43 (1.62x); very sparse SubscriptionManager 5.41 vs 39.35 (7.28x); single file 3.70 vs 5.21 (1.41x); but -rl 'fn main' 7.50 ms vs GNU grep 7.12 ms (0.95x, GNU grep faster). Scaling: 1.48x at 50 files, 2.43x at 200, 3.08x at 500. |
| **Workload** | Recursive searches over a generated corpus of 200 files x 5,000 lines of Rust-like source (sparse and dense matches, case-insensitive, regex, single 100k-line file) and a scaling test of 50 to 500 files. |
| **Metric** | latency |
| **Hardware** | Apple M2 Max (12 logical CPUs), 32 GB, macOS 27.0.1 |
| **Compiler and flags** | fastgrep 0.1.9 at commit 5094623, Rust 1.99.0, repository release profile: opt-level = "s", LTO, codegen-units 1, panic = abort, stripped; Criterion 0.8.2, one subprocess per iteration with output captured in memory, warm filesystem cache, LC_ALL=C, default thread counts. GNU grep 3.12 is Homebrew's ggrep (build flags not stated). |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Why it wins** | README: parallel by default across all CPU threads, lazy trigram index that skips non-matching files on repeat searches, SIMD-accelerated literal search. |
| **Adoption** | 2 stars; crates.io 431 downloads (113 recent), current version 0.1.10 |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/awnion/fastgrep) · [benchmark](https://github.com/awnion/fastgrep/blob/main/docs/benchmarks/README.md) |

## Verdict

Criterion 0.8.2 on an Apple M2 Max (12 logical CPUs), macOS 27.0.1, LC_ALL=C, warm page cache, with process start-up and captured output in every sample. fastgrep 0.1.9 (Rust 1.99.0, opt-level "s", LTO) ran on 12 threads against single-threaded Homebrew GNU grep 3.12 (build flags unstated) over an 84.9 MB generated corpus (200 files x 5,000 lines; size derived from benches/corpus.rs). fastgrep was 1.41x to 9.91x faster on 6 of 7 queries (e.g. -rn 'fn main' 8.82 vs 32.99 ms; -rc 'use ' 8.55 vs 84.75 ms), and GNU grep won -rl (7.12 vs 7.50 ms).

## Use it when

- An agent or editor integration repeating selective literal searches (identifiers, error strings) over the same large tree, where a warm index can skip most files.
- Recursive -rn or -rc searches over hundreds of files on a multi-core machine, where GNU grep's single thread is the bottleneck.
- Tooling that wants JSON Lines output and guard rails against multi-GB blobs and minified one-line files.
- Literal search in a single file larger than 4 MiB, which is split across threads.

## Skip it when

- Scripts written for GNU grep's default BRE: `foo\|bar`, `\(x\)`, `a\+` and `\{2\}` are literals or different operators in Rust regex syntax, and back-references are unsupported.
- Regexes with an optional character after the literal prefix (`colou?r`, `https?://`, `ab*c`) under -c, on files over 4 MiB, or with a warm index: lines are silently missed (see gotchas).
- Output that must be deterministic (diffs, golden tests), or logs over 100 MiB, which are skipped by default.
- One-off searches in many fresh directories: the first recursive search builds the index (44.6 ms vs 7.4 ms with --no-index on a 14 MB corpus; 322 ms vs 11 ms on a 165.6 MiB Linux corpus) and the cache can grow to 2 GiB.
- Low-core or -j1 environments, where the main advantage (parallelism) disappears.

## How it is fast

Two to four walker threads feed file paths through bounded kanal channels to one search thread per logical CPU. Each worker reads small files into a reused buffer and mmaps files over 256 KiB, then searches literals with memchr::memmem (SIMD substring search). Regexes run through a literal-prefix memmem candidate filter before regex-crate verification, and single files over 4 MiB are split at newlines across all threads. A lazy trigram index (trigram to sorted file-ID postings, bitcode-serialized under the OS cache directory, invalidated by mtime and size) lets repeat searches skip unchanged files that lack a required trigram, but only when the candidates are under 90% of indexed files.

## Compared with alternatives

Pick fastgrep over xerg (compared against an unnamed, probably BSD system grep) or zrep (numbers known only from search snippets) when you want GNU-grep flag compatibility, JSON output and a public Criterion harness against a named GNU grep 3.12. For general code search, the regex-crate-based ripgrep is the more mature parallel option, and fastgrep publishes no comparison with it.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | memchr, regex, memmap2, kanal, bitcode, serde, serde_json, clap, dirs, itoa |
| **Minimum toolchain** | Rust 1.99 (edition 2024) |
| **Platforms** | Linux x86-64 and arm64 (static musl release archives, CI on Ubuntu 24.04/26.04 and Debian 13), macOS Apple Silicon; Intel macOS source-only and untested in CI; Windows not documented |
| **Thread safety** | CLI tool; workers share one mutex-guarded stdout writer and flush per-file buffers, so lines from one file stay together but the file order varies. Library thread-safety guarantees are not documented. |
| **Drop-in for the baseline** | partial — installs as `grep` and accepts most GNU grep flags, but its regex syntax is not GNU BRE, -G/-P/-z/-R/--binary-files are missing, output order is nondeterministic, and it skips files over 100 MiB and truncates long lines by default |

## Gotchas

- Correctness bug in src/pattern.rs extract_literal_prefix: it keeps the character before a `?`, `*` or `{` quantifier, so `colou?r` gets the required prefix "colou" and `https?://` gets "https". That prefix drives the warm-index file filter (required_trigrams), the -c count path (count_matches) and the over-4-MiB parallel chunk path (collect_prefix_accelerated), all of which only look at lines containing the prefix. Lines with only "color" or "http://" are silently missed, even though GNU grep and fastgrep's own cold streaming path find them, so a first run and a later run can disagree. The benchmark patterns are unaffected.
- The regex dialect is the Rust regex crate with unicode(false): GNU BRE escapes become literals (`grep 'foo\|bar'` silently matches nothing), and `.`, `\w` and -i work on bytes and ASCII only. The harness had to pass `impl\s\+Drop` to GNU grep and `impl\s+Drop` to fastgrep.
- The index trusts mtime (ns) plus size: a file whose content changed but whose mtime was restored with the same size (cp -p, rsync -t, tar extraction) is skipped as non-matching until more than 10% of records go stale. Index files live under \~/.cache/fastgrep/trigram (or \~/Library/Caches) and are evicted LRU only past 2 GiB.
- Harness: every fastgrep row runs one search thread per logical CPU (12) plus 2-4 walkers against single-threaded GNU grep. That includes the 'Single file (100k lines)' row, which the bench source calls a raw speed comparison, but its 8.7 MB file (derived from benches/corpus.rs) is above the 4 MiB parallel-chunk threshold. The project's own Linux thread sweep shows the effect of threads: -j1 vs -j12 is 22.80 vs 12.64 ms for a no-index literal and 75.14 vs 17.92 ms for a regex count. No -j1 run against GNU grep is published, and the warm-index default is slower than --no-index in 4 of the 5 indexed rows.

## Known shortcomings

- The gain is mainly 12 threads against single-threaded GNU grep; --no-index beats indexed mode in 4 of 5 rows; tiny start-up-dominated corpus; GNU grep wins -rl; Homebrew ggrep build flags unstated and the Rust side is built at opt-level s; 2 stars.
- Correctness bug in src/pattern.rs extract_literal_prefix: it keeps the character before a ?, \* or { quantifier, so colou?r gets the required prefix 'colou' and https?:// gets 'https'; the prefix drives the warm-index file filter, the -c count path and the over-4-MiB parallel chunk path, which only look at lines containing it, so lines with only 'color' or 'http://' are missed. The win is mostly 12-thread parallelism against single-threaded GNU grep on a small synthetic corpus (runs of 4-85 ms including start-up); --no-index is faster than the default warm-index mode in 4 of 5 indexed rows, and GNU grep wins -rl 'fn main' (7.12 vs 7.50 ms).

## Caveats and trade-offs

Very new (crate first published 2026-03-04), first-party numbers on a small synthetic corpus (about 1M lines; runs of 4-85 ms that include process start-up). The win is mostly 12-thread parallelism against single-threaded GNU grep: the --no-index mode is faster than the default warm-index mode in 4 of the 5 indexed rows (e.g. 7.31 vs 8.82 ms on 'fn main', 7.64 vs 8.55 ms on 'use '), and the index helps only on the very sparse query (5.41 vs 6.30 ms); every file contains 'fn main', 'use ' and 'impl Drop', so the index cannot skip files for them. No per-thread or single-threaded comparison is published, so no faster per-byte scan is shown (literal and regex search come from the memchr and regex crates). GNU grep wins -rl (7.12 vs 7.50 ms). fastgrep is built at opt-level s (size), not a speed-tuned build, while GNU grep is a Homebrew bottle with unstated flags. Deliberate behaviour differences (100 MiB file-size limit, 15000-byte line truncation, unordered parallel output) change semantics versus GNU grep. [retier] Very new (crate first published 2026-03-04), first-party numbers on a small synthetic corpus (about 1M lines; runs of 4-85 ms including process start-up). The win is mostly 12-thread parallelism against single-threaded GNU grep: --no-index is faster than the default warm-index mode in 4 of the 5 indexed rows and the index helps only on the very sparse query; GNU grep wins -rl 'fn main' (7.12 vs 7.50 ms). Correctness bug in src/pattern.rs extract_literal_prefix: it keeps the character before a ?, \* or { quantifier, so colou?r gets the required prefix 'colou' and https?:// gets 'https'; that prefix drives the warm-index file filter, the -c count path and the over-4-MiB parallel chunk path, which only look at lines containing it, so lines with only 'color' or 'http://' are missed. The benchmarked patterns do not use those quantifiers.

Output order is non-deterministic (multi-threaded); deliberate deviations from GNU grep (binary files, long lines). Index cache stored under the OS cache directory and invalidated by mtime and size. Not every GNU grep flag implemented.

## Maintenance

Active but young (crate first published 2026-03-04; work in bursts, the latest on 2026-10-05/06; v0.1.10, 2 stars, MIT OR Apache-2.0) and copyable, but the prefix-extraction bug in the index, -c and large-file paths means it should not replace grep in scripts until that is fixed.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party Criterion run with public bench code (benches/grep_bench.rs, bench_baseline/baseline_bench.rs, benches/corpus.rs), Rust 1.99.0, the release profile flags and an Apple M2 Max all stated, but GNU grep is a Homebrew ggrep 3.12 bottle with unstated build flags, so the C side's build is not documented and the entry stays C.
- **Verifier notes:** All README numbers match docs/benchmarks/README.md and bench_baseline/baseline.md; GNU grep and fastgrep run identical command lines in the harness. Shortcomings: gain is parallelism (12 threads vs single-threaded grep), index mode usually slower than --no-index, tiny corpus with start-up dominated ms timings, GNU grep wins -rl, GNU grep build flags unstated, 2 stars.
- **Fields the verifier corrected:** `benchmark_url`, `compiler_and_flags`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-12 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/awnion/fastgrep/HEAD/README.md>
  - <https://github.com/awnion/fastgrep>
  - <https://github.com/awnion/fastgrep/commits/main>
  - <https://raw.githubusercontent.com/awnion/fastgrep/HEAD/docs/benchmarks/README.md>
  - <https://raw.githubusercontent.com/awnion/fastgrep/HEAD/bench_baseline/baseline.md>
  - <https://raw.githubusercontent.com/awnion/fastgrep/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/awnion/fastgrep/HEAD/bench_baseline/baseline_bench.rs>
  - <https://raw.githubusercontent.com/awnion/fastgrep/HEAD/benches/grep_bench.rs>
  - <https://crates.io/api/v1/crates/fastgrep>
- **Sources the enricher read:**
  - <https://github.com/awnion/fastgrep>
  - <https://github.com/awnion/fastgrep/commits/main>
  - <https://github.com/awnion/fastgrep/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/awnion/fastgrep/HEAD/README.md>
  - <https://raw.githubusercontent.com/awnion/fastgrep/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/awnion/fastgrep/HEAD/rust-toolchain.toml>
  - <https://raw.githubusercontent.com/awnion/fastgrep/HEAD/docs/benchmarks/README.md>
  - <https://raw.githubusercontent.com/awnion/fastgrep/HEAD/docs/benchmarks/results.json>
  - <https://raw.githubusercontent.com/awnion/fastgrep/HEAD/bench_baseline/baseline.md>
  - <https://raw.githubusercontent.com/awnion/fastgrep/HEAD/bench_baseline/baseline_bench.rs>
  - <https://raw.githubusercontent.com/awnion/fastgrep/HEAD/benches/grep_bench.rs>
  - <https://raw.githubusercontent.com/awnion/fastgrep/HEAD/benches/corpus.rs>
  - <https://raw.githubusercontent.com/awnion/fastgrep/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/awnion/fastgrep/HEAD/src/pattern.rs>
  - <https://raw.githubusercontent.com/awnion/fastgrep/HEAD/src/searcher.rs>
  - <https://raw.githubusercontent.com/awnion/fastgrep/HEAD/src/trigram.rs>
  - <https://raw.githubusercontent.com/awnion/fastgrep/HEAD/src/cli.rs>
  - <https://raw.githubusercontent.com/awnion/fastgrep/HEAD/src/output.rs>
  - <https://raw.githubusercontent.com/awnion/fastgrep/HEAD/src/threadpool.rs>
  - <https://raw.githubusercontent.com/awnion/fastgrep/HEAD/src/walker.rs>
  - <https://raw.githubusercontent.com/awnion/fastgrep/HEAD/src/bin/grep.rs>
  - <https://raw.githubusercontent.com/awnion/fastgrep/HEAD/src/bin/fastgrep.rs>
  - <https://raw.githubusercontent.com/awnion/fastgrep/HEAD/src/bin/common/mod.rs>
  - <https://raw.githubusercontent.com/awnion/fastgrep/HEAD/GNU_GREP_COMPAT.md>
  - <https://raw.githubusercontent.com/awnion/fastgrep/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/awnion/fastgrep/HEAD/ARCHITECTURE.md>
  - <https://raw.githubusercontent.com/awnion/fastgrep/HEAD/docs/profiling/2026-10-05/README.md>
  - <https://raw.githubusercontent.com/awnion/fastgrep/HEAD/docs/index-performance.md>
  - <https://raw.githubusercontent.com/microsoft/tgrep/main/README.md>
  - WebSearch: fastgrep awnion "drop-in replacement for GNU grep" trigram index AI agents (snippet of docs.rs/crate/fastgrep 0.1.8: earlier README claimed '2-12x faster than GNU grep across common workloads')
  - WebSearch: tgrep "Trigram-indexed grep" github
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/awnion/fastgrep`) · [data/wave14/enrich/raw/github_com_awnion_fastgrep.json](../../../data/wave14/enrich/raw/github_com_awnion_fastgrep.json) (enrichment confidence 0.8)

</details>
