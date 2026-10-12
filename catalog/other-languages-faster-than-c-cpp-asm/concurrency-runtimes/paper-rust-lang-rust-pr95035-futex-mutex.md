# Rust std futex-based Mutex (rust-lang/rust PR 95035) vs the pthread_mutex-based std Mutex

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Concurrency runtimes](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0 OR MIT` · 🟢 active

> Rust's std::sync::Mutex on Linux since 1.62: an inline three-state futex word with a short spin, replacing a boxed glibc pthread_mutex_t.

| | |
|---|---|
| **Beats** | glibc (and musl) pthread_mutex_t, as wrapped by the previous Rust std::sync::Mutex on Linux |
| **Claimed result** | PR comment by m-ou-se on a 64C/128T AMD Threadripper (average per round): extreme contention new 27.65 ms vs old std (gnu pthread) 58.51 ms and old std (musl) 89.15 ms; heavy contention 1.82 ms vs 8.11 ms (gnu) and 7.08 ms (musl); light contention 0.784 ms vs 2.80 ms (gnu) and 2.90 ms (musl); no contention 1.19 ms vs 2.98 ms (gnu) and 2.79 ms (musl). About 2.1x, 4.4x, 3.6x and 2.5x faster than the glibc pthread-based version (derived from page data). |
| **Workload** | matklad/lock-bench: 32 threads, 10,000 lock/unlock operations per thread over 2 (extreme), 64 (heavy), 1,000 (light) or 1,000,000 (no contention) locks, 100 rounds, average time per round. |
| **Metric** | throughput |
| **Hardware** | 64-core / 128-thread AMD Threadripper (exact model not stated) |
| **Compiler and flags** | Not stated in the PR comment; lock-bench is run with cargo run --release (rustc of March 2022, flags otherwise unstated); the glibc and musl pthread builds are distribution builds |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Why it wins** | PR design: the lock is a single 32-bit futex word (0 unlocked, 1 locked, 2 contended) with a short spin before parking in the kernel and no heap-allocated pthread_mutex_t, so uncontended lock and unlock are one atomic operation each. |
| **Adoption** | 119.7k stars, 18.3k forks (rust-lang/rust); part of the Rust standard library: PR 95035 merged by bors on 2022-04-05, milestone 1.62.0, listed in the 1.62.0 release notes |
| **Last commit** | 2026-10-11 |
| **Links** | [repository](https://github.com/rust-lang/rust) · [benchmark](https://github.com/rust-lang/rust/pull/95035) |

## Verdict

In one run posted on the PR by its author on a 64-core/128-thread AMD Threadripper (model, rustc version, glibc and musl versions not stated), matklad/lock-bench with 32 threads and 10,000 lock operations per thread averaged 27.6 ms versus 58.5 ms (glibc) and 89.1 ms (musl) per round on 2 locks, 1.82 versus 8.11 ms on 64 locks, 0.784 versus 2.80 ms on 1,000 locks and 1.19 versus 2.98 ms on 1,000,000 locks, against the earlier Rust std Mutex built on boxed pthread_mutex_t. The baseline is glibc reached through Rust's boxed wrapper, not a C program, and the measured gap includes layout and barrier effects of the harness as well as the spin-then-park algorithm.

## Use it when

- Any Rust code on Linux that needs a plain mutex: it is the default std::sync::Mutex since Rust 1.62, so there is nothing to add; just build with a current toolchain.
- Short critical sections under moderate or heavy contention with fewer runnable threads than cores, where the 100-iteration spin catches most hand-offs (the PR's 32 threads on a 128-thread Threadripper: heavy contention 1.82 ms versus 8.11 ms for the glibc-based version).
- Many small locks (one per object or bucket): no per-lock heap allocation and 4 bytes of state (1 byte on Windows) instead of a separate pthread_mutex_t allocation.
- Statics and const contexts: the constructor is const, so no lazy initialisation or OnceLock wrapper is needed.

## Skip it when

- Real-time or priority-sensitive code: it has no priority inheritance or robust-mutex mode; the tracking issue keeps pthread on non-futex Unix 'to maintain priority inheritance'. Note that the old Linux std Mutex never set PTHREAD_PRIO_INHERIT either, so use a pthread wrapper with the PI attribute if you need it.
- Oversubscribed systems (more runnable threads than cores) or long critical sections: the fixed spin burns CPU while the owner may be descheduled; the only numbers are from 32 threads on 128 hardware threads, and lock-bench's own README on a 4-core i7-7820HQ found spinning locks much worse than a good mutex.
- Light or no contention where every nanosecond counts: in the same PR run parking_lot::Mutex (0.695 ms, 0.940 ms) and spin::Mutex (0.605 ms, 0.765 ms) beat it (0.784 ms, 1.19 ms).
- Workloads needing fairness: lock hand-off is unfair (an unlock sets 0 and wakes one waiter, and a spinning thread can barge in first), so a waiter can starve; the tracking issue notes pthread and SRW locks are not fair either.
- C or C++ code: it is not a pthread_mutex_t replacement and has no C ABI; it only speeds up Rust programs.

## How it is fast

It is the classic three-state futex lock (0 unlocked, 1 locked, 2 locked with waiters): lock and unlock are one inlined compare_exchange and one swap, and the kernel is entered only when the state is 2. Unlike glibc 2.35's normal mutex, which is the same three-state algorithm without spinning (__lll_lock_wait goes straight to futex_wait) and also writes __owner and __nusers on every lock, the Rust lock first spins up to 100 iterations of hint::spin_loop with plain loads, stops early when the state becomes 0 or 2, and spins again after each wake-up. It also removes the Box indirection, so the lock word sits next to the protected data instead of in a separate heap allocation.

## Compared with alternatives

No mutex is catalogued among this category's siblings; Cynosure RingBuf and Myelon remove locking for single-producer queues and IPC instead, and Tokio or Embassy schedule tasks rather than guard data. Use this whenever a Rust program needs a blocking mutex; for C or C++ code the catalogued lock entries are Cosmopolitan Libc's pthread_mutex_t and AlexeyAB's contention_free_shared_mutex in the concurrency-queues-locks category.

## Integration

| | |
|---|---|
| **Form** | module (part of the Rust standard library, std::sync::Mutex) |
| **Dependencies** | none (Linux futex syscall via libc::syscall; WaitOnAddress on Windows; _umtx_op on FreeBSD) |
| **Minimum toolchain** | Rust 1.62 for the Linux futex version (PR milestone 1.62.0); const construction on all platforms came with the later PR 97791 |
| **Platforms** | Linux, Android, FreeBSD, OpenBSD, DragonFly, Windows (non-win7 targets), wasm with atomics, Hermit, WASI p3; macOS and other Unix keep pthread, Fuchsia has its own |
| **Thread safety** | Mutex&lt;T&gt; is Sync for T: Send; poisoning on panic is kept at the std::sync layer; re-locking from the owning thread deadlocks |
| **Drop-in for the baseline** | partial: for Rust code it replaced the pthread-based std::sync::Mutex with the same API, transparently; it cannot replace pthread_mutex_t in C or C++ programs |

## Gotchas

- Harness flaw (lock-bench src/main.rs): each lock is wrapped in crossbeam CachePadded, but the 1.60 std Mutex holds only a Box pointer there; the pthread_mutex_t lives in a separate unpadded heap allocation made in a tight loop, so neighbouring old-std locks can share cache lines (false sharing) while the new futex word, parking_lot and spin are padded. Part of the extreme- and heavy-contention gap is therefore layout, not lock algorithm (likely, not measured).
- Harness flaw: the timed region runs from start_barrier to end_barrier, and std::sync::Barrier is itself a std Mutex plus Condvar (1.60 barrier.rs), so every round includes 32 threads waking from a Condvar and re-acquiring the Barrier's mutex, done with the old pthread pair in the old build and the new futex pair in the new one. At about 1 to 3 ms per round this fixed cost is not separated from the 'no contention' result, and the PR also replaced Condvar, so that row mixes the two changes.
- In the 1,000,000-lock 'no contention' case the old version needs two dependent cache misses per operation (padded slot, then boxed pthread_mutex_t) against one for the inline futex word, so its 2.5x gap mostly reflects memory layout.
- After any contention the woken thread always sets the state to 2 (by design, so other waiters are not lost), so the next unlock makes a FUTEX_WAKE syscall even when nobody is waiting any more; the spin count is a fixed 100 iterations of hint::spin_loop on every CPU, with no adaptive tuning.

## Known shortcomings

- Baseline is the glibc pthread_mutex boxed behind the old Rust std, not a C program; the win comes from a 100-spin loop plus the inline futex word, not the language; parking_lot and spin beat the new lock under light and no contention; one run with CPU model and rustc unstated; merged 2022-04-05 (milestone 1.62.0).
- Two harness flaws in matklad/lock-bench src/main.rs: CachePadded pads only the Box pointer of the 1.60 std Mutex, so the boxed pthread_mutex_t objects sit unpadded on the heap and neighbouring old-std locks can falsely share cache lines while the new futex word, parking_lot and spin are padded (likely, not measured); and the timed region spans std::sync::Barrier, itself a std Mutex plus Condvar, so each round includes a 32-thread wake and herd on the lock under test and the no-contention row mixes in the Condvar change from the same PR. glibc 2.35's normal mutex is the same three-state futex lock with no spin plus __owner and __nusers writes per lock, so the real algorithm difference is the 100-iteration spin plus inline storage; the same lock now also backs Windows (WaitOnAddress) and the BSDs.

## Caveats and trade-offs

The baseline is the earlier Rust std::sync::Mutex (library/std/src/sys/unix/mutex.rs in 1.60.0): a Box&lt;Mutex&gt; around a pthread_mutex_t initialised as PTHREAD_MUTEX_NORMAL and called through non-inlined libc calls, so part of the gap is the heap indirection rather than glibc's lock algorithm; a C program would normally embed pthread_mutex_t inline, and no standalone C program was benchmarked. glibc's normal mutex is itself a three-state futex lock without spinning, so the new lock's main algorithmic difference is a 100-iteration spin before futex_wait (background knowledge for glibc, not checked in this pass). The run used 32 threads on a 128-thread machine (no oversubscription), which favours spinning: in the same table even spin::Mutex (42.4 ms extreme, 2.13 ms heavy) and AmdSpinlock beat the old glibc-based std Mutex, and parking_lot::Mutex and spin::Mutex were faster than the new std Mutex under light and no contention (parking_lot 0.695 ms and 0.940 ms, spin 0.605 ms and 0.765 ms), while lock-bench's own README on a 4-core i7-7820HQ found spinlocks much worse than a good mutex. Under extreme contention parking_lot (313 ms) was about 11x slower than the new lock. In the 1,000,000-lock no-contention case the old version holds one separately heap-allocated pthread_mutex_t per lock, so its 2.5x gap is mostly memory footprint. Single author-posted run on one machine; the comment itself says 'Realistic benchmarks are very hard'; glibc and musl versions are not stated. rust-timer found no relevant compiler-performance change. lock-bench carries no licence file. Only the Mutex has numbers on the PR page; this PR also replaced Condvar, and the matching RwLock PR (95801) gives none. [retier] Enricher: in matklad/lock-bench src/main.rs CachePadded pads only the Box pointer of the 1.60 std Mutex, so the boxed pthread_mutex_t objects sit unpadded on the heap and neighbouring old-std locks can falsely share cache lines while the new futex word, parking_lot and spin are padded (likely, not measured); and the timed region spans std::sync::Barrier, itself a std Mutex plus Condvar, so each round includes a 32-thread wake and herd on the lock under test and the no-contention row mixes in the Condvar change from the same PR. glibc 2.35's normal mutex is the same three-state futex lock with no spin plus __owner and __nusers writes per lock, so the real difference is the 100-iteration spin plus inline storage.

A futex-based lock is Linux-specific (the PR targets Linux; other platforms keep their own implementations); one word of state with no heap allocation and a const constructor, but no priority inheritance or robust-mutex support that pthread mutex attributes offer.

## Maintenance

Active and shipped: part of rust-lang/rust (Apache-2.0 OR MIT), unchanged in algorithm from 1.62.0 to current main apart from a 1-byte state on Windows and a move to library/std/src/sys/sync/mutex/futex.rs; usable by every Rust program, with the evidence a single first-party run on one machine.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The numbers are an author-posted lock-bench run in the PR conversation (m-ou-se, a Rust libs maintainer, so first-party) on an unnamed '64C/128T AMD Threadripper' with no rustc version or flags; lock-bench (matklad/lock-bench) is public and runs with cargo run --release, but the CPU model and compiler are not given, so it is not A, and nothing independent or peer-reviewed backs it.
- **Verifier notes:** All new-vs-old averages in claimed_speedup match the PR comment tables (27.645506 vs 58.506588/89.146548 ms; 1.822707 vs 8.10534/7.08335 ms; 784.189 us vs 2.802436/2.900143 ms; 1.189231 vs 2.97886/2.794938 ms) and the derived ratios 2.1x, 4.4x, 3.6x, 2.5x check out. Record shortcomings: baseline is glibc pthread_mutex boxed behind Rust std, not a C program; win is lock design (spin, inline futex word), not language; parking_lot and spin beat the new lock under light and no contention; one run, CPU model and compiler unstated.
- **Fields the verifier corrected:** `last_commit`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-84 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/rust-lang/rust/pull/95035>
  - <https://github.com/matklad/lock-bench>
  - <https://github.com/rust-lang/rust>
  - <https://github.com/rust-lang/rust/commits/main>
  - <https://raw.githubusercontent.com/rust-lang/rust/1.62.0/library/std/src/sys/unix/locks/futex.rs>
  - <https://raw.githubusercontent.com/rust-lang/rust/1.60.0/library/std/src/sys/unix/mutex.rs>
  - <https://raw.githubusercontent.com/rust-lang/rust/1.60.0/library/std/src/sys_common/mutex.rs>
- **Sources the enricher read:**
  - <https://github.com/rust-lang/rust/pull/95035>
  - <https://github.com/rust-lang/rust/issues/93740>
  - <https://github.com/rust-lang/rust/pull/99505>
  - <https://github.com/rust-lang/rust/tree/main/library/std/src/sys/sync>
  - <https://raw.githubusercontent.com/rust-lang/rust/1.62.0/library/std/src/sys/unix/locks/futex.rs>
  - <https://raw.githubusercontent.com/rust-lang/rust/1.60.0/library/std/src/sys/unix/mutex.rs>
  - <https://raw.githubusercontent.com/rust-lang/rust/1.60.0/library/std/src/sys_common/mutex.rs>
  - <https://raw.githubusercontent.com/rust-lang/rust/1.60.0/library/std/src/sync/barrier.rs>
  - <https://raw.githubusercontent.com/rust-lang/rust/HEAD/library/std/src/sys/sync/mutex/futex.rs>
  - <https://raw.githubusercontent.com/rust-lang/rust/HEAD/library/std/src/sys/sync/mutex/mod.rs>
  - <https://raw.githubusercontent.com/rust-lang/rust/HEAD/library/std/src/sys/sync/futex/mod.rs>
  - <https://raw.githubusercontent.com/rust-lang/rust/HEAD/library/std/src/sys/sync/futex/unix.rs>
  - <https://raw.githubusercontent.com/rust-lang/rust/HEAD/library/std/src/sys/sync/futex/windows.rs>
  - <https://raw.githubusercontent.com/matklad/lock-bench/HEAD/README.md>
  - <https://raw.githubusercontent.com/matklad/lock-bench/HEAD/src/main.rs>
  - <https://raw.githubusercontent.com/matklad/lock-bench/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/bminor/glibc/glibc-2.35/nptl/lowlevellock.c>
  - <https://raw.githubusercontent.com/bminor/glibc/glibc-2.35/sysdeps/nptl/lowlevellock.h>
  - <https://raw.githubusercontent.com/bminor/glibc/glibc-2.35/nptl/pthread_mutex_lock.c>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `paper:rust-lang-rust-pr95035-futex-mutex`) · [data/wave14/enrich/raw/paper_rust_lang_rust_pr95035_futex_mutex.json](../../../data/wave14/enrich/raw/paper_rust_lang_rust_pr95035_futex_mutex.json) (enrichment confidence 0.6)

</details>
