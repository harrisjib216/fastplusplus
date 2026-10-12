# Go net TCP echo server (Boost.Redis echo benchmark, vs libuv)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Concurrency runtimes](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Go` · `BSD-3-Clause` · 🟢 active

> Go's net package with one goroutine per connection, as a TCP echo server; about 1.22x less wall time than the libuv docs example.

| | |
|---|---|
| **Beats** | libuv TCP echo server (C, epoll event loop, libuv docs tcp-echo-server example); the table also holds a Boost.Asio C++20 coroutine echo server that is faster than Go |
| **Claimed result** | Go 35.6 s vs libuv 43.6 s wall time for 1000 connections x 5000 echoes (about 1.22x less wall time, derived from page data); Boost.Asio (C++) 29.5 s is about 1.21x faster than Go (derived from page data). Each value is a single run; the Go value was recorded on 2022-08-25 after the Go server was rewritten (it was 81.0 s before), the libuv value by 2022-07-15. Doc text: 'Go did surprise me: faster than nodejs and libuv!' |
| **Workload** | TCP echo server serving 1000 concurrent client connections on localhost (the Boost.Redis echo_server_client driver, benchmarks.tex comment 'time ./echo_server_client 1000 5000'); metric is the total wall-clock seconds the client run took against each server, one server per language/library, each written from that library's own docs example. |
| **Metric** | throughput |
| **Compiler and flags** | libuv server: 'gcc echo_server_direct.c -luv -O2 -o echo_server_direct' (benchmarks/c/libuv/README.md), linked against an unstated system libuv build. Go server: version and build command not stated; runtime.GOMAXPROCS(1), one goroutine per connection, 1024-byte buffer. Asio server/client: CMake target with C++20 (benchmarks/CMakeLists.txt), compiler and optimisation level not stated. |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | not stated |
| **Adoption** | 139.2k stars (golang/go); suite repo boostorg/redis has 282 stars |
| **Last commit** | 2026-10-10 |
| **Links** | [repository](https://github.com/golang/go) · [benchmark](https://raw.githubusercontent.com/boostorg/redis/develop/benchmarks/benchmarks.tex) |

## Verdict

Each server had one timed run of the single-threaded Boost.Asio client (1000 localhost connections x 5000 13-byte echoes) on the author's unnamed machine (localhost latency 0.07 ms). The rewritten Go net server took 35.6 s, the libuv docs example built with gcc -O2 took 43.6 s (about 1.22x more), Asio took 29.5 s and Tokio 30.7 s. No CPU, OS, Go, libuv or compiler versions are given.

## Use it when

- New network services with many concurrent, mostly idle connections exchanging small messages, where one blocking goroutine per connection is the easiest correct design.
- When the C alternative under consideration is a straightforward libuv callback server written from the docs, without buffer pooling.
- Single-process, single-core deployments: the measured server pinned itself to GOMAXPROCS(1) and still beat the libuv example on 1000 localhost connections.

## Skip it when

- When C++ is an option: the Boost.Asio C++20 coroutine echo server in the same chart took 29.5 s against Go's 35.6 s, and Tokio took 30.7 s.
- As proof that Go beats libuv: the libuv server allocates per message and was never revised, while the Go server was rewritten before its 35.6 s run; a libuv server that reuses its buffers was not measured.
- Latency-critical paths that cannot tolerate garbage-collector work or scheduler latency; no tail-latency figures exist, only total wall time.
- Inside an existing C or C++ process: Go needs cgo or a separate process, plus its own runtime and garbage collector.

## How it is fast

The code is blocking-style but runs on Go's netpoller. A conn.Read that hits EAGAIN parks the goroutine (internal/poll FD.Read calls waitRead), the runtime's edge-triggered epoll wakes it, and the scheduler runs ready goroutines on the single P without an OS thread per connection. Each echo is one read and one write syscall into a buffer reused for the whole connection. The libuv baseline does the same syscalls but, as the unmodified docs example, mallocs a 64 KiB read buffer on every read callback (libuv passes 64 \* 1024 as suggested_size) and a write request on every echo, then frees both. The measured gap therefore comes mostly from the baseline's per-message allocation, not from a Go runtime advantage.

## Compared with alternatives

The Tokio echo entry runs the same harness and is faster (30.7 s against 35.6 s), so pick Go only when its blocking goroutine style and standard library outweigh about 16% more wall time. Pick evio or Redcon (Go event-loop frameworks) when you need more requests per second than net's goroutine-per-connection model gives and can accept a callback API.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none beyond the Go standard library (net, runtime, fmt, os) |
| **Minimum toolchain** | Not stated; measured in August 2022 with an unrecorded Go version; the code uses only long-stable net APIs |
| **Platforms** | any Go platform; on Linux the netpoller uses edge-triggered epoll (runtime/netpoll_epoll.go); other OS pollers not checked |
| **Thread safety** | not documented in the pages read; the benchmark gives each connection its own goroutine and shares no state |
| **Drop-in for the baseline** | no |

## Gotchas

- The doc page's 'code used' link for Go points to commit 3fb018c, the earlier bufio.ReadBytes server that scored 81.0 s, not the f11622e rewrite behind the 35.6 s bar. That old server never left its loop on EOF or error, because `break` inside its switch exits only the switch, so each goroutine kept calling ReadBytes and Write on a closed socket after its client finished, with no GOMAXPROCS cap. That bug probably explains part of the 81.0 s to 35.6 s drop (inferred from the code, not measured).
- Each bar is one `time ./echo_server_client 1000 5000` run, and the bars were recorded on different dates (libuv by 2022-07-15, Go 2022-08-25, Asio re-run 2022-10-07). The client catches each session's exception, prints it to stderr and carries on, and it never counts completed echoes. Nothing in the repo shows that all 5,000,000 round trips completed in every run.
- The libuv baseline is the docs example built with `gcc -O2` against an unstated system libuv. It mallocs and frees a 64 KiB buffer and a write_req_t per message, while the Go, Asio and Tokio servers reuse one 1 KiB buffer per connection.
- The current Go server checks the stale read error after conn.Write, so write errors are ignored, and it never closes connections. Both are harmless for a single timed run but need fixing before reuse.

## Known shortcomings

- Beats only the libuv docs example (a 64 KiB malloc plus write_req per message, gcc -O2) in single runs from different dates (libuv by 2022-07-15, Go 2022-08-25 after a rewrite from 81.0 to 35.6 s), no CPU or versions, and loses to Asio (29.5 s): no valid same-run measurement (tier D).
- The doc page links the Go code at 3fb018c, the old bufio server behind the 81.0 s row, not the f11622e rewrite behind the 35.6 s row; the old server never exits its loop on EOF (a break inside a switch), so goroutines spin on closed sockets, likely inflating the 81.0 s. The client swallows per-session errors and never counts completed echoes; libuv mallocs 64 KiB plus a write_req per message; gcc -O2.

## Caveats and trade-offs

Numbers are the pgfplots source (benchmarks.tex) of the chart on the Boost.Redis doc page 'Echo server benchmark' (doc/modules/ROOT/pages/benchmarks.adoc); the rendered PNG on boostorg.github.io was not viewed. The chart is a composite of single `time` runs recorded on different dates by the Boost.Redis (C++) author on 'my machine' (localhost latency 0.07 ms; no CPU model, OS, Go/Rust/compiler versions, no repetitions or variance): libuv 43.568 s was recorded by 2022-07-15 (commit 3fb018c) and never re-run; Tokio moved from 42.2 s/43.2 s to 30.7 s on 2022-07-16 after switching to a newer Tokio and the current_thread runtime; Go moved from 81.0 s to 35.6 s on 2022-08-25 (commit f11622e) after its server was rewritten from bufio ReadBytes line echo to a raw 1024-byte read loop with GOMAXPROCS(1); Asio was re-measured at 29.5 s on 2022-10-07. Unequal work: the libuv server is the unmodified libuv docs tcp-echo-server example, which mallocs a 64 KiB read buffer (libuv passes 64\*1024 as suggested_size, src/unix/stream.c) on every read callback and a write_req_t per echo and frees both after each write, while the Go, Tokio and Asio servers reuse one 1 KiB buffer per connection; the Go server was revised between runs, the libuv one never was. The libuv server is built per benchmarks/c/libuv/README.md with 'gcc echo_server_direct.c -luv -O2' (not -O3; system libuv build flags unknown). The load generator is the single-threaded Boost.Asio echo_server_client (1000 sessions x 5000 13-byte ping-pong messages) on the same host, which may set a floor near the Asio/Tokio results. All servers are single-threaded (Asio io_context with BOOST_ASIO_CONCURRENCY_HINT_UNSAFE_IO, Tokio current_thread, Go GOMAXPROCS(1), one libuv loop). The C++ Boost.Asio coroutine server in the same table is the fastest entry (29.5 s), so this is not a win over the best C++ result. The author gives no explanation for the gap beyond 'I expected Libuv to have similar performance to Asio and Tokio'. The Go server ignores conn.Write's return value (its error check tests the stale read error), harmless for timing. Measured in 2022 (Go about 1.19); the doc page is unchanged since. [retier] The doc page links the Go code at 3fb018c (the old bufio server behind the 81.0 s row), not the f11622e rewrite behind the 35.6 s row; the old server never exits its loop on EOF, so goroutines spin on closed sockets, likely inflating the 81.0 s. The client swallows per-session errors and never counts completed echoes; libuv mallocs 64 KiB plus a write_req per message; gcc -O2.

Go brings a garbage-collected runtime and goroutine scheduler with its own netpoller; calling Go from C++ goes through cgo or a separate process.

## Maintenance

Go is active and BSD-3-Clause licensed. The evidence is a 2022 single-run composite chart that the 2025 doc page still shows unchanged (and links the wrong Go code for), against an allocation-heavy C example, so it supports only a directional, tier-D claim.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification C, tier now D.
- **Tier reason:** Numbers are real (benchmarks.tex: Asio 29.5 s, Tokio 30.7 s, Go 35.6 s, Libuv 43.6 s, Nodejs 74.2 s) and server code is public (benchmarks/go/echo_server_direct.go, benchmarks/c/libuv/echo_server_direct.c, benchmarks/cpp/asio/echo_server_client.cpp), but there is no CPU model or Go version, each bar is one run recorded on a different date (libuv by 2022-07-15, Go 2022-08-25 after a server rewrite), and the C side is the libuv docs example that mallocs a 64 KiB read buffer and a write request per message at -O2 while Go reuses one 1 KiB buffer: crippled-baseline and cross-run precedents put the Go-over-C claim at D.
- **Verifier notes:** Downgrade C to D: the only C baseline Go beats is the unmodified libuv docs example (per-message 64 KiB malloc plus write-request malloc, -O2) recorded weeks before the revised Go server, one run each; Go loses to the C++ Asio server (29.5 s) in the same table. Shortcomings for decisions.json: composite single-run chart across July-October 2022, no hardware or versions, unequal buffer management, -O2 C build, single-threaded client may cap results.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-31 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/boostorg/redis/develop/benchmarks/benchmarks.tex>
  - <https://raw.githubusercontent.com/boostorg/redis/develop/doc/modules/ROOT/pages/benchmarks.adoc>
  - <https://github.com/boostorg/redis/tree/develop/benchmarks>
  - <https://github.com/boostorg/redis/tree/develop/doc/modules/ROOT/pages>
  - <https://github.com/boostorg/redis/tree/develop/benchmarks/c/libuv>
  - <https://raw.githubusercontent.com/boostorg/redis/develop/benchmarks/c/libuv/README.md>
  - <https://raw.githubusercontent.com/boostorg/redis/develop/benchmarks/c/libuv/echo_server_direct.c>
  - <https://raw.githubusercontent.com/boostorg/redis/develop/benchmarks/go/echo_server_direct.go>
  - <https://raw.githubusercontent.com/boostorg/redis/develop/benchmarks/cpp/asio/echo_server_direct.cpp>
  - <https://raw.githubusercontent.com/boostorg/redis/develop/benchmarks/cpp/asio/echo_server_client.cpp>
  - <https://raw.githubusercontent.com/boostorg/redis/develop/benchmarks/CMakeLists.txt>
  - <https://github.com/boostorg/redis/commits/develop/benchmarks/benchmarks.tex>
  - <https://github.com/boostorg/redis/commits/develop/benchmarks/go/echo_server_direct.go>
  - <https://github.com/boostorg/redis/commit/f11622e74678f9d1b9082bad103798871591f6d4>
  - <https://raw.githubusercontent.com/boostorg/redis/3fb018ccc6138d310ac8b73540391cdd8f2fdad6/benchmarks/benchmarks.tex>
  - <https://raw.githubusercontent.com/boostorg/redis/ab68e8a31dd5f10a2b6ecfd6aec44bab71233aae/benchmarks/benchmarks.tex>
  - <https://raw.githubusercontent.com/boostorg/redis/f11622e74678f9d1b9082bad103798871591f6d4/benchmarks/benchmarks.tex>
  - <https://raw.githubusercontent.com/boostorg/redis/ba82c6cd8487eca9b3142f34c8ad7b2ff16548b1/benchmarks/benchmarks.tex>
  - <https://raw.githubusercontent.com/libuv/libuv/v1.x/src/unix/stream.c>
  - <https://github.com/boostorg/redis>
  - <https://github.com/golang/go>
  - <https://github.com/golang/go/commits/master>
- **Sources the enricher read:**
  - <https://github.com/golang/go>
  - <https://raw.githubusercontent.com/golang/go/master/src/runtime/netpoll_epoll.go>
  - <https://raw.githubusercontent.com/golang/go/master/src/internal/poll/fd_unix.go>
  - <https://raw.githubusercontent.com/boostorg/redis/develop/benchmarks/benchmarks.tex>
  - <https://raw.githubusercontent.com/boostorg/redis/develop/doc/modules/ROOT/pages/benchmarks.adoc>
  - <https://raw.githubusercontent.com/boostorg/redis/develop/benchmarks/go/echo_server_direct.go>
  - <https://raw.githubusercontent.com/boostorg/redis/develop/benchmarks/c/libuv/echo_server_direct.c>
  - <https://raw.githubusercontent.com/boostorg/redis/develop/benchmarks/c/libuv/README.md>
  - <https://raw.githubusercontent.com/boostorg/redis/develop/benchmarks/cpp/asio/echo_server_direct.cpp>
  - <https://raw.githubusercontent.com/boostorg/redis/develop/benchmarks/cpp/asio/echo_server_client.cpp>
  - <https://raw.githubusercontent.com/boostorg/redis/develop/benchmarks/CMakeLists.txt>
  - <https://raw.githubusercontent.com/boostorg/redis/develop/benchmarks/rust/echo_server_direct/src/main.rs>
  - <https://raw.githubusercontent.com/boostorg/redis/develop/benchmarks/nodejs/echo_server_direct/echo_server_direct.js>
  - <https://raw.githubusercontent.com/boostorg/redis/3fb018ccc6138d310ac8b73540391cdd8f2fdad6/benchmarks/go/echo_server_direct.go>
  - <https://raw.githubusercontent.com/boostorg/redis/3fb018ccc6138d310ac8b73540391cdd8f2fdad6/benchmarks/benchmarks.tex>
  - <https://github.com/boostorg/redis/commit/f11622e74678f9d1b9082bad103798871591f6d4>
  - <https://github.com/boostorg/redis/commits/develop/benchmarks/benchmarks.tex>
  - <https://raw.githubusercontent.com/libuv/libuv/v1.x/src/unix/stream.c>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:go/boostorg/redis#tcp-echo-direct`) · [data/wave14/enrich/raw/lang_go_boostorg_redis_tcp_echo_direct.json](../../../data/wave14/enrich/raw/lang_go_boostorg_redis_tcp_echo_direct.json) (enrichment confidence 0.55)

</details>
