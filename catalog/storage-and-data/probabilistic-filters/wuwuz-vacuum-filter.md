# Vacuum Filter

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Probabilistic filters](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `MIT` · 🟡 stale

> Deletable cuckoo-filter variant allowing any table size; \~25% less space than cuckoo on average, smaller than Bloom below 3% FPR.

| | |
|---|---|
| **Beats** | Bloom filter, cuckoo filter |
| **Claimed result** | Abstract: about 25% less space on average and similar throughput vs cuckoo filters, and about 15% less space and &gt;10x throughput vs Bloom filters, at the same false-positive rate. In memory: VF-ss is about 1.1x-1.8x faster than CF-ss for positive lookups. VFs have the highest lookup throughput below 90% occupancy, but CFs are slightly better at high occupancy. VFs have the highest insertion throughput below 65% occupancy, and deletion throughput is similar to CFs. On SSD with a 100 MB memory limit, VF lookups are 1.86x-2.13x faster than CF. Space: VFs save 2-5 bits per item vs the other methods in the average case (about 5 fewer bits vs CFs). |
| **Workload** | Positive/mixed lookup, insertion, and deletion throughput plus bits-per-item vs. target false-positive rate, 64-bit random keys, varying table occupancy 0-100%, on a DELL workstation (PVLDB 13, 2020) |
| **Metric** | throughput |
| **Hardware** | DELL workstation, Intel Xeon E5-2687W @ 3.00GHz, 30MB L3 cache, SK-hynix SC311-S 1TB SSD |
| **Compiler and flags** | Not stated in the paper. The repo makefile builds the test.cpp demo with g++ -Ofast -march=native -mpopcnt -std=c++14 (plus -pg -g). |
| **Adoption** | 54 stars; PVLDB 13(2), 2020 |
| **Last commit** | 2024-11-23 |
| **Links** | [repository](https://github.com/wuwuz/Vacuum-Filter) · [benchmark](http://www.vldb.org/pvldb/vol13/p197-wang.pdf) |

## Verdict

The PVLDB 2020 paper ran on an Intel Xeon E5-2687W (3.0 GHz, 30 MB L3) with the compiler and flags not stated, using 0.95x2^27 random 64-bit keys in 192 MB filters with 12-bit fingerprints (13-bit semi-sorted), against Fan et al.'s CF code, the authors' own Bloom/BBF/DIBF and the published MF/CQF code. VF-ss did positive lookups 1.1-1.8x faster than CF-ss and tied on deletes, and VF had the highest lookup throughput below 90% occupancy and the highest insert throughput below 65%. The \~25%-less-space-than-CF result comes mainly from CF's power-of-two table rounding. The '&gt;10x vs Bloom' headline uses the authors' own Bloom implementation, which an xor-filter co-author on HN called un-optimized (other papers show about 2x for CF over Bloom). No std:: container is compared.

## Use it when

- Dynamic sets of 64-bit integer (or pre-hashed) keys that need deletes, where the item count is known up front and is not near 3.8x2^k: there a cuckoo filter must round up to a power-of-two table (the paper's 274,926-cert set: VF-ss 12.9 vs CF-ss 21.0 bits/item at 0.1% FPR, similar lookup speed).
- Target false-positive rates below about 3% (e.g. 0.1%-0.01%), where VF-ss needs about 2.07 + 1.05\*log2(1/eps) bits/item and beats Bloom on space.
- Filters much larger than the last-level cache, or on SSD/mmap, where two-bucket locality matters (the paper measured 1.86-2.13x faster lookups than CF on SSD with a 100 MB memory limit).
- Bulk loads and probes that can use the 128-key batch APIs with padded arrays.
- Research or prototyping where you will vendor and patch the headers yourself.

## Skip it when

- Static or build-once sets: xor/binary fuse or ribbon filters are smaller and faster to query.
- Filters run near full (&gt;90% occupancy for lookups, &gt;65% for inserts): the paper shows cuckoo filters tie or win there.
- You need resizing, duplicate-insert tolerance, serialization or concurrent access: the paper's IUPR/dynamic-VF framework is not in the repo, there is no save/load API, and there is no locking. Inserting the same key 9 times overflows its 8 candidate slots.
- Tiny filters, or FPR above 3%: the fast version rounds the table up to a multiple of at least 1,024 buckets (wasteful below about 4k keys), and above 3% FPR Bloom is smaller.
- Space is not tight and raw lookup speed is the goal: TUM's 2021 partitioned-filters study found that non-power-of-two addressing mostly slows cuckoo/Morton filters and recommends power-of-two tables in that case.

## How it is fast

The table is split into power-of-two chunks, and the alternate bucket is B1 XOR (H(f) mod L), so both candidate buckets sit in the same chunk. The table then only needs to be a multiple of L, not a power of two. A multi-range alternate function uses the fingerprint's low 2 bits to pick one of 4 range sizes, each sized with a balls-into-bins bound for 95% load. Most keys get small ranges and so better cache/TLB locality: the paper's Table 2 reports 75% of bucket pairs in the same 4 KB page, versus 0.83% with a single range. Insertion looks one step ahead, checking the alternates of all 8 fingerprints in the two full buckets before a random-walk kick; bucket indexes use the multiply-shift (x\*m)&gt;&gt;32 range reduction; lookups use the CF's SWAR bit-trick tag compare; and optional semi-sorting saves 1 bit per item.

## Compared with alternatives

Pick it over Xor/Binary Fuse and BuRR when the set changes and you need deletions, since those are build-once. Pick it over Prefix Filter when you need deletes: Prefix Filter's README calls it an incremental (insert-only) filter. Against Morton Filter, the other deletable cuckoo variant, the VF paper reports lower memory in all its tested cases and support for arbitrary fingerprint lengths; SuRF solves range queries, a different problem.

## Integration

| | |
|---|---|
| **Form** | source-drop (header-only templates: vacuum.h + hashutil.h, or ModifiedCuckooFilter/src/\*.h; no CMake/package, only demo makefiles) |
| **Dependencies** | vacuum.h: standard library only. Fast version: ModifiedCuckooFilter/src/hashutil.h includes &lt;openssl/evp.h&gt;, so it needs OpenSSL headers to compile (it links -lssl -lcrypto only if hashutil.cc is used). |
| **Minimum toolchain** | C++14 per the top-level makefile (C++11 in the CF subdirectory). GCC/Clang only: needs unsigned __int128, __attribute__((packed)), and &lt;bits/stdc++.h&gt; in the demo. No tested compiler versions are documented. |
| **Platforms** | 64-bit little-endian. The paper tested x86-64 (Xeon E5-2687W) and the makefile uses -march=native -mpopcnt. No SIMD intrinsics are needed, but the code does unaligned 64-bit loads. |
| **Thread safety** | Not documented. There is no synchronization, and inserts use the global rand() (the fast constructor also calls srand(1)). Treat it as single-threaded and lock writers externally. |
| **Drop-in for the baseline** | partial: the fast version keeps efficient/cuckoofilter's constructor and Add/Contain/Delete Status API, so a CF user mostly just renames the type. It has no Bloom-style API, and keys must be 64-bit integers. |

## Gotchas

- A failed insert silently drops an older key. When vacuum.h insert() or the batch Add_many()/evict() runs out of kicks, it returns false after placing the new fingerprint and discards the last evicted one, so a previously inserted key can start returning false negatives. Rebuild on any failure.
- The batch APIs assume key and result arrays padded to a multiple of 128. Contain_many always processes full 128-key batches, and all \*_many calls memcpy 128 results, so unpadded arrays are read and written out of bounds. Contain_many also ignores the victim slot.
- The headers are not ODR-safe. Non-inline free functions (upperpower2, solve_equation, proper_alt_range, a global max(int,int)) break linking if included in 2+ translation units. They also define global macros (MIN, MAX, ROUNDUP, debug), and hashutil.h does a global 'using namespace std'. vacuum.h uses assert/log without including &lt;cassert&gt;/&lt;cmath&gt;, and its include guard is named CUCKOO_H.
- Side effects and fixed hashing: the fast constructor prints alt ranges to std::cout and reseeds rand(). Each vacuum.h object embeds 512 KiB of encode/decode tables (the demo puts one on the stack). Hash seeds are fixed (mt19937(1), constant MurmurHash64), so adversarial keys can force insert failures. Deleting a key that was never inserted can remove another key's fingerprint.

## Known shortcomings

- Correctness: a failed insert evicts an older fingerprint (vacuum.h insert, Add_many/evict), causing false negatives. \*_many batch calls overrun unless arrays are padded to 128. Headers aren't ODR-safe (non-inline functions, global max, macros, using namespace std); the fast constructor prints to cout and calls srand(1); the fast version needs OpenSSL headers and __int128 (GCC/Clang only). The paper's resize and duplicate-insert variants (IUPR/DVF) aren't in the repo; no serialization or thread safety; fixed unseeded hashes. The '&gt;10x vs Bloom' used an unoptimized Bloom (per an xor-filter co-author), and the space win mostly comes from cuckoo's power-of-2 rounding; cuckoo ties or wins above 90% occupancy. Code frozen since 2019-10 (only a 2024 LICENSE commit).

## Caveats and trade-offs

The paper gives the CPU but no compiler or flags. The repo has no harness for the Bloom, Morton and CQF comparisons, only the test.cpp demo and Fan et al.'s inherited CF benchmarks under ModifiedCuckooFilter/. The top-level license is MIT, added 2024-11-23. ModifiedCuckooFilter/ is Apache-2.0 code derived from CMU/Intel's cuckoofilter. The throughput advantage over cuckoo filters is small or reversed at high occupancy.

Built on top of / modified from Fan et al.'s cuckoo filter code; the fast implementation is a modified cuckoo filter rather than a from-scratch design; deletion throughput is only 'similar to' cuckoo filter, not better; insertion advantage narrows and eventually loses to cuckoo/vacuum crossover above \~65% occupancy where both slow down comparably.

## Maintenance

Research code frozen since October 2019: the only later commit (2024-11-23) added the MIT LICENSE, and a 2021 license question is still open with no reply. It is MIT, with an Apache-2.0 subdirectory derived from CMU/Intel's cuckoofilter, and small enough to vendor, but expect to patch the ODR, batch-overrun and stdout issues before production use. A Java port exists in Alibaba's mpc4j, and TUM's partitioned-filters repo vendors the code.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** The peer-reviewed PVLDB 13 paper compares vacuum filters against Bloom, blocked Bloom, cuckoo, Morton and CQF filters on a stated Intel E5-2687W CPU. It gives no compiler or flags. The repo has only a demo (test.cpp), not the comparison harness, so the entry cannot be tier A.
- **Verifier notes:** The numbers match Sec. 6.2. The abstract's '&gt;10x throughput vs Bloom filters' headline was added. The '2-5 fewer bits' claim is scoped to the paper's average case. Metadata checks out: MIT (plus an Apache-2.0 subdirectory), 54 stars, last commit 2024-11-23, stale.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `compared_against_cpp_std_directly`, `caveats`
- **Pages the verifier opened:**
  - <http://www.vldb.org/pvldb/vol13/p197-wang.pdf>
  - <https://github.com/wuwuz/Vacuum-Filter>
  - <https://raw.githubusercontent.com/wuwuz/Vacuum-Filter/master/README.md>
  - <https://raw.githubusercontent.com/wuwuz/Vacuum-Filter/master/LICENSE>
  - <https://raw.githubusercontent.com/wuwuz/Vacuum-Filter/master/ModifiedCuckooFilter/LICENSE>
  - <https://raw.githubusercontent.com/wuwuz/Vacuum-Filter/master/makefile>
  - <https://raw.githubusercontent.com/wuwuz/Vacuum-Filter/master/test.cpp>
- **Sources the enricher read:**
  - <https://github.com/wuwuz/Vacuum-Filter>
  - <https://github.com/wuwuz/Vacuum-Filter/blob/master/README.md>
  - <https://github.com/wuwuz/Vacuum-Filter/blob/master/makefile>
  - <https://github.com/wuwuz/Vacuum-Filter/blob/master/test.cpp>
  - <https://github.com/wuwuz/Vacuum-Filter/blob/master/vacuum.h>
  - <https://github.com/wuwuz/Vacuum-Filter/blob/master/hashutil.h>
  - <https://github.com/wuwuz/Vacuum-Filter/blob/master/LICENSE>
  - <https://github.com/wuwuz/Vacuum-Filter/blob/master/ModifiedCuckooFilter/README.md>
  - <https://github.com/wuwuz/Vacuum-Filter/blob/master/ModifiedCuckooFilter/LICENSE>
  - <https://github.com/wuwuz/Vacuum-Filter/blob/master/ModifiedCuckooFilter/Makefile>
  - <https://github.com/wuwuz/Vacuum-Filter/blob/master/ModifiedCuckooFilter/src/cuckoofilter.h>
  - <https://github.com/wuwuz/Vacuum-Filter/blob/master/ModifiedCuckooFilter/src/singletable.h>
  - <https://github.com/wuwuz/Vacuum-Filter/blob/master/ModifiedCuckooFilter/src/packedtable.h>
  - <https://github.com/wuwuz/Vacuum-Filter/blob/master/ModifiedCuckooFilter/src/hashutil.h>
  - <https://github.com/wuwuz/Vacuum-Filter/blob/master/ModifiedCuckooFilter/src/bitsutil.h>
  - <https://github.com/wuwuz/Vacuum-Filter/blob/master/ModifiedCuckooFilter/src/permencoding.h>
  - <https://github.com/wuwuz/Vacuum-Filter/blob/master/ModifiedCuckooFilter/src/debug.h>
  - <https://github.com/wuwuz/Vacuum-Filter/blob/master/ModifiedCuckooFilter/benchmarks/bulk-insert-and-query.cc>
  - <https://github.com/wuwuz/Vacuum-Filter/blob/master/ModifiedCuckooFilter/benchmarks/Makefile>
  - <https://github.com/wuwuz/Vacuum-Filter/issues/1>
  - <https://github.com/wuwuz/Vacuum-Filter/commits/master>
  - <http://www.vldb.org/pvldb/vol13/p197-wang.pdf>
  - <https://hn.algolia.com/api/v1/search?query=%22vacuum%20filter%22&tags=story>
  - <https://hn.algolia.com/api/v1/search?query=%22vacuum%20filters%22&tags=comment>
  - <https://hn.algolia.com/api/v1/items/28113100>
  - <https://github.com/search?q=VacuumFilter&type=code>
  - <https://github.com/tum-db/partitioned-filters>
  - <https://db.in.tum.de/~bandle/papers/vldb21-partitionedFilters.pdf>
  - <https://github.com/FastFilter/fastfilter_cpp>
  - <https://github.com/TomerEven/Prefix-Filter/blob/main/README.md>
  - <https://github.com/opengauss-mirror/openGauss-server/blob/master/contrib/gv_index/filter.h>
  - <https://github.com/jerryp1/mapcomp/blob/main/mpc4j-common-tool/src/main/java/edu/alibaba/mpc4j/common/tool/filter/VacuumFilter.java>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/wuwuz/vacuum-filter`) · [data/wave6/enrich/raw/github_com_wuwuz_vacuum_filter.json](../../../data/wave6/enrich/raw/github_com_wuwuz_vacuum_filter.json) (enrichment confidence 0.85)

</details>
