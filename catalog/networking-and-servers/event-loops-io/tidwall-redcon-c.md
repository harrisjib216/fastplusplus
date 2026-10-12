# redcon.c

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [Event loops and async I/O](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟢 active

> Small C framework for Redis-protocol (RESP) servers on epoll/kqueue; its toy clone outruns Redis 6.0.6 under deep pipelining.

| | |
|---|---|
| **Beats** | Redis 6.0.6 (the README writes 'Redis 6.06'), single-threaded stock redis-server |
| **Claimed result** | SET at pipeline 128: 2,122,295 vs 990,307 req/s (2.14x, derived from page data); GET at pipeline 128: 2,230,151 vs 1,208,751 req/s (1.85x, derived from page data); SET at pipeline 16: 1,310,787 vs 765,284 req/s; parity at pipeline 1 (SET 114,554 vs 114,467 req/s, GET 114,602 vs 114,888); about 7% less memory (79.7 MB vs 84.8 MB). |
| **Workload** | redis-benchmark -q -t set,get -r 1000000 -n 10000000 against the example Redis clone (example/clone.c, single-threaded, built on redcon.c and evio.c) and against stock Redis 6.0.6, pipeline depths 1 to 128, on one AWS c5.2xlarge. |
| **Metric** | throughput |
| **Hardware** | AWS c5.2xlarge instance (Intel Xeon 3.6 GHz per the README; exact CPU model not named). The example clone binds tcp://localhost:6380 and the README's redis-benchmark commands carry no -h, so the client ran on the same 8-vCPU instance as the server (inferred). |
| **Compiler and flags** | Not stated. The README build line is 'cc \*.c && ./a.out' with no -O flag; the benchmark commands are stated (redis-benchmark -q -t set,get -r 1000000 -n 10000000 -P 16 against ports 6379 and 6380, other depths varied) but how the Redis binary was built and configured (persistence, save points) is not. |
| **Adoption** | 58 stars; C port of the widely used tidwall/redcon Go library |
| **Last commit** | 2026-06-29 |
| **Links** | [repository](https://github.com/tidwall/redcon.c) · [benchmark](https://github.com/tidwall/redcon.c) |

## Verdict

The author's July 2020 run on one AWS c5.2xlarge (Intel Xeon 3.6 GHz, model not named) drove both the single-threaded example clone and stock Redis 6.0.6 with redis-benchmark -t set,get -r 1000000 -n 10000000 at pipeline depths 1 to 128 on the same host. The clone matched Redis at pipeline 1 and reached 2,122,295 vs 990,307 SET/s (2.14x) and 2,230,151 vs 1,208,751 GET/s (1.85x) at pipeline 128, which measures a minimal key/value command path against full Redis, not the event loop on equal work; compiler, flags and the Redis configuration are not given.

## Use it when

- Building a custom service that speaks the Redis protocol (cache front, proxy, embedded store, test double) so existing Redis clients and redis-cli can talk to it.
- Pipelined workloads (pipeline depth 8 and up) where a minimal command path should beat a general-purpose server; the README shows 1.4x to 2.1x over Redis 6.0.6 at depths 8 to 128.
- Single-threaded C servers on Linux or macOS that want RESP parsing and reply encoding without writing them by hand.
- Prototyping a multi-threaded RESP server with redcon_main_mt, provided you bring your own locking.

## Skip it when

- As a Redis replacement: the example clone only does SET/GET/DEL/KEYS/TTL/PING/FLUSHDB/DBSIZE/QUIT with no persistence, replication, other data types, ACLs, pub/sub or scripting.
- Unpipelined request/response traffic: at pipeline 1 the README shows parity with Redis (about 114.5k req/s each), so there is no speedup to collect.
- Windows (evio.c has only epoll and kqueue back ends) or TLS-terminated endpoints (no TLS support in the library).
- Untrusted clients without review: a negative bulk length crash path was only fixed on 2026-06-29, there is no test suite in the repo and the library has 58 stars.
- When you only need an event loop: libev, libhv or picoev give the loop without RESP framing.

## How it is fast

The event loop is tidwall/evio.c: level-triggered epoll (kqueue on macOS/BSD), each readable socket drained into a 16 KB stack buffer until EAGAIN, commands parsed in place when no partial packet is pending, and argument buffers reused per connection so steady-state parsing does not allocate. Replies are appended to a per-connection buffer and flushed with one write() after the batch of events, so a 128-command pipeline costs a few syscalls. The big pipelined gains in the README come mostly from the example clone doing far less per command than Redis (a Robin Hood hashmap of single-allocation key/value pairs, no command-table ACL checks, stats, keyspace notifications or persistence).

## Compared with alternatives

Pick redcon.c over a bare loop such as libev, libhv, picoev or mrloop when the wire protocol is RESP and you want parsing, reply encoding and write coalescing done for you; pick tidwall's Go redcon or redcon.rs when the rest of the service is in those languages.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | evio.c v0.5.3 and buf.c (imported with tidwall's pkg.sh from the .package manifest); the example clone also uses tidwall/hashmap.c; pthreads for redcon_main_mt |
| **Minimum toolchain** | C99-compatible C compiler (README builds with plain 'cc \*.c'); not otherwise documented |
| **Platforms** | Linux (epoll), macOS and BSD (kqueue); no Windows |
| **Thread safety** | Single-threaded by default; redcon_main_mt runs one evio loop per thread with connections spread across them, and the command callback must synchronize shared state itself (the example clone uses one pthread rwlock when built with -DUSEMT). |
| **Drop-in for the baseline** | no |

## Gotchas

- The benchmark table dates from the first commit (2020-07-27, evio.c v0.3.2) and was never re-run: the args move to the connection, multithread support, five evio.c updates and the 2026 parser fix all came later, Redis 6.0.6 was the only Redis tested, the build line has no -O flag, Redis's persistence settings are not stated (its default save points can trigger BGSAVE during the 87-second pipeline-1 run), and redis-benchmark with default 3-byte values ran on the same 8-vCPU c5.2xlarge as the server.
- Race in the optional -DUSEMT clone build (PR #2, merged 2026-06-29): evio runs the tick hook on one thread, and the clone's tick() deletes expired keys from the shared hashmap and writes server-&gt;now without taking the rwlock while other threads run GET and SET; it also drops expired pairs without pair_free, which leaks them in every build.
- The README's quick-start clone declares 'int vallen' and passes &vallen to redcon_args_at, whose length parameter has been size_t \* since 2021-01-26; that writes 8 bytes into a 4-byte int (GCC 14 rejects the incompatible pointer by default) and the sample also stores keys as NUL-terminated strings, so keys are not binary safe. example/clone.c handles both correctly.
- MAXARGSZ allows 512 MB bulk arguments, but the clone stores key and value lengths in 29-bit signed bitfields (maximum 268,435,455), so values between 256 MB and 512 MB overflow the stored length.

## Known shortcomings

- First-party README; the example server is a minimal clone compared against full Redis 6.0.6, so much of the gain is skipped work; parity at pipeline 1; build flags unstated (cc \*.c, no -O); the client runs on the same host (the clone binds localhost:6380).
- Enricher: the benchmark table dates from the first commit (2020-07-27, evio.c v0.3.2) and was never re-run. The clone's tick() deletes expired keys from the shared hashmap without the rwlock in the -DUSEMT build (data race) and never frees them (leak in every build); the README quick-start passes int\* where size_t\* is expected (8-byte write into a 4-byte int); the clone's 29-bit length bitfields overflow below MAXARGSZ 512 MB.

## Caveats and trade-offs

First-party README numbers only. The comparison is a minimal key-value server against full Redis, so the speedup mostly measures how much work each server skips (no command table with ACL checks, no client tracking or stats, no persistence or replication backlog), not a faster event loop for the same job. Parity at pipeline 1 shows the test is client or network bound there. Redis 6.0.6 was released in 2020 and later Redis versions were not tested. Build flags unstated ('cc \*.c' has no -O), Redis persistence settings unstated (default RDB save points could fork during a 10M-request run), CPU model not named. README memory line says the clone used about 7% less memory (79.7 MB to 84.8 MB). A parser bug (negative bulk lengths) was fixed on 2026-06-29, after the numbers were taken. No independent measurement found (two searches); I opened the README, example/README.md, example/clone.c and redcon.c. [retier] Enricher: the table dates from the first commit (2020-07-27) and was never re-run; the clone's tick() races and leaks expired keys; the README quick-start passes int\* where size_t\* is expected; 29-bit length bitfields overflow below MAXARGSZ.

It is a framework for writing Redis-protocol servers, not a Redis replacement. The example clone supports only SET (EX/PX/NX/XX/KEEPTTL), GET, DEL, KEYS, PING, FLUSHDB, DBSIZE and QUIT, with no persistence, replication, other data types, ACLs, pub/sub or scripting. The README example stores keys as NUL-terminated C strings, so keys are not binary safe. Single-threaded by default; redcon_main_mt adds threads, and the clone's multithreaded build serializes access with one global rwlock. Event loop comes from tidwall/evio.c (epoll on Linux, kqueue on macOS/BSD). Dependencies (hashmap.c, match.c) are fetched with pkg.sh.

## Maintenance

Light maintenance (25 commits, last on 2026-06-29 with a parser fix and a merged multithreaded clone build), MIT-licensed and two small C files plus evio.c, so easy to vendor, but the benchmark is six years old and untested against current Redis or Valkey.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README and example/README.md table (redis-benchmark, pipeline 1 to 128, Redis 6.06 vs the example clone) carries every quoted number and the memory line, on an AWS c5.2xlarge with the benchmark command given, but it is first-party, the CPU model, compiler and flags are not stated (build line 'cc \*.c' has no -O), and the Redis build and configuration are unstated, so C.
- **Verifier notes:** Record is accurate: MIT (Copyright 2022 Joshua J Baker), 58 stars, 25 commits, last commits 2026-06-29 ('Fix negative bulk lengths' and the merge of PR #2, which adds an optional -DUSEMT multithreaded clone build; the default clone stays single-threaded, matching single-threaded Redis). Shortcomings: first-party only; a minimal clone (GET/SET/DEL/KEYS/PING/FLUSHDB/DBSIZE/TTL, no ACL, persistence or replication) against full Redis 6.0.6, so the 1.85-2.14x at pipeline 128 measures skipped work rather than a faster loop; parity at pipeline 1; client and server share the box; build flags and Redis persistence settings unstated; parser bug fixed after the numbers were taken.
- **Fields the verifier corrected:** `hardware`, `caveats`
- **Shortcomings recorded by:** verifier batch-82 (wave 5 seed pass, 2026-10-13); enricher (seed pass, 2026-10-13)
- **Pages the verifier opened:**
  - <https://github.com/tidwall/redcon.c>
  - <https://github.com/tidwall/redcon.c/commits>
  - <https://raw.githubusercontent.com/tidwall/redcon.c/HEAD/README.md>
  - <https://raw.githubusercontent.com/tidwall/redcon.c/HEAD/example/README.md>
  - <https://raw.githubusercontent.com/tidwall/redcon.c/HEAD/example/clone.c>
  - <https://raw.githubusercontent.com/tidwall/redcon.c/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/tidwall/redcon.c>
  - <https://github.com/tidwall/redcon.c/commits>
  - <https://github.com/tidwall/redcon.c/commits/main/README.md>
  - <https://github.com/tidwall/redcon.c/issues?q=is%3Aissue>
  - <https://github.com/tidwall/redcon.c/issues/1>
  - <https://raw.githubusercontent.com/tidwall/redcon.c/HEAD/README.md>
  - <https://raw.githubusercontent.com/tidwall/redcon.c/HEAD/redcon.c>
  - <https://raw.githubusercontent.com/tidwall/redcon.c/HEAD/redcon.h>
  - <https://raw.githubusercontent.com/tidwall/redcon.c/HEAD/.package>
  - <https://raw.githubusercontent.com/tidwall/redcon.c/HEAD/example/README.md>
  - <https://raw.githubusercontent.com/tidwall/redcon.c/HEAD/example/clone.c>
  - <https://raw.githubusercontent.com/tidwall/redcon.c/51b431aa6e3c4cfedda2d9242da4e6192be96ba6/README.md>
  - <https://raw.githubusercontent.com/tidwall/redcon.c/51b431aa6e3c4cfedda2d9242da4e6192be96ba6/example/README.md>
  - <https://raw.githubusercontent.com/tidwall/redcon.c/51b431aa6e3c4cfedda2d9242da4e6192be96ba6/.package>
  - <https://raw.githubusercontent.com/tidwall/evio.c/HEAD/evio.c>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/tidwall/redcon.c`) · [data/wave5/enrich/raw/github_com_tidwall_redcon_c.json](../../../data/wave5/enrich/raw/github_com_tidwall_redcon_c.json) (enrichment confidence 0.75)

</details>
