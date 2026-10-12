# Auto-MPFT

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [FFT](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `Apache-2.0` · 🟡 stale

> Research code (KDD 2024) computing only a low-frequency block of 2-D Fourier coefficients faster than a full FFTW/MKL FFT.

| | |
|---|---|
| **Beats** | FFTW 3.3.5 (planning excluded from run time), Intel MKL (version not stated), PFT (snudatalab/PFT, KDD 2021) and FFTW's pruned FFT (fftw.org/pruned.html); all single precision, with tolerances set so every method keeps relative l2 error below 1e-6. |
| **Claimed result** | Paper, real-world datasets (Figure 4): up to 7.6x on Cityscapes, with per-dataset maxima annotated as 7.6x (Cityscapes), 5.7x (ADE20K), 6.9x (DF2K), 2.8x (RiceLeaf) and 2.6x (Bird) over the competitors. Synthetic data: up to 4.7x over the baselines when the input size varies (2^8 x 2^8 to 2^15 x 2^15, output 2^6 x 2^6), and up to 3.3x over PFT and Pruned FFT when the output size varies (input 2^15 x 2^15). The text does not name which competitor each annotated ratio is taken against. Relaxing the tolerance to 1e-4 or 1e-2 cuts Auto-MPFT's own time by up to 21.2% or 49.8% (Table 4; e.g. 133.7 ms at 1e-6 for a 2^5 x 2^5 output from a 2^15 x 2^15 input). |
| **Workload** | 2-D real single-precision arrays: synthetic sets of 1,000 random matrices of size 2^n x 2^n for n = 8..15, and five image datasets (Cityscapes, ADE20K, DF2K, RiceLeaf, Bird) resized to one resolution per set; output is a centered 2^4 x 2^4 to 2^9 x 2^9 block of Fourier coefficients (synthetic: up to 2^13 x 2^13). |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-10700KF @ 3.80GHz, 32GB RAM (paper Section 4.1). Thread count not stated. |
| **Compiler and flags** | Not stated in the paper. The paper says only that all methods are implemented in C++; the repo ships no Makefile or CMake file. |
| **Adoption** | 3 stars, 0 forks, 32 commits |
| **Last commit** | 2025-08-19 |
| **Links** | [repository](https://github.com/snudatalab/Auto-MPFT) · [benchmark](https://raw.githubusercontent.com/yongchanpark/yongchanpark.github.io/gh-pages/resources/2024/KDD/ParkKK24.pdf) |

## Verdict

Peer-reviewed KDD 2024 paper (pp. 2328-2339) whose abstract claims up to 7.6x over partial-FT methods (PFT, pruned FFT) and optimized FFT libraries (FFTW, MKL) at equal accuracy; a WebSearch summary of the paper PDF (not opened, host blocked) places the experiments on an Intel Core i7-10700KF at 3.80 GHz with 32 GB RAM and says PFT is weakest on the smaller images (Cityscapes, ADE20K, DF2K). The 7.6x is a maximum over datasets and baselines; compiler, flags, library versions and per-baseline ratios were not available, and the repository contains no harness to reproduce them.

## Use it when

- You only need a small low-frequency window of the 2-D spectrum of large real images (the paper's sets range from 2048 x 1024 Cityscapes frames to 6000 x 4000 Bird photos) and currently run a full FFTW or MKL FFT and discard most of it.
- Single-precision accuracy targets between 1e-1 and 1e-7 are acceptable (those are the only precomputed tolerance tables).
- You are already on x86-64 with Intel oneMKL and IPP installed and can adapt a research kernel into your own code.
- You want a reference implementation of partial-FT by polynomial twiddle approximation to compare against pruned FFTs or sparse FFTs.

## Skip it when

- You need the full spectrum, complex input, double precision, or 1-D/3-D transforms: the shipped code handles 2-D real float input with a zero-centered target range only (its header says other cases need 'a slight modification', with details only in the paper).
- You need a reusable API: there is no function interface, no build files (no Makefile or CMake), sizes are compile-time constants, and the demo also runs a full MKL FFT before the partial one.
- Non-Intel platforms (Arm, Apple Silicon) or a dependency-free build: the core routines call proprietary Intel MKL and IPP.
- Production use: a 3-star research repository with no tests, no releases and no commits since 2025-08-19.
- Your coefficients of interest are not a contiguous low-frequency block (for a spectrum with a few large coefficients anywhere, a sparse FFT is the better fit).

## How it is fast

Partial Fourier transform: the input is split into p1 x p2 blocks of size q1 x q2, the twiddle factors inside each block are replaced by a truncated multivariate polynomial approximation (precomputed weights for tolerances 1e-1 to 1e-7 in src/precomputed/e-\*.csv), so the block sums become two batched SGEMMs (cblas_sgemm_batch) against small r x q matrices. That leaves r1\*r2 small p1 x p2 real FFTs (one batched MKL DFTI call) plus an elementwise post-processing pass with Intel IPP (ippsMul/ippsAddProduct) and a twiddle multiply, so the cost scales with the output size and the approximation order r rather than with a full N1 x N2 FFT. The 'Auto' part picks p (and hence r) by solving a convex cost model with Newton's method instead of a grid search.

## Compared with alternatives

Pick it over a full-spectrum library such as FFTW, Admiral or VectorFFT only when you need a small zero-centered block of a large 2-D real spectrum and can live with MKL/IPP and research-grade code. Pick MPSFT instead when the 1-D spectrum is sparse with coefficients at unknown positions; Auto-MPFT targets a known contiguous range.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | Intel oneMKL (DFTI, cblas_sgemm_batch, mkl_somatcopy, mkl_malloc) and Intel IPP (ipps complex vector ops); FFTW3 only for the baseline program; the precomputed/e-\*.csv tables must sit at the relative path precomputed/ from the working directory |
| **Minimum toolchain** | not documented; plain C++ (uses the 'and'/'or' alternative tokens); the FFTW baseline includes the Windows-only &lt;tchar.h&gt; and the code defines _USE_MATH_DEFINES, which points to a Visual Studio build |
| **Platforms** | x86-64 only in practice (MKL and IPP); tested CPU not stated in the repo |
| **Thread safety** | not documented; it is a single-threaded main() calling MKL, whose DFTI and GEMM calls use MKL's default internal threading |
| **Drop-in for the baseline** | no |

## Gotchas

- The repository has no timing code at all: Auto-MPFT.cpp, PFT.cpp and FFTW.cpp only compute and print a few coefficients, so the paper's speedups cannot be re-measured from what is committed, and the FFTW baseline hard-codes fftwf_plan_with_nthreads(32), FFTW_MEASURE and a 6000 x 4000 r2c size.
- In the 2-D post-processing loop only the first ippsMul_32fc term is offset to the current (s1, s2) segment of DS; the ippsAddProduct_32fc terms read segment 0, and every segment writes into the same TEMP buffer. With the shipped M = 128, p1 = p2 = 128 there is exactly one segment, so the demo is unaffected, but a larger target range (M &gt; p2 or M &gt; 2\*p1) would give wrong or overwritten output as written (the 1-D PFT.cpp does offset every term).
- Arithmetic is float32 while the tightest table targets 1e-7, close to single-precision epsilon; tolerances below that are not offered.
- The precomputed tables are read with a relative path and stod() without error checks, so running from another directory throws or reads garbage; the demo also keeps about 0.8 MB of pointer arrays on the stack (six arrays of p1\*p2 = 16,384 pointers).

## Known shortcomings

- Repo has no timing code (Auto-MPFT.cpp, FFTW.cpp and PFT.cpp only print coefficients), so the 7.6x claim cannot be reproduced from it; correctness bug: post-processing offsets only the first DS term per segment and every segment writes the same TEMP buffer, so M &gt; p^2 gives wrong output (the shipped M=128, p=128 demo is fine); FFTW baseline hard-codes 32 threads.
- KDD 2024 paper opened (author gh-pages PDF): i7-10700KF 3.80 GHz, 32 GB, single precision, relative L2 below 1e-6, FFTW 3.3.5 with planning excluded; 7.6x is the Cityscapes maximum, the other datasets give 5.7x, 6.9x, 2.8x, 2.6x and synthetic 4.7x, 3.3x. No compiler, flags, thread count or MKL version, so B not A.

## Caveats and trade-offs

Peer-reviewed (KDD 2024) but the README has no result table, hardware or compiler flags, and the 7.6x figure is a maximum over all datasets and baselines (the abstract groups partial-FT methods and optimized FFT libraries together, so the max ratio may not be against FFTW or MKL). The paper PDF (author site, ACM DL, OpenReview) could not be opened from this container, so per-baseline numbers were not read. The baseline file src/FFTW.cpp includes the Windows-only tchar.h, the repo ships no Makefile or CMake file, and the code depends on Intel MKL and Intel IPP (proprietary, free-to-use) for the core routines. Computes only a subset of 2-D Fourier coefficients, not a full FFT. The predecessor PFT (snudatalab/PFT, KDD 2021, C++, Apache-2.0, 16 stars) makes the same kind of claim against FFTW and MKL but its README states no numbers. [retier] The speedups hold only when the output window is much smaller than the input. The paper says that as M approaches N Auto-MPFT runs slightly slower than a full FFT, and Figure 3(a) shows it losing to the baselines in some cases. The 7.6x headline is the single best dataset (Cityscapes); the other datasets give 2.6x to 6.9x, and the paper does not say which competitor each ratio is measured against. Compiler, flags, threading and MKL version are not stated. The paper says code and datasets are at the GitHub repo, but the repo has no build files, src/FFTW.cpp includes the Windows-only tchar.h, and the core routines depend on Intel MKL and IPP. Only a 2-D subset of Fourier coefficients is computed, not a full FFT.

Approximates only a chosen subset of coefficients (partial Fourier transform) and so wins only when the output is much smaller than the input; needs MKL, IPP and FFTW installed to build the comparison code. Hyperparameters chosen automatically by a convex solver.

## Maintenance

Stale research artifact (last commit 2025-08-19, 3 stars) under Apache-2.0, small enough to lift into your own code, but it needs proprietary Intel MKL and IPP and has no build system.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed KDD 2024 paper (README BibTeX gives Proc. 30th ACM SIGKDD, pp. 2328-2339; DOI 10.1145/3637528.3671667 confirmed in search results) whose abstract claims up to 7.6x over partial-FT methods and optimized FFT libraries (FFTW, MKL); the repo README has no result table, no build files, no hardware and no flags, so not A.
- **Verifier notes:** Repo, Apache-2.0 license, 3 stars and last commit 2025-08-19 (README edit) confirmed on github.com; stale is right (13 months). src/ holds Auto-MPFT.cpp (MKL DFTI + IPP), FFTW.cpp, PFT.cpp, Pruned FFT.cpp and Newton.cpp, but no build files. Paper unreachable (openreview.net, dl.acm.org, yongchanpark.github.io all blocked by egress).
- **Fields the verifier corrected:** `caveats`, `stars_or_usage`, `benchmark_url`, `hardware`, `compiler_and_flags`, `baseline`, `claimed_speedup`, `workload`
- **Shortcomings recorded by:** retier check 14 read the KDD 2024 paper
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/snudatalab/Auto-MPFT/HEAD/README.md>
  - <https://raw.githubusercontent.com/snudatalab/Auto-MPFT/HEAD/LICENSE>
  - <https://github.com/snudatalab/Auto-MPFT>
  - <https://github.com/snudatalab/Auto-MPFT/commits>
  - <https://github.com/snudatalab/Auto-MPFT/tree/main/src>
  - <https://raw.githubusercontent.com/snudatalab/Auto-MPFT/HEAD/src/FFTW.cpp>
  - <https://raw.githubusercontent.com/snudatalab/Auto-MPFT/HEAD/src/Auto-MPFT.cpp>
- **Sources the enricher read:**
  - <https://github.com/snudatalab/Auto-MPFT>
  - <https://raw.githubusercontent.com/snudatalab/Auto-MPFT/HEAD/README.md>
  - <https://raw.githubusercontent.com/snudatalab/Auto-MPFT/HEAD/LICENSE>
  - <https://github.com/snudatalab/Auto-MPFT/tree/main/src>
  - <https://github.com/snudatalab/Auto-MPFT/tree/main/src/precomputed>
  - <https://raw.githubusercontent.com/snudatalab/Auto-MPFT/HEAD/src/Auto-MPFT.cpp>
  - <https://raw.githubusercontent.com/snudatalab/Auto-MPFT/HEAD/src/FFTW.cpp>
  - <https://raw.githubusercontent.com/snudatalab/Auto-MPFT/HEAD/src/PFT.cpp>
  - <https://raw.githubusercontent.com/snudatalab/Auto-MPFT/HEAD/src/Pruned%20FFT.cpp>
  - <https://raw.githubusercontent.com/snudatalab/Auto-MPFT/HEAD/src/Newton.cpp>
  - <https://raw.githubusercontent.com/snudatalab/Auto-MPFT/HEAD/src/precomputed/e-7.csv>
  - https://yongchanpark.github.io/resources/2024/KDD/ParkKK24.pdf (EGRESS_BLOCKED; content seen only via WebSearch summaries)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/snudatalab/auto-mpft`) · [data/wave8/enrich/raw/github_com_snudatalab_auto_mpft.json](../../../data/wave8/enrich/raw/github_com_snudatalab_auto_mpft.json) (enrichment confidence 0.7)

</details>
