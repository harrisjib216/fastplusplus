# ImGui SIMD ImStrlen/ImMemchr (PR #8421, Kraionix/ImGuiMemchrBench)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Assembly-level string and memory routines](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `no license` · 🟡 stale

> Unmerged Dear ImGui PR: SSE/AVX2 strlen and memchr with software prefetch, 1.4-1.55x over MSVC CRT on large buffers.

| | |
|---|---|
| **Beats** | C runtime strlen and memchr (labelled CSTD; ImMemchrCSTD is a plain memchr call). The bench repo is a Visual Studio 2022 project (v143 toolset, Release\|x64, static CRT /MT), so CSTD is the MSVC CRT implementation, not glibc |
| **Claimed result** | 1 GB buffer: ImStrlen AVX2_PREFETCH 56.6 ms (17.6 Gi/s) vs CSTD 79.9 ms (12.5 Gi/s), 1.41x; ImMemchr AVX2_PREFETCH 58.2 ms (17.17 Gi/s) vs CSTD 89.9 ms (10.93 Gi/s), 1.54x, which is the '55%' in the PR title; plain AVX2 ImMemchr without prefetch 79.8 ms, only 1.13x; 16 MB ImMemchr 0.799 vs 1.17 ms (1.46x); 1 MB ImStrlen 0.010 vs 0.059 ms (about 5.9x, 93.3 vs 16.4 Gi/s) (ratios derived from page data). A later comment says AVX2 ImMemchr gave 'about 60%' more performance on a 16 MB buffer and ImGui::TextUnformatted dropped from 1.6 ms to 0.98 ms per frame |
| **Workload** | Google Benchmark on std::string buffers of random ASCII from 1 MB to 1 GB: strlen scans for the terminator; memchr scans for 131-character lines ending in a newline; SSE, SSE+prefetch, AVX2 and AVX2+prefetch variants. |
| **Metric** | throughput |
| **Hardware** | Intel Core i9-10980XE (18 cores / 36 threads, all cores 4600 MHz, uncore 3200 MHz), 128 GB quad-channel at 4000 MHz, power saving disabled, AVX offset 400 MHz |
| **Compiler and flags** | MSVC, Visual Studio 2022 v143 toolset (exact version not stated); ImMemchrBench.vcxproj Release\|x64: /Oi, /GL whole-program optimization, /Ob2, /arch:AVX2, /MT, /std:c++latest (no Optimization element, so the MSBuild Release default /O2 applies); the README says only 'Compiled benchmark in release' |
| **Adoption** | 4 stars on the bench repo; proposed for Dear ImGui (PR open, not merged) |
| **Last commit** | 2025-02-23 |
| **Links** | [repository](https://github.com/Kraionix/ImGuiMemchrBench) · [benchmark](https://github.com/ocornut/imgui/pull/8421) |

## Verdict

Author-run Google Benchmark tables in PR #8421 on an overclocked i9-10980XE, built with MSVC v143 Release /arch:AVX2 /MT (exact version unstated), against the MSVC CRT: memchr finding a newline every 131 bytes, AVX2+prefetch 20.53 vs 14.29 GiB/s at 1 MB (about 1.44x) and 17.17 vs 10.93 GiB/s at 1 GB (about 1.55x; 1.13x without prefetch); strlen over one long string 93.33 vs 16.45 GiB/s at 1 MB (about 5.7x, L2-resident) and 17.6 vs 12.52 GiB/s at 1 GB (about 1.41x), ratios derived from page data. Only the memchr harness is public; the strlen benchmark code is not.

## Use it when

- MSVC x64 builds of Dear ImGui that render very large text blocks (multi-megabyte logs through TextUnformatted, where the author saw frame time drop from about 1.6 ms to 0.98 ms on a 16 MB buffer with a newline every 131 characters).
- Projects already compiling with /arch:AVX2 (or -march=haswell) whose C runtime strlen/memchr is not AVX2-dispatched.
- As a starting point for your own ImStrlen/ImMemchr override, patched into imgui_internal.h in place of the strlen/memchr defines.

## Skip it when

- Typical ImGui UI text: labels are short, and ImMemchr falls back to a byte-by-byte loop below 32 bytes (16 for SSE) and for every 0-31 byte tail, where a libc memchr is likely as fast or faster (not measured by the author).
- Linux/glibc or macOS: the only baseline measured is the MSVC static CRT, and glibc already dispatches AVX2/EVEX memchr and strlen, so the gain there is undocumented.
- Debug builds: the maintainer noted libc is always compiled optimized while ImGui follows the project's flags, so unoptimized intrinsics may lose to the CRT.
- Builds checked with AddressSanitizer: ImStrlen reads whole aligned 32-byte blocks past the terminator (page-safe but outside the allocation).
- Non-x86-64 targets: no NEON or other fallback beyond libc.

## How it is fast

Each function does one unaligned 32-byte (or 16-byte) load at the start, rounds the pointer up to an aligned boundary, then loops on aligned loads with PCMPEQB + PMOVMSKB and TZCNT to locate the first match, and issues a software prefetch 1024 bytes ahead on every iteration. ImStrlen keeps over-reads inside the first 4 KB page explicitly and then relies on aligned loads never crossing a page; ImMemchr stays inside [buf, buf+count) and finishes the last 0-31 bytes with a scalar loop. At 1 GB most of the gain is the prefetch: AVX2 memchr without it is only 1.13x over the CRT.

## Compared with alternatives

Pick it over WojciechMula/toys avx512-string when you need AVX2 rather than AVX-512 and the baseline is MSVC's CRT; pick it over AOCL-LibMem when you only want ImGui's two string hot paths sped up rather than replacing libc wholesale. For general use, a tuned libc or Arm/AMD optimized routines remain the safer choice.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none for the functions (intrin.h or x86intrin.h); the benchmark needs Google Benchmark, fmt and reflect-cpp via vcpkg plus the repo's BenchConfigCpp project |
| **Minimum toolchain** | Measured with Visual Studio 2022 (v143, /std:c++latest, /arch:AVX2); GCC/Clang builds not shown in the PR thread. |
| **Platforms** | x86-64 only (AVX2 path also uses BMI1 TZCNT/ANDN; SSE path uses TZCNT); other targets use libc strlen/memchr. |
| **Thread safety** | Pure functions over caller memory with no shared state; safe to call concurrently (not documented). |
| **Drop-in for the baseline** | partial: same signatures as strlen/memchr and wired in by the PR's fork, but upstream ImGui master defines ImStrlen/ImMemchr to strlen/memchr without an #ifndef guard, so using it today means patching imgui_internal.h. |

## Gotchas

- Benchmark-repo defects found reading ImMemchrBench/immemchr.h (they do not touch the posted AVX2/SSE/CSTD rows): the SSE4.2 variants use _mm_cmpistri, an implicit-length string compare that stops at a 0x00 byte, so they miss matches after an embedded NUL and cannot search for '\0'; their two-chunk loop runs while ptr &lt;= end - 16 but loads ptr + 16 as well, reading 16 bytes past the buffer and returning a pointer beyond end if that garbage holds the byte. The AVX2_UNROLL variants set the unrolled bound to end - 32 \* 128 (4096 bytes) instead of end - 128. The harness never compares any variant's result with memchr, so these went unnoticed.
- Harness asymmetry: the SIMD variants are defined in the benchmark's own translation unit (inlinable under /GL /Ob2), while CSTD calls the static CRT memchr once per 131-byte line, about 8.2 million calls per GiB, so per-call overhead is part of the measured gap (inference from the code; not quantified).
- Portability: the PR gates the SSE path on __SSE__ (always defined on x86-64) and the AVX2 path on __AVX2__, yet both call _tzcnt_u32 and the AVX2 path _andn_u64, which GCC's bmiintrin.h compiles under target("bmi"); a GCC build without -mbmi is therefore expected to fail with a target-specific option mismatch (read from the header, not compiled here). MSVC accepts them.
- ImMemchr computes end - 32 (or 16) and end - 1024 before checking the length, forming pointers before the buffer for short inputs (formally undefined, harmless on x86); ImStrlen's aligned loads read up to 31 bytes past the terminator (page-safe), which AddressSanitizer will report as an out-of-bounds read.

## Known shortcomings

- Numbers come from an open, unmerged PR thread (ocornut/imgui #8421) on an i9-10980XE; the bench repo README has no results table, compiler or flags and no LICENSE (reference only); only memchr has a public harness, the ImStrlen numbers have none.
- Harness flaws in immemchr.h outside the posted rows: the SSE4.2 variants use _mm_cmpistri (stops at NUL), read 16 bytes past the end and can return a pointer beyond end; the AVX2_UNROLL bound is end - 4096 instead of end - 128; no result validation. The SIMD variants are inlinable in the benchmark's translation unit while CSTD calls the CRT memchr once per 131-byte line (per-call overhead in the gap, inference). The PR's SSE/AVX2 paths call _tzcnt_u32/_andn_u64 gated only on __SSE__/__AVX2__, so a GCC build without -mbmi is expected to fail (read from the header, not compiled). Upstream master 1.93.0 WIP has an unguarded '#define ImStrlen strlen', so the hooks need a patch; ImStrlen over-reads trip ASan.

## Caveats and trade-offs

Numbers are from a PR thread (ocornut/imgui #8421, still open, not merged); the bench repo README has no results table, no compiler or flags, and no LICENSE file (so reference only; the PR code would carry ImGui's licence if merged). The bench repo only benchmarks memchr: the ImStrlen code was added to the PR on 2025-03-01, after the repo's last commit, so the strlen numbers have no public harness. The posted table omits the AVX-512, UNROLL and SSE4.2 variants the harness also runs, run_benchmark.ps1 named in the README is not in the repo, and TestData::set_lines wrote past the end of the test buffer until a fix on 2025-02-23 (harness only; newline pattern unchanged). Buffers of 1 MB to 1 GB are far from typical ImGui string lengths and the 1 GB gain comes mostly from software prefetch (AVX2 without prefetch is 1.13x); the 60% figure is for one text-rendering workload. Baseline is the MSVC CRT on Windows, so gains over glibc's AVX2 strlen/memchr may be smaller. Google Benchmark's header reports 36 x 3000 MHz although the PR states a 4600 MHz all-core overclock. The maintainer only added ImStrlen/ImMemchr #define hooks to master (commit 1ec99f4, 2025-03-07) so such variants can be supplied externally, and a commenter argued these belong in the C library.

x86-64 only (SSE and AVX2 variants; the bench repo's run_benchmark.ps1 exists 'to avoid crashes when avx512 is not supported'); the PR adds compile-time SIMD config macros (IMGUI_ENABLE_SSE, SSE4_2, AVX, AVX2). The maintainer rebased the PR and added ImStrlen/ImMemchr hooks (commit 1ec99f4, 2025-03-07) but the SIMD versions were not shown as merged; a reviewer argued libc should be optimized instead.

## Maintenance

Reference only: the bench repo has no licence and five commits (last 2025-02-23), the PR has been open and unmerged since 2025-02-21 with the maintainer adding only strlen/memchr #define hooks (commit 1ec99f4, 2025-03-07); the fork's code sits in an MIT-licensed ImGui fork but the author states no licence for it.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party Google Benchmark tables in the PR thread against the C runtime strlen/memchr (CSTD rows) on a stated i9-10980XE; the memchr harness (ImMemchrBench/ImMemchrGoogleBench.cpp) is public and its Visual Studio project gives MSVC v143 Release flags, but the ImStrlen benchmark code is not public, no compiler version is stated with the results, and the posted table is a subset, so not A.
- **Verifier notes:** PR tables match the record; the 55% title equals the 1 GB ImMemchr AVX2_PREFETCH vs CSTD ratio (derived). The memchr half nearly meets A (public harness, vcxproj flags, stated CPU) but strlen has no public code, so C overall. Shortcomings to record: PR not merged, no licence (reference), MSVC CRT baseline only, memory-bound 1 MB-1 GB buffers, gain at 1 GB mostly from prefetch, strlen harness not public, curated subset of results.
- **Fields the verifier corrected:** `baseline`, `compiler_and_flags`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-61 (wave 13), file only (agent killed by the spend limit before reporting); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/ocornut/imgui/pull/8421>
  - <https://github.com/Kraionix/ImGuiMemchrBench>
  - <https://github.com/Kraionix/ImGuiMemchrBench/commits/master>
  - <https://github.com/Kraionix/ImGuiMemchrBench/tree/master/ImMemchrBench>
  - <https://raw.githubusercontent.com/Kraionix/ImGuiMemchrBench/HEAD/README.md>
  - <https://raw.githubusercontent.com/Kraionix/ImGuiMemchrBench/HEAD/ImMemchrBench/ImMemchrBench.vcxproj>
  - <https://raw.githubusercontent.com/Kraionix/ImGuiMemchrBench/HEAD/ImMemchrBench/ImMemchrGoogleBench.cpp>
  - <https://raw.githubusercontent.com/Kraionix/ImGuiMemchrBench/HEAD/ImMemchrBench/immemchr.h>
  - <https://raw.githubusercontent.com/Kraionix/ImGuiMemchrBench/HEAD/ImMemchrBench/bench_config.json>
  - <https://raw.githubusercontent.com/Kraionix/ImGuiMemchrBench/b641208/ImMemchrBench/ImMemchrBench.vcxproj>
  - <https://raw.githubusercontent.com/Kraionix/ImGuiMemchrBench/b641208/ImMemchrBench/ImMemchrGoogleBench.cpp>
  - <https://raw.githubusercontent.com/Kraionix/ImGuiMemchrBench/b641208/ImMemchrBench/immemchr.h>
- **Sources the enricher read:**
  - <https://github.com/Kraionix/ImGuiMemchrBench>
  - <https://raw.githubusercontent.com/Kraionix/ImGuiMemchrBench/HEAD/README.md>
  - <https://raw.githubusercontent.com/Kraionix/ImGuiMemchrBench/HEAD/ImMemchrBench/ImMemchrGoogleBench.cpp>
  - <https://raw.githubusercontent.com/Kraionix/ImGuiMemchrBench/HEAD/ImMemchrBench/immemchr.h>
  - <https://raw.githubusercontent.com/Kraionix/ImGuiMemchrBench/HEAD/ImMemchrBench/ImMemchrBench.vcxproj>
  - <https://raw.githubusercontent.com/Kraionix/ImGuiMemchrBench/HEAD/ImMemchrBench/bench_config.json>
  - <https://raw.githubusercontent.com/Kraionix/ImGuiMemchrBench/HEAD/LICENSE>
  - <https://github.com/ocornut/imgui/pull/8421>
  - <https://github.com/ocornut/imgui/pull/8421/files>
  - <https://github.com/ocornut/imgui/pull/8421/checks>
  - <https://raw.githubusercontent.com/Kraionix/imgui/master/imgui_internal.h>
  - <https://raw.githubusercontent.com/Kraionix/imgui/master/imgui.cpp>
  - <https://raw.githubusercontent.com/Kraionix/imgui/master/LICENSE.txt>
  - <https://raw.githubusercontent.com/ocornut/imgui/master/imgui_internal.h>
  - <https://raw.githubusercontent.com/gcc-mirror/gcc/master/gcc/config/i386/bmiintrin.h>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/kraionix/imguimemchrbench`) · [data/wave13/enrich/raw/github_com_kraionix_imguimemchrbench.json](../../../data/wave13/enrich/raw/github_com_kraionix_imguimemchrbench.json) (enrichment confidence 0.7)

</details>
