# libPhenom

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [Event loops and async I/O](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `Apache-2.0` · 🔴 abandoned

> Archived Facebook C eventing framework (epoll/kqueue/ports job scheduler); first-party gut check shows 1.07-1.39x libevent events/s.

| | |
|---|---|
| **Beats** | libevent |
| **Claimed result** | Commit 41b6106 'Streamline nbio scheduling a bit' (9 Jun 2013): 'we're a bit faster because we're doing overall less book keeping per event'. Linux, './tests/bench/iopipes.t -n 1024 -c 1': libphenom 366,624 events/s vs libevent ('-e') 264,129 events/s (about 1.39x, derived from page data). OSX: libphenom 505,155 events/s vs libevent 471,385 events/s (about 1.07x, derived from page data). The OSX and Linux boxes are different machines; single core only because that is all the harness can compare against libevent. |
| **Workload** | tests/bench/iopipes.c (iopipes.t) event-dispatch benchmark: 1024 AF_UNIX socketpairs (-n 1024), each primed with one byte; every read callback reads the byte and writes one back, so each descriptor stays permanently ready, and the tool counts callbacks dispatched per second over a \~1 s run on one scheduler thread (-c 1). libphenom re-arms with ph_job_set_nbio; the libevent mode (-e) uses the legacy event_init/event_set API with non-persistent EV_READ events re-added via event_add in every callback. |
| **Metric** | throughput |
| **Hardware** | Not stated; the commit says the OSX and Linux numbers came from two different machines. Single core only. |
| **Adoption** | 1.7k stars; repository archived 2019-03-09 (README points to folly as the maintained alternative) |
| **Last commit** | 2019-03-08 |
| **Links** | [repository](https://github.com/facebook/libphenom) · [benchmark](https://github.com/facebook/libphenom/commit/41b6106.patch) |

## Verdict

One first-party commit message (41b6106, June 2013) reports single \~1 s runs of tests/bench/iopipes.t with 1024 AF_UNIX socketpairs on one scheduler thread: 366,624 vs 264,129 events/s against libevent on Linux (about 1.39x) and 505,155 vs 471,385 on OS X (about 1.07x), on two unnamed machines with unstated compiler, flags and libevent version. The libevent side uses non-persistent events that cost it an extra epoll_ctl per event on Linux, so the Linux ratio overstates the scheduler difference.

## Use it when

- Maintaining or studying an existing libphenom-based C service, or mining its design (per-thread emitters, one-shot re-arm, epoch-based job freeing) for your own loop.
- Multi-threaded C servers that want readiness dispatch, thread pools, timers and buffered TLS streams from one framework rather than gluing libevent, a pool and OpenSSL BIOs together.
- Linux, OS X or illumos hosts where you can pin old dependencies (Concurrency Kit 0.5.x, OpenSSL 1.0.x) and vendor the code yourself.

## Skip it when

- Anything new: archived 2019-03-09, last code commit 2016-01-28, and the README sends users to folly; libev, libuv or libhv are maintained alternatives.
- Modern toolchains: configure accepts only Concurrency Kit 0.5.0-0.5.1 (issue #84 reports a static-assert build failure with newer CK, still open) and the OpenSSL glue uses a static BIO_METHOD and direct BIO field access, which do not compile against OpenSSL 1.1 or 3.x without patching.
- Code written against libevent's API: there is no compatibility layer, and every NBIO job is one-shot and must be re-armed explicitly.
- Fine-grained timers: the timer wheel ticks every 100 ms (WHEEL_INTERVAL_MS), so timeouts are coarse.
- FreeBSD/OpenBSD: the kqueue port is described as not tried in a while, and issue #48 (tests/timer failures on FreeBSD) is still open.

## How it is fast

Each scheduler thread ('emitter') owns its own epoll (or kqueue/port) descriptor and jobs are hashed onto emitters by emitter_affinity, so there is no shared event queue. On Linux readiness uses EPOLLONESHOT and a re-arm is a single epoll_ctl(EPOLL_CTL_MOD), with the job's believed kernel state (kmask) cached so it never has to probe with a failing ADD; on kqueue, deferred re-arms are batched into one kevent() call. Commit 41b6106 credits the gain to less bookkeeping per event, removed sanity checks in ph_job_set_nbio() and that syscall avoidance; Concurrency Kit epoch reclamation and per-thread counters keep the hot path free of locks.

## Compared with alternatives

Pick libphenom only if you need its integrated job scheduler, thread pools and TLS streams in plain C and accept vendoring a frozen codebase; for a minimal single-threaded loop libev (also measured faster than libevent) is smaller and maintained, and libhv covers the same 'faster libevent with batteries' ground with active maintenance and a 4-thread pingpong benchmark.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (autotools/libtool build, pkg-config libphenom) |
| **Dependencies** | Concurrency Kit 0.5.0-0.5.1, OpenSSL (1.0.x API), pthreads, pkg-config; autoconf, automake and libtool to build; libevent only for the optional iopipes comparison (--enable-libevent-comparison) |
| **Minimum toolchain** | C99 (configure selects -std=gnu1x on GCC 4.6+, gnu99 below); README says GCC 4.3 or later works best; -O2 is forced because CK breaks without optimization, and -Werror is on unless --enable-lenient |
| **Platforms** | Linux (epoll, timerfd), OS X (kqueue), illumos/Solaris (port_create); FreeBSD 9.1 and OpenBSD 5.2 kqueue builds unmaintained; x86-64 and i686 flags in configure |
| **Thread safety** | Multi-threaded scheduler: jobs are hashed onto scheduler threads by emitter_affinity and jobs with the same hash run serially with respect to each other; ph_job_set_nbio from another thread is deferred and applied by the owning emitter; freeing jobs goes through ph_job_free and an epoch grace period |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw behind the 1.39x Linux number: iopipes.c drives libevent with non-persistent EV_READ events re-added via event_add() in every callback. In libevent 2.0's epoll backend (changelist off by default) a fired non-persistent event is removed with epoll_ctl(EPOLL_CTL_DEL) and the re-add issues epoll_ctl(EPOLL_CTL_ADD), so libevent pays two epoll_ctl calls per event where libphenom pays one EPOLL_CTL_MOD; with EV_PERSIST libevent would pay none. libevent's kqueue backend batches such changes into the next kevent() call, which fits the gap shrinking to 1.07x on OS X (inference from the code, not measured).
- Smaller asymmetries in the same harness: libphenom's NBIO thread is CPU-pinned by default (tid affinity) while the libevent loop is not, and libphenom's 'dispatched' counter also counts its own internal jobs (a 100 ms timerfd tick and the deadline), a negligible inflation of about 10 events/s.
- Every NBIO job is one-shot (EPOLLONESHOT): forget to call ph_job_set_nbio() again in the callback and the descriptor goes silent; since July 2014 an epoll_ctl failure calls ph_panic() and aborts the process instead of returning an error.
- The build pins Concurrency Kit to 0.5.0-0.5.1 and uses pre-1.1 OpenSSL internals, so expect patching before it compiles on a current distribution.

## Known shortcomings

- First-party single \~1 s gut check in commit 41b6106 (Linux 1.39x, OSX 1.07x over libevent on 1024 AF_UNIX socketpairs, -n 1024 -c 1) with no hardware, compiler or libevent version; libevent was driven through the legacy event_set API with non-persistent events (no EV_PERSIST), so it likely paid an extra epoll_ctl per event. Archived 2019. Filed under networking-and-servers/event-loops-io.
- Enricher: iopipes.c drives libevent with non-persistent EV_READ re-added every callback, so libevent 2.0.21 epoll does EPOLL_CTL_DEL plus EPOLL_CTL_ADD per event while libphenom does one EPOLL_CTL_MOD (EPOLLONESHOT); with EV_PERSIST libevent would do none, so the 1.39x Linux gap is overstated (kqueue batches changes, which fits the 1.07x on OSX). libphenom's thread is CPU-pinned by default while the libevent loop is not. Build rot: configure accepts only CK 0.5.0-0.5.1 (issue #84), the OpenSSL code uses pre-1.1 BIO internals, -Werror is on by default, the timer wheel ticks every 100 ms.

## Caveats and trade-offs

First-party, single \~1 s runs from one commit message in June 2013; hardware, compiler, flags and libevent version are all unstated, and OSX and Linux numbers came from different machines. The commit added the -e option 'so that it is simpler to gut check against it'. The libevent side of the harness uses the deprecated libevent 1.x API (event_init/event_set) with non-persistent events re-added after every callback rather than EV_PERSIST, which probably costs libevent's epoll backend extra epoll_ctl calls per event, while the same commit makes libphenom track kernel descriptor state to avoid syscalls; libevent is therefore not shown at its fastest. The commit also notes events/s per core drops as scheduler threads are added. Benchmark code (tests/bench/iopipes.c, run-pipes.php, phenom.R) is public, but no charts or later numbers are checked in. Archived 2019-03-09 (README points to folly); last code commit January 2016. The README itself gives no numbers. Category event-loops-io belongs to wave 5, not one of wave 11's categories.

C99 eventing framework (epoll, kqueue, port_create) with its own job scheduler, buffers, hash tables and JSON variants; depends on Concurrency Kit and OpenSSL; any IO thread can service any descriptor (no thread affinity), so more threads add events/s but with a falling per-core rate on the iopipes workload (commit message).

## Maintenance

Abandoned: archived by Facebook on 2019-03-09 with the last code change in January 2016; Apache-2.0 and copyable, but it needs Concurrency Kit 0.5.x and OpenSSL 1.0.x-era APIs, so treat it as reference code rather than a dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party commit message (41b6106, 9 Jun 2013) with four single \~1 s runs of the public tests/bench/iopipes.c harness (-n 1024 -c 1, with -e for libevent); compiler, flags, CPU model and libevent version are not stated, so it falls short of A and is not independent.
- **Verifier notes:** Numbers match the commit message exactly, but the record wrongly said the descriptor count was unstated: the commands are 'iopipes.t -n 1024 -c 1' (1024 socketpairs). Keep at C; shortcomings: first-party single-run gut check, no hardware/compiler/libevent version, libevent driven with non-persistent events (no EV_PERSIST), only 1.07x on OSX, archived since 2019.
- **Fields the verifier corrected:** `workload`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** first-party commit message (verifier); enricher harness reading
- **Pages the verifier opened:**
  - <https://github.com/facebook/libphenom/commit/41b6106.patch>
  - <https://github.com/facebook/libphenom>
  - <https://github.com/facebook/libphenom/commits/master>
  - <https://raw.githubusercontent.com/facebook/libphenom/HEAD/tests/bench/iopipes.c>
  - <https://raw.githubusercontent.com/facebook/libphenom/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/facebook/libphenom>
  - <https://raw.githubusercontent.com/facebook/libphenom/HEAD/README.markdown>
  - <https://github.com/facebook/libphenom/commit/41b6106>
  - <https://github.com/facebook/libphenom/commits/master>
  - <https://raw.githubusercontent.com/facebook/libphenom/HEAD/tests/bench/iopipes.c>
  - <https://raw.githubusercontent.com/facebook/libphenom/HEAD/configure.ac>
  - <https://raw.githubusercontent.com/facebook/libphenom/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/facebook/libphenom/HEAD/include/phenom/job.h>
  - <https://raw.githubusercontent.com/facebook/libphenom/HEAD/include/phenom/sysutil.h>
  - <https://github.com/facebook/libphenom/tree/master/corelib>
  - <https://github.com/facebook/libphenom/tree/master/corelib/nbio>
  - <https://raw.githubusercontent.com/facebook/libphenom/HEAD/corelib/nbio/epoll.c>
  - <https://raw.githubusercontent.com/facebook/libphenom/HEAD/corelib/nbio/common.c>
  - <https://raw.githubusercontent.com/facebook/libphenom/HEAD/corelib/nbio/kqueue.c>
  - <https://raw.githubusercontent.com/facebook/libphenom/HEAD/corelib/job.c>
  - <https://raw.githubusercontent.com/facebook/libphenom/HEAD/corelib/job.h>
  - <https://github.com/facebook/libphenom/tree/master/corelib/openssl>
  - <https://raw.githubusercontent.com/facebook/libphenom/HEAD/corelib/openssl/bio_bufq.c>
  - <https://raw.githubusercontent.com/facebook/libphenom/HEAD/corelib/openssl/init.c>
  - <https://github.com/facebook/libphenom/issues?q=is%3Aissue>
  - <https://github.com/facebook/libphenom/issues/84>
  - <https://github.com/facebook/libphenom/issues/73>
  - <https://raw.githubusercontent.com/libevent/libevent/release-2.0.21-stable/event.c>
  - <https://raw.githubusercontent.com/libevent/libevent/release-2.0.21-stable/epoll.c>
  - <https://raw.githubusercontent.com/libevent/libevent/release-2.0.21-stable/kqueue.c>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/facebook/libphenom`) · [data/wave11/enrich/raw/github_com_facebook_libphenom.json](../../../data/wave11/enrich/raw/github_com_facebook_libphenom.json) (enrichment confidence 0.75)

</details>
