# Caches

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md)</sub>

**What these beat:** memcached, Redis, LRU baselines the benchmark names  
**40 entries:** 1 tier A · 17 tier B · 22 tier C · 0 tier D · 35 copyable, 5 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**go-sieve**](opencoff-go-sieve.md) | Fixed-capacity generic Go SIEVE cache whose mutex-free Get path out-scales hashicorp/golang-lru LRU/ARC under concurrent reads. | **A** | Go | BSD-2-Clause | 🟢 active |
| 2 | [**Garnet**](microsoft-garnet.md) | Multi-threaded Redis-protocol (RESP) cache-store in C# from Microsoft Research; up to \~100x Valkey/Redis throughput on many-core servers. | **B** | C# | MIT | 🟢 active |
| 3 | [**CacheLib**](facebook-cachelib.md) | Meta's in-process C++ caching engine with an optional SSD tier; the authors report up to 60% more throughput than Memcached. | **B** | C++ | Apache-2.0 | 🟢 active |
| 4 | [**quick-cache**](arthurprs-quick-cache.md) | Sharded concurrent Rust cache with S3-FIFO/CLOCK-Pro-style eviction; beats Mutex-guarded LRU mainly on hit ratio and thread scaling. | **B** | Rust | MIT | 🟢 active |
| 5 | [**GL-Cache**](paper-gl-cache.md) | Learned eviction (XGBoost over write-time object groups): higher hit ratio than LRU, slower than LRU, 228x faster than LRB. | **B** | C | Apache-2.0 | 🟢 active |
| 6 | [**S3-FIFO**](paper-s3-fifo.md) | SOSP'23 three-FIFO-queue eviction policy: lower miss ratios than LRU, and over 6x CacheLib LRU's throughput at 16 threads. | **B** | C | Apache-2.0 | 🟢 active |
| 7 | [**SIEVE**](paper-sieve.md) | Parameter-free FIFO-plus-moving-hand eviction policy that beats LRU on miss ratio and multi-thread throughput for web caches. | **B** | C | Apache-2.0 | 🟢 active |
| 8 | [**Pelikan / Segcache**](pelikan-io-pelikan.md) | Rust cache-server framework whose pelikan-segcache speaks memcached's text protocol over Segcache, a TTL-segmented store with 5-byte-per-item metadata. | **B** | Rust | Apache-2.0 | 🟢 active |
| 9 | [**RAMCloud**](platformlab-ramcloud.md) | Distributed, durable in-DRAM key-value store with kernel-bypass RPC; beats Redis 2.6 on read-heavy YCSB, not on writes. | **B** | C++ | ISC | 🔴 abandoned |
| 10 | [**MICA**](efficient-mica.md) | Research in-memory key-value cache/store over DPDK UDP; 65-77 Mops on tiny items per 16-core server, far above Memcached. | **B** | C | Apache-2.0 (license text… | 🔴 abandoned |
| 11 | [**MemC3**](efficient-memc3.md) | NSDI'13 research fork of Memcached 1.4.13: optimistic cuckoo hashing plus CLOCK eviction; \~3x read-heavy throughput, incomplete protocol. | **B** | C | BSD-3-Clause | 🔴 abandoned |
| 12 | [**RobinHood (tail-latency-aware cache repartitioning)**](dasebe-robinhoodcache.md) | Research controller that resizes per-backend memcached partitions by request-blocking count, cutting request P99 versus one shared cache. | **B** | Go | BSD-3-Clause | 🔴 abandoned |
| 13 | [**LRB (Learning Relaxed Belady) / webcachesim2**](sunnyszy-lrb.md) | ML (LightGBM) CDN cache-eviction policy approximating relaxed Belady; cuts simulated WAN traffic 4-25% vs Bloom-filter LRU. | **B** | C++ | BSD-2-Clause | 🔴 abandoned |
| 14 | [**AdaptSize**](dasebe-adaptsize.md) | Size-aware probabilistic admission for Varnish's memory cache; raises CDN object hit ratio 47-91% over stock LRU Varnish. | **B** | C | BSD-2-Clause | 🔴 abandoned |
| 15 | [**LHD (Least Hit Density) / RankCache**](cmu-corgi-lhd.md) | Trace-driven simulator for LHD, a size-aware eviction policy needing \~8x less cache than LRU for equal hit rate. | **B** | C++ | MIT (verbatim MIT text… | 🔴 abandoned |
| 16 | [**Hyperbolic Caching**](kantai-hyperbolic-caching.md) | Research Redis 3.0 fork plus simulator whose cost-aware 'hits over time-in-cache' eviction beats Redis's sampled LRU on miss rate. | **B** | C | MIT | 🔴 abandoned |
| 17 | [**Masstree**](kohler-masstree-beta.md) | Concurrent in-memory trie of B+-trees with ordered range scans; authors measured 1.5-3.7x Redis 2.4 throughput on 16 cores. | **B** | C++ | MIT plus two clauses taken… (study only) | 🟡 stale |
| 18 | [**Cacheus**](sylab-cacheus.md) | Research Python simulator of Cacheus (FAST'21), a learned two-expert page-cache eviction policy that competes with ARC/LIRS/DLIRS on hit rate. | **B** | Python | reference (no LICENSE file… (study only) | 🟡 stale |
| 19 | [**Valkey**](valkey-io-valkey.md) | BSD-licensed fork of Redis OSS 7.2 whose async I/O threads give \~37% more SET throughput than Redis 8.0. | **C** | C | BSD-3-Clause | 🟢 active |
| 20 | [**Caffeine**](ben-manes-caffeine.md) | Concurrent in-process JVM cache using W-TinyLFU and buffered policy updates; beats ConcurrentLinkedHashMap, Guava Cache and synchronized LinkedHashMap on multi-threaded… | **C** | Java | Apache-2.0 | 🟢 active |
| 21 | [**Ristretto**](dgraph-io-ristretto.md) | Concurrent in-process Go cache with TinyLFU admission and cost-based eviction; \~3x a mutex-wrapped groupcache LRU's throughput in its own benchmarks. | **C** | Go | Apache-2.0 | 🟢 active |
| 22 | [**otter**](maypok86-otter.md) | Caffeine-style concurrent Go cache (adaptive W-TinyLFU): 10-34x hashicorp/golang-lru throughput at 25-100% reads; slower on pure writes. | **C** | Go | Apache-2.0 | 🟢 active |
| 23 | [**Skytable**](skytable-skytable.md) | Multithreaded in-memory Rust NoSQL server with a SQL-like query language; one unaudited 2022 benchmark shows \~6x Redis GET/SET throughput. | **C** | Rust | AGPL-3.0 | 🟢 active |
| 24 | [**Pogocache**](tidwall-pogocache.md) | Multithreaded C cache server speaking RESP, memcache, HTTP and Postgres; about 2x Redis and 1.2-2.3x memcached throughput (author-run). | **C** | C | MIT | 🟢 active |
| 25 | [**Yac (PHP shared-memory object cache)**](laruence-yac.md) | PHP extension: lock-free shared-memory key/value cache for FPM workers on one host, replacing local Memcached/APCu without a network hop. | **C** | C | PHP-3.01 | 🟢 active |
| 26 | [**Ferrous**](igentai-ferrous.md) | AI-written Rust Redis/RESP2 server; self-reported 0-8% over Valkey 8.0.4 on single commands, \~2x slower pipelined SET. | **C** | Rust | MIT OR Apache-2.0 | 🟢 active |
| 27 | [**warp_cache**](toloco-warp-cache.md) | Rust/PyO3 memoization decorator for Python with SIEVE eviction, TTL, async and mmap cross-process backend; \~25x cachetools, slower than lru_cache. | **C** | Rust | MIT | 🟢 active |
| 28 | [**RapidKV**](shashank2602-rapidkv.md) | Single-threaded C++20 RESP server with 13 string commands; ties Redis unpipelined, 1.45-4.2x faster when pipelined. | **C** | C++ | MIT | 🟢 active |
| 29 | [**KeyDB**](snapchat-keydb.md) | Multithreaded C++ Redis 6.2 fork serving one keyspace from many event-loop threads; claims \~7x Redis 6 throughput under TLS. | **C** | C++ | BSD-3-Clause | 🟡 stale |
| 30 | [**python-diskcache**](grantjenks-python-diskcache.md) | Pure-Python, SQLite-backed persistent cache that runs in-process and beats localhost Memcached/Redis on read latency, not writes. | **C** | Python | Apache-2.0 | 🟡 stale |
| 31 | [**cachegrand**](danielealbano-cachegrand.md) | Multi-threaded C key-value server speaking the Redis protocol (string commands only); out-scales single-threaded Redis on many-core Linux. | **C** | C | BSD-3-Clause | 🟡 stale |
| 32 | [**IKV (Inlined Key-Value Store)**](inlinedio-ikv-store.md) | Embedded, eventually consistent Rust key-value store for ML features that serves reads in-process instead of calling a remote Redis. | **C** | Rust | MIT | 🟡 stale |
| 33 | [**golang-fifo**](scalalang2-golang-fifo.md) | Go generic in-process cache implementing SIEVE and S3-FIFO eviction; about 16-18% fewer misses than hashicorp LRU, but no higher ops/sec. | **C** | Go | MIT | 🟡 stale |
| 34 | [**mrcache**](markreedz-mrcache.md) | Single-threaded io_uring key-value cache server in C; README claims 7x Redis and 46x memcached GET throughput at 16 B. | **C** | C | MIT | 🟡 stale |
| 35 | [**Varnish Cache**](varnishcache-varnish-cache.md) | Multi-threaded HTTP reverse-proxy cache programmed in VCL; beats a single-worker nginx proxy_cache but not nginx on all cores. | **C** | C | BSD-2-Clause | ⚪ unknown |
| 36 | [**Cachelot**](cachelot-cachelot.md) | Single-threaded C++ LRU cache library plus a memcached-text-protocol server that fits 7-16% more data than Memcached in the same RAM. | **C** | C++ | BSD-2-Clause | 🔴 abandoned |
| 37 | [**Vettel**](japrozs-vettel.md) | A \~300-line C CLI key-value store on one flat text file; its README times it slightly faster than redis-cli. | **C** | C | MIT | 🔴 abandoned |
| 38 | [**Dragonfly**](dragonflydb-dragonfly.md) | Multi-threaded, shared-nothing in-memory store that speaks the Redis and Memcached protocols; beats single-process Redis once there are many cores. | **C** | C++ | BUSL-1.1 (study only) | 🟢 active |
| 39 | [**EloqKV**](eloqdata-eloqkv.md) | Multi-threaded Redis-API distributed KV database with ACID transactions; vendor benchmark shows about 4.5-8.5x single-threaded Redis throughput. | **C** | C++ | GPL-2.0-only OR… (study only) | 🟢 active |
| 40 | [**W-TinyLFU (C++ header-only, based on the TinyLFU paper)**](vimpunk-w-tinylfu.md) | Small C++ header-only W-TinyLFU cache: frequency-sketch admission in front of segmented LRU, for higher hit ratios than plain LRU. | **C** | C++ | reference (no LICENSE file… (study only) | 🔴 abandoned |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
