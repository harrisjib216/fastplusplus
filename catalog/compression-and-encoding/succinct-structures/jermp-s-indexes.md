# Sliced Indexes (s_indexes)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Succinct data structures](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Universe-sliced compressed integer sets (bitmaps/posting lists) with SIMD intersection; 5-10x faster AND than Partitioned Elias-Fano.

| | |
|---|---|
| **Beats** | Partitioned Elias-Fano (ds2i-style PEF); Roaring also compared |
| **Claimed result** | README Table 2 (microseconds per 2-list intersection) Slicing vs PEF: Census-Income 11.56 vs 115.17, Census-1881 0.18 vs 0.92, Weather 25.70 vs 213.00, Wikileaks 0.47 vs 2.51; about 5x to 10x faster than PEF (derived from page data). Versus Roaring: slower on 3 of 4 (11.56 vs 4.68, 0.18 vs 0.15, 25.70 vs 13.37), faster on Wikileaks (0.47 vs 0.86). DCC 2021 paper Table 2 (ms per AND query, TREC queries): RUP 0.32/1.67/1.78 vs PEF 2.48/12.54/19.72 on Gov2/ClueWeb09/CCNews (about 7.8x/7.5x/11x, derived from page data); Roaring 0.32/1.64/1.29 is equal or faster. |
| **Workload** | Average microseconds per intersection of two compressed lists, 1,000 random pairs repeated 10 times, on the Census-Income, Census-1881, Weather and Wikileaks datasets shipped with CRoaring; bits per integer also reported. |
| **Metric** | latency |
| **Hardware** | Intel i7-7700 @3.6 GHz, 64 GB RAM, Linux 4.4.0 |
| **Compiler and flags** | gcc 7.3.0; CMakeLists.txt sets -std=c++14 -O3 -march=native -ggdb (Release default); clang builds add -stdlib=libc++ |
| **Adoption** | 19 stars |
| **Last commit** | 2023-01-08 |
| **Links** | [repository](https://github.com/jermp/s_indexes) · [benchmark](https://github.com/jermp/s_indexes) |

## Verdict

On an Intel i7-7700 with gcc 7.3.0 and -O3 -march=native, the README reports 2-list intersections over CRoaring's real datasets at 0.18-25.70 us for Slicing versus 0.92-213.00 us for Partitioned Elias-Fano (about 5-10x faster), and the peer-reviewed DCC 2021 paper reports 0.32/1.67/1.78 ms per TREC AND query on Gov2/ClueWeb09/CCNews versus about 2.5/12.8/19 ms for the cardinality-partitioned codecs (7.6-10.6x). Only the Slicing timing harness (src/intersect.cpp) is in the repo; PEF and Roaring numbers come from the authors' own code run separately.

## Use it when

- Inverted-index or bitmap-index query processing dominated by AND queries over 32-bit doc ids, where PEF or another cardinality-partitioned codec is your current choice and intersection latency matters more than the last bit per integer.
- Read-mostly, static collections built once and then memory-mapped (the builder serializes to a flat buffer that s_index mmaps).
- When you want space between PEF and Roaring: the README shows Slicing smaller than Roaring on all four CRoaring datasets (e.g. 10.83 vs 15.93 bits/int on Census-1881) while staying within about 2x of Roaring's intersection time.
- x86-64 servers with SSE4.2 and AVX2 (the build uses -march=native).

## Skip it when

- When raw speed beats space: CRoaring was faster on 3 of 4 README datasets (Census-Income 4.68 vs 11.56 us) and on unions in the DCC 2021 paper; the author attributes this to extra branches from recursive partitioning.
- When minimum space is the goal: PEF and Interpolative are 1.3-2 bits/int smaller in the paper (e.g. 2.03 vs 2.23 bpi on Census-Income, 7.28 vs 10.83 on Census-1881).
- Mutable sets: there is no insert/delete; sequences are built once from sorted input.
- Non-x86 targets (ARM, Apple Silicon) or general rank/select bitvector needs: the code uses inline x86 asm (bt/sbb) and SSE4.2/AVX2 intrinsics with no fallback, and offers select/next_geq on sets, not rank/select over a plain bitvector.
- Production use needing support: no releases, 19 stars, 2 closed issues, last commit 2023-01-08.

## How it is fast

Recursive universe partitioning (the 'RUP' / slicing scheme of Pibiri, DCC 2021): the universe is cut into 2^16-integer chunks typed empty, full, dense (8 KiB bitmap, chosen when cardinality &gt;= 2^15) or sparse, and sparse chunks are re-sliced into 256-integer blocks stored either as 32-byte bitmaps or as sorted arrays of 8-bit offsets. Intersection walks the two header arrays and only touches chunks/blocks with the same id, so work is proportional to shared slices rather than list lengths. Bitmap-bitmap pairs use 64-bit AND plus ctz extraction; array-array pairs use an SSE4.2 _mm_cmpestrm all-versus-all byte compare (after Schlegel et al.) with a precomputed shuffle table, widened to 32-bit with AVX2 _mm256_cvtepu8_epi32; bitmap-array pairs use bit tests.

## Compared with alternatives

The other catalogued succinct-structures entries (SPIDER, QuadRank, LA-vector, h0_bv, rankselect) speed up rank/select over a single bitvector; pick s_indexes when the operation you need is intersection or union of many compressed sorted integer sets, as in an inverted index. Among the same author's work, mutable_rank_select is the choice for updatable bitmaps, s_indexes for static posting lists.

## Integration

| | |
|---|---|
| **Form** | header-only (include/\*.hpp) plus a CMake project for tools and benchmarks; serialization pulls in git submodules |
| **Dependencies** | jermp/essentials (serialization, timing) and jermp/mm_file (memory mapping) as git submodules; no other libraries |
| **Minimum toolchain** | C++14 (CMakeLists sets -std=c++14); tested with gcc 7.3.0 on Linux and clang 10.0.0 on macOS 10.14; clang builds add -stdlib=libc++ |
| **Platforms** | x86-64 only in practice (inline 'bt' asm in util.hpp, SSE4.2 _mm_cmpestrm and AVX2 intrinsics in intersection.hpp); Linux and macOS tested |
| **Thread safety** | not documented; s_sequence is a const view over immutable bytes, so concurrent reads look safe, but nothing states it |
| **Drop-in for the baseline** | no |

## Gotchas

- Several helpers in util.hpp and intersection.hpp (and_bitmaps, or_bitmaps, bytes_for, ss_intersect_block, ...) are defined in headers without 'inline', so including them from more than one translation unit will hit multiple-definition link errors; keep the library in one .cpp or patch the headers.
- Values are uint32_t and the chunk count is stored in a 16-bit header field, so the universe is limited to 2^32; the output buffer must be large enough for the whole result (the benchmark allocates universe() words).
- include/table.hpp is a 65,547-line precomputed shuffle table for the cmpestrm path, which slows compilation and adds about 1 MB of static data.
- Build density/size thresholds (--density) decide which lists get sliced in s_index; the README notes tests must be run with the same density used at build time.

## Known shortcomings

- Downgraded A to B: intersect.cpp times Slicing only and the PEF/Roaring runs are not in the public harness. The DCC 2021 paper (read via jermp.github.io on raw.githubusercontent.com) gives RUP 0.32/1.67/1.78 ms vs PEF 2.48/12.54/19.72 ms, about 7.5-11x (derived from page data); Roaring is equal or faster.
- x86-64 only (inline bt asm, SSE4.2 _mm_cmpestrm, AVX2, no fallback); non-inline functions defined in headers (and_bitmaps, ss_intersect_block and others) give multiple-definition link errors across translation units; uint32 values only; table.hpp holds a 65,547-line shuffle table; static sets only (no insert/delete). Roaring is faster on 3 of 4 README datasets and on unions (DCC 2021 Table 3).

## Caveats and trade-offs

Baseline is PEF (ds2i), not SDSL or sux, so baseline_in_list is false. Slicing loses to Roaring on most README datasets and ties or loses in the DCC 2021 paper, so the win is against cardinality-partitioned succinct/compressed lists (PEF and others) only. The repo's intersect.cpp times only Slicing; competitor timings come from the authors' code (ds2i, CRoaring) run outside this repo. Space is larger than PEF (e.g. 2.23 vs 2.03 bpi on Census-Income; 4.31 vs 3.12 bits/int on Gov2). Old hardware and gcc 7.3; last commit 2023-01-08.

Uses more space than PEF on all four datasets (bits per integer 2.23 vs 2.03, 10.83 vs 7.28, 4.05 vs 3.13, 10.18 vs 8.87 for Slicing vs PEF) but is smaller than Roaring on all four. Targets bitmaps and inverted lists, not general rank/select. Needs AVX/SIMD-capable CPU for the fast paths (-march=native).

## Maintenance

Inactive since 2023-01-08 with no releases, but MIT-licensed, header-based and small enough to vendor for x86-64; known-good compiler gcc 7.3.0.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification A, tier now B.
- **Tier reason:** README Table 2 numbers match, and compiler (gcc 7.3.0), flags (CMakeLists -O3 -march=native) and CPU (i7-7700) are stated, but the repo's harness (src/intersect.cpp) only times Slicing; the PEF and Roaring runs are not in public benchmark code, so not A. The peer-reviewed DCC 2021 paper (same setup) shows RUP/Slicing 7.6-10.6x faster than PEF on AND queries, which supports B.
- **Verifier notes:** Paper PDF fetched via raw.githubusercontent.com/jermp/jermp.github.io/master/assets/pdf/papers/DCC2021.pdf (Pibiri, DCC 2021, pp. 293-302); it states i7-7700, gcc 7.3.0, -O3 -march=native and uses competitors' own code. Downgrade A to B only because the baseline harness is not public; MIT license, 19 stars confirmed.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier read the DCC 2021 PDF; enricher
- **Pages the verifier opened:**
  - <https://github.com/jermp/s_indexes>
  - <https://github.com/jermp/s_indexes/tree/master/src>
  - <https://github.com/jermp/s_indexes/commits>
  - <https://raw.githubusercontent.com/jermp/s_indexes/HEAD/README.md>
  - <https://raw.githubusercontent.com/jermp/s_indexes/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/jermp/s_indexes/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/jermp/jermp.github.io/master/assets/pdf/papers/DCC2021.pdf>
- **Sources the enricher read:**
  - <https://github.com/jermp/s_indexes>
  - <https://github.com/jermp/s_indexes/tree/master/include>
  - <https://github.com/jermp/s_indexes/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/jermp/s_indexes/HEAD/README.md>
  - <https://raw.githubusercontent.com/jermp/s_indexes/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/jermp/s_indexes/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/jermp/s_indexes/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/jermp/s_indexes/HEAD/include/constants.hpp>
  - <https://raw.githubusercontent.com/jermp/s_indexes/HEAD/include/util.hpp>
  - <https://raw.githubusercontent.com/jermp/s_indexes/HEAD/include/intersection.hpp>
  - <https://raw.githubusercontent.com/jermp/s_indexes/HEAD/include/s_sequence.hpp>
  - <https://raw.githubusercontent.com/jermp/s_indexes/HEAD/include/table.hpp>
  - <https://raw.githubusercontent.com/jermp/s_indexes/HEAD/src/intersect.cpp>
  - <https://raw.githubusercontent.com/jermp/jermp.github.io/master/assets/pdf/papers/DCC2021.pdf>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/jermp/s_indexes`) · [data/wave9/enrich/raw/github_com_jermp_s_indexes.json](../../../data/wave9/enrich/raw/github_com_jermp_s_indexes.json) (enrichment confidence 0.8)

</details>
