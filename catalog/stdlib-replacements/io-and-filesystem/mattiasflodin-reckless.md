# reckless

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [I/O and filesystem](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Asynchronous C++ logging library, drastically lower caller-side latency than std::fstream/fprintf and other async loggers.

| | |
|---|---|
| **Beats** | std::fstream, fprintf (stdio) |
| **Claimed result** | Relative average call latency (reckless = 1.00). Periodic calls: fstream 41.32, stdio 43.77, spdlog 40.85, boost_log 67.42, g3log 78.19. Call burst: spdlog 1.93, fstream 2.36, stdio 2.55. Disk I/O: stdio 17.01, spdlog 23.82, fstream 5719.93. Mandelbrot overhead: single thread fstream 10.73, stdio 12.21, spdlog 9.21; 8 threads fstream 4.62, stdio 3.70. The page concludes: 'For low loads, the speed advantage over a simple fprintf can be a factor of 40.' |
| **Workload** | Caller-side log-call latency in four scenarios. (1) Single-threaded periodic calls that never fill the buffer. (2) A call burst that fills the buffer. (3) Disk I/O: 2048 log entries interleaved with writing 64 GiB of data. (4) A Mandelbrot computation that logs \~1M lines with 1-8 worker threads (total runtime over 100 runs, overhead vs no-op). Baselines are std::fstream (std::flush after each line) and fprintf (fflush after each call), plus spdlog, g3log and Boost.Log. |
| **Metric** | latency |
| **Hardware** | AMD Ryzen 7 2700X @ 3.7GHz, 8 cores (SMT off); Samsung 970 EVO 1TB SSD (+ WD Red 3TB HDD for disk-I/O scenario); 32GB RAM; Linux kernel 4.14.65 |
| **Compiler and flags** | gcc 7.3.0 (stated on the benchmark page). The benchmarks are built with tup (benchmarks/Tupfile.lua + Tuprules.lua), which on Linux compiles with g++ -O3 -ggdb3 -std=c++11 -Wall -Werror unless DEBUG=yes (then -O0). The page itself does not restate the flags. |
| **Adoption** | 510 stars |
| **Last commit** | 2021-04-10 |
| **Links** | [repository](https://github.com/mattiasflodin/reckless) · [benchmark](https://github.com/mattiasflodin/reckless/blob/master/doc/performance.md) |

## Verdict

First-party benchmarks (doc/performance.md, gcc 7.3.0, AMD Ryzen 7 2700X @3.7GHz, libstdc++) show reckless's caller-side latency far below std::fstream (flushed per line) and fprintf (fflush per call): about 41-44x lower under light periodic load, and up to \~5720x lower than fstream in the disk-I/O scenario, though this compares an async design against baselines that synchronously flush every line, not raw I/O throughput.

## Use it when

- Latency-sensitive hot paths that log frequently but can tolerate async/eventual persistence
- Single-threaded or lightly-threaded workloads where formatting cost on a shared background thread won't bottleneck
- Windows or Linux targets on x86-family hardware; C++11-only codebases
- Willing to vendor/pin an unmaintained MIT library instead of using an actively developed logger
- Need low overhead specifically vs. synchronous std::fstream/fprintf-with-flush logging

## Skip it when

- Need macOS/BSD support (README: OS X unsupported, BSD only 'on the roadmap')
- High log-argument volume from many parallel threads, since all formatting funnels through one background thread (README calls this out as a scalability limit)
- Passing pointers/references to short-lived data without ensuring they outlive the flush (dangling-pointer risk by design)
- Need guaranteed-precise float formatting: custom float-to-string algorithm mismatches the exact/shortest round-trip representation for roughly 0.6% of values per the manual's own stats
- Want an actively maintained project: last commit 2021-04-10, open ThreadSanitizer data-race report (#35) unresolved

## How it is fast

Call site only pushes args onto a lockless MPSC ring buffer (mpsc_ring_buffer.hpp) shared with the writer thread, so the common case costs about one function call with no kernel transition, no lock, and no formatting or I/O on the caller's thread. Formatting and writing happen entirely on the background thread, and bursts of queued entries are batched into fewer I/O operations. Uses a home-grown float-to-string routine (template_formatter) instead of the standard library's, trading some accuracy for speed.

## Compared with alternatives

No siblings catalogued yet in this category target std::fstream/fprintf directly the way reckless does; CPath and FastReader address filesystem traversal and file reads, not logging, so they aren't substitutes for this use case.

## Integration

| | |
|---|---|
| **Form** | static lib (built via Make/CMake/Visual Studio; not header-only) |
| **Dependencies** | pthread (POSIX threads) on Linux; no other third-party deps for core library |
| **Minimum toolchain** | C++11 (CMakeLists.txt sets CMAKE_CXX_STANDARD 11); GCC-compatible compiler or MSVC/Visual Studio |
| **Platforms** | Windows and Linux only; no macOS/OS X, BSD listed as roadmap-only; no stated architecture restriction beyond x86 cache-line-size assumptions in the buffer sizing docs |
| **Thread safety** | Multiple threads may call write/debug/info/warn/error concurrently (lockless input queue); worker_thread() access for priority/affinity tuning is documented as unsafe to misuse (moving/detaching it breaks the library); an open issue (#35) reports ThreadSanitizer-flagged data races the maintainer has not resolved |
| **Drop-in for the baseline** | partial — explain: not source-compatible with std::fstream/fprintf; requires constructing a writer + policy_log/severity_log object and using its typed write methods instead of ostream operators or printf |

## Gotchas

- Passing log arguments by pointer/reference requires the referenced data to stay valid until the log is flushed or closed; prefer std::string/shared_ptr/unique_ptr for dynamic data
- Crash safety requires explicit handling (panic_flush/crash_handler) since unflushed async data can be lost on crash, same class of issue as buffered fprintf but easier to overlook
- Custom float-to-string formatter is not always the shortest round-trip representation: manual reports 98.5% exact match and 99.4% correct-but-sometimes-longer over 100M random values
- worker_thread() exposes the internal std::thread for OS-level tuning (priority/affinity) but destructive operations on it (move/detach) will break the logger

## Caveats and trade-offs

The benchmark is first-party. reckless is asynchronous (formatting and writing happen on a background thread), while the fstream/stdio baselines flush after every line. So the win is caller-side latency under an async-vs-synchronous-flush design, not raw I/O throughput. The figures use 2019-era versions of the competitors (spdlog 1.3.1, g3log 1.3.2, Boost 1.65). GitHub's license detector reports NOASSERTION, but LICENSE.txt is standard MIT text. The last commit on master is 2021-04-10 (a 'next' branch has 2022-07-17 commits); the repo's pushed_at of 2023-10-22 matches no branch head.

Async design allows passing raw pointers to the background writer thread for speed, at the cost of dangling-pointer risk if misused; trades some floating-point formatting precision for performance; writes are backgrounded/batched rather than immediate, with a configurable buffer size trading latency spikes against memory use.

## Maintenance

Abandoned: last commit on master 2021-04-10, no newer maintenance activity found; MIT licensed and small enough to vendor, but an unresolved ThreadSanitizer data-race report (#35) and a still-open VS2019 compile-error issue (#45) are unpatched.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded from C. The benchmark code is public (benchmarks/periodic_calls.cpp, call_burst.cpp, write_files.cpp, benchmark_mandelbrot.cpp), built via benchmarks/Tupfile.lua + Tuprules.lua, which uses g++ -O3 -std=c++11 for non-DEBUG Linux builds. doc/performance.md states gcc 7.3.0 and an AMD Ryzen 7 2700X, and runs directly against std::fstream and stdio. The 'first-party caps at C' reasoning in the record misreads the rules, which say who ran the benchmark does not matter.
- **Verifier notes:** The record wrongly said fstream was not in the disk-I/O scenario; it is, at 5719.93x relative latency. The A tier assumes the published runs used the default non-DEBUG tup build (-O3); the page does not say so explicitly. The master branch was last committed in 2021-04, so it is abandoned, not stale.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `last_commit`, `maintenance_status`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/mattiasflodin/reckless>
  - <https://github.com/mattiasflodin/reckless/blob/master/doc/performance.md>
  - <https://github.com/mattiasflodin/reckless/blob/master/Tuprules.lua>
  - <https://github.com/mattiasflodin/reckless/blob/master/benchmarks/Tupfile.lua>
  - <https://github.com/mattiasflodin/reckless/blob/master/Makefile>
  - <https://github.com/mattiasflodin/reckless/blob/master/LICENSE.txt>
- **Sources the enricher read:**
  - <https://github.com/mattiasflodin/reckless>
  - <https://github.com/mattiasflodin/reckless/blob/master/doc/performance.md>
  - <https://github.com/mattiasflodin/reckless/blob/master/README.md>
  - <https://github.com/mattiasflodin/reckless/blob/master/doc/manual.md>
  - <https://github.com/mattiasflodin/reckless/blob/master/CMakeLists.txt>
  - https://github.com/mattiasflodin/reckless (file tree via git trees API)
  - https://github.com/mattiasflodin/reckless/issues (all issues, state=all)
  - <https://github.com/mattiasflodin/reckless/issues/35>
  - https://github.com/mattiasflodin/reckless/blob/master/LICENSE.txt (per verification block)
  - https://github.com/mattiasflodin/reckless/blob/master/Tuprules.lua (per verification block)
  - https://github.com/mattiasflodin/reckless/blob/master/benchmarks/Tupfile.lua (per verification block)
  - https://github.com/mattiasflodin/reckless/blob/master/Makefile (per verification block)
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/mattiasflodin/reckless`) · [data/wave1/enrich/raw/github_com_mattiasflodin_reckless.json](../../../data/wave1/enrich/raw/github_com_mattiasflodin_reckless.json) (enrichment confidence 0.8)

</details>
