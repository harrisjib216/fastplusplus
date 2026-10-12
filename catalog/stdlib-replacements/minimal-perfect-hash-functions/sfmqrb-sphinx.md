# Sphinx

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Minimal perfect hash functions](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `BSD-2-Clause` · 🟡 stale

> Dynamic succinct perfect hash index (\~4 bits/key) for log-structured KV stores; paper reports \~2x lower latency than DHT/Aleph Filter.

| | |
|---|---|
| **Beats** | DHT (Delta Hash Table, a dynamic perfect hash table) / RSQF / Aleph Filter / Adaptive Aleph Filter (state-of-the-art fingerprint and perfect-hash indexes for log-structured hash tables / key-value stores) |
| **Claimed result** | Abstract: about 2x lower query latency, update latency and memory footprint than the best alternatives. Fig. 6: zero false positives for queries to existing keys, and at most half the memory of the other baselines. In memory (Fig. 8), Sphinx has the lowest average and p99 query/update latency. Its average insertion is slightly slower than some baselines (read-before-write); Sphinx-4 (4 reserve bits) beats all baselines on every in-memory metric. On Optane, Sphinx variants are fastest. On SSD (Fig. 9), they match or beat all baselines, with only a slight gap to DHT-expandable under a uniform workload. Under skew at 90-99% cache hit rate, Sphinx is 10-35% faster than DHT-expandable (Fig. 10A). |
| **Workload** | Average and tail-99 query/update/insertion latency and memory footprint (bits/entry) of an in-memory, Optane, and SSD-resident LSH-table index over up to 10^8 keys, against DHT, DHT-expandable, RSQF, Aleph Filter and Adaptive Aleph Filter C++ implementations |
| **Metric** | latency |
| **Hardware** | Platform 1: Intel Xeon W7-2495X (24 cores/48 threads, 2.5GHz), 1.9MB L1/48MB L2/45MB L3, 512GB NVMe SSD (OS) + 2TB Samsung 980 Pro SSD (benchmark drive), Ubuntu 22.04; Platform 2: dual Intel Xeon Silver 4314 (32 cores/64 threads, 2.4GHz) with 256GB RAM + 496GB Intel Optane Persistent Memory 200 Series, Ubuntu 22.04 |
| **Compiler and flags** | GCC 11.4.0 (benchmark/reproducibility.md, 'version installed or later'); -std=c++23 -O3 -march=native -mbmi2 (CMakeLists.txt). CMakeLists.txt also sets an RPATH to /usr/local/gcc-14.1.0 and has a commented-out GCC 14.1.0 compiler path. |
| **Adoption** | 22 stars; PVLDB vol. 18(11), pp. 4424-4437 (2025); the paper's PVLDB Artifact Availability section points to the repo |
| **Last commit** | 2025-08-31 |
| **Links** | [repository](https://github.com/sfmqrb/sphinx) · [benchmark](https://www.vldb.org/pvldb/vol18/p4424-maghrebi.pdf) |

## Verdict

The PVLDB 18(11) paper measures Sphinx against the authors' own C++ DHT and DHT-expandable and against RSQF, Aleph Filter and Adaptive Aleph Filter (Memento Filter codebase), using \~1.2x10^8 xxhash-hashed int64 keys and uniform queries to existing keys, built with GCC 11.4.0+ -O3 -march=native -mbmi2 on a Xeon W7-2495X (in memory and on a Samsung 980 PRO SSD) and on dual Xeon Silver 4314 with Optane PMem 200. The results are figures only: Sphinx has the lowest in-memory average and p99 query/update latency (average insert is slightly slower unless 4 Reserve Bits are used), a slight edge over DHT-expandable on SSD with uniform keys, and 10-35% speedup at 90-99% cache hit rates; std::unordered_map and static MPHFs were never measured.

## Use it when

- In-memory key-to-log-address index for an index+log / Bitcask-style KV store on SSD or Optane, where index memory per key limits scale.
- Queries, updates and deletes of existing keys that must cost exactly one storage read with stable p99 latency (no fingerprint false positives, unlike RSQF/Aleph-style fingerprint indexes).
- Datasets that grow over time: the index expands one 64-block group at a time rather than being preallocated like DHT or fully rehashed.
- Skewed workloads with a hot block cache where index CPU cost dominates: the paper measures 10-35% speedup over DHT-expandable at 90-99% cache hit rates.
- x86-64 Linux servers with fast BMI2 (Intel Haswell or newer, AMD Zen 3 or newer).

## Skip it when

- As a general in-memory hash map: it stores no keys, so every hit reads the backing log to get the key and value, and you must provide the log and its garbage collection yourself.
- Static key sets: the catalogued static MPHFs use about 2-3 bits/key and need no backing log. Sphinx's Trie Store alone is about 4 bits/key before payloads, and with uncompressed 32-bit pointers the payloads dominate. The paper's \~20 bits/key total depends on DHT-style pointer compression.
- Insert-heavy or miss-heavy workloads in the default configuration: every insert (read-before-write) and every query for an absent key costs one storage read unless you enable Reserve Bits (the Sphinx-4 variant with 4 bits).
- ARM, Apple Silicon, Windows/macOS, or AMD CPUs before Zen 3, where PDEP/PEXT are microcoded at about 18 cycles instead of 3. The code includes &lt;x86intrin.h&gt;, builds with -march=native, and the paper lists an ARM port as future work.
- Production use that needs a stable API: this is a research artifact configured through global #defines and Traits structs, with hard-coded benchmark paths, no releases, no CI and no API docs.

## How it is fast

Each 64-slot block is a 256-bit Trie Store: an occupancy bitmap, 1-delimited unary slot sizes, and DHT-style delta tries with one extra delimiter bit, so the number of 1s before any slot's trie is known and the slot is reached with rank (POPCNT) and select (PDEP+TZCNT) over four 64-bit words instead of DHT's bit-by-bit scan, at a cost of about 0.3 bits/entry. A 4 KB L1-resident Decoder, a collision-free 512-bucket table of the 128 most probable trie shapes hashed with shifts and XOR, turns trie decoding into one PEXT of the fingerprint plus a packed-offset lookup; only about 1% of lookups fall back to walking the trie. Overflowing slots go to 4 shared extension blocks per 64-block group instead of chains. Growth splits one block group at a time through an extendible-hashing directory and reuses hash bits already in the tries and the optional Reserve Bits, so expansion rarely rereads keys from storage.

## Compared with alternatives

Every catalogued sibling (PTHash, PtrHash, RecSplit, ShockHash, PHast, etc.) is a static MPHF: it is built once over a fixed key set and reaches roughly 2-3 bits/key with tens of ns per query (e.g. PTHash 37 ns at 3.23 bits/key). Pick Sphinx only when keys are continually inserted, updated and deleted and each key already has a record in storage that can be read to confirm it; for a fixed key set, PtrHash or PTHash is smaller, simpler and needs no backing log.

## Integration

| | |
|---|---|
| **Form** | source-drop (header templates exposed as CMake INTERFACE targets, plus one small static lib holding the Decoder table; no install target or package) |
| **Dependencies** | Vendored in lib/: xxhash (XXHash64) and moodycamel ConcurrentQueue; Catch2 for tests; Memento filter and a YCSB Zipfian generator for benchmarks only; links -latomic |
| **Minimum toolchain** | C++23 (CMake passes -std=c++23 to GCC); GCC 11.4.0+ and CMake 3.22.1+ per benchmark/reproducibility.md (CMakeLists sets an RPATH to /usr/local/gcc-14.1.0); Clang and MSVC not documented |
| **Platforms** | x86-64 with BMI2 (PDEP/PEXT), POPCNT and LZCNT/TZCNT; Linux as written (SSDLog uses O_DIRECT, posix_fallocate, sysconf); no ARM |
| **Thread safety** | Opt-in at compile time. With ENABLE_MT, every read and write takes a per-block-group std::mutex, directory doubling takes a global mutex, and the async readSegment/writeSegment/removeSegment calls shard work by group ID to per-thread lock-free queues and return std::future. Without ENABLE_MT, the \*SingleThread calls are unsynchronized and the async calls throw. SSDLog::write is never synchronized (the benchmarks call it from the main thread). |
| **Drop-in for the baseline** | no |

## Gotchas

- A read does not check that the returned log entry's key equals the queried key. For an absent key (with Reserve Bits off) it returns whatever record that slot points to, so compare kv.key yourself.
- Reads modify the index: with Reserve Bits enabled, a read rewrites that entry's reserve bits from the fetched key. Concurrent readers of one block group therefore need the per-group mutex, which is taken only under ENABLE_MT.
- Behaviour depends on global macros in config/config.h (IN_MEMORY_FILE, ENABLE_XDP, ENABLE_MT, ENABLE_BP_FOR_READ) and on compile-time Traits (key and payload types, reserve bits, DHT modes). The Directory constructor starts maxThreads worker threads that spin on std::this_thread::yield() until destruction. A failed remove throws std::invalid_argument.
- Keys must be fixed-size and trivially copyable (default int64_t). They are hashed as raw bytes with XXHash64 under two seeds, and updates identify a key by that 128-bit digest. The bundled SSDLog is a benchmark-grade, fixed-size circular log with no garbage collection that detects Optane by the substring 'optane' in the file name. The README build steps omit the `cmake ..` configure step.

## Caveats and trade-offs

The baselines are LSH-table indexes and filters (DHT, RSQF, Aleph Filter), not std::unordered_map or MPHFs such as BBHash, CMPH or PTHash. DHT is the authors' own C++ reimplementation, because the original is closed-source. RSQF and Aleph Filter come from the Memento Filter codebase. Sphinx is a dynamic succinct perfect hash table (a key-to-payload index), not a static MPHF. It is x86-only and needs BMI2 PDEP/PEXT. The 2x headline comes from the abstract; the figures carry the per-experiment detail and there is no numeric table. The compiler version comes from the repo's reproducibility doc, not the paper, and the CMake RPATH points to GCC 14.1.0, so the exact compiler for the paper runs is not certain.

Designed specifically as an in-memory index for LSH-table / log-structured key-value stores (not a general-purpose associative container); relies on x86 rank/select instructions (POPCNT, PEXT, TZCNT) for full speed; static succinct trie-based decoder is built for a fixed key set per block and expands via block-group splitting rather than arbitrary rehashing; DHT baseline was the authors' own C++ re-implementation since the original DHT code is closed-source

## Maintenance

Stale BSD-2-Clause research artifact (last commit 2025-08-31, only a paper link; no releases or CI; a third-party 'Simd' PR closed unmerged in April 2026) that is copyable once you strip the benchmark scaffolding, last documented with GCC 11.4.0.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification B, tier now A.
- **Tier reason:** Upgraded from B. The PVLDB 18(11) paper compares Sphinx with DHT, DHT-expandable, RSQF, Aleph Filter and Adaptive Aleph Filter, and names the CPUs (Xeon W7-2495X; 2x Xeon Silver 4314). The repo states the build: CMakeLists.txt gives -std=c++23 -O3 -march=native -mbmi2, and benchmark/reproducibility.md lists GCC 11.4.0. The public benchmark code (benchmark/benchmark_main.cpp, benchmark_tail.cpp and related files) runs all these baselines.
- **Verifier notes:** Upgraded to Tier A because the repo states the compiler and flags and the paper states the CPU models. I dropped the unverified 'ACM Artifacts Available badge' wording from stars_or_usage. The 'lowest latency everywhere' part of the claim was slightly overstated (average insertion, and the SSD case), so I narrowed it to what the paper says. Metadata matches gh: BSD-2-Clause, 22 stars, last commit 2025-08-31 (about 12.8 months ago, so stale).
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://www.vldb.org/pvldb/vol18/p4424-maghrebi.pdf>
  - <https://github.com/sfmqrb/sphinx>
  - <https://github.com/sfmqrb/sphinx/blob/master/CMakeLists.txt>
  - <https://github.com/sfmqrb/sphinx/blob/master/benchmark/CMakeLists.txt>
  - <https://github.com/sfmqrb/sphinx/blob/master/benchmark/reproducibility.md>
  - <https://github.com/sfmqrb/sphinx/blob/master/benchmark/benchmark_main.cpp>
- **Sources the enricher read:**
  - <https://github.com/sfmqrb/sphinx>
  - <https://github.com/sfmqrb/sphinx/blob/master/README.md>
  - <https://github.com/sfmqrb/sphinx/blob/master/CMakeLists.txt>
  - <https://github.com/sfmqrb/sphinx/blob/master/benchmark/reproducibility.md>
  - <https://github.com/sfmqrb/sphinx/blob/master/benchmark/CMakeLists.txt>
  - <https://github.com/sfmqrb/sphinx/blob/master/benchmark/benchmark_main.cpp>
  - <https://github.com/sfmqrb/sphinx/blob/master/benchmark/benchmark_multi_threaded.cpp>
  - <https://github.com/sfmqrb/sphinx/blob/master/config/config.h>
  - <https://github.com/sfmqrb/sphinx/blob/master/directory/directory.h>
  - <https://github.com/sfmqrb/sphinx/blob/master/directory/directory_tests.cpp>
  - <https://github.com/sfmqrb/sphinx/blob/master/segment/segment.h>
  - <https://github.com/sfmqrb/sphinx/blob/master/block/block.h>
  - <https://github.com/sfmqrb/sphinx/blob/master/SSDLog/SSDLog.h>
  - <https://github.com/sfmqrb/sphinx/blob/master/hashtable/hashtable.h>
  - <https://github.com/sfmqrb/sphinx/blob/master/hashtable/hashtable.cpp>
  - <https://github.com/sfmqrb/sphinx/blob/master/hashtable/CMakeLists.txt>
  - <https://github.com/sfmqrb/sphinx/blob/master/hashing/hashing.h>
  - <https://github.com/sfmqrb/sphinx/blob/master/fingerprint_gen_helper/fingerprint_gen_helper.h>
  - <https://github.com/sfmqrb/sphinx/blob/master/bitset_wrapper/bitset_wrapper.h>
  - <https://github.com/sfmqrb/sphinx/blob/master/payload/payload.h>
  - <https://github.com/sfmqrb/sphinx/blob/master/extension_block/extension_block.h>
  - <https://github.com/sfmqrb/sphinx/blob/master/block/CMakeLists.txt>
  - <https://github.com/sfmqrb/sphinx/blob/master/directory/CMakeLists.txt>
  - <https://github.com/sfmqrb/sphinx/blob/master/segment/CMakeLists.txt>
  - <https://github.com/sfmqrb/sphinx/blob/master/SSDLog/CMakeLists.txt>
  - <https://github.com/sfmqrb/sphinx/commits/master>
  - <https://github.com/sfmqrb/sphinx/pull/1>
  - <https://www.vldb.org/pvldb/vol18/p4424-maghrebi.pdf>
  - <https://en.wikipedia.org/wiki/X86_Bit_manipulation_instruction_set>
- **Raw records:** [data/wave1-phf/verified.json](../../../data/wave1-phf/verified.json) (id `https://github.com/sfmqrb/sphinx`) · [data/wave1-phf/enrich/raw/github_com_sfmqrb_sphinx.json](../../../data/wave1-phf/enrich/raw/github_com_sfmqrb_sphinx.json) (enrichment confidence 0.8)

</details>
