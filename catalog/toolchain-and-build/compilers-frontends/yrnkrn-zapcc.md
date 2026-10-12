# zapcc

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Toolchain and build](../README.md) › [Compilers and front ends](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `NCSA` · 🔴 abandoned

> zapcc: a Clang fork with a persistent caching server that rebuilds template-heavy C++ 1.2-3.3x faster than GCC/Clang.

| | |
|---|---|
| **Beats** | GCC, Clang |
| **Claimed result** | Debug full build (-j1): GCC 5.4.0 469s, Clang 3.9 710s, Zapcc++ 214s -- 'zapcc is 3.3 times faster to compile than Clang and around 2 times faster than GCC'. Release build (-j1): GCC 782s, Clang 960s, Zapcc 640s -- 'zapcc is still 1.2 times faster than gcc and 1.5 times faster than clang' |
| **Workload** | Full build of the ETL (Expression Template Library, header-only, template-heavy) test cases: debug at -j1/-j2/-j4, release at -j1 only; link time excluded |
| **Metric** | compile-time |
| **Hardware** | Desktop machine, 4 physical cores, 16GB RAM (exact CPU model not stated) |
| **Compiler and flags** | GCC 5.4.0, Clang 3.9, zapcc++ (beta); ETL debug and release configurations; optimization flags not stated on the page |
| **Adoption** | 1.3k stars |
| **Last commit** | 2020-07-21 |
| **Links** | [repository](https://github.com/yrnkrn/zapcc) · [benchmark](https://baptiste-wicht.com/posts/2016/12/zapcc-cpp-compilation-speed-against-gcc-54-and-clang-39.html) |

## Verdict

On Baptiste Wicht's 2016 ETL (header-only, template-heavy) benchmark on a 4-core/16GB desktop, zapcc++ (beta) built ETL's debug config at -j1 in 214s vs 469s for GCC 5.4.0 (\~2.2x) and 710s for Clang 3.9 (\~3.3x); the release config at -j1 took 640s vs 782s for GCC (\~1.2x) and 960s for Clang (\~1.5x). Colfax Research's independent 2017 compiler comparison found Zapcc 1.0.1 compiling the TMV library in 510s vs 848s for GCC 7.2.0 and 902s for Clang 5.0.0 (\~1.7x) on a 2-socket Xeon Platinum 8168, corroborating the direction and rough magnitude of the gain.

## Use it when

- Large, template/header-heavy C++ codebase (clang- or gcc-compatible source) built repeatedly on Linux x86-64, where CI or local dev-loop compile time dominates
- Iterative development where a single file changes and you rebuild often (the caching server gives its biggest wins here)
- Full debug builds of header-only template libraries similar in shape to ETL (measured 2-3.3x faster than Clang/GCC)
- You already know the project compiles cleanly with vanilla Clang and can dedicate a long-lived background process and extra RAM to the caching server
- You don't need sanitizers and can tolerate an unmaintained, LLVM-r325000-vintage (Feb 2018) fork

## Skip it when

- Plain C or lightly-templated C++, where the README itself says caching gives little to no acceleration
- Any build needing ASan/UBSan/TSan/MSan - explicitly unsupported
- Modern C++17/C++20 code: development stopped in 2020, last synced to LLVM trunk 2018-02-13, and -std=gnu++17 was still rejected as an invalid value as of the last activity on that issue (Dec 2018)
- Correctness-sensitive or release builds: a user reported (issue #42) non-deterministic object files and binaries that segfault at reproducible-but-build-order-dependent locations under parallel (-j&gt;1) builds, not reproduced with plain clang, and it was never resolved
- Windows/macOS targets: only minimally/lightly tested, MSVC ABI and zapcc-cl are explicitly unsupported, and there is no one left maintaining platform fixes

## How it is fast

The zapccs server keeps parsed ASTs, template instantiations, and generated IR/code resident in memory between compiles instead of redoing that work per translation unit, and can reuse results across source files in a way the README compares to link-time inlining decisions being made proactively. This turns repeated compilation of shared, heavily-templated headers (the dominant cost in libraries like ETL) into cache hits instead of full reparses/re-instantiations. The README claims single-file incremental recompiles are typically 10-50x faster than a cold build because only the changed dependency subgraph is reprocessed; full from-scratch builds see smaller (2-5x) gains that scale with how template/header-heavy the project is.

## Compared with alternatives

Pick zapcc over MIR/c2m or TinyCC when the actual cost is template-instantiation and header re-parsing in a large, clang/gcc-compatible C++ codebase (its gains scale with template/header weight); MIR/c2m and TinyCC instead target small/simple C or C-subset inputs for fast one-shot JIT-style compiles and are both still maintained, whereas zapcc has been abandoned since 2020 with an open, unresolved correctness bug (issue #42).

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none beyond a standard LLVM/Clang build toolchain (CMake + Ninja, per README) |
| **Minimum toolchain** | Effectively frozen at Clang/LLVM \~6.0-era conformance (last merged with LLVM r325000, 2018-02-13); build via CMake + Ninja exactly as for LLVM. -std=gnu++17 was not recognized as of the last relevant activity (issue #32, Dec 2018); treat full C++17/C++20 support as unverified/likely absent. |
| **Platforms** | x86-64 Linux (thoroughly tested, primary target); Windows via MSVC or mingw-w64 targeting mingw-w64 32/64-bit (minimally tested; zapcc-cl/MSVC-ABI target explicitly unsupported); macOS via Clang (experimental, lightly tested). No aarch64 or RISC-V support (a RISC-V feature request was closed unresolved). |
| **Thread safety** | Not documented as safe under parallel builds. Issue #42 reports non-deterministic .o output and binaries that segfault at build-order-dependent locations when using -j&gt;1, which the maintainer attributed to cross-translation-unit state reuse in the caching server (not reproduced on plain clang++ 7). |
| **Drop-in for the baseline** | partial — CLI syntax matches clang/clang++ exactly (set CMAKE_CXX_COMPILER=zapcc++), so it slots into a clang-compatible build, but it also requires a persistent background zapccs server, extra RAM, has no sanitizer support, and per user reports can produce non-deterministic or crashing output under parallel builds that the equivalent clang/gcc build did not. |

## Gotchas

- The in-memory server can share/inline state across translation units, making -j&gt;1 builds non-deterministic and, per issue #42, occasionally producing binaries that segfault at reproducible-but-order-dependent locations not seen with plain clang
- -std=gnu++17 was rejected as an invalid value as of the project's last active development (issue #32); it was never fixed before the maintainer confirmed (issue #47, 2021) the project is dead
- zapccs must be killed manually (pkill zapcc) to release memory or to pick up a freshly rebuilt zapcc binary; it also has a configurable memory cap (bin/zapccs.config MaxMemory) that silently resets the entire cache when hit
- README recommends -j should not exceed physical core count + 2, especially on hyperthreaded Intel CPUs that report double the physical core count — oversubscribing the server can make builds slower, not faster

## Caveats and trade-offs

The blog benchmark (2016) predates modern GCC/Clang by many major versions and states no CPU model or flags. The biggest gains are on debug builds (3.3x vs Clang, about 2x vs GCC); release gains are 1.5x/1.2x. Corroboration: Colfax Research 'A Performance-Based Comparison of C/C++ Compilers' (2017-11-11) Table 1 gives TMV library compile times of 510 s for Zapcc 1.0.1 vs 848 s for G++ 7.2.0 and 902 s for Clang 5.0.0 (\~1.66x/\~1.77x, derived from page data) on a 2-socket Xeon Platinum 8168. The -O3 -march=skylake-avx512 lines in that paper are for the compute kernels, not the TMV compile. The project has been abandoned since 2020 (last merged with LLVM trunk 2018-02-13). GitHub reports license NOASSERTION; LICENSE.TXT is the LLVM Release License (University of Illinois/NCSA).

Requires a persistent background caching server (zapccs) that consumes extra RAM; gains shrink for plain C or lightly-templated code; Windows/macOS support only lightly tested; sanitizers unsupported

## Maintenance

Abandoned since 2020 (last commit 2020-07-21, last synced to LLVM trunk 2018-02-13); the maintainer confirmed in a 2021 issue that the project is dead. NCSA/LLVM-Release-licensed and copyable, but it's a full compiler toolchain you'd have to build and maintain yourself, not a small vendorable file, and the known non-determinism/segfault correctness bug (issue #42) was never fixed.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): confirm; tier before verification B, tier now B.
- **Tier reason:** Two independent third-party sources show zapcc beating GCC and Clang on compile time. The Wicht blog tables match the record but give no CPU model or flags. Colfax Research's 2017 compiler comparison (Table 1: TMV compile 510 s Zapcc 1.0.1 vs 848 s G++ 7.2.0 and 902 s Clang 5.0.0, on a 2-socket Xeon Platinum 8168) supports B. It is not A because the TMV compile flags are not stated and its TMV build is not in ColfaxResearch/CompilerComparisonCode.
- **Verifier notes:** All blog numbers match exactly (debug -j1 469/710/214 s; release -j1 782/960/640 s). The release build was measured at -j1 only, not -j1/-j2/-j4. I confirmed the Colfax per-compiler figures directly from its Table 1. If a single URL with a CPU model is preferred, https://colfaxresearch.com/compiler-comparison/ is the stronger B source.
- **Fields the verifier corrected:** `compiler_and_flags`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://baptiste-wicht.com/posts/2016/12/zapcc-cpp-compilation-speed-against-gcc-54-and-clang-39.html>
  - <https://colfaxresearch.com/compiler-comparison/>
  - <https://github.com/ColfaxResearch/CompilerComparisonCode>
  - <https://github.com/yrnkrn/zapcc>
- **Sources the enricher read:**
  - <https://github.com/yrnkrn/zapcc>
  - <https://github.com/yrnkrn/zapcc/blob/master/README.md>
  - <https://github.com/yrnkrn/zapcc/blob/master/LICENSE.TXT>
  - <https://github.com/yrnkrn/zapcc/issues/32>
  - <https://github.com/yrnkrn/zapcc/issues/42>
  - <https://github.com/yrnkrn/zapcc/issues/47>
- **Raw records:** [data/wave2/verified.json](../../../data/wave2/verified.json) (id `https://github.com/yrnkrn/zapcc`) · [data/wave2/enrich/raw/github_com_yrnkrn_zapcc.json](../../../data/wave2/enrich/raw/github_com_yrnkrn_zapcc.json) (enrichment confidence 0.7)

</details>
