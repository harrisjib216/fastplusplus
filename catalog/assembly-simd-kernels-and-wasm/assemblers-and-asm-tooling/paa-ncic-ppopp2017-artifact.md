# KeplerAs and SGEMM assembly (PPoPP 2017 artifact)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Assemblers and assembly tooling](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `SASS assembly kernels plus an assembler (implementation language not confirmed; README says KeplerAs is based on MaxAs)` · `No repository-wide licence. KeplerAs/LICENSE is MIT (Copyright 2014 Scott Gray, 2015\~2016 Xiuxia Zhang); the SGEMM .sass kernels carry 'Copyright 2015\~2017 Xiuxia Zhang ... All rights reserved' lines (commit 'Added licence information', 2017-05-24), and one kernel file carries an Apache-2.0 header.` · 🔴 abandoned

> Kepler (sm_35) SASS assembler plus hand-scheduled SGEMM kernels that beat cuBLAS 7.0 by up to 1.15x on a Tesla K20m.

| | |
|---|---|
| **Beats** | NVIDIA cuBLAS 7.0 SGEMM (and cuDNN v4.0 for the convolution kernel), i.e. NVIDIA's library kernels built by NVIDIA's own toolchain |
| **Claimed result** | Paper (sgemm.pdf in the repo): at 12288 x 12288 the hand-assembled SGEMM reaches 3.1 Tflop/s (88% of peak) versus cuBLAS 7.0 at 2.7 Tflop/s (76%), a 1.15x speedup; convolution kernel 39%, 46% and 62% faster than cuDNN v4.0 for three CNN configurations. |
| **Workload** | Single-precision GEMM on an NVIDIA Tesla K20m, square matrices 384 to 12288 (step 384) and rectangular shapes, plus a convolution kernel on the same GPU (batch size 128). |
| **Metric** | throughput |
| **Hardware** | NVIDIA Tesla K20m (Kepler, 13 SMs); host CPU model not stated in the paper text read |
| **Compiler and flags** | cuBLAS from CUDA 7.0 as the baseline; the optimized kernels are written directly in SASS and assembled with KeplerAs, so no nvcc flags apply. Compiler flags for any host harness are not stated on the pages opened. |
| **Adoption** | 87 stars |
| **Last commit** | 2019-10-08 |
| **Links** | [repository](https://github.com/PAA-NCIC/PPoPP2017_artifact) · [benchmark](https://raw.githubusercontent.com/PAA-NCIC/PPoPP2017_artifact/HEAD/sgemm.pdf) |

## Verdict

PPoPP 2017 paper (sgemm.pdf in the repo) on an NVIDIA Tesla K20m against cuBLAS from CUDA 7.0: the 12x12-blocked SASS SGEMM reaches 3.1 Tflop/s (88% of a 3520 Gflop/s peak) versus 2.7 Tflop/s (76%) at 12288x12288x12288, 1.15x, and beats cuBLAS 'in most cases' over square sizes 384-12288 (step 384) and four rectangular shapes; convolution kernels average 39%, 46% and 62% above cuDNN v4.0 on AlexNet, VGG-A and OverFeat layers (batch 128). The public harness behind the SGEMM figures times one cold launch per size with CUDA events.

## Use it when

- Studying or teaching GPU microarchitecture-level tuning: dual-issue control codes, register-bank conflicts and load-width choices, with a worked SGEMM and the paper's microbenchmark methodology.
- Squeezing single-precision GEMM on legacy GK110-class Kepler (sm_35) GPUs such as the Tesla K20m, where the paper reports 3.1 versus 2.7 Tflop/s over cuBLAS 7.0 for large square matrices.
- Reverse-engineering another NVIDIA ISA encoding: the Solver scripts ship sm_35 and sm_52 inputs and are the reusable part of the toolchain.
- Large matrices (the paper's gains grow with size; 12x12 blocking wins above about 1000, 8x8 at small sizes).

## Skip it when

- Any GPU newer than Kepler: KeplerAs refuses cubins that are not sm_35 ('Cubin not in sm_35'), and Maxwell and later use different encodings; use MaxAs (Maxwell/Pascal) or TuringAs (Volta/Turing/Ampere) instead.
- As a cuBLAS replacement in an application: no BLAS API, fixed 192x192/128x128 tiles, kernel-specific parameter blocks (lda8-style strides), and edge handling for sizes that are not tile multiples is not documented (all tested sizes are multiples of 192 or 128).
- Convolution: the kernels behind the 39-62% over cuDNN v4.0 claim are not in the repository.
- Small matrices on a 13-SM K20m: a 384x384 problem launches only 4 thread blocks and is load-imbalanced, per the paper.
- Anything needing support or a modern toolchain: code last changed 2017-05-24, CUDA 7.0 and cuDNN 4.0 era.

## How it is fast

Bare-metal scheduling that nvcc/ptxas did not do on Kepler: control codes set so that FFMA pairs dual-issue (the paper's pattern issues six FFMAs per four clocks), registers allocated to avoid register-bank conflicts (four-aligned quads for LDS.128), non-FFMA instructions placed where they cost little, and global/shared load widths (LDG.128, LDS.64 versus LDS.128) chosen to stay off the shared-memory roofline. Blocking is two-level, 192x192 shared-memory tiles with 12x12 register tiles (or 128x128 with 8x8), double-buffered in shared memory and registers, the same structure as MaxAs's Maxwell SGEMM it derives from.

## Compared with alternatives

Among the SASS assemblers already listed, MaxAs covers Maxwell/Pascal and TuringAs covers Volta/Turing/Ampere; pick KeplerAs only for sm_35 Kepler hardware or for its ISA-encoding solver, which neither sibling ships.

## Integration

| | |
|---|---|
| **Form** | source-drop (SASS kernel files assembled with the KeplerAs Perl tool into a cubin, loaded via the CUDA driver API) |
| **Dependencies** | Perl 5.10+ with Carp and Data::Dumper (KeplerAs/Makefile.PL, installed with 'perl Makefile.PL; make; sudo make install'); CUDA toolkit with nvcc to build the template cubin (nvcc -arch sm_35 -m 64 -cubin) and cuobjdump/nvdisasm for the solver and test modes; cuBLAS and the CUDA driver/runtime for the harness (nvcc -o sgemm sgemm.cpp -lcudart -lcuda -lcublas) |
| **Minimum toolchain** | Perl 5.10; CUDA 7.0 was the paper's baseline toolkit; newer toolkits not documented |
| **Platforms** | NVIDIA Kepler sm_35 only (tested on Tesla K20m); Linux shell scripts |
| **Thread safety** | not documented (stateless GPU kernels; the harnesses are single-threaded host programs) |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw: each sgemm.cpp times a single launch of each side (iterations = 1 in the NN and NT harnesses, 10 in TN) with CUDA events and no warm-up, the cuBLAS call is the first one after cublasCreate, and NT/sgemm.sh runs every size in a fresh process ('sleep 5' between sizes), so every number is one cold sample; GPU clocks are not pinned or stated (the paper's 88% uses a 3520 Gflop/s peak).
- Baseline layout asymmetry: the NN harness computes its row-major C with cublasSgemm(CUBLAS_OP_T, CUBLAS_OP_T, ...) writing a column-major C (checked through transposed indexing) instead of the operand-swapped CUBLAS_OP_N/CUBLAS_OP_N call, so cuBLAS ran a different transposition variant than the kernel; its speed relative to cuBLAS's NN path is not shown. The NN 8x8 harness passes lda = M and ldb = K to that transposed call, which does not fit the transposed shapes when M &lt; K or K &lt; N (three of the paper's four rectangular shapes), and no harness checks the cuBLAS return status.
- The correctness check requires bitwise-equal floats against cuBLAS (C[index] != cublasC[indexT]) and only prints 'Passed' or 'Error'; the paper does not report its outcome.
- KeplerAs constraints: it patches an existing nvcc-compiled template cubin whose kernel signature must match the SASS parameter mapping; kernel size must be a multiple of 8 instructions, at most 255 registers and 16 barriers; LDS.128 destinations need a register index divisible by 4 or the GPU raises illegal-instruction errors (paper, Section 4.1). Its POD still calls it an 'Assembler for NVIDIA Maxwell architecture', inherited from MaxAs.

## Known shortcomings

- No harness in the artifact and the convolution code is absent; the cuBLAS 7.0 baseline is obsolete (3.1 vs 2.7 Tflop/s, 1.15x); KeplerAs is MIT but the SGEMM kernels are "All rights reserved" (mixed).
- Record corrections: a timing harness does exist (SGEMM/\*/sgemm.cpp with Makefiles and NT/sgemm.sh), and every kernel .sass opened is Apache-2.0 (usability copyable). Harness flaws: one cold launch per size with no warm-up (iterations = 1 in the NN and NT harnesses); cuBLAS is called OP_T/OP_T with a column-major C instead of the operand-swapped OP_N/OP_N call, so it ran a different transposition variant; the NN 8x8 harness passes lda = M and ldb = K, which do not fit the shapes when M &lt; K or K &lt; N; the cuBLAS status is never checked; the result check needs bitwise-equal floats.

## Caveats and trade-offs

This is a peer-reviewed PPoPP 2017 paper ('Understanding the GPU Microarchitecture to Achieve Bare-Metal Performance Tuning', originally 'Demystifying GPU Microarchitecture to Tune SGEMM'), but the repo has no benchmark harness, timing code or run scripts, and the convolution kernels behind the cuDNN claim are not in the repo at all (only KeplerAs, SGEMM and Solver directories). The paper says the 12x12 and 8x8 kernels beat cuBLAS 'in most cases' (8x8 is better at small sizes, the gain grows with matrix size), so 1.15x is the best large-matrix figure, not a uniform one. cuBLAS 7.0 and cuDNN 4.0 (2015-2016) and the Kepler-only ISA encoding are long obsolete. KeplerAs is a Perl assembler (Makefile.PL, lib/KeplerAs) derived from Scott Gray's MaxAs, which is listed separately in wave 13; the measured artifact is hand-written SASS against a vendor library, not an assembler-versus-assembler test. The kernels are 'All rights reserved' and only the assembler is MIT. [retier] Peer-reviewed PPoPP 2017 paper ('Understanding the GPU Microarchitecture to Achieve Bare-Metal Performance Tuning'); the repo holds KeplerAs, the SGEMM kernels (.sass files with Apache-2.0 headers) and a timing harness (SGEMM/\*/sgemm.cpp with Makefiles and NT/sgemm.sh), but not the convolution kernels behind the cuDNN claim. Harness flaws: each sgemm.cpp times a single launch of each side with CUDA events and no warm-up (iterations = 1 in the NN and NT harnesses, 10 in TN), the cuBLAS call is the first after cublasCreate, NT/sgemm.sh runs every size in a fresh process, and GPU clocks are not pinned or stated (the paper's 88% uses a 3520 Gflop/s peak). Baseline layout asymmetry: the NN harness computes its row-major C with cublasSgemm(CUBLAS_OP_T, CUBLAS_OP_T, ...) writing a column-major C instead of the operand-swapped OP_N/OP_N call, so cuBLAS ran a different transposition variant, and the NN 8x8 harness passes lda = M and ldb = K, which do not fit the transposed shapes when M &lt; K or K &lt; N; the cuBLAS status is never checked and the correctness check requires bitwise-equal floats and only prints 'Passed' or 'Error' (outcome not reported in the paper). The paper says the 12x12 and 8x8 kernels beat cuBLAS 'in most cases' (8x8 better at small sizes, the gain grows with matrix size), so 1.15x is the best large-matrix figure. cuBLAS 7.0 and cuDNN 4.0 (2015) have long been superseded. KeplerAs patches an nvcc-compiled template cubin whose kernel signature must match the SASS parameter mapping (kernel size a multiple of 8 instructions, at most 255 registers and 16 barriers; LDS.128 destinations need a register index divisible by 4); its POD still calls it an assembler for Maxwell, inherited from MaxAs.

Kepler-only SASS (the ISA encoding was cracked for Kepler and differs from Maxwell); kernels and the assembler do not carry over to newer GPUs. The same research line produced MaxAs (Maxwell/Pascal) and TuringAs (Volta/Turing/Ampere).

## Maintenance

Abandoned research artifact (code last changed 2017-05-24, README edits 2019-10-08) for obsolete Kepler hardware; corrections to the record: a timing harness does exist (SGEMM/\*/sgemm.cpp with Makefiles and NT/sgemm.sh), and every kernel file opened (NN and TN, 12x12 and 8x8, plus the common include) carries an Apache-2.0 header (copyright Nervana Systems 2014 and Xiuxia Zhang 2015-2017), with KeplerAs and Solver under MIT, so the code is copyable rather than mixed.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification B, tier now B.
- **Tier reason:** The PPoPP 2017 paper (sgemm.pdf in the repo, ACM ISBN 978-1-4503-4493-7) states on a Tesla K20m that the SGEMM reaches 3.1 Tflop/s (88%) against cuBLAS 7.0's 2.7 Tflop/s (76%) at 12288 x 12288, a 1.15x speedup, and that the convolution is 39%, 46% and 62% faster than cuDNN v4.0. It is peer-reviewed, but the repo holds only the .sass kernels, the assembler and the solver, with no timing harness or run scripts, so it is not A.
- **Verifier notes:** Numbers verified in the repo's sgemm.pdf (pdftotext): 3.1 vs 2.7 Tflop/s, 88% vs 76%, 1.15x, and 39%/46%/62% over cuDNN v4.0. Not a duplicate of MaxAs (NervanaSystems/maxas): KeplerAs targets a different ISA (Kepler) using encodings from the authors' solver and has its own paper claim. Usability moved to mixed: MIT assembler, all-rights-reserved kernels.
- **Fields the verifier corrected:** `license`, `usability`, `hardware`, `caveats`
- **Shortcomings recorded by:** verifier batch-51 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/PAA-NCIC/PPoPP2017_artifact>
  - <https://github.com/PAA-NCIC/PPoPP2017_artifact/commits/master>
  - <https://github.com/PAA-NCIC/PPoPP2017_artifact/commit/8a8de27>
  - <https://github.com/PAA-NCIC/PPoPP2017_artifact/tree/master/SGEMM>
  - <https://github.com/PAA-NCIC/PPoPP2017_artifact/tree/master/SGEMM/NN>
  - <https://github.com/PAA-NCIC/PPoPP2017_artifact/tree/master/KeplerAs>
  - <https://raw.githubusercontent.com/PAA-NCIC/PPoPP2017_artifact/HEAD/sgemm.pdf>
  - <https://raw.githubusercontent.com/PAA-NCIC/PPoPP2017_artifact/HEAD/README.md>
  - <https://raw.githubusercontent.com/PAA-NCIC/PPoPP2017_artifact/HEAD/KeplerAs/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/PAA-NCIC/PPoPP2017_artifact>
  - <https://github.com/PAA-NCIC/PPoPP2017_artifact/commits/master>
  - <https://raw.githubusercontent.com/PAA-NCIC/PPoPP2017_artifact/HEAD/README.md>
  - <https://raw.githubusercontent.com/PAA-NCIC/PPoPP2017_artifact/HEAD/sgemm.pdf>
  - <https://github.com/PAA-NCIC/PPoPP2017_artifact/tree/master/KeplerAs>
  - <https://raw.githubusercontent.com/PAA-NCIC/PPoPP2017_artifact/HEAD/KeplerAs/README.md>
  - <https://raw.githubusercontent.com/PAA-NCIC/PPoPP2017_artifact/HEAD/KeplerAs/LICENSE>
  - <https://raw.githubusercontent.com/PAA-NCIC/PPoPP2017_artifact/HEAD/KeplerAs/Makefile.PL>
  - <https://raw.githubusercontent.com/PAA-NCIC/PPoPP2017_artifact/HEAD/KeplerAs/Install.sh>
  - <https://raw.githubusercontent.com/PAA-NCIC/PPoPP2017_artifact/HEAD/KeplerAs/bin/KeplerAs.pl>
  - <https://raw.githubusercontent.com/PAA-NCIC/PPoPP2017_artifact/HEAD/KeplerAs/lib/KeplerAs/KeplerAs.pm>
  - <https://raw.githubusercontent.com/PAA-NCIC/PPoPP2017_artifact/HEAD/KeplerAs/lib/KeplerAs/Cubin.pm>
  - <https://github.com/PAA-NCIC/PPoPP2017_artifact/tree/master/Solver>
  - <https://raw.githubusercontent.com/PAA-NCIC/PPoPP2017_artifact/HEAD/Solver/LICENSE>
  - <https://raw.githubusercontent.com/PAA-NCIC/PPoPP2017_artifact/HEAD/Solver/Readme.md>
  - <https://github.com/PAA-NCIC/PPoPP2017_artifact/tree/master/SGEMM>
  - <https://github.com/PAA-NCIC/PPoPP2017_artifact/tree/master/SGEMM/NN>
  - <https://github.com/PAA-NCIC/PPoPP2017_artifact/tree/master/SGEMM/NN/12x12>
  - <https://github.com/PAA-NCIC/PPoPP2017_artifact/tree/master/SGEMM/NT>
  - <https://raw.githubusercontent.com/PAA-NCIC/PPoPP2017_artifact/HEAD/SGEMM/NN/12x12/Makefile>
  - <https://raw.githubusercontent.com/PAA-NCIC/PPoPP2017_artifact/HEAD/SGEMM/NN/12x12/sgemm.cpp>
  - <https://raw.githubusercontent.com/PAA-NCIC/PPoPP2017_artifact/HEAD/SGEMM/NN/12x12/sgemm_nn_192x192.cu>
  - <https://raw.githubusercontent.com/PAA-NCIC/PPoPP2017_artifact/HEAD/SGEMM/NN/12x12/sgemm_nn_192x192.sass>
  - <https://raw.githubusercontent.com/PAA-NCIC/PPoPP2017_artifact/HEAD/SGEMM/NN/12x12/sgemm_common_192x192.sass>
  - <https://raw.githubusercontent.com/PAA-NCIC/PPoPP2017_artifact/HEAD/SGEMM/NN/8x8/sgemm.cpp>
  - <https://raw.githubusercontent.com/PAA-NCIC/PPoPP2017_artifact/HEAD/SGEMM/NN/8x8/Makefile>
  - <https://raw.githubusercontent.com/PAA-NCIC/PPoPP2017_artifact/HEAD/SGEMM/NN/8x8/sgemm_nn_128x128.sass>
  - <https://raw.githubusercontent.com/PAA-NCIC/PPoPP2017_artifact/HEAD/SGEMM/TN/12x12/sgemm.cpp>
  - <https://raw.githubusercontent.com/PAA-NCIC/PPoPP2017_artifact/HEAD/SGEMM/TN/12x12/sgemm_tn_192x192.sass>
  - <https://raw.githubusercontent.com/PAA-NCIC/PPoPP2017_artifact/HEAD/SGEMM/TN/8x8/sgemm.cpp>
  - <https://raw.githubusercontent.com/PAA-NCIC/PPoPP2017_artifact/HEAD/SGEMM/TN/8x8/sgemm_tn_128x128.sass>
  - <https://raw.githubusercontent.com/PAA-NCIC/PPoPP2017_artifact/HEAD/SGEMM/NT/sgemm.sh>
  - <https://raw.githubusercontent.com/PAA-NCIC/PPoPP2017_artifact/HEAD/SGEMM/NT/sgemm.cpp>
  - <https://raw.githubusercontent.com/PAA-NCIC/PPoPP2017_artifact/HEAD/SGEMM/NT/Makefile>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/paa-ncic/ppopp2017_artifact`) · [data/wave13/enrich/raw/github_com_paa_ncic_ppopp2017_artifact.json](../../../data/wave13/enrich/raw/github_com_paa_ncic_ppopp2017_artifact.json) (enrichment confidence 0.8)

</details>
