# alignas(64) per-thread result slots against false sharing (Asynchronous Programming with C++ companion code)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Concurrent queues and locks](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟡 stale

> Pad each thread's result slot to its own 64-byte cache line with alignas(64) to stop false sharing between packed slots.

| | |
|---|---|
| **Beats** | adjacent unpadded 8-byte per-thread result slots (false sharing on one cache line) |
| **Claimed result** | Book, relayed by the seed lead and not present on the repo page: 4403 ms with adjacent slots against 160 ms aligned to 64 bytes, about 27x (ratio 27.5x derived from those figures); the book also reports perf stat cache misses of 96.63% against 27.21%. |
| **Workload** | Eight pinned std::thread workers each draw 100 million std::mt19937 values through uniform_int_distribution(1,5) and add them to a per-thread unsigned long slot; slots packed adjacently against slots in structs aligned with alignas(64); wall clock with std::chrono::high_resolution_clock. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen Threadripper Pro 5975WX, Ubuntu 24.04 (from the book via the seed lead; the repo itself does not state a CPU) |
| **Compiler and flags** | Chapter_13/CMakeLists.txt sets -O3 -DNDEBUG -std=c++20 -march=native; the repo README lists GCC 14.2 and Clang 18, while the lead says GCC (13) with libstdc++ produced the numbers. |
| **Adoption** | 95 stars |
| **Last commit** | 2026-04-22 |
| **Links** | [repository](https://github.com/PacktPublishing/Asynchronous-Programming-with-CPP) · [benchmark](https://github.com/PacktPublishing/Asynchronous-Programming-with-CPP/blob/main/Chapter_13/13x06-false_sharing.cpp) |

## Verdict

Per the book via the seed lead (numbers not in the repo): 8 threads pinned to cores 0-7 of an AMD Ryzen Threadripper Pro 5975WX on Ubuntu 24.04, built with GCC per the lead and the Chapter_13 flags (-O3 -DNDEBUG -std=c++20 -march=native), each summing 100 million std::mt19937 draws, took 4403 ms with packed 8-byte slots against 160 ms with alignas(64) slots, about 27.5x (derived from those figures), with perf stat cache misses of 96.63% against 27.21%. One run per variant, timed with std::chrono::high_resolution_clock around thread creation and join.

## Use it when

- Per-thread counters, partial sums, histograms or status words kept in a shared array and written inside a hot loop.
- Per-worker or per-core state structs (statistics, local queues) stored contiguously in an array or std::vector and updated concurrently.
- Indices or flags written by different threads that happen to sit next to each other, such as a ring buffer's head and tail (the same repo's SPSC queue sibling uses alignas(64) spacing for them).
- Profiles that show heavy cache-miss counts on data that is not logically shared between threads.

## Skip it when

- When each thread can accumulate in a local variable and write its slot once at the end: that removes the shared-line traffic without any padding or memory growth.
- Many small per-thread objects or large arrays of them: each padded slot grows from 8 to 64 bytes, which costs cache and memory capacity for little gain if the slots are rarely written.
- Read-mostly data or data written by only one thread: there is no invalidation traffic to remove.
- CPUs whose destructive interference size is 128 bytes (per the record, some Arm and Apple cores): a hard-coded 64 under-pads there; std::hardware_destructive_interference_size (C++17) or 128 is safer.

## How it is fast

Cache coherence tracks whole lines, so when eight cores write different words of one 64-byte line, every store invalidates the other cores' copies and the line bounces between them (false sharing). Cache-line padding gives each slot its own line, so each core keeps its line in its own cache and stores stay local. The book's perf stat cache-miss rates relayed in the record (96.63% packed against 27.21% padded) fit this mechanism.

## Compared with alternatives

Same idiom as 'The Art of Writing Efficient Programs: cache-line padding of per-thread partial sums' (book: about 2x, scaling with thread count); this example's packed baseline puts all eight slots on one line, so it shows the worst-case gap and comes with fixed flags and pinning. The queue siblings (atomic_queue, moodycamel, Boost.Lockfree) are for passing data between threads; this is for per-thread state that sits side by side.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none for the idiom; the benchmark uses pthread_setaffinity_np and cpu_set_t (Linux/glibc), and Chapter_13/CMakeLists.txt requires Google Benchmark (find_package(benchmark REQUIRED)) and links it into every example even though this file does not use it |
| **Minimum toolchain** | C++11 for alignas; C++17 aligned new for heap arrays of over-aligned structs (the benchmark calls new(std::align_val_t(64))); Chapter_13 builds with -O3 -DNDEBUG -std=c++20 -march=native |
| **Platforms** | idiom: any; benchmark: Linux only, with at least 8 logical CPUs for its fixed pinning to cores 0-7 |
| **Thread safety** | each slot is written by exactly one thread with plain non-atomic stores; readers must join the writers (or switch the slots to atomics) before reading |
| **Drop-in for the baseline** | partial — only the element type changes, but sizeof grows to 64 and arrays of it need over-aligned allocation (C++17 aligned new or std::vector) |

## Gotchas

- As checked in, main() runs only sum_random_aligned; the sum_random_unaligned call is commented out, so reproducing the comparison needs a one-line edit (preferably running each variant in its own process).
- The baseline is the worst case: eight 8-byte slots allocated with align_val_t(64) fill exactly one line, so all eight threads contend for it. Fewer threads per line or less frequent writes give a far smaller gap than the book's 27x.
- The size of the effect depends on code generation: data.result += dist(gen) is a plain store through a reference, and if a compiler keeps the accumulator in a register until the loop ends, the false sharing and the gap disappear; -march=native also ties the binary to the build host.
- Harness: set_affinity calls perror and exit(EXIT_FAILURE) if pinning fails (e.g. on a machine with fewer than 8 CPUs), the main thread re-pins itself to each core while spawning, thread creation sits inside the timed region, each variant runs once, and the per-thread sums are never printed or checked.

## Known shortcomings

- Book numbers only, no CPU. The unaligned call is commented out in main(); the Chapter13 CMake forces -O3 -march=native for any build type; thread spawn sits inside the timed region; last code change 2024-11-14.
- Enricher: worst-case packed baseline (8 slots in one line), effect vanishes if the accumulator stays in a register, core pinning exits on fewer than 8 CPUs, sums never checked; single commit 2024-10-18.

## Caveats and trade-offs

First-party book numbers; the benchmark code and CMake flags are public but the CPU model and the results exist only in the book, so this is tier C, not A. The checked-in main() runs only the aligned variant (the unaligned call is commented out), so reproducing the comparison needs a one-line edit. Chapter_13/CMakeLists.txt overwrites CMAKE_CXX_FLAGS with -O3 -DNDEBUG -std=c++20 -march=native and blanks the Debug/Release flag sets, so the flags apply whatever the build type. Single run; thread creation is inside the timed region, and the main thread also re-pins itself to each core while spawning workers. Slots are plain non-atomic stores, so how much false sharing occurs also depends on whether the compiler keeps the accumulator in a register. Threads are pinned to cores 0-7 of a many-core CPU, and the effect size depends on the cache topology. The comparison is an idiom difference (padded against packed slots), not a library against the standard library. Last code change in the repo is 2024-11-14; the 2026 commits only edit a conference banner in the README. [retier] Enricher: the packed baseline is the worst case (8 slots fill exactly one cache line), and the effect depends on codegen: an accumulator kept in a register removes it. Built with -march=native; pinning to cores 0-7 exits on machines with fewer than 8 CPUs; the sums are never checked. The Chapter_13 CMake requires Google Benchmark, which this file does not use.

Each slot grows from 8 to 64 bytes. The alignment is hard-coded to 64 rather than std::hardware_destructive_interference_size, so it is wrong for CPUs with 128-byte destructive interference (some Arm and Apple cores). Pinning uses pthread_setaffinity_np, so the code is Linux-only.

## Maintenance

MIT-licensed book companion code (95 stars, not archived); this file has a single commit (2024-10-18, 'Chapter-13 examples') and the 2026 commits only edit a README banner, so treat it as frozen teaching code: copy the alignas idiom and treat the harness as a demo.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** Chapter_13/13x06-false_sharing.cpp holds both variants (8-byte result_data slots packed in one 64-byte-aligned array against alignas(64) aligned_result_data) and Chapter_13/CMakeLists.txt fixes -O3 -DNDEBUG -std=c++20 -march=native, but no CPU model or results are in the repo; the 4403 ms against 160 ms figures are the book's first-party measurement relayed by the lead, so C.
- **Verifier notes:** Code, iteration count (100000000), 8 pinned threads and flags match the record; book numbers not checkable here (book not consulted per harness). Repo: MIT, 95 stars, 34 forks, not archived, not a fork, last commit 2026-04-22.
- **Fields the verifier corrected:** `caveats`, `maintenance_status`
- **Shortcomings recorded by:** verifier batch-86 (wave 1 book seed pass, 2026-10-24); enrichment (wave 1 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://github.com/PacktPublishing/Asynchronous-Programming-with-CPP>
  - <https://github.com/PacktPublishing/Asynchronous-Programming-with-CPP/commits/main>
  - <https://github.com/PacktPublishing/Asynchronous-Programming-with-CPP/tree/main/Chapter_13>
  - <https://github.com/PacktPublishing/Asynchronous-Programming-with-CPP/blob/main/Chapter_13/13x06-false_sharing.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/Asynchronous-Programming-with-CPP/main/Chapter_13/13x06-false_sharing.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/Asynchronous-Programming-with-CPP/main/Chapter_13/CMakeLists.txt>
  - <https://raw.githubusercontent.com/PacktPublishing/Asynchronous-Programming-with-CPP/main/CMakeLists.txt>
  - <https://raw.githubusercontent.com/PacktPublishing/Asynchronous-Programming-with-CPP/main/README.md>
  - <https://raw.githubusercontent.com/PacktPublishing/Asynchronous-Programming-with-CPP/main/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/PacktPublishing/Asynchronous-Programming-with-CPP>
  - <https://github.com/PacktPublishing/Asynchronous-Programming-with-CPP/tree/main/Chapter_13>
  - <https://github.com/PacktPublishing/Asynchronous-Programming-with-CPP/commits/main/Chapter_13/13x06-false_sharing.cpp>
  - <https://github.com/PacktPublishing/Asynchronous-Programming-with-CPP/issues?q=is%3Aissue>
  - <https://github.com/PacktPublishing/Asynchronous-Programming-with-CPP/issues/26>
  - <https://github.com/PacktPublishing/Asynchronous-Programming-with-CPP/issues/27>
  - <https://raw.githubusercontent.com/PacktPublishing/Asynchronous-Programming-with-CPP/main/Chapter_13/13x06-false_sharing.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/Asynchronous-Programming-with-CPP/main/Chapter_13/CMakeLists.txt>
  - <https://raw.githubusercontent.com/PacktPublishing/Asynchronous-Programming-with-CPP/main/CMakeLists.txt>
  - <https://raw.githubusercontent.com/PacktPublishing/Asynchronous-Programming-with-CPP/main/README.md>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `paper:book-asynchronous-programming-with-cpp-false-sharing-alignas-64`) · [data/wave1/enrich/raw/paper_book_asynchronous_programming_with_cpp_false_sharing_alignas_64.json](../../../data/wave1/enrich/raw/paper_book_asynchronous_programming_with_cpp_false_sharing_alignas_64.json) (enrichment confidence 0.6)

</details>
