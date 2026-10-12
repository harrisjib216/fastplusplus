# Binary Fuse Filter demo (FastFilter/FilterPassword)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Probabilistic filters](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `no license` · 🟡 stale

> Demo CLI pair that builds an mmap-queried binary fuse filter over HaveIBeenPwned SHA1 prefixes, with a Bloom filter for comparison.

| | |
|---|---|
| **Beats** | Bloom filter |
| **Claimed result** | Construction: 0.420s vs 0.613s for bloom12 (\~1.46x faster, derived from page data). Serialized size: 11,272,228 vs 15,000,024 bytes (\~1.33x smaller, derived from page data). Single-query processing time: 241 µs vs 344 µs, which the tool reports as 4149.377 vs 2906.977 expected queries/sec (\~1.43x, derived from page data). All figures come from one-off runs. |
| **Workload** | Build & query benchmark over 10M password-hash-derived 64-bit keys (HaveIBeenPwned SHA1 list) comparing a binaryfuse8 filter vs a bloom12 filter built and queried with the project's build_filter/query_filter CLI tools. |
| **Metric** | throughput |
| **Compiler and flags** | The Makefile builds with 'c++ -O3 -std=c++11'. The compiler and version used for the README run are not stated; CI runs GCC 11 on Ubuntu 22.04, but that is only a sanitized build/test job, not the benchmark run. |
| **Adoption** | 50 stars |
| **Last commit** | 2024-12-09 |
| **Links** | [repository](https://github.com/FastFilter/FilterPassword) · [benchmark](https://github.com/FastFilter/FilterPassword#performance-comparisons) |

## Verdict

The data comes from single CLI runs on an undisclosed machine and compiler (the Makefile builds with c++ -O3 -std=c++11) over the first 10M 64-bit prefixes of the HIBP v4 ordered-by-count SHA1 list. binaryfuse8 took 0.420 s of CPU time to construct vs 0.613 s for a classic unblocked k=8, 12-bit/key Bloom filter, and wrote 11.27 MB vs 15.00 MB, at a slightly higher false-positive rate (2^-8 ≈ 0.39% vs about 0.32% for the Bloom filter, measured by a user in issue #4). Only the build-time and size figures stand. The one-shot query timings include open and mmap, and the binary fuse query hit a since-fixed header-parsing bug and gave a wrong answer.

## Use it when

- You want a small, readable end-to-end example of building a static membership filter offline and querying it through mmap without loading it into RAM.
- Offline or batch screening of password hashes against an HIBP-style list, where a \~0.4% false-positive rate (2^-8 for binaryfuse8) is acceptable and an exact lookup follows on a hit.
- Comparing the file size and build time of binaryfuse8, binaryfuse16, xor8 and bloom12 on your own 64-bit-keyed data with one tool (-f picks the filter type, -V checks for false negatives and estimates the false-positive rate).
- Sets of tens to a few hundred million keys on a Linux or macOS box with plenty of RAM for the one-time build.

## Skip it when

- Anything you ship or depend on: the maintainer calls it a demonstration and not a library (README, issue #9), and the repo has no LICENSE file. Build on xor_singleheader instead; the maintainer says it is Apache-licensed.
- Sets that change: the filter is build-once and immutable, with no insert or delete.
- Build machines with little RAM: construction needs up to \~64 bytes/key (README), the full list is said to need 64 GB, and build_filter reserves a fixed \~5 GB key buffer (600\*1024\*1024 uint64 slots) whatever -m is set to.
- Current full HIBP dumps (issue #9 puts them near 1 billion records): past 629,145,600 input lines, read_data grows the buffer with realloc(array, array_capacity), which passes an element count as a byte count, so the buffer shrinks and later writes overflow the heap. HIBP also no longer ships the ordered-by-count 7z file the README tells you to download (issue #9).
- Measuring or serving high query throughput: query_filter answers one key per process, and there is no batch or server mode (issue #1 has been open since 2019).
- Windows: the README expects Linux or macOS, and the code uses POSIX getline, getopt and mmap.

## How it is fast

The default filter is an 8-bit binary fuse filter (Graf & Lemire, arXiv 2201.01174), taken from the pinned xor_singleheader submodule. Each key is mixed with a murmur64 finalizer and mapped to 3 byte slots in 3 adjacent segments. A lookup XORs those 3 bytes against the key's fingerprint, so it always costs exactly 3 memory reads. The table has about 1.125 slots per key (about 9 bits/key at 10M keys; the README's file is 11.27 MB). Construction peels a 3-uniform hypergraph, like xor filters, but first bucket-sorts the hashes by segment block so memory accesses stay local. The bloom12 baseline is fastfilter_cpp's classic unblocked Bloom filter: 12 bits/key, k=8 double-hashed probes into random 64-bit words, so a positive lookup can take up to 8 cache misses and the file is 15 MB.

## Compared with alternatives

Pick it only as a runnable, HIBP-shaped reference for the build-once, mmap-and-query pattern. For code you ship, use Xor Filter (xor_singleheader), which this repo wraps and which has built-in serialize/deserialize, or xorfilter (Go) or xorf (Rust) in those languages. Use Boost.Bloom if you need incremental inserts or a cache-blocked Bloom filter, which is a stronger baseline than the unblocked bloom12 used here.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | git submodules FastFilter/xor_singleheader (binary fuse and xor filters, pinned at 3c0fd15) and FastFilter/fastfilter_cpp (the bloom12 baseline only, pinned at 0e85974); bundled TinySHA1 header (src/sha.h); POSIX getline, getopt and mmap |
| **Minimum toolchain** | C++11 (Makefile: c++ -O3 -std=c++11; CMakeLists needs CMake 3.10+). The CI workflow is labelled GCC 11 on Ubuntu 22.04, but no CI check is recorded on the latest commit. Without __uint128_t, fastrange64 falls back to a modulo. |
| **Platforms** | Linux and macOS (README). Any 64-bit POSIX system should work. Filter files are raw native-endian structs with no endianness or version marker. |
| **Thread safety** | The README says the filter is immutable and so safe to share in multithreaded applications. Both CLI tools are single-threaded and query_filter does one lookup per process. |
| **Drop-in for the baseline** | no |

## Gotchas

- The README benchmark block was written on 2021-06-03 (commit 202f2180), before commit c5eac973 (2021-11-01, issue #6) fixed query_filter so it reads SegmentLengthMask from the binary fuse file header. In that block, binaryfuse8 answers 'Surely not in the set' for 7C4A8D09CA3762AF, the SHA1 prefix of '123456', which the README's own full-list example reports as present. It also 'expects' 11,206,692 bytes for a file it wrote as 11,272,228 bytes. That query result is a false negative from the old bug, so the 241 us vs 344 us comparison is void.
- The example query keys in the README have 17 hex characters (7C4A8D09CA3762AF6). The current query_filter rejects any key that is not exactly 16 characters, so the README output cannot be reproduced as written.
- The timings use clock(), which is CPU time, not wall time. 'Processing time' and 'Expected number of queries per second' cover fopen, the header read, mmap and page-faulting a single lookup. They do not measure lookup cost; a bulk benchmark with the same filter family cited in issue #1 reports about 50 ns per query.
- Latent limits in the pinned xor_singleheader: key counts go through uint32_t parameters, so more than 4,294,967,295 keys would be silently truncated. Its duplicate-removal qsort comparator also casts a uint64_t difference to int, which is not a valid ordering if 64-bit prefixes ever collide. The same comparator is still on upstream master.

## Known shortcomings

- A demo program rather than a library; ratios are derived from README numbers; the CI badge machine differs from the benchmark machine.
- The README query numbers are void: they predate a header-parse fix (2021-11, #6), and binaryfuse8 then gave a false negative for SHA1('123456'); README keys are 17 hex chars while the current query tool accepts exactly 16. Timing is clock() CPU time over open+mmap+one lookup. build_filter's realloc passes an element count as bytes, so input beyond 629,145,600 lines overflows the heap (current HIBP \~1B lines). No LICENSE; demo only (use xor_singleheader).

## Caveats and trade-offs

The numbers are single-run wall-clock output copied from example README commands, not repeated or averaged, and the CPU model is not stated. The query comparison is one query per filter, and those times likely include memory-mapping and page-fault costs. The two example queries also gave different answers for the same key: binaryfuse8 printed 'Surely not in the set' and bloom12 printed 'Probably in the set', so the single-query times are not like-for-like. The repo has no LICENSE file (GitHub license API returns 404). The README says the reusable library is FastFilter/xor_singleheader.

Filter is immutable (build-once, no add/remove); construction needs \~64 bytes/entry RAM even though the finished filter uses \~1 byte/entry; project explicitly a demonstration, not the library to depend on (library is FastFilter/xor_singleheader).

## Maintenance

Stale: the last commit is 2024-12-09 (a dependency tidy and a CMake file), the repo has 50 stars and no LICENSE, and the maintainer describes it as a demonstration, so read it for the pattern and build on xor_singleheader.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README 'Performance comparisons' section shows first-party, single-run CLI output for binaryfuse8 against bloom12 over 10M HIBP hashes. The code is public (src/build_filter.cpp, src/query_filter.cpp, built with -O3), but the page gives no CPU model and no compiler for the run. That makes it C.
- **Verifier notes:** Every number in the claim is on the README. The only fixes are marking the ratios as derived from page data and correcting compiler_and_flags, since the CI badge does not describe the benchmark machine. No license, so 'reference' is correct. The last commit is 2024-12-09 and 50 stars is correct.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/FastFilter/FilterPassword>
  - <https://github.com/FastFilter/FilterPassword#performance-comparisons>
  - <https://github.com/FastFilter/FilterPassword/blob/master/Makefile>
  - <https://github.com/FastFilter/FilterPassword/blob/master/.github/workflows/ubuntu.yml>
- **Sources the enricher read:**
  - <https://github.com/FastFilter/FilterPassword>
  - <https://github.com/FastFilter/FilterPassword#performance-comparisons>
  - <https://github.com/FastFilter/FilterPassword/blob/master/src/build_filter.cpp>
  - <https://github.com/FastFilter/FilterPassword/blob/master/src/query_filter.cpp>
  - <https://github.com/FastFilter/FilterPassword/blob/master/src/mappeablebloomfilter.h>
  - <https://github.com/FastFilter/FilterPassword/blob/master/src/util.h>
  - <https://github.com/FastFilter/FilterPassword/blob/master/src/hexutil.h>
  - <https://github.com/FastFilter/FilterPassword/blob/master/src/sha.h>
  - <https://github.com/FastFilter/FilterPassword/blob/master/Makefile>
  - <https://github.com/FastFilter/FilterPassword/blob/master/CMakeLists.txt>
  - <https://github.com/FastFilter/FilterPassword/blob/master/.gitmodules>
  - <https://github.com/FastFilter/FilterPassword/blob/master/.github/workflows/ubuntu.yml>
  - <https://github.com/FastFilter/FilterPassword/commits/master>
  - <https://github.com/FastFilter/FilterPassword/blame/master/README.md>
  - <https://github.com/FastFilter/FilterPassword/issues/1>
  - <https://github.com/FastFilter/FilterPassword/issues/2>
  - <https://github.com/FastFilter/FilterPassword/issues/4>
  - <https://github.com/FastFilter/FilterPassword/issues/6>
  - <https://github.com/FastFilter/FilterPassword/issues/7>
  - <https://github.com/FastFilter/FilterPassword/issues/8>
  - <https://github.com/FastFilter/FilterPassword/issues/9>
  - <https://github.com/FastFilter/FilterPassword/commit/c5eac973df91e29cdb5cee0c105744cd69a26325.diff>
  - <https://github.com/FastFilter/FilterPassword/commit/202f2180.diff>
  - <https://raw.githubusercontent.com/FastFilter/xor_singleheader/3c0fd15b1e04281b2ada00cf82ddffc4b3292dee/include/binaryfusefilter.h>
  - <https://raw.githubusercontent.com/FastFilter/xor_singleheader/master/include/binaryfusefilter.h>
  - <https://raw.githubusercontent.com/FastFilter/fastfilter_cpp/0e859745bf2b08b07dcf5845a2bab23c0245c39b/src/bloom/bloom.h>
  - <http://export.arxiv.org/api/query?id_list=2201.01174>
  - <https://hn.algolia.com/api/v1/search?query=FilterPassword&tags=story>
  - <https://hn.algolia.com/api/v1/search?query=%22FastFilter%2FFilterPassword%22>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/fastfilter/filterpassword`) · [data/wave6/enrich/raw/github_com_fastfilter_filterpassword.json](../../../data/wave6/enrich/raw/github_com_fastfilter_filterpassword.json) (enrichment confidence 0.85)

</details>
