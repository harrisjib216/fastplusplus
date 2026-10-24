# C++20 modules instead of header inclusion (Alibaba Hologres case)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Toolchain and build](../README.md) › [Preprocessors and code generators](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `no license` · ⚪ unknown

> Field report: moving Alibaba's Hologres code base from #include headers to C++20 named modules cut its compile time 42%.

| | |
|---|---|
| **Beats** | header-based includes (#include); whether precompiled headers were in the baseline is not confirmed |
| **Claimed result** | Alibaba reports C++20 modules cut Hologres compile time by 42% (blog title '42% Boost in Compilation Efficiency! A Practical Analysis of C++ Modules'); snippet says modules have run on the Hologres mainline for more than a year and a half. A snippet also mentions an import-std test of about 0.03 s, 'an order of magnitude' better than headers (unverified). |
| **Workload** | Compile time of Alibaba's Hologres mainline code base after moving from header inclusion to C++20 modules (per search-result snippet of the Alibaba Cloud blog; the page itself could not be opened). |
| **Metric** | compile-time |
| **Compiler and flags** | Alibaba Cloud Compiler, an in-house Clang/LLVM-based compiler (per search snippet); version and flags not stated. |
| **Adoption** | Used on the Hologres mainline (Alibaba Cloud data warehouse), per the blog snippet |
| **Links** | [benchmark](https://www.alibabacloud.com/blog/42%25-boost-in-compilation-efficiency-a-practical-analysis-of-c%2B%2B-modules_601974) |

## Verdict

Alibaba Cloud's blog (English and Chinese versions, both seen only through search snippets because the pages did not resolve here) says C++20 modules have run on the Hologres mainline for more than a year and a half and reduced its compile time by 42%, using Alibaba Cloud Compiler built from open-source Clang/LLVM; the baseline is header inclusion with no stated use of precompiled headers, and no compiler version, flags, hardware, build type or full-versus-incremental split is published. Other projects report anything from roughly halving full builds (Infinity, per snippet) to slower builds (LLVM Discourse thread), so the 42% is project-specific.

## Use it when

- Large C++ code bases where front-end time on heavy, widely included headers (standard library, template-heavy internal libraries) dominates full builds.
- Teams that control the whole toolchain: Clang 16+ (or GCC 14+, MSVC 14.34+) with CMake 3.28+ and Ninja 1.11+, and Clang 18.1.2+ / GCC 15+ / MSVC 14.36+ if you want import std through CMake.
- New code or internal libraries that can adopt module interfaces from the start, or libraries that can ship a named-module wrapper next to their headers (the export-using style that keeps the ABI).
- Projects whose header hygiene is already good, since duplicated global-module-fragment includes erase much of the gain.

## Skip it when

- Code bases that already build fast with precompiled headers, unity builds or a lightweight core API: the {fmt} author reported no measurable build speed-up from modules over the lightweight core API (search snippet), and the Hologres post's baseline may not have included PCH.
- When many module units include the same big headers in their global module fragments: Clang's performance tips warn that duplicated declarations make importers compile more slowly, and an LLVM Discourse thread ('Modules increased build times', snippet only) found half the compile time spent reading modules.
- Mixed toolchains or IDE/tooling pipelines that do not yet understand modules, Make-based builds, or Visual Studio generators if you need import std (CMake supports import std only with Ninja generators).
- Builds that rely on CMake UNITY_BUILD: scanned module sources are excluded from unity builds.
- Shipping libraries to outside users whose ABI must not change: the ABI-breaking transition style changes name mangling and module initializers.

## How it is fast

Header inclusion re-preprocesses and re-parses the same headers in every translation unit (the post's hello-world example says &lt;iostream&gt; alone expands to about 30,000 lines, roughly 1 MB, under libstdc++); a module interface is compiled once to a BMI and later imports deserialize it lazily. Clang's documentation describes modules as 'a kind of cache to speed up compilation'; Reduced BMIs (-fmodules-reduced-bmi) and, from Clang 19, non-cascading BMI changes cut the rebuilds caused by edits to transitive dependencies. Clang can also preload a prebuilt std BMI with -fmodule-file=&lt;std BMI&gt; to get most of the std-module benefit without rewriting includes.

## Compared with alternatives

The siblings (asp staged parsers, RapidProto, Zserio, FlatBuffers, vtprotobuf) speed up generated code at run time; this entry is the one to read when the problem is your own C++ build time rather than parse or serialization speed.

## Integration

| | |
|---|---|
| **Form** | language feature (C++20 named modules); no package to install |
| **Dependencies** | A module-aware compiler and a dependency-scanning build system: CMake 3.28+ with the Ninja (1.11+) or Visual Studio 17 2022+ generators, or xmake; Hologres itself used Alibaba Cloud Compiler (in-house, based on open-source Clang/LLVM, per post snippets). |
| **Minimum toolchain** | C++20. CMake scanning: Clang 16.0+, GCC 14+, MSVC toolset 14.34+ (VS 17.4+). CMake import std: Clang 18.1.2+ with libc++ or libstdc++, GCC 15+ (16+ on macOS), MSVC 14.36+ (VS 17.6+). Hologres compiler version not documented. |
| **Platforms** | Any platform the compiler supports; the Hologres post's experiments ran on Alibaba Cloud Linux (Alinux, per snippet). CMake notes Ubuntu releases before 26.04 ship broken libstdc++.modules.json files for import std. |
| **Thread safety** | not applicable (compile-time technique) |
| **Drop-in for the baseline** | partial — the std module can be preloaded with Clang's -fmodule-file without source changes, but converting project headers means writing module interface units, reordering includes and imports, and possibly changing the library ABI. |

## Gotchas

- Clang rejects a BMI used with different language-dialect options (for example built with -std=c++20, imported with -std=c++23); every importer must match the module's dialect flags.
- #include of a header after an import of a module that already contains it is rejected in Clang today (llvm-project issue #61465); keep includes before imports or move everything to imports.
- Clang's cross-TU ODR checking has many false positives and is disabled for the global module fragment by default; BMIs drop the preferred_name attribute, so debuggers show uglier type names.
- The reported 0.03 s 'import std' hello-world time excludes building the std module itself, which is precompiled once; the 42% figure does not say whether it covers full or incremental builds.

## Known shortcomings

- Snippet only (the Alibaba Cloud post was unreachable); a 42% compile-time cut on an in-house Clang/LLVM build of a closed codebase; import std at 0.03 s excludes building the std module; no public code.
- Enricher: still snippet only (alibabacloud.com, help.aliyun.com, discourse.llvm.org unreachable); no stated baseline (PCH or not, full or incremental); in-house Clang-based compiler; the 0.03 s import std excludes building the std module; other projects report mixed module results.

## Caveats and trade-offs

Snippet only: www.alibabacloud.com failed to resolve (getaddrinfo ENOTFOUND) in this session, so the numbers, compiler, flags, hardware and baseline details come from WebSearch result summaries, not from the page. Vendor blog about a product the vendor sells, so tier C at best. Hologres is a commercial Alibaba Cloud product with no public source repository found, no benchmark code is public, compiler and flags are unknown, and it is unclear whether the 42% covers full or incremental builds, whether it includes the standard library, or whether a precompiled-header baseline was used. Independent reports in the same search put module speedups between 10% and 50% and one LLVM forum thread reports build times increasing after migrating to modules, so the figure is plausible but project-specific. Listed 'repo_url' in the assignment is the blog page, not a code repository. [verifier] Re-checked by snippet only: the English post and its Chinese original (https://developer.aliyun.com/article/1634418) were both unreachable (getaddrinfo ENOTFOUND). Snippets say the compiler is Alibaba's in-house build based on open-source Clang/LLVM, not a stock release, and that the import std hello-world is fast because the standard library module was precompiled, so that 0.03 s figure excludes the cost of building the std module. [retier] Enricher: no baseline is stated (headers with or without PCH, full or incremental build); the 0.03 s import std figure excludes building the std module itself. Other projects report mixed results: Infinity halved its build time, an LLVM Discourse thread saw slower builds, and {fmt} saw no gain.

Needs a compiler with working C++20 module support and a build system that scans module dependencies; the technique is a language feature, so there is nothing to copy except the migration approach described in the post.

## Maintenance

Reference-only first-party case study from a closed commercial code base with no public code; the technique itself is standard C++20, and Alibaba's open-source async_simple carries an experimental named-module wrapper (Clang 16+, CMake 3.26+ or xmake) that shows a related, copyable style.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): confirm; tier before verification C, tier now C.
- **Tier reason:** Vendor (Alibaba Cloud) blog reporting a 42% compile-time cut on its own Hologres code base; the page and its Chinese mirror were unreachable (getaddrinfo ENOTFOUND), so the claim is confirmed from WebSearch snippets only. First-party, no public code, compiler, flags or hardware, so C at best.
- **Verifier notes:** Two fetch failures (alibabacloud.com, developer.aliyun.com); WebSearch snippets confirm 42% and the 1.5-year mainline use. Keep at C with snippet-only caveat; refresh numbers if the page becomes reachable.
- **Fields the verifier corrected:** `caveats`, `compiler_and_flags`
- **Shortcomings recorded by:** verifier batch-10 (wave 2 book seed pass, 2026-10-24); enrichment (wave 2 book seed pass, 2026-10-24)
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/llvm/llvm-project/main/clang/docs/StandardCPlusPlusModules.md>
  - <https://github.com/llvm/llvm-project/tree/main/clang/docs>
  - <https://raw.githubusercontent.com/Kitware/CMake/master/Help/manual/cmake-cxxmodules.7.rst>
  - <https://raw.githubusercontent.com/alibaba/async_simple/HEAD/README.md>
- **Raw records:** [data/wave2/verified.json](../../../data/wave2/verified.json) (id `paper:c-20-modules-instead-of-header-inclusion-alibaba-hologres-case`) · [data/wave2/enrich/raw/paper_c_20_modules_instead_of_header_inclusion_alibaba_hologres_case.json](../../../data/wave2/enrich/raw/paper_c_20_modules_instead_of_header_inclusion_alibaba_hologres_case.json) (enrichment confidence 0.45)

</details>
