# IsoAlloc

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Allocators and garbage collectors](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `Apache-2.0` · 🟢 active

> Security-hardened C11 malloc replacement (size-isolated zones, guard pages, canaries) that runs near glibc ptmalloc speed.

| | |
|---|---|
| **Beats** | glibc malloc only (the 'jemalloc' row of PERFORMANCE.md actually times IsoAlloc) |
| **Claimed result** | iso_alloc/iso_free 1834784 tests in 0.081202 s vs system malloc/free 0.662565 s; calloc 1.04 s vs 2.73 s; realloc 0.83 s vs 1.94 s (derived from page data: roughly 8x, 2.6x and 2.3x). jemalloc under the same harness: 0.0846 s, 1.46 s, 0.78 s. README text itself says 'on average IsoAlloc is faster than ptmalloc but the difference is so close it will likely not be noticeable'. |
| **Workload** | malloc_cmp_test: about 1.4 million alloc/calloc/realloc operations with every other allocation freed, run as an LD_PRELOAD comparison against system malloc, jemalloc and scudo; also mimalloc-bench graphs. |
| **Metric** | throughput |
| **Hardware** | Ubuntu 20.04.3 ARM64 docker container on a MacOS host (kernel 5.10.76-linuxkit), glibc 2.31; later perf run on an AWS t2.xlarge |
| **Adoption** | 388 stars |
| **Last commit** | 2026-05-06 |
| **Links** | [repository](https://github.com/struct/isoalloc) · [benchmark](https://github.com/struct/isoalloc/blob/master/PERFORMANCE.md) |

## Verdict

In a single-threaded micro test of about 1.8 million alloc/calloc/realloc operations (sizes 16 B-42 KB, every other one freed), the author measured IsoAlloc at 0.081 s, 1.04 s and 0.83 s vs glibc 2.31 ptmalloc at 0.66 s, 2.73 s and 1.94 s. That was on an ARM64 Ubuntu 20.04 docker container on a macOS host, clang -O2, with flags inferred from the Makefile. The 'jemalloc' row in the same table actually re-runs IsoAlloc, so it gives no jemalloc comparison, and mimalloc-bench shows IsoAlloc slower than jemalloc and mimalloc.

## Use it when

- Client-side desktop or mobile C/C++ apps with a risky attack surface (parsers, media, browsers), where heap hardening is worth some speed and memory
- Replacing glibc malloc via LD_PRELOAD (use make library_less_strict) to get double-free, canary and guard-page checks at roughly ptmalloc speed in mostly single-threaded programs
- Fuzzing and testing builds, where FUZZ_MODE, ALLOC_SANITY (GWP-ASan-like sampling) and leak detection catch bugs ASan misses (wild, unaligned and double frees)
- Code that wants explicit per-type heaps through private zones, optionally with ARM MTE on armv8.5-a

## Skip it when

- Allocation-heavy multithreaded servers: all threads share one global lock on the root; in mimalloc-bench larsonN took 1328.9 s vs about 1.0-1.2 s for jemalloc and mimalloc, and redis 7.58 vs 3.16 (je) and 2.78 (mi)
- Memory-constrained processes: RSS is several times higher than jemalloc/mimalloc (cfrac 30612 KB vs 4552/2484 KB; redis 50516 vs 9492/7084 KB) because of 4 MB zones, guard pages and canaries
- 32-bit targets (not supported); Windows (not supported); FreeBSD has only partial support with flaky CI
- When you only need speed: jemalloc or mimalloc beat it on every mimalloc-bench test except a tie on barnes
- Single allocations above 4 GB (the big-zone limit)

## How it is fast

Each zone tracks chunk state in a 2-bit-per-chunk bitmap that is scanned 64 bits at a time (with ARM NEON loops when available), so it avoids linked free lists. Several caches cut the hot path: a per-zone free-bit-slot list, a chunk-to-zone lookup table keyed on the address MSBs, a thread-local MRU zone cache (8 entries), and a thread-local free quarantine that batches frees. Default zones for 16-8192 B are created in the constructor.

## Compared with alternatives

Pick IsoAlloc over speed-first allocators like mimalloc-style siblings (v8malloc, FastAlloc, Kaname-Shiki) or Mesh when heap-exploit mitigation is the goal and you can accept higher RSS and poor multithreaded scaling. If raw throughput or memory footprint matters, pick one of those instead.

## Integration

| | |
|---|---|
| **Form** | shared lib (LD_PRELOAD/DYLD_INSERT_LIBRARIES or linked), or object files via make c_library_objects; C++ new/delete via make cpp_library |
| **Dependencies** | none beyond libc and pthreads (macOS links the Security framework) |
| **Minimum toolchain** | C11 (C++17 for the C++ interface); Makefile defaults to clang with -O2 and -flto |
| **Platforms** | 64-bit Linux and macOS (x86-64, arm64), Android arm64 via ndk-build, partial FreeBSD, minimal Solaris/Illumos |
| **Thread safety** | Thread safe with THREAD_SUPPORT=1 (default): a global pthread mutex (or spinlock with USE_SPINLOCK) guards the root, plus TLS zone caches and quarantine; THREAD_SUPPORT=0 removes locking for single-threaded programs |
| **Drop-in for the baseline** | partial: drop-in malloc replacement via LD_PRELOAD, but the default build aborts on pointers it does not own (use library_less_strict), realloc always returns a new chunk, mallopt is unsupported (#219) and macOS hooking is incomplete (#213) |

## Gotchas

- The PERFORMANCE.md 'jemalloc' row is not a jemalloc measurement: it runs LD_PRELOAD=./libjemalloc.so build/tests, but build/tests is compiled with the IsoAlloc sources and calls iso_alloc/iso_free directly (its output even prints 'iso_alloc/iso_free'), so that row times IsoAlloc again
- The malloc_cmp_test comparison uses two binaries (build/tests calling iso_\* directly, with LTO, vs build/malloc_tests calling malloc), times with clock() CPU time, and runs single-threaded on an ARM64 docker container on macOS; the perf-stat section calls the same host an 'AWS t2.xlarge' while showing armv8 PMU counters
- The mimalloc-bench table was produced with 'make library_benchmark', which turns off canaries, freelist randomization, pointer masking and ABORT_ON_UNOWNED_PTR, not the secure default configuration the text implies
- Default build behavior: aborts on unowned pointers, returns a PROT_NONE page for malloc(0), and prints leak and usage reports from the destructor in DEBUG/LEAK_DETECTOR builds; MAX_ZONES (8192) caps the total heap and causes OOM-style aborts if exceeded

## Known shortcomings

- Harness bug in PERFORMANCE.md: the 'jemalloc' row runs LD_PRELOAD=./libjemalloc.so build/tests, but build/tests links the IsoAlloc sources and calls iso_alloc directly (its output prints iso_alloc/iso_free), so that row times IsoAlloc, not jemalloc. The mimalloc-bench table was built with make library_benchmark (canaries, freelist randomization, MASK_PTRS off), not the default config. The perf-stat section says 'AWS t2.xlarge' but shows armv8 counters.

## Caveats and trade-offs

The IsoAlloc timings use build/tests while scudo and system malloc use build/malloc_tests, a different binary built from the same test source, so the rows are not strictly like for like. Compiler flags not stated. Single-threaded micro test in an ARM64 docker container on macOS, yet the perf section says 'the same AWS t2.xlarge instance as above', so the hardware description is inconsistent. The roughly 8x over system malloc contradicts the author's own prose ('the difference is so close it will likely not be noticable'). The mimalloc-bench table ('best case', not averages) shows IsoAlloc slower than jemalloc and mimalloc on every test except a tie on barnes (cfrac 4.78 s vs 3.07/2.97 s; redis 7.579 vs 3.160/2.780; larsonN 1328.904 vs about 1.0-1.2) with much higher RSS; the author says it is not ready for performance-sensitive server workloads. It is a security-hardened allocator, fast(ish) by its own description. [retier] The PERFORMANCE.md 'jemalloc' row runs LD_PRELOAD=./libjemalloc.so build/tests, but build/tests links IsoAlloc and calls iso_alloc directly, so it times IsoAlloc, not jemalloc; the mimalloc-bench table was built with make library_benchmark (canaries, freelist randomization, MASK_PTRS off); the perf-stat section says AWS t2.xlarge but shows armv8 counters; mimalloc-bench shows IsoAlloc slower than jemalloc and mimalloc (larsonN 1328 s vs about 1 s).

Security-focused allocator (guard pages, canaries, zone isolation, quarantine); 64-bit Linux and macOS only; higher memory use from bitmap zones; the author states it falls behind other allocators on some mimalloc-bench tests.

## Maintenance

Active (last commit 2026-05-06), Apache-2.0, small enough to vendor; positioned by its author as fast enough for client-side apps but not ready for performance-sensitive server workloads.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** PERFORMANCE.md shows first-party malloc_cmp_test timings against system malloc (glibc 2.31), jemalloc and scudo plus a mimalloc-bench table; test source is public but compiler and flags are not stated and the host is a docker container on macOS, so not A.
- **Verifier notes:** Numbers in claimed_speedup match the page. Real value is security hardening at near-ptmalloc speed; against jemalloc/mimalloc it is slower. Metadata: 388 stars, Apache-2.0, last commit 2026-05-06.
- **Fields the verifier corrected:** `caveats`, `baseline`
- **Shortcomings recorded by:** code reading by enricher
- **Pages the verifier opened:**
  - <https://github.com/struct/isoalloc>
  - <https://raw.githubusercontent.com/struct/isoalloc/master/PERFORMANCE.md>
  - <https://raw.githubusercontent.com/struct/isoalloc/master/README.md>
  - <https://raw.githubusercontent.com/struct/isoalloc/master/LICENSE>
  - <https://github.com/struct/isoalloc/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/struct/isoalloc/master/README.md>
  - <https://raw.githubusercontent.com/struct/isoalloc/master/PERFORMANCE.md>
  - <https://raw.githubusercontent.com/struct/isoalloc/master/Makefile>
  - <https://raw.githubusercontent.com/struct/isoalloc/master/tests/tests.c>
  - <https://raw.githubusercontent.com/struct/isoalloc/master/include/conf.h>
  - <https://raw.githubusercontent.com/struct/isoalloc/master/include/iso_alloc.h>
  - <https://raw.githubusercontent.com/struct/isoalloc/master/src/iso_alloc_interfaces.c>
  - <https://raw.githubusercontent.com/struct/isoalloc/master/MEMORY_TAGGING.md>
  - <https://raw.githubusercontent.com/struct/isoalloc/master/SECURITY_COMPARISON.MD>
  - <https://github.com/struct/isoalloc/issues?q=is%3Aissue>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/struct/isoalloc`) · [data/wave11/enrich/raw/github_com_struct_isoalloc.json](../../../data/wave11/enrich/raw/github_com_struct_isoalloc.json) (enrichment confidence 0.75)

</details>
