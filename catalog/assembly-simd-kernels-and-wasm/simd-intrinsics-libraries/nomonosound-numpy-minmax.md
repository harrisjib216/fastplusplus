# numpy-minmax

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [SIMD intrinsics libraries](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C (Python extension)` · `MIT` · 🟢 active

> Single-pass AVX/AVX-512 min and max for float32 and int16 NumPy arrays, replacing separate np.amin and np.amax passes.

| | |
|---|---|
| **Beats** | NumPy np.amin followed by np.amax |
| **Claimed result** | README: 'Roughly 2.3x speedup compared to the numpy amin+amax equivalent (tested on Intel CPU with numpy 1.24-1.26)'. |
| **Workload** | Minimum and maximum of float32 NumPy arrays (C/F-contiguous or 1-D strided; up to 999,999,999 elements in the script, plus 100,000 small 9-element and 3x9 arrays) and contiguous int16 arrays in one pass using AVX/AVX-512 (C via cffi). |
| **Metric** | throughput |
| **Hardware** | 'Intel CPU' (model not stated) |
| **Compiler and flags** | Measurement compiler not stated; the build file numpy_minmax/_minmax_cffi.py sets -O3 -Wall (-Wextra on POSIX) -mavx -mavx512f on x86, and CHANGELOG 0.2.1 says Linux wheels are built with clang. Benchmark: scripts/perf_benchmark.py (time.time, numpy pair timed once, minmax median of 5, diplib also compared). |
| **Adoption** | 16 stars; PyPI package numpy-minmax |
| **Last commit** | 2026-06-04 |
| **Links** | [repository](https://github.com/nomonosound/numpy-minmax) · [benchmark](https://github.com/nomonosound/numpy-minmax) |

## Verdict

The README gives one figure, roughly 2.3x over np.amin followed by np.amax, on an unnamed Intel CPU with numpy 1.24-1.26; no table or output is published. scripts/perf_benchmark.py times numpy's pair once and minmax as the median of 5 with time.time() (diplib is a third arm), over 100,000 9-element and 3x9 arrays and over arrays of about 1e9 float32 elements (1-D, 2-D C/F, flipped, stride 5). Issue #15 concedes each test runs one iteration with notable variation on small arrays. The large-array gain is what fusing two memory-bound passes into one predicts, and none of the benchmark inputs contain NaN or infinity.

## Use it when

- Large contiguous float32 buffers (audio frames, images, sensor dumps) on Linux x86-64 where you need both extremes and the data is known to be finite: one memory pass instead of two.
- Contiguous int16 PCM audio on Linux x86-64 with AVX2.
- 1-D strided float32 views such as one channel of interleaved audio (a[::n]), which NumPy reduces with two strided passes.
- Projects pinned to NumPy 2.0-2.5, which have no single-pass min/max; NumPy 2.6 adds np.minmax.

## Skip it when

- Data that can contain NaN or consist only of infinities: results can be silently wrong (see gotchas). np.amin/np.amax propagate NaN; np.nanmin/np.nanmax ignore it.
- NumPy 2.6 or later: np.minmax (numpy/numpy PR #32231, merged 2026-09-10) does the same single pass for every dtype, with axis support and NaN propagation. A NumPy maintainer measured 9.15 ms vs 17.7 ms for min+max on 1e8 float64 values.
- Windows, macOS or ARM wheels: the published win_amd64 0.6.0 wheel contains only the scalar pairwise loop (no AVX instructions in the binary), the macOS wheels are arm64-only, and ARM has no NEON path (issue #18), so the advertised AVX speedup exists only in the Linux x86-64 wheels.
- Many tiny arrays: constant cffi and Python dispatch cost dominates (issue #16: 9-element and 23-element arrays take about the same time), and no small-array win is published.
- float64, other integer types, N-D strided arrays or per-axis reductions: these take the np.amin + np.amax fallback, plus wrapper overhead.

## How it is fast

Pass fusion: one sweep over memory updates both a running-min and a running-max vector (_mm256_min_ps/_mm256_max_ps, or the _mm512 versions when CPUID reports AVX-512F; _mm256_min_epi16 for int16), followed by a horizontal reduction and a pairwise scalar tail. On large arrays the workload is memory-bound, so reading the data once instead of twice is the bulk of the claimed 2.3x. 1-D strided float32 is packed into vectors with _mm256_set_ps, which the comments say beat hardware gather.

## Compared with alternatives

Pick it over argminmax (Rust, returns indices, has NaN-aware variants and runtime SIMD dispatch including NEON) only when you are in Python, need the values for NaN-free float32 or int16 data on Linux x86-64, and cannot move to NumPy 2.6's np.minmax. vstat covers wider descriptive statistics from C++.

## Integration

| | |
|---|---|
| **Form** | module (PyPI wheels built with cffi; the C kernel is a single _minmax.c file of about 300 lines that can be vendored) |
| **Dependencies** | numpy&gt;=2,&lt;3, cffi&gt;=1.0.0 |
| **Minimum toolchain** | CPython 3.10-3.14, including free-threaded 3.14t wheels; numpy 2.x (use a pre-0.4.0 release for numpy 1.x); an sdist build on x86 needs a compiler that accepts -mavx -mavx512f (Linux wheels use clang) |
| **Platforms** | x86-64 Linux: every float32 call needs AVX, the int16 path needs AVX2, and AVX-512F is used when detected. aarch64 Linux, macOS arm64 and the Windows x86-64 wheel: scalar only. No Windows arm64 build (issue #31). |
| **Thread safety** | not documented. The C kernels keep no global mutable state, cffi releases the GIL around the call (PyEval_SaveThread in the 0.6.0 Linux wheel), and cp314t wheels are published, so concurrent calls on arrays that are not being mutated look safe. |
| **Drop-in for the baseline** | partial — returns the same (min, max) as (np.amin(a), np.amax(a)) for finite float32 and int16 data, but has no axis, keepdims, out, where or initial arguments, and differs from NumPy on NaN and all-infinity inputs |

## Gotchas

- NaN corrupts results instead of propagating. MINPS returns its second operand when either input is NaN, so a NaN lane overwrites the accumulated minimum and the next chunk replaces it. In the scalar pairwise code a NaN knocks its pair partner out of the comparison. Emulating the exact C logic: 32 float32 values with -5 at index 0 and NaN at index 16 give (1.0, 1.0) on the AVX-512 path, [0, NaN, 5, 6] gives (5, 6), [1, 2, 3, NaN] gives (NaN, NaN), and 32 NaNs give (3.4028235e38, -3.4028235e38). Each case matches neither np.amin (NaN) nor np.nanmin. The tests have no NaN case; open issue #38 only asks for nanmax-style behaviour.
- The SIMD accumulators start at FLT_MAX and -FLT_MAX instead of the first element or infinity. A float32 array of 16 or more +inf values whose length is a multiple of the vector width (16 with AVX-512, 8 with AVX) returns min = 3.4028235e38 instead of inf; all -inf returns max = -3.4028235e38.
- A 1-D float32 view with stride 0 and at least 16 elements, such as np.broadcast_to(np.float32(1), (16,)) (C_CONTIGUOUS False, strides (0,)), sends x86-64 into minmax_avx_strided_float32, whose loop step is 8\*stride = 0, so the call never returns. The GIL is released during the hang.
- ISA dispatch is fragile. The AVX path and the AVX2 int16 path run without any CPUID check (SIGILL on x86-64 CPUs lacking them). The AVX-512 check runs CPUID leaf 7 on every call of 16 or more elements without setting ECX, because the code uses __cpuid rather than __cpuid_count, so the subleaf is whatever the register holds. Detection can silently miss AVX-512, and under virtualization every call pays a CPUID VM exit. On the positive side, the 0.6.0 cp312 manylinux wheel confines zmm code to minmax_avx512_float32.

## Known shortcomings

- One 2.3x ratio with no table or CPU model, measured on numpy 1.24-1.26 although the package needs numpy&gt;=2 since 0.4.0; the script times numpy once against a median of 5 for minmax; NaN is not propagated (NumPy propagates it) and the int16 AVX2 path has no CPUID check.
- Correctness bugs in the C kernel, found by reading the source and confirmed by Python emulation: NaN drops the true min/max (-5 at index 0 plus NaN at index 16 returns (1.0, 1.0)); an all-+inf array whose length is a multiple of the vector width returns min = FLT_MAX; a stride-0 1-D view such as np.broadcast_to(np.float32(1), (16,)) loops forever on x86 with the GIL released; CPUID leaf 7 runs on every call without ECX set; AVX and AVX2 are used with no CPU check. Disassembly: the win_amd64 0.6.0 wheel is scalar only (no AVX instructions); SIMD exists only in the Linux x86-64 wheels. The benchmark inputs had no NaN or inf, so the numbers stand; the harness takes one numpy run vs the median of 5 (issue #15 admits one iteration).

## Caveats and trade-offs

One headline ratio, no table, no CPU model ('Intel CPU'), measured against numpy 1.24-1.26 while the package has required numpy&gt;=2,&lt;3 since 0.4.0 (2025-03), so the claim predates the current baseline. scripts/perf_benchmark.py times np.amin+np.amax once but takes the median of 5 minmax runs, and prints times without published output; the win on large arrays is expected from one pass versus two over memory. Semantics differ from NumPy: NaN is not propagated (minps/maxps and &lt; comparisons drop NaN; np.amin/np.amax return NaN) and the tests have no NaN case. Only float32 (C/F-contiguous or 1-D strided) and contiguous int16 are accelerated; other inputs fall back to np.amin/np.amax. The int16 AVX2 path runs without a CPUID check and the whole C file is compiled with -mavx512f. ARM has no NEON path. [retier] One headline ratio, no table, no CPU model ('Intel CPU'), measured against numpy 1.24-1.26 while the package has required numpy&gt;=2 since 0.4.0; scripts/perf_benchmark.py times np.amin+np.amax once but takes the median of 5 minmax runs (issue #15 admits one iteration), and the win on large arrays is expected from one pass versus two over memory. Correctness bugs (read in the C source, confirmed by Python emulation; the benchmark inputs have no NaN or inf, so the numbers stand): NaN is not propagated and corrupts results (MINPS returns its second operand on NaN, so -5 at index 0 plus NaN at index 16 in a 32-element float32 array returns (1.0, 1.0); [1, 2, 3, NaN] gives (NaN, NaN)); the SIMD accumulators start at FLT_MAX and -FLT_MAX, so an all-+inf array whose length is a multiple of the vector width returns min = 3.4028235e38; a stride-0 1-D float32 view of 16 or more elements (np.broadcast_to) enters minmax_avx_strided_float32 with a loop step of 0 and never returns, with the GIL released; the AVX and AVX2 int16 paths run with no CPUID check (SIGILL on CPUs lacking them) and the AVX-512 check runs CPUID leaf 7 on every call without setting ECX (__cpuid rather than __cpuid_count), so detection can silently miss and virtualized hosts pay a VM exit per call. The win_amd64 0.6.0 wheel is scalar only (no AVX instructions in its disassembly); SIMD exists only in the Linux x86-64 wheels. Only float32 (contiguous or 1-D strided) and contiguous int16 are accelerated.

Fast path for float32 C-contiguous, F-contiguous or 1D strided arrays and contiguous int16; strided arrays with ndim &gt;= 2 fall back to numpy amin/amax with no gain; Linux (arm and x86-64), macOS arm, Windows x86-64 wheels.

## Maintenance

Lightly maintained by Nomono (0.6.0 tagged 2025-12-27, wheels for CPython 3.10-3.14 uploaded 2026-06-26, last commit a 2026-06-04 dependency bump), MIT and labelled alpha. The 2.3x is an unpublished one-iteration numpy-1.x figure; SIMD exists only in the Linux x86-64 wheels; NaN, all-infinity and stride-0 inputs give wrong results or hang; and NumPy 2.6's np.minmax will cover the same use upstream.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README states one ratio (about 2.3x versus np.amin followed by np.amax) with no published table, no CPU model and no compiler stated for the run; the benchmark script scripts/perf_benchmark.py is public but its output is not published.
- **Verifier notes:** Ratio matches the README text; no table exists. Shortcomings to record: single unsourced ratio with no CPU model, measured on numpy 1.x while the current release targets numpy 2.x, asymmetric timing (one numpy run versus median of 5), NaN not propagated unlike NumPy, AVX2 int16 path without a CPU check. Last code change 2026-02-06 (Python 3.14); last commit 2026-06-04 is a dependency bump; PyPI 0.6.0.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`, `workload`
- **Shortcomings recorded by:** verifier batch-59 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/nomonosound/numpy-minmax>
  - <https://github.com/nomonosound/numpy-minmax/commits>
  - <https://github.com/nomonosound/numpy-minmax/tree/main/tests>
  - <https://raw.githubusercontent.com/nomonosound/numpy-minmax/HEAD/README.md>
  - <https://raw.githubusercontent.com/nomonosound/numpy-minmax/HEAD/scripts/perf_benchmark.py>
  - <https://raw.githubusercontent.com/nomonosound/numpy-minmax/HEAD/pyproject.toml>
  - <https://raw.githubusercontent.com/nomonosound/numpy-minmax/HEAD/setup.py>
  - <https://raw.githubusercontent.com/nomonosound/numpy-minmax/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/nomonosound/numpy-minmax/HEAD/numpy_minmax/_minmax_cffi.py>
  - <https://raw.githubusercontent.com/nomonosound/numpy-minmax/HEAD/numpy_minmax/_minmax.c>
  - <https://raw.githubusercontent.com/nomonosound/numpy-minmax/HEAD/numpy_minmax/__init__.py>
  - <https://raw.githubusercontent.com/nomonosound/numpy-minmax/HEAD/tests/test_minmax.py>
  - <https://pypi.org/pypi/numpy-minmax/json>
- **Sources the enricher read:**
  - <https://github.com/nomonosound/numpy-minmax/issues?q=is%3Aissue>
  - <https://github.com/nomonosound/numpy-minmax/issues/15>
  - <https://github.com/nomonosound/numpy-minmax/issues/16>
  - <https://github.com/nomonosound/numpy-minmax/issues/38>
  - <https://raw.githubusercontent.com/nomonosound/numpy-minmax/HEAD/README.md>
  - <https://raw.githubusercontent.com/nomonosound/numpy-minmax/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/nomonosound/numpy-minmax/HEAD/pyproject.toml>
  - <https://raw.githubusercontent.com/nomonosound/numpy-minmax/HEAD/setup.py>
  - <https://raw.githubusercontent.com/nomonosound/numpy-minmax/HEAD/scripts/perf_benchmark.py>
  - <https://raw.githubusercontent.com/nomonosound/numpy-minmax/HEAD/numpy_minmax/_minmax_cffi.py>
  - <https://raw.githubusercontent.com/nomonosound/numpy-minmax/HEAD/numpy_minmax/_minmax.c>
  - <https://raw.githubusercontent.com/nomonosound/numpy-minmax/HEAD/numpy_minmax/__init__.py>
  - <https://raw.githubusercontent.com/nomonosound/numpy-minmax/HEAD/tests/test_minmax.py>
  - <https://pypi.org/pypi/numpy-minmax/json>
  - https://files.pythonhosted.org/packages/5c/a5/bc7e17149c2000d462d7c2ce80c3ce06d05e0c12dd93a6b69392c3cdbba7/numpy_minmax-0.6.0-cp312-cp312-manylinux1_x86_64.manylinux_2_28_x86_64.manylinux_2_5_x86_64.whl (disassembled with objdump)
  - numpy_minmax-0.6.0-cp312-cp312-win_amd64.whl from files.pythonhosted.org (disassembled with llvm-objdump)
  - <https://raw.githubusercontent.com/numpy/numpy/main/numpy/_core/src/umath/loops_minmax.dispatch.c.src>
  - <https://raw.githubusercontent.com/numpy/numpy/main/numpy/_core/code_generators/generate_umath.py>
  - <https://raw.githubusercontent.com/numpy/numpy/main/numpy/_core/code_generators/ufunc_docstrings.py>
  - <https://raw.githubusercontent.com/numpy/numpy/main/numpy/_core/fromnumeric.py>
  - <https://raw.githubusercontent.com/numpy/numpy/main/pyproject.toml>
  - <https://github.com/numpy/numpy/commits/main/numpy/_core/src/umath/loops_minmax.dispatch.c.src>
  - <https://github.com/numpy/numpy/pull/32231>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/nomonosound/numpy-minmax`) · [data/wave13/enrich/raw/github_com_nomonosound_numpy_minmax.json](../../../data/wave13/enrich/raw/github_com_nomonosound_numpy_minmax.json) (enrichment confidence 0.8)

</details>
