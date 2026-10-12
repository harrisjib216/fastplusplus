# fpconv (night-shift)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Number parsing and formatting](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `BSL-1.0` · 🟡 stale

> Tiny Grisu2 C library converting doubles to shortest round-trip strings, \~10x faster than std::ostringstream.

| | |
|---|---|
| **Beats** | std::ostringstream (iostreams); page's headline ratio is vs sprintf() |
| **Claimed result** | 4.59x faster than sprintf() (verbatim, page's own Speedup column: fpconv 273.822ns vs sprintf 1256.376ns); \~10.1x faster than std::ostringstream (derived from page data: 273.822ns vs 2,778.748ns) |
| **Workload** | RandomDigit case: convert 1,000 random doubles (1-17 significant decimal digits) to shortest round-trippable ASCII string, min of 10 trials x100 iterations each. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7 920 @ 2.67GHz |
| **Compiler and flags** | Visual C++ 2013, Win64; release config via premake4 flags {"Optimize"} + NDEBUG (build/premake4.lua); literal compiler flags not stated |
| **Adoption** | 62 stars, 14 forks |
| **Last commit** | 2023-12-14 |
| **Links** | [repository](https://github.com/night-shift/fpconv) · [benchmark](https://github.com/miloyip/dtoa-benchmark) |

## Verdict

On the independent miloyip/dtoa-benchmark RandomDigit case (1,000 random doubles, 1-17 significant digits, min of 10 trials x100 iterations), fpconv converts in 273.822ns vs sprintf's 1,256.376ns (4.59x) and std::ostringstream's 2,778.748ns (\~10.1x, derived), measured with MSVC 2013 on Windows x64 on a Core i7-920 @2.67GHz.

## Use it when

- Hot-path double serialization (JSON/log/wire-format emitters) where sprintf/ostringstream formatting overhead shows up in profiles
- C or C++ code that can vendor a single .c/.h pair rather than pull in a library or link a header-only C++ template
- Need the shortest round-trippable string and don't care about scientific/fixed formatting control
- Pre-C++17 toolchains without &lt;charconv&gt;/std::to_chars available
- Embedded or size-constrained builds where a \~300-line, dependency-free source drop is preferable to a bigger conversion library

## Skip it when

- Need std::to_chars/from_chars-compatible API, or sprintf-style format control (precision, fixed vs scientific) - fpconv only emits shortest round-trip form
- Need string-to-double parsing too - fpconv is dtoa-only, no strtod-equivalent shipped
- Want active upstream maintenance - repo is stale (last commit Dec 2023), single maintainer, tiny community (62 stars, 14 forks)
- Vendoring an old/pinned copy predating the Dec 2023 fix: versions before that had a documented 24-byte buffer overflow on some large-magnitude doubles (e.g. -2^77), overflowing the buffer the header itself recommends
- Want benchmark evidence against a modern baseline - the only published numbers are vs VC2013 ostringstream/sprintf on a 2009 Core i7-920, not vs std::to_chars

## How it is fast

Implements Fabian Loitsch's Grisu2 algorithm: the double's mantissa/exponent are converted to a 64-bit fixed-point `Fp` struct, scaled into a normalized range using a precomputed table of 87 power-of-ten cache constants (powers.h), and digits are generated directly via integer division against upper/lower boundary intervals (`generate_digits`/`round_digit`). This avoids the arbitrary-precision bignum arithmetic and locale/format-flag machinery that `sprintf`/`ostringstream` pay for, at the cost of Grisu2 occasionally emitting one digit more than the true shortest form (unlike Grisu3/Ryu, which always find the minimal digit count).

## Compared with alternatives

On the same dtoa-benchmark page, both milo Grisu2 (138.021ns) and google/double-conversion (201.645ns) beat fpconv (273.822ns) outright, so pick this over them only when you specifically want a minimal plain-C .c/.h pair to vendor rather than a header-only C++ template (milo) or a heavier C++ library with a bignum fallback path (double-conversion); pick Boost.Charconv, c4core, or rigtorp/CharConv instead if you want a std::to_chars-shaped API.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (only C stdlib headers: stdbool.h, string.h, stdint.h) |
| **Minimum toolchain** | not documented; plain C99 (uses stdbool.h/stdint.h), no CMake or version pin in the repo |
| **Platforms** | any platform with IEEE-754 doubles; pure C with no SIMD/intrinsics, bit access via a union type-pun |
| **Thread safety** | not documented, but appears reentrant: fpconv.c and powers.h contain no mutable global/static state, only a read-only power-of-ten table and stack locals |
| **Drop-in for the baseline** | partial — different function signature than std::to_string/ostringstream/sprintf, caller must adapt the call site, and the output buffer is not null-terminated |

## Gotchas

- Pre-Dec-2023 snapshots overflow the documented 24-byte buffer for some large-magnitude values (GitHub issue #5, e.g. -2^77); fixed in the same commit recorded as last_commit (2023-12-14), so only affects older vendored copies
- Output is not null-terminated; caller must track and use the returned length
- Grisu2 can emit one extra digit versus the true shortest representation in rare cases (no Grisu3/Ryu fallback)
- Repo also bundles an unmaintained D port (fpconv_ctfe.d); it is not covered by the same fix history as the C code

## Caveats and trade-offs

Same aged hardware (Core i7 920) and compiler (VC++2013) as the shootout this is harvested from; no explicit optimizer flags stated, capping this at Tier B; small, low-activity project (62 stars).

Tiny single .c/.h pair (Grisu2 algorithm), easy to vendor; repo also bundles an unmaintained D port; Grisu2 is not a fully-optimal algorithm (unlike Grisu3/Ryu/Schubfach) so in rare cases output is one digit longer than the true shortest representation.

## Maintenance

Stale since its last commit in December 2023 (which was also the fix for the buffer-overflow bug) with a small community (62 stars, 14 forks), but it's a two-file BSL-1.0 source drop small enough to read end-to-end and vendor with confidence.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification B, tier now B.
- **Tier reason:** In the independent, well-known miloyip/dtoa-benchmark README, the fpconv row reads 273.822 ns (4.59x vs sprintf) and the ostringstream row reads 2,778.748 ns, so the derived \~10.1x is correct. Code is public and the compiler and CPU are stated, but literal compiler flags are not (build/premake4.lua only has a release config with premake flags {"Optimize"}), so not A.
- **Verifier notes:** Metadata checks out: BSL-1.0, 62 stars, 14 forks, last commit 2023-12-14 (stale), not a fork, not archived. The README results header wrongly says 'sequential ... u32toa()' (copy-paste from itoa-benchmark), but the table and charts are the RandomDigit dtoa case.
- **Fields the verifier corrected:** `compiler_and_flags`
- **Pages the verifier opened:**
  - <https://github.com/miloyip/dtoa-benchmark>
  - <https://github.com/miloyip/dtoa-benchmark/blob/master/build/premake4.lua>
  - <https://github.com/night-shift/fpconv>
- **Sources the enricher read:**
  - <https://github.com/night-shift/fpconv>
  - <https://github.com/night-shift/fpconv/blob/master/README.md>
  - <https://github.com/night-shift/fpconv/blob/master/src/fpconv.h>
  - <https://github.com/night-shift/fpconv/blob/master/src/fpconv.c>
  - <https://github.com/night-shift/fpconv/blob/master/src/powers.h>
  - <https://github.com/night-shift/fpconv/blob/master/license>
  - <https://github.com/night-shift/fpconv/issues/5>
  - <https://github.com/miloyip/dtoa-benchmark>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/night-shift/fpconv`) · [data/wave1/enrich/raw/github_com_night_shift_fpconv.json](../../../data/wave1/enrich/raw/github_com_night_shift_fpconv.json) (enrichment confidence 0.72)

</details>
