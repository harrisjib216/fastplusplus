# FASTBuild

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Toolchain and build](../README.md) › [Compile caching and distribution](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Zlib` · 🟢 active

> Full build system combining object caching, unity builds and distributed compilation; replaces make/MSBuild, not a wrapper.

| | |
|---|---|
| **Beats** | the same build without FASTBuild's object cache, Unity/Blob builds or distributed compilation (implicit; no baseline tool is named) |
| **Claimed result** | fastbuild.org docs/features page: "Caching can accelerate compile times up to 10x"; "Improvements of 10x or more are not uncommon" for unity/blob builds; "Speedups of 5x are common" for distributed compilation. |
| **Workload** | General C/C++ project builds using FASTBuild's own build description language, covering its object-caching mode and its network-distributed compilation mode; no specific project or file count named. |
| **Metric** | build-time |
| **Adoption** | 1.4k stars; used by many game studios (README: "from small independent teams to some of the largest studios in the world") |
| **Last commit** | 2026-09-20 |
| **Links** | [repository](https://github.com/fastbuild/fastbuild) · [benchmark](https://www.fastbuild.org/docs/features.html) |

## Verdict

fastbuild.org's features page gives first-party, unqualified figures — object caching 'up to 10x', Unity/Blob builds 'improvements of 10x or more', distributed compilation 'speedups of 5x are common' — each measured against the same build without that FASTBuild feature enabled. No workload, hardware, compiler, or flags are given, so these are vendor round numbers, not a reproducible benchmark.

## Use it when

- Large multi-platform (PC/console/mobile) C/C++ game or engine codebase, where you're willing to author the build in FASTBuild's own BFF language
- Team has spare workstation or render-farm capacity to run FBuildWorker for network distribution
- CI or local dev with deterministic compiler output, where object-cache hits repeat across builds and machines
- Cross-compiler shop needing one build tool across MSVC, GCC, Clang, SNC, GreenHills, CodeWarrior, NVCC
- Want unity-build automation without hand-writing jumbo .cpp generation scripts

## Skip it when

- Want to keep an existing CMake/Make/MSBuild/Ninja build and just add caching or distribution without rewriting build files
- No dedicated worker machines or spare network compute — distributed mode adds nothing without hardware to distribute to
- Non-deterministic compiler output or unusual toolchains: issue #1021 (cache errors when system locale differs) and #992 (clang-cl PCH + cache 'fatal error in some situations') show real cache-correctness edge cases
- Linux build farm with &gt;32 cores per worker: issue #1197 reports the CPU-affinity mask is 32-bit, giving a wrong mask on wider machines
- Small or single-machine project where compile time is already short — BFF authoring and cache/worker setup cost may not pay off

## How it is fast

Unity/Blob builds merge many .cpp files into fewer translation units, cutting per-file compiler startup/parse overhead. The object cache stores compiled objects keyed by build inputs and reuses them across machines instead of recompiling identical code. Distributed compilation preprocesses source locally then ships it to idle worker machines running FBuildWorker, so object compilation runs in parallel across a farm rather than being limited to one machine's core count.

## Compared with alternatives

Pick FASTBuild when you're building (or willing to rebuild) a multi-platform C/C++ project around its own BFF language and want unity builds, object cache and worker-farm distribution bundled in one tool. Pick NativeLink or HOMCC instead when you need to keep an existing Bazel/REAPI or distcc-compatible build and only add remote caching or distributed compilation without rewriting build files, or octobuild when the target is specifically Unreal Engine's UBT/UAT pipeline.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none documented for the core build; the OSUI component links native OS UI frameworks (WinAPI on Windows, Cocoa .mm files on macOS) |
| **Minimum toolchain** | not documented as a stated minimum; Linux CI (Linux.yml) builds and tests with GCC 10 and Clang 15 on Ubuntu 22.04 — Windows/macOS minimum compiler versions not checked this session |
| **Platforms** | Windows, Linux and macOS as build hosts (README); used to target PC, Mac, Linux, consoles, smartphones and retro systems as build outputs — specific host CPU architectures not documented |
| **Thread safety** | not documented — FASTBuild is a standalone CLI/executable build tool, not an embeddable library, so this doesn't apply in the usual sense |
| **Drop-in for the baseline** | false — requires authoring or converting your build description into FASTBuild's own BFF language; it is not a wrapper around an existing make/CMake/MSBuild setup |

## Gotchas

- Cache correctness assumes deterministic compiler output; issue #1021 shows cache errors when the system locale differs and #992 shows clang-cl PCH + cache producing a fatal error in some situations
- Distributed compilation is reported to intermittently fail (issue #1058, open, 'Need More Info')
- Linux CPU-affinity helper uses a 32-bit mask (issue #1197), so it can compute the wrong core mask on machines with more than 32 cores
- GitHub's UI reports 'no license' for this repo because the license file lives at Code/LICENSE.TXT rather than repo root, even though it is zlib-licensed

## Caveats and trade-offs

No baseline tool (ccache/sccache/distcc/IncrediBuild) is named. The figures are unqualified marketing-style numbers with no workload, hardware, compiler or flags. The Unity/Blob gain comes from the unity-build technique itself, which other build systems also offer. The page's comparisons with Visual Studio/MSBuild, make and SCons are qualitative only. GitHub reports no license because the license file is at Code/LICENSE.TXT (zlib license text).

Requires adopting FASTBuild's own build-description language/build system rather than being a drop-in wrapper around an existing build; distributed mode needs dedicated worker machines; caching correctness depends on deterministic compiler output.

## Maintenance

Actively maintained — the dev branch (where patches land) was last committed 2026-09-20, days before this entry — and zlib-licensed (Code/LICENSE.TXT), so it's free to vendor; its 1.4k GitHub stars understate real usage since it's mainly distributed via fastbuild.org binaries and used by many closed-source game studios.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): confirm; tier before verification C, tier now C.
- **Tier reason:** The features page gives first-party round numbers ('Caching can accelerate compile times up to 10x', Unity/Blob 'Improvements of 10x or more are not uncommon', distributed 'Speedups of 5x are common') relative to building without those features. It gives no workload, hardware, compiler, flags or code, so these are numbers without methodology.
- **Verifier notes:** All three quoted figures appear verbatim on the features page. The default branch 'main' was last committed 2026-07-26; the 'dev' branch (where patches land) was last committed 2026-09-20, which matches the record, so last_commit was left unchanged. Code/LICENSE.TXT is the zlib license text with an added attribution example, so Zlib/copyable stands.
- **Fields the verifier corrected:** `baseline`, `caveats`
- **Pages the verifier opened:**
  - <https://www.fastbuild.org/docs/features.html>
  - <https://www.fastbuild.org/docs/license.html>
  - <https://github.com/fastbuild/fastbuild>
- **Sources the enricher read:**
  - <https://github.com/fastbuild/fastbuild>
  - <https://github.com/fastbuild/fastbuild/blob/main/README.md>
  - <https://www.fastbuild.org/docs/features.html>
  - <https://www.fastbuild.org/docs/home.html>
  - <https://github.com/fastbuild/fastbuild/blob/main/.github/workflows/Linux.yml>
  - <https://github.com/fastbuild/fastbuild/issues/1197>
  - <https://github.com/fastbuild/fastbuild/issues/1021>
  - <https://github.com/fastbuild/fastbuild/issues/992>
  - <https://github.com/fastbuild/fastbuild/issues/1058>
  - <https://github.com/fastbuild/fastbuild/issues?q=label%3ABug>
- **Raw records:** [data/wave2/verified.json](../../../data/wave2/verified.json) (id `https://github.com/fastbuild/fastbuild`) · [data/wave2/enrich/raw/github_com_fastbuild_fastbuild.json](../../../data/wave2/enrich/raw/github_com_fastbuild_fastbuild.json) (enrichment confidence 0.35)

</details>
