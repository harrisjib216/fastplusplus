# PFT (Partial Fourier Transform)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [FFT](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `Apache-2.0` · 🟡 stale

> Research C++ code computing only M of N Fourier coefficients with polynomial-approximated twiddles; up to 19x over FFTW/MKL.

| | |
|---|---|
| **Beats** | FFTW (real-to-complex 1D, FFTW_ESTIMATE), Intel MKL DFTI, FFTW pruned FFT, Goertzel algorithm |
| **Claimed result** | Per the authors' KDD 2021 paper (text seen only as a search snippet, not on any opened page): an order of magnitude speedup for sufficiently small output sizes without sacrificing accuracy, outperforming FFTW, MKL, pruned FFT and Goertzel. No number appears in the repo. |
| **Workload** | Partial Fourier transform of length N up to 2^22 computing M output coefficients (Table 3 best 1.273 ms at M=2^9, N=2^22), single precision, relative L2 error below 1e-6, versus FFTW 3.3.5, MKL and pruned FFTW with planning time excluded (paper Section 5). |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-6700HQ 2.60 GHz, 8 GB RAM (paper Section 5); compiler, flags and thread count not stated. |
| **Adoption** | 16 stars, 3 forks; KDD 2021 paper |
| **Last commit** | 2025-08-19 |
| **Links** | [repository](https://github.com/snudatalab/PFT) · [benchmark](https://raw.githubusercontent.com/yongchanpark/yongchanpark.github.io/gh-pages/resources/2021/KDD/ParkJK21.pdf) |

## Verdict

The KDD 2021 paper (read from the author's GitHub Pages repository) times PFT on an Intel Core i7-6700HQ @ 2.60 GHz with 8 GB RAM, in single precision at relative L2 error below 1e-6, averaged over 100 runs of 1000 random vectors: up to 19x faster than FFTW 3.3.5 (planning excluded), MKL and pruned FFTW for the target range R_{0,2^9} as N grows to 2^22, with the best setting at N = 2^22 taking 1.273 ms for M = 2^9 and 11.924 ms for M = 2^18 (Table 3). The compiler, flags, MKL version and thread count are not stated, and the repository has no timing harness.

## Use it when

- You need only a small contiguous band (e.g. the lowest frequencies) of the spectrum of a long real series: the paper reports PFT beating the full FFT for M &lt; 2^19 at N = 2^22, with the largest gains when the output is under about 10% of the input.
- Many transforms with the same N, M and tolerance, so the precomputed B, D, twiddle tables and DFTI descriptors amortize (batch feature extraction, sliding windows, the paper's anomaly detection at about 8x over FFT).
- Single-precision results at a stated tolerance such as 1e-6 relative L2 error, or looser: relaxing to 1e-4 or 1e-2 cut a further 17% or 27% in the paper.
- Intel x86 machines where MKL and IPP are already part of the build.
- Lengths with a convenient divisor p, including non-powers of two (the paper runs N = 32000).

## Skip it when

- M close to N or the full spectrum: the O(N) pre-processing and post-processing overhead makes it slower than a plain FFT (Table 3 omits settings that lost to FFT).
- Exact or double-precision coefficients: it is an approximation, and the sample is float-only.
- N prime or with only awkward divisors: the paper's N = 19735 = 5 x 3947 forced p = 3947.
- ARM, non-Intel or fully open-source builds: it depends on proprietary Intel MKL and IPP.
- Sparse spectra at unknown positions (use a sparse FFT), or production code needing an API, tests or maintenance: this is a 2021 research sample with hard-coded parameters and no timing harness.

## How it is fast

The input is viewed as a p x q matrix (N = p\*q) and the q-dependent twiddle factors are replaced by a degree-r minimax polynomial approximation of e^(pi\*i\*x), whose coefficients are precomputed per tolerance in src/precomputed/e-\*.csv. The inner sums then collapse into one r x q by q x p SGEMM (O(rN)), r batched real FFTs of size p (O(r p log p)) and an elementwise post-processing pass over powers of the output index and twiddles (IPP ippsMul/ippsAddProduct, cblas_saxpy). The paper gives O((N + M log M) log(1/eps)) versus O(N log N), with r growing as M/p grows or the tolerance tightens; the heavy steps run in MKL BLAS and DFTI.

## Compared with alternatives

Pick PFT over full-spectrum libraries (FFTW, Admiral, VectorFFT, PocketFFT) only when you need a small contiguous band of a long 1-D real series; for 2-D blocks use Auto-MPFT, the same group's KDD 2024 successor with automatic choice of p, and for sparse spectra at unknown positions use MPSFT or SFFT.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | Intel MKL (cblas_sgemm, cblas_saxpy, DFTI), Intel IPP (ipps), the precomputed CSV tables in src/precomputed; FFTW 3 only for the baseline programs |
| **Minimum toolchain** | not documented; any C++ compiler supported by MKL and IPP (the code is C++98-style); the FFTW.cpp baseline includes the Windows-only tchar.h |
| **Platforms** | x86-64 with Intel MKL and IPP (paper machine: Intel Core i7-6700HQ); others not documented |
| **Thread safety** | not documented; everything lives in local buffers inside main(), and MKL/IPP default threading applies |
| **Drop-in for the baseline** | no |

## Gotchas

- The tolerance table is read from the relative path precomputed/&lt;tol&gt;.csv with no open or parse check, so running outside src/ ends in a std::stod exception.
- q = N / p uses integer division with no check that p divides N, and r is capped at 27 by the 26-entry threshold table (M/p up to about 3.9 at 1e-7).
- The sample assumes real input and a target range centered at zero; another center needs the modulation step from the paper, which makes the input complex.
- The repo's FFTW.cpp (FFTW_ESTIMATE, 4 threads, N = 2^20, no timer read) is not the paper's baseline ('optimized FFTW 3.3.5' with planning excluded), so do not reuse it as a fair comparison.

## Known shortcomings

- Downgraded B to C: README bibtex confirms KDD 2021, but the paper could not be opened and the snippet could not be tied to the abstract. No timing harness; the FFTW baseline uses FFTW_ESTIMATE; needs proprietary MKL/IPP.
- Retiered C to B on the KDD 2021 paper (opened via the author's gh-pages PDF). The repo's FFTW.cpp baseline (FFTW_ESTIMATE, 4 threads, N=2^20, timer never read) is not the paper's baseline. Reads precomputed/&lt;tol&gt;.csv by relative path with no check, does not check that p divides N, and needs MKL plus IPP.

## Caveats and trade-offs

(1) Snippet only: the paper (ACM DOI 10.1145/3447548.3467293, arXiv 2008.12559) could not be opened here (dl.acm.org, arXiv, openreview and yongchanpark.github.io are egress-blocked; the yongchanpark.github.io GitHub repo holds only an empty README), so CPU model, compiler, flags and the actual ratios are unknown. The KDD 2021 venue itself is confirmed by the repo README's citation. Retier to B if a session with ACM or arXiv access confirms the abstract and tables. (2) No timing harness in the repo: src/PFT.cpp prints the first and last coefficients and the relative L2 error against the MKL DFTI full FFT and has no timers; src/FFTW.cpp declares clock_t variables but never reads them; src/PrunedFFTW.cpp is the FFTW pruned-FFT web-page pseudocode and does not compile as is; src/goertzel.c is copied from pramasoul/jrand. (3) The FFTW baseline in src/FFTW.cpp is a 1,048,576-point float r2c transform on 4 threads planned with FFTW_ESTIMATE (FFTW_MEASURE only in a comment), weaker than a tuned FFTW; it includes the Windows-only tchar.h. (4) PFT.cpp's header says the example is designed for real-valued input with a target range centered at zero; other ranges need the modification described in the paper. (5) Building needs Intel MKL and IPP (proprietary but freely redistributable) in addition to the Apache-2.0 code. (6) Last commit 2025-08-19 is a README edit; the last source change is 'Update PFT.cpp' on 2021-06-03 (github.com commits page). (7) Follow-up multidimensional work (snudatalab/Auto-MPFT, KDD 2024) was not opened.

Approximate, not exact: error is selectable from e-1 to e-7 through precomputed polynomial coefficient files (src/precomputed). The sample code is written for real-valued input and a target output range centered at zero (the file header says a small modification removes this limit). Single precision throughout. Needs Intel MKL and IPP (mkl.h, mkl_dfti.h, ipp.h, ipps.h) plus fftw3.h. Gains only when M is much smaller than N (O(N + M log M) instead of O(N log N)). Research sample code, not a packaged library.

## Maintenance

Stale research code (last source change 2021-06-03, README edits through 2025-08-19); Apache-2.0 and small enough to copy, but it needs proprietary MKL and IPP and must be refactored out of main() before use.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification B, tier now B.
- **Tier reason:** The venue is confirmed as peer-reviewed (the README cites KDD 2021, pp. 1309-1318, and links the ACM DOI), but I could not open the paper (dl.acm.org, arXiv and the author site are egress-blocked) and could not confirm that the 'order of magnitude' snippet is the KDD abstract rather than the arXiv preprint, so per the snippet-only rule it drops to C. The repo has no timing harness (PFT.cpp prints coefficients and L2 error only; FFTW.cpp never reads its timers), so A is unavailable.
- **Retiered** C to B: Peer-reviewed KDD 2021 paper opened by the enricher via the author's gh-pages copy (resources/2021/KDD/ParkJK21.pdf): FFTW 3.3.5 and MKL baselines with planning excluded, i7-6700HQ 2.60 GHz, 8 GB, single precision, relative L2 error below 1e-6, up to 19x over FFTW, MKL and pruned FFTW; compiler, flags and thread count are not stated, so not A.
- **Verifier notes:** Downgraded B to C: KDD 2021 (peer-reviewed) is confirmed by the README, but the speedup text is snippet only and the paper could not be opened. Metadata (Apache-2.0, 16 stars, 3 forks, last commit 2025-08-19, stale) confirmed.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `caveats`, `hardware`, `workload`
- **Shortcomings recorded by:** verifier; enricher opened the KDD 2021 paper
- **Pages the verifier opened:**
  - <https://github.com/snudatalab/PFT>
  - <https://raw.githubusercontent.com/snudatalab/PFT/HEAD/README.md>
  - <https://github.com/snudatalab/PFT/tree/main/src>
  - <https://raw.githubusercontent.com/snudatalab/PFT/HEAD/src/PFT.cpp>
  - <https://raw.githubusercontent.com/snudatalab/PFT/HEAD/src/FFTW.cpp>
  - <https://raw.githubusercontent.com/snudatalab/PFT/HEAD/src/PrunedFFTW.cpp>
  - <https://github.com/snudatalab/PFT/commits/main>
  - <https://github.com/yongchanpark/yongchanpark.github.io>
  - <https://github.com/yongchanpark/yongchanpark.github.io/tree/main>
  - <https://raw.githubusercontent.com/yongchanpark/yongchanpark.github.io/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/snudatalab/PFT/tree/main/src>
  - <https://github.com/snudatalab/PFT/tree/main/src/precomputed>
  - <https://github.com/snudatalab/PFT/commits/main>
  - <https://raw.githubusercontent.com/snudatalab/PFT/HEAD/README.md>
  - <https://raw.githubusercontent.com/snudatalab/PFT/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/snudatalab/PFT/HEAD/src/PFT.cpp>
  - <https://raw.githubusercontent.com/snudatalab/PFT/HEAD/src/FFTW.cpp>
  - <https://raw.githubusercontent.com/snudatalab/PFT/HEAD/src/PrunedFFTW.cpp>
  - <https://raw.githubusercontent.com/snudatalab/PFT/HEAD/src/goertzel.c>
  - <https://raw.githubusercontent.com/snudatalab/PFT/HEAD/src/precomputed/e-7.csv>
  - <https://raw.githubusercontent.com/yongchanpark/yongchanpark.github.io/gh-pages/resources/2021/KDD/ParkJK21.pdf>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/snudatalab/pft`) · [data/wave8/enrich/raw/github_com_snudatalab_pft.json](../../../data/wave8/enrich/raw/github_com_snudatalab_pft.json) (enrichment confidence 0.8)

</details>
