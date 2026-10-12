# SimdQuickHeap

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Priority queues and heaps](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `MIT` · 🟢 active

> SIMD-accelerated Rust priority queue, \~12x faster than std::collections::BinaryHeap on large monotone-key workloads; i32/u32/i64/u64 only.

| | |
|---|---|
| **Beats** | Rust std::collections::BinaryHeap |
| **Claimed result** | Table 1, MonotoneConstantSize, i64 keys, n=2^25: SimdQuickHeapAvx2 35.6 ns/elem and SimdQuickHeapAvx512 32.2 ns/elem vs Rust std BinaryHeap 439.6 ns/elem, i.e. \~12.3x and \~13.7x (derived from page data). At small n (2^10) the gap is small: 27.1 / 23.5 vs 27.4 ns/elem. Abstract: 1.2-1.7x as fast as the monotone radix heap (the next-best competitor) and 1.4-2.8x as fast as the superscalar sample queue (S3Q). The README says up to 10x faster than binary and d-ary heaps. |
| **Workload** | MonotoneConstantSize workload, i64 keys, n=2^25: build heap via (push∘pop∘push)^n, then 10n interleaved pop/push operations with monotone-increasing keys, timed per element. |
| **Metric** | throughput |
| **Hardware** | AMD Zen 4 EPYC 9684X (92 cores, 32 KiB L1d, 1 MiB L2, 32+64 MiB L3 per 8-core package), 12-channel DDR5, Rocky Linux 9.4 |
| **Compiler and flags** | C++ competitors: Clang, -std=c++17 -O3 -DNDEBUG -march=native -flto. Rust: release mode, target-cpu=native, full LTO, single codegen unit. |
| **Adoption** | 35 stars |
| **Last commit** | 2026-08-26 |
| **Links** | [repository](https://github.com/RagnarGrootKoerkamp/quickheap) · [benchmark](https://arxiv.org/abs/2604.25681) |

## Verdict

On an AMD EPYC 9684X (Zen4), Rust nightly release build (target-cpu=native, fat LTO, single codegen unit), the paper's Table 1 shows SimdQuickHeapAvx2 at 35.6 ns/elem and Avx512 at 32.2 ns/elem versus Rust std::collections::BinaryHeap at 439.6 ns/elem (\~12.3x / \~13.7x) on a monotone-key push/pop workload at n=2^25; the gap shrinks to near-parity at n=2^10. No C++ std::priority_queue was benchmarked -- only Rust's BinaryHeap and several C++ competitors (Boost.Heap, S3Q, radix heap, original QuickHeap) via LLM-generated FFI wrappers.

## Use it when

- Priority queue over i32/u32/i64/u64 keys, large enough to exceed cache (paper's gains are at n=2^25; negligible at n=2^10)
- x86-64 with AVX2 or AVX-512 available at compile time (target-cpu=native / -march=native)
- Monotone or near-sorted key sequences (Dijkstra-like, event queues, radix-heap-style workloads) -- where the paper's largest wins are shown
- Rust code that can pin to nightly (crate currently requires it) and can vendor a small, very new, unaudited crate
- C++ code able to build and statically/dynamically link a Rust cdylib and accept LLM-generated, unreviewed FFI bindings for a throughput win over a naive priority_queue

## Skip it when

- Keys can equal the type's MAX value (e.g. u64::MAX): open issue #6 shows pop() can silently return the wrong element because MAX is used internally as an empty-slot sentinel
- Need arbitrary Ord types, custom comparators, decrease-key, iteration, or merge -- only 4 fixed integer types and push/pop are supported
- No AVX2/AVX-512 target, or a stable-Rust-only build (crate needs nightly; issue #3 tracks moving off portable-simd)
- Heap stays small enough to fit in cache: measured advantage over BinaryHeap collapses to near-parity at n=2^10
- Need a mature, widely audited dependency: 35 stars, first public benchmark paper (ESA 2026, arXiv Sept 2026) with no independent replication, and an open correctness bug

## How it is fast

Uses QuickSelect-style recursive partitioning of elements into buckets by pivot (median-of-3 by default), keeping only the bottom bucket sorted once it drops below a size threshold (N=16), so most of the heap stays partitioned rather than fully ordered. Partitioning and insertion use SIMD (AVX2, or AVX-512 when compiled in) to compare and move several keys per instruction. This avoids the pointer-chasing and cache misses of array/pointer-based binary heaps once the queue exceeds L2/L3 cache, matching the paper's finding that the gap over BinaryHeap is huge at n=2^25 and nearly gone at n=2^10.

## Compared with alternatives

Pick this over prio_queue (rollbear) or radix-heap when working in Rust against std::collections::BinaryHeap with one of the four supported integer key types and a large, cache-exceeding, monotone-ish workload; it is the only sibling using SIMD partitioning and the only one benchmarked directly against S3Q and monotone radix heaps (1.2-2.8x, more representative than the \~12x BinaryHeap figure). Prefer RadixHeap (radix_heap_rust) instead if you need stable-Rust maturity over a nightly-only crate with an open correctness bug.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | Rust: ensure_simd 0.1, rand 0.10, wide 1.2. C++ bindings: none beyond the compiled libquickheap.{so,dylib,a} plus quickheap.h/quickheap.hpp. |
| **Minimum toolchain** | Rust nightly (rust-toolchain.toml pins channel = "nightly"); C++17 for the bindings example |
| **Platforms** | x86-64 only; AVX2 or AVX-512 required at compile time. No other architectures documented. |
| **Thread safety** | not documented -- push/pop take &mut self, no Send/Sync mentioned, implying single-threaded/exclusive-access use like std::collections::BinaryHeap |
| **Drop-in for the baseline** | partial -- explain: same push/pop min-heap semantics as BinaryHeap, but restricted to 4 integer key types and missing iterator/peek/into_sorted_vec/generic-Ord support; the C++ wrapper is a separate hand-written class, not a std::priority_queue specialization. |

## Gotchas

- Pushing the type's MAX value (e.g. u64::MAX) can corrupt later pop() results -- MAX is used as an internal empty-slot sentinel (issue #6, open, unresolved as of 2026-09-02)
- No LICENSE file in the repo (GitHub reports license: null); MIT is declared only via Cargo.toml's license field
- Requires nightly Rust today; issue #3 (open) tracks replacing portable-simd with the stable `wide` crate
- C++ bindings are explicitly LLM-generated and unreviewed; authors recommend building with panic="abort" so a Rust panic can't unwind across the FFI boundary

## Caveats and trade-offs

Published at ESA 2026 (DOI 10.4230/LIPIcs.ESA.2026.16); very recent, with no independent replication yet. The largest multiplier is against Rust's own BinaryHeap, not libstdc++/libc++/MSVC std::priority_queue (C++ std::priority_queue was not tested; Boost 4-ary heap was). The speedup is small while the heap fits in cache. It supports only i32/u32/i64/u64 keys, needs AVX2 or AVX-512, and the benchmarks need nightly Rust. The C++ bindings are LLM-generated. The repo has no LICENSE file: MIT is declared only in Cargo.toml.

The 12-13x figure is on a monotone-key workload engineered to be near-degenerate for comparison-based heaps; the general win over the next-best rival (S3Q) is a more modest 1.4-2.8x. Needs AVX2/AVX512 for full speed. No run against an actual GCC/Clang/MSVC std::priority_queue was performed -- only against Rust's std::collections::BinaryHeap and several boost::heap variants.

## Maintenance

Actively maintained (last commit 2026-08-26) but very new (ESA 2026 paper, 35 stars) with an open, unresolved correctness bug on MAX-valued keys; usable as a copyable/vendorable crate, but MIT is only declared in Cargo.toml, not backed by a checked-in LICENSE file.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** The paper's Table 1 (arXiv v3 / ESA 2026) gives BinaryHeap 439.6 vs SimdQuickHeapAvx2 35.6 vs Avx512 32.2 ns/elem at n=2^25, and the abstract gives the radix-heap and S3Q ratios. The benchmark code is public (bench/examples/bench.rs via run-all.sh). Rust is built nightly, release, target-cpu=native, fat LTO; C++ competitors use Clang -std=c++17 -O3 -DNDEBUG -march=native -flto; the CPU is an AMD EPYC 9684X. The baseline actually run is Rust's std::collections::BinaryHeap.
- **Verifier notes:** The numbers match the paper exactly; the ratios just needed a 'derived' label. The baseline was relabeled to Rust's BinaryHeap because std::priority_queue itself was never benchmarked. GitHub reports no license (spdx null), but Cargo.toml declares license = "MIT", so it is kept as MIT/copyable with a caveat.
- **Fields the verifier corrected:** `baseline`, `baseline_in_list`, `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/abs/2604.25681>
  - <https://arxiv.org/pdf/2604.25681v3>
  - <https://github.com/RagnarGrootKoerkamp/quickheap>
- **Sources the enricher read:**
  - <https://github.com/RagnarGrootKoerkamp/quickheap>
  - <https://github.com/RagnarGrootKoerkamp/quickheap/blob/master/README.md>
  - <https://github.com/RagnarGrootKoerkamp/quickheap/blob/master/Cargo.toml>
  - <https://github.com/RagnarGrootKoerkamp/quickheap/blob/master/src/lib.rs>
  - <https://github.com/RagnarGrootKoerkamp/quickheap/blob/master/cpp/README.md>
  - <https://github.com/RagnarGrootKoerkamp/quickheap/blob/master/rust-toolchain.toml>
  - <https://github.com/RagnarGrootKoerkamp/quickheap/issues/6>
  - <https://github.com/RagnarGrootKoerkamp/quickheap/issues>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/ragnargrootkoerkamp/quickheap`) · [data/wave1/enrich/raw/github_com_ragnargrootkoerkamp_quickheap.json](../../../data/wave1/enrich/raw/github_com_ragnargrootkoerkamp_quickheap.json) (enrichment confidence 0.8)

</details>
