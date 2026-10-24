# CMake precompiled headers (target_precompile_headers)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Toolchain and build](../README.md) › [Compile caching and distribution](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> CMake 3.16+ target_precompile_headers: parses a shared header set once per target instead of once per source file.

| | |
|---|---|
| **Beats** | ordinary one-translation-unit-per-source CMake build (same target without precompiled headers) |
| **Claimed result** | Qt Creator: 22.09% speed-up with MinGW GCC 8.1.0, 37.28% with Visual C++ 2017, 30.66% with Clang-cl 8.0.0 (from search summaries of the Qt blog post; snippet only); the post says a few CMake lines give a 20-40% speed increase without changing sources. |
| **Workload** | Qt Creator build on Windows 10 with target_precompile_headers (CMake merge request 3553 prototype) against the same build without precompiled headers, with three compilers. |
| **Metric** | build-time |
| **Hardware** | Windows 10 machine with an AMD Ryzen CPU (model not shown in the summary) |
| **Compiler and flags** | MinGW GCC 8.1.0, Visual C++ 2017, Clang-cl 8.0.0 (versions per search summary); flags and build type not shown |
| **Adoption** | 8.1k stars (GitHub mirror of the upstream CMake repository); target_precompile_headers ships since CMake 3.16 |
| **Last commit** | 2026-10-24 |
| **Links** | [repository](https://github.com/kitware/cmake) · [benchmark](https://www.qt.io/blog/2019/08/01/precompiled-headers-and-unity-jumbo-builds-in-upcoming-cmake) |

## Verdict

The only CMake-specific timings are the implementer's 2019 Qt blog post (unreachable here; figures from search summaries): a CMake build of Qt Creator on one Windows 10 Ryzen machine, using the pre-release MR 3553 code, was 22.09% faster with MinGW GCC 8.1.0, 37.28% with Visual C++ 2017 and 30.66% with Clang-cl 8.0.0 than the same build without PCH. If these are time saved, as the same author's unity-build MR figures are, they equal about 1.28x, 1.59x and 1.44x (derived from page data); there is no CPU model, flags, run count or benchmark code.

## Use it when

- Header-heavy C++ targets where many sources include the same stable, expensive headers (STL, Qt, Boost, windows.h, a large in-house framework) and front-end parsing dominates compile time.
- MSVC and clang-cl builds on Windows: the only published CMake numbers (the implementer's 2019 Qt Creator run) show 37.28% with Visual C++ 2017 and 30.66% with Clang-cl 8.0.0 against 22.09% with MinGW GCC 8.1.0.
- Clang 18+ builds: LLVM's own CMake now enables target_precompile_headers by default for Clang 18 and newer (and disables it for GCC), and an LLVM RFC reported 1.5-2x faster LLVM builds (search snippet only; the thread was unreachable).
- Groups of targets with identical compile flags (test executables, plugins) that can share one PCH through REUSE_FROM, so the header set is compiled once for all of them.
- Replacing a hand-maintained stdafx.h/pch.h scheme or the cotire module with a generator-independent, built-in mechanism.

## Skip it when

- GCC builds: LLVM's HandleLLVMOptions.cmake turns PCH off by default with GCC because, tested with GCC 14 and 15, it gave very little compile-time improvement while substantially increasing build-directory size.
- Headers that change often: the PCH is force-included into every source of the target, so editing any precompiled header rebuilds the PCH and recompiles the whole target (and every target reusing it); headers used by only one or two sources add cost without benefit.
- Builds behind sccache, or ccache with non-Clang compilers: LLVM disables PCH there by default because sccache does not support PCH and ccache can return stale objects when only a macro definition changes (ccache issue 1668, sccache issues 615 and 2562); clang-cache and C++20-modules builds are excluded too.
- Very large header sets: llvm-project issue 61750 reports a PCH built from mlpack.hpp taking 190 s and 7.8 GB to build with Clang 17 and making an empty int main() take 90 s and 4.1 GB to compile (open, no diagnosis).
- Installed or exported library targets: CMake's docs say to avoid PUBLIC/INTERFACE precompile headers there (or wrap them in \$&lt;BUILD_INTERFACE:...&gt;), because consumers should choose their own PCH.

## How it is fast

Precompiled headers: the compiler front end preprocesses, parses and analyses the listed headers once and serialises that state to disk; each translation unit loads the image instead of re-parsing the same STL, Qt or Boost headers. The gain scales with the share of each TU's front-end time spent in the shared headers. For Clang 11+ (not AppleClang) CMake also passes -fpch-instantiate-templates by default (PCH_INSTANTIATE_TEMPLATES, CMake 3.19), so template instantiations are done once while building the PCH.

## Compared with alternatives

Pick PCH when a single machine's clean or CI build is dominated by re-parsing the same headers and you want a gain without a cache server or build farm; it keeps one translation unit per source, so unlike the sibling CMake unity-build entry it adds no ODR clashes and keeps incremental rebuilds fine-grained. It complements rather than replaces sccache/ccache, distcc/icecream or FASTBuild, but check the cache-compatibility caveats before combining it with sccache or with ccache on GCC/MSVC.

## Integration

| | |
|---|---|
| **Form** | build-system feature (CMake command and target properties; nothing to link) |
| **Dependencies** | CMake 3.16+ and a compiler with PCH support (GCC, Clang/AppleClang, MSVC, clang-cl) |
| **Minimum toolchain** | CMake 3.16 (PCH_WARN_INVALID 3.18, PCH_INSTANTIATE_TEMPLATES 3.19 with Clang 11+, ALIAS targets 4.5, PCH_WARNINGS in the 4.6 docs on master) |
| **Platforms** | Any CMake platform with GCC (.gch), Clang/AppleClang (.pch) or MSVC/clang-cl (.pch with /Yc and /Yu); Xcode and FASTBuild generators have their own code paths; multi-arch Apple builds get one PCH per architecture |
| **Thread safety** | not applicable (build-time feature) |
| **Drop-in for the baseline** | partial — no source changes are needed, but every source now sees the precompiled headers force-included, which can mask missing #includes and introduce name collisions (per the LLVM RFC), and Objective-C/C++ or other-language files may need SKIP_PRECOMPILE_HEADERS |

## Gotchas

- CMake marks the generated PCH header as a system header (#pragma GCC/clang system_header), so warnings from the precompiled headers silently disappear; the PCH_WARNINGS property (4.6 docs) restores them, and LLVM clears the undocumented CMAKE_PCH_PROLOGUE for the same reason (CMake issue 21219).
- REUSE_FROM requires identical compile options, flags and definitions on both targets; if they differ the compiler may be unable to use the PCH, and with GCC only the -Winvalid-pch warning (on by default through PCH_WARN_INVALID since 3.18) reports it. LLVM disables reuse for targets with non-default RTTI/EH or with C sources.
- Compiler caches need extra flags: LLVM adds -Xclang -fno-pch-timestamp for Clang and -fpch-preprocess for GCC so ccache can cache PCH builds, and enables ccache depend mode when PCH is on (llvm-project PR 225118).
- PCH artifacts are per language: Objective-C (.m) and Objective-C++ (.mm) files in C/C++ targets can fail to compile with Ninja/Makefile generators until marked SKIP_PRECOMPILE_HEADERS.

## Known shortcomings

- Implementer's own numbers (Qt Creator build 22.09/37.28/30.66%), seen only in search snippets: the Qt blog and Kitware MRs were unreachable from the cloud session. One machine, no CPU model, no benchmark code.
- Enricher: no independent numbers; LLVM disables PCH by default with GCC, sccache and non-Clang ccache (little gain, stale objects); PCH warnings hidden as a system header; heavy PCHs can cost more than they save (llvm-project #61750).

## Caveats and trade-offs

Snippet only: www.qt.io could not be opened (host unresolvable from this container), so the percentages come from WebSearch result summaries of the 2019-08-01 Qt blog post and need re-checking on the page. Single machine, one project, 2019, measured on the pre-release merge request, not the shipped 3.16 code; CPU model and flags missing; the percentage definition (time saved or speed ratio) is not clear from the summary. The kitware/cmake repo carries the implementation and docs but no benchmark code or timings (Help/command/target_precompile_headers.rst has no numbers). The book's companion example (ch07/06-precompile, a hello-world) carries no timings. [retier] Enricher: if the Qt Creator percentages (22.09/37.28/30.66%) are time saved, they correspond to about 1.28x/1.59x/1.44x (derived). LLVM's HandleLLVMOptions.cmake turns PCH off by default with GCC (GCC 14/15 gave very little gain and a bigger build directory), with sccache, and with ccache on non-Clang compilers (stale objects when only a macro changes). CMake marks the PCH as a system header, hiding its warnings. llvm-project issue 61750: mlpack's PCH takes 190 s and 7.8 GB to build, an empty main() 90 s and 4.1 GB. An LLVM RFC claim of 1.5-2x was seen only as a snippet.

Implemented in Source/cmLocalGenerator.cxx (AddPchDependencies) with PRECOMPILE_HEADERS, INTERFACE_PRECOMPILE_HEADERS, SKIP_PRECOMPILE_HEADERS. Needs a sensible set of headers to precompile; a Qt mailing-list thread cited in search results argued that precompiling headers used only once or twice wastes time, and an ITK developer reported no significant reduction in their tests. Projects should avoid PUBLIC or INTERFACE precompile headers on exported targets (CMake docs).

## Maintenance

Actively developed (GitHub mirror commit on 2026-10-24, v4.4.4 released 2026-10-02, v4.5.0-rc1 on 2026-10-15) and BSD-3-Clause; nothing to vendor, since it ships in every CMake from 3.16.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): confirm; tier before verification C, tier now C.
- **Tier reason:** The only numbers are in the 2019-08-01 Qt blog post by the feature's implementer (single Windows 10 Ryzen machine, one project, no CPU model, flags or benchmark code); the page is unreachable from this container (getaddrinfo ENOTFOUND www.qt.io and qt.io), and two independent WebSearch summaries give the same Qt Creator figures (22.09% MinGW GCC 8.1.0, 37.28% Visual C++ 2017, 30.66% Clang-cl 8.0.0), so snippet-only first-party evidence stays at C.
- **Verifier notes:** Could not open benchmark_url (DNS blocked) or CMake MR 3553 on gitlab.kitware.com (also ENOTFOUND); the percentages are confirmed only via search summaries and an enricher with egress to qt.io should re-check them and the percentage definition. The GitHub mirror Kitware/CMake: BSD-3-Clause, 8.1k stars, 'Mirror of CMake upstream repository', last commit 2026-10-24; Help/command/target_precompile_headers.rst (versionadded 3.16) has no numbers.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-11 (wave 2 book seed pass, 2026-10-24); enrichment (wave 2 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://github.com/Kitware/CMake>
  - <https://github.com/Kitware/CMake/commits/master>
  - <https://raw.githubusercontent.com/Kitware/CMake/HEAD/Help/command/target_precompile_headers.rst>
  - <https://raw.githubusercontent.com/Kitware/CMake/HEAD/LICENSE.rst>
- **Sources the enricher read:**
  - <https://github.com/Kitware/CMake>
  - <https://github.com/Kitware/CMake/tags>
  - <https://github.com/Kitware/CMake/commits/master>
  - <https://raw.githubusercontent.com/Kitware/CMake/HEAD/Help/command/target_precompile_headers.rst>
  - <https://raw.githubusercontent.com/Kitware/CMake/HEAD/Help/prop_tgt/PRECOMPILE_HEADERS.rst>
  - <https://raw.githubusercontent.com/Kitware/CMake/HEAD/Help/prop_tgt/PRECOMPILE_HEADERS_REUSE_FROM.rst>
  - <https://raw.githubusercontent.com/Kitware/CMake/HEAD/Help/prop_tgt/INTERFACE_PRECOMPILE_HEADERS.rst>
  - <https://raw.githubusercontent.com/Kitware/CMake/HEAD/Help/prop_sf/SKIP_PRECOMPILE_HEADERS.rst>
  - <https://raw.githubusercontent.com/Kitware/CMake/HEAD/Help/prop_tgt/DISABLE_PRECOMPILE_HEADERS.rst>
  - <https://raw.githubusercontent.com/Kitware/CMake/HEAD/Help/prop_tgt/PCH_INSTANTIATE_TEMPLATES.rst>
  - <https://raw.githubusercontent.com/Kitware/CMake/HEAD/Help/prop_tgt/PCH_WARN_INVALID.rst>
  - <https://raw.githubusercontent.com/Kitware/CMake/HEAD/Help/prop_tgt/PCH_WARNINGS.rst>
  - <https://raw.githubusercontent.com/Kitware/CMake/HEAD/Help/variable/CMAKE_PCH_INSTANTIATE_TEMPLATES.rst>
  - <https://raw.githubusercontent.com/Kitware/CMake/HEAD/Help/variable/CMAKE_PCH_WARN_INVALID.rst>
  - <https://raw.githubusercontent.com/Kitware/CMake/HEAD/Help/release/3.16.rst>
  - <https://raw.githubusercontent.com/Kitware/CMake/HEAD/Source/cmLocalGenerator.cxx>
  - <https://raw.githubusercontent.com/Kitware/CMake/HEAD/Modules/Compiler/Clang.cmake>
  - <https://raw.githubusercontent.com/Kitware/CMake/HEAD/Modules/Compiler/GNU.cmake>
  - <https://raw.githubusercontent.com/Kitware/CMake/HEAD/Modules/Platform/Windows-MSVC.cmake>
  - <https://raw.githubusercontent.com/llvm/llvm-project/main/llvm/cmake/modules/AddLLVM.cmake>
  - <https://raw.githubusercontent.com/llvm/llvm-project/main/llvm/cmake/modules/HandleLLVMOptions.cmake>
  - <https://raw.githubusercontent.com/llvm/llvm-project/main/llvm/docs/CMake.md>
  - <https://raw.githubusercontent.com/llvm/llvm-project/main/llvm/docs/ReleaseNotes.md>
  - <https://github.com/llvm/llvm-project/commits/main/llvm/cmake/modules/HandleLLVMOptions.cmake>
  - <https://github.com/llvm/llvm-project/issues/61750>
  - https://www.qt.io/blog/2019/08/01/precompiled-headers-and-unity-jumbo-builds-in-upcoming-cmake (fetch failed: getaddrinfo ENOTFOUND www.qt.io; content from WebSearch summaries)
  - https://discourse.llvm.org/t/rfc-use-pre-compiled-headers-to-speed-up-llvm-build-by-1-5-2x/89345 (not fetched; discourse.llvm.org unresolvable; WebSearch summary only)
- **Raw records:** [data/wave2/verified.json](../../../data/wave2/verified.json) (id `paper:book-cmake-precompiled-headers`) · [data/wave2/enrich/raw/paper_book_cmake_precompiled_headers.json](../../../data/wave2/enrich/raw/paper_book_cmake_precompiled_headers.json) (enrichment confidence 0.65)

</details>
