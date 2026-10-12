# Caffeine

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Caches](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Java` · `Apache-2.0` · 🟢 active

> Concurrent in-process JVM cache using W-TinyLFU and buffered policy updates; beats ConcurrentLinkedHashMap, Guava Cache and synchronized LinkedHashMap on multi-threaded throughput.

| | |
|---|---|
| **Beats** | ConcurrentLinkedHashMap (LRU) |
| **Claimed result** | Server-class (Xeon E5-2698B v3, 16 threads, bounded caches), GetPutBenchmark: 100% read 382.4M ops/s vs 313.9M (ConcurrentLinkedHashMap, \~1.2x) and 43.1M (Guava with concurrencyLevel 64, \~8.9x) (derived from page data); 75/25 read/write 279.4M vs 122.3M (\~2.3x) and 37.3M (Guava-64, \~7.5x) (derived from page data); 100% write 48.3M vs 39.8M (\~1.2x) (derived from page data). JDK LinkedHashMap LRU reaches only 13.6M/12.8M/10.9M ops/s in the same runs. |
| **Workload** | JMH microbenchmark (ComputeBenchmark/GetPutBenchmark) at 16 threads, varying read/write mixes (100% read, 75/25 read/write, 100% write) on a bounded in-process cache, vs ConcurrentLinkedHashMap, Guava Cache, Ehcache, Infinispan and plain ConcurrentHashMap |
| **Metric** | throughput |
| **Hardware** | Server-class: single-socket Xeon E5-2698B v3 @ 2.00GHz, 16 cores (hyperthreading disabled), 224GB RAM, Ubuntu 15.04, Azure G4 instance; desktop-class: MacBook Pro i7-4870HQ @ 2.50GHz |
| **Adoption** | 17.9k stars; used as the cache implementation inside Spring, Cassandra, Solr and others |
| **Last commit** | 2026-09-25 |
| **Links** | [repository](https://github.com/ben-manes/caffeine) · [benchmark](https://github.com/ben-manes/caffeine/wiki/Benchmarks) |

## Verdict

Only the author's own JMH GetPutBenchmark numbers exist. They date from about 2015 and an early Caffeine release, and the JVM version and flags are not stated. The run was on a 16-core Azure G4 Xeon E5-2698B v3 (hyperthreading off, Ubuntu 15.04). At 16 threads, bounded Caffeine did 382M ops/s on 100% reads vs 314M for ConcurrentLinkedHashMap (\~1.2x) and 43M for Guava at concurrencyLevel 64; 279M vs 122M on 75/25 read/write (\~2.3x); and 48M vs 40M on 100% writes (\~1.2x). In the current benchmark source the cache is prepopulated for a 100% hit rate with \~11K Zipf-distributed keys against a 65,536-entry bound, so the runs measure hit and update bookkeeping, not eviction throughput. No C++ or stdlib comparison is involved.

## Use it when

- Read-heavy, skewed (Zipf-like) lookups inside one JVM with many threads, where a synchronized LinkedHashMap LRU or Guava Cache is the contention point (author's 16-thread server run: 382M reads/s vs 43M for Guava at concurrencyLevel 64 and 13.6M for LinkedHashMap LRU).
- Mixed read/write traffic on a bounded cache: 75/25 read/write was 2.3x ConcurrentLinkedHashMap's throughput in the same run.
- Workloads where LRU hit rate suffers from scans, loops or shifting recency/frequency patterns: the author's trace simulations show W-TinyLFU near Belady's optimum and competitive with ARC and LIRS without keeping ghost entries.
- Services that need loading, async refresh, per-entry variable expiration (timer wheel, amortized O(1)) or stampede protection via AsyncCache, not just a bounded map.
- Existing Spring, Quarkus, Micronaut, Play or Guava-cache code: integrations exist, and CaffeinatedGuava provides an adapter for code written against Guava's cache interfaces.

## Skip it when

- State has to be shared across processes or hosts, or has to survive restarts: this is a per-JVM on-heap cache with no off-heap or persistence mode; use a networked cache (or put Caffeine in front of one as an L1).
- Write floods: writes go through a bounded buffer drained by one maintenance thread, and writers spin and then yield when it is full. In the author's own 100% write run, Caffeine (48.3M ops/s) is only \~1.2x ConcurrentLinkedHashMap and slightly below unbounded ConcurrentHashMap (50.6M). In issue #1320 a user's non-JMH test found writes slower than Guava when using merge() with both expiration modes enabled.
- Code that relies on strict LRU order or exact capacity: the policy is eventually consistent with the map, eviction runs once the maximum is crossed (Guava evicts before), and TinyLFU can reject newly inserted entries.
- Memory-tight caches that use weak or soft references: the author's measurements show 112 bytes per entry for weakKeys+weakValues vs 72 for Guava (it is 64 vs 64 for plain maximumSize).
- Java 8 runtimes (3.x needs Java 11; stay on 2.x) or Android/GWT, which the wiki says are not supported.

## How it is fast

It follows the BP-Wrapper idea: reads are recorded into striped, lossy ring buffers and writes into a bounded, growable MPSC queue, and a single thread replays them in batches under a try-lock. Readers therefore never contend on the LRU-list lock that ConcurrentLinkedHashMap-style and Guava-style caches take or segment. It decorates Java 8's ConcurrentHashMap (lock-free reads), uses relaxed memory ordering where the lock already provides visibility, and generates a separate class for each feature combination so unused per-entry fields are dropped. For compute/get-with-loader it checks for a present entry without locking before falling back to computeIfAbsent (1.58B vs 29.7M ops/s for plain ConcurrentHashMap on a single hot key in the author's server run). Hit rate comes from Window TinyLFU: a small LRU admission window, a segmented-LRU main space, a 4-bit Count-Min Sketch frequency filter, and hill climbing to size the window.

## Compared with alternatives

Garnet, Pelikan/Segcache and KeyDB are networked Redis/Memcached-style servers shared by many clients. Pick Caffeine when the cache can live inside a single JVM process, which avoids a network hop and serialization per lookup, or use it as a near cache in front of one of them.

## Integration

| | |
|---|---|
| **Form** | module (Maven Central jar com.github.ben-manes.caffeine:caffeine, about 1.06 MB for 3.3.0; JPMS module com.github.benmanes.caffeine) |
| **Dependencies** | jspecify 1.0.1 and error_prone_annotations 2.50.0, which are annotation-only jars declared 'requires static' in module-info; optional extra artifacts are caffeine-guava and caffeine-jcache |
| **Minimum toolchain** | Java 11+ for 3.x (the build defaults to Java 11 as the release target); Java 8 needs the 2.x line |
| **Platforms** | any JVM 11+; the wiki says Android/GWT are not supported |
| **Thread safety** | Fully thread-safe: retrievals are fully concurrent and updates are expected to be highly concurrent. The eviction/expiration policy is updated in batches and is eventually consistent with the map. Maintenance and removal notifications run on the configured Executor, which defaults to ForkJoinPool.commonPool(). |
| **Drop-in for the baseline** | partial — ConcurrentLinkedHashMap is a ConcurrentMap built with its own Builder. Caffeine has a different builder and Cache interface and exposes a ConcurrentMap only through asMap(). It evicts by W-TinyLFU rather than LRU, so eviction order and listener timing differ. ConcurrentLinkedHashMap's README tells projects on JDK 8+ to move to Caffeine. |

## Gotchas

- Loads and asMap().compute run inside ConcurrentHashMap's bin locks. A slow load can block other keys that hash to the same bin and can stall eviction (issue #672). A compute must not write to the same cache, which livelocks on Java 8 and throws IllegalStateException on 9+. The documented mitigations are AsyncCache or a larger initialCapacity.
- Mutating a key's equals/hashCode while it is cached corrupts state. In 2.x this could spin a CPU at 100% in a retry loop (issue #1696); since v3.1.2 it throws IllegalStateException instead.
- Expiration and eviction happen only during maintenance triggered by cache activity, and that maintenance runs asynchronously on the executor. Configure a Scheduler (e.g. Scheduler.systemScheduler()) if entries must expire promptly, and call cleanUp() or use a direct executor in tests.
- weakKeys(), weakValues() and softValues() switch comparisons to identity (==) instead of equals(). Weights are computed only on write and do not change afterwards.

## Known shortcomings

- Only first-party numbers from \~2015 (Azure G4, Ubuntu 15.04, early release), JVM version and flags unstated, no independent benchmark. The current GetPutBenchmark prepopulates \~11K Zipf keys against a 65,536-entry bound (100% hits, no eviction), so it measures hit/update bookkeeping, not eviction. Gain over ConcurrentLinkedHashMap is modest (\~1.2x read-only and write-only, 2.3x at 75/25); the 7-9x ratios are against Guava (concurrencyLevel 64). CLHM is the same author's predecessor. Java, not C++. Writes slower than Guava under write floods with both expirations on (#1320); slow loads block other keys and eviction via ConcurrentHashMap bin locks (#672); mutable keys caused 100% CPU in 2.x (#1696).

## Caveats and trade-offs

First-party numbers only. The exact JVM version and flags for the JMH run are not given. The server run is an old Azure G4 / Ubuntu 15.04 setup (the desktop run is on OS X Yosemite), so the figures date from roughly 2015 and an early Caffeine release. The Guava ratios use Guava tuned to concurrencyLevel 64; Guava's default does worse. Benchmark code is public (ComputeBenchmark.java, GetPutBenchmark.java under caffeine/src/jmh). Language is Java, not C++.

In-process JVM cache, not a distributed/remote cache like Redis or Memcached, so it solves a different deployment problem (per-process hit ratio and speed rather than shared/networked state); W-TinyLFU admission policy adds bookkeeping vs a plain LRU

## Maintenance

Actively maintained: v3.3.0 was released 2026-09-21, there are commits through 2026-09-25, and 1 issue is open. It is an Apache-2.0 Maven dependency and the default in-process cache of many JVM frameworks. The baseline, ConcurrentLinkedHashMap, is the same author's predecessor and has been in maintenance mode since Caffeine appeared.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification B, tier now C.
- **Tier reason:** First-party wiki page with JMH numbers against ConcurrentLinkedHashMap, Guava, Ehcache, Infinispan and java.util.LinkedHashMap LRU. The code is public (caffeine/src/jmh/.../GetPutBenchmark.java) and the CPU is stated, but the JVM version and flags are not. The rubric makes the project's own benchmark code with partial methodology C, not B; there is no peer-reviewed or independent third-party source.
- **Verifier notes:** All the figures match the server-class tables on the wiki; the ratios are computed and are now marked as derived. The C++-only search filter returned a Java project. The rubric's rule that own code with partial methodology is C forced the downgrade from B.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/ben-manes/caffeine/wiki/Benchmarks>
  - <https://raw.githubusercontent.com/wiki/ben-manes/caffeine/Benchmarks.md>
  - <https://github.com/ben-manes/caffeine>
- **Sources the enricher read:**
  - <https://github.com/ben-manes/caffeine>
  - <https://github.com/ben-manes/caffeine/wiki/Benchmarks>
  - <https://raw.githubusercontent.com/wiki/ben-manes/caffeine/Benchmarks.md>
  - <https://raw.githubusercontent.com/wiki/ben-manes/caffeine/Design.md>
  - <https://raw.githubusercontent.com/wiki/ben-manes/caffeine/Efficiency.md>
  - <https://raw.githubusercontent.com/wiki/ben-manes/caffeine/Faq.md>
  - <https://raw.githubusercontent.com/wiki/ben-manes/caffeine/Eviction.md>
  - <https://raw.githubusercontent.com/wiki/ben-manes/caffeine/Guava.md>
  - <https://raw.githubusercontent.com/wiki/ben-manes/caffeine/Compute.md>
  - <https://raw.githubusercontent.com/wiki/ben-manes/caffeine/Memory-overhead.md>
  - <https://raw.githubusercontent.com/wiki/ben-manes/caffeine/Population.md>
  - <https://github.com/ben-manes/caffeine/blob/master/caffeine/src/jmh/java/com/github/benmanes/caffeine/cache/GetPutBenchmark.java>
  - <https://github.com/ben-manes/caffeine/blob/master/caffeine/src/jmh/java/com/github/benmanes/caffeine/cache/CacheType.java>
  - <https://github.com/ben-manes/caffeine/blob/master/caffeine/src/jmh/java/com/github/benmanes/caffeine/cache/impl/LinkedHashMapCache.java>
  - <https://github.com/ben-manes/caffeine/blob/master/caffeine/src/main/java/com/github/benmanes/caffeine/cache/BoundedLocalCache.java>
  - <https://github.com/ben-manes/caffeine/blob/master/caffeine/src/main/java/com/github/benmanes/caffeine/cache/FrequencySketch.java>
  - <https://github.com/ben-manes/caffeine/blob/master/caffeine/src/main/java/com/github/benmanes/caffeine/cache/StripedBuffer.java>
  - <https://github.com/ben-manes/caffeine/blob/master/caffeine/src/main/java/module-info.java>
  - <https://github.com/ben-manes/caffeine/blob/master/caffeine/build.gradle.kts>
  - <https://github.com/ben-manes/caffeine/blob/master/gradle/plugins/src/main/kotlin/lifecycle/java-library.caffeine.gradle.kts>
  - <https://github.com/ben-manes/caffeine/blob/master/gradle/plugins/src/main/kotlin/ProjectExtensions.kt>
  - <https://github.com/ben-manes/caffeine/releases>
  - <https://github.com/ben-manes/caffeine/issues/672>
  - <https://github.com/ben-manes/caffeine/issues/1320>
  - <https://github.com/ben-manes/caffeine/issues/1696>
  - <https://github.com/ben-manes/concurrentlinkedhashmap>
  - <https://repo1.maven.org/maven2/com/github/ben-manes/caffeine/caffeine/3.3.0/caffeine-3.3.0.pom>
  - <https://repo1.maven.org/maven2/com/github/ben-manes/caffeine/caffeine/3.3.0/caffeine-3.3.0.jar>
  - <https://hn.algolia.com/api/v1/search?query=caffeine%20cache>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/ben-manes/caffeine`) · [data/wave6/enrich/raw/github_com_ben_manes_caffeine.json](../../../data/wave6/enrich/raw/github_com_ben_manes_caffeine.json) (enrichment confidence 0.8)

</details>
