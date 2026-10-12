# Koka (Perceus reference counting): cfold benchmark vs C++ gcc 9.3.0

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Systems and safety](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Koka` · `Apache-2.0` · 🟢 active

> Koka: functional language compiled to C with Perceus reference counting; cfold ran 3.3x faster than a never-freeing C++ port.

| | |
|---|---|
| **Beats** | C++ port in test/bench/cpp/cfold.cpp (gcc 9.3.0, CMake Release -O3, standard libc allocator): allocates every node with new and never frees anything, and its const_folding only folds the root node (no recursion into children), unlike the recursive Koka cfold. |
| **Claimed result** | Perceus TR Figure 9 (identical chart in the README, doc/bench-amd3600-nov-2020.png), normalized to Koka = 1.00: cfold execution time C++ 3.33 (Koka about 3.3x faster), peak working set C++ 2.94x. Koka 'no-opt' (reuse analysis and drop/reuse specialization off) is 1.54, so even without reuse Koka is about 2.2x faster than C++ (derived from page data). Other rows of the same figure: deriv C++ 1.33, rbtree C++ 0.92 and nqueens C++ 0.79 (C++ faster), rbtree-ck no C++ version. |
| **Workload** | cfold: constant folding over a large symbolic expression, an allocation-heavy benchmark with little computation. |
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

Perceus TR Figure 9 and the identical README chart: on a 6-core AMD Ryzen 5 3600XT running Ubuntu 20.04 (November 2020), the gcc 9.3.0 C++ port (CMake Release -O3, glibc malloc, never frees) took 3.33x the time and 2.94x the peak RSS of Koka 2.0.3 (generated C at -O2 -flto with bundled mimalloc). Koka with reuse optimizations off scored 1.54, which still makes it about 2.2x faster than C++ (derived from page data).

## Use it when

- Tree-rewriting code (compiler passes, symbolic algebra, term rewriting) written in a functional style that would otherwise copy nodes immutably: reuse analysis turns those copies into in-place updates without manual ownership code.
- Allocation-heavy programs that need garbage-free memory behaviour without a tracing GC: Perceus frees each node as it dies, so peak working set stays close to the live data (the never-freeing C++ port peaked at 2.94x Koka's RSS).
- Research or prototyping of functional algorithms that must call C: Koka emits C and can link C libraries directly.
- Single-threaded work on x64 Linux, macOS (x64 and M1) or Windows, where binary installers exist.

## Skip it when

- As evidence that Koka beats C++ you can write yourself: nobody tried an in-place C++ reassoc (the input tree is dead after reassoc in the C++ main too), an arena or pool, or mimalloc linked into the C++ binary. The paper calls Figure 9 'not a direct comparison of absolute performance between systems'.
- Workloads that are not allocation-bound or that share structure heavily: in the same figure C++ wins rbtree (0.92) and nqueens (0.79), and Java beats Koka on deriv (0.86).
- Production code: the README calls Koka v3 'a research language that is currently under development and not quite ready for production use', and its ecosystem is small.
- Cyclic data: there is no cycle collector, so cycles built through mutable references leak.
- Deep non-tail recursion over huge structures without stack tuning: the current bench README advises 'ulimit -s unlimited' for cfold, and current Koka builds the suite with --stack=128M.

## How it is fast

Perceus inserts precise reference-count operations at compile time and frees each node as soon as it dies. Reuse analysis (FBIP, 'functional but in-place') then turns a match on a uniquely owned constructor followed by an allocation of the same shape into an in-place update. In cfold, append_add rebuilds the spine of a list it owns, so optimized Koka rewrites those cells in place where the C++ port allocates a fresh node at every step. Koka also links a customized mimalloc with 8-byte alignment, while the paper notes that the C++ side's glibc allocations must be 16-byte aligned.

## Compared with alternatives

Most siblings are tools (fuc cpz/rmz, mosdepth, sambamba) or language entries with fairer harnesses (Nim ref-object binary trees against a C++ make_unique tree that frees its nodes; Rust and Zig sorts against std::sort). Pick Koka for functional tree rewriting, where in-place reuse of uniquely owned nodes replaces copying, and treat the sibling deriv row (same rewrite rules on both sides) as the more like-for-like Koka-versus-C++ number.

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

- Harness flaw, allocation volume differs by design (derived from the source, not measured): mk_expr(20,1) builds 2^21-1 nodes, and the C++ reassoc copies the whole left spine at every Add (append_add returns a new AddExpr per step), about 20 x 2^19 = 10.5M extra nodes that are never freed. Optimized Koka rewrites the same uniquely owned cells in place and allocates about one cell per internal node. So the 3.33x mostly measures copying without freeing against in-place reuse, not code generation. Even Koka 'no-opt' (1.54) frees and recycles through mimalloc, while C++ touches fresh memory for every node.
- The two programs fold differently: the C++ const_folding inspects only the root (one rewrite, no recursion), while Koka's cfold folds the whole list bottom-up, and the C++ eval then walks the unfolded list of 2^20 leaves. The printed checksums match, but the timed phases do not correspond one-to-one (same_algorithm is false).
- Measurement: run.kk at v2.0.3 times the whole process with /usr/bin/time -f '%e %M' (wall clock and peak RSS, including tree construction, the first eval and process exit), drops the single slowest run and averages the rest. The Perceus TR says 'median over 10 runs' and the README says 'averaged'. Java gets -Xss128m for cfold but C++ gets no stack setting, so the C++ run depends on the shell's stack ulimit, which the 2020 instructions do not document.
- The numbers are first-party, from Koka 2.0.3 in November 2020. At HEAD the Koka benchmark has been reformatted and given a test() entry point, and the suite builds with a newer compiler, so the chart has not been re-measured on current Koka. C++ uses 64-bit long, while Koka's int is arbitrary precision with a small-int fast path, which costs Koka extra checks.

## Known shortcomings

- Perceus TR MSR-TR-2020-42 v4 Fig. 9 (3.33x time, 2.94x RSS): the C++ baseline leaks every node and its const_folding is non-recursive (unequal algorithm); Koka uses mimalloc against glibc malloc, so part of the win belongs to mimalloc (listed); the authors disclaim an absolute-speed comparison; Koka 2.0.3 (2020), -O2 mapping to gcc -O2 -flto vs CMake Release -O3.
- Unequal work in the C++ baseline (derived from the source, not measured): the C++ reassoc copies the whole left spine at every Add (append_add returns a new AddExpr per step), about 20 x 2^19 = 10.5M extra nodes that are never freed, while optimised Koka rewrites the same uniquely owned cells in place; the input tree is dead after reassoc in C++ main too, so an in-place C++ version would be legal. The C++ const_folding inspects only the root and its eval walks the unfolded 2^20-element list, so the phases are not one-to-one. v2.0.3 run.kk times the whole process with /usr/bin/time, drops the slowest run and averages the rest, while the Perceus TR says median over 10 runs; C++ gets no stack setting (Java gets -Xss128m). The paper admits C++ never frees in deriv, nqueens and cfold. Retiered to C: the 3.33x mostly measures copy-without-free against in-place reuse.

## Caveats and trade-offs

The paper and README say the results are 'not a direct comparison of absolute performance between systems'. Not like-for-like: the C++ version never reclaims memory (glibc malloc, peak working set 2.94x Koka) while Koka frees and reuses nodes in place with mimalloc, and the C++ const_folding is shallow (does strictly less work than Koka's recursive cfold; the eval checksum is unchanged either way). An arena or pooled C++ version, or C++ linked against mimalloc, was not tried. Numbers are from Koka 2.0.3 and gcc 9.3.0 in November 2020; Koka is now v3.2.9 with different C flags. Koka ints are arbitrary-precision with a small-int fast path, C++ uses long. Mixed results across the suite: C++ wins rbtree (0.92) and nqueens (0.79). [retier] Enricher: unequal work (derived from the source, not measured); the C++ reassoc copies the whole left spine at every Add (append_add returns a new AddExpr per step), about 20 x 2^19 = 10.5M extra nodes that are never freed, while optimised Koka rewrites the same uniquely owned cells in place; the input tree is dead after reassoc in C++ main too, so an in-place C++ version would be legal. The C++ const_folding inspects only the root and its eval walks the unfolded 2^20-element list, so the phases are not one-to-one. v2.0.3 run.kk times the whole process with /usr/bin/time, drops the slowest run and averages the rest, while the Perceus TR says median over 10 runs; the C++ build gets no stack setting (Java gets -Xss128m).

Reference counting with in-place reuse needs no tracing GC but adds refcount work and cannot reclaim cycles; Koka compiles through C so any C toolchain can build it; much smaller ecosystem than C++.

## Maintenance

Koka is actively developed at Microsoft Research (v3.2.9 released 2026-09-17, 4.1k stars, Apache-2.0) but calls itself a research language not ready for production. This is a 2020 first-party result against a C++ port the authors call a performance baseline that copies without freeing, so read 3.33x as evidence for Perceus reuse, not as a Koka-versus-C++ speed ratio.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** Upgraded C to B: the same Figure 9 (cfold time C++ 3.33, peak working set C++ 2.94, relative to Koka 1.00) is in the Perceus paper (MSR-TR-2020-42 v4, the extended version of the peer-reviewed PLDI 2021 paper, opened), with gcc 9.3.0 and AMD 3600XT stated. Not A: compile flags are not stated with the results (only derivable from CMake's Release default and the v2.0.3 Koka compiler source), and the run is first-party on code since revised.
- **Retiered** B to C: Downgraded from B to C: unequal work in the C++ baseline. The C++ reassoc copies the whole left spine at every Add (about 20 x 2^19 = 10.5M extra nodes, never freed) while optimised Koka rewrites the same uniquely owned cells in place, the C++ const_folding inspects only the root and its eval walks the unfolded 2^20-element list, so the phases are not one-to-one and the 3.33x mostly measures copy-without-free against in-place reuse (SHOGUN unequal-work precedent).
- **Verifier notes:** Numbers verified on the README chart and the Perceus TR figure; same chart, so cfold 3.33x time and 2.94x RSS are correct. Shortcomings to record: C++ baseline leaks every node and its const_folding is non-recursive (different algorithm, same_algorithm false), Koka links mimalloc versus glibc malloc on the C++ side (part of the win belongs to mimalloc, check against the listed mimalloc entry), authors disclaim it as an absolute speed comparison, 2020 Koka 2.0.3 numbers, C++ wins rbtree and nqueens. License Apache-2.0 (LICENSE), 4.1k stars, last commit 2026-10-01 on dev, active.
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
  - <https://raw.githubusercontent.com/koka-lang/koka/HEAD/test/bench/cpp/cfold.cpp>
  - <https://raw.githubusercontent.com/koka-lang/koka/v2.0.3/test/bench/cpp/cfold.cpp>
  - <https://raw.githubusercontent.com/koka-lang/koka/HEAD/test/bench/koka/cfold.kk>
  - <https://raw.githubusercontent.com/koka-lang/koka/v2.0.3/test/bench/koka/cfold.kk>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/koka-lang/koka/HEAD/readme.md>
  - <https://github.com/koka-lang/koka>
  - <https://microsoft.com/en-us/research/uploads/prod/2020/11/perceus-tr-v4.pdf>
  - <https://github.com/koka-lang/koka/tree/v2.0.3/test/bench>
  - <https://raw.githubusercontent.com/koka-lang/koka/v2.0.3/test/bench/run.kk>
  - <https://raw.githubusercontent.com/koka-lang/koka/v2.0.3/test/bench/README.md>
  - <https://raw.githubusercontent.com/koka-lang/koka/HEAD/test/bench/README.md>
  - <https://raw.githubusercontent.com/koka-lang/koka/v2.0.3/test/bench/cpp/cfold.cpp>
  - <https://raw.githubusercontent.com/koka-lang/koka/HEAD/test/bench/cpp/cfold.cpp>
  - <https://raw.githubusercontent.com/koka-lang/koka/v2.0.3/test/bench/koka/cfold.kk>
  - <https://raw.githubusercontent.com/koka-lang/koka/HEAD/test/bench/koka/cfold.kk>
  - <https://raw.githubusercontent.com/koka-lang/koka/v2.0.3/test/bench/CMakeLists.txt>
  - <https://raw.githubusercontent.com/koka-lang/koka/HEAD/test/bench/CMakeLists.txt>
  - <https://raw.githubusercontent.com/koka-lang/koka/v2.0.3/test/bench/cpp/CMakeLists.txt>
  - <https://raw.githubusercontent.com/koka-lang/koka/HEAD/test/bench/cpp/CMakeLists.txt>
  - <https://raw.githubusercontent.com/koka-lang/koka/v2.0.3/test/bench/koka/CMakeLists.txt>
  - <https://raw.githubusercontent.com/koka-lang/koka/HEAD/test/bench/koka/CMakeLists.txt>
  - <https://github.com/koka-lang/koka/issues?q=is%3Aissue+benchmark>
  - <https://github.com/koka-lang/koka/issues?q=is%3Aissue+%22stack+overflow%22>
  - <https://github.com/koka-lang/koka/issues?q=is%3Aissue+label%3Aruntime-performance>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:koka/koka-lang/koka#cfold`) · [data/wave14/enrich/raw/lang_koka_koka_lang_koka_cfold.json](../../../data/wave14/enrich/raw/lang_koka_koka_lang_koka_cfold.json) (enrichment confidence 0.7)

</details>
