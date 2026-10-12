# tracing_malloc

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Profilers and instrumentation](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `no license` · 🟢 active

> Linux LD_PRELOAD malloc hook that records live allocations with stack traces; far lower overhead than Valgrind for leak hunting.

| | |
|---|---|
| **Beats** | Valgrind (memcheck default tool) |
| **Claimed result** | real time 5.375 s native, 6.888 s with tracing_malloc, 53.204 s under valgrind (about 7.7x less wall time than valgrind, derived from page data) |
| **Workload** | Run of an Unreal Engine 4 example server for about 5 s, native vs LD_PRELOAD tracing_malloc vs valgrind. |
| **Metric** | latency |
| **Adoption** | 8 stars |
| **Last commit** | 2026-05-25 |
| **Links** | [repository](https://github.com/dpull/tracing_malloc) · [benchmark](https://github.com/dpull/tracing_malloc) |

## Verdict

One first-party `time` run of a UE4 ExampleServer (about 5 s, -ansimalloc): real 5.375 s native, 6.888 s under tracing_malloc, 53.204 s under default Valgrind (memcheck), with no hardware, compiler or repeat counts given. CPU time tells a sharper story than wall time: user+sys 0.97 s native, 2.61 s with tracing_malloc (about 2.7x) and 49.3 s under Valgrind (about 19x more than tracing_malloc) (derived from page data); the native run is mostly idle, so the 28% wall-clock overhead understates the hook's cost.

## Use it when

- Finding leaks or memory growth in large Linux C/C++ servers (the README example is a UE4 dedicated server) that are too slow to run under Valgrind.
- Observing which call stacks hold memory at a given moment in a long-running process, without rebuilding it.
- Quick x86-64 Linux investigations where you can build libunwind 1.3.1 and a CMake shared library.

## Skip it when

- Detecting invalid reads/writes, use-after-free or uninitialised memory: it only tracks allocation lifetimes, unlike Valgrind memcheck or ASan.
- Allocation-heavy multithreaded programs: every malloc takes a full libunwind backtrace and one global mutex, and freed slots become tombstones that are never compacted, so probe chains can grow over long runs.
- Processes with more than 8,388,608 (RECORD_MAX_COUNT) live allocations: further records are silently dropped when the table fills.
- Non-Linux targets, or when you need memalign/valloc/pvalloc/reallocarray or mmap-based allocations tracked (not hooked).
- Projects that need a license: no LICENSE file is in the repository.

## How it is fast

It does far less work than Valgrind: no dynamic binary translation or shadow memory, only a dlsym(RTLD_NEXT) forward to the real allocator plus a libunwind unw_backtrace and an insert into a fixed-size open-addressing (linear probing) table guarded by one pthread mutex. Records live directly in a MAP_SHARED file, so there is no serialization step and the data survives a crash.

## Compared with alternatives

Pick it over heaptrack or bytehound only when you want a tiny, readable LD_PRELOAD hook whose records sit in a crash-surviving mmap file; heaptrack and bytehound are more complete heap profilers, and AddressSanitizer or Dr. Memory are the choice when you also need access-error detection.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | libunwind (static unwind.a, build_libunwind fetches v1.3.1), libdl, pthread; Python for the analysis tools |
| **Minimum toolchain** | C11, CMake 3.5 |
| **Platforms** | Linux (LD_PRELOAD, /proc, sbrk); 64-bit only (static assert sizeof(void\*) == 8) |
| **Thread safety** | Inserts and removes are serialized by one pthread mutex; record_update's lookup and the field writes after hashmap_add run outside the lock |
| **Drop-in for the baseline** | partial: replaces valgrind --leak-check style leak finding via LD_PRELOAD on unmodified binaries, but provides none of memcheck's access checking |

## Gotchas

- At startup hashmap_create writes the pointer field of all 8M 256-byte slots, so each traced process touches a 2 GiB MAP_SHARED file in /tmp (plus a .maps copy); forked children create their own.
- free() calls the real free before removing the record, and record_update looks up without the mutex, so under threads an address reused by another thread can race with its stale record.
- Hash slot is pointer % 8M; allocator pointers are 16-byte aligned, so only one slot in 16 is a home slot and linear-probe clusters form.
- Bash processes are skipped on purpose (is_bash), and calloc's pre-init fallback multiplies nmemb\*size without an overflow check.

## Known shortcomings

- Wall time understates the cost: the native run is mostly idle; CPU user+sys is 0.97 s native, 2.61 s traced (about 2.7x, derived) and 49.3 s under valgrind. Each process touches a 2 GiB MAP_SHARED /tmp file at startup (8M x 256 B slots), records beyond 8,388,608 live allocations are silently dropped, tombstones are never compacted, there is a free/record race and the record_update lookup runs without the mutex. No LICENSE.

## Caveats and trade-offs

Single run, no compiler flags, hardware or repeat counts; no LICENSE file found at repo root via raw fetch (license unconfirmed, so marked reference); the tools compare different things (leak tracking vs full memcheck).

Linux LD_PRELOAD allocation tracker and leak detector; does not detect invalid accesses like memcheck.

## Maintenance

Small single-author project (8 stars, 89 commits, last commit 2026-05-25) with no license file, so reference only; the code is short enough to read in an hour and reimplement.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** README Performance section shows first-party `time` output for the UE4 ExampleServer: real 5.375 s native, 6.888 s with LD_PRELOAD tracing_malloc, 53.204 s under valgrind; no compiler flags (beyond RelWithDebInfo build instruction), hardware or repeats, so C.
- **Verifier notes:** Numbers match the README exactly; 7.7x ratio is correctly marked derived. No LICENSE, LICENSE.txt or LICENSE.md at repo root (raw fetch 404) and github.com shows no license, so reference stands. Last commit date not re-checked.
- **Shortcomings recorded by:** code reading by enricher
- **Pages the verifier opened:**
  - <https://github.com/dpull/tracing_malloc>
  - <https://raw.githubusercontent.com/dpull/tracing_malloc/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/dpull/tracing_malloc>
  - <https://raw.githubusercontent.com/dpull/tracing_malloc/HEAD/README.md>
  - <https://github.com/dpull/tracing_malloc/tree/master/src>
  - <https://github.com/dpull/tracing_malloc/tree/master/tools>
  - <https://github.com/dpull/tracing_malloc/commits/master>
  - <https://raw.githubusercontent.com/dpull/tracing_malloc/HEAD/src/CMakeLists.txt>
  - <https://raw.githubusercontent.com/dpull/tracing_malloc/HEAD/src/tracing_malloc.h>
  - <https://raw.githubusercontent.com/dpull/tracing_malloc/HEAD/src/tracing_malloc_hook.c>
  - <https://raw.githubusercontent.com/dpull/tracing_malloc/HEAD/src/tracing_malloc_record.c>
  - <https://raw.githubusercontent.com/dpull/tracing_malloc/HEAD/src/tracing_malloc_stacktrace.c>
  - <https://raw.githubusercontent.com/dpull/tracing_malloc/HEAD/src/tracing_malloc_hashmap.c>
  - <https://raw.githubusercontent.com/dpull/tracing_malloc/HEAD/src/tracing_malloc_hashmap.h>
  - <https://raw.githubusercontent.com/dpull/tracing_malloc/HEAD/build_libunwind>
  - <https://raw.githubusercontent.com/dpull/tracing_malloc/HEAD/LICENSE>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/dpull/tracing_malloc`) · [data/wave11/enrich/raw/github_com_dpull_tracing_malloc.json](../../../data/wave11/enrich/raw/github_com_dpull_tracing_malloc.json) (enrichment confidence 0.75)

</details>
