# Qbix Server (PHP webserver)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP servers and frameworks](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `PHP` · `MIT` · 🟢 active

> Pure-PHP HTTP/WebSocket server that forks copy-on-write workers after preloading the app, aimed at php-fpm's worker-count limit on I/O-bound PHP.

| | |
|---|---|
| **Beats** | php-fpm |
| **Claimed result** | 1,060 req/s (Qbix octane persistent workers) vs 78 req/s (php-fpm, 4 workers) under 50ms simulated I/O, c=40, same 200MB budget = \~13.6x (derived from page data; doc states '14x'). The worker count behind 1,060 is inconsistent: the BENCHMARKS.md table says 40 workers, but the same doc's summary and the README say 100 workers. |
| **Workload** | PHP request handling with a simulated 50ms I/O wait (usleep), c=40, measured with ab. php-fpm is held to 4 persistent workers on the assumption of 4 x 50MB = 200MB; Qbix octane runs COW-forked persistent workers in the same 200MB budget (40 per the table, 100 per the summary/README). Single-core container, PHP 8.3.6, Ubuntu 24. |
| **Metric** | throughput |
| **Hardware** | single-core container, Ubuntu 24, PHP 8.3.6; no CPU model stated |
| **Adoption** | 160 stars |
| **Last commit** | 2026-09-25 |
| **Links** | [repository](https://github.com/Qbix/webserver) · [benchmark](https://github.com/Qbix/webserver/blob/main/docs/BENCHMARKS.md) |

## Verdict

First-party ab runs on an unnamed single-core container (PHP 8.3.6, Ubuntu 24, no CPU model) with a usleep(50000) handler at c=40 give php-fpm, held to 4 workers by an assumed 50 MB each in 200 MB, 78 req/s vs 1,060 req/s for Qbix persistent workers (\~13.6x; the doc says 14x). That 1,060 cannot come from the stated setup, because at c=40 and at least 50 ms per request Little's law caps throughput at 40/0.05 = 800 req/s, and the docs variously give it as 40 or 100 workers, as '9x' with p50 56 ms, or as c=200; the doc's own c=200 run shows 358 vs 79 req/s (4.5x) with 200 workers.

## Use it when

- I/O-bound PHP (requests mostly wait on a database or API) on a RAM-limited Linux/macOS host where memory caps fpm's pm.max_children; the project's own c=200 test shows 3.4-8x fpm throughput with 200 workers vs 4.
- You want HTTP, WebSocket/Socket.IO rooms and SSE from one PHP process, without separate Node, Redis pub/sub or supervisor processes.
- Code you control and can audit for cross-request state (function-level statics, define(), unguarded class declarations), or scripts you can run in forkPerRequest mode.
- Small PHP apps you want to ship as one bundled binary (PHP + SQLite + app code).

## Skip it when

- CPU-bound or trivial handlers: fpm wins in the project's own tables (CPU-only 3,940 vs 2,609 req/s; CPU c=1 5,048 vs 2,818), and a user in issue #24 measured 134 vs 9,127 req/s against fpm on an `echo 'OK'` script (defaults at the time, fork-per-request).
- Static files: nginx did 50,742 vs 18,311 req/s in the same benchmark doc, and architecture.md itself recommends nginx or a CDN in front for static files.
- Production or large-scale use: the project is weeks old (v1.0.0 on 2026-08-31, v2.0.0 on 2026-09-25, 7 releases in 4 weeks). Recent issues include the master process dying with exit code 0 (#15), hangs under ab (#27) and truncated large downloads (#26), and at least 10 compat PRs (#39-#48) are still open.
- Legacy code that uses call_user_func('header', ...), eval(), code inside .phar files, or C extensions that send headers: the rewriter does not reach these, so they must go to php-cgi, which loses preload and COW. Fork-per-request mode measured only 96-115 req/s at 50 ms I/O.
- Windows: there is no pcntl. PHP runs in php-cgi subprocesses without preload or COW, or through an experimental FFI fork that uses the undocumented ntdll RtlCloneUserProcess. The README links a Windows .exe that the v2.0.0 release does not include.

## How it is fast

Fork-after-preload: the parent bootstraps the framework once, then calls pcntl_fork(), so workers share its pages copy-on-write and pay only for pages they dirty (docs quote 120 KB-5 MB private per worker, measured with /proc/smaps_rollup, vs \~42 MB per fpm worker). More workers per GB means more blocking requests in flight, so the gain is concurrency under I/O wait, not per-request speed. In persistent ('octane') mode a worker loops and restores class statics from a Reflection snapshot between requests (\~0.05 ms) instead of re-forking (\~8.8 ms). A single-threaded parent event loop (stream_select, or epoll/kqueue through PHP 8.6 Io\Poll) passes requests to workers over Unix socket pairs as length-prefixed JSON.

## Compared with alternatives

Every sibling (fasthttp, Drogon, H2O, Sogou Workflow and the others) is a non-PHP server that means rewriting the app, and each serves plain HTTP far faster; this one's static-file path reached only 36% of nginx's throughput on the same box. Pick Qbix only when the constraint is keeping an existing blocking-I/O PHP codebase and raising in-flight requests per GB of RAM compared with php-fpm.

## Integration

| | |
|---|---|
| **Form** | standalone server application: qbixserver.php from a source checkout, a \~280 KB phar, or a bundled static binary (Linux x86-64/aarch64, macOS arm64). It is not a library and not a FastCGI backend. |
| **Dependencies** | PHP with ext-sockets. ext-pcntl is required for workers, COW and signals; ext-openssl for TLS. Optional: revolt/event-loop, amphp/http-server (HTTP/2), and ext-ffi + qbix_fork.dll on Windows. |
| **Minimum toolchain** | PHP 8.1+ (composer.json). Benchmarks ran on PHP 8.3.6. epoll/kqueue needs PHP 8.6+ (Io\Poll); older versions use O(n) stream_select. |
| **Platforms** | Linux x86-64/aarch64, macOS and FreeBSD with COW fork. Windows x64 through php-cgi subprocesses (no COW) or the experimental FFI fork. iOS/Android through embedded PHP runtimes. |
| **Thread safety** | No threads. A single-threaded event-loop parent runs the server, and concurrency comes from forked worker processes. The docs require that the parent opens no DB connections or other stateful resources before forking. |
| **Drop-in for the baseline** | partial — it replaces the nginx + php-fpm pair as a whole (it reads .htaccess and has Laravel/Symfony/WordPress/Drupal presets), but it cannot sit behind nginx as a FastCGI replacement for fpm. Persistent mode also needs code with no cross-request state, and some calls bypass the shims. |

## Gotchas

- The docs disagree about the default mode: the README says persistent workers, while architecture.md, why.md and http.md say fork-per-request. In code, when pcntl is present and --workers is not set, it spawns max(4, min((RAM-1GB)/200KB, nproc\*200)) persistent workers. RAM comes from /proc/meminfo MemTotal, which is usually host RAM inside a container. A user in issue #27 got 3,200 workers using 22 GB that served no requests. Always set --workers.
- Persistent mode leaves define() constants, function-level statics, stream wrappers and C-extension state in place between requests. An inline class declaration fatals on the second request ('Cannot declare class'). Workers recycle every 1,000 requests by default (maxRequests). OPcache must stay off in CLI or use validate_timestamps=1, because it compiles rewritten source.
- Pool-dispatched PHP responses always send Connection: close, so dynamic responses get no keep-alive (maintainer in #27; Pool.php sets _keepAlive false). Pool.php also hard-codes remoteAddr '127.0.0.1' for pooled script requests, and an open PR (#43) fixes SCRIPT_NAME being set to the script's basename.
- Worker IPC is JSON. The worker exits on request messages over 10 MB, and writeMsg() calls json_encode() on the raw output body without an invalid-UTF-8 flag. Test binary (non-UTF-8) PHP output before relying on it; this comes from reading the code, not from a test.

## Known shortcomings

- Single-core container, no CPU model, no benchmark harness in the repo. The doc gives two worker counts behind 1,060 req/s (40 in the table, 100 in the summary/README); with 40 workers the figure exceeds the doc's own 800 req/s ceiling (40 x 20 req/s). php-fpm's 4-worker cap comes from an assumed (unmeasured) 50 MB per worker, while the doc elsewhere says \~42 MB. At c=200 the gain is only 4.5x (358 vs 79 req/s); php-fpm is faster on CPU-bound work and nginx on static files. The README's '100x more traffic' is about workers fitting in memory, not measured throughput. Baseline php-fpm is outside the category's listed baselines.
- The headline 1,060 req/s cannot hold: ab at c=40 with a 50 ms sleep per request caps throughput at 800 req/s by Little's law, whatever the worker count; the docs report that number four inconsistent ways (40 vs 100 workers, '9x' with p50 56 ms, c=200). The only self-consistent figure is 358 vs 79 req/s (4.5x) at c=200 with 200 workers. Counter-evidence: a user's wrk c=100 echo test (#24) measured Qbix 134 vs php-fpm 9,127 req/s (fork-per-request defaults at the time); the project's own tables have fpm winning CPU-bound work and nginx static files. The docs mischaracterize php-fpm (claims it leaks globals and re-bootstraps; HN disputed, citing OPcache) and quote per-worker memory three ways. Without --workers it spawns up to nproc x 200 workers sized from /proc/meminfo (host RAM in containers); a user got 3,200 idle workers using 22 GB (#27). Weeks old (v1.0.0 2026-08-31, v2.0.0 2026-09-25); master process dying with exit 0 (#15), hangs under ab (#27), truncated downloads (#26). Code reading: pooled responses always Connection: close, REMOTE_ADDR hard-coded to 127.0.0.1, JSON worker IPC with 10 MB cap, json_encode on raw bodies may fail on binary output.

## Caveats and trade-offs

The worker count is internally inconsistent. The table says 40 workers reached 1,060 req/s at 50ms I/O, but 40 workers x 20 req/s is a theoretical ceiling of 800 req/s, by the doc's own '4 workers x 20 req/s = 80' math. The summary and README say 100 workers. The fpm side is capped at 4 workers by an assumed 50MB/worker budget; fpm was not measured running out of memory, and the doc elsewhere gives \~42MB/worker, or \~24 workers/GB. The same page's c=200 test shows a smaller gain at 50ms I/O: 358 vs 79 req/s (4.5x), with 200 octane workers. On CPU-bound work fpm beats octane (469 vs 439, 3,940 vs 2,609 and 5,048 vs 2,818 req/s). On static files nginx beats Qbix (50,742 vs 18,311 req/s). The repo description's 'Handle over 100x more traffic' refers to worker density, not measured throughput; the best measured throughput gain is \~14x. The I/O is simulated with usleep. No CPU model is stated.

Relies on pcntl_fork() (Unix/Linux only, no Windows); the memory/worker-count advantage under I/O-bound load is the whole story, not raw per-request latency; on CPU-bound work it loses to Swoole (439 vs 483 req/s) and roughly ties php-fpm.

## Maintenance

Very active but very young: first HN post July 2026, v1.0.0 to v2.0.0 in under 4 weeks, 160 stars, and scope growing into mesh networking and mobile. It is MIT-licensed and runs as its own server process rather than a vendored library.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** docs/BENCHMARKS.md has first-party ab numbers against php-fpm (the 'Octane scaled' table gives 1,060 req/s for Qbix vs 78 req/s for fpm at 50ms I/O, c=40, labelled '14x'), measured on an unnamed 'single-core container, PHP 8.3.6, Ubuntu 24' with no CPU model. The repo has no dedicated benchmark harness (tests/ holds only functional tests), so it cannot be A, and it is not independent, so it cannot be B.
- **Verifier notes:** The numbers are on the page and the comparison is against php-fpm, a recognizable incumbent, so tier C stands. Metadata checks out via GraphQL: MIT, 160 stars, not a fork or archived, last commit 2026-09-25. The REST API was rate-limited, so GraphQL and raw.githubusercontent were used. The caveats were rewritten to flag the 40-vs-100-worker inconsistency and that the 1,060 req/s figure exceeds the 40-worker theoretical ceiling.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/Qbix/webserver>
  - <https://github.com/Qbix/webserver/blob/main/docs/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/Qbix/webserver/main/docs/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/Qbix/webserver/main/README.md>
- **Sources the enricher read:**
  - <https://github.com/Qbix/webserver>
  - <https://raw.githubusercontent.com/Qbix/webserver/main/README.md>
  - <https://raw.githubusercontent.com/Qbix/webserver/main/docs/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/Qbix/webserver/main/composer.json>
  - <https://raw.githubusercontent.com/Qbix/webserver/main/docs/architecture.md>
  - <https://raw.githubusercontent.com/Qbix/webserver/main/docs/why.md>
  - <https://raw.githubusercontent.com/Qbix/webserver/main/docs/reset.md>
  - <https://raw.githubusercontent.com/Qbix/webserver/main/docs/http.md>
  - <https://raw.githubusercontent.com/Qbix/webserver/main/docs/running.md>
  - <https://raw.githubusercontent.com/Qbix/webserver/main/docs/configuration.md>
  - <https://raw.githubusercontent.com/Qbix/webserver/main/docs/compatibility.md>
  - <https://raw.githubusercontent.com/Qbix/webserver/main/qbixserver.php>
  - <https://raw.githubusercontent.com/Qbix/webserver/main/src/Q/WebServer.php>
  - <https://raw.githubusercontent.com/Qbix/webserver/main/src/Q/WebServer/Pool.php>
  - <https://raw.githubusercontent.com/Qbix/webserver/main/src/Q/WebServer/Fork.php>
  - <https://raw.githubusercontent.com/Qbix/webserver/main/src/fork_shim.c>
  - <https://github.com/Qbix/webserver/issues/15>
  - <https://github.com/Qbix/webserver/issues/24>
  - <https://github.com/Qbix/webserver/issues/26>
  - <https://github.com/Qbix/webserver/issues/27>
  - <https://github.com/Qbix/webserver/pulls>
  - <https://github.com/Qbix/webserver/releases/tag/v2.0.0>
  - <https://hn.algolia.com/api/v1/search?query=qbix%20server&tags=story>
  - <https://hn.algolia.com/api/v1/search?query=Qbix%2Fwebserver>
  - <https://news.ycombinator.com/item?id=49749789>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/qbix/webserver`) · [data/wave5/enrich/raw/github_com_qbix_webserver.json](../../../data/wave5/enrich/raw/github_com_qbix_webserver.json) (enrichment confidence 0.3)

</details>
