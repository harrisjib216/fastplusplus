# Monocoque

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Message queues and logs](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `MIT` · 🟢 active

> Pure-Rust, ZeroMQ wire-compatible (ZMTP 3.x) async messaging library; about 3x lower REQ/REP latency than libzmq.

| | |
|---|---|
| **Beats** | ZeroMQ (libzmq) |
| **Claimed result** | REQ/REP p50 latency 2.75x-3.12x lower than libzmq 4.3.5 across IPC and TCP at 64B/1024B/16384B payloads. Example: IPC 1024B, monocoque 13.79us vs libzmq 42.16us at p50 and 16.80us vs 47.49us at p99. Across all six payloads (16B-16KiB) the compio backend is 2.69x-3.12x. The tokio backend reaches about 4.3x at IPC 16B-1KiB (9.36-9.70us vs 40.17-42.16us p50). The same run shows about 2.0x-4.7x higher single-pair throughput than libzmq (derived from page data). |
| **Workload** | REQ/REP round trip over TCP (per-run network namespace with private loopback) and IPC (Unix domain socket), payload sizes 16B-16KiB, one socket pair per cell. libzmq 4.3.5 (Ubuntu 24.04 package, 1 I/O thread) is compared with monocoque 0.4.1 (default compio/io_uring backend, plus tokio and smol backends). Each cell runs 5-11 replicates with MAD outlier rejection inside a cgroup v2 leaf (cpuset 0-3, 256 MiB memory cap). Each implementation is built in a pinned Docker image and then exec'd directly on bare metal (chroot plus network namespace, no container runtime) under zmq-arena's harness. |
| **Metric** | latency |
| **Hardware** | 13th Gen Intel Core i5-13400 (16 threads), Ubuntu 24.04.2 LTS, kernel 6.8.0-58-generic, x86_64, performance governor, turbo disabled, bare metal, run as root (per the run's recorded hardware block) |
| **Compiler and flags** | monocoque target: rustc 1.96.0 (rust-toolchain.toml plus Dockerfile), [profile.release] opt-level=3, lto=true, codegen-units=1, panic=abort, RUSTFLAGS='-C target-cpu=x86-64-v3'. libzmq target: Ubuntu 24.04 build-essential g++, CMake Release with '-O3 -flto -march=x86-64-v3' for the wrapper, linked against the Ubuntu libzmq5 4.3.5 distro package. |
| **Adoption** | 46 stars |
| **Last commit** | 2026-09-22 |
| **Links** | [repository](https://github.com/vorjdux/monocoque) · [benchmark](https://vorjdux.github.io/zmq-arena/history/2026-08-26-run.json) |

## Verdict

In zmq-arena's 2026-08-26 run on a bare-metal i5-13400 (Ubuntu 24.04, kernel 6.8, turbo off), monocoque 0.4.1 (rustc 1.96, fat LTO, x86-64-v3) had REQ/REP p50 round trips 2.69x-3.12x lower than Ubuntu's libzmq 4.3.5 package. libzmq was driven from an -O3 C++ wrapper with one I/O thread; example cells are 13.79 vs 42.16 us over IPC at 1 KiB and 15.48 vs 42.99 us over TCP at 1 KiB. Monocoque's author wrote the harness and published both run files, and no third party has reproduced them.

## Use it when

- Rust services on Linux that must talk to existing libzmq/pyzmq peers and want lower request/reply latency: in the arena run, REQ/REP p50 was about 13-22 us against 40-61 us for libzmq across 16 B-16 KiB payloads.
- Same-host request/reply over IPC: with the tokio backend, p50 was 9.36-9.70 us at 16 B-1 KiB against 40.17-42.16 us for libzmq.
- Small-message PUSH/PULL pipelines where you can call flush() at batch boundaries: coalesced PUSH/PULL reached 13.3 M msg/s at 64 B over IPC against 2.84 M msg/s for libzmq, and 7.6 M vs 3.1 M over TCP.
- PUB/SUB fan-out to many subscribers: at 32 subscribers it delivered 1.7x-4.5x libzmq's message rate, with lower peak RSS (35 MB vs 162 MB at 16 KiB).
- Async Rust codebases already on tokio or smol: pick the matching backend feature and run the sockets on a current-thread runtime.

## Skip it when

- Non-Rust callers, or code that depends on libzmq's C ABI, blocking send/recv, zmq_poll or libzmq's many language bindings. This is an async Rust library only.
- Deployments that need transports or features beyond TCP/IPC: PGM/EPGM, TIPC, draft sockets and GSSAPI are listed as skipped in the CHANGELOG, and inproc is a channel bridge that the migration guide says is not the same as libzmq inproc.
- Security-critical CURVE setups that need a track record. Before 0.4.0 (2026-07-31) the CURVE message cipher was not the real CurveZMQ construction, so encrypted interop with libzmq never worked. That same release also closed several pre-auth DoS holes (slow-loris recv timeout, unbounded handshake, unbounded multipart).
- Fan-in of many tiny messages from many producers: at 4-peer fan-in with 16 B messages, the default compio backend reached only 0.94x libzmq's rate. At 1 KiB its peak RSS was 85.6 MB against 38.5 MB for libzmq.
- Teams that need a mature dependency. The crate was first published on 2026-06-22 and has 312 total downloads and 46 stars. It is essentially single-maintainer (49 of 50 issues were filed by the author) and pre-1.0, with breaking changes in 0.3.0 and 0.4.0.

## How it is fast

The main latency lever is that there is no background I/O thread. send() and recv() do the I/O inline on the caller's single-threaded runtime (thread-per-core, and sockets are !Send). libzmq instead passes every message through a lock-free queue to a separate I/O thread. The arena data backs this up: the epoll-based tokio backend matches or beats the io_uring default on REQ/REP (IPC 16 B: 9.36 vs 13.08 us p50), so the win comes from removing the thread hop, not from io_uring. For bulk traffic it uses refcounted Bytes (PUB fan-out clones references and never copies payloads), a reused 64 KiB read slab, allocation-free recv_into, writev for bodies of 32 KB and up, and opt-in write coalescing that packs many small frames into one 64 KB write. The arena's throughput cells turn coalescing on; its REQ/REP cells do not.

## Compared with alternatives

Pick Monocoque over TCPSHM when the other side must stay a stock ZeroMQ peer: TCPSHM uses its own protocol and wins on raw same-host RTT, especially in shared-memory mode. Pick it over NanoMsg when you need ZMTP wire compatibility and CURVE rather than nanomsg's own SP protocols.

## Integration

| | |
|---|---|
| **Form** | crate (monocoque-rs; library name `monocoque`; the ZeroMQ API sits behind the opt-in `zmq` feature) |
| **Dependencies** | No libzmq or C library. Requires exactly one runtime: compio 0.19 (default, io_uring), tokio or smol. Also pulls bytes, compio-io/compio-buf, tracing and flume, plus dashmap, parking_lot, hashbrown, smallvec, socket2 and zeroize in the core crate. The workspace declares RustCrypto x25519-dalek, crypto_box, chacha20poly1305 and sha2 for PLAIN/CURVE. |
| **Minimum toolchain** | Rust 1.95 (edition 2024) for every backend, as checked in CI. The manifest notes that the tokio/smol backends can compile as far back as 1.93. |
| **Platforms** | Linux first: the io_uring default needs kernel 5.11+ for the full benefit and falls back to thread-pool I/O on older kernels. The docs offer the tokio/smol backends for macOS, Windows and older kernels, but CI runs only on ubuntu-latest. IPC is Unix-only. |
| **Thread safety** | Sockets are !Send on every backend. Run one single-threaded runtime per thread (compio runtime, current-thread tokio in a LocalSet, or smol LocalExecutor) and scale by running one runtime per core. The worker-pool PubSocket shards fan-out writes across its own worker threads. |
| **Drop-in for the baseline** | partial — wire-compatible with libzmq 4.1+ peers (ZMTP 3.x with NULL/PLAIN/CURVE), so it can replace one side of an existing ZeroMQ deployment. It is not an API or ABI replacement: it is async Rust only, has no context and no zmq_poll (futures::select! instead), handles multipart messages as a single Vec&lt;Bytes&gt;, and sets options through a SocketOptions builder. |

## Gotchas

- Write coalescing is off by default, so each eager send() is one syscall (about 0.44-0.52 M msg/s at 64 B in the project's local bench). Turning coalescing on makes you own flush(): in request/reply, forgetting flush() before recv() deadlocks, and messages still in the buffer are lost if the process crashes.
- Cancelling a send future mid-write (a timeout, or a losing select! branch) poisons the socket, and later I/O fails with BrokenPipe, 'reconnect required'. This matters because the migration guide suggests futures::select! as the replacement for zmq_poll.
- On the tokio backend, the worker-pool PubSocket's writes depend on the runtime that accepted the subscriber. A short-lived publisher that lets that runtime shut down right after sending can drop the tail of its broadcast.
- Benchmark caveat: the run kept the default cgroup cpuset 0-3. The arena's own README says that setting is only correct on four distinct physical performance cores. The i5-13400 is a hybrid SMT part, and libzmq's extra I/O thread per process competes for those four logical CPUs, so the gap may be different on other hardware.

## Known shortcomings

- The zmq-arena harness is by Monocoque's own author; the tokio backend gain is \~4.3x (the 2.75-3.12x p50 figure is the fastest backend).
- The speedup comes from skipping libzmq's I/O-thread hop; the tokio/epoll backend beats the io_uring default on IPC REQ/REP (9.36 vs 13.08 us p50). Its CURVE cipher was not real CurveZMQ before 0.4.0 (2026-07-31), which also fixed pre-auth DoS holes. Young (crate from 2026-06, 312 downloads, author filed 49 of 50 issues), pre-1.0 with breaking changes; async Rust only (no C ABI/zmq_poll/blocking API), sockets are !Send, CI Linux only.
- Fan-in with 16 B messages on compio is 0.94x libzmq and fan-in at 1 KiB uses 85.6 vs 38.5 MB RSS. A cancelled send poisons the socket (clashes with select! advice); coalescing needs a manual flush() (deadlock/loss risk). Author-run benchmark pinned to cpuset 0-3 on a hybrid SMT i5, which the arena README itself warns about.

## Caveats and trade-offs

The harness (vorjdux/zmq-arena, 1 star, Apache-2.0) is written by monocoque's own author, and no independent third party has reproduced the result. Only two runs are published (2026-08-21 and 2026-08-26), both on a single machine (i5-13400, turbo off). The libzmq baseline is Ubuntu's distro-built libzmq5, not built with the harness flags. The same run also covers throughput, pub/sub (32 subscribers) and fan-in/fan-out (4 peers), where monocoque mostly leads too; the one loss is fan-in at 16B, 0.94x. One cell, compio IPC 64B, is flagged unstable. The run tested 0.4.1; crates.io now has monocoque-rs 0.4.2. The repo is small (46 stars; the crate has 312 downloads).

Benchmark is authored by the same person who wrote both monocoque and the zmq-arena harness (first-party, though code, hardware and raw per-cell JSON are all public and independently re-runnable); monocoque is a from-scratch ZMTP 3.1 reimplementation rather than a libzmq wrapper, so it forgoes libzmq's mature C ABI, CURVE hardening track record, and broad language-binding ecosystem; each engine is built from a version-pinned Docker image (image digest recorded) rather than a bare compiler-flags string.

## Maintenance

Actively maintained (0.4.2 released 2026-09-22 after roughly monthly releases since June 2026) and MIT-licensed, but it is pre-1.0, single-maintainer and lightly used, so pin the version and expect API breaks between minor releases.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** The 2026-08-26 run JSON has libzmq@4.3.5 and monocoque@0.4.1 records that match the claim: IPC 1024B p50 13.79 vs 42.16 us and p99 16.80 vs 47.49 us, with 2.75x-3.12x at 64/1024/16384B. The code is public in vorjdux/zmq-arena: targets/monocoque_target/src/main.rs, targets/libzmq_cpp_target/src/main.cpp and the orchestrator. The build flags are pinned: rustc 1.96.0 with opt-level=3, lto, codegen-units=1 and target-cpu=x86-64-v3; the C++ wrapper uses -O3 -flto -march=x86-64-v3 with Ubuntu 24.04 g++. The CPU (i5-13400) is recorded, so A holds.
- **Verifier notes:** The numbers match the run JSON exactly. The record's caveat 'single socket pair, no fan-out or multi-peer contention' was wrong, since the run includes pub/sub and fan-in/fan-out cells. Metadata checks out: MIT, not a fork, 46 stars, last commit 2026-09-22.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://vorjdux.github.io/zmq-arena/history/2026-08-26-run.json>
  - <https://vorjdux.github.io/zmq-arena/history/index.json>
  - <https://vorjdux.github.io/zmq-arena/>
  - <https://github.com/vorjdux/monocoque>
  - <https://github.com/vorjdux/monocoque/blob/main/README.md>
  - <https://github.com/vorjdux/zmq-arena>
  - <https://github.com/vorjdux/zmq-arena/blob/main/targets/libzmq_cpp_target/Dockerfile>
  - <https://github.com/vorjdux/zmq-arena/blob/main/targets/libzmq_cpp_target/CMakeLists.txt>
  - <https://github.com/vorjdux/zmq-arena/blob/main/targets/libzmq_cpp_target/src/main.cpp>
  - <https://github.com/vorjdux/zmq-arena/blob/main/targets/monocoque_target/Dockerfile>
  - <https://github.com/vorjdux/zmq-arena/blob/main/targets/monocoque_target/Cargo.toml>
  - <https://github.com/vorjdux/zmq-arena/blob/main/targets/monocoque_target/rust-toolchain.toml>
  - <https://crates.io/api/v1/crates/monocoque-rs>
- **Sources the enricher read:**
  - <https://github.com/vorjdux/monocoque>
  - <https://github.com/vorjdux/monocoque/blob/main/README.md>
  - <https://github.com/vorjdux/monocoque/blob/main/Cargo.toml>
  - <https://github.com/vorjdux/monocoque/blob/main/monocoque/Cargo.toml>
  - <https://github.com/vorjdux/monocoque/blob/main/monocoque-core/Cargo.toml>
  - <https://github.com/vorjdux/monocoque/blob/main/docs/COMPATIBILITY.md>
  - <https://github.com/vorjdux/monocoque/blob/main/docs/performance.md>
  - <https://github.com/vorjdux/monocoque/blob/main/docs/MIGRATION.md>
  - <https://github.com/vorjdux/monocoque/blob/main/docs/PRODUCTION_DEPLOYMENT.md>
  - <https://github.com/vorjdux/monocoque/blob/main/docs/troubleshooting.md>
  - <https://github.com/vorjdux/monocoque/blob/main/CHANGELOG.md>
  - <https://github.com/vorjdux/monocoque/blob/main/.github/workflows/ci.yml>
  - <https://github.com/vorjdux/monocoque/blob/main/monocoque/src/zmq/dealer.rs>
  - <https://github.com/vorjdux/monocoque/blob/main/monocoque-zmtp/src/base.rs>
  - <https://github.com/vorjdux/monocoque/blob/main/monocoque-core/src/poison.rs>
  - <https://github.com/vorjdux/monocoque/issues?q=is%3Aissue>
  - <https://github.com/vorjdux/monocoque/pulls?q=is%3Apr>
  - <https://vorjdux.github.io/zmq-arena/history/2026-08-26-run.json>
  - <https://vorjdux.github.io/zmq-arena/history/index.json>
  - <https://github.com/vorjdux/zmq-arena>
  - <https://github.com/vorjdux/zmq-arena/blob/main/README.md>
  - <https://github.com/vorjdux/zmq-arena/blob/main/targets/monocoque_target/src/main.rs>
  - <https://github.com/vorjdux/zmq-arena/blob/main/targets/libzmq_cpp_target/src/main.cpp>
  - <https://crates.io/api/v1/crates/monocoque-rs>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/vorjdux/monocoque`) · [data/wave6/enrich/raw/github_com_vorjdux_monocoque.json](../../../data/wave6/enrich/raw/github_com_vorjdux_monocoque.json) (enrichment confidence 0.8)

</details>
