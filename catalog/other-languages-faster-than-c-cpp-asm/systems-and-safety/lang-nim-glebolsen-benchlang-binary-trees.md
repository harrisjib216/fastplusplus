# Nim 2.2.10 (ref objects): benchLANG binary trees vs C and C++ at -O3

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Systems and safety](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Nim` · `MIT` · 🟢 active

> Nim 2.2.10 ref-object binary trees (default ORC) run 1.25x faster than malloc/free C and 1.42x faster than new/delete C++ under matched GCC flags.

| | |
|---|---|
| **Beats** | C (GCC 16.2.0: gcc -O3 -march=native -flto -funroll-loops -ffp-contract=off) and C++ (g++ -std=c++20, same flags); both malloc/new every node and free (delete) it inside the timed region |
| **Claimed result** | README results table (September 2026, one run per language): Nim 0.809 s vs C 1.010 s and C++ 1.147 s on binary trees, about 1.25x faster than C and 1.42x faster than C++ (derived from page data). Other columns, Nim vs C: primes 2.725 vs 2.725 s, Fibonacci 1.716 vs 1.694 s, strings 2.804 vs 2.132 s, Mandelbrot 2.244 vs 2.201 s; total 10.298 s vs 9.762 s, so C is faster overall. |
| **Workload** | CLBG-style binary trees, depths 4 to 18: allocate, check and drop complete binary trees of individually allocated nodes; benchLANG's fifth workload (the others are primes, Fibonacci(45), strings and Mandelbrot). |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 5900X locked at 3.5 GHz, 48 GB DDR4-3600 CL16, Arch Linux; one run per language, 3 September 2026 |
| **Compiler and flags** | Nim 2.2.10: nim c --hints:off --nimcache:nimcache -d:danger -d:lto --panics:on --passC:-march=native --passC:-ffp-contract=off --passL:-s; Nim's config/nim.cfg (v2.2.10) adds gcc.options.speed '-O3 -fno-ident -fno-math-errno' and -flto under -d:lto, so the generated C is built at -O3 -march=native -flto (backend gcc from the Nix dev shell, which uses gcc16Stdenv; the exact backend gcc version is not printed). Default Nim 2 memory management (ORC) and Nim's own allocator (no -d:useMalloc). C: gcc -O3 -march=native -flto -funroll-loops -ffp-contract=off -s; C++: g++ -std=c++20 with the same flags (GCC 16.2.0, nixpkgs-unstable). |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | yes |
| **Adoption** | 8 stars (suite repo) |
| **Last commit** | 2026-09-03 |
| **Links** | [repository](https://github.com/GlebOlsen/benchLANG) · [benchmark](https://raw.githubusercontent.com/GlebOlsen/benchLANG/HEAD/README.md) |

## Verdict

benchLANG's 3 September 2026 run (one run per language; Ryzen 9 5900X locked at 3.5 GHz, Arch Linux, 48 GB DDR4-3600) timed binary trees at 0.809 s for Nim 2.2.10 (-d:danger -d:lto, default ORC and allocator, -march=native) against 1.010 s for C and 1.147 s for C++, both built with GCC 16.2.0 at -O3 -march=native -flto -funroll-loops -ffp-contract=off and allocating every node with malloc/free or new/delete. That makes Nim about 1.25x faster than C and 1.42x faster than C++ (derived from page data), and analyze_results.sh confirms all languages printed the same checksum.

## Use it when

- You already write Nim and build many small tree or graph nodes as ref objects: with the default ORC memory manager and allocator they beat naive per-node malloc/free C under the same GCC flags.
- Porting allocation-heavy C or C++ code to Nim and worried about the cost of ref objects: on this workload you do not need manual pooling to keep up.
- You want deterministic freeing without tracing-GC pauses: ORC frees each tree at scope exit, unlike the Java (0.347 s) or Bun (0.816 s) rows, which collect when they like.
- As evidence that per-node glibc malloc/free, not the language, sets the speed of a naive C or C++ tree builder.

## Skip it when

- As evidence that Nim generates faster code than C: same algorithm and comparable flags, so the gap is the allocator; a C or C++ version with an arena (for example std::pmr::monotonic_buffer_resource) or a faster malloc would likely close or reverse it (inference; benchLANG has no such variant).
- Memory-constrained deployments: whole-process peak RSS is 51.5 MiB for Nim against 33.3 MiB for C; scaled to the 1,048,575-node stretch tree that suggests about 48 bytes per Nim node against 32 for glibc (inference from page data).
- If the margin matters to you: it is 0.2 s from one run, while C and C++ themselves differ by 0.137 s on identical logic.
- String-heavy or whole-program comparisons: Nim loses strings (2.804 s vs 2.132 s for C) and the suite total (10.298 s vs 9.762 s).
- Cyclic object graphs: these trees never form cycles, so the cost of ORC's cycle collector is not exercised here.

## How it is fast

The gain comes from the allocation path, not from code generation: both sides run the same recursion and both free every node inside the timer (C and C++ walk the tree a second time with free_tree; Nim's ORC destructors walk it when the reference drops to zero). Nim takes nodes from its own runtime allocator (the build does not pass -d:useMalloc), while C and C++ call glibc malloc/free or operator new/delete for every 24-byte node. Per node that is about 11.8 ns for Nim against 14.8 ns for C and 16.8 ns for C++ (derived from page data over 68.3M nodes). The generated C is compiled at -O3 -fno-math-errno (gcc.options.speed in Nim 2.2.10's nim.cfg) with -flto=auto (the nim.cfg lto block) and -march=native, so the backend flags match the C row except -funroll-loops.

## Compared with alternatives

This is the cleaner Nim data point: same GCC 16.2.0 flags on both sides, checksums enforced, a dated 2026 run. The LangArena Nim Binarytrees::Obj sibling shows a larger margin (Nim/GCC/ARC 1.193 s vs C++ 2.098 s) but against std::make_unique. Among benchLANG's own binary-trees rows, Java (0.347 s) wins by far more but at 987.8 MiB peak RSS, and Bun (0.816 s) roughly ties Nim at 336.1 MiB, so pick Nim when you want a native binary with deterministic freeing.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | Nim standard library only (std/monotimes, std/strutils); the Nix dev shell from flake.nix, with nixpkgs-unstable pinned in flake.lock (rev e8be781, 2026-08-29) |
| **Minimum toolchain** | Nim 2.2.10 as measured (default ORC memory management); backend C compiler taken from \$CC in the dev shell, GCC 16.2.0 by inference since the runner does not print it |
| **Platforms** | Measured on x86-64 Linux only (flake.nix pins x86_64-linux); -march=native ties the binary to the build CPU |
| **Thread safety** | Not applicable: single-threaded workload |
| **Drop-in for the baseline** | no |

## Gotchas

- The C compiler behind the Nim row is not recorded: the nixpkgs Nim wrapper compiles the generated C with \$CC and only falls back to its own build-time compiler when CC is unset. In the gcc16Stdenv dev shell that should be GCC 16.2.0, but the runner logs only `nim --version`. The -O3 and -flto=auto flags come from nim.cfg, not the command line, and -funroll-loops is not passed to Nim.
- Single run per language (run_benchmarks.sh defaults to RUNS=1; --runs N exists but the README table does not use it), and the raw benchmark_results_\*.txt files are gitignored, so the README table is the only record.
- The .gitignore ignores every file except whitelisted extensions (.nim is tracked, but nim.cfg and config.nims are not), so a local Nim config that changed the allocator or memory manager would not show up in the repo; the published numbers can only be assumed to use the defaults.
- A May 2026 commit titled 'Fixed nim unfair slowness moved to 32bit from 64bit' (68b9be5) changed only the Nim primes code to int32; the binary-trees code was not touched, but it shows the Nim file was tuned after earlier runs.

## Known shortcomings

- One run; the win is the Nim allocator vs glibc malloc (Java 0.347 s also beats C) and C is faster overall in the suite; 8 stars.
- Same algorithm on both sides with checksums enforced; the win is the allocator (about 11.8 ns per node for Nim vs 14.8 for C, derived). One run per language (RUNS=1), the C compiler behind the Nim row is not logged (GCC 16.2.0 inferred from \$CC in the gcc16Stdenv dev shell), -O3 and -flto=auto come from nim.cfg rather than the command line, Nim gets no -funroll-loops, the .gitignore would hide a local nim.cfg, and peak RSS is 51.5 vs 33.3 MiB.

## Caveats and trade-offs

One run per language on one machine (run_benchmarks.sh defaults to RUNS=1), so a 0.2 s gap is within plausible run-to-run noise; inputs are compile-time constants. Same algorithm and same work on both sides (C frees each tree inside the timed region, Nim's ORC destructors free at scope exit). The win is allocator behaviour: C and C++ pay glibc malloc/free (new/delete) per 24-byte node, while Nim uses its own runtime allocator; a pooled or arena C version, or C linked with a faster malloc, would likely erase the gap (my inference, not measured). Many other languages also beat C here (Java 0.347 s, Bun 0.816 s, OCaml and Dart 0.865 s, C# 0.931 s, Fortran 0.986 s). C is faster over the whole suite (9.762 s vs Nim 10.298 s); Nim loses strings (2.804 vs 2.132 s). 8-star suite. [retier] Enricher: same algorithm on both sides with checksums enforced; the win is the allocator (about 11.8 ns per node for Nim vs 14.8 for C, derived). The C compiler behind the Nim row is not logged (GCC 16.2.0 inferred from \$CC in the gcc16Stdenv dev shell), -O3 and -flto=auto come from nim.cfg rather than the command line, Nim gets no -funroll-loops, the .gitignore would hide a local nim.cfg, and peak RSS is 51.5 vs 33.3 MiB.

Peak RSS for the whole process is 51.5 MiB for Nim vs 33.3 MiB for C; Nim loses to C on the strings workload (2.804 s vs 2.132 s).

## Maintenance

Small single-author MIT suite (8 stars, last commit 2026-09-03) with a Nix flake and flake.lock that make the toolchains reproducible; the Nim file is a benchmark sample, not a component to adopt.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded C to A: benchLANG is a third-party suite with public code (languages/Nim/bench.nim, languages/C/bench.c, languages/C++/bench.cpp, run_benchmarks.sh, Nix flake), compilers (GCC 16.2.0, Nim 2.2.10), exact build flags for every language and the CPU (Ryzen 9 5900X locked at 3.5 GHz) all stated; README table shows Nim 0.809 s vs C 1.010 s and C++ 1.147 s. A missing mechanism is not a tier criterion.
- **Verifier notes:** Numbers match the README table (Nim 0.809 s, C 1.010 s, C++ 1.147 s; 1.25x vs C and 1.42x vs C++ derived from page data). Shortcomings to record: single run, allocator-driven win (glibc malloc baseline), many languages including Java beat C on this workload, C faster overall, small 8-star suite. MIT, last commit 2026-09-03, active.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-88 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/HEAD/README.md>
  - <https://github.com/GlebOlsen/benchLANG>
  - <https://github.com/GlebOlsen/benchLANG/commits>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/HEAD/languages/Nim/bench.nim>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/HEAD/languages/C/bench.c>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/HEAD/languages/C++/bench.cpp>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/HEAD/run_benchmarks.sh>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/HEAD/flake.nix>
  - <https://raw.githubusercontent.com/nim-lang/Nim/v2.2.10/config/nim.cfg>
- **Sources the enricher read:**
  - <https://github.com/GlebOlsen/benchLANG>
  - <https://github.com/GlebOlsen/benchLANG/commits>
  - <https://github.com/GlebOlsen/benchLANG/commit/68b9be5>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/HEAD/README.md>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/HEAD/languages/Nim/bench.nim>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/HEAD/languages/C/bench.c>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/HEAD/languages/C++/bench.cpp>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/HEAD/run_benchmarks.sh>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/HEAD/analyze_results.sh>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/HEAD/flake.nix>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/HEAD/flake.lock>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/HEAD/.gitignore>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/nim-lang/Nim/v2.2.10/config/nim.cfg>
  - <https://raw.githubusercontent.com/NixOS/nixpkgs/nixpkgs-unstable/pkgs/by-name/ni/nim/package.nix>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:nim/glebolsen/benchlang#binary-trees`) · [data/wave14/enrich/raw/lang_nim_glebolsen_benchlang_binary_trees.json](../../../data/wave14/enrich/raw/lang_nim_glebolsen_benchlang_binary_trees.json) (enrichment confidence 0.4)

</details>
