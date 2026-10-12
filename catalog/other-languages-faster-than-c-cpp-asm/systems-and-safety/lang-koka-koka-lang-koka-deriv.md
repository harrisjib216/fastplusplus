# Koka (Perceus reference counting): deriv benchmark vs C++ gcc 9.3.0

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Systems and safety](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Koka` · `Apache-2.0` · 🟢 active

> Koka (functional language compiled to C with Perceus reference counting): deriv ran 1.33x faster than a never-freeing C++ port.

| | |
|---|---|
| **Beats** | C++ port in test/bench/cpp/deriv.cpp (gcc 9.3.0, CMake Release -O3, standard libc allocator): same rewrite rules and node allocations as the Koka version, but memory is never reclaimed. |
| **Claimed result** | Perceus TR Figure 9 (identical chart in the README), normalized to Koka = 1.00: deriv execution time C++ 1.33 (Koka about 1.33x faster), peak working set C++ 2.25x. Koka 'no-opt' is 1.05, Java 0.86 (Java faster than Koka). Other rows: cfold C++ 3.33, rbtree C++ 0.92 and nqueens C++ 0.79 (C++ faster). |
| **Workload** | deriv: symbolic derivative of a large expression, an allocation-heavy benchmark with little computation. |
| **Metric** | throughput |
| **Hardware** | 6-core AMD Ryzen 5 3600XT at 3.8 GHz, 64 GiB 3600 MHz memory, Ubuntu 20.04, November 2020; README says averaged over 10 runs, the Perceus tech report says median over 10 runs |
| **Compiler and flags** | Koka 2.0.3 -O2 (test/bench/koka/CMakeLists.txt), which the v2.0.3 compiler (src/Compiler/Options.hs) turns into gcc 9.3.0 '-O2 -flto -DNDEBUG' on the generated C, linked with Koka's bundled mimalloc (KK_MIMALLOC, MI_MAX_ALIGN_SIZE=8; the paper says 'a customized version of the mimalloc allocator'); C++: gcc 9.3.0, C++17, built through test/bench/CMakeLists.txt with CMAKE_BUILD_TYPE Release and no extra flags in cpp/CMakeLists.txt, so CMake's default '-O3 -DNDEBUG', standard libc allocator. Flags are derived from the public build files, not printed with the results. Current Koka (v3.2.x) uses gcc -O2 -DNDEBUG -march=haswell instead. |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | not stated |
| **Same optimization level** | not stated |
| **Why it wins** | Source (README): precise Perceus reference counting with reuse analysis, compiled to C 'without needing a garbage collector or runtime system'; the README frames the benchmarks as showing reference counting is viable and competitive, not as a direct absolute-speed comparison across languages. |
| **Adoption** | 4.1k stars (Microsoft Research, Daan Leijen) |
| **Last commit** | 2026-10-01 |
| **Links** | [repository](https://github.com/koka-lang/koka) · [benchmark](https://microsoft.com/en-us/research/uploads/prod/2020/11/perceus-tr-v4.pdf) |

## Verdict

Perceus TR Figure 9 and the identical README chart: on a 6-core AMD Ryzen 5 3600XT running Ubuntu 20.04 (November 2020), the gcc 9.3.0 C++ port (CMake Release -O3, glibc malloc, never frees) took 1.33x the time and 2.25x the peak RSS of Koka 2.0.3 (generated C at -O2 -flto with bundled mimalloc). On the same scale Koka without reuse optimizations scored 1.05 and Java 0.86.

## Use it when

- Symbolic algebra, term rewriting or compiler passes over immutable trees with heavy subterm sharing, when memory should be reclaimed promptly without a tracing GC (the never-freeing C++ port peaked at 2.25x Koka's RSS).
- Functional rewriting code you would otherwise write in OCaml, Haskell or Swift, when you want C output and direct linking with C libraries.
- Long-running single-threaded symbolic work where peak working set matters as much as time.
- x64 Linux, macOS (x64 and M1) or Windows, where binary installers exist.

## Skip it when

- When a tuned tracing GC is an option: Java (HotSpot G1) beat Koka on this row (0.86 relative time), and the paper reports that OCaml used slightly less memory here.
- As evidence that Koka beats C++ you can write yourself: nobody tried a C++ port with an arena, a node pool, reference counting or mimalloc linked in. The authors call Figure 9 'not a direct comparison of absolute performance between systems', and C++ wins rbtree (0.92) and nqueens (0.79) in the same figure.
- Production code: the README calls Koka v3 'a research language that is currently under development and not quite ready for production use', and its ecosystem is small.
- Cyclic data: there is no cycle collector, so cycles built through mutable references leak.

## How it is fast

Perceus inserts precise reference-count operations at compile time and frees each node when its last reference dies. Each derivative's dead input is therefore reclaimed, and its memory is recycled by Koka's bundled mimalloc (8-byte alignment) instead of growing the heap. Reuse analysis barely matters here: the paper says heavy sharing sends most matches down the slow path, and Koka 'no-opt' is only 1.05x optimized Koka. The C++ port runs the same rewrite rules but allocates with glibc malloc (16-byte aligned, per the paper) and never frees, so the 1.33x gap most likely comes from memory management (allocator, reclamation, footprint), not code generation.

## Compared with alternatives

Of the two Koka rows, deriv is the more like-for-like (the same rewrite rules on both sides, unlike cfold's shallow C++ fold and copying reassoc), but its 1.33x margin is small and Java beats it. Among siblings, the Nim ref-object binary-trees entry is stronger evidence that managed memory can beat C++ allocation, because its C++ baseline frees its nodes; pick Koka when you want functional tree rewriting with prompt reclamation and C output.

## Integration

| | |
|---|---|
| **Form** | language and compiler (Koka source compiled to C, then by gcc, clang or MSVC); not a C++ library |
| **Dependencies** | Koka compiler (binary installer, or built from source with Haskell stack) plus a C compiler; the kklib runtime with bundled mimalloc is linked automatically; vcpkg optional for C libraries |
| **Minimum toolchain** | Measured with Koka 2.0.3 and gcc 9.3.0; current release Koka v3.2.9 (2026-09-17) |
| **Platforms** | Binary installers for Windows x64, macOS x64 and Apple M1, and Linux x64; other platforms build from source. Benchmark run on Linux x86-64. |
| **Thread safety** | Each object carries a thread-shared flag: reference counts stay non-atomic until an object is shared with another thread, then use atomic operations (Perceus TR section 2.7.2). The paper measured 5% to 59% slowdowns with always-atomic counts. The benchmark is single-threaded. |
| **Drop-in for the baseline** | no |

## Gotchas

- Same algorithm, different memory management: deriv.cpp mirrors the Koka rewrite rules case for case but allocates every node with new and never deletes, while Koka frees and recycles. At the measured v2.0.3 tag, deriv.cpp's mul returned the existing zero node where Koka allocates Val(0); HEAD now allocates new ValExpr(0). That gave C++ slightly fewer allocations, so the published row slightly favours C++ on allocation count.
- C++ pown mishandles negative exponents (pown(x,-1) returns x). The path is never reached, because every Pow base in this workload stays Var x, so powr never sees two constants and the printed counts are unaffected (derived from the source).
- Measurement: run.kk at v2.0.3 times the whole process with /usr/bin/time -f '%e %M' (wall clock and peak RSS, including printing the per-level node counts and process exit), drops the single slowest run and averages the rest. The Perceus TR says 'median over 10 runs' and the README says 'averaged'.
- The numbers are first-party, from Koka 2.0.3 in November 2020. At HEAD, deriv.kk's d borrows its argument (^e) and the suite builds with a newer compiler and --stack=128M, so the row has not been re-measured on current Koka. C++ uses 64-bit long, while Koka's int is arbitrary precision with a small-int fast path.

## Known shortcomings

- Perceus TR MSR-TR-2020-42 v4 Fig. 9 (1.33x time, 2.25x RSS): same algorithm but the C++ side never frees; mimalloc vs libc malloc, so part of the win belongs to mimalloc (listed); Java beats Koka (0.86) and reuse barely helps (no-opt 1.05); Koka 2.0.3 (2020).
- Same rewrite rules on both sides; the gap is memory management (C++ never frees through glibc malloc, Koka frees and reuses through Perceus and mimalloc): Koka no-opt is 1.05 and Java 0.86 beats Koka on the same chart. At the measured v2.0.3 tag deriv.cpp's mul reused the existing zero node where Koka allocates Val(0), which slightly favours C++ on allocation count. C++ pown(x,-1) returns x, but the path is unreachable in this workload (every Pow base stays Var x), so counts are unaffected. run.kk times the whole process with /usr/bin/time %e %M, drops the slowest run and averages the rest, while the TR says median over 10 runs; the C++ build gets no stack setting (Java gets -Xss128m) and the current bench README asks for ulimit -s unlimited.

## Caveats and trade-offs

The paper and README say the results are 'not a direct comparison of absolute performance between systems'. The C++ version never frees memory (peak working set 2.25x Koka), while Koka frees and reuses with mimalloc; an arena C++ version or C++ with mimalloc was not tried. At the measured v2.0.3 tag deriv.cpp's mul returned the existing zero node where HEAD now allocates new ValExpr(0), so the benchmark code at HEAD differs slightly from what was measured. Numbers are from Koka 2.0.3 and gcc 9.3.0 in November 2020 (Koka is now v3.2.9). Java beats Koka on this row (0.86), and C++ wins rbtree and nqueens. The paper notes reuse analysis barely helps on deriv (no-opt 1.05) because of heavy sharing. [retier] Enricher: same rewrite rules on both sides; the gap is memory management (C++ never frees through glibc malloc, Koka frees and reuses through Perceus and mimalloc), Koka no-opt is 1.05 and Java 0.86 beats Koka on the same chart. At the measured v2.0.3 tag deriv.cpp's mul reused the existing zero node where Koka allocates Val(0), slightly favouring C++ on allocation count. C++ pown(x,-1) returns x, but the path is unreachable in this workload. run.kk times the whole process with /usr/bin/time %e %M, drops the slowest run and averages the rest, while the TR says median over 10 runs; the C++ build gets no stack setting (Java gets -Xss128m) and the current bench README asks for ulimit -s unlimited.

Reference counting with in-place reuse needs no tracing GC but adds refcount work and cannot reclaim cycles; Koka compiles through C so any C toolchain can build it; much smaller ecosystem than C++.

## Maintenance

Koka is actively developed at Microsoft Research (v3.2.9 released 2026-09-17, 4.1k stars, Apache-2.0) but calls itself a research language not ready for production. This is a 2020 first-party result against a C++ port that never frees memory, so read the 1.33x as evidence that garbage-free reference counting is competitive, not as a general Koka-versus-C++ speed ratio.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now B.
- **Tier reason:** Upgraded C to B: the deriv row (C++ time 1.33, peak working set 2.25, Koka 1.00) is in Figure 9 of the Perceus paper (MSR-TR-2020-42 v4, extended version of the peer-reviewed PLDI 2021 paper, opened) with gcc 9.3.0 and AMD 3600XT stated. Not A: compile flags are not stated with the results (only derivable from CMake's Release default and the v2.0.3 Koka compiler source), first-party run.
- **Verifier notes:** Numbers verified on the README chart and the Perceus TR figure (deriv 1.33x time, 2.25x RSS). Shortcomings to record: C++ never reclaims memory, mimalloc vs glibc malloc (part of the win belongs to mimalloc), authors disclaim it as an absolute speed comparison, Java faster than Koka on deriv, 2020 numbers on Koka 2.0.3, benchmark source changed since. License Apache-2.0, 4.1k stars, last commit 2026-10-01, active.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `baseline`, `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** verifier batch-88 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/koka-lang/koka/HEAD/readme.md>
  - <https://raw.githubusercontent.com/koka-lang/koka/HEAD/doc/bench-amd3600-nov-2020.png>
  - <https://github.com/koka-lang/koka>
  - <https://github.com/koka-lang/koka/commits>
  - <https://raw.githubusercontent.com/koka-lang/koka/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/koka-lang/koka/HEAD/test/bench/CMakeLists.txt>
  - <https://raw.githubusercontent.com/koka-lang/koka/HEAD/test/bench/cpp/CMakeLists.txt>
  - <https://raw.githubusercontent.com/koka-lang/koka/HEAD/test/bench/koka/CMakeLists.txt>
  - <https://raw.githubusercontent.com/koka-lang/koka/v2.0.3/test/bench/CMakeLists.txt>
  - <https://raw.githubusercontent.com/koka-lang/koka/v2.0.3/test/bench/cpp/CMakeLists.txt>
  - <https://raw.githubusercontent.com/koka-lang/koka/v2.0.3/test/bench/koka/CMakeLists.txt>
  - <https://raw.githubusercontent.com/koka-lang/koka/v2.0.3/src/Compiler/Options.hs>
  - <https://raw.githubusercontent.com/koka-lang/koka/v2.0.3/src/Compiler/Compile.hs>
  - <https://raw.githubusercontent.com/koka-lang/koka/v2.0.3/kklib/CMakeLists.txt>
  - <https://raw.githubusercontent.com/koka-lang/koka/HEAD/src/Compile/Options.hs>
  - <https://microsoft.com/en-us/research/uploads/prod/2020/11/perceus-tr-v4.pdf>
  - <https://raw.githubusercontent.com/koka-lang/koka/HEAD/test/bench/cpp/deriv.cpp>
  - <https://raw.githubusercontent.com/koka-lang/koka/v2.0.3/test/bench/cpp/deriv.cpp>
  - <https://raw.githubusercontent.com/koka-lang/koka/HEAD/test/bench/koka/deriv.kk>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/koka-lang/koka/HEAD/readme.md>
  - <https://github.com/koka-lang/koka>
  - <https://microsoft.com/en-us/research/uploads/prod/2020/11/perceus-tr-v4.pdf>
  - <https://github.com/koka-lang/koka/tree/v2.0.3/test/bench>
  - <https://raw.githubusercontent.com/koka-lang/koka/v2.0.3/test/bench/run.kk>
  - <https://raw.githubusercontent.com/koka-lang/koka/v2.0.3/test/bench/README.md>
  - <https://raw.githubusercontent.com/koka-lang/koka/HEAD/test/bench/README.md>
  - <https://raw.githubusercontent.com/koka-lang/koka/v2.0.3/test/bench/cpp/deriv.cpp>
  - <https://raw.githubusercontent.com/koka-lang/koka/HEAD/test/bench/cpp/deriv.cpp>
  - <https://raw.githubusercontent.com/koka-lang/koka/v2.0.3/test/bench/koka/deriv.kk>
  - <https://raw.githubusercontent.com/koka-lang/koka/HEAD/test/bench/koka/deriv.kk>
  - <https://raw.githubusercontent.com/koka-lang/koka/v2.0.3/test/bench/CMakeLists.txt>
  - <https://raw.githubusercontent.com/koka-lang/koka/HEAD/test/bench/CMakeLists.txt>
  - <https://raw.githubusercontent.com/koka-lang/koka/v2.0.3/test/bench/cpp/CMakeLists.txt>
  - <https://raw.githubusercontent.com/koka-lang/koka/HEAD/test/bench/cpp/CMakeLists.txt>
  - <https://raw.githubusercontent.com/koka-lang/koka/v2.0.3/test/bench/koka/CMakeLists.txt>
  - <https://raw.githubusercontent.com/koka-lang/koka/HEAD/test/bench/koka/CMakeLists.txt>
  - <https://github.com/koka-lang/koka/issues?q=is%3Aissue+benchmark>
  - <https://github.com/koka-lang/koka/issues?q=is%3Aissue+%22stack+overflow%22>
  - <https://github.com/koka-lang/koka/issues?q=is%3Aissue+label%3Aruntime-performance>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:koka/koka-lang/koka#deriv`) · [data/wave14/enrich/raw/lang_koka_koka_lang_koka_deriv.json](../../../data/wave14/enrich/raw/lang_koka_koka_lang_koka_deriv.json) (enrichment confidence 0.7)

</details>
