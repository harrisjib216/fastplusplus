# S+ tree (Algorithmica static B-tree array layout)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Ordered maps and trees](README.md)</sub>

**Tier A** (reproducible public benchmark) · Study only · `C++` · `no license` · 🔴 abandoned

> SIMD (AVX2) static B+-tree array layout beating std::lower_bound/std::set on batched int32 lookups.

| | |
|---|---|
| **Beats** | std::lower_bound (primary), std::set (bench code binsearch/set.cc actually uses std::multiset), absl::btree |
| **Claimed result** | Reciprocal throughput. The S+ tree is up to 15x faster than std::lower_bound; the S-tree variant is up to 8x (article). The repo README says \~15x over std::lower_bound for small cache-resident arrays and \~8x for large arrays (&gt;1e6). The S+ tree is up to 30x faster than std::set on the same lower-bound queries, and the S+ tree with pointers is \~15x faster than Abseil's B-tree for large arrays (article). The article says the real-latency speedup is 'not that impressive'. |
| **Workload** | Point/predecessor lookup over sorted arrays of 32-bit integers up to 2^25 (\~33.5M) elements; reciprocal-throughput microbenchmark (batched independent queries) on an AMD Zen 2 CPU with Clang 10 |
| **Metric** | throughput |
| **Hardware** | AMD Zen 2 CPU |
| **Compiler and flags** | Clang 10; binsearch/Makefile: clang++ -std=c++17 -O3 -march=native |
| **Adoption** | 841 stars (amh-code repo) |
| **Last commit** | 2022-10-06 |
| **Links** | [repository](https://github.com/sslotin/amh-code) · [benchmark](https://en.algorithmica.org/hpc/data-structures/s-tree/) |

## Verdict

Reciprocal-throughput microbenchmarks on an AMD Zen 2 CPU with Clang 10 (-O3 -march=native) show the S+ tree up to \~15x faster than std::lower_bound on cache-resident sorted int32 arrays (\~8x for arrays &gt;1e6, up to 2^25 elements), up to \~30x faster than std::multiset::lower_bound, and (pointer variant) \~15x faster than Abseil's absl::btree on large arrays; the author explicitly notes real single-query latency gains are much smaller than these throughput figures.

## Use it when

- Read-mostly/static sorted 32-bit-integer key sets that are bulk-built once (or rarely rebuilt), not mutated incrementally
- Workloads that issue many independent lookups that can be batched/pipelined (joins, index probes, columnar scans) so the reciprocal-throughput gains actually materialize
- x86-64 targets with AVX2 where you can build with -march=native and enable transparent huge pages for large (&gt;1e6-element) arrays
- Arrays that fit or mostly fit in cache, where the article's \~15x-over-std::lower_bound number applies (\~8x still holds up to 2^25 elements)
- You're willing to vendor and adapt a single .cc file into your own build rather than link a maintained library

## Skip it when

- You need insert/delete or any online mutation of the key set -- no dynamic update path is implemented, only a full prepare() rebuild
- Latency-sensitive single-query paths with data-dependent lookups (pointer chasing between queries) -- the author states real per-query latency gains are much smaller than the throughput numbers
- Non-x86 or AVX2-unavailable targets -- the article says porting to AVX-512 or Arm NEON needs 'non-trivial changes', and none is provided in this repo
- You need arbitrary key/value types, comparators, or a runtime-chosen array size -- N is a compile-time constant baked into the offset/height calculations
- Anything beyond experimentation/benchmarking in production -- no LICENSE file, abandoned since 2022, and the author frames this as teaching/reference code

## How it is fast

The sorted array is rearranged into a B-ary tree (16 keys per node/cache line, branching factor 17) stored as one flat array with compile-time layer offsets instead of pointers (the 'S+ tree' = separate internal/leaf layers, vs. the pointer/Eytzinger-numbered 'S-tree'). Each node comparison loads 16 keys into two AVX2 256-bit registers, does _mm256_cmpgt_epi32 SIMD compares, permutes/packs the masks, and extracts the branch index with tzcnt, replacing several scalar branchy comparisons per level with one branchless SIMD step; large trees also use aligned_alloc + madvise(MADV_HUGEPAGE) to cut TLB misses. The headline numbers are reciprocal-throughput over batches of independent queries, which lets the CPU overlap several independent tree descents (\~3x ILP per the article) rather than shrinking single-query latency much.

## Compared with alternatives

Pick this over tlx::btree or boost::container::flat_set/fast-containers when your key set is effectively static (bulk-loaded, then read-heavy) and lookups can be batched for throughput; those siblings are actual libraries supporting online insert/erase/find, whereas amh-code is an unpackaged technique reference you'd have to adapt, re-tune, and maintain yourself.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none beyond platform headers (x86intrin.h, sys/mman.h) |
| **Minimum toolchain** | C++17; article/Makefile use Clang 10 (clang++ -std=c++17 -O3 -march=native); GCC compiles but the author notes it performs slightly worse |
| **Platforms** | x86-64 with AVX2 required; Linux assumed for the madvise/hugepage path, a Windows path is stubbed out in comments (memoryapi.h) but not implemented |
| **Thread safety** | not documented; the implementation uses process-global state (a global btree array/pointer), so multiple independent trees or concurrent prepare()/query calls in one process are not safe without rewriting it |
| **Drop-in for the baseline** | partial -- explain: lower_bound()-style query semantics match std::lower_bound, but there is no container type, no insert/erase, and the array size is a compile-time constant, so it cannot replace std::set/std::map as a mutable, runtime-sized container |

## Gotchas

- Array size N is a preprocessor/constexpr constant (binsearch.hh defaults to 1&lt;&lt;20), so each key-set size effectively needs its own compiled variant rather than being a runtime parameter
- Requires AVX2 codegen (-march=native or explicit target attributes); there is no scalar fallback path in these files
- Large-array speedups depend on aligned_alloc + madvise(MADV_HUGEPAGE) actually getting huge pages from the OS; without that configured, expect smaller gains than reported
- Headline speedups are reciprocal-throughput over batches of independent queries -- single dependent-query ('real') latency shows a much smaller win, per the author's own caveat in the article

## Caveats and trade-offs

Headline speedups are reciprocal-throughput numbers from batches of independent queries; the author explicitly notes that single-query real latency (with data dependencies) shows a much smaller gain ('not that impressive'), so most of the win is instruction-level parallelism across queries rather than lower per-lookup latency; repository has no LICENSE file or stated license

Static structure: no insert/delete support without a full rebuild, so it is not a drop-in replacement for a mutable std::set; SIMD/AVX and layout choices are microarchitecture-tuned; requires branchless/permutation tricks that add code complexity

## Maintenance

Abandoned reference code (last commit 2022-10-06, no LICENSE file) published as teaching/benchmark material for the Algorithmica HPC book, not a maintained library -- treat it as a technique to study and port, not a dependency to pull in.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** The article compares the S+ tree against std::lower_bound, std::set and absl::btree. The linked repo has runnable baselines: binsearch/std.cc (std::lower_bound), binsearch/set.cc (std::multiset), binsearch/bplus.cc and standalone.cc. binsearch/Makefile gives clang++ -std=c++17 -O3 -march=native, and the article states Clang 10 on a Zen 2 CPU (the CPU model is not named).
- **Verifier notes:** Numbers verified on the article and the repo README. The record's Abseil wording was garbled: it is the S+ tree with pointers that is \~15x faster than the Abseil B-tree, not an Abseil B-tree 'with pointers'. The last commit on main (the only branch) is 2022-10-06; pushed_at 2022-12-11 is not a commit date. No LICENSE file (GitHub license null), so 'reference' usability is correct. 841 stars.
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `compiler_and_flags`, `last_commit`
- **Pages the verifier opened:**
  - <https://en.algorithmica.org/hpc/data-structures/s-tree/>
  - <https://github.com/sslotin/amh-code>
  - <https://github.com/sslotin/amh-code/blob/main/README.md>
  - <https://github.com/sslotin/amh-code/blob/main/binsearch/Makefile>
  - <https://github.com/sslotin/amh-code/blob/main/binsearch/set.cc>
  - <https://github.com/sslotin/amh-code/blob/main/binsearch/std.cc>
  - <https://github.com/sslotin/amh-code/blob/main/binsearch/standalone.cc>
- **Sources the enricher read:**
  - <https://github.com/sslotin/amh-code>
  - <https://github.com/sslotin/amh-code/blob/main/README.md>
  - <https://github.com/sslotin/amh-code/blob/main/binsearch/Makefile>
  - <https://github.com/sslotin/amh-code/blob/main/binsearch/bplus.cc>
  - <https://github.com/sslotin/amh-code/blob/main/binsearch/bplus-pointers.cc>
  - <https://github.com/sslotin/amh-code/blob/main/binsearch/binsearch.hh>
  - <https://github.com/sslotin/amh-code/blob/main/binsearch/std.cc>
  - <https://github.com/sslotin/amh-code/blob/main/binsearch/set.cc>
  - <https://github.com/sslotin/amh-code/blob/main/binsearch/eytzinger.cc>
  - <https://github.com/sslotin/amh-code/blob/main/binsearch/standalone.cc>
  - <https://en.algorithmica.org/hpc/data-structures/s-tree/>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/sslotin/amh-code`) · [data/wave1/enrich/raw/github_com_sslotin_amh_code.json](../../../data/wave1/enrich/raw/github_com_sslotin_amh_code.json) (enrichment confidence 0.75)

</details>
