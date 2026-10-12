# MaxAs

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Assemblers and assembly tooling](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Perl` · `MIT` · 🔴 abandoned

> Perl assembler for NVIDIA Maxwell SASS; its hand-scheduled SGEMM beat cuBLAS's Maxwell kernels by about 4-25%.

| | |
|---|---|
| **Beats** | cuBLAS sgemm (NVIDIA's library kernels, compiled by NVIDIA's toolchain) |
| **Claimed result** | SGEMM walkthrough: 'performing as much as 25% over cublas' for small matrices (64-thread version) and 'beating cublas by 4.8%' at size 4096 (256-thread version); about 98% of theoretical peak on GM107 and 96% on GM204. Charts (read from the xldrx/maxas.wiki.fixed mirror; the original wiki images are broken, issue #13): BenchSmall.png gives Max64 about 3,100 vs Cub128 about 2,470 GFLOPS at N = 320 only (the '25%'), about 9-10% at N = 384 and 512, and Max64 falls below cuBLAS above N of about 5,600; BenchLarge.png gives Max256 about 6,200 vs Cub256 about 5,950 GFLOPS (about 4%) (values read off chart pixels). |
| **Workload** | Hand-scheduled single-precision GEMM kernels written in Maxwell SASS and assembled with MaxAs, versus cuBLAS sgemm, on large (4096) and small matrices. |
| **Metric** | throughput |
| **Hardware** | NVIDIA GM204 (Maxwell) at a sustained 1607 MHz core clock (1620 MHz boost scores excluded) with 8000 MHz memory; GM107 also cited for the 98% efficiency figure. Card model, driver, CUDA and cuBLAS versions are not stated on the page. |
| **Adoption** | 1.1k stars |
| **Last commit** | 2023-01-03 |
| **Links** | [repository](https://github.com/NervanaSystems/maxas) · [benchmark](https://github.com/NervanaSystems/maxas/wiki/SGEMM) |

## Verdict

On a GM204 (Maxwell) at a sustained 1607 MHz core clock and 8000 MHz memory, the hand-scheduled fp32 SGEMM (64- and 256-thread kernels, square NT matrices, all-ones inputs) ran up to about 25% faster than cuBLAS's own Maxwell SGEMM kernels at one small size (N = 320) and 4.8% faster at N = 4096. It reached about 96% of theoretical peak on GM204 and 98% on GM107. Per the harness comments the cuBLAS kernels were taken from CUDA 6.5 and run in the same driver-API harness; the card model and driver are not stated, and the GFLOPS appear only in chart images.

## Use it when

- Learning how a near-peak GPU GEMM is built at the instruction level: the SGEMM wiki walkthrough on register banks, the reuse cache, control codes and latency hiding is the project's lasting value.
- Writing or patching kernels for Maxwell GPUs (measured on GM107 and GM204) when ptxas register allocation or scheduling is the bottleneck.
- Disassembling a Maxwell cubin (-e), editing it and reinserting it (-i), for example to test register mappings or reuse flags on a ptxas-compiled kernel.
- Microbenchmarking Maxwell instruction latencies and control-code behaviour with the bundled microbench framework.

## Skip it when

- Volta or newer GPUs: MaxAs knows the Maxwell-era instruction grammar only; use TuringAs (Volta, Turing, Ampere) instead. Pascal support is not documented (Cubin.pm only rejects cubins older than sm_50).
- Production GEMM: the measured win is over a 2014-2015 cuBLAS and is about 4% for large matrices; the 64-thread kernel falls below both cuBLAS kernels above roughly N = 5,600 on GM204 (chart).
- Full SGEMM semantics: the sample kernels compute C = alpha\*A\*B^T only (no beta term, NT layout only), need leading dimensions that are multiples of 4 floats for the quad loads, read inputs through 1D textures and are 32-bit-address cubins (-m 32).
- Low-maintenance toolchains: the wiki requires the nvdisasm from CUDA 6.5, newer cuobjdump output broke parsing (issue #10, still open), the sample harness is a Windows Visual Studio project, and the repository is archived.
- Code without hand-checked memory dependencies: the assembler deliberately leaves dependency barriers for memory operations to the programmer, so a wrong control code gives a silent race rather than an error.

## How it is fast

The assembler itself adds no speed. It exposes what ptxas hides: explicit register allocation by bank (on Maxwell the bank is the register number mod 4), automatic operand-reuse flags, hand-set control codes (stall counts, dependency barriers, dual issue) and an optional list scheduler for marked blocks. The SGEMM uses an 8x8-per-thread register blocking with 64 accumulators, double-buffered shared memory, 128-bit quad texture loads (lda/ldb divided by 4), warp-split loads where each half of the threads fetches A or B, a bank-aware C-register layout and a warp-synchronous shared-memory shuffle for coalesced C stores. The main loop issues 512 FFMAs in 520 issue slots, a 98.5% upper bound.

## Compared with alternatives

Choose MaxAs only for Maxwell GPUs or for its SGEMM walkthrough, the most detailed write-up among the GPU SASS assemblers catalogued; KeplerAs (PPoPP 2017 artifact, 1.15x over cuBLAS 7.0 on Kepler) covers the previous generation with a paper behind it, and TuringAs is the choice for Volta, Turing and Ampere.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | Perl 5.10+ (64-bit) with Carp and Data::Dumper; CUDA toolkit (nvcc for the shell cubin, cuobjdump, and the CUDA 6.5 nvdisasm); CUDA driver API to load the resulting cubin |
| **Minimum toolchain** | Perl 5.10 (named regex captures, 64-bit integers); nvdisasm from CUDA 6.5 (later toolkits work only with that nvdisasm swapped in, per the wiki and issue #10) |
| **Platforms** | Host: any OS with 64-bit Perl (author worked on Windows with Visual Studio; wiki also covers Linux install). Target: NVIDIA Maxwell (sm_50/sm_52; GM107 and GM204 measured) |
| **Thread safety** | not applicable (offline command-line assembler); not documented for the generated kernels |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw: the published sgemm/sgemm.cpp comments out every cuBLAS call (cublasCreate, the Cub64/Cub128 runs and the reference cublasSgemm), yet still runs test(C, T) against devT, which is only ever zeroed, so the accuracy check compares MaxAs output with zeros. Inputs are all-ones matrices (A[i] = B[i] = 1.0f), so every element of C equals N whatever the layout, and even with cuBLAS restored the check cannot catch indexing or transpose bugs.
- The cuBLAS baseline was cuBLAS's own maxwell_sgemm_128x64_nt and 128x128_nt SASS, extracted from CUDA 6.5's Win32 cublas_device.lib into cublas_sgemm.cubin and launched outside cuBLAS (cublas_sgemm.ptx comments). That is a kernel-against-kernel test in one NT layout, not cublasSgemm with its kernel selection. The MaxAs kernels were themselves derived from studying that SASS, and the wiki blames 28 GFLOPS of cuBLAS's gap on a register-bank-conflict bug in its first FFMA.
- The '25% over cublas' figure is one chart point. Reading BenchSmall.png: N = 320 gives Max64 about 3,100 against Cub128 about 2,470 GFLOPS, but the gap is about 9-10% at N = 384 and 512. BenchLarge.png shows Max256 about 6,200 against Cub256 about 5,950 GFLOPS (about 4%). sgemm.pl's size sweep sits after an 'exit;' and uses the 16-bit normalized texture format, so the fp32 runs behind the cuBLAS charts are not scripted in the repo. The original wiki images are broken (issue #13); the charts survive in the xldrx/maxas.wiki.fixed mirror.
- Assembly is the source of truth: re-extracting with a newer cuobjdump can drop instructions wrapped in braces (issue #10). Register-bank and reuse tuning is specific to Maxwell's 4-bank register file and does not transfer to later architectures.

## Known shortcomings

- First-party wiki only: up to 25% over cuBLAS on small matrices and 4.8% at 4096, GFLOPS in charts, no CUDA or cuBLAS versions, card unnamed; the cuBLAS timing code is commented out in sgemm/sgemm.cpp; kernels derived from cuBLAS's own SASS; archived 2023, last code commit 2016.
- Harness flaws: sgemm/sgemm.cpp has every cuBLAS call commented out but still runs test(C, T) against a zeroed devT, so the accuracy check compares against zeros, and the inputs are all ones, so layout and transpose bugs are undetectable. The cuBLAS baseline is CUDA 6.5's cublas_device.lib SASS kernels extracted and launched outside cuBLAS. The charts (read from the xldrx/maxas.wiki.fixed mirror) show the '25%' as a single point at N = 320 (about 3,100 vs 2,470 GFLOPS), about 9-10% at 384 and 512 and about 4% at large sizes, with Max64 below cuBLAS above N of about 5,600; sgemm.pl's size sweep is dead code after an exit and uses the INT16 texture format.

## Caveats and trade-offs

First-party wiki claim; exact per-size GFLOPS are only in chart images, and the page names no cuBLAS, CUDA or driver version, no card model and no flags. The public harness (sgemm/sgemm.cpp with sgemm.pl, a Windows Visual Studio build) has its cuBLAS timing code commented out, so the comparison cannot be rerun as published. The author says the kernels were 'derived from detailed study of the cublas Kepler and Maxwell sgemm implementations', and part of the gap comes from a cuBLAS bug that the wiki says costs cuBLAS sgemm 28 GFLOPS on GM204; the 2015-era cuBLAS has long since been superseded. The speedup is of a hand-scheduled SASS kernel against a library, not of the assembler against ptxas, GNU as, NASM or MASM; MaxAs only targets Maxwell (later partial half and dp4a support). Archived by the owner on 2023-01-03 with an Intel discontinuation notice; the last code commit is from 2016-06-10. Treat as a reference, not a general assembler win. [retier] First-party wiki claim from 2015; exact per-size GFLOPS exist only in chart images, and the page names no cuBLAS, CUDA or driver version, no card model and no flags. Harness flaws: the published sgemm/sgemm.cpp comments out every cuBLAS call (cublasCreate, the Cub64/Cub128 runs and the reference cublasSgemm) yet still runs test(C, T) against devT, which is only ever zeroed, so the accuracy check compares MaxAs output with zeros; inputs are all-ones matrices, so every element of C equals N whatever the layout and even a restored cuBLAS check could not catch indexing or transpose bugs. The cuBLAS baseline was cuBLAS's own maxwell_sgemm_128x64_nt and 128x128_nt SASS extracted from CUDA 6.5's Win32 cublas_device.lib and launched outside cuBLAS (a kernel-against-kernel test in one NT layout, not cublasSgemm with its kernel selection); the MaxAs kernels were derived from studying that SASS, and the wiki blames 28 GFLOPS of cuBLAS's gap on a register-bank-conflict bug in its first FFMA. sgemm.pl's size sweep sits after an 'exit;' and uses the 16-bit normalized texture format, so the fp32 runs behind the charts are not scripted. The 2015-era cuBLAS has long since been superseded; register-bank and reuse tuning is specific to Maxwell's 4-bank register file, and re-extracting with a newer cuobjdump can drop instructions wrapped in braces (issue #10).

Assembler for NVIDIA Maxwell SASS only (GTX 9xx era), written in Perl; the repository is archived and Intel has discontinued the project. Gains come from hand-written kernels and scheduling, not from the assembler alone.

## Maintenance

Archived 2023-01-03 with an Intel discontinuation notice (last code commit 2016-06-10, 1.1k stars). It is MIT-licensed and still the best-documented Maxwell SASS workflow, but treat it as a reference: it does not target current GPUs, and the published harness cannot rerun the cuBLAS comparison (cuBLAS calls are commented out and the accuracy check compares against a zeroed buffer).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party SGEMM wiki states 'as much as 25% over cublas' for small matrices (64-thread kernel) and 'At the 4096 size we're beating cublas by 4.8%' (256-thread kernel), 98% of theoretical on GM107 and 96% on GM204; GFLOPS exist only in chart images. The harness (sgemm/sgemm.cpp, sgemm.pl) is public but its cuBLAS timing calls are commented out, it builds as a Windows Visual Studio project, and no CUDA, cuBLAS or driver version or card model is given, so not A; no independent head-to-head found (maxDNN arXiv 1501.06633 reports 96% efficiency for a maxas-style SGEMM, snippet only, no cuBLAS comparison).
- **Verifier notes:** Wiki numbers match the record (25% small-matrix, 4.8% at 4096, 98%/96% efficiency). Shortcomings: first-party, GFLOPS chart-only, no cuBLAS/CUDA versions or card model, cuBLAS comparison code commented out in the published harness, kernels derived from cuBLAS's own SASS plus a cuBLAS bug, archived 2023 (last code 2016).
- **Fields the verifier corrected:** `hardware`, `caveats`, `claimed_speedup`
- **Shortcomings recorded by:** verifier batch-02 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/NervanaSystems/maxas/wiki/SGEMM>
  - <https://github.com/NervanaSystems/maxas>
  - <https://github.com/NervanaSystems/maxas/commits/master>
  - <https://github.com/NervanaSystems/maxas/tree/master/sgemm>
  - <https://raw.githubusercontent.com/NervanaSystems/maxas/HEAD/README.md>
  - <https://raw.githubusercontent.com/NervanaSystems/maxas/master/sgemm/sgemm.cpp>
  - <https://raw.githubusercontent.com/NervanaSystems/maxas/master/sgemm/sgemm.pl>
  - <https://raw.githubusercontent.com/NervanaSystems/maxas/master/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/NervanaSystems/maxas>
  - <https://github.com/NervanaSystems/maxas/commits/master>
  - <https://github.com/NervanaSystems/maxas/issues?q=is%3Aissue>
  - <https://github.com/NervanaSystems/maxas/issues/10>
  - <https://github.com/NervanaSystems/maxas/tree/master/sgemm>
  - <https://github.com/NervanaSystems/maxas/wiki/SGEMM>
  - <https://raw.githubusercontent.com/wiki/NervanaSystems/maxas/SGEMM.md>
  - <https://raw.githubusercontent.com/wiki/NervanaSystems/maxas/Introduction.md>
  - <https://raw.githubusercontent.com/wiki/NervanaSystems/maxas/Getting-Started.md>
  - <https://raw.githubusercontent.com/wiki/NervanaSystems/maxas/Control-Codes.md>
  - <https://raw.githubusercontent.com/xldrx/maxas.wiki.fixed/master/img/BenchSmall.png>
  - <https://raw.githubusercontent.com/xldrx/maxas.wiki.fixed/master/img/BenchLarge.png>
  - <https://raw.githubusercontent.com/xldrx/maxas.wiki.fixed/master/img/BenchNormFloat.png>
  - <https://raw.githubusercontent.com/NervanaSystems/maxas/master/README.md>
  - <https://raw.githubusercontent.com/NervanaSystems/maxas/master/LICENSE>
  - <https://raw.githubusercontent.com/NervanaSystems/maxas/master/sgemm/sgemm.cpp>
  - <https://raw.githubusercontent.com/NervanaSystems/maxas/master/sgemm/sgemm.pl>
  - <https://raw.githubusercontent.com/NervanaSystems/maxas/master/sgemm/sgemm.cu>
  - <https://raw.githubusercontent.com/NervanaSystems/maxas/master/sgemm/sgemm64.sass>
  - <https://raw.githubusercontent.com/NervanaSystems/maxas/master/sgemm/cublas_sgemm.ptx>
  - <https://raw.githubusercontent.com/NervanaSystems/maxas/master/cpanfile>
  - <https://raw.githubusercontent.com/NervanaSystems/maxas/master/Makefile.PL>
  - <https://raw.githubusercontent.com/NervanaSystems/maxas/master/Changes>
  - <https://raw.githubusercontent.com/NervanaSystems/maxas/master/lib/MaxAs/MaxAs.pm>
  - <https://raw.githubusercontent.com/NervanaSystems/maxas/master/lib/MaxAs/Cubin.pm>
  - <https://raw.githubusercontent.com/NervanaSystems/maxas/master/bin/maxas.pl>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/nervanasystems/maxas`) · [data/wave13/enrich/raw/github_com_nervanasystems_maxas.json](../../../data/wave13/enrich/raw/github_com_nervanasystems_maxas.json) (enrichment confidence 0.8)

</details>
