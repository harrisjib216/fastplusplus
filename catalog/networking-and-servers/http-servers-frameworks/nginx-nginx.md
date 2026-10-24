# NGINX

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP servers and frameworks](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `BSD-2-Clause` · 🟢 active

> Event-driven C web server and reverse proxy; served a small static page at 1.9-3.2x Apache httpd's request rate.

| | |
|---|---|
| **Beats** | Apache httpd (Apache2, version and MPM not stated on the benchmark page) |
| **Claimed result** | Requests/sec: NGINX Default 116415.16 vs Apache2 62124.60, about 1.9x (derived from page data); NGINX Tuned 201407.17 vs Apache2 62124.60, about 3.2x (derived from page data). Average latency: NGINX Default 4.24 ms and Tuned 2.40 ms vs Apache2 178.92 ms. Cross-check in a second third-party run (ApacheBench in Docker, nginx 1.11.8 vs Apache 2.4.25 event MPM, concurrency 50): 20166.17 vs 16951.31 req/s with keep-alive (+19%), 5454.22 vs 4827.32 req/s without (+13%). |
| **Workload** | wrk with 12 threads and 500 connections for 5 s against the same static page on localhost (no file name or size given); requests/sec and latency for NGINX default config, NGINX tuned config (denji/nginx-tuning) and Apache2; best of three runs. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-8550U at 1.80 GHz, 8 CPUs, about 25.1 GB RAM, Linux kernel 5.17.5 x86_64 |
| **Compiler and flags** | Not stated (no build flags; nginx and Apache versions and configs not given on the page; load command: wrk -c 500 -t 12 -d 5s http://127.0.0.1:8081/ for NGINX, wrk -c 500 -t 12 -d 5 http://127.0.0.1:80/ for Apache2) |
| **Adoption** | 32k stars (official nginx/nginx repository) |
| **Last commit** | 2026-10-23 |
| **Links** | [repository](https://github.com/nginx/nginx) · [benchmark](https://github.com/mufeedvh/binserve/blob/master/BENCHMARKS.md) |

## Verdict

binserve's BENCHMARKS.md ran wrk (12 threads, 500 connections, 5 s, best of three) against one small static page over localhost on a Core i7-8550U laptop with Linux 5.17.5: NGINX default 116,415 req/s and NGINX tuned 201,407 req/s against Apache2 at 62,125 req/s (1.9x and 3.2x, derived from page data), with nginx and Apache versions, configs, MPM and build flags not stated, and the Apache row internally inconsistent (178.92 ms mean latency at that rate). A 2016 gist (ab -c 50, Docker images, nginx 1.11.8 with 4 workers vs stock Apache 2.4.25 event MPM, hardware not stated) found nginx 19% ahead with keep-alive and 13% without.

## Use it when

- Serving static files or small cached responses to many concurrent keep-alive clients, the case the binserve and gist runs measure.
- Reverse proxy, TLS termination and load balancing in front of application servers (FastCGI, uwsgi, HTTP upstreams) where a large, well-documented directive set and module ecosystem matter more than the last few percent of throughput.
- Replacing a prefork or thread-per-connection Apache setup that runs out of workers under many idle or slow connections.
- Edge caching and rate limiting with shared-memory zones across workers, without adding a separate cache tier.

## Skip it when

- You rely on .htaccess, mod_rewrite rule files edited per directory, or in-process modules such as mod_php: NGINX has no per-directory overrides and needs a reload for config changes.
- Maximum req/s per core on micro-benchmarks is the only goal: catalog siblings such as H2O, Kore, libuhttpd and Sogou Workflow report higher numbers than nginx on their own tests.
- Dynamic, API-driven configuration at runtime (service-mesh xDS style): the open-source build reloads config files; Envoy or Pingora-based proxies fit that model better.
- Windows production hosts: the README calls the Windows build a proof of concept for development and testing only.
- You want to drop in third-party modules freely: a module is either compiled into the binary or built as a dynamic module for your nginx build, so every addition means a rebuild or a matching package.

## How it is fast

A master process reads the config and manages a fixed set of single-threaded worker processes (worker_processes, auto matches the core count), each running a non-blocking event loop over epoll (or kqueue), so thousands of keep-alive connections cost a small connection struct each rather than a thread or process. Accept load can be spread with per-worker SO_REUSEPORT listening sockets (listen ... reuseport) or EPOLLEXCLUSIVE wakeups, with accept4 and SOCK_NONBLOCK; the accept_mutex is off by default. Per-request memory comes from region pools (ngx_pool_t, 16 KB default blocks, freed all at once when the request ends), static files go out with zero-copy sendfile (optionally offloaded to thread pools), and the HTTP request-line parser is a hand-written byte state machine that matches method names with single 32-bit compares on little-endian CPUs.

## Compared with alternatives

Pick NGINX over H2O, Kore or libuhttpd when you need the broadest module set, documentation and packaging for static files plus reverse proxying, even if those servers post higher micro-benchmark numbers; over Envoy when plain HTTP/1 proxy throughput matters (Envoy ran at 0.77x of NGINX in Proxy-Benchmarks); prefer Pingora only if you will write the proxy logic in Rust.

## Integration

| | |
|---|---|
| **Form** | standalone server binary (official packages, or built from source with auto/configure and make); modules are static or dynamic shared objects |
| **Dependencies** | Minimal build per README: a C compiler (gcc), make, PCRE (libpcre3-dev) for rewrites and regex locations, zlib for gzip; OpenSSL (libssl-dev) for TLS; more for optional modules. |
| **Minimum toolchain** | Any C compiler supported by auto/configure (README shows GCC); no C standard version documented in the files read |
| **Platforms** | Linux (epoll; the Linux sendfile path requires sendfile64), FreeBSD and other kqueue systems; Windows build is proof-of-concept only |
| **Thread safety** | Multi-process: each worker process is single-threaded with its own event loop; workers share state only through configured shared-memory zones; optional thread pools handle blocking file I/O (aio threads, sendfile offload) |
| **Drop-in for the baseline** | partial — covers Apache's static file, reverse proxy and TLS roles, but needs a rewritten configuration; no .htaccess, mod_php or Apache module compatibility |

## Gotchas

- Out-of-the-box config is conservative: the repository's conf/nginx.conf sets worker_processes 1 and worker_connections 1024, and the compiled-in defaults are 1 worker and 512 connections, so a 'default NGINX' benchmark row can mean one worker; the binserve page does not say which default it ran.
- The binserve 'Tuned' row follows denji/nginx-tuning (worker_processes auto, multi_accept on, access_log off, open_file_cache, keepalive_requests 100000), while Apache2 shows no tuning, so the 3.2x figure is tuned against apparently stock; the like-for-like default row is 1.9x.
- In the 2016 gist cross-check, the author notes the nginx HTTP/1.0 run was limited by docker-proxy, so the +13% non-keep-alive gap is bounded by Docker's userland port proxy rather than the servers; nginx also served a 612 B page against Apache's 45 B page and was raised to 4 workers.
- Security fixes arrive in batches on both branches: October 2026's 1.31.7 and 1.30.6 fixed five CVEs (buffer overflows in alias-with-rewrite and string expressions, HTTP/3 request body injection, TLS session-ticket rotation, SSI with AIO use-after-free), and September's releases fixed an HTTP/3 buffer overflow; stay on a current stable or mainline release.

## Known shortcomings

- Verifier: binserve's Apache2 row fails a Little's law check (62,124 req/s at 178.92 ms mean needs about 11,100 requests in flight on 500 connections); wrk ran on the same laptop CPU; the 2016 gist tuned nginx to 4 workers against stock Apache.
- 3.2x row is tuned NGINX against apparently stock Apache; 1.9x is the like-for-like default row

## Caveats and trade-offs

No first-party benchmark in the nginx repository: its README has no performance content and does not mention Apache. The numbers come from the README-linked BENCHMARKS.md of binserve (a competing Rust static server, MIT), which publishes the NGINX and Apache2 rows only as reference baselines for its own results. Tier C: CPU, OS and wrk commands are stated, but nginx and Apache versions, config files, served file, MPM and compiler flags are not given, so it is not reproducible. wrk ran on the same 8-thread laptop CPU (i7-8550U, 15 W mobile part with turbo) as the servers, over localhost. Apache2 ran on port 80 and NGINX on 8081 (possibly an untuned distro Apache against nginx), and the Apache2 row is internally inconsistent: 62,124.60 req/s at a 178.92 ms mean latency would need about 11,100 requests in flight while wrk held 500 connections (Little's law, derived from page data; the NGINX rows give about 480-490, consistent), with stdev 244 ms and max 804 ms, so it reflects stalled or queued connections (e.g. a worker or connection limit) rather than a clean steady-state measurement. Runs are 5 s, best of three. The tuned NGINX row uses an outside tuning guide (denji/nginx-tuning). The cross-check at https://gist.github.com/lukassup/d5ad12753ee13325b177429db01e0258 (last active Dec 2016; nginx 1.11.8 with worker_processes raised to 4 vs stock Apache 2.4.25 event MPM, both from Docker images reached on localhost:8080, single-threaded ab at concurrency 50, no CPU stated) is dated and asymmetrically tuned; nginx served its 612 B welcome page against Apache's 45 B page, httpd had 189 failed requests (length mismatches) in the keep-alive run, and the author's note that nginx's page is the smaller one contradicts the measured lengths; the gap there is only 13-19%. The listed lead in the book (Software Architecture with C++, 2nd ed., ch. 4) calls NGINX an HTTP accelerator / cache, with no numbers. Search snippets (not opened pages) point to other 2026 blog comparisons with nginx ahead on static files at high concurrency, but those hosts were unreachable. [retier] Enricher: the repo's conf/nginx.conf sets worker_processes 1 and the compiled-in defaults are 1 worker and 512 connections; the binserve page does not say which 'default' it ran. The 'Tuned' row follows the denji tuning guide (access_log off, open_file_cache, keepalive_requests 100000) while Apache shows no tuning, so 3.2x is tuned against apparently stock; 1.9x is the like-for-like default row. In the cross-check gist the author says the HTTP/1.0 run was limited by docker-proxy, so its +13% is capped by Docker's port proxy, not by the servers.

Event-driven master/worker design with a small, mostly flat per-connection memory footprint, so it suits many idle or slow connections; dynamic content goes through proxy/FastCGI/uwsgi upstreams rather than in-process modules like mod_php. No per-directory .htaccess override, so configuration is central and needs a reload. Most third-party modules must be compiled in or built as dynamic modules against the same nginx version and flags. Written in C, so memory-safety bugs are possible.

## Maintenance

Actively developed by F5 under BSD-2-Clause (32.0k stars, mainline 1.31.8 released Oct 21, 2026, master at 1.31.9) with separate stable and mainline branches and an F5 security process; ships as packages for most Linux distributions.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** binserve BENCHMARKS.md shows NGINX Default/Tuned and Apache2 wrk rows with CPU model and wrk commands, but no nginx or Apache version, config, MPM, served file or build details; a competitor's quick reference run, not a well-known suite and not reproducible, so C. The 2016 ab gist cross-check is also partial (no hardware, asymmetric tuning).
- **Verifier notes:** All binserve and gist numbers match the record (1.9x and 3.2x derive correctly; +19%/+13% match the gist). Added harness caveats: Apache2 row fails a Little's law check, wrk co-located on a laptop CPU, gist nginx tuned to 4 workers vs stock Apache. Metadata (BSD-2-Clause, 32.0k stars, last commit 2026-10-23) checked.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-84 (wave 5 book seed pass, 2026-10-24); enrichment (wave 5 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/mufeedvh/binserve/HEAD/BENCHMARKS.md>
  - <https://gist.github.com/lukassup/d5ad12753ee13325b177429db01e0258>
  - <https://github.com/nginx/nginx>
  - <https://github.com/nginx/nginx/commits/master>
- **Sources the enricher read:**
  - <https://github.com/nginx/nginx>
  - <https://raw.githubusercontent.com/nginx/nginx/HEAD/README.md>
  - <https://raw.githubusercontent.com/nginx/nginx/HEAD/SECURITY.md>
  - <https://raw.githubusercontent.com/nginx/nginx/HEAD/CONTRIBUTING.md>
  - <https://raw.githubusercontent.com/nginx/nginx/HEAD/conf/nginx.conf>
  - <https://raw.githubusercontent.com/nginx/nginx/HEAD/src/core/nginx.h>
  - <https://raw.githubusercontent.com/nginx/nginx/HEAD/src/core/nginx.c>
  - <https://raw.githubusercontent.com/nginx/nginx/HEAD/src/core/ngx_palloc.h>
  - <https://raw.githubusercontent.com/nginx/nginx/HEAD/src/event/ngx_event.h>
  - <https://raw.githubusercontent.com/nginx/nginx/HEAD/src/event/ngx_event.c>
  - <https://raw.githubusercontent.com/nginx/nginx/HEAD/src/event/ngx_event_accept.c>
  - <https://raw.githubusercontent.com/nginx/nginx/HEAD/src/event/modules/ngx_epoll_module.c>
  - <https://raw.githubusercontent.com/nginx/nginx/HEAD/src/os/unix/ngx_process_cycle.c>
  - <https://raw.githubusercontent.com/nginx/nginx/HEAD/src/os/unix/ngx_linux_sendfile_chain.c>
  - <https://raw.githubusercontent.com/nginx/nginx/HEAD/src/http/ngx_http_parse.c>
  - <https://github.com/nginx/nginx/releases>
  - <https://github.com/nginx/nginx/security/advisories>
  - <https://raw.githubusercontent.com/mufeedvh/binserve/HEAD/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/denji/nginx-tuning/HEAD/README.md>
  - <https://gist.github.com/lukassup/d5ad12753ee13325b177429db01e0258>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/nginx/nginx`) · [data/wave5/enrich/raw/github_com_nginx_nginx.json](../../../data/wave5/enrich/raw/github_com_nginx_nginx.json) (enrichment confidence 0.75)

</details>
