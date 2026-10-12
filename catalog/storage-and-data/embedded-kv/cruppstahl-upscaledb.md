# upscaledb

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Embedded key-value stores](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🔴 abandoned

> Embedded typed-key B+tree store (formerly hamsterdb) whose in-engine aggregates beat cursor scans in LevelDB and Berkeley DB.

| | |
|---|---|
| **Beats** | LevelDB v1.11.0 and Berkeley DB v5.1.0 |
| **Claimed result** | about 90 times faster than LevelDB and about 140 times faster than Berkeley DB (homepage text, read from a WebSearch snippet of upscaledb.com). |
| **Workload** | Full-table scan over 50 million uint32 records that retrieves the maximum value, upscaledb v2.0.0 (built-in analytical function) vs LevelDB v1.11.0 vs Berkeley DB v5.1.0 on 64-bit Linux, commodity hardware. |
| **Metric** | throughput |
| **Compiler and flags** | Benchmark driver Makefile in the author's gist: g++ -std=c++11 -g -O0 (driver only; flags for the upscaledb, LevelDB and Berkeley DB libraries are not stated); 4 MB cache per database, LevelDB compression disabled. |
| **Adoption** | 572 stars, 70 forks |
| **Last commit** | 2021-08-20 |
| **Links** | [repository](https://github.com/cruppstahl/upscaledb) · [benchmark](https://upscaledb.com/) |

## Verdict

The first-party homepage (seen only as a search snippet) says a full scan of 50 million uint32 key/record pairs to find the maximum record, with 4 MB of cache on 64-bit Linux, ran about 90x faster than LevelDB 1.11.0 and 140x faster than Berkeley DB 5.1.0. No absolute times, CPU or library build flags are given. The linked gist shows that upscaledb computed MAX inside the engine over PAX leaf arrays, while LevelDB (compression off) and Berkeley DB walked every record through an iterator or cursor in a driver compiled with g++ -std=c++11 -g -O0, one run each. The comparison therefore measures pushing an aggregate into the engine against client-side iteration, and the run is labelled with a version older than the API it uses.

## Use it when

- Embedded stores keyed by integers (uint32/uint64 ids, timestamps) with small fixed-size records, where you want MIN/MAX/SUM/COUNT/AVERAGE or a custom aggregate over all or a key range of the data without writing an iteration loop
- Read-mostly or append-ordered workloads on one node, where a B+tree with typed, compressed integer keys keeps the index small
- Applications that need transactions, journalling and duplicate keys in one embeddable library under Apache-2.0, and that can fork and maintain it
- Research or teaching on PAX layouts, SIMD in-node search and integer-key compression inside a real B+tree

## Skip it when

- New production systems that need a maintained dependency: the last commit is 2021-08-20, builds fail with current Boost.Asio and protobuf (issues #134 and #135, no maintainer reply), and issue #134 links a Homebrew-core commit titled 'upscaledb: deprecate'
- Write-heavy random-insert workloads at scale: a 2014 comparison by the same author (search snippets only) found it slower than LevelDB on random writes past about 10 million keys
- Multi-threaded write throughput: every public API call takes the environment's mutex, so operations on one environment are serialised
- Workloads where you need cursor correctness under transactions to be proven: open issues report cursors skipping entries (#106), moving the wrong way (#107), finding erased items with UPS_FIND_GEQ_MATCH (#105) and endless recursion in cursor find (#50), and three unit tests failing (#111)
- Choosing it on the 90x/140x claim alone: that measures an in-engine aggregate against client-side iteration, not general key-value speed

## How it is fast

For fixed-size typed keys and records it uses a PAX-style leaf layout (btree_impl_pax.h): a page holds a dense key array and a separate record array, which gives tight, cache-friendly loops. Lookups inside a node run a binary search that switches to an SSE2 linear search once the remaining range is small (simd.h). uint32 keys can be compressed with integer codecs such as VarByte/MaskedVByte, SIMDComp, FOR and SIMD-FOR (the Lemire and Rupp work), and files are memory-mapped by default. The headline gain comes from UQI: btree_visit.cc walks the leaf chain and hands each leaf's key and record arrays to a scan visitor (the MAX visitor is a plain scalar loop), with no per-record cursor call or key/record copy. The baselines instead iterate 50 million records one at a time through their client APIs.

## Compared with alternatives

Against LMDB, the closest catalogued B+tree sibling, pick upscaledb only when you need typed, compressed integer keys and built-in aggregates (MIN/MAX/SUM/COUNT/TOP over a key range) and are prepared to maintain an abandoned codebase; otherwise LMDB is the safer B+tree choice. LevelDB, the RocksDB derivatives, Badger and the other LSM siblings suit write-heavy random inserts better.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | Boost &gt;= 1.53 (system, filesystem, thread, chrono), protobuf (remote access), OpenSSL for AES (optional), zlib/snappy/lzf for compression, tcmalloc (optional), libdb-dev only for its comparison tests; autotools build (./configure && make) or an MSVC 2013 solution; shared and static libraries are both built. |
| **Minimum toolchain** | C++0x/C++11 (configure forces -std=c++0x); last fixes target GCC 10.2 and MSVC 2013; newer Boost.Asio (strand template change) and protobuf break the build |
| **Platforms** | Linux, macOS, other Unix, Windows (MSVC 2013, MinGW); x86 builds use SSE2/SSE4 when /proc/cpuinfo shows them, with a non-SIMD fallback added in 2018 |
| **Thread safety** | Each public API function locks the environment mutex (ScopedLock lock(env-&gt;mutex) in upscaledb.cc), so handles may be shared across threads but calls are serialised. The key-&gt;data and record-&gt;data pointers returned by lookups are not thread-safe unless you use UPS_KEY_USER_ALLOC/UPS_RECORD_USER_ALLOC (upscaledb.h). UQI plugins must be stateless. |
| **Drop-in for the baseline** | no |

## Gotchas

- A plain ./configure && make builds without optimisation. configure.ac sets CFLAGS to '-DNDEBUG' before AC_PROG_CC, which suppresses autoconf's default -O2, and then overwrites CXXFLAGS with "\$CFLAGS -std=c++0x", so any CXXFLAGS you set are discarded. Pass CFLAGS='-O2 -DNDEBUG' (the RPM spec passes RPM_OPT_FLAGS).
- Harness flaw: the homepage labels the run 'upscaledb v2.0.0', but no such release exists (hamsterdb 2.0.0 shipped in January 2012 with no analytical functions; the hola API arrived in May 2014). The published driver calls uqi_select with typed records, which the ChangeLog dates to 2016-02-23 (upscaledb 2.2.0). The label and the code do not match, and the driver's MAX check only prints a message on a wrong result (its exit is commented out).
- Licensing changed over time: hamsterdb was GPL, upscaledb 2.1.12-2.2.0 were GPL-3.0 (ChangeLog, Sep 2015), and only 2.2.1/master are Apache-2.0. Take the code from master or 2.2.1, not older tarballs.
- The default cache is about 2 MB (UPS_DEFAULT_CACHE_SIZE) and files are memory-mapped by default (UPS_DISABLE_MMAP turns this off). Size the cache with UPS_PARAM_CACHE_SIZE before comparing it with other engines.

## Known shortcomings

- Tier C: the '90x vs LevelDB, 140x vs BerkeleyDB' line exists only in a search snippet of upscaledb.com (ENOTFOUND here) and is not like for like (built-in MAX vs full iteration); the author's gist driver is built -O0 with library flags unstated, no CPU or timings, 2014-2016 versions. Abandoned (last commit 2021-08-20); Apache-2.0.
- Enricher: the homepage labels the run 'upscaledb v2.0.0' but no such release exists (hamsterdb 2.0.0, Jan 2012, had no analytics) and the gist uses uqi_select plus typed records added in 2.2.0 (2016-02-23), so label and code mismatch; the MAX check only prints on a wrong result; it compares an in-engine PAX-leaf MAX with a per-record cursor walk in an -O0 driver. A plain ./configure builds without -O (CFLAGS preset '-DNDEBUG' suppresses -O2, CXXFLAGS overwritten); global env mutex per API call; open cursor-correctness issues #50, #105-107; breaks with current Boost.Asio and protobuf (#134, #135); GPL-3.0 for 2.1.12-2.2.0, Apache only 2.2.1+. Abandoned 2021-08-20.

## Caveats and trade-offs

Snippet only: upscaledb.com did not resolve from this environment (getaddrinfo ENOTFOUND); a site-restricted WebSearch snippet of the homepage confirms the claim: full-table scan over 50 million records retrieving the maximum, upscaledb about 90 times faster than leveldb and about 140 times faster than BerkeleyDB, upscaledb v2.0.0, leveldb v1.11.0, BerkeleyDB v5.1.0, 64-bit Linux, 4 MB cache, with a link to the benchmark code. That code is the author's gist (https://gist.github.com/cruppstahl/dd98144e52ceac2e1df06df1fe7b852b, created 2016-04-04, one run per test, no results): upscaledb computes the max with its built-in query uqi_select('MAX(\$record) FROM DATABASE 1') inside the B+tree, while Berkeley DB and LevelDB walk every record with a cursor/iterator and track the max in driver code compiled with g++ -std=c++11 -g -O0, so the baselines' per-record loop runs unoptimized while upscaledb's runs in the optimized library; flags for the three libraries are not stated, no absolute timings or CPU model are published, LevelDB uses its default bytewise comparator on raw uint32 bytes with compression off, and the gist prints but does not exit on wrong results. Versions date from 2014-2016; the repo's last commit is 2021-08-20 and its README and ChangeLog carry no benchmarks. Per search snippets, a 2014-era hamsterdb-vs-leveldb post by the same author was mixed (hamsterdb faster on random reads and sequential inserts/scans, slower on random writes past about 10 million keys). The Lemire and Rupp paper (arXiv 1611.05428) was not reachable and compares codecs inside upscaledb only.

Sorted B+tree key/value store with transactions, logging and recovery, duplicate keys, optional integer-key compression (SIMD codecs) and network access; GPL history: lead listed GPLv3, repo README and COPYING now state Apache-2.0 (APL 2.0). The headline number is for an in-engine aggregate that LevelDB and Berkeley DB do not offer, so they are scanned key by key through cursors.

## Maintenance

Abandoned: the last commit is 2021-08-20 (an MSVC 2013 build fix), the newest open issues are unanswered build failures with current Boost and protobuf, and a Homebrew-core 'deprecate' commit is linked from issue #134. It is Apache-2.0 from 2.2.1, so it is copyable, but expect to patch the build and to own the open cursor-correctness issues.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party homepage claim (about 90x faster than LevelDB v1.11.0 and 140x faster than BerkeleyDB v5.1.0 on a 50-million-record max scan, 4 MB cache, 64-bit Linux), confirmed only through a WebSearch snippet of upscaledb.com; the linked benchmark code (gist benchmark.cc + Makefile) is public but has no results, no CPU model, and builds the driver at -O0 with library flags unstated, and the &gt;50x gain caps it at C anyway.
- **Verifier notes:** Homepage numbers confirmed by snippet only (vendor site blocked); tier C stands (first-party, no CPU model, &gt;50x with unstated library flags). Shortcomings to record: not like-for-like (built-in MAX vs full iteration), baseline loop compiled at -O0, no absolute timings or hardware, 2014-2016 versions, project abandoned (last commit 2021-08-20). Metadata checked: Apache-2.0, 572 stars, 70 forks, not archived.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-90 (wave 6); enricher w6 pair-010
- **Pages the verifier opened:**
  - <https://github.com/cruppstahl/upscaledb>
  - <https://github.com/cruppstahl/upscaledb/commits>
  - <https://gist.github.com/cruppstahl/dd98144e52ceac2e1df06df1fe7b852b>
  - <https://raw.githubusercontent.com/cruppstahl/upscaledb/HEAD/ChangeLog>
- **Sources the enricher read:**
  - <https://github.com/cruppstahl/upscaledb>
  - <https://github.com/cruppstahl/upscaledb/commits/master>
  - <https://github.com/cruppstahl/upscaledb/issues>
  - <https://github.com/cruppstahl/upscaledb/issues/134>
  - <https://github.com/cruppstahl/upscaledb/tree/master/src>
  - <https://github.com/cruppstahl/upscaledb/tree/master/src/4uqi>
  - <https://github.com/cruppstahl/upscaledb/tree/master/src/2simd>
  - <https://github.com/cruppstahl/upscaledb/tree/master/src/3btree>
  - <https://gist.github.com/cruppstahl/dd98144e52ceac2e1df06df1fe7b852b>
  - <https://raw.githubusercontent.com/cruppstahl/upscaledb/master/README>
  - <https://raw.githubusercontent.com/cruppstahl/upscaledb/master/ChangeLog>
  - <https://raw.githubusercontent.com/cruppstahl/upscaledb/master/COPYING>
  - <https://raw.githubusercontent.com/cruppstahl/upscaledb/master/INSTALL>
  - <https://raw.githubusercontent.com/cruppstahl/upscaledb/master/configure.ac>
  - <https://raw.githubusercontent.com/cruppstahl/upscaledb/master/Makefile.am>
  - <https://raw.githubusercontent.com/cruppstahl/upscaledb/master/upscaledb.spec>
  - <https://raw.githubusercontent.com/cruppstahl/upscaledb/master/src/Makefile.am>
  - <https://raw.githubusercontent.com/cruppstahl/upscaledb/master/include/ups/upscaledb.h>
  - <https://raw.githubusercontent.com/cruppstahl/upscaledb/master/include/ups/upscaledb_uqi.h>
  - <https://raw.githubusercontent.com/cruppstahl/upscaledb/master/src/4uqi/minmax.h>
  - <https://raw.githubusercontent.com/cruppstahl/upscaledb/master/src/4uqi/scanvisitor.h>
  - <https://raw.githubusercontent.com/cruppstahl/upscaledb/master/src/4uqi/uqi.cc>
  - <https://raw.githubusercontent.com/cruppstahl/upscaledb/master/src/4uqi/plugin_wrapper.h>
  - <https://raw.githubusercontent.com/cruppstahl/upscaledb/master/src/4env/env_local.cc>
  - <https://raw.githubusercontent.com/cruppstahl/upscaledb/master/src/3btree/btree_visit.cc>
  - <https://raw.githubusercontent.com/cruppstahl/upscaledb/master/src/3btree/btree_impl_pax.h>
  - <https://raw.githubusercontent.com/cruppstahl/upscaledb/master/src/3btree/btree_keys_pod.h>
  - <https://raw.githubusercontent.com/cruppstahl/upscaledb/master/src/2simd/simd.h>
  - <https://raw.githubusercontent.com/cruppstahl/upscaledb/master/src/5upscaledb/upscaledb.cc>
  - WebSearch snippet of https://upscaledb.com/ (site itself unreachable: getaddrinfo ENOTFOUND per verifier)
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/cruppstahl/upscaledb`) · [data/wave6/enrich/raw/github_com_cruppstahl_upscaledb.json](../../../data/wave6/enrich/raw/github_com_cruppstahl_upscaledb.json) (enrichment confidence 0.6)

</details>
