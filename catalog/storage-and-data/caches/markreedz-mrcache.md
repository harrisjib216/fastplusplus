# mrcache

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Caches](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟡 stale

> Single-threaded io_uring key-value cache server in C; README claims 7x Redis and 46x memcached GET throughput at 16 B.

| | |
|---|---|
| **Beats** | Redis (also memcached) |
| **Claimed result** | README table 'GET - 16B (ops/sec)': mrcache 18.6m, redis 2.5m, memcached 400k (about 7.4x Redis and 46x memcached, derived from page data). 'GET - 10kb (ops/sec)': mrcache 979k, redis 313k, memcached 261k (about 3.1x and 3.8x, derived from page data); mrcache with zstd 212k is slower than both. README intro still says 'a key value cache with support for compression that is 25x faster than memcached' (matches the older 9.8m vs 400k table, not the current one). Older README revisions (commit e33dfb6, 2024-04-21): 16B GET mrcache 9.8m, redis 2.7m, memcached 400k. |
| **Workload** | GET of a single small value (16 B) and of a 10 kB value on one node over TCP (almost certainly loopback: 979k ops/sec x 10 kB is about 9.8 GB/s), in-memory; README tables show ops/sec for mrcache, Redis and memcached. The client harness bench/bench.go (Go; defaults 16 connections, 2 s, batch 1, 16-byte key, 256-byte value, one repeated zero-filled key) is in the repo, but the README does not state which flags produced the tables; the 16 B and 10 kB rows need -v overrides and, given the 18.6m figure, a large -b batch (pipelining). |
| **Metric** | throughput |
| **Compiler and flags** | Server: gcc -O3 (Makefile CFLAGS = -O3), Linux kernel 5.8+, liburing, zstd; io_uring configured with SQPOLL, SINGLE_ISSUER, multishot accept/recv and provided buffer ring. Benchmark client: Go (go run bench.go). Redis and memcached versions, build and configuration are not stated. |
| **Adoption** | 26 stars, 2 forks |
| **Last commit** | 2024-10-29 |
| **Links** | [repository](https://github.com/MarkReedZ/mrcache) · [benchmark](https://github.com/MarkReedZ/mrcache) |

## Verdict

The README reports single-node GET throughput from the repo's Go client (bench.go, localhost by default), which fetches one zero-filled 16-byte key over and over: 18.6m ops/s against Redis 2.5m and memcached 400k with 16 B values, and 979k against 313k and 261k with 10 kB values (212k with zstd on an all-zero value). No CPU, kernel, compiler, Redis or memcached version or configuration, connection count or batch size is given, and the memcached client is not in the repo. mrcache's numbers come from a busy-polling event thread plus an SQPOLL kernel thread, while the Redis and memcached configurations are unstated.

## Use it when

- Studying or forking a compact io_uring server: SQPOLL, multishot accept/recv, provided buffer rings and one zero-copy writev per received chunk, all in a few hundred lines of net.c.
- A trusted, single-tenant cache of many small items behind your own client, where about 18 B of per-item overhead (8 B index slot at a 70% load cap plus a 6 B item header) matters more than Redis features and FIFO eviction is acceptable.
- Read-heavy, pipelined GET traffic from a few long-lived connections on one Linux 6.0+ machine, where giving up one spinning user core plus the SQPOLL kernel core is acceptable.
- Large compressible values you want stored zstd-compressed (level 2) on the server via setz/getz, trading GET throughput (979k to 212k ops/s at 10 kB in the README) for RAM.

## Skip it when

- You need Redis or memcached protocol compatibility, data types, TTLs, DEL, persistence, replication or auth; none exist, and set has no acknowledgement.
- Clients are untrusted, buggy or reconnect often: request lengths are not validated, an unknown command frees the connection while its multishot recv is still armed, and client sockets are never closed.
- Memory beyond the item store is tight: the receive pool is 16,384 x 32 KB = 512 MB of address space (each buffer gets at least one page touched as the ring cycles, so 64 MB or more resident), each connection callocs about 6.3 MB of iovec groups, and the index is sized once at startup and never grows.
- You want multi-core scaling or an idle server that sleeps: there is one event-loop thread, and it spins on the completion ring even with no traffic.
- Kernel older than 6.0 or any non-Linux platform: IORING_SETUP_SINGLE_ISSUER and multishot recv need 6.0, although the README says 5.5+ in one place and 5.8+ in another.

## How it is fast

Networking uses io_uring with SQPOLL, multishot accept and multishot recv into a 16,384-entry provided buffer ring, and the event loop busy-polls the completion ring, so the user thread makes almost no syscalls and the kernel's SQ thread does the submission work on another core. Every request in a received chunk is parsed in place and all replies go out in one writev whose iovecs point straight at the stored item (length header plus value), so GET replies are never copied in user space. Lookup is wyhash plus linear probing in a power-of-two table of 8-byte slots that pack a 28-bit block id, 12 hash bits and a 24-bit offset; a SET is a bump allocation into the current block and eviction drops a whole block, so there is no per-item free or LRU bookkeeping.

## Compared with alternatives

Pick Pogocache, Dragonfly or Valkey when you need a drop-in Redis/Memcached server with published versions and repeatable runs (Pogocache: about 2.0x Redis 8.2.1 GET at pipeline 1, median of 31 runs). Pick mrcache only when you control both client and server, want the lowest per-item overhead for many small items on one core with FIFO eviction, or want a small io_uring server to study or fork and harden.

## Integration

| | |
|---|---|
| **Form** | source-drop (standalone server binary; clients use its binary TCP protocol) |
| **Dependencies** | liburing (provided-buffer-ring API, io_uring_setup_buf_ring) and libzstd; wyhash.h is vendored. The Makefile also links -lmrloop, which the source no longer uses. |
| **Minimum toolchain** | gcc with -std=c99 -D_GNU_SOURCE (the repo's bld script uses -O3); Linux kernel 6.0+ in practice |
| **Platforms** | Linux only (io_uring); the parser does native-endian unaligned loads, so little-endian x86-64 or aarch64 |
| **Thread safety** | Single-threaded server: one event-loop thread plus the kernel SQPOLL thread, with no locks and no multi-core scaling. |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw (bench/bench.go): the client counts a batch as done after length\*batch reply bytes, read in 4 KB chunks, but mrcache sends 4+length bytes per GET and Redis 23 bytes at 16 B. Once a batch's replies exceed one 4 KB read (batch above about 200 at 16 B), leftover reply bytes carry into the next batch and, at many batch sizes, keep piling up, so the client stops waiting for its own batch. The reported rate then tends to 1.25x the served rate for mrcache and 1.44x for Redis at 16 B, so this bias favours Redis rather than mrcache. The zstd row used an all-zero 10 kB value (rand.Read is commented out), which is zstd's best case.
- The server cannot safely absorb deep pipelines. Each received chunk (up to 32 KB) is answered with one writev from a fixed 1,024-entry iovec array with no bounds check, so more than 1,024 GETs in one chunk (about 20 KB of 16-byte-key GETs) overflows into the free list and the next iovec group and exceeds IOV_MAX. In addition, a short write that ends inside the first iovec resends that whole iovec and desyncs the stream.
- No input validation: SET value lengths (signed 32-bit) are never checked against the 16 MB block size, so an oversized or negative length writes past the block. GETZ on a key stored with plain SET tests an unsigned ZSTD_getFrameContentSize result with `< 0`, so the guard never fires: the server mallocs 2 bytes, writes a 4-byte header into them and queues a negative-length reply, and the client gets no answer. A SETZ whose compression fails (for example, an incompressible value above about 2 MB overflowing the vlen+64 output buffer) never advances the parse pointer, so the single thread spins forever. GETZ decompression buffers are also stored at free_me[num] instead of free_me[num-1], so the last buffer of every write leaks; with one GETZ per write, every buffer leaks.
- Connections leak. No close() appears anywhere in the server, and an EOF completion arrives without IORING_CQE_F_MORE, so it falls into the write-completion branch and free_conn never runs. Each closed client therefore leaks its fd and its roughly 6.3 MB connection struct. The README's `make` fails: the Makefile wildcard also compiles probe.c, which has its own main(), and it links the dropped -lmrloop; use the bld script instead. The documented -z/--zstd flag is not parsed (it prints usage and exits with status 2), and the default -m is 128 MB, not the 256 MB the README and usage text state.

## Known shortcomings

- First-party README table only: no CPU, versions or run flags, the memcached harness is missing from the repo, and bench.go hits one repeated key (default value 256 B) over loopback with batch 1 and 16 connections, at which 18.6M gets/s is implausible without undisclosed pipelining; its length-times-batch count undercounts mrcache's 4-byte reply header as well as Redis RESP. SQPOLL burns an extra core. The lead's 9.8M vs 2.7M numbers are the pre-2024-04-24 README; the '25x faster than memcached' headline is stale against the current table (16 B: 18.6M vs Redis 2.5M vs memcached 400k; 10 kB: 979k vs 313k vs 261k). MIT, 26 stars, last commit 2024-10-29 (stale); the HEAD Makefile still links -lmrloop after mrloop.h was removed.
- Enricher (code reading): security and robustness bugs in the server: a 1,024-entry iovec array with no bounds check (overflows above 1,024 GETs per 32 KB recv chunk), no close() anywhere (each connection leaks an fd plus about 6.3 MB), SET lengths not validated (heap overflow), an unsigned '&lt; 0' guard in GETZ that never fires, an infinite loop when SETZ compression fails, an off-by-one leak of GETZ buffers, and a short write inside the first iovec that resends it. bench.go counts length\*batch reply bytes while mrcache sends 4+length and Redis 23 B at 16 B, so above about batch 200 the client runs ahead of replies and reported rates drift to about 1.25x served (mrcache) and 1.44x (Redis), a bias that favours Redis; the zstd row used an all-zero value. The event loop busy-polls one core even when idle plus the SQPOLL core, the recv buffer pool is 512 MB, the real minimum kernel is 6.0 (not 5.8), and `make` fails (build with the bld script).

## Caveats and trade-offs

Tier C: first-party README numbers with no CPU model, core count, kernel version, Redis or memcached version, connection count, pipelining/batch size or run command stated. The bench/bench.go harness in the repo defaults to 16 connections, batch 1, a 16-byte key and a 256-byte value, and issues GET on one single key (zero-filled key and value) over and over, so the hot path is one cache-resident entry and the result mostly measures the network loop, not the hash index. At batch 1, 18.6m ops/sec over 16 TCP connections would need sub-microsecond round trips, so the headline row was almost certainly run with heavy pipelining that the README does not disclose. bench.go only speaks mrcache's binary protocol and Redis RESP; it has no memcached mode, and bench/py/mc.py, red.py and mrc.py are one-shot set/get smoke scripts, so the harness behind the memcached numbers is not in the repo. The client counts a batch complete after length\*batch bytes, which undercounts both servers' replies (mrcache sends a 4-byte length header plus the value per GET; a Redis RESP bulk reply adds 7 bytes at 16 B and 10 bytes at 10 kB), so split reads can let the client run ahead of its replies and the per-server error differs. Numbers moved between README revisions: 1.07m vs redis 270k vs memcached 100k (commit cce89a1, 2024-02-28; 10 kB rows 179k / 79k zstd / memcached 24k / redis 32k), 9.8m vs 2.7m vs 400k (commit e33dfb6, 2024-04-21), 18.6m vs 2.5m vs 400k (from 2024-04-24, after the io_uring multishot rewrite); the 10 kB rows are identical in e33dfb6 and HEAD, so they predate the rewrite. The headline '25x faster than memcached' is stale against the current table (18.6m/400k is about 46x, derived from page data). The server uses io_uring SQPOLL, which keeps a kernel polling thread busy on an extra core; Redis in its default configuration runs commands on one thread and memcached defaults to 4 worker threads, so per-core fairness is unstated. Single-node in-memory scope only; no networked or persistence comparison. The README is inconsistent on the kernel requirement (5.5+ in the intro, 5.8+ in Dependencies) and the HEAD Makefile still links -lmrloop although mrloop.h was removed on 2024-05-12 and the README no longer lists mrloop, so a build may need fixes. No third-party measurement found (WebSearch for mrcache with io_uring, Redis and memcached returned nothing about the project). [retier] Enricher (code reading): unbounded 1,024-entry iovec array, unvalidated SET lengths (heap overflow), no close() (fd and about 6.3 MB leaked per connection), infinite loop on SETZ compression failure; bench.go's byte-count bias favours Redis above batch 200; busy-polling event loop plus SQPOLL core; minimum kernel 6.0.

Single-node in-memory cache with a proprietary binary protocol (get/set/getz/setz; set has no response) and its own clients (Python asyncio asyncmrcache), so it is not a drop-in replacement for Redis or memcached. Needs Linux 5.8+ io_uring. Keys limited to under 32 kB, values under 16 MB. The hash index (open addressing, about 14 B per item) is allocated once at startup and never grows or shrinks, so it must be sized up front. Eviction is FIFO by dropping the oldest 16 MB block, not LRU; README documents per-item overhead of about 18 B against 50-60 B for Redis and memcached. No data structures, clustering or persistence documented. Optional zstd compression (getz/setz) roughly cuts 10 kB GET throughput to 212k.

## Maintenance

Stale: last commit 2024-10-29, last code change 2024-05-12, and issue #2 (2020) is still open. MIT and small enough to read in an afternoon, but experimental code: the connection leak, unchecked request lengths and the 1,024-iovec limit make it unfit for production without fixes, and it should be built with the bld script rather than make.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README table (GET 16B: mrcache 18.6m, redis 2.5m, memcached 400k ops/sec; GET 10kb: 979k, zstd 212k, memcached 261k, redis 313k) with a partial harness (bench/bench.go) but no CPU model, Redis/memcached versions, run command or flags for the runs; the memcached harness is not in the repo. Partial methodology from the project itself is tier C.
- **Verifier notes:** README numbers match the record; repo metadata checked (MIT, 26 stars, 2 forks, not archived or a fork, last commit 2024-10-29 'Add Liburing dependency to the README', so stale). Corrections only sharpen the harness caveats: bench.go defaults to a 256-byte value, undercounts mrcache's 4-byte reply header as well as Redis RESP framing, and the 18.6m row implies undisclosed pipelining. Shortcomings to record: unstated hardware/versions/run flags, memcached harness missing, single-key loopback workload, SQPOLL extra core, stale 25x headline.
- **Fields the verifier corrected:** `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-92 (wave 6 seed pass, 2026-10-13); enricher (seed pass, 2026-10-13)
- **Pages the verifier opened:**
  - <https://github.com/MarkReedZ/mrcache>
  - <https://github.com/MarkReedZ/mrcache/commits>
  - <https://github.com/MarkReedZ/mrcache/tree/master/bench>
  - <https://github.com/MarkReedZ/mrcache/tree/master/bench/py>
  - <https://raw.githubusercontent.com/MarkReedZ/mrcache/HEAD/README.md>
  - <https://raw.githubusercontent.com/MarkReedZ/mrcache/HEAD/bench/bench.go>
  - <https://raw.githubusercontent.com/MarkReedZ/mrcache/HEAD/bench/README.md>
  - <https://raw.githubusercontent.com/MarkReedZ/mrcache/HEAD/bench/py/mc.py>
  - <https://raw.githubusercontent.com/MarkReedZ/mrcache/HEAD/bench/py/mrc.py>
  - <https://raw.githubusercontent.com/MarkReedZ/mrcache/HEAD/bench/py/red.py>
  - <https://raw.githubusercontent.com/MarkReedZ/mrcache/HEAD/Makefile>
  - <https://raw.githubusercontent.com/MarkReedZ/mrcache/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/MarkReedZ/mrcache/HEAD/mrcache.c>
  - <https://raw.githubusercontent.com/MarkReedZ/mrcache/HEAD/net.c>
  - <https://raw.githubusercontent.com/MarkReedZ/mrcache/HEAD/protocol.txt>
  - <https://raw.githubusercontent.com/MarkReedZ/mrcache/cce89a1/README.md>
  - <https://raw.githubusercontent.com/MarkReedZ/mrcache/e33dfb6/README.md>
- **Sources the enricher read:**
  - <https://github.com/MarkReedZ/mrcache>
  - <https://github.com/MarkReedZ/mrcache/commits>
  - <https://github.com/MarkReedZ/mrcache/issues?q=is%3Aissue>
  - <https://github.com/MarkReedZ/mrcache/issues/2>
  - <https://raw.githubusercontent.com/MarkReedZ/mrcache/HEAD/README.md>
  - <https://raw.githubusercontent.com/MarkReedZ/mrcache/HEAD/Makefile>
  - <https://raw.githubusercontent.com/MarkReedZ/mrcache/HEAD/bld>
  - <https://raw.githubusercontent.com/MarkReedZ/mrcache/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/MarkReedZ/mrcache/HEAD/protocol.txt>
  - <https://raw.githubusercontent.com/MarkReedZ/mrcache/HEAD/mrcache.c>
  - <https://raw.githubusercontent.com/MarkReedZ/mrcache/HEAD/mrcache.h>
  - <https://raw.githubusercontent.com/MarkReedZ/mrcache/HEAD/common.h>
  - <https://raw.githubusercontent.com/MarkReedZ/mrcache/HEAD/net.c>
  - <https://raw.githubusercontent.com/MarkReedZ/mrcache/HEAD/net.h>
  - <https://raw.githubusercontent.com/MarkReedZ/mrcache/HEAD/hashtable.c>
  - <https://raw.githubusercontent.com/MarkReedZ/mrcache/HEAD/hashtable.h>
  - <https://raw.githubusercontent.com/MarkReedZ/mrcache/HEAD/blocks.c>
  - <https://raw.githubusercontent.com/MarkReedZ/mrcache/HEAD/blocks.h>
  - <https://raw.githubusercontent.com/MarkReedZ/mrcache/HEAD/probe.c>
  - <https://raw.githubusercontent.com/MarkReedZ/mrcache/HEAD/todo>
  - <https://raw.githubusercontent.com/MarkReedZ/mrcache/HEAD/.gitignore>
  - <https://raw.githubusercontent.com/MarkReedZ/mrcache/HEAD/tests.py>
  - <https://raw.githubusercontent.com/MarkReedZ/mrcache/HEAD/tests2.py>
  - <https://raw.githubusercontent.com/MarkReedZ/mrcache/HEAD/tst.py>
  - <https://raw.githubusercontent.com/MarkReedZ/mrcache/HEAD/rtst.py>
  - <https://raw.githubusercontent.com/MarkReedZ/mrcache/HEAD/blk.py>
  - <https://raw.githubusercontent.com/MarkReedZ/mrcache/HEAD/bench/bench.go>
  - <https://raw.githubusercontent.com/MarkReedZ/mrcache/HEAD/bench/README.md>
  - <https://raw.githubusercontent.com/MarkReedZ/mrcache/HEAD/bench/py/mc.py>
  - <https://raw.githubusercontent.com/MarkReedZ/mrcache/HEAD/bench/py/mrc.py>
  - <https://raw.githubusercontent.com/MarkReedZ/mrcache/HEAD/bench/py/red.py>
  - <https://github.com/MarkReedZ/asyncmrcache>
  - <https://github.com/MarkReedZ/asyncmrcache/tree/master/src/asyncmrcache>
  - <https://github.com/MarkReedZ/asyncmrcache/commits>
  - <https://raw.githubusercontent.com/MarkReedZ/asyncmrcache/HEAD/src/asyncmrcache/client.py>
  - <https://raw.githubusercontent.com/MarkReedZ/asyncmrcache/HEAD/src/asyncmrcache/server.py>
  - <https://pypi.org/pypi/asyncmrcache/json>
  - <https://raw.githubusercontent.com/axboe/liburing/master/man/io_uring_setup.2>
  - <https://raw.githubusercontent.com/axboe/liburing/master/man/io_uring_setup_buf_ring.3>
  - <https://raw.githubusercontent.com/axboe/liburing/master/man/io_uring_prep_recv.3>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/markreedz/mrcache`) · [data/wave6/enrich/raw/github_com_markreedz_mrcache.json](../../../data/wave6/enrich/raw/github_com_markreedz_mrcache.json) (enrichment confidence 0.8)

</details>
