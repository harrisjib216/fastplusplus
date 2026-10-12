# SFFT library (ETH Zurich optimized sparse FFT, versions 1-3)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [FFT](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `GPL-2.0-or-later` · 🔴 abandoned

> ETH Zurich's SSE-optimized C++ build of MIT's sparse FFT (sFFT v1-v3) for k-sparse spectra; no published win over FFTW.

| | |
|---|---|
| **Beats** | FFTW |
| **Claimed result** | No numbers anywhere in the repository or its docs. The docs call it a 'high-performance C++ implementation' of sFFT v1, v2 and v3 with SSE kernels. The underlying MIT sFFT algorithm is billed as faster than FFTW for sparse spectra (Hacker News thread 'The faster-than-fast Fourier transform'), but those figures were not opened this session. |
| **Workload** | Discrete Fourier transform of a signal whose spectrum has only k non-zero frequencies out of n (sparse spectrum), compared in the underlying sFFT work against a full dense FFT such as FFTW; this repository itself contains no benchmark. |
| **Metric** | throughput |
| **Adoption** | 69 stars, 19 forks |
| **Last commit** | 2015-06-03 |
| **Links** | [repository](https://github.com/davidediger/sfft) |

## Verdict

No benchmark exists in the repository: README.txt, CHANGELOG.txt and doc/\*.rst give no numbers, and the --develop tools (sfft-timing, sfft-timing_many, sfft-instruction_count) time or count only the SFFT call with no FFTW harness. Any faster-than-FFTW claim rests on the unopened Schumacher 2013 ETH thesis and Schumacher/Pueschel SiPS 2014 paper, whose search snippets reportedly show 2-5x over the MIT reference sFFT and roughly FFTW parity at large n.

## Use it when

- Exactly sparse, noise-free spectra (v3) where n is large (the tuned tables go up to 2^24 points) and k is tiny relative to n, for example k=50 at n=4,194,304.
- Many same-size sparse transforms that can share one plan and run in parallel through sfft_exec_many on x86 with OpenMP.
- Research or algorithm comparison where you need a tuned reference sFFT implementation rather than the original MIT code.
- Noisy signals only if your (n, k) is one of the 20 pairs the usage docs list for v1/v2 (n = 2^13..2^24 with k=50, or n=4,194,304 with k from 50 to 4,000).

## Skip it when

- Dense or moderately sparse spectra: it is not a general FFT, and the README says it is 'NOT intended to be used as a drop-in replacement for the FFT library of your choice'.
- Any setting that needs a demonstrated speedup: the repo has no FFTW comparison, and the only figures seen (search snippets of the thesis) suggest parity with FFTW at large n, not a clear win.
- Noisy signals with v3, or v1/v2 with an (n, k) outside the tuned table: parameters fall back to defaults and n is silently floored to a power of two.
- Non-x86 targets, Windows or MSVC: SSE intrinsics are mandatory, intrinsics.h errors out on compilers other than GCC/ICC, and the docs say it was tested only on Linux with GCC 4.4/4.7 and ICC 13+.
- Production or closed-source code: experimental, abandoned since 2015, open build-failure issues, and GPL-2.0-or-later.

## How it is fast

The sFFT algorithms (Hassanieh, Indyk, Katabi, Price) permute the spectrum pseudo-randomly, apply flat-window (Gaussian/Dolph-Chebyshev) filters to hash frequencies into B buckets, run small FFTW transforms on the buckets, and then locate and estimate the large coefficients by voting over several loops; v3 does this in O(k log n) for exactly sparse signals. Schumacher's 2013 ETH thesis added a plan/execute split, SSE2 intrinsics for the filter and permutation loops (about 140 _mm_ calls in the v3 source), batched in-place FFTW calls, an interleaved data layout, fixed loop counts in v3 and optional Intel IPP vector math.

## Compared with alternatives

Pick it over MPSFT only when you specifically need the classic MIT sFFT v1-v3 algorithms on power-of-two sizes; MPSFT publishes timings against FFTW (19.4 ms vs 225.3 ms at N about 2^22, S=64) and handles prime sizes. For anything dense, FFTW, PocketFFT or KFR remain the right choice; Auto-MPFT covers the partial-transform case.

## Integration

| | |
|---|---|
| **Form** | static lib + shared lib (libsfft.a / libsfft.so, waf build); optional Python ctypes wrapper |
| **Dependencies** | FFTW 3, OpenMP (libgomp), libm, librt, Intel IPP by default (--without-ipp disables it); the waf configure step also checks for valgrind even without --develop |
| **Minimum toolchain** | Documented for GCC 4.4/4.7 and Intel C++ 13+ (ICC 12 does not work); uses std::tr1::unordered_map and C99 'double complex' through &lt;complex.h&gt;, so modern C++11+ default modes may fail (open issue #3: 'complex_t has not been declared') |
| **Platforms** | x86/x86-64 with SSE2 (built with -march=native -ffast-math by default); Linux only tested |
| **Thread safety** | sfft_exec_many parallelizes with OpenMP over per-thread buffers made at plan time; the docs warn the program will crash if the OpenMP thread count differs between sfft_make_plan and sfft_exec_many. v1/v2 behavior is controlled by process-global flags (ALGORITHM1, WITH_COMB) set at plan time, so mixing v1 and v2 plans in one process is unsafe. |
| **Drop-in for the baseline** | no |

## Gotchas

- sfft_exec in this repo writes a dense length-n output array and zeroes all n entries on every call, an O(n) memory pass that undercuts the sublinear point of v3; the docs/usage.rst still describe an unordered_map output, so docs and header disagree.
- sfft_v1_make_plan sets the global WITH_COMB=false and sfft_v2_make_plan sets it true, but sfft_v1 execution does not reset it, so creating a v2 plan after a v1 plan changes how the v1 plan runs.
- Default build flags are -O3 -ffast-math -march=native, so binaries are not portable to older CPUs and IEEE semantics are relaxed.
- Inputs must come from sfft_malloc (16-byte aligned _mm_malloc) because the SSE kernels use aligned loads.

## Known shortcomings

- No numbers in the repo; sfft-timing times SFFT only (no FFTW harness). Thesis, spiral.net and ETH research-collection blocked here; a search snippet says 2-5x over the MIT reference code and roughly equal to FFTW for large n, so faster-than-FFTW is unproven. Docs call it experimental, not a drop-in replacement ('be prepared to find bugs'). Abandoned since 2015; mirror of the spiral.net 0.1.0 release.
- Build broken on modern compilers (open #3: 'complex_t has not been declared'; fft.h defines complex_t as C99 double complex and sfft.h uses tr1::unordered_map). sfft_exec zeroes all n output entries every call (O(n) cost); header and docs disagree on the output type. v1 and v2 plans share global WITH_COMB/ALGORITHM1 flags, so mixing them in one process is unsafe.

## Caveats and trade-offs

Tier D: no benchmark numbers in README.txt, CHANGELOG.txt or doc/\*.rst (all read via raw.githubusercontent.com). The bundled dev tools (sfft-timing, sfft-timing_many, sfft-instruction_count, sfft-verification; built with --develop) time only the SFFT call and include no FFTW comparison. Numbers presumably live in J. Schumacher's ETH master thesis 'High Performance Sparse Fast Fourier Transform' (2013, supervised by M. Pueschel; PDF at spiral.ece.cmu.edu/pub-spiral/pubfile/Final_Thesis_SFFT_169.pdf) and in Schumacher and Pueschel, 'High-performance sparse fast Fourier transforms', IEEE SiPS 2014; spiral.net, spiral.ece.cmu.edu, research-collection.ethz.ch and arXiv were all egress-blocked, so none was opened. WebSearch snippets only (not verified): the thesis abstract reports the optimized library as two to five times faster than the MIT reference SFFT implementation, and one summary says the optimized SFFT is 'about equally efficient as' FFTW for large input sizes, so a win over FFTW is not established and at best holds for large, very sparse signals. The project's own README and docs say the implementation 'is in an experimental state', is 'NOT intended to be used as a drop-in replacement for the FFT library of your choice', and 'Be prepared to find bugs'. It depends on FFTW 3 (used internally) and by default on Intel IPP (configure --without-ipp to disable); kernels are SSE for x86. The GitHub repo is an import of the spiral.net 0.1.0 release ('Official download of version 0.1.0', 2015-06-01) plus a ctypes Python wrapper, example app and API cleanups by the importer (12 commits, last 2015-06-03); it is not a GitHub fork, and the canonical upstream is spiral.net/software/sfft.html. Notability is modest by stars (69), but the sFFT algorithm (Hassanieh, Indyk, Katabi, Price) is widely cited. Related sparse-FFT repos mpsft and Auto-MPFT are already catalogued.

Only helps when the spectrum is sparse; it is not a general dense FFT. README states it is experimental and 'NOT intended to be used as a drop-in replacement for the FFT library of your choice'. Docs say v1 and v2 work only with a few specific input parameters and v3 cannot handle noisy signals. Targets x86 with SSE; Intel IPP is required by default (configure --without-ipp disables it). It calls FFTW internally for its sub-transforms (FFTW plan flags are a plan parameter), so FFTW is a dependency as well as the baseline. GPL-2.0-or-later (strong copyleft).

## Maintenance

Abandoned: a 2015 GitHub import (12 commits, last 2015-06-03) of the 2013 spiral.net 0.1.0 release plus a BSD-licensed Python ctypes wrapper; the library itself is GPL-2.0-or-later, and three issues about build errors, Windows and cross-compiling are open without replies.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification D, tier now D.
- **Tier reason:** benchmark_url is null and the repository has no numbers: README.txt, CHANGELOG.txt and all doc/\*.rst were read, and the developer tools they describe (sfft-timing, sfft-timing_many, sfft-instruction_count) time or count only the SFFT call, with no FFTW comparison harness. The thesis and SiPS 2014 paper that may hold numbers are on egress-blocked hosts, so D.
- **Verifier notes:** Kept at D rather than rejected: the sFFT algorithm is widely referenced and this is the ETH/SPIRAL optimized release, though only a GitHub mirror with 69 stars. Lead for a retier with paper access: Schumacher thesis PDF (spiral.ece.cmu.edu) and SiPS 2014 paper; a search snippet suggests parity with FFTW for large n rather than a clear win, so the faster-than-FFTW claim is unproven.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier; enrichment
- **Pages the verifier opened:**
  - <https://github.com/davidediger/sfft>
  - <https://github.com/davidediger/sfft/commits/master>
  - <https://github.com/davidediger/sfft/tree/master/doc>
  - <https://github.com/davidediger/sfft/tree/master/tools>
  - <https://raw.githubusercontent.com/davidediger/sfft/HEAD/README.txt>
  - <https://raw.githubusercontent.com/davidediger/sfft/HEAD/CHANGELOG.txt>
  - <https://raw.githubusercontent.com/davidediger/sfft/HEAD/COPYING.txt>
  - <https://raw.githubusercontent.com/davidediger/sfft/HEAD/COPYRIGHT.txt>
  - <https://raw.githubusercontent.com/davidediger/sfft/HEAD/AUTHORS.txt>
  - <https://raw.githubusercontent.com/davidediger/sfft/HEAD/doc/introduction.rst>
  - <https://raw.githubusercontent.com/davidediger/sfft/HEAD/doc/development.rst>
  - <https://raw.githubusercontent.com/davidediger/sfft/HEAD/doc/usage.rst>
  - <https://raw.githubusercontent.com/davidediger/sfft/HEAD/doc/installation.rst>
  - <https://raw.githubusercontent.com/davidediger/sfft/HEAD/doc/index.rst>
- **Sources the enricher read:**
  - <https://github.com/davidediger/sfft>
  - <https://github.com/davidediger/sfft/commits/master>
  - <https://github.com/davidediger/sfft/issues?q=is%3Aissue>
  - <https://github.com/davidediger/sfft/issues/3>
  - <https://github.com/davidediger/sfft/tree/master/python>
  - <https://raw.githubusercontent.com/davidediger/sfft/HEAD/README.txt>
  - <https://raw.githubusercontent.com/davidediger/sfft/HEAD/CHANGELOG.txt>
  - <https://raw.githubusercontent.com/davidediger/sfft/HEAD/COPYING.txt>
  - <https://raw.githubusercontent.com/davidediger/sfft/HEAD/AUTHORS.txt>
  - <https://raw.githubusercontent.com/davidediger/sfft/HEAD/doc/introduction.rst>
  - <https://raw.githubusercontent.com/davidediger/sfft/HEAD/doc/usage.rst>
  - <https://raw.githubusercontent.com/davidediger/sfft/HEAD/doc/installation.rst>
  - <https://raw.githubusercontent.com/davidediger/sfft/HEAD/doc/development.rst>
  - <https://raw.githubusercontent.com/davidediger/sfft/HEAD/doc/index.rst>
  - <https://raw.githubusercontent.com/davidediger/sfft/HEAD/src/sfft.h>
  - <https://raw.githubusercontent.com/davidediger/sfft/HEAD/src/sfft.cc>
  - <https://raw.githubusercontent.com/davidediger/sfft/HEAD/src/fftw.cc>
  - <https://raw.githubusercontent.com/davidediger/sfft/HEAD/src/fft.h>
  - <https://raw.githubusercontent.com/davidediger/sfft/HEAD/src/intrinsics.h>
  - <https://raw.githubusercontent.com/davidediger/sfft/HEAD/src/computefourier-3.0.cc>
  - <https://raw.githubusercontent.com/davidediger/sfft/HEAD/src/computefourier-1.0-2.0.cc>
  - <https://raw.githubusercontent.com/davidediger/sfft/HEAD/src/parameters.cc>
  - <https://raw.githubusercontent.com/davidediger/sfft/HEAD/src/utils.cc>
  - <https://raw.githubusercontent.com/davidediger/sfft/HEAD/wscript>
  - <https://raw.githubusercontent.com/davidediger/sfft/HEAD/configure>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/davidediger/sfft`) · [data/wave8/enrich/raw/github_com_davidediger_sfft.json](../../../data/wave8/enrich/raw/github_com_davidediger_sfft.json) (enrichment confidence 0.7)

</details>
