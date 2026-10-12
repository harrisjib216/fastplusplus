# fCWT

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [FFT](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `Apache-2.0` · 🟡 stale

> Single-precision Morlet continuous wavelet transform on FFTW, OpenMP and AVX; README times it 10-120x faster than other CWT libraries.

| | |
|---|---|
| **Beats** | PyWavelets (pywt.cwt), MATLAB cwt, SciPy, ssqueezepy, CCWT, Rwave (C), Wavelib (C++) and Mathematica CWT implementations |
| **Claimed result** | README: 'Calculating CWT 34-120x faster than all competitors' (C++ performance). Table (seconds, 10k-300 / 10k-3000 / 100k-300 / 100k-3000): fCWT C++ 0.005 / 0.04 / 0.03 / 0.32; CCWT (Python) 0.019 / 0.11 / 0.15 / 3.40; PyWavelets 0.10 / 1.17 / 1.06 / 12.69; Matlab 0.75 / 0.86 / 1.06 / 13.26; ssqueezepy 0.04 / 0.43 / 1.16 / 17.76; SciPy 0.19 / 1.82 / 2.11 / 18.70; Rwave (C) 0.18 / 1.84 / 2.28 / 23.22; Mathematica - / - / - / 27.83; Wavelib (C++) 0.25 / 2.55 / 4.85 / 45.04. README 'speedup factor' column (100k-3000): CCWT 10.63x, PyWavelets 34.29x, Matlab 35.85x, ssqueezepy 48.00x, SciPy 50.54x, Rwave 62.75x, Mathematica 75.20x, Wavelib 121.72x. All factors except CCWT's equal the competitor time divided by 0.37 s, not the table's 0.32 s (CCWT's uses 0.32 s) (derived from page data). The '34-120x than all competitors' headline is contradicted by the README's own CCWT row (10.63x) and shrinks at small sizes: at 10k-300 CCWT is 0.019 s vs 0.005 s (about 3.8x) and ssqueezepy 0.04 s (8x) (derived from page data). Paper abstract (search snippet only): 122 times and 34 times faster than the reference and the fastest state-of-the-art implementations. fCWT Python wrapper 0.66 s and Matlab wrapper 1.55 s at 100k-3000. |
| **Workload** | Continuous wavelet transform of synthetic signals, 10k or 100k samples with 300 or 3000 frequencies; README says fCWT C++ is run with 8 threads and exhaustive FFTW plans (its own benchmark target). |
| **Metric** | latency |
| **Hardware** | MacBook Pro 2019, 2.3 GHz Intel Core i9 (4.5 GHz boost), 16 GB 2400 MHz DDR4 |
| **Compiler and flags** | Compiler not stated. CMakeLists.txt sets '-fPIC -mavx -O2' on Unix ('/arch:AVX /O2' on MSVC), default build type Release, OpenMP; README says FFTW must be built with OpenMP and AVX to reproduce the table. |
| **Adoption** | 402 stars; cited in a Nature Computational Science 2022 paper |
| **Last commit** | 2025-01-06 |
| **Links** | [repository](https://github.com/fastlib/fCWT) · [benchmark](https://github.com/fastlib/fCWT) |

## Verdict

On a 2019 MacBook Pro (Core i9 2.3 GHz, 8 threads, single-precision FFTW with OpenMP and AVX, exhaustive wisdom, -O2 -mavx, compiler not stated), fCWT computed a Morlet CWT of 100k samples x 3000 frequencies in 0.32 s against 3.40 s for CCWT, 12.69 s for PyWavelets 1.1.1, 23.22 s for Rwave and 45.04 s for Wavelib; the README's speedup column divides by 0.37 s, and at 10k samples x 300 frequencies the lead over CCWT is only about 3.8x (derived from page data). Rwave and Wavelib ran single-threaded in double precision, the Python, MATLAB and Mathematica rows ran through their interpreters, and no output equivalence was checked.

## Use it when

- Dense time-frequency maps (hundreds to thousands of frequencies, tens of voices per octave) of long float signals, 10^4 to 10^6 samples: EEG/LFP, audio, vibration scalograms.
- Repeated transforms at a fixed padded length and thread count, where FFTW wisdom computed once with -fcwtoptimize (MEASURE, PATIENT or EXHAUSTIVE) is reused on every call.
- Replacing PyWavelets, SciPy or ssqueezepy Morlet CWTs in Python when single precision is acceptable (README: Python wrapper 0.66 s vs PyWavelets 12.69 s at 100k samples x 3000 frequencies, with different settings per row).
- x86-64 desktops or servers with AVX and around 8 cores; 8 threads was the README setting and the best count reported in issue #83 on a 32-thread Ryzen 9 7945HX.

## Skip it when

- Coarse frequency grids (about 2 voices per octave or fewer): the work buffer is not cleared between scales, so higher-frequency content leaks into lower rows (see gotchas).
- You need double precision, wavelets other than Morlet (issue #60 open), an inverse transform (issue #36 open) or a sample-by-sample streaming CWT (issue #61 open).
- Non-x86 or non-AVX targets: CMakeLists.txt and setup.py hard-code -mavx (/arch:AVX on MSVC); Apple Silicon users report failures (#37 illegal hardware instruction, #69 missing _omp_get_max_threads), and PyPI's latest fcwt 0.1.18 (March 2023) ships only a cp310 macOS x86-64 wheel.
- Long-running services calling cwt() in a loop: every call leaks the padded-length mother table and a padded-length scratch buffer (about 1.5 MB per call at 100k samples).
- Products that cannot take GPL code: the default build links the prebuilt FFTW3f binaries bundled in libs/.

## How it is fast

Scale-independent work is done once per call: one real-to-complex FFTW transform of the signal zero-padded to the next power of two, and one frequency-domain Morlet table of that padded length. Each scale then costs an AVX-vectorized multiply that samples the shared table by nearest index (no per-scale exp calls) over only the bins below twice the scale's centre frequency, followed by one inverse complex FFT. FFTW runs multithreaded through OpenMP with plans tuned ahead of time and saved as wisdom files (n&lt;N&gt;_t&lt;threads&gt;.wis), and the multiply is split across OpenMP threads.

## Compared with alternatives

No other CWT library is catalogued; the fft siblings (KFR, PocketFFT, VkFFT and others) are transform engines a CWT is built on. Pick fCWT when you want a ready Morlet scalogram on x86 CPUs with dense grids; build your own filter bank on PocketFFT or KFR for double precision, other wavelets or non-AVX targets, or on VkFFT/cuFFT for GPU batches.

## Integration

| | |
|---|---|
| **Form** | shared lib by default (BUILD_SHARED_LIBS=ON) or static lib; also a pip package (SWIG extension) and MATLAB MEX files |
| **Dependencies** | FFTW 3.3+ single precision with OpenMP threads (prebuilt fftw3f and fftw3f_omp binaries for macOS, Linux and Windows are bundled in libs/ unless USE_OWN_FFTW=ON; the README says self-built FFTW needs OpenMP and AVX enabled to match the benchmark), OpenMP runtime (libomp or libgomp); Python wrapper needs NumPy and matplotlib |
| **Minimum toolchain** | C++17, CMake 3.10+, GCC 10+, Clang or MSVC 15.7+, OpenMP 5 (README) |
| **Platforms** | x86-64 with AVX (flags hard-coded for Unix and MSVC); the source has a scalar fallback path but the build files must be edited to use it; README says tested on macOS (Intel and Apple Silicon), Windows 10 and Ubuntu 20.04, while issues report Apple Silicon failures |
| **Thread safety** | not documented; cwt() calls omp_set_num_threads, fftwf_init_threads, fftwf_plan_with_nthreads and the FFTW planner (process-global, not thread-safe) and stores the signal length in the object, so serialize calls |
| **Drop-in for the baseline** | no |

## Gotchas

- Stale spectrum between scales (found by reading src/fcwt/fcwt.cpp at HEAD; not reported upstream): the frequency-domain buffer O1 is zeroed once per cwt() call, but each scale writes only the bins below its own endpoint (min(N/2, 2N/scale)) and scales run from smallest to largest, so bins above the current endpoint still hold earlier scales' products when the inverse FFT runs. A numpy model of the loop written for this review shows the effect is negligible on dense grids (benchmark.cpp's 300 log scales with Morlet(1.0): below 5e-8 relative; the README Python example: 2e-4 on its lowest row), but at 1 voice per octave a pure 64 Hz tone appears in the 32, 16 and 8 Hz rows at 96% of its own row's magnitude (about 6e-5 with the buffer cleared), and at 2 voices per octave with Morlet(1.0) at 3.3%. Rows whose scale exceeds twice the padded length get no bins and repeat the previous row, and the per-thread split (endpoint/4 divided by threads, integer division) also skips up to threads-1 AVX vectors at each band's top.
- Odd signal lengths (code reading, not reproduced): each row's inverse FFT is written straight into the n-strided output and fftbased() first passes the row pointer through std::align(16, ...); with odd n every other row starts 8 bytes off a 16-byte boundary, so that row is written one sample late and its first sample is the previous row's padding tail. Each inverse FFT also writes the whole padded length past its row into the next row, which is why rows must be computed in order and the last row goes through a temporary buffer.
- Housekeeping bugs: Morlet::generate() mallocs a new mother table on every cwt() call without freeing the old one, and convolve() never frees lastscalemem (issue #74 was closed in January 2025 but HEAD still lacks the free). Wisdom files are read from and written to the current working directory; a missing file only prints a warning and falls back to FFTW_ESTIMATE plans (issue #30). Python fcwt.cwt() defaults to nthreads=1 and fast=False (no wisdom), and fcwt.plot() at HEAD calls _plot() with one positional argument missing.
- Benchmark harness: the Rwave (C) and Wavelib (C++) rows run double precision on one thread, and src/rwave-bench.cpp uses a Numerical Recipes four1 radix-2 FFT with a malloc per transform, so much of the 62.75x is FFTW against a textbook FFT. benchmark.cpp hard-codes 300 log scales (the 3000-frequency columns need a source edit), uses Morlet(1.0), times wisdom-file reads and planning inside every call, and never compares outputs. The Python notebook (benchmark.ipynb) used FFTW_MEASURE wisdom, linear frequencies 1-101 Hz at fs=100 (above Nyquist; the Scales check is only an assert) and a 3000 x 100k output array for the 10k-sample case.

## Known shortcomings

- Nature Computational Science abstract seen as a snippet only (122x and 34x). The '34-120x than all competitors' claim is contradicted by the repo's own CCWT row (10.63x; 3.8x at 10k-300); fCWT runs 8-thread float against single-thread double Rwave and Wavelib; factors use 0.37 s where the table shows 0.32 s and the benchmark folder README gives different times. Bundles GPL FFTW, so usability is mixed.
- Enricher found an unreported correctness bug in src/fcwt/fcwt.cpp: the O1 buffer is zeroed only once per cwt() call, so bins above each later scale's endpoint keep earlier scales' products (a pure 64 Hz tone shows up in the 32/16/8 Hz rows at 96% with 1 voice per octave; dense grids like benchmark.cpp's 300 log scales are unaffected, so timings stand). Also: odd signal lengths shift every other row by one sample via std::align (code reading), per-call leaks of the mother table and lastscalemem (#74 closed, HEAD still lacks the free), the Rwave row uses a Numerical Recipes four1 FFT in double on 1 thread, the Python notebook asks for 1-101 Hz at fs=100 (above Nyquist), the only PyPI wheel is cp310 macOS x86-64 and -mavx is hard-coded. Downgraded B to C (uniwidth precedent: bug in the measured hot path).

## Caveats and trade-offs

Evidence is the README table, which the README ties to the Nature Computational Science paper (Arts and van den Broek, 2022, cover article); the paper could not be opened (nature.com, doi.org and the PMC copy PMC10766549 blocked), and the abstract's 122x/34x was seen only in a search snippet. Harness asymmetries in src/benchmark.cpp: fCWT runs in single precision (float) with 8 threads and exhaustive FFTW plans, while the Rwave and Wavelib rows run double precision single-threaded (rwave::cwt and wavelib cwt take no thread count); the Python (cwtbench.py) and Matlab/Mathematica rows run through interpreters with default threading. benchmark.cpp hard-codes 300 frequencies (noct 6 x nvoi 50) and 5 runs, so the 3000-frequency C++ columns need source edits; cwtbench.py uses 3000 scales. src/benchmark/README.md reports different competitor times from the main table (MATLAB 18.28 s, Mathematica 38.86 s, PyWavelets 12.59 s, SciPy 19.56 s). The speedup factors use 0.37 s for fCWT (probably the paper's figure) while the table shows 0.32 s, and CCWT's 10.63x contradicts the '34-120x faster than all competitors' headline. The Matlab row (0.75 s at 10k-300 vs 0.86 s at 10k-3000) looks odd. No output equivalence check between implementations in the harness. Compiler not stated; CMakeLists.txt sets -fPIC -mavx -O2 on Unix with OpenMP. The default build links prebuilt FFTW (fftw3f) binaries bundled in libs/, which are GPL-2.0-or-later, hence usability mixed. Baselines are other CWT libraries, not an FFT incumbent; fCWT is a CWT built on FFTW, a weak fit for the fft category. [retier] Nature Computational Science abstract seen as a snippet only (122x and 34x). The '34-120x than all competitors' claim is contradicted by the repo's own CCWT row (10.63x; 3.8x at 10k-300); fCWT runs 8-thread float against single-thread double Rwave (Numerical Recipes four1 FFT) and Wavelib; factors use 0.37 s where the table shows 0.32 s and the benchmark folder README gives different times. Correctness: src/fcwt/fcwt.cpp zeroes the O1 buffer only once per cwt() call, so bins above each later scale's endpoint keep earlier scales' products (a pure 64 Hz tone appears in the 32/16/8 Hz rows at 96% with 1 voice per octave, 3.3% with 2 voices and Morlet(1.0); dense grids such as benchmark.cpp's 300 log scales are unaffected); odd signal lengths shift every other row by one sample via std::align; per-call leaks of the mother table and lastscalemem (#74 closed without the free). The Python notebook asks for 1-101 Hz at fs=100 (above Nyquist); the only PyPI wheel is cp310 macOS x86-64; -mavx is hard-coded. Bundles GPL FFTW, so usability is mixed.

Single-precision (float) CWT with Morlet wavelet; built on FFTW with OpenMP and AVX. The repo's libs/ directory ships prebuilt FFTW3 binaries (fftw3f, OpenMP) and omp.h; FFTW is GPL-2.0-or-later, so the fCWT source is Apache-2.0 but a build linking those binaries is GPL. Python (pip fcwt) and MATLAB MEX wrappers are slower than the C++ build (README says Matlab path loses performance).

## Maintenance

Stale: last commit 2025-01-06 (two merged cleanup and plotting PRs), last PyPI release 0.1.18 in March 2023, and recent issues (#66 out-of-band energy, #69, #83) have no maintainer reply; Apache-2.0 source but the default build links bundled GPL FFTW binaries (usability mixed), and the stale-spectrum and odd-length row bugs found here mean results on coarse grids or odd lengths should be checked against a reference CWT.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now C.
- **Tier reason:** Peer-reviewed Nature Computational Science 2022 paper (abstract via search snippet only: 122x and 34x faster than the reference and the fastest state-of-the-art implementations) matches the README speedup-factor column; the README table and public harness (src/benchmark.cpp, src/benchmark/cwtbench.py) name the MacBook Pro 2019 i9 but no compiler, so not A.
- **Retiered** B to C: Downgraded B to C: enricher found an unreported correctness bug in the measured cwt() hot path (O1 buffer zeroed once per call, so sparse scale grids inherit earlier scales' products; the paper's and benchmark.cpp's dense 300-scale grids are unaffected, so the timings are real but measured on buggy code; uniwidth precedent). The Nature Computational Science paper was seen only as an abstract snippet.
- **Verifier notes:** Tier B confirmed on the peer-reviewed paper (abstract via search snippet only); README numbers match the record. Shortcomings: headline '34-120x than all competitors' contradicted by its own CCWT row (10.63x) and much smaller at 10k-300 (3.8x vs CCWT); 8-thread float fCWT vs single-thread double Rwave/Wavelib; speedup factors computed against 0.37 s not the table's 0.32 s; benchmark folder README gives different competitor times. Apache-2.0, 402 stars, 84 forks confirmed on github.com; last commit 2025-01-06 confirmed (commits atom feed), so stale.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** first-party table (verifier); enricher code reading
- **Pages the verifier opened:**
  - <https://github.com/fastlib/fCWT>
  - <https://raw.githubusercontent.com/fastlib/fCWT/HEAD/README.md>
  - <https://raw.githubusercontent.com/fastlib/fCWT/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/fastlib/fCWT/HEAD/src/benchmark.cpp>
  - <https://raw.githubusercontent.com/fastlib/fCWT/HEAD/src/wavelib-bench.cpp>
  - <https://raw.githubusercontent.com/fastlib/fCWT/HEAD/src/rwave-bench.cpp>
  - <https://raw.githubusercontent.com/fastlib/fCWT/HEAD/LICENSE.txt>
  - <https://github.com/fastlib/fCWT/tree/main/src>
  - <https://github.com/fastlib/fCWT/tree/main/src/benchmark>
  - <https://raw.githubusercontent.com/fastlib/fCWT/HEAD/src/benchmark/README.md>
  - <https://raw.githubusercontent.com/fastlib/fCWT/HEAD/src/benchmark/cwtbench.py>
  - <https://github.com/fastlib/fCWT/commits/main.atom>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/fastlib/fCWT/HEAD/README.md>
  - <https://raw.githubusercontent.com/fastlib/fCWT/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/fastlib/fCWT/HEAD/setup.py>
  - <https://raw.githubusercontent.com/fastlib/fCWT/HEAD/src/fcwt/fcwt.h>
  - <https://raw.githubusercontent.com/fastlib/fCWT/HEAD/src/fcwt/fcwt.cpp>
  - <https://raw.githubusercontent.com/fastlib/fCWT/HEAD/src/fcwt/boilerplate.py>
  - <https://raw.githubusercontent.com/fastlib/fCWT/HEAD/src/main.cpp>
  - <https://raw.githubusercontent.com/fastlib/fCWT/HEAD/src/benchmark.cpp>
  - <https://raw.githubusercontent.com/fastlib/fCWT/HEAD/src/wavelib-bench.cpp>
  - <https://raw.githubusercontent.com/fastlib/fCWT/HEAD/src/rwave-bench.cpp>
  - <https://raw.githubusercontent.com/fastlib/fCWT/HEAD/src/benchmark/README.md>
  - <https://raw.githubusercontent.com/fastlib/fCWT/HEAD/src/benchmark/cwtbench.py>
  - <https://raw.githubusercontent.com/fastlib/fCWT/HEAD/benchmark.ipynb>
  - <https://github.com/fastlib/fCWT/tree/main/src/benchmark>
  - <https://github.com/fastlib/fCWT/tree/main/src/fcwt>
  - <https://github.com/fastlib/fCWT/tree/main/libs>
  - <https://github.com/fastlib/fCWT/commits/main>
  - <https://github.com/fastlib/fCWT/issues?q=is%3Aissue>
  - <https://github.com/fastlib/fCWT/issues?page=2&q=is%3Aissue>
  - <https://github.com/fastlib/fCWT/issues/83>
  - <https://github.com/fastlib/fCWT/issues/74>
  - <https://github.com/fastlib/fCWT/issues/66>
  - <https://github.com/fastlib/fCWT/issues/69>
  - <https://github.com/fastlib/fCWT/issues/49>
  - <https://pypi.org/pypi/fcwt/json>
  - <https://pypi.org/pypi/pyfcwt/json>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/fastlib/fcwt`) · [data/wave8/enrich/raw/github_com_fastlib_fcwt.json](../../../data/wave8/enrich/raw/github_com_fastlib_fcwt.json) (enrichment confidence 0.8)

</details>
