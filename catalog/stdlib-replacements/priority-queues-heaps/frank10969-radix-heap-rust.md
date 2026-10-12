# RadixHeap (radix_heap_rust)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Priority queues and heaps](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0` · 🟢 active

> Monotone bucket-based radix heap for Rust; \~1.7-2x faster than std BinaryHeap&lt;Reverse&lt;u32&gt;&gt; for large random u32 heapsort.

| | |
|---|---|
| **Beats** | Rust std::collections::BinaryHeap (with Reverse) |
| **Claimed result** | \~1.7-2x faster than BinaryHeap across sizes: 1M elems \~180ms vs \~320ms; 8M \~1.6s vs \~3.0s; 64M \~15s vs \~28s. |
| **Workload** | Criterion benchmark: push N uniformly random u32 keys, then pop all of them (heapsort pattern), N = 125,000 &lt;&lt; i for i in 0..10 (125K-64M), vs Rust std::collections::BinaryHeap&lt;Reverse&lt;u32&gt;&gt;. |
| **Metric** | throughput |
| **Hardware** | "mid-range desktop CPU" (exact model not stated) |
| **Adoption** | 0 stars |
| **Last commit** | 2026-05-14 |
| **Links** | [repository](https://github.com/Frank10969/radix_heap_rust) · [benchmark](https://github.com/Frank10969/radix_heap_rust) |

## Verdict

The project's own Criterion benchmark (benches/benchmark.rs) pushes N random u32 keys then pops all of them (N = 125,000 &lt;&lt; i, i in 0..10, i.e. 125K-64M) against std::collections::BinaryHeap&lt;Reverse&lt;u32&gt;&gt;, on an unspecified 'mid-range desktop CPU' with no compiler version or flags stated; reported totals: 1M \~180ms vs \~320ms, 8M \~1.6s vs \~3.0s, 64M \~15s vs \~28s (\~1.7-2x faster).

## Use it when

- Dijkstra / SSSP or other monotone-extraction graph algorithms where extracted keys are non-decreasing
- Fixed-width integer keys (u8-u128, i8-i128, usize/isize) or f32/f64, large N (millions), push-all-then-pop-all or monotone-interleaved throughput workloads
- Rust code currently doing BinaryHeap&lt;Reverse&lt;K&gt;&gt; for a min-heap and able to change call sites, not just imports
- Willing to accept a hard panic (not a Result) as the failure mode if a non-monotone key is ever pushed
- OK vendoring a small (4-file), unaudited, non-1.0 crate rather than depending on a maintained package

## Skip it when

- General-purpose priority queue where later-pushed keys can be smaller than an already-popped minimum (this panics; BinaryHeap just works)
- You need BinaryHeap's API surface: peek_mut, into_sorted_vec, iterator support, From&lt;Vec&gt;, etc. -- none exist here
- Non-numeric or custom key types beyond what you're willing to hand-implement Key (xor + position_of_highest_set_bit) for yourself
- Multi-threaded/concurrent access -- no Sync/Send or synchronization documented or present in source
- Production reliance on correctness/maintenance guarantees: 0-star, two-author WS2023/24 university coursework crate with no releases

## How it is fast

Classic radix-heap bucketing: on push, the key is XORed with the last-extracted minimum and the position of the highest differing bit picks a bucket (RadixHeap::get_bucket_to_insert_into in src/heap.rs), so push is an O(1) append with no per-element comparisons against existing heap contents, unlike BinaryHeap's O(log n) sift. pop scans for the first nonempty bucket and, only when it isn't bucket 0, redistributes that bucket's elements into finer buckets (rearrange()) before returning the true minimum (tracked per-bucket via a real `<` comparison, not the XOR trick). For fixed-width integers the bit range is a small constant (e.g. 32 for u32), making amortized pop cost effectively O(1) in practice.

## Compared with alternatives

Pick this over prio_queue (rollbear) or pair_radix_heap when you're in Rust, not C++ (those are C++-only). Versus SimdQuickHeap, the other Rust sibling beating the same BinaryHeap baseline, SimdQuickHeap reports far larger per-element speedups (\~12-14x, AVX2/AVX512) and isn't monotone-restricted, so prefer this crate only when you specifically want the simpler bucket/XOR radix-heap technique for a Dijkstra-style monotone workload without SIMD or nightly-feature requirements.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | rand 0.8.5 (runtime); proptest 1.3.1 and criterion 0.5 (dev-only, for tests/benches) |
| **Minimum toolchain** | Rust 2021 edition (Cargo.toml edition = "2021"); exact MSRV not documented |
| **Platforms** | not documented; pure safe Rust with no unsafe blocks, no SIMD intrinsics, and no arch-specific code observed in heap.rs, bucket.rs, or key.rs |
| **Thread safety** | not documented -- no Sync/Send impls or synchronization in the source read |
| **Drop-in for the baseline** | partial -- explain: same conceptual push/pop shape as BinaryHeap&lt;Reverse&lt;K&gt;&gt; but a distinct type with a smaller method set and an added monotonicity precondition BinaryHeap doesn't have, so call sites must change, not just the import |

## Gotchas

- push() panics with "Invalid Key" (not a Result/Option) if the key is smaller than the last-extracted minimum -- a crash risk if input isn't guaranteed monotone
- f32/f64 support XORs raw IEEE-754 bit patterns via to_bits() with no separate sign-order transform; verified only by two fixed 5-element unit tests (f32, f64) -- the proptest random-key property test covers only u32, not floats
- LICENSE file in the repo is Apache-2.0, while Cargo.toml and the README both declare MIT -- check which actually applies before vendoring
- A compiled binary (src/main.exe) is committed to the repo alongside src/main.rs, suggesting light packaging/CI hygiene

## Caveats and trade-offs

A university course project (README says Programming in Rust WS 2023/24, two authors, 0 stars). The benchmark is the project's own Criterion suite, with approximate '\~' README numbers, no stated CPU model and no compiler flags. It compares only against Rust's std BinaryHeap, never against C++ std::priority_queue. The license is inconsistent: the LICENSE file is Apache-2.0, while the README and Cargo.toml say MIT (both are OSI).

Monotone-only: panics if a pushed key is smaller than the last-extracted minimum, so it cannot be a drop-in replacement for std::priority_queue in general use -- only in monotone-extraction algorithms like Dijkstra. Fixed-width integer/float keys only.

## Maintenance

Last commit 2026-05-14 (active by date) but is a two-author WS2023/24 university coursework project with 0 stars, 0 forks, and no tagged releases beyond Cargo.toml's 0.1.0; small and dependency-light enough to vendor, but treat as unaudited/unmaintained-risk rather than a supported package.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The README's 'Example results' table (1M \~180ms vs \~320ms, 8M \~1.6s vs \~3.0s, 64M \~15s vs \~28s, '\~1.7-2x faster') comes from the project's own Criterion benchmark (benches/benchmark.rs) against Rust std BinaryHeap. The CPU is only described as a 'mid-range desktop CPU' and no compiler version or flags are given, so it is first-party with partial methodology: C.
- **Verifier notes:** The numbers match the README. The workload was corrected: the benchmark is push-all-then-pop-all, not interleaved. The license is kept as Apache-2.0 because that is what the LICENSE file and GitHub say, and the MIT conflict is noted in caveats.
- **Fields the verifier corrected:** `baseline`, `baseline_in_list`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/Frank10969/radix_heap_rust>
- **Sources the enricher read:**
  - <https://github.com/Frank10969/radix_heap_rust>
  - <https://github.com/Frank10969/radix_heap_rust/blob/main/README.md>
  - <https://github.com/Frank10969/radix_heap_rust/blob/main/Cargo.toml>
  - <https://github.com/Frank10969/radix_heap_rust/blob/main/LICENSE>
  - <https://github.com/Frank10969/radix_heap_rust/blob/main/benches/benchmark.rs>
  - <https://github.com/Frank10969/radix_heap_rust/blob/main/src/heap.rs>
  - <https://github.com/Frank10969/radix_heap_rust/blob/main/src/bucket.rs>
  - <https://github.com/Frank10969/radix_heap_rust/blob/main/src/key.rs>
  - <https://github.com/Frank10969/radix_heap_rust/blob/main/src/lib.rs>
  - <https://api.github.com/repos/Frank10969/radix_heap_rust>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/frank10969/radix_heap_rust`) · [data/wave1/enrich/raw/github_com_frank10969_radix_heap_rust.json](../../../data/wave1/enrich/raw/github_com_frank10969_radix_heap_rust.json) (enrichment confidence 0.5)

</details>
