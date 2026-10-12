# frawk

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [CSV and tabular data](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟡 stale

> JIT-compiled AWK dialect in Rust with SIMD CSV/TSV parsing; runs AWK scripts several times faster than gawk and mawk.

| | |
|---|---|
| **Beats** | gawk 5.1 (Linux) / 5.0.1 (macOS) run with -b, and mawk 1.3.4; one ad-hoc task also against a CPython csv-module script and a Rust csv-crate program (Python version not stated); xsv 0.13.0 and tsv-utils 2.1.1 also compared |
| **Claimed result** | Sum two columns, macOS: all_train TSV gawk 10.4 s and mawk 10.8 s vs frawk (LLVM) 3.1 s and parallel frawk 1.7 s; TREE_GRM_ESTN TSV gawk 14.0 s, mawk 42.0 s vs frawk 10.0 s / parallel 3.4 s. Linux: gawk 23.1 s vs frawk 14.7 s on TREE_GRM_ESTN TSV. Statistics (TREE_GRM_ESTN, macOS): gawk 1m13.3s and mawk 1m12.6s vs frawk (LLVM) 12.5 s TSV (about 5.9x vs gawk, derived from page data). Ad-hoc filtered weighted sum on CSV, macOS: CPython csv script 2m48.7s vs frawk (LLVM) 19.6 s (about 8.6x, derived from page data) and 4.9 s parallel; a quick Rust csv-crate program took 25.9 s. On a per-core basis frawk beats mawk and gawk but is slower than tsv-utils wherever tsv-utils ran. Group By Key is a tie with gawk (14.8 s vs 14.8 s on macOS; 22.1 s vs 23.5 s on Linux). |
| **Workload** | AWK-style CSV and TSV processing on 5.2 GB HEPMASS all_train and 8.9 GB TREE_GRM_ESTN files: sum two columns, statistics, select, filter, group by key. |
| **Metric** | throughput |
| **Hardware** | macOS: 16-inch MacBook Pro with 8-core i9 2.3 GHz (boost 4.8 GHz); Linux: dual-socket workstation with 2 x 8-core Xeon E5-2620v4 2.2 GHz, 64 GB RAM, Ubuntu 18.04 |
| **Compiler and flags** | frawk built with use_jemalloc and allow_avx2 features, LLVM and Cranelift backends 'with all optimizations enabled'; mawk on Linux compiled from source with -march=native; gawk invoked with -b; rustc/LLVM versions not stated |
| **Adoption** | 1.3k stars |
| **Last commit** | 2025-09-26 |
| **Links** | [repository](https://github.com/ezrosent/frawk) · [benchmark](https://raw.githubusercontent.com/ezrosent/frawk/HEAD/info/performance.md) |

## Verdict

The author's 2021 runs report the minimum wall time of 5 runs on a 16-inch MacBook Pro (8-core i9 2.3 GHz, Big Sur 11.2.1) and on a dual Xeon E5-2620 v4 Ubuntu 18.04 box. gawk 5.0.1/5.1 ran with -b and mawk was 1.3.4; frawk used the use_jemalloc and allow_avx2 features, and rustc/LLVM versions are not stated. On the 7.9 GB TREE_GRM_ESTN TSV on macOS, serial frawk (LLVM) summed two columns in 10.0 s vs gawk 14.0 s and mawk 42.0 s, and ran the statistics script in 12.5 s vs gawk 73.3 s; the logged sums, means and stddevs match gawk except in the parallel stats runs.

## Use it when

- Ad-hoc aggregations (sums, filters, group-bys, custom arithmetic) over multi-GB CSV with quoted fields, where awk would need a csv2tsv pass and Python's csv module is roughly 8x slower (19.6 s vs 2m48.7s in the author's run).
- Replacing gawk or mawk in batch pipelines that scan large files: serial frawk was 1.4-3x faster than gawk -b on sum, select and filter, and 5.9x faster on a statistics script.
- Embarrassingly parallel scans of one big file on a multicore box: -pr reached about 1.8-3 GB/s on an 8-core laptop without splitting the file first.
- Logic that does not fit a fixed menu of commands (xsv/xan/qsv/tsv-utils), such as conditional weighted sums or multi-column expressions.

## Skip it when

- Simple fixed operations on TSV: tsv-utils beat serial frawk on every task it ran (for example 2.7 s vs 3.1 s sum, 4.9 s vs 14.8 s group-by on macOS) and was faster per core even against parallel frawk.
- Hash-map-heavy work such as group-by: serial frawk only ties gawk (14.8 s vs 14.8 s macOS, 22.1 s vs 23.5 s Linux), and the author says arrays need optimization.
- Scripts that read from command pipes via getline: issue #98 reports frawk about 3x slower than mawk.
- Production pipelines that need strict POSIX awk behaviour or prompt bug fixes: open issues include field assignment not working in CSV mode (#111), NF override not clearing fields (#119), string format specifiers broken on the Cranelift backend (#121) and scientific-notation literals (#83).
- Windows or environments where you cannot install nightly Rust and LLVM 12: Windows is untested by the author, and a Cranelift misaligned-pointer report is open there (#101).

## How it is fast

The script goes through a typed SSA CFG with static type inference, so numbers and strings are known before execution and coercion branches disappear. That typed IR is JIT-compiled with LLVM (or Cranelift; a bytecode interpreter is available via -Binterp) and calls into a shared Rust runtime. Input uses a two-phase, simdcsv-style parser: a SIMD pass finds structural characters, then a cheap state machine runs once per structural character. The same split lets one reader thread chunk a single file and hand records to worker threads (-pr). It also uses SIMD UTF-8 validation, a fast float parser, the Rust regex crate, hashbrown maps and jemalloc.

## Compared with alternatives

Pick frawk over xan, qsv or zsv when the job is a small program (conditional sums, custom formulas, explicit multi-pass aggregation) rather than one of their built-in commands, and the CSV is quoted so classic awk cannot parse it. For standard select, count, stats or filter jobs, xan, qsv and zsv are maintained and need no LLVM or nightly toolchain.

## Integration

| | |
|---|---|
| **Form** | crate (command-line binary; `cargo install frawk`), not a library API |
| **Dependencies** | Rust crates (regex, hashbrown, cranelift 0.93, crossbeam, memchr, fast-float, bumpalo, optional tikv-jemallocator); system LLVM 12 via llvm-sys 120 for the default llvm_backend feature |
| **Minimum toolchain** | Nightly Rust by default (stable works without the `unstable` feature); LLVM 12 for the LLVM backend; no MSRV stated |
| **Platforms** | Linux and macOS on x86-64 tested by the author (allow_avx2 feature uses AVX2 when present); Windows untested and only builds with default features disabled; aarch64 not documented |
| **Thread safety** | Not a library. -pr (record-level) and -pf (file-per-worker) run the main loop on -j worker threads; BEGIN and END run on one thread, and variables shared with END are aggregated implicitly. |
| **Drop-in for the baseline** | partial: many awk programs run unchanged, but frawk has no awk-style strnum, so a user function such as max(\$4,\$5) on raw fields compares lexicographically unless the arguments are converted with +0 (the performance doc's own note). CSV mode needs -icsv, -itsv and -F'\t' are different parsers, and parallel mode changes semantics (row order, implicit aggregation). |

## Gotchas

- Harness flaw in the published Statistics benchmark: the parallel script's variance merge tests `if (i == 1)` with i never set and adds `sums[k]` with k undefined, so the merged mean feeding the variance is wrong. The logged outputs show parallel stddev 1.906e14 to 2.017e14, varying per run, against 1.806e14 from serial frawk, gawk, mawk, xsv and tsv-summarize. The parallel stats times (3.4-3.6 s TSV on macOS) therefore come from a script with wrong output. The serial numbers are unaffected, and their outputs match gawk.
- In -pr mode, numeric scalars used in both the main loop and END are summed across workers, and string scalars take an arbitrary worker's value. min, max and variance need explicit PREPARE/PID merging, which is easy to get wrong, as the author's own stats script shows. Output rows are also reordered, so the parallel select and filter timings are not like-for-like with tools that keep order.
- Benchmark scope: TSV runs used -F'\t' (plain split, no escape handling), not -itsv. The filter benchmark gave awk/frawk `$4 > 0.000024` but tsv-filter `--gt 4:0.000025 -H`, with outputs sent to /dev/null and never compared. The group-by data has only two distinct keys (FORESTLAND, TIMBERLAND), so it hardly exercises hash maps.
- Every frawk timing includes JIT compile time. That cost is small here, but it dominates on tiny inputs; -Binterp exists for small scripts.

## Known shortcomings

- Near A (public scripts and raw logs, Xeon E5-2620 v4 named) but no rustc or LLVM version; ties gawk on Group By Key and is slower per core than tsv-utils; the CPython ad-hoc comparison (2m48.7s vs 19.6 s, about 8.6x derived) gives it a listed baseline. Rust awk; moved to csv-tabular.
- Enricher: the published parallel Statistics benchmark's info/scripts/stat_2.sh has a broken variance merge (tests 'if (i == 1)' with i never set and adds sums[k] with k undefined), and the logged parallel stddev of 1.906e14-2.017e14 differs from the 1.806e14 that serial frawk, gawk, mawk, xsv and tsv-summarize all produce, so the parallel stats timings (3.4-3.6 s) come from a wrong-output script; the serial claim (12.5 s vs gawk 73.3 s) is unaffected and its outputs match gawk. filter.sh uses threshold 0.000024 for awk and frawk against 0.000025 for tsv-filter; the group-by data has only 2 keys; last crates.io release 0.4.8 (2023-03-21).

## Caveats and trade-offs

Author's own benchmarks; scripts and raw logs are in info/scripts but rustc/LLVM versions are missing and the numbers date from about 2021 (macOS Big Sur 11.2.1). frawk ties gawk on Group By Key, the Cranelift build is slower than gawk there on macOS, and frawk is slower than tsv-utils per core on every task tsv-utils ran; parallel select/filter does not preserve row order. The CPython comparison is one ad-hoc script, Python version unstated, and frawk's time includes its own compile. The doc asks readers to draw only modest conclusions. gawk and mawk are AWK implementations, not listed category baselines. Building needs nightly Rust by default and LLVM 12 for the LLVM backend; the maintainer noted in 2024 that he has much less time for bug fixes. [retier] Near A (public scripts and raw logs, Xeon E5-2620 v4 named) but no rustc or LLVM version. The parallel Statistics timings (3.4-3.6 s) come from info/scripts/stat_2.sh, whose variance merge is broken ('if (i == 1)' with i never set, sums[k] with k undefined): the logged parallel stddev (1.906e14-2.017e14) differs from the 1.806e14 that serial frawk, gawk, mawk, xsv and tsv-summarize produce, so quote only the serial Statistics result (12.5 s vs gawk 73.3 s, outputs matching gawk). filter.sh uses threshold 0.000024 for awk and frawk against 0.000025 for tsv-filter; the group-by data has only 2 keys. Ties gawk on Group By Key and is slower per core than tsv-utils. Last crates.io release 0.4.8 (2023-03-21). Rust awk; filed under csv-tabular.

AWK dialect with its own semantics (explicit numeric conversion needed in comparisons, CSV/TSV input modes), parallel mode splits input across workers; build needs LLVM or uses Cranelift; maintainer says bug-fix time is limited.

## Maintenance

Stale: the author stepped back in 2024, and a contributor landed parser and runtime fixes in September 2025, but the last crates.io release is 0.4.8 from 2023-03-21. It is MIT OR Apache-2.0 and usable as a CLI if you build master with nightly Rust plus LLVM 12 (or Cranelift only). The published parallel Statistics benchmark comes from a script with a variance-merge bug that prints a wrong stddev.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party doc with public scripts and raw timing logs (info/scripts/sum2.sh, stat_2.sh, select.sh, filter.sh, groupby.sh, complex_sum.sh with .out and .out.mac files), a named Linux CPU (Xeon E5-2620 v4) and frawk build features, but no rustc/LLVM version (and the Mac CPU is only '8-core i9 2.3GHz'), so C by the compiler-version precedent; close to A.
- **Verifier notes:** All claimed numbers match info/performance.md and the sum2.sh.out.mac log (e.g. gawk 14.231 s, mawk 42.108 s); the page also compares against a CPython script, so baseline_in_list set true. frawk is an AWK implementation benchmarked on CSV/TSV against gawk, mawk, xsv and tsv-utils, so its real category is arguably csv-tabular (wave 3, parsing-and-text) rather than language-interpreters. Metadata checked: MIT OR Apache-2.0, 1.3k stars, last commit 2025-09-26 (stale), not archived.
- **Fields the verifier corrected:** `baseline`, `baseline_in_list`, `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/ezrosent/frawk/HEAD/info/performance.md>
  - <https://github.com/ezrosent/frawk/tree/master/info/scripts>
  - <https://raw.githubusercontent.com/ezrosent/frawk/HEAD/info/scripts/sum2.sh>
  - <https://raw.githubusercontent.com/ezrosent/frawk/HEAD/info/scripts/sum2.sh.out.mac>
  - <https://raw.githubusercontent.com/ezrosent/frawk/HEAD/README.md>
  - <https://github.com/ezrosent/frawk>
  - <https://github.com/ezrosent/frawk/commits>
- **Sources the enricher read:**
  - <https://github.com/ezrosent/frawk>
  - <https://raw.githubusercontent.com/ezrosent/frawk/HEAD/README.md>
  - <https://raw.githubusercontent.com/ezrosent/frawk/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/ezrosent/frawk/HEAD/info/performance.md>
  - <https://raw.githubusercontent.com/ezrosent/frawk/HEAD/info/overview.md>
  - <https://raw.githubusercontent.com/ezrosent/frawk/HEAD/info/parallelism.md>
  - <https://raw.githubusercontent.com/ezrosent/frawk/HEAD/info/types.md>
  - <https://github.com/ezrosent/frawk/tree/master/info/scripts>
  - <https://raw.githubusercontent.com/ezrosent/frawk/HEAD/info/scripts/sum2.sh>
  - <https://raw.githubusercontent.com/ezrosent/frawk/HEAD/info/scripts/sum2.sh.out>
  - <https://raw.githubusercontent.com/ezrosent/frawk/HEAD/info/scripts/sum2.sh.out.mac>
  - <https://raw.githubusercontent.com/ezrosent/frawk/HEAD/info/scripts/stat_2.sh>
  - <https://raw.githubusercontent.com/ezrosent/frawk/HEAD/info/scripts/stat_2.sh.out>
  - <https://raw.githubusercontent.com/ezrosent/frawk/HEAD/info/scripts/stat_2.sh.out.mac>
  - <https://raw.githubusercontent.com/ezrosent/frawk/HEAD/info/scripts/complex_sum.sh>
  - <https://raw.githubusercontent.com/ezrosent/frawk/HEAD/info/scripts/complex_sum.py>
  - <https://raw.githubusercontent.com/ezrosent/frawk/HEAD/info/scripts/complex_sum.sh.out.mac>
  - <https://raw.githubusercontent.com/ezrosent/frawk/HEAD/info/scripts/groupby.sh>
  - <https://raw.githubusercontent.com/ezrosent/frawk/HEAD/info/scripts/groupby.sh.out.mac>
  - <https://raw.githubusercontent.com/ezrosent/frawk/HEAD/info/scripts/select.sh>
  - <https://raw.githubusercontent.com/ezrosent/frawk/HEAD/info/scripts/filter.sh>
  - <https://github.com/ezrosent/frawk/issues>
  - <https://github.com/ezrosent/frawk/issues/98>
  - <https://github.com/ezrosent/frawk/issues/110>
  - <https://github.com/ezrosent/frawk/commits/master>
  - <https://crates.io/api/v1/crates/frawk>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/ezrosent/frawk`) · [data/wave12/enrich/raw/github_com_ezrosent_frawk.json](../../../data/wave12/enrich/raw/github_com_ezrosent_frawk.json) (enrichment confidence 0.8)

</details>
