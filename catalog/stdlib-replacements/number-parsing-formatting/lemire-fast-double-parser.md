# fast_double_parser

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Number parsing and formatting](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `Apache-2.0` · 🟡 stale

> Header-only C++11 double parser using the Eisel-Lemire algorithm; 2.5-9.5x strtod throughput, superseded by fast_float.

| | |
|---|---|
| **Beats** | std::stod (strtod) |
| **Claimed result** | Headline: 4x faster than strtod. Benchmark detail: random integers 460.64 MB/s (fast_double_parser) vs 186.90 MB/s (strtod), \~2.5x; canada.json real-world doubles 662.01 MB/s vs 69.73 MB/s, \~9.5x. |
| **Workload** | Parsing ASCII decimal strings into IEEE754 double, measured in MB/s against strtod_l (C locale), abseil, and double-conversion. Two inputs: random doubles in [0,1) generated as rand()/RAND_MAX (the benchmark labels these 'random integers in the range [0,1)'), and real-world coordinates from canada.json/canada.txt. Configuration: Apple clang 11.0.0 on an i7-7700K. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-7700K |
| **Compiler and flags** | Apple clang 11.0.0 (stated in README); CMake Release build (CMakeLists.txt defaults CMAKE_BUILD_TYPE to Release) |
| **Adoption** | 670 stars; algorithm ported into Go's standard library and used in Microsoft LightGBM |
| **Last commit** | 2025-05-27 |
| **Links** | [repository](https://github.com/lemire/fast_double_parser) · [benchmark](https://github.com/lemire/fast_double_parser/blob/master/README.md) |

## Verdict

Benchmarked against strtod_l (C locale) on Apple clang 11.0.0 / Intel Core i7-7700K: 460.64 MB/s vs strtod's 186.90 MB/s (\~2.5x) parsing random doubles in [0,1), and 662.01 MB/s vs 69.73 MB/s (\~9.5x) parsing the canada.json real-world coordinate dataset; the README's '4x' headline sits between these two workload-specific ratios. The same run also reports abseil and double-conversion figures, both slower than fast_double_parser on both workloads.

## Use it when

- Hot-path parsing of many decimal doubles from files/network (GeoJSON, CSV, log lines) where strtod is a measured bottleneck
- JSON-shaped numeric literals only (no hex floats, no locale decimal comma)
- Header-only vendoring is acceptable (drop include/fast_double_parser.h into the build)
- C++11-only toolchains that can't adopt fast_float's newer API/build requirements
- Throughput-bound batch parsing (MB/s) rather than a single latency-critical call

## Skip it when

- Any new project — the README itself tells users to adopt fast_float instead (more grammar support, same speed, wider adoption/testing)
- Need std::from_chars-style explicit begin/end pointers rather than a null/non-numeric-terminated C string — use fast_float
- Need 32-bit float parsing — this library is double-only
- Need hex floats, NaN/Infinity, or non-JSON strtod grammar (e.g. leading '+', "0x1p3", leading zeros like "01")
- Repo is stale (last commit 2025-05-27) with only 2 open issues (macro hygiene, power-range tightening) and no active feature work

## How it is fast

Implements the Eisel-Lemire algorithm (Lemire, "Number Parsing at a Gigabyte per Second," arXiv:2101.11408): accumulate up to 19 significant digits into a 64-bit integer, then multiply it by a precomputed 64-bit truncated mantissa for the decimal exponent using a 128-bit full multiplication (hardware `_umul128`/`__uint128_t`, with an emulated fallback) to directly assemble the correctly-rounded IEEE754 bit pattern. This skips strtod's general parsing path entirely and falls back to the platform's locale-independent strtod_l/_strtod_l only for the rare &gt;19-significant-digit or ambiguous-rounding cases.

## Compared with alternatives

No catalogued sibling targets double parsing (they cover to_chars/from_chars formatting or integer conversions); the real alternative is its own successor fast_float. Pick fast_double_parser only when a C++11-only toolchain or an existing call site already depends on its exact pointer-in/pointer-out API — otherwise fast_float matches its speed with a std::from_chars-style API and broader (non-JSON-restricted) grammar support.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (the benchmark target pulls in abseil and double-conversion, but the library itself has zero deps) |
| **Minimum toolchain** | C++11 (CMakeLists sets CMAKE_CXX_STANDARD 11); MSVC, GCC, and Clang all supported |
| **Platforms** | x86-64, ARM64, and 32-bit (native _umul128/__uint128_t 128-bit multiply where available, emulated fallback otherwise); Windows/Linux/macOS plus a stringstream-based strtod workaround for Cygwin/MSYS2/Solaris |
| **Thread safety** | not explicitly documented by the project; from reading the header, parse_number is a pure function over caller-supplied buffers, and the &gt;19-digit fallback path uses a function-local static locale object (newlocale/_create_locale) whose one-time initialization is safe under C++11's thread-safe 'magic statics' rule, so concurrent parsing calls appear safe |
| **Drop-in for the baseline** | partial — explain: produces the same double, bit-for-bit, as strtod (by the library's own accuracy claim), but the call is parse_number(const char\*, double\*) returning an end-pointer, not std::stod(std::string) with exceptions, so call sites need adapting |

## Gotchas

- Global-namespace macros (WARN_UNUSED, really_inline, unlikely) defined in the header are never #undef'd and can collide with same-named macros pulled in transitively from other libraries (issue #66); this bit a real user combining it with Microsoft LightGBM, which itself vendors this same library
- Rejects some strtod-valid-but-JSON-invalid forms: leading zeros ("01"), a bare trailing decimal point ("1."), hex floats, and never produces NaN/Infinity
- Falls back to platform strtod_l for any number with &gt;19 significant digits, so very long decimal mantissas get strtod's speed rather than the fast path
- Assumes the FPU rounding mode is round-to-nearest (FE_TONEAREST); behavior under other rounding modes is unverified

## Caveats and trade-offs

The project's own README explicitly tells users to adopt fast_float instead ('We encourage users to adopt fast_float library instead of fast_double_parser'), so this is best treated as a historical/reference implementation rather than a current recommendation; benchmarked directly against strtod (the C routine std::stod delegates to) rather than a literal std::stod(std::string) call, though the two are computationally equivalent for this purpose.

Only parses double (no formatting direction); JSON (RFC 7159) grammar only, not the full strtod grammar (e.g. no hex floats); superseded by the same author's fast_float (github.com/fastfloat/fast_float, already catalogued), which the README itself now recommends instead.

## Maintenance

Maintenance status is stale — last commit 2025-05-27, no active feature development, and the maintainer's own README recommends migrating to fast_float — but it's a single small header under a dual Apache-2.0/Boost-1.0 license, cheap to vendor and freeze if a project already depends on its exact API.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** The benchmark code is benchmarks/benchmark.cpp in the repo and times strtod_l (C locale) directly. The README gives the build steps (CMake, --config Release, which is also the default build type in CMakeLists.txt). The README states the configuration as Apple clang 11.0.0 on an i7-7700K.
- **Verifier notes:** The original benchmark_url (the benchmarks/ directory) holds only code and data. The numbers are in the README's 'Sample results' section and the canada.json table, so the URL was changed to the README. The record's workload was wrong to say 'integer-valued doubles': the input is random doubles in [0,1). All figures (460.64 vs 186.90 MB/s, 662.01 vs 69.73 MB/s, the '4x' headline) and the README's pointer to fast_float are confirmed.
- **Fields the verifier corrected:** `benchmark_url`, `compiler_and_flags`, `workload`
- **Pages the verifier opened:**
  - <https://github.com/lemire/fast_double_parser>
  - <https://github.com/lemire/fast_double_parser/tree/master/benchmarks>
  - <https://github.com/lemire/fast_double_parser/blob/master/README.md>
  - <https://github.com/lemire/fast_double_parser/blob/master/benchmarks/benchmark.cpp>
  - <https://github.com/lemire/fast_double_parser/blob/master/CMakeLists.txt>
- **Sources the enricher read:**
  - <https://github.com/lemire/fast_double_parser>
  - <https://github.com/lemire/fast_double_parser/blob/master/README.md>
  - <https://github.com/lemire/fast_double_parser/tree/master>
  - <https://github.com/lemire/fast_double_parser/blob/master/include/fast_double_parser.h>
  - <https://github.com/lemire/fast_double_parser/blob/master/CMakeLists.txt>
  - <https://github.com/lemire/fast_double_parser/issues>
  - <https://github.com/lemire/fast_double_parser/issues/66>
  - <https://github.com/lemire/fast_double_parser/blob/master/LICENSE.BSL>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/lemire/fast_double_parser`) · [data/wave1/enrich/raw/github_com_lemire_fast_double_parser.json](../../../data/wave1/enrich/raw/github_com_lemire_fast_double_parser.json) (enrichment confidence 0.9)

</details>
