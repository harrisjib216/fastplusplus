# wepoll

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [Event loops and async I/O](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `BSD-2-Clause` · 🔴 abandoned

> Linux epoll API for Windows sockets on the AFD driver; flat 1.4 us select cost where select() grows linearly.

| | |
|---|---|
| **Beats** | Winsock select() as used by the JDK's legacy select-based Windows Selector (WindowsSelectorImpl); measured through the JDK NIO Selector, not wepoll against raw select()/WSAPoll in C |
| **Claimed result** | wepoll-based Selector vs select-based Selector, ns/op: 1 channel 1428.914 vs 1587.429 (about 1.1x); 10 channels 1429.806 vs 2515.324 (about 1.8x); 100 channels 1433.371 vs 10903.445 (about 7.6x); 1000 channels 1435.007 vs 101651.369 (about 71x); 10000 channels 1445.201 vs 932032.385 (about 645x) (ratios derived from page data). wepoll-based cost stays flat at about 1.43-1.45 us from 1 to 10,000 registered channels while the select-based cost grows linearly. The PR author states the benefit as selection cost depending on ready sockets rather than registered channels. |
| **Workload** | OpenJDK JMH microbenchmark SelectOne.testSelectOne: time per Selector.select() call with N loopback SocketChannels registered for OP_READ and one of them ready, N = 1, 10, 100, 1000, 10000; JDK 17 wepoll-based Selector vs the pre-existing select()-based Selector, on Windows Server 2019. |
| **Metric** | latency |
| **Hardware** | Windows Server 2019; CPU model and JDK build not stated on the PR page |
| **Adoption** | 1.1k stars; vendored in OpenJDK's Windows Selector since JDK 17 (JDK-8266369, PR 3816 integrated 2021-05-08) |
| **Last commit** | 2020-11-30 |
| **Links** | [repository](https://github.com/piscisaureus/wepoll) · [benchmark](https://github.com/openjdk/jdk/pull/3816) |

## Verdict

Alan Bateman's JMH SelectOne.testSelectOne run in OpenJDK PR 3816 (Windows Server 2019, CPU and JDK build not stated) timed Selector.select() with one of N loopback channels readable: the wepoll-based Selector stayed at 1428.914-1445.201 ns/op for N = 1 to 10,000, while the JDK's select()-based Selector rose from 1587.429 to 932032.385 ns/op (about 1.1x to 645x, derived from page data). The harness checks that each select returns exactly one key and never drains the ready byte, so it measures steady-state re-reporting of one ready socket, not registration churn, many ready sockets or WSAPoll/IOCP; libevent PR #1006 independently found wepoll faster than libevent's win32 backend above about 100 connections in libevent's bench (charts only, no readable numbers) and no difference in an HTTP-server test.

## Use it when

- Porting a Linux epoll event loop (servers, proxies, message brokers) to Windows while keeping readiness semantics instead of rewriting for IOCP.
- Windows processes that register thousands to 100,000s of mostly idle sockets: the OpenJDK JMH run stays at about 1.43-1.45 us per select from 1 to 10,000 channels while the select()-based selector reaches 932 us.
- Replacing select() in code that hits the 1024-socket FD_SETSIZE ceiling or uses helper threads to get past it, as the JDK's old WindowsSelectorImpl did.
- Several threads waiting on the same epoll port, or one socket in several epoll sets, which the README lists as supported.

## Skip it when

- Low socket counts: at 1 channel the JDK gain is only about 1.1x, and libevent's maintainers saw 'no significant change' versus the win32 select backend in an Apache Bench HTTP-server test (libevent PR #1006).
- Edge-triggered designs: EPOLLET, EPOLLEXCLUSIVE and EPOLLWAKEUP are not supported, and only sockets can be polled (no pipes, files, events or eventfd; issues #17 and #8 are open since 2020 and 2018).
- Code that wants completion-based I/O with AcceptEx/ConnectEx or zero-byte-receive close detection: a libevent reviewer argued for keeping libevent's IOCP backend for exactly those reasons (PR #1006).
- Multi-threaded programs that delete and re-add a socket while another thread is in epoll_wait: issue #35 (open since December 2023, no fix) reports lost events on Windows Server 2016 through Windows 11; using EPOLL_CTL_MOD avoided it.
- Projects that need an actively maintained dependency: no master commits since 2020-11-30 and the dist release is 1.5.8, although OpenJDK still vendors it.

## How it is fast

Instead of passing the whole socket set to select() or WSAPoll() on every call, wepoll keeps one overlapped IOCTL_AFD_POLL request pending per socket on a \Device\Afd handle (opened with NtCreateFile; up to 32 sockets share one AFD handle as a poll group) and routes completions to an I/O completion port, which epoll_wait drains with GetQueuedCompletionStatusEx (up to 256 entries on the stack). Idle sockets cost nothing per wait, so wait cost scales with ready sockets, not registered ones; level-triggered behaviour comes from re-submitting a socket's AFD poll after each completion. Interest changes from epoll_ctl are queued and applied at the next wait, sockets are found through a red-black tree keyed by SOCKET, and the ntdll entry points are resolved at runtime with GetProcAddress.

## Compared with alternatives

Pick wepoll when you need epoll-style readiness on Windows specifically: none of the catalogued siblings documents a scalable Windows readiness path (libevent's default Windows backend is select-based and it now offers wepoll as an opt-in backend), and Condy, uring_exec, Asio's io_uring backend and the other io_uring siblings are Linux-only.

## Integration

| | |
|---|---|
| **Form** | source-drop (wepoll.c + wepoll.h from the dist branch); master also has a CMake build |
| **Dependencies** | Windows SDK only: Winsock (ws2_32) plus undocumented ntdll functions (NtCreateFile, NtDeviceIoControlFile, NtCancelIoFileEx, keyed events) resolved at runtime |
| **Minimum toolchain** | C; recent MSVC, Clang or GCC per README (open issues: VS2010 does not compile, #45; VS2022 ALL_BUILD fails on cast warnings, #38) |
| **Platforms** | Windows Vista or later (_WIN32_WINNT 0x0600); CPU architectures not documented; sockets only |
| **Thread safety** | Fully thread-safe per README: multiple threads may call epoll_wait on one port and epoll_ctl concurrently, with a critical section per port and an SRW-locked handle tree; but see issue #35 for lost events under concurrent DEL+ADD. |
| **Drop-in for the baseline** | partial: epoll-style replacement for select()/WSAPoll loops, but the caller must switch to the epoll API, use HANDLE ports and epoll_close(), and give up edge-triggered mode |

## Gotchas

- Relies on the undocumented AFD poll IOCTL (0x00012024) and ntdll calls, so a Windows change could break it; OpenJDK kept the select-based selector as a fallback behind -Djava.nio.channels.spi.SelectorProvider=sun.nio.ch.WindowsSelectorProvider.
- Always EPOLL_CTL_DEL a socket before closesocket(): when Windows reuses the SOCKET value, the old socket's AFD_POLL_LOCAL_CLOSE can delete the new socket's registration (issue #34, closed with that README advice, no code change).
- The dist 1.5.8 header defines EPOLLONESHOT as 1&lt;&lt;31 (Linux's EPOLLET bit); master fixed it to 1&lt;&lt;30 on 2020-11-30 but never cut a new dist release, so code that defines Linux numeric flags itself can get one-shot behaviour silently. OpenJDK's copy also uses 1&lt;&lt;31.
- epoll_ctl changes are queued and applied on the next epoll_wait (or immediately only if a thread is currently polling), and epoll_wait mallocs a completion array on every call when maxevents exceeds 256.

## Known shortcomings

- Tier B on openjdk/jdk PR 3816 JMH (SelectOne, 1445 ns vs 932032 ns at 10000 channels, about 645x derived): measured only through the JDK NIO Selector against the JDK select() Selector (1024-fd cap with a helper thread per extra 1023 channels, so the 10000-channel ratio includes thread coordination), not raw select/WSAPoll/IOCP; CPU and build flags unstated; one ready socket; no first-party numbers. Abandoned since 2020-11-30 but vendored in openjdk master (WEPollSelectorProvider default).
- Enricher: the SelectOne harness is sound (checks nselected == 1 each call) but measures only the steady re-report of one ready socket, with no registration churn, many-ready case, WSAPoll or IOCP; libevent PR #1006 (merged 2020-05-08) is a second independent source showing wepoll faster than the win32 select backend above about 100 connections (charts only) and no difference in an ab HTTP-server test. Issue #35 lost events with concurrent DEL+ADD (open since 2023-12), #34 SOCKET reuse race needs DEL before close, dist 1.5.8 defines EPOLLONESHOT as 1&lt;&lt;31 (Linux's EPOLLET bit, fixed on master only), undocumented AFD IOCTL; abandoned since 2020-11-30.

## Caveats and trade-offs

The only numbers are third-party and indirect. They come from an OpenJDK maintainer's JMH run of the JDK Selector built on wepoll (PR 3816, Windows Server 2019), so the roughly 1.4 us floor includes JVM/JNI and Selector overhead, and the gain at 1 channel is only about 1.1x. The baseline is the JDK's own select() Selector (WindowsSelectorImpl), not WSAPoll, IOCP, or raw select() in C; that selector caps each select() call at MAX_SELECTABLE_FDS = 1024 and adds one helper thread per further 1023 channels, so the 10000-channel row (about 645x) also includes helper-thread coordination, while the 100 and 1000 rows are a single linear select(). One ready socket only; the PR notes an exception (select after wakeup) where the old Selector skips selection and gives no number. CPU model and JDK build flags are not stated, and the PR rows show Cnt 20 while the current benchmark file in openjdk/jdk (test/micro/org/openjdk/bench/java/nio/channels/SelectOne.java) uses @Fork(3) with 5 warmup and 5 measurement iterations, so rerunning would use different settings. wepoll's own README makes only qualitative claims ('fast and scalable', 'can poll 100000s of sockets efficiently') with no numbers. No commits since 2020-11-30 on master (default branch dist last updated 2020-06-29, version 1.5.8); the maintenance status follows the over-3-years rule, but the library is stable and still vendored: openjdk/jdk master carries src/java.base/windows/native/libnio/ch/wepoll.c and its Windows DefaultSelectorProvider is WEPollSelectorProvider.

Windows only (Vista or later), sockets only; level-triggered and one-shot modes, no EPOLLET or EPOLLEXCLUSIVE; epoll port is a HANDLE, not a file descriptor; distributed as a single wepoll.c plus wepoll.h; builds with MSVC, Clang and GCC. The JDK PR text describes it as wrapping the Ancillary Function Driver for Winsock behind an epoll-like interface.

## Maintenance

Abandoned upstream (last master commit 2020-11-30, dist 1.5.8 of 2020-06-29) with open lost-event and build issues, but BSD-2-Clause, two files, and still vendored in OpenJDK's default Windows Selector and offered as a libevent backend, so it is practical to vendor and patch.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Independent measurement: OpenJDK maintainer Alan Bateman's JMH run (SelectOne.testSelectOne, avgt ns/op, Cnt 20) in reviewed and integrated openjdk/jdk PR 3816 shows the wepoll-based Selector flat at 1428.914-1445.201 ns/op versus the select()-based Selector rising from 1587.429 to 932032.385 ns/op for 1 to 10000 channels. The benchmark code is public (test/micro/org/openjdk/bench/java/nio/channels/SelectOne.java) but CPU model, JDK build and compiler flags are not stated, so not A.
- **Verifier notes:** Record accurate: all ten ns/op figures match the PR page, ratios correctly marked derived, BSD-2-Clause confirmed from LICENSE, 1.1k stars, last master commit 2020-11-30, not archived. Shortcomings to record: indirect measurement through the JDK NIO Selector, baseline is the JDK's select()-based Selector with helper threads beyond 1023 channels (not raw select/WSAPoll/IOCP), CPU and build flags unstated, one ready socket only, no first-party numbers, abandoned since 2020 but still vendored in OpenJDK.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-81 (wave 5); enricher w5 pair-030
- **Pages the verifier opened:**
  - <https://github.com/openjdk/jdk/pull/3816>
  - <https://github.com/piscisaureus/wepoll>
  - <https://github.com/piscisaureus/wepoll/commits>
  - <https://github.com/piscisaureus/wepoll/commits/master>
  - <https://github.com/piscisaureus/wepoll/branches>
  - <https://raw.githubusercontent.com/piscisaureus/wepoll/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/openjdk/jdk/master/test/micro/org/openjdk/bench/java/nio/channels/SelectOne.java>
  - <https://raw.githubusercontent.com/openjdk/jdk/master/src/java.base/windows/classes/sun/nio/ch/WindowsSelectorImpl.java>
  - <https://raw.githubusercontent.com/openjdk/jdk/master/src/java.base/windows/classes/sun/nio/ch/DefaultSelectorProvider.java>
  - <https://raw.githubusercontent.com/openjdk/jdk/master/src/java.base/windows/native/libnio/ch/wepoll.c>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/piscisaureus/wepoll/HEAD/README.md>
  - <https://raw.githubusercontent.com/piscisaureus/wepoll/dist/wepoll.c>
  - <https://raw.githubusercontent.com/piscisaureus/wepoll/dist/wepoll.h>
  - <https://raw.githubusercontent.com/piscisaureus/wepoll/master/include/wepoll.h>
  - <https://github.com/piscisaureus/wepoll/issues>
  - <https://github.com/piscisaureus/wepoll/issues/35>
  - <https://github.com/piscisaureus/wepoll/issues/41>
  - <https://github.com/piscisaureus/wepoll/issues/34>
  - <https://github.com/piscisaureus/wepoll/commits/master>
  - <https://github.com/openjdk/jdk/pull/3816>
  - <https://raw.githubusercontent.com/openjdk/jdk/master/test/micro/org/openjdk/bench/java/nio/channels/SelectOne.java>
  - <https://raw.githubusercontent.com/openjdk/jdk/master/src/java.base/windows/native/libnio/ch/wepoll.h>
  - <https://github.com/libevent/libevent/pull/1006>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/piscisaureus/wepoll`) · [data/wave5/enrich/raw/github_com_piscisaureus_wepoll.json](../../../data/wave5/enrich/raw/github_com_piscisaureus_wepoll.json) (enrichment confidence 0.75)

</details>
