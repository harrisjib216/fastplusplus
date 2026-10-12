# GoAWK

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [Text search and indexing](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `MIT` · 🟢 active

> POSIX AWK interpreter in Go with CSV mode and embedding API; faster than one-true-awk, slower than gawk and mawk.

| | |
|---|---|
| **Beats** | one-true-awk (original-awk), gawk and mawk; also GoAWK's previous tree-walking interpreter ('orig') |
| **Claimed result** | PR #88 real-world table (speed relative to one-true-awk = 1.00, 23 testdata/tt.\* scripts): geo mean GoAWK 1.45, GoAWK tree-walker 1.28, gawk 1.86, mawk 2.32. GoAWK beats one-true-awk on 18 of 23 scripts but is slower on tt.04 (0.97), tt.05 (0.95), tt.10 (0.34), tt.10a (0.32) and tt.15 (0.62); it beats gawk on 9 of 23. By geo mean gawk is about 1.28x and mawk about 1.6x faster than GoAWK (derived from page data). README: 'Most AWK scripts are faster than awk and on a par with gawk, though usually slower than mawk.' |
| **Workload** | AWK script execution on GoAWK's bytecode compiler and virtual machine; the README links an article with the benchmark results (not opened). |
| **Metric** | throughput |
| **Adoption** | 2.1k stars; used in Redpanda Connect |
| **Last commit** | 2026-09-15 |
| **Links** | [repository](https://github.com/benhoyt/goawk) · [benchmark](https://github.com/benhoyt/goawk/pull/88) |

## Verdict

In the author's January 2022 run (PR #88; scripts/benchmark_awks.py over 23 testdata/tt.\* scripts, wall time including process start, second-best of six runs), the bytecode VM averaged 1.45x the speed of one-true-awk (geo mean), against 1.86x for gawk and 2.32x for mawk. GoAWK was slower than one-true-awk on 5 scripts, down to 0.32x on regex matching. Hardware, OS, Go version and awk versions are not stated.

## Use it when

- You need an AWK engine embedded in a Go program (no cgo, no external awk binary), e.g. user-supplied transform scripts in a pipeline, as Redpanda Connect does.
- Machines whose only awk is one-true-awk / BWK awk (macOS, BSD): GoAWK beat it on 18 of 23 timing scripts in the author's run, geo mean 1.45x.
- CSV/TSV processing with AWK syntax and proper quoting: the author's 1 GB CSV read takes 3.18 s (on a par with Go's encoding/csv at 3.22 s) and write 5.64 s versus 13.0 s for frawk.
- Field arithmetic, loops and array-heavy scripts (sum, count, mandelbrot-style loops), where the VM gains concentrate; it also beat gawk on 9 of 23 scripts.
- Sandboxed execution: Config.NoExec, NoFileWrites and NoFileReads block system(), pipes and file I/O, and a context can cancel long runs.

## Skip it when

- If gawk or mawk is available and raw speed is the goal: by geo mean gawk is about 1.28x and mawk about 1.6x faster (derived from page data), and mawk won every one of the 23 scripts.
- Regex-heavy scripts: `/.$/` (tt.10) ran at 0.34x the speed of one-true-awk and the text formatter tt.15 at 0.62x, because Go's regexp is slow; the umbrella optimisation issue #91 lists regex speed as not done.
- CSV reading at maximum throughput: the project's own CSV benchmark shows frawk reading 1 GB about 3.1x faster (1.01 s vs 3.18 s).
- Scripts relying on gawk-only extensions: GoAWK targets POSIX AWK plus its own additions, not gawk compatibility.
- Unicode character semantics on long strings: chars mode (-c / Config.Chars) is opt-in, and an earlier character-based default made gron.awk hang in v1.13 (issue #93) because string functions became O(N).

## How it is fast

Since PR #88 (January 2022) programs are compiled to 32-bit 'word code' and run on a stack virtual machine with a single big switch dispatch loop (interp/vm.go); the opcode count was cut (24 builtin calls folded into one CallBuiltin) and specialised opcodes such as AugAssignLocal, FieldInt and ConcatMulti avoid generic paths. Numeric strings are converted to numbers lazily, regexes and printf formats are cached, and release binaries are built with Go profile-guided optimisation from the interp microbenchmarks (scripts/make_binaries.sh). Regex matching uses Go's RE2-style regexp in leftmost-longest mode, which is the main remaining bottleneck.

## Compared with alternatives

The listed siblings (Tantivy, IResearch, SeekStorm, ugrep, ngi and other index or grep tools) solve indexed search, not line-by-line AWK scripting, so pick GoAWK when you need an AWK language runtime inside Go; for the fastest AWK, frawk (another wave 12 entry) reads CSV about 3x faster and mawk wins every timing script.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none (go.mod has no requires) |
| **Minimum toolchain** | Go 1.20 (go.mod; raised in v1.31.0) |
| **Platforms** | any Go target; release binaries for linux 386/amd64/arm64, windows 386/amd64, darwin amd64/arm64, freebsd amd64/arm |
| **Thread safety** | not documented; an Interpreter keeps variables, I/O state and caches between Execute calls, so use one per goroutine |
| **Drop-in for the baseline** | partial — the goawk binary accepts POSIX AWK programs and the common flags, but output can differ where the README lists differences (CSV mode, negative field indexes, single-quoted strings) and regex semantics come from Go's regexp in leftmost-longest mode |

## Gotchas

- Harness flaw: scripts/benchmark_awks.py keeps min(sorted(times)[1:]), i.e. the second-fastest of six runs rather than discarding a warm-up run; it times whole processes, ignores non-zero exit status beyond printing it, never compares outputs, and scales the input until GoAWK alone takes 0.5 s.
- First-party numbers drift a lot between runs: the author's 23 Dec 2021 table (commit b05d0d9, tree-walker) has GoAWK tt.01 at 4.25 and geo mean 1.57, while PR #88 a month later shows tt.01 at 2.02 and geo mean 1.45; the gawk and mawk leads hold in both.
- The published tables predate v1.30.0's switch to leftmost-longest regex matching, PGO-built releases and newer Go compilers, and have not been re-measured; a `go install` build does not get the PGO profile, which is generated only by scripts/make_binaries.sh.
- The dynamic regex cache is 'dumb, non-LRU': only the first 100 distinct dynamic regex strings are cached (interp.go), so scripts that build many regexes at run time recompile them on every use.

## Known shortcomings

- Raised D to C on PR #88 (2022): geomean 1.45 vs one-true-awk 1.00, but gawk (1.86) and mawk (2.32) are faster, so 'on a par with gawk' is overstated; no hardware. Go awk; moved to text-search-and-indexing (frawk covers the CSV mode).
- Enricher: scripts/benchmark_awks.py keeps the second-fastest of 6 runs, ignores exit status, never compares outputs and calibrates the input size on GoAWK alone; the numbers swing between first-party runs (tt.01 was 4.25 in commit b05d0d9 of 2021-12-23 and 2.02 in PR #88) and the tables predate the v1.30.0 switch to leftmost-longest regex; the dynamic regex cache holds only the first 100 regexes.

## Caveats and trade-offs

First-party numbers from January 2022 (bytecode VM PR #88); hardware, OS, Go version and awk versions are not stated. Harness scripts/benchmark_awks.py takes the minimum of runs 2-6 of six per awk, repeats the input file until GoAWK runs at least 0.5 s, includes process start and does not compare outputs across awks. The README's 'on a par with gawk' is generous against its own data (gawk geo mean 1.86 vs GoAWK 1.45), mawk is faster on every script, and regex-heavy scripts are slower than other awks because of Go's regexp package (README). The linked blog article (benhoyt.com/writings/goawk-compiler-vm) is blocked here; a search snippet shows the same geo means (goawk 1.45, orig 1.28, awk 1.00, gawk 1.86).

AWK interpreter in Go with CSV/TSV support and a Go API for embedding; regular-expression heavy scripts are slower than other implementations because Go's regexp is slow (README).

## Maintenance

Actively maintained (v1.32.0 released 2026-09-15, the last commit), MIT, no dependencies and a stable v1 Go API; usable as a library today, but listed as faster than one-true-awk only, not than gawk or mawk.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification D, tier now C.
- **Tier reason:** Upgraded from D: the numbers behind the README claim are on github.com in PR #88 (merged 2022-01-31), a first-party table from the public harness scripts/benchmark_awks.py over testdata/tt.\* comparing GoAWK with one-true-awk, gawk and mawk; no hardware, Go version or awk versions stated, so C.
- **Verifier notes:** Tier raised D to C: numbers found in PR #88 on github.com; GoAWK is faster than one-true-awk only, slower than gawk and mawk by geo mean, so it is weak as a 'faster' entry (keep with that shortcoming). frawk, a faster AWK, is already in wave 12 merged; if the orchestrator prefers an earlier-wave category for AWK implementations, the nearest is text-search-and-indexing (grep-style text processing), with csv-tabular for its CSV mode. Metadata confirmed: MIT, 2.1k stars, not archived or a fork, last commit 2026-09-15 (v1.32.0), used in Redpanda Connect per README.
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/benhoyt/goawk/HEAD/README.md>
  - <https://github.com/benhoyt/goawk>
  - <https://github.com/benhoyt/goawk/commits>
  - <https://github.com/benhoyt/goawk/tree/master/scripts>
  - <https://raw.githubusercontent.com/benhoyt/goawk/HEAD/scripts/benchmark_awks.py>
  - <https://raw.githubusercontent.com/benhoyt/goawk/HEAD/scripts/benchmark.sh>
  - <https://raw.githubusercontent.com/benhoyt/goawk/HEAD/scripts/benchstat.sh>
  - <https://github.com/benhoyt/goawk/pull/88>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/benhoyt/goawk/HEAD/README.md>
  - <https://raw.githubusercontent.com/benhoyt/goawk/HEAD/scripts/benchmark_awks.py>
  - <https://raw.githubusercontent.com/benhoyt/goawk/HEAD/scripts/benchmark.sh>
  - <https://raw.githubusercontent.com/benhoyt/goawk/HEAD/scripts/make_binaries.sh>
  - <https://raw.githubusercontent.com/benhoyt/goawk/HEAD/go.mod>
  - <https://raw.githubusercontent.com/benhoyt/goawk/HEAD/docs/csv.md>
  - <https://raw.githubusercontent.com/benhoyt/goawk/HEAD/interp/interp.go>
  - <https://raw.githubusercontent.com/benhoyt/goawk/HEAD/interp/newexecute.go>
  - <https://raw.githubusercontent.com/benhoyt/goawk/HEAD/interp/vm.go>
  - <https://raw.githubusercontent.com/benhoyt/goawk/HEAD/goawk.go>
  - <https://raw.githubusercontent.com/benhoyt/goawk/HEAD/testdata/tt.04_printf_fields>
  - <https://raw.githubusercontent.com/benhoyt/goawk/HEAD/testdata/tt.05_concat_fields>
  - <https://raw.githubusercontent.com/benhoyt/goawk/HEAD/testdata/tt.10_regex_ends_with>
  - <https://raw.githubusercontent.com/benhoyt/goawk/HEAD/testdata/tt.15_format_lines>
  - <https://github.com/benhoyt/goawk/pull/88>
  - <https://github.com/benhoyt/goawk/tree/master/testdata>
  - <https://github.com/benhoyt/goawk/commit/b05d0d983d4e96ae518c6af3e846fbb1a15040aa>
  - <https://github.com/benhoyt/goawk/commit/b05d0d983d4e96ae518c6af3e846fbb1a15040aa.patch>
  - <https://github.com/benhoyt/goawk/releases>
  - <https://github.com/benhoyt/goawk/issues?q=is%3Aissue+performance+OR+slow>
  - <https://github.com/benhoyt/goawk/issues/93>
  - <https://github.com/benhoyt/goawk/issues/91>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/benhoyt/goawk`) · [data/wave12/enrich/raw/github_com_benhoyt_goawk.json](../../../data/wave12/enrich/raw/github_com_benhoyt_goawk.json) (enrichment confidence 0.75)

</details>
