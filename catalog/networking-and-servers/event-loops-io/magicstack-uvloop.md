# uvloop

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [Event loops and async I/O](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Python` · `Apache-2.0 OR MIT` · 🟢 active

> Cython/libuv replacement for CPython's default asyncio event loop; 2-4x echo throughput in its own 2016 benchmark.

| | |
|---|---|
| **Beats** | CPython asyncio default event loop (pure-Python SelectorEventLoop, epoll-backed on Linux) |
| **Claimed result** | README states 'uvloop makes asyncio 2-4x faster'. Read off the README bar chart (derived from page data): protocol API at 1 KiB \~106k uvloop vs \~43k asyncio req/s (\~2.5x); sockets API at 1 KiB \~52k vs \~13.5k (\~3.9x); streams API at 1 KiB \~44k vs \~17.5k (\~2.5x); at 100 KiB the gap narrows to \~1.8x (protocol, \~23.5k vs \~12.8k) and \~1.4x (streams, \~12k vs \~8.8k). |
| **Workload** | Echo-server benchmark exercising asyncio's low-level socket API (loop.sock_recv/sock_sendall), high-level streams API (asyncio.start_server), and the protocol API (loop.create_server), at 1/10/100 KiB message sizes, comparing stock asyncio's default epoll-based SelectorEventLoop against uvloop (a libuv-backed loop swapped in via asyncio.set_event_loop_policy). |
| **Metric** | throughput |
| **Hardware** | Intel Xeon E5-1620 v2 @ 3.70GHz, Ubuntu Linux, Python 3.5, single-threaded servers in Docker, concurrency 10, 30 s runs (from the May 3, 2016 magic.io blog post that the README chart links to; the README itself does not restate hardware) |
| **Adoption** | 11.9k stars |
| **Last commit** | 2026-07-14 |
| **Links** | [repository](https://github.com/MagicStack/uvloop) · [benchmark](https://raw.githubusercontent.com/MagicStack/uvloop/master/performance.png) |

## Verdict

MagicStack's own 2016 vmbench echo servers ran single-threaded in Docker (concurrency 10, 30 s runs, TCP_NODELAY) on a Xeon E5-1620 v2, Ubuntu, Python 3.5; compiler and flags are not given. Against the stdlib selector loop, uvloop measured about 2.5x (protocol API), 3.9x (sock_recv/sock_sendall) and 2.5x (streams) at 1 KiB, and about 1.4-1.8x at 100 KiB. A 2026 third-party run (rsloop's benchmark doc: i9-9900K, Linux, CPython 3.14.7, uvloop 0.22.1) still put uvloop ahead of stdlib asyncio, by less: 2.15x on callbacks, 1.62x on tasks and 1.19x on 1 KiB TCP streams round trips.

## Use it when

- Long-running asyncio network services on Linux or macOS (uvicorn/ASGI apps, aiohttp, websockets, custom asyncio.Protocol servers) where profiles show time in the event loop itself.
- Many small messages or many callbacks/task switches: the 2016 chart shows the biggest gaps at 1 KiB (about 2.5x for the protocol API, 3.9x for sock_recv/sock_sendall), and a 2026 CPython 3.14.7 run still found 2.15x on 200k callbacks and 1.6x on 50k tasks.
- Worker-thread hand-off via call_soon_threadsafe: a third-party benchmark (python-async-bench, Python version and hardware not stated) measured 3.47 s vs 5.88 s wall time for 250k messages.
- You want a speedup from a one-line change with no rewrite, and your deployment can use the prebuilt wheels: CPython 3.8-3.14 including free-threaded 3.14t, manylinux/musllinux x86-64/aarch64, macOS x86-64/universal2.

## Skip it when

- Windows: setup.py refuses to build there ('uvloop does not support Windows at the moment'), and the request has been open since 2016 (#14). There you must use asyncio's own loops.
- Code that needs loop.sendfile/sock_sendfile (open since 2019, #228), sock_recvfrom/sock_recvfrom_into/sock_sendto (these raise NotImplementedError), Server.close_clients from 3.13 (#683), or create_connection's happy_eyeballs_delay/interleave (not in the signature, #406).
- Large-message, bulk or TLS-bound traffic, or apps whose own code dominates. At 100 KiB the first-party gap drops to about 1.4x (streams) and 1.8x (protocol). A 2026 Linux run on CPython 3.14.7 measured only 1.19x over stdlib asyncio for 1 KiB streams round trips. The 2016 blog itself found aiohttp's HTTP parser, not the loop, was the bottleneck.
- PyPy, GraalPy or other non-CPython runtimes: the package declares CPython only, and PyPy install/import failures are open issues (#380, #537).
- Deployments that need recent fixes from PyPI: 0.22.1 (2025-10-16) is still the latest release. The free-threading call_soon_threadsafe race fix (#720), eager_start support and the 2026 write-path/SSL speedups exist only on master. A segfault in __uv_close_handle_cb under uvicorn/FastAPI is still open (#706).

## How it is fast

The loop's hot paths are compiled C instead of interpreted Python. A Cython loop drains the ready deque, Handle/TimerHandle objects come from 250-entry Cython freelists, and uv_run() runs with the GIL released while libuv waits in epoll/kqueue. Transport.write first tries a direct write() syscall for one buffer, or uv_try_write (scatter-gather) for several, and queues a uv_write only when the socket would block. Reads go into one preallocated 256,000-byte buffer per loop. TLS is a Cython port of asyncio's SSLProtocol over Python's ssl module, not libuv. The kernel side is the same readiness-based epoll/kqueue as the stdlib selector loop, so the gain comes from less per-event interpreter overhead, not a different I/O interface.

## Compared with alternatives

Pick uvloop when you are staying in Python asyncio: it is the only catalogued entry that speeds up existing asyncio code without changing it. UCall beats FastAPI/uvicorn only by replacing the whole server stack with its own JSON-RPC server. libhv, libev and picoev are C event libraries (libhv even benchmarks ahead of libuv, which uvloop wraps) that help only if you leave Python.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none at runtime: libuv is vendored and built into the wheel. Source builds need Cython \~=3.1, setuptools&gt;=60, packaging and a C compiler, plus autotools when building libuv from a git checkout. The --use-system-libuv option links against a system libuv instead. |
| **Minimum toolchain** | CPython 3.8.1+ (wheels cp38-cp314 plus cp314t). A source build needs Cython \~=3.1 and a C compiler; it uses -O2 by default (override with UVLOOP_OPT_CFLAGS). |
| **Platforms** | Linux (manylinux2014 and musllinux_1_2, x86-64 and aarch64) and macOS (x86-64, universal2). No Windows. CPython only. |
| **Thread safety** | One loop per thread, as in asyncio. Only call_soon_threadsafe is safe to call from other threads, and wrong-thread calls are detected only in debug mode. Free-threaded 3.14t wheels ship, but a call_soon_threadsafe race under free-threading (#720) is fixed only on unreleased master. |
| **Drop-in for the baseline** | partial — same asyncio.AbstractEventLoop API, selected with uvloop.run() or loop_factory, and most asyncio code runs unchanged. Missing: Windows support, sendfile/sock_sendfile, sock_recvfrom/sock_recvfrom_into/sock_sendto, Server.close_clients, and happy-eyeballs arguments. subprocess_exec rejects startupinfo/creationflags and requires bufsize=0. |

## Gotchas

- Selecting the loop: uvloop.install() emits DeprecationWarning on 3.12+, and install() and EventLoopPolicy are removed for 3.16. The policy's get_event_loop() raises RuntimeError when no loop is set, where older stdlib policies created one (#702, open). Some libraries broke on this.
- Debug mode (PYTHONASYNCIODEBUG=1 or debug=True) can crash during async-generator finalization on Python 3.13/3.14 (#715, open; one report says aarch64 only). Keep debug mode out of production.
- Behavior differs from stdlib in edge cases. libuv's process spawn can briefly block the loop (#118, open since 2017), and one user reported responses being coalesced under uvicorn but not under stdlib asyncio (#631, open).
- Memory is not necessarily lower: an HN user measured 204 MB vs 171 MB max RSS for 100k sleeping tasks under uvloop vs asyncio on an M1 Mac (anecdotal, CPython 3.12+).

## Known shortcomings

- Python, not C++ (it is a libuv binding for asyncio); the 2016 chart (Python 3.5) compares against CPython's default asyncio loop, and at 100 KiB messages the gain is only about 1.4-1.8x. No compiler or flags stated.
- Only first-party numbers are the 2016 chart (Python 3.5, Xeon E5-1620 v2, no compiler/flags), never re-run (#631). A 2026 third-party run (rsloop's docs, i9-9900K, CPython 3.14.7, uvloop 0.22.1) still has it ahead of stdlib asyncio but by less: 2.15x on callbacks, 1.62x on tasks, 1.19x on 1 KiB TCP stream round trips. Not fully drop-in: no Windows (#14), no loop.sendfile/sock_sendfile (#228), sock_recvfrom/sendto raise NotImplementedError, no Server.close_clients (#683) or happy_eyeballs_delay (#406), subprocess limits (#605 asks to qualify 'drop-in'). PyPI 0.22.1 (2025-10) lags master (free-threading race fix #720, eager_start, 2026 speedups). Open crashes: segfault under uvicorn (#706), debug-mode async-generator crash on 3.13/3.14 (#715), spawn can block the loop (#118). uvloop.install() deprecated from 3.12; policy get_event_loop() raises (#702). CPython only (PyPy #380, #537); loop methods not thread-safe.

## Caveats and trade-offs

First-party benchmark. The chart was committed on 2016-05-22 and the linked magic.io blog post (May 3, 2016) no longer resolves live; it is still readable via the Wayback Machine (2017-03-01 snapshot), which gives the CPU, OS, Python 3.5 and vmbench setup but no compiler or flags. The README chart's sockets/streams/protocol series do not appear in the blog post's own charts, so it is assumed, not proven, that they came from the same run and hardware. All numbers are read off a bar-chart image, not from text. The data is from Python 3.5, and stock asyncio has changed a lot since, so today's gap is unmeasured here. At 100 KiB messages the gain is only \~1.4-1.8x, below the '2-4x' headline. Both loops ultimately use epoll on Linux (uvloop through libuv), so this is a Python-event-loop-implementation comparison rather than a win over raw epoll. The vmbench harness was last pushed in 2018.

Adds a compiled C-extension (Cython + vendored libuv) build/install dependency instead of the pure-Python stdlib loop; historically Linux/macOS-focused with weaker Windows story; some asyncio edge cases (e.g. certain subprocess/signal behaviors) have lagged the stdlib implementation over time.

## Maintenance

Actively maintained (commits through 2026-07-14, CI on CPython 3.8-3.14t) but releases lag: 0.22.1 from 2025-10-16 is still the latest on PyPI. Dual Apache-2.0/MIT, installed as prebuilt wheels with no runtime dependencies.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party bar chart in the uvloop README comparing uvloop with stock asyncio's default loop on echo servers (sockets, streams and protocol APIs at 1/10/100 KiB). The benchmark code is public (MagicStack/vmbench servers/asyncioecho.py, with --uvloop/--streams/--proto) and the linked 2016 blog post (now only on the Wayback Machine) names the CPU (Xeon E5-1620 v2), but no compiler or flags are given for the Cython/libuv build, so it cannot be A.
- **Verifier notes:** The numbers match the chart to within chart-reading precision (the blog text itself quotes \~105,000 req/s for uvloop at 1 KiB). The baseline was changed from 'epoll' to stock asyncio's event loop, since that is what the chart labels and both sides use epoll underneath; baseline_in_list was set to false. License corrected to the dual Apache-2.0/MIT stated in the README (GitHub reports only Apache-2.0); stars (11,904), last commit (2026-07-14) and active status are verified.
- **Fields the verifier corrected:** `baseline`, `baseline_in_list`, `claimed_speedup`, `hardware`, `license`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/MagicStack/uvloop/master/performance.png>
  - <https://github.com/MagicStack/uvloop>
  - <https://github.com/MagicStack/uvloop/blob/master/README.rst>
  - <https://github.com/MagicStack/uvloop/blob/master/pyproject.toml>
  - <https://github.com/MagicStack/uvloop/blob/master/LICENSE-MIT>
  - <http://magic.io/blog/uvloop-blazing-fast-python-networking/>
  - <https://web.archive.org/web/20170301175905/https://magic.io/blog/uvloop-blazing-fast-python-networking/>
  - <https://github.com/MagicStack/vmbench>
  - <https://github.com/MagicStack/vmbench/blob/master/servers/asyncioecho.py>
  - <https://github.com/MagicStack/vmbench/blob/master/Dockerfile>
- **Sources the enricher read:**
  - <https://github.com/MagicStack/uvloop>
  - <https://github.com/MagicStack/uvloop/blob/master/README.rst>
  - <https://github.com/MagicStack/uvloop/blob/master/pyproject.toml>
  - <https://github.com/MagicStack/uvloop/blob/master/setup.py>
  - <https://github.com/MagicStack/uvloop/blob/master/uvloop/__init__.py>
  - <https://github.com/MagicStack/uvloop/blob/master/uvloop/_version.py>
  - <https://github.com/MagicStack/uvloop/blob/master/uvloop/loop.pyx>
  - <https://github.com/MagicStack/uvloop/blob/master/uvloop/handles/stream.pyx>
  - <https://github.com/MagicStack/uvloop/blob/master/uvloop/handles/udp.pyx>
  - <https://github.com/MagicStack/uvloop/blob/master/uvloop/handles/process.pyx>
  - <https://github.com/MagicStack/uvloop/blob/master/uvloop/dns.pyx>
  - <https://github.com/MagicStack/uvloop/blob/master/uvloop/sslproto.pyx>
  - <https://github.com/MagicStack/uvloop/blob/master/uvloop/server.pyx>
  - <https://github.com/MagicStack/uvloop/blob/master/uvloop/cbhandles.pyx>
  - <https://github.com/MagicStack/uvloop/blob/master/uvloop/includes/consts.pxi>
  - <https://github.com/MagicStack/uvloop/blob/master/.github/workflows/release.yml>
  - <https://github.com/MagicStack/uvloop/blob/master/.github/workflows/tests.yml>
  - <https://github.com/MagicStack/uvloop/blob/master/docs/index.rst>
  - <https://github.com/MagicStack/uvloop/blob/master/docs/user/index.rst>
  - <https://github.com/MagicStack/uvloop/blob/master/docs/dev/index.rst>
  - <https://github.com/MagicStack/uvloop/tree/master/vendor>
  - <https://github.com/MagicStack/uvloop/commits/master>
  - <https://github.com/MagicStack/uvloop/releases/tag/v0.22.1>
  - <https://github.com/MagicStack/uvloop/releases/tag/v0.22.0>
  - <https://github.com/MagicStack/uvloop/issues/706>
  - <https://github.com/MagicStack/uvloop/issues/720>
  - <https://github.com/MagicStack/uvloop/issues/715>
  - <https://github.com/MagicStack/uvloop/issues/118>
  - <https://github.com/MagicStack/uvloop/issues/683>
  - <https://github.com/MagicStack/uvloop/issues/702>
  - <https://github.com/MagicStack/uvloop/issues/631>
  - <https://github.com/MagicStack/uvloop/issues/605>
  - <https://github.com/MagicStack/uvloop/issues/228>
  - <https://github.com/MagicStack/uvloop/issues?q=is%3Aissue+is%3Aopen+label%3A%22missing+feature%22>
  - <https://pypi.org/pypi/uvloop/json>
  - <https://raw.githubusercontent.com/MagicStack/uvloop/master/performance.png>
  - <https://web.archive.org/web/20170301175905/https://magic.io/blog/uvloop-blazing-fast-python-networking/>
  - <https://github.com/MagicStack/vmbench>
  - <https://github.com/MagicStack/vmbench/blob/master/servers/asyncioecho.py>
  - <https://github.com/rogerbinns/python-async-bench>
  - <https://github.com/RustedBytes/rsloop>
  - <https://github.com/RustedBytes/rsloop/blob/HEAD/docs/benchmarks.md>
  - <https://hn.algolia.com/api/v1/search?query=uvloop&tags=story>
  - <https://hn.algolia.com/api/v1/search?query=uvloop&tags=comment>
  - <https://news.ycombinator.com/item?id=42274054>
  - <https://docs.python.org/3/whatsnew/3.12.html>
  - <https://docs.python.org/3/whatsnew/3.14.html>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/magicstack/uvloop`) · [data/wave5/enrich/raw/github_com_magicstack_uvloop.json](../../../data/wave5/enrich/raw/github_com_magicstack_uvloop.json) (enrichment confidence 0.75)

</details>
