# fluxsort

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Sorting](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `Unlicense` · 🟡 stale

> Stable branchless quicksort/mergesort hybrid with a qsort-style C interface, claimed \~3x faster than std::stable_sort on random ints.

| | |
|---|---|
| **Beats** | std::stable_sort |
| **Claimed result** | \~3.2x faster than std::stable_sort on random-order 100K 32-bit ints (0.006113s vs 0.001906s, best-of-100); up to \~18x faster on ascending-order input (0.000804s vs 0.000044s). |
| **Workload** | Sorting 100,000 random 32-bit elements across many distributions (random, ascending, descending, sawtooth, pipe-organ, bit-reversal), best-of-100 runs. |
| **Metric** | throughput |
| **Compiler and flags** | g++ -O3 -w -fpermissive (GCC 7.5.0, WSL/Ubuntu 18.04) |
| **Adoption** | 749 stars |
| **Last commit** | 2024-07-27 |
| **Links** | [repository](https://github.com/scandum/fluxsort) · [benchmark](https://github.com/scandum/fluxsort#benchmarks) |

## Verdict

Author's own bench.c (wolfsort benchmark suite), compiled with g++ -O3 -w -fpermissive on GCC 7.5.0/Ubuntu 18.04 under WSL, hardware unstated: best-of-100 sorting 100,000 random 32-bit ints took 0.001906s for fluxsort vs 0.006113s for std::stable_sort (\~3.2x); on ascending-order input, 0.000044s vs 0.000804s (\~18x); 64-bit random ints were 0.002032s vs 0.006008s (\~3.0x).

## Use it when

- Stable sorting of primitive fixed-width integers, longs, or doubles (8/16/32/64-bit, long double) where you would otherwise use std::stable_sort
- Arrays from \~10K to 10M elements of random or partially-ordered data on x86-64/GCC, where extra O(n) scratch memory is affordable
- Data with exploitable structure - ascending/descending runs, sawtooth, pipe-organ patterns - where the analyzer gives the largest (10-18x) gains
- C/C++ code that can vendor a small C source drop and compile it with GCC -O3 (the author's tuned toolchain)
- Offline/batch sorting where a first-party-benchmarked throughput gain is sufficient evidence, not latency-critical or safety-certified code

## Skip it when

- You need the actual std::stable_sort C++ template API (iterators, allocators, arbitrary value types by move) - fluxsort is a C function with the qsort comparator contract, a code change, not a header swap
- Memory is constrained: fluxsort allocates n elements of swap memory (shared with quadsort); if allocation fails it silently falls back to quadsort's slower in-place rotations. Use blitsort (same author) for a true in-place stable sort
- Your comparator is subtraction-based (`a - b`) or otherwise not a strict, overflow-safe ordering - reported "bugs" (issue #10 buffer overflow, issue #4 stability failure) both turned out to be caller comparator mistakes, but they show how easy this footgun is to hit
- You need current, independently verified performance evidence: the project is stale (last commit 2024-07-27) and every published benchmark is first-party (author's own bench.c/wolfsort suite) on an old GCC 7.5.0/WSL toolchain with hardware unstated
- You're sorting only unsigned 32-bit ints at very large scale and can use radix sorting instead - the README itself says wolfsort (adaptive radix, same author) beats fluxsort on 8/16/32-bit types, and crumsort beats it if stability isn't required

## How it is fast

A top-down analyzer first checks for fully ordered/reversed runs and per-quarter presortedness, falling back to its sibling quadsort when a segment is mostly ordered. Partitioning is quicksort-style but partially in-place: elements &lt;=pivot are written back in place and elements &gt;pivot go to an auxiliary swap buffer, which cuts the branch-misprediction cost that plagues classic quicksort and gives memory-level parallelism on the writes. Pivots are chosen via a branchless quasimedian-of-9 (up to a median of 1024 for large partitions, an approximation of cbrt(n)), and partitions under 96 elements are sorted with quadsort's branchless small-array routine; a 1/16 partition-imbalance guard bounds the worst case to n log n.

## Compared with alternatives

Pick fluxsort over the unstable/radix/SIMD siblings (BlockQuicksort, IPS4o, x86-simd-sort, LearnedSort, poor-circle/radix_sort) when you need a stable, portable scalar C sort rather than raw unsigned-int throughput. Prefer quadsort itself, its stablemate, when the data has long ordered runs or is strings/objects (README: quadsort's branchless merge beats fluxsort there); fluxsort's edge is random or low-cardinality data plus the same qsort-style interface.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (fluxsort.h textually includes fluxsort.c and bundles quadsort.h/quadsort.c for the small-array/run fallback; all four files must sit in the same directory) |
| **Minimum toolchain** | Plain C (no version stated beyond needing stdlib.h/string.h/assert.h); author recommends compiling with gcc -O3 for the numbers claimed - the README's own clang-10 benchmark shows some fluxsort/quadsort routines 2-3x slower under clang |
| **Platforms** | any (portable C, no SIMD/intrinsics in the header); all published benchmarks are x86-64 (WSL/Ubuntu) |
| **Thread safety** | not documented - no shared/global state visible in fluxsort.h beyond per-call swap allocation, but concurrent use is never discussed |
| **Drop-in for the baseline** | partial — explain: matches C qsort(3)'s (array, nmemb, size, cmp) shape, not std::stable_sort's C++ template signature, so callers must switch call sites, not just link a different library |

## Gotchas

- Comparator must be a real strict ordering that returns a consistent sign for all inputs; `a - b`-style comparators on 64-bit values silently truncate/overflow to int and cause out-of-bounds writes or unstable results (reported as a fluxsort bug in issue #10, root-caused to the caller's comparator)
- fluxsort_prim only covers 32/64-bit signed/unsigned integers (size = sizeof(int) or sizeof(long long), +1 to select unsigned); anything else needs fluxsort_size with a by-reference comparator, same as sorting an array of pointers
- Falls back silently to quadsort (still stable, but in-place via rotations) if the swap-memory malloc fails - a correctness safety net that is also a silent performance cliff
- A closed 2024 issue shows a Rust-glue port mismapped its comparator into fluxsort's internal contract and produced an apparent stability failure; the C library itself is not the source of that bug, but it illustrates how fragile porting the comparator convention is

## Caveats and trade-offs

First-party benchmark suite (same author and suite as quadsort/wolfsort; code in src/bench.c). Hardware/CPU is not stated, and the toolchain is an old GCC 7.5.0 on WSL/Ubuntu 18.04. No peer-reviewed or independent benchmark against std::stable_sort was found; the Voultapher sort-research-rs writeups checked compare fluxsort only against Rust sorts.

Stable quicksort/mergesort hybrid, needs O(n) auxiliary memory; same GCC/x86-tuning caveats as its sibling quadsort.

## Maintenance

Stale (last commit 2024-07-27) but Unlicense (public-domain) makes it safe to freeze and vendor; the only known-good configuration is the author's GCC 7.5.0 -O3 toolchain, and no independent benchmark against std::stable_sort was found.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification B, tier now C.
- **Tier reason:** The README benchmarks table compares fluxsort vs std::stable_sort using the in-repo src/bench.c, compiled with g++ -O3 -w -fpermissive on GCC 7.5.0. Hardware is not stated, so tier A fails. The benchmark is first-party, with no peer-reviewed or independent third-party suite, so tier B fails.
- **Verifier notes:** Numbers verified exactly: random 32-bit 0.006113s vs 0.001906s (\~3.2x), ascending 0.000804s vs 0.000044s (\~18x). Random 64-bit is 0.006008s vs 0.002032s (\~3.0x). Record tier B was not supported, because the source is the author's own README. Metadata verified: Unlicense, 749 stars, not a fork, last commit 2024-07-27 (stale).
- **Fields the verifier corrected:** `caveats`
- **Pages the verifier opened:**
  - <https://github.com/scandum/fluxsort>
  - <https://github.com/scandum/fluxsort#benchmarks>
  - <https://github.com/Voultapher/sort-research-rs/blob/main/writeup/glidesort_perf_analysis/text.md>
  - <https://github.com/Voultapher/sort-research-rs/blob/main/writeup/driftsort_introduction/text.md>
- **Sources the enricher read:**
  - <https://github.com/scandum/fluxsort>
  - <https://github.com/scandum/fluxsort#benchmarks>
  - <https://raw.githubusercontent.com/scandum/fluxsort/main/README.md>
  - <https://github.com/scandum/fluxsort/blob/main/src/fluxsort.h>
  - <https://github.com/scandum/fluxsort/issues/10>
  - <https://github.com/scandum/fluxsort/issues/4>
  - <https://github.com/scandum/fluxsort/issues/9>
  - <https://github.com/scandum/fluxsort/issues/8>
  - <https://github.com/scandum/fluxsort/issues/5>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/scandum/fluxsort`) · [data/wave1/enrich/raw/github_com_scandum_fluxsort.json](../../../data/wave1/enrich/raw/github_com_scandum_fluxsort.json) (enrichment confidence 0.75)

</details>
