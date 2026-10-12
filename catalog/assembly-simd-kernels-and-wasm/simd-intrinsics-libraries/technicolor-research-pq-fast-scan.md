# PQ Fast Scan

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [SIMD intrinsics libraries](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `BSD-3-Clause-Clear` · 🔴 abandoned

> Research C++ kernel for 8x8-bit product-quantization nearest-neighbour scans: keeps lookup tables in SSE registers, 4-6x faster than scalar PQ Scan.

| | |
|---|---|
| **Beats** | PQ Scan (product quantization distance scan with lookup tables in L1 cache; the project's own reference implementation, also with SSE, AVX and AVX gather variants) |
| **Claimed result** | README: 'PQ Fast Scan to perform 4-6x faster than PQ Scan, while returning the exact same results' (chart image not readable here). The README's sample pqfastscan output gives pq_us 75392 vs fast_pq_us 12272 (about 6.1x) and 74754 vs 17480 (about 4.3x) for two queries on a partition of 25,159,451 codes (derived from page data). PVLDB paper: 4-6x lower scan latency (search snippet only; the paper could not be opened). |
| **Workload** | Nearest-neighbour scan of 8x8-bit product-quantized codes (ANN_SIFT100M1 split into 8 partitions of about 25M codes, ANN_SIFT1B queries): the distance lookup tables are kept in SIMD registers instead of the L1 cache and the results are exactly the same as PQ Scan. |
| **Metric** | throughput |
| **Compiler and flags** | g++ 4.9.x ('we benchmarked it with this version only'); CMakeLists.txt: -std=c++11 -g -ggdb -O3 -m64 -march=native -ffast-math -Wall -Werror, AVX option ON, AVX2 option OFF |
| **Adoption** | 70 stars; PVLDB 9(4) 2015 paper (VLDB 2016) |
| **Last commit** | 2019-05-31 |
| **Links** | [repository](https://github.com/technicolor-research/pq-fast-scan) · [benchmark](https://raw.githubusercontent.com/technicolor-research/pq-fast-scan/HEAD/README.md) |

## Verdict

The authors' own scalar PQ Scan (8 float-table lookups per code plus heap) versus PQ Fast Scan on 25.2M-code ANN_SIFT100M1 partitions with ANN_SIFT1B queries, k = 100, keep = 0.5%: README rows give 75,392 vs 12,272 us and 74,754 vs 17,480 us (about 6.1x and 4.3x, derived from page data), consistent with the README's 4-6x and the PVLDB 9(4) paper (snippet only, which reports 4-6x across Intel CPUs released 2009-2014); built with g++ 4.9 -O3 -march=native -ffast-math, CPU model not stated on any reachable page.

## Use it when

- Exhaustive or large-partition (millions of codes) k-NN scans over 8x8-bit PQ codes with squared-L2 distance tables, on x86-64 with SSSE3.
- Top-k queries with small k (the benchmark uses k = 100) where most codes can be pruned by a lower bound, so throughput comes from skipping exact rescoring.
- When you need exactly the scalar ADC distances back rather than an approximation, and can afford a one-off re-layout of the database.
- As a readable reference implementation of the register-resident lookup-table idea before moving to a maintained engine.

## Skip it when

- Inverted-file (IVF) indexes with many small cells: the grouping into 16^4 groups and the 0.5% scalar warm-up only pay off on large partitions; the authors' Quick ADC (4-bit codes) and Faiss IndexIVFPQFastScan target that case.
- Inner-product or additive-quantization distances with negative terms: the lower-bound pruning assumes non-negative additive components (issue #2, an oracle mismatch abort on dot-product tables).
- Non-x86 targets, other code sizes (only 8 sub-quantizers of 8 bits are supported, NSQ and NCENT are compile-time macros) or batched multi-query search.
- Production use: research code abandoned since 2019, no library target, no tests beyond the oracle check, and it hard-links libpfm4 even for pqfastscan.

## How it is fast

The partition is re-laid out once: codes are grouped by the high 4 bits of components 4-7 (stored once in a group header), which shrinks each code from 8 to 6 bytes, and transposed into blocks of 16 codes. Per query it builds 16-entry int8 tables (minimums over centroid groups for components 0-3, exact 4-bit sub-tables per group for components 4-7), quantized against a bound obtained by scalar-scanning the first 0.5% of codes (keep). Each block of 16 codes then gets 8 pshufb lookups and saturating int8 adds, a lower bound compared against the quantized heap bound with pcmpgtb/pmovmskb; only survivors (24,404 and 435,694 of 25.2M codes for the two README queries) are rescored with the exact float tables.

## Compared with alternatives

Among the catalogued SIMD libraries only its sibling Quick ADC addresses the same problem; pick PQ Fast Scan when you need exact 8x8-bit PQ distances over large partitions, and Quick ADC when you scan many small IVF cells and accept 4-bit codes with a small recall loss.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | libpfm4 (linked into both benchmark executables for perf counters); CMake 2.8+ to build the benchmarks; the scan kernel itself needs only &lt;immintrin.h&gt; and the repo's binheap |
| **Minimum toolchain** | C++11, g++ 4.9 recommended (the only version benchmarked; g++ 5.2 'seemed' fine, clang untested); -march=native -ffast-math -Werror in CMakeLists |
| **Platforms** | x86-64 Linux with SSE2, SSE3, SSSE3 and POPCNT (AVX/AVX2 only for the baseline variants in pqscan) |
| **Thread safety** | not documented; scan_partition_1 increments global non-atomic Counters::total_scan and writes Counters::quant_bound, so concurrent scans race on those counters |
| **Drop-in for the baseline** | partial: the result heap matches PQ Scan's distances, but the database must be re-laid out (grouped and interleaved) and labels come from a permutation array the caller must keep |

## Gotchas

- Label bug in the shipped code: layout_partition() groups only the codes after the first 'keep' codes but permutes the identity array starting at index 0, and fast_scan_1() reports labels[i] without adding keep, so every neighbour found outside the first 0.5% of the partition is returned with an ID too small by keep (125,797 in the README run). The benchmark's oracle check compares only distances (tolerance 0.1), so it never catches this; timing is unaffected.
- Exactness depends on a strict test: candidates are kept only if the sum of floor-quantized int8 lower bounds is strictly below the floor-quantized heap bound, so a code whose true distance is just under the bound can in principle be pruned when the smallest table entry (qmin) is near zero; the 7\*qmin slack from per-component offsets usually hides this, and the benchmark aborts on any mismatch (reading of fastscan.cpp, not observed in a run).
- The published pqfastscan rows are single runs (repeat = 1, gettimeofday) per query with PQ Scan always timed first; speedup varies by query with the number of survivors (6.1x with 24,404 rescored codes, 4.3x with 435,694).
- pqscan needs root for perf counters and requests Intel-only events (CYCLE_ACTIVITY:CYCLES_LDM_PENDING and others); on other CPUs it fails until those events are removed (issue #1). Dataset links on assets.xion345.info no longer resolve (issue #3).

## Known shortcomings

- PVLDB paper known from snippets only (vldb.org blocked); the baseline is the authors' own scalar scan with no CPU model, built -march=native -ffast-math; README sample rows give 4.3x and 6.1x (derived) and the AVX+prefetch scan is only 9% faster than scalar.
- Bug in the shipped code: layout_partition() permutes labels starting at 0 for the codes after 'keep' and fast_scan_1() never adds keep back, so every neighbour outside the first 0.5% of the partition gets an ID too small by keep (125,797 in the README run); the oracle check compares distances only (tolerance 0.1), so it never catches this; timing is unaffected. Pruning uses a strict '&lt;' on floored int8 bounds, so it can in theory drop a true neighbour when qmin is near 0 (code reading, not observed). README rows are single runs (repeat = 1); lower-bound pruning breaks on inner-product tables (issue #2). No CPU model; the paper remains closed.

## Caveats and trade-offs

Tier B rests on the peer-reviewed PVLDB 9(4) paper (Andre, Kermarrec, Le Scouarnec; presented at VLDB 2016). The paper could not be opened (vldb.org blocked), so the 4-6x figure comes from the README and a search snippet. No reachable page gives a CPU model. The baseline is the authors' own scalar PQ Scan. In the README's pqscan output the SSE+prefetch (91214) and AVX+vgather+prefetch (97841) variants are slower than the scalar scan (74758), while AVX+prefetch (68490) is about 9% faster, so most of the gain comes from the register-resident lookup tables, not from vectorizing the plain scan. Builds use -march=native -ffast-math. The technique requires reorganizing the code lists (grouping), which the Quick ADC README says prevents combining it with inverted indexes, and it was tuned for 8x8-bit PQ codes on ANN_SIFT100M1 partitions. The datasets were generated with a commercially licensed libpq. Clear BSD has no patent grant and is not OSI-listed (permissive, treated as copyable).

Needs SSE2/SSE3/SSSE3 and POPCNT; relies on reorganising code lists, which prevents combining it with inverted indexes (README); Linux with libpfm4; best results only with g++ 4.9.

## Maintenance

Abandoned since 2019-05-31 (26 commits, 70 stars) but Clear-BSD-licensed and small enough to lift two source files from; fix the keep label offset before using its neighbour IDs, or use Faiss's maintained 4-bit FastScan indexes instead.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification B, tier now B.
- **Tier reason:** The README states the 4-6x figure over the scalar PQ Scan reference and cites the peer-reviewed PVLDB 9(4) paper. Search snippets confirm that the paper reports a 4-6x reduction in scan latency, but the paper itself was not opened here (vldb.org DNS blocked, snippet only). No CPU model is on any reachable page, so the record cannot reach A even though the code (pqfastscan) and flags (CMakeLists) are public.
- **Verifier notes:** The README matches the claim and the sample output rows support 4.3x to 6.1x (derived). Tier B rests on the PVLDB paper, which is known only from search snippets. Shortcomings to record: no CPU model on reachable pages, the authors' own scalar baseline, -march=native -ffast-math, and a code layout that cannot be combined with inverted indexes. 70 stars, 15 forks, last commit 2019-05-31 (abandoned). Not a duplicate, though Faiss (wave 8) later adopted a related 4-bit fast-scan approach (from memory, not checked here).
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`, `workload`
- **Shortcomings recorded by:** verifier batch-109 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/technicolor-research/pq-fast-scan/HEAD/README.md>
  - <https://raw.githubusercontent.com/technicolor-research/pq-fast-scan/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/technicolor-research/pq-fast-scan/HEAD/CMakeLists.txt>
  - <https://github.com/technicolor-research/pq-fast-scan>
  - <https://github.com/technicolor-research/pq-fast-scan/commits>
- **Sources the enricher read:**
  - <https://github.com/technicolor-research/pq-fast-scan>
  - <https://raw.githubusercontent.com/technicolor-research/pq-fast-scan/HEAD/README.md>
  - <https://raw.githubusercontent.com/technicolor-research/pq-fast-scan/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/technicolor-research/pq-fast-scan/HEAD/LICENSE>
  - <https://github.com/technicolor-research/pq-fast-scan/tree/master/pqfastscan>
  - <https://github.com/technicolor-research/pq-fast-scan/tree/master/pqscan>
  - <https://raw.githubusercontent.com/technicolor-research/pq-fast-scan/master/pqfastscan/pqfastscan.cpp>
  - <https://raw.githubusercontent.com/technicolor-research/pq-fast-scan/master/pqfastscan/fastscan.cpp>
  - <https://raw.githubusercontent.com/technicolor-research/pq-fast-scan/master/pqfastscan/fastscan.hpp>
  - <https://raw.githubusercontent.com/technicolor-research/pq-fast-scan/master/pqfastscan/layout.cpp>
  - <https://raw.githubusercontent.com/technicolor-research/pq-fast-scan/master/pqfastscan/layout.hpp>
  - <https://raw.githubusercontent.com/technicolor-research/pq-fast-scan/master/pqscan/pqscan.cpp>
  - <https://raw.githubusercontent.com/technicolor-research/pq-fast-scan/master/pqscan/scan_naive.cpp>
  - <https://raw.githubusercontent.com/technicolor-research/pq-fast-scan/master/pqscan/scan_avx.cpp>
  - <https://raw.githubusercontent.com/technicolor-research/pq-fast-scan/master/pqscan/populate.cpp>
  - <https://raw.githubusercontent.com/technicolor-research/pq-fast-scan/master/benchmark.cpp>
  - <https://raw.githubusercontent.com/technicolor-research/pq-fast-scan/master/benchmark.hpp>
  - <https://raw.githubusercontent.com/technicolor-research/pq-fast-scan/master/binheap.cpp>
  - <https://raw.githubusercontent.com/technicolor-research/pq-fast-scan/master/binheap.hpp>
  - <https://raw.githubusercontent.com/technicolor-research/pq-fast-scan/master/common.cpp>
  - <https://raw.githubusercontent.com/technicolor-research/pq-fast-scan/master/common.hpp>
  - <https://raw.githubusercontent.com/technicolor-research/pq-fast-scan/master/config.h.in>
  - <https://github.com/technicolor-research/pq-fast-scan/issues?q=is%3Aissue>
  - <https://github.com/technicolor-research/pq-fast-scan/issues/1>
  - <https://github.com/technicolor-research/pq-fast-scan/issues/2>
  - https://github.com/facebookresearch/faiss/wiki/Fast-accumulation-of-PQ-and-AQ-codes-(FastScan)
  - http://assets.xion345.info/vldb16/slides.pdf (DNS failure, not read)
  - WebSearch snippets for the PVLDB paper and the thesis arXiv 1712.02912 (pages not opened, arXiv blocked)
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/technicolor-research/pq-fast-scan`) · [data/wave13/enrich/raw/github_com_technicolor_research_pq_fast_scan.json](../../../data/wave13/enrich/raw/github_com_technicolor_research_pq_fast_scan.json) (enrichment confidence 0.8)

</details>
