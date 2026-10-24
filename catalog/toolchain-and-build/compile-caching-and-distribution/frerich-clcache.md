# clcache

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Toolchain and build](../README.md) › [Compile caching and distribution](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Python` · `BSD-3-Clause` · 🔴 abandoned

> Python ccache-style object cache for MSVC cl.exe that skips recompiling unchanged translation units on repeat builds.

| | |
|---|---|
| **Beats** | uncached MSVC compile (cl.exe without a compiler cache) |
| **Claimed result** | Merge request text: the average uncached MSBuild RelWithDebInfo job is either barely passing or barely failing the 2 hour timeout; with the clcache fork the 2nd build (partial cache) succeeded in 100 minutes, the 3rd build (full cache) in 55 minutes, and subsequent jobs in as little as 49 minutes. Roughly 2.2x (120 / 55, derived from page data, the 120 minute figure being the job timeout, not a measured uncached time). |
| **Workload** | OpenMW GitLab CI job (MSBuild, MSVC 2022, 64-bit RelWithDebInfo) run uncached versus with a third-party fork of clcache and a CI-restored cache across successive pipeline runs. |
| **Metric** | build-time |
| **Compiler and flags** | MSVC 2022, 64-bit, RelWithDebInfo; clcache with CLCACHE_COMPRESS, cache limit 1.5 GB (clcache -M 1610612736) |
| **Adoption** | 324 stars; archived by owner on 2020-02-04 |
| **Last commit** | 2019-02-19 |
| **Links** | [repository](https://github.com/frerich/clcache) · [benchmark](https://gitlab.com/OpenMW/openmw/-/merge_requests/5021) |

## Verdict

The only recent numbers come from OpenMW's unmerged draft MR !5021: a GitLab Windows MSBuild RelWithDebInfo job (MSVC 2022, 64-bit, runner hardware not stated) that usually sits at its 2 hour timeout uncached finished in 100, 55 and as little as 49 minutes on successive runs with a restored cache, using a patched fork rather than upstream, and with precompiled headers turned off (OpenMW's CMake default is on), /Zi rewritten to /Z7 and MSBuild TrackFileAccess disabled only in the cached configuration, so the \~2.2x (derived from page data, against the timeout) compares different builds across separate pipelines. Upstream issue #239 has a same-machine user measurement of upstream clcache: 4:49 without, 6:22 cold and 2:06 warm on a 4-core 2 GHz SSD CI machine (about 2.3x warm, derived from page data), and 2:21 against 1:10 warm on a 4-core 3.3 GHz machine; project and compiler version not stated.

## Use it when

- Windows CI jobs with MSVC where a restored cache directory covers most translation units (OpenMW's draft MR saw 100 then 55 minutes on the 2nd and 3rd cached runs of a job that otherwise sits near its 2 hour timeout).
- Developer machines that rebuild the same sources after cleans or branch switches with the same compiler install and build directory (or CLCACHE_BASEDIR set).
- Ninja, NMake or CMake compiler-launcher builds, or MSBuild builds that can run with TrackFileAccess=false (required for MSBuild cache hits per the wiki).
- Codebases that can compile with /Z7 instead of /Zi and without MSVC precompiled headers, since those invocations bypass the cache.

## Skip it when

- Cold or mostly-miss builds: upstream issue reports show the empty-cache build slower than no cache (4:49 to 6:22 on a 4-core CI machine in #239; 7 to 23 minutes in #251), so one-off builds lose.
- Projects that depend on /Zi PDBs or PCH (/Yc, /Yu): those compiles are passed through uncached, and switching to /Z7 and turning PCH off to get hits can slow the uncached build and enlarge objects and the cache.
- Current toolchains with upstream code: the archived repository predates Python 3.10 and MSVC 2019 flags such as /external:I, and users run forks pinned to a commit (OpenMW used Aussiemon/clcache@21c50c2).
- Very large or highly parallel builds: CacheLockException timeouts on section and stats locks and slow in-build cache cleanup are open, unfixed issues (#251, #347; one reporter's cache passed 100 GB and a million files).
- Non-Windows hosts or GCC/Clang command lines: it uses Win32 named mutexes and only parses cl.exe/clang-cl options; sccache or ccache cover those.

## How it is fast

Content-addressed result caching, modeled on ccache. In the default direct mode an MD5 of the compiler binary's mtime and size, the normalized command line and the source file selects a manifest; on a miss clcache injects /showIncludes to record the header set, and on later runs a hit only requires the MD5 of every recorded header to match, so the preprocessor is not run (CLCACHE_NODIRECT falls back to hashing /EP output). A hit copies, or with CLCACHE_HARDLINK hard-links, the stored object instead of compiling. The optional clcachesrv server keeps header hashes in memory and watches the files for changes; the maintainer found warm-cache time dominated by hashing include files (issue #239), which is the cost the server targets.

## Compared with alternatives

Pick clcache over sccache only for an MSVC-only Windows build that needs no remote storage and already runs a pinned fork; sccache is maintained, handles MSVC as well as GCC/Clang/Rust/CUDA and offers shared cloud backends. Against FASTBuild or octobuild it needs no build-system change, but it caches nothing the build does not pass as a plain /c compile.

## Integration

| | |
|---|---|
| **Form** | module (Python package exposing clcache and clcache-server console scripts; optional PyInstaller-built executable) |
| **Dependencies** | Python 3 with atomicwrites, pymemcache and pyuv (setup.py install_requires); the real cl.exe; optional memcached server |
| **Minimum toolchain** | Python 3.5+ upstream (CI tested 3.5 and 3.6; 3.3/3.4 dropped in 4.2.0); MSVC tested in CI with Visual Studio 2013; Python &gt;=3.10 and MSVC &gt;=2019 need third-party fork patches |
| **Platforms** | Windows only (Win32 named mutexes and named pipes via ctypes windll) |
| **Thread safety** | Concurrent invocations on one machine coordinate through Windows named mutexes in the Local\ namespace: hash-sharded locks for object and manifest sections (256 sections per the maintainer in #251) plus a global statistics lock, with a 10 s default timeout (CLCACHE_OBJECT_CACHE_TIMEOUT_MS). These do not coordinate across machines sharing a cache directory. |
| **Drop-in for the baseline** | partial — wraps cl.exe transparently, but only single-source /c compiles without /Zi or PCH are cached, and MSBuild needs TrackFileAccess=false to get hits |

## Gotchas

- The compiler is identified by cl.exe's mtime and size, not its contents, so reinstalling or re-imaging the same MSVC version can invalidate the whole cache.
- Changes to the INCLUDE and LIBPATH environment variables are not detected in direct mode and can return a stale object (wiki Caveats); set CLCACHE_NODIRECT or clear the cache.
- CLCACHE_COMPRESS caches are incompatible with uncompressed ones; changing the setting requires clearing the cache.
- clcachesrv watches header directories and blocks deleting them (use its exclude option), and a PyInstaller --onefile build is documented as considerably slower.

## Known shortcomings

- Numbers come from an unmerged draft OpenMW merge request (!5021) that timed the Aussiemon fork, not upstream, with no hardware stated; upstream issue 251 shows a cold cache slower (7 to 23 min); archived, last commit 2019-02-19.

## Caveats and trade-offs

The README and CHANGELOG of frerich/clcache carry no timing numbers (only 'greatly improves performance of cache hits' for the server). The only reachable numbers are third-party CI anecdotes. The OpenMW merge request (opened 2025-11-29) used Aussiemon's fork pinned to a commit, not upstream, and states no uncached time (only that it is near the 2 hour timeout), no runner hardware, and mixes cache states across different pipeline runs, so the speedup is approximate and not a controlled comparison. The upstream issue https://github.com/frerich/clcache/issues/251 (2016, Windows Server 2012 R2, E5-2650) reports the opposite: a 5 to 8 minute build rose to 23 minutes with a cold cache and was roughly equal to no clcache when fully cached, blamed on cache lock contention and virus scanning. The same MR author found ccache's MSVC precompiled-header hits as slow as misses and called clcache the most stable option, but wished ccache could match its speed. [verifier] As of the check, MR !5021 is still a Draft and not merged into OpenMW master; its first clcache run (empty cache) also hit the timeout, and the fork patches clcache for Python &gt;=3.10 and MSVC &gt;=2019, so upstream clcache itself was not what was timed.

Python wrapper around cl.exe (the repo also has a pyinstaller folder) that stores compiler output in a local directory cache; the optional clcachesrv.py server is documented as greatly improving the performance of cache hits. Upstream is archived: Python 3.10+ and MSVC 2019+ patches live only in forks, which is why users run forks. Precompiled-header caching is not available upstream (the OpenMW fork author says his fork has experimental changes toward it).

## Maintenance

Archived by its owner on 2020-02-04 with the last upstream commit on 2019-02-19; BSD-3-Clause and pure Python, so it can be vendored, but modern Python and MSVC need a third-party fork such as Aussiemon/clcache, whose 2025 commits add Python &gt;=3.10 and /external:I fixes.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): confirm; tier before verification C, tier now C.
- **Tier reason:** OpenMW MR !5021 gives CI job times (uncached near the 2 hour timeout; 100, 55 and as low as 49 minutes with the clcache fork and a restored cache) but no hardware, no measured uncached time, no controlled runs and no public harness beyond the CI config; upstream README has no numbers. Third-party CI anecdote without methodology, so C.
- **Verifier notes:** Numbers, fork, cache settings and issue #251 details all match the pages. MR is a Draft, unmerged; caveat addendum says so. Archived 2020-02-04, last commit 2019-02-19 confirmed.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-10 (wave 2 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://gitlab.com/OpenMW/openmw/-/merge_requests/5021>
  - <https://github.com/frerich/clcache>
  - <https://github.com/frerich/clcache/commits/master>
  - <https://github.com/frerich/clcache/issues/251>
- **Sources the enricher read:**
  - <https://github.com/frerich/clcache>
  - <https://raw.githubusercontent.com/frerich/clcache/master/README.asciidoc>
  - <https://raw.githubusercontent.com/frerich/clcache/master/CHANGELOG.md>
  - <https://raw.githubusercontent.com/frerich/clcache/master/setup.py>
  - <https://raw.githubusercontent.com/frerich/clcache/master/appveyor.yml>
  - <https://raw.githubusercontent.com/frerich/clcache/master/clcache/__main__.py>
  - <https://github.com/frerich/clcache/wiki/Caveats>
  - <https://github.com/frerich/clcache/issues?q=is%3Aissue+slow>
  - <https://github.com/frerich/clcache/issues/251>
  - <https://github.com/frerich/clcache/issues/347>
  - <https://github.com/frerich/clcache/issues/239>
  - <https://github.com/Aussiemon/clcache/commits/master>
  - <https://gitlab.com/OpenMW/openmw/-/merge_requests/5021>
  - <https://gitlab.com/OpenMW/openmw/-/merge_requests/5021/diffs>
  - <https://gitlab.com/OpenMW/openmw/-/raw/master/CMakeLists.txt>
  - <https://gitlab.com/OpenMW/openmw/-/raw/master/CI/before_script.msvc.sh>
  - <https://gitlab.com/OpenMW/openmw/-/raw/master/.gitlab-ci.yml>
- **Raw records:** [data/wave2/verified.json](../../../data/wave2/verified.json) (id `https://github.com/frerich/clcache`) · [data/wave2/enrich/raw/github_com_frerich_clcache.json](../../../data/wave2/enrich/raw/github_com_frerich_clcache.json) (enrichment confidence 0.75)

</details>
