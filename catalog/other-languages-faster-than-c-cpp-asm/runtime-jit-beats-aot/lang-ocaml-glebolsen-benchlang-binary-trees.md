# OCaml 5.4.1: benchLANG binary trees vs C and C++ at -O3

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Runtime JIT beats ahead-of-time](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `OCaml` · `MIT` · 🟢 active

> Non-flambda ocamlopt (OCaml 5.4.1) running benchLANG binary trees 14% faster than per-node malloc/free C and 25% faster than new/delete C++.

| | |
|---|---|
| **Beats** | C (GCC 16.2.0: gcc -O3 -march=native -flto -funroll-loops -ffp-contract=off) and C++ (g++ -std=c++20 with the same flags) binary-trees programs that allocate every node with malloc/free (C) or new/delete (C++) |
| **Claimed result** | OCaml 5.4.1 0.865 s vs C 1.010 s and C++ 1.147 s: about 1.17x faster than C and 1.33x faster than C++ (derived from page data). |
| **Workload** | CLBG-style binary trees, depths 4 to 18: allocate, traverse and (in native code) free complete binary trees of individually allocated nodes; the README says the workload measures allocator plus GC plus pointer chasing, with native frees inside the timer and GC runtimes collecting when they like. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 5900X locked at 3.5 GHz (cpupower performance governor, min and max 3500 MHz), 48 GB DDR4-3600 CL16, Arch Linux |
| **Compiler and flags** | C: gcc 16.2.0 -O3 -march=native -flto -funroll-loops -ffp-contract=off -s; C++: g++ 16.2.0 -std=c++20 with the same flags (nixpkgs-unstable pins, run_benchmarks.sh). OCaml 5.4.1: ocamlopt -O3 -unsafe -inline 200 -nodynlink monotonic.c bench.ml -o bench -ccopt -s. flake.nix installs the plain nixpkgs `ocaml` package, and nixpkgs' pkgs/development/compilers/ocaml/generic.nix defaults flambdaSupport to false, so -O3 has no effect and the OCaml side is a non-flambda (closure-mode) build. |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | yes |
| **Why it wins** | Source (README workload note): native code frees every node inside the timed region while GC runtimes collect when they like. Likely mechanism (inference): bump-pointer allocation in the runtime and deferred or concurrent reclamation against glibc malloc and free per node. |
| **Adoption** | 8 stars |
| **Last commit** | 2026-09-03 |
| **Links** | [repository](https://github.com/GlebOlsen/benchLANG) · [benchmark](https://raw.githubusercontent.com/GlebOlsen/benchLANG/main/README.md) |

## Verdict

benchLANG's 3 September 2026 run on a Ryzen 9 5900X locked at 3.5 GHz (Arch Linux, 48 GB DDR4-3600) timed binary trees at 0.865 s for OCaml 5.4.1 (ocamlopt, non-flambda, default GC) against 1.010 s for C and 1.147 s for C++, both built by GCC 16.2.0 with -O3 -march=native -flto -funroll-loops and allocating each node with malloc/free or new/delete; about 1.17x and 1.33x faster (derived from page data), one run each, with the analyzer checking that every language printed the same checksum.

## Use it when

- You already write OCaml (compilers, provers, symbolic tools) and wonder whether a pass that builds many short-lived immutable tree nodes should move to C: with default GC settings the native OCaml binary beat naive malloc/free C here.
- Workloads that allocate whole trees or ASTs and drop them before the next minor collection, which is the case the generational minor heap makes nearly free.
- You want a single native executable (1039 KiB stripped here) with GC-speed allocation and no JIT warm-up or separate VM install, unlike the Java, C# and Bun rows of the same table.
- As a data point that per-node malloc/free, not the language, is the bottleneck of a naive C or C++ tree builder.

## Skip it when

- As evidence that OCaml beats tuned C or C++: benchLANG has no arena or pool variant, and a per-tree bump arena or std::pmr::monotonic_buffer_resource would remove both the per-node frees and the second traversal (inference, not measured here). Benchmarks Game search snippets (pages not opened, different runs and multicore programs, directional only) list gcc #2 with APR pools at 1.56 s against an OCaml 5.2.0\~alpha1 program at 3.41 s.
- Compute-bound or recursion-heavy code: the same OCaml program loses Fibonacci(45) (4.897 s vs 1.694 s for C), strings (5.000 s vs 2.132 s), primes (3.200 s vs 2.725 s) and Mandelbrot (2.271 s vs 2.201 s), and the suite overall (16.233 s vs 9.762 s, 1.66x slower).
- Memory-constrained deployments: whole-process peak RSS was 89.7 MiB for OCaml against 33.3 MiB for C and 35.4 MiB for C++.
- Workloads whose trees outlive the minor heap: here the depth-16 and depth-18 short-lived trees (4 and 16 MiB), the stretch tree (32 MiB) and the long-lived tree (16 MiB), about 18.3M of 68.3M nodes (27%), are too big for the default 2 MiB minor heap and must be promoted and later swept by the major GC (derived from the source and runtime defaults); programs with large live data pay more of that cost.
- If you just want the biggest allocation-throughput win from a GC runtime: in the same table Java (0.347 s), Nim (0.809 s) and Bun (0.816 s) beat OCaml, and Dart AOT ties it at 0.865 s.

## How it is fast

Memory management, not code generation; there is no JIT, ocamlopt is an AOT compiler. Likely mechanism (inference, consistent with the README's 'GC runtimes collect when they like'): each Node is a 4-word block (header plus three fields, 32 bytes, the same as glibc's chunk for the C program's 24-byte struct) bumped out of the minor heap, and a minor collection copies only live blocks, so short-lived trees of depth 14 or less (at most 1 MiB, below the default 256k-word or 2 MiB minor heap, Minor_heap_def 262144 in OCaml 5.4.1's runtime/caml/config.h) are never traced or freed one by one. The C and C++ programs call malloc or operator new per node and then walk every tree again (free_tree) to free or delete each node inside the timer. Per node that is about 12.7 ns for OCaml against 14.8 ns for C and 16.8 ns for C++ (derived from page data over 68.3M nodes).

## Compared with alternatives

Among the catalogued benchLANG binary-trees rows OCaml (0.865 s) sits between Bun (0.816 s) and C# (0.931 s) and well behind Java (0.347 s); pick it when you want an AOT native binary with no JIT or VM and a single-threaded GC, and pick the Java or Bun rows (or LangArena's Java and Bun Binarytrees::Obj entries, which also include stronger C++ baselines) when the size of the margin matters.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | OCaml 5.4.1 from nixpkgs-unstable (the plain `ocaml` attribute, i.e. ocamlPackages_5_4, at the flake.lock rev e8be7818) and a C compiler for the monotonic.c clock stub; no opam packages |
| **Minimum toolchain** | OCaml 5.4.1 as measured; bench.ml uses only the Stdlib and one external C stub, so other OCaml releases should compile it, but only 5.4.1 (non-flambda) was measured |
| **Platforms** | Measured on x86-64 Linux only (flake.nix sets system = x86_64-linux), Ryzen 9 5900X locked at 3.5 GHz |
| **Thread safety** | Not applicable: single-threaded workload on one OCaml 5 domain |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness asymmetry behind the margin: C and C++ free every node in a second traversal inside the timer, while OCaml stops its timer with the 16 MiB long-lived tree and all promoted garbage from the depth-16, depth-18 and stretch trees still uncollected in the major heap, and the process exits without a final collection. The README states this design ('native code frees inside the timer'), so the row compares allocation strategies, not code generation.
- The documented -O3 does nothing: at the pinned nixpkgs rev (flake.lock e8be7818) pkgs/development/compilers/ocaml/generic.nix defaults flambdaSupport to false and top-level ocamlPackages is ocamlPackages_5_4, and in OCaml 5.4.1's driver/main_args.ml -O3 only sets Flambda simplify rounds and inlining arguments. -inline 200 does still raise the Closure-mode inlining threshold (middle_end/closure/closure.ml), so the OCaml row is a plain closure-mode build with bigger inlining, not an optimised Flambda build.
- Small, noisy margin from one run: OCaml's 0.865 s is 14% under C's 1.010 s, while the native malloc-based rows running the identical algorithm already spread from 0.986 s (Fortran) to 1.147 s (C++), 16%. run_benchmarks.sh supports --runs N, but the published table is one run, and the raw benchmark_results_\*.txt file (with the CPUx column) is not committed (.gitignore ignores everything not re-included, and .txt is not).
- Results depend on default GC parameters (2 MiB minor heap, space_overhead 120 per Percent_free_def in config.h); setting a larger minor heap through OCAMLRUNPARAM would keep the 4 MiB depth-16 trees young and likely help this workload, while a smaller one would promote more (inference, not measured). Binary trees runs last in the process, after four workloads that leave little on the heap. Checksums use OCaml's 63-bit int against C's long long; the analyzer exits with an error on any checksum mismatch, and the values here stay far below 2^62.

## Known shortcomings

- One run (0.865 vs 1.010 s); the win is allocator plus GC since C frees in a recursive pass inside the timer; ocamlopt is AOT so the runtime-jit-beats-aot category is loose; the nixpkgs ocaml is built without flambda so -O3 does nothing.
- Harness asymmetry behind the 14% margin: C and C++ free every node in a second traversal inside the timer, while OCaml stops its timer with the 16 MiB long-lived tree plus all promoted major-heap garbage uncollected and exits without a final collection (the README states this design). The documented -O3 is a no-op at the pinned flake.lock rev e8be7818 (flambdaSupport false, ocamlPackages 5_4; main_args.ml _o3 sets Flambda parameters only), -inline 200 is still active, and the default 2 MiB minor heap holds trees only up to depth 14, so 18.3M of 68.3M nodes (27%) are promoted. One run, inside the native-row spread of 0.986-1.147 s. No correctness bug. Retiered to C.

## Caveats and trade-offs

One run per language (no variance) from a single machine on 2026-09-03. The C and C++ programs allocate every node with malloc/new and walk every tree a second time to free it inside the timer (languages/C/bench.c make_tree/free_tree), while OCaml just drops the references and its minor GC never traces dead young trees; an arena or pool allocator in C would likely beat the runtimes here. The column is an allocator benchmark, not a codegen one: the malloc-based native rows spread from 0.986 s (Fortran) through 1.010 s (C), 1.033 s (Rust), 1.109 s (Ada) and 1.119 s (Zig) to 1.147 s (C++), and Java 0.347 s, Nim 0.809 s, Bun 0.816 s, Dart AOT 0.865 s and C# 0.931 s also beat C. ocamlopt is an ahead-of-time compiler, so the win comes from the OCaml GC runtime, not from a JIT. Binary trees is 1 of 5 workloads and C wins overall (total 9.762 s vs OCaml 16.233 s); OCaml loses primes (3.200 s vs 2.725 s), Fibonacci (4.897 s vs 1.694 s), strings (5.000 s vs 2.132 s) and Mandelbrot (2.271 s vs 2.201 s). OCaml peak RSS 89.7 MiB vs 33.3 MiB for C. OCaml uses 63-bit tagged ints where C uses long long; the analyzer checks that checksums agree. The -O3 flag is ignored because the nixpkgs OCaml is built without flambda. [retier] Enricher: harness asymmetry; C and C++ free every node in a second traversal inside the timer, while OCaml stops its timer with the 16 MiB long-lived tree plus all promoted major-heap garbage uncollected and exits without a final collection (the README states this design). The documented -O3 is a no-op at the pinned flake.lock rev e8be7818 (flambdaSupport false, ocamlPackages 5_4; main_args.ml _o3 sets Flambda parameters only), -inline 200 is still active, and the default 2 MiB minor heap holds trees only up to depth 14, so 18.3M of 68.3M nodes (27%) are promoted. One run, inside the native-row spread of 0.986-1.147 s; no correctness bug.

Whole-process peak RSS 89.7 MiB for OCaml vs 33.3 MiB for C; OCaml is slower than C on primes (3.200 s vs 2.725 s), Fibonacci (4.897 s vs 1.694 s) and strings (5.000 s vs 2.132 s).

## Maintenance

Small single-author MIT repo (8 stars, 0 forks, 42 commits, last commit 2026-09-03) with Nix-pinned toolchains and a committed flake.lock, so anyone can rerun it, but this is one run of one micro-workload, not something to adopt as a library.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now C.
- **Tier reason:** The README results table (3 September 2026, one run) gives Binary Trees 0.865 s for OCaml 5.4.1 against 1.010 s for C and 1.147 s for C++ (GCC 16.2.0). Code for every side is public (languages/C/bench.c, languages/C++/bench.cpp, languages/OCaml/bench.ml with monotonic.c, run_benchmarks.sh), with Nix-pinned toolchains, exact build commands and the CPU (Ryzen 9 5900X locked at 3.5 GHz), so it meets A.
- **Retiered** A to C: Downgraded from A to C: asymmetric harness. C and C++ free every node in a second traversal inside the timer while OCaml stops its timer with the long-lived tree and all promoted major-heap garbage uncollected and exits without a final collection, so part of the 14% margin is deallocation work charged to the baselines only; the documented -O3 is a no-op at the pinned toolchain and the one-run margin sits inside the native-row spread.
- **Verifier notes:** Numbers and the derived ratios (1.17x over C, 1.33x over C++) match the README; same tree build/check algorithm on all sides, C/C++ at -O3 with -march=native and LTO, so the baseline is not crippled and A stands. Main shortcomings: one run, a modest margin, C/C++ pay an explicit free traversal inside the timer, the win is GC bump allocation against glibc malloc/free (Java, Nim, Bun, Dart and C# also beat C), OCaml is AOT so the runtime-jit-beats-aot category is loose, and -O3 is a no-op without flambda. Sibling ids for the same table: lang:csharp (batch 53), lang:javascript (batch 56), lang:java (this batch).
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
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
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/main/languages/OCaml/bench.ml>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/main/languages/OCaml/monotonic.c>
  - <https://raw.githubusercontent.com/NixOS/nixpkgs/nixpkgs-unstable/pkgs/development/compilers/ocaml/generic.nix>
- **Sources the enricher read:**
  - <https://github.com/GlebOlsen/benchLANG>
  - <https://github.com/GlebOlsen/benchLANG/commits/main>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/main/README.md>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/main/languages/OCaml/bench.ml>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/main/languages/OCaml/monotonic.c>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/main/languages/C/bench.c>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/main/languages/C%2B%2B/bench.cpp>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/main/run_benchmarks.sh>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/main/analyze_results.sh>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/main/flake.nix>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/main/flake.lock>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/main/.gitignore>
  - <https://raw.githubusercontent.com/NixOS/nixpkgs/e8be7818e19ada32105a8af937a6a473b38167ca/pkgs/development/compilers/ocaml/generic.nix>
  - <https://raw.githubusercontent.com/NixOS/nixpkgs/e8be7818e19ada32105a8af937a6a473b38167ca/pkgs/development/compilers/ocaml/5.4.nix>
  - <https://raw.githubusercontent.com/NixOS/nixpkgs/e8be7818e19ada32105a8af937a6a473b38167ca/pkgs/top-level/ocaml-packages.nix>
  - <https://raw.githubusercontent.com/ocaml/ocaml/5.4.1/driver/main_args.ml>
  - <https://raw.githubusercontent.com/ocaml/ocaml/5.4.1/middle_end/closure/closure.ml>
  - <https://raw.githubusercontent.com/ocaml/ocaml/5.4.1/runtime/caml/config.h>
  - WebSearch: benchmarks game binary-trees OCaml vs C gcc apr pools (snippets only; benchmarksgame-team.pages.debian.net did not resolve here)
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:ocaml/glebolsen/benchlang#binary-trees`) · [data/wave14/enrich/raw/lang_ocaml_glebolsen_benchlang_binary_trees.json](../../../data/wave14/enrich/raw/lang_ocaml_glebolsen_benchlang_binary_trees.json) (enrichment confidence 0.75)

</details>
