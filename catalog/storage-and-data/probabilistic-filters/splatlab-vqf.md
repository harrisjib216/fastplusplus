# Vector Quotient Filter (VQF)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Probabilistic filters](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `BSD-3-Clause` · 🟡 stale

> SIMD two-choice quotient-style filter with deletes; about 2x faster inserts than the Morton filter and steady throughput to 90% load.

| | |
|---|---|
| **Beats** | Morton filter |
| **Claimed result** | 2x faster inserts than the Morton filter (a cuckoo-filter variant, described in the paper as state-of-the-art for inserts); lookup and deletion performance similar to the cuckoo filter (described as fastest for queries/deletes); concurrent insert throughput scales 3x with 4 threads vs 1 thread; minimal performance decline at high load factors vs quotient, cuckoo, and Morton filters. |
| **Workload** | SIGMOD 2021 paper's insert/lookup/delete throughput measurements across load factors for a SIMD (AVX-512/AVX2) Robin-Hood-hashed quotient filter, including a thread-safe concurrent-insert variant. |
| **Metric** | throughput |
| **Adoption** | 13 stars |
| **Last commit** | 2024-05-19 |
| **Links** | [repository](https://github.com/splatlab/vqf) · [benchmark](https://raw.githubusercontent.com/swkim101/cspapers.org/main/index2/2021/sigmod/Vector%20Quotient%20Filters%3A%20Overcoming%20the%20Time%20Space%20Trade-Off%20in%20Filter%20Design) |

## Verdict

The authors' raw data in the repo (scripts/Performance.gnumeric: 2^28 slots, 8-bit tags, CPU and compiler not recorded, pre-2024 hashing code) backs the paper's claims: 40.1 ns vs 80.1 ns per insert against the Morton filter (2.0x), and 3.4x insert scaling from 1 to 4 threads; it also shows lookups at 34.3 ns vs 25-31 ns for the cuckoo filter, so VQF is slower on lookups rather than at parity. An independent run of the current code (Schmitz et al. 2025, AMD Ryzen 9 9950X, 2^30 slots) measured 22.1 M inserts/s and 25.4 M lookups/s, behind the Prefix filter (33.2 / 39.1) on both; the paper PDF itself returned 403, so its setup is unverified.

## Use it when

- Dynamic filters (inserts plus deletes) filled to high load: in the authors' 2^28-slot data, VQF inserts run at about 22 Mops up to 60% load and about 17 Mops at 90%, while the cuckoo filter falls from 33 Mops to about 2 Mops.
- Insert-heavy ingest on x86-64 servers with AVX-512 (the 8-bit fast path needs VBMI) and hardware-speed BMI2 (Intel Haswell or later, AMD Zen 3 or later), where a roughly 0.44% false-positive rate (8-bit tags) or roughly 0.002% (16-bit tags) is acceptable.
- Multi-threaded, insert-only build phases: the THREAD=1 build uses per-block spinlocks, and the authors' TXN data shows 62.3 ns/insert on 1 thread vs 18.4 ns on 4 threads.
- Keys you can already reduce to a well-mixed 64-bit hash, such as k-mers or IDs, with sizes from about 2^21 to 2^30 slots (the range the authors and later papers benchmarked).
- A reference or baseline implementation when evaluating quotient- or pocket-dictionary-style filters.

## Skip it when

- Lookup-dominated workloads: in the authors' own data the cuckoo filter answers lookups faster (25-31 ns vs 34 ns at 2^28). Schmitz et al. 2025 measured 25.4 M lookups/s for VQF vs 32-44 M/s for their cuckoo variants and 39 M/s for the Prefix filter.
- Insert-only or static sets: the Prefix filter builds 1.39-1.46x faster at similar space, and xor or binary fuse filters are smaller and faster for static sets.
- Non-x86 targets (ARM, Apple Silicon), MSVC or clang-only toolchains, and AMD Zen 1/Zen 2, where PDEP/PEXT are microcoded at about 18-cycle latency.
- You need a tunable FPR, counting, resizing, merging, serialization or enumeration. Only 8- or 16-bit tags exist, fixed at compile time; the CQF covers the rest.
- Production use needing maturity: no tests, releases or library target, and the May 2024 commit rewrote bucket and alternate-bucket hashing after the paper's measurements, with no published re-benchmark from the authors.

## How it is fast

Each 64-byte block holds 48 8-bit fingerprints plus a 128-bit metadata bitvector that unary-encodes run boundaries for 80 buckets. That is quotient-filter/Robin Hood layout confined to one block (the paper's 'mini-filter'). A lookup broadcasts the fingerprint, compares it against the whole block in one AVX-512 compare (two AVX2 compares on the fallback path), and masks the hits to the bucket's run using BMI2 pdep/tzcnt rank-select on the metadata; power-of-two-choices hashing means it checks two blocks. An insert picks the less-loaded of the two blocks, looking at the alternate only once the primary is about 75% full, then shifts tags with one vpermb permute from precomputed shuffle tables and updates the metadata with pdep. There are no cuckoo kick-out chains, so insert cost stays nearly flat as the filter fills.

## Compared with alternatives

Pick VQF over the cuckoo filter (efficient/cuckoofilter) or the Morton filter when you need deletes and insert throughput that holds at 80-90% load, and over the Prefix Filter when you need deletions or an AVX2 fallback (the Prefix Filter is insert-only and needs AVX-512). Choose the CQF instead for counting, resizing or merging, the cuckoo filter for lookup-bound workloads, and xor/binary fuse filters for static sets.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | vqf_filter.c needs only libc and x86 intrinsics headers. libssl/libcrypto (RAND_bytes), pthread and libitm are linked by the Makefile for the bundled benchmark drivers. |
| **Minimum toolchain** | GCC/g++ with -std=c++11: vqf_filter.c is C++ despite its .c extension (reinterpret_cast, references, &lt;algorithm&gt;). The Makefile hard-codes gcc/g++ with -fgnu-tm and -march=native. |
| **Platforms** | x86-64 only; BMI2 (pdep/pext/tzcnt) and at least AVX2 are required. The fast 8-bit path needs AVX-512 VBMI. The Makefile detects AVX-512 with Linux lscpu. |
| **Thread safety** | Not thread-safe by default. With -DENABLE_THREADS (make THREAD=1), only vqf_insert takes per-block spinlocks. vqf_is_present and vqf_remove are unsynchronized, so queries or deletes running alongside inserts are unsafe. PR #1, which added those locks, was closed unmerged. |
| **Drop-in for the baseline** | no |

## Gotchas

- The caller supplies the hash. Bucket = hash % range and tag = bits 32-39 (tag 0 is remapped to 1), so a poorly mixed 64-bit hash raises the FPR. Duplicate inserts consume extra slots, and removing a key that was never inserted can delete another key's fingerprint.
- The AVX-512 path is guarded by __AVX512BW__, and the Makefile checks for avx512bw. The default 8-bit code, however, calls _mm512_permutexvar_epi8, which GCC places under avx512vbmi, so -march=native builds on BW-only CPUs (Skylake-SP, Cascade Lake) will likely fail to compile (inferred from the code, not tested). TAG_BITS is a hard #define in vqf_filter.h, so switching to 16-bit tags means editing the header.
- Library hygiene: vqf_init prints 'Size: N' to stdout and checks malloc only with assert. There is no destroy function (call free()). A failed insert prints 'vqf filter is full.' to stderr and returns false. The 64-byte blocks start 48 bytes after the malloc'd header, so whether each block fits in one cache line depends on the allocator.
- The full-block check in vqf_insert runs only inside the branch taken when the alternate bucket is in a different block. If both candidate buckets map to the same full block, the insert proceeds without a capacity check and can overwrite the last stored tag. This comes from code reading and was not tested.

## Known shortcomings

- The full SIGMOD paper is paywalled (ACM 403), so CPU/compiler are unseen; last commit 2024-05.
- The authors' own raw sheet shows inserts 2x Morton (40 vs 80 ns) but lookups slower than cuckoo (34 vs 25-31 ns); an independent 2025 run (Ryzen 9950X) puts it behind the Prefix filter on both and behind every cuckoo variant on lookups. In thread mode only insert is locked (query/remove unlocked). The 8-bit AVX-512 path uses vpermb (VBMI) behind an avx512bw check; GCC + Linux + x86 BMI2 only; a 2024 hashing rewrite was never re-benchmarked; no destroy/resize/serialize.

## Caveats and trade-offs

The headline 2x speed claim is against the Morton filter, not directly against Bloom, cuckoo or xor filters. Against the cuckoo filter itself, the paper claims only parity ('similar lookup and deletion performance'), not a win. The paper's CPU model, compiler and flags could not be checked: the paper is gold open access (CC-BY) at dl.acm.org, but it returned HTTP 403 to curl and WebFetch, and the abstract was confirmed through a GitHub-hosted paper-index mirror. The repo Makefile builds with gcc/g++ -Ofast -march=native -msse4.2 and uses AVX-512 when lscpu reports avx512bw, with an AVX2 fallback. The repo holds no baseline-comparison harness.

Depends on libssl; requires AVX-512 (or AVX2 fallback) instructions; more complex build than a plain Bloom or cuckoo filter.

## Maintenance

Stale: the last commit (2024-05-19) rewrote the hashing, and the repo has 0 open issues and 13 stars. It is BSD-3-Clause and small (vqf_filter.c is about 630 lines), so it is easy to vendor, but it ships no library target, tests or releases.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** The benchmark_url mirror has the SIGMOD 2021 abstract verbatim: 2x faster inserts than the Morton filter, lookup and delete performance similar to the cuckoo filter, and 3x insert scaling with 4 threads. That is a peer-reviewed win over the named baseline. It is not A: the full paper (the source for CPU and compiler) returned 403 from both curl and WebFetch, and the repo's own src/bm.cc benchmarks only the VQF, with no Morton, cuckoo or quotient comparison code.
- **Verifier notes:** All claim numbers match the abstract. The last commit on the default branch (master) is 2024-05-19; the record's 2024-07-16 is the repo's pushed_at, and no branch has a later commit. The status stays 'stale'. BSD-3-Clause, 13 stars, not archived and not a fork, all confirmed through gh.
- **Fields the verifier corrected:** `last_commit`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/splatlab/vqf>
  - <https://raw.githubusercontent.com/swkim101/cspapers.org/main/index2/2021/sigmod/Vector%20Quotient%20Filters%3A%20Overcoming%20the%20Time%20Space%20Trade-Off%20in%20Filter%20Design>
  - <https://dl.acm.org/doi/pdf/10.1145/3448016.3452841>
  - <https://api.crossref.org/works?query.title=Vector+Quotient+Filters+Overcoming+the+Time+Space+Trade-Off&rows=3>
  - <https://api.semanticscholar.org/graph/v1/paper/DOI:10.1145/3448016.3452841?fields=title,openAccessPdf,externalIds>
  - <https://prashantpandey.github.io/publications/>
- **Sources the enricher read:**
  - <https://github.com/splatlab/vqf>
  - <https://raw.githubusercontent.com/splatlab/vqf/master/README.md>
  - <https://raw.githubusercontent.com/splatlab/vqf/master/Makefile>
  - <https://raw.githubusercontent.com/splatlab/vqf/master/include/vqf_filter.h>
  - <https://raw.githubusercontent.com/splatlab/vqf/master/include/vqf_wrapper.h>
  - <https://raw.githubusercontent.com/splatlab/vqf/master/src/vqf_filter.c>
  - <https://raw.githubusercontent.com/splatlab/vqf/master/src/main_tx.cc>
  - <https://raw.githubusercontent.com/splatlab/vqf/master/src/bm.cc>
  - <https://raw.githubusercontent.com/splatlab/vqf/master/scripts/Performance.gnumeric>
  - <https://github.com/splatlab/vqf/commit/8606e24e312d93d2a5bbc729d606518b4893a1f9.diff>
  - <https://github.com/splatlab/vqf/commit/62accaf20c0f6014f98fc8d9b995e244b6318ce3.diff>
  - <https://github.com/splatlab/vqf/pull/1>
  - <https://raw.githubusercontent.com/swkim101/cspapers.org/main/index2/2021/sigmod/Vector%20Quotient%20Filters%3A%20Overcoming%20the%20Time%20Space%20Trade-Off%20in%20Filter%20Design>
  - <https://prashantpandey.github.io/publications/>
  - <https://api.openalex.org/works/doi:10.1145/3448016.3452841>
  - <https://api.semanticscholar.org/graph/v1/paper/DOI:10.1145/3448016.3452841>
  - <https://dblp.org/search/publ/api?q=Vector%20Quotient%20Filters&format=json>
  - <https://export.arxiv.org/api/query?search_query=all:%22vector%20quotient%20filter%22>
  - <https://arxiv.org/pdf/2203.17139>
  - <https://arxiv.org/pdf/2505.05847>
  - <https://en.wikipedia.org/wiki/X86_Bit_manipulation_instruction_set>
  - <https://raw.githubusercontent.com/gcc-mirror/gcc/master/gcc/config/i386/avx512vbmiintrin.h>
  - <https://raw.githubusercontent.com/gcc-mirror/gcc/master/gcc/config/i386/avx512bwintrin.h>
  - <https://hn.algolia.com/api/v1/search?query=%22vector%20quotient%20filter%22>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/splatlab/vqf`) · [data/wave6/enrich/raw/github_com_splatlab_vqf.json](../../../data/wave6/enrich/raw/github_com_splatlab_vqf.json) (enrichment confidence 0.72)

</details>
