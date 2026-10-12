# GHC Haskell lightweight threads (skynet 1M-spawn benchmark vs pthread/std::thread)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Concurrency runtimes](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Haskell` · `BSD-3-Clause` · 🟢 active

> GHC sparks and green threads: skynet spawn cost 0.05-0.06 us per unit versus 52-73 us per C++ OS thread.

| | |
|---|---|
| **Beats** | pthread_create and std::thread (C/C++ OS threads, 8 kB pthread stacks) running the skynet recursive spawn-and-sum benchmark |
| **Claimed result** | Haskell (stack-1.4.0/ghc-8.0.1): 0.05-0.06 us per unit (average over 1,000,000) versus pthread 54-73 us, std::thread 52-73 us and std::async 106-122 us per thread (average over 10,000, because 1,000,000 OS threads exhausted resources): about 870x-1,460x lower per-unit cost (derived from page data; sizes differ). The same page shows Boost.Fiber (C++, 16C/32T, work stealing, tcmalloc) at 0.05-0.09 us per fiber, so C++ user-space fibers match the Haskell row. |
| **Workload** | skynet microbenchmark: a root unit spawns 10 children, each spawns 10 more, down to 1,000,000 leaves that return their ordinal; sums flow back up; time per spawned unit (GHC thread versus OS thread). |
| **Metric** | latency |
| **Hardware** | dual Intel Xeon E5-2620 v4 2.2 GHz, 16C/32T, 64 GB RAM, Linux x86_64 |
| **Compiler and flags** | C++ side (page): gcc-6.3.1, Boost.Build variant=release optimization=speed (-O3), pthreads created with 8 kB stacks, std::thread with the system default 1-2 MB stacks, glibc malloc or tcmalloc (-ltcmalloc). Haskell side (page): stack-1.4.0 / ghc-8.0.1 only. The skynet repo's haskell/skynet.cabal sets ghc-options -O2 -threaded -rtsopts and its README runs 'stack exec skynet +RTS -N', but the Boost page does not say which Haskell variant or RTS options it used. |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | not stated |
| **Why it wins** | Implied by the page rather than argued: GHC threads are runtime-scheduled green threads, pthreads are OS threads. No explicit mechanism is given. |
| **Adoption** | 3.3k stars (github.com/ghc/ghc is a read-only mirror of gitlab.haskell.org/ghc/ghc, which was not opened) |
| **Last commit** | 2026-10-11 |
| **Links** | [repository](https://github.com/ghc/ghc) · [benchmark](https://github.com/boostorg/fiber/blob/develop/doc/performance.qbk) |

## Verdict

The Boost.Fiber performance page (gcc-6.3.1 release/speed for the C++ side, dual Xeon E5-2620 v4, 16C/32T, Linux, 2017-era toolchains) lists Haskell stack-1.4.0/ghc-8.0.1 at 0.05-0.06 us per unit averaged over 1,000,000 leaves against pthread 54-73 us, std::thread (libstdc++) 52-73 us and std::async 106-122 us per thread averaged over 10,000 leaves, about 870x-1,460x (derived from page data), while Boost.Fiber's work-stealing scheduler shows 0.05-0.09 us. The Haskell build flags, RTS options and variant are unstated, the sizes differ, and the likely Haskell variant creates sparks rather than threads.

## Use it when

- You already write Haskell and have a recursive, pure divide-and-conquer computation: parMap rpar or Control.Parallel.Strategies spreads it over all cores with almost no per-task cost.
- A Haskell server or crawler that wants one forkIO thread per connection or request, with hundreds of thousands alive at once, synchronised through MVar, Chan or STM.
- Comparing language runtimes for massive task counts: GHC's spark and forkIO costs sit with Go, Erlang and Boost.Fiber, not with OS threads.
- Multicore runs where the binary is linked with -threaded and started with +RTS -N (without it the program runs on one capability).

## Skip it when

- Your code base is C++: the same Boost page shows Boost.Fiber (work stealing, tcmalloc, 16C/32T) at 0.05-0.09 us per fiber, matching the Haskell row, so the gap is green threads against kernel threads, not Haskell against C++.
- As evidence that Haskell code generation beats C++: the C++ rows create about 11,110 kernel threads and pass every value through a mutex and condition-variable channel, while the likely Haskell variant creates sparks without stacks or channels.
- Hard latency budgets: thread stacks and all data live on a garbage-collected heap, and the measured per-unit numbers say nothing about pause times.
- Work dominated by foreign calls: only calls not marked unsafe let other Haskell threads keep running, and parallel execution needs the -threaded RTS (GHC user guide, using-concurrent).
- Very small tasks via sparks: sparks that are already evaluated, unreferenced or beyond the pool size are discarded, so speedups depend on granularity and are not guaranteed.

## How it is fast

A forkIO thread starts with a 1 kB stack that lives on the garbage-collected heap and grows in 32 kB chunks (RTS defaults -ki 1k, -kc 32k), so creating one costs a heap allocation rather than an mmap'd stack plus a clone() system call. The skynet Haskell variant that matches the Boost row's magnitude (Parallel.hs, parMap rpar) does not create threads at all: rpar pushes a pointer to the unevaluated child onto a per-capability work-stealing deque (newSpark in rts/Sparks.c), idle capabilities steal it, and a spark nobody steals is simply evaluated by its parent. That is the same work-stealing idea as Boost.Fiber's work_stealing scheduler, which reaches 0.05-0.09 us per fiber on the same page.

## Compared with alternatives

Pick this entry when the question is per-task spawn cost at million-task scale for fine-grained pure parallelism in Haskell; the Erlang/OTP and Go thread-ring siblings measure message passing against a 503-pthread Boost.Asio program, and the Tokio 1M-tasks sibling is the fairer C++ comparison because its baselines (Asio C++20 coroutines, concurrencpp) are user-space tasks too.

## Integration

| | |
|---|---|
| **Form** | compiler toolchain and runtime (GHC); forkIO and MVar in base, parMap/rpar in the parallel package |
| **Dependencies** | skynet harness: base, async, criterion, parallel, stm, time, unagi-chan 0.4 (haskell/skynet.cabal); the measured technique itself needs only base plus parallel |
| **Minimum toolchain** | GHC with -threaded for +RTS -N; skynet's stack.yaml pins resolver lts-5.1 and its README names GHC 7.10.3; the Boost row used stack-1.4.0/ghc-8.0.1 |
| **Platforms** | measured on x86-64 Linux (dual Xeon E5-2620 v4); other platforms not checked this session |
| **Thread safety** | forkIO threads share one heap and synchronise through MVar, Chan or STM; the Parallel variant is pure code and needs no synchronisation |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw in the C++ baseline: boostorg/fiber performance/thread/skynet_pthread.cpp calls pthread_attr_setstacksize(&tattr, 8\*1024), which glibc rejects with EINVAL because 8 kB is below PTHREAD_STACK_MIN (16384 on Linux; check_stacksize_attr in nptl), and its error branches construct std::runtime_error without throwing it. The pthreads therefore ran with the default glibc stack, not the 8 kB the page states, which fits the near-identical pthread (54-73 us) and std::thread (52-73 us) rows; neither OS-thread port checks the result (the fiber port does) and the attr is never destroyed.
- Variant and work mismatch: Boost's 0.05-0.06 us times 1,000,000 is 50-60 ms, the order of skynet's Parallel variant (0.017 s on an i7-4930K per Main.hs comments), not the forkIO+MVar variant (1.7 s). Parallel.hs computes a pure tree sum with parMap rpar; newSpark pushes onto a bounded per-capability deque (maxLocalSparks default 4096 in rts/RtsFlags.c, extra sparks counted as overflowed and dropped), and unstolen sparks are evaluated by the parent, so many of the 1,111,111 'units' never become threads.
- Possible measurement artefact (not compiled or run here): in Parallel.hs 'let !result = skynet 6 0' has no free variables, so -O2 full laziness can float it into a top-level constant; criterion's whnfIO then repeats run and only the first iteration would compute the sum. Neither the Boost page nor the repo says which output (criterion mean or the printed 'Result ... in' line) was taken.
- Sizes and divisors differ: the Haskell row averages over 1,000,000 leaves, the OS-thread rows over 10,000 leaves (11,111 threads actually created) because 1,000,000 kernel threads exhausted resources; the Haskell RTS options (-N value) and GHC flags for the Boost run are unstated, and the page's single-threaded fiber row (1.69-1.79 us) shows how much the 32 hardware threads matter.

## Known shortcomings

- Numbers from boostorg/fiber performance.qbk (0.05-0.06 us vs pthread 54-73 us, about 870-1,460x derived) probably come from a parMap/rpar sparks variant rather than forkIO plus MVar, sizes differ (1M vs 10k), Haskell flags and variant unstated, and Boost.Fiber C++ matches it on the same page; the baseline is OS threads, not an equivalent C++ fiber.
- Harness flaw: boostorg/fiber's skynet_pthread.cpp calls pthread_attr_setstacksize(8\*1024), which glibc rejects with EINVAL (PTHREAD_STACK_MIN 16384); the error branch builds a std::runtime_error without throwing it, so the pthreads ran default stacks, not the 8 kB the page says (which fits the pthread row matching std::thread); the OS-thread ports never check the result. Parallel.hs uses parMap rpar sparks (a bounded 4096-entry deque, unstolen sparks run by the parent), not threads; a possible -O2 CAF float of skynet 6 0 under criterion repeat is unverified (no GHC here). Boost.Fiber matches the Haskell row.

## Caveats and trade-offs

Variant mismatch (main finding): atemerev/skynet haskell/src/Main.hs runs five implementations under criterion (Parallel, MVar, Chan, TBQueue, Unagi); its own comments give, on an i7-4930K with +RTS -N6, Parallel 0.017 s and MVar 1.7 s per 1,000,000-leaf run. The Boost row (0.05-0.06 us x 1,000,000 = 50-60 ms) matches the Parallel variant's order of magnitude, not the forkIO+MVar one (inference; the page does not name the variant). Parallel.hs computes a pure tree sum with parMap rpar: it creates sparks (work-stealing pool entries the parent may evaluate itself), no forkIO threads and no channel messages, whereas the C++ port (boostorg/fiber performance/thread/skynet_pthread.cpp) creates about 11,110 detached pthreads for its 10,000 leaves and passes every value through a mutex/condition-variable buffered_channel. So the comparison is sparks (or green threads) against kernel threads, not the same work, and the win is the runtime's, not Haskell codegen's. Scale differs (1,000,000 units for Haskell, 10,000 for pthread/std::thread). The skynet README's own Haskell (GHC 7.10.3) results range from 41-44 ms (i7-4771, Ubuntu) to 2820-6181 ms (Windows, OS X), consistent with different variants being run. Toolchains date from 2017 (go1.8.1, ghc-8.0.1, erts-8.3, gcc-6.3.1). The baseline is OS threads, not the idiomatic C++ answer for massive concurrency; Boost.Fiber on the same page reaches 0.05-0.09 us. No Haskell benchmark code lives in boostorg/fiber (performance/ holds only fiber/ and thread/). The repo_url is the GHC mirror (gitlab.haskell.org/ghc/ghc is upstream); the skynet sources are MIT, last commit 2023-11-10. GHC's licence file is the Glasgow Haskell Compiler License (BSD-3-Clause text). [retier] boostorg/fiber's skynet_pthread.cpp asks for 8 kB stacks, which glibc rejects (PTHREAD_STACK_MIN 16384) and the error is never thrown, so the pthreads ran default stacks (which fits the pthread row matching std::thread). Parallel.hs uses parMap rpar sparks (bounded 4096-entry deque, unstolen sparks run by the parent), not threads; a possible -O2 CAF float under criterion repeat is unverified. Boost.Fiber matches the Haskell row.

GHC threads are heap-allocated stack chunks scheduled by the GHC runtime (garbage-collected, optional -threaded and -N). Foreign calls and unsafe FFI interact with the scheduler differently from C.

## Maintenance

GHC is actively developed upstream at gitlab.haskell.org (the github.com/ghc/ghc read-only mirror shows 3.3k stars and 69,753 commits) under a BSD-3-style licence; the skynet Haskell harness (MIT) has not changed since April 2016 and the Boost numbers date from 2017, so the entry is tier C evidence for a runtime property, not a copyable component.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification B, tier now C.
- **Tier reason:** boostorg/fiber doc/performance.qbk (Boost.Fiber author, independent of GHC) shows Haskell 0.05-0.06 us per unit at 1,000,000 units against pthread 54-73 us and std::thread 52-73 us at 10,000 threads on a stated Xeon E5-2620 v4 with gcc-6.3.1 release/speed, but the Haskell build flags, RTS options and which of the five skynet Haskell variants ran are unstated, the gain is \~870-1,460x (cap at C for &gt;50x with unstated flags), and the two sides run at different sizes and very likely different algorithms. Not A (no Haskell flags), not B (unequal workloads, unknown variant).
- **Verifier notes:** Downgrade B to C: numbers are on the Boost.Fiber page, but the Haskell row very likely measured the parMap/rpar spark variant (no threads, no channels) against one detached pthread per unit, at different sizes (1M vs 10k) and with Haskell flags unstated. Shortcomings to record: different algorithm (sparks vs kernel threads), unequal workload sizes, Haskell variant/flags/RTS options unstated, 2017 toolchains, C++ fibers on the same page match Haskell so no language-level win. baseline_stdlib set to libstdc++ (gcc-6.3.1 on Linux runs std::thread/std::async from libstdc++).
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`, `baseline_stdlib`
- **Shortcomings recorded by:** verifier batch-01 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/boostorg/fiber/develop/doc/performance.qbk>
  - <https://raw.githubusercontent.com/boostorg/fiber/develop/performance/thread/skynet_pthread.cpp>
  - <https://github.com/boostorg/fiber/tree/develop/performance>
  - <https://github.com/atemerev/skynet>
  - <https://github.com/atemerev/skynet/commits/master>
  - <https://raw.githubusercontent.com/atemerev/skynet/master/README.md>
  - <https://raw.githubusercontent.com/atemerev/skynet/master/haskell/src/Main.hs>
  - <https://raw.githubusercontent.com/atemerev/skynet/master/haskell/src/Parallel.hs>
  - <https://raw.githubusercontent.com/atemerev/skynet/master/haskell/src/MVar.hs>
  - <https://raw.githubusercontent.com/atemerev/skynet/master/haskell/src/Chan.hs>
  - <https://raw.githubusercontent.com/atemerev/skynet/master/haskell/skynet.cabal>
  - <https://raw.githubusercontent.com/atemerev/skynet/master/haskell/stack.yaml>
  - <https://github.com/ghc/ghc>
  - <https://github.com/ghc/ghc/commits/master>
  - <https://raw.githubusercontent.com/ghc/ghc/master/LICENSE>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/boostorg/fiber/develop/doc/performance.qbk>
  - <https://raw.githubusercontent.com/boostorg/fiber/develop/performance/thread/skynet_pthread.cpp>
  - <https://raw.githubusercontent.com/boostorg/fiber/develop/performance/thread/skynet_std.cpp>
  - <https://raw.githubusercontent.com/boostorg/fiber/develop/performance/thread/skynet_async.cpp>
  - <https://raw.githubusercontent.com/boostorg/fiber/develop/performance/thread/buffered_channel.hpp>
  - <https://raw.githubusercontent.com/boostorg/fiber/develop/performance/fiber/skynet_stealing_async.cpp>
  - <https://raw.githubusercontent.com/atemerev/skynet/master/README.md>
  - <https://raw.githubusercontent.com/atemerev/skynet/master/haskell/src/Main.hs>
  - <https://raw.githubusercontent.com/atemerev/skynet/master/haskell/src/Parallel.hs>
  - <https://raw.githubusercontent.com/atemerev/skynet/master/haskell/src/MVar.hs>
  - <https://raw.githubusercontent.com/atemerev/skynet/master/haskell/src/Chan.hs>
  - <https://raw.githubusercontent.com/atemerev/skynet/master/haskell/skynet.cabal>
  - <https://raw.githubusercontent.com/atemerev/skynet/master/haskell/stack.yaml>
  - <https://github.com/atemerev/skynet/commits/master/haskell>
  - <https://github.com/ghc/ghc>
  - <https://raw.githubusercontent.com/ghc/ghc/master/docs/users_guide/using-concurrent.rst>
  - <https://raw.githubusercontent.com/ghc/ghc/master/docs/users_guide/runtime_control.rst>
  - <https://raw.githubusercontent.com/ghc/ghc/master/rts/Sparks.c>
  - <https://raw.githubusercontent.com/ghc/ghc/master/rts/RtsFlags.c>
  - <https://raw.githubusercontent.com/bminor/glibc/master/nptl/pthread_attr_setstacksize.c>
  - <https://raw.githubusercontent.com/bminor/glibc/master/nptl/pthread_attr_setstack.c>
  - <https://raw.githubusercontent.com/bminor/glibc/master/sysdeps/nptl/pthreadP.h>
  - <https://raw.githubusercontent.com/bminor/glibc/master/sysdeps/unix/sysv/linux/bits/pthread_stack_min.h>
  - <https://raw.githubusercontent.com/bminor/glibc/master/sysdeps/unix/sysv/linux/bits/local_lim.h>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:haskell/atemerev/skynet#skynet`) · [data/wave14/enrich/raw/lang_haskell_atemerev_skynet_skynet.json](../../../data/wave14/enrich/raw/lang_haskell_atemerev_skynet_skynet.json) (enrichment confidence 0.6)

</details>
