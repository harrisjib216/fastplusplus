# Succinct data structures

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md)</sub>

**What these beat:** SDSL, sux  
**30 entries:** 8 tier A · 7 tier B · 11 tier C · 4 tier D · 27 copyable, 3 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**tsl::htrie_map (hat-trie)**](tessil-hat-trie.md) | Header-only C++11 HAT-trie string map/set using about 3x less memory than std::unordered_map&lt;std::string, T&gt;. | **A** | C++ | MIT | 🟢 active |
| 2 | [**genedex**](feldroop-genedex.md) | Rust FM-index for DNA-sized texts; locates short reads in hg38 about 4.4x faster than rust-bio's FM-index with a third of its memory. | **A** | Rust | MIT OR Apache-2.0 | 🟢 active |
| 3 | [**QuadRank / BiRank**](ragnargrootkoerkamp-quadrank.md) | Rust rank structures for bit vectors and 2-bit DNA, one cache miss per query; about 2x sux-rs Rank9 throughput with prefetching. | **A** | Rust | MIT | 🟢 active |
| 4 | [**3star-rankselect (3\* rank/select)**](nrilu-3star-rankselect.md) | Research rank/select bit vector with worst-case constant-time select at about 0.8 percent space overhead, far below SDSL, sux and pasta. | **A** | C++ | MPL-2.0 | 🟢 active |
| 5 | [**lexindex**](ilgrad-lexindex.md) | Rust crate of immutable string-to-id dictionaries; front-coded DictIndex comes in smaller than MARISA and XCDAT on the author's 13 corpora. | **A** | Rust | MIT | 🟢 active |
| 6 | [**C2 (cache-conscious succinct tries)**](gt-alg-kit-c2.md) | Research re-implementations of FST, CoCo-trie and MARISA succinct tries; C2-FST and C2-MARISA beat the originals on lookup and size. | **A** | C++ | MIT | 🟢 active |
| 7 | [**xcdat**](kampersanda-xcdat.md) | Header-only C++17 compressed double-array trie dictionary; about 2x faster key-to-ID lookup than marisa-trie, at about 1.1-2x its size. | **A** | C++ | MIT | 🟡 stale |
| 8 | [**poplar-trie**](kampersanda-poplar-trie.md) | Header-only dynamic path-decomposed trie string map; about 5.4x less memory than std::unordered_map, but 3-4x slower. | **A** | C++ | MIT | 🔴 abandoned |
| 9 | [**sucds**](kampersanda-sucds.md) | Safe pure-Rust succinct structures (Rank9Sel, DArray, Elias-Fano, wavelet matrix); select1 1.3-7.8x faster than vers-vecs on ARM64. | **B** | Rust | Apache-2.0 OR MIT | 🟢 active |
| 10 | [**sux-rs**](vigna-sux-rs.md) | Vigna's Rust succinct-structures crate; Rank9 plus SelectAdapt was fastest of four Rust crates on rank1 and select1. | **B** | Rust | Apache-2.0 OR MIT | 🟢 active |
| 11 | [**QWT (Rust quad wavelet tree)**](rossanoventurini-qwt.md) | Rust 4-ary wavelet matrix (rank/select/access over integer sequences), about 2x lower query latency than SDSL wavelet trees. | **B** | Rust | MIT | 🟢 active |
| 12 | [**LA-vector**](gvinciguerra-la-vector.md) | Header-only C++17 compressed sorted-integer container and rank/select dictionary built from piecewise linear approximations; competes with SDSL sd_vector-style… | **B** | C++ | Apache-2.0 | 🟡 stale |
| 13 | [**Sliced Indexes (s_indexes)**](jermp-s-indexes.md) | Universe-sliced compressed integer sets (bitmaps/posting lists) with SIMD intersection; 5-10x faster AND than Partitioned Elias-Fano. | **B** | C++ | MIT | 🔴 abandoned |
| 14 | [**Clustered Elias-Fano Indexes (CPEF)**](jermp-clustered-elias-fano-indexes.md) | Research inverted-index codec that encodes clusters of posting lists against a shared reference list; smaller than partitioned Elias-Fano. | **B** | C++ | Apache-2.0 | 🔴 abandoned |
| 15 | [**quad-wavelet-tree (C++ QWT)**](matteoceregini-quad-wavelet-tree.md) | Header-only C++20 4-ary (quad) wavelet matrix with about 2x lower access/rank/select latency than SDSL wavelet trees. | **B** | C++ | MIT | 🔴 abandoned |
| 16 | [**marisa-trie (libmarisa)**](s-yata-marisa-trie.md) | Static LOUDS-based recursive (nested Patricia) trie dictionary; about 7.4x smaller than darts-clone and 2.5x smaller than tx-trie. | **C** | C++ | BSD-2-Clause OR… | 🟢 active |
| 17 | [**vers (vers-vecs)**](cydhra-vers.md) | Pure-Rust succinct structures (rank/select bit vector, Elias-Fano, RMQ, wavelet matrix, BP tree) benchmarked against other Rust crates only. | **C** | Rust | Apache-2.0 OR MIT | 🟢 active |
| 18 | [**Generalized Elias-Fano (GEF)**](mxpucci-generalized-elias-fano.md) | Elias-Fano-style compressed integer arrays for unsorted sequences, with O(1) random access; claims smaller than ALP, LeCo and DAC. | **C** | C++ | Apache-2.0 | 🟢 active |
| 19 | [**succinct-bitvec-cpp (FastBitVec / RRRBitVec)**](ishantgarg2332-succinct-bitvec-cpp.md) | Small header-only rank/select bit vectors (FastBitVec, RRRBitVec) tuned on Apple Silicon; edges SDSL rank_support_v/select_support_mcl at 1M bits. | **C** | C++ | MIT | 🟢 active |
| 20 | [**Darts-clone**](s-yata-darts-clone.md) | Single-header static double-array trie with 32-bit units; half the size of Darts and faster on cache-bound lookups. | **C** | C++ | BSD-2-Clause | 🟡 stale |
| 21 | [**AWFM-index (AvxWindowFmIndex)**](traviswheelerlab-avxwindowfmindex.md) | C FM-index for DNA/RNA/protein exact k-mer count and locate; paper reports 2-6x faster than SeqAn3's FM-index. | **C** | C | BSD-3-Clause | 🟡 stale |
| 22 | [**pwm (parallel wavelet tree and matrix construction)**](kurpicz-pwm.md) | Sequential, parallel and external-memory wavelet tree/matrix construction (prefix counting/sorting); ALENEX 2018 reports up to 2x faster than Shun's construction. | **C** | C++ | BSD-2-Clause | 🔴 abandoned |
| 23 | [**rankselect (PTSelect, splatlab)**](splatlab-rankselect.md) | Research fork of CMU's CS-Poppy rank/select bitvector that swaps word-level select for PTSelect (PDEP+TZCNT); benchmarked against SDSL. | **C** | C++ | Apache-2.0 | 🔴 abandoned |
| 24 | [**SPIDER (Succinct Predictive InDEx for Rank and select)**](williams-cs-spider.md) | Research C code for a \~3.8%-overhead rank/select bit vector that interleaves rank counters with data and predicts select positions. | **C** | C | no license (study only) | 🟡 stale |
| 25 | [**orzo (Elias-Fano encoded L2 rank/select)**](hpcgroup-orzo.md) | Research rank/select index for plain bitvectors that Elias-Fano-packs L2 counts, cutting index space below pasta-flat and cs-poppy. | **C** | C++ | no license (study only) | 🟡 stale |
| 26 | [**h0_bv (H0-compressed bitvectors)**](saskeli-h0-bv.md) | Research C++ RRR-style H0-compressed bitvectors with faster block decoding; beat SDSL rrr_vector on access at block size 63. | **C** | C++ | no license (study only) | 🟡 stale |
| 27 | [**AWRY**](traviswheelerlab-awry.md) | Rust port of the AVX2 windowed FM-index (AvxWindowFmIndex); in the only third-party benchmark found it is slower than genedex. | **D** | Rust | BSD-3-Clause | 🟡 stale |
| 28 | [**wavelet_forest**](aaronhong1024-wavelet-forest.md) | Research code for the SPIRE 2024 wavelet-forest paper: per-block SDSL Huffman wavelet trees instead of one global tree. | **D** | C++ | GPL-3.0 | 🟡 stale |
| 29 | [**mutable_rank_select**](jermp-mutable-rank-select.md) | SIMD b-ary Segment-Tree index for rank/select/flip on mutable bitmaps; paper reports it beats Marchini-Vigna compact Fenwick trees. | **D** | C++ | MIT | 🔴 abandoned |
| 30 | [**faster-minuter (wt_fbb fixed-block-boosting wavelet tree)**](dominikkempa-faster-minuter.md) | Single-header SDSL-compatible byte-alphabet wavelet tree (wt_fbb) using fixed-block compression boosting, aimed at faster, smaller FM-indexes than SDSL's. | **D** | C++ | MIT | 🔴 abandoned |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
