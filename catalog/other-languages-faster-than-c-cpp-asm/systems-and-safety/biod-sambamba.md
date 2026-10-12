# sambamba (D tools for SAM/BAM)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Systems and safety](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `D` · `GPL-2.0` · 🟡 stale

> D command-line tools for SAM/BAM (view, flagstat, sort, markdup, index, depth) that parallelise work samtools 1.7 ran single-threaded.

| | |
|---|---|
| **Beats** | samtools (view, flagstat, markdup, sort, index; C, htslib) |
| **Claimed result** | README (quoting the CRG comparison): flagstat 1.4x faster than samtools, index similar, markdup almost 6x, view 4x, sort beaten by samtools but up to 2x faster on 120GB+ machines. The README's linked report (public-docs.crg.es sambamba_ws_report.html) could not be opened. The pipeline's own 16 CPU / 120 GB report gives wall times (realtime) vs samtools 1.7: flagstat 7.7 s (sambamba 0.6.8-pre1) and 11.4 s (0.6.6) vs 11.5 s, 1.49x and 1.00x; index 12.7 s and 14.9 s vs 13.1 s, 1.03x and 0.88x; view 15.9 s (0.6.6) and 52.8 s (0.6.8-pre1) vs 77.8 s, 4.88x and 1.47x; markdup 197.1 s and 244.6 s vs 885.8 s for a four-stage samtools sort/fixmate/sort/markdup pipeline, 4.49x and 3.62x; sort 249.3 s and 327.2 s vs 146.7 s, so samtools 1.7 is 1.70x faster at 120 GB (all ratios derived from page data). |
| **Workload** | sambamBench-nf (Nextflow) runs flagstat, index, markdup, name sort (-n/-N) and view to /dev/null on the \~4 GB ENCODE BAM ENCFF044SJL with 16 threads and 120 GB (cluster profile; workstation profile 8 CPUs/40 GB), one run per tool version; samtools-1.7 markdup is a name sort, fixmate -m, coordinate sort and markdup pipeline, while sambamba markdup reads the BAM directly. |
| **Metric** | throughput |
| **Hardware** | CRG cluster node, 16 CPUs and 120 GB RAM allocated to each task (CPU model not stated), per the sambamBench-nf README and nextflow.config cluster profile; the README's quoted figures may come from the unopened 'ws' (workstation, 8 CPUs, 40 GB) report. |
| **Compiler and flags** | sambamba 0.6.6 and 0.6.8-pre1 and samtools 1.3 and 1.7 from grape/&lt;tool&gt;:&lt;version&gt; containers (build flags not published). sambamba's own release build uses ldc2 -O3 -release -enable-inlining -boundscheck=off (test/benchmark/stats.org); samtools 1.7's Makefile defaults to CFLAGS = -g -Wall -O2. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | not stated |
| **Same optimization level** | not stated |
| **Why it wins** | README: when sambamba started in 2012 its main advantage over samtools was parallelized BAM reading and writing. |
| **Adoption** | 613 stars; over 1,000 citations (Bioinformatics 2015 paper); 250,000 conda installs |
| **Last commit** | 2024-12-22 |
| **Links** | [repository](https://github.com/biod/sambamba) · [benchmark](https://github.com/guigolab/sambamBench-nf) |

## Verdict

The Guigo lab's Nextflow pipeline ran sambamba 0.6.6 and 0.6.8-pre1 (official static LDC -O3 release binaries) and samtools 1.3 and 1.7 (built with plain make, -O2, against Debian zlib, no libdeflate) on the 4.6 GB ENCODE BAM ENCFF044SJL, with 16 CPUs and 120 GB on one CRG node of unstated CPU model. Tasks ran sequentially, once each. Wall times against samtools 1.7: flagstat 7.7-11.4 s vs 11.5 s, index 12.7-14.9 s vs 13.1 s, view 15.9 s (warm) vs 77.8 s, markdup 197-245 s vs 886 s for a single-threaded pipeline, sort 249-327 s vs 147 s (samtools wins).

## Use it when

- Marking duplicates on a coordinate-sorted BAM in one command on a many-core node, where the alternative is a samtools sort -n | fixmate -m | sort | markdup pipeline or Picard MarkDuplicates.
- Converting BAM to SAM text (view) on 8-16 cores, where samtools 1.7's single-threaded text formatting is the bottleneck: 15.9 s against 77.8 s on a 4.6 GB BAM with warm caches.
- flagstat on many cores: 7.7 s for sambamba 0.6.8-pre1 against 11.5 s for samtools 1.7 -@16.
- Pipelines that already use sambamba's filter expressions (-F) or view -L region skipping and want its output byte-for-byte as before.
- Name or coordinate sorting only when the machine has enough RAM to hold the whole file (tens of GB); this is the maintainers' own advice in issue #447.

## Skip it when

- Sorting on ordinary machines: samtools 1.7 sorted the same BAM 1.70x faster at equal 72 GB memory (146.7 s against 249.3 s), and on a Ryzen 5 3600 with a 128 MB cap sambamba 0.7.1 took 84.8 s single-threaded against 39.3 s for samtools 1.9 (33.7 s against 15.1 s with three extra threads, issue #447).
- CRAM input or output: removed in 0.8.0 (only old binaries read it).
- When you need current samtools/htslib features or speed: the comparison is against samtools 1.7 built with plain zlib, while htslib 1.8 added libdeflate and later samtools releases also thread markdup and use collate in place of sort -n.
- When you need exact Picard duplicate counts: issue #461 shows small differences (29,370,719 against 29,393,253 duplicates), which the maintainer called not worth worrying about.
- Low-core or shared nodes: the gains come from extra cores (658-1534% CPU in the trace), and index is at parity (12.7 s and 14.9 s against 13.1 s).

## How it is fast

Each command splits BGZF block decompression, record decoding, SAM text formatting and BGZF recompression across a D std.parallelism TaskPool. samtools 1.7 threads only the BGZF block (de)compression and formats SAM text on one thread, so its view ran at 193% CPU with -@16 in the guigolab trace. markdup is a two-pass Picard reimplementation: the first pass pairs read ends in a hash table (default 262,144 reads) with an overflow list and LZ4-compressed sorted temporary storage, collects the duplicate indices, and the second pass re-reads the BAM and rewrites the flags. sort holds as much as -m allows in RAM; per test/benchmark/stats.org, giving it 120 GB instead of 20 GB halves its own wall time because the intermediate chunk I/O goes away.

## Compared with alternatives

Use mosdepth instead for depth or coverage (its README times sambamba depth 5.71x slower), and look at mako for template-coordinate sorting. Pick sambamba when the job is BAM duplicate marking, SAM conversion or flagstat on a many-core node and you accept GPL and an older, slower-moving codebase.

## Integration

| | |
|---|---|
| **Form** | CLI binary (static release builds); the BioD D library is in-tree but not packaged as a separate dub library |
| **Dependencies** | LDC (LLVM D compiler) to build, zlib, liblz4; meson+ninja optional (the Makefile's -singleobj LTO release build is the fastest, meson about 5% slower per INSTALL.md) |
| **Minimum toolchain** | LDC &gt;= 1.6.1 per README; 1.0.1 release notes say a recent msgpack was needed for recent ldc2; current builds shown with LDC 1.32 and 1.38 |
| **Platforms** | Linux x86-64 and macOS (Conda, Homebrew, Guix, Debian packages); ARM64 builds since 0.8.0 |
| **Thread safety** | not documented for the library; each CLI command takes -t/--nthreads (default: all cores) |
| **Drop-in for the baseline** | partial: covers view, flagstat, index, sort, markdup, merge, slice and depth with different flags (-t not -@, total -m, Picard-style markdup on coordinate-sorted input, no CRAM); samtools' other subcommands (mpileup, fixmate, collate, stats and others) are not reimplemented |

## Gotchas

- Harness flaw in guigolab/sambamBench-nf: the samtools-1.7 markdup template writes '-@{task.cpus}' without the '\$' in three of its four stages. The resolved script in the report shows the literal string, the thread count never reaches samtools, and the task ran at 102% CPU against 658-890% for sambamba. The 4.49x and 3.62x markdup wins are measured against a single-threaded four-stage pipeline.
- Cold-cache flaw in the same 16 CPU / 120 GB report: the tasks ran one after another, and only the first (sambamba 0.6.8-pre1 view) read the 4.59 GB BAM from disk (read_bytes 4,586,659,840; every later task read under 4 MB). Its 52.8 s and the '1.47x' view figure are therefore a cold-disk number, not a regression. The warm 0.6.6 view row (15.9 s, 4.88x) has no CPU or I/O counters in the trace, and every task ran once.
- The README's 'up to 2x faster than samtools on large RAM machines (120GB+)' has no samtools measurement behind it. test/benchmark/stats.org compares sambamba with itself: sort -N took 8m0s with a 20 GB limit and 3m46s with 120 GB on a 56-core Xeon E5-2683 v3. The only same-machine comparison at 120 GB has samtools 1.7 sorting 1.70x faster.
- Some older Xeons segfault under heavy hyperthreading (README, issue #335), and markdup has open crash and hang reports (#520 segfault, #519 stuck finding positions, #501 range violation). Its D garbage collector sends SIGUSR1/SIGUSR2, which gdb must be told to ignore.

## Known shortcomings

- Markdup baseline crippled: the samtools sort/fixmate/sort/markdup pipeline carries a -@{task.cpus} typo and ran at 102% CPU; the sort claim is contradicted (samtools 1.7 sorts 1.70x faster); view 4.88x holds only for 0.6.6; flagstat 1.49x; samtools at its -O2 default; the gain comes from parallelism, not D (16-CPU report readable at gh-pages report_16_120G.html; public-docs.crg.es unreachable).
- Three harness flaws in guigolab/sambamBench-nf: the samtools-1.7 markdup template writes '-@{task.cpus}' without the '\$' (the resolved script in report_16_120G.html shows the literal), so samtools ran at 102% CPU against 658-890% for sambamba; the first task (sambamba 0.6.8-pre1 view) read 4.59 GB cold from disk while every later task read under 4 MB, so its 52.8 s (1.47x) is a cold-cache artefact and the warm 0.6.6 view row (4.88x) has no CPU or I/O counters; the README's '2x faster than samtools at 120GB+' is really sambamba against itself (stats.org, 20 GB vs 120 GB). samtools 1.7 was built at -O2 with plain zlib (no libdeflate before htslib 1.8). Issue #447: the maintainer recommends samtools sort except on high-RAM machines.

## Caveats and trade-offs

The markdup baseline is crippled: the samtools-1.7 template does two full sorts plus fixmate before markdup, and its sort and fixmate steps pass '-@{task.cpus}' without the '\$', so the thread count is never interpolated; the trace shows 102% CPU for that task versus 658-890% for sambamba. The README's sort claim (up to 2x faster at 120GB+) is contradicted by the 120 GB report, where samtools 1.7 sorts 1.70x faster. The view 4x win holds for sambamba 0.6.6 only (0.6.8-pre1 is 1.47x), and flagstat 1.4x holds for 0.6.8-pre1 only. One run per task, 2018 tool versions (samtools 1.7, sambamba 0.6.x), and the README's linked CRG report does not resolve (getaddrinfo ENOTFOUND public-docs.crg.es). samtools is built at its -O2 default against sambamba's -O3 release build. The README says samtools 1.4 reached parity in many areas and that sambamba's original advantage was parallel BAM I/O; the gains are parallelism and pipeline differences, not D against C. htslib (samtools' library) is listed in wave 8. [retier] The markdup baseline is crippled: the samtools-1.7 template does two full sorts plus fixmate before markdup, and its sort and fixmate steps pass '-@{task.cpus}' without the '\$' (the resolved script in report_16_120G.html shows the literal), so samtools ran at 102% CPU against 658-890% for sambamba; the 4.49x and 3.62x markdup wins are against a single-threaded four-stage pipeline. The first task (sambamba 0.6.8-pre1 view) read 4.59 GB cold from disk while every later task read under 4 MB, so its 52.8 s (1.47x) is a cold-cache artefact and the warm 0.6.6 view row (4.88x) has no CPU or I/O counters. The README's sort claim (up to 2x faster at 120GB+) is sambamba against itself (stats.org, 20 GB vs 120 GB) and the 120 GB report has samtools 1.7 sorting 1.70x faster; issue #447: the maintainer recommends samtools sort except on high-RAM machines. samtools 1.7 was built at -O2 with plain zlib (no libdeflate before htslib 1.8). The CRG report behind the README could not be opened.

Implements an important subset of samtools (view, index, sort, markdup, depth); GPL; wins depend on spare cores since parallel reading and writing is the mechanism.

## Maintenance

Stale: v1.0.1 (August 2023) is the last release and the last commits (December 2024) are build and warning fixes, with markdup crash reports still open; GPL-2.0+, with binaries in Bioconda, Debian, Guix and Homebrew, so usable as a tool but not as a permissively licensed library.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification B, tier now C.
- **Tier reason:** Independent measurement: the Guigó lab's public Nextflow pipeline guigolab/sambamBench-nf (templates/&lt;tool&gt;/&lt;version&gt; command scripts, nextflow.config) ran sambamba 0.6.6 and 0.6.8-pre1 against samtools 1.3 and 1.7 in grape Singularity containers, and its 16-CPU/120 GB report (gh-pages report_16_120G.html) carries per-task wall times; CPU model and compiler flags are not stated, so not A. Tier stays B, but the README's headline claims are overstated (see corrections).
- **Retiered** B to C: Enricher: the markdup baseline in guigolab/sambamBench-nf ran single-threaded because the samtools template drops the '\$' from '-@{task.cpus}', the sambamba view 1.47x row is a cold-cache artefact and the warm 4.88x row has no counters, and the README's '2x faster at 120GB+' compares sambamba with itself. Crippled-baseline precedent: B to C.
- **Verifier notes:** README numbers are first-party quotes of a CRG report that no longer resolves; the pipeline's accessible 16-CPU report shows real flagstat (1.49x) and view (1.47-4.88x) wins, parity on index, a samtools win on sort (1.70x), and a markdup win against a crippled single-threaded four-stage samtools pipeline. Downgraded for the overstated markdup and sort claims; tier B kept on the independent pipeline. Record shortcomings: crippled markdup baseline, contradicted sort claim, 2018 versions, single runs, samtools -O2 default against sambamba -O3, parallelism rather than a D language effect.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** verifier batch-67 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/biod/sambamba/HEAD/README.md>
  - <https://raw.githubusercontent.com/biod/sambamba/HEAD/test/benchmark/stats.org>
  - <https://github.com/biod/sambamba>
  - <https://github.com/biod/sambamba/commits/master>
  - <https://github.com/guigolab/sambamBench-nf>
  - <https://raw.githubusercontent.com/guigolab/sambamBench-nf/HEAD/README.md>
  - <https://raw.githubusercontent.com/guigolab/sambamBench-nf/HEAD/nextflow.config>
  - <https://raw.githubusercontent.com/guigolab/sambamBench-nf/HEAD/main.nf>
  - <https://github.com/guigolab/sambamBench-nf/tree/master/templates>
  - <https://raw.githubusercontent.com/guigolab/sambamBench-nf/HEAD/templates/markdup/samtools-1.7>
  - <https://raw.githubusercontent.com/guigolab/sambamBench-nf/HEAD/templates/markdup/sambamba>
  - <https://raw.githubusercontent.com/guigolab/sambamBench-nf/HEAD/templates/view/samtools>
  - <https://raw.githubusercontent.com/guigolab/sambamBench-nf/HEAD/templates/view/sambamba>
  - <https://raw.githubusercontent.com/guigolab/sambamBench-nf/HEAD/templates/sort/samtools>
  - <https://raw.githubusercontent.com/guigolab/sambamBench-nf/HEAD/templates/sort/sambamba>
  - <https://raw.githubusercontent.com/guigolab/sambamBench-nf/HEAD/templates/flagstat/samtools-1.7>
  - <https://raw.githubusercontent.com/guigolab/sambamBench-nf/HEAD/templates/flagstat/sambamba>
  - <https://github.com/guigolab/sambamBench-nf/tree/gh-pages>
  - <https://raw.githubusercontent.com/guigolab/sambamBench-nf/gh-pages/report_16_120G.html>
  - <https://raw.githubusercontent.com/samtools/samtools/1.7/Makefile>
- **Sources the enricher read:**
  - <https://github.com/biod/sambamba>
  - <https://github.com/biod/sambamba/commits/master>
  - <https://github.com/biod/sambamba/issues?q=is%3Aissue+markdup+OR+segfault+OR+wrong>
  - <https://github.com/biod/sambamba/issues/447>
  - <https://github.com/biod/sambamba/issues/461>
  - <https://raw.githubusercontent.com/biod/sambamba/HEAD/README.md>
  - <https://raw.githubusercontent.com/biod/sambamba/HEAD/INSTALL.md>
  - <https://raw.githubusercontent.com/biod/sambamba/HEAD/Makefile>
  - <https://raw.githubusercontent.com/biod/sambamba/HEAD/meson.build>
  - <https://raw.githubusercontent.com/biod/sambamba/HEAD/dub.json>
  - <https://raw.githubusercontent.com/biod/sambamba/HEAD/RELEASE-NOTES.md>
  - <https://raw.githubusercontent.com/biod/sambamba/HEAD/VERSION>
  - <https://raw.githubusercontent.com/biod/sambamba/HEAD/test/benchmark/stats.org>
  - <https://raw.githubusercontent.com/biod/sambamba/HEAD/sambamba/view.d>
  - <https://raw.githubusercontent.com/biod/sambamba/HEAD/sambamba/markdup.d>
  - <https://raw.githubusercontent.com/biod/sambamba/HEAD/sambamba/sort.d>
  - <https://raw.githubusercontent.com/biod/sambamba/HEAD/sambamba/flagstat.d>
  - <https://github.com/guigolab/sambamBench-nf/tree/gh-pages>
  - <https://raw.githubusercontent.com/guigolab/sambamBench-nf/HEAD/README.md>
  - <https://raw.githubusercontent.com/guigolab/sambamBench-nf/HEAD/main.nf>
  - <https://raw.githubusercontent.com/guigolab/sambamBench-nf/HEAD/nextflow.config>
  - <https://raw.githubusercontent.com/guigolab/sambamBench-nf/HEAD/Makefile>
  - <https://raw.githubusercontent.com/guigolab/sambamBench-nf/HEAD/docker/samtools/Dockerfile>
  - <https://raw.githubusercontent.com/guigolab/sambamBench-nf/HEAD/docker/sambamba/Dockerfile>
  - <https://raw.githubusercontent.com/guigolab/sambamBench-nf/HEAD/templates/markdup/samtools-1.7>
  - <https://raw.githubusercontent.com/guigolab/sambamBench-nf/HEAD/templates/markdup/samtools-1.3>
  - <https://raw.githubusercontent.com/guigolab/sambamBench-nf/HEAD/templates/markdup/sambamba>
  - <https://raw.githubusercontent.com/guigolab/sambamBench-nf/HEAD/templates/view/samtools>
  - <https://raw.githubusercontent.com/guigolab/sambamBench-nf/HEAD/templates/view/sambamba>
  - <https://raw.githubusercontent.com/guigolab/sambamBench-nf/HEAD/templates/sort/samtools>
  - <https://raw.githubusercontent.com/guigolab/sambamBench-nf/HEAD/templates/sort/sambamba>
  - <https://raw.githubusercontent.com/guigolab/sambamBench-nf/HEAD/templates/flagstat/samtools-1.7>
  - <https://raw.githubusercontent.com/guigolab/sambamBench-nf/HEAD/templates/flagstat/samtools-1.3>
  - <https://raw.githubusercontent.com/guigolab/sambamBench-nf/HEAD/templates/flagstat/sambamba>
  - <https://raw.githubusercontent.com/guigolab/sambamBench-nf/HEAD/templates/index/samtools-1.7>
  - <https://raw.githubusercontent.com/guigolab/sambamBench-nf/HEAD/templates/index/samtools-1.3>
  - <https://raw.githubusercontent.com/guigolab/sambamBench-nf/HEAD/templates/index/sambamba>
  - <https://raw.githubusercontent.com/guigolab/sambamBench-nf/gh-pages/report_16_120G.html>
  - <https://raw.githubusercontent.com/samtools/htslib/develop/NEWS>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/biod/sambamba`) · [data/wave14/enrich/raw/github_com_biod_sambamba.json](../../../data/wave14/enrich/raw/github_com_biod_sambamba.json) (enrichment confidence 0.78)

</details>
