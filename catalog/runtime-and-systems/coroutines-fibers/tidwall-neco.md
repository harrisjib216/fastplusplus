# Neco

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Coroutines and fibers](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C` · `MIT` · 🟢 active

> Single-file C coroutine runtime with Go-like channels, deterministic scheduler and epoll/kqueue I/O; about 11 ns switches, no baseline measured.

| | |
|---|---|
| **Beats** | none named (README claims fast switching; ucontext fallback only) |
| **Claimed result** | About 11 ns per context switch (via llco assembly). |
| **Workload** | Stackful symmetric coroutines with built-in scheduler and I/O; context switch time. |
| **Metric** | latency |
| **Hardware** | AMD Ryzen 9 5950X |
| **Adoption** | 1.4k stars |
| **Last commit** | 2026-05-30 |
| **Links** | [repository](https://github.com/tidwall/neco) · [benchmark](https://github.com/tidwall/neco/blob/main/README.md) |

## Verdict

The README states that an llco-based context switch takes about 11 ns on the author's AMD Ryzen 9 5950X, with no compiler, flags, benchmark code or comparison library. The linked Bluebox repo (not part of the verified claim) shows memtier_benchmark default runs on the same CPU at 493,346 ops/s for the Neco-based Redis clone versus 207,735 ops/s for redis-server (about 2.4x, derived from page data), an application benchmark against a far larger server, not a coroutine comparison.

## Use it when

- Network servers or clients in plain C on Linux/macOS/FreeBSD where you want sequential code per connection instead of callback state machines (the author's Bluebox Redis clone is the reference design).
- Programs with thousands to tens of thousands of mostly idle coroutines on one core.
- Simulations or tests that need deterministic, reproducible interleaving (fair, deterministic scheduler).
- Projects that want a single .c/.h drop-in under MIT with no external dependencies.

## Skip it when

- CPU-bound work that should scale across cores: one scheduler per thread, cross-thread communication only via pipes/eventfd/atomics; multithreaded scheduling is an explicit non-goal.
- Windows or WebAssembly network code: neco_wait and fd-based I/O are not available there (no epoll/kqueue), Windows is amd64 only, and guards, CSPRNG and unwinding are missing.
- Code that must call blocking libraries using pthread_mutex_t/pthread_cond_t from inside coroutines (README: they do not work well), or that must coexist with another event loop such as libuv (issue #5 open).
- Bursty spawning of many coroutines: neco_start switches into the new coroutine immediately, and issues #10 (slow creation of thousands of coroutines) and #12 (about 105,050 switches for 100 spawns among 1,000 coroutines) report the cost.
- Old glibc (&lt; 2.30) targets: issue #6 open.

## How it is fast

Context switches go through the bundled llco layer, a hand-written assembly register swap (callee-saved registers only, no signal-mask syscall) adapted from minicoro and Lua Coco. Scheduling is done by the bundled sco, a fair FIFO scheduler, entirely in user space. Stacks are 8 MiB mmap regions grouped with 1 MiB gaps, recycled via a stack free list and with early page release, and coroutine and channel objects are pooled; blocking writes on Linux and getaddrinfo are pushed to worker threads so the scheduler thread keeps running.

## Compared with alternatives

Pick Neco over libdill or libmill when you want a maintained, single-file C runtime with channels, deadlines and networking wrappers plus deterministic scheduling; pick llco or minicoro when you only need the switch primitive, and libdill when you want published switch numbers against a baseline (Go goroutines).

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none beyond libc and pthreads (dlsym used for getaddrinfo threads); epoll or kqueue for I/O |
| **Minimum toolchain** | C11 with &lt;stdatomic.h&gt; (GCC or Clang); glibc 2.30+ reported for Linux (issue #6) |
| **Platforms** | Linux, macOS, FreeBSD full; Windows amd64 and WebAssembly (Emscripten -sASYNCIFY) core coroutines only |
| **Thread safety** | One runtime and scheduler per thread; neco objects are not shared across threads; pthread mutex/cond are unsuitable inside coroutines |
| **Drop-in for the baseline** | no |

## Gotchas

- Coroutine argv pointers are valid only until the coroutine's first neco_\* call; copy arguments first (README example 4).
- Default stack is 8 MiB of virtual memory per coroutine plus 1 MiB gaps (1 MiB heap stacks on Windows/WebAssembly); guard pages need -DNECO_USEGUARDS.
- neco_start called first from main() blocks until that coroutine and all children finish; neco_main changes program behavior slightly (see API docs).
- Signal handling and worker threads are on by default on POSIX; disable with NECO_NOSIGNALS / NECO_NOWORKERS when embedding in a host that owns signals or threads.

## Known shortcomings

- No baseline measured: README gives only about 11 ns per switch on a Ryzen 9 5950X, with no libco, Boost.Context or ucontext comparison and no benchmark code. Directional only (tier D).
- neco_start switches into the new coroutine immediately; issues 10 and 12 report slow mass spawn; issue 6 (glibc below 2.30) is open; Windows and WASM lack fd I/O. The only number anywhere is about 11 ns per switch on a Ryzen 9 5950X with no baseline.

## Caveats and trade-offs

First-party single number (about 11 ns per switch, Ryzen 9 5950X), no baseline library or ucontext measured, no benchmark code or flags. Context switch is llco, whose assembly is adapted from minicoro. The README points to tidwall/bluebox for benchmarks (not checked).

Single scheduler per thread; pthread mutex/cond do not work well inside coroutines; Windows and WebAssembly support incomplete; Linux/macOS/BSD focus.

## Maintenance

Active (last commit 2026-05-30), MIT, 1.4k stars, single 8,761-line neco.c with a test suite claiming 100% coverage under sanitizers and Valgrind; six issues open, including C++ export, Windows sockets and old-glibc support.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): reject; tier before verification C, tier now D.
- **Tier reason:** README 'Fast context switching' says only that a switch takes about 11 ns on an AMD Ryzen 9 5950X via llco assembly; no baseline is measured on the page or in llco's README, so no speedup claim exists.
- **Verifier notes:** Metadata verified: MIT, 1.4k stars, last commit 2026-05-30. If the keep-and-document rule applies, keep it as tier D with a 'no baseline' shortcoming; the switch code is essentially minicoro's assembly via llco.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** first-party README
- **Pages the verifier opened:**
  - <https://github.com/tidwall/neco>
  - <https://raw.githubusercontent.com/tidwall/neco/HEAD/README.md>
  - <https://raw.githubusercontent.com/tidwall/neco/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/tidwall/llco/HEAD/README.md>
  - <https://github.com/tidwall/neco/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/tidwall/neco/HEAD/README.md>
  - <https://raw.githubusercontent.com/tidwall/neco/HEAD/neco.h>
  - <https://raw.githubusercontent.com/tidwall/neco/HEAD/neco.c>
  - <https://raw.githubusercontent.com/tidwall/neco/HEAD/LICENSE>
  - <https://github.com/tidwall/neco/issues?q=is%3Aissue>
  - <https://github.com/tidwall/neco/issues/10>
  - <https://github.com/tidwall/neco/issues/12>
  - <https://github.com/tidwall/bluebox>
  - <https://raw.githubusercontent.com/tidwall/bluebox/HEAD/README.md>
  - <https://raw.githubusercontent.com/tidwall/llco/HEAD/llco.c>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/tidwall/neco`) · [data/wave11/enrich/raw/github_com_tidwall_neco.json](../../../data/wave11/enrich/raw/github_com_tidwall_neco.json) (enrichment confidence 0.8)

</details>
