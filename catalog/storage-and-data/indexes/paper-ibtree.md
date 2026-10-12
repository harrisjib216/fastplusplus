# IBTree (Interpolating B-Tree, SOSD implementation)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Indexes](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `GPL-3.0` · 🔴 abandoned

> Static B-tree using interpolation search inside nodes, from the SOSD benchmark; about 8% faster lookups than STX B+-tree.

| | |
|---|---|
| **Beats** | B-tree (STX B-Tree, in-memory) |
| **Claimed result** | 446.55 ns vs the STX BTree's 482.11 ns lookup time (\~1.08x, \~8% faster), using 9.0 MB vs 166.0 MB (\~18x smaller) (derived from page data; 32-bit amzn, PVLDB 14(1) Table 2) |
| **Workload** | SOSD 'Benchmarking Learned Indexes' Table 2: the fastest configured variant of each structure, lower-bound lookups (10M random lookup keys) on a 32-bit version of the amzn dataset (200M keys). It is 32-bit because the SIMD CuckooMap in the table only supports 32-bit keys (footnote 4). |
| **Metric** | latency |
| **Hardware** | Intel Xeon Gold 6230 CPU @ 2.10GHz, 256GB RAM |
| **Compiler and flags** | Compiler not stated in the paper or the repo (the README dependency list installs clang). SOSD CMakeLists.txt adds -ffast-math -march=native (and -fopenmp if available), and scripts/prepare.sh builds with CMAKE_BUILD_TYPE=Release (CMake default -O3 -DNDEBUG). |
| **Adoption** | SOSD repo has 313 stars |
| **Last commit** | 2022-04-08 |
| **Links** | [repository](https://github.com/learnedsystems/SOSD/blob/master/competitors/interpolation_btree.h) · [benchmark](https://www.vldb.org/pvldb/vol14/p1-marcus.pdf) |

## Verdict

SOSD's PVLDB 14(1) Table 2 (fastest variant of each structure, 32-bit version of the 200M-key amzn dataset, 10M lookups in one harness that finishes with a search over the sorted array) reports IBTree at 446.55 ns per lookup and 9.0 MB against 482.11 ns and 166.0 MB for the STX B+-tree, about 8% faster, on an Intel Xeon Gold 6230 @ 2.10GHz with 256 GB RAM. The build used SOSD's Release -march=native -ffast-math flags, but no compiler is named, no std:: container is compared, and the 64-bit datasets have only Pareto plots, not IBTree numbers.

## Use it when

- Static, sorted 32- or 64-bit unsigned integer keys that are loaded once and then only read.
- Keys whose distribution is close to linear inside each 256-key node (smooth CDFs like SOSD's amzn), so the interpolation guess is nearly exact.
- A small sparse index over a large sorted array: index every Nth key and finish with a binary search in the returned window. The 9.0 MB variant beat STX's best 166 MB variant on 32-bit amzn.
- Index-structure research or benchmarking, as the 'B-tree plus interpolation, no learned model' baseline next to RMI, RadixSpline and PGM.
- You want a \~370-line template with no dependencies that you can vendor and modify, and GPL-3.0 is acceptable.

## Skip it when

- Any workload with inserts, deletes or updates. The SOSD code only bulk-loads, even though the paper's Table 1 marks IBTree as supporting updates.
- Skewed or clustered keys inside a node, such as osm-like cell IDs. A bad guess is corrected by a linear walk of up to 255 slots per node, with no fallback to binary search.
- Latency is the priority. In the same Table 2, RMI (180.90 ns), RadixSpline (266.58 ns), PGM (326.48 ns) and FAST (435.33 ns) are all faster, and the hash tables are faster still for pure point lookups (RobinHash 93.69 ns, CuckooMap 114.50 ns).
- Non-numeric or composite keys such as strings or tuples. Interpolation needs key subtraction and conversion to double, and there is no comparator parameter.
- You need range scans, iteration, a 'not found' result, a maintained library, or a non-copyleft license. None of these is provided, the code is only exercised by SOSD's harness, and the license is GPL-3.0.

## How it is fast

Each inner and leaf node stores a slope, count / (last_key - first_key), so a lookup guesses the slot as slope \* (key - first_key) in one linear-interpolation step. It then walks left or right one slot at a time to the exact lower bound, instead of binary-searching the node (the linear and std::lower_bound versions remain in the file, commented out). The idea is from G. Graefe, 'B-tree indexes, interpolation search, and skew', DaMoN '06 (DOI 10.1145/1140402.1140409), not a 2018 VLDB paper. When keys within a node are close to evenly spaced the guess lands near the target, so the walk is short, and the 256-way fanout keeps the tree shallow.

## Compared with alternatives

Choose it over RadixSpline, RMI or FAST (fast64) only when you want a plain comparison tree with no model tuning, no RMI code generation and no Rust/AVX-512 FAST library; on speed alone it loses, since RadixSpline is both faster (266.58 ns) and smaller (4.0 MB) in the same table. If you need updates, use PGM-index, ALEX or LIPP instead.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | The core interpolation_btree::BTree needs only the C++ standard library. The file itself does not include &lt;vector&gt;, &lt;functional&gt; or &lt;cassert&gt;; it gets them through SOSD's competitors/base.h -&gt; util.h. The InterpolationBTree wrapper also needs SOSD's Competitor, KeyValue, SearchBound and util::timing. |
| **Minimum toolchain** | Not documented. SOSD builds with CMAKE_CXX_STANDARD 17, but the header uses only C++11-level features. The maintainers built SOSD with g++-9 in an Ubuntu 18.04 container (issue #8), and the README installs clang on Ubuntu 20.04. |
| **Platforms** | Any. The code is portable scalar C++ with no SIMD intrinsics. The paper's numbers were measured on x86-64 (Xeon Gold 6230) with SOSD's -march=native -ffast-math build. |
| **Thread safety** | Not documented. The tree cannot change after the bulk load, and Lookup is const and never writes, so concurrent reads should be safe. The paper's multithreaded lookup experiment (Fig. 16) includes IBTree. There is no write path to synchronize. |
| **Drop-in for the baseline** | no |

## Gotchas

- Destruction is broken. BTreeNodeBase has no virtual destructor, so `delete root` and `delete children[i]` go through base pointers. That is undefined behavior, the inner-node destructors never run, and nearly the whole tree leaks. Separately, the inner destructor loop runs i &lt; count and would skip the last of the count+1 children anyway.
- Querying a key larger than the largest indexed key is undefined behavior. The leaf's early-exit path returns `count`, so Lookup reads values[count], which is uninitialized or past the end of a full 256-entry leaf. SOSD avoids this only because its wrapper always indexes the last key and it only queries existing keys.
- Lookup has lower-bound semantics and never reports a miss: it always returns some value. Node fanout (256) is hard-coded in private type aliases, nodes are allocated with plain new (no allocator parameter), and the internal asserts are compiled out in SOSD's Release (-DNDEBUG) build.
- The 9.0 MB vs 166.0 MB memory comparison reflects which sampling variant was fastest for each structure (both are tuned by indexing every Nth key), not an inherent 18x difference in compactness.

## Known shortcomings

- The only numbers come from SOSD (PVLDB 14(1) Table 2) on 32-bit amzn keys; no compiler named; a SOSD competitor implementation rather than a standalone library.
- Bulk-load only (no insert/delete, though the paper's Table 1 says updatable). No virtual destructor on the node base (UB; most of the tree leaks); a key above the max indexed reads values[count] (uninitialized or past the end); on skewed data one interpolation guess is followed by a linear walk of up to 255 slots with no binary fallback. Only \~8% faster than STX; RS/RMI/PGM/FAST are faster in the same table and the 18x memory gap reflects the fastest-variant pick. GPL-3.0 source drop in SOSD, abandoned.

## Caveats and trade-offs

Single table row: 32-bit amzn only, best variant per structure. The margin over the STX B-tree is modest (\~8%). FAST (435.33 ns) edges it, and learned indexes (RMI 180.90 ns, RS 266.58 ns) and hash tables are far faster in the same table. IBTree is a header inside the SOSD benchmark repo, not a standalone library. SOSD has had no commits since April 2022. The previously cited CIDR'21 Hist-Tree paper does not contain IBTree or these numbers.

Implements interpolation search inside B-tree nodes per G. Graefe's 2018 VLDB paper 'B-tree indexes, interpolation search, and skew'; only exists as a template competitor inside the SOSD benchmark harness, not a standalone packaged library; degrades on skewed/adversarial key distributions where interpolation mispredicts

## Maintenance

Abandoned (the IBTree file last changed in a May 2021 reformat, SOSD's last commit was April 2022, and a maintainer wrote in March 2026 in issue #35 that the repo is not kept up to date), but it is a \~370-line GPL-3.0 header that is easy to copy, as long as you accept the copyleft and fix the destructor and out-of-range bugs.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification A, tier now B.
- **Tier reason:** The numbers come from Table 2 of the peer-reviewed PVLDB 14(1) paper 'Benchmarking Learned Indexes' (Marcus et al.): IBTree 446.55 ns / 9.0 MB against the STX BTree at 482.11 ns / 166.0 MB, on a Xeon Gold 6230 @ 2.10GHz. It is B, not A: the SOSD harness is public (learnedsystems/SOSD benchmarks/ + competitors/interpolation_btree.h + scripts/prepare.sh + CMakeLists.txt), but neither the paper nor the repo names the compiler. This matches the earlier B verdicts on RMI, RadixSpline and FAST from the same table.
- **Verifier notes:** The record's benchmark_url (Crotty, CIDR'21 Hist-Tree) evaluates BS/STX/ART/RMI/PGM/RS/HT/CHT on a c5.4xlarge Xeon Platinum 8124M with gcc 9.3.0. It never mentions IBTree, and it has no 446.55/482.11 numbers. The numbers, the table and the Xeon Gold 6230 hardware are all from the SOSD PVLDB paper (arXiv 2006.12804), so benchmark_url was corrected. Metadata checked: GPL-3.0, 313 stars, not archived; default-branch last commit 2022-04-08 (pushed_at 2022-04-27).
- **Fields the verifier corrected:** `benchmark_url`, `workload`, `claimed_speedup`, `compiler_and_flags`, `last_commit`, `caveats`
- **Pages the verifier opened:**
  - <https://cs.brown.edu/people/acrotty/pubs/cidr2021_paper20.pdf>
  - <https://arxiv.org/pdf/2006.12804>
  - <https://www.vldb.org/pvldb/vol14/p1-marcus.pdf>
  - <https://github.com/learnedsystems/SOSD>
  - <https://github.com/learnedsystems/SOSD/blob/master/competitors/interpolation_btree.h>
  - <https://github.com/learnedsystems/SOSD/blob/master/CMakeLists.txt>
  - <https://github.com/learnedsystems/SOSD/blob/master/scripts/prepare.sh>
  - <https://github.com/learnedsystems/SOSD/blob/master/README.md>
  - <https://github.com/learnedsystems/SOSD/blob/master/.drone.yml>
- **Sources the enricher read:**
  - <https://github.com/learnedsystems/SOSD/blob/master/competitors/interpolation_btree.h>
  - <https://github.com/learnedsystems/SOSD>
  - <https://github.com/learnedsystems/SOSD/blob/master/README.md>
  - <https://github.com/learnedsystems/SOSD/blob/master/CMakeLists.txt>
  - <https://github.com/learnedsystems/SOSD/blob/master/benchmarks/benchmark_ibtree.cc>
  - <https://github.com/learnedsystems/SOSD/blob/master/benchmarks/benchmark_ibtree.h>
  - <https://github.com/learnedsystems/SOSD/blob/master/benchmarks/benchmark_btree.cc>
  - <https://github.com/learnedsystems/SOSD/blob/master/competitors/base.h>
  - <https://github.com/learnedsystems/SOSD/blob/master/competitors/stx_btree.h>
  - <https://github.com/learnedsystems/SOSD/blob/master/benchmark.h>
  - <https://github.com/learnedsystems/SOSD/blob/master/util.h>
  - <https://github.com/learnedsystems/SOSD/commits/master/competitors/interpolation_btree.h>
  - <https://github.com/learnedsystems/SOSD/issues/8>
  - <https://github.com/learnedsystems/SOSD/issues/9>
  - <https://github.com/learnedsystems/SOSD/issues/35>
  - <https://www.vldb.org/pvldb/vol14/p1-marcus.pdf>
  - <https://api.crossref.org/works?query.bibliographic=B-tree+indexes+interpolation+search+and+skew+Graefe>
  - <https://api.semanticscholar.org/graph/v1/paper/DOI:10.1145/1140402.1140409>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `paper:ibtree`) · [data/wave6/enrich/raw/paper_ibtree.json](../../../data/wave6/enrich/raw/paper_ibtree.json) (enrichment confidence 0.8)

</details>
