# LWMalloc

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Allocators and garbage collectors](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C` · `no license` · 🟢 active

> 618-line single-file C malloc for embedded Linux, injected via LD_PRELOAD; paper claims up to 53% faster than glibc ptmalloc.

| | |
|---|---|
| **Beats** | glibc ptmalloc |
| **Claimed result** | Up to 53% faster execution time and 23% lower memory usage than glibc ptmalloc; 530 lines of code and 20 KB vs ptmalloc's 4838 lines and 116 KB (press release and CNX Software snippets only; paper not opened). |
| **Workload** | Real applications on Raspberry Pi Zero W, Raspberry Pi 4 and Jetson Orin Nano (IEEE Internet of Things Journal 2025). |
| **Metric** | throughput |
| **Adoption** | 93 stars |
| **Last commit** | 2026-07-07 |
| **Links** | [repository](https://github.com/taehyeon-masu/lwmalloc) · [benchmark](https://ieeexplore.ieee.org/iel8/6488907/6702522/10883044.pdf) |

## Verdict

Only press-release and news snippets were reachable: up to 53% shorter execution time and 23% lower memory use than glibc ptmalloc on real applications on Raspberry Pi Zero W, Raspberry Pi 4 and Jetson Orin Nano, with 530 lines and 20 KB vs ptmalloc's 4838 lines and 116 KB. The IEEE paper, its workloads, compiler flags and glibc version could not be read, and the repo has no benchmark code, so none of this could be checked.

## Use it when

- Single-threaded C programs on 64-bit embedded Linux boards (the paper names Raspberry Pi 4 and Jetson Orin Nano) where glibc malloc's code size or overhead matters.
- Experiments comparing allocator policies (deferred coalescing, small-chunk pools) against ptmalloc on small devices.
- Reading material: the whole allocator fits in one 618-line file built on the classic CS:APP implicit/segregated-list design.

## Skip it when

- Any multi-threaded process: all free lists and the heap pointer are unsynchronized globals with no locks, so concurrent malloc/free will corrupt the heap.
- 32-bit targets: word sizes are hard-coded (WSIZE 8, DSIZE 16) instead of sizeof(size_t)/sizeof(void\*), and issue #2 (open, no reply) reports a segfault of the bundled test on a 32-bit Allwinner ARM SoC, even though the paper lists a Raspberry Pi Zero W.
- Code that needs 16-byte alignment (SSE/NEON vectors, long double, max_align_t): ALIGNMENT is 8.
- Programs that call posix_memalign, aligned_alloc or memalign (common in C++ runtimes and media libraries): those still go to glibc, and passing such pointers to the preloaded free() is undefined behaviour.
- Anything shipped: there is no license (issue #1, open since 2025-09-04, unanswered), so the code cannot legally be reused.

## How it is fast

Small requests (up to 120 bytes) go to per-size singly linked bins carved from 4 KiB sbrk chunks, so they allocate and free in O(1) with an 8-byte header. Larger blocks use boundary tags (header plus footer) and 62 segregated free lists searched first-fit. Frees next to a free neighbour are parked on a buffer list and merged lazily on the next large malloc or realloc (deferred coalescing), which skips work that ptmalloc does on every free. There are no locks, arenas, tcache or per-thread state, which is where both the small footprint and the single-threaded speed come from.

## Compared with alternatives

Pick LWMalloc over rlsf or Talc only for single-threaded 64-bit Linux processes you can LD_PRELOAD and only for study, since it has no license; for a licensed small-footprint allocator with real-time bounds rlsf (TLSF, 260-320 cycles vs dlmalloc 450-750) is the safer choice, and for general multi-threaded use any of the jemalloc/mimalloc-class siblings apply.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | none (libc sbrk, memset, memcpy) |
| **Minimum toolchain** | not documented; Makefile uses gcc -O2 -fPIC. The code returns values from void functions and stores NULL through a size_t pointer, which GCC 14's default errors (-Wreturn-mismatch, -Wint-conversion) reject, so newer compilers may need -fpermissive or older -std flags |
| **Platforms** | Linux with sbrk; effectively 64-bit only (see 32-bit issue #2) |
| **Thread safety** | none: no locking anywhere in lwmalloc.c |
| **Drop-in for the baseline** | partial — LD_PRELOAD replacement for malloc/calloc/realloc/free only; no aligned allocation, malloc_usable_size, mallinfo, malloc_trim or thread support |

## Gotchas

- Memory is never returned to the OS: the heap only grows via sbrk, and small-object chunks are never merged back into the large-block pool.
- Error handling is broken in places: lw_mem_init and lw_sbrk compare sbrk's result to NULL instead of (void \*)-1, lw_sbrk ignores sbrk failure, and lw_calloc reads the header of the returned pointer before its NULL check and does not check nmemb\*size for overflow.
- The Makefile builds liblwmalloc.so while the README tells you to preload lwmalloc.so.
- The bundled test.c discards realloc's return value and then frees the old pointer, which is a double free under LWMalloc (a 4-to-8-byte realloc moves the block); in lw_realloc the branch that merges both neighbours is unreachable because the preceding 'if (!next_alloc)' already catches that case.

## Known shortcomings

- No locks (unsafe in multi-threaded programs), 8-byte alignment, no posix_memalign or aligned_alloc, WSIZE hard-coded to 8. Issue 2: the test segfaults on 32-bit ARM, yet the paper lists a Pi Zero W (32-bit), so the published code may not be what was measured. calloc reads the header before the NULL check and has no overflow check; the sbrk failure check is wrong; test.c double-frees after a discarded realloc; likely fails under GCC 14 default errors. Still no license (issue 1). The 53% and 23% figures are snippet only.

## Caveats and trade-offs

Numbers from press-release search snippets only; paper (IEEE IoT Journal 2025) blocked here and repo README carries no numbers or benchmark code (only lwmalloc.c, Makefile, test.c). No LICENSE file in the repo (LICENSE, LICENSE.md, LICENSE.txt, COPYING all 404), so reference only. Compares to ptmalloc, not jemalloc or mimalloc; targets single-board embedded systems (Raspberry Pi Zero W, Pi 4, Jetson Orin Nano).

About 530 lines, about 20 KB footprint; LD_PRELOAD injection; for resource-constrained devices.

## Maintenance

10 commits, 93 stars, last commit 2026-07-07, three open issues (license, 32-bit segfault, mallinfo) with no maintainer replies; unlicensed and not thread-safe, so reference only.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification B, tier now C.
- **Tier reason:** Peer-reviewed IEEE IoT Journal 2025 paper exists (DOI 10.1109/JIOT.2025.3541247 cited in README), but the paper, ieeexplore and the press release (eurekalert) are egress-blocked; the 53%/23% figures were seen only in search snippets of the press release and CNX Software. Repo has no benchmark code or numbers, so the win could not be checked against the paper; capped at C until the paper is read.
- **Verifier notes:** Real peer-reviewed allocator; retier to B if the IEEE paper becomes reachable and shows the ptmalloc comparison. Stars 93, 10 commits, last commit 2026-07-07 confirmed on github.com.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** snippet only
- **Pages the verifier opened:**
  - <https://github.com/taehyeon-masu/lwmalloc>
  - <https://github.com/taehyeon-masu/lwmalloc/commits>
  - <https://raw.githubusercontent.com/taehyeon-masu/lwmalloc/HEAD/README.md>
  - <https://raw.githubusercontent.com/taehyeon-masu/lwmalloc/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/taehyeon-masu/lwmalloc>
  - <https://raw.githubusercontent.com/taehyeon-masu/lwmalloc/HEAD/README.md>
  - <https://raw.githubusercontent.com/taehyeon-masu/lwmalloc/HEAD/Makefile>
  - <https://raw.githubusercontent.com/taehyeon-masu/lwmalloc/HEAD/lwmalloc.c>
  - <https://raw.githubusercontent.com/taehyeon-masu/lwmalloc/HEAD/test.c>
  - <https://github.com/taehyeon-masu/lwmalloc/issues>
  - <https://github.com/taehyeon-masu/lwmalloc/issues/1>
  - <https://github.com/taehyeon-masu/lwmalloc/issues/2>
  - <https://github.com/taehyeon-masu/lwmalloc/issues/3>
  - WebSearch snippets: https://www.eurekalert.org/news-releases/1096402, https://www.cnx-software.com/2025/09/03/lwmalloc-lightweight-dynamic-memory-allocator-for-embedded-systems/ (fetch EGRESS_BLOCKED), https://ieeexplore.ieee.org/document/10883044/
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/taehyeon-masu/lwmalloc`) · [data/wave11/enrich/raw/github_com_taehyeon_masu_lwmalloc.json](../../../data/wave11/enrich/raw/github_com_taehyeon_masu_lwmalloc.json) (enrichment confidence 0.75)

</details>
