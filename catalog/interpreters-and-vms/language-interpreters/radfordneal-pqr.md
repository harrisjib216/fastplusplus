# pqR (a pretty quick implementation of R)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Language interpreters](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `GPL-2.0-only OR GPL-3.0-only` · 🔴 abandoned

> Radford Neal's fork of GNU R 2.15 with a faster interpreter, GC and builtins; beats R-3.4/3.5 on many operations.

| | |
|---|---|
| **Beats** | GNU R (derived from R-2.15.0; the NEWS compares with R-3.4.0) |
| **Claimed result** | NEWS (release 2018-11-18): paste and paste0 are 'about two to six times faster than in R-3.4.0, and are usually faster than the stri_paste function from the stringi package'. Other GNU R comparisons in NEWS: the rewritten parser (release 2015-09-14) is 'usually about a factor of 1.5 faster than the parser in R-3.2.2' and sometimes enormously faster; rep and rep.int (release 2014-09-30) are 'often substantially faster in pqR than in R-2.15.2 or later R Core versions to at least R-3.1.1'. The 'up to a factor two or more' gain for replacing parts of vectors or lists with [ ], [[ ]] and \$ is from the 2016-10-05 release and is relative to the previous pqR release, not to GNU R. |
| **Workload** | Assorted R operations named in the release notes, for example paste and paste0 on character vectors and replacing parts of vectors or lists; the README states that the modifications substantially improve the speed of R. |
| **Metric** | throughput |
| **Adoption** | 240 stars |
| **Last commit** | 2020-07-23 |
| **Links** | [repository](https://github.com/radfordneal/pqR) · [benchmark](https://raw.githubusercontent.com/radfordneal/pqR/HEAD/NEWS) |

## Verdict

All numbers are first-party: NEWS says paste/paste0 are 2-6x faster than R-3.4.0 and the parser about 1.5x faster than R-3.2.2, and the author's 2018-11-25 blog (WebSearch snippet only, blog blocked here) times a[2:19999] &lt;- 3.1 run 100,000 times at 0.257 s versus 4.360 s in R-3.5.1, both built with gcc 8.2.0 -O3 on an Intel Skylake. No benchmark scripts are in the repo; the only third-party timing found (issue #49) shows GNU R 4.0.3 about 2.4x faster than pqR on simple scalar loops.

## Use it when

- Legacy R-2.15-era scripts dominated by vector or list subassignment (x[a:b] &lt;- v, l\$x &lt;- v), paste/paste0, number-string conversion, sample() of few items from a large set, or sort/order, where the release notes and author timings show several-fold gains over R-3.4/3.5.
- Machines with spare cores running long-vector arithmetic: helper threads (pqR --helpers N) parallelize and pipeline elementwise math and matrix products with no code changes.
- Work that needs bit-reproducible floating point: pqR forces -ffp-contract=off, checks for fused multiply-add at startup and its matrix products reproduce naive sequential summation.
- Studying how to speed up an R-style interpreter: NEWS, MODS and the R Internals manual document each optimization.

## Skip it when

- Any project that needs current R: NEWS back-ports items only up to about R-3.5, so R 4.x features (for example the native |&gt; pipe) are absent, and CRAN packages requiring R &gt;= 3.x usually fail to install or need DESCRIPTION edits.
- Scalar-loop-heavy code: GitHub issue #49 (2021) times while/repeat loops decrementing a counter 1e6 times at about 97 ms in pqR 2.15.1 versus about 41/36 ms in GNU R 4.0.3, so modern R with its default byte-compiler JIT is about 2.4x faster there.
- Production use: abandoned since 2020-07-23, with open crash reports (#43 buffer overflow with attributes on a recursive function, #44 floating point exception, #45 abort in plot) and open build failures on Ubuntu 20.04 (#46) and Slackware 15.0 (#48).
- BLAS-bound linear algebra: the built-in matprod routines are by NEWS's own account up to about 2x slower than OpenBLAS (an external BLAS can be linked, losing the reproducibility guarantee).
- Windows or RStudio-centric setups: no Windows binary (issue #34), RStudio needs --enable-R-shlib, and a Mac GUI issue with helper threads (#17) is open.

## How it is fast

The speed comes from many interpreter-level changes rather than a JIT: a 3-bit NAMEDCNT reference count that avoids needless duplication, unmaterialized integer sequences (for (i in 1:n) and x[101:200] allocate no index vector), in-place vector growth and subassignment, 'static boxes' and a scalar stack for scalar results, and fused operations such as sum(vec&gt;0) without the intermediate. A deferred-evaluation framework does 'task merging' (exp(v+1) in one loop) and runs long vector operations in OpenMP 'helper threads' with pipelining between tasks. Memory uses the Segmented Generational Garbage Collector (radfordneal/sggc) with optional 32-bit compressed pointers. Builtins were rewritten piecemeal: a recursive-descent parser, hashed sample(), faster paste/substr/number-to-string conversion, serialize without Sun XDR, data.table's radix sort plus a merge sort, and a SIMD matrix multiply (matprod) that keeps naive summation order.

## Compared with alternatives

It is the only R implementation catalogued; unlike PyPy, TruffleRuby or LuaJIT it is an evolved fork of the reference interpreter with no JIT, so choose it only to run R-2.15-compatible code faster where vector and string builtins dominate, not as a general accelerator for modern R.

## Integration

| | |
|---|---|
| **Form** | Full interpreter built from source (configure && make); optional shared libR with --enable-R-shlib |
| **Dependencies** | C, C++ and Fortran compilers (gcc/gfortran per INSTALL), OpenMP 3.0/3.1 for helper threads, system zlib, bzip2, pcre and xz/liblzma dev packages; optional external BLAS/LAPACK |
| **Minimum toolchain** | C99 (INSTALL suggests CC='gcc -std=gnu99') plus gfortran; the 2020-07-23 release adds fixes for gcc-10 and recent gfortran; newer toolchains not documented |
| **Platforms** | Linux and other Unix including macOS and Solaris (INSTALL); Windows only by building from src/gnuwin32; requires correct 64-bit IEEE double (no x87-only Pentium III or earlier) |
| **Thread safety** | R code runs in one interpreter thread; helper threads parallelize internal vector tasks; an external BLAS is assumed not thread-safe unless configured with BLAS_in_helpers=TRUE |
| **Drop-in for the baseline** | partial — source-compatible with R-2.15.1 scripts, but compiled packages must be reinstalled and most packages built for R 3.x/4.x are not supported |

## Gotchas

- The byte compiler is off by default and the JIT can never be enabled; byte-compiled code bypasses task merging, helper threads and unmaterialized sequences, so forcing it (R_USE_BYTECODE=TRUE) usually slows pqR down.
- --enable-compressed-pointers saves memory but slows the interpreter by up to about 40% (INSTALL; NEWS says up to about 30%), and packages with C code must be built with the same compressed-pointer and aux-for-attrib settings as the interpreter.
- Behaviour differs from GNU R in places: necessary parentheses are dropped from parsed expressions (breaks formula-sensitive packages such as coxme), else at the start of a top-level line is accepted, and the interpreter aborts on a PROTECT stack imbalance that GNU R only warns about.
- The headline gains are microbenchmarks of single operations; the author's 17x figure times one statement (a[2:19999] &lt;- 3.1) that exercises pqR's no-index-vector range subscript path.

## Known shortcomings

- First-party NEWS claims only: '2-6x faster than R-3.4.0' applies to paste/paste0, the 'up to 2x' vector and list replacement figure was against an earlier pqR release (2016-10-05) rather than GNU R, and the author's 2018 blog numbers (17x vector replacement over R-3.5.1, GC 14.129 s vs 8.257 s on Skylake) are snippet only. No bench script, compiler or CPU; based on R-2.15, own matmul under 2x slower than OpenBLAS, abandoned since 2020-07-23. Off-baseline (GNU R).
- Enricher: no bench scripts in the repo; third-party issue #49 shows GNU R 4.0.3 about 2.4x faster on scalar while and repeat loops (41/36 ms vs 97/93 ms); the blog's 17x (snippet only) is one statement, a[2:19999] &lt;- 3.1, with gcc 8.2.0 -O3 on Skylake. Open crash issues #43, #44, #45, build failures #46 and #48, status issue #50 (2024) unanswered.

## Caveats and trade-offs

Claims are release-note statements without a benchmark script, hardware or compiler flags; the main baseline (R-3.4.0, 2017) is old and modern GNU R 4.x with the byte compiler/JIT may have closed some gaps. The record's vector/list replacement speedup was measured against an earlier pqR, not GNU R. The author's blog post 'New version of pqR, with major speed improvements' (2018-11-25) reports, per WebSearch snippets only (blog, r-bloggers and pqR-project.org are blocked here), a vector element replacement test taking 4.360 s in R-3.5.1 versus 0.257 s in pqR-2018-11-18 on an Intel Skylake (about 17x), another arithmetic/conditional test almost 2x faster, and a garbage-collection test at 14.129 s (R-3.5.1, JIT on) versus 8.257 s; these are first-party and their scripts were not opened. NEWS also says pqR's own matrix multiplication is generally less than a factor of two slower than optimized BLAS such as OpenBLAS (not faster). A third-party paper ('Database-Inspired Optimizations for Statistical Analysis', snippet only) found Renjin outperforming both GNU R and pqR in its scenarios. Based on R-2.15.0/2.15.1, so newer R language features and packages may be incompatible. Last commit on every branch is 2020-07-23.

Source-compatible modification of R-2.15.0 (with some modules from R-2.15.1 and later), so it lags current R releases and package compatibility; adds some language extensions such as preliminary automatic differentiation. Includes the R packages and Fortran/C sources of the R distribution.

## Maintenance

Abandoned: last commit 2020-07-23, 21 open issues including an unanswered 2024 'Status of the project?' (#50); GPL-2 or GPL-3, usable for running legacy R-2.15-era code or as a reference for interpreter optimizations, not as a current R replacement.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** The NEWS file (2018-11-18 release section) states paste/paste0 are about two to six times faster than in R-3.4.0, a first-party statement with no benchmark script, compiler, flags or CPU model; the author's 2018 blog timings against R-3.5.1 (seen as WebSearch snippets only, blog blocked) are also first-party, so tier C.
- **Verifier notes:** Real, notable alternative R interpreter by Radford Neal; tier C stays (first-party release notes and blog numbers only, no published methodology). Metadata checked on github.com: 240 stars, 16 forks, not a fork, not archived, default branch Release-2020-07-23 with last commit 2020-07-23 (no newer branch), README says GPL version 2 or version 3, so license, usability copyable and abandoned status stand. Shortcomings to record: old baseline (R-3.4.0/R-3.5.1), no benchmark scripts or hardware/compiler details in the repo, record misattributed the vector-replacement gain (it was vs earlier pqR), project abandoned since 2020 and based on R-2.15.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/radfordneal/pqR/HEAD/NEWS>
  - <https://raw.githubusercontent.com/radfordneal/pqR/HEAD/README>
  - <https://github.com/radfordneal/pqR>
  - <https://github.com/radfordneal/pqR/commits>
  - <https://github.com/radfordneal/pqR/branches/all>
  - <https://github.com/radfordneal?tab=repositories>
- **Sources the enricher read:**
  - <https://github.com/radfordneal/pqR>
  - <https://raw.githubusercontent.com/radfordneal/pqR/HEAD/README>
  - <https://raw.githubusercontent.com/radfordneal/pqR/HEAD/NEWS>
  - <https://raw.githubusercontent.com/radfordneal/pqR/HEAD/INSTALL>
  - <https://raw.githubusercontent.com/radfordneal/pqR/HEAD/MODS>
  - <https://raw.githubusercontent.com/radfordneal/pqR/HEAD/VERSION>
  - <https://github.com/radfordneal/pqR/issues>
  - <https://github.com/radfordneal/pqR/issues/49>
  - <https://github.com/radfordneal/pqR/issues/50>
  - <https://github.com/radfordneal/pqR/wiki>
  - <https://github.com/radfordneal?tab=repositories>
  - <https://raw.githubusercontent.com/radfordneal/xsum/HEAD/README>
  - <https://raw.githubusercontent.com/radfordneal/matprod/HEAD/README>
  - WebSearch: pqR Radford Neal speed tests R-3.5.1 vector element replacement (snippets of radfordneal.wordpress.com/2018/11/25 and r-bloggers; radfordneal.wordpress.com EGRESS_BLOCKED)
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/radfordneal/pqr`) · [data/wave12/enrich/raw/github_com_radfordneal_pqr.json](../../../data/wave12/enrich/raw/github_com_radfordneal_pqr.json) (enrichment confidence 0.6)

</details>
