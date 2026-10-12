# .NET 11 preview JIT (C#): benchLANG binary trees vs C and C++ at -O3

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Runtime JIT beats ahead-of-time](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C#` · `MIT` · 🟢 active

> Default-settings .NET 11 preview JIT running C# binary trees 8% faster than per-node malloc/free C and 23% faster than new/delete C++ at -O3.

| | |
|---|---|
| **Beats** | C (GCC 16.2.0: gcc -O3 -march=native -flto -funroll-loops -ffp-contract=off) and C++ (g++ -std=c++20 with the same flags) binary-trees programs that allocate every node with malloc/free (C) or new/delete (C++) |
| **Claimed result** | C# (.NET SDK 11.0.100-preview.7) 0.931 s vs C 1.010 s and C++ 1.147 s: about 1.08x faster than C and 1.23x faster than C++ (derived from page data). |
| **Workload** | CLBG-style binary trees, depths 4 to 18: allocate, traverse and (in native code) free complete binary trees of individually allocated nodes; the README says the workload measures allocator plus GC plus pointer chasing, with native frees inside the timer and GC runtimes collecting when they like. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 5900X locked at 3.5 GHz (cpupower performance governor, min and max 3500 MHz), 48 GB DDR4-3600 CL16, Arch Linux |
| **Compiler and flags** | C: gcc 16.2.0 -O3 -march=native -flto -funroll-loops -ffp-contract=off -s; C++: g++ 16.2.0 -std=c++20 with the same flags (nixpkgs-unstable pins, run_benchmarks.sh). C#: .NET SDK 11.0.100-preview.7, built as a file-based app with dotnet build -c Release -o out Program.cs (no .csproj in the repo) and run as dotnet out/Program.dll (default tiered JIT and default GC, no Native AOT). |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | yes |
| **Why it wins** | Source (README workload note): native code frees every node inside the timed region while GC runtimes collect when they like. Likely mechanism (inference): bump-pointer allocation in the runtime and deferred or concurrent reclamation against glibc malloc and free per node. |
| **Adoption** | 8 stars |
| **Last commit** | 2026-09-03 |
| **Links** | [repository](https://github.com/GlebOlsen/benchLANG) · [benchmark](https://raw.githubusercontent.com/GlebOlsen/benchLANG/main/README.md) |

## Verdict

benchLANG's 3 September 2026 run on a Ryzen 9 5900X locked at 3.5 GHz (Arch Linux, 48 GB DDR4-3600) timed binary trees at 0.931 s for C# on .NET SDK 11.0.100-preview.7 (default JIT and GC) against 1.010 s for C and 1.147 s for C++, both built by GCC 16.2.0 with -O3 -march=native -flto -funroll-loops and allocating each node with malloc/free or new/delete. That makes C# about 1.08x faster than C and 1.23x faster than C++ (derived from page data); the runner's analyzer checks that every language printed the same checksum.

## Use it when

- You already ship .NET and wonder whether to move an allocation-heavy tree or graph builder to native code: on this workload the default JIT and GC already match or beat naive malloc/free C.
- Workloads that create many small short-lived objects (parse trees, temporary graphs) and drop them all at once, the pattern generational GCs handle best.
- Batch or throughput jobs where whole-process wall time matters more than pause times or memory footprint.
- As a data point when arguing that per-node malloc/free, not the language, is the bottleneck in a C or C++ tree builder.

## Skip it when

- As evidence that .NET beats tuned C++: a per-tree arena such as std::pmr::monotonic_buffer_resource or a pool allocator would remove both the per-node frees and the second traversal; benchLANG has no arena version (inference, not measured).
- Memory-constrained deployments: whole-process peak RSS was 122.1 MiB for C# against 33.3 MiB for C, and the .NET runtime ships outside the reported binary size.
- If the C# margin matters to you: it is 8% from one run, inside the 0.986-1.147 s spread of the native malloc-based rows (Fortran, C, Rust, Ada, Zig, C++) for the same algorithm.
- If you are picking a managed runtime for allocation throughput: in the same table Java (OpenJDK 25, 0.347 s), Nim (0.809 s), Bun (0.816 s), OCaml and Dart (0.865 s) all beat C#.
- Code dominated by recursion or arithmetic: C# loses the suite overall (11.914 s vs C 9.762 s) and needs 3.793 s vs 1.694 s for C on Fibonacci(45).

## How it is fast

The gain comes from memory management, not code generation. Likely mechanism (inference, consistent with the README's note that GC runtimes 'collect when they like'): .NET hands out each node from a bump-pointer allocation context, and since each short-lived tree is dead by the next gen0 collection, the generational GC reclaims it without tracing it. The C and C++ programs instead call glibc malloc or operator new for every node, then walk every tree a second time (free_tree) to free or delete each node inside the timer. Per node that works out to about 13.6 ns for C# against 14.8 ns for C and 16.8 ns for C++ (derived from page data over 68.3M nodes), a small margin that JIT warm-up inside the timed region does not erase.

## Compared with alternatives

Among the catalogued benchLANG binary-trees rows, C# (0.931 s) is slower than Bun (0.816 s) and OCaml (0.865 s), so pick it only when you are already on .NET; if you want the biggest managed-runtime win on allocation churn, the same table's Java row (0.347 s) and LangArena's Bun Binarytrees::Obj entry show much larger margins over C and C++.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | .NET SDK 11.0.100-preview.7 from nixpkgs-unstable (dotnet-sdk_11 in flake.nix); no NuGet packages |
| **Minimum toolchain** | .NET SDK 11.0.100-preview.7 as measured; the repo has no .csproj, so the build relies on SDK support for file-based apps (dotnet build Program.cs) |
| **Platforms** | Measured on x86-64 Linux only (flake.nix pins x86_64-linux); other .NET platforms not tested here |
| **Thread safety** | Not applicable: single-threaded workload; the runtime may use extra GC and JIT threads |
| **Drop-in for the baseline** | no |

## Gotchas

- The C/C++ harness does more work than the C# one: free_tree walks every tree a second time and frees each node inside the timer, while the C# program just drops the root. That is by design ('native code frees inside the timer, GC runtimes collect when they like'), but it means the result compares allocation strategies rather than languages.
- Only Program.cs is versioned: the repo's .gitignore ignores every file by default, including project files and any runtimeconfig or Directory.Build.props, so the published numbers can only be assumed to use default runtime settings (tiered JIT, default GC). Microsoft's docs (search snippet only; the page was blocked here) say file-based apps default to PublishAot=true, but the runner uses dotnet build plus dotnet out/Program.dll, which runs on the JIT, not Native AOT.
- Single run per language on 2026-09-03 with a preview SDK, wall time from Stopwatch inside the program; run_benchmarks.sh supports --runs N averaging, but the README table does not use it.
- The C++ row (new/delete, 1.147 s) is 13% slower than the C row (malloc/free, 1.010 s) on identical logic, which shows how much of the gap comes from the allocator call path and run-to-run noise rather than the C# runtime.

## Known shortcomings

- One run; the 8% lead over C (0.931 vs 1.010 s) falls inside the 0.986-1.147 s spread of the malloc-based native rows (Fortran to C++); C frees every tree inside the timer; Java 0.347 s, Nim, Bun, OCaml and Dart also beat C, so the win is GC against glibc malloc/free, not JIT codegen.
- Allocator-strategy comparison: C and C++ free every node inside the timer via a second traversal while C# just drops the root; at 68.3M nodes that is 13.6 vs 14.8 ns per node (C), an 8% margin from one run inside the native 0.986-1.147 s spread. .gitignore hides any csproj or runtimeconfig, so the default GC and JIT are assumed. Java 0.347 s, Bun, OCaml, Nim and Dart all beat C#. No harness bug behind the numbers.

## Caveats and trade-offs

One run per language (no variance) from a single machine on 2026-09-03. The C and C++ programs are naive per-node malloc/free (new/delete in C++) and walk every tree a second time to free it inside the timer, while the .NET GC never traces dead trees; an arena or pool allocator in C would beat the runtimes here. The native malloc-based rows for the same algorithm already spread from 0.986 s (Fortran) through 1.010 s (C), 1.033 s (Rust), 1.109 s (Ada) and 1.119 s (Zig) to 1.147 s (C++), so the 8% C# margin over C lies inside the run-to-run and implementation spread of one algorithm; the 1.23x figure is against the slowest of those rows. Several runtimes beat C on this workload in the same table (Java 0.347 s, Nim 0.809 s, Bun 0.816 s, OCaml and Dart 0.865 s), which points at glibc per-node malloc/free rather than a .NET-specific code-generation win. The benchmark is 1 of 5 workloads, and C wins overall (total 9.762 s vs Java 13.536 s, C# 11.914 s, OCaml 16.233 s; C is faster than C# on Fibonacci 1.694 s vs 3.793 s, strings 2.132 s vs 2.235 s and Mandelbrot 2.201 s vs 2.229 s). Managed runtimes keep default settings with JIT warm-up inside the timed region and may use extra GC and JIT threads, so wall time is not CPU time; .NET 11 was a preview SDK. [retier] C and C++ free every node inside the timer via a second traversal while C# just drops the root; at 68.3M nodes that is 13.6 vs 14.8 ns per node (C), an 8% margin from one run inside the native 0.986-1.147 s spread. .gitignore hides any csproj or runtimeconfig, so the default GC and JIT are assumed. Java 0.347 s, Bun, OCaml, Nim and Dart all beat C#.

Whole-process peak RSS 122.1 MiB for C# vs 33.3 MiB for C; Fibonacci(45) takes 3.793 s vs 1.694 s for C.

## Maintenance

Small single-author MIT repo (8 stars, 42 commits, no issues, last commit 2026-09-03) with Nix-pinned toolchains, so anyone can rerun it, but the result is one run of one micro-workload, not something to adopt.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now C.
- **Tier reason:** The README results table (3 September 2026, one run) gives Binary Trees 0.931 s for C# (.NET 11.0.100-preview.7) against 1.010 s for C and 1.147 s for C++ (GCC 16.2.0). Code for both sides is public (languages/C/bench.c, languages/C++/bench.cpp, languages/C#/Bench/Program.cs, run_benchmarks.sh), with Nix-pinned compiler versions, exact flags and the CPU (Ryzen 9 5900X locked at 3.5 GHz), so it meets A.
- **Retiered** A to C: Enricher: C stands; C and C++ free every node inside the timer while C# drops the root, and the 8% margin from one run sits inside the native spread.
- **Verifier notes:** Numbers and the derived ratios (1.08x over C, 1.23x over C++) match the README; same source algorithm, release builds on both sides, so tier A stands, but the margin over C is small, from one run and within the 0.986-1.147 s spread of the malloc-based native rows, and the win comes from GC bump allocation against glibc malloc/free with explicit free traversal, not from JIT code generation. Sibling ids for the same table (lang:java, lang:ocaml, lang:javascript benchlang#binary-trees) are in batches 54 and 56.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-53 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/main/README.md>
  - <https://github.com/GlebOlsen/benchLANG>
  - <https://github.com/GlebOlsen/benchLANG/commits>
  - <https://github.com/GlebOlsen/benchLANG/tree/main/languages>
  - <https://github.com/GlebOlsen/benchLANG/tree/main/languages/C>
  - <https://github.com/GlebOlsen/benchLANG/tree/main/languages/C%23/Bench>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/main/languages/C/bench.c>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/main/languages/C++/bench.cpp>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/main/languages/C%23/Bench/Program.cs>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/main/run_benchmarks.sh>
- **Sources the enricher read:**
  - <https://github.com/GlebOlsen/benchLANG>
  - <https://github.com/GlebOlsen/benchLANG/commits/main>
  - <https://github.com/GlebOlsen/benchLANG/issues?q=is%3Aissue>
  - <https://github.com/GlebOlsen/benchLANG/tree/main/languages/C%23/Bench>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/main/README.md>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/main/run_benchmarks.sh>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/main/clean.sh>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/main/analyze_results.sh>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/main/flake.nix>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/main/.gitignore>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/main/languages/C/bench.c>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/main/languages/C++/bench.cpp>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/main/languages/C%23/Bench/Program.cs>
  - WebSearch: .NET file-based apps default MSBuild properties (snippets from learn.microsoft.com/en-us/dotnet/core/sdk/file-based-apps; the page itself was unreachable)
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:csharp/glebolsen/benchlang#binary-trees`) · [data/wave14/enrich/raw/lang_csharp_glebolsen_benchlang_binary_trees.json](../../../data/wave14/enrich/raw/lang_csharp_glebolsen_benchlang_binary_trees.json) (enrichment confidence 0.75)

</details>
