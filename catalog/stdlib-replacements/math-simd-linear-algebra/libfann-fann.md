# FANN (Fast Artificial Neural Network Library)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Math, SIMD and linear algebra](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `LGPL-2.1` · 🟢 active

> Small C library for training and running multilayer perceptrons; 2003 report shows 164x over jneural, \~1.3x over lwnn.

| | |
|---|---|
| **Beats** | Lightweight Neural Network (lwnn 0.6) and Jet's Neural Library (jneural 1.05) |
| **Claimed result** | AMD Athlon, four layers of 128 neurons: "the fann (thres) library is 238.583 times faster than the jneural library and the fann library is 164.388 times faster than the jneural library"; table: lwnn 4.007 ns per connection (127.074x jneural), jneural 509.138 ns, so standard fann is about 3.10 ns and about 1.29x faster than lwnn (derived from page data). At 512 neurons: fann 64.867x jneural (about 8.07 ns, derived) versus lwnn 8.662 ns and jneural 523.175 ns, so fann is about 1.07x lwnn (derived from page data). At 8 neurons lwnn (11.962 ns) is faster than standard fann per the text. iPAQ, 128 neurons: fann (fix) 188.134 ns per connection versus jneural 13,108.617 ns, "almost 70 times faster than the jneural library and more than 40 times faster than the lwnn library"; the 2.7x remark compares fann (fix) on the iPAQ with jneural on the Athlon. README: "up to 150 times faster execution than other libraries" (no baseline named). |
| **Workload** | Execution time per connection (nanoseconds) for fully connected four-layer ANNs with equal layer sizes (doubling from 1 neuron; 128 neurons per layer is the headline case), each size executed continuously for 20 seconds, on an AMD Athlon XP 1600+ (1400 MHz) and on a 206 MHz StrongARM iPAQ H3600 without an FPU, from Steffen Nissen's 2003 FANN report. |
| **Metric** | throughput |
| **Hardware** | AMD Athlon XP 1600+ (1400 MHz, 256 KB L2) and 206 MHz Intel StrongARM iPAQ H3600, both Linux |
| **Compiler and flags** | Same compiler and compile options for all three libraries per the report; compiler and flags not named on the page |
| **Adoption** | 1.8k stars; packaged in Debian, Fedora and vcpkg |
| **Last commit** | 2026-07-06 |
| **Links** | [repository](https://github.com/libfann/fann) · [benchmark](https://fann.sourceforge.net/report/node8.html) |

## Verdict

Steffen Nissen's own 2003 report timed four-layer fully connected nets (forward pass only) for 20 s each on an AMD Athlon XP 1600+ and a 206 MHz StrongARM iPAQ, all three libraries built with the same unnamed compiler and options: at 128 neurons per layer standard fann ran about 3.1 ns/connection versus 509 ns for a single-precision-modified jneural 1.05 (164x) and 4.0 ns for lwnn 0.6 (about 1.3x, derived from page data), shrinking to about 1.07x over lwnn at 512 neurons; on the iPAQ the fixed-point build was about 70x faster than jneural and over 40x faster than lwnn.

## Use it when

- Small MLPs (tens to a few hundred neurons per layer) for classic tabular or control problems where you want training and inference in one dependency-free C library
- Microcontrollers or CPUs without an FPU: the fixed-point build (fixedfann) runs a float-trained net exported with fann_save_to_fixed using only integer arithmetic
- Projects that need Cascade2 constructive training or RPROP out of the box and a stable on-disk network format
- Embedding a NN into an LGPL-compatible C or C++ program, or via one of its many language bindings, where a deep-learning framework is too heavy

## Skip it when

- Anything needing convolutions, recurrence, attention, GPUs or modern layers: FANN is MLP-only and CPU-only
- Throughput-critical inference on modern CPUs: the forward pass is scalar C with strided neuron reads and no SIMD or BLAS, and no benchmark against any post-2003 library exists, so a gemv-based implementation may well be faster (not measured)
- Sparse networks: the 2003 report itself says sparse connected ANNs 'have serious performance problems in the fann library'
- Very small nets (about 8 neurons per layer) on desktop CPUs: lwnn's table-lookup sigmoid beat standard fann there in the report
- Static linking into closed-source products if LGPL-2.1 relinking obligations are a problem

## How it is fast

All weights live in one contiguous array and all neurons in one array, so a fully connected layer is a straight dot product over weights[] with a 4-way manually unrolled loop (fann_run in src/fann.c); a separate pointer-chasing path is used only for sparse nets. A fixed-point build (fixedfann, int fann_type, stepwise-linear sigmoid with six precomputed breakpoints) avoids floating point entirely on FPU-less CPUs, which is where the 70x iPAQ result comes from. There is no SIMD, BLAS or threading in the forward pass; the per-neuron struct is packed (24 bytes) so neuron values are read with a 24-byte stride.

## Compared with alternatives

The catalogued siblings (xsimd, SLEEF, NumKong, VDT, fmath and others) are math or SIMD primitives, not neural-network libraries; pick FANN when you want a complete train-and-run MLP library, and reach for NumKong-style dot kernels or a BLAS gemv if you only need fast dense forward passes.

## Integration

| | |
|---|---|
| **Form** | shared lib (static variants also built: fann, floatfann, doublefann, fixedfann); header-only C++ wrapper |
| **Dependencies** | none for the library (libm on Unix); OpenMP optional for the parallel training functions; bundled GoogleTest for tests |
| **Minimum toolchain** | C compiler (C89-style code), CMake 3.5+; C++11 only for the test suite |
| **Platforms** | any (portable C; Linux, macOS, Windows/MSVC builds; fixed-point build for FPU-less targets) |
| **Thread safety** | Not documented. fann_run writes neuron sums and values into the struct fann and returns a pointer to the net's internal output buffer, so one network cannot be run concurrently; use fann_copy per thread. OpenMP-parallel training exists only via parallel_fann.h (fann_train_epoch_\*_parallel). |
| **Drop-in for the baseline** | no |

## Gotchas

- Benchmark harness (report appendix B.3.3 performance.cc): the author modified the jneural baseline from double to single precision before timing it, and the 20-second loop calls time_elapsed() on every iteration, so timer overhead is included per network evaluation and inflates small-network ns/connection for all libraries; the 238x headline uses a threshold activation that skips the sigmoid.
- fann_run returns ann-&gt;output, an internal buffer overwritten by the next call; copy the outputs if you need them later.
- Fixed-point build: fann_mult is (x\*y)&gt;&gt;decimal_point on int, so out-of-range inputs overflow; fann_run only printf()s a warning per out-of-range input in the hot path, and Elliot, Gaussian, sin and cos activations raise FANN_E_CANT_USE_ACTIVATION.
- Last tagged release is 2.2.0 (2013-03-10); distro packages ship that, while master has later additions (Adam, new activations, a new file-format version for Adam).

## Known shortcomings

- 2003 author report vs jneural and lwnn; compiler and flags unnamed and the benchmark code exists only in the report's appendix B.3.3. The 238x headline uses threshold activation, not sigmoid; only \~1.3x over lwnn at 128 neurons, \~1.07x at 512, and slower at 8.
- Enricher: in the report's appendix B.3.3 performance.cc the author converted the jneural baseline from double to single precision before timing, time_elapsed() is polled every iteration (timer overhead inflates small-net ns/connection) and the 238x headline uses threshold activation. The code is a scalar 4-way unrolled loop with no SIMD or BLAS reading a packed 24-byte neuron struct strided; fann_run is not reentrant (writes into struct fann, returns an internal buffer); the only tag is 2.2.0 (2013-03-10).

## Caveats and trade-offs

Author's own 2003 report, measured on 2003 hardware against two obscure libraries (jneural, lwnn); no comparison with any current ML library. The benchmark programs (performance.cc, benchmark.sh) are printed in the report's appendix B.3.3/B.3.4 but are not in the current repo (no benchmarks directory), and the compiler and flags are not named (only 'same compiler and the same compile-options'). Table values come from the LaTeX ALT text of image tables on the page (lwnn 4.007 ns and 127.074x, jneural 509.138 ns at 128 neurons; lwnn 8.662 ns, jneural 523.175 ns at 512). The 238.583x headline uses fann (thres), a threshold activation that does not compute the sigmoid, so it is not the same computation as the baselines; the like-for-like figure is 164.388x for standard fann. Against lwnn the win is small (about 1.3x at 128 neurons, about 1.07x at 512) and lwnn is faster at 8 neurons. The README '150 times' figure names no baseline.

Multilayer perceptrons only (RPROP, Quickprop, batch, incremental, Cascade2), CPU only, no GPU or convolutions; fixed-point mode exists for FPU-less devices; cache-optimised layout. LGPL.

## Maintenance

Maintained at a low pace (Adam training added January 2026, last commit 2026-07-06) but no release since 2.2.0 in 2013; LGPL-2.1, small portable C, packaged in Debian, Fedora and vcpkg, and its only speed evidence is the 2003 first-party report against libraries nobody uses today.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party 2003 report by the FANN author; the benchmark programs are public in its appendix (B.3.3 performance.cc, B.3.4 benchmark.sh at fann.sourceforge.net/report/node12.html) and the CPUs are named, but the compiler and flags are not stated, and it is not peer-reviewed, so it stays C.
- **Verifier notes:** Report page and its image-table ALT text confirm the ratios; the earlier caveat that WebFetch reads disagreed is superseded by the ALT text values. Shortcomings to record: 2003 first-party report on 2003 hardware against obscure jneural/lwnn, compiler and flags unnamed, benchmark code only in the report appendix, 238x headline uses a non-sigmoid activation, only about 1.3x over lwnn and slower than lwnn on small nets.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `caveats`
- **Shortcomings recorded by:** author's 2003 report (verifier); enricher code reading
- **Pages the verifier opened:**
  - <https://fann.sourceforge.net/report/node8.html>
  - <https://fann.sourceforge.net/report/node12.html>
  - <https://github.com/libfann/fann>
  - <https://raw.githubusercontent.com/libfann/fann/HEAD/README.md>
  - <https://raw.githubusercontent.com/libfann/fann/HEAD/LICENSE.md>
  - <https://github.com/libfann/fann/commits/master.atom>
- **Sources the enricher read:**
  - <https://github.com/libfann/fann>
  - <https://raw.githubusercontent.com/libfann/fann/HEAD/README.md>
  - <https://raw.githubusercontent.com/libfann/fann/HEAD/LICENSE.md>
  - <https://raw.githubusercontent.com/libfann/fann/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/libfann/fann/HEAD/src/CMakeLists.txt>
  - <https://raw.githubusercontent.com/libfann/fann/HEAD/src/fann.c>
  - <https://raw.githubusercontent.com/libfann/fann/HEAD/src/fann_train.c>
  - <https://raw.githubusercontent.com/libfann/fann/HEAD/src/include/fann.h>
  - <https://raw.githubusercontent.com/libfann/fann/HEAD/src/include/fann_data.h>
  - <https://raw.githubusercontent.com/libfann/fann/HEAD/src/include/fann_activation.h>
  - <https://raw.githubusercontent.com/libfann/fann/HEAD/src/include/fann_internal.h>
  - <https://raw.githubusercontent.com/libfann/fann/HEAD/src/include/fann_cpp.h>
  - <https://raw.githubusercontent.com/libfann/fann/HEAD/src/include/floatfann.h>
  - <https://raw.githubusercontent.com/libfann/fann/HEAD/src/include/parallel_fann.h>
  - <https://raw.githubusercontent.com/libfann/fann/HEAD/src/include/config.h>
  - <https://fann.sourceforge.net/report/node8.html>
  - <https://fann.sourceforge.net/report/node12.html>
  - <https://github.com/libfann/fann/issues?q=is%3Aissue+crash+OR+overflow+OR+performance+OR+thread+OR+slow>
  - <https://github.com/libfann/fann/issues/145>
  - <https://github.com/libfann/fann/issues/110>
  - <https://github.com/libfann/fann/commits/master.atom>
  - <https://github.com/libfann/fann/tags>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/libfann/fann`) · [data/wave1/enrich/raw/github_com_libfann_fann.json](../../../data/wave1/enrich/raw/github_com_libfann_fann.json) (enrichment confidence 0.72)

</details>
