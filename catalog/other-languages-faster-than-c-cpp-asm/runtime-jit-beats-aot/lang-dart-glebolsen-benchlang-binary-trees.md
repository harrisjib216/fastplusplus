# Dart AOT 3.13.0: benchLANG binary trees vs C and C++ at -O3

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Runtime JIT beats ahead-of-time](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Dart` · `MIT` · 🟢 active

> Dart 3.13 AOT binary beats per-node malloc/free C by 1.17x on benchLANG binary trees; Dart source unpublished.

| | |
|---|---|
| **Beats** | C (GCC 16.2.0: gcc -O3 -march=native -flto -funroll-loops -ffp-contract=off) and C++ (g++ -std=c++20 with the same flags) binary-trees programs that allocate every node with malloc/free (C) or new/delete (C++) |
| **Claimed result** | README table of 3 September 2026, binary trees: Dart (3.13.0 AOT) 0.865 s vs C 1.010 s and C++ 1.147 s, about 1.17x faster than C and 1.33x faster than C++ (derived from page data). Dart loses overall: total 20.754 s against 9.762 s for C (2.13x slower), with Fibonacci 8.135 s vs 1.694 s and strings 6.523 s vs 2.132 s. |
| **Workload** | CLBG-style binary trees, depths 4 to 18: allocate, traverse and (in native code) free complete binary trees of individually allocated nodes; the README says the workload measures allocator plus GC plus pointer chasing, with native frees inside the timer and GC runtimes collecting when they like. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 5900X locked at 3.5 GHz (cpupower performance governor, min and max 3500 MHz), 48 GB DDR4-3600 CL16, Arch Linux with i3-wm, one run per language on 2026-09-03 |
| **Compiler and flags** | C: gcc 16.2.0 -O3 -march=native -flto -funroll-loops -ffp-contract=off -s; C++: g++ 16.2.0 -std=c++20 with the same flags (nixpkgs-unstable, flake.lock pinned). Dart: dart compile exe bench.dart -o bench -S bench.sym (AOT, runtime embedded; no optimization switches used). |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | not stated |
| **Same optimization level** | yes |
| **Why it wins** | Source (README workload note): native code frees every node inside the timed region while GC runtimes collect when they like. Likely mechanism (inference): bump allocation in the Dart young generation and cheap scavenges of short-lived trees against glibc malloc and free per node. |
| **Adoption** | 8 stars |
| **Last commit** | 2026-09-03 |
| **Links** | [repository](https://github.com/GlebOlsen/benchLANG) · [benchmark](https://raw.githubusercontent.com/GlebOlsen/benchLANG/HEAD/README.md) |

## Verdict

benchLANG's 3 September 2026 run (one run per language, Ryzen 9 5900X locked at 3.5 GHz, Arch Linux) timed binary trees at 0.865 s for Dart 3.13.0 AOT (dart compile exe, default VM GC settings) against 1.010 s for C (gcc 16.2.0 -O3 -march=native -flto -funroll-loops, malloc/free per node) and 1.147 s for C++ (g++ 16.2.0, new/delete). That is about 1.17x and 1.33x faster, or roughly 12.7 against 14.8 ns per node over 68.3 million nodes (derived from page data). The Dart program behind the number is not published.

## Use it when

- You already ship Dart (Flutter back ends, CLI tools) and wonder whether a pass that builds many short-lived tree nodes (ASTs, parse trees, immutable persistent structures) needs to move to C through FFI: with default VM settings the AOT binary beat naive malloc/free C on this workload.
- Allocation-heavy code whose objects die before the next young-generation scavenge, the case bump allocation and copying collection handle cheaply.
- As one data point when picking a garbage-collected AOT language: Dart's 0.865 s ties OCaml (0.865 s), is close to Bun (0.816 s) and Nim (0.809 s), and is well ahead of Go (1.796 s) and Node (1.444 s) on this row of the same table.

## Skip it when

- As evidence that Dart beats C in general: it lost the other four workloads and is 2.13x slower in total (20.754 s vs 9.762 s; Fibonacci 8.135 vs 1.694 s, strings 6.523 vs 2.132 s, primes 2.963 vs 2.725 s).
- Against C or C++ that allocates tree nodes from an arena, pool or bump allocator: the benchmark's C uses malloc/free per node by design, and the advantage is the allocator, not compiled-code quality.
- Memory- or size-constrained deployments: whole-process peak RSS was 74.6 MiB against 33.3 MiB for C, and the stripped executable 5617 KiB against 26 KiB, because the AOT binary embeds the Dart runtime.
- When you need reproducible evidence: the Dart program is not published, the table is one run per language, and the raw results file with checksums and CPU times is not committed.

## How it is fast

The win comes from the memory manager rather than Dart code generation: the Dart VM allocates by bumping a pointer in a semi-space young generation (up to 16 MB per semi-space on 64-bit by default in SDK 3.13.0) and reclaims dead trees with a copying scavenge whose cost scales with survivors, while C pays one malloc and one free call per node plus a second traversal to free. Old-generation marking and sweeping run concurrently on helper threads by default (concurrent_mark and concurrent_sweep true, 2 marker tasks in 3.13.0's flag_list.h), so part of the reclamation is off the timed main thread; the README publishes no CPU time for this row. This mechanism is inferred from the VM defaults, since the Dart program itself could not be read.

## Compared with alternatives

Among the catalogued benchLANG binary-trees rows Dart (0.865 s) ties OCaml, trails Java (0.347 s) and Bun (0.816 s), and beats C# (0.931 s); prefer the OCaml or C# rows when you need an inspectable program (their sources are committed), and LangArena's Java and Bun Binarytrees::Obj entries for stronger C++ baselines. Cite this row only when Dart is already your stack.

## Integration

| | |
|---|---|
| **Form** | source-drop (benchmark program; the Dart file itself is not published) |
| **Dependencies** | Dart SDK 3.13.0 from nixpkgs-unstable (flake.lock pinned); any pubspec or package use is not documented |
| **Minimum toolchain** | Dart 3.13.0 as measured; `dart compile exe` has no optimisation-level option for native executables (in the SDK's compile command only the wasm target takes -O), so this is the default AOT pipeline |
| **Platforms** | Measured on x86-64 Linux only (Arch Linux, Ryzen 9 5900X locked at 3.5 GHz) |
| **Thread safety** | Not applicable: a single-isolate workload (the VM's GC helper threads run alongside it) |
| **Drop-in for the baseline** | no |

## Gotchas

- The Dart source is missing, so the row cannot be reproduced. .gitignore ignores every file and re-includes extensions language by language with no !\*.dart rule, languages/ has no Dart directory, and raw languages/Dart/bench.dart returns 404, although run_benchmarks.sh changes into languages/Dart and runs `dart compile exe bench.dart`. A fresh clone fails at the Dart compile step. The algorithm, node layout and timer placement cannot be checked, and checksum agreement cannot be confirmed because benchmark_results_\*.txt is not committed either.
- Harness asymmetry, stated in the README ('native code frees inside the timer, GC runtimes collect when they like'): C and C++ walk every tree a second time to free each node inside the timed region, while a GC runtime just drops the root. With 16 MB semi-spaces and concurrent old-generation mark and sweep on helper threads, some reclamation happens off the main thread and some garbage may still be live at exit, so the row compares allocation strategies rather than languages.
- Small single-run margin: 0.865 s against C's 1.010 s is 14% less time, but the native malloc rows running the same algorithm already spread from 0.986 s (Fortran) to 1.147 s (C++); against the best native row the margin is about 1.14x (derived from page data), from one run with no variance reported.
- The README says `-S` 'strips the snapshot'; in the Dart SDK, -S is --save-debugging-info, which removes debugging information from the executable and saves it to bench.sym. That affects only the reported 5617 KiB binary size, not timing.

## Known shortcomings

- The Dart source is not in the repo (raw 404, not tracked), so the row cannot be reproduced; the C side frees every node inside the timer while Dart's GC does not (OCaml benchLANG precedent); one run; Dart is about 2.13x slower than C over the whole suite.
- Enricher: bench.dart was never committed (.gitignore has no !\*.dart rule; raw 404), so the row cannot be reproduced; C frees inside the timer while Dart 3.13's GC (16 MB semi-space, concurrent mark and sweep on helper threads) does not; one run; the native rows themselves spread 0.986-1.147 s; the README misdescribes -S, which is --save-debugging-info and affects only binary size.

## Caveats and trade-offs

The Dart source is not in the repository: .gitignore ignores every file and whitelists extensions language by language (\*.c, \*.cpp, \*.d, \*.java and so on) with no rule for \*.dart, the languages/ directory listing on GitHub has no Dart folder, and raw.githubusercontent.com returns 404 for languages/Dart/bench.dart although run_benchmarks.sh runs it from there. The Dart row therefore cannot be reproduced or inspected, so the tier is C although the suite is otherwise public; same_algorithm is null because only the analyzer's checksum comparison supports it. One run per language (no variance), single machine. The C and C++ programs are naive per-node malloc/free (I read languages/C/bench.c and languages/C++/bench.cpp); an arena or pool allocator in C would beat the runtimes here. This is 1 of 5 workloads, and C wins overall. Managed runtimes keep default settings with JIT or GC threads and the C code frees inside the timer while the GC need not collect, the same harness effect that puts Java (0.347 s), Nim (0.809 s), Bun (0.816 s), OCaml (0.865 s) and C# (0.931 s) ahead of C on this row. [retier] Enricher: bench.dart is not in the repository (raw 404, not tracked); Dart 3.13's GC runs concurrent mark and sweep on helper threads while C frees inside the timer; one run; native rows spread 0.986-1.147 s.

Whole-process peak RSS 74.6 MiB for Dart against 33.3 MiB for C; stripped executable 5617 KiB against 26 KiB (the AOT binary embeds the runtime). Dart is slower than C on primes (2.963 s vs 2.725 s), Fibonacci and strings.

## Maintenance

Small single-author MIT repo (8 stars, last commit 2026-09-03) with Nix-pinned toolchains, but the Dart row cannot be reproduced from it because bench.dart was never committed; treat it as a first-party anecdote at tier C at most (a move to D is defensible if unpublished code counts as no valid measurement).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The README results table (3 September 2026, one run per language, Ryzen 9 5900X at 3.5 GHz) shows Dart 3.13.0 AOT binary trees 0.865 s against C 1.010 s and C++ 1.147 s, and the build table gives the C/C++ flags (gcc/g++ 16.2.0 -O3 -march=native -flto -funroll-loops -ffp-contract=off -s) and the Dart command. The Dart program itself is not in the repository (.gitignore whitelists no \*.dart, languages/ has no Dart directory, raw languages/Dart/bench.dart returns 404), so the Dart side cannot be inspected or reproduced and the row cannot reach A.
- **Verifier notes:** All numbers check out on the page (Dart 0.865 s, C 1.010 s, C++ 1.147 s; Dart total 20.754 s against C 9.762 s, Fibonacci 8.135 s vs 1.694 s, strings 6.523 s vs 2.132 s). languages/C/bench.c allocates every node with malloc and frees every tree inside the timed loop (make_tree/free_tree), so the win is the harness effect already documented for the OCaml benchLANG binary-trees row (C frees inside the timer, the GC runtime need not collect) plus bump allocation, not Dart codegen; same_algorithm stays unverifiable because the Dart source is missing. Shortcomings: one run, Dart source absent from the repo, 1 of 5 workloads, Dart 2.13x slower overall.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-117 (wave 14 seed pass, 2026-10-13); enricher (seed pass, 2026-10-13)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/HEAD/README.md>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/HEAD/.gitignore>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/HEAD/run_benchmarks.sh>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/HEAD/languages/Dart/bench.dart>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/HEAD/languages/C/bench.c>
  - <https://github.com/GlebOlsen/benchLANG>
  - <https://github.com/GlebOlsen/benchLANG/tree/main/languages>
  - <https://github.com/GlebOlsen/benchLANG/commits/main>
- **Sources the enricher read:**
  - <https://github.com/GlebOlsen/benchLANG/commits/main>
  - <https://github.com/GlebOlsen/benchLANG/tree/main/languages>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/HEAD/README.md>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/HEAD/.gitignore>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/HEAD/run_benchmarks.sh>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/HEAD/flake.nix>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/HEAD/analyze_results.sh>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/HEAD/languages/C/bench.c>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/HEAD/languages/C++/bench.cpp>
  - https://raw.githubusercontent.com/GlebOlsen/benchLANG/HEAD/languages/Dart/bench.dart (404)
  - https://raw.githubusercontent.com/GlebOlsen/benchLANG/HEAD/languages/dart/bench.dart (404)
  - <https://raw.githubusercontent.com/dart-lang/sdk/main/pkg/dartdev/lib/src/commands/compile.dart>
  - <https://raw.githubusercontent.com/dart-lang/sdk/main/runtime/vm/flag_list.h>
  - <https://raw.githubusercontent.com/dart-lang/sdk/main/runtime/vm/globals.h>
  - <https://raw.githubusercontent.com/dart-lang/sdk/3.13.0/runtime/vm/flag_list.h>
  - <https://raw.githubusercontent.com/dart-lang/sdk/3.13.0/runtime/vm/globals.h>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:dart/glebolsen/benchlang#binary-trees`) · [data/wave14/enrich/raw/lang_dart_glebolsen_benchlang_binary_trees.json](../../../data/wave14/enrich/raw/lang_dart_glebolsen_benchlang_binary_trees.json) (enrichment confidence 0.7)

</details>
