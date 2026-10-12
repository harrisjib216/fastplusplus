# milo Grisu2 (header-only, via miloyip/dtoa-benchmark)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Number parsing and formatting](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Header-only Grisu2 double-to-string routine; fastest entry in its author's own benchmark, beating std::ostringstream and sprintf().

| | |
|---|---|
| **Beats** | std::ostringstream (iostreams); page's headline ratio is vs sprintf() |
| **Claimed result** | 9.10x faster than sprintf() (verbatim, page's own Speedup column: milo 138.021ns vs sprintf 1256.376ns) -- the fastest contender in this shootout, beating google/double-conversion (6.23x) and fpconv (4.59x); \~20.1x faster than std::ostringstream (derived from page data: 138.021ns vs 2,778.748ns) |
| **Workload** | RandomDigit case: convert 1,000 random doubles (1-17 significant decimal digits) to shortest round-trippable ASCII string, min of 10 trials x100 iterations each. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7 920 @ 2.67GHz |
| **Compiler and flags** | Visual C++ 2013, Win64; release config via premake4 flags {"Optimize"} + NDEBUG (build/premake4.lua); literal compiler flags not stated |
| **Adoption** | 258 stars (benchmark repo hosting the implementation, at src/milo/) |
| **Last commit** | 2020-04-27 |
| **Links** | [repository](https://github.com/miloyip/dtoa-benchmark) · [benchmark](https://github.com/miloyip/dtoa-benchmark) |

## Verdict

On the benchmark's own RandomDigit case (1,000 random doubles with 1-17 significant decimal digits, minimum of 10 trials x 100 iterations each), milo averaged 138.021 ns/conversion versus sprintf's 1256.376 ns (9.10x, the page's own figure) and versus std::ostringstream's 2,778.748 ns (\~20.1x, derived from the same table), measured on an Intel Core i7 920 @ 2.67GHz with Visual C++ 2013, Windows 64-bit, release config.

## Use it when

- Hot double-to-ASCII serialization paths (e.g. JSON/log writers) on x86/x86-64 where you control the toolchain (MSVC or GCC/Clang) and can vendor a single header.
- You've already excluded NaN/Inf upstream and can size and validate the output buffer yourself.
- You want the fastest Grisu-family converter shown in this specific benchmark and are willing to re-benchmark it against double-conversion/fpconv on your own hardware and compiler rather than trust the 2013-era, i7-920/VC2013 numbers.
- 'Almost always shortest' output (not the guaranteed-shortest of Grisu3+bignum) is acceptable for your format.

## Skip it when

- You need a std::to_chars-compatible signature (pointer-pair/span, error code, format flags) — this is a raw C-style buffer writer, not drop-in.
- You need guaranteed-correct NaN/Inf handling — the code only asserts !isnan/!isinf, which is compiled out under NDEBUG (undefined behavior in release).
- Your value distribution can hit the known unresolved out-of-bounds read in DigitGen (e.g. 0.020000000000000005, kappa = -14) — GitHub issue #7, filed 2016, still open as of 2026-09-24, caught by Clang ASan, no fix landed in this repo.
- You need an actively maintained dependency — repo has had no default-branch commits since 2020-04-27, and issue #18 explicitly asks the maintainer to transfer ownership because he isn't accepting pull requests.
- Target is a non-x86 platform — the fast paths use MSVC's _umul128/_BitScanReverse64 or GCC/Clang's __int128/__builtin_clzll on x86-64; other architectures fall back to an untested, unbenchmarked portable path.

## How it is fast

Implements Loitsch's Grisu2 algorithm: converts the double into a DiyFp (64-bit significand plus binary exponent), then generates digits using only fixed-width integer/bit arithmetic against a precomputed table of cached powers of ten (GetCachedPower), avoiding the arbitrary-precision bignum fallback that fully-correct converters like Grisu3-based double-conversion sometimes need. A 200-byte two-digit lookup table (GetDigitsLut) speeds up decimal digit and exponent formatting in WriteExponent/Prettify. Being Grisu2 rather than Grisu3, it can occasionally emit a decimal one digit longer than the true shortest representation in exchange for never invoking the slow bignum path.

## Compared with alternatives

Against fpconv (also Grisu2, 4.59x vs sprintf) and google/double-conversion (Grisu3+bignum fallback, 6.23x, always-shortest), milo is the fastest of the three on this same benchmark/hardware (9.10x vs sprintf) but carries the same Grisu2 not-always-shortest caveat as fpconv plus an unresolved OOB read that neither sibling has documented against it; pick milo only after your own benchmark confirms the throughput edge and you can tolerate or patch the DigitGen edge case, otherwise prefer double-conversion (more correctness testing, used in V8) or Boost.Charconv/c4core (independently benchmarked, actively maintained, std::to_chars-compatible APIs).

## Integration

| | |
|---|---|
| **Form** | header-only (source-drop from a benchmark repo; not distributed as a standalone package — must be extracted from src/milo/dtoa_milo.h) |
| **Dependencies** | none beyond the C/C++ standard library (assert.h, math.h, stdint.h); on MSVC it also pulls in a bundled msinttypes/stdint.h shim and &lt;intrin.h&gt; |
| **Minimum toolchain** | not documented; the source itself only requires C++03-level syntax plus compiler intrinsics/extensions (MSVC any version with _umul128/_BitScanReverse64; GCC &gt;=4.6 or Clang for __int128 on x86-64); portable fallback compiles with any C++ compiler |
| **Platforms** | x86-64 optimized via MSVC or GCC/Clang intrinsics; portable C++ fallback for other compilers/architectures exists in source but is not covered by the published benchmark numbers |
| **Thread safety** | not documented; implementation holds no mutable global state (only function-local static const lookup tables) and writes only to the caller-provided buffer, so concurrent calls with distinct buffers appear safe, but this is not asserted by the author |
| **Drop-in for the baseline** | partial — different signature (raw buffer write, no error code, no precision/format control, no NaN/Inf handling) than std::ostringstream or std::to_chars; needs a wrapper to substitute at call sites |

## Gotchas

- Open, unresolved bug (issue #7, filed 2016): certain values, e.g. 0.020000000000000005, cause an out-of-bounds read on the internal kPow10 table inside DigitGen (kappa = -14), caught by Clang AddressSanitizer.
- assert(!isnan(value)); assert(!isinf(value)) — with NDEBUG (release builds) these are no-ops, so NaN/Inf input is undefined behavior rather than a checked error.
- No buffer-size parameter or internal bound check; caller must supply a sufficiently large buffer with no guidance from the header on how large that needs to be.
- Issue #20 (wrong result for 16385.0, a rounding-direction bug in the cached-power exponent calculation) was fixed by the maintainer, closed on the same date as the repo's last commit (2020-04-27) — confirms the currently-read source no longer has that specific bug, but shows fixes were rare and reactive.

## Caveats and trade-offs

First-party numbers: milo Grisu2 is Milo Yip's own implementation, measured in his own benchmark repo. It is the fastest non-null entry in this shootout. The repo has had no default-branch commits since 2020-04-27 (abandoned). Hardware is 2009-era (Core i7 920) and the compiler is VC++2013, with literal flags not stated. The sprintf ratio is the page's own; the ostringstream ratio is derived from page data.

Not packaged as a standalone library -- lives inside the benchmark harness at src/milo/\*.h and would need to be extracted to vendor into a project; header-only Grisu2 C++ implementation by the benchmark author (miloyip); same Grisu2 not-always-shortest caveat as fpconv.

## Maintenance

Abandoned: no default-branch commits since 2020-04-27, and an open issue (#18) asks the maintainer to transfer ownership since he no longer accepts pull requests; MIT-licensed and small enough to vendor as a single header, but ships with at least one known, unresolved memory-safety bug (issue #7) that has sat open since 2016.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification B, tier now C.
- **Tier reason:** The milo row (138.021 ns, 9.10x vs sprintf; ostringstream 2,778.748 ns, so the derived \~20.1x is correct) is on the README, but the cataloged project is the benchmark repo itself, and milo's Grisu2 is the benchmark author's own implementation, so these are first-party numbers. Code (src/milo/), compiler (VC2013) and CPU (i7 920) are public or stated, but literal flags are not (premake flags {"Optimize"} only), so not A. First-party with partial methodology is C.
- **Verifier notes:** Metadata checks out: MIT, 258 stars, last commit 2020-04-27 (abandoned), not a fork, not archived. Downgraded from B to C only because this benchmark is the project's own, not an independent third-party suite.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/miloyip/dtoa-benchmark>
  - <https://github.com/miloyip/dtoa-benchmark/blob/master/build/premake4.lua>
- **Sources the enricher read:**
  - <https://github.com/miloyip/dtoa-benchmark>
  - <https://github.com/miloyip/dtoa-benchmark/blob/master/readme.md>
  - <https://github.com/miloyip/dtoa-benchmark/blob/master/src/milo/dtoa_milo.h>
  - <https://github.com/miloyip/dtoa-benchmark/blob/master/license.txt>
  - <https://github.com/miloyip/dtoa-benchmark/blob/master/src/milotest.cpp>
  - <https://github.com/miloyip/dtoa-benchmark/blob/master/src/test.h>
  - <https://github.com/miloyip/dtoa-benchmark/blob/master/src/main.cpp>
  - <https://github.com/miloyip/dtoa-benchmark/issues/7>
  - <https://github.com/miloyip/dtoa-benchmark/issues/20>
  - <https://github.com/miloyip/dtoa-benchmark/issues>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/miloyip/dtoa-benchmark`) · [data/wave1/enrich/raw/github_com_miloyip_dtoa_benchmark.json](../../../data/wave1/enrich/raw/github_com_miloyip_dtoa_benchmark.json) (enrichment confidence 0.55)

</details>
