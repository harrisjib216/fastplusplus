# randomgen (NumPy-compatible bit generators: SFC64, Romu, Xoshiro256, PCG64, SFMT)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Random and quasi-random numbers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C (Cython/Python wrapper)` · `BSD-3-Clause OR NCSA` · 🟢 active

> Python/C package of extra NumPy bit generators (Romu, SFC64, Xoshiro256, counter-based); about 2.3-2.8x faster overall than legacy RandomState.

| | |
|---|---|
| **Beats** | MT19937 as used by NumPy's legacy RandomState (also compared against MT19937, MT64, DSFMT inside randomgen) |
| **Claimed result** | uint64: Romu 2.6 ns, SFC64 2.6, Xoshiro256 2.8, SFMT 2.8, PCG64 3.2 versus MT19937 4.2 ns and NumPy RandomState 5.2 ns; uniform double: Romu 2.4, SFC64 2.5, Xoshiro256 2.7, PCG64 2.9 versus MT19937 4.0 and RandomState 5.2. The page's own overall geometric-mean score relative to RandomState: Romu(trio) 276%, Romu 268%, SFC64 259%, Xoshiro256 243%, SFMT 242%, PCG64 227%, MT19937 (via Generator) 191%. |
| **Workload** | Time in ns per random value (uint32, uint64, uniform double, exponential, normal, gamma) from each bit generator through numpy.random.Generator versus NumPy's legacy RandomState, measured by doc/source/performance.py with timeit (each call draws 25,000 values, 100 calls, min of 10 repeats), on Linux with an Intel Cascade Lake CPU (Family 6, Model 85, Stepping 7) at 3.1GHz. |
| **Metric** | throughput |
| **Hardware** | Intel Cascade Lake (Family 6, Model 85, Stepping 7) at 3.1GHz, Linux |
| **Adoption** | 127 stars |
| **Last commit** | 2026-09-28 |
| **Links** | [repository](https://github.com/bashtage/randomgen) · [benchmark](https://raw.githubusercontent.com/bashtage/randomgen/main/doc/source/performance.rst) |

## Verdict

The project's doc script times numpy.random.Generator draws of 25,000 values per call (min of 10 repeats of 100 calls) on an Intel Cascade Lake at 3.1 GHz under Linux, compiler and flags unstated: uniform doubles take 2.4 ns (Romu trio), 2.5 (SFC64) and 2.9 (PCG64) versus 4.0 ns for MT19937 and 5.2 ns for NumPy's legacy RandomState, and the geometric mean across six distributions is 2.3-2.8x RandomState for the listed fast generators.

## Use it when

- Python/NumPy simulations that still use RandomState or MT19937 and draw arrays of thousands of values, where a faster bit generator under numpy.random.Generator is a one-line change
- You need a generator NumPy does not ship (Romu, Xoshiro256/512, JSF, LXM, SFMT, Squares, Tyche, EFIIX64, AESCounter, ChaCha, SPECK128, HC128), for example to reproduce a C/C++ simulation's stream from Python
- Thousands of parallel streams: SFC64 with distinct Weyl increments (weyl_increments(n)), keyed counter-based generators, or PCG64DXSM with SeedSequence.spawn, as the performance page recommends
- C/C++ developers who want tested C sources for many generators with Python bindings for cross-checking output

## Skip it when

- Pure C++ projects: this is a Python extension, and lifting a generator from randomgen/src means also taking common/randomgen_config.h and honoring that component's own license
- When NumPy's built-in PCG64 or SFC64 is enough: in the same table Romu(trio) draws uniforms in 2.4 ns versus 2.5 ns for SFC64 and 2.9 ns for PCG64 (about 1.2x at best, derived from page data), a small gain for an extra dependency
- Environments on NumPy 2.4 with the latest release (2.3.0): import fails (open issue #426)
- Scalar one-at-a-time draws from Python: the timings amortize 25,000 values per call, so per-call overhead dominates single draws
- Mersenne Twister variants (MT19937, MT64, SFMT, DSFMT) or RDRAND (about 880 ns per value): the docs advise against the MT family unless backward compatibility is needed

## How it is fast

Each generator is a small C state machine (randomgen/src/&lt;gen&gt;/) exposed through NumPy's bitgen function pointers (next_uint64, next_uint32, next_double), so Generator fills whole arrays in C. The fast cores are cheap per step: RomuTrio/RomuQuad are rotate-multiply generators with 3-4 words of state, SFC64 is add/xor/shift/rotate plus a Weyl counter with no multiply, Xoshiro256 (xoshiro256\*\*) updates four words with xor/shift/rotate and scrambles with two multiplies, whereas MT19937 regenerates a 624-word state block and, per the docs, needs two 32-bit outputs per 64-bit value. 32-bit draws use the cached upper half of a 64-bit output. Most of the normal and exponential gap against RandomState comes from NumPy Generator's ziggurat samplers versus the legacy methods, not from the bit generator.

## Compared with alternatives

Against the NumPy Generator entry, pick randomgen only for generators NumPy lacks (Romu, Xoshiro, JSF, AES, ChaCha, Squares, Tyche) or for SFC64's configurable Weyl increment; NumPy's own PCG64/SFC64 give nearly the same speed. For C or C++ code, Randompack (a C library) or EigenRand are the better catalogued choices, and dqrng fills the same role in R.

## Integration

| | |
|---|---|
| **Form** | module (Python/Cython package on PyPI and conda-forge; the per-generator C files under randomgen/src can be used as a source-drop) |
| **Dependencies** | NumPy &gt;=1.22.3 at runtime; building needs NumPy &gt;=2.0, Cython &gt;=3.0.10 and meson-python (meson &gt;=1.9) |
| **Minimum toolchain** | Python 3.9-3.13 per README (pyproject says &gt;=3.8); C99 compiler (GCC, Clang or MSVC) |
| **Platforms** | PyPI 2.3.0 wheels for Linux x86-64 and aarch64 (manylinux), musllinux x86-64, macOS x86-64 and arm64, Windows x86-64; README also lists FreeBSD and Linux ARM CI. RDRAND is x86-only and AESCounter is fast only with AES-NI |
| **Thread safety** | Bit generator objects carry a Python lock (self.lock, taken in the Cython sources); the C state structs are unsynchronized, so use one bit generator per thread or stream |
| **Drop-in for the baseline** | partial — Generator(SFC64(seed)) replaces RandomState or default_rng() with one line, but the stream differs from MT19937, randomgen's own RandomState was removed in 1.23, and legacy method names (randint, random_sample) become Generator's integers and random |

## Gotchas

- randomgen 2.3.0 (the latest PyPI release, 2025-10-22) fails to import with NumPy 2.4 because numpy.random.bit_generator.SeedlessSequence was removed (issue #426, open since 2025-12-22); main's common.pyx no longer references it, but no newer release was on PyPI as of 2026-10-01
- randomgen/meson.build adds -msse2 -mssse3 -maes -mrdrnd -mavx2 to every extension on GCC/Clang, so x86-64 builds appear to assume AVX2 and AES-NI CPUs (inferred from the build file; not stated in the docs)
- Component licenses differ from the package's BSD-3-Clause/NCSA: the Romu sources are Apache-2.0 and the SFC64 header is MIT (per file headers), which matters when lifting C code
- Past correctness fixes worth knowing if you pinned an old version: a non-deterministic Xoshiro256 jump (#336) and a wrong xoroshiro128 jump (#321), both closed 2023, and LCG128Mix ignoring its default inc (fixed in 2.1.0)

## Known shortcomings

- On gammas MT19937 beats PCG64, PCG64DXSM and Xoshiro256; overlaps NumPy (NumPy's Generator was derived from it); dual-licensed BSD-3-Clause OR NCSA; Python package.
- Latest PyPI release 2.3.0 fails to import with NumPy 2.4 (#426 open; fix on main, unreleased). randomgen/meson.build adds -mavx2 -maes -mrdrnd to every extension, so x86 builds appear to assume AVX2 CPUs (inferred from the build file). Gain over NumPy's own PCG64/SFC64 is at most \~1.2x. Python package; Romu C sources are Apache-2.0.

## Caveats and trade-offs

First-party documentation table. The script is public (doc/source/performance.py; also a top-level benchmark.py), and the CPU family is stated without a model name, but compiler and flags are not stated. Values are drawn in bulk (25,000 per call), so Python call overhead is amortized and the numbers do not represent one-at-a-time draws. On gammas, MT19937 under Generator (20.8 ns) beats PCG64 (23.2), PCG64DXSM (23.8), Xoshiro256 (22.1) and SFMT (21.5); only Romu variants and SFC64 (20.6) are faster there. The RandomState gap on normals and exponentials is inflated by Box-Muller and log-based inversion versus ziggurat in the newer code. The page itself recommends against all Mersenne Twister variants unless backward compatibility is needed. The baseline is NumPy's C MT19937, not std::mt19937. Dual-licensed NCSA or BSD-3-Clause; component licenses are stored with each component's source.

Python/Cython package that needs NumPy; the C generator sources live in the repo and can be lifted into C/C++ projects, but the package itself is not a C++ library. SFC64 lacks jump-ahead (per the NumPy docs), so parallel streams rely on distinct seeds or Weyl increments; Philox, AES and other counter-based generators are available when many streams are needed.

## Maintenance

Actively maintained (commits through 2026-09-28, mostly dependency bumps; last release 2.3.0 on 2025-10-22), dual BSD-3-Clause/NCSA with per-component licenses, and marked Production/Stable on PyPI.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party docs table against NumPy RandomState and MT19937; the generating script is public (doc/source/performance.py, plus top-level benchmark.py) and the CPU family is stated (Cascade Lake, Family 6 Model 85 Stepping 7, 3.1GHz), but no compiler or flags, so C.
- **Verifier notes:** All claimed numbers match the page. The record's statement that no benchmark script exists was wrong (doc/source/performance.py generates the table). LICENSE.md says dual-licensed NCSA and BSD-3-Clause, so the SPDX expression is OR, not AND. NumPy's Generator API was derived from randomgen, so this overlaps the NumPy entry; it is a separate project with extra generators (Romu, Xoshiro, SFMT, and others).
- **Fields the verifier corrected:** `license`, `workload`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/bashtage/randomgen/main/doc/source/performance.rst>
  - <https://raw.githubusercontent.com/bashtage/randomgen/main/doc/source/performance.py>
  - <https://raw.githubusercontent.com/bashtage/randomgen/main/benchmark.py>
  - <https://raw.githubusercontent.com/bashtage/randomgen/main/LICENSE.md>
  - <https://github.com/bashtage/randomgen>
  - <https://github.com/bashtage/randomgen/commits>
- **Sources the enricher read:**
  - <https://github.com/bashtage/randomgen>
  - <https://github.com/bashtage/randomgen/commits/main>
  - <https://github.com/bashtage/randomgen/tree/main/randomgen/src>
  - <https://github.com/bashtage/randomgen/issues?q=is%3Aissue>
  - <https://github.com/bashtage/randomgen/issues?q=is%3Aissue+illegal+instruction>
  - <https://github.com/bashtage/randomgen/issues/426>
  - <https://github.com/bashtage/randomgen/issues/389>
  - <https://raw.githubusercontent.com/bashtage/randomgen/main/README.md>
  - <https://raw.githubusercontent.com/bashtage/randomgen/main/doc/source/performance.rst>
  - <https://raw.githubusercontent.com/bashtage/randomgen/main/doc/source/performance.py>
  - <https://raw.githubusercontent.com/bashtage/randomgen/main/benchmark.py>
  - <https://raw.githubusercontent.com/bashtage/randomgen/main/LICENSE.md>
  - <https://raw.githubusercontent.com/bashtage/randomgen/main/pyproject.toml>
  - <https://raw.githubusercontent.com/bashtage/randomgen/main/requirements.txt>
  - <https://raw.githubusercontent.com/bashtage/randomgen/main/meson.build>
  - <https://raw.githubusercontent.com/bashtage/randomgen/main/randomgen/meson.build>
  - <https://raw.githubusercontent.com/bashtage/randomgen/main/doc/source/change-log.rst>
  - <https://raw.githubusercontent.com/bashtage/randomgen/main/doc/source/index.rst>
  - <https://raw.githubusercontent.com/bashtage/randomgen/main/randomgen/src/sfc/sfc.h>
  - <https://raw.githubusercontent.com/bashtage/randomgen/main/randomgen/src/romu/romu.h>
  - <https://raw.githubusercontent.com/bashtage/randomgen/main/randomgen/src/xoshiro256/xoshiro256.h>
  - <https://raw.githubusercontent.com/bashtage/randomgen/main/randomgen/src/sfmt/sfmt.h>
  - <https://raw.githubusercontent.com/bashtage/randomgen/main/randomgen/sfc.pyx>
  - <https://raw.githubusercontent.com/bashtage/randomgen/main/randomgen/romu.pyx>
  - <https://raw.githubusercontent.com/bashtage/randomgen/main/randomgen/xoshiro256.pyx>
  - <https://raw.githubusercontent.com/bashtage/randomgen/main/randomgen/sfmt.pyx>
  - <https://raw.githubusercontent.com/bashtage/randomgen/main/randomgen/common.pxd>
  - <https://raw.githubusercontent.com/bashtage/randomgen/main/randomgen/common.pyx>
  - <https://pypi.org/pypi/randomgen/json>
  - <https://raw.githubusercontent.com/bashtage/randomgen/main/randomgen/src/mt19937/mt19937.h>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/bashtage/randomgen`) · [data/wave8/enrich/raw/github_com_bashtage_randomgen.json](../../../data/wave8/enrich/raw/github_com_bashtage_randomgen.json) (enrichment confidence 0.8)

</details>
