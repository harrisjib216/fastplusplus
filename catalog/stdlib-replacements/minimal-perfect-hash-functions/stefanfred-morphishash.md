# MorphisHash

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Minimal perfect hash functions](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `GPL-3.0` · 🟡 stale

> Minimal perfect hash function that removes ShockHash's redundant cycle-orientation bits: 1.501 vs 1.523 bits/key at equal build time.

| | |
|---|---|
| **Beats** | ShockHash |
| **Claimed result** | Abstract: MorphisHash saves Theta(ln n) bits in expectation vs ShockHash, 'a factor of 20 less space overhead in practice'. That factor is for a single unpartitioned base case (Sec. 6.1, Bipartite MorphisHash with b=n-6): under 0.1 bits of total overhead vs about 2 bits for Bipartite ShockHash, at the cost of about 4x more seed tests. For a full MPHF on 100M keys (Table 1), Bip. MorphisHash-RS (n=52, b=n-4) gives 1.501 bits/key, 137 ns/query and 6,669 ns/key construction. Bip. ShockHash-RS (n=66) gives 1.523 bits/key, 147 ns/query and 7,186 ns/key. This is about 0.02 bits/key, or 27% less overhead, at equal construction time. At an equal 1.489 bits/key, MorphisHash-RS builds in 8,085 ns/key vs 172,738 ns/key for ShockHash-RS, which the paper calls about 21x faster construction. |
| **Workload** | (1) A single Bipartite MorphisHash vs Bipartite ShockHash base case (n up to about 64 keys): idealized space overhead and average successful seed (Figs. 2-3). (2) Partitioned MorphisHash-RS/-Flat vs Bipartite ShockHash-RS/-Flat (and CONSENSUS-RS, PHOBIC) on 100 million keys in the MPHF-Experiments framework: space (bits/key), query time (ns/query) and construction time (ns/key) (Table 1, Fig. 5). |
| **Metric** | memory |
| **Hardware** | Intel Core i7-11700 (48 KiB L1d and 512 KiB L2 per core, 16 MiB L3), 64 GiB dual-channel DDR4-3200 |
| **Adoption** | 3 stars |
| **Last commit** | 2025-07-03 |
| **Links** | [repository](https://github.com/stefanfred/MorphisHash) · [benchmark](https://arxiv.org/abs/2503.10161) |

## Verdict

In the MPHF-Experiments harness (std::string keys) on 100M keys on an Intel Core i7-11700, bipartite MorphisHash-RS (n=52, b=n-4) measured 1.501 bits/key, 137 ns/query and 6,669 ns/key build vs bipartite ShockHash-RS (n=66) at 1.523 bits/key, 147 ns and 7,186 ns/key. At an equal 1.489 bits/key, it built in 8,085 vs 172,738 ns/key. The paper does not state the compiler or flags (the CMake default is Release with -march=native), and there is no std:: or CMPH baseline. The abstract's '20x less overhead' applies to one unpartitioned base case (under 0.1 vs about 2 bits total at b=n-6, with about 4x more seed tests), not to the bits/key of a full MPHF.

## Use it when

- Static key sets that are built once and queried many times, where the size of the MPHF matters most (for example compressed indexes or k-mer tools), and single-core build costs of about 6-8 microseconds per key are acceptable.
- You want the space-optimized RecSplit-style trade-off. On 100M keys, MorphisHash-RS (n=52, ws=4) gives 1.501 bits/key with 137 ns queries and a 6,669 ns/key build, about 0.02 bits/key less than bipartite ShockHash-RS at the same build time.
- You need ShockHash-RS space (1.489 bits/key) without its build time: MorphisHash-RS builds at 8,085 ns/key vs 172,738 ns/key, about 21x faster, with similar queries (139 vs 131 ns).
- You want queries around 75 ns at about 1.54 bits/key: MorphisHash-Flat (n=88, ws=2) gives 1.541 bits/key vs 1.554 for bipartite ShockHash-Flat at the same query time.
- Your platform is Linux x86-64 with GCC 11-13 and CMake subprojects, and a GPL-3.0 (plus GCC Runtime Library Exception) dependency is acceptable.

## Skip it when

- Space is the only priority: in the same Table 1, Consensus-RS reaches 1.447 bits/key at a similar build cost (6,733 ns/key), but its queries are slower (222 ns vs 137 ns).
- Query latency is the priority: PHOBIC answers in 49 ns vs 137 ns for MorphisHash-RS, at 1.749 bits/key.
- The key set changes or you need membership tests: there is no insert or delete, and non-member keys map to arbitrary valid slots unless you store keys or fingerprints yourself.
- You need a maintained production library: there is no save/load serialization API in the headers and no README usage docs; the repo has 3 stars, and the code last changed in April 2025.
- Your toolchain is MSVC or non-GCC: the code needs libstdc++ &lt;experimental/simd&gt;, __uint128_t, __builtin_parityll and glibc's __attribute_noinline__ macro, and CI only covers GCC 11, 12 and 13 on Ubuntu 24.04.

## How it is fast

The gain is in space, not speed. As in bipartite ShockHash, each key gets two candidate positions, and a seed search samples random graphs until the graph is a pseudoforest, which can be oriented into a bijection. ShockHash then stores n bits of orientation in a retrieval structure and wastes about one bit per cycle, because every cycle has two valid orientations. MorphisHash writes the valid orientations as a GF(2) linear system Ay = d, substitutes a smaller b-bit retrieval vector (y = Hx, b &lt; n), and solves AHx = d with Gaussian elimination only for seeds that pass the pseudoforest filter. The paper proves this saves Θ(ln n) bits per base case in expectation; a query reads the seed and the b-bit vector, takes the parity of a masked 128-bit hash and picks one of the two candidates.

## Compared with alternatives

Pick MorphisHash over ShockHash when you want ShockHash-RS space at about 1/21 of its build time, or slightly less space at the same build time. Pick ConsensusRecSplit instead when the last 0.05 bits/key matters more than queries 1.6x slower (1.447 bits/key, 222 ns vs 137 ns in the same table), and PTHash/PHOBIC or PtrHash when queries must be under about 50 ns and 1.7-3 bits/key is acceptable.

## Integration

| | |
|---|---|
| **Form** | shared lib — header templates plus two CMake-built shared libraries (MorphisHash2Precompiled, Ips2raMorphisHashSorter); consume via add_subdirectory and link the MorphisHash target |
| **Dependencies** | sux, tlx, ips2ra (links Intel TBB, pthread and libatomic) and ByteHamster/Util (pulls in pasta bit_vector); all are git submodules except TBB, which must be installed |
| **Minimum toolchain** | C++20, CMake 3.25+, GCC 11+ (CI tests GCC 11, 12 and 13) |
| **Platforms** | x86-64 Linux is tested (paper uses an Intel Core i7-11700; top-level Release builds use -march=native). The GCC/glibc-specific code rules out MSVC. Other architectures are not documented. |
| **Thread safety** | Not documented. MorphisHash-RS construction takes a num_threads argument (parallel key hashing and per-bucket work); MorphisHashFlat construction is single-threaded. operator() is non-const on both classes, though it only reads state. |
| **Drop-in for the baseline** | partial — the constructor shape (keys, bucketSize, threads) and operator()(key) returning an index in [0, n) follow ShockHash, but the namespace, class names, template parameters and output positions differ, so code must be recompiled and positions rebuilt |

## Gotchas

- Input keys must be distinct, and neither constructor checks this. Identical keys hash identically under every seed, so the while (true) seed search can never find a bijection.
- The library writes to stdout during construction ('Skipped seed because of floating point inaccuracy' from the seed-pairing function). The precompiled base-case dispatcher prints to stderr and calls exit(1) for leaf sizes or widths that were not compiled in (leaf sizes up to 106 and up to 7 below each).
- MorphisHashFlat allocates its rank-select structure with a raw new and has no destructor or copy/move handling, so it leaks and copies share the pointer. Construct it in place, as MPHF-Experiments does with new.
- All tuning is compile-time and barely documented. The paper's Pareto picks are ws=4 (b=n-4) for RS and ws=2 for Flat. MorphisHashFlat's template order is &lt;k, ws, extraSeedBits&gt;, while the MPHF-Experiments wrapper orders it &lt;l, eb, ws&gt;.

## Caveats and trade-offs

The '20x less space overhead' figure applies to the per-base-case redundancy of ShockHash, not to total bits/key. For full 100M-key MPHFs, the gain is about 0.01-0.02 bits/key at equal construction time, or about 21x faster construction at equal space (1.489 bits/key). The paper does not state the compiler or flags; the MorphisHash and MPHF-Experiments CMake files default to a Release build with -march=native. The baseline (ShockHash) is an advanced research MPHF by the same group, not std::unordered_map, CMPH or BBHash. Single-author paper that uses the group's own benchmark framework. The repo is a GitHub fork of ByteHamster/ShockHash with 3 stars. The newest commit on any branch is 2025-07-03 (the pushed_at of 2025-11-13 adds no newer commit).

GitHub fork of ByteHamster/ShockHash that changes the seed-encoding scheme to remove redundant key-to-position mappings, reducing space at the same query complexity; integrated as its own contender in ByteHamster/MPHF-Experiments; very low external adoption (3 stars) despite the algorithmic improvement

## Maintenance

The repo is stale research code, a fork of ByteHamster/ShockHash: the code last changed 2025-04-08, the README 2025-07-03, and its only release is a 'zenodo' archive tag (2025-11-13). It ships ShockHash's GPLv3 COPYING plus COPYING.RUNTIME (GCC Runtime Library Exception), so it can be vendored at a pinned commit with submodules, but expect to fix build and API rough edges yourself.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed paper (the arXiv comment says 'ESA version') compares MorphisHash with ShockHash in Sec. 6.1/Fig. 2 and Table 1 on 100M keys. It uses the public MPHF-Experiments code (src/tableMorphisHash.cpp) and states the CPU (Intel Core i7-11700). It does not state the compiler or flags, so it cannot be tier A.
- **Verifier notes:** The full paper text was readable from the arXiv PDF (v2). The abstract numbers are verbatim, and I added Table 1 figures to give the '20x' claim its real context. I corrected last_commit (2025-07-03 on main; the dev and compCount branches are older), which makes the repo stale.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `hardware`, `last_commit`, `maintenance_status`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/abs/2503.10161>
  - <https://arxiv.org/pdf/2503.10161>
  - <https://github.com/stefanfred/MorphisHash>
  - <https://github.com/stefanfred/MorphisHash/blob/main/CMakeLists.txt>
  - <https://github.com/ByteHamster/MPHF-Experiments>
  - <https://github.com/ByteHamster/MPHF-Experiments/blob/main/src/tableMorphisHash.cpp>
  - <https://github.com/ByteHamster/MPHF-Experiments/blob/main/CMakeLists.txt>
- **Sources the enricher read:**
  - <https://github.com/stefanfred/MorphisHash>
  - <https://github.com/stefanfred/MorphisHash/blob/main/README.md>
  - <https://github.com/stefanfred/MorphisHash/blob/main/include/MorphisHash.h>
  - <https://github.com/stefanfred/MorphisHash/blob/main/include/MorphisHash-internal.h>
  - <https://github.com/stefanfred/MorphisHash/blob/main/include/MorphisHashFlat.h>
  - <https://github.com/stefanfred/MorphisHash/blob/main/include/MorphisHashFlatBase.h>
  - <https://github.com/stefanfred/MorphisHash/blob/main/include/MorphisHash-precompiled.h>
  - <https://github.com/stefanfred/MorphisHash/blob/main/src/MorphisHash-precompiled.cpp>
  - <https://github.com/stefanfred/MorphisHash/blob/main/CMakeLists.txt>
  - <https://github.com/stefanfred/MorphisHash/blob/main/.github/workflows/build.yml>
  - <https://github.com/stefanfred/MorphisHash/blob/main/.gitmodules>
  - <https://github.com/stefanfred/MorphisHash/blob/main/benchmark/benchmark_construction.cpp>
  - <https://github.com/stefanfred/MorphisHash/blob/main/COPYING.RUNTIME>
  - <https://github.com/stefanfred/MorphisHash/issues?q=is%3Aissue>
  - <https://github.com/stefanfred/MorphisHash/commits/main>
  - <https://github.com/stefanfred/MorphisHash/actions>
  - <https://github.com/stefanfred/MorphisHash/releases>
  - <https://github.com/ByteHamster/ShockHash>
  - <https://github.com/ByteHamster/Util/blob/main/CMakeLists.txt>
  - <https://github.com/ByteHamster/MPHF-Experiments/blob/main/src/tableMorphisHash.cpp>
  - <https://github.com/ByteHamster/MPHF-Experiments/blob/main/contenders/shockhash/MorphisHashContender.h>
  - <https://github.com/ByteHamster/MPHF-Experiments/blob/main/contenders/shockhash/MorphisHashFlatContender.h>
  - <https://arxiv.org/abs/2503.10161>
  - <https://arxiv.org/pdf/2503.10161>
- **Raw records:** [data/wave1-phf/verified.json](../../../data/wave1-phf/verified.json) (id `https://github.com/stefanfred/morphishash`) · [data/wave1-phf/enrich/raw/github_com_stefanfred_morphishash.json](../../../data/wave1-phf/enrich/raw/github_com_stefanfred_morphishash.json) (enrichment confidence 0.78)

</details>
