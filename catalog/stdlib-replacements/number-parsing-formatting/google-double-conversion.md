# google/double-conversion

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Number parsing and formatting](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> Grisu3-based double&lt;-&gt;string library extracted from V8; beats sprintf/ostringstream, covers both to_chars- and from_chars-like directions.

| | |
|---|---|
| **Beats** | std::ostringstream (iostreams); page's headline ratio is vs sprintf() |
| **Claimed result** | 6.23x faster than sprintf() (verbatim, page's own Speedup column: doubleconv 201.645ns vs sprintf 1256.376ns); \~13.8x faster than std::ostringstream (derived from page data: 201.645ns vs 2,778.748ns) |
| **Workload** | RandomDigit case: convert 1,000 random doubles (1-17 significant decimal digits) to shortest round-trippable ASCII string, min of 10 trials x100 iterations each. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7 920 @ 2.67GHz |
| **Compiler and flags** | Visual C++ 2013, Win64; release config via premake4 flags {"Optimize"} + NDEBUG (build/premake4.lua); literal compiler flags not stated |
| **Adoption** | 1,194 stars; used in V8, Chromium, RapidJSON and many other JSON/serialization libraries |
| **Last commit** | 2026-09-13 |
| **Links** | [repository](https://github.com/google/double-conversion) · [benchmark](https://github.com/miloyip/dtoa-benchmark) |

## Verdict

On the independent miloyip/dtoa-benchmark RandomDigit workload (1,000 random doubles, 1-17 significant digits, shortest round-trippable ASCII, min of 10x100 trials), double-conversion's EcmaScriptConverter().ToShortest() averaged 201.645ns vs sprintf's 1256.376ns (6.23x) and std::ostringstream's 2,778.748ns (\~13.8x, derived), on an Intel Core i7 920 @2.67GHz built with VC++2013 Win64 release config (only premake's {"Optimize"} flag is itemized, no literal compiler flags).

## Use it when

- JSON/serialization code needing shortest round-trippable double&lt;-&gt;string conversion at high throughput (already used inside V8, Chromium, RapidJSON)
- Hot paths currently bottlenecked on sprintf/ostringstream for float formatting
- Need both formatting and parsing directions from one small dependency instead of stitching together separate libraries
- Targeting older/pre-C++11 toolchains (utils.h ships fallback macros for pre-C++11 compilation)
- Cross-platform desktop/server build via scons/cmake/bazel; willing to link a small library rather than stay header-only

## Skip it when

- Need an actual drop-in for std::to_chars/std::from_chars call sites — API shape is a converter class with explicit buffers/flags, not a function-call replacement
- Code relies on ToPrecision(): it can fall onto the slow bignum-fallback path for many inputs and become slower than sprintf (open issue #83, unresolved as of this research)
- Inputs frequently have decimal expansions of the form N\*10^M — same Grisu3-fails/bignum-fallback slow path (open issue #28, open since 2016, still open)
- Need header-only, zero-build-step integration — this requires its own static/shared library build step (scons/cmake/bazel)
- Parsing throughput is the priority — open issue #153 reports StringToDouble is slower than other dtoa-style parsers on some inputs; a parsing specialist may win there

## How it is fast

Formatting uses the Grisu3 algorithm (fast-dtoa.cc): 64-bit fixed-precision 'DiyFp' arithmetic plus precomputed cached powers of ten (cached-powers.cc) generate the shortest round-trippable decimal directly, skipping printf format-string parsing and avoiding arbitrary-precision math for the common case. When Grisu3 can't resolve a value unambiguously it falls back to an exact bignum algorithm (bignum-dtoa.cc). Parsing (strtod.cc) mirrors this: a DiyFp fast path handles typical inputs and only escalates to bignum arithmetic for correctly-rounded edge cases.

## Compared with alternatives

Pick this over milo Grisu2 (miloyip/dtoa-benchmark) when you want the battle-tested, actively maintained, V8-derived implementation with real production adoption (V8, Chromium, RapidJSON) rather than a single-header benchmark contender that happens to be faster in that one shootout. Pick c4core or fast_double_parser instead when raw throughput matters more than provenance: c4core's own README claims 40%-2x faster than std::to_chars, and fast_double_parser is a parsing-only specialist that issue #153 suggests may beat double-conversion's StringToDouble.

## Integration

| | |
|---|---|
| **Form** | static lib \| shared lib (also viable as a source-drop: 8 .cc files, no header-only mode) |
| **Dependencies** | none (Bazel BUILD links -lm) |
| **Minimum toolchain** | no CMAKE_CXX_STANDARD is pinned; utils.h carries pre-C++11 fallback macros, so the code itself targets C++03+; CMake path requires CMake 3.29+, scons/bazel builds don't |
| **Platforms** | x86-64, arm64 (issue #6 confirms arm64 support), and other GCC/Clang/MSVC targets; no SIMD/ISA requirement |
| **Thread safety** | not documented explicitly; DoubleToStringConverter/StringToDoubleConverter hold only constructor-set config and write into caller-supplied buffers, so concurrent calls against one shared const converter instance look safe by design, but this is not asserted anywhere in the docs |
| **Drop-in for the baseline** | partial — explain: functionally covers what std::to_chars/std::from_chars and sprintf/ostringstream do, but requires rewriting call sites to the converter-class API with explicit output buffers/StringBuilder |

## Gotchas

- ToShortest() needs a buffer sized to at least kBase10MaximalLength+1 (or kMaxCharsEcmaScriptShortest=25 for the EcmaScript preset) or the call can fail; buffer sizing is the caller's responsibility
- ToPrecision() can silently take the slow bignum-fallback path and end up worse than sprintf for a large class of inputs (open issue #83)
- DoubleToAscii on N\*10^M-shaped values hits the same Grisu3-fails/bignum-fallback slow path (open issue #28, open since 2016)
- ALLOW_HEX and ALLOW_OCTALS parsing flags only apply to integer literals; combining them with fractional/exponent characters yields 'trailing junk' rather than a parse error

## Caveats and trade-offs

Benchmark hardware (2009-era Core i7 920) and compiler (VC++2013) are over a decade old; explicit optimizer flags not stated so this falls short of Tier A; benchmark predates C++17 std::to_chars, so std::ostringstream (iostreams) is the only in-scope std facility with a number on the page; sprintf figure is the page's own ratio, ostringstream ratio is derived from page data.

Built as a small standalone library (not header-only), needs its own build step; C++ (extracted from V8's number conversion code); covers both double-&gt;string and string-&gt;double directions, matching std::to_chars and std::stod/from_chars.

## Maintenance

Actively maintained (last commit 2026-09-13, enrolled in OSS-Fuzz and OpenSSF Scorecard) and BSD-3-Clause; not header-only, so it needs a small build step or manual vendoring of its \~8 .cc files, but has no external dependencies.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification B, tier now B.
- **Tier reason:** In the independent, well-known miloyip/dtoa-benchmark README, the doubleconv row reads 201.645 ns (6.23x vs sprintf) and the ostringstream row reads 2,778.748 ns, so the derived \~13.8x is correct. Benchmark code is public and VC2013 plus Core i7 920 are stated, but literal compiler flags are not (premake flags {"Optimize"} only), so B rather than A.
- **Verifier notes:** Metadata checks out: BSD-3-Clause, 1,194 stars, last commit 2026-09-13 (active), not a fork, not archived. The benchmark ran double-conversion via EcmaScriptConverter().ToShortest().
- **Fields the verifier corrected:** `compiler_and_flags`
- **Pages the verifier opened:**
  - <https://github.com/miloyip/dtoa-benchmark>
  - <https://github.com/miloyip/dtoa-benchmark/blob/master/build/premake4.lua>
  - <https://github.com/google/double-conversion>
- **Sources the enricher read:**
  - <https://github.com/google/double-conversion>
  - <https://github.com/google/double-conversion/blob/master/README.md>
  - https://github.com/google/double-conversion (repo tree listing)
  - <https://github.com/google/double-conversion/blob/master/double-conversion/double-to-string.h>
  - <https://github.com/google/double-conversion/blob/master/double-conversion/utils.h>
  - <https://github.com/google/double-conversion/blob/master/double-conversion/string-to-double.h>
  - <https://github.com/google/double-conversion/blob/master/CMakeLists.txt>
  - <https://github.com/google/double-conversion/blob/master/BUILD>
  - <https://github.com/google/double-conversion/blob/master/Changelog>
  - <https://github.com/google/double-conversion/issues/28>
  - <https://github.com/google/double-conversion/issues/83>
  - https://github.com/google/double-conversion/issues (search: bug, performance)
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/google/double-conversion`) · [data/wave1/enrich/raw/github_com_google_double_conversion.json](../../../data/wave1/enrich/raw/github_com_google_double_conversion.json) (enrichment confidence 0.78)

</details>
