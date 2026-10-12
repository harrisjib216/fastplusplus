# Superscalar Sample Queue (S3Q)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Priority queues and heaps](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only C++17 cache-efficient priority queue beating std::priority_queue via batched, sample-sort-style bucket classification.

| | |
|---|---|
| **Beats** | std::priority_queue |
| **Claimed result** | S3Q obtains speedups over min(S3QBH tuned binary heap, StdQueue = GCC's std::priority_queue) that grow roughly logarithmically with N, reaching 4.6x-7x for the largest instances (2^13-2^27 elements). |
| **Workload** | Random Sort / Random Wiggle push+pop microbenchmark, N from 2^13 to 2^27 elements, measuring (T_insert + T_deleteMin) / (2 log N) in nanoseconds. |
| **Metric** | throughput |
| **Hardware** | Intel Xeon E5-2650 v2 (Ivy Bridge EP) and AMD Athlon II X4 635 (K10), both x86-64 |
| **Compiler and flags** | GCC 9.3.0-17ubuntu1\~20.04, -O3 (deliberately no -march=native), Ubuntu 20.04.2 LTS, Linux 5.4.0-72-generic |
| **Adoption** | 7 stars |
| **Last commit** | 2026-05-27 |
| **Links** | [repository](https://github.com/raphinesse/s3q) · [benchmark](https://ae.iti.kit.edu/documents/theses/MA-von-der-Gr%c3%bcn.pdf) |

## Verdict

In a push+pop microbenchmark (2^13 to 2^27 elements) measured on GCC 9.3.0 -O3 (Ubuntu 20.04) across an Intel Xeon E5-2650 v2 and an AMD Athlon II X4 635, S3Q's speedup over min(S3QBH tuned binary heap, StdQueue) grows roughly logarithmically with N, reaching 4.6x-7x at the largest sizes; StdQueue in the benchmark harness is literally `std::priority_queue<T, std::vector<T>, std::greater<T>>` (confirmed in benchmarks/include/subjects/StdQueue.hpp), i.e. GCC's libstdc++ std::priority_queue.

## Use it when

- Large queues (benchmark validated 2^13-2^27 elements) where cache-miss-driven throughput matters more than per-op latency
- Comparison-based key ordering needed with no monotonicity constraint (unlike radix heaps)
- Keys are mostly-unique or have modest duplication (see gotchas)
- C++17 project that can pull in ips4o, range-v3, and xoshiro as build dependencies
- Workload matches push/pop-heavy microbenchmark shape (bulk insert then repeated pop+push)

## Skip it when

- Workloads with many duplicate/near-duplicate keys: open issue #15 (opened 2026-04-10, still open) reports a stack overflow inserting millions of identical/near-identical keys; thesis 5.2.1 admits full duplicate-key handling is future work
- Need item keys at the extreme of the key's range (e.g. INT_MIN for i32 keys) — reserved internally as sentinels, confirmed problematic in issue #15
- Need a true drop-in for std::priority_queue's template interface (comparator + container) — S3Q requires a Cfg struct and different construction
- Concurrent/multi-threaded access — no synchronization in the code and thread safety is not documented
- Small queues that fit comfortably in L1 already — the bucket/classifier machinery adds setup overhead a plain heap doesn't need

## How it is fast

It avoids per-insert branch mispredictions of a plain binary heap by batching pushes/pops and using a branchless, sample-sort-derived splitter classifier (borrowed from ips4o's classifier.hpp) to route items into buckets in bulk. Only a small base-case binary heap (sized to fit L1, `kBufBaseSize`, default \~32KiB/Item) is ever heap-ordered directly; the rest lives in coarser buckets that are split/merged in batches, giving amortized O(1/B log(M/B) N/M) cache misses per operation instead of O(log N) essentially-random accesses.

## Compared with alternatives

Pick S3Q over radix-heap/pair_radix_heap when keys aren't monotone or aren't well-suited to radix decomposition, since S3Q is purely comparison-based. Pick it over prio_queue (rollbear) when N is large enough (thesis tested up to 2^27) that cache-miss throughput dominates over a simpler binary-heap implementation; for smaller queues or simplicity, prio_queue's plain-heap approach avoids S3Q's extra dependencies and duplicate-key edge cases. If AVX2/AVX-512 hardware is available and the workload is monotone/constant-size, SimdQuickHeap is reported to beat S3Q itself by 1.4-2.8x.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | ips4o (fork: raphinesse/ips4o, tag s3q.2), range-v3 (pinned commit 6f3d0e2af9ae), xoshiro (Reputeless/Xoshiro-cpp v1.1); benchmarks additionally pull tlx and raphinesse/SequenceHeap |
| **Minimum toolchain** | C++17; thesis benchmarks used GCC 9.3.0 -O3. Closed issues #1, #5, #8 record and fix build failures on GCC 12-15 (-Werror=array-bounds, dangling-pointer warnings) |
| **Platforms** | x86-64 tested in the thesis (Xeon E5-2650 v2, Athlon II X4 635); no SIMD intrinsics or arch-specific code visible in the headers I read, so likely portable, but only x86-64 is verified |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | partial — explain: same push/top/pop/size/empty semantics, but construction requires a Cfg template parameter (Item type + GetKey) instead of std::priority_queue's Compare/Container template parameters, so call sites need rewriting, not just a type swap |

## Gotchas

- Open issue #15 (still open as of 2026-05-27): stack overflow on inputs with large numbers of duplicate/near-duplicate keys; root cause is that overflowing buckets need enough distinct keys to split cleanly
- Item keys must avoid the extreme sentinel values of the key type (e.g. i32::MIN) — reserved internally for range bounds per the issue #15 discussion
- kBufBaseSize/kLogMaxDegree defaults are tuned for a 32KiB, 8-way, 64B-line L1D (per maintainer comment on issue #15); mismatched cache geometry may need retuning for best throughput
- Requires defining a Cfg struct per Item type (Item::key member or custom GetKey functor) — more upfront setup than a comparator-only API

## Caveats and trade-offs

Numbers come from a 2021 KIT master's thesis (not a peer-reviewed venue), though methodology -- code, compiler, exact hardware -- is fully specified, satisfying tier A. 'StdQueue' in the thesis is literally the std::priority_queue shipped with the author's GCC build, the most direct C++-stdlib comparison in this set.

Comparison-based, no monotonicity requirement (unlike radix heaps). Loses to Sequence Heap on measured cache-miss counts even though it wins on wall-clock time in this thesis. Later beaten itself by SimdQuickHeap (1.4-2.8x). Header-only C++17, depends on ips4o/range-v3/xoshiro.

## Maintenance

Actively maintained (last commit 2026-05-27, three build/correctness issues closed in 2025, one duplicate-key stack-overflow issue still open); MIT-licensed and header-only so it's easy to vendor, but small (7 stars) and the duplicate-key edge case is unresolved.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** Thesis section 6.5.2 states verbatim that against min(S3QBH, StdQueue) the speedups are 'roughly logarithmic in N for N in [2^13, 2^27], finally reaching values between 4.6 and 7'. StdQueue is GCC's std::priority_queue. The setup is GCC 9.3.0 -O3 on Ubuntu 20.04.2 with a Xeon E5-2650 v2 and an Athlon II X4 635, and the benchmark code is public at benchmarks/benchmark.cpp.in in the repo.
- **Verifier notes:** Everything checked out: MIT license, 7 stars, not a fork, last commit 2026-05-27. The thesis ran one benchmark copy per physical core to simulate a loaded machine, which is worth keeping in mind when comparing it with single-thread numbers elsewhere.
- **Pages the verifier opened:**
  - <https://ae.iti.kit.edu/documents/theses/MA-von-der-Gr%c3%bcn.pdf>
  - <https://github.com/raphinesse/s3q>
- **Sources the enricher read:**
  - <https://github.com/raphinesse/s3q>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/raphinesse/s3q`) · [data/wave1/enrich/raw/github_com_raphinesse_s3q.json](../../../data/wave1/enrich/raw/github_com_raphinesse_s3q.json) (enrichment confidence 0.85)

</details>
