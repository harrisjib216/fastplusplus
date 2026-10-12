# dotnet JIT (C# on .NET 11): LangArena Graph::AStar

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Runtime JIT beats ahead-of-time](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C#` · `MIT` · 🟢 active

> C# on .NET 11 runs LangArena's Graph::AStar 1.38x faster than C++ std::priority_queue builds; per-search allocation, not JIT, likely explains it.

| | |
|---|---|
| **Beats** | C++ with std::priority_queue&lt;Node, std::vector&lt;Node&gt;, std::greater&lt;Node&gt;&gt; (binary heap ordered on f-score only): the best C++ row is C++/Clang++/Unsafe at 1.908 s, and the prod rows are C++/Clang++ 2.064 s and C++/G++ 2.198 s. The C program (c/src/graph_path.c, best row C/Clang/Unsafe 1.767 s) uses a hand-written binary heap whose pop is buggy (see caveats). |
| **Claimed result** | C#/JIT 1.384 s vs the best C++ row, C++/Clang++/Unsafe at 1.908 s (-O3 -march=native -ffast-math), and the prod rows C++/Clang++ 2.064 s and C++/G++ 2.198 s (-O2): about 1.38x faster than the best C++ row and 1.59x faster than C++/G++ prod (derived from page data). The best C row overall is C/Clang/Unsafe at 1.767 s (about 1.28x, derived), but that program's heap pop is buggy. .NET AOT builds win too (C#/R2R 1.222 s, C#/AOT 1.321 s), as do F#/JIT 1.381 s, Julia/Default 1.458 s and Java/OpenJDK 1.486 s. The timed loop is 1,000 searches after 200 untimed warm-up searches. |
| **Workload** | A\* shortest path search on a large generated grid graph using a priority queue open set. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 7 3800X 8-Core Processor, 78GB RAM, x86_64 Linux (results file 2026-10-05, host kostya-ms7c37) |
| **Compiler and flags** | C/C++ (cpp/Makefile, c/Makefile; versions from the results file): Clang 22.1.8 and GCC 16.0.1 20260322 (trunk, Ubuntu package build), libstdc++ (no -stdlib flag). 'prod' (headline rows): -O2 -DNDEBUG -fstack-protector-strong -fno-omit-frame-pointer, -std=c++20 for C++. 'Fast': -O3 -march=native -mtune=native -DNDEBUG -pipe -fstack-protector -ftree-vectorize -funroll-loops. 'Unsafe': -O3 -march=native -DNDEBUG -pipe -fno-stack-protector -fomit-frame-pointer -ffast-math -fvisibility=hidden -fno-common -fstrict-overflow -fno-trapping-math. 'PGO': -O2 plus -fprofile-instr-use (Clang) or -fprofile-use (GCC). -flto=thin (Fast) and -flto=full (Unsafe) are passed only on the link line (LDFLAGS) while objects are compiled without -flto, so no link-time optimisation actually takes place. Managed side: dotnet 11.0.100-rc.1.26425.128, 'dotnet build -c Release' (Optimize=true) run as 'dotnet Benchmark.dll' with default tiered JIT; the C#/AOT rows are NativeAOT with IlcInstructionSet=native and IlcOptimizationPreference=Speed; Julia 1.13.1 run as 'julia --project=. --threads=16 benchmark.jl' (Julia/Max adds -O3 --check-bounds=no --math-mode=fast); Temurin OpenJDK 27+35 run as 'java -Xmx2g -jar'. Every language, C and C++ included, runs untimed warm-up iterations (20 percent of the timed count) before the timed loop. |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | yes |
| **Why it wins** | Not stated by the suite. The sources use .NET PriorityQueue&lt;int,int&gt; (a 4-ary heap) against std::priority_queue (binary heap) in C++; the difference may be the heap rather than JIT quality (agent inference). |
| **Adoption** | 41 stars |
| **Last commit** | 2026-10-08 |
| **Links** | [repository](https://github.com/kostya/LangArena) · [benchmark](https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-10-05-kostya-ms7c37.js) |

## Verdict

LangArena results of 2026-10-05 on an AMD Ryzen 7 3800X: 1,000 timed searches on a 500,000-vertex graph after 200 warm-ups took 1.384 s for C#/JIT (.NET 11.0.100-rc.1). The C++ version (std::priority_queue and std::vector on libstdc++) took 2.064 s with Clang++ 22.1.8 -O2, 2.198 s with G++ 16.0.1 -O2 and 1.908 s at best with Clang++ -O3 -march=native -ffast-math, so C# is 1.38-1.59x faster (derived from page data). C# ReadyToRun (1.222 s) and NativeAOT (1.321 s) are faster still; each configuration ran once.

## Use it when

- You already run .NET and do many independent graph searches over large vertex sets with fresh per-query score arrays: 1.38 ms per 500,000-vertex search on a Ryzen 7 3800X, against 2.06 ms for the idiomatic C++/Clang++ -O2 build.
- Request-scoped code that allocates multi-megabyte scratch arrays on every call, where a GC heap that stays committed avoids the allocate, fault and release cycle of a default glibc malloc (inference from this test, not separately measured).
- Any .NET deployment mode works: ReadyToRun 1.222 s, NativeAOT 1.321 s and JIT 1.384 s all beat every C and C++ row, so NativeAOT is fine where startup time or JIT warm-up matters.

## Skip it when

- As evidence that a JIT beats ahead-of-time C++: the AOT and R2R C# builds win too, as do Java, Julia, D (LDC) and Crystal. The C++ code reallocates 4 MB per search; hoisting the two vectors and resetting them with assign(), or linking a caching allocator, would likely close the gap (not measured).
- Graph traversal in general: on the same graph, Graph::BFS takes 2.013 s for C#/JIT against 1.346 s for C++/G++ and 1.143 s for C/Clang, Graph::DFS 1.343 s against 0.894 s for C/Gcc, and Maze::AStar 1.832 s against 1.188 s for C++/G++/Fast and 0.861 s for C/Gcc/Fast.
- Memory-constrained hosts: C# peaked at 354 MB RSS on this test against 85 MB for C++ (about 4.2x), and Java at about 1.1 GB.
- When you need true shortest paths: the benchmarked heuristic is inadmissible, so the code returns a 1,172-edge path where BFS on the same graph finds 1,050.

## How it is fast

The search itself does little work: the heuristic target - v overestimates by orders of magnitude, so the search is greedy best-first with 1,173 pops and about 23,800 pushes per search, while every search allocates and fills two 500,000-int arrays (4 MB). glibc malloc probably serves those 2 MB arrays with mmap, or from a heap it trims back after each search under its dynamic mmap and trim thresholds, so each C++ search likely page-faults about 1,000 fresh 4 KB pages. The .NET GC instead keeps its large-object heap committed (peak RSS 354 MB against 85 MB for C++). This explanation is agent inference from the code and the results table, not a measurement. It fits the table: every tracing-GC runtime (C# 1.22-1.39 s, F# 1.381, Julia 1.458, D/LDC 1.471, Java 1.486, Crystal 1.554) beats every language that uses glibc malloc (C 1.77-2.06 s, C++ 1.91-2.20, Rust with its default system allocator 1.995, Swift 2.073).

## Compared with alternatives

Like the benchLANG .NET 11 binary-trees entry and the LangArena Distance::NGram C# entry, this measures the .NET runtime's memory management and base library against naive C/C++ allocation rather than JIT code quality. Cite NGram for hash-map-heavy code and benchLANG for node-per-allocation trees; cite this entry only for loops that allocate large temporary arrays on every call.

## Integration

| | |
|---|---|
| **Form** | module (application code on the .NET base library; nothing to vendor beyond csharp/GraphPath.cs) |
| **Dependencies** | .NET runtime only; PriorityQueue&lt;TElement,TPriority&gt; from System.Collections.Generic |
| **Minimum toolchain** | .NET SDK 11.0.100-rc.1 as benchmarked (csproj targets net11.0, Release with Optimize=true, default tiered JIT) |
| **Platforms** | x86-64 Linux as measured (AMD Ryzen 7 3800X, Docker containers on an Arch Linux host); other .NET platforms not benchmarked |
| **Thread safety** | Single-threaded benchmark; not documented in the suite |
| **Drop-in for the baseline** | no |

## Gotchas

- The test is not really A\*: heuristic(v) = target - v counts vertices, but one edge spans up to 500 vertices, so the heuristic overestimates and the search degenerates into greedy best-first. It returns 1,172 edges (checksum 1,406,400 over 1,000 timed plus 200 warm-up runs) while Graph::BFS on the identical graph returns 1,050 (checksum 50,400 over 48 runs; same config and RNG reset, derived from run.js). With 1,173 pops per search the heap is barely exercised, so the test times allocate, fill and walk, not priority-queue speed. The code is the same in every language, so the comparison stands, but the name misleads.
- Harness effect, agent inference not measured: each test runs as its own process (benchmarks.rb launches one docker compose run per test), so glibc starts with its default 128 KB mmap threshold. After the first search frees its arrays the threshold rises to about 2 MB and the trim threshold to about 4 MB, and the roughly 4.3 MB freed at the end of every later search then exceeds the trim threshold, so the heap is probably trimmed and re-faulted on every search. The C# side runs GC.Collect() once before timing and then reuses its committed GC heap.
- The C rows are not a valid baseline: priority_queue_pop in c/src/graph_path.c compares the children with the stale root, breaks at once and leaves the last element at the root without sifting it down. Read the C++ rows (1.908 s at best).
- Each configuration has one self-timed run with no variance (benchmarks.rb records one run per test). The README says only JIT languages get a warm-up, but cpp/src/benchmark.cpp also warms up for 20 percent of the iterations, and every checksum includes those warm-up runs.

## Known shortcomings

- Identical pops and pushes on both heaps, so the heap-arity explanation is unsupported and the 4 MB array allocation plus fill per search probably dominates; C#/R2R and AOT also win; the C heap pop in c/src/graph_path.c is buggy (no sift-down), so the fair baseline is C++ (1.38x over the best C++ row); -flto inert; single run.
- Two harness flaws: the search is not real A\* (the heuristic target-v is inadmissible, so it is greedy best-first; it returns a 1,172-edge path where BFS on the same graph gives 1,050, from checksums 1,406,400/1,200 and 50,400/48, and the heap is barely used); and every glibc-malloc language loses (C, C++, Rust, Swift) while every tracing-GC runtime wins (C# including AOT and R2R, F#, Java, Julia, D, Crystal), whereas on Graph::BFS/DFS over the same graph C and C++ beat C#. The likely cause is per-search 4 MB vectors trimmed and re-faulted under glibc's mmap and trim thresholds with one process per test (inference, not measured): an allocator effect, not JIT.

## Caveats and trade-offs

C heap bug: priority_queue_pop in c/src/graph_path.c compares the children with the stale root instead of the moved last element, so it stops at once and leaves that element at the root without sifting it down. A verifier transcription of the code pops out of order on random input. On this benchmark's input the C search still does the same pops, pushes and edge scans as C++ and C# (verifier simulation), so the C rows time the same search with a cheaper pop, but the code is not a correct priority queue. Not a JIT win: the .NET ReadyToRun (1.222 s) and NativeAOT (1.321 s) rows beat every C/C++ row, and so do Java (1.486 s) and Julia (1.458 s), so the runtime-jit-beats-aot category fits poorly. Heap work is small (about 24,000 pushes per search), while each search allocates and fills two 500,000-int arrays (4 MB in total), which probably dominates the time. The result therefore likely measures allocation and initialisation behaviour rather than search code. Every language, C and C++ included, runs untimed warm-up iterations (20 percent of the timed count, cpp/src/benchmark.cpp and csharp/BenchmarkBase.cs) before the timed loop, so steady state is compared on both sides; the record's statement that only JIT languages get a warm-up was wrong. -flto appears only on the link line in cpp/Makefile, so the 'Fast' and 'Unsafe' rows get no actual LTO (the hot code sits in one translation unit, so this is probably immaterial). One measurement per test and configuration (no variance). LangArena's README calls it 'a subjective benchmark' and says AI tools helped translate the tests between languages. Rows were selected as tests where a managed-runtime row beats every C/C++ row; most tests go the other way (for example Sort::Quick, Sort::Merge and Binarytrees::Arena). Ratios are derived from the results file, not stated by the suite. [retier] The search is not real A\*: the heuristic is inadmissible, so it is greedy best-first (a 1,172-edge path where BFS gives 1,050) and the heap is barely used. Every glibc-malloc language loses (C, C++, Rust, Swift) while every tracing-GC runtime wins (C# including AOT and R2R, F#, Java, Julia, D, Crystal), and on Graph::BFS/DFS over the same graph C and C++ beat C#; the likely cause is per-search 4 MB vectors trimmed and re-faulted under glibc's mmap and trim thresholds (inference, not measured): an allocator effect, not JIT.

C# peak RSS about 354 MB; Java about 1.1 GB on this test.

## Maintenance

LangArena is active (622 commits, last commit 2026-10-08, monthly result files), MIT-licensed and has 41 stars; the C# file is easy to copy, but the only reusable component is the base-library PriorityQueue, and the win is best read as an allocator effect in a suite the README calls subjective.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** The code is public (cpp/src/graph_path.cpp with std::priority_queue vs csharp/GraphPath.cs with PriorityQueue&lt;int,int&gt;; run.js sets 500,000 vertices, jumps 20, jump_len 1000 and 1,000 timed searches), the compilers and flags (cpp/Makefile, results file) and the CPU are stated. A verifier simulation of the suite's graph reproduces the checksum's path length (1,172) and shows both heaps doing identical work (1,173 pops, 23,842 pushes and 25,625 edge scans per search), so same_algorithm holds and A stands.
- **Verifier notes:** Confirm at A: the numbers match the results file, and same work on both sides was verified by simulating the suite's graph (path 1,172 equals the checksum 1,406,400 over 1,200 runs including warm-up). Shortcomings to record: the heap explanation is unsupported (heap work is identical and small, and per-search 4 MB array allocation and fill likely dominate); not a JIT effect, since C# AOT and R2R also win; the C rows run a heap whose pop never sifts down; the baseline should be read as C++ (1.38x over the best C++ row); a single run; a subjective suite.
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-24 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-10-05-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/Makefile>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/Makefile>
  - <https://github.com/kostya/LangArena>
  - <https://github.com/kostya/LangArena/commits/master>
  - <https://github.com/kostya/LangArena/tree/master/cpp/src>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/run.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/cpp/src/benchmark.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/cpp/src/helper.cpp>
  - <https://github.com/kostya/LangArena/tree/master/csharp>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/cpp/src/graph_path.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/cpp/src/graph_path.hpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/csharp/GraphPath.cs>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/csharp/BenchmarkBase.cs>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/c/src/graph_path.c>
- **Sources the enricher read:**
  - <https://github.com/kostya/LangArena>
  - <https://github.com/kostya/LangArena/commits/master>
  - <https://github.com/kostya/LangArena/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/README.md>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/LICENSE>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/run.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/benchmarks.rb>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-10-05-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/cpp/src/graph_path.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/cpp/src/graph_path.hpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/cpp/src/benchmark.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/cpp/Makefile>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/csharp/GraphPath.cs>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/csharp/BenchmarkBase.cs>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/csharp/Benchmark.csproj>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/c/src/graph_path.c>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/rust/Cargo.toml>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:csharp/kostya/langarena#graph-astar`) · [data/wave14/enrich/raw/lang_csharp_kostya_langarena_graph_astar.json](../../../data/wave14/enrich/raw/lang_csharp_kostya_langarena_graph_astar.json) (enrichment confidence 0.6)

</details>
