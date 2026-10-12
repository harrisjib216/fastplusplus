# Coz causal profiler

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Profilers and instrumentation](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `BSD-2-Clause` · 🟢 active

> Causal profiler for C/C++/Rust that predicts the whole-program effect of speeding up each line; far lower overhead than gprof.

| | |
|---|---|
| **Beats** | gprof |
| **Claimed result** | Paper (CACM 2018 version of SOSP 2015): Coz profiling overhead on PARSEC averages 17.6% (minimum 0.1%, maximum 65%), under 30% for all but three benchmarks; 'the widely used gprof profiler can impose much higher overhead (e.g., 6 times for ferret, versus 6% with Coz)'. |
| **Workload** | Profiling overhead of Coz on the PARSEC benchmarks with native inputs (startup, sampling and virtual-speedup delay components), with one gprof overhead comparison on ferret; also case studies on Memcached, SQLite and PARSEC. |
| **Metric** | other |
| **Hardware** | 64-core four-socket AMD Opteron, 60 GB RAM, Linux 3.14 (exact CPU model not stated) |
| **Compiler and flags** | GCC 4.9.1, -O3 -g -fno-omit-frame-pointer |
| **Adoption** | 4.6k stars; SOSP 2015 best paper |
| **Last commit** | 2026-07-10 |
| **Links** | [repository](https://github.com/plasma-umass/coz) · [benchmark](https://github.com/emeryberger/publications/blob/master/Coz-cacm2018.pdf) |

## Verdict

In the CACM 2018 version of the SOSP 2015 paper (GCC 4.9.1 -O3 -g -fno-omit-frame-pointer, 64-core four-socket AMD Opteron, 60 GB, Linux 3.14), Coz's overhead on PARSEC native inputs averaged 17.6% (min 0.1%, max 65%, under 30% for all but three), and the sole gprof comparison is one sentence: gprof can cost about 6x on ferret versus 6% for Coz. Prediction accuracy was checked on two cases (dedup predicted 9% vs 8.95% observed; ferret 21.4% vs 21.2%).

## Use it when

- Multithreaded or pipelined C/C++/Rust servers and batch jobs where flat profiles mislead because of contention, critical paths or idle waiting (paper case studies: Memcached +9%, SQLite +25%, six PARSEC apps by up to 68% after Coz-guided fixes).
- Long-running throughput workloads with a clear unit of work (request, query, frame) that can carry a progress point.
- Latency questions about one transaction type, using COZ_BEGIN/COZ_END pairs.
- When gprof's instrumentation overhead is unacceptable or it fails outright (paper: gprof about 6x on ferret vs 6% with Coz; gprof segfaults on SQLite).
- Linux x86-64 or aarch64 hosts where perf_event_paranoid can be lowered to 1.

## Skip it when

- Short programs or code without an obvious progress point: Coz needs many experiments to build a profile and the README says sample apps may need several runs.
- Interpreted or JIT languages (Python, Ruby, JavaScript); README says interpreted languages will likely never be supported.
- Windows or WSL 2 (open issues #163 and #216), locked-down containers that forbid perf_event_open, or macOS where the private kperf API needs elevated privileges or SIP changes.
- Code dominated by usleep or mmap page faults: open issues #231 (incorrect predictions with usleep) and #223 (samples not counted during mmap).
- Rust release builds in some setups: open issues #180, #193 and #197 report silent failure, DWARF format errors and random lines.

## How it is fast

Overhead stays low because Coz never instruments functions: it samples instruction pointers per thread with perf_event_open (Linux) or kperf (macOS) every 1 ms and processes samples in batches of ten. 'Virtual speedups' are made by pausing all other threads whenever the chosen line is sampled, so speeding up one line is emulated by slowing everything else, and progress-point counters are relaxed atomic increments. In the paper, the 17.6% average overhead on PARSEC splits into 2.6% startup (DWARF parsing), 4.8% sampling and 10.2% inserted delays.

## Compared with alternatives

Pick Coz when you want to know which line is worth optimizing in a concurrent program; Tracy, Palanteer and funtrace instrument zones or calls to show timelines, magic-trace gives Intel PT traces, and wallClockProfiler gives cheap wall-clock stack samples, but none of them predicts the end-to-end effect of a speedup.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | libelfin (fetched by CMake from plasma-umass/libelfin), libdl, Python 3 for the coz CLI/viewer; optional LLM API keys only for the suggestion features |
| **Minimum toolchain** | C++11, CMake 3.13; Linux kernel 2.6.32+ with perf_event_open |
| **Platforms** | Linux x86-64 and aarch64 (deb/rpm packages), macOS via kperf; no Windows |
| **Thread safety** | Designed for multithreaded programs: intercepts pthread_create and pthread blocking calls; progress-point counters use relaxed atomics |
| **Drop-in for the baseline** | partial — unlike gprof it needs no -pg rebuild and runs on a -g binary, but useful output requires adding progress-point macros and the output is a causal profile, not a flat profile or call graph |

## Gotchas

- Lower /proc/sys/kernel/perf_event_paranoid to 1 before profiling on Linux, or sampling does not work.
- Build with -g (DWARF 5 is supported) and preferably -fno-omit-frame-pointer, which the paper used for accurate callchains; samples outside in-scope files are attributed to the last in-scope call site.
- coz.h finds libcoz through a weak dlsym reference, so macros are no-ops when the program runs without coz; link with -ldl as the README instructs.
- Command-line progress points are disabled ('did not work particularly well'); the newer `coz suggest-points` and viewer assistant send source code to an external LLM provider unless Ollama is used.
- Benchmark sample apps (Phoenix, pbzip2) carry their own licenses, separate from the BSD-2-Clause core.

## Known shortcomings

- Overhead of 17.6% on average is 2.6 startup plus 4.8 sampling plus 10.2 delays; the gprof comparison is a single sentence (ferret: 6x against 6%). Open issues: 231 (usleep gives wrong predictions), 223 (mmap samples lost), 216 (WSL2), and Rust issues 180, 193 and 197.

## Caveats and trade-offs

The gprof comparison is one data point (ferret: gprof about 6x overhead vs 6% for Coz), not a systematic overhead study; the paper also says gprof segfaults on SQLite. Coz is a causal profiler, so its output differs from a gprof profile; the claim is about lower overhead, not a like-for-like profile. 2015 results on GCC 4.9.1 and Linux 3.14. The repo README has no comparative numbers. Sample apps in benchmarks/ (Phoenix, pbzip2) are licensed separately from the BSD-2-Clause core.

Needs progress points in source (or latency points) and debug info; Linux and macOS; Python 3 for the viewer; it answers a different question (what to optimize) than gprof or perf.

## Maintenance

Active (last commit 2026-07-10, 4.6k stars, 43 open issues), BSD-2-Clause with prebuilt deb/rpm/tarball releases; usable as a tool, and coz.h is copyable into any project.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now B.
- **Tier reason:** The peer-reviewed paper (CACM 2018 research-highlight version of the SOSP 2015 paper, read from emeryberger/publications) states Coz's overhead on PARSEC is 17.6% on average (min 0.1%, max 65%) and that gprof can impose much higher overhead (6 times for ferret, versus 6% with Coz). The setup gives GCC 4.9.1 -O3 -g -fno-omit-frame-pointer on a 64-core four-socket AMD Opteron, but no exact CPU model and only a single gprof data point, so B not A.
- **Verifier notes:** Paper PDF reached at raw.githubusercontent.com/emeryberger/publications/HEAD/Coz-cacm2018.pdf (the SOSP PDF there has no text layer). Metadata on github.com: BSD 2-clause, 4.6k stars, last commit 2026-07-10.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** peer-reviewed paper, read from a repo copy
- **Pages the verifier opened:**
  - <https://github.com/plasma-umass/coz>
  - <https://github.com/plasma-umass/coz/commits/master>
  - <https://raw.githubusercontent.com/plasma-umass/coz/HEAD/README.md>
  - <https://github.com/emeryberger/publications>
  - <https://raw.githubusercontent.com/emeryberger/publications/HEAD/Coz-sosp2015.pdf>
  - <https://raw.githubusercontent.com/emeryberger/publications/HEAD/Coz-cacm2018.pdf>
- **Sources the enricher read:**
  - <https://github.com/plasma-umass/coz>
  - <https://raw.githubusercontent.com/plasma-umass/coz/HEAD/README.md>
  - <https://raw.githubusercontent.com/plasma-umass/coz/HEAD/include/coz.h>
  - <https://raw.githubusercontent.com/plasma-umass/coz/HEAD/CMakeLists.txt>
  - <https://github.com/plasma-umass/coz/issues>
  - <https://raw.githubusercontent.com/emeryberger/publications/HEAD/Coz-cacm2018.pdf>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/plasma-umass/coz`) · [data/wave11/enrich/raw/github_com_plasma_umass_coz.json](../../../data/wave11/enrich/raw/github_com_plasma_umass_coz.json) (enrichment confidence 0.75)

</details>
