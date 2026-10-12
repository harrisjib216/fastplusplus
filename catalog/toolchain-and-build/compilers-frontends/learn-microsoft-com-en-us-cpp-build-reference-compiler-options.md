# Microsoft Visual C++ (MSVC cl.exe)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Toolchain and build](../README.md) › [Compilers and front ends](README.md)</sub>

**Tier D** (directional, no numbers) · Study only · `C++` · `proprietary (closed-source Microsoft toolchain)` · 🟢 active

> Microsoft's closed C++ compiler; one Node.js report had it compiling \~2.5x faster than clang-cl, but only versus no-PCH clang-cl.

| | |
|---|---|
| **Beats** | clang-cl (Clang's MSVC-compatible driver) |
| **Claimed result** | Issue #55208 (StefanStojanovic, 2024-10-01): 'ClangCL compilation is \~2.5 slower (less with x64, more with ARM64)' than MSVC when building Node.js with vcbuild.bat, attributed to ClangCL not using precompiled headers while MSVC did. PR #55249 (merged 2024-10-11) enabled PCH for clang-cl and states it 'improves ClangCL compilation time drastically'; no before/after or MSVC-vs-ClangCL numbers are given, so no valid equal-settings ratio exists on the page. |
| **Workload** | Building Node.js on Windows with vcbuild.bat using MSVC versus vcbuild.bat clang-cl. |
| **Metric** | compile-time |
| **Adoption** | Standard Windows C++ toolchain; evidence is a Node.js build issue (Oct 1, 2024) |
| **Links** | [repository](https://learn.microsoft.com/en-us/cpp/build/reference/compiler-options) · [benchmark](https://github.com/nodejs/node/issues/55208) |

## Verdict

A Node.js Windows build contributor reported in October 2024 that building Node with vcbuild.bat clang-cl took about 2.5x as long as with MSVC, with no hardware, versions, flags or timings, and attributed the gap to clang-cl builds lacking precompiled headers; the PCH fix for clang-cl landed eleven days later without numbers. No measurement of cl.exe versus clang-cl at equal build settings was found.

## Use it when

- Windows-only MSBuild solutions that already depend on cl /MP and /Yc-/Yu precompiled headers, where moving to clang-cl without Ninja-style parallelism and PCH would lengthen builds
- C++/CLI code (/clr), which clang-cl's option table lists as unsupported
- Debug-build edit-compile loops on Windows, where Lemire's 2023 'Visual Studio versus ClangCL' post (search snippet only) says MSVC compiles faster than ClangCL

## Skip it when

- Throughput-bound SIMD or parsing code: simdjson parsed twitter.json at 1.31 GB/s built with MSVC 19.25 vs 2.22 GB/s with ClangCL 9.0 (ClangCL 1.70x, derived from page data), and llama.cpp PR #10668 measured clang with Ninja 15.68% faster prompt processing than MSVC on an AMD 7600X
- Projects that track Node.js or V8: Node.js 24.0.0 (2025-05-06) removed MSVC support and requires ClangCL on Windows
- CPU-heavy Windows on ARM builds: llama.cpp's build docs say MSVC's ARM NEON intrinsic support may be incomplete, and its release workflow builds the CPU backend with clang
- Cross-platform or open toolchains: cl.exe is closed-source and runs only on Windows hosts
- As evidence of a compile-time edge: no equal-settings (both with PCH, both parallel) comparison was found; the only ratio compares PCH with no PCH

## How it is fast

Nothing measured isolates compiler speed. The reported gap came from precompiled headers: Node's MSVC builds used PCH so shared headers were parsed once, while its gyp setup gave clang-cl no PCH until PR #55249. cl.exe can also compile several sources in parallel inside one invocation (/MP), which clang-cl's option table lists as unsupported, so MSBuild builds that rely on /MP rather than a parallel generator such as Ninja run serially under clang-cl.

## Compared with alternatives

The catalogued siblings (icpx, AOCC, zapcc, TinyCC, MIR/c2m, cg_clif) target generated-code speed or one-shot compile speed, mostly on Linux; pick MSVC only for Windows MSBuild solutions that need cl.exe-specific features such as /clr or /MP-driven builds, and prefer clang-cl or icpx (intel/llvm also builds on 64-bit Windows) when runtime speed matters.

## Integration

| | |
|---|---|
| **Form** | compiler toolchain (closed-source binary in Visual Studio / Build Tools) |
| **Dependencies** | Visual Studio or Build Tools with the 'Desktop development with C++' workload (MSVC STL, Windows SDK) |
| **Minimum toolchain** | not applicable; the cited issue names no MSVC version, and Node's current build guide targets Visual Studio 2026 or VS 2022 17.14 |
| **Platforms** | Windows hosts; x64 and ARM64 targets (Node lists ARM64/ARM64EC build tools) |
| **Thread safety** | not applicable (compiler) |
| **Drop-in for the baseline** | partial — both take cl.exe-style options and plug into MSBuild as platform toolsets, but code that now requires Clang (Node.js 24+ with its V8) will not build with cl.exe, and in the other direction clang-cl ignores /MP and rejects /clr |

## Gotchas

- The \~2.5x figure (no hardware, versions, flags or timings; 'less with x64, more with ARM64') compares MSVC with precompiled headers against clang-cl without them; Node PR #55249 enabled PCH for clang-cl through gyp-next (merged 2024-10-11, backported to v22.12.0) and published no before/after numbers, so the evidence measures a build-configuration difference that no longer exists.
- clang-cl lists /MP under unsupported options, so reports that clang-cl builds are several times slower in MSBuild projects (a llama.cpp-related search snippet cites 3-4x) usually measure lost per-invocation parallelism; build with Ninja or another parallel generator before comparing.
- Clang does not instantiate templates into a PCH by default (-fpch-instantiate-templates defaults off), but clang-cl /Yc turns it on by default in current LLVM's driver; a January 2020 cfe-dev thread (search snippet only) reported clang-cl PCH builds about 3x slower than MSVC for one codebase before that change, so older comparisons may not hold.
- Lemire's Node issue #52809 (May 2024) calls a warm-ccache ClangCL build of 15-20 minutes an improvement over MSVC but gives no MSVC figure; cached versus uncached, so it is not an equal-settings counter-measurement either.

## Known shortcomings

- Downgraded C to D: the Node.js issue #55208 '\~2.5x slower' comparison ran MSVC with precompiled headers against clang-cl without them; PR #55249 (merged 2024-10-11) fixed that and the gap is obsolete. simdjson #847 confirms MSVC-built code runs slower (1.3051 vs 2.2221 GB/s). Lemire's 2023 post was blocked (snippet only).
- Enricher: Node.js 24.0.0 (2025-05-06) removed MSVC support and requires ClangCL, so the evidence workload is gone; clang-cl lists /MP and /clr as unsupported and its /Yc now enables -fpch-instantiate-templates by default. Counter-evidence: llama.cpp PR #10668 found clang plus Ninja 15.68% faster than MSVC at runtime. No equal-settings compile-time comparison found; learn.microsoft.com blocked.

## Caveats and trade-offs

Single issue report by a Node.js Windows build contributor with no hardware, compiler versions, flags or raw timings; the stated cause is that MSVC used precompiled headers and clang-cl did not, and the issue was closed by Node.js PR #55249 which enables PCH for clang-cl, so the 2.5x gap measured a build-configuration difference and is obsolete. MSVC is a closed binary with no repo; usability reference. Counter-evidence on generated-code speed, opened: simdjson issue #847 (jkeiser, 2020-05-01) 'MSVC simdjson twice as slow as ClangCL': twitter.json overall 1.3051 (MSVC 19.25.28614) vs 2.2221 (ClangCL 9.0.0), stage 1 2.3777 vs 5.4161, stage 2 3.3898 vs 4.6401; issue #812 shows the same pattern (per the search agent). Weak extra compile-time data (search agent): vcpkg issue #15961, about 36 s MSVC on Windows vs about 1 min 10 s GCC under WSL, different platforms, no versions or flags. Search-snippet only (pages blocked, not opened): Daniel Lemire's 2023-02-27 post 'Visual Studio versus ClangCL' (VS 2022, ClangCL on LLVM 15, i7-11370 Tiger Lake, simdutf) says compiling with ClangCL takes much longer and that in Debug MSVC compiles faster, while ClangCL Release code can be up to 40% faster; a llama.cpp PR #10668 snippet attributes a 3-4x clang build slowdown to MSVC spawning parallel cl processes (/MP), another configuration artifact; a Chrome team post reportedly says building Chrome with Clang is about 15% slower than MSVC. The docs.microsoft.com URL in the list is a C++/CLI page with no performance data; learn.microsoft.com and Microsoft devblogs were blocked.

Proprietary closed-source compiler (the open part is MSVC STL, microsoft/STL, not benchmarked here); Windows-oriented; in the numeric runtime comparisons found MSVC-generated code was often slower than clang-cl or GCC.

## Maintenance

Actively shipped with Visual Studio but closed-source and Windows-only, so usability is reference; the evidence workload is gone, since Node.js 24 (May 2025) dropped MSVC builds and requires ClangCL.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): downgrade; tier before verification C, tier now D.
- **Tier reason:** nodejs/node issue #55208 gives only an approximate '\~2.5 slower' for ClangCL with no hardware, versions, flags or timings, and the issue itself attributes the gap to ClangCL builds not using precompiled headers while MSVC builds did; PR #55249 enabled PCH for clang-cl and 'improves ClangCL compilation time drastically'. The only number therefore measures PCH versus no PCH (a crippled baseline, AssemblyScript precedent), not compiler speed at equal settings, leaving only directional evidence.
- **Verifier notes:** Issue and PR opened: the \~2.5x figure is real but it measures MSVC-with-PCH vs clang-cl-without-PCH and was fixed by PR #55249, so downgrade C to D (crippled-baseline precedent, not a reject). Shortcomings to record: no methodology, configuration artifact rather than compiler speed, gap closed in Oct 2024, and MSVC-generated code is slower than ClangCL (simdjson #847, 1.3051 vs 2.2221 GB/s, ClangCL 1.70x faster, derived from page data). Lemire's 2023 post (snippet only) is the best lead for an equal-settings compile-time comparison if lemire.me becomes reachable.
- **Fields the verifier corrected:** `claimed_speedup`, `license`, `caveats`
- **Shortcomings recorded by:** verifier batch-08 (wave 2); enricher (wave 2)
- **Pages the verifier opened:**
  - <https://github.com/nodejs/node/issues/55208>
  - <https://github.com/nodejs/node/pull/55249>
  - <https://github.com/simdjson/simdjson/issues/847>
- **Sources the enricher read:**
  - https://learn.microsoft.com/en-us/cpp/build/reference/compiler-options (EGRESS_BLOCKED)
  - <https://github.com/nodejs/node/issues/55208>
  - <https://github.com/nodejs/node/pull/55249>
  - <https://github.com/nodejs/node/issues/52809>
  - <https://raw.githubusercontent.com/nodejs/node/main/BUILDING.md>
  - <https://raw.githubusercontent.com/nodejs/node/main/doc/changelogs/CHANGELOG_V24.md>
  - <https://github.com/simdjson/simdjson/issues/847>
  - <https://github.com/ggml-org/llama.cpp/pull/10668>
  - <https://raw.githubusercontent.com/ggml-org/llama.cpp/master/docs/build.md>
  - <https://raw.githubusercontent.com/intel/llvm/sycl/clang/include/clang/Options/Options.td>
  - <https://raw.githubusercontent.com/llvm/llvm-project/main/clang/lib/Driver/ToolChains/Clang.cpp>
  - https://lists.llvm.org/pipermail/cfe-dev/2020-January/064321.html (EGRESS_BLOCKED; search snippet only)
- **Raw records:** [data/wave2/verified.json](../../../data/wave2/verified.json) (id `https://learn.microsoft.com/en-us/cpp/build/reference/compiler-options`) · [data/wave2/enrich/raw/learn_microsoft_com_en_us_cpp_build_reference_compiler_options.json](../../../data/wave2/enrich/raw/learn_microsoft_com_en_us_cpp_build_reference_compiler_options.json) (enrichment confidence 0.55)

</details>
