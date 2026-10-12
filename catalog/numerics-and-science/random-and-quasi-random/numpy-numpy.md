# NumPy numpy.random Generator (PCG64, PCG64DXSM, SFC64 bit generators)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Random and quasi-random numbers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Python/C (Cython)` · `BSD-3-Clause` · 🟢 active

> NumPy's Generator API with PCG64/PCG64DXSM/SFC64 bit generators and ziggurat samplers; about 1.6-2.5x faster than legacy MT19937 RandomState.

| | |
|---|---|
| **Beats** | MT19937 (legacy RandomState and MT19937 under Generator) |
| **Claimed result** | Uniforms: PCG64 3.1 ns, PCG64DXSM 2.9, SFC64 2.6 versus MT19937 5.9 and legacy RandomState 6.0; 64-bit unsigned ints: PCG64 3.2, SFC64 2.5 versus MT19937 5.6. Overall geometric mean relative to RandomState: PCG64 219%, PCG64DXSM 225%, SFC64 251%, MT19937 under Generator 159%. 64-bit Linux table normalised to MT19937=100: PCG64 161, PCG64DXSM 168, SFC64 192 overall. |
| **Workload** | Time in ns per random value (32-bit and 64-bit unsigned ints, uniforms, normals, exponentials, gammas, binomials, laplaces, poissons) per bit generator under numpy.random.Generator versus legacy RandomState, measured by doc/source/reference/random/performance.py with timeit (each call draws 1,000,000 values, min of 3 repeats), on Linux with an AMD Ryzen 9 3900X; plus relative tables (MT19937 = 100) for 64-bit Linux, 64-bit Windows and 32-bit Windows. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 3900X for all tables (Linux and Windows timings) |
| **Compiler and flags** | Linux tables: GCC 9.3.0 on Ubuntu 20.04; Windows tables: Microsoft C/C++ Optimizing Compiler Version 19 (Visual Studio 2019) on Windows 10; optimization flags not stated |
| **Adoption** | 32.9k stars; ubiquitous Python scientific stack |
| **Last commit** | 2026-10-01 |
| **Links** | [repository](https://github.com/numpy/numpy) · [benchmark](https://raw.githubusercontent.com/numpy/numpy/main/doc/source/reference/random/performance.rst) |

## Verdict

NumPy's own timeit script (min of 3 runs, 1,000,000 values per call) on an AMD Ryzen 9 3900X under Ubuntu 20.04 with GCC 9.3.0 gives uniforms in 3.1 ns (PCG64), 2.9 ns (PCG64DXSM) and 2.6 ns (SFC64) versus 5.9 ns for MT19937 under Generator and 6.0 ns for legacy RandomState, for overall geometric-mean speedups over RandomState of 2.19x, 2.25x and 2.51x. Optimization flags are not stated, the baseline is NumPy's own C MT19937 rather than std::mt19937, and 32-bit Windows reverses the result for the PCG generators.

## Use it when

- Python code still calling np.random.\* or RandomState for bulk draws: switching to default_rng() gives about 2.2x geometric-mean speedup overall (5.3x for normals, 10.7x for exponentials) on the page's 64-bit Linux run.
- Large array draws (the benchmark uses 1,000,000 values per call) of uniforms, ints, normals, exponentials or gammas on 64-bit x86 Linux or Windows.
- Raw speed with no jump-ahead needed: SFC64 is the fastest NumPy bit generator (2.5 ns per uint64, 2.6 ns per uniform versus 5.6/5.9 for MT19937), including on 32-bit builds.
- Many parallel streams: SeedSequence.spawn or BitGenerator.spawn for independent streams; prefer PCG64DXSM over PCG64 when spawning millions of streams.
- C, Cython or Numba code that already ships with NumPy and wants its distribution samplers through the bitgen_t C API instead of writing its own.

## Skip it when

- Plain C++ projects: the measured path is the Python API, and using the C core means linking NumPy's npyrandom and npymath static libraries or copying sources; pcg-cpp or a header-only generator is simpler.
- 32-bit builds: on 32-bit Windows PCG64 scores 25 and PCG64DXSM 39 versus MT19937 at 100 overall; only SFC64 (77) comes close.
- One value at a time in a Python loop: per-call interpreter overhead dominates and the per-value nanosecond figures do not apply.
- Laplace, Poisson or binomial-heavy workloads: gains are small or negative (Laplace 76.1 ns with PCG64DXSM versus 73.2 ns with MT19937 under Generator).
- Security or cryptography: the docs say these generators are not suitable; use secrets.

## How it is fast

The bit generators are cheaper per 64-bit output than MT19937: PCG64 is a 128-bit LCG with an XSL-RR output permutation, PCG64DXSM uses a cheaper 64-bit multiplier on the LCG step plus a stronger xorshift-multiply (DXSM) output, and SFC64 (from PractRand) is a 256-bit add/xor/shift/rotate generator with no multiplications. Native __uint128_t is used where the compiler has it, with _umul128 emulation on MSVC. Much of the larger gain over RandomState comes from the samplers: ziggurat normals and exponentials instead of Box-Muller and log inversion, and Lemire's nearly divisionless method for bounded integers; draws are made in bulk loops in C with the GIL released.

## Compared with alternatives

Pick NumPy's Generator when you are already in the Python/NumPy stack and need many distributions with sound parallel seeding at no integration cost. randomgen (the project this code came from) adds faster bit generators such as Romu and Xoshiro256 with the same interface, and Randompack's paper reports lower per-value times than NumPy (U(0,1) 0.42 versus 1.8 ns); in C++ use pcg-cpp, EigenRand or a SIMD generator instead.

## Integration

| | |
|---|---|
| **Form** | module (Python package with Cython/C extension); C access via the npyrandom static library shipped in numpy/random/lib |
| **Dependencies** | Python and NumPy; the C API also needs npymath |
| **Minimum toolchain** | not documented on the pages read; the C sources require C99 or later (pcg64.h errors on nonstandard GNU inline semantics) |
| **Platforms** | any platform NumPy supports; fast path needs a 64-bit build (native __uint128_t where available, _umul128 emulation on MSVC) |
| **Thread safety** | Each BitGenerator carries a shared RLock that Generator methods take while releasing the GIL, so a shared instance is safe but serialized; the docs recommend one Generator per thread via SeedSequence.spawn (multithreading.rst shows 4 threads cutting a 10M-normal fill from 99.6 ms to 32.8 ms). |
| **Drop-in for the baseline** | partial: Generator mirrors most RandomState method names, but output streams differ and some methods were renamed (for example integers replaces randint), so seeded results are not reproduced |

## Gotchas

- Stream compatibility is only promised for the same seed, method calls, NumPy build and machine; Generator algorithms may change in X.Y releases, and default_rng may switch its default bit generator (PCG64DXSM is slated to replace PCG64).
- PCG64 (XSL-RR) has a known weakness with millions of randomly seeded streams: two streams sharing the low 58 state bits fail PractRand when interleaved (numpy issue #16313); use PCG64DXSM, SFC64 or Philox at that scale.
- SFC64 has no jumped() or advance(); parallel use must go through SeedSequence spawning.
- Calling rng.random() five times is not guaranteed to equal rng.random(5); NumPy reserves the right to use different algorithms for different block sizes.

## Known shortcomings

- Flags missing (GCC 9.3.0 / MSVC 19 on Ryzen 9 3900X; script doc/source/reference/random/performance.py); bulk draws (1e6 per call); the new generators lose on 32-bit Windows and Laplace is slower with PCG64DXSM; Python library, the C core is reachable only via numpy's C API.
- Python-first, not a C++ API. Known PCG64 multi-stream weakness (#16313, addressed by PCG64DXSM). On 32-bit Windows PCG64 is slower than MT19937 (25 vs 100).

## Caveats and trade-offs

First-party docs. The script is public (doc/source/reference/random/performance.py) and the page names GCC 9.3.0 (Linux) and MSVC 19 / VS2019 (Windows) on an AMD Ryzen 9 3900X, but optimization flags are not stated. Values are drawn in bulk (1,000,000 per call), so the per-value times amortize Python call overhead and do not represent one-at-a-time draws. The win depends on the platform: on 32-bit Windows the new generators are slower than MT19937 (overall PCG64 25, PCG64DXSM 39, SFC64 77 versus 100), and Philox scores 28 on 64-bit Windows. Not every distribution improves: Laplaces take 76.1 ns with PCG64DXSM versus 73.2 ns with MT19937 under Generator, and Laplace and Poisson gains are 3-27 percent. Much of the normals and exponentials gap versus RandomState comes from the algorithm (ziggurat versus Box-Muller and log inversion), not from the bit generator. PCG64 is the PCG family already catalogued as pcg-cpp, and SFC64 comes from PractRand, so those rows are partly evidence for the underlying algorithms. The baseline is NumPy's own C MT19937, not std::mt19937.

Python-first API; using the generators from plain C++ means embedding Python/NumPy or copying the C sources. SFC64 lacks jump-ahead (per the same page); PCG64DXSM is recommended for heavily parallel use.

## Maintenance

Actively maintained (32.9k stars, commits on 2026-10-01) and BSD-3-Clause; the Generator API has shipped since NumPy 1.17 and the C sources are small enough to copy if you need the generators without Python.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party docs table against MT19937 and legacy RandomState; the generating script is public (doc/source/reference/random/performance.py, timeit over 1,000,000-value draws) and the page names GCC 9.3.0 / MSVC 19 and an AMD Ryzen 9 3900X, but optimization flags are not stated, so it falls short of A.
- **Verifier notes:** All claimed numbers match the page exactly. The record wrongly said the compiler and the Windows hardware were unstated; the page's closing note gives both. Tier stays C because flags are absent. The entry is a Python package; its C core (npyrandom bitgen_t) is C-callable, but the measured path goes through the Python API.
- **Fields the verifier corrected:** `compiler_and_flags`, `hardware`, `workload`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/numpy/numpy/main/doc/source/reference/random/performance.rst>
  - <https://raw.githubusercontent.com/numpy/numpy/main/doc/source/reference/random/performance.py>
  - <https://raw.githubusercontent.com/numpy/numpy/main/LICENSE.txt>
  - <https://github.com/numpy/numpy>
  - <https://github.com/numpy/numpy/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/numpy/numpy/main/doc/source/reference/random/performance.rst>
  - <https://raw.githubusercontent.com/numpy/numpy/main/doc/source/reference/random/performance.py>
  - <https://raw.githubusercontent.com/numpy/numpy/main/doc/source/reference/random/index.rst>
  - <https://raw.githubusercontent.com/numpy/numpy/main/doc/source/reference/random/bit_generators/index.rst>
  - <https://raw.githubusercontent.com/numpy/numpy/main/doc/source/reference/random/upgrading-pcg64.rst>
  - <https://raw.githubusercontent.com/numpy/numpy/main/doc/source/reference/random/compatibility.rst>
  - <https://raw.githubusercontent.com/numpy/numpy/main/doc/source/reference/random/multithreading.rst>
  - <https://raw.githubusercontent.com/numpy/numpy/main/doc/source/reference/random/c-api.rst>
  - <https://raw.githubusercontent.com/numpy/numpy/main/doc/source/reference/random/extending.rst>
  - <https://raw.githubusercontent.com/numpy/numpy/main/doc/source/reference/random/parallel.rst>
  - <https://raw.githubusercontent.com/numpy/numpy/main/doc/source/reference/thread_safety.rst>
  - <https://raw.githubusercontent.com/numpy/numpy/main/numpy/random/src/pcg64/pcg64.h>
  - <https://raw.githubusercontent.com/numpy/numpy/main/numpy/random/src/sfc64/sfc64.h>
  - <https://raw.githubusercontent.com/numpy/numpy/main/numpy/random/src/distributions/distributions.c>
  - <https://raw.githubusercontent.com/numpy/numpy/main/numpy/random/_sfc64.pyx>
  - <https://raw.githubusercontent.com/numpy/numpy/main/numpy/random/_pcg64.pyx>
  - <https://raw.githubusercontent.com/numpy/numpy/main/numpy/random/bit_generator.pyx>
  - <https://raw.githubusercontent.com/numpy/numpy/main/numpy/random/_generator.pyx>
  - <https://github.com/numpy/numpy>
  - <https://github.com/numpy/numpy/issues?q=is%3Aissue+label%3A%22component%3A+numpy.random%22+performance>
  - <https://github.com/numpy/numpy/issues/16313>
  - <https://github.com/numpy/numpy/issues/13857>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/numpy/numpy`) · [data/wave8/enrich/raw/github_com_numpy_numpy.json](../../../data/wave8/enrich/raw/github_com_numpy_numpy.json) (enrichment confidence 0.85)

</details>
