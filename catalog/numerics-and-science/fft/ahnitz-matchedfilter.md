# matchedfilter (formerly peak-fft)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [FFT](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C core with Python bindings; GPU kernels in Slang (Vulkan/Metal)` · `MIT` · 🟢 active

> Fused batched matched filter (spectral product, inverse FFT, peak scan) for data x template banks; peak-only mode beats FFTW's inverse-only time.

| | |
|---|---|
| **Beats** | FFTW (inverse transform only, timed through pyFFTW); on GPU rocFFT / MLX FFT inverse-only references |
| **Claimed result** | Milliseconds per batch (16 x 512 x 4096-point complex64, one thread), FFTW inverse-only vs matchedfilter full / peak-only / hierarchical fd=0.01 at SNR 5.5: Ryzen 9 5950X 63.63 vs 52.23 / 34.27 / 3.95; Ryzen AI Max+ 395 69.54 vs 35.12 / 20.68 / 3.12; Ryzen 5 5500U 87.45 vs 73.70 / 49.37 / 6.11; Core i5-13500H 44.96 vs 56.24 / 35.49 / 4.69; Apple M2 252.55 vs 68.75 / 57.84 / 6.28; Xeon Platinum 8260 (VM) 219.57 vs 155.19 / 79.18 / 6.24; Xeon E5-2698 v3 (contended) 178.90 vs 303.35 / 132.75 / 14.47. Peak-only is 1.86x, 3.36x, 1.77x, 1.27x, 4.37x, 2.77x and 1.35x faster than FFTW's inverse-only time (derived from page data); full output is slower than FFTW on the i5-13500H and the Haswell node. GPU (Radeon 8060S): rocFFT inverse-only 2.58 ms vs full 1.49, peak-only 0.71, hierarchical 0.20 ms; M2 GPU: MLX FFT-only 11.73 vs peak-only 3.92 ms. |
| **Workload** | Batched matched filtering (frequency-domain product, inverse FFT and peak scan) of 16 data spectra x 512 templates x 4096-point complex64 transforms, one CPU thread, timed against FFTW doing only the inverse FFT of the same batch. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 5950X; Ryzen AI Max+ 395 (Radeon 8060S); Ryzen 5 5500U; Intel Core i5-13500H; Apple M2; Xeon Platinum 8260 (VM); Xeon E5-2698 v3 (shared, contended node) |
| **Compiler and flags** | matchedfilter: setup.py builds with -O3 -fno-math-errno -std=c++17 (plus -msse4.2 -maes -mpclmul on x86) and Highway runtime dispatch (AVX2/AVX3 on the x86 hosts, NEON_BF16 on M2); compiler not recorded. FFTW baseline: pyFFTW-bundled FFTW 3.3.5 'sse2-avx' build (gcc -O2 with Fedora RPM hardening flags) on the x86 hosts, FFTW 3.3.10-neon through FFTW's C API on the M2; FFTW_PATIENT, 15 s planning limit, one thread. |
| **Adoption** | 1 star |
| **Last commit** | 2026-09-30 |
| **Links** | [repository](https://github.com/ahnitz/matchedfilter) · [benchmark](https://github.com/ahnitz/matchedfilter/blob/main/docs/measurements/teaser-fleet-20260928.md) |

## Verdict

First-party seven-machine run at revision eecb43c (2026-09-28): 16 data x 512 templates x 4096-point complex64 per call, one pinned thread, against a single batched FFTW_PATIENT backward plan (pyFFTW-bundled FFTW 3.3.5 sse2-avx built with gcc -O2 on x86, FFTW 3.3.10 NEON via the C API on M2). Peak-only took 34.27 vs 63.63 ms on a Ryzen 9 5950X and 20.68 vs 69.54 ms on a Ryzen AI Max+ 395 (1.86x and 3.36x), but the two sides do different work: FFTW does only the inverse FFT and writes every output, while matchedfilter adds the product and peak scan but never writes the correlation; the x86 FFTW build also lacks AVX2/FMA codelets.

## Use it when

- Template-bank searches (gravitational-wave style, radar/sonar, pulse detection) where many data segments are correlated against many templates and only the loudest lag per window is needed
- Power-of-two segment lengths from 64 to 1,048,576 (peak-only CPU) in complex64, where the 1.3x-3.4x gain of peak-only over FFTW's bare inverse FFT on the measured x86 hosts matters
- Searches where most pairs are noise and a calibrated false-dismissal budget is acceptable: hierarchical mode ran 3.95 ms vs 34.27 ms for flat peaks on a Ryzen 9 5950X at SNR 5.5, fd=1e-2
- Python pipelines that want the same API on CPU, Vulkan GPUs (Linux/Windows) and Metal (macOS)

## Skip it when

- General FFT work: there is no standalone transform API, only fused correlation of pre-transformed spectra
- When you need every lag on CPU: full-output mode was slower than FFTW's inverse-only time on the Core i5-13500H (56.24 vs 44.96 ms) and the Haswell node
- Float64 or non-power-of-two lengths: complex64 only, power-of-two sizes only
- Multithreaded single filters: CPU filtering uses one thread and parallelism is left to the caller
- Production use that needs a stable API or reviewed code: alpha (0.1.0a5 on PyPI, 0.1.0a6 in the tree), 1 star, single author; the 0.1.0a6 changelog fixes a stage-B intermediate indexing bug and an earlier fleet benchmark note says correctness for that revision was not yet established

## How it is fast

Each pair's inverse FFT uses a balanced (four-step style) split N = N1\*N2 with both factors near sqrt(N) and multiples of the SIMD width, so SIMD lanes run independent small transforms with broadcast twiddles and no in-register shuffles; the one corner turn is fused into stage A's store through a WxW register transpose. The data\*conj(template) product is fused into stage A's loads (both banks are rearranged once at ingest into the layout stage A walks), and in peak-only mode the binned maximum is computed in registers inside stage B, so the correlation is never written to memory. Google Highway compiles the kernel once per SIMD target (AVX2, AVX-512, NEON) with runtime dispatch; the hierarchical mode correlates only a low-frequency band on a coarse lag grid and runs the full filter only for pairs above a calibrated coarse threshold.

## Compared with alternatives

Pick it over FFTW, PocketFFT or VkFFT when the workload is many-data x many-template correlation and you only need peaks, since the gain comes from fusing the product and never writing the correlation; FlashFFTConv is the analogous fused-FFT-convolution choice for PyTorch/H100 sequence models, not for detection searches.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | NumPy (&gt;=1.20); Google Highway (vendored git submodule, or HIGHWAY_ROOT); optional pyFFTW / mkl-fft for reference timings; GPU path needs a Vulkan or Metal driver (SPIR-V and Metal kernels ship in the wheel) |
| **Minimum toolchain** | Python 3.10+, setuptools 77+, a C++17 compiler (manylinux_2_28 toolchain needed for Highway's AVX-512 targets); no Makefile or CMake, pip install is the only build |
| **Platforms** | Wheels for Linux x86-64 and macOS arm64; Linux arm64 builds from source and runs in CI; x86 baseline SSE4.2 with runtime dispatch to AVX2/AVX3; SVE and RVV targets disabled; macOS x86-64 untested |
| **Thread safety** | Not documented as thread-safe per plan. The extension releases the GIL, but pyproject.toml says plan state has not been audited for concurrent use (free-threaded builds deliberately not shipped); use one filter object per thread. |
| **Drop-in for the baseline** | partial — replaces a pipeline of FFTW inverse transform plus product plus peak search for correlation workloads, but has a different API, takes spectra rather than time series (except run_series), and is not an FFTW substitute |

## Gotchas

- Correlation is circular and the inverse is unnormalised (a perfect match returns n \* energy); zero-pad for linear correlation and check the threshold's normalisation.
- Results reuse internal storage; copy them before the next call. Series execution consumes the data slots, so a later run() needs set_data() again.
- Hierarchical mode can drop detections by design, refuses to run without a covering calibration file (or an explicit band plus threshold with no guarantee), and can be slower than flat filtering when many pairs survive (Iris Xe: 23.01 ms vs 9.75 ms flat).
- CPU and GPU results can differ slightly and near-equal maxima can select different lags; full output for large banks is huge (2^22 x 128 x 512 is 2 TiB) and automatic allocation is capped at 512 MiB.

## Known shortcomings

- Unequal work: FFTW times the inverse FFT only while matchedfilter fuses product + IFFT + peak scan, so it is not a drop-in FFT (closer to correlation than FFT). Weak FFTW baseline: x86 uses pyFFTW's FFTW 3.3.5 SSE2/AVX build (no AVX2/FMA); M2 FFTW at 252 ms vs 45-87 ms on x86 suggests the 4.37x M2 ratio is inflated. Full-output mode is slower than FFTW on i5-13500H and Haswell. Compiler not recorded.
- The x86 FFTW baseline is FFTW 3.3.5 sse2-avx built with gcc -O2. Its CHANGELOG fixes a stage-B intermediate indexing bug, and an older benchmark note says correctness for that revision was not yet established. Alpha, 1 star.

## Caveats and trade-offs

First-party numbers from a young alpha repo (PyPI 0.1.0a5, 1 star). The page itself says the comparison is unequal work: FFTW and the rocFFT/MLX references time only the inverse transform, while matchedfilter also does the spectral product and peak scan and peak-only mode skips writing the output, so the gain comes from fusion and output reduction, not a faster FFT kernel; it is not a drop-in FFT. Full-output mode is slower than FFTW on the Core i5-13500H and on the Haswell node. The x86 FFTW baseline is the pyFFTW-bundled FFTW 3.3.5 built for SSE2/AVX only (no AVX2/FMA codelets), while matchedfilter dispatches to AVX2/AVX3. The M2 FFTW baseline (252.55 ms) is 3-6x slower than the x86 hosts' FFTW (44.96-87.45 ms), so the 4.37x M2 ratio likely reflects a weak arm64 FFTW build (derived from page data). The page flags the Haswell node as contended (full and hierarchical rows indicative only) and the Xeon 8260 VM as least stable. Hierarchical mode trades a false-dismissal budget for speed and these timings do not measure FDR. Compiler for matchedfilter not recorded; build flags taken from current setup.py, which may differ from revision eecb43c. Interactive pages at ahnitz.github.io were not opened (egress-blocked); repo was renamed from peak-fft and its docs mention agent handoffs, so treat claims as unreviewed.

Not a general-purpose FFT. It fuses the spectral product, inverse FFT and peak search for matched-filter searches. Peak-only sizes are powers of two from 64 to 1,048,576 on CPU; full-output sizes are powers of two from 1,024 to 4,194,304. Single precision (complex64) only, one CPU thread per filter. The main interface is a pip-installable Python package over a C core, so use from C++ means linking the C code directly. Hierarchical mode needs calibration files and trades a false-dismissal budget for speed. The README calls it alpha software with an unstable API.

## Maintenance

Very active (last commit 2026-09-30, 638 commits) but alpha with an unstable API and a single maintainer; MIT-licensed, installable from PyPI, and usable from C/C++ only by building the C sources and Highway yourself.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** teaser-fleet-20260928.md and its JSON give single-thread FFTW (FFTW_PATIENT) inverse-only times next to matchedfilter full, peak-only and hierarchical times on seven named CPUs; all record numbers match. The harness (tools/teaser_fleet.py, tools/teaser_figure.py) and build flags (setup.py: -O3 -fno-math-errno -std=c++17) are public, but the compiler used for matchedfilter is not recorded and the two sides do unequal work (fused product + inverse FFT + peak scan vs a bare inverse FFT), so it stays first-party tier C.
- **Verifier notes:** Numbers verified on the md page and in the recorded JSON (FFTW version, build and compiler per host are recorded there, contrary to the original caveat). MIT license, not a fork, last commit 2026-09-30 confirmed. Category fft is the closest wave-8 fit, but it is a fused matched filter / batched correlation, not a general FFT library.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier; enrichment
- **Pages the verifier opened:**
  - <https://github.com/ahnitz/matchedfilter>
  - <https://github.com/ahnitz/matchedfilter/commits/main>
  - <https://raw.githubusercontent.com/ahnitz/matchedfilter/main/docs/measurements/teaser-fleet-20260928.md>
  - <https://raw.githubusercontent.com/ahnitz/matchedfilter/main/docs/measurements/teaser-fleet-20260928.json>
  - <https://raw.githubusercontent.com/ahnitz/matchedfilter/main/README.md>
  - <https://raw.githubusercontent.com/ahnitz/matchedfilter/main/LICENSE>
  - <https://raw.githubusercontent.com/ahnitz/matchedfilter/main/tools/teaser_fleet.py>
  - <https://raw.githubusercontent.com/ahnitz/matchedfilter/main/tools/teaser_figure.py>
  - <https://raw.githubusercontent.com/ahnitz/matchedfilter/main/setup.py>
  - <https://pypi.org/pypi/matchedfilter/json>
- **Sources the enricher read:**
  - <https://github.com/ahnitz/matchedfilter>
  - <https://github.com/ahnitz/matchedfilter/tree/main/src>
  - <https://raw.githubusercontent.com/ahnitz/matchedfilter/main/README.md>
  - <https://raw.githubusercontent.com/ahnitz/matchedfilter/main/LICENSE>
  - <https://raw.githubusercontent.com/ahnitz/matchedfilter/main/setup.py>
  - <https://raw.githubusercontent.com/ahnitz/matchedfilter/main/pyproject.toml>
  - <https://raw.githubusercontent.com/ahnitz/matchedfilter/main/CHANGELOG.md>
  - <https://raw.githubusercontent.com/ahnitz/matchedfilter/main/docs/README.md>
  - <https://raw.githubusercontent.com/ahnitz/matchedfilter/main/docs/usage.md>
  - <https://raw.githubusercontent.com/ahnitz/matchedfilter/main/docs/python-support.md>
  - <https://raw.githubusercontent.com/ahnitz/matchedfilter/main/docs/measurements/teaser-fleet-20260928.md>
  - <https://raw.githubusercontent.com/ahnitz/matchedfilter/main/docs/measurements/teaser-fleet-20260928.json>
  - <https://raw.githubusercontent.com/ahnitz/matchedfilter/main/docs/measurements/m2-teaser-headroom.md>
  - <https://raw.githubusercontent.com/ahnitz/matchedfilter/main/python/matchedfilter/matchedfilter.h>
  - <https://raw.githubusercontent.com/ahnitz/matchedfilter/main/src/balanced-inl.h>
  - <https://raw.githubusercontent.com/ahnitz/matchedfilter/main/src/kernel.cc>
  - <https://raw.githubusercontent.com/ahnitz/matchedfilter/main/src/matchfilt.c>
  - <https://raw.githubusercontent.com/ahnitz/matchedfilter/main/src/internal.h>
  - <https://raw.githubusercontent.com/ahnitz/matchedfilter/main/src/transform.h>
  - <https://raw.githubusercontent.com/ahnitz/matchedfilter/main/tools/teaser_fleet.py>
  - <https://raw.githubusercontent.com/ahnitz/matchedfilter/main/tools/teaser_figure.py>
  - <https://pypi.org/pypi/matchedfilter/json>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/ahnitz/matchedfilter`) · [data/wave8/enrich/raw/github_com_ahnitz_matchedfilter.json](../../../data/wave8/enrich/raw/github_com_ahnitz_matchedfilter.json) (enrichment confidence 0.8)

</details>
