# Quicker ADC (faiss-quickeradc)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [SIMD intrinsics libraries](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Study only · `C++` · `BSD-3-Clause-Clear` · 🔴 abandoned

> 2018 FAISS fork that scans PQ codes with quantized in-register lookup tables; about 4-5x faster than FAISS PQ ADC at equal recall.

| | |
|---|---|
| **Beats** | FAISS PQ ADC (IndexPQ-style m x 8 float lookup-table scan, FAISS as of mid-2018) and polysemous codes |
| **Claimed result** | Numbers read from the README table image img/exhaustive_search_sift1M.png (query time per query in ms): 64-bit codes: FAISS PQ m x 8 5.50 ms (R@1 0.227, R@100 0.918); polysemous 1.19 ms (0.225 / 0.854); Quicker ADC m x {8,8} AVX512 BW 1.18 ms (0.223 / 0.918), i.e. about 4.7x faster than FAISS PQ at equal R@100 (derived from page data); m x {6,6,4} AVX512 BW 0.56 ms (0.179 / 0.859, about 9.8x faster at lower recall); m x {4,4} AVX512 BW 0.58 ms (0.158 / 0.807, about 9.5x). 128-bit codes: FAISS PQ 9.51 ms (0.446 / 0.998); polysemous 2.90 ms (0.447 / 0.987); Quicker ADC m x {8,8} AVX512 BW 2.36 ms (0.446 / 0.997, about 4.0x); m x {6,6,4} 0.99 ms (0.371 / 0.984, about 9.6x); m x {4,4} AVX512 BW 0.80 ms (0.313 / 0.964, about 11.9x). Against polysemous codes the margin is small: at 64 bits m x {8,8} ties polysemous on time (1.18 vs 1.19 ms) with higher R@100 (0.918 vs 0.854), and m x {6,6,4} is about 2.1x faster at equal R@100 (0.859 vs 0.854); at 128 bits m x {8,8} is about 1.2x faster (2.36 vs 2.90 ms) (all derived from page data). The non-exhaustive SIFT1000M and Deep1B figures are curves with no printed numbers. |
| **Workload** | Exhaustive nearest-neighbour search on SIFT1M with 64-bit and 128-bit product-quantization codes: per-query time (ms) with R@1 and R@100; non-exhaustive IVF, Inverted Multi-Index and HNSW-IVF search on SIFT1000M and Deep1B as recall-vs-query-time curves. |
| **Metric** | latency |
| **Hardware** | README says 'AWS m5 instances' for the SIFT1000M and Deep1B plots; no CPU model for the SIFT1M exhaustive table (AVX512 BW needs a Skylake-SP class or newer CPU). |
| **Compiler and flags** | Not stated; ./configure detects the CPU and enables SSE, AVX2 or AVX512 accordingly. Benchmarks run through benchs/bench_vpq_sift1000m.py and benchs/bench_vpq_1bn.py at code commit d11c5af. |
| **Adoption** | 62 stars, 5 forks; fork of FAISS (179 commits); successor of the already-listed Quick ADC (technicolor-research/quick-adc) |
| **Last commit** | 2019-01-03 |
| **Links** | [repository](https://github.com/technicolor-research/faiss-quickeradc) · [benchmark](https://github.com/technicolor-research/faiss-quickeradc) |

## Verdict

The paper's SIFT1M exhaustive-search table (README image; single-threaded per the committed scripts; AVX-512 BW CPU, model and compiler unstated) shows m x {8,8} AVX-512 at 1.18 ms per query vs 5.50 ms for mid-2018 FAISS PQ ADC with 64-bit codes at equal R@100 (0.918), and 2.36 vs 9.51 ms with 128-bit codes (about 4-5x, derived from page data); the 9.5-12x rows use lower-recall {6,6,4} or {4,4} layouts, and against polysemous codes the gain ranges from a tie to about 2x.

## Use it when

- Reproducing or extending the Quicker ADC paper (arXiv 1812.09162, IEEE TPAMI) on x86-64 with AVX-512 BW.
- Billion-scale IVF, Inverted Multi-Index or HNSW-IVF search with 64-bit or 128-bit PQ codes where per-query scan time dominates and the {8,8} layout keeps PQ-level recall.
- Latency-bound single-thread exhaustive PQ scans over about 1M codes where about 1.2 ms per query (vs 5.5 ms for 2018 FAISS PQ at 64 bits) matters.
- As a source of the {6,6,4} and {8,8} AVX-512 scan kernels to port into a current ANN library.

## Skip it when

- New projects on current FAISS: upstream now ships IndexPQFastScan and IndexIVFPQFastScan (4-bit codes with 8-bit tables in registers, credited to Andre et al.), maintained and with AVX2 support (FAISS wiki and API docs, seen as search snippets only).
- Inner-product or cosine search: only L2 is implemented.
- Non-x86 or pre-AVX2 hardware: the build always adds -mf16c and the kernels use x86 intrinsics; without AVX-512 the fast {6,6,4} and {8,8} variants fall back to scalar code.
- When you need exact PQ distances or the best recall from the faster layouts: {4,4} and {6,6,4} lose recall versus 8-bit PQ (64-bit codes: R@100 0.807 and 0.859 vs 0.918).
- Production use needing maintenance or a patent licence: abandoned since 2019-01-03, Python 2 benchmark scripts, Clear BSD code with no patent grant on top of FAISS's old BSD+PATENTS terms.

## How it is fast

Per query it computes the float distance tables, scans the first 4k codes with them to seed the top-k heap, then quantizes the tables to 8-bit (4-bit sub-codes) or 16-bit entries between the per-subquantizer minimum and the current k-th distance. Codes are stored in transposed groups so one shuffle looks up many codes at once: pshufb (_mm_shuffle_epi8 / _mm256_shuffle_epi8) for 16-entry tables and AVX-512 BW 16-bit permutes (_mm512_permutexvar_epi16, _mm512_permutex2var_epi16 with mask blends) for the 6-bit and 8-bit sub-codes of the irregular quantizers. Saturating adds accumulate the distances, a SIMD compare against the quantized heap bound plus movemask selects the few candidates that touch the heap.

## Compared with alternatives

Pick it over Quick ADC (the standalone 4-bit SSE predecessor) or PQ Fast Scan when you want the work inside FAISS with IVF, IMI and HNSW-IVF indexes and the AVX-512 {6,6,4} or {8,8} layouts that keep 8-bit-PQ recall; bolt targets learned encoders against Eigen matmul, a different trade-off.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | BLAS, LAPACK, OpenMP, Boost (Boost.Align aligned_allocator); SWIG, numpy and Python 2 for the Python interface and benchmark scripts |
| **Minimum toolchain** | C++11 (configure.ac requires it), autoconf ./configure; built and benchmarked with 2018-era compilers, newer toolchains not documented |
| **Platforms** | x86-64 only: AVX2 for the 4-bit AVX2 variants, AVX-512 BW for the {4,4} AVX-512, {6,6,4}, {6,5,5}, {5,5,5} and {8,8} variants; the {8} AVX-512 VBMI variant was never timed |
| **Thread safety** | Same model as 2018 FAISS: search is const and OpenMP-parallel over queries (#pragma omp parallel for); concurrent add during search is not documented |
| **Drop-in for the baseline** | partial — same FAISS Index train/add/search API as IndexPQ and IndexIVFPQ, but only inside this fork, with new class or factory names, L2 only and approximate (dequantized) result distances |

## Gotchas

- Result distances are dequantized 8-bit or 16-bit sums (heap entries come from unquantize_sum), with no float re-ranking, so ties and near-ties can order differently from FAISS PQ.
- The AVX-512 classes are wrapped in #ifdef __AVX512F__ and otherwise silently alias the scalar NoVec/NoVecTable classes under the same names, so a build on a machine without AVX-512 runs the slow path without warning.
- Reproducibility gap: the committed benchs/bench_vpq_sift1m.py (identical at the pinned commit d11c5af and at HEAD) evaluates neither the {8,8} AVX-512 variants (2vc/4vc) nor the 64-bit {4,4} AVX-512 one (2W4 is commented out), and benchs/bench_polysemous_sift1m.py runs only the 128-bit IndexPQ(d,16,8) with k=1 and reports R@1, so the headline {8,8} rows, the 64-bit FAISS PQ row and every baseline R@100 value come from runs not in the repo. The README's reproduce command names benchs/bench_vpq_sift1000m.py, which does not exist (404), with 'pyton' and PYTHON_PATH typos. Timing is one time.time() pair around a single 10,000-query batch, single-threaded on both sides, no warm-up or repeats.
- The signed VecProductQuantizer_4_AVX256 class shown in the README sums its two lanes with an unsigned saturating add (_mm_adds_epu8) and then a signed compare (_mm_cmplt_epi8), so far codes whose lane sums exceed 127 wrap negative and would enter the heap with a too-small distance; it is not registered in VPQ_Impl.h (the _AVX2 names map to the _unsigned classes), so the published numbers are unaffected, but do not instantiate it directly.

## Known shortcomings

- Raised from C to B: the README table image is the TPAMI 2021 paper's own table (venue confirmed by snippet only, paper text unopened). The baseline is mid-2018 FAISS, the about 10x gains appear only at lower recall, and against polysemous codes it is a tie to about 2x; no CPU model or compiler. Clear BSD licence with no patent grant; abandoned since 2019. Related to the listed Quick ADC but a separate project.
- Enricher: the committed bench_vpq_sift1m.py (identical at d11c5af and HEAD) runs neither the {8,8} AVX-512 variants nor the 64-bit {4,4} AVX-512 variant, and bench_polysemous_sift1m.py runs only 128-bit IndexPQ at R@1, so the headline {8,8} rows, the 64-bit FAISS PQ row and all baseline R@100 values come from runs not in the repo; the README's reproduce command names a file that returns 404. Timing is one time.time() around one 10k-query batch; results are dequantised distances with no float re-rank; AVX-512 classes silently fall back to scalar without __AVX512F__. Likely bug in an unregistered class: signed VecProductQuantizer_4_AVX256 adds with _mm_adds_epu8 then compares with _mm_cmplt_epi8, so lane sums over 127 wrap negative (published numbers unaffected).

## Caveats and trade-offs

Peer-reviewed (IEEE TPAMI, May 2021, DOI 10.1109/TPAMI.2019.2952606; arXiv 1812.09162), but the venue was confirmed only from search snippets because arXiv, doi.org, IEEE and EPFL Infoscience are blocked here; the README table comes from the technical report built on code commit d11c5af and the TPAMI text was not opened. No CPU model or compiler for the SIFT1M exhaustive table (the footnote says then-current processors lacked AVX512 VBMI, so a Skylake-SP class machine is implied; the SIFT1000M and Deep1B plots say only 'AWS m5 instances'). The FAISS baseline is the mid-2018 FAISS this fork branched from, and later FAISS releases added their own 4-bit fast-scan PQ path (not checked this session), so the baseline is dated. At equal recall (m x {8,8}) the gain over FAISS PQ is about 4x to 5x; the 10x figures are at lower recall, and against polysemous codes the gain is between a tie and about 2x. The 'Sequential' float rows in the same table (for example 25.8 ms for m x {4,4}) are the authors' own scalar versions, not a competitor. The m x {8} AVX512 VBMI row has no timing (hardware unavailable) and its 'up to 4 times' is a projection. Licence is mixed: Thomson Licensing's Quicker ADC changes are Clear BSD (not OSI-approved; explicitly no patent licence) on top of Facebook's BSD-3-Clause plus the inherited PATENTS file (Facebook Additional Grant of Patent Rights Version 2, which terminates on patent assertion against Facebook). Not a duplicate of Quick ADC: this repo is the later FAISS integration with AVX-512, irregular product quantizers and a separate paper. Abandoned since 2019-01-03. [retier] Enricher: the committed benchmark scripts run neither the {8,8} AVX-512 variants nor the 64-bit {4,4} AVX-512 variant, so the headline rows and baseline R@100 values come from runs not in the repo; one timed 10k-query batch; dequantised distances without re-rank; AVX-512 classes fall back to scalar silently.

L2 distance only; AVX512 BW needed for the fastest m x {8,8} and 6-bit variants, AVX2 and SSE variants exist; m x {8} VBMI timings could not be measured because no processor supported it at the time. Faster variants pay in recall (m x {4,4} loses about 0.07 R@1 and 0.11 R@100 vs PQ at 64 bits). Heavy template instantiation increases compile time. No OnDiskInvertedList support.

## Maintenance

Abandoned since 2019-01-03 on a mid-2018 FAISS base with Python 2 scripts and a Clear BSD licence without patent grant, so treat it as a reference implementation of the paper's kernels rather than a library to deploy; upstream FAISS fast-scan covers the 4-bit case.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now B.
- **Tier reason:** The README image img/exhaustive_search_sift1M.png is the paper's own table (citation markers, 'Section 3.2' footnote) and shows every claimed time against FAISS PQ ADC m x 8 and polysemous codes; the paper was published in IEEE TPAMI (May 2021, DOI 10.1109/TPAMI.2019.2952606, confirmed by search snippets only), so it is a peer-reviewed measurement; no CPU model, compiler or flags for the SIFT1M table, so not A. Upgraded from C on the peer-review evidence.
- **Verifier notes:** All table numbers verified from the README image; tier raised C to B on TPAMI publication (snippet-confirmed, paper text not opened). Shortcomings: dated mid-2018 FAISS baseline, 10x gains only at lower recall, small margin over polysemous codes, no CPU/compiler, Clear BSD core without patent grant, abandoned 2019. Related to the already-listed Quick ADC but a distinct project.
- **Fields the verifier corrected:** `claimed_speedup`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-127 (wave 13 seed pass, 2026-10-13); enricher (seed pass, 2026-10-13)
- **Pages the verifier opened:**
  - <https://github.com/technicolor-research/faiss-quickeradc>
  - <https://github.com/technicolor-research/faiss-quickeradc/commits>
  - <https://raw.githubusercontent.com/technicolor-research/faiss-quickeradc/HEAD/README.md>
  - <https://raw.githubusercontent.com/technicolor-research/faiss-quickeradc/HEAD/img/exhaustive_search_sift1M.png>
  - <https://raw.githubusercontent.com/technicolor-research/faiss-quickeradc/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/technicolor-research/faiss-quickeradc/HEAD/PATENTS>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/technicolor-research/faiss-quickeradc/HEAD/README.md>
  - <https://raw.githubusercontent.com/technicolor-research/faiss-quickeradc/HEAD/benchs/bench_vpq_sift1m.py>
  - <https://raw.githubusercontent.com/technicolor-research/faiss-quickeradc/HEAD/benchs/bench_vpq_sift1000m.py>
  - <https://raw.githubusercontent.com/technicolor-research/faiss-quickeradc/d11c5af/benchs/bench_vpq_sift1m.py>
  - <https://raw.githubusercontent.com/technicolor-research/faiss-quickeradc/HEAD/benchs/bench_polysemous_sift1m.py>
  - <https://raw.githubusercontent.com/technicolor-research/faiss-quickeradc/HEAD/VecProductQuantizer.h>
  - <https://raw.githubusercontent.com/technicolor-research/faiss-quickeradc/HEAD/VPQ_Impl.h>
  - <https://raw.githubusercontent.com/technicolor-research/faiss-quickeradc/HEAD/configure.ac>
  - <https://raw.githubusercontent.com/technicolor-research/faiss-quickeradc/HEAD/makefile.inc.in>
  - <https://github.com/technicolor-research/faiss-quickeradc/issues>
  - https://github.com/facebookresearch/faiss/wiki/Implementation-notes/Getting-started (search snippet only)
  - https://faiss.ai/cpp_api/struct/structfaiss_1_1IndexPQFastScan.html (search snippet only)
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/technicolor-research/faiss-quickeradc`) · [data/wave13/enrich/raw/github_com_technicolor_research_faiss_quickeradc.json](../../../data/wave13/enrich/raw/github_com_technicolor_research_faiss_quickeradc.json) (enrichment confidence 0.75)

</details>
