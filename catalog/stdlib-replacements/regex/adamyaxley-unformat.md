# Unformat

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Regex](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Unlicense` · 🟢 active

> Single-header scanf-style '{}' field extractor for fixed-shape strings; beats std::regex when regex is overkill.

| | |
|---|---|
| **Beats** | std::regex |
| **Claimed result** | Unformat: 32.6 ns (11.5 ns using the compile-time constexpr make_format path) vs std::regex (StdRegex in the benchmark): 3269 ns -- roughly 100x-284x faster; the project's own description claims 'up to 300x faster than std::regex'. |
| **Workload** | Parsing 'Harry is 18 years old and weighs 67.8 kilograms' against '{} is {} years old and weighs {} {}' into string_view, int, float and string_view, timed with Google Benchmark (unformat_benchmark.cpp). The std::regex leg uses regex_search with a 4-group pattern, then stoi/stof and std::string copies. The README usage example '{} is {} years old.' is not the benchmarked input. |
| **Metric** | latency |
| **Hardware** | 32 x 2420 MHz CPUs (exact CPU model and OS not stated) |
| **Adoption** | 46 stars |
| **Last commit** | 2026-03-02 |
| **Links** | [repository](https://github.com/adamyaxley/Unformat) · [benchmark](https://github.com/adamyaxley/Unformat/blob/master/README.md) |

## Verdict

On the repo's own Google Benchmark run (32 x 2420 MHz CPUs; compiler, flags, and OS unstated), Unformat took 32.6 ns per call (11.5 ns with the constexpr make_format path) versus 3269 ns for std::regex parsing the same 4-field string. The std::regex leg constructs (compiles) the regex object inside the timed loop every iteration, so that 3269 ns bundles NFA compilation with the match itself; against a precompiled regex the gap would be far smaller than the \~100x-284x (or advertised '300x') headline suggests.

## Use it when

- Extracting a handful of ints/floats/strings from a fixed, known-shape line (logs, telemetry, simple protocols) where std::regex would only be used for its capture groups, not real pattern matching.
- Hot loops calling the same format thousands of times per second, where std::regex's per-construction NFA compile is the bottleneck (the benchmarked 3269 ns/call includes that compile, not just matching).
- The format string can be pinned as a compile-time literal, so ay::make_format runs at compile time (11.5 ns vs 32.6 ns for the runtime-parsed path, per the repo's own benchmark).
- Header-only vendoring is acceptable: copy unformat.h into a codebase with no other dependencies and no build-system integration.
- Input is trusted and guaranteed to match the format exactly (internal data, not raw user/network input).

## Skip it when

- You need actual regex features -- wildcards, character classes, alternation, quantifiers, anchors; Unformat only matches literal text between '{}' tokens.
- Input may be malformed, truncated, or adversarial: the string_view/char scan path (unformat_arg_scan&lt;ay::string_view&gt; in unformat.h) has no check against the input's terminating null while hunting for a delimiter, so a non-matching string can read past the buffer end.
- You need match/fail feedback: there is no success return, exception, or optional -- bad input silently yields wrong values (a 'does this match' check was requested in issue #3 back in 2017 and is still open).
- More than 16 '{}' placeholders in one format string (hard-coded format::MAX_COUNT = 16).
- Your real baseline is a precompiled std::regex rather than one rebuilt every call -- the \~100x-284x gap narrows a lot once compilation is amortized (see verified_claims_summary).

## How it is fast

It avoids std::regex entirely: no NFA construction, no std::string allocations, no capture-group bookkeeping. The constexpr make_format path precomputes each placeholder's byte offset and delimiter character at compile time, so unformat_internal just walks pointers with inlined, per-type combined scan+parse loops (fixed-point digit accumulation instead of std::stoi/std::stof). Numeric parsing accumulates an integer mantissa and applies one final multiply against precomputed powers-of-10 tables, with a noinline cold path reserved for scientific notation or &gt;18-digit literals.

## Compared with alternatives

Pick Unformat over Boost.Regex, RE/flex, or REAL when you're pulling a few typed fields out of a fixed-shape string and don't need any real regex syntax (wildcards, classes, alternation) -- it's a smaller, dependency-free single header, where the siblings are full regex engines (or, for RE/flex, a code-generation tool) sized for genuine pattern-matching workloads.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (only &lt;cstddef&gt; from the standard library) |
| **Minimum toolchain** | C++14 in practice for the constexpr make_format path -- make_format_non_template declares a local variable, uses a loop, and a throw, which need C++14 relaxed-constexpr rules. CMakeLists.txt sets CMAKE_CXX_STANDARD 11 for the test/benchmark build, which predates that; the plain runtime unformat() call compiles fine under C++11. |
| **Platforms** | any -- portable C++, no SIMD/intrinsics; MSVC/GCC/Clang are detected via macros only to pick inline/noinline/restrict hints, with a generic fallback for other compilers |
| **Thread safety** | not documented; the implementation has no shared/global mutable state beyond read-only static pow10 lookup tables, so concurrent calls writing to disjoint output variables look safe by inspection |

## Gotchas

- The string_view/char scan path has no null-terminator check while hunting for a placeholder's end delimiter -- malformed input that never contains that delimiter can read out of bounds (verified in unformat.h's unformat_arg_scan&lt;ay::string_view&gt; specialization).
- Exceeding 16 '{}' placeholders throws a raw string literal ("Max number of {} has been exceeded.") from the format constructor -- a compile error in a constexpr context, an untyped throw at runtime.
- ay::string_view is a bare {const char\* data; size_t size;}, non-owning into the original input buffer -- it dangles if the source string is freed, reallocated, or goes out of scope.
- CMakeLists.txt declares C++11 but constexpr make_format needs C++14 relaxed-constexpr to actually compile as constexpr; verify your compiler's effective standard before relying on the compile-time path.

## Caveats and trade-offs

The StdRegex benchmark constructs (compiles) std::regex inside the timed loop on every iteration, so the 3269 ns includes pattern compilation plus std::string/stoi/stof conversions. That inflates the gap versus a precompiled regex, and the '300x' claim should be read with this in mind. The README does not state the compiler, optimization flags or OS (only 32 x 2420 MHz CPUs). The same run also shows std::stringstream at 391 ns and sscanf at 677 ns. This is typed parsing of a fixed format, narrower than general regex matching.

Not a general regex engine -- only handles fixed brace-delimited '{}' format-string extraction of basic types (similar to a type-safe scanf), with no wildcards, character classes, alternation, or quantifiers, so it cannot replace std::regex for general pattern matching; the win mainly reflects avoiding std::regex's NFA-compilation/allocation overhead for a task regex is overkill for.

## Maintenance

Actively maintained as of March 2026, with recent commits micro-optimizing numeric parsing and the pow10 tables; public-domain (Unlicense) and small enough (one header) to vendor and maintain yourself even if upstream activity stops.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The README shows Google Benchmark output from the in-repo unformat_benchmark.cpp (Unformat 32.6 ns, constexpr 11.5 ns, StdRegex 3269 ns), but the compiler, flags and OS are unstated (only '32 X 2420 MHz CPU s'), and the gain is 100-284x (&gt;50x). That caps it at C.
- **Verifier notes:** The numbers match the README; the repo description says 'up to 300x faster than std::regex'. Metadata verified: Unlicense (OSI-approved), 46 stars, last commit 2026-03-02, not a fork. The workload was misdescribed and a significant fairness caveat (regex compiled per iteration) was missing; both are now fixed.
- **Fields the verifier corrected:** `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/adamyaxley/Unformat/blob/master/README.md>
  - <https://github.com/adamyaxley/Unformat>
  - <https://github.com/adamyaxley/Unformat/blob/master/unformat_benchmark.cpp>
- **Sources the enricher read:**
  - <https://github.com/adamyaxley/Unformat>
  - <https://github.com/adamyaxley/Unformat/blob/master/README.md>
  - <https://github.com/adamyaxley/Unformat/blob/master/unformat.h>
  - <https://github.com/adamyaxley/Unformat/blob/master/unformat_benchmark.cpp>
  - <https://github.com/adamyaxley/Unformat/blob/master/unformat_test.cpp>
  - <https://github.com/adamyaxley/Unformat/blob/master/CMakeLists.txt>
  - <https://github.com/adamyaxley/Unformat/issues>
  - <https://github.com/adamyaxley/Unformat/commits/master>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/adamyaxley/unformat`) · [data/wave1/enrich/raw/github_com_adamyaxley_unformat.json](../../../data/wave1/enrich/raw/github_com_adamyaxley_unformat.json) (enrichment confidence 0.6)

</details>
