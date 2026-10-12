# quad-wavelet-tree (C++ QWT)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Succinct data structures](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Header-only C++20 4-ary (quad) wavelet matrix with about 2x lower access/rank/select latency than SDSL wavelet trees.

| | |
|---|---|
| **Beats** | SDSL wavelet trees/matrices |
| **Claimed result** | README: 'improve the latency of access, rank and select queries by factor of about 2 compared to other implementations of wavelet trees contained in ... SDSL'; no numbers on this page. The companion Rust README table, which labels Qwt256/Qwt512 as 'C++/Rust', gives SDSL 2.1.1 1178/1223/2900 ns vs Qwt256 584/613/1623 ns for access/rank/select on 4 GiB Big English. Paper abstract (search snippet only): up to 2x for access and select and up to 3x for rank vs SDSL. |
| **Workload** | Access, rank and select latency of a 4-ary wavelet matrix on text (details in the paper arXiv 2302.09239). |
| **Metric** | latency |
| **Hardware** | 8-core Intel i9-9900KF 3.60 GHz, 64 GiB RAM, Linux 5.19.0 |
| **Compiler and flags** | GCC 12.2.0 with -O3 -march=native -DNDEBUG -flto |
| **Adoption** | 11 stars |
| **Last commit** | 2023-02-21 |
| **Links** | [repository](https://github.com/MatteoCeregini/quad-wavelet-tree) · [benchmark](https://github.com/MatteoCeregini/quad-wavelet-tree) |

## Verdict

The C++ README states about 2x lower access/rank/select latency than SDSL wavelet trees on a single i9-9900KF thread (GCC 12.2.0, -O3 -march=native -DNDEBUG -flto) but shows no numbers. The companion Rust README's table (4 GiB Big English, 168 symbols, rows marked C++/Rust) gives Qwt256 584/613/1623 ns vs SDSL 2.1.1 1178/1223/2900 ns for access/rank/select. The peer-reviewed DCC 2024 paper reports up to 2x faster access/select and 3x faster rank (abstract via search snippet only). This repo's tests/test_qwm.cpp is a correctness test that times nothing and does not build SDSL.

## Use it when

- Large in-memory sequences (GiB-scale text, BWTs for FM-index backward search) over small or medium alphabets (bytes, up to 16-bit codes), where each query misses cache and latency per access/rank/select dominates.
- When you want SDSL-class wavelet matrix functionality at about 2x lower latency and less space than the SDSL 2.1.1 row (Rust companion table: 4616 vs 6089 MiB on 4 GiB English).
- C++20 code built with GCC or Clang on x86-64, where a small header-only drop of five files is acceptable.
- As a reference implementation to port: the code is short (qwm.hpp 220 lines, qvector.hpp 316 lines) and follows the published DCC paper.

## Skip it when

- If you need entropy-compressed (Huffman-shaped) wavelet trees or the rank-prediction variants: those (HQwt\*, \*Pfs) exist only in the Rust qwt crate, which is also the maintained implementation and the faster one in its own table.
- Sparse or huge alphabets: the alphabet must be dense [0, sigma], and precomputed_paths=true allocates 2 x (levels + 1) x (sigma + 1) 64-bit offsets.
- MSVC or non-GCC/Clang toolchains: counters use __uint128_t and __builtin_prefetch.
- Production code that needs a maintained library: this repo has had no code change since early 2023 and no releases, issue tracker activity or CI.
- Dynamic sequences: the structure is static; it is built once and has no insert, delete or update.

## How it is fast

Each level of the wavelet matrix consumes 2 bits of the symbol instead of 1, so a query visits ceil(log2(sigma)/2) levels: half the levels and about half the cache misses of a binary wavelet matrix. Each level is a 'quad vector' of 2-bit symbols whose rank inside a 64-bit word is a mask-and-popcount; per-symbol superblock (44-bit) and block (12-bit) counters are packed into one 64-byte-aligned 128-bit-per-symbol counter record and prefetched, so one rank costs about one counter-line miss plus one data-block miss. Select uses sampled superblock positions (every 8192 occurrences), then binary or sqrt-step linear search over counters and a broadword in-word select (the pasta-toolbox table). The optional precomputed_paths mode stores per-symbol level offsets so select skips the top-down pass.

## Compared with alternatives

Pick it over SDSL-based wavelet trees, wavelet_forest or faster-minuter when you are in C++ and want the lowest-latency uncompressed wavelet matrix in a small header-only drop; choose the Rust qwt sibling instead if you can use Rust or need Huffman compression or the prediction (Pfs) variants. pwm is a construction-speed tool, complementary rather than an alternative.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (C++ standard library only) |
| **Minimum toolchain** | C++20 (std::bit_width, std::popcount, &lt;bit&gt;); GCC or Clang for __uint128_t; README builds with GCC 12.2.0 and CMake 3.14+ |
| **Platforms** | x86-64 tested (i9-9900KF); portable C++20 otherwise, with no SIMD intrinsics; -march=native set in CMakeLists.txt |
| **Thread safety** | not documented; queries are const member functions with no mutable state, so concurrent reads after construction look safe (inferred from code) |
| **Drop-in for the baseline** | partial: it covers the access/rank/select functionality of SDSL's wavelet matrix but with a different class template, constructor and serialization API, and no namespace |

## Gotchas

- select.hpp defines the non-inline, non-template function select_uint64_t in a header, so including qvector.hpp or qwm.hpp from two translation units should cause a duplicate-symbol link error (inferred from code). Mark it inline when vendoring.
- No bounds or argument checks in release builds: rank, select and access preconditions are assert() only and the default flags include -DNDEBUG. select(r, v) needs 1 &lt;= r &lt;= rank(size, v), and select is 1-based while access and rank are 0-based.
- qvector.hpp calls std::sqrt without including &lt;cmath&gt;, and the classes (wavelet_matrix, qvector, counters) live in the global namespace, which can collide with other code.
- The constructor takes the input vector by value and counting-sorts a copy per level, so peak construction memory is several times the input size.

## Known shortcomings

- Downgraded A to B: the README says only 'about 2x' vs SDSL with no numbers and tests/test_qwm.cpp runs no SDSL; B rests on the DCC 2024 paper (snippet: up to 2x access/select, 3x rank). Abandoned (last commit 2023-02-21), 11 stars.
- tests/test_qwm.cpp checks correctness only and times nothing (no SDSL code). A non-inline select_uint64_t is defined in select.hpp, so including it from two translation units should give a duplicate-symbol link error (inferred); global namespace, std::sqrt without &lt;cmath&gt;, __uint128_t so GCC/Clang only. Commits span only 2023-01-26 to 2023-02-21. The Rust qwt (same group) has Huffman and Pfs variants this C++ port lacks; kept as the C++ entry, cross-reference rossanoventurini/qwt.

## Caveats and trade-offs

This C++ repo carries no result numbers and its benchmark (tests/test_qwm.cpp) does not run SDSL; the SDSL comparison harness is not public here. Flags (-O3 -march=native -DNDEBUG -flto) are confirmed in CMakeLists.txt. Paper (arXiv 2302.09239, DCC 2024) was not opened (arXiv blocked); its claims come from a search snippet. Last commit is a README edit from 2023-02-21; the Rust companion (rossanoventurini/qwt) is the maintained implementation. Latency measured with dependent queries.

C++ wavelet matrix with 4-ary tree and quad vectors; CMake build, test programs only (test_qvector, test_qwm), no installable library API seen. In the Rust companion table, Qwt256 uses less memory than SDSL (4616 vs 6089 MiB).

## Maintenance

Abandoned: all 24 commits are from 2023-01-26 to 2023-02-21, mostly README edits. It is MIT-licensed and header-only (five headers), so it is copyable, but the Rust crate rossanoventurini/qwt is where development continued.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification A, tier now B.
- **Tier reason:** The C++ README states the win over SDSL only as 'factor of about 2' with GCC 12.2.0, -O3 -march=native -DNDEBUG -flto and an i9-9900KF, but the repo's benchmark program (tests/test_qwm.cpp, built by CMakeLists.txt) times only the quad wavelet matrix and contains no SDSL code, so the baseline side is not reproducible from public code and A fails. The win is backed by the peer-reviewed paper (Ceregini, Kurpicz, Venturini, DCC 2024; extended in Software: Practice and Experience 2025), whose abstract (search snippet; arXiv blocked) reports up to 2x faster access/select and up to 3x faster rank than SDSL, so B.
- **Verifier notes:** Real and peer-reviewed, but the C++ repo itself has neither numbers nor baseline benchmark code; downgraded A to B on the paper. Consider folding into the Rust qwt entry as its C++ companion if the catalog prefers one record per project.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/MatteoCeregini/quad-wavelet-tree>
  - <https://github.com/MatteoCeregini/quad-wavelet-tree/commits>
  - <https://raw.githubusercontent.com/MatteoCeregini/quad-wavelet-tree/HEAD/README.md>
  - <https://raw.githubusercontent.com/MatteoCeregini/quad-wavelet-tree/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/MatteoCeregini/quad-wavelet-tree/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/MatteoCeregini/quad-wavelet-tree/HEAD/tests/test_qwm.cpp>
- **Sources the enricher read:**
  - <https://github.com/MatteoCeregini/quad-wavelet-tree>
  - <https://github.com/MatteoCeregini/quad-wavelet-tree/commits>
  - <https://github.com/MatteoCeregini/quad-wavelet-tree/tree/main/include>
  - <https://raw.githubusercontent.com/MatteoCeregini/quad-wavelet-tree/HEAD/README.md>
  - <https://raw.githubusercontent.com/MatteoCeregini/quad-wavelet-tree/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/MatteoCeregini/quad-wavelet-tree/HEAD/include/qwm.hpp>
  - <https://raw.githubusercontent.com/MatteoCeregini/quad-wavelet-tree/HEAD/include/qvector.hpp>
  - <https://raw.githubusercontent.com/MatteoCeregini/quad-wavelet-tree/HEAD/include/select.hpp>
  - <https://raw.githubusercontent.com/MatteoCeregini/quad-wavelet-tree/HEAD/include/essentials.hpp>
  - <https://raw.githubusercontent.com/MatteoCeregini/quad-wavelet-tree/HEAD/include/cache_aligned_allocator.hpp>
  - <https://raw.githubusercontent.com/MatteoCeregini/quad-wavelet-tree/HEAD/tests/test_qwm.cpp>
  - <https://raw.githubusercontent.com/MatteoCeregini/quad-wavelet-tree/HEAD/tests/create_dataset.cpp>
  - <https://raw.githubusercontent.com/rossanoventurini/qwt/HEAD/README.md>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/matteoceregini/quad-wavelet-tree`) · [data/wave9/enrich/raw/github_com_matteoceregini_quad_wavelet_tree.json](../../../data/wave9/enrich/raw/github_com_matteoceregini_quad_wavelet_tree.json) (enrichment confidence 0.75)

</details>
