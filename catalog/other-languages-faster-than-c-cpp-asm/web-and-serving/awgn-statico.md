# statico

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Web and serving](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟢 active

> Rust benchmarking stub that returns one fixed HTTP response; its README table puts it ahead of nginx 'return 200'.

| | |
|---|---|
| **Beats** | nginx (static in-memory 'return' response) |
| **Claimed result** | README table, requests/s at 1 / 4 threads: statico (tokio) 399,025 / 1,071,433 vs nginx (return) 286,960 / 832,082 (1.39x / 1.29x) and statico (monoio) 656,517 / 1,436,420 (2.29x / 1.73x), but the nginx rows are from an earlier run (2025-12-31) than the statico rows (2026-03-28). In the original same-run table standard statico was 279,842 vs nginx 286,960 req/s at 1 thread (nginx 2.5% faster) and 966,248 vs 832,082 at 4 threads (1.16x, derived from page data). |
| **Workload** | Synthetic static in-memory HTTP response served to 1024 connections at 1, 2 and 4 server threads, comparing statico runtimes with nginx, HAProxy, Go net/http, fasthttp, Axum and actix-web. |
| **Metric** | throughput |
| **Compiler and flags** | cargo build --release with per-runtime feature flags; Cargo.toml [profile.release] is opt-level 3, lto fat, codegen-units 1, panic abort, mimalloc as default allocator (profile added in the 2026-09-12 commit 'Optimize release build for performance', after the table was last updated on 2026-04-25 'Benchmarks updated.'). nginx build and flags not stated. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | not stated |
| **Why it wins** | Pre-built responses held in memory, HTTP pipelining, thread-per-core io_uring runtimes (tokio-uring, monoio, glommio, compio) with CPU pinning for glommio and compio (README). |
| **Adoption** | 1 star; 872 crates.io downloads |
| **Last commit** | 2026-09-16 |
| **Links** | [repository](https://github.com/awgn/statico) · [benchmark](https://raw.githubusercontent.com/awgn/statico/HEAD/README.md) |

## Verdict

Author's README table, 1024 connections at 1, 2 and 4 server threads, with no published load generator, CPU, nginx build or nginx config: standard statico (hyper on per-thread Tokio) 399,025 / 1,071,433 req/s vs nginx 'return' 286,960 / 832,082 at 1 / 4 threads, monoio 656,517 / 1,436,420. The nginx row comes from the 2025-12-31 run and was not re-measured with the updated statico rows; in that original run statico was level with nginx on one thread (279,842 vs 286,960) and 1.16x faster on four.

## Use it when

- Upstream for load-testing an HTTP client, load generator, proxy or service mesh, where the backend must never be the bottleneck.
- Mock endpoint with a fixed status, headers and body, plus injected latency (--delay, or --body-delay for slow bodies) to test client timeouts.
- Measuring the keep-alive HTTP/1.1 request-rate ceiling of a Linux box or NIC with an io_uring runtime and the built-in --meter.
- Health-check or MCP mock stub in a CI or test environment.

## Skip it when

- Any real serving: every request gets the same response, with no routing, directory serving, access log or config file.
- Facing untrusted clients on the io_uring runtimes: a malformed request is treated as incomplete, so the connection is never answered or closed and its buffer keeps growing.
- As evidence that Rust beats nginx: the nginx row was never re-measured alongside the current statico rows, and the nginx configuration, load generator and CPU are unpublished.
- HTTP/2, TLS, verbose or body-delay on the io_uring runtimes, which support only HTTP/1.1 (TLS is tokio-only).
- Multi-thread scaling on macOS or Windows: SO_REUSEPORT load balancing is enabled only on Linux, FreeBSD, DragonFly, Solaris and illumos.

## How it is fast

Thread-per-core design: each worker runs its own single-threaded runtime (current-thread Tokio, or the io_uring runtimes tokio-uring, monoio, glommio, compio) with its own SO_REUSEPORT listener, so the kernel spreads connections and no work moves between threads. The io_uring runtimes bypass hyper: they set up the ring with SINGLE_ISSUER and COOP_TASKRUN (or SQPOLL on request), parse requests with httparse (via the author's http_wire crate) out of one reusable buffer, handle several pipelined requests per read, and write a response serialized once per connection. The default tokio runtime is stock hyper http1 with the body held as a shared Bytes value; mimalloc is the default global allocator.

## Compared with alternatives

Pick statico when you need a configurable mock or load-test target binary (status, headers, body, delays, metering) rather than a measured server. The HttpArena entries (tokio-uring, the raw tokio server) and routez rest on independent or better-documented harnesses against a pinned nginx build, so cite those for 'beats nginx' evidence.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | binary crate (cargo install statico): hyper 1, tokio, hyper-util, httparse, http_wire, socket2, rustls/tokio-rustls, clap, pingora-timeout, core_affinity, mimalloc (default feature); optional tokio-uring, monoio + io-uring, glommio, smol + smol-hyper, compio |
| **Minimum toolchain** | Rust edition 2021; no rust-version declared (the io_uring paths use inline const array initialisers, so Rust 1.79 or newer) |
| **Platforms** | tokio and smol runtimes on Linux, macOS and Windows; tokio-uring, monoio and glommio Linux-only; compio cross-platform (io_uring or IOCP) |
| **Thread safety** | Standalone server process; shared config is immutable and counters are sharded atomics, so there is no library API to share |
| **Drop-in for the baseline** | partial — it can replace an nginx 'location / { return 200; }' stub in a benchmark or mock setup, but it is not a substitute for nginx as a web server |

## Gotchas

- Cross-run baseline: the nginx, HAProxy, Go, Axum and actix-web rows (nginx 286,960 / 379,974 / 832,082) are unchanged since the table first appeared on 2025-12-31 (commit 5e044f0), while the statico rows were re-measured by 2026-03-28. In that original same-run table standard statico was 279,842 vs nginx 286,960 req/s at 1 thread (nginx 2.5% faster) and 966,248 vs 832,082 at 4 threads (1.16x). The README's 'about 40% faster single-threaded' and the doubled io_uring rows (270,263 rising to 589,086 to 656,517) are compared against nginx numbers from the older run.
- The io_uring responses are pre-encoded by http_wire, which writes only the status line, the user's headers and Content-Length, so there is no Date header (RFC 9110 requires one from an origin server with a clock) and no Server header, while nginx formats Date, Server and Content-Type per response. Pipelined requests are parsed from one read, but each response is still a separate awaited write_all, not one syscall per batch as the README says.
- Unsafe code in the monoio, tokio-uring and compio paths: Vec::from_raw_parts on a pointer into the middle of another Vec's spare capacity, then mem::forget, which breaks Vec's allocation contract. Every http_wire decode error (including malformed requests or more than 128 headers) is treated as 'incomplete', so the connection hangs and grows its buffer 4 KiB per read. The compio runtime's commit is titled 'vibe coded'.
- Build drift: the benchmarked build (table last updated 2026-04-25) had neither the current release profile (opt-level 3, fat LTO, 2026-09-12) nor the pinning of every worker to a core (pin_worker, added 2026-09-16). .cargo/config.yaml (target-cpu=native plus LLVM inlining flags) is inert: Cargo reads only config.toml, and the file is cut off mid-array.

## Known shortcomings

- No CPU, load generator or nginx config; README prose disagrees with the table (compio, monoio); the table dated 2026-04-25 predates the current release profile; the io_uring rows send a pre-encoded response once per connection; a benchmark stub, not a general server.
- Cross-run baseline: the nginx, HAProxy, Go, Axum and actix-web rows are unchanged since the table first appeared on 2025-12-31 (commit 5e044f0) while the statico rows were re-measured by 2026-03-28; in the original same-run table standard statico was 279,842 vs nginx 286,960 req/s at 1 thread (nginx 2.5% faster) and 966,248 vs 832,082 at 4 threads (1.16x), so the 'about 40% faster single-threaded' claim rests on a cross-run comparison. No CPU, load generator, nginx configuration or build is published; the README's key observations disagree with its own table.

## Caveats and trade-offs

First-party; no CPU model, load generator (or whether it pipelines requests), nginx configuration or nginx build is published, so tier C. The table was last updated 2026-04-25, before the current release profile (2026-09-12) and the removal of the tokio-local runtime (2026-08-20). The README's key observations disagree with its own table: they list tokio-uring leading at 1.39M, monoio 1.36M and compio 1.27M at four threads, while the table gives monoio 1,436,420, compio 1,395,047 and tokio-uring 1,393,573, so the prose and table come from different runs. The io_uring runtimes write a response pre-encoded once per connection (src/response.rs build_response; any Date header frozen at connection start), while nginx builds its headers per request, so the io_uring rows do less work per response. statico is a benchmarking stub that returns one configured response, not a general web server. Actix-web (798,809) is slower than nginx (832,082) at four threads in the same table, and the README does not say whether nginx used tuned worker settings. src/monoio.rs builds a Vec with Vec::from_raw_parts pointing into the middle of another Vec's allocation (forgotten after the read), an unsound pattern. [retier] First-party; no CPU model, load generator, nginx configuration or nginx build is published. Cross-run baseline: the nginx, HAProxy, Go, Axum and actix-web rows are unchanged since the table first appeared on 2025-12-31 (commit 5e044f0) while the statico rows were re-measured by 2026-03-28, so the 'about 40% faster single-threaded' claim compares different runs; the only same-run table had nginx 2.5% faster at 1 thread and statico 1.16x at 4 threads. The table (2026-04-25) predates the current release profile (2026-09-12) and the removal of the tokio-local runtime (2026-08-20), and the README's key observations disagree with its own table.

Designed strictly for benchmarking: returns a fixed response from memory, no routing, no logging; Linux-only io_uring runtimes.

## Maintenance

Active single-maintainer project (v0.18.0, last commit 2026-09-16, 1 star, 0 forks, MIT OR Apache-2.0) and a usable, copyable benchmarking and mocking stub, but its nginx speedup is a cross-run comparison against baseline rows carried over from December 2025 and should not be relied on.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now D.
- **Tier reason:** First-party README table and pic/benchmark.png compare statico with nginx's 'return'; no benchmark script, load generator, nginx configuration or CPU model is published, so C.
- **Retiered** C to D: Enricher: the nginx, HAProxy, Go, Axum and actix-web rows date from the table's first version (2025-12-31) while the statico rows were re-measured by 2026-03-28, so the headline is a cross-run comparison; in the only same-run table nginx was 2.5% faster at 1 thread and statico 1.16x at 4 threads. Cross-run precedent (PostgreSQL, MySQL, ODB): C to D.
- **Verifier notes:** Numbers match the README table and chart (399,025/1,071,433 tokio and 656,517/1,436,420 monoio vs nginx 286,960/832,082; ratios 1.39x/1.29x and 2.29x/1.73x derived). Set same_algorithm false because the io_uring rows send a once-per-connection pre-encoded response while nginx builds headers per request; standard tokio statico uses Hyper per request. Shortcomings to record: no hardware, load generator or nginx config; prose vs table mismatch; numbers predate current release profile. Metadata checked: MIT OR Apache-2.0, 1 star, 0 forks, not a fork, last commit 2026-09-16 (active), crates.io 872 downloads, version 0.18.0.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`, `claimed_speedup`
- **Shortcomings recorded by:** verifier batch-20 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/awgn/statico/HEAD/README.md>
  - <https://raw.githubusercontent.com/awgn/statico/HEAD/pic/benchmark.png>
  - <https://raw.githubusercontent.com/awgn/statico/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/awgn/statico/HEAD/src/monoio.rs>
  - <https://raw.githubusercontent.com/awgn/statico/HEAD/src/http.rs>
  - <https://raw.githubusercontent.com/awgn/statico/HEAD/src/response.rs>
  - <https://github.com/awgn/statico>
  - <https://github.com/awgn/statico/commits>
  - <https://github.com/awgn/statico/commits/main/README.md>
  - <https://github.com/awgn/statico/tree/main/src>
  - <https://crates.io/api/v1/crates/statico>
- **Sources the enricher read:**
  - <https://github.com/awgn/statico>
  - <https://github.com/awgn/statico/commits/main>
  - <https://github.com/awgn/statico/commits/main/src/main.rs>
  - <https://github.com/awgn/statico/commits/main/.cargo/config.yaml>
  - <https://github.com/awgn/statico/tree/main/.cargo>
  - <https://github.com/awgn/statico/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/awgn/statico/HEAD/README.md>
  - <https://raw.githubusercontent.com/awgn/statico/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/awgn/statico/HEAD/.cargo/config.yaml>
  - <https://raw.githubusercontent.com/awgn/statico/HEAD/cert.pem>
  - <https://raw.githubusercontent.com/awgn/statico/HEAD/src/main.rs>
  - <https://raw.githubusercontent.com/awgn/statico/HEAD/src/monoio.rs>
  - <https://raw.githubusercontent.com/awgn/statico/HEAD/src/tokio.rs>
  - <https://raw.githubusercontent.com/awgn/statico/HEAD/src/tokio_uring.rs>
  - <https://raw.githubusercontent.com/awgn/statico/HEAD/src/glommio.rs>
  - <https://raw.githubusercontent.com/awgn/statico/HEAD/src/compio.rs>
  - <https://raw.githubusercontent.com/awgn/statico/HEAD/src/smol.rs>
  - <https://raw.githubusercontent.com/awgn/statico/HEAD/src/options.rs>
  - <https://raw.githubusercontent.com/awgn/statico/HEAD/src/uring.rs>
  - <https://raw.githubusercontent.com/awgn/statico/HEAD/src/http.rs>
  - <https://raw.githubusercontent.com/awgn/statico/HEAD/src/response.rs>
  - <https://raw.githubusercontent.com/awgn/statico/5e044f0/README.md>
  - <https://raw.githubusercontent.com/awgn/statico/61081cb/README.md>
  - <https://raw.githubusercontent.com/awgn/statico/ae2a209/README.md>
  - <https://raw.githubusercontent.com/awgn/statico/20b7c6a/README.md>
  - <https://raw.githubusercontent.com/awgn/statico/d5e42df/README.md>
  - <https://raw.githubusercontent.com/awgn/statico/d994f10/README.md>
  - <https://raw.githubusercontent.com/awgn/statico/9c003cb/README.md>
  - <https://raw.githubusercontent.com/awgn/statico/ed6189e/README.md>
  - <https://raw.githubusercontent.com/awgn/statico/7551cb0/src/main.rs>
  - <https://raw.githubusercontent.com/awgn/statico/ab20db3/src/main.rs>
  - <https://raw.githubusercontent.com/awgn/statico/e5d4d08/src/main.rs>
  - <https://raw.githubusercontent.com/awgn/statico/81e21cc/src/main.rs>
  - <https://crates.io/api/v1/crates/statico>
  - <https://crates.io/api/v1/crates/http_wire>
  - <https://raw.githubusercontent.com/awgn/http_wire/HEAD/README.md>
  - <https://raw.githubusercontent.com/awgn/http_wire/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/awgn/http_wire/HEAD/src/response.rs>
  - WebSearch: "statico" rust http server static responses benchmark nginx awgn (snippets of docs.rs/crate/statico 0.3.x-0.9.x README pages)
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/awgn/statico`) · [data/wave14/enrich/raw/github_com_awgn_statico.json](../../../data/wave14/enrich/raw/github_com_awgn_statico.json) (enrichment confidence 0.75)

</details>
