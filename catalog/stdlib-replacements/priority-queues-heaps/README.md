# Priority queues and heaps

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md)</sub>

**What these beat:** std::priority_queue, std::make_heap  
**5 entries:** 4 tier A · 0 tier B · 1 tier C · 0 tier D · 5 copyable, 0 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**SimdQuickHeap**](ragnargrootkoerkamp-quickheap.md) | SIMD-accelerated Rust priority queue, \~12x faster than std::collections::BinaryHeap on large monotone-key workloads; i32/u32/i64/u64 only. | **A** | Rust | MIT | 🟢 active |
| 2 | [**Superscalar Sample Queue (S3Q)**](raphinesse-s3q.md) | Header-only C++17 cache-efficient priority queue beating std::priority_queue via batched, sample-sort-style bucket classification. | **A** | C++ | MIT | 🟢 active |
| 3 | [**prio_queue (rollbear)**](rollbear-prio-queue.md) | Header-only B-heap priority queue storing priority/payload in separate arrays; faster than std::priority_queue on cache-friendly workloads. | **A** | C++ | BSL-1.0 | 🟡 stale |
| 4 | [**radix-heap (pair_radix_heap)**](iwiwi-radix-heap.md) | Header-only C++ monotone radix heap: 1.2-1.7x faster than std::priority_queue on Dijkstra shortest-path workloads. | **A** | C++ | MIT | 🔴 abandoned |
| 5 | [**RadixHeap (radix_heap_rust)**](frank10969-radix-heap-rust.md) | Monotone bucket-based radix heap for Rust; \~1.7-2x faster than std BinaryHeap&lt;Reverse&lt;u32&gt;&gt; for large random u32 heapsort. | **C** | Rust | Apache-2.0 | 🟢 active |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
