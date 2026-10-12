# Chapel in Fourmilab floating_point_benchmarks: fbench

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Numerics and arrays](README.md)</sub>

**Tier D** (directional, no numbers) · Study only · `Chapel` · `CC-BY-SA-4.0` · 🔴 abandoned

> Chapel 1.16 port of John Walker's trig-heavy fbench lens ray tracer, timed at 0.53x the run time of a GCC 5.4 -O3 C build on one laptop.

| | |
|---|---|
| **Beats** | C fbench (src/c/fbench.c, glibc libm trig functions) built with GCC 5.4.0 'gcc -Wall -O3 -lm' (src/c/Makefile, no -march), 166,051,660 iterations, mean 296.536 s, 1.7858 us per iteration on the same Dell laptop under Xubuntu. The fbench.html table labels the C row 'GCC 3.2.3 -O3', but the 2017 Chapel and JavaScript notes (src/chapel/README, src/javascript/README) both use this GCC 5.4.0 run. |
| **Claimed result** | fbench.html relative time (C = 1): Chapel 1.16.0 --fast 0.528 (about 1.9x faster than C, derived from page data). src/chapel/README: serial build with CHPL_RT_NUM_THREADS_PER_LOCALE=1, 250,000,000 iterations, mean 235.68 s = 0.9427 us/iteration vs C 1.7858 us/iteration, ratio 0.5279; with the default runtime (two threads even in the serial build) user time was 1.1982 us/iteration. The 0.0314 row is a pariter=64 build on the 64-core server Pallas (14.00 s real for 250,000,000 iterations), parallel Chapel against serial C, not comparable. |
| **Workload** | fbench, a trigonometry-heavy optical ray-tracing kernel; run time per iteration relative to the C version on the same machine. |
| **Metric** | latency |
| **Hardware** | Dell laptop running Xubuntu Linux with eight cores (CPU model not stated); the parallel rows ran on the 64-core Fourmilab server Pallas (CPU not stated). |
| **Compiler and flags** | Chapel 1.16.0 'chpl --fast' (= --no-checks, -O, --specialize); with the GNU backend Chapel 1.16 compiles the generated C at -O3 and, by its defaults (util/chplenv/chpl_arch.py sets CHPL_TARGET_ARCH=native on Linux with CHPL_COMM=none; make/compiler/Makefile.gnu SPECIALIZE_CFLAGS), with -march=native; backend GCC version and the author's CHPL_\* settings not stated. C baseline: GCC 5.4.0 'gcc -Wall -O3 -lm' without -march. |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | no |
| **Adoption** | 6 stars |
| **Last commit** | 2021-09-24 |
| **Links** | [repository](https://github.com/Fourmilab/floating_point_benchmarks) · [benchmark](https://raw.githubusercontent.com/Fourmilab/floating_point_benchmarks/HEAD/Web_pages/fbench.html) |

## Verdict

In October 2017 on an eight-core Dell laptop under Xubuntu (CPU not named), the serial Chapel 1.16.0 build (chpl --fast, one runtime thread) averaged 0.9427 us per iteration over five 250M-iteration runs. The C reference built with GCC 5.4.0 'gcc -Wall -O3 -lm' averaged 1.7858 us per iteration over five 166M-iteration runs, for a ratio of 0.528. The 0.0314 row is 64-thread Chapel on a different 64-core server against serial C.

## Use it when

- As one data point that Chapel's C backend can produce scalar double-precision code at least as fast as straightforward C when built with chpl --fast, for a trig-heavy kernel that cannot be vectorised.
- Iteration-farm parallelism: the pariter=n build split 250,000,000 independent iterations over coforall tasks, 235.68 s serial to 48.57 s on 8 laptop threads, and 459.76 s to 17.17 s with 32 threads in the same pariter=32 build on the 64-core server Pallas.
- As a portable, self-validating floating-point kernel for comparing compilers and libm builds across languages; the repository holds the same algorithm in about 30 languages.

## Skip it when

- As evidence that Chapel beats C in general: the comparison is one laptop run with unequal flags, and the same Chapel code on one thread ran no faster than C on Pallas (see gotchas).
- Fine-grained task parallelism: partrace=true, with four cobegin tasks per iteration, took 16.92 s on one thread against 9.49 s serial for 10,000,000 iterations, and 64.29 s on 8 threads.
- Serial runs with the default runtime: Chapel 1.16 still started two threads (about 200% CPU, 170 s of system time per 250M iterations) until CHPL_RT_NUM_THREADS_PER_LOCALE=1 was set.
- Current toolchains: the port was written for Chapel 1.16.0 (2017) and the repository has not changed since 2021; it has not been checked against current Chapel.
- Reusing the code: CC BY-SA 4.0 is not an OSI software licence, and the flat-surface branch carries a latent port bug (below).

## How it is fast

Nothing in the repository explains it: the author never examined the generated code and gives no mechanism. Both programs make the same glibc libm calls (sin, asin, tan, cos) per iteration. The documented differences are in the build: chpl --fast compiles the generated C at -O3 with -march=native (Chapel 1.16 GNU defaults), while the C Makefile uses plain -O3. The Chapel loop also discards each iteration's result except the last, while C stores into static globals. Which of these produces the 1.9x is not established.

## Compared with alternatives

Pick it only as a trig-dominated scalar data point. For array or compute claims with reproducible harnesses, look at the gfortran plb2 matmul entry (about 6% over clang C) or the D matmul in kostya/benchmarks. The CBQN CRLF and Mojo Mandelbrot entries are SIMD wins with named compilers, while this entry rests on one laptop run on an unnamed CPU.

## Integration

| | |
|---|---|
| **Form** | single Chapel source file (benchmark program), built with the chpl compiler |
| **Dependencies** | Chapel compiler and runtime (1.16.0 used, C back end with GCC), glibc libm |
| **Minimum toolchain** | Chapel 1.16.0 as measured; newer releases not tested |
| **Platforms** | Linux (Xubuntu laptop and the 64-core Fourmilab server Pallas); CPU models not stated |
| **Thread safety** | not applicable; the Chapel runtime starts worker threads even in a serial build unless CHPL_RT_NUM_THREADS_PER_LOCALE=1 |
| **Drop-in for the baseline** | no |

## Gotchas

- The author's own data contradicts the 1.9x. On Pallas, which by his check runs the C program at the laptop's speed (static C binary 301.43 and 300.92 s for 166,051,660 iterations, 1.81 us per iteration), the pariter=32 Chapel build on one thread took 459.76 s for 250,000,000 iterations, 1.84 us per iteration (derived from src/chapel/README). The same per-iteration work showed no Chapel advantage on the second machine.
- The baseline is the likely outlier. The same GCC 5.4.0 C run (1.7858 us per iteration) is 2.7x slower than Firefox 55's JavaScript (0.372 on fbench.html), and the author wrote that a recent C maths library seemed to slow trig by up to a factor of two. GCC 5.4.0 is the Ubuntu 16.04 compiler, and glibc 2.23 there had a known 2-4x maths-function slowdown on AVX machines caused by _dl_runtime_resolve's AVX register saves (Launchpad 1663280, fixed in glibc 2.25; search snippet only). A -march=native build like Chapel's may avoid part of that penalty, but this was not tested.
- Benchmark-code bug in the parallel path: runBenchmark's pariter branch only validates when n == iterations, which cannot happen when n counts to iterations/pariter, so the 0.0314 (64-thread) row was never checked against the reference output. Leftover iterations go to task i == 0, which does not exist in 1..pariter, so counts that are not a multiple of pariter silently drop work. The published 250,000,000 runs divide evenly by 8, 32 and 64.
- Latent port bug: the marginal-ray flat-surface branch computes -(asin(n1/n2))\*sin(a), where C has -asin((n1/n2)\*sin(a)). It is dead code for the all-curved Wyld lens, so results still validate, but a design with a plane surface would trace wrong.

## Known shortcomings

- Baseline is GCC 5.4.0 -O3 (src/chapel/README shares the C run with the JavaScript notes), not 3.2.3; flags unequal since chpl --fast adds -march=native under Chapel 1.16 defaults; same glibc libm on both sides with the mechanism unexplained; CPU not named; the 64-thread row is not comparable. CC-BY-SA-4.0, reference usability.
- The author's own data contradicts the 1.9x: on Pallas the pariter=32 build on 1 thread ran 1.84 us per iteration against static C's 1.81 (derived), so no Chapel edge; the C baseline is likely an outlier (Firefox JS runs at 0.372 of the same C run; a glibc 2.23 AVX slowdown, Launchpad 1663280, is a candidate, untested). Code bug in fbench.chpl's pariter path: validation never runs (n never reaches iterations), so the 0.0314 row is unvalidated, and extras go to a nonexistent task i==0 and are dropped; the flat-surface port bug is confirmed (dead code).

## Caveats and trade-offs

Single-author runs on an unnamed CPU. The C row on fbench.html says GCC 3.2.3, but the Chapel comparison used a GCC 5.4.0 -O3 C run (shared with the JavaScript notes), so the old-compiler confound in the search record is wrong; the real confounds are that the builds are not flag-equivalent (Chapel's --fast adds -march=native by default, the C Makefile has none) and that both sides call the same glibc libm trig functions, whose speed the author himself suspected (src/javascript/README: a recent GCC math library slowed trig 'perhaps by as much as a factor of two'; a glibc 2.23 AVX-SSE transition regression in sin/cos, Ubuntu Launchpad 1663280, is a candidate, search snippet only). The Chapel loop discards each iteration's result except the last (C stores into globals), which lets the backend drop pure arithmetic but not the errno-setting libm calls; not checked in generated code. A latent port bug (flat-surface marginal branch computes -(asin(n1/n2))\*sin(a) instead of -asin((n1/n2)\*sin(a))) is dead code for the all-curved Wyld lens. The 0.0314 row compares 64-thread Chapel with serial C. Chapel 1.16.0 dates from 2017. License is CC BY-SA 4.0 (LICENSE.md), not an OSI software license. [retier] The author's own data contradicts the 1.9x: on Pallas the pariter=32 build on 1 thread ran 1.84 us per iteration against static C's 1.81, so no Chapel edge; the C baseline is likely an outlier (Firefox JS runs at 0.372 of the same C run). fbench.chpl's pariter path never runs validation (n never reaches iterations), so the 0.0314 row is unvalidated, and extras go to a nonexistent task and are dropped; the flat-surface port bug is confirmed (dead code).

## Maintenance

Abandoned reference material: last commit 2021-09-24 (5 commits, 6 stars), Chapel port and numbers from 2017, CC BY-SA 4.0; the C and Chapel sources are short enough to re-run, and a re-run with matched -march flags and a current glibc is needed before the 1.9x can be trusted.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now D.
- **Tier reason:** fbench.html lists Chapel 1.16.0 -fast at 0.528 and the 64-thread run at 0.0314 against C = 1, and src/chapel/README gives the raw runs (Chapel serial 0.9427 us/iteration with one runtime thread vs C 1.7858 us/iteration, ratio 0.5279, five runs each on the same laptop); code (src/chapel/fbench.chpl, src/c/fbench.c) and flags (src/chapel/Makefile --fast, src/c/Makefile -O3) are public, but the CPU is never named and the two builds use different flags, so C.
- **Retiered** C to D: Enricher: the author's own pariter build on one thread runs 1.84 us per iteration against C's 1.81, the compared C run is a likely outlier, and the pariter path never validates its result; the 1.9x has no valid like-for-like measurement behind it: C to D.
- **Verifier notes:** Numbers on fbench.html and src/chapel/README match the record; tier stays C. Shortcomings: baseline is GCC 5.4.0 -O3 (not 3.2.3) on an unnamed CPU, Chapel build adds -march=native, same libm underneath, mechanism unexplained, parallel row not comparable, license CC BY-SA 4.0 (corrected from null).
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `license`, `caveats`
- **Shortcomings recorded by:** verifier batch-80 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/Fourmilab/floating_point_benchmarks/HEAD/Web_pages/fbench.html>
  - <https://raw.githubusercontent.com/Fourmilab/floating_point_benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/Fourmilab/floating_point_benchmarks/HEAD/LICENSE.md>
  - <https://github.com/Fourmilab/floating_point_benchmarks>
  - <https://github.com/Fourmilab/floating_point_benchmarks/commits>
  - <https://github.com/Fourmilab/floating_point_benchmarks/tree/master/src>
  - <https://raw.githubusercontent.com/Fourmilab/floating_point_benchmarks/HEAD/src/Makefile>
  - <https://raw.githubusercontent.com/Fourmilab/floating_point_benchmarks/HEAD/src/c/Makefile>
  - <https://raw.githubusercontent.com/Fourmilab/floating_point_benchmarks/HEAD/src/c/fbench.c>
  - <https://github.com/Fourmilab/floating_point_benchmarks/tree/master/src/chapel>
  - <https://raw.githubusercontent.com/Fourmilab/floating_point_benchmarks/HEAD/src/chapel/README>
  - <https://raw.githubusercontent.com/Fourmilab/floating_point_benchmarks/HEAD/src/chapel/Makefile>
  - <https://raw.githubusercontent.com/Fourmilab/floating_point_benchmarks/HEAD/src/chapel/fbench.chpl>
  - <https://raw.githubusercontent.com/Fourmilab/floating_point_benchmarks/HEAD/src/javascript/README>
  - <https://raw.githubusercontent.com/chapel-lang/chapel/release/1.16/man/chpl.rst>
  - <https://raw.githubusercontent.com/chapel-lang/chapel/release/1.16/make/compiler/Makefile.gnu>
  - <https://raw.githubusercontent.com/chapel-lang/chapel/release/1.16/util/chplenv/chpl_arch.py>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/Fourmilab/floating_point_benchmarks/HEAD/Web_pages/fbench.html>
  - <https://raw.githubusercontent.com/Fourmilab/floating_point_benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/Fourmilab/floating_point_benchmarks/HEAD/LICENSE.md>
  - <https://raw.githubusercontent.com/Fourmilab/floating_point_benchmarks/HEAD/src/Makefile>
  - <https://raw.githubusercontent.com/Fourmilab/floating_point_benchmarks/HEAD/src/c/Makefile>
  - <https://raw.githubusercontent.com/Fourmilab/floating_point_benchmarks/HEAD/src/c/fbench.c>
  - <https://raw.githubusercontent.com/Fourmilab/floating_point_benchmarks/HEAD/src/chapel/README>
  - <https://raw.githubusercontent.com/Fourmilab/floating_point_benchmarks/HEAD/src/chapel/Makefile>
  - <https://raw.githubusercontent.com/Fourmilab/floating_point_benchmarks/HEAD/src/chapel/fbench.chpl>
  - <https://raw.githubusercontent.com/Fourmilab/floating_point_benchmarks/HEAD/src/javascript/README>
  - <https://raw.githubusercontent.com/chapel-lang/chapel/release/1.16/man/chpl.rst>
  - <https://raw.githubusercontent.com/chapel-lang/chapel/release/1.16/make/compiler/Makefile.gnu>
  - <https://github.com/Fourmilab/floating_point_benchmarks>
  - <https://github.com/Fourmilab/floating_point_benchmarks/commits>
  - https://lists.snapcraft.io/archives/foundations-bugs/2018-June/360669.html (WebSearch snippet only)
  - https://bugzilla.redhat.com/show_bug.cgi?id=1421121 (WebSearch snippet only)
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:chapel/fourmilab/floating_point_benchmarks#fbench`) · [data/wave14/enrich/raw/lang_chapel_fourmilab_floating_point_benchmarks_fbench.json](../../../data/wave14/enrich/raw/lang_chapel_fourmilab_floating_point_benchmarks_fbench.json) (enrichment confidence 0.65)

</details>
