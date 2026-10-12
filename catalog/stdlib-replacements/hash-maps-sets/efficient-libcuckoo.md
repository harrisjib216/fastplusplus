# libcuckoo (cuckoohash_map, efficient/libcuckoo)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Hash maps and sets](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Header-only concurrent cuckoo hash map with per-bucket locks; beats std::unordered_map only under real multi-core contention.

| | |
|---|---|
| **Beats** | std::unordered_map |
| **Claimed result** | Peer-reviewed (EuroSys'14): on a 16-core machine the design executes 'almost 40 million inserts and more than 70 million lookup operations per second'; Figure 1 (4-core, 120M keys, 1:1 read/write) places it well above the C++11 std::unordered_map bar, though no exact std::unordered_map multiplier is printed as text (only 'up to 2.5x' vs Intel TBB concurrent_hash_map is quoted numerically) |
| **Workload** | Concurrent multi-threaded insert/lookup/mixed workloads on 120M 8-byte-key/8-byte-value pairs (Figure 1, 4-core, 1:1 read:write) and large-scale insert/lookup throughput on a 16-core machine |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-4770 (4-core Haswell) @ 3.4GHz, 32KB L1D / 256KB L2 / 8MB L3, 16GB DDR3 (main experiments); a separate 16-core machine is used for the headline \~40M insert/\~70M lookup number |
| **Adoption** | 1747 stars |
| **Last commit** | 2026-07-31 |
| **Links** | [repository](https://github.com/efficient/libcuckoo) · [benchmark](https://www.cs.princeton.edu/~mfreed/docs/cuckoo-eurosys14.pdf) |

## Verdict

On a 16-core machine the EuroSys'14 paper reports \~40M inserts/sec and \~70M lookups/sec; Figure 1 (4-core Intel i7-4770 Haswell, 120M 8-byte-key/8-byte-value pairs, 1:1 read:write) places libcuckoo well above C++11 std::unordered_map, but the only explicit numeric multiplier given in text is 'up to 2.5x' vs Intel TBB concurrent_hash_map — the std::unordered_map comparison is visual-only in the figure, and the paper treats std::unordered_map as a single-writer table (run under a global or TSX lock), so the measured win is multi-core scalability, not single-threaded op speed.

## Use it when

- Multi-threaded workloads with genuine concurrent inserts and lookups across several cores (paper measures gains at 4-16 cores, 1:1 read:write and mixed operation mixes).
- Fixed-shape, trivially hashable keys/values (paper benchmark uses 8-byte key/8-byte value, \~120M entries) where the 2-cache-line cuckoo probe pays off.
- Code that can adopt a non-STL API (out-parameter find, functor-based update/upsert) instead of std::unordered_map's interface.
- Workloads that need occasional safe bulk iteration via locked_table(), not concurrent iteration.
- C++11-capable toolchain on Linux/macOS; header-only, so easy to vendor into a build with no link step.

## Skip it when

- Single-threaded or low-contention use: the per-bucket spinlock/version machinery is pure overhead with no payoff.
- Memory-constrained settings: users report roughly 3x higher RSS than std::unordered_map for long-key/int-value maps at \~42M entries (issues #134, #136).
- Many reader threads hammering the same hot keys: open issue #159 reports spinlock contention degrading badly past \~16-64 threads, since even find() takes the bucket spinlock (no shared/exclusive mode).
- Code relying on std::unordered_map's free iterators or erase-while-iterating: normal access has no standalone iterators, only locked_table() does, and that locks the entire table.
- Scaling requirements beyond what's measured: the peer-reviewed numbers stop at 16 cores, and at least one independent report (issue #152) found scalability collapsing beyond \~16 threads in their own workload.

## How it is fast

Uses cuckoo hashing: each key maps to 2 candidate buckets of SLOT_PER_BUCKET=4 slots, so a lookup touches at most 2 cache lines and displacement chains stay short. Concurrency comes from fine-grained per-bucket spinlocks combined with a resize counter/versioning scheme (the EuroSys'14 optimistic-locking design), letting many writers and readers operate on different buckets simultaneously instead of serializing on one table-wide lock the way std::unordered_map does under concurrent access.

## Compared with alternatives

All catalogued siblings (emhash, dense_hash_map, rigtorp/HashMap, Verstable, sparsepp, hopscotch/ordered/robin-map, ska::flat_hash_map/bytell_hash_map) are single-threaded tables tuned for single-core cache behavior and are not safe for concurrent access without an external lock. Pick libcuckoo over any of them only when multiple threads genuinely insert into and look up the same map concurrently.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (self-contained headers: cuckoohash_map.hh, bucket_container.hh, cuckoohash_config.hh, cuckoohash_util.hh; optional C wrapper in libcuckoo-c/) |
| **Minimum toolchain** | C++11; clang++ &gt;= 3.3 or g++ &gt;= 4.8 per README (latest versions recommended for atomics support); CMake &gt;= 3.1.0 needed only to build tests/examples |
| **Platforms** | Tested on macOS &gt;= 10.8 and Ubuntu &gt;= 12.04 (README); no stated architecture restriction, plain std::atomic used, no SIMD/intrinsics observed in the header; Windows build status is an open/unclear question (issue #62) |
| **Thread safety** | Multiple concurrent readers and writers on the same table via per-bucket spinlocks plus a resize counter/versioning scheme (EuroSys'14 design); find() still acquires a bucket lock, so heavy same-key read contention can spin (issue #159). |
| **Drop-in for the baseline** | partial — same template parameter shape (Key, T, Hash, KeyEqual, Allocator) as std::unordered_map, but find()/insert()/update() use out-parameter or functor style instead of iterators, there is no operator[], and iterators exist only inside locked_table(). |

## Gotchas

- find(key, val) (bool-returning, out-parameter) and find(key) (returns mapped_type or throws std::out_of_range) are different overloads; there is no iterator/end() sentinel on the normal concurrent path.
- Automatic expansion throws load_factor_too_low if load factor falls below minimum_load_factor() (default 0.05) — a weak hash function or adversarial key set can trigger this.
- Bulk/STL-style iteration requires locked_table(), which takes an exclusive lock over the whole table for as long as it's held, blocking every other thread.
- Reported \~3x memory overhead vs std::unordered_map for 8-byte-key/4-byte-value workloads at scale (issues #134, #136); size capacity planning accordingly.

## Caveats and trade-offs

The repo's universal-benchmark (tests/universal-benchmark) compiles only LIBCUCKOO, with no std::unordered_map baseline. The std comparison comes from the EuroSys'14 paper's Figures 1-2, where the multiplier is only visual. The only explicit numeric speedup ('up to 2.5x') is against other concurrent tables such as Intel TBB. The paper treats std::unordered_map as a single-writer table: Section 2.3 says such tables 'allow only one writer at a time', and Figure 2 runs it under a global lock or TSX lock elision. So the win shows multi-core scalability, not a faster single-threaded operation. The compiler, flags, and std library are not stated in the paper.

Adds per-bucket spinlock/version-counter overhead irrelevant for single-threaded use; find() returns via out-parameter rather than iterator; requires locked_table() for safe bulk iteration; mainly wins when there is real concurrent contention, not necessarily in single-threaded use

## Maintenance

Active (last commit 2026-07-31, 1747 stars); Apache-2.0, header-only, and small enough to vendor directly into a project (usability: copyable).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification B, tier now B.
- **Tier reason:** The paper is peer-reviewed (EuroSys'14, DOI 10.1145/2592798.2592820) and the libcuckoo README cites it. Figure 1 (4-core i7-4770, 120M keys, 64-bit key/value, 1:1 read/write) and Figure 2 include C++11 std::unordered_map. The abstract states the \~40M insert / \~70M lookup per second figures on 16 cores and the 'up to 2.5x' figure versus other concurrent tables. The repo's own universal-benchmark supports only LIBCUCKOO, so it is not A.
- **Verifier notes:** The quotes and hardware match the paper. GitHub reports the license spdx_id as NOASSERTION, but the LICENSE file is the Apache License 2.0 (Carnegie Mellon University and Intel, 2013). The only third-party code is the bundled PCG headers in tests/pcg, so license Apache-2.0 and usability copyable stand. Other metadata checks out: 1747 stars, last commit 2026-07-31.
- **Fields the verifier corrected:** `caveats`
- **Pages the verifier opened:**
  - <https://www.cs.princeton.edu/~mfreed/docs/cuckoo-eurosys14.pdf>
  - <https://github.com/efficient/libcuckoo>
  - <https://github.com/efficient/libcuckoo/blob/master/LICENSE>
  - <https://github.com/efficient/libcuckoo/blob/master/README.md>
  - <https://github.com/efficient/libcuckoo/tree/master/tests/universal-benchmark>
  - <https://github.com/efficient/libcuckoo/blob/master/tests/universal-benchmark/universal_table_wrapper.hh>
- **Sources the enricher read:**
  - <https://github.com/efficient/libcuckoo>
  - <https://github.com/efficient/libcuckoo/blob/master/README.md>
  - <https://github.com/efficient/libcuckoo/blob/master/libcuckoo/cuckoohash_map.hh>
  - <https://github.com/efficient/libcuckoo/blob/master/libcuckoo/cuckoohash_util.hh>
  - <https://github.com/efficient/libcuckoo/blob/master/libcuckoo/cuckoohash_config.hh>
  - <https://github.com/efficient/libcuckoo/blob/master/tests/universal-benchmark/README.md>
  - <https://github.com/efficient/libcuckoo/issues/159>
  - <https://github.com/efficient/libcuckoo/issues/134>
  - <https://github.com/efficient/libcuckoo/issues/152>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/efficient/libcuckoo`) · [data/wave1/enrich/raw/github_com_efficient_libcuckoo.json](../../../data/wave1/enrich/raw/github_com_efficient_libcuckoo.json) (enrichment confidence 0.65)

</details>
