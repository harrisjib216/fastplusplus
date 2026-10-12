# Bun (JavaScriptCore JIT 1.3.13): benchLANG binary trees

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Runtime JIT beats ahead-of-time](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `JavaScript` · `MIT` · 🟢 active

> Plain JavaScript on Bun 1.3.13 runs benchLANG binary trees 1.24x faster than per-node malloc/free C at -O3.

| | |
|---|---|
| **Beats** | C (GCC 16.2.0, malloc and free per node, 1.010 s) and C++ (GCC 16.2.0, new and delete per node, 1.147 s) |
| **Claimed result** | JS (Bun) 0.816 s vs C 1.010 s and C++ 1.147 s: about 1.24x faster than C and 1.41x faster than C++ (derived from page data). JS (Node v26.8.1) is slower at 1.444 s. Peak RSS 336.1 MiB for Bun vs 33.3 MiB for C. |
| **Workload** | CLBG-style binary trees in one process after four other workloads: a stretch tree of depth 19, a long-lived tree of depth 18, then 2^(22-d) short-lived trees for each even depth d from 4 to 18, each built and checked; C and C++ free every tree with a recursive free pass (malloc/free or new/delete per node) inside the timer, the JS version just drops the references (no free pass). |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 5900X locked at 3.5 GHz (performance governor), 48 GB DDR4-3600 CL16, Arch Linux with i3-wm; results dated 3 September 2026, one run per language |
| **Compiler and flags** | C: gcc -O3 -march=native -flto -funroll-loops -ffp-contract=off -s (GCC 16.2.0); C++: g++ -std=c++20 with the same flags. JS (Bun) 1.3.13: bun run directly, JIT default (no flags). |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | yes |
| **Why it wins** | Stated by the suite's methodology: 'Binary trees: ... Allocator + GC + pointer chase, native code frees inside the timer, GC runtimes collect when they like'. Agent inference: per-node malloc/free (C, C++) against bump-pointer allocation and deferred or concurrent collection in a managed runtime; the C/C++ programs do not use an arena. |
| **Adoption** | 8 stars |
| **Last commit** | 2026-09-03 |
| **Links** | [repository](https://github.com/GlebOlsen/benchLANG) · [benchmark](https://raw.githubusercontent.com/GlebOlsen/benchLANG/main/README.md) |

## Verdict

benchLANG's 3 September 2026 run on a Ryzen 9 5900X locked at 3.5 GHz (Arch Linux, i3-wm, 48 GB DDR4-3600) timed binary trees at 0.816 s for bench.js on Bun 1.3.13 (default JIT) against 1.010 s for C and 1.147 s for C++, both built with GCC 16.2.0 -O3 -march=native -flto -funroll-loops -ffp-contract=off and allocating each node with malloc/free or new/delete; that is about 1.24x faster than C and 1.41x faster than C++ (derived from page data). Times are in-program monotonic-clock wall times from one run, with JIT warm-up inside the timed region.

## Use it when

- You ship a Bun service and wonder whether to move an allocation-heavy tree or graph builder into a native addon: with per-node malloc/free on the native side, Bun already wins on this shape.
- Workloads that create many small, same-shaped, short-lived objects and drop them wholesale (parse trees, temporary graphs, per-request object churn).
- Throughput or batch jobs on a multi-core machine where spare cores can absorb concurrent GC marking and peak memory is cheap.
- As a data point that per-node glibc malloc/free, not the language, is the bottleneck in a naive C or C++ tree builder.

## Skip it when

- As evidence that JavaScript beats tuned C or C++: an arena or pool (std::pmr::monotonic_buffer_resource, a per-tree bump allocator) removes both the per-node free calls and the second traversal; benchLANG has no arena variant, so that comparison is untested here (inference).
- Memory-constrained deployments: whole-process peak RSS was 336.1 MiB for Bun against 33.3 MiB for C (about 10x).
- On Node.js: the same bench.js takes 1.444 s on Node v26.8.1, 1.43x slower than C, so the win is specific to Bun's JavaScriptCore and does not generalise to JavaScript.
- Compute-bound code: Bun loses every other benchLANG column to C (Fibonacci(45) 7.735 s vs 1.694 s, strings 3.129 s vs 2.132 s) and the suite overall (16.732 s vs 9.762 s).
- If you need the largest managed-runtime gain on allocation churn: Java (0.347 s) and Nim (0.809 s) are faster in the same table, and Bun's margin over C is about 24% from one run.

## How it is fast

Memory management, not code generation, decides this column. JavaScriptCore's Riptide collector is non-moving and generational through sticky mark bits: eden collections visit only new objects plus write-barrier-remembered ones, and most marking runs concurrently and in parallel on up to eight logical CPUs (WebKit's Riptide description, read as search snippets). Dropping a tree therefore costs the JS program nothing at the drop site, while the C and C++ programs call malloc or operator new per node and then walk every tree a second time (free_tree) to free or delete each node inside the timer. That works out to about 11.9 ns per node for Bun against 14.8 ns for C and 16.8 ns for C++ (derived from page data over 68,332,206 nodes).

## Compared with alternatives

Among benchLANG's binary-trees rows Bun (0.816 s) beats C# (0.931 s) and OCaml (0.865 s) but is more than twice as slow as Java (0.347 s), so cite it only when the question is specifically Bun or JavaScript; the LangArena Binarytrees::Obj entry shows Bun about 2x ahead of make_unique C++ and the alya-lang entry about 1.28x ahead of -O2 C with a median of 10 runs, which is better-repeated evidence for the same effect.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | Bun 1.3.13 from nixpkgs-unstable (flake.lock pins nixpkgs rev e8be7818, dated 2026-08-29); no npm packages |
| **Minimum toolchain** | Bun 1.3.13 as measured; the script is plain ES2015+ (performance.now, template literals) and also runs on Node |
| **Platforms** | Measured on x86-64 Linux only (flake.nix pins x86_64-linux); Bun on other platforms not tested here |
| **Thread safety** | Not applicable: single-threaded program; JavaScriptCore uses extra threads for concurrent GC marking and JIT compilation |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness asymmetry by design: C and C++ run free_tree inside the timer (a second full traversal plus 68.3M free or delete calls), while bench.js only drops references, and garbage left at the end of the timed function is never collected inside the timer. The README states this ('native code frees inside the timer, GC runtimes collect when they like'); the free pass's share of C's 1.010 s is not measured.
- Single-core versus multi-core: the C program runs on one core, but Riptide marks concurrently on helper threads of the 12-core Ryzen 9 5900X, so wall time hides GC CPU. The runner records CPUx = (user+sys)/wall per language, but the README table omits it and .gitignore keeps the benchmark_results_\*.txt files out of the repo, so Bun's whole-process CPU time is unpublished.
- One run per language (3 September 2026); run_benchmarks.sh supports --runs N averaging, but the table does not use it, and Bun's 0.194 s margin over C is not much larger than the 0.137 s gap between the near-identical C (malloc/free) and C++ (new/delete) programs.
- No correctness problem found: bench.js does the same depth schedule and item arithmetic as bench.c (values stay far below 2^53), and analyze_results.sh exits non-zero and marks the ranking invalid if any language's checksum differs.

## Known shortcomings

- One run per language; the GC partly runs after the timer stops while C and C++ free every node inside it, so the win is glibc malloc/free per node, not codegen (Java 0.347 s, Nim 0.809 s, C# 0.931 s and Fortran 0.986 s also beat C's 1.010 s).
- No code bug (bench.js matches bench.c's work and a checksum check exists). Harness asymmetry: the C and C++ free_tree pass runs inside the timer while JS drops references and the garbage left at the end of the timer is never collected inside it; Riptide marks concurrently on helper cores while C is single-core. CPUx is computed but absent from the README table and the results .txt files are gitignored, so Bun's CPU time is unpublished. One run; Bun's margin of 0.194 s is comparable to the 0.137 s C/C++ gap. Node on the same file takes 1.444 s, slower than C.

## Caveats and trade-offs

One run per language ('1 run/lang'), no variance. In-program wall times from a monotonic clock: JIT warm-up is inside the managed runtimes' timed region, but their garbage collection can run partly after the timer stops ('GC runtimes collect when they like'), while C/C++ pay an extra recursive free traversal inside the timer. The column is an allocator benchmark, not a codegen one: Java 0.347 s, Nim 0.809 s, Dart AOT 0.865 s, OCaml 0.865 s, C# 0.931 s and Fortran 0.986 s also beat C's 1.010 s, so per-node glibc malloc/free is the bottleneck and an arena or pool allocator in C/C++ would likely beat every managed runtime (compare the Arena variant in LangArena, where C wins by about 6x). Only the binary-trees column is a Bun win: on primes, fib, strings and mandelbrot Bun loses to C (total 16.732 s vs 9.762 s). Bun's peak RSS is 336.1 MiB vs 33.3 MiB for C. Bun's win is modest (about 1.24x) and rests on one run; Node v26.8.1 is slower than C (1.444 s). The earlier caveat about an 'Updated May 2026' header no longer applies: the current README says results are from September 2026. [retier] The C and C++ free_tree pass runs inside the timer while JS drops references and the garbage left at the end of the timer is never collected inside it; Riptide marks concurrently on helper cores while C is single-core. CPUx is computed but absent from the README table and the results .txt files are gitignored. One run; Bun's margin of 0.194 s is comparable to the 0.137 s C/C++ gap; Node on the same file takes 1.444 s, slower than C.

10x the peak memory of C; other columns are much slower than C (fib 7.735 s vs 1.694 s).

## Maintenance

Small single-author MIT repo (8 stars, 0 forks, 42 commits, no issues; results and code last updated 2026-09-03) with Nix-pinned toolchains and a checksum check, easy to rerun, but the result is one run of one micro-workload and a statement about allocators rather than something to adopt.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** README results table (3 September 2026) shows Binary Trees C 1.010 s, C++ 1.147 s, JS (Bun 1.3.13) 0.816 s on a Ryzen 9 5900X locked at 3.5 GHz; benchmark code is public (languages/C/bench.c, languages/C++/bench.cpp, languages/JS/bench.js, run_benchmarks.sh) and GCC 16.2.0 with -O3 -march=native -flto -funroll-loops -ffp-contract=off is stated for both C and C++.
- **Verifier notes:** Numbers and ratios check out against the README table; C, C++ and JS sources implement the same tree build/check with one allocation per node, and C/C++ are at -O3 with -march=native and LTO, so the baseline is not crippled. Main shortcomings: one run per language, GC partly outside the timer while C/C++ free inside it, and the win reflects glibc malloc/free per node rather than JavaScriptCore codegen (Java, Nim, C#, Dart, OCaml and Fortran also beat C on this column).
- **Fields the verifier corrected:** `baseline_stdlib`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-56 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/main/README.md>
  - <https://github.com/GlebOlsen/benchLANG>
  - <https://github.com/GlebOlsen/benchLANG/commits>
  - <https://github.com/GlebOlsen/benchLANG/tree/main/languages>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/main/languages/C/bench.c>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/main/languages/C++/bench.cpp>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/main/languages/JS/bench.js>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/main/run_benchmarks.sh>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/main/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/GlebOlsen/benchLANG>
  - <https://github.com/GlebOlsen/benchLANG/commits/main>
  - <https://github.com/GlebOlsen/benchLANG/commits/main/languages/JS/bench.js>
  - <https://github.com/GlebOlsen/benchLANG/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/main/README.md>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/main/languages/JS/bench.js>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/main/languages/C/bench.c>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/main/languages/C++/bench.cpp>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/main/run_benchmarks.sh>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/main/analyze_results.sh>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/main/clean.sh>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/main/flake.nix>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/main/flake.lock>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/main/.gitignore>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/main/CITATION.cff>
  - WebSearch: WebKit Riptide garbage collector (snippets from webkit.org/blog/7122 and the WebKit 'Marking should be generational' commit; pages not opened)
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:javascript/glebolsen/benchlang#binary-trees`) · [data/wave14/enrich/raw/lang_javascript_glebolsen_benchlang_binary_trees.json](../../../data/wave14/enrich/raw/lang_javascript_glebolsen_benchlang_binary_trees.json) (enrichment confidence 0.75)

</details>
