# Lockless Memory Allocator

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Allocators](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `GPL-3.0-or-later` · 🔴 abandoned

> Abandoned GPL x86 malloc replacement (per-thread slabs, lock-free remote frees); 1.15-1.48x faster than glibc malloc in Ruby tests.

| | |
|---|---|
| **Beats** | glibc malloc (ptmalloc, the built-in allocator of Ruby 2.6.5 and 2.5.1 on Linux); jemalloc and tcmalloc also run |
| **Claimed result** | SamSaffron/allocator_bench (Ruby 2.6.5, lockless 1.4 versus built-in glibc malloc): 8 threads 2.859 s versus 3.423 s (1.20x faster, derived from page data) with RSS 249,540 KB versus 186,336 KB (34% more, the highest RSS of every allocator in that run); 1 thread 2.874 s versus 3.296 s (1.15x faster, derived from page data) with RSS 164,468 KB versus 169,444 KB. Older runs: Ruby 2.5.1, lockless 1.4 3.568 s versus 4.928 s (1.38x, derived from page data); Ruby 2.3.3, lockless 1.3 3.689 s versus 5.463 s (1.48x, derived from page data). Lockless is mid-pack among the alternatives: at 8 threads tcmalloc 2.5 (2.764 s), tcmalloc 2.0 (2.797 s), rpmalloc (2.824 s) and jemalloc 5.2.0 (2.837 s) are faster and jemalloc 5.2.1 is within 2% (2.922 s); at 1 thread tcmalloc 2.6.3 (2.526 s) and several other tcmalloc/jemalloc versions are faster. The vendor's own page (blocked, snippet only) compares against eglibc 2.11, nedmalloc 1.06, hoard 3.8, jemalloc 2.2.1 and tcmalloc 1.7 with the t-test1 benchmark. |
| **Workload** | Third-party Ruby allocation stress script (12 million small string allocations with 600,000 retained and periodic large allocations up to 100 KB), run with LD_PRELOAD of each allocator, wall seconds and peak RSS, for 1 and 8 threads. |
| **Metric** | throughput |
| **Adoption** | benchmark repo (allocator_bench) has 56 stars; no stars figure for the vendor site |
| **Links** | [repository](https://locklessinc.com/) · [benchmark](https://raw.githubusercontent.com/SamSaffron/allocator_bench/HEAD/README.md) |

## Verdict

SamSaffron/allocator_bench preloads each allocator into a Ruby 2.6.5 process on an unnamed x86-64 Arch Linux machine (no CPU, compiler or flags stated) that makes 12 million small string allocations, retains 600,000 and makes periodic large allocations up to 100 KB. Single runs: lockless 1.4 took 2.86 s against 3.42 s for glibc malloc with 8 GVL-serialised threads (1.20x) and 2.87 s against 3.30 s with 1 thread (1.15x), ranking 10th and 13th of 37 configurations. Earlier Ruby 2.5.1 and 2.3.3 runs on another machine had it fastest of all (1.38x and 1.48x over glibc, derived from page data).

## Use it when

- A quick LD_PRELOAD experiment on x86-64 Linux for a malloc-bound program that allocates mostly small objects (512 B or less), where extra RSS is acceptable.
- Older Ruby interpreters: in SamSaffron/allocator_bench it was the fastest of every allocator tested on Ruby 2.3.3 (lockless 1.3, 1.48x over glibc) and Ruby 2.5.1 (lockless 1.4, 1.38x).
- Reproducing 2010-2013 allocator studies that name it as a contender, such as Percona's 2012 MySQL tests (best throughput group with jemalloc 3.0 and tcmalloc, search snippet only) or the vendor's t-test1 page.
- GPL-compatible projects that want one readable C file showing per-thread slabs, a B-tree free-space index and lock-free remote-free queues.

## Skip it when

- Memory-constrained services. In the 8-thread allocator_bench run its end-of-run RSS was 249,540 KB, against 186,336 KB for glibc (+34%) and 135,780 KB for glibc with MALLOC_ARENA_MAX=2 (+84%); only rpmalloc (291,428 KB) used more of the 37 configurations, so the record's 'highest RSS of every allocator' is wrong. Percona's 2012 MySQL test reports mysqld RSS growing by more than 5 GB (search snippet only).
- Anything other than x86/x86-64 on Linux or Windows. It uses x86 inline asm (bsf/bsr, xchg, rdtsc, rep;nop, mfence), Linux futexes and the real sbrk, and compiler.h has no macOS or ARM path.
- Closed-source distribution without buying the vendor's commercial licence: the code is GPL-3.0-or-later.
- Security-sensitive or hostile-input processes. Free-list pointers sit unprotected inside freed slab blocks, double-free detection exists only in a DEBUG_ALLOC build, and the vendor's own install page (search snippet) says it is designed for speed, not security.
- New code generally: unmaintained since about 2012. In the same 8-thread run it ranked 10th of 37 by time: tcmalloc 2.5, 2.6.2, 2.0, 2.6.1, 2.7, 2.4 and 2.6, rpmalloc and jemalloc 5.2.0 were all faster, and tcmalloc 2.5 used about 55% of its RSS. In the 1-thread run it ranked 13th, behind 12 tcmalloc and jemalloc versions.

## How it is fast

Each thread owns a heap (an initial-exec TLS 'atls' block), so the common path takes no lock. Requests up to 512 B come from per-thread 128 KiB slabs in 33 size classes of 16 bytes, served by a bump pointer and then an intrusive free list. Requests up to 128 MiB come from 64 bitmask-indexed fast lists (bins found with bsf) backed by a per-thread B-tree of free extents. A free from a non-owning thread is pushed with xchg onto the owner's lock-free queue (hazard-pointer protected) instead of taking a lock, and anything larger goes straight to mmap, with mremap for realloc.

## Compared with alternatives

Rarely. gperftools TCMalloc and jemalloc matched or beat it on the same Ruby benchmark at 8 threads with 55-65% of its RSS, and are maintained, permissively licensed and portable; rpmalloc was slightly faster but used even more RSS. Pick lockless only on old x86 Linux stacks where it already measured fastest (Ruby 2.3/2.5-era runs) and where GPL and higher memory use are acceptable.

## Integration

| | |
|---|---|
| **Form** | shared lib (LD_PRELOAD libllalloc.so), static lib (libllalloc.a) or source-drop (ll_alloc.c plus headers) |
| **Dependencies** | pthreads and Linux kernel headers (linux/futex.h); on Windows, mingw-w64 to compile ll_alloc.c plus MSVC for win_stub.cc |
| **Minimum toolchain** | GNU C99 compiler with GNU inline asm and asm goto (makefile: gcc -std=gnu99 -O3) |
| **Platforms** | x86 and x86-64 only; Linux and Windows (no macOS build path, no ARM) |
| **Thread safety** | Thread-safe. Heaps are per thread, cross-thread frees go through lock-free queues with hazard pointers, global slab lists use futex mutexes, and pthread_atfork handlers stabilise locks across fork(). A dead thread's heap is reused by the next new thread or merged into another heap. |
| **Drop-in for the baseline** | partial: a symbol-level drop-in for glibc malloc via LD_PRELOAD on x86 Linux, but mallopt() ignores every parameter, malloc_trim() ignores its pad, and glibc tunables such as MALLOC_ARENA_MAX have no effect |

## Gotchas

- Harness flaws in the evidence (SamSaffron/allocator_bench stress_mem.rb and test_all.rb). The 'mem' column is the RSS read with ps after the threads join, an end-of-run value, not peak RSS. Retained-string sizes use the unseeded global Random.rand, while the other sizes use a seeded RAND shared by all threads, so the workload is not identical from run to run. Every allocator ran once in a fixed order. In the 1-thread table, near-identical tcmalloc versions differ by up to 14.5% (2.1 at 3.199 s, 2.2 at 2.793 s), the same size as lockless's 15% margin over glibc. The 8 'threads' are Ruby threads serialised by the GVL, so the run never exercises concurrent allocation.
- Cross-thread frees are queued to the owning thread and reclaimed only when that thread drains its queue. A slab goes back to the OS (madvise MADV_DONTNEED) only when all 128 KiB of it are free, and the fork child handler deliberately leaks the other threads' heaps (source comment). Producer/consumer patterns, and GC sweeps that free other threads' objects, are plausible causes of its high RSS; neither source measured the cause.
- Small objects come from slabs grown with the real process break (sbrk), and free() recognises them by address range alone, with no header check. Once sbrk fails, a permanent sbrk_oom flag routes everything through the slower B-tree path.
- The GitHub mirror read here (jl2922/lockless_allocator, a 2017 'pull from lockless website') has a makefile that builds libllalloc.so.1.3, while the benchmark preloaded libllalloc.so.1.4 from the vendor download, so the mirror may not be byte-identical to the measured build. The Windows DLL variant overwrites CRT malloc/free entry points with 5-byte JMP patches, locating call sites by scanning bytes for a CALL opcode, which is fragile on newer CRTs.

## Known shortcomings

- Small win under the Ruby GVL in a third-party bench (1.15-1.48x vs glibc), no CPU or compiler, single runs; mid-pack (tcmalloc, rpmalloc and jemalloc 5.2.0 faster) with the highest RSS at 8 threads (+34%). GPL-3.0-or-later (via the jl2922/lockless_allocator mirror); vendor site blocked; code copyright 2009-2011, last update July 2012, abandoned.
- Enricher: in SamSaffron/allocator_bench lockless ranks 10th of 37 on time (tcmalloc 2.0-2.7, rpmalloc and jemalloc 5.2.0 faster) and second of 37 on 8-thread RSS (rpmalloc master higher), correcting the verifier's 'highest RSS' note; the 'mem' column is end-of-run RSS from ps, not peak, retained sizes use an unseeded Random.rand so the workload differs per run, single runs, and tcmalloc 2.1 vs 2.2 differ by 14.5% at 1 thread, the same size as lockless's 15% margin; threads are GVL-serialised. The jl2922 mirror builds libllalloc.so.1.3 while the bench preloaded .so.1.4. x86-only assembly, real sbrk slabs, mallopt/malloc_trim ignore their parameters, a fork child leaks other threads' heaps; the Windows DLL hot-patches the CRT. Percona 2012 (snippet) put it in the best throughput group with mysqld RSS +5 GB.

## Caveats and trade-offs

Evidence is one personal Ruby benchmark repo (SamSaffron/allocator_bench, public scripts, last commit 2020-07-06) with no CPU model, compiler or flags stated, so tier C; the results are single runs without variance. The workload is Ruby string allocation under the GVL, so the '8 threads' runs do not allocate truly in parallel and the allocator margin is small (1.15 to 1.48x); lockless also used the most memory of any allocator at 8 threads (34% more RSS than glibc). Many tcmalloc and jemalloc versions match or beat it. The vendor page https://locklessinc.com/benchmarks_allocator.shtml and the whole locklessinc.com domain (including mail.locklessinc.com) are egress-blocked, so vendor numbers (t-test1 versus eglibc 2.11, nedmalloc 1.06, hoard 3.8, jemalloc 2.2.1, tcmalloc 1.7) are known from search snippets only. Licence GPL-3.0-or-later is confirmed from the vendor README and ll_alloc.c header carried in the GitHub mirror jl2922/lockless_allocator ('GPL version 3 (or any later version)'; commercial licences offered by the vendor); the source copyright reads 2009-2011, and the vendor what's-new page (snippet only) lists the last allocator update on 23 Jul 2012 (aligned_alloc support), so the code is effectively abandoned. GPL means linking obliges source redistribution. [retier] Third-party SamSaffron/allocator_bench (Ruby, GVL-serialised threads, single runs, no CPU or compiler): 1.15-1.48x vs glibc but 10th of 37 on time (tcmalloc 2.0-2.7, rpmalloc and jemalloc 5.2.0 faster) and second-highest 8-thread RSS of 37 (rpmalloc master higher). The 'mem' column is end-of-run RSS from ps, not peak; retained sizes use an unseeded Random.rand so the workload differs per run; tcmalloc 2.1 vs 2.2 differ by 14.5% at 1 thread, the same size as lockless's margin. The bench preloaded libllalloc.so.1.4 while the jl2922/lockless_allocator mirror (2017, 0 stars) builds .so.1.3. x86-only assembly, real sbrk slabs, mallopt/malloc_trim ignore their parameters, a fork child leaks other threads' heaps. Vendor numbers (locklessinc.com, blocked) and Percona 2012 (best throughput group, mysqld RSS +5 GB) seen as snippets only. GPL-3.0-or-later; code copyright 2009-2011, last update July 2012, abandoned.

Preload or link replacement of malloc; the benchmark shows a larger memory footprint than glibc (about 34% higher RSS at 8 threads) and Percona's MySQL test is quoted in search snippets as showing over 5 GB RSS for mysqld. GPL (with a commercial licence sold by the vendor) rules out some uses.

## Maintenance

Abandoned: the source copyright is 2009-2011, the last vendor update was in July 2012 (snippet), and the only GitHub copy is a 2017 two-commit mirror with 0 stars. It is GPL-3.0-or-later (commercial licence from the vendor) and small enough to vendor, but x86-only and not advisable for new production use.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The SamSaffron/allocator_bench README shows lockless 1.4 against the built-in glibc malloc with public scripts (stress_mem.rb, test_all.rb, LD_PRELOAD per allocator), but no CPU model, compiler or flags, single unrepeated runs, and a small personal repo (56 stars) rather than a well-known suite, so it falls short of A and of a B-grade independent suite; the vendor's own benchmark page is first-party and was egress-blocked.
- **Verifier notes:** All README numbers match the page; I added the Ruby 2.3.3 row and the fact that lockless is mid-pack (several tcmalloc versions, rpmalloc and jemalloc 5.2.0 are faster) and has the highest 8-thread RSS. Licence GPL-3.0-or-later now confirmed via the jl2922/lockless_allocator mirror; maintenance set to abandoned from the 2009-2011 source copyright and a what's-new snippet (last allocator update July 2012). Shortcomings: small Ruby-dominated margin, GVL-serialised threads, no hardware/compiler, single runs, vendor page blocked.
- **Fields the verifier corrected:** `claimed_speedup`, `maintenance_status`, `caveats`
- **Shortcomings recorded by:** third-party Ruby bench (verifier); enricher harness reading
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/SamSaffron/allocator_bench/HEAD/README.md>
  - <https://raw.githubusercontent.com/SamSaffron/allocator_bench/HEAD/test_all.rb>
  - <https://raw.githubusercontent.com/SamSaffron/allocator_bench/HEAD/stress_mem.rb>
  - <https://raw.githubusercontent.com/SamSaffron/allocator_bench/HEAD/make_jemallocs.rb>
  - <https://github.com/SamSaffron/allocator_bench>
  - <https://github.com/SamSaffron/allocator_bench/commits>
  - <https://github.com/jl2922/lockless_allocator>
  - <https://raw.githubusercontent.com/jl2922/lockless_allocator/HEAD/README.txt>
  - <https://raw.githubusercontent.com/jl2922/lockless_allocator/HEAD/ll_alloc.c>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/SamSaffron/allocator_bench/HEAD/README.md>
  - <https://raw.githubusercontent.com/SamSaffron/allocator_bench/HEAD/test_all.rb>
  - <https://raw.githubusercontent.com/SamSaffron/allocator_bench/HEAD/stress_mem.rb>
  - <https://raw.githubusercontent.com/SamSaffron/allocator_bench/HEAD/make_jemallocs.rb>
  - <https://github.com/SamSaffron/allocator_bench>
  - <https://github.com/SamSaffron/allocator_bench/commits>
  - <https://github.com/jl2922/lockless_allocator>
  - <https://github.com/jl2922/lockless_allocator/commits>
  - <https://raw.githubusercontent.com/jl2922/lockless_allocator/HEAD/README.txt>
  - <https://raw.githubusercontent.com/jl2922/lockless_allocator/HEAD/ll_alloc.c>
  - <https://raw.githubusercontent.com/jl2922/lockless_allocator/HEAD/makefile>
  - <https://raw.githubusercontent.com/jl2922/lockless_allocator/HEAD/ll_asm.h>
  - <https://raw.githubusercontent.com/jl2922/lockless_allocator/HEAD/gcc.h>
  - <https://raw.githubusercontent.com/jl2922/lockless_allocator/HEAD/compiler.h>
  - <https://raw.githubusercontent.com/mjansson/rpmalloc/HEAD/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/mjansson/rpmalloc/HEAD/README.md>
  - https://locklessinc.com/benchmarks_allocator.shtml (EGRESS_BLOCKED; search snippet only)
  - https://www.percona.com/blog/2012/07/05/impact-of-memory-allocators-on-mysql-performance/ (EGRESS_BLOCKED; search snippet only)
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://locklessinc.com`) · [data/wave1/enrich/raw/locklessinc_com.json](../../../data/wave1/enrich/raw/locklessinc_com.json) (enrichment confidence 0.7)

</details>
