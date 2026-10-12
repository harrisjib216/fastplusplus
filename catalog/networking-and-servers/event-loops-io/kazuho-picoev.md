# picoev

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [Event loops and async I/O](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `BSD-3-Clause` · 🔴 abandoned

> Tiny C event loop (\~1k lines; epoll/kqueue/select) that beat 2009-era libevent \~2x on libev's bench.c.

| | |
|---|---|
| **Beats** | libevent |
| **Claimed result** | README: 'it is faster than libevent or libev!' The two charts (1,000 active clients, 1k-100k fds) show picoev lowest throughout. At 100,000 fds, setup time is about 600k µs for libevent vs about 190k µs for picoev (\~3x), and event-processing time is about 22.5k vs about 11k µs (\~2x). libev (native) is close behind picoev (\~12k µs). These values are approximate, read off the unlabeled chart axes (derived from page data). |
| **Workload** | Re-modified version of libev's bench.c measuring per-descriptor setup time and per-event processing time across scaling file-descriptor counts, for select/epoll/kqueue backends. |
| **Metric** | latency |
| **Adoption** | 403 stars; vendored by the meinheld Python WSGI server (meinheld/server/picoev_\*.c, \~1.45k stars) |
| **Last commit** | 2016-04-27 |
| **Links** | [repository](https://github.com/kazuho/picoev) · [benchmark](https://github.com/kazuho/picoev#readme) |

## Verdict

The author's 2009 charts (libev's bench.c adapted for picoev: socketpairs, 1,000 active clients, 1k-100k fds, read off the archived images) show, at 100k fds, about 190k µs per run including re-registering every fd for picoev vs about 595k µs for libevent (\~3.1x) and about 200k µs for libev native, and event processing of about 10.8k vs 22.5k µs (\~2.1x; libev native \~12.1k). No compiler, flags, CPU, OS, backend, timer setting or library versions are given. An independent 2018 run (-Os, no hardware stated, 100k fds, 1 active) measured picoev at \~61k µs total vs \~123k µs for libevent and \~27.5k µs for libev.

## Use it when

- Small single-purpose Unix servers (memcached-style protocol, proxy, WSGI front end) where you want an event loop you can read end to end: picoev.h plus the epoll backend is about 570 lines.
- Many long-lived connections, each with one idle timeout, where 1-second (or coarser) timeout precision is fine. In the author's chart, setup and dispatch time grew no faster than libev's native API from 1k to 100k fds.
- Linux epoll workloads that register and unregister the same fds often, because deferred deletes turn a del-then-add cycle into a single epoll_ctl.
- One loop per thread with fds partitioned between loops, the design the author wrote it for (mycached), when 2009 libevent had no multithreading support.
- As a starting point for your own event library; the author recommends it for exactly this.

## Skip it when

- You need sub-second or standalone timers, signals, child watchers, cross-thread wakeups, or buffered I/O, DNS or HTTP layers. None exist, and the author said sub-second timeouts would need 'something completely different' than the bit-vector ring.
- Windows or io_uring. Windows works only through the select backend with an fd-to-SOCKET table (built with MinGW g++), there is no IOCP, and the io_uring request (issue #7, 2021) is unanswered.
- macOS/BSD code that asks for PICOEV_READWRITE. The kqueue backend ORs EVFILT_READ (-1) with EVFILT_WRITE (-2), which yields -1, so only the read filter is registered (from reading the code; meinheld's vendored copy has the same line).
- Unbounded or unknown fd counts. The fd table size is fixed at picoev_init(max_fd), and fd &gt;= max_fd is caught only by assert() (issue #6 hit this). With NDEBUG, it writes out of bounds. The select backend never checks FD_SETSIZE.
- You need maintained, documented code. The last code change is from 2015, there are no API docs (issue #4 asking for them is unanswered), and the only first-party benchmark is from 2009.

## How it is fast

Per-fd state (callback, argument, owning loop, watched events) lives in one flat array indexed directly by the fd number, so add, modify and dispatch are O(1) array accesses with no tree or hash. Timeouts use a coarse timing wheel: a ring of 128 bit vectors (one bit per fd) plus a second-level summary bitmap, so the expiry scan skips empty 16-fd words; bucket width is ceil(max_timeout/128) seconds. The epoll backend defers EPOLL_CTL_DEL and tries MOD before ADD, so a del-then-re-add costs one epoll_ctl (a new fd costs two), and the kqueue backend batches pending changes into the next kevent() wait call. Despite the PICOEV_SIMD_BITS constant, the timeout scan is scalar code; the source still says 'TODO use SIMD instructions'.

## Compared with alternatives

Against libev (catalogued), the author's own charts put picoev only about 5-12% ahead of libev's native API, and an independent 2018 run (bartman/event-loop-benchmark) had libev about 2.2x faster on total time. Pick picoev over libev, or over the maintained, cross-platform libhv, only when a roughly 1k-line, forkable fd-array loop matters more than features, maintenance and IOCP support.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (libc and the OS poller: epoll, kqueue or select; ws2_32 on Windows) |
| **Minimum toolchain** | not documented; C with GCC/Clang extensions (__inline__, __attribute__((unused))). The header can be included from C++ (extern "C"), and the Windows example builds with MinGW g++. |
| **Platforms** | Linux (epoll), macOS/FreeBSD (kqueue), other POSIX via select, Windows via select (2009 MinGW port; picoev_w32_init lacks a success return); no architecture-specific code |
| **Thread safety** | Not documented. There is one process-wide fd table and no locks. Several loops can exist, and each fd is tagged with its owner loop, so one loop per thread with disjoint fds is the apparent model. picoev_init and picoev_create_loop are not thread-safe (non-atomic ++num_loops). |
| **Drop-in for the baseline** | no |

## Gotchas

- Every argument check is an assert(). With NDEBUG, an out-of-range fd, adding an fd that is already registered, and epoll_ctl failures all go unreported. The epoll backend's update function always returns 0, so picoev_add never reports an epoll error.
- picoev_create_loop(max_timeout) sets the wheel resolution to ceil(max_timeout/128) seconds, and longer per-fd timeouts silently clamp to the last bucket. max_timeout=0 gives resolution 0: picoev_set_timeout divides by zero, and the timeout scan loop never advances (base_time += 0).
- Only EPOLLIN/EPOLLOUT (or the kqueue READ/WRITE filters) are mapped to callbacks. An EPOLLERR/EPOLLHUP-only event invokes nothing, so detect errors and hangups from read()/write() return values. picoev_del leaves the fd in the epoll set until its next event unless you build with PICOEV_EPOLL_DEFER_DELETES=0.
- Global state has side effects. picoev_memalign calls rand() to scatter allocations, which perturbs the program's rand() sequence. The Makefile selects kqueue with the misspelled DARWING_BUILD, and its shared-library rule uses GNU ld's -soname. picoev_w32_init has no return statement on success.

## Known shortcomings

- The README charts are dead on their original host (archived copies exist) and have unlabeled axes; no compiler, flags or CPU given. Minimal API, no Windows; mostly vendored by meinheld.
- The benchmark is not like-for-like: libevent/libev get randomized timeouts that go through a heap while picoev gets fixed ones, and picoev's epoll backend defers deletes; the libevent version and whether timers were on are not stated. picoev is only \~5-12% ahead of libev native on the charts. An independent run (bartman/event-loop-benchmark, 100k fds) has libev \~2.2x faster overall, with picoev fastest only on event processing. Code-reading bugs: kqueue backend ORs EVFILT_READ|EVFILT_WRITE into -1, so read-write registration drops the write filter; errors are assert()-only (fd &gt;= max_fd writes out of bounds with NDEBUG, #6); EPOLLERR/EPOLLHUP-only events reach no callback; select backend ignores FD_SETSIZE; max_timeout=0 divides by zero. Windows init lacks a return; Makefile misspells DARWING_BUILD. No LICENSE file; last commit 2016, issues unanswered.

## Caveats and trade-offs

There is no LICENSE file. The BSD-3-Clause terms come from per-file headers (Copyright 2009 Cybozu Labs, with an unfilled '&lt;ORGANIZATION&gt;' placeholder), and the 326-byte declarations-only picoev_w32.h has no header. The README's chart images and original post on developer.cybozu.co.jp are dead; they survive only on web.archive.org (picoev_setup.png and picoev_event.png, 2015 snapshots). The charts have no numeric labels, and there is no stated compiler, flags, hardware, library versions or timeout settings. Only select, epoll and kqueue backends are supported, and timeouts have coarse 1-second granularity (a 128-slot ring of bit vectors). In the independent bartman/event-loop-benchmark README (5 stars, -Os -ggdb, picoev built -O2, no hardware stated), picoev's total is \~61k µs vs libevent's \~123k µs per run, with libev fastest at \~27.5k µs.

Only supports select(2)/epoll(2)/kqueue(2) (no IOCP); array-plus-bitvector-ring-buffer design gives only \~1-2s timeout granularity beyond 128 buckets; author explicitly states picoev is 'not comparable' to libevent/libev in maturity or feature set.

## Maintenance

Abandoned: the last code change is from 2015, the last commit (a README typo) from 2016-04-27, and three issues are unanswered. It is BSD-3-Clause via per-file headers (no LICENSE file) and about 965 lines, so it is easy to vendor; the living descendants are meinheld's modified vendored copy and V's vlib/picoev port.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README (copied from the author's 2009 Cybozu Labs post) with two charts, 'Setup Time (1,000 active)' and 'Event Processing Time (1,000 active)', plotting picoev against libevent and libev (emul and native). The benchmark code is public (example/bench.c, a modified libevent/libev bench.c), but no compiler, flags, CPU or library versions are stated, so it is C.
- **Verifier notes:** The claim is qualitative in the README, and the archived charts support it against both libevent and libev. The record's 'license: null' was wrong: every core source file has a BSD-3-Clause header, so usability becomes copyable. Tier C is unchanged.
- **Fields the verifier corrected:** `claimed_speedup`, `license`, `usability`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/kazuho/picoev#readme>
  - <https://github.com/kazuho/picoev>
  - <https://github.com/kazuho/picoev/blob/master/picoev.h>
  - <https://github.com/kazuho/picoev/blob/master/picoev_w32.h>
  - <https://github.com/kazuho/picoev/blob/master/Makefile>
  - <https://github.com/kazuho/picoev/blob/master/example/bench.c>
  - <https://github.com/kazuho/picoev/blob/master/example/Makefile>
  - <http://developer.cybozu.co.jp/archives/kazuho/files/picoev_setup.png>
  - <http://developer.cybozu.co.jp/archives/kazuho/files/picoev_event.png>
  - <http://developer.cybozu.co.jp/archives/kazuho/2009/08/picoev-a-tiny-e.html>
  - <http://coderepos.org/share/browser/lang/c/picoev/trunk/example/bench.c>
  - <http://web.archive.org/web/20150421145622/http://developer.cybozu.co.jp/archives/kazuho/files/picoev_setup.png>
  - <http://web.archive.org/web/20150421154804/http://developer.cybozu.co.jp/archives/kazuho/files/picoev_event.png>
  - <http://web.archive.org/web/20191117202924/http://developer.cybozu.co.jp:80/archives/kazuho/2009/08/picoev-a-tiny-e.html>
  - <https://github.com/bartman/event-loop-benchmark>
  - <https://github.com/mopemope/meinheld>
- **Sources the enricher read:**
  - <https://github.com/kazuho/picoev>
  - <https://github.com/kazuho/picoev#readme>
  - <https://github.com/kazuho/picoev/blob/master/picoev.h>
  - <https://github.com/kazuho/picoev/blob/master/picoev_epoll.c>
  - <https://github.com/kazuho/picoev/blob/master/picoev_kqueue.c>
  - <https://github.com/kazuho/picoev/blob/master/picoev_select.c>
  - <https://github.com/kazuho/picoev/blob/master/picoev_w32.h>
  - <https://github.com/kazuho/picoev/blob/master/Makefile>
  - <https://github.com/kazuho/picoev/blob/master/.gitignore>
  - <https://github.com/kazuho/picoev/blob/master/example/bench.c>
  - <https://github.com/kazuho/picoev/blob/master/example/Makefile>
  - <https://github.com/kazuho/picoev/blob/master/example/Makefile.w32>
  - <https://github.com/kazuho/picoev/blob/master/example/picoev_echo.c>
  - <https://github.com/kazuho/picoev/commits/master>
  - <https://github.com/kazuho/picoev/commit/6ed894e>
  - <https://github.com/kazuho/picoev/pull/1>
  - <https://github.com/kazuho/picoev/issues/4>
  - <https://github.com/kazuho/picoev/issues/5>
  - <https://github.com/kazuho/picoev/issues/6>
  - <https://github.com/kazuho/picoev/issues/7>
  - <https://github.com/kazuho/picoev/forks>
  - <http://web.archive.org/web/20191117202924/http://developer.cybozu.co.jp:80/archives/kazuho/2009/08/picoev-a-tiny-e.html>
  - <http://web.archive.org/web/20150421145622/http://developer.cybozu.co.jp/archives/kazuho/files/picoev_setup.png>
  - <http://web.archive.org/web/20150421154804/http://developer.cybozu.co.jp/archives/kazuho/files/picoev_event.png>
  - <https://github.com/bartman/event-loop-benchmark>
  - <https://github.com/bartman/event-loop-benchmark/blob/master/Makefile>
  - <https://github.com/mopemope/meinheld>
  - <https://github.com/mopemope/meinheld/blob/master/meinheld/server/picoev_kqueue.c>
  - <https://github.com/mopemope/meinheld/blob/master/meinheld/server/picoev_epoll.c>
  - <https://github.com/freebsd/freebsd-src/blob/main/sys/sys/event.h>
  - <https://github.com/apple-oss-distributions/xnu/blob/main/bsd/sys/event.h>
  - <https://github.com/vlang/v/tree/master/vlib/picoev>
  - <https://hn.algolia.com/api/v1/search?query=picoev>
  - <https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch=picoev>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/kazuho/picoev`) · [data/wave5/enrich/raw/github_com_kazuho_picoev.json](../../../data/wave5/enrich/raw/github_com_kazuho_picoev.json) (enrichment confidence 0.6)

</details>
