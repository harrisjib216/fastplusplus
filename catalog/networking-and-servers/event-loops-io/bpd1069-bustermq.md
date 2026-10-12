# BusterMQ

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [Event loops and async I/O](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Zig` · `Apache-2.0` · 🟢 active

> Zig thread-per-core io_uring server for the core NATS pub/sub protocol; \~1.4x Go nats-server publish rate in its own benchmark.

| | |
|---|---|
| **Beats** | NATS Server (nats-server, Go, epoll-based via Go's netpoller) |
| **Claimed result** | Like-for-like standard NATS protocol (same bench_pub_sub client): BusterMQ 2.98M msg/s publish, 28.86M delivery, 4.03 GB/s, p50 11.43 ms, p99 92.55 ms vs Go NATS 2.16M, 21.09M, 2.94 GB/s, p50 55.70 ms, p99 104.00 ms (\~1.38x publish rate, \~1.37x bandwidth, \~4.9x lower p50; derived from page data). With BusterMQ's non-standard +ROUTE shard-aware extension (different client, bench_pub_sub_route): 6.78M msg/s, 8.80 GB/s, p50 5.02 ms (\~3.1x publish rate, \~3.0x bandwidth, \~11x lower p50 vs Go NATS; derived from page data). |
| **Workload** | Pub/sub fan-out benchmark from benchmark_pubsub.sh: 10 publishers, 10 subscribers, 10 topics, 50M messages of 128 bytes (\~10x fan-out), server pinned to cores 0-15 with 16 benchmark client threads; BusterMQ run in Standard, Std+BusyPoll, +ROUTE and +ROUTE+BusyPoll modes; Go nats-server run at default config via taskset with the standard bench_pub_sub client |
| **Metric** | throughput, latency |
| **Hardware** | AMD Ryzen 9 9950X (README: '9950x'), 16 threads for the server, 16 for the benchmark client; OS/kernel not stated |
| **Compiler and flags** | Not stated in the README. The repo pins Zig 0.15.2 (MODULE.bazel, rules_zig 0.12.2) and .bazelrc defaults to --compilation_mode=opt with rules_zig mode=release_fast; benchmark_pubsub.sh builds with --config=nixos. nats-server (Go) version and build not stated. |
| **Adoption** | 1 star; Show HN post 134 points, 65 comments (2026-01-01) |
| **Last commit** | 2026-01-01 |
| **Links** | [repository](https://github.com/bpd1069/bustermq) · [benchmark](https://github.com/bpd1069/bustermq/blob/master/README.md) |

## Verdict

In a single first-party run on one AMD Ryzen 9 9950X over localhost (16 server threads and 16 client threads; 10 publishers, 10 subscribers, 10 subjects, 50M 128-byte messages sent open-loop, so the latencies are queueing delay at saturation), BusterMQ on the standard protocol published 2.98M msg/s at 4.03 GB/s with p50 11.43 ms, against Go nats-server's 2.16M msg/s, 2.94 GB/s and p50 55.70 ms (about 1.38x). The bench client spread BusterMQ connections across its per-worker ports (-w 16) while nats-server took all of them on 4222, the 6.78M msg/s (\~3.1x) headline needs +ROUTE and its own client, and BusterMQ was built with Zig 0.15.2 ReleaseFast per the repo config while nats-server's version and config and the kernel are not stated.

## Use it when

- Studying or prototyping thread-per-core io_uring broker design: the Zig source is compact and ships with a deterministic-simulation (VOPR-style) test harness.
- Ephemeral core-NATS fan-out of small messages (the benchmark used 128 B) on one Linux box with dedicated cores, where at-most-once delivery with silent drops is acceptable.
- Latency-sensitive fan-out on dedicated cores that can spin at 100% CPU: in the saturated benchmark, --busy-poll cut p99 from 92.55 ms to 21.22 ms and raised the publish rate from 2.98M to 4.72M msg/s over the standard mode.
- Clients you control and can teach +ROUTE, with subjects that map cleanly to single workers; this was the fastest mode in the README (6.78M msg/s).

## Skip it when

- Production messaging. The project is a single 'first commit' tagged 0.1.0-alpha, and the author said on HN it is 'not a nats replacement' and that he has no time to maintain it. The original bustermq/bustermq repo and bustermq.sh are gone, and the catalogued URL is a third-party copy.
- Anything that needs JetStream or persistence, queue groups, headers, TLS, auth, clustering or leaf nodes, or payloads over 64 KB (max_payload is 65536).
- Workloads with heavy subscription churn, such as request/reply inboxes with unique subjects. The first SUB to a new subject on a worker, every wildcard SUB and each last UNSUB bump a global version under a mutex, and then every worker rebuilds its whole routing cache. UNSUB also linearly scans all of that worker's subscriptions.
- Memory-constrained or container deployments. By default it prefaults a 2 GB mbuf pool, reserves an N x N matrix of 131,072-entry SPSC queues (about 1 GiB at 16 workers; derived from 256 queues x 131,072 x 32-byte descriptors) and reserves a 16 MB send buffer per connection.
- Hosts with more than 64 hardware threads (worker bitmasks are u64), and kernels older than 6.1 if you publish payloads of 4 KB or more: that path uses IORING_OP_SENDMSG_ZC, which liburing documents as available since 6.1, while the README only asks for Linux 5.10+.

## How it is fast

Thread-per-core: one worker per core, pinned with sched_setaffinity, each with its own io_uring ring (optional SQPOLL or --busy-poll spinning), its own SO_REUSEPORT listener, and its own clients and subscriptions. Reads land in 64 KB reference-counted mbufs from a prefaulted pool, and publishes needed on other cores are forwarded as offset descriptors over an N x N matrix of lock-free SPSC queues with eventfd wakeups, so the payload is not copied between cores. Sends are batched once per loop iteration per client, payloads of 4 KB or more go out as scatter-gather IORING_OP_SENDMSG_ZC straight from the shared mbuf, and subject lookup uses a 64-bit rapidhash key in a per-worker routing cache fronted by a 256-bit Bloom filter. The +ROUTE extension removes the cross-worker hop by steering each subscriber to the worker that owns its subject (subject hash mod worker count).

## Compared with alternatives

Pick it only if you specifically need the NATS core wire protocol: it is the only catalogued entry that speaks NATS, but it is an unmaintained prototype. For a thread-per-core io_uring message system with persistence and an active project, Apache Iggy is the sibling to use; to build your own thread-per-core io_uring server, start from monoio or ringline instead.

## Integration

| | |
|---|---|
| **Form** | source-drop (standalone server binary built with Bazel; no library API) |
| **Dependencies** | Bazel with rules_zig 0.12.2 (hermetic Zig toolchain), rules_cc, bazel_skylib, aspect_bazel_lib, rules_oci, rules_distroless; libc (-lc); freref/spsc-queue fetched at a pinned git commit; vendored rapidhash.h |
| **Minimum toolchain** | Zig 0.15.2 (pinned in MODULE.bazel); .bazelversion pins Bazel 7.6.0 although the README says Bazel 8+ |
| **Platforms** | Linux only (io_uring; README says 5.10+, but payloads of 4 KB or more need SENDMSG_ZC, available since 6.1). Bazel platforms are declared for x86-64 and aarch64, but it was benchmarked only on x86-64 (Ryzen 9 9950X). Listeners are IPv4 only. |
| **Thread safety** | Not a library. Internally each worker owns its clients and subscriptions, cross-worker traffic goes through SPSC queues, the global routing index sits behind a mutex, and the mbuf pool is a shared lock-free free list. |
| **Drop-in for the baseline** | partial — standard NATS clients can connect and use core PUB/SUB/UNSUB on 4222, but queue groups, headers, TLS/auth, clustering, JetStream and payloads over 64 KB are missing, and it also binds one extra port per worker (4223 and up). |

## Gotchas

- Queue-group SUBs are parsed but the group is ignored, so every member gets every message instead of one of them. HPUB is rejected as an invalid command.
- Messages are dropped silently, with only a stats counter bumped, when a client's 16 MB send buffer, a cross-worker SPSC queue, or the 1,024-forwards-per-read-batch limit is full. There is no slow-consumer disconnect. The optional --overflow queue (1,024 messages) gives up per-client ordering.
- Exact subscriptions are keyed only by the 64-bit rapidhash of the subject, with identity equality and no string compare at delivery, so a hash collision would deliver to the wrong subscribers. The default starts one worker per detected CPU even though bitmasks cap it at 64 workers.
- -h/--host is accepted but ignored (listeners always bind 0.0.0.0). All heap allocations, including the per-SUB subject and SID copies, go through std.heap.page_allocator.

## Known shortcomings

- The 3.1x headline uses a non-standard +ROUTE protocol extension with a different client; like-for-like on the standard protocol it is \~1.38x (2.98M vs 2.16M msg/s), p50 11.43 vs 55.70 ms. nats-server version, compiler and flags not stated (repo pins Zig 0.15.2 release_fast). One commit; the author said on HN it is 'not a NATS replacement' and he has no time to maintain it; bustermq.sh no longer resolves (verifier downgrade).
- The listed repo is a third-party re-upload (not a GitHub fork) of a single-commit project whose original repo now 404s; the original author said on HN it is not a NATS replacement and won't be maintained. The 'standard' run spread BusterMQ's connections over 16 per-worker ports while nats-server took all on 4222 (SO_REUSEPORT 'broken on localhost'). Latencies are queueing delay at saturation (open-loop publishers, 1-in-100 sampling). Route modes deliver \~0.6-0.8% fewer messages than expected: the server silently drops on full 16 MB send buffers, full cross-worker queues or past 1,024 forwards per batch; no slow-consumer handling. NATS gaps: queue groups ignored (every member gets every message), HPUB rejected, no TLS or auth, 64 KB max payload, --host ignored (binds 0.0.0.0, IPv4 only), 64-worker cap, exact subscriptions matched only by 64-bit hash. README says Linux 5.10+ but zero-copy send needs 6.1; README says Bazel 8+ but 7.6.0 is pinned. Prefaults a 2 GB mbuf pool, \~1 GiB of SPSC queues at 16 workers, 16 MB per connection; subscription churn rebuilds every worker's routing cache under a global mutex.

## Caveats and trade-offs

First-party, self-run, single-host, single unrepeated run. The 3x headline needs BusterMQ's +ROUTE protocol extension and a shard-aware client, while Go NATS was driven by the standard client; the standard-protocol win is \~1.38x throughput. nats-server version unstated and run at defaults. The README's Benchmarks section shows only the bench_pub_sub_route command, but the table matches benchmark_pubsub.sh output. The repo is a single commit (2026-01-01); in the HN thread the author called it a personal-rig test, 'not a nats replacement', with no time to maintain it. Homepage bustermq.sh no longer resolves. Core NATS features only (no JetStream, group queues pending).

Zig + Bazel toolchain; implements only core NATS features, not the full protocol; SQPOLL/busy-poll modes trade CPU for latency

## Maintenance

One commit (2026-01-01), still 'active' only by the 12-month rule: the author disclaimed maintenance, the original repo and site are gone, and this URL is a third-party copy. It is Apache-2.0 and small enough to read or vendor as reference code, not as a maintained server.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification C, tier now C.
- **Tier reason:** The README table compares BusterMQ with Go nats-server on an AMD 9950X, and the harness is public (benchmark_pubsub.sh driving examples/benchmarks/bench_pub_sub.zig and bench_pub_sub_route.zig). The repo pins Zig 0.15.2 (MODULE.bazel) and release_fast/opt (.bazelrc), but the README states no compiler or flags and the nats-server version is never given, so it is first-party partial methodology: C.
- **Verifier notes:** Numbers match the README exactly. Verdict is downgrade for an overstated headline (the +ROUTE mode uses a non-standard protocol extension); tier stays C. maintenance_status left 'active' by the 12-month rule (last commit 2026-01-01), but the author signalled no ongoing maintenance.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `hardware`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/bpd1069/bustermq>
  - <https://github.com/bpd1069/bustermq/blob/master/README.md>
  - <https://github.com/bpd1069/bustermq/blob/master/benchmark_pubsub.sh>
  - <https://github.com/bpd1069/bustermq/blob/master/.bazelrc>
  - <https://github.com/bpd1069/bustermq/blob/master/MODULE.bazel>
  - <https://github.com/bpd1069/bustermq/blob/master/LICENSE>
  - <https://hn.algolia.com/api/v1/search?query=bustermq&tags=story>
  - <https://hn.algolia.com/api/v1/items/46449812>
- **Sources the enricher read:**
  - <https://github.com/bpd1069/bustermq>
  - <https://github.com/bpd1069/bustermq/blob/master/README.md>
  - <https://github.com/bpd1069/bustermq/blob/master/.bazelrc>
  - <https://github.com/bpd1069/bustermq/blob/master/.bazelversion>
  - <https://github.com/bpd1069/bustermq/blob/master/MODULE.bazel>
  - <https://github.com/bpd1069/bustermq/blob/master/BUILD.bazel>
  - <https://github.com/bpd1069/bustermq/blob/master/benchmark_pubsub.sh>
  - <https://github.com/bpd1069/bustermq/blob/master/examples/benchmarks/BUILD.bazel>
  - <https://github.com/bpd1069/bustermq/blob/master/examples/benchmarks/bench_pub_sub.zig>
  - <https://github.com/bpd1069/bustermq/blob/master/src/BUILD.bazel>
  - <https://github.com/bpd1069/bustermq/blob/master/src/bustermq.zig>
  - <https://github.com/bpd1069/bustermq/blob/master/src/server.zig>
  - <https://github.com/bpd1069/bustermq/blob/master/src/worker.zig>
  - <https://github.com/bpd1069/bustermq/blob/master/src/client.zig>
  - <https://github.com/bpd1069/bustermq/blob/master/src/io.zig>
  - <https://github.com/bpd1069/bustermq/blob/master/src/io_bundle.zig>
  - <https://github.com/bpd1069/bustermq/blob/master/src/mbuf.zig>
  - <https://github.com/bpd1069/bustermq/blob/master/src/message.zig>
  - <https://github.com/bpd1069/bustermq/blob/master/src/routing.zig>
  - <https://github.com/bpd1069/bustermq/blob/master/src/parser.zig>
  - <https://github.com/bpd1069/bustermq/blob/master/src/protocol.zig>
  - <https://github.com/bpd1069/bustermq/blob/master/src/rapidhash.zig>
  - <https://github.com/bpd1069/bustermq/blob/master/src/version.zig>
  - <https://github.com/bpd1069/bustermq/blob/master/src/testing/BUILD.bazel>
  - <https://github.com/bpd1069/bustermq/blob/master/third_party/non_module_deps.bzl>
  - <https://github.com/bpd1069/bustermq/blob/master/third_party/spsc_queue/repo.bzl>
  - <https://github.com/bpd1069/bustermq/blob/master/third_party/spsc_queue/spsc_queue.bazel>
  - <https://github.com/bpd1069/bustermq/blob/master/platforms/BUILD.bazel>
  - <https://github.com/bpd1069/bustermq/commits/master>
  - <https://github.com/bpd1069/bustermq/issues>
  - <https://github.com/bustermq/bustermq>
  - <https://github.com/bpd1069>
  - <https://github.com/jbdalido?tab=repositories>
  - <https://bustermq.sh/>
  - <https://hn.algolia.com/api/v1/items/46449812>
  - <https://hn.algolia.com/api/v1/search?query=bustermq>
  - <https://raw.githubusercontent.com/axboe/liburing/master/man/io_uring_enter.2>
  - <https://raw.githubusercontent.com/axboe/liburing/master/man/io_uring_prep_send_zc.3>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/bpd1069/bustermq`) · [data/wave5/enrich/raw/github_com_bpd1069_bustermq.json](../../../data/wave5/enrich/raw/github_com_bpd1069_bustermq.json) (enrichment confidence 0.75)

</details>
