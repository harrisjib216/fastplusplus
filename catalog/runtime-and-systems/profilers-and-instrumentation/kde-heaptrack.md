# heaptrack

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Profilers and instrumentation](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `GPL-2.0-or-later` · 🟢 active

> Linux heap profiler using LD_PRELOAD and libunwind; much lower time and memory overhead than Valgrind massif (no published numbers).

| | |
|---|---|
| **Beats** | Valgrind Massif |
| **Claimed result** | No numbers in README: 'speed and memory overhead' of heaptrack is significantly lower than massif, multi-threaded apps not serialized, CPU-bound code not slowed |
| **Workload** | Heap allocation profiling with stack traces, compared qualitatively with Valgrind massif on larger real-world applications. |
| **Metric** | throughput |
| **Adoption** | 4.2k stars |
| **Last commit** | 2026-10-02 |
| **Links** | [repository](https://github.com/KDE/heaptrack) · [benchmark](https://github.com/KDE/heaptrack) |

## Verdict

No measurement exists: the README only says heaptrack's time and memory overhead is 'significantly lower' than Valgrind massif, that it does not serialize threads and that it does not slow non-allocating CPU work. The author's blog post (found by search, not opened) gives only rough estimates, so the tier stays D.

## Use it when

- Heap profiling of large or long-running multi-threaded C/C++ (or Rust/D) applications on Linux that are impractical to run under massif's serialization.
- Finding allocation hotspots and temporary allocations (malloc directly followed by free), which massif's pre-aggregated output cannot show.
- Attaching to an already running process to see what is allocating right now (needs gdb).
- Embedded targets: record a raw trace with --raw on the device and interpret it on a host with --sysroot and debug paths.
- CPU-heavy code with few allocations, where heaptrack adds almost nothing because it only intercepts allocator calls.

## Skip it when

- Allocation-heavy hot loops: every malloc/free takes a global lock, unwinds the stack and writes a line, so programs that allocate millions of times per second still slow down noticeably (no overhead numbers are published).
- Pool or arena allocators that bypass malloc, or page-level and stack accounting: massif's --pages-as-heap and stack profiling cover these, while heaptrack needs code annotations and cannot profile the stack.
- Non-Linux targets: the collector is Linux-only (FreeBSD has code paths); only heaptrack_print and heaptrack_gui build on macOS.
- Binaries built with clang's ASan (unsupported), or code linked with old gold linkers, where libunwind produces bogus backtraces that crash the GUI with out-of-memory.
- Hour-long captures you need to browse quickly: the data format cannot be seeked, so large profiles load slowly and zooming the timeline reloads them.

## How it is fast

The application runs natively instead of on Valgrind's serializing JIT: a preload library interposes malloc, free, calloc, realloc, posix_memalign, aligned_alloc, valloc, dlopen and dlclose, plus mimalloc and Boehm GC hooks, through dlsym(RTLD_NEXT), so only allocation calls pay any cost. Each event captures a backtrace with libunwind's unw_backtrace using a per-thread unwind cache (cache size 1024), deduplicates it into a TraceTree of instruction pointers (sorted children, binary-searched) and emits one compact hex line (+ size index ptr / - ptr) to a pipe. Symbolization and aggregation happen later in the separate heaptrack_interpret process, and a timer thread samples timestamps and RSS from /proc/self/statm.

## Compared with alternatives

Choose heaptrack over bytehound when you want a mature, distro-packaged C/C++ heap profiler with a GUI and an attach mode; bytehound claims cheaper unwinding but likewise publishes no numbers. Choose it over memtrail or heapusage when you need full allocation timelines and flame graphs rather than just leak reports.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | collector: libunwind (or unwind tables), Boost iostreams and program_options, zlib, optionally zstd, elfutils, libdl, pthread, gdb for attach; GUI: Qt 6.5+, KDE Frameworks, optional KDiagram |
| **Minimum toolchain** | C++17 and CMake 3.16 per CMakeLists.txt (the README's C++11, CMake 2.8.9 and Qt 5 lines are out of date) |
| **Platforms** | Linux (x86-64, ARM, embedded via --raw); analyzers also build on macOS |
| **Thread safety** | Safe for multi-threaded targets: one global timed mutex serializes allocation event recording, and a thread_local RecursionGuard prevents re-entry; pthread_atfork handlers cover forking. |
| **Drop-in for the baseline** | partial: replaces massif as a workflow (run the app under heaptrack instead of valgrind --tool=massif, and heaptrack_print can export massif format), but it does not do page-as-heap or stack profiling |

## Gotchas

- The README's 'multi-threaded applications are not serialized' means the program code; allocator calls from all threads still contend on one global lock inside libheaptrack.
- Backtraces need debug symbols and frame unwinding info; release builds without debug info give unresolved frames, and Rust needs debug = true in the workspace Cargo.toml.
- The GitHub repo is a mirror: patches go to invent.kde.org/sdk/heaptrack and bugs to bugs.kde.org.
- Unwind depth is capped at 64 frames (Trace::MAX_SIZE) and can be lowered for speed; deeper stacks are truncated.

## Known shortcomings

- README's 'not serialized' covers application code only: every allocation still takes one global lock in libheaptrack. README says C++11/Qt5 but CMakeLists needs C++17, CMake 3.16 and Qt 6.5; no clang-ASan support; the old gold linker gives bogus backtraces; no page or stack profiling.

## Caveats and trade-offs

No numbers in the README; a search snippet of the author's blog claims roughly 10x faster than massif but the blog was not opened, so no number recorded. GitHub repo is the KDE mirror; development happens on invent.kde.org/sdk/heaptrack. REUSE-style LICENSES directory (GPL-2.0-or-later main, plus LGPL/BSD/MIT/BSL/Apache for components). Massif keeps advantages for custom allocators and page-level (pages-as-heap) tracking.

Linux only; LD_PRELOAD interposition so only allocation-heavy code pays overhead; heap profiling only (no CPU profile); GUI needs Qt/KDE.

## Maintenance

Actively maintained by KDE and KDAB (version 1.6.80 in CMakeLists, commits through 2026-10-02); the collector is GPL-2.0-or-later with LGPL-2.1+ parts, fine for use as a tool though not for vendoring into proprietary code.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification D, tier now D.
- **Tier reason:** README section 'Comparison to Valgrind's massif' says time and memory overhead is significantly lower, multi-threaded apps are not serialized and CPU-bound code is not slowed, but gives no numbers.
- **Verifier notes:** Last commit 2026-10-02 confirmed on github.com commits page (later than prompt date, real). License GPL-2.0-or-later plausible from LICENSES dir; copyable (OSI).
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** code reading by enricher
- **Pages the verifier opened:**
  - <https://github.com/KDE/heaptrack>
  - <https://github.com/KDE/heaptrack/commits>
  - <https://github.com/KDE/heaptrack/tree/master/LICENSES>
  - <https://raw.githubusercontent.com/KDE/heaptrack/HEAD/README.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/KDE/heaptrack/HEAD/README.md>
  - <https://raw.githubusercontent.com/KDE/heaptrack/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/KDE/heaptrack/HEAD/src/track/libheaptrack.cpp>
  - <https://raw.githubusercontent.com/KDE/heaptrack/HEAD/src/track/heaptrack_preload.cpp>
  - <https://raw.githubusercontent.com/KDE/heaptrack/HEAD/src/track/heaptrack_inject.cpp>
  - <https://raw.githubusercontent.com/KDE/heaptrack/HEAD/src/track/heaptrack.sh.cmake>
  - <https://raw.githubusercontent.com/KDE/heaptrack/HEAD/src/track/trace.h>
  - <https://raw.githubusercontent.com/KDE/heaptrack/HEAD/src/track/trace_libunwind.cpp>
  - <https://raw.githubusercontent.com/KDE/heaptrack/HEAD/src/track/tracetree.h>
  - WebSearch: heaptrack massif overhead comparison faster milianw blog (snippets only)
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/kde/heaptrack`) · [data/wave11/enrich/raw/github_com_kde_heaptrack.json](../../../data/wave11/enrich/raw/github_com_kde_heaptrack.json) (enrichment confidence 0.75)

</details>
