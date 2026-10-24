# FreeGuard

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Allocators](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `GPL-2.0` · 🔴 abandoned

> Research secure malloc (CCS 2017) with near-glibc speed, far faster than the DieHarder and OpenBSD secure allocators.

| | |
|---|---|
| **Beats** | DieHarder (secure allocator) and OpenBSD malloc; roughly parity with the default Linux (glibc) allocator |
| **Claimed result** | Seen only in WebSearch snippets of the CCS 2017 paper: FreeGuard averages 1.8% runtime overhead (arithmetic mean; 1.4% geometric mean) relative to the default Linux (glibc) allocator over 19 multithreaded applications, against OpenBSD malloc 34% (arithmetic) or 22% (geometric) and DieHarder 88% (arithmetic) or 36% (geometric); canneal and freqmine exceed 10% overhead under FreeGuard. A later patent for the group's Guarder allocator quotes DieHarder 74%, OpenBSD 31% and FreeGuard 1% from a different setup. The win is against secure allocators (DieHarder, OpenBSD); against glibc it is near parity (about 2% slower), not faster. |
| **Workload** | Average runtime overhead relative to the default Linux allocator over 19 multithreaded applications: 11 from PARSEC plus real applications including Apache, Firefox and MySQL (per search snippets of the paper; the full list was not read). OpenBSD malloc run with junking level 0 and DieHarder (08/05/2017 version) with heap multiplier 8/7 and destroy-on-free on, per the snippets. |
| **Metric** | other |
| **Hardware** | 16-core Xeon E5-2640, Ubuntu 16.04 (from a search snippet of the paper's setup; unverified) |
| **Compiler and flags** | GCC 4.9.1 -O2 (from a search snippet of the paper's setup; DieHarder heap multiplier 8/7 and default settings; unverified) |
| **Adoption** | 38 stars |
| **Last commit** | 2018-01-04 |
| **Links** | [repository](https://github.com/utsasrg/freeguard) · [benchmark](https://arxiv.org/abs/1709.02746) |

## Verdict

Per WebSearch snippets of the CCS 2017 paper (the paper itself could not be opened): over 19 multithreaded applications (11 PARSEC plus Apache, Firefox, MySQL, Memcached, SQLite and others), averaged over ten runs and normalised to the default glibc allocator, FreeGuard ran 1.8% slower (arithmetic mean; 1.4% geometric), OpenBSD malloc 34% (22% geometric) and DieHarder 88% (36% geometric). Hardware, compiler and memory-overhead figures were not confirmed, and the repository carries no benchmark code.

## Use it when

- Research or hardening experiments that need overflow, double-free and use-after-free mitigation on multithreaded Linux x86-64 programs at about glibc speed (1.8% average overhead in the paper, per search snippets).
- Replacing DieHarder or OpenBSD-style malloc where their 22-36% (geometric mean) slowdown is unacceptable.
- Programs with at most a few dozen threads, ordinary malloc/free/realloc use and no over-aligned allocations.
- As a readable reference design for a BiBOP secure allocator with shadow-memory metadata (the same group's successor is Guarder).

## Skip it when

- When raw speed is the goal: it is at best about glibc speed, and canneal and freqmine exceeded 10% overhead in the paper (per search snippets).
- C++17 code that uses over-aligned new, or any code calling aligned_alloc, valloc or pvalloc: FreeGuard's versions print an error and return NULL, and malloc_usable_size is not provided.
- Programs with more than 128 live threads, threads that need stacks larger than about 8 MB, or code that runs on fibers, coroutine stacks or sigaltstack handlers (see gotchas).
- Production use: abandoned since January 2018, a reported malloc(SIZE_MAX) integer overflow still in the source, random seed taken from time(NULL), and invalid frees of non-heap pointers only logged (open issues #2 and #3).
- Memory-constrained deployments: power-of-two classes plus the canary byte round a 16-byte request up to a 32-byte block, and startup reserves terabytes of virtual address space (MAP_NORESERVE), which fails under ulimit -v.

## How it is fast

It is a BiBOP (big bag of pages) allocator: power-of-two size classes, per-thread heaps, bump-pointer allocation and per-bag freelists kept in separate shadow memory, so most allocations take no lock and need no in-object headers. The thread index comes from shifting the stack address (each thread runs in a fixed 8 MB stack slot), not from a TLS lookup. Security is added cheaply on top: four randomly chosen bag sets per size class, randomised 4-16 MB bag sizes, a 10% chance of a guard page at each page boundary, a one-byte canary per object checked on free together with two neighbours each side, and FIFO freelists that delay reuse.

## Compared with alternatives

None of the speed-oriented siblings (mimalloc, jemalloc, snmalloc, TCMalloc) is described in this catalog as a secure allocator with randomised layout, guard pages and canaries, so FreeGuard is the pick only when those defences matter more than speed; for throughput over glibc, choose mimalloc or snmalloc, and NUMAlloc from the same UTSA group for NUMA machines.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | libdl, libpthread, librt; bundled SSE2 random-number generator (rng/sse2rng.c) |
| **Minimum toolchain** | C++11; the Makefile uses clang++ -O2 with a hard-coded GCC 4.8 libstdc++ include path (the paper reportedly used GCC 4.9.1, unverified) |
| **Platforms** | Linux x86-64 only (glibc __libc_start_main and pthread interposition, -msse2, x86 inline assembly) |
| **Thread safety** | Thread-safe through per-thread heaps plus per-bag spinlocks on freelists; at most 128 live threads, and threads are only recognised if created through the interposed pthread_create. |
| **Drop-in for the baseline** | partial — LD_PRELOAD covers malloc, free, calloc, realloc, memalign and posix_memalign, but aligned_alloc, valloc and pvalloc return NULL, malloc_usable_size is missing, every thread stack is forced to 8 MB minus guard pages, and memory overhead is higher than glibc. |

## Gotchas

- Security bugs in the shipped source: the canary byte is added to the size with no overflow check, so malloc(SIZE_MAX) returns a small valid block (issue #1, closed in 2021, though no commit has landed since 2018); calloc multiplies nelem by elsize without an overflow check; srand is seeded with time(NULL) (issue #2, 'Guessable random').
- xthread::thread_create has no return statement, so the interposed pthread_create returns an indeterminate value (undefined behaviour; -Wall warns). When all 128 thread slots are in use, allocThreadIndex hands back an out-of-range index with no check. Source reading, not tested.
- The thread index is computed from the current stack address; code running outside FreeGuard's stack slots (fibers, ucontext or Boost.Context stacks, sigaltstack handlers) maps to thread 0 and shares its unlocked bump pointer with the main thread. Source reading, not tested.
- The README says plain make uses rand(), but the Makefile always defines SSE2RNG and MANYBAGS, and the security features (guard pages, random guards, canaries, FIFO freelist) are on unless NO_SECURITY is set; destroy-on-free is off by default, unlike the DieHarder configuration it was compared with.

## Known shortcomings

- Paper unreachable (arXiv egress blocked), checked from snippets only: 1.8% mean overhead vs glibc over 19 multithreaded apps, so the win is only against secure allocators (OpenBSD 22%, DieHarder &gt;36%, DieHarder runs destroy-on-free); parity with glibc. No bench code in the repo. Abandoned, last commit 2018-01-04. Could reach B once someone reads the paper.
- Security bugs: malloc(SIZE_MAX) overflow (issue #1), unchecked calloc multiplication, time(NULL) seed (issue #2), aligned_alloc/valloc/pvalloc return NULL (C++17 aligned new fails), wrong memalign formula; quality bugs from source reading: thread_create lacks a return, no guard past 128 live threads, thread index from stack address. Claim text mixed arithmetic and geometric means (fixed). No commit since 2018.

## Caveats and trade-offs

Snippet only: arxiv.org, ar5iv, deepai, the West Point copy, the co-author's site, usenix.net and patents.justia.com were unreachable, so the paper's evaluation section was never opened and every number comes from WebSearch result summaries. Hardware (Xeon E5-2640) and compiler (GCC 4.9.1 -O2) come from earlier snippets and were not confirmed in this verification. The repo has no paper, benchmark scripts or results (6 commits, no benchmark directory); the README only cites the CCS 2017 paper and makes unquantified 'dramatically improve performance' claims. A peer-reviewed paper would normally rate tier B; held at C because the numbers could not be read at the source. The claim against glibc is parity (1.8% average overhead), the speed win is only against other secure allocators (DieHarder, OpenBSD); DieHarder still enables destroy-on-free while FreeGuard and OpenBSD do not, so the comparison is not security-equivalent. Figures differ between the paper (OpenBSD 22%, DieHarder &gt;36%) and later Guarder material (31%, 74%), which used a different setup. Authors' own implementation and measurement. No commits since 2018-01-04; the same group's successor is UTSASRG/Guarder. [retier] Enricher: the earlier claim text compared FreeGuard's arithmetic mean with the rivals' geometric means; compare like with like (above). Security bugs in the code: malloc(SIZE_MAX) size overflow (issue #1, closed 2021, no commit since 2018), an unchecked calloc multiplication, a time(NULL) seed (issue #2), aligned_alloc, valloc and pvalloc return NULL (so C++17 aligned new fails) and a wrong memalign formula. Quality bugs from source reading (not tested): thread_create lacks a return statement, nothing guards past 128 live threads, and the thread index comes from the stack address, so fibers or sigaltstack map to thread 0 and race its bump pointer. The Makefile uses clang++, not the paper's GCC 4.9.1.

Security-oriented drop-in malloc (LD_PRELOAD or link) guarding against heap overflow, use-after-free, double and invalid free; uses randomised, bag-based allocation, so memory overhead and Linux x86-64 only; make SSE2RNG=1 uses an SSE2 random number generator, plain make uses rand(). Dual licence: GPL-2.0 or a commercial licence purchased from UT San Antonio.

## Maintenance

Abandoned since 2018-01-04 (6 commits, no releases, issues #2 and #3 open without replies); GPL-2.0 with a paid commercial licence from UTSA, so copying it into proprietary code needs that licence; the group's successor is Guarder.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** Peer-reviewed CCS 2017 paper (arXiv 1709.02746) would support B, but arxiv.org, ar5iv, deepai, the West Point repository copy and the co-author's site were all unreachable (getaddrinfo ENOTFOUND), so the numbers were seen only in WebSearch snippets of the paper; the repo carries no benchmark code or results. Held at C per the precedent for papers that could not be opened.
- **Verifier notes:** Repo checked on github.com: GPL-2.0 (README also offers commercial licensing via UTSA), 38 stars, 6 commits, last commit 2018-01-04, not archived, not a fork; maintenance corrected to abandoned (&gt;3 years). Benchmark URL (arXiv) is live but blocked from this session; a verifier with arXiv access could raise this to B after reading the evaluation section.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-76 (wave 1 book seed pass, 2026-10-24); enrichment (wave 1 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://github.com/utsasrg/freeguard>
  - <https://github.com/utsasrg/freeguard/commits>
  - <https://github.com/UTSASRG/Guarder>
- **Sources the enricher read:**
  - <https://github.com/UTSASRG/FreeGuard>
  - <https://raw.githubusercontent.com/UTSASRG/FreeGuard/master/README.md>
  - <https://raw.githubusercontent.com/UTSASRG/FreeGuard/master/Makefile>
  - <https://raw.githubusercontent.com/UTSASRG/FreeGuard/master/xdefines.hh>
  - <https://raw.githubusercontent.com/UTSASRG/FreeGuard/master/libfreeguard.cpp>
  - <https://raw.githubusercontent.com/UTSASRG/FreeGuard/master/bibopheap.hh>
  - <https://raw.githubusercontent.com/UTSASRG/FreeGuard/master/bigheap.hh>
  - <https://raw.githubusercontent.com/UTSASRG/FreeGuard/master/xthread.hh>
  - <https://raw.githubusercontent.com/UTSASRG/FreeGuard/master/xthread.cpp>
  - <https://raw.githubusercontent.com/UTSASRG/FreeGuard/master/real.cpp>
  - <https://raw.githubusercontent.com/UTSASRG/FreeGuard/master/mm.hh>
  - <https://raw.githubusercontent.com/UTSASRG/FreeGuard/master/threadstruct.hh>
  - <https://github.com/UTSASRG/FreeGuard/issues?q=is%3Aissue>
  - <https://github.com/UTSASRG/FreeGuard/issues/1>
  - <https://github.com/UTSASRG/FreeGuard/issues/2>
  - <https://github.com/UTSASRG/FreeGuard/issues/3>
  - WebSearch snippets of https://arxiv.org/pdf/1709.02746 (page not opened)
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/utsasrg/freeguard`) · [data/wave1/enrich/raw/github_com_utsasrg_freeguard.json](../../../data/wave1/enrich/raw/github_com_utsasrg_freeguard.json) (enrichment confidence 0.6)

</details>
