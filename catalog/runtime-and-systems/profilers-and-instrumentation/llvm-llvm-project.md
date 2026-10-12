# AddressSanitizer (LLVM compiler-rt)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Profilers and instrumentation](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0 WITH LLVM-exception` · 🟢 active

> Compiler-instrumented memory-error detector in Clang/GCC; about 2x slowdown where Valgrind Memcheck costs about 20x.

| | |
|---|---|
| **Beats** | Valgrind Memcheck |
| **Claimed result** | About 2x slowdown for AddressSanitizer versus about 20x for Valgrind/Memcheck and about 10x for Dr. Memory (comparison table); own SPEC CPU2006 run: average slowdown 1.93, median 1.86, range 1.12x (462.libquantum) to 3.79x (400.perlbench). |
| **Workload** | Memory-error detection (heap/stack/global buffer overflow, use-after-free) on SPEC CPU2006 C/C++ programs. |
| **Metric** | throughput |
| **Hardware** | Intel Xeon W3690 @ 3.47GHz (own-numbers page only; the comparison table does not state hardware) |
| **Compiler and flags** | Clang 3.3 trunk r179094, -O2 -fsanitize=address -fno-omit-frame-pointer (own-numbers page https://github.com/google/sanitizers/wiki/AddressSanitizerPerformanceNumbers) |
| **Adoption** | llvm/llvm-project 40.9k stars; ASan ships in Clang and GCC; google/sanitizers docs repo 12.5k stars (per record, not rechecked) |
| **Links** | [repository](https://github.com/llvm/llvm-project) · [benchmark](https://github.com/google/sanitizers/wiki/AddressSanitizerComparisonOfMemoryTools) |

## Verdict

Google's 2013 run on SPEC CPU2006 C/C++ (Clang 3.3 r179094, -O2 -fsanitize=address -fno-omit-frame-pointer vs plain -O2, Xeon W3690 @ 3.47 GHz) gave average slowdown 1.93x, median 1.86x, range 1.12x (462.libquantum) to 3.79x (400.perlbench). The Memcheck 20x and Dr. Memory 10x figures in the comparison table are cited from the Dr. Memory paper, not measured on the same machine.

## Use it when

- CI and test runs of C/C++ code you can rebuild, where Memcheck's slowdown makes full test suites or fuzzing impractical
- Fuzzing (libFuzzer, AFL) and long integration tests where a 1.1x-3.8x slowdown (SPEC CPU2006 range) is affordable
- Hunting stack and global buffer overflows and use-after-return, which Memcheck does not detect
- Linux, macOS, Android, FreeBSD, NetBSD, iOS Simulator and Windows 8.1+ builds with Clang, or GCC 4.8+

## Skip it when

- You need uninitialized-read detection: ASan does not do it; use MemorySanitizer or Memcheck
- You cannot recompile the program or its libraries: bugs inside uninstrumented code are mostly missed (only intercepted libc calls are checked); Memcheck or Dr. Memory work on the binary
- Statically linked executables (not supported) or memory-tight environments: more real memory (worse for small allocations), up to 3x stack, and 16+ TB of mapped virtual address space that breaks ulimit -v
- Production binaries: the docs say the runtime was not built with security constraints and may compromise the executable

## How it is fast

Compile-time instrumentation instead of dynamic binary translation: each load/store gets an inline shadow-memory check, Shadow = (Mem &gt;&gt; 3) + 0x7fff8000 on x86-64, with 8 application bytes mapped to 1 shadow byte and a slow path only when the shadow byte is nonzero. The allocator surrounds blocks with poisoned redzones and holds freed memory in a poisoned quarantine; stack and globals get compiler-inserted redzones. Stopping at the first error lets the compiler emit about 5% faster and smaller code.

## Compared with alternatives

Pick ASan over Dr. Memory, RetroWrite or Valgrind-style tools whenever you control the build: it is the fastest general detector with the broadest bug coverage of the three (stack/global OOB). Pick DoubleTake when even 2x is too much and end-of-epoch detection suffices; pick Dr. Memory or Memcheck for binaries you cannot rebuild. It is the same tool as the google/sanitizers entry.

## Integration

| | |
|---|---|
| **Form** | compiler flag plus runtime library shipped with Clang (compiler-rt) and GCC (libasan) |
| **Dependencies** | Clang with compiler-rt or GCC 4.8+; llvm-symbolizer for symbolized reports |
| **Minimum toolchain** | Clang/LLVM 3.1+ or GCC 4.8+ |
| **Platforms** | Linux, macOS, iOS Simulator, Android, NetBSD, FreeBSD, Windows 8.1+ (Windows port less well supported); x86, ARM, PPC per the comparison page |
| **Thread safety** | Multithreaded programs supported (reports name the thread, e.g. T0); per-thread details not documented on the pages read |
| **Drop-in for the baseline** | partial — needs a rebuild with -fsanitize=address and covers a different bug set (adds stack/global OOB and use-after-return, lacks uninitialized reads) |

## Gotchas

- Do not link with -Wl,-z,defs or -Wl,--no-undefined (link errors unless -shared-libasan); final link must go through clang/gcc, not ld
- Clang and GCC ASan implementations are incompatible; code and runtimes from the two cannot be mixed
- Container-overflow checks (annotated std::vector etc.) can give false positives in partially instrumented binaries; disable with ASAN_OPTIONS=detect_container_overflow=0
- This record's id is the whole llvm-project monorepo and the catalog already has 'AddressSanitizer (google/sanitizers)' with the same numbers; the two entries describe the same tool

## Known shortcomings

- The Valgrind 20x figure is quoted from the Dr. Memory paper and was not measured on the same machine; the entry is the whole llvm-project monorepo (docs now in clang/docs/AddressSanitizer.md). The google/sanitizers entry for the same tool and numbers was folded into this one.

## Caveats and trade-offs

The comparison table cites its Valgrind/Memcheck and Dr. Memory slowdowns from the Dr. Memory paper; they were not rerun on the same machine. The only ASan measurement (AddressSanitizerPerformanceNumbers) compares against uninstrumented clang -O2 on SPEC CPU2006, which is licensed rather than public, and dates from 2013 (Clang 3.3). The peer-reviewed USENIX ATC 2012 paper was not reachable. The id is the whole llvm-project monorepo; the catalogued component is compiler-rt/lib/asan, so check that this id does not clash with other llvm-project entries (libc++, BOLT and others).

Needs recompilation with the sanitizer (compiler instrumentation, not binary instrumentation); roughly 2x memory use; cannot check uninstrumented libraries; different bug classes than Memcheck (no uninitialized-read detection, that is MemorySanitizer).

## Maintenance

Actively developed inside LLVM and shipped with every Clang and GCC; Apache-2.0 WITH LLVM-exception, used as a compiler feature rather than copied code.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The comparison page lists ASan 2x vs Valgrind/Memcheck 20x and Dr. Memory 10x, but the Valgrind and Dr. Memory figures are cited from the Dr. Memory paper rather than measured alongside ASan. The own-numbers page states Clang 3.3 r179094, -O2 -fsanitize=address -fno-omit-frame-pointer and a Xeon W3690, but it measures ASan against uninstrumented clang -O2 only, and SPEC CPU2006 is not public code, so the record cannot be tier A against Valgrind.
- **Verifier notes:** The numbers match both wiki pages. The record id is the generic llvm-project URL; if llvm-project is already catalogued for another component, give this entry a distinct id or name before applying. License not rechecked from LICENSE.TXT (the page shows LICENSE.TXT; Apache-2.0 WITH LLVM-exception is standard).
- **Fields the verifier corrected:** `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** public benchmark code
- **Pages the verifier opened:**
  - <https://github.com/google/sanitizers/wiki/AddressSanitizerComparisonOfMemoryTools>
  - <https://github.com/google/sanitizers/wiki/AddressSanitizerPerformanceNumbers>
  - <https://github.com/llvm/llvm-project>
- **Sources the enricher read:**
  - <https://github.com/google/sanitizers/wiki/AddressSanitizerComparisonOfMemoryTools>
  - <https://github.com/google/sanitizers/wiki/AddressSanitizerPerformanceNumbers>
  - <https://github.com/google/sanitizers/wiki/AddressSanitizerAlgorithm>
  - <https://github.com/google/sanitizers/wiki/AddressSanitizer>
  - <https://raw.githubusercontent.com/llvm/llvm-project/refs/heads/main/clang/docs/AddressSanitizer.md>
  - <https://raw.githubusercontent.com/llvm/llvm-project/refs/heads/main/compiler-rt/lib/asan/README.txt>
  - <https://raw.githubusercontent.com/llvm/llvm-project/refs/heads/main/LICENSE.TXT>
  - <https://github.com/llvm/llvm-project/tree/main/clang/docs>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/llvm/llvm-project`) · [data/wave11/enrich/raw/github_com_llvm_llvm_project.json](../../../data/wave11/enrich/raw/github_com_llvm_llvm_project.json) (enrichment confidence 0.8)

</details>
