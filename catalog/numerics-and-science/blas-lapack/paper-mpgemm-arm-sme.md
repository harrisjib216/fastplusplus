# MPGEMM (ARM SME)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [BLAS and LAPACK](README.md)</sub>

**Tier C** (first-party claim) · Study only · `?` · `no license` · ⚪ unknown

> SME GEMM library for Apple M4 from a NUDT paper; code unreleased; reports 1.23x average over Apple Accelerate.

| | |
|---|---|
| **Beats** | OpenBLAS, Apple Accelerate, LIBXSMM, KleidiAI |
| **Claimed result** | Avg 5.7x over OpenBLAS, 1.23x over Apple Accelerate, 3.96x over LIBXSMM, 4.69x over KleidiAI |
| **Workload** | GEMM and mixed-precision GEMM using ARM SME |
| **Metric** | throughput |
| **Hardware** | Apple M4 Pro |
| **Compiler and flags** | AppleClang 16, macOS 15.1 |
| **Links** | [repository](https://github.com/mpgemm/MPGEMM) · [benchmark](https://arxiv.org/html/2512.21473) |

## Verdict

The authors report average speedups of 1.23x over Apple Accelerate, 5.7x over OpenBLAS, 3.96x over LIBXSMM and 4.69x over KleidiAI, on an Apple M4 Pro (10 P-cores) with AppleClang 16 on macOS 15.1 (flags not stated). For fp32 on one SME unit, the paper's ratios as cited by the reproduction are smaller: 1.95x over LIBXSMM, 2.34x over KleidiAI and 2.85x over OpenBLAS. An independent rebuild from the text (MTGEMM-A, Apple clang 21, M4 Pro with 8 P-cores) measured the paper design at 1.09x (row-major) and 0.95x (column-major) of Accelerate on one thread, and its tuned version at 1.25x and 1.19x.

## Use it when

- As a design reference when writing SME/SME2 GEMM kernels for Apple M4-class chips: 16x64 tile shape over 32x32, ZA-based transposition while packing, x4 loads, blocking capped at 8 MB
- LLM-shaped fp32 GEMMs on an M4 (M = 64 or 128 with large N and K): the reproduction's largest gains over Accelerate were on these thin-M groups (1.34x-1.52x row-major, one thread)
- When you need running code, use the MIT reproduction MTGEMM-A (fp32/fp64, no transposes), which measured 1.25x row-major and 1.19x column-major over Accelerate on the paper's 24 workloads, one thread
- Inside OpenBLAS, once the SME2 port of this design lands (PR #6074, open as of 2026-09-30)

## Skip it when

- Any production dependency on MpGEMM itself: no code, binary or license has been published
- Hardware other than SME2 with 512-bit streaming vectors and an M4-like cache: the blocking model and tile shapes are tuned for the M4 Pro, and M1-M3 have no SME
- Small or GEMV-shaped products: in the reproduction the SME path is 0.16x-0.9x of Accelerate for squares below 64^3, about 0.5x at 4x4, and about 0.4x when one side is 1; LIBXSMM is fastest from 16^3 to 48^3
- Short-K shapes with one side of 32 or less and the other 512 or more (0.6x-0.9x of Accelerate at K = 512 in the reproduction)
- Mixed-precision (FP16/INT8) work you need to verify: no independent reproduction of those paths exists

## How it is fast

It is a Goto-style six-loop blocked GEMM whose mc/nc/kc come from an analytical model bounded by TLB reach and an 8 MB working-set limit, because the SME unit keeps full load bandwidth only up to 8 MB of the 16 MB L2. The fp32 micro-kernel is 16x64 and uses all four ZA tiles: one A vector and four B vectors feed four FMOPA outer products per K step (fp64: 8x64 over eight tiles). Row-major A is transposed during packing through the ZA array (rows in as horizontal slices, columns out as vertical slices), B is packed online during the first pass, and all loads and stores use SME2 four-register (x4) forms, which the reproduction measured at 874-992 GB/s against 391-465 GB/s for single-register loads. Each of the M4 Pro's two P-cluster SME units gets its own thread.

## Compared with alternatives

None of the catalogued siblings (BLASFEO, LibShalom, IAAT, sgemm.c, FT-BLAS) uses SME, so this is the only catalogued design aimed at Apple M4's matrix units. Because its code is unreleased, read it for the design and run MTGEMM-A, Eigen's unmerged SME branch (MR !3164, which carries elements of it) or the OpenBLAS port instead. Keep LibShalom or BLASFEO for small or irregular GEMM on NEON-only Arm.

## Integration

| | |
|---|---|
| **Form** | not released (paper only); the MTGEMM-A reproduction builds a static lib (libmtgemm.a) |
| **Dependencies** | not documented for MpGEMM; MTGEMM-A needs none at runtime (Python 3 only for tools) |
| **Minimum toolchain** | Paper: AppleClang 16 on macOS 15.1, flags not stated. Reproduction: Apple clang (Xcode 16+), -std=c++17 -O3 -march=armv8.6-a+sme2+sme-f64f64 |
| **Platforms** | aarch64 with SME2, 512-bit SVL (evaluated only on Apple M4 Pro); FEAT_SME_F64F64 for fp64 |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | no |

## Gotchas

- The baselines in the headline ratios are uneven. The reproduction matched the paper's LIBXSMM numbers within 2%, but a September 2026 KleidiAI ran 1.5x faster than the paper measured. Homebrew OpenBLAS 0.3.34 used SME only in a direct SME1 SGEMM and fell back to NEON at M = 4096. OpenBLAS develop has had SME GEMM kernels since August 2026.
- The design as the paper describes it does not reach the paper's numbers: rebuilt literally, it ran 7-11% below the paper's MpGEMM and at 0.95x of Accelerate in column-major order. Core-side L2 prefetch and four-row ZA moves, which are not in the paper, were needed to get to 1.19x-1.25x.
- The paper's claim that stack buffers stall the SME unit was not reproduced (heap vs stack 0.98x-1.02x). What does cost about a third of throughput is any core store during an SME loop.
- Two-unit scaling depends on macOS placing the two threads on different P-clusters, and macOS has no API to pin them. Ratios against Accelerate also depend on the macOS version: a newer multi-threaded Accelerate cut the reproduction's two-unit gain to 1.12x-1.15x.

## Known shortcomings

- OpenBLAS had no SME kernels on M4 at the time, inflating the 5.7x; paper says code is open source but gives no link.
- Claim not reproduced: tesch1/MTGEMM-A, rebuilt from the paper text, got only 1.09x row-major and 0.95x col-major over Accelerate (paper 1.23x); the stack-buffer stall claim was not reproduced; the paper's OpenBLAS M=4096 numbers (422-533 GFLOPS) do not match OpenBLAS 0.3.34, which falls back to NEON there (114); fp32 one-SME-unit ratios (1.95x/2.34x/2.85x) are far below the headline 3.96x/4.69x/5.7x. OpenBLAS PR #6074 (open, 2026-09-30) ports the design.
- Code is public at github.com/mpgemm/MPGEMM (MIT, IPDPS '26), found by the MaxMulSK verifier; the record previously said no code. tesch1/MTGEMM-A is an independent reimplementation.

## Caveats and trade-offs

Paper calls MpGEMM open-source but links no code (none found); flags unstated; OpenBLAS lacked SME kernels on M4 at the time, which inflates the 5.7x figure, so the meaningful win is 1.23x over Apple Accelerate. An independent MIT reimplementation of the paper's design (github.com/tesch1/MTGEMM-A, Apple clang 21, -O3 -march=armv8.6-a+sme2, bench/bench.cpp) measured the paper design at 1.09x over Accelerate fp32 single-thread geomean, and its own tuned version at 1.25x.

Apple SME only

## Maintenance

Paper-only reference: an arXiv preprint (Dec 2025, no venue stated) whose promised open-source code never appeared, so maintenance does not apply. The design lives on in the MIT-licensed MTGEMM-A reproduction (active Sep 2026) and in OpenBLAS PR #6074 (open).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** arXiv preprint by the authors (NUDT, 'Demystifying ARM SME to Optimize General Matrix Multiplications') with averages vs OpenBLAS 5.7x, Accelerate 1.23x, LIBXSMM 3.96x, KleidiAI 4.69x on an Apple M4 Pro with AppleClang 16; it is called open-source but gives no code URL and no flags, and no venue is stated, so it is not A or B.
- **Verifier notes:** Numbers match the page. Lead: tesch1/MTGEMM-A (MIT, 0 stars, active Sep 2026) is a reproducible standalone SME GEMM with tier-A-style methodology vs Accelerate, LIBXSMM, KleidiAI and OpenBLAS; consider adding it as its own entry. The same author has an OpenBLAS SME2 PR (OpenMathLib/OpenBLAS#6072, not opened).
- **Fields the verifier corrected:** `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/html/2512.21473>
  - <https://github.com/tesch1/MTGEMM-A>
- **Sources the enricher read:**
  - <https://github.com/tesch1/MTGEMM-A>
  - <https://raw.githubusercontent.com/tesch1/MTGEMM-A/HEAD/README.md>
  - <https://raw.githubusercontent.com/tesch1/MTGEMM-A/HEAD/results/paper_numbers.csv>
  - <https://raw.githubusercontent.com/tesch1/MTGEMM-A/HEAD/include/mtgemm.h>
  - <https://github.com/OpenMathLib/OpenBLAS/pull/6072>
  - <https://github.com/OpenMathLib/OpenBLAS/pull/6074>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `paper:mpgemm-arm-sme`) · [data/wave8/enrich/raw/paper_mpgemm_arm_sme.json](../../../data/wave8/enrich/raw/paper_mpgemm_arm_sme.json) (enrichment confidence 0.55)

</details>
