# Miller 6 (mlr, Go rewrite of C Miller 5)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Strings and text](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `BSD-2-Clause` · 🟢 active

> Go rewrite of Miller, the header-keyed CSV/JSON record tool; beats its C predecessor 5.10.3 on CSV and multi-verb chains.

| | |
|---|---|
| **Beats** | Miller 5.10.3, the earlier C implementation of the same tool (charts label it mlr-5.10.3); the docs explicitly decline to compare with awk, sort or cut |
| **Claimed result** | Read from the 2026-02-22 charts on docs/src/performance.md (approximate, y-axis is seconds per scripts/perf/time-verbs.py, mlr-5.10.3 vs mlr-6.17.0, one-million-record files, Apple M1): then-chains of put chain-1 about 3.8 s vs 1.6 s and chain-4 about 10.2 s vs 2.15 s (about 2.4x and 4.7x, derived from chart reading); CSV verbs stats1 about 1.8 s vs 0.9 s (about 2x), sort-n about 2.9 s vs 2.5 s, sort-f about 1.7 s vs 1.4 s, tac about 1.6 s vs 1.3 s, check and tail about 0.85-0.9 s vs 0.8 s; format cats cat-csv about 1.5 s vs 0.8 s, cat-xtab about 3.15 s vs 1.1 s, cat-dkvp about 1.5 s vs 1.2 s, cat-csvlite about equal, but Miller 6 is slower on cat-nidx (about 0.9 s vs 3.2 s) and cat-json (about 6.3 s vs 8.7 s). Page text: 'CSV processing was particularly improved in Miller 6'; 'Even single-verb processing with put and stats1 was significantly faster on both platforms'; JSON 'Miller 5 did better than Miller 6 but only on Linux, not Mac'. |
| **Workload** | scripts/perf/time-verbs.py: average wall-clock time of 5 runs per case (process spawned via the shell, output to /dev/null) for mlr check, cat, tail, tac, sort -f, sort -n, stats1 and put then-chains of depth 1-4 on a one-million-record CSV made by scripts/perf/prep-perf-data.sh (example.csv repeated 100000 times, shuffled, with added fields), plus mlr cat over its CSV, CSV-lite, DKVP, NIDX, XTAB and JSON conversions. |
| **Metric** | throughput |
| **Hardware** | MacBook Air with Apple M1 (early 2026 runs, charts dated 2026-02-22); the Linux machine mentioned in the notes is not described |
| **Compiler and flags** | Not stated for the 2026 runs: the Go 1.15.15, 1.16.12, 1.17.5 and 1.18beta1 list is from late-2021 benchmarking; how the mlr-5.10.3 binary was built is not stated (the Miller 5.10.3 autotools build uses AM_CFLAGS -Wall -std=gnu99 plus autoconf's default -g -O2 per the c/Makefile.am link-line comment, not -O3) |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Why it wins** | docs/src/cpu.md: Miller 6 runs the input reader (two goroutines), each verb in a then-chain and the writer as concurrent goroutines connected by channels, so deep chains use several cores (typically 250-350 percent CPU); the page gives no mechanism for the CSV I/O gain. |
| **Adoption** | 10.0k stars |
| **Last commit** | 2026-09-29 |
| **Links** | [repository](https://github.com/johnkerl/miller) · [benchmark](https://raw.githubusercontent.com/johnkerl/miller/HEAD/docs/src/performance.md) |

## Verdict

First-party wall-clock times read from PNG charts dated 2026-02-22 (Apple M1 MacBook Air, average of 5 shell-launched runs per case by scripts/perf/time-verbs.py, one-million-record files): Miller 6.17.0 (Go) against Miller 5.10.3 (C, build flags not stated), put chain-1 about 1.6 s vs 3.8 s, chain-4 about 2.15 s vs 10.2 s, stats1 about 0.9 s vs 1.8 s, CSV cat about 0.8 s vs 1.5 s, but NIDX cat about 3.2 s vs 0.9 s and JSON cat about 8.7 s vs 6.3 s. The baseline is Miller's own C predecessor, not awk, cut or sort, and the big wins come from running the pipeline on several cores.

## Use it when

- Multi-step transformations of header-keyed CSV, TSV or JSON in a shell pipeline (cut, sort, stats1, put or filter joined with then) on a machine with idle cores, where reader, verbs and writer can run in parallel.
- Replacing Miller 5: in the 2026-02-22 M1 run, then-chains of put ran about 2.4x (one put) to 4.7x (four puts) faster, stats1 about 2x, CSV cat about 1.9x and XTAB cat about 2.9x (read from charts).
- Format conversion between CSV, TSV, JSON, DKVP and XTAB where header handling, quoting and heterogeneous records matter more than peak throughput.
- When one dependency-free binary must run on Linux, macOS and Windows (apt, yum, snap, brew, port, choco, winget and scoop packages per the README).

## Skip it when

- Single fixed operations on big files: on the page's own 40-million-record cell_towers.csv, mlr cut took 1m27.6s real and 3m8.9s user against 1m8.3s real and 1m7.1s user for the M1 laptop's system cut; in issue #1527 Miller 6.11.0 cut on a 5 GB CSV was killed after 2:15.86 while qsv select took 3.988 s (6.12.0 finished in 12:45.40).
- JSON or NIDX heavy work if you still have Miller 5: in the 2026-02-22 run Miller 6.17.0 took about 8.7 s vs 6.3 s on JSON cat and about 3.2 s vs 0.9 s on NIDX cat.
- Data larger than RAM through non-streaming verbs: sort and tac keep every record in memory and do not spill to disk (sort -nf peaked at 1306 MB RSS on the one-million-record CSV after the June 2026 work).
- Core-starved settings (single-CPU containers, many concurrent mlr processes, GOMAXPROCS=1): the chain advantage depends on spare cores, and Miller 6 spends more total CPU than single-threaded C tools.
- Peak CSV throughput: catalogued tools such as qsv, xan, zsv, tsv-utils, hck and tuc are built for speed on fixed operations, and the maintainer says xsv is known to be faster and Miller makes no claim to beat it.

## How it is fast

Miller 6 runs the reader as two goroutines (byte reading and record building), each verb of the then-chain as its own goroutine and the writer as another, connected by channels that pass batches of records (--records-per-batch); C Miller 5 runs the whole chain on one core. A four-put chain therefore spreads over several cores (cpu.md: at most 250-350 percent CPU for deep chains), which explains most of the 4.7x chain-4 gap, and even a single verb overlaps parsing, the verb and formatting. The June 2026 work cut heap allocations per record and field (lazy per-record hashing, slab allocation of record fields, writer-buffer reuse, DSL stack-frame pooling and copy elision). The docs give no mechanism for the CSV reader gain over Miller 5.

## Compared with alternatives

Pick Miller when you need format-aware, header-keyed processing across CSV, TSV, JSON and DKVP with a DSL and multi-verb chains in one binary. For a single fixed operation the siblings are faster: hck and tuc beat cut by about 4.6-6.3x and 5.3x, eBay tsv-utils beats awk and cut, while Miller's own page shows it slower than system cut.

## Integration

| | |
|---|---|
| **Form** | static binary (CLI); Go module github.com/johnkerl/miller/v6, executable built from cmd/mlr |
| **Dependencies** | none at runtime (README: zero runtime dependencies); building needs a Go toolchain |
| **Minimum toolchain** | Go 1.26.0 per go.mod at HEAD (go.mod at v6.17.0, the version in the 2026-02-22 charts, says go 1.24.0) |
| **Platforms** | Linux, macOS and Windows (distribution packages listed in the README); all published 2026 timings are from one Apple M1 MacBook Air |
| **Thread safety** | Not applicable to a CLI; internally one goroutine per reader stage, verb and writer, with core use controlled by GOMAXPROCS |
| **Drop-in for the baseline** | partial — same mlr command and verb set as Miller 5, but Miller 6 changed some flags, type handling and DSL behaviour (documented list of changes from Miller 5); not a drop-in for awk, cut or sort |

## Gotchas

- Wall clock hides extra CPU: all Miller 5 versus Miller 6 numbers are elapsed time against single-threaded C, and the charts give no user time. The page's one user-time sample (mlr cut 3m8.9s user vs system cut 1m7.1s user on the same file) shows Miller 6 using about 2.8x the CPU of a C tool for the same column extraction (derived from page data).
- Harness: scripts/perf/time-verbs.py launches each case through the shell with output to /dev/null, averages 5 runs, and neither checks the exit status nor compares output between versions, so a failing or semantically different run would still be timed. The Miller 5 binary's build (autotools default -g -O2) and the Go compiler version for the 2026 runs are not stated.
- Do not mix the page's two runs: the June 2026 table is best-of-five for 6.18.1 versus 6.19.0, while the 2026-02-22 charts average five runs for 5.10.3 through 6.17.0. CSV cat was 0.62 s 'before' in June against about 0.8 s for 6.17.0 in February, so June figures cannot be set against the Miller 5 points.
- Regressions inside Miller 6: NIDX cat went from about 0.9 s at 6.0.0 to 2.7 s at 6.8.0 and 3.2 s at 6.17.0 in the same chart, and 6.0.0 had sort -n at about 6 s and JSON cat at about 16 s before later fixes. Issue #1409 reports mlr count on a 5 GB CSV killed while wc -l finished in 37.9 s; the maintainer closed it saying slower-than-wc is expected.

## Known shortcomings

- 2026-02-22 PNG charts (mlr 5.10.3 C vs 6.17.0 on an M1): chain-4 about 10.2 vs 2.15 s and stats1 about 2x, but slower on cat-nidx (about 0.9 vs 3.2 s) and cat-json (about 6.3 vs 8.7 s); the chain wins are multicore goroutines vs single-threaded C; Miller 5's default build is -g -O2, not -O3; the same page shows mlr cut slower than system cut (87.6 vs 68.3 s).
- Timings are wall clock only; the page's one user-time sample (mlr cut 3m8.9s user vs system cut 1m7.1s) shows Miller 6 using about 2.8x the CPU of a C tool. time-verbs.py never checks exit status or compares output between versions. NIDX cat regressed within 6.x (0.9 s to 3.2 s). The June 2026 table is a separate best-of-5 run and cannot be compared with the Miller 5 points. Issues #1527 and #1409: on a 5 GB CSV, mlr cut was killed (qsv 3.988 s) and mlr count was killed.

## Caveats and trade-offs

First-party, numbers only in PNG charts (values read approximately), one M1 laptop, average of 5 runs including process startup. Miller 6 is not uniformly faster: in the same 2026-02-22 run it is about 3.5x slower on NIDX cat and about 1.4x slower on JSON cat than Miller 5.10.3, and the page says Miller 5 beat Miller 6 on JSON on Linux. The large then-chain wins come from Miller 6 spreading reader, verbs and writer over several cores against single-threaded C Miller 5, not from Go codegen. Miller 5's build for these runs is unstated and its default autotools build is -g -O2, not the -O3 wave 14 asks for. The 'Before/After' June 2026 tables and the 2026-06-20 charts compare Miller 6.18.1 with 6.19.0 only; their faster numbers (for example chain-4 about 0.96 s) come from a separate run and must not be compared with the Miller 5 points (cross-run). The same page times system cut (C) at 1m8.3s real against mlr cut at 1m27.6s real (3m8.9s user) on a 40-million-record CSV, so Miller 6 is slower than cut there, though the docs say such comparisons are not apples-to-apples. Miller 5 is a same-tool predecessor, not the C incumbent (awk, cut, sort) most developers use. [retier] Wall clock only: the page's one user-time sample (mlr cut 3m8.9s user vs system cut 1m7.1s) shows Miller 6 using about 2.8x the CPU of a C tool. time-verbs.py never checks exit status or compares output between versions; NIDX cat regressed within 6.x (0.9 s to 3.2 s); the June 2026 table is a separate best-of-5 run not comparable with the Miller 5 points. Issues #1527 and #1409: on a 5 GB CSV, mlr cut and mlr count were killed (qsv 3.988 s).

Miller 6 is not fully backward compatible with Miller 5 (a documented list of changes). Parallelism is tied to the number of verbs in the chain, so a single simple verb gains nothing. Peak RSS on the million-line CSV `cat` was 379 MB before and 180 MB after the June 2026 allocation work (Miller 6 versus itself).

## Maintenance

Actively maintained (last commit 2026-09-29, 10.0k stars, packaged by the major Linux distributions, Homebrew and Windows package managers) and BSD-2-Clause, but the speed evidence is first-party, chart-only and against its own single-threaded C predecessor, so read it as 'the Go rewrite wins on CSV and deep chains through pipelining' rather than as Go beating C.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification D, tier now C.
- **Tier reason:** Upgraded from D: the 2026-02-22 PNG charts on the performance page plot wall-clock times for mlr-5.10.3 (C) against mlr-6.0.0 to 6.17.0 (Go) on an Apple M1 MacBook Air, from the public script scripts/perf/time-verbs.py; first-party, numbers only readable from charts, and the Go version and the Miller 5 build flags for these runs are unstated, so not A.
- **Verifier notes:** Record said the charts were unreadable; I read the 2026-02-22 PNGs and they hold Miller 5.10.3 vs 6.x times, so the tier rises D to C (verdict confirm with upgrade). Shortcomings: chart-only first-party numbers, Miller 6 slower on NIDX and JSON, chain wins are multicore vs single-threaded, Miller 5 build unstated (default -O2), slower than system cut on the page's cell_towers example. License BSD-2-Clause, 10.0k stars, last commit 2026-09-29 confirmed.
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `hardware`, `compiler_and_flags`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-94 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/johnkerl/miller/HEAD/docs/src/performance.md>
  - <https://raw.githubusercontent.com/johnkerl/miller/HEAD/docs/src/cpu.md>
  - <https://raw.githubusercontent.com/johnkerl/miller/HEAD/docs/src/perf/2026-02-22-verbs.png>
  - <https://raw.githubusercontent.com/johnkerl/miller/HEAD/docs/src/perf/2026-02-22-cats.png>
  - <https://raw.githubusercontent.com/johnkerl/miller/HEAD/docs/src/perf/2026-02-22-chains.png>
  - <https://raw.githubusercontent.com/johnkerl/miller/HEAD/docs/src/perf/timings-2026-06-20-verbs.png>
  - <https://raw.githubusercontent.com/johnkerl/miller/HEAD/docs/src/perf/timings-2026-06-20-cats.png>
  - <https://raw.githubusercontent.com/johnkerl/miller/HEAD/docs/src/perf/timings-2026-06-20-chains.png>
  - <https://raw.githubusercontent.com/johnkerl/miller/HEAD/scripts/perf/time-verbs.py>
  - <https://raw.githubusercontent.com/johnkerl/miller/HEAD/scripts/perf/prep-perf-data.sh>
  - <https://raw.githubusercontent.com/johnkerl/miller/v5.10.3/c/Makefile.am>
  - <https://raw.githubusercontent.com/johnkerl/miller/v5.10.3/configure.ac>
  - <https://raw.githubusercontent.com/johnkerl/miller/HEAD/LICENSE.txt>
  - <https://github.com/johnkerl/miller>
  - <https://github.com/johnkerl/miller/commits>
- **Sources the enricher read:**
  - <https://github.com/johnkerl/miller>
  - <https://raw.githubusercontent.com/johnkerl/miller/HEAD/README.md>
  - <https://raw.githubusercontent.com/johnkerl/miller/HEAD/LICENSE.txt>
  - <https://raw.githubusercontent.com/johnkerl/miller/HEAD/go.mod>
  - <https://raw.githubusercontent.com/johnkerl/miller/v6.17.0/go.mod>
  - <https://raw.githubusercontent.com/johnkerl/miller/HEAD/docs/src/performance.md>
  - <https://raw.githubusercontent.com/johnkerl/miller/HEAD/docs/src/cpu.md>
  - <https://raw.githubusercontent.com/johnkerl/miller/HEAD/docs/src/new-in-miller-6.md>
  - <https://raw.githubusercontent.com/johnkerl/miller/HEAD/docs/src/streaming-and-memory.md>
  - <https://raw.githubusercontent.com/johnkerl/miller/HEAD/docs/src/reference-main-flag-list.md>
  - <https://raw.githubusercontent.com/johnkerl/miller/HEAD/scripts/perf/time-verbs.py>
  - <https://raw.githubusercontent.com/johnkerl/miller/HEAD/scripts/perf/prep-perf-data.sh>
  - <https://raw.githubusercontent.com/johnkerl/miller/HEAD/scripts/perf/chain-1.mlr>
  - <https://raw.githubusercontent.com/johnkerl/miller/HEAD/docs/src/perf/2026-02-22-verbs.png>
  - <https://raw.githubusercontent.com/johnkerl/miller/HEAD/docs/src/perf/2026-02-22-cats.png>
  - <https://raw.githubusercontent.com/johnkerl/miller/HEAD/docs/src/perf/2026-02-22-chains.png>
  - <https://github.com/johnkerl/miller/issues?q=is%3Aissue+performance+OR+slow>
  - <https://github.com/johnkerl/miller/issues/1527>
  - <https://github.com/johnkerl/miller/issues/1409>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/johnkerl/miller`) · [data/wave14/enrich/raw/github_com_johnkerl_miller.json](../../../data/wave14/enrich/raw/github_com_johnkerl_miller.json) (enrichment confidence 0.75)

</details>
