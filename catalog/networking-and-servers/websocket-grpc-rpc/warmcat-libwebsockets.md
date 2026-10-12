# libwebsockets

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [WebSocket, gRPC and RPC](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟢 active

> Pure C client/server library for WebSockets, HTTP/1-2-3 and MQTT; in a 2016 competitor table it used \~5.7x less memory per connection than WebSocket++.

| | |
|---|---|
| **Beats** | WebSocket++ (websocketpp) v0.7.0 |
| **Claimed result** | The page gives only uWebSockets (uWS) ratios: uWS is 11x as lightweight as libwebsockets 2.0 and 63x as lightweight as WebSocket++ v0.7.0; connection performance uWS equal to libwebsockets and 4x WebSocket++; short messages uWS 6x libwebsockets and 3x WebSocket++; huge messages uWS 4x libwebsockets and 2x WebSocket++. Derived from page data: libwebsockets is about 5.7x lighter than WebSocket++ in memory and about 4x faster at connection setup, but about 2x slower than WebSocket++ on short-message and huge-message echo throughput. |
| **Workload** | uWebSockets author's WebSocket echo-server benchmarks run with default settings: scalability (memory per connection and connection rate, 1M connections for uWebSockets and 500k for the others), short message throughput (10000 connections, 20-byte payload, 10 frames per send) and a 100 MB huge message echo. |
| **Metric** | memory |
| **Adoption** | 5.3k stars |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/warmcat/libwebsockets) · [benchmark](https://github.com/iCyberon/uWebSockets) |

## Verdict

The only numbers are the 2016 uWebSockets README table (iCyberon fork, uWS v0.6.3 era). The uWS author's Linux harness (g++ -std=c++11 -O3, lws 2.0 on the libev backend, WebSocket++ 0.7.0 on Asio, no CPU, compiler version or kernel given) rated each server only against uWS. Cross ratios derived from page data put libwebsockets about 5.7x lighter in memory and about 4x faster at connection setup than WebSocket++, but about 2x slower on 20-byte and 100 MB echo throughput, and behind uWS on every row.

## Use it when

- Embedded or constrained targets (ESP32/FreeRTOS, ARM Linux) that need WebSocket or HTTP client/server code in plain C with a small, configurable footprint
- Servers holding very many mostly idle WebSocket connections, where memory per connection matters more than echo throughput (the only rows where it beat WebSocket++ in the 2016 table)
- Projects that already run libuv, libevent, libev, glib or sd-event and want WebSockets on the same loop
- Products that need several protocols (ws, h2, h3/QUIC, MQTT, WebTransport) and a choice of TLS backend (OpenSSL, mbedTLS, wolfSSL, BoringSSL, GnuTLS, SChannel and others) from one library

## Skip it when

- High message-rate echo or fan-out workloads: the same 2016 table put libwebsockets about 2x behind WebSocket++ on short and huge messages, and 6x and 4x behind uWebSockets
- C++ code that wants an idiomatic Asio-style API (WebSocket++ or Boost.Beast); lws is callback-reason C code with strict write discipline
- Multithreaded apps that want to send from any thread: only lws_cancel_service() is thread-safe, so every other call has to be handed to the service thread
- Pinning an old release: the README calls pre-5.0 releases effectively deprecated, with many security fixes only on v5.0-stable and main
- Builds where you cannot follow fast-moving ABI changes (LWS_PRE headroom grew from 16 to 32 bytes on 64-bit in the development branch)

## How it is fast

Compact per-connection state (a struct lws plus your per_session_data_size block and an rx buffer sized by the protocol's rx_buffer_size) driven by one serialized poll/epoll loop, or by libuv, libevent, libev, sd-event, glib or uloop if you ask for one. Sends are flow-controlled by peer writability (lws_callback_on_writable), so the library avoids queueing data the socket cannot take. Optional SMP mode runs up to 32 service threads on one context, and the least-loaded thread accepts each new connection. No benchmark in the current repo backs any speed claim.

## Compared with alternatives

Pick it over sockudo-ws, Courierust or nexus-async-web (all Rust, and the first measured against uWebSockets) when you need C, an RTOS or embedded target, many protocols in one library or a choice of TLS backend; for raw WebSocket message throughput in a C++ or Rust server, the catalogued uWebSockets-class options are the better bet.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (both built by default via CMake) |
| **Dependencies** | a TLS library unless LWS_WITH_SSL is off (OpenSSL by default for h1/h2 on \*nix; GnuTLS for QUIC/h3; mbedTLS, wolfSSL, BoringSSL, AWS-LC, LibreSSL, BearSSL, openHiTLS or SChannel as alternatives); optional libuv, libevent, libev, glib, sd-event or uloop; optional zlib (LWS_WITH_ZLIB, needed for permessage-deflate, which is off by default via LWS_WITHOUT_EXTENSIONS=ON) |
| **Minimum toolchain** | C compiler plus CMake 3.10 or later; minimum C standard not documented |
| **Platforms** | Linux (x86 and ARM), Windows (Visual Studio and MinGW), macOS, NetBSD, ESP32/FreeRTOS and other RTOS targets |
| **Thread safety** | Single-threaded serialized event loop; only lws_cancel_service() may be called from other threads. SMP service (count_threads, up to 32 threads) needs -DLWS_MAX_SMP&gt;1 at build time and user-spawned service threads |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw: the benchmark's lws echo server (benchmarks/lws.cpp, written by the uWebSockets author) loops several lws_write() calls inside one WRITEABLE callback. lws has rejected that since v2.5 ('Illegal back-to-back write'), so the harness cannot run unchanged against any current release, and the numbers describe lws 2.0 only. It also copies every message twice (std::string append, then a fresh heap Message), copies a 100 MB payload in the huge-message test, leaves rx_buffer_size at its default and links a prebuilt /usr/lib/libwebsockets.a with unknown build flags, while uWS was compiled from source at -O3.
- Harness flaw: scalability.cpp reports memory as the total line of pmap for the listening process. That is mapped virtual size, shared libraries included, not resident memory. uWS ran at 1M connections and the others at 500k, so fixed costs were spread differently. The throughput client counts echoed bytes without parsing frames, and connection rate comes from 10 blocking client threads, so the 'equal' connection row may be limited by the client.
- Default v5 \*nix builds enable HTTP/3, which forces GnuTLS instead of OpenSSL unless you pick another QUIC-capable TLS library or turn HTTP/3 off (CMakeLists.txt). Code compiled against older headers must be rebuilt for the larger LWS_PRE, and must always spell the headroom as LWS_PRE.
- 2025 CVEs: CVE-2025-11677 (use-after-free in lws_handshake_server when a LWS_CALLBACK_HTTP_CONFIRM_UPGRADE handler is used), CVE-2025-11678 (stack overflow in async DNS label parsing), CVE-2025-11679/11680 (PNG decoder OOB read/write with LWS_WITH_UPNG) and CVE-2025-1866 (Win32 pointer arithmetic, before 4.3.4). The maintainer reports an ongoing audit that keeps finding and fixing issues.

## Known shortcomings

- Evidence is the 2016 uWebSockets competitor table (v0.6.3, in the 0-star fork iCyberon/uWebSockets): lws vs WebSocket++ only as cross-ratios of rounded integers; wins memory (about 5.7x) and connection setup (about 4x) but is about 2x slower on message throughput and loses every row to uWebSockets, the listed baseline. Harness public (-O3) but no CPU or compiler version.
- Enricher: the uWS harness benchmarks/lws.cpp calls lws_write() several times per WRITEABLE callback, which lws rejects since v2.5 ('Illegal back-to-back write'), so the numbers apply to lws 2.0 only and the harness cannot run on current releases; the echo server copies each message twice and lws was linked from a prebuilt /usr/lib/libwebsockets.a with unknown flags while uWS was built at -O3; scalability.cpp reports the pmap virtual size (not RSS), uWS ran at 1M connections while the others ran at 500k, and the throughput client counts bytes without parsing frames. 2025 CVEs (11677-11680, 1866); pre-5.0 deprecated; a default v5 \*nix build forces GnuTLS.

## Caveats and trade-offs

The numbers are a competitor's table: the uWebSockets README in iCyberon/uWebSockets, a 0-star fork snapshot of uNetworking/uWebSockets whose last commit is v0.6.3 on 2016-06-26 (upstream no longer carries the table). libwebsockets and WebSocket++ are never compared directly; every ratio is a rounded integer relative to uWS, so the derived figures (about 5.7x lighter than WebSocket++, about 4x faster connection setup, about 2x slower on short- and huge-message echo) are rough. Benchmark code is in benchmarks/ (lws.cpp, wsPP.cpp, scalability.cpp, throughput.cpp; Makefile uses -O3 and links the system /usr/lib/libwebsockets.a with the libev backend); the libwebsockets echo server was written by the uWS author with a uWS-style thin message queue, and the memory test used 500k connections for libwebsockets and WebSocket++ versus 1M for uWS. No CPU, compiler version or kernel stated; libwebsockets 2.0 (2016) and WebSocket++ 0.7.0 are old versions. benchmarks/README.md notes that with one frame per send the WebSocket++-to-uWS gap shrinks from 3x to 2x. Against the category's listed baseline uWebSockets, libwebsockets loses on every row (11x more memory, equal connection rate, 6x slower short messages, 4x slower huge messages); WebSocket++ is not a listed baseline for websocket-grpc-rpc. The current libwebsockets README makes no benchmark claims. License is MIT with some files under BSD-2/BSD-3, zlib, Apache-2.0 (mbedtls wrapper, built only with mbedtls) and OFL, and test apps and minimal examples under CC0.

Pure C client and server for http/1, http/2, http/3, websockets, webtransport and MQTT with embedded-friendly footprint; callback-driven API and its own event-loop plumbing (libuv, libevent or libev integration optional), versus websocketpp's header-only C++ with Boost or standalone Asio.

## Maintenance

Very active (v5.0, commits into October 2026, 5.3k stars), MIT with CC0 examples, and broadly deployed. The performance evidence is a decade-old competitor table on an API generation that no longer accepts the benchmark's write pattern, so treat its speed as unmeasured for current versions.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The uWebSockets README table rates libwebsockets 2.0 and WebSocket++ v0.7.0 against uWS in the same harness (11x vs 63x lighter, equal vs 4x connection rate, 6x vs 3x short messages, 4x vs 2x huge messages), so the libwebsockets-vs-WebSocket++ ratios exist only as derived cross-ratios of rounded integers. Benchmark code is public (benchmarks/lws.cpp, wsPP.cpp, scalability.cpp, throughput.cpp, Makefile with g++ -std=c++11 -O3) but no CPU, compiler version or libwebsockets build is stated, so not A; a competitor's table, not an independent suite, so C.
- **Verifier notes:** Table numbers match the page and the record already labels its cross-ratios as derived; metadata checks out (MIT, 5.3k stars, last commit 2026-10-06, active). Shortcomings to record: evidence is a 2016 competitor table with no direct libwebsockets-vs-WebSocket++ run, win only on memory and connection setup while message throughput is about 2x worse, slower than uWebSockets (a listed baseline) on every row, baseline_in_list corrected to false. Low confidence entry; keep at C.
- **Fields the verifier corrected:** `baseline_in_list`, `caveats`
- **Shortcomings recorded by:** uWebSockets 2016 table (verifier); enricher harness reading
- **Pages the verifier opened:**
  - <https://github.com/iCyberon/uWebSockets>
  - <https://github.com/iCyberon/uWebSockets/commits>
  - <https://github.com/iCyberon/uWebSockets/tree/master/benchmarks>
  - <https://raw.githubusercontent.com/iCyberon/uWebSockets/HEAD/README.md>
  - <https://raw.githubusercontent.com/iCyberon/uWebSockets/HEAD/benchmarks/README.md>
  - <https://raw.githubusercontent.com/iCyberon/uWebSockets/HEAD/benchmarks/Makefile>
  - <https://raw.githubusercontent.com/iCyberon/uWebSockets/HEAD/benchmarks/lws.cpp>
  - <https://raw.githubusercontent.com/iCyberon/uWebSockets/HEAD/benchmarks/wsPP.cpp>
  - <https://raw.githubusercontent.com/iCyberon/uWebSockets/HEAD/benchmarks/scalability.cpp>
  - <https://github.com/warmcat/libwebsockets>
  - <https://github.com/warmcat/libwebsockets/commits>
  - <https://raw.githubusercontent.com/warmcat/libwebsockets/HEAD/README.md>
  - <https://raw.githubusercontent.com/warmcat/libwebsockets/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/warmcat/libwebsockets>
  - <https://raw.githubusercontent.com/warmcat/libwebsockets/HEAD/README.md>
  - <https://raw.githubusercontent.com/warmcat/libwebsockets/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/warmcat/libwebsockets/HEAD/SECURITY.md>
  - <https://raw.githubusercontent.com/warmcat/libwebsockets/HEAD/changelog>
  - <https://raw.githubusercontent.com/warmcat/libwebsockets/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/warmcat/libwebsockets/HEAD/READMEs/README.coding.md>
  - <https://raw.githubusercontent.com/warmcat/libwebsockets/HEAD/READMEs/README.build.md>
  - <https://raw.githubusercontent.com/warmcat/libwebsockets/HEAD/include/libwebsockets/lws-protocols-plugins.h>
  - <https://github.com/warmcat/libwebsockets/issues?q=is%3Aissue+performance>
  - <https://github.com/warmcat/libwebsockets/issues/3030>
  - <https://raw.githubusercontent.com/iCyberon/uWebSockets/HEAD/README.md>
  - <https://raw.githubusercontent.com/iCyberon/uWebSockets/HEAD/benchmarks/README.md>
  - <https://raw.githubusercontent.com/iCyberon/uWebSockets/HEAD/benchmarks/Makefile>
  - <https://raw.githubusercontent.com/iCyberon/uWebSockets/HEAD/benchmarks/lws.cpp>
  - <https://raw.githubusercontent.com/iCyberon/uWebSockets/HEAD/benchmarks/wsPP.cpp>
  - <https://raw.githubusercontent.com/iCyberon/uWebSockets/HEAD/benchmarks/scalability.cpp>
  - <https://raw.githubusercontent.com/iCyberon/uWebSockets/HEAD/benchmarks/throughput.cpp>
  - https://www.sentinelone.com/vulnerability-database/cve-2025-11678/ (WebSearch snippet only)
  - https://www.cvelogic.com/cve/CVE-2025-11677 (WebSearch snippet only)
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/warmcat/libwebsockets`) · [data/wave5/enrich/raw/github_com_warmcat_libwebsockets.json](../../../data/wave5/enrich/raw/github_com_warmcat_libwebsockets.json) (enrichment confidence 0.5)

</details>
