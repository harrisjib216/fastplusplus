# faster-minuter (wt_fbb fixed-block-boosting wavelet tree)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Succinct data structures](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Single-header SDSL-compatible byte-alphabet wavelet tree (wt_fbb) using fixed-block compression boosting, aimed at faster, smaller FM-indexes than SDSL's.

| | |
|---|---|
| **Beats** | SDSL wavelet trees (e.g. Huffman-shaped and hybrid-bitvector wavelet trees inside SDSL FM-indexes) |
| **Claimed result** | No numbers on the repo page. The Algorithmica 2019 paper (Gog, Karkkainen, Kempa, Petri, Puglisi) is cited for the experiments; its abstract, seen only as a search snippet, says the new FM-indexes are 'consistently fast and small relative to the state-of-the-art'. No ratio against SDSL has been seen. |
| **Workload** | Wavelet tree plugged into an FM-index (the 'Faster Minuter' index) for count and locate queries; details only in the Algorithmica 2019 paper, which could not be opened here (publisher and arXiv hosts blocked). |
| **Metric** | latency |
| **Adoption** | 17 stars, 1 fork |
| **Last commit** | 2021-05-18 |
| **Links** | [repository](https://github.com/dominikkempa/faster-minuter) · [benchmark](https://github.com/dominikkempa/faster-minuter) |

## Verdict

Nothing measurable was read this session: the repo has no numbers or benchmark code, the Algorithmica 2019 paper (and its arXiv 1104.3810 SPIRE 2011 precursor) could not be opened, and the only reachable text, search snippets of the abstract, says the new indexes are 'consistently fast and small relative to the state-of-the-art' with no ratio, compiler or hardware.

## Use it when

- Building a byte-alphabet FM-index (DNA, text, BWT of a log or corpus) on SDSL where count/locate speed or index size matters and you can test against SDSL's own wt_huff or wt_hutu choices.
- Highly compressible or locally skewed BWTs, where per-block Huffman shaping gives compression boosting without the cost of optimal partitioning.
- Research or benchmarking of FM-index variants that needs the reference implementation of the Algorithmica 2019 fixed-block-boosting wavelet tree.
- Workloads dominated by rank and LF-mapping (backward search, inverse_select), which is what the class implements.

## Skip it when

- You need select on the sequence, lex_count or interval_symbols (bidirectional or range searches): wt_fbb does not implement them.
- Alphabets larger than 256 symbols or integer sequences: the class is byte-alphabet only (sdsl::byte_alphabet_tag, uint8_t symbols).
- You need a maintained library: 2 commits, version 0.1.0, last commit 2021-05-18, no tests, no build files and no benchmark code in the repo.
- You need numbers you can check before adopting it: the repo has no measurements, and the paper's tables could not be read here, so the speed and space win over SDSL is unverified.
- Your project does not already use sdsl-lite: the header depends on SDSL types throughout.

## How it is fast

Fixed-block compression boosting: the text is cut into superblocks (2^20 symbols by default) and variable-size blocks, and each block gets its own small Huffman-shaped wavelet tree over only the symbols that occur in it, so the per-block alphabet and tree height stay small and a rank query touches a few cache lines. Precomputed rank counts at hyperblock (2^32), superblock and block boundaries, plus a navigational block header (ADD_NAVIGATIONAL_BLOCK_HEADER), let a query skip tree navigation for boundary ranks. The bitvectors are sdsl::hyb_vector (hybrid bitvectors) by default, and any SDSL bitvector with a rank_1_type can be substituted for speed.

## Compared with alternatives

Pick wt_fbb over QWT (C++ or Rust) or wavelet_forest only when you need a compressed, Huffman-shaped byte-alphabet FM-index inside an existing SDSL codebase and care about size; QWT has a published 2x win over SDSL on access/rank/select and supports select, so it is the safer choice for uncompressed, query-speed-first use.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | sdsl-lite (sdsl_concepts, int_vector_buffer, bit_vectors, io headers) |
| **Minimum toolchain** | not documented; uses C++11 features (defaulted constructors, move semantics) and GCC packed attributes; 'tested on Linux/PC' |
| **Platforms** | Linux on x86-64 per README ('tested on Linux/PC'); relies on __attribute__((packed)) and 32-bit pointer casts into byte arrays, so other compilers or strict-alignment targets are untested |
| **Thread safety** | not documented; the query methods are const and the class has no mutable members, so concurrent read-only queries look safe, but this is not promised |
| **Drop-in for the baseline** | partial — follows SDSL's wavelet tree concept (wt_tag, byte alphabet, operator[], rank, inverse_select, serialize/load) so it can be a csa_wt template argument for backward search, but lacks select, lex_count and interval_symbols that some SDSL algorithms call |

## Gotchas

- Configuration is by #define macros at the top of the header (ADD_NAVIGATIONAL_BLOCK_HEADER, SPARSE_SUPERBLOCK_MAPPING, ALLOW_VARIABLE_BLOCK_SIZE, FAST_CONSTRUCTION), so they apply to every instantiation in the translation unit.
- The off-by-default SPARSE_SUPERBLOCK_MAPPING path's load() calls sdsl::load without the stream argument and references a member m_select_support that does not exist, so enabling that option should fail to compile (read from source, not built).
- rank(i, c) assumes 0 &lt;= i &lt;= size() and does no bounds checking.
- A search snippet claiming '2-3 times faster than the fastest known ones, for 1.5-5 times more space' belongs to the separate 'FM-index for Dummies' paper (Grabowski et al.), not to this project; do not quote it for wt_fbb.

## Known shortcomings

- Downgraded C to D: no numbers anywhere reachable; the Algorithmica paper (Springer, ResearchGate, helsinki.fi blocked) holds them. Last commit 2021-05-18. Paper-access retier candidate.
- No select, lex_count or interval_symbols; byte alphabet only; needs sdsl-lite. From source (not built): the off-by-default SPARSE_SUPERBLOCK_MAPPING load() calls sdsl::load without a stream and uses a missing member m_select_support, so it should not compile when enabled. The snippet '2-3 times faster than the fastest known ones, for 1.5-5 times more space' belongs to 'FM-index for Dummies' (Grabowski et al.), not to this project.

## Caveats and trade-offs

This is wt_fbb, an SDSL-compatible wavelet tree class with no benchmark scripts in the repo. The win over SDSL is unverified because the Algorithmica paper (arXiv 1104.3810 is the SPIRE 2011 conference version) could not be opened. Retier when arXiv or Springer is reachable; B is likely if the paper's count/locate tables beat SDSL FM-indexes. Third-party follow-ups ('Another Virtue of Wavelet Forests', SPIRE 2024; 'Wavelet Forests Revisited', arXiv 2604.11338) study the same fixed-block-boosting wavelet forests; the latter reports, per snippet only, up to 2x faster queries than standalone optimized wavelet trees with RRR bitvectors. A search snippet's 'up to 2x access/select, 3x rank vs SDSL' figure belongs to Kurpicz's 'Faster Wavelet Tree Queries', a different project, and must not be attributed here. The repo has 2 commits; the last is 2021-05-18.

SDSL-compatible class wt_fbb; default hybrid bitvector, faster but larger bitvectors can be plugged in. Tested on Linux/PC only. Header-only include directory.

## Maintenance

Abandoned research code (2 commits, last 2021-05-18, version 0.1.0) but MIT-licensed and a single \~1,900-line header, so it is easy to vendor into an SDSL project if you benchmark it yourself first.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification C, tier now D.
- **Tier reason:** The repo README has no numbers and no benchmark code. It only points to the Algorithmica 2019 paper, which could not be opened here (Springer, ResearchGate, the Helsinki research portal and arXiv are blocked). The only paper text seen, through search snippets, is directional ('consistently fast and small relative to the state-of-the-art'), so this is D until the paper's tables are read.
- **Verifier notes:** Downgraded from C to D: neither the repo nor anything reachable shows numbers. Keep it (it is a peer-reviewed technique widely cited by later wavelet-forest papers) and put it on the paper-access retier list.
- **Fields the verifier corrected:** `claimed_speedup`, `last_commit`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/dominikkempa/faster-minuter>
  - <https://raw.githubusercontent.com/dominikkempa/faster-minuter/HEAD/README.md>
  - <https://raw.githubusercontent.com/dominikkempa/faster-minuter/HEAD/LICENCE>
  - <https://github.com/dominikkempa/faster-minuter/commits/master>
- **Sources the enricher read:**
  - <https://github.com/dominikkempa/faster-minuter>
  - <https://raw.githubusercontent.com/dominikkempa/faster-minuter/HEAD/README.md>
  - <https://raw.githubusercontent.com/dominikkempa/faster-minuter/HEAD/VERSION>
  - <https://github.com/dominikkempa/faster-minuter/tree/master/include>
  - <https://raw.githubusercontent.com/dominikkempa/faster-minuter/HEAD/include/wt_fbb.hpp>
  - https://sites.google.com/view/dkempa/software (EGRESS_BLOCKED)
  - WebSearch: "Fixed Block Compression Boosting in FM-Indexes" pdf (snippets only)
  - WebSearch: "Faster, Minuter" DCC 2016 (snippets only)
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/dominikkempa/faster-minuter`) · [data/wave9/enrich/raw/github_com_dominikkempa_faster_minuter.json](../../../data/wave9/enrich/raw/github_com_dominikkempa_faster_minuter.json) (enrichment confidence 0.55)

</details>
