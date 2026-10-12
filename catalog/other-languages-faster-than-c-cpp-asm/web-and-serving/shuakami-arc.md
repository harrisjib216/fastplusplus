# Arc (Arc Gateway)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Web and serving](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0` · 🟢 active

> Young Rust io_uring reverse proxy claiming 2.05-2.30x nginx's HTTP/1.1 proxy throughput on a 2-vCPU WSL2 box.

| | |
|---|---|
| **Beats** | nginx (C) as an HTTP/1.1 and HTTP/2 reverse proxy; version, build and the configuration behind the README table are not stated (the repo's benchmark script uses worker_processes auto and upstream keepalive 1024) |
| **Claimed result** | README Performance table: HTTP/1.1 proxy c=256 102,203 RPS vs nginx 49,930 RPS (2.05x); c=512 96,143 vs 41,740 RPS (2.30x); HTTP/2 high concurrency 100% success vs 91.5% for nginx; proxy latency overhead +0.82 ms vs +1.35 ms (39% lower). |
| **Workload** | Reverse-proxy throughput measured with wrk at 256 and 512 concurrent connections on WSL2 Debian with 2 vCPU, plus an HTTP/2 high-concurrency success rate and the proxy latency overhead. |
| **Metric** | throughput |
| **Hardware** | WSL2 Debian, 2 vCPU (CPU model not stated) |
| **Compiler and flags** | Arc built with cargo build --release -p arc-gateway (docs/benchmarks/index.mdx); Cargo.toml release profile opt-level 3, lto fat, codegen-units 1, panic abort; nginx build and flags not stated; wrk and h2load used as load generators |
| **Kind** | library or program |
| **Same algorithm as the baseline** | not stated |
| **Same optimization level** | not stated |
| **Why it wins** | The README attributes it to a thread-per-core architecture on Linux io_uring with lock-free algorithms; no profile or ablation is given. |
| **Adoption** | 8 stars |
| **Last commit** | 2026-03-11 |
| **Links** | [repository](https://github.com/shuakami/Arc) · [benchmark](https://github.com/shuakami/Arc) |

## Verdict

First-party README table on a WSL2 Debian VM with 2 vCPU: HTTP/1.1 proxy 102,203 vs 49,930 RPS at 256 connections (2.05x) and 96,143 vs 41,740 RPS at 512 (2.30x), HTTP/2 success 100% vs 91.5%, and added latency +0.82 ms vs +1.35 ms over a 1.18 ms direct path. Per the deleted methodology page, the backend was a static 64-byte nginx and wrk -t4 shared the host. CPU model, nginx version and build, nginx config and raw outputs are not published, and the shipped benchmark script uses a different backend and settings.

## Use it when

- Experimenting with an io_uring, thread-per-core Rust proxy on Linux 6.1+ where small-response HTTP/1.1 proxy throughput per core is the main goal and you can run your own wrk comparison against your nginx config.
- Lab or edge setups that want gateway features (GCRA rate limiting, WASM request plugins, traffic mirroring, XDP SYN-flood filtering) in one Rust binary rather than nginx plus modules.
- Reading a compact, single-author example of io_uring fixed buffers, multishot accept and per-worker upstream pools in Rust.

## Skip it when

- Production traffic: 11 commits between 2026-03-01 and 2026-03-11, 8 stars, releases v0.1.1 and v0.1.2, and the README itself says the project is 'in active testing'; fixes for self-upstream loops, HEAD handling and async upstream I/O landed after the benchmark numbers were published.
- TLS-heavy serving: the deleted benchmark page measured TLS 1.3 keepalive traffic at about 207 RPS for Arc against about 227 RPS for nginx (0.91x), a row the README leaves out.
- macOS, Windows without WSL2, or Linux kernels older than 5.10: the data plane needs io_uring.
- Anything that depends on nginx configuration, modules, caching or static file serving; Arc has its own config schema and feature set.
- Decisions based on the README numbers alone: they are first-party, from a 2-vCPU WSL2 VM with load generator, proxy and backend sharing the cores, and no raw runs are published.

## How it is fast

Thread-per-core workers each own an io_uring ring (custom bindings in arc-net), a registered fixed-buffer pool and a connection slab, with multishot accept and optional SQPOLL, so the hot path batches socket I/O into few kernel transitions and avoids cross-thread locks. HTTP/1.1 heads are parsed in place in the fixed buffers and responses are forwarded from the same buffer, and upstream connections are pooled per worker. The project gives no profile or ablation showing which of these produces the reported gap over nginx's epoll workers.

## Compared with alternatives

The catalogued siblings (tokio-uring, vanilla, zix, zeemo, libxev and others in HttpArena) are origin HTTP servers measured on a shared multi-core harness with published configs, whereas Arc is a reverse proxy/gateway measured only by its author. Pick Arc only when you specifically need an io_uring proxy with gateway features in front of other servers, and plan to benchmark it yourself.

## Integration

| | |
|---|---|
| **Form** | standalone binary (Rust workspace, crate arc-gateway; prebuilt Linux x86_64 and arm64 release assets via install.sh) |
| **Dependencies** | Linux io_uring (kernel 5.10+, 6.1+ recommended); crates rustls/tokio-rustls, hyper, tokio, serde_json/toml/serde_yaml, arc-swap, Wasmtime (plugins); Redis 6+ optional for global rate limiting; XDP needs eBPF support |
| **Minimum toolchain** | not documented (CI builds with stable Rust; workspace crates use edition 2021) |
| **Platforms** | Linux x86_64 and arm64 only (WSL2 works); no macOS |
| **Thread safety** | Not applicable (server process); each worker thread owns its ring, buffers and connection slab, and config hot reload swaps an ArcSwap snapshot |
| **Drop-in for the baseline** | partial — same reverse-proxy role as nginx proxy_pass, but a different configuration format and no nginx module, cache or static-file ecosystem |

## Gotchas

- Benchmark harness: the README table comes from docs/benchmarks.md, deleted in commit ce78a49 (2026-03-02). That page used an nginx static 64-byte backend, wrk -t4 on the same 2-vCPU host and 'the same number of worker processes/threads', and Arc ran with routing, a high rate limit and a no-op plugin. The shipped script (benchmark/scripts/run_h1_wrk_vs_nginx.sh) differs: a Python HTTP/1.0 backend that closes every upstream connection, wrk -t8, ARC_WORKERS=1 against nginx worker_processes auto, and a zero-error gate that checks only non-2xx responses, not wrk socket errors. The deleted page also had rows the README omits: HTTP/2 multiplexing 7,200 vs 6,984 RPS (1.03x) and TLS about 207 vs 227 RPS (0.91x). Its HTTP/2 success-rate row (100% vs 91.5%) was at 32 clients and 10 streams, while the current H2 script defaults to 64 and 20. The Arc RPS figures are identical in its nginx and Pingora tables, so one Arc run was reused against both baselines.
- Upstream keep-alive handling (from reading the code, no failure was measured): when an upstream response is not keep-alive, for example an HTTP/1.0 reply without 'Connection: keep-alive' like the bundled Python backend's, worker.rs injects 'Connection: keep-alive' into the client response and sets resp_keepalive. That same flag drives should_checkin_upstream_keepalive, so a socket the upstream is about to close goes back into the idle pool. Only an EPOLLRDHUP watcher drained before checkout evicts it, and the code comment calls that a way 'to reduce stale-conn reuse window'.
- Documentation and code disagree: the README Quick Start arc.yaml (node/listeners/discovery schema, 'plugins: {}') does not match arc-config's ConfigFile, which requires top-level listen, admin_listen, workers, io_uring, buffers, timeouts_ms, upstreams, a plugins list and routes. That file would fail to load, so use the arc.example.json schema. docs/benchmarks/index.mdx also documents a PAYLOAD_BYTES variable and random ports, but the script hard-codes --payload-bytes 2 and fixed ports.
- Most of the data plane is one 11,675-line worker.rs with 64 unsafe blocks over raw io_uring bindings and manual buffer copies (for example the header injection above). The docs site arc.sdjz.wiki did not resolve, so the in-repo docs are the only reference.

## Known shortcomings

- First-party README numbers only with no CPU, nginx version or config and no raw results; the shipped script uses an HTTP/1.0 Python backend that cannot reach 100k RPS, so the setup behind the README is unknown; arc.sdjz.wiki unreachable.
- The source of the README numbers is docs/benchmarks.md, deleted in ce78a49 (2026-03-02) and read at 9ddfb32: nginx 64-byte static backend, wrk -t4, same 2-vCPU host; the same page had rows the README omits (TLS Arc about 207 vs nginx about 227 RPS, 0.91x; HTTP/2 multiplex 1.03x), and the Arc RPS was reused unchanged in the Pingora table. The shipped script differs (Python HTTP/1.0 backend, wrk -t8, ARC_WORKERS=1, a zero-error gate that ignores socket errors). Keep-alive flaw by code reading: worker.rs injects Connection: keep-alive and returns the upstream socket to the pool although the upstream said close, with only the EPOLLRDHUP watcher evicting it. The README quick-start arc.yaml fails ConfigFile (missing listen). Numbers predate fixes 8c81ffb and 60f1aa9.

## Caveats and trade-offs

First-party numbers; the README table gives no nginx version or configuration, no CPU model and no tool flags. The repo ships a reproducible benchmark workflow (benchmark/scripts/run_h1_wrk_vs_nginx.sh, which writes the nginx.conf it uses and records versions in env.txt) but benchmark/results holds only .gitkeep, so no raw runs are published. In that script the backend is benchmark/backends/http_ok_backend.py, a Python ThreadingHTTPServer returning 2 bytes with the default HTTP/1.0 protocol_version, so it closes every upstream connection and neither proxy's upstream keepalive 1024 can take effect; Arc runs with ARC_WORKERS=1 by default while nginx uses worker_processes auto, and wrk runs on the same 2 vCPU host as the servers. A Python backend of that kind is unlikely to sustain the 50k to 100k RPS in the table, so the backend and settings behind the README numbers are probably different and are not stated. The HTTP/2 row compares success rates, not speed. The docs site arc.sdjz.wiki did not resolve (ENOTFOUND); docs/benchmarks/index.mdx in the repo holds methodology only, no results. Tier C: first-party with partial methodology. [retier] The README numbers come from docs/benchmarks.md (deleted in ce78a49, readable at 9ddfb32): nginx 64-byte static backend, wrk -t4, same 2-vCPU host; that page also had rows the README omits (TLS Arc about 207 vs nginx about 227 RPS, 0.91x; HTTP/2 multiplex 1.03x), and the Arc RPS was reused unchanged in the Pingora table. The shipped script differs (Python HTTP/1.0 backend, wrk -t8, ARC_WORKERS=1, a zero-error gate that ignores socket errors). worker.rs injects Connection: keep-alive and pools upstream sockets the upstream asked to close. Numbers predate fixes 8c81ffb and 60f1aa9.

Linux io_uring only (the docs recommend kernel 6.1 or newer; no macOS); very young project (11 commits at the time of reading) that the README marks as in active testing; thread-per-core design; feature set (rate limiting, XDP/eBPF DDoS protection) goes beyond a plain proxy.

## Maintenance

Apache-2.0 and buildable, but an 11-commit, 8-star project last committed 2026-03-11 (two v0.1.x releases), so treat it as experimental rather than an nginx replacement.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README table (102,203 vs 49,930 RPS at c=256; 96,143 vs 41,740 at c=512; 100% vs 91.5% HTTP/2 success; +0.82 vs +1.35 ms) with no CPU model, nginx version or config; the repo's benchmark scripts are public but no raw results are published and the shipped backend cannot have produced these numbers.
- **Verifier notes:** README numbers match the record; license Apache-2.0, 8 stars, 11 commits, last commit 2026-03-11 (active) confirmed. Shortcomings: first-party only, no CPU model or nginx version/config, no raw results, published benchmark script uses an HTTP/1.0 Python backend that cannot explain 100k RPS so the README setup is undocumented, HTTP/2 row is a success rate not throughput.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-95 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/shuakami/Arc>
  - <https://github.com/shuakami/Arc/commits>
  - <https://raw.githubusercontent.com/shuakami/Arc/HEAD/README.md>
  - <https://raw.githubusercontent.com/shuakami/Arc/HEAD/benchmark/README.md>
  - <https://raw.githubusercontent.com/shuakami/Arc/HEAD/benchmark/scripts/run_h1_wrk_vs_nginx.sh>
  - <https://raw.githubusercontent.com/shuakami/Arc/HEAD/benchmark/backends/http_ok_backend.py>
  - <https://raw.githubusercontent.com/shuakami/Arc/HEAD/benchmark/results/.gitkeep>
  - <https://raw.githubusercontent.com/shuakami/Arc/HEAD/docs/benchmarks/index.mdx>
  - <https://raw.githubusercontent.com/shuakami/Arc/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/shuakami/Arc/HEAD/.cargo/config.toml>
- **Sources the enricher read:**
  - <https://github.com/shuakami/Arc>
  - <https://github.com/shuakami/Arc/commits/master>
  - <https://github.com/shuakami/Arc/releases>
  - <https://github.com/shuakami/Arc/tree/master/crates/arc-gateway/src>
  - <https://github.com/shuakami/Arc/commit/ce78a49>
  - <https://raw.githubusercontent.com/shuakami/Arc/HEAD/README.md>
  - <https://raw.githubusercontent.com/shuakami/Arc/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/shuakami/Arc/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/shuakami/Arc/HEAD/.cargo/config.toml>
  - <https://raw.githubusercontent.com/shuakami/Arc/HEAD/arc.example.json>
  - <https://raw.githubusercontent.com/shuakami/Arc/HEAD/arc.yaml>
  - <https://raw.githubusercontent.com/shuakami/Arc/HEAD/install.sh>
  - <https://raw.githubusercontent.com/shuakami/Arc/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/shuakami/Arc/HEAD/.github/workflows/ci.yml>
  - <https://raw.githubusercontent.com/shuakami/Arc/HEAD/benchmark/README.md>
  - <https://raw.githubusercontent.com/shuakami/Arc/HEAD/benchmark/scripts/run_h1_wrk_vs_nginx.sh>
  - <https://raw.githubusercontent.com/shuakami/Arc/HEAD/benchmark/scripts/run_h2_h2load_vs_nginx.sh>
  - <https://raw.githubusercontent.com/shuakami/Arc/HEAD/benchmark/scripts/parse_wrk.py>
  - <https://raw.githubusercontent.com/shuakami/Arc/HEAD/benchmark/backends/http_ok_backend.py>
  - <https://raw.githubusercontent.com/shuakami/Arc/HEAD/docs/benchmarks/index.mdx>
  - <https://raw.githubusercontent.com/shuakami/Arc/HEAD/crates/arc-gateway/Cargo.toml>
  - <https://raw.githubusercontent.com/shuakami/Arc/HEAD/crates/arc-gateway/src/main.rs>
  - <https://raw.githubusercontent.com/shuakami/Arc/HEAD/crates/arc-gateway/src/worker.rs>
  - <https://raw.githubusercontent.com/shuakami/Arc/HEAD/crates/arc-config/src/lib.rs>
  - <https://raw.githubusercontent.com/shuakami/Arc/HEAD/crates/arc-proto-http1/src/lib.rs>
  - <https://raw.githubusercontent.com/shuakami/Arc/9ddfb3236d8afc3185279536e697c51112632e46/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/shuakami/Arc/9ddfb3236d8afc3185279536e697c51112632e46/docs/benchmarks.md>
  - <https://raw.githubusercontent.com/python/cpython/main/Lib/http/server.py>
  - <https://raw.githubusercontent.com/python/cpython/main/Lib/socketserver.py>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/shuakami/arc`) · [data/wave14/enrich/raw/github_com_shuakami_arc.json](../../../data/wave14/enrich/raw/github_com_shuakami_arc.json) (enrichment confidence 0.72)

</details>
