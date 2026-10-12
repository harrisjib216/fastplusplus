# ksw2

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [SIMD intrinsics libraries](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🔴 abandoned

> SSE2/SSE4.1 global and extension DNA alignment (minimap2's kernel) using Suzuki-Kasahara 8-bit difference DP; beats parasail's 32-bit striped global aligners.

| | |
|---|---|
| **Beats** | parasail (global Needleman-Wunsch, striped/scan/diagonal SIMD variants) and ksw2's own scalar Green-formulation DP (ksw2_gg) |
| **Claimed result** | README Performance Analysis table, 50k pair, global score-only: ksw2 scalar `-t gg -s` 7.3 s; parasail `ps_nw_striped_32` (SSE4) 2.2 s, SSE2 striped 2.9 s, scan and diag 3.0 s; ksw2 `-t extz2_sse -sg` 0.96 s (SSE2) and 0.84 s (SSE4) (about 2.6x faster than parasail's best row and 8.7x faster than scalar gg for SSE4, derived from page data). With extension and Z-drop (`-t extz2_sse -s`) 3.0 s (SSE2) and 2.7 s (SSE4), which is slower than parasail's 2.2 s global row. 16.5k pair with CIGAR: `-t gg` 1.6 s, `-t extz2_sse` 0.40 s (about 4x, derived), `-t extz2_sse -g` 0.18 s. |
| **Workload** | Global affine-gap alignment of two long DNA sequence pairs (a 50k pair and a 16.5k pair in the repo's test directory), wall time in seconds, score-only or with CIGAR as marked in the table. |
| **Metric** | throughput |
| **Compiler and flags** | Makefile default: gcc -g -Wall -Wextra -Wc++-compat -O2 -march=native (SSE4.1 when available; `make sse2=1` for SSE2 only). The README does not say which compiler or flags produced the table. |
| **Adoption** | 144 stars; component of minimap2 |
| **Last commit** | 2023-06-27 |
| **Links** | [repository](https://github.com/lh3/ksw2) · [benchmark](https://github.com/lh3/ksw2/blob/master/README.md) |

## Verdict

README table, one run each, wall time in seconds. On the 50 kb phage pair (test/t2.fa.gz against test/q2.fa.gz, phage50k_ref and phage50k_mut90 per issue #3), global score only: ksw_extz2_sse with -sg takes 0.84 s (SSE4.1) and 0.96 s (SSE2), against 2.2 s for parasail nw_striped_32 (2.6x, derived from page data) and 7.3 s for ksw2's scalar Green DP (8.7x). On the 16.5 kb mitochondrial pair with CIGAR: 0.40 s against 1.6 s scalar, and 0.18 s with -g. CPU, compiler, parasail version and scoring parameters are not stated; the CLI defaults are match 2, mismatch -4, gap open 4, extend 2, and the Makefile builds with gcc -O2 -march=native.

## Use it when

- Long DNA or nucleotide pairs (kilobases to tens of kilobases) with simple match/mismatch scoring where you need a global score or a Z-drop extension, e.g. read-to-reference extension as in minimap2
- Score-only global alignment of long pairs on x86 SSE4.1: the README's 50 kb pair runs in 0.84 s against 2.2 s for parasail's best SSE4 row
- Banded alignment with CIGAR (left- or right-aligned gaps) when you can bound the band width, which keeps traceback memory proportional to sequence length times band
- Two-piece affine gaps (ksw_extd2_sse) to keep long indels from being split, or splice-aware alignment (ksw_exts2_sse)
- Projects that want to vendor two files (ksw2.h plus one ksw2_\*.c, MIT) with no dependencies

## Skip it when

- Local (Smith-Waterman) alignment or protein alignment with a full substitution matrix: no local mode, and the SSE kernels assume one match and one mismatch score (KSW_EZ_GENERIC_SC exists but the README says diagonal vectorisation is harder with generic matrices); use parasail or SSW
- Traceback on long unbanded pairs: the direction matrix takes about (qlen+tlen) x min(qlen,tlen) bytes, so a 50 kb pair with CIGAR needs gigabytes; in issue #3 that run segfaulted from an integer overflow and the maintainer declined to fix it ('not worth increasing the peak memory')
- Highly similar long sequences, where edit-distance or wavefront methods with dynamic banding (edlib, WFA2-lib) do far less work; the README itself points to edlib's dynamic banding
- Targets without x86 SSE2: there are no AVX2, AVX-512 or NEON kernels here (avx2=1 only adds -mavx2), and only ksw2_extd2_sse.c has a USE_SIMDE switch
- Code that needs a maintained upstream: this repository has had no commits since 2023-06-27, and correctness issues are open (#28 banded extd2_sse reports a score above the unbanded optimum, 1084 against 1078; #19 ksw_extd with tlen &gt; qlen + w; #15 segfault in ksw_exts2_sse)

## How it is fast

Suzuki and Kasahara's difference recurrence stores the differences between neighbouring DP cells instead of absolute scores. The differences are bounded by the match and gap scores, so they fit in int8 lanes and one 128-bit register holds 16 cells whatever the total alignment score; parasail needs 32-bit lanes (4 per register) on 50 kb inputs. Cells are processed along anti-diagonals so the lanes in a vector have no dependency on each other, and SSE4.1 blendv/max replace the SSE2 emulation. Global score-only mode (-g, approximate max) stays 16-way through the whole inner loop; tracking the exact maximum for extension needs a 32-bit H array updated 4-way, which is why -s rows are about 3x slower than -sg.

## Compared with alternatives

Pick ksw2 over parasail for long DNA with match/mismatch scoring when you need global or Z-drop extension alignment with a CIGAR; parasail wins on scoring generality, local and semi-global modes and wider SIMD. SSW covers local alignment with CIGAR, and WFA2-lib (which uses ksw2_extz2_sse as its baseline) is the better choice when the sequences are highly similar.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (optional kalloc memory pool via HAVE_KALLOC; the ksw2-test CLI needs zlib; parasail and gaba only for the comparison build) |
| **Minimum toolchain** | C compiler with SSE2 intrinsics (Makefile: gcc -O2 -march=native, -Wc++-compat so it also builds as C++); SSE4.1 optional at compile time, KSW_SSE2_ONLY forces SSE2 |
| **Platforms** | x86 and x86-64 with SSE2 (SSE4.1 faster); KSW_CPU_DISPATCH hooks exist but the dispatcher file is not in this repo |
| **Thread safety** | Functions keep no static or global state (none in ksw2_extz2_sse.c or ksw2_extd2_sse.c) and allocate from the caller's km pool, so separate threads with separate pools and ksw_extz_t structs are safe; kalloc's own thread safety is not documented |
| **Drop-in for the baseline** | no |

## Gotchas

- ksw_extz2_sse returns without computing anything when -min_sc &gt; 2\*(q+e) (ksw2_extz2_sse.c line 82), i.e. when the mismatch penalty exceeds twice the gap-open-plus-extend cost, so ez keeps whatever it held before; initialise ez and keep mismatch penalties modest. Scores and penalties are int8 and mat[0] + 2\*(q+e) must fit in an int8 lane.
- When the wildcard (last) matrix entry is 0, as ksw_gen_simple_mat and the README example produce, the SSE kernel scores N as -e, not 0 (line 68 sets sc_N_ to -e), so ksw_extz2_sse and the scalar ksw_extz give different scores on sequences containing N (issue #11). Issue #25 (open) reports ez-&gt;mte_q set from en where en0 was meant.
- The fastest README rows use -g (KSW_EZ_APPROX_MAX | KSW_EZ_APPROX_DROP): the global end score is built by summing exact cell differences along a path to the corner, and the code comment says only the tracked maximum and Z-drop become approximate, so extension callers that need the exact max must drop -g and pay about 3x (2.7 s against 0.84 s on the 50 kb pair).
- Benchmark harness (cli.c): there is no internal timer, so the table is presumably whole-process wall time of one run, including gzip parsing, encoding and per-call calloc. parasail gets parasail_matrix_create("ACGTN", match, mismatch), which scores N against N as a match where ksw2 gives 0 (a TODO in the code); that does not matter for the N-free test pairs. parasail's nw_striped_32 is a dispatcher that would pick AVX2 on an AVX2 machine, and the CPU is not named.

## Known shortcomings

- The README table (0.84 s vs parasail 2.2 s) gives no CPU or compiler, only the global score-only mode beats parasail and with a simpler scoring model; abandoned since 2023-06-27; the minimap2 paper's about 3x over parasail (snippet only) could move it to B.
- Enricher: no timer in the harness (whole-process, one run, CPU unnamed); parasail's N scoring differs (TODO in cli.c), harmless on N-free test data. Code gotchas: extz2_sse returns silently when -min_sc &gt; 2\*(q+e); N is scored -e when the matrix wildcard is 0 (#11); open issues #28 (banded extd2_sse score above the optimum), #25, #19, #15; a 50 kbp pair with CIGAR segfaults (#3, wontfix).

## Caveats and trade-offs

No CPU model, compiler or flags are stated for the timing table, so tier C. The README itself says KSW2 is faster than parasail 'partly because' KSW2 uses one score for all matches and another for mismatches while parasail takes a generic matrix, so the comparison is not quite the same task. The parasail rows are 32-bit-lane variants (ps_nw_\*_32), the widths that do not saturate on 50 kb sequences; ksw2's Suzuki-Kasahara difference formulation keeps 8-bit lanes, which is the source of its win. Rows differ in what they compute (score-only global vs extension with Z-drop; the parasail rows do not list `-s` but report no CIGAR), and only the global score-only rows (0.96 s SSE2, 0.84 s SSE4) beat parasail's best 2.2 s; the extension rows (3.0 s and 2.7 s) are slower than parasail's global row. Test data are checked in (test/ has MT-human.fa, MT-orang.fa, q1.fa, t1.fa and gzipped q2 and t2; which files are the 50k and 16.5k pairs was not confirmed) so the table can be rerun on your own CPU with `make parasail=prefix`. A search snippet of the minimap2 preprint says the implementation is about three times as fast as parasail's 4-way vectorization for global alignment (snippet only, not verified in the published paper). Last commit 2023-06-27 (about 3.3 years ago); minimap2 carries its own copy of these sources. The Suzuki-Kasahara BMC Bioinformatics 2018 and minimap2 Bioinformatics 2018 papers were not opened (arXiv and publisher sites blocked).

Global alignment and extension (Z-drop) only, no local alignment; SSE2 and SSE4.1 intrinsics documented in the README (the Makefile only offers an avx2=1 compile flag, no NEON); fixed banding; affine and dual (two-piece) affine gap costs; supports CIGAR with left or right gap alignment. Suzuki-Kasahara diagonal formulation needs a single match score and a single mismatch score.

## Maintenance

Abandoned upstream since 2023-06-27 (last change: an int-overflow fix in gg2_sse allocation), with 2022 commits syncing it from minimap2, whose copy is the maintained one; MIT and two files to vendor, but check the open banded-score and segfault issues before relying on ksw_extd/ksw_exts2.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README Performance Analysis table against parasail and ksw2's own scalar DP; the test data and cli.c harness are in the repo and the Makefile shows default flags, but the table names no CPU, compiler or flags used. The minimap2 paper's \~3x-vs-parasail statement was seen only as a search snippet (preprint wording), so no B.
- **Verifier notes:** Confirmed at C; README table numbers match (0.84 s SSE4 extz2_sse -sg vs parasail ps_nw_striped_32 2.2 s, 2.6x derived; 8.7x vs scalar gg). Shortcomings: no CPU or compiler for the table, only the global score-only mode beats parasail, scoring model simpler than parasail's generic matrix, abandoned since 2023-06-27. Possible B via the minimap2 paper if a paper-access retier confirms the \~3x-vs-parasail sentence in the published version.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-126 (wave 13 seed pass, 2026-10-13); enricher (seed pass, 2026-10-13)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/lh3/ksw2/HEAD/README.md>
  - <https://raw.githubusercontent.com/lh3/ksw2/HEAD/Makefile>
  - <https://raw.githubusercontent.com/lh3/ksw2/HEAD/LICENSE.txt>
  - <https://github.com/lh3/ksw2>
  - <https://github.com/lh3/ksw2/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/lh3/ksw2/HEAD/README.md>
  - <https://raw.githubusercontent.com/lh3/ksw2/HEAD/Makefile>
  - <https://raw.githubusercontent.com/lh3/ksw2/HEAD/ksw2.h>
  - <https://raw.githubusercontent.com/lh3/ksw2/HEAD/cli.c>
  - <https://raw.githubusercontent.com/lh3/ksw2/HEAD/ksw2_extz2_sse.c>
  - <https://raw.githubusercontent.com/lh3/ksw2/HEAD/ksw2_extd2_sse.c>
  - <https://raw.githubusercontent.com/lh3/ksw2/HEAD/test/MT-human.fa>
  - <https://github.com/lh3/ksw2/issues?q=is%3Aissue>
  - <https://github.com/lh3/ksw2/issues/3>
  - <https://github.com/lh3/ksw2/issues/11>
  - <https://github.com/lh3/ksw2/issues/25>
  - <https://github.com/lh3/ksw2/issues/28>
  - <https://github.com/lh3/ksw2/commits>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/lh3/ksw2`) · [data/wave13/enrich/raw/github_com_lh3_ksw2.json](../../../data/wave13/enrich/raw/github_com_lh3_ksw2.json) (enrichment confidence 0.75)

</details>
