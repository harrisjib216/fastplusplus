# vroom

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [CSV and tabular data](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `R` · `MIT` · 🟢 active

> Lazy, ALTREP-backed delimited-file reader for R; indexes then reads on demand, beating base R's read.delim/readr/data.table.

| | |
|---|---|
| **Beats** | R base read.delim (utils) |
| **Claimed result** | \~22.6x faster on initial read alone (1m 21.5s vs 3.6s; derived from page data); \~11.8x faster for the full workflow (1m 22.6s vs 7s; derived from page data) |
| **Workload** | Reading a 1.55GB / 14.7M-row / 11-column real-world taxi-trip CSV and running read+print+head+tail+sample+filter+summarise, vroom vs base R read.delim (also readr and data.table) |
| **Metric** | throughput |
| **Adoption** | 643 stars; core part of the tidyverse ecosystem |
| **Last commit** | 2026-06-09 |
| **Links** | [repository](https://github.com/r-lib/vroom) · [benchmark](https://tidyverse.org/blog/2019/05/vroom-1-0-0/) |

## Verdict

On a real 1.53GB/14.7M-row/11-column taxi-trip CSV, the tidyverse blog table reports vroom reading in 3.6s versus base R read.delim's 1m21.5s (\~22.6x), and a full read+print+head+tail+sample+filter+summarise workflow at 7s versus 1m22.6s (\~11.8x); the post gives no CPU or compiler flags. A newer benchmarks vignette (vroom 1.5.1, public code in inst/bench/taxi, EC2 m5.4xlarge/16 vCPUs) shows read.delim at 1m12.3s versus vroom 1.3s to read, still without compiler flags.

## Use it when

- Large local, uncompressed CSV/TSV/FWF files (hundreds of MB to multi-GB) read directly from disk, where memory-mapping applies
- Pipelines that only touch a subset of rows/columns after loading (select/filter before printing or string ops), so lazy character materialization pays off
- Existing readr users who want a faster, largely drop-in replacement without rewriting column-spec code
- Writing large delimited files, where parallel formatting plus async write beats base R's write functions
- R &gt;= 4.1 environments, where ALTREP is fully supported by the runtime

## Skip it when

- Small files, where indexing overhead and R startup cost dominate and base read.delim/readr are already fast enough
- Workflows that immediately print, filter, or string-process every character column, since that forces materialization and shifts most of the 'read' cost to first access, hiding behind read-time-only benchmarks
- Remote or compressed sources (.gz/.bz2/.xz/.zip): vroom downloads to a temp file before mapping it, losing the mmap/lazy advantage
- Contexts needing embedded newlines inside quoted headers/fields, which force num_threads = 1 and remove the multi-threaded indexing speedup
- Situations requiring reproducible cross-hardware speedup numbers: the cited benchmarks give no compiler flags, and only the newer vignette names a CPU (EC2 m5.4xlarge)

## How it is fast

Memory-maps the input file (bundled mio C++ library) and scans it with multiple threads to build a byte-offset index of every delimited field, so no value is parsed before it's needed. Returned columns are R ALTREP objects (character columns lazy by default) that convert raw bytes to R values only on access; non-character materialization and file writing also run multi-threaded, and grisu3 provides fast double-to-string formatting when writing.

## Compared with alternatives

All catalogued siblings target C/Go/Rust/.NET/Ruby/Python CSV stacks; vroom is the only R-ecosystem entry, so pick it whenever the pipeline is already in R and you want readr-compatible syntax — its speed claim is against base R's read.delim, not against any sibling's baseline, so it isn't a substitute for those language-specific choices.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | R packages bit64, cli, glue, hms, lifecycle, rlang, tibble, tidyselect, tzdb, vctrs, withr (Imports); cpp11, progress, tzdb (LinkingTo, compile-time); bundled mio (header-only C++ mmap library) |
| **Minimum toolchain** | R &gt;= 4.1 (Depends, needed for full ALTREP support); C++ compiler to build from source (CRAN also ships binaries) |
| **Platforms** | any platform R runs on (Windows/macOS/Linux, x86-64/aarch64) via mio's cross-platform mmap wrapper |
| **Thread safety** | not documented for concurrent R sessions/threads calling vroom simultaneously; internally spawns VROOM_THREADS worker threads (default parallel::detectCores()) for indexing, materialization, and writing |
| **Drop-in for the baseline** | partial — the baseline here is base R read.delim, and vroom's call signature is different (readr-style, not read.delim/read.csv-style); switching requires touching read calls, though the tibble result behaves like a data frame |

## Gotchas

- Only character columns use ALTREP lazy loading by default (VROOM_USE_ALTREP_CHR=true); numeric/integer/date ALTREP is opt-in via separate env vars, so headline read-time numbers can hide deferred character-materialization cost
- Reading from R connections or compressed/remote files downloads to a temp file first, forfeiting the mmap-based lazy-read advantage
- Embedded newlines inside quoted headers or fields require num_threads = 1, disabling the multi-threaded indexing that produces most of the speedup
- Repository moved from r-lib/vroom to tidyverse/vroom in April 2022; the r-lib URL still resolves via GitHub's redirect

## Caveats and trade-offs

The baseline is base R's read.delim (the post's table row), not read.csv; it is a widely used incumbent in another language ecosystem. The 2019 blog gives no hardware or build flags. The updated benchmark vignette (vroom 1.5.1, 2021-06-22, EC2 m5.4xlarge with 16 vCPUs, code in inst/bench/taxi) shows read.delim 1m 12.3s read vs vroom 1.3s read (1m 14.5s vs 6.7s total with dplyr+Altrep), but still no compiler or flags. vroom's read time relies partly on lazy Altrep materialization, which shifts cost to later filter and summarise steps.

Lazy/ALTREP-based loading means first access to character columns (print, filter, string ops) carries a deferred cost not captured by read-time-only comparisons; behavior depends on R's ALTREP framework.

## Maintenance

Actively maintained (last commit 2026-06-09, current CRAN release 1.7.1, part of the core tidyverse); MIT-licensed (DESCRIPTION and LICENSE.md) and simple to depend on via CRAN or pak, despite GitHub's NOASSERTION license auto-detection.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** Tidyverse blog table on the 1.55GB, 14.7M-row, 11-column taxi data: base R read.delim reads in 1m 21.5s (1m 22.6s total) vs vroom 3.6s (7s total); no CPU or flags. The linked benchmark vignette adds public code (inst/bench/taxi) and an EC2 m5.4xlarge but no compiler or flags, so first-party C.
- **Verifier notes:** Baseline corrected from read.csv to read.delim, as the page shows. The last commit on the default branch (main) is 2026-06-09; 2026-09-21 is only pushed_at. License is MIT per DESCRIPTION ('MIT + file LICENSE') and LICENSE.md despite gh's NOASSERTION; status is still active.
- **Fields the verifier corrected:** `baseline`, `workload`, `claimed_speedup`, `last_commit`, `caveats`
- **Pages the verifier opened:**
  - <https://tidyverse.org/blog/2019/05/vroom-1-0-0/>
  - <https://vroom.r-lib.org/articles/benchmarks.html>
  - <https://vroom.tidyverse.org/articles/benchmarks.html>
  - <https://github.com/r-lib/vroom>
- **Sources the enricher read:**
  - <https://github.com/r-lib/vroom>
  - <https://github.com/r-lib/vroom/blob/main/README.md>
  - <https://github.com/r-lib/vroom/blob/main/DESCRIPTION>
  - <https://github.com/r-lib/vroom/blob/main/NEWS.md>
  - <https://github.com/r-lib/vroom/tree/main/inst/bench/README.md>
  - <https://github.com/r-lib/vroom/tree/main/src>
  - <https://tidyverse.org/blog/2019/05/vroom-1-0-0/>
  - <https://vroom.r-lib.org/articles/benchmarks.html>
  - <https://vroom.tidyverse.org/articles/benchmarks.html>
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/r-lib/vroom`) · [data/wave3/enrich/raw/github_com_r_lib_vroom.json](../../../data/wave3/enrich/raw/github_com_r_lib_vroom.json) (enrichment confidence 0.6)

</details>
