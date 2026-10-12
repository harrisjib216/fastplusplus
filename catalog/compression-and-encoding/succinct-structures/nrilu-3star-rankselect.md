# 3star-rankselect (3\* rank/select)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Succinct data structures](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MPL-2.0` · 🟢 active

> Research rank/select bit vector with worst-case constant-time select at about 0.8 percent space overhead, far below SDSL, sux and pasta.

| | |
|---|---|
| **Beats** | SDSL (sd_vector, mcl select), sux (rank9sel, simple_select), pasta flat rank/select, Poppy (benchmark script options) |
| **Claimed result** | Space: paper abstract (search snippet) reports 0.78 percent overhead, 4.5x to 64.1x less than previous implementations. Checked-in logs (1e9 bits, density 0.5, 2e7 random select_1 queries, i9-13900H): m3 overhead 0.82 percent vs simple_s1 2.34, pasta flat 3.58, simple_s3 7.03, sdsl_mcl 23.63, rank9sel 56.25, sdsl_sd 78.15 percent (2.9x to 95x less overhead, derived from page data). Query time is not a win: m3 100.4 ns vs simple_s1 100.2, rank9sel 100.3, sdsl_mcl 80.9, simple_s3 49.1 ns in the same run; a second run gives m3 95 to 96 ns (0.82 percent config) or 77 to 79 ns (3.2 percent config) vs 76 to 185 ns for competitors depending on density. |
| **Workload** | Rank and select on plain bit vectors with worst-case constant query time; repo script benchmarks select_1 query time (ns) and space overhead percent against competitor code it downloads. |
| **Metric** | memory |
| **Hardware** | 13th Gen Intel Core i9-13900H (from checked-in log lines) |
| **Compiler and flags** | Clang 18.1.3, -O3 -march=native -DNDEBUG (CMakeLists.txt and log RESULT lines) |
| **Adoption** | 5 stars |
| **Last commit** | 2026-09-15 |
| **Links** | [repository](https://github.com/nrilu/3star-rankselect) · [benchmark](https://github.com/nrilu/3star-rankselect/tree/main/multibench_out) |

## Verdict

Checked-in multibench_out logs (1e9 random bits at densities 0.5, 0.2 and 0.02, 2e7 dependent random select_1 queries, one run each, Clang 18.1.3 -O3 -march=native -DNDEBUG, Intel Core i9-13900H) show m3 at 0.82 percent overhead and 95-96 ns per select, against pasta flat 3.58 percent, sux simple_select s1 2.34 percent, SDSL mcl about 23 percent and rank9sel about 50-56 percent, at 76-185 ns for those competitors; the space win (about 2.9x to 95x less overhead, derived from page data) is the result, not speed. The paper's 0.78 percent and 4.5x to 64.1x figures come from a search snippet of arXiv 2509.17819 (blocked here).

## Use it when

- Very large static bit vectors (around 1e9 bits and up) where the rank/select index must stay under 1 percent of the bits, e.g. succinct trees, FM-index or wavelet-tree building blocks under tight memory.
- Workloads that need worst-case constant select time, including adversarial or very uneven densities where sampling-based select (sux simple_select, SDSL mcl) can degrade.
- x86-64 machines with AVX2 and BMI2 (Haswell or Zen 2 and later) built with -march=native.
- As a reference design for engineering your own low-overhead select: the code exposes many compile-time variants (L0 size 512/1024/2048, tree strategies, prefetch and huge-page switches).

## Skip it when

- When select latency matters more than space: in the repo's own runs at 0.82 percent overhead select_1 took about 95-100 ns; at density 0.5 that is level with sux rank9sel (88 ns) and simple_select s1 (91 ns) and slower than SDSL mcl (about 81-85 ns) and simple_select s3 (about 49 ns at 7 percent overhead). It only pulls ahead at density 0.02, where pasta flat (144 ns) and SDSL mcl (185 ns) slow down.
- If you need select_0 or access: m3::select_0 and m3::access are stubs that return 0.
- Non-x86 targets (ARM, RISC-V) or x86 without AVX2/BMI2: the code includes x86intrin.h and uses _mm256_\*, _pdep_u64 and _lzcnt_u64 unconditionally.
- Dynamic bit vectors: the index is built once (build_auxiliaries) over a static input.
- If you want a packaged dependency: there is no install target, no tests beyond the driver's validate mode, 15 commits, 5 stars.

## How it is fast

It pairs a summary tree (per-superblock counters: 64 Ki-bit superblocks of 32 L0 blocks of 2048 bits, with 12-bit relative L0 counts unpacked with SSE/AVX2 shuffles and compared in SIMD) with a compressed three-level sample tree that stores positions of some 1-bits, which bounds select to a constant number of steps in the worst case. Blocks whose minority bits are rare are stored sparsely as 11-bit position lists and dense blocks verbatim, and the final in-word step uses PDEP/TZCNT. Prefetch hints and 2 MiB transparent huge pages (madvise) cut cache and TLB misses.

## Compared with alternatives

Pick it over SPIDER (about 3.8 percent overhead), orzo and pasta flat when the index size must be under 1 percent and you only need rank_1/select_1; pick SPIDER, QuadRank/BiRank or splatlab's PTSelect when query speed or throughput is the priority, and LA-vector or h0_bv when the bit vector itself should be compressed.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none for m3 itself beyond the repo's bv.hpp, alignedallocator.hpp, constants.hpp and Tree3.hpp; the benchmark driver also pulls vendored pasta and tlx and clones sdsl-lite, sux, rankselect and rankselect2 at HEAD |
| **Minimum toolchain** | C++20 (std::popcount, constexpr std::string), CMake 3.28; logs show Clang 18.1.3 |
| **Platforms** | x86-64 only, AVX2 + BMI2 + LZCNT required (built with -march=native); Linux (madvise MADV_HUGEPAGE via sys/mman.h) |
| **Thread safety** | not documented; queries are const member functions but the class reads process-wide globals, so one structure per process in practice |
| **Drop-in for the baseline** | partial — same rank_1/select_1 semantics as SDSL or sux, but different interface, input taken from global vectors, and no select_0/access |

## Gotchas

- m3::access(i) and m3::select_0(k) are unimplemented and silently return 0; calling them gives wrong answers rather than an error.
- Input is not passed in: m3 builds from the globals bits / N_bits / N_words (declared extern in bv.hpp, defined in bv.cpp), so extracting it into another project means rewiring those globals or editing the class.
- Macro typo in m3::rank_1: '#if REVERSE==2 && POP==2 && CUSTOM_LO != 512' tests CUSTOM_LO (letter O), which is undefined and evaluates to 0, so the intended exclusion for 512-bit L0 blocks never applies; it affects rank_1 only with CUSTOM_L0=512 (the 3.2 percent configuration) and was not exercised by the select-only checked-in runs. Run the driver's 'valid' job (compares every query against a naive structure) before trusting a non-default configuration.
- Benchmark caveats: single instance, single iteration per point, random uniform densities only (indep generator), FORCE_CRIT_PATH makes queries dependent (latency, not throughput), and competitors are cloned at their current heads, so reruns may not match the logs.

## Known shortcomings

- Raised C to A from the repo's multibench_out logs (i9-13900H, Clang 18.1.3, -O3 -march=native), but the win is space only (0.82% overhead vs 2.34-78.15%); select_1 is level or slower (m3 100.4 ns vs simple_s3 49.1 ns).
- m3::access and m3::select_0 are stubs returning 0. Input is read from globals (bits/N_bits/N_words), so not a drop-in library. Macro typo CUSTOM_LO != 512 in rank_1 (should be CUSTOM_L0), so the 512-bit-L0 exclusion never applies (checked-in select-only runs unaffected). x86-64 AVX2+BMI2+LZCNT only, C++20, CMake 3.28. Logs confirm 0.82% overhead at 95-96 ns, level with or slower than SDSL mcl/rank9sel/simple_select at density 0.5 and ahead only at 0.02. Single-run logs; competitors cloned unpinned.

## Caveats and trade-offs

Paper (arXiv 2509.17819, Kurpicz, Rigi-Luperti, Sanders) is blocked here; its 4.5x to 64.1x figure comes from a search snippet. The checked-in logs are single-instance, single-iteration example runs (the README calls the script an exemplary benchmark) and include one run tagged 'vb', apparently a virtual machine. The claim is about space overhead; at the 0.82 percent setting select_1 is level with rank9sel and simple_select s1 and about 2x slower than simple_select s3 and slower than SDSL mcl. Reproduction script clones competitor repos (sdsl-lite, sux, rankselect, rankselect2) at their heads, not pinned commits.

Targets minimal space overhead with worst-case constant-time queries; the README does not claim faster queries than pasta or SDSL, only 'good practical performance'.

## Maintenance

Active (README edited 2026-09-15, code last changed 2025-09-21), MPL-2.0 so files can be vendored with file-level copyleft; research code from the KIT group (Kurpicz, Rigi-Luperti, Sanders) that needs extraction work before use outside its benchmark driver.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded from C: the repo checks in benchmark logs (multibench_out/1758490314_vb_others_s1_n1_indep.txt and 1758490731_mypc_\*_indep.txt) produced by the public pybuild/run_bitvectors.py, each RESULT line naming CPU 13th Gen Intel Core i9-13900H, Clang 18.1.3, -O3 (OPTIMIZE=3) -march=native -DNDEBUG, and giving select_1 t(ns) and overhead_percent for m3 against sdsl_sd, sdsl_mcl, sux rank9sel and simple_select, and pasta flat. The space win holds there; the 4.5x to 64.1x headline comes only from the paper abstract (search snippet, arXiv blocked).
- **Verifier notes:** Found real numbers in the repo's multibench_out logs, so tier goes C to A for the space claim; speed is not faster. Metadata matches (MPL-2.0 per README/LICENSE.md, 5 stars, last commit 2026-09-15 README edit, code last changed 2025-09-21).
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** verifier; first-party logs
- **Pages the verifier opened:**
  - <https://github.com/nrilu/3star-rankselect>
  - <https://github.com/nrilu/3star-rankselect/commits>
  - <https://github.com/nrilu/3star-rankselect/tree/main/multibench_out>
  - <https://raw.githubusercontent.com/nrilu/3star-rankselect/HEAD/README.md>
  - <https://raw.githubusercontent.com/nrilu/3star-rankselect/HEAD/pybuild/run_bitvectors.py>
  - <https://raw.githubusercontent.com/nrilu/3star-rankselect/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/nrilu/3star-rankselect/HEAD/multibench_out/1758490314_vb_others_s1_n1_indep.txt>
  - <https://raw.githubusercontent.com/nrilu/3star-rankselect/HEAD/multibench_out/1758490731_mypc_others_s1_n1_indep.txt>
  - <https://raw.githubusercontent.com/nrilu/3star-rankselect/HEAD/multibench_out/1758490731_mypc_m3_s1_n1_indep.txt>
  - <https://raw.githubusercontent.com/nrilu/3star-rankselect/HEAD/multibench_out/1758492826_mypc_m3_s1_n1_indep.txt>
- **Sources the enricher read:**
  - <https://github.com/nrilu/3star-rankselect>
  - <https://raw.githubusercontent.com/nrilu/3star-rankselect/HEAD/README.md>
  - <https://raw.githubusercontent.com/nrilu/3star-rankselect/HEAD/LICENSE.md>
  - <https://raw.githubusercontent.com/nrilu/3star-rankselect/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/nrilu/3star-rankselect/HEAD/m3.hpp>
  - <https://raw.githubusercontent.com/nrilu/3star-rankselect/HEAD/Tree3.hpp>
  - <https://raw.githubusercontent.com/nrilu/3star-rankselect/HEAD/bv.hpp>
  - <https://raw.githubusercontent.com/nrilu/3star-rankselect/HEAD/bv.cpp>
  - <https://raw.githubusercontent.com/nrilu/3star-rankselect/HEAD/alignedallocator.hpp>
  - <https://raw.githubusercontent.com/nrilu/3star-rankselect/HEAD/constants.hpp>
  - <https://raw.githubusercontent.com/nrilu/3star-rankselect/HEAD/sampling.hpp>
  - <https://raw.githubusercontent.com/nrilu/3star-rankselect/HEAD/pybuild/run_bitvectors.py>
  - <https://raw.githubusercontent.com/nrilu/3star-rankselect/HEAD/multibench_out/1758490731_mypc_m3_s1_n1_indep.txt>
  - <https://raw.githubusercontent.com/nrilu/3star-rankselect/HEAD/multibench_out/1758490731_mypc_others_s1_n1_indep.txt>
  - WebSearch: "Theory Meets Practice for Bit Vectors Supporting Rank and Select" (abstract snippet of arXiv 2509.17819 only)
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/nrilu/3star-rankselect`) · [data/wave9/enrich/raw/github_com_nrilu_3star_rankselect.json](../../../data/wave9/enrich/raw/github_com_nrilu_3star_rankselect.json) (enrichment confidence 0.8)

</details>
