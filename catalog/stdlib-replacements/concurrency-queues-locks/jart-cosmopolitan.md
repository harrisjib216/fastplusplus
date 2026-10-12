# Cosmopolitan Libc (pthread_mutex_t)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Concurrent queues and locks](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `ISC` · 🟢 active

> Portable libc whose pthread_mutex_t (Google nsync underneath) beat glibc 2.7x and musl 9.6x on a contended 30-thread lock test.

| | |
|---|---|
| **Beats** | glibc pthread_mutex_t (also musl pthread_mutex_t) |
| **Claimed result** | Comment block in test/libc/thread/footek_test.c, 'with posix', Linux 6.8 AMD Ryzen Threadripper PRO 7995WX: cosmo 40,965 us real vs glibc 111,560 us real (about 2.7x faster, derived from page data) vs musl 392,765 us real (about 9.6x faster, derived from page data); user time 47,168 us (cosmo) vs 153,985 us (glibc) vs 1,885,558 us (musl); sys time 25,398 us (cosmo) vs 2,988,121 us (glibc) vs 9,667,865 us (musl). Other rows in the same file: FreeBSD cosmo 126,803 us vs freebsd libc 219,073 us (about 1.7x); OpenBSD cosmo 138,619 us vs openbsd libc 385,431 us (about 2.8x); Windows 10 cosmo 156,382 us vs Cygwin 9,334,610 us (not native Windows locks); but Apple M2 Ultra cosmo 65,118 us vs Apple libc 45,443 us (cosmo about 1.4x slower). All ratios derived from page data. |
| **Workload** | footek_test with USE POSIX: 30 threads each doing 100000 iterations of pthread_mutex_lock, increment a shared counter, pthread_mutex_unlock (heavily contended); wall time of the whole run on Linux 6.8. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen Threadripper PRO 7995WX, Linux 6.8 (other rows: Apple M2 Ultra, FreeBSD, OpenBSD, NetBSD, Windows 10 test machines) |
| **Compiler and flags** | Not stated in the file (compiler, flags and glibc/musl versions unrecorded). |
| **Adoption** | 21.4k stars |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/jart/cosmopolitan) · [benchmark](https://github.com/jart/cosmopolitan/blob/master/test/libc/thread/footek_test.c) |

## Verdict

footek_test.c has 30 threads each run 100,000 lock/increment/unlock rounds on one PTHREAD_MUTEX_DEFAULT mutex, timing wall-clock including thread create and join. On Linux 6.8 with an AMD Threadripper PRO 7995WX, Cosmo took 40,965 us vs 111,560 us for glibc (about 2.7x) and 392,765 us for musl (about 9.6x). These are single first-party runs with compiler, flags and libc versions unrecorded, and on Apple M2 Ultra Cosmo was about 1.4x slower than Apple libc.

## Use it when

- You already ship, or are willing to ship, cosmocc-built binaries and have private (non-process-shared) mutexes that many threads hit at once on x86-64 Linux.
- Throughput-bound code where a hot lock is taken and released in short critical sections by tens of threads on a many-core machine (the test machine was a Threadripper PRO 7995WX on Linux 6.8).
- One binary has to run on Linux, FreeBSD, OpenBSD and Windows: on the same test Cosmo was about 1.7x faster than FreeBSD libc and 2.8x faster than OpenBSD libc, and much faster than Cygwin (native Windows SRWLOCK was not measured).
- You want POSIX mutex semantics plus cosmocc -mdbg lock-order (deadlock cycle) checking during development.

## Skip it when

- Apple Silicon: Cosmo skips nsync there and uses ulock, and the same test shows it about 1.4x slower than Apple's libc (65,118 us vs 45,443 us).
- You need fairness or bounded wait times: the lock lets newcomers jump queued waiters, and its starvation guard (MU_LONG_WAIT) only engages after a waiter has been woken 30 times without getting the lock. The benchmark measured aggregate throughput only.
- An existing glibc or musl program, a shared library, or anything that must interoperate with the host libc: Cosmopolitan's pthread_mutex_t is a 64-byte struct of its own and cannot be linked into a glibc process. To get the same algorithm there, use google/nsync directly.
- Process-shared (PTHREAD_PROCESS_SHARED) or ERRORCHECK mutexes: shared ones never take the nsync path, and errorcheck ones run deadlock tracking on every lock, so the measured speedup does not apply to them.
- macOS older than Darwin 23.1.0, Windows before 8, and other platforms outside the README's support table (open issue #1446: nsync futex assertion crash in mutex_test on Darwin 17.7).

## How it is fast

nsync keeps the whole lock in one 32-bit word with a compare-and-swap fast path, spins with exponential backoff before sleeping (pthread_delay_np spins 1 to 64 iterations, then sched_yield), and parks waiters on a spinlock-protected list, each waiter on its own semaphore. It is a barging lock: an arriving thread may take a free lock ahead of queued waiters, and a 'designated waker' bit means an unlock wakes at most one sleeper until that thread runs, which avoids wake storms. On the 30-thread test this keeps threads out of the kernel: 25 ms of system time against 2,988 ms for glibc. After the first call the mutex caches a direct function pointer (mutex-&gt;_lock), so later locks skip the type dispatch.

## Compared with alternatives

The catalogued siblings (atomic_queue, moodycamel, Boost.Lockfree, xenium, oneTBB queues) replace a mutex-plus-queue with a lock-free structure, and eventpp::SpinLock is a pure spinlock. Pick Cosmopolitan's mutex when you need a general blocking POSIX mutex around arbitrary shared state, and only if the program is built with cosmocc anyway; for a single shared queue the lock-free siblings usually remove the lock altogether.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | Cosmopolitan toolchain (cosmocc, a repackaged GCC/Clang) and Cosmopolitan libc; nsync is vendored in third_party/nsync (Apache-2.0) |
| **Minimum toolchain** | cosmocc release from cosmo.zip (bundled GCC/Clang); the repo builds with GNU Make |
| **Platforms** | x86-64 (AMD K8+ / Intel Core+) and aarch64; Linux 2.6.18+, Windows 8+, macOS Darwin 23.1.0+, FreeBSD 13, OpenBSD 7.3, NetBSD 9.2 |
| **Thread safety** | It is a mutex with POSIX pthread_mutex semantics. It blocks thread cancellation while waiting. Recursive mutexes refuse unlocks from another thread or from a forked child (EPERM). Errorcheck mode works only for mutexes in static memory (.data/.bss). |
| **Drop-in for the baseline** | partial: source-compatible with the pthread_mutex_\* API, but only inside programs built with cosmocc against Cosmopolitan libc; not ABI-compatible with glibc or musl |

## Gotchas

- The fast path applies only to private, non-recursive, non-errorcheck mutexes in non-debug builds on non-Apple-Silicon hosts. Recursive private mutexes also use nsync but wrap it in owner and depth bookkeeping. cosmocc -mdbg runs deadlock tracking on every lock.
- Benchmark harness limits: footek_test starts its timer before mutex init and thread creation and stops it after pthread_join, so thread start-up is inside the timed region. Each row is one run. The glibc and musl rows use PTHREAD_MUTEX_DEFAULT only; glibc's spinning PTHREAD_MUTEX_ADAPTIVE_NP type and other spin-then-park locks were not tried. The FUTEX, SPIN and many fleet rows are Cosmo-only, with no host-libc comparison.
- The 2.7x comes from comparing a spinning lock that lets newcomers jump the queue against a baseline that sleeps in futex (glibc 2,988 ms of system time vs 25 ms). Critical sections that are longer, or that block, will not see the same gap.
- The lock code still gets correctness fixes: commits on 2026-05-20 fixed an EINTR bug in pthread_cond_timedwait, a past-timestamp lock bug on Windows and XNU, and a NetBSD lock signal bug.

## Known shortcomings

- Scoped to pthread_mutex_t: footek_test.c comment block (Threadripper PRO 7995WX) gives 2.7x over glibc and 9.6x over musl from one run each with no compiler, flags or libc versions; a single 30-thread contended test with thread creation inside the timed region and no fairness or latency measure; slower on the M2 Ultra; the Windows baseline is Cygwin. The fast path is third_party/nsync (Google nsync, Apache-2.0), which is not catalogued. Filed under stdlib-replacements/concurrency-queues-locks by override although mined into wave 11.
- Enricher: the pthread_mutex_t win is a barging nsync lock (newcomers jump queued waiters, starvation guard only after 30 wakeups) with spin backoff, measured against glibc's non-spinning PTHREAD_MUTEX_DEFAULT only (PTHREAD_MUTEX_ADAPTIVE_NP not tried); single runs with thread create/join inside the timer, throughput only. Process-shared, errorcheck and Apple Silicon mutexes skip the nsync path; lock fixes as recent as 2026-05-20; open #1446 (nsync futex assert on Darwin 17.7); not ABI-compatible with glibc (64-byte struct).

## Caveats and trade-offs

Results are first-party comments pasted into a test file, one run each, no compiler, flags or libc versions recorded, so tier C although the test source is public and the CPU is named. Only a single heavily contended 30-thread microbenchmark (100,000 lock/increment/unlock per thread); the timed region also includes creating and joining the 30 threads; it measures aggregate throughput only, not fairness, handoff latency or uncontended lock cost, and says nothing about other libc facilities. The win comes from Cosmo's non-Apple fast path, which calls nsync_mu_lock from third_party/nsync (Google's nsync, Apache-2.0, as modified in Cosmopolitan); on Apple Silicon Cosmo uses ulock instead and the same file shows it slower than Apple's libc. The Windows comparison is against Cygwin, not native SRWLOCK or MSVC locks. The maintainer's blog post on mutexes (justine.lol, not reachable from this session) is reported by search snippets with slightly different figures (36,905 us vs 101,353 us for glibc, and 2.75x over Windows SRWLOCK); those were not opened and are not used. Using the mutex means building with the Cosmopolitan toolchain (cosmocc) and libc; license is ISC for the core with third-party components such as nsync under Apache-2.0. The project's other speed claims (startup 400 us faster with binfmt_misc registration, README) have no baseline numbers.

Cosmopolitan is a whole libc plus the Actually Portable Executable format, not a drop-in mutex library: using its mutex means building with cosmocc and linking its libc; some platform behavior differs from the host libc; the mutex code is tied to the libc's futex and thread internals.

## Maintenance

Actively maintained (last commit 2026-10-06; lock fixes in May 2026). ISC-licensed core with Apache-2.0 nsync. The mutex cannot be copied out on its own because it is tied to the libc's futex, TLS and thread internals, so outside Cosmopolitan use upstream google/nsync.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** test/libc/thread/footek_test.c is public and its comment block names the CPU (AMD Ryzen Threadripper PRO 7995WX, Linux 6.8) with glibc, musl and Cosmo rows, but no compiler, flags or libc versions are recorded and each row is one first-party run, so C.
- **Verifier notes:** Every number in the record matches the footek_test.c comment block; added sys times, the nsync origin of the fast path (libc/intrin/pthread_mutex_lock.c) and that thread creation is inside the timed region. Not a duplicate of any listed project; google/nsync itself is not listed and could be a lead. Metadata checked: ISC, 21.4k stars, not archived, not a fork, last commit 2026-10-06.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** multi-run comparison with versions and flags; enricher code reading
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/jart/cosmopolitan/HEAD/test/libc/thread/footek_test.c>
  - <https://raw.githubusercontent.com/jart/cosmopolitan/HEAD/libc/intrin/pthread_mutex_lock.c>
  - <https://raw.githubusercontent.com/jart/cosmopolitan/HEAD/libc/intrin/pthread_mutex_unlock.c>
  - <https://raw.githubusercontent.com/jart/cosmopolitan/HEAD/third_party/nsync/mu.c>
  - <https://raw.githubusercontent.com/jart/cosmopolitan/HEAD/LICENSE>
  - <https://github.com/jart/cosmopolitan>
  - <https://github.com/jart/cosmopolitan/commits/master.atom>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/jart/cosmopolitan/HEAD/test/libc/thread/footek_test.c>
  - <https://raw.githubusercontent.com/jart/cosmopolitan/HEAD/libc/intrin/pthread_mutex_lock.c>
  - <https://raw.githubusercontent.com/jart/cosmopolitan/HEAD/libc/intrin/pthread_mutex_unlock.c>
  - <https://raw.githubusercontent.com/jart/cosmopolitan/HEAD/libc/intrin/pthread_delay_np.c>
  - <https://raw.githubusercontent.com/jart/cosmopolitan/HEAD/libc/thread/thread.h>
  - <https://raw.githubusercontent.com/jart/cosmopolitan/HEAD/third_party/nsync/mu.c>
  - <https://raw.githubusercontent.com/jart/cosmopolitan/HEAD/third_party/nsync/mu.h>
  - <https://raw.githubusercontent.com/jart/cosmopolitan/HEAD/third_party/nsync/common.internal.h>
  - <https://raw.githubusercontent.com/jart/cosmopolitan/HEAD/third_party/nsync/README.cosmo>
  - <https://raw.githubusercontent.com/jart/cosmopolitan/HEAD/README.md>
  - <https://raw.githubusercontent.com/jart/cosmopolitan/HEAD/LICENSE>
  - <https://github.com/jart/cosmopolitan>
  - <https://github.com/jart/cosmopolitan/commits/master>
  - <https://github.com/jart/cosmopolitan/issues?q=is%3Aissue+mutex>
  - <https://github.com/jart/cosmopolitan/issues/1446>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/jart/cosmopolitan`) · [data/wave11/enrich/raw/github_com_jart_cosmopolitan.json](../../../data/wave11/enrich/raw/github_com_jart_cosmopolitan.json) (enrichment confidence 0.8)

</details>
