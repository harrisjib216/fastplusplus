# OpenJDK HotSpot (Java 25): benchLANG binary trees

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Runtime JIT beats ahead-of-time](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Java` · `MIT` · 🟢 active

> Default-settings OpenJDK 25 running benchLANG's binary trees about 2.9x faster than per-node malloc/free C and 3.3x faster than new/delete C++.

| | |
|---|---|
| **Beats** | C (GCC 16.2.0, malloc and free per node, 1.010 s) and C++ (GCC 16.2.0, new and delete per node, 1.147 s) |
| **Claimed result** | Java 0.347 s vs C 1.010 s and C++ 1.147 s: about 2.9x faster than C and 3.3x faster than C++ (derived from page data). Peak RSS 987.8 MiB for Java vs 33.3 MiB for C and 35.4 MiB for C++. |
| **Workload** | CLBG-style binary trees with depths 4 to 18: a stretch tree, a long-lived tree, then many short-lived trees built, checked and (in C/C++) freed, one allocation per node. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 5900X locked at 3.5 GHz (performance governor), 48 GB DDR4-3600 CL16, Arch Linux with i3-wm; results dated 3 September 2026, one run per language |
| **Compiler and flags** | C: gcc -O3 -march=native -flto -funroll-loops -ffp-contract=off -s (GCC 16.2.0); C++: g++ -std=c++20 with the same flags. Java: OpenJDK 25.0.4, javac bench.java then java bench with default heap and default GC. |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | yes |
| **Why it wins** | Stated by the suite's methodology: 'Binary trees: ... Allocator + GC + pointer chase, native code frees inside the timer, GC runtimes collect when they like'. Agent inference: per-node malloc/free (C, C++) against bump-pointer allocation and deferred or concurrent collection in a managed runtime; the C/C++ programs do not use an arena. |
| **Adoption** | 8 stars |
| **Last commit** | 2026-09-03 |
| **Links** | [repository](https://github.com/GlebOlsen/benchLANG) · [benchmark](https://raw.githubusercontent.com/GlebOlsen/benchLANG/main/README.md) |

## Verdict

benchLANG's 3 September 2026 run on a Ryzen 9 5900X locked at 3.5 GHz (Arch Linux, 48 GB DDR4-3600) timed binary trees at 0.347 s for OpenJDK 25.0.4 with default heap and GC against 1.010 s for C and 1.147 s for C++, both built by GCC 16.2.0 with -O3 -march=native -flto -funroll-loops and allocating each node with malloc/free or new/delete; about 2.9x and 3.3x faster (derived from page data), one run each, with the analyzer checking that all languages print the same checksum.

## Use it when

- You already run on the JVM and are tempted to move a builder of many small, short-lived objects (parse trees, temporary graphs, ASTs) to native code: with default settings HotSpot beat naive malloc/free C by about 2.9x here.
- Throughput or batch jobs that allocate and drop whole object graphs at once, where wall time matters more than memory footprint or pause times.
- Machines with plenty of RAM and idle cores, which the JVM's default heap sizing and parallel GC workers exploit.
- As a data point that per-node malloc/free, not the language, is the bottleneck of a C or C++ tree builder.

## Skip it when

- As evidence that Java beats tuned C++: benchLANG has no arena or pool variant. In LangArena's Binarytrees::Arena test a C index arena grown by realloc (C/Gcc/Fast 0.255 s) beats HotSpot's object tree (Binarytrees::Obj, 0.479 s), though a C++ std::vector arena without reserve does not (best 0.512 s); std::pmr::monotonic_buffer_resource or a bump allocator would also remove the per-node frees and the second traversal here (inference, not measured in benchLANG).
- Memory-constrained deployments: whole-process peak RSS was 987.8 MiB for Java against 33.3 MiB for C and 35.4 MiB for C++, about 30x, and the JVM is not counted in any binary size.
- Latency-sensitive code with tight pause or footprint budgets: the table reports no pause times and no per-workload CPU time.
- Recursion- or string-heavy code: the same Java program loses Fibonacci(45) (4.109 s vs 1.694 s for C) and strings (4.075 s vs 2.132 s) and the suite overall (13.536 s vs 9.762 s).

## How it is fast

Memory management, not code generation. Likely mechanism (inference, consistent with the README's 'GC runtimes collect when they like'): HotSpot hands out each Node by bumping a pointer in a thread-local allocation buffer, and the default G1 collector's young collections copy only live objects, so the millions of dead short-lived trees cost nothing to reclaim; only the long-lived tree survives. The C and C++ programs call glibc malloc or operator new per node and then walk every tree a second time (free_tree) to free or delete each node inside the timer. Per node that is about 5.1 ns for Java against 14.8 ns for C and 16.8 ns for C++ (derived from page data over 68.3M nodes).

## Compared with alternatives

Java's 0.347 s is the largest managed-runtime margin among the catalogued benchLANG binary-trees rows (C# 0.931 s, Bun 0.816 s, OCaml 0.865 s), so it is the strongest of those data points if you are on the JVM; LangArena's Java Binarytrees::Obj entry (0.479 s vs C++ 2.098 s, with -O3 and PGO baselines) is better evidence because it also measures an arena variant that shows where the win ends.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | A JDK: OpenJDK 25.0.4 from nixpkgs-unstable (jdk25 in flake.nix, pinned by the committed flake.lock); no libraries |
| **Minimum toolchain** | OpenJDK 25.0.4 as measured; bench.java itself uses only long-standing language features (final fields, numeric-literal underscores, String.split), so older JDKs should compile it, but only 25.0.4 was measured |
| **Platforms** | Measured on x86-64 Linux only (flake.nix sets system = x86_64-linux), Ryzen 9 5900X locked at 3.5 GHz |
| **Thread safety** | Not applicable: single-threaded workload; the JVM runs GC and JIT compiler threads beside it |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness asymmetry behind the margin: C and C++ free every node in a second traversal inside the timer, while Java drops the root and stops its timer with the long-lived tree and the last young-generation garbage still uncollected (the JVM exits right after). The README states this design, so it is a fair description of what is measured, but it compares allocation strategies, not languages.
- Extra cores are invisible: CPUx = (user+sys)/wall is computed by analyze_results.sh over the whole process but is left out of the README table, and the raw benchmark_results_\*.txt file is never committed (.gitignore ignores '\*' and does not re-include .txt), so how much GC and JIT helper-thread CPU the Java run used cannot be checked. Java at 0.347 s is also 2.3x ahead of every other managed or native row (Nim 0.809 s, Bun 0.816 s), an outlier that one run cannot confirm. On a similar test in LangArena (Binarytrees::Obj), HotSpot (OpenJDK 27) restricted to single-threaded SerialGC and a 512 MB heap ran in 0.886 s against 0.479 s with default G1, so GC worker threads and heap size can account for about half of such a margin.
- Default JVM ergonomics on a 48 GB machine: no -Xmx or GC flag is passed, so heap and young-generation sizes follow the host's RAM and core count; peak RSS of 987.8 MiB suggests a large young generation and few collections. A smaller container or a fixed heap could change the result (inference, not measured).
- One run per language on 3 September 2026, wall time from System.nanoTime() inside the program; binary trees runs last in the same JVM after the other four workloads, so JVM startup is excluded but makeTree and checkTree still JIT-compile inside the timed region. run_benchmarks.sh supports --runs N, but the published table does not use it.

## Known shortcomings

- One run (0.347 vs 1.010 s) with peak RSS 987.8 MiB vs 33.3 MiB and GC CPU time unreported; the win is allocator plus GC since C frees every tree inside the timer.
- Harness flaw: CPUx ((user+sys)/wall) is computed but left out of the README table, and the raw benchmark_results_\*.txt files are gitignored, so the GC and JIT helper-thread CPU cannot be verified. Java's 0.347 s is 2.3x ahead of every other row (Nim 0.809, Bun 0.816) on one run. C and C++ free every node in a second traversal inside the timer while the Java heap is never collected. No correctness bug; checksums are cross-checked by the analyzer.

## Caveats and trade-offs

One run per language ('1 run/lang'), no variance. In-program wall times from a monotonic clock: JIT warm-up is inside the timed region, young-generation collections run inside it too, but garbage still live in the heap when the timer stops is never collected ('GC runtimes collect when they like'), while C/C++ walk every tree a second time to free it inside the timer. The Java run uses JVM ergonomics (default G1 with parallel GC worker threads on a 12-core CPU); the README defines CPUx = (user+sys)/wall but the published table does not show it, so extra GC-thread CPU time is not visible. Peak RSS 987.8 MiB for Java vs 33.3 MiB for C: the win trades about 30x memory for time. The column is an allocator benchmark: Nim 0.809 s, Bun 0.816 s, OCaml and Dart AOT 0.865 s, C# 0.931 s and Fortran 0.986 s also beat C's 1.010 s, so per-node glibc malloc/free is the bottleneck and an arena or pool allocator in C/C++ would likely beat every managed runtime (compare the Arena variant in LangArena). Only the binary-trees column is a Java win: Java loses Fibonacci (4.109 s vs 1.694 s), strings (4.075 s vs 2.132 s) and Mandelbrot (2.275 s vs 2.201 s) and ties primes (2.730 s vs 2.725 s); total 13.536 s vs C 9.762 s. [retier] CPUx ((user+sys)/wall) is computed but left out of the README table and the raw benchmark_results_\*.txt files are gitignored, so the GC and JIT helper-thread CPU cannot be verified. Java's 0.347 s is 2.3x ahead of every other row (Nim 0.809, Bun 0.816) on one run. C and C++ free every node in a second traversal inside the timer while the Java heap is never collected.

About 30x the peak memory of C; whole-process CPU time exceeds wall time because of GC and JIT threads; needs a JVM.

## Maintenance

Small single-author MIT repo (8 stars, 42 commits, no issues, last commit 2026-09-03) with Nix-pinned toolchains and a committed flake.lock, so anyone can rerun it, but this is one run of one micro-workload whose raw results file and CPU-time column are unpublished.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** The README results table (3 September 2026, one run) gives Binary Trees 0.347 s for Java (OpenJDK 25.0.4) against 1.010 s for C and 1.147 s for C++ (GCC 16.2.0). Code for every side is public (languages/C/bench.c, languages/C++/bench.cpp, languages/Java/bench.java, run_benchmarks.sh), with Nix-pinned versions, exact build and run commands and the CPU (Ryzen 9 5900X locked at 3.5 GHz), so it meets A.
- **Verifier notes:** Numbers and derived ratios (2.9x over C, 3.3x over C++) match the README; same tree build/check algorithm, C/C++ at -O3 with -march=native and LTO, so the baseline is not crippled and A stands. Main shortcomings: one run, C/C++ pay an explicit free traversal inside the timer, the final heap is never collected, GC-thread CPU time is unreported, and 987.8 MiB peak RSS vs 33.3 MiB; the win is GC bump allocation against glibc malloc/free, not JIT code generation. Fixed two caveat errors: Ada (1.666 s), not C, is fastest on Fibonacci, and the current README no longer carries an 'Updated May 2026' header.
- **Fields the verifier corrected:** `baseline_stdlib`, `caveats`
- **Shortcomings recorded by:** verifier batch-54 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/main/README.md>
  - <https://github.com/GlebOlsen/benchLANG>
  - <https://github.com/GlebOlsen/benchLANG/commits>
  - <https://github.com/GlebOlsen/benchLANG/tree/main/languages>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/main/languages/C/bench.c>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/main/languages/C%2B%2B/bench.cpp>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/main/run_benchmarks.sh>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/main/flake.nix>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/main/languages/Java/bench.java>
- **Sources the enricher read:**
  - <https://github.com/GlebOlsen/benchLANG>
  - <https://github.com/GlebOlsen/benchLANG/commits/main>
  - <https://github.com/GlebOlsen/benchLANG/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/main/README.md>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/main/languages/Java/bench.java>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/main/languages/C/bench.c>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/main/languages/C%2B%2B/bench.cpp>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/main/run_benchmarks.sh>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/main/analyze_results.sh>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/main/flake.nix>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/main/.gitignore>
  - https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-10-05-kostya-ms7c37.js (Binarytrees::Obj and ::Arena rows, read for the second entry of this pair)
  - WebSearch: benchmarks game binary-trees C gcc apr_pools vs Java (snippets from benchmarksgame-team.pages.debian.net; the pages themselves were not opened)
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:java/glebolsen/benchlang#binary-trees`) · [data/wave14/enrich/raw/lang_java_glebolsen_benchlang_binary_trees.json](../../../data/wave14/enrich/raw/lang_java_glebolsen_benchlang_binary_trees.json) (enrichment confidence 0.75)

</details>
