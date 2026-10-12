# jtkukunas/zlib (Intel zlib fork)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [General-purpose lossless compression](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `Zlib` · 🔴 abandoned

> Archived Intel fork of zlib with SSE4.2 hashing and new quick/medium deflate strategies; about 1.8x stock zlib at mid levels.

| | |
|---|---|
| **Beats** | zlib (stock deflate) |
| **Claimed result** | jsnell/zlib-bench level 5 (Intel fork vs stock zlib, seconds): executable 1.49 vs 2.66 (1.79x), html 0.85 vs 1.62 (1.91x), jpeg 1.08 vs 0.93 (slower) (derived from page data); level 1 at 36% of baseline time with ratio 0.46 vs 0.37. |
| **Workload** | Compression speed at levels 1, 5/6 and 7-9 on HTML, executables, JPEG and PNG pixel data, as reported by a third-party blog comparing the Intel and Cloudflare zlib forks with stock zlib. |
| **Metric** | throughput |
| **Hardware** | i7-4770 (from search snippet) |
| **Compiler and flags** | not available (blog blocked) |
| **Adoption** | 144 stars, 37 forks; archived 2024-03-01 |
| **Last commit** | 2024-03-01 |
| **Links** | [repository](https://github.com/jtkukunas/zlib) · [benchmark](https://github.com/jsnell/zlib-bench) |

## Verdict

Juho Snellman's independent zlib-bench harness (github.com/jsnell/zlib-bench) pins madler/zlib 5089329, cloudflare a80420c and Intel e176b3c and builds each with ./configure && make; its README example run at level 5 shows Intel at 1.49 s vs 2.66 s baseline on an executable (56.1%), 0.85 vs 1.62 s on HTML (52.8%) and 1.08 vs 0.93 s on JPEG (115.4%), with decompression at 97.6-103.2% of baseline. CPU and compiler are not stated in the repo; the blog's level-1 numbers and the i7-4770 came from search snippets only, and all of it measures the 2014 zlib 1.2.8-based state, not the 1.2.13 HEAD.

## Use it when

- Reproducing or studying the 2014-era Intel deflate work that zlib-ng later merged (deflate_quick, deflate_medium, CRC hashing).
- Legacy x86-64 builds already pinned to zlib-intel (for example older .NET runtimes) that need an audit trail of what they ship.
- Mid-level (4-6) compression on x86 of text or executables where a zlib-1.2.13 API is required and zlib-ng's compat mode is not an option: Snellman's zlib-bench README shows level 5 at 52.8-56.1% of stock zlib time.

## Skip it when

- Any new project: Intel archived it on 2024-03-01 ('This project will no longer be maintained by Intel ... no longer accepts patches'), and zlib-ng carries the same quick and medium strategies with runtime dispatch, ARM support and active maintenance.
- Correctness-critical pipelines: issue #24 'deflate_medium doesn't always produce output that can be inflated' (2019) is still open, as are inflate reports #21 (corrupted output on \~8-byte inputs after commit 62b7616), #33 (zip member inflated 6,906 bytes short, v1.2.11.1_jtkv6.3) and #34 (checksum failure with windowBits 47, reported by the .NET team); none has a maintainer reply, and whether the 2022 rebase fixed them is not documented.
- Incompressible data such as JPEG: zlib-bench shows level 5 at 115.4% of baseline time, i.e. slower than stock zlib.
- Non-x86 targets: Makefile.in and CMakeLists.txt compile crc_folding.c and deflate_quick.c with -mpclmul -msse4 unconditionally, and the x86 code paths are the whole point; use zlib-ng or stock zlib on ARM.
- Security-sensitive deployments: it stops at zlib 1.2.13, so upstream fixes from zlib 1.3 onward are not merged.

## How it is fast

Deflate hashes 4 bytes with one SSE4.2 crc32 instruction (inline asm, chosen at runtime by a CPUID check) instead of zlib's rolling shift-xor hash, slides the hash table with SSE2, and uses 16-bit unaligned compares in longest_match. Levels 4-6 run deflate_medium, a match-extending strategy that avoids zlib's lazy evaluation, and the optional deflate_quick (level 1) compares with SSE4.2 pcmpestri, emits only static-Huffman blocks and caps the window at 8 KiB (windowBits 13). The gzip path folds CRC-32 with PCLMULQDQ while copying input (crc_fold_copy).

## Compared with alternatives

Essentially never for new code: zlib-ng (catalogued, with lzbench numbers) contains these same Intel strategies plus ARM and AVX2/AVX-512 paths and is maintained; Cloudflare's fork is the comparable deprecated alternative and is faster at levels 6-9. Keep this entry for attribution and for auditing systems that still ship zlib-intel.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (configure/make or CMake) |
| **Dependencies** | none |
| **Minimum toolchain** | C89-style zlib 1.2.13 code base; GCC or Clang with -msse4/-mpclmul support (inline asm in deflate_quick needs GCC-style asm outside MSVC) |
| **Platforms** | x86-64 and x86-32 (SSE2 required for the build; SSE4.2 and PCLMULQDQ used when CPUID reports them); other architectures not supported by the build files |
| **Thread safety** | Same as zlib for separate z_stream objects (bundled README: 'All the code is thread safe'), but x86_check_features() sets global feature flags behind an unsynchronised static once flag on every deflateInit, a benign but formal data race when streams are created concurrently. |
| **Drop-in for the baseline** | partial — same zlib 1.2.13 API, ABI and stream format, but x86-only, compressed bytes differ from stock zlib, and the fast level-1 strategy is not compiled in by default |

## Gotchas

- deflate_quick is off in current HEAD: it is wrapped in #ifdef USE_QUICK and nothing in configure, Makefile.in or CMakeLists.txt defines it, whereas the 2014 commit benchmarked by zlib-bench (e176b3c) added -DUSE_QUICK -DUSE_MEDIUM in configure. A default HEAD build therefore runs deflate_fast with the CRC hash at level 1, and the 2014 'level 1 at 36% of baseline time' result does not describe it; add -DUSE_QUICK to get it.
- With USE_QUICK, level 1 silently reduces windowBits to 13 (8 KiB window), which is why its ratio drops (0.46 vs 0.37 of input size on the executable in the 2014 run).
- The public crc32() function is stock zlib 1.2.13; the PCLMULQDQ folding is used only inside deflate's gzip wrapper path.
- Past memory-safety fixes show the risk profile: out-of-bounds reads in crc_folding (issue #15) and fizzle_matches (#3), and 'deflate_medium: avoid out-of-bounds read' landed only in the November 2022 rebase.

## Known shortcomings

- Superseded by zlib-ng, whose README says its deflate medium and quick algorithms are based on Intel's zlib fork; archived 2024-03-01. Numbers come from Snellman's blog (blocked; snippets confirm level 1 at 36% of baseline time with ratio 0.46 vs 0.37, and level 5 executable 0.99 s vs 1.76 s) with no CPU or flags stated; harness public at jsnell/zlib-bench.
- HEAD (the 1.2.13 rebase) does not define USE_QUICK, so a default build has no deflate_quick at level 1; the 2014 commit e176b3c measured by Snellman had -DUSE_QUICK -DUSE_MEDIUM, so the 36% level-1 figure does not describe HEAD. Open correctness issues: #24 (deflate_medium output not always inflatable), #21, #33, #34 (inflate bugs). x86-only build. Archived 2024-03-01 at zlib 1.2.13; .NET moved from zlib-intel to zlib-ng.

## Caveats and trade-offs

The benchmark blog (snellman.net) is egress-blocked, so its figures were checked only through WebSearch snippets: level 1 at 36% of baseline time with a worse ratio (0.46 vs 0.37), and level 5 at 0.99 s vs 1.76 s on an executable and 0.75 s vs 0.69 s on JPEG. The harness is public at github.com/jsnell/zlib-bench, but its README names no compiler, flags or CPU; the i7-4770 comes from a snippet. The blog measured the 2014 state of the fork, not the later 1.2.13 rebase. The repo was archived on 2024-03-01 with Intel's 'no longer maintained' notice. Superseded by zlib-ng (already catalogued): zlib-ng's README says it has 'Deflate medium and quick algorithms based on Intel's zlib fork' and 'Includes improvements from Cloudflare and Intel forks', and its author says he 'merge[d] all the Intel optimizations'. Use zlib-ng instead; keep this entry for history and attribution. The level-1 'quick' strategy trades compression ratio for speed. The license is the standard zlib license (LICENSE file read). [retier] Measured commit e176b3c (2014) was built with -DUSE_QUICK -DUSE_MEDIUM; HEAD (1.2.13 rebase) does not define USE_QUICK by default. Superseded by zlib-ng, which absorbed the deflate medium and quick algorithms.

Fork of zlib adding SSE4.2 crc32 hashing, PCLMULQDQ CRC folding, deflate_quick (level 1) and deflate_medium (levels 4-5). Compression ratio is lower at level 1 (new speed/ratio point) and about equal at level 5. x86 only; archived by Intel with a notice that it is no longer maintained. Repo HEAD is rebased on zlib 1.2.13 per its README and zlib.h.

## Maintenance

Abandoned: archived by Intel on 2024-03-01 with an explicit no-maintenance notice and several open correctness reports; Zlib-licensed so vendoring is legal, but zlib-ng is the maintained successor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now B.
- **Tier reason:** The numbers come from Snellman's independent 2014 blog, which compares the Intel fork against stock zlib (baseline) and the Cloudflare fork. The blog itself is egress-blocked, so its level-1 and level-5 figures were confirmed only through WebSearch snippets. Its harness is public (github.com/jsnell/zlib-bench) but its README states no compiler, flags or CPU. A blog read only through snippets stays at C; it could reach B if the post is opened in full.
- **Retiered** C to B: Raised C to B: the enricher read the independent jsnell/zlib-bench README.org on github.com, which holds the full level-5 table (Intel zlib 1.49 vs stock 2.66 s on executable, 0.85 vs 1.62 s on html, 1.08 vs 0.93 s on jpeg) with pinned commits; the earlier C rested on search snippets of the blocked blog. Not A: no CPU model or compiler stated. The measured 2014 commit was built with -DUSE_QUICK -DUSE_MEDIUM, which HEAD no longer defines by default; the caveats say so.
- **Verifier notes:** Superseded by zlib-ng, which merged Intel's deflate_quick and deflate_medium according to zlib-ng's README. Consider listing it as reference or history rather than a recommended pick. Metadata confirmed from github.com: archived 2024-03-01, 144 stars, 37 forks, not a GitHub fork, last commit 2024-03-01 'archive repository'.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`, `benchmark_url`
- **Shortcomings recorded by:** independent (Snellman blog, snippet); independent jsnell/zlib-bench (commits pinned, no CPU or compiler)
- **Pages the verifier opened:**
  - <https://github.com/jtkukunas/zlib>
  - <https://github.com/jtkukunas/zlib/commits/master>
  - <https://raw.githubusercontent.com/jtkukunas/zlib/HEAD/README>
  - <https://raw.githubusercontent.com/jtkukunas/zlib/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/zlib-ng/zlib-ng/HEAD/README.md>
  - <https://github.com/jsnell/zlib-bench>
- **Sources the enricher read:**
  - <https://github.com/jtkukunas/zlib>
  - <https://github.com/jtkukunas/zlib/commits/master>
  - <https://github.com/jtkukunas/zlib/issues?q=is%3Aissue>
  - <https://github.com/jtkukunas/zlib/issues/21>
  - <https://github.com/jtkukunas/zlib/issues/24>
  - <https://github.com/jtkukunas/zlib/issues/33>
  - <https://github.com/jtkukunas/zlib/issues/34>
  - <https://raw.githubusercontent.com/jtkukunas/zlib/HEAD/README>
  - <https://raw.githubusercontent.com/jtkukunas/zlib/HEAD/README.md>
  - <https://raw.githubusercontent.com/jtkukunas/zlib/HEAD/ChangeLog>
  - <https://raw.githubusercontent.com/jtkukunas/zlib/HEAD/configure>
  - <https://raw.githubusercontent.com/jtkukunas/zlib/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/jtkukunas/zlib/HEAD/Makefile.in>
  - <https://raw.githubusercontent.com/jtkukunas/zlib/HEAD/zlib.h>
  - <https://raw.githubusercontent.com/jtkukunas/zlib/HEAD/zutil.h>
  - <https://raw.githubusercontent.com/jtkukunas/zlib/HEAD/rte_memcpy.h>
  - <https://raw.githubusercontent.com/jtkukunas/zlib/HEAD/deflate.c>
  - <https://raw.githubusercontent.com/jtkukunas/zlib/HEAD/deflate.h>
  - <https://raw.githubusercontent.com/jtkukunas/zlib/HEAD/deflate_quick.c>
  - <https://raw.githubusercontent.com/jtkukunas/zlib/HEAD/deflate_medium.c>
  - <https://raw.githubusercontent.com/jtkukunas/zlib/HEAD/crc32.c>
  - <https://raw.githubusercontent.com/jtkukunas/zlib/HEAD/crc_folding.c>
  - <https://raw.githubusercontent.com/jtkukunas/zlib/HEAD/x86.c>
  - <https://raw.githubusercontent.com/jtkukunas/zlib/HEAD/x86.h>
  - <https://raw.githubusercontent.com/jtkukunas/zlib/HEAD/inflate.c>
  - <https://raw.githubusercontent.com/jtkukunas/zlib/HEAD/inffast.c>
  - <https://raw.githubusercontent.com/jtkukunas/zlib/e176b3c23ace88d5ded5b8f8371bbab6d7b02ba8/x86.h>
  - <https://raw.githubusercontent.com/jtkukunas/zlib/e176b3c23ace88d5ded5b8f8371bbab6d7b02ba8/configure>
  - <https://raw.githubusercontent.com/jtkukunas/zlib/e176b3c23ace88d5ded5b8f8371bbab6d7b02ba8/zlib.h>
  - <https://github.com/jsnell/zlib-bench>
  - <https://raw.githubusercontent.com/jsnell/zlib-bench/HEAD/README.org>
  - <https://raw.githubusercontent.com/jsnell/zlib-bench/HEAD/bench.pl>
  - <https://github.com/dotnet/runtime/issues/87560>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/jtkukunas/zlib`) · [data/wave9/enrich/raw/github_com_jtkukunas_zlib.json](../../../data/wave9/enrich/raw/github_com_jtkukunas_zlib.json) (enrichment confidence 0.75)

</details>
