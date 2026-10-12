# ringline

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [Event loops and async I/O](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟢 active

> Thread-per-core io_uring runtime for Rust servers: 4-71% faster than default tokio on TCP echo, -10% to +9% versus tuned tokio.

| | |
|---|---|
| **Beats** | tokio (multi-thread work-stealing runtime, epoll/mio-based) |
| **Claimed result** | TCP echo (Sept 2026, commit a685e16): against the best of five tokio configurations, ringline leads in 13 of 16 cells, from -10.3% to +8.9% (the page says 'roughly 0-10% faster'). It loses at 16 KiB/64 conns (-10.3%), 16 KiB/512 (-4.9%) and 4 KiB/64 (-0.1%). Against tokio's default multi-thread runtime it is +4% to +71% (256 B: +4/+70/+46/+27%; 4 KiB: +16/+57/+36/+33%; 16 KiB: +42/+71/+51%). The page itself retracts the earlier '27-71%' lead because it implied a win over tokio's best configuration. At 512 conns/256 B it does 619,863 ops/s against 591,854 for tokio-uring and 425,486 for default tokio. Segcache GET (June 2026, v0.1.3, 4 workers, 128 conns): at 256 B/1 KiB, +31%/+30% throughput, -28%/-24% p50, -15%/-18% p99, +22%/+23% ops/core-s. At 4 KiB, throughput and p50 tie, p99 is -8% and ops/core-s +14%. At open-loop saturation the two tie (NIC/PPS-bound). |
| **Workload** | Two-machine TCP echo benchmark (9 server configs x 4 message sizes x 4 connection counts, bare-metal Xeon, X710 40G LAG) plus a Segcache GET cache-server workload (256B/1KiB/4KiB values, 128 connections) on AWS Graviton4 c8g instances |
| **Metric** | throughput |
| **Hardware** | Echo run: server is a 24 vCPU Xeon (hv02 guest), client a 56 vCPU Xeon (hv01 guest). The page says 'bare metal', but the runs were SystemsLab anvil-vm jobs with the X710 PFs passed through. Network is 4x Intel X710 in a direct-attached 40G LAG; no CPU model is given. 8 server workers, 16 client threads. Segcache run: AWS c8g.4xlarge (16 vCPU Graviton4, Neoverse-V2) server and c8g.8xlarge (32 vCPU Graviton4) client, same AZ, cluster placement group, Debian 13, Linux 6.12. |
| **Compiler and flags** | Rust 'stable' (segcache run only). Neither run gives a rustc version or build flags. The workspace has edition 2024 and MSRV 1.88, no [profile.release] overrides and no rust-toolchain pin. |
| **Adoption** | 8 stars; crates.io ringline 0.6.3, 2,895 downloads (1,427 recent) |
| **Last commit** | 2026-09-26 |
| **Links** | [repository](https://github.com/ringline-rs/ringline) · [benchmark](https://github.com/ringline-rs/ringline/blob/main/BENCHMARKS.md) |

## Verdict

First-party two-machine TCP echo (Sept 2026, commit a685e16). The server ran 8 workers in a 24 vCPU Xeon VM guest with passed-through X710 40G NICs; no CPU model, rustc version or build flags are given. ringline beat the best of five tokio configurations in 13 of 16 cells (-10.3% to +8.9%) and default multi-thread tokio by 4% to 71%. An older Segcache GET run (June 2026, v0.1.3, Graviton4 c8g, 4 workers, 128 conns, 'stable' Rust) against a single tokio configuration showed about +30% throughput and 24-28% lower p50 at 256 B-1 KiB, a tie at 4 KiB, and a tie at open-loop saturation. Its harness branch no longer exists.

## Use it when

- Linux 6.1+ request/response servers (caches, protocol servers) with many connections and small-to-medium messages (256 B-4 KiB), where CPU per request and p50/p99 matter
- Replacing a default multi-thread tokio service whose tokio-ecosystem dependencies you can drop; that is where the +27-71% echo and +30% Segcache gains were measured
- Workloads that shard cleanly per core, where connection state never has to move between threads
- Stacks that want the same per-core runtime for their outbound clients: the workspace ships Redis, memcache, HTTP/1.1-2-3, gRPC and QUIC crates on top of it

## Skip it when

- You already run tokio per-core or on tokio-uring: its lead there is about 0-10% (tokio-uring came within 4.7% at 512 conns/256 B), and it loses at 16 KiB with 64 or 512 connections
- Byte-forwarding proxies with payloads of 16 KiB or more at moderate concurrency: splice-based tokio beat every ringline configuration by up to 10.3%
- Code built on hyper, tonic, tower or tokio::sync: the APIs are incompatible, and tasks, channels and wakers only work within their own worker thread
- Hosts or containers where seccomp, kernel.io_uring_disabled or a tight RLIMIT_MEMLOCK blocks or limits io_uring (open issue #426 is io_uring_setup failing with ENOMEM on CI runners)
- Teams that need a stable API: it is pre-1.0, has had a breaking 0.x minor bump every 2-7 weeks (0.1.0 in April to 0.6.3 in September 2026), and has essentially one author

## How it is fast

Mostly the thread-per-core scheduler, meaning no work-stealing and no task migration. The project's own 2x2 shows that a per-core tokio closes most of the gap, and ringline's epoll backend beats default tokio (451k vs 425k ops/s) even though it makes more syscalls. The io_uring backend adds multishot recv into ring-provided buffers, fixed (direct) file descriptors and SINGLE_ISSUER/DEFER_TASKRUN/COOP_TASKRUN rings. Sends and receives ride one batched io_uring_enter, so it makes 0.06 syscalls/op against tokio's 2.08 at 512 conns/256 B. It also uses SendMsgZc zero-copy for guard-backed sends of 4 KiB or more.

## Compared with alternatives

monoio is the closest catalogued sibling, also a Rust thread-per-core io_uring runtime, and its 1.86x is likewise against default tokio. Pick ringline when you want built-in rustls TLS, UDP/QUIC and protocol clients plus a mio fallback in one workspace, or a benchmark page that also reports results against tuned tokio. For C++ services, Seastar or uring_exec fill the same niche.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | io-uring 0.7 (Linux only), mio 1, rustls 0.23 (ring), bytes, crossbeam-channel, futures-io, metriken, libc, thiserror, pin-project-lite |
| **Minimum toolchain** | Rust 1.88 (edition 2024) |
| **Platforms** | io_uring backend: Linux 6.1+ on x86_64 or aarch64; mio backend: macOS, other Unix and older Linux (no zero-copy send or NVMe passthrough) |
| **Thread safety** | Thread-per-core. The handler type is Send (it is built once per worker), but connection futures, channels (Rc&lt;RefCell&gt;) and wakers are !Send and bound to their worker thread. Cross-thread signalling goes through WakeHandle/on_notify or spawn_blocking; ShutdownHandle stops all workers. |
| **Drop-in for the baseline** | no |

## Gotchas

- The backend is picked by build.rs from the build host's /proc kernel version. Building on a pre-6.1 kernel silently gives you a mio binary, and cross-compiles assume io_uring. Check ringline::backend() before you benchmark.
- Its Waker pushes onto the calling thread's thread-local ready queue, so a foreign future completed from another OS thread (for example a tokio or futures channel) will not wake the ringline task. ConnStream (the futures-io AsyncRead/AsyncWrite adapter) panics if it is polled outside the ringline executor.
- Capacity is fixed at config time. Exhausting the copy-send pool, zero-copy slab, task slab or timer slots returns an error rather than growing. Workers default to one per physical core, but its own sweep shows ops/core-s falling from 221k at 4 workers to 127k at 16 workers with 128 connections, so size the worker count to your concurrency.
- It is young: recent fixes include io_uring dropping a response sent after the peer's FIN (#371) and merged-accept mode silently ignoring TCP_NODELAY, which made TLS accepts 29x slower (#460). The mio backend still makes 2.9x tokio's epoll syscalls (open issue #395).

## Known shortcomings

- Rust io_uring runtime compared with Tokio on its own page: +4% to +71% over default Tokio, and against best-tuned Tokio it loses by up to 10.3% in some rows. CPU named only as 'Xeon'; no rustc or flags; the cache-server benchmark branch no longer exists.
- Only \~0-10% ahead of well-configured tokio and behind at 16 KiB with 64/512 connections; the 4-71% lead is against default multi-thread tokio, and tokio-uring comes within 4.7%. Segcache is the only protocol-parsing benchmark, stale (v0.1.3) and its harness branch is gone. build.rs picks io_uring or epoll from the build host's kernel, so a build on a pre-6.1 kernel silently ships epoll. Wakers push onto the calling thread's queue, so wakeups from other OS threads are lost; does not fit hyper/tonic/tower. Fixed-capacity pools error when full; RLIMIT_MEMLOCK, seccomp or io_uring_disabled can block startup (#426). Pre-1.0 with breaking releases every 2-7 weeks, one main author. Recent bugs: lost response after peer FIN (#371, fixed), merged-accept ignored TCP_NODELAY (#460, fixed), epoll backend makes 2.9x tokio's syscalls (#395, open). Per-core throughput drops sharply with too many workers.

## Caveats and trade-offs

First-party benchmark in the project's own repo, not independent. It stays below Tier A because the echo CPU is only 'Xeon', no rustc version or build flags are given, and the segcache harness is said to be on branch bench/fair-throughput, which no longer exists on GitHub; only the echo harness (ringline-bench) is on main. The retraction of the earlier 27-71% headline is in BENCHMARKS.md's own 'Read this first' section, not in the README. The README's Benchmarks section still describes only the June 2026 segcache run. Segcache is the only protocol-like workload. It is stale (ringline 0.1.3, June 2026), predates the harness fairness fix #392, compares against a single tokio configuration, and ties at open-loop saturation. The echo run is a byte pipe with no parsing, and its 2048-connection column is labelled directional. ringline loses to splice-based tokio at 16 KiB. The echo rig is called bare metal but was run as VM guests with NIC passthrough. The README says ringline is not a tokio replacement and is not API-compatible.

Only \~0-10% faster than tokio's best-tuned configurations; the larger 27-71% figure holds only against tokio's default (non-per-core) config. Loses to a zero-copy tokio+splice path at 16KiB payloads. Requires manual worker-count tuning matched to concurrency for best CPU efficiency. Linux-focused (io_uring/epoll/mio backends).

## Maintenance

Very active, with daily commits; crates.io has 0.6.3 with about 2.9k downloads, used mostly by the author's own sibling crates. Dual MIT/Apache-2.0 and easy to depend on, but pre-1.0, with frequent breaking releases and effectively one maintainer.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** BENCHMARKS.md is a first-party two-machine comparison against tokio, with a named rig, Little's-law validity gates and reproduction commands. The echo harness is public (ringline-bench/src/bin/server.rs has the --tokio-scheduler/--echo-mode arms), but the echo CPU is only 'Xeon' and neither run gives a rustc version or build flags. The segcache harness is said to live on branch bench/fair-throughput, which no longer exists, so this is not A.
- **Verifier notes:** The page's numbers match the record. The segcache figures are exact. I rewrote claimed_speedup because the default-tokio range is really +4% to +71% (the 1-connection cells are +4%/+16%), and the 'best tokio' comparison includes losses of up to 10.3%. I also fixed the caveat that credited the retraction to the README (it is in BENCHMARKS.md). The license is dual MIT OR Apache-2.0 (Cargo.toml, README, and both LICENSE-MIT and LICENSE-APACHE files), even though GitHub's API reports only Apache-2.0. The last commit is 2026-09-26; the repo is not archived and not a fork.
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `compiler_and_flags`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/ringline-rs/ringline/blob/main/BENCHMARKS.md>
  - <https://github.com/ringline-rs/ringline>
  - <https://github.com/ringline-rs/ringline/blob/main/README.md>
  - <https://github.com/ringline-rs/ringline/blob/main/Cargo.toml>
  - <https://github.com/ringline-rs/ringline/blob/main/ringline-bench/Cargo.toml>
  - <https://github.com/ringline-rs/ringline/blob/main/ringline-bench/src/bin/server.rs>
  - <https://github.com/ringline-rs/ringline/tree/main/experiments>
  - <https://github.com/ringline-rs/ringline/commit/c77cfbae2f6743e2b74560680c2ed686c4e15109>
  - <https://github.com/ringline-rs/ringline/commit/a685e1615a770d2a68bd92f8d0f199ea4cf29691>
  - <https://crates.io/api/v1/crates/ringline>
- **Sources the enricher read:**
  - <https://github.com/ringline-rs/ringline>
  - <https://github.com/ringline-rs/ringline/blob/main/README.md>
  - <https://github.com/ringline-rs/ringline/blob/main/BENCHMARKS.md>
  - <https://github.com/ringline-rs/ringline/blob/main/Cargo.toml>
  - <https://github.com/ringline-rs/ringline/blob/main/CHANGELOG.md>
  - <https://github.com/ringline-rs/ringline/blob/main/ringline/Cargo.toml>
  - <https://github.com/ringline-rs/ringline/blob/main/ringline/build.rs>
  - <https://github.com/ringline-rs/ringline/blob/main/ringline/README.md>
  - <https://github.com/ringline-rs/ringline/blob/main/ringline/ROADMAP.md>
  - <https://github.com/ringline-rs/ringline/blob/main/ringline/src/lib.rs>
  - <https://github.com/ringline-rs/ringline/blob/main/ringline/src/config.rs>
  - <https://github.com/ringline-rs/ringline/blob/main/ringline/src/runtime/handler.rs>
  - <https://github.com/ringline-rs/ringline/blob/main/ringline/src/runtime/stream.rs>
  - <https://github.com/ringline-rs/ringline/blob/main/ringline/src/runtime/waker.rs>
  - <https://github.com/ringline-rs/ringline/blob/main/ringline/src/runtime/channel.rs>
  - <https://github.com/ringline-rs/ringline/blob/main/ringline/src/wakeup.rs>
  - <https://github.com/ringline-rs/ringline/blob/main/ringline/tests/memlock_limit.rs>
  - <https://github.com/ringline-rs/ringline/blob/main/docs/architecture.md>
  - <https://github.com/ringline-rs/ringline/blob/main/docs/io-uring-primer.md>
  - <https://github.com/ringline-rs/ringline/blob/main/docs/syscalls-and-copies.md>
  - <https://github.com/ringline-rs/ringline/issues>
  - <https://github.com/ringline-rs/ringline/issues/426>
  - <https://github.com/ringline-rs/ringline/issues/395>
  - <https://github.com/ringline-rs/ringline/issues/460>
  - <https://github.com/ringline-rs/ringline/issues/371>
  - <https://github.com/ringline-rs/ringline/branches>
  - <https://api.github.com/repos/ringline-rs/ringline/contributors>
  - <https://crates.io/api/v1/crates/ringline>
  - <https://crates.io/api/v1/crates/ringline/reverse_dependencies>
  - <https://crates.io/api/v1/crates/ringline-momento>
  - <https://hn.algolia.com/api/v1/search?query=ringline&tags=story>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/ringline-rs/ringline`) · [data/wave5/enrich/raw/github_com_ringline_rs_ringline.json](../../../data/wave5/enrich/raw/github_com_ringline_rs_ringline.json) (enrichment confidence 0.75)

</details>
