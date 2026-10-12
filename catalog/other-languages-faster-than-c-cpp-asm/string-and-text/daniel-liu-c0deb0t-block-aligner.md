# block-aligner

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Strings and text](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟡 stale

> Rust SIMD adaptive-block heuristic aligner (affine gaps, profiles); about 2-3x faster than Edlib, 1.5-2x than banded ksw2, approximate.

| | |
|---|---|
| **Beats** | parasail (C), ksw2 ksw_extz2_sse (C), Edlib (C++), WFA2-lib (C), each called from the Rust benchmark through FFI bindings (parasailors, ksw2-sys, edlib_rs, rust-wfa2) |
| **Claimed result** | Saved notebook outputs in vis/block_aligner_bench_vis.ipynb, total seconds, 'ours (1%-1%)' with traceback vs baselines: Illumina 0.331 s vs Edlib 1.078, ksw_extz2_sse(1%) 0.702, ksw_extz2_sse(10%) 0.662, parasail 1.877, WFA2 0.0396, WFA2 adaptive 0.0338; Nanopore 1kbp 0.355 vs Edlib 0.982, ksw2(1%) 0.690, ksw2(10%) 1.492, WFA2 1.074, WFA2 adaptive 0.968, parasail 4.241; Nanopore under 10kbp 1.233 vs Edlib 4.182, ksw2(1%) 2.041, ksw2(10%) 13.948, WFA2 12.232, WFA2 adaptive 2.636, parasail 35.789; Nanopore under 50kbp 29.619 vs Edlib 63.197, ksw2(1%) 44.493, ksw2(10%) 571.018, WFA2 331.475, WFA2 adaptive 58.830 (parasail not run). Derived from page data: block-aligner is 2.1x to 3.4x faster than Edlib, 1.5x to 2.1x faster than banded ksw2 at 1% band, 5.7x to 29x faster than parasail, but about 8.4x SLOWER than exact WFA2 on Illumina reads. Protein Uniclust30 (no traceback, block 32-256) 0.0886 s vs parasail 0.8250 s (9.3x, derived); with traceback 0.1698 s (4.9x, derived). SCOP profile pairs 0.149 s (block 32-32) vs parasail 0.597 s (4.0x, derived). The same notebook's 25 kbp Nanopore benchmark shows block-aligner SLOWER than the C aligners from diff-bench-paper: ours (no trace 32-32) 0.991 s and (trace 32-32) 1.378 s against libgaba 0.433 s, Suzuki-Kasahara editdist 0.480 s, diff-raw 0.611 s and non-diff 0.676 s fill time, while Edlib took 28.0 s and SeqAn 90.3 s (about 2.3x slower than libgaba, derived from page data; the C rows come from a separate harness, custom_bench.sh, and count fill time only). |
| **Workload** | Global affine-gap alignment with traceback of Illumina reads, Nanopore reads (1 kbp, under 10 kbp, under 50 kbp) with match 2, mismatch -4, gap open -6, extend -2, plus Uniclust30 protein pairs (BLOSUM62, gaps 11/1) and SCOP sequence-to-profile pairs against score-only parasail. |
| **Metric** | throughput |
| **Hardware** | CPU model not stated anywhere opened; AVX2 build; notebook paths (/usr/local/anaconda3, Homebrew LLVM clang) suggest an x86-64 macOS machine. |
| **Compiler and flags** | cargo run --release --features simd_avx2 on Rust nightly (rust-toolchain file says 'nightly'); Cargo profile.release lto='thin', panic='abort'; the DNA script sets CC=/usr/local/opt/llvm/bin/clang for the C/C++ -sys crates; their optimisation flags live in each -sys crate's build script and were not read; rustc and clang versions unstated. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Why it wins** | Adaptive block-based dynamic programming: only a small square block is computed and shifted down or right greedily (growing or shrinking as needed) instead of the full matrix or a fixed band, using SIMD; the README says this trades some accuracy for speed. |
| **Adoption** | 141 stars, 10 forks; crates.io 0.5.1, about 23k downloads |
| **Last commit** | 2024-06-23 |
| **Links** | [repository](https://github.com/Daniel-Liu-c0deb0t/block-aligner) · [benchmark](https://raw.githubusercontent.com/Daniel-Liu-c0deb0t/block-aligner/HEAD/vis/block_aligner_bench_vis.ipynb) |

## Verdict

In the author's executed notebook (AVX2 build, Rust nightly, CPU not stated, likely an x86-64 Mac), global alignment with traceback at a 1% block took 0.33-29.6 s per dataset versus 2.1-3.4x longer for Edlib, 1.5-2.1x for 1%-banded ksw2 and 5.7-29x for score-only parasail, while exact WFA2 was 8.4x faster on Illumina reads; proteins were 4-9x faster than parasail. A third-party Criterion chart (rchikhi/rust-alignbench, 1 kbp random DNA, block-aligner score-only at a fixed block of 16, no CPU stated) shows block-aligner flat at about 55-57 MB/s from 1% to 10% divergence against WFA2 falling from about 167 to 7.5 MB/s, parasail about 2 MB/s and unbanded ksw2_extz2_sse about 1 MB/s (read from the chart).

## Use it when

- Global alignment with traceback of noisy long reads (Nanopore, roughly 1-50 kbp at 5-15% error) where an exact aligner's time grows with divergence; the author's notebook shows 2.1-3.4x over Edlib and 1.5-2.1x over 1%-banded ksw2.
- Protein alignment with BLOSUM-style matrices or sequence-to-profile (PSSM) alignment, where WFA-family and bit-parallel edit-distance aligners do not apply; the notebook shows 4-9x over parasail on Uniclust30 and SCOP pairs.
- Batches of alignments in one thread that can reuse one Block allocation sized for the longest pair, on x86-64 (AVX2 or SSE2), aarch64 (Neon) or WebAssembly SIMD.
- X-drop extension around seeds when an approximate score and end position are acceptable.

## Skip it when

- You need the guaranteed optimal score: the block placement is heuristic, the README says it trades some accuracy for speed, and the maintainer notes repeats and large gaps can mislead it unless the block is made larger.
- Short, low-divergence reads: in the same notebook exact WFA2 was about 8.4x faster on Illumina reads, and in a third-party benchmark (rchikhi/rust-alignbench, 1 kbp random DNA) WFA2 was about 3x faster at 1% divergence.
- Unit-cost edit distance on long DNA, where exact bit-parallel tools (A\*PA2, Edlib) or, on the 25 kbp Nanopore set, libgaba and the Suzuki-Kasahara difference-recurrence codes (about 2x faster in the notebook, separate harness) are competitive.
- Very long sequences with traceback on limited memory: the trace arrays hold (max_block/16) x (n+m+2+2\*max_block) 32-bit words twice with AVX2, which is about 477 MB for a 50 kbp pair at max block 8192 (derived from Trace::new).
- Large scores: lanes are 16-bit, so very large blocks or scores saturate (README: use a smaller block size); gap penalties are i8 and open must be strictly larger in magnitude than extend.

## How it is fast

Instead of filling the whole DP matrix or a fixed band, it computes only a small square block that greedily shifts right or down depending on which edge holds the larger scores, grows from a saved checkpoint when the scores stall (large gaps, hard regions) and shrinks when a large block is not needed. Each block is filled with SIMD (SSE2, AVX2, Neon or WASM SIMD) using 16-bit score lanes plus 32-bit per-block offsets and a prefix-scan formulation of the gap recurrences, so the computed area stays close to the alignment path. The cost is that the result is heuristic: the block can leave the optimal path and return a suboptimal score.

## Compared with alternatives

Pick block-aligner over A\*PA2, bitdp or Sassy when you need affine gaps with substitution matrices or profiles (proteins, PSSMs) or traceback on noisy long reads and can accept an approximate score; pick A\*PA2 for exact unit-cost long-read alignment, Sassy for pattern search in text, and note that the same author's triple_accel covers only Hamming and Levenshtein and has no measured claim.

## Integration

| | |
|---|---|
| **Form** | crate (block-aligner on crates.io, 0.5.1); C API built from c/ as a static library |
| **Dependencies** | none at runtime (parasailors, rust-wfa2, edlib_rs, ksw2-sys and bio are dev-dependencies for benchmarks only) |
| **Minimum toolchain** | Stable Rust, edition 2018 with const generics (no rust-version declared); nightly Rust and Linux or macOS for tests and benchmarks |
| **Platforms** | x86-64 (SSE2 or AVX2), aarch64 (Neon), wasm32 (SIMD128); selected by Cargo feature at compile time, no runtime detection |
| **Thread safety** | not documented; each Block owns its scratch and trace buffers, so use one instance per thread |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaws in examples/nanopore_bench_global.rs (behind the DNA numbers): the ksw2 scoring matrix is a zeroed 5x5 array with only mat[0]=2 and mat[1]=-4 set, so ksw_extz2_sse scores A:A=+2, A:C=-4 and every other pair 0 and solves a different problem from block-aligner's +2/-4 matrix (fixed-band fill time is probably little affected, but its scores and paths are meaningless); WFA2 runs with penalties mismatch 4, open 4, extend 2, while the WFA equivalent of the shared +2/-4, gap -6/-2 scheme is mismatch 6, open 4, extend 3, so WFA2 solves an easier lower-penalty problem that likely flatters WFA2.
- Parasail is timed score-only (no traceback, which favours parasail) through parasail_nw_striped_profile_sat, the dispatcher that runs the 8-bit kernel first and recomputes at 16 and 32 bits on overflow; kilobase global scores overflow 8 bits, so parasail's times likely include a discarded pass. Timer placement also differs: in the DNA bench Block::new is outside the timer while Edlib and ksw2 allocate inside it; in uc_bench block-aligner's per-pair allocation is inside the timer and only block-aligner gets warm-up runs.
- No runtime CPU dispatch: building without a SIMD feature hits compile_error, the no_simd feature compiles none of the aligner modules, an AVX2 build crashes on CPUs without AVX2, and two SIMD features enabled at once (possible through Cargo feature unification) would re-export L twice (inferred from lib.rs). Block sizes must be powers of two, at least 32 recommended and at most 16384.
- Open bugs with no maintainer reply: #33 returns an empty CIGAR for 1-2 bp sequences when FREE_QUERY_END_GAPS is set, #34 panics with 'Traceback cigar end position must be in bounds!' on a repetitive query containing an N run with free query gaps, and #15 (open since 2022) says traceback became much slower after a gap-traceback correctness fix.

## Known shortcomings

- Downgraded from B to C: the numbers come from the author's own notebook with no CPU model and C/C++ flags unstated; the Bioinformatics 2023 paper is unreachable (snippet only). It compares an approximate aligner against exact ones, parasail ran score-only, WFA2 is about 8.4x faster on Illumina, and libgaba (C) is about 2.3x faster on 25 kbp Nanopore in a separate harness. Stale; paper-access retier candidate.
- Enricher: harness flaws in examples/nanopore_bench_global.rs: the ksw2 scoring matrix is zeroed except mat[0]=2 and mat[1]=-4, so ksw2's scores and paths are meaningless; WFA2 runs with penalties 4/4/2 rather than the equivalent 6/4/3; parasail score-only goes through the _sat dispatcher; timer placement is uneven across tools. Open bugs #33 (empty CIGAR), #34 (traceback panic), #15 (traceback slowdown); trace memory about 477 MB for a 50 kbp pair (derived). Third-party rchikhi/rust-alignbench (Criterion, 1 kbp DNA, no CPU) shows block-aligner flat at about 55-57 MB/s against WFA2 167 to 7.5 MB/s and parasail about 2 MB/s, but block-aligner ran score-only and WFA2 full alignment.

## Caveats and trade-offs

The Bioinformatics paper (Liu and Steinegger 2023, btad487) could not be opened (doi, academic.oup.com, PMC and bioRxiv are blocked here), so the numbers come from the repo's executed benchmark notebook, which the README says reproduces the manuscript experiments; a search-result snippet of the paper abstract says 5-10x faster than some previous methods with under 3% error on protein and long-read data (snippet only). Not like-for-like: block-aligner is an approximate aligner while Edlib (unit-cost edit distance), parasail and WFA2 without heuristic are exact and use different scoring models, and ksw2 is banded; in examples/nanopore_bench_global.rs parasail is called through global_alignment_score (score only, no traceback) while block-aligner, Edlib (EDLIB_TASK_PATH), WFA2 (AlignmentScope::Alignment) and ksw_extz2_sse (score-only flag left at 0) compute a path, which favours parasail; the speedup over parasail grows with length because parasail does full O(nm) DP. WFA2 is far faster than block-aligner on low-error short reads, and on the notebook's 25 kbp Nanopore set the C aligners libgaba and the Suzuki-Kasahara difference-recurrence codes from diff-bench-paper beat it by about 2x (cross-harness, fill time only). The C/C++ baselines are reached through forked binding crates (parasailors, edlib_rs with logging removed, rust-wfa2 fork with 'small changes that ensures wfa2 code autovectorizes', ksw2-sys), so call overhead and build flags may differ from stock builds. Single saved run, no error bars, no CPU model; datasets must be downloaded separately (data/README.md). Lead came from the A\*PA2 enricher (pa-bench lists block-aligner as an approximate aligner); the pa-bench result files were not reachable. Not a language-level claim: the win is algorithmic (adaptive approximate blocks), not Rust codegen. [retier] Enricher: in nanopore_bench_global.rs the ksw2 matrix is zeroed except two cells (scores and paths meaningless), WFA2 runs 4/4/2 instead of the equivalent 6/4/3, parasail score-only goes through the _sat dispatcher, and timers are placed unevenly; open bugs #33, #34, #15.

Heuristic, not exact: the block shifts, grows and shrinks greedily, so it can return a suboptimal score (README: 'at the expense of some accuracy'); block size must be tuned (README: min 32, max 256 for proteins; about 1% and 10% of length for Nanopore reads); 16-bit lanes saturate on very large scores; the SIMD instruction set (SSE2, AVX2, Neon, WASM SIMD) is chosen by Cargo feature at compile time with no runtime detection; tests and benchmarks need nightly Rust; C API available in c/.

## Maintenance

Stale: last release 0.5.1 and last commit 2024-06-23, with 2024-2025 bug reports unanswered, but MIT-licensed, dependency-free and on stable Rust, so usable as a crate if you pin the SIMD feature per target and validate scores on your data.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification B, tier now C.
- **Tier reason:** The numbers come from the author's own executed notebook vis/block_aligner_bench_vis.ipynb (benchmark code in examples/nanopore_bench_global.rs, uc_bench, pssm_bench), with no CPU model and unstated C/C++ build flags, so first-party with partial methodology; the peer-reviewed Bioinformatics 2023 paper that could justify B was unreachable (doi, OUP, PMC, bioRxiv blocked) and is known here only from a search snippet ('5-10x faster than some previous methods'), which the wave rule caps at C.
- **Verifier notes:** Downgrade B to C: tier B rested on a paper nobody could open; the repo notebook is first-party, no CPU model, C/C++ flags unstated. Shortcomings: approximate vs exact aligners, parasail score-only, 8.4x slower than WFA2 on Illumina and about 2x slower than libgaba on 25 kbp Nanopore; stale (last commit 2024-06-23). Candidate for a paper-access retier to B if the Bioinformatics paper's per-tool figures are reached.
- **Fields the verifier corrected:** `claimed_speedup`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-112 (wave 14 seed pass, 2026-10-13); enricher (seed pass, 2026-10-13)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/Daniel-Liu-c0deb0t/block-aligner/HEAD/vis/block_aligner_bench_vis.ipynb>
  - <https://raw.githubusercontent.com/Daniel-Liu-c0deb0t/block-aligner/HEAD/README.md>
  - <https://raw.githubusercontent.com/Daniel-Liu-c0deb0t/block-aligner/HEAD/examples/nanopore_bench_global.rs>
  - <https://github.com/Daniel-Liu-c0deb0t/block-aligner>
  - <https://github.com/Daniel-Liu-c0deb0t/block-aligner/commits>
  - <https://crates.io/api/v1/crates/block-aligner>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/Daniel-Liu-c0deb0t/block-aligner/HEAD/README.md>
  - <https://raw.githubusercontent.com/Daniel-Liu-c0deb0t/block-aligner/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/Daniel-Liu-c0deb0t/block-aligner/HEAD/examples/nanopore_bench_global.rs>
  - <https://raw.githubusercontent.com/Daniel-Liu-c0deb0t/block-aligner/HEAD/examples/uc_bench.rs>
  - <https://raw.githubusercontent.com/Daniel-Liu-c0deb0t/block-aligner/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/Daniel-Liu-c0deb0t/block-aligner/HEAD/src/scan_block.rs>
  - <https://raw.githubusercontent.com/Daniel-Liu-c0deb0t/block-aligner/HEAD/src/avx2.rs>
  - <https://raw.githubusercontent.com/Daniel-Liu-c0deb0t/block-aligner/HEAD/src/scores.rs>
  - <https://raw.githubusercontent.com/Daniel-Liu-c0deb0t/block-aligner/HEAD/vis/block_aligner_bench_vis.ipynb>
  - <https://github.com/Daniel-Liu-c0deb0t/block-aligner/issues?q=is%3Aissue>
  - <https://github.com/Daniel-Liu-c0deb0t/block-aligner/issues/13>
  - <https://github.com/Daniel-Liu-c0deb0t/block-aligner/issues/15>
  - <https://github.com/Daniel-Liu-c0deb0t/block-aligner/issues/33>
  - <https://github.com/Daniel-Liu-c0deb0t/block-aligner/issues/34>
  - <https://crates.io/api/v1/crates/block-aligner>
  - <https://raw.githubusercontent.com/Daniel-Liu-c0deb0t/parasailors-new/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/Daniel-Liu-c0deb0t/parasailors-new/HEAD/src/align.rs>
  - <https://raw.githubusercontent.com/Daniel-Liu-c0deb0t/parasailors-new/HEAD/src/profile.rs>
  - <https://raw.githubusercontent.com/pairwise-alignment/rust-wfa2/HEAD/src/aligner.rs>
  - <https://github.com/rchikhi/rust-alignbench>
  - <https://raw.githubusercontent.com/rchikhi/rust-alignbench/HEAD/README.md>
  - <https://raw.githubusercontent.com/rchikhi/rust-alignbench/HEAD/analysis/out.png>
  - <https://github.com/rchikhi/rust-alignbench/tree/master/benches>
  - <https://raw.githubusercontent.com/rchikhi/rust-alignbench/HEAD/benches/bench.rs>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/daniel-liu-c0deb0t/block-aligner`) · [data/wave14/enrich/raw/github_com_daniel_liu_c0deb0t_block_aligner.json](../../../data/wave14/enrich/raw/github_com_daniel_liu_c0deb0t_block_aligner.json) (enrichment confidence 0.85)

</details>
