# Redcon (Go Redis-compatible server framework; clone vs real Redis)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Concurrency runtimes](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `MIT` · 🟢 active

> Go framework for writing Redis-protocol servers; its 136-line map clone out-ran redis-server about 2x on a 2016 laptop pipeline test.

| | |
|---|---|
| **Beats** | Redis (C, single-threaded, started as 'redis-server --port 6379 --appendonly no'; version not stated) |
| **Claimed result** | README table as printed: SET 2,018,570.88 (Redcon, one thread) vs 941,265.12 (Redis), about 2.14x; GET 2,403,846.25 vs 1,189,909.50, about 2.02x; multi-threaded GET 3,993,610.25 (about 3.36x). The Redis row dates from 2016-08-20 and was never re-run while the Redcon rows were re-measured on 2016-09-07 and after the 2016-09-18 rewrite (cross-run); the same-day ratios were 1.40x SET and 1.30x GET (derived from page data), and issue #3's network test at GOMAXPROCS=1 gives Redcon 687,994.50 vs Redis 622,045.25 (about 1.1x). |
| **Workload** | redis-benchmark -t set,get -n 10000000 -q -P 512 -c 512 against real Redis ('redis-server --port 6379 --appendonly no') and against example/clone.go (Go map with an RWMutex; PING, QUIT, SET, GET, SETNX, DEL, PUBLISH, SUBSCRIBE/PSUBSCRIBE, DETACH and a blank CONFIG stub that exists only so redis-benchmark runs), Redcon run with GOMAXPROCS=1 and GOMAXPROCS=0. No -r flag is passed, so redis-benchmark uses one fixed key for every SET and GET with its default 3-byte value. |
| **Metric** | throughput |
| **Hardware** | MacBook Pro 15-inch, 2.8 GHz Intel Core i7 (README), client and server on one laptop |
| **Compiler and flags** | Go 1.7 via 'go run' (default flags); Redis version and build flags not stated (Redis's own Makefile defaulted to -O2, checked for 4.0.2). |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Adoption** | 2.3k stars |
| **Last commit** | 2026-07-22 |
| **Links** | [repository](https://github.com/tidwall/redcon) · [benchmark](https://github.com/tidwall/redcon) |

## Verdict

redis-benchmark (-t set,get -n 10000000 -P 512 -c 512, one fixed key, 3-byte values) against the example Go-map clone versus redis-server with AOF off (version not stated) on a 2.8 GHz Core i7 MacBook Pro with Go 1.7: single-threaded Redcon SET 2.02M vs 0.94M rps (about 2.1x) and GET 2.40M vs 1.19M (about 2.0x), but the Redis row is from a 2016-08-20 run and the Redcon rows from a 2016-09-18 re-run.

## Use it when

- You need a custom service (spatial index, proxy, cache front, test double) that existing Redis clients can talk to without a new client library.
- Your service is written in Go and you want the goroutine-per-connection model with plain blocking-style handlers.
- Read-heavy, deeply pipelined traffic from many connections on a multicore box: the README's multi-threaded GET (3,993,610.25 rps) scales past the single-threaded run (2,403,846.25).
- You want Redis-compatible pub/sub, TLS or unix-socket serving out of the box.

## Skip it when

- You actually need Redis: no persistence, expiry, replication, cluster or data types come with it; the benchmarked clone has SET, GET, SETNX, DEL, PING, QUIT, pub/sub and a blank CONFIG stub.
- Facing untrusted clients without a length guard: the parser has no cap on multibulk count or bulk length, and crafted lengths can pin a core or crash the process (see gotchas).
- Write-heavy multi-core workloads behind one global lock: the README's multi-threaded SET (1,944,390.38 rps) is slower than single-threaded (2,018,570.88).
- A C++ codebase that wants an in-process library: this is Go and runs as a separate server or sidecar; the author's C port tidwall/redcon.c is the in-process option.
- Tail-latency-bound services: the README publishes throughput only, no latency percentiles.

## How it is fast

Each connection gets its own goroutine that reads into a growable 4 KB buffer, parses every complete command in that buffer in one pass, runs the handler for each, appends all replies to one byte slice and flushes it with a single write per batch, so a 512-deep pipeline costs a handful of syscalls. With GOMAXPROCS above 1 the Go scheduler spreads connections across cores, which single-threaded Redis cannot do. In the benchmark the handler is a map lookup under a sync.RWMutex with no persistence, expiry or data-type machinery, so most of the gap is less work per command rather than a faster event loop; the README itself names no mechanism.

## Compared with alternatives

Pick redcon over evio when you want a simple goroutine-per-connection handler API with pub/sub, TLS and Detach and your connection count is moderate; evio (an epoll/kqueue event loop that reuses redcon's ReadNextCommand parser) only matched Redis at pipeline 1 in its own table. Neither replaces Redis; both are frameworks for your own RESP server.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | github.com/tidwall/btree v1.1.0, github.com/tidwall/match v1.1.1 (used by PubSub) |
| **Minimum toolchain** | Go 1.20 (go.mod since commit 7776fcd, 2026-07-22, which uses unsafe.String) |
| **Platforms** | any Go target with the net package (TCP, unix sockets, TLS) |
| **Thread safety** | Handlers run concurrently, one goroutine per connection, so shared state needs your own locking (the example uses sync.RWMutex); a Conn is meant to be used inside its handler, and a detached connection must be flushed and closed by its new owner. |
| **Drop-in for the baseline** | no |

## Gotchas

- The comparison is cross-run: the Redis row (SET 941,265.12, GET 1,189,909.50) was published on 2016-08-20 (commit 9e38e36) and never re-run, while the Redcon rows were re-measured twice, at SET 3,119,151.50 on 2016-09-07 (commit 4276409) and SET 2,018,570.88 after the 2016-09-18 API rewrite (commit 67c21aa). The 2.1x ratios pair runs a month apart on different code; the original same-day ratios were 1,320,655.00 vs 941,265.12 for SET (about 1.40x, derived) and 1,552,354.25 vs 1,189,909.50 for GET (about 1.30x, derived).
- Parser robustness, found by reading redcon.go and resp.go at HEAD (not executed): readCommands has no upper bound on the multibulk count and its 'for j := 0; j &lt; count; j++' loop keeps incrementing past the buffer without breaking, so '\*1000000000000000000\r\n' spins the connection goroutine for about 1e18 iterations; a bulk length near MaxInt64 makes 'i+size+2' overflow negative and index the buffer out of range, an unrecovered panic that ends the process (redcon.go has no recover). The exported ReadNextCommand (used by evio's Redis example) checks 'count &lt;= 0' instead of the bulk length n, so '\$-2' passes and 'packet[i:i+n]' panics.
- Stored arguments are sub-slices of a per-command copy of the whole raw RESP message, so keeping cmd.Args[2] in a map (as the clone does) retains the key and framing bytes too, and every command costs one allocation.
- Over a real network the gap shrinks: in issue #3 (2016) the author's two-droplet test gave single-threaded Redcon 687,994.50 rps vs Redis 622,045.25 (about 1.1x, derived) at -P 128 -c 128; the benchmark clone's CONFIG stub reads cmd.Args[2] unchecked, so a two-argument CONFIG command panics it.

## Known shortcomings

- A Go 1.7 era laptop run with the Redis version unknown and one fixed key (no -r); the multi-threaded SET is slower than single-threaded; no mechanism stated.
- Cross-run comparison: the Redis row (SET 941,265.12 / GET 1,189,909.50) was published 2016-08-20 (commit 9e38e36) and never re-run, while the Redcon rows were re-measured twice (3,119,151.50 on 2016-09-07 in 4276409, then 2,018,570.88 after the 2016-09-18 API rewrite 67c21aa); the same-day ratios were only 1.40x SET and 1.30x GET (derived). Issue #3's network test at GOMAXPROCS=1: Redcon 687,994.50 vs Redis 622,045.25 (about 1.1x). Security, from reading the code: readCommands puts no cap on the multibulk count, so \*1000000000000000000 spins a goroutine for about 1e18 iterations; a bulk length near MaxInt64 overflows i+size+2 into an unrecovered panic that crashes the process; the exported ReadNextCommand checks count &lt;= 0 instead of n, so \$-2 panics (evio's Redis example uses it); the clone's CONFIG stub panics on a 2-argument CONFIG.

## Caveats and trade-offs

First-party README numbers from the Go 1.7 era (2016) with no Redis version, no compiler, no run count and no variance. The Redis command disables the append-only file but not RDB snapshots; because redis-benchmark ran without -r, the dataset is a single key, so any snapshot fork during the 10M-command SET run would be cheap and this is a minor concern. The Go clone implements a handful of commands over a bare map behind an RWMutex, while Redis runs its full command dispatch, so the two servers do different work per command and the gap is mostly per-command overhead, not language (verifier inference). Client, server and OS share one laptop; 512 connections and pipeline depth 512 favour batch throughput over latency. Multi-threaded Redcon SET (1,944,390.38) is slower than single-threaded (2,018,570.88), consistent with every SET taking the global mutex. No latency numbers. The README names no mechanism. The redcon parser has changed since the measurement (it copies each command's raw bytes, and a 2026-07-22 commit reworked number parsing), so the numbers predate the current code. Redis-vs-Go comparison, not a runtime-level language claim. evio's Redis example reuses redcon's parser. [retier] Cross-run table (Redis row 2016-08-20, Redcon rows re-measured twice afterwards); same-day ratios 1.40x/1.30x. Security, from reading the code: readCommands caps neither the multibulk count (a huge count spins a goroutine) nor a bulk length near MaxInt64 (i+size+2 overflows into an unrecovered panic); the exported ReadNextCommand checks count &lt;= 0 instead of n, so \$-2 panics (evio's Redis example uses it).

Go library, so a C++ project would run it as a separate server or sidecar. The clone in the benchmark has none of Redis's persistence, expiry, data structures or replication. Each connection is served by Go's net package with goroutines.

## Maintenance

Active (last commit 2026-07-22, a number-parsing fix), MIT, single-package Go module that is easy to vendor; the headline numbers are a 2016 first-party cross-run comparison (CLAUDE.md precedent sends cross-run comparisons to D), and the parser should get length limits before it faces untrusted clients.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README Benchmarks section shows the exact redis-server and redis-benchmark commands and the SET/GET numbers for Redis, single-threaded Redcon and multi-threaded Redcon, all matching the record; the clone code (example/clone.go) is public but the Redis version and build flags are missing and the CPU is only '2.8 GHz Intel Core i7', so not A, and there is no independent run.
- **Verifier notes:** README numbers verified exactly; keep at C. Shortcomings: tiny clone vs full Redis, Redis version and build unknown (Makefile default -O2), single laptop run from the Go 1.7 era, single fixed key, multi-threaded SET slower than single-threaded, no mechanism stated.
- **Fields the verifier corrected:** `workload`, `compiler_and_flags`, `caveats`, `claimed_speedup`
- **Shortcomings recorded by:** verifier batch-33 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/tidwall/redcon>
  - <https://github.com/tidwall/redcon/commits>
  - <https://raw.githubusercontent.com/tidwall/redcon/HEAD/README.md>
  - <https://raw.githubusercontent.com/tidwall/redcon/HEAD/example/clone.go>
  - <https://raw.githubusercontent.com/tidwall/redcon/HEAD/redcon.go>
  - <https://raw.githubusercontent.com/tidwall/redcon/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/redis/redis/4.0.2/src/Makefile>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/tidwall/redcon/HEAD/README.md>
  - <https://raw.githubusercontent.com/tidwall/redcon/HEAD/redcon.go>
  - <https://raw.githubusercontent.com/tidwall/redcon/HEAD/resp.go>
  - <https://raw.githubusercontent.com/tidwall/redcon/HEAD/example/clone.go>
  - <https://raw.githubusercontent.com/tidwall/redcon/HEAD/go.mod>
  - <https://raw.githubusercontent.com/tidwall/redcon/HEAD/LICENSE>
  - <https://github.com/tidwall/redcon/commits/master/redcon.go>
  - <https://github.com/tidwall/redcon/commits/master/redcon.go?after=7e866b48ea78ec2a060fa30cd945052e4bfa5031+34>
  - <https://github.com/tidwall/redcon/commits/master/README.md>
  - <https://raw.githubusercontent.com/tidwall/redcon/9e38e36/README.md>
  - <https://raw.githubusercontent.com/tidwall/redcon/408b582/README.md>
  - <https://raw.githubusercontent.com/tidwall/redcon/a88a6c7/README.md>
  - <https://raw.githubusercontent.com/tidwall/redcon/4276409/README.md>
  - <https://raw.githubusercontent.com/tidwall/redcon/0ec132a/README.md>
  - <https://raw.githubusercontent.com/tidwall/redcon/67c21aa/README.md>
  - <https://raw.githubusercontent.com/tidwall/redcon/ffcf137/README.md>
  - <https://raw.githubusercontent.com/tidwall/redcon/142cd0b/README.md>
  - <https://raw.githubusercontent.com/tidwall/redcon/b110d63/README.md>
  - <https://raw.githubusercontent.com/tidwall/redcon/4276409/redcon.go>
  - <https://raw.githubusercontent.com/tidwall/redcon/0ec132a/redcon.go>
  - <https://raw.githubusercontent.com/tidwall/redcon/67c21aa/redcon.go>
  - <https://raw.githubusercontent.com/tidwall/redcon/bd8eb49/redcon.go>
  - <https://raw.githubusercontent.com/tidwall/redcon/6f1afba/redcon.go>
  - <https://raw.githubusercontent.com/tidwall/redcon/ffcf137/redcon.go>
  - <https://raw.githubusercontent.com/tidwall/redcon/142cd0b/redcon.go>
  - <https://raw.githubusercontent.com/tidwall/redcon/b110d63/redcon.go>
  - <https://github.com/tidwall/redcon/commit/7776fcd>
  - <https://github.com/tidwall/redcon/issues?q=is%3Aissue+panic+OR+crash+OR+DoS+OR+performance>
  - <https://github.com/tidwall/redcon/issues/3>
  - <https://raw.githubusercontent.com/tidwall/evio/HEAD/examples/redis-server/main.go>
  - <https://raw.githubusercontent.com/tidwall/redcon.c/HEAD/README.md>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/tidwall/redcon`) · [data/wave14/enrich/raw/github_com_tidwall_redcon.json](../../../data/wave14/enrich/raw/github_com_tidwall_redcon.json) (enrichment confidence 0.75)

</details>
