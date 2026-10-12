# PLEX / TrieSpline

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Indexes](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Read-only learned index for sorted integer keys: error-bounded spline plus auto-tuned radix tree; \~2x faster lookups than B-tree.

| | |
|---|---|
| **Beats** | B-tree (and ART, PGM-index) |
| **Claimed result** | Graph-only. In Fig. 3 (size vs lookup time, 200M 64-bit keys) the PLEX curve lies at roughly 200-300 ns against BTree's roughly 500-900 ns and ART's roughly 400-600 ns on amzn and face (approximate, read from the plot). The text gives no ratio. It says 'PGM, ART, and BTree eventually lose performance as the index size is increased', and it notes that PLEX fixes RadixSpline's outlier problem on face and sits at a constant offset of about 25 ns from RMI on amzn and face. In the plot, RMI is the faster of the two. |
| **Workload** | Four 64-bit SOSD real-world datasets (amzn, face, osm, wiki; 200M keys each). Build time vs size is compared against RMI, CHT, PGM and RadixSpline (Fig. 2). Lookup time vs size is compared against those plus ART and BTree (Fig. 3). |
| **Metric** | latency |
| **Hardware** | AWS m5zn.metal instance, 48 vCPUs at 4.5GHz turbo, 192GiB RAM |
| **Adoption** | 16 stars |
| **Last commit** | 2022-06-30 |
| **Links** | [repository](https://github.com/stoianmihail/PLEX) · [benchmark](https://arxiv.org/pdf/2108.05117) |

## Verdict

Fig. 3 of the AIDB@VLDB'21 extended abstract plots lookup time against index size for 200M-key 64-bit SOSD datasets (amzn, face, osm, wiki), run on an AWS m5zn.metal (48 vCPUs, 4.5 GHz turbo, 192 GiB). Read off the plot, PLEX's best points (about 190-255 ns) sit roughly 2-2.7x below SOSD's BTree baseline at its best (about 505-515 ns) and below ART (about 360-450 ns; ART is not plotted on wiki). RMI stays about 25 ns faster on amzn and face, and the paper states no exact numbers, compiler or flags (the repo's CMake uses C++17 with -march=native).

## Use it when

- Static or bulk-loaded sorted arrays of 32/64-bit unsigned integer keys (IDs, timestamps, cell IDs) in the 10^6 to 10^8+ range, where you rebuild rather than update
- You want roughly half of a B-tree's lookup latency over the same sorted array (best points about 190-255 ns vs about 505-515 ns for BTree on 200M-key SOSD data, read from the plot) with an index that can be KBs to MBs
- You want one knob (max error epsilon) and a fast rebuild: about 1-2 s for 200M keys including auto-tuning, against about 10-20 s for RMI plus its offline grid search (Fig. 2)
- Distributions with outliers or long shared key prefixes that defeat RadixSpline's flat radix table (the paper's 'face' dataset), since PLEX switches to a CHT there
- Keys with duplicates: the spline only records distinct keys, so duplicate-heavy data (e.g. 'wiki') works, unlike the paper's standalone CHT

## Skip it when

- Any workload with inserts, deletes or in-place updates: the structure is read-only and a change means a full rebuild (the Fenwick-tree update extension was only proposed as future work)
- Non-integer or signed keys (strings, floats, composite keys): only uint32_t and uint64_t overloads of the bit helpers exist
- When peak lookup latency matters more than build cost: RMI sits about 25 ns lower on amzn and face, and the standalone CHT is lower on osm in the paper's own Fig. 3
- Production code that needs a maintained dependency: abandoned since mid-2022, 16 stars, a reported out-of-bounds crash on sequential keys (issue #4, Feb 2024) and a radix-layer off-by-one patch (PR #3, June 2022), both unresolved
- MSVC/Windows builds: it relies on GCC/Clang __builtin_clz/__builtin_clzl, and the 64-bit path assumes a 64-bit 'long'

## How it is fast

A greedy error-bounded linear spline (GreedySplineCorridor, Neumann & Michel, BNCOD'08) is fitted in one O(N) pass, so every prediction lands within epsilon positions of the true slot. The spline points are indexed either by a flat radix table (as in RadixSpline) or by a Compact Hist-Tree (CHT, Crotty CIDR'21), a flat-array radix tree that keeps splitting dense bins. The choice is automatic: cost models built from an lcp histogram of adjacent spline keys estimate the average lookup depth and exact size of every (radix bits, bin error) configuration without building any of them, then pick the cheapest one whose size does not exceed the spline itself. A lookup is a few shift/mask table hops, a short linear search (under 32 points) or binary search over spline points, one FMA interpolation, and a last-mile binary search over the epsilon window, which is far fewer cache misses than walking B-tree nodes.

## Compared with alternatives

Over RadixSpline: pick PLEX when your key distribution has outliers or long common prefixes (RS's flat radix table stalls there), or when you do not want to tune radix bits; you pay a slightly longer build. Over RMI and PGM-index: pick it when you want a single-knob static index that builds in seconds; RMI is still about 25 ns faster at lookup but needs offline tuning, and PGM-index is maintained and supports updates. LIPP and ALEX are the choice once you need writes.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (C++ standard library only; the CMake Threads requirement is for the bundled example/benchmark) |
| **Minimum toolchain** | C++17 (std::optional; CMake sets CMAKE_CXX_STANDARD 17), GCC or Clang for __builtin_clz/clzl; specific compiler versions not documented |
| **Platforms** | 64-bit LP64 targets (Linux/macOS, x86-64 or aarch64) by construction; the repo CMake adds -march=native; no SIMD or ISA-specific code; Windows/MSVC not supported as written |
| **Thread safety** | not documented; the Builder is single-threaded, and after Finalize() TrieSpline lookups are const and touch no mutable state, so concurrent readers look safe from the code |
| **Drop-in for the baseline** | false: it is not a B-tree/map replacement. It holds no keys or values, has no insert/erase/iterators, and only returns a search window into a sorted array you keep and search yourself |

## Gotchas

- The README snippet calls ts::Builder tsb(min, max, keys.size()), but the third argument is spline_max_error, not a key count, so copying it gives an error bound equal to the dataset size. example.cc correctly passes a small epsilon (32).
- The input contract is checked only by assert(): keys must arrive in non-decreasing order, and the first and last keys must equal the min/max passed to the constructor. A release (NDEBUG) build silently returns wrong bounds if you violate it, and min == max hits __builtin_clz(0), which is undefined behaviour.
- SOSD's competitors/ts submodule pins commit 862e3c5 (June 2021), which predates the March 2022 fix to the single-node radix-table fallback (it read past the bin array). Vendor PLEX HEAD, and consider applying the open PR #3 fix too.
- The radix/CHT layer stores 32-bit offsets, with the top bit used as a leaf flag, so the spline must stay under about 2^31 points. There is no serializer for TrieSpline (only the bundled RadixSpline has one), so you rebuild after every load.

## Known shortcomings

- Evidence is a plot only (read off Fig. 3: PLEX \~200-300 ns vs B-tree \~500-900 ns, approximate); RMI is about 25 ns faster. AWS m5zn instance with no CPU model named.
- Read-only, uint32/uint64 keys only; returns a search window into the caller's sorted array (not a container). Abandoned since 2022 with an open out-of-bounds crash on sequential keys (#4) and an unmerged off-by-one fix (PR #3); the README example passes keys.size() as the max-error argument. Input checks are assert-only (release builds return wrong bounds); SOSD's copy predates the 2022 radix-table fix; GCC/Clang builtins (no MSVC); no serializer. CHT is faster on osm.

## Caveats and trade-offs

AIDB@VLDB 2021 workshop extended abstract, not a full research-track paper. The hardware is an AWS instance type with no CPU model, and the compiler and flags are not stated. The speedup evidence is only plots with no quoted number. PLEX does not beat RMI on lookup latency (RMI is about 25 ns faster on amzn and face).

Single hyperparameter (max prediction error) with an auto-tuner, unlike RMI/CHT/RS which need offline grid search; read-only (no update support, follow-up work planned a Fenwick-tree extension that was not implemented in this repo).

## Maintenance

Abandoned research code (last commit June 2022; the author acknowledged a 2024 crash report but no fix landed); MIT-licensed, about 1.1k lines of headers, and easy to vendor, as long as you pin HEAD and add your own input validation.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** The AIDB@VLDB'21 extended abstract (peer-reviewed workshop) plots PLEX against BTree, ART, PGM, RMI, RS and CHT on the four 64-bit SOSD datasets (Fig. 3). The PLEX lookup-time curve sits well below BTree's on every dataset. It is not A: the text gives only the machine type (AWS m5zn.metal, 4.5 GHz turbo), not a CPU model, compiler or flags, and the repo's own bench_end_to_end.cc compares only against RadixSpline.
- **Verifier notes:** Metadata checked and correct: MIT, 16 stars, last commit 2022-06-30 (over 3 years ago, so abandoned), not a fork, not archived. TrieSpline also ships as a SOSD competitor (competitors/ts), which is presumably how Fig. 3's BTree/ART comparison was run. Plot values above are approximate visual readings, not printed numbers.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/pdf/2108.05117>
  - <https://github.com/stoianmihail/PLEX>
  - <https://github.com/stoianmihail/PLEX/blob/main/benchmark.sh>
  - <https://github.com/stoianmihail/PLEX/blob/main/bench_end_to_end.cc>
  - <https://github.com/stoianmihail/PLEX/blob/main/CMakeLists.txt>
  - <https://github.com/learnedsystems/SOSD/tree/master/competitors>
- **Sources the enricher read:**
  - <https://github.com/stoianmihail/PLEX>
  - <https://github.com/stoianmihail/PLEX/blob/main/README.md>
  - <https://github.com/stoianmihail/PLEX/blob/main/include/ts/builder.h>
  - <https://github.com/stoianmihail/PLEX/blob/main/include/ts/ts.h>
  - <https://github.com/stoianmihail/PLEX/blob/main/include/ts/common.h>
  - <https://github.com/stoianmihail/PLEX/blob/main/include/ts/ts_cht/builder.h>
  - <https://github.com/stoianmihail/PLEX/blob/main/include/ts/ts_cht/cht.h>
  - <https://github.com/stoianmihail/PLEX/blob/main/include/ts/ts_cht/common.h>
  - <https://github.com/stoianmihail/PLEX/blob/main/CMakeLists.txt>
  - <https://github.com/stoianmihail/PLEX/blob/main/example.cc>
  - <https://github.com/stoianmihail/PLEX/blob/main/bench_end_to_end.cc>
  - <https://github.com/stoianmihail/PLEX/blob/main/benchmark.sh>
  - <https://github.com/stoianmihail/PLEX/blob/main/tune.sh>
  - <https://github.com/stoianmihail/PLEX/issues/4>
  - <https://github.com/stoianmihail/PLEX/pull/3>
  - <https://github.com/stoianmihail/PLEX/commit/af2b4281c2>
  - <https://github.com/stoianmihail/PLEX/commits/main>
  - <https://arxiv.org/pdf/2108.05117>
  - <https://github.com/learnedsystems/SOSD/tree/master/competitors>
  - <https://github.com/learnedsystems/SOSD/blob/master/competitors/ts.h>
  - <https://github.com/learnedsystems/SOSD/blob/master/.gitmodules>
  - <https://hn.algolia.com/api/v1/search?query=TrieSpline>
  - <https://export.arxiv.org/api/query?search_query=all:TrieSpline>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/stoianmihail/plex`) · [data/wave6/enrich/raw/github_com_stoianmihail_plex.json](../../../data/wave6/enrich/raw/github_com_stoianmihail_plex.json) (enrichment confidence 0.75)

</details>
