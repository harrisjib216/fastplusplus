# ish

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Numerics and arrays](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Mojo` · `Apache-2.0` · 🟢 active

> Mojo grep-like CLI that filters lines or FASTA/FASTQ records by striped-SIMD alignment score; slightly beats parasail_aligner at matched costs.

| | |
|---|---|
| **Beats** | parasail (C) parasail_aligner, striped semi-global (sg_dx_striped sse41_128 and avx2_256, 8- and 16-bit variants) |
| **Claimed result** | Sassy evals README (written by the authors of a competing tool, evals artifact of the Sassy paper): ish takes 69 s with an SSE build and 110 s with the AVX2 build; parasail_aligner with ish's cost parameters (-X 2 -M 2 -o 3 -e 1) takes '81s-198s' across the four striped variants (sse41_128_8, sse41_128_16, avx2_256_8, avx2_256_16); with parasail's default cost parameters it takes '53-69s'. Best against best at matched costs: 81 s / 69 s = 1.17x faster (derived from page data); the per-variant mapping of times is not given. The ish paper (Bioinformatics Advances, November 2025, DOI 10.1093/bioadv/vbaf292) states that ish's core algorithms meet or exceed the performance of their reference implementations in Parasail for both SIMD and GPU alignment as measured by GCUPS (snippet only; paper not opened). The ish README itself gives no performance numbers. |
| **Workload** | Single-thread semi-global search of one 23 bp DNA pattern (ACTCGACTTCAGCTACGCACATA) across the human T2T CHM13 v2.0 genome (chm13v2.0.fa), ish scoring match 2, mismatch -2, gap open 3, extend 1. |
| **Metric** | throughput |
| **Compiler and flags** | ish: 'mojo build --march native' via pixi (HEAD pins Mojo 0.25.6; the Sassy comparison used ish commit 92f4fad of 2025-07-21, whose Mojo version is probably 25.4 per the CHANGELOG), SSE row built with -D ISH_SIMD_TARGET=sse; parasail: built from a git clone with its default configure or cmake build, flags not stated. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | not stated |
| **Adoption** | 63 stars; no releases |
| **Last commit** | 2025-10-31 |
| **Links** | [repository](https://github.com/BioRadOpenSource/ish) · [benchmark](https://raw.githubusercontent.com/RagnarGrootKoerkamp/sassy/HEAD/evals/README.md) |

## Verdict

In the Sassy paper's evals README, Sassy's authors timed one 23 bp DNA pattern searched single-threaded across T2T CHM13 v2.0: ish (commit 92f4fad, 16-bit striped semi-global, match 2, mismatch -2, gap open 3, extend 1) took 69 s with an SSE build and 110 s with AVX2, against 81-198 s for parasail_aligner's four sg_dx striped variants (SSE4.1 and AVX2, 8- and 16-bit) at the same costs (best against best 1.17x, derived from page data) and 53-69 s at parasail's default costs. Wall times come from 'time' and include FASTA parsing for both tools; CPU model, compiler flags, repetition count and the per-variant split of the parasail range are not given, and the ish paper's own GCUPS numbers were not reachable.

## Use it when

- Shell pipelines that need a fuzzy grep by affine-gap alignment score, e.g. finding a primer, barcode or guide sequence with mismatches and indels in reads or assemblies (actgn matrix, fastx mode).
- Protein queries scored with BLOSUM62 against FASTA databases, filtering records by local or semi-global score rather than computing full alignments.
- Single-pattern CPU scans at small gap penalties (open 3, extend 1), where Sassy's evals measured ish's SSE build at 69 s against 81-198 s for parasail_aligner's striped sg_dx variants at the same costs.
- Many target records on a machine with a Mojo-supported GPU; the author says the GPU path pays off with many reference sequences (e.g. a protein database), not for one query against one genome.

## Skip it when

- Pure edit-distance pattern search in whole genomes: in issue #54 Sassy took 2 s wall for a 23 bp pattern with up to 4 errors where ish took about 60 s wall (200 s CPU) on the same 3 Gbp genome.
- You need every hit: the CLI reports only the single best match per line or record, so a chromosome-sized FASTA record yields at most one hit.
- Multicore scaling matters: Mojo's parallelize runtime caps ish at about half the cores (300% CPU on a 6-core machine, issue #54, still open, blocked on upstream Mojo).
- You can use parasail at its default costs (match 1, mismatch 0, open 10, extend 1): it took 53-69 s there, as fast as or faster than ish's 69 s best.
- You need a C/C++ library, a stable toolchain or releases: ish requires pixi or conda with a pinned Mojo (0.25.6 at HEAD), has no tagged releases, and its ish-aligner benchmark tool is marked development-only.

## How it is fast

The kernels are Farrar's striped SIMD alignment (query profile laid out in striped segments, SWPS3-style lazy-F correction loop), refined as in SSW and modelled on parasail, written with Mojo SIMD types and LLVM saturating add/subtract intrinsics. The CLI's semi-global path runs a 16-bit (int16) profile with saturation checks compiled out, and runs the reverse pass that locates the match start only when the forward score clears the cutoff. Vector width is a compile-time choice (ISH_SIMD_TARGET sse, avx256, avx512, or native); the lazy-F loop runs up to one pass per lane, so narrow SSE vectors suit short patterns. Both sides of the parasail comparison run the same algorithm, and no source read explains where ish's small edge comes from.

## Compared with alternatives

None of the numerics-and-arrays siblings is a sequence aligner; the Mojo siblings (llama2.mojo, llm.mojo, mojo-analyze) share only the toolchain, so pick ish when the job is score-thresholded alignment filtering. The catalogued Sassy entry (wave 14) is orders of magnitude faster for edit-distance search of short patterns, so pick ish only when you need affine gaps, scoring matrices such as BLOSUM62 or local alignment.

## Integration

| | |
|---|---|
| **Form** | CLI binary built from Mojo source (pixi run build) or a conda package from the modular-community channel; ishlib can be packaged as a Mojo module |
| **Dependencies** | Mojo compiler (pinned =0.25.6 at v1.4.0), extramojo 0.18.0, pixi or conda; parasail, autotools and the UniProt 2015_11 data only for the benchmark tasks |
| **Minimum toolchain** | Mojo 0.25.6 at HEAD (v1.2.0 to v1.3.x used Mojo 25.4); Linux x86-64 per the issue reports; the README recommends building from source over the conda package for speed |
| **Platforms** | x86-64 with SSE, AVX2 or AVX-512 (width chosen at build time; Mojo emulates wider vectors if the CPU lacks them); GPU path needs a Mojo-supported GPU; macOS and aarch64 not documented |
| **Thread safety** | not documented; the CLI parallelizes over record batches with --threads (default: physical cores) and --batch-size |
| **Drop-in for the baseline** | partial — same striped semi-global and local algorithms and scoring options as parasail, but exposed as a grep-style filter that returns matching records, not parasail's C API or parasail_aligner's pairwise score output |

## Gotchas

- Build width matters more than expected: the default 'pixi run build' uses the native width (AVX-512 where present), yet Sassy measured the AVX2 build at 110 s against 69 s for -D ISH_SIMD_TARGET=sse on a 23 bp pattern; a native-width build also segfaulted with the actgn matrix on an AVX-512 Xeon Gold 6240 until a June 2025 fix (issue #50).
- Output is not byte-identical to input: matched records are printed after an encoding round-trip, so under actgn lowercase soft-masked bases come out uppercase and letters outside ACGTU come out as N; each FASTA sequence is written on one line, and the match is highlighted with ANSI colour codes only when stdout is a terminal.
- The CLI semi-global path uses only the int16 profile with do_saturation_check=False and no 8-bit or 32-bit fallback, so very long patterns could clamp silently near the int16 limit (inferred from the code, not tested).
- Harness flaw in the repo's own benchmark (benchmarking/bench_scripts/bench.py, which the paper's GCUPS comparison presumably used): parasail_aligner is called with non-profile function names, so its 'alignment time' rebuilds the query profile for every target pair and includes result output, while ish-aligner builds profiles before its timer, flushes output after it, and reports the mean of 3 iterations against parasail's single run; no results or hardware are stored, so the paper's 'meets or exceeds parasail' GCUPS claim cannot be checked from the repo.

## Known shortcomings

- Raised from C to B on the independent Sassy evals README (artifact of the Sassy paper): at ish's costs ish 69 s SSE and 110 s AVX2 against parasail 81-198 s, best against best about 1.17x (derived from page data), but at parasail's default costs parasail ties or wins (53-69 s); no CPU or flags. The ish paper (Bioinformatics Advances 2025) was seen as a snippet only.
- Enricher: ish's own bench.py runs parasail_aligner with non-profile function names, so parasail rebuilds the query profile per pair and includes output writes in its time, while ish builds profiles before the timer and reports a mean of 3 runs against parasail's single run; no stored results. The catalogued B rests on the Sassy evals instead (same algorithm at 16-bit: ish 69 s SSE vs parasail 81-198 s; parasail at its defaults 53-69 s). The CLI prints only the best hit per record and loses lowercase and non-ACGT letters; Mojo thread cap (#54); AVX-512 segfault fixed (#50).

## Caveats and trade-offs

The ish paper was published in Bioinformatics Advances (November 2025, DOI 10.1093/bioadv/vbaf292, PMC12930471; seen in a search snippet only) but could not be opened (bioRxiv, doi.org and ncbi.nlm.nih.gov are unreachable here), so the authors' own GCUPS numbers, hardware and build flags are unseen; the only numbers found are from the Sassy repo, where Sassy's authors time ish and parasail as side baselines. CPU model, Mojo and parasail build flags and run count are not given in that README ('For me, this takes 69s for SSE'). The win depends on cost parameters: parasail with its default costs (53-69 s) is as fast as or faster than ish (69 s SSE, 110 s AVX2); at matched costs the best margin is only 1.17x and the mapping of the 81-198 s range onto the four parasail variants is not given. The ish AVX2 build is slower than SSE for this short pattern. The repo ships a reproducible harness (benchmarking/bench_scripts/bench.py, 'pixi run bench-all-cpu', uniprot_sprot 2015_11 and the parasail paper's query set, parasail built with autoreconf and configure; it runs parasail_aligner single-threaded with -x, gap open 3 and extend 1, Blosum62 by default and the saturation-checking 'sat' variants by default) but no stored results and no hardware record. Both sides run Farrar-style striped semi-global alignment, so the comparison is same-algorithm; the mechanism behind ish's edge is not stated in the sources opened. No ksw2 comparison found. [retier] Enricher: ish's bench.py runs parasail with non-profile functions (profile rebuilt per pair, output writes timed) against ish's pre-built profiles and a mean of 3 runs; the B rests on the Sassy evals, where at parasail's defaults parasail ties or wins.

CLI grep-like record filter written in Mojo (pixi or conda install); striped semi-global and local alignment with affine gaps and scoring matrices; optional GPU path; SIMD width is a compile-time choice (SSE or AVX2 or AVX-512); ish-aligner is flagged development-only.

## Maintenance

Apache-2.0 and single-author (Bio-Rad), last commit 2025-10-31 (v1.4.0, Mojo 0.25.6) with one open issue and no releases, so it is maintained but tied to a fast-moving pinned Mojo toolchain; usable as a CLI, not as a library to vendor into C++.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now B.
- **Tier reason:** Upgraded C to B: the timings come from an independent party (the authors of the competing tool Sassy) in the evals artifact of their paper, which the catalog's Sassy entry records as published in Bioinformatics (May 2026); the evals README gives exact commands for both tools but no CPU model or compiler flags, so not A. Ish's own peer-reviewed paper (Bioinformatics Advances, Nov 2025) also claims parity-or-better against parasail, but that was seen only in a search snippet.
- **Verifier notes:** Metadata checks out (63 stars, Apache-2.0, no releases, last commit 2025-10-31, Sassy-tested commit 92f4fad dated 2025-07-21). Upgraded to B on the independent Sassy measurement; shortcomings: marginal 1.17x win only at ish's cost parameters, parasail at default costs ties or wins, no CPU or flags in the README, ish paper numbers unseen. Sassy itself is already listed in wave 14 (a different project, not a duplicate).
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-111 (wave 14 seed pass, 2026-10-13); enricher (seed pass, 2026-10-13)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/sassy/HEAD/evals/README.md>
  - <https://raw.githubusercontent.com/BioRadOpenSource/ish/HEAD/README.md>
  - <https://github.com/BioRadOpenSource/ish>
  - <https://github.com/BioRadOpenSource/ish/commits>
  - <https://github.com/BioRadOpenSource/ish/tree/main/benchmarking>
  - <https://raw.githubusercontent.com/BioRadOpenSource/ish/HEAD/benchmarking/bench_scripts/bench.py>
- **Sources the enricher read:**
  - <https://github.com/BioRadOpenSource/ish>
  - <https://github.com/BioRadOpenSource/ish/commits/main>
  - <https://github.com/BioRadOpenSource/ish/issues?q=is%3Aissue>
  - <https://github.com/BioRadOpenSource/ish/issues/54>
  - <https://github.com/BioRadOpenSource/ish/issues/50>
  - <https://github.com/BioRadOpenSource/ish/tree/main/ishlib>
  - <https://github.com/BioRadOpenSource/ish/tree/main/ishlib/matcher>
  - <https://github.com/BioRadOpenSource/ish/tree/main/ishlib/matcher/alignment>
  - <https://github.com/BioRadOpenSource/ish/tree/main/benchmarking>
  - <https://raw.githubusercontent.com/BioRadOpenSource/ish/HEAD/README.md>
  - <https://raw.githubusercontent.com/BioRadOpenSource/ish/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/BioRadOpenSource/ish/HEAD/pixi.toml>
  - <https://raw.githubusercontent.com/BioRadOpenSource/ish/HEAD/BENCHMARKING.md>
  - <https://raw.githubusercontent.com/BioRadOpenSource/ish/HEAD/benchmarking/bench_scripts/bench.py>
  - <https://raw.githubusercontent.com/BioRadOpenSource/ish/HEAD/benchmarking/ish_bench_aligner.mojo>
  - <https://raw.githubusercontent.com/BioRadOpenSource/ish/HEAD/ishlib/matcher/striped_semi_global_matcher.mojo>
  - <https://raw.githubusercontent.com/BioRadOpenSource/ish/HEAD/ishlib/matcher/alignment/semi_global_aln/striped.mojo>
  - <https://raw.githubusercontent.com/BioRadOpenSource/ish/HEAD/ishlib/matcher/alignment/scoring_matrix.mojo>
  - <https://raw.githubusercontent.com/BioRadOpenSource/ish/HEAD/ishlib/matcher/__init__.mojo>
  - <https://raw.githubusercontent.com/BioRadOpenSource/ish/HEAD/ishlib/fastx_search_runner.mojo>
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/sassy/HEAD/evals/README.md>
  - <https://raw.githubusercontent.com/jeffdaily/parasail/HEAD/apps/parasail_aligner.cpp>
  - WebSearch snippet: Ish: SIMD and GPU accelerated local and semi-global alignment as a CLI filtering tool (Bioinformatics Advances, PMC12930471; full text unreachable)
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/bioradopensource/ish`) · [data/wave14/enrich/raw/github_com_bioradopensource_ish.json](../../../data/wave14/enrich/raw/github_com_bioradopensource_ish.json) (enrichment confidence 0.65)

</details>
