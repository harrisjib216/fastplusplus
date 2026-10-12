# memtrail

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Profilers and instrumentation](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C` · `MIT (permission headers in memtrail.cpp, memtrail.h and the memtrail script, Copyright 2011-2019 Jose Fonseca; no LICENSE file)` · 🟢 active

> LD_PRELOAD heap profiler and leak finder for Linux; claims much lower overhead than Valgrind Massif or Memcheck, unmeasured.

| | |
|---|---|
| **Beats** | Valgrind Memcheck and Massif |
| **Claimed result** | Qualitative: 'very little runtime overhead'; built because workloads 'run too slow under Valgrind' |
| **Workload** | LD_PRELOAD memory profiler and leak detector for long-running CPU-heavy workloads. |
| **Metric** | other |
| **Adoption** | 89 stars |
| **Last commit** | 2026-04-26 |
| **Links** | [repository](https://github.com/jrfonseca/memtrail) · [benchmark](https://github.com/jrfonseca/memtrail) |

## Verdict

No measurement exists: the README says only 'very little runtime overhead' and that the author's workloads ran too slowly under Valgrind's dynamic binary instrumentation. The repo's benchmark.cpp drives 262,144 4-byte allocations through random 8-deep call chains, but the `make bench` target times only `memtrail report`, not the profiled run against native or Valgrind.

## Use it when

- Finding leaks or peak-memory call sites in long-running, CPU-heavy Linux programs that are too slow to finish under Valgrind Memcheck or Massif.
- Unmodified binaries built with frame pointers or unwind tables, where you cannot recompile with AddressSanitizer or LeakSanitizer.
- Mostly single-threaded or lightly threaded code with moderate allocation rates, since every event takes one global lock.
- Taking peak and leak snapshots at chosen points in a run by calling memtrail_snapshot() from the program.

## Skip it when

- Highly multi-threaded, allocation-heavy servers: every malloc and free takes one process-wide recursive pthread mutex, so allocations are serialized across threads.
- Programs with many small allocations and tight memory: each block carries a header with a 32-entry return-address array plus list links, size and pointer (over 280 bytes on x86-64), and the library stops the program with _exit(1) once tracked bytes pass half of physical RAM.
- Bug hunting for use-after-free, overflows or uninitialized reads: it only accounts allocations; use Memcheck, AddressSanitizer or Dr. Memory.
- Non-Linux platforms: it relies on LD_PRELOAD, glibc's __libc_malloc and PTHREAD_RECURSIVE_MUTEX_INITIALIZER_NP; the header is a no-op elsewhere.
- Cases where you need a measured overhead figure: the README gives none, and benchmark.cpp with `make bench` only times the report step.

## How it is fast

The program runs natively instead of under dynamic binary instrumentation: only allocator calls are intercepted, by symbol interposition through LD_PRELOAD, and they forward to __libc_malloc and __libc_free. Each call captures up to 32 return addresses with libunwind (statically linked and chosen because it does not call malloc), and the events are buffered in PIPE_BUF-sized chunks and piped to a forked `gzip --fast` child, so compression runs on another core. Symbol resolution and tree building are deferred to the offline Python report step.

## Compared with alternatives

Choose it over heaptrack or bytehound when you want a small, self-contained tool with a pipe-to-gzip recorder and gprof2dot output; prefer heaptrack for multi-threaded programs (it does not serialize threads, per its README) and tracing_malloc when you want a published runtime number against Valgrind.

## Integration

| | |
|---|---|
| **Form** | shared lib (LD_PRELOAD) plus Python 3 driver script |
| **Dependencies** | libunwind (bundled git submodule, built static), Python 3, gzip, binutils addr2line; gprof2dot for graphs |
| **Minimum toolchain** | C++17 (gnu++17), g++ by default, autotools to build the bundled libunwind |
| **Platforms** | Linux with glibc; x86-64 assumed for 16-byte minimum alignment, other architectures fall back to sizeof(double) alignment |
| **Thread safety** | thread-safe through one global recursive mutex around all bookkeeping |
| **Drop-in for the baseline** | partial — like Valgrind it runs unmodified binaries, but it replaces only Massif- and leak-check-style accounting, not Memcheck's error detection |

## Gotchas

- Allocations made before the library has opened its output file (for example libstdc++'s emergency pool) are marked internal and left out of totals.
- Freed blocks that were already logged stay on a pending list until the next flush, so the process's real RSS under memtrail can stay above its native peak.
- Allocator calls re-entered while the lock is held are marked internal and print 'memtrail: warning: recursion', so they are missing from the report.
- Licensing: there is no LICENSE file and GitHub shows none, but memtrail.cpp, memtrail.h and the memtrail script carry MIT permission headers (Copyright 2011-2019 Jose Fonseca), so the code can be reused under those terms.

## Known shortcomings

- No numbers or baseline comparison anywhere, and no license file at the repo root. Kept as a notable project (89 stars); directional only (tier D).
- Still no overhead measurement: make bench times only the report step. One global recursive mutex serializes all mallocs, the per-block header is over 280 B, and the program is forced to _exit(1) past half of physical RAM.

## Caveats and trade-offs

No numbers; README claims 'very little runtime overhead' versus Valgrind's dynamic binary instrumentation without measurement. No LICENSE, LICENSE.txt, LICENSE.md or COPYING file at the repo root (all 404) and no license shown on the GitHub page, so it is reference-only. 89 stars.

Linux LD_PRELOAD only; less detailed than Valgrind.

## Maintenance

Active (commits on 2026-04-26 add tests and coverage, 188 commits, 0 open issues, 89 stars); MIT terms sit in the file headers despite the missing LICENSE file, so it is usable, but the speed claim against Valgrind is unmeasured.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): reject; tier before verification D, tier now D.
- **Tier reason:** README only says 'Very little runtime overhead' and that Valgrind is too slow for the author's workloads; no measurements anywhere on the page.
- **Verifier notes:** Tier D with 89 stars, so it meets the not-notable reject rule; the orchestrator may override to keep per the keep-and-document rule. License absence confirmed by 404s on common license file names; last_commit was not re-checked.
- **Fields the verifier corrected:** `caveats`, `license`, `usability`
- **Shortcomings recorded by:** code reading by enricher
- **Pages the verifier opened:**
  - <https://github.com/jrfonseca/memtrail>
  - <https://raw.githubusercontent.com/jrfonseca/memtrail/HEAD/README.md>
  - <https://raw.githubusercontent.com/jrfonseca/memtrail/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/jrfonseca/memtrail>
  - <https://github.com/jrfonseca/memtrail/commits>
  - <https://raw.githubusercontent.com/jrfonseca/memtrail/HEAD/README.md>
  - <https://raw.githubusercontent.com/jrfonseca/memtrail/HEAD/Makefile>
  - <https://raw.githubusercontent.com/jrfonseca/memtrail/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/jrfonseca/memtrail/HEAD/memtrail.h>
  - <https://raw.githubusercontent.com/jrfonseca/memtrail/HEAD/memtrail.cpp>
  - <https://raw.githubusercontent.com/jrfonseca/memtrail/HEAD/memtrail>
  - <https://raw.githubusercontent.com/jrfonseca/memtrail/HEAD/benchmark.cpp>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/jrfonseca/memtrail`) · [data/wave11/enrich/raw/github_com_jrfonseca_memtrail.json](../../../data/wave11/enrich/raw/github_com_jrfonseca_memtrail.json) (enrichment confidence 0.7)

</details>
