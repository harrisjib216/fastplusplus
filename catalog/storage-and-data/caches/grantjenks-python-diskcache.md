# python-diskcache

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Caches](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Python` · `Apache-2.0` · 🟡 stale

> Pure-Python, SQLite-backed persistent cache that runs in-process and beats localhost Memcached/Redis on read latency, not writes.

| | |
|---|---|
| **Beats** | Memcached (pylibmc client) and Redis (redis.StrictRedis) |
| **Claimed result** | Single process (100k ops): diskcache.Cache get median 12.159us vs pylibmc.Client 25.988us vs redis.StrictRedis 44.107us, i.e. \~2.1x and \~3.6x lower median get latency (derived from page data). Concurrent (8 processes): diskcache.Cache total get time 12.349s vs pylibmc 61.824s vs redis 101.197s. The page says DiskCache 90th-percentile gets are 'less than half the latency of Memcached' (P90 23.127us vs 107.050us). Writes are slower: single-process set median is 68.903us vs 27.895us for pylibmc. Under 8-way concurrency, plain Cache's overall total (157.888s) is worse than pylibmc's (68.788s). Only FanoutCache(shards=8) beats Memcached overall, at 58.991s. |
| **Workload** | 100,000 get/set/delete ops (10:1 gets:sets, 10:1 sets:deletes) against a local Memcached (pylibmc) and Redis (redis.StrictRedis) server, single-process and 8-worker concurrent variants, short byte-string keys/values. |
| **Metric** | latency |
| **Adoption** | 2.9k stars |
| **Last commit** | 2024-03-03 |
| **Links** | [repository](https://github.com/grantjenks/python-diskcache) · [benchmark](https://github.com/grantjenks/python-diskcache/blob/master/docs/cache-benchmarks.rst) |

## Verdict

The author's tests/benchmark_core.py runs 100k ops per process (90% get, 9% set, 1% delete) over only 100 keys with values of a few hundred bytes, so the whole working set stays hot in SQLite's page cache. It pits DiskCache in-process against pylibmc and redis-py talking to default-configured localhost servers. Single-process median get was 12.2 us vs 26.0 us (Memcached) and 44.1 us (Redis), and median set was 68.9 us vs 27.9 us. With 8 processes, only FanoutCache(8 shards) beat Memcached overall (59.0 s vs 68.8 s total); plain Cache took 157.9 s. The page gives no CPU, OS, Python, SQLite, Memcached or Redis versions, its tables date from 2017, and the committed tests/timings_core_p1.txt comes from a different run (19.1 us get median).

## Use it when

- A Python app on a single host (web workers, CLI tools, data pipelines) that needs a cache shared between its processes and kept across restarts, without running Memcached or Redis.
- Read-dominated traffic (around 90% gets) with small keys and values, where in-process gets beat a localhost Memcached round trip (median 12.2 us vs 26.0 us in the author's benchmark).
- Caches larger than RAM: gigabytes on local disk, with large values written to files and readable as file handles (`read=True`).
- Memoizing expensive function results across runs (`memoize`, `memoize_stampede` for cache-stampede protection).
- Django sites that want a replacement for the built-in file-based cache, via `DjangoCache`.

## Skip it when

- Write-heavy traffic, or many writers on one unsharded `Cache`: writers take turns on SQLite's write lock. With 8 processes, set P99 was 21.3 ms and the max 1.85 s, against a 312 us max for Memcached. Single-process sets are also about 2.5x slower than Memcached (68.9 us vs 27.9 us median).
- Caches shared between machines: there is no network interface, and SQLite is not recommended on NFS. The docs also report poor performance on PythonAnywhere and problems in Parallels shared folders.
- Cache directories writable by less-trusted code: the default Disk unpickles values on read. CVE-2025-69872 / GHSA-w8v5-vhqr-4h9v (medium) covers all versions up to 5.6.3 with no patched release. Use JSONDisk or lock down the directory.
- LRU/LFU eviction or statistics: these turn every get into a write transaction, which gives up the fast read path the benchmark measured. The benchmark ran the default least-recently-stored policy.
- asyncio code (no native async; wrap calls in a thread executor), or many threads under a tight memory budget: each thread opens its own SQLite connection and mmap. In issue #293, 10 threads peaked at 2.15 GB RSS against 0.13 GB for one thread.

## How it is fast

Gets skip the network round trip: the cache is an embedded SQLite database queried in-process, while the Memcached and Redis baselines go through a localhost socket. SQLite runs in write-ahead-log (WAL) mode so reads and writes don't block each other, with a 64 MB mmap and an 8,192-page page cache. Values under 32 KB are stored inline and larger ones in separate files, and SQLite triggers keep count and size so nothing needs a scan. Under the default least-recently-stored eviction policy a get is one indexed SELECT with no transaction and no write. FanoutCache hashes keys (adler32) across N SQLite files, so concurrent writers compete for N write locks instead of one.

## Compared with alternatives

Pick DiskCache over server caches like Pogocache, Valkey or Dragonfly when the cache lives on one machine inside a Python app and you want persistence and no server to run. Those siblings win when the cache must be shared across hosts or has to absorb heavy concurrent writes.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none (uses only the standard-library sqlite3 module) |
| **Minimum toolchain** | Python 3 (setup.py python_requires '&gt;=3'); CI tests CPython 3.8-3.11; current release 5.6.3 |
| **Platforms** | any platform with Python's sqlite3 on a local filesystem; CI runs on Linux, macOS and Windows; not NFS |
| **Thread safety** | Thread-safe and process-safe: one SQLite connection per thread (threading.local), reopened after fork. Readers don't block writers, but writers block other writers on the same shard. |
| **Drop-in for the baseline** | partial: the get/set/add/incr/delete/touch-with-expiry API resembles a memcached client and DjangoCache swaps into Django's cache settings, but there is no Memcached/Redis protocol and no cross-host sharing, so client code must change |

## Gotchas

- FanoutCache's default timeout is 10 ms, and set/delete swallow the Timeout and return False, so writes can fail silently (39 of 71,530 sets were dropped in the 8-process benchmark). A plain `Cache` raises Timeout instead, with a 60 s default.
- Keys are matched by their serialized bytes, not by __hash__/__eq__. Pickled container keys such as tuples can serialize differently when equal (issue #54), and 1 and 1.0 count as the same key. Use JSONDisk for consistent keys.
- In FanoutCache, size_limit (default 1 GB) is split evenly across shards, and an item larger than one shard's share is culled immediately. Culling is lazy (at most cull_limit=10 keys per write), so the cache can briefly exceed its limit.
- Open bug #325: on macOS, forking after opening two `Cache` objects on the same directory gives sqlite3 'disk I/O error'. A full disk raises sqlite3.OperationalError on any write, but reads keep working.

## Known shortcomings

- Sets are \~2.5x slower than Memcached, and the plain Cache loses overall at 8 workers (157.9 s vs 68.8 s); only FanoutCache with 8 shards wins. No CPU stated.
- SECURITY: CVE-2025-69872 / GHSA-w8v5-vhqr-4h9v - the default Disk unpickles stored values, so anyone who can write the cache directory can execute code; affects &lt;=5.6.3 with no patched release and no fix timeline from the maintainer (2026-07). Use a non-pickle Disk or trusted directories only.
- The benchmark uses only 100 keys, so the working set stays hot in SQLite's page cache and the GET win is mostly avoiding a localhost socket. Writes are slower (set 68.9 us vs 27.9 us for Memcached; unsharded Cache at 8 processes has set P99 21 ms, max 1.85 s). FanoutCache's 10 ms timeout makes set/delete fail silently; LRU/LFU/stats turn every get into a write; no async, no NFS; macOS fork bug #325 open. Stale since 2024-03 (last release 5.6.3, 2023-08).

## Caveats and trade-offs

First-party benchmark (tests/benchmark_core.py). The page gives no CPU, OS, Python or Memcached/Redis versions, and its tables date from a 2017-12-15 docs update. Memcached and Redis are reached over the localhost network while DiskCache runs in-process on SQLite, so much of the get-latency win comes from avoiding IPC. Sets and deletes are 2-3x slower than Memcached. The author says to take the data 'with a grain of salt'.

Disk-backed (SQLite-based), so writes hit disk I/O; single Cache without sharding shows very high tail store/delete latency under concurrency (multi-second max), mitigated by FanoutCache sharding. Persistent by default unlike in-memory Redis/Memcached.

## Maintenance

Stale: last commit 2024-03-03 and last release 5.6.3 (2023-08-31), with 85 open issues. In July 2026 the maintainer declined to commit to a fix or timeline for the pickle CVE. It is Apache-2.0, pure Python and dependency-free, so it is easy to vendor or fork.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party benchmark page with public code (tests/benchmark_core.py; raw output in tests/timings_core_p1.txt and timings_core_p8.txt) and a documented workload. It gives no CPU model, OS, Python version or server versions, so it stays at C.
- **Verifier notes:** The record's numbers match the page (rounded). I added derived-ratio markers and the slower-writes caveat. I also fixed the caveat that claimed the page 'states' hardware is not given: the page is simply silent on it. The committed tests/timings_core_p1.txt comes from a different run than the one the docs page shows (get median 19.073us). License Apache-2.0 (gh reports NOASSERTION, but LICENSE holds the Apache 2.0 notice); 2,908 stars; last commit 2024-03-03 (stale).
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/grantjenks/python-diskcache>
  - <https://github.com/grantjenks/python-diskcache/blob/master/docs/cache-benchmarks.rst>
  - <https://raw.githubusercontent.com/grantjenks/python-diskcache/master/docs/cache-benchmarks.rst>
  - <https://raw.githubusercontent.com/grantjenks/python-diskcache/master/LICENSE>
  - <https://raw.githubusercontent.com/grantjenks/python-diskcache/master/README.rst>
  - <https://raw.githubusercontent.com/grantjenks/python-diskcache/master/tests/timings_core_p1.txt>
  - <https://raw.githubusercontent.com/grantjenks/python-diskcache/master/tests/benchmark_core.py>
- **Sources the enricher read:**
  - <https://github.com/grantjenks/python-diskcache>
  - <https://github.com/grantjenks/python-diskcache/blob/master/README.rst>
  - <https://github.com/grantjenks/python-diskcache/blob/master/docs/cache-benchmarks.rst>
  - <https://github.com/grantjenks/python-diskcache/blob/master/docs/tutorial.rst>
  - <https://github.com/grantjenks/python-diskcache/blob/master/diskcache/core.py>
  - <https://github.com/grantjenks/python-diskcache/blob/master/diskcache/fanout.py>
  - <https://github.com/grantjenks/python-diskcache/blob/master/diskcache/__init__.py>
  - <https://github.com/grantjenks/python-diskcache/blob/master/setup.py>
  - <https://github.com/grantjenks/python-diskcache/blob/master/requirements.txt>
  - <https://github.com/grantjenks/python-diskcache/blob/master/.github/workflows/integration.yml>
  - <https://github.com/grantjenks/python-diskcache/blob/master/tests/benchmark_core.py>
  - <https://github.com/grantjenks/python-diskcache/issues/357>
  - <https://github.com/grantjenks/python-diskcache/issues/360>
  - <https://github.com/grantjenks/python-diskcache/issues/362>
  - <https://github.com/grantjenks/python-diskcache/issues/325>
  - <https://github.com/grantjenks/python-diskcache/issues/293>
  - <https://github.com/grantjenks/python-diskcache/issues/266>
  - <https://github.com/grantjenks/python-diskcache/pull/364>
  - <https://github.com/advisories/GHSA-w8v5-vhqr-4h9v>
  - <https://pypi.org/pypi/diskcache/json>
  - <https://hn.algolia.com/api/v1/search?query=diskcache&tags=story>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/grantjenks/python-diskcache`) · [data/wave6/enrich/raw/github_com_grantjenks_python_diskcache.json](../../../data/wave6/enrich/raw/github_com_grantjenks_python_diskcache.json) (enrichment confidence 0.82)

</details>
