# couring

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Filesystems and I/O](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `MIT` · 🔴 abandoned

> Single-file C++20 teaching demo comparing blocking reads, a thread pool, raw io_uring and io_uring coroutines for loading OBJ files.

| | |
|---|---|
| **Beats** | single-threaded blocking file reads |
| **Claimed result** | 512 OBJ files, real time: trivial 0.419s; thread pool 0.177s (2.4x, derived from page data); io_uring 0.368s (1.14x); coroutines 0.339s (1.24x); coroutines with thread pool 0.230s (1.8x) |
| **Workload** | Process 512 OBJ files with trivial, multithreaded, io_uring, coroutine and coroutine+thread-pool implementations. |
| **Metric** | throughput |
| **Compiler and flags** | CMake Release build (compiler not stated) |
| **Adoption** | 57 stars |
| **Last commit** | 2022-11-30 |
| **Links** | [repository](https://github.com/pabloariasal/couring) · [benchmark](https://github.com/pabloariasal/couring) |

## Verdict

One run of run_all on unspecified hardware and compiler (CMake Release, GCC gets -fcoroutines), loading 512 OBJ files. Wall times: blocking single-thread 0.419 s, thread pool 0.177 s (2.4x), io_uring 0.368 s (1.14x), coroutines 0.339 s (1.24x), coroutines plus thread pool 0.230 s (1.8x, all derived from page data). Multithreaded parsing, not io_uring, gives the biggest gain.

## Use it when

- Learning how to bridge io_uring completions to C++20 coroutine handles (awaitable + user_data = coroutine_handle pattern)
- As a starting skeleton for batching many small whole-file reads through one ring on Linux 5.1+
- Teaching that CPU-bound parsing, not I/O, often dominates 'load many files' workloads

## Skip it when

- As a production I/O library: no API, no error handling for short reads, no tests, abandoned since 2022-11-30
- When files are page-cache hot and parsing dominates: the README's own run has the plain thread pool (0.177 s) beat every io_uring variant (0.230-0.368 s)
- On non-Linux platforms or kernels older than 5.1; liburing is required
- When you need more than 512 files: openFiles stops at MAX_FILES = 512

## How it is fast

The io_uring variants queue one IORING_OP_READ per file into a 512-entry ring with liburing and collect completions with io_uring_submit_and_wait / io_uring_peek_cqe. The coroutine variants wrap each read in a C++20 awaitable whose completion entry carries the coroutine handle, so a completion resumes parsing. --coro-pool then hops onto a BS::thread_pool (v3.3.0) to parse on many threads. The thread-pool variant simply runs blocking read() plus parse across hardware threads, and since parsing dominates, that is where the gain comes from.

## Compared with alternatives

Pick it only to learn the coroutine-over-io_uring pattern. For real io_uring work use liburing directly (it is the dependency here). For a measured multi-file copy or read pipeline, copy-fast or uring-sync are closer to usable tools.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | liburing (system), BS::thread_pool v3.3.0 and tinyobjloader v2.0.0rc10 via CMake FetchContent |
| **Minimum toolchain** | C++20 with coroutines (GCC needs -fcoroutines, which CMakeLists sets), CMake 3.2+ |
| **Platforms** | Linux 5.1+ only (io_uring) |
| **Thread safety** | not documented; --coro-pool resumes coroutines on pool threads while the main thread busy-polls the CQ and reads handle.done() without synchronization |
| **Drop-in for the baseline** | no |

## Gotchas

- Coroutine results are thrown away: promise_type::return_value(Result result) does `result = std::move(result);`, which assigns the parameter to itself (it shadows the member). So --coroutines and --coro-pool return empty ObjReaders. Parsing still runs, so the timings reflect the work, but the output is never checked.
- Nothing validates the output: the only check is an assert (compiled out in Release) that each mesh has 1024 faces, and 'Processed N files' counts every result, good or not. Short or failed read() calls are ignored in the trivial and thread-pool paths.
- --coro-pool busy-spins the main thread on io_uring_peek_cqe, which inflates user time (0.732 s against 0.371 s for trivial).
- Timings come from bash `time` on one run of the whole process, including directory walk and opening all 512 fds. The README's data prep copies one OBJ file hundreds of times, so reads are almost certainly page-cache hot.

## Known shortcomings

- Correctness bug: Task::promise_type::return_value does result = std::move(result), assigning the parameter to itself (it shadows the member), so --coroutines and --coro-pool throw their parse results away; parsing still runs so timings roughly hold, but nothing is checked (the only assert is compiled out in Release and read() return values are ignored). --coro-pool also busy-spins the main thread and calls done() across threads without synchronization. Abandoned demo: 4 commits, last 2022-11-30. Not faster: a plain thread pool beats every io_uring variant.

## Caveats and trade-offs

Plain multithreading beats every io_uring variant; no hardware or compiler flags; speedup over trivial is modest. Reference value only.

C++20 coroutines over liburing, Linux 5.1+; demo-quality.

## Maintenance

Abandoned demo (4 commits, last 2022-11-30, no issues), MIT-licensed; worth reading for the coroutine/io_uring glue, not for vendoring.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** README shows a single run_all timing output for five of its own implementations against its own trivial single-threaded version; no hardware, compiler version or flags beyond CMake Release. First-party, partial methodology: C.
- **Verifier notes:** Numbers match README exactly. Educational demo with a blog series (pabloariasal.github.io, blocked); plain thread pool beats every io_uring variant, as the caveats already say. last_commit not checked (gh blocked).
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`
- **Shortcomings recorded by:** code reading by enricher
- **Pages the verifier opened:**
  - <https://github.com/pabloariasal/couring>
  - <https://raw.githubusercontent.com/pabloariasal/couring/HEAD/README.md>
  - <https://raw.githubusercontent.com/pabloariasal/couring/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/pabloariasal/couring/issues>
  - <https://github.com/pabloariasal/couring/commits>
  - <https://raw.githubusercontent.com/pabloariasal/couring/HEAD/README.md>
  - <https://raw.githubusercontent.com/pabloariasal/couring/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/pabloariasal/couring/HEAD/couring.cpp>
  - <https://raw.githubusercontent.com/pabloariasal/couring/HEAD/run_all>
  - <https://raw.githubusercontent.com/pabloariasal/couring/HEAD/cmake/fetch_thread_pool.cmake>
  - <https://raw.githubusercontent.com/pabloariasal/couring/HEAD/cmake/fetch_tinyobjloader.cmake>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/pabloariasal/couring`) · [data/wave11/enrich/raw/github_com_pabloariasal_couring.json](../../../data/wave11/enrich/raw/github_com_pabloariasal_couring.json) (enrichment confidence 0.75)

</details>
