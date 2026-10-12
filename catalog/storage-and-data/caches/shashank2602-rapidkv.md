# RapidKV

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Caches](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Single-threaded C++20 RESP server with 13 string commands; ties Redis unpipelined, 1.45-4.2x faster when pipelined.

| | |
|---|---|
| **Beats** | Redis |
| **Claimed result** | At pipeline=1 throughput is within 4% (135,165 vs 130,019 ops/sec) but p99 latency is 49% lower; at pipeline=16 mixed workload RapidKV is +63% ops/sec (1,823,366 vs 1,119,012) with 58% lower p99; at pipeline=100 RapidKV reaches 5,178,742 vs Redis's 1,718,018 ops/sec, a 3.01x speedup; author's headline figure is 'up to \~4.2x faster than Redis on pipelined workloads' (pipeline=500) |
| **Workload** | memtier_benchmark (8 threads, 25 clients/thread, CPU-pinned via taskset) against RapidKV and Redis on the same machine, with Redis persistence disabled and both servers restarted between runs. Runs: baseline pipeline=1, 1:1 SET:GET, 8B values, 100K keys; mixed pipeline=16, 1:9 SET:GET, 64B values, 200K keys; pipeline-depth sweep (1/10/100/200/500), 1:9 SET:GET, 8B values, 1M keys, 30s runs; plus 2KB-value (pipeline=64), SET-only 128B and GET-only runs |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 7 4800H (8C/16T, 2.9GHz base), 16GB RAM, 32KiB L1d/L1i x8, 512KiB L2 x8, 4096KiB L3 x2, Kubuntu 24.04 LTS |
| **Compiler and flags** | Compiler used for the benchmarks not stated (README requires GCC 12+/Clang 15+/MSVC 2022+); the CMakeLists Release build uses -O3 -march=native -flto on GCC/Clang |
| **Adoption** | 1 star |
| **Last commit** | 2026-05-10 |
| **Links** | [repository](https://github.com/shashank2602/RapidKV) · [benchmark](https://github.com/shashank2602/RapidKV#benchmarks) |

## Verdict

The author ran memtier_benchmark (8 threads x 25 clients) over loopback on one AMD Ryzen 7 4800H laptop running Kubuntu 24.04, CPU-pinned, with Redis persistence off; the Redis version and io-threads setting are not stated. RapidKV tied Redis at pipeline 1 (135K vs 130K ops/s; 0.99x in the 1M-key sweep) with about half the p99, then led by 1.45x at pipeline 10, 3.01x at 100 (5.18M vs 1.72M ops/s) and 4.23x at 500 (8.04M vs 1.90M) on 1:9 SET:GET with 8-byte values. The compiler is not stated beyond the CMake Release flags (-O3 -march=native -flto), and the memtier command lines are not in the repo.

## Use it when

- A single-core, read-heavy GET/SET cache whose clients pipeline deeply. In the README's 1:9 SET:GET sweep, RapidKV was 1.45x Redis at pipeline 10, 3.0x at 100 and 4.2x at 500, with 3.8-5.1x lower p99 at depths of 100 and more.
- Bulk value transfer on one core. At pipeline 64 with 2 KB values it moved 1.52 GB/s against Redis's 780 MB/s, and a SET-only run with 128 B values (every key and value on the slab path) was 47% faster.
- Unpipelined string traffic where Redis's tail latency is the problem. At pipeline 1, throughput tied (135K vs 130K ops/s) but p99 was 1.57 ms against 3.06 ms in the README run.
- As a source of parts to study or vendor. flatMap.h is a header-only template and CompactString is small, and both are MIT-licensed. The README puts FlatMap at 1.9-2.6x std::unordered_map, but that is with 10-character random keys against std::hash and no reserve(); it was not compared with absl or boost flat maps.

## Skip it when

- You need anything beyond 13 string commands: lists, hashes, sets, MGET/MSET, SETNX/SETEX, Lua, pub/sub, MULTI, persistence, replication or clustering.
- Untrusted networks. It has no AUTH, ACL or TLS, binds 0.0.0.0 by default, and has no maximum request or bulk length: the per-connection read buffer keeps doubling while a declared bulk string is still incomplete.
- Multi-core throughput. A single thread does all I/O and command work, so at pipeline 1 it only matched Redis (about 125-135K ops/s in the README runs).
- A keyspace that keeps growing while you need exact answers. From reading flatMap.h: during each incremental doubling, a key whose home slot the migration cursor has passed, but which sits further along its probe run, is found in neither table. GET can miss it, DEL returns 0, and a SET issued meanwhile is later overwritten by the stale migrated value. The resize unit test finishes migrating before it reads back, so this path is untested.
- Production use in general. The project has 1 star and no releases or issues, all code commits fall between 2026-01-31 and 2026-02-22, and every Redis comparison is an unscripted first-party laptop run.

## How it is fast

It does less work per command rather than using more cores. The README's perf stat shows 2,144 instructions and 2,265 cycles per GET, against Redis's 5,421 and 3,813. The store is a Robin Hood open-addressing hash table in structure-of-arrays layout (2-byte PSL + tag metadata array, 16-byte keys, rapidhash with a random per-process seed) that doubles incrementally, 32 slots migrated per operation. Keys and values are 16-byte CompactStrings with a 15-byte inline SSO, and anything longer comes from a thread-local slab allocator with power-of-two classes (32 B-2 KB). The I/O path is one Asio event loop, a zero-copy RESP parser that returns string_views into a 64 KB read buffer, command names packed into a uint64 for dispatch, pipelined commands run in batches of 16 with hash-slot prefetch 4 commands ahead, and double-buffered async writes.

## Compared with alternatives

For anything multi-core or feature-bearing, pick Pogocache, Dragonfly, KeyDB or Garnet. In its own suite Pogocache already doubled Redis GET throughput at pipeline 1 with 8 threads, where RapidKV only ties Redis, and Dragonfly, KeyDB and Garnet carry real Redis data types and persistence. RapidKV is the pick only for a small, readable single-threaded C++20 codebase to learn from or mine for its FlatMap and CompactString, or for a one-core cache serving deeply pipelined plain GET/SET.

## Integration

| | |
|---|---|
| **Form** | standalone server binary built from source with CMake (its components are internal static libs); flatMap.h can be copied out as a header-only template, while CompactString also needs compactString.cpp and slabAllocator.cpp |
| **Dependencies** | Asio 1.36.0 (header-only, pulled by CMake FetchContent at configure time, so the build needs git and network access) and vendored rapidhash; GoogleTest 1.15.2 and Google Benchmark 1.9.1 only with -DBUILD_EXTRAS=ON |
| **Minimum toolchain** | C++20 and CMake 3.20+. The README claims GCC 12+ / Clang 15+ / MSVC 2022+, but the code includes &lt;format&gt; and calls std::format_to_n, and cppreference lists text formatting in libstdc++ only from GCC 13 (libc++ 17), so plan on GCC 13+. Release builds use -O3 -march=native -flto, so the binaries do not carry across CPUs. |
| **Platforms** | Little-endian only (the CompactString SSO flag lives in byte 15). The README gives Linux and Windows/MSVC build steps; the only benchmarks are on x86-64 Linux. Prefetching uses __builtin_prefetch or _mm_prefetch, with a no-op fallback. macOS and aarch64 are not documented. |
| **Thread safety** | The server runs every command on one Asio event-loop thread, so each command is atomic with respect to the others. The reusable pieces (FlatMap, Database) have no locking. SlabAllocator is a thread_local singleton, so CompactStrings should be destroyed on the thread that created them. |
| **Drop-in for the baseline** | partial — RESP2-compatible for the 13 listed commands only, and on port 8080 by default. Semantics also differ: EXPIRE takes milliseconds and TTL returns milliseconds where Redis uses seconds (there is no PEXPIRE or PTTL); SET accepts only PX; there is no SELECT; HELLO, CLIENT, INFO and COMMAND return 'ERR unknown command'; and a malformed or inline (non-array) request closes the connection instead of getting an error reply. |

## Gotchas

- Expiry checks read a cached steady_clock value that only the maintenance timer refreshes (every 100 ms by default, 200 ms in the sample config), so TTL resolution is that interval. The cached value starts at 0, so a key given a PX TTL before the first tick gets an absolute expiry near zero and expires at the first refresh.
- The README says the 7-bit hash tag 'avoids \~99% of false-positive key comparisons', but the tag is the hash's low 7 bits, which are also slot-index bits. Any entry that passes the PSL check therefore already has the same tag, and a full key compare always follows.
- The eviction the README calls SIEVE is really a CLOCK-style second-chance sweep in hash-slot order, with the visited bit set only by GET. It runs only after usage exceeds max_memory_usage, 10 keys per SET. If the limit is crossed mid-resize, every unvisited entry left in the old table is dropped as migration proceeds.
- Memory accounting counts the table arrays and slab slot sizes, but not unused slots in 1 MB slab pages (never returned to the OS) or the 64 KB read and write buffers of each connection, so RSS can exceed max_memory_usage. Separately, each connection has a hard 8 MB cap on unsent replies; exceeding it closes the socket without an error.

## Known shortcomings

- Parity with Redis at pipeline depth 1; the 3.01x/4.23x appear only at depth 100/500. 1 star, compiler and Redis version unstated.
- Resize bug (from reading flatMap.h, not run): during incremental doubling, keys past the migrate cursor cannot be found, so GET misses, DEL returns 0 and a stale value can overwrite a newer SET; untested. Not a Redis drop-in: EXPIRE/TTL in ms not s, SET PX only, no MGET/MSET/SELECT/HELLO, a bad request closes the connection.
- SECURITY: no AUTH or TLS, binds 0.0.0.0, and no bulk-length cap (unbounded read buffer). README claims are wrong (the 7-bit tag equals the slot bits so it skips no compares; 'SIEVE' is CLOCK over slot order; needs GCC 13+ for std::format, not 12+). TTL clock refreshed only every 100 ms; RSS can exceed max_memory_usage. Code written over three weeks in 2026-01/02; benchmarks unscripted on one laptop.

## Caveats and trade-offs

The benchmark is first-party and self-run with no independent verification. The compiler and Redis version are not stated, Redis io-threads settings are not stated, and the memtier command lines are not scripted in the repo (Tier C). The 4.2x headline is the best case at pipeline=500; at pipeline=1, throughput is at parity (+4% in one run, 0.99x in the sweep). The comparison is not feature-equivalent: RapidKV is single-threaded with string-only values, no persistence, replication, AUTH or TLS, and 13 commands against Redis's 400+. The repo has 1 star, and its first commit was 2026-01-31.

Single-threaded, no multi-core scaling; implements only a small subset of Redis commands (PING/ECHO/SET/GET/DEL/EXISTS/INCR/DECR/INCRBY/DECRBY/EXPIRE/PERSIST/TTL - no lists/hashes/sets/pub-sub/persistence/replication); SIEVE eviction approximates LRU rather than exact LRU

## Maintenance

The record calls it active because of the last push (2026-05-10), but that push only added the MIT license and deleted a CMakeSettings.json file; the code dates from a three-week burst ending 2026-02-22 (1 star, no releases, no issues), so treat it as a small, readable MIT reference whose FlatMap and CompactString can be copied out, not as a production cache without your own testing.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README Benchmarks section shows first-party memtier_benchmark tables against Redis on an AMD Ryzen 7 4800H, and every quoted number matches (130,019 vs 135,165; 1,119,012 vs 1,823,366; 1,718,018 vs 5,178,742 = 3.01x; 4.23x at pipeline=500). It stays C, not A: the memtier command lines are not scripted in the repo, the compiler and Redis version used are not stated, and benchmarks/ holds only Google Benchmark microbenchmarks.
- **Verifier notes:** The README also has Google Benchmark microbenchmarks against std: its FlatMap is 1.5-2.6x faster than std::unordered_map, and CompactString is up to 5.8x faster than std::string on moves. These could matter for the C++-first catalog, but compiler and flags for those runs are not stated either. Metadata checked: MIT, not a fork, not archived, 1 star, last commit 2026-05-10 (active).
- **Fields the verifier corrected:** `workload`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/shashank2602/RapidKV>
  - <https://github.com/shashank2602/RapidKV#benchmarks>
  - <https://raw.githubusercontent.com/shashank2602/RapidKV/master/CMakeLists.txt>
- **Sources the enricher read:**
  - <https://github.com/shashank2602/RapidKV>
  - <https://github.com/shashank2602/RapidKV#benchmarks>
  - <https://github.com/shashank2602/RapidKV/blob/master/CMakeLists.txt>
  - <https://github.com/shashank2602/RapidKV/blob/master/RapidKV.config>
  - <https://github.com/shashank2602/RapidKV/blob/master/inc/storage/flatMap.h>
  - <https://github.com/shashank2602/RapidKV/blob/master/inc/storage/database.h>
  - <https://github.com/shashank2602/RapidKV/blob/master/src/storage/database.cpp>
  - <https://github.com/shashank2602/RapidKV/blob/master/inc/storage/databaseErrors.h>
  - <https://github.com/shashank2602/RapidKV/blob/master/inc/storage/compactString.h>
  - <https://github.com/shashank2602/RapidKV/blob/master/src/storage/compactString.cpp>
  - <https://github.com/shashank2602/RapidKV/blob/master/inc/storage/slabAllocator.h>
  - <https://github.com/shashank2602/RapidKV/blob/master/src/storage/slabAllocator.cpp>
  - <https://github.com/shashank2602/RapidKV/blob/master/inc/server/connection.h>
  - <https://github.com/shashank2602/RapidKV/blob/master/src/server/connection.cpp>
  - <https://github.com/shashank2602/RapidKV/blob/master/src/server/server.cpp>
  - <https://github.com/shashank2602/RapidKV/blob/master/src/main.cpp>
  - <https://github.com/shashank2602/RapidKV/blob/master/src/commands/commands.cpp>
  - <https://github.com/shashank2602/RapidKV/blob/master/inc/commands/commandDispatcher.h>
  - <https://github.com/shashank2602/RapidKV/blob/master/src/commands/commandDispatcher.cpp>
  - <https://github.com/shashank2602/RapidKV/blob/master/inc/protocol/respParser.h>
  - <https://github.com/shashank2602/RapidKV/blob/master/src/protocol/respParser.cpp>
  - <https://github.com/shashank2602/RapidKV/blob/master/inc/utility/utility.h>
  - <https://github.com/shashank2602/RapidKV/blob/master/inc/utility/linearBuffer.h>
  - <https://github.com/shashank2602/RapidKV/blob/master/src/utility/linearBuffer.cpp>
  - <https://github.com/shashank2602/RapidKV/blob/master/inc/utility/config.h>
  - <https://github.com/shashank2602/RapidKV/blob/master/tests/testFlatMap.cpp>
  - <https://github.com/shashank2602/RapidKV/blob/master/tests/testIntegration.cpp>
  - <https://github.com/shashank2602/RapidKV/blob/master/benchmarks/benchmarkFlatMap.cpp>
  - <https://github.com/shashank2602/RapidKV/blob/master/benchmarks/CMakeLists.txt>
  - <https://github.com/shashank2602/RapidKV/commits/master>
  - <https://github.com/shashank2602/RapidKV/issues>
  - <https://en.cppreference.com/w/cpp/compiler_support/20>
  - <https://hn.algolia.com/api/v1/search?query=RapidKV&tags=story>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/shashank2602/rapidkv`) · [data/wave6/enrich/raw/github_com_shashank2602_rapidkv.json](../../../data/wave6/enrich/raw/github_com_shashank2602_rapidkv.json) (enrichment confidence 0.75)

</details>
