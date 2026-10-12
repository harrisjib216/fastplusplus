# ALEX (Adaptive Learned indEX)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Indexes](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `MIT` · 🟡 stale

> Header-only C++ learned ordered index for numeric keys; beats STX B+Tree up to 4x on in-memory lookups and inserts.

| | |
|---|---|
| **Beats** | STX B+Tree (std::map-like ordered index); also beats Adaptive Radix Tree (ART), a 2-stage RMI ("Learned Index"), and a Model-enhanced B+Tree |
| **Claimed result** | Up to 4.1x/2.2x/2.9x/3.0x higher throughput and 800x/15x/160x/8000x smaller index than B+Tree/Learned-Index/Model-B+Tree/ART on read-only workloads; up to 4.0x/2.7x/2.7x higher throughput and 2000x/475x/36000x smaller index vs B+Tree/Model-B+Tree/ART on read-write workloads |
| **Workload** | Single-threaded throughput on 4 datasets with 8-byte keys: longitudes (1B keys), longlat (200M), lognormal (190M) and YCSB (200M, 80-byte payloads). Five workloads: read-only, read-heavy (95% reads/5% inserts), write-heavy (50/50), short range scans (95% scans/5% inserts) and write-only. |
| **Metric** | throughput |
| **Hardware** | Intel Core i9-9900K 3.6GHz, 64GB RAM, Ubuntu Linux, single-threaded |
| **Adoption** | 701 stars; used as a baseline by many follow-up learned-index papers (LIPP, CARMI, etc.) |
| **Last commit** | 2024-03-12 |
| **Links** | [repository](https://github.com/microsoft/ALEX) · [benchmark](https://arxiv.org/abs/1905.08898) |

## Verdict

In the SIGMOD'20 paper (single-threaded, Intel Core i9-9900K, 64 GB RAM), ALEX reached up to 4.1x read-only and 4.0x read-write throughput over an STX B+Tree whose page size was grid-searched per dataset and workload, and up to 2.2x over a 2-level RMI Learned Index. The tests used 8-byte keys: 1B longitudes, 200M longlat, 190M lognormal and 200M YCSB keys with 80-byte payloads. The paper names no compiler or flags, does not compare against std::map, and the repo's benchmark runs ALEX alone. GRE (PVLDB'22, gcc 8.3.0 -O3, Xeon Platinum 8268) independently ranked ALEX among the top single-threaded indexes against STX B+Tree, ART and HOT, except on hard data with 50% or more writes.

## Use it when

- Single-threaded (or externally locked) in-memory ordered map with 8-byte integer or double keys and small fixed-size payloads, where point lookups dominate: the paper reports up to 4.1x read-only throughput over a page-size-tuned STX B+Tree.
- Read-only to read-intensive mixes with inserts (for example 95% reads / 5% inserts): the independent GRE study found single-core learned indexes such as ALEX beat traditional indexes there regardless of how hard the key distribution is.
- Short range scans (up to about 1000 keys) mixed with lookups and inserts: the paper shows up to 2.27x over B+Tree on its 95% scan / 5% insert workload, helped by large leaves (median 161 KB on longitudes).
- Append-heavy keys such as timestamps or sequence IDs: leaves detect append-mostly behavior, and the paper shows up to 3.6x over B+Tree when the remaining keys are inserted in ascending order.
- Memory-constrained cases where you would otherwise pick LIPP: GRE measured ALEX as the most space-efficient of its three top performers, with LIPP using 4-5x more memory.

## Skip it when

- Concurrent access: the public code has no locking, and even lookups write per-node statistics. GRE's concurrent port (ALEX+, based on the APEX protocol) lives in a research repo (gre4index/GRE) that declares no license.
- String, composite or custom-ordered keys: a static_assert requires an arithmetic key type and the default AlexCompare comparator.
- Hard, locally nonlinear key distributions with 50% or more writes: GRE found learned indexes lose to traditional indexes there. ALEX's key shifts per insert grow with hardness (42.6 on genome versus 8.1 on covid), and its 99.9th-percentile insert latency is high on osm and genome. The README also warns that extreme outlier keys inflate the key domain and tree depth.
- Workloads whose distribution shifts from easy to hard after bulk load (GRE measured up to a 52% throughput drop), large payloads under heavy writes (payloads are stored inline and copied on every expansion or split; ART matched ALEX on write-only YCSB with 80-byte payloads), and long scans past about 1000 keys, where a B+Tree tuned for scans wins.
- Non-x86 targets: the code includes x86intrin.h, runs inline cpuid assembly and calls _lzcnt_u64/_tzcnt_u64/_mm_popcnt_u64 unconditionally, so aarch64 (Apple Silicon, Graviton) needs porting.

## How it is fast

ALEX is an updatable Recursive Model Index (RMI). Each internal node holds a linear regression that computes the child slot directly, so no key comparisons happen above the leaves. Leaves are Gapped Arrays filled by model-based inserts, so most keys sit at or near their predicted slot and an exponential search from the prediction finishes in a few steps; a per-leaf bitmap marks gaps, and popcnt/lzcnt/tzcnt find the nearest gap for an insert. Cost models (expected search iterations and key shifts) plus a 'fanout tree' decide the node layout at bulk load and whether a full leaf expands and retrains, splits sideways or splits downward.

## Compared with alternatives

Pick ALEX over LIPP when memory or a path to concurrency matters: GRE measured LIPP at 4-5x ALEX's memory and found LIPP scales poorly when parallelized, while ALEX+ scales well. Pick LIPP or CARMI when raw single-threaded lookup speed is all that counts (their catalog entries claim up to 2.8x and on average 1.9x over ALEX), PGM-index for write-only or static data (GRE saw PGM with the best insert throughput at 100% writes but lookups dominated by ALEX), and ART Synchronized when you need a concurrent index today.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none beyond the C++ standard library and x86 intrinsics headers (doctest is downloaded by CMake only for the unit tests) |
| **Minimum toolchain** | C++14 (README and CMakeLists). The shipped CMake uses -O3 -march=native for GCC/Clang and /O2 /arch:AVX2 for MSVC. The CPU and flags must enable POPCNT and LZCNT/TZCNT (BMI, Haswell or later), or builds fail with 'target specific option mismatch' (issues #13, #31). C++20 against libc++ will probably not compile: ALEX uses std::allocator::rebind and destroy, which the libc++ headers declare only for C++17 and earlier (inferred from the headers, not built). |
| **Platforms** | x86-64 only (Linux, Intel macOS, Windows/MSVC); no aarch64 code path |
| **Thread safety** | Not thread-safe; the README says ALEX runs single-threaded. Lookups (find, get_payload, lower_bound) increment per-node and global counters that feed the cost models, so even concurrent readers race without an external lock. |
| **Drop-in for the baseline** | partial — AlexMap fills the same ordered-map role as STX B+Tree and std::map and mirrors most of the std::map API. However, keys must be numeric with the default comparator, operator\* returns a copy of the pair rather than a reference, and forward iterators cannot be decremented (a separate reverse_iterator exists). Alex::insert does not overwrite an existing key, and iterators and references do not stay stable across inserts. |

## Gotchas

- Inserts shift keys inside a leaf, and expansions or splits allocate new slot arrays and free the old ones. Iterators and payload references (from operator[], at() or iterator payload()) can therefore dangle after any insert, unlike std::map. The repo does not document these invalidation rules.
- Payload slots are default-constructed with placement new and freed with deallocate(); neither resize nor the leaf destructor calls payload destructors. Use trivially destructible payloads (integers, POD structs, raw pointers); a std::string payload would leak.
- Gap slots after a leaf's largest key hold std::numeric_limits&lt;T&gt;::max() as an end sentinel, and find_key compares slot contents without checking the gap bitmap. Treat max() as a reserved key value (inferred from the source, not documented).
- bulk_load() expects sorted input and silently does nothing if the index is not empty or num_keys &lt;= 0. Key counts are int, so one index cannot exceed about 2.1 billion keys. The paper's '800x-2000x smaller index' counts inner nodes only; leaves start 70% full, and GRE found that no learned index saves more than 3.2x end to end versus traditional indexes.

## Known shortcomings

- Not thread-safe; lookups write stats counters, so even concurrent readers race (the ALEX+ port in GRE declares no license). x86-64 only (x86intrin, cpuid, lzcnt/tzcnt; needs BMI).
- Iterators and payload references dangle after inserts; payload destructors never run, so non-trivial payloads leak. On hard data with 50%+ writes it loses to traditional indexes (GRE); easy-to-hard distribution shift costs up to 52% throughput. Stale since 2024-03 with unanswered memory-blowup and null-child issues; baseline was a page-tuned STX B+Tree, no compiler flags stated.

## Caveats and trade-offs

The paper states hardware (i9-9900K, 64GB) but no compiler or optimization flags. The public repo's benchmark (src/benchmark/main.cpp) runs only ALEX, so the B+Tree/ART comparison cannot be reproduced from the repo. The baseline is STX B+Tree, not std::map. Later peer-reviewed work corroborates the win: LIPP (PVLDB'21) and GRE (PVLDB'22, gcc 8.3.0 -O3, Xeon Platinum 8268) found ALEX among the top single-threaded indexes against STX B+Tree/ART/HOT.

No concurrency support in the public implementation; can degrade under adversarial/skewed insert patterns without retraining; README explicitly calls it 'a near drop-in replacement for std::map'

## Maintenance

Stale: the last commit is 2024-03-12 (bug-fix PR #29), and issues about runaway memory on insert (#30) and unassigned child pointers in expand_root (#26) have no maintainer reply. It is MIT-licensed and six headers, so it is easy to vendor on x86-64 with C++14/17.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** The peer-reviewed SIGMOD'20 paper (arXiv 1905.08898) shows ALEX beating STX B+Tree, ART, a 2-level RMI and a Model B+Tree on an Intel Core i9-9900K. It states no compiler or flags, and the repo's src/benchmark/main.cpp benchmarks ALEX alone with no baseline harness, so it cannot be A.
- **Verifier notes:** All claimed ratios appear verbatim in Section 6 (4.1x/2.2x/2.9x/3.0x read-only; 4.0x/2.7x/2.7x read-write; index-size ratios). Two fields were wrong: compared_against_cpp_std_directly was set true, but the paper benchmarks STX B+Tree, not std::map; and the workload said all datasets were 200M keys, but longitudes is 1B and lognormal 190M. The metadata checks out: MIT, 701 stars, last commit 2024-03-12 (stale), not a fork.
- **Fields the verifier corrected:** `compared_against_cpp_std_directly`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/pdf/1905.08898>
  - <https://github.com/microsoft/ALEX>
  - <https://www.vldb.org/pvldb/vol15/p3004-wongkham.pdf>
- **Sources the enricher read:**
  - <https://github.com/microsoft/ALEX>
  - <https://github.com/microsoft/ALEX/blob/master/src/core/alex.h>
  - <https://github.com/microsoft/ALEX/blob/master/src/core/alex_base.h>
  - <https://github.com/microsoft/ALEX/blob/master/src/core/alex_nodes.h>
  - <https://github.com/microsoft/ALEX/blob/master/src/core/alex_map.h>
  - <https://github.com/microsoft/ALEX/blob/master/CMakeLists.txt>
  - <https://github.com/microsoft/ALEX/blob/master/src/examples/main.cpp>
  - <https://github.com/microsoft/ALEX/wiki/API-Documentation>
  - <https://github.com/microsoft/ALEX/issues>
  - <https://github.com/microsoft/ALEX/issues/3>
  - <https://github.com/microsoft/ALEX/issues/4>
  - <https://github.com/microsoft/ALEX/issues/10>
  - <https://github.com/microsoft/ALEX/issues/13>
  - <https://github.com/microsoft/ALEX/issues/16>
  - <https://github.com/microsoft/ALEX/issues/26>
  - <https://github.com/microsoft/ALEX/issues/30>
  - <https://github.com/microsoft/ALEX/issues/31>
  - <https://github.com/microsoft/ALEX/issues/34>
  - <https://github.com/microsoft/ALEX/pulls>
  - <https://github.com/microsoft/ALEX/commits/master>
  - <https://arxiv.org/pdf/1905.08898>
  - <https://www.vldb.org/pvldb/vol15/p3004-wongkham.pdf>
  - <https://github.com/gre4index/GRE>
  - <https://hn.algolia.com/api/v1/search?query=ALEX%20learned%20index&tags=story>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/microsoft/alex`) · [data/wave6/enrich/raw/github_com_microsoft_alex.json](../../../data/wave6/enrich/raw/github_com_microsoft_alex.json) (enrichment confidence 0.85)

</details>
