# Rust raw tokio HTTP/1.1 server (HttpArena tokio entry)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Web and serving](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `MIT` · 🟢 active

> Benchmark-only hand-rolled HTTP/1.1 server on raw tokio; 1.27x nginx on HttpArena baseline-4096 but 0.96x libreactorng (C).

| | |
|---|---|
| **Beats** | nginx 1.31.4 (C, custom handler module, -O3 -march=native -DNDEBUG) and libreactorng (C, io_uring, gcc -O3 -march=native) implementing the same HttpArena endpoints |
| **Claimed result** | baseline-4096: 4,187,085 req/s vs nginx 3,284,513 (1.27x, derived from page data), h2o 3,641,609 (1.15x), mongoose 3,707,598 (1.13x), Drogon 2,022,710 (2.07x), but libioma 4,255,834 (0.98x) and libreactorng 4,377,377 (0.96x) are slightly ahead. pipelined-4096: 54,755,795 vs libreactorng 43,424,448 (1.26x), nginx 4,037,345 (13.6x). limited-conn-4096: 2,721,455 vs libioma 2,707,029 (1.01x), nginx 2,626,297 (1.04x). |
| **Workload** | HttpArena baseline (mixed GET/POST with query parsing, 4096 connections), 16x pipelined and limited-conn profiles for a minimal HTTP/1.1 server hand-written on raw tokio (no HTTP framework): one current_thread runtime per core with SO_REUSEPORT, hand-rolled request parser, responses batched per read. Code lives in frameworks/tokio of the HttpArena repo. |
| **Metric** | throughput |
| **Hardware** | HttpArena dedicated machine: AMD Ryzen Threadripper PRO 3995WX (Zen 2, 64 cores / 128 threads, one NUMA node), 251 GiB RAM, Ubuntu 24.04.4 LTS, kernel 6.17.0-22-generic, Docker 29.3.0 (runc), performance governor (site/data/current.json, site/content/docs/hardware/_index.md). The server container is pinned to cpuset 0-31,64-95 (32 cores / 64 threads) for these profiles and the load generator (gcannon for HTTP/1.1, wrk for the TLS profiles, h2load for h2c) runs on the other half over loopback; 5 s runs, best of 3 (scripts/lib/common.sh RUNS=3, scripts/lib/profiles.sh). current.json is undated and describes the machine now, not necessarily at the date of each results file. |
| **Compiler and flags** | tokio entry: rust:1.95 image, RUSTFLAGS='-C target-cpu=native' cargo build --release with opt-level 3, thin LTO, codegen-units 1, panic='abort', tokio 1 with only io-util/net/rt/time features plus socket2 (frameworks/tokio/Dockerfile and Cargo.toml). C/C++ rows: nginx 1.31.4 with a custom C handler module, --with-cc-opt='-O3 -march=native -DNDEBUG' (debian:trixie); libreactorng 7a65f8b configured CFLAGS='-O3 -march=native' and its server built gcc -O3 -march=native (no LTO); libioma and mongoose gcc-14 -O3 -march=native -flto; h2o clang CMake Release -march=native -mtune=native, no LTO; agensio CMake Release -DAGENSIO_NATIVE=ON; userver service CMake Release -march=native on the prebuilt userver v3.2 image; Drogon handler only, CMake Release on the unpinned drogonframework/drogon:latest image (MDA2AV/HttpArena frameworks/&lt;name&gt;/Dockerfile). |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | yes |
| **Why it wins** | Per-core current_thread runtimes with SO_REUSEPORT (no work stealing), TCP_NODELAY, responses batched per read and a minimal hand-rolled parser (frameworks/tokio README); the same design as the C entries, so the source gives no language-level mechanism. |
| **Adoption** | HttpArena repo has 128 stars; tokio itself is a widely used runtime |
| **Last commit** | 2026-10-11 |
| **Links** | [repository](https://github.com/MDA2AV/HttpArena) · [benchmark](https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/tokio.json) |

## Verdict

HttpArena on an AMD Ryzen Threadripper PRO 3995WX (server pinned to 32 cores / 64 threads, gcannon over loopback, 4,096 connections, best of 3 five-second runs): 4,187,085 req/s against nginx 1.31.4 3,284,513 (1.27x), h2o 3,641,609 (1.15x), libioma 4,255,834 (0.98x) and libreactorng 4,377,377 (0.96x); pipelined-4096 54,755,795 against libreactorng 43,424,448 (1.26x); limited-conn-4096 2,721,455 against libioma 2,707,029 (1.01x). The rows come from runs weeks apart and the servers send different response sizes; all ratios are derived from page data.

## Use it when

- As a reference design for a thread-per-core tokio HTTP/1.1 server: plain epoll tokio reached 4,187,085 req/s at 4,096 connections on a 32-core/64-thread cpuset, about 4% behind libreactorng (C, io_uring) and 1.17x the HttpArena tokio-uring entry (3,565,878).
- Throughput-bound keep-alive or pipelined HTTP/1.1 services with tiny CPU-only handlers, where batching all responses from one read into one write pays off.
- When CPU per request at a fixed load matters: at a pinned 1M req/s it used 18.75 us of CPU per request against 21.04 us for libreactorng and 19.32 us for libioma (partly because its responses are smaller).
- Connection-churn workloads (limited-conn, 10 requests per connection): 2,721,455 req/s, level with libioma 2,707,029 and libreactorng 2,685,717.

## Skip it when

- Tail-latency-sensitive services: at a pinned 1M req/s its p99.9 was 25,128 us against libreactorng's 687 us (36.6x) and libioma's 1,147 us; at 10k req/s 2,979 us against 182 us (16x), although mean and p99 are close (p99 166 us against 171 us at 1M).
- Production traffic: no Date header, no method check, a 200 with the a + b sum for any unknown path, no TLS or HTTP/2, a 1 MiB buffer cap that closes the connection without a status, and a remotely triggerable abort (see gotchas).
- As proof that Rust beats C: it trails libreactorng (0.96x) and libioma (0.98x) on baseline-4096, ties on limited-conn, and the only clear win (pipelined, 1.26x) is a reference-only profile that tracks its smaller responses.
- As a prediction for hyper, axum or actix: HttpArena's hyper entry made 3,003,360 req/s and actix-web 2,775,120 on the same profile.
- Memory-tight hosts at high connection counts: each connection task holds a 16 KiB stack array plus two 16 KiB Vecs (about 48 KiB, derived from main.rs), consistent with 187 MiB at baseline-4096 (libreactorng 105 MiB, though libioma 1.2 GiB and nginx 3.5 GiB) and 426 MiB at limited-conn against 175 MiB.

## How it is fast

One OS thread per allowed CPU (available_parallelism, 64 under the 0-31,64-95 cpuset), each running its own tokio current_thread runtime with a private SO_REUSEPORT listener, so the kernel shards accepts and there is no work stealing, cross-thread wakeup or shared state; connections are tasks on the runtime that accepted them, on epoll through mio, with TCP_NODELAY. Each read parses every complete request in the buffer and appends all responses to one Vec flushed with a single write_all, so a 16-deep pipelined burst costs one syscall (pipelined-4096 54.8M req/s against libreactorng's 43.4M). Responses are minimal (status line, Content-Type, Content-Length; no Date or Server header), and the build is thin LTO, codegen-units 1, panic = abort, target-cpu=native, tokio with only rt/net/io-util/time. The design matches the C entries; nothing in it is a Rust-language mechanism.

## Compared with alternatives

Among Rust siblings, read this as the ceiling of plain tokio: it beats the HttpArena tokio-uring entry (3.57M), hyper (3.00M), actix-web (2.78M) and ntex (2.17M) on baseline-4096, so pick actix-web or ntex when you need a framework and this design only for a custom engine. For a reusable thread-per-core engine at the same throughput, libxev (Zig, 4.38M) or zix and zeemo (Zig, 4.44M and 4.42M) are standalone projects, whereas this is a single benchmark file.

## Integration

| | |
|---|---|
| **Form** | source-drop (frameworks/tokio/src/main.rs plus Cargo.toml in MDA2AV/HttpArena; no crate) |
| **Dependencies** | tokio 1 (default features off; io-util, net, rt, time) and socket2 0.5 |
| **Minimum toolchain** | not documented; built on the rust:1.95 Docker image, edition 2021 |
| **Platforms** | Linux (relies on SO_REUSEPORT accept sharding; built with -C target-cpu=native); measured on x86-64 Zen 2 (Threadripper PRO 3995WX), kernel 6.17 |
| **Thread safety** | shared-nothing: one current_thread runtime and listener per OS thread, each connection a task on its accepting runtime; no state is shared between threads |
| **Drop-in for the baseline** | no |

## Gotchas

- Remote crash found by reading the code (not executed): parse_usize accepts any Content-Length up to 18446744073709551615, body_start + cl then wraps in the release build, the 'buf.len() &lt; body_start + cl' check passes, and &buf[body_start..body_start + cl] panics; Cargo.toml sets panic = "abort", so one such request kills the whole process (all 64 runtimes). decode_chunked has the same wrap for a chunk size of ffffffffffffffff. The bug is in the first commit (2f52740) and scripts/validate.sh does not test it; it does not affect the measured numbers.
- Cross-run rows and code drift: the baseline-4096, pipelined-4096 and limited-conn-4096 rows are unchanged since at least 2026-07-24 (commit 5698fa8), so they were measured between 2026-06-06 and 2026-07-24 with the original main.rs (no time driver, no /delay branch); the current file adds enable_time() and a delay branch. The libreactorng rows quoted are a 2026-09-07 re-run; its July rows were 4,309,995, 42,807,713 and 2,662,214, against which tokio is 0.97x, 1.28x and 1.02x. Run-to-run drift of about 1.5% makes the 0.96-1.02x ratios ties.
- Smaller responses carry part of the win: about 62.9 bytes per response at baseline-4096 against 108.7 for libreactorng and 135.4 for nginx, and 61.4 against 106.2 at pipelined-4096 (3.36 GB/s against 4.61 GB/s output), all derived from page data; HttpArena's validation does not require a Date header.
- Parser shortcuts: a naive windows() search for the header end rescans the whole buffer on every fragmented read, malformed chunk framing is treated as incomplete until the 1 MiB cap closes the connection, and accept errors loop with continue (a busy loop when file descriptors run out).

## Known shortcomings

- Behind libreactorng (0.96x) and libioma (0.98x) at baseline-4096 and tied on limited-conn; the only clear win over C is the reference-only pipelined row; the suite-written minimal server sends no Date or Server header (62.9 vs 108.7 bytes per response), so the work is unequal and the language-level claim is unsupported. HttpArena runs are best of 3, cross-run rows, 32-core server.
- Security bug found by reading the code (not executed): parse_usize accepts a Content-Length of 18446744073709551615, body_start + cl wraps in the release build and the slice panics; with panic='abort' one such request kills all 64 runtimes, and decode_chunked wraps the same way for a chunk size of ffffffffffffffff; present since the first commit 2f52740 and not covered by validate.sh. The numbers are unaffected. Measurement window: the tokio H1 rows have been unchanged since 5698fa8 (2026-07-24), so they were measured between June 6 and July 24 with an older main.rs; the libreactorng July rows (4,309,995 / 42,807,713 / 2,662,214) give tokio 0.97x / 1.28x / 1.02x. At 1M req/s tokio's p99.9 is 25,128 us against libreactorng's 687 us (36.6x worse) while its CPU per request is lower (18.75 vs 21.04 us).

## Caveats and trade-offs

Not faster than the best C entries on HttpArena's scored HTTP/1.1 profiles: at baseline-4096 libreactorng (4,377,377) and libioma (4,255,834) are ahead (0.96x, 0.98x), and limited-conn-4096 is a tie (1.01x over libioma 2,707,029, mongoose 2,701,933 and libreactorng 2,685,717). The only clear win over C is pipelined-4096 (1.26x libreactorng), which is reference-only in HttpArena's composite score (site/content/docs/scoring/composite-score.md). The entry is a minimal server written for the suite (meta.json lists no maintainers; it is not tokio project code): it routes only /pipeline and /delay and answers every other path with the a+b sum, sends no Date or Server header, and runs on epoll while libreactorng and libioma use io_uring. Bytes per response (derived from page data, bandwidth divided by req/s) are 62.9 at baseline-4096 against 108.7 for libreactorng (which sends a per-second cached Date header, per vanilla's docs/PERF_GAP_ANALYSIS.md), 85.8 for libioma, 72.5 for mongoose, 98.2 for h2o and 135.4 for nginx; at pipelined-4096 it writes 61.4 bytes per response against libreactorng's 106.2 (3.36 GB/s against 4.61 GB/s), so the pipelined ratio tracks smaller responses. The ratios over nginx, h2o and mongoose compare a minimal handler with full servers that write larger headers. Does not generalise to hyper or axum (hyper 3,003,360 req/s at baseline-4096). Other non-C entries are faster than this Rust entry at baseline-4096 (zix 4,442,329 and zeemo 4,422,489 in Zig, minima-sync 4,386,544 in C#). Each number is the best of 3 runs of 5 s with the server limited to 32 cores / 64 threads; results files are undated and rows come from different runs (tokio.json last written 2026-08-30, libreactorng.json 2026-09-07, per git history). The C/C++ rows are built -O3 -march=native (nginx, libreactorng, libioma, mongoose; libioma and mongoose also with LTO) or clang CMake Release -march=native (h2o); the Drogon entry builds only its handler against the unpinned drogonframework/drogon:latest image, so the Drogon ratio (2.07x) is weaker evidence than the nginx, h2o, libreactorng and libioma ratios. [retier] Enricher: remote crash found by reading the code (not executed); parse_usize accepts a Content-Length of 18446744073709551615, body_start + cl wraps in the release build and the slice panics; with panic='abort' one such request kills all 64 runtimes, and decode_chunked wraps the same way for a chunk size of ffffffffffffffff (present since the first commit 2f52740, not covered by validate.sh). The tokio H1 rows have been unchanged since 5698fa8 (2026-07-24), so they were measured between June 6 and July 24 with an older main.rs; the libreactorng July rows (4,309,995 / 42,807,713 / 2,662,214) give tokio 0.97x / 1.28x / 1.02x. At 1M req/s tokio's p99.9 is 25,128 us against libreactorng's 687 us while its CPU per request is lower (18.75 vs 21.04 us).

The measured program is a benchmark-only, hand-rolled HTTP/1.1 server (not tokio, hyper or a framework); Linux only; epoll based, no TLS in this entry.

## Maintenance

HttpArena is active (MIT, 128 stars, last commit 2026-10-11) and the entry was last touched 2026-08-29, but it is MIT benchmark code with no API, no maintainers and a one-request abort on oversized Content-Length, so treat it as a design reference, not a dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** Every quoted number matches site/data/results/tokio.json and the sibling nginx, libreactorng, libioma, h2o, mongoose, drogon and hyper JSON files in MDA2AV/HttpArena; the code is public (frameworks/tokio/{Dockerfile,Cargo.toml,src/main.rs}, frameworks/libreactorng/{Dockerfile,src/server.c}, frameworks/nginx/Dockerfile, scripts/lib/common.sh, scripts/lib/profiles.sh), Rust and C flags are in the Dockerfiles and Cargo.toml, and the CPU model (Threadripper PRO 3995WX) is in site/data/current.json, the HttpArena tier-A precedent (actix, libxev, tokio-uring, nilo).
- **Verifier notes:** All quoted numbers verified against the HttpArena JSON files; tier A kept on the HttpArena precedent. Corrected: runs are best of 3, not one; same_algorithm set false (62.9 bytes per response with no Date or Server header against 108.7 for libreactorng and 135.4 for nginx, epoll against io_uring, routing limited to /pipeline). Shortcomings to record: behind libreactorng (0.96x) and libioma (0.98x) at baseline-4096, a tie at limited-conn, the only clear C win is the reference-only pipelined profile, a minimal suite-written entry rather than tokio project code, and cross-run rows (2026-08-30 against 2026-09-07). The language-level claim is not supported by these data.
- **Fields the verifier corrected:** `hardware`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-49 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/tokio.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/nginx.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/libreactorng.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/libioma.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/h2o.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/mongoose.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/drogon.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/hyper.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/zix.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/minima-sync.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/current.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/frameworks.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/content/docs/hardware/_index.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/content/docs/scoring/composite-score.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/lib/common.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/lib/profiles.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/tokio/Cargo.toml>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/tokio/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/tokio/README.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/tokio/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/tokio/src/main.rs>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/libreactorng/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/libreactorng/src/server.c>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/nginx/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/libioma/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/h2o/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/mongoose/Dockerfile>
  - <https://github.com/MDA2AV/HttpArena>
  - <https://github.com/MDA2AV/HttpArena/commits/main>
  - <https://github.com/MDA2AV/HttpArena/tree/main/site/data/results>
  - <https://github.com/MDA2AV/HttpArena/tree/main/frameworks/tokio>
  - <https://github.com/MDA2AV/HttpArena/commits/main/site/data/results/tokio.json>
  - <https://github.com/MDA2AV/HttpArena/commits/main/site/data/results/libreactorng.json>
  - <https://raw.githubusercontent.com/enghitalo/vanilla/HEAD/docs/PERF_GAP_ANALYSIS.md>
- **Sources the enricher read:**
  - <https://github.com/MDA2AV/HttpArena>
  - <https://github.com/MDA2AV/HttpArena/issues?q=tokio>
  - <https://github.com/MDA2AV/HttpArena/commits/main/frameworks/tokio>
  - <https://github.com/MDA2AV/HttpArena/commits/main/site/data/results/tokio.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/tokio/README.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/tokio/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/tokio/Cargo.toml>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/tokio/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/tokio/src/main.rs>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/2f52740/frameworks/tokio/src/main.rs>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/2f52740/frameworks/tokio/Cargo.toml>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/tokio.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/5698fa8/site/data/results/tokio.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/2773acb/site/data/results/tokio.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/f78b367/site/data/results/tokio.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/7c29cee/site/data/results/tokio.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/libreactorng.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/5698fa8/site/data/results/libreactorng.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/libioma.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/nginx.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/validate.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/lib/common.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/lib/profiles.sh>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:rust/mda2av/httparena#baseline-4096`) · [data/wave14/enrich/raw/lang_rust_mda2av_httparena_baseline_4096.json](../../../data/wave14/enrich/raw/lang_rust_mda2av_httparena_baseline_4096.json) (enrichment confidence 0.75)

</details>
