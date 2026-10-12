# bitdp (compile-time derived bit-parallel alignment kernels)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Strings and text](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Zig` · `MIT` · 🟢 active

> Zig compile-time generator of bit-parallel linear-gap alignment kernels; batched mode outpaces edlib, ksw2 and parasail on DNA pairs.

| | |
|---|---|
| **Beats** | edlib (C++), ksw2 extz2_sse (C) and parasail scan16/diag16 (C) |
| **Claimed result** | bench/RESULTS.md (medians of three runs, GCUPS, one core, Ryzen 7 8840U under WSL2): on 5,000 random 1 kbp pairs at 15% divergence, batched bitdp 35.20 (4 lanes AVX2) and 34.89 (8 lanes AVX-512) vs edlib 21.73, ksw2 extz2_sse 2.20, parasail scan16 5.19 and diag16 1.98 (1.62x edlib); unbatched bitdp is slower than edlib on every DNA set (18.07 vs 21.73 at 1 kbp, 5.69 vs 6.19 at 150 bp, 4.33 vs 4.42 on reads), so the win needs batching, and the AVX-512 batch is no faster than AVX2. |
| **Workload** | Edit-distance and other linear-gap global alignment of independent DNA pairs (1 kbp and 150 bp sets, real Illumina reads, a 32-guide CRISPR scan of E. coli K-12), measured in GCUPS on one core with every tool's total cost cross-checked. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 7 8840U (Zen 4, AVX-512), Ubuntu under WSL2 (kernel 6.6.114.1), one core, no threading |
| **Compiler and flags** | bitdp: Zig 0.16.0 -Doptimize=ReleaseFast, built twice: -Dcpu=znver4 (AVX-512, 8 lanes of 64 bits) and -Dcpu=x86_64_v3 (AVX2, 4 lanes). Baseline harnesses built with gcc 15.2.0 -O3 -march=native: bench/baselines.c linked against the Ubuntu packages parasail 2.6.2 and edlib 1.2.7 (the libraries themselves are distro builds, their compile flags are not stated, and the Ubuntu parasail has no AVX-512 kernels), and bench/ksw2_baseline.c compiled together with ksw2 commit 289609b (ksw_extz2_sse, 128-bit SSE). BGSA from its repository at commit dffcf9e (2022-02-24), kernels from its own generator, built with make cc=gcc. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Why it wins** | Bit-parallel kernel derived at compile time from the recurrence (14 word operations per column for unit edit costs versus 15 for Myers) with one alignment per SIMD lane for independent pairs. |
| **Adoption** | 0 stars (15 commits) |
| **Last commit** | 2026-09-29 |
| **Links** | [repository](https://github.com/endlessconflict/bitdp) · [benchmark](https://raw.githubusercontent.com/endlessconflict/bitdp/HEAD/README.md) |

## Verdict

On one core of a Ryzen 7 8840U under WSL2, bitdp (Zig 0.16.0 ReleaseFast) in batched AVX2 mode computed unit-cost NW distances for 5,000 random 1 kbp pairs at 15 % divergence at 35.2 GCUPS vs edlib 1.2.7 at 21.7, parasail 2.6.2 scan16 at 5.2 and ksw2 extz2_sse at 2.2 (C harnesses gcc 15.2.0 -O3 -march=native, edlib and parasail from Ubuntu packages), with all cost sums agreeing; on 193,660 real 100 bp E. coli reads the batched margin over edlib is 5.09 vs 4.42 GCUPS, and unbatched bitdp is slower than edlib on every DNA set.

## Use it when

- Verifying many independent short-to-medium DNA pairs at once (read-mapper candidate verification, 100 bp to 1 kbp) where only the cost is needed: batched AVX2 measured 35.2 GCUPS vs edlib 21.7 on 1 kbp pairs and about 15 % ahead of edlib on real 100 bp Illumina reads.
- Scoring schemes no hand-derived bit-vector aligner covers, such as transition/transversion costs or other small integer substitution matrices with linear gaps (tstv 19.2 GCUPS batched AVX2 vs parasail scan16 5.2 and ksw2 0.94 on 1 kbp).
- All-vs-all comparisons of equal-length sequences (the BGSA setting) when you want the same order of speed as BGSA from Zig with an MIT licence.
- Scanning a genome for many short guides or primers (up to 63 nt) in search mode, where `Packed` fits three 20 nt guides per 64-bit lane word.

## Skip it when

- One pair at a time: single-pair bitdp was slower than edlib on every DNA edit workload measured (18.07 vs 21.73 GCUPS on 1 kbp, 5.69 vs 6.19 on 150 bp, 4.33 vs 4.42 on real reads); the win needs enough independent pairs to fill the SIMD lanes.
- Affine gap penalties, local (Smith-Waterman) alignment or anything needing the alignment path or CIGAR: only linear gaps, global and search modes, cost-only output.
- Protein with BLOSUM62: 0.77-0.82 GCUPS vs parasail scan16 2.87, about 3.5x slower, and deriving the kernel takes about 15 s and 375 MB of compiler memory.
- Production or long-lived C/C++ code bases: research code created over two days (15 commits on 2026-09-28/29), no releases or known users, pinned to Zig 0.16.0 and no C API.
- Same-regime competition with hand-tuned kernels: it reaches only 0.73-0.93x of BGSA's Myers speed with AVX2 and trails BGSA's packed BitPAl (8.6 vs 13.0 and 11.7 vs 14.0 GCUPS).

## How it is fast

It reads each DP column as a finite-state machine over bounded score differences, writes the state in thermometer code and shows each threshold bit is a constant, a copy of another bit, or a carry chain that a single integer addition evaluates across 63 rows of a 64-bit word; the Zig compiler derives this program at comptime (Myers' 1999 bit-vector algorithm falls out as the one-chain case, 14 word operations per column vs 15). Wide score ranges use Batcher odd-even merging networks for unary addition, and tiny schemes try exhaustive truth-table synthesis. The headline speed over edlib comes from the batched mode, which runs one independent alignment per 64-bit lane of an AVX2 (4 lanes) or AVX-512 (8 lanes) vector.

## Compared with alternatives

The listed systems-and-safety siblings (ckmeans, zroar, zipir, fucina and others) do no sequence alignment; the closest catalogued alternatives are Sassy (SIMD approximate string matching, beats edlib for pattern search) and A\*PA2 (exact global alignment of long, divergent pairs), so pick bitdp for many short independent pairs or custom linear-gap substitution schemes, Sassy for searching one pattern in a long text and A\*PA2 for single long pairs.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none (Zig standard library only) |
| **Minimum toolchain** | Zig 0.16.0 (build.zig.zon minimum_zig_version; uses the new std.Io API) |
| **Platforms** | Any target Zig supports via portable @Vector code; lane count is std.simd.suggestVectorLength(u64) at compile time, so speed depends on -Dcpu (8 lanes with znver4/AVX-512, 4 with x86_64_v3/AVX2, typically 2 on baseline x86-64 or NEON). Only x86-64 Zen 4 was benchmarked. |
| **Thread safety** | not documented; the API is pure functions plus caller-owned Aligner/Group/Packed state and no globals, so separate instances per thread look safe, but no threaded use is shown |
| **Drop-in for the baseline** | partial — computes the same NW edit distance as edlibAlign(EDLIB_MODE_NW, EDLIB_TASK_DISTANCE) and the same linear-gap global scores as parasail_nw_\* with open = extend, but only from Zig, without traceback, affine gaps or local mode |

## Gotchas

- Bytes outside the scheme's alphabet count as the costliest substitution and the default alphabet is uppercase "ACGT", so lowercase (soft-masked) or N bases are silently penalised unless you uppercase input; the bench scripts uppercase the genome and drop reads with N.
- `Kernel.distance` asserts pattern length below 63 only via std.debug.assert, which ReleaseFast compiles out; longer patterns must go through `Aligner`.
- Harness: bitdp's batched time is one wall-clock interval around `distances`, while edlib and parasail are timed per pair, and edlib 1.2.7 and parasail 2.6.2 are Ubuntu package builds (no AVX-512 kernels in that parasail) against a bitdp built for -Dcpu=znver4 or x86_64_v3; ksw2 extz2_sse and parasail are affine-gap engines run with gap open 0 or open = extend and full bands, so they do more work per cell than a linear-gap kernel. No correctness defect found: every tool's cost sum is cross-checked, and parasail's striped kernels were dropped because they returned non-optimal scores with open = extend.
- AVX-512 does not help in batched pairwise mode (7.11 vs 7.75 GCUPS on 150 bp, 4.59 vs 5.09 on real reads, 34.89 vs 35.20 on 1 kbp) because each lane gathers its planes separately; the 0.30 s vs 13.3 s genome scan is forward strand only and is measured against the repo's plain scalar reference loop, not an optimised aligner.

## Known shortcomings

- Batched SIMD against per-pair edlib, ksw2 and parasail; against BGSA (C++, same batched regime) only 0.73-1.20x; edlib and parasail are Ubuntu package builds; the 13.3 s genome scan baseline is bitdp's own scalar reference loop; AVX2 build is -Dcpu=x86_64_v3.
- Correction: unbatched bitdp is slower than edlib on every DNA set (18.07 vs 21.73 GCUPS at 1 kbp, 5.69 vs 6.19 at 150 bp, 4.33 vs 4.42 on reads), not only at 150 bp, so the win needs batching; the AVX-512 batch is no faster than AVX2. edlib and parasail are Ubuntu builds; ksw2 and parasail run as affine engines; the genome scan is forward strand only against a scalar loop. All tools' cost sums agree (no correctness bug). Category moved to string-and-text (alignment kernels sit with Sassy and A\*PA2).

## Caveats and trade-offs

Single author, single machine (Ryzen 7 8840U under WSL2). The comparison is batched SIMD lanes (one alignment per lane) against single-pair tools, a different regime from edlib's per-pair banded algorithm; on 150 bp pairs a single bitdp pair is slower than edlib. Against BGSA, the closest same-regime tool (C++, hand-derived kernels), bitdp reaches only 0.73-1.20 of its speed for edit distance and trails BGSA's packed BitPAl, so the win over C/C++ comes from batching and the derived kernel, not from Zig. edlib and parasail are Ubuntu package builds, not rebuilt at -O3 -march=native; parasail's NW kernels are affine-gap kernels run with open = extend for linear gaps. parasail's striped kernels were excluded because they returned wrong costs on some pairs (426 of 100,000 on the 150 bp edit set). The 13.3 s genome-scan figure is the repo's own scalar reference loop. Research code, API not stable. [retier] Unbatched bitdp is slower than edlib on every DNA set, not only at 150 bp; the AVX-512 batch is no faster than AVX2. edlib and parasail are Ubuntu builds; ksw2 and parasail run as affine engines; the genome scan is forward strand only against a scalar loop. All tools' cost sums agree.

Research code, not yet stable; global and search modes with linear gap costs only; at most 32 distinct score differences and 24 substitution costs; compile-time derivation takes seconds to about 15 s (375 MB of compiler memory for BLOSUM62); batched mode needs many independent pairs to fill SIMD lanes.

## Maintenance

Brand-new research code (15 commits on 2026-09-28 and 2026-09-29, 0 stars, no releases, no issues), MIT-licensed and small (about 1,700 lines across src/root.zig, derive.zig, schemes.zig and reference.zig) so it is easy to vendor into a Zig project, but its API is declared unstable and it targets Zig 0.16.0 (minimum_zig_version) and its new std.Io API.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** Public benchmark code (bench/baselines.c, bench/ksw2_baseline.c, bench/gen.py, the bitdp-bench build step, reproduction commands in bench/README.md), compilers and flags (Zig 0.16.0 ReleaseFast with -Dcpu=znver4 or -Dcpu=x86_64_v3; gcc 15.2.0 -O3 -march=native for the C harnesses) and CPU (Ryzen 7 8840U) are all stated in bench/RESULTS.md, and every tool's total cost is cross-checked; the README's headline numbers (35.2 vs 21.7 / 2.2 / 5.2 GCUPS, 15 % over edlib on real reads, 0.30 s vs 13.3 s) appear in RESULTS.md.
- **Verifier notes:** Numbers verified in README Speed and bench/RESULTS.md; harness code (baselines.c with edlibAlign k=-1 EDLIB_MODE_NW distance task, parasail_nw_\* with open=extend) opened. Fixed compiler_and_flags (AVX2 build is -Dcpu=x86_64_v3; the C harness is gcc 15.2.0 -O3 -march=native but edlib/parasail libraries are Ubuntu builds) and added the BGSA same-regime comparison, which shows no consistent win. Metadata (MIT, 0 stars, 15 commits, last commit 2026-09-29, active) checked; same_algorithm stays false, same_opt_level left null (ksw2 and harness at -O3 -march=native, edlib and parasail distro builds).
- **Fields the verifier corrected:** `compiler_and_flags`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-64 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/endlessconflict/bitdp/HEAD/README.md>
  - <https://raw.githubusercontent.com/endlessconflict/bitdp/HEAD/bench/RESULTS.md>
  - <https://raw.githubusercontent.com/endlessconflict/bitdp/HEAD/bench/README.md>
  - <https://raw.githubusercontent.com/endlessconflict/bitdp/HEAD/bench/baselines.c>
  - <https://raw.githubusercontent.com/endlessconflict/bitdp/HEAD/bench/ksw2_baseline.c>
  - <https://raw.githubusercontent.com/endlessconflict/bitdp/HEAD/bench/gen.py>
  - <https://github.com/endlessconflict/bitdp>
  - <https://github.com/endlessconflict/bitdp/commits>
- **Sources the enricher read:**
  - <https://github.com/endlessconflict/bitdp>
  - <https://github.com/endlessconflict/bitdp/commits>
  - <https://github.com/endlessconflict/bitdp/issues?q=is%3Aissue>
  - <https://github.com/endlessconflict/bitdp/tree/main/src>
  - <https://github.com/endlessconflict/bitdp/tree/main/bench>
  - <https://raw.githubusercontent.com/endlessconflict/bitdp/HEAD/README.md>
  - <https://raw.githubusercontent.com/endlessconflict/bitdp/HEAD/REFERENCES.md>
  - <https://raw.githubusercontent.com/endlessconflict/bitdp/HEAD/bench/RESULTS.md>
  - <https://raw.githubusercontent.com/endlessconflict/bitdp/HEAD/bench/README.md>
  - <https://raw.githubusercontent.com/endlessconflict/bitdp/HEAD/bench/baselines.c>
  - <https://raw.githubusercontent.com/endlessconflict/bitdp/HEAD/bench/ksw2_baseline.c>
  - <https://raw.githubusercontent.com/endlessconflict/bitdp/HEAD/bench/gen.py>
  - <https://raw.githubusercontent.com/endlessconflict/bitdp/HEAD/bench/bench.zig>
  - <https://raw.githubusercontent.com/endlessconflict/bitdp/HEAD/bench/scan.zig>
  - <https://raw.githubusercontent.com/endlessconflict/bitdp/HEAD/bench/reads.py>
  - <https://raw.githubusercontent.com/endlessconflict/bitdp/HEAD/src/root.zig>
  - <https://raw.githubusercontent.com/endlessconflict/bitdp/HEAD/src/derive.zig>
  - <https://raw.githubusercontent.com/endlessconflict/bitdp/HEAD/src/schemes.zig>
  - <https://raw.githubusercontent.com/endlessconflict/bitdp/HEAD/src/reference.zig>
  - <https://raw.githubusercontent.com/endlessconflict/bitdp/HEAD/build.zig>
  - <https://raw.githubusercontent.com/endlessconflict/bitdp/HEAD/build.zig.zon>
  - <https://github.com/sdu-hpcl/BGSA>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/endlessconflict/bitdp`) · [data/wave14/enrich/raw/github_com_endlessconflict_bitdp.json](../../../data/wave14/enrich/raw/github_com_endlessconflict_bitdp.json) (enrichment confidence 0.8)

</details>
