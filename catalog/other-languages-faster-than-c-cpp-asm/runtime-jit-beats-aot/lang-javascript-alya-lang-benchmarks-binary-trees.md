# Bun (JavaScriptCore JIT 1.4.2): alya-lang/benchmarks binary trees

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Runtime JIT beats ahead-of-time](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `JavaScript` · `MIT` · 🟢 active

> One CI run of the Alya suite: Bun 1.4.2 finishes depth-14 binary trees in 98.3 ms, against 126.3 ms for gcc -O2 C using malloc and free per node.

| | |
|---|---|
| **Beats** | C (gcc 13.3.0 -O2, malloc and free per node, binary_trees.c) |
| **Claimed result** | Bun 98.3 ms vs C 126.3 ms (median of 10 timed runs after 1 warm-up): about 1.28x faster (derived from page data). Of the 14 benchmarks in the same table, Bun beats C only on this one. |
| **Workload** | Binary trees at depth 14: stretch tree, long-lived tree, then repeated pairs of short-lived trees built, checked and (in C) freed. |
| **Metric** | throughput |
| **Compiler and flags** | gcc (Ubuntu 13.3.0-6ubuntu2\~24.04.1) 13.3.0 invoked by cross_lang/runner.ts as 'gcc -O2 binary_trees.c -o binary_trees_c' (no -march, no LTO); Bun 1.4.2 run as 'bun run binary_trees.js' (installed by oven-sh/setup-bun@v2 at CI time); Ubuntu 24.04.5 LTS x64 on a GitHub Actions ubuntu-latest runner (.github/workflows/benchmark.yml). |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | no |
| **Adoption** | 0 stars |
| **Last commit** | 2026-10-08 |
| **Links** | [repository](https://github.com/alya-lang/benchmarks) · [benchmark](https://raw.githubusercontent.com/alya-lang/benchmarks/main/README.md) |

## Verdict

On a GitHub Actions ubuntu-latest x64 runner (Ubuntu 24.04.5, CPU not recorded, run of 2026-10-08), the median of 10 whole-process runs after one warm-up was 98.3 ms for 'bun run binary_trees.js' (Bun 1.4.2). The same depth-14 binary-trees program in C, built with gcc 13.3.0 -O2 with malloc and free per node, took 126.3 ms: about 1.28x (derived from page data). Earlier snapshots of the same job range from Bun 1.31x faster to C 1.19x faster.

## Use it when

- As one small data point that a JIT plus a generational GC can beat naive per-node malloc/free in C on allocation-bound code with tiny, short-lived nodes (24-byte structs, roughly 6.35 million allocations).
- As a prompt to check the allocator in your own C or C++ tree code: the C program here mallocs and frees one node at a time, at -O2 without -march or LTO.
- As a small MIT-licensed, four-language test kit: each program prints one integer that the runner checks against a fixed expected value (-43682 for binary trees).

## Skip it when

- As evidence that Bun beats C in general: C wins the other 13 rows of the same table, by 2.5x (linked list, 3.0 vs 7.4 ms) up to 9.2x (matrix multiply, 1.3 vs 12.0 ms) (derived from page data).
- As a stable number: in earlier snapshots of the same CI job, C beats Bun on binary trees in 4 of 14 runs (see gotchas).
- Against a C program that uses an arena or pool allocator, frees nothing before exit, or builds with -O3 -march=native: none of these was measured here.
- When memory or footprint matters: the README's Bun figures (about 92 MB runtime, about 24 ms cold start, about 36.5 MB RSS) are hard-coded strings in runner.ts, not measurements, and Bun's RSS is never recorded for this workload.
- As a sub-100 ms latency figure: these are whole-process times on a shared, noisy VM whose CPU model is not recorded.

## How it is fast

The suite names no mechanism. The gap comes from memory management, not code generation: C makes one malloc and one free call per node, plus a second recursive walk to free each tree, about 6.35 million of each (20 ns per node at 126.3 ms, process start included; derived from page data). JavaScriptCore allocates from a segregated-storage heap. Its non-moving Riptide collector is generational through sticky mark bits, so an eden collection visits only new objects and remembered-set entries, and dead short-lived trees are reclaimed by sweeping with no per-object free call. Allocation-bound tree code with the same shape also lets the GC'd runtimes beat malloc/free C in the benchLANG and LangArena sibling entries.

## Compared with alternatives

Cite the benchLANG Bun row (0.816 s vs C 1.010 s built at -O3 -march=native -flto) or LangArena Binarytrees::Obj (Bun 0.973 s vs the best C/C++ build at 2.098 s) instead. They show the same Bun-beats-malloc effect against stronger C builds in second-long runs; this row is only a 100 ms CI data point whose winner changes with the runner.

## Integration

| | |
|---|---|
| **Form** | benchmark script (single-file JavaScript, run with 'bun run binary_trees.js') |
| **Dependencies** | Bun runtime (1.4.2 as measured); the full runner also needs gcc, Python 3.12, Rust and the Alya compiler (alya-lang/alya, built from the develop branch in CI) |
| **Minimum toolchain** | Bun 1.4.2 as measured (CI installs whatever oven-sh/setup-bun@v2 resolves to); C baseline gcc 13.3.0 at -O2 |
| **Platforms** | Published numbers are from GitHub Actions ubuntu-latest x64 (Ubuntu 24.04.5 LTS) only; the workflow can also target ARM64 Linux, Windows and macOS runners, but those results are not in the README |
| **Thread safety** | not applicable (single-threaded scripts) |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw, the result flips between CI runs. I read 14 README snapshots written by the same workflow (2026-09-18 to 2026-10-08; all Bun 1.4.2, gcc 13.3.0 -O2, Ubuntu 24.04.5 x64, one warm-up plus 10 runs). The C/Bun time ratio ranges from 0.84 to 1.31, and C wins in 4 of them: 5ff783f (C 60.0 vs Bun 64.6 ms), 37e3b6c (70.2 vs 83.3), 3ee8a72 (70.5 vs 82.4) and e382f6c (106.0 vs 113.4). In the fast snapshots every row speeds up (fib C 1.4 to 1.6 ms vs 2.3), C's binary-trees time drops about 1.8x (126 to 70 ms) and Bun's only about 1.17x (97 to 83 ms). Which machine the shared runner draws decides the winner, and the runner never records the CPU model.
- Unequal work: inside the timed process, C calls free on every node through a recursive free_tree (about 6.35 million free calls plus an extra full traversal of each tree). The JS version frees nothing and leaves dead trees to the GC and to process exit. Only the build and check passes are the same algorithm.
- Whole-process wall clock: spawnSync timing of programs that run about 100 ms. Bun's start-up, parsing and JIT tiering fall inside its 98.3 ms, and C's process start falls inside its 126.3 ms. Each language's 10 runs are taken back to back, not interleaved.
- Output check: a substring match on -43682 that only warns, although the runner then exits 1 and the CI commit step does not run, so committed numbers did pass the check. The verifier's '1.9x to 9x' range for the other 13 C wins is really 2.5x to 9.2x on the 2026-10-08 table.

## Known shortcomings

- C row built -O2 not -O3; no CPU model (GitHub Actions shared runner); timing is whole-process wall clock; the C program does malloc/free per node plus a timed recursive free pass while JavaScript leaves it to the GC, so the win is allocator/GC, not codegen; Bun wins 1 of 14 rows.
- Harness flaw: the win flips between CI runs. Across 14 README snapshots (all Bun 1.4.2, gcc 13.3.0 -O2, Ubuntu x64) the C/Bun ratio runs 0.84-1.31 and C wins 4 of them (5ff783f 60.0 vs 64.6 ms, 37e3b6c 70.2 vs 83.3, 3ee8a72 70.5 vs 82.4, e382f6c 106.0 vs 113.4), so the outcome depends on the unrecorded runner CPU. C does about 6.35M free calls plus an extra traversal while JS frees nothing; timing is whole-process spawnSync. Correction: the other 13 C wins span 2.5x-9.2x, not 1.9x-9x.

## Caveats and trade-offs

This suite exists to compare the new Alya language; the Bun-versus-C row is incidental, first-party to Alya, and the repo gives no mechanism for Bun. C is built at -O2, not -O3. Runs happen on a shared GitHub Actions ubuntu-latest VM (CPU model not stated, noisy neighbours) and the README is rewritten by CI on each dispatch, so the numbers drift between commits. Timing is whole-process wall clock via spawnSync (1 warm-up, median of 10), so Bun's runtime start-up and JIT warm-up are inside its 98.3 ms and C's process start is inside 126.3 ms; the workload is only about 100 ms. The work differs in memory management: the C version calls glibc malloc per node and walks every tree again with a recursive free_tree inside the timed region, while the JS version never frees and leaves dead trees to the GC (possibly never collected before exit). Bun beats C on only this 1 of 14 rows; C wins the other 13 by 1.9x to 9x. The README's start-up, binary-size and RSS table rows for Bun and C are hard-coded strings in runner.ts, not measurements. [retier] The win flips between CI runs: across 14 README snapshots (all Bun 1.4.2, gcc 13.3.0 -O2, Ubuntu x64) the C/Bun ratio runs 0.84-1.31 and C wins 4 (5ff783f 60.0 vs 64.6 ms, 37e3b6c 70.2 vs 83.3, 3ee8a72 70.5 vs 82.4, e382f6c 106.0 vs 113.4), so the outcome depends on the unrecorded runner CPU. C does about 6.35M free calls plus an extra traversal while JS frees nothing; timing is whole-process spawnSync. The other 13 C wins span 2.5x-9.2x.

Bun process start (about 24 ms cold start per the README) is inside the measured time; Bun peak RSS about 36 MB vs about 3 MB for C.

## Maintenance

Active: CI-generated README commits continue to 2026-10-08 (51 commits, 0 stars, MIT). The suite exists to promote the Alya language, so treat it as a reference data point, not something to adopt; the C and JS sources have not changed since the initial commit on 2026-09-11.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now D.
- **Tier reason:** README table (also state/latest_results.json, 2026-10-08) shows C 126.3 ms vs Bun 98.3 ms for binary trees; code (cross_lang/collections/binary_trees.c/.js, cross_lang/runner.ts) and compiler/flags (gcc 13.3.0 -O2) are public, but no CPU model is stated (runs on a GitHub Actions ubuntu-latest shared runner), so not A; a 0-star suite built to promote Alya is not a well-known independent suite, so not B.
- **Retiered** C to D: Enricher: across 14 README snapshots with identical toolchains the C/Bun ratio runs 0.84-1.31 and C wins 4 of them, so the outcome is runner noise rather than a measured win; no stable measurement: C to D (the other C wins span 2.5x-9.2x).
- **Verifier notes:** Numbers verified on README and latest_results.json; tier C stands. Shortcomings for the orchestrator: C at -O2 not -O3, CPU unstated (GitHub Actions shared runner), whole-process wall-clock timing of \~100 ms runs, C pays malloc/free per node plus a timed recursive free pass while JS relies on GC, Bun wins only this 1 of 14 rows, suite is a 0-star promotional benchmark for Alya.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-57 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/alya-lang/benchmarks/main/README.md>
  - <https://raw.githubusercontent.com/alya-lang/benchmarks/main/cross_lang/collections/binary_trees.c>
  - <https://raw.githubusercontent.com/alya-lang/benchmarks/main/cross_lang/collections/binary_trees.js>
  - <https://raw.githubusercontent.com/alya-lang/benchmarks/main/cross_lang/runner.ts>
  - <https://raw.githubusercontent.com/alya-lang/benchmarks/main/state/latest_results.json>
  - <https://raw.githubusercontent.com/alya-lang/benchmarks/main/package.json>
  - <https://raw.githubusercontent.com/alya-lang/benchmarks/main/.github/workflows/benchmark.yml>
  - <https://github.com/alya-lang/benchmarks>
  - <https://github.com/alya-lang/benchmarks/commits>
  - <https://github.com/alya-lang/benchmarks/tree/main/.github/workflows>
- **Sources the enricher read:**
  - <https://github.com/alya-lang/benchmarks>
  - <https://github.com/alya-lang/benchmarks/commits>
  - <https://github.com/alya-lang/benchmarks/commits/main/cross_lang/collections/binary_trees.c>
  - <https://raw.githubusercontent.com/alya-lang/benchmarks/main/README.md>
  - <https://raw.githubusercontent.com/alya-lang/benchmarks/main/cross_lang/collections/binary_trees.c>
  - <https://raw.githubusercontent.com/alya-lang/benchmarks/main/cross_lang/collections/binary_trees.js>
  - <https://raw.githubusercontent.com/alya-lang/benchmarks/main/cross_lang/runner.ts>
  - <https://raw.githubusercontent.com/alya-lang/benchmarks/main/state/latest_results.json>
  - <https://raw.githubusercontent.com/alya-lang/benchmarks/main/package.json>
  - <https://raw.githubusercontent.com/alya-lang/benchmarks/main/.github/workflows/benchmark.yml>
  - <https://raw.githubusercontent.com/alya-lang/benchmarks/87402b1/README.md>
  - <https://raw.githubusercontent.com/alya-lang/benchmarks/e382f6c/README.md>
  - <https://raw.githubusercontent.com/alya-lang/benchmarks/77b1c35/README.md>
  - <https://raw.githubusercontent.com/alya-lang/benchmarks/a8dd0e8/README.md>
  - <https://raw.githubusercontent.com/alya-lang/benchmarks/e592c90/README.md>
  - <https://raw.githubusercontent.com/alya-lang/benchmarks/3ee8a72/README.md>
  - <https://raw.githubusercontent.com/alya-lang/benchmarks/53976ab/README.md>
  - <https://raw.githubusercontent.com/alya-lang/benchmarks/4df784e/README.md>
  - <https://raw.githubusercontent.com/alya-lang/benchmarks/37e3b6c/README.md>
  - <https://raw.githubusercontent.com/alya-lang/benchmarks/90ef849/README.md>
  - <https://raw.githubusercontent.com/alya-lang/benchmarks/5ff783f/README.md>
  - <https://raw.githubusercontent.com/alya-lang/benchmarks/cdab7d0/README.md>
  - <https://raw.githubusercontent.com/alya-lang/benchmarks/bcfa1da/README.md>
  - <https://raw.githubusercontent.com/alya-lang/benchmarks/88d3d14/README.md>
  - WebSearch snippets for webkit.org/blog/7122 (Introducing Riptide; the page itself not opened)
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:javascript/alya-lang/benchmarks#binary-trees`) · [data/wave14/enrich/raw/lang_javascript_alya_lang_benchmarks_binary_trees.json](../../../data/wave14/enrich/raw/lang_javascript_alya_lang_benchmarks_binary_trees.json) (enrichment confidence 0.75)

</details>
