# libcsp

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Coroutines and fibers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🔴 abandoned

> Go-style M:N process scheduler for C (GCC plugin, x86-64 Linux); about 10x faster than Go 1.14 at spawning short-lived tasks.

| | |
|---|---|
| **Beats** | Go goroutines (Go 1.14, sync.WaitGroup); pthreads also run at a reduced size |
| **Claimed result** | libcsp versus Go seconds per round: 3.047 versus 31.145 on 1 core (10.2x), 0.847 versus 11.172 on 4 cores (13.2x), 0.726 versus 8.030 on 8 cores (11.1x) (ratios derived from page data). Memory of the machine: 2.3% versus 31.2% at 8 cores. The docs say libcsp is 'at least 10 times faster and use less memory than golang'. Repo description: 'A concurrency C library 10x faster than Golang'. |
| **Workload** | Divide-and-conquer sum(0, 10,000,000) spawning two lightweight processes per node (about 20 million short-lived processes), 10 rounds, seconds per round and memory share, for 1 to 8 CPU cores. |
| **Metric** | throughput |
| **Hardware** | 8 CPU cores, 8192 MB memory, Linux 4.15.0-88-generic x86_64 (ubuntu-bionic); CPU model not stated |
| **Compiler and flags** | GCC 8.3.0 with -Wall -O3 and the libcsp gcc plugin (cspcli analyze); Go v1.14 'go build' defaults |
| **Adoption** | 1.3k stars |
| **Last commit** | 2023-06-30 |
| **Links** | [repository](https://github.com/yann-shi/libcsp) · [benchmark](https://raw.githubusercontent.com/shiyanhui/libcsp/HEAD/docs/content/performance/_index.md) |

## Verdict

The author's docs page times sum(0, 10^7) with two child processes per node (about 2 x 10^7 spawns per round, 10 rounds) on an unnamed 8-core, 8 GB Ubuntu 18.04 machine, GCC 8.3.0 -O3 with the libcsp plugin versus Go 1.14 defaults: 3.05 s versus 31.1 s per round on 1 core and 0.73 s versus 8.03 s on 8 cores, about 10-13x. It measures task create-schedule-destroy cost under each runtime's scheduling order, not application throughput.

## Use it when

- Linux x86-64 C code built with GCC 8 or later that spawns millions of short-lived tasks, such as recursive divide-and-conquer or fan-out/fan-in pipelines.
- Workloads where per-task memory matters: compile-time stack sizing plus depth-first scheduling kept the benchmark at 0.2-2.3% of an 8 GB machine against Go's 28-31%.
- C network services that want goroutine-style blocking code over epoll (netpoll) and timers without writing callbacks.
- Experiments with compile-time stack analysis as an alternative to growable or fixed-size coroutine stacks.

## Skip it when

- Any compiler other than GCC, any language other than C, or any target other than x86-64 Linux: the install docs list only that combination.
- Code with recursion inside a process, VLAs or alloca, function pointers, or heavy calls into external libraries: frames the plugin cannot see (dynamic frames, functions not compiled with it, such as libc) are charged a 2 KB default, and there are no guard pages, so an overflow silently corrupts a neighbouring process.
- Programs that need select over several channels: open issue #14 asks for it with no reply; and block() can hang main (open issue #16, Sep 2022).
- Production use needing support: single author, last code release 0.0.2 (January 2021), commits since then are docs and typo fixes, last commit 2023-06-30.
- Processes that share an address space with other code reserving large fixed regions: the allocator mmaps with MAP_FIXED at hard-coded addresses ((core+1) x 64 GiB), which replaces any existing mapping there (not documented).

## How it is fast

Stacks are sized at compile time: the GCC plugin records every function's frame size and the call graph, cspcli computes each process's worst-case stack and rounds it to 4 KiB pages, so spawning is a page-span allocation from a per-core lock-free heap plus a hand-written assembly context switch. New processes are pushed to the front of the core's local run queue and popped from the front (LIFO), so divide-and-conquer work runs depth-first and only about tree-depth processes per core are alive at once; idle cores take half of a busy core's queue.

## Compared with alternatives

Pick libcsp over libdill or libmill when you need the scheduler to use several cores and can live with GCC on x86-64 Linux; libdill and libmill are single-threaded but portable and measured against Go too (libdill create+terminate 44 ns vs Go 237 ns). For plain fork-join parallelism Coros or oneTBB-style work stealing is the more standard choice, and minicoro or libaco fit when you only need fast single-threaded context switches.

## Integration

| | |
|---|---|
| **Form** | shared lib (libcsp.so) plus a GCC plugin (libcspplugin.so) and the cspcli build tool; autotools install |
| **Dependencies** | GCC plugin development headers (gcc-N-plugin-dev or gcc-plugin-devel), pthreads; valgrind optional |
| **Minimum toolchain** | GCC 8+, C11 atomics; C only |
| **Platforms** | x86-64 Linux only |
| **Thread safety** | Multi-core M:N scheduler with one worker per configured core (set at build time with cspcli --cpu-cores); channels are lock-free and a mutex type is provided; blocking system calls must be wrapped in block() so the core is handed off. |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw (scheduling order, not just spawn cost): Go 1.14's `go` statement puts the new goroutine in runnext and kicks the previous one to the tail of a FIFO run queue (runtime/proc.go runqput), so the benchmark's left children queue up shallowest-first and the tree is expanded broadly; libcsp pushes and pops at the front of its run queue and runs the tree depth-first. Go's 28-31% memory (about 2.3-2.6 GB of 8 GB, consistent with roughly a million live goroutines at the 2 KB minimum stack, derived from page data) and part of its time come from this order, from sync.WaitGroup parking and from closures that escape to the heap and feed the GC; per spawn the run costs about 152 ns for libcsp versus 1.56 us for Go on 1 core (derived from page data), while libdill's own table puts Go goroutine create+terminate near 237 ns on other hardware. Neither side uses a sequential cutoff, and a cutoff version was not measured.
- The benchmark is otherwise honest: both programs print the correct sum 50000005000000, so the work is not optimised away, and both scale similarly from 1 to 8 cores (libcsp 4.2x, Go 3.9x, derived from page data).
- Stack sizes come from the build: every source file with processes must go through the plugin, cspcli analyze must run before the final link, and the core count is baked into config.c, so a binary built for 4 cores uses at most 4 even on a larger machine.
- The allocator calls exit(EXIT_FAILURE) without a message when a core's 64 GiB heap range is exhausted or mmap fails, and csp_proc_new exits the program on allocation failure instead of returning an error.

## Known shortcomings

- Spawn-only microbenchmark (10.2x-13.2x) against untuned Go 1.14 goroutines with the CPU model missing; requires a GCC plugin. MIT LICENSE with ISC-style source headers. Last commit 2023-06-30, abandoned.
- Enricher: Go 1.14 puts each new goroutine in runnext and kicks the previous one to a FIFO queue, so the Go tree spreads broadly while libcsp's LIFO run queue runs depth-first; Go's 28-31% extra memory and part of its time come from that order plus WaitGroup parking and GC, not only spawn cost (152 ns vs 1.56 us per spawn, derived). MAP_FIXED at hard-coded addresses ((core+1) x 64 GiB), no stack guard pages, 2 KB default stack for functions the plugin cannot size. Repo moved to yann-shi/libcsp. Leads: glepnir/CspChan, libgoc (repo not found).

## Caveats and trade-offs

First-party benchmark with public code (benchmarks/sum_libcsp.c, sum_go.go, sum_thread.c and benchmarks/Makefile), but the CPU model is not stated; the environment is listed only as 8 cores, 8192 MB, Linux ubuntu-bionic 4.15.0-88-generic (the hostname and round memory size suggest a VM, not confirmed). The workload is a pure process-spawn microbenchmark (two child processes per node, about 20 million per round) with no cutoff, so it measures create-schedule-destroy overhead rather than real applications; the Go side allocates two closures and a WaitGroup per node that escape to the heap, so Go's GC and growable-stack costs are included, while libcsp's stacks are sized at compile time by its GCC plugin and 'cspcli analyze' (the memory column reflects that static sizing). Building needs the libcsp GCC plugin plus the cspcli analysis step with a fixed core count. Go 1.14 dates from 2020; no newer Go was tested. The pthread comparison could not run at the same size: sum_thread.c comments say MAX had to be cut to 10,000 (3.2 s per round) because 10^7 exceeds the Linux thread limit. LICENSE file is MIT while source headers carry ISC-style permission text (both OSI-permissive). Single author; last commit 2023-06-30, so abandoned.

Needs a GCC plugin plus the cspcli tool to analyse stack sizes at compile time, so stack use must be statically analysable; C only, GCC only; custom syntax (proc, sync, async macros); includes netpoll and timers.

## Maintenance

Abandoned (last commit 2023-06-30, last code change January 2021, version 0.0.2; the repository now lives under github.com/yann-shi/libcsp, the shiyanhui URL redirects there) but MIT-licensed and small; usable only where a GCC-plugin build on x86-64 Linux is acceptable.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party docs page with public benchmark code (benchmarks/sum_libcsp.c, benchmarks/sum_go.go, benchmarks/Makefile with CFLAGS -Wall -O3, GCC 8.3.0, Go 1.14) but the CPU model is not stated (only 8 cores, 8192 MB, Linux 4.15.0-88-generic), so not A.
- **Verifier notes:** All eight libcsp/Go timings and the memory column match the docs page (ratios 10.2x, 13.2x, 11.1x correctly derived). Metadata verified: 1.3k stars, MIT, last commit 2023-06-30 (abandoned). Shortcomings: CPU model missing, spawn-only microbenchmark versus untuned Go 1.14 code, GCC-plugin build requirement.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** first-party README (verifier); enricher code reading
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/shiyanhui/libcsp/HEAD/docs/content/performance/_index.md>
  - <https://raw.githubusercontent.com/shiyanhui/libcsp/HEAD/benchmarks/sum_libcsp.c>
  - <https://raw.githubusercontent.com/shiyanhui/libcsp/HEAD/benchmarks/sum_go.go>
  - <https://raw.githubusercontent.com/shiyanhui/libcsp/HEAD/benchmarks/sum_thread.c>
  - <https://raw.githubusercontent.com/shiyanhui/libcsp/HEAD/benchmarks/Makefile>
  - <https://raw.githubusercontent.com/shiyanhui/libcsp/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/shiyanhui/libcsp/HEAD/README.md>
  - <https://raw.githubusercontent.com/shiyanhui/libcsp/HEAD/src/sched.h>
  - <https://github.com/shiyanhui/libcsp>
  - <https://github.com/shiyanhui/libcsp/commits>
  - <https://github.com/shiyanhui/libcsp/tree/master/src>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/shiyanhui/libcsp/HEAD/README.md>
  - <https://raw.githubusercontent.com/shiyanhui/libcsp/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/shiyanhui/libcsp/HEAD/docs/content/performance/_index.md>
  - <https://raw.githubusercontent.com/shiyanhui/libcsp/HEAD/docs/content/_index.md>
  - <https://raw.githubusercontent.com/shiyanhui/libcsp/HEAD/docs/content/installation/_index.md>
  - <https://raw.githubusercontent.com/shiyanhui/libcsp/HEAD/docs/content/building/_index.md>
  - <https://raw.githubusercontent.com/shiyanhui/libcsp/HEAD/docs/content/tutorial/_index.md>
  - <https://raw.githubusercontent.com/shiyanhui/libcsp/HEAD/docs/content/api/_index.md>
  - <https://raw.githubusercontent.com/shiyanhui/libcsp/HEAD/benchmarks/sum_libcsp.c>
  - <https://raw.githubusercontent.com/shiyanhui/libcsp/HEAD/benchmarks/sum_go.go>
  - <https://raw.githubusercontent.com/shiyanhui/libcsp/HEAD/benchmarks/sum_thread.c>
  - <https://raw.githubusercontent.com/shiyanhui/libcsp/HEAD/benchmarks/Makefile>
  - <https://raw.githubusercontent.com/shiyanhui/libcsp/HEAD/src/sched.h>
  - <https://raw.githubusercontent.com/shiyanhui/libcsp/HEAD/src/sched.c>
  - <https://raw.githubusercontent.com/shiyanhui/libcsp/HEAD/src/proc.h>
  - <https://raw.githubusercontent.com/shiyanhui/libcsp/HEAD/src/proc.c>
  - <https://raw.githubusercontent.com/shiyanhui/libcsp/HEAD/src/runq.c>
  - <https://raw.githubusercontent.com/shiyanhui/libcsp/HEAD/src/mem.c>
  - <https://raw.githubusercontent.com/shiyanhui/libcsp/HEAD/src/core.c>
  - <https://raw.githubusercontent.com/shiyanhui/libcsp/HEAD/src/csp.h>
  - <https://raw.githubusercontent.com/shiyanhui/libcsp/HEAD/src/chan.h>
  - <https://raw.githubusercontent.com/shiyanhui/libcsp/HEAD/plugin/sa.hpp>
  - <https://raw.githubusercontent.com/golang/go/go1.14/src/runtime/proc.go>
  - <https://github.com/shiyanhui/libcsp>
  - <https://github.com/shiyanhui/libcsp/commits>
  - <https://github.com/shiyanhui/libcsp/tree/master/src>
  - <https://github.com/shiyanhui/libcsp/tree/master/plugin>
  - <https://github.com/shiyanhui/libcsp/tree/master/docs/content>
  - <https://github.com/shiyanhui/libcsp/issues?q=is%3Aissue>
  - <https://github.com/shiyanhui/libcsp/issues/4>
  - <https://github.com/shiyanhui/libcsp/issues/14>
  - <https://github.com/shiyanhui/libcsp/issues/16>
  - <https://github.com/shiyanhui/libcsp/issues/17>
  - WebSearch: libcsp "10x faster than Golang" concurrency C library (no independent benchmark found)
  - WebSearch (news.ycombinator.com): libcsp concurrency C library faster than golang (HN item 22797286 title only; thread blocked)
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/shiyanhui/libcsp`) · [data/wave1/enrich/raw/github_com_shiyanhui_libcsp.json](../../../data/wave1/enrich/raw/github_com_shiyanhui_libcsp.json) (enrichment confidence 0.75)

</details>
