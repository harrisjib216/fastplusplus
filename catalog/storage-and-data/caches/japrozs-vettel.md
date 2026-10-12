# Vettel

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Caches](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🔴 abandoned

> A \~300-line C CLI key-value store on one flat text file; its README times it slightly faster than redis-cli.

| | |
|---|---|
| **Beats** | Redis |
| **Claimed result** | 10.72s (vettel) vs 13.26s (redis) wall time to add 1000 keys, about 1.24x (derived from page data) |
| **Workload** | 1000 sequential set commands, each spawned as a separate process from Python os.system: 'vt -c "set k v"' (vettel appends to a flat file) vs 'redis-cli set k v' (TCP round trip to a Redis server), timed with the fish shell's time |
| **Metric** | throughput |
| **Hardware** | MacBook Pro (13-inch, Mid 2012), 2.5 GHz Dual-Core Intel Core i5, 16 GB 1600 MHz DDR3, macOS Catalina 10.15.7 (from the README screenshot assets/my_machine.png; the exact i5 SKU is not named) |
| **Compiler and flags** | vettel: clang -Wall -Wextra -pedantic with no optimization flag (default -O0), per make.sh; Redis/redis-cli build unstated |
| **Adoption** | 3 stars |
| **Last commit** | 2023-02-12 |
| **Links** | [repository](https://github.com/japrozs/vettel) · [benchmark](https://github.com/japrozs/vettel/blob/master/README.md) |

## Verdict

A Python script ran os.system 1000 times. Each call started a shell, which ran either `vt -c "set k v"` (an unoptimized clang build appending to \~/.store.vt) or `redis-cli set k "v"` (default host, so a local Redis server; the Redis version, build and persistence settings are unstated). A single run, timed with fish's `time` on a MacBook Pro 13-inch Mid 2012 (2.5 GHz dual-core Core i5, 16 GB DDR3, macOS 10.15.7), took 10.72 s vs 13.26 s: about 10.7 ms vs 13.3 ms per key, or 1.24x (derived). This measures process-spawn plus IPC overhead, not the throughput of either store.

## Use it when

- Reading \~300 lines of C to learn how a naive flat-file key-value CLI works (parsing, append-only writes, rewrite-on-delete)
- A personal shell scratchpad of at most a few hundred string keys on a single-user macOS machine, where losing data is acceptable
- A teaching example of benchmark pitfalls: timing process spawn plus a local file append against a client/server network round trip

## Skip it when

- As a Redis replacement or as a cache: there is no server, no network protocol, no data types, no TTL, no eviction and no memory bound
- Any store past a few hundred keys: every set and get is a full linear scan of the file, and delete rewrites the whole file
- Concurrent writers: there is no file locking, so check-then-append can create duplicate keys, and a delete's read-truncate-rewrite can drop a concurrent append
- Anything that needs durability: there is no fsync, and delete opens the store with mode "w" (truncating it) before writing it back, so a crash mid-delete can empty the store
- Production or security-sensitive use: the C has undefined behavior (see gotchas), was built at -O0, and has no tests, CI, releases or issue tracker activity

## How it is fast

It has no speed technique. `set` scans the whole store file line by line to reject a duplicate key and then appends one line with fopen("a"); `get` is the same O(n) scan. It 'wins' only because each benchmarked call is a short-lived process doing a local file append, while redis-cli also pays a TCP connect and a request/response round trip to a Redis server, and process creation dominates both timings (5.10 s vs 6.27 s sys time). The one comment on the Feb 2023 Show HN post made the same O(n) point and expected Redis to win by a wide margin with more data.

## Compared with alternatives

Pick it only when you want a tiny, readable toy. For an embedded, serverless local store that really beats Redis on local get latency, use python-diskcache. For a faster Redis-protocol server, use Valkey, Pogocache or Dragonfly.

## Integration

| | |
|---|---|
| **Form** | source-drop (one main.c that builds a CLI executable, out/vt; a prebuilt out/vt binary is committed; there is no library API) |
| **Dependencies** | libedit (editline/readline.h, -ledit). make.sh hard-codes MacPorts paths under /opt/local. |
| **Minimum toolchain** | Not documented. make.sh uses clang with -Wall -Wextra -pedantic, no -std and no -O flag. The code needs POSIX getline, BSD/GNU vasprintf and the non-standard `uint` type. |
| **Platforms** | Only macOS (MacPorts) has a build script, and the author's benchmark machine is a 2012 Intel MacBook Pro. Linux and Windows are not documented; glibc would likely need _GNU_SOURCE for vasprintf. |
| **Thread safety** | Not documented. It runs one command per process with no locking of the shared \$HOME/.store.vt file. |
| **Drop-in for the baseline** | no |

## Gotchas

- delete matches by prefix: delete_key uses strncmp with strlen(key), so `del user` also removes `user1`, `username` and so on (get uses an exact comparison)
- set is insert-only and errors with 'a record with key ... already exists', so an update means delete then set. Every command exits with status 0, even on errors and misses, so scripts must parse stdout.
- Parsing is fragile: keys containing ':' break the key:value format, values are split on spaces and rejoined with single spaces, and the code relies on overlapping sprintf plus an uninitialized malloc buffer in delete (undefined behavior)
- get_store_path calls fclose() on a NULL FILE\* when the store file does not exist yet. That is undefined behavior and likely crashes the first run, after which the empty file exists.

## Known shortcomings

- Built at -O0 (no -O flag in make.sh), and the benchmark spawns a process per key (vt -c vs redis-cli), measuring process startup rather than store speed; 2012 MacBook Pro; abandoned.
- No speed technique: set/get are an O(n) linear scan of a flat file, and the 'win' is a process spawn plus file append vs a redis-cli TCP round trip. CLI only (no server, RESP, TTL or eviction; the old TCP server was removed); not a cache. Bugs: delete prefix-matches (del user also removes user1), exit code always 0, fclose(NULL) on first run (UB), overlapping sprintf (UB); no locking or fsync and delete truncates then rewrites (a crash can wipe the store). macOS/MacPorts-only build at -O0; abandoned since 2023-02.

## Caveats and trade-offs

The benchmark measures per-key process spawn: the vt CLI doing a flat-file append vs redis-cli doing a TCP round trip to a Redis server. It does not measure store throughput, so it is not a like-for-like comparison with a Redis server. Vettel is a \~300-line single-file C store with no server. The margin is small (about 1.24x), from a single run, on a 2012 laptop, and vettel itself was built at -O0. Not independently reproduced.

\~300 lines of C, minimal command set, single-threaded, no documented persistence/consistency guarantees; toy-scale project

## Maintenance

Abandoned since 2023-02-12 after 12 commits, with no releases, no issues and one fork that has no later pushes; the code is MIT-licensed and readable in minutes but not usable as a real store.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README has one first-party timing (10.72s vettel vs 13.26s redis for 1000 keys), and the scripts are public (benchmarks/vettel.py, benchmarks/redis.py). make.sh builds vettel without any -O flag (an unoptimized -O0 build), which caps it at C, and the Redis build is unstated.
- **Verifier notes:** The numbers are on the page, but the 1.24x ratio is derived. The screenshot gives the hardware more precisely than the record did. The comparison is methodologically weak (it is dominated by process startup) but is a real, recognizable Redis comparison, so it is kept at C. The MIT license is confirmed; the last commit is 2023-02-12, so it stays abandoned.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `hardware`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/japrozs/vettel>
  - <https://github.com/japrozs/vettel/blob/master/README.md>
  - <https://raw.githubusercontent.com/japrozs/vettel/master/README.md>
  - <https://raw.githubusercontent.com/japrozs/vettel/master/benchmarks/vettel.py>
  - <https://raw.githubusercontent.com/japrozs/vettel/master/benchmarks/redis.py>
  - <https://raw.githubusercontent.com/japrozs/vettel/master/make.sh>
  - <https://raw.githubusercontent.com/japrozs/vettel/master/main.c>
  - <https://raw.githubusercontent.com/japrozs/vettel/master/LICENSE>
  - <https://raw.githubusercontent.com/japrozs/vettel/master/assets/my_machine.png>
- **Sources the enricher read:**
  - <https://github.com/japrozs/vettel>
  - <https://github.com/japrozs/vettel/blob/master/README.md>
  - <https://github.com/japrozs/vettel/blob/master/main.c>
  - <https://github.com/japrozs/vettel/blob/master/make.sh>
  - <https://github.com/japrozs/vettel/blob/master/benchmarks/vettel.py>
  - <https://github.com/japrozs/vettel/blob/master/benchmarks/redis.py>
  - <https://github.com/japrozs/vettel/blob/master/benchmarks/data.py>
  - <https://github.com/japrozs/vettel/blob/master/LICENSE>
  - <https://raw.githubusercontent.com/japrozs/vettel/master/assets/my_machine.png>
  - <https://github.com/japrozs/vettel/commits/master>
  - <https://github.com/japrozs/vettel/commit/bc7526e>
  - <https://github.com/japrozs/vettel/commit/2d5d6d7>
  - <https://github.com/japrozs/vettel/issues>
  - <https://github.com/japrozs/vettel/releases>
  - <https://github.com/japrozs/vettel/forks>
  - <https://github.com/mobiliodevelopment/vettel>
  - <https://hn.algolia.com/api/v1/search?query=vettel%20key%20value&tags=story>
  - <https://news.ycombinator.com/item?id=34760870>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/japrozs/vettel`) · [data/wave6/enrich/raw/github_com_japrozs_vettel.json](../../../data/wave6/enrich/raw/github_com_japrozs_vettel.json) (enrichment confidence 0.85)

</details>
