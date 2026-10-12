# matbech/zlib (optimized zlib 1.2.11 fork, MSVC)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [General-purpose lossless compression](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `Zlib` · 🔴 abandoned

> Archived Windows/MSVC zlib fork with SIMD hashing, CRC and match patches; about 1.3-1.9x zlib 1.2.11 level-6 compression.

| | |
|---|---|
| **Beats** | zlib (original 1.2.11) |
| **Claimed result** | Results.md, level 6: silesia/mozilla zlib original 26 MB/s (x86) and 28 MB/s (x64) vs matbech/zlib 47 and 52 MB/s, output 19,064,581 vs 19,089,124 bytes; silesia/webster 29 and 30 MB/s vs 38 and 43 MB/s (about 1.3-1.9x, derived from page data). zlib-ng (x86 only; x64 marked broken) was 30 and 35 MB/s on the same files. |
| **Workload** | deflate compression at level 6 of silesia/mozilla (51,220,480 bytes) and silesia/webster (41,458,703 bytes), x86 and x64 builds |
| **Metric** | throughput |
| **Hardware** | Intel Core i7 8770 (as written in the results file; the linked Intel page is for the i7-8700) |
| **Compiler and flags** | MSVC 19.14.26433.0 (VS 15.7); flags not stated |
| **Adoption** | 7 stars |
| **Last commit** | 2025-02-21 |
| **Links** | [repository](https://github.com/matbech/zlib) · [benchmark](https://github.com/matbech/zlib-perf/blob/HEAD/Results.md) |

## Verdict

First-party Results.md: compression only, level 6, two silesia files, MSVC 19.14 (VS 15.7) on a CPU written as 'i7 8770' (link is the i7-8700), timed with GetTickCount; by the listed times the fork took 1234/922 ms vs zlib 1.2.11's 1813/1718 ms on mozilla (x86/x64) and 1032/907 vs 1359/1313 ms on webster, i.e. 1.32-1.86x (derived from page data), with slightly smaller output. The measured binaries predate the current code (1.2.13 base, chunkset and AVX2 patches added in 2022), and zlib-ng was not measured on x64 because of a deflate bug at the time.

## Use it when

- Windows applications that ship their own zlib1.dll built with MSVC and spend time in deflate level 6 (the measured case: 1.3-1.9x on silesia mozilla and webster).
- Windows on ARM64 builds that want a zlib with CRC32 hashing and NEON adler32 under the stock zlib API.
- As a reference for how the Intel, Cloudflare and fast_zlib deflate patches combine, before choosing a maintained fork.

## Skip it when

- Anything that needs maintenance or security fixes: the repository was archived on 2026-06-17, the last commit is 2025-02-21, and it is based on zlib 1.2.13, so upstream 1.3.x fixes (e.g. the minizip CVE-2023-45853 fix in 1.3.1) are absent.
- Linux, macOS or GCC/Clang builds: there is no Makefile, configure or CMake at the root, only zlib.sln/zlib.vcxproj (toolset v143), crc32.c includes headers with Windows backslash paths, and SIMD paths are gated on MSVC macros (_M_IX86, _M_AMD64, _M_ARM64).
- Old x86 CPUs without SSE4.2/PCLMUL: open issue #2 (2018, no maintainer reply) reports altered decompressed output (text 'becomes upper-cased') on an AMD CPU with only SSE4A; it was never confirmed or fixed.
- Workloads that need byte-identical output with stock zlib: the CRC32 hash and fixed hash_bits produce different compressed streams (19,064,581 vs 19,089,124 bytes on mozilla).
- New projects: zlib-ng and libdeflate (siblings) carry the same ideas, run on all major platforms and are maintained.

## How it is fast

On x86 with SSE4.2 the deflate hash is the hardware CRC32 instruction over 4 bytes with a fixed 15-bit hash table (insert_string_sse), and the window slide uses SSE2; on ARM64 the ACLE CRC32 hash is used unconditionally. longest_match is the fast_zlib/Cloudflare variant (compares several bytes at once, compare256), CRC-32 uses PCLMULQDQ folding, adler32 uses SSE/AVX2 or NEON, and inflate copies matches with zlib-ng's chunkset. CPU features are detected at run time (x86_check_features) on x86.

## Compared with alternatives

Rarely: pick it only for a Windows-only MSVC build that must keep the stock zlib API and a single zlib1.dll and cannot adopt zlib-ng in compat mode. Otherwise zlib-ng (maintained, faster, same API in compat mode), libdeflate (faster whole-buffer API) or Cloudflare's zlib fork (the source of its longest_match patch) are better choices.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | none (Visual Studio project; a 2023 commit links onecore.lib) |
| **Minimum toolchain** | MSVC with platform toolset v143 (Visual Studio 2022), C17 (LanguageStandard_C stdc17); ARM64 target set to ARMv8.2 |
| **Platforms** | Windows x86 (Win32), x64 and ARM64; SIMD paths need SSE2 (slide_hash), SSE4.2 for the CRC32 hash and PCLMUL for CRC-32, chosen at run time; other OSes not supported by the build files |
| **Thread safety** | Same as zlib (README: 'All the code is thread safe' per stream); CPU-feature globals are set on deflateInit or crc32(0, NULL, 0) without synchronisation (benign write of identical values). |
| **Drop-in for the baseline** | partial — same zlib API and zlib1.dll name on Windows, so it replaces a Windows zlib DLL; compressed bytes differ from stock zlib, memLevel no longer sets the hash size when SSE4.2 or ARM64 is used, and some project configurations define ZLIB_CONST, which changes next_in to const. |

## Gotchas

- With SSE4.2 (and always on ARM64) hash_bits is forced to 15 regardless of memLevel, so memLevel tuning has no effect on the hash table.
- crc32() called before any deflateInit or crc32(0, NULL, 0) sees CPU features as unset and takes the table path: correct but without the PCLMUL speedup.
- The benchmark harness (zlib-perf perf.c) has a no-op verification: it compares 'checksum != checksum' and never uses checksum2, so '-v' only catches inflate errors; timing uses GetTickCount (10-16 ms resolution) and includes fread of the input file.
- Results.md is internally inconsistent for one row: matbech/zlib x86 on mozilla lists 1234 ms but 47 MB/s, while the harness formula gives 39 MB/s for 1234 ms (every other row matches), so that speedup is about 1.47x by time, not 1.8x.

## Known shortcomings

- MSVC-only fork of zlib 1.2.11; archived 2026-06-17 (last commit 2025-02-21). zlib DLL build flags unstated and 'i7 8770' is not a real CPU model. README at HEAD says zlib 1.2.13 while the numbers are from the 1.2.11 era.
- Open issue #2 (2018, no reply): altered decompressed output on an AMD CPU without SSE4.2/PCLMUL. The 1.2.13 base lacks the minizip CVE-2023-45853 fix. MSVC-only build (vcxproj v143, backslash includes). Output is not byte-identical to stock zlib; hash_bits forced to 15. The harness perf.c verify is a no-op (checksum != checksum) and GetTickCount timing includes fread. Results.md row mozilla x86 lists 1234 ms but 47 MB/s where the formula gives 39, so 1.47x not 1.8x; by time the range is 1.32-1.86x. Benchmarked binaries predate the 2022 chunkset/AVX2 code.

## Caveats and trade-offs

Repository archived 2026-06-17 (read-only); last commit 2025-02-21. Benchmark measured compression only, level 6, two files, one machine, timed with GetTickCount (coarse resolution); flags of the tested zlib DLL builds unstated; CPU written as 'i7 8770' (linked page is i7-8700). Results date from MSVC VS 15.7 on the zlib 1.2.11 base, while the repo README at HEAD reads zlib 1.2.13, so the numbers predate the current code. Speedup combines Intel, Cloudflare, ARM and Chromium patches already known from other forks. Footnotes say the zlib asm baseline variant is broken. GitHub does not mark it as a fork, but it is derived from madler/zlib.

Compression only (no decompression numbers); drop-in zlib API; targets Windows/MSVC and ARM64 with SIMD CRC and hash; the same table shows zlib-ng broken on x64 in that test.

## Maintenance

Abandoned: archived 2026-06-17, last commit 2025-02-21, 7 stars, 3 open issues including an unanswered correctness report; Zlib-licensed and copyable, but treat it as a patch reference rather than a dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** Results.md compares against original zlib with compiler (MSVC 19.14.26433.0) and a CPU, and harness code is public (zlib-perf/zlibperf/perf.c, run.cmd, vcxproj with /O2 MaxSpeed for the harness), but the flags used to build the tested zlib DLLs are not given and the CPU model 'i7 8770' does not exist (link points to i7-8700), so not A; first-party, so C.
- **Verifier notes:** Numbers match Results.md exactly. Benchmark harness is public in matbech/zlib-perf (perf.c, run.cmd); tier stays C because zlib build flags and an exact CPU model are missing. 7 stars.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** first-party Results.md with public harness zlib-perf/zlibperf/perf.c; first-party Results.md
- **Pages the verifier opened:**
  - <https://github.com/matbech/zlib>
  - <https://github.com/matbech/zlib/commits>
  - <https://raw.githubusercontent.com/matbech/zlib/HEAD/README>
  - <https://github.com/matbech/zlib-perf>
  - <https://github.com/matbech/zlib-perf/tree/master/zlibperf>
  - <https://raw.githubusercontent.com/matbech/zlib-perf/HEAD/Results.md>
  - <https://raw.githubusercontent.com/matbech/zlib-perf/HEAD/zlibperf/zlibperf.vcxproj>
  - <https://raw.githubusercontent.com/matbech/zlib-perf/HEAD/zlibperf/perf.c>
  - <https://raw.githubusercontent.com/matbech/zlib-perf/HEAD/zlibperf/run.cmd>
- **Sources the enricher read:**
  - <https://github.com/matbech/zlib>
  - <https://github.com/matbech/zlib/commits/master>
  - <https://github.com/matbech/zlib/issues>
  - <https://github.com/matbech/zlib/issues/2>
  - <https://raw.githubusercontent.com/matbech/zlib/HEAD/README>
  - <https://raw.githubusercontent.com/matbech/zlib/HEAD/README.md>
  - <https://raw.githubusercontent.com/matbech/zlib/HEAD/zlib.h>
  - <https://raw.githubusercontent.com/matbech/zlib/HEAD/deflate.c>
  - <https://raw.githubusercontent.com/matbech/zlib/HEAD/crc32.c>
  - <https://raw.githubusercontent.com/matbech/zlib/HEAD/inflate.c>
  - <https://raw.githubusercontent.com/matbech/zlib/HEAD/contrib/minizip/zip.c>
  - <https://raw.githubusercontent.com/matbech/zlib/HEAD/zlib.vcxproj>
  - <https://raw.githubusercontent.com/matbech/zlib-perf/HEAD/README.md>
  - <https://raw.githubusercontent.com/matbech/zlib-perf/HEAD/Results.md>
  - <https://raw.githubusercontent.com/matbech/zlib-perf/HEAD/zlibperf/perf.c>
  - <https://raw.githubusercontent.com/matbech/zlib-perf/HEAD/zlibperf/run.cmd>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/matbech/zlib`) · [data/wave9/enrich/raw/github_com_matbech_zlib.json](../../../data/wave9/enrich/raw/github_com_matbech_zlib.json) (enrichment confidence 0.75)

</details>
