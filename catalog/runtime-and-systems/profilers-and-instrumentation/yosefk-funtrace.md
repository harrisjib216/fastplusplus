# funtrace

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Profilers and instrumentation](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-2-Clause` · 🟡 stale

> Small flight-recorder function call tracer for C/C++ on x86-64 Linux; author reports 4.5-18x lower per-call cost than XRay and uftrace.

| | |
|---|---|
| **Beats** | LLVM XRay and uftrace function tracers (not perf, gprof or Valgrind) |
| **Claimed result** | &lt;10 ns per instrumented call or return; 6x faster than an XRay microbenchmark (flight recorder logging), 15-18x faster than XRay basic logging, 4.5x faster than a uftrace microbenchmark |
| **Workload** | Per-call/return overhead of compiler-instrumented function tracing in the repo's simple-example microbenchmark. |
| **Metric** | latency |
| **Compiler and flags** | gcc -finstrument-functions / -pg -mfentry -minstrument-return=call; clang -finstrument-functions / -fxray-instrument (flags stated for the instrumented builds, not for the comparison harness) |
| **Adoption** | 201 stars |
| **Last commit** | 2025-03-23 |
| **Links** | [repository](https://github.com/yosefk/funtrace) · [benchmark](https://github.com/yosefk/funtrace) |

## Verdict

The author's own microbenchmark gives under 10 ns per instrumented call or return, 6x faster than an LLVM XRay flight-recorder-logging microbenchmark, 15-18x faster than XRay basic logging and 4.5x faster than uftrace; the README gives no hardware, compiler version or harness, and the repo's simple-example/run.sh runs only funtrace's own four builds, not the XRay/uftrace comparison.

## Use it when

- Debugging tail-latency outliers in a C++ server: time each request with funtrace_time() and keep a snapshot of the slowest one.
- You can rebuild the program with instrumentation flags and want a full call timeline per thread rather than perf's averaged samples.
- You want to read trace data out of a core dump to see what each thread did just before a crash.
- Counting exact call frequencies with the bundled funcount (about as fast as funtrace, thread-safe unlike gprof) to decide what to exclude.
- You need a tracer small enough to audit or port (about 1K LOC runtime, BSD-2-Clause).

## Skip it when

- You cannot recompile, or need to trace a plugin or Python extension loaded by an uninstrumented host: the runtime must be linked into the executable.
- Non-x86-64 or non-Linux targets: the hot path uses __rdtsc and the docs cover x86/Linux only.
- Programs that create and destroy many threads: thread exit takes a global lock (documented), and open issue #4 reports a program going from 32 ms to 5500 ms with pauses on pthread_join.
- Sampling-style whole-program CPU profiles: without culling short hot functions (NOFUNTRACE, -funtrace-instr-thresh) the overhead of tracing every call is large and the 1 MB per-thread buffer covers only about 16K recent calls.
- Statically linked libstdc++ is not handled by the exception hooks (open issue #5 proposes -Wl,-wrap flags).

## How it is fast

The hook is a few instructions: load the thread_local write pointer, AND it with a wraparound mask (the buffer is aligned to twice its size so clearing one bit wraps it, and a zero mask disables tracing with one branch), store a 16-byte {code pointer | flag bits, rdtsc} entry, bump the pointer. There is no locking, no formatting and no syscalls on the hot path, the runtime lives in the executable so TLS access is a register+offset, and the -pg hooks are hand-written assembly that avoid clobbering argument registers. Decoding and symbolization are deferred to the offline funtrace2viz.

## Compared with alternatives

Pick it over Tracy or Palanteer when you want automatic per-function tracing from compiler hooks instead of manual zones, and over magic-trace when you are not on Intel PT hardware or want snapshots triggered from inside the program; bpftime targets uprobe-based instrumentation without recompiling.

## Integration

| | |
|---|---|
| **Form** | source-drop (funtrace.cpp, funtrace_pg.S, funtrace.h) plus compiler wrapper scripts and a Rust decoder |
| **Dependencies** | none at runtime beyond pthreads; decoder built with Rust (or prebuilt release); viztracer for viewing |
| **Minimum toolchain** | stock gcc or clang; XRay shared-library support needs clang with -fxray-shared (late 2024); program must be linked as C++ |
| **Platforms** | x86-64 Linux |
| **Thread safety** | per-thread lock-free buffers; snapshot taking and thread create/exit share one mutex and snapshots pause tracing globally |
| **Drop-in for the baseline** | partial — replaces XRay's runtime hooks (needs --allow-multiple-definition and a linker wrapper) but has its own API and file format; not compatible with uftrace's workflow |

## Gotchas

- Likely cause of the open slowdown issue, found in funtrace.cpp: current_time_ms() divides by cpu_cycles_per_second() on every call instead of the cached cpu_freq. When CPUID leaf 0x15 gives no frequency (ECX=0), that function runs popen("dmesg | grep ..."), and if dmesg yields nothing (restricted dmesg) it sleeps 100 ms; this happens on each thread exit while holding the global mutex, and in the GC thread. The per-call hot path is not affected.
- Tail-call artifacts with gcc -pg and XRay, and 'everyone returned' artifacts when an untraced function catches an exception, except with gcc -finstrument-functions.
- gcc -pg mode cannot link shared objects with -Wl,--no-undefined, and passing -pg to the linker makes the program write gmon.out.
- The -funtrace-instr-thresh / no-trace filters post-process compiler assembly text heuristically; the author flags this as hacky for production. Trace entries can be out of order or missing near the buffer wrap because writeout is racy.

## Known shortcomings

- Thread-exit bug (not on the hot path): current_time_ms() calls cpu_cycles_per_second() every time instead of using the cached cpu_freq. When CPUID 0x15 gives no frequency it runs popen('dmesg | grep ...') and may usleep 100 ms, holding the global mutex on each thread exit and in the GC thread; likely cause of open issue 4 (a 32 ms run becomes 5500 ms, with pauses at pthread_join), though that cause is the enricher's inference and the issue is unanswered. The per-call ns numbers are not affected. Hot path: masked thread_local pointer, 16-byte {ptr, rdtsc} store.

## Caveats and trade-offs

Author's own microbenchmark; comparison numbers are in the README only, hardware not stated; baseline is XRay/uftrace, not perf/gprof/Valgrind; the author notes uftrace has different design goals. The linked blog post was blocked, so only the README was read.

Tracing profiler (timeline of calls), not a sampling profiler; x86-64 Linux; must be told what to trace; trace buffer is a flight recorder so old events are overwritten; needs recompilation with instrumentation flags.

## Maintenance

Stale since 2025-03-23 with two open, unanswered issues (#4 slowdown, #5 static libstdc++), but BSD-2-Clause and small enough to vendor and patch.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The README states &lt;10 ns per instrumented call or return, 6x faster than an LLVM XRay flight-recorder microbenchmark, 15-18x faster than XRay basic logging and 4.5x faster than a uftrace microbenchmark. These are the author's own numbers with no hardware and no published comparison harness, so C.
- **Verifier notes:** The metadata checks out: BSD-2-Clause (LICENSE.txt), 201 stars, not a fork, last commit 2025-03-23, so stale. The simple-example/run.sh in the repo runs the tracer variants but does not run the XRay/uftrace comparison.
- **Shortcomings recorded by:** code reading by enricher
- **Pages the verifier opened:**
  - <https://github.com/yosefk/funtrace>
  - <https://github.com/yosefk/funtrace/commits>
  - <https://raw.githubusercontent.com/yosefk/funtrace/HEAD/README.md>
  - <https://raw.githubusercontent.com/yosefk/funtrace/HEAD/LICENSE.txt>
  - <https://raw.githubusercontent.com/yosefk/funtrace/HEAD/simple-example/run.sh>
- **Sources the enricher read:**
  - <https://github.com/yosefk/funtrace>
  - <https://raw.githubusercontent.com/yosefk/funtrace/HEAD/README.md>
  - <https://raw.githubusercontent.com/yosefk/funtrace/HEAD/funtrace.cpp>
  - <https://raw.githubusercontent.com/yosefk/funtrace/HEAD/simple-example/run.sh>
  - <https://github.com/yosefk/funtrace/issues?q=is%3Aissue>
  - <https://github.com/yosefk/funtrace/issues/4>
  - <https://github.com/yosefk/funtrace/issues/5>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/yosefk/funtrace`) · [data/wave11/enrich/raw/github_com_yosefk_funtrace.json](../../../data/wave11/enrich/raw/github_com_yosefk_funtrace.json) (enrichment confidence 0.75)

</details>
