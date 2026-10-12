# HOT (Height Optimized Trie)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Indexes](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `ISC` · 🔴 abandoned

> Header-only C++14 order-preserving trie for in-memory indexes. Beats STX B+-tree, ART and Masstree on string-key lookups, scans and memory.

| | |
|---|---|
| **Beats** | B-tree (STX B+-Tree), ART, Masstree |
| **Claimed result** | "For the lookup-only workload C, HOT achieves an at least 25% higher throughput across all evaluated data sets compared to the other evaluated index structures... In case of the URL data set, HOT's throughput is 200% higher than for the other data structures" (workload E). |
| **Workload** | YCSB workload C (100% read) and workload E (95% short range-scan, 5% insert) over 50M-entry url/email/yago/integer key data sets, single node, comparing HOT against the STX B+-Tree, ART, and Masstree. |
| **Metric** | throughput |
| **Hardware** | Intel i7-6700 (4-core, 3.4GHz/4.0GHz turbo) and Intel i9-7900X (10-core, 3.3GHz/4.3GHz turbo) |
| **Compiler and flags** | GCC 7.2 (stated in the paper). The paper gives no flags. The repo's CMakeLists.txt Release build (default USEAVX2=ON) uses -std=c++14 -march=native -mavx -mavx2 -mbmi2 -mlzcnt -O3 -DNDEBUG. |
| **Adoption** | 159 stars |
| **Last commit** | 2018-03-26 |
| **Links** | [repository](https://github.com/speedskater/hot) · [benchmark](https://15721.courses.cs.cmu.edu/spring2019/papers/08-oltpindexes2/p521-binna.pdf) |

## Verdict

In the SIGMOD'18 paper, 50M keys (url, email, yago, random 63-bit integers) were loaded and then 100M uniform YCSB-style operations were run single-threaded on an Intel i7-6700 with GCC 7.2 (no flags stated). Workload C lookups ran 1.3/1.5/4.1/5.3 Mops/s against the best rival's 0.9 (Masstree), 1.2 (Masstree), 2.4 (ART) and 5.0 (ART), per the Figure 8 labels. So the text's 'at least 25% higher' holds for url, email and yago but not for integers (\~6%). The '200% higher' is workload E on URLs (0.6 vs 0.2 Mops/s for the STX B+-tree and ART). The STX B+-tree baseline uses 256-byte nodes and resolves string keys through tuple ids, which helps explain its low string throughput.

## Use it when

- Read-mostly in-memory ordered indexes on variable-length string keys of 255 bytes or less, such as URLs or emails. Paper workload C (50M keys): 1.3 vs 0.9 Mops/s for Masstree on URLs, and 1.5 vs 1.2 on emails.
- Short range scans over string keys. On workload E (95% scans of up to 100 entries) over URLs, HOT ran 0.6 Mops/s against 0.2 for the STX B+-tree and ART and 0.1 for Masstree.
- Memory-bound indexes. For 50M keys the paper measured 11.4-14.4 bytes/key: 0.53-0.67 GB against 1.26 GB for the STX B+-tree, 1.09-1.64 GB for ART and 1.53-5.05 GB for Masstree (all figures include 0.37 GB of raw tuple ids). HOT was also smaller than the raw URL and email key bytes.
- Skewed or compound 8-byte keys, such as the yago triples: lookups ran 4.1 vs 2.4 Mops/s for ART.
- Concurrent insert and lookup without deletes on Intel x86-64 Linux. HOTRowex readers never take locks, and the paper shows near-linear scaling to 10 cores (mean lookup speedup 9.96x, insert 9.00x).

## Skip it when

- Uniformly random 64-bit integer keys. Figure 8 shows lookups only \~6% ahead of ART (5.3 vs 5.0 Mops/s), and ART inserts 50% faster (3.9 vs 2.6 Mops/s).
- Point lookups where you don't need key order. In issue #3, one user measured HOT at 82 ns/find and 236 ns/insert against Folly F14 at 27/31 ns, on \~570K short strings on a Xeon E-2278G.
- Workloads that need concurrent deletes (HOTRowex has no remove), keys longer than 255 bytes, binary keys with zero bytes, or an index that owns its keys and values the way std::map does.
- CPUs other than Intel Haswell or newer. AVX2, BMI2 and LZCNT are required. PEXT is slow on AMD Zen 1/2 (issue #8), and an ARM port using SIMDe ran 'very poor' (issue #10). MSVC and Windows are not supported as written.
- Anything that needs upkeep. The code has been frozen since March 2018, nine issues from 2019-2024 have no maintainer reply, and the bundled build breaks on current toolchains.

## How it is fast

It is a binary Patricia trie whose nodes are grouped into compound nodes of at most k=32 entries. Each node's span, meaning how many key bits it looks at, is chosen from the data so that the overall tree height is as small as possible, which keeps fanout high even for sparse string keys. Inside a node, the discriminative bit positions are stored as a single or multi byte mask, and the matching bits of the search key are gathered with one BMI2 PEXT. The result is compared against all of the node's 8/16/32-bit 'sparse partial keys' at once with AVX2 and/cmpeq/movemask, and the last match wins. Inserts rebuild partial keys with PDEP into copy-on-write nodes. Nodes come in 9 physical layouts, the node type is encoded in the low bits of each child pointer, and the first 4 cache lines of each node are prefetched. On the paper's string data sets the mean leaf depth is up to 68% lower than ART's.

## Compared with alternatives

Pick HOT over ART (ARTSynchronized or rafaelkallis/adaptive-radix-tree) when keys are strings or skewed and index memory matters. Stay with ART for uniformly random integer keys and insert-heavy loads, where HOT's own paper has ART inserting 50% faster at near-equal lookup speed. The learned-index siblings (RadixSpline, RMI, PLEX, fast64, PGM-index) report results on fixed-width integer key sets, while HOT needs no training and has its largest wins on variable-length strings.

## Integration

| | |
|---|---|
| **Form** | header-only (copy libs/idx/content-helpers, libs/hot/commons, libs/hot/single-threaded and/or libs/hot/rowex; CMake INTERFACE targets are also provided) |
| **Dependencies** | HOTSingleThreaded needs nothing outside the repo headers. HOTRowex needs Intel TBB (enumerable_thread_specific for epoch reclamation), and the README recommends tcmalloc. The repo's own build also pulls TBB 2018, boost-cmake 1.66 and Boost.Hana (for benchmarks and tests) as git submodules. |
| **Minimum toolchain** | C++14, CMake 2.8+. The paper used GCC 7.2. On GCC 8+ the bundled benchmark framework fails to compile under -std=c++14 because of Boost.Hana constexpr lambdas (issues #1, #7). The code uses GCC attributes and glibc's __bswap_64. |
| **Platforms** | x86-64 with AVX2, BMI2 and LZCNT (Haswell or newer); build with -march=haswell or native. Only Linux is documented. There is an optional USEAVX512 CMake flag. No ARM or other non-x86 support. |
| **Thread safety** | HOTSingleThreaded is not thread-safe. All of its instances also share one unsynchronized function-static MemoryPool, so even separate trees on separate threads race. HOTRowex uses ROWEX: lookups and scans are wait-free and lock-free, and writers lock only the affected nodes (bottom-up) and restart when validation fails. Freed nodes go through a process-wide epoch-based reclamation singleton. |
| **Drop-in for the baseline** | false — this is not a B-tree or std::map replacement. It indexes values of 8 bytes or less (63 usable bits) whose keys are re-derived through a KeyExtractor. lookup returns an OptionalValue, iterators are const-only, and the concurrent version cannot delete. |

## Gotchas

- The trie stores only your 63-bit value (tid or pointer), not the key. Every lookup ends by dereferencing the value through KeyExtractor and running a full compare (strcmp for strings), so the key memory must stay alive and unchanged while it is indexed.
- C-string keys are capped at 255 bytes because bit offsets are uint8 (issue #6). KeyUtilities.hpp silently truncates longer keys to 255 bytes with strncpy/std::min instead of rejecting them, and every operation copies the key into a 255-byte fixed array.
- There is no allocator hook. Nodes are allocated with posix_memalign (the single-threaded version adds a static free-list pool), a failed allocation throws std::bad_alloc, and inserts and deletes use an unchecked fixed 64-entry std::array traversal stack. The paper says HOT's worst-case height has not yet been proven.
- Builds break out of the box. The pinned boost-cmake submodule commit can't be checked out (issue #2) and its Boost download URL returns 403 (issue #3). Without BMI/LZCNT target flags, GCC fails with 'inlining failed ... _tzcnt_u32' (issue #4).

## Known shortcomings

- The repo benchmarks only HOT (no public head-to-head harness); ART inserts about 50% faster on the integer set.
- The paper's '&gt;=25% on all' for workload C does not hold for integers: its own Fig. 8 gives 5.3 vs ART 5.0 Mops (\~6%). The string and memory wins are real (url C 1.3 vs 0.9 Mops, E 3x, 11-14 B/key). The STX B-tree baseline resolves string keys through tuple ids, which handicaps it.
- Single-threaded version uses a shared static unsynchronised MemoryPool, so separate instances race across threads; the ROWEX variant has no delete and needs TBB. Keys capped at 255 B with silent truncation; values &lt;=63 bits; keys are re-derived from values. x86 AVX2/BMI2 only (pext is slow on Zen 1/2). The build is broken (submodule, Boost download 403, GCC 8+ with Hana); frozen since 2018 with 9 unanswered issues; the TODS'22 code is unreleased.

## Caveats and trade-offs

SIGMOD 2018 peer-reviewed paper. It states two CPU models and GCC 7.2 but no optimization flags, which caps it at Tier B. The 200% (3x) margin is workload E on the url data set only; workload C is at least 25%. ART inserts 50% faster than HOT on the integer data set. Needs AVX2/BMI2. The repo has had no pushes since 2018: treat it as a frozen academic artifact, not an actively developed library.

Header-only, order-preserving trie with a variable per-node bit span for balance; uses the most memory-efficient layout of the four structures tested in its own paper, but ART shows 50% higher insertion throughput than HOT on pure-integer keys; string-heavy tries (Masstree, ART) grow space 51-230% on long textual keys where HOT only grows 26%.

## Maintenance

Abandoned since 2018-03-26 with no active fork, and the code for the extended TODS 2022 'Height Optimized Tries' version (DOI 10.1145/3506692) was never released (issue #9). It is ISC-licensed and header-only, so vendoring the core headers is feasible, but expect to fix the build yourself; GCC 7.2 on Linux x86-64 is the last toolchain documented to work.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** The SIGMOD'18 paper (Sec. 6.1-6.2, Fig. 8) compares HOT against the STX B+-Tree, ART and Masstree, and both quoted sentences appear verbatim. It names both CPUs and GCC 7.2 but no optimization flags. The repo's apps/benchmarks run only HOT, and the published index-microbench fork holds only the workload generator plus STX/ART wrappers, so no public harness reproduces the comparison. Not A.
- **Verifier notes:** Metadata checked and correct: ISC, 159 stars, last commit 2018-03-26, not a fork, not archived, so abandoned. The benchmark_url is a CMU course mirror of the SIGMOD'18 paper (DOI 10.1145/3183713.3196896); the text matches.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://15721.courses.cs.cmu.edu/spring2019/papers/08-oltpindexes2/p521-binna.pdf>
  - <https://github.com/speedskater/hot>
  - <https://github.com/speedskater/hot/blob/master/CMakeLists.txt>
  - <https://github.com/speedskater/hot/blob/master/releaseBuild.sh>
  - <https://github.com/speedskater/index-microbench>
  - <https://github.com/speedskater/index-microbench/blob/master/index.h>
- **Sources the enricher read:**
  - <https://github.com/speedskater/hot>
  - <https://github.com/speedskater/hot/blob/master/README.md>
  - <https://github.com/speedskater/hot/blob/master/CMakeLists.txt>
  - <https://github.com/speedskater/hot/blob/master/.gitmodules>
  - <https://github.com/speedskater/hot/blob/master/libs/hot/rowex/CMakeLists.txt>
  - <https://github.com/speedskater/hot/blob/master/libs/hot/single-threaded/CMakeLists.txt>
  - <https://github.com/speedskater/hot/blob/master/libs/hot/single-threaded/include/hot/singlethreaded/HOTSingleThreaded.hpp>
  - <https://github.com/speedskater/hot/blob/master/libs/hot/single-threaded/include/hot/singlethreaded/HOTSingleThreadedInterface.hpp>
  - <https://github.com/speedskater/hot/blob/master/libs/hot/single-threaded/include/hot/singlethreaded/HOTSingleThreadedNodeBase.hpp>
  - <https://github.com/speedskater/hot/blob/master/libs/hot/single-threaded/include/hot/singlethreaded/HOTSingleThreadedNode.hpp>
  - <https://github.com/speedskater/hot/blob/master/libs/hot/single-threaded/include/hot/singlethreaded/MemoryPool.hpp>
  - <https://github.com/speedskater/hot/blob/master/libs/hot/rowex/include/hot/rowex/HOTRowex.hpp>
  - <https://github.com/speedskater/hot/blob/master/libs/hot/rowex/include/hot/rowex/HOTRowexInterface.hpp>
  - <https://github.com/speedskater/hot/blob/master/libs/hot/rowex/include/hot/rowex/HOTRowexNode.hpp>
  - <https://github.com/speedskater/hot/blob/master/libs/hot/rowex/include/hot/rowex/EpochBasedMemoryReclamationStrategy.hpp>
  - <https://github.com/speedskater/hot/blob/master/libs/hot/commons/include/hot/commons/SIMDHelper.hpp>
  - <https://github.com/speedskater/hot/blob/master/libs/hot/commons/include/hot/commons/MultiMaskPartialKeyMapping.hpp>
  - <https://github.com/speedskater/hot/blob/master/libs/idx/content-helpers/include/idx/contenthelpers/KeyUtilities.hpp>
  - <https://github.com/speedskater/hot/blob/master/libs/idx/content-helpers/include/idx/contenthelpers/TidConverters.hpp>
  - <https://github.com/speedskater/hot/blob/master/libs/idx/content-helpers/include/idx/contenthelpers/ContentEquals.hpp>
  - <https://github.com/speedskater/hot/blob/master/libs/idx/content-helpers/include/idx/contenthelpers/KeyComparator.hpp>
  - <https://github.com/speedskater/hot/issues/1>
  - <https://github.com/speedskater/hot/issues/2>
  - <https://github.com/speedskater/hot/issues/3>
  - <https://github.com/speedskater/hot/issues/4>
  - <https://github.com/speedskater/hot/issues/5>
  - <https://github.com/speedskater/hot/issues/6>
  - <https://github.com/speedskater/hot/issues/7>
  - <https://github.com/speedskater/hot/issues/8>
  - <https://github.com/speedskater/hot/issues/9>
  - <https://github.com/speedskater/hot/issues/10>
  - <https://github.com/speedskater/hot/commits/master>
  - <https://github.com/speedskater/hot/forks>
  - <https://github.com/speedskater/hot-sample>
  - <https://15721.courses.cs.cmu.edu/spring2019/papers/08-oltpindexes2/p521-binna.pdf>
  - <https://api.crossref.org/works?query.bibliographic=Height+Optimized+Tries+Binna>
  - <https://hn.algolia.com/api/v1/search?query=%22height%20optimized%20trie%22>
  - <https://hn.algolia.com/api/v1/items/31296184>
  - <https://hn.algolia.com/api/v1/items/43293070>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/speedskater/hot`) · [data/wave6/enrich/raw/github_com_speedskater_hot.json](../../../data/wave6/enrich/raw/github_com_speedskater_hot.json) (enrichment confidence 0.85)

</details>
