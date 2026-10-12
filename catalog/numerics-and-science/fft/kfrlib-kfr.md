# KFR

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [FFT](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `GPL-2.0-or-later (dual commercial license)` · 🟢 active

> C++20 SIMD DSP framework whose any-length FFT tracks or beats FFTW in vendor and LIGO/KAGRA benchmarks; GPL or paid license.

| | |
|---|---|
| **Beats** | FFTW |
| **Claimed result** | Graphs only. Independent LVK paper (arXiv 2503.14292 Fig. 6): KFR 6.0.2 shows higher MFlops than FFTW 3.3.10 for complex forward in-place FFTs across sizes (no numeric values in text). First-party README graph (powers of 2, 16..16M, double): KFR 3.0.5-rc \~1.3-3x FFTW 3.3.8 FFTW_ESTIMATE MFlops (derived from page data, read from graph); similar to Intel IPP. |
| **Workload** | FFT of power-of-2, prime, composite and random sizes against FFTW, Intel MKL, Intel IPP (graphs in README; harness in kfrlib/fft-benchmark) |
| **Metric** | throughput |
| **Hardware** | Not stated (LVK paper says only 'Intel AMD64') |
| **Compiler and flags** | README graph: clang 7.0.1 on Windows, AVX2; LVK paper: Clang (flags not stated) |
| **Adoption** | 1.9k stars; release 7.0.1 Nov 2025 |
| **Last commit** | 2026-09-14 |
| **Links** | [repository](https://github.com/kfrlib/kfr) · [benchmark](https://arxiv.org/html/2503.14292) |

## Verdict

The independent evidence is an LVK (LIGO/Virgo/KAGRA) proceedings paper (arXiv 2503.14292, Fig. 6): complex forward in-place FFTs on a local Osaka cluster show KFR 6.0.2 with higher MFlops than FFTW 3.3.10 (Clang), shown only as graphs, with no CPU model or planner flags and using a harness first written by KFR's author. KFR's own README graphs (KFR 3.0.5-rc, clang 7.0.1, AVX2, Windows) show roughly 1.3-3x FFTW 3.3.8 on powers of two, but its kfrlib/fft-benchmark harness plans FFTW with FFTW_ESTIMATE, which understates FFTW.

## Use it when

- Repeated fixed-size 1D FFTs (power-of-two or arbitrary, including primes) in float or double where FFTW's GPL is acceptable but its planning time or wisdom management is not
- Audio and real-time DSP pipelines that also need FIR/IIR filters, FFT convolution, sample-rate conversion and audio file I/O from one library
- Cross-platform builds (x86 SSE2-AVX-512, ARM/AArch64 NEON, RISC-V RVV, WebAssembly, iOS/Android) that want one FFT code base with runtime CPU dispatch on x86
- Real-time callbacks with a fixed power-of-two size: ngfft has no allocation and no scratch at execution time
- Projects that can pay for KFR's commercial license and want an FFT outside FFTW's licensing

## Skip it when

- Closed-source or permissively licensed products that will not buy a commercial license: KFR is GPLv2+ otherwise
- MSVC-only toolchains: the DFT module is off by default with MSVC, the docs warn of lower DFT performance, and a Release-mode MSVC build produced a wrong 2^19 real FFT (issue #272, labeled compiler bug)
- Multithreaded single large transforms: no internal threading is documented, and its own benchmark harness disables multithreading
- Strided, transposed or non-contiguous multidimensional data: MD plans require contiguous row-major tensors, and real MD transforms require an even last axis
- When you need proof that it beats a tuned FFTW (FFTW_MEASURE/PATIENT) on your CPU: the published comparisons use FFTW_ESTIMATE or do not state planner flags

## How it is fast

Transforms run on KFR's own vec&lt;T,N&gt; SIMD layer (SSE2 to AVX-512, NEON, RVV) rather than relying on auto-vectorization, with multiarchitecture builds dispatching to the best kernel at runtime on x86. Power-of-two sizes use a four-step (DIF half plus DIT half, the 'sandwich') decomposition whose split is chosen from hard-coded per-architecture tables that switch layout once the data exceeds 32 KiB (AVX) or 128 KiB (Apple NEON). Other sizes use mixed-radix stages with fixed SIMD butterflies for radices 2-10 plus a generic butterfly, and Bluestein's algorithm where needed. There is no runtime measurement or wisdom phase, so plan creation is deterministic.

## Compared with alternatives

Pick KFR over PocketFFT, PFFFT or muFFT when you want SIMD speed on arbitrary 1D lengths plus a full DSP toolkit and can accept GPL or a paid license; over FFTS because FFTS is unmaintained. Pick VectorFFT only for x86 double c2c work that wants an MIT license and an MKL-beating claim, and VkFFT for GPUs.

## Integration

| | |
|---|---|
| **Form** | static lib (DFT, DSP, IO and audio modules are compiled libraries via CMake; the SIMD/expression core is header-only); optional C API library |
| **Dependencies** | none beyond a C++20 standard library; CMake 3.16+ to build |
| **Minimum toolchain** | C++20; Clang 16+, GCC 11+, MSVC 2022 (19.30+), Xcode 13+; Clang recommended for best performance |
| **Platforms** | Windows, Linux, macOS, iOS, Android, WebAssembly; x86/x86-64 (SSE2-AVX-512), ARM/AArch64 (NEON), RISC-V 64 with RVV (VLEN &gt;= 128, Linux, Clang); runtime dispatch only on x86 |
| **Thread safety** | An initialized dft_plan or ngfft plan is read-only during execute and can be shared across threads if each call has its own data and scratch buffer; the dft_cache used by dft()/realdft() is mutex-protected |
| **Drop-in for the baseline** | no |

## Gotchas

- No transform is normalized: forward then inverse returns N times the input (2/N for the DCT pair)
- Real-spectrum layout depends on dft_pack_format (CCs default vs Perm); ngfft real transforms always use Perm, and irealdft infers an even length from the buffer size
- Building the DFT module is memory-heavy (vcpkg CI out-of-memory in issue #261); KFR_CLASSIC_FFT restores the pre-7.1 FFT path
- ngfft twiddle buffers must be cache-line aligned and outlive the plan; ngfft_twiddle_count returns SIZE_MAX for sizes unsupported on the active architecture

## Known shortcomings

- README graph is old (KFR 3.0.5-rc) and measures FFTW in FFTW_ESTIMATE mode, overstating the gap; independent LIGO/Virgo/KAGRA paper (arXiv 2503.14292) gives a graph only, no CPU model.
- Vendor harness (kfrlib/fft-benchmark, libs/fftw/fftw.cpp at HEAD) still plans FFTW with FFTW_ESTIMATE, so its graphs overstate the gap to FFTW.
- The LVK paper's benchmark harness was first written by KFR's author, so the tier-B measurement is not fully independent.
- Issue #272: KFR 7.0.1 built with MSVC Release gave a ghost peak on a 2^19 r2c FFT (closed, labelled compiler bug); building the DFT module ran out of memory in vcpkg CI (#261).

## Caveats and trade-offs

README graphs are old (KFR 3.0.5-rc) and compare against FFTW with FFTW_ESTIMATE, a weak planning mode, so they overstate the gap vs FFTW_MEASURE/PATIENT. LVK paper is graph-only with no CPU model. kfrlib/fft-benchmark harness is public but publishes no numbers. GPL or paid commercial license.

Dual license: GPL or paid commercial; best performance needs Clang; SSE2-AVX512, NEON, RVV; broader DSP framework.

## Maintenance

Actively maintained (KFR 7.1.0 released 2026-08-18, about 1.9k stars, 18 open issues); usable as GPLv2+ code or under a paid commercial license, with prebuilt release packages and CMake integration.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now B.
- **Tier reason:** Upgraded: README links an independent LIGO/Virgo/KAGRA proceedings paper (arXiv 2503.14292, Fig. 6, KFR 6.0.2 vs FFTW 3.3.10, Clang, MFlops; code at git.ligo.org/kagra/software/fft-benchmark) reporting KFR faster than FFTW, but graph only and no CPU model, so not A. First-party README graphs are C.
- **Verifier notes:** Tier upgraded C -&gt; B via independent LVK proceedings; flag the FFTW_ESTIMATE baseline in the first-party graph as a shortcoming.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `license`, `last_commit`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/kfrlib/kfr>
  - <https://raw.githubusercontent.com/kfrlib/kfr/HEAD/README.md>
  - <https://raw.githubusercontent.com/kfrlib/kfr/HEAD/img/powers2_double_16_16777216.png>
  - <https://github.com/kfrlib/kfr/commits>
  - <https://raw.githubusercontent.com/kfrlib/fft-benchmark/HEAD/README.md>
  - <https://arxiv.org/abs/2503.14292>
  - <https://arxiv.org/html/2503.14292>
- **Sources the enricher read:**
  - <https://github.com/kfrlib/kfr>
  - <https://raw.githubusercontent.com/kfrlib/kfr/HEAD/README.md>
  - <https://raw.githubusercontent.com/kfrlib/kfr/HEAD/docs/docs/dft/dft.md>
  - <https://raw.githubusercontent.com/kfrlib/kfr/HEAD/docs/docs/dft/ngfft.md>
  - <https://raw.githubusercontent.com/kfrlib/kfr/HEAD/docs/docs/dft/dft_introduction.md>
  - <https://raw.githubusercontent.com/kfrlib/kfr/HEAD/docs/docs/getting-started/whatsnew7.md>
  - <https://raw.githubusercontent.com/kfrlib/kfr/HEAD/docs/docs/getting-started/installation.md>
  - <https://raw.githubusercontent.com/kfrlib/kfr/HEAD/docs/docs/getting-started/clang.md>
  - <https://raw.githubusercontent.com/kfrlib/kfr/HEAD/CMakeLists.txt>
  - <https://github.com/kfrlib/kfr/tree/main/src/dft>
  - <https://raw.githubusercontent.com/kfrlib/kfr/HEAD/src/dft/ngfft-impl.hpp>
  - <https://raw.githubusercontent.com/kfrlib/kfr/HEAD/src/dft/dft-impl.hpp>
  - <https://raw.githubusercontent.com/kfrlib/kfr/HEAD/src/dft/sandwich.hpp>
  - <https://github.com/kfrlib/kfr/releases>
  - <https://github.com/kfrlib/kfr/issues?q=is%3Aissue+dft+OR+fft>
  - <https://github.com/kfrlib/kfr/issues/272>
  - <https://github.com/kfrlib/kfr/issues/261>
  - <https://github.com/kfrlib/fft-benchmark>
  - <https://raw.githubusercontent.com/kfrlib/fft-benchmark/HEAD/README.md>
  - <https://github.com/kfrlib/fft-benchmark/tree/master/src>
  - <https://raw.githubusercontent.com/kfrlib/fft-benchmark/HEAD/src/fft_benchmark.cpp>
  - <https://github.com/kfrlib/fft-benchmark/tree/master/libs>
  - <https://github.com/kfrlib/fft-benchmark/tree/master/libs/fftw>
  - <https://raw.githubusercontent.com/kfrlib/fft-benchmark/HEAD/libs/fftw/fftw.cpp>
  - <https://raw.githubusercontent.com/kfrlib/fft-benchmark/HEAD/libs/kfr/kfr.cpp>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/kfrlib/kfr`) · [data/wave8/enrich/raw/github_com_kfrlib_kfr.json](../../../data/wave8/enrich/raw/github_com_kfrlib_kfr.json) (enrichment confidence 0.8)

</details>
