# Pison

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [JSON](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `MIT` · 🟡 stale

> Multithreaded SIMD structural-index builder and path iterator for single huge JSON records; beats simdjson/RapidJSON end-to-end using 8 threads.

| | |
|---|---|
| **Beats** | RapidJSON, simdjson |
| **Claimed result** | README: "parallel Pison achieves 5.4X and 3.1X speedups (on average) over simdjson on Server 1 (with 8 threads) and Server 2 (with 4 threads)"; "both Pison and simdjson outperform RapidJSON"; serial Pison is "comparable to simdjson". README Fig.1 (Server 1) geo-mean end-to-end: RapidJSON 4.98s, simdjson 1.78s, Pison(1) 1.31s, Pison(8) 0.33s, about 15x vs RapidJSON (derived from page data). Peer-reviewed PVLDB'21 paper (section 6.4, Table 5, 16-core server): parallel Pison with 8 threads is 12.2X faster than RapidJSON and 4.6X faster than simdjson end-to-end. |
| **Workload** | Parallel structural-index construction plus JSONPath query evaluation over \~1GB single JSON records (Twitter, BestBuy, Google Maps Directions, UK NSPL, Walmart, Wikipedia datasets) on 16-core and 4-core Xeon servers |
| **Metric** | throughput |
| **Hardware** | Server 1 (paper and README): 16-core, two Intel Xeon E5-2620 v4 @2.1GHz, 64GB RAM, CentOS 7; Server 2 (README only): 4-core Intel Xeon E3-1240 v5 @3.5GHz, 16GB RAM |
| **Compiler and flags** | G++ 7.4.0 with -O3 on CentOS 7 (PVLDB'21 paper section 6.1); repo makefile builds with g++ -O3 -std=c++11 -mavx -mavx2 -msse -msse2 -msse4 -msse4.2 -mpclmul; README lists g++ 7.4.0 or higher as prerequisite |
| **Adoption** | 27 stars; VLDB 2021 paper (PVLDB 14(4):694-707) |
| **Last commit** | 2024-10-10 |
| **Links** | [repository](https://github.com/AutomataLab/Pison) · [benchmark](https://github.com/AutomataLab/Pison#performance-results) |

## Verdict

The PVLDB'21 paper (G++ 7.4.0 -O3, CentOS 7, 16-core 2x Xeon E5-2620 v4) times index construction plus JSONPath queries over six \~1GB single-record datasets. Pison with 8 threads is 12.2X faster than RapidJSON, 4.6X faster than simdjson, and 4.2X faster than serial Pison. Serial Pison is roughly even with simdjson. The README's 5.4X (Server 1, 8 threads) and 3.1X (4-core Xeon E3-1240 v5, 4 threads) figures compare multithreaded Pison with single-threaded baselines whose 2020-era versions are not stated.

## Use it when

- Extracting a few paths (for example \$.routes[\*].legs[\*].steps[\*].distance.text) from one very large JSON document, from hundreds of MB to about 1GB, on a multi-core Linux x86-64 server where you can spend 4-8 cores to cut end-to-end latency.
- Running several queries against the same large record: the index is built once and reused (the paper's Twitter workload shares one index across 8 queries).
- Queries that only reach a few levels deep: pass level_num so bitmaps are built only for the depths the query touches.
- Research or prototyping of Mison-style structural-index JSON analytics, where a small (about 3.3K lines) MIT codebase is easy to read and change.

## Skip it when

- You need a DOM, typed values, JSON validation, or serialization. Pison only finds raw value text, and index construction has no error path for malformed input.
- Streams of many small records: the README reports only serial Pison there, example3 says parallel construction for record sets is 'TBD', and serial Pison is about even with simdjson (paper Table 5 sum 12.14s vs 11.9s).
- Non-Linux or non-x86 targets: it requires AVX2 and pclmulqdq, uses pthread_setaffinity_np and malloc.h, and has no NEON or scalar fallback.
- A single streaming query over a big file, where JSONSki (same lab) says it is about 3x faster than Pison. Also avoid it under tight memory: the paper's Figure 18 reports about 3.0GB average footprint for about 1GB records.
- Production code that sees untrusted input. This is research-grade code with fixed-size buffers and no bounds checks. Parallel mode segfaulted at -O1 and above until a missing return was fixed in October 2023 (issue #2, PR #5).

## How it is fast

Each 64-byte word goes through bit-parallel steps taken from Mison and simdjson: AVX2 compare+movemask builds the structural-character bitmaps, carry arithmetic finds odd backslash runs, and a pclmulqdq prefix-XOR builds the string mask. Leveled bitmaps are then built word by word rather than step by step, which cuts memory traffic (the paper reports 40.8% less memory than step-by-step). To parallelize one record, Pison splits the text into per-thread chunks. Contradiction-based context inference (tokenize a chunk's first 64 bytes as inside-string and as outside-string; a token error rules one out) decides each chunk's string state. When inference fails, Pison speculates and repairs a wrong guess by flipping that chunk's string-mask bitmap. Per-chunk leveled bitmaps are then merged by re-basing their relative levels. Queries only build and touch the levels they need (level_num).

## Compared with alternatives

Pick Pison over simdjson or RapidJSON when the input is one very large JSON record, you need only a handful of paths, and you can spend 4-8 cores: the parallel index build is where its end-to-end win over simdjson comes from. For a single streaming query, JSONSki (same lab) reports about 3x faster than Pison. For general parsing, DOM access, or small documents, simdjson or yyjson are the safer picks.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none beyond pthreads and the C++ standard library |
| **Minimum toolchain** | C++11; g++ 7.4.0+ (README); makefile uses -O3 -mavx -mavx2 -msse4.2 -mpclmul |
| **Platforms** | Linux x86-64 only (AVX2 and pclmulqdq required; CPU pinning via pthread_setaffinity_np) |
| **Thread safety** | Not safe for concurrent parallel use: ParallelBitmapConstructor keeps the bitmap and thread arrays in static members, and ParallelBitmapIterator uses file-scope global arrays. The README's getCopy() gives separate iterators for querying one index from several threads. Nothing else is documented. |
| **Drop-in for the baseline** | no |

## Gotchas

- getValue() returns a malloc'd copy of the raw text between structural characters, including leading whitespace and string quotes, and the caller must free() it. On some edge paths it returns the string literal "", and the examples' pattern `if (value) free(value)` would then free a literal.
- Index depth is capped at MAX_LEVEL = 22, and deeper levels are silently left unindexed. down() skips only spaces and newlines before a nested value, so tabs or carriage returns there make it return false. The context-inference tokenizer treats a carriage return as a token error, so CRLF-formatted input may get the wrong string state in parallel mode (inferred from code, not documented).
- Memory-safety edges: loadSingleRecord writes its NUL terminator one byte past the buffer when the file size is a multiple of 64. loadRecords strcpy's into a buffer with no room for the terminator and reads lines through a 1MB stack buffer. Iterator position arrays are fixed-size guesses with no bounds checks (for example 125,001 entries for getCopy() iterators).
- Input must be padded to a multiple of 64 bytes, which RecordLoader does with 'd' filler. Worker i is pinned to CPU i (at most 70 threads). Chunk offsets and word loop counters are 32-bit int, so treat records over 2GB as untested in this code.

## Known shortcomings

- The headline wins pit 8- or 4-thread Pison against single-threaded simdjson and RapidJSON; serial Pison is about even with simdjson, and the metric is end-to-end time, not throughput. Not a drop-in: bitmap index plus iterator, no DOM, no validation, raw value text. Memory-safety bugs from reading the source (one-byte overflows in the loaders, unchecked fixed-size position arrays), parallel state in statics so not thread-safe, CRLF input may misparse, nesting capped at 22 levels. Linux x86-64 AVX2 only. JSONSki from the same lab is about 3x faster.

## Caveats and trade-offs

Headline win compares multithreaded Pison (8 or 4 threads) with single-threaded simdjson/RapidJSON. Serial Pison is about parity with simdjson (paper Table 5: sum 12.14s vs 11.9s, geo-mean 1.76s vs 1.93s). README 5.4X/3.1X numbers come from a different query set (one TT query vs the paper's TT1-TT8); the Server 2 results are not in the paper. simdjson/RapidJSON versions are unstated (2020 era); no baseline harness is published in the repo. x86 AVX2+pclmul, Linux only; repo stale since 2024-10-10.

Requires Linux plus a CPU with pclmulqdq/256-bit SIMD; builds a leveled bitmap structural index rather than a full DOM, so the downstream query API differs from RapidJSON/simdjson; parallel speedup depends on having large single records and enough cores

## Maintenance

Stale research code: the last source fix was October 2023, the last commit (README only) was 2024-10-10, and two outside PRs are still open. It is MIT-licensed and about 3.3K lines, so vendoring and patching it is practical.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed PVLDB 14(4) paper (read in full; section 6) shows end-to-end wins over RapidJSON (12.2X) and simdjson (4.6X), and states G++ 7.4.0, -O3, 2x Xeon E5-2620 v4. It stays B, not A, because the repo has no baseline harness (only src/ and example/) and baseline versions are unstated.
- **Verifier notes:** README figures confirm 5.4X (1.78/0.33) and 3.1X (0.78/0.25) vs simdjson. The peer-reviewed paper gives 4.6X vs simdjson and 12.2X vs RapidJSON, so B rests on the paper. The metric field says throughput, but the source measures end-to-end execution time. The metric field is outside the allowed corrections, so it was left unchanged.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/AutomataLab/Pison>
  - <https://github.com/AutomataLab/Pison#performance-results>
  - <https://github.com/AutomataLab/Pison/blob/master/doc/compare_large_server1.png>
  - <https://github.com/AutomataLab/Pison/blob/master/doc/compare_large_server2.png>
  - <https://github.com/AutomataLab/Pison/blob/master/doc/compare_large_server3.png>
  - <https://github.com/AutomataLab/Pison/blob/master/doc/compare_small_server1.png>
  - <https://github.com/AutomataLab/Pison/blob/master/doc/compare_small_server2.png>
  - <https://github.com/AutomataLab/Pison/blob/master/makefile>
  - <https://github.com/AutomataLab/Pison/blob/master/LICENSE.md>
  - <http://vldb.org/pvldb/vol14/p694-zhao.pdf>
- **Sources the enricher read:**
  - <https://github.com/AutomataLab/Pison>
  - <https://github.com/AutomataLab/Pison#performance-results>
  - <https://github.com/AutomataLab/Pison/blob/master/makefile>
  - <https://github.com/AutomataLab/Pison/blob/master/src/Bitmap.h>
  - <https://github.com/AutomataLab/Pison/blob/master/src/BitmapConstructor.h>
  - <https://github.com/AutomataLab/Pison/blob/master/src/BitmapConstructor.cpp>
  - <https://github.com/AutomataLab/Pison/blob/master/src/BitmapIterator.h>
  - <https://github.com/AutomataLab/Pison/blob/master/src/Records.h>
  - <https://github.com/AutomataLab/Pison/blob/master/src/RecordLoader.h>
  - <https://github.com/AutomataLab/Pison/blob/master/src/RecordLoader.cpp>
  - <https://github.com/AutomataLab/Pison/blob/master/src/SerialBitmap.h>
  - <https://github.com/AutomataLab/Pison/blob/master/src/SerialBitmap.cpp>
  - <https://github.com/AutomataLab/Pison/blob/master/src/SerialBitmapConstructor.cpp>
  - <https://github.com/AutomataLab/Pison/blob/master/src/SerialBitmapIterator.cpp>
  - <https://github.com/AutomataLab/Pison/blob/master/src/ParallelBitmap.h>
  - <https://github.com/AutomataLab/Pison/blob/master/src/ParallelBitmap.cpp>
  - <https://github.com/AutomataLab/Pison/blob/master/src/ParallelBitmapConstructor.h>
  - <https://github.com/AutomataLab/Pison/blob/master/src/ParallelBitmapConstructor.cpp>
  - <https://github.com/AutomataLab/Pison/blob/master/src/ParallelBitmapIterator.h>
  - <https://github.com/AutomataLab/Pison/blob/master/src/ParallelBitmapIterator.cpp>
  - <https://github.com/AutomataLab/Pison/blob/master/src/LocalBitmap.h>
  - <https://github.com/AutomataLab/Pison/blob/master/src/LocalBitmap.cpp>
  - <https://github.com/AutomataLab/Pison/blob/master/src/Tokenizer.h>
  - <https://github.com/AutomataLab/Pison/blob/master/src/Tokenizer.cpp>
  - <https://github.com/AutomataLab/Pison/blob/master/example/example1.cpp>
  - <https://github.com/AutomataLab/Pison/blob/master/example/example2.cpp>
  - <https://github.com/AutomataLab/Pison/blob/master/example/example3.cpp>
  - <https://github.com/AutomataLab/Pison/issues/2>
  - <https://github.com/AutomataLab/Pison/pull/4>
  - <https://github.com/AutomataLab/Pison/pull/5>
  - <https://github.com/AutomataLab/Pison/pull/6>
  - <https://github.com/AutomataLab/Pison/commits/master>
  - <http://vldb.org/pvldb/vol14/p694-zhao.pdf>
  - <https://github.com/AutomataLab/JSONSki>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/automatalab/pison`) · [data/wave4/enrich/raw/github_com_automatalab_pison.json](../../../data/wave4/enrich/raw/github_com_automatalab_pison.json) (enrichment confidence 0.8)

</details>
