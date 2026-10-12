# warp_cache

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Caches](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟢 active

> Rust/PyO3 memoization decorator for Python with SIEVE eviction, TTL, async and mmap cross-process backend; \~25x cachetools, slower than lru_cache.

| | |
|---|---|
| **Beats** | cachetools (Python LRU/TTL cache library) |
| **Claimed result** | Single-threaded, cache size 256: 20.4M ops/s vs cachetools 826K, about 24.7x (derived from page data; docs/performance.md lists 19.1-27.0x across cache sizes 32-1024). Multi-threaded with the GIL enabled, 16 threads: 19.5M vs cachetools+Lock 795K, about 24.5x (derived from page data). About 1.6x faster than functools.lru_cache+Lock in multi-threaded runs. Plain functools.lru_cache is about 1.5x faster than warp_cache single-threaded (31.0M vs 20.4M ops/s). |
| **Workload** | Python @cache() decorator hit/miss throughput (ops/s) on Zipf-distributed keys (2000 unique), cache size 256, median of 3 rounds, CPython 3.13.2. Single-threaded vs lru_cache/cachetools/cachebox/moka_py; multi-threaded (GIL-enabled, 1-32 threads) vs lru_cache+Lock and cachetools+Lock. |
| **Metric** | throughput |
| **Hardware** | Apple M-series (arm64), exact chip model not stated |
| **Compiler and flags** | Rust release profile lto="fat", codegen-units=1 (Cargo.toml); CPython 3.13.2 built with Clang 20.1.0 (docs/performance.md); rustc version unstated |
| **Adoption** | 9 stars |
| **Last commit** | 2026-06-18 |
| **Links** | [repository](https://github.com/toloco/warp_cache) · [benchmark](https://github.com/toloco/warp_cache/blob/master/README.md) |

## Verdict

These are first-party numbers from the repo's runner. The workload is 100K calls of an identity function over Zipf keys (2000 unique, \~71% hit rate at 256 entries), median of 3, on CPython 3.13.2 (Clang 20.1.0) on an unspecified Apple M-series Mac with cachetools 7.0.1. warp_cache did 20.4M calls/s against cachetools.func.lru_cache's 826K (\~24.7x; 19.1-27.0x across 32-1024 entries), while stdlib functools.lru_cache did 31.0M. With 16 GIL-bound threads warp_cache did 19.5M, against 795K for cachetools with an added threading.Lock and 11.9M for lru_cache plus a Lock. cachetools.func already locks internally with a Condition, and lru_cache is documented thread-safe, so both threaded baselines pay for a lock they do not need. Plain lru_cache under threads was not measured.

## Use it when

- Hot memoized functions called from thread pools or web-server threads on standard GIL CPython when you also want TTL or async in the same decorator. The author measured \~20M calls/s at 256 entries, against 0.8M for cachetools.func.lru_cache.
- Replacing cachetools.func.lru_cache or ttl_cache decorators on hot paths. The author measured 19-27x more calls/s at 32-1024 entries, and 12-14x more than cachetools ttl_cache in the TTL loop (7.2-7.4M vs 0.52-0.60M).
- Async functions. A cache hit returns without awaiting the coroutine, and concurrent misses on the same key are coalesced within each event loop.
- Gunicorn or Celery workers on Linux or macOS that should share small results through mmap: keys up to 512 B and values up to 4 KB by default, primitives preferred. The author measured 5.0M ops/s in one process and 8.1M total with 4 processes.
- Skewed or scan-heavy key streams where hit ratio matters more than call overhead. The author's Zipf tests show SIEVE with 15-22% fewer misses than LRU at the same size.

## Skip it when

- Plain memoization where you would otherwise use functools.lru_cache. The stdlib C cache is 1.3-1.8x faster single-threaded (31.0M vs 20.4M ops/s at 256 entries), and the CPython docs say it is already thread-safe (coherent under concurrent updates), so the repo's 'lru_cache + Lock' comparison adds a lock you do not need.
- Free-threaded CPython. PyPI 0.7.0 ships no cp313t or cp314t wheels. The only published no-GIL results are from February 2026, before the current sharded store, and show total throughput falling from 15.1M ops/s at 1 thread to 3.0-4.2M at 8-32 threads. There is no newer data.
- Code that needs features warp_cache lacks. Instance methods do not bind (open issue #52). There is no unbounded mode (max_size must be an int), no `typed=` flag, no custom key function, no dict-like cache object, no per-entry TTL, no stampede protection on sync calls, and no size-in-bytes eviction (#15 open). cachetools, cachebox or moka-py cover these.
- Shared backend where a process can be SIGKILLed or OOM-killed mid-write. The cross-process TTAS spinlock has no owner-death recovery (#38 open), so every process hangs until the shm file is deleted. The shared backend is also unavailable on Windows and unsafe across trust boundaries, because complex types round-trip through pickle (#46, #50 open).
- Production code that needs a stable release. The project has 9 stars and a Beta classifier, and the June 2026 memory-safety and concurrency fixes (#30, #31, #37, #39, #40) are on master but not in any PyPI release.

## How it is fast

The whole hit path runs inside one PyO3 `tp_call`. It hashes the args tuple with `PyObject_Hash` and picks a shard with `hash & mask`. It probes a hashbrown table through a passthrough hasher that reuses Python's hash, using a borrowed-key `Equivalent` lookup so a hit allocates no key. It compares keys with `PyObject_RichCompareBool` and returns the value. On GIL builds the per-shard lock is `GilCell`, an `UnsafeCell` wrapper that does no locking because the GIL already serializes access; free-threaded builds compile in a parking_lot `RwLock` per shard instead. SIEVE eviction (NSDI'24) reduces a hit to one relaxed atomic store of a visited bit, with no LRU list relinking. The release build uses fat LTO and codegen-units=1. Most of the gap to cachetools is simply native code against a pure-Python wrapper plus a Condition lock.

## Compared with alternatives

python-diskcache is the only other Python sibling. Pick warp_cache for in-memory memoization where per-call overhead matters, or for small primitive results shared among local workers through mmap. Pick diskcache for large or persistent values, bytes-bounded eviction, or when a crashed worker must not wedge the cache. The SIEVE and quick-cache entries are the underlying algorithm and a native Rust cache; warp_cache matters only when the caller is Python.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | No Python runtime dependencies. Rust crates: pyo3 0.29, parking_lot 0.12 and hashbrown 0.15, plus memmap2, libc and ahash on non-Windows. Source builds need a Rust toolchain and maturin. |
| **Minimum toolchain** | CPython 3.10+ on master (PyPI 0.7.0 declares &gt;=3.9); Rust edition 2021, minimum rustc not documented |
| **Platforms** | PyPI 0.7.0 wheels: manylinux2014 x86_64/aarch64, macOS x86_64/arm64 and Windows x86_64 for CPython 3.9-3.14. No musllinux and no free-threaded wheels. The shared backend is POSIX-only and raises RuntimeError on Windows. |
| **Thread safety** | The memory backend is safe to call from many threads without extra locking. On GIL builds it relies on the GIL (GilCell); free-threaded builds use a per-shard parking_lot RwLock. Concurrent sync misses on one key may each run the function; the async wrapper coalesces misses per event loop. The shared backend uses a seqlock (lock-free reads) plus a TTAS write spinlock. |
| **Drop-in for the baseline** | partial — `@cache(max_size=N)` replaces `cachetools.func.lru_cache(maxsize=N)` or `ttl_cache` on module-level functions. Missing: `typed`, `maxsize=None`, `cache_parameters()`, `cachetools.cached(cache, key=...)`-style custom caches and keys, and LFU/RR/FIFO policies. Methods do not bind, and CacheInfo fields are named `max_size`/`current_size`. |

## Gotchas

- The latest PyPI release, 0.7.0 (2026-04-13), predates the June 2026 fixes. Those include unsound GilCell aliasing under reentrant `__eq__` (#30, critical), an out-of-bounds slab write with shared max_size=0 (#31), a data race on the lock-free read path (#37), and world-readable shm files holding pickled data (#39). Pin to master if you need them.
- Shared-backend files are named from the function's `__module__` and `__qualname__` and persist across restarts. On reopen they are reused whenever version, capacity, key/value size limits and TTL match. A redeploy with changed function logic can therefore serve stale results, and closures that share a qualname share one cache. Keys or values over the size limits are silently not cached; watch `oversize_skips`.
- max_size is split across up to 16 shards, each running its own SIEVE with ceil(max_size/shards) slots. Capacity is therefore approximate (max_size=100 gives 16x7=112 slots) and eviction is per shard. Also, eviction removes from a VecDeque at the hand position, which from reading the code is linear in shard size, not the O(1) the docs claim. max_size=0 still caches one entry on the memory backend (#47).
- Keys follow Python equality with no `typed` option, so f(1), f(1.0) and f(True) share one entry. Keyword arguments are sorted, so f(a=1, b=2) and f(b=2, a=1) hit the same entry, unlike lru_cache. Expired TTL entries are only dropped lazily and keep their values alive until they are evicted or overwritten. Negative or NaN TTL can panic on the memory backend (#86 open).

## Known shortcomings

- The \~24.5x at 16 threads is vs cachetools with a Lock; single-threaded, the stdlib lru_cache is 1.5x faster.
- The baselines are artificially slow: lru_cache is already thread-safe (the '+Lock' adds an unneeded lock) and cachetools.func.lru_cache already locks, so 'cachetools+Lock' is double-locked; single-threaded, lru_cache is 1.3-1.8x faster. SECURITY: PyPI 0.7.0 (2026-04) predates June fixes for UB (#30), out-of-bounds (#31), a race (#37) and world-readable pickled shared memory (#39).
- No free-threaded (cp313t) wheels and throughput falls from 15.1M at 1 thread to 3-4M at 8-32 threads without the GIL. Open bugs: methods do not bind (#52), the shm spinlock wedges if its holder dies (#38), max_size=0 caches one item (#47), a bad TTL can panic (#86). The shm name persists across restarts (stale results after redeploy); shards make max_size approximate; eviction is linear. First-party only on an unnamed M-series chip with \~5 ms runs.

## Caveats and trade-offs

First-party benchmark in the project's own repo, not independently reproduced. The CPU is given only as 'Apple M-series', with no exact model. The stdlib incumbent functools.lru_cache beats warp_cache by about 1.5x single-threaded. warp_cache only wins against lru_cache when a threading.Lock is added (about 1.6x). The \~25x wins are against pure-Python cachetools.

Single-threaded functools.lru_cache (pure C, no FFI) is itself \~1.5x faster than warp_cache; warp_cache's win only materializes once thread-safety is required; adds a Rust/PyO3 build dependency

## Maintenance

Actively maintained (last master commit 2026-06-18, a batch of memory-safety and concurrency fixes), MIT-licensed and pip-installable from prebuilt wheels. The newest PyPI release (0.7.0, April 2026) lacks those fixes, and the project is small (9 stars, Beta).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification C, tier now C.
- **Tier reason:** The README and docs/performance.md give first-party ops/s against cachetools and functools.lru_cache, and the benchmark code is public (benchmarks/bench_all.sh, benchmarks/_bench_runner.py). Hardware is given only as 'Apple M-series (arm64)' with no chip model, so it cannot be A.
- **Verifier notes:** The record's '\~26x at 16 threads' is overstated: the page shows 19.5M vs 795K, about 24.5x, and that baseline is cachetools+Lock. The record also left out that stdlib lru_cache is faster single-threaded. The original benchmark_url (/blob/main/) returns 404 because the default branch is master. The last commit on master is 2026-06-18; the record's 2026-08-19 is a push to the non-default branch refactor/benchmark-workflow. The project is still active and the MIT license is confirmed.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `compiler_and_flags`, `last_commit`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/toloco/warp_cache>
  - <https://github.com/toloco/warp_cache/blob/main/README.md>
  - <https://raw.githubusercontent.com/toloco/warp_cache/master/README.md>
  - <https://raw.githubusercontent.com/toloco/warp_cache/master/docs/performance.md>
  - <https://raw.githubusercontent.com/toloco/warp_cache/master/Cargo.toml>
  - <https://raw.githubusercontent.com/toloco/warp_cache/master/benchmarks/results/bench_py3.13.json>
  - <https://raw.githubusercontent.com/toloco/warp_cache/master/benchmarks/results/bench_default.json>
- **Sources the enricher read:**
  - <https://github.com/toloco/warp_cache>
  - <https://github.com/toloco/warp_cache/blob/master/README.md>
  - <https://github.com/toloco/warp_cache/blob/master/docs/performance.md>
  - <https://github.com/toloco/warp_cache/blob/master/docs/ARCHITECTURE.md>
  - <https://github.com/toloco/warp_cache/blob/master/docs/usage.md>
  - <https://github.com/toloco/warp_cache/blob/master/docs/alternatives.md>
  - <https://github.com/toloco/warp_cache/blob/master/benchmarks/COMPARISON.md>
  - <https://github.com/toloco/warp_cache/blob/master/benchmarks/_bench_runner.py>
  - <https://github.com/toloco/warp_cache/blob/master/benchmarks/results/bench_py3132t_nogil.json>
  - <https://github.com/toloco/warp_cache/blob/master/benchmarks/results/bench_py3.13t.json>
  - <https://github.com/toloco/warp_cache/blob/master/Cargo.toml>
  - <https://github.com/toloco/warp_cache/blob/master/pyproject.toml>
  - <https://github.com/toloco/warp_cache/blob/master/src/lib.rs>
  - <https://github.com/toloco/warp_cache/blob/master/src/store.rs>
  - <https://github.com/toloco/warp_cache/blob/master/src/entry.rs>
  - <https://github.com/toloco/warp_cache/blob/master/src/shared_store.rs>
  - <https://github.com/toloco/warp_cache/blob/master/src/shm/hashtable.rs>
  - <https://github.com/toloco/warp_cache/blob/master/warp_cache/_decorator.py>
  - <https://github.com/toloco/warp_cache/blob/master/warp_cache/__init__.py>
  - <https://github.com/toloco/warp_cache/issues>
  - <https://github.com/toloco/warp_cache/issues/52>
  - <https://github.com/toloco/warp_cache/issues/38>
  - <https://github.com/toloco/warp_cache/issues/47>
  - <https://github.com/toloco/warp_cache/issues/46>
  - <https://github.com/toloco/warp_cache/issues/86>
  - <https://github.com/toloco/warp_cache/releases>
  - <https://github.com/toloco/warp_cache/commits/master>
  - <https://github.com/tkem/cachetools/blob/master/src/cachetools/func.py>
  - <https://github.com/tkem/cachetools/blob/v7.0.1/src/cachetools/func.py>
  - <https://docs.python.org/3/library/functools.html>
  - <https://pypi.org/pypi/warp_cache/json>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/toloco/warp_cache`) · [data/wave6/enrich/raw/github_com_toloco_warp_cache.json](../../../data/wave6/enrich/raw/github_com_toloco_warp_cache.json) (enrichment confidence 0.8)

</details>
