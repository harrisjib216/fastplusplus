# Ada (WHATWG URL parser)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP parsers](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `Apache-2.0 OR MIT` · 🟢 active

> WHATWG-compliant C++20 URL parser used by Node.js; about 7.8x faster than libcurl's URL API on real-world URLs.

| | |
|---|---|
| **Beats** | libcurl URL parser |
| **Claimed result** | README, top100 dataset: ada 188 ns/URL vs servo url 664 ns/URL vs CURL 1471 ns/URL. That is about 7.8x faster than curl and 3.5x faster than servo rust-url (derived from page data). The README also quotes State of Node.js Performance 2023: after Node.js adopted Ada, 'Some results could reach up to an improvement of 400%'. The peer-reviewed paper reports Ada above 3M URLs/s (AMD EPYC 7262) and 5M URLs/s (Apple M2), against about 0.5M and nearly 1M URLs/s for curl. On top100 it needs 8x fewer instructions than curl. |
| **Workload** | Validating and normalizing thousands of real-world URLs harvested from the top 100 popular websites (ada-url/url-various-datasets top100 corpus), measuring nanoseconds per URL. |
| **Metric** | throughput |
| **Hardware** | README: 'Apple MacBook 2022' with LLVM 14, chip not stated. The linked paper's Apple system is an Apple M2 3.0 GHz MacBook Air (2022) with Apple/LLVM 14, and it also tests an AMD EPYC 7262 (Zen 2, 3.4 GHz) with GCC 11. |
| **Compiler and flags** | README: LLVM 14, optimization flags not stated. Paper: GCC 11 (EPYC 7262) and Apple/LLVM 14 (M2), flags not stated. Ada's cmake/ada-flags.cmake defaults to CMAKE_BUILD_TYPE=Release when no build type is given. |
| **Adoption** | 1.85k stars; README names Node.js, Redpanda, Kong, Telegram, DataDog and Cloudflare Workers as users |
| **Last commit** | 2026-09-20 |
| **Links** | [repository](https://github.com/ada-url/ada) · [benchmark](https://github.com/ada-url/ada#readme) |

## Verdict

Ada's own Google Benchmark harness parses each URL in the top100 corpus and reads back the normalized href. The README reports 188 ns/URL for Ada, 664 for servo rust-url and 1471 for curl's `curl_url_set` + `curl_url_get`, on an 'Apple MacBook 2022' with LLVM 14 and unstated flags. The curl run reuses one handle but allocates the href string for every URL. The peer-reviewed paper shows the same gap on an AMD EPYC 7262 (GCC 11) and an Apple M2 (Apple/LLVM 14): above 3M and 5M URLs/s for Ada, against about 0.5M and nearly 1M for curl 7.81.0.

## Use it when

- Servers, proxies, crawlers or log pipelines that normalize or validate millions of URLs and want output identical to a browser's or Node's `new URL()`.
- Replacing a hot-path libcurl `CURLU` parse-plus-serialize step when WHATWG normalization (punycode hosts, percent-encoded paths) is acceptable or wanted.
- Validation-only filtering with `ada::can_parse`: the v4 release post reports 28.1 ns/URL on a \~100k-URL dataset (Apple M5 Max).
- Embedding a spec-compliant URL implementation in a JavaScript runtime or polyglot stack: Ada has a C API plus official Rust, Go, Python and Kotlin bindings.
- Route matching with URLPattern or the experimental URLPattern list, with the regex engine of your choice plugged in.

## Skip it when

- You need RFC 3986 behavior or byte-exact round-trips. Ada rewrites hosts to punycode and percent-encodes paths, and it accepts a different set of URLs from curl (on the top100 corpus, curl rejects 130 URLs and Ada 26).
- Your toolchain is older than C++20. The README lists GCC 12+, LLVM 14+ and Visual Studio 2022 as tested.
- Your input is not UTF-8 (UTF-16 or Latin-1 strings from a JS engine, for example). The code base assumes UTF-8, and issue #77 about other encodings is still open.
- Binary size is tight. An issue thread (#900) puts the compiled library at around 500 KB, mostly IDNA/Unicode tables. URLPattern can be turned off with `ADA_INCLUDE_URL_PATTERN=OFF`, but the maintainers say the Unicode support cannot be removed.
- You need HTTP request-line or header parsing. Ada only parses URLs.

## How it is fast

The default `url_aggregator` writes the normalized URL into one `std::string` and tracks the components as 32-bit offsets. The buffer is reserved up front, rounded to the next power of two, so getters return `string_view`s and do no allocation. A fast path (`try_parse_simple_absolute` / `try_parse_simple_relative`) skips the full WHATWG state machine for URLs that are already canonical. On main, that path classifies 16 bytes at a time with nibble-table lookups (SSSE3 `pshufb` / NEON `tbl`, with an SSE2 fallback). Elsewhere Ada uses vectorized tab/newline scans (SSSE3, NEON, SSE2, LoongArch LSX, RISC-V RVV, and a 64-bit SWAR fallback), 256-entry constexpr lookup tables for delimiters and forbidden host code points, and a branchless perfect hash to detect special schemes. The paper reports up to 8x fewer instructions than curl and 3x fewer than servo rust-url.

## Compared with alternatives

ada-rs (Rust) and lucid-url both benchmark against C++ Ada. They claim small wins on small corpora (7.4% on 9 URLs; 1.27x for Url but slower for UrlAggregator), and sorug is a Rust WHATWG parser measured only against servo url. Pick Ada when you need C/C++ integration, full web-platform-test compliance, fuzzing coverage and a production record (Node.js, Cloudflare Workers).

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (CMake, SOVERSION 4), or source-drop of the amalgamated ada.h + ada.cpp |
| **Dependencies** | none (simdutf is optional via ADA_USE_SIMDUTF; tests and benchmarks fetch their own dependencies through CPM) |
| **Minimum toolchain** | C++20; tested with GCC 12+, LLVM 14+ and MSVC 2022; CMake 3.16+ |
| **Platforms** | any C++20 target. SIMD paths: x86-64 (SSE2 baseline, SSSE3 scanners, optional AVX-512 BW/VL/VBMI2 IPv4 kernel chosen at compile time), aarch64 NEON, LoongArch LSX, RISC-V RVV, with a scalar SWAR fallback. CI covers Ubuntu x86-64 and ARM64, s390x and loongarch64 under QEMU, Windows MSVC/clang-cl, and macOS. |
| **Thread safety** | Not documented. `parse` is a free function that returns an owned value. The only global state found is the max-input-length limit, a relaxed `std::atomic` that applies to the whole process. Concurrent mutation of one URL object is not addressed. |
| **Drop-in for the baseline** | no |

## Gotchas

- `url_aggregator` getters return `string_view`s into the internal buffer, and any setter invalidates them. The header warns against passing a getter's result into a setter on the same object without copying it first. C API `ada_string` values are borrowed in the same way.
- Check the parse result before dereferencing it. The README calls `url->get_href()` on a failed parse unsafe.
- `ada::set_max_input_length` is process-wide. When the limit is exceeded, the `void` setters (`set_search`, `set_hash`) do nothing and give no signal.
- Release and main differ. v4.0.0 (2026-07-27) bumped SOVERSION to 4 and now rejects some inputs it used to accept. The README Quick Start still downloads v3.0.0 single-header files. The August 2026 SIMD fast-path work (PRs #1214/#1216) is on main only. On main, GCC/Clang x86-64 builds compile those scanners with `target("ssse3")`, and I found no runtime CPU check, so CPUs without SSSE3 may fault.

## Known shortcomings

- The August 2026 SIMD fast paths are on main only, compiled with target('ssse3') and no runtime CPU check (possible fault on pre-SSSE3 x86-64); the ideas came from a WebKit/Bun change that claims to beat Ada 4.0.0. The curl comparison has curl allocate an href per URL while Ada returns a view. README Quick Start still points at v3.0.0. UTF-8 input only; \~500 KB library, mostly IDNA tables.

## Caveats and trade-offs

The README benchmark is first-party. Hardware is given only as 'Apple MacBook 2022' with LLVM 14, and no flags are listed. It is backed by a peer-reviewed paper (Nizipli & Lemire, 'Parsing Millions of URLs per Second', Software: Practice and Experience 54(5), 2024, https://doi.org/10.1002/spe.3296) whose C++ results appear only as bar charts. The comparison is not like-for-like: curl follows RFC 3986, not WHATWG, and the paper warns 'direct comparisons must be done with care'. On top100, curl rejects 130 URLs versus 26 for Ada. The 400% Node.js figure is a Node 16-to-20 URL benchmark from a third-party blog post, not an isolated parser comparison.

URL parsing/validation only (not HTTP header/request-line parsing); WHATWG-URL-standard semantics differ subtly from RFC 3986 parsers, which can matter for strict compliance; requires C++20 compiler.

## Maintenance

Actively maintained: last commit 2026-09-20, v4.0.0 released 2026-07-27, with ABI-check CI and fuzzing in CI (CIFuzz plus past OSS-Fuzz reports). It is dual-licensed Apache-2.0/MIT and easy to vendor as two amalgamated files.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** The README bar chart (ada 188, servo url 664, CURL 1471 ns/URL, top100 dataset) is first-party and gives only 'Apple MacBook 2022 with LLVM 14', with no chip or flags. The peer-reviewed paper (Nizipli & Lemire, SPE 54(5) 2024, arXiv 2311.10533) shows Ada beating curl 7.81.0 and names the CPUs (AMD EPYC 7262, Apple M2) and compilers (GCC 11, Apple/LLVM 14). The paper's code is public (benchmarks/bench.cpp, benchdata target), but no optimization flags are stated, so the evidence is B, not A.
- **Verifier notes:** README numbers and the 400% Node.js quote are verified. The State of Node.js Performance 2023 post contains the 400% sentence. The ada_analysis raw Google Benchmark JSON for an Apple machine (overall/m2/top100.json: 3.4 GHz, curl 7.87.0) shows 239 ns/URL for ada (162 for url_aggregator) vs 1234 ns/URL for curl, which fits the README claim but is not the same run. ClickHouse, Adguard and Internet Archive were removed from usage: the README and ada-url.com do not list them, and ClickHouse's contrib/ has no ada. License is dual Apache-2.0/MIT (LICENSE-APACHE and LICENSE-MIT; README: 'Apache License 2.0 as well as the MIT license'). Last commit 2026-09-20; the repo is not a fork and not archived.
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `compiler_and_flags`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/ada-url/ada#readme>
  - <https://github.com/ada-url/ada>
  - <https://github.com/ada-url/ada/blob/main/benchmarks/CMakeLists.txt>
  - <https://github.com/ada-url/ada/blob/main/benchmarks/benchmark_template.cpp>
  - <https://github.com/ada-url/ada/blob/main/CMakeLists.txt>
  - <https://github.com/ada-url/ada/blob/main/cmake/ada-flags.cmake>
  - <https://arxiv.org/abs/2311.10533>
  - <https://arxiv.org/pdf/2311.10533>
  - <https://github.com/ada-url/ada_analysis>
  - <https://github.com/ada-url/ada_analysis/blob/main/overall/m2/top100.json>
  - <https://github.com/ada-url/ada_analysis/blob/main/overall/bigscript.sh>
  - <https://www.ada-url.com/>
  - <https://blog.rafaelgss.dev/state-of-nodejs-performance-2023>
  - <https://github.com/ClickHouse/ClickHouse/tree/master/contrib>
- **Sources the enricher read:**
  - <https://github.com/ada-url/ada>
  - <https://github.com/ada-url/ada#readme>
  - <https://github.com/ada-url/ada/blob/main/src/parser.cpp>
  - <https://github.com/ada-url/ada/blob/v4.0.0/src/parser.cpp>
  - <https://github.com/ada-url/ada/blob/main/src/unicode.cpp>
  - <https://github.com/ada-url/ada/blob/main/src/implementation.cpp>
  - <https://github.com/ada-url/ada/blob/main/src/checkers.cpp>
  - <https://github.com/ada-url/ada/blob/main/src/helpers.cpp>
  - <https://github.com/ada-url/ada/blob/main/include/ada/url_components.h>
  - <https://github.com/ada-url/ada/blob/main/include/ada/url_aggregator.h>
  - <https://github.com/ada-url/ada/blob/main/include/ada/implementation.h>
  - <https://github.com/ada-url/ada/blob/main/include/ada/common_defs.h>
  - <https://github.com/ada-url/ada/blob/main/include/ada/scheme-inl.h>
  - <https://github.com/ada-url/ada/blob/main/include/ada/checkers-inl.h>
  - <https://github.com/ada-url/ada/blob/main/include/ada/expected.h>
  - <https://github.com/ada-url/ada/blob/main/cmake/ada-flags.cmake>
  - <https://github.com/ada-url/ada/blob/main/CMakeLists.txt>
  - <https://github.com/ada-url/ada/blob/main/SECURITY.md>
  - <https://github.com/ada-url/ada/blob/main/benchmarks/benchmark_template.cpp>
  - <https://github.com/ada-url/ada/blob/main/.github/workflows/ubuntu.yml>
  - <https://github.com/ada-url/ada/blob/main/.github/workflows/abi-check.yml>
  - <https://github.com/ada-url/ada/blob/main/.github/workflows/windows.yml>
  - <https://github.com/ada-url/ada/blob/main/.github/workflows/macos.yml>
  - <https://github.com/ada-url/ada/issues/77>
  - <https://github.com/ada-url/ada/issues/640>
  - <https://github.com/ada-url/ada/issues/900>
  - <https://github.com/ada-url/ada/issues/970>
  - <https://github.com/ada-url/ada/issues/1076>
  - <https://github.com/ada-url/ada/pull/1214>
  - <https://github.com/ada-url/ada/pull/1216>
  - <https://github.com/ada-url/ada/releases/tag/v4.0.0>
  - <https://github.com/ada-url/ada/security/advisories>
  - <https://yagiz.co/release-of-ada-v4/>
  - <https://arxiv.org/abs/2311.10533>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/ada-url/ada`) · [data/wave5/enrich/raw/github_com_ada_url_ada.json](../../../data/wave5/enrich/raw/github_com_ada_url_ada.json) (enrichment confidence 0.85)

</details>
