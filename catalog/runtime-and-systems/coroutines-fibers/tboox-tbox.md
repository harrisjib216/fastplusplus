# tbox (coroutine switch)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Coroutines and fibers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `Apache-2.0` · 🟢 active

> glib-like C library whose stackful coroutine scheduler switches faster than Boost.Coroutine and libco in its author's benchmark.

| | |
|---|---|
| **Beats** | Boost.Context (boost), libco (Tencent), libgo(boost), libmill, libtask, Go, cloudwu coroutine, acl libfiber |
| **Claimed result** | LinuxMint x86_64 VM, 1000 coroutines: tbox 400 ms vs boost 894 ms vs libco 2288 ms for 10M switches (derived from page data: about 2.2x vs boost, 5.7x vs libco). 2 coroutines: tbox 187 ms vs boost 199 ms vs libco 687 ms (about 1.06x vs boost, 3.7x vs libco; libmill 145 ms is faster). macOS x86_64: 2 coroutines tbox 205 ms vs boost 728 ms; 1000 coroutines 438 ms vs 1949 ms (derived from page data: about 3.6x and 4.5x vs boost). |
| **Workload** | 10,000,000 coroutine switches among 2 and 1000 coroutines, in the benchbox 'switch' test, on macOS x86_64 and on ArchLinux i386 and LinuxMint x86_64 under VirtualBox. |
| **Metric** | throughput |
| **Hardware** | VirtualBox VMs (LinuxMint x86_64, ArchLinux i386) and macOS x86_64; CPU model not stated |
| **Adoption** | 5.1k stars |
| **Last commit** | 2026-09-15 |
| **Links** | [repository](https://github.com/tboox/tbox) · [benchmark](https://github.com/tboox/benchbox/wiki/switch) |

## Verdict

The author's benchbox 'switch' test times 10,000,000 yields among 2 or 1000 coroutines: on a LinuxMint x86-64 VirtualBox VM tbox took 187 ms (2) and 400 ms (1000) vs Boost.Coroutine symmetric_coroutine 199/894 ms, libco 687/2288 ms and libmill 145/1014 ms; on macOS x86-64 tbox 205/438 ms vs boost 728/1949 ms. No CPU, compiler, flags or Boost version are given, and the boost and libco harnesses perform two context jumps per counted switch versus one for tbox (read from the benchbox sources).

## Use it when

- Pure C projects that want coroutine-based network or I/O servers with built-in poller integration (epoll/kqueue/IOCP) and channels
- Many-coroutine (around 1000) cooperative scheduling on one thread where switch cost dominates
- Projects already using xmake or willing to take the tbox package, on x86, x86-64, ARM or ARM64
- Embedded or cross-platform code that also benefits from tbox's other modules (micro build is about 64K)

## Skip it when

- You only need a context-switch primitive; minicoro, libaco or Boost.Context are far smaller dependencies than all of tbox
- C++ code that wants a standard or Boost interface (C++20 coroutines, Boost.Context/Fiber); tbox's API is C and scheduler-centric
- Multi-threaded work-stealing schedulers; the benchmarked scheduler runs coroutines on one thread
- Code that changes the floating-point environment inside coroutines; the x86-64 jump routine does not save MXCSR or the x87 control word as Boost.Context's does
- When you need a fair published comparison: the only numbers are a first-party VM benchmark from 2015-2017

## How it is fast

The context switch (tb_context_jump) is a hand-written assembly routine adapted from Boost.Context's jump_fcontext: on x86-64 it pushes the six callee-saved integer registers, swaps the stack pointer and jumps, with no syscalls and no signal-mask save. tb_coroutine_yield picks the next ready coroutine and jumps to it directly, so each yield is a single coroutine-to-coroutine switch rather than a round trip through a central resumer.

## Compared with alternatives

Pick tbox over libco, libgo or libfiber when you want a C coroutine runtime bundled with pollers, channels and I/O helpers in one maintained library; pick minicoro or libaco instead when you only need a tiny switch primitive, and libmill/libdill if you want a smaller C coroutine library with similar measured switch speed.

## Integration

| | |
|---|---|
| **Form** | static lib (or shared lib) built with xmake; also available as an xmake package (add_requires("tbox", {configs = {coroutine = true}})) |
| **Dependencies** | none required for the coroutine module; optional zlib, OpenSSL/mbedTLS/PolarSSL, MySQL, SQLite3 for other modules |
| **Minimum toolchain** | C99 compiler (benchbox builds with c99/cxx11); xmake build system |
| **Platforms** | Windows, macOS, Linux, Android, iOS, BSD; coroutine switch assembly for x86, x86-64, ARM, ARM64 |
| **Thread safety** | not documented in the README; each scheduler and its coroutines run on the thread that loops it |
| **Drop-in for the baseline** | no |

## Gotchas

- Benchmark asymmetry: in tboox/benchbox the tbox and libmill tests yield coroutine-to-coroutine through their schedulers (one jump per counted switch), while the boost (symmetric_coroutine called from main) and libco (co_resume from main, co_yield_ct back) tests bounce through main, doing two context jumps per counted switch; the reported 2.2x to 4.5x lead over boost and 3.7x to 5.7x over libco therefore overstates per-jump cost, roughly by up to 2x
- libmill, measured the same scheduler-to-scheduler way, beat tbox on the LinuxMint x86-64 VM with 2 coroutines (145 ms vs 187 ms)
- Debug builds enable assertions and memory checking; use the xmake release mode for performance
- The x86-64 switch saves only integer callee-saved registers; floating-point control state is not preserved across switches

## Known shortcomings

- Harness flaw behind the numbers: the benchbox boost and libco tests bounce through main (two context jumps per counted switch) while the tbox and libmill tests yield coroutine to coroutine (one jump), so the 2.2-4.5x lead over Boost and 3.7-5.7x over libco is overstated by up to about 2x. The x86-64 tb_context_jump skips MXCSR and the x87 control word, unlike Boost.Context.

## Caveats and trade-offs

First-party benchmark (benchbox by the same author). No compiler, flags or CPU model stated, VM runs. Lead over boost is marginal with 2 coroutines and libmill is faster there. Benchmark source is benchbox src (xmake coroutine -n switch). [retier] benchbox boost and libco tests bounce through main (2 context jumps per counted switch) while tbox and libmill yield coroutine to coroutine (1 jump), so the lead over Boost.Context and libco is overstated by up to about 2x; VM runs with no flags or CPU model; x86-64 tb_context_jump skips MXCSR and the x87 control word.

Coroutine switch is one module of a glib-like C library (tbox); needs xmake or its build to use; stackful and stackless coroutines; assembly per architecture (x86, x86_64, ARM, ARM64).

## Maintenance

Actively maintained (last commit 2026-09-15, 5.1k stars, CI on Windows/Linux/macOS/Android) and Apache-2.0, but the coroutine benchmark dates from 2015-2017 and has not been rerun publicly.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** benchbox wiki 'switch' page (same author) lists 10M-switch times for tbox, boost, libco and others on macOS and two VirtualBox Linux VMs; benchmark code lives in tboox/benchbox but no compiler, flags or CPU model given, so C.
- **Verifier notes:** All quoted numbers match the wiki page (fetched as raw wiki markdown). Metadata verified: Apache-2.0, 5.1k stars, last commit 2026-09-15. Benchmark is old and VM-based; Boost version not stated.
- **Fields the verifier corrected:** `compared_against_cpp_std_directly`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** code reading by enricher
- **Pages the verifier opened:**
  - <https://github.com/tboox/tbox>
  - <https://raw.githubusercontent.com/tboox/tbox/HEAD/README.md>
  - <https://raw.githubusercontent.com/tboox/tbox/HEAD/LICENSE.md>
  - <https://raw.githubusercontent.com/wiki/tboox/benchbox/switch.md>
  - <https://github.com/tboox/tbox/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/tboox/tbox/HEAD/README.md>
  - <https://raw.githubusercontent.com/wiki/tboox/benchbox/switch.md>
  - <https://github.com/tboox/benchbox>
  - <https://github.com/tboox/benchbox/tree/master/src/coroutine>
  - <https://github.com/tboox/benchbox/tree/master/src/coroutine/switch>
  - <https://raw.githubusercontent.com/tboox/benchbox/HEAD/xmake.lua>
  - <https://raw.githubusercontent.com/tboox/benchbox/master/src/coroutine/switch/tbox/main.c>
  - <https://raw.githubusercontent.com/tboox/benchbox/master/src/coroutine/switch/tbox/xmake.lua>
  - <https://raw.githubusercontent.com/tboox/benchbox/master/src/coroutine/switch/boost/main.cpp>
  - <https://raw.githubusercontent.com/tboox/benchbox/master/src/coroutine/switch/boost/xmake.lua>
  - <https://raw.githubusercontent.com/tboox/benchbox/master/src/coroutine/switch/libco/main.cpp>
  - <https://raw.githubusercontent.com/tboox/benchbox/master/src/coroutine/switch/libmill/main.c>
  - <https://raw.githubusercontent.com/tboox/benchbox/master/src/coroutine/switch/libaco/main.c>
  - <https://raw.githubusercontent.com/tboox/tbox/HEAD/src/tbox/coroutine/impl/scheduler.c>
  - <https://raw.githubusercontent.com/tboox/tbox/HEAD/src/tbox/platform/arch/x64/context.S>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/tboox/tbox`) · [data/wave11/enrich/raw/github_com_tboox_tbox.json](../../../data/wave11/enrich/raw/github_com_tboox_tbox.json) (enrichment confidence 0.75)

</details>
