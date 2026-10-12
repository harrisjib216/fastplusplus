# libhat

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [SIMD intrinsics libraries](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🟢 active

> C++20 SIMD byte-signature scanner (IDA-style wildcards and bitmasks) that outruns std::search over masked pattern elements.

| | |
|---|---|
| **Beats** | std::search (MSVC STL) called by libhat's own scan_mode::Search path: std::search(begin, end, sig.begin(), sig.end()) over a std::byte haystack with a std::span&lt;const hat::signature_element&gt; needle, each comparison doing (byte & mask) == value; a wildcard-capable scalar baseline, not a plain-byte std::search |
| **Claimed result** | libhat+AVX2 55.1129 GiB/s at 4 MiB and 23.3351 GiB/s at 256 MiB versus the README's std::search row (libhat's own scalar masked fallback, 2.89578 GiB/s); against the MSVC std::find(unseq) plus std::equal row shown before PR #46 (20.6418 and 13.1721 GiB/s) the gain is about 2.8x and 1.75x (derived from page data) |
| **Workload** | Single-threaded search for a 9-byte pattern (01 02 .. 09) that never matches in a seeded random buffer of 4 MiB to 256 MiB, Google Benchmark, real time, 4 s minimum per run, libhat AVX2 scanner without scan hints. |
| **Metric** | throughput |
| **Hardware** | Intel i7-14700K (AVX2), 64 GB DDR5-6000 (30-38-38-96) |
| **Compiler and flags** | clang-cl 22.1.1 with the MSVC 14.51.36231 toolchain on Windows, default release flags /GR /EHsc /MD /O2 /Ob2 (README); benchmark source test/benchmark/Compare.cpp read via raw.githubusercontent.com |
| **Adoption** | 148 stars; vcpkg port 'libhat' in the vcpkg ports list |
| **Last commit** | 2026-10-10 |
| **Links** | [repository](https://github.com/BasedInc/libhat) · [benchmark](https://github.com/BasedInc/libhat#benchmarks) |

## Verdict

README table (PR #46, 2026-10-10): clang-cl 22.1.1 with the MSVC 14.51.36231 toolchain at /O2, i7-14700K with DDR5-6000, Google Benchmark real time, one thread, a 9-byte pattern that never matches in a seeded random buffer: libhat AVX2 55.11 GiB/s at 4 MiB and 23.34 GiB/s at 256 MiB versus libhat's own std::search fallback over masked signature elements at 2.90 GiB/s (about 19x and 8.1x, derived from page data). Against the STL-built std::find + std::equal path the July 2026 README showed about 2.8x (4 MiB) and 1.75x (256 MiB).

## Use it when

- Locating functions or data in a loaded executable or DLL by byte signature with wildcards (game modding, instrumentation, hooking), where the pattern has at least two consecutive fully specified bytes.
- Scanning hundreds of MiB of x86-64 or AArch64 machine code: pass scan_hint::x86_64/aarch64 and, for function starts, scan_alignment::X16 (README Chromium table: 6.09 GiB/s unhinted vs 18.6-22.9 GiB/s hinted or aligned).
- Replacing hand-rolled UnknownCheats-style scanners (the csgosimple and learn_more rows run at 0.96-2.3 GiB/s in the same harness) or a std::search over a masked element type.
- C++20 projects on Windows, Linux, macOS or Android that can link a small static library (or use the C bindings for dynamic linking).

## Skip it when

- Plain substring search without wildcards: memchr/memmem or a vectorised std::find + compare is already fast; libhat's own std::find + std::equal row reached 20.6 GiB/s at 4 MiB and 13.2 GiB/s at 256 MiB in the July 2026 README, so the margin there is about 2.8x and 1.75x, not 19x.
- Patterns with no fully specified byte: they fall back to the scalar Single path, and the README warns of 'significant performance degradation'; patterns without two adjacent full bytes lose the pair filter.
- Machine code with common anchor bytes and no scan hint: candidate verification dominates and throughput fell to 6.09 GiB/s on chrome.dll in the README's (older) table.
- Pre-C++20 toolchains or projects that need a header-only drop-in: libhat is a CMake static library (CMake 3.23+, cxx_std_20).
- Code where anti-cheat or licence terms of the target program forbid memory scanning: the library's purpose is user-space game hacking.

## How it is fast

The SIMD paths (SSE4.1, AVX2, AVX-512BW, Neon, picked at run time via cpuid unless compiled in) choose an anchor pair of two adjacent fully masked bytes, compare each aligned 32-byte block against both broadcast anchor bytes with vpcmpeqb, AND the two movemasks (shifted by one), and only then verify each candidate with a single unaligned 32-byte load, XOR and vptest against the signature's value and mask vectors (patterns of at most 32 bytes for AVX2; longer ones verify with std::equal). The anchor pair is chosen to avoid bytes repeated in the pattern, or, with scan_hint::x86_64 or aarch64, from a 512-entry pair-frequency table so that rare opcode pairs gate the expensive verify step; scan_alignment::X4/X16 masks out candidates at unaligned offsets. This is the generic 'SIMD-friendly substring search' anchor-filter idea applied to masked byte patterns.

## Compared with alternatives

Pick libhat over memchr (Rust crate) or vectorized_find when the needle has wildcards or bitmasked bytes and you are in C++ scanning loaded modules; for exact-byte substring or single-value search those siblings (or a vectorised std::find) are the simpler choice and libhat's advantage shrinks.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | none at run time (Google Benchmark and a test framework only for the optional tests/benchmarks); C bindings can be built as static or shared libhat_c |
| **Minimum toolchain** | C++20, CMake 3.23+; README benchmark used clang-cl 22.1.1 with MSVC 14.51; optional C++20 module target |
| **Platforms** | Windows, Linux, macOS, Android; x86 and x86-64 (SSE4.1/AVX2 runtime-detected, AVX-512BW on x86-64), ARM/AArch64 (Neon); portable scalar fallback elsewhere |
| **Thread safety** | not documented; from source, find_pattern builds a fresh scan_context per call (the Single mode's self-reordering anchor list lives in that per-call context), so concurrent scans of read-only memory share no mutable state |
| **Drop-in for the baseline** | partial: replaces std::search over a byte range for signature lookups, but takes a hat::signature/signature_view instead of a needle iterator pair and returns a scan_result rather than an iterator (nullptr when absent) |

## Gotchas

- Baseline selection in the README: the headline table compares against libhat's scan_mode::Search fallback, std::search over hat::signature_element whose operator== does (byte & mask) == value, so no vectorised or memcmp-style STL path can apply. The README before PR #46 (commit bf17bf1, July 2026) also published BM_Throughput_std_find_std_equal (libhat's Single mode: MSVC std::find with std::execution::unseq on the anchor byte plus std::equal) at 20.6418 GiB/s at 4 MiB and 13.1721 GiB/s at 256 MiB against libhat 58.2888 and 22.9961 GiB/s (about 2.8x and 1.75x, derived from page data); PR #46 dropped that row, keeping only the 2.9 GiB/s std::search row.
- README labels do not match the current harness: test/benchmark/Compare.cpp now registers every libhat X1 unhinted mode (Auto, Search, Single, SSE, AVX2; AVX-512 and Neon skip on an i7-14700K) as libhat+&lt;Mode&gt;+X1, so a run prints Auto, Single and SSE rows the README omits and names the two published rows libhat+AVX2+X1 and libhat+Search+X1. The Chromium table (BM_find, BM_UC1 ...) was not re-run in PR #46: its names and its 18-byte DllMain pattern come from the older Chromium.cpp, while the current file scans a 20-byte pattern through the scanner registry.
- Throughput in the Chromium benchmark counts only the bytes before the first match (result - buf.data()), and the synthetic benchmark's random buffer makes an anchor-pair hit a 1-in-65536 event, so both tables show the filter at its best; dense candidate streams cost a 32-byte verify each.
- find_pattern is noexcept but the Single fallback allocates its anchor list with make_unique per call; an allocation failure there terminates. Declarations in detail or experimental namespaces (scan_mode, scan_context, find_vtable) are outside the semver guarantee.

## Known shortcomings

- The std::search baseline is libhat's own scan_mode::Search path with a masked, wildcard-aware signature_element compare per byte, not a plain-byte std::search; README row names are hand-relabelled.
- Enricher: the headline std::search row is libhat's own scalar masked fallback; the README before PR #46 (commit bf17bf1, July 2026) also showed BM_Throughput_std_find_std_equal (MSVC std::find(unseq) plus std::equal) at 20.6418 GiB/s at 4 MiB and 13.1721 GiB/s at 256 MiB, making libhat about 2.8x and 1.75x faster than an STL-built path rather than 19x and 8.1x (derived); PR #46 dropped that row; README labels do not match the current Compare.cpp; the Chromium table is stale (old harness and 18-byte pattern, never re-run after #46).

## Caveats and trade-offs

First-party benchmark on one CPU and one compiler. The std::search row is libhat's scan_mode::Search fallback (include/libhat/scanner.hpp, find_pattern_search&lt;X1&gt;): std::search with a heterogeneous needle type (hat::signature_element with a bitmask, compared to std::byte via a masked operator==), so no memcmp-style or vectorised STL search path can apply; its flat 2.9 GiB/s is a scalar search, and a plain-byte search (memmem, a vectorised std::search or std::boyer_moore_horspool_searcher on bytes) without wildcard support would narrow the 8x to 19x gap. The README row labels (libhat+AVX2, std::search) differ from the names the current Compare.cpp prints (libhat+AVX2+X1, libhat+Search+X1), so the table was relabelled by hand; both files were last changed in the same commit (Adaptive anchors, #46, 2026-10-10). 4 MiB to 16 MiB buffers fit in the i7-14700K's L3 and run at 50-55 GiB/s; 32 MiB and above drop to 23-31 GiB/s. The needle has no wildcards and never matches (full-buffer scan). On real machine code (chrome.dll, test/benchmark/Chromium.cpp) unhinted, unaligned libhat falls to 6.09 GiB/s, and that table has no std::search row. AVX2 is selected at runtime; the build uses default release flags without /arch:AVX2. [retier] Headline baseline is libhat's own scalar fallback; the STL-built path row was dropped in PR #46; README labels do not match the current Compare.cpp; Chromium table stale

Scanner needs SSE4.1 or AVX2 (x86), AVX-512 (x86-64) or NEON (ARM) for the vector paths, with runtime cpuid validation; patterns are IDA-style byte signatures with wildcards, not general string search. Optional x86_64/aarch64 scan hints trade a small data table for faster scans of machine code. C++20; bindings for C, Java, Python and C#. Aimed at game hacking in user space (signature scanning, memory protection helpers).

## Maintenance

Actively developed (468 commits, PR #46 merged 2026-10-10, v0.11.1 in README, vcpkg and xmake packages), MIT-licensed and easy to link; the headline 19x is against a deliberately generic masked std::search, and the README no longer shows the faster std::find + std::equal row it published in July 2026 (about 2.8x and 1.75x behind libhat), so expect single-digit gains over a vectorised STL anchor search.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** README Benchmarks table lists libhat+AVX2 55.1129 GiB/s (4 MiB) and 23.3351 GiB/s (256 MiB) against std::search 2.89578 and 2.89598 GiB/s; the code is public (test/benchmark/Compare.cpp plus test/benchmark/scanner/\*.cpp, Google Benchmark, real time, 2 s warm-up, 4 s min time, result checked against the expected null match), and compiler (clang-cl 22.1.1, MSVC 14.51.36231 toolchain), flags (/GR /EHsc /MD /O2 /Ob2) and CPU (i7-14700K) are stated.
- **Verifier notes:** Numbers, ratios (about 19x at 4 MiB and 8.1x at 256 MiB, derived from page data), MIT license, 148 stars, last commit 2026-10-10 and vcpkg port all check out. Shortcoming to record: the std::search baseline is libhat's own wildcard-aware std::search fallback with a masked element compare, a scalar path, not the fastest plain-byte search the STL or memmem could do.
- **Fields the verifier corrected:** `baseline`, `caveats`, `claimed_speedup`
- **Shortcomings recorded by:** verifier batch-75 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/BasedInc/libhat>
  - <https://github.com/BasedInc/libhat/commits/master>
  - <https://github.com/BasedInc/libhat/commits/master/test/benchmark/Compare.cpp>
  - <https://github.com/BasedInc/libhat/commits/master/README.md>
  - <https://github.com/BasedInc/libhat/pull/46>
  - <https://github.com/BasedInc/libhat/tree/master/test/benchmark>
  - <https://github.com/BasedInc/libhat/tree/master/test/benchmark/scanner>
  - <https://raw.githubusercontent.com/BasedInc/libhat/HEAD/README.md>
  - <https://raw.githubusercontent.com/BasedInc/libhat/HEAD/test/benchmark/Compare.cpp>
  - <https://raw.githubusercontent.com/BasedInc/libhat/HEAD/test/benchmark/scanner/scanner.hpp>
  - <https://raw.githubusercontent.com/BasedInc/libhat/HEAD/test/benchmark/scanner/libhat.cpp>
  - <https://raw.githubusercontent.com/BasedInc/libhat/HEAD/include/libhat/scanner.hpp>
  - <https://raw.githubusercontent.com/BasedInc/libhat/HEAD/include/libhat/signature.hpp>
  - <https://raw.githubusercontent.com/BasedInc/libhat/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/BasedInc/libhat/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/BasedInc/libhat>
  - <https://github.com/BasedInc/libhat/tree/master/src>
  - <https://github.com/BasedInc/libhat/tree/master/src/scanner>
  - <https://github.com/BasedInc/libhat/pull/46>
  - <https://github.com/BasedInc/libhat/commits/master/README.md>
  - <https://github.com/BasedInc/libhat/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/BasedInc/libhat/HEAD/README.md>
  - <https://raw.githubusercontent.com/BasedInc/libhat/HEAD/test/benchmark/Compare.cpp>
  - <https://raw.githubusercontent.com/BasedInc/libhat/HEAD/test/benchmark/Chromium.cpp>
  - <https://raw.githubusercontent.com/BasedInc/libhat/HEAD/test/benchmark/scanner/scanner.hpp>
  - <https://raw.githubusercontent.com/BasedInc/libhat/HEAD/test/benchmark/scanner/libhat.cpp>
  - <https://raw.githubusercontent.com/BasedInc/libhat/HEAD/include/libhat/scanner.hpp>
  - <https://raw.githubusercontent.com/BasedInc/libhat/HEAD/include/libhat/signature.hpp>
  - <https://raw.githubusercontent.com/BasedInc/libhat/HEAD/include/libhat/defines.hpp>
  - <https://raw.githubusercontent.com/BasedInc/libhat/HEAD/src/scanner/avx2.cpp>
  - <https://raw.githubusercontent.com/BasedInc/libhat/HEAD/src/scanner/simd.hpp>
  - <https://raw.githubusercontent.com/BasedInc/libhat/HEAD/src/scanner/single.cpp>
  - <https://raw.githubusercontent.com/BasedInc/libhat/HEAD/src/scanner/scanner.cpp>
  - <https://raw.githubusercontent.com/BasedInc/libhat/HEAD/src/scanner/scan_context.hpp>
  - <https://raw.githubusercontent.com/BasedInc/libhat/HEAD/src/utils.cpp>
  - <https://raw.githubusercontent.com/BasedInc/libhat/HEAD/src/utils.hpp>
  - <https://raw.githubusercontent.com/BasedInc/libhat/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/BasedInc/libhat/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/BasedInc/libhat/bf17bf1/README.md>
  - <https://raw.githubusercontent.com/BasedInc/libhat/bf17bf1/test/benchmark/Compare.cpp>
  - <https://raw.githubusercontent.com/BasedInc/libhat/bf17bf1/test/benchmark/Chromium.cpp>
  - <https://raw.githubusercontent.com/BasedInc/libhat/bf17bf1/include/libhat/scanner.hpp>
  - <https://raw.githubusercontent.com/BasedInc/libhat/bf17bf1/src/Scanner.cpp>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/basedinc/libhat`) · [data/wave13/enrich/raw/github_com_basedinc_libhat.json](../../../data/wave13/enrich/raw/github_com_basedinc_libhat.json) (enrichment confidence 0.85)

</details>
