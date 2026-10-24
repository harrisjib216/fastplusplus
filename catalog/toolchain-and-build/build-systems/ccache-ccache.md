# ccache

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Toolchain and build](../README.md) › [Build systems](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `GPL-3.0-or-later` · 🟢 active

> Compiler cache that skips re-running GCC/Clang/MSVC on unchanged source, reusing prior object output.

| | |
|---|---|
| **Beats** | Uncached compilation (same compiler command run without ccache); the page does not involve Make/Ninja and does not name the compiler |
| **Claimed result** | ccache.c: 145.39x (direct mode), 137.81x (depend mode), 28.33x (preprocessor mode) vs no cache. c++_includes.cc: 29.10x (direct), 29.32x (depend), 5.09x (preprocessor) vs no cache. |
| **Workload** | Median of 100 runs compiling ccache's own ccache.c (-g -O2 -MD) and a preprocessor-heavy c++_includes.cc (-MD), comparing no-cache vs ccache's direct/preprocessor/depend cache-hit modes. |
| **Metric** | compile-time |
| **Hardware** | Intel Core i5-4690K, standard SSD, Linux desktop |
| **Compiler and flags** | Compiler not named on page; -g -O2 -MD plus needed -I flags (ccache.c); -MD only (c++_includes.cc); ccache 3.7.1 |
| **Adoption** | 3.0k stars; bundled/used by default in many Linux distro and CI C/C++ build pipelines |
| **Last commit** | 2026-09-19 |
| **Links** | [repository](https://github.com/ccache/ccache) · [benchmark](https://ccache.dev/performance.html) |

## Verdict

First-party ccache.dev page reports median-of-100-runs, single-file cache-hit timings on an Intel Core i5-4690K with SSD (compiler unnamed, ccache 3.7.1): compiling ccache.c (-g -O2 -MD) was 145.39x/137.81x/28.33x faster than an uncached compile in direct/depend/preprocessor mode, and compiling the header-heavy c++_includes.cc (-MD) was 29.10x/29.32x/5.09x faster. These are cache-hit-only, single-file numbers against a plain uncached compile, not end-to-end project build speedups, and the same page shows cache misses running 0.83-0.98x (slightly slower) than uncached.

## Use it when

- Repeated local or CI rebuilds of the same C/C++/CUDA/Objective-C tree where most translation units are unchanged (branch switches, re-running CI on similar commits)
- Toolchains already on GCC, Clang, MSVC, or NVCC on Linux, macOS, or native Windows (mingw-w64), where masquerading as the compiler via symlink or PATH prefix is acceptable
- Shared build farms or multi-developer teams that want cross-machine hits via ccache's Redis or HTTP remote storage backends
- Header-heavy C++ files where preprocessing dominates wall time and hit rate is expected to be high

## Skip it when

- True cold/clean builds or CI that wipes the cache every run — the vendor's own numbers show cache misses at 0.83-0.98x (i.e. slightly slower) than an uncached compile
- Source using __TIME__, __DATE__, or __TIMESTAMP__, which forces the slower preprocessor-mode fallback unless you opt into `sloppiness=time_macros`
- Build flags that defeat the cache key: most -Xpreprocessor uses, -Wp options other than -MD/-MMD/-D/-U, or filesystems with coarse mtime granularity that make ccache disable caching as a race-condition safeguard
- Windows setups needing more than mingw-w64 parity — MSYS2 and other Unix-likes are only partially supported, and MSVC-style compilers don't get full direct-mode support
- Situations demanding fully reproducible, audited benchmark numbers — the vendor's own performance page never names the compiler used

## How it is fast

In direct mode it hashes the raw, unpreprocessed source plus its `#include`d headers (using mtime/ctime plus content hashes) to form a cache key, skipping the preprocessor pass entirely on a hit. Preprocessor mode falls back to running cpp and hashing its output when direct mode is unsafe (e.g. macros like __TIME__). Depend mode derives the key from the compiler's -MD/-MMD dependency list. Hashing uses BLAKE3 and results are stored zstd-compressed, so a hit is a hash computation plus a file copy instead of a full parse/codegen/link.

## Compared with alternatives

No direct siblings — Mill, Buck2, tup, and xmake are build-graph orchestrators, while ccache caches individual compiler invocations underneath any of them. Use ccache alongside those tools when the bottleneck is redundant single-file recompiles rather than build-graph scheduling or dependency tracking.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | Required: BLAKE3, fmt, tl-expected, xxhash, Zstandard (bundled or auto-downloaded if not found locally). Optional: cpp-httplib and hiredis for HTTP/Redis remote storage, doctest for tests. |
| **Minimum toolchain** | CMake 3.15+ to build; C++20 compiler (GCC 11+, Clang 12+, AppleClang 10+) plus a C99 compiler. Note: the benchmarked version (3.7.1) predates this and had much looser requirements. |
| **Platforms** | Linux and macOS (Level A, regularly tested on Ubuntu 22.04/24.04 and macOS 14); native Windows via mingw-w64 (Level A); Windows/MSYS2 and other Unix-likes (Level B, partial) |
| **Thread safety** | Not a library API; as a CLI tool it is designed for concurrent invocations sharing one cache directory (per-entry locking, mtime-based race-condition guard on include files) and has a --threads option for its own internal parallel operations |
| **Drop-in for the baseline** | partial — explain: wraps the exact same compiler command via PATH prefix or symlink masquerade and produces identical output, but requires a PATH/symlink change, and cache misses run 2-17% slower than an uncached compile per the vendor's own figures |

## Gotchas

- __TIME__/__DATE__/__TIMESTAMP__ in source disables direct mode and forces the slower preprocessor-mode path
- If an included header's mtime is newer than the time ccache started, it disables caching entirely for that compile as a race-condition safeguard (tune with sloppiness=include_file_ctime,include_file_mtime)
- Default cache size cap is 5 GB with no file-count limit; old entries are evicted silently once the cap is hit
- Direct mode has compiler-option restrictions (most -Xpreprocessor uses and non-dependency -Wp options force preprocessor mode)

## Caveats and trade-offs

Measures single-file cache hits against a plain uncached compile, not an end-to-end Make/Ninja build, so real speedup depends on hit rate. Cache misses are slower than no cache: first-time runs were 0.96-0.98x (ccache.c) and 0.83-0.97x (c++_includes.cc), and the page cites 5-20% miss overhead (1-3% in depend mode). The page does not name the compiler or give a date. It was measured with the old ccache 3.7.1 on a dated i5-4690K. ccache is itself a named baseline of the compile-caching-and-distribution category.

Only accelerates cache-hit rebuilds; provides no benefit on true cold/clean builds; requires stable compiler/flags/includes for hits; direct mode is disabled by some preprocessor macros (e.g. __TIME__).

## Maintenance

Actively maintained (last commit 2026-09-19; current release targets C++20/CMake 3.15+), GPL-3.0-or-later, and easy to obtain via package managers or source build — it's the de facto default compiler cache bundled in many Linux distros and CI images.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): downgrade; tier before verification A, tier now C.
- **Tier reason:** First-party page lists the CPU (Core i5-4690K, SSD), flags (-g -O2 -MD / -MD), ccache 3.7.1 and median-of-100 method, and the repo has a timing script (misc/performance). But the page never names the compiler or its version, and it does not link the script, so this is not tier A. First-party numbers with partial methodology are tier C.
- **Verifier notes:** All six speedup factors match the page exactly. The downgrade is only because the compiler is unnamed; the rest of the methodology is solid. The GPL-3.0-or-later license is confirmed from LICENSE.adoc (gh shows NOASSERTION), and stars are 2,961.
- **Fields the verifier corrected:** `baseline`, `baseline_in_list`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://ccache.dev/performance.html>
  - <https://github.com/ccache/ccache>
  - <https://github.com/ccache/ccache/blob/master/LICENSE.adoc>
  - <https://github.com/ccache/ccache/tree/master/misc>
  - <https://github.com/ccache/ccache/blob/master/misc/performance>
- **Sources the enricher read:**
  - <https://github.com/ccache/ccache>
  - <https://ccache.dev/performance.html>
  - <https://ccache.dev/platform-compiler-language-support.html>
  - <https://github.com/ccache/ccache/blob/master/doc/install.md>
  - <https://github.com/ccache/ccache/blob/master/CMakeLists.txt>
  - <https://github.com/ccache/ccache/blob/master/misc/performance>
  - <https://github.com/ccache/ccache/blob/master/doc/manual.adoc>
  - <https://github.com/ccache/ccache/blob/master/LICENSE.adoc>
- **Raw records:** [data/wave2/verified.json](../../../data/wave2/verified.json) (id `https://github.com/ccache/ccache`) · [data/wave2/enrich/raw/github_com_ccache_ccache.json](../../../data/wave2/enrich/raw/github_com_ccache_ccache.json) (enrichment confidence 0.6)

</details>
