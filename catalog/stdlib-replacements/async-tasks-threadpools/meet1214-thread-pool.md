# meet1214/thread-pool

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Async tasks and thread pools](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `no license` · 🟢 active

> Header-only C++17 fixed-size thread pool with typed futures and exception propagation, beats std::async by reusing worker threads.

| | |
|---|---|
| **Beats** | std::async |
| **Claimed result** | ThreadPool(4 threads) 10ms vs std::async 18ms = 1.8x faster (derived from page data); ThreadPool(8 threads) 7ms vs std::async 18ms = 2.6x faster (derived from page data); README states 6.8x speedup for the pool vs 3.8x for std::async, both relative to the 68ms single-threaded baseline |
| **Workload** | 100 CPU-bound tasks (std::sqrt loop, 100k iterations each) on an unspecified 4-core Linux machine; single-threaded, std::async, and the pool at 2/4/8 threads. |
| **Metric** | latency |
| **Hardware** | "4-core Linux machine" (no CPU model or compiler stated) |
| **Adoption** | 0 stars |
| **Last commit** | 2026-04-01 |
| **Links** | [repository](https://github.com/meet1214/thread-pool) · [benchmark](https://github.com/meet1214/thread-pool#benchmark-results) |

## Verdict

README's own benchmark/benchmark.cpp, run once on an unspecified 4-core Linux box with no compiler or flags stated, timed 100 std::sqrt-loop tasks: single-threaded 68ms, std::async 18ms (3.8x), ThreadPool at 4 threads 10ms (6.8x) and at 8 threads 7ms (9.7x) — all relative to the single-threaded run; against std::async directly that's about 1.8x (4 threads) to 2.6x (8 threads) faster.

## Use it when

- Many short-lived CPU-bound tasks where std::async's per-call thread spawn is the dominant cost
- You want a drop-in-shaped replacement for ad-hoc std::async fan-out with typed futures and exception propagation
- A single-header dependency is acceptable and you can vendor code without a LICENSE file being a blocker (internal/prototype use)
- A fixed, known worker count is fine and you don't need cancellation or priorities
- Teaching/reference use: the README's architecture section is a clear worked example of the packaged_task + shared_ptr pattern for storing move-only tasks in std::function

## Skip it when

- Any production dependency where a license is required — there is no LICENSE file despite an MIT badge in the README (404 on GitHub)
- Workloads needing task cancellation, priorities, or dynamic pool resizing — none are implemented
- High task-submission-rate workloads — single global queue/mutex/condvar means no work stealing and one contention point across all workers
- Any decision that needs trustworthy performance numbers — the published benchmark shows superlinear speedup (3.2x on 2 threads, 9.7x on 8 threads, all on a 4-core machine), a single untimed-repetition run, and an unoptimized default build
- Projects wanting an actively maintained, community-vetted pool — 0 stars, single author, no issues or PRs, so no external validation exists

## How it is fast

Amortizes thread-creation cost: std::async(std::launch::async, ...) typically spawns a fresh OS thread per call, while ThreadPool spawns n threads once and reuses them across all submitted tasks via a locked queue. Workers block on a condition_variable when idle (no busy-waiting). No lock-free structures, work stealing, or SIMD — the entire speedup story is 'don't call clone()/pthread_create() 100 times.'

## Compared with alternatives

Pick this only as a tiny, license-free-to-check, easy-to-read reference implementation of the packaged_task/shared_ptr pattern; for real use, BS::thread_pool (also header-only, mature, widely used) or utl::parallel (also targets std::async, with a somewhat more detailed benchmark) are safer choices since both have far more scrutiny and, in BS::thread_pool's case, an actual license.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none for the library itself; tests/benchmark build pulls GoogleTest via CMake FetchContent (test-only) |
| **Minimum toolchain** | C++17, CMake 3.14+ for the provided build (GCC/Clang, exact versions not documented) |
| **Platforms** | not documented beyond "4-core Linux machine"; implementation uses only &lt;thread&gt;/&lt;mutex&gt;/&lt;condition_variable&gt;/&lt;atomic&gt;/&lt;future&gt; so it should build anywhere a C++17 std library is available, but only Linux is exercised |
| **Thread safety** | submit() locks queue_mutex_ so concurrent submission from multiple threads is safe by inspection; not explicitly documented as thread-safe anywhere in the README |
| **Drop-in for the baseline** | partial — explain: call shape changes from std::async(std::launch::async, f, args...) to pool.submit(f, args...) on a pre-constructed ThreadPool object; futures behave the same |

## Gotchas

- No LICENSE file exists despite the README's MIT badge — legal status of reuse is actually undefined
- CMakeLists.txt sets no CMAKE_BUILD_TYPE and only passes -Wall -Wextra, so the documented `cmake -B build && cmake --build build` produces an unoptimized (likely -O0) benchmark and test build
- Single shared queue/mutex/condvar design (no work stealing) means throughput will not scale past the point where lock contention dominates, unlike pools built for high task-submission rates
- The benchmark's std::async row spawns 100 OS threads for 100 tasks, so the reported 'ThreadPool beats std::async' number is largely measuring thread-creation overhead, not scheduling efficiency

## Caveats and trade-offs

No CPU model, compiler or optimization flags are stated. CMakeLists.txt sets no CMAKE_BUILD_TYPE and only -Wall -Wextra, so the documented `cmake -B build` produces an unoptimized build, likely -O0 (Tier C cap). Each variant is timed once at millisecond resolution, with no repetitions or warm-up; the single-threaded baseline runs first. The table shows implausible superlinear speedups on a 4-core machine (3.2x with 2 threads, 9.7x with 8 threads), which points to measurement artifacts. The std::async variant spawns 100 OS threads, so the win mostly measures thread-creation overhead. There is no LICENSE file (404) despite an MIT badge in the README, so usability is 'reference'. Zero stars; single-author project.

No task cancellation, no priorities, fixed thread count, no work stealing; simple single-queue design.

## Maintenance

Repo shows recent activity (last push 2026-04-01, marked active) but has zero stars, one author, no issues/PRs, and no LICENSE file, so despite MIT branding it is usable only as a reference, not a dependency to actually take on.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The README benchmark table compares ThreadPool against std::async (std::launch::async) using the public benchmark/benchmark.cpp. It gives no CPU model or compiler, and CMakeLists.txt sets no build type or -O flags, so the documented build is unoptimized by default. First-party numbers with thin methodology: Tier C.
- **Verifier notes:** The claimed numbers match the README table (10ms/7ms vs 18ms; 6.8x and 3.8x vs the 68ms single-threaded run) and the derived markers are present. The record is kept at Tier C, but the evidence is weak: likely unoptimized build, single run, superlinear speedups. Metadata matches: no license, 0 stars, last commit 2026-04-01, active.
- **Fields the verifier corrected:** `caveats`
- **Pages the verifier opened:**
  - <https://github.com/meet1214/thread-pool>
  - <https://github.com/meet1214/thread-pool#benchmark-results>
  - <https://github.com/meet1214/thread-pool/blob/main/benchmark/benchmark.cpp>
  - <https://github.com/meet1214/thread-pool/blob/main/CMakeLists.txt>
- **Sources the enricher read:**
  - <https://github.com/meet1214/thread-pool>
  - <https://github.com/meet1214/thread-pool#benchmark-results>
  - <https://github.com/meet1214/thread-pool/blob/main/include/ThreadPool.h>
  - <https://github.com/meet1214/thread-pool/blob/main/CMakeLists.txt>
  - <https://github.com/meet1214/thread-pool/blob/main/benchmark/benchmark.cpp>
  - <https://github.com/meet1214/thread-pool/blob/main/LICENSE>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/meet1214/thread-pool`) · [data/wave1/enrich/raw/github_com_meet1214_thread_pool.json](../../../data/wave1/enrich/raw/github_com_meet1214_thread_pool.json) (enrichment confidence 0.3)

</details>
