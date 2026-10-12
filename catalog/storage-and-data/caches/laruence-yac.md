# Yac (PHP shared-memory object cache)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Caches](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `PHP-3.01` · 🟢 active

> PHP extension: lock-free shared-memory key/value cache for FPM workers on one host, replacing local Memcached/APCu without a network hop.

| | |
|---|---|
| **Beats** | Memcached |
| **Claimed result** | +18.6% to +20.1% RPS (141.6 vs 118.7 at c=20, 140.6 vs 118.5 at c=50, 142.1 vs 118.4 at c=100) and \~16-17% lower p50 latency (e.g. 699ms vs 840ms at c=100; derived from page data, the README summarizes it as \~15%); cross-checked with a fixed-count run (ab -n 10000 -c 100): 141.8 vs 120.6 RPS, +17.6% |
| **Workload** | Full WordPress homepage renders under `ab -t 30 -c <concurrency>` at 20/50/100 concurrent users on the author's live site (laruence.com), PHP 8.1 FPM, 8 cores. Each run starts from a flushed cache, a restarted php-fpm and a 500-request warmup, and only the object-cache drop-in differs (Yac vs the classic Memcached drop-in on localhost:11211). |
| **Metric** | throughput |
| **Hardware** | 8-core / 31 GB server running PHP 8.1 FPM behind Nginx (per docs/blog-yac-object-cache.md); exact CPU model not stated |
| **Adoption** | 833 stars (yac core extension); 5 stars (wp-yac-cache WordPress plugin) |
| **Last commit** | 2026-09-24 |
| **Links** | [repository](https://github.com/laruence/yac) · [benchmark](https://github.com/laruence/wp-yac-cache/blob/master/README.md) |

## Verdict

On the author's WordPress site (laruence.com; an 8-core/31 GB server running PHP 8.1 FPM behind Nginx; CPU model and compiler flags not stated), swapping the Memcached object-cache drop-in (memcached on localhost:11211) for the Yac drop-in raised full-homepage throughput from about 118.5 to about 141.5 RPS (+18.6% to +20.1%). It also cut p50 latency by about 16-17% at 20, 50 and 100 concurrent ab clients, with both setups capped by PHP rendering and MySQL; a fixed 10,000-request run gave +17.6%. Yac's own microbenchmark (16 forked workers, 100:1 read:write, Apple M5 Pro, PHP 8.5) reports 170-727x more aggregate ops/s than per-worker TCP connections to a local memcached 1.6.45, which mostly measures the removed loopback round trip rather than cache mechanics.

## Use it when

- A single PHP-FPM host, or a few independent ones, where Memcached or Redis on localhost serves only as a same-machine cache: the WordPress object cache, config, routing tables, rendered fragments.
- Requests that do dozens to hundreds of cache gets each, where localhost TCP round trips per get add up. This is the WordPress case: about 19% more RPS even though the ceiling is set by PHP and MySQL.
- Read-heavy access (the project's own benchmark uses 100:1 read:write) with many small values. Ints, bools, null and strings of 7 bytes or less live in the slot and skip value allocation entirely.
- You would rather not run, secure and monitor a cache daemon, and losing the cache on every php-fpm restart is acceptable.
- PHP 7.0-8.5 on Linux x86-64/ARM64 or Windows (both covered by CI), in NTS or ZTS builds.

## Skip it when

- Several web nodes that must see each other's writes or invalidations. Each host's segment is private, so a delete or flush on one node never reaches the others.
- Sharing between unrelated processes such as cron jobs, standalone CLI scripts or a second FPM master. Only the process that created the segment and its forked children can attach to it (issue #124), and CLI is disabled by default.
- Write-heavy or hot-key write workloads. set() returns false when it loses the slot CAS race, and the README says to avoid several processes setting the same key at once. The WordPress drop-in's incr/decr is a non-atomic get-then-set, so counters lose updates under concurrency.
- Keys over 48 bytes (PSR-16 requires 64, issue #83), values over 64 MB raw or 1 MB after compression, or incompressible values above the compression threshold, where set() fails if LZ4 would make them bigger.
- Risk-averse production that needs a long-settled engine. The storage layer was largely rewritten in Aug-Sep 2026 (2.4.0-2.4.2): 2.4.2 fixed a get() crash under concurrency and a flush() race that could leave a slot permanently unusable. In 2021 (issue #122) the author said the older partial-CRC Yac 'has a certain probability of error'.

## How it is fast

It removes the network: a get() is a MurmurHash64A lookup into a fixed power-of-two slot table in already-mapped memory. It probes at most 4 slots (home slot plus an odd stride) and copies the value out, with no socket, loopback TCP round trip or protocol encoding. Concurrency is lock-free. Each slot has a seqlock-style version counter: readers snapshot it and retry, and writers claim it with a CAS, giving up after 30 spins. Values sit in ring segments handed out by a CAS bump pointer. On every read a full CRC-32C check (SSE4.2 or ARMv8 hardware, detected at runtime) turns recycled or torn blocks into misses instead of taking a lock. Small scalars and strings up to 7 bytes are embedded in the slot's pointer word, and values that fit beside the key in the 48-byte key area are stored inline, so neither needs a value block. Values over 4K are LZ4-compressed by default.

## Compared with alternatives

Pick Yac when the application is PHP-FPM. It is the only catalogued Memcached-beater whose cache lives in memory shared across forked PHP workers; CacheLib (in-process C++) and python-diskcache (in-process Python) are the equivalents for other runtimes. Stay with a networked cache such as Memcached, Pogocache or Dragonfly when more than one host has to share entries or invalidations.

## Integration

| | |
|---|---|
| **Form** | shared lib (PHP extension yac.so/.dll, installed via PECL, PIE or phpize; the WordPress path adds the wp-yac-cache plugin, which deploys wp-content/object-cache.php) |
| **Dependencies** | none required (LZ4 is bundled, or a system LZ4 via --with-system-lz4); optional msgpack, igbinary or json serializers. The WordPress plugin needs PHP 7.2+ and WordPress 5.6+. |
| **Minimum toolchain** | PHP 7.0+ (package.xml; CI builds 7.0 through 8.5). A C compiler with the GCC/Clang __atomic/__sync builtins, or MSVC; configure fails otherwise. Needs mmap(MAP_ANON) or SysV shm. |
| **Platforms** | Linux x86-64 and ARM64 (CI, including a 30-second 16-worker concurrency hammer on both), Windows x64 and x86 (named file mapping), macOS (the author's benchmark machine, not in CI). Hardware CRC-32C is used when SSE4.2 or ARMv8 CRC is detected at runtime, with a slicing-by-8 software fallback otherwise. |
| **Thread safety** | Safe across processes and ZTS threads through lock-free per-slot version counters (seqlock-style) with CAS claims, a CAS bump allocator and CRC-32C validation on every read. Writes can fail under contention and return false, and the README advises retrying and avoiding concurrent writers on the same key. |
| **Drop-in for the baseline** | partial — it is neither wire- nor API-compatible with Memcached, so code must call the Yac class, whose add/set/get/delete-with-TTL semantics resemble memcached's. For WordPress, the wp-yac-cache drop-in replaces the Memcached object-cache drop-in with no code changes. However, wp_cache_flush_group only clears the request-local copy, and wp_cache_flush wipes the whole host's Yac memory. |

## Gotchas

- Yac::flush() (and so wp_cache_flush()) invalidates the entire shared segment on the host, across every prefix and every app attached to the same PHP master. delete() only writes a tombstone, and memory comes back only when the value ring wraps around.
- Without a default argument, get() returns false for both a miss and a stored false; pass a sentinel default (2.4.0+) to tell them apart. Since 2.4.0, multi-get omits missing keys instead of returning false placeholders, so code that reads \$result[\$key] directly can raise warnings. The WordPress drop-in writes a stored false as 0.
- In the WordPress drop-in, keys over the 48-byte budget have their key part replaced by a 32-bit crc32b hash and are not re-checked on read. Two long keys in the same group can therefore collide and silently return each other's value. A birthday estimate (derived, not documented) is about a 1% chance with \~10K live long keys in one group. Do not set yac.serializer=json for WordPress either: objects come back as arrays and cause fatal errors.
- Capacity is fixed at startup. keys_memory_size sets the slot count (8M is about 64K slots), and each key can only occupy its 4 probe slots, so live entries can be kicked long before the table fills. A value bigger than one 4M+ segment fails (the 'fails' counter goes up). Size both pools from info() hit, kick and recycle counters.

## Known shortcomings

- Per-host only (no cross-node sharing/invalidation) and shared only with forked children of the creating process (#124); CLI off by default. Writes are lossy under contention (set() returns false on a lost CAS) and the WordPress drop-in's incr/decr is non-atomic; 48 B key cap, and the drop-in hashes long keys to crc32b without a read-back check (silent collision risk). flush() wipes the whole host segment; capacity is fixed at startup with a 4-slot probe; a 2026 storage rewrite, with 2.4.2 fixing a get() crash and a flush race. The 170-727x microbenchmark mostly reflects removing the loopback round trip.

## Caveats and trade-offs

This is a real-site benchmark from the plugin author's own README/blog and has not been independently reproduced. It gives no CPU model and no compiler flags, and it covers a single site. Throughput saturates at \~142 RPS because of PHP rendering and MySQL, so the \~19% gain reflects the localhost TCP round trips the drop-in removes. Separately, the yac core repo's bench/README.md (code in bench/mp_bench.php and bench/run_mp.sh; Apple M5 Pro 15-core, PHP 8.5, memcached 1.6.45 on 127.0.0.1) reports 169.6x-726.7x higher aggregate ops/s than local Memcached and 13.4x-69.8x higher than APCu 5.1.28, using 16 forked workers at a 100:1 read:write ratio. That figure does come with a stated methodology. It is not used as the headline because the compiler and flags are unstated and it pits in-process shared memory against per-worker TCP connections, so it mostly measures network round-trip cost. The wp-yac-cache plugin is GPL-2.0-or-later; yac core is PHP-3.01 (GitHub reports NOASSERTION).

Only benefits single-node or few-node installs where PHP workers share a machine (no cross-node cache the way Memcached/Redis provide); shared-memory segment is capacity-bounded; keys over Yac's 48-byte limit get hashed instead of stored verbatim

## Maintenance

Actively maintained by the original author: 2.4.2 stable released 2026-09-10, 2.5.0-dev on master, commits through 2026-09-24. Core is PHP-3.01 licensed (GitHub shows NOASSERTION) and the WordPress plugin is GPLv2-or-later. Install from PECL or PIE rather than vendoring, and expect fast-moving internals after the 2026 storage rewrite.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party real-site benchmark (ab against laruence.com, Yac drop-in vs Memcached drop-in) with the command and table published, but no CPU model, no compiler/flags and no runnable harness. Yac's own microbenchmark (bench/mp_bench.php, bench/run_mp.sh; Apple M5 Pro) has public code and a CPU model, but no compiler or flags and a &gt;50x gain, so it also stays at C.
- **Verifier notes:** The original benchmark_url returns 404 because the repo's default branch is master, not main; corrected. All RPS numbers match the README table exactly. The record's '15-19% lower p50' was slightly off: it is 16.0-16.8% from the table. The caveat that the 170x-730x claim had 'no methodology' was wrong, because yac/bench/README.md documents it with code and hardware. The HN story 49680028 (2026-09-13, 2 points) links the plugin and quotes \~19%. Metadata checked: 833 stars, last commit 2026-09-24, not a fork, not archived.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `hardware`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/laruence/yac>
  - <https://github.com/laruence/wp-yac-cache>
  - <https://github.com/laruence/wp-yac-cache/blob/main/README.md>
  - <https://raw.githubusercontent.com/laruence/wp-yac-cache/main/README.md>
  - <https://raw.githubusercontent.com/laruence/wp-yac-cache/master/README.md>
  - <https://raw.githubusercontent.com/laruence/wp-yac-cache/master/readme.txt>
  - <https://raw.githubusercontent.com/laruence/wp-yac-cache/master/docs/blog-yac-object-cache.md>
  - <https://raw.githubusercontent.com/laruence/yac/master/README.md>
  - <https://raw.githubusercontent.com/laruence/yac/master/bench/README.md>
  - <https://raw.githubusercontent.com/laruence/yac/master/LICENSE>
  - <https://hn.algolia.com/api/v1/search?query=yac%20wordpress&tags=story>
- **Sources the enricher read:**
  - <https://github.com/laruence/yac>
  - <https://github.com/laruence/yac/blob/master/README.md>
  - <https://github.com/laruence/yac/blob/master/bench/README.md>
  - <https://github.com/laruence/yac/blob/master/bench/mp_bench.php>
  - <https://github.com/laruence/yac/blob/master/storage/yac_storage.c>
  - <https://github.com/laruence/yac/blob/master/storage/yac_storage.h>
  - <https://github.com/laruence/yac/blob/master/storage/yac_atomic.h>
  - <https://github.com/laruence/yac/blob/master/storage/allocator/yac_allocator.c>
  - <https://github.com/laruence/yac/blob/master/php_yac.h>
  - <https://github.com/laruence/yac/blob/master/config.m4>
  - <https://github.com/laruence/yac/blob/master/RELEASE_NOTES.md>
  - <https://github.com/laruence/yac/blob/master/package.xml>
  - <https://github.com/laruence/yac/blob/master/.github/workflows/linux.yml>
  - <https://github.com/laruence/yac/blob/master/.github/workflows/hammer.yml>
  - <https://github.com/laruence/yac/blob/master/.github/workflows/windows.yml>
  - <https://github.com/laruence/yac/issues>
  - <https://github.com/laruence/yac/issues/132>
  - <https://github.com/laruence/yac/issues/128>
  - <https://github.com/laruence/yac/issues/125>
  - <https://github.com/laruence/yac/issues/124>
  - <https://github.com/laruence/yac/issues/122>
  - <https://github.com/laruence/yac/issues/83>
  - <https://github.com/laruence/wp-yac-cache>
  - <https://github.com/laruence/wp-yac-cache/blob/master/README.md>
  - <https://github.com/laruence/wp-yac-cache/blob/master/object-cache.php>
  - <https://github.com/laruence/wp-yac-cache/blob/master/docs/blog-yac-object-cache.md>
  - <https://hn.algolia.com/api/v1/search?query=laruence%20yac&tags=story>
  - <https://hn.algolia.com/api/v1/items/49680028>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/laruence/yac`) · [data/wave6/enrich/raw/github_com_laruence_yac.json](../../../data/wave6/enrich/raw/github_com_laruence_yac.json) (enrichment confidence 0.78)

</details>
