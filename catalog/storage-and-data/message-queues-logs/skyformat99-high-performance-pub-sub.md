# High-performance pub/sub (uWS broadcast-coalescing prototype)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Message queues and logs](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Zlib` · 🔴 abandoned

> 150-line C++11 µWebSockets demo of broadcast coalescing for pub/sub fan-out; claims 89 ms vs Redis pub/sub's 5 s.

| | |
|---|---|
| **Beats** | Redis pub/sub |
| **Claimed result** | Completes in 89 ms vs Redis pub/sub's 5 s for the same problem size - 'more than 50x faster than Redis pub/sub' (README also claims &gt;3000x vs a Socket.IO based implementation, 4.5 min) |
| **Workload** | Broadcast-coalescing pub/sub prototype on µWebSockets, run against the deepstream.io event benchmark, compared with Redis pub/sub on the same problem size. The in-repo redisBenchmark.cpp (hiredis async plus libuv, localhost) opens 9,000 subscribers and 1,000 publishers; each publisher sends a 1-byte message to one channel, for 9M deliveries per round, and it times the round. Message count and size come from that file; the README text does not state them. |
| **Metric** | throughput |
| **Adoption** | 14 stars |
| **Last commit** | 2016-11-25 |
| **Links** | [repository](https://github.com/skyformat99/High-performance-pub-sub) · [benchmark](https://github.com/skyformat99/High-performance-pub-sub/blob/master/README.md) |

## Verdict

The README reports 89 ms per fan-out round, against 5 s for Redis pub/sub (\~56x) and 4.5 min for Socket.IO. The uWS side is 10,000 localhost connections with 1,000 publications of a 16-byte deepstream event, about 10M deliveries; deepstream.io-benchmarks' Socket.IO row for that size is 274,335.6 ms. The Redis side, in redisBenchmark.cpp, is 9,000 SUBSCRIBE plus 1,000 PUBLISH connections with a 1-byte payload, 9M deliveries. That works out to roughly 112M vs 1.8M deliveries/s (derived). No hardware, compiler, flags or Redis version are given, and no raw uWS-side output is published. The two timed runs also include very different client work: 10,000 coalesced frames counted by length versus 9M separate pub/sub messages parsed by hiredis.

## Use it when

- You are writing your own WebSocket fan-out server (chat rooms, game lobbies, live dashboards) and want a small reference for batching many small publications into one frame per subscriber.
- Bursty rooms: many clients publish into one busy room at about the same moment, then the loop goes quiet, and per-message framing and send calls are the bottleneck.
- Your application messages delimit themselves (a record separator like deepstream's 0x1E, or fixed-size messages), so clients can split a frame that holds several messages.
- You care about throughput more than per-message latency. Every message waits at least until a loop iteration with no new publications.
- You want to reproduce the 2016 Socket.IO / deepstream.io / Redis fan-out comparison. The Redis client is in this repo; the WebSocket client is deepstream.io-benchmarks' eventBenchmark.cpp.

## Skip it when

- You need a broker. There are no topics or multiple rooms, no subscribe/unsubscribe, persistence, acks, auth, clustering or Redis protocol. Use Redis, NATS or current µWebSockets' built-in pub/sub instead.
- Sustained load where every loop iteration receives at least one publication. The flush condition never fires, and there is no maximum batch size or deadline, so latency and the shared buffer grow without bound.
- Clients need message boundaries. A batch goes out as a single TEXT frame of payloads joined with no separator.
- You are on current µWebSockets. The code targets the removed 2016 uWS::Hub API (about v0.12) with the libuv backend, so it won't compile against modern uWS without a port.
- Many different publishers per batch with large batches. Each sender's custom message is built with substr/append copies of the shared buffer, so copying grows with senders × batch bytes.

## How it is fast

It uses broadcast coalescing: publications are appended to one shared per-room buffer, and the batch is flushed only on a libuv loop iteration that brought no new publications. A uv_prepare hook arms a 1 ms no-op timer so epoll_wait wakes up, and a uv_check hook does the flush. On flush the buffer is framed once with µWS prepareMessage and sent verbatim with sendPrepared to every listen-only socket, so N publications to M subscribers cost about M frames and sends instead of N×M. Sockets that published in the batch instead get a copy with their own bytes cut out ('gaps'), found by walking a sorted socket vector in lockstep with a std::map of senders.

## Compared with alternatives

Pick it only as a design reference for coalescing fan-out inside your own WebSocket server. For something you can deploy, use Wisp or NATS JetStream (real brokers with clients, subjects and published delivery-rate comparisons) or Eclipse Mosquitto (MQTT).

## Integration

| | |
|---|---|
| **Form** | source-drop (a code block in README.md; the repo has no build files and no .cpp for the server) |
| **Dependencies** | µWebSockets of the v0.12 era (uWS::Hub, WebSocket&lt;SERVER&gt;::prepareMessage/sendPrepared/finalizeMessage, getPollHandle) built on its default libuv backend, because the code calls uv_prepare, uv_check and uv_timer, which uWS's optional micro-uv epoll shim (USE_MICRO_UV) does not provide. That uWS also needs OpenSSL and zlib. The Redis harness needs hiredis (async API plus the libuv adapter) and libuv. |
| **Minimum toolchain** | C++11 (stated in the README; the uWS v0.12 Makefile builds with g++ -std=c++11 -O3). No compiler versions are given. The companion benchmark client's README gives Ubuntu 16.04 build steps. |
| **Platforms** | Not documented for the prototype. The uWS v0.12 it depends on has Linux and Darwin Makefile targets, and the published runs were on localhost (Linux, per the Ubuntu 16.04 instructions). |
| **Thread safety** | None. It is single-threaded: one global Room is mutated from event-loop callbacks. |
| **Drop-in for the baseline** | no |

## Gotchas

- There is no disconnection handler, so closed sockets stay in Room::sockets and keep getting sends. In uWS v0.12 a WebSocket is a thin wrapper around a raw uv_poll_t\*, so reusing that handle after close is unsafe.
- The lockstep walk assumes every publisher is also in the sorted subscriber vector. If a sender is not subscribed, the index stops advancing, and every later sender in that batch gets the shared frame, including its own messages.
- The benchmark client never parses a batched frame. It counts deliveries as frame length / 16, which works only because every deepstream test event is exactly 16 bytes.
- addSubscriber calls push_back and then re-sorts the whole vector on every connect, and broadcast() copies each map entry by value. The author's own comments mark both as unoptimized.

## Known shortcomings

- A re-upload of Alex Hultman's uWS broadcast-coalescing prototype (the original repo is 404); the benchmark is 9k subscribers x 1k publishers with 1-byte messages vs Redis (not a listed baseline).
- The server is a 150-line README code block with no build files, needing 2016-era uWS \~v0.12 (it does not compile on modern uWS). It flushes only on a loop iteration with no new publishes, so sustained load never flushes (unbounded latency and buffer); a batch is one frame of concatenated payloads with no separator; no disconnect handler; one hard-coded room; no Redis API. The benchmark's client work is unequal (10k frames counted by length vs 9M messages parsed by hiredis), with no hardware/flags/Redis version. Modern uWS's TopicTree pub/sub (Apache-2.0) is the maintained alternative.

## Caveats and trade-offs

No hardware, compiler or flags are given for either side. Only the Redis-side harness is in the repo; the uWS side relies on the external deepstream.io-benchmarks client. The ratios (&gt;50x vs Redis, &gt;3000x vs Socket.IO) are first-party and unreproduced. All commits are authored by Alex Hultman (uWebSockets author, Nov 2016), so this is a non-fork re-upload of his repo; the likely original, alexhultman/High-performance-pub-sub, returns 404. The Zlib license has no patent grant.

Single C++11 'braindump' file demonstrating a broadcast-batching technique on top of uWebSockets, not a full message broker (no persistence, clustering, or wire-protocol compatibility); problem size and hardware are unspecified so the ratio can't be independently checked.

## Maintenance

Abandoned since the last commit on 2016-11-25. This copy re-uploads Alex Hultman's repo (the original URL now returns 404; one typo-fix commit comes from a contributor). It is Zlib-licensed and small enough to copy, but it builds only against 2016-era µWebSockets. The maintained path is current µWebSockets' own Apache-2.0 pub/sub (src/TopicTree.h), which also queues per-subscriber publishes and drains them in batches.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README claim of 89 ms vs Redis's 5 s. The Redis-side benchmark code is in the repo (redisBenchmark.cpp) and the uWS side points to deepstream.io-benchmarks, but no hardware, compiler or flags are given, and the &gt;50x ratio with unstated flags is capped at C.
- **Verifier notes:** The README numbers match the record (89 ms vs 5 s for Redis, 4.5 min for Socket.IO). The metadata checks out: Zlib (LICENSE text confirmed), 14 stars, last commit 2016-11-25, not archived, not a GitHub fork. The workload is corrected because redisBenchmark.cpp does state the problem size.
- **Fields the verifier corrected:** `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/skyformat99/High-performance-pub-sub>
  - <https://github.com/skyformat99/High-performance-pub-sub/blob/master/README.md>
  - <https://github.com/skyformat99/High-performance-pub-sub/blob/master/redisBenchmark.cpp>
  - <https://github.com/skyformat99/High-performance-pub-sub/blob/master/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/skyformat99/High-performance-pub-sub>
  - <https://github.com/skyformat99/High-performance-pub-sub/blob/master/README.md>
  - <https://github.com/skyformat99/High-performance-pub-sub/blob/master/redisBenchmark.cpp>
  - <https://github.com/skyformat99/High-performance-pub-sub/blob/master/LICENSE>
  - <https://github.com/skyformat99/High-performance-pub-sub/commits/master>
  - <https://github.com/skyformat99/High-performance-pub-sub/issues?q=is%3Aissue>
  - <https://github.com/alexhultman/High-performance-pub-sub>
  - <https://github.com/uNetworking/High-performance-pub-sub>
  - <https://github.com/deepstreamIO/deepstream.io-benchmarks>
  - <https://github.com/deepstreamIO/deepstream.io-benchmarks/blob/master/README.md>
  - <https://github.com/deepstreamIO/deepstream.io-benchmarks/blob/master/eventBenchmark.cpp>
  - <https://github.com/deepstreamIO/deepstream.io-benchmarks/blob/master/Makefile>
  - <https://github.com/deepstreamIO/deepstream.io-benchmarks/blob/master/runBenchmarks>
  - <https://github.com/deepstreamIO/deepstream.io-benchmarks/blob/master/socketio.js>
  - <https://github.com/deepstreamIO/deepstream.io-benchmarks/blob/master/deepstream2.csv>
  - <https://github.com/deepstreamIO/deepstream.io-benchmarks/blob/master/deepstream2rc.csv>
  - <https://github.com/deepstreamIO/deepstream.io-benchmarks/blob/master/socketio.csv>
  - <https://github.com/uNetworking/uWebSockets/tags>
  - <https://github.com/uNetworking/uWebSockets/blob/v0.12.0/src/WebSocket.h>
  - <https://github.com/uNetworking/uWebSockets/blob/v0.12.0/src/Hub.h>
  - <https://github.com/uNetworking/uWebSockets/blob/v0.12.0/src/Node.h>
  - <https://github.com/uNetworking/uWebSockets/blob/v0.12.0/src/uUV.h>
  - <https://github.com/uNetworking/uWebSockets/blob/v0.12.0/src/Networking.h>
  - <https://github.com/uNetworking/uWebSockets/blob/v0.12.0/Makefile>
  - <https://github.com/uNetworking/uWebSockets/blob/master/src/TopicTree.h>
  - <https://github.com/uNetworking/uWebSockets/blob/master/README.md>
  - <https://news.ycombinator.com/item?id=12906228>
  - <https://hn.algolia.com/api/v1/search?query=High-performance-pub-sub&restrictSearchableAttributes=url>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/skyformat99/high-performance-pub-sub`) · [data/wave6/enrich/raw/github_com_skyformat99_high_performance_pub_sub.json](../../../data/wave6/enrich/raw/github_com_skyformat99_high_performance_pub_sub.json) (enrichment confidence 0.7)

</details>
