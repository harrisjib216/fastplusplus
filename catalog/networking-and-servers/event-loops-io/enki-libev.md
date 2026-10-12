# libev

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [Event loops and async I/O](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `BSD-2-Clause OR GPL-2.0-or-later` · 🔴 abandoned

> Small, embeddable C event loop with io, timer, signal, child and stat watchers; halves libevent 1.4's per-iteration cost when timers churn.

| | |
|---|---|
| **Beats** | libevent |
| **Claimed result** | libev 3.31 vs libevent 1.4.3 (both on epoll) using libevent's bench.c. With no timeouts, libevent takes 'almost twice as much time than libev' in total time per iteration (the gap grows with fd count), but the event-processing (poll) times differ by less than 5%. With per-connection idle timeouts, libev's event processing is 'consistently faster (with a factor of two to almost three)' over 100-100,000 fds, and overall time 'has been almost halved'. The 2011 appendix rerun (libev 4.03 vs libevent 1.4.13 and 2.0.10) shows the same pattern. All figures are from the page's prose; the charts carry no numeric tables. |
| **Workload** | Socket-pair event loop benchmark (libev's bench.c): active clients exchanging data plus idle timers, scaled from 100 to 100,000 file descriptors with 100 and 1,000 active clients, measuring per-iteration dispatch time and timeout-handling overhead. |
| **Metric** | latency |
| **Hardware** | Core2 Quad @ 3.6GHz, Debian GNU/Linux, kernel 2.6.24-1 |
| **Compiler and flags** | gcc 4.2.3, -O3 -fno-guess-branch-probability -g |
| **Adoption** | 1,790 stars on the unofficial GitHub mirror (enki/libev). Node.js bundled it through v0.4 (deps/libev). The upstream page lists GNU Virtual Private Ethernet, rxvt-unicode, auditd and the Deliantra server and client as users. |
| **Last commit** | 2016-05-13 |
| **Links** | [repository](http://software.schmorp.de/pkg/libev.html) · [benchmark](http://libev.schmorp.de/bench.html) |

## Verdict

The libev author ran a modified libevent bench.c: libev 3.31 vs libevent 1.4.3, both on epoll, gcc 4.2.3 -O3, Core2 Quad at 3.6 GHz, Linux 2.6.24. The runs covered 100-100,000 socket pairs with 100 or 1,000 active clients, taking the minimum of six runs. Without timeouts, total time per iteration was roughly halved, mostly from cheaper watcher setup, while poll time differed by under 5%. With per-socket idle timeouts, event processing was 2-3x faster. A 2011 rerun (libev 4.03 vs libevent 1.4.13 and 2.0.10) showed the same pattern, in charts only.

## Use it when

- Linux servers holding 10k-100k connections, each with an idle timeout reset on activity. This was the benchmark's heaviest case: event processing 2-3x faster than libevent 1.4.3.
- Code that starts, stops or re-arms many watchers per iteration. libev batches the changes before the poll, so each one does not cost an epoll_ctl.
- Embedding a loop in a C/C++ program or a language runtime as a few source files with no dependencies. The EV Perl module, rxvt-unicode and gvpe embed it, and gevent uses it by default on CPython outside Windows.
- You need more than fd readiness: wall-clock cron-style timers (ev_periodic), child-process reaping, inotify-backed file watching, signalfd/eventfd, one loop per thread with ev_async wakeups.
- Existing libevent-1.4-API code that you want to try on libev by recompiling against libev's event.h.

## Skip it when

- Windows: only a select backend that handles sockets only. The docs say programs needing more than about a hundred sockets need a different implementation. gevent defaults to libuv there.
- macOS and most BSDs: kqueue is used by default only on NetBSD. Without an explicit EVBACKEND_KQUEUE, macOS falls back to select and loses the O(active fds) scaling.
- You want buffered sockets, DNS, HTTP or TLS in the same library (libevent, libuv, libhv). libev is only the loop.
- Completion-based I/O: the upstream io_uring backend is documented as slower than epoll and is off by default. Readiness-model limits still apply.
- You need a maintained dependency with measured wins against current libraries. There has been no release since 4.33 (2020), the GitHub mirror is frozen at 4.22, and nobody has benchmarked libev against libevent 2.1 or libuv. gevent reports libev and libuv as 'roughly the same'.

## How it is fast

Starting or stopping an io watcher only marks the fd in an fdchanges array. fd_reify then pushes the net change to the kernel once, before the next poll. The epoll backend also skips EPOLL_CTL_DEL and tags each event with a per-fd generation counter to drop stale events, so stopping and restarting a watcher usually costs no syscall. The benchmark page says libevent 1.4 calls epoll_ctl on every change. Timers live in a heap indexed by array position, so the next timer is O(1) and a reset (ev_timer_again) only moves the entry. The Changes file dates a 4-ary heap that caches expiry times in each node (EV_USE_4HEAP, EV_HEAP_CACHE_AT) to 3.41. The benchmark page calls it the 'upcoming 3.33', and the benchmarked 3.31 still used a binary heap. Per-fd state is a flat array indexed by fd, and pending watchers are kept in per-priority arrays.

## Compared with alternatives

Choose libev over picoev when you need exact timers and a broad watcher set. picoev claims to beat libev on a variant of this benchmark, but it keeps timeouts in a 1-second-granularity ring buffer and calls itself less mature. Choose libev over libhv when you want only a tiny, dependency-free loop to vendor. libhv is an actively developed cross-platform TCP/HTTP/WebSocket library benchmarked on throughput. For io_uring completion I/O, look at Condy or uring_exec instead.

## Integration

| | |
|---|---|
| **Form** | source-drop (ev.c #includes the enabled backend files; add event.c for the libevent API) or an autotools-built static/shared lib |
| **Dependencies** | none beyond libc and the OS polling APIs (README: 'no dependencies'); older glibc may need -lrt for clock_gettime (Changes 4.18) |
| **Minimum toolchain** | ISO C compiler; sources also compile as C++. The mirror's 4.22 ev++.h fails under C++17 because of dynamic exception specs (mirror issue #15). Upstream 4.25 removed them. |
| **Platforms** | Linux (epoll; upstream 4.26+ adds optional linuxaio and io_uring backends), Solaris (event ports), NetBSD (kqueue), other BSDs and macOS (select/poll by default, kqueue opt-in), generic POSIX; Windows only via winsocket select, sockets only |
| **Thread safety** | Functions are reentrant. There is no internal locking: separate loops can run in parallel threads, but calls on the same loop must be serialized by the caller. ev_async is the thread-safe wakeup. |
| **Drop-in for the baseline** | partial: event.h emulates only the libevent 1.4.1-beta API at source level, not ABI level. Priorities are unsupported and ev_flags/EVLIST_\* behave differently. There is no bufferevent/evdns/evhttp in libev. The fast path is the different native ev_\* API. |

## Gotchas

- After fork(), the child must call ev_loop_fork(), set EVFLAG_FORKCHECK, or use select/poll. Otherwise epoll/kqueue state is inherited and wrong.
- Default error handling aborts. Unhandled syscall errors call the syserr callback, which prints and calls abort(). Usage errors are assert()s. The allocator callback returning NULL may abort.
- Idle-timeout speed depends on the pattern. Stopping, setting and restarting a timer on every packet is the documented slow way. Use ev_timer_again, or one timer plus a linked list for millions of identical timeouts. In the benchmark, libev's libevent emulation (del+add, two heap operations per reset) was noticeably slower than the native API.
- epoll quirks surface through libev: keep one watcher active per fd until close, avoid watchers on dup()'ed fds, and expect regular files to be rejected. The docs say select can match epoll up to about 100 fds.

## Known shortcomings

- The recorded repo is an unofficial mirror stuck at 4.22; upstream (software.schmorp.de) is at 4.33 (2020-03). The benchmark is libev's author's own, on a 'Core2 Quad at 3.6GHz' with gcc 4.2.3; without timeouts poll times differ from libevent by under 5%, the 2-3x gain is with idle timeouts.
- enki/libev is a stale mirror frozen at 4.22 (2015); upstream (CVS, dist.schmorp.de) is at 4.33 with small commits into 2026, so link upstream. The mirror lacks the 4.23-4.33 fixes (ev++.h fails under C++17, #15; timerfd time-jump detection; linuxaio/io_uring backends, which upstream documents as slower than epoll). The benchmark is from 2008 against libevent 1.4; its appendix says libevent 2.0.10 was a tiny bit slower, not closer, and nothing compares libev with libevent 2.1 or libuv (gevent finds libev and libuv roughly equal). Its 'latency' metric is CPU time per loop pass. Windows has only a select backend for sockets (docs advise another library above \~100 sockets); kqueue is the default only on NetBSD, so macOS/other BSDs use select/poll unless asked.
- Re-found by the wave 5 seed backfill (w5-mine-k): bartman/event-loop-benchmark README has libev about 4.5x faster than libevent in the total column (third-party harness, no CPU or flags stated here); the author's bench.html stays blocked. Possible retier lead (lead in data/wave5/leads.md).

## Caveats and trade-offs

enki/libev is an unofficial GitHub mirror stuck at libev 4.22 (Dec 2015). Upstream lives in schmorpforge CVS (http://software.schmorp.de/pkg/libev.html), and its latest release, 4.33, is from 2020-03-18. The benchmark is the libev author's own: the original run (libevent 1.4.3 vs libev 3.31) is from \~2008 and the writeup was last revised 2011-01-11 (version 6). The CPU is given only as 'Core2 Quad at 3.6GHz', and results are line charts, not tables. Without timeouts, the gain is almost entirely in watcher setup; poll times are within 5%. libuv is not covered. The independent bartman/event-loop-benchmark (5 stars, -Os -ggdb, no hardware stated) reuses this bench.c. In its README, libev's total is \~27.5k µs vs libevent's \~123k µs, but libevent's event-processing column is lower (\~215 vs \~270 µs).

More manual/lower-level API than libevent or libuv (explicit watcher structs, no built-in cross-platform abstraction beyond POSIX backends); weaker Windows support; author himself notes libevent 2.x (much newer than the 1.4.3 tested here) narrowed some gaps.

## Maintenance

The GitHub mirror is frozen at 4.22 (Dec 2015), and upstream (schmorp CVS, dist.schmorp.de) last released 4.33 on 2020-03-18, with only sporadic small CVS commits since (latest ev.c revision 2026-04-13). It is dual BSD-2-Clause/GPL-2.0 and designed to be vendored as a few C files, so take 4.33 from upstream rather than the mirror.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification A, tier now C.
- **Tier reason:** This is the libev author's own writeup. The benchmark code is public (http://libev.schmorp.de/bench.c, a modified copy of libevent's bench.c), and the compiler and flags are stated (gcc 4.2.3 -O3 -fno-guess-branch-probability -g). The CPU, however, is given only as 'a Core2 Quad at 3.6GHz', a family and clock with no model or SKU, so it misses A. First-party with partial methodology is C.
- **Verifier notes:** The numbers and prose match the page. Downgraded from A to C because the CPU is given only by family and clock (no model) and the benchmark is first-party; this follows earlier batches' rulings on family-only CPUs. The record's usage claims 'EventMachine, Tor' could not be verified and look wrong (Tor uses libevent, and EventMachine has its own reactor), so they were replaced with verified users.
- **Fields the verifier corrected:** `claimed_speedup`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** backfill w5-mine-k
- **Pages the verifier opened:**
  - <http://libev.schmorp.de/bench.html>
  - <http://libev.schmorp.de/bench.c>
  - <http://libev.schmorp.de/dat1.t0.png>
  - <http://libev.schmorp.de/dat1.t1.png>
  - <http://libev.schmorp.de/dat.t0.png>
  - <http://libev.schmorp.de/dat.t1.png>
  - <https://github.com/enki/libev>
  - <https://github.com/enki/libev/blob/master/LICENSE>
  - <https://github.com/enki/libev/blob/master/Changes>
  - <http://software.schmorp.de/pkg/libev.html>
  - <http://dist.schmorp.de/libev/>
  - <https://github.com/nodejs/node/tree/v0.4.0/deps>
  - <https://github.com/bartman/event-loop-benchmark>
  - <https://github.com/bartman/event-loop-benchmark/blob/master/Makefile>
- **Sources the enricher read:**
  - <https://github.com/enki/libev>
  - <https://github.com/enki/libev/blob/master/README>
  - <https://github.com/enki/libev/blob/master/Changes>
  - <https://github.com/enki/libev/blob/master/ev.pod>
  - <https://github.com/enki/libev/blob/master/ev.h>
  - <https://github.com/enki/libev/blob/master/ev.c>
  - <https://github.com/enki/libev/blob/master/ev_epoll.c>
  - <https://github.com/enki/libev/issues>
  - <https://github.com/enki/libev/issues/6>
  - <https://github.com/enki/libev/issues/12>
  - <https://github.com/enki/libev/issues/15>
  - <https://github.com/enki/libev/issues/16>
  - <https://github.com/enki/libev/pull/2>
  - <https://github.com/enki/libev/pull/8>
  - <http://libev.schmorp.de/bench.html>
  - <http://libev.schmorp.de/bench.c>
  - <http://software.schmorp.de/pkg/libev.html>
  - <http://dist.schmorp.de/libev/>
  - <http://cvs.schmorp.de/libev/>
  - <http://cvs.schmorp.de/libev/Changes>
  - <http://cvs.schmorp.de/libev/ev.pod>
  - <http://cvs.schmorp.de/libev/ev.h>
  - <http://cvs.schmorp.de/libev/ev.c?view=log>
  - <https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch=libev&keywordExactMatch>
  - <https://hn.algolia.com/api/v1/search?query=libev&tags=story&hitsPerPage=20>
  - <https://hn.algolia.com/api/v1/search?query=libev%20libuv&hitsPerPage=15>
  - <https://hn.algolia.com/api/v1/items/6598527>
  - <https://www.gevent.org/loop_impls.html>
  - <https://github.com/bartman/event-loop-benchmark>
  - <https://github.com/kazuho/picoev>
  - <https://github.com/ithewei/libhv>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/enki/libev`) · [data/wave5/enrich/raw/github_com_enki_libev.json](../../../data/wave5/enrich/raw/github_com_enki_libev.json) (enrichment confidence 0.82)

</details>
