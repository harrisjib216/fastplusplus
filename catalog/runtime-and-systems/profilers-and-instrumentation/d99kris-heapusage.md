# heapusage

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Profilers and instrumentation](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> LD_PRELOAD/DYLD_INSERT_LIBRARIES heap-error and leak checker covering a small subset of Valgrind Memcheck without CPU emulation.

| | |
|---|---|
| **Beats** | Valgrind Memcheck |
| **Claimed result** | Qualitative: 'less performance impact than Valgrind'; for large applications that cannot run at Valgrind slowdown |
| **Workload** | LD_PRELOAD heap error and leak finder, a small subset of Memcheck functionality. |
| **Metric** | other |
| **Adoption** | 111 stars |
| **Last commit** | 2026-07-12 |
| **Links** | [repository](https://github.com/d99kris/heapusage) · [benchmark](https://github.com/d99kris/heapusage) |

## Verdict

Nothing was measured. The README says only that Heapusage 'has less performance impact than Valgrind' and is meant for applications that cannot run at Valgrind slowdown speed; no benchmark, compiler, flags or hardware are given.

## Use it when

- Finding leaks (`-t leak`) in a large program that is too slow to run under Valgrind, on a debug build.
- Embedded Linux on x86, amd64 or aarch64, or macOS, where Valgrind is unavailable or badly supported (it cannot run on current Apple Silicon macOS).
- Catching heap overflows past the end of a block and use-after-free in a binary you cannot rebuild with -fsanitize=address.
- Taking leak snapshots of a long-running process on demand with `-s SIGUSR1`.

## Skip it when

- Allocation-heavy or multithreaded code under the default `error` tool: each malloc costs at least two pages, two mprotect calls and a backtrace under a global mutex, so slowdown can be large and memory use can grow by orders of magnitude for small objects. No overhead numbers are published.
- When you need uninitialized-read detection, stack or global overflow checks, or underflow (before-start) detection; Memcheck or ASan cover these and Heapusage does not ('scribble' mode only makes such bugs more likely to show).
- Code that allocates through aligned_alloc, memalign, posix_memalign, valloc or pvalloc, or relies on malloc_usable_size; these are not intercepted.
- When you can rebuild: ASan/LSan (about 2x slowdown) finds more bug classes with exact reports.
- Third-party macOS apps without the get-task-allow entitlement, because DYLD_INSERT_LIBRARIES injection is refused.

## How it is fast

The program runs natively; only allocator calls are intercepted, unlike Valgrind, which runs the whole program on a synthetic CPU. Overflow and use-after-free detection use an electric-fence style page allocator: each block is page-aligned via posix_memalign with a PROT_NONE guard page right after it, and freed blocks are mprotect'ed PROT_NONE in a FIFO quarantine (default 10% of physical RAM), so bad accesses fault in hardware and are reported from a SIGSEGV/SIGBUS handler. The speed comes from not instrumenting loads and stores, not from making the allocator itself cheap: every allocation captures a backtrace() of up to 20 frames under one global std::mutex.

## Compared with alternatives

Pick it over AddressSanitizer or DoubleTake when you cannot recompile, and over Dr. Memory when you need macOS or aarch64 Linux support. For heap profiling rather than error finding, heaptrack or bytehound fit better, and tracing_malloc is the sibling with an actual measured speedup over Valgrind.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | pthread, libdl; bundled backward-cpp (MIT); optional binutils-dev (libbfd), libdw or libdwarf for file:line in stack traces |
| **Minimum toolchain** | C++11, CMake 3.0+ |
| **Platforms** | Linux 2.6.31+ on x86, amd64, aarch64; macOS 10.12+ (tested on macOS 15.7 and Ubuntu 24.04) |
| **Thread safety** | Thread-safe: a single global std::mutex serializes all intercepted allocator calls, with thread-local recursion guards and pthread_atfork handlers. |
| **Drop-in for the baseline** | partial — a runtime wrapper like `valgrind ./prog` with no recompilation, but it covers only leaks, double frees, past-the-end heap overflows and use-after-free, with different flags and less precise output |

## Gotchas

- Guarding allocations makes many mprotect regions; large programs can hit /proc/sys/vm/max_map_count, and the tool then exits and tells you to raise it.
- Once the quarantine (10% of RAM by default, `-q`) is full, the oldest freed blocks are really released and later use-after-free on them is no longer detected.
- Blocks are padded to 2\*sizeof(void\*), so overflows of a few bytes into that padding are not caught; only accesses that reach the guard page fault.
- Leak reports can include memory from system libraries (for example printf buffers) that would be freed at library teardown.

## Known shortcomings

- No numbers and no baseline comparison; the README makes only qualitative claims. Kept as a notable project (111 stars); directional only (tier D).
- Default error mode costs 2+ pages, an mprotect and a backtrace per malloc, all under one global std::mutex; it can hit vm.max_map_count and misses overflows that stay inside the 2\*sizeof(void\*) padding.

## Caveats and trade-offs

No numbers anywhere in the README. Provides only a small subset of Memcheck (leaks, overflows, use-after-free, double free); does not intercept aligned_alloc or posix_memalign and may report leaks from system libraries. Recommended on debug builds, like Valgrind.

Less precise than Memcheck; Linux and macOS.

## Maintenance

Actively maintained (v2.39, last commit 2026-07-12, no open issues) and BSD-3-Clause, so it is fine to use or vendor; there is no performance evidence, so treat the speed claim as directional only.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): reject; tier before verification D, tier now D.
- **Tier reason:** README only says 'Heapusage has less performance impact than Valgrind' and targets apps that cannot run at Valgrind slowdown speed; no numbers anywhere.
- **Verifier notes:** Tier D with 111 stars, so not-notable reject per prompt rules; orchestrator may override to keep with a shortcoming. Metadata confirmed: BSD-3-Clause, not archived, last commit 2026-07-12.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** code reading by enricher
- **Pages the verifier opened:**
  - <https://github.com/d99kris/heapusage>
  - <https://github.com/d99kris/heapusage/commits>
  - <https://raw.githubusercontent.com/d99kris/heapusage/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/d99kris/heapusage>
  - <https://github.com/d99kris/heapusage/issues?q=is%3Aissue>
  - <https://github.com/d99kris/heapusage/tree/master/src>
  - <https://raw.githubusercontent.com/d99kris/heapusage/HEAD/README.md>
  - <https://raw.githubusercontent.com/d99kris/heapusage/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/d99kris/heapusage/HEAD/src/humalloc.cpp>
  - <https://raw.githubusercontent.com/d99kris/heapusage/HEAD/src/humain.cpp>
  - <https://raw.githubusercontent.com/d99kris/heapusage/HEAD/src/hulog.cpp>
  - <https://raw.githubusercontent.com/d99kris/heapusage/HEAD/src/heapusage>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/d99kris/heapusage`) · [data/wave11/enrich/raw/github_com_d99kris_heapusage.json](../../../data/wave11/enrich/raw/github_com_d99kris_heapusage.json) (enrichment confidence 0.75)

</details>
