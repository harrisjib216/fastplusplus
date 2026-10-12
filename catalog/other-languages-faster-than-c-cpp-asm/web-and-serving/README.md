# Web and serving

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md)</sub>

**What these beat:** the same task written in C or C++ at -O3, or hand-written assembly where the source compares against it  
**56 entries:** 19 tier A · 4 tier B · 21 tier C · 12 tier D · 51 copyable, 5 study only

**Languages swept:** Rust, Go, Zig, Java, .NET, Crystal (vs C/C++ servers)  
**Where they tend to win:** TechEmpower-style throughput/latency

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**Kestrel (ASP.NET Core HTTP server, HttpArena kestrel entry)**](dotnet-aspnetcore.md) | ASP.NET Core's managed HTTP server; in HttpArena it beats nginx on pipelined and cleartext HTTP/2 but loses on plain HTTP/1.1, TLS and HTTP/3. | **A** | C# | MIT | 🟢 active |
| 2 | [**actix-web**](actix-actix-web.md) | Full-featured Rust HTTP/1.1 and HTTP/2 web framework; in HttpArena it beats Drogon and Cutelyst (C++) but trails nginx and h2o. | **A** | Rust | Apache-2.0 OR MIT | 🟢 active |
| 3 | [**Quarkus (Vert.x/Netty, JDK 21)**](quarkusio-quarkus.md) | Java framework (Jakarta REST on Vert.x/Netty) that beats nginx's HTTP/2-over-TLS path on HttpArena but loses every scored HTTP/1.1 profile. | **A** | Java | Apache-2.0 | 🟢 active |
| 4 | [**Eclipse Vert.x (HttpArena vertx entry)**](eclipse-vertx-vert-x.md) | JVM event-loop HTTP toolkit on Netty; beats some C++ servers on HttpArena but trails nginx, h2o and mongoose on scored profiles. | **A** | Java | EPL-2.0 OR Apache-2.0 | 🟢 active |
| 5 | [**Helidon SE (Nima WebServer)**](helidon-io-helidon.md) | Java 27 microservice framework on the virtual-thread Níma WebServer; edges nginx on HttpArena's HTTP/2 hello-world profiles only. | **A** | Java | Apache-2.0 | 🟢 active |
| 6 | [**libxev (HttpArena baseline server)**](mitchellh-libxev.md) | Zig proactor event loop (io_uring, epoll, kqueue, WASI) with a C API; its HttpArena server ties libreactorng and beats h2o, nginx, Drogon. | **A** | Zig | MIT | 🟢 active |
| 7 | [**ntex**](ntex-rs-ntex.md) | Rust framework for HTTP/1, HTTP/2, WebSocket and TLS services; in HttpArena it edges Drogon on keep-alive requests but loses on connection churn. | **A** | Rust | Apache-2.0 OR MIT | 🟢 active |
| 8 | [**cpeak (Rust)**](cododev-technology-cpeak.md) | Express-style Rust HTTP/1.1 framework on hyper that outruns Drogon, Cutelyst and userver in HttpArena, not nginx or h2o. | **A** | Rust | MIT | 🟢 active |
| 9 | [**tokio-websockets**](gelbpunkt-tokio-websockets.md) | Strict RFC 6455 WebSocket client/server crate for Tokio; ties or edges mongoose (C) on HttpArena small-message echo. | **A** | Rust | MIT | 🟢 active |
| 10 | [**dusty**](lalinsky-dusty.md) | Zig HTTP/1.1 server and client framework on the zio coroutine runtime; ties nginx and beats Drogon in HttpArena. | **A** | Zig | MIT | 🟢 active |
| 11 | [**C# NativeAOT minima-sync (HttpArena entry)**](lang-csharp-mda2av-httparena-baseline-4096.md) | Benchmark-only NativeAOT C# io_uring HTTP/1.1 server; ties libreactorng (C) and beats nginx 1.34x on HttpArena baseline-4096. | **A** | C# | MIT | 🟢 active |
| 12 | [**Rust raw tokio HTTP/1.1 server (HttpArena tokio entry)**](lang-rust-mda2av-httparena-baseline-4096.md) | Benchmark-only hand-rolled HTTP/1.1 server on raw tokio; 1.27x nginx on HttpArena baseline-4096 but 0.96x libreactorng (C). | **A** | Rust | MIT | 🟢 active |
| 13 | [**vanilla (V HTTP server)**](enghitalo-vanilla.md) | V-language HTTP/1.1 and h2c server engine on raw io_uring/epoll; about 1.31x nginx on HttpArena baseline, level with libreactorng. | **A** | V | MIT | 🟢 active |
| 14 | [**zix**](prothegee-zix.md) | Pure-Zig network library with io_uring HTTP/1.1, HTTP/2 and HTTP/3 engines; beats nginx, h2o and Drogon in HttpArena. | **A** | Zig | BSD-3-Clause | 🟢 active |
| 15 | [**nilo**](nevindra-nilo.md) | Zig web framework on zio fibers; beats nginx on HttpArena h2/h2c, TLS-JSON and pipelined rows, loses on plain HTTP/1.1. | **A** | Zig | MIT | 🟢 active |
| 16 | [**cardigan**](phjeltman-cardigan.md) | Experimental Java 26 HTTP/1.1 and HTTP/2 server on raw io_uring; out-runs nginx's custom C module on HttpArena's plaintext profiles. | **A** | Java | MPL-2.0 | 🟢 active |
| 17 | [**tokio-uring (HttpArena minimal HTTP/1.1 server)**](tokio-rs-tokio-uring.md) | io_uring-backed Rust runtime; a hand-rolled HTTP/1.1 server on it edges nginx 1.09x in HttpArena but loses to plain epoll tokio. | **A** | Rust | MIT | 🟡 stale |
| 18 | [**fib**](lesismal-fib.md) | Go event-loop networking library serving net/http handlers; beats Sogou workflow (C++) on HTTP/1 echo, ties uSockets on TLS. | **A** | Go | no license (study only) | 🟢 active |
| 19 | [**zeemo**](skylightis666-zeemo.md) | Zig io_uring HTTP/1.1 benchmark server and young library; 1.35x nginx's HttpArena baseline rate, ties libreactorng. | **A** | Zig | no license (study only) | 🟢 active |
| 20 | [**Tako (per-thread server)**](rust-dd-tako.md) | Rust multi-transport web framework on hyper; its thread-per-core HTTP/1.1 server out-served Drogon 1.12-1.24x in the-benchmarker. | **B** | Rust | MIT | 🟢 active |
| 21 | [**jet_server**](wdestroier-jet-server.md) | Experimental pure-Dart HTTP/1.1 server driving epoll through dart:ffi; 1.36-1.46x Drogon's req/s in the-benchmarker. | **B** | Dart | MIT | 🟢 active |
| 22 | [**khttp**](karlivory-khttp.md) | Synchronous Rust HTTP/1.1 micro-framework (memchr and libc only) with an epoll dispatcher; 1.12-1.22x Drogon on the-benchmarker's trivial routes. | **B** | Rust | MIT | 🟡 stale |
| 23 | [**firenio**](firenio-firenio.md) | Java NIO/epoll network framework whose stripped 'http-lite' TechEmpower entry ties lithium and cinatra (C++) on plaintext. | **B** | Java | Apache-2.0 | 🔴 abandoned |
| 24 | [**Netty**](netty-netty.md) | Java asynchronous network framework; a 2015 Netty 3 hello-world server out-ran a 4-worker nginx echo setup and Crow. | **C** | Java | Apache-2.0 | 🟢 active |
| 25 | [**grpc-go**](grpc-grpc-go.md) | Google's pure-Go gRPC; beat a stock gRPC C++ async server at 2-4 CPUs in one grpc_bench run, lost in another. | **C** | Go | Apache-2.0 | 🟢 active |
| 26 | [**tonic (Rust gRPC)**](hyperium-tonic.md) | Rust async gRPC (tokio, hyper, prost) that out-served the stock C++ gRPC async servers in grpc_bench's small unary echo test. | **C** | Rust | MIT | 🟢 active |
| 27 | [**Armeria gRPC server (Java): grpc_bench unary echo vs C++…**](line-armeria.md) | JVM microservice framework (Netty-based) whose gRPC server out-served the stock gRPC C++ async server at 2-4 CPUs in one grpc_bench run. | **C** | Java | Apache-2.0 | 🟢 active |
| 28 | [**grpc-dotnet (gRPC for .NET)**](grpc-grpc-dotnet.md) | Managed gRPC for ASP.NET Core; outran stock gRPC C++ async servers 1.48-1.67x on grpc_bench's 2026 unary test. | **C** | C# | Apache-2.0 | 🟢 active |
| 29 | [**Undertow**](undertow-io-undertow.md) | Embeddable non-blocking Java HTTP server (Red Hat); a 2014 build topped Kore, libmicrohttpd and a 4-worker nginx in a 2015 hello-world test. | **C** | Java | Apache-2.0 | 🟢 active |
| 30 | [**linkerd2-proxy (Rust) vs Envoy as service-mesh sidecars**](linkerd-linkerd2-proxy.md) | Rust sidecar micro-proxy of the Linkerd mesh; vendor benchmarks show 6-9x less per-proxy memory than Istio's Envoy. | **C** | Rust | Apache-2.0 | 🟢 active |
| 31 | [**kawipiko**](volution-kawipiko.md) | Go static-site server that serves a prebuilt CDB archive from memory over fasthttp; author measured 1.22-1.34x NGINX request rate. | **C** | Go | AGPL-3.0-or-later | 🟢 active |
| 32 | [**ioxide**](mda2av-ioxide.md) | Shared-nothing io_uring runtime for .NET; a hand-written HTTP/1.1 handler on it outruns nginx 1.25x on HttpArena baseline-4096. | **C** | C# | MIT | 🟢 active |
| 33 | [**Apache Pekko gRPC (Scala): grpc_bench unary echo vs C++…**](apache-pekko-grpc.md) | Scala/Java gRPC on Pekko HTTP and Pekko Streams; out-served the stock C++ async gRPC greeter 1.27-1.73x in one grpc_bench run. | **C** | Scala | Apache-2.0 | 🟢 active |
| 34 | [**Vert.x gRPC server (Java): grpc_bench unary echo vs C++…**](eclipse-vertx-vertx-grpc.md) | Eclipse Vert.x's own gRPC server for the JVM; served unary grpc_bench echo 1.75x faster than the gRPC C++ async server in one 2026 run. | **C** | Java | EPL-2.0 OR Apache-2.0 | 🟢 active |
| 35 | [**Orion Proxy**](kmesh-net-orion.md) | Rust L4/L7 proxy configured through Envoy's xDS and bootstrap protobufs; first-party wrk charts show 2.3-6x Envoy's HTTP req/s. | **C** | Rust | Apache-2.0 | 🟢 active |
| 36 | [**swerver**](justingrosvenor-swerver.md) | Zig HTTP/1.1, HTTP/2 and HTTP/3 server and gateway on io_uring; edges an -O3 nginx on HttpArena plaintext and TLS, loses badly on HTTP/3. | **C** | Zig | MIT | 🟢 active |
| 37 | [**PowPow**](openpeeps-powpow.md) | Nim event-loop library with a built-in HTTP/1.1 server that out-served Drogon by 1.34-1.39x in one the-benchmarker snapshot. | **C** | Nim | MIT | 🟢 active |
| 38 | [**Arc (Arc Gateway)**](shuakami-arc.md) | Young Rust io_uring reverse proxy claiming 2.05-2.30x nginx's HTTP/1.1 proxy throughput on a 2-vCPU WSL2 box. | **C** | Rust | Apache-2.0 | 🟢 active |
| 39 | [**Thruster (Rust, thruster-grpc)**](thruster-rs-thruster.md) | Koa-style Rust web framework whose experimental thruster-grpc server, on hyper/h2, out-served gRPC C++ in grpc_bench unary echo. | **C** | Rust | MIT | 🟡 stale |
| 40 | [**wizzardo-http**](wizzardo-http.md) | Small Java HTTP server and web framework on a JNI epoll core; ties C++ cinatra and lithium in TechEmpower plaintext. | **C** | Java | MIT | 🟡 stale |
| 41 | [**faf**](errantmind-faf.md) | Minimal Linux epoll HTTP/1.1 server in unsafe Rust that tied lithium and cinatra (C++) on TechEmpower Round 22 plaintext. | **C** | Rust | AGPL-3.0 | 🟡 stale |
| 42 | [**D (LDC, betterC) port of the C epoll raw HTTP responder…**](lang-d-tchaloupka-httpbench-raw-epoll-http-responder.md) | Single-file betterC D port of a C epoll 'Hello, World!' HTTP responder; matches the gcc -O3 original within 10%. | **C** | D | Unlicense | 🔴 abandoned |
| 43 | [**routez**](endel-routez.md) | nginx-style edge server in pure Zig (HTTP/1.1, TLS 1.3, HTTP/3, proxy); beats nginx on fixed, proxied and TLS keep-alive rows. | **C** | Zig | no license (study only) | 🟢 active |
| 44 | [**rproxy**](pipelinedude-rproxy.md) | Rust io_uring HTTP/1.1 filtering reverse proxy; first-party 1.24x nginx-as-proxy throughput on a 2-byte keep-alive response. | **C** | Rust | no license (study only) | 🟢 active |
| 45 | [**Caddy**](caddyserver-caddy.md) | Go web server and reverse proxy with automatic HTTPS; claimed to beat nginx, but measured 4-14x slower in HttpArena. | **D** | Go | Apache-2.0 | 🟢 active |
| 46 | [**Traefik (Go reverse proxy; TLS latency vs Nginx and HAProxy)**](traefik-traefik.md) | Go reverse proxy and load balancer; one small third-party Docker test shows lower TLS (HTTP/2) tail latency than nginx at 5k req/s. | **D** | Go | MIT | 🟢 active |
| 47 | [**Ferron**](ferronweb-ferron.md) | Rust web server and reverse proxy with automatic TLS and built-in tracing; markets nginx-class speed but publishes no numbers. | **D** | Rust | MIT | 🟢 active |
| 48 | [**Spire**](lsk569937453-spire.md) | Rust (Tokio/Hyper) reverse proxy and gateway; HAProxy and Envoy wins come from an unequal harness; nginx beats it. | **D** | Rust | Apache-2.0 | 🟢 active |
| 49 | [**during (D io_uring wrapper)**](tchaloupka-during.md) | Low-level D binding to Linux io_uring (no liburing); author's echo and HTTP microbenchmarks edge C liburing servers. | **D** | D | BSL-1.0 | 🟢 active |
| 50 | [**statico**](awgn-statico.md) | Rust benchmarking stub that returns one fixed HTTP response; its README table puts it ahead of nginx 'return 200'. | **D** | Rust | MIT OR Apache-2.0 | 🟢 active |
| 51 | [**cblt**](evgenyigumnov-cblt.md) | Small Rust (tokio) static file server and reverse proxy whose '10x faster than nginx' small-file claim does not survive a harness check. | **D** | Rust | MIT | 🟡 stale |
| 52 | [**bladebench Rust raw TCP server**](lang-rust-synaptechlabs-bladebench-tcp-static-http-response.md) | Toy Rust std::net TCP server measured 1.21x faster than identical C++ and 1.5x than C; invalid comparison. | **D** | Rust | MIT | 🟡 stale |
| 53 | [**bladebench Zig raw TCP server**](lang-zig-synaptechlabs-bladebench-tcp-static-http-response.md) | 47-line Zig blocking TCP responder whose 2x wrk lead over C/C++ comes from skipping the request read, not codegen. | **D** | Zig | MIT | 🟡 stale |
| 54 | [**wut-server**](nixigaj-wut-server.md) | Single-purpose Rust HTTPS server that returns the caller's IP; one first-party wrk run beat a one-worker nginx 1.49x. | **D** | Rust | MIT | 🟡 stale |
| 55 | [**monolake**](cloudwego-monolake.md) | Rust io_uring thread-per-core proxy framework (ByteDance, archived) edging nginx on small-body HTTPS proxying; slower on plain HTTP. | **D** | Rust | MIT OR Apache-2.0 | 🔴 abandoned |
| 56 | [**Go net/http vs nginx on localhost (yosssi gist)**](lang-go-yosssi-4d719cccdf185259ea1d-http-vs-nginx.md) | 2014 loopback wrk transcript: a Go net/http empty handler beats nginx 1.96x, but no row shows Go serving the same file faster. | **D** | Go | no license (study only) | 🔴 abandoned |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
