# Zig std.sort.pdq (LangArena Sort::Self) vs C++ std::sort

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Systems and safety](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Zig` · `MIT` · 🟢 active

> Zig's standard-library pdqsort (std.sort.pdq) sorts 400k int32 about 1.2x faster than libstdc++ std::sort in LangArena Sort::Self.

| | |
|---|---|
| **Beats** | std::sort (libstdc++) on a copied std::vector&lt;int32_t&gt; in the C++ version of the same test |
| **Claimed result** | Zig 0.809 s (ReleaseSafe) vs C++/G++ 0.982 s (best of all C/C++ configurations; C++/Clang++ 1.022 s). About 1.2x faster (derived from page data). Zig/Unchecked (ReleaseFast) 0.819 s. |
| **Workload** | LangArena Sort::Self: copy a 400,000-element int32 array (values below 1,000,000) and sort the copy with the language's built-in sort, 50 iterations (run.js). |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 7 3800X 8-Core Processor, 78GB RAM, x86_64 Linux (host kostya-ms7c37, results dated 2026-10-05) |
| **Compiler and flags** | C/C++ 'prod' build: make -j prod with -O2 -DNDEBUG -fstack-protector-strong -fno-omit-frame-pointer, -std=c++20 (clang 22.1.8, g++ 16.0.1 20260322 trunk). Same suite also builds 'Fast' (-O3 -march=native -mtune=native -funroll-loops, thin LTO), 'Unsafe' (-O3 -march=native -ffast-math, full LTO) and PGO variants of every C and C++ test; all of them are in the results file. Zig 0.17.0: zig build build-zig (ReleaseSafe, per zig/build.zig); the Unchecked row uses ReleaseFast. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | yes |
| **Why it wins** | Not stated by the suite. zig/src/sort_self.zig calls std.sort.pdq(i32, arr, {}, std.sort.asc(i32)), a pattern-defeating quicksort variant, against libstdc++ introsort; the library algorithm difference is the likely cause (inferred from the source, not measured separately). |
| **Adoption** | 43.3k stars (GitHub copy; development moved to Codeberg, last GitHub commit 'README: migrated to codeberg') |
| **Last commit** | 2025-11-27 |
| **Links** | [repository](https://github.com/ziglang/zig) · [benchmark](https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-10-05-kostya-ms7c37.js) |

## Verdict

On an AMD Ryzen 7 3800X (LangArena results 2026-10-05, one run per configuration), 50 copy-and-sort iterations of a 400,000-element int32 array take 0.809 s with Zig 0.17.0 ReleaseSafe std.sort.pdq (0.819 s ReleaseFast) against 0.982 s for g++ 16.0.1 trunk -O2 std::sort on libstdc++, the best of the 10 C++ configurations (clang++ 22.1.8 1.022 s; all C++ rows 0.982-1.027 s; C qsort rows 1.957-2.207 s): about 1.21x (derived from page data). Peak memory is 7.3 MB for Zig against 8.6 MB for C++/G++.

## Use it when

- In Zig code sorting large slices of primitive keys where stability does not matter: std.sort.pdq or std.mem.sortUnstable sorts in place with no allocator and a fixed-size stack of ranges.
- When you want to keep safety checks on: the ReleaseSafe build (0.809 s) was no slower than ReleaseFast (0.819 s) on this test, so bounds checks cost nothing measurable here.
- Inputs that may be presorted or reversed: pivot sampling flags increasing or decreasing slices, reverses the latter and tries a partial insertion sort before partitioning (per pdq.zig).
- As a C++ reader: evidence that libstdc++ std::sort on random 32-bit keys is a weak baseline; the C++ form of the same idea, with branchless partitioning added, is the catalogued orlp/pdqsort header.

## Skip it when

- As evidence that Zig the language beats C++: in the same run the hand-written, same-algorithm Sort::Quick has Zig ReleaseSafe at 1.266 s against C/Gcc 1.15 s and C++/G++ 1.175 s (Zig/Unchecked 1.146 s, parity), and Sort::Merge has Zig 1.504 s against C/Clang 1.09 s.
- When you need the fastest integer sort: on the same data Rust's built-in slice::sort takes 0.41 s (about 2x faster than Zig's pdq) and Julia's radix-sorting sort! 0.116 s.
- When equal keys must keep their order: pdq is unstable; std.mem.sort (block sort) is Zig's stable option and was not measured here.
- From C or C++: there is nothing to call without FFI; use orlp/pdqsort or another catalogued C++ sort instead.

## How it is fast

lib/std/sort/pdq.zig is a port of Orson Peters' pattern-defeating quicksort: Tukey's ninther pivot for ranges of 50 or more, insertion sort for ranges of 24 or fewer, a bounded partial insertion sort when pivot sampling sees presorted data, an equal-elements partition when the pivot equals its left neighbour, xorshift pattern breaking and a heapsort fallback after too many unbalanced partitions. Its partition is still a branchy Hoare loop (the source carries 'TODO: Enable the BlockQuicksort optimization'), so it lacks the branchless block partition that makes orlp/pdqsort about 2x faster than std::sort on random ints. libstdc++ std::sort is introsort with a median of three (first+1, middle, last-1), an unguarded Hoare partition, a 16-element cutoff and one final insertion-sort pass. The suite does not isolate whether the 1.2x comes from the better pivot sampling, the leaf handling or LLVM versus GCC code generation.

## Compared with alternatives

The Rust slice::sort Sort::Self sibling is about 2x faster on the same data and the ipnsort/driftsort entry (sort-research-rs) has controlled benchmarks, so for engineering decisions about sort algorithms cite those; this row matters only to Zig users choosing an unstable, allocation-free sort. For C++ code, orlp/pdqsort is the like-for-like replacement and adds the branchless block partition that Zig's port leaves as a TODO.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none (Zig standard library, lib/std/sort/pdq.zig) |
| **Minimum toolchain** | std.sort.pdq was added to Zig's standard library on 2023-05-24 ('std.sort: add pdqsort and heapsort'); the subrange out-of-bounds fix (#25253) landed 2025-09-18 for the 0.15.2 milestone; measured on Zig 0.17.0 |
| **Platforms** | any Zig target; measured on x86-64 (AMD Ryzen 7 3800X, Linux) |
| **Thread safety** | single-threaded in-place sort of the caller's slice; no global state and no allocation (fixed stack array of ranges), so sorts of distinct slices can run concurrently |
| **Drop-in for the baseline** | partial — semantics match std::sort (unstable, in place, O(n log n) worst case through the heapsort fallback), but it is a Zig API taking a comptime lessThan function and C++ cannot call it without FFI |

## Gotchas

- Input quirk, equal on both sides (checked by re-running the generator): the data come from the Benchmarks Game LCG (IM 139968, IA 3877, IC 29573 in both cpp/src/helper.hpp and zig/src/helper.zig), whose period is 139,968, so the 400,000 keys are one sequence repeated about 2.86 times and every value occurs 2 or 3 times. Zig's equal-pivot partition may gain slightly from that; the input is not 400k independent random keys.
- The checksum (run.js expects 61757772) adds one random input element and one random element of the sorted copy per iteration, so it proves the code ran on identical data but would not catch a partly wrong sort; no harness bug was found: both sides share the RNG, the reset before timing, the 20% untimed warm-up and the timed loop that includes the copy.
- Issue #25250: pdqContext on a subrange starting above 0 called lessThan and swap with an index outside the range (partialInsertionSort); fixed in PR #25253 on 2025-09-18. Whole-slice std.sort.pdq calls start at 0 and were not affected, but older Zig releases used with pdqContext on subranges were.
- One measurement per configuration on one machine, no variance; ReleaseSafe beating ReleaseFast by 1% shows noise of that order. The GitHub copy of pdq.zig checked here is frozen at 2025-11-27; the Zig 0.17.0 source on Codeberg could not be opened from this session.

## Known shortcomings

- Win is the stdlib: Zig's pdqsort vs libstdc++ introsort (0.809 vs 0.982 s, 1.2x, single run); the GitHub repo is frozen since 2025-11-27 with development moved to Codeberg; C++ -O3 -march=native builds included and slower.
- No harness bug: data, RNG, warm-up and timing are symmetric. The win is the stdlib pdqsort against libstdc++ introsort, not the language: Zig's pdq.zig partition is still branchy ('TODO: Enable the BlockQuicksort optimization'), orlp/pdqsort would be the better C++ choice, the same-algorithm Sort::Quick row has Zig ReleaseSafe 1.266 s vs C/Gcc 1.15 s, and Rust's slice::sort is 2x faster on the same data. The LCG period is 139,968, so keys repeat 2-3 times. Issue #25250 (subrange out-of-bounds) was fixed by #25253.

## Caveats and trade-offs

Small margin (about 20 percent) on one machine and one run. The ReleaseSafe build (0.809 s) is slightly faster than ReleaseFast (0.819 s), which suggests run-to-run noise of a few percent. The win belongs to Zig's standard-library pdqsort versus libstdc++ introsort, not to the Zig language; the -O3 -march=native C++ builds (0.995-1.021 s) do not beat the -O2 prod G++ build. The GitHub repository ziglang/zig is a frozen copy since 2025-11-27 ('README: migrated to codeberg'); development and the Zig 0.17.0 used in this run come from Codeberg, which was unreachable from this session, so the pdq source checked is the GitHub copy. LangArena describes itself as a subjective benchmark; the README says AI tools assisted translating tests between languages and that idiomatic constructs are used per language. One measurement per test and configuration (no variance reported), single machine, one monthly run. Rows were selected by the search agent as tests where the language beats every C/C++ configuration; most other tests in the suite go the other way. Ratios are derived from the results file, not stated by the suite. The benchmark suite itself is MIT-licensed (kostya/LangArena, 41 stars, last commit 2026-10-08). [retier] Enricher: no harness bug; the win is the stdlib pdqsort against libstdc++ introsort, not the language. Zig's pdq.zig partition is still branchy ('TODO: Enable the BlockQuicksort optimization'), the same-algorithm Sort::Quick row has Zig ReleaseSafe 1.266 s vs C/Gcc 1.15 s, and Rust's slice::sort is 2x faster on the same data. Issue #25250 (subrange out-of-bounds) was fixed by #25253.

Zig 0.x standard library API is still changing between releases; the benchmark ran on Zig 0.17.0.

## Maintenance

Zig (MIT) is actively developed on Codeberg while the GitHub repository is a frozen copy since 2025-11-27 ('README: migrated to codeberg'); pdq.zig's algorithm is unchanged since 2023 apart from bug fixes; the result is a modest, single-run standard-library algorithm win in a self-described subjective suite, with no harness bug found behind the numbers.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** Results file has Sort::Self-runtime Zig 0.809 s (ReleaseSafe) and Zig/Unchecked 0.819 s (ReleaseFast) vs C++/G++ 0.982 s, the minimum over all C/C++ configurations, with Zig 0.17.0, build commands (zig build build-zig, build.zig ReleaseSafe), g++/clang versions, flags in cpp/Makefile and the Ryzen 7 3800X CPU; code public (zig/src/sort_self.zig, cpp/src/sort.cpp). Third-party suite, fully reproducible.
- **Verifier notes:** Numbers match the results file (Zig 0.809 s vs C++/G++ 0.982 s, C++/Clang++ 1.022 s; 1.2x derived). Shortcomings: small single-run margin, stdlib pdqsort vs introsort rather than language, GitHub repo frozen since 2025-11-27 with development on Codeberg (repo_url could point to codeberg.org/ziglang/zig; maintenance active by the GitHub date for now).
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-59 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-10-05-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/run.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/Makefile>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/rust/Cargo.toml>
  - <https://github.com/kostya/LangArena>
  - <https://github.com/kostya/LangArena/commits>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/zig/src/sort_self.zig>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/zig/build.zig>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/sort.cpp>
  - <https://github.com/ziglang/zig>
  - <https://github.com/ziglang/zig/commits>
  - <https://raw.githubusercontent.com/ziglang/zig/HEAD/lib/std/sort/pdq.zig>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/run.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-10-05-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/zig/build.zig>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/zig/build.zig.zon>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/zig/src/sort_self.zig>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/zig/src/benchmark.zig>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/zig/src/helper.zig>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/zig/src/main.zig>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/Makefile>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/sort.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/sort.hpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/benchmark.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/helper.hpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/helper.cpp>
  - <https://raw.githubusercontent.com/ziglang/zig/HEAD/lib/std/sort/pdq.zig>
  - <https://raw.githubusercontent.com/ziglang/zig/HEAD/lib/std/sort.zig>
  - <https://raw.githubusercontent.com/ziglang/zig/HEAD/lib/std/mem.zig>
  - <https://github.com/ziglang/zig>
  - <https://github.com/ziglang/zig/commits>
  - <https://github.com/ziglang/zig/commits/master/lib/std/sort/pdq.zig>
  - <https://github.com/ziglang/zig/issues/25250>
  - <https://raw.githubusercontent.com/gcc-mirror/gcc/HEAD/libstdc++-v3/include/bits/stl_algo.h>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:zig/kostya/langarena#sort-self`) · [data/wave14/enrich/raw/lang_zig_kostya_langarena_sort_self.json](../../../data/wave14/enrich/raw/lang_zig_kostya_langarena_sort_self.json) (enrichment confidence 0.75)

</details>
