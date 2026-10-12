# stb_sprintf (nothings/stb)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Number parsing and formatting](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT OR Unlicense` · 🟢 active

> Single-header, public-domain sprintf/snprintf replacement claiming 4-35x faster formatting than MSVC 2008's CRT.

| | |
|---|---|
| **Beats** | sprintf/snprintf (C runtime, MSVC/GCC CRT) |
| **Claimed result** | Verbatim from stb_sprintf.h header comment ("PERFORMANCE vs MSVC 2008 32-/64-bit"): "%f" across e-10..e+10 floats 7.3x/6.0x faster; "%e" 8.1x/6.0x faster; "%g" 10.0x/7.1x faster; "%.320f" near e-300 12.6x/11.2x faster; "%d" across all 32-bit ints 4.8x/4.0x faster; "...512 char string..." 35.0x/32.5x faster; text also states GCC's CRT sprintf is "even slower than MSVC" but gives no GCC numbers. |
| **Workload** | Formatting microbenchmarks across %d/%x/%f/%e/%g/%a/%I64d and long strings, run against the platform C runtime's sprintf implementation. |
| **Metric** | throughput |
| **Compiler and flags** | MSVC 2008 (32-bit and 64-bit) as the comparison CRT; no optimization flags stated; GCC mentioned qualitatively only |
| **Adoption** | 34.7k stars for the stb collection; stb_sprintf.h is widely embedded in game engines and graphics codebases |
| **Last commit** | 2026-08-02 |
| **Links** | [repository](https://github.com/nothings/stb) · [benchmark](https://github.com/nothings/stb/blob/master/stb_sprintf.h) |

## Verdict

The library's own header (stb_sprintf.h, "PERFORMANCE vs MSVC 2008 32-/64-bit") reports first-party speedups against MSVC 2008's CRT sprintf, e.g. %f 7.3x/6.0x faster, %e 8.1x/6.0x, %g 10.0x/7.1x, %d 4.8x/4.0x, and a 512-char string format 35.0x/32.5x faster (32-bit/64-bit builds respectively); no CPU model, optimizer flags, or benchmark harness are given, and GCC's CRT is claimed qualitatively "even slower than MSVC" with no numbers.

## Use it when

- Game/graphics/embedded C or C++ codebases that want a small, dependency-free, single-header drop-in for heavy sprintf/snprintf call volume
- Cross-platform code that wants one format-string dialect instead of juggling MSVC (%I64d) vs GCC (%lld) differences for 64-bit integers
- Formatting-heavy hot paths (many floats/ints or long strings per frame/tick) where CRT sprintf throughput is a known bottleneck
- Code-space-constrained targets (embedded, consoles) where \~8K of formatting code beats linking in a full CRT static sprintf (\~16K per the header)
- Want built-in thousands separators or SI/JEDEC-suffix number formatting (%'d, %\$d, %\$\$d) without hand-rolling it

## Skip it when

- Strict C-standard sprintf conformance is required: open issues document divergent behavior for '+'/' '/'0' flags on unsigned types, negative width via '\*', and %n with non-default size (issues #1788-#1790, #1785, #1778)
- Format strings or precision values come from untrusted input: issue #1792 shows a buffer overrun via large integer precision (e.g. "%0.513x"), and issue #1963 shows stbsp_snprintf(buf, 0, ...) with a non-NULL buf writes one byte before the buffer -- both open, unpatched as of 2026-09-24
- You rely on the common "call with count=0 to get required length" idiom against a non-NULL buffer pointer -- that exact pattern triggers the #1963 OOB write
- You need independently benchmarked, modern numbers before committing: the header's speedup table is first-party, measured against MSVC 2008's CRT only, no CPU model or flags given (Tier C evidence)
- 16-bit int platforms are a target: issue #1779 is an open feature request, not currently supported

## How it is fast

It bypasses the CRT's generic, often locale-aware formatting machinery with hand-written, allocation-free integer/float-to-ASCII routines that feed a small internal buffer and a callback, so it never calls malloc and stays small enough to fit in cache (header states \~8K compiled with float support, \~4K without, vs. \~16K pulled in by MSVC's static sprintf). Float-to-string conversion uses an internal double-double (\~105-bit) arithmetic scheme for round-trip-correct output without going through the CRT's arbitrary-precision or locale-sensitive dtoa path (documented in the header's FLOATS/DOUBLES section).

## Compared with alternatives

The catalogued siblings (Boost.Charconv, c4core, fast_double_parser, rigtorp CharConv, fpconv, double-conversion, milo Grisu2, itoa variants) are narrow number&lt;-&gt;string converters that replace std::to_chars/from_chars or a single strtod/itoa call. stb_sprintf is scoped differently: it is a full printf-style format-string engine (mixed text plus args, width/precision, %n, etc.), so pick it when you need a drop-in-shaped replacement for whole sprintf/snprintf call sites -- especially in C or C-style C++ (game/graphics) code that already uses sprintf throughout -- rather than a targeted numeric conversion routine.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (only &lt;stdarg.h&gt; and &lt;stddef.h&gt; from the C standard library) |
| **Minimum toolchain** | C89/C99-compatible C or C++ compiler; no C++ standard required. Explicit shims for MSVC, GCC (&gt;=4.8), and Clang (including ASan attribute handling) |
| **Platforms** | any (portable C; explicit 32-/64-bit pointer-size detection for x86, x86-64, aarch64, ppc64, s390x) |
| **Thread safety** | Formatting calls themselves use only stack-local state per call (reentrant). stbsp_set_separators() mutates process-wide static globals (comma/period characters) with no locking, so it is not safe to call concurrently with formatting on other threads. Not explicitly documented as thread-safe by the author. |
| **Drop-in for the baseline** | partial -- explain: functions are stbsp_-prefixed, not sprintf/snprintf themselves (rename via STB_SPRINTF_DECORATE or #define if a literal drop-in is needed); stbsp_snprintf always null-terminates output, which the header notes differs from some CRT snprintf implementations; float output's insignificant digits can differ from glibc/MSVC CRT even though round-trip via atof is bit-exact |

## Gotchas

- Two open, unresolved correctness/security bugs as of 2026-09-24: stbsp_snprintf(buf, 0, ...) with non-NULL buf writes one byte before the buffer (#1963); large integer precision like "%0.513x" overruns the internal conversion buffer (#1792)
- stbsp_set_separators() changes process-wide global state (comma/period), not thread-local or per-call
- Float insignificant digits differ from glibc/MSVC CRT output (documented in header) even though round-trip via atof is exact
- Several open issues catalog format-flag edge cases (nan/inf capitalization, %A case, negative precision crash) that diverge from strict C sprintf semantics

## Caveats and trade-offs

First-party claim in the library's own header, not an independent benchmark; comparison baseline is MSVC 2008 (very old, \~2008-era CRT) with no CPU model or optimizer flags given, and no methodology beyond the numbers themselves -- caps this at Tier C; numbers have not been refreshed for modern MSVC/glibc CRTs.

Single-header, drop-in sprintf/snprintf replacement (no external deps); float formatting uses internal double-double math (\~105-bit precision) for round-trip-correct output, so exact insignificant digits can differ from glibc/MSVC CRT (documented in the header) even though round-trip via atof is exact.

## Maintenance

Actively maintained (pushed 2026-08-02, part of the 34.7k-star stb collection, not archived) but has a cluster of open correctness/security issues, including two out-of-bounds-write bugs, unresolved as of 2026-09-24. Dual MIT/public-domain (Unlicense) licensed per the header's own license block, so it is trivially copyable and safe to vendor regardless of upstream fixes.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** stb_sprintf.h lines 124-142 list per-format speedup ratios vs MSVC 2008 32-/64-bit sprintf (e.g. %f 7.3x/6.0x, %g 10.0x/7.1x, %d 4.8x/4.0x, 512-char string 35.0x/32.5x), matching the record verbatim; first-party numbers with no benchmark harness, CPU model or flags, so C.
- **Verifier notes:** All quoted ratios verified verbatim in the header comment; 'GCC is even slower than MSVC' is stated with no numbers. GitHub license is NOASSERTION but LICENSE file is MIT (Alternative A) or Unlicense/public domain (Alternative B), so 'MIT OR Unlicense' and copyable are correct; last commit 2026-08-02, 34,701 stars.
- **Shortcomings recorded by:** Falcon audio codec README table (first-party, x86-64 and Apple M5): stb_vorbis 1.22 decodes 1.31x faster than libvorbis 1.3.7 on x86-64 and 1.53x on the M5 (derived from page data).
- **Pages the verifier opened:**
  - <https://github.com/nothings/stb/blob/master/stb_sprintf.h>
  - <https://github.com/nothings/stb>
  - <https://github.com/nothings/stb/blob/master/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/nothings/stb>
  - <https://github.com/nothings/stb/blob/master/stb_sprintf.h>
  - <https://github.com/nothings/stb/blob/master/README.md>
  - <https://github.com/nothings/stb/issues/1963>
  - <https://github.com/nothings/stb/issues/1792>
  - <https://github.com/nothings/stb/issues/1793>
  - <https://github.com/nothings/stb/issues/1788>
  - <https://github.com/nothings/stb/issues/1780>
  - <https://github.com/nothings/stb/issues/1783>
  - <https://github.com/nothings/stb/issues/1730>
  - <https://github.com/nothings/stb/issues/1779>
  - <https://github.com/nothings/stb/issues/1785>
  - <https://github.com/nothings/stb/issues/1909>
  - <https://github.com/nothings/stb/issues/1778>
  - <https://github.com/nothings/stb/issues/1784>
  - <https://github.com/nothings/stb/issues/1786>
  - <https://github.com/nothings/stb/issues/1787>
  - <https://github.com/nothings/stb/issues/1789>
  - <https://github.com/nothings/stb/issues/1790>
  - <https://github.com/nothings/stb/issues/1777>
  - <https://github.com/nothings/stb/issues/1781>
  - <https://github.com/nothings/stb/issues/1782>
  - <https://github.com/nothings/stb/issues/1795>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/nothings/stb`) · [data/wave1/enrich/raw/github_com_nothings_stb.json](../../../data/wave1/enrich/raw/github_com_nothings_stb.json) (enrichment confidence 0.6)

</details>
