# dnspython

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [DNS, QUIC and HTTP/3](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Python` · `ISC` · 🟢 active

> Pure-Python DNS toolkit; gevent's wrapper for it beat gevent's c-ares resolver on the maintainer's macOS, but lost on Linux.

| | |
|---|---|
| **Beats** | c-ares |
| **Claimed result** | gevent PR #1088 (gevent maintainer, local caching dnsmasq, macOS): 300 sequential gethostbyname calls took c-ares 3.19-3.60 s vs dnspython 0.81-1.80 s across PyPy 2 5.10 / CPython 2.7 / 3.6 / 3.7b1 (about 2-4.4x, derived from page data). 100 parallel greenlet lookups took c-ares 2.33-2.60 s vs dnspython 0.18-0.29 s (about 8.6-13x, derived from page data). bench_dns_resolver.py on CPython 3.7.0: dnspython 147 us vs ares 6.56 ms sequential, 152 us vs 6.76 ms parallel (about 44-45x, derived from page data). The changelog says only 'generally faster than c-ares', and the gevent dnspython resolver docstring says 'usually much faster than the c-ares resolver'. CONTESTED: another user on the same PR, running the same script on Linux Mint 19.1 / CPython 2.7.15, got ares at 36.7 us vs dnspython at 100 us sequential (ares about 2.7x faster, derived from page data). |
| **Workload** | gevent resolver backends (gevent.resolver.dnspython vs gevent.resolver.ares) doing gethostbyname against a local dnsmasq configured to cache everything: 300 sequential lookups, 100 concurrent greenlet lookups, and gevent benchmarks/bench_dns_resolver.py (pyperf, N=150, RUN_COUNT=2) |
| **Metric** | other |
| **Hardware** | unspecified macOS machine (gevent maintainer); counter-measurement on unspecified Linux Mint 19.1 machine; no CPU models stated |
| **Adoption** | 2.7k stars; used as a resolver backend by gevent, and as a dependency by many Python networking/security tools (e.g. certbot ecosystem) |
| **Last commit** | 2026-09-26 |
| **Links** | [repository](https://github.com/rthalley/dnspython) · [benchmark](https://github.com/gevent/gevent/pull/1088) |

## Verdict

On one unspecified macOS machine with a local dnsmasq that caches everything, gevent's maintainer measured gevent's dnspython resolver ahead of gevent's c-ares resolver: about 2-4.4x on 300 sequential gethostbyname calls and 8.6-13x on 100 parallel greenlet lookups (Feb 2018, dnspython cache off, PyPy 2 5.10 and CPython 2.7/3.6/3.7b1), and 147 us vs 6.56 ms per lookup (about 45x) with gevent's bench_dns_resolver.py on CPython 3.7.0 (Oct 2018, LRUCache on). The result is contested: the same script on Linux Mint 19.1 (CPython 2.7.15rc1) gave c-ares 36.7 us vs dnspython 100 us (c-ares about 2.7x faster); dnspython's per-lookup time was similar on both machines (147 vs 100 us), and c-ares differed about 180x (6.56 ms vs 36.7 us), so the flip comes from c-ares on the macOS setup (all ratios derived from page data; no CPU models given).

## Use it when

- gevent programs that make many concurrent lookups, where the default threaded resolver is not acceptable and you have measured gevent's c-ares resolver as slow on your own platform (the published win is from macOS only).
- Workloads that look up the same names many times, where an in-process cache that obeys DNS TTLs, can be sized (set_max_size) and can be flushed is useful.
- Anything beyond A/AAAA lookups: arbitrary record types, zone transfers, dynamic updates, TSIG, EDNS0, DNSSEC, and DNS over HTTPS, TLS or QUIC through optional extras.
- asyncio or Trio code that needs a native async resolver (dns.asyncresolver) instead of running getaddrinfo in a thread pool.
- PyPy or other deployments where you want no C extension: dnspython has no required dependencies, and gevent's docs call its own c-ares resolver 'extremely experimental on PyPy' with possible interpreter crashes.

## Skip it when

- gevent services on Linux. The only independent rerun of gevent's script (Linux Mint 19.1, CPython 2.7.15rc1, gevent 1.3.7, local dnsmasq) had c-ares at 36.7 us vs dnspython at 100 us per sequential lookup and 32.8 vs 103 us in parallel, so c-ares was about 2.7-3.1x faster (derived from page data).
- Uncached lookups against a remote resolver. In the PR's first test (100 lookups against 8.8.8.8), c-ares took 50-53 s and dnspython 156-162 s, so c-ares was about 3x faster; the same user's earlier Linux run with the older script had dnspython at 5.46 s vs c-ares at 0.31 s (best of 5).
- When you need system resolution semantics. dnspython does not read /etc/hosts, and its README says socket.getaddrinfo() or socket.gethostbyname() is better for simple forward lookups.
- CPU-bound, very high-rate resolution: every response is parsed in Python. Issue #259 showed large A/AAAA answers burning CPU in the old O(n^2) set code; the new set code fixed it, but parsing is still interpreted.
- When you need a current number: all measurements are from 2018-2019 (dnspython 1.15-era on Python 2.7/3.6/3.7) and were never re-run. Since c-ares 1.31.0 the c-ares query cache is on by default (gevent now bundles c-ares 1.34.5), which removes the cache asymmetry the old runs depended on.

## How it is fast

There is no new algorithm; the measured win comes from how gevent uses dnspython. gevent attaches a TTL-respecting, thread-safe dns.resolver.LRUCache to one module-global dnspython resolver (dnspython caches nothing by default), so repeat lookups are answered in-process with no network round trip; the maintainer reported that turning the cache on cut the parallel run from 0.18-0.29 s to 0.05-0.07 s. Under gevent monkey-patching, dnspython's pure-Python sockets become cooperative, so 100 greenlet lookups overlap: on the maintainer's machine the parallel run took 16-22% of the sequential time, against 65-82% for c-ares. The benchmark harness also creates a new gevent c-ares Resolver, and so a new c-ares channel, inside every timed call, while each new dnspython Resolver reuses the shared, already-warm resolver.

## Compared with alternatives

The catalogued siblings are DNS servers (Unbound, Hickory DNS, Nail, Bundy-DNS, measured against BIND) and QUIC stacks, and none is a client-side Python resolver library. Pick dnspython when resolution or DNS message and zone handling must happen inside a Python process, and pair it with a local caching server such as Unbound; for native code or Linux gevent services, the c-ares baseline is the better-measured choice.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none for the default install (standard library only). Optional extras: dnssec (cryptography), doh (httpcore2, httpx2, h2), doq (aioquic), idna, trio, wmi (Windows only). The benchmarked setup also needs gevent. |
| **Minimum toolchain** | Python 3.10+ (dnspython 2.8.0 and 2.9.0 dev); Python 2 support ended with 1.16.0 |
| **Platforms** | any platform with CPython 3.10+ (package classifiers list POSIX and Windows); gevent's changelog says the dnspython backend works on PyPy |
| **Thread safety** | Resolver.resolve() is safe to call from many threads, but changing resolver configuration is not. Cache and LRUCache are thread-safe. Name and Rdata are immutable; Message, Rdataset, RRset and Zone are not locked (VersionedZone is thread-safe). |
| **Drop-in for the baseline** | partial — inside gevent it replaces gevent's c-ares resolver behind the same socket-module functions through gevent's resolver setting; as a standalone library its API is unrelated to c-ares, though dns.resolver.override_system_resolver() can patch Python's socket module to use it |

## Gotchas

- dnspython's resolver does not cache unless you assign a cache (resolver.cache = dns.resolver.LRUCache()). The gevent benchmark had gevent's LRUCache on, so direct dnspython users without a cache will not see those numbers.
- gevent's wrapper adds its own hosts-file layer (reloaded every 300 s) and, by default, extra CNAME queries for aliases. gevent's benchmark turns the alias lookups off for dnspython because c-ares does not do them.
- gevent still documents the dnspython resolver as '\*experimental\*' and says it 'may be removed or modified in the future'; errors and IPv6 scope-ID handling differ from the standard library.
- Use 2.6.1 or later: CVE-2023-29483 (GHSA-3rq5-2g8h-59hc, the 'TuDoor' DoS through spoofed responses in the stub resolver) affects versions before 2.6.1.

## Known shortcomings

- Contested and platform-dependent: the gevent maintainer's macOS runs (local caching dnsmasq) show dnspython 2-45x faster, but a Linux Mint rerun of the same script found c-ares 2.7-3.1x faster, an earlier Linux run \~17x faster, and the maintainer's own uncached test against 8.8.8.8 \~3x faster; dnspython's per-lookup time was similar on both machines while c-ares differed \~180x. It compares gevent's wrappers, not the libraries: gevent attaches a TTL LRU cache to dnspython (plain dnspython caches nothing), the harness builds a new c-ares channel inside every timed call while dnspython reuses a warm resolver, and dnspython's CNAME lookups are disabled. Data is 2018-19 (dnspython 1.15 era), never re-run; c-ares 1.31+ caches by default and gevent now bundles 1.34.5. gevent still labels its dnspython resolver experimental. dnspython itself does not read /etc/hosts (gevent's wrapper does). Versions before 2.6.1 are affected by CVE-2023-29483 (TuDoor DoS).

## Caveats and trade-offs

Numbers come from gevent's maintainer (gevent PR #1088), not from the dnspython project. They compare gevent's resolver wrappers: dnspython (pure Python, with its own TTL cache) vs c-ares behind gevent's Cython binding, so they do not test dnspython against c-ares as a standalone library. The gevent PR author found early runs against 8.8.8.8 'wildly variable and extremely suspect', and in that setup dnspython was about 3x slower than c-ares. Only the later runs against a local caching dnsmasq favour dnspython. An independent rerun of the same benchmark script on Linux (gevent 1.3.7, Python 2.7) found c-ares about 2.7x faster than dnspython, so the win looks platform- and setup-dependent (macOS). No CPU model, compiler or flags are given. gevent labels its dnspython resolver 'experimental', and it does not read /etc/hosts. dnspython's GitHub license shows NOASSERTION, but the LICENSE file holds two ISC-style notices (Dnspython Contributors; Nominum/Google).

dnspython is a pure-Python, feature-rich DNS toolkit (zone transfers, dynamic updates, TSIG, EDNS0) that gevent wraps with greenlets for async behavior, versus c-ares which is a native C library with its own event loop integration; no iterator/API compatibility with c-ares, and pure-Python parsing may not universally win on CPU-bound workloads.

## Maintenance

Actively maintained (last commit 2026-09-26; latest PyPI release 2.8.0 on 2025-09-07, 2.9.0 in development) and ISC-licensed pure Python with no required dependencies, so it is easy to adopt; gevent still labels its dnspython backend experimental.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification D, tier now C.
- **Tier reason:** Upgraded D-&gt;C: the listed changelog (gevent 1.3b1 Enhancements) has the no-numbers sentence verbatim, but the PR it cites, gevent PR #1088, has the gevent maintainer's timing tables for the gevent dnspython resolver against the gevent c-ares resolver, and the benchmark code is public (gevent benchmarks/bench_dns_resolver.py). It is not A: no CPU model, compiler or flags are given, only 'my macOS machine' and a local dnsmasq cache. It is not B: these are the integrator's own numbers, not peer-reviewed and not from an independent suite.
- **Verifier notes:** Metadata checked via gh graphql because REST returned 403 rate-limit: not archived, not a fork, 2,677 stars, last commit 2026-09-26 (active). LICENSE file read directly: ISC. Keep this as a flagged entry. The speed claim is disputed on the same PR page (a Linux rerun had c-ares faster), and the orchestrator may want to demote it if a clean win is required.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/gevent/gevent/master/docs/changelog_1_3.rst>
  - <https://github.com/gevent/gevent/pull/1088>
  - <https://github.com/gevent/gevent/issues/1103>
  - <https://raw.githubusercontent.com/gevent/gevent/master/benchmarks/bench_dns_resolver.py>
  - <https://raw.githubusercontent.com/gevent/gevent/master/docs/dns.rst>
  - <https://raw.githubusercontent.com/gevent/gevent/master/src/gevent/resolver/dnspython.py>
  - <https://github.com/rthalley/dnspython>
  - <https://raw.githubusercontent.com/rthalley/dnspython/main/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/rthalley/dnspython>
  - <https://raw.githubusercontent.com/rthalley/dnspython/main/README.md>
  - <https://raw.githubusercontent.com/rthalley/dnspython/main/pyproject.toml>
  - <https://raw.githubusercontent.com/rthalley/dnspython/main/dns/resolver.py>
  - <https://raw.githubusercontent.com/rthalley/dnspython/main/dns/asyncresolver.py>
  - <https://raw.githubusercontent.com/rthalley/dnspython/main/doc/whatsnew.rst>
  - <https://raw.githubusercontent.com/rthalley/dnspython/main/doc/threads.rst>
  - <https://raw.githubusercontent.com/rthalley/dnspython/main/doc/resolver-caching.rst>
  - <https://raw.githubusercontent.com/rthalley/dnspython/main/doc/resolver-class.rst>
  - <https://raw.githubusercontent.com/rthalley/dnspython/main/doc/async-resolver-class.rst>
  - <https://raw.githubusercontent.com/rthalley/dnspython/main/doc/async.rst>
  - <https://raw.githubusercontent.com/rthalley/dnspython/main/doc/resolver-override.rst>
  - <https://github.com/rthalley/dnspython/tree/main/doc>
  - <https://github.com/rthalley/dnspython/issues/259>
  - <https://github.com/rthalley/dnspython/issues/365>
  - <https://github.com/rthalley/dnspython/issues/1073>
  - <https://github.com/rthalley/dnspython/issues/1069>
  - <https://github.com/rthalley/dnspython/issues?q=slow>
  - <https://github.com/rthalley/dnspython/issues?q=performance>
  - <https://github.com/advisories/GHSA-3rq5-2g8h-59hc>
  - <https://pypi.org/pypi/dnspython/json>
  - <https://github.com/gevent/gevent/pull/1088>
  - <https://gist.githubusercontent.com/jamadden/b369cd5c5679969190481ef9ba7fd1b2/raw>
  - <https://github.com/gevent/gevent/issues/1103>
  - <https://raw.githubusercontent.com/gevent/gevent/master/benchmarks/bench_dns_resolver.py>
  - <https://raw.githubusercontent.com/gevent/gevent/1.3.7/benchmarks/bench_dns_resolver.py>
  - <https://raw.githubusercontent.com/gevent/gevent/master/src/gevent/resolver/dnspython.py>
  - <https://raw.githubusercontent.com/gevent/gevent/1.3.7/src/gevent/resolver/dnspython.py>
  - <https://raw.githubusercontent.com/gevent/gevent/master/src/gevent/resolver/ares.py>
  - <https://raw.githubusercontent.com/gevent/gevent/1.3.7/src/gevent/resolver/ares.py>
  - <https://raw.githubusercontent.com/gevent/gevent/master/docs/dns.rst>
  - <https://raw.githubusercontent.com/gevent/gevent/master/docs/changelog_1_3.rst>
  - <https://raw.githubusercontent.com/gevent/gevent/master/deps/c-ares/include/ares_version.h>
  - <https://raw.githubusercontent.com/c-ares/c-ares/main/docs/ares_init_options.3>
  - <https://hn.algolia.com/api/v1/search?query=dnspython&tags=story>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/rthalley/dnspython`) · [data/wave5/enrich/raw/github_com_rthalley_dnspython.json](../../../data/wave5/enrich/raw/github_com_rthalley_dnspython.json) (enrichment confidence 0.3)

</details>
