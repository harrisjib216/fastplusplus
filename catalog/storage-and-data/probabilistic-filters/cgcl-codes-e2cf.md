# Entry-Extensible Cuckoo Filter (E2CF)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Probabilistic filters](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🔴 abandoned

> Growable cuckoo filter that extends buckets into adjacent memory; paper: up to 82% less query time than Dynamic Cuckoo Filter.

| | |
|---|---|
| **Beats** | State-of-the-art dynamic approximate-membership filters with filter-level extension (the paper's references suggest Dynamic Cuckoo Filter / Dynamic Bloom Filter; exact baselines are not named on the README or in the abstract) |
| **Claimed result** | Reduces query time by up to 82% and insertion time by up to 28% compared to existing designs (README; the NPC 2020 paper abstract says 82% and 28% vs 'state-of-the-art designs'). No raw numbers are published. |
| **Workload** | Membership query and insertion over items with configurable false-positive rate, using adjacent-bucket entry extension to avoid discrete memory accesses, compared to existing (unnamed-in-README) cuckoo filter designs. |
| **Metric** | latency |
| **Hardware** | Intel CPU @ 2.60GHz, 64GB RAM, 64-byte cache line, Red Hat Enterprise Linux Server 6.2 |
| **Compiler and flags** | /usr/bin/g++ -std=c++0x -Wall with no -O flag (default -O0), per makefile; compiler version not stated |
| **Adoption** | 3 stars |
| **Last commit** | 2020-08-29 |
| **Links** | [repository](https://github.com/CGCL-codes/E2CF) · [benchmark](https://github.com/CGCL-codes/E2CF#e2cf-the-entry-extensible-cuckoo-filter) |

## Verdict

The open-access HAL manuscript of the NPC 2020 paper (hal-03768761) names the baselines: DBF and the lab's own DCF, with m=2^22 buckets, b=4, α=0.9 and 16-bit fingerprints for E2CF and DCF, run on an Intel Xeon E5-2670 at 2.60GHz with 64 GB RAM over MAWI/WIDE traces and synthetic data, averaging five runs. It reports negative-query time up to 82% lower than DCF (85% vs DBF) with up to 32 sub-filters, instantaneous non-repeatable insert time up to 28% (45%) lower, cumulative insert time up to 22% (41%) lower, delete time up to 79% (84%) lower, and memory comparable to DCF. All results are plots with no tables, the compiler and flags are not stated, and the public repo (-O0 build, 12-bit fingerprints, no baseline) cannot reproduce them.

## Use it when

- Research or teaching: you want a compact reference for entry-level extension to set against DCF and the Dynamic Bloom Filter (DBF), and you will write your own benchmark harness. The lab's CGCL-codes/DCF repo carries both the DCF and DBF code that the paper compared against.
- A deletable filter must grow several-fold from an unknown starting size, and lookup latency, not space, is the bottleneck. The paper's gains grow with the number of sub-filters (measured up to 32). With a single filter, E2CF is a plain cuckoo filter.
- Lookup streams dominated by absent keys (the paper uses MAWI/WIDE network-traffic traces), where DCF must probe every sub-filter before it can answer 'no'. At s=32 the paper shows E2CF ahead of DCF and DBF at every negative-query mix from 0% to 100%.
- Single-threaded x86-64 Linux code that can vendor about 1,200 lines of C++, fix it, and replace the per-operation OpenSSL SHA-1 with a fast non-cryptographic hash.

## Skip it when

- Any production use as-is. Reading the code shows correctness bugs: CuckooFilter::queryImpl has no return statement on the 12-bit miss path (undefined behaviour, which is risky once you add -O2). insertItem returns true even when an insert or victim relocation failed. The destructor deletes PtoCF[128], one element past the 128-slot array.
- Large or unbounded growth. Load-triggered splits happen only while countCF&lt;16 and numCF+2^l&lt;=16, kick-failure splits stop past slot 37, and the level is a 4-bit field in fixed 128-slot arrays. Beyond those limits, items are dropped while the call still reports success. Shrinking is not implemented: the paper describes merging sparse PCFs, but compact() has no definition.
- When you need a specific false-positive rate. The fingerprint is 12 bits whatever FPR you pass, because every branch of the constructor's size switch sets 12 (the paper's experiments used 16). Each level also doubles the entries scanned, so by the paper's Eq. 7 the rate is about 2^(l+1)\*4/2^12: roughly 0.2% with one PCF and about 3% with 16. The repo's default config asks for 0.05%.
- Static or known-size sets. E2CF is only faster than other growable filters. A fixed cuckoo, Morton, Vacuum, Xor or BuRR filter sized for the peak is smaller or faster and better engineered.
- Multithreaded access, big-endian or strict-alignment targets, binary keys containing NUL bytes (keys are hashed up to strlen), or builds against OpenSSL 1.1.0 or newer.

## How it is fast

The core technique is entry-level extension. When a partial cuckoo filter (PCF) k at level l splits, its odd-indexed buckets move to a new PCF numbered k+2^l, and the freed entries merge into the neighbouring even bucket, so a logical bucket at level l is 2^l physically adjacent 4-slot buckets. A query hashes once, picks the PCF by index mod 2^l, and scans each of its two candidate runs sequentially with a 64-bit SWAR match (hasvalue12, from the Stanford bit-twiddling hacks). DCF instead makes two small random bucket reads per sub-filter. Asynchronous extension (each PCF splits on its own once its load passes a threshold or a kick chain fails) keeps memory close to DCF's. Fine-grained splitting moves buckets lazily during inserts, tracked by a per-bucket flag (a 4-bit level field in the code), so there is no stop-the-world rehash. By the paper's own cost model (Eq. 4-5), query memory traffic still grows linearly with the number of PCFs s (s/8 to s/2 cache lines, vs 2s for DCF), so the gain is a smaller constant, not O(1) lookups.

## Compared with alternatives

Pick it only when the object of study is growable filters. It is the query-optimised successor to the sibling Dynamic Cuckoo Filter (DCF, same lab), and you would read the two side by side. For anything that ships, size a static filter for the peak and rebuild on growth: the efficient/cuckoofilter reference, Morton Filter (1.3-2.5x faster lookups than it) or Vacuum Filter if you need deletes, and Xor or BuRR for immutable sets.

## Integration

| | |
|---|---|
| **Form** | source-drop (the makefile builds only the ./test driver; there is no library target, install step or package) |
| **Dependencies** | OpenSSL libcrypto (EVP SHA-1 in hashfunction.cpp, linked with -lssl -lcrypto), and it needs the pre-1.1.0 API: a stack-allocated EVP_MD_CTX and EVP_MD_CTX_cleanup |
| **Minimum toolchain** | C++11 (makefile: /usr/bin/g++ -std=c++0x -Wall, with no -O flag) plus OpenSSL 1.0.x headers. The authors built on RHEL 6.2; the compiler version is not stated. |
| **Platforms** | Little-endian only (the code carries 'Little-Endian' comments and packs 12-bit fingerprints with unaligned 16/32/64-bit type-punned loads and stores). Only tested on x86-64 Linux. It uses no SIMD, only 64-bit SWAR. |
| **Thread safety** | Not documented. Not thread-safe: level counters, split flags, the PCF pointer table and the heavy-load queue are unguarded mutable members, and kicks use global rand(). Queries read split state that inserts change, so even concurrent reads alongside a writer need an external lock. |
| **Drop-in for the baseline** | partial — the constructor(capacity, fpr) and queryItem/deleteItem(const char\*) match the lab's DynamicCuckooFilter class, but insertion goes through insertItemNR (insertItem(const char\*) is declared and not defined), compact() is missing, and the fixed 12-bit fingerprint changes the false-positive behaviour |

## Gotchas

- It does not build against current OpenSSL as written. hashfunction.cpp declares EVP_MD_CTX on the stack and calls EVP_MD_CTX_cleanup, and OpenSSL 1.1.0 (Aug 2016) made EVP_MD_CTX opaque and removed that call (use EVP_MD_CTX_new/free/reset). Every operation also computes a full SHA-1 and allocates a std::string before any filter work.
- Buckets are 7 bytes (four 12-bit fingerprints plus a 4-bit level) but are read and written as unaligned 8-byte words. The last bucket's load runs one byte past the allocation. The split helper addBNewCF does \*(uint64_t\*)p &= 0xf0000000000000, which zeroes byte 7: the next bucket's level nibble and the low 4 bits of its first fingerprint.
- test.cpp is not a benchmark. It records insert time only every 20,000,000 inserts and never increments its false-positive counter, most Metric fields are uninitialised, and the shipped config is 100 items. That is why result/result.txt holds garbage. The repo has no DCF or DBF code to compare against.
- Headers leak: cuckoofilter.h does 'using namespace std;' and #defines MaxNumKicks 40, and EECuckooFilter.h relies on both (unqualified queue&lt;int&gt;). Split paths print to stdout with cout inside insert, and each CuckooFilter destructor frees the Bucket array but leaks the fingerprint storage.

## Known shortcomings

- The baseline is unnamed dynamic filters (likely DCF/DBF), not a plain cuckoo filter; no baseline code in the repo and an -O0 build.
- The repo differs from the paper: fingerprints are hard-coded at 12 bits whatever FPR is requested (\~0.2% at 1 sub-filter, \~3% at 16). Won't build on OpenSSL &gt;=1.1.0. Bugs: queryImpl's 12-bit miss path has no return (UB), insertItem always returns true (silent drops), the destructor deletes PtoCF[128] out of bounds, 7-byte buckets are accessed as unaligned 8-byte words. Growth is capped at \~16 sub-filters and compact() is declared but never defined.
- The paper (HAL hal-03768761) compares against DBF and DCF with plot-only results (query -82% vs DCF at &lt;=32 sub-filters, insert -28%); test.cpp is not a real benchmark (-O0, no baseline); not thread-safe; little-endian only.

## Caveats and trade-offs

The README does not name the baseline. The paper abstract says the comparison is against existing dynamic (filter-level-extensible) structures, not the static cuckoo filter, and its references include DCF (ICNP 2017) and DBF (TKDE 2010). The repo contains no baseline implementation or comparison harness; the committed result/result.txt holds uninitialized garbage values. The makefile builds without optimization. The hardware line gives no CPU model (Intel 2.60GHz, 64 GB RAM, RHEL 6.2). Paper: Yu, Wu, Chen, Jin, 'The Entry-Extensible Cuckoo Filter', NPC 2020, LNCS 12639 (2021).

Uses adjacent, sequentially-addressed buckets plus asynchronous extension and fine-grained splitting to reduce cache misses on query; from the same research group as DCF and BCF, so likely compares against the standard Cuckoo Filter, but the README does not name the baseline explicitly.

## Maintenance

Abandoned: one code upload plus README edits on 2020-08-28/29, 3 stars, no issues or releases, one fork identical to upstream and the other no longer reachable. It is Apache-2.0 and about 1,200 lines of library code, so it can be vendored as a design reference, but it needs an OpenSSL 1.0.x toolchain or a hash patch plus the bug fixes above before it is usable.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README only states 'compared to existing designs, E2CF reduces the query and insertion time by up to 82% and 28%', with no results table and no named baseline. The repo's test.cpp benchmarks only E2CF, includes no baseline code, and is built at -O0 (makefile: -std=c++0x -Wall). The NPC 2020 paper abstract (LNCS, DOI 10.1007/978-3-030-79478-1_32) repeats 82%/28% vs unnamed 'state-of-the-art designs', but the paywalled evaluation could not be checked, so the tier stays C.
- **Verifier notes:** The 82%/28% claim appears verbatim on the README, but it is a bare percentage vs unnamed 'existing designs'. The paper abstract shows the baselines are dynamic filters, not the plain cuckoo filter, so I corrected baseline and set baseline_in_list=false. Metadata is correct (Apache-2.0, last commit 2020-08-29, 3 stars, abandoned).
- **Fields the verifier corrected:** `baseline`, `baseline_in_list`, `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/CGCL-codes/E2CF>
  - <https://github.com/CGCL-codes/E2CF#e2cf-the-entry-extensible-cuckoo-filter>
  - <https://raw.githubusercontent.com/CGCL-codes/E2CF/master/makefile>
  - <https://raw.githubusercontent.com/CGCL-codes/E2CF/master/result/result.txt>
  - <https://raw.githubusercontent.com/CGCL-codes/E2CF/master/src/test.cpp>
  - <https://api.crossref.org/works?query.bibliographic=Entry-Extensible%20Cuckoo%20Filter>
  - <https://link.springer.com/chapter/10.1007/978-3-030-79478-1_32>
- **Sources the enricher read:**
  - <https://github.com/CGCL-codes/E2CF>
  - <https://github.com/CGCL-codes/E2CF#e2cf-the-entry-extensible-cuckoo-filter>
  - <https://github.com/CGCL-codes/E2CF/blob/master/README.md>
  - <https://github.com/CGCL-codes/E2CF/blob/master/makefile>
  - <https://github.com/CGCL-codes/E2CF/blob/master/src/EECuckooFilter.h>
  - <https://github.com/CGCL-codes/E2CF/blob/master/src/EECuckooFilter.cpp>
  - <https://github.com/CGCL-codes/E2CF/blob/master/src/cuckoofilter.h>
  - <https://github.com/CGCL-codes/E2CF/blob/master/src/cuckoofilter.cpp>
  - <https://github.com/CGCL-codes/E2CF/blob/master/src/test.cpp>
  - <https://github.com/CGCL-codes/E2CF/blob/master/src/hashfunction.h>
  - <https://github.com/CGCL-codes/E2CF/blob/master/src/hashfunction.cpp>
  - <https://github.com/CGCL-codes/E2CF/blob/master/src/bithack.h>
  - <https://github.com/CGCL-codes/E2CF/blob/master/src/linklist.h>
  - <https://github.com/CGCL-codes/E2CF/blob/master/src/uint.h>
  - <https://github.com/CGCL-codes/E2CF/blob/master/configuration/config.txt>
  - <https://github.com/CGCL-codes/E2CF/blob/master/configuration/config_Q.txt>
  - <https://github.com/CGCL-codes/E2CF/blob/master/result/result.txt>
  - <https://github.com/CGCL-codes/E2CF/blob/master/input/input100.txt>
  - <https://github.com/CGCL-codes/E2CF/commits/master>
  - <https://github.com/CGCL-codes/E2CF/issues?q=is%3Aissue>
  - <https://github.com/CGCL-codes/E2CF/forks>
  - <https://github.com/Horae20/E2CF>
  - <https://github.com/search?q=EECuckooFilter&type=code>
  - <https://github.com/CGCL-codes/DCF>
  - <https://github.com/CGCL-codes/DCF/blob/master/src/dynamiccuckoofilter.h>
  - <https://link.springer.com/chapter/10.1007/978-3-030-79478-1_32>
  - <https://api.crossref.org/works/10.1007/978-3-030-79478-1_32>
  - <https://api.semanticscholar.org/graph/v1/paper/DOI:10.1007/978-3-030-79478-1_32>
  - <https://inria.hal.science/hal-03768761/document>
  - <https://docs.openssl.org/1.1.1/man3/EVP_DigestInit/>
  - <https://raw.githubusercontent.com/openssl/openssl/OpenSSL_1_1_1-stable/doc/man3/EVP_DigestInit.pod>
  - <https://raw.githubusercontent.com/openssl/openssl/OpenSSL_1_1_1-stable/CHANGES>
  - <https://hn.algolia.com/api/v1/search?query=%22Entry-Extensible%20Cuckoo%20Filter%22>
  - <https://hn.algolia.com/api/v1/search?query=E2CF%20cuckoo>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/cgcl-codes/e2cf`) · [data/wave6/enrich/raw/github_com_cgcl_codes_e2cf.json](../../../data/wave6/enrich/raw/github_com_cgcl_codes_e2cf.json) (enrichment confidence 0.8)

</details>
