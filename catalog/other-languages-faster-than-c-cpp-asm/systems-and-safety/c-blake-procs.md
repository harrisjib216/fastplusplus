# procs (c-blake, Nim ps, pgrep and pkill replacement: pd, pf, pk)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Systems and safety](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Nim` · `ISC` · 🟢 active

> Nim /proc query toolkit whose pd/pf/pk read fewer /proc files than procps ps, pgrep and pkill.

| | |
|---|---|
| **Beats** | procps ps ('/bin/ps ax'), pgrep and pkill (C) |
| **Claimed result** | README footnote: pd -f%p %c 2.8576 ms +- 0.0070 vs /bin/ps ax 5.0281 ms +- 0.0063 (README says roughly 2X and 'about 57% the run-time'; 1.76x derived from page data); with process typology and highlights on, pd takes 3.9739 ms +- 0.0044, 1.27X faster than stock ps; pgrep and pkill are (5.025 +- 0.015)X and (5.745 +- 0.016)X slower than pf and pk for an 'average process' on a 4-core and a 20-core CPU. bench.sh comments (overhead subtracted): i7-6700K pf -e1 init 1014.1 us, pf -e1 with no match 2060.1 us, pgrep -x init 7724 us; i7-1370P 582.7 us, 1345.7 us and 5539.6 us; bench.sh calls this 'up to' 7.617x and 9.507x. The 'up to' figures compare pf stopping at the first /proc entry (init) with pgrep's full scan; the equal-work full-scan rows (pf with no match vs pgrep) give 3.75x and 4.12x (derived from page data), and the README 5.025X/5.745X figures are pgrep's time divided by the mean of pf's first-hit and no-match times (derived from page data). |
| **Workload** | Listing all processes with a minimal format (pid and command) to /dev/null, and finding a process by name over roughly 200 to 320 processes (pf -e1 vs pgrep -x), measured with the author's tim/tails tools under chrt 99 taskset. |
| **Metric** | latency (wall time) |
| **Hardware** | i7-6700K (no HT, 4.7 GHz) and i7-1370P in bench.sh; the machine for the README ps timings is not named |
| **Compiler and flags** | Not stated for the benchmark; README build line is 'nim c -d:release --path:../cligen procs' (C backend compiler version not stated); procps version not stated |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Why it wins** | README: 'tries hard not to make unnecessary system calls', for example only opening /proc/PID/stat for a pid-and-command format while procps ps also opens and parses /proc/PID/status (the author says this makes pd roughly 2X faster). |
| **Adoption** | 25 stars |
| **Last commit** | 2026-07-04 |
| **Links** | [repository](https://github.com/c-blake/procs) · [benchmark](https://raw.githubusercontent.com/c-blake/procs/HEAD/bench.sh) |

## Verdict

bench.sh (added 2025-04-01; the author's tim tool, chrt 99 taskset -c 2, wrapper overhead subtracted): on an i7-6700K with about 196 processes, pf -e1 with no match took 2.06 ms vs 'pgrep -x init' at 7.72 ms (3.75x); on an i7-1370P with about 323 processes, 1.35 ms vs 5.54 ms (4.12x). Stopping at PID 1 gives the 'up to' 7.6x and 9.5x. The README footnote times 'pd -f%p %c' at 2.86 ms vs '/bin/ps ax' at 5.03 ms (1.76x, different output, machine unnamed), and 3.97 ms (1.27x) with default kinds and highlights. Nim, C compiler, flags and procps versions are unstated.

## Use it when

- Scripts or interactive use on Linux that call pgrep/pkill/pidof often, especially 'does a process named X exist' checks (pf -e), where the first-match exit and stat-only reads cut wall time by 4x or more
- Killing runaway processes on an overloaded box: pk sends signals as each match is found instead of after a full scan
- Custom ps/top-style reports (merged kernel threads, per-category colours, diffs every N seconds with pd -d1) where you would otherwise post-process ps output
- Nim programs that want a typed /proc reader (procs is also a library) that reads only the fields asked for

## Skip it when

- Anything that is not Linux /proc: no BSD, macOS or Windows support
- Scripts that rely on exact pgrep/ps semantics: pf has no -x exact mode (use '^name\$'), patterns are PCRE not POSIX ERE, and pd's formats differ from ps's
- Rich listings: speed comes from reading less, so formats that need status, cmdline, io or smaps lose most of the gap (the README shows pd at 1.27x over ps once its default kinds and highlights are on, and says there are configurations where ps can be faster)
- Locked-down or minimal systems: it needs Nim and cligen to build, PCRE1 (libpcre, loaded by Nim's std/nre) at run time, and a config tree; the author calls it a work in progress with 'surely many bugs'

## How it is fast

Demand-driven /proc reads: each format code or filter declares the ProcFields it needs, and needs() maps them to the minimal set of files. A '%p %c' listing or a name match therefore opens only /proc/PID/stat, while procps also opens and parses status and, for pgrep, cmdline. It reuses one IO buffer for every readFile and parses stat in place with memory slices. pf/pk act 'ASAP' as each process matches, and --exist returns at the first match, whereas procps pgrep/pkill read and select all processes before acting.

## Compared with alternatives

Among the catalogued siblings it is the only process-table tool. It shares the 'issue fewer syscalls' approach of the author's cligen/dents walker and bu tools (dups, mk1), and like hexdump-rs or neosmart tac it replaces a coreutils-era C utility. Pick it when pgrep/pkill/ps latency or ASAP signalling matters on Linux and you can live with different option semantics.

## Integration

| | |
|---|---|
| **Form** | module plus CLI binary (nimble package procs; pd, pf, pk, pw, sc are symlinks) |
| **Dependencies** | cligen &gt;= 1.10.0; Nim stdlib including std/nre, which loads the PCRE1 shared library at run time; optional config files (configs/cb0) |
| **Minimum toolchain** | Nim &gt;= 1.6.0 per procs.nimble, built with --threads:on (procs.nims); C backend compiler version not documented |
| **Platforms** | Linux only (/proc); README reports Gentoo, Debian and Android Termux |
| **Thread safety** | not documented; the library parses every /proc file through one global shared buffer ('var buf ... shared IO buffer for all readFile'), so do not call its readers from several threads |
| **Drop-in for the baseline** | partial: pf/pk take options 'most similar to pgrep' and default to SIGTERM like pkill, but matching is unanchored PCRE on comm with no -x; pd is not ps-compatible (user-defined formats and config files) |

## Gotchas

- bench.sh never times pkill, only pgrep. The README's '(5.745±0.016)X slower than pk' is the i7-1370P pgrep row divided by the mean of pf's first-hit and no-match times (derived from page data). That 'average process' figure assumes pf stops at the first match; pk, which signals every match, has to scan everything, so the equal-work ratios are 3.75x (i7-6700K) and 4.12x (i7-1370P).
- In bench.sh the pf pattern is the comm of the first /proc entry (\$p), but the pgrep side is hard-coded 'pgrep -x init'. On a systemd machine (PID 1 comm 'systemd') a user re-running it would compare pf's first-entry hit against pgrep's no-match scan. pf's match is also an unanchored substring, not pgrep's exact -x.
- The README ps comparison is not like for like: 'pd -f%p %c' with PROCS_CONFIG=/n prints the pid and the 15-character comm from /proc/PID/stat ('%c' is pf_cmd; '%C' would be the full command line), while '/bin/ps ax' prints PID, TTY, STAT, TIME and the full argv. No equal-output run such as 'ps -eo pid=,comm=' was timed.
- Config fragility: the shipped cb0 config raised 'unknown color key: "rcuS"' exceptions after an update (issue #8, fixed 2025-05-28), and 0.8.14 fixed an fd leak in pf --newest/--oldest; the tool parses its config on every run unless PROCS_CONFIG points to an empty file.

## Known shortcomings

- Win from fewer /proc reads, not Nim codegen: bench.sh's 'up to 7.617x/9.507x' times pf -e1 (exit at first match, with init the first /proc entry) against a full pgrep scan; equal-work no-match rows give 3.75x/4.12x (derived); the README 5.025X/5.745X divides pgrep time by the mean of pf hit and miss times; the ps comparison prints different output (ps ax shows full argv plus TTY, STAT, TIME; pd -f%p %c shows pid plus a 15-char comm); compiler, flags, procps version and the README machine unstated.
- bench.sh never times pkill: the README's 'pk 5.745X' is the i7-1370P pgrep row over the mean of pf's first-hit and no-match times, and the equal-work ratios are 3.75x and 4.12x. The pgrep side is hard-coded 'pgrep -x init' while pf uses the first /proc entry's comm, so the script breaks on systemd hosts; pf matches with an unanchored PCRE and has no -x mode. pd '%c' prints the 15-character comm against ps ax's full argv, so the outputs differ.

## Caveats and trade-offs

The gains come from doing less work, so this is a different, narrower program and not the same algorithm. pd -f%p %c reads only /proc/PID/stat and prints the pid and the 15-character comm. /bin/ps ax prints PID, TTY, STAT, TIME and the full argv (from /proc/PID/cmdline), and procps also parses /proc/PID/status, so the README ps comparison does not produce the same output. In bench.sh, -e1 means --exist --first (exit at the first match with no output). Because init is the first /proc entry, the 'up to 7.617x/9.507x' rows read one process while pgrep scans all of them; the equal-work no-match rows give 3.75x and 4.12x. procps pgrep 3.3.17 with a pattern sets PROC_FILLCOM and PROC_FILLSTATUS, so it reads cmdline and status for every process, while pf reads stat. The author says there are configurations where ps can be faster. The README timing machine and flags are unstated, the Nim/C compiler versions and the procps version are unstated, and bench.sh needs the author's tim and tails tools from c-blake/bu. These are millisecond-scale wins on a single-user tool. The nimble file says 'MIT/ISC' but LICENSE is ISC text. [retier] The gains come from doing less work: pd -f%p %c reads only /proc/PID/stat and prints the pid and the 15-character comm, while /bin/ps ax prints PID, TTY, STAT, TIME and the full argv and procps also parses /proc/PID/status, so the outputs differ. bench.sh never times pkill: the README's '(5.745 +- 0.016)X slower than pk' is the i7-1370P pgrep row over the mean of pf's first-hit and no-match times, and the equal-work ratios are 3.75x (i7-6700K) and 4.12x (i7-1370P). The pgrep side is hard-coded 'pgrep -x init' while pf uses the first /proc entry's comm, so the script breaks on systemd hosts; pf matches with an unanchored PCRE and has no -x mode. In bench.sh -e1 means --exist --first (exit at the first match with no output).

Linux /proc only. Fewer canned formats than ps (it is a construction toolkit with config files); pd/pf/pk are symlinks to one binary. Author calls it 'a work in progress'.

## Maintenance

Active single-author project (last commit 2026-07-04, version 0.8.14, 25 stars, ISC LICENSE text although the nimble file says 'MIT/ISC'). A WebSearch snippet of the 1996 procps-1.01 LSM lists Charles Blake as a procps co-author (page not opened). Small enough to vendor, but it ties you to Nim, cligen, PCRE1 and its config tree, and the measured wins are millisecond-scale and depend on narrow formats.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party numbers only: bench.sh (public, names i7-6700K and i7-1370P) times pf against procps pgrep, and the README footnote times pd against /bin/ps ax, but neither states the Nim/C compiler versions, the flags actually used for the benchmarked binaries, or the procps version and build, and the README ps timings name no machine; that falls short of A, and there is no independent measurement.
- **Verifier notes:** Real first-party measurements, and the numbers match the README and bench.sh exactly. The win is a narrower program doing less /proc I/O, not the Nim language (language_level_claim false and same_algorithm false are correct; same_opt_level stays unknown because neither side's build flags are stated). The headline 'up to 7.6x/9.5x' pf-vs-pgrep figures compare early exit at the first process with a full scan (equal-work ratio is 3.75x/4.12x, derived), and the README ps comparison prints different columns. Record these as shortcomings. Metadata checked: ISC, 25 stars, 3 forks, not a fork, not archived, last commit 2026-07-04 (active).
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-99 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/c-blake/procs/HEAD/bench.sh>
  - <https://raw.githubusercontent.com/c-blake/procs/HEAD/README.md>
  - <https://raw.githubusercontent.com/c-blake/procs/HEAD/procs.nim>
  - <https://github.com/c-blake/procs>
  - <https://github.com/c-blake/procs/commits>
  - <https://gitlab.com/procps-ng/procps/-/raw/v3.3.17/pgrep.c>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/c-blake/procs/HEAD/README.md>
  - <https://raw.githubusercontent.com/c-blake/procs/HEAD/bench.sh>
  - <https://raw.githubusercontent.com/c-blake/procs/HEAD/procs.nim>
  - <https://raw.githubusercontent.com/c-blake/procs/HEAD/procs.nimble>
  - <https://raw.githubusercontent.com/c-blake/procs/HEAD/procs.nims>
  - <https://raw.githubusercontent.com/c-blake/procs/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/c-blake/procs/HEAD/RELEASE-NOTES.md>
  - <https://github.com/c-blake/procs>
  - <https://github.com/c-blake/procs/commits/master/bench.sh>
  - <https://github.com/c-blake/procs/issues?q=is%3Aissue>
  - <https://github.com/c-blake/procs/issues/8>
  - <https://raw.githubusercontent.com/c-blake/lc/HEAD/README.md>
  - <https://raw.githubusercontent.com/c-blake/bu/HEAD/doc/rr.md>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/c-blake/procs`) · [data/wave14/enrich/raw/github_com_c_blake_procs.json](../../../data/wave14/enrich/raw/github_com_c_blake_procs.json) (enrichment confidence 0.7)

</details>
