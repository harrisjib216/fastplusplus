# Small-buffer containers and strings

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md)</sub>

**What these beat:** std::string, std::string_view, SSO  
**16 entries:** 1 tier A · 0 tier B · 12 tier C · 3 tier D · 14 copyable, 2 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**to_static_string**](anarthal-to-static-string.md) | Header-only C++17 wrapper over std::to_chars that returns a stack-based string, replacing allocating, locale-dependent std::to_string. | **A** | C++ | BSL-1.0 | 🟡 stale |
| 2 | [**EASTL string (eastl::basic_string / eastl::string…**](paper-eastl-string-fixed-string.md) | EA's non-COW, SSO basic_string and inline-buffer fixed_string; beat the VC++ 7.1 Dinkumware string on push_back and swap. | **C** | C++ | BSD-3-Clause | 🟢 active |
| 3 | [**bstring**](msteinert-bstring.md) | Maintained fork of Paul Hsieh's Bstrlib: length-prefixed, auto-growing C strings that avoid strcat-style rescans of char\* code. | **C** | C | BSD-3-Clause OR GPL-2.0-only | 🟢 active |
| 4 | [**fastcpp::small_vector (developer source)**](private-developer-source-small-buffer-and-strings.md) | C++ vector with N inline slots (default 8). It skips std::vector's heap allocation while the vector stays small. | **C** | C++ | MIT | 🟢 active |
| 5 | [**buffet**](alcover-buffet.md) | C buffer type with SSO and refcounted views beating std::string on append, but not on plain memcopy or views. | **C** | C | GPL-3.0 | 🟡 stale |
| 6 | [**FastString**](m3janitha-faststring.md) | Fixed-capacity, stack-allocated, constexpr string class that avoids the heap allocation std::string needs past SSO. | **C** | C++ | MIT | 🟡 stale |
| 7 | [**Pool-allocator string (Dicanio STL/ATL/Pool string…**](giovannidicanio-stringbenchmarkstlatlpool.md) | Fixed-chunk pool allocator for bulk wide-char strings, beating ATL CStringW and std::wstring on creation. | **C** | C++ | MIT | 🟡 stale |
| 8 | [**Bstrlib (The Better String Library)**](websnarf-bstrlib.md) | Paul Hsieh's original length-tracked C string library (plus CBString C++ wrapper) replacing string.h char\* handling. | **C** | C | BSD-3-Clause | 🔴 abandoned |
| 9 | [**shoco**](ed-von-schleck-shoco.md) | Tiny C entropy coder for short ASCII strings; first-party 2014 timings show about 2x smaz's speed on English words. | **C** | C | MIT | 🔴 abandoned |
| 10 | [**librope**](josephg-librope.md) | Two-file C99 skip-list UTF-8 rope with O(log n) insert/delete at character offsets; beats flat strings on large documents. | **C** | C | MIT | 🔴 abandoned |
| 11 | [**Str (MengRao/str)**](mengrao-str.md) | Fixed-capacity char-array type with SIMD-accelerated equality, compare, and fixed-width integer/string conversion, beating std::string and stoi/to_string in author… | **C** | C++ | MIT | 🔴 abandoned |
| 12 | [**zuu_string_view**](zuudevs-zuu-string-view.md) | Header-only C++11 SWAR-accelerated string_view alternative; faster find/rfind/find_first_of than std::string_view, slower on not_of scans. | **C** | C++ | no license (study only) | 🟢 active |
| 13 | [**Loki flex_string**](snaewe-loki-lib.md) | Alexandrescu's 2001 policy-based std::basic_string clone; only evidence is an anecdotal 5-10% Boost.Wave speedup. | **C** | C++ | MIT for the Loki library… (study only) | 🔴 abandoned |
| 14 | [**Coost fastring and fastream**](idealvin-coost-small-buffer-and-strings.md) | coost v3's fastream (append-only text buffer) and fastring (heap string), claimed 10-30x faster than snprintf with no published harness. | **D** | C++ | MIT | 🟢 active |
| 15 | [**jank persistent_string**](jank-lang-jank.md) | jank's built-in immutable string (jtl::immutable_string, backing persistent_string); claims to tie or beat std::string and folly::fbstring. | **D** | C++ | MPL-2.0 | 🟢 active |
| 16 | [**ETL fixed-capacity strings and algorithms (etl::string…**](etlcpp-etl-small-buffer-and-strings.md) | Heap-free fixed-capacity strings (etl::string&lt;N&gt;) and STL-style algorithms for embedded C++03+; no speed claim versus std::string or std::sort. | **D** | C++ | MIT | 🟢 active |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
