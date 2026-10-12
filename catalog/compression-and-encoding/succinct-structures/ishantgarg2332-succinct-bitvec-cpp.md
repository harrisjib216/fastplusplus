# succinct-bitvec-cpp (FastBitVec / RRRBitVec)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Succinct data structures](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Small header-only rank/select bit vectors (FastBitVec, RRRBitVec) tuned on Apple Silicon; edges SDSL rank_support_v/select_support_mcl at 1M bits.

| | |
|---|---|
| **Beats** | SDSL rank_support_v and select_support_mcl |
| **Claimed result** | README table at N=1M, 50% density: FastBitVec rank 1.65 ns vs SDSL rank_support_v 2.25 ns (about 1.36x, derived from page data); FastBitVec select 44.5 ns vs SDSL select_support_mcl 78.4 ns (about 1.76x, derived from page data); RRRBitVec select 33.7 ns (paper states 2.33x over SDSL). Paper Table 1 rank across sizes: FastBitVec 1.65/1.65/1.71/1.95 ns vs SDSL 2.32/2.25/2.29/2.45 ns at 100K/1M/10M/100M (about 1.26x at 100M, derived from page data). Total space 1.141 bpe vs SDSL 1.250 bpe (SDSL figure counts only the rank_support_v directory; select_support_mcl adds more). |
| **Workload** | Rank and select on a 1,000,000-bit vector, 50% density, uniform random queries, Google Benchmark mean latency. |
| **Metric** | latency |
| **Hardware** | Apple Silicon M-series (exact chip not stated) |
| **Compiler and flags** | Apple Clang 15.0.0, -O3 -march=native -std=c++17 -DNDEBUG, CMake Release |
| **Adoption** | 2 stars |
| **Last commit** | 2026-05-24 |
| **Links** | [repository](https://github.com/ishantgarg2332/succinct-bitvec-cpp) · [benchmark](https://github.com/ishantgarg2332/succinct-bitvec-cpp) |

## Verdict

First-party Google Benchmark runs at 1M bits, 50% density, uniform random queries on an unspecified Apple Silicon M-series CPU with Apple Clang 15.0.0 and -O3 -march=native: FastBitVec rank 1.65 ns vs SDSL rank_support_v 2.25 ns, FastBitVec select 44.5 ns and RRRBitVec select 33.7 ns vs SDSL select_support_mcl 78.4 ns. The companion PDF extends rank to 100M bits, where FastBitVec's lead shrinks to about 1.26x; select is reported only at 1M bits.

## Use it when

- Static bit vectors up to a few hundred million bits where rank latency matters and you want a single header with no SDSL build dependency.
- Read-heavy rank workloads on ARM64 (Apple M-series) where a 1.3-1.4x gain over SDSL rank_support_v at cache-resident sizes is worth having (narrowing to about 1.26x at 100M bits per the paper's Table 1).
- Select-heavy workloads at medium-to-high density where RRRBitVec's 33.7 ns select (1M bits, 50%) beats SDSL select_support_mcl's 78.4 ns in the author's runs.
- Very sparse or very dense vectors where RRRBitVec's entropy coding gets below 1 bit per element (0.84 bpe at 1% density per the README).
- Teaching or prototyping: about 600 lines, easy to read and adapt.

## Skip it when

- Bit vectors longer than 2^32 bits: select sample tables store positions (FastBitVec) and superblock indices (RRRBitVec) as uint32_t, so FastBitVec select breaks silently beyond about 4.29 billion bits.
- When you need rank0/select0 or access on RRRBitVec: the README says all four queries are supported, but the header implements only rank1 and select1 (no rank0/select0 functions exist in bitvec.hpp or the tests).
- When you need serialization, mmap loading, or dynamic updates: none are provided; every structure is rebuilt in memory from RawBits.
- Sparse vectors with FastBitVec select: 256 ones span about 25,600 bits at 1% density, so select becomes a longer binary search of rank1 calls; RRRBitVec, sux/pasta or SDSL sd_vector fit better.
- Space-critical uses at 50% density with RRRBitVec: its 1.695 bpe total is larger than an uncompressed vector plus FastBitVec's index (1.141 bpe).

## How it is fast

FastBitVec is a two-level rank directory with 4096-bit superblocks (64-bit absolute counts) and 256-bit blocks (16-bit relative counts), so a rank query is two table loads plus at most four popcounts that the compiler unrolls. Select samples every 256th set bit (uint32 positions) and then binary-searches with rank1 inside the sampled range. RRRBitVec is a Raman-Raman-Rao encoding with 15-bit blocks, 4-bit packed classes, variable-width offsets and 240-bit superblocks, decoded through precomputed class/offset/decode tables; its select narrows to one superblock via the same 1-in-256 sampling and scans at most 16 class nibbles.

## Compared with alternatives

Pick it over SPIDER, rankselect (PTSelect) or QuadRank only when you want a tiny dependency-free header for plain rank/select on ARM64 and can live with unreviewed code; those siblings are better engineered and benchmarked against stronger baselines (pasta, poppy, rank9). For compressed bit vectors, h0_bv and LA-vector are more mature alternatives to its RRRBitVec.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none for the library (C++ standard library only); Google Benchmark v1.8.3 and optionally sdsl-lite for the benchmark binary |
| **Minimum toolchain** | C++17; uses __builtin_popcountll/__builtin_popcount, so GCC or Clang (MSVC not supported as written); tested only with Apple Clang 15.0.0 |
| **Platforms** | any 64-bit target with GCC/Clang builtins; tuned and measured only on Apple Silicon ARM64 (-march=native) |
| **Thread safety** | not documented; queries are const and noexcept with no mutable state (RRR lookup tables are a function-local static, initialized thread-safely in C++11+), so concurrent reads after construction should be safe |
| **Drop-in for the baseline** | partial: same role as SDSL rank_support_v/select_support_mcl but a different API (own RawBits container, inclusive rank1, -1 for missing select), no serialization, no rank0/select0 |

## Gotchas

- Every index class stores a const RawBits& to the input, not a copy: the RawBits object must outlive the index, or rank/select read freed memory. RRRBitVec keeps the reference too, though it only uses the length.
- rank1(i) counts ones in [0, i] inclusive, unlike SDSL's rank(i) over [0, i); the benchmark calls SDSL with i + 1 to match. FastBitVec::rank1 does no bounds check (i &gt;= len reads past the words array); RRRBitVec::rank1 clamps to total_ones.
- The SDSL space figure (1.250 bpe) counts only the rank_support_v directory, not select_support_mcl, while FastBitVec's 1.141 bpe includes its select samples; SDSL's more compact rank_support_v5 was not compared.
- README clone URL (github.com/ishgarg/succinct-bitvec-cpp) points to a different account than the repo.

## Known shortcomings

- Tier C: README and the in-repo paper PDF agree (rank to 100M: 1.95 vs 2.45 ns, about 1.26x, derived from page data) but the Apple M-series CPU is not named; the arXiv id 2605.25528 could not be confirmed from the README or PDF.
- The README promises rank0/select0 but bitvec.hpp and the tests only have rank1/select1; index classes keep a const RawBits& (dangling if the input is freed); select samples are uint32_t, so FastBitVec select breaks past 2^32 bits; FastBitVec::rank1 has no bounds check; no serialization; SDSL's compact rank_support_v5 was not compared.

## Caveats and trade-offs

Single-author preprint (companion PDF succint_bitvec.pdf is in the repo; the arXiv number 2605.25528 does not appear in the README or the PDF, so it is unverified here), not peer reviewed. The headline README table is N=1M (cache-resident); the paper's Table 1 extends rank to 100M (12.5 MB, beyond the 4 MiB L2), where the FastBitVec lead narrows to about 1.26x (derived from page data); select is only reported at 1M. Exact CPU model missing ('Apple Silicon M-series, 64 KiB L1D, 4 MiB L2'), so tier C not A. SDSL rank_support_v is not the most compact SDSL rank (v5 has less space), and sux, pasta, poppy and SPIDER were not compared. The SDSL space figure excludes the select_support_mcl directory. Correctness fuzzer with 78M assertions is included. README's clone URL points to github.com/ishgarg/succinct-bitvec-cpp, not this repo.

Header-only. Tuned for ARM64: 4096/256-bit asymmetric blocks and select sampling every 256th set bit. RRRBitVec is entropy compressed but slow on rank (9.39 ns). Build time of FastBitVec about 330 ms at 100M bits.

## Maintenance

Two commits on 2026-05-24, 2 stars, no issues; MIT-licensed and small enough to vendor, but it is a new single-author research companion with a README that overstates the API (rank0/select0).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** README and the companion paper PDF checked into the repo (succint_bitvec.pdf) give first-party Google Benchmark numbers against SDSL rank_support_v and select_support_mcl, with public bench code (src/bench.cpp, BM_Rank_SDSL under HAS_SDSL), Apple Clang 15.0.0 and -O3 -march=native -std=c++17 -DNDEBUG; the CPU is only 'Apple Silicon M-series', so not A, and the paper is an unreviewed single-author preprint, so not B.
- **Verifier notes:** MIT license confirmed (LICENSE file, Copyright 2026 Ishant Garg), 2 stars, 0 forks, 2 commits both 2026-05-24; metadata correct. Numbers verified in the README and the companion paper PDF; tier C stands.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/ishantgarg2332/succinct-bitvec-cpp>
  - <https://github.com/ishantgarg2332/succinct-bitvec-cpp/commits>
  - <https://raw.githubusercontent.com/ishantgarg2332/succinct-bitvec-cpp/HEAD/README.md>
  - <https://raw.githubusercontent.com/ishantgarg2332/succinct-bitvec-cpp/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/ishantgarg2332/succinct-bitvec-cpp/HEAD/succint_bitvec.pdf>
  - <https://raw.githubusercontent.com/ishantgarg2332/succinct-bitvec-cpp/HEAD/src/bench.cpp>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/ishantgarg2332/succinct-bitvec-cpp/HEAD/README.md>
  - <https://raw.githubusercontent.com/ishantgarg2332/succinct-bitvec-cpp/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ishantgarg2332/succinct-bitvec-cpp/HEAD/include/bitvec.hpp>
  - <https://raw.githubusercontent.com/ishantgarg2332/succinct-bitvec-cpp/HEAD/src/bench.cpp>
  - <https://raw.githubusercontent.com/ishantgarg2332/succinct-bitvec-cpp/HEAD/src/test.cpp>
  - <https://github.com/ishantgarg2332/succinct-bitvec-cpp/issues>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/ishantgarg2332/succinct-bitvec-cpp`) · [data/wave9/enrich/raw/github_com_ishantgarg2332_succinct_bitvec_cpp.json](../../../data/wave9/enrich/raw/github_com_ishantgarg2332_succinct_bitvec_cpp.json) (enrichment confidence 0.8)

</details>
