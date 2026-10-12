# v8malloc

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Allocators and garbage collectors](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `Apache-2.0` · 🟢 active

> Early-stage Linux malloc replacement (LD_PRELOAD) claiming parity or small wins over glibc, tcmalloc, jemalloc and mimalloc on microbenchmarks.

| | |
|---|---|
| **Beats** | glibc malloc, jemalloc, tcmalloc, mimalloc |
| **Claimed result** | MB-02 64 B scalability: 4 threads 150.5 M ops/s vs 134.9 glibc, 122.6 tcmalloc, 124.1 jemalloc, 102.6 mimalloc (12% over glibc); 8 threads 296.4 M vs 295.2 glibc, 290.8 tcmalloc, 271.3 jemalloc, 217.5 mimalloc (within noise of glibc and tcmalloc); MB-01 8 B 22 ns/op vs 23 glibc and tcmalloc, 26 jemalloc, 32 mimalloc; MB-06 256 MiB alloc p99 1 us vs 48 glibc, 8 jemalloc, 2 tcmalloc, 160 mimalloc; MB-05 RSS 9.13 MiB, tied with glibc, vs 19.50 tcmalloc and 27.50 jemalloc. Slower on MB-01 16-256 KiB (59-62 vs 24 ns tcmalloc), MB-03 producer/consumer and MB-04 mixed (11.50 vs 22.26 M tcmalloc, 15.42 M glibc). |
| **Workload** | Microbenchmarks MB-01 to MB-06: single-thread 8-byte alloc, 8-thread scalability, mixed workload, fragmentation RSS, 256 MiB allocation p99 latency. |
| **Metric** | throughput |
| **Hardware** | Intel Core Ultra 5 236V (8-core dev container) |
| **Compiler and flags** | Clang Release, -flto=auto |
| **Adoption** | 1 star |
| **Last commit** | 2026-04-28 |
| **Links** | [repository](https://github.com/iqbqioza/v8malloc) · [benchmark](https://github.com/iqbqioza/v8malloc) |

## Verdict

The README reports single runs of in-tree microbenchmarks MB-01 to MB-06 on an 8-core Intel Core Ultra 5 236V dev container: v8malloc as a clang Release LTO build, competitors as Debian Trixie libjemalloc.so.2, libtcmalloc.so.4 and libmimalloc.so.3 under LD_PRELOAD. The clear margins are 150.5 M vs 134.9 M ops/s (glibc) at 4 threads on 64 B, 256 MiB alloc p99 of 1 us, and the lowest RSS (tied with glibc); most other wins are within the author's own noise band. As shown in the gotchas, the documented harness cannot isolate the competitor allocators, so the comparison is unreliable until the build used is documented.

## Use it when

- Experimenting on Linux with a drop-in LD_PRELOAD allocator for long-running services where steady-state RSS matters (MB-05 RSS 9.13 MiB vs 19.50 tcmalloc and 27.50 jemalloc)
- Workloads that repeatedly allocate very large buffers (256 MiB alloc p99 1 us vs mimalloc 160 and glibc 48 in the README)
- When you want built-in heap observability (pprof dumps, lifetime histograms, NUMA balance) and are willing to benchmark it on your own workload first

## Skip it when

- Production use today: 1 star, self-described as in active development with most internals still being implemented, and a concurrency bug (MB-03 SEGV in v8m_core_cache_pop_batch) fixed during the very run that produced the table
- Medium allocations of 16-256 KiB: about 60 ns/op vs tcmalloc's 24 ns/op on MB-01, and mixed workloads (MB-04 11.50 M ops/s vs tcmalloc 22.26 M and glibc 15.42 M)
- Cross-thread producer/consumer patterns, where mimalloc and glibc lead MB-03
- Non-Linux platforms, or when you need AddressSanitizer (unsupported) or ThreadSanitizer (experimental)

## How it is fast

A four-tier path: lock-free thread-local cache, per-CPU core cache, NUMA-node pool, then a global page heap, with an MPSC remote-free queue and page-owner-CPU routing for cross-thread frees. It uses header-less per-page metadata with O(1) pointer-to-metadata lookup, a branchless lookup over 41 size classes (8 B to 2 MiB), a buddy pool behind a medium-class thread cache for 16-256 KiB, and a recycle cache that keeps freed large regions mapped. The release build relies on LTO, -fno-plt, -fno-semantic-interposition and branch hints to inline the fast path.

## Compared with alternatives

Among general-purpose replacements, Mesh is the published, peer-reviewed choice for cutting RSS and FastAlloc publishes more comparison cells; pick v8malloc only to experiment with a Linux-only allocator that has built-in pprof/NUMA diagnostics, and validate its numbers yourself first.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | pthread, libdl; Linux kernel 5.4+ |
| **Minimum toolchain** | C, GCC 13+ or Clang 16+, CMake 3.25+ (lld or llvm-ar needed for clang Release static builds with thin LTO) |
| **Platforms** | Linux only: x86_64, aarch64, riscv64, ppc64le, s390x, loongarch64 (non-x86 tested under QEMU-user) |
| **Thread safety** | thread-safe malloc replacement (thread-local and per-CPU caches, MPSC remote free); TSan runs are experimental and the suite does not pass under it |
| **Drop-in for the baseline** | yes |

## Gotchas

- Harness flaw: bench/CMakeLists.txt links the benchmarks against v8malloc_static whenever V8MALLOC_BUILD_STATIC is ON (the default, also used by bench-weekly.yml), and the static archive defines malloc/free in v8m_api_libc_compat.c, so the executable's own malloc calls bind to v8malloc and LD_PRELOAD of jemalloc, tcmalloc or mimalloc cannot change them. In a shared build, libv8malloc.so is a NEEDED dependency that interposes libc, so the 'glibc (system malloc)' row of bench-compare.sh also runs v8malloc. The README does not say how its competitor columns were built; the glibc column matching v8malloc almost cell for cell on MB-01 and exactly on MB-05 (9.13 MiB) is consistent with this.
- MB-01 and MB-02 call clock_gettime (now_ns()) on every iteration, so the 21-32 ns/op figures include a clock read and compress real allocator differences.
- AddressSanitizer bypasses v8malloc entirely (ASan interposes malloc); use Valgrind or the UBSan build instead.
- The library constructor makes early mmap reservations and the shared object is built with initial-exec TLS, so it must be loaded at exec time (LD_PRELOAD or link), not dlopen()ed later.

## Known shortcomings

- Harness flaw, inferred from the code and not run: bench/CMakeLists.txt links the benches against v8malloc_static by default (V8MALLOC_BUILD_STATIC ON, also in bench-weekly.yml), and the static archive defines malloc and free (src/v8m_api_libc_compat.c), so LD_PRELOAD rows for jemalloc, tcmalloc and mimalloc cannot change the bench's allocator. In the shared build libv8malloc.so is a NEEDED entry, so the 'glibc (system malloc)' row of bench-compare.sh also runs v8malloc. That fits the glibc column tying v8malloc on MB-01 and matching exactly on MB-05 RSS (9.13 MiB). MB-01 and MB-02 call clock_gettime every iteration; the README does not say how the competitor columns were built.

## Caveats and trade-offs

Each cell is a single run in an 8-core dev container, and the README itself says to treat single-digit-percent gaps as noise, which covers most of the wins (8-thread MB-02 is 0.4% over glibc, MB-01 small sizes within 1 ns). The clear wins are MB-02 at 4 threads, 256 MiB p99 latency and fragmentation RSS. The README shows it behind tcmalloc and glibc on the mixed workload (11.50 vs 22.26 and 15.42 M ops/s), about 2.5x slower than tcmalloc on 16-256 KiB allocations, and behind mimalloc and glibc on producer/consumer. Clang version not stated; README's make release target uses GCC while the table used clang. Status line says most allocator internals are still being implemented, and this run included a concurrency bug fix in v8m_core_cache_pop_batch (MB-03 SEGV). Linux only. 1 star; not run. [retier] Competitor columns may not measure the stated allocators: benches link v8malloc_static by default (the static archive defines malloc/free), so LD_PRELOAD rows cannot change the allocator and the shared-build 'glibc' row also runs v8malloc (inferred from bench/CMakeLists.txt and bench-compare.sh, not run); the README does not say how competitor columns were built; MB-01/MB-02 call clock_gettime every iteration; most wins are inside the author's own single-run noise band.

Linux only; early-stage; AddressSanitizer unsupported, ThreadSanitizer experimental.

## Maintenance

Active (171 commits, last commit 2026-04-28) and Apache-2.0, but a 1-star, self-described early-stage project whose benchmark harness has a linkage flaw; treat it as experimental.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification A, tier now C.
- **Tier reason:** README Cross-allocator comparison runs the in-tree bench/mb_01..mb_06 programs via scripts/bench-compare.sh with LD_PRELOAD of Debian Trixie glibc, jemalloc, tcmalloc and mimalloc; v8malloc built as a clang Release build with -flto=auto, on an Intel Core Ultra 5 236V. Code, compiler, flags and CPU are stated (the clang version is not), so A is kept at the margin.
- **Retiered** A to C: Downgraded from A. Enricher read bench/CMakeLists.txt and bench-compare.sh (inferred, not run): the benches link v8malloc_static by default, and the static archive defines malloc and free, so the LD_PRELOAD jemalloc/tcmalloc/mimalloc rows cannot change the bench's allocator; in the shared build the 'glibc (system malloc)' row also runs v8malloc. The glibc column tying v8malloc on MB-01 and matching exactly on MB-05 RSS (9.13 MiB) fits that. The README does not say how the competitor columns were built, so the comparison cannot be reproduced from public sources.
- **Verifier notes:** All numbers in the record appear in the README tables. claimed_speedup now leads with the 4-thread result, since the 8-thread margin the record led with is inside the author's own noise band. Glibc is the default here, and the README gives baseline numbers for all four incumbents.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** code reading by enricher
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/iqbqioza/v8malloc/HEAD/README.md>
  - <https://raw.githubusercontent.com/iqbqioza/v8malloc/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/iqbqioza/v8malloc/HEAD/bench/mb_02_scalability.c>
  - <https://raw.githubusercontent.com/iqbqioza/v8malloc/HEAD/scripts/bench-compare.sh>
  - <https://github.com/iqbqioza/v8malloc/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/iqbqioza/v8malloc/HEAD/README.md>
  - <https://raw.githubusercontent.com/iqbqioza/v8malloc/HEAD/scripts/bench-compare.sh>
  - <https://raw.githubusercontent.com/iqbqioza/v8malloc/HEAD/bench/CMakeLists.txt>
  - <https://raw.githubusercontent.com/iqbqioza/v8malloc/HEAD/bench/mb_01_throughput.c>
  - <https://raw.githubusercontent.com/iqbqioza/v8malloc/HEAD/bench/mb_02_scalability.c>
  - <https://raw.githubusercontent.com/iqbqioza/v8malloc/HEAD/bench/mb_05_fragmentation.c>
  - <https://raw.githubusercontent.com/iqbqioza/v8malloc/HEAD/bench/mb_06_large_latency.c>
  - <https://raw.githubusercontent.com/iqbqioza/v8malloc/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/iqbqioza/v8malloc/HEAD/src/v8m_api.c>
  - <https://raw.githubusercontent.com/iqbqioza/v8malloc/HEAD/src/v8m_api_libc_compat.c>
  - <https://raw.githubusercontent.com/iqbqioza/v8malloc/HEAD/include/v8malloc/v8malloc.h>
  - <https://raw.githubusercontent.com/iqbqioza/v8malloc/HEAD/.github/workflows/bench-weekly.yml>
  - <https://github.com/iqbqioza/v8malloc/tree/main/src>
  - <https://github.com/iqbqioza/v8malloc>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/iqbqioza/v8malloc`) · [data/wave11/enrich/raw/github_com_iqbqioza_v8malloc.json](../../../data/wave11/enrich/raw/github_com_iqbqioza_v8malloc.json) (enrichment confidence 0.7)

</details>
