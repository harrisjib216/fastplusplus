# OTFFT (OK Ojisan's Template FFT)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [FFT](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `MIT` · 🔴 abandoned

> MIT double-precision Stockham FFT library for x86 (SSE2/AVX/AVX2) whose upstream author claims it beats FFTW at 2^1 to 2^24.

| | |
|---|---|
| **Beats** | FFTW |
| **Claimed result** | Project homepage title 'OTFFT -- FFT library using AVX that is faster than FFTW'; no numbers were available on any page opened here (the akinomyoga/OTFFT README only says the bundled fftbench programs need FFTW3 and Ooura's fftsg.c). |
| **Workload** | Stockham/mixed-radix complex FFT with AVX; project homepage compares against FFTW (and Ooura FFT) for lengths 2^1 to 2^24 (homepage not reachable from the research environment). |
| **Metric** | throughput |
| **Adoption** | 29 stars (DEWETRON fork); akinomyoga/OTFFT OTFFT-6.5m fork 13 stars; included in kfrlib/fft-benchmark and used as the model for ZL-Audio/zldsp_fft |
| **Last commit** | 2022-08-17 |
| **Links** | [repository](https://github.com/DEWETRON/otfft) |

## Verdict

Nothing measured was opened. The upstream homepage (egress-blocked here; seen only through a search snippet) reports OTFFT 11.6 faster than multi-threaded FFTW 3.3.10 at every power of two from 2^1 to 2^24 on a Surface Laptop 5 (10 cores/12 threads, WSL2 Ubuntu 22.04, GCC 11.4.0). The snippet gives two ratios, 81% of FFTW's time at 2^10 and 89% at 2^11. The upstream benchmark sources (fftbench with an FFTW3 wrapper) exist, but their FFTW planner flags were not seen.

## Use it when

- Double-precision 1-D complex or real FFTs on x86-64 desktops and servers where an MIT license matters and FFTW's GPL does not fit
- Power-of-two lengths from 2 to 2^24, the range the upstream benchmark covers
- Windows (MSVC) or Linux (GCC/Clang) products that need one binary for SSE2, AVX and AVX2 machines: the fork builds all three back-ends and picks one at run time with CPUID
- Applications that also need DCT-II or arbitrary-length (Bluestein) transforms from the same small library

## Skip it when

- When you need a verified win over FFTW: no repository has numbers, and the only comparison is the upstream homepage (search snippet, not opened: OTFFT 11.6 vs FFTW 3.3.10 multi-threaded on a Surface Laptop 5 under WSL2, GCC 11.4.0, OTFFT taking 81% of FFTW's time at 2^10 and 89% at 2^11; FFTW planner flags unknown). This fork is at 11.5, not 11.6
- Single precision, 2-D/3-D transforms, batched/strided (guru-style) plans, or wisdom: none exist
- ARM, Apple Silicon or other non-x86 targets: kernels are SSE2/AVX intrinsics and dispatch uses x86 cpuid/xgetbv inline assembly; kfrlib/fft-benchmark lists it as x86 only
- AVX-512 machines expecting 512-bit kernels: the build only compiles SSE2, AVX and AVX2 back-ends
- Projects that need upkeep: the fork's last commit is 2022-08-17, and the kernel-selection table was tuned on the upstream author's machine with no ffttune tool in the fork to retune it

## How it is fast

It uses the self-sorting Stockham algorithm (no bit-reversal pass) in radix-4, -8 and -16 decimation-in-frequency and decimation-in-time variants, written as C++ templates over SSE2 (__m128d) and AVX/AVX2 (__m256d) complex arithmetic. Large power-of-two sizes use a six-step/eight-step (cache-blocked, transpose-based) algorithm, and other lengths use a mixed-radix kernel. A hard-coded table, copied from upstream's ffttune-generated setup, picks one of these seven kernels for each power of two up to 2^24. Above 2^15 points it runs OpenMP loops automatically unless built with DO_SINGLE_THREAD.

## Compared with alternatives

Choose OTFFT over PocketFFT or PFFFT only if you want x86 double-precision 1-D transforms with run-time AVX2/AVX/SSE2 dispatch under MIT and accept an unmaintained codebase; PocketFFT (N-D, any length, any arch) and KFR or VectorFFT (published wins over FFTW/MKL) are the better-documented choices.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | OpenMP (find_package(OpenMP REQUIRED) in the standalone build); Boost.Test only for the unit tests |
| **Minimum toolchain** | C++11; CMake 3.0+; GCC, Clang, Intel C++ or MSVC (CI badges: Ubuntu 14.04 and 20.04, VS2013; a 2018 commit fixed the VS2017 build) |
| **Platforms** | x86 only; x86-64 gets SSE2, AVX and AVX2 back-ends chosen at run time by CPUID, 32-bit x86 builds only the SSE2 back-end |
| **Thread safety** | Not formally documented. The README says to use FFT0/DCT0 with a caller-supplied work buffer in multi-threaded code and to create one Bluestein object per thread, so do not share one transform object across threads. The library itself spawns OpenMP threads for N &gt;= 2^15. |
| **Drop-in for the baseline** | no |

## Gotchas

- fwd() divides by N (forward normalization), unlike FFTW's unnormalized forward transform; use fwd0() for FFTW-style scaling. inv() is unnormalized, and the real inverse transforms destroy their input
- The factory comment says complex, real and DCT lengths must be even (up to 2^30); only the Bluestein transform takes any length (up to 2^28). Non-power-of-two and above-2^24 lengths fall through to the mixed-radix kernel
- Internal OpenMP parallelism above 2^15 points can oversubscribe cores when the caller already runs FFTs on several threads; define DO_SINGLE_THREAD to turn it off
- The README examples (OTFFT::FFT fft(N), OTFFT::FFT0) do not match the public header, which only exports the Factory functions. The CPUID probe also runs xgetbv before checking the OSXSAVE bit, so it can fault with an invalid-instruction error on CPUs or VMs without XSAVE

## Known shortcomings

- Tier D: upstream homepage (wwwa.pikara.ne.jp) unreachable here; a search snippet says faster than FFTW for 2^1-2^24 (Surface Laptop 5, GCC 11.4.0, FFTW 3.3.10); needs a retier from a host that can reach it; abandoned (2022-08-17).
- Fork is at OTFFT 11.5; upstream homepage blocked here. Search snippet: OTFFT 11.6 vs multi-threaded FFTW 3.3.10 on a Surface Laptop 5, GCC 11.4.0, 81% of FFTW's time at 2^10 and 89% at 2^11. fwd() scales by 1/N, unlike FFTW. CPUID probe runs xgetbv before checking OSXSAVE, so it can crash on CPUs/VMs without XSAVE. Abandoned since 2022.

## Caveats and trade-offs

No numeric evidence was opened, so this is tier D. A WebSearch snippet (not opened) says the upstream homepage wwwa.pikara.ne.jp/okojisan/otfft-en/ claims OTFFT is faster than FFTW at lengths 2^1 to 2^24, measured on a Surface Laptop 5 with GCC 11.4.0, OTFFT 11.6 and FFTW 3.3.10; a verifier that can open that page should re-tier. Upstream benchmark code exists (fftbench\*.cpp with cpp_fftw3.h, mirrored in temerkhanov/OTFFT) but results are only on the homepage. The DEWETRON repo is a source-level fork of OK Ojisan's (Takuya Okahisa) upstream, synced to version 11.5, not a GitHub fork; last commit 2022-08-17. kfrlib/fft-benchmark lists it as double precision only and x86 only; upstream builds target the compiling machine's ISA (an AVX build crashes on CPUs without AVX, per the akinomyoga/OTFFT README).

C++ template metaprogramming makes builds slow; compile-time AVX selection; OpenMP six-step variant; DEWETRON fork adds CMake, multi-ISA builds (AVX2, AVX, SSE2) and unit tests; complex, real, DCT-II and Bluestein, sizes up to 2^24-2^25.

## Maintenance

Abandoned: the fork has 38 commits, the last a 2022-08-17 upstream sync to 11.5, and no open issues. It is MIT-licensed and small enough to vendor as a CMake static library, with unit tests and a GitHub Actions build.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification D, tier now D.
- **Tier reason:** No opened page has OTFFT timings: the DEWETRON README, the kfrlib/fft-benchmark README (OTFFT 11.5.0 is a supported library but no results are published in the repo) and the temerkhanov/OTFFT mirror (ships fftbench0-3.cpp and cpp_fftw3.h, no results) all lack numbers; the upstream homepage is egress-blocked.
- **Verifier notes:** Kept at D rather than rejected as not-notable (29 stars) because it is one of the libraries kfrlib/fft-benchmark selected for popularity and the upstream homepage reportedly holds a methodology-stated FFTW comparison; worth a retier check from a host that can reach wwwa.pikara.ne.jp. Metadata confirmed: MIT, 29 stars, not a GitHub fork, last commit 2022-08-17 (abandoned).
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://github.com/DEWETRON/otfft>
  - <https://github.com/DEWETRON/otfft/commits>
  - <https://raw.githubusercontent.com/DEWETRON/otfft/HEAD/README.md>
  - <https://github.com/kfrlib/fft-benchmark>
  - <https://raw.githubusercontent.com/kfrlib/fft-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/akinomyoga/OTFFT/HEAD/README.md>
  - <https://github.com/temerkhanov/OTFFT>
- **Sources the enricher read:**
  - <https://github.com/DEWETRON/otfft>
  - <https://github.com/DEWETRON/otfft/commits>
  - <https://github.com/DEWETRON/otfft/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/DEWETRON/otfft/HEAD/README.md>
  - <https://raw.githubusercontent.com/DEWETRON/otfft/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/DEWETRON/otfft/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/DEWETRON/otfft/HEAD/inc/otfft.h>
  - <https://raw.githubusercontent.com/DEWETRON/otfft/HEAD/inc/otfft_types.h>
  - <https://raw.githubusercontent.com/DEWETRON/otfft/HEAD/inc/otfft_fwd.h>
  - <https://raw.githubusercontent.com/DEWETRON/otfft/HEAD/src/otfft.cpp>
  - <https://raw.githubusercontent.com/DEWETRON/otfft/HEAD/src/otfft_algo.cpp>
  - <https://raw.githubusercontent.com/DEWETRON/otfft/HEAD/src/otfft_config.h.in>
  - <https://raw.githubusercontent.com/DEWETRON/otfft/HEAD/src/otfft_factory.h>
  - <https://raw.githubusercontent.com/DEWETRON/otfft/HEAD/src/otfft_mixedradix.h>
  - <https://raw.githubusercontent.com/DEWETRON/otfft/HEAD/src/otfft_sixstep.h>
  - <https://raw.githubusercontent.com/DEWETRON/otfft/HEAD/src/otfft_misc.h>
  - <https://raw.githubusercontent.com/DEWETRON/otfft/HEAD/unit_tests/CMakeLists.txt>
  - <https://raw.githubusercontent.com/akinomyoga/OTFFT/HEAD/README.md>
  - <https://raw.githubusercontent.com/kfrlib/fft-benchmark/HEAD/README.md>
  - http://wwwa.pikara.ne.jp/okojisan/otfft-en/ (EGRESS_BLOCKED; content known only from a WebSearch snippet)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/dewetron/otfft`) · [data/wave8/enrich/raw/github_com_dewetron_otfft.json](../../../data/wave8/enrich/raw/github_com_dewetron_otfft.json) (enrichment confidence 0.6)

</details>
