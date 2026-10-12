# Granian

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP servers and frameworks](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `BSD-3-Clause` · 🟢 active

> Rust (hyper + tokio) HTTP server for Python ASGI/WSGI/RSGI apps, with higher single-worker throughput than Uvicorn and Gunicorn.

| | |
|---|---|
| **Beats** | Uvicorn (httptools and h11 protocols) running on uvloop |
| **Claimed result** | 125,539 RPS (Granian ASGI) vs 14,501 RPS (Uvicorn H11 on uvloop) = \~8.66x; vs 51,051 RPS (Uvicorn Httptools on uvloop) = \~2.46x (derived from page data) |
| **Workload** | ASGI HTTP GET request returning a 10KB static plain-text response, benchmarked with `oha` at concurrency 128 for 10s (after a primer/warmup run), single worker/thread, HTTP/1.1; all async servers including the baseline use uvloop as the asyncio event loop. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 7 5700X, 16 CPUs, Gentoo Linux 6.18.41 |
| **Compiler and flags** | Rust (rustc version not stated), built with `maturin build --release --features jemalloc` (benchmarks/runbench.sh); Cargo [profile.release] lto="fat", panic="abort", strip=true; .cargo/config.toml rustflags --cfg pyo3_disable_reference_pool; Python 3.13 venv |
| **Adoption** | 5.7k stars |
| **Last commit** | 2026-09-13 |
| **Links** | [repository](https://github.com/emmett-framework/granian) · [benchmark](https://github.com/emmett-framework/granian/blob/c0b1e0b9ba8349e2451b1b688037d8d79e4693b4/benchmarks/vs.md) |

## Verdict

The project's own benchmarks/vs.md (run 2026-08-05; Granian 2.8.1 built with maturin --release, jemalloc and fat LTO; Python 3.13; AMD Ryzen 7 5700X, Gentoo Linux) tested an ASGI GET returning a static 10 KB body. It used oha at 128 connections for 10 s, one worker and one runtime thread, HTTP/1.1, every async server on uvloop and Uvicorn's access log off. Granian reached 125,539 RPS vs 51,051 for Uvicorn+httptools (\~2.46x) and 14,501 for Uvicorn+h11 (\~8.66x). Each number is a single run, and the competing servers were whatever versions were latest on that date.

## Use it when

- Python ASGI services where the server's HTTP layer is a large share of per-request cost, such as fast handlers returning in-memory bodies. vs.md, 10 KB GET, one worker: 125,539 RPS vs 51,051 for Uvicorn+httptools.
- WSGI apps (Django, Flask) now on Gunicorn gthread/gevent or uWSGI. vs.md, 10 KB GET at c64: Granian WSGI 125,824 RPS vs 9,175-12,204 for those servers.
- Serving a Python app directly over HTTP/2. vs.md: 129,750 RPS vs 7,327 for Hypercorn.
- Replacing the Gunicorn + uvicorn + httptools stack with one prebuilt wheel. Wheels cover Windows, aarch64/armv7 Linux, musl, PyPy 3.11 and free-threaded CPython 3.14t/3.15t.
- Serving static assets or large files next to the app without passing them through Python (static-path mounts, pathsend streaming; \~50 KB file: 48,049 vs 30,004 RPS for Uvicorn+httptools).

## Skip it when

- I/O-bound apps whose handlers spend milliseconds waiting on a database or upstream. With 10 ms waits at c512, vs.md has Granian ASGI at 45,859 RPS vs 43,903 for Uvicorn+httptools (\~4%), and 100 ms waits are a tie, so the app is the bottleneck.
- Apps built on trio or gevent, or apps that need ASGI extensions Granian has not implemented (README; issue #93, TLS extension #788 still open).
- Teams that need a pure-Python server they can patch or step through in a debugger. The README says Granian is not the choice for advanced debugging.
- Heavy WebSocket broadcast with many clients per worker. At 32 clients, vs.md has Gunicorn's ASGI worker at 378,446 msg/s vs 338,230 for Granian ASGI and 341,182 for Granian RSGI.
- Free-threaded Python in production. The README calls that support experimental and 'highly discouraged in production environments'.

## How it is fast

hyper does the HTTP parsing, connection handling, TLS and response writing in Rust on a tokio runtime (N single-threaded runtimes in `st` mode or one N-thread runtime in `mt` mode), so Python never touches sockets or protocol state. Each request goes to a dedicated interop thread through a crossbeam channel; that thread attaches to the interpreter only while it builds the scope dict and schedules the app coroutine on the asyncio loop via `call_soon_threadsafe`. ASGI `send`/`receive` return Rust-implemented awaitables (an asyncio.Future-like object, or an already-completed one when nothing needs to wait) instead of pure-Python futures. A single-message response goes to hyper as one `Full` body, and tokio streams pathsend files without calling into Python. In the benchmark both servers run on uvloop, so the gap is the server layer, not the event loop.

## Compared with alternatives

Pick Granian when the app is Python. The catalogued siblings (Ultimate Express for Node, Qbix for PHP, Drogon, Sogou Workflow and the other C++/Go/Rust servers) cannot host an ASGI/WSGI callable. Granian is built on the catalogued hyper crate, so if the service can be written in Rust, using hyper directly avoids the Python hop entirely.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | click at runtime. Optional extras: uvloop/rloop/winloop, watchfiles (reload), python-dotenv, setproctitle. Source builds need a Rust toolchain and maturin&gt;=1.14 (PyO3 0.29, hyper 1.11, tokio 1.51, rustls via tls-listener). |
| **Minimum toolchain** | Python 3.10+ (CPython 3.10-3.15, PyPy 3.11, free-threaded 3.14t/3.15t). Rust edition 2024 for source builds; minimum rustc version not documented. |
| **Platforms** | Prebuilt wheels for Linux x86_64/aarch64/i686/armv7 (manylinux and musllinux), macOS x86_64/aarch64 and Windows x86_64. On Linux, multiple workers with respawn need kernel &gt;= 5.14 and net.ipv4.tcp_migrate_req enabled, or queued connections can be dropped. |
| **Thread safety** | Async interfaces run Python code on each worker's asyncio loop thread. WSGI runs it on a pool of up to --blocking-threads threads that contend for the GIL. Workers are separate processes, or threads on free-threaded builds, where the app object is shared. Nothing else is documented. |
| **Drop-in for the baseline** | partial — the same ASGI 3 callable runs with no code changes, but the CLI and tuning model differ (workers, runtime threads, backpressure), trio is unsupported, some ASGI extensions are missing, and forwarded headers need the granian.utils.proxies wrappers instead of a CLI option. |

## Gotchas

- Release builds set panic="abort", so any Rust panic kills the whole worker process. CVE-2026-42544 (high; a non-ASCII Sec-WebSocket-Protocol header) and CVE-2026-42545 (an invalid WSGI response header) were single-request worker crashes, fixed in 2.7.4. Stay current and consider --respawn-failed-workers (off by default).
- A plain `pip install granian` runs on stdlib asyncio, because uvloop and rloop are extras. asyncio.md shows ASGI at 85,281 RPS on asyncio vs 127,962 on uvloop. Also, raising --runtime-threads did not raise ASGI throughput in concurrency.md (st 1→4 threads: 132,067→108,238 RPS); scale with --workers.
- Backpressure limits accepted connections, not requests. Behind a reverse proxy that holds many keep-alive connections, a value below that count stops new connections being accepted (README warning). Also set --workers-kill-timeout, which has no default: #875 reported workers hanging forever on shutdown, and 2.8.0/2.8.2 shipped shutdown fixes.
- Passing --ssl-client-verify without --ssl-ca only logs a warning and turns client-certificate verification off (issue #853, open), so a mistyped mTLS setup accepts unauthenticated clients.

## Known shortcomings

- The lead mostly vanishes on I/O-bound apps (10 ms waits at c=512: 45,859 vs Uvicorn+httptools 43,903 RPS; tie at 100 ms). Release builds use panic=abort, so any Rust panic kills a worker; two single-request crashes fixed in 2.7.4 (CVE-2026-42544 high, non-ASCII Sec-WebSocket-Protocol; CVE-2026-42545 medium, invalid WSGI header). A default pip install runs on stdlib asyncio (85,281 vs 127,962 RPS with uvloop). More runtime threads don't raise ASGI throughput; scale with workers. Gunicorn's ASGI worker wins 32-client WebSocket broadcast. --ssl-client-verify without --ssl-ca silently disables client-cert verification (#853 open). No default --workers-kill-timeout (hangs, #875; fixes in 2.8.0/2.8.2); backpressure limits connections, not requests; multi-worker respawn needs Linux 5.14+ with tcp_migrate_req. No trio/gevent; free-threaded Python experimental; Rust task impl disabled on 3.12+ after a leak (#500). First-party single runs with unpinned competitors.

## Caveats and trade-offs

First-party benchmark with a public harness. Granian's ASGI server also runs on uvloop in this test, so the gain is over Uvicorn's Python HTTP layer, not over uvloop itself. Single worker, single runtime thread (Granian ASGI in --runtime-mode st), HTTP/1.1, 10 KB static response; the third-party servers are the 'latest available version at the time of the run', not pinned. The lead shrinks when the app does I/O: ASGI with 10 ms waits at c512 gives 45,859 vs 43,903 RPS for Uvicorn Httptools (\~1.04x); \~50 KB file responses give 48,049 vs 30,004 RPS (\~1.6x) (derived from page data). Rust toolchain version not stated.

Rust/PyO3 build dependency (maturin); single benchmark run, not averaged over repeated trials; desktop CPU rather than a controlled cloud instance

## Maintenance

Actively maintained: 2.8.3 shipped 2026-09-14, patch releases are frequent, and fixes usually land only on the latest minor. BSD-3-Clause, installed from PyPI wheels; the README lists production users including paperless-ngx, SearXNG, Weblate, Mozilla and Sentry.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** benchmarks/vs.md (run 2026-08-05, Granian 2.8.1, Python 3.13) lists Granian ASGI get 10KB c128 at 125,539 RPS vs Uvicorn H11 14,501 and Uvicorn Httptools 51,051. The harness is public (benchmarks/benchmarks.py, benchmarks/runbench.sh, benchmarks/envs/\*.txt, benchmarks/app/). Build flags are stated (maturin --release --features jemalloc; Cargo release profile lto=fat, panic=abort) and so is the CPU (AMD Ryzen 7 5700X).
- **Verifier notes:** Numbers and ratios match vs.md (8.66x over Uvicorn H11, 2.46x over Uvicorn Httptools, derived from page data). I changed the baseline from 'uvloop' to Uvicorn, because vs.md says every async server, Granian included, runs on uvloop; uvloop is the shared event loop, not what Granian beats. Metadata checks out: BSD-3-Clause, 5,673 stars, last commit 2026-09-13, not a fork, not archived.
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `baseline_in_list`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/emmett-framework/granian>
  - <https://raw.githubusercontent.com/emmett-framework/granian/master/benchmarks/vs.md>
  - <https://raw.githubusercontent.com/emmett-framework/granian/master/benchmarks/runbench.sh>
  - <https://github.com/emmett-framework/granian/tree/master/benchmarks>
  - <https://github.com/emmett-framework/granian/blob/master/Cargo.toml>
  - <https://github.com/emmett-framework/granian/blob/master/.cargo/config.toml>
  - <https://github.com/emmett-framework/granian/blob/master/benchmarks/envs/asgi.txt>
  - <https://github.com/emmett-framework/granian/blob/master/benchmarks/envs/common.txt>
- **Sources the enricher read:**
  - <https://github.com/emmett-framework/granian>
  - <https://github.com/emmett-framework/granian/blob/c0b1e0b9ba8349e2451b1b688037d8d79e4693b4/benchmarks/vs.md>
  - <https://raw.githubusercontent.com/emmett-framework/granian/master/Cargo.toml>
  - <https://raw.githubusercontent.com/emmett-framework/granian/master/pyproject.toml>
  - <https://raw.githubusercontent.com/emmett-framework/granian/master/src/runtime.rs>
  - <https://raw.githubusercontent.com/emmett-framework/granian/master/src/callbacks.rs>
  - <https://raw.githubusercontent.com/emmett-framework/granian/master/src/blocking.rs>
  - <https://raw.githubusercontent.com/emmett-framework/granian/master/src/net.rs>
  - <https://raw.githubusercontent.com/emmett-framework/granian/master/src/asgi/http.rs>
  - <https://raw.githubusercontent.com/emmett-framework/granian/master/src/asgi/callbacks.rs>
  - <https://raw.githubusercontent.com/emmett-framework/granian/master/src/asgi/io.rs>
  - <https://raw.githubusercontent.com/emmett-framework/granian/master/granian/_futures.py>
  - <https://raw.githubusercontent.com/emmett-framework/granian/master/granian/asgi.py>
  - <https://raw.githubusercontent.com/emmett-framework/granian/master/granian/_loops.py>
  - <https://raw.githubusercontent.com/emmett-framework/granian/master/.github/workflows/release.yml>
  - <https://raw.githubusercontent.com/emmett-framework/granian/master/benchmarks/benchmarks.py>
  - <https://raw.githubusercontent.com/emmett-framework/granian/master/benchmarks/app/asgi.py>
  - <https://raw.githubusercontent.com/emmett-framework/granian/master/benchmarks/envs/asgi.txt>
  - <https://raw.githubusercontent.com/emmett-framework/granian/master/benchmarks/envs/common.txt>
  - <https://raw.githubusercontent.com/emmett-framework/granian/master/benchmarks/concurrency.md>
  - <https://raw.githubusercontent.com/emmett-framework/granian/master/benchmarks/asyncio.md>
  - <https://github.com/emmett-framework/granian/releases>
  - <https://github.com/emmett-framework/granian/security/advisories/GHSA-vrg7-482j-p6f6>
  - <https://github.com/emmett-framework/granian/security/advisories/GHSA-f5p7-9fr5-8jmj>
  - <https://github.com/emmett-framework/granian/issues>
  - <https://github.com/emmett-framework/granian/issues/853>
  - <https://github.com/emmett-framework/granian/issues/875>
  - <https://github.com/emmett-framework/granian/issues/500>
  - <https://github.com/emmett-framework/granian/issues/585>
  - <https://github.com/emmett-framework/granian/issues/712>
  - <https://github.com/emmett-framework/granian/issues/883>
  - <https://github.com/emmett-framework/granian/issues/908>
  - <https://hn.algolia.com/api/v1/search?query=granian&tags=story>
  - <https://news.ycombinator.com/item?id=34399125>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/emmett-framework/granian`) · [data/wave5/enrich/raw/github_com_emmett_framework_granian.json](../../../data/wave5/enrich/raw/github_com_emmett_framework_granian.json) (enrichment confidence 0.88)

</details>
