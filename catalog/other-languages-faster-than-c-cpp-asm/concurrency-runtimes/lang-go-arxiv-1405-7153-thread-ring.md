# Go goroutines on thread-ring (SCOOP/Qs paper, arXiv 1405.7153) vs C++/TBB

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Concurrency runtimes](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Go` · `BSD-3-Clause` · 🟢 active

> Go goroutines passing a token round a 503-member ring, 2.4x faster than a C++ Boost.Asio program on 503 OS threads.

| | |
|---|---|
| **Beats** | The paper's 'C++/TBB' column; for thread-ring the authors' public code (scottgw/quicksilver benchmarks/concurrent/cxx/threadring/main.cpp) is not TBB but the Computer Language Benchmarks Game C++ program by The Anh Tran: 503 OS pthreads (4 KB stacks) all blocked in one boost::asio::io_service::run() queue, each token pass a post() that wakes an OS thread; built with g++ -O3 -std=c++11 -pthread -lboost_system. No fiber, coroutine or single-threaded C++ ring was measured. |
| **Claimed result** | Thread-ring on 32 cores (snippet only, paper Table 5): Go 13.98 s versus the paper's C++/TBB column 34.13 s, about 2.4x (derived from the snippet numbers); the C++ program is Boost.Asio over 503 OS threads. Erlang took 3.30 s in the same table. |
| **Workload** | thread-ring (Computer Language Benchmarks Game spec): 503 ring members pass a token 5,000,000 times (input in benchmarks/run_all.py); essentially single-threaded and bound by context-switch cost. Paper table reported for a 32-core machine (snippet). |
| **Metric** | latency |
| **Hardware** | 32 cores (CPU model not seen) |
| **Compiler and flags** | From the authors' Makefiles and run.sh in scottgw/quicksilver benchmarks/concurrent/\*/threadring: C++ g++ -O3 -std=c++11 -pthread -lboost_system; Go 'go build' defaults, run with GOMAXPROCS set to the worker count; Erlang erlc -W (plain BEAM, no +native) run as erl -smp enable -noshell +t 8192 +P &lt;n&gt; +ec +K true +hms 4 +hmbs 1; Haskell ghc --make -O2 -threaded -rtsopts. Input 5,000,000 token passes for every language. Compiler and runtime versions not stated in the repo (code dates from 2014). |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | not stated |
| **Same optimization level** | not stated |
| **Why it wins** | Inferred, not argued by the snippet: goroutines are user-space units multiplexed by the Go scheduler onto OS threads and a channel hand-off is cheaper than an OS-thread wake-up. Go's own 13.98 s is 4x slower than Erlang in the same table, so the ranking is scheduler-specific. |
| **Adoption** | 139.2k stars |
| **Last commit** | 2026-10-10 |
| **Links** | [repository](https://github.com/golang/go) · [benchmark](https://arxiv.org/pdf/1405.7153) |

## Verdict

WebSearch summaries of Table 5 in arXiv 1405.7153 give 13.98 s for Go and 34.13 s for the 'C++/TBB' column on thread-ring (503 members, 5,000,000 passes), about 2.4x. The C++ program is the Benchmarks Game Boost.Asio version over 503 pthreads, built with g++ -O3. Compiler and runtime versions, the CPU model and the effective GOMAXPROCS of the published run are not stated anywhere opened.

## Use it when

- Services built from thousands of mostly-blocked tasks that hand work to each other in sequence (pipelines, actor-like rings), where a C++ design would otherwise park one OS thread per task.
- Choosing a language for a new concurrent service when the C++ alternative under consideration is thread-per-task rather than coroutines or fibers.
- Message-passing code where cheap goroutine creation (503 here, millions in practice) matters more than peak single-thread speed.

## Skip it when

- As evidence that Go beats C++ in general: the paper's own geometric mean over its concurrent tasks ranks C++/TBB first (1.57 s) ahead of Go (1.82 s); thread-ring and condition are the stated exceptions because both are essentially single-threaded (search snippet).
- When a C++ fiber or coroutine runtime (Boost.Fiber, Boost.Context, C++20 coroutines) or a single-threaded loop is an option: none was measured, and those remove the OS-thread wake-up that the baseline pays on every pass.
- When you need the fastest runtime for this pattern: Erlang processes did the same ring in 3.30 s against Go's 13.98 s in the same table.
- Inside an existing C++ program: calling Go goes through cgo or a separate process, and Go brings a garbage collector and its own scheduler.

## How it is fast

A hand-off never leaves user space in the common case: Mutex.Unlock on a parked waiter calls the runtime semaphore release, which readies the waiting goroutine on the current P (runtime.ready puts it in the run queue), and Gosched puts the current goroutine on the global queue and runs the next one on the same OS thread. The C++ baseline instead posts each pass to one shared boost::asio::io_service queue; in Boost 1.55 every post() takes the io_service mutex and signals an idle OS thread's wakeup event (task_io_service::wake_one_thread_and_unlock), so each pass is a kernel-level wake-up and context switch among 503 pthreads. The win is M:N user-space scheduling against 1:1 OS threads, not code generation.

## Compared with alternatives

Pick this over the GHC skynet entry when the question is hand-off latency between long-lived tasks rather than spawn cost. Pick Erlang's thread-ring entry, from the same paper, if the fastest runtime for this pattern matters (3.30 s against Go's 13.98 s). Pick the luncliff Comparison-Go-CppTBB entry when the C++ alternative is a real TBB task scheduler, because this entry's 'TBB' column is Boost.Asio over OS threads.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | Go toolchain and runtime (no third-party packages; the benchmark uses only fmt, os, runtime, strconv, sync) |
| **Minimum toolchain** | Not stated by the paper or repo; code dates from 2014 (Go 1.2/1.3 era) and uses only APIs still present in current Go |
| **Platforms** | any platform Go supports |
| **Thread safety** | sync.Mutex is documented as not tied to a goroutine (one goroutine may lock, another unlock), which the benchmark relies on; Unlock synchronizes-before the next Lock per the Go memory model |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness asymmetry: run_all.py passes the worker count as \$2, and only the Go run.sh uses it (GOMAXPROCS=\$2). The C++ program ignores its second argument and always runs 503 OS threads on every core, and Erlang's run.sh sets no +S, so it uses all schedulers. The concurrent tasks run with worker_range = [4] at HEAD, and the search snippet ties the paper's '32 cores' label to Figure 18 (parallel tasks), so Table 5 may be GOMAXPROCS=4 rather than 32.
- The baseline's '4 KB stacks' never took effect on Linux: glibc's pthread_attr_setstack returns EINVAL below PTHREAD_STACK_MIN (check_stacksize_attr in glibc 2.19; 16384 bytes on x86-64), main.cpp ignores the return value, and the 503 threads were created with default-size stacks. This does not change the timing much, but the record's baseline description is wrong on this point.
- Each language was run once (range(0, 1)) and timed as wall clock around Popen, so process start and creating 503 pthreads count against C++. Erlang alone reports its own timer:tc figure, which excludes VM boot.
- Not reproducible as published against current Boost: main.cpp uses asio::io_service and io_service::post(), and boostorg/asio develop (Asio 1.38.2) has neither the io_service typedef nor an io_context::post member, so it needs a port to io_context and asio::post() before it builds.

## Known shortcomings

- Same paper (Go 13.98 s vs C++ 34.13 s, 2.4x) with the same baseline correction: the C++ side is the Boost.Asio thread-ring with 503 OS pthreads, so the win is goroutine mutex hand-off vs OS-thread futex wakes, not codegen; snippet only, compiler versions and CPU model unseen. Paper-access retier lead.
- Harness flaw: the worker count in run_all.py reaches only Go (GOMAXPROCS=\$2); C++ ignores it and always runs 503 OS threads, and Erlang sets no +S; the concurrent tasks run with worker_range=[4], and the snippet's '32 cores' label belongs to Figure 18 (parallel tasks), so the Table 5 configuration is uncertain. The C++ baseline's '4 KB stacks' were never applied (glibc pthread_attr_setstack returns EINVAL under PTHREAD_STACK_MIN 16384 and main.cpp ignores the return), and main.cpp no longer builds on Asio 1.38.2 (no io_service, no io_context::post). Per the snippet, the paper's geomean has C++/TBB 1.57 s beating Go's 1.82 s, so thread-ring is an exception; each language was run once.

## Caveats and trade-offs

Paper numbers seen only through WebSearch result summaries (Table 5 of arXiv 1405.7153, 'Efficient and Reasonable Object-Oriented Concurrency', West, Nanz and Meyer, published at ESEC/FSE 2015): thread-ring on 32 cores Go 13.98 s, C++/TBB 34.13 s, Erlang 3.30 s, SCOOP/Qs 5.82 s, Haskell 57.44 s; arxiv.org is blocked here, so the table, CPU model and compiler versions were not opened. The benchmark code is public in https://github.com/scottgw/quicksilver/tree/master/benchmarks/concurrent; all thread-ring programs are Computer Language Benchmarks Game submissions. The C++ side is not TBB: it is the Benchmarks Game Boost.Asio program with 503 OS pthreads waiting on one shared io_service queue, so every token pass is an OS-level futex wake-up and context switch. The Go program (Benchmarks Game, 'contributed by KP') gives each goroutine a sync.Mutex used as a binary semaphore and calls runtime.Gosched() after each hand-off, with GOMAXPROCS set to the worker count. The win is goroutines against OS threads (runtime scheduler, not codegen); a C++ ring on Boost.Fiber, Boost.Context or a single-threaded loop was not measured. The C++ build is -O3, so the baseline is not crippled by flags, but the comparison is of threading models. Go is 4.2x slower than Erlang in the same table. Timing asymmetry in benchmarks/run_all.py: Erlang's TotalTime is its own timer:tc figure printed to stderr (excludes VM boot and shutdown), while C++, Go and Haskell are wall-clock around Popen including process launch and, for C++, creating 503 pthreads; small against multi-second runs but it favours Erlang. The repo's run_all.py at HEAD runs the concurrent tasks with worker_range = [4], while the snippet says the paper table is for 32 cores, so the exact configuration of the published run is not certain. Toolchains date from about 2014 (Go 1.2 or 1.3 era, version not stated). Lead for a paper-access retier. [retier] The worker count in run_all.py reaches only Go (GOMAXPROCS=\$2); C++ ignores it and always runs 503 OS threads, Erlang sets no +S; the '32 cores' label belongs to the parallel-task figure, so the Table 5 configuration is uncertain. The C++ '4 KB stacks' were never applied (pthread_attr_setstack fails under PTHREAD_STACK_MIN 16384, return ignored) and main.cpp no longer builds on Asio 1.38.2. The paper's geomean has C++/TBB 1.57 s beating Go's 1.82 s; each language was run once.

Go gives cheap goroutines and channels but adds a garbage-collected runtime, a fixed scheduler policy and slower cgo calls into C; stacks grow dynamically.

## Maintenance

Go is active and BSD-3-Clause licensed (139.2k stars); the evidence is a single-run 2014 academic comparison whose paper could not be opened (snippet only), whose C++ side no longer builds against current Boost.Asio, and whose worker setting constrained only the Go run, so treat the 2.4x as directional for goroutines against OS threads.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now D.
- **Tier reason:** The paper (peer-reviewed at ESEC/FSE 2015) could not be opened (arxiv.org blocked); a WebSearch summary of its Table 5 gives Go 13.98 s vs C++ 34.13 s on thread-ring, so per the wave-14 rule snippet-only paper numbers stay C. The benchmark code with build flags is public (scottgw/quicksilver benchmarks/concurrent/{cxx,go}/threadring), but compiler versions and the CPU model were not seen, so not A.
- **Retiered** C to D: Enricher: the worker count reaches only Go while the C++ side always runs 503 OS threads with default stacks, the paper's thread-ring row is snippet-only and single-run, and its geomean has C++/TBB ahead of Go; asymmetric threading with no valid like-for-like row: C to D.
- **Verifier notes:** Keep at C. Main shortcomings: numbers snippet only; the 'C++/TBB' baseline for thread-ring is actually the Benchmarks Game Boost.Asio program on 503 OS threads (goroutines vs OS threads, not a codegen win; no C++ fiber ring measured); wall-clock timing via Python Popen. Shares its source and baseline with the Erlang thread-ring record.
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `compiler_and_flags`, `workload`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-93 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/golang/go>
  - <https://github.com/golang/go/commits>
  - <https://github.com/scottgw?tab=repositories>
  - <https://github.com/scottgw/concurrent-languages>
  - <https://github.com/scottgw/concbench>
  - <https://github.com/scottgw/quicksilver>
  - <https://github.com/scottgw/quicksilver/tree/master/benchmarks>
  - <https://github.com/scottgw/quicksilver/tree/master/benchmarks/concurrent>
  - <https://github.com/scottgw/quicksilver/tree/master/benchmarks/concurrent/cxx>
  - <https://github.com/scottgw/quicksilver/tree/master/benchmarks/concurrent/cxx/threadring>
  - <https://github.com/scottgw/quicksilver/tree/master/notes>
  - <https://raw.githubusercontent.com/scottgw/quicksilver/master/benchmarks/run_all.py>
  - <https://raw.githubusercontent.com/scottgw/quicksilver/master/benchmarks/Makefile>
  - <https://raw.githubusercontent.com/scottgw/quicksilver/master/benchmarks/run.sh>
  - <https://raw.githubusercontent.com/scottgw/quicksilver/master/benchmarks/concurrent_graph.r>
  - <https://raw.githubusercontent.com/scottgw/quicksilver/master/benchmarks/common.r>
  - <https://raw.githubusercontent.com/scottgw/quicksilver/master/benchmarks/concurrent/Makefile>
  - <https://raw.githubusercontent.com/scottgw/quicksilver/master/benchmarks/concurrent/cxx/Makefile>
  - <https://raw.githubusercontent.com/scottgw/quicksilver/master/benchmarks/concurrent/go/Makefile>
  - <https://raw.githubusercontent.com/scottgw/quicksilver/master/benchmarks/concurrent/erlang/Makefile>
  - <https://raw.githubusercontent.com/scottgw/quicksilver/master/benchmarks/concurrent/haskell/Makefile>
  - <https://raw.githubusercontent.com/scottgw/quicksilver/master/benchmarks/concurrent/cxx/threadring/Makefile>
  - <https://raw.githubusercontent.com/scottgw/quicksilver/master/benchmarks/concurrent/cxx/threadring/main.cpp>
  - <https://raw.githubusercontent.com/scottgw/quicksilver/master/benchmarks/concurrent/cxx/threadring/run.sh>
  - <https://raw.githubusercontent.com/scottgw/quicksilver/master/benchmarks/concurrent/go/threadring/Makefile>
  - <https://raw.githubusercontent.com/scottgw/quicksilver/master/benchmarks/concurrent/go/threadring/run.sh>
  - <https://raw.githubusercontent.com/scottgw/quicksilver/master/benchmarks/concurrent/go/threadring/main.go>
  - <https://raw.githubusercontent.com/scottgw/quicksilver/master/benchmarks/concurrent/erlang/threadring/Makefile>
  - <https://raw.githubusercontent.com/scottgw/quicksilver/master/benchmarks/concurrent/erlang/threadring/run.sh>
  - <https://raw.githubusercontent.com/scottgw/quicksilver/master/benchmarks/concurrent/erlang/threadring/main.erl>
  - <https://raw.githubusercontent.com/scottgw/quicksilver/master/benchmarks/concurrent/haskell/threadring/Makefile>
- **Sources the enricher read:**
  - <https://github.com/golang/go>
  - <https://raw.githubusercontent.com/golang/go/master/src/sync/mutex.go>
  - <https://raw.githubusercontent.com/golang/go/master/src/internal/sync/mutex.go>
  - <https://raw.githubusercontent.com/golang/go/master/src/runtime/proc.go>
  - <https://raw.githubusercontent.com/scottgw/quicksilver/master/benchmarks/run_all.py>
  - <https://raw.githubusercontent.com/scottgw/quicksilver/master/benchmarks/run.sh>
  - <https://raw.githubusercontent.com/scottgw/quicksilver/master/benchmarks/Makefile>
  - <https://raw.githubusercontent.com/scottgw/quicksilver/master/benchmarks/concurrent/cxx/Makefile>
  - <https://raw.githubusercontent.com/scottgw/quicksilver/master/benchmarks/concurrent/cxx/threadring/main.cpp>
  - <https://raw.githubusercontent.com/scottgw/quicksilver/master/benchmarks/concurrent/cxx/threadring/Makefile>
  - <https://raw.githubusercontent.com/scottgw/quicksilver/master/benchmarks/concurrent/cxx/threadring/run.sh>
  - <https://raw.githubusercontent.com/scottgw/quicksilver/master/benchmarks/concurrent/go/Makefile>
  - <https://raw.githubusercontent.com/scottgw/quicksilver/master/benchmarks/concurrent/go/threadring/main.go>
  - <https://raw.githubusercontent.com/scottgw/quicksilver/master/benchmarks/concurrent/go/threadring/Makefile>
  - <https://raw.githubusercontent.com/scottgw/quicksilver/master/benchmarks/concurrent/go/threadring/run.sh>
  - <https://raw.githubusercontent.com/scottgw/quicksilver/master/benchmarks/concurrent/erlang/threadring/main.erl>
  - <https://raw.githubusercontent.com/scottgw/quicksilver/master/benchmarks/concurrent/erlang/threadring/run.sh>
  - <https://raw.githubusercontent.com/bminor/glibc/glibc-2.19/nptl/pthread_attr_setstack.c>
  - <https://raw.githubusercontent.com/bminor/glibc/glibc-2.19/nptl/pthreadP.h>
  - <https://raw.githubusercontent.com/bminor/glibc/master/nptl/pthread_attr_setstack.c>
  - <https://raw.githubusercontent.com/boostorg/asio/boost-1.55.0/include/boost/asio/detail/impl/task_io_service.ipp>
  - <https://raw.githubusercontent.com/boostorg/asio/boost-1.66.0/include/boost/asio/io_service.hpp>
  - <https://raw.githubusercontent.com/boostorg/asio/develop/include/boost/asio/io_context.hpp>
  - <https://raw.githubusercontent.com/boostorg/asio/develop/include/boost/asio/version.hpp>
  - <https://github.com/scottgw?tab=repositories>
  - https://arxiv.org/abs/1405.7153 (blocked: ENOTFOUND)
  - WebSearch: Efficient and Reasonable Object-Oriented Concurrency thread-ring table (2 queries; snippets give Table 5 times, the 32-core label on Figure 18 and the concurrent-task geometric means)
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:go/arxiv-1405.7153#thread-ring`) · [data/wave14/enrich/raw/lang_go_arxiv_1405_7153_thread_ring.json](../../../data/wave14/enrich/raw/lang_go_arxiv_1405_7153_thread_ring.json) (enrichment confidence 0.4)

</details>
