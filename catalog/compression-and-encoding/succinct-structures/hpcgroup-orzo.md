# orzo (Elias-Fano encoded L2 rank/select)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Succinct data structures](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `no license` · 🟡 stale

> Research rank/select index for plain bitvectors that Elias-Fano-packs L2 counts, cutting index space below pasta-flat and cs-poppy.

| | |
|---|---|
| **Beats** | cs-poppy and pasta-flat |
| **Claimed result** | Snippet only: 'Orzo achieves 26.49% space saving over existing state-of-the-art structures like cs-poppy and pasta-flat'. No speed claim seen. |
| **Workload** | Rank and select on bit vectors with Elias-Fano compressed L2 indices to cut index space below the 3.51% of cs-poppy and pasta-flat. |
| **Metric** | memory |
| **Compiler and flags** | clang++-17 -std=c++23 -O3 -flto -mbmi -mbmi2 -mavx2 -static (Makefile; an AVX-512 variant is commented out for the Zaratan cluster) |
| **Adoption** | 2 stars, 1 fork; single commit |
| **Last commit** | 2025-05-12 |
| **Links** | [repository](https://github.com/hpcgroup/orzo) · [benchmark](https://github.com/hpcgroup/orzo/blob/master/benchmarking/comparison.cc) |

## Verdict

Search snippets of the SEA 2025 paper (Hough and Bhatele, LIPIcs vol. 338) say orzo cuts the rank index overhead by about 26.5% relative to cs-poppy and pasta-flat (3.51% overhead with select, 3.125% rank only), at a rank slowdown of about 9-38% versus pasta-flat depending on CPU and input. The repo's benchmark times rank1/select1 for orzo, pasta-flat and pasta's poppy over 10M random queries on 2^24 to 2^34-bit random bitvectors built with clang++-17 -O3 -flto -mavx2, but no CPU model or results are committed, and the paper itself was not opened.

## Use it when

- Very large static plain bitvectors (the bundled script sweeps 2^24 to 2^34 bits) where index memory matters more than the last nanoseconds of rank latency.
- Moderate to dense bitvectors (the script tests 10%, 50% and 90% ones) on x86-64 CPUs with BMI2 and AVX2.
- Research or prototyping of space-reduced poppy-style indexes, since the code is short (one \~400-line header) and the benchmark harness compares directly against pasta-flat and cs-poppy.

## Skip it when

- Latency-critical rank: search snippets of the SEA 2025 paper report rank is about 9-38% slower than pasta-flat depending on CPU and input (snippet only, paper not opened); pick pasta-flat, SPIDER or QuadRank if speed is the goal.
- Production code: no license file (so it cannot legally be copied), a single commit, no tests beyond a CHECK_CORRECTNESS mode in the benchmark, and no issues or releases.
- Non-x86 targets or x86 without BMI2: the header includes immintrin.h and calls _pdep_u64 and _tzcnt_u64 unconditionally; MSVC lacks the __uint128_t it relies on.
- Sparse bitvectors with heavy select traffic: select scans L1 entries linearly from a sample taken every 8192 ones, so long runs of zeros mean longer scans (observed in source, not measured).
- Anything that needs compressed or dynamic bitvectors; the bit array is stored uncompressed and the index is build-once.

## How it is fast

It keeps the cache-centric L0/L1/L2 layout of poppy-style indexes, but each 5632-bit lower block (11 basic blocks of 512 bits) gets one 128-bit entry holding an 18-bit L1 count plus the 10 cumulative L2 counts Elias-Fano encoded (20 upper bits, 90 lower bits). A rank decodes one L2 value with PDEP+TZCNT (BMI2 select-in-word) and then popcounts at most 8 words; by my arithmetic from the source constants the L1/L2 part costs 128/5632, about 2.3% of the bitvector (derived from source constants, not measured). Select uses a separate 2^32-bit upper level, a sample every 8192 ones, a linear scan over L1 entries, a linear Elias-Fano decode of the L2s and a PDEP/TZCNT finish.

## Compared with alternatives

Choose orzo over SPIDER, rankselect or succinct-bitvec-cpp only when shaving roughly a quarter off a poppy/pasta-style rank index matters more than rank speed and you can live with unlicensed research code; for compressed sparse sets use LA-vector or h0_bv instead.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none for the index itself (include/orzo/orzo.h plus utils.h); the benchmark needs pasta-toolbox bit_vector, pasta utils and tlx at pinned commits via external/install_deps.sh |
| **Minimum toolchain** | C++20 language features (std::popcount, std::countl_zero, std::has_single_bit); the Makefile uses clang++-17 -std=c++23; GCC or Clang only (__uint128_t) |
| **Platforms** | x86-64 with BMI2 (PDEP, TZCNT); Makefile builds with -mbmi -mbmi2 -mavx2, with a commented AVX-512 variant |
| **Thread safety** | not documented; queries only read the index, so concurrent reads look safe, but nothing is stated |
| **Drop-in for the baseline** | partial: same rank1/select1 names as pasta-flat, but construction takes a raw uint64_t\* plus length and every query takes the bit array pointer again |

## Gotchas

- Template parameters are not really tunable: UPPER_BLOCK_COUNT is hard-coded to 259072 with a comment that it is 'temporarily hardcoded' for the default N_L2 = 10, and the L1 field is only 18 bits wide.
- Class owns raw new[]/calloc buffers with no copy or move constructor, so copying an Orzo double-frees; with support_select = false the destructor still deletes and frees the uninitialised select pointers.
- rank0 returns 1 + (i - rank1(i)), which looks off by one against rank1's exclusive convention; the constructor reads whole 512-bit basic blocks, so the bit array must be padded to a multiple of 512 bits (both observed in source, not tested).
- The benchmark main checks argc &lt; 4 but reads argv[4], and the repo commits no results.csv, so the paper's numbers cannot be reproduced from the repo alone.

## Known shortcomings

- Downgraded B to C: the win is space only (26.49%, snippet only); the bench (comparison.cc vs pasta-flat and cs-poppy, clang++-17 -O3 -flto) publishes no results and no CPU; no LICENSE. SEA 2025 paper (Dagstuhl) blocked.
- Not a speed win: the SEA 2025 paper (snippet) has rank 9-38% slower than pasta-flat depending on CPU and input; space (about 26.5% less overhead) is the only win. No license; one commit; UPPER_BLOCK_COUNT hard-coded to 259072 for N_L2=10 only; no copy constructor (copies double-free); the destructor frees uninitialised pointers when support_select=false; rank0 returns 1 + (i - rank1(i)), off by one; the bench main checks argc&lt;4 but reads argv[4]; no results.csv or CPU model; needs x86-64 BMI2.

## Caveats and trade-offs

Peer-reviewed (SEA 2025, LIPIcs vol. 338 paper 23, 'Elias-Fano Compression for Space-Efficient Rank and Select Structures'), but the Dagstuhl PDF is blocked here; the 26.49% space saving is from search snippets only. The win is space, not speed: rank must decode Elias-Fano encoded L2 indices, and no speed claim over pasta-flat or cs-poppy was seen. Baselines are pasta-toolbox structures, not SDSL or sux. No LICENSE file (raw 404, none shown on the repo page), so reference only. Single commit (2025-05-12), 2 stars.

Smaller than the smallest known rank/select structures, but this is a space result; query speed relative to pasta-flat/cs-poppy is not established here.

## Maintenance

Single-commit research artifact (2025-05-12, 2 stars) with no license file, so reference only; read it to learn the Elias-Fano L2 trick, do not vendor it.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification B, tier now C.
- **Tier reason:** The repo's benchmarking/comparison.cc times orzo against pasta-flat and cs-poppy (pasta-toolbox) rank/select with clang++-17 -O3 -flto -mavx2 (Makefile), but no results or CPU model are published in the repo; the only number (26.49% space saving) comes from search snippets of the SEA 2025 paper, which is blocked here. Without seeing the paper's figures the peer-reviewed B cannot be confirmed, so C.
- **Verifier notes:** Real peer-reviewed research code, but it is a space-saving structure with no speed claim; consider keeping it as a documented memory-metric item rather than a faster-than entry. A session that reaches drops.dagstuhl.de could restore B (paper at drops.dagstuhl.de/storage/00lipics/lipics-vol338-sea2025/LIPIcs.SEA.2025.23/LIPIcs.SEA.2025.23.pdf, not opened).
- **Fields the verifier corrected:** `benchmark_url`, `compiler_and_flags`, `caveats`, `stars_or_usage`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/hpcgroup/orzo>
  - <https://github.com/hpcgroup/orzo/commits/master>
  - <https://github.com/hpcgroup/orzo/tree/master/benchmarking>
  - <https://raw.githubusercontent.com/hpcgroup/orzo/HEAD/README.md>
  - <https://raw.githubusercontent.com/hpcgroup/orzo/HEAD/Makefile>
  - <https://raw.githubusercontent.com/hpcgroup/orzo/HEAD/benchmarking/comparison.cc>
- **Sources the enricher read:**
  - <https://github.com/hpcgroup/orzo>
  - <https://github.com/hpcgroup/orzo/tree/master/scripts>
  - <https://github.com/hpcgroup/orzo/tree/master/external>
  - <https://raw.githubusercontent.com/hpcgroup/orzo/HEAD/README.md>
  - <https://raw.githubusercontent.com/hpcgroup/orzo/HEAD/Makefile>
  - <https://raw.githubusercontent.com/hpcgroup/orzo/HEAD/benchmarking/comparison.cc>
  - <https://raw.githubusercontent.com/hpcgroup/orzo/HEAD/include/orzo/orzo.h>
  - <https://raw.githubusercontent.com/hpcgroup/orzo/HEAD/include/orzo/bitvector.h>
  - <https://raw.githubusercontent.com/hpcgroup/orzo/HEAD/include/orzo/utils.h>
  - <https://raw.githubusercontent.com/hpcgroup/orzo/HEAD/scripts/run_benchmark.sh>
  - <https://raw.githubusercontent.com/hpcgroup/orzo/HEAD/external/install_deps.sh>
  - WebSearch snippet: https://drops.dagstuhl.de/storage/00lipics/lipics-vol338-sea2025/LIPIcs.SEA.2025.23/LIPIcs.SEA.2025.23.pdf (not opened)
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/hpcgroup/orzo`) · [data/wave9/enrich/raw/github_com_hpcgroup_orzo.json](../../../data/wave9/enrich/raw/github_com_hpcgroup_orzo.json) (enrichment confidence 0.65)

</details>
