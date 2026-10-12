# Memset by memcpy doubling (riteme gist: 'Memcpy is faster than memset on Intel i7 12700 with glibc 2.36')

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Assembly-level string and memory routines](README.md)</sub>

**Tier A** (reproducible public benchmark) · Study only · `C++` · `no license` · ⚪ unknown

> A 20-line memset wrapper that fills huge buffers by memcpy-doubling an 8 MiB block, 2.47x faster than glibc 2.36 memset.

| | |
|---|---|
| **Beats** | glibc 2.36 memset() |
| **Claimed result** | glibc memset 6.23 s user / 6.34 s elapsed versus my_memset 2.47 s user / 2.57 s elapsed for 100 fills of 1 GiB on an i7-12700 with glibc 2.36 (single /usr/bin/time run each). The author calls this about 60 percent faster. That means about 60 percent less time, a 2.47x speedup (derived from page data). |
| **Workload** | Fill a 1 GiB char buffer (1 \* 1024 \* 1024 \* 1024) 100 times with either glibc memset or my_memset. Above a threshold constant written as 2 \* 2048 \* 2048 (8 MiB, although the code comment says 2 MiB), my_memset memsets the first chunk once. It then copies that same chunk with memcpy(s + i, s, threshold) to each later chunk-sized slot (the ranges do not overlap) and memsets any tail. The test prints a[0] so the fills are not optimised away. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-12700 (12 cores, 20 threads), 15 GiB RAM, Manjaro Linux kernel 6.1.0-1, glibc 2.36-6 |
| **Compiler and flags** | g++ memset_test.cpp -O3 -march=native (g++ version not stated); -DUSE_MY_MEMSET selects the custom version |
| **Adoption** | Gist with 1 star, 12 revisions and 3 comments (January 1-5, 2023); last active 2025-12-27. |
| **Links** | [repository](https://gist.github.com/riteme/d584b0bf6cced5d74cde7aa8d2195e75) · [benchmark](https://gist.github.com/riteme/d584b0bf6cced5d74cde7aa8d2195e75) |

## Verdict

100 fills of a 1 GiB buffer (about 107 GB written) took 6.34 s elapsed (6.23 s user) with glibc 2.36-6 memset and 2.57 s elapsed (2.47 s user) with my_memset, i.e. about 16.9 vs 41.8 GB/s and 2.47x (derived from page data). Built with g++ -O3 -march=native on an Intel Core i7-12700 under Manjaro with Linux 6.1, single run each. The glibc 2.36 sources confirm that memset takes rep stosb at this size while memcpy takes the non-temporal path, which explains the gap.

## Use it when

- Filling or zeroing buffers of tens of MiB or more on x86-64 Linux with glibc older than 2.40, where memset has no non-temporal path.
- Write-once fills that will not be read back soon (non-temporal stores leave the destination out of cache).
- As a quick experiment showing whether non-temporal stores help your fill workload, before writing a proper streaming memset.

## Skip it when

- glibc 2.40 or newer on Intel and AMD: memset itself switches to a non-temporal store loop above the same non-temporal threshold (except on Skylake-AVX512 and Cannon Lake, where glibc sets Avoid_Non_Temporal_Memset), so the trick probably gives nothing there (not measured).
- Buffers under 16 MiB: with the 8 MiB block, no memcpy runs until n reaches 16 MiB, so smaller sizes only pay for an extra branch or a split memset.
- Buffers that are read right after the fill and fit in cache: non-temporal stores push the data out to DRAM.
- CPUs whose last-level cache is smaller than 8 MiB, where re-reading the source block probably adds DRAM read traffic (inference, not measured); also non-glibc libcs (musl, MSVC CRT, macOS) whose memcpy and memset thresholds differ.

## How it is fast

The gain comes from glibc's size heuristics, not from memcpy being inherently faster. In glibc 2.36, x86-64 memset uses rep stosb for every size above __x86_rep_stosb_threshold (2048 bytes). memcpy above __x86_shared_non_temporal_threshold (3/4 of one thread's cache share, well below 8 MiB on this CPU) switches to a page-interleaved loop with non-temporal stores that skip read-for-ownership. The repeated 8 MiB source block fits in the i7-12700's 25 MiB L3, so the copy mostly reads from cache while it streams writes to DRAM.

## Compared with alternatives

Use it on glibc 2.36-2.39 when you want a no-intrinsics, portable one-function fix and cannot vendor fancy-memset or nadavrot/memset_benchmark (AVX2 assembly) or write an explicit non-temporal store loop like Carandiru0's memset_threaded. Those siblings stream directly and do not re-read an 8 MiB source, but they need x86 assembly or intrinsics.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (libc memcpy and memset) |
| **Minimum toolchain** | C++11 (constexpr); trivially portable to C |
| **Platforms** | any; the measured benefit is specific to x86-64 glibc before 2.40 |
| **Thread safety** | Stateless and reentrant, same as memset |
| **Drop-in for the baseline** | yes |

## Gotchas

- The constant 2 \* 2048 \* 2048 is 8 MiB, not the 2 MiB that the code comments say.
- Harness flaw: one /usr/bin/time run per variant, unpinned, on a hybrid 8P+4E Alder Lake (lscpu shows 12 cores and 9 L2 instances) with frequency scaling active. There are no repetitions or variance and the g++ version is not stated. Both runs include the 1 GiB first-touch faults, with near-equal fault counts (639 vs 634 minor).
- The 'contradicting' perf bench mem numbers in the comments (i7-12700: memset 72.70 GB/s vs memcpy 31.20 GB/s) use 1 MB cache-resident buffers, a different regime from the 1 GiB fill. The result really compares rep stosb against glibc's non-temporal memcpy path, not memset against memcpy.
- The gist has no licence, so the code is not formally reusable; the idea is easy to re-implement.

## Known shortcomings

- One run per configuration with the g++ version unstated and no licence (reference); the chunk is 8 MiB (the code comment says 2 MiB); the perf bench contradiction used 1 MB cache-resident buffers (a different regime); glibc 2.40's non-temporal memset probably closes the gap (snippet only).
- Enricher: glibc 2.36 sources confirm the mechanism (memset uses rep stosb above 2048 B, memcpy uses non-temporal stores above its threshold) but glibc 2.40 adds a non-temporal memset on Intel and AMD, so the gain is likely gone (not measured); the harness is one unpinned /usr/bin/time run per variant on a hybrid 8P+4E i7-12700 with frequency scaling, no repetitions, g++ version unstated; the 8 MiB threshold means memcpy only kicks in from 16 MiB (the comments say 2 MiB).

## Caveats and trade-offs

This is a single wall-clock run per variant with no repetitions or variance, and the g++ version is not stated. The chunk is 8 MiB (2 \* 2048 \* 2048), not the 2 MiB the comment says. The source chunk is always the first chunk, so it likely stays in the i7-12700's 25 MB L3 while the destination streams to DRAM. The 'contradiction' in the comments is a different regime: perf bench mem (author's i7-12700: memset default 72.70 GB/s vs memcpy default 31.20 GB/s; Ristovski's Ryzen 5700G: memcpy default 51.79 vs memset default 37.38 GB/s) ran on 1 MB cache-resident buffers, not on 1 GiB fills. Neither commenter ran memset_test.cpp, and sada-amd only guessed rep stosb vs vector moves without a disassembly. The baseline is probably outdated (WebSearch snippet only, patchwork and Phoronix not opened): glibc before May 2024 used rep stosb for all large memsets. Noah Goldstein's 'x86: Improve large memset perf with non-temporal stores' (glibc 2.40, Intel only, disabled on Skylake Server) added the non-temporal path that memcpy already had, so the gap this gist exploits is likely closed on glibc 2.40+. The gist has no licence.

A technique snippet, not a library. It only makes sense for very large fills (the first block is memset, the rest is doubled with memcpy), and it needs a correct handling of the final partial block. No licence on the gist.

## Maintenance

Gist from January 1-5, 2023 (12 revisions, 1 star, no licence), not maintained. It is a reference for a glibc-version-specific trick that glibc 2.40's non-temporal memset has probably made unnecessary.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** The gist has the full benchmark (memset_test.cpp, with my_memset selected by -DUSE_MY_MEMSET), the compile command (g++ -O3 -march=native; the g++ version is not stated), the CPU (Intel Core i7-12700) and glibc 2.36-6. Its /usr/bin/time output gives 6.23 s user / 6.34 s elapsed for glibc memset and 2.47 s user / 2.57 s elapsed for my_memset. That is enough for tier A, but it is a single run with no repetitions.
- **Verifier notes:** The measurement is valid and crude: both variants produce the same fill, and the memcpy ranges do not overlap. Tier A stands on code + flags + CPU + glibc version, but the result is one run on glibc 2.36. glibc 2.40's non-temporal large memset probably removes the advantage (snippet only). Record shortcomings: single run, unstated g++ version, the code comment says 2 MiB but the chunk is 8 MiB, the baseline is superseded, and there is no licence.
- **Fields the verifier corrected:** `workload`, `claimed_speedup`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-92 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://gist.github.com/riteme/d584b0bf6cced5d74cde7aa8d2195e75>
- **Sources the enricher read:**
  - <https://gist.github.com/riteme/d584b0bf6cced5d74cde7aa8d2195e75>
  - <https://raw.githubusercontent.com/bminor/glibc/glibc-2.36/sysdeps/x86_64/multiarch/memset-vec-unaligned-erms.S>
  - <https://raw.githubusercontent.com/bminor/glibc/glibc-2.36/sysdeps/x86_64/multiarch/memmove-vec-unaligned-erms.S>
  - <https://raw.githubusercontent.com/bminor/glibc/glibc-2.36/sysdeps/x86/dl-cacheinfo.h>
  - <https://raw.githubusercontent.com/bminor/glibc/glibc-2.40/sysdeps/x86_64/multiarch/memset-vec-unaligned-erms.S>
  - <https://raw.githubusercontent.com/bminor/glibc/glibc-2.40/sysdeps/x86_64/multiarch/memmove-vec-unaligned-erms.S>
  - <https://raw.githubusercontent.com/bminor/glibc/glibc-2.40/sysdeps/x86/dl-cacheinfo.h>
  - <https://raw.githubusercontent.com/bminor/glibc/glibc-2.40/sysdeps/x86/cpu-features.c>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://gist.github.com/riteme/d584b0bf6cced5d74cde7aa8d2195e75`) · [data/wave13/enrich/raw/gist_github_com_riteme_d584b0bf6cced5d74cde7aa8d2195e75.json](../../../data/wave13/enrich/raw/gist_github_com_riteme_d584b0bf6cced5d74cde7aa8d2195e75.json) (enrichment confidence 0.75)

</details>
