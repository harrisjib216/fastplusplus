# CMake unity (jumbo) builds

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Toolchain and build](../README.md) › [Compile caching and distribution](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> CMake 3.16+ UNITY_BUILD: compiles batches of sources as one translation unit, cutting clean-build time against per-file builds.

| | |
|---|---|
| **Beats** | ordinary one-translation-unit-per-source CMake build (same target without UNITY_BUILD) |
| **Claimed result** | Independent (j-jorge/unity-build, i5-3210M, Debug default, batch size 65536, make -j nproc): incremental rebuild with about 10% of files modified, tweenerspp 18.12 s to 7.17 s (about 2.53x) and iscool-core 154.03 s to 70.37 s (about 2.19x), but weak-function 3.51 s to 3.97 s (slower); in the Release plot (read by eye) unity is slower for iscool::core below about 20 modified files. First-party (snippet only): CMake MR 3611 reports SpeedCrunch medians with batch size 5 of MinGW 25.215 s to 17.495 s (30.61% time saved, about 1.44x) and MSVC 23.526 s to 12.097 s (48.58%; the stated 48.52% does not match); the Qt blog's 29.33/53.50/23.61% figures were not found again on the second pass. |
| **Workload** | Release build of the SpeedCrunch calculator target with CMake -DCMAKE_UNITY_BUILD=ON against the same build without unity, with three Windows compilers. The batch size used in the blog post is not confirmed from the summaries (CMake's default UNITY_BUILD_BATCH_SIZE is 8; the merge request's own run used 5). |
| **Metric** | build-time |
| **Hardware** | Independent run: Intel Core i5-3210M. First-party SpeedCrunch runs: Windows 10 with an AMD Ryzen CPU (model not shown). |
| **Compiler and flags** | Independent run: compiler and version not stated, CMake Debug by default, CMAKE_UNITY_BUILD with batch size 65536, make -j\$(nproc), ccache on when installed. First-party: MinGW GCC 8.1.0, Visual C++ 2017, Clang-cl 8.0.0, Release, CMake -DCMAKE_UNITY_BUILD=ON. |
| **Adoption** | 8.1k stars (GitHub mirror of the upstream CMake repository); UNITY_BUILD ships since CMake 3.16 |
| **Last commit** | 2026-10-24 |
| **Links** | [repository](https://github.com/kitware/cmake) · [benchmark](https://github.com/j-jorge/unity-build) |

## Verdict

The record's numbers are the implementer's 2019 measurements on one Windows 10 Ryzen machine (pages unreachable; search summaries only, and this pass's searches did not re-find the blog's SpeedCrunch figures): SpeedCrunch Release with -DCMAKE_UNITY_BUILD=ON was 29.33% (MinGW GCC 8.1.0), 53.50% (Visual C++ 2017) and 23.61% (Clang-cl 8.0.0) faster per the blog, while MR 3611 gives medians of three runs at batch size 5 of 25.215 s to 17.495 s with MinGW 8.1 (30.61% time saved, about 1.44x) and 23.526 s to 12.097 s with Visual C++ 2017 (stated 48.52%, the times give 48.58%, about 1.94x; derived from page data), so the percentages are time saved, not speed ratios. Independently, j-jorge/unity-build's public scripts (CMake make -j nproc, batch size 65536, Debug by default, ccache if installed, one run per configuration, compiler version not stated) report on an Intel Core i5-3210M incremental rebuilds of tweenerspp at 18.12 s to 7.17 s, iscool-core at 154.03 s to 70.37 s, and weak-function at 3.51 s to 3.97 s (slower).

## Use it when

- Clean or CI builds of header-heavy C++ on a modest core count, where per-file front-end work dominates; the implementer's 2019 SpeedCrunch numbers show the largest saving with MSVC (53.50% in the blog, 48.52% in MR 3611) and less with MinGW GCC and clang-cl.
- Rebuilds that touch many files at once (branch switches, widely used header edits): the independent j-jorge/unity-build scripts measured incremental rebuilds after modifying about 10% of files at 2.53x (tweenerspp) and 2.19x (iscool-core) faster (derived from page data).
- Code bases already free of file-scope name collisions (static functions, anonymous-namespace names, macros without #undef, file-scope using-directives), or willing to use UNITY_BUILD_UNIQUE_ID and SKIP_UNITY_BUILD_INCLUSION to fix the few that clash.
- As an opt-in developer or CI switch per machine, which is how CMake's documentation says it should be enabled.

## Skip it when

- Edit-compile loops that touch one or two files: any change recompiles its whole batch; in j-jorge/unity-build's Release no-ccache plot, iscool::core rebuilt slower with unity than without for most runs with fewer than about 20 modified files (read visually), and weak-function took 3.97 s with unity against 3.51 s without.
- Many-core machines or distributed builds (distcc, icecream): fewer, larger translation units leave cores idle; an LLVM RFC reported about 30% wall-clock gain at about 16 cores that decays at higher core counts (search snippet only).
- Code that relies on per-file isolation: file-local names, unbalanced #defines and file-scope using-directives from different files collide in one TU and cause ODR or ambiguity errors that the normal build never shows.
- Memory-limited build machines with large batch sizes: CMake's docs warn that too-large batches can exhaust compiler memory or fail, and strongly discourage batch size 0 (all sources in one file).
- Workflows built on compile_commands.json (clang-tidy, clangd): CMake's docs say CMAKE_UNITY_BUILD does not work well with CMAKE_EXPORT_COMPILE_COMMANDS; C++20 module sources are excluded from batching automatically.

## How it is fast

Unity (jumbo, single-compilation-unit) builds amortise front-end work: headers shared by the batched sources are preprocessed and parsed once per batch instead of once per file, common template instantiations are emitted once, and fewer object files reach the linker. The saving grows with batch size and header overlap, but bigger batches mean fewer, longer compile jobs, so build parallelism and incremental granularity drop.

## Compared with alternatives

Choose CMake unity builds when you already use CMake and want a free single-machine cut in clean-build time without a cache server or build farm; FASTBuild has its own Unity/Blob mode, and sccache/ccache/distcc/icecream target repeated or distributed builds and can be combined with it, with each batch becoming the unit that is cached or shipped. Against the sibling precompiled-headers entry, unity builds also share template instantiation and link work but give up per-file isolation and fine-grained incremental rebuilds; the two can be enabled together.

## Integration

| | |
|---|---|
| **Form** | build-system feature (CMake target property and cache variable; nothing to link) |
| **Dependencies** | CMake 3.16+ |
| **Minimum toolchain** | CMake 3.16 (UNITY_BUILD_MODE and UNITY_GROUP 3.18, UNITY_BUILD_UNIQUE_ID 3.20, OBJC/OBJCXX 3.29, CUDA 3.31, UNITY_BUILD_RELOCATABLE 4.0, file-set exclusions 4.4) |
| **Platforms** | Any CMake generator and compiler; the FASTBuild generator does its own unity batching instead of CMake's generated unity files |
| **Thread safety** | not applicable (build-time feature) |
| **Drop-in for the baseline** | partial — enabling it needs no source edits, but code with file-local name clashes, unbalanced macros or file-scope using-directives fails to build until fixed or excluded with SKIP_UNITY_BUILD_INCLUSION |

## Gotchas

- BATCH mode slices the target's source list in order into contiguous chunks of UNITY_BUILD_BATCH_SIZE (cmLocalGenerator::AddUnityFilesModeAuto), so adding or removing one source early in the list reshuffles every later batch and recompiles them; GROUP mode with UNITY_GROUP gives stable buckets.
- Sources with their own COMPILE_OPTIONS, COMPILE_DEFINITIONS, COMPILE_FLAGS or INCLUDE_DIRECTORIES source properties (and HEADER_FILE_ONLY files) are silently compiled on their own, so a target can end up with little batching.
- Anonymous namespaces no longer isolate names across merged files; set UNITY_BUILD_UNIQUE_ID (3.20) and wrap file-local code in namespace { namespace MY_UNITY_ID { ... } }, or inject cleanup such as NOMINMAX handling through UNITY_BUILD_CODE_BEFORE_INCLUDE and UNITY_BUILD_CODE_AFTER_INCLUDE.
- Generated unity files #include sources by absolute path, so their content differs with the checkout location; UNITY_BUILD_RELOCATABLE (4.0) switches to relative paths where possible but does not guarantee identical files across environments.

## Known shortcomings

- Implementer's own numbers (SpeedCrunch 29.33/53.50/23.61%), seen only in search snippets; CMake MR 3611 gives conflicting figures (about 30.61/48.52%, batch size 5). One machine, no CPU model, no benchmark code; percentages need a re-check where qt.io and gitlab.kitware.com are reachable.
- Enricher retier C to B on j-jorge/unity-build (independent, i5-3210M): mixed results (2.53x and 2.19x on two projects, slower on weak-function and on small Release incrementals); one run per configuration, ccache possibly on, compiler unstated. BATCH mode reshuffles all later batches when a source is added or removed.

## Caveats and trade-offs

Snippet only: www.qt.io and gitlab.kitware.com could not be opened (host unresolvable from this container), so the percentages come from WebSearch result summaries of the 2019-08-01 Qt blog post and of CMake MR 3611 and need re-checking on the page. Measured by the feature's implementer on a single machine and one project in 2019, on the pre-release feature. The blog and the merge request report different figures for the same project (29.33%/53.50% vs about 30.61%/48.52%), apparently because of different batch sizes. The percentage definition (time saved or speed ratio) is not clear from the summary. The book's quoted 20-50% for Qt Creator could not be matched to that post: the summaries tie the unity figures to SpeedCrunch and the Qt Creator figures to precompiled headers. The Kitware/CMake repo carries the implementation and docs but no benchmark code or timings (Help/prop_tgt/UNITY_BUILD.rst has no numbers). [retier] Enricher: BATCH mode cuts the source list into fixed-size chunks in order, so adding or removing one source reshuffles every later batch and defeats incremental reuse. One run per configuration in the independent scripts; ccache may mask compile time. www.qt.io and gitlab.kitware.com were unreachable, so the first-party numbers rest on search snippets.

Implemented in Source/cmLocalGenerator.cxx (AddUnityBuild) with UNITY_BUILD, UNITY_BUILD_BATCH_SIZE, UNITY_BUILD_MODE and SKIP_UNITY_BUILD_INCLUSION. CMake's own docs say projects should not set UNITY_BUILD or CMAKE_UNITY_BUILD directly; per the book lead, merged sources can clash on file-scope names and macros, and larger translation units cut parallelism, raise memory use and make incremental rebuilds recompile whole batches. Qt Creator's own sources were not unity-compatible per the post, which is why SpeedCrunch was measured.

## Maintenance

Actively developed (GitHub mirror commit on 2026-10-24, v4.4.4 released 2026-10-02, v4.5.0-rc1 on 2026-10-15) and BSD-3-Clause; nothing to vendor, since it ships in every CMake from 3.16.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): confirm; tier before verification C, tier now B.
- **Tier reason:** Numbers exist only in the implementer's 2019 Qt blog post (single Windows 10 Ryzen machine, SpeedCrunch Release, no CPU model, flags or benchmark code), which is unreachable from this container; search summaries give the exact SpeedCrunch figures, so snippet-only first-party evidence stays at C.
- **Retiered** C to B: C to B: independent public scripts (j-jorge/unity-build) measure CMAKE_UNITY_BUILD on three projects with the CPU stated (i5-3210M); not A because each configuration ran once, ccache is used when installed and the compiler version is not stated. Results are mixed.
- **Verifier notes:** Corrected claimed_speedup to the exact two-decimal figures the search summaries attribute to the post and added the conflicting MR 3611 figures; removed the unverified 'default batch size 8' claim from workload. Metadata same as the PCH record (BSD-3-Clause, 8.1k stars, mirror, last commit 2026-10-24).
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `caveats`, `benchmark_url`, `hardware`, `compiler_and_flags`
- **Shortcomings recorded by:** verifier batch-11 (wave 2 book seed pass, 2026-10-24); enrichment (wave 2 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://github.com/Kitware/CMake>
  - <https://github.com/Kitware/CMake/commits/master>
  - <https://raw.githubusercontent.com/Kitware/CMake/HEAD/Help/prop_tgt/UNITY_BUILD.rst>
  - <https://raw.githubusercontent.com/Kitware/CMake/HEAD/LICENSE.rst>
  - <https://raw.githubusercontent.com/Kitware/CMake/HEAD/Help/prop_tgt/UNITY_BUILD_BATCH_SIZE.rst>
- **Sources the enricher read:**
  - <https://github.com/Kitware/CMake>
  - <https://github.com/Kitware/CMake/tags>
  - <https://github.com/Kitware/CMake/commits/master>
  - <https://raw.githubusercontent.com/Kitware/CMake/HEAD/Help/prop_tgt/UNITY_BUILD.rst>
  - <https://raw.githubusercontent.com/Kitware/CMake/HEAD/Help/prop_tgt/UNITY_BUILD_BATCH_SIZE.rst>
  - <https://raw.githubusercontent.com/Kitware/CMake/HEAD/Help/prop_tgt/UNITY_BUILD_MODE.rst>
  - <https://raw.githubusercontent.com/Kitware/CMake/HEAD/Help/prop_tgt/UNITY_BUILD_UNIQUE_ID.rst>
  - <https://raw.githubusercontent.com/Kitware/CMake/HEAD/Help/prop_tgt/UNITY_BUILD_CODE_BEFORE_INCLUDE.rst>
  - <https://raw.githubusercontent.com/Kitware/CMake/HEAD/Help/prop_tgt/UNITY_BUILD_CODE_AFTER_INCLUDE.rst>
  - <https://raw.githubusercontent.com/Kitware/CMake/HEAD/Help/prop_tgt/UNITY_BUILD_RELOCATABLE.rst>
  - <https://raw.githubusercontent.com/Kitware/CMake/HEAD/Help/prop_sf/SKIP_UNITY_BUILD_INCLUSION.rst>
  - <https://raw.githubusercontent.com/Kitware/CMake/HEAD/Help/prop_sf/UNITY_GROUP.rst>
  - <https://raw.githubusercontent.com/Kitware/CMake/HEAD/Help/variable/CMAKE_UNITY_BUILD.rst>
  - <https://raw.githubusercontent.com/Kitware/CMake/HEAD/Help/variable/CMAKE_UNITY_BUILD_BATCH_SIZE.rst>
  - <https://raw.githubusercontent.com/Kitware/CMake/HEAD/Help/variable/CMAKE_UNITY_BUILD_UNIQUE_ID.rst>
  - <https://raw.githubusercontent.com/Kitware/CMake/HEAD/Help/release/3.16.rst>
  - <https://raw.githubusercontent.com/Kitware/CMake/HEAD/Source/cmLocalGenerator.cxx>
  - <https://raw.githubusercontent.com/j-jorge/unity-build/HEAD/README.md>
  - <https://raw.githubusercontent.com/j-jorge/unity-build/HEAD/bin/benchmark.sh>
  - <https://raw.githubusercontent.com/j-jorge/unity-build/HEAD/bin/am-i-special.sh>
  - <https://raw.githubusercontent.com/j-jorge/unity-build/HEAD/lib/benchmark-utils.sh>
  - <https://raw.githubusercontent.com/j-jorge/unity-build/HEAD/results/release/noccache/plot.png>
  - https://www.qt.io/blog/2019/08/01/precompiled-headers-and-unity-jumbo-builds-in-upcoming-cmake (fetch failed: getaddrinfo ENOTFOUND www.qt.io; WebSearch summaries only)
  - https://gitlab.kitware.com/cmake/cmake/merge_requests/3611 (fetch failed: getaddrinfo ENOTFOUND gitlab.kitware.com; WebSearch summaries only)
  - https://discourse.llvm.org/t/rfc-enabling-unity-build/90306 (fetch failed: getaddrinfo ENOTFOUND discourse.llvm.org; WebSearch summary only)
- **Raw records:** [data/wave2/verified.json](../../../data/wave2/verified.json) (id `paper:book-cmake-unity-builds`) · [data/wave2/enrich/raw/paper_book_cmake_unity_builds.json](../../../data/wave2/enrich/raw/paper_book_cmake_unity_builds.json) (enrichment confidence 0.65)

</details>
