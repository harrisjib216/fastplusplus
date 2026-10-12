# RadixSpline

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Indexes](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Single-pass, read-only learned index (spline + radix table) for sorted uint32/uint64 arrays; beats STX B+Tree lookups at \~1/40th the size.

| | |
|---|---|
| **Beats** | B-tree (STX B-Tree) |
| **Claimed result** | 266.58 ns/lookup (4.0 MB) for RS vs 482.11 ns/lookup (166.0 MB) for BTree (STX B+ Tree) on the 32-bit version of the amzn dataset, fastest variant of each -&gt; \~1.8x lower latency at \~41x less space (derived from page data, Table 2) |
| **Workload** | Point lookups (10M random lookup keys) on the SOSD amzn (books) dataset of 200M keys. Table 2 specifically uses a 32-bit version of amzn and reports the best-performing (often largest) variant of each index structure, comparing RadixSpline (RS) against the STX B+ Tree, IBTree, FAST, binary search, PGM, RMI, CuckooMap and RobinHash. The Pareto plots (Fig. 7) cover 64-bit keys over amzn/face/osm/wiki. |
| **Metric** | latency |
| **Hardware** | Intel Xeon Gold 6230 CPU @ 2.10GHz, 256GB RAM |
| **Compiler and flags** | Not stated in the paper. The SOSD repo build (scripts/prepare.sh, CMakeLists.txt) uses CMAKE_BUILD_TYPE=Release, C++17, -ffast-math -march=native, and -fopenmp if available. The compiler is not pinned; the README installs clang on Ubuntu 20.04. |
| **Adoption** | 141 stars |
| **Last commit** | 2021-05-13 |
| **Links** | [repository](https://github.com/learnedsystems/RadixSpline) · [benchmark](http://www.vldb.org/pvldb/vol14/p1-marcus.pdf) |

## Verdict

SOSD paper (PVLDB 14(1), Table 2): 32-bit version of the 200M-key amzn dataset, 10M random lookups, single-threaded, Xeon Gold 6230 @ 2.10GHz, fastest variant of each index. RS averaged 266.58 ns/lookup with a 4.0 MB index vs 482.11 ns and 166.0 MB for the STX B+Tree (about 1.8x lower latency, about 41x smaller), with the last-mile binary search included. No compiler is named (the SOSD build is CMake Release with -march=native), and no std:: container was measured.

## Use it when

- Immutable or write-once sorted arrays of uint32/uint64 keys that get rebuilt in bulk, such as LSM-tree runs or SSTables at compaction time. The paper's preliminary RocksDB swap on osmc (50/50 reads/writes) cut total time from 712 s to 521 s and memory use by about 45%.
- Point or lower_bound lookups where both latency and index memory matter. On SOSD 32-bit amzn the best RS was about 1.8x faster than the best STX B+Tree with a 4 MB vs 166 MB index.
- When a learned index must build fast. SOSD measured 20 s for RS vs 38 s for PGM and 80 s for RMI on the largest (800M-key) dataset, with constant work per key.
- Range and predecessor queries over sorted data, which hash tables cannot serve.
- Smooth real-world key distributions (amzn/wiki-like CDFs) where tuning just two knobs (radix bits, spline error) to hit a memory budget is acceptable.

## Skip it when

- Any inserts, updates or deletes. It is strictly read-only and needs a full rebuild; use a B-tree or an updatable learned index (ALEX, LIPP, dynamic PGM).
- Key sets with a few extreme outliers or empty high-bit ranges. On SOSD face, about 100 keys in (2^59, 2^64-1) against a bulk below 2^50 made the radix table nearly useless. The aiDM paper's fastest face config needed over 600 MiB (39% of the key data).
- Pure point lookups with memory to spare. In the same Table 2, RobinHash (93.69 ns) and CuckooMap (114.50 ns) beat RS (266.58 ns), and RMI (180.90 ns at 48 MB) was also faster.
- Non-uint keys (strings, floats, signed or composite keys) are not supported. 32-bit keys give essentially no gain over 64-bit, because RS converts keys to 64-bit floats.
- Production use needing support. There have been no commits since May 2021, no releases or packages, and GCC/Clang builtins with no Windows/MSVC build. A 2023 PR arguing that the spline-cut condition is stricter than the paper (more knots than needed) was closed unmerged.

## How it is fast

It first fits an error-bounded linear spline to the key-&gt;position CDF using GreedySplineCorridor (Neumann & Michel, BNCOD'08). This runs in one pass with constant work per key and guarantees that interpolating between two knots lands within max_error positions of the true one. A flat radix table (a uint32 array indexed by the top r bits of key - min_key, with common prefix bits removed, similar to one ART Node256 level) narrows the search to a few spline points, which are scanned linearly (&lt;32) or binary-searched. An FMA interpolation then gives the estimate, followed by a short binary search over about 2\*max_error+2 elements. A lookup is therefore a shift, one table load, a short knot search and a tiny last-mile search, instead of a walk down several B-tree levels.

## Compared with alternatives

Choose RS over PGM-index or RMI when the data is immutable, rebuilt often, and build time matters. It built 800M keys in 20 s vs 38 s for PGM and 80 s for RMI, and on 32-bit amzn it beat PGM's lookup (266.58 vs 326.48 ns) with a smaller index, though RMI was faster (180.90 ns at 48 MB). Choose ALEX or LIPP instead when you need inserts.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (GoogleTest only for the repo's own tests, pulled by CMake) |
| **Minimum toolchain** | C++14 per CMakeLists.txt (CMake 3.10+). Needs GCC or Clang for __builtin_clz/__builtin_clzl; no minimum compiler version documented. |
| **Platforms** | Not documented. The code is plain C++ apart from the GCC/Clang builtins; __builtin_clzl on 64-bit keys assumes a 64-bit long (LP64 Linux/macOS). The repo's CMake adds -march=native, but only for its own example/bench/test targets. CI runs on an unspecified self-hosted runner. |
| **Thread safety** | Not documented. After Finalize(), RadixSpline and MultiMap lookups are const with no mutable state, so concurrent readers are safe by construction; SOSD ran RS lookups on 40 threads. Builder is single-threaded, and there are no mutating operations at all. |
| **Drop-in for the baseline** | partial — rs::MultiMap mimics std::multimap's find/lower_bound/begin/end/size over a sorted copy, but has no insert/erase/upper_bound/equal_range/count. The core rs::RadixSpline only returns a search bound into your own array, so it cannot replace a mutable B-tree. |

## Gotchas

- Builder preconditions are checked only by assert(): keys added in sorted order, min/max known up front, and the last key equal to max_key. In NDEBUG builds a violation silently yields wrong bounds, and a key above max_key can write past the end of the radix table.
- The radix table is a flat uint32 array of up to 2^r+2 entries, whatever the data size. The default r=18 costs about 1 MiB even for tiny inputs, and bench.cc's tuned configs go up to r=28 (up to about 1 GiB).
- Only uint32_t/uint64_t compile, because GetNumShiftBits overloads only those. When all keys are equal (min==max), 0 is passed to __builtin_clz, which is formally undefined, although the SingleKey/AllMinKeys tests pass.
- Serializer writes raw native-endian size_t/key/double fields with no header, version or length checks. The bytes are not portable across architectures and are unsafe to load from untrusted input.

## Known shortcomings

- Read-only (no insert/erase; full rebuild). On the face dataset (outliers) the radix table is nearly useless and the best config exceeds 600 MiB; hash tables and RMI are faster on point lookups (Table 2). uint32/uint64 keys only; clz(0) UB when all keys are equal; builder preconditions are assert-only, so NDEBUG builds can write past the radix table. The serializer is raw native-endian with no checks; abandoned since 2021-05 with 3 unmerged PRs.

## Caveats and trade-offs

Same SOSD/VLDB'21 paper as the RMI entry. The CPU is stated and the SOSD harness is public, but no compiler is named (flags only in the SOSD CMake build), so it is capped at Tier B. Table 2 numbers are for a 32-bit version of amzn and are the fastest variant per structure. RS beats PGM (326.48 ns) but trails RMI (180.90 ns), and both hash tables (CuckooMap 114.50 ns, RobinHash 93.69 ns) beat every ordered index at far larger size. RS and RBS degrade badly on the face dataset because of outliers. It is a header-only C++ library whose last commit on master is 2021-05-13 (the 2023-04-28 date is only the repo pushed_at). The SOSD harness itself is GPL-3.0, while the RS library is MIT.

Read-only, single-pass build; can be built as a drop-in replacement for std::multimap over sorted data. Degrades badly on data with a small number of extreme outliers (e.g. the 'face' dataset in SOSD), where its radix table becomes nearly useless.

## Maintenance

Abandoned: the last commit on master is 2021-05-13 (tuning configs only; the last functional change, a serializer, landed 2021-03-03), and three outside PRs were closed unmerged. Still, it is MIT-licensed and five small dependency-free headers, so vendoring and patching it yourself is easy.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** This is a peer-reviewed PVLDB 14(1) paper ('Benchmarking Learned Indexes'). Its Table 2 lists RS at 266.58 ns / 4.0 MB against the STX B+ Tree [6] at 482.11 ns / 166.0 MB, and the setup section states the CPU (Xeon Gold 6230 @ 2.10GHz, 256 GB RAM). The SOSD harness is public (learnedsystems/SOSD, benchmarks/ + scripts/prepare.sh + CMakeLists.txt), but neither the paper nor the repo pins a compiler, so it cannot be A.
- **Verifier notes:** Numbers and the STX B-Tree baseline check out, but Table 2 is explicitly on a 32-bit version of amzn, not the 64-bit keys the record claimed; I fixed the workload. last_commit was the repo pushed_at; the real last commit on master is 2021-05-13, so it is still abandoned. License MIT, 141 stars, not a fork and not archived were all verified.
- **Fields the verifier corrected:** `workload`, `claimed_speedup`, `compiler_and_flags`, `last_commit`, `caveats`
- **Pages the verifier opened:**
  - <http://www.vldb.org/pvldb/vol14/p1-marcus.pdf>
  - <https://github.com/learnedsystems/RadixSpline>
  - <https://github.com/learnedsystems/SOSD>
  - <https://github.com/learnedsystems/SOSD/blob/master/CMakeLists.txt>
  - <https://github.com/learnedsystems/SOSD/blob/master/README.md>
  - <https://github.com/learnedsystems/SOSD/blob/master/scripts/prepare.sh>
- **Sources the enricher read:**
  - <https://github.com/learnedsystems/RadixSpline>
  - <https://github.com/learnedsystems/RadixSpline/blob/master/README.md>
  - <https://github.com/learnedsystems/RadixSpline/blob/master/include/rs/builder.h>
  - <https://github.com/learnedsystems/RadixSpline/blob/master/include/rs/radix_spline.h>
  - <https://github.com/learnedsystems/RadixSpline/blob/master/include/rs/multi_map.h>
  - <https://github.com/learnedsystems/RadixSpline/blob/master/include/rs/common.h>
  - <https://github.com/learnedsystems/RadixSpline/blob/master/include/rs/serializer.h>
  - <https://github.com/learnedsystems/RadixSpline/blob/master/CMakeLists.txt>
  - <https://github.com/learnedsystems/RadixSpline/blob/master/.github/workflows/main.yml>
  - <https://github.com/learnedsystems/RadixSpline/blob/master/bench.cc>
  - <https://github.com/learnedsystems/RadixSpline/blob/master/example.cc>
  - <https://github.com/learnedsystems/RadixSpline/blob/master/test/radix_spline_test.cc>
  - <https://github.com/learnedsystems/RadixSpline/blob/master/test/multi_map_test.cc>
  - <https://github.com/learnedsystems/RadixSpline/blob/master/LICENSE>
  - <https://github.com/learnedsystems/RadixSpline/commits/master>
  - <https://github.com/learnedsystems/RadixSpline/issues/1>
  - <https://github.com/learnedsystems/RadixSpline/pull/2>
  - <https://github.com/learnedsystems/RadixSpline/pull/3>
  - <https://github.com/learnedsystems/RadixSpline/pull/4>
  - <http://www.vldb.org/pvldb/vol14/p1-marcus.pdf>
  - <https://arxiv.org/pdf/2004.14541>
  - <https://arxiv.org/abs/2108.05117>
  - <https://news.ycombinator.com/item?id=25901362>
  - <https://news.ycombinator.com/item?id=30617139>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/learnedsystems/radixspline`) · [data/wave6/enrich/raw/github_com_learnedsystems_radixspline.json](../../../data/wave6/enrich/raw/github_com_learnedsystems_radixspline.json) (enrichment confidence 0.86)

</details>
