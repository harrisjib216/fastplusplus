# BuRR (Ribbon Filter)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Probabilistic filters](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Static bumped-ribbon retrieval/filter library: 0.06-1.4% space overhead against Xor's 23% and Bloom's 44%+, with slower sequential queries.

| | |
|---|---|
| **Beats** | Bloom filter, xor filter |
| **Claimed result** | Space overhead over the information-theoretic minimum (arXiv 2109.01892 Table 2, false-positive rate about 1%, r=7/8): Xor 23.0%, Xor+ 14.4%, blocked Bloom 45-52% and Cuckoo12 40-46%. Plain Bloom is at least 44% by construction (1.44\*log2(1/f)). BuRR ranges from 0.06% to 1.4% depending on ribbon width (0.21-0.48% at w=64). Speed: in the 64-thread parallel workload, BuRR and homogeneous ribbon Pareto-dominate plain Bloom filters. In that workload, BuRR 2-bit w=64 takes 215/215 ns for positive/negative queries and 190 ns/key to construct, against Xor r=8 at 386/392 ns and 586 ns/key. Sequentially, the faster BuRR variants are 'only moderately slower than Bloom and Xor filters'. For example, at n=10^8, BuRR 2-bit w=64 takes 82/74 ns for positive/negative queries against Xor's 41/41 ns, and constructs at 115 against 159 ns/key. The README's rounded figures are overheads 'as low as 0.1%' and below 0.5% for speed-oriented configurations. |
| **Workload** | Space overhead, construction time and positive/negative query time (ns/key). Sequential runs use n=10^6 and 10^8 keys, and a parallel run queries 1280 filters of 10^7 keys from 64 threads. False-positive rates are about 1%, 10% and 0.05%. BuRR is compared against Bloom, blocked Bloom, cuckoo, Morton, quotient, xor, xor+ and fuse filters in the lorenzhs/fastfilter_cpp harness (SEA 2022 best paper; the arXiv version is the extended one). |
| **Metric** | memory |
| **Hardware** | AMD EPYC 7702, 64 cores, 2.0 GHz base / 3.35 GHz boost, 1 TiB DDR4-3200 |
| **Compiler and flags** | clang++ 11.0 with -O3 -march=native on Ubuntu 20.04 (paper Experimental Setup). The BuRR Makefile bench target uses -O3 -DNDEBUG -march=native. |
| **Adoption** | 52 stars; won Best Paper at SEA 2022 (20th International Symposium on Experimental Algorithms) |
| **Last commit** | 2026-09-13 |
| **Links** | [repository](https://github.com/lorenzhs/BuRR) · [benchmark](https://arxiv.org/abs/2109.01892) |

## Verdict

Table 2 of arXiv 2109.01892 (lorenzhs/fastfilter_cpp harness, clang++ 11 -O3 -march=native, 64-core AMD EPYC 7702) shows BuRR 2-bit w=64 at 0.25% space overhead at about 1% FPR, against 23% for Xor, 14.4% for Xor+, 40-46% for Cuckoo12 and 45-52% for blocked Bloom. At 10^8 keys, run sequentially, it built faster than Xor (115 vs 159 ns/key) but queried about 2x slower (82/74 vs 41/41 ns); only in the 64-thread, 1280-filter run did it also beat Xor on queries (215 vs 386-392 ns). Plain Bloom is not in the table: the claim that BuRR Pareto-dominates it comes from the paper's parallel-workload summary (Figure 1).

## Use it when

- Immutable key sets built in one bulk pass (read-only indexes, per-file filters, shipped lookup tables) where bits per key matter most. At about 1% FPR, BuRR 2-bit w=64 measured 0.25% over the n\*r-bit lower bound, against Xor's 23% and blocked Bloom's 45-52%.
- Retrieval / static-function use: storing 1-16 bits per key without the keys, for example as a building block for perfect hashing or compact key-to-small-value maps where non-member queries do not need to be detected.
- Many sharded filters queried from all cores, where memory bandwidth is the bottleneck. In the paper's 64-thread run over 1280 filters of 10^7 keys, BuRR 2-bit w=64 answered queries in 215 ns (Xor r=8: 386/392 ns) and built at 190 ns/key (Xor: 586).
- Large inputs (around 10^8 keys) where build time matters: BuRR 2-bit w=64 constructed at 115 ns/key, against Xor's 159 ns/key, sequentially.
- Linux builds with GCC or Clang, where you can vendor templated headers, git submodules and a system libxxhash.

## Skip it when

- Any need for inserts, deletes or counting after construction. The whole key set must be present at build time; blocked Bloom, cuckoo or Prefix Filter handle incremental inserts.
- Single-threaded, latency-critical lookups, especially on cache-resident filters. At n=10^6, positive/negative queries took 19/24 ns, against Xor's 5/5 and blocked Bloom's 3/3. At n=10^8 they took 82/74 ns, against Xor's 41/41 and blocked Bloom's 24/24.
- Large r (very low false-positive rates). Query and build time grow with the number of result bits, and the paper's heatmap hands the large-r region to Xor and cuckoo filters.
- Memory-tight builds. Construction holds an 8-byte hash per key plus a CoeffRow and a ResultRow per slot (about 17 bytes/key for w=64, r=8) before BackSubst compacts to roughly r bits/key, on top of your own input array.
- Windows/MSVC, macOS, or teams wanting a hardened library: headers include glibc's &lt;bits/stdint-uintn.h&gt;, configuration is compile-time and, in a maintainer's words, 'a bit of a mess' (issue #3), and the project is small research code (52 stars, 4 issues).

## How it is fast

Ribbon ('Rapid Incremental Boolean Banding ON the fly') gives each key a w-bit (32/64/128) random coefficient window at a hashed start slot. On-the-fly GF(2) Gaussian elimination keeps a banded row-echelon system using word-wide XORs, and back-substitution then produces the solution. Bumping keeps this compact. Start positions are grouped into buckets of about w^2/log w and radix-sorted by bucket (ips2ra). When a bucket hits a linear dependency, the keys below a threshold are rolled back and pushed to a smaller recursive layer, and only 1-2 bits of threshold metadata are kept per bucket. That lets the table be overloaded (fewer slots than keys), so almost no slots stay empty. A query hashes once (a 64-bit master hash code, remixed per layer) and checks the bucket threshold. Each result bit is then the parity of the coefficients ANDed with an interleaved, column-major solution block, touching at most two adjacent blocks, and filter queries stop at the first mismatching bit.

## Compared with alternatives

Pick BuRR over Xor/binary fuse (xor_singleheader) when space dominates: 0.1-0.5% overhead against about 23% for xor and 7.5-12.5% for binary fuse. Also pick it when you need retrieval of small values, or when many shards are queried under heavy parallel load. Prefer xor_singleheader for the fastest single-threaded queries from one dependency-free header, and Prefix Filter when keys arrive incrementally on AVX-512 hardware.

## Integration

| | |
|---|---|
| **Form** | source-drop (templated headers plus sorter.cpp compiled to sorter.o with explicit ips2ra instantiations, linked with a CMake-built libtlx.a; the third-party SimpleRibbon repo wraps a few configs as a CMake static library) |
| **Dependencies** | system libxxhash &gt;= 0.8.0 (XXH3); git submodules tlx (built and linked), ips2ra (radix sort), DySECT (cuckoo table for 1+-bit thresholds), pcg-cpp; vendored RocksDB headers; pthread; gtest for tests. CI also installs libtbb-dev. |
| **Minimum toolchain** | C++17 (Makefile -std=c++17 -Werror). CI builds (build only, no tests) with GCC 10-14 and Clang 16-18 on Ubuntu 24.04, and the paper used clang++ 11. GCC 15 -O3 miscompiled until the 2026-09-13 fix (issue #4). |
| **Platforms** | Linux/glibc with GCC or Clang: the code uses &lt;bits/stdint-uintn.h&gt;, __uint128_t, ssize_t and GCC builtins. x86-64 is the only tested target (the paper used AMD EPYC, and the Makefile sets -march=native). BuRR's own code has no ISA-specific intrinsics, but aarch64, macOS and MSVC are not documented. |
| **Thread safety** | Not documented. On main, construction is single-threaded (parallel construction lives on the separate 'parallel' branch). Query methods are const, and the bundled ribbon.cpp benchmark runs QueryFilter on one filter from several threads, so concurrent reads after BackSubst appear safe. Querying during construction is not. |
| **Drop-in for the baseline** | false — static bulk-build API (AddRange once, BackSubst, then query) configured through compile-time Config templates; no incremental add as in Bloom filters, no deletes, and a different interface from xor_singleheader. |

## Gotchas

- Deduplicate input. Unique master hash codes are only checked with assert(), so -DNDEBUG builds skip the check. By our reading of the code, a duplicate row is always linearly dependent, so the non-bumping base layer keeps retrying with 0.05 more slots per item and never succeeds. Distinct keys whose 64-bit XXH3 hashes collide behave the same way.
- Size limits are compile-time. RConfig fixes Index to uint32_t, so one structure is capped at about 4.29 billion slots unless you write a custom config (issue #3). Retrieval presets link only against sorter.cpp's explicit Sorter instantiations for 8- and 16-bit values, so wider values need an added instantiation.
- Serialization is 'not meant as a robust storage and transfer format' (binary_format.txt): there are no corruption checks and the hash function is not recorded. Deserializing with a different compile-time config throws config_error, and endianness conversion is untested.
- Header hygiene: config.hpp defines a non-inline operator&lt;&lt; for __uint128_t inside namespace std, so including ribbon.hpp from two translation units should give duplicate-symbol link errors. The default configs also print construction timings (DefaultConfig::log = true). The GCC 15 miscompile workaround (XXH_FORCE_MEMORY_ACCESS=0) is on main only; the 'parallel' branch is 3 commits behind main.

## Known shortcomings

- Static only (bulk build, no insert/delete). Sequential queries \~2x slower than Xor at 1e8 keys and \~4x at 1e6; only the 64-thread run beats Xor. Linux/glibc with GCC/Clang only (bits/stdint-uintn.h, __uint128_t); needs system libxxhash plus submodules; CI builds but runs no tests. Duplicate keys are checked only by assert (with NDEBUG the base layer likely retries forever, from code reading). uint32 index caps one structure at \~4.29B slots; retrieval values over 16 bits need a new instantiation; a non-inline operator&lt;&lt; in a header likely causes duplicate-symbol link errors; weak serialization; \~17 B/key peak build memory. A GCC 15 -O3 miscompile was fixed on main only on 2026-09-13 (the parallel branch lacks it).

## Caveats and trade-offs

The main win is space, not speed. Sequential query latency is about 2x that of xor filters, and the blocked Bloom filter is fastest overall at about 50% overhead. BuRR beats xor and plain Bloom on speed mainly in the heavily loaded parallel benchmark. BuRR is a static retrieval/AMQ structure: no inserts after build. The comparison harness lorenzhs/fastfilter_cpp is a fork of pdillinger/fastfilter_cpp, last pushed 2021-09-11. The README's '\~20%' xor and '\~10%' xor+ overheads round the paper's measured 23% and 12.8-14.4%. Building needs git submodules (tlx, ips2ra, DySECT, pcg-cpp, rocksdb).

Static/immutable retrieval structure (no keys stored, so it cannot enumerate members); construction cost scales worse than hash-table-based filters for very large n; a parallel-construction variant exists on a separate branch.

## Maintenance

Active but low-traffic research code: a few maintenance commits a year, the latest (2026-09-13) fixing a GCC 15 -O3 miscompile; all 4 issues are closed. It is Apache-2.0 and small enough to vendor, but you must wire up submodules, a system libxxhash and compile-time configs yourself, or use the SimpleRibbon CMake wrapper.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now A.
- **Tier reason:** This is an upgrade from B. The Experimental Setup paragraph of the arXiv full version states an AMD EPYC 7702 and clang++ 11.0 with -O3 -march=native. The benchmark code and scripts are public in lorenzhs/BuRR (Makefile bench target, scripts/) and lorenzhs/fastfilter_cpp (benchmarks/bulk-insert-and-query.cc, ribbon-benchmark.sh). Table 2 measures BuRR against Bloom, blocked Bloom, cuckoo, xor and xor+.
- **Verifier notes:** Tier upgraded from B to A: the arXiv full version states CPU, compiler and flags, and the code and scripts are public. The record's overhead numbers are README paraphrases, not the paper's measured values, so claimed_speedup is rewritten from Table 2. Metadata (Apache-2.0, 52 stars, last commit 2026-09-13, active, not a fork) is correct.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/abs/2109.01892>
  - <https://arxiv.org/pdf/2109.01892>
  - <https://github.com/lorenzhs/BuRR>
  - <https://github.com/lorenzhs/BuRR/blob/main/README.md>
  - <https://github.com/lorenzhs/BuRR/blob/main/Makefile>
  - <https://github.com/lorenzhs/BuRR/tree/main/scripts>
  - <https://github.com/lorenzhs/fastfilter_cpp>
  - <https://github.com/lorenzhs/fastfilter_cpp/tree/dev/benchmarks>
- **Sources the enricher read:**
  - <https://github.com/lorenzhs/BuRR>
  - <https://github.com/lorenzhs/BuRR/blob/main/README.md>
  - <https://github.com/lorenzhs/BuRR/blob/main/Makefile>
  - <https://github.com/lorenzhs/BuRR/blob/main/.gitmodules>
  - <https://github.com/lorenzhs/BuRR/blob/main/.github/workflows/build.yml>
  - <https://github.com/lorenzhs/BuRR/blob/main/config.hpp>
  - <https://github.com/lorenzhs/BuRR/blob/main/ribbon.hpp>
  - <https://github.com/lorenzhs/BuRR/blob/main/hasher.hpp>
  - <https://github.com/lorenzhs/BuRR/blob/main/construction.hpp>
  - <https://github.com/lorenzhs/BuRR/blob/main/query.hpp>
  - <https://github.com/lorenzhs/BuRR/blob/main/storage.hpp>
  - <https://github.com/lorenzhs/BuRR/blob/main/backsubst.hpp>
  - <https://github.com/lorenzhs/BuRR/blob/main/sorter.cpp>
  - <https://github.com/lorenzhs/BuRR/blob/main/sorter.hpp>
  - <https://github.com/lorenzhs/BuRR/blob/main/minimal_hasher.hpp>
  - <https://github.com/lorenzhs/BuRR/blob/main/thresh_compress.hpp>
  - <https://github.com/lorenzhs/BuRR/blob/main/serialization.hpp>
  - <https://github.com/lorenzhs/BuRR/blob/main/binary_format.txt>
  - <https://github.com/lorenzhs/BuRR/blob/main/ribbon.cpp>
  - <https://github.com/lorenzhs/BuRR/blob/main/tests.cpp>
  - <https://github.com/lorenzhs/BuRR/blob/main/rocksdb/math.h>
  - <https://github.com/lorenzhs/BuRR/commits/main>
  - <https://github.com/lorenzhs/BuRR/compare/main...parallel>
  - <https://github.com/lorenzhs/BuRR/compare/main...variable-bitlength>
  - <https://github.com/lorenzhs/BuRR/issues/1>
  - <https://github.com/lorenzhs/BuRR/issues/2>
  - <https://github.com/lorenzhs/BuRR/issues/3>
  - <https://github.com/lorenzhs/BuRR/issues/4>
  - <https://arxiv.org/abs/2109.01892>
  - <https://arxiv.org/pdf/2109.01892>
  - <https://arxiv.org/abs/2411.12365>
  - <https://github.com/ByteHamster/SimpleRibbon>
  - <https://github.com/lorenzhs/fastfilter_cpp>
  - <https://github.com/lorenzhs/fastfilter_cpp/tree/dev/benchmarks>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/lorenzhs/burr`) · [data/wave6/enrich/raw/github_com_lorenzhs_burr.json](../../../data/wave6/enrich/raw/github_com_lorenzhs_burr.json) (enrichment confidence 0.8)

</details>
