# DoubleTake

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Profilers and instrumentation](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `MIT` · 🔴 abandoned

> LD_PRELOAD heap-error checker (overflow, use-after-free, leaks) using checkpoint/replay; few-percent overhead versus ASan's 30%+ and Valgrind's \~17x.

| | |
|---|---|
| **Beats** | Valgrind Memcheck and AddressSanitizer |
| **Claimed result** | On SPEC CPU2006 (ref inputs), 4% average runtime overhead with all three detectors (overflow, leak, use-after-free) and about 3% with overflow detection alone, versus an AddressSanitizer average over 30%. DoubleTake is faster than ASan on 17 of 19 benchmarks. Valgrind Memcheck averages about 17x (geomean, range 4.5x-42.8x) on the same suite. The README states 2% average for overflow detection only. |
| **Workload** | Evidence-based detection of heap overflows, use-after-free and leaks, runtime overhead on benchmark suites. |
| **Metric** | other |
| **Hardware** | Dual-processor Intel Core 2-era Xeon system, 4 cores per processor at 2.33GHz, 4MB shared L2, 16GB RAM, Linux 3.13, glibc 2.19 (no exact model number) |
| **Compiler and flags** | LLVM 3.2 clang -O2, 64-bit |
| **Adoption** | 21 stars |
| **Last commit** | 2016-05-22 |
| **Links** | [repository](https://github.com/plasma-umass/doubletake) · [benchmark](https://github.com/plasma-umass/DoubleTake/blob/master/doc/UM-CS-2015-018.pdf) |

## Verdict

In the UMass tech report UM-CS-2015-018 (ICSE 2016 paper), all 19 C/C++ SPEC CPU2006 benchmarks with ref inputs, built with LLVM 3.2 clang -O2 on a 2.33GHz dual 4-core Core 2-era Xeon with Linux 3.13/glibc 2.19, ran with 4% average overhead under DoubleTake with all detectors versus over 30% for AddressSanitizer, beating ASan on 17 of 19; Valgrind Memcheck averaged about 17x on the same suite. Rollback cost was excluded and each result is the mean of three runs.

## Use it when

- Single-threaded C/C++ batch programs on x86-64 Linux where ASan's \~2x slowdown or rebuild requirement is too expensive, e.g. running long test or input-fuzzing campaigns with checking left on.
- You cannot recompile the binary (third-party or legacy code) and Valgrind Memcheck's 4.5x-42.8x slowdown is unacceptable.
- Programs with few epoch-ending system calls (mostly file I/O, no sockets) and moderate malloc rates, where the report measured under 3% overhead on 14 of 19 SPEC CPU2006 benchmarks.
- Leak hunting during execution rather than only at exit (it checks at every epoch boundary, ASan only at program end).

## Skip it when

- Multithreaded code: the tech report says the prototype is limited to single-threaded programs; the repo has pthread interposition, but open issues #11-#13 report failed rollback on PARSEC dedup, ferret, fluidanimate and kmeans.
- You need read-error detection, stack/global overflows, or overflows that skip past canaries: detectors fire only on heap writes, use-after-free canaries cover only the first 128 bytes of a freed object, and non-contiguous overflows are missed.
- Malloc-heavy or syscall-heavy programs: 403.gcc (canary filling of freed memory) and 464.h264ref (825 epochs) ran above 20% overhead; network servers end an epoch on every socket read.
- Anything needing a maintained tool: last commit 2016-05-22, 6 open issues, built against LLVM 3.2-era toolchains; modern ASan/HWASan are actively maintained.
- Non-x86-64 or non-Linux targets: relies on x86 debug registers, getcontext/setcontext and Linux /proc and perf_event_open.

## How it is fast

Evidence-based dynamic analysis: the program runs at full speed inside epochs that end only at irrevocable system calls (socket I/O, unlisted syscalls); at each epoch end it scans a bitmap of heap canaries (padding after objects, canary-filled quarantined freed objects) and looks for unreachable objects. Only if evidence is found does it roll back to the epoch snapshot and re-execute with x86 hardware watchpoints (perf_event_open, up to 4) on the corrupted words and call-site recording in the allocator. Most syscalls are classified as repeatable, recordable or deferrable so epochs stay long (most SPEC benchmarks run in 1-9 epochs).

## Compared with alternatives

Pick DoubleTake over AddressSanitizer when you cannot or do not want to recompile and only need heap overflow/use-after-free/leak detection on single-threaded code at near-native speed; pick Dr. Memory or Valgrind Memcheck when you need read errors, uninitialized-value tracking, multithreading or a maintained tool.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | libdl, pthread; bundled Heap Layers (heaplayers/); clang preferred by the Makefile |
| **Minimum toolchain** | C11 / C++11; Makefile defaults to clang/clang++ (paper used LLVM 3.2) |
| **Platforms** | Linux x86-64 (an x86 32-bit build flag exists); hardware watchpoints required for pinpointing |
| **Thread safety** | Paper prototype single-threaded only; later code interposes pthreads (MAX_ALIVE_THREADS = 128) but rollback failures on multithreaded PARSEC programs are open issues |
| **Drop-in for the baseline** | partial — preloads into unmodified binaries like Valgrind (no ASan-style recompilation), but detects only heap write errors and leaks, not ASan's or Memcheck's full set |

## Gotchas

- The default Makefile builds at -O0 with -DDEBUG_LEVEL=3 and leak detection (-DDETECT_MEMORY_LEAKS) commented out; build with make O=2 and adjust FEATURE_FLAGS before measuring overhead.
- It replaces the heap with a fixed 8 GB user heap plus a 4 GB internal heap (xdefines.hh) in power-of-two BiBOP size classes, so allocation-size behavior and memory footprint differ from glibc; the README says the open-file limit must be raised for some programs.
- The overhead numbers exclude rollback and replay time (rollback was disabled in the evaluation), so a run that finds errors costs more than reported.
- Overhead figures disagree across sources: README says 2% for overflow-only, the report's introduction says 3%, and its evaluation text says no observable overhead without use-after-free detection; 4% with all three detectors is the consistent number.

## Known shortcomings

- Paper prototype is single-threaded only; open issues 11-13 report rollback failing on PARSEC dedup, ferret, fluidanimate and kmeans. Detects heap writes only; use-after-free canaries cover the first 128 bytes. Overhead excludes rollback time. The overflow-only figure disagrees across sources (README 2%, report intro 3%, evaluation text 'no observable'); the 4% all-detectors figure is consistent. Default Makefile builds -O0 with DEBUG_LEVEL=3 and leak detection off. Abandoned since 2016-05-22.

## Caveats and trade-offs

Numbers come from the tech report in the repo's doc/ directory (published at ICSE 2016; the arXiv 1601.07962 and camera-ready copies are blocked here, so small differences from the final paper are possible). The README's 2% figure differs from the report's 3% for overflow-only. Rollback/replay cost is excluded from the overhead measurement. Measured with 2013-era LLVM 3.2 ASan on old Xeon hardware; the code has been unmaintained since 2016. SPEC CPU2006 is not public.

Detects errors after the fact via checkpoint and replay; needs deterministic replay, so programs with external I/O are harder; Linux.

## Maintenance

Abandoned research prototype (last commit 2016-05-22, 21 stars, 6 open rollback/threading issues) but MIT-licensed; treat it as a reference design for checkpoint-and-replay checking rather than a production tool.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now B.
- **Tier reason:** The tech report checked into the repo (doc/UM-CS-2015-018.pdf), published as an ICSE 2016 paper, runs SPEC CPU2006 against AddressSanitizer: 4% average overhead with all detectors versus over 30% for ASan, and DoubleTake beats ASan on 17 of 19 benchmarks. Valgrind's roughly 17x geomean is reported as context. That makes it B; it is not A because SPEC is not public and the CPU is described only as a 2.33GHz 4-core Xeon, with no model number.
- **Verifier notes:** Upgraded C to B: the peer-reviewed paper's tech report is in the repo and compares directly against ASan, with Valgrind as context. The README itself does not mention either baseline. The ICSE venue comes from a WebSearch result; the umass.edu PDF host was blocked (403).
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** peer-reviewed tech report, read from a repo copy
- **Pages the verifier opened:**
  - <https://github.com/plasma-umass/DoubleTake>
  - <https://github.com/plasma-umass/DoubleTake/commits>
  - <https://github.com/plasma-umass/DoubleTake/tree/master/doc>
  - <https://raw.githubusercontent.com/plasma-umass/DoubleTake/HEAD/README.md>
  - <https://raw.githubusercontent.com/plasma-umass/DoubleTake/HEAD/doc/UM-CS-2015-018.pdf>
- **Sources the enricher read:**
  - <https://github.com/plasma-umass/DoubleTake>
  - <https://github.com/plasma-umass/DoubleTake/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/plasma-umass/DoubleTake/HEAD/README.md>
  - <https://raw.githubusercontent.com/plasma-umass/DoubleTake/HEAD/Makefile>
  - <https://raw.githubusercontent.com/plasma-umass/DoubleTake/HEAD/doc/UM-CS-2015-018.pdf>
  - <https://raw.githubusercontent.com/plasma-umass/DoubleTake/HEAD/source/libdoubletake.cpp>
  - <https://raw.githubusercontent.com/plasma-umass/DoubleTake/HEAD/include/xthread.hh>
  - <https://raw.githubusercontent.com/plasma-umass/DoubleTake/HEAD/include/xdefines.hh>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/plasma-umass/doubletake`) · [data/wave11/enrich/raw/github_com_plasma_umass_doubletake.json](../../../data/wave11/enrich/raw/github_com_plasma_umass_doubletake.json) (enrichment confidence 0.75)

</details>
