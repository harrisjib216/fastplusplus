# WFA2-lib

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [SIMD intrinsics libraries](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `MIT` · 🟢 active

> Exact wavefront (WFA/BiWFA) pairwise aligner in C; about 7x faster than unbanded KSW2 on long, similar reads.

| | |
|---|---|
| **Beats** | KSW2 (ksw2_extz2_sse, exact unbanded gap-affine DP with CIGAR); the artifact also times edlib, BitPAl and WFA-LM |
| **Claimed result** | No comparison numbers in the WFA2-lib README or tools README (the tools README only shows a sample align_benchmark run of 5M 100 bp pairs on an unnamed machine). From the BiWFA paper artifact data (smarco/BiWFA-paper evaluation/data, matched pairs, ratios computed by me from the raw per-pair time_ms rows, derived from page data): total time of ksw2-extz2-sse divided by WFA2 default high-memory mode is 7.26x on the 1,326 ONT-region pairs (median per-pair ratio 12.2x, WFA2 faster on 99% of pairs) and 7.51x on the 1,991 MinION ultra-long pairs (median per-pair ratio 4.6x, WFA2 faster on about 100% of pairs at two-decimal rounding); BiWFA (O(s) memory) is 9.95x and 9.76x faster in total time than ksw2; the medium-memory mode is 2.6x and 2.0x faster than ksw2. The alignment scores agree with ksw2 on all 3,317 pairs compared. WFA2 high-memory mode is also 3.0x faster than WFA-LM, but edlib (edit distance only, not gap-affine) is faster than every WFA2 mode (about 9x faster than the high-memory mode in total time on the first set, derived). |
| **Workload** | Exact gap-affine alignment (penalties 0,4,6,2, CIGAR output) of long real sequence pairs: 1,326 ONT-region pairs and 1,991 ONT MinION ultra-long read pairs (hsapiens HG002/CHM13 data), per-pair time in ms from the BiWFA paper artifact's statistics_all.tsv.gz. |
| **Metric** | latency |
| **Hardware** | BSC cluster jobs (the evaluation scripts copy data to amdlogin.bsc.es, BSC's AMD partition) submitted with sbatch -c 128 --exclusive, one alignment at a time per job loop; CPU model not stated in the repo. |
| **Compiler and flags** | gcc 10.2.0 (module load gcc/10.2.0 in evaluation/0_Preparation.md); BiWFA-paper Makefile 'all' target adds -O3 -march=native to CC_FLAGS=-Wall -g; benchmark branch pinned at commit d5532da; ksw2 run through the artifact's align_benchmark with ksw2_bandwidth -1 and zdrop -1 (no banding). |
| **Adoption** | 229 stars; 54 forks |
| **Last commit** | 2026-09-30 |
| **Links** | [repository](https://github.com/smarco/WFA2-lib) · [benchmark](https://github.com/smarco/BiWFA-paper/tree/main/evaluation/data) |

## Verdict

In the BiWFA paper artifact (smarco/BiWFA-paper, gcc 10.2.0, -O3 -march=native, BSC AMD cluster nodes with unnamed CPU), WFA2 high-memory mode in exact mode took 7.26x and 7.51x less total time than unbanded ksw2_extz2_sse on 1,326 ONT-region pairs and 1,991 ultra-long MinION pairs (penalties 0,4,6,2, CIGAR output; ratios derived from the per-pair rows), BiWFA about 9.8-10x, with identical scores; edlib (edit distance only) was faster still.

## Use it when

- Exact gap-affine global or ends-free alignment with CIGAR of long, similar sequences (ONT/PacBio reads against a reference region, assembly contigs, haplotypes) where full DP is O(n^2).
- Pipelines that currently call ksw2 without banding and want the optimal alignment faster: the BiWFA artifact shows about 7x total-time gains at 0,4,6,2 penalties on long human ONT data.
- Very long pairs (100 kbp to Mbp) where O(s^2) or O(n^2) memory is a problem: use the ultralow (BiWFA) mode for O(s) memory.
- Portable builds that must run on x86, ARM or other ISAs without per-ISA SIMD code paths.

## Skip it when

- Highly divergent pairs or pairs with very different lengths: cost grows with score s, and issue #13 (labelled bug) reports slow runs when lengths differ greatly; banded SIMD DP (ksw2, parasail) can win there.
- Local (Smith-Waterman) alignment: not supported (open feature request #61); use SSW or parasail.
- Edit distance only: in the same artifact edlib was faster than every WFA2 mode.
- Ends-free alignment with a nonzero match score: open issue #102 reports suboptimal results, with no maintainer reply.
- Short reads in bulk with the default high-memory mode and per-pair aligner creation: issue #97 reports out-of-memory and segfaults after millions of alignments.

## How it is fast

The wavefront alignment algorithm only computes the furthest-reaching diagonal offsets for each score, so its time is O(ns+s^2) in alignment score s rather than O(n^2) DP cells; on similar sequences most of the work is the 'extend' step, which compares 8 bytes at a time with 64-bit XOR plus count-trailing-zeros. The per-score 'compute' loops are written to be auto-vectorised by the compiler (PRAGMA_LOOP_VECTORIZE, -O3 -march=native) instead of using ISA intrinsics. BiWFA (memory mode ultralow) runs the wavefronts from both ends and recurses at the meeting point, cutting memory to O(s) while keeping O(ns) time.

## Compared with alternatives

Pick WFA2-lib over ksw2 when you need the exact gap-affine CIGAR of long, similar sequences without tuning a band; pick ksw2 or parasail for banded or divergent alignments and their SIMD striped kernels, and SSW or parasail when you need local alignment.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | none for the C library (libm; optional OpenMP); C++ bindings ship as libwfacpp; Rust bindings generated with bindgen |
| **Minimum toolchain** | C compiler with GNU builtins (__builtin_ctzl, __builtin_expect), i.e. GCC or Clang; CMake 3.16+ or the plain Makefile; no minimum version documented |
| **Platforms** | any 64-bit target the compiler auto-vectorises for (README names SSE, AVX2, AVX-512, NEON, SVE, POWER, RISC-V); Release builds use -march=native |
| **Thread safety** | not documented; an aligner object holds mutable buffers, so use one wavefront_aligner_t per thread (single-threaded by default; -DOPENMP enables intra-alignment parallelism via max_num_threads) |
| **Drop-in for the baseline** | partial — same alignment problem and penalties as ksw2 extz2 (scores matched on all 3,317 artifact pairs), but a different API, ASCII input instead of encoded bases, and different banding/zdrop controls |

## Gotchas

- The default attributes (wavefront_aligner_attr_default, also used by the C++ WFAligner constructors) enable the wf-adaptive heuristic (min_wavefront_length 10, max_distance_threshold 50), so out-of-the-box results are not guaranteed optimal despite the README's 'exact' framing; set heuristic.strategy = wf_heuristic_none (or setHeuristicNone()) for exact results. The BiWFA-paper benchmark used align_benchmark's own default wf_heuristic_none, so the measured numbers are exact-mode numbers.
- Create the aligner once and reuse it; per-pair create/delete has significant overhead and is implicated in the memory blow-ups of issue #97.
- CIGARs describe pattern-to-text; swap arguments to get SAM-convention I/D, and ultralow (BiWFA) breaks score ties differently from the other modes.
- The measured numbers come from a 2022 BiWFA-paper snapshot (commit d5532da), not the current main, on long low-divergence ONT reads; CPU model unstated.

## Known shortcomings

- Ratios recomputed from the BiWFA paper's statistics_all.tsv.gz (7.26x and 7.51x vs ksw2, scores equal on all 3,317 pairs) with the timer covering only the alignment call, but no CPU model is stated, the measured code is the d5532da paper snapshot, the workload favours long low-divergence reads, edlib is faster than every WFA2 mode, and the gain comes from the algorithm rather than SIMD (loose category fit).
- Enricher: the library defaults (C attributes and the C++ WFAligner) turn on the wf-adaptive heuristic, so out-of-the-box results are not guaranteed optimal; the BiWFA paper benchmark used wf_heuristic_none, so the measured numbers are exact. Open #102 (suboptimal ends-free results with a nonzero match score, no maintainer reply) and #97 (OOM or segfault after millions of alignments).

## Caveats and trade-offs

The measured code is the BiWFA-paper snapshot (benchmark branch commit d5532da), not the current WFA2-lib main, and the data are long noisy reads at small divergence where WFA's O(ns) behaviour is most favourable; short reads or highly divergent pairs will show other ratios. CPU model is missing, so tier B (peer-reviewed artifact of the Bioinformatics 2023 BiWFA paper) not A; the paper itself was not reachable (NCBI, bioRxiv and NSF PAR blocked). The time_ms column is align_benchmark's own per-pair timer (InfoAlignment line parsed by evaluation/scripts/log2info.py): timer_start/timer_stop wrap only the alignment call in each wrapper (ksw_extz2_sse for ksw2), the --check correct verification runs outside the timer, and --repeat 100000 is a target number of aligned bases, so long pairs run once and shorter pairs are averaged over repeats; process startup and input parsing are excluded. ksw2 completed 1,991 of the 2,000 MinION pairs; the 9 missing pairs are excluded from the ratios. The artifact's ksw2 wrapper passes the raw ASCII sequences rather than the 0-3 encoded copies it builds; ksw2's fast path only compares bases for equality, and the scores match WFA2 on all 3,317 pairs, so results are correct. The memory_kb column looked inconsistent and was not used. Edlib (edit distance only, not gap-affine) is faster than every WFA2 mode in this data, and BitPAl's score-only mode is about as fast as WFA2 high-memory (7.5x vs ksw2). The speedup is algorithmic (wavefront O(ns) versus full O(n^2) DP) rather than from SIMD intrinsics, so the simd-intrinsics-libraries category is a loose fit. [retier] Enricher: the library defaults enable the wf-adaptive heuristic (results not guaranteed optimal); the BiWFA benchmark ran wf_heuristic_none, so its numbers are exact; open #102 (suboptimal ends-free results) and #97 (OOM or segfault after millions of alignments).

Exact algorithm whose time is O(ns+s^2) in score s: huge wins on similar sequences, shrinking as divergence grows. Default high-memory mode needs O(s^2) memory; low, ultralow (BiWFA, O(s) memory) and heuristic modes trade time for memory or accuracy. Gap-linear, gap-affine and dual-gap affine costs with end-to-end and ends-free (semi-global, glocal, extension) modes per the README; local Smith-Waterman is not listed. Plain C with compiler auto-vectorisation rather than intrinsics, so no ISA-specific code. C++ and Rust bindings.

## Maintenance

Active (commits through 2026-09-30, README and CI fixes in September 2026), MIT-licensed and easy to vendor as a static C library, but 17 open issues include an unanswered suboptimal-result bug in ends-free mode (#102) and memory problems at scale (#97).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed artifact of the Bioinformatics 2023 BiWFA paper (smarco/BiWFA-paper evaluation/1_RealData.md scripts, tools/align_benchmark wrappers, evaluation/data/statistics_all.tsv.gz) with compiler (gcc 10.2.0) and flags (-O3 -march=native) stated; the CPU model is not stated in the repo and the paper (NCBI, bioRxiv, NSF PAR) was unreachable, so not A. I re-derived every ratio in claimed_speedup from the raw per-pair time_ms rows and they match.
- **Verifier notes:** Confirmed at B. Ratios re-derived from statistics_all.tsv.gz: wfa-high vs ksw2-extz2-sse 7.26x total (median 12.2x, faster on 98.6% of pairs) on 1,326 ONT-region pairs and 7.51x (median 4.6x) on 1,991 MinION pairs; BiWFA 9.95x and 9.76x; scores agree on all 3,317 pairs. Shortcomings: CPU model unstated, measured code is a 2022 paper snapshot, favourable low-divergence long-read workload, edlib (edit distance only) faster than all WFA2 modes; a paper-access retier could reach A if the paper names the CPU.
- **Fields the verifier corrected:** `hardware`, `caveats`
- **Shortcomings recorded by:** verifier batch-126 (wave 13 seed pass, 2026-10-13); enricher (seed pass, 2026-10-13)
- **Pages the verifier opened:**
  - <https://github.com/smarco/WFA2-lib>
  - <https://github.com/smarco/WFA2-lib/commits>
  - <https://github.com/smarco/BiWFA-paper/tree/main/evaluation/data>
  - <https://github.com/smarco/BiWFA-paper/tree/main/evaluation>
  - <https://raw.githubusercontent.com/smarco/BiWFA-paper/HEAD/README.md>
  - <https://raw.githubusercontent.com/smarco/BiWFA-paper/HEAD/evaluation/0_Preparation.md>
  - <https://raw.githubusercontent.com/smarco/BiWFA-paper/main/evaluation/1_RealData.md>
  - <https://raw.githubusercontent.com/smarco/BiWFA-paper/main/Makefile>
  - <https://raw.githubusercontent.com/smarco/BiWFA-paper/main/evaluation/data/statistics_all.tsv.gz>
  - <https://raw.githubusercontent.com/smarco/BiWFA-paper/main/evaluation/data/scores_all.tsv.gz>
  - <https://raw.githubusercontent.com/smarco/BiWFA-paper/main/evaluation/scripts/log2info.py>
  - <https://raw.githubusercontent.com/smarco/BiWFA-paper/d5532da3b861d545d5c34ea4ef314ec439591d05/tools/align_benchmark/align_benchmark.c>
  - <https://github.com/smarco/BiWFA-paper/tree/d5532da3b861d545d5c34ea4ef314ec439591d05/tools/align_benchmark>
  - <https://github.com/smarco/BiWFA-paper/tree/d5532da3b861d545d5c34ea4ef314ec439591d05/tools/align_benchmark/external>
  - <https://github.com/smarco/BiWFA-paper/tree/d5532da3b861d545d5c34ea4ef314ec439591d05/tools/align_benchmark/benchmark>
  - <https://raw.githubusercontent.com/smarco/BiWFA-paper/d5532da3b861d545d5c34ea4ef314ec439591d05/tools/align_benchmark/benchmark/external/benchmark_ksw2.c>
  - <https://raw.githubusercontent.com/smarco/BiWFA-paper/d5532da3b861d545d5c34ea4ef314ec439591d05/tools/align_benchmark/benchmark/benchmark_gap_affine.c>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/smarco/WFA2-lib/HEAD/README.md>
  - <https://raw.githubusercontent.com/smarco/WFA2-lib/HEAD/wavefront/wavefront_attributes.c>
  - <https://raw.githubusercontent.com/smarco/WFA2-lib/HEAD/bindings/cpp/WFAligner.cpp>
  - <https://raw.githubusercontent.com/smarco/WFA2-lib/HEAD/Makefile>
  - <https://raw.githubusercontent.com/smarco/WFA2-lib/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/smarco/WFA2-lib/HEAD/wavefront/wavefront_extend_kernels.c>
  - <https://raw.githubusercontent.com/smarco/WFA2-lib/HEAD/wavefront/wavefront_compute_affine.c>
  - <https://raw.githubusercontent.com/smarco/BiWFA-paper/main/evaluation/1_RealData.md>
  - <https://raw.githubusercontent.com/smarco/BiWFA-paper/d5532da3b861d545d5c34ea4ef314ec439591d05/tools/align_benchmark/align_benchmark.c>
  - <https://github.com/smarco/WFA2-lib>
  - <https://github.com/smarco/WFA2-lib/issues>
  - <https://github.com/smarco/WFA2-lib/issues/102>
  - <https://github.com/smarco/WFA2-lib/issues/97>
  - <https://github.com/smarco/WFA2-lib/commits>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/smarco/wfa2-lib`) · [data/wave13/enrich/raw/github_com_smarco_wfa2_lib.json](../../../data/wave13/enrich/raw/github_com_smarco_wfa2_lib.json) (enrichment confidence 0.8)

</details>
