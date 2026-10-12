# cblt

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Web and serving](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Rust` · `MIT` · 🟡 stale

> Small Rust (tokio) static file server and reverse proxy whose '10x faster than nginx' small-file claim does not survive a harness check.

| | |
|---|---|
| **Beats** | nginx (Docker image nginx:latest per benchmark/nginx/Dockerfile) |
| **Claimed result** | README percentile table for 'ab -c 1000 -n 3000 http://127.0.0.1/logo.png' (23,911-byte file; ab reports ms): 50%: 179 vs nginx 1209 (6.75x lower, derived from page data); 75%: 194 vs 1655 (8.53x); 100%: 200 vs 2146 (10.73x). Feature list: '10 times faster than Nginx for small content under 100KB'. The table was added on 10 Nov 2024 (commit 3fb9fa5, version 0.1.5) and replaced an earlier 5 MB test (ab -c 100 -n 300, logo_huge.png) whose medians were cblt 1956 ms, nginx 1941 ms, Caddy 1768 ms. |
| **Workload** | Apache Benchmark, 3000 requests at 1000 concurrent connections, downloading a 23 KB logo.png from 127.0.0.1; response-time percentiles. |
| **Metric** | latency |
| **Hardware** | Not stated for the 23 KB table; the earlier README revision with the 5 MB test shows the runs were made from a Windows MINGW64 shell on a Lenovo machine with Docker containers. |
| **Compiler and flags** | Cargo release profile with lto = true (opt-level 3 by default); benchmark/cblt/Dockerfile runs the Docker image ievkz/cblt:0.1.2 (Alpine, cargo build --release) and overwrites its config with a Cbltfile for host 'example.com'; nginx is the nginx:latest Docker image with its default configuration; both run in Docker. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | not stated |
| **Adoption** | 71 stars; crates.io about 28,900 downloads |
| **Last commit** | 2025-06-04 |
| **Links** | [repository](https://github.com/evgenyigumnov/cblt) · [benchmark](https://github.com/evgenyigumnov/cblt/blob/main/README.md) |

## Verdict

The author ran 'ab -c 1000 -n 3000 http://127.0.0.1/logo.png' (23,911-byte PNG) against cblt 0.1.x and the default nginx:latest Docker image, both in Docker on a Windows laptop (the earlier run's MINGW64 'lenovo' shell; CPU not stated), and reported p50/p75/p100 of 179/194/200 ms versus 1209/1655/2146 ms, with no raw output or status counts. The same author's earlier 5 MB run, with full ab output in article-en.md, had cblt at 1956 ms median against nginx 1.27.2 at 1941 ms and Caddy at 1768 ms, so no verified win exists.

## Use it when

- A hobby or internal deployment that wants one small Rust binary with a readable KDL config for a few static sites plus a reverse proxy.
- Docker Swarm setups where backends announce host, path, port and load-balancing policy through service labels and a tiny label-driven proxy is enough.
- Serving downloads to non-browser clients (curl, scripts) that need range requests and send no Accept-Encoding header.
- Reading a compact (\~2k lines) tokio HTTP/1.1 server as a learning reference.

## Skip it when

- Browser-facing static sites: browsers send Accept-Encoding: gzip, which triggers an undeclared gzip body with the wrong Content-Length (see gotchas).
- Internet-facing servers: no read or idle timeouts, unbounded header and body buffering, and a 10,000-permit connection semaphore make slowloris-style exhaustion easy.
- High request-rate small-file serving where keep-alive, HTTP/2, sendfile or caching matter; every request opens and closes its own TCP connection.
- Several TLS domains on one port: there is no SNI certificate selection, the last host's cert/key on a port wins.
- Anything needing an active upstream: last commit 2025-06-04, crate 0.6.2 from December 2024, 8 open issues.

## How it is fast

Nothing structurally faster than nginx: a tokio multi-thread runtime with one worker per CPU, httparse request parsing, one request per connection then close, and file bodies streamed with tokio::io::copy from tokio::fs::File (thread-pool reads, no sendfile). The README gap is best explained by the listen backlog: tokio's TcpListener::bind goes through mio, which calls listen(fd, 1024), while nginx's Linux default is NGX_LISTEN_BACKLOG 511; with 'ab -c 1000' nginx's accept queue overflows and the dropped connections wait for the 1 s TCP SYN retransmit, which matches nginx's \~1.2 s median against cblt's 200 ms maximum (inferred from source, not reproduced). With 'listen 80 backlog=1024' in nginx the comparison would likely change.

## Compared with alternatives

Only when a tiny Rust proxy driven by Docker Swarm labels is the point; for measured static or proxy throughput, statico, kawipiko or routez publish their harnesses, and for a full-featured server Caddy (Go) or Ferron (Rust) are maintained alternatives.

## Integration

| | |
|---|---|
| **Form** | binary crate (cargo install cblt) or Docker image ievkz/cblt |
| **Dependencies** | tokio (full), httparse, http, bytes, kdl 4.6, rustls 0.23 + tokio-rustls, async-compression (gzip), bollard (Docker API), clap, fdlimit, mime_guess, env_logger/tracing |
| **Minimum toolchain** | Rust 2021 edition; no rust-version declared in Cargo.toml or on crates.io |
| **Platforms** | any tokio target; Docker label mode needs the Docker socket; README and Dockerfile target Linux/Alpine |
| **Thread safety** | not applicable (standalone server); config swaps go through a tokio RwLock&lt;Arc&lt;ServerSettings&gt;&gt; per port |
| **Drop-in for the baseline** | false: different config language, HTTP/1.1 only, no keep-alive, and no equivalents for most nginx directives |

## Gotchas

- Correctness bug at HEAD (src/response.rs send_response_file, unchanged since the 'Gzip (#3)' commit e5861b5 on 10 Nov 2024): when the request's Accept-Encoding contains 'gzip' the file body is gzip-compressed but the 'Content-Encoding: gzip' header write is commented out and Content-Length stays the uncompressed file size, so browsers get an undeclared gzip stream with a mismatched length (already-compressed PNG/JPEG are gzipped too). ab sends no Accept-Encoding, so the benchmark never exercised this path.
- Harness flaw behind the README table: tokio/mio bind with backlog 1024 versus nginx's Linux default of 511, under 'ab -c 1000', so nginx's \~1.2 s median looks like accept-queue overflow plus the 1 s SYN retransmit rather than serving cost; in addition the repo's benchmark/cblt Cbltfile defines only host 'example.com', and cblt answers a Host '127.0.0.1' request with a 9-byte 403 when no '\*' host exists, and no raw ab output (Document Length, Non-2xx) was published to rule that out.
- Host routing: without a '\*' host, the raw Host header (including any ':port') must equal a configured key exactly, else 403; build_servers stores the first host on a port without its port suffix and later ones with it, so the first named host on a non-default port never matches a client's 'host:port' Host header and gets 403. With a '\*' host present, it captures every request on that port.
- No timeouts and unbounded buffering: socket_to_request grows its BytesMut until headers parse and the body is read fully up to Content-Length; a suffix range 'bytes=-N' with N above the file size underflows a u64 (wraps in release) and returns Content-Length N with no body; every request is logged at info level.

## Known shortcomings

- Crippled baseline: the repo's own benchmark/cblt Cbltfile serves host 'example.com' only, so cblt 0.1.x answers 403 to the tested http://127.0.0.1/logo.png; README gives no ab byte or non-2xx counts and never says which config ran; the same-week 5 MB test that showed parity with nginx (1956 vs 1941 ms) was removed.
- Harness flaw (inferred from source, not run): tokio/mio listens with backlog 1024 while nginx's Linux default is 511 (NGX_LISTEN_BACKLOG), so at ab -c 1000 nginx's accept queue overflows and its about 1.2 s median fits the 1 s SYN retransmit, not serving cost; the benchmark Cbltfile would also answer 403 for Host 127.0.0.1. Correctness bug at HEAD: src/response.rs gzips the file when Accept-Encoding has gzip, but its Content-Encoding header line has been commented out since e5861b5 (2024-11-10) and Content-Length stays the uncompressed size, so browsers get broken bodies. No timeouts, unbounded buffering, host:port matching 403. An older 5 MB run in article-en.md shows parity with nginx.

## Caveats and trade-offs

Single first-party run of one 23 KB file with no raw ab output, so it cannot be checked that cblt actually returned the file: the repo's benchmark/cblt/Cbltfile (last changed in PR #4 'Highload', merged the same day the table appeared) defines only host 'example.com', and cblt 0.1.x returns 403 Forbidden when no '\*' host exists and the Host header (here 127.0.0.1) does not match; only the root Cbltfile ('\*:80', ./assets) would have served logo.png, and the README does not say which was used. The previous README benchmark (5 MB file, same week) showed cblt at parity with nginx (median 1956 vs 1941 ms) and slower than Caddy, and was removed rather than kept beside the new table. Medians above one second for nginx at 1000 concurrent connections for 3000 requests suggest connection queueing (listen-backlog overflow and SYN retransmission are a plausible cause, not verified) rather than per-request serving cost. Hardware, OS, Docker networking mode and the nginx config are not stated; the '10x faster for content under 100KB' headline rests on this one file. The benchmarked build was cblt 0.1.x (November 2024); the current crate is 0.6.2 (December 2024) and the last commit is June 2025. [retier] Harness flaw (inferred from source): tokio/mio listens with backlog 1024 while nginx's Linux default is 511, so at ab -c 1000 nginx's accept queue overflows and its about 1.2 s median fits the 1 s SYN retransmit rather than serving cost. Correctness bug at HEAD: when Accept-Encoding has gzip the file body is gzip-compressed but the Content-Encoding header line has been commented out since e5861b5 (2024-11-10) and Content-Length stays the uncompressed size. No timeouts, unbounded buffering. An older 5 MB run in article-en.md shows parity with nginx.

Minimal file server and reverse proxy with load balancing, Docker label integration and TLS; far fewer features than nginx.

## Maintenance

Stale since June 2025 (crate 0.6.2, December 2024), MIT-licensed hobby project that article-en.md describes as a Rust learning exercise; fine to read or run internally, but not a browser-facing nginx replacement until the gzip header bug is fixed.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification C, tier now D.
- **Tier reason:** The README table (179/194/200 vs 1209/1655/2146 ms) is first-party with no raw ab output (no Document Length, Failed or Non-2xx counts), and the repo's own benchmark/cblt setup (ievkz/cblt:0.1.2 with a Cbltfile for host 'example.com' only) would answer the documented 'ab ... http://127.0.0.1/logo.png' with 403 Forbidden under the 0.1.x host-matching code, so no valid measurement can be confirmed; the same week's earlier 5 MB run had cblt no faster than nginx.
- **Verifier notes:** Downgraded C to D: no valid measurement can be confirmed (published harness config would serve 403 for the tested URL; no ab byte or non-2xx counts), and an earlier same-week test showed no win; not rejected because the 403 path is not proven (the root '\*:80' config would have served the file). Shortcomings to record: possible 403 fast path, replaced parity result, single file, queueing-dominated latency at -c 1000, no hardware or nginx config, stale since June 2025. Metadata checked: MIT, 71 stars, 16 forks, crates.io 28,901 downloads, last commit 2025-06-04 (stale).
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** verifier batch-71 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/evgenyigumnov/cblt/blob/main/README.md>
  - <https://raw.githubusercontent.com/evgenyigumnov/cblt/HEAD/README.md>
  - <https://github.com/evgenyigumnov/cblt>
  - <https://github.com/evgenyigumnov/cblt/commits/main>
  - <https://github.com/evgenyigumnov/cblt/commits/main/README.md>
  - <https://github.com/evgenyigumnov/cblt/commits/main/benchmark/cblt/Cbltfile>
  - <https://github.com/evgenyigumnov/cblt/tree/main/benchmark>
  - <https://github.com/evgenyigumnov/cblt/tree/main/src>
  - <https://github.com/evgenyigumnov/cblt/pull/4>
  - <https://raw.githubusercontent.com/evgenyigumnov/cblt/HEAD/benchmark/ab.md>
  - <https://raw.githubusercontent.com/evgenyigumnov/cblt/HEAD/benchmark/nginx/Dockerfile>
  - <https://raw.githubusercontent.com/evgenyigumnov/cblt/HEAD/benchmark/cblt/Dockerfile>
  - <https://raw.githubusercontent.com/evgenyigumnov/cblt/HEAD/benchmark/cblt/Cbltfile>
  - <https://raw.githubusercontent.com/evgenyigumnov/cblt/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/evgenyigumnov/cblt/HEAD/src/server.rs>
  - <https://raw.githubusercontent.com/evgenyigumnov/cblt/HEAD/src/directive.rs>
  - <https://raw.githubusercontent.com/evgenyigumnov/cblt/HEAD/src/file_server.rs>
  - <https://raw.githubusercontent.com/evgenyigumnov/cblt/6a09e5a/README.md>
  - <https://raw.githubusercontent.com/evgenyigumnov/cblt/3fb9fa5/README.md>
  - <https://raw.githubusercontent.com/evgenyigumnov/cblt/3fb9fa5/src/main.rs>
  - <https://raw.githubusercontent.com/evgenyigumnov/cblt/3fb9fa5/Cbltfile>
  - <https://raw.githubusercontent.com/evgenyigumnov/cblt/3fb9fa5/Dockerfile>
  - <https://raw.githubusercontent.com/evgenyigumnov/cblt/fd8d67b/benchmark/cblt/Cbltfile>
  - <https://raw.githubusercontent.com/evgenyigumnov/cblt/fd8d67b/benchmark/cblt/Dockerfile>
  - <https://raw.githubusercontent.com/evgenyigumnov/cblt/7e21585/benchmark/cblt/Cbltfile>
  - <https://crates.io/api/v1/crates/cblt>
- **Sources the enricher read:**
  - <https://github.com/evgenyigumnov/cblt>
  - <https://raw.githubusercontent.com/evgenyigumnov/cblt/HEAD/README.md>
  - <https://raw.githubusercontent.com/evgenyigumnov/cblt/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/evgenyigumnov/cblt/HEAD/Cbltfile>
  - <https://raw.githubusercontent.com/evgenyigumnov/cblt/HEAD/Dockerfile>
  - <https://raw.githubusercontent.com/evgenyigumnov/cblt/HEAD/article-en.md>
  - <https://raw.githubusercontent.com/evgenyigumnov/cblt/HEAD/benchmark/ab.md>
  - <https://raw.githubusercontent.com/evgenyigumnov/cblt/HEAD/benchmark/cblt/Cbltfile>
  - <https://raw.githubusercontent.com/evgenyigumnov/cblt/HEAD/benchmark/cblt/Dockerfile>
  - <https://raw.githubusercontent.com/evgenyigumnov/cblt/HEAD/benchmark/nginx/Dockerfile>
  - <https://raw.githubusercontent.com/evgenyigumnov/cblt/HEAD/src/main.rs>
  - <https://raw.githubusercontent.com/evgenyigumnov/cblt/HEAD/src/server.rs>
  - <https://raw.githubusercontent.com/evgenyigumnov/cblt/HEAD/src/directive.rs>
  - <https://raw.githubusercontent.com/evgenyigumnov/cblt/HEAD/src/file_server.rs>
  - <https://raw.githubusercontent.com/evgenyigumnov/cblt/HEAD/src/request.rs>
  - <https://raw.githubusercontent.com/evgenyigumnov/cblt/HEAD/src/response.rs>
  - <https://raw.githubusercontent.com/evgenyigumnov/cblt/HEAD/src/reverse_proxy.rs>
  - <https://raw.githubusercontent.com/evgenyigumnov/cblt/e5861b5/src/response.rs>
  - <https://raw.githubusercontent.com/evgenyigumnov/cblt/824b8b8/src/response.rs>
  - <https://raw.githubusercontent.com/evgenyigumnov/cblt/3fb9fa5/src/response.rs>
  - <https://raw.githubusercontent.com/evgenyigumnov/cblt/dd34582/src/response.rs>
  - <https://raw.githubusercontent.com/evgenyigumnov/cblt/ce5f4a9/src/response.rs>
  - <https://raw.githubusercontent.com/evgenyigumnov/cblt/3fb9fa5/src/file_server.rs>
  - <https://raw.githubusercontent.com/evgenyigumnov/cblt/3fb9fa5/src/main.rs>
  - <https://github.com/evgenyigumnov/cblt/issues?q=is%3Aissue>
  - <https://github.com/evgenyigumnov/cblt/commits/main/src/response.rs>
  - <https://raw.githubusercontent.com/tokio-rs/mio/v1.0.2/src/net/tcp/listener.rs>
  - <https://raw.githubusercontent.com/tokio-rs/mio/v0.8.11/src/net/tcp/listener.rs>
  - <https://raw.githubusercontent.com/tokio-rs/mio/v1.0.2/src/sys/unix/tcp.rs>
  - <https://raw.githubusercontent.com/tokio-rs/tokio/tokio-1.41.0/tokio/src/net/tcp/listener.rs>
  - <https://raw.githubusercontent.com/nginx/nginx/master/src/os/unix/ngx_linux_config.h>
  - <https://raw.githubusercontent.com/nginx/nginx/master/src/os/unix/ngx_freebsd_config.h>
  - <https://crates.io/api/v1/crates/cblt>
  - WebSearch: cblt Rust web server nginx benchmark (snippets: lib.rs, habr.com/en/articles/857306; no independent benchmark found)
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/evgenyigumnov/cblt`) · [data/wave14/enrich/raw/github_com_evgenyigumnov_cblt.json](../../../data/wave14/enrich/raw/github_com_evgenyigumnov_cblt.json) (enrichment confidence 0.75)

</details>
