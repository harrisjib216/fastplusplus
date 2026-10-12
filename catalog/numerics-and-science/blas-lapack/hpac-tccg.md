# TCCG / GETT (Tensor Contraction Code Generator)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [BLAS and LAPACK](README.md)</sub>

**Tier A** (reproducible public benchmark) · Study only · `Python (generator that emits vectorized C code)` · `no license` · 🔴 abandoned

> Python code generator for GETT tensor contractions; beats MKL-backed transpose-transpose-GEMM-transpose up to about 2x on bandwidth-bound cases.

| | |
|---|---|
| **Beats** | TTGT (transpose-transpose-GEMM-transpose) tensor contraction built on Intel MKL sgemm/dgemm (the repo's default BLAS in config.cfg is MKL); TTGT is TCCG's own backend, not a third-party tensor library |
| **Claimed result** | No numeric table; values read by eye from the figures. benchmark/GETT_LoG_TTGT.png, single precision, one Haswell core: abcde-efbad-cf GETT about 20.5 GFLOPS vs TTGT about 15 (about 1.4x, derived from figure); abcdef-dfgb-geac GETT about 55.5 vs TTGT about 25 (about 2.2x, derived from figure); on compute-bound cases TTGT ties or beats GETT (abcd-aebf-fdec about 67 vs about 75 GFLOPS single precision; in double precision TTGT leads on the last four cases, about 31 vs 37). benchmark/benchmark.png (Fig. 11): TCCG about 55 GFLOPS vs max(CTF, naive) about 13 on abcdef-dfgb-geac, and about 20.5 vs about 2 on abcde-efbad-cf (roughly 10x, derived from figure); near parity with the best other tool on the compute-bound cases. README text only says GETT is 'especially outstanding' for bandwidth-bound contractions. |
| **Workload** | Dense tensor contractions from the repo's benchmark v0.1 (CCSD, AO2MO and intensli test cases, up to 6-D tensors, largest tensor 200 MiB), single and double precision, GFLOPS on one core; GETT versus LoG versus TTGT, and TCCG versus the best of CTF/naive (single) or CTF/TT/naive (double). |
| **Metric** | throughput |
| **Hardware** | Single core of an Intel Xeon E5-2680 v3 (Haswell); ECC enabled, Intel SpeedStep and TurboBoost disabled |
| **Compiler and flags** | Intel icpc 16.0.1 20151021, -O3 -xhost -mkl (benchmark/README.md) |
| **Adoption** | 40 stars; subject of ACM TOMS 2018 / arXiv 1607.00145. TCL uses TTGT, not GETT (GETT is planned there 'eventually'). |
| **Last commit** | 2017-08-14 |
| **Links** | [repository](https://github.com/HPAC/tccg) · [benchmark](https://github.com/HPAC/tccg/tree/master/benchmark) |

## Verdict

On one core of an Intel Xeon E5-2680 v3 (Haswell, TurboBoost and SpeedStep off), built with icpc 16.0.1 -O3 -xhost -mkl, the figures (read by eye) show GETT at about 20.5 vs 15 GFLOPS for MKL-backed TTGT on abcde-efbad-cf and about 55.5 vs 25 on abcdef-dfgb-geac in single precision, and TCCG roughly 10x the best of CTF/naive on the most bandwidth-bound cases, with parity or a TTGT lead on compute-bound ones. The TTGT baseline is the authors' own implementation, not a third-party library.

## Use it when

- Bandwidth-bound contractions of 4- to 6-D tensors with modest index extents (coupled-cluster CCSD, AO2MO style), where TTGT spends much of its time transposing.
- Fixed contraction shapes known ahead of time, where offline autotuning per shape and generating code into your build is acceptable.
- x86-64 with AVX2 and an Intel compiler plus MKL, the configuration the published results used.
- As a reference implementation of GETT packing and macro-kernels to reimplement in your own tensor code.

## Skip it when

- Compute-bound contractions: in the repo's own figures TTGT ties or beats GETT (abcd-aebf-fdec about 67 vs 75 GFLOPS in single precision; TTGT leads on the last four double-precision cases).
- Shapes known only at run time, or index sizes where the product of each input's free-index sizes is not a multiple of 24 (the stated GETT limitation).
- Anything you need to redistribute: the repository has no license file, so the code is all rights reserved.
- Complex numbers or GPUs for GETT: only single and double precision real types (issue #2, 2024, asks for double complex), and CUDA covers only TTGT and LoG.
- Modern Python environments: the generator is Python 2 code (print statements, distutils setup.py) last changed in 2017.

## How it is fast

GETT (GEMM-like Tensor-Tensor multiplication, Springer and Bientinesi, arXiv 1607.00145) applies the BLIS/Goto GEMM blocking directly to tensors: it packs sub-tensors into cache-sized buffers while preserving the stride-one index, then runs an AVX2 or AVX-512 register-blocked macro-kernel, so it never materializes transposed copies the way TTGT does and needs no workspace beyond small tiles. A performance model ranks the blocking and loop-order candidates and the tool then times up to --maxImplementations of them (default 16 for GETT). The gain is largest when the contraction is bandwidth-bound and TTGT's transposes dominate.

## Compared with alternatives

TBLIS is the closer sibling and also avoids explicit transposes with a runtime library interface, so prefer it for production; pick TCCG only to study or reproduce GETT, or to autotune a few fixed bandwidth-bound shapes offline. HPTT is the transposition building block that TCCG's TTGT path itself uses, so it complements rather than replaces this.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | Python 2.7 for the generator; a BLAS (config.cfg defaults to MKL); the HPTT transposition library; the Makefile's CPU target also links TCL's libtcl.so although the README calls TCL optional; cuBLAS for the CUDA path |
| **Minimum toolchain** | Python 2.7 (tested 2.7.5 and 2.7.9); Intel icpc 15+ recommended or g++ 4.8+ (experimental); generated code built with -std=c++11 |
| **Platforms** | x86-64 AVX2 (AVX-512 experimental); NVIDIA CUDA for TTGT and LoG only (config.cfg sets -arch=sm_30) |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | no |

## Gotchas

- The performance model hard-codes the authors' Haswell machine in tccg/arch.py (AVX2: 2.5 GHz, 2 FMAs per cycle, 256 KiB L2, 2 x 30 MiB L3, 13 GiB/s axpy bandwidth; AVX-512: 1.3 GHz), so candidate ranking on other CPUs may be off; raise --maxImplementations to time more variants.
- Small tiles live on the stack by default; --useDynamicMemory is needed if the stack is too small and the help text warns it may degrade performance.
- Tuned solutions are cached in an SQLite database (tccg/tccg.db under TCCG_ROOT) and reused unless --ignoreDatabase is passed.
- Thread affinity is left to the user (--affinity sets KMP_AFFINITY or GOMP_CPU_AFFINITY), and the help text warns that a bad choice hurts performance severely.

## Known shortcomings

- No licence, so reference only; abandoned 2017.
- Record corrected: TCL uses TTGT, not GETT (its README says GETT is planned 'eventually'). Python 2 only; Haswell constants hard-coded in arch.py; no licence.

## Caveats and trade-offs

No LICENSE file in the repository (raw LICENSE, LICENSE.txt, LICENSE.md and COPYING all returned 404 and GitHub shows none), so the code is reference-only even though the sibling HPTT is BSD-3-Clause. The TTGT baseline is the authors' own implementation (HPTT-style transposes plus MKL GEMM) rather than an independent library. Results are single-core, 2016-era hardware and compiler; figures are images, so values are read by eye and approximate. GETT does not win everywhere: on compute-bound contractions TTGT is on par or faster. benchmark.py also drives libtensor, TBLIS, CTF and Eigen scripts (with a hard-coded author path) but the README publishes only the GETT/LoG/TTGT and TCCG-vs-best-of-others figures. The peer-reviewed paper (Springer and Bientinesi, ACM TOMS 2018, arXiv 1607.00145) is not opened (arXiv, ACM and the author's PDF host are blocked); its abstract, seen only as search-engine snippets, reports up to 12.4x over existing approaches for bandwidth-bound contractions and up to 91.3% of peak on compute-bound ones; those numbers are not used above. Abandoned since 2017.

Generator written in Python 2.7 that emits C with AVX2 (AVX-512 experimental; CUDA only for TTGT and LoG); needs Intel icc 15+ (g++ 4.8+ experimental), a BLAS such as MKL, and the HPTT library. GETT has a stated limitation: the product of free-index sizes of each input tensor must be a multiple of 24. Auto-tuning explores up to N candidate implementations at generation time (--maxImplementations). Parallel GETT only on the v0.2.0 branch per the changelog; the published benchmark is single-core.

## Maintenance

Abandoned since 2017-08-14 (47 commits, 40 stars, one branch) and unlicensed, so it is reference-only; the same author's TCL library is also unmaintained and points users to NVIDIA cuTENSOR.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** benchmark/README.md states one core of an Intel Xeon E5-2680 v3, icpc 16.0.1 20151021 with -O3 -xhost -mkl (TurboBoost and SpeedStep off), and the figures (GETT_LoG_TTGT.png, benchmark.png) plot GETT against the MKL-backed TTGT and against max(CTF, naive) / max(CTF, TT, naive); the generator and benchmark scripts (benchmark/benchmark.py, ctf.py, eigen.py, tblis.py, libtensor.py) are public.
- **Verifier notes:** Figure values in the record match what the PNGs show. Metadata confirmed: no license file (LICENSE, LICENSE.txt, LICENSE.md, COPYING all 404; README and setup.py name none), 40 stars, 3 forks, last commit 2017-08-14 (abandoned). Figures date from the benchmark v0.1 / 2016 paper version; the current branch (v0.2) switched to HPTT and parallel GETT, so a re-run would use different code.
- **Fields the verifier corrected:** `claimed_speedup`, `stars_or_usage`
- **Shortcomings recorded by:** verifier; enrichment
- **Pages the verifier opened:**
  - <https://github.com/HPAC/tccg>
  - <https://github.com/HPAC/tccg/tree/master/benchmark>
  - <https://github.com/HPAC/tccg/commits/master>
  - <https://raw.githubusercontent.com/HPAC/tccg/master/benchmark/README.md>
  - <https://raw.githubusercontent.com/HPAC/tccg/master/README.md>
  - <https://raw.githubusercontent.com/HPAC/tccg/master/config.cfg>
  - <https://raw.githubusercontent.com/HPAC/tccg/master/setup.py>
  - <https://raw.githubusercontent.com/HPAC/tccg/master/benchmark/GETT_LoG_TTGT.png>
  - <https://raw.githubusercontent.com/HPAC/tccg/master/benchmark/benchmark.png>
- **Sources the enricher read:**
  - <https://github.com/HPAC/tccg>
  - <https://github.com/HPAC/tccg/tree/master/tccg>
  - <https://github.com/HPAC/tccg/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/HPAC/tccg/master/README.md>
  - <https://raw.githubusercontent.com/HPAC/tccg/master/benchmark/README.md>
  - <https://raw.githubusercontent.com/HPAC/tccg/master/benchmark/GETT_LoG_TTGT.png>
  - <https://raw.githubusercontent.com/HPAC/tccg/master/benchmark/benchmark.png>
  - <https://raw.githubusercontent.com/HPAC/tccg/master/config.cfg>
  - <https://raw.githubusercontent.com/HPAC/tccg/master/setup.py>
  - <https://raw.githubusercontent.com/HPAC/tccg/master/example.tccg>
  - <https://raw.githubusercontent.com/HPAC/tccg/master/scripts/tccg>
  - <https://raw.githubusercontent.com/HPAC/tccg/master/tccg/Makefile>
  - <https://raw.githubusercontent.com/HPAC/tccg/master/tccg/arch.py>
  - <https://raw.githubusercontent.com/HPAC/tccg/master/tccg/gett.py>
  - <https://raw.githubusercontent.com/HPAC/tccg/master/tccg/tccg.py>
  - <https://raw.githubusercontent.com/HPAC/tccg/master/tccg/tccg_util.py>
  - <https://raw.githubusercontent.com/HPAC/tccg/master/tccg/sql_util.py>
  - <https://github.com/springer13/tcl>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/hpac/tccg`) · [data/wave8/enrich/raw/github_com_hpac_tccg.json](../../../data/wave8/enrich/raw/github_com_hpac_tccg.json) (enrichment confidence 0.75)

</details>
