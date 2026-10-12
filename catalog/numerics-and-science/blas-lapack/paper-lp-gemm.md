# LP-GEMM

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [BLAS and LAPACK](README.md)</sub>

**Tier C** (first-party claim) · Study only · `?` · `no license` · ⚪ unknown

> Research GEMM variant (UNICAMP, OpenBLAS-derived kernels) that skips repacking between chained GEMMs; about 2.25x over OpenBLAS on chains.

| | |
|---|---|
| **Beats** | OpenBLAS, BLIS, Intel MKL, oneDNN |
| **Claimed result** | Average 2.25x over OpenBLAS for sequential (chained) GEMMs on Intel Xeon Gold 6252 (AVX-512), single-thread; single-GEMM median \~1.5x over OpenBLAS. Abstract claims 'up to 2x for x86 and up to 5x for RISC-V for Attention-like workloads', but the RISC-V attention figure (Fig. 6b) shows roughly 1.5x at best. |
| **Workload** | Chained GEMM with layout propagation, attention-like workloads, single-thread |
| **Metric** | throughput |
| **Hardware** | Intel Xeon Gold 6252; SpacemiT K1 X60 |
| **Links** | [benchmark](https://arxiv.org/html/2604.04599) |

## Verdict

Single-threaded on an Intel Xeon Gold 6252 (AVX-512), chained GEMMs averaged 2.25x over OpenBLAS; mid/end kernels had a median of about 1.5x on single GEMMs from GEMMBench, and MKL and oneDNN stayed close. RISC-V (SpacemiT X60, RVV 1.0) attention results vs OpenBLAS are reported, but the abstract-level 5x does not match Fig. 6b per the verifier; compiler and flags are not given.

## Use it when

- Chains of small to medium GEMMs where packing is a large share of runtime, e.g. LLM attention at short sequence lengths (the paper shows about 2x at 10 tokens on x86)
- Edge or CPU inference engines you control end to end, so custom layouts can flow between ops
- RISC-V RVV 1.0 targets where OpenBLAS's unpack step is slow
- As a design reference for fusing packing across operators in your own GEMM or ML compiler

## Skip it when

- As a library: no LP-GEMM kernels are public (the linked simple_attention repo is a naive-matmul Llama driver that links a libopenblas not included in the repo)
- Single, isolated GEMM calls: the initial kernel performs about like OpenBLAS, and BLIS and FlashGEMM median speedups beat it there
- Large matrices (for example the MLP at about 1.1x on x86), where packing is negligible
- beta != 0 accumulation into existing C, which needs explicit packing
- Multi-threaded workloads: only single-threaded results are reported

## How it is fast

The technique is layout propagation, i.e. packing elimination across operator boundaries. The micro-kernel writes C in the same tiled order the next GEMM's packed operand expects, so the O(n^2) pack and unpack steps around each O(n^3) micro-kernel run only at the ends of the chain. The kernels are derived from OpenBLAS (AVX-512 with mr=16, nr=4 on x86; RVV 1.0 with mr=16, nr=8 on RISC-V), so per-kernel FLOP efficiency is about OpenBLAS's level and the gain comes from the data movement it removes.

## Compared with alternatives

Siblings such as BLASFEO, LibShalom and IAAT speed up individual small GEMMs; LP-GEMM's idea only pays off across chains of dependent GEMMs, and with no code it is a technique to copy, not a library to adopt. For a usable single-call kernel choose BLASFEO or LibShalom.

## Integration

| | |
|---|---|
| **Form** | not released (paper only; authors give a contact email) |
| **Dependencies** | modified OpenBLAS (per the paper) |
| **Minimum toolchain** | not documented (driver Makefile uses g++ -mavx512f -fopenmp with no -O flag) |
| **Platforms** | x86-64 AVX-512 (Xeon Gold 6252), RISC-V RV64GCV with RVV 1.0 (SpacemiT K1 X60) |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | no |

## Gotchas

- Results stay in the propagated tiled layout, so every non-GEMM op between GEMMs (softmax, RoPE, RMSNorm) needs a layout-aware rewrite; softmax pays extra at tile boundaries
- The 'up to 5x for RISC-V' claim (Section V-C) is a speedup that rises with token count to 500 tokens and is attributed to a weak OpenBLAS RVV unpack kernel, not to LP-GEMM itself; the verifier found Fig. 6b peaks at about 1.5x, inconsistent with that text
- Compiler, flags and OpenBLAS/BLIS/MKL versions are not stated

## Known shortcomings

- No LP-GEMM code released; compiler and flags not stated; gain mostly from skipping packing; BLIS/FlashGEMM beat the initial kernel on single GEMMs; abstract's 'up to 5x on RISC-V' contradicts Fig. 6b (\~1.5x at best).
- Not BLAS-API compliant, cannot handle beta != 0; linked simple_attention repo uses a naive matmul with -g and no -O flag; no compiler or library versions; 'up to 5x' RISC-V is credited by the paper itself to a weak OpenBLAS RVV unpack kernel.

## Caveats and trade-offs

No LP-GEMM code released (the only linked repo, czariv/simple_attention, is a 0-star Llama attention driver without the GEMM kernels); compiler and flags unstated; kernels derived from OpenBLAS and the gain comes mainly from skipping packing; BLIS and FlashGEMM median speedups exceed the initial LP-GEMM kernel on single GEMMs; the 5x RISC-V abstract figure is not borne out by the paper's own plots.

Single-threaded evaluation

## Maintenance

arXiv 2604.04599 preprint (2026, no venue stated) with no released kernels and no license, so it is listed as a reference only.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification C, tier now C.
- **Tier reason:** arXiv preprint (no venue stated) by the authors (UNICAMP); compares against OpenBLAS, BLIS, MKL, oneDNN, FlashGEMM on named CPUs, but no LP-GEMM code is released and compiler/flags are not stated. Tier stays C; the claim was overstated, so the verdict is downgrade.
- **Verifier notes:** Real result, but the headline is narrow: 2.25x average holds only for chained GEMMs against OpenBLAS. Record the shortcoming that the abstract's 5x RISC-V claim is inconsistent with Fig. 6b. Usability stays reference (no code).
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/html/2604.04599>
  - <https://github.com/czariv/simple_attention>
- **Sources the enricher read:**
  - <https://arxiv.org/html/2604.04599>
  - <https://github.com/czariv/simple_attention>
  - <https://raw.githubusercontent.com/czariv/simple_attention/HEAD/Makefile>
  - <https://raw.githubusercontent.com/czariv/simple_attention/HEAD/main.cpp>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `paper:lp-gemm`) · [data/wave8/enrich/raw/paper_lp_gemm.json](../../../data/wave8/enrich/raw/paper_lp_gemm.json) (enrichment confidence 0.55)

</details>
