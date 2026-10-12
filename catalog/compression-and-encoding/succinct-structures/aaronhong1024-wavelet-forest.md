# wavelet_forest

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Succinct data structures](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `GPL-3.0` · 🟡 stale

> Research code for the SPIRE 2024 wavelet-forest paper: per-block SDSL Huffman wavelet trees instead of one global tree.

| | |
|---|---|
| **Beats** | SDSL Huffman-shaped wavelet tree (sdsl-lite), uncompressed bitvectors |
| **Claimed result** | README, no numbers: wavelet forest 'often outperforms' the wavelet tree on larger alphabets (ASCII); faster for hex across a broad range of block sizes; blocks of about 0.5 MB frequently best; speedups are not monotonic in block size. |
| **Workload** | access queries (10,000 random positions) on synthetic multi-GB texts over bit, base-4, octal, hex and ASCII alphabets; wavelet forest built with fixed block sizes from 50 KB to 10 MB versus one global wavelet tree. |
| **Metric** | latency |
| **Compiler and flags** | C++17 via CMake (CMakeLists.txt sets no build type or optimization flags; OpenMP if found). The README says g++ &gt;= 12 with CMAKE_BUILD_TYPE=Release. |
| **Adoption** | 1 star |
| **Last commit** | 2025-08-29 |
| **Links** | [repository](https://github.com/AaronHong1024/wavelet_forest) · [benchmark](https://github.com/AaronHong1024/wavelet_forest/blob/master/src/main.cpp) |

## Verdict

No measurements are reachable: the README states qualitatively that the forest often beats an SDSL Huffman-shaped wavelet tree on access for ASCII and hex alphabets with uncompressed bitvectors, best near 0.5 MB blocks, citing the SPIRE 2024 paper (arXiv 2308.07809, blocked here); no compiler, flags or hardware are given, and the repo's own timer cannot reproduce a fair comparison.

## Use it when

- As a reference for reproducing or extending the 'Another Virtue of Wavelet Forests' experiments (access on byte alphabets, uncompressed bitvectors).
- When you already use SDSL wt_huff for access-heavy queries on multi-GB byte texts and want a few-dozen-line sketch of the block-partitioned alternative to re-implement.
- Large alphabets (hex, ASCII) where the README reports the forest most often ahead; block sizes around 0.5 MB are the README's suggested starting point.

## Skip it when

- As a library: there is no header, no API, no rank/select, no tests, and every program has hard-coded placeholder paths.
- When you need numbers to justify the switch: the repo has none and its timing program is not a fair comparison (see gotchas).
- Small texts that fit in cache (the generator's default is only 8 MB), or binary/DNA-sized alphabets, where the README itself reports little or no gain.
- GPL-incompatible projects: the LICENSE is GPL-3.0 despite the README calling it permissive.
- If you want a maintained fast wavelet structure: QWT (C++ or Rust) and faster-minuter's wt_fbb are complete libraries with rank/select.

## How it is fast

Wavelet forest (block-partitioned wavelet tree, as used in fixed-block compression boosting): each block's tree has small bitvectors, so a root-to-leaf access descent stays inside one small region of memory instead of touching log(sigma) far-apart bitvectors of a global tree. Search-result snippets of the paper put it as a wavelet-tree descent usually causing about 4 cache misses where a forest may cause one. The effect needs texts much larger than the last-level cache.

## Compared with alternatives

Pick it only to study or reproduce the wavelet-forest locality idea; for a usable fast wavelet structure, QWT (C++ quad-wavelet-tree or Rust qwt) has numbers about 2x over SDSL and full access/rank/select, and faster-minuter's wt_fbb is the maintained fixed-block-boosting wavelet tree with the same block-partitioning idea.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | sdsl-lite (fetched at HEAD via FetchContent), libdivsufsort 2.0.1, malloc_count v0.7.1, CLI11 v1.9.0 (included but unused), optional OpenMP |
| **Minimum toolchain** | C++17, CMake 3.22 (README says g++ 12+) |
| **Platforms** | not documented; Linux and macOS OpenMP paths in CMakeLists.txt |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | partial — the forest is a std::vector of sdsl::wt_huff, so per-block access uses the SDSL API, but global positions must be split by the caller and no global rank/select is provided |

## Gotchas

- The build is broken as checked in: the root CMakeLists.txt calls add_executable(wavelet_forest main.cpp) and likewise for randomFileGenerator.cpp and wavelet_engine.cpp, but those files live in src/ and there is no src/CMakeLists.txt, so configuration should fail on missing sources. The README's bin/gen_text, build_wt, build_wf and bench_access tools and CSV output do not exist.
- Inconsistent block size: wavelet_engine.cpp builds the forest with 1 MiB (1,048,576-symbol) blocks while main.cpp looks it up with block_size = 10,000,000, so forest[idx / 10000000][idx % 10000000] indexes past the end of a 1 MiB block (undefined behaviour, wrong answers) unless the user edits one of them.
- Off-by-one in the query generator: std::uniform_int_distribution&lt;size_t&gt;(0, size) is inclusive, so a query can hit position wt.size(), one past the end. Queries are seeded from std::random_device, so runs are not repeatable.
- Unfair timing in main.cpp: the wavelet-tree loop discards wt[i] (the compiler may drop the work), while the forest loop prints every result to std::cout inside the timed region; only 10,000 queries, one run, and no build type or -O flags set in CMakeLists.txt.

## Known shortcomings

- Downgraded B to D: no numbers; the SPIRE 2024 paper (arXiv 2308.07809) is blocked. The README describes tools that do not exist in the repo (gen_text, build_wf, bench_access); src/main.cpp's timing is flawed (the WT loop discards its result, the WF loop prints to stdout inside the timed region); the README says 'permissive' but the license is GPL-3.0. Last commit 2025-08-29, stale.
- Build is broken (root CMakeLists lists main.cpp etc. while the files sit in src/ with no src/CMakeLists.txt). Block-size mismatch: the builder uses 1 MiB blocks while the timer indexes with 10,000,000, out-of-bounds UB. Off-by-one: uniform_int_distribution(0, size) can return wt.size(). random_device seed, not repeatable. Unfair timing (WT result discarded, WF prints inside the timed loop). Access only, no rank/select. GPL-3.0 although the README says permissive. Paper (arXiv 2604.11338) blocked here.

## Caveats and trade-offs

No numbers in the repo; the claim rests on the SPIRE 2024 paper 'Another Virtue of Wavelet Forests' (arXiv 2308.07809), which was not opened. The README describes a benchmark harness (gen_text, build_wt, build_wf, bench_access, CSV output, a block-size sweep) that does not exist in the repo. The actual timing code, src/main.cpp, has hard-coded placeholder file paths and a fixed 10 MB block; its wavelet-tree loop discards the result of wt[i] (the compiler may remove it), while the forest loop prints every character to stdout inside the timed region, so the two timings are not comparable. The README calls the license permissive, but the LICENSE file is GPL-3.0 and the source headers say 'Copyright (c) Boucher Lab. All rights reserved. Licensed under the GNU license'. Research-grade code, 1 star.

Gain comes from cache locality of per-block trees; the README tests uncompressed bitvectors only, so space behavior with compressed bitvectors is not shown. Per-block alphabets and metadata add overhead. Targets access, with rank 'often'.

## Maintenance

Stale (last commit 2025-08-29, 1 star, 0 issues), GPL-3.0 research code that does not build as checked in; treat it as a paper companion, not a dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification B, tier now D.
- **Tier reason:** The README compares the wavelet forest with SDSL's Huffman-shaped wavelet tree, but it gives only qualitative observations and no numbers, and the SPIRE 2024 paper (Springer; arXiv 2308.07809) is blocked here. The README also describes tools (bin/gen_text, build_wt, build_wf, bench_access with CSV output) that are not in the repo; src/ holds only main.cpp, randomFileGenerator.cpp and wavelet_engine.cpp.
- **Verifier notes:** Downgraded to D: no numbers anywhere reachable, and the repo's timing harness is flawed (dead-result WT loop; stdout I/O inside the WF timed region) and does not match the README. Metadata confirmed: GPL-3.0, 1 star, 22 commits, last commit 2025-08-29 (stale, just over 12 months). baseline_in_list true is correct (simongog/sdsl-lite is listed).
- **Fields the verifier corrected:** `benchmark_url`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier; no numbers in repo
- **Pages the verifier opened:**
  - <https://github.com/AaronHong1024/wavelet_forest>
  - <https://github.com/AaronHong1024/wavelet_forest/commits>
  - <https://github.com/AaronHong1024/wavelet_forest/tree/master/src>
  - <https://raw.githubusercontent.com/AaronHong1024/wavelet_forest/HEAD/README.md>
  - <https://raw.githubusercontent.com/AaronHong1024/wavelet_forest/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/AaronHong1024/wavelet_forest/master/src/main.cpp>
  - <https://raw.githubusercontent.com/AaronHong1024/wavelet_forest/master/src/wavelet_engine.cpp>
  - <https://raw.githubusercontent.com/AaronHong1024/wavelet_forest/master/CMakeLists.txt>
- **Sources the enricher read:**
  - <https://github.com/AaronHong1024/wavelet_forest>
  - <https://github.com/AaronHong1024/wavelet_forest/tree/master/src>
  - <https://github.com/AaronHong1024/wavelet_forest/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/AaronHong1024/wavelet_forest/HEAD/README.md>
  - <https://raw.githubusercontent.com/AaronHong1024/wavelet_forest/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/AaronHong1024/wavelet_forest/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/AaronHong1024/wavelet_forest/HEAD/src/main.cpp>
  - <https://raw.githubusercontent.com/AaronHong1024/wavelet_forest/HEAD/src/wavelet_engine.cpp>
  - <https://raw.githubusercontent.com/AaronHong1024/wavelet_forest/HEAD/src/randomFileGenerator.cpp>
  - WebSearch: "Another Virtue of Wavelet Forests" (snippets of arXiv 2308.07809 only; also surfaced arXiv 2604.11338 'Wavelet Forests Revisited')
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/aaronhong1024/wavelet_forest`) · [data/wave9/enrich/raw/github_com_aaronhong1024_wavelet_forest.json](../../../data/wave9/enrich/raw/github_com_aaronhong1024_wavelet_forest.json) (enrichment confidence 0.75)

</details>
