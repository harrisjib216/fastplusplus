# CppCMS

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP servers and frameworks](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> C++11 web framework (FastCGI/SCGI/HTTP) with trigger-invalidated page cache; 2008 first-party case study shows \~41x uncached WordPress throughput.

| | |
|---|---|
| **Beats** | WordPress on PHP 5.2 (lighttpd 1.4.13 + FastCGI, MySQL 5.0, WP-Cache-2); also Java Servlets/JSP blog in the project's other case study |
| **Claimed result** | Snippet only (cppcms.com blocked). benchmarks_php, no cache: CppCMS 310 fetches/s vs WordPress 7.6 fetches/s, about 41x (derived from page data); warm-up 0.28 s vs 13.0 s. Cache miss-ratio table (fetches/s, CppCMS vs WordPress): 0% 2300 vs 711 (about 3.2x, derived); 3% 1940 vs 176 (about 11x, derived; the page states 'more than 10 times' at 3%); 40% 570 vs 13 (about 44x, derived). The page's own wording is that PHP performance drops very fast once the miss ratio reaches a few percent. Separate case study benchmarks_all (CppCMS 0.99.3 vs PHP 5.2.6 on lighttpd/FastCGI, Mono 2.6.7 Asp.Net, JSP on Tomcat 6.0.18): at 0% miss CppCMS 3200.73 req/s vs PHP 974.142, JSP/Tomcat 821.887, Mono 747.164 (about 3.3x-4.3x, derived from page data); PHP used almost 3x and Java Servlets almost 30x the memory of CppCMS. |
| **Workload** | Full blog application (database access, text formatting, comment sanitation, caching) served through FastCGI, measured in page fetches per second with no cache and with varying cache miss ratios, CppCMS blog versus WordPress. |
| **Metric** | throughput |
| **Hardware** | AMD Athlon XP 64bit, 1 GB RAM |
| **Adoption** | 528 stars |
| **Last commit** | 2025-12-18 |
| **Links** | [repository](https://github.com/artyom-beilis/cppcms) · [benchmark](http://cppcms.com/wikipp/en/page/benchmarks_php) |

## Verdict

In a first-party, roughly 2008 case study on an AMD Athlon XP 64 with 1 GB RAM (Debian Etch; compiler and flags not stated), a CppCMS blog served 310 fetches/s uncached against 7.6 for WordPress 2.5 on PHP 5.2 with XCache behind lighttpd/FastCGI (about 41x, derived from page data), and 2300 vs 711 fetches/s at 0% cache miss, 1940 vs 176 at 3% and 570 vs 13 at 40% against WordPress with WP-Cache-2 (about 3.2x, 11x and 44x, derived). A second case study (CppCMS 0.99.3 vs PHP 5.2.6, Mono 2.6.7 and JSP on Tomcat 6.0.18) shows about 3.3-4.3x at 0% miss; all figures come from search snippets of blocked pages.

## Use it when

- Read-heavy content sites (blogs, wikis, news) whose pages can be cached with trigger invalidation: the case study's gap widens as the cache miss ratio rises (3% miss: 1940 vs 176 fetches/s against WordPress with WP-Cache-2, snippet only).
- Deployments that already run nginx, lighttpd or Apache and want a compiled application behind FastCGI or SCGI rather than a standalone server.
- Memory-constrained hosts: the benchmarks_all case study reports Java/Tomcat and Mono/Asp.Net using one or two orders of magnitude more memory than CppCMS (snippet only).
- Projects pinned to C++11 that need an MIT-licensed framework with sessions, forms, localisation (Booster.Locale) and caching in one package.

## Skip it when

- You need WebSocket or HTTP/2: neither is documented, and issue #97 ('Does cppcms support websockets?', 2023-02-13) has no maintainer answer.
- You want an actively developed ecosystem: the last commits are a 2.0.1 version bump (2025-11-02) and a CMake 4 fix (2025-12-18) after gaps of a year or more, and 40 issues are open, several unanswered since 2019-2021.
- You need evidence against a modern C++ framework or server: the only numbers compare a 2008-era CppCMS blog with WordPress 2.5 on PHP 5.2, and with Java/C#/PHP blogs in a separate case study; there is no comparison with nginx, Drogon or other C++ frameworks.
- Your traffic is mostly uncacheable per-user pages: the large ratios come from the cache-miss scenarios against a slow PHP baseline, and the cached 0% miss case is only about 3.2x.
- Windows deployments that need multiple worker processes: service.cpp throws 'Prefork is not supported under Windows and Cygwin'.

## How it is fast

Application logic and templates are compiled C++ rather than interpreted. The built-in cache (cache_interface: fetch_page/store_page/fetch_frame) invalidates by triggers: every fragment fetched while building a page adds its key as a dependency, and rise("article_123") drops every page that used it, so pages stay cached until their data actually changes. Cached pages are stored already gzip-compressed (separate _Z:/_U: keys), the cache lives in process-shared memory when worker processes are preforked (shmem_allocator) or in a separate TCP cache server, and connections are handled by a booster::aio reactor (epoll, kqueue, /dev/poll, poll or select) that hands synchronous requests to a worker thread pool.

## Compared with alternatives

Pick CppCMS over Drogon or Sogou Workflow when you deploy behind an existing server via FastCGI/SCGI, want the trigger-invalidated page and fragment cache, or must stay on C++11; pick Drogon for WebSocket, async database clients, coroutines and active maintenance, and note that Qbix Server is the catalogued option if the goal is only to speed up an existing PHP stack rather than rewrite it in C++.

## Integration

| | |
|---|---|
| **Form** | shared lib and static lib (both built by default), plus the bundled Booster library |
| **Dependencies** | Python at build time (CMake aborts without it; it runs the template compiler); optional zlib (gzip output), OpenSSL or libgcrypt (AES session encryption), ICU, PCRE and iconv (Booster locale and regex) |
| **Minimum toolchain** | C++11 (-std=c++11 set for GCC, Clang and Intel; MSVC supported); CMake 3.5+, CMake 4 compatible since 2025-12-18 |
| **Platforms** | Linux, FreeBSD, NetBSD, Solaris (SunOS flags in CMakeLists) and Windows (MSVC, MinGW, Cygwin; no prefork there); reactor selectable among epoll, kqueue, /dev/poll, poll and select |
| **Thread safety** | applications_pool is documented as thread safe; synchronous applications are created by the pool and run on the worker thread pool (optionally thread_specific), while an asynchronous application is a single instance running in the event-loop thread. |
| **Drop-in for the baseline** | no |

## Gotchas

- Evidence is snippet only: cppcms.com is blocked here, so benchmarks_php and benchmarks_all were read through WebSearch summaries. This session's summary lists lighttpd 1.4.13, FastCGI, PHP 5.2, XCache 1.2.1, MySQL 5.0, WP-Cache-2 with the author's patch, Athlon XP 64 with 1 GB RAM on Debian Etch, and gives WordPress 711 fetches/s at 0% miss (an earlier summary printed 71) plus a 5% row of 1790 vs 118.
- Harness limits: it compares two different blog applications (language, data access and cache design all differ), so it does not isolate framework overhead; benchmarks_all used only 1000 requests at a maximum concurrency of 5 per data point (snippet), and that page itself says the C#, Java and PHP implementations behaved very similarly.
- The benchmarked blog is not in the GitHub repo: it lives in the project's SourceForge SVN (blog/trunk, last changed 2012-02-01), and neither the revision tested nor the compiler and flags are stated.
- Cached pages are stored per encoding (gzip and plain under separate keys), so a page requested by both kinds of client occupies the cache twice; templates are compiled C++, so view changes need a rebuild (or a rebuilt view shared library).

## Known shortcomings

- Evidence is search-result text only (cppcms.com blocked, page never opened): first-party numbers from about 2008 against WordPress (a PHP application, not a C++ framework), no compiler, flags or code; search results disagree on the WordPress 0% miss figure (71 or 711); the 'order of magnitude over JSP/PHP' claim is not supported by benchmarks_all, which shows about 3.3x-4.3x at 0% miss.
- Enricher: the WordPress comparison (711 req/s at 0% cache miss, 1790 vs 118 at 5%) is an app-vs-app test on lighttpd 1.4.13, PHP 5.2, XCache 1.2.1, MySQL 5.0 and Debian Etch, seen as a search snippet only (cppcms.com blocked); benchmarks_all ran 1000 requests at concurrency 5 per point; the blog code is in SourceForge SVN (2012) with revision and flags unstated. Maintenance sparse (2.0.1 2025-11, CMake 4 fix 2025-12); no WebSocket support (issue #97 unanswered).

## Caveats and trade-offs

SNIPPET ONLY: cppcms.com and blog.cppcms.com are blocked by the egress proxy, so benchmarks_php and benchmarks_all were never opened; figures come from WebSearch result summaries. The summaries disagree: one printed WordPress 71 fetches/s at 0% miss and a scaled-down column (37, 17, 11 ...), another printed 71 at 0% followed by 370 at 1%, 176 at 3%, 118 at 5%; 711 at 0% is the reading consistent with the 1% row and with the page's 'more than 10 times at 3%' statement (1940/176), but it was not seen on the page. Both summaries print identical 40% and 50% rows (570 vs 13), so the 50% row is uncertain and only the 40% row is used. One earlier summary printed 3,100 fetches/s for the no-cache CppCMS figure; 310 repeated in two summaries. First-party, roughly 2008-2010 era numbers (WordPress 2.5, PHP 5, Athlon XP 64) comparing two different blog applications, not a controlled framework microbenchmark; the PHP side is WordPress with a WP-Cache-2 plugin patched by the author. The earlier claim that the CppCMS blog beats JSP and PHP blogs by an order of magnitude was not supported by the summaries: the benchmarks_all case study shows about 3.3x-4.3x at 0% miss and says the C#, Java and PHP implementations behaved similarly; the order-of-magnitude statement there concerns memory (Java/Tomcat and Mono). The record's lighttpd 1.4.13 and MySQL 5.0 versions were not seen in any summary (benchmarks_all names PHP 5.2.6 with lighttpd and FastCGI). Compiler, flags and benchmark code (the blog application) are not in the CppCMS repo. The 'LGPLv3' tag in the awesome-cpp list is outdated: README and COPYING.TXT say MIT since 1.2. Baseline is a PHP application, not a C++ incumbent. Cap at C.

Applications are compiled C++ with a template-to-C++ view compiler, so no scripting-style edit-and-reload; smaller ecosystem than PHP/Java; needs the bundled Booster library and a FastCGI/SCGI/HTTP front end.

## Maintenance

Slowly maintained rather than active (version 2.0.1 in November 2025 and a CMake 4 fix in December 2025, otherwise sparse commits since 2020) and MIT-licensed since 1.2; usable as a built library, but the performance evidence is a 2008-era app-vs-PHP comparison read only through search snippets.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party wiki case study (benchmarks_php) comparing a CppCMS blog with WordPress 2.5 plus a patched WP-Cache-2 on an AMD Athlon XP 64bit with 1 GB RAM; no compiler or flags and no benchmark code in the repo. cppcms.com is EGRESS_BLOCKED here, so numbers were checked against WebSearch summaries only (snippet only), which caps it at C.
- **Verifier notes:** Real, maintained project (MIT, 528 stars, last commit 2025-12-18). Shortcomings: snippet-only evidence because cppcms.com is blocked; first-party, \~2008-era, app-vs-app comparison with a PHP baseline, no compiler/flags/code; summaries disagree on the WordPress 0% miss value (71 vs 711) and the order-of-magnitude claim over JSP/PHP was not supported (benchmarks_all shows about 3.3x-4.3x at 0% miss). claimed_speedup and caveats rewritten accordingly.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** reachable benchmark page with hardware and flags; enricher snippet check
- **Pages the verifier opened:**
  - <https://github.com/artyom-beilis/cppcms>
  - <https://github.com/artyom-beilis/cppcms/commits>
  - <https://raw.githubusercontent.com/artyom-beilis/cppcms/HEAD/README.md>
  - <https://raw.githubusercontent.com/artyom-beilis/cppcms/HEAD/COPYING.TXT>
- **Sources the enricher read:**
  - <https://github.com/artyom-beilis/cppcms>
  - <https://github.com/artyom-beilis/cppcms/commits/master>
  - <https://github.com/artyom-beilis/cppcms/tree/master/src>
  - <https://github.com/artyom-beilis/cppcms/issues>
  - <https://github.com/artyom-beilis/cppcms/issues/97>
  - <https://raw.githubusercontent.com/artyom-beilis/cppcms/HEAD/README.md>
  - <https://raw.githubusercontent.com/artyom-beilis/cppcms/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/artyom-beilis/cppcms/HEAD/booster/CMakeLists.txt>
  - <https://raw.githubusercontent.com/artyom-beilis/cppcms/HEAD/cppcms/cache_interface.h>
  - <https://raw.githubusercontent.com/artyom-beilis/cppcms/HEAD/cppcms/applications_pool.h>
  - <https://raw.githubusercontent.com/artyom-beilis/cppcms/HEAD/src/cache_interface.cpp>
  - <https://raw.githubusercontent.com/artyom-beilis/cppcms/HEAD/src/cache_storage.cpp>
  - <https://raw.githubusercontent.com/artyom-beilis/cppcms/HEAD/src/service.cpp>
  - <https://raw.githubusercontent.com/artyom-beilis/cppcms/HEAD/src/http_api.cpp>
  - <https://raw.githubusercontent.com/artyom-beilis/cppcms/HEAD/src/thread_pool.cpp>
  - <https://sourceforge.net/p/cppcms/code/HEAD/tree/>
  - <https://sourceforge.net/p/cppcms/code/HEAD/tree/blog/>
  - http://cppcms.com/wikipp/en/page/benchmarks_php (EGRESS_BLOCKED; WebSearch snippet only)
  - https://cppcms.com/wikipp/en/page/benchmarks_all (not opened; WebSearch snippet only)
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/artyom-beilis/cppcms`) · [data/wave5/enrich/raw/github_com_artyom_beilis_cppcms.json](../../../data/wave5/enrich/raw/github_com_artyom_beilis_cppcms.json) (enrichment confidence 0.6)

</details>
