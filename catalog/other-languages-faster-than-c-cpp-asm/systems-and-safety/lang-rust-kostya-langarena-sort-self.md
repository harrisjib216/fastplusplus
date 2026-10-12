# Rust slice::sort (LangArena Sort::Self) vs C++ std::sort

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Systems and safety](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `Apache-2.0 OR MIT` · 🟢 active

> Rust's built-in slice::sort (driftsort) sorts 400k int32 about 2.4x faster than libstdc++ std::sort in LangArena Sort::Self.

| | |
|---|---|
| **Beats** | std::sort (libstdc++ introsort) on a copied std::vector&lt;int32_t&gt; in the C++ version of the same test (g++ and clang++, prod, Fast, Unsafe and PGO builds); C version (libc qsort) is slower still |
| **Claimed result** | Rust 0.41 s vs C++/G++ 0.982 s (prod) and C++/G++/Fast 0.998 s, C++/Clang++ 1.022 s; best of all C/C++ configurations is C++/G++ 0.982 s, C/Clang 1.986 s. About 2.4x faster than the best C/C++ configuration (derived from page data). Rust/WMO 0.403 s, Rust/PGO 0.412 s. |
| **Workload** | LangArena Sort::Self: copy a 400,000-element int32 array (values below 1,000,000) and sort the copy with the language's built-in sort, 50 iterations (run.js). |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 7 3800X 8-Core Processor, 78GB RAM, x86_64 Linux (host kostya-ms7c37, results dated 2026-10-05) |
| **Compiler and flags** | C++ 'prod' (make -j prod): -O2 -DNDEBUG -fstack-protector-strong -fno-omit-frame-pointer -std=c++20; 'Fast': -O3 -march=native -mtune=native -fstack-protector -ftree-vectorize -funroll-loops with -flto=thin; 'Unsafe': -O3 -march=native -ffast-math -fno-stack-protector -fomit-frame-pointer with -flto=full; PGO variants at -O2 (g++ 16.0.1 20260322 trunk, clang 22.1.8; no -stdlib flag, so both compilers use libstdc++ on Linux). Rust 1.99.0 (2026-09-28): cargo build --release (opt-level 3, no LTO); WMO profile codegen-units=1, max-perf profile fat LTO. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | yes |
| **Why it wins** | Not stated by the suite. Reading the sources (rust/src/benchmarks/sort_self.rs calls t.sort() on a cloned Vec&lt;i32&gt;; cpp/src/sort.cpp calls std::sort on a cloned vector) the difference is the standard-library sort itself: Rust's std stable sort versus libstdc++ introsort. The Rust std stable sort is believed to be driftsort in recent releases, which was not verified in this session. |
| **Adoption** | 119.7k stars (rust-lang/rust); the benchmark suite has 41 stars |
| **Last commit** | 2026-10-11 |
| **Links** | [repository](https://github.com/rust-lang/rust) · [benchmark](https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-10-05-kostya-ms7c37.js) |

## Verdict

On an AMD Ryzen 7 3800X (LangArena results 2026-10-05, one run per configuration), 50 copy-and-sort iterations of a 400,000-element int32 array take 0.41 s with rustc 1.99.0 cargo release (Rust/WMO 0.403 s) against 0.982 s for g++ 16.0.1 trunk -O2 std::sort on libstdc++, the best of the 27 C and C++ configurations (clang++ 22.1.8 1.022 s; C qsort rows 1.957-2.207 s): about 2.4x (derived from page data).

## Use it when

- In Rust, sorting large Vec&lt;i32&gt;/Vec&lt;u64&gt;-style primitive slices where stability matters or the input may hold presorted runs: plain .sort() is already driftsort, no crate needed.
- As evidence when porting C++ code to Rust that the default sort will not be a regression: here it is 2.4x faster than std::sort on random 32-bit keys.
- Inputs with partial order (presorted or reversed runs): driftsort detects natural runs and is linear on fully sorted or reversed input, per the slice::sort docs.
- For a C++ project, read this row as a pointer that std::sort is a weak baseline on random integers; the like-for-like algorithms are catalogued in the sort-research-rs entry (ipnsort and driftsort).

## Skip it when

- As evidence that Rust the language beats C++: same-algorithm rows in the same run say otherwise (Sort::Quick parity; Sort::Merge Rust 1.621 s vs C/Clang 1.09 s and C++/Clang++ 1.192 s).
- Memory-constrained code: for this input driftsort allocates a scratch buffer of max(n - n/2, min(n, 8 MB / size_of T)) elements, which is the full 400,000 int32 (1.6 MB) on every call (derived from library/core/src/slice/sort/stable/mod.rs); sort_unstable (ipnsort) sorts in place.
- When stability is not needed: Rust's own docs recommend sort_unstable as generally faster and allocation-free, so this row understates what Rust can do and is not the best Rust choice for plain integers.
- As a C++ std::stable_sort comparison: the suite never measured std::stable_sort, which is the like-for-like stable C++ call.

## How it is fast

Since Rust 1.81 slice::sort is driftsort (Orson Peters and Lukas Bergdoll): powersort-style merging of natural runs found lazily (minimum good run about sqrt(n)), with unsorted stretches handed to a stable quicksort that partitions branchlessly into a scratch buffer, uses an ancestor-pivot check to group equal keys (O(n log k) for k distinct values), and finishes small pieces with a small-sort. libstdc++ std::sort is a classic introsort whose branchy partition mispredicts heavily on random keys. The same suite's hand-written Sort::Quick (same algorithm in every language) is at parity (Rust 1.145 s, C/Gcc 1.15 s, C++/G++ 1.175 s), and even Rust compiled to WASM under Node (0.458 s) beats native std::sort, so the win is the library algorithm, not rustc code generation.

## Compared with alternatives

This row is an independent shootout data point for the ipnsort and driftsort entry (sort-research-rs), which has the controlled benchmarks and the stable-vs-stable comparison; cite that entry for engineering decisions and this one only as third-party confirmation. Against the Zig std.sort.pdq Sort::Self sibling (0.809 s, 1.2x) the Rust default sort is about 2x faster on the same data, though Zig's sort is unstable and allocation-free.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none (Rust core/alloc slice::sort) |
| **Minimum toolchain** | Rust 1.81 (driftsort replaced the old sorts in PR #124032, release-notes tracking issue #129661, milestone 1.81.0); the scratch-size abort fix (#136163) landed February 2025; measured on rustc 1.99.0 |
| **Platforms** | any Rust target; 16-bit targets and optimize_for_size builds fall back to a small mergesort (cfg_select in stable/mod.rs); measured on x86-64 (AMD Ryzen 7 3800X, Linux) |
| **Thread safety** | single-threaded in-place sort of a &mut [T]; the exclusive borrow rules out concurrent access to the same slice |
| **Drop-in for the baseline** | partial — default in Rust code only; semantically it matches std::stable_sort (stable, allocates), not std::sort, and C++ cannot call it without FFI |

## Gotchas

- Algorithm mismatch is the headline flaw: stable driftsort with a full-size scratch buffer against unstable in-place introsort; no std::stable_sort, pdqsort or Rust sort_unstable row was measured, so the 2.4x is a library-choice result, not a like-for-like comparison.
- Input quirk (checked by re-running the generator): the data comes from the Benchmarks Game LCG (IM 139968, IA 3877, IC 29573, same in cpp/src/helper.hpp and rust/src/helper.rs), whose full period is 139,968, so the 400,000 keys are one sequence repeated about 2.86 times with at most 139,968 distinct values. It affects both sides equally; driftsort's O(n log k) equal-key handling may gain slightly from it. The checksum samples only one sorted element per iteration, which would not catch a partly wrong sort (not a concern for std sorts).
- Since 1.81 slice::sort may panic if Ord is not a total order (documented in library/alloc/src/slice.rs); issue #136103 showed an abort (SIGILL) from an undersized scratch buffer with very large element types on odd lengths, fixed in PR #136163 (February 2025).
- One measurement per configuration on one machine, no variance; the Rust row uses cargo release without LTO, and the -O3 -march=native, Unsafe and PGO C++ builds (0.995-1.027 s) are no faster than -O2 prod g++ (0.982 s).

## Known shortcomings

- Win is the stdlib: Rust's driftsort (library/alloc/src/slice.rs, stable) vs libstdc++ introsort (unstable), not the language; single run of a subjective AI-assisted suite; the C++ -O3 -march=native builds are included and slower, so the baseline is not crippled.
- The win comes from the standard-library algorithm, not Rust: stable driftsort against unstable introsort with no std::stable_sort row. The suite's own rows confirm it: Sort::Quick is at parity (Rust 1.145 s vs C/Gcc 1.15 s), Sort::Merge has Rust slower (1.621 s vs C/Clang 1.09 s), and Rust/WASM/Node (0.458 s) still beats native std::sort. Input quirk: the LCG has period 139,968, so the 400k keys are one sequence repeated about 2.86 times, hitting both sides equally; driftsort allocates a 1.6 MB scratch buffer per call. No harness bug behind the numbers.

## Caveats and trade-offs

Compares the stable Rust sort (driftsort) against C++ std::sort (unstable introsort), so the algorithms differ by design; the like-for-like C++ call would be std::stable_sort (not measured). The win belongs to Rust's standard library sort, not to the Rust language or compiler; the -O3 -march=native C++ builds (0.995-1.021 s) do not beat the -O2 prod G++ build (0.982 s). The Rust std sort work (ipnsort and driftsort) is also being catalogued from sort-research-rs by other wave-14 searches, so this row mostly adds an independent shootout measurement. Rust build is cargo release without LTO and is still faster than the C++ Fast/Unsafe/PGO builds. Workload is uniformly random int32 below 1,000,000 (n=400,000), 50 iterations, copy included in the timing on both sides. LangArena describes itself as a subjective benchmark; the README says AI tools assisted translating tests between languages and that idiomatic constructs are used per language. One measurement per test and configuration (no variance reported), single machine, one monthly run. Rows were selected by the search agent as tests where the language beats every C/C++ configuration; most other tests in the suite go the other way. Ratios are derived from the results file, not stated by the suite. The benchmark suite itself is MIT-licensed (kostya/LangArena, 41 stars, last commit 2026-10-08). [retier] Enricher: the suite's own rows show the win is the stdlib algorithm, not Rust; Sort::Quick is at parity (Rust 1.145 s vs C/Gcc 1.15 s), Sort::Merge has Rust slower (1.621 s vs C/Clang 1.09 s), and Rust/WASM/Node (0.458 s) still beats native std::sort. The LCG has period 139,968, so the 400k keys are one sequence repeated about 2.86 times (both sides equally); driftsort allocates a 1.6 MB scratch buffer per call.

Rust's t.sort() is a stable sort and needs a scratch buffer (the suite's Rust memory 8.3 MB vs 8.6 MB for C++/G++). Using std::stable_sort or Rust sort_unstable would change the comparison.

## Maintenance

rust-lang/rust is active and dual-licensed MIT or Apache-2.0, and driftsort is the default since 1.81, so any current toolchain gets it; LangArena (MIT, 41 stars, monthly runs) calls itself a subjective benchmark and this row adds a third-party measurement of a standard-library algorithm win; no harness bug was found behind the numbers.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** Results file 2026-10-05-kostya-ms7c37.js has Sort::Self-runtime Rust 0.41 s vs C++/G++ 0.982 s (min over all 27 C/C++ configurations; C/qsort rows 1.957-2.207 s), with compiler versions (rustc 1.99.0, g++ 16.0.1, clang 22.1.8), build commands and CPU (Ryzen 7 3800X); code is public (rust/src/benchmarks/sort_self.rs, cpp/src/sort.cpp, c/src/sort.c) and flags are in cpp/Makefile and rust/Cargo.toml. Third-party suite, fully reproducible.
- **Verifier notes:** Numbers match the results file exactly (Rust 0.41 s, Rust/WMO 0.403 s, Rust/PGO 0.412 s; C++/G++ 0.982 s, C++/G++/Fast 0.998 s, C++/Clang++ 1.022 s, C/Clang 1.986 s; 2.4x derived). Same work on both sides, -O3 C++ builds included and slower, so not a crippled baseline; shortcoming: stable driftsort vs unstable introsort, win is the stdlib algorithm not the language, single run without variance. Driftsort confirmed from rust-lang/rust library/alloc/src/slice.rs.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-59 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-10-05-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/run.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/Makefile>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/rust/Cargo.toml>
  - <https://github.com/kostya/LangArena>
  - <https://github.com/kostya/LangArena/commits>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/rust/src/benchmarks/sort_self.rs>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/rust/src/benchmarks/sort_benchmark.rs>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/sort.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/src/sort.c>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/Makefile>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/test.js>
  - <https://github.com/rust-lang/rust>
  - <https://github.com/rust-lang/rust/commits>
  - <https://raw.githubusercontent.com/rust-lang/rust/HEAD/library/alloc/src/slice.rs>
- **Sources the enricher read:**
  - <https://github.com/kostya/LangArena>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/run.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-10-05-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/Makefile>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/sort.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/sort.hpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/helper.hpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/benchmark.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/src/sort.c>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/rust/Cargo.toml>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/rust/src/main.rs>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/rust/src/helper.rs>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/rust/src/benchmarks/sort_self.rs>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/rust/src/benchmarks/sort_benchmark.rs>
  - <https://raw.githubusercontent.com/rust-lang/rust/HEAD/library/alloc/src/slice.rs>
  - <https://raw.githubusercontent.com/rust-lang/rust/HEAD/library/core/src/slice/sort/stable/mod.rs>
  - <https://raw.githubusercontent.com/rust-lang/rust/HEAD/library/core/src/slice/sort/stable/drift.rs>
  - <https://raw.githubusercontent.com/rust-lang/rust/HEAD/library/core/src/slice/sort/stable/quicksort.rs>
  - <https://raw.githubusercontent.com/rust-lang/rust/HEAD/library/core/src/slice/sort/shared/smallsort.rs>
  - <https://github.com/rust-lang/rust/issues?q=is%3Aissue+driftsort>
  - <https://github.com/rust-lang/rust/issues/136103>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:rust/kostya/langarena#sort-self`) · [data/wave14/enrich/raw/lang_rust_kostya_langarena_sort_self.json](../../../data/wave14/enrich/raw/lang_rust_kostya_langarena_sort_self.json) (enrichment confidence 0.8)

</details>
