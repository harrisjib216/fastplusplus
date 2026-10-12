# Unbound

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [DNS, QUIC and HTTP/3](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `BSD-3-Clause` · 🟢 active

> NLnet Labs' validating, recursive, caching DNS resolver in C; the developer's 2008 changelog puts cache-hit throughput at \~3.4x BIND's.

| | |
|---|---|
| **Beats** | BIND |
| **Claimed result** | 31,218.3 qps (Unbound) vs 8,987.99 qps (BIND) with no DO bit; 28,735.6 qps (Unbound) vs 8,269.31 qps (BIND) with DO bit set -- roughly 3.4x faster cache-hit throughput than BIND (also noted as roughly on par with NSD: 36,048.4 vs 35,182.8 qps on an NXDOMAIN/NSEC3 workload) |
| **Workload** | Cache-hit DNS query throughput: www.nlnetlabs.nl served from cache, with and without the DO (DNSSEC OK) bit set. |
| **Metric** | throughput |
| **Adoption** | 4.9k stars |
| **Last commit** | 2026-09-22 |
| **Links** | [repository](https://github.com/NLnetLabs/unbound) · [benchmark](https://github.com/NLnetLabs/unbound/blob/master/doc/Changelog) |

## Verdict

A 22 Feb 2008 developer Changelog entry reports 31,218 qps (Unbound) vs 8,988 qps (BIND) serving www.nlnetlabs.nl from cache, and 28,736 vs 8,269 qps with the DO bit set, about 3.4x. It also reports near parity with NSD on 100 NSEC3 NXDOMAIN queries (36,048 vs 35,183 qps). The BIND version, compiler, flags, CPU and load generator are not stated. An in-tree perf tool (testcode/perf.c) was written the week before, but the entry does not say it was used. The numbers came right after a round of cache-path optimizations and have not been rerun against modern BIND.

## Use it when

- Recursive or forwarding resolver for a LAN, ISP or host where most queries are cache hits. This is the path the 3.4x figure measures.
- DNSSEC-validating resolution. The DO-bit cache-hit test kept roughly the same lead over BIND (28.7k vs 8.3k qps).
- Multi-core Linux servers. Set num-threads to the core count and so-reuseport to yes; slabs then scale automatically. The docs say a forked (non-threaded) build is another 10-20% faster.
- Applications that need validated DNS lookups in-process via libunbound, synchronous or asynchronous.
- Resolvers that serve or forward DoT, DoH (libnghttp2) or DoQ (libngtcp2). These are optional build features.

## Skip it when

- You need an authoritative primary: dynamic updates or AXFR/IXFR/NOTIFY serving (doc/FEATURES). Keep BIND or NSD for that role.
- You need current numbers. The only head-to-head is an unreproducible 2008 changelog note, and the repo has no recent BIND comparison.
- Windows at high load. The maintainer recommends Linux or BSD for more capacity (issue #240), and the Windows outgoing-range default is 48.
- Very large RPZ or auth-zone datasets where startup and reload time matter. Issue #998 'Unbound is slow at loading (big) auth/rpz zones' is open.
- Low-volume DoT forwarding with many threads. One user measured 90 min for 11k sequential DoT lookups with 4-8 threads vs 30 min with 1 thread (issue #1452, open).

## How it is fast

On a cache hit the worker thread hashes the query, looks it up in the message cache, locks the referenced RRsets and writes the reply straight from stored wire-format data. It does not enter the iterator/validator module stack (daemon/worker.c answer_from_cache). Both caches are 'slabhash' tables: several fixed-size LRU hash tables, each behind a spinlock, with an rwlock per entry. The number of slabs is set near num-threads to cut lock contention, and each RRset is stored as one contiguous block that messages reference by ID. Other per-thread tricks: an alloc cache that avoids the global malloc lock, NSD-style region allocators per query, and up to 100 UDP reads per readiness event (NUM_UDP_PER_SELECT). The built-in 'mini_event' loop is the default because the authors found it faster than libevent.

## Compared with alternatives

Pick Unbound when you need a production-grade, maintained, validating recursive resolver. NailDNS (Nail) is a demo server and Bundy-DNS's 180K qps l1cache is an experimental branch. Hickory DNS is the choice for a Rust/memory-safe stack, but its BIND comparison is only a single-query latency tie, while Unbound's evidence is an old first-party cache-throughput gap.

## Integration

| | |
|---|---|
| **Form** | daemon (unbound) plus shared/static library (libunbound); built from source with ./configure && make, widely distro-packaged |
| **Dependencies** | OpenSSL (libnettle allowed only with --with-libunbound-only), libexpat (for unbound-anchor), flex+bison when building from git; optional: libevent, libnghttp2 (DoH), libngtcp2 (DoQ), libhiredis (cachedb), libsodium (DNSCrypt), Python (pythonmod) |
| **Minimum toolchain** | Portable C compiler; minimum C standard not documented; autoconf 2.56+ only if regenerating configure |
| **Platforms** | Linux, FreeBSD and other BSDs, macOS, Solaris, Windows (reduced capacity); any CPU architecture (users run it on ARM64) |
| **Thread safety** | Daemon: num-threads workers share the slabbed message and RRset caches (spinlock per slab, rwlock per entry). libunbound: multiple threads may share one ub_ctx for blocking calls. unbound.h says the application must set up OpenSSL locking callbacks. |
| **Drop-in for the baseline** | partial — replaces BIND's recursive/caching resolver role only; configuration must be rewritten in unbound.conf syntax, and authoritative features (dynamic update, outbound zone transfer) are not provided |

## Gotchas

- Defaults are conservative: num-threads 1, and msg-cache-size and rrset-cache-size are 4m each. Follow the performance how-to (threads = cores, rrset cache about 2x msg cache, larger so-rcvbuf/so-sndbuf) before judging speed.
- The docs say malloc overhead can push real memory to 2-2.5x the configured cache sizes. In forked mode every process keeps its own cache.
- The default build uses the built-in mini_event loop, which caps outgoing ports (outgoing-range default 960 vs 4096 with --with-libevent). doc/README still says libevent is the default, but configure.ac contradicts it.
- Security churn is heavy: 1.25.2 (2026-07-22) fixed 24 CVEs and 1.26.1 (2026-09-16) fixed 9, including a DNSKEY heap overflow with possible RCE (CVE-2026-81642) and wildcard cache poisoning (CVE-2026-44690). SECURITY.md says fixes land only in the latest release, with no backports.

## Known shortcomings

- The \~3.4x over BIND comes from a 2008 Changelog entry against a 2008 BIND; no modern comparison is cited.
- A recursive resolver, not an authoritative server (no dynamic update, AXFR/IXFR/NOTIFY serving). Heavy security churn: 1.25.2 fixed 24 CVEs and 1.26.1 fixed 9 (including a heap overflow with possible RCE, CVE-2026-81642); fixes land only in the latest release. Defaults are 1 thread and 4 MB caches; real memory can reach 2-2.5x the configured cache size.

## Caveats and trade-offs

This is a first-party developer changelog entry dated 22 February 2008, comparing Unbound to a BIND version of that era; no CPU model, compiler, or exact BIND version is stated, and the result is 18 years old so it may not reflect current BIND/Unbound performance.

Unbound is a validating recursive/caching resolver, not an authoritative server like BIND or NSD, so the roles only overlap for the cache-hit/recursive-resolution path measured here.

## Maintenance

Actively maintained by NLnet Labs (1.26.1 released 2026-09-16, commits through 2026-09-22), BSD-3-Clause and packaged by most distros, so use it as a packaged service rather than vendoring it; stay on the latest release because security fixes are not backported.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party Changelog entry (22 February 2008, Wouter) lists cache-hit qps for BIND and Unbound and states 'about 3.4x faster than BIND in cache performance'. There is no BIND version, compiler, flags, CPU model or named load tool, so C.
- **Verifier notes:** All numbers match doc/Changelog verbatim (BIND 8987.99 vs Ub 31218.3; DO bit BIND 8269.31 vs Ub 28735.6 qps; NSD 35182.8 vs Ub 36048.4), and the 3.4x ratio is stated on the page, not derived. The repo has testcode/perf.c ('estimates DNS name server performance') but the entry does not say it was used. Metadata checks out: BSD-3-Clause, 4,942 stars, last commit 2026-09-22, not archived.
- **Pages the verifier opened:**
  - <https://github.com/NLnetLabs/unbound/blob/master/doc/Changelog>
  - <https://github.com/NLnetLabs/unbound>
  - <https://github.com/NLnetLabs/unbound/blob/master/LICENSE>
  - <https://github.com/NLnetLabs/unbound/blob/master/README.md>
  - <https://github.com/NLnetLabs/unbound/blob/master/testcode/perf.c>
  - <https://www.nlnetlabs.nl/projects/unbound/about/>
- **Sources the enricher read:**
  - <https://github.com/NLnetLabs/unbound>
  - <https://github.com/NLnetLabs/unbound/blob/master/README.md>
  - <https://github.com/NLnetLabs/unbound/blob/master/doc/Changelog>
  - <https://github.com/NLnetLabs/unbound/blob/master/doc/README>
  - <https://github.com/NLnetLabs/unbound/blob/master/doc/FEATURES>
  - <https://github.com/NLnetLabs/unbound/blob/master/doc/unbound.conf.rst>
  - <https://github.com/NLnetLabs/unbound/blob/master/SECURITY.md>
  - <https://github.com/NLnetLabs/unbound/blob/master/configure.ac>
  - <https://github.com/NLnetLabs/unbound/blob/master/dnscrypt/dnscrypt.m4>
  - <https://github.com/NLnetLabs/unbound/blob/master/daemon/worker.c>
  - <https://github.com/NLnetLabs/unbound/blob/master/util/storage/lruhash.h>
  - <https://github.com/NLnetLabs/unbound/blob/master/util/storage/slabhash.h>
  - <https://github.com/NLnetLabs/unbound/blob/master/util/alloc.h>
  - <https://github.com/NLnetLabs/unbound/blob/master/util/regional.h>
  - <https://github.com/NLnetLabs/unbound/blob/master/util/data/packed_rrset.h>
  - <https://github.com/NLnetLabs/unbound/blob/master/util/data/msgreply.h>
  - <https://github.com/NLnetLabs/unbound/blob/master/util/netevent.c>
  - <https://github.com/NLnetLabs/unbound/blob/master/libunbound/unbound.h>
  - <https://github.com/NLnetLabs/unbound/issues/1452>
  - <https://github.com/NLnetLabs/unbound/issues/1113>
  - <https://github.com/NLnetLabs/unbound/issues/240>
  - <https://github.com/NLnetLabs/unbound/issues?q=performance>
  - <https://github.com/NLnetLabs/unbound/issues?q=cpu>
  - <https://github.com/NLnetLabs/unbound/issues?q=memory+leak>
  - <https://github.com/NLnetLabs/unbound/releases>
  - <https://nlnetlabs.nl/projects/unbound/security-advisories/>
  - <https://unbound.docs.nlnetlabs.nl/en/latest/topics/core/performance.html>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/nlnetlabs/unbound`) · [data/wave5/enrich/raw/github_com_nlnetlabs_unbound.json](../../../data/wave5/enrich/raw/github_com_nlnetlabs_unbound.json) (enrichment confidence 0.8)

</details>
