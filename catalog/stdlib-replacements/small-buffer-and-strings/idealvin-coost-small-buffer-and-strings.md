# Coost fastring and fastream

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Small-buffer containers and strings](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `MIT` · 🟢 active

> coost v3's fastream (append-only text buffer) and fastring (heap string), claimed 10-30x faster than snprintf with no published harness.

| | |
|---|---|
| **Beats** | snprintf and std::ostringstream (fastream); std::string (fastring, benchmark code only, no published numbers) |
| **Claimed result** | fastream: 'about 10\~30 times faster than snprintf on different platforms'; the same page says std::ostringstream 'may be several times slower than snprintf' (coost v3 docs, first-party, no methodology). fastring: no numbers against std::string anywhere found. |
| **Workload** | Unstated. fastream is an append-only char stream meant to replace std::ostringstream/snprintf for building strings (its number formatting uses coost's fast::u64toa/u64toh/dtoa, which v3.0.2 test/fast.cc times against snprintf with no published results). fastring/co::string vs std::string assign and find micro-benchmarks exist as code only (v3.0.2 test/str.cc, master benchmark/string.cc). |
| **Metric** | throughput |
| **Adoption** | 4.2k stars |
| **Last commit** | 2026-09-28 |
| **Links** | [repository](https://github.com/idealvin/coost) · [benchmark](https://raw.githubusercontent.com/coostdocs/coostdocs.github.io/deb7584c3a15d214821ce8eac64eb5e48b38f5f4/en/co/other/fastream/index.html) |

## Verdict

The only number is a first-party docs sentence (coost v3 docs, archived at coostdocs commit deb7584; the Chinese page says it was measured) that fastream is about 10-30x faster than snprintf across platforms and that std::ostringstream is several times slower than snprintf; no workload, compiler, flags, CPU or table accompanies it and no harness in any branch times fastream itself. fastring against std::string has benchmark code (v3.0.2 test/str.cc, master benchmark/string.cc) with no published results, and the code has the degenerate-input flaw noted above.

## Use it when

- Maintaining code already on coost v3 (its log, json and flag modules use fastream/fastring internally) where switching to std::ostringstream would add overhead.
- Hot paths that concatenate integers, pointers, booleans and short strings into a reusable buffer (log lines, keys, protocol text) and can tolerate shortest-or-truncated float output.
- Builds limited to C++11 (gcc 4.8+, clang 3.3+, VS2015+) that still want allocation-light string building without pulling in {fmt}.
- Single-threaded or thread-local buffers that are cleared and reused, so the 1.5x growth and in-place realloc amortise to near-zero allocations.

## Skip it when

- New code: fastring.h and fastream.h no longer exist after coost v4.0.0 (2026-09-15); use co::string from v4, or {fmt}/std::to_chars outside coost.
- Many small, short-lived strings: fastring has no small-string optimization (issue #282, closed in May 2025 without SSO; v4 co::string keeps the same three-field layout), so every non-empty string is a heap allocation where std::string would use its inline buffer.
- Output that must match printf or iostream formatting: fastream &lt;&lt; double prints at most 6 decimal places by truncation, not rounding (issue #333: dp::_n(3.14159265, 4) prints 3.1415; maintainer: rounding is not considered), and there is no width, padding, precision or hex manipulator.
- Generic code that expects a std::string-shaped type: no begin()/end() iterators, no insert/erase/at, no allocator template parameter, char only.
- Projects that want a standalone header: both classes need coost's compiled fast.cc, fastring.cc and mem.cc and its global allocator.

## How it is fast

There is no locale, no virtual streambuf and no format-string parsing: operator&lt;&lt; appends straight into a contiguous buffer that grows by 1.5x through co::realloc, which can extend a block in place inside coost's thread-local slab allocator (blocks up to 2048 bytes in 16-byte units, sized free). Integers go through a 10,000-entry table of pre-rendered 4-digit ASCII groups whose first byte also encodes the digit count, so a 64-bit value needs at most four divide-by-10000 steps and five table loads; pointers and hex use a 256-entry byte-to-two-hex-digits table; doubles use Milo Yip's Grisu2 dtoa (the RapidJSON one). fastring::find uses memchr for the first byte and then Eric Blake's Two-Way substring search.

## Compared with alternatives

Only when you are already inside coost v3; for formatting numbers into fixed buffers to_static_string (std::to_chars-based, with published numbers) or MengRao/str are cleaner standalone choices, and for a faster std::string replacement EASTL string or FastString publish actual measurements against std::string while fastring publishes none and lacks SSO.

## Integration

| | |
|---|---|
| **Form** | static lib (libco from coost v3.0.2; xmake or CMake, also vcpkg and conan); v4 replaces it with co::string |
| **Dependencies** | coost core: fast.h/fast.cc (integer and hex tables, Grisu2 dtoa), mem.h/mem.cc (co::alloc thread-local allocator), god.h, murmur hash for std::hash&lt;fastring&gt;, fastring.cc (memmem, trim, replace) |
| **Minimum toolchain** | C++11 (README: gcc 4.8+, clang 3.3+, Visual Studio 2015+); default xmake builds use -O2 ("faster"), benchmark targets -O3 |
| **Platforms** | Linux, macOS, Windows (CI badges for all three in v3.0.2); 32- and 64-bit |
| **Thread safety** | Same as std::string: no shared state between copies (reference counting was removed in July 2020 after issue #59); concurrent mutation of one object needs external locking. |
| **Drop-in for the baseline** | partial — fastream covers ostringstream's operator&lt;&lt; for built-in types but is move-only and has no manipulators or locale; fastring mirrors much of std::string's search and compare API but lacks iterators, insert/erase, SSO and allocator customization |

## Gotchas

- Harness flaw: no code backs the '10\~30 times faster than snprintf' sentence. The only snprintf comparison in the repo (v3.0.2 test/fast.cc) times the bare u64toa/u64toh/dtoa primitives, not fastream; its default range 1000..9999 keeps every integer at four digits, so u64toa only ever takes its single-table-lookup branch, and dtoa (shortest round-trip, Grisu2) is timed against snprintf("%.7g") on the single value 3.14159, i.e. different output contracts. No results are published.
- Harness flaw in the fastring-vs-std::string code (v3.0.2 test/str.cc): the 'ss = ss.c_str() + 1' case starts from an 8,191-character string, but co's benchmark macro runs one warm-up call and then 100,000 iterations for any body under 1 microsecond, so after 8,191 iterations both strings are empty and over 90% of the timed iterations assign an empty string; the harness also times a single batch with no repetition and BM_use is an empty out-of-line call placed after the timed loop. master benchmark/string.cc (co::string) has the same shape and also publishes nothing.
- append(uint16), append(uint32) and append(uint64) on fastream/fastring append the raw binary bytes, not decimal text; use operator&lt;&lt; or cat() for text.
- fast::i32toa/i64toa negate the value before converting, which is signed-overflow undefined behaviour for INT32_MIN/INT64_MIN (works on common two's-complement builds, but not guaranteed under optimisation).

## Known shortcomings

- Raised D to C on the old coost v3 docs (coostdocs history, commit deb7584): fastream 'about 10-30 times faster than snprintf' and std::ostringstream 'several times slower than snprintf', first-party with no workload, compiler, flags, CPU or table; the baseline is snprintf/std::ostringstream, not std::string (baseline_in_list false); fastring vs std::string has benchmark code only (v3.0.2 test/str.cc, master benchmark/string.cc) with no results. Both headers were removed in v4.0.0 (2026-09-15) in favour of co::string, and current docs make no performance claim.
- Enricher: no code backs the '10\~30x faster than snprintf' claim (v3.0.2 test/fast.cc times only the u64toa/u64toh/dtoa primitives with a default 1000..9999 range that keeps every input at 4 digits so u64toa takes its single-table-lookup branch, and dtoa (Grisu2 shortest) is timed against snprintf "%.7g" on one value with different output); test/str.cc's ss = ss.c_str()+1 starts from 8191 chars while the co bench macro runs 100,000 iterations, so over 90% of timed iterations assign an empty string, one batch, no repetition, no published results; no SSO (#282); &lt;&lt; double truncates to 6 places (#333); append(uint32) appends raw bytes; INT_MIN negation is UB; no iterators, insert or erase; both headers removed in v4.0.0. Retiered to D.

## Caveats and trade-offs

Only number is the coost v3 docs sentence '10\~30 times faster than snprintf on different platforms' (first-party, no workload, compiler, flags, CPU or table); it is gone from the current docs, which were rewritten for coost v4 (Sep-Oct 2026) and make no performance claim for co::string. No published fastream benchmark against snprintf or std::ostringstream was found (v3.0.2 test/fast.cc only times the u64toa/u64toh/dtoa primitives against snprintf; the benchmark branch has only json_bm.cc and log_bm.cc). fastring has no numbers against std::string; v3.0.2 test/str.cc and master benchmark/string.cc (std::string vs co::string assign and find) publish no results. fastring.h and fastream.h were removed in v4.0.0 (2026-09-15; raw fetch at HEAD returns 404) and exist only up to tag v3.0.2 (2023-11-23); master has co::string in include/co/string.h, which uses coost's own allocator. Not standalone headers: they depend on coost's fast.h and memory allocator.

fastring is not a drop-in std::string: it derives from a fast::stream byte buffer and relies on coost's own memory allocator; coost issue #282 (2022) notes there is no small string optimization, so small strings may be slower than std::string with the default allocator; the maintainer said SSO may be considered later and the issue was closed in May 2025 without numbers. Pulls in the rest of the coost library headers.

## Maintenance

coost is actively maintained (MIT, last commit 2026-09-28, tag v4.0.1), but fastream and fastring themselves are retired: they exist only up to tag v3.0.2 and their successor co::string has no performance claim, so treat this entry as historical and vendorable only together with coost's allocator and number-conversion code.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification D, tier now D.
- **Tier reason:** Upgraded D to C: the coost v3 docs (archived in the coostdocs/coostdocs.github.io repo at commit deb7584, Mar 2024, pages en/co/other/fastream/ and cn/co/other/fastream/) state that fastream is 'about 10\~30 times faster than snprintf on different platforms' and that std::ostringstream 'may be several times slower than snprintf' (the Chinese page says measured). That is a first-party number with no workload, compiler, flags, CPU or results table; fastring itself has benchmark code against std::string (v3.0.2 test/str.cc, master benchmark/string.cc) but no published numbers.
- **Retiered** C to D: Enricher (2026-10-12): no measurement supports the fastring/fastream claim. v3.0.2 test/fast.cc times only the u64toa/u64toh/dtoa primitives (4-digit inputs on the single-table-lookup branch; dtoa against snprintf %.7g on one value with different output), and test/str.cc assigns an empty string in over 90% of its 100,000 timed iterations; no published results, no repetition. No valid measurement.
- **Verifier notes:** Record's 'no numbers anywhere' was wrong: the v3 docs (reachable via raw.githubusercontent.com on the coostdocs/coostdocs.github.io repo history, since \*.github.io is blocked) claim fastream is 10\~30x faster than snprintf, so tier moves D to C, but the baseline is snprintf/std::ostringstream rather than the category's std::string, and fastring vs std::string has code but no numbers. The components were removed in coost v4.0.0 (replaced by co::string), so the lead is historical; metadata checked: MIT (LICENSE.md), 4.2k stars, not a fork, not archived, last commit 2026-09-28 (tag v4.0.1). Same repo already listed for co/json and co/log (separate ids), not a duplicate of those.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `baseline`, `baseline_in_list`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-72 (wave 1, stdlib decomposition); enricher (wave 1 stdlib seeds, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/idealvin/coost>
  - <https://github.com/idealvin/coost/commits>
  - <https://github.com/idealvin/coost/tags>
  - <https://github.com/idealvin/coost/tree/v3.0.2/test>
  - <https://github.com/idealvin/coost/tree/v3.0.2/benchmark>
  - <https://github.com/idealvin/coost/tree/benchmark>
  - <https://github.com/idealvin/coost/tree/benchmark/benchmark>
  - <https://raw.githubusercontent.com/idealvin/coost/HEAD/readme.md>
  - <https://raw.githubusercontent.com/idealvin/coost/HEAD/readme_cn.md>
  - <https://raw.githubusercontent.com/idealvin/coost/v3.0.2/readme.md>
  - <https://raw.githubusercontent.com/idealvin/coost/v3.0.2/readme_cn.md>
  - <https://raw.githubusercontent.com/idealvin/coost/v3.0.1/readme.md>
  - <https://raw.githubusercontent.com/idealvin/coost/HEAD/benchmark/string.cc>
  - <https://raw.githubusercontent.com/idealvin/coost/HEAD/include/co/string.h>
  - <https://raw.githubusercontent.com/idealvin/coost/HEAD/include/co/fastring.h>
  - <https://raw.githubusercontent.com/idealvin/coost/HEAD/include/co/fastream.h>
  - <https://raw.githubusercontent.com/idealvin/coost/HEAD/LICENSE.md>
  - <https://raw.githubusercontent.com/idealvin/coost/v3.0.2/include/co/fastring.h>
  - <https://raw.githubusercontent.com/idealvin/coost/v3.0.2/include/co/fastream.h>
  - <https://raw.githubusercontent.com/idealvin/coost/v3.0.2/test/fast.cc>
  - <https://raw.githubusercontent.com/idealvin/coost/v3.0.2/test/str.cc>
  - <https://github.com/coostdocs/coostdocs.github.io>
  - <https://github.com/coostdocs/coostdocs.github.io/commits/main>
  - <https://raw.githubusercontent.com/coostdocs/coostdocs.github.io/main/en/co/string/index.html>
  - <https://raw.githubusercontent.com/coostdocs/coostdocs.github.io/deb7584c3a15d214821ce8eac64eb5e48b38f5f4/en/co/other/fastream/index.html>
  - <https://raw.githubusercontent.com/coostdocs/coostdocs.github.io/deb7584c3a15d214821ce8eac64eb5e48b38f5f4/cn/co/other/fastream/index.html>
  - <https://raw.githubusercontent.com/coostdocs/coostdocs.github.io/deb7584c3a15d214821ce8eac64eb5e48b38f5f4/en/co/other/fastring/index.html>
  - <https://raw.githubusercontent.com/coostdocs/coostdocs.github.io/deb7584c3a15d214821ce8eac64eb5e48b38f5f4/en/co/benchmark/index.html>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/idealvin/coost/v3.0.2/include/co/fastring.h>
  - <https://raw.githubusercontent.com/idealvin/coost/v3.0.2/include/co/fastream.h>
  - <https://raw.githubusercontent.com/idealvin/coost/v3.0.2/include/co/fast.h>
  - <https://raw.githubusercontent.com/idealvin/coost/v3.0.2/include/co/def.h>
  - <https://raw.githubusercontent.com/idealvin/coost/v3.0.2/include/co/mem.h>
  - <https://raw.githubusercontent.com/idealvin/coost/v3.0.2/include/co/god.h>
  - <https://raw.githubusercontent.com/idealvin/coost/v3.0.2/include/co/str.h>
  - <https://raw.githubusercontent.com/idealvin/coost/v3.0.2/include/co/benchmark.h>
  - <https://raw.githubusercontent.com/idealvin/coost/v3.0.2/include/co/__/dtoa_milo.h>
  - <https://raw.githubusercontent.com/idealvin/coost/v3.0.2/src/fast.cc>
  - <https://raw.githubusercontent.com/idealvin/coost/v3.0.2/src/fastring.cc>
  - <https://raw.githubusercontent.com/idealvin/coost/v3.0.2/src/two_way.h>
  - <https://raw.githubusercontent.com/idealvin/coost/v3.0.2/src/str.cc>
  - <https://raw.githubusercontent.com/idealvin/coost/v3.0.2/src/mem.cc>
  - <https://raw.githubusercontent.com/idealvin/coost/v3.0.2/src/benchmark.cc>
  - <https://raw.githubusercontent.com/idealvin/coost/v3.0.2/test/fast.cc>
  - <https://raw.githubusercontent.com/idealvin/coost/v3.0.2/test/str.cc>
  - <https://raw.githubusercontent.com/idealvin/coost/v3.0.2/xmake.lua>
  - <https://raw.githubusercontent.com/idealvin/coost/v3.0.2/readme.md>
  - <https://raw.githubusercontent.com/idealvin/coost/HEAD/include/co/string.h>
  - <https://raw.githubusercontent.com/idealvin/coost/HEAD/benchmark/string.cc>
  - <https://raw.githubusercontent.com/idealvin/coost/HEAD/include/co/fast.h>
  - <https://raw.githubusercontent.com/coostdocs/coostdocs.github.io/deb7584c3a15d214821ce8eac64eb5e48b38f5f4/en/co/other/fastream/index.html>
  - <https://raw.githubusercontent.com/coostdocs/coostdocs.github.io/deb7584c3a15d214821ce8eac64eb5e48b38f5f4/cn/co/other/fastream/index.html>
  - <https://raw.githubusercontent.com/coostdocs/coostdocs.github.io/deb7584c3a15d214821ce8eac64eb5e48b38f5f4/en/co/other/fastring/index.html>
  - <https://raw.githubusercontent.com/coostdocs/coostdocs.github.io/deb7584c3a15d214821ce8eac64eb5e48b38f5f4/en/co/benchmark/index.html>
  - <https://raw.githubusercontent.com/coostdocs/coostdocs.github.io/main/en/co/string/index.html>
  - <https://github.com/idealvin/coost/issues/282>
  - <https://github.com/idealvin/coost/issues?q=is%3Aissue+fastring>
  - <https://github.com/idealvin/coost/issues/333>
  - <https://github.com/idealvin/coost/issues/329>
  - <https://github.com/idealvin/coost/issues/59>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/idealvin/coost#small-buffer-and-strings`) · [data/wave1/enrich/raw/github_com_idealvin_coost_small_buffer_and_strings.json](../../../data/wave1/enrich/raw/github_com_idealvin_coost_small_buffer_and_strings.json) (enrichment confidence 0.75)

</details>
