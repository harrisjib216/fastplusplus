# Pony actor mailbox performance (100,000,000 messages) vs CAF and Charm++

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Concurrency runtimes](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Pony` · `BSD-2-Clause` · 🟢 active

> Pony's actor runtime on a 100-sender, one-receiver mailbox stress test, about 6-8x CAF 0.13 throughput in 2015 charts.

| | |
|---|---|
| **Beats** | CAF 0.13 (C++ Actor Framework); Charm++ 6.6.1 (C++) is in the same chart |
| **Claimed result** | Read off the charts (approximate, ratios derived from page data): at 1 core Pony 0.1.5 about 3.7 versus CAF 0.13 about 0.56 (about 6.6x) and Charm++ 6.6.1 about 0.9 (about 4x); at 16 physical cores Pony about 1.67 versus CAF about 0.27 (about 6x); at 32 physical cores Pony about 1.62 versus CAF about 0.2 (about 8x). Charm++ drops to about 0.15 at 2 cores and stays at or below about 0.13 after that; Erlang OTP 17 falls below 0.1 from about 15 cores; Scala/Akka stays near 0.02 at every core count. With hyper-threading (also Figure 8 of the AGERE! 2015 paper) Pony is about 1.48 against CAF about 0.15-0.2 at 64 threads (roughly 7-10x). Every system, Pony included, loses speed as cores are added (Pony falls from 3.7 at 1 core to about 1.8 at 4), since all senders target one mailbox. |
| **Workload** | Mailbox performance benchmark from the CAF benchmark suite: N sender actors each send M payload-free messages to one counting receiver, 100,000,000 messages in total (N/M split not stated). Pony side: examples/mailbox/main.pony (tag 0.1.7; now examples/actors/mailbox), Mailer actors each calling receiver.pong() M times; CAF side: src/caf/mailbox_performance.cpp in actor-framework/benchmarks. Plotted as speed relative to Erlang OTP 17 on 1 core against physical cores (1-32) and against 32 physical cores with hyper-threading (up to 64 threads). |
| **Metric** | throughput |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | not stated |
| **Same optimization level** | not stated |
| **Adoption** | 6.2k stars (ponyc) |
| **Last commit** | 2026-10-11 |
| **Links** | [repository](https://github.com/ponylang/ponyc) · [benchmark](https://raw.githubusercontent.com/ponylang/ponylang-website/main/docs/benchmarks_all.pdf) |

## Verdict

In the Pony authors' 2015 charts (also Figure 8 of their AGERE! 2015 paper; average of 100 runs, normalised to Erlang OTP 17 on 1 core), Pony 0.1.5 delivered about 3.7 versus CAF 0.13 at about 0.56 on 1 core (about 6.6x) and about 1.6 versus 0.2 at 32 physical cores (about 8x), on 100 million empty messages from many senders to one receiver. CPU model, compilers, flags and the Pony launch parameters are not stated; CAF 0.13 was itself slower than Erlang at 1 core, so the baseline is weak.

## Use it when

- Writing a new service wholly in Pony where many actors fan in to one aggregator (counters, loggers, sinks) and you want a wait-free enqueue path.
- Comparing actor-runtime designs: the Pony MPSC mailbox (messageq.c, about 200 lines of C11 atomics) is a compact reference for a contended N:1 mailbox in your own C or C++ runtime.
- Workloads with payload-free or small messages where per-message overhead, not the handler, dominates.

## Skip it when

- Inside an existing C++ code base: there is no in-process embedding (library mode was removed in ponyc 0.47.0 and the rest of its runtime surface in 0.67.0), so the only route is a separate Pony process.
- Sustained fan-in under modern Pony: since 0.21.0 (2017) the runtime mutes senders to an overloaded actor, and issue #2980 (open since 2019) reports CPU dropping from about 48 busy cores to 1-2 for 10+ seconds on a fan-in pattern; the 2015 chart predates this backpressure.
- Memory-bounded deployments of the 2015-era runtime: the same examples/mailbox program with 20 senders x 1,000,000 messages used more than 2 GB on a 2-core machine (issue #302), and 20 x 100,000,000 reached 17 GB RSS; the chart reports speed only.
- If you need many cores to speed up a single receiver: every system in the chart, Pony included, gets slower with more cores (Pony about 3.7 at 1 core, about 1.8 at 4, about 1.6 at 32, relative to Erlang on 1 core).
- If you need a stable language: Pony is pre-1.0 and its README says it semi-regularly introduces breaking changes.

## How it is fast

Each actor mailbox is a Vyukov-style intrusive MPSC queue: a sender enqueues with one atomic exchange on the head (messageq_push, unchanged in shape from 0.1.7 to today), so producers never retry, and the single consumer pops from the tail with a plain acquire load, no read-modify-write. CAF 0.13's mailbox (detail/single_reader_queue.hpp) is a LIFO stack that every sender pushes onto with a compare_exchange_strong retry loop, and the reader swaps the whole stack out and reverses it; with many senders on one mailbox those CAS retries are the likely source of CAF's loss (the paper gives no profile). Pony messages come from the runtime's pool allocator, and an actor processes up to PONY_SCHED_BATCH (100) messages per scheduling.

## Compared with alternatives

Pick Pony over the Lingua Franca entry (deterministic reactors with a C++ target, also measured against CAF) only if you are writing the whole system in Pony and want nondeterministic actors with compile-time data-race freedom; from C++, Lingua Franca or CAF 1.x is the practical choice. Against the Erlang and Go thread-ring entries, Pony is the native-code actor option with the cheapest contended enqueue, but its chart is a decade old.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | ponyc toolchain (bundles a vendored LLVM, 23.1.3 as of 0.75.0); the standard library's net package needs OpenSSL 1.1.x/3.0.x/4.0.x or LibreSSL at build time |
| **Minimum toolchain** | ponyc (0.75.0 current); building ponyc needs Clang &gt;= 3.4 or GCC &gt;= 4.7, CMake &gt;= 3.25 and Python 3 |
| **Platforms** | Linux amd64/arm64 (kernel 5.3+), macOS amd64/arm64, Windows 11 / Server 2022 amd64/arm64 released; FreeBSD, OpenBSD, DragonFly amd64 and Linux riscv64 tested from source |
| **Thread safety** | Data-race freedom enforced at compile time by reference capabilities; actors share no mutable state and run one behaviour at a time. |
| **Drop-in for the baseline** | no |

## Gotchas

- Benchmark parity looks fine: the Pony program (examples/mailbox, identical at tags 0.1.4, 0.1.5 and 0.1.7) and CAF's mailbox_performance.cpp both send N x M empty messages to one counting receiver. But the 2015 CAF source is not retrievable (the suite's history is not browsable on github.com), and the current CAF usage string still reads 'NUM_THREADS MSGS_PER_THREAD', so the 2015 CAF senders may have been OS threads rather than actors; Pony's senders were actors on one scheduler thread per core.
- No backpressure in Pony 0.1.5: senders could enqueue all 100,000,000 messages faster than Main drained them, so part of the measured speed may come from deferring work into an unbounded queue; memory use was not reported for the chart (the CAF suite's caf_run_bench records memory, but Pony is not one of the suite's run labels, so Pony was launched by its authors' own scripts, which are not published).
- Today's results will differ: generalized runtime backpressure (0.21.0, 2017) mutes senders whose target is overloaded, which this exact fan-in pattern triggers; no post-2015 mailbox run against CAF was found on reachable pages.
- The current CAF suite does not fix an optimisation level for its own executables (no CMAKE_BUILD_TYPE; configure's --build-type is optional) and compiles Charm++ objects with a bare 'charmc -c' (-O3 only on the link line); whether the 2015 runs had the same gaps is unknown.

## Known shortcomings

- Chart is Fig. 8 of the peer-reviewed AGERE! 2015 paper (copy in ponylang-website docs/media/papers/fast-cheap.pdf) from the CAF team's suite, 100-run average, same work both sides, but no CPU, compiler or flags; decade-old versions; CAF 0.13 is slower than Erlang at 1 core, so a weak baseline. Pony's runtime libponyrt is C.
- Programs are equal (N senders x M empty messages; the Pony example is identical at 0.1.4, 0.1.5 and 0.1.7) and the win is a wait-free atomic-exchange MPSC mailbox against CAF 0.13's CAS-retry LIFO stack, but Pony 0.1.5 had no backpressure (issue #302: the same example at 20x1M used more than 2 GB and 20x100M reached 17 GB RSS; memory is not charted). Sender muting since 0.21.0 and the open fan-in issue #2980 mean the ratio is not valid for today's runtime. The 2015 CAF source is unrecoverable (its usage string 'NUM_THREADS' hints the senders were OS threads), the current CAF suite sets no CMAKE_BUILD_TYPE and Charm++ objects are built with bare charmc -c, so 2015 build settings are unknown. Library mode was removed in ponyc 0.47.0, so there is no in-process use from C++. Enricher confidence 0.45.

## Caveats and trade-offs

Charts only: the website PDF (6 pages, gnuplot, created 2015-07-06) and the AGERE! 2015 paper (HT chart only, Figure 8) have no tables, so all figures are read off the plots and are approximate. The paper says results are the average of 100 runs normalised to Erlang on one core, and that the benchmark implementations come from the CAF suite, written by programmers expert in each system (the CAF team for CAF). Neither source names the CPU (only '32 physical cores with HT'), compiler, optimisation flags or variance. The CAF-side build type used in 2015 could not be recovered: the suite's history before today is not browsable, and its current CMakeLists sets Erlang +native/hipe o3 and Charm++ -O3 but no C++ build type. The March 2015 tech-report version (fast-cheap-with-proof.pdf) ran an execution-time version on a 12-core 2.3 GHz Opteron 6338P; those are different runs. The versions are about a decade old (Pony 0.1.5, CAF 0.13, Charm++ 6.6.1, Erlang OTP 17, Scala 2.11.6 Akka; ponyc is now at 0.75.0 and CAF at 1.x), so the ratio may not hold today. CAF 0.13 at 1 core (about 0.56) is slower than both Erlang (1.0) and Charm++ (about 0.9) here, so the C++ baseline is a weak spot of CAF 0.13 under a contended mailbox, not tuned hand-written C++. Both papers are by the Pony authors (Causality and Imperial College). The same PDF and paper show a loss: on 'Creating 1,048,576 actors' CAF overtakes Pony beyond about 10 physical cores (about 17 versus 9 at 32 cores), so this is a per-benchmark win. The Pony runtime (libponyrt) is written in C. www.ponylang.io and a later Pony 0.26.0 versus CAF 0.16.3 run on doc.ic.ac.uk/\~scb12/pony.html were blocked here and are not used. [retier] Enricher: programs are equal (N senders x M empty messages; the Pony example is identical at 0.1.4, 0.1.5 and 0.1.7) and the win is a wait-free atomic-exchange MPSC mailbox against CAF 0.13's CAS-retry LIFO stack, but Pony 0.1.5 had no backpressure (issue #302: 20x1M used more than 2 GB and 20x100M reached 17 GB RSS; memory is not charted), and sender muting since 0.21.0 plus the open fan-in issue #2980 mean the ratio is not valid for today's runtime. The 2015 CAF source is unrecoverable (its usage string 'NUM_THREADS' hints the senders were OS threads), the current CAF suite sets no CMAKE_BUILD_TYPE and Charm++ objects are built with bare charmc -c, so 2015 build settings are unknown. Library mode was removed in ponyc 0.47.0.

Pony is a separate language and runtime (actors with per-actor heaps, reference capabilities, no shared mutable state); using it from C++ means FFI or a separate process. Smaller ecosystem and a steeper learning curve than a C++ library such as CAF.

## Maintenance

ponyc is actively maintained (0.75.0 released 2026-10-11, BSD-2-Clause, about 6.2k stars), but the measurement is from Pony 0.1.5 and CAF 0.13 in 2015, before Pony added sender-muting backpressure, so treat it as a historical data point about MPSC mailbox design rather than a current ratio.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now B.
- **Tier reason:** Upgraded C to B: the hyper-threaded chart in the PDF is Figure 8 of the peer-reviewed AGERE! 2015 paper 'Deny Capabilities for Safe, Fast Actors' (author copy docs/media/papers/fast-cheap.pdf in ponylang-website), which states the benchmarks come from the CAF team's suite (github.com/actor-framework/benchmarks) and plots the average of 100 runs; CPU model, compiler and flags are not stated anywhere, so not A.
- **Verifier notes:** Upgraded to B on the peer-reviewed AGERE! 2015 paper (same chart as Figure 8, CAF team's benchmark suite, 100-run average); CPU, compiler and flags missing. Pony and CAF programs do the same work (N senders, M empty messages, one counting receiver). Shortcomings: decade-old versions; CAF 0.13 slower than Erlang at 1 core, so a weak baseline; build flags unknown (same_opt_level null); first-party authors; the win is from Pony's C runtime; Pony loses actor creation to CAF.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-45 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/ponylang/ponylang-website/main/docs/benchmarks_all.pdf>
  - <https://raw.githubusercontent.com/ponylang/ponylang-website/main/docs/media/papers/fast-cheap.pdf>
  - <https://raw.githubusercontent.com/ponylang/ponylang-website/main/docs/media/papers/fast-cheap-with-proof.pdf>
  - <https://github.com/ponylang/ponylang-website>
  - <https://github.com/ponylang/ponylang-website/tree/main/docs>
  - <https://github.com/ponylang/ponyc>
  - <https://github.com/ponylang/ponyc/commits/main>
  - <https://github.com/ponylang/ponyc/tree/main/examples/actors>
  - <https://github.com/actor-framework/benchmarks>
  - <https://github.com/actor-framework/benchmarks/tree/master/src>
  - <https://github.com/actor-framework/benchmarks/tree/master/src/caf>
  - <https://raw.githubusercontent.com/actor-framework/benchmarks/master/CMakeLists.txt>
  - <https://raw.githubusercontent.com/actor-framework/benchmarks/master/README.md>
  - <https://raw.githubusercontent.com/ponylang/ponyc/main/examples/actors/mailbox/main.pony>
  - <https://raw.githubusercontent.com/ponylang/ponyc/0.1.7/examples/mailbox/main.pony>
  - <https://raw.githubusercontent.com/actor-framework/benchmarks/master/src/caf/mailbox_performance.cpp>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/ponylang/ponylang-website/main/docs/benchmarks_all.pdf>
  - <https://raw.githubusercontent.com/ponylang/ponylang-website/main/docs/media/papers/fast-cheap.pdf>
  - <https://raw.githubusercontent.com/ponylang/ponyc/main/README.md>
  - <https://raw.githubusercontent.com/ponylang/ponyc/main/BUILD.md>
  - <https://raw.githubusercontent.com/ponylang/ponyc/main/INSTALL.md>
  - <https://raw.githubusercontent.com/ponylang/ponyc/main/CHANGELOG.md>
  - <https://raw.githubusercontent.com/ponylang/ponyc/main/examples/actors/mailbox/main.pony>
  - <https://raw.githubusercontent.com/ponylang/ponyc/0.1.7/examples/mailbox/main.pony>
  - <https://raw.githubusercontent.com/ponylang/ponyc/0.1.5/examples/mailbox/main.pony>
  - <https://raw.githubusercontent.com/ponylang/ponyc/0.1.4/examples/mailbox/main.pony>
  - <https://raw.githubusercontent.com/ponylang/ponyc/main/src/libponyrt/actor/messageq.c>
  - <https://raw.githubusercontent.com/ponylang/ponyc/0.1.7/src/libponyrt/actor/messageq.c>
  - <https://raw.githubusercontent.com/ponylang/ponyc/main/src/libponyrt/actor/actor.c>
  - <https://raw.githubusercontent.com/ponylang/ponyc/main/src/libponyrt/sched/scheduler.c>
  - <https://raw.githubusercontent.com/ponylang/ponyc/main/src/libponyrt/sched/start.c>
  - <https://raw.githubusercontent.com/ponylang/ponyc/main/src/libponyc/options/options.c>
  - <https://raw.githubusercontent.com/actor-framework/benchmarks/master/src/caf/mailbox_performance.cpp>
  - <https://raw.githubusercontent.com/actor-framework/benchmarks/master/README.md>
  - <https://raw.githubusercontent.com/actor-framework/benchmarks/master/CMakeLists.txt>
  - <https://raw.githubusercontent.com/actor-framework/benchmarks/master/configure>
  - <https://raw.githubusercontent.com/actor-framework/benchmarks/master/src/caf/CMakeLists.txt>
  - <https://raw.githubusercontent.com/actor-framework/benchmarks/master/scripts/activate_cores>
  - <https://raw.githubusercontent.com/actor-framework/benchmarks/master/src/scripts/run.in>
  - <https://raw.githubusercontent.com/actor-framework/benchmarks/master/src/scripts/caf_run_benchmarks.in>
  - <https://raw.githubusercontent.com/actor-framework/actor-framework/0.13/libcaf_core/caf/detail/single_reader_queue.hpp>
  - <https://github.com/actor-framework/benchmarks/commits/master/src/scripts/caf_run_benchmarks.in>
  - <https://github.com/ponylang/ponyc/issues?q=is%3Aissue%20mailbox%20OR%20backpressure%20performance>
  - <https://github.com/ponylang/ponyc/issues/302>
  - <https://github.com/ponylang/ponyc/issues/2980>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:pony/ponylang/ponylang-website#mailbox-performance`) · [data/wave14/enrich/raw/lang_pony_ponylang_ponylang_website_mailbox_performance.json](../../../data/wave14/enrich/raw/lang_pony_ponylang_ponylang_website_mailbox_performance.json) (enrichment confidence 0.45)

</details>
