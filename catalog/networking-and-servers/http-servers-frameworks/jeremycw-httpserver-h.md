# httpserver.h

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP servers and frameworks](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C` · `MIT` · 🟢 active

> Single-header C library for embedding a non-blocking HTTP/1.1 server; the author's 2019 ab hello-world run beat a one-worker nginx 1.14 by about 1.7x.

| | |
|---|---|
| **Beats** | NGINX 1.14.0 (worker_processes 1) |
| **Claimed result** | Keep-alive: 123,907.91 vs 74,441.26 requests/sec (about 1.66x, derived from page data). Connection: close: 27,605.45 vs 15,773.47 requests/sec (about 1.75x, derived from page data). Mean time per request 1.614 ms vs 2.687 ms (keep-alive) and 7.245 ms vs 12.680 ms (close). |
| **Workload** | Hello, World! (13-byte body) served on localhost, ApacheBench with 200 concurrent clients and 100,000 requests, once with keep-alive (ab -k) and once with Connection: close. |
| **Metric** | throughput |
| **Adoption** | 1.9k stars |
| **Last commit** | 2026-04-26 |
| **Links** | [repository](https://github.com/jeremycw/httpserver.h) · [benchmark](https://github.com/jeremycw/httpserver.h) |

## Verdict

The author ran ApacheBench on localhost in December 2019 (ab -c 200 -n 100000, 13-byte Hello, World! body) against nginx 1.14.0 with worker_processes 1: 123,908 vs 74,441 req/s with keep-alive (about 1.66x) and 27,605 vs 15,773 req/s with Connection: close (about 1.75x). No CPU, OS, compiler or flags are given, the server binary came from the 2019 code rather than today's src/ tree, and the author says the run was a reference point, not a claim of superiority.

## Use it when

- Adding a small HTTP endpoint (health check, metrics, local REST control API, debug console) to an existing C or C++ program on Linux, FreeBSD or macOS, with no dependencies beyond POSIX sockets.
- Single-threaded programs that already own a main loop: poll mode handles at most one ready request per http_server_poll call, and http_server_loop exposes the epoll/kqueue descriptor so your own fds can share it.
- Small replies on keep-alive connections from a trusted client or behind a reverse proxy that terminates TLS and HTTP/2, which is the only workload the published numbers cover.
- When you want an MIT-licensed single file you can vendor and patch, and you will keep response headers under about 1 KB (see gotchas).

## Skip it when

- Internet-facing without a hardened proxy in front: the response-header overflow bug below is still on master, issue #77 (signed overflow when parsing Content-Length, filed 2026-05-29) and #72 (keep-alive mis-parsing) are open with no maintainer reply, and there is no TLS.
- Windows (issue #63, no support) or any platform without epoll or kqueue.
- Multi-core throughput: there is one event-loop thread and no worker model; the listening socket sets SO_REUSEPORT, so scaling means running several processes yourself.
- Clients that pipeline HTTP/1.1 requests (wrk pipelining scripts, TechEmpower plaintext): bytes of a second request read together with the first are freed when http_respond swaps the request buffer for the response buffer, so that request is never answered and the connection idles until the 120 s keep-alive timeout.
- Tens of thousands of idle keep-alive connections: on Linux every connection owns a timerfd that wakes the loop once a second, and keep-alive connections are held for 120 s by default.

## How it is fast

One thread runs an edge-triggered epoll (Linux) or kqueue (BSD, macOS) loop over non-blocking sockets. A Ragel-generated state-machine parser records each request element as an (offset, length) token into the read buffer, so request strings are zero-copy slices, and the Date header is cached and refreshed by a one-second timer. Each response is serialized into one buffer and sent with a single write(). Nothing exotic is involved (no io_uring, writev batching or SIMD): epoll_wait takes one event per call, every connection gets its own timerfd, and a request costs several malloc/free pairs, so the win over nginx comes from doing very little per request rather than from a special technique.

## Compared with alternatives

Pick httpserver.h over libuhttpd, Lwan, Kore or H2O when you want one MIT header with no dependencies inside an existing C or C++ program and can live with one thread and HTTP/1.1 only. Those siblings are full servers or frameworks with stronger evidence against nginx (wrk runs, TechEmpower) and multi-core designs, so they are the better choice when throughput or exposure to untrusted clients matters.

## Integration

| | |
|---|---|
| **Form** | header-only (single generated header; #define HTTPSERVER_IMPL in exactly one .c or .cpp file); src/ also builds a CMake static library libhttpsrv, which needs ragel and m4 to regenerate the parser and header |
| **Dependencies** | none at runtime (POSIX sockets; epoll and timerfd on Linux, kqueue on BSD and macOS); ragel and m4 only when rebuilding from src/ |
| **Minimum toolchain** | C99 (CMake sets C_STANDARD 99); usable from C++ through extern "C" (the functional tests have a C++ mode); specific compiler versions not documented |
| **Platforms** | Linux (epoll) and FreeBSD, OpenBSD and macOS (kqueue); no Windows. The single header does not auto-detect the platform: compile with -DEPOLL on Linux or -DKQUEUE on BSD and macOS (only the CMake build detects this). |
| **Thread safety** | not documented; everything runs on one event-loop thread with no locking, so call the API only from that thread |
| **Drop-in for the baseline** | no |

## Gotchas

- Response-header serialization bug (src/respond.c _grwprintf, still on master after the 2026-04-26 va_list fix d095bae): when the headers outgrow the 1024-byte HTTP_RESPONSE_BUF_SIZE, the retry does `bytes += vsnprintf(...)`, counting the overflowing header line twice, so the response carries that many uninitialized heap bytes; if the doubled size passes the new capacity, the next vsnprintf gets a negative length converted to a huge size_t and writes past the buffer. The `>` check is also off by one, so a line that exactly fills the buffer loses its last byte to the NUL. Keep total response headers well under 1 KB or patch it to `bytes = vsnprintf(...)` with a `>=` test. The hello-world benchmark sends about 130 bytes, so this bug sits outside the numbers.
- Keep-alive connections never reset their token array (tokens.size is zeroed only at accept), so http_request_target, http_request_header and the keep-alive check return the first request's offsets applied to the current buffer. A later request with a different-length URL or header layout is mis-read (issue #72, open since 2024-02, no maintainer reply), and the array grows with every request on the connection. The ab -k benchmark repeats one identical request about 500 times per connection with a handler that reads nothing from the request, so it cannot show this bug.
- Benchmark harness flaws: the nginx config in the README cannot be loaded as written (it has no events block, which nginx requires), so the actual file is unknown. It leaves access logging on and keepalive_requests at its default (99,052 of 100,000 keep-alive), and its add_header Content-Type on top of nginx's default_type likely sends two Content-Type headers (about 210 vs 134 bytes per response, derived from page data). Both nginx runs show 1 s connect outliers (max 1029 and 1123 ms) that httpserver.h never hit. The single-threaded ab client at \~124k req/s may itself have been the limit.
- Request strings (http_string_s) are not NUL-terminated and stay valid only until http_respond, which frees the request buffer. hs_write_socket tests a stale errno == EPIPE without checking write()'s return, so a leftover EPIPE can close a connection whose write succeeded. Content-Length parsing overflows int64 on huge values (#77). The documented HTTP_MAX_TOKEN_LENGTH (8 KB) is not what the Ragel parser enforces: src/parser.rl hard-codes 1024 bytes for the request target, 256 for header names and 4096 for header values.

## Known shortcomings

- Tier C: README ab runs vs nginx 1.14.0 (1.66x keep-alive, 1.75x with Connection: close) date from 2019-12-12 and were not re-run after the code was restructured; no compiler, flags or CPU; no bench target in the Makefile; nginx was left with the access log on and default keepalive_requests (99,052 of 100,000 keep-alive, 1 s connect outliers); the author disclaims any superiority claim. MIT, active.
- Enricher: library bug (not behind the numbers): src/respond.c _grwprintf's retry does bytes += vsnprintf once response headers pass 1024 bytes, so an overflowing header line is counted twice (uninitialized heap bytes sent, heap write past the buffer when the doubled size exceeds the new capacity; still on master after the 2026-04-26 va_list fix d095bae); off-by-one truncation at exact fit. tokens.size is never reset on keep-alive (#72, open), so later requests get the first request's offsets (ab -k repeats one identical request, hiding it); pipelined requests dropped; stale errno EPIPE check; Content-Length overflow #77 open; must define -DEPOLL or -DKQUEUE. Harness: the README nginx conf cannot load as shown (no events block), access log on, add_header Content-Type likely duplicates the header, ab is single-threaded and may cap the about 124k req/s.

## Caveats and trade-offs

The author states the run was only a micro-benchmark for a performance reference point and explicitly makes no statement of superiority, since httpserver.h is not a competitor or replacement for NGINX. Compiler, flags and CPU model are not stated, and the repo has no benchmark target (the Makefile only builds Debug tests and a -O0 fuzzer), so the exact server binary and build are unknown. The numbers date from the README's first commits (2019-12-12) and were never re-run; the library has since been restructured (src/ split, m4-generated single header, 2026 socket-leak fixes). The nginx config shown is minimal (worker_processes 1, a return 200 location) and does not disable access logging; nginx also sent more bytes per response (about 210 vs 134 keep-alive and 205 vs 129 close, derived from page data) because of its headers. In the keep-alive run nginx served 99,052 of 100,000 requests as keep-alive (consistent with nginx's default keepalive_requests 100 forcing reconnects) and had 1 s connect outliers (max 1150 ms), so the keep-alive gap partly reflects nginx defaults. Hello-world workload with ab as a single-threaded client on localhost, nginx version from 2018 (1.14.0). Own benchmark with partial methodology, so tier C. [retier] README ab runs (2019-12-12, never re-run after the restructure): 1.66x keep-alive and 1.75x close vs nginx 1.14.0 with access log on, default keepalive_requests and a conf that does not load as shown; ab single-threaded; no compiler, flags or CPU. Library: header lines over 1024 bytes counted twice in _grwprintf (heap over-write), keep-alive token offsets never reset (#72), pipelining dropped, Content-Length overflow #77; needs -DEPOLL or -DKQUEUE.

Single-header C library, event driven and non-blocking, epoll on Linux and kqueue on BSD and macOS; no Windows support, no TLS or HTTP/2 mentioned in the README, and far fewer features than nginx.

## Maintenance

Dormant from 2023 until a burst of fixes and fuzzing on 2026-04-25/26 (socket leak, va_list reuse), but the response-header overflow above is still on master and keep-alive mis-parsing (#72) and Content-Length overflow (#77) are open without maintainer replies. It is MIT-licensed and one file, so vendor it and patch those bugs before exposing it to untrusted clients.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now D.
- **Tier reason:** The README Benchmark section shows the author's own ApacheBench runs against nginx/1.14.0 (worker_processes 1) with every quoted number present (123907.91 vs 74441.26 req/s keep-alive, 27605.45 vs 15773.47 req/s Connection: close), but no compiler, flags, CPU model or benchmark server source/build target is given, so first-party with partial methodology: C.
- **Retiered** C to D: The 2019 ab numbers come from an nginx baseline configured as shown in a README conf that cannot load (no events block) with the access log on and default keepalive_requests, driven by single-threaded ab, with no compiler, flags or CPU and no bench target; the author disclaims superiority (crippled-baseline precedent). Directional only.
- **Verifier notes:** Numbers, baseline, MIT license, 1.9k stars, last commit 2026-04-26 (active) all verified. Shortcomings: 2019 numbers on an older code version, no compiler/flags/CPU, no benchmark build target in repo, nginx left at default access logging and keepalive_requests, author disclaims any superiority claim.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-75 (wave 5); enricher (wave 5)
- **Pages the verifier opened:**
  - <https://github.com/jeremycw/httpserver.h>
  - <https://github.com/jeremycw/httpserver.h/commits>
  - <https://github.com/jeremycw/httpserver.h/commits/master/README.md>
  - <https://raw.githubusercontent.com/jeremycw/httpserver.h/HEAD/README.md>
  - <https://raw.githubusercontent.com/jeremycw/httpserver.h/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/jeremycw/httpserver.h/HEAD/Makefile>
- **Sources the enricher read:**
  - <https://github.com/jeremycw/httpserver.h>
  - <https://raw.githubusercontent.com/jeremycw/httpserver.h/HEAD/README.md>
  - <https://raw.githubusercontent.com/jeremycw/httpserver.h/HEAD/httpserver.h>
  - <https://raw.githubusercontent.com/jeremycw/httpserver.h/HEAD/Makefile>
  - <https://raw.githubusercontent.com/jeremycw/httpserver.h/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/jeremycw/httpserver.h/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/jeremycw/httpserver.h/HEAD/src/CMakeLists.txt>
  - <https://raw.githubusercontent.com/jeremycw/httpserver.h/HEAD/src/httpserver.m4>
  - <https://raw.githubusercontent.com/jeremycw/httpserver.h/HEAD/src/respond.c>
  - <https://raw.githubusercontent.com/jeremycw/httpserver.h/HEAD/src/write_socket.c>
  - <https://raw.githubusercontent.com/jeremycw/httpserver.h/HEAD/src/parser.rl>
  - <https://raw.githubusercontent.com/jeremycw/httpserver.h/HEAD/test/functional/functional-test-runner>
  - <https://github.com/jeremycw/httpserver.h/issues?q=is%3Aissue>
  - <https://github.com/jeremycw/httpserver.h/issues/77>
  - <https://github.com/jeremycw/httpserver.h/issues/72>
  - <https://github.com/jeremycw/httpserver.h/issues/73>
  - <https://github.com/jeremycw/httpserver.h/issues/46>
  - <https://github.com/jeremycw/httpserver.h/commits/master>
  - <https://github.com/jeremycw/httpserver.h/commits/master/src/respond.c>
  - <https://github.com/jeremycw/httpserver.h/commit/d095bae>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/jeremycw/httpserver.h`) · [data/wave5/enrich/raw/github_com_jeremycw_httpserver_h.json](../../../data/wave5/enrich/raw/github_com_jeremycw_httpserver_h.json) (enrichment confidence 0.75)

</details>
