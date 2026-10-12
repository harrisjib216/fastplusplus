# h0_bv (H0-compressed bitvectors)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Succinct data structures](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `no license` · 🟡 stale

> Research C++ RRR-style H0-compressed bitvectors with faster block decoding; beat SDSL rrr_vector on access at block size 63.

| | |
|---|---|
| **Beats** | SDSL rrr_vector (and SDSL hybrid bitvector) |
| **Claimed result** | plotting/results.ipynb output (machine 'laptop'): at block size 63/64, the iterative decoder IT63 vs SDSL rrr_vector b=63 access 249 vs 345 ns on WT-DNA-1GB, 304 vs 392 ns on bv-dump, 75 vs 94 ns on WT-WEB-1GB (about 1.2-1.4x, derived from page data); rank 262 vs 345 ns on WT-DNA but 179 vs 148 ns on WT-WEB (slower). GAP/DBS at b=15 (access 151-165 ns on DNA/bv-dump) beat SDSL b=24 (256/284 ns) but are slower than the SDSL-based RRR15 row (110/126 ns). Paper (SEA 2025, snippet only): non-lexicographical block codes 'can lead to faster query times'. |
| **Workload** | Access and rank on H0-compressed bitvectors with alternative block decoding and code assignment, benchmarked on web and DNA data (WT-WEB-1GB, WT-DNA-1GB) using code adapted from SDSL rrr_time_and_space.cpp. |
| **Metric** | latency |
| **Hardware** | Result tables are from a machine labelled 'laptop' (CPU not stated); the notebook also lists AMD EPYC 7452 and Intel Xeon E7-8890 v4 runs. |
| **Compiler and flags** | g++ (version unstated) -std=c++2b -march=native -Ofast -DNDEBUG (Makefile) |
| **Adoption** | 1 star |
| **Last commit** | 2025-07-17 |
| **Links** | [repository](https://github.com/saskeli/h0_bv) · [benchmark](https://github.com/saskeli/h0_bv/blob/master/plotting/results.ipynb) |

## Verdict

First-party notebook output from a machine labelled 'laptop' (CPU not stated; g++ -std=c++2b -Ofast -march=native) shows the iterative b=63 decoder against SDSL rrr_vector&lt;63&gt; at equal space: access 249 vs 345 ns on WT-DNA-1GB and 75 vs 94 ns on WT-WEB-1GB (about 1.2-1.4x), rank 262 vs 345 ns on DNA but 179 vs 148 ns on WEB (slower); SDSL's rrr_vector&lt;15&gt; remains faster in absolute terms at more space.

## Use it when

- Research or prototyping of RRR-style compressed bitvectors for FM-indexes and wavelet trees, where you want SDSL rrr_vector&lt;63&gt; space (about 0.71 bits/bit on WT-DNA-1GB, same as SDSL) with lower access latency (249 vs 345 ns in the notebook).
- Workloads dominated by random access on compressible bitvectors at large block size, where the iterative b=63 decoder beat SDSL b=63 on every dataset in the notebook (for example 75 vs 94 ns on WT-WEB-1GB).
- Build-time-sensitive pipelines: the notebook shows IT63 construction at 3.2 s vs 21.0 s for SDSL b=63 on WT-DNA-1GB (about 6.5x, derived from page data).
- As reference code for the SEA 2025 paper's decoders, to port the iterative or gap-table decoding into your own bitvector.

## Skip it when

- Production use: no LICENSE file (all rights reserved by default), 1 star, no releases, debugging code still present, and hyb_256.hpp is marked broken (its checksums disagree in the notebook).
- Rank-heavy workloads on very compressible data: IT63 rank on WT-WEB-1GB was 179 ns vs 148 ns for SDSL b=63, so it is slower there.
- When access speed matters more than space: SDSL's rrr_vector&lt;15&gt; (RRR15 row) was fastest overall (110 ns access, 149 ns rank on WT-DNA-1GB) at about 0.90 bits/bit vs 0.71 for IT63.
- Incompressible or random dense bitvectors: on RND-1 all H0 variants use more than 1 bit per bit (IT63 1.07), worse than a plain bitvector with rank support.
- Non-x86 or pre-BMI2 targets: headers include immintrin.h and select uses _pdep_u64/_pdep_u32 (BMI2).

## How it is fast

RRR decoding of a block offset into its bit pattern dominates query time at large block sizes. h0_63/h0_it decode a 63/64-bit block iteratively in 8-bit chunks using compile-time binomial and limit tables (constexpr std::array), so a block is decoded with a few table lookups instead of SDSL's bit-by-bit combinatorial walk. h0_gap stores a sampled (gap) lookup table of all block codes for b&lt;32, and the de Bruijn variants assign non-lexicographic codes to blocks (the SEA 2025 paper 'Succinct Rank Dictionaries Revisited' argues these can give faster queries). Select uses BMI2 _pdep_u64 for the in-word step.

## Compared with alternatives

Pick it over LA-vector or succinct-bitvec-cpp's RRRBitVec only when you specifically need the RRR (block class/offset) representation with faster decoding at b=63; for compressed bitvectors you intend to ship, LA-vector (TALG 2022, select fastest in its comparison) is the better-supported choice, and for uncompressed rank/select SPIDER or rankselect trade more space for speed.

## Integration

| | |
|---|---|
| **Form** | header-only (include/\*.hpp), but depends on SDSL headers and library; the benchmark build patches files inside the sdsl-lite submodule |
| **Dependencies** | sdsl-lite (git submodule; int_vector and bit_vector), Python 3 to generate the de Bruijn headers (dbs15/dbs24/wdbs\*.hpp) |
| **Minimum toolchain** | g++ with -std=c++2b (Makefile); h0_gap needs -fconstexpr-ops-limit=5000000000 -fconstexpr-loop-limit=10000000 (GCC-specific flags) for its compile-time tables |
| **Platforms** | x86-64 with BMI2 (immintrin.h, _pdep_u64); Makefile uses -march=native and reads the cache line size via getconf (Linux) |
| **Thread safety** | not documented; query methods are const and the structures are immutable after construction |
| **Drop-in for the baseline** | partial — constructed from an sdsl::bit_vector like rrr_vector, but queries are member functions access/rank/select rather than operator[] plus rank_support/select_support objects, and there is no serialization |

## Gotchas

- Select timings in the notebook are not valid: the harness (adapted from SDSL's rrr_time_and_space.cpp, which has the same bug) sets stop = timer::now() where it should reset start before the select loop, so every reported select time also includes the rank loop.
- The benchmark measures independent random queries (sum of results over 10M queries from 2^20 sampled positions), i.e. throughput-like ns/query, not dependent-query latency.
- Each constructor builds four temporary std::vectors copying metadata and block codes (left over from debugging), adding about 8 bytes per 63-bit block of peak memory during construction.
- The SDSL baseline is built from patched sdsl_hacks/rrr_vector.hpp and rrr_helper.hpp; the patches add size accessors and an optional RRR_NO_OPT path that the Makefile does not enable, so the baseline appears unmodified in behavior.

## Known shortcomings

- Downgraded B to C: real numbers live in plotting/results.ipynb (machine 'laptop', CPU unstated) and the win over SDSL rrr_vector is mixed: IT63 vs SDSL b=63 access about 1.2-1.4x faster, rank slower on WT-WEB, b=15 variants slower than RRR15. No license, so reference; 1 star; stale. The SEA 2025 paper (Dagstuhl, arXiv blocked) could restore B.
- The notebook's select times are invalid: the harness sets stop instead of start before the select loop (a bug inherited from SDSL's rrr_time_and_space.cpp), so select includes the rank loop; the access/rank claim is unaffected. The benchmark measures independent-query throughput, not dependent latency. No serialize/load, x86 BMI2 only, no license, hyb_256 checksums mismatch in the notebook. The SDSL patches only add size accessors, so the baseline is fair. Paper: 'Succinct Rank Dictionaries Revisited', SEA 2025 (LIPIcs.SEA.2025.15).

## Caveats and trade-offs

No LICENSE file (raw LICENSE 404, none shown on the repo page), so reference only. Win over SDSL rrr_vector is mixed: faster access at equal large block sizes, but rank is slower on WT-WEB and the b=15 variants are slower than the RRR15 row. Numbers are first-party notebook output from an unnamed 'laptop' CPU. hyb_256.hpp is marked broken in the README. Paper (Donges and Puglisi, SEA 2025, LIPIcs vol 338) not opened (Dagstuhl blocked).

Entropy-compressed bitvectors (RRR family) trading code complexity for decode speed. Research code: one hybrid variant (hyb_256) is marked broken and debugging code remains.

## Maintenance

Stale research code (last commit 2025-07-17, 48 commits, 1 star) with no license, so it is reference only: read it for the decoding ideas, do not vendor it.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification B, tier now C.
- **Tier reason:** plotting/results.ipynb carries first-party output tables comparing the H0 bitvectors with SDSL rrr_vector at block sizes 24/31/63 on six datasets (benchmark code sdsl_hacks/rrr_time_and_space.cpp, Makefile g++ -Ofast -march=native), but the 'laptop' machine that produced the tables has no CPU model stated (the notebook lists an AMD EPYC 7452 and a Xeon E7-8890 v4 for other runs), so not A. The SEA 2025 paper could support B, but it was not opened (Dagstuhl blocked) and its snippet gives no magnitude, so C.
- **Verifier notes:** Found real numbers in plotting/results.ipynb (record said none) but they show a mixed space-time trade-off rather than a clean win; tier set to C, not B, since the paper was not readable. A retier to B is possible from an environment that reaches drops.dagstuhl.de.
- **Fields the verifier corrected:** `claimed_speedup`, `benchmark_url`, `compiler_and_flags`, `hardware`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier; notebook: IT63 build 3.2 s vs SDSL b=63 21.0 s on WT-DNA-1GB (about 6.5x, derived from page data) at equal space 0.713 bits per bit
- **Pages the verifier opened:**
  - <https://github.com/saskeli/h0_bv>
  - <https://github.com/saskeli/h0_bv/commits>
  - <https://github.com/saskeli/h0_bv/tree/master/plotting>
  - <https://raw.githubusercontent.com/saskeli/h0_bv/HEAD/README.md>
  - <https://raw.githubusercontent.com/saskeli/h0_bv/HEAD/Makefile>
  - <https://raw.githubusercontent.com/saskeli/h0_bv/HEAD/tester.sh>
  - <https://raw.githubusercontent.com/saskeli/h0_bv/master/plotting/results.ipynb>
- **Sources the enricher read:**
  - <https://github.com/saskeli/h0_bv>
  - <https://raw.githubusercontent.com/saskeli/h0_bv/HEAD/README.md>
  - <https://raw.githubusercontent.com/saskeli/h0_bv/HEAD/Makefile>
  - <https://raw.githubusercontent.com/saskeli/h0_bv/HEAD/tester.sh>
  - <https://raw.githubusercontent.com/saskeli/h0_bv/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/saskeli/h0_bv/HEAD/sdsl_hacks/rrr_time_and_space.cpp>
  - <https://raw.githubusercontent.com/saskeli/h0_bv/HEAD/sdsl_hacks/rrr_vector.hpp>
  - <https://raw.githubusercontent.com/saskeli/h0_bv/HEAD/sdsl_hacks/rrr_helper.hpp>
  - <https://raw.githubusercontent.com/saskeli/h0_bv/HEAD/include/h0_63.hpp>
  - <https://raw.githubusercontent.com/saskeli/h0_bv/HEAD/include/h0_it.hpp>
  - <https://raw.githubusercontent.com/saskeli/h0_bv/HEAD/include/h0_bv.hpp>
  - <https://raw.githubusercontent.com/saskeli/h0_bv/HEAD/include/h0_gap.hpp>
  - <https://raw.githubusercontent.com/saskeli/h0_bv/HEAD/include/internal.hpp>
  - <https://raw.githubusercontent.com/saskeli/h0_bv/master/plotting/results.ipynb>
  - <https://raw.githubusercontent.com/simongog/sdsl-lite/master/include/sdsl/rrr_vector.hpp>
  - <https://raw.githubusercontent.com/simongog/sdsl-lite/master/include/sdsl/rrr_helper.hpp>
  - <https://raw.githubusercontent.com/simongog/sdsl-lite/master/benchmark/rrr_vector/src/rrr_time_and_space.cpp>
  - https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.SEA.2025.15 (WebSearch snippet only; Dagstuhl blocked)
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/saskeli/h0_bv`) · [data/wave9/enrich/raw/github_com_saskeli_h0_bv.json](../../../data/wave9/enrich/raw/github_com_saskeli_h0_bv.json) (enrichment confidence 0.7)

</details>
