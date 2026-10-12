# CARMI (Cache-Aware RMI)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Indexes](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Header-only, updatable learned index (a cost-model-built RMI) for numeric keys that beats STX B+ Tree and ALEX on in-memory lookups.

| | |
|---|---|
| **Beats** | STX B+Tree and ALEX; also beats RMI on the SOSD benchmark platform |
| **Claimed result** | Average 2.2x (up to 4.2x) speedup vs STX B+ Tree and 1.9x (up to 7.2x) vs ALEX, using \~0.77x the memory of the B+ Tree; on the SOSD platform the average speedup over the nearest competitor, RMI, is 1.2x (1.21x, up to 1.5x). In SOSD Table 3, ART is slightly faster on face32 (182.36 vs 187.43 ns) and RMI/RS are within \~1-5 ns on face64/wiki. |
| **Workload** | 7 datasets: 4 synthetic (lognormal, uniform, normal, exponential; 1GB each of &lt;double,double&gt; pairs) plus YCSB, OSMC and Facebook (67,108,864 records each). Workloads: read-only, write-heavy (50/50), read-heavy (95/5), write-partial (85% reads / 15% inserts concentrated in 60-90% of key range) and range scan, with uniform and Zipfian access; single-threaded, 100,000 operations per workload. Plus SOSD: amzn/face/wiki/osmc real-world datasets of 200M 32/64-bit keys, 10M uniform lookups. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 3700X 8-core CPU, 32GB RAM, Ubuntu Linux, single-threaded |
| **Adoption** | 10 stars |
| **Last commit** | 2022-01-03 |
| **Links** | [repository](https://github.com/embryo-labs/CARMI) · [benchmark](https://arxiv.org/abs/2103.00858) |

## Verdict

In the authors' own single-threaded runs on an AMD Ryzen 3700X (Ubuntu; compiler and flags not stated, the repo's CMake builds Release), over seven \~67M-key datasets and five 100K-operation workloads, CARMI averaged 2.2x (up to 4.2x) the throughput of STX B+ Tree with 512-byte nodes and 1.9x (up to 7.2x) that of ALEX, using about 0.77x the B+ Tree's memory. Ported to SOSD (200M-key amzn/face/wiki/osmc, 10M uniform lookups), it averaged about 1.2x faster than a tuned RMI, but ART was faster on face32 and RMI/RS came within about 1-5 ns on face64 and wiki; no std:: container was benchmarked.

## Use it when

- Single-threaded, in-memory ordered index over 64-bit numeric keys (double or uint64) with small fixed-size numeric values, at roughly 10^7-10^8 keys, where point lookups and short range scans dominate.
- Real-world key sets whose CDF is locally non-linear (OSM coordinates, user IDs, timestamps), where RMI and ALEX degrade. The paper reports about 1.5x over ALEX on OSMC/Facebook read-only, and about 1.2x over a hand-tuned RMI on SOSD.
- Mixed read/insert workloads (50/50, 95/5, inserts clustered in one key range) where you can bulk-load first and supply representative sample insert keys. The paper reports 2.2x over the B+ Tree and 3.0x over ALEX on write-heavy workloads.
- Indexes that are rebuilt rarely (the authors suggest off-peak rebuilds), so a construction step of several minutes is acceptable in exchange for faster lookups.
- Learned-index research or prototyping where you want an explicit time/space knob (lambda) and swappable node types.

## Skip it when

- Any concurrent access. The headers contain no locks or atomics, and the paper describes read/write-lock concurrency only as a possible extension.
- String, composite or other non-arithmetic keys or values. The paper states that only numeric key types are supported, and the code relies on DBL_MAX sentinels and key+1 arithmetic.
- Memory-tight deployments. SOSD Table 4 shows CARMI at 3918/5481 MB (uint32/uint64) against 2472/3143 MB for RMI and 2657/3541 MB for the B+ Tree, over 2289/3052 MB of raw data. The headline '0.77x the B+ Tree's memory' comes only from the authors' own harness.
- Fast startup or frequent rebuilds. Construction took 0.3-3.2 minutes on the 67M-key datasets, against about 10 s for STX B+ Tree and 20 s for ALEX.
- Production code that needs a maintained dependency. The repo has had no commits since Jan 2022, has 10 stars, no releases, no CI, and its unit tests are commented out in CMakeLists.txt.

## How it is fast

Every node that holds a model is exactly 64 bytes, so each inner step costs at most one cache miss, and each leaf is a 'cache-friendly array' (a 64-byte header of block minimum keys over a few 256-byte sorted data blocks), so the last-mile search scans one block instead of doing RMI/ALEX-style error-bounded binary search. A cost model (measured per-node latency + lambda × space, with the entropy of child partition sizes as the measure of how well a node splits the data) drives a hybrid dynamic-programming/greedy construction that picks each subtree's node type and fanout. The result is a flat tree: average depth 2.1 in the paper, against 2.5 for ALEX and 7.3 for the B+ Tree. The piecewise-linear root also has a prefetch model, which issues __builtin_prefetch for the predicted data block while the leaf is being fetched.

## Compared with alternatives

Pick CARMI over PGM-index when you need an updatable, std::map-like container with values stored inline, tuned for skewed real-world keys, and you can accept more memory and minutes-long builds; PGM-index is maintained, orders of magnitude smaller and the better fit for static or space-critical use. Choose an ART (such as rafaelkallis/adaptive-radix-tree) instead when keys are byte strings or dense 32-bit IDs: SOSD's ART beat CARMI on face32 (182 vs 187 ns).

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (C++ standard library only; the bundled STX B+ Tree and the ALEX/RadixSpline pointers exist only for the experiments) |
| **Minimum toolchain** | C++17 (CMake sets CMAKE_CXX_STANDARD 17 and a Release build); no compiler versions documented |
| **Platforms** | Linux/macOS with GCC or Clang (__builtin_prefetch). A Windows branch uses _mm_prefetch, so x86 only there. No SIMD is required. The per-node latency constants in params.h are the authors' measurements; the repo tells you to re-run src/profiler on your own machine. |
| **Thread safety** | Not thread-safe: no synchronization anywhere in the headers, and concurrency is listed only as future work. |
| **Drop-in for the baseline** | partial — CARMIMap has the same method names as std::map/STX btree_map. It differs in four ways: it is meant to be bulk-built (optionally with a lambda cost weight and sample insert keys), it accepts only arithmetic keys and values, insert() does not reject duplicate keys, and max_size() is INT32_MAX. |

## Gotchas

- Empty slots are marked with static_cast&lt;KeyType&gt;(DBL_MAX), and values with static_cast&lt;ValueType&gt;(DBL_MAX). During construction, a value equal to that sentinel is treated as an insert placeholder. For integer types the cast is out of range (undefined behaviour), so keep keys and values away from the type's maximum and check what your compiler produces.
- insert() has no existing-key check. It stores a second entry and returns true, where std::map would return false; erase(key) is documented as removing all entries with that key.
- Block size, the DP/greedy switch threshold, external leaf capacity and the latency constants are all constexpr in params.h, which also has a global '#define DEBUG'. Tuning means editing the header. The repo defaults also differ from the paper's appendix (kAlgorithmThreshold 60000 vs kDPThreshold 512; external leaf capacity 1024 vs 512). The two-iterator constructor derives lambda from the data size, while the paper tuned lambda per dataset.
- The README says to include ./include/carmi_common.h, but that file does not exist. Include carmi_map.h or carmi_external_map.h instead. The public experiment harness runs only CARMI (no B+ Tree/ALEX drivers), and the SOSD port is in neither this repo nor upstream learnedsystems/SOSD, so the comparisons cannot be reproduced out of the box.

## Known shortcomings

- Real datasets have 67,108,864 records, not \~10^8 keys; 'beats all on SOSD' is overstated (ART wins face32); no compiler stated.
- No thread safety; numeric keys only; DBL_MAX cast as the empty-slot sentinel is UB for integer keys. insert() has no duplicate-key check (stores a second entry and returns true, unlike std::map). In SOSD it uses among the most memory (3918/5481 MB vs RMI 2472/3143, B+Tree 2657/3541); the '0.77x B+Tree memory' comes only from the authors' harness. Build takes 0.3-3.2 min vs \~10 s for a B+Tree; knobs are constexpr and repo defaults differ from the paper. README references a missing header; the public harness runs CARMI only and the SOSD port isn't published, so comparisons can't be reproduced. Abandoned since 2022-01, no CI, unit tests commented out.

## Caveats and trade-offs

Very low adoption (10 stars) and the repo has not been updated since Jan 2022. Numbers are the authors' own, from a peer-reviewed PVLDB 2022 paper. The abstract's 'outperforms all baselines on SOSD' is slightly overstated: ART beats CARMI on face32 and RMI is effectively tied on face64. No compiler or flags are stated. The lambda parameter is tuned per dataset.

Read/static-friendly cost model; construction is more expensive due to a cost-based dynamic-programming search; gains shrink on already cache-friendly small datasets

## Maintenance

Abandoned since January 2022 (a single author, 10 stars, no issues filed), but it is MIT-licensed, header-only C++17 and small enough to vendor as research code: numeric keys only, single-threaded, parameters compiled in.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed paper (arXiv 2103.00858, published as PVLDB 15(11):2679-2691, 2022, DOI 10.14778/3551793.3551823) benchmarks CARMI against STX B+ Tree and ALEX and, on the SOSD platform, against RMI/RS/ALEX/FAST/ART/B+Tree etc. The CPU (AMD Ryzen 3700X) is stated and the code is public (embryo-labs/CARMI src/ with bundled stx_btree and alex), but no compiler or flags are given, so it cannot be A.
- **Verifier notes:** The abstract numbers match the record. The workload's '\~10^8 keys' was wrong: real datasets have 67,108,864 records, and the 10^8 in the paper is a key-value multiplier for the synthetic data. GitHub metadata was verified: MIT, 10 stars, not a fork, last commit 2022-01-03, so abandoned is correct.
- **Fields the verifier corrected:** `workload`, `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/abs/2103.00858>
  - <https://arxiv.org/pdf/2103.00858>
  - <https://github.com/embryo-labs/CARMI>
  - <https://api.crossref.org/works?query.bibliographic=CARMI+cache-aware+learned+index+Zhang+Gao&rows=5>
- **Sources the enricher read:**
  - <https://github.com/embryo-labs/CARMI>
  - <https://github.com/embryo-labs/CARMI/blob/master/README.md>
  - <https://github.com/embryo-labs/CARMI/blob/master/src/CMakeLists.txt>
  - <https://github.com/embryo-labs/CARMI/blob/master/src/include/params.h>
  - <https://github.com/embryo-labs/CARMI/blob/master/src/include/carmi_map.h>
  - <https://github.com/embryo-labs/CARMI/blob/master/src/include/carmi_external_map.h>
  - <https://github.com/embryo-labs/CARMI/blob/master/src/include/carmi.h>
  - <https://github.com/embryo-labs/CARMI/blob/master/src/include/base_node.h>
  - <https://github.com/embryo-labs/CARMI/blob/master/src/include/nodes/leafNode/cfarray_type.h>
  - <https://github.com/embryo-labs/CARMI/blob/master/src/include/nodes/rootNode/root_nodes.h>
  - <https://github.com/embryo-labs/CARMI/blob/master/src/include/func/find_function.h>
  - <https://github.com/embryo-labs/CARMI/blob/master/src/include/func/insert_function.h>
  - <https://github.com/embryo-labs/CARMI/blob/master/src/example/example.cpp>
  - <https://github.com/embryo-labs/CARMI/blob/master/src/experiment.cpp>
  - <https://github.com/embryo-labs/CARMI/blob/master/src/experiment/core.cpp>
  - <https://github.com/embryo-labs/CARMI/blob/master/src/experiment/experiment_params.h>
  - <https://github.com/embryo-labs/CARMI/blob/master/src/experiment/main_experiment.cpp>
  - <https://github.com/embryo-labs/CARMI/blob/master/src/experiment/functions.h>
  - <https://github.com/embryo-labs/CARMI/blob/master/alex/src.txt>
  - <https://github.com/embryo-labs/CARMI/blob/master/rs/src.txt>
  - <https://github.com/embryo-labs/CARMI/blob/master/stx_btree/src.txt>
  - <https://github.com/embryo-labs/CARMI/issues>
  - <https://github.com/embryo-labs/CARMI/pulls>
  - <https://github.com/embryo-labs/CARMI/forks>
  - <https://github.com/embryo-labs/CARMI/commits/master>
  - <https://arxiv.org/pdf/2103.00858>
  - <https://github.com/learnedsystems/SOSD>
  - <https://hn.algolia.com/api/v1/search?query=CARMI%20learned%20index&tags=story>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/embryo-labs/carmi`) · [data/wave6/enrich/raw/github_com_embryo_labs_carmi.json](../../../data/wave6/enrich/raw/github_com_embryo_labs_carmi.json) (enrichment confidence 0.8)

</details>
