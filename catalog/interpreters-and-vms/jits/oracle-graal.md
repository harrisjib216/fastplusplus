# Graal compiler (GraalVM JIT)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [JIT compilers](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Java` · `GPL-2.0-with-classpath-exception` · 🟢 active

> Java-written optimizing JIT that replaces HotSpot's C2; 16% lower time-per-op geomean than C2 on a third-party JMH compiler suite.

| | |
|---|---|
| **Beats** | HotSpot C2 JIT (OpenJDK HotSpot VM, JDK 25) |
| **Claimed result** | ionutbalosin JDK 25 JIT benchmark suite compiler.csv: Graal CE geomean 0.84 of HotSpot C2 time (reproduced as 0.835 from 298 committed CSV rows), but the median ratio is 0.99 and a 0.2x-5x trim gives 0.94 (derived from page data); outlier wins such as DeadLoopElimination (30000x) and NpeControlFlow (153x) drive the geomean. Whole suite 0.904 after correcting the script's unit handling (published api 0.92 vs corrected 0.93). The JDK 21 release (v3.0) had CE at 1.06 compiler and 1.03 overall, slower than C2. |
| **Workload** | JMH suite from the ionutbalosin/jvm-performance-benchmarks repository on JDK 25 x86_64: 298 compiler-optimization microbenchmarks (inlining, loop unrolling, escape analysis, devirtualization and similar) and 1136 benchmarks overall including Java API and classic programs. |
| **Metric** | throughput |
| **Compiler and flags** | JDK 25 (exact OpenJDK, GraalVM CE and Oracle GraalVM builds not stated); JMH options -wi 5 -w 10 -i 5 -r 10 -f 5 and JVM args -Xms4g -Xmx4g -XX:+AlwaysPreTouch for every benchmark (settings/benchmarks-suite-jdk25.json); GraalVM CE and Oracle GraalVM JIT vs OpenJDK HotSpot C2 |
| **Adoption** | 21.7k stars (oracle/graal); the benchmark suite ionutbalosin/jvm-performance-benchmarks has 132 stars |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/oracle/graal) · [benchmark](https://raw.githubusercontent.com/ionutbalosin/jvm-performance-benchmarks/HEAD/results/jdk-25/x86_64/geomean/compiler.csv) |

## Verdict

ionutbalosin/jvm-performance-benchmarks (JMH average time, 5 forks of 5 x 10 s measurement iterations after 5 x 10 s warmup, -Xms4g -Xmx4g -XX:+AlwaysPreTouch, JDK 25 on an unnamed x86_64 machine, exact builds not stated) puts GraalVM CE's JIT at a time-per-op geomean of 0.84 of OpenJDK HotSpot C2 over 298 compiler-pattern microbenchmarks, and the GraalVM CE VM at 0.90 over all 1136. Recomputing from the committed per-benchmark CSVs gives 0.835 for the compiler category; correcting the throughput-row direction gives 0.904 for the whole suite.

## Use it when

- Long-running, throughput-bound JVM services where steady-state peak matters more than startup, and where you can A/B the same build with -XX:-UseJVMCICompiler.
- Abstraction-heavy Java with many short-lived objects (streams, lambdas, iterators, boxed values), where partial escape analysis removes allocations; in the suite's program category GameOfLife iterative ran at 0.49x C2's time, LZW decompress 0.52x and dynamic-programming knapsack 0.59x.
- Code with megamorphic interface or virtual call chains, or redundant/nested locking, where the inliner and lock optimizations remove most of the cost.
- Hosting Truffle languages (GraalJS, GraalPy, Espresso), which depend on this compiler for their JIT.
- Teams already on GraalVM CE for JDK 25: per the compiler CHANGELOG, optimizations that used to be Oracle-only (loop vectorization, duplication) are now in the open-source community configuration, and in this suite CE and Oracle GraalVM land on the same 0.84.

## Skip it when

- Code whose hot paths rely on C2-specific simplifications: in the same suite Graal is 30,000x slower on DeadLoopEliminationBenchmark.dead_loop (C2 deletes the loop, 0.61 ns vs 18,233 ns), 8,800x on any_true_array_element, 153x on NpeControlFlowBenchmark.try_npe_catch, 35-41x on implicit NullPointerException throws, and 3-7x on sequential byte/short/int stores that C2 merges.
- Short-lived or cold-start-sensitive processes: the suite measures steady state only, and issue #13387 reports a 27% cold-wall regression vs C2 (4.78 s vs 3.47 s median) from repeated 'COMPILE SKIPPED: Speculation failed' recompiles on Oracle GraalVM 25.0.2.
- Workloads where the median benchmark is what matters: the median per-benchmark ratio to C2 is 0.99 in the compiler category, 0.95 in API and 0.96 in programs, so most code sees little change and the geomean comes from a minority of large wins.
- Deployments that cannot absorb a less battle-tested top-tier compiler: open issue #14495 (Sept 2026) is a miscompile where a loop that must never terminate returns a finite sum on Oracle GraalVM 25.0.3 and 25.4 (C2 correct).
- When pinned to one GraalVM version without testing: on the JDK 21 release of the same suite GraalVM CE was slower than C2 (compiler category 1.06, whole suite 1.03) while Oracle GraalVM was 0.64 and 0.77, so the gain depends heavily on edition and release.

## How it is fast

It compiles from a graph IR with speculative optimizations backed by deoptimization, partial escape analysis (an object is allocated only on the paths where it escapes), aggressive and polymorphic inlining (a call-graph-wide PriorityInliningPhase became the default in 25.3), and path duplication (DBDS, CGO 2018). The 25.x community configuration has also gained loop vectorization, lock coarsening and elimination of nested locks, partial redundancy elimination scheduling, write sinking and aggressive partial unrolling. The suite's largest wins come from these: nested synchronized blocks at 0.48 ns vs C2 196 ns, a megamorphic virtual call chain at 0.8-3.5 ns vs 37.6 ns, and non-escaping objects scalar-replaced (0.61 ns vs 11.5 ns).

## Compared with alternatives

Choose Graal over Eclipse OpenJ9 when steady-state peak throughput of abstraction-heavy Java matters more than startup and footprint, which is where OpenJ9's catalogued advantage (about 40% faster startup with a shared-class-cache AOT) lies. It is also the compiler underneath the catalogued Graal.js, so pick it whenever you run Truffle languages.

## Integration

| | |
|---|---|
| **Form** | shared lib (libgraal inside a GraalVM JDK distribution; or experimental -XX:+UseGraalJIT in Oracle JDK); jargraal runs as ordinary Java on the heap |
| **Dependencies** | A JVMCI-enabled JDK (GraalVM CE/Oracle GraalVM, or LabsJDK when building from source); the mx build tool to build it yourself |
| **Minimum toolchain** | JDK 17+ (GR-42212 removed support for older JDKs); current master is built against LabsJDK 25 (jvmci-25.1-b14 in vm/README.md) |
| **Platforms** | AMD64 and AArch64 back ends (both named in compiler/CHANGELOG.md); the cited suite measured x86_64 only |
| **Thread safety** | Not applicable as a library; compiles on background JVMCI threads whose default count matches C2's since GraalVM for JDK 24 (-XX:JVMCINativeLibraryThreadFraction=0.66), which can raise peak RSS |
| **Drop-in for the baseline** | partial — no source changes, but you switch JDK distribution or add experimental flags; C2-specific -XX tuning flags do not apply and Graal is tuned with -Djdk.graal.\* properties |

## Gotchas

- Harness flaw in the cited suite: scripts/ggplot2/geomean-utils.r converts s/ms/us scores to ns but leaves 12 throughput-mode rows (ops/s, from ColumnarDBFilterBenchmark and VectorizedScanOperationBenchmark) in the lower-is-better geomean, so Graal's throughput losses count as wins (vectorized_query_IS_EVEN_pivot at size 1048576: HotSpot 3356 ops/s vs Graal 466 ops/s is scored as a 7x Graal gain). Recomputed from the committed CSVs, the API category is 0.93 rather than the published 0.92 and the whole suite 0.904; the compiler-category 0.84 (reproduced as 0.835 over 298 rows) has no throughput rows and is unaffected.
- The geomean depends on a few extreme results. In the compiler category 116 of 298 rows are more than 5% faster than C2 and 74 more than 5% slower; dropping rows outside a 0.2x-5x ratio gives 0.94 instead of 0.84, and per-class equal weighting gives 0.75. The script also divides one geomean of raw scores by another rather than matching rows by name; the row sets happen to be identical here.
- Edition and version matter more than the docs suggest: the reference Options.md still says vectorization and the 'enterprise' configuration are Oracle GraalVM only, but compiler/CHANGELOG.md moves those optimizations into the community compiler during the 25.x series, and in this JDK 25 run 991 of 1136 rows are within 2% between CE and Oracle GraalVM. The suite records neither the exact GraalVM releases nor -Djdk.graal.ShowConfiguration output, so which optimizations ran cannot be confirmed.
- jargraal (the compiler running as plain Java) allocates on the application heap, can increase GC pauses and starts interpreted; use libgraal, as the GraalVM builds do, unless you are debugging the compiler.

## Known shortcomings

- compiler.csv geomean 0.84 against HotSpot C2 at 1.00 (ionutbalosin JDK 25 suite) is a geomean over microbenchmark patterns with JVM flags public but no CPU model; CE and Oracle GraalVM results are within noise of each other. Java compiler, not C++.
- Enricher: the ionutbalosin suite's scripts/ggplot2/geomean-utils.r converts s, ms and us to ns but keeps 12 throughput rows (ops/s, ColumnarDBFilterBenchmark and VectorizedScanOperationBenchmark) in the lower-is-better geomean, so Graal throughput losses count as wins (corrected api 0.93 vs published 0.92, whole suite 0.904; the compiler-category 0.84 has no ops/s rows and reproduces as 0.835 from 298 committed CSV rows). The geomean is driven by outliers (median ratio 0.99; a 0.2x-5x trim gives 0.94; losses DeadLoopElimination 30000x, NpeControlFlow 153x); the JDK 21 release of the same suite had CE at 1.06 compiler and 1.03 overall (slower than C2) with Oracle at 0.64, CE catching up through 25.x by moving optimizations into the community config; exact GraalVM builds unrecorded; open miscompile #14495.

## Caveats and trade-offs

The numbers are in a third-party suite, not in the oracle/graal repo, whose README gives no performance figures. No CPU model or exact JDK build is stated in the suite README, settings, PR #115 or result CSVs (README covers OS tuning only), which is why this is tier B rather than A. The compiler category is made of handwritten patterns chosen to exercise optimizations, so the 16% geomean gap is not an application speedup; the other categories are smaller (api 0.92 over 756 benchmarks, miscellaneous 0.91 over 82, whole suite 0.9 over 1136, in sibling geomean CSVs). Normalized geometric means hide per-benchmark losses. GraalVM CE and Oracle GraalVM results are within run-to-run noise of each other (e.g. FibonacciBenchmark CSVs), so the Oracle build shows no extra gain here. The suite itself is Apache-2.0; graal's compiler is GPL-2.0 with Classpath Exception while other graal components carry UPL, BSD-3-Clause and GPL-2.0. The suite author's articles for JDK 17 and 21 (blog host) were not opened. [retier] scripts/ggplot2/geomean-utils.r keeps 12 ops/s throughput rows in a lower-is-better geomean, so throughput losses count as wins (the compiler category has none); JVM flags public but no CPU model and exact GraalVM builds unrecorded; CE and Oracle GraalVM results are within noise on JDK 25 while on JDK 21 Oracle was 0.64 and CE slower than C2. Open miscompile #14495. Java compiler, not C++.

The Graal JIT plugs into HotSpot through JVMCI, or ships inside GraalVM. GraalVM Community Edition is GPLv2 with Classpath Exception; the Oracle GraalVM build has separate licence terms, so only the CE numbers are about copyable code. Memory, warmup and startup are not covered by the geomean pages opened.

## Maintenance

Very active (commits on 2026-10-06, frequent compiler changes between 25.x releases); the compiler is GPL-2.0 with Classpath Exception in GraalVM CE, and Oracle GraalVM builds carry separate licence terms. You adopt it by switching JDK, not by vendoring code.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification B, tier now B.
- **Tier reason:** Independent third-party JMH suite (ionutbalosin/jvm-performance-benchmarks, JDK 25 results committed 2026-04-13) with public code, JMH options and JVM args in settings/benchmarks-suite-jdk25.json, and per-benchmark CSVs; compiler.csv shows C2 1.00 vs GraalVM CE 0.84 over 298 benchmarks. No CPU model or exact JDK build is stated anywhere opened, so not A.
- **Verifier notes:** compiler.csv and summary.csv match the record exactly (C2 1.00 vs Graal CE/Oracle 0.84 over 298; HotSpot 1.0 vs 0.9 over 1136). JVM flags are public, CPU model is not; keep at B. Shortcomings: microbenchmark-pattern geomean, no CPU model, CE and Oracle GraalVM indistinguishable.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`, `claimed_speedup`
- **Pages the verifier opened:**
  - <https://github.com/oracle/graal>
  - <https://github.com/oracle/graal/commits/master>
  - <https://raw.githubusercontent.com/ionutbalosin/jvm-performance-benchmarks/HEAD/results/jdk-25/x86_64/geomean/compiler.csv>
  - <https://raw.githubusercontent.com/ionutbalosin/jvm-performance-benchmarks/HEAD/results/jdk-25/x86_64/geomean/summary.csv>
  - <https://raw.githubusercontent.com/ionutbalosin/jvm-performance-benchmarks/HEAD/results/jdk-25/x86_64/geomean/api.csv>
  - <https://raw.githubusercontent.com/ionutbalosin/jvm-performance-benchmarks/HEAD/results/jdk-25/x86_64/geomean/miscellaneous.csv>
  - <https://raw.githubusercontent.com/ionutbalosin/jvm-performance-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/ionutbalosin/jvm-performance-benchmarks/HEAD/settings/config.properties>
  - <https://raw.githubusercontent.com/ionutbalosin/jvm-performance-benchmarks/HEAD/settings/benchmarks-suite-jdk25.json>
  - <https://raw.githubusercontent.com/ionutbalosin/jvm-performance-benchmarks/HEAD/results/jdk-25/x86_64/jmh/graalvm-ce/FibonacciBenchmark.csv>
  - <https://raw.githubusercontent.com/ionutbalosin/jvm-performance-benchmarks/HEAD/results/jdk-25/x86_64/jmh/graalvm-ee/FibonacciBenchmark.csv>
  - <https://raw.githubusercontent.com/ionutbalosin/jvm-performance-benchmarks/HEAD/results/jdk-25/x86_64/jmh/openjdk-hotspot-vm/FibonacciBenchmark.csv>
  - <https://github.com/ionutbalosin/jvm-performance-benchmarks>
  - <https://github.com/ionutbalosin/jvm-performance-benchmarks/commits/main>
  - <https://github.com/ionutbalosin/jvm-performance-benchmarks/tree/main/results/jdk-25/x86_64>
  - <https://github.com/ionutbalosin/jvm-performance-benchmarks/tree/main/results/jdk-25/x86_64/jmh>
  - <https://github.com/ionutbalosin/jvm-performance-benchmarks/tree/main/results/jdk-25/x86_64/jmh/graalvm-ce>
  - <https://github.com/ionutbalosin/jvm-performance-benchmarks/tree/main/settings>
  - <https://github.com/ionutbalosin/jvm-performance-benchmarks/pull/115>
- **Sources the enricher read:**
  - <https://github.com/oracle/graal>
  - <https://raw.githubusercontent.com/oracle/graal/HEAD/README.md>
  - <https://raw.githubusercontent.com/oracle/graal/HEAD/compiler/README.md>
  - <https://raw.githubusercontent.com/oracle/graal/HEAD/compiler/CHANGELOG.md>
  - <https://raw.githubusercontent.com/oracle/graal/HEAD/compiler/LICENSE.md>
  - <https://raw.githubusercontent.com/oracle/graal/HEAD/SECURITY.md>
  - <https://raw.githubusercontent.com/oracle/graal/HEAD/vm/README.md>
  - <https://raw.githubusercontent.com/oracle/graal/HEAD/docs/reference-manual/java/compiler.md>
  - <https://raw.githubusercontent.com/oracle/graal/HEAD/docs/reference-manual/java/Options.md>
  - <https://raw.githubusercontent.com/oracle/graal/HEAD/docs/reference-manual/java/Operations.md>
  - <https://github.com/oracle/graal/commits/master>
  - <https://github.com/oracle/graal/issues?q=is%3Aissue%20label%3Acompiler%20label%3Abug>
  - <https://github.com/oracle/graal/issues/14495>
  - <https://github.com/oracle/graal/issues/13387>
  - <https://github.com/oracle/graal/issues/5468>
  - <https://raw.githubusercontent.com/ionutbalosin/jvm-performance-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/ionutbalosin/jvm-performance-benchmarks/HEAD/settings/benchmarks-suite-jdk25.json>
  - <https://raw.githubusercontent.com/ionutbalosin/jvm-performance-benchmarks/HEAD/settings/config.properties>
  - <https://raw.githubusercontent.com/ionutbalosin/jvm-performance-benchmarks/HEAD/results/jdk-25/x86_64/geomean/compiler.csv>
  - <https://raw.githubusercontent.com/ionutbalosin/jvm-performance-benchmarks/HEAD/results/jdk-25/x86_64/geomean/summary.csv>
  - <https://raw.githubusercontent.com/ionutbalosin/jvm-performance-benchmarks/HEAD/results/jdk-25/x86_64/geomean/api.csv>
  - <https://raw.githubusercontent.com/ionutbalosin/jvm-performance-benchmarks/HEAD/results/jdk-25/x86_64/geomean/miscellaneous.csv>
  - <https://raw.githubusercontent.com/ionutbalosin/jvm-performance-benchmarks/HEAD/scripts/ggplot2/geomean-benchmark.r>
  - <https://raw.githubusercontent.com/ionutbalosin/jvm-performance-benchmarks/HEAD/scripts/ggplot2/geomean-utils.r>
  - <https://raw.githubusercontent.com/ionutbalosin/jvm-performance-benchmarks/HEAD/scripts/ggplot2/utils.r>
  - <https://raw.githubusercontent.com/ionutbalosin/jvm-performance-benchmarks/HEAD/scripts/ggplot2/merge-utils.r>
  - <https://raw.githubusercontent.com/ionutbalosin/jvm-performance-benchmarks/HEAD/scripts/ggplot2/merge-benchmark.r>
  - https://raw.githubusercontent.com/ionutbalosin/jvm-performance-benchmarks/HEAD/results/jdk-25/x86_64/jmh/{openjdk-hotspot-vm,graalvm-ce,graalvm-ee}/&lt;all 136 benchmark CSVs named in settings/benchmarks-suite-jdk25.json&gt;
  - <https://github.com/ionutbalosin/jvm-performance-benchmarks/tree/main/results/jdk-25/x86_64>
  - <https://github.com/ionutbalosin/jvm-performance-benchmarks/tree/main/results/jdk-25/x86_64/jmh/graalvm-ce>
  - <https://github.com/ionutbalosin/jvm-performance-benchmarks/tree/main/scripts>
  - <https://github.com/ionutbalosin/jvm-performance-benchmarks/tree/main/scripts/ggplot2>
  - <https://raw.githubusercontent.com/ionutbalosin/jvm-performance-benchmarks/v3.0/results/jdk-21/x86_64/geomean/compiler.csv>
  - <https://raw.githubusercontent.com/ionutbalosin/jvm-performance-benchmarks/v3.0/results/jdk-21/x86_64/geomean/summary.csv>
  - <https://raw.githubusercontent.com/ionutbalosin/jvm-performance-benchmarks/v3.0/results/jdk-21/x86_64/jmh/{openjdk-hotspot-vm,graalvm-ce,graalvm-ee}/VectorizationPatternsSingleIntArrayBenchmark.csv>
  - https://www.graalvm.org/release-notes/JDK_25/ (EGRESS_BLOCKED)
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/oracle/graal`) · [data/wave12/enrich/raw/github_com_oracle_graal.json](../../../data/wave12/enrich/raw/github_com_oracle_graal.json) (enrichment confidence 0.8)

</details>
