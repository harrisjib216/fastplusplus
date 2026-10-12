# wavelib

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [FFT](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `BSD-3-Clause` · 🟢 active

> Plain C wavelet library (DWT, SWT, MODWT, packets, CWT); its WebAssembly build beats pure-JS discrete-wavelets by 82-154x on wavedec.

| | |
|---|---|
| **Beats** | discrete-wavelets (npm pure-JavaScript 1D DWT package, ^5.0.15); PyWavelets under Pyodide also measured |
| **Claimed result** | wavedec vs discrete-wavelets (pure JS): 100000 db2 1.28 vs 162.48 ms (\~127x, derived from page data); 100000 db4 2.27 vs 185.34 ms (\~82x derived); 1000000 db2 13.19 vs 2030.32 ms (\~154x derived); 1000000 db4 22.94 vs 2572.65 ms (\~112x derived); discrete-wavelets has no waverec result (N/A). Against PyWavelets in Pyodide (data kept in Python memory) wasmlets decomposition is slower in all four cases (1.28 vs 1.23, 2.27 vs 1.64, 13.19 vs 10.16, 22.94 vs 14.93 ms; PyWavelets 1.5x faster on 1M db4), while reconstruction is faster in three of four (0.77 vs 1.20, 1.30 vs 1.41, 8.85 vs 9.70 ms) and slower on 1M db4 (15.18 vs 12.88 ms). Against PyWavelets with per-trial JS/Python marshalling, wasmlets is faster in every case (e.g. 1.28 vs 4.95 ms dec, 0.77 vs 4.94 ms rec at 100000 db2). |
| **Workload** | 1D discrete wavelet decomposition (wavedec) and reconstruction (waverec), db2/db4, Float64 arrays of 100k and 1M samples, Node.js, each op averaged over a 1000 ms loop; wasmlets is wavelib compiled to WebAssembly. |
| **Metric** | latency |
| **Hardware** | GitHub Actions ubuntu-latest runner; CPU model not stated |
| **Compiler and flags** | Emscripten (emcc) build of wavelib via the wasmlets Makefile with CFLAGS -O3 --closure 1 (emcc version not pinned or stated). Benchmark harness is TypeScript on Node.js 18 in GitHub Actions; PyWavelets comes from pyodide ^0.25.0; wasmlets ^0.0.6 in package.json. |
| **Adoption** | 446 stars (rafat/wavelib); wasmlets (flatironinstitute) builds on it |
| **Last commit** | 2025-12-12 |
| **Links** | [repository](https://github.com/rafat/wavelib) · [benchmark](https://raw.githubusercontent.com/flatironinstitute/web-wavelets-benchmarking/benchmark-results/benchmark-results/benchmark.md) |

## Verdict

A third-party CI benchmark by the wasmlets authors ran wavelib compiled with emcc -O3 --closure 1 on Node.js 18 (GitHub Actions ubuntu-latest, CPU not recorded), averaging each op over a 1000 ms loop: db2/db4 wavedec at 100k and 1M samples took 1.28-22.94 ms versus 162-2573 ms for the pure-JS discrete-wavelets package (82-154x, derived from page data). Against PyWavelets compiled to WebAssembly under Pyodide it is slower on all four decompositions (e.g. 22.94 vs 14.93 ms at 1M db4) and faster on three of four reconstructions; it wins every row only when PyWavelets pays JS-to-Python marshalling per call.

## Use it when

- You need DWT, SWT, MODWT or wavelet packets from plain C (or C++ via extern "C") with a permissive licence and no dependencies beyond libm.
- Browser or Node.js code that needs a 1-D wavedec/waverec without loading Pyodide: through wasmlets it runs 1M-sample db2/db4 decompositions in 13-23 ms versus 2.0-2.6 s for the pure-JS discrete-wavelets package.
- Embedded or small builds where vendoring a handful of .c files is preferable to depending on PyWavelets, GSL or a C++ template library.
- MODWT on signals of arbitrary length (orthogonal wavelets only), following Percival and Walden.

## Skip it when

- Continuous wavelet transforms where speed matters: fCWT's README (MacBook Pro 2019 i9) shows wavelib slowest of all tested CWTs, 45.04 s at 100k samples x 3000 scales against PyWavelets 12.69 s and fCWT 0.32 s.
- As a faster PyWavelets: in the same WebAssembly benchmark PyWavelets under Pyodide decomposes faster at every size (up to 1.5x on 1M db4) and reconstructs faster on 1M db4.
- Library code that must not terminate the host: invalid wavelet names, too many levels or a bad extension string call printf and exit(-1) (56 exit calls in wavelib.c alone).
- Very large inputs: buffer sizes are computed in int and none of the \~120 malloc results in wavelib.c is checked; issue #19 (open) reports a null-pointer write in modwt2 on a 23000x30000 image.
- As an FFT library: the category is a loose fit; the internal FFT exists only to serve convolution and CWT and has no published comparison against FFTW, PocketFFT or KissFFT.

## How it is fast

Nothing exotic: the default 'direct' path evaluates the decimated filter only at every second output position with periodic or symmetric extension handled inline per tap (dwt_per_stride / dwt_sym_stride in wtmath.c), computing the low-pass and high-pass outputs in the same loop instead of convolving fully and then downsampling. An optional FFT convolution path uses the library's own mixed-radix plus Bluestein FFT (hsfft.c), and the CWT is FFT-based. The code is scalar, single-threaded C with no SIMD or OpenMP; the measured 82-154x gap is compiled C (as WebAssembly) against a pure-JavaScript implementation, not an algorithmic advantage.

## Compared with alternatives

Among the catalogued siblings only fCWT overlaps, and it is far faster for CWT; pick wavelib when you need decimated or undecimated discrete transforms (DWT, SWT, MODWT, packets), which fCWT does not provide. The FFT siblings (PocketFFT, PFFFT, KFR and others) are better choices for plain FFTs.

## Integration

| | |
|---|---|
| **Form** | static lib (CMake builds libwavelib and libwauxlib) or source-drop of the src/\*.c files |
| **Dependencies** | none beyond the C standard library and libm; the default BUILD_UT=ON also builds a C++ unit-test target |
| **Minimum toolchain** | C compiler accepting zero-length trailing arrays (params[0], a GNU/MSVC extension); CMake 3.5+ (issue #41, opened Oct 2026, reports configure failure with CMake 4.5, no details yet); Emscripten for the wasmlets build |
| **Platforms** | any (portable scalar C; WebAssembly via wasmlets) |
| **Thread safety** | not documented; each transform object holds mutable state (output buffer, FFT convolution object), so use one wt_object per thread; no file-scope mutable state seen in the sources read |
| **Drop-in for the baseline** | no |

## Gotchas

- Error handling is printf plus exit(-1) throughout (bad wavelet name, J above the maximum level, unknown extension or convolution method), so a malformed argument terminates the calling process instead of returning an error code; wrappers must validate inputs first.
- Allocation sizes such as siglength\*(J+1) are int arithmetic and no malloc result is NULL-checked; large 2-D inputs can overflow or dereference NULL (issue #19, modwt2/swt2 on 23000x30000).
- idwt only reads coefficients left in the object by a prior dwt(); there is no public setter, so wasmlets patches wt-&gt;output and wt-&gt;length through a helper its own comments call 'not an official part of the wavelib API'. SWT additionally requires the signal length to be a multiple of 2^J.
- Benchmark harness notes (flatironinstitute/web-wavelets-benchmarking src/benchmark.ts): wasmlets and PyWavelets round trips are checked against each other to 1e-6, but discrete-wavelets output is never checked and its waverec is disabled because it hangs; wasmlets and discrete-wavelets use the same PyWavelets max-level formula and symmetric mode, so levels match; the runner CPU is not recorded and the systemInfo label says wasmlets 0.0.3 while package.json pins ^0.0.6. No correctness bug was found behind the numbers.

## Known shortcomings

- Numbers are a CI run of flatironinstitute/web-wavelets-benchmarking (by the wasmlets wrapper's authors, emcc -O3 --closure 1, emcc version unstated) measuring the wasm wrapper, not native wavelib; wasmlets is slower than PyWavelets on all 4 wavedec rows, faster on 3 of 4 waverec rows; the only clear win is over pure-JS discrete-wavelets; no FFTW comparison; slowest CWT in the fCWT README (45.04 s vs PyWavelets 12.69 s); loose fit for fft.
- Enricher: no harness bug behind the numbers (same max-level formula and sym mode, wasmlets and PyWavelets round trips checked to 1e-6), but discrete-wavelets output is never checked and its waverec is disabled (hangs), the CI CPU is unrecorded, and the label says wasmlets 0.0.3 while package.json pins ^0.0.6. wavelib is scalar single-threaded direct convolution without SIMD; PyWavelets-in-Pyodide is faster on all 4 decompositions. Library flaws: 56 exit(-1) calls on bad arguments, about 120 unchecked mallocs in wavelib.c, int size arithmetic, open null write in modwt2 at 23000x30000 (#19), CMake 4.5 configure failure (#41), no public idwt coefficient setter (wasmlets hacks struct fields).

## Caveats and trade-offs

Weak evidence for the project itself. (1) No FFTW comparison anywhere: README, wiki, repo and web search found none; the guessed baseline FFTW does not apply. (2) The only numbers found come from a third-party benchmark of the wasmlets wrapper, not native wavelib. (3) The baseline discrete-wavelets is a small pure-JS npm package; the \~82-154x gap says little about native C DWT libraries. (4) Against PyWavelets (compiled C under Pyodide) wasmlets is level on 100k db2 and up to 1.5x slower on 1M db4, and the README itself says compute times are similar. (5) discrete-wavelets has no waverec result (N/A). (6) fCWT README (github.com/fastlib/fCWT, MacBook Pro 2019 i9) shows wavelib CWT slower than PyWavelets in every case (e.g. 100k samples x 3000 frequencies: wavelib 45.04 s vs PyWavelets 12.69 s), so wavelib is not fast for CWT. (7) Version labels in the harness are inconsistent (benchmark.ts says wasmlets 0.0.3, package.json ^0.0.6); the results page is the latest CI run and is not timestamped on the page; CI CPU is not stated.

Plain C library covering DWT, SWT, MODWT, CWT and wavelet packets with a BSD-3-Clause licence. The README says DWT uses implicit signal extension and up/downsampling and only optionally an FFT path ('will not be usually needed'), so it is not an FFT competitor and has no FFTW comparison. The measured artefact is the WebAssembly build, not native wavelib.

## Maintenance

Maintained at a low rate by one author (last commits 2025-12-12 fixing a modwt_fft leak and the CMake minimum; open CMake 4.5 configure issue from October 2026); BSD-3-Clause, dependency-free and small enough to vendor, but its exit-on-error and unchecked-allocation style needs wrapping before use inside a long-running service.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The only numbers are a CI run of flatironinstitute/web-wavelets-benchmarking (src/benchmark.ts, by the authors of the wasmlets wrapper) comparing wavelib-in-WebAssembly with a pure-JS package and PyWavelets under Pyodide; code and emcc flags (-O3 --closure 1 in the wasmlets Makefile) are public, but the runner CPU model and emcc version are not stated and it is not a well-known suite, so C.
- **Verifier notes:** Numbers on benchmark.md match the record for the discrete-wavelets comparison; the PyWavelets comparison was slightly overstated as 'no win' (wasmlets wins 3 of 4 reconstruction rows and all marshalling rows) and is corrected. Shortcomings for the orchestrator: no FFTW or other native-library comparison exists; the only win is against a small pure-JS npm package; the measured artefact is the wasmlets WebAssembly wrapper, not native wavelib; fCWT README (MacBook Pro 2019 i9) shows wavelib slowest of all CWT implementations (100k-3000: 45.04 s vs PyWavelets 12.69 s); category 'fft' is a loose fit (wavelet transforms). Metadata confirmed: BSD-3-Clause, 446 stars, 138 forks, last commit 2025-12-12 ('modwt_fft leak plugged'), active.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`
- **Shortcomings recorded by:** verifier batch-177 (wave 8); enricher w8 pair-038
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/flatironinstitute/web-wavelets-benchmarking/benchmark-results/benchmark-results/benchmark.md>
  - <https://github.com/flatironinstitute/web-wavelets-benchmarking>
  - <https://raw.githubusercontent.com/flatironinstitute/web-wavelets-benchmarking/main/README.md>
  - <https://raw.githubusercontent.com/flatironinstitute/web-wavelets-benchmarking/main/package.json>
  - <https://raw.githubusercontent.com/flatironinstitute/web-wavelets-benchmarking/main/src/benchmark.ts>
  - <https://raw.githubusercontent.com/flatironinstitute/web-wavelets-benchmarking/main/.github/workflows/benchmark.yml>
  - <https://github.com/flatironinstitute/wasmlets>
  - <https://raw.githubusercontent.com/flatironinstitute/wasmlets/main/Makefile>
  - <https://github.com/rafat/wavelib>
  - <https://github.com/rafat/wavelib/commits/master>
  - <https://raw.githubusercontent.com/fastlib/fCWT/main/README.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/rafat/wavelib/master/README.md>
  - <https://raw.githubusercontent.com/rafat/wavelib/master/header/wavelib.h>
  - <https://raw.githubusercontent.com/rafat/wavelib/master/CMakeLists.txt>
  - <https://raw.githubusercontent.com/rafat/wavelib/master/src/CMakeLists.txt>
  - <https://raw.githubusercontent.com/rafat/wavelib/master/unitTests/CMakeLists.txt>
  - <https://raw.githubusercontent.com/rafat/wavelib/master/unitTests/wavelibBoostTests/CMakeLists.txt>
  - <https://raw.githubusercontent.com/rafat/wavelib/master/test/CMakeLists.txt>
  - <https://raw.githubusercontent.com/rafat/wavelib/master/auxiliary/CMakeLists.txt>
  - <https://raw.githubusercontent.com/rafat/wavelib/master/src/wavelib.c>
  - <https://raw.githubusercontent.com/rafat/wavelib/master/src/wtmath.c>
  - <https://raw.githubusercontent.com/rafat/wavelib/master/src/conv.c>
  - <https://raw.githubusercontent.com/rafat/wavelib/master/src/hsfft.c>
  - <https://raw.githubusercontent.com/rafat/wavelib/master/src/real.c>
  - <https://raw.githubusercontent.com/rafat/wavelib/master/src/wavefunc.c>
  - <https://github.com/rafat/wavelib/issues?q=is%3Aissue>
  - <https://github.com/rafat/wavelib/issues/41>
  - <https://github.com/rafat/wavelib/issues/19>
  - <https://github.com/rafat/wavelib/commits/master>
  - <https://raw.githubusercontent.com/flatironinstitute/web-wavelets-benchmarking/benchmark-results/benchmark-results/benchmark.md>
  - <https://raw.githubusercontent.com/flatironinstitute/web-wavelets-benchmarking/main/src/benchmark.ts>
  - <https://raw.githubusercontent.com/flatironinstitute/web-wavelets-benchmarking/main/README.md>
  - <https://raw.githubusercontent.com/flatironinstitute/wasmlets/main/Makefile>
  - <https://raw.githubusercontent.com/flatironinstitute/wasmlets/main/README.md>
  - <https://raw.githubusercontent.com/flatironinstitute/wasmlets/main/package.json>
  - <https://raw.githubusercontent.com/flatironinstitute/wasmlets/main/src/index.ts>
  - <https://raw.githubusercontent.com/flatironinstitute/wasmlets/main/src/functional.ts>
  - <https://raw.githubusercontent.com/flatironinstitute/wasmlets/main/c/wavelib_helpers.c>
  - <https://raw.githubusercontent.com/Symmetronic/discrete-wavelets/master/src/wt.ts>
  - <https://raw.githubusercontent.com/fastlib/fCWT/main/README.md>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/rafat/wavelib`) · [data/wave8/enrich/raw/github_com_rafat_wavelib.json](../../../data/wave8/enrich/raw/github_com_rafat_wavelib.json) (enrichment confidence 0.75)

</details>
