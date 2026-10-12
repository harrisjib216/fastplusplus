# count-db

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Embedded key-value stores](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Java` · `MIT` · 🔴 abandoned

> Java embedded store for 64-bit-keyed counters; first-party bigram test: \~82x LevelDB write, \~12x read throughput.

| | |
|---|---|
| **Beats** | LevelDB |
| **Claimed result** | Bigram-count test, 8 threads, ops/sec. Writing 256M counts: count-db 1.12E7 vs LevelDB 1.37E5 (\~82x, derived from page data; the README rounds this to '80 times') and RocksDB 1.40E5. Reading 256M counts: 1.06E7 vs LevelDB 8.90E5 (\~12x, derived from page data; the README says '11 times') and RocksDB 4.93E5. Across 1M-256M items, count-db beats LevelDB by \~19x-82x on writes and \~3.9x-15x on reads (derived from page data). Uniform-count test at 128M: write 1.48E7 vs LevelDB 1.56E5 (\~95x, derived), RocksDB 1.07E5 and Kyoto Cabinet 2.01E6; read 2.29E7 vs LevelDB 8.32E5 (\~28x, derived). In the mixed parallel test at 128M: read 1.75E6 and write 1.74E6, vs LevelDB 2.02E5 and 1.24E5. |
| **Workload** | JNI-bound Java benchmark writing/reading 1M-256M Wikipedia bigram counts (8 threads), plus a uniform-random-count test, against LevelDB, RocksDB and Kyoto Cabinet. |
| **Metric** | throughput |
| **Hardware** | Intel i7-4770, SATA 6Gb/s 7200rpm HDD, 32GB RAM (10GB JVM heap) |
| **Adoption** | 57 stars |
| **Last commit** | 2019-10-31 |
| **Links** | [repository](https://github.com/koendeschacht/count-db) · [benchmark](https://github.com/koendeschacht/count-db/blob/master/doc/performance.md) |

## Verdict

These are first-party ops/sec figures. The hardware was an i7-4770 with a 7200 rpm SATA HDD and 32 GB RAM (10 GB JVM heap); the JVM version and flags are not stated. Eight threads called increaseCount/readCount on Wikipedia bigram hashes. count-db ran with its cache and Bloom layers; LevelDB (leveldbjni), RocksDB (RocksJava) and Kyoto Cabinet ran uncached with default options. The LevelDB and RocksDB adapters do a per-key-locked get-then-put per increment, no merge operator on this path, and LevelDB gets no filter policy. At 256M bigrams count-db reached 1.12E7 writes/s vs LevelDB 1.37E5 (\~82x) and 1.06E7 reads/s vs 8.90E5 (\~12x). The uniform test draws 128M increments from only 1M distinct keys (Random.nextInt(1000000)), so for count-db it is effectively an in-heap counter test.

## Use it when

- Counting n-grams, events or per-entity tallies from Java where the same keys are incremented many times (Zipf/power-law keys) and bulk throughput matters more than durability of each write.
- Batch pipelines with separate write and read phases: it detects write phases and defers compaction, and optimizeForReading() compacts everything before the read phase.
- Keys that are already 64-bit longs (IDs, precomputed hashes) and values that are primitives or small JSON-serializable objects.
- Single-machine data sets larger than the heap, where you would otherwise hand-roll a HashMap that spills to disk.
- Legacy Java 8 code that can vendor MIT-licensed source rather than depend on a maintained artifact.

## Skip it when

- You need durability or crash consistency. Files are written with plain FileOutputStream append and close, with no fsync. The cache layer holds writes in heap for up to about 1 s, and writes are not visible to reads until flush().
- You need exact String or byte[] keys, or ordered scans over the original keys. Strings are hashed to 64 bits with a multiply-by-65599 hash and not stored, so collisions merge silently and iterators return hashes.
- You need transactions, snapshots, several processes sharing one data directory, or a LevelDB/RocksDB-compatible API.
- Your writes are write-once or have few repeated keys. The published speedups come from in-memory combining of repeated increments, and no fair benchmark covers this case.
- You need a maintained production dependency. The last code commit was in 2019. Master depends on master-SNAPSHOT builds of the author's utility libraries via JitPack and on jackson-databind 2.9.7, with Dependabot bump PRs left open. The only Maven Central release (1.1.12) dates from October 2015 and pulls in Spring 4.1.

## How it is fast

By default a write-combining cache sits in front of the store. Writes go into 10 in-heap hash maps, sharded by key mod 10, where repeated keys are combined in memory. A background job flushes those maps to disk in batches every second, so a hot key costs one disk write per flush instead of one read-modify-write per increment. Underneath is a hash-partitioned append-then-compact log: keys are split into 64 buckets by their low 6 bits, and each bucket is a list of key-range files that take blind appends. A periodic job, or the first read of a dirty bucket, sorts each file, merges duplicates with the Combinator and rewrites it to about 10 MB with a sparse in-memory offset index. Reads binary-search that index and scan a short run. Whole files are cached on heap up to a third of available memory, and an optional per-interface Bloom filter answers misses.

## Compared with alternatives

HyperLevelDB keeps LevelDB's API and storage semantics for a \~3.4x write gain; HaloDB is a general value store catalogued as beating RocksDB and Kyoto Cabinet on fill-random. Pick count-db over either only for increment-heavy counters on 64-bit keys inside one JVM, where in-memory write combining and merge-on-compaction do the work. For general get/put or durable storage, use those siblings.

## Integration

| | |
|---|---|
| **Form** | module (Maven JAR: be.bagofwords:count-db:1.1.12 on Central from 2015; current master is com.github.koendeschacht:count-db:master-SNAPSHOT via JitPack) |
| **Dependencies** | master: bow-utils, bow-utils-extra and mini-dep-i (all master-SNAPSHOT via JitPack), guava 19.0, commons-io 2.5, commons-lang3 3.4, jackson-databind 2.9.7, lmdbjni-linux64 0.4.6, snappy-java 1.1.2.6; the 1.1.12 release also pulls in Spring 4.1.0 (beans/context/core/test) and jackson-databind 2.3.3 |
| **Minimum toolchain** | Java 8 (maven-compiler source/target 1.8); newer JDKs not documented |
| **Platforms** | Any JVM in principle, since the file backend is pure Java, though the core POM still declares lmdbjni-linux64. The benchmark comparison needs Linux x86-64 JNI libraries (bundled in count-db-run/lib). Otherwise not documented. |
| **Thread safety** | Built for concurrent use: the file store uses a ReentrantReadWriteLock per bucket, the cache layer has 10 synchronized write buffers, and the benchmarks run 8 threads. Only one owner per data directory is allowed (LOCK file); if another interface takes the lock, the original logs an error and closes itself. |
| **Drop-in for the baseline** | no |

## Gotchas

- Writes only become visible to reads after flush(), which the README states explicitly. Cached writers block when the heap monitor (MemoryManager) reports low memory, and that monitor can call System.gc().
- The first read on a bucket written since its last compaction synchronously rewrites the whole bucket (lockForRead -&gt; rewriteBucket), so read latency can spike right after write bursts.
- The default config enables the cache layer (DataInterfaceConfig sets cache=true) but not the Bloom filter. The published numbers used CACHED_AND_BLOOM, which you must request.
- Stale docs: the README's ExampleUsage.java link and the benchmark-source links in doc/performance.md are dead because the code moved to count-db-run/. The README's Maven coordinates point to the 2015 release, not current master.

## Known shortcomings

- Unfair setup: cached count-db writes vs read-modify-write LevelDB; ratios (\~82x/\~12x, uniform write \~95x) are derived; benchmark links are dead (code moved to count-db-run/); abandoned.
- The speedup is in-heap write combining plus a Bloom filter vs uncached LevelDB/RocksDB doing get-then-put per increment with no merge operator (LevelDB without a filter policy); the uniform test is 128M increments over only 1M distinct keys. No fsync (writes sit \~1 s in heap); string keys are hashed to 64 bits and not stored, so collisions merge silently; the first read on a dirty bucket triggers a synchronous rewrite. Stale dependencies (Spring 4.1, jackson-databind 2.9.7); abandoned 2019.

## Caveats and trade-offs

Old (2015-era) hardware: an i7-4770 with a 7200rpm SATA HDD, no SSD. JVM version and flags are unstated. First-party benchmark. All baselines run with default parameters through JNI bindings. In the benchmark source, count-db runs with its in-process CACHED_AND_BLOOM caching layer while the (now commented-out) baseline lines use DatabaseCachingType.DIRECT. The LevelDB adapter implements each count increment as a get-then-put read-modify-write, with no merge operator. The workload therefore favours count-db's write-combining counter design over general-purpose stores. Ratios reach \~95x (uniform write vs LevelDB), above the &gt;50x implausibility threshold with flags unstated, which caps it at tier C. The benchmark-source links in doc/performance.md are dead because the code moved to count-db-run/.

Optimized narrowly for primitive counters/counts and simple serialized objects; no SQL-style querying or transactions.

## Maintenance

Abandoned since 2019-10-31, with only Dependabot PRs after that and the last Central release in 2015. It is MIT-licensed plain Java 8, so vendoring src/ together with the author's bow-utils/bow-utils-extra/mini-dep-i sources is the realistic way to use it.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party ops/sec tables against LevelDB, RocksDB and Kyoto Cabinet (via JNI, default parameters). The benchmark code is public (count-db-run/src/main/java/be/bagofwords/db/benchmarks/bigrams/BigramTestsMain.java and uniform/UniformDataTestsMain.java) and the CPU is stated (i7-4770), but the JVM version and flags are not. Ratios reach \~95x with flags unstated, so the &gt;50x rule also caps it at C.
- **Verifier notes:** Every raw number in the record matches doc/performance.md. The \~80x and \~11x figures come from the README; the page itself has only raw tables, so ratios are now marked as derived. Metadata checks out: MIT, 57 stars, not a fork or archived, last commit 2019-10-31, abandoned. The main shortcoming is the asymmetric setup: a cached, write-combining count-db against uncached read-modify-write LevelDB and RocksDB adapters.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/koendeschacht/count-db>
  - <https://github.com/koendeschacht/count-db/blob/master/doc/performance.md>
  - <https://raw.githubusercontent.com/koendeschacht/count-db/master/doc/performance.md>
  - <https://raw.githubusercontent.com/koendeschacht/count-db/master/README.md>
  - <https://raw.githubusercontent.com/koendeschacht/count-db/master/count-db-run/src/main/java/be/bagofwords/db/benchmarks/bigrams/BigramTestsMain.java>
  - <https://raw.githubusercontent.com/koendeschacht/count-db/master/count-db-run/src/main/java/be/bagofwords/db/interfaces/leveldb/LevelDBDataInterface.java>
  - <https://raw.githubusercontent.com/koendeschacht/count-db/master/count-db-run/src/main/java/be/bagofwords/db/interfaces/rocksdb/RocksDBDataInterface.java>
- **Sources the enricher read:**
  - <https://github.com/koendeschacht/count-db>
  - <https://github.com/koendeschacht/count-db/blob/master/README.md>
  - <https://github.com/koendeschacht/count-db/blob/master/doc/performance.md>
  - <https://github.com/koendeschacht/count-db/blob/master/pom.xml>
  - <https://github.com/koendeschacht/count-db/blob/master/count-db-run/pom.xml>
  - <https://github.com/koendeschacht/count-db/blob/master/count-db-run/README.md>
  - <https://github.com/koendeschacht/count-db/blob/master/src/main/resources/count-db.properties>
  - <https://github.com/koendeschacht/count-db/blob/master/src/main/java/be/bagofwords/db/filedb/FileDataInterface.java>
  - <https://github.com/koendeschacht/count-db/blob/master/src/main/java/be/bagofwords/db/filedb/FileBucket.java>
  - <https://github.com/koendeschacht/count-db/blob/master/src/main/java/be/bagofwords/db/cached/CachedDataInterface.java>
  - <https://github.com/koendeschacht/count-db/blob/master/src/main/java/be/bagofwords/db/bloomfilter/BloomFilterDataInterface.java>
  - <https://github.com/koendeschacht/count-db/blob/master/src/main/java/be/bagofwords/db/DataInterface.java>
  - <https://github.com/koendeschacht/count-db/blob/master/src/main/java/be/bagofwords/db/DataInterfaceConfig.java>
  - <https://github.com/koendeschacht/count-db/blob/master/src/main/java/be/bagofwords/db/DatabaseCachingType.java>
  - <https://github.com/koendeschacht/count-db/blob/master/src/main/java/be/bagofwords/db/DatabaseBackendType.java>
  - <https://github.com/koendeschacht/count-db/blob/master/src/main/java/be/bagofwords/db/impl/BaseDataInterfaceFactory.java>
  - <https://github.com/koendeschacht/count-db/blob/master/src/main/java/be/bagofwords/db/application/EmbeddedDBContextFactory.java>
  - <https://github.com/koendeschacht/count-db/blob/master/src/main/java/be/bagofwords/db/combinator/LongCombinator.java>
  - <https://github.com/koendeschacht/count-db/blob/master/count-db-run/src/main/java/be/bagofwords/db/benchmarks/bigrams/BigramTestsMain.java>
  - <https://github.com/koendeschacht/count-db/blob/master/count-db-run/src/main/java/be/bagofwords/db/benchmarks/bigrams/BigramTestsThread.java>
  - <https://github.com/koendeschacht/count-db/blob/master/count-db-run/src/main/java/be/bagofwords/db/benchmarks/uniform/UniformDataTestsMain.java>
  - <https://github.com/koendeschacht/count-db/blob/master/count-db-run/src/main/java/be/bagofwords/db/benchmarks/uniform/UniformDataTestsThread.java>
  - <https://github.com/koendeschacht/count-db/blob/master/count-db-run/src/main/java/be/bagofwords/db/interfaces/leveldb/LevelDBDataInterface.java>
  - <https://github.com/koendeschacht/count-db/blob/master/count-db-run/src/main/java/be/bagofwords/db/interfaces/rocksdb/RocksDBDataInterface.java>
  - <https://github.com/koendeschacht/count-db/issues?q=is%3Aissue>
  - <https://github.com/koendeschacht/count-db/issues/1>
  - <https://github.com/koendeschacht/count-db/pulls?q=is%3Apr>
  - <https://github.com/koendeschacht/count-db/commits/master>
  - <https://github.com/koendeschacht/bow-utils/blob/master/src/main/java/be/bagofwords/util/HashUtils.java>
  - <https://github.com/koendeschacht/bow-utils-extra/blob/master/src/main/java/be/bagofwords/memory/MemoryManager.java>
  - <https://search.maven.org/solrsearch/select?q=g:be.bagofwords+AND+a:count-db&core=gav&rows=20&wt=json>
  - <https://repo1.maven.org/maven2/be/bagofwords/count-db/1.1.12/count-db-1.1.12.pom>
  - <https://repo1.maven.org/maven2/be/bagofwords/count-db/1.1.12/count-db-1.1.12.jar>
  - <https://hn.algolia.com/api/v1/search?query=count-db%20bagofwords&tags=story>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/koendeschacht/count-db`) · [data/wave6/enrich/raw/github_com_koendeschacht_count_db.json](../../../data/wave6/enrich/raw/github_com_koendeschacht_count_db.json) (enrichment confidence 0.8)

</details>
