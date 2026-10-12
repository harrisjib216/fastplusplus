# W-TinyLFU (C++ header-only, based on the TinyLFU paper)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Caches](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `reference (no LICENSE file in vimpunk/w-tinylfu)` · 🔴 abandoned

> Small C++ header-only W-TinyLFU cache: frequency-sketch admission in front of segmented LRU, for higher hit ratios than plain LRU.

| | |
|---|---|
| **Beats** | LRU |
| **Claimed result** | Per the paper (not this port), W-TinyLFU with a 1% window matched or beat every other evaluated policy on the majority of traces, including LRU, ARC and LIRS. It outperformed all other policies on DS1, SPC1-like and the search-engine traces. On OLTP, F1 and F2, the 1% window was not the top performer; a 20-40% window was needed. On P8/P12 it led at all but the largest cache sizes. The \~89% figure is TinyLFU's memory saving over a strawman sliding-window sketch (Zipf 0.9, 1K cache, 9K histogram), not a result against LRU. |
| **Workload** | Synthetic Zipf(0.7/0.94) and SPC1-like traces plus real YouTube/Wikipedia/DS1/S3/OLTP traces evaluated for hit ratio, comparing TinyLFU-admission-augmented LRU/Random/LFU against plain LRU, ARC, SLRU, LRU-K and others (algorithm's own paper; this specific repo is an independent C++11 header-only reimplementation) |
| **Metric** | other |
| **Adoption** | 64 stars |
| **Last commit** | 2018-10-24 |
| **Links** | [repository](https://github.com/vimpunk/w-tinylfu) · [benchmark](https://arxiv.org/pdf/1512.00727) |

## Verdict

This C++ port has no benchmark of its own. The only evidence is hit-ratio plots in the TinyLFU paper (arXiv 1512.00727v2), which the authors produced with a Java prototype and with Caffeine 2.0 on Zipf 0.7/0.94, SPC1-like and real traces. There, W-TinyLFU with a 1% window tied or beat LRU, ARC and LIRS on most traces, but OLTP, F1 and F2 needed a 20-40% window, which this port cannot configure. Hit ratio does not depend on hardware, and no compiler, hardware or throughput figures exist for this code.

## Use it when

- Single-threaded, or externally locked, in-process C++ object caches where plain LRU loses hit ratio to scans or to skewed (Zipf-like) traffic full of one-time keys.
- Keys that are integers or padding-free POD ids. The sketch hashes the key's raw bytes, so only these keys hash consistently.
- Expensive or large values (the repo's test caches 4 KB objects), where each extra hit is worth more than the policy's per-operation overhead (map lookup, list splice, sketch updates), and where returning shared_ptr keeps an evicted value alive while a caller still uses it.
- As a readable reference (under 900 lines across four headers, including license text) to vendor and harden when you need W-TinyLFU in C++ and cannot use the JVM.
- Frequency-skewed workloads like the paper's search-engine, DS1 and SPC1-like traces, where the fixed 1% window tied or beat LRU, ARC and LIRS.

## Skip it when

- Multithreaded access without your own lock. Even get() mutates the LRU order and the sketch, and a single global mutex serializes every operation.
- Recency-heavy or 'sparse burst' workloads such as the paper's OLTP, F1 and F2 traces, which needed a 20-40% window. This port hard-codes a 1% window and an 80/20 split, with no hill-climbing adaptation of the kind Caffeine now does.
- Untrusted or adversarial keys. There is no HashDoS protection: Caffeine's random admission of 'warm' candidates is missing, and issue #1 has been open since 2017.
- std::string keys, or structs with pointers or padding. Equal keys hash differently, so admission decisions silently degrade.
- Windows/MSVC builds, caches bounded by bytes or needing expiry, or latency-critical hot paths. Every insert does three heap allocations (std::map node, std::list node, make_shared block) and stores two copies of the key, and no throughput benchmark exists.

## How it is fast

The gain is in hit ratio, not per-operation speed. A count-min sketch of 4-bit counters (four counters per key, packed sixteen to a 64-bit word, following Caffeine) estimates each key's recent frequency. Once about 10x capacity increments have been recorded, every counter is halved (the paper's 'reset' aging). New keys go into an LRU window sized at 1% of capacity. The window's LRU victim is admitted into a 99% segmented LRU (80% protected, 20% probationary) only if its estimated frequency is strictly higher than that of the probationary segment's LRU victim; otherwise the newcomer is dropped. Each get() pays a std::map lookup, a std::list splice, four sketch increments and a shared_ptr copy, so it costs more per call than a hand-rolled LRU. A Bloom-filter 'doorkeeper' header ships in the repo but is not wired in.

## Compared with alternatives

On the JVM, use Caffeine: it is the canonical W-TinyLFU, with an adaptive window, HashDoS jitter and concurrency. For offline trace studies, libCacheSim (SIEVE's repo) already ships WTinyLFU.c next to SIEVE, LRU and ARC. Pick this one only when you want a tiny dependency-free C++ W-TinyLFU object to embed in a single-threaded component with integer keys and are prepared to fix its edge cases. If you mainly need a simpler, better-than-LRU C++ policy, SIEVE or LHD have stronger evidence.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (standard library only) |
| **Minimum toolchain** | README says C++11, but detail.hpp's constexpr functions contain loops and multiple statements, which needs C++14 relaxed constexpr in practice. No compiler versions are documented and there is no CI. |
| **Platforms** | Portable C++ with no SIMD or intrinsics. It assumes a 64-bit long (LP64, e.g. Linux/macOS on x86-64 or aarch64): the sketch shifts 1L/0xfL by up to 60 bits, which is undefined where long is 32-bit (Windows). |
| **Thread safety** | Not thread-safe. The header says 'NOTE: it is NOT thread-safe!', and get() mutates state, so every call needs an external lock. Returned shared_ptr&lt;V&gt; values stay valid after eviction. The circonus-labs fork (2023) adds a single global std::mutex. |
| **Drop-in for the baseline** | partial — it has the same get/insert/erase shape as a typical std::list + map LRU cache, but get returns std::shared_ptr&lt;V&gt; (nullptr on a miss), K needs operator&lt; (the index is std::map, not a hash map) plus a byte-stable representation, and there are no custom hash, comparator or allocator parameters |

## Gotchas

- The sketch hashes the key's raw object bytes (Jenkins one-at-a-time over reinterpret_cast&lt;const char\*&gt;(&key)), not std::hash. For std::string, or any key holding pointers or padding, the caller's key and the cache's stored copy can hash differently, so frequency comparisons turn into noise and nothing reports it.
- Capacity edge cases (found by reading the code, not by running it): with capacity 1 the main SLRU gets 0 slots, and the second insert reads the victim of an empty probationary list, which is undefined behavior. Shrinking with change_capacity() can hit the same path when the protected segment holds more entries than the new capacity. change_capacity() also clears the sketch and, because is_full uses &gt;=, evicts one entry more than needed.
- insert() on an existing key only swaps the value. It does not refresh recency or bump the sketch; only get() records accesses. If the window is full it runs an eviction first anyway, so an update can shrink a full cache by one entry.
- Portability: uint32_t, std::enable_if, std::max, std::min and std::hash are used without including &lt;cstdint&gt;, &lt;type_traits&gt;, &lt;algorithm&gt; or &lt;functional&gt;. The code relies on transitive includes of the kind GCC 13 removed from libstdc++. The hit and miss counters are plain int and overflow after 2^31.

## Known shortcomings

- 'Best on every trace' is overstated: the default 1% window loses on OLTP/F1/F2 traces (needs 20-40%); the \~89% figure is memory saved vs a strawman sketch, not a gain over LRU. No licence (reference only), last commit 2018-10, not thread-safe (verifier downgrade).
- No benchmark of its own; hit-ratio figures come from the paper (Java prototype and Caffeine). The window is fixed at 1% with no adaptation, while the paper's OLTP/F1/F2 traces needed 20-40%. Not thread-safe, no HashDoS guard (issue #1 open since 2017), abandoned 2018.
- The frequency sketch hashes raw key bytes, so std::string or padded keys hash wrongly and admission quietly degrades. From code reading (not run): capacity 1 and change_capacity shrinking hit UB on an empty probationary list; 1L/0xfL shifts are UB where long is 32-bit (Windows). README says C++11 but a constexpr loop needs C++14; missing &lt;cstdint&gt; etc. may break GCC 13+. No LICENSE file, but every header carries an MIT-style notice.

## Caveats and trade-offs

The quantitative hit-ratio results come from the original paper's Java simulator and Caffeine evaluation. They were not re-measured on this C++11 header-only port, so the entry is tier C even though the algorithm's paper is well cited. The README says thread-safety and hash-collision protection are absent. The repo has no LICENSE file. Caffeine itself (the canonical TinyLFU implementation) is already catalogued and excluded.

This specific repo explicitly omits thread-safety and hash-collision protection ('barebones' header-only port); the underlying TinyLFU paper's hit-ratio numbers come from a Java prototype and from Caffeine, not from this C++ port directly

## Maintenance

Abandoned: the last commit was 2018-10-24, there are no releases, and six issues opened in 2017-2018 are still open, including HashDoS protection and 'Thorough testing required'. GitHub detects no license and there is no LICENSE file, but every header carries an MIT-style permission notice (Copyright 2017 mandreyel), so it is best treated as a small reference to vendor and fix rather than a dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification C, tier now C.
- **Tier reason:** The TinyLFU paper (arXiv 1512.00727v2) plots hit ratio against LRU, ARC, LIRS and others, but those results come from the authors' Java simulator and Caffeine, not from this C++ port. The repo has no benchmark of its own, so it stays at C for this entry.
- **Verifier notes:** The claim 'best on every tested trace' is overstated: the paper's own OLTP/F1/F2 results show the default 1% window losing, and the abstract's 'equal or better' wording is qualified in Section 5. The metadata checks out: no license (gh license null, no LICENSE file in the root), 64 stars, not a fork or archived, last commit 2018-10-24 (abandoned). This is a small independent reimplementation.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/pdf/1512.00727>
  - <https://github.com/vimpunk/w-tinylfu>
- **Sources the enricher read:**
  - <https://github.com/vimpunk/w-tinylfu>
  - <https://github.com/vimpunk/w-tinylfu/blob/master/README.md>
  - <https://github.com/vimpunk/w-tinylfu/blob/master/wtinylfu.hpp>
  - <https://github.com/vimpunk/w-tinylfu/blob/master/frequency_sketch.hpp>
  - <https://github.com/vimpunk/w-tinylfu/blob/master/detail.hpp>
  - <https://github.com/vimpunk/w-tinylfu/blob/master/bloom_filter.hpp>
  - <https://github.com/vimpunk/w-tinylfu/blob/master/test/test.cpp>
  - <https://github.com/vimpunk/w-tinylfu/issues>
  - <https://github.com/vimpunk/w-tinylfu/issues/1>
  - <https://github.com/vimpunk/w-tinylfu/commits/master>
  - <https://github.com/vimpunk/w-tinylfu/network/members>
  - <https://github.com/vimpunk/w-tinylfu/compare/master...circonus-labs:w-tinylfu:master>
  - <https://github.com/vimpunk/w-tinylfu/compare/master...kevins981:w-tinylfu:master>
  - <https://arxiv.org/pdf/1512.00727>
  - <https://github.com/ben-manes/caffeine/wiki/Efficiency>
  - <https://gcc.gnu.org/gcc-13/porting_to.html>
  - <https://github.com/1a1a11a/libCacheSim>
  - <https://github.com/zetta-cai/DACO-public/blob/main/src/cache/wtinylfu/wtinylfu_cache_policy.hpp>
  - <https://github.com/search?q=wtinylfu_cache&type=code>
  - <https://hn.algolia.com/api/v1/search?query=vimpunk%20tinylfu>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/vimpunk/w-tinylfu`) · [data/wave6/enrich/raw/github_com_vimpunk_w_tinylfu.json](../../../data/wave6/enrich/raw/github_com_vimpunk_w_tinylfu.json) (enrichment confidence 0.8)

</details>
