# The Art of Writing Efficient Programs: spinlock-guarded thread-safe stack

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Concurrent queues and locks](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟡 stale

> Book example: std::stack behind a test-and-test-and-set spinlock, about 2.3x the single-thread push/pop rate of a std::mutex-guarded stack.

| | |
|---|---|
| **Beats** | std::stack guarded by std::mutex (mt_stack1) |
| **Claimed result** | Book: spinlock stack about 70 million operations per second against about 30 million for the mutex stack on one thread (about 2.3x, derived from the book figures; Figures 7.3 and 7.11); an unlocked std::stack reaches about 485 million on the same machine. |
| **Workload** | Chapter07/02_stack.C (Google Benchmark, Arg(1), 1 to numcpu threads, real time): BM_stack (mt_stack, a std::stack guarded by the test-and-test-and-set spinlock from spinlock.h, which calls nanosleep(1 ns) every 8 failed spins) against BM_stack1 (mt_stack1, a std::stack guarded by std::mutex); each iteration pushes then pops one int and counts as one item. The file also registers producer/consumer variants (BM_stack_prod_cons against BM_stack1_prod_cons) and reader-writer-lock variants. Chapter07/03_queue.C defines the same spinlock/mutex pair for a queue, but its BM_queue and BM_queue1 registrations are commented out; only spinlock-queue producer/consumer benchmarks are registered. |
| **Metric** | throughput |
| **Hardware** | x86 machine for the 70M and 30M figures; CPU model not stated |
| **Adoption** | 405 stars (Packt book companion repository) |
| **Last commit** | 2024-05-13 |
| **Links** | [repository](https://github.com/packtpublishing/the-art-of-writing-efficient-programs) · [benchmark](https://github.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/blob/master/Chapter07/02_stack.C) |

## Verdict

The book, relayed by the seed lead and not present in the repo, reports about 70 million push/pop pairs per second for the spinlock stack against about 30 million for the std::mutex stack on one thread of an unnamed x86 machine (about 2.3x, derived), with an unlocked std::stack at about 485 million; compiler, flags, standard library and CPU model are not given. The checked-in Google Benchmark harness (02_stack.C, Arg(1), real time) runs exactly this comparison, but its single-thread point measures only uncontended lock cost.

## Use it when

- Very short critical sections, such as a push or pop of a small value, where the lock is mostly uncontended and the lock/unlock cost itself dominates.
- Low thread counts on dedicated or pinned cores, where a lock holder is rarely preempted while others spin.
- Linux or other POSIX targets on x86-64 (the header calls POSIX nanosleep; the book's figures come from an x86 machine).
- As the coarse-locked baseline before trying a lock-free stack: the record notes the same chapter finds the lock-free stack does not beat this spinlock stack on x86.

## Skip it when

- Oversubscribed or loaded machines, or threads that can be preempted while holding the lock: waiters burn CPU, there is no fairness or priority inheritance, and one thread can starve.
- Latency-sensitive waiters: after 8 failed spins a waiter sleeps in nanosleep, and on Linux the requested 1 ns is stretched by the thread's timer slack (50 microseconds for init and inherited by default, per the PR_SET_TIMERSLACK man page seen via a search snippet; not applied to real-time scheduling policies), so a contended acquire can take tens of microseconds.
- Code that needs try_lock, timed locking, recursion or blocking waits: spinlock has only lock() and unlock(), so it cannot go into std::scoped_lock with several locks or std::try_lock, and std::condition_variable needs std::mutex (std::condition_variable_any would be required).
- Windows/MSVC: spinlock.h uses POSIX nanosleep, 02_stack.C uses unistd.h sysconf, and rw_spinlock's 0x1000000000000000L constant needs a 64-bit long, which Windows' 32-bit long is not, although the top-level README lists Visual Studio and Windows.
- Message passing between threads: the sibling queues (atomic_queue, moodycamel, Boost.Lockfree) are built for it, while this is a LIFO with one coarse lock.

## How it is fast

The lock is test-and-test-and-set: a waiter spins on a relaxed load and only tries exchange(1, acquire) when the flag reads free, and unlock() is a single release store. After every 8 failed attempts the waiter calls nanosleep for 1 ns as backoff. Uncontended, lock and unlock are inline atomic operations on a 4-byte flag, while std::mutex lock/unlock go through the platform threads library; the single-thread benchmark measures exactly this uncontended path, not behaviour under contention.

## Compared with alternatives

If you want to keep a std::stack or std::queue and only swap the lock, this 25-line spinlock and eventpp::SpinLock are the same idea; eventpp's is packaged in a maintained library with its own benchmark (about 1.4x over std::mutex), this one is easier to read and copy. For cross-thread queues, atomic_queue, moodycamel::ConcurrentQueue or Boost.Lockfree avoid the lock entirely and report several-fold lower latency than std::mutex; prefer this only for LIFO order with tiny, mostly uncontended critical sections.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none for spinlock.h beyond POSIX nanosleep; the benchmark needs Google Benchmark 1.5.x (it reads state.thread_index and state.threads as data members) |
| **Minimum toolchain** | C++17 (class template argument deduction in std::lock_guard g(l_), std::optional); compiler and flags for the book figures not documented |
| **Platforms** | POSIX (Linux); rw_spinlock assumes a 64-bit long (LP64) |
| **Thread safety** | push, pop and top lock; reset() does not, and the benchmark calls it from thread 0 before the timed loop |
| **Drop-in for the baseline** | partial — mt_stack has the same interface as the std::mutex version mt_stack1, and spinlock meets BasicLockable for std::lock_guard and std::unique_lock, but without try_lock it cannot replace std::mutex in std::scoped_lock of several locks, std::try_lock or std::condition_variable |

## Gotchas

- 02_stack.C does not compile against Google Benchmark 1.6.0 or later: it uses state.thread_index and state.threads as data members, which 1.6.0 turned into the member functions thread_index() and threads() (1.5.6 still has the fields).
- The spin loop has no CPU pause instruction, and the 4-byte flag has no alignas padding, so it can share a cache line with the std::stack's own fields or neighbouring globals; both matter under contention, not in the single-thread figure.
- One benchmark item is a push plus a pop (Arg(1)), counted the same on both sides. In multi-thread runs a pop that finds the stack empty still counts, and items per second are summed over threads with real time, so an unfair lock that lets one thread run while the others sleep can post high aggregate throughput; per-thread latency and fairness are not reported.
- ThreadRange(1, numcpu) takes numcpu from sysconf(_SC_NPROCESSORS_CONF), which counts configured CPUs (offline ones included), so the top thread count can exceed the CPUs actually online.

## Known shortcomings

- Book numbers only; no build files. The spinlock sleeps 1 ns every 8 spins; one item is a push plus a pop; producer/consumer variants count empty pops as items; 03_queue.C's spinlock and mutex queue registrations are commented out.
- Enricher: does not build on Google Benchmark 1.6.0+ (thread_index member); POSIX-only and 64-bit-long dependent despite the README listing Windows; aggregate items/s rewards unfairness; no pause instruction or flag padding.

## Caveats and trade-offs

The timing numbers are the book's own (quoted in the seed lead); the repository carries the benchmark program but no results file, so the numbers do not appear on the benchmark_url page and the ratios could not be checked against it. The single-thread comparison measures uncontended lock cost, not behaviour under contention; the book's own multi-thread charts are image-only. The same chapter says the lock-free stack does not beat the spinlock stack on x86. BM_stack0 (unlocked reference) is not registered in the file. Compiler, flags and CPU not stated; std::mutex cost varies by standard library. The repository has no Makefile, CMake file, build script or results file in Chapter05-07; the top-level README only lists 'GCC, Clang, Visual Studio' and Google Benchmark generically. Harness check: one item is a push plus a pop, so 'operations per second' means push/pop pairs (same on both sides, ratio unaffected). In the registered producer/consumer variants a pop on an empty stack still counts as an item, so those multi-thread throughput figures include failed pops. The spinlock sleeps via nanosleep under contention, so its multi-thread behaviour depends on the kernel timer slack. [retier] Enricher: 02_stack.C reads state.thread_index and state.threads as data members, so it fails to build on Google Benchmark 1.6.0 and later (needs 1.5.x). Aggregate real-time items/s rewards unfairness (a thread that keeps re-acquiring the lock raises throughput).

The spinlock backs off with a 1 ns nanosleep after 8 failed spins; on a loaded or oversubscribed machine, or with a preempted lock holder, spinning wastes cores and can invert priorities. Not fair, not recursive, no condition-variable integration.

## Maintenance

Book companion code under MIT (Copyright (c) 2020 Packt); Chapter07 is unchanged since its 2021-09-17 upload, builds only against Google Benchmark 1.5.x as written, and the one open issue (#4, about 02b_stack_cas.C) has no maintainer reply, so copy spinlock.h with the caveats above rather than depend on the repo.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** Chapter07/02_stack.C registers BM_stack (mt_stack with the spinlock from spinlock.h) and BM_stack1 (mt_stack1 with std::mutex), so the baseline comparison is in public code, but the 70M and 30M figures are the book author's own with no compiler, flags or CPU model in the repo: first-party, tier C.
- **Verifier notes:** Code matches the record (spinlock vs std::mutex stack, BM_stack0 commented out); corrected workload: the queue file's spinlock/mutex pairing is not registered. Numbers book-only.
- **Fields the verifier corrected:** `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-87 (wave 1 book seed pass, 2026-10-24); enrichment (wave 1 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter07/02_stack.C>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter07/spinlock.h>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter07/03_queue.C>
  - <https://github.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/tree/master/Chapter07>
  - <https://github.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs>
  - <https://github.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/commits/master>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/README.md>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/tree/master/Chapter07>
  - <https://github.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/commits/master/Chapter07>
  - <https://github.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/issues>
  - <https://github.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/issues?q=is%3Aissue+is%3Aclosed>
  - <https://github.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/issues/4>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/README.md>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/LICENSE>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter02/ReadMe.md>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter07/02_stack.C>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter07/spinlock.h>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter07/02b_stack_cas.C>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter07/03_queue.C>
  - <https://raw.githubusercontent.com/google/benchmark/v1.5.6/include/benchmark/benchmark.h>
  - <https://raw.githubusercontent.com/google/benchmark/v1.6.0/include/benchmark/benchmark.h>
  - <https://man7.org/linux/man-pages/man2/pr_set_timerslack.2const.html>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `paper:book-the-art-of-writing-efficient-programs-spinlock-guarded-stack`) · [data/wave1/enrich/raw/paper_book_the_art_of_writing_efficient_programs_spinlock_guarded_stack.json](../../../data/wave1/enrich/raw/paper_book_the_art_of_writing_efficient_programs_spinlock_guarded_stack.json) (enrichment confidence 0.6)

</details>
