# Bundy-DNS (l1cache experimental branch)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [DNS, QUIC and HTTP/3](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `ISC` · 🟢 active

> Bundy's unpublished l1cache experiment: pre-rendered wire-format DNS answer cache, claimed 180K vs 41K qps over BIND 9.9.2.

| | |
|---|---|
| **Beats** | BIND |
| **Claimed result** | Experimental cache-only server with fully-rendered cached data: 'over 180Kqps' vs 'just 41K qps' for BIND 9.9.2 (queryperf-like benchmark, single core, 2.20GHz AMD64), about 4.4x (derived from page data). The same memo says the jinmei-l1cache branch 'ran vary [sic] fast; more than 4 times faster than BIND 9, and even much faster than other implementations that have full response cache (although, as usual, the comparison is not entirely fair)'. |
| **Workload** | Recursive-resolver cache-hit path (not authoritative serving): experimental cache-only implementation (jinmei-l1cache branch) using a hash table keyed by (query name, type) that stores the fully rendered wire-format answer section (minimal-responses) plus RR offsets for TTL update/rotation; max response throughput measured with a queryperf-like tool on one core against BIND 9.9.2. |
| **Metric** | throughput |
| **Hardware** | One test machine, 2.20GHz AMD64, single core used; CPU model not named |
| **Adoption** | 138 stars |
| **Last commit** | 2026-03-18 |
| **Links** | [repository](https://github.com/bundy-dns/bundy) · [benchmark](https://github.com/bundy-dns/bundy/blob/master/doc/design/resolver/03-cache-algorithm) |

## Verdict

A first-party design memo committed in December 2013 reports that an experimental cache-only server with fully rendered cached answers handled over 180K qps, against 41K qps for BIND 9.9.2 (about 4.4x), measured with a 'queryperf-like' tool on one core of a 2.20GHz AMD64 machine. It gives no CPU model, compiler, flags, query set or BIND configuration, and the benchmarked code is not public.

## Use it when

- As a design reference for a resolver or DNS front-end: put a small per-thread cache of pre-rendered answers in front of a shared record cache.
- Traffic where most queries hit the cache and a few names dominate (the memo's data: top 10k names about 80% of queries) and answer-only minimal responses are acceptable.
- Capacity planning: the memo's model A = rQ2/(rQ2 + Q1(1-r)) estimates what share of server time goes to cache hits at a given hit rate r (about 72-76% at r = 0.9 in its experiments).
- Prototyping DNS features on the Bundy codebase, which its README recommends because much of it is Python.

## Skip it when

- When you need runnable code: the benchmarked jinmei-l1cache branch is not published (the repo has 21 branches and none of them is l1cache), so it cannot be built or reproduced.
- Production DNS of any kind: the README puts Bundy in 'hibernation' with no development and no security fixes and says not to use it in production, and open issue #110 proposes removing the resolver code entirely.
- DNSSEC validation or full responses with authority and additional sections: the memo says the experiment 'skips some necessary features for a production server' and caches only the answer section.
- Modern toolchains: open issues report build failures with Boost 1.60 (#102), Clang 8 on macOS 10.12 (#114, #115) and newer Python headers under -Werror (#123), and GCC 4.9 needs -std=c++11 (#119).
- When you want a maintained resolver that beats BIND on cache-hit throughput: use Unbound.

## How it is fast

It is a full-response ('L1') cache. The hash table is keyed by (query name, type), and each entry holds the answer section already rendered in wire format (it assumes minimal-responses) plus the offset of each RR, so TTLs can be patched in place or RRs rotated. When neither is needed, a hit is just a hash lookup and a copy of the stored bytes: no RRset lookups, name compression or message rendering. It relies on skewed query popularity (in two datasets the top 10,000 queries covered about 80% of traffic), so the whole cache was about 5 MB, small enough for each process or thread to keep a private copy with no lock contention.

## Compared with alternatives

Pick it only as a design idea for a per-thread pre-rendered answer cache. For a caching resolver you will actually run, Unbound is the maintained sibling that also beats BIND on cache-hit qps. Nail and Hickory DNS are the BIND alternatives with public code, but they target authoritative serving and query latency, not resolver caching.

## Integration

| | |
|---|---|
| **Form** | source-drop (the benchmarked l1cache code is unpublished; Bundy itself is an autotools-built daemon suite and requires shared libraries) |
| **Dependencies** | Boost headers (&gt;=1.35; fails with 1.60 per #102), Botan &gt;=1.8, log4cplus &gt;=1.0.3, SQLite3 &gt;=3.3.9, Python &gt;=3.1 with dev headers; bundled ext/asio and ext/coroutine (BSL-1.0); googletest optional |
| **Minimum toolchain** | C++03-era code; the guide lists tests with GCC 3.4.3-4.4.1, Clang++ 2.8 and Sun C++ 5.10; GCC 4.9 needs -std=c++11 (#119); recent Boost, Clang and Python fail to build per open issues |
| **Platforms** | The guide lists tested builds on Debian 6, Ubuntu 9.10, NetBSD 5, Solaris 10/11, FreeBSD 7/8, CentOS 5.3, macOS 10.6/10.7 and OpenBSD 5.1, on Sparc, i386 and amd64; the l1cache figure comes from one 2.20GHz AMD64 core only |
| **Thread safety** | The shipped bundy-resolver runs a single asio IOService loop from main(). The memo proposes a private copy of the roughly 5 MB l1cache per process or thread to avoid contention; no locking design is documented. |
| **Drop-in for the baseline** | no |

## Gotchas

- The 180K qps figure is for a cache-only experiment answering hits. The author says a production version 'wouldn't be that fast' and only projects that more than 100K qps 'may not be very difficult' once recursion is included.
- The fast path is a hash lookup plus a copy only when neither TTL adjustment nor RR rotation is needed; either one adds per-hit rewriting through the stored RR offsets.
- Claims that it is 'much faster than other implementations that have full response cache' give no numbers or names, and the memo calls the comparison 'not entirely fair'. The memo's other experiments ran BIND 9.9.2 forward-only with crafted query data, but the setup for the 41K qps BIND run is not stated.
- Do not mistake the shipped src/lib/cache for the benchmarked design: its TODO says the LRU hash table is not yet used, dump/load/resize are not implemented and DNSSEC AD flags are not set. The memo's links (lists.bundy.org, bundy.bundy.org wiki) are dead; the original 2012 ISC bind10-dev post survives but has no qps figures for this server.

## Known shortcomings

- The benchmarked l1cache branch is not in the public repo, so the 4.4x over BIND 9.9.2 (single core, 2.2 GHz AMD64) cannot be reproduced. The project is in 'hibernation': last code commit 2017, later commits edit only the README.
- The shipped cache is a different, unfinished design (unbound-style message cache; LRU, dump/load and DNSSEC AD flags TODO) and the resolver is an experimental proof of concept (#110 proposes removing it). Build is broken on current toolchains (#102, #114, #115, #123). The benchmark gives no BIND setup, CPU, compiler or flags, and its links are dead. Enrichment confidence 0.3 (below the 0.4 flag threshold).

## Caveats and trade-offs

First-party design-memo claim (doc/design/resolver/03-cache-algorithm, committed 2013, benchmark against BIND 9.9.2) with no compiler, flags or CPU model. The author says the experimental implementation 'skips some necessary features for a production server', that a production version 'wouldn't be that fast', and that the comparison is 'not entirely fair'. The jinmei-l1cache branch is not among the 21 branches of bundy-dns/bundy and GitHub code search finds 'l1cache' only in this design doc, so the benchmarked code is not public; shipped Bundy has no such speed claim. README declares the project in 'hibernation' (no active development, no security fixes, not recommended for production); the last code commit is 2017-05-10 and the 2026 commits only edit README.org. License: ISC core; bundled ext/asio and ext/coroutine are BSL-1.0.

The design doc itself cautions 'as usual, the comparison is not entirely fair'; the l1cache approach was an experimental idea documented on a named developer branch, not confirmed as merged into Bundy's mainline default response path. Bundy is a community continuation of the discontinued ISC BIND10 project.

## Maintenance

The 2026 commits only edit README.org; the last code commit was 2017-05-10 and the README declares hibernation with no security fixes. The code is ISC-licensed (asio and coroutine are BSL-1.0), but the benchmarked l1cache implementation was never published, so there is nothing to vendor and the entry is usable only as a documented technique.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party design memo gives numbers against BIND 9.9.2 (&gt;180Kqps vs 41K qps, queryperf-like tool, one core of a 2.20GHz AMD64 machine) and says the jinmei-l1cache branch was 'more than 4 times faster than BIND 9'. The benchmarked code is not public in this repo, and there is no compiler, flags or CPU model, so it cannot be A; not peer-reviewed, so C.
- **Verifier notes:** Record understated the page: exact qps figures (&gt;180Kqps vs 41K qps for BIND 9.9.2) are present, and the workload is a recursive-resolver cache, not an authoritative path. maintenance_status left 'active' by the last-commit rule (2026-03-18), but those commits are README-only and README says 'hibernation'; orchestrator may prefer 'abandoned' (last code commit 2017). has_code left true (repo has DNS code) but the benchmarked l1cache code is not public; consider has_code=false for this variant. The memo's cited list link lists.bundy.org is dead (DNS failure); the ISC copy of the related 2012 bind10-dev post has no qps numbers.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `hardware`, `is_fork_of`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/bundy-dns/bundy/blob/master/doc/design/resolver/03-cache-algorithm>
  - <https://github.com/bundy-dns/bundy>
  - <https://github.com/bundy-dns/bundy/blob/master/COPYING>
  - <https://github.com/bundy-dns/bundy/blob/master/README.org>
  - <https://github.com/bundy-dns/bundy/branches>
  - <https://github.com/bundy-dns/bundy/commits/master>
  - <https://lists.isc.org/pipermail/bind10-dev/2012-July/003628.html>
- **Sources the enricher read:**
  - <https://github.com/bundy-dns/bundy>
  - <https://github.com/bundy-dns/bundy/blob/master/README.org>
  - <https://github.com/bundy-dns/bundy/blob/master/doc/design/resolver/03-cache-algorithm>
  - <https://github.com/bundy-dns/bundy/blob/master/doc/design/resolver/README>
  - <https://github.com/bundy-dns/bundy/blob/master/doc/design/resolver/01-scaling-across-cores>
  - <https://github.com/bundy-dns/bundy/blob/master/src/lib/cache/TODO>
  - <https://github.com/bundy-dns/bundy/blob/master/src/lib/cache/message_cache.h>
  - <https://github.com/bundy-dns/bundy/blob/master/src/lib/cache/resolver_cache.h>
  - <https://github.com/bundy-dns/bundy/blob/master/src/lib/cache/message_entry.h>
  - <https://github.com/bundy-dns/bundy/blob/master/src/bin/resolver/bundy-resolver.xml>
  - <https://github.com/bundy-dns/bundy/blob/master/src/bin/resolver/main.cc>
  - <https://github.com/bundy-dns/bundy/blob/master/src/bin/resolver/resolver.cc>
  - <https://github.com/bundy-dns/bundy/blob/master/configure.ac>
  - <https://github.com/bundy-dns/bundy/blob/master/COPYING>
  - <https://github.com/bundy-dns/bundy/blob/master/INSTALL>
  - <https://github.com/bundy-dns/bundy/blob/master/doc/guide/bundy-guide.xml>
  - <https://github.com/bundy-dns/bundy/tree/master>
  - <https://github.com/bundy-dns/bundy/branches>
  - <https://github.com/bundy-dns/bundy/commits/master>
  - <https://github.com/bundy-dns/bundy/commits/master/doc/design/resolver/03-cache-algorithm>
  - <https://github.com/bundy-dns/bundy/commit/3677658ea0>
  - <https://github.com/bundy-dns/bundy/issues>
  - <https://github.com/bundy-dns/bundy/issues/102>
  - <https://github.com/bundy-dns/bundy/issues/108>
  - <https://github.com/bundy-dns/bundy/issues/110>
  - <https://github.com/bundy-dns/bundy/issues/119>
  - <https://github.com/bundy-dns/bundy/issues/123>
  - <https://github.com/jinmei?tab=repositories>
  - <https://github.com/jinmei/queryperfpp>
  - <https://github.com/isc-projects/bind10>
  - <https://github.com/search?q=l1cache&type=repositories>
  - <https://lists.isc.org/pipermail/bind10-dev/2012-July/003628.html>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/bundy-dns/bundy`) · [data/wave5/enrich/raw/github_com_bundy_dns_bundy.json](../../../data/wave5/enrich/raw/github_com_bundy_dns_bundy.json) (enrichment confidence 0.3)

</details>
