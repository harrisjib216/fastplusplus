# Masstree

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Caches](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Study only · `C++` · `MIT plus two clauses taken from the W3C license (no use of the copyright holders' names in publicity without prior written permission; title to copyright stays with the holders). It is a custom text, not a verbatim OSI/SPDX license; GitHub reports NOASSERTION.` · 🟡 stale

> Concurrent in-memory trie of B+-trees with ordered range scans; authors measured 1.5-3.7x Redis 2.4 throughput on 16 cores.

| | |
|---|---|
| **Beats** | Redis |
| **Claimed result** | Figure 13 of the EuroSys'12 paper, in millions of req/s on 16 cores. Uniform get: Masstree 9.10 vs Redis 5.97 (65.6%, \~1.5x derived from page data). Uniform put: 5.84 vs 2.97 (50.9%, \~2.0x derived). MYCSB-C all-get: 9.86 vs Redis 2.70 (27.4%, \~3.65x derived) and vs memcached 5.28 (53.6%, \~1.87x derived). MYCSB-A and MYCSB-B vs Redis: 6.05 vs 2.13 and 8.90 vs 2.69 (\~2.8x and \~3.3x derived). The paper says Masstree 'outperforms the other systems on almost all workloads, usually by a substantial margin', giving 'up to 3.7x the throughput' of Redis and memcached on non-uniform workloads. memcached is 7.4% faster on uniform get (9.78 vs 9.10). |
| **Workload** | Database of 20M key-value pairs on 16 cores, with logging and network I/O included (25 client machines over 10GbE). Two workload sets: (1) uniform get/put with 1-to-10-byte decimal keys and one 8-byte column, run for 60 s; (2) YCSB-derived MYCSB-A/B/C/E with Zipfian key popularity, 5-to-24-byte keys and ten 4-byte columns. Baselines are 16 Redis 2.4.5 processes and 16 memcached 1.4.8 processes. |
| **Metric** | throughput |
| **Hardware** | 48-core server with eight 2.4 GHz six-core AMD Opteron 8431 chips, Linux 3.1.5. Tests use 16 cores on up to three chips; the other cores are disabled. |
| **Adoption** | 459 stars |
| **Last commit** | 2023-10-12 |
| **Links** | [repository](https://github.com/kohler/masstree-beta) · [benchmark](https://pdos.csail.mit.edu/papers/masstree:eurosys12.pdf) |

## Verdict

In the authors' EuroSys 2012 paper, on 16 cores of a 2.4 GHz AMD Opteron 8431 server with networking and logging on, the full Masstree server did 9.10M uniform gets/s against 5.97M for 16 Redis 2.4.5 processes, 5.84M puts/s against 2.97M, and 6.05-9.86M against 2.13-2.70M on Zipfian MYCSB-A/B/C (about 1.5-3.7x), while memcached 1.4.8 was 7.4% faster on uniform gets. No compiler or flags are given, the baselines date from 2011, and the paper itself calls the comparisons 'not entirely fair'.

## Use it when

- You need an ordered in-memory index with range scans that many threads share, for example the index layer of an in-memory database or transactional store where a hash table cannot serve scans.
- Access is skewed (Zipfian) on a multicore box. At the paper's highest skew (delta=9), one shared Masstree delivered 3.5x the throughput of 16 hard-partitioned instances, which stall on the hot partition.
- Keys share long prefixes (URLs, hierarchical or composite keys). The trie layers compare each 8-byte slice once instead of re-comparing the whole key at every tree level.
- Workloads are small-key, small-value and read-heavy on x86-64 Linux. The paper measured 9-10M gets/s on 16 cores with networking and logging included.
- You want a reference design or research baseline. HN commenters note Masstree became a standard comparator in key-value store papers.

## Skip it when

- You want a Redis replacement. It has no RESP protocol, rich data types, TTLs or eviction (none found in the source), replication or clustering, and mtd is a research-grade server.
- You only do point lookups on uniform keys. The paper's own concurrent hash table reached 2.5x Masstree's throughput, 16 hard-partitioned Masstrees beat the shared tree by 1.5x on uniform gets, and memcached 1.4.8 was 7.4% faster on uniform gets.
- You target anything other than x86. The master branch hard-codes x86 inline asm (pause, mfence, prefetcht0, bswapq, rdtsc), and its acquire/release fences are compiler-only barriers that rely on x86 ordering. The arm64 port (PR #31) has been open and unmerged since 2018.
- You need an actively maintained dependency. The last commit was 2023-10-12, it has one old tag (v0.9.0) and no GitHub releases, and 9 issues remain open, including a scan race (#33) and empty leftmost leaves that are not freed after deleting all keys (#43).
- Your legal review cannot approve a custom license. It is MIT plus W3C-style publicity and title clauses, and GitHub shows NOASSERTION.

## How it is fast

Keys are cut into 8-byte slices stored as byte-swapped 64-bit integers, so each trie layer is a fanout-15 B+-tree that compares keys with plain integer compares (the paper credits this with 13-19%) and compares a long shared prefix only once per layer. Nodes are four cache lines and are prefetched whole before use, so each level costs about one DRAM latency. Readers use optimistic concurrency control (they check per-node version counters, take no locks and never write shared memory), while writers lock only the nodes they touch, publish a leaf insert in one step through a 64-bit permutation field, and free nodes through epoch-based (RCU-like) reclamation. The paper's factor analysis also credits a fast allocator and 2 MB superpages with a 27-37% gain.

## Compared with alternatives

Pick Masstree over MICA or MemC3 when you need ordered keys and range scans: both are hash-based, and MICA's paper reports 75.5-76.9 Mops against Masstree's 16.5 on tiny point operations. Prefer it over Garnet, Dragonfly or Valkey only if you are building your own storage engine and want an embeddable concurrent ordered index rather than a maintained server that speaks the Redis protocol.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | pthreads and libm. autoconf (2.69) is needed to bootstrap the build. Optional: jemalloc, tcmalloc, mimalloc, Hoard or Flow as the malloc, and libnuma. |
| **Minimum toolchain** | C++11 language features are required. configure retries with -std=gnu++1y and its error message asks for C++14. It needs GCC or Clang with GNU inline asm and __sync builtins. C++20/23 warnings were fixed in 2023 (PR #48). |
| **Platforms** | x86-64 only on master. The README says it is tested on Debian, Ubuntu and macOS, and a FreeBSD build fix was merged (PR #32). |
| **Thread safety** | Built for concurrency: many threads can get, put, remove and scan one table, each with its own threadinfo. Gets are lock-free optimistic reads and writers take per-node spinlocks. Scans are not atomic with respect to concurrent inserts or updates. Memory is reclaimed only if the embedder advances the global epoch and calls rcu_quiesce. |
| **Drop-in for the baseline** | no |

## Gotchas

- Embedding it means defining the globals the library expects (globalepoch, active_epoch and recovering, as unit-mt.cc does), creating a threadinfo per thread, and advancing epochs or calling rcu_quiesce regularly. Without that, freed nodes accumulate in per-thread limbo lists.
- Key handling does intentional 'sloppy' reads that can touch up to 8 bytes outside the key buffer (the preconditions are documented in string_slice.hh). Open issue #42 reports a possible segfault for key lengths that are not a multiple of 8, so pad key buffers and expect sanitizer reports.
- The write API is low-level. tcursor.find_insert() or find_locked() locks the leaf, you write lp.value(), and lp.finish(+1/0/-1, ti) must always be called because it applies the insert or remove and releases the lock.
- Assertions are compiled in by default. The README says to build with ./configure --disable-assertions before measuring performance, and the tree's node allocations go through the threadinfo pool allocator, so the malloc you link affects results.

## Known shortcomings

- Numbers are from the EuroSys'12 paper vs Redis 2.4.5 and memcached 1.4.8 (2012 versions); the license is MIT plus W3C-style publicity clauses (custom).
- Against memcached it is only +7.4% on uniform gets (the 2.5x figure is the authors' own hash table inside Masstree's framework). x86-only inline asm (arm64 PR #31 open since 2018); a source drop with no install/lib, and embedders must define epoch globals and run rcu_quiesce or memory is never freed. Open bugs: scan race (#33), empty leftmost leaves not freed (#43), reads outside the key buffer / possible segfault (#42). Stale since 2023-10; own protocol, no TTL or eviction (not Redis-compatible).

## Caveats and trade-offs

All numbers come from the authors' own EuroSys 2012 paper ('Cache Craftiness for Fast Multicore Key-Value Storage', Mao/Kohler/Morris), not from an independent third party. The paper itself says the system comparisons are 'not entirely fair'. The baselines are 2011-era Redis 2.4.5 and memcached 1.4.8, both hash tables, run as 16 partitioned processes. memcached beats Masstree by 7.4% on uniform gets. The hardware is 2012-era AMD Opteron, and the paper gives no compiler or flags. The LICENSE file is MIT plus W3C-style publicity and title clauses, a custom non-OSI text, so usability stays 'reference'. There have been no commits since 2023-10-12.

Masstree is a research B+-tree/trie key-value engine, not a drop-in Redis replacement: no rich data types (columns emulated via byte-range reads/writes on values), manual client-side sharding across processes/threads, and the same paper shows a plain partitioned hash table (memcached, single core) can beat Masstree by \~2.5x on pure uniform gets.

## Maintenance

Stale (last commit 2023-10-12, no GitHub releases, arm64 PR never merged) and under a custom MIT-plus-W3C-clause license, so treat it as a reference design to study, or to vendor after legal review, rather than a maintained dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** The paper is peer-reviewed (EuroSys 2012). Its Figure 13 measures Masstree against Redis 2.4.5 and memcached 1.4.8 on the same 16 cores. It is not A: the code is public (kohler/masstree-beta: mtd.cc, mtclient.cc) and the CPU model (AMD Opteron 8431) is stated, but the paper gives no compiler or flags.
- **Verifier notes:** Every Figure 13 number in the record matches the paper; the only change was marking the ratios as derived. The record said there was no license file, but a LICENSE file exists with MIT plus W3C-style clauses. It is not verbatim OSI, so usability stays 'reference'; the orchestrator may treat it as effectively permissive. The last commit, 2023-10-12, is about 2.9 years old, so the entry is stale, which the record already said.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `hardware`, `license`, `caveats`
- **Pages the verifier opened:**
  - <https://pdos.csail.mit.edu/papers/masstree:eurosys12.pdf>
  - <https://github.com/kohler/masstree-beta>
  - <https://github.com/kohler/masstree-beta/blob/master/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/kohler/masstree-beta>
  - <https://github.com/kohler/masstree-beta/blob/master/README.md>
  - <https://github.com/kohler/masstree-beta/blob/master/LICENSE>
  - <https://github.com/kohler/masstree-beta/blob/master/configure.ac>
  - <https://github.com/kohler/masstree-beta/blob/master/GNUmakefile.in>
  - <https://github.com/kohler/masstree-beta/blob/master/masstree.hh>
  - <https://github.com/kohler/masstree-beta/blob/master/compiler.hh>
  - <https://github.com/kohler/masstree-beta/blob/master/kvthread.hh>
  - <https://github.com/kohler/masstree-beta/blob/master/unit-mt.cc>
  - <https://github.com/kohler/masstree-beta/blob/master/masstree_tcursor.hh>
  - <https://github.com/kohler/masstree-beta/blob/master/masstree_insert.hh>
  - <https://github.com/kohler/masstree-beta/blob/master/masstree_struct.hh>
  - <https://github.com/kohler/masstree-beta/blob/master/masstree_key.hh>
  - <https://github.com/kohler/masstree-beta/blob/master/string_slice.hh>
  - <https://github.com/kohler/masstree-beta/blob/master/stringbag.hh>
  - <https://github.com/kohler/masstree-beta/blob/master/nodeversion.hh>
  - <https://github.com/kohler/masstree-beta/blob/master/ksearch.hh>
  - <https://github.com/kohler/masstree-beta/blob/master/mtd.cc>
  - <https://github.com/kohler/masstree-beta/blob/master/kvproto.hh>
  - <https://github.com/kohler/masstree-beta/commits/master>
  - <https://github.com/kohler/masstree-beta/tags>
  - <https://github.com/kohler/masstree-beta/issues?q=is%3Aissue>
  - <https://github.com/kohler/masstree-beta/issues/30>
  - <https://github.com/kohler/masstree-beta/pull/31>
  - <https://github.com/kohler/masstree-beta/issues/33>
  - <https://github.com/kohler/masstree-beta/issues/35>
  - <https://github.com/kohler/masstree-beta/issues/36>
  - <https://github.com/kohler/masstree-beta/issues/37>
  - <https://github.com/kohler/masstree-beta/issues/40>
  - <https://github.com/kohler/masstree-beta/issues/41>
  - <https://github.com/kohler/masstree-beta/issues/42>
  - <https://github.com/kohler/masstree-beta/issues/43>
  - <https://github.com/kohler/masstree-beta/issues/47>
  - <https://github.com/kohler/masstree-beta/issues/50>
  - <https://pdos.csail.mit.edu/papers/masstree:eurosys12.pdf>
  - <https://hn.algolia.com/api/v1/search?query=masstree>
  - <https://news.ycombinator.com/item?id=18199086>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/kohler/masstree-beta`) · [data/wave6/enrich/raw/github_com_kohler_masstree_beta.json](../../../data/wave6/enrich/raw/github_com_kohler_masstree_beta.json) (enrichment confidence 0.82)

</details>
