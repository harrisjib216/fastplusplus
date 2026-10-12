# BS::thread_pool

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Async tasks and thread pools](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `MIT` · 🟢 active

> Single-header C++17/20/23 thread pool that reuses worker threads to avoid std::thread's per-task creation overhead.

| | |
|---|---|
| **Beats** | std::thread |
| **Claimed result** | Qualitative only ("std::thread ... can have a significant performance overhead"); no specific ratio vs std::thread or std::async is given anywhere in the documentation |
| **Workload** | General motivational claim (README "Motivation" section): std::thread creates a new OS thread per call with significant overhead; no direct numeric std::thread-vs-pool micro-benchmark is published. The only quantified benchmark is single- vs multi-threaded Mandelbrot-set rendering using the pool itself (24.2x speedup on a 32-thread Intel i9-13900K, MSVC C++23 /O2), which measures multithreading efficiency, not std::thread/std::async overhead directly. |
| **Metric** | latency |
| **Adoption** | 3,054 stars; also published in SoftwareX (DOI 10.1016/j.softx.2024.101687) and as arXiv:2105.00613 |
| **Last commit** | 2026-01-04 |
| **Links** | [repository](https://github.com/bshoshany/thread-pool) · [benchmark](https://github.com/bshoshany/thread-pool#readme) |

## Verdict

No direct std::thread- or std::async-vs-pool number is published anywhere in the README; the only measured figure is a 24.2x multithreaded-vs-single-threaded speedup on the project's own Mandelbrot benchmark (32-thread Intel i9-13900K, MSVC, C++23, /O2), which quantifies parallel scaling of the pool itself, not the per-task OS-thread-creation overhead the Motivation section claims std::thread has.

## Use it when

- Need a zero-dependency, header-only pool that drops into an existing C++17 project without a new build dependency
- Many short-lived tasks (thousands+) where std::thread's per-call OS thread creation would dominate runtime
- Want built-in loop parallelization (submit_loop/detach_loop) instead of hand-rolling chunking over std::thread
- Need optional task priority, pause/resume, or deadlock detection without adopting a larger framework like oneTBB or Taskflow
- HPC/scientific-computing workloads with many uniform-sized tasks, where a single shared queue is enough

## Skip it when

- Imbalanced task graphs where some threads finish early and idle -- no work-stealing, so tail latency suffers vs. TooManyCooks/dispenso/libfork under uneven task sizes
- Need a hard measured number vs. std::thread/std::async before adopting -- none is published; only a self-referential single-vs-multithreaded Mandelbrot speedup is measured
- Calling wait()/wait_for()/wait_until() recursively from inside a task on the same pool without enabling wait_deadlock_checks -- deadlocks silently by default (documented in the README's own example)
- Need fiber/coroutine-style cooperative scheduling or tight oneTBB/OpenMP interop -- this is a plain OS-thread pool
- Apple Clang + C++20 module import path: README states Apple Clang is not officially supported there (plain header-only include is unaffected)

## How it is fast

The entire speed case is avoiding OS thread creation/teardown per task: threads are spawned once at pool construction and repeatedly pull work off one shared task queue guarded by a mutex/condition variable for the pool's lifetime, instead of std::thread's per-call CreateThread()/clone(). Optional features (priority, pause, deadlock checks) are selected via a bitmask template parameter, so pools that don't enable them pay no extra runtime cost. There is no work-stealing, lock-free queue, or SIMD involved -- it is one shared FIFO queue plus thread reuse, not algorithmic scheduling cleverness.

## Compared with alternatives

Pick BS::thread_pool over Boost.Fiber, dispenso, TooManyCooks, libfork, or Taskflow when you want one self-contained header with zero dependencies beyond the standard library and don't need work-stealing or fiber-level concurrency; pick a work-stealing pool instead (dispenso, TooManyCooks, libfork) when task sizes are uneven or you need a published std::thread/std::async number, which this project doesn't provide.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (C++ standard library only) |
| **Minimum toolchain** | C++17 (C++20/23 optional, enables module import and extra perf); verified with Clang 21, GCC 15, MSVC 19.50 |
| **Platforms** | any C++17-conformant compiler/OS; native extensions (thread/process priority, affinity, naming) additionally target Windows, Linux, macOS |
| **Thread safety** | not documented as a blanket guarantee -- task submission (submit_task/detach_task/etc.) and reset() are described as safe to call at any time, but no formal per-function thread-safety table is given |
| **Drop-in for the baseline** | partial -- replaces manual std::thread construction with a shared pool object and a submit/detach API; call sites must change, it is not a constructor-signature swap |

## Gotchas

- wait()/wait_for()/wait_until() called from inside a task running on the same pool deadlocks by default; opting into BS::tp::wait_deadlock_checks (BS::wdc_thread_pool) turns that into a thrown BS::wait_deadlock instead of a hang
- Optional features (priority, pause, wait-deadlock checks) are chosen via a bitmask template parameter at the pool's type, so combining features means a distinct pool type per combination, not a runtime toggle
- The pool cannot forcibly terminate a running task; cancellation requires the task itself to poll a flag
- Task priority is a signed 8-bit value (-128 to 127, higher runs first) only when BS::tp::priority is enabled -- ignored otherwise

## Caveats and trade-offs

Included as the single Tier-D entry for this run: the project is highly notable (3k+ stars, peer-reviewed companion paper) and its entire premise is beating std::thread's per-task overhead, but no page found in this session states an actual measured std::thread-vs-pool number -- only the unrelated Mandelbrot single-vs-multithreaded speedup is quantified.

Single self-contained header, C++17/20/23, only standard library dependency; no work-stealing (single shared queue) unlike TooManyCooks/citor/dispenso.

## Maintenance

Actively maintained (pushed 2026-01-04, 0 open issues, MIT-licensed, 3,055 stars, companion SoftwareX paper and arXiv:2105.00613); single header is trivially small enough to vendor into any project.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification D, tier now D.
- **Tier reason:** README only says std::thread 'can have a significant performance overhead' (Motivation section); its only quantified benchmark is pool-vs-single-threaded Mandelbrot (24.2x on i9-13900K, MSVC C++23 /O2), which has no std::thread/std::async baseline, so no numbers against the named baseline.
- **Verifier notes:** All metadata checks out (MIT, 3,054 stars, last commit 2026-01-04, not fork/archived; SoftwareX DOI and arXiv:2105.00613 are linked from the README). claimed_speedup has no numbers to verify; the qualitative quote and the Mandelbrot figures in workload are on the page. Tier D, but notable, so kept.
- **Pages the verifier opened:**
  - <https://github.com/bshoshany/thread-pool>
  - <https://github.com/bshoshany/thread-pool#readme>
  - <https://arxiv.org/abs/2105.00613>
- **Sources the enricher read:**
  - <https://github.com/bshoshany/thread-pool>
  - <https://github.com/bshoshany/thread-pool#readme>
  - <https://github.com/bshoshany/thread-pool/blob/master/README.md>
  - <https://github.com/bshoshany/thread-pool/issues>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/bshoshany/thread-pool`) · [data/wave1/enrich/raw/github_com_bshoshany_thread_pool.json](../../../data/wave1/enrich/raw/github_com_bshoshany_thread_pool.json) (enrichment confidence 0.45)

</details>
