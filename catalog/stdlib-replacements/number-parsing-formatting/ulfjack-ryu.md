# Ryu

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Number parsing and formatting](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `Apache-2.0 OR BSL-1.0` · 🟢 active

> Shortest round-trip float/double-to-string conversion beating sprintf, plus a faster %f/%e printf replacement.

| | |
|---|---|
| **Beats** | printf (sprintf) |
| **Claimed result** | 16.164x faster than sprintf per double (46.07ns vs 744.72ns), directly stated in the benchmark table |
| **Workload** | Converting each of a 1.7M-value pool of random doubles (reduced to 1-17 significant digits) to a shortest round-trip decimal string via Ryu's d2s_buffered vs. C sprintf("%.17g", value), measured with Google Benchmark; mean time per conversion. |
| **Metric** | latency |
| **Hardware** | MacBook Pro (Apple M1 Pro) |
| **Compiler and flags** | Apple clang version 21.0.0 (clang-2100.0.123.102); CMake default Release build type (CMakeLists.txt sets CMAKE_BUILD_TYPE=Release for optimized code; exact -O flag not printed in the results table itself) |
| **Adoption** | 1.4k stars; ported to Rust (dtolnay/ryu), Go, Julia (in the Julia standard library), Zig, C#, D, Scala, Erlang/OTP, Haskell bytestring; algorithm published in peer-reviewed PLDI'18 and OOPSLA'19 papers |
| **Last commit** | 2026-02-09 |
| **Links** | [repository](https://github.com/ulfjack/ryu) · [benchmark](https://github.com/fmtlib/dtoa-benchmark) |

## Verdict

The independent fmtlib/dtoa-benchmark (Google Benchmark, Apple clang 21.0.0, CMake Release build, Apple M1 Pro) measured Ryu's d2s_buffered at 46.07ns/double mean vs C sprintf("%.17g", value) at 744.72ns — 16.164x faster — across a mixed 1.7M-value pool of doubles at 1-17 significant digits; the same table puts std::to_chars (libc++) at 51.35ns, only about 1.11x slower than Ryu.

## Use it when

- Hot paths serializing large volumes of doubles to text (JSON/CSV emitters, log lines, time-series export) where sprintf/ostringstream latency shows up in profiles.
- Need shortest round-trip decimal output (like Python repr or JS Number.toString) rather than a fixed %.17g dump.
- C/C++ codebase that can vendor a small, dependency-free source tree (CMake 3.10+ or Bazel build, no external libs).
- Want %f/%e output several times faster than platform printf while matching its rounding, and can live without other printf flags.
- Targeting x86-64/aarch64, or another platform where float and integer types share endianness; the hand-tuned fast paths cover 32/64-bit float/double.

## Skip it when

- Need full printf flag support (%g, width, padding, +, #) — Ryu Printf only implements %f/%e precision, not the full spec.
- Formatting mostly small-integer-valued doubles (counters, sensor readings) — issue #144 reports Ryu \~1.5-2x slower than double-conversion there; no built-in integer fast path.
- Need fast long double/__float128 conversion — only a slower generic 128-bit fallback exists for those widths, and it isn't available on MSVC (needs __uint128_t).
- Need a documented safe output-buffer-size constant before calling \*_buffered — issue #149 (open) notes ryu.h has no #define for required buffer length.
- Want output identical to std::to_chars — the measured margin over libc++'s to_chars is only \~1.11x, and to_chars ships in the standard library with zero extra dependency.

## How it is fast

Ryu is a table-based shortest-decimal algorithm (successor to Dragon4/Grisu): fixed lookup tables of powers of 5 let it compute, without bignum arithmetic, the shortest decimal digit string whose rounding interval contains the original binary float in one pass. This avoids the double-rounding correctness checks and slow-path fallbacks that Grisu3-style algorithms need for hard cases. Ryu Printf reuses the same table machinery but is restricted to a fixed precision, letting it skip the general shortest-digit search entirely. Correctness for both is proven in peer-reviewed papers (PLDI'18, OOPSLA'19) rather than established only by fuzz testing.

## Compared with alternatives

Pick Ryu over Dragonbox when you want a plain-C implementation with the widest set of independent language ports to reference (Rust, Go, Julia stdlib, Erlang/OTP, etc.); Dragonbox is faster still on this same benchmark (25.7x vs sprintf and a direct win over Ryu) if closing that extra gap matters more than portability. Pick {fmt} instead if you're already pulling in a formatting/iostream-replacement library (it also uses Dragonbox internally) and want printf-style format strings rather than raw conversion functions.

## Integration

| | |
|---|---|
| **Form** | static lib (source-drop; CMake or Bazel build, no header-only mode) |
| **Dependencies** | none for the C core; CMake 3.10+ or Bazel 0.14+ to build; JDK 8+ only for the separate Java port |
| **Minimum toolchain** | C99 (uses stdint.h/inttypes.h); generic_128 (128-bit fallback) needs GCC/Clang/Intel for __uint128_t, not available on MSVC |
| **Platforms** | x86-64, aarch64, and other platforms where the float type and same-width integer type share endianness (README states big-endian works under that condition); CI covers Ubuntu 18.04, macOS, Windows Server 1803 |
| **Thread safety** | not documented by upstream; common.h/d2s.c use only static inline pure functions and const lookup tables with no mutable globals observed, so concurrent calls appear safe, but this is not an explicit upstream guarantee |
| **Drop-in for the baseline** | partial — explain: d2s_buffered_n covers the shortest-round-trip case sprintf can't directly express and always emits scientific notation rather than %g-style output; d2fixed/d2exp mimic %f/%e precision but implement no other printf flags, so it's not a full sprintf replacement. |

## Gotchas

- Ryu, Dragonbox, and Schubfach (per the fmtlib benchmark's own notes) always emit exponential notation in shortest mode, e.g. 0.1 -&gt; 1E-1, unlike %g's 0.1 — don't assume output matches sprintf's shortest-%g style.
- No documented #define for safe output buffer size (open issue #149); undersizing the buffer passed to a \*_buffered_n function is a real overflow risk.
- f2s (float32) shortest mode has at least one known incorrect-rounding case still open as of 2025 (#235: 2147483904 is formatted as 2.147484E9 instead of the exact value) — the d2s/double path used in this benchmark is a separate code path but this signals the algorithm's edge cases aren't all closed.
- Public C identifiers (d2s, f2s, d2s_buffered, etc.) are unprefixed (open issue #148) and can collide with other libraries' symbols when statically linked.

## Caveats and trade-offs

Ryu's own README gives Ryu Printf speedups against platform printf of 15x (glibc), 4x (musl), 9x (MSVC), 8-20x (msys) and 24x (Apple libc). It names no CPU, only OS/libc versions, so that first-party claim alone is Tier C. This record cites the independent fmtlib/dtoa-benchmark (compiler and CPU stated), which shows a 16.164x win over C sprintf for shortest d2s. Against std::to_chars (libc++), the margin is only \~1.11x (46.07 vs 51.35 ns, derived from page data). The results are a single hardware sample (Apple M1 Pro), and the Release build config comes from CMakeLists.txt. Licensing: all code is Apache-2.0, and files in ryu/ may also be used under BSL-1.0.

C implementation (plus a Java port); the highly optimized paths only cover 32/64-bit float/double, with a slower generic 128-bit fallback for long double/__float128; Ryu Printf only implements %f/%e precision formatting, not the full printf flag set.

## Maintenance

Actively maintained (last commit 2026-02-09, \~1.4k stars) under dual Apache-2.0/BSL-1.0 licensing, so it's copyable under either regime; the algorithm has been ported into a dozen-plus languages and standard libraries (Rust, Go, Julia's stdlib, Erlang/OTP, etc.), a strong maturity signal despite a few still-open ergonomics/correctness issues (undocumented buffer size, an f32 shortest-mode rounding edge case).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): confirm; tier before verification A, tier now A.
- **Tier reason:** The fmtlib/dtoa-benchmark README table shows ryu 46.07 ns against sprintf 744.72 ns (16.164x), and to_chars 51.35 ns, on an Apple M1 Pro with Apple clang 21.0.0. The code is public (src/ryu-test.cc, src/sprintf-test.cc), and CMakeLists.txt pins the Release build type (-O3 -DNDEBUG).
- **Verifier notes:** The existing caveat overstated the Ryu README range as 15x-24x; the README table actually runs from 4x (musl) to 24x. The benchmark calls d2s_buffered_n (the README method table says d2s_buffered). Metadata checked: 1354 stars, last commit 2026-02-09, gh spdx Apache-2.0.
- **Fields the verifier corrected:** `caveats`
- **Pages the verifier opened:**
  - <https://github.com/fmtlib/dtoa-benchmark>
  - <https://github.com/fmtlib/dtoa-benchmark/blob/main/CMakeLists.txt>
  - <https://github.com/fmtlib/dtoa-benchmark/blob/main/src/ryu-test.cc>
  - <https://github.com/fmtlib/dtoa-benchmark/blob/main/src/sprintf-test.cc>
  - <https://github.com/ulfjack/ryu>
- **Sources the enricher read:**
  - <https://github.com/ulfjack/ryu>
  - <https://github.com/ulfjack/ryu/blob/master/README.md>
  - <https://github.com/ulfjack/ryu/blob/master/ryu/ryu.h>
  - <https://github.com/ulfjack/ryu/blob/master/CMakeLists.txt>
  - <https://github.com/ulfjack/ryu/blob/master/ryu/common.h>
  - <https://github.com/ulfjack/ryu/issues/149>
  - <https://github.com/ulfjack/ryu/issues/144>
  - <https://github.com/ulfjack/ryu/issues/235>
  - https://github.com/ulfjack/ryu/issues (search: bug, performance labels)
  - <https://github.com/fmtlib/dtoa-benchmark/blob/main/README.md>
- **Raw records:** [data/wave0-seed/verified.json](../../../data/wave0-seed/verified.json) (id `https://github.com/ulfjack/ryu`) · [data/wave0-seed/enrich/raw/github_com_ulfjack_ryu.json](../../../data/wave0-seed/enrich/raw/github_com_ulfjack_ryu.json) (enrichment confidence 0.85)

</details>
