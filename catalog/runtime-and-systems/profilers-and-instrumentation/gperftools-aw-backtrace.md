# aw-backtrace

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Profilers and instrumentation](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `ISC` · 🟢 active

> Async-signal-safe, crash-free DWARF (.eh_frame) backtracer from the gperftools maintainers that unwinds faster than libgcc and LLVM libunwind.

| | |
|---|---|
| **Beats** | libgcc _Unwind_Backtrace and LLVM libunwind (stack unwinders used by profilers) |
| **Claimed result** | Cache-hit microbenchmark (frame pointers on): about 9.0-9.7 ns per unwind step vs libgcc 52.3-58.6 ns and LLVM libunwind 275.9-292.4 ns. With the cache off: 28.6-29.4 ns. With the cache off and -fomit-frame-pointer: 69.5-76.1 ns vs libgcc 121.9-133.6 ns and LLVM libunwind 491.8-525.2 ns. README: libgcc about 5x slower, LLVM libunwind another 5x slower than libgcc. |
| **Workload** | Microbenchmark of unwind cost per frame on recursive stacks, mostly cache hits (recursion-test.cc). |
| **Metric** | latency |
| **Compiler and flags** | CC=clang bazel build -c opt --copt=-ggdb3 --copt=-fno-omit-frame-pointer --copt=-march=native (plus -DTESTING_NO_CACHE and -fomit-frame-pointer variants); clang version not stated |
| **Adoption** | 3 stars; from the gperftools maintainers |
| **Last commit** | 2026-09-25 |
| **Links** | [repository](https://github.com/gperftools/aw-backtrace) · [benchmark](https://github.com/gperftools/aw-backtrace/blob/master/README.md) |

## Verdict

On the author's recursion-test.cc microbenchmark (clang, bazel -c opt, -march=native, -fno-omit-frame-pointer, unnamed CPU), a cached aw_backtrace step costs about 9.0-9.7 ns versus 52.3-58.6 ns for glibc backtrace()/libgcc and 275.9-292.4 ns for LLVM libunwind; with the cache disabled and -fomit-frame-pointer it is 69.5-76.1 ns versus 121.9-133.6 ns and 491.8-525.2 ns. These are first-party numbers from the README with no hardware stated.

## Use it when

- Sampling CPU profilers or heap/allocation profilers that take many backtraces per second on Linux glibc x86-64 and want to drop the frame-pointer requirement.
- Backtraces from inside signal handlers (SIGPROF, SIGSEGV crash handlers) or malloc hooks, where libgcc's unwinder can deadlock or crash on bad unwind info.
- Hot code with recurring call sites (the cache-hit case): about 9 ns per frame versus about 53-59 ns for glibc backtrace() through libgcc in the author's microbenchmark.
- Codebases already using gperftools, which vendors it and exposes it through its existing stack-trace APIs.

## Skip it when

- Non-Linux or non-glibc systems (musl, macOS, Windows), or glibc older than 2.35: _dl_find_object is required; i386, RISC-V and 32-bit ARM are planned but not supported.
- Programs that dlopen and dlclose plugins: only modules present at startup (main binary, LD_PRELOAD, initial DT_NEEDED) are cached, so frames in later-loaded code take the slower uncached path.
- Builds that already keep frame pointers and only need plain PCs: the README's own trivial frame-pointer backtracer is about 10x faster (about 0.6-1.2 ns per frame).
- Projects that need a stable API/ABI or a CMake/make install: version 0.0.1, first public release 2026-09-01, Bazel-only build, API explicitly pre-release.
- Exception unwinding: it only captures backtraces and does not replace the _Unwind_RaiseException personality machinery.

## How it is fast

The main lever is a single global, fixed-size (4096 entries, 8-way buckets) cache of compressed per-PC unwind info with a seqlock per bucket and second-chance eviction; lookups are load-only and nothing ever waits (a busy bucket is a miss, a contended insert is dropped), which keeps it async-signal-safe. Module lookup uses glibc's _dl_find_object instead of dl_iterate_phdr, and a fast-path parser/interpreter handles the common subset of DWARF CFI. Stack VMA bounds for validation come from the PROCMAP_QUERY ioctl (Linux 6.11+) and are cached per thread.

## Compared with alternatives

Pick it over the ClickHouse libunwind stack-trace cache when you want a standalone, async-signal-safe unwinder you can link without forking LLVM libunwind; ClickHouse's patch is the better reference if you must keep the libunwind API or need exception unwinding. Tools such as Tracy, bytehound or heaptrack ship their own unwinding; aw-backtrace is the component you would build such a profiler on.

## Integration

| | |
|---|---|
| **Form** | static lib (Bazel module aw-backtrace 0.0.1) or source-drop; also vendored inside gperftools |
| **Dependencies** | none for the core library (glibc 2.35+); abseil, googletest and lua are dev-only dependencies for tests and perf-convert |
| **Minimum toolchain** | C++20 (author says C++17 is possible on request), GCC or Clang; Bazel build |
| **Platforms** | Linux glibc 2.35+ on x86-64 (main focus) and aarch64 (less tested); best performance with Linux 6.11+ PROCMAP_QUERY, otherwise falls back to reading /proc/pid/maps |
| **Thread safety** | Fully async-signal-safe and thread-safe; the shared cache uses non-blocking per-bucket seqlocks (DebugExtensionV0::TryGet is not signal-safe on first call) |
| **Drop-in for the baseline** | partial — aw_backtrace() mirrors glibc backtrace() with extra ucontext and skip arguments and aw_backtrace_full() resembles _Unwind_Backtrace, but callers must switch to the new symbols; it does not interpose on libgcc |

## Gotchas

- The headline numbers come from recursion-test.cc, which unwinds the same handful of eval_ast call sites over and over, so nearly every lookup hits the cache; with the cache off (-DTESTING_NO_CACHE) it is about 28.6-29.4 ns per frame with frame pointers and about 70-76 ns without, versus libgcc's about 122-134 ns (about 1.8x faster).
- The libgcc baseline is glibc backtrace() (which goes through libgcc's _Unwind_Backtrace) and the LLVM libunwind baseline is the same binary with LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libunwind.so.1; no CPU model or clang version is given, and timing uses clock() over 10240 iterations.
- Without PROCMAP_QUERY (kernels before 6.11) VMA bound discovery reads /proc/pid/maps, which the README says is slower and scales poorly with the number of VMAs.
- Source files carry SPDX 0BSD headers while the LICENSE file is ISC; both are permissive. The author discloses that Gemini and Claude helped write and review the code.

## Known shortcomings

- The headline numbers are mostly cache hits: recursion-test.cc reuses the same few eval_ast call sites against a 4096-entry global seqlock cache; with the cache off the gain over libgcc is about 1.8x. The libgcc baseline is glibc backtrace(). No CPU and no clang version stated. Source SPDX is 0BSD while LICENSE is ISC.

## Caveats and trade-offs

No CPU model is stated, so the record is not tier A. The headline microbenchmark is mostly cache hits; the cache-off rows (about 1.8x faster than libgcc) are the fairer comparison for cache-missing workloads. First public release was 2026-09-01; the author says the API is not stable and the library needs glibc 2.35+ and works best on Linux 6.11+ (PROCMAP_QUERY). The baselines are unwinders, not perf, gprof or Valgrind. The author discloses using LLMs during development.

Linux glibc 2.35+ (_dl_find_object) on x86-64 and aarch64; API not stable, no install story, Bazel build; frame-pointer unwinding is still \~10x faster.

## Maintenance

Active (72 commits, last on 2026-09-25, no issues filed yet) and ISC/0BSD-licensed, so it can be copied, but it is a 0.0.1 pre-release with an unstable API and a Bazel-only build.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The README Benchmark section prints recursion-test.cc output with the exact bazel/clang flags for aw-backtrace, libgcc and LLVM libunwind (LD_PRELOAD libunwind.so.1), but it states no CPU model, so the record is not tier A; these are first-party numbers.
- **Verifier notes:** ISC license confirmed from LICENSE (0BSD-like ISC text, Copyright 2026 gperftools Contributors). 3 stars, 72 commits, not a fork; last commit 2026-09-25.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** code reading by enricher
- **Pages the verifier opened:**
  - <https://github.com/gperftools/aw-backtrace>
  - <https://github.com/gperftools/aw-backtrace/commits>
  - <https://raw.githubusercontent.com/gperftools/aw-backtrace/HEAD/README.md>
  - <https://raw.githubusercontent.com/gperftools/aw-backtrace/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/gperftools/aw-backtrace>
  - <https://raw.githubusercontent.com/gperftools/aw-backtrace/HEAD/README.md>
  - <https://raw.githubusercontent.com/gperftools/aw-backtrace/HEAD/include/aw-backtrace/aw-backtrace.h>
  - <https://raw.githubusercontent.com/gperftools/aw-backtrace/HEAD/recursion-test.cc>
  - <https://raw.githubusercontent.com/gperftools/aw-backtrace/HEAD/unwind-info-cache.h>
  - <https://raw.githubusercontent.com/gperftools/aw-backtrace/HEAD/BUILD.bazel>
  - <https://raw.githubusercontent.com/gperftools/aw-backtrace/HEAD/MODULE.bazel>
  - <https://github.com/gperftools/aw-backtrace/issues?q=is%3Aissue>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/gperftools/aw-backtrace`) · [data/wave11/enrich/raw/github_com_gperftools_aw_backtrace.json](../../../data/wave11/enrich/raw/github_com_gperftools_aw_backtrace.json) (enrichment confidence 0.8)

</details>
