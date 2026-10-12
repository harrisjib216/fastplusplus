# {fmt}

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Number parsing and formatting](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🟢 active

> Type-safe C++ formatting library beating printf/iostreams; its Dragonbox-based float formatter is the speed driver here.

| | |
|---|---|
| **Beats** | printf (sprintf) |
| **Claimed result** | 20.214x faster than sprintf per double (36.84ns vs 744.72ns); \~24x faster than ostringstream (885.30ns) (derived from page data); fmt README separately states '{fmt} can be tens of percent to 20-30x faster than sprintf and iostreams, especially for numeric formatting' |
| **Workload** | Converting each of a 1.7M-value pool of random doubles (reduced to 1-17 significant digits) to a shortest round-trip decimal string via fmt::format_to with compile-time format strings, measured with Google Benchmark; mean time per conversion. |
| **Metric** | latency |
| **Hardware** | MacBook Pro (Apple M1 Pro) |
| **Compiler and flags** | Apple clang version 21.0.0 (clang-2100.0.123.102); CMake default Release build type (CMakeLists.txt sets CMAKE_BUILD_TYPE=Release for optimized code; exact -O flag not printed in the results table itself) |
| **Adoption** | 25.8k stars; used in FoundationDB, Ceph, ClickHouse, Envoy, Battle.net, and the reference implementation basis for C++20 std::format |
| **Last commit** | 2026-09-21 |
| **Links** | [repository](https://github.com/fmtlib/fmt) · [benchmark](https://github.com/fmtlib/dtoa-benchmark) |

## Verdict

On an Apple M1 Pro with Apple Clang 21.0.0, fmt::format_to with FMT_COMPILE converted a 1.7M-value pool of random doubles to shortest round-trip decimal strings in a mean 36.84ns each, versus 744.72ns for sprintf (20.214x) and 885.30ns for ostringstream (\~24x), per the fmtlib/dtoa-benchmark suite that fmt's own README links from its Performance section.

## Use it when

- Hot paths converting many doubles/ints to strings (logging, serialization) where printf/iostreams latency is measurable
- Format strings are known at compile time and paired with FMT_COMPILE to get the benchmarked fast path — the \~20x number does not apply to runtime-only format strings
- Need shortest, correctly-rounded, round-trip float-to-string output, which sprintf/ostringstream do not guarantee
- C++11+ codebase that can take on a header-only or compiled dependency for type-safe, low-allocation formatting
- Already moving toward C++20/23 std::format/std::print — fmt is the pre-standard superset (adds chrono, ranges, color/style output)

## Skip it when

- Format strings are assembled dynamically at runtime with unknown structure — loses the FMT_COMPILE path the benchmark measured
- printf's current latency is already acceptable and adding any dependency isn't worth it
- Pre-C++11 toolchain — CMakeLists.txt requires cxx_std_11 as a hard minimum
- Compile-time budget is tight across many translation units: fmt headers add \~5.1s vs printf's 1.6s per the README's 100-TU bloat-test (still far below IOStreams' 25.5s)
- Need it truly drop-in for existing printf/sprintf call sites — the fast {}-syntax API requires rewriting call sites; only fmt::printf approximates a drop-in and wasn't the path benchmarked

## How it is fast

Float-to-string conversion uses the Dragonbox algorithm for shortest, correctly-rounded, round-trip decimal output, confirmed directly in the dtoa-benchmark README ('fmt::format_to with compile-time format strings (uses Dragonbox)'). FMT_COMPILE parses the format string into formatting code at compile time — confirmed in include/fmt/compile.h, which requires C++17 constexpr-if support for the compiled fast path and otherwise silently falls back to a non-compiled string check. Output accumulates in fmt::memory_buffer, avoiding iostreams' per-call locale/stream-state overhead and sprintf's null-terminated buffer handling.

## Compared with alternatives

Pick fmt when you want a full formatting API (containers, chrono, positional args, color output) whose float path happens to use Dragonbox internally, not just a float-to-string primitive. Pick Dragonbox directly (1.77x faster than std::to_chars) or Ryu (16.164x vs sprintf) when you need a standalone dtoa routine with no formatting-library overhead; fast_float solves the reverse problem (string-to-double parsing) and isn't a substitute here.

## Integration

| | |
|---|---|
| **Form** | header-only (FMT_HEADER_ONLY macro) or compiled static/shared lib (default); minimum config is 3 headers (core.h, format.h, format-inl.h) per README |
| **Dependencies** | none (README: 'no external dependencies') |
| **Minimum toolchain** | C++11 minimum (CMakeLists.txt: target_compile_features(fmt PUBLIC cxx_std_11)); C++17 constexpr-if needed for the FMT_COMPILE fast path used in the benchmark |
| **Platforms** | any — README lists Linux/macOS/Windows CI (linux.yml, macos.yml, windows.yml workflows); no architecture-specific requirement found |
| **Thread safety** | 'fmt::format is thread-safe' (fmt maintainer, GitHub issue #3417 comment); no broader documented guarantee found this session for fmt::print or format_to writing into a buffer shared across threads |
| **Drop-in for the baseline** | partial — fmt::printf (fmt/printf.h) offers printf-syntax compatibility including POSIX positional args, but the benchmarked fast path (fmt::format_to + FMT_COMPILE) uses the different {}-format API and is not a source drop-in for sprintf |

## Gotchas

- FMT_COMPILE needs C++17 constexpr-if (__cpp_if_constexpr) to produce the compiled fast path; without it, it falls back to FMT_STRING (compile-time validated, not the fast-formatting path) — per include/fmt/compile.h
- Exceptions can be disabled for -fno-exceptions builds via FMT_USE_EXCEPTIONS (checked in include/fmt/format.h)
- basic_memory_buffer takes an Allocator template parameter (include/fmt/format.h) for custom allocation, but the default allocator is used unless a caller specifies otherwise

## Caveats and trade-offs

The exact numbers come from the fmtlib/dtoa-benchmark repo (linked from the fmt README's Performance section) rather than being pasted directly into the fmt README; the fmt README's own separate compile-time table (Apple M5 Max, Apple Clang 21.0.0, -O3) shows a different comparison (compile time/binary size, not speed) so was not used here. Single-hardware-sample (Apple M1 Pro) result; 'Release' build config was confirmed by reading CMakeLists.txt rather than being printed alongside the results table.

Adds a header-only or compiled dependency vs. printf; compiles noticeably slower than raw printf (5.1s vs 1.6s for the bloat-test suite) though far faster than IOStreams (25.5s); template-heavy formatting machinery can grow binary size if many format-string/type combinations are instantiated; requires C++11+.

## Maintenance

Actively maintained (25,807 stars, MIT license, last commit 2026-09-21, 12 open issues, not archived) — low-risk long-term dependency; it's the reference basis for C++20 std::format.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): confirm; tier before verification A, tier now A.
- **Tier reason:** The fmtlib/dtoa-benchmark README table shows fmt 36.84 ns against sprintf 744.72 ns (20.214x) and ostringstream 885.30 ns, on an Apple M1 Pro with Apple clang 21.0.0. The code is public (src/fmt-test.cc uses FMT_COMPILE), and CMakeLists.txt pins the Release build type (-O3 -DNDEBUG).
- **Verifier notes:** The fmt README Performance section quote ('tens of percent to 20-30 times faster than sprintf and iostreams') is verbatim and links to dtoa-benchmark. The \~24x figure against ostringstream is correctly derived. Metadata checked: MIT license, 25806 stars, last commit 2026-09-21.
- **Shortcomings recorded by:** Formatting 20k mixed rows with '{:&gt;8} {:&gt;10.3f} {}', fmt::format_to with FMT_COMPILE took 71.9 ns/row vs 227.129 ns for snprintf (3.16x) and 391.713 ns for std::ostringstream. fmt::format returning a std::string took 140.399 ns, about 35% over format_to into a reused stack buffer (104.134 ns). (developer source, private repo; gcc 13.3.0 -O2 -march=native, Intel Xeon @ 2.10GHz, run 2026-09-02-core); Writing 20k doubles in shortest round-trip form, fmt (Dragonbox) took 52.679 ns each vs 288.311 ns for snprintf %.17g (5.47x) and 456.477 ns for std::ostringstream. (developer source, private repo; gcc 13.3.0 -O2 -march=native, Intel Xeon @ 2.10GHz, run 2026-09-02-core)
- **Pages the verifier opened:**
  - <https://github.com/fmtlib/dtoa-benchmark>
  - <https://github.com/fmtlib/dtoa-benchmark/blob/main/CMakeLists.txt>
  - <https://github.com/fmtlib/dtoa-benchmark/blob/main/src/fmt-test.cc>
  - <https://github.com/fmtlib/fmt>
- **Sources the enricher read:**
  - <https://github.com/fmtlib/fmt>
  - <https://github.com/fmtlib/fmt/blob/master/README.md>
  - <https://github.com/fmtlib/fmt/blob/master/CMakeLists.txt>
  - <https://github.com/fmtlib/fmt/blob/master/include/fmt/base.h>
  - <https://github.com/fmtlib/fmt/blob/master/include/fmt/core.h>
  - <https://github.com/fmtlib/fmt/blob/master/include/fmt/format.h>
  - <https://github.com/fmtlib/fmt/blob/master/include/fmt/compile.h>
  - <https://github.com/fmtlib/fmt/issues/3417>
  - <https://github.com/fmtlib/dtoa-benchmark/blob/main/README.md>
- **Raw records:** [data/wave0-seed/verified.json](../../../data/wave0-seed/verified.json) (id `https://github.com/fmtlib/fmt`) · [data/wave0-seed/enrich/raw/github_com_fmtlib_fmt.json](../../../data/wave0-seed/enrich/raw/github_com_fmtlib_fmt.json) (enrichment confidence 0.88)

</details>
