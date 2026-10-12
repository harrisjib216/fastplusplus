# emphf

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Minimal perfect hash functions](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `Apache-2.0` · 🔴 abandoned

> Hypergraph-peeling (MWHC) minimal perfect hash builder that constructs 5-63x faster than CMPH's CHD, using \~0.5 more bits/key.

| | |
|---|---|
| **Beats** | CMPH |
| **Claimed result** | On mphf_benchmark (PTHash SIGIR'21 Table 5, 1 billion random 64-bit keys, single core, i9-9900K), emphf builds in 374 s at 2.61 bits/key. CMPH's CHD needs 1972 / 5964 / 23746 s for lambda=4/5/6 (2.17/2.07/2.01 bits/key), so emphf builds about 5.3-63x faster (derived from page data). emphf lookups take 199 ns/key vs CHD's 416-419 ns/key, about 2.1x faster (derived from page data), but emphf uses 0.4-0.6 more bits/key. Separately, the rchikhi/benchmphf README reports emphf's HEM variant building a 1-billion-key MPHF in 770 s using 24 GB, vs the 'phf' library's 3900 s and 48 GB, about 5x faster (derived from page data); that page gives no CMPH numbers. |
| **Workload** | Single-core construction and lookup of MPHFs over 1 billion random 64-bit keys, comparing emphf (in-memory seq peeling) against CMPH's CHD algorithm (mphf_benchmark table). Separately compared against the 'phf' library in rchikhi/benchmphf's own 1-billion-key test. |
| **Metric** | build-time |
| **Hardware** | Intel i9-9900K @3.60GHz, 64GB DDR3 RAM @2.66GHz, Linux 5 (64-bit) |
| **Compiler and flags** | gcc 9.2.1, -O3, -march=native (mphf_benchmark harness) |
| **Adoption** | 66 stars |
| **Last commit** | 2013-12-06 |
| **Links** | [repository](https://github.com/ot/emphf) · [benchmark](https://github.com/roberto-trani/mphf_benchmark/blob/main/README.md) |

## Verdict

In the PTHash authors' mphf_benchmark (Table 5 of the SIGIR'21 paper), single-threaded on an Intel i9-9900K with gcc 9.2.1 -O3 -march=native, emphf's in-memory seq builder built an MPHF over 1 billion random 64-bit keys in 374 s at 2.61 bits/key with 199 ns/key average lookup, versus 1972-23746 s, 2.01-2.17 bits/key and 416-419 ns/key for CMPH's CHD at lambda 4-6. At 100 million keys the same table gives 24 s and 147 ns for emphf versus 121-1418 s and 197-204 ns for CHD; the comparison uses the benchmark authors' harness, not emphf's own.

## Use it when

- Static sets of 10^8-10^9+ keys where single-threaded build time matters and \~2.6 bits/key is acceptable: in PTHash's Table 5 it is the fastest-building row under 2.9 bits/key at both 100M keys (24 s) and 1B keys (374 s).
- Replacing CMPH's CHD in an offline build step: 24 s vs 121-1418 s at 100M keys and 374 s vs 1972-23746 s at 1B keys, with lookups also 1.4-2.1x faster.
- Key sets whose peeling working set does not fit in RAM: compute_mphf_scan_mmap builds the same structure from mmapped temporary files; the DCC 2014 paper reports 7.6 billion keys in under 21 hours on one machine.
- Variable-length string or binary keys: any key type works through an adaptor that returns a byte range, hashed once per lookup.
- Projects that can vendor and patch 17 small headers and do not need a maintained upstream.

## Skip it when

- Lookup-heavy paths: 199 ns/key at 1B keys (147 ns at 100M) versus 37-101 ns for PTHash configurations and 170 ns for BBHash gamma=1 in the same table; each lookup reads three random 2-bit slots plus a rank block that popcounts up to 16 words.
- Space-critical uses: 2.61 bits/key versus 1.80 for RecSplit l=8,b=100 and 2.01-2.17 for CHD itself.
- Multi-core machines where you want a parallel build: every construction path in the source is single-threaded.
- Dynamic sets or membership tests: the structure is static, and lookup() does no check, so a key outside the build set returns an arbitrary index.
- Code that needs an active upstream or portability: no commits since 2013-12-06, an open 2015 issue about an endless 'Hypergraph is not peelable' loop on a small set, an unmerged 2024 modernization PR, a Python 2 test script, and no Windows or non-x86 build as written.

## How it is fast

It uses the Majewski-Wormald-Havas-Czech (MWHC) scheme: one Jenkins 64-bit hash pass gives each key three vertices of a random 3-partite 3-hypergraph with 1.23n vertices, the graph is peeled in linear time, and 2-bit vertex values are assigned in reverse peeling order; a rank over nonzero pairs (one 64-bit count per 512 pairs) makes the result minimal, which is where 1.23 x 2 + \~0.15 = 2.61 bits/key comes from. The in-memory peeler (seq) uses the 'xor trick': each vertex stores only its degree and the XOR of the other endpoints of its edges, so adjacency is a flat array of fixed-size records, not lists. There is no per-bucket displacement search as in CHD, whose build time in the same benchmark grows from 1972 s to 23746 s as lambda goes from 4 to 6. For inputs that exceed RAM, scan_mmap implements the paper's cache-oblivious peeling (sequential scans and sorts, O(sort(n)) I/Os), and HEM splits keys into \~256-key buckets (Botelho-Pagh-Ziviani) that are each peeled in memory.

## Compared with alternatives

Pick emphf over RecSplit (Sux) only when build time outweighs space (374 s vs 936 s at 1B keys, but 2.61 vs 1.80 bits/key at similar \~200 ns lookups), and pick PTHash instead whenever lookup speed matters (37-101 ns vs 199 ns). Its remaining niche is external-memory peeling (scan_mmap) for key sets larger than RAM; none of the sources read here compare it with SicHash, SimdRecSplit, ShockHash or ConsensusRecSplit.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none beyond the C++ standard library and POSIX (sys/mman.h, sys/time.h, mkstemp for the mmap/HEM paths); build via CMake only for the CLI tools |
| **Minimum toolchain** | C++11 (-std=c++11) with GCC or Clang; uses the GNU '?:' extension, __builtin_clzll/__builtin_ctzll and inline asm, so MSVC is out; CMakeLists declares cmake_minimum_required(VERSION 2.8), which CMake 4.0+ rejects unless CMAKE_POLICY_VERSION_MINIMUM=3.5 is set; the PTHash benchmark compiled the headers with gcc 9.2.1 in C++17 mode |
| **Platforms** | Unix only (CMake stops with 'Unsupported platform' otherwise); x86/x86-64 as written because bitpair_vector.hpp includes &lt;xmmintrin.h&gt; (unused); little-endian assumed per a XXX note in base_hash.hpp; optional SSE4.2 hardware popcount via EMPHF_USE_POPCOUNT |
| **Thread safety** | Not documented. Construction is single-threaded. lookup() is a non-const member (the mphf_benchmark wrapper comments 'this should be const but lookup is not const') but only reads state, so concurrent lookups on a built object look safe from the source; no guarantee is stated. |
| **Drop-in for the baseline** | no |

## Gotchas

- common.hpp defines non-inline functions (logger(), nonzero_pairs()) at namespace scope in a header, so including emphf from more than one .cpp gives multiple-definition link errors; mark them inline or keep emphf in one translation unit.
- Duplicate keys are not detected on the seq path and the retry loop in mphf.hpp is unbounded, so duplicates (or an input that never peels, see issue #1) retry forever; HEM restarts on duplicate hashes with the same result. Deduplicate first. The benchmphf README also reports HEM crashing with std::length_error on sets of \~1000 keys or fewer.
- Build and lookup must use the same adaptor: stl_string_adaptor hashes the trailing NUL byte, so hashing (s.data(), s.size()) at lookup time returns wrong indices.
- Construction logs timestamps to stderr unconditionally; seq and HEM need on the order of 30 bytes/key while building (benchmphf README); scan_mmap/HEM create 'mphf.temp.XXXXXX' files in the current working directory; save/load write raw host-endian binaries with no version or checksum.

## Caveats and trade-offs

The benchmark is the PTHash authors' harness, not emphf's own. emphf builds and looks up faster than CMPH's CHD but uses more space (2.61 vs 2.01-2.17 bits/key). On the same table it is slower than BBHash gamma=1 (253 s build, 170 ns lookup) and much slower at lookup than PTHash. emphf's README makes no CMPH-specific claim; it only calls compute_mphf_seq 'the fastest MPHF construction implementation that we know of' (2013). GitHub reports the license as NOASSERTION, but the LICENSE file is the Apache-2.0 notice. There have been no commits since 2013-12-06.

Noticeably slower lookup (199 ns/key) than BBHash or PTHash in the same table; external-memory scan_mmap mode trades speed for lower construction memory; predates BBHash (2017) and PTHash (2021), so it was never tuned against them.

## Maintenance

Abandoned since 2013-12-06 (one open issue from 2015, one unmerged PR from 2024), but Apache-2.0 per the LICENSE file and only 17 headers, so it is easy to vendor and patch; last known-good compiler in the sources read is gcc 9.2.1 (C++17 mode, via mphf_benchmark).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification A, tier now A.
- **Tier reason:** roberto-trani/mphf_benchmark (src/mphf_benchmark.cpp, include/emphf_wrapper.hpp, include/chd_wrapper.hpp linking libcmph from the bonitao/cmph submodule) runs emphf against CMPH's CHD. The README states the i9-9900K CPU, CMakeLists.txt sets -O3 -march=native, and the PTHash SIGIR'21 paper, whose Table 5 the README reproduces, states gcc 9.2.1.
- **Verifier notes:** Numbers match the EMPHF and CHD rows of the mphf_benchmark README; the ratios are now marked as derived. last_commit was the repo's pushed_at date (2024-05-29); the only branch's last commit is 2013-12-06, so the repo is abandoned. The license was checked in the LICENSE file (Apache-2.0).
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `last_commit`, `maintenance_status`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/roberto-trani/mphf_benchmark/blob/main/README.md>
  - <https://github.com/roberto-trani/mphf_benchmark>
  - <https://github.com/roberto-trani/mphf_benchmark/blob/main/CMakeLists.txt>
  - <https://github.com/roberto-trani/mphf_benchmark/blob/main/.gitmodules>
  - <https://github.com/roberto-trani/mphf_benchmark/blob/main/src/mphf_benchmark.cpp>
  - <https://github.com/roberto-trani/mphf_benchmark/blob/main/include/emphf_wrapper.hpp>
  - <https://github.com/roberto-trani/mphf_benchmark/blob/main/include/chd_wrapper.hpp>
  - <https://arxiv.org/pdf/2104.10402>
  - <https://github.com/ot/emphf>
  - <https://github.com/ot/emphf/blob/master/README.md>
  - <https://github.com/ot/emphf/blob/master/LICENSE>
  - <https://github.com/rchikhi/benchmphf>
  - <https://github.com/rchikhi/benchmphf/blob/master/README.md>
- **Sources the enricher read:**
  - <https://github.com/ot/emphf>
  - <https://github.com/ot/emphf/blob/master/README.md>
  - <https://github.com/ot/emphf/blob/master/LICENSE>
  - <https://github.com/ot/emphf/blob/master/CMakeLists.txt>
  - <https://github.com/ot/emphf/blob/master/mphf.hpp>
  - <https://github.com/ot/emphf/blob/master/mphf_hem.hpp>
  - <https://github.com/ot/emphf/blob/master/base_hash.hpp>
  - <https://github.com/ot/emphf/blob/master/common.hpp>
  - <https://github.com/ot/emphf/blob/master/hypergraph.hpp>
  - <https://github.com/ot/emphf/blob/master/hypergraph_sorter_seq.hpp>
  - <https://github.com/ot/emphf/blob/master/hypergraph_sorter_scan.hpp>
  - <https://github.com/ot/emphf/blob/master/ranked_bitpair_vector.hpp>
  - <https://github.com/ot/emphf/blob/master/bitpair_vector.hpp>
  - <https://github.com/ot/emphf/blob/master/bitstream.hpp>
  - <https://github.com/ot/emphf/blob/master/packed_edge_list.hpp>
  - <https://github.com/ot/emphf/blob/master/packed_vector.hpp>
  - <https://github.com/ot/emphf/blob/master/internal_memory_model.hpp>
  - <https://github.com/ot/emphf/blob/master/mmap_memory_model.hpp>
  - <https://github.com/ot/emphf/blob/master/perfutils.hpp>
  - <https://github.com/ot/emphf/blob/master/emphf_config.hpp.in>
  - <https://github.com/ot/emphf/blob/master/compute_mphf_generic.hpp>
  - <https://github.com/ot/emphf/blob/master/compute_mphf_seq.cpp>
  - <https://github.com/ot/emphf/blob/master/compute_mphf_scan_mmap.cpp>
  - <https://github.com/ot/emphf/blob/master/compute_mphf_hem.cpp>
  - <https://github.com/ot/emphf/blob/master/test_mphf_generic.hpp>
  - <https://github.com/ot/emphf/blob/master/test_mphf.cpp>
  - <https://github.com/ot/emphf/blob/master/test_all.py>
  - <https://github.com/ot/emphf/blob/master/gen_synthetic_data.cpp>
  - <https://github.com/ot/emphf/commits/master>
  - <https://github.com/ot/emphf/issues/1>
  - <https://github.com/ot/emphf/pull/2>
  - <https://github.com/roberto-trani/mphf_benchmark/blob/main/README.md>
  - <https://github.com/roberto-trani/mphf_benchmark/blob/main/CMakeLists.txt>
  - <https://github.com/roberto-trani/mphf_benchmark/blob/main/.gitmodules>
  - <https://github.com/roberto-trani/mphf_benchmark/blob/main/src/mphf_benchmark.cpp>
  - <https://github.com/roberto-trani/mphf_benchmark/blob/main/include/emphf_wrapper.hpp>
  - <https://github.com/roberto-trani/mphf_benchmark/blob/main/include/emphf_hem_wrapper.hpp>
  - <https://github.com/roberto-trani/mphf_benchmark/blob/main/include/chd_wrapper.hpp>
  - <https://github.com/rchikhi/benchmphf/blob/master/README.md>
  - <https://arxiv.org/abs/1312.0526>
  - <https://arxiv.org/pdf/2104.10402>
  - <https://cmake.org/cmake/help/latest/release/4.0.html>
- **Raw records:** [data/wave1-phf/verified.json](../../../data/wave1-phf/verified.json) (id `https://github.com/ot/emphf`) · [data/wave1-phf/enrich/raw/github_com_ot_emphf.json](../../../data/wave1-phf/enrich/raw/github_com_ot_emphf.json) (enrichment confidence 0.85)

</details>
