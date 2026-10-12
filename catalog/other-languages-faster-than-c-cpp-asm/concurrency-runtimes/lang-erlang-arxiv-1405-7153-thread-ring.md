# Erlang/OTP processes on thread-ring (SCOOP/Qs paper, arXiv 1405.7153) vs C++/TBB

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Concurrency runtimes](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Erlang` · `Apache-2.0` · 🟢 active

> Erlang/BEAM processes pass a token round a 503-member ring about 10x faster than a Boost.Asio C++ program using 503 OS threads.

| | |
|---|---|
| **Beats** | The paper's 'C++/TBB' column; for thread-ring the authors' public code (scottgw/quicksilver benchmarks/concurrent/cxx/threadring/main.cpp) is not TBB but the Computer Language Benchmarks Game C++ program by The Anh Tran: 503 OS pthreads (4 KB stacks) all blocked in one boost::asio::io_service::run() queue, each token pass a post() that wakes an OS thread; built with g++ -O3 -std=c++11 -pthread -lboost_system. No fiber, coroutine or single-threaded C++ ring was measured. |
| **Claimed result** | Thread-ring on 32 cores (snippet only, paper Table 5): Erlang 3.30 s versus the paper's C++/TBB column 34.13 s, about 10.3x (derived from the snippet numbers); the C++ program is Boost.Asio over 503 OS threads. |
| **Workload** | thread-ring (Computer Language Benchmarks Game spec): 503 ring members pass a token 5,000,000 times (input in benchmarks/run_all.py); essentially single-threaded and bound by context-switch cost. Paper table reported for a 32-core machine (snippet). |
| **Metric** | latency |
| **Hardware** | 32 cores (CPU model not seen) |
| **Compiler and flags** | From the authors' Makefiles and run.sh in scottgw/quicksilver benchmarks/concurrent/\*/threadring: C++ g++ -O3 -std=c++11 -pthread -lboost_system; Go 'go build' defaults, run with GOMAXPROCS set to the worker count; Erlang erlc -W (plain BEAM, no +native) run as erl -smp enable -noshell +t 8192 +P &lt;n&gt; +ec +K true +hms 4 +hmbs 1; Haskell ghc --make -O2 -threaded -rtsopts. Input 5,000,000 token passes for every language. Compiler and runtime versions not stated in the repo (code dates from 2014). |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | not stated |
| **Same optimization level** | not stated |
| **Why it wins** | Inferred, not argued by the snippet: Erlang processes are lightweight units switched by the BEAM scheduler in user space, and the benchmark is context-switch bound, so the cost per switch dominates. |
| **Adoption** | 12.4k stars |
| **Last commit** | 2026-10-09 |
| **Links** | [repository](https://github.com/erlang/otp) · [benchmark](https://arxiv.org/pdf/1405.7153) |

## Verdict

In West, Nanz and Meyer's ESEC/FSE 2015 paper (arXiv 1405.7153), the thread-ring entry in Table 5, seen through search summaries only, shows Erlang at 3.30 s against 34.13 s for the column labelled C++/TBB, about 10.3x (derived from those numbers). The C++ column is the Benchmarks Game Boost.Asio program (g++ -O3 -std=c++11 -pthread) on 503 OS threads. Erlang was plain BEAM bytecode from circa 2014. The run was on a Linux machine with 32 cores; CPU model and compiler versions were not stated, and the token was passed 5,000,000 times.

## Use it when

- Designs with very many mostly idle concurrent agents (thousands to millions of actors or sessions) that hand small messages to each other, where per-message cost is dominated by switching rather than computation.
- Message-passing pipelines or rings where one OS thread per agent would be the natural C++ design and the C++ team would not otherwise reach for fibers or an executor.
- Systems that also want BEAM's preemptive per-process scheduling, per-process heaps and supervision, with context-switch-bound hand-offs as a performance bonus.
- As a reference point when arguing that an OS-thread-per-agent C++ design is the problem: the 10x gap measures thread models, not compilers.

## Skip it when

- As evidence that Erlang beats C++ on concurrency in general: in the same paper's concurrent suite C++/TBB has the best geometric mean (1.57 s) and Erlang one of the worst (5.01 s, only Haskell is slower at 12.20 s), per a search summary of the paper.
- Against a C++ design that uses user-space switching (Boost.Fiber, Boost.Context, C++20 coroutines on one executor, or a plain single-threaded loop); none was measured, and these remove the OS context switch that the C++ baseline pays on every pass.
- CPU-bound kernels or numeric code: BEAM's single-thread compute is slower than optimised C++, and the 2014 run used the bytecode interpreter (erlc without +native, before the OTP 24 JIT).
- Code that must call C on the hot path: NIFs or ports add a boundary and long-running NIFs block a scheduler.

## How it is fast

The speedup comes from green threads against OS threads. An Erlang process is a heap-allocated BEAM object, and a send-and-receive between two processes is a mailbox enqueue plus a user-space scheduler switch inside one runtime thread. In the C++ program each post() locks the shared io_service queue and wakes one of the 503 sleeping OS threads, so every pass costs a futex wake-up and a kernel context switch, often across cores. The task is essentially single-threaded (one token in flight), so the per-switch cost decides the result. The paper itself says thread-ring and condition test context-switching overhead.

## Compared with alternatives

This is the same paper and harness as the Go goroutines thread-ring sibling: Erlang is 3.30 s against Go's 13.98 s, so pick it if a context-switch-bound ring or pipeline is the whole workload. The GHC lightweight-threads sibling (skynet) measures spawn cost rather than hand-off cost, and Pony against CAF compares actors with C++ actors rather than with OS threads, which makes the Pony entry the fairer actor-runtime comparison.

## Integration

| | |
|---|---|
| **Form** | language runtime (Erlang/OTP: erlc compiler plus the BEAM virtual machine started with erl) |
| **Dependencies** | Erlang/OTP runtime (ERTS); the C++ baseline needs Boost.Asio and libboost_system |
| **Minimum toolchain** | Not stated for the 2014 run (erlc -W, erl -smp enable); current master is OTP 30.0-rc0. The run script's -smp and +K flags no longer appear in the current erl command reference, so a modern rerun should drop them. |
| **Platforms** | Wherever ERTS runs (Linux, macOS, Windows, BSDs); the measured run was Linux on a 32-core machine whose CPU model was not seen |
| **Thread safety** | Erlang processes share nothing and communicate by copying messages; the runtime runs one scheduler thread per logical CPU by default (+S). |
| **Drop-in for the baseline** | no |

## Gotchas

- The C++ baseline in this comparison is not TBB and is not tuned for this task. It is the Benchmarks Game Boost.Asio program on 503 OS threads. Its claimed 4 KB stacks are not used on glibc either: pthread_attr_setstack() rejects sizes below PTHREAD_STACK_MIN (16384 bytes in glibc's Linux pthread_stack_min.h; check_stacksize_attr returns EINVAL), main.cpp ignores the return value, and the 503 threads get default-sized stacks. This harness flaw does not change the timing much, but the record's '503 OS pthreads (4 KB stacks)' should read 'default-sized stacks'.
- The timers differ. In benchmarks/run_all.py, Erlang's TotalTime is its own timer:tc figure printed to stderr, which excludes VM start-up and shutdown. C++ is timed as wall clock around Popen (sh, run.sh, process launch and creation of 503 pthreads). Against 3.30 s and 34.13 s this is small, but it favours Erlang.
- The thread counts are not equal. At HEAD, run_all.py runs the concurrent tasks only with workers = 4. Go's run.sh sets GOMAXPROCS=4. The C++ thread-ring ignores the worker argument (always 503 threads). Erlang's run.sh passes '+P 5000000 4', so the 4 becomes a stray plain argument, and BEAM starts its default of one scheduler per logical CPU. The '32 cores' attached to Table 5 may come from the parallel-task figure caption (Figure 18), so the published configuration is uncertain.
- The paper numbers (Erlang 3.30 s against C++ 34.13 s) were seen only through WebSearch summaries; arxiv.org could not be resolved from this environment, and the repo has no result CSVs, so the table was not checked directly.

## Known shortcomings

- Paper numbers (Table 5: Erlang 3.30 s vs C++ 34.13 s) seen in a snippet only (arXiv blocked); the C++ side is not TBB but the Benchmarks Game Boost.Asio program with 503 OS pthreads on one io_service (g++ -O3), so the win is green threads vs OS threads, not codegen, and no C++ fiber ring was measured; Erlang timed by timer:tc, C++ wall-clock; code in scottgw/quicksilver benchmarks/concurrent without compiler versions or CPU model. Paper-access retier lead.
- Harness flaws: the C++ main.cpp asks for 4 KB stacks, below glibc's PTHREAD_STACK_MIN of 16384, so pthread_attr_setstack returns EINVAL, the return is unchecked and the 503 threads get default stacks (the record's '4 KB stacks' was wrong). Unequal threads: run_all.py's concurrent tasks use workers=4 (Go GOMAXPROCS=4; C++ ignores the argument; Erlang's run.sh passes '+P 5000000 4', so BEAM runs one scheduler per CPU); the '32 cores' label likely comes from the parallel-task Figure 18 caption, not Table 5. Erlang is timed by timer:tc, the others by wall clock. The paper's concurrent geomean (snippet) has C++/TBB 1.57 s against Erlang 5.01 s, so thread-ring is an outlier. The -smp and +K flags are gone from current erl docs.

## Caveats and trade-offs

Paper numbers seen only through WebSearch result summaries (Table 5 of arXiv 1405.7153, 'Efficient and Reasonable Object-Oriented Concurrency', West, Nanz and Meyer, published at ESEC/FSE 2015): thread-ring on 32 cores Erlang 3.30 s, SCOOP/Qs 5.82 s, Go 13.98 s, C++/TBB 34.13 s, Haskell 57.44 s; arxiv.org is blocked here, so the table, CPU model and compiler versions were not opened. The benchmark code is public in https://github.com/scottgw/quicksilver/tree/master/benchmarks/concurrent (cxx, go, erlang, haskell, qs, java), and all thread-ring programs are Computer Language Benchmarks Game submissions. The C++ side is not TBB: it is the Benchmarks Game Boost.Asio program with 503 OS pthreads waiting on one shared io_service queue, so every token pass is an OS-level futex wake-up and context switch, while Erlang passes the token between BEAM processes inside a user-space scheduler. The win is green threads against OS threads (runtime, not codegen); a C++ ring on Boost.Fiber, Boost.Context or a single-threaded loop was not measured and would very likely beat both. The C++ build is -O3, so the baseline is not crippled by flags, but the comparison is of threading models. Timing asymmetry in benchmarks/run_all.py: Erlang's TotalTime is its own timer:tc figure printed to stderr (excludes VM boot and shutdown), while C++, Go and Haskell are wall-clock around Popen including process launch and, for C++, creating 503 pthreads; small against multi-second runs but it favours Erlang. The repo's run_all.py at HEAD runs the concurrent tasks with worker_range = [4], while the snippet says the paper table is for 32 cores, so the exact configuration of the published run is not certain. Toolchains date from about 2014 (BEAM without JIT). Lead for a paper-access retier. [retier] The C++ main.cpp asks for 4 KB stacks below glibc's PTHREAD_STACK_MIN, so pthread_attr_setstack fails silently and the 503 threads get default stacks. run_all.py's concurrent tasks use workers=4 (Go GOMAXPROCS=4; C++ ignores the argument; Erlang '+P 5000000 4' runs one scheduler per CPU); the '32 cores' label likely belongs to the parallel-task figure, not Table 5. Erlang is timed by timer:tc, the others by wall clock. The paper's concurrent geomean has C++/TBB 1.57 s against Erlang 5.01 s, so thread-ring is an outlier.

BEAM gives cheap processes and preemptive per-process scheduling with garbage-collected per-process heaps; a language runtime is required, and raw single-thread compute is slower than C++. Calling C needs NIFs or ports.

## Maintenance

Erlang/OTP is actively maintained (Apache-2.0, 12.4k stars, master at OTP 30.0-rc0). The benchmark harness (scottgw/quicksilver, 2014) is unmaintained but public. Treat the result as a measurement of green threads against OS threads, not a reason to port C++ code to Erlang; the thread-count and timer mismatches and the misdescribed 4 KB C++ stacks are harness flaws documented above.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now D.
- **Tier reason:** The paper (peer-reviewed at ESEC/FSE 2015) could not be opened (arxiv.org blocked); a WebSearch summary of its Table 5 gives Erlang 3.30 s vs C++ 34.13 s on thread-ring, so per the wave-14 rule snippet-only paper numbers stay C. The benchmark code with build flags is public (scottgw/quicksilver benchmarks/concurrent/{cxx,erlang}/threadring), but compiler versions and the CPU model were not seen, so not A.
- **Retiered** C to D: Enricher: the paper's thread-ring row is snippet-only, each language ran once, the C++ side is a Boost.Asio program over 503 OS threads whose 4 KB stacks were never applied while Erlang ran one scheduler per CPU, and the paper's own concurrent geomean goes the other way (C++/TBB 1.57 s vs Erlang 5.01 s); asymmetric threading on a single snippet-only run: C to D (same table and tier as the Go row).
- **Verifier notes:** Keep at C. Main shortcomings: numbers snippet only; the 'C++/TBB' baseline for thread-ring is actually the Benchmarks Game Boost.Asio program on 503 OS threads (OS threads vs green threads, not a language/codegen win; no C++ fiber ring measured); Erlang timed by its own timer:tc while C++ is wall-clock with process launch. Code is public at scottgw/quicksilver benchmarks/concurrent, so a retier to B needs only the paper.
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `compiler_and_flags`, `workload`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-93 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/erlang/otp>
  - <https://github.com/erlang/otp/commits>
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
  - <https://raw.githubusercontent.com/scottgw/quicksilver/master/benchmarks/run_all.py>
  - <https://raw.githubusercontent.com/scottgw/quicksilver/master/benchmarks/run.sh>
  - <https://raw.githubusercontent.com/scottgw/quicksilver/master/benchmarks/concurrent/cxx/threadring/main.cpp>
  - <https://raw.githubusercontent.com/scottgw/quicksilver/master/benchmarks/concurrent/cxx/threadring/Makefile>
  - <https://raw.githubusercontent.com/scottgw/quicksilver/master/benchmarks/concurrent/cxx/threadring/run.sh>
  - <https://raw.githubusercontent.com/scottgw/quicksilver/master/benchmarks/concurrent/erlang/threadring/main.erl>
  - <https://raw.githubusercontent.com/scottgw/quicksilver/master/benchmarks/concurrent/erlang/threadring/Makefile>
  - <https://raw.githubusercontent.com/scottgw/quicksilver/master/benchmarks/concurrent/erlang/threadring/run.sh>
  - <https://raw.githubusercontent.com/scottgw/quicksilver/master/benchmarks/concurrent/go/threadring/main.go>
  - <https://raw.githubusercontent.com/scottgw/quicksilver/master/benchmarks/concurrent/go/threadring/run.sh>
  - <https://raw.githubusercontent.com/scottgw/quicksilver/master/benchmarks/concurrent/go/threadring/Makefile>
  - <https://raw.githubusercontent.com/scottgw/quicksilver/master/benchmarks/concurrent/haskell/threadring/run.sh>
  - <https://raw.githubusercontent.com/scottgw/quicksilver/master/benchmarks/concurrent/qs/threadring/Makefile>
  - <https://raw.githubusercontent.com/scottgw/quicksilver/master/benchmarks/concurrent/qs/threadring/run.sh>
  - <https://raw.githubusercontent.com/scottgw/quicksilver/master/benchmarks/concurrent/qs/threadring/main.e>
  - <https://raw.githubusercontent.com/scottgw/quicksilver/master/benchmarks/concurrent_graph.r>
  - <https://raw.githubusercontent.com/scottgw/quicksilver/master/benchmarks/concurrent_eve.r>
  - <https://raw.githubusercontent.com/scottgw/quicksilver/master/benchmarks/common.r>
  - <https://raw.githubusercontent.com/scottgw/quicksilver/master/benchmarks/gen_graphs.r>
  - <https://github.com/scottgw/quicksilver/tree/master/benchmarks>
  - <https://github.com/erlang/otp>
  - <https://raw.githubusercontent.com/erlang/otp/master/README.md>
  - <https://raw.githubusercontent.com/erlang/otp/master/OTP_VERSION>
  - <https://raw.githubusercontent.com/erlang/otp/master/erts/doc/references/erl_cmd.md>
  - <https://raw.githubusercontent.com/bminor/glibc/master/nptl/pthread_attr_setstack.c>
  - <https://raw.githubusercontent.com/bminor/glibc/master/sysdeps/nptl/pthreadP.h>
  - <https://raw.githubusercontent.com/bminor/glibc/master/sysdeps/unix/sysv/linux/bits/pthread_stack_min.h>
  - https://arxiv.org/abs/1405.7153 (blocked: DNS lookup failed; WebSearch summary of the paper used instead)
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:erlang/arxiv-1405.7153#thread-ring`) · [data/wave14/enrich/raw/lang_erlang_arxiv_1405_7153_thread_ring.json](../../../data/wave14/enrich/raw/lang_erlang_arxiv_1405_7153_thread_ring.json) (enrichment confidence 0.55)

</details>
