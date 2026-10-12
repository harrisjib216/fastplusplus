# Tracy Profiler

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Profilers and instrumentation](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> Hybrid instrumentation plus sampling frame profiler for C/C++ with nanosecond rdtsc timestamps and a remote GUI; no measured win over perf, gprof or Valgrind.

| | |
|---|---|
| **Beats** | No perf, gprof or Valgrind comparison; manual compares profiled versus unprofiled run only |
| **Claimed result** | No speedup claim against another profiler; the manual's 2.25 ns per zone is a wall-time difference divided by 16,777,216 zones while 12 threads run in parallel, so the real per-thread cost is about 27 ns per zone (derived from page data; issue 192 reports 28-29 ns per span on a Ryzen 9 3950X, GCC 9.3 -O3) |
| **Workload** | etcpak compressing a 16384x16384 test image on 12 threads with the 4x4 block compression function instrumented (16777216 zones per image); mean single-image time, clean run versus profiling run, ETC1 and ETC2 modes. |
| **Metric** | latency |
| **Adoption** | 16.9k stars |
| **Last commit** | 2026-10-03 |
| **Links** | [repository](https://github.com/wolfpld/tracy) · [benchmark](https://github.com/wolfpld/tracy/blob/master/manual/tracy.tex) |

## Verdict

First-party manual table: etcpak compressing a 16384x16384 image on 12 threads with the 4x4 block function instrumented (16777216 zones per image) took 110.9 vs 148.2 ms (ETC1) and 212.4 vs 250.5 ms (ETC2) clean versus profiled, which the manual reports as 2.25 ns per zone; compiler, flags and CPU are not stated and no other profiler was measured. Because the division uses wall time across 12 parallel threads, the per-thread cost is closer to 27 ns per zone (derived from page data), consistent with an independent 28-29 ns report.

## Use it when

- Games and other frame-based real-time apps where you need to see which frame stuttered and why, across threads, not just aggregate hot spots
- Native C/C++ (also C API, Lua, Python, Fortran) code you can rebuild with TRACY_ENABLE and zone macros
- Profiling on a remote or mobile device (Android, iOS, consoles via platform layer) with the viewer on a desktop
- Correlating CPU zones with GPU work, lock contention, allocations and context switches in one timeline
- Long captures with millions of zones where per-event cost of tens of ns is acceptable

## Skip it when

- You cannot rebuild or annotate the binary and only want whole-program sampling: perf or a pure sampler needs no build change
- Very fine-grained zones (sub-100 ns functions) where an event cost of roughly 25-30 ns per zone (issue #192; derived figure below) distorts what you measure
- Virtual machines or cloud instances: the manual warns of reduced timestamp precision and missing invariant TSC
- macOS/iOS: the manual says the overhead is higher, TRACY_NO_EXIT is unsupported and OpenGL cannot be profiled
- Hard limits matter: 65534 source locations, 64 threads per lock, 1.6-day sessions, 16 million unique call stacks, little-endian 48-bit address space only

## How it is fast

Each zone begin/end writes a 32-byte item into a thread-local 128-item queue buffer with an inline rdtsc timestamp and a pointer to a static source-location struct; the manual's x64 listing shows about 20 instructions and no locks on the hot path. Heavy work (string resolution, compression, symbol lookup) is deferred to a background thread and to the server, which also reduces network bandwidth.

## Compared with alternatives

Pick Tracy over Palanteer or MicroProfiler when you need GPU zones, broad platform coverage and a mature viewer; pick funtrace when you want automatic function-level tracing under 10 ns per call, and magic-trace or perf when you cannot add instrumentation.

## Integration

| | |
|---|---|
| **Form** | source-drop (add public/TracyClient.cpp, or CMake/Meson target Tracy::TracyClient as static or shared lib); viewer is a separate CMake-built app |
| **Dependencies** | client: none beyond pthread and libdl on Unix (libexecinfo on BSD; optional libunwind, libdebuginfod); server build needs network and git at CMake configure time to fetch its libraries |
| **Minimum toolchain** | C++11; MSVC, GCC or Clang (MSVC Edit and Continue /ZI must be off) |
| **Platforms** | Windows (x86, x64, ARM64), Linux (x86, x64, ARM, ARM64), Android, FreeBSD, WSL, macOS x64, iOS, QNX; x86 needs invariant rdtsc (Sandy Bridge or later); little-endian only |
| **Thread safety** | Client zones are recorded into per-thread queues and are safe from any thread; lock markup supports up to 64 threads per lock. dbghelp Sym\* calls on Windows must be serialized with Tracy's (manual). |
| **Drop-in for the baseline** | partial — sampling works without markup, but the main instrumentation mode needs TRACY_ENABLE builds and source macros, unlike perf/gprof |

## Gotchas

- The manual's 2.25 ns per zone is wall-clock difference divided by zones while 12 threads ran in parallel; per-thread cost is about 12x that, roughly 27 ns per zone (derived from page data), which matches the 28-29 ns per span a user measured on a Ryzen 9 3950X with GCC 9.3 -O3 -flto -march=native (issue #192, open, rdtsc about 70% of time).
- Without TRACY_ON_DEMAND the client buffers all events in memory until a viewer connects and never releases that memory (can reach gigabytes); on-demand mode adds bookkeeping cost per event.
- TRACY_ENABLE must be defined for every translation unit; TRACY_ENABLE=0 still enables it because only definedness is checked.
- ON_DEMAND with a static TracyLockable deadlocked during static initialization (issue #775, closed); the client also listens on all interfaces and broadcasts on the LAN by default (TRACY_ONLY_LOCALHOST, TRACY_NO_BROADCAST).

## Known shortcomings

- No external baseline: the manual compares only profiled against unprofiled runs (2.25 ns per zone, etcpak); the overhead table names no CPU or flags. Kept as a notable project (16.9k stars, BSD-3-Clause).
- The manual's 2.25 ns per zone divides a wall-time difference (37.7 ms) by 16,777,216 zones while 12 threads run in parallel; the real per-thread cost is about 27 ns per zone (derived from page data), matching issue 192 (28-29 ns per span on a Ryzen 9 3950X, GCC 9.3 -O3). The headline is overstated about 12x. Issue 775 (ON_DEMAND static TracyLockable deadlock, closed); events are buffered without bound until the viewer connects.

## Caveats and trade-offs

No named baseline from perf, gprof or Valgrind is measured; overhead is relative to the unprofiled program only. The manual's overhead table does not state compiler, flags or CPU (the Ryzen 9 3900X/MSVC note belongs to a separate client compression table). Third-party per-zone figures that differ from 2.25 ns were not verified. [retier] Headline 2.25 ns/zone is overstated about 12x (12 threads in parallel); no external baseline (profiled vs unprofiled only); issue 775 ON_DEMAND static TracyLockable deadlock (closed); events are buffered without bound until the viewer connects.

Instrumentation (zones) plus sampling; needs source macros for zones; network server/viewer architecture.

## Maintenance

Very actively maintained (commits in October 2026, 16.9k stars), BSD-3-Clause and copyable; the master branch is the development line with no stability guarantee, so pin a release tag and keep client and viewer versions matched because the network protocol changes between releases.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): reject; tier before verification C, tier now C.
- **Tier reason:** Manual section 'Performance impact' gives first-party clean vs profiling run times for etcpak (ETC1 110.9 vs 148.2 ms, ETC2 212.4 vs 250.5 ms, 16777216 zones per image), giving 2.25 ns per zone; no compiler, flags or CPU stated for this table and no comparison with perf, gprof, Valgrind or any other profiler, so at most C.
- **Verifier notes:** Reject is strictly for no baseline comparison (only profiled vs unprofiled); Tracy is highly notable (16.9k stars, BSD-3-Clause confirmed from LICENSE), so the orchestrator may override to keep with this shortcoming per the keep-and-document rule. Last commit date not re-checked.
- **Fields the verifier corrected:** `workload`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** first-party manual and issue
- **Pages the verifier opened:**
  - <https://github.com/wolfpld/tracy>
  - <https://raw.githubusercontent.com/wolfpld/tracy/master/manual/tracy.tex>
  - <https://raw.githubusercontent.com/wolfpld/tracy/master/LICENSE>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/wolfpld/tracy/HEAD/README.md>
  - <https://raw.githubusercontent.com/wolfpld/tracy/master/manual/tracy.tex>
  - <https://github.com/wolfpld/tracy/issues?q=is%3Aissue+overhead>
  - <https://github.com/wolfpld/tracy/issues/192>
  - <https://github.com/wolfpld/tracy/issues/775>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/wolfpld/tracy`) · [data/wave11/enrich/raw/github_com_wolfpld_tracy.json](../../../data/wave11/enrich/raw/github_com_wolfpld_tracy.json) (enrichment confidence 0.75)

</details>
