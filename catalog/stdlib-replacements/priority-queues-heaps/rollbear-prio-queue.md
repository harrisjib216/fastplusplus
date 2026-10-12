# prio_queue (rollbear)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Priority queues and heaps](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `BSL-1.0` · 🟡 stale

> Header-only B-heap priority queue storing priority/payload in separate arrays; faster than std::priority_queue on cache-friendly workloads.

| | |
|---|---|
| **Beats** | std::priority_queue |
| **Claimed result** | "always faster than std::priority_queue&lt;int&gt;" across all tested mini-heap sizes, and "consistently much faster than std::priority_queue&lt;std::pair&lt;int,int&gt;&gt;" when priority and payload are stored in separate arrays; exact ratios are shown only in the post's benchmark graphs, not stated as numeric text |
| **Workload** | 320 push + 320 pop cycles of random values at increasing queue sizes, comparing a cache-friendly B-heap layout (mini-heap sizes 8/16/32/64) against std::priority_queue&lt;int&gt; and std::priority_queue&lt;pair&lt;int,int&gt;&gt; |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-4500U, Ubuntu 15.04, 32KB L1d cache, 64-byte cache lines |
| **Compiler and flags** | g++ 4.9.3, -O3 -std=c++14 |
| **Adoption** | 111 stars |
| **Last commit** | 2025-09-18 |
| **Links** | [repository](https://github.com/rollbear/prio_queue) · [benchmark](https://playfulprogramming.blogspot.com/2015/08/cache-optimizing-priority-queue.html) |

## Verdict

On an Intel Core i7-4500U (Ubuntu 15.04, 32KB L1d, 64B cache lines) with g++ 4.9.3 -O3 -std=c++14 against libstdc++'s std::priority_queue, the author's blog graphs (no numeric text given) show the B-heap 'always faster' than std::priority_queue&lt;int&gt; across all tested mini-heap sizes (8/16/32/64), and 'consistently much faster' than std::priority_queue&lt;pair&lt;int,int&gt;&gt; when priority/payload are split into separate arrays, over 320 push+pop cycles at increasing queue sizes; the same post reports worse-or-comparable results for a std::pair&lt;int, unique_ptr&lt;msg&gt;&gt; payload.

## Use it when

- Hot push/pop loops (event queues, schedulers, simulations) with small trivially-copyable priority keys (e.g. int) where std::priority_queue's array-of-struct layout causes cache misses
- Workloads where priority and payload can be stored/passed separately via push(key, value) rather than bundled into one pair/struct
- Throughput-oriented benchmarking over many push+pop cycles rather than a single latency-critical operation
- x86-64 GCC/Clang, C++14+ codebases willing to tune miniheap_size to the target cache line size (64 bytes in the reference hardware)
- Projects that want a dependency-free single header they can vendor without pulling in a build system

## Skip it when

- Payload is a large or non-trivial type such as std::pair&lt;int, std::unique_ptr&lt;msg&gt;&gt; — the author's own benchmark shows this configuration can be worse than or comparable to std::priority_queue
- You need a stable ordering among equal priorities — it's an unstable B-heap (confirmed by the maintainer in issue #2); add a discriminator field if insertion order matters
- You rely on container-adaptor features std::priority_queue doesn't even need to promise here but users may expect: iterators, merge, or swap are not implemented
- Concurrent/multi-threaded access — thread safety is not documented and there is no internal synchronization
- You need active maintenance: no CI/CMake in the repo, no open issues or PRs, last commit 2025-09-18, and the maintainer said in 2022 he'd probably just use std::vector&lt;&gt; if writing it today

## How it is fast

Core technique is a B-heap layout (mini-heap size tunable as a power of two, e.g. 8/16/32/64) that groups a node's ancestors/descendants into the same cache line, cutting the cache misses a plain array-backed binary heap incurs on deep trees. It pairs this with a 'structure of arrays' split of priority and payload (a custom skip_vector) so comparisons during sift only touch the small, dense priority array and never pull large payload objects into cache. GCC builds additionally use __builtin_expect branch hints on the hot sift loops.

## Compared with alternatives

Pick prio_queue when priorities are not monotonically non-decreasing (not a Dijkstra-style access pattern), you need an arbitrary Compare rather than radix bucketing, and you want a tiny dependency-free C++ header. Prefer radix-heap/RadixHeap or S3Q when your workload fits their monotonic-priority or graph-search assumptions — they report larger, more concretely quantified speedups (radix-heap 1.2-1.7x, S3Q 4.6-7x) than this entry's graph-only, unstated ratios.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none for the library itself (only &lt;vector&gt;, &lt;cassert&gt;, &lt;tuple&gt;, &lt;cstddef&gt;); self_test.cpp and perf_benchmark.cpp additionally pull in Catch2, trompeloeil, and the author's own tachymeter benchmarking header, but none of those are needed to use prio_queue.hpp |
| **Minimum toolchain** | C++14 (uses std::enable_if_t); originally built and benchmarked with g++ 4.9.3 -O3 -std=c++14 |
| **Platforms** | any (portable C++, no SIMD/intrinsics); __builtin_expect is used under __GNUC__ with a no-op fallback elsewhere; miniheap_size should be tuned to the target's cache line size (64 bytes assumed in the reference benchmarks) |
| **Thread safety** | not documented; no internal locking, treat as unsynchronized like std::priority_queue |
| **Drop-in for the baseline** | partial — different template parameter order, split key/value push and top() API, adds reschedule_top(); call sites need to change, it is not a header swap |

## Gotchas

- Not a stable sort: equal-priority elements are not ordered by insertion (maintainer confirmed in issue #2); add an insertion-sequence discriminator to Prio if you need stability
- miniheap_size must be a power of two and matched to the CPU cache line / Prio size for the claimed gains; size 8 was 'consistently bad' in the author's own tests
- The speedup depends on splitting priority and payload into separate push(key, value) calls; storing both in one struct/pair defeats the optimization and can be slower than std::priority_queue
- Exception guarantee is conditional: strong guarantee only if Prio and Value have noexcept move constructors/assignment; otherwise only the weak guarantee (per README)

## Caveats and trade-offs

Methodology (CPU, compiler, flags) is fully stated but dates from 2015 on old hardware. The post's text gives no numeric ratios, only relative graphs. The in-place std::pair&lt;int, std::unique_ptr&lt;msg&gt;&gt; layout gave mixed results, including 'examples of worse performance than std::priority_queue&lt;&gt;'; gains are consistent only for int payloads and the split priority/payload layouts. Mini-heap size 8 is consistently bad. The current perf_benchmark.cpp uses the tachymeter library and may differ from the 2015 version. The last commit (2025-09-18) is just over 12 months before this run.

best performance requires storing priority and payload in separate arrays rather than a combined pair/struct; mini-heap size must be tuned to the cache line size; the same blog post reports worse performance than std::priority_queue for a std::pair&lt;int, unique_ptr&lt;msg&gt;&gt; payload in some configurations; less battle-tested than std::priority_queue

## Maintenance

Stale: last commit 2025-09-18, no open issues or PRs, and no CI/CMake in the repo, but it's a single BSL-1.0 header small enough to vendor and re-benchmark yourself; the maintainer noted in a 2022 issue he'd likely design it differently (plain std::vector&lt;&gt;) today.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** The blog post states g++ 4.9.3 with -O3 -std=c++14 on an Intel i7-4500U (Ubuntu 15.04) and graphs speed relative to std::priority_queue. The benchmark program is public in the repo (perf_benchmark.cpp, which includes &lt;queue&gt;), so this meets A.
- **Verifier notes:** The qualitative quotes in claimed_speedup appear verbatim on the page. Metadata checks out: BSL-1.0, 111 stars, last commit 2025-09-18, so stale.
- **Fields the verifier corrected:** `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://playfulprogramming.blogspot.com/2015/08/cache-optimizing-priority-queue.html>
  - <https://github.com/rollbear/prio_queue>
  - <https://github.com/rollbear/prio_queue/blob/master/perf_benchmark.cpp>
- **Sources the enricher read:**
  - <https://github.com/rollbear/prio_queue>
  - <https://github.com/rollbear/prio_queue/blob/master/README.md>
  - <https://github.com/rollbear/prio_queue/blob/master/prio_queue.hpp>
  - <https://github.com/rollbear/prio_queue/blob/master/perf_benchmark.cpp>
  - <https://github.com/rollbear/prio_queue/issues/2>
  - <https://github.com/rollbear/prio_queue/issues/5>
  - <https://playfulprogramming.blogspot.com/2015/08/cache-optimizing-priority-queue.html>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/rollbear/prio_queue`) · [data/wave1/enrich/raw/github_com_rollbear_prio_queue.json](../../../data/wave1/enrich/raw/github_com_rollbear_prio_queue.json) (enrichment confidence 0.72)

</details>
