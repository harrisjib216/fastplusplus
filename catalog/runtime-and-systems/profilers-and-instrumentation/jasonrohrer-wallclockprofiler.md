# wallClockProfiler

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Profilers and instrumentation](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Public-Domain (no_copyright.txt)` · 🟢 active

> Single-file C++ 'poor man's profiler' that drives GDB to sample wall-clock stacks, with far less slowdown than callgrind.

| | |
|---|---|
| **Beats** | Valgrind callgrind |
| **Claimed result** | About 12% slowdown at 20 samples/second versus callgrind about 11x slowdown (160 s versus 14 s). |
| **Workload** | Profiling overhead on the author's own test program (fseek-bound), wall-clock stack sampling via GDB. |
| **Metric** | other |
| **Adoption** | 70 stars |
| **Last commit** | 2026-02-10 |
| **Links** | [repository](https://github.com/jasonrohrer/wallClockProfiler) · [benchmark](https://github.com/jasonrohrer/wallClockProfiler) |

## Verdict

First-party README: on the author's single-threaded fseek-heavy test program (source in testProgram/), sampling at 20 Hz slowed it by about 12%, while valgrind --tool=callgrind --collect-systime=yes ran it 11x slower (160 s vs 14 s). The callgrind output shows an i386 eglibc 2.19 system; CPU, compiler flags and repeat counts are not given.

## Use it when

- Single-threaded Linux programs whose time goes to blocking calls (seeks, sockets, sleeps, lock waits) that on-CPU profilers such as perf or gperftools attribute badly.
- Short-term sampling of a live process that GDB can attach to (often needs root), e.g. a few hundred samples from a loaded server.
- Machines where only g++ and gdb are available: one .cpp file, built with plain g++, no other dependencies.
- Low sampling rates (around 20 Hz) when you are hunting one dominant hotspot; the author reports 12% slowdown at that rate.

## Skip it when

- Multithreaded programs: it lists frames for the current thread only (open issue #7, 'It doesn't work for multithreading').
- Disk-bound code in uninterruptible sleep: GDB cannot stop a process in D state, so those intervals get few or no samples (open issue #12 saw 2 samples instead of about 90 for a 900 ms 1 GB read at 99 Hz).
- High-rate or low-overhead production profiling: every sample is a full ptrace stop plus a GDB MI round trip; perf-style or eBPF samplers cost far less per sample.
- When you need exact call counts or instruction-level cost: the output is a sample histogram, not callgrind-style exact counts.

## How it is fast

It does not instrument or emulate the program: the target runs natively and is stopped only at each sample. The loop is usleep(1e6/rate), then -exec-interrupt or kill(pid, SIGINT), -stack-list-frames over GDB's MI interface, then -exec-continue. Overhead therefore scales with the sampling rate rather than with instructions executed, which is why it is far cheaper than callgrind's dynamic binary translation.

## Compared with alternatives

Pick it over magic-trace or Coz when you have only gdb and g++ on a box, want blocking time attributed to call stacks, and the target is single-threaded. magic-trace (Intel PT, 2-10% overhead) and Coz (causal estimates for multithreaded code) are stronger tools when their requirements are met.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | gdb on PATH (run with --interpreter=mi), pidof, POSIX/Linux headers |
| **Minimum toolchain** | any g++ (README: g++ -o wallClockProfiler wallClockProfiler.cpp); no standard version stated |
| **Platforms** | Linux (fork/pipe/kill, pidof, GDB); other platforms not documented |
| **Thread safety** | not applicable (CLI); samples only the target's current thread |
| **Drop-in for the baseline** | partial — it replaces callgrind for 'where does the time go' questions, with sampled wall-clock stacks instead of exact instruction counts |

## Gotchas

- In direct-run mode it finds the target with pidof &lt;name&gt; and takes the first PID printed, so another process with the same name can be picked.
- The real sample rate is below the requested one: the interval is usleep plus the GDB interrupt/stack/continue round trip, not a fixed timer.
- The target sees SIGINT on each sample in direct-run mode; programs with their own SIGINT handlers or other signals need --ignore= (added in December 2025 and February 2026 commits).
- Per-function totals add a stack's count once for every frame naming that function, so recursive functions can show more than 100%.

## Known shortcomings

- Samples the current thread only (issue 7) and misses disk I/O in D state (issue 12: 2 samples against about 90 expected), which weakens the wall-clock claim; direct-run mode picks its target via the first pidof PID. Test program source is in testProgram/.

## Caveats and trade-offs

Single synthetic fseek-bound test program, no hardware or compiler flags stated, first-party only; the 12% figure and the callgrind 160 s vs 14 s figure are separate statements rather than one side-by-side table. Overhead of the two tools differs by design (sampling rate versus exact tracing). Public-domain dedication (no_copyright.txt) carries no patent grant.

Samples through GDB so each sample stops the process; wall-clock sampling shows I/O waits that CPU-cycle profilers miss.

## Maintenance

Lightly maintained (last commits 2026-02-10, merging signal-ignore PRs; five issues open, including multithreading and D-state sampling) and public domain via no_copyright.txt, so the single file is easy to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** README states a 12% slowdown at 20 samples/second on the author's test program and that callgrind (valgrind --tool=callgrind --collect-systime=yes) made it run 11x slower (160 s vs 14 s); first-party, test program source not in README, no CPU or flags beyond plain g++ build, so C.
- **Verifier notes:** Numbers match README; no_copyright.txt confirmed ('This work is not copyrighted. I place it into the public domain.'). Last commit date not re-checked.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** code reading by enricher
- **Pages the verifier opened:**
  - <https://github.com/jasonrohrer/wallClockProfiler>
  - <https://raw.githubusercontent.com/jasonrohrer/wallClockProfiler/HEAD/README.md>
  - <https://raw.githubusercontent.com/jasonrohrer/wallClockProfiler/HEAD/no_copyright.txt>
- **Sources the enricher read:**
  - <https://github.com/jasonrohrer/wallClockProfiler>
  - <https://raw.githubusercontent.com/jasonrohrer/wallClockProfiler/HEAD/README.md>
  - <https://raw.githubusercontent.com/jasonrohrer/wallClockProfiler/HEAD/wallClockProfiler.cpp>
  - <https://github.com/jasonrohrer/wallClockProfiler/commits>
  - <https://github.com/jasonrohrer/wallClockProfiler/issues>
  - <https://github.com/jasonrohrer/wallClockProfiler/issues/12>
  - <https://github.com/jasonrohrer/wallClockProfiler/issues/7>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/jasonrohrer/wallclockprofiler`) · [data/wave11/enrich/raw/github_com_jasonrohrer_wallclockprofiler.json](../../../data/wave11/enrich/raw/github_com_jasonrohrer_wallclockprofiler.json) (enrichment confidence 0.75)

</details>
