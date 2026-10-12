# rsloop

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [Event loops and async I/O](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `Apache-2.0` · 🟢 active

> Rust/PyO3 asyncio event loop on io_uring, IOCP or kqueue; beats uvloop on TLS, bulk and TCP round-trips, not plaintext WebSockets.

| | |
|---|---|
| **Beats** | uvloop (libuv-based asyncio event loop) |
| **Claimed result** | 5,000 TCP roundtrips (Sept 14 2026, rsloop 0.1.52): rsloop 83.30 ms vs uvloop 127.87 ms (\~1.53x, derived from page data); rsloop also edges uvloop on 200,000 callbacks (47.77 vs 52.67 ms) and 50,000 tasks (88.29 vs 92.85 ms), but zuvloop is fastest on those two. Sustained matrix (Sept 7 2026, rsloop 0.1.49, 16 connections): TLS HTTP 72,496 vs 26,226 ops/s (\~2.76x), bulk transfer 2,009.9 vs 1,264.9 MiB/s (\~1.59x), mixed streams 43,795 vs 34,196 (derived from page data); uvloop beats rsloop on plaintext `websockets` (25,800 vs 24,667), aiohttp WebSocket (32,765 vs 31,636), Starlette WebSocket (20,407 vs 18,785) and marginally raw WebSocket (4,890 vs 4,870), and zuvloop leads plaintext HTTP keep-alive. Idle activation first-reply median 17.221 ms vs uvloop 18.193 ms, but the page rates the paired p95 comparison (-23.5%, 95% interval [-48.6%, +5.9%]) as inconclusive. |
| **Workload** | asyncio-compatible event loop microbenchmarks (200K callbacks, 50K tasks, 5,000 TCP roundtrips) plus a sustained network workload matrix (HTTP keep-alive, TLS, WebSockets, bulk transfer) and idle-activation latency; rsloop vs stdlib asyncio, uvloop, and zuvloop |
| **Metric** | throughput, latency |
| **Hardware** | Intel Core i9-9900K, Linux 7.0.0-31-generic (x86_64) |
| **Compiler and flags** | rustc 1.98.1 (pinned in rust-toolchain.toml at bench commits 5d0a2bb/6cc3444); Cargo [profile.release] opt-level=3, lto="fat", codegen-units=1, incremental=false; built with `maturin develop --release`; CPython 3.14.7; uvloop 0.22.1; zuvloop 0.0.16 (microbenchmarks) / 0.0.14 (workload matrix) |
| **Adoption** | 203 stars |
| **Last commit** | 2026-09-15 |
| **Links** | [repository](https://github.com/RustedBytes/rsloop) · [benchmark](https://github.com/RustedBytes/rsloop/blob/master/docs/benchmarks.md) |

## Verdict

In the author's own harness (i9-9900K, Linux 7.0, CPython 3.14.7, release build with rustc 1.98.1 and fat LTO, uvloop 0.22.1, medians of 7 fresh-process runs), rsloop 0.1.52 did 5,000 sequential 1 KiB loopback round-trips in 83.3 ms vs 127.9 ms (1.53x), with rsloop on its native fast streams and uvloop on stdlib streams. A separate 16-connection sustained run of 0.1.49 gave 72,496 vs 26,226 ops/s on TLS HTTP (2.76x) and 2,010 vs 1,265 MiB/s on bulk transfer (1.59x), while uvloop won the plaintext WebSocket-library rows and the idle-wakeup latency gain was classed inconclusive.

## Use it when

- Asyncio services that terminate or originate TLS (aiohttp, websockets, Starlette/uvicorn): with 16 connections on the author's i9-9900K, TLS HTTP ran 72,496 vs 26,226 ops/s on uvloop, and websockets over TLS 26,781 vs 14,872, with lower p95.
- Bulk streaming over TCP (large bodies, proxies, file relays): 2,009.9 vs 1,264.9 MiB/s in 64 KiB chunks, with p95 15.1 ms vs 25.2 ms.
- Latency-bound request/response code built on `asyncio.open_connection`/`start_server` without TLS, where the native fast-stream reader applies: 5,000 sequential 1 KiB loopback round-trips took 83.3 ms vs 127.9 ms.
- Windows or macOS deployments that want a compiled asyncio loop: uvloop does not build on Windows, while rsloop ships win_amd64/win_arm64 and macOS 13+ wheels.
- Free-threaded CPython 3.14t with one loop per thread: the extension declares gil_used = false, so separate loops on separate threads run concurrently.

## Skip it when

- Code bound by callback or task scheduling: rsloop is only 1.10x/1.05x ahead of uvloop on 200,000 callbacks and 50,000 tasks (47.77 vs 52.67 ms, 88.29 vs 92.85 ms), and zuvloop beats it on both (36.77, 82.21 ms).
- Plaintext WebSocket or HTTP keep-alive servers: uvloop wins on websockets (25,800 vs 24,667), aiohttp WebSocket and Starlette WebSocket, zuvloop leads HTTP keep-alive, and rsloop's raw WebSocket p95 is the worst of the three (4.45 vs 3.87 ms). The author's March 2026 Show HN post (early version) likewise found uvloop 10-20% faster on a synthetic FastAPI run, with rsloop ahead only on p99.
- CPU-limited containers or busy hosts: the loop spins before parking and TLS I/O, add_reader/add_writer watches and parts of the write path use helper threads. The benchmark page warns that rsloop 'has more to lose when cores are contended'.
- TLS setups that need full OpenSSL SSLContext semantics: the rustls backend rejects encrypted private keys and sets an empty server ALPN list (so no h2 negotiation through its TLS server). On servers it treats CERT_OPTIONAL as no client auth (only CERT_REQUIRED verifies client certs), and a server context must call load_cert_chain() after rsloop is imported.
- Conservative or legacy environments: it is an Alpha-classified 0.1.x project, and patch releases have broken platforms. 0.1.34-0.1.45 refused kernels older than 6.1 and panicked where io_uring was unavailable (issue #75, fixed in 0.1.46), and Windows 10 broke until 0.1.49 (issue #76). Linux wheels are manylinux_2_39 only (glibc 2.39+, no musllinux), and subprocess preexec_fn is unsupported.

## How it is fast

Each loop runs a vendored single-threaded Rust runtime (vibeio): io_uring set up with SINGLE_ISSUER, COOP_TASKRUN and DEFER_TASKRUN on Linux (epoll via mio as fallback), IOCP on Windows, one-shot kqueue on macOS. On Unix a second runtime on the Python thread serves TCP protocol reads, so reads are not handed across threads. `call_soon` is a CPython FASTCALL descriptor that skips the argument tuple for zero or one argument, the ready queue drains in bounded batches, and before parking the loop busy-waits up to 50 us (reader workers 30 us) to catch ping-pong replies without a sleep/wake cycle. TLS is rustls on helper reader/writer threads instead of CPython's ssl module on the loop thread, which is the likely (undocumented) source of its TLS lead.

## Compared with alternatives

Choose rsloop over uvloop on Windows or when TLS, bulk transfer or stream round-trips dominate; stay on uvloop for plaintext WebSocket/HTTP servers, full OpenSSL SSLContext behaviour and a longer production record. Against uringcore, the other Rust asyncio loop, rsloop is the practical choice: it supports ssl= (uringcore raises NotImplementedError), ships wheels for three OSes and CPython 3.10-3.15, and is actively released.

## Integration

| | |
|---|---|
| **Form** | module (CPython extension wheel built from a Rust crate with PyO3/maturin). The crate is also on crates.io for Rust extensions that return asyncio awaitables, but only up to 0.1.44, while docs/rust-extensions.md asks for 0.1.52. |
| **Dependencies** | No Python runtime dependencies. Rust side (compiled into the wheel): pyo3 0.29, rustls 0.23 + rustls-native-certs, io-uring 0.7 (Linux), mio 1, socket2, crossbeam, async-std, tokio (io-util only), windows-sys, plus a vendored copy of the vibeio runtime. |
| **Minimum toolchain** | CPython 3.10-3.15 (3.14t free-threaded supported). Source builds need Rust 1.98.1 (pinned in rust-toolchain.toml, edition 2024) and maturin &gt;= 1.9.4. |
| **Platforms** | Linux x86-64/aarch64 (wheels need glibc 2.39+). The README says Linux 6.1+, but master probes io_uring and falls back to mio/epoll, and that fallback path is not benchmarked. macOS 13+ x86-64/arm64 (kqueue). Windows 10+ x64/arm64 (IOCP; no arm64 wheel for cp310 or 3.14t). Other Unixes are refused at runtime. |
| **Thread safety** | One loop per thread. A loop is single-threaded internally and asyncio objects are not thread-safe. call_soon_threadsafe() is the cross-thread entry point and keeps FIFO order. On 3.14t, separate loops on separate threads run in parallel. |
| **Drop-in for the baseline** | partial: same entry points as uvloop (install()/run()/new_event_loop()) and the standard AbstractEventLoop API, with integration scripts for FastAPI, Starlette, aiohttp, Sanic, Django ASGI, anyio, uvicorn, Granian and others. But importing it patches asyncio and ssl.SSLContext, TLS is rustls with narrower SSLContext support, datagram endpoints, sendfile and sock_recvfrom/sendto are Python-level shims over add_reader/sock_\* calls, and preexec_fn is unsupported. |

## Gotchas

- Import side effects: `import rsloop` patches asyncio.set_event_loop, and asyncio.open_connection/start_server (non-TLS streams then get a native PyFastStreamReader rather than asyncio.StreamReader). It also wraps ssl.SSLContext.load_cert_chain, load_verify_locations, load_default_certs and set_default_verify_paths. Set RSLOOP_USE_FAST_STREAMS=0 to keep stdlib streams.
- The headline TCP-roundtrip win depends on those patched fast streams. The benchmark's --no-rsloop-fast-streams flag gives the like-for-like run, but no result from it is published.
- Tunables are read from the environment once: RSLOOP_WAKE_SPIN_US (default 50, max 1000, 0 disables spinning), RSLOOP_READER_SPIN_US (30), RSLOOP_MAX_WRITE_BUFFER_BYTES (64 MiB) and RSLOOP_MAX_PENDING_TLS_HANDSHAKES (256). Inbound reads pause at 1 MiB buffered per connection and resume below 256 KiB.
- Runtime-initialisation failures have shown up as Rust panics ('failed to initialize loop-thread vibeio runtime') rather than Python exceptions (issues #75, #76). A loop that is never close()d leaks its runtime at thread exit. Client TLS handshakes are blocking and run in the default executor.

## Known shortcomings

- The TCP-roundtrip win uses rsloop's native fast streams while the other loops use stdlib streams; the author rates the idle-latency result inconclusive; uvloop-derivative zuvloop (not uvloop) beats it on callbacks and tasks.
- The 1.53x TCP round trip uses rsloop's native fast streams vs stdlib streams for the others (the same-streams run is unpublished), on one loopback connection in one process. Author-run benchmarks from two versions (0.1.52 small, 0.1.49 sustained) without core pinning; the only outside signal (author's March 2026 Show HN, early version) had uvloop 10-20% faster on FastAPI. Workload-dependent: loses to uvloop on plaintext websockets, aiohttp and Starlette WebSockets; zuvloop leads keep-alive; worst raw WebSocket p95. TLS runs in rustls on helper threads (likely cause of the 2.76x TLS lead, inference) and spins 50/30 us before parking, so it suffers under core contention. Narrower TLS: encrypted keys rejected, empty server ALPN (no h2), CERT_OPTIONAL treated as no client auth, client handshakes block in the default executor. Alpha: 0.1.34-0.1.45 refused pre-6.1 kernels and panicked without io_uring (#75), Windows 10 broken until 0.1.49 (#76); failures are Rust panics. README says Linux 6.1+ but master falls back to an unbenchmarked epoll path; docs cite crate 0.1.52 but crates.io stops at 0.1.44. glibc 2.39+ only, no musl; import patches asyncio and ssl.SSLContext; UDP, sendfile and sock_recvfrom/sendto are Python shims; no preexec_fn.

## Caveats and trade-offs

First-party benchmark (same author wrote rsloop and the harness) but careful: pinned dependency versions, medians of 7 runs after 2 warmups in fresh subprocesses, confidence intervals for idle latency. The TCP-roundtrip win uses rsloop's native fast streams while the other loops use stdlib asyncio streams (`--no-rsloop-fast-streams` gives the like-for-like run, not published). Microbenchmarks and the workload matrix come from different runs and rsloop versions (0.1.52 vs 0.1.49) with unrestricted CPU affinity and other host services running. rustc version and release flags come from the repo (rust-toolchain.toml, Cargo.toml), not from the benchmarks page. Idle-latency advantage is labelled inconclusive by the author.

Results are workload-dependent: rsloop leads TCP/TLS/bulk-transfer scenarios but loses to uvloop/zuvloop on raw callback/task scheduling and some WebSocket scenarios; author explicitly cautions these are local microbenchmarks, not isolated-lab or general application performance claims; trades helper-thread CPU for loop-thread work under contention

## Maintenance

Actively released (0.1.53 on PyPI 2026-09-15, 52 releases since 2026-03-21, 203 stars), almost entirely by one maintainer; Apache-2.0 with prebuilt wheels on PyPI and conda-forge, but still classified Alpha, and patch releases have carried breaking platform changes.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** docs/benchmarks.md compares rsloop directly with uvloop 0.22.1 (plus stdlib asyncio and zuvloop) using public harnesses benches/compare_event_loops.py and benches/workload_matrix.py, and names the CPU (Intel Core i9-9900K), kernel and CPython 3.14.7. At the benchmark commits (5d0a2bb, 6cc3444) the repo pins rustc 1.98.1 (rust-toolchain.toml) and the release profile (opt-level=3, lto="fat", codegen-units=1) that `maturin develop --release` uses, so compiler, flags, CPU and code are all available (same standard as the xutf precedent).
- **Verifier notes:** All claimed numbers appear on docs/benchmarks.md. The record wrongly said uvloop beats rsloop on callbacks and tasks; on the Linux run only zuvloop does. Default branch master was last committed 2026-09-15; the 2026-09-25 date is a push to side branch perf/nightly-allocator-api. Stars 203, Apache-2.0, not a fork, not archived.
- **Fields the verifier corrected:** `last_commit`, `compiler_and_flags`, `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/RustedBytes/rsloop>
  - <https://github.com/RustedBytes/rsloop/blob/master/docs/benchmarks.md>
  - <https://github.com/RustedBytes/rsloop/blob/master/Cargo.toml>
  - <https://github.com/RustedBytes/rsloop/blob/master/rust-toolchain.toml>
  - <https://github.com/RustedBytes/rsloop/blob/5d0a2bb/rust-toolchain.toml>
  - <https://github.com/RustedBytes/rsloop/blob/5d0a2bb/Cargo.toml>
  - <https://github.com/RustedBytes/rsloop/blob/6cc3444/rust-toolchain.toml>
  - <https://github.com/RustedBytes/rsloop/tree/master/benches>
  - <https://github.com/RustedBytes/rsloop/blob/master/.cargo/config.toml>
- **Sources the enricher read:**
  - <https://github.com/RustedBytes/rsloop>
  - <https://github.com/RustedBytes/rsloop/blob/master/README.md>
  - <https://github.com/RustedBytes/rsloop/blob/master/docs/benchmarks.md>
  - <https://github.com/RustedBytes/rsloop/blob/master/docs/how-it-works.md>
  - <https://github.com/RustedBytes/rsloop/blob/master/docs/supported-features.md>
  - <https://github.com/RustedBytes/rsloop/blob/master/docs/fast-streams.md>
  - <https://github.com/RustedBytes/rsloop/blob/master/docs/free-threading.md>
  - <https://github.com/RustedBytes/rsloop/blob/master/docs/getting-started.md>
  - <https://github.com/RustedBytes/rsloop/blob/master/docs/index.md>
  - <https://github.com/RustedBytes/rsloop/blob/master/Cargo.toml>
  - <https://github.com/RustedBytes/rsloop/blob/master/rust-toolchain.toml>
  - <https://github.com/RustedBytes/rsloop/blob/master/pyproject.toml>
  - <https://github.com/RustedBytes/rsloop/blob/master/src/vibeio/UPSTREAM.md>
  - <https://github.com/RustedBytes/rsloop/blob/master/src/vibeio/builder.rs>
  - <https://github.com/RustedBytes/rsloop/blob/master/src/vibeio/driver/mod.rs>
  - <https://github.com/RustedBytes/rsloop/blob/master/src/engine/loop_core.rs>
  - <https://github.com/RustedBytes/rsloop/blob/master/src/bindings/loop_api/fast_callbacks.rs>
  - <https://github.com/RustedBytes/rsloop/blob/master/src/transport/stream/tuning.rs>
  - <https://github.com/RustedBytes/rsloop/blob/master/src/transport/stream/tls_session.rs>
  - <https://github.com/RustedBytes/rsloop/blob/master/src/transport/tls/mod.rs>
  - <https://github.com/RustedBytes/rsloop/blob/master/src/transport/tls/material.rs>
  - <https://github.com/RustedBytes/rsloop/blob/master/python/rsloop/_loop_compat.py>
  - <https://github.com/RustedBytes/rsloop/blob/master/python/rsloop/_bootstrap.py>
  - <https://github.com/RustedBytes/rsloop/blob/master/benches/compare_event_loops.py>
  - <https://github.com/RustedBytes/rsloop/blob/master/.github/workflows/wheels.yml>
  - <https://github.com/RustedBytes/rsloop/blob/master/.github/workflows/tests.yml>
  - <https://github.com/RustedBytes/rsloop/issues>
  - <https://github.com/RustedBytes/rsloop/issues/30>
  - <https://github.com/RustedBytes/rsloop/issues/37>
  - <https://github.com/RustedBytes/rsloop/issues/66>
  - <https://github.com/RustedBytes/rsloop/issues/73>
  - <https://github.com/RustedBytes/rsloop/issues/75>
  - <https://github.com/RustedBytes/rsloop/issues/76>
  - <https://pypi.org/pypi/rsloop/json>
  - <https://crates.io/api/v1/crates/rsloop>
  - https://hn.algolia.com/api/v1/search?query=rsloop&tags=(story,comment)
  - <https://hn.algolia.com/api/v1/items/47472041>
  - <https://github.com/RustedBytes/rsloop/blob/master/docs/rust-extensions.md>
  - <https://crates.io/api/v1/crates/rsloop/versions>
  - <https://api.github.com/repos/RustedBytes/rsloop/contributors>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/rustedbytes/rsloop`) · [data/wave5/enrich/raw/github_com_rustedbytes_rsloop.json](../../../data/wave5/enrich/raw/github_com_rustedbytes_rsloop.json) (enrichment confidence 0.8)

</details>
