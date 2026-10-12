# Nim ref-object binary trees (LangArena Binarytrees::Obj) vs C++ make_unique tree

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Systems and safety](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Nim` · `MIT` · 🟢 active

> Nim 2.2.12 ref objects (default ORC, Nim's own allocator) build and free depth-20 trees 1.35x faster than the best make_unique C++ build.

| | |
|---|---|
| **Beats** | C++ version of the same test (std::make_unique per tree node, g++ and clang++) and the C version (malloc per node) |
| **Claimed result** | Nim/Clang (prod row, default ORC) 1.55 s and Nim/GCC/ARC 1.193 s vs C++/G++/Fast 2.098 s (the best of the C and C++ prod, Fast, Unsafe and PGO configurations; only the instrumented C++/Clang++/PGO/Gen build is lower, at 2.081 s), C++/G++ 2.101 s and C/Clang 2.482 s. That is about 1.35x faster at default and 1.76x with ARC than the best C/C++ configuration (derived from page data). The lead held in the three previous runs (2026-08-14 to 2026-09-18: Nim/Clang 1.51-1.55 s vs best C/C++ 2.02-2.15 s). Memory: Nim/Clang 102 MB and Nim/GCC/ARC 69 MB vs C++/G++ 70 MB. |
| **Workload** | LangArena Binarytrees::Obj: build a complete binary tree of depth 20 of individually allocated nodes, sum it, and free it; 30 iterations (run.js). |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 7 3800X 8-Core Processor, 78GB RAM, x86_64 Linux (host kostya-ms7c37, results dated 2026-10-05) |
| **Compiler and flags** | C/C++ 'prod' build: make -j prod with -O2 -DNDEBUG -fstack-protector-strong -fno-omit-frame-pointer, -std=c++20 (clang 22.1.8, g++ 16.0.1 20260322 trunk), glibc malloc. The suite also builds 'Fast' (-O3 -march=native -mtune=native -ftree-vectorize -funroll-loops, -flto=thin passed only at link), 'Unsafe' (-O3 -march=native -ffast-math, -flto=full at link) and PGO variants of every C and C++ test, all in the results file. Nim 2.2.12: Nim/Clang (the suite's 'prod' Nim row) is nim c --threads:on -d:release --cc:clang; Nim/GCC/ARC (a 'hack' row) is nim c --threads:on -d:release --cc:gcc --gc:arc. In Nim's config/nim.cfg, -d:release turns on opt:speed, so the generated C is compiled at clang -O3 or gcc -O3 -fno-ident -fno-math-errno, both with -fno-strict-aliasing. Nim/Clang uses the default ORC memory manager (Nim doc/mm.md). No build passes -d:useMalloc, so Nim's own allocator is used. |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | yes |
| **Why it wins** | Not stated by the suite. Unverified inference: Nim's ref objects are allocated by Nim's own allocator and released by reference counting (ARC or ORC) at scope end, so the per-node allocate and free path avoids glibc malloc and free that the C and C++ tests hit once per node. The suite's own index-based Arena variant of this test removes the per-node allocation. |
| **Adoption** | 18.3k stars (nim-lang/Nim) |
| **Last commit** | 2026-10-11 |
| **Links** | [repository](https://github.com/nim-lang/Nim) · [benchmark](https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-10-05-kostya-ms7c37.js) |

## Verdict

LangArena's 2026-10-05 run on an AMD Ryzen 7 3800X (Linux, Docker) timed 30 depth-20 build-sum-free iterations. Nim 2.2.12 (nim c -d:release --cc:clang, clang 22.1.8 at -O3, default ORC, Nim's allocator) took 1.55 s and the Nim/GCC/ARC build 1.193 s. The best C/C++ configuration, C++/G++/Fast (GCC 16.0.1 trunk, -O3 -march=native, std::make_unique nodes, glibc malloc), took 2.098 s and the prod C++/G++ row 2.101 s. That is about 1.35x and 1.76x (derived from page data), with every checksum matching 75497436.

## Use it when

- Nim programs that build and drop many small heap nodes (ASTs, tries, temporary trees) with plain ref objects: the stock allocator plus ARC/ORC beat per-node new/malloc C++ and C by 1.35x (ORC, prod) to 1.76x (ARC) here.
- Acyclic structures where you can build with --mm:arc: the ARC rows (1.193 s gcc, 1.214 s clang) use about the same peak memory as C++ (69 MB vs 70 MB) and are still 1.7x faster.
- Deciding whether to port tree-heavy Nim code to C++ for speed: idiomatic make_unique C++ and malloc C lost in all 27 C and C++ rows (20 gcc and clang configurations plus the mycc and cproc hobby compilers; 2.081-2.548 s, and 3.65 s for the instrumented C/Gcc/PGO/Gen build) unless it switches to an arena.
- Any Nim backend: every Nim row on this test (gcc, clang, the nim cpp C++ backend at 1.494-1.523 s, NLVM at 1.385 s) is faster than the best C/C++ row.

## Skip it when

- As evidence that Nim beats C or C++ with an arena: the suite's realloc-grown C index arena takes 0.255 s (C/Gcc/Fast, 27 MB) and the C++ std::vector arena 0.512-0.685 s, while Nim's own seq-based arena variant takes 1.049 s at 235 MB.
- Memory-constrained code on the default ORC: peak RSS is 102 MB vs 70 MB for C++ (about 46 percent more), because each ORC cell is 48 bytes against a 32-byte malloc chunk (derived, see gotchas).
- Comparisons against C or C++ linked with a fast allocator (mimalloc, jemalloc, a pool): not measured; the baseline is glibc malloc in the suite's ubuntu:26.04 containers.
- Builds that need -d:useMalloc (Valgrind, sanitizers) replace Nim's allocator with the C one; not measured, and the gap should shrink since the allocator is the likely source of the win (inference).
- Cyclic object graphs with the faster ARC setting: ARC leaks cycles and the docs say async code needs ORC, so the 1.76x figure only holds for acyclic data.

## How it is fast

The difference is in allocation and freeing, not in the loop code. Nim's nimNewObj allocates from Nim's own allocator (lib/system/alloc.nim): a thread-local region with page-sized small chunks in 16-byte size classes. An allocation pops the chunk's free list or bumps an accumulator, and a free pushes the cell back onto its chunk's free list; the source says 'true deallocation is delayed for as long as possible in favor of reusing cells'. ARC/ORC frees the tree with a recursive destructor at scope end, using non-atomic RC operations (doc/mm.md). The C and C++ versions instead call glibc malloc/free (C++ through std::make_unique and the unique_ptr destructor) once per 24-byte node. Per node that comes to 24.6 ns for Nim/Clang (ORC), 19.0 ns for Nim/GCC/ARC, 33.3 ns for C++/G++/Fast and 39.5 ns for C/Clang (derived from page data over 62.9M timed nodes). This mechanism is an inference from the sources; the suite does not explain the result.

## Compared with alternatives

This is stronger evidence than the benchLANG Nim binary-trees sibling (one run, compile-time constant inputs, 1.25x vs C): it measures 20 gcc and clang C/C++ build configurations, ARC, ORC and backend variants, and an arena variant over five monthly runs. Unlike the Koka cfold and deriv siblings, the C++ baseline here really frees its nodes. Java's Binarytrees::Obj row is 3.2x faster (0.479 s) but peaks at 892 MB, so pick Nim when deterministic freeing and 69-102 MB matter.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | Nim 2.2.12 compiler plus a C compiler (clang 22.1.8 from the LLVM release tarball for the prod row, gcc 16 trunk for the ARC row); the tree code uses only Nim's system module, while the suite's harness also needs the jsony and regex nimble packages |
| **Minimum toolchain** | Nim 2.2.12 as measured (nimble file requires nim &gt;= 2.0.0); ORC is the default memory manager in the v2.2.12 doc/mm.md; older Nim versions were not measured |
| **Platforms** | Measured on x86-64 Linux (AMD Ryzen 7 3800X, 78 GB) in Docker images built FROM ubuntu:26.04 with a 16 GB memory limit; the build targets generic x86-64 (no -march=native) |
| **Thread safety** | Not applicable: single-threaded workload built with --threads:on; ARC/ORC RC operations are non-atomic and object subgraphs are moved between threads rather than shared (doc/mm.md) |
| **Drop-in for the baseline** | no |

## Gotchas

- The default ORC row pays for cycle collection the tree does not need. TreeNodeObj has no {.acyclic.} annotation, and Nim's ORC announcement post says this annotation 'can be crucial in order to get ORC's performance close to ARC's'. ORC also adds a rootIdx word to every object header (lib/system/arc.nim RefHeader). With a 24-byte payload and MemAlign 16, that makes 48-byte ORC cells against 32-byte ARC cells: 2,097,151 x 48 B = 100.7 MB and x 32 B = 67.1 MB, which matches the measured 102 MB and 69 MB (derived). The headline 1.76x comes from the non-default ARC 'hack' row; the default prod row gives 1.35x.
- The harness looks fair on work done. C frees every node in a separate pass and C++ through recursive unique_ptr destructors inside each timed iteration, and Nim's destructor runs at the end of run(); the 69 MB peak of the ARC row shows only one tree is alive at a time. The Nim harness calls GC_fullCollect() after warm-up and after the timer, but under ARC/ORC an acyclic tree that has already been freed gives that call nothing to collect. Depth and iteration counts are read from run.js at runtime.
- The flags and types are not matched. Nim's -d:release maps to clang -O3 or gcc -O3 -fno-ident -fno-math-errno, both with -fno-strict-aliasing (v2.2.12 config/nim.cfg), and keeps overflow and bound checks on. The C/C++ prod rows are -O2 with -fstack-protector-strong, but the -O3 -march=native Fast, -ffast-math Unsafe and PGO rows also lose (2.098-2.457 s). The Nim node holds a 64-bit int item where C and C++ use a 32-bit int.
- Each configuration is timed once per monthly run, with no repeats. The lead held in all five runs checked (2026-07-14 to 2026-10-05: Nim/Clang 1.513-1.564 s vs C++/G++ 2.101-2.21 s), including the 2026-10-05 run after the host OS moved from Ubuntu to Arch Linux (the containers stay ubuntu:26.04).

## Known shortcomings

- Allocator win (Nim allocator plus ARC/ORC vs glibc malloc per node); the arena variant reverses it (C 0.255 s vs Nim 1.049 s); the headline 1.76x is a non-default ARC build, default ORC gives 1.35x; lead stable over 4 monthly runs.
- No harness bug: every side frees each tree inside the timed loop and checksums match. The win is Nim's own free-list allocator (alloc.nim) plus ARC/ORC against glibc malloc per node; the headline 1.76x is the non-default ARC hack row and the default ORC prod row gives 1.35x. TreeNodeObj lacks {.acyclic.}, and ORC's extra header word makes 48-byte cells against 32-byte ARC cells (102 vs 69 MB, derived). The Arena variant reverses the result. The lead held in five runs from 2026-07-14 to 2026-10-05.

## Caveats and trade-offs

The win is allocation-strategy specific: an arena or pool allocator in C or C++ beats it, and the suite's Binarytrees::Arena rows go the other way (C/Gcc/Fast 0.255 s, C++/G++/Fast 0.53 s, Nim/Clang 1.049 s). The 1.76x figure is the non-default ARC 'hack' configuration; the default ORC 'prod' row gives 1.35x and uses 46% more memory than C++ (102 vs 70 MB). Nim's generated C is compiled at -O3, while the headline C/C++ prod rows are -O2; the -O3 Fast and Unsafe rows also lose. Nim's node carries a 64-bit int item, where C and C++ use a 32-bit int. ORC as the default and the -O3 mapping were checked in Nim's doc/mm.md and config/nim.cfg on the devel branch, not in the 2.2.12 tag. V (Clang) 0.806 s, Crystal 1.175 s and Java also beat C++ on this test; Rust (2.62 s), Zig (6.31 s) and C3 (3.4 s) are slower. LangArena calls itself a subjective benchmark, and its README says AI tools helped translate the tests. Each configuration is timed once per monthly run with no variance reported, though four monthly runs agree. Rows were selected by the search agent as tests where the language beats every C/C++ configuration; most other tests in the suite go the other way. Ratios are derived from the results file, not stated by the suite. [retier] Enricher: no harness bug (every side frees each tree in the timed loop, checksums match). The win is Nim's own free-list allocator (alloc.nim) plus ARC/ORC against glibc malloc per node. TreeNodeObj lacks {.acyclic.}, and ORC's extra header word makes 48-byte cells against 32-byte ARC cells (102 vs 69 MB, derived). The lead held in five runs from 2026-07-14 to 2026-10-05.

About 45 percent more memory than C++ in this test; reference counting adds a count word per object.

## Maintenance

Nim is actively developed (MIT with some modules excepted, 18.3k stars, 23,330 commits on devel), and LangArena is an active MIT suite (41 stars, last commit 2026-10-08, monthly reruns); the 20-line tree code is copyable, but the win belongs to Nim's runtime allocator and ARC/ORC, not to the source.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** Independent third-party suite with public code for every side (nim/src/benchmarks/binarytrees.nim, cpp/src/binarytrees.cpp and .hpp, c/src/binarytrees.c; workload in run.js). C/C++ flags are in cpp/Makefile, and the Nim build commands, compiler versions and CPU (AMD Ryzen 7 3800X) are in results/2026-10-05-kostya-ms7c37.js. The record's runtime and memory numbers match the Binarytrees::Obj rows. Same tier and precedent as lang:java/kostya/langarena#binarytrees-obj.
- **Verifier notes:** Confirm at A. Runtimes and memory match the 2026-10-05 results file, and the lead is stable over four monthly runs. The Nim build commands and memory-manager details were checked in the results file, Nim's config/nim.cfg and doc/mm.md. Shortcomings to record: allocator win (Nim allocator plus ARC/ORC against per-node glibc malloc/free) that the arena variant reverses; the headline 1.76x is a non-default ARC build; single run per configuration; subjective, AI-assisted suite; prod C/C++ at -O2, though the -O3 rows also lose. Metadata checks out: nim-lang/Nim is MIT (some modules excepted per copying.txt), 18.3k stars, last commit 2026-10-11; LangArena is MIT with 41 stars.
- **Fields the verifier corrected:** `compiler_and_flags`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-58 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-10-05-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-09-18-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-09-03-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-08-14-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/nim/src/benchmarks/binarytrees.nim>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/nim/src/benchmark.nim>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/nim/src/benchmarks.nim>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/binarytrees.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/binarytrees.hpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/src/binarytrees.c>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/Makefile>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/run.js>
  - <https://github.com/kostya/LangArena>
  - <https://github.com/kostya/LangArena/tree/master/nim/src>
  - <https://github.com/kostya/LangArena/tree/master/results>
  - <https://github.com/nim-lang/Nim>
  - <https://github.com/nim-lang/Nim/commits/devel>
  - <https://raw.githubusercontent.com/nim-lang/Nim/devel/config/nim.cfg>
  - <https://raw.githubusercontent.com/nim-lang/Nim/devel/doc/mm.md>
  - <https://raw.githubusercontent.com/nim-lang/Nim/devel/doc/nimc.md>
  - <https://raw.githubusercontent.com/nim-lang/Nim/devel/changelogs/changelog_2_0_0.md>
- **Sources the enricher read:**
  - <https://github.com/nim-lang/Nim>
  - <https://github.com/kostya/LangArena/commits/master>
  - <https://github.com/kostya/LangArena/commits/master/nim/src/benchmarks/binarytrees.nim>
  - <https://github.com/kostya/LangArena/issues?q=is%3Aissue+nim>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/run.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/benchmarks.rb>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/docker-compose.yaml>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/docker/base>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/docker/base_clang>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/docker/base_gcc>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/docker/nim_clang>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/docker/nim_gcc>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-10-05-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-09-18-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-09-03-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-08-14-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-07-14-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/nim/src/benchmarks/binarytrees.nim>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/nim/src/benchmark.nim>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/nim/src/benchmarks.nim>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/nim/benchmarks.nimble>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/nim/run>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/binarytrees.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/binarytrees.hpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/benchmark.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/Makefile>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/src/binarytrees.c>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/Makefile>
  - <https://raw.githubusercontent.com/nim-lang/Nim/v2.2.12/config/nim.cfg>
  - <https://raw.githubusercontent.com/nim-lang/Nim/v2.2.12/doc/mm.md>
  - <https://raw.githubusercontent.com/nim-lang/Nim/v2.2.12/lib/system/alloc.nim>
  - <https://raw.githubusercontent.com/nim-lang/Nim/v2.2.12/lib/system/arc.nim>
  - <https://raw.githubusercontent.com/nim-lang/Nim/v2.2.12/lib/system/orc.nim>
  - <https://raw.githubusercontent.com/nim-lang/Nim/v2.2.12/lib/system/bitmasks.nim>
  - <https://raw.githubusercontent.com/nim-lang/website/master/jekyll/_posts/2020-12-08-introducing-orc.md>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:nim/kostya/langarena#binarytrees-obj`) · [data/wave14/enrich/raw/lang_nim_kostya_langarena_binarytrees_obj.json](../../../data/wave14/enrich/raw/lang_nim_kostya_langarena_binarytrees_obj.json) (enrichment confidence 0.75)

</details>
