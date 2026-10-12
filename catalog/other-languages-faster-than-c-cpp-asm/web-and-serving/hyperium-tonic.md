# tonic (Rust gRPC)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Web and serving](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟢 active

> Rust async gRPC (tokio, hyper, prost) that out-served the stock C++ gRPC async servers in grpc_bench's small unary echo test.

| | |
|---|---|
| **Beats** | gRPC C++ (grpc/grpc) servers cpp_grpc_st, cpp_grpc_mt and cpp_asio_grpc in the grpc_bench suite |
| **Claimed result** | 1-CPU server (req/s, avg latency): rust_tonic_st 41,546 (23.77 ms) vs cpp_grpc_st 26,700 (37.33 ms), cpp_grpc_mt 26,376 and cpp_asio_grpc 24,926 (1.56x, 1.58x, 1.67x, derived from page data); rust_tonic_mt 35,443 (1.33x vs cpp_grpc_st). At 2 CPUs rust_tonic_st 42,072 vs cpp_grpc_st 26,229 (1.60x) but cpp_grpc_mt 69,882 and rust_tonic_mt 53,832 (0.77x); at 3 CPUs cpp_grpc_mt 71,806 vs rust_tonic_mt 64,091 (0.89x). |
| **Workload** | grpc_bench 'complex_proto' unary scenario: 50 client connections, 1000 concurrent requests, unlimited QPS, 120 s with 30 s warmup, server RAM 512m, commit 14a8435 (2022-04-22); server limited to 1, 2 or 3 CPUs. |
| **Metric** | throughput |
| **Hardware** | Intel(R) Xeon(R) CPU E5-1650 v3 @ 3.50GHz, 32G RAM (grpc_bench wiki page 2022-04-23; server limited to 1, 2 or 3 CPUs, client 9 CPUs) |
| **Compiler and flags** | 2022-04-23 run at grpc_bench commit 14a8435. rust_tonic_st: rust:1.59 image, cargo build --release --locked, [profile.release] opt-level 3, codegen-units 1, lto true; jemallocator 0.3.2, tonic 0.7, prost 0.10, tokio 1.17 current_thread. cpp_grpc_st: gcc:11 image, g++ -O3 -flto on main.cpp and the protoc-generated stubs, linked with -lgrpc++ -lprotobuf -lgrpc -ljemalloc from the distro packages (apt libgrpc++-dev). cpp_grpc_mt: the same plus --std=c++20 and -lpthread, one completion queue and thread per GRPC_SERVER_CPUS. cpp_asio_grpc: asio-grpc 1.0.0, CMake Release, the same distro libgrpc++. The gcc:11 image was presumably Debian bullseye, whose libgrpc++-dev is gRPC 1.30.2-3 (Debian package listing, search snippet only); that library was built with Debian's flags, not the benchmark's -O3 -flto. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | yes |
| **Why it wins** | Single-threaded tokio current_thread runtime with jemalloc avoids cross-thread synchronization at a 1-CPU limit (inference from the benchmark setup; no source claim). |
| **Adoption** | 12.5k stars |
| **Last commit** | 2026-10-07 |
| **Links** | [repository](https://github.com/hyperium/tonic) · [benchmark](https://github.com/LesnyRumcajs/grpc_bench/wiki/2022-04-23-bench-results) |

## Verdict

In grpc_bench's complex_proto unary echo test (commit 14a8435, 2022-04-23 wiki page, Xeon E5-1650 v3, 50 connections, 1000 in-flight requests, 120 s after a 30 s warm-up), rust_tonic_st (tonic 0.7, Rust 1.59, LTO, jemalloc) served 41,546 req/s at 1 CPU. The C++ servers, built with g++ 11 -O3 -flto against the distro libgrpc++, served 26,700 (cpp_grpc_st), 26,376 (cpp_grpc_mt) and 24,926 (cpp_asio_grpc), so tonic was 1.56-1.67x faster, but cpp_grpc_mt led at 2 and 3 CPUs. All three C++ servers register only one pending request per completion queue, which gRPC's performance guide warns serialises request handling.

## Use it when

- New gRPC services or clients written in Rust: async/await on tokio, prost-generated types, streaming, rustls TLS, health and reflection services.
- Small unary RPCs at high concurrency in CPU-capped containers. In grpc_bench's 1-CPU complex_proto test, rust_tonic_st served 41,546 req/s against 24,926-26,700 for the three C++ servers in 2022, and 102,754 against 56,669-57,403 in the 2026-04-23 run.
- One process per core with predictable tails: the current_thread variant held p99 at 33.24 ms (2022) and 14.47 ms (2026) at 1 CPU, while the multi-thread runtime's p99 was 668.38 ms and 98.22 ms.
- Memory-tight sidecars: 12-18 MiB average memory in grpc_bench, close to the C++ servers (about 9-37 MiB) and far below dotnet_grpc (114-176 MiB).

## Skip it when

- In-process use from C++. Tuning grpc++ (more pre-registered requests per completion queue, or the callback API) is likely cheaper than adding a Rust process, and the grpc_bench C++ baseline never did that tuning.
- Multi-core servers judged on the 2022 data alone. At 2 and 3 CPUs, cpp_grpc_mt (69,882 and 71,806 req/s) and cpp_asio_grpc beat rust_tonic_mt (53,832 and 64,091). tonic_mt led C++ at 2-4 CPUs only in the 2026 run.
- The multi-thread runtime under a 1-CPU quota when tail latency matters: p99 was about 20x (2022) and 7x (2026) worse than the current_thread variant.
- When you need a stable API: the crate is still 0.x, master is preparing breaking changes (the README points to the 0.14.x branch), and the repository now lives at grpc/grpc-rust next to a new grpc crate.
- Tail-latency-critical clients on aarch64: issue #1606 (elevated p99 and above on a master client compared with v0.10.2) is still open and has no root cause.

## How it is fast

The README describes three layers: a generic gRPC core, the hyper/h2 HTTP/2 implementation on tokio, and prost codegen, all compiled together, so the grpc_bench build gets whole-program opt-level 3, LTO and codegen-units 1 plus jemalloc. The winning 1-CPU variant, rust_tonic_st, runs tokio's current_thread runtime: one event loop with no cross-thread wake-ups or work stealing. That last point is the benchmark's setup rather than a documented tonic technique. Part of the measured gap comes from the C++ side, not from tonic (see gotchas).

## Compared with alternatives

Pick tonic over Thruster (thruster-grpc) when you want the mainstream Rust gRPC stack with prost codegen, TLS, health, reflection and xDS work; rust_thruster_st was within 0.5-4.2% of rust_tonic_st in both grpc_bench runs (41,334 vs 41,546 and 98,464 vs 102,754). Pick it over grpc-dotnet or grpc-go when the service is in Rust or memory is tight (about 13-15 MiB vs 120-135 MiB for dotnet_grpc in 2026); grpc-dotnet was close in multi-core throughput (136,452 vs 139,886 at 3 CPUs).

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | tokio, hyper 1 and h2 0.4, hyper-util, tower 0.5, axum 0.8 (default router feature), bytes, tokio-stream, tokio-util; prost through tonic-prost; optional rustls (tls-ring or tls-aws-lc), flate2 (gzip/deflate), zstd; codegen in tonic-build/tonic-prost-build needs protoc |
| **Minimum toolchain** | Rust 1.88 (MSRV in the README and the workspace rust-version); the 2022 benchmark used Rust 1.59 with tonic 0.7 |
| **Platforms** | not documented in the README (any target tokio supports); grpc_bench measured only x86-64 Linux in Docker |
| **Thread safety** | Handlers take &self and may run concurrently on a multi-thread tokio runtime, so shared service state needs Sync types; the README documents no other threading rules. |
| **Drop-in for the baseline** | partial — wire-compatible with gRPC C++ peers (the repo carries interop tests), but a different language and API; C++ code cannot link it as a grpc++ replacement |

## Gotchas

- Harness flaw in the baseline: all three grpc_bench C++ servers (cpp_grpc_st, cpp_grpc_mt and cpp_asio_grpc) post exactly one RequestSayHello per completion queue, while the client keeps 1000 requests in flight. In the CallData servers, each call registers its successor only on reaching PROCESS. The asio-grpc server runs one accept-loop coroutine per GrpcContext and awaits one agrpc::request at a time. gRPC's own performance guide says to 'register enough server requests for the desired level of concurrency' to avoid 'a slow path that results in essentially serial request processing'. grpc_bench issue #490 (opened 2024-11-04, still open) reports this for cpp_grpc_mt; the maintainer replied that the code came from the gRPC examples. The server code is unchanged at the 2026 run's commit c4c93b3. The C++ servers also link the distro libgrpc++ package, asio-grpc is pinned to 1.0.0, and cpp_grpc_mt runs one thread per completion queue, where the guide (as of gRPC 1.41) suggests two. So the C++ numbers are a lower bound for grpc++, which is consistent with rust_grpcio (C core) also beating them at 1 CPU (31,035 req/s in 2022).
- The record's caveat that the win appears only at 1 CPU is outdated. In the 2026-04-23 run (discussion #559, Xeon Gold 6548N, 4096m server RAM, tonic 0.14 on Rust 1.94), rust_tonic_mt beat the best C++ server at 2, 3 and 4 CPUs: 130,370 vs 74,869 (1.74x), 139,886 vs 81,581 (1.71x) and 136,638 vs 85,485 (1.60x), derived from page data. The same under-registered C++ harness was used.
- Results depend on the runtime flavour. At 1 CPU, current_thread beat multi-thread by 17-25% in throughput and by 7-20x at p99. A current_thread server uses one core per process, so scaling out means several processes behind SO_REUSEPORT or a load balancer.
- Tonic was not alone. At 1 CPU in 2022, go_vtgrpc (44,074) and rust_thruster_st (41,334) matched or beat rust_tonic_st, and in 2026 dotnet_grpc reached 84,809 against 57,403 for the best C++ server. The lead over C++ is a property of this harness as much as of tonic.

## Known shortcomings

- grpc_bench discussion 559: wins only at 1 CPU (41,546 vs cpp_grpc_st 26,700 req/s); cpp_grpc_mt leads at 2-3 CPUs; the C++ side links the distro libgrpc++ (probably 1.30.2 on bullseye, snippet only) rather than a benchmark-flag build; rust_grpcio (C core) also beat the C++ rows.
- Harness flaw: all three grpc_bench C++ servers (cpp_grpc_st, cpp_grpc_mt, cpp_asio_grpc) post exactly one RequestSayHello per completion queue against 1,000 in-flight requests, which gRPC's performance guide calls essentially serial request processing (grpc_bench issue #490, open since 2024-11-04; same code at the 2026 commit c4c93b3), so the C++ baseline is untuned. The record's 'win only at 1 CPU' caveat is outdated: discussion #559 (2026-04-23, Xeon Gold 6548N) has rust_tonic_mt beating the best C++ at 2/3/4 CPUs (130,370 vs 74,869; 139,886 vs 81,581; 136,638 vs 85,485). The repo is now grpc/grpc-rust (hyperium/tonic redirects).

## Caveats and trade-offs

The win appears only with the server limited to 1 CPU. There, all three C++ servers (cpp_grpc_st 26,700, cpp_grpc_mt 26,376, cpp_asio_grpc 24,926 req/s) trail rust_tonic_st (41,546) and rust_tonic_mt (35,443). With 2 and 3 CPUs, cpp_grpc_mt (69,882 and 71,806) and cpp_asio_grpc (66,828 and 71,296) lead rust_tonic_mt (53,832 and 64,091). The wiki page states no compiler versions or flags; they come from the Dockerfiles at commit 14a8435, and the repo's current Dockerfiles (gcc 16.1, Rust 1.94) are newer than the run. The C++ servers link the distro libgrpc++ package (probably gRPC 1.30.2 from Debian bullseye, a 2020 release, against tonic 0.7 from 2022). That library is built with distribution flags, while the Rust stack is compiled whole with opt-level 3 and LTO. At 1 CPU, rust_grpcio, which compiles the gRPC C core from source, reached 31,035 req/s, also above every C++ server, so part of the gap may come from the distro build or the old gRPC version rather than from tonic. go_vtgrpc (44,074) topped the 1-CPU table. Both servers do the same echo work (copy the request string into the reply). It is a single run with no variance reported. The tonic README makes no performance claim; the evidence is the third-party grpc_bench suite, whose latest wiki results page is this 2022-04-23 run. [retier] Enricher (Pekko gRPC pass): grpc_bench's cpp_grpc_mt pre-posts one call per completion queue (gRPC's own server_async.cc pre-posts 5000) and allocates per RPC; it links unpinned Debian libgrpc++ (likely 1.51.1). Every grpc_bench row compared against cpp_grpc_mt inherits this crippled baseline.

Rust async gRPC on tokio and hyper; the winning variant is single-threaded, so it cannot use more than one core per process; calling it from C++ needs a separate process.

## Maintenance

Actively maintained: last commit 2026-10-07, MIT, 12.5k stars. The project now lives at github.com/grpc/grpc-rust (hyperium/tonic redirects there), and the latest release is the 0.14.x line, with breaking changes pending on master. It is a copyable crate, but the measured advantage over C++ rests on an untuned grpc++ harness: one outstanding request per completion queue, the open grpc_bench issue #490.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification B, tier now C.
- **Tier reason:** grpc_bench is a well-known independent third-party suite, and its 2022-04-23 wiki page shows rust_tonic_st at 41,546 req/s against cpp_grpc_st 26,700, cpp_grpc_mt 26,376 and cpp_asio_grpc 24,926 at 1 CPU on a Xeon E5-1650 v3. The server code and Dockerfiles at commit 14a8435 are public (g++ -O3 -flto in cpp_grpc_st_bench/Dockerfile; rust 1.59 with opt-level 3, LTO and codegen-units 1 in rust_tonic_st_bench/Cargo.toml). The C++ side links the distro libgrpc++ package, whose version and build flags the repo does not state, so this is not A.
- **Retiered** B to C: Downgraded from B to C (crippled-baseline precedent): grpc_bench's C++ entry cpp_grpc_mt pre-posts one RequestSayHello per completion queue and does new/delete per RPC, while gRPC's own async QPS server pre-posts 5000 per queue, and it links unpinned Debian libgrpc++ (likely gRPC 1.51.1) with version and flags unrecorded, so wins over it measure a weak C++ server setup rather than the C++ gRPC stack at its best.
- **Verifier notes:** Numbers and derived ratios match the 2022-04-23 wiki page. The record's compiler_and_flags described the repo's current HEAD Dockerfiles; they are replaced with the commit-14a8435 build used for the run. The caveat that the 1-CPU ratio compares only against single-threaded C++ servers was wrong, since cpp_grpc_mt also ran at 1 CPU (26,376). Shortcomings: win only at a 1-CPU limit; C++ baseline is a stale distro libgrpc++ not built with the benchmark's flags; rust_grpcio (C core) also beat it; single 2022 run. Metadata confirmed: MIT, 12.5k stars, last commit 2026-10-07.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-44 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/LesnyRumcajs/grpc_bench/wiki/2022-04-23-bench-results>
  - <https://github.com/LesnyRumcajs/grpc_bench/wiki>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/14a8435/cpp_grpc_st_bench/Dockerfile>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/14a8435/cpp_grpc_mt_bench/Dockerfile>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/14a8435/cpp_asio_grpc_bench/Dockerfile>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/14a8435/rust_tonic_st_bench/Dockerfile>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/14a8435/rust_tonic_st_bench/Cargo.toml>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/14a8435/rust_tonic_mt_bench/Cargo.toml>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/14a8435/cpp_grpc_st_bench/main.cpp>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/14a8435/cpp_grpc_mt_bench/main.cpp>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/14a8435/rust_tonic_st_bench/src/main.rs>
  - <https://github.com/hyperium/tonic>
  - <https://github.com/hyperium/tonic/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/hyperium/tonic/HEAD/README.md>
  - <https://raw.githubusercontent.com/hyperium/tonic/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/hyperium/tonic/HEAD/tonic/Cargo.toml>
  - <https://github.com/hyperium/tonic>
  - <https://github.com/grpc/grpc-rust/commits>
  - <https://github.com/hyperium/tonic/issues?q=is%3Aissue%20performance>
  - <https://github.com/hyperium/tonic/issues/1606>
  - <https://github.com/grpc/grpc-rust/issues/784>
  - <https://github.com/grpc/grpc-rust/issues/1001>
  - <https://github.com/LesnyRumcajs/grpc_bench/wiki/2022-04-23-bench-results>
  - <https://github.com/LesnyRumcajs/grpc_bench/discussions/559>
  - <https://github.com/LesnyRumcajs/grpc_bench/issues?q=cpp>
  - <https://github.com/LesnyRumcajs/grpc_bench/issues/490>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/14a8435/rust_tonic_st_bench/src/main.rs>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/14a8435/rust_tonic_mt_bench/src/main.rs>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/14a8435/rust_tonic_st_bench/Cargo.toml>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/14a8435/rust_tonic_mt_bench/Cargo.toml>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/14a8435/rust_tonic_st_bench/Dockerfile>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/14a8435/cpp_grpc_st_bench/main.cpp>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/14a8435/cpp_grpc_mt_bench/main.cpp>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/14a8435/cpp_grpc_st_bench/Dockerfile>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/14a8435/cpp_grpc_mt_bench/Dockerfile>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/14a8435/cpp_asio_grpc_bench/main.cpp>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/14a8435/cpp_asio_grpc_bench/CMakeLists.txt>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/14a8435/cpp_asio_grpc_bench/Dockerfile>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/master/cpp_grpc_st_bench/main.cpp>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/master/cpp_grpc_st_bench/Dockerfile>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/rust_tonic_st_bench/Cargo.toml>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/rust_tonic_st_bench/Dockerfile>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/rust_tonic_st_bench/src/main.rs>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/rust_tonic_mt_bench/src/main.rs>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/cpp_grpc_mt_bench/main.cpp>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/cpp_grpc_mt_bench/Dockerfile>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/cpp_asio_grpc_bench/main.cpp>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/cpp_asio_grpc_bench/Dockerfile>
  - <https://raw.githubusercontent.com/grpc/grpc.io/main/content/en/docs/guides/performance.md>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/hyperium/tonic`) · [data/wave14/enrich/raw/github_com_hyperium_tonic.json](../../../data/wave14/enrich/raw/github_com_hyperium_tonic.json) (enrichment confidence 0.6)

</details>
