# Bigloo Scheme

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Language interpreters](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Scheme/C` · `GPL-2.0-or-later (compiler and tools) AND LGPL-2.0-or-later (run-time system and libraries, 'GNU Library General Public License' per the repo LICENSE file)` · 🟢 active

> Optimizing Scheme-to-C (and JVM) compiler; about 1.6x faster than Guile 3.0.11 on the ecraven R7RS suite, slower than Chez.

| | |
|---|---|
| **Beats** | Guile 3.0.11 (guild compile -O3); Chez Scheme 10.3.0 also in the same suite (Bigloo is slower than Chez on aggregate) |
| **Claimed result** | From all.csv (derived from page data): bigloo-4.6a is faster than guile-3.0.11 on 36 of 50 shared benchmarks, geomean about 1.62x. Examples: fib:40:5 2.564524032 s vs 6.489886582 s; tak:40:20:11:1 1.762351104 vs 3.113433651; mbrot:75:1000 15.49738496 vs 22.496891153; cat:50 1.918521088 vs 15.986089402; sum1:25 0.335073792 vs 5.443149564; string:500000:100 0.438892032 vs 0.204681098 (slower than Guile); graphs:7:3 20.211041024 vs 6.8123056 (slower). Versus chez-10.3.0+r7rs the same method gives geomean about 0.63x. |
| **Workload** | ecraven/r7rs-benchmarks: wall-clock seconds of R7RS benchmark programs, Bigloo '-O6 -call/cc -copt -O3' native executable versus Guile precompiled with guild compile -O3. |
| **Metric** | throughput |
| **Hardware** | Intel Core i3-N305 @ 3.8 GHz, 48 GB RAM, Arch Linux packages (per the suite's index.html); results logs show host kernel Linux 6.16.8-arch3-1 x86_64; Bigloo and Guile runs dated 2026-01-16. |
| **Compiler and flags** | bench script: bigloo '&lt;file&gt; -O6 -call/cc -copt -O3 -o &lt;out&gt;' (C backend; the C compiler is the Arch Linux gcc, version not stated); Guile 'guild compile -O3' with GC_INITIAL_HEAP_SIZE=100000000; Chez '--optimize-level 2 --program'; versions bigloo-4.6a, guile-3.0.11, chez-10.3.0+r7rs; one run per benchmark (NB_RUNS=1), times are the in-program elapsed time printed per benchmark. |
| **Adoption** | 174 stars |
| **Last commit** | 2026-09-15 |
| **Links** | [repository](https://github.com/manuel-serrano/bigloo) · [benchmark](https://raw.githubusercontent.com/ecraven/r7rs-benchmarks/master/all.csv) |

## Verdict

In ecraven/r7rs-benchmarks (independent; Intel Core i3-N305, Arch Linux, single run each, safe mode), Bigloo 4.6a compiled with '-O6 -call/cc -copt -O3' through gcc beat Guile 3.0.11 (guild compile -O3) on 36 of 50 shared programs, with a geomean of 1.62x (derived from all.csv), e.g. fib 2.56 s vs 6.49 s and tak 1.76 s vs 3.11 s. Seven Bigloo rows failed or crashed and were excluded. In the same run, Chez Scheme 10.3.0 at --optimize-level 2 was about 1.6x faster than Bigloo on aggregate.

## Use it when

- You want standalone native executables or C-linkable libraries from Scheme and need a large win over Guile on CPU-bound integer, flonum and list code (fib, tak, fft, peval and lattice ran 2.2x to 3.4x faster than Guile 3.0.11 -O3)
- I/O-heavy text processing with ports (read1, cat, wc, tail, sum1 ran 5x to 16x faster than Guile)
- Projects that call C or Java libraries directly through an FFI, or that need Bigloo's object system, pattern matching and parser generators in compiled code
- Server-side or systems Scheme on Linux that uses the bundled pthread, SSL, SQLite, libuv and socket libraries from compiled code

## Skip it when

- When top speed is the goal: Chez Scheme 10.3.0 beats Bigloo 4.6a on aggregate in the same suite (Bigloo about 0.63x of Chez's speed, faster on 18 of 50 rows), and Gambit (0.78x) and Loko (0.73x) are also faster on aggregate (derived from all.csv)
- Continuation-heavy code: first-class call/cc needs the -call/cc flag, fibc ran at 0.35x Guile's speed, ctak was killed at the 300 s limit, and on the JVM back end call/cc only works within its dynamic extent
- Strict R7RS programs: there are no complex numbers (mbrotZ failed with 'Unbound variable -- imag-part'), and the compiler, slatex and equal benchmarks failed to compile, crashed or hit the time limit
- Allocation-heavy symbolic workloads where Guile was faster: graphs 0.34x, nboyer 0.62x, gcbench 0.67x, string 0.47x
- Interactive development with an embeddable VM: Bigloo is a batch whole-program compiler, and building it from git needs an existing Bigloo to bootstrap

## How it is fast

Scheme is compiled ahead of time to C and then optimized by gcc, so the program runs as native code with no bytecode dispatch. The compiler front end does closure analysis (control-flow analysis, comptime/Cfa), type and storage-use inference, inlining, beta reduction, dataflow type specialization, tagged-fixnum and flonum specialization (Fxop, Flop, Fastfl), box/unbox elimination (Prebox, Uncell), and tail-call and return-to-goto rewriting. -O6 adds stack allocation of non-escaping values (Stackable), numeric specialization (Nums) and fast flonums on top of -O3 (comptime/Init/parse_args.scm). Memory is managed by a bundled Boehm-Demers-Weiser conservative GC (gc-8.2.12 at head).

## Compared with alternatives

Pick Bigloo over Chez Scheme, Gambit Scheme or Loko when you need Scheme compiled through C or to the JVM with a direct C/Java FFI, an object system and bundled SSL/SQLite/libuv libraries. If raw speed on this suite is what matters, Chez (about 1.6x faster than Bigloo on aggregate), Gambit and Loko all beat it.

## Integration

| | |
|---|---|
| **Form** | compiler toolchain (bigloo executable) producing native executables or static/shared libraries via C; separate JVM back end |
| **Dependencies** | a C compiler and GNU make; bundled Boehm GC (gc-8.2.12), libuv (v1.51.0), PCRE/PCRE2, GMP (6.3.0 if none found) and libbacktrace; optional OpenSSL, SQLite, libunistring and multimedia libraries; JDK for the JVM back end |
| **Minimum toolchain** | not documented; CI builds with the ubuntu-latest gcc, and closed issues cover clang-16 (#98) and gcc-15 (#149) fixes |
| **Platforms** | Linux x86-64 is the only CI target; configure has options for macOS (darwin), Win32 (mingw, cygwin) and Android; a musl/Alpine build issue (#125) was closed in 2025 |
| **Thread safety** | Preemptive threads through the pthread and srfi18 libraries plus FairThreads (fthread), with a thread-enabled Boehm GC; per-object thread safety is not documented |
| **Drop-in for the baseline** | partial: runs most portable R7RS benchmark programs once a prelude adds missing R7RS procedures, but it has no Guile module system, no Guile C API and no complex numbers |

## Gotchas

- The headline 1.62x geomean over Guile is lifted by five I/O rows (sum1 16.2x, read1 12.7x, cat 8.3x, wc 7.0x, tail 5.3x). Without them it is about 1.33x, faster on 31 of 45 rows, and about 0.57x of Chez (derived from all.csv).
- Harness flaw: the ecraven Bigloo prelude defines exact-integer-sqrt through a float-based integer-length, (ceiling (/ (log n) (log 2))). That overflows for bignums above about 1.8e308 and is off by one at exact powers of two, so the pi and chudnovsky 'floating point exception' crashes are probably the prelude's fault rather than Bigloo's. These rows are excluded from the ratios, so the result is not inflated.
- The same prelude rebinds error (to return its arguments) and call-with-current-continuation at top level, and Bigloo warns 'Disabling optimization for library function' for both. Results are in safe mode: -O6 without -unsafe. Bigloo's own -Obench mode adds -unsafe, -freturn and static linking, so it could run faster than the suite shows.
- Each benchmark was run once (NB_RUNS=1) on a low-power i3-N305 with the Arch gcc, version unstated. The suite ran 4.6a while the repo head is 4.7b (unstable) and a 4.7a tarball exists (issue #147); Bigloo timestamps come from epoch nanoseconds converted to a double, so they are quantised to 256 ns (irrelevant at second scale).

## Known shortcomings

- ecraven/r7rs-benchmarks all.csv (Intel Core i3-N305, 48 GB, Arch Linux): 36 of 50 rows faster than Guile 3.0.11, geomean 1.615x (derived from page data), but slower than the listed Chez Scheme (0.63x), slower than Guile on 14 rows, 7 failed or crashed rows, one run each, backend gcc version not stated. Licence: compiler GPL-2.0-or-later, runtime LGPL.
- Enricher: the 1.62x geomean over Guile is lifted by five I/O rows (sum1 16.2x, read1 12.7x, cat 8.3x, wc 7.0x, tail 5.3x); without them it is about 1.33x, faster on 31 of 45 rows, and about 0.57x of Chez (derived from all.csv). The ecraven Bigloo prelude defines exact-integer-sqrt through a float-based integer-length that overflows for huge bignums and is off by one at powers of two, so the pi and chudnovsky crashes are probably the prelude's fault (excluded rows). Results are in safe mode (-O6 without -unsafe); Bigloo's own -Obench adds -unsafe. One run each, gcc version unstated, suite ran 4.6a against head 4.7b.

## Caveats and trade-offs

Independent community suite run on an Intel Core i3-N305 (low-power 8-core Alder Lake-N) with Arch packages; the page says 'No guarantees for any of the numbers', each benchmark is run once, and the gcc version behind Bigloo's C backend is not stated, so tier B. Bigloo has failed or crashed rows in all.csv (ctak ULIMITKILLED, mbrotZ COMPILEERROR, pi CRASHED, compiler COMPILEERROR, slatex CRASHED, chudnovsky CRASHED, equal ULIMITKILLED) which are excluded from the derived geomean. Bigloo's repo has a bench/ directory (bague, earley, fft, maze, etc.) but no committed comparison with Guile or Chez was found. Chez Scheme (already listed) beats Bigloo on aggregate (about 0.63x derived, Bigloo faster on 18 of 50 shared rows), and Bigloo loses to Guile on 14 of 50 shared rows (deriv, destruc, diviter, divrec, puzzle, cpstak, fibc, ack, string, earley, graphs, matrix, nboyer, gcbench). Lua not part of the suite. Bigloo 4.6a in the suite is not necessarily the repo head. [retier] ecraven/r7rs-benchmarks (Intel Core i3-N305, one run each, gcc version unstated, Bigloo 4.6a in safe mode -O6 without -unsafe): 36 of 50 rows faster than Guile 3.0.11, geomean 1.615x, lifted by five I/O rows (sum1 16.2x, read1 12.7x, cat 8.3x, wc 7.0x, tail 5.3x); about 1.33x without them and about 0.57x of Chez (derived from page data). 7 failed or crashed rows, probably from the suite's float-based exact-integer-sqrt prelude. Compiler GPL-2.0-or-later, runtime LGPL.

Scheme to C (and JVM) compiler; per the repo LICENSE file the compiler and tools are GPL (version 2 or later) and the run-time system and libraries are under the GNU Library General Public License (version unspecified); bootstrapping the git version needs an existing Bigloo (configure downloads one if none is found). '-call/cc' build option used in the benchmark.

## Maintenance

Actively maintained by Manuel Serrano (last commit 2026-09-15; a 4.7a tarball was published in 2026 per issue #147; 5 open issues). The runtime and libraries are under the GNU Library GPL, so compiled programs can link them, while the compiler itself is GPL-2.0-or-later.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification B, tier now B.
- **Tier reason:** Well-known independent suite (ecraven/r7rs-benchmarks: public bench script and src/ programs, Scheme compiler versions and flags stated, CPU Intel i3-N305 stated in the repo's index.html), but Bigloo compiles through the Arch gcc whose version is not stated anywhere, so it falls just short of A.
- **Verifier notes:** All quoted numbers and the derived ratios re-computed from all.csv (36 of 50 faster than Guile, geomean 1.615x; versus Chez 0.629x). Shortcomings: slower than already-listed Chez on aggregate, slower than Guile on 14 of 50 rows, seven failed/crashed rows, single run on a low-power i3-N305, backend gcc version unstated. The repo LICENSE splits licences: compiler GPL-2.0-or-later, runtime and libraries GNU Library GPL.
- **Fields the verifier corrected:** `hardware`, `license`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** repeated runs with stated gcc version; repeated runs with -Obench and a fixed prelude
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/ecraven/r7rs-benchmarks/master/all.csv>
  - <https://raw.githubusercontent.com/ecraven/r7rs-benchmarks/master/README.org>
  - <https://raw.githubusercontent.com/ecraven/r7rs-benchmarks/master/bench>
  - <https://raw.githubusercontent.com/ecraven/r7rs-benchmarks/master/index.html>
  - <https://raw.githubusercontent.com/ecraven/r7rs-benchmarks/master/results.Guile>
  - <https://github.com/ecraven/r7rs-benchmarks>
  - <https://github.com/ecraven/r7rs-benchmarks/commits>
  - <https://raw.githubusercontent.com/ecraven/r7rs-benchmarks/master/results.Bigloo>
  - <https://github.com/manuel-serrano/bigloo>
  - <https://github.com/manuel-serrano/bigloo/commits>
  - <https://github.com/manuel-serrano/bigloo/tree/master/bench>
  - <https://raw.githubusercontent.com/manuel-serrano/bigloo/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/manuel-serrano/bigloo/HEAD/COPYING>
  - <https://raw.githubusercontent.com/manuel-serrano/bigloo/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/manuel-serrano/bigloo>
  - <https://github.com/manuel-serrano/bigloo/commits/master>
  - <https://github.com/manuel-serrano/bigloo/tree/master/comptime>
  - <https://github.com/manuel-serrano/bigloo/issues?q=is%3Aissue>
  - <https://github.com/manuel-serrano/bigloo/issues/147>
  - <https://github.com/manuel-serrano/bigloo/issues/119>
  - <https://raw.githubusercontent.com/manuel-serrano/bigloo/HEAD/README.md>
  - <https://raw.githubusercontent.com/manuel-serrano/bigloo/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/manuel-serrano/bigloo/HEAD/COPYING>
  - <https://raw.githubusercontent.com/manuel-serrano/bigloo/HEAD/INSTALL.md>
  - <https://raw.githubusercontent.com/manuel-serrano/bigloo/HEAD/configure>
  - <https://raw.githubusercontent.com/manuel-serrano/bigloo/HEAD/.github/workflows/bigloo.yml>
  - <https://raw.githubusercontent.com/manuel-serrano/bigloo/HEAD/comptime/Init/parse_args.scm>
  - <https://raw.githubusercontent.com/ecraven/r7rs-benchmarks/master/all.csv>
  - <https://raw.githubusercontent.com/ecraven/r7rs-benchmarks/master/bench>
  - <https://raw.githubusercontent.com/ecraven/r7rs-benchmarks/master/README.org>
  - <https://raw.githubusercontent.com/ecraven/r7rs-benchmarks/master/index.html>
  - <https://raw.githubusercontent.com/ecraven/r7rs-benchmarks/master/results.Bigloo>
  - <https://raw.githubusercontent.com/ecraven/r7rs-benchmarks/master/results.Guile>
  - <https://raw.githubusercontent.com/ecraven/r7rs-benchmarks/master/src/Bigloo-prelude.scm>
  - <https://raw.githubusercontent.com/ecraven/r7rs-benchmarks/master/src/Guile-prelude.scm>
  - <https://raw.githubusercontent.com/ecraven/r7rs-benchmarks/master/src/common.scm>
  - <https://raw.githubusercontent.com/ecraven/r7rs-benchmarks/master/src/common-postlude.scm>
  - <https://raw.githubusercontent.com/ecraven/r7rs-benchmarks/master/src/pi.scm>
  - <https://raw.githubusercontent.com/ecraven/r7rs-benchmarks/master/src/chudnovsky.scm>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/manuel-serrano/bigloo`) · [data/wave12/enrich/raw/github_com_manuel_serrano_bigloo.json](../../../data/wave12/enrich/raw/github_com_manuel_serrano_bigloo.json) (enrichment confidence 0.8)

</details>
