# HaloDB

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Embedded key-value stores](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Java` · `Apache-2.0` · 🔴 abandoned

> Java embedded key-value store for point lookups: append-only logs plus an off-heap hash index. Beats RocksDB on random writes and reads in IO-bound tests.

| | |
|---|---|
| **Beats** | RocksDB |
| **Claimed result** | The charts on the page are value-labelled. On 500M records, 8-byte keys and 1024-byte values: fill-random 127 MB/s vs RocksDB 10 and KyotoCabinet 14 (\~12.7x vs RocksDB, derived from page data); random update 19 MB/s vs RocksDB 2 and KyotoCabinet 4 (\~9.5x, derived); random read with 32 threads 94,409 ops/s vs RocksDB 59,936 and KyotoCabinet 86,230 (\~1.6x, derived); mixed read+update 45,750 reads/s and 6,144 writes/s vs RocksDB 8,625 and 2,691 (\~5.3x and \~2.3x, derived). HaloDB LOSES the fill-sequential test to RocksDB: 133 MB/s vs 165 MB/s (\~0.81x), though it beats KyotoCabinet's 31. |
| **Workload** | 500 million records, 8-byte keys / 1024-byte values (\~500GB, IO-bound): fill-sequential, random-read (32 threads, 640M reads), random-update, fill-random, and mixed read+update tests, vs RocksDB and KyotoCabinet. |
| **Metric** | throughput |
| **Hardware** | 2x Xeon E5-2680 2.50GHz (24 cores/48 threads HT), 128GB RAM, 1x Samsung PM863 960GB SSD (XFS), RHEL 6, kernel 2.6.32 |
| **Adoption** | 528 stars |
| **Last commit** | 2023-04-26 |
| **Links** | [repository](https://github.com/yahoo/HaloDB) · [benchmark](https://github.com/yahoo/HaloDB/blob/master/docs/benchmarks.md) |

## Verdict

This is a first-party benchmark from about 2018: 500M records with 8-byte keys and 1 KB values (about 500 GB) on 2x Xeon E5-2680, 128 GB RAM, one Samsung PM863 SSD and RHEL 6. It compared HaloDB with rocksdbjni 5.7.2 (WAL disabled, Snappy on L2 and above, custom 10 MB L1 tuning) and KyotoCabinet; the JVM version and flags are not stated. HaloDB won fill-random 127 vs 10 MB/s, random update 19 vs 2 MB/s, 32-thread random reads 94,409 vs 59,936 ops/s (about 1.6x) and mixed read+update 45,750 vs 8,625 reads/s and 6,144 vs 2,691 writes/s. It lost sorted-order fill to RocksDB, 133 vs 165 MB/s.

## Use it when

- JVM services doing only point lookups, where the data set is much larger than RAM but every key plus about 20 bytes of metadata fits in memory (e.g. 8-byte keys with 1-10 KB values)
- Write-heavy random insert/update workloads on SSD where LSM write amplification is the bottleneck: 127 vs 10 MB/s fill-random and 19 vs 2 MB/s random update against RocksDB in the project's test
- One writer thread (e.g. a consumer draining a Kafka log) with many concurrent readers that need sub-millisecond p99 reads, the setup Yahoo ran in production
- Kyoto Cabinet replacement in Java where fast crash recovery matters: only the one or two files being written need repair

## Skip it when

- You need range scans, ordered or prefix iteration, write batches, transactions or column families. Stay on RocksDB.
- Keys are longer than 127 bytes, or the whole key set will not fit in RAM. Yahoo quotes about 44 GB for 1 billion 8-byte keys with the memory pool and about 64 GB without.
- Bulk loads in sorted key order: RocksDB won that test (165 vs 133 MB/s). Disk use is also higher (556 GB vs RocksDB's 504 GB after 500M random updates).
- Restart time matters: opening a database scans every index and tombstone file to rebuild the index, which the README says can take minutes.
- You need a maintained dependency on a current JDK: the code targets Java 8 and relies on sun.misc.Unsafe, which is deprecated in JDK 23 (issue #63). The last release was 2021, and the Yahoo artifacts are not on Maven Central.

## How it is fast

It uses a Bitcask/Haystack-style log-structured hash design. Every write is a sequential append to a data file (1 GB in the examples). An in-memory hash index maps each key to its file id, value offset, size and sequence number, so a get needs at most one positional disk read (read amplification 1). The index lives off the Java heap to avoid GC pressure. It is derived from OHC, segmented like Java 7's ConcurrentHashMap with 2x-cores segments, and has an optional slab memory pool for fixed-size keys. A rate-limited background thread rewrites any file whose stale fraction passes a threshold, so a 50% threshold gives about 2x write amplification. Yahoo measured 10-12x for RocksDB on its own workload. Deletes go to separate tombstone files, and no key ordering is maintained.

## Compared with alternatives

Pick HaloDB when you must stay inside a Java process and only need point gets, puts and deletes. Badger and Pogreb (Go) and NuDB (C++) cannot be embedded directly in the JVM. If you can leave the JVM or need ordered access, one of those siblings or RocksDB fits better.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | slf4j-api 1.7.12, Guava 18.0, JNA 4.1.0 (native malloc for the off-heap index); lz4 1.3 optional. Jar is com.oath.halodb:halodb 0.5.6, published only to GitHub Packages (needs a token) or via JitPack as com.github.yahoo:HaloDB; not on Maven Central. |
| **Minimum toolchain** | Java 8 (compiled with source/target 1.8; CI runs only JDK 8). The README says newer JDKs are untested. A user in issue #63 reports it running on Java 22. |
| **Platforms** | The README says it was tested on Linux x86 and macOS. It needs a 64-bit JVM (the Uns class rejects address sizes above 8 bytes). Windows has an open bug where repair after an unclean shutdown fails (issue #23). Tuning advice: disable Transparent Huge Pages and set vm.swappiness=0. |
| **Thread safety** | get() is safe from many threads concurrently. put() and delete() share one global ReentrantLock, so writes are effectively single-threaded (issue #7; finer locking is a TODO). A LOCK file allows only one process per database directory. |
| **Drop-in for the baseline** | no |

## Gotchas

- The key limit is really 127 bytes (Byte.MAX_VALUE, checked in HaloDBInternal.put), not the 128 the README says. With the memory pool on, any key longer than the declared fixedKeySize is rejected.
- Writes are not durable by default. They land in the OS page cache and are synced only after flushDataSizeBytes accumulates, unless enableSyncWrites(true) is set, which the author says costs significant write throughput. After a power loss, interleaved puts and deletes keep only partial ordering.
- Interrupting a thread during IO makes the JVM close the FileChannel it was using, and the README warns not to do this.
- Set setNumberOfRecords (about 2x the expected key count) up front, or the off-heap index has to rehash. Without the memory pool every write calls native malloc, so the README recommends jemalloc against fragmentation.

## Known shortcomings

- RocksDB wins sequential fill (165 vs 133 MB/s); the gains (fill-random 12.7x, update 9.5x, read 1.6x) are vs rocksdbjni 5.7.2; abandoned.
- Abandoned (last release v0.5.6, 2021-05); Java 8 with sun.misc.Unsafe (deprecated in JDK 23); the jar is not on Maven Central. Keys max 127 B and all keys live in RAM (\~44 GB per 1B 8-byte keys); open scans all index files (minutes). One global write lock (single writer); no range scans/batches/transactions; not durable by default. The benchmark used RocksDB 5.7.2 with WAL off and an odd 10 MB L1; JVM unstated; Windows repair bug #23.

## Caveats and trade-offs

The author states HaloDB is not always better than RocksDB, and supports only a subset of RocksDB's features (no range scans), so the comparison 'is not exactly fair to RocksDB'. RocksDB beats HaloDB on sequential fill. HaloDB keeps all keys and metadata in an in-memory index, so it uses more RAM and disk space and has a slow index rebuild on startup. The baseline is old: rocksdbjni 5.7.2 (2017), with the WAL disabled and Snappy compression in the bench config. JVM version and flags are unstated. First-party benchmark, run on RHEL 6 / kernel 2.6.32.

No range scans or ordered access; entire key set + metadata must fit in memory; startup requires scanning all keys to rebuild the in-memory index.

## Maintenance

The Yahoo repository is abandoned: the last release is v0.5.6 (May 2021), the last commit is from April 2023, and an open 'Project status?' issue has no maintainer reply. It is Apache-2.0 and about 50 Java files, so it can be vendored. The live continuation is the community fork outr/HaloDB (halodb-revive 0.7.0 on Maven Central, JDK 22+, FFM instead of Unsafe, longer keys, prefix scans), but that fork is new and has almost no adoption.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification C, tier now C.
- **Tier reason:** First-party charts against RocksDB (rocksdbjni 5.7.2, tuned options, WAL disabled) and KyotoCabinet. The benchmark code is public (benchmarks/src/main/java/com/oath/halodb/benchmarks/BenchmarkTool.java, RocksDBStorageEngine.java) and the CPU and SSD are stated, but the JVM version and flags are not, so this is not A.
- **Verifier notes:** Downgraded because the claim was overstated: RocksDB wins the fill-sequential test (165 vs 133 MB/s), so HaloDB does not win 'across fill/read/update tests'. The record gave no numbers and said the page has none, but every embedded chart is value-labelled, so claimed_speedup now carries the chart values (numbers_found_on_page is null because there were no record numbers to check). Metadata checks out: Apache-2.0, 528 stars, not archived or a fork, last commit 2023-04-26, abandoned.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/yahoo/HaloDB>
  - <https://github.com/yahoo/HaloDB/blob/master/docs/benchmarks.md>
  - <https://raw.githubusercontent.com/yahoo/HaloDB/master/docs/benchmarks.md>
  - <https://raw.githubusercontent.com/amannaly/HaloDB-images/master/images/fill-sequential.png>
  - <https://raw.githubusercontent.com/amannaly/HaloDB-images/master/images/random-reads.png>
  - <https://raw.githubusercontent.com/amannaly/HaloDB-images/master/images/random-update.png>
  - <https://raw.githubusercontent.com/amannaly/HaloDB-images/master/images/fill-random.png>
  - <https://raw.githubusercontent.com/amannaly/HaloDB-images/master/images/read-update.png>
  - <https://raw.githubusercontent.com/yahoo/HaloDB/master/benchmarks/pom.xml>
  - <https://raw.githubusercontent.com/yahoo/HaloDB/master/benchmarks/src/main/java/com/oath/halodb/benchmarks/RocksDBStorageEngine.java>
- **Sources the enricher read:**
  - <https://github.com/yahoo/HaloDB>
  - <https://github.com/yahoo/HaloDB/blob/master/README.md>
  - <https://github.com/yahoo/HaloDB/blob/master/docs/benchmarks.md>
  - <https://github.com/yahoo/HaloDB/blob/master/docs/WhyHaloDB.md>
  - <https://github.com/yahoo/HaloDB/blob/master/CHANGELOG.md>
  - <https://github.com/yahoo/HaloDB/blob/master/pom.xml>
  - <https://github.com/yahoo/HaloDB/blob/master/.github/workflows/maven.yml>
  - <https://github.com/yahoo/HaloDB/blob/master/.github/workflows/maven-publish.yml>
  - <https://github.com/yahoo/HaloDB/blob/master/src/main/java/com/oath/halodb/HaloDB.java>
  - <https://github.com/yahoo/HaloDB/blob/master/src/main/java/com/oath/halodb/HaloDBInternal.java>
  - <https://github.com/yahoo/HaloDB/blob/master/src/main/java/com/oath/halodb/HaloDBOptions.java>
  - <https://github.com/yahoo/HaloDB/blob/master/src/main/java/com/oath/halodb/HaloDBFile.java>
  - <https://github.com/yahoo/HaloDB/blob/master/src/main/java/com/oath/halodb/InMemoryIndex.java>
  - <https://github.com/yahoo/HaloDB/blob/master/src/main/java/com/oath/halodb/InMemoryIndexMetaData.java>
  - <https://github.com/yahoo/HaloDB/blob/master/src/main/java/com/oath/halodb/CompactionManager.java>
  - <https://github.com/yahoo/HaloDB/blob/master/src/main/java/com/oath/halodb/Uns.java>
  - <https://github.com/yahoo/HaloDB/blob/master/src/main/java/com/oath/halodb/UnsafeAllocator.java>
  - <https://github.com/yahoo/HaloDB/blob/master/benchmarks/pom.xml>
  - <https://github.com/yahoo/HaloDB/blob/master/benchmarks/src/main/java/com/oath/halodb/benchmarks/RocksDBStorageEngine.java>
  - <https://github.com/yahoo/HaloDB/blob/master/benchmarks/src/main/java/com/oath/halodb/benchmarks/HaloDBStorageEngine.java>
  - <https://raw.githubusercontent.com/amannaly/HaloDB-images/master/images/fill-sequential.png>
  - <https://raw.githubusercontent.com/amannaly/HaloDB-images/master/images/fill-random.png>
  - <https://raw.githubusercontent.com/amannaly/HaloDB-images/master/images/random-reads.png>
  - <https://raw.githubusercontent.com/amannaly/HaloDB-images/master/images/read-update.png>
  - <https://github.com/yahoo/HaloDB/issues>
  - <https://github.com/yahoo/HaloDB/issues/3>
  - <https://github.com/yahoo/HaloDB/issues/5>
  - <https://github.com/yahoo/HaloDB/issues/7>
  - <https://github.com/yahoo/HaloDB/issues/10>
  - <https://github.com/yahoo/HaloDB/issues/17>
  - <https://github.com/yahoo/HaloDB/issues/23>
  - <https://github.com/yahoo/HaloDB/issues/26>
  - <https://github.com/yahoo/HaloDB/issues/28>
  - <https://github.com/yahoo/HaloDB/issues/42>
  - <https://github.com/yahoo/HaloDB/issues/44>
  - <https://github.com/yahoo/HaloDB/issues/52>
  - <https://github.com/yahoo/HaloDB/issues/58>
  - <https://github.com/yahoo/HaloDB/issues/63>
  - <https://github.com/yahoo/HaloDB/issues/68>
  - <https://github.com/yahoo/HaloDB/issues/69>
  - <https://github.com/yahoo/HaloDB/releases>
  - <https://github.com/yahoo/HaloDB/commits/master>
  - <https://github.com/outr/HaloDB>
  - <https://github.com/outr/HaloDB/releases>
  - <https://repo1.maven.org/maven2/com/oath/halodb/halodb/maven-metadata.xml>
  - <https://repo1.maven.org/maven2/com/outr/halodb-revive/maven-metadata.xml>
  - <https://hn.algolia.com/api/v1/search?query=HaloDB&tags=story>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/yahoo/halodb`) · [data/wave6/enrich/raw/github_com_yahoo_halodb.json](../../../data/wave6/enrich/raw/github_com_yahoo_halodb.json) (enrichment confidence 0.8)

</details>
