# evio (Go epoll/kqueue event loop; Redis clone vs real Redis)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Concurrency runtimes](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `MIT` · 🔴 abandoned

> Go event-loop framework using raw epoll/kqueue; its toy Redis clone out-served Redis 4.0.2 on pipelined PING.

| | |
|---|---|
| **Beats** | Redis 4.0.2 (C, single-threaded ae event loop on epoll) answering PING_INLINE; the same table also holds Go net/http, fasthttp and a Go net echo server, which are Go baselines and not counted here |
| **Claimed result** | Requests per second, evio Redis clone vs real Redis 4.0.2 (benchmarks/out/redis{1,8,16}.txt, final redis-benchmark line): pipeline 1: 177,147.92 vs 176,991.14 (parity); pipeline 8: 1,285,347.00 vs 878,734.62 (about 1.46x, derived from page data); pipeline 16: 2,123,142.25 vs 879,507.50 (about 2.41x, derived from page data). The README itself only shows chart images and states the goal 'performs on par with Redis and Haproxy'. |
| **Workload** | redis-benchmark -t ping_inline -q -c 50 -n 1000000 with pipeline depth 1, 8 and 16 against the real redis-server and against the evio example Redis clone (examples/redis-server/main.go), both started with GOMAXPROCS=1 on localhost. |
| **Metric** | throughput |
| **Hardware** | EC2 c4.xlarge instance (CPU model not named in the repo), client and server on localhost over IPv4; run on 2017-11-04 per the log timestamps |
| **Compiler and flags** | Not stated. Go version not recorded (2017 snapshot); bench-redis.sh builds the clone with plain 'go build' and starts both servers with GOMAXPROCS=1. Real Redis is whatever 'redis-server' was on PATH (Redis 4.0.2 per the log, commit=00000000), started with only '--port 6392' (no config file); its build flags are not stated. Redis 4.0.2's own src/Makefile defaults to OPTIMIZATION?=-O2 with jemalloc, so a default build was -O2, not -O3. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Adoption** | 6.0k stars; foundation of Tile38 |
| **Last commit** | 2026-05-19 |
| **Links** | [repository](https://github.com/tidwall/evio) · [benchmark](https://raw.githubusercontent.com/tidwall/evio/HEAD/benchmarks/out/redis16.txt) |

## Verdict

In the author's 2017 run on an EC2 c4.xlarge (both servers started with GOMAXPROCS=1, client on the same box over IPv4 localhost, redis-benchmark -t ping_inline -c 50 -n 1000000), the evio example Redis clone tied Redis 4.0.2 at pipeline depth 1 (177,147.92 vs 176,991.14 req/s) and beat it at depth 8 (1,285,347 vs 878,735, about 1.46x) and depth 16 (2,123,142 vs 879,508, about 2.41x). The Go version and Redis build flags are not recorded, and only the inline PING command was measured.

## Use it when

- A custom line- or RESP-protocol TCP/unix-socket server in Go where handlers are short, non-blocking in-memory operations and clients pipeline requests.
- Many mostly-idle connections where goroutine-per-connection stacks are the memory cost you want to avoid (the README claims low memory use but gives no figures).
- Single-threaded or N-loop (NumLoops, SO_REUSEPORT, Random/RoundRobin/LeastConnections balancing) designs on Linux or BSD/macOS, including UDP and unix sockets on the same loop.
- Prototyping a Redis-protocol front end for a handful of commands, together with redcon's parser.

## Skip it when

- As a Redis replacement: the example clone has PING, ECHO, GET, SET, DEL, FLUSHDB, QUIT, SHUTDOWN and WAKE over a mutex-guarded Go map, with no persistence, expiry, replication or memory limits.
- Handlers that block (database calls, disk I/O, slow computation) stall every connection on the loop, and there is no TLS (open issue #28).
- Server-push designs built on Conn.Wake(): loopWake replaces pending output with c.out = append([]byte{}, out...) instead of appending (open issues #74 and #72, unfixed), and #46 and #40 report blocked writes and unreported write errors.
- Unpipelined request/response traffic, where it only tied Redis (177,148 vs 176,991 req/s at depth 1) because the client was the bottleneck.
- New long-lived projects: no code change since 2020-11-03 and 22 open issues; Tile38, which the README names as its target, now depends on redcon v1.6.2 and not on evio.

## How it is fast

Each loop is one goroutine around a level-triggered epoll_wait (64 events, 100 ms timeout) with a shared 64 KiB read buffer, and callbacks run inline with no goroutine per connection, no net.Conn and no channels. The speedup over Redis comes mostly from the clone's thin command path: redcon.ReadNextCommand walks the whole pipelined batch and PING appends '+PONG' to one output slice, written once. Redis 4.0.2's inline path does more per command: it copies the line (sdsnewlen), re-splits it into new sds strings (sdssplitargs), allocates argv and a robj per argument, and memmoves the rest of the query buffer (sdsrange). It then runs processCommand (lookupCommand, maxmemory check) and call(), which times every command with two ustime() calls and updates stats, slowlog and latency monitoring. evio itself costs two epoll_ctl calls per response (ModReadWrite, then ModRead after the write), so the event loop is not where it wins.

## Compared with alternatives

Against Redcon (same author, net-package goroutine-per-connection, maintained, what Tile38 uses), pick evio only if you specifically want a callback event loop with explicit loop count, SO_REUSEPORT and connection balancing, and can avoid Wake(). For plain TCP echo-style services, the Go net and Tokio echo entries are maintained baselines with fewer sharp edges.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | github.com/kavu/go_reuseport v1.5.0 (the example Redis clone also needs github.com/tidwall/redcon) |
| **Minimum toolchain** | Go 1.15 per go.mod; the Go version of the 2017 benchmark run is not recorded |
| **Platforms** | Linux (epoll) and darwin/freebsd/netbsd/openbsd/dragonfly (kqueue); other OSes, including Windows, fall back to emulation over the net package; open issue #81 (2026-07) reports an arm64 cross-build problem |
| **Thread safety** | Callbacks for one loop run on that loop's goroutine; with NumLoops &gt; 1 they run concurrently across loops and shared state needs your own locking (README); Conn.Wake() is the only Conn method meant for other goroutines and has open output-loss bugs |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw (like-for-like): the run compares a 9-command toy against full Redis 4.0.2 on PING_INLINE only. Redis plateaus at 878,735 and 879,508 req/s at depths 8 and 16 because of its per-command inline parse and call() bookkeeping (networking.c processInlineBuffer, server.c call()), not its event loop. Redcon, a Go net-package server with no evio, shows a similar 2.1-2.4x over Redis in its README (SET/GET, -P 512 -c 512), which suggests the gain comes from the thin command path rather than evio.
- Measurement is thin: one run per cell, with the redis-benchmark client on the same 4-vCPU c4.xlarge. The depth-16 clone figure covers 1,000,000 requests at 2.12M/s, about 0.47 s of measurement with two progress samples. Redis came from PATH with unknown build flags (commit=00000000) on a host warning about THP and somaxconn 128.
- Every read is copied into a fresh slice unless Options.ReuseInputBuffer is set (the clone does not set it); with reuse on, the Data input aliases a buffer shared by all connections on the loop and must not be retained.
- Record corrections: maintenance 'active' reflects only two README edits (2026-05-12, 2026-05-19); the last code commits are 'Update dependencies' (2020-11-03) and 'Add a deadline for epollwait' (2020-01-15). 'Foundation of Tile38' is historical: Tile38's current go.mod has redcon and no evio.

## Known shortcomings

- A small clone against the full Redis 4.0.2 (different work per command), PING_INLINE only, one run with the client on the same c4.xlarge, Redis build unknown (Makefile default -O2); the clone uses redcon's parser.
- Like-for-like flaw: the speed-up is a 9-command clone against full Redis 4.0.2 PING_INLINE; Redis 4.0.2's per-command parse and call() work (processInlineBuffer copy, sdssplitargs, robj allocations, two ustime() calls) explains its about 879k plateau, and Redcon (Go net package, no evio) shows a similar 2.1-2.4x, so the event loop is not the source. The depth-16 cell is about 0.47 s of measurement in a single run. The Wake() output-loss bug is confirmed in the loopWake code (#74, #72 open). Record corrections: maintenance 'active' was wrong (last code commit 2020-11-03; the 2026 commits touch the README only) and 'foundation of Tile38' is outdated (Tile38's go.mod has redcon v1.6.2, no evio).

## Caveats and trade-offs

The two servers do different amounts of work: the evio example is a tiny Redis-protocol clone (PING, ECHO, GET, SET, DEL, FLUSHDB, QUIT, SHUTDOWN, WAKE) over a Go map with a mutex, parsed by redcon.ReadNextCommand (so evio's clone reuses tidwall/redcon's parser), with no persistence, expiry, replication, statistics or full command table; PING is a string switch that appends +PONG. At pipeline depth 1 both are client-bound and equal (177,147.92 vs 176,991.14). Real Redis stays at about 878k-880k requests per second at depth 8 and 16 while the clone keeps climbing; the repo gives no explanation, and the most plausible one is Redis's per-command dispatch path rather than the language or event loop (verifier inference). Only PING_INLINE was benchmarked. One run per cell, no variance, and the redis-benchmark client shares the 4-vCPU instance with the server. Redis 4.0.2 is from 2017; its binary came from PATH with unstated build flags (Redis's Makefile default was -O2) and the log shows THP enabled and somaxconn 128 warnings. The README shows only chart PNGs for pipeline 1 and 8 and states the goal 'performs on par with Redis and Haproxy'; the depth-16 numbers come from benchmarks/out/redis16.txt. The clone at HEAD differs from the 2017 build that was measured (its 'redis server started' log line has since gained a loops field). Latest two commits are README edits (2026-05-12, 2026-05-19) and the one before is from 2022-05-14. [retier] Redis 4.0.2's per-command parse and call() work (processInlineBuffer copy, sdssplitargs, robj allocations, two ustime() calls) explains its about 879k plateau, and Redcon (Go net package, no evio) shows a similar 2.1-2.4x, so the event loop is not the source. The depth-16 cell is about 0.47 s of measurement in a single run. The Wake() output-loss bug is confirmed in loopWake (#74, #72 open). 'Foundation of Tile38' is outdated: Tile38's go.mod has redcon v1.6.2, no evio.

Not a drop-in replacement for Go net or net/http (the README says so). Handlers run inside the event-loop goroutines and must not block. Linux epoll and BSD/macOS kqueue only, with a net-package fallback elsewhere. Calling it from C++ means a separate Go process.

## Maintenance

Dormant rather than active: the last code change was 2020-11-03 and 22 issues are open, including unfixed Wake() output-loss bugs (#72, #74); it is MIT and small enough to vendor, but treat the Redis comparison as evidence about a thin command path, not as a faster Redis.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party raw logs benchmarks/out/redis{1,8,16}.txt from the public script benchmarks/bench-redis.sh show real Redis 4.0.2 and the evio clone (examples/redis-server/main.go) under the same redis-benchmark command, with every number in the record matching the final lines; the Go version, the Redis build and flags, and the CPU model (only 'ec2 c4.xlarge') are not stated, so not A, and no independent run exists, so not B.
- **Verifier notes:** Numbers verified exactly in the raw logs; keep at C. Shortcomings: clone vs full Redis (different work per command), PING_INLINE only, single run, client on the same 4-vCPU box, Redis build unknown (default -O2), 2017 snapshot, no mechanism stated; the clone uses redcon's parser, so evio and redcon share code.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`, `maintenance_status`
- **Shortcomings recorded by:** verifier batch-33 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/tidwall/evio/HEAD/benchmarks/out/redis1.txt>
  - <https://raw.githubusercontent.com/tidwall/evio/HEAD/benchmarks/out/redis8.txt>
  - <https://raw.githubusercontent.com/tidwall/evio/HEAD/benchmarks/out/redis16.txt>
  - <https://raw.githubusercontent.com/tidwall/evio/HEAD/benchmarks/bench-redis.sh>
  - <https://raw.githubusercontent.com/tidwall/evio/HEAD/benchmarks/README.md>
  - <https://raw.githubusercontent.com/tidwall/evio/HEAD/README.md>
  - <https://raw.githubusercontent.com/tidwall/evio/HEAD/examples/redis-server/main.go>
  - <https://raw.githubusercontent.com/tidwall/evio/HEAD/LICENSE>
  - <https://github.com/tidwall/evio>
  - <https://github.com/tidwall/evio/commits>
  - <https://raw.githubusercontent.com/redis/redis/4.0.2/src/Makefile>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/tidwall/evio/HEAD/README.md>
  - <https://raw.githubusercontent.com/tidwall/evio/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/tidwall/evio/HEAD/go.mod>
  - <https://raw.githubusercontent.com/tidwall/evio/HEAD/evio.go>
  - <https://raw.githubusercontent.com/tidwall/evio/HEAD/evio_unix.go>
  - <https://raw.githubusercontent.com/tidwall/evio/HEAD/evio_std.go>
  - <https://raw.githubusercontent.com/tidwall/evio/HEAD/evio_other.go>
  - <https://raw.githubusercontent.com/tidwall/evio/HEAD/internal/internal_linux.go>
  - <https://raw.githubusercontent.com/tidwall/evio/HEAD/internal/internal_bsd.go>
  - <https://raw.githubusercontent.com/tidwall/evio/HEAD/benchmarks/bench-redis.sh>
  - <https://raw.githubusercontent.com/tidwall/evio/HEAD/benchmarks/bench.sh>
  - <https://raw.githubusercontent.com/tidwall/evio/HEAD/benchmarks/README.md>
  - <https://raw.githubusercontent.com/tidwall/evio/HEAD/benchmarks/out/redis1.txt>
  - <https://raw.githubusercontent.com/tidwall/evio/HEAD/benchmarks/out/redis8.txt>
  - <https://raw.githubusercontent.com/tidwall/evio/HEAD/benchmarks/out/redis16.txt>
  - <https://raw.githubusercontent.com/tidwall/evio/HEAD/examples/redis-server/main.go>
  - <https://github.com/tidwall/evio/issues>
  - <https://github.com/tidwall/evio/issues/72>
  - <https://github.com/tidwall/evio/issues/74>
  - <https://github.com/tidwall/evio/commits>
  - <https://raw.githubusercontent.com/redis/redis/4.0.2/src/networking.c>
  - <https://raw.githubusercontent.com/redis/redis/4.0.2/src/server.c>
  - <https://raw.githubusercontent.com/tidwall/redcon/HEAD/README.md>
  - <https://raw.githubusercontent.com/tidwall/tile38/HEAD/go.mod>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/tidwall/evio`) · [data/wave14/enrich/raw/github_com_tidwall_evio.json](../../../data/wave14/enrich/raw/github_com_tidwall_evio.json) (enrichment confidence 0.7)

</details>
