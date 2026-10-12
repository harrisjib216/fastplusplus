# MPSFT (Matrix Pencil Sparse Fourier Transform)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [FFT](README.md)</sub>

**Tier A** (reproducible public benchmark) · Study only · `C++` · `no license` · 🔴 abandoned

> Research sparse Fourier transform (C++11) that recovers S dominant modes of a huge noisy spectrum faster than a full FFTW transform.

| | |
|---|---|
| **Beats** | FFTW (FFTW_ESTIMATE and FFTW_MEASURE plans) |
| **Claimed result** | At N=4194301 (prime near 2^22) MPSFT takes 19.4 ms at S=64, 75.8 ms at S=512, 140.8 ms at S=1024 and 263.4 ms at S=2048; FFTW at N=4194304 takes 225.3 ms with FFTW_ESTIMATE (benchmark arg 64) and 102.3 ms with FFTW_MEASURE (arg 0). The README and report say it is faster than FFTW when S is below about 1800, which is the FFTW_ESTIMATE crossover; the README also says S must be around 1000 to beat FFTW, matching FFTW_MEASURE. Derived from page data: 5.3x faster than FFTW_MEASURE and 11.6x faster than FFTW_ESTIMATE at S=64; break-even against FFTW_MEASURE between S=512 and S=1024. |
| **Workload** | Sparse Fourier transform of an N=2^22 signal with S nonzero frequencies, single core, Google Benchmark, FFTW built from source on the same machine. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-6700K, 4 GHz (report/report.pdf section 4.1) |
| **Compiler and flags** | gcc (version not stated; the report discusses gcc autovectorization and .bazelrc uses the GCC-only -fopt-info-vec-optimized), Bazel --config=opt: -std=c++11 -O3 -ffast-math -mavx2 -mtune=native -fopenmp-simd -g0 -DNDEBUG; FFTW 3.3.6-pl2 compiled locally with -O3 -mtune=native -ffast-math (report section 4.1); CPU scaling disabled; single-threaded. |
| **Adoption** | 6 stars |
| **Last commit** | 2017-09-03 |
| **Links** | [repository](https://github.com/jiaweichiu/mpsft) · [benchmark](https://github.com/jiaweichiu/mpsft) |

## Verdict

Single-core Google Benchmark runs on an Intel i7-6700K at 4 GHz (CPU scaling off), gcc with -O3 -ffast-math -mavx2, against a locally built FFTW 3.3.6-pl2: MPSFT at prime N=4194301 took 19.4/75.8/140.8/263.4 ms for S=64/512/1024/2048, while full FFTW transforms at N=4194304 took 225.3 ms (FFTW_ESTIMATE) and 102.3 ms (FFTW_MEASURE). So it wins by 5.3x over FFTW_MEASURE at S=64 and breaks even between S=512 and 1024 (derived from page data); the report's '&lt;1800' crossover is against FFTW_ESTIMATE only.

## Use it when

- Very long 1-D complex signals (N around 2^22 or more) whose spectrum is known to be dominated by a few hundred to about a thousand tones plus noise, and you only need those tones.
- Fixed N with S well below \~1000 (against FFTW_MEASURE) or \~1800 (against FFTW_ESTIMATE): at S=64 it took 19.4 ms vs 102 ms (MEASURE) for a full 2^22 FFTW transform.
- Workloads where N grows but S stays small: at S=50 runtime rose only from 7.7 ms (N=8191) to 20.5 ms (N=16777213) in the README table.
- Studying or prototyping SFT algorithms; the code is small and the report explains each step (binning, matrix pencil, symmetry trick).

## Skip it when

- Dense or moderately sparse spectra: at N\~2^22 it loses to FFTW_MEASURE somewhere between S=512 and S=1024 (140.8 ms at S=1024 vs 102.3 ms).
- When you need an exact DFT: output is a probabilistic set of approximate modes; modes can be missed or spurious ones added.
- Small or medium N, multi-dimensional, real-to-complex or batched transforms: none are implemented.
- Production use: abandoned since 2017, no releases, no tests of robustness beyond the synthetic model, and the authors' own report says it is not competitive with sFFT1/sFFT2 at N\~2^22 (it only overtakes them at N &gt;= 2^23 / 2^25 with S=50).
- Projects that cannot take GPL code (source headers are GPL-2.0-or-later) or the dated Boost.SIMD dependency.

## How it is fast

It follows the sFFT-style framework: a random spectral permutation and modulation (k -&gt; a\*k+b mod N) isolates modes into B \~ 2S+1 bins, and binning runs in the time domain with a Gaussian-smoothed boxcar window of support O(B log(1/delta)), followed by a small B-point FFTW transform. Each bin's mode location is decoded one bit at a time by sampling shifts tau = q +/- 2^s B and running a 2x2 matrix pencil SVD (Eigen JacobiSVD), which also rejects bins with mode collisions; an even/odd symmetry trick halves the number of sin/cos evaluations. The hot loop (BinInTime) is vectorized with OpenMP SIMD and Boost.SIMD sincos, which the report credits with at least 2x.

## Compared with alternatives

Pick MPSFT over dense FFTs (FFTW, PocketFFT, KFR) only when the spectrum is truly sparse and you do not know where the peaks are; Auto-MPFT fits when you know which output coefficients you need, and FINUFFT is for non-uniform samples, not sparse spectra.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | FFTW3 (small inner FFTs), Eigen3 (2x2 SVD), Boost.SIMD (boost/simd/\* sincos), glog, Google Benchmark (benchmarks only), gperftools (demo1_main links -lprofiler); built with Bazel |
| **Minimum toolchain** | C++11 with GCC (Bazel opt config passes -std=c++11 -O3 -ffast-math -mavx2 -fopenmp-simd and the GCC-only -fopt-info-vec-optimized); compiler versions not documented |
| **Platforms** | x86-64 Linux as configured (opt config requires AVX2; links -lrt); other platforms not documented |
| **Thread safety** | Not thread-safe as written: Iterate and Transform draw random shifts from a single global, unsynchronized std::mt19937 in base.cc; nothing else documented. |
| **Drop-in for the baseline** | no |

## Gotchas

- N should be prime: Transform draws any a in [1, N-1] and inverts it mod N, which only always works for prime N; all benchmarks use primes near powers of two (kPrimes table, 4194301 for 2^22) while FFTW was timed at exact powers of two.
- Caller must know S and the noise level sigma: Demo1 sets bins = 2\*(S - found)+1 (min 51), bin_threshold = 3 sigma/sqrt(B) and sv_threshold = sigma/sqrt(B); wrong values change both speed and recovery.
- Spectrum convention is x_hat_k = (1/N) sum x_t e^(-2 pi i k t/N) (report), unlike FFTW's unnormalized forward transform; results come back as std::unordered_map&lt;int32_t, complex&lt;double&gt;&gt;.
- Array&lt;T&gt; in base.h frees its buffer in the destructor but has no user-defined copy constructor, so copying a CplexArray shallow-copies the pointer and double-frees; call mps::MainInit first (seeds the RNG with a fixed seed and builds division magic numbers).

## Known shortcomings

- The 1800 figure is against FFTW_ESTIMATE; against FFTW_MEASURE the crossover is S\~1000; MPSFT runs at prime N while FFTW runs at a power of two; loses to sFFT1 and sFFT2 at N\~2^22.
- Array&lt;T&gt; in base.h frees its buffer but has no copy constructor (copy double-frees); one global unsynchronized mt19937 (not thread-safe); works only for prime N; source headers say GPL-2.0-or-later (record had no license).

## Caveats and trade-offs

Wins hold only for sparse spectra (S below about 1000 against FFTW_MEASURE). MPSFT is timed at prime N=4194301 while FFTW runs at the power of two 4194304, FFTW's best case. The report says MPSFT is not competitive with sFFT1 or sFFT2 at N near 2^22 (they win there; MPSFT only overtakes them at larger N with S=50). The input model is a noisy sparse spectrum (sigma=0.1), and MPSFT returns approximate modes, not an exact DFT. The report is explicitly 'not a formal publication'. GPL-2.0 text is in src/COPYING.txt; whether 'or later' applies is not stated. The README says it plans to drop the FFTW dependency (KissFFT), which never happened. Last commit 2017.

Only useful for signals that are exactly or nearly sparse in frequency; approximate output; depends on FFTW, Eigen and Boost.SIMD.

## Maintenance

Abandoned research code (last commit 2017-09-03, 6 stars, no issues or releases), GPL-2.0-or-later per the source headers; useful as a reference implementation of matrix-pencil SFT, not as a maintained library.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded from C. The README tables come from the public Google Benchmark targets (demo1_bench and the FFTW bench, built with Bazel --config=opt from src/.bazelrc). The repo's report/report.pdf (section 4.1, same parameters as the README) names the CPU (Intel i7-6700K 4 GHz, scaling off, single core), the compiler (gcc) and flags for MPSFT and for the locally built FFTW 3.3.6-pl2. The gcc version is not stated.
- **Verifier notes:** Numbers verified; the FFTW block mapping is confirmed by FFTW's flag values (FFTW_ESTIMATE = 64, FFTW_MEASURE = 0 in the benchmark names). The report PDF in the repo supplies the CPU and flags, so I upgraded C to A. The '1800' headline is against FFTW_ESTIMATE only.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/jiaweichiu/mpsft/HEAD/README.md>
  - <https://github.com/jiaweichiu/mpsft>
  - <https://github.com/jiaweichiu/mpsft/commits/master>
  - <https://raw.githubusercontent.com/jiaweichiu/mpsft/HEAD/src/COPYING.txt>
  - <https://raw.githubusercontent.com/jiaweichiu/mpsft/HEAD/src/.bazelrc>
  - <https://raw.githubusercontent.com/jiaweichiu/mpsft/HEAD/report/report.pdf>
- **Sources the enricher read:**
  - <https://github.com/jiaweichiu/mpsft>
  - <https://github.com/jiaweichiu/mpsft/tree/master/src>
  - <https://github.com/jiaweichiu/mpsft/commits/master>
  - <https://github.com/jiaweichiu/mpsft/tree/master/report2>
  - <https://raw.githubusercontent.com/jiaweichiu/mpsft/HEAD/README.md>
  - <https://raw.githubusercontent.com/jiaweichiu/mpsft/HEAD/report/report.pdf>
  - <https://raw.githubusercontent.com/jiaweichiu/mpsft/HEAD/report2/report.pdf>
  - <https://raw.githubusercontent.com/jiaweichiu/mpsft/HEAD/report3/report.pdf>
  - <https://raw.githubusercontent.com/jiaweichiu/mpsft/HEAD/src/BUILD>
  - <https://raw.githubusercontent.com/jiaweichiu/mpsft/HEAD/src/.bazelrc>
  - <https://raw.githubusercontent.com/jiaweichiu/mpsft/HEAD/src/base.h>
  - <https://raw.githubusercontent.com/jiaweichiu/mpsft/HEAD/src/base.cc>
  - <https://raw.githubusercontent.com/jiaweichiu/mpsft/HEAD/src/binner.h>
  - <https://raw.githubusercontent.com/jiaweichiu/mpsft/HEAD/src/binner.cc>
  - <https://raw.githubusercontent.com/jiaweichiu/mpsft/HEAD/src/iterate.h>
  - <https://raw.githubusercontent.com/jiaweichiu/mpsft/HEAD/src/iterate.cc>
  - <https://raw.githubusercontent.com/jiaweichiu/mpsft/HEAD/src/freqid.h>
  - <https://raw.githubusercontent.com/jiaweichiu/mpsft/HEAD/src/freqid.cc>
  - <https://raw.githubusercontent.com/jiaweichiu/mpsft/HEAD/src/demo1.h>
  - <https://raw.githubusercontent.com/jiaweichiu/mpsft/HEAD/src/demo1.cc>
  - <https://raw.githubusercontent.com/jiaweichiu/mpsft/HEAD/src/demo1_bench.cc>
  - <https://raw.githubusercontent.com/jiaweichiu/mpsft/HEAD/src/fftw_bench.cc>
  - <https://raw.githubusercontent.com/jiaweichiu/mpsft/HEAD/src/window.h>
  - <https://raw.githubusercontent.com/jiaweichiu/mpsft/HEAD/src/window.cc>
  - <https://raw.githubusercontent.com/jiaweichiu/mpsft/HEAD/src/integer.h>
  - <https://raw.githubusercontent.com/jiaweichiu/mpsft/HEAD/src/integer.cc>
  - <https://raw.githubusercontent.com/jiaweichiu/mpsft/HEAD/src/sincos.h>
  - <https://raw.githubusercontent.com/jiaweichiu/mpsft/HEAD/src/sincos.cc>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/jiaweichiu/mpsft`) · [data/wave8/enrich/raw/github_com_jiaweichiu_mpsft.json](../../../data/wave8/enrich/raw/github_com_jiaweichiu_mpsft.json) (enrichment confidence 0.8)

</details>
