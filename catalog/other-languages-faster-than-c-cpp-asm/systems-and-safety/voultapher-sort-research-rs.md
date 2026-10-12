# ipnsort and driftsort (Rust std slice::sort_unstable and slice::sort)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Systems and safety](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `Apache-2.0` · 🟢 active

> Research home of ipnsort and driftsort, Rust's standard sorts since 1.81; ipnsort beats libstdc++ and libc++ std::sort on 10k u64.

| | |
|---|---|
| **Beats** | C++ standard library sorts: std::sort and std::stable_sort of libstdc++ and libc++ (benchmark variants cpp_std_gnu / cpp_std_libcxx in the repo) |
| **Claimed result** | Plot values in writeup/sort_safety/assets/unstable-hot-u64-10k.png (10k u64, hot, Zen 3, time in us): rust_ipnsort_unstable vs libstdc++ std::sort / libc++ std::sort: ascending 2.07 vs 49.3 / 6.23 (23.8x / 3.0x), descending 3.16 vs 32.2 / 11.4 (10.2x / 3.6x), random 77.0 vs 297.6 / 265.1 (3.9x / 3.4x), random_d20 24.3 vs 136.5 / 97.6 (5.6x / 4.0x), random_p5 12.4 vs 57.2 / 16.7 (4.6x / 1.35x), random_s95 83.4 vs 182.2 / 84.2 (2.2x / 1.01x), random_z1 56.8 vs 222.9 / 200.2 (3.9x / 3.5x) (ratios derived from page data). The text's 'current Rust standard library unstable sort ... outperforms the C++ standard library counterparts' refers to the pre-2024 pdqsort-based rust_std_unstable (random 136.9 us). Stable plot: driftsort is not tested; the then-current rust_std_stable beats libstdc++ std::stable_sort on random (253.0 vs 318.6 us) but loses on random_d20 (250.5 vs 190.5) and random_p5 (156.8 vs 69.8) and loses to libc++ on random, random_d20 and random_z1. |
| **Workload** | Sorting 10k u64 values with a hot cache across seven input patterns (ascending, descending, random, random_d20, random_p5, random_s95, random_z1) on Zen 3; unstable contestants include rust_ipnsort_unstable (research-repo commit 757478b) and the pre-2024 Rust std sorts vendored mid 2022; MSVC rows are listed but not in the Linux plots. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 5900X (Zen 3), Linux 6.5, CPU boost enabled |
| **Compiler and flags** | rustc 1.75.0-nightly (2023-10-03) with --release and lto=thin; C/C++ built through build.rs with opt_level(3) and -std=c++20 (-march=native only for the AVX2/AVX-512 contestants); clang 16.0.6 and gcc 13.2.1. The libstdc++ and libc++ variants are separate cargo features (cpp_std_sys, cpp_std_libcxx). |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Why it wins** | Newer algorithms than the introsort-style C++ std implementations: ipnsort (pattern-defeating quicksort lineage with a branchless cyclic Lomuto partition and small-sort networks) and driftsort (adaptive merge sort that falls back to quicksort for low-cardinality input); the author attributes the gap to old C++ implementations, not to the language. |
| **Adoption** | 545 stars; ipnsort and driftsort replaced the sorts in the Rust standard library (rust-lang/rust PR 124032) |
| **Last commit** | 2026-03-02 |
| **Links** | [repository](https://github.com/Voultapher/sort-research-rs) · [benchmark](https://raw.githubusercontent.com/Voultapher/sort-research-rs/main/writeup/sort_safety/text.md) |

## Verdict

On 10k u64 with a hot cache (Ryzen 9 5900X, rustc 1.75.0-nightly with thin LTO, C++ at -O3 -std=c++20), ipnsort sorted random input in 77.0 us vs 297.6 us for libstdc++ std::sort (gcc 13.2.1) and 265.1 us for libc++ std::sort (clang 16.0.6). Across seven patterns it was 2.2x to 23.8x faster than libstdc++ and 1.01x to 4.0x faster than libc++ (plot values, ratios derived from page data). driftsort was not part of the run.

## Use it when

- Rust code that sorts integer-like or small Copy keys: slice::sort_unstable is already ipnsort on Rust 1.81+, with the largest measured gains on low-cardinality (random_d20: 24.3 us vs 136.5/97.6) and Zipfian inputs.
- Generic sorts with user comparators where a buggy Ord must not cause memory unsafety: ipnsort is Ord-, panic- and observation-safe and usually panics on a detected strict-weak-order violation.
- Sorting already ascending or descending data: ipnsort does N-1 comparisons (2.07 us vs 49.3 us for libstdc++ std::sort on 10k ascending u64).
- As a design reference for a C or C++ port, or when choosing a C++ replacement: the same plot shows C++ pdqsort and C crumsort recover most of the gap over std::sort.

## Skip it when

- Inside C++ code: there is no C/C++ interface, so you would need Rust FFI or a port; pdqsort, crumsort or vqsort in C/C++ are the practical substitutes.
- Append-then-sort (random_s95): ipnsort ties libc++ std::sort (83.4 vs 84.2 us) and is about 5x slower than crumsort (16.9 us), because it scans 95% of the input before giving up on the already-sorted check.
- Maximum integer throughput: the authors list SIMD sorts (vqsort with AVX2+ and Clang), radix or counting sorts for small keys, and multithreading for multi-millisecond sorts as faster options outside its design goals.
- Code whose Ord is inconsistent: since Rust 1.81 the new sorts may panic on non-total orders where the old ones silently returned unsorted data.
- Memory-tight stable sorts: driftsort allocates an N-element buffer up to 8 MB and N/2 beyond; there is no published driftsort-versus-C++ stable_sort measurement in this repo.

## How it is fast

ipnsort keeps the pdqsort skeleton (quicksort with ancestor-pivot equal-element filtering, so K distinct values cost O(N log K)) but adds a single-pass already-sorted/reversed scan, glidesort's recursive sqrt(N) median pivot, a branchless cyclic Lomuto partition for small types, sorting-network plus bidirectional-merge small-sorts, and a branchless heapsort fallback at depth 2\*log2(N). It aims at instruction-level parallelism, not SIMD, so it stays generic over Ord and user comparators. driftsort combines glidesort-style run detection and lazy merging with a branchless stable quicksort partition and a branchless merge. The author puts the gap down to older C++ std implementations, not to the language: C++ pdqsort (144.4 us on random) matches the old pdqsort-based Rust sort (136.9 us).

## Compared with alternatives

This is the primary source behind the sibling 'Rust slice::sort (LangArena Sort::Self) vs C++ std::sort' entry (driftsort, 0.41 s vs 0.982 s). That sibling supplies the third-party C++ comparison of driftsort that this repo lacks, while this entry adds per-pattern ipnsort-versus-std::sort numbers with published flags. Prefer it over the Zig std.sort.pdq sibling when the code is Rust; neither helps a C++ codebase without a port.

## Integration

| | |
|---|---|
| **Form** | module (Rust standard library slice::sort / sort_unstable since 1.81.0); research copy is a path crate (ipnsort/) in this repo, not on crates.io |
| **Dependencies** | none (ipnsort is no_std without alloc; driftsort needs alloc for its buffer) |
| **Minimum toolchain** | Rust 1.81.0 for the std versions; the research repo builds on nightly (specialization in src/ffi_util.rs; the benchmark used rustc 1.75.0-nightly 2023-10-03) |
| **Platforms** | any Rust target; no architecture-specific code (designed and tuned for rustc with LLVM only) |
| **Thread safety** | single-threaded in-place sort of a &mut slice; no internal parallelism |
| **Drop-in for the baseline** | partial: drop-in only as Rust's own slice::sort_unstable/sort; not callable from C++ in place of std::sort without FFI or a port |

## Gotchas

- Harness checked, no flaw found: the C++ rows call std::sort/std::stable_sort with the default operator&lt; once per sort through extern "C" (src/cpp/cpp_std_sort.cpp), Criterion iter_batched_ref regenerates input each iteration (switched from iter_batched in commit e698b65 after issue #13, before this 2023-10 run), and the thread is pinned to one core; no contestant used -march=native. The libstdc++ variant uses the cc crate's default C++ compiler (gcc 13.2.1), the libc++ variant clang 16.0.6 with -stdlib=libc++.
- The baselines are old: LLVM 16 libc++ std::sort predates the bitsetsort-derived rewrite (LLVM 17), which the writeup calls untested; only hot-cache 10k u64 on one Zen 3 box was measured, and the ipnsort tested (commit 757478b) predates the code merged into std in June 2024.
- Doc mismatch: the writeup says random_d20 is 0..=20, but benches/bench.rs builds it with random_uniform(len, 0..20).
- Stable half: the plot shows the 2022 Rust merge sort, not driftsort; it loses to libstdc++ std::stable_sort on random_d20 and random_p5 and to libc++ on random, random_d20 and random_z1. glidesort, driftsort's ancestor, beats both C++ stable sorts on every pattern except random_p5 against libstdc++ (74.1 vs 69.8 us).

## Known shortcomings

- Plot readings give ipnsort 1.01x to 23.8x over libstdc++ and libc++ std::sort while driftsort is not benchmarked against C++; the old Rust stable sort is slower than the C++ stable sorts on 2-3 of 7 patterns; the win comes from the algorithm, not the language.
- Identity kept by override: a numerics-and-arrays copy from w14-num-gh-any took the bare id at merge; the verified claim is the systems-and-safety one (batch-08).
- Harness read end to end, no flaw: C++ std::sort is called once per sort through FFI with the default operator&lt;, fresh input each iteration (iter_batched_ref since e698b65), core pinned, no -march=native on either side; the plot values are confirmed. Driftsort was never measured against C++ (the 2022 Rust stable sort loses on 2-3 patterns); the libc++ baseline is LLVM 16, before the bitsetsort rewrite; ipnsort ties libc++ on random_s95 and loses 5x to crumsort; no crate, Rust 1.81+ only. Doc mismatch: random_d20 is 0..20 in code and 0..=20 in the write-up.

## Caveats and trade-offs

Bias disclaimer: the ipnsort author wrote the analysis. Only 10k u64 on one CPU with 2023 toolchains (rustc 1.75 nightly, gcc 13.2.1, clang 16.0.6); the bitsetsort-derived libc++ std::sort of LLVM 17 is 'so far untested'. Driftsort (today's slice::sort) does not appear in this benchmark or in any C++ comparison found (the driftsort and ipnsort introductions compare only against Rust sorts), so the stable half of the record has no evidence against C++; the Rust stable sort shown (rust_std_stable, vendored mid 2022) is slower than libstdc++ std::stable_sort on random_d20 and random_p5 and slower than libc++ on random, random_d20 and random_z1. The ipnsort tested is the research-repo version at 757478b, not necessarily the code merged into std by rust-lang/rust PR 124032 (merged 2024-06-20). The win is algorithmic, not a Rust language effect: C++ pdqsort (144.4 us random) matches the pdqsort-based rust_std_unstable (136.9 us) and C crumsort (95.6 us) is close to ipnsort (77.0 us). ipnsort roughly ties libc++ on random_s95 (83.4 vs 84.2 us). Neither side uses -march=native for these contestants. [retier] Harness checked: C++ std::sort called once per sort through FFI with the default operator&lt;, fresh input each iteration, core pinned, no -march=native on either side. Driftsort was never measured against C++; the libc++ baseline is LLVM 16, before the bitsetsort rewrite; ipnsort ties libc++ on random_s95 and loses 5x to crumsort; Rust 1.81+ only. random_d20 is 0..20 in code and 0..=20 in the write-up.

Generic over Ord with arbitrary user comparators; written with a lot of unsafe Rust for code-gen reasons but designed to avoid UB on non-strict-weak orderings and panics (the writeup's Ord and exception safety analysis). Needs Rust; stable sort needs auxiliary memory.

## Maintenance

Research repo is active (last commit 2026-03-02, Apache-2.0); the production code lives in rust-lang/rust and is maintained there, so it is copyable in principle but in practice usable only from Rust 1.81+.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification A, tier now A.
- **Tier reason:** A for ipnsort: writeup/sort_safety/text.md states rustc 1.75.0-nightly, clang 16.0.6, gcc 13.2.1, Ryzen 9 5900X, links build.rs at commit 190b3ec (C++ opt_level(3), -std=c++20; Rust --release, lto=thin), the bench code (benches/, src/cpp/cpp_std_sort.cpp calling std::sort(data, data+len) with the default comparator for u64) is public, and the plot labels give per-pattern times. Claim narrowed: driftsort is not in this benchmark and the then-current Rust stable sort loses to the C++ stable sorts on several patterns.
- **Verifier notes:** Downgraded for an overstated claim, tier stays A for ipnsort: per-pattern numbers are readable on the plots (ipnsort 1.0x to 23.8x faster than libstdc++/libc++ std::sort), but driftsort is absent and the then-current Rust stable sort is slower than the C++ stable sorts on 2-3 of 7 patterns. Consider a name override to ipnsort (Rust std slice::sort_unstable) or a shortcoming saying driftsort has no C++ comparison. Metadata confirmed: 545 stars, Apache-2.0, last commit 2026-03-02 (active); rust-lang/rust PR 124032 merged 2024-06-20 replacing slice::sort with driftsort and sort_unstable with ipnsort.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-08 (wave 14); orchestrator (wave 14 merge); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/Voultapher/sort-research-rs/main/writeup/sort_safety/text.md>
  - <https://raw.githubusercontent.com/Voultapher/sort-research-rs/main/writeup/sort_safety/assets/unstable-hot-u64-10k.png>
  - <https://raw.githubusercontent.com/Voultapher/sort-research-rs/main/writeup/sort_safety/assets/stable-hot-u64-10k.png>
  - <https://raw.githubusercontent.com/Voultapher/sort-research-rs/190b3ec27f616c139370285b2b8534d1c5eaec1b/build.rs>
  - <https://raw.githubusercontent.com/Voultapher/sort-research-rs/190b3ec27f616c139370285b2b8534d1c5eaec1b/src/cpp/cpp_std_sort.cpp>
  - <https://raw.githubusercontent.com/Voultapher/sort-research-rs/190b3ec27f616c139370285b2b8534d1c5eaec1b/Cargo.toml>
  - <https://raw.githubusercontent.com/Voultapher/sort-research-rs/main/writeup/driftsort_introduction/text.md>
  - <https://raw.githubusercontent.com/Voultapher/sort-research-rs/main/writeup/ipnsort_introduction/text.md>
  - <https://raw.githubusercontent.com/Voultapher/sort-research-rs/main/writeup/intel_avx512/text.md>
  - <https://raw.githubusercontent.com/Voultapher/driftsort/main/README.md>
  - <https://github.com/Voultapher/sort-research-rs>
  - <https://github.com/Voultapher/sort-research-rs/commits/main>
  - <https://github.com/rust-lang/rust/pull/124032>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/Voultapher/sort-research-rs/main/README.md>
  - <https://raw.githubusercontent.com/Voultapher/sort-research-rs/main/writeup/sort_safety/text.md>
  - <https://raw.githubusercontent.com/Voultapher/sort-research-rs/main/writeup/sort_safety/assets/unstable-hot-u64-10k.png>
  - <https://raw.githubusercontent.com/Voultapher/sort-research-rs/main/writeup/sort_safety/assets/stable-hot-u64-10k.png>
  - <https://raw.githubusercontent.com/Voultapher/sort-research-rs/main/writeup/ipnsort_introduction/text.md>
  - <https://raw.githubusercontent.com/Voultapher/sort-research-rs/main/writeup/driftsort_introduction/text.md>
  - <https://raw.githubusercontent.com/Voultapher/sort-research-rs/main/Cargo.toml>
  - <https://raw.githubusercontent.com/Voultapher/sort-research-rs/main/build.rs>
  - <https://raw.githubusercontent.com/Voultapher/sort-research-rs/main/src/cpp/cpp_std_sort.cpp>
  - <https://raw.githubusercontent.com/Voultapher/sort-research-rs/main/src/cpp/shared.h>
  - <https://raw.githubusercontent.com/Voultapher/sort-research-rs/main/src/ffi_util.rs>
  - <https://raw.githubusercontent.com/Voultapher/sort-research-rs/main/src/unstable/cpp_std_sys.rs>
  - <https://raw.githubusercontent.com/Voultapher/sort-research-rs/main/src/unstable/rust_ipnsort.rs>
  - <https://raw.githubusercontent.com/Voultapher/sort-research-rs/main/src/unstable/mod.rs>
  - <https://raw.githubusercontent.com/Voultapher/sort-research-rs/main/src/unstable/c_idisort.rs>
  - <https://raw.githubusercontent.com/Voultapher/sort-research-rs/main/src/cpp/c_idisort.cpp>
  - <https://raw.githubusercontent.com/Voultapher/sort-research-rs/main/src/cpp/idisort/qsort.h>
  - <https://raw.githubusercontent.com/Voultapher/sort-research-rs/main/benches/bench.rs>
  - <https://raw.githubusercontent.com/Voultapher/sort-research-rs/main/benches/modules/sort.rs>
  - <https://raw.githubusercontent.com/Voultapher/sort-research-rs/main/benches/modules/util.rs>
  - <https://raw.githubusercontent.com/Voultapher/sort-research-rs/main/benches/modules/mod.rs>
  - <https://github.com/Voultapher/sort-research-rs/tree/main/src>
  - <https://github.com/Voultapher/sort-research-rs/tree/main/src/unstable>
  - <https://github.com/Voultapher/sort-research-rs/tree/main/benches/modules>
  - <https://github.com/Voultapher/sort-research-rs/tree/main/src/cpp/idisort>
  - <https://github.com/Voultapher/sort-research-rs/issues?q=is%3Aissue>
  - <https://github.com/Voultapher/sort-research-rs/issues/13>
  - <https://raw.githubusercontent.com/Voultapher/driftsort/main/README.md>
  - <https://raw.githubusercontent.com/rust-lang/rust/master/RELEASES.md>
  - <https://github.com/rust-lang/rust/pull/124032>
  - <https://crates.io/api/v1/crates/driftsort>
  - <https://crates.io/api/v1/crates/ipnsort>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/voultapher/sort-research-rs`) · [data/wave14/enrich/raw/github_com_voultapher_sort_research_rs.json](../../../data/wave14/enrich/raw/github_com_voultapher_sort_research_rs.json) (enrichment confidence 0.75)

</details>
