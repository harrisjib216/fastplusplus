# Str (MengRao/str)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Small-buffer containers and strings](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Fixed-capacity char-array type with SIMD-accelerated equality, compare, and fixed-width integer/string conversion, beating std::string and stoi/to_string in author benchmarks.

| | |
|---|---|
| **Beats** | std::string, std::to_string/stoi |
| **Claimed result** | "2x faster than strncmp/memcmp or those of std::string" (comparisons); "10x faster than stoi/strtol/to_string/sprintf" (integer/float conversions) (verbatim from README) |
| **Workload** | Fixed-length string equality/comparison microbenchmarks, and integer/float parsing and formatting (fromi/toi) microbenchmarks, in the project's own bundled benchmark. |
| **Metric** | latency |
| **Compiler and flags** | g++ -march=native -O3 (benchmark/build.sh); GCC version not stated |
| **Adoption** | 127 stars |
| **Last commit** | 2021-07-04 |
| **Links** | [repository](https://github.com/MengRao/str) · [benchmark](https://github.com/MengRao/str) |

## Verdict

Author's own bundled microbenchmarks (benchmark/benchcmp.cc for comparisons, benchmark/benchnum.cc for conversions; built with g++ -march=native -O3, no compiler version or hardware stated) report Str's operator==/compare running about 2x faster than strncmp/memcmp/std::string equivalents, and fromi/toi running about 10x faster than stoi/strtol/to_string/sprintf for fixed-width numeric conversions. The README gives only these round numbers, with no result tables.

## Use it when

- Fixed-width string fields known at compile time (exchange/ticker symbols, FIX/ITCH-style protocol codes, instrument IDs)
- Hot-path equality/ordering comparisons of short (up to tens of bytes), fixed-length keys, e.g. market-data order-book keys
- Fixed-width, zero-padded decimal integer&lt;-&gt;string conversion where the exact digit width is known ahead of time (e.g. date/session codes)
- x86-64 targets that can build with -march=native or at least enable SSE4.1/AVX-512 to hit the accelerated code paths
- Low-latency code already avoiding heap allocation that wants a trivially-copyable POD string type usable as a map/hash key

## Skip it when

- Variable-length or arbitrary strings: Str has no resize/append/growth, its capacity is baked into the template parameter
- General integer parsing/formatting: fromi/toi require the number to fit exactly in SIZE zero-padded digits; no sign handling or variable width like stoi/to_string
- Non-x86 targets: Str.h includes &lt;x86intrin.h&gt; unconditionally, so it will not compile on ARM/aarch64
- Constructing Str from a C-string/buffer shorter than SIZE: the (const char\*) constructor does a raw SIZE-byte struct copy and can read past the source buffer
- Projects wanting upstream support: last commit 2021-07-04, single maintainer, 127 stars, no CI beyond the bundled benchmarks

## How it is fast

operator==/compare fold the array into 8-byte word comparisons and use __builtin_ctzll to locate the first differing byte, avoiding a per-byte loop, and switch to AVX-512 (VL+BW) masked byte compares (_mm512/256/128_cmpneq_epu8_mask) when the target supports it. fromi/toi convert between fixed-width, zero-padded decimal digits and integers using a branchless SIMD digit-pair multiply-add trick (SSE4.1 pmaddubsw/pmaddwd chain, citing arXiv:1902.08318 Fig.7) for 8/16-digit chunks, plus a precomputed 2-character lookup table for the remaining/non-SIMD path, replacing libc's division-per-digit stoi/to_string loop.

## Compared with alternatives

Pick Str over to_static_string/FastString/fstring/buffet when the field width is a known compile-time constant (fixed-width protocol/exchange codes) and you want the fastest possible equality/compare plus fixed-width numeric conversion via word-at-a-time/AVX-512 compare and SIMD digit conversion; for general resizable strings or variable-width number formatting, use one of those siblings instead.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (STL headers + x86 intrinsics only) |
| **Minimum toolchain** | C++11 minimum; C++17 only needed for tosv() (std::string_view). Benchmarks build with g++ -march=native -O3 (benchfindstr/benchfindint additionally add -std=c++17); GCC version not stated. |
| **Platforms** | x86-64 only (unconditionally includes &lt;x86intrin.h&gt;); AVX-512VL+AVX-512BW enable the SIMD compare path, SSE4.1 enables the SIMD toi/fromi path, otherwise a generic 8-byte-word fallback is used |
| **Thread safety** | not documented; Str itself is a stateless/POD char-array wrapper with no shared mutable state, so independent instances can be used concurrently, but this is not asserted anywhere in the docs |
| **Drop-in for the baseline** | no |

## Gotchas

- Str(const char\*) does a raw SIZE-byte struct copy (`*(const Str<SIZE>*)p`), which can read past the source buffer if it is shorter than SIZE — no null-termination or bounds checks
- fromi/toi require the value to fit exactly in SIZE zero-padded decimal digits (no sign, no variable width); correctness is only exercised via asserts in the author's own benchmark, not enforced by the header
- Which code path (and therefore the speedup) you get is decided at compile time by preprocessor macros (__AVX512VL__/__AVX512BW__/__SSE4_1__), so build flags like -march=native directly determine performance
- AlignSize is documented but not enforced: Str is not required to be aligned, but the README/header notes that aligning it speeds up comparisons

## Caveats and trade-offs

The README gives only round-number claims (2x, 10x), with no result tables, compiler version or hardware. Flags are available only from benchmark/build.sh (-march=native -O3). No commits since 2021-07-04. First-party numbers, not independently verified.

Str is a fixed maximum-length string type (template-parameterized capacity), not a resizable/dynamic string like std::string, so it is not a drop-in replacement; also ships an adaptive open-addressing hash table (StrHash) claiming 7x over std::unordered_map, which is out of scope for this category but shows the project's low-latency/trading-oriented design focus.

## Maintenance

Abandoned since 2021-07-04 (last commit), single maintainer, 127 stars, 2 open issues and no CI; MIT-licensed and small enough (single header) to vendor and freeze as-is.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The README gives the 2x (compare vs strncmp/memcmp/std::string) and 10x (fromi/toi vs stoi/strtol/to_string/sprintf) claims verbatim with no measured tables. Benchmark code is public (benchmark/benchcmp.cc, benchnum.cc, build.sh with g++ -march=native -O3), but there is no compiler version and no hardware, so this is C.
- **Verifier notes:** The README also claims StrHash is 7x faster than std::unordered_map (benchfindstr.cc, KRX option-code dataset), which may deserve its own hash-map entry. baseline_stdlib is left empty because build.sh uses g++ (likely libstdc++) but never names the platform. MIT, 127 stars, abandoned.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/MengRao/str>
  - <https://github.com/MengRao/str/tree/master/benchmark>
  - <https://github.com/MengRao/str/blob/master/benchmark/build.sh>
- **Sources the enricher read:**
  - <https://github.com/MengRao/str>
  - <https://github.com/MengRao/str/blob/master/Str.h>
  - <https://github.com/MengRao/str/blob/master/benchmark/build.sh>
  - <https://github.com/MengRao/str/blob/master/benchmark/benchcmp.cc>
  - <https://github.com/MengRao/str/blob/master/benchmark/benchnum.cc>
  - <https://github.com/MengRao/str/issues>
  - <https://github.com/MengRao/str/pulls>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/mengrao/str`) · [data/wave1/enrich/raw/github_com_mengrao_str.json](../../../data/wave1/enrich/raw/github_com_mengrao_str.json) (enrichment confidence 0.5)

</details>
