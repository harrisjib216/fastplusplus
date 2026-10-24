# Varnish Cache

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Caches](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `BSD-2-Clause` · ⚪ unknown

> Multi-threaded HTTP reverse-proxy cache programmed in VCL; beats a single-worker nginx proxy_cache but not nginx on all cores.

| | |
|---|---|
| **Beats** | NGINX 1.12.2 proxy_cache (worker_processes 1 and worker_processes auto on 12 cores) in front of an nginx origin |
| **Claimed result** | Not faster on equal footing. Table 1 (1 Gbps, 1000 connections), requests/s: hello-world 12 B Varnish 133094 vs nginx 1 worker 33454 (3.98x, derived from page data) but vs nginx 12 workers 214217 (0.62x, derived from page data); 1 KB Varnish 87772 vs nginx 1 worker 36034 (2.44x, derived from page data) and vs nginx 12 workers 91497 (0.96x, derived from page data). Table 2 (loopback, 1000 connections) hello-world: Varnish 115928 vs nginx 1 worker 30996 (3.74x, derived from page data) and vs nginx 12 workers 136844 (0.85x, derived from page data). Table 3 (loopback, 5000 connections) hello-world: Varnish 111711 vs nginx 12 workers 125309 (0.89x, derived from page data); nginx 1 worker is marked ERROR in every Table 3 row. nginx with all cores beats Varnish in every row of all three tables. No number against an origin server without a cache was found, and Varnish publishes no figures in its README. |
| **Workload** | wrk -t 100 -c 1000 -d 30 requests for cached static files of 12 B to 1 KB through each cache server (Varnish 4.1.8 malloc 1024M, default threads; nginx 1.12.2 proxy_cache) on a 12-core Xeon, over a 1 Gbps link and over loopback, plus 5000 connections on loopback; measured by the author of the competing nuster cache. |
| **Metric** | throughput |
| **Hardware** | Intel Xeon X5650 @ 2.67GHz, 12 cores, 32 GB RAM, 1 Gbps NIC, CentOS 7.4.1708 (origin nginx on a second machine in the 1 Gbps runs) |
| **Compiler and flags** | Not stated: distribution packages are implied; Varnish VCL backend, beresp.ttl = 1d, VARNISH_STORAGE malloc,1024M; nginx proxy_cache STATIC, proxy_cache_valid any 1d, worker_connections 1000000, keepalive_requests 100000; wrk 4.0.2-2-g91655b5. |
| **Adoption** | 4.0k stars, 391 forks; widely deployed HTTP accelerator |
| **Last commit** | 2026-02-16 |
| **Links** | [repository](https://github.com/varnishcache/varnish-cache) · [benchmark](https://github.com/jiangwenyuan/nuster/wiki/Web-cache-server-performance-benchmark:-nuster-vs-nginx-vs-varnish-vs-squid) |

## Verdict

The author of the competing nuster cache ran wrk (-t 100, -c 1000 or 5000, 30 s) against Varnish 4.1.8 (malloc 1024M, default threads) and nginx 1.12.2 proxy_cache on a 12-core Xeon X5650 with CentOS 7.4 packages (no compiler or flags stated): Varnish served 2.4-4.0x more requests/s than nginx with one worker, but only 0.62-0.96x of nginx with all 12 workers, which won every row. The 512 B and 1 KB rows over 1 Gbps are close to link saturation for the fastest servers (about 0.89-0.93 Gbit/s of HTTP payload for nginx on 12 workers, derived from page data), and the loopback runs put wrk's 100 threads on the same 12 cores as the server.

## Use it when

- HTTP reverse-proxy caching for sites or APIs where per-request cache logic (normalising URLs, stripping cookies, grace and ban/purge rules) is easier to write in VCL than in nginx directives.
- Small cached objects served at high request rates from RAM, on a box where Varnish can use several cores; in the nuster benchmark it sustained about 107-133k req/s for 12 B to 1 KB objects on a 12-core Xeon X5650.
- Origins that are slow relative to the cache, where collapsing concurrent misses and serving stale content during refresh matters more than raw hit throughput.
- Teams that already run nginx or HAProxy for TLS termination and want a separate, scriptable cache layer behind it.

## Skip it when

- Maximum small-object hit throughput per box: nginx proxy_cache with worker_processes auto beat Varnish 4.1.8 in every row of the only comparison found (for example 214,217 vs 133,094 req/s for a 12-byte body over 1 Gbps).
- When you need TLS termination in the cache itself: the core has no TLS listener, so you need Hitch, HAProxy or nginx in front.
- When you want HTTP/2 without extra configuration: HTTP/2 is a feature bit (feature=+http2) that is off in the default feature set.
- When you need a key-value cache API for application data: it only speaks HTTP to clients and backends.
- If you need a single long-term upstream: the GitHub repo is archived, and the code lives on as Vinyl Cache while Varnish Software keeps the Varnish Cache name, so packaging and naming are in flux.

## How it is fast

VCL is translated to C and compiled with the system C compiler into a dlopen(3)-loaded object (cc_command parameter), so request policy runs as native code rather than being interpreted. Cached objects are looked up through a critbit tree (default -h critbit) and stored in the malloc stevedore by default (jemalloc on Linux builds), so hits are served from memory. Requests run on pooled worker threads (thread_pools default 2, thread_pool_min 100, thread_pool_max 5000), idle keep-alive connections are parked in an epoll/kqueue/event-ports waiter, and logging goes to a shared-memory ring (VSL) read by separate tools instead of being written synchronously.

## Compared with alternatives

None of the catalogued siblings is an HTTP reverse-proxy cache: Pogocache, Dragonfly, Valkey and CacheLib are key-value caches or libraries, and AdaptSize is an admission-control patch evaluated on top of Varnish itself. Pick Varnish when the cache must speak HTTP to clients and origins and you want programmable policy; pick a KV cache when the application controls lookups.

## Integration

| | |
|---|---|
| **Form** | standalone server (varnishd plus CLI tools); VMODs as loadable modules |
| **Dependencies** | libpcre2-8, python3-docutils (rst2man) and python3-sphinx to build, jemalloc by default on Linux, optional libunwind; a C compiler at runtime to compile VCL |
| **Minimum toolchain** | C99 compiler (AC_PROG_CC_C99), autoconf 2.69+ |
| **Platforms** | Linux (epoll waiter), FreeBSD and other kqueue systems, Solaris/illumos (event ports, umem storage); macOS has build handling in configure.ac |
| **Thread safety** | not applicable: a multi-threaded server process with per-pool worker threads; thread_pools, thread_pool_min and thread_pool_max are runtime parameters |
| **Drop-in for the baseline** | no |

## Gotchas

- Defaults are not tuned for benchmarks: the compared Varnish ran with default thread settings while nginx was given worker_connections 1000000 and keepalive_requests 100000, so neither side was tuned the same way.
- The miss-path delay quoted from issue #1923 (30-40 ms extra per miss on 4.0.2) was not a Varnish defect: the reporter traced it to a Node.js backend that sent no Content-Length header, and adding one removed the wait.
- Security fixes keep landing in HTTP/1 and HTTP/2 parsing (VSV00014 to VSV00017, HTTP/2 rapid reset CVE-2023-44487 and 'Made You Reset'), so track the Vinyl Cache release stream rather than the frozen GitHub 'last' tag.
- vsl_space (default 80M) sizes the shared-memory log; if it is too small varnishlog and varnishncsa cannot keep up.

## Known shortcomings

- Not faster than nginx proxy_cache (verifier reject not-faster overridden to keep): in the nuster wiki numbers nginx with 12 workers beats Varnish in all 18 rows; Varnish wins only against a 1-worker nginx (asymmetric baseline). Repo archived 2026-02-16 and moved to Vinyl Cache (unreachable).
- 1 Gbps rows near link saturation; loopback load generator shares the server's cores; GitHub repo archived, development moved to Vinyl Cache

## Caveats and trade-offs

The only numeric comparison found is a competitor's wiki page (nuster author; nuster tops every table), page last edited 13 Aug 2018 with sample-output Date headers of 5 Nov 2017, on old releases (Varnish 4.1.8, nginx 1.12.2, wrk with --timeout 300 and -t 100); not a first-party Varnish claim and not peer reviewed, so tier C. The only wins are against a single nginx worker (an asymmetric baseline against multi-threaded Varnish); nginx on 12 workers beats Varnish in every row, and Varnish logged socket timeouts in two rows (17 at 1 KB in Table 1, 118 at hello-world in Table 2). Varnish's thread settings were left at defaults. The origin-without-cache baseline in the assignment has no number anywhere reachable (a varnish/hitch issue reports about 10,835 req/s through Varnish against 776 req/s through a TLS path, which is not an origin comparison). The GitHub repository was archived on 2026-02-16 (last commit 'Moving') and its README says development moved to code.vinyl-cache.org with the last usable GitHub version tagged 'last' (that site did not resolve from this container, so it was not checked); maintenance_status is 'unknown' for that reason. Related prior work: the AdaptSize paper tunes Varnish admission and reports hit-ratio gains over stock Varnish, which is not a comparison against Varnish as the winner. [retier] Enricher: harness defects in the nuster wiki: the 512 B and 1 KB rows over 1 Gbps run near link saturation (nginx 12 workers at about 0.89-0.93 Gbit/s of HTTP payload, derived from page data), so they measure the link; the loopback runs put wrk -t 100 on the same 12 cores as the server; Varnish threads stayed at defaults while nginx was tuned. Correction: the 30-40 ms miss delay in issue #1923 came from a Node.js backend that sent no Content-Length, not from Varnish, so it is not a Varnish tradeoff.

In-memory (malloc) or file-backed HTTP reverse-proxy cache configured through the VCL language, which gives fine control over caching and request handling but has a learning curve; no TLS termination in the core (needs Hitch or similar); multi-threaded, so a hit costs more cores than one nginx worker; a miss path adds latency (Varnish issue #1923 reported about 30-40 ms extra on misses with 4.0.2, snippet only).

## Maintenance

GitHub repository archived on 16 Feb 2026 (last 8.0.0 release 15 Sep 2025, 'last' tag); development continues under the Vinyl Cache name at code.vinyl-cache.org (search snippets mention a 9.0.0 release in April 2026, not opened), and BSD-2-Clause licensing makes it freely deployable.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): reject; tier before verification C, tier now C.
- **Tier reason:** The nuster wiki page (a competitor's author) publishes wrk commands, server configs, versions and the CPU (Xeon X5650) but no compiler or flags (distribution packages) and no harness repo; it is neither first-party to Varnish nor peer reviewed, so C. On equal resources (nginx worker_processes auto on 12 cores) nginx proxy_cache beats Varnish in all 18 rows of the three tables; the only Varnish wins are against a single nginx worker.
- **Verifier notes:** All table numbers on the nuster wiki match the record; derived ratios recomputed and correct. Rejected as not-faster against the equal-resource baseline (nginx proxy_cache with all cores); keep with a 'not faster' shortcoming if policy keeps it. Archived repo, development moved to Vinyl Cache (unreachable), so maintenance left 'unknown' rather than 'abandoned'.
- **Fields the verifier corrected:** `claimed_speedup`, `stars_or_usage`, `caveats`, `maintenance_status`
- **Shortcomings recorded by:** verifier batch-93 (wave 6 book seed pass, 2026-10-24); enrichment (wave 6 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://github.com/jiangwenyuan/nuster/wiki/Web-cache-server-performance-benchmark:-nuster-vs-nginx-vs-varnish-vs-squid>
  - <https://github.com/varnishcache/varnish-cache>
  - <https://github.com/varnishcache/varnish-cache/commits>
  - <https://raw.githubusercontent.com/varnishcache/varnish-cache/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/varnishcache/varnish-cache/tree/master/bin/varnishd>
  - <https://github.com/varnishcache/varnish-cache/tree/master/bin/varnishd/storage>
  - <https://raw.githubusercontent.com/varnishcache/varnish-cache/HEAD/README.rst>
  - <https://raw.githubusercontent.com/varnishcache/varnish-cache/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/varnishcache/varnish-cache/HEAD/INSTALL>
  - <https://raw.githubusercontent.com/varnishcache/varnish-cache/HEAD/doc/changes.rst>
  - <https://raw.githubusercontent.com/varnishcache/varnish-cache/HEAD/configure.ac>
  - <https://raw.githubusercontent.com/varnishcache/varnish-cache/HEAD/include/tbl/params.h>
  - <https://raw.githubusercontent.com/varnishcache/varnish-cache/HEAD/include/tbl/feature_bits.h>
  - <https://raw.githubusercontent.com/varnishcache/varnish-cache/HEAD/bin/varnishd/mgt/mgt_main.c>
  - <https://github.com/varnishcache/varnish-cache/issues/1923>
  - <https://github.com/jiangwenyuan/nuster/wiki/Web-cache-server-performance-benchmark:-nuster-vs-nginx-vs-varnish-vs-squid>
  - https://ma.ttias.be/varnish-vinyl-cache-2026/ (search snippet only)
  - https://dfsg-new-queue.debian.org/reviews/vinyl-cache (search snippet only)
  - https://www.varnish.org/what-is-varnish-cache/ (search snippet only)
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/varnishcache/varnish-cache`) · [data/wave6/enrich/raw/github_com_varnishcache_varnish_cache.json](../../../data/wave6/enrich/raw/github_com_varnishcache_varnish_cache.json) (enrichment confidence 0.65)

</details>
