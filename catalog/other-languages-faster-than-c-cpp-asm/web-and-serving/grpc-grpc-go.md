# grpc-go

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Web and serving](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `Apache-2.0` · 🟢 active

> Google's pure-Go gRPC; beat a stock gRPC C++ async server at 2-4 CPUs in one grpc_bench run, lost in another.

| | |
|---|---|
| **Beats** | gRPC C++ (grpc/grpc) servers cpp_grpc_st, cpp_grpc_mt and cpp_asio_grpc in the grpc_bench suite |
| **Claimed result** | Results flip between runs; all ratios derived from page data. Newest maintainer run (discussion #559, 2026-04-22, commit c4c93b3, Go 1.26.2, grpc-go v1.79.3): go_grpc is behind at 1 CPU, 55,667 req/s vs cpp_grpc_mt 57,403, cpp_grpc_st 57,140 and cpp_asio_grpc 56,669 (0.97x, 0.97x, 0.98x). It is ahead at 2 CPUs, 88,531 vs cpp_asio_grpc 74,869 and cpp_grpc_mt 74,574 (1.18x, 1.19x); at 3 CPUs, 109,481 vs 81,581 (1.34x); and at 4 CPUs, 117,082 vs 85,485 (1.37x). 2022-04-23 wiki run (commit 14a8435, Go 1.17, grpc-go v1.36.0): ahead only at 1 CPU, 34,289 vs cpp_grpc_st 26,700, cpp_grpc_mt 26,376 and cpp_asio_grpc 24,926 (1.28x, 1.30x, 1.38x). Behind at 2 CPUs, 50,939 vs cpp_grpc_mt 69,882 (0.73x), and at 3 CPUs, 61,002 vs 71,806 (0.85x). Third-party run (discussion #547, 2025-12-09, Ryzen 9 5900X, client CPUs equal to server CPUs, 10 s): a tie with cpp_grpc_mt, 0.96x at 1 CPU, 1.02x at 4 and 1.00x at 24. go_vtgrpc, which uses the vtprotobuf codec already listed in wave 2, is faster than go_grpc in both main runs. |
| **Workload** | grpc_bench complex_proto unary SayHello over loopback: 50 client connections, 1000 concurrent requests, unlimited QPS, 120 s with 30 s warmup, ghz client. One run per server-CPU setting: 1 to 4 server CPUs in the 2026-04-22 run (commit c4c93b3, discussion #559) and 1 to 3 in the 2022-04-23 run (commit 14a8435, wiki). |
| **Metric** | throughput |
| **Hardware** | Newest run (discussion #559, posted by maintainer LesnyRumcajs 2026-04-22, commit c4c93b3): Intel Xeon Gold 6548N (16) @ 2.80 GHz, 64 GB RAM, Ubuntu 24.04.3, kernel 6.8.0-71, DigitalOcean dedicated server. Server limited to 1, 2, 3 or 4 CPUs and 4096m RAM; client 11 CPUs. 2022-04-23 wiki run (commit 14a8435): Intel Xeon E5-1650 v3 @ 3.50GHz, 32 GB RAM. Server limited to 1, 2 or 3 CPUs and 512m RAM; client 9 CPUs. |
| **Compiler and flags** | go_grpc in the 2026-04 run (c4c93b3): golang:1.26.2-bookworm, go build ./... with default gc settings; go.mod has grpc v1.79.3, protobuf v1.36.10 and go.uber.org/automaxprocs v1.5.3; protoc-gen-go v1.33.0 and protoc-gen-go-grpc v1.3.0. In the 2022 run (14a8435): golang:1.17, grpc v1.36.0, protobuf v1.27.1, automaxprocs v1.4.0. C++ baselines: cpp_grpc_mt and cpp_grpc_st are built with g++ --std=c++20 -O3 -flto over main.cpp and the generated stubs, linking jemalloc and Debian's prebuilt libgrpc++-dev from the base image (gcc:15.2.0 at c4c93b3, gcc:11 at 14a8435, gcc:16.1.0 at HEAD). The gRPC core's version and build flags are the distro package's and are not stated or pinned. cpp_asio_grpc uses asio-grpc v1.0.0, CMake Release with jemalloc, against the same distro libgrpc++. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | not stated |
| **Adoption** | 23.1k stars |
| **Last commit** | 2026-10-10 |
| **Links** | [repository](https://github.com/grpc/grpc-go) · [benchmark](https://github.com/LesnyRumcajs/grpc_bench/discussions/559) |

## Verdict

grpc_bench discussion #559 (maintainer run, 2026-04-22, commit c4c93b3, Xeon Gold 6548N, Ubuntu 24.04, ghz client on 11 CPUs, 50 connections, 1,000 concurrent requests, 120 s after 30 s warmup, one run per setting): go_grpc (grpc-go v1.79.3 built with Go 1.26.2, default options) served 55,667 / 88,531 / 109,481 / 117,082 req/s at 1-4 server CPUs against the best C++ server (cpp_grpc_mt or cpp_asio_grpc, app code built with g++ 15.2 -O3 -flto over Debian's prebuilt libgrpc++) at 57,403 / 74,869 / 81,581 / 85,485, i.e. 0.97x, 1.18x, 1.34x and 1.37x (derived from page data). The 2022 wiki run (Xeon E5-1650 v3, grpc-go v1.36.0, Go 1.17) reversed this: 1.28x at 1 CPU, 0.73x and 0.85x at 2-3 CPUs.

## Use it when

- Any Go service that needs gRPC: it is the reference Go implementation and is wire-compatible with C++, Java, Rust and .NET peers.
- Small unary RPCs on 2-4 core containers, where the 2026 grpc_bench run put it at 88,531-117,082 req/s against 74,869-85,485 for the stock gRPC C++ async servers (1.18-1.37x).
- Memory-constrained deployments: 21-31 MiB average memory in grpc_bench #559, similar to the C++ servers (9-32 MiB) and far below grpc-dotnet (122-135 MiB) or Java Vert.x (108-333 MiB).
- Services that need xDS, ALTS, interceptors or OpenTelemetry stats in the same library (all live in this module and its go.mod).

## Skip it when

- If you need a stable speed advantage over C++ gRPC: the 2022 run of the same harness reversed the order (1.28x at 1 CPU, 0.73x and 0.85x at 2-3 CPUs), a 2025 third-party run (#547) is a tie, and a tuned C++ server (many pre-posted requests per completion queue, callback API, a current gRPC core) was never measured.
- Single-core servers with tight tail latency: at 1 CPU it serves 0.97x of cpp_grpc_mt with a p99 of 37.04 ms versus 21.81 ms.
- If you want the fastest gRPC server outright: in the same 2026 run rust_tonic_st (102,754 req/s at 1 CPU, 1.85x), grpc-dotnet, rust_thruster and java_vertx_grpc (130,000-153,000 req/s at 2-4 CPUs) all beat go_grpc at every CPU count.
- GC-sensitive hot paths: the server path still allocates per RPC (performance issue #3305, 'reduce garbage allocations in server path', open since 2020) and the default server starts one goroutine per stream.
- C or C++ codebases: there is no C/C++ API; the only route is a separate Go process.

## How it is fast

Each connection has a reader goroutine and a 'loopy writer' goroutine that drains a control buffer, interleaves DATA frames from active streams within flow-control quota, and batches frames into a 32 KB write buffer that it flushes only when nothing is queued; if fewer than 1,000 bytes are pending it yields once (runtime.Gosched) so stream goroutines can add to the batch (internal/transport/controlbuf.go). Every RPC runs in its own goroutine on Go's netpoller-backed M:N scheduler, so all GOMAXPROCS threads share incoming calls instead of being bound to one completion queue each as in the C++ async example used as the baseline. A BDP estimator sizes flow-control windows dynamically, and buffers come from a mem.BufferPool. The measured lead is a scaling effect, not per-core speed: at 1 server CPU it is 0.97x of C++.

## Compared with alternatives

Pick grpc-go when the service is written in Go; tonic and Thruster (Rust) and grpc-dotnet out-served it at every CPU count of the same 2026 run (rust_tonic_st 102,754 vs 55,667 req/s at 1 CPU; grpc-dotnet 123,609-136,452 vs 88,531-117,082 at 2-4 CPUs). Against grpc-dotnet it uses a quarter to a sixth of the memory (21-31 MiB vs 122-135 MiB).

## Integration

| | |
|---|---|
| **Form** | module (Go module google.golang.org/grpc; code generation with protoc-gen-go and protoc-gen-go-grpc) |
| **Dependencies** | golang.org/x/net (HTTP/2 framer, HPACK), google.golang.org/protobuf, genproto rpc status; go.mod also pulls Envoy go-control-plane, cncf/xds, OpenTelemetry and go-spiffe for the xDS and stats packages |
| **Minimum toolchain** | Go 1.26 at HEAD (go.mod 'go 1.26.0'; the benchmarked v1.79.3 needed Go 1.24); the README supports only the two latest Go major releases |
| **Platforms** | any Go target; the README installs it with a plain import and go build, no C toolchain step |
| **Thread safety** | ClientConn and generated clients are safe to share across goroutines; on one stream only one goroutine may call SendMsg and one RecvMsg at a time; each server handler runs in its own goroutine (Documentation/concurrency.md) |
| **Drop-in for the baseline** | partial: wire-compatible with gRPC C++ (same .proto, same HTTP/2 protocol), so it can replace a C++ server or client process, but it is not a C++ library and shares no API or ABI |

## Gotchas

- Baseline asymmetry in the measured win: the C++ servers link Debian's prebuilt libgrpc++-dev (unpinned; Debian stable ships the 1.51.1 series per Debian package listings seen in a search snippet, so most likely a late-2022 gRPC core) while go_grpc used grpc-go v1.79.3 from 2026. cpp_grpc_mt is the helloworld async pattern with one completion-queue thread per GRPC_SERVER_CPUS and a single pre-posted RequestSayHello per queue, so under 1,000 concurrent requests each queue accepts new calls one at a time. Its efficiency collapses with cores, from 57,403 req/s at 103% CPU to 85,485 at 406% (about 55,600 to 21,100 req/s per CPU, derived from page data), while go_grpc goes from 55,667 at 101% to 117,082 at 333% (about 55,200 to 35,100). The 2-4 CPU win therefore measures a poorly scaling C++ server, not faster per-core code.
- bench.sh limits the server with docker --cpus, a CFS quota rather than a cpuset: go_grpc imports go.uber.org/automaxprocs, so GOMAXPROCS matches the quota, while the C++ process still sees all 16 host cores. Only one run per setting, the client reaches the server through Docker's published port 50051, and the workload is a single unary complex_proto echo.
- The benchmarked v1.79.3 predates three 2026 advisories: GHSA-hrxh-6v49-42gf (HTTP/2 Rapid Reset mitigation bypass, fixed in 1.82.1), GHSA-vp52-pcj8-j9qc / CVE-2026-84304 (heap exhaustion from millions of tiny DATA frames, fixed in 1.83.1 with receive-buffer compaction) and GHSA-2v4p-qf9q-27wj (xDS server crash on missing :authority and Host, fixed in 1.82.2 and 1.83.2). The fixes add per-frame accounting, and HEAD also turns on the shared write buffer by default (off in v1.79.3); nobody has re-measured throughput on these versions.
- Defaults matter: the harness uses grpc.NewServer() with no options, so NumStreamWorkers (experimental, reuses goroutines instead of one per stream), WriteBufferSize/ReadBufferSize and window sizes were not tuned on the Go side either. The faster go_vtgrpc rows (4-8% above go_grpc) come from the vtprotobuf codec, listed separately in wave 2.

## Known shortcomings

- Result flips between grpc_bench runs: 2022 wins at 1 CPU only; 2026 (discussion 559) loses at 1 CPU (0.97x) and wins at 2-4 CPUs (1.18-1.37x). Shared C++ baseline flaw: unpinned distro libgrpc++, helloworld async pattern, poor scaling (85,485 req/s at 4 CPUs).
- Harness flaw: the C++ baseline is the untuned helloworld async server (one completion-queue thread per CPU, one pre-posted request per queue) on unpinned Debian libgrpc++, most likely the 1.51.1 series (version from a search snippet; packages.debian.org blocked); its per-CPU throughput falls from 55,600 to 21,100 req/s between 1 and 4 CPUs (Go 55,200 to 35,100), so the 2-4 CPU win measures C++ scaling. docker --cpus is a quota, not a cpuset: Go matches it via automaxprocs while C++ sees 16 cores. The benchmarked v1.79.3 predates the 2026 advisories GHSA-hrxh-6v49-42gf, GHSA-vp52-pcj8-j9qc (CVE-2026-84304) and GHSA-2v4p-qf9q-27wj and was never re-measured; tonic, Thruster and grpc-dotnet beat go_grpc at every CPU count in #559.

## Caveats and trade-offs

The result is not robust and flips between runs.
- In 2022 grpc-go led only at 1 CPU and trailed multi-threaded C++ gRPC at 2-3 CPUs (0.73x, 0.85x).
- In the newest maintainer run it trails all C++ servers at 1 CPU (0.97x) and leads at 2-4 CPUs (1.18-1.37x).
- In a client-bound third-party run (#547) it ties.
- Its 1-CPU p99 in 2026 is 37.04 ms vs 21.81 ms for cpp_grpc_mt.
- The C++ servers link Debian's prebuilt libgrpc++, which is unpinned and of unstated version and flags, so the -O3 -flto applies only to the server code and stubs. They follow the helloworld async-example pattern: one completion queue and thread per server CPU, with one pre-posted request per queue (cpp_grpc_mt_bench/main.cpp). They scale poorly: cpp_grpc_mt does 57,403 req/s at 1 CPU and 85,485 at 4 CPUs while using 405% CPU. So the baseline is a stock but untuned gRPC C++ server.
- The faster go_vtgrpc rows belong to vtprotobuf (wave 2), not to grpc-go itself.
- The workload is a unary complex_proto SayHello only, over loopback on one host, with a single run per setting.
- The grpc-go README links an external performance dashboard but states no figures. [retier] Enricher (Pekko gRPC pass): grpc_bench's cpp_grpc_mt pre-posts one call per completion queue (gRPC's own server_async.cc pre-posts 5000) and allocates per RPC; it links unpinned Debian libgrpc++ (likely 1.51.1). Every grpc_bench row compared against cpp_grpc_mt inherits this crippled baseline.

Go garbage collector and runtime; goroutine-per-stream model.

## Maintenance

Actively maintained by the gRPC team (latest release v1.84.0 dated 17 Sep on the releases page, 23.1k stars, 120 open issues, Apache-2.0) and the standard choice for Go; the speed edge over C++ gRPC is run-dependent and rests on an untuned, probably 1.51-era C++ baseline, and production users should run 1.84.0 or later because the benchmarked v1.79.3 is affected by 2026 DoS advisories.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification B, tier now C.
- **Tier reason:** LesnyRumcajs/grpc_bench is a well-known independent third-party gRPC shootout. Its 2022-04-23 wiki page and its newest maintainer-posted run (discussion #559, 2026-04-22) both state the CPU, commit and settings, and the harness is public (go_grpc_bench/{Dockerfile,go.mod}, cpp_grpc_mt_bench/{Dockerfile,main.cpp}, cpp_asio_grpc_bench). It falls short of A because the C++ baseline links Debian's prebuilt libgrpc++-dev of unstated, unpinned version and flags (wave 5 grpc/grpc precedent).
- **Retiered** B to C: Downgraded from B to C (crippled-baseline precedent): grpc_bench's C++ entry cpp_grpc_mt pre-posts one RequestSayHello per completion queue and does new/delete per RPC, while gRPC's own async QPS server pre-posts 5000 per queue, and it links unpinned Debian libgrpc++ (likely gRPC 1.51.1) with version and flags unrecorded, so wins over it measure a weak C++ server setup rather than the C++ gRPC stack at its best.
- **Verifier notes:** The 2022 numbers match the wiki page exactly. The record's 'loses clearly from two CPUs up' no longer holds: the newest run of the same harness (discussion #559, 2026-04) reverses the ordering, so the Go win is run-dependent. benchmark_url moved to #559 and the claim now lists both runs. Shortcomings to record: inconsistent across runs (1-CPU win in 2022 only, 2-4 CPU win in 2026 only); the C++ baseline is an untuned helloworld-pattern server on an unpinned distro libgrpc++; worse 1-CPU p99 than C++. Metadata confirmed: Apache-2.0, 23.1k stars, last commit 2026-10-10, not a fork or archived.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-42 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/LesnyRumcajs/grpc_bench/discussions/559>
  - <https://github.com/LesnyRumcajs/grpc_bench/wiki/2022-04-23-bench-results>
  - <https://github.com/LesnyRumcajs/grpc_bench/discussions/547>
  - <https://github.com/LesnyRumcajs/grpc_bench/discussions/categories/benchmark-results>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/cpp_grpc_mt_bench/Dockerfile>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/cpp_grpc_mt_bench/main.cpp>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/cpp_asio_grpc_bench/Dockerfile>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/14a8435/cpp_grpc_mt_bench/Dockerfile>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/14a8435/cpp_asio_grpc_bench/Dockerfile>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/HEAD/cpp_grpc_mt_bench/Dockerfile>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/go_grpc_bench/Dockerfile>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/go_grpc_bench/go.mod>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/14a8435/go_grpc_bench/Dockerfile>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/14a8435/go_grpc_bench/go.mod>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/HEAD/go_grpc_bench/Dockerfile>
  - <https://github.com/grpc/grpc-go>
  - <https://github.com/grpc/grpc-go/commits>
- **Sources the enricher read:**
  - <https://github.com/grpc/grpc-go>
  - <https://raw.githubusercontent.com/grpc/grpc-go/HEAD/README.md>
  - <https://raw.githubusercontent.com/grpc/grpc-go/HEAD/go.mod>
  - <https://raw.githubusercontent.com/grpc/grpc-go/v1.79.3/go.mod>
  - <https://raw.githubusercontent.com/grpc/grpc-go/HEAD/server.go>
  - <https://raw.githubusercontent.com/grpc/grpc-go/v1.79.3/server.go>
  - <https://raw.githubusercontent.com/grpc/grpc-go/HEAD/internal/transport/controlbuf.go>
  - <https://raw.githubusercontent.com/grpc/grpc-go/HEAD/internal/transport/http_util.go>
  - <https://raw.githubusercontent.com/grpc/grpc-go/HEAD/Documentation/concurrency.md>
  - <https://github.com/grpc/grpc-go/releases>
  - <https://github.com/grpc/grpc-go/security/advisories>
  - <https://github.com/grpc/grpc-go/security/advisories/GHSA-vp52-pcj8-j9qc>
  - <https://github.com/grpc/grpc-go/security/advisories/GHSA-hrxh-6v49-42gf>
  - <https://github.com/grpc/grpc-go/issues?q=is%3Aissue+label%3A%22Type%3A+Performance%22>
  - <https://github.com/LesnyRumcajs/grpc_bench/discussions/559>
  - <https://github.com/LesnyRumcajs/grpc_bench/discussions/547>
  - <https://github.com/LesnyRumcajs/grpc_bench/tree/c4c93b3/go_grpc_bench>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/README.md>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/bench.sh>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/go_grpc_bench/Dockerfile>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/go_grpc_bench/go.mod>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/go_grpc_bench/example/main.go>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/cpp_grpc_mt_bench/Dockerfile>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/cpp_grpc_mt_bench/main.cpp>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/grpc/grpc-go`) · [data/wave14/enrich/raw/github_com_grpc_grpc_go.json](../../../data/wave14/enrich/raw/github_com_grpc_grpc_go.json) (enrichment confidence 0.7)

</details>
