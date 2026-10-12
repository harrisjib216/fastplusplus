# xor-filter (Java, komiya-atsushi)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Probabilistic filters](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Java` · `MIT` · 🔴 abandoned

> Small Java xor filter (8/16-bit) built on Guava Funnels; about 2x faster Long-key queries than Guava BloomFilter at equal FPR.

| | |
|---|---|
| **Beats** | Bloom filter (Guava com.google.common.hash.BloomFilter) |
| **Claimed result** | Long keys: 17,458.015 q/ms (xor8) vs 8,879.024 q/ms (Guava Bloom, fpp=0.389%), \~1.97x (derived from page data). String keys: 7,121.787 vs 5,318.409 q/ms, \~1.34x (derived from page data). Serialization: 123,042 bytes / 9.843 bits per entry (xor8) vs 144,390 bytes / 11.551 bits per entry (Bloom, fpp=0.389%), \~1.17x smaller (derived from page data). |
| **Workload** | JMH (me.champeau.gradle.jmh 0.5.0, default settings, results in ms) query throughput over a 16,384-element filter (NUM_ELEMENTS = 1 &lt;&lt; 14) for Long and String keys, plus serialization size (FppAndSerializationSize.java). Xor Filter (8-bit, 16-bit, Murmur128 via Guava Funnels) is compared against Guava 28.2-jre BloomFilter at fpp=0.389% and fpp=0.002%. |
| **Metric** | throughput |
| **Adoption** | 20 stars |
| **Last commit** | 2020-01-23 |
| **Links** | [repository](https://github.com/komiya-atsushi/xor-filter) · [benchmark](https://github.com/komiya-atsushi/xor-filter#benchmark) |

## Verdict

This is first-party JMH (Gradle jmh plugin 0.5.0 defaults, time unit ms) on an undisclosed JVM and CPU. Each filter was built from 8,192 keys (every other of 16,384 pregenerated keys) and queried round-robin over all 16,384, so half the queries hit, everything stayed cache-resident, and hashing went through Guava 28.2 murmur3_128 for both filters. XOR8 did 17,458 vs 8,879 queries/ms against Guava BloomFilter at fpp 0.389% for boxed Long keys (1.97x) and 7,122 vs 5,318 for 20-character strings (1.34x). A separate 100,000-key run gave 9.84 vs 11.55 bits/key serialized (1.17x smaller). All ratios are derived from the README tables.

## Use it when

- JVM service with a static key set built once, queried many times and shipped as bytes, e.g. a nightly blocklist, known-ID set or per-segment key set.
- You already use Guava Funnels/BloomFilter and want about 2x faster Long-key queries at the same \~0.39% FPR with about 15% less memory (XOR8: 9.84 vs 11.55 bits/key).
- You need a very low FPR. XOR16 vs Guava Bloom at fpp 0.002% ran 2.6x faster on Long keys (16,976 vs 6,535 q/ms) at 19.69 vs 22.52 bits/key.
- Workloads with many positive lookups, where a Bloom filter must test all k bits while the xor filter always does exactly three reads.
- You want a tiny, auditable piece of code to vendor: two source files (about 516 lines), Java 8, Guava as the only dependency.

## Skip it when

- Keys arrive incrementally, or the set changes: there is no put/remove/merge, so every change means rebuilding from a complete in-memory Collection. Guava BloomFilter supports put/putAll.
- You need it as a Gradle/Maven dependency. me.k11i:xor-filter was published only to Bintray, which is gone, and Maven Central has no me.k11i artifacts. FastFilter/fastfilter_java is maintained (Apache-2.0, pushed 2026-07) and adds binary fuse and xor+ filters, but it takes pre-hashed long keys.
- Space is the priority. There is no binary fuse or xor+ variant, so XOR8 costs 9.84 bits/key at 100k keys, and the fixed +32-slot overhead inflates tiny filters.
- Very large sets under tight heap. Construction holds all keys plus temporary arrays of roughly 35 bytes/key: sorted hashes, per-slot xor and count, queue, and stack (derived from the source). Bloom filters build by streaming.
- Long or expensive-to-hash keys (e.g. strings), where the query gain falls to about 1.34x and may not justify adopting unmaintained code with no issue history and tests only at 5,000-10,000 keys.

## How it is fast

It implements Graf & Lemire's xor filter (arXiv 1912.08258), a Dietzfelbinger-Pagh / Bloomier-style construction. Each key maps to three slots, one in each third of an array of about 1.23n+32 fingerprints, and a query is just fingerprint == B[h0] ^ B[h1] ^ B[h2]: exactly three array reads, with multiply-shift range reduction instead of division. Both this library and Guava's BloomFilter (MURMUR128_MITZ_64 strategy) compute one Guava murmur3_128 per query. Guava then tests numHashFunctions bits by double hashing, with a 64-bit modulo per probe; the xor filter adds one MurmurHash3 fmix64 and the three reads. Because the expensive hash is shared, the gap shrinks when hashing dominates (1.97x for Long keys vs 1.34x for 20-character strings). Construction is hypergraph peeling: a queue of singleton slots, a stack, then back-assignment, retried with a new seed if peeling fails.

## Compared with alternatives

Every catalogued xor/binary-fuse sibling targets another runtime: xor_singleheader (C), xorfilter (Go), xorf (Rust), exor_filter (Erlang) and BinaryFuseFilter (.NET). Pick this one only when you need a pure-JVM xor filter keyed through Guava Funnels. If native code or another language is an option, those siblings are maintained and offer binary fuse filters, which sit within 13% of the space lower bound vs 23% for xor, per the Go sibling.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | Guava (built against 28.2-jre; uses Funnel, HashFunction, Hashing.murmur3_128) |
| **Minimum toolchain** | Java 8 (0.1.1 was built with sourceCompatibility 8; 0.1.0 targeted Java 11) |
| **Platforms** | any JVM |
| **Thread safety** | Not documented. After build() the filter is immutable (final fields, read-only query path), so concurrent mightContain calls appear safe; build() uses only local state. |
| **Drop-in for the baseline** | partial — same Guava Funnel and mightContain/Predicate query API as Guava BloomFilter, but built once from a full Collection (no put/putAll, no expectedInsertions or fpp knobs; FPR fixed by 8- or 16-bit fingerprints) with an incompatible serialized format |

## Gotchas

- writeTo/readFrom wrap the caller's stream in try-with-resources and close it. writeTo also emits one byte/short per call through DataOutputStream, so wrap file or socket streams in a BufferedOutputStream.
- build() on an empty collection throws ArrayIndexOutOfBoundsException, because HashedElements reports size 1 for zero keys. The peeling queue is a fixed n+1 ring buffer with no overflow check; in a Python port of the construction loop, sets under \~32 keys peeled on only \~20-50% of seeds vs \~95% for larger sets. Such sets need extra retries but still come out correct.
- The serialized bytes store strategy, seed and capacity but not the Funnel. readFrom must get the identical Funnel (including charset) or it silently returns false negatives. readFrom also trusts the header (strategy index, capacity), so untrusted bytes can throw or allocate up to 2^31 slots.
- The default build() seeds from ThreadLocalRandom, so identical inputs give different bytes; pass rngSeed for reproducible artifacts. The code relies on Guava APIs flagged unstable (the source suppresses UnstableApiUsage).

## Known shortcomings

- Ratios derived from JMH numbers vs Guava 28.2's BloomFilter at 16,384 elements only.
- Not on Maven Central (vendor source only). Build-once with all keys in memory plus \~35 B/key temp; an empty collection throws ArrayIndexOutOfBoundsException; writeTo/readFrom close the caller's stream and readFrom trusts the header. The benchmark filter held 8,192 keys (cache-resident, 50% hits, no JVM/CPU); the gain shrinks to 1.34x for strings. Abandoned 2020; FastFilter/fastfilter_java is the maintained alternative.

## Caveats and trade-offs

No JVM version, CPU model or JMH warmup/iteration/fork counts are documented; the build uses the plugin defaults. The \~1.97x/\~1.34x throughput and \~1.17x size ratios are derived from page data. At equal target FPR the xor8 vs Bloom (0.389%) size gain is modest (9.843 vs 11.551 bits/entry). The Bintray repository in the README is defunct. The project has been unmaintained since 2020.

Immutable filter (build once); needs Guava for the Funnels API; example dependency snippet references a defunct Bintray repo (library itself is on Maven Central).

## Maintenance

Abandoned since January 2020 (v0.1.1, zero issues ever filed); the Bintray-hosted artifact no longer resolves, but the MIT-licensed code is two small files that are easy to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README Benchmark tables match the record exactly (17,458.015 vs 8,879.024 q/ms for Long keys; 7,121.787 vs 5,318.409 for String keys; 123,042 vs 144,390 bytes). The JMH code (src/jmh/java/me/k11i/xorfilter/QueryBenchmark.java) confirms the baseline is Guava BloomFilter.create at fpp 0.00389 and 0.00002. No JVM, CPU or JMH settings are stated, so it is first-party C.
- **Verifier notes:** The numbers and baseline are verified. Metadata confirmed: MIT, last commit 2020-01-23 (abandoned), 20 stars, not archived, not a fork. The corrections only make the workload more precise and mark the ratios as derived.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/komiya-atsushi/xor-filter>
  - <https://github.com/komiya-atsushi/xor-filter#benchmark>
  - <https://raw.githubusercontent.com/komiya-atsushi/xor-filter/develop/src/jmh/java/me/k11i/xorfilter/QueryBenchmark.java>
  - <https://raw.githubusercontent.com/komiya-atsushi/xor-filter/develop/build.gradle>
- **Sources the enricher read:**
  - <https://github.com/komiya-atsushi/xor-filter>
  - <https://github.com/komiya-atsushi/xor-filter#benchmark>
  - <https://github.com/komiya-atsushi/xor-filter/blob/develop/CHANGELOG.md>
  - <https://github.com/komiya-atsushi/xor-filter/blob/develop/build.gradle>
  - <https://github.com/komiya-atsushi/xor-filter/blob/develop/gradle.properties>
  - <https://github.com/komiya-atsushi/xor-filter/blob/develop/.circleci/config.yml>
  - <https://github.com/komiya-atsushi/xor-filter/blob/develop/src/main/java/me/k11i/xorfilter/XorFilter.java>
  - <https://github.com/komiya-atsushi/xor-filter/blob/develop/src/main/java/me/k11i/xorfilter/MurmurHashFinalizer.java>
  - <https://raw.githubusercontent.com/komiya-atsushi/xor-filter/develop/src/test/java/me/k11i/xorfilter/XorFilterTest.java>
  - <https://raw.githubusercontent.com/komiya-atsushi/xor-filter/develop/src/jmh/java/me/k11i/xorfilter/QueryBenchmark.java>
  - <https://raw.githubusercontent.com/komiya-atsushi/xor-filter/develop/src/jmh/java/me/k11i/xorfilter/FppAndSerializationSize.java>
  - <https://github.com/komiya-atsushi/xor-filter/pulls?q=is%3Apr>
  - <https://repo1.maven.org/maven2/me/k11i/xor-filter/>
  - <https://repo1.maven.org/maven2/me/k11i/>
  - <https://search.maven.org/solrsearch/select?q=g:me.k11i&rows=20&wt=json>
  - <https://jcenter.bintray.com/me/k11i/xor-filter/0.1.1/xor-filter-0.1.1.pom>
  - <https://dl.bintray.com/komiya-atsushi/maven/>
  - <https://raw.githubusercontent.com/google/guava/v28.2/guava/src/com/google/common/hash/BloomFilterStrategies.java>
  - <https://arxiv.org/abs/1912.08258>
  - <https://github.com/FastFilter/fastfilter_java>
  - <https://raw.githubusercontent.com/FastFilter/fastfilter_java/master/README.md>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/komiya-atsushi/xor-filter`) · [data/wave6/enrich/raw/github_com_komiya_atsushi_xor_filter.json](../../../data/wave6/enrich/raw/github_com_komiya_atsushi_xor_filter.json) (enrichment confidence 0.8)

</details>
