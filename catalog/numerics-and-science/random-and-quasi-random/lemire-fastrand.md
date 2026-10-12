# fastrand (PCG32 and xorshift128+ with nearly-divisionless bounded integers for Python)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Random and quasi-random numbers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C (CPython extension)` · `Apache-2.0` · 🟢 active

> Tiny CPython C extension: PCG32/xorshift128+ bounded integers about 9x faster per call than random.randint.

| | |
|---|---|
| **Beats** | CPython random.randint (Mersenne Twister) |
| **Claimed result** | fastrand.pcg32bounded(1001) 23.6 ns and fastrand.pcg32randint(100,1000) 24.6 ns versus random.randint(0,1000) 216 ns (about 9.2x and 8.8x, derived from page data) and numpy.random.randint(0,1000) 955 ns (about 40x, derived). README headline: 'up to 10x faster than random.randint'. |
| **Workload** | python3 -m timeit of a single bounded integer draw in [0,1001) or [100,1000] with fastrand versus random.randint(0,1000) and numpy.random.randint(0,1000). |
| **Metric** | latency |
| **Adoption** | 124 stars; on PyPI as fastrand |
| **Last commit** | 2026-05-15 |
| **Links** | [repository](https://github.com/lemire/fastrand) · [benchmark](https://raw.githubusercontent.com/lemire/fastrand/HEAD/README.md) |

## Verdict

The README's python3 -m timeit lines (also in scripts/runtests3.sh) show pcg32bounded(1001) at 23.6 ns and pcg32randint(100,1000) at 24.6 ns per call, against random.randint(0,1000) at 216 ns (about 9x, derived from page data) and legacy numpy.random.randint(0,1000) at 955 ns. No CPU, Python version, compiler or flags are given, and the comparison is per call to CPython's Mersenne Twister path, not against std::mt19937.

## Use it when

- Pure-Python loops that draw one bounded integer at a time (simulations, randomized algorithms, sampling indices), where random.randint's \~200 ns per call dominates.
- Ranges that fit in 32 bits with a non-negative lower bound (pcg32bounded / pcg32randint), or unsigned 64-bit ranges via xorshift128plusbounded on Linux/macOS 64-bit builds.
- When you want a fixed, reproducible stream that you seed explicitly, and the global-state API is acceptable.
- As a reference for porting the PCG32 + nearly-divisionless bounded-integer code into C or C++: the core is about 30 lines.

## Skip it when

- Bulk generation of arrays: numpy's Generator (PCG64/SFC64) is vectorized and much cheaper per value; the README's numpy comparison times the legacy per-call numpy.random.randint, not batched draws.
- Negative lower bounds or results above 2\*\*32-1 with pcg32randint: the result n1 + r is returned through Py_BuildValue("I"), an unsigned 32-bit format, so it should wrap or truncate (code reading, not executed). xorshift128plusrandint accepts only unsigned bounds.
- Anything security-related (tokens, keys, shuffling for gambling): PCG32 and xorshift128+ are not cryptographic; use the secrets module.
- Code that needs independent per-object or per-thread generators, getstate/setstate, or the random module's distributions and sequence helpers.
- Arbitrary-size integers: bounds must fit in a C long (issue #21 shows OverflowError for a 256-bit bound where random.randint succeeds).

## How it is fast

Each call is one METH_O or METH_FASTCALL C function, so it skips the several Python-level frames that random.randint goes through (randint -&gt; randrange -&gt; _randbelow). The generator is PCG32 (XSH-RR: one 64-bit multiply-add plus a xorshift and rotate), and the bounded draw uses Lemire's nearly-divisionless multiply-shift method (TOMACS 2019), which needs a modulo only on the rare rejection path. Most of the README's 9x gap is interpreter call overhead rather than generator speed.

## Compared with alternatives

Pick it over numpy's Generator or randomgen when you need single scalar draws inside Python code rather than arrays. If you are in C++, take the same nearly-divisionless method from FastShuffleExperiments, or use simdpcg when you need PCG32 throughput, instead of going through this Python wrapper.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none (CPython C API only; build needs setuptools&gt;=77 and a C compiler, or a prebuilt wheel) |
| **Minimum toolchain** | Python 3.9+ (pyproject requires-python); randint functions need 3.7+ METH_FASTCALL; wheels for CPython 3.9-3.14 and 3.14t |
| **Platforms** | Wheels for Linux x86-64/aarch64 (glibc and musl), macOS x86-64/arm64/universal2, Windows AMD64. xorshift128+ bounded/randint functions exist only where __int128 is available on a 64-bit target (fastrand.SIXTYFOUR == 1); issue #26 reports a 32-bit Linux build failure. |
| **Thread safety** | Not documented. Generator state is plain C globals with no locking, so it relies on the GIL; all threads share one stream. Free-threaded (cp314t) wheels are published without any visible locking in the source. |
| **Drop-in for the baseline** | partial — pcg32randint(a,b) mirrors random.randint(a,b) for 0 &lt;= a &lt;= b &lt; 2\*\*32, but it is a separate module-level API with no Random class, no shuffle/choice/sample, and different seeding. |

## Gotchas

- Fixed default seed: both generators start from hard-coded constants and the module never seeds from OS entropy, so every new process produces the same sequence until you call pcg32_seed (and pcg32inc for distinct streams). Forked workers share the same state.
- Error paths set ValueError and then return None, which CPython reports as SystemError (returned a result with an exception set); a non-integer or out-of-range argument does not raise a clean ValueError.
- pcg32_uniform has only 32 bits of resolution (r \* 2\*\*-32); xorshift128plus_uniform uses the low 53 bits of xorshift128+, whose lowest bits are its weakest.
- Seeding xorshift128+ with both state words zero leaves it stuck at zero; there is no check. The repo has no unit tests: CI only builds wheels and scripts/runtests3.sh runs the timeit lines.

## Known shortcomings

- Bug (code read, not run): pcg32randint with a negative lower bound wraps via Py_BuildValue("I"), and error paths raise SystemError instead of ValueError; Python extension.
- pcg32randint returns n1+r via Py_BuildValue("I"), so negative or &gt;2\*\*32 results wrap (code reading); error paths set ValueError then return None (SystemError). Fixed hard-coded default seed, never seeded from OS entropy, so every process gets the same stream. No tests in CI. README numbers give no CPU or Python version and the numpy baseline is per-call legacy randint. Issue #21: OverflowError on big ints. Python extension, not a C++ API.

## Caveats and trade-offs

One-line timeit measurements with no CPU, Python version or compiler stated. The gap is dominated by random.randint's Python-level call overhead and its slower bounded-integer path rather than by raw generator speed. The baseline is CPython, not std::mt19937. Checked in fastrandmodule.c: PCG32 (XSH-RR) and Lemire's nearly-divisionless bounded method are implemented correctly. Correctness issues seen by code reading (not executed): pcg32randint takes signed long bounds but returns n1 + value through Py_BuildValue("I"), an unsigned 32-bit format, so ranges with a negative lower bound (e.g. pcg32randint(-10, 10)) should come back wrapped to values near 2\*\*32 instead of negatives. The error paths set ValueError and then return None, which CPython 3 turns into a SystemError.

Python extension with module-level generator state; pcg32 gives 32-bit output only and xorshift128+ is available only on some 64-bit platforms; not cryptographically secure; the C core (PCG32 plus Lemire's multiply-shift bounded draw) is small enough to reuse in C/C++.

## Maintenance

Active: version 3.1.0 was released on 2026-05-15 with wheels for CPython 3.9-3.14. Apache-2.0, and the C core is small enough to copy, but the Python wrapper has the bound and error-handling bugs noted above.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README shows python3 -m timeit lines: fastrand.pcg32bounded(1001) 23.6 ns and pcg32randint(100,1000) 24.6 ns against random.randint(0,1000) 216 ns and numpy.random.randint 955 ns. No CPU, Python version, compiler or flags are given, so these are first-party numbers without methodology. The peer-reviewed TOMACS 2019 paper it cites covers the bounded-integer algorithm in C, not this extension against CPython.
- **Verifier notes:** Numbers match the README. The 2016 blog post linked from the README is on lemire.me, which is egress-blocked here. Metadata confirmed: Apache-2.0, 124 stars, last commit 2026-05-15 ('version 3.1.0').
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/lemire/fastrand/HEAD/README.md>
  - <https://raw.githubusercontent.com/lemire/fastrand/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/lemire/fastrand/HEAD/fastrandmodule.c>
  - <https://github.com/lemire/fastrand>
  - <https://github.com/lemire/fastrand/commits/master>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/lemire/fastrand/HEAD/README.md>
  - <https://raw.githubusercontent.com/lemire/fastrand/HEAD/fastrandmodule.c>
  - <https://raw.githubusercontent.com/lemire/fastrand/HEAD/pyproject.toml>
  - <https://raw.githubusercontent.com/lemire/fastrand/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/lemire/fastrand/HEAD/scripts/runtests3.sh>
  - <https://raw.githubusercontent.com/lemire/fastrand/HEAD/.github/workflows/buildwheels.yml>
  - <https://github.com/lemire/fastrand>
  - <https://github.com/lemire/fastrand/commits/master>
  - <https://github.com/lemire/fastrand/tree/master/scripts>
  - <https://github.com/lemire/fastrand/tree/master/.github/workflows>
  - <https://github.com/lemire/fastrand/issues?q=is%3Aissue>
  - <https://github.com/lemire/fastrand/issues/13>
  - <https://github.com/lemire/fastrand/issues/21>
  - <https://github.com/lemire/fastrand/issues/26>
  - <https://pypi.org/pypi/fastrand/json>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/lemire/fastrand`) · [data/wave8/enrich/raw/github_com_lemire_fastrand.json](../../../data/wave8/enrich/raw/github_com_lemire_fastrand.json) (enrichment confidence 0.8)

</details>
