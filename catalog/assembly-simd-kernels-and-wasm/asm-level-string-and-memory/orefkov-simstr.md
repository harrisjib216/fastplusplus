# simstr

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Assembly-level string and memory routines](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🟢 active

> C++20 string types and expression-template concatenation that build strings with one allocation; 1.5-5x faster than naive std::string idioms.

| | |
|---|---|
| **Beats** | std::string and std::string_view idioms: concatenation, std::to_string, std::format hex formatting, find, replace and split code written with the C++ standard library |
| **Claimed result** | README headline 'Speed up your work with strings by 2-10 times!'. v2.0.0 result files, six toolchains on Xeon E5-2682 v4 (derived from page data): string + number + literal into std::string 1.55-2.46x vs std::to_string concatenation (3.0-5.0x into simstr::stringa), README says 1.6-2x; hex formatting into std::string 4.3-9.2x vs s1 + std::format("{:#x}") + literal (5.9-11.0x into stringa), README says 9-14x, but only 1.3-2.4x vs the std::to_chars version in the same suite; find of three concatenated strings 1.7-3.3x with strexpr into std::string and 3.7-9.7x with stack-buffer lstringa, README says 1.5-9x; conditional concatenation (prec 10) 1.85-3.1x into std::string and 2.1-5.4x into stringa, README says 1.5-2.2x; replace-while-copying 1.4-2.2x, README says 1.5x and higher; split and parse 1.4-3.25x (1.4-1.8x on Linux, 1.8-3.25x on Windows and WASM), README says 2-3x. |
| **Workload** | Google Benchmark microbenchmarks (bench/bench_str.cpp) of string concatenation, number and hex formatting, literal search, replace-while-copying and split/parse, each against a plain std version of the same task. |
| **Metric** | throughput |
| **Hardware** | Intel Xeon E5-2682 v4 (32 threads at about 2.5 GHz, 40 MiB L3), Windows 10 and Ubuntu 22 under WSL; WASM build in Chrome 143 on the same machine |
| **Compiler and flags** | Clang 22.0.0 (libstdc++ and, via -stdlib=libc++, libc++) and GCC 15.2.0 on Ubuntu 22 under WSL; clang-cl 22.1.0 and MSVC 19.44.35213 on Windows 10; Emscripten Clang 22 (libc++, 32-bit WASM, -msimd128 -msse4.2 -msse3) run in Chrome 143. CMake Release presets from CMakePresets.json (CMake defaults -O3 -DNDEBUG for GCC/Clang, /O2 /Ob2 /DNDEBUG plus /utf-8 /Zc:strictStrings for MSVC), C++23, no -march; Google Benchmark 1.9.4, 4 repetitions, ASLR enabled. The result files do not name the preset used. |
| **Adoption** | 34 stars, 3 forks; vcpkg port orefkov-simstr |
| **Last commit** | 2026-10-04 |
| **Links** | [repository](https://github.com/orefkov/simstr) · [benchmark](https://github.com/orefkov/simstr/tree/main/bench/results) |

## Verdict

The committed v2.0.0 Google Benchmark files (means of 4 repetitions, one Xeon E5-2682 v4, Linux rows under WSL) time each task against a plain std version. With Clang 22 and libstdc++: number concatenation 224 to 107 ns (2.1x), hex formatting 716 to 137 ns vs std::format (5.2x) but 207 to 137 ns vs std::to_chars (1.5x), concatenated-key find 114 to 51.3 ns (std::string result) or 20.0 ns (lstringa), conditional type-name build 59.3 to 23.6 ns, replace-while-copying 209 to 148 ns, and split plus parse 275 to 160 ns. MSVC 19.44, GCC 15.2, clang-cl and WASM runs show the same direction with different magnitudes; the README's 9-14x hex and 2-3x split figures overstate these files.

## Use it when

- Hot code that builds many short strings from literals, numbers and existing strings (log lines, keys, SQL or type names): string + number + literal into std::string ran 224 ns vs 107 ns per six concatenations (Clang 22, libstdc++) and 333 vs 215 ns (MSVC 19.44).
- Hex or octal number formatting inside a concatenation: 716 ns vs 137 ns against s + std::format("{:#x}") + literal (Clang), 1018 vs 120 ns (MSVC).
- Temporary keys or messages that fit a fixed stack buffer: lstringa&lt;200&gt; took the 'find a concatenated key' row from 114 ns to 20.0 ns on Clang/Linux and 221 to 29.3 ns under MSVC.
- Splitting delimited text and parsing integers without per-part copies: 275 ns to 160 ns (Clang/Linux) and 558 ns to 220 ns (MSVC, splitf).
- Code that needs the same string algorithms for char, char8_t, char16_t, char32_t and wchar_t, where std::format and std::to_chars only cover char.

## Skip it when

- You want a drop-in std::string: simstr has its own string types and only partly std-compatible methods, so adoption is a rewrite.
- Single integer parsing: std::from_chars is as fast or faster (MSVC 11.9 ns vs to_int 15.5 ns; GCC 15 12.1 ns vs stringa::to_int 17.1 ns).
- String-keyed hash maps on Linux: hashStrMapA (built on std::unordered_map) took 3.73 ms vs 3.64 ms for std::unordered_map&lt;std::string&gt; with Clang and 3.84 vs 3.64 ms with GCC; it wins only under MSVC.
- Long-haystack substring search: ssa::find ties std::string_view::find on Linux (7.82 vs 7.40 ns, Clang); a SIMD searcher is the tool there.
- Toolchains older than C++20, or builds that cannot take simdutf as a dependency (needed by the full library, not by strexpr.h).

## How it is fast

Expression templates compute the total length of a whole concatenation once, allocate the result once and write every piece (including numbers formatted in place) directly into it, so no temporaries or reallocations occur. lstring&lt;N&gt; keeps results up to N characters on the stack (the find example builds its 36-character search key without touching the heap), and integer parsing and hex/decimal formatting are inline template code instead of strtol, std::to_string or std::format. There is no SIMD in strexpr.h: substring search is a char_traits::find on the first character followed by compare, the same method libstdc++ uses.

## Compared with alternatives

The siblings in this category (WojciechMula's AVX-512 string toys, sliceslice, the MSVC STL's vectorised std::search, Arm Optimized Routines) speed up scanning and copying bytes. Pick simstr when the time goes into building, formatting and splitting many short strings (temporaries, std::to_string, std::format), and pick a SIMD searcher when the cost is searching long buffers.

## Integration

| | |
|---|---|
| **Form** | header-only (strexpr.h part) or static lib (full library: three headers and two sources) |
| **Dependencies** | none for strexpr.h; full library needs simdutf (CMake fetches v7.5.0); the benchmark also pulls Google Benchmark 1.9.4, fmt 12.1.0 and StringZilla main |
| **Minimum toolchain** | C++20 (concepts, std::format), CMake 3.20; README says it was checked on MSVC 19, Clang 19 and 21, GCC 13 and Emscripten 4.0.6 |
| **Platforms** | any (portable C++ with no intrinsics in strexpr.h); author tests Windows, Linux and 32-bit WASM |
| **Thread safety** | not documented; sstring shares buffers through an atomic reference count (relaxed ordering), other types are plain values |
| **Drop-in for the baseline** | partial: strexpr.h expressions accept and produce std::string and std::string_view, but split, parsing and replace use simstr types and the full speedups need stringa or lstring |

## Gotchas

- The std baselines are naive idioms: the find row builds its key with std::string{name} plus two concatenation temporaries, the std hash-map string_view row constructs a std::string on every lookup instead of using C++20 heterogeneous lookup, and the replace row appends to an unreserved std::string. Against the fastest std path in the same suite the gap narrows: hex 1.5x (Clang) to 2.1x (MSVC) vs std::to_chars, and short-text replace with std::string_view find_first_of + copy (166 ns) beats simstr's memorising variant (178 ns) on Clang.
- The catalogue's asm-level label does not fit: the gains come from allocation avoidance and inline number conversion, not from vectorised scanning (find = first-character char_traits::find + compare).
- sstring's reference count is decremented with std::memory_order_relaxed and the buffer freed on the last release, with no release/acquire ordering (SharedStringData::decr in sstring.h). That is the pattern std::shared_ptr avoids; on weakly ordered CPUs such as ARM, sharing one sstring across threads may race a reader's last accesses with another thread's free. x86's locked fetch_sub hides it. This is from reading the code; no failure has been reported.
- Harness notes: the CHECK_RESULT answer checks are compiled out by default; StringZilla is fetched from its main branch and linked header-only with no -march flags, so its competitor rows (sz::string::find 98.6 ns vs std::string::find 7.17 ns on Clang) probably measure a serial fallback and say nothing about StringZilla; in the concat and hex rows the loop values of i (1 to 100000) are compile-time constants not hidden with DoNotOptimize.

## Known shortcomings

- README overstates two claims against its own bench/results files (hex 9-14x claimed, 4.3-9.2x measured; split 2-3x claimed, 1.4-3.25x measured); baselines are naive std idioms (against std::to_chars the hex win is 1.3-2.4x); hashStrMapA is slightly slower than std::unordered_map on Linux; single CPU (Xeon E5-2682 v4), Linux runs under WSL.
- Baselines are naive idioms (extra temporaries, a std::string built per hash lookup, no reserve); against the fastest std path in the same suite the gap narrows to 1.5-2.1x for hex (std::to_chars), and std::from_chars beats to_int on MSVC and trails it by 1.3-1.8x on GCC. No SIMD, so the asm-level category does not fit. sstring's reference count uses a relaxed fetch_sub before free, a possible race on ARM (code reading only). The StringZilla competitor rows are probably a serial fallback (unpinned main, header-only, no -march).

## Caveats and trade-offs

Speedups are against the author's own std idioms (std::to_string or std::format concatenation with temporaries, find + substr + strtol, a hand-written std replace loop), not the fastest std alternatives: with std::to_chars the hex-formatting gap shrinks from 4.3-9.2x to 1.3-2.4x, and in decimal int parsing std::from_chars trails simstr's to_int by only 1.3-1.8x on Linux and beats it under MSVC (11.9 ns vs 15.5 ns). The README's 9-14x hex and 2-3x split figures overstate the v2.0.0 result files (4.3-9.2x and 1.4-3.25x). Not every row wins: hashStrMapA is slightly slower than std::unordered_map&lt;std::string&gt; on Linux (3.73 ms vs 3.64 ms for Clang/libstdc++) and faster only on Windows, and ssa::find ties std::string_view::find on Linux. All runs are on one CPU (Xeon E5-2682 v4), the Linux rows ran under WSL, ASLR was on and only 4 repetitions were taken. The result files do not name the CMake preset (Release inferred). The optional CHECK_RESULT answer checks are compiled out by default, though the split benchmark's std and simstr versions compute the same total by design. bench_str.cpp also compares StringZilla and fmt, which are not baselines here.

Own string types and 'string expressions' API rather than a drop-in std::string; version 2.0.0 needs C++20 (concepts, std::format); the full library adds UTF conversion and shared/mutable string types.

## Maintenance

Actively maintained by one author (75 commits, v2.0.0 on 2026-10-04, 34 stars, one closed issue, vcpkg port orefkov-simstr). It is MIT-licensed, and strexpr.h alone can be vendored into a C++20 project without dependencies.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded C to A: the README ratios come from Google Benchmark result files committed in bench/results/ (v2.0.0, 2026-10-04) produced by the public bench/bench_str.cpp, each naming the CPU (Intel Xeon E5-2682 v4) and exact compiler (Clang 22.0.0 with libstdc++ and libc++, GCC 15.2.0, clang-cl 22.1.0, MSVC 19.44.35213, Emscripten Clang 22), with flags from the public CMakePresets.json Release presets (lzbench public-Makefile precedent). The result files do not name the preset; Release is inferred from the presets and the absence of Google Benchmark's DEBUG warning.
- **Verifier notes:** Real entry with fair-looking Google Benchmark harness (DoNotOptimize on inputs and outputs, same task on both sides) and committed v2.0.0 result files for six toolchains, so tier rises C to A. Shortcomings to record: README overstates hex (9-14x vs 4.3-9.2x measured) and split (2-3x vs 1.4-3.25x); baselines are naive std idioms (std::to_chars narrows hex to 1.3-2.4x); hashStrMapA not faster than std::unordered_map on Linux; single CPU, WSL Linux runs, preset not named in result files. orefkov.github.io/simstr/results.html was EGRESS_BLOCKED, but bench/results.html and the raw result files in the repo carry the same data.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `baseline_stdlib`, `compiler_and_flags`, `hardware`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-62 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/orefkov/simstr>
  - <https://github.com/orefkov/simstr/commits>
  - <https://github.com/orefkov/simstr/tree/main/docs>
  - <https://github.com/orefkov/simstr/tree/main/bench>
  - <https://github.com/orefkov/simstr/tree/main/bench/results>
  - <https://raw.githubusercontent.com/orefkov/simstr/HEAD/readme.md>
  - <https://raw.githubusercontent.com/orefkov/simstr/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/orefkov/simstr/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/orefkov/simstr/HEAD/CMakePresets.json>
  - <https://raw.githubusercontent.com/orefkov/simstr/HEAD/bench/bench_str.cpp>
  - <https://raw.githubusercontent.com/orefkov/simstr/HEAD/bench/CMakeLists.txt>
  - <https://raw.githubusercontent.com/orefkov/simstr/HEAD/bench/results.html>
  - <https://raw.githubusercontent.com/orefkov/simstr/HEAD/bench/process_result.cpp>
  - <https://raw.githubusercontent.com/orefkov/simstr/HEAD/bench/results/000-Xeon%20E5-2682%20v4%2C%20Ubuntu%2022%20%28WSL%29%2C%20Clang-22.txt>
  - <https://raw.githubusercontent.com/orefkov/simstr/HEAD/bench/results/001-Xeon%20E5-2682%20v4%2C%20Ubuntu%2022%20%28WSL%29%2C%20Clang-22%20libc%2B%2B.txt>
  - <https://raw.githubusercontent.com/orefkov/simstr/HEAD/bench/results/002-Xeon%20E5-2682%20v4%2C%20Ubuntu%2022%20%28WSL%29%2C%20GCC-15.txt>
  - <https://raw.githubusercontent.com/orefkov/simstr/HEAD/bench/results/003-Xeon%20E5-2682%20v4%2C%20Windows%2010%2C%20Clang-22.txt>
  - <https://raw.githubusercontent.com/orefkov/simstr/HEAD/bench/results/004-Xeon%20E5-2682%20v4%2C%20Windows%2010%2C%20MSVC-19.txt>
  - <https://raw.githubusercontent.com/orefkov/simstr/HEAD/bench/results/005-Xeon%20E5-2682%20v4%2C%20WASM%20Chrome%20143%2C%20Clang-22.txt>
- **Sources the enricher read:**
  - <https://github.com/orefkov/simstr>
  - <https://github.com/orefkov/simstr/commits/main>
  - <https://github.com/orefkov/simstr/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/orefkov/simstr/HEAD/readme.md>
  - <https://raw.githubusercontent.com/orefkov/simstr/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/orefkov/simstr/HEAD/CMakePresets.json>
  - <https://raw.githubusercontent.com/orefkov/simstr/HEAD/bench/bench_str.cpp>
  - <https://raw.githubusercontent.com/orefkov/simstr/HEAD/bench/CMakeLists.txt>
  - <https://raw.githubusercontent.com/orefkov/simstr/HEAD/include/simstr/strexpr.h>
  - <https://raw.githubusercontent.com/orefkov/simstr/HEAD/include/simstr/sstring.h>
  - <https://raw.githubusercontent.com/orefkov/simstr/HEAD/bench/results/000-Xeon%20E5-2682%20v4%2C%20Ubuntu%2022%20%28WSL%29%2C%20Clang-22.txt>
  - <https://raw.githubusercontent.com/orefkov/simstr/HEAD/bench/results/002-Xeon%20E5-2682%20v4%2C%20Ubuntu%2022%20%28WSL%29%2C%20GCC-15.txt>
  - <https://raw.githubusercontent.com/orefkov/simstr/HEAD/bench/results/004-Xeon%20E5-2682%20v4%2C%20Windows%2010%2C%20MSVC-19.txt>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/orefkov/simstr`) · [data/wave13/enrich/raw/github_com_orefkov_simstr.json](../../../data/wave13/enrich/raw/github_com_orefkov_simstr.json) (enrichment confidence 0.75)

</details>
