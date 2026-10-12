# Wormhole (fast ordered index)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Indexes](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `GPL-3.0` · 🔴 abandoned

> Concurrent in-memory ordered KV index in C fusing hash table, trie and B+-tree; lookups beat B+-tree, skip list, ART, Masstree.

| | |
|---|---|
| **Beats** | Skip list (extracted from LevelDB), STX B+-tree (fanout 128), Adaptive Radix Tree (libart from GitHub), Masstree (beta release) |
| **Claimed result** | Up to 8.4x, 4.9x, 4.3x and 6.6x key-lookup throughput vs skip list, B+ tree, ART and Masstree respectively (abstract and conclusion; these are not single-thread figures, and the paper's default is 16 threads). At 16 threads Wormhole beats the best other index by 1.3x-4.2x per keyset. Single-thread on Az1: 1.266 MOPS vs ART's 0.834 MOPS (about 52% higher). At 16 threads: 19.5 MOPS, 43% higher than ART. |
| **Workload** | In-memory point lookups with uniformly random search keys on 8 keysets: Amazon review metadata Az1/Az2 (142M keys, avg 40B), MemeTracker URLs 'Url' (192M keys, avg 82B), and synthetic random fixed-length keys K3-K10 (8B-1024B). There is 1-16 thread scaling on Az1, the per-keyset comparisons use 16 threads, and a networked variant ports the indexes to HERD over 100Gb/s InfiniBand. Baselines are thread-unsafe except Masstree. |
| **Metric** | throughput |
| **Hardware** | Dell R630, 2x 16-core Intel Xeon E5-2697A v4 (40MB LLC each), hyper-threading off, single NUMA node, 256GB DDR4-2400 ECC RAM, 64-bit Linux v4.15.15 |
| **Adoption** | 86 stars |
| **Last commit** | 2022-04-29 |
| **Links** | [repository](https://github.com/wuxb45/wormhole) · [benchmark](http://web.archive.org/web/20211016045757/https://www.cs.uic.edu/~wuxb/papers/wormhole.pdf) |

## Verdict

The EuroSys'19 paper ran uniformly random point lookups on 8 keysets (Amazon review metadata, MemeTracker URLs, random 8B-1KB keys) on a 2x16-core Xeon E5-2697A v4 server (one NUMA node, hyper-threading off). The baselines were LevelDB's skip list, the STX B+-tree (fanout 128), libart ART and Masstree. At 16 threads Wormhole beat the best other index by 1.3-4.2x per keyset; single-threaded on Az1 it did 1.266 MOPS vs ART's 0.834. Three of the four baselines ran without locking on read-only workloads, and neither the compiler/flags nor the comparison harness is published.

## Use it when

- Point lookups on long or variable-length string or binary keys (tens to hundreds of bytes, e.g. URLs or composite item|user|time keys), where a B+-tree's O(log N) full-key comparisons dominate. On 82-byte MemeTracker URLs the paper still measured at least 1.7x over every rival.
- Very large DRAM-resident indexes (hundreds of millions of keys). Lookup cost follows anchor length, not key count, and the Cuckoo Trie authors measured nearly constant Wormhole lookup throughput from 10M to 640M keys.
- Read-mostly multi-threaded services that need a thread-safe ordered map with iterators, callable from C or C++ on Linux, FreeBSD or macOS on x86-64 or AArch64, without adding an external lock.
- Keys containing arbitrary bytes, including NULs, or keys longer than 255 bytes. Per the author's notes in issue #5, HOT's implementation cannot handle these (it uses null-terminated keys of at most 255 bytes).
- Workloads that need atomic read-modify-write (merge), in-place value updates or range deletes under concurrency.

## Skip it when

- Fixed-size integer keys. The planned 64-bit-integer specialization (issue #8) never shipped. In the author's own test in issue #11, seek() over 10M random u64 keys took 7.5 s for absent keys vs 3.8 s for std::upper_bound on a sorted array, and only tied on present keys. KV pairs are allocated individually, which the author estimates at 2-3x the space of a packed array.
- Scan-heavy workloads. The paper measured only 1.05-1.59x over the STX B+-tree for 100-key range scans. There is no reverse iteration (no prev() or seek-for-less-equal). Cuckoo Trie's authors saw low scan throughput right after loading, because leaves are sorted lazily.
- Insert-heavy or bulk-load-heavy use. In the paper, single-thread insert throughput only matches LevelDB's skip list and falls below the B+-tree and skip list on long URL keys. The Cuckoo Trie authors found Wormhole's insert throughput saturating at high thread counts.
- Keysets with long shared prefixes, such as zero-padded keys. Long anchors mean more hash probes: with 512-byte keys that share all but their last 4 bytes, lookups fell from about 78% to 40% of a cuckoo hash table's throughput.
- Products that cannot take a GPL-3.0 dependency, or that need an actively maintained one. There have been no commits since April 2022 and there is no CI. A January 2026 request to relicense (issue #12) has had no reply.

## How it is fast

Leaves are B+-tree-style nodes of 128 keys linked in a sorted list. The internal nodes are replaced by a trie over the leaves' anchor keys (the MetaTrie), which is stored in a hash table (MetaTrieHT). A lookup runs a binary search over prefix length, hashing the key's prefixes incrementally with CRC32C and probing the table for the longest prefix match, so the cost is O(log L) in key length rather than O(log N) in key count. Table probes compare 16-bit hash tags with SSE or NEON before reading full keys. Inside a leaf, entries are ordered by tag so a point lookup jumps to a predicted slot (1-3 tag compares) instead of binary-searching (the paper's TagMatching, IncHashing, SortByTag and DirectPos). The paper's ablation says these raise the gain over the B+-tree from 1.26-2.25x for the base design to up to 4.9x. Concurrency uses per-leaf rwlocks, QSBR RCU and a second copy of the MetaTrieHT, so readers keep running while splits and merges update the trie.

## Compared with alternatives

Pick Wormhole over HOT or ART Synchronized when keys are long, binary or variable-length and you need a complete thread-safe ordered map with deletes, range deletes and merge. The author's single-thread numbers in issue #5 put it ahead of HOT on string keysets (1.80 vs 1.27 MOPS on Amazon keys). Cuckoo Trie beat Wormhole by up to 50% on YCSB-C in its SOSP'21 paper, but its own README says it is not robust enough for use in real programs.

## Integration

| | |
|---|---|
| **Form** | shared lib (make builds libwh.so) or source-drop (lib.c, kv.c, wh.c plus lib.h/kv.h/wh.h/ctypes.h) |
| **Dependencies** | pthread and libm; librt on Linux/FreeBSD and libexecinfo on FreeBSD. The Makefile links libbacktrace and liburing only if their headers are found. No other libraries. |
| **Minimum toolchain** | C (the Makefile uses -std=gnu18) with Clang (default, and faster per the README) or GCC. Minimum versions are not documented. The author reported a 2-4% regression with Clang 9. The headers are wrapped in extern "C", and the author's issue #11 benchmark includes them from C++17. |
| **Platforms** | Linux, FreeBSD, macOS. x86-64 with SSE4.2 required (AVX2 used if enabled), or AArch64 with NEON and the crc extension. Builds with -march=native by default. No Windows support. |
| **Thread safety** | The wh_\*, whsafe_\* and wormhole_\* APIs are thread-safe (per-leaf rwlocks plus QSBR RCU), including iterators; each thread needs its own ref. Under the wormhole_\* API an idle ref holder blocks writers doing splits, and it can deadlock if it waits on an external lock unless it parks or refreshes its qstate. whunsafe_\* needs external synchronization. The QSBR registry holds 23x32 refs; wh_ref returns NULL when its shard is full. |
| **Drop-in for the baseline** | no |

## Gotchas

- Linking lib.c installs process-wide constructors. Unless it is built with -DNOSIGNAL (make O=ns), a SIGSEGV, SIGFPE, SIGILL or SIGBUS anywhere in the host process prints a backtrace and then sleeps forever 'waiting for GDB' instead of crashing. Internal fatal errors (debug_die) do the same. It also tries to mlock() every mmap'd region and prints 'mlock disabled' to stderr when that fails.
- With the struct-kv APIs, the caller must keep each key's CRC32C hash current (kv_update_hash / kref_refill_hash32). Only debug builds assert this.
- Keys are compared as byte strings, so integer keys must be byte-swapped to big-endian (e.g. __builtin_bswap64) to sort numerically.
- The main tuning knobs are compile-time macros in wh.c and lib.c: keys per leaf (WH_KPN, default 128; 256 is 5-10% faster for point operations, 64 is better for scans), slab and hugepage size, and QSBR capacity. A split fails if 129 keys share a common prefix of 65,535+ bytes. In-place update callbacks must change only value bytes, or the index is corrupted.

## Known shortcomings

- The up-to 8.4/4.9/4.3/6.6x gains use the paper's default 16 threads; single-thread it is 1.266 vs 0.834 MOPS on the Az1 Amazon keyset; the repo has no harness against the baselines (LevelDB skiplist, STX B+tree, libart, Masstree).
- For u64 keys, seek on absent keys is 2x slower than std::upper_bound (the author, #11) and uses 2-3x the space of a packed array; scans are only 1.05-1.59x over a B+tree with no prev() and are slow right after load (lazy leaf sort); inserts run at about skip-list speed and saturate at high thread counts; Cuckoo Trie has up to 50% faster lookups. lib.c constructors hijack SIGSEGV and hang the process 'waiting for GDB' unless built with -DNOSIGNAL (plus mlock and stderr noise); an idle wormhole reference blocks writers (deadlock risk). GPL-3.0 (relicense request #12 unanswered); no commits since 2022-04, no CI.

## Caveats and trade-offs

Evidence is the EuroSys'19 peer-reviewed paper plus the authors' reference implementation. Hardware is fully specified, but the paper gives no compiler or flags. The repo Makefile defaults to clang with -O3 -flto, but that is not tied to the paper's runs. The comparison harness for skip list/B+tree/ART/Masstree is not in the repo, which has only Wormhole's own concbench/stresstest. The 'up to' ratios are best cases across keysets; per-keyset gains over the best competitor are 1.3x-4.2x. The repo has had no commits since April 2022.

Combines a hash table, prefix trie, and B+-tree to keep fast range/point ops without sacrificing space versus B+-tree/skip list; concurrent access requires thread-local reference/RCU handles (wh_ref), adding a small per-op cost versus the thread-unsafe variant (\~7.8% throughput loss when made thread-safe); plain C API, requires SSE4.2 on x86_64 or NEON+crc on AArch64

## Maintenance

Abandoned since an April 2022 'minor sync' commit; a copy of wh.c also ships in the author's RemixDB, last pushed March 2023. It is GPL-3.0, which rules out permissive-license products, but at about 10k lines of plain C in three modules it is small enough to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** This is a peer-reviewed EuroSys'19 paper comparing Wormhole against LevelDB's skip list, the STX B+-tree, libart ART and Masstree, with the CPU model and full hardware stated. The paper does not state a compiler or flags, and the repo contains only Wormhole's own concbench/stresstest, not the harness that compares against the baselines, so it is not A.
- **Verifier notes:** All quoted numbers and the hardware were checked against the archived paper PDF. The record wrongly called the up-to ratios single-thread figures and described the data as URL/webpage keys; the single-thread numbers use the Amazon Az1 keyset. Metadata matches: GPL-3.0, not archived or a fork, 86 stars, last commit 2022-04-29.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `baseline`, `caveats`
- **Pages the verifier opened:**
  - <http://web.archive.org/web/20211016045757/https://www.cs.uic.edu/~wuxb/papers/wormhole.pdf>
  - <https://github.com/wuxb45/wormhole>
  - <https://github.com/wuxb45/wormhole/blob/master/README.md>
  - <https://github.com/wuxb45/wormhole/blob/master/Makefile.common>
- **Sources the enricher read:**
  - <https://github.com/wuxb45/wormhole>
  - <https://github.com/wuxb45/wormhole/blob/master/README.md>
  - <https://github.com/wuxb45/wormhole/blob/master/wh.h>
  - <https://github.com/wuxb45/wormhole/blob/master/wh.c>
  - <https://github.com/wuxb45/wormhole/blob/master/lib.c>
  - <https://github.com/wuxb45/wormhole/blob/master/lib.h>
  - <https://github.com/wuxb45/wormhole/blob/master/Makefile>
  - <https://github.com/wuxb45/wormhole/blob/master/Makefile.common>
  - <https://github.com/wuxb45/wormhole/commits/master>
  - <https://github.com/wuxb45/wormhole/issues?q=is%3Aissue>
  - <https://github.com/wuxb45/wormhole/pulls?q=is%3Apr>
  - <https://github.com/wuxb45/wormhole/issues/1>
  - <https://github.com/wuxb45/wormhole/issues/2>
  - <https://github.com/wuxb45/wormhole/issues/5>
  - <https://github.com/wuxb45/wormhole/issues/6>
  - <https://github.com/wuxb45/wormhole/issues/7>
  - <https://github.com/wuxb45/wormhole/issues/8>
  - <https://github.com/wuxb45/wormhole/issues/10>
  - <https://github.com/wuxb45/wormhole/issues/11>
  - <https://github.com/wuxb45/wormhole/issues/12>
  - <http://web.archive.org/web/20211016045757/https://www.cs.uic.edu/~wuxb/papers/wormhole.pdf>
  - <https://github.com/wuxb45/remixdb>
  - <https://news.ycombinator.com/item?id=20389076>
  - <https://export.arxiv.org/api/query?search_query=abs:Wormhole+AND+abs:index&max_results=20>
  - <https://arxiv.org/pdf/2201.09331v1>
  - <https://github.com/cuckoo-trie/cuckoo-trie-code/blob/master/README.md>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/wuxb45/wormhole`) · [data/wave6/enrich/raw/github_com_wuxb45_wormhole.json](../../../data/wave6/enrich/raw/github_com_wuxb45_wormhole.json) (enrichment confidence 0.8)

</details>
