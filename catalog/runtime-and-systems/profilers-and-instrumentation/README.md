# Profilers and instrumentation

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md)</sub>

**What these beat:** perf, gprof, Valgrind  
**20 entries:** 0 tier A · 5 tier B · 10 tier C · 5 tier D · 17 copyable, 3 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**Coz causal profiler**](plasma-umass-coz.md) | Causal profiler for C/C++/Rust that predicts the whole-program effect of speeding up each line; far lower overhead than gprof. | **B** | C++ | BSD-2-Clause | 🟢 active |
| 2 | [**Dr. Memory**](dynamorio-drmemory.md) | DynamoRIO-based memory error checker for unmodified binaries; about 2x faster than Valgrind Memcheck on SPEC CPU2006 per its CGO 2011 paper. | **B** | C++ | LGPL-2.1-only (drfuzz and… | 🟢 active |
| 3 | [**bpftime**](eunomia-bpf-bpftime.md) | Userspace eBPF runtime that runs unmodified libbpf/bpftrace uprobe programs with about 13-16x lower per-hit cost than kernel uprobes. | **B** | C++ | MIT | 🟢 active |
| 4 | [**E9Patch**](gjduck-e9patch.md) | Static x86_64 ELF binary rewriter that skips control-flow recovery; more robust and scalable than Dyninst-style rewriters, but not faster. | **B** | C++ | GPL-3.0-only | 🟢 active |
| 5 | [**DoubleTake**](plasma-umass-doubletake.md) | LD_PRELOAD heap-error checker (overflow, use-after-free, leaks) using checkpoint/replay; few-percent overhead versus ASan's 30%+ and Valgrind's \~17x. | **B** | C++ | MIT | 🔴 abandoned |
| 6 | [**ClickHouse libunwind stack-trace cache (llvm-project fork)**](clickhouse-clickhouse.md) | ClickHouse's patched LLVM libunwind with a lock-free per-IP cache of decoded DWARF rules; 4.8-7.3x faster repeated stack traces. | **C** | C++ | Apache-2.0 (ClickHouse)… | 🟢 active |
| 7 | [**AddressSanitizer (LLVM compiler-rt)**](llvm-llvm-project.md) | Compiler-instrumented memory-error detector in Clang/GCC; about 2x slowdown where Valgrind Memcheck costs about 20x. | **C** | C++ | Apache-2.0 WITH… | 🟢 active |
| 8 | [**Tracy Profiler**](wolfpld-tracy.md) | Hybrid instrumentation plus sampling frame profiler for C/C++ with nanosecond rdtsc timestamps and a remote GUI; no measured win over perf, gprof or Valgrind. | **C** | C++ | BSD-3-Clause | 🟢 active |
| 9 | [**magic-trace**](janestreet-magic-trace.md) | Intel PT tracer recording every function call at about 40 ns resolution, with 2-10% overhead, below perf -g call-graph sampling. | **C** | OCaml | MIT | 🟢 active |
| 10 | [**MicroProfiler (micro-profiler)**](tyoma-micro-profiler.md) | Low-overhead real-time instrumenting C/C++ profiler; README chart shows 6-7x less slowdown than AQtime and the VS instrumenting profiler. | **C** | C++ | MIT | 🟢 active |
| 11 | [**wallClockProfiler**](jasonrohrer-wallclockprofiler.md) | Single-file C++ 'poor man's profiler' that drives GDB to sample wall-clock stacks, with far less slowdown than callgrind. | **C** | C++ | Public-Domain… | 🟢 active |
| 12 | [**aw-backtrace**](gperftools-aw-backtrace.md) | Async-signal-safe, crash-free DWARF (.eh_frame) backtracer from the gperftools maintainers that unwinds faster than libgcc and LLVM libunwind. | **C** | C++ | ISC | 🟢 active |
| 13 | [**funtrace**](yosefk-funtrace.md) | Small flight-recorder function call tracer for C/C++ on x86-64 Linux; author reports 4.5-18x lower per-call cost than XRay and uftrace. | **C** | C++ | BSD-2-Clause | 🟡 stale |
| 14 | [**tracing_malloc**](dpull-tracing-malloc.md) | Linux LD_PRELOAD malloc hook that records live allocations with stack traces; far lower overhead than Valgrind for leak hunting. | **C** | C++ | no license (study only) | 🟢 active |
| 15 | [**Palanteer**](dfeneyrou-palanteer.md) | Single-header C++11 tracing/logging instrumentation plus viewer; enqueues a log in \~19 ns versus 1250 ns measured for spdlog. | **C** | C++ | MIT (instrumentation… (study only) | 🟡 stale |
| 16 | [**heaptrack**](kde-heaptrack.md) | Linux heap profiler using LD_PRELOAD and libunwind; much lower time and memory overhead than Valgrind massif (no published numbers). | **D** | C++ | GPL-2.0-or-later | 🟢 active |
| 17 | [**heapusage**](d99kris-heapusage.md) | LD_PRELOAD/DYLD_INSERT_LIBRARIES heap-error and leak checker covering a small subset of Valgrind Memcheck without CPU emulation. | **D** | C++ | BSD-3-Clause | 🟢 active |
| 18 | [**memtrail**](jrfonseca-memtrail.md) | LD_PRELOAD heap profiler and leak finder for Linux; claims much lower overhead than Valgrind Massif or Memcheck, unmeasured. | **D** | C | MIT (permission headers in… | 🟢 active |
| 19 | [**bytehound**](koute-bytehound.md) | LD_PRELOAD heap profiler for Linux recording every allocation with full backtraces, positioned as a cheaper heaptrack/massif alternative. | **D** | Rust | Apache-2.0 OR MIT | 🔴 abandoned |
| 20 | [**Perforator**](yandex-perforator.md) | Yandex's eBPF continuous CPU profiler that unwinds frame-pointer-less native stacks in-kernel; a perf record alternative, no measured win. | **D** | Go | Apache-2.0 (eBPF unwinder… (study only) | 🟢 active |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
