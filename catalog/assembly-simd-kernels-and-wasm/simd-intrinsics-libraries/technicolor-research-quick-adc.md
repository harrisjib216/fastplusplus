# Quick ADC

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [SIMD intrinsics libraries](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `BSD-3-Clause-Clear` · 🔴 abandoned

> Research C++14 PQ search engine whose AVX2 scan uses 4-bit sub-quantizers and pshufb tables; about 3.8x faster scans than scalar ADC.

| | |
|---|---|
| **Beats** | ADC (asymmetric distance computation in product quantization, lookup tables in L1 cache; the authors' scalar implementation) |
| **Claimed result** | README: 'Quick ADC achieves 4-6x better performance than ADC by storing lookup tables in SIMD registers'. The README example on SIFT1M with an IVF index of 256 cells and ma=24 gives scan_us 86 for db_query_4 (16x4 OPQ, Recall@100 0.9426) vs 323 for db_query ADC (8x8 OPQ, Recall@100 0.9646), about 3.8x (derived from page data). Paper abstract (arXiv 1704.07355): a 3 to 6 times speedup over ADC (search snippet only). |
| **Workload** | Nearest-neighbour search over product-quantized codes using 4-bit quantizers so lookup tables fit SIMD registers (AVX/AVX2 scan_avx_4), batches of 32 queries, with inverted-index support. |
| **Metric** | throughput |
| **Hardware** | Tested on Intel Haswell, Broadwell and Skylake processors (README); exact CPU model for the speedup chart not stated |
| **Compiler and flags** | g++ 5.4 or newer; CMakeLists.txt: -std=c++14 -g -O3 -m64 -march=native -ffast-math -fopenmp -Wall -Werror; sequential (single-threaded) BLAS, OpenCV core, Cereal 1.2.2 |
| **Adoption** | 27 stars; ICMR 2017 paper |
| **Last commit** | 2019-05-31 |
| **Links** | [repository](https://github.com/technicolor-research/quick-adc) · [benchmark](https://raw.githubusercontent.com/technicolor-research/quick-adc/HEAD/README.md) |

## Verdict

README example on SIFT1M with an IVF index of 256 cells, 24 cells probed and r = 100: the authors' scalar ADC over 8x8 OPQ codes scans in 323 us per query (Recall@100 0.9646) versus 86 us for Quick ADC over 16x4 OPQ codes with keep 0.213% (Recall@100 0.9426), about 3.8x (derived from page data); the README states 4-6x and the ICMR 2017 paper abstract 3-6x (snippet only). Built with g++ 5.4+ -O3 -march=native -ffast-math; tested on Haswell, Broadwell and Skylake, with no CPU model given for these numbers.

## Use it when

- IVF-ADC search with many small cells and multiple assignment (the README run probes 24 of 256 cells on SIFT1M), where PQ Fast Scan's per-partition grouping cannot be used.
- 64-bit (16x4) or 128-bit (32x4) codes on x86-64 with AVX2, when you accept a small recall loss for about 4x faster code scans.
- Recall@100-style workloads where the true neighbour only has to land somewhere in a 100-item candidate list that a later stage re-ranks.
- As a compact reference for the 4-bit pshufb fast-scan kernel that Faiss later productised.

## Skip it when

- When you need exact ADC distances or a precise top-1: results are ranked by 8-bit quantized sums with no float re-ranking pass in db_query_4, on top of the 4-bit quantizer loss (Recall@100 0.9426 vs 0.9646 for 8x8 OPQ in the README run).
- 8-bit codes or code sizes other than 16x4 and 32x4: get_simd_scan_func_epi8 exits on anything else.
- CPUs without AVX2 or non-x86 targets (config.h hard-defines AVX2; -march=native).
- Production deployments: three commits, abandoned since 2019, no library target or tests; Faiss IndexIVFPQFastScan (which credits the same authors' fast-scan work) is the maintained route.
- Inner-product or other metrics with negative table entries: negative entries are clamped to zero before quantization.

## How it is fast

With 16-centroid (4-bit) sub-quantizers every distance table has 16 entries, so after quantizing the float tables to int8 it fits one 128-bit register. Codes are transposed into 16-vector blocks; scan_avx_4 does two pshufb lookups per byte (low and high nibble) with saturating int8 adds, two sub-quantizer rows per 256-bit register, then compares the 16 sums against the int8 heap bound with a movemask and pushes only survivors. The quantization range comes from a scalar float scan of a small 'keep' fraction of each probed cell (0.213% in the README run), which sets qmax to the current top-r bound.

## Compared with alternatives

Pick it over its sibling PQ Fast Scan when the database is an IVF index with many small cells or you can use 4-bit codes; PQ Fast Scan returns exact 8x8-bit ADC results but only pays off on large, re-laid-out partitions. No other catalogued SIMD library targets PQ distance scans.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | sequential (single-threaded) BLAS such as OpenBLAS 0.2.19 built by getdeps.sh, OpenCV core, Cereal 1.2.2; codebooks must be learned with an external tool (arbabenko/Quantizations) and converted by convert-quantizer.py |
| **Minimum toolchain** | C++14, g++ 5.4 or newer, CMake 3.2 (CMakeLists) although the README says 2.8; -O3 -march=native -ffast-math -fopenmp -Werror |
| **Platforms** | x86-64 Linux with AVX and AVX2 (tested on Intel Haswell, Broadwell and Skylake per README) |
| **Thread safety** | not documented; each nns_engine owns its table, residual and assignment buffers and query_scan clamps the caller's tables in place, so use one engine per thread; OpenMP is used only when building databases |
| **Drop-in for the baseline** | partial: same IVF structure and code size as ADC, but it needs 4-bit codebooks, a re-laid-out copy of each cell and a tuned keep parameter, and returns int8-quantized distances |

## Gotchas

- The keep fraction must give at least r scalar-scanned codes across the probed cells, otherwise qmax stays at FLT_MAX and db_query_4 exits with 'Max quantization bound too high. Try larger keep value.'; the README recommends keep between 0.05% and 1%, and -k is given in percent.
- Tail handling in scan_avx_4: the last block of each cell is padded with copies of the cell's last code and padded lanes are not masked; bh_push clamps their index to the last code, so that code can enter the top-r list up to 16 times, displacing real candidates (minor effect on recall, none on timing).
- The README comparison changes two variables at once: ADC scans 8x8 OPQ codes while Quick ADC scans 16x4 OPQ codes (same 64-bit size, lower recall). Both use batches of 32 queries; scan_us is averaged over the whole query set and includes Quick ADC's scalar keep pass and table quantization.
- Dataset, slide and poster links on assets.xion345.info no longer resolve (issue #1 reports broken links; the host did not resolve in this session).

## Known shortcomings

- ICMR 2017 abstract (3-6x) seen as a snippet only; the README example (86 vs 323 us, about 3.8x) compares 16x4 against 8x8 OPQ at lower recall (0.9426 vs 0.9646), not like for like; own baseline, no CPU model.
- Ranks by int8 quantized sums with no float re-rank; the README 3.8x compares 8x8 vs 16x4 OPQ codes under the lenient Recall@100 (t = 1). Tail bug: padded lanes in each cell's last block are unmasked and clamped to the last code's label, so that code can fill up to 16 heap slots (timing unaffected, small recall effect); a keep too small exits with 'Max quantization bound too high'. No CPU model; the paper remains closed.

## Caveats and trade-offs

Tier B rests on the peer-reviewed ICMR 2017 paper cited in the README; the paper (ACM and arXiv) could not be opened here, so the figures come from the README and a search snippet (the abstract says 3-6x, the README 4-6x). The README example compares different quantizers (16x4 OPQ for Quick ADC vs 8x8 OPQ for ADC) at lower recall (0.9426 vs 0.9646), and Quick ADC scans a 'keep' fraction of codes without SIMD first, so the 3.8x example is not like for like. 4-bit quantizers cost some accuracy (the README calls it slight and often negligible). The baseline ADC is the authors' own scalar implementation. Tested on Intel Haswell, Broadwell and Skylake, but no CPU model is given for the published numbers. Builds use -march=native -ffast-math. Clear BSD has no patent grant and is not OSI-listed (permissive, treated as copyable).

Needs AVX2 (Haswell or newer); 4-bit quantizers cause 'a slight decrease in accuracy' (README says often negligible); builds on the same idea as PQ Fast Scan.

## Maintenance

Abandoned since 2019-05-31 (3 commits, 27 stars) but Clear-BSD-licensed research code with a self-contained AVX2 kernel; the authors' later Quicker ADC (technicolor-research/faiss-quickeradc, AVX-512, non-4-bit codes) and Faiss's FastScan indexes supersede it.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification B, tier now B.
- **Tier reason:** The README claims 4-6x over the scalar ADC reference, shows one example run (scan 86 us vs 323 us) and cites the peer-reviewed ICMR 2017 paper. The paper (arXiv 1704.07355, ACM) could not be opened here; its abstract says 3 to 6 times (search snippet only). No CPU model is given for the numbers, so the record stays below A.
- **Verifier notes:** The README matches the 4-6x claim. The reachable example gives about 3.8x (derived) at lower recall with a different quantizer, and the paper abstract says 3-6x (snippet only). Shortcomings to record: not like for like (16x4 vs 8x8 codes, lower recall), the authors' own baseline, no CPU model, and the paper not opened. 27 stars, 3 commits, last commit 2019-05-31 (abandoned). Sibling of PQ Fast Scan (same authors, different technique), not a duplicate.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-109 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/technicolor-research/quick-adc/HEAD/README.md>
  - <https://raw.githubusercontent.com/technicolor-research/quick-adc/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/technicolor-research/quick-adc/HEAD/CMakeLists.txt>
  - <https://github.com/technicolor-research/quick-adc>
  - <https://github.com/technicolor-research/quick-adc/commits>
- **Sources the enricher read:**
  - <https://github.com/technicolor-research/quick-adc>
  - <https://raw.githubusercontent.com/technicolor-research/quick-adc/HEAD/README.md>
  - <https://raw.githubusercontent.com/technicolor-research/quick-adc/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/technicolor-research/quick-adc/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/technicolor-research/quick-adc/master/db_query_4.cpp>
  - <https://raw.githubusercontent.com/technicolor-research/quick-adc/master/db_query.cpp>
  - <https://raw.githubusercontent.com/technicolor-research/quick-adc/master/query_common.hpp>
  - <https://raw.githubusercontent.com/technicolor-research/quick-adc/master/simd_scan.hpp>
  - <https://raw.githubusercontent.com/technicolor-research/quick-adc/master/simd_layout.hpp>
  - <https://raw.githubusercontent.com/technicolor-research/quick-adc/master/binheap.hpp>
  - <https://raw.githubusercontent.com/technicolor-research/quick-adc/master/recall.hpp>
  - <https://raw.githubusercontent.com/technicolor-research/quick-adc/master/common.hpp>
  - <https://raw.githubusercontent.com/technicolor-research/quick-adc/master/config.h>
  - <https://raw.githubusercontent.com/technicolor-research/quick-adc/master/LibsPath.cmake>
  - <https://raw.githubusercontent.com/technicolor-research/quick-adc/master/getdeps.sh>
  - <https://raw.githubusercontent.com/technicolor-research/quick-adc/master/databases.cpp>
  - <https://github.com/technicolor-research/quick-adc/issues?q=is%3Aissue>
  - <https://github.com/technicolor-research/pq-fast-scan>
  - https://github.com/facebookresearch/faiss/wiki/Fast-accumulation-of-PQ-and-AQ-codes-(FastScan)
  - <https://github.com/nlescoua/faiss-quickeradc>
  - WebSearch snippets for arXiv 1704.07355 (Quick ADC) and arXiv 1812.09162 (Quicker ADC, TPAMI 2021); arXiv itself blocked
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/technicolor-research/quick-adc`) · [data/wave13/enrich/raw/github_com_technicolor_research_quick_adc.json](../../../data/wave13/enrich/raw/github_com_technicolor_research_quick_adc.json) (enrichment confidence 0.8)

</details>
