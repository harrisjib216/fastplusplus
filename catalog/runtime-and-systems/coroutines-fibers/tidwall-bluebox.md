# bluebox

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Coroutines and fibers](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C` · `no license` · 🟡 stale

> Toy Redis-protocol server (SET/GET/DEL/PING) showcasing Neco coroutines; first-party memtier run shows 2.4x redis-server throughput.

| | |
|---|---|
| **Beats** | redis-server (its epoll event loop) |
| **Claimed result** | Totals 493,346.12 ops/sec (Bluebox) vs 207,734.88 ops/sec (redis-server), about 2.4x (derived from page data); average latency 0.40524 ms vs 0.96274 ms, p99 0.46300 ms vs 1.87100 ms, p99.9 0.74300 ms vs 3.16700 ms. |
| **Workload** | memtier_benchmark with default options (only --hide-histogram and the port given) against a local server on one machine; by the table's ops/sec about 9% SET and 91% GET (18,903.87 of 207,734.88 ops/sec for Redis, a 1:10 ratio), every GET counted as a miss. Redis started with --appendonly no --save ""; Bluebox serving SET/GET/DEL/PING (plus QUIT, DBSIZE, KEYS) on port 9999. The Redis run uses memtier_benchmark from PATH and the Bluebox run uses ./memtier_benchmark, a local binary, so the two runs may have used different client builds. |
| **Metric** | throughput |
| **Hardware** | Linux, AMD Ryzen 9 5950X 16-Core (README); kernel, client/server placement and core pinning not stated. |
| **Compiler and flags** | Makefile builds with \${CC} -O3 -g \${CFLAGS} src/\*.c; compiler name and version not stated, Redis version and build not stated, memtier_benchmark version not stated. |
| **Adoption** | 29 stars |
| **Last commit** | 2025-05-27 |
| **Links** | [repository](https://github.com/tidwall/bluebox) · [benchmark](https://github.com/tidwall/bluebox) |

## Verdict

One first-party memtier_benchmark run with default options (4 threads x 50 connections, pipeline 1, 1:10 SET:GET, 32-byte values) on Linux with an AMD Ryzen 9 5950X gave Bluebox 493,346 ops/sec at 0.405 ms average (p99 0.463 ms) against redis-server with persistence off at 207,735 ops/sec and 0.963 ms (p99 1.871 ms), about 2.4x (derived from page data). Compiler, Redis and memtier versions are unstated, Bluebox used two extra Neco write threads, and every GET was a miss because of memtier's shared default seed.

## Use it when

- Reading or adapting a coroutine-per-connection RESP or line-protocol server in C on Neco: the read-args, dispatch and flush-on-empty-buffer loop in src/bluebox.c is short and clear.
- Reproducing the Neco versus redis-server comparison on Linux with a fairer harness (memtier --distinct-client-seed or --randomize, a key range that produces hits, pinned client and server cores, Redis io-threads matched to Neco's I/O workers).
- Local experiments on how Neco's Linux write-worker offload changes latency with hundreds of connections and one request in flight each (memtier's default pipeline 1).
- A throwaway local endpoint for client code that only issues GET/SET/DEL/PING, when Redis features and licensing do not matter.

## Skip it when

- As a Redis replacement: only SET (no EX/NX options), GET, DEL, PING, QUIT, DBSIZE and KEYS (which ignores its pattern); no persistence, expiry, eviction or maxmemory, auth, TLS, replication, transactions or non-string types.
- In shipped code: the repository has no LICENSE file, so Bluebox's own code carries no grant; take the MIT-licensed neco.c and hashmap.c from their own repositories instead.
- On untrusted networks: the key hashmap uses fixed seeds 0,0 (hash flooding), each bulk argument may be up to 500 MB with no memory cap, and DEL leaks the stored key and value buffers.
- When you need multi-core scaling: one Neco scheduler serves all connections (Neco lists a scalable multithreaded runtime as a non-goal); only write() calls leave that thread.
- As evidence that Neco beats an epoll loop: the benchmark compares whole servers with different feature sets and thread counts, not event loops.

## How it is fast

Each connection is a blocking-style read/dispatch loop inside a Neco coroutine (llco assembly context switch, about 11 ns per the Neco README) over a 4 KiB buffered neco_stream; replies are buffered and flushed when the read buffer drains or after 1,000 pipelined commands. Keys live in tidwall's open-addressing Robin Hood hashmap keyed with xxHash3. On Linux the vendored Neco enables write workers by default (NECO_USEWRITEWORKERS, NECO_MAXIOWORKERS 2), so every write() is handed to one of two I/O threads while the scheduler thread re-arms an EPOLLONESHOT registration and reads; the server therefore spreads its syscalls over up to three threads, against one thread for default redis-server. That offload and the much smaller per-command work (no ACL checks, stats, keyspace notifications, expiry or object encoding) likely explain most of the gap; the README isolates neither from coroutine switching.

## Compared with alternatives

Pick Bluebox only as a worked example of a Neco-based network server; for the coroutine library itself take Neco (same author, MIT, about 11 ns switches, no baseline), libdill or libmill for C coroutines with published switch costs against Go and Boost.Context, or iqiyi libfiber if you want a server-level QPS comparison against libco.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none beyond libc and pthreads; vendors neco.c/neco.h (Neco with llco and sco embedded) and tidwall hashmap.c/hashmap.h under src/ |
| **Minimum toolchain** | not documented; Neco README says most modern C compilers work. Makefile is \${CC} -O3 -g \${CFLAGS} -o bluebox src/\*.c and links no -lpthread or -ldl although neco.c uses pthreads and dlsym |
| **Platforms** | Linux, macOS, FreeBSD (Neco's epoll/kqueue event queue); the write-worker offload behind the published numbers is Linux-only; Windows and WebAssembly lack Neco's socket wait, so the server is not usable there |
| **Thread safety** | One Neco scheduler thread owns the hashmap and every connection coroutine, so no locking; Neco's Linux I/O worker threads only perform write() calls on behalf of paused coroutines |
| **Drop-in for the baseline** | partial — speaks RESP so redis-cli and Redis clients connect (port 9999 by default, -p to change), but only SET/GET/DEL/PING/QUIT/DBSIZE/KEYS work and every other command returns -ERR unknown command |

## Gotchas

- Harness flaw affecting both runs: memtier_benchmark clones one object generator per client with a constant seed unless --distinct-client-seed or --randomize is given, so all 200 clients (4 threads x 50) replay the same R:R key sequence and GETs land on keys that were never SET; that is why both tables show 0.00 hits. The store held only about 909 distinct 32-byte keys (10,000 requests per client, 1 in 11 a SET), so the run measures connection handling plus a miss lookup in a tiny table, not a key-value workload.
- Closed loop with one request in flight per connection: ops/sec equals 200 connections divided by average latency (200 / 0.96274 ms = 207.7k, 200 / 0.40524 ms = 493.5k, derived from page data), so the 2.4x is the per-request round-trip cost of each server with unpinned client threads on the same 16-core machine; client binaries also differ (memtier_benchmark from PATH versus ./memtier_benchmark).
- Unequal threads: the vendored Neco (already at README commit fcde463) sends every write() to up to 2 I/O worker threads through a mutex and condition variable, and re-arms EPOLLONESHOT with an epoll_ctl call before every read, while redis-server at its default io-threads 1 does all reads and writes on one thread; compare against Redis with io-threads enabled before crediting coroutines.
- Code bugs outside the measured path: cmdDEL removes entries without bulk_release of the stored key and value (leak per deleted key); read_integer0 reads buf[-1] on an empty length line and never clears errno before strtoll, so a stale errno (Neco's epoll_ctl MOD-then-ADD leaves ENOENT) can reject a valid zero length such as SET k "" as 'invalid bulk length'. The 2025 commits 25a2011 (SET body disabled) and 2190cd7 (restored) postdate the README numbers.

## Known shortcomings

- First-party single run of a 4-command toy server against full Redis: Bluebox gets two extra Neco write threads on Linux (NECO_USEWRITEWORKERS, NECO_MAXIOWORKERS 2) while Redis ran single-threaded by default; the Redis run used memtier_benchmark from PATH and the Bluebox run a local ./memtier_benchmark, so the clients may differ; GETs only exercise the miss path. SET was disabled by an if (0) in commit 25a2011 (2025) and restored in 2190cd7, after the README numbers (fcde463, 2024-04-15). No LICENSE file, so reference only; demo app for the catalogued Neco; 29 stars, stale since 2025-05-27.
- Enricher: memtier by default clones one object generator per client with a constant seed (no --distinct-client-seed or --randomize), so all 200 clients replay the same key sequence and both tables show 0.00 hits; the store held about 909 keys, so the run measures connection handling plus a miss lookup in a tiny table. Closed loop at pipeline 1 means ops/s = 200 / average latency, so the 2.4x is round-trip cost per request, with Neco's two I/O threads doing every write() and the scheduler calling epoll_ctl before every read against redis-server's single io-thread; unpinned, client binaries differ. Bugs outside the measured path: cmdDEL leaks key and value, read_integer0 reads buf[-1] and checks stale errno (SET k "" can fail), KEYS ignores its pattern, hashmap seeds fixed at 0,0.

## Caveats and trade-offs

First-party README numbers from one run with no repetitions or variance (README unchanged since commit fcde463 on 2024-04-15). This is an app-level comparison of a 4-command server against a full-featured Redis, so the gap mostly reflects how much less work Bluebox does per request; it does not isolate Neco from Redis's epoll loop. The thread counts are not equal either: Neco on Linux enables write workers by default (NECO_USEWRITEWORKERS, NECO_MAXIOWORKERS 2, already in the neco.c vendored at the README commit), so Bluebox offloads every socket write to up to 2 extra I/O threads, while redis-server at its default io-threads 1 does all reads and writes on one thread. Both tables show 0.00 hits/sec with all GETs counted as misses, so the GET path measured is the not-found path, not a value copy. The Redis run calls memtier_benchmark from PATH and the Bluebox run calls ./memtier_benchmark (a local build), so the client binaries may differ. Redis version, memtier version, compiler and kernel are unstated. The repo has no LICENSE file (GitHub shows no license); the vendored neco.c and hashmap.c headers say MIT-style and point to a LICENSE file that is absent, and Bluebox's own code is unlicensed, hence usability reference. A transient 2025 commit (25a2011, 'fix neco_main') wrapped SET's body in if (0) and 'enable set' (2190cd7, 2025-05-27) restored it; this postdates the README numbers and HEAD stores keys normally. Neco itself is catalogued at tier D with no baseline; this record is the Redis comparison only. Last commit 2025-05-27, about 16 months before 2026-10-07. [retier] First-party single memtier run (Ryzen 9 5950X): all 200 clients replay the same key sequence (constant generator seed, 0.00 hits, about 909 keys), so the 2.4x is per-request round-trip cost, not key-value throughput; Bluebox ran with two Neco I/O threads against redis-server's default single io-thread, clients may differ (PATH vs local memtier_benchmark), 4-command toy server. No LICENSE file (reference); demo app for Neco; stale since 2025-05-27.

Demo server for the Neco coroutine library (one coroutine per connection), not a Redis replacement: supports only SET, GET, DEL and PING, no persistence, replication, expiry, pub/sub or data structures beyond a string hashmap. Vendors neco.c (v0.3.2) and tidwall's hashmap.c (v0.8.0) under src/. No pthread use appears in src/bluebox.c, so it runs on one OS thread like default redis-server.

## Maintenance

Stale since 2025-05-27 (10 commits, 29 stars, 1 fork, no issues) and unlicensed, so reference reading only; the reusable parts, Neco and hashmap.c, are MIT in their own repositories.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README tables (memtier_benchmark against redis-server and Bluebox) with the CPU model (AMD Ryzen 9 5950X) and Makefile flags (-O3 -g) public, but no compiler name or version, no Redis or memtier version and a single run, so it falls short of A; no independent measurement, so C.
- **Verifier notes:** README numbers match the record exactly (493,346.12 vs 207,734.88 ops/sec total; 0.40524 vs 0.96274 ms average; p99 0.46300 vs 1.87100; p99.9 0.74300 vs 3.16700); the derived 2.4x is correct. Shortcomings to record: first-party single run; a 4-command toy server compared with full Redis; Bluebox uses 2 extra Neco write-worker threads on Linux against single-threaded default Redis; possibly different memtier binaries; GET measured on the miss path only; no LICENSE file (reference). Metadata checked: 29 stars, 1 fork, not a fork, not archived, no license, last commit 2025-05-27 (stale). The orchestrator may prefer folding this in as evidence for the tier-D Neco entry rather than listing it separately; it is a demo app, not a wrapper or port.
- **Fields the verifier corrected:** `workload`, `caveats`
- **Shortcomings recorded by:** same-client, same-thread-count comparison; randomised-key memtier run with equal thread counts
- **Pages the verifier opened:**
  - <https://github.com/tidwall/bluebox>
  - <https://github.com/tidwall/bluebox/commits>
  - <https://github.com/tidwall/bluebox/commits/main>
  - <https://github.com/tidwall/bluebox/tree/main/src>
  - <https://raw.githubusercontent.com/tidwall/bluebox/HEAD/README.md>
  - <https://raw.githubusercontent.com/tidwall/bluebox/HEAD/Makefile>
  - <https://raw.githubusercontent.com/tidwall/bluebox/HEAD/src/bluebox.c>
  - <https://raw.githubusercontent.com/tidwall/bluebox/HEAD/src/neco.c>
  - <https://raw.githubusercontent.com/tidwall/bluebox/HEAD/src/hashmap.c>
  - <https://raw.githubusercontent.com/tidwall/bluebox/fcde46382f8ebf230b817c75aeb80d43ac716685/README.md>
  - <https://raw.githubusercontent.com/tidwall/bluebox/fcde46382f8ebf230b817c75aeb80d43ac716685/src/bluebox.c>
  - <https://raw.githubusercontent.com/tidwall/bluebox/fcde46382f8ebf230b817c75aeb80d43ac716685/src/neco.c>
  - <https://raw.githubusercontent.com/tidwall/bluebox/25a20118f65adc9619074f81a79269512d1d8e1a/src/bluebox.c>
  - <https://raw.githubusercontent.com/tidwall/bluebox/2190cd7ccf52bbce54dae7947943bbd70005e1c5/src/bluebox.c>
  - <https://raw.githubusercontent.com/RedisLabs/memtier_benchmark/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/tidwall/bluebox>
  - <https://github.com/tidwall/bluebox/commits/main>
  - <https://github.com/tidwall/bluebox/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/tidwall/bluebox/HEAD/README.md>
  - <https://raw.githubusercontent.com/tidwall/bluebox/HEAD/Makefile>
  - <https://raw.githubusercontent.com/tidwall/bluebox/HEAD/src/bluebox.c>
  - <https://raw.githubusercontent.com/tidwall/bluebox/HEAD/src/neco.c>
  - <https://raw.githubusercontent.com/tidwall/bluebox/HEAD/src/neco.h>
  - <https://raw.githubusercontent.com/tidwall/bluebox/HEAD/src/hashmap.c>
  - <https://raw.githubusercontent.com/tidwall/bluebox/HEAD/src/hashmap.h>
  - <https://raw.githubusercontent.com/tidwall/bluebox/HEAD/.gitignore>
  - <https://raw.githubusercontent.com/tidwall/bluebox/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/tidwall/bluebox/fcde46382f8ebf230b817c75aeb80d43ac716685/src/neco.c>
  - <https://raw.githubusercontent.com/tidwall/neco/HEAD/README.md>
  - <https://raw.githubusercontent.com/tidwall/neco/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/RedisLabs/memtier_benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/RedisLabs/memtier_benchmark/HEAD/memtier_benchmark.cpp>
  - <https://raw.githubusercontent.com/RedisLabs/memtier_benchmark/HEAD/client.cpp>
  - <https://raw.githubusercontent.com/RedisLabs/memtier_benchmark/HEAD/protocol.cpp>
  - <https://raw.githubusercontent.com/RedisLabs/memtier_benchmark/HEAD/obj_gen.cpp>
  - <https://raw.githubusercontent.com/RedisLabs/memtier_benchmark/HEAD/obj_gen.h>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/tidwall/bluebox`) · [data/wave11/enrich/raw/github_com_tidwall_bluebox.json](../../../data/wave11/enrich/raw/github_com_tidwall_bluebox.json) (enrichment confidence 0.8)

</details>
