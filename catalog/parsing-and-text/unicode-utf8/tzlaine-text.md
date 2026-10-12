# Boost.Text (tzlaine/text)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [Unicode and UTF-8](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSL-1.0` · 🟡 stale

> Boost-style C++ Unicode library (transcoding, normalization, text types) faster than ICU only in narrow, now-degraded cases.

| | |
|---|---|
| **Beats** | ICU |
| **Claimed result** | Author text: '[Text] is factors faster than ICU's UTF-8 code path, and a bit faster than ICU's much faster UTF-16 code path' (NFC normalization of NFC-input European text); 'In every case, [Text] is faster than the UTF-8 ICU code path.' Chart bar widths (derived from page data): NFC European from NFC \~474k ns (Text string append) vs \~588k ns ICU UTF-8 (\~1.24x) vs \~476k ns ICU UTF-16 (parity); in the other three NFC scenarios Text beats ICU UTF-8 by only \~1.02-1.13x and ICU UTF-16 is faster (e.g. non-European from NFD \~893k vs \~558k ns). UTF-8-&gt;UTF-16 transcoding: Text SIMD \~473k ns vs ICU \~476k ns (parity); Text no-SIMD \~590k ns (slower than ICU). |
| **Workload** | UTF-8-&gt;UTF-16 and UTF-8-&gt;UTF-32 transcoding (ICU compared only for UTF-8-&gt;UTF-16 via UnicodeString::fromUTF8) and NFC/FCC/NFD normalization of \~0.5 MB Wikipedia text (European and non-European, NFC-input and NFD-input) against ICU's UTF-8 and UTF-16 normalizers; Google Benchmark |
| **Metric** | throughput |
| **Compiler and flags** | GCC (version unspecified) on Linux; optimization flags not stated |
| **Adoption** | 346 stars |
| **Last commit** | 2024-01-18 |
| **Links** | [repository](https://github.com/tzlaine/text) · [benchmark](https://github.com/tzlaine/text/blob/master/doc/performance.qbk) |

## Verdict

Vendor's Google Benchmark charts (GCC on Linux, no CPU model/compiler version/flags stated) on \~0.5MB of Wikipedia text show Text's NFC-normalize-from-NFC-input path on European text beating ICU's UTF-8 normalizer by \~1.02-1.24x and roughly matching ICU's UTF-16 normalizer, while ICU's UTF-16 path wins the other 3 of 4 NFC scenarios; for UTF-8-&gt;UTF-16 transcoding, Text's SIMD path matched ICU (\~473k vs \~476k ns) but the code now shipped (SIMD disabled) runs the slower \~590k ns scalar path.

## Use it when

- NFC normalization of already-NFC European-script UTF-8 text, compared only against ICU's UTF-8-input normalizer (not ICU's faster UTF-16 path) -- best case \~1.24x per the vendor's charts.
- You call the pointer-to-pointer bulk transcode_to_\*/normalize_append APIs directly instead of back-inserters or transcoding iterators; that is the only path where any measured gain applies.
- You want one Boost-style, STL-familiar library covering the full Unicode algorithm stack (segmentation, collation, bidi) plus text/rope types, not just fast transcoding.
- A C++14 codebase (Clang 6+/GCC 6+/VS2019+) that cannot add ICU as a dependency and values API/code familiarity over ICU feature completeness.

## Skip it when

- UTF-8-&gt;UTF-16 throughput: since dd2959e7 (Jan 2024) disabled SIMD, the shipped scalar path is slower than ICU's UnicodeString::fromUTF8 per the vendor's own chart.
- Non-European scripts or NFD-origin input for normalization: ICU's UTF-16 normalizer beats Text in 3 of the 4 charted NFC scenarios.
- Code that pipes output through std::back_inserter or the transcoding iterators for further per-code-unit work: documented by the author as 'quite bad'/'terrible' for performance, erasing the advantage.
- Wanting an actively maintained dependency: no commits since 2024-01-18 (stale), and the last fix was for a silent data-corruption bug in the fast path.
- Header-only vendoring: the data-heavy parts (collation_data_\*.cpp, normalization_data_\*.cpp, break tables) are compiled sources, not header-only, so you must build a library, not just #include headers.

## How it is fast

The fast paths write runs of already-decoded or already-normalized output in bulk rather than branching per code unit, which is what a std::back_inserter or the transcoding iterators force. A SIMD transcode path (originally from Bob Steagall's C++Now 2018 work) decoded up to 16 UTF-8 bytes per op, but commit dd2959e7 (2024-01-18, fixing issue #212 — a correctness bug that produced silently wrong UTF-16 output) force-disabled that SIMD path repo-wide, so the code now shipping runs the plain scalar path that the vendor's own charts show as slower than ICU for UTF-8-&gt;UTF-16.

## Compared with alternatives

Pick Boost.Text only when you need its broader Unicode algorithm/text-type surface (segmentation, collation, bidi, rope) in one Boost-style library; for pure UTF-8 validation/transcoding speed, ada-url/idna, encoding_rs, or SimdUnicode show larger, better-documented speedups over ICU or their respective baselines without a disabled fast path.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | Boost &gt;= 1.71.0 (auto-cloned by CMake if not found); Boost.Filesystem/System only for the optional ncurses example editor |
| **Minimum toolchain** | C++14 minimum (Clang 6+, GCC 6+, VS2019+); C++20 mode (concepts/coroutines) needs GCC 10+/Clang 13+/VS2019+ |
| **Platforms** | any platform supported by GCC/Clang/MSVC; the transcode SIMD path targeted x86 SIMD historically but is force-disabled as of 2024-01-18, so the current build is effectively scalar |
| **Thread safety** | not documented, beyond a perf note that rope ref-counting uses atomics (8ns non-atomic vs 9-10ns atomic per copy, measured on macOS) |
| **Drop-in for the baseline** | partial -- covers ICU's transcoding/normalization/segmentation/collation feature areas but with a different, Boost/STL-style API, not ICU's UnicodeString/UBreakIterator surface |

## Gotchas

- SIMD-accelerated transcoding (transcode_algorithm.hpp) was force-disabled repo-wide by commit dd2959e7 (2024-01-18), fixing issue #212 where BOOST_TEXT_USE_SIMD=1 produced corrupted, non-deterministic UTF-16 output; there is no supported way to safely re-enable it in the shipped code.
- Using std::back_inserter or the transcode/normalize iterators directly forfeits nearly all the measured speed advantage -- only the pointer-to-pointer bulk APIs are fast.
- MSVC users must build with /utf8 (or at least /source-charset:utf-8) or the \~150 CLDR locale headers under boost/text/data/ will be misinterpreted.
- The published performance charts predate the 2024-01-18 SIMD disable and no longer reflect the UTF-8-&gt;UTF-16 numbers of the code you'd actually build today.

## Caveats and trade-offs

Only 'GCC on Linux' stated: no CPU model, compiler version or flags; results appear only as SVG bar charts (doc copyright 2020, run date not given). The 'factors faster' text overstates the charts: best case is \~1.24x vs ICU's UTF-8 normalizer and parity with ICU's UTF-16 normalizer, and ICU UTF-16 wins the other three NFC scenarios. The latest commit (dd2959e, 2024-01-18, issue #212) force-disables the SIMD transcoding path, so current code runs the 'no SIMD' path that the chart shows slower than ICU for UTF-8-&gt;UTF-16. No commits since Jan 2024.

Header-heavy Boost-style API; back-inserter-based usage is much slower, so gains are only realized through the pointer-to-pointer bulk transcoding APIs.

## Maintenance

Stale since its last commit on 2024-01-18, which force-disabled the SIMD transcode path after it was found to silently corrupt UTF-16 output; BSL-1.0 licensed and copyable, but not header-only -- vendoring means building compiled data/algorithm sources, not just including headers.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): downgrade; tier before verification C, tier now C.
- **Tier reason:** First-party Google Benchmark results (sources in perf/transcoding_perf.cpp, perf/normalize_perf.cpp, perf/icu_normalization.cpp) with only 'GCC on Linux' stated: no CPU model, compiler version or flags, so C. Values exist only as SVG bar charts, but bar widths on the 0-2,500,000 ns axis make them derivable.
- **Verifier notes:** Quoted sentences are on performance.qbk, but the SVG bar geometry shows modest gains (1.02-1.24x vs ICU UTF-8 normalization) and losses to ICU UTF-16 in 3 of 4 NFC cases; downgraded for overstated claim, tier stays C. The record's caveat that results are 'worse than ICU' for non-European/NFD input holds only against ICU's UTF-16 path, not its UTF-8 path. Metadata (BSL-1.0, 346 stars, last commit 2024-01-18) confirmed.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/tzlaine/text>
  - <https://github.com/tzlaine/text/blob/master/doc/performance.qbk>
  - <https://github.com/tzlaine/text/blob/master/doc/utf_8_to_16_perf.svg>
  - <https://github.com/tzlaine/text/blob/master/doc/utf_8_to_32_perf.svg>
  - <https://github.com/tzlaine/text/blob/master/doc/norm_nfc_euro_from_nfc_perf.svg>
  - <https://github.com/tzlaine/text/blob/master/doc/norm_nfc_non_euro_from_nfc_perf.svg>
  - <https://github.com/tzlaine/text/blob/master/doc/norm_nfc_euro_from_nfd_perf.svg>
  - <https://github.com/tzlaine/text/blob/master/doc/norm_nfc_non_euro_from_nfd_perf.svg>
  - <https://github.com/tzlaine/text/commit/dd2959e7>
  - <https://github.com/tzlaine/text/tree/master/perf>
- **Sources the enricher read:**
  - <https://github.com/tzlaine/text>
  - <https://github.com/tzlaine/text/blob/master/doc/performance.qbk>
  - <https://github.com/tzlaine/text/blob/master/doc/compiler_support.qbk>
  - <https://github.com/tzlaine/text/blob/master/doc/configuration.qbk>
  - <https://github.com/tzlaine/text/blob/master/doc/overview.qbk>
  - <https://github.com/tzlaine/text/blob/master/CMakeLists.txt>
  - <https://github.com/tzlaine/text/blob/master/cmake/dependencies.cmake>
  - <https://github.com/tzlaine/text/commit/dd2959e7143fde3f62b24d87a6573b5b96b6ea46>
  - <https://github.com/tzlaine/text/issues/212>
  - <https://github.com/tzlaine/text/tree/master>
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/tzlaine/text`) · [data/wave3/enrich/raw/github_com_tzlaine_text.json](../../../data/wave3/enrich/raw/github_com_tzlaine_text.json) (enrichment confidence 0.4)

</details>
