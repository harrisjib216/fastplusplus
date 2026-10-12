# Lingua Franca (reactor language, C++ runtime) on the Savina actor benchmarks vs CAF

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Concurrency runtimes](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Lingua Franca (code generator targeting C++ and C)` · `BSD-2-Clause` · 🟡 mixed

> Deterministic reactor language whose generated C++ (reactor-cpp runtime) ran the ported Savina suite faster than CAF and Akka.

| | |
|---|---|
| **Beats** | CAF (C++ Actor Framework) running the same Savina benchmarks; Akka (JVM) is the second baseline |
| **Claimed result** | Not on any page opened. From the abstract of the ACM TACO 2023 paper 'High-Performance Deterministic Concurrency using Lingua Franca', seen only as web search snippets (arXiv, ACM and mirrors were blocked): LF is about 1.42x faster than CAF and about 1.85-1.86x faster than Akka over the Savina suite at 20 threads, with LF behind CAF on Ping Pong and Thread Ring, ahead on Fork Join and Chameneos, and roughly on par on the parallelism benchmarks. |
| **Workload** | Savina actor benchmark suite ported to Lingua Franca reactors (micro-benchmarks such as Ping Pong, Thread Ring, Counting, Fork Join, Big, Chameneos plus concurrency and parallelism benchmarks), execution time at a given number of worker threads. |
| **Metric** | throughput |
| **Compiler and flags** | Paper flags not seen. From the public build sources: the LF C++ benchmarks declare target Cpp { build-type: Release, no-runtime-validation: true, fast: true } (Cpp/Savina/src/micro/PingPong.lf), i.e. CMake Release (-O3 -DNDEBUG); the CAF baseline programs (lf-lang/savina CMakeLists.txt) and CAF 0.16.5 itself both default CMAKE_BUILD_TYPE to RelWithDebInfo (-O2 -g level) and the README build commands pass no build type, so a build that follows the README compares LF at -O3 against CAF at -O2. Compiler and version not stated. |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | not stated |
| **Adoption** | 329 stars (lingua-franca); benchmark repo lf-lang/benchmarks-lingua-franca has 4 stars |
| **Last commit** | 2026-09-26 |
| **Links** | [repository](https://github.com/lf-lang/lingua-franca) · [benchmark](https://arxiv.org/abs/2301.02444) |

## Verdict

Per web-search snippets of the ACM TACO 2023 paper (not opened here; arXiv, cfaed.tu-dresden.de and fis.tu-dresden.de unreachable), LF's C++ target averaged about 1.42x faster than CAF and 1.86x faster than Akka over the Savina benchmarks it could port, losing to CAF on Ping Pong and Thread Ring. The public harness pins Akka 2.6.17 (lf-lang/savina pom.xml) and CAF 0.16.5 (benchmark README), but CPU, compiler, thread count and aggregation could not be confirmed, and the baselines' timed regions include actor-system startup and teardown that LF's do not.

## Use it when

- New concurrent C++ code with a fixed set of components and connections where reproducible, deterministic behaviour (testable, replayable) matters as much as throughput.
- Pipelines and fan-out/fan-in workloads that map onto a static reactor graph, where broadcast connections replace per-receiver message copies.
- Embedded or cyber-physical systems that need explicit logical timing alongside multicore execution (the C target and reactor-uc cover small devices).
- Teams willing to adopt the lfc toolchain (Java-based code generator) and write reaction bodies inside .lf files.

## Skip it when

- Workloads that create actors dynamically (Fibonacci, Quicksort, Fork Join create): the snippet-reported paper results cover only the benchmarks expressible as static graphs, and LF reactor graphs are fixed at startup apart from the unfinished mutations work (reactor-cpp issue #61, open).
- Latency-bound two-party message exchange: the paper (snippet) reports LF behind CAF on Ping Pong and Thread Ring.
- Long-lived production C++ services: reactor-cpp, the C++ runtime behind these numbers, has carried a 'currently not actively maintained' banner since 2025-05-20 (contributors moved to the Xronos SDK fork and reactor-uc).
- Existing CAF or Akka code bases: there is no migration path; every actor must be rewritten as a reactor with declared ports.
- Distributed actor systems that rely on location transparency or supervision trees; LF federations are a different model.

## How it is fast

reactor-cpp schedules reactions of a statically known dependency graph on a worker pool, tag by tag: reactions at the same logical tag that are not ordered by the graph run in parallel, and no per-message mailbox or dynamic actor creation is needed. Fan-out goes through connections rather than messages: in the Fork Join throughput port one set() on a void output broadcast via (producer.outMessage)+ triggers all 60 worker reactions, where CAF enqueues 600,000 individual message_t objects into 60 mailboxes. Benchmarks build with build-type Release and no-runtime-validation (runtime checks compiled out), and PingPong adds fast: true.

## Compared with alternatives

Pick LF over the Pony actor entries when you want C++ reaction code and deterministic, testable concurrency on a static component graph; Pony (and CAF itself) fit better when actors are created dynamically or message order nondeterminism is acceptable. Against Tokio or goroutine entries it is a different model (logical-time reactors, not async tasks) and only makes sense if determinism is a requirement.

## Integration

| | |
|---|---|
| **Form** | code generator (lfc) emitting a CMake project linked against the reactor-cpp static library |
| **Dependencies** | lfc (Java toolchain), CMake, reactor-cpp runtime (fetched by the generated build); the comparison harness needs Python with hydra-core, cogapp and pandas, CAF 0.16.5 and a Java 8 JDK for Savina/Akka |
| **Minimum toolchain** | C++17 (reactor-cpp CMakeLists sets CMAKE_CXX_STANDARD 17; its 'Update to C++20' issue #35 was closed on 2025-05-20 with the standard still 17); compiler versions used in the paper not documented |
| **Platforms** | Not documented on the pages opened (the benchmark runner's printSystemInfo has Windows, macOS, Linux and BSD branches, but that only prints the OS name); paper hardware not confirmed |
| **Thread safety** | Deterministic by construction: reactions of one reactor never run concurrently and state is reactor-local; the runtime owns the worker pool (--workers). reactor-cpp issue #34 (sync_shutdown not thread safe) was fixed in 2022. |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness asymmetry in the public code: the CAF timed region is run_iteration(), which constructs and destroys a whole caf::actor_system (spawning and joining the scheduler's max-threads workers) and spawns every actor; the Akka timed region likewise creates a new ActorSystem per iteration and awaits its termination. The LF BenchmarkRunner starts its clock at start.set() with the reactor graph and worker pool already built, so system startup and teardown are charged to the baselines only; the size of this bias was not measured.
- CAF iteration times are truncated to whole milliseconds (duration_cast&lt;std::chrono::milliseconds&gt; before conversion to double) while LF reports fractional milliseconds; the runner's parser takes both at face value.
- Ports are not line-for-line: Fork Join throughput becomes one void broadcast per round to 60 workers instead of 600,000 mailbox messages from the main thread, and PingPong breaks its causality loop with a logical action, so wins partly reflect the reactor model avoiding message traffic the actor versions must perform.
- Build defaults differ: LF ports use CMake Release (-O3 -DNDEBUG) with runtime validation off, while lf-lang/savina's CMakeLists defaults CAF programs to RelWithDebInfo (-O2 -g -fno-omit-frame-pointer); the runner's lf-cpp target also builds against reactor-cpp runtime_version 'master', so a rerun today does not use the paper's runtime revision.

## Known shortcomings

- TACO 2023 numbers (1.86x Akka, 1.42x CAF) seen only in a snippet (arXiv 2301.02444 blocked); only 22 of 30 Savina benchmarks ported; public build defaults are CAF RelWithDebInfo -O2 vs LF Release -O3; the win comes from the C++ reactor runtime, not codegen.
- Crippled baselines in the public harness: the CAF timed region, run_iteration(), constructs and destroys a whole caf::actor_system (spawning and joining the scheduler's max-threads workers) and spawns every actor, and the Akka harness creates a new ActorSystem per iteration and awaits its termination, while the LF BenchmarkRunner starts its clock at start.set() with the reactor graph and worker pool already built, so startup and teardown are charged to the baselines only. CAF iteration times are truncated to whole milliseconds, and the LF Fork Join port sends one broadcast to 60 workers where CAF sends 600,000 mailbox messages. reactor-cpp, the C++ runtime behind the numbers, has been marked unmaintained since 2025-05-20; lf-lang/savina pins Akka 2.6.17. The TACO 2023 paper is still reachable only as snippets. Retiered to D.

## Caveats and trade-offs

Numbers are snippet only: the TACO 2023 paper and its artifact data were not opened (arXiv, par.nsf.gov, cfaed.tu-dresden.de, ar5iv and deepai unreachable), so tier C; snippets agree on 1.86x over Akka and 1.42x over CAF but give no thread count, CPU or aggregation method, and the '20 threads' setting, CAF 0.17.6, Akka 2.6.17 and i9-10900K details could not be confirmed (the benchmark README names CAF 0.16.5). Snippets also say only 22 of the 30 Savina benchmarks were ported to the LF C++ target: benchmarks needing dynamic actor creation (Fork Join creation, Fibonacci, Quicksort and others), A\*-Search and Logistic Map Series (whose CAF version uses a blocking call) are excluded, so the suite average covers only benchmarks LF can express with a static reactor graph. Same-opt-level problem in the public sources: LF benchmarks build with build-type Release (-O3) plus no-runtime-validation, while the lf-lang/savina CAF programs and CAF 0.16.5 default to RelWithDebInfo (-O2) and the README passes no build type; whether the paper overrode this is unknown. The LF ports restructure the Savina programs into reactors with fixed connections (PingPong breaks its causality loop with a logical action), so the work is equivalent but not line-for-line identical to the CAF and Akka versions. The paper's authors built both sides. Both sides are C++ (LF generates C++ against the reactor-cpp runtime), so the win is a runtime and programming-model result, not a code-generation one; the paper also reports LF behind CAF on Ping Pong and Thread Ring and behind Akka on Counting and Big (snippet). The benchmark repo has no LICENSE file; the lingua-franca repo is BSD-2-Clause. [retier] Enricher: harness asymmetry in the public code; the CAF timed region, run_iteration(), constructs and destroys a whole caf::actor_system (spawning and joining the scheduler's max-threads workers) and spawns every actor, and the Akka harness creates a new ActorSystem per iteration and awaits its termination, while the LF BenchmarkRunner starts its clock at start.set() with the reactor graph and worker pool already built. CAF iteration times are truncated to whole milliseconds; the LF Fork Join port sends one broadcast to 60 workers where CAF sends 600,000 mailbox messages. lf-lang/savina pins Akka 2.6.17. The TACO 2023 paper is still reachable only as snippets.

Programs are written in the LF language and compiled by a code generator, so adopting it means a new toolchain; the generated runtime is C or C++, so this is a coordination-language and scheduler claim, not a claim that non-C/C++ machine code is faster. Deterministic semantics restrict some actor patterns (logical time, reactors).

## Maintenance

Lingua Franca itself is active (BSD-2-Clause, commits through 2026-09) and the benchmark repo was touched on 2026-09-20, but the C++ runtime that produced these numbers, reactor-cpp, has been marked unmaintained since 2025-05-20, so treat the C++ target as a research artifact rather than a supported product.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now D.
- **Tier reason:** The 1.86x (Akka) and 1.42x (CAF) figures of the ACM TACO 2023 paper (DOI 10.1145/3617687, arXiv 2301.02444) were seen only in WebSearch snippets; arXiv, par.nsf.gov, cfaed.tu-dresden.de, ar5iv and deepai were all unreachable, and the public harness (lf-lang/benchmarks-lingua-franca runner/ and Cpp/Savina/src, CAF sources in lf-lang/savina) holds no results, CPU model or compiler, so snippet-only paper numbers stay C.
- **Retiered** C to D: Downgraded from C to D: the numbers are snippet-only and the public harness charges actor-system startup and teardown to the baselines only (CAF run_iteration() constructs and destroys a whole caf::actor_system and the Akka harness creates a new ActorSystem per iteration, while the LF BenchmarkRunner starts its clock with the reactor graph and worker pool already built), CAF times are truncated to whole milliseconds, and the LF Fork Join port sends one broadcast to 60 workers where CAF sends 600,000 mailbox messages. Crippled baseline with no valid measurement; reactor-cpp is unmaintained since 2025-05-20.
- **Verifier notes:** Kept at C: numbers from TACO 2023 snippets only, benchmark_url set to the arXiv abstract (not opened, egress blocked). Shortcomings to record: snippet-only numbers; only 22 of 30 Savina benchmarks (dynamic-creation ones excluded); public build defaults put CAF at RelWithDebInfo -O2 against LF Release -O3 (same_opt_level false); win comes from the C++ reactor runtime, not the language's codegen.
- **Fields the verifier corrected:** `benchmark_url`, `compiler_and_flags`, `caveats`, `maintenance_status`
- **Shortcomings recorded by:** verifier batch-45 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/lf-lang/benchmarks-lingua-franca>
  - <https://raw.githubusercontent.com/lf-lang/benchmarks-lingua-franca/HEAD/README.md>
  - <https://github.com/lf-lang/benchmarks-lingua-franca/tree/main/runner/conf/target>
  - <https://raw.githubusercontent.com/lf-lang/benchmarks-lingua-franca/main/runner/conf/target/caf.yaml>
  - <https://raw.githubusercontent.com/lf-lang/benchmarks-lingua-franca/main/runner/conf/target/lf-cpp.yaml>
  - <https://raw.githubusercontent.com/lf-lang/benchmarks-lingua-franca/main/runner/conf/target/lf-c.yaml>
  - <https://raw.githubusercontent.com/lf-lang/benchmarks-lingua-franca/main/runner/conf/target/akka.yaml>
  - <https://raw.githubusercontent.com/lf-lang/benchmarks-lingua-franca/main/Cpp/Savina/src/micro/PingPong.lf>
  - <https://raw.githubusercontent.com/lf-lang/savina/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/lf-lang/savina/HEAD/README.md>
  - <https://raw.githubusercontent.com/actor-framework/actor-framework/0.16.5/CMakeLists.txt>
  - <https://github.com/lf-lang/lingua-franca>
  - <https://github.com/lf-lang/lingua-franca/commits>
  - <https://raw.githubusercontent.com/lf-lang/lingua-franca/HEAD/LICENSE.md>
  - <https://github.com/lf-lang/lingua-franca/wiki/Benchmarks>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/lf-lang/benchmarks-lingua-franca/main/README.md>
  - <https://raw.githubusercontent.com/lf-lang/benchmarks-lingua-franca/main/runner/conf/target/caf.yaml>
  - <https://raw.githubusercontent.com/lf-lang/benchmarks-lingua-franca/main/runner/conf/target/lf-cpp.yaml>
  - <https://raw.githubusercontent.com/lf-lang/benchmarks-lingua-franca/main/runner/conf/target/akka.yaml>
  - <https://raw.githubusercontent.com/lf-lang/benchmarks-lingua-franca/main/runner/parser.py>
  - <https://raw.githubusercontent.com/lf-lang/benchmarks-lingua-franca/main/runner/run_benchmark.py>
  - <https://raw.githubusercontent.com/lf-lang/benchmarks-lingua-franca/main/runner/conf/default.yaml>
  - <https://raw.githubusercontent.com/lf-lang/benchmarks-lingua-franca/main/runner/conf/problem_size/large.yaml>
  - <https://raw.githubusercontent.com/lf-lang/benchmarks-lingua-franca/main/runner/conf/benchmark/savina_micro_pingpong.yaml>
  - <https://raw.githubusercontent.com/lf-lang/benchmarks-lingua-franca/main/Cpp/Savina/src/BenchmarkRunner.lf>
  - <https://raw.githubusercontent.com/lf-lang/benchmarks-lingua-franca/main/Cpp/Savina/src/micro/PingPong.lf>
  - <https://raw.githubusercontent.com/lf-lang/benchmarks-lingua-franca/main/Cpp/Savina/src/micro/Throughput.lf>
  - <https://github.com/lf-lang/benchmarks-lingua-franca>
  - <https://github.com/lf-lang/benchmarks-lingua-franca/commits/main>
  - <https://github.com/lf-lang/benchmarks-lingua-franca/tree/main/Cpp/Savina/src>
  - <https://github.com/lf-lang/benchmarks-lingua-franca/tree/main/Cpp/Savina/src/micro>
  - <https://github.com/lf-lang/benchmarks-lingua-franca/tree/main/Cpp/Savina/src/concurrency>
  - <https://github.com/lf-lang/benchmarks-lingua-franca/tree/main/Cpp/Savina/src/parallelism>
  - <https://raw.githubusercontent.com/lf-lang/savina/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/lf-lang/savina/HEAD/README.md>
  - <https://raw.githubusercontent.com/lf-lang/savina/HEAD/pom.xml>
  - <https://raw.githubusercontent.com/lf-lang/savina/HEAD/src/main/cpp/edu/rice/habanero/benchmark.cpp>
  - <https://raw.githubusercontent.com/lf-lang/savina/HEAD/src/main/cpp/edu/rice/habanero/benchmark.hpp>
  - <https://raw.githubusercontent.com/lf-lang/savina/HEAD/src/main/cpp/edu/rice/habanero/benchmark_runner.hpp>
  - <https://raw.githubusercontent.com/lf-lang/savina/HEAD/src/main/cpp/edu/rice/habanero/benchmarks/caf/caf_01_pingpong.cpp>
  - <https://raw.githubusercontent.com/lf-lang/savina/HEAD/src/main/cpp/edu/rice/habanero/benchmarks/caf/caf_03_fjthrput.cpp>
  - <https://raw.githubusercontent.com/lf-lang/savina/HEAD/src/main/scala/edu/rice/habanero/benchmarks/pingpong/PingPongAkkaActorBenchmark.scala>
  - <https://raw.githubusercontent.com/lf-lang/lingua-franca/HEAD/README.md>
  - <https://github.com/lf-lang/lingua-franca>
  - <https://raw.githubusercontent.com/lf-lang/reactor-cpp/HEAD/README.md>
  - <https://raw.githubusercontent.com/lf-lang/reactor-cpp/HEAD/CMakeLists.txt>
  - <https://github.com/lf-lang/reactor-cpp/commits>
  - <https://github.com/lf-lang/reactor-cpp/issues?q=is%3Aissue>
  - https://cfaed.tu-dresden.de/files/Images/people/chair-cc/publications/2309_Menard_TACO.pdf (unreachable, ENOTFOUND)
  - https://fis.tu-dresden.de/portal/en/publications/highperformance-deterministic-concurrency-using-lingua-franca(cd92d8c1-d68d-4f4b-ba07-5c152a6a1c59).html (unreachable, ENOTFOUND)
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:lingua-franca/lf-lang/benchmarks-lingua-franca#savina`) · [data/wave14/enrich/raw/lang_lingua_franca_lf_lang_benchmarks_lingua_franca_savina.json](../../../data/wave14/enrich/raw/lang_lingua_franca_lf_lang_benchmarks_lingua_franca_savina.json) (enrichment confidence 0.35)

</details>
