# c4core (charconv/xtoa/atox module)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Number parsing and formatting](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Low-level C++ utility library whose charconv module (xtoa/atox) beats std::to_chars and std::from_chars on integers.

| | |
|---|---|
| **Beats** | std::to_chars, std::from_chars |
| **Claimed result** | README prose (Linux/g++11.2 run): c4::to_chars \~40% to 2x faster than std::to_chars, \~10x-30x faster than sprintf, \~50x-100x faster than stringstream. c4::from_chars \~10%-30% faster than std::from_chars, \~10x faster than scanf, \~30x-50x faster than stringstream. The README also has a text MB/s table for integers. In that table, to_chars vs std::to_chars ranges from 1.07x (u16: 486.40 vs 454.24 MB/s) to 2.44x (i8: 599.98 vs 246.32 MB/s). from_chars vs std::from_chars ranges from 1.05x (u8: 163.06 vs 154.85 MB/s) to 1.54x (i32: 345.53 vs 224.46 MB/s). Float results appear only in PNG charts (g++12.1 / VS2019). |
| **Workload** | CI-run microbenchmarks (c4::xtoa/c4::atox) converting 8/16/32/64-bit signed and unsigned integers and floats to/from decimal ASCII strings, measured in MB/s, against std::to_chars/std::from_chars, sprintf/scanf, and stringstream, on Linux (g++11.2, GCC12.1 charts) and Windows (VS2019). |
| **Metric** | throughput |
| **Compiler and flags** | g++ 11.2 (text claim) / g++ 12.1 Release (Linux charts); MSVC / VS2019 Release (Windows charts); exact optimization flags not shown in README prose |
| **Adoption** | 149 stars |
| **Last commit** | 2026-09-03 |
| **Links** | [repository](https://github.com/biojppm/c4core) · [benchmark](https://github.com/biojppm/c4core/blob/master/README.md) |

## Verdict

On Linux with g++11.2 Release, c4core's own CI microbenchmark (bm/bm_charconv.cpp) shows c4::to_chars beating std::to_chars by 1.07x-2.44x and c4::from_chars beating std::from_chars by 1.05x-1.54x across 8/16/32/64-bit signed and unsigned integers, measured in MB/s. Float/double comparisons exist only as PNG charts from a separate g++12.1 (Linux) / VS2019 (Windows) run; no CPU or hardware is disclosed for either run.

## Use it when

- Hot loops converting many fixed-width integers (u8-u64, i8-i64) to/from decimal ASCII, e.g. log lines or serialization formatting
- Already using c4core/rapidyaml or want one low-level utility library instead of many point solutions
- Comfortable with a substr/csubstr buffer API instead of std::to_chars' pointer-pair + result-struct signature
- Building on a toolchain without full C++17 &lt;charconv&gt;: c4core still gets integer speedups on C++11, and floats route through fast_float
- Want MIT-licensed source that can be vendored as a single amalgamated header (tools/amalgamate.py)

## Skip it when

- Only need fast float/double parsing: use fast_float directly, since c4core's float path is just fast_float underneath with extra library weight on top
- Want a minimal, single-purpose charconv library: c4core pulls in a large general-purpose utility library (span, allocators, error handling, etc.)
- Need the exact std::to_chars/from_chars call signature for drop-in replacement without call-site changes
- Need independently-verified numbers: only the project's own README/CI benchmarks exist (evidence tier C), with no hardware/CPU disclosed
- Targeting old MSVC (&lt;2019): std::to_chars/from_chars interop is unavailable, and the README's text table itself is from an older g++11.2 run vs. current CI's newer compilers

## How it is fast

For integers, c4core uses its own digit-counting and decimal-digit extraction routines (digits_dec()/write_dec()/read_dec()) with no locale handling, format-flag dispatch, or allocation, avoiding overhead present in libstdc++/MSVC STL's std::to_chars/from_chars. For float/double, c4core does not implement its own parsing algorithm: from_chars for floating types is answered by the bundled fast_float submodule (already catalogued separately) when C++17 and the fastfloat option are enabled (the default), so the float speedup is fast_float's algorithm, not original c4core code.

## Compared with alternatives

Pick c4core's charconv when you already want its broader utility library (substr, span, error handling) and only need integer to/from-decimal speed; its documented integer wins (1.05x-2.44x over std) are smaller than Boost.Charconv's or rigtorp/CharConv's claimed multiples, so choose one of those instead — or fast_double_parser/fast_float — if isolated charconv or float-parsing performance alone is the goal.

## Integration

| | |
|---|---|
| **Form** | source-drop (CMake subproject/static lib) or single-header via tools/amalgamate.py |
| **Dependencies** | fast_float (bundled git submodule, used for float/double parsing when C++17 + fastfloat option enabled, the default); sg14 inplace_function (BSL-1.0) and debugbreak (BSD-2-Clause) are bundled for other parts of c4core, not charconv itself |
| **Minimum toolchain** | C++11 minimum for the library and integer xtoa/atox; C++17 with MSVC2019+/GCC or a compiler exposing &lt;charconv&gt; is needed to enable the std::to_chars/from_chars interop path |
| **Platforms** | x64, x86, arm, aarch64, wasm (emscripten), ppc64le, s390x tested in CI; bare-metal, RISC-V and LoongArch reported working via issues/PRs but not in the official CI matrix |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | partial — explain: covers the same numeric types as std::to_chars/from_chars, but c4::to_chars(substr, T) returns size_t and c4::from_chars(csubstr, T\*) returns bool, unlike std's pointer-pair + to_chars_result/from_chars_result interface, so call sites must change |

## Gotchas

- Requires cloning with --recursive (or `git submodule update --init`) for the cmake/, fast_float, and debugbreak submodules; the amalgamation script is the alternative for header-only use
- On MSVC, c4core deliberately disables std::from_chars in favor of fast_float ('prefer fast_float with MSVC'), so float from_chars comparisons on Windows are effectively fast_float vs. an MSVC STL that also uses similar techniques internally
- A static-assertion failure in charconv.cpp on VS2019 was reported (issue #19, closed as duplicate in 2020) — worth checking current MSVC versions before relying on it
- Float/double results in the README exist only as PNG charts (g++12.1 Linux / VS2019 Windows), not in the text MB/s table, which covers integers only

## Caveats and trade-offs

The numbers come from the project's own README and CI benchmark runs, with no independent check. Hardware is not disclosed. The text MB/s table covers integers only. Float comparisons are PNG charts only. The table's range for from_chars vs std::from_chars (\~5%-54%) is wider than the prose '10%-30%'. The README table is from an older g++11.2 run, but current CI uses newer compilers (g++-14, clang-18, VS2022).

Part of a large general-purpose C++ utility library, not a standalone charconv package; when compiled with C++17 and the fast_float path enabled, float/double from_chars performance rides on bundled fast_float (github.com/fastfloat/fast_float, already catalogued) as a dependency — the integer xtoa/atox path is c4core's own code, the float path is not entirely original.

## Maintenance

Actively maintained (last commit 2026-09-03, \~149 stars); MIT-licensed core with permissively-licensed bundled dependencies (fast_float, sg14 BSL-1.0, debugbreak BSD-2-Clause), so it is safely copyable/vendorable, including via the single-header amalgamation script.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification A, tier now C.
- **Tier reason:** Reproducible benchmark code exists in the repo (bm/bm_charconv.cpp, bm_xtoa.cpp, bm_atox.cpp) and runs against std::to_chars/std::from_chars. The README states g++11.2 (text table), plus g++12.1 and VS2019 Release (charts). No hardware is stated anywhere, and the CI runs use GitHub-hosted runners with no CPU model given. So it is not A. It is not B because the numbers are the project's own. That leaves C.
- **Verifier notes:** The record's caveat said only the prose percentages were available as text. That is wrong: the README has a full text MB/s table for integers, and it confirms that c4core beats std::to_chars and std::from_chars in every integer cell. usability changed from mixed to copyable because every part has an OSI license: the MIT core, sg14 (BSL-1.0), fast_float (MIT/Apache/BSL), debugbreak (BSD-2-Clause) and rng (MIT).
- **Fields the verifier corrected:** `claimed_speedup`, `usability`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/biojppm/c4core>
  - <https://github.com/biojppm/c4core/blob/master/README.md>
  - <https://github.com/biojppm/c4core/tree/master/bm>
  - <https://github.com/biojppm/c4core/blob/master/.github/workflows/benchmarks.yml>
  - <https://github.com/biojppm/c4core/blob/master/LICENSE.txt>
  - <https://github.com/biojppm/c4core/blob/master/LICENSE-BOOST.txt>
  - <https://github.com/biojppm/c4core/tree/master/src/c4/ext>
  - <https://github.com/biojppm/c4core/blob/master/src/c4/ext/rng/rng.hpp>
  - <https://github.com/biojppm/c4core/blob/master/src/c4/ext/fast_float_all.h>
  - <https://github.com/biojppm/c4core/blob/master/.gitmodules>
  - <https://github.com/biojppm/debugbreak>
  - <https://github.com/biojppm/cmake>
- **Sources the enricher read:**
  - <https://github.com/biojppm/c4core>
  - <https://github.com/biojppm/c4core/blob/master/README.md>
  - <https://github.com/biojppm/c4core/blob/master/CMakeLists.txt>
  - <https://github.com/biojppm/c4core/blob/master/src/c4/charconv.hpp>
  - <https://github.com/biojppm/c4core/blob/master/LICENSE.txt>
  - <https://github.com/biojppm/c4core/blob/master/LICENSE-BOOST.txt>
  - <https://github.com/biojppm/c4core/blob/master/bm/bm_charconv.hpp>
  - <https://github.com/biojppm/c4core/blob/master/.gitmodules>
  - https://github.com/biojppm/c4core/tree/master (full repo file tree)
  - https://github.com/biojppm/c4core/issues?q=charconv (issue search)
  - https://github.com/biojppm/c4core/issues?q=performance (issue search)
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/biojppm/c4core`) · [data/wave1/enrich/raw/github_com_biojppm_c4core.json](../../../data/wave1/enrich/raw/github_com_biojppm_c4core.json) (enrichment confidence 0.8)

</details>
