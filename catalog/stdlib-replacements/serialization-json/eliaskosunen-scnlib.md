# scnlib

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [JSON serialization](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Type-safe scanf/istream replacement; \~3-5x faster than std::stringstream and sscanf at parsing ints, floats, and words.

| | |
|---|---|
| **Beats** | std::stringstream / sscanf |
| **Claimed result** | Average ns, scn::scan vs std::stringstream vs sscanf: int 27.1 vs 85.5 vs 272.7; double 59.7 vs 283 vs 432; string word 24.5 vs 134 vs 58.4. That is \~3.2x (int), \~4.7x (double) and \~5.5x (string) faster than std::stringstream (derived from page data). The same tables show std::from_chars is faster than scn::scan (int 10.9 ns, double 23.0 ns). |
| **Workload** | Parsing an integer, a floating-point number, and a whitespace-delimited word/string from text input, comparing scn::scan to std::stringstream and libc sscanf |
| **Metric** | latency |
| **Hardware** | AMD Ryzen 7 5700X, Fedora 40, Linux kernel 6.8.9 |
| **Compiler and flags** | clang 18.1.1, -O3 -DNDEBUG -march=haswell, LTO enabled |
| **Adoption** | 1.3k stars |
| **Last commit** | 2025-10-29 |
| **Links** | [repository](https://github.com/eliaskosunen/scnlib) · [benchmark](https://github.com/eliaskosunen/scnlib) |

## Verdict

On an AMD Ryzen 7 5700X (Fedora 40, kernel 6.8.9), compiled with clang 18.1.1 at -O3 -DNDEBUG -march=haswell with LTO, scnlib's own in-repo benchmark suite (commit 3fd830de, run 2024-05-23) measured scn::scan averaging 27.1ns for int, 59.7ns for double, and 24.5ns for a whitespace-delimited string word, versus std::stringstream at 85.5ns/283ns/134ns and sscanf at 272.7ns/432ns/58.4ns — roughly 3.2x, 4.7x, and 5.5x faster than stringstream respectively. The same tables show std::from_chars (10.9ns int, 23.0ns double) and fast_float::from_chars beating scn::scan outright.

## Use it when

- Hot loops parsing many ints/doubles/whitespace-delimited words out of in-memory text (logs, config, simple text protocols) where stringstream or sscanf overhead shows up in profiles
- C++17+ codebases on GCC 7+/Clang 8+/MSVC 2019+ that can add a CMake dependency and rewrite the affected parsing call sites
- Code that wants compile-time-checked format strings instead of scanf's unchecked '%' format bugs
- Environments that disable exceptions/RTTI, since scnlib's core scanning path is usable without either
- Cross-platform targets beyond x86: ARM/AArch64, RISC-V, ppc64le, s390x are all CI-tested

## Skip it when

- Pure numeric conversion only (string-&gt;int/double, no whitespace/word handling) — std::from_chars and fast_float::from_chars both beat scn::scan outright (10.9ns/23.0ns vs 27.1ns/59.7ns for int/double in the README's own table)
- Projects that need a header-only drop-in — scnlib builds a library (source-drop with a src/scn/impl.cpp) and pulls in fast_float via CMake FetchContent by default
- Teams unwilling to learn scn's format-string semantics, which are evaluated left-to-right per-type and are explicitly not a regex/pattern language (documented FAQ gotcha)
- Code paths hit by open correctness issues: wrong result scanning from a std::deque-backed range (#144), a multi-value scan failing after a string value (#134), and floats with very large/small magnitude (#126) — check these against the version you'd pin before relying on them
- I/O-bound parsing (reading from disk/socket dominates), since the measured gains are for in-memory string parsing only, not end-to-end I/O latency

## How it is fast

It parses the format string once and dispatches straight to type-specialized scanning routines, avoiding stringstream's locale-aware state construction and sscanf's repeated format-string reparsing and whitespace-skipping (the README attributes \~400ns of sscanf's overhead to %n handling and whitespace skipping). Integer scanning has a stripped-down fast path (scn::scan_int, scn::scan_int_exhaustive_valid) and float scanning is built on the fast_float library (or std::from_chars) rather than a locale-aware strtod-style conversion. It also avoids RTTI and, in its core scanning path, exceptions (built with -fno-exceptions -fno-rtti in CI).

## Compared with alternatives

All the catalogued siblings (cjson.cpp, json.cpp, Cap'n Proto, DAW JSON Link, zpp::bits, Tachyon.JSON, utl::json, HPS) target structured JSON or binary (de)serialization; scnlib solves a different problem — unformatted, scanf/istream-style extraction of ints/floats/words from free text. Pick scnlib when the baseline you're replacing is std::stringstream/sscanf/operator&gt;&gt;, not when you're parsing or emitting JSON or a binary wire format.

## Integration

| | |
|---|---|
| **Form** | static lib (default; shared lib via BUILD_SHARED_LIBS=ON; a C++20 module target scn::module is also available via SCN_MODULES) |
| **Dependencies** | fast_float (fetched via CMake FetchContent by default; can be pointed at an external/vendored copy, or disabled with SCN_DISABLE_FAST_FLOAT to fall back to std::from_chars). GTest and Google Benchmark are pulled in only when building scnlib's own tests/benchmarks, not for library consumers. |
| **Minimum toolchain** | C++17; GCC 7+, Clang 8+, or Visual Studio 2019/2022 (CI-tested) |
| **Platforms** | Windows, Linux, macOS (14/15); x86, x86-64, arm, aarch64, riscv64, ppc64le, s390x, mips64le all CI-tested; 32- and 64-bit Windows, MinGW/MSYS2 also covered. One open issue reports test failures on OpenBSD (#155) and another a build failure against libc++ 23 (#159) |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | partial — same problem domain as scanf/istream (extracting typed values from text) but a different API: scn::scan returns values via a result object instead of scanf's output parameters or istream's operator&gt;&gt;, so existing call sites must be rewritten |

## Gotchas

- Format strings are not regexes or patterns: scn::scan&lt;std::string,std::string&gt;(input, "{},{}") does NOT stop the first field at the comma — each {} scans per its type's default rule (a string reads until whitespace), and the literal text between fields is matched and discarded separately; use "{:[^,]},{}" to stop at a comma (documented in the FAQ)
- Requires and assumes Unicode input (UTF-8, UTF-16, or UTF-32); behavior on non-Unicode/binary input is not something this session verified
- Not exception-free end-to-end: a custom Scanner's parse() can still throw scn::scan_format_string_error even though the core value-scanning path avoids exceptions/RTTI
- This is the reference implementation of an in-progress ISO C++ proposal (P1729 'Text Parsing'), so API surface may still shift across major versions

## Caveats and trade-offs

Numbers come from the project's own in-repo benchmark suite, run 2024-05-23 at commit 3fd830de; no third-party reproduction. The README does not say whether std::stringstream came from libstdc++ or libc++. scn::scan beats iostream and sscanf but loses to std::from_chars and fast_float::from_chars, and only roughly matches strtol (scn::scan_int).

Requires adopting scn's scan-based API instead of iostream/scanf idioms; adds a library/header dependency; format-string parsing has its own learning curve; gains are largest for CPU-bound parsing, smaller for I/O-bound workloads

## Maintenance

Actively maintained (latest master commit 2025-10-29, v4.0 docs current, ongoing releases and CI); Apache-2.0 and technically copyable, but it's a compiled library with a build step and a fast_float dependency, not a header you can just drop into a source tree.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** README Benchmarks tables compare scn::scan to std::stringstream and sscanf. The code is in the benchmark/ directory (CMake option SCN_BENCHMARKS), and the README states clang 18.1.1, -O3 -DNDEBUG -march=haswell with LTO, on an AMD Ryzen 7 5700X, so it meets A.
- **Verifier notes:** Every number matches the README. The record's last_commit (2026-09-23) was the repo's pushed_at; the latest commit on the default branch (master) is 2025-10-29, which still counts as active. The category 'serialization-json' does not fit a scanf/iostream replacement, but category is not a correctable field.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`, `last_commit`
- **Pages the verifier opened:**
  - <https://github.com/eliaskosunen/scnlib>
  - <https://github.com/eliaskosunen/scnlib/blob/master/README.md>
- **Sources the enricher read:**
  - <https://github.com/eliaskosunen/scnlib>
  - <https://github.com/eliaskosunen/scnlib/blob/master/README.md>
  - <https://github.com/eliaskosunen/scnlib/blob/master/cmake/dependencies.cmake>
  - <https://github.com/eliaskosunen/scnlib/blob/master/docs/pages/faq.md>
  - <https://github.com/eliaskosunen/scnlib/blob/master/docs/pages/guide.md>
  - <https://github.com/eliaskosunen/scnlib/blob/master/docs/pages/mainpage.md>
  - <https://github.com/eliaskosunen/scnlib/blob/master/include/scn/istream.h>
  - <https://github.com/eliaskosunen/scnlib/issues>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/eliaskosunen/scnlib`) · [data/wave1/enrich/raw/github_com_eliaskosunen_scnlib.json](../../../data/wave1/enrich/raw/github_com_eliaskosunen_scnlib.json) (enrichment confidence 0.85)

</details>
