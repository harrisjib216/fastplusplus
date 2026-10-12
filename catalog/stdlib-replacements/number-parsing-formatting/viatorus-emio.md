# emio

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Number parsing and formatting](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only C++20 format/scan library for embedded targets; claims integer scanning about 2x sscanf, binary about 38x smaller than {fmt}.

| | |
|---|---|
| **Beats** | scanf (sscanf) |
| **Claimed result** | "Scanning on the other hand is around twice as fast then scanf." (docs/DESIGN.md, Performance section). Formatting is stated to be "round about 1.5 - 2 times slower than fmtlib" and "similar to printf (e.g. for integer types)". |
| **Workload** | emio::scan with compile-time or runtime format strings (nothing, simple int, 64-bit int, hex) versus sscanf, run with Catch2 BENCHMARK in test/benchmark/bench_scan.cpp. |
| **Metric** | throughput |
| **Adoption** | 189 stars; on Conan Center |
| **Last commit** | 2026-08-26 |
| **Links** | [repository](https://github.com/Viatorus/emio) · [benchmark](https://github.com/Viatorus/emio/blob/main/docs/DESIGN.md) |

## Verdict

The only performance evidence is a prose sentence in docs/DESIGN.md: scanning is 'around twice as fast' as sscanf (glibc on GitHub-hosted Ubuntu CI runners), and formatting is 1.5-2x slower than fmt and similar to printf for integers, measured by Catch2 BENCHMARK cases (a 445-character literal, "1", a 19-digit int64 and a 16-digit hex uint64) with no committed results, compiler, flags or CPU. The concrete measured win is binary size: about 5 kB versus 191 kB of flash for one statically linked format("{}", 1).

## Use it when

- Firmware on Cortex-M class MCUs (128 kB-2 MB flash) where fmt's 191 kB for one statically linked format("{}", 1) is unaffordable; DESIGN.md measures about 5 kB for emio, and CI size-tests arm-none-eabi Cortex-M7 builds with newlib and nano.specs.
- Builds with -fno-exceptions and no heap: results propagate as emio::result with EMIO_TRY/EMIO_TRYV, output goes to static_buffer/span_buffer, and freestanding builds are supported since April 2024 (#92).
- Replacing sscanf for fixed-shape text (UART commands, sensor lines, key=value config) parsed into integers, chars or string_views, where compile-time-checked format strings and typed arguments remove the varargs/format-mismatch bugs of scanf.
- Code that needs both formatting and scanning, possibly in constexpr context, from one small header-only dependency.

## Skip it when

- Floating-point input: there is no float scanner; use fast_float or std::from_chars.
- Throughput-bound formatting on hosted systems: self-reported 1.5-2x slower than fmt, and floats go through Dragon4; {fmt}, Dragonbox or jeaiii/itoa are faster.
- Parsing untrusted integers where range errors matter: the overflow check in detail::parse_int misses many out-of-range inputs (see gotchas), so values can be silently wrapped.
- Hot-loop number conversion where field boundaries are already known: std::from_chars or fast_float skip format-string handling entirely, and emio publishes no numbers against them.
- Projects needing locale support, fmt API compatibility, chrono formatting (open #8) or a stable API: the library is labelled beta and issue #10 'Define a stable API' has been open since 2022.

## How it is fast

Against sscanf the gain comes from avoided overhead, not a new parsing algorithm: no FILE/stream object, varargs or locale handling, compile-time-validated format strings so only a light re-parse runs per call, and a literal-only format is matched with a single memcmp-style compare (reader::read_if_match_str). Integers are parsed with a plain digit-by-digit multiply-add loop (detail::parse_int), and arguments are type-erased behind one virtual call each (concept/model objects in inline storage) to keep template instantiations and code size small. Float formatting uses a Dragon4 bignum port of Rust's flt2dec 'dragon' strategy, which is exact and compact but not a Ryu/Dragonbox-class algorithm; the author's own docs and issue #6 say formatting is 1.5-2x slower than fmt because the goal is the smallest binary, not the fastest code.

## Compared with alternatives

Pick emio over {fmt} when flash size, no exceptions and no heap matter more than speed (fmt formats 1.5-2x faster by emio's own account), and over scnlib (catalogued under serialization-json, with tier-A scan numbers against sscanf and stringstream and float support) when you want one tiny library for both formatting and scanning on a microcontroller; for raw conversion speed, fast_float, Dragonbox or rigtorp/CharConv are the better tools.

## Integration

| | |
|---|---|
| **Form** | header-only (CMake INTERFACE target emio::emio; Quom-generated single header; Conan Center recipe) |
| **Dependencies** | none (fmt and Catch2 are fetched only for its own tests and benchmarks) |
| **Minimum toolchain** | C++20; README says tested with GCC 11/12/13 and Clang 16/17; the CI matrix also lists GCC 14 and Clang 18/19 with C++20 and C++23 |
| **Platforms** | any C++20 target; CI builds and tests x86-64 Linux and size-tests arm-none-eabi (Cortex-M7); emscripten include fixes landed in #101; MSVC not documented |
| **Thread safety** | not documented; the scan and format paths read keep all state in caller-owned reader, writer and buffer objects with no global state, so concurrent calls on separate buffers appear safe |
| **Drop-in for the baseline** | partial — replaces sscanf only for integers, chars and strings, with {}-style format strings, exact literal matching (a space in the format is a literal space, not scanf's 'skip any whitespace'), whole-input consumption required by emio::scan, no leading-whitespace skipping for integers, and an emio::result instead of a match count |

## Gotchas

- Integer overflow detection is incomplete (found by reading include/emio/reader.hpp detail::parse_int and running a Python model of the loop with wrap-around arithmetic; not compiled, no issue filed). The loop only rejects when value\*base+digit wraps below the previous value, so many out-of-range inputs pass: scanning "5000000000" into uint32_t returns success with 705032704, "30000000000000000000" into uint64_t gives 11553255926290448384, and hex "1FFFFFFFFFFFFFFFF" into uint64_t gives 0xFFFFFFFFFFFFFFFF; about 75% of random 10-digit values above UINT32_MAX are accepted. For int32_t/int64_t the multiply is signed overflow (undefined behaviour). docs/API.md promises err::out_of_range, but the unit tests (test/unit_test/integer_ranges.hpp) only try max+1 and max\*10, which the check does catch. uint32_t and int32_t are not upcast before parsing (upcasted_int_t maps them to themselves), so plain int/unsigned scans are affected.
- Benchmark harness (test/benchmark/bench_scan.cpp): the sscanf rows are labelled "snprintf"; the 'scan nothing' case pits emio's single memcmp of a 445-character literal against sscanf interpreting the same text as a format in which every space is a 'skip any whitespace' directive, so the two do different work; sscanf %d and %" PRIi64 " also skip leading whitespace and %i auto-detects the base, which emio's "{}" does not. All benchmark inputs are in range and checked in the 'base' cases, so the overflow bug does not change the measured rows.
- The 2x figure points to CI logs only: ctest runs the benchmark binary in both Debug and Release builds on shared GitHub-hosted runners, no result is committed, and the matrix's gcc-14 and clang-19 jobs have no matching branch in the 'Install Compiler' step, so they build with the runner's default compiler under a wrong label. The benchmarks link fmt pinned to an unreleased 9.1.1 commit that no longer builds with clang-20 (#111).
- Version metadata is inconsistent: CMakeLists.txt still says 0.2.0 while the README's Compiler Explorer link uses emio 0.8.0 (open issue #108).

## Known shortcomings

- One prose claim in DESIGN.md (scanning about 2x faster than sscanf) with no compiler, flags or CPU; benchmark output is not committed and CI runs it in both Debug and Release; bench_scan.cpp labels its sscanf rows 'snprintf'. Formatting is 1.5-2x slower than fmt.
- Enricher: the overflow check in detail::parse_int (include/emio/reader.hpp) only rejects when value\*base+digit wraps below the previous value, so scanning '5000000000' into uint32_t succeeds as 705032704, '30000000000000000000' into uint64_t as 11553255926290448384 and hex '1FFFFFFFFFFFFFFFF' as 0xFFFFFFFFFFFFFFFF (about 75% of 10-digit values above UINT32_MAX accepted; signed paths hit overflow UB; unit tests try only max+1 and max\*10); unreported, benchmark inputs are in range so the measured rows are unchanged. bench_scan.cpp labels sscanf rows 'snprintf' and its 'scan nothing' row times one memcmp against sscanf's whitespace-skipping format interpretation; the 2x claim exists only in CI logs, and the gcc-14/clang-19 matrix jobs build with the runner's default compiler. No float scanning; formatting (Dragon4) is self-reported 1.5-2x slower than fmt.

## Caveats and trade-offs

Single first-party prose sentence in docs/DESIGN.md ('Scanning on the other hand is around twice as fast then scanf'); no result table, compiler, flags or CPU are given and no benchmark output is committed. The DESIGN.md points to 'the benchmark tests inside the CI': the CI matrix (GCC 11-13, Clang 16-19 on GitHub-hosted Ubuntu runners) runs ctest --verbose in both Debug and Release builds, so it is unknown which build or compiler the 2x figure came from, and the CI logs could not be opened here. In test/benchmark/bench_scan.cpp the sscanf cases are mislabelled 'snprintf'; the four cases are a 445-character literal-only format, a single-digit int, a 19-digit int64 and a 16-digit hex uint64, each with a compile-time and a runtime format string, and the claim does not say whether the runtime-format path (parsed sequentially, which DESIGN.md calls a performance overhead) is also 2x. The sscanf baseline is the C library (glibc on the CI runners), not a C++ standard library. Its own DESIGN.md says formatting is about 1.5-2x slower than fmtlib and similar to printf, so the speed win is scanning only; the headline win is binary size (about 5 kB vs 191 kB for fmt, 38x smaller). No independent measurement was found (one web search). [retier] One prose claim in DESIGN.md (scanning about 2x faster than sscanf) with no compiler, flags or CPU; the numbers exist only in CI logs (Debug and Release both run; the gcc-14/clang-19 matrix jobs have no install step, so they build with the runner's default compiler). bench_scan.cpp labels its sscanf rows 'snprintf' and its 'scan nothing' row times one memcmp against sscanf's whitespace-skipping format interpretation. Correctness: the overflow check in detail::parse_int (include/emio/reader.hpp) rejects only when value\*base+digit wraps below the previous value, so '5000000000' scans into uint32_t as 705032704, '30000000000000000000' into uint64_t as 11553255926290448384 and hex '1FFFFFFFFFFFFFFFF' as 0xFFFFFFFFFFFFFFFF (about 75% of 10-digit values above UINT32_MAX accepted; signed paths hit overflow UB; unit tests try only max+1 and max\*10); benchmark inputs are in range, so the measured rows are unchanged. No float scanning; formatting (Dragon4) is self-reported 1.5-2x slower than fmt.

Targets bare-metal and RTOS embedded systems: no exceptions (returns emio::result), works without heap, about 5 kBytes versus 191 kBytes of flash for fmt on a one-line format (38 times smaller, per DESIGN.md). Supports fewer features than fmt. C++20 required (GCC 11-13, Clang 16-17 tested). Library is labelled beta.

## Maintenance

Active but slow-moving beta (last commit 2026-08-26 after a 13-month gap, all recent commits by the author), MIT and header-only so easy to vendor; its scan integer overflow check is incomplete (unreported), so range-check untrusted input yourself.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** docs/DESIGN.md (Performance section) gives one first-party prose figure, scanning 'around twice as fast then scanf', and points to the CI benchmark run; the benchmark code is public (test/benchmark/bench_scan.cpp, Catch2 BENCHMARK vs sscanf) but no compiler, flags or CPU are tied to the figure and no results are committed, so it cannot reach A or B.
- **Verifier notes:** Real entry, record accurate; keep at tier C. Shortcomings: prose-only 2x claim with no stated compiler/flags/CPU, CI benchmark output not committed and run in both Debug and Release, sscanf rows mislabelled 'snprintf' in bench_scan.cpp, formatting is slower than fmt. Metadata checked: MIT, 189 stars, not a fork, not archived, last commit 2026-08-26 (active), Conan Center badge in README.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** first-party DESIGN.md (verifier); enricher code reading
- **Pages the verifier opened:**
  - <https://github.com/Viatorus/emio>
  - <https://github.com/Viatorus/emio/commits/main.atom>
  - <https://raw.githubusercontent.com/Viatorus/emio/HEAD/docs/DESIGN.md>
  - <https://raw.githubusercontent.com/Viatorus/emio/HEAD/README.md>
  - <https://raw.githubusercontent.com/Viatorus/emio/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/Viatorus/emio/HEAD/test/benchmark/bench_scan.cpp>
  - <https://raw.githubusercontent.com/Viatorus/emio/HEAD/test/benchmark/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Viatorus/emio/HEAD/.github/workflows/ci.yml>
  - <https://raw.githubusercontent.com/Viatorus/emio/HEAD/CMakePresets.json>
- **Sources the enricher read:**
  - <https://github.com/Viatorus/emio>
  - <https://github.com/Viatorus/emio/commits/main>
  - <https://github.com/Viatorus/emio/issues?q=is%3Aissue>
  - <https://github.com/Viatorus/emio/issues?q=is%3Aissue+is%3Aclosed>
  - <https://github.com/Viatorus/emio/issues/6>
  - <https://raw.githubusercontent.com/Viatorus/emio/HEAD/README.md>
  - <https://raw.githubusercontent.com/Viatorus/emio/HEAD/docs/DESIGN.md>
  - <https://raw.githubusercontent.com/Viatorus/emio/HEAD/docs/API.md>
  - <https://raw.githubusercontent.com/Viatorus/emio/HEAD/test/benchmark/bench_scan.cpp>
  - <https://raw.githubusercontent.com/Viatorus/emio/HEAD/test/benchmark/bench_format.cpp>
  - <https://raw.githubusercontent.com/Viatorus/emio/HEAD/test/benchmark/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Viatorus/emio/HEAD/.github/workflows/ci.yml>
  - <https://raw.githubusercontent.com/Viatorus/emio/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Viatorus/emio/HEAD/CMakePresets.json>
  - <https://raw.githubusercontent.com/Viatorus/emio/HEAD/cmake/dev-mode.cmake>
  - <https://raw.githubusercontent.com/Viatorus/emio/HEAD/include/emio/emio.hpp>
  - <https://raw.githubusercontent.com/Viatorus/emio/HEAD/include/emio/scan.hpp>
  - <https://raw.githubusercontent.com/Viatorus/emio/HEAD/include/emio/scanner.hpp>
  - <https://raw.githubusercontent.com/Viatorus/emio/HEAD/include/emio/reader.hpp>
  - <https://raw.githubusercontent.com/Viatorus/emio/HEAD/include/emio/detail/conversion.hpp>
  - <https://raw.githubusercontent.com/Viatorus/emio/HEAD/include/emio/detail/predef.hpp>
  - <https://raw.githubusercontent.com/Viatorus/emio/HEAD/include/emio/detail/args.hpp>
  - <https://raw.githubusercontent.com/Viatorus/emio/HEAD/include/emio/detail/scan/scan_from.hpp>
  - <https://raw.githubusercontent.com/Viatorus/emio/HEAD/include/emio/detail/scan/parser.hpp>
  - <https://raw.githubusercontent.com/Viatorus/emio/HEAD/include/emio/detail/scan/scanner.hpp>
  - <https://raw.githubusercontent.com/Viatorus/emio/HEAD/include/emio/detail/scan/args.hpp>
  - <https://raw.githubusercontent.com/Viatorus/emio/HEAD/include/emio/detail/format/dragon.hpp>
  - <https://raw.githubusercontent.com/Viatorus/emio/HEAD/include/emio/detail/format/formatter.hpp>
  - <https://raw.githubusercontent.com/Viatorus/emio/HEAD/test/unit_test/test_scan.cpp>
  - <https://raw.githubusercontent.com/Viatorus/emio/HEAD/test/unit_test/test_reader.cpp>
  - <https://raw.githubusercontent.com/Viatorus/emio/HEAD/test/unit_test/integer_ranges.hpp>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/viatorus/emio`) · [data/wave1/enrich/raw/github_com_viatorus_emio.json](../../../data/wave1/enrich/raw/github_com_viatorus_emio.json) (enrichment confidence 0.75)

</details>
