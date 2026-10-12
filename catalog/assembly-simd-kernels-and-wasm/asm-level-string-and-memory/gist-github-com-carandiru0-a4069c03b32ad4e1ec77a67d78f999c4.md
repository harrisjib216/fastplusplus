# memcpy_threaded / memset_threaded (Carandiru0 mem.h gist)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Assembly-level string and memory routines](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `CC-BY-NC-SA-4.0` · 🔴 abandoned

> MSVC/Windows header that splits huge memcpy and memset across Intel TBB threads using AVX2 non-temporal loads and stores.

| | |
|---|---|
| **Beats** | MSVC compiler-intrinsic memcpy and memset (the gist declares #pragma intrinsic(memcpy) and #pragma intrinsic(memset), i.e. the compiler/CRT built-ins), single-threaded and also run multithreaded; MSVC version not stated |
| **Claimed result** | Code comments: 'intrinsic memcpy (single threaded) at 22 GB/s', 'intrinsic memcpy (multithreaded) at 29 GB/s', '___memcpy_threaded at 33.3 GB/s (memory bandwidth is saturated)'; ___memset_threaded 'has the same 33.3 GB/s, but in this case it's all write bandwidth'. The 33.3 GB/s for memcpy is a combined figure ('read 10 GB/s + write 23.3 GB/s'). About 1.5x over the single-threaded intrinsic and about 1.15x over the multithreaded intrinsic (derived from page data). |
| **Workload** | Large-buffer copy and fill using AVX/SSE intrinsics, Intel TBB parallel_for and PrefetchVirtualMemory; header comments quote GB/s for single-thread intrinsic, multithreaded intrinsic and the threaded routine. |
| **Metric** | throughput |
| **Adoption** | 1 star, 0 forks |
| **Last commit** | 2022-06-12 |
| **Links** | [repository](https://gist.github.com/Carandiru0/a4069c03b32ad4e1ec77a67d78f999c4) · [benchmark](https://gist.github.com/Carandiru0/a4069c03b32ad4e1ec77a67d78f999c4) |

## Verdict

The author's code comments report memory-controller bus traffic from Intel PCM: 22 GB/s for MSVC's intrinsic memcpy on one thread, 29 GB/s for it multithreaded, and 33.3 GB/s (10 GB/s read plus 23.3 GB/s write) for ___memcpy_threaded. ___memset_threaded is also reported at 33.3 GB/s of writes. That is about 1.15x over the threaded intrinsic (derived from page data). No CPU model, compiler version, flags, buffer size or harness is given, and the code that produced the numbers is not in the gist.

## Use it when

- Windows x64 MSVC code that already links oneTBB and needs to clear or copy buffers of many megabytes, where a single core cannot saturate memory bandwidth.
- Destinations mapped write-combining (GPU upload heaps, mapped device memory): the author's later revision keeps the streaming kernels only for that case and says they give up to 16x there.
- As a reference for a threaded non-temporal fill or copy pattern (TBB grain splitting plus AVX2 streaming stores) to rewrite under your own licence terms.

## Skip it when

- Ordinary write-back memory: in February 2023 the author's own Common-Libraries version replaced the streaming kernels in ___memcpy_threaded/___memset_threaded with per-block calls to the intrinsic memcpy/memset, keeping streaming only in new \*_stream variants for write-combined memory.
- Any memset with a non-zero byte value: the fill vector is _mm256_set1_epi32(value), so value 0x41 writes the pattern 41 00 00 00, not 41 41 41 41.
- Sizes that are not multiples of 16 bytes, or buffers aligned to less than 32 bytes: the kernels drop the last bytes % 16 bytes and use aligned 256-bit loads and stores.
- Small or medium buffers, data that will be read again soon (non-temporal stores evict it from cache), Linux/macOS, GCC/Clang without MSVC extensions, or commercial products (CC BY-NC-SA 4.0).

## How it is fast

Memset writes 256 bytes per iteration with _mm256_stream_si256/_mm256_stream_ps (non-temporal stores that skip read-for-ownership). Memcpy bounces each 4 KiB block through a 4 KiB thread_local buffer: MOVNTDQA streaming loads (_mm256_stream_load_si256) into the buffer, an mfence, then ordinary loads and non-temporal stores to the destination. Several threads are used because one core cannot saturate DRAM bandwidth; the author reports bus traffic rising from 22 GB/s (single-threaded intrinsic memcpy) and 29 GB/s (threaded intrinsic) to 33.3 GB/s.

## Compared with alternatives

Pick it over fast-strlen.c (bjourne) or the riteme memset gist only when you are on Windows/MSVC with TBB and want threaded non-temporal fills or copies, especially into write-combined memory. Those siblings are portable C/C++ with a timed harness and stated hardware, while this one has comment-only numbers and a memset value bug. For measured copy and fill kernels, tinymembench is the better reference.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | Intel oneTBB (tbb::parallel_for, tbb::blocked_range, not included by the header), the author's ..\Math\superfastmath.h from Carandiru0/Common-Libraries (which pulls in DirectXMath and vec4_t.h) for SFM::roundToMultipleOf, and the Windows SDK for PrefetchVirtualMemory |
| **Minimum toolchain** | MSVC with C++20 (constinit, __declspec(selectany) thread_local, #pragma loop(ivdep), __vectorcall); exact version not documented (the repo history mentions a 'vs 2022' commit) |
| **Platforms** | Windows x64 with AVX2 |
| **Thread safety** | Not documented; each call blocks in a TBB parallel_for and the bounce buffer is thread_local, so concurrent calls from different threads look safe from the code |
| **Drop-in for the baseline** | partial — different names and a required alignment template argument; memset matches only for value 0 (or -1); both routines need 32-byte-aligned pointers and sizes that are multiples of 16, and source and destination must not overlap |

## Gotchas

- Correctness bug: ___memset_threaded broadcasts the int with _mm256_set1_epi32 instead of a byte broadcast, so only zero (and -1) fills match memset; the 33.3 GB/s memset figure is presumably a zero fill (not stated). The bug is still present in the current Common-Libraries ___memset_threaded_stream.
- Tails are silently dropped: the kernels stop at 16-byte granularity, so the final bytes % 16 bytes are never copied or set. The 'alignment' template parameter is never read, and the header's 'minimum alignment of 16 bytes' note understates the 32 bytes the aligned 256-bit loads and stores need.
- The TBB grain is counted in __m256i elements (blocked_range over __m256i pointers), so the default block_size of 4096 makes 64-128 KiB tasks, not the 4 KB per thread the comment says.
- The numbers are memory-controller bus traffic read from Intel PCM, with no CPU, compiler, buffer size or timing harness. The memcpy split (read 10 GB/s, write 23.3 GB/s) does not balance as a DRAM-to-DRAM copy would, so 33.3 GB/s cannot be converted to bytes copied per second. MOVNTDQA streaming loads only act as non-temporal on write-combining memory; on ordinary write-back memory a CPU may treat them as plain loads (Intel SDM text, via search snippets).

## Known shortcomings

- Numbers are code comments only (PCM bus traffic, memcpy 33.3 GB/s counts read plus write) with no CPU or compiler; only about 1.15x over the multithreaded MSVC intrinsic (derived); the header is not standalone. CC BY-NC-SA (reference). Last revision 2022-06-12.
- Enricher: the gist is byte-identical to Carandiru0/Common-Libraries Utility/mem.h at commit c4538da; ___memset_threaded broadcasts with _mm256_set1_epi32, so only 0 and -1 fills match memset; the final bytes % 16 are silently dropped; the alignment template parameter is never read and aligned 256-bit ops need 32 bytes, not the 16 the header states; the TBB grain counts __m256i elements so tasks are 64-128 KiB, not 4 KB; the author's 2023-02-27 commit a967e71 switched both routines back to threaded intrinsic memcpy/memset for normal memory (streaming kept only in the \*_stream variants); the comment-only PCM figures (read 10 plus write 23.3 GB/s) do not balance for a copy; CC BY-NC-SA 4.0, reference only.

## Caveats and trade-offs

Numbers are code comments from the author, measured as memory-controller traffic with Intel PCM, with no CPU model, compiler, flags, buffer size or harness. The baseline is MSVC's intrinsic memcpy/memset (#pragma intrinsic), not a custom routine. The 33.3 GB/s memcpy figure is read plus write bus traffic (10 + 23.3 GB/s), so it is not bytes-copied throughput, and it is unclear whether the 22 and 29 GB/s baseline figures were counted the same way; streaming stores also avoid read-for-ownership traffic, which changes what bus GB/s means. Against the fair multithreaded-intrinsic row the gain is only about 1.15x (derived from page data). The '16x faster' line about SSE stores over rep stosb is quoted from a Microsoft MSRC blog post, not measured. The header is not standalone: it includes the author's ..\Math\superfastmath.h, uses TBB parallel_for and PrefetchVirtualMemory without including their headers, and ___prefetch_vmem is never called (a commenter noted this). Windows/MSVC only (__declspec, __vectorcall), AVX2 streaming intrinsics. Four revisions, all June 10-12, 2022; the June 10, 2025 'last active' date is a comment, not a code change. Licence CC BY-NC-SA 4.0 (non-commercial, not OSI) next to an 'All Rights Reserved' copyright line.

Windows and MSVC specific (__declspec, #pragma loop, PrefetchVirtualMemory) and needs Intel TBB; threads only pay off once a single core cannot saturate memory bandwidth; the NonCommercial-ShareAlike licence is not OSI-approved.

## Maintenance

Abandoned as a gist (four revisions, June 10-12, 2022). The live copy is Utility/mem.h in Carandiru0/Common-Libraries, last changed February 27, 2023, where the threaded routines now call the intrinsic memcpy/memset for normal memory. It is reference-only: Windows/MSVC/TBB-bound, licensed CC BY-NC-SA 4.0 (non-commercial, not OSI) under an 'All Rights Reserved' line, and carrying a memset value bug.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party GB/s figures appear only as code comments in mem.h (said to be read off Intel PCM in real time); no harness, timing code, CPU model, compiler or flags, so C.
- **Verifier notes:** Numbers match the gist comments. Fixed the baseline description (it is MSVC's intrinsic memcpy/memset, not the author's own routine) and the last-change date (last revision 2022-06-12, so abandoned); the 2025 date was a comment. Shortcomings: comment-only numbers from PCM bus traffic, no CPU/compiler, only about 1.15x over a multithreaded intrinsic, non-commercial licence, header not standalone.
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `last_commit`, `maintenance_status`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-64 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://gist.github.com/Carandiru0/a4069c03b32ad4e1ec77a67d78f999c4>
  - <https://gist.github.com/Carandiru0/a4069c03b32ad4e1ec77a67d78f999c4/revisions>
- **Sources the enricher read:**
  - <https://gist.github.com/Carandiru0/a4069c03b32ad4e1ec77a67d78f999c4>
  - <https://github.com/Carandiru0?tab=repositories>
  - <https://github.com/Carandiru0/Common-Libraries>
  - <https://github.com/Carandiru0/Common-Libraries/commits/main/Utility/mem.h>
  - <https://raw.githubusercontent.com/Carandiru0/Common-Libraries/HEAD/Utility/mem.h>
  - <https://raw.githubusercontent.com/Carandiru0/Common-Libraries/c4538da/Utility/mem.h>
  - <https://raw.githubusercontent.com/Carandiru0/Common-Libraries/a967e71/Utility/mem.h>
  - <https://raw.githubusercontent.com/Carandiru0/Common-Libraries/HEAD/Math/superfastmath.h>
  - https://community.intel.com/t5/Intel-ISA-Extensions/Do-Non-Temporal-Loads-Prefetch/m-p/1027104 (WebSearch snippet only)
  - https://shell-storm.org/x86doc/MOVNTDQA.html (WebSearch snippet only)
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://gist.github.com/carandiru0/a4069c03b32ad4e1ec77a67d78f999c4`) · [data/wave13/enrich/raw/gist_github_com_carandiru0_a4069c03b32ad4e1ec77a67d78f999c4.json](../../../data/wave13/enrich/raw/gist_github_com_carandiru0_a4069c03b32ad4e1ec77a67d78f999c4.json) (enrichment confidence 0.7)

</details>
