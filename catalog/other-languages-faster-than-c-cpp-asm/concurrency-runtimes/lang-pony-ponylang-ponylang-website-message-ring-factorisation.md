# Pony actor message ring plus factorisation vs CAF and Charm++

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Concurrency runtimes](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Pony` · `BSD-2-Clause` · 🟢 active

> Pony actor rings plus trial-division workers vs CAF 0.13 (2015 charts, 2-4x); Pony's program skips most repetitions.

| | |
|---|---|
| **Beats** | CAF 0.13 (C++ Actor Framework); Charm++ 6.6.1 (C++) is in the same chart |
| **Claimed result** | Read off the charts (approximate, ratios derived from page data): at 1 core Pony 0.1.5 about 2.2 versus CAF 0.13 about 0.5 (about 4x); at 16 physical cores Pony about 29 versus CAF about 8 (about 3.6x); at 32 physical cores Pony about 48 versus CAF about 16 (about 3.0x), with Erlang OTP 17 about 19, Scala/Akka about 13.5 and Charm++ 6.6.1 about 9. With hyper-threading (also Figure 9 of the AGERE! 2015 paper) Pony is about 62 at 64 threads, against CAF at about 26-27 over 56-63 threads and about 30 at its final 64-thread point (about 2.1-2.4x), Erlang about 24 and Akka about 25. |
| **Workload** | Mixed case ('Message ring + factorisation') from the CAF benchmark suite: rings of actors pass a token while a worker factorises 86028157 x 329545133 by trial division on each repetition. Pony side: examples/mixed/main.pony (tag 0.1.7; now examples/actors/mixed) with defaults of 20 rings of 50 actors, 10,000 laps and 5 repetitions. CAF side: src/caf/mixed_case.cpp in actor-framework/benchmarks. The run parameters behind the charts are not stated. Plotted as speed relative to Erlang OTP 17 on 1 core against physical cores (1-32) and against 32 physical cores with hyper-threading (up to 64 threads). |
| **Metric** | throughput |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | not stated |
| **Same optimization level** | not stated |
| **Adoption** | 6.2k stars (ponyc) |
| **Last commit** | 2026-10-11 |
| **Links** | [repository](https://github.com/ponylang/ponyc) · [benchmark](https://raw.githubusercontent.com/ponylang/ponylang-website/main/docs/benchmarks_all.pdf) |

## Verdict

The Pony authors' 2015 charts (also Figure 9 of the AGERE! 2015 paper; 100-run averages normalised to Erlang OTP 17 on 1 core; CPU, compilers and flags not stated) show Pony 0.1.5 at about 2.2 vs CAF 0.13 at about 0.5 on 1 core and about 48 vs 16 at 32 physical cores. Reading the Pony program shows it runs only the first repetition of each ring under its own and the suite's default arguments, so Pony likely did a quarter to a fifth of CAF's ring messages and factorisations; the ratios are not a valid like-for-like measurement.

## Use it when

- Do not use this entry as evidence; use it only as a pointer to the Pony runtime and to the CAF suite's mixed workload, which is a reasonable shape (messaging plus CPU-bound workers) for testing an actor runtime.
- If you write a new service in Pony that mixes chatty actors with CPU-heavy tasks, Pony's work-stealing schedulers run both on the same threads without dedicated OS threads per worker.
- If you are re-running the comparison: fix the Pony ring so the master always restarts (or choose laps with pass = 1 mod (size + 1)) and check the factorisation result, then compare against a current CAF 1.x.

## Skip it when

- As a performance claim against CAF: the Pony program does a fraction of CAF's work under any arguments where the laps value is not 1 mod (ring size + 1).
- From C++: ponyc removed library mode in 0.47.0 (2022), so Pony code can only run as its own process; Pony calls C, not the reverse.
- As a guide to today's runtime: the chart used Pony 0.1.5, before generalized runtime backpressure (sender muting, 0.21.0 in 2017) and dynamic scheduler scaling (0.21.1), and CAF 0.13, a decade before CAF 1.x.
- If you need a stable language: Pony is pre-1.0 and its README says it semi-regularly introduces breaking changes.

## How it is fast

In principle the same runtime properties as the mailbox entry: wait-free MPSC mailboxes (one atomic exchange per send), per-core scheduler threads with work stealing, and native LLVM code for the trial division, with the factorisation run as an ordinary actor instead of CAF's detached (own OS thread) worker. In practice most of the charted gap is explained by a bug in the Pony benchmark program that makes it run only the first of its repetitions (see gotchas), so no runtime technique can be credited from this chart.

## Compared with alternatives

Do not pick this entry on its numbers; the Pony mailbox entry is the sounder Pony-vs-CAF data point, and Lingua Franca (C++ target, also measured against CAF on Savina) is the option usable from C++. Against the Erlang and Go thread-ring entries, this one carries a known work-shortfall bug.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | ponyc toolchain (bundles a vendored LLVM, 23.1.3 as of 0.75.0); the net package needs OpenSSL 1.1.x/3.0.x/4.0.x or LibreSSL at build time |
| **Minimum toolchain** | ponyc (0.75.0 current); building ponyc needs Clang &gt;= 3.4 or GCC &gt;= 4.7, CMake &gt;= 3.25 and Python 3 |
| **Platforms** | Linux amd64/arm64 (kernel 5.3+), macOS amd64/arm64, Windows 11 / Server 2022 amd64/arm64 released; FreeBSD, OpenBSD, DragonFly amd64 and Linux riscv64 tested from source |
| **Thread safety** | Data-race freedom enforced at compile time by reference capabilities; actors share no mutable state and run one behaviour at a time. |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness bug, Pony side: each Ring is a master plus 'size' neighbours (size + 1 actors). The master sends a token of value pass \* size, every actor forwards value - 1, and the actor that receives 0 calls run(); only the master has repetitions left (neighbours are built with _repetitions = 0), so a neighbour that receives 0 does nothing and the token dies. The master receives the 0 only when pass = 1 mod (size + 1). With the program's own defaults (20 rings, 50 actors, 10,000 laps, 5 repetitions) and with the CAF suite's defaults (mixed_case="100 100 1000 4") that does not hold, so each ring runs one repetition: one Worker (factorisation) instead of 5 or 4, and 500,001 or 100,001 token hops instead of about 2.5 million or 400,000. A step-by-step model of the code confirms this (1 of 5 and 1 of 4 repetitions; with pass = 102, size = 100 all 4 run). The program then ends by quiescence with no error. The code is unchanged at 0.1.4, 0.1.5 (the charted version), 0.1.7 and on main.
- CAF's mixed_case.cpp always completes every repetition (the master decrements the token once per lap and builds a new ring on 0), rebuilds the ring each time, factorises in a detached worker and sends every result to a supervisor that counts 400 results plus 100 done messages at suite defaults. Pony also builds each ring only once and never uses its factorisation result.
- The Pony launch arguments behind the chart are not published (Pony is not one of the suite's run labels), so a run with a laps value that happens to satisfy pass = 1 mod (size + 1) cannot be ruled out. But the about 4.4x Pony/CAF ratio at 1 core (about 2.2 vs 0.5) is close to the 4-5x work shortfall, while by operation count the dominant cost at suite defaults (400 trial divisions of about 165 million 64-bit modulo steps each, against about 40 million token hops) is native code in both systems (inference from the code, not a measurement).
- The current CAF suite sets no CMAKE_BUILD_TYPE for its executables and compiles Charm++ objects with a bare 'charmc -c' (-O3 only on the link line); the 2015 build settings are not recoverable.

## Known shortcomings

- Unequal work: Pony builds the ring once and drops the factor result while CAF mixed_case rebuilds the ring each repetition and sends checked results; at 64 threads CAF reads about 30 at the last point, so the gap is about 2.1x, not 2.4x; no CPU, compiler or flags. Pony's runtime libponyrt is C.
- Harness bug in the Pony program (examples/mixed at 0.1.4, 0.1.5 as charted, 0.1.7 and main): the master receives the 0 token only if pass = 1 mod (size + 1); otherwise the token dies at a neighbour (built with _repetitions = 0) and the program quits at quiescence without error. With its own defaults (20, 50, 10000, 5) it runs 1 of 5 repetitions and with the CAF suite's defaults ('100 100 1000 4') 1 of 4, confirmed by a Python model of the ring, so Pony did about a quarter to a fifth of CAF's work, which matches the 4.4x gap at 1 core. The CAF suite sets no CMAKE_BUILD_TYPE and Charm++ objects are built with bare charmc -c. Retiered to D as no valid measurement (fc_malloc and dp::thread_pool precedents).

## Caveats and trade-offs

Unequal work between implementations: in the public Pony program (unchanged from tag 0.1.7 to today) each Ring master builds its ring once and reuses it across all repetitions, spawns a fresh Worker actor per repetition, and computes but never uses the factorisation result (the 'correct' flag is dropped; no message, no check). The CAF suite's mixed_case.cpp (current version; the 2015 CAF 0.13 version could not be retrieved) spawns a new ring of ring_size-1 actors on every repetition while the old links quit, factorises in one detached (own-thread) worker per ring, and sends every factor vector to a supervisor that checks it. Pony therefore skips ring re-creation and the result messages that CAF pays for. Charts only: the website PDF (gnuplot, created 2015-07-06) and the paper have no tables, so figures are approximate. The paper gives 100-run averages but no CPU model (only '32 physical cores with HT'), compiler, flags or variance, and the CAF build type is unknown. Versions are about a decade old (Pony 0.1.5, CAF 0.13, Charm++ 6.6.1, Erlang OTP 17, Scala 2.11.6 Akka). On the physical-core chart Erlang OTP 17 beats CAF at every core count (about 19 versus 16 at 32 cores); with HT, CAF passes Erlang at about 48 threads and ends ahead (about 30 versus 24 at 64). So CAF 0.13 is a weak baseline here, and the Pony gap says more about CAF's scaling and the unequal work than about the language. Both papers are by the Pony authors. The same sources show CAF beating Pony on actor creation beyond about 10 physical cores. The Pony runtime (libponyrt) is written in C. www.ponylang.io and doc.ic.ac.uk/\~scb12/pony.html were blocked and are not used. [retier] Enricher: harness bug in the Pony program; the master receives the 0 token only if pass = 1 mod (size + 1), otherwise the token dies at a neighbour (built with _repetitions = 0) and the program quits at quiescence without error. With its own defaults (20, 50, 10000, 5) it runs 1 of 5 repetitions and with the CAF suite's defaults ('100 100 1000 4') 1 of 4, confirmed by a Python model of the ring, so Pony did about a quarter to a fifth of CAF's work, matching the 4.4x gap at 1 core. The CAF suite sets no CMAKE_BUILD_TYPE and Charm++ objects are built with bare charmc -c.

Pony is a separate language and runtime (actors with per-actor heaps, reference capabilities, no shared mutable state); using it from C++ means FFI or a separate process. Smaller ecosystem and a steeper learning curve than a C++ library such as CAF.

## Maintenance

ponyc is actively maintained (0.75.0 released 2026-10-11, BSD-2-Clause, about 6.2k stars), but this 2015 measurement rests on a Pony benchmark program that skips all but its first repetition, so it should be treated as no valid measurement (candidate for tier D or reject under the fc_malloc and dp::thread_pool precedents) until rerun with a fixed ring.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now D.
- **Tier reason:** The hyper-threaded chart is Figure 9 of the peer-reviewed AGERE! 2015 paper (author copy docs/media/papers/fast-cheap.pdf), which on its own would give B. It stays C because the public Pony program does less work than the CAF suite's mixed_case: Pony builds each ring once and discards the factorisation result, while CAF rebuilds every ring on each repetition and sends checked results to a supervisor. CPU, compiler and flags are also unstated.
- **Retiered** C to D: Downgraded from C to D: no valid measurement. The Pony examples/mixed program (at 0.1.4, 0.1.5 as charted, 0.1.7 and main) delivers the 0 token to the master only when pass = 1 mod (size + 1); with its own defaults and with the CAF suite's defaults the token dies at a neighbour after the first repetition and the program quits at quiescence, so Pony did about a quarter to a fifth of CAF's work, which matches the 4.4x gap at 1 core (fc_malloc and dp::thread_pool precedents).
- **Verifier notes:** Kept at C. The peer-reviewed AGERE! 2015 paper (Figure 9) carries the chart, but the Pony and CAF programs do unequal work: Pony skips ring re-creation per repetition and drops the factorisation result. The 64-thread figure was corrected: CAF is about 30 at its last point, so the gap is about 2.1x there, not 2.4x. Erlang does not merely reach parity; CAF overtakes it near 48 threads. Shortcomings: unequal work (same_algorithm false), flags and CPU unknown, decade-old versions, weak CAF 0.13 baseline, first-party authors.
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
  - <https://raw.githubusercontent.com/ponylang/ponyc/main/examples/actors/mixed/main.pony>
  - <https://raw.githubusercontent.com/ponylang/ponyc/0.1.7/examples/mixed/main.pony>
  - <https://raw.githubusercontent.com/ponylang/ponyc/0.2.1/examples/mixed/main.pony>
  - <https://raw.githubusercontent.com/actor-framework/benchmarks/master/src/caf/mixed_case.cpp>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/ponylang/ponylang-website/main/docs/benchmarks_all.pdf>
  - <https://raw.githubusercontent.com/ponylang/ponylang-website/main/docs/media/papers/fast-cheap.pdf>
  - <https://raw.githubusercontent.com/ponylang/ponyc/main/README.md>
  - <https://raw.githubusercontent.com/ponylang/ponyc/main/BUILD.md>
  - <https://raw.githubusercontent.com/ponylang/ponyc/main/INSTALL.md>
  - <https://raw.githubusercontent.com/ponylang/ponyc/main/CHANGELOG.md>
  - <https://raw.githubusercontent.com/ponylang/ponyc/main/examples/actors/mixed/main.pony>
  - <https://raw.githubusercontent.com/ponylang/ponyc/0.1.7/examples/mixed/main.pony>
  - <https://raw.githubusercontent.com/ponylang/ponyc/0.1.5/examples/mixed/main.pony>
  - <https://raw.githubusercontent.com/ponylang/ponyc/0.1.4/examples/mixed/main.pony>
  - <https://raw.githubusercontent.com/ponylang/ponyc/main/src/libponyrt/actor/messageq.c>
  - <https://raw.githubusercontent.com/ponylang/ponyc/0.1.7/src/libponyrt/actor/messageq.c>
  - <https://raw.githubusercontent.com/ponylang/ponyc/main/src/libponyrt/actor/actor.c>
  - <https://raw.githubusercontent.com/ponylang/ponyc/main/src/libponyrt/sched/scheduler.c>
  - <https://raw.githubusercontent.com/ponylang/ponyc/main/src/libponyrt/sched/start.c>
  - <https://raw.githubusercontent.com/ponylang/ponyc/main/src/libponyc/options/options.c>
  - <https://raw.githubusercontent.com/actor-framework/benchmarks/master/src/caf/mixed_case.cpp>
  - <https://raw.githubusercontent.com/actor-framework/benchmarks/master/README.md>
  - <https://raw.githubusercontent.com/actor-framework/benchmarks/master/CMakeLists.txt>
  - <https://raw.githubusercontent.com/actor-framework/benchmarks/master/configure>
  - <https://raw.githubusercontent.com/actor-framework/benchmarks/master/src/caf/CMakeLists.txt>
  - <https://raw.githubusercontent.com/actor-framework/benchmarks/master/scripts/activate_cores>
  - <https://raw.githubusercontent.com/actor-framework/benchmarks/master/src/scripts/run.in>
  - <https://raw.githubusercontent.com/actor-framework/benchmarks/master/src/scripts/caf_run_benchmarks.in>
  - <https://github.com/actor-framework/benchmarks/commits/master/src/scripts/caf_run_benchmarks.in>
  - <https://github.com/ponylang/ponyc/issues?q=is%3Aissue%20mailbox%20OR%20backpressure%20performance>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:pony/ponylang/ponylang-website#message-ring-factorisation`) · [data/wave14/enrich/raw/lang_pony_ponylang_ponylang_website_message_ring_factorisation.json](../../../data/wave14/enrich/raw/lang_pony_ponylang_ponylang_website_message_ring_factorisation.json) (enrichment confidence 0.2)

</details>
