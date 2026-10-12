# HTTP servers and frameworks

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md)</sub>

**What these beat:** nginx, Go net/http, Boost.Beast, actix-web, uvloop  
**53 entries:** 6 tier A · 22 tier B · 22 tier C · 3 tier D · 51 copyable, 2 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**Granian**](emmett-framework-granian.md) | Rust (hyper + tokio) HTTP server for Python ASGI/WSGI/RSGI apps, with higher single-worker throughput than Uvicorn and Gunicorn. | **A** | Rust | BSD-3-Clause | 🟢 active |
| 2 | [**Lithium (HTTP server / web framework)**](matt-42-lithium.md) | Header-only C++ HTTP server and async SQL toolkit on fibers; beat actix-web on TechEmpower DB tests only in Round 20. | **A** | C++ | MIT | 🟢 active |
| 3 | [**Ultimate Express**](dimdengd-ultimate-express.md) | Express 4 API re-implemented on uWebSockets.js; README shows 3-12x Express req/s, but Node 24 narrows most gaps. | **A** | JavaScript | Apache-2.0 | 🟢 active |
| 4 | [**Cutelyst**](cutelyst-cutelyst.md) | Qt 6 web framework with its own epoll HTTP/1.1, HTTP/2 and FastCGI server; edges Drogon on HttpArena, trails nginx and actix-web. | **A** | C++ | BSD-3-Clause | 🟢 active |
| 5 | [**agensio**](yiannisbourkelis-agensio.md) | Pre-alpha C++ static-file, FastCGI and reverse-proxy web server on Asio; outpaces nginx on most HttpArena infrastructure rows. | **A** | C++ | MIT | 🟢 active |
| 6 | [**CPV Framework**](cpv-project-cpv-framework.md) | C++17 HTTP/1.1 web framework on Seastar's thread-per-core reactor; 5-14% more plaintext req/s than actix-web 2.0 at 100 connections. | **A** | C++ | MIT | 🔴 abandoned |
| 7 | [**Elysia (Bun)**](elysiajs-elysia.md) | Bun-first TypeScript web framework; ties actix-web on a hello-world GET because Bun serves that route natively. | **B** | TypeScript | MIT | 🟢 active |
| 8 | [**hyper**](hyperium-hyper.md) | Rust's low-level HTTP/1 and HTTP/2 library under axum and warp; raw hyper roughly ties actix-web on minimal GET /. | **B** | Rust | MIT | 🟢 active |
| 9 | [**Drogon**](drogonframework-drogon.md) | Async C++17/20 HTTP/1.1 web framework on an epoll reactor; \~1.8-2x Go net/http req/s on hello-world. | **B** | C++ | MIT | 🟢 active |
| 10 | [**uWebSockets.js**](unetworking-uwebsockets-js.md) | Node.js addon running the uWebSockets C++ server behind JS callbacks; 2.6x Fastify, about 1.06x actix-web on hello-world. | **B** | JavaScript | Apache-2.0 | 🟢 active |
| 11 | [**Oat++**](oatpp-oatpp.md) | Zero-dependency C++ web framework (REST, DTO/JSON, Swagger, WebSocket) whose default server beat Go net/http \~1.5x on hello-world. | **B** | C++ | Apache-2.0 | 🟢 active |
| 12 | [**Lwan**](lpereira-lwan.md) | C HTTP/1.1 server and embeddable library; topped TechEmpower Round 10 JSON at \~5.8x Go net/http's throughput. | **B** | C | GPL-2.0 | 🟢 active |
| 13 | [**Pistache**](pistacheio-pistache.md) | C++17 HTTP/1.1 REST server library; in a 2020 shootout it beat C++ REST SDK by 3.2x and Restbed by 1.26x on small POSTs. | **B** | C++ | Apache-2.0 | 🟢 active |
| 14 | [**Jooby (Java)**](jooby-project-jooby.md) | Java/Kotlin web framework on Netty (or Jetty/Undertow/Vert.x); ties actix-web on the-benchmarker's empty GET / test. | **B** | Java | Apache-2.0 | 🟢 active |
| 15 | [**http.zig (httpz)**](karlseguin-http-zig.md) | Zig HTTP/1.1 server library on epoll/kqueue; ties actix-web on hello-world req/s, leading \~5% only at 512 connections. | **B** | Zig | MIT | 🟢 active |
| 16 | [**RESTinio**](stiffstream-restinio.md) | Header-only C++17 embedded async HTTP/WebSocket server on ASIO; served a 10-client POST echo test 1.3-2.1x faster than Restbed. | **B** | C++ | BSD-3-Clause | 🟢 active |
| 17 | [**ActiveJ**](activej-activej.md) | Java NIO event-loop platform whose HTTP server beat actix-web by \~9% on the-benchmarker's empty GET test. | **B** | Java | Apache-2.0 | 🟢 active |
| 18 | [**may_minihttp**](xudong-huang-may-minihttp.md) | Bare-bones Rust HTTP/1.1 server on the may stackful-coroutine runtime; 1.19x actix-web on the-benchmarker's empty-body GET. | **B** | Rust | Apache-2.0 | 🟢 active |
| 19 | [**ohkami (nio backend)**](ohkami-rs-ohkami.md) | Rust HTTP/1.1 web framework whose nio thread-per-core build out-served actix-web by \~11% on an empty-route benchmark. | **B** | Rust | MIT | 🟢 active |
| 20 | [**Breeze**](nelthaarion-breeze.md) | Go web framework on the gnet event loop; about 2.5x Go net/http on hello-world HTTP/1.1 throughput. | **B** | Go | MIT | 🟢 active |
| 21 | [**caprese**](zenywallet-caprese.md) | Nim HTTP/1.1 and WebSocket server with built-in TLS; about 30% more req/s than actix-web on an empty GET /. | **B** | Nim | MIT | 🟢 active |
| 22 | [**micro-http (foldright)**](foldright-micro-http.md) | Tiny tokio HTTP/1.1 server and web framework; matches actix-web on hello-world throughput, ahead \~2% only at 512 connections. | **B** | Rust | Apache-2.0 | 🟢 active |
| 23 | [**fulmine.js**](nigrosimone-fulmine-js.md) | Drop-in Express 5 replacement on uWebSockets.js; hello-world suite run: \~5x Express, 1.25x actix-web req/s. | **B** | JavaScript | Apache-2.0 | 🟢 active |
| 24 | [**CWIST**](c4punks-cwist.md) | Plain-C17 web framework and app server; about 2.1-2.3x Go net/http's plaintext req/s in one independent suite run. | **B** | C | MIT | 🟢 active |
| 25 | [**MoroJS engine (@morojs/engine)**](moro-js-engine.md) | C++ HTTP/1.1 and WebSocket server addon for Node.js, the engine under MoroJS; beat actix-web 1.11-1.14x on a hello-world shootout. | **B** | C++ | MIT | 🟢 active |
| 26 | [**httpbeast**](dom96-httpbeast.md) | Minimal multi-threaded epoll/kqueue HTTP/1.1 server core for Nim; about 7% above actix-web at 256-512 connections on hello-world. | **B** | Nim | MIT | 🟡 stale |
| 27 | [**Agoo-C**](ohler55-agoo-c.md) | Small C HTTP/1.1 and GraphQL server library built on Ruby Agoo's C core; \~2.1x Go net/http at 256+ connections. | **B** | C | MIT | 🔴 abandoned |
| 28 | [**Bun (Bun.serve)**](oven-sh-bun.md) | Bun's built-in JavaScript HTTP server (Bun.serve); 2.0-2.2x Go net/http throughput on a 3-route hello-world API, 4 cores. | **B** | Rust/C++/C | MIT for Bun's own code, per… (study only) | 🟢 active |
| 29 | [**Pingora**](cloudflare-pingora.md) | Rust async framework for building HTTP proxies; replaced Cloudflare's NGINX-based edge proxy with less CPU, memory and TTFB. | **C** | Rust | Apache-2.0 | 🟢 active |
| 30 | [**fasthttp (Go HTTP server/client package)**](valyala-fasthttp.md) | Zero-allocation HTTP/1.1 server and client for Go; about 5x faster per request than net/http in its own benchmarks. | **C** | Go | MIT | 🟢 active |
| 31 | [**cpp-httplib**](yhirose-cpp-httplib.md) | Single-header C++11 HTTP/1.1 client and server; easiest to embed, but not shown faster than C++ REST SDK. | **C** | C++ | MIT | 🟢 active |
| 32 | [**Sogou C++ Workflow (HTTP Server)**](sogou-workflow.md) | Sogou's C++11 async task engine; its embedded HTTP server hit \~2.2-2.6x nginx's QPS on small bodies (first-party test). | **C** | C++ | Apache-2.0 | 🟢 active |
| 33 | [**Mongoose**](cesanta-mongoose.md) | Two-file C networking library with its own bare-metal TCP/IP stack; vendor reports about 3.8x lwIP raw's HTTP requests/s on an STM32F746. | **C** | C | GPL-2.0-only | 🟢 active |
| 34 | [**H2O**](h2o-h2o.md) | C HTTP/1, HTTP/2 and HTTP/3 web server and reverse proxy; 2016 charts show more req/s per core than nginx 1.9. | **C** | C | MIT | 🟢 active |
| 35 | [**Crow**](crowcpp-crow.md) | Header-only C++17 Flask-style HTTP/WebSocket framework on Asio; a 2014 first-party /json run beat Go net/http by \~1.5x. | **C** | C++ | BSD-3-Clause | 🟢 active |
| 36 | [**Kore**](jorisvink-kore.md) | Sandboxed C (or Python/Lua) web application server; outran an OpenResty nginx echo setup 1.5x in a 2015 unequal hello-world test. | **C** | C | ISC | 🟢 active |
| 37 | [**cinatra**](qicosmos-cinatra.md) | Header-only C++20 coroutine HTTP/1.1 server and client library. On the project's own plaintext test it beats nginx by about 3%. | **C** | C++ | MIT | 🟢 active |
| 38 | [**icey (HTTP server module)**](nilstate-icey.md) | Single-threaded libuv + llhttp HTTP/1.1 server inside a C++20 media toolkit; 34% more keep-alive req/s than Go net/http on one vCPU. | **C** | C++ | LGPL-2.1-or-later | 🟢 active |
| 39 | [**Pipy**](flomesh-io-pipy.md) | C++ programmable proxy scripted in PipyJS; the vendor's single-core hello-world test shows 1.4-2.6x nginx keep-alive throughput. | **C** | C++ | MIT | 🟢 active |
| 40 | [**CppCMS**](artyom-beilis-cppcms.md) | C++11 web framework (FastCGI/SCGI/HTTP) with trigger-invalidated page cache; 2008 first-party case study shows \~41x uncached WordPress throughput. | **C** | C++ | MIT | 🟢 active |
| 41 | [**Qbix Server (PHP webserver)**](qbix-webserver.md) | Pure-PHP HTTP/WebSocket server that forks copy-on-write workers after preloading the app, aimed at php-fpm's worker-count limit on I/O-bound PHP. | **C** | PHP | MIT | 🟢 active |
| 42 | [**TrueAsync Server (PHP extension with a C core, HttpArena…**](true-async-server.md) | C HTTP/1.1, HTTP/2 and HTTP/3 server inside PHP (TrueAsync fork) that out-runs HttpArena's nginx on small-response HTTP/2. | **C** | C | Apache-2.0 | 🟢 active |
| 43 | [**aeronet**](sjanel-aeronet.md) | C++23 HTTP/1.1, HTTP/2 and WebSocket server library; out-serves Go net/http and mostly Boost.Beast in first-party single-thread tests. | **C** | C++ | MIT | 🟢 active |
| 44 | [**cofetch**](ssarcandy-cofetch.md) | Header-only async HTTP client on libcurl's multi interface and ASIO; out-runs one-request-at-a-time cpr and cpp-httplib clients by multiplexing. | **C** | C++ | MIT | 🟢 active |
| 45 | [**Mach**](machframework-mach.md) | C++20 web framework with ASP.NET Core-style minimal APIs on Boost.Beast; mixed against an unnamed C# server, slower than Drogon. | **C** | C++ | MIT | 🟢 active |
| 46 | [**epoll-httpd**](sapnilpatel-epoll-httpd.md) | Small Linux-only C++17 static-file HTTP/1.1 server on raw epoll; \~1.4-1.6x single-worker nginx on 1-8 KB files. | **C** | C++ | MIT | 🟢 active |
| 47 | [**Muduo**](chenshuo-muduo.md) | Linux one-loop-per-thread C++ TCP reactor library; author's ping-pong test puts it about 18% above libevent2's bufferevents. | **C** | C++ | BSD-3-Clause | 🟡 stale |
| 48 | [**libuhttpd**](zhaojh329-libuhttpd.md) | Small embeddable C HTTP/1.1 server library on libev for embedded Linux; one first-party wrk run shows 1.74x nginx req/s. | **C** | C | MIT | 🟡 stale |
| 49 | [**libevhtp**](yellow-camper-libevhtp.md) | Archived C HTTP/1.1 server library on libevent; about 1.15x Boost.Beast's async example on one plaintext wrk test. | **C** | C | BSD-3-Clause | 🔴 abandoned |
| 50 | [**uhttp (io_uring-http-benchmark)**](squigglekernel-io-uring-http-benchmark.md) | Single-route io_uring static HTTP server in C++20; 40-54% more req/s than tuned nginx serving one 10 KB file on loopback. | **C** | C++ | no license (study only) | 🟢 active |
| 51 | [**nghttp2 (nghttpx HTTP/2 proxy)**](nghttp2-nghttp2.md) | C HTTP/2 framing library (curl's HTTP/2 backend) plus nghttpx, an HTTP/3/2/1.1 TLS-terminating reverse proxy; weak evidence against ATS. | **D** | C | MIT | 🟢 active |
| 52 | [**httpserver.h**](jeremycw-httpserver-h.md) | Single-header C library for embedding a non-blocking HTTP/1.1 server; the author's 2019 ab hello-world run beat a one-worker nginx 1.14 by about 1.7x. | **D** | C | MIT | 🟢 active |
| 53 | [**Ichor**](volt-software-ichor.md) | C++20/23 dependency-injection and event-queue framework with HTTP services on Boost.Beast; its 'faster than Beast' numbers come from a broken baseline. | **D** | C++ | MIT | 🟢 active |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
