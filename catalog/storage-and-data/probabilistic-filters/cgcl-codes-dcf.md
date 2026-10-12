# Dynamic Cuckoo Filter (DCF)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Probabilistic filters](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🔴 abandoned

> Growable, shrinkable cuckoo filter (linked cuckoo-filter blocks) with reliable deletes; beats a Dynamic Bloom Filter on space and speed.

| | |
|---|---|
| **Beats** | Dynamic Bloom Filter (DBF) |
| **Claimed result** | Space: 2.5 MB (DCF) vs 10.8754 MB (DBF), labelled 4X. Time for 1M items: insert 1.08 s vs 1.69 s (1.5X), query 1.05 s vs 1.92 s (1.8X), delete 1.36 s vs 3.35 s (2.4X). Numbers and ratio labels are verbatim from the README results table; the README text summarizes this as 30-80% faster insert/query/delete and a 75% memory reduction. |
| **Workload** | Insert/query/delete/compact 1,000,000 items at expected FPR 0.0005, comparing DCF (cuckoo-hashing based, linked homogeneous cuckoo-filter blocks) against a Dynamic Bloom Filter of matched actual FPR. |
| **Metric** | latency |
| **Hardware** | Intel Core i5-2430M @ 2.4GHz, Ubuntu 14.04.3 LTS |
| **Compiler and flags** | g++ -Wall with no -O flag (default -O0), for both DCF (makefile) and DBF (makefile_DBF); compiler version not stated |
| **Adoption** | 38 stars |
| **Last commit** | 2017-11-16 |
| **Links** | [repository](https://github.com/CGCL-codes/DCF) · [benchmark](https://github.com/CGCL-codes/DCF#results) |

## Verdict

One README run inserts, queries and deletes 1M decimal-integer strings at a 0.0005 FPR target. The baseline is the repo's own Dynamic Bloom Filter, built from 4-bit counting Bloom filters. Both are compiled with g++ -Wall at default -O0, timed with clock() on an i5-2430M under Ubuntu 14.04, with SHA-1 per operation on both sides. DCF takes 1.08/1.05/1.36 s for insert/query/delete versus 1.69/1.92/3.35 s for DBF. DCF computes 2.5 MB of fingerprint bits versus 10.88 MB of DBF counter bits; this is not measured heap, and about 4x of that gap comes from the counters, since plain 1-bit Bloom arrays would be roughly 2.7 MB. The ICNP 2017 paper reports similar gains at FPR 1.17e-2 with up to 64,512 items: about 50% faster insert, 80% faster query, 25% faster delete and 75% less memory.

## Use it when

- You need an approximate set that must both grow and shrink with a fluctuating or unknown item count, and also support deletes. An example is the in-memory chunk-fingerprint index for deduplication in the paper's file-backup prototype.
- You are replacing a Dynamic Bloom Filter or a chain of counting Bloom filters where deletes get skipped when several blocks match. Here each item owns one fingerprint, so deletes are exact for inserted items.
- FPR targets are moderate (about 1e-2 down to 5e-4 with the default \~6 blocks), so 16-bit or smaller fingerprints are enough, and the final item count stays close to the planned maximum.
- You want a short (\~850 lines), readable reference for the ICNP 2017 design to port into your own codebase with a fast non-cryptographic hash and proper memory management.

## Skip it when

- Capacity is known up front. A single fixed-size cuckoo, xor or binary fuse filter avoids the per-block probing, and query and delete time here grows linearly with the number of blocks (paper Fig. 13 and 15).
- The filter grows well past its planned size or serves many negative lookups. Every miss probes 2 buckets in every block, and FPR compounds per block: open issue #2 reports FPR approaching 100% after growing from 1,000 to 30,000 items at a 3% per-block target.
- FPR targets below about 5e-4 at the default settings. Fingerprints are capped at 16 bits: any computed size from 17 to 32 bits is silently set to 16, so the target is not met.
- Anything production-facing. SHA-1 is computed only over the first sizeof(const char\*) bytes of the key, destructors double-free, compact() leaks and can cause false negatives, and the repo has been unmaintained since 2017.
- Concurrent access. There is no synchronization, and kick-out victims are chosen with the global rand().

## How it is fast

Each block is a standard Fan et al. cuckoo filter: 4-slot buckets, partial-key cuckoo hashing (alternate bucket = index XOR hash(fingerprint)) and up to 500 kicks. When a block reaches 93.75% load, a new block with the same table length and hash is linked on. A victim left over from a failed insert goes to the same bucket index in the next block. A lookup checks the 4 packed fingerprints of a bucket at once with SWAR 'hasvalue' bit tricks (Stanford bithacks haszero4/8/12/16), so each block costs 2 bucket probes, where each DBF block costs k 4-bit counter reads. A DCF delete stops at the first matching block; the in-repo DBF scans every block twice. Compaction is greedy: it moves fingerprints from the sparsest block into the same bucket indexes of denser blocks.

## Compared with alternatives

Pick DCF over efficient/cuckoofilter, Vacuum Filter or Morton Filter only when the set must grow and later shrink with reliable deletes; those are fixed-capacity cuckoo-style filters. Its same-lab successor E2CF instead grows at the bucket-entry level to avoid probing many blocks, and reports up to 82% lower query time than existing designs. Prefer E2CF when lookups dominate.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | OpenSSL libcrypto (SHA-1 through the EVP API; the makefile links -lssl -lcrypto) |
| **Minimum toolchain** | C++98-style g++ code (no C++11 features). It needs the OpenSSL 1.0.x EVP API: a stack-allocated EVP_MD_CTX and EVP_MD_CTX_cleanup. OpenSSL 1.1.0 made these structures opaque (EVP_MD_CTX_new/free), so OpenSSL 1.1 and 3.x need a small patch. |
| **Platforms** | Tested only on Linux x86-64 (Ubuntu 14.04). The code assumes little-endian layout and uses unaligned, type-punned integer loads on the bucket bytes. |
| **Thread safety** | Not documented. There is no locking, and the shared Victim member and global rand() mean it is single-threaded only. |
| **Drop-in for the baseline** | partial: it has the same constructor signature and insertItem/queryItem/deleteItem(const char\*) calls as the repo's own DynamicBloomFilter class (the two test harnesses differ only in the class name), plus compact(). It is not a drop-in for any external Bloom filter library. |

## Gotchas

- Hashing bug: HashFunc::sha1 hashes sizeof(key) bytes, where key is a const char\*, so 8 bytes on 64-bit. Keys that share an 8-byte prefix always collide. Keys shorter than 7 characters hash bytes past their NUL terminator, so the same key stored in different buffers can hash differently, which means false negatives. The bundled benchmark hides this by reusing the same string buffers for insert, query and delete.
- Memory handling is broken. \~CuckooFilter deletes both next and front, so linked blocks free each other twice. \~DynamicCuckooFilter deletes curCF and then the list head, which is the same pointer. LinkList::remove() unlinks a block during compact() but never frees it and never fixes tail_pt, the successor's front pointer or curCF. After the README's delete-everything-then-compact flow the block count is 0, so every later insert lands in an unlinked block and is never found. Open issue #3 reports a segfault (no details).
- The reported space_cost (size_in_mb) counts fingerprint bits only. Each 8-byte bucket is a separate new char[] allocation plus an 8-byte pointer, so real heap use is at least 2x the reported figure before allocator overhead. The constructor also leaks 3 preallocated blocks. For 4/8/12-bit fingerprints, queryImpl reads 8 bytes from buckets allocated as 2/4/6 bytes, which is a heap over-read.
- The build instructions are wrong. The README says 'cd src/; make test', but the makefile is at the repo root and uses src/ paths, and the test binary reads ./configuration/config.txt and writes ./result/result.txt relative to the working directory. makefile_DBF points at src/\*.cpp although the DBF sources live in src_DBF/, so the baseline does not build as shipped.

## Known shortcomings

- Both makefiles build with g++ -Wall and no -O flag (-O0); the baseline is a Dynamic Bloom Filter, not a standard Bloom or cuckoo filter.
- Hash bug: SHA-1 covers only sizeof(const char\*) = 8 bytes, so keys sharing an 8-byte prefix collide and keys under 7 chars hash bytes past the NUL (false negatives). Destructors double-free; compact() frees nothing and leaves stale pointers, so after the README's delete-all + compact later inserts are never found. space_cost counts fingerprint bits only (real heap &gt;=2x), and the DBF baseline is a 4-bit counting Bloom filter, so most of the \~4x space gap is counters.
- Fingerprints capped at 16 bits (FPR below \~5e-4 silently unreachable); FPR compounds per block (#2) and queries are O(blocks). Uses the OpenSSL 1.0 EVP API (needs patching for 1.1/3.x); wrong build docs, broken makefile_DBF paths, -O0 with clock() timing; abandoned 2017.

## Caveats and trade-offs

The baseline is a Dynamic Bloom Filter (a Bloom variant, implemented in the repo under src_DBF/), not the plain incumbent Bloom filter, so baseline_in_list=false. Both DCF and DBF are built by the repo makefiles without optimization (g++ -Wall, default -O0), so absolute times and ratios may not hold at -O2/-O3. Hardware is a 2011-era laptop CPU (i5-2430M). The repo has been unmaintained since 2017. Paper: Chen, Liao, Jin, Wu, 'The Dynamic Cuckoo Filter', ICNP 2017, DOI 10.1109/icnp.2017.8117563.

Adds reliable item deletion plus dynamic capacity extension/reduction on top of standard Cuckoo Filters; requires OpenSSL for hashing and a compact/rehash operation to reclaim space from removed building blocks.

## Maintenance

Abandoned since November 2017, with issues on FPR degradation and a segfault left unanswered. It is Apache-2.0 and about 850 lines, so treat it as a reference implementation of the ICNP 2017 design to port and fix (OpenSSL 1.0-era hashing, destructors, compaction) rather than a library to link.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README results table compares DCF against a Dynamic Bloom Filter implementation that ships in the repo (src_DBF/, makefile_DBF) on an i5-2430M. However, both makefiles compile with 'g++ -Wall' and no optimization flag (default -O0), so the -O0 baseline cap applies and the tier stays C, even though the design is also published at ICNP 2017.
- **Verifier notes:** The numbers match the README table; the only fix is DBF space_cost, which is 10.8754 MB (the record rounded it to 10.9). Both builds are unoptimized, which caps the tier at C despite the peer-reviewed ICNP 2017 paper. All metadata is correct (Apache-2.0, last commit 2017-11-16, 38 stars, abandoned).
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/CGCL-codes/DCF>
  - <https://github.com/CGCL-codes/DCF#results>
  - <https://raw.githubusercontent.com/CGCL-codes/DCF/master/makefile>
  - <https://raw.githubusercontent.com/CGCL-codes/DCF/master/makefile_DBF>
  - <https://raw.githubusercontent.com/CGCL-codes/DCF/master/result/result.txt>
  - <https://api.crossref.org/works?query.bibliographic=The%20Dynamic%20Cuckoo%20Filter%20Chen%20Liao%20Jin%20Wu>
- **Sources the enricher read:**
  - <https://github.com/CGCL-codes/DCF>
  - <https://github.com/CGCL-codes/DCF#results>
  - <https://raw.githubusercontent.com/CGCL-codes/DCF/master/makefile>
  - <https://raw.githubusercontent.com/CGCL-codes/DCF/master/makefile_DBF>
  - <https://raw.githubusercontent.com/CGCL-codes/DCF/master/result/result.txt>
  - <https://raw.githubusercontent.com/CGCL-codes/DCF/master/configuration/config.txt>
  - <https://raw.githubusercontent.com/CGCL-codes/DCF/master/NOTICE>
  - <https://raw.githubusercontent.com/CGCL-codes/DCF/master/.gitignore>
  - <https://raw.githubusercontent.com/CGCL-codes/DCF/master/input/input.txt>
  - <https://raw.githubusercontent.com/CGCL-codes/DCF/master/src/bithack.h>
  - <https://raw.githubusercontent.com/CGCL-codes/DCF/master/src/cuckoofilter.h>
  - <https://raw.githubusercontent.com/CGCL-codes/DCF/master/src/cuckoofilter.cpp>
  - <https://raw.githubusercontent.com/CGCL-codes/DCF/master/src/dynamiccuckoofilter.h>
  - <https://raw.githubusercontent.com/CGCL-codes/DCF/master/src/dynamiccuckoofilter.cpp>
  - <https://raw.githubusercontent.com/CGCL-codes/DCF/master/src/hashfunction.h>
  - <https://raw.githubusercontent.com/CGCL-codes/DCF/master/src/hashfunction.cpp>
  - <https://raw.githubusercontent.com/CGCL-codes/DCF/master/src/linklist.h>
  - <https://raw.githubusercontent.com/CGCL-codes/DCF/master/src/uint.h>
  - <https://raw.githubusercontent.com/CGCL-codes/DCF/master/src/test.cpp>
  - <https://raw.githubusercontent.com/CGCL-codes/DCF/master/src_DBF/countingbloomfilter.h>
  - <https://raw.githubusercontent.com/CGCL-codes/DCF/master/src_DBF/countingbloomfilter.cpp>
  - <https://raw.githubusercontent.com/CGCL-codes/DCF/master/src_DBF/dynamicbloomfilter.h>
  - <https://raw.githubusercontent.com/CGCL-codes/DCF/master/src_DBF/dynamicbloomfilter.cpp>
  - <https://raw.githubusercontent.com/CGCL-codes/DCF/master/src_DBF/hashfunctions.h>
  - <https://raw.githubusercontent.com/CGCL-codes/DCF/master/src_DBF/hashfunctions.cpp>
  - <https://raw.githubusercontent.com/CGCL-codes/DCF/master/src_DBF/test.cpp>
  - <https://github.com/CGCL-codes/DCF/commits/master>
  - <https://github.com/CGCL-codes/DCF/issues/2>
  - <https://github.com/CGCL-codes/DCF/issues/3>
  - <https://github.com/CGCL-codes/DCF/pull/1>
  - <https://github.com/CGCL-codes/DCF/forks>
  - <https://github.com/GerHobbelt/DCF/commits>
  - <https://github.com/skyler1grey/DCF/commits>
  - <https://api.crossref.org/works/10.1109/icnp.2017.8117563>
  - <https://api.semanticscholar.org/graph/v1/paper/DOI:10.1109/ICNP.2017.8117563>
  - <https://cis.temple.edu/~wu/research/publications/Publication_files/>
  - <https://cis.temple.edu/~wu/research/publications/Publication.html>
  - <https://cis.temple.edu/~wu/research/publications/Publication_files/Chen_ICNP_2017.pdf>
  - <https://wiki.openssl.org/index.php/OpenSSL_1.1.0_Changes>
  - <https://github.com/CGCL-codes/E2CF>
  - <https://hn.algolia.com/api/v1/search?query=%22dynamic%20cuckoo%20filter%22>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/cgcl-codes/dcf`) · [data/wave6/enrich/raw/github_com_cgcl_codes_dcf.json](../../../data/wave6/enrich/raw/github_com_cgcl_codes_dcf.json) (enrichment confidence 0.82)

</details>
