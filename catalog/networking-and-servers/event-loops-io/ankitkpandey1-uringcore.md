# uringcore

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [Event loops and async I/O](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0` · 🟢 active

> Rust/PyO3 io_uring asyncio event loop; claims \~3x lower single-op latency than uvloop, but loses on gather(100).

| | |
|---|---|
| **Beats** | uvloop (built on libuv) |
| **Claimed result** | 2.9-3.3x faster single-task latency than uvloop (e.g. sleep(0): 4.26us vs 12.53us); 26x fewer syscalls than uvloop under gather(100) |
| **Workload** | Python asyncio drop-in replacement using io_uring: single-task latency (sleep(0), lock_acquire, future result) and gather(100) concurrency, syscall counts via strace |
| **Metric** | latency |
| **Compiler and flags** | Rust release profile opt-level=3, lto=true, codegen-units=1 (Cargo.toml); rustc version not stated |
| **Adoption** | 2 stars |
| **Last commit** | 2026-01-11 |
| **Links** | [repository](https://github.com/ankitkpandey1/uringcore) · [benchmark](https://github.com/ankitkpandey1/uringcore#benchmarks) |

## Verdict

The 2.9-3.3x figures time one await (sleep(0), an uncontended Lock, an already-resolved Future) inside its own run_until_complete() call; uvloop sits at a flat 11-13 us on every such benchmark, slower than stock asyncio's 4-5 us, so the gap measures loop entry/exit cost, and in the committed run uringcore is only \~1.4x faster than stock asyncio (sleep(0) 3.56 vs 5.25 us) and slower than both on gather(100). The micro-runs used CPython 3.14.2 and Rust release flags (opt-level 3, LTO, 1 codegen unit) on an unnamed 'Linux 6.x' machine; the only hardware stated anywhere is ARCHITECTURE.md's TCP-echo run (AMD Ryzen 7 9700X, WSL2 kernel 6.6.87.2, Python 3.13.3, echo clients as threads in the same process), and VERIFY.md's pinned-CPU run shows parity with uvloop (5,573 vs 5,551 req/s).

## Use it when

- Linux 5.19+ hosts (6.0+ for SEND_ZC) where you control RLIMIT_MEMLOCK and seccomp, and you want to try io_uring under unmodified asyncio code.
- Code that calls run_until_complete() many times on tiny coroutines (CLI tools, test suites, sync-to-async bridges): the committed run shows 3.1-3.6 us per call vs 4.3-5.3 us for stock asyncio and 11-13 us for uvloop.
- Plain-TCP or UDP send-heavy services where syscall count or UDP sendto rate matters; the project reports \~831k vs \~550k sendto ops/s over stock asyncio (no hardware given; uvloop does not implement sock_sendto).
- Experiments comparing readiness-based and completion-based I/O in Python: the code base is small, Apache-2.0, and ships its benchmark and strace scripts.

## Skip it when

- Fan-out workloads with many concurrent tasks: in the committed run gather(100) takes 188 us vs 116 us for uvloop and 170 us for stock asyncio, and sleep_conc_100 takes 277 us vs 154 us for uvloop.
- Timer-heavy code: the committed call_later result is 186 us vs 12.7 us for uvloop; BENCHMARK.md's 13.5 us figure does not appear in any committed output.
- TLS servers or clients: create_server, create_connection and create_unix_connection raise NotImplementedError('SSL not yet supported') for ssl=; only start_tls() wraps a transport through a memory BIO, and kTLS is not integrated.
- Non-Linux, non-x86-64, or any Python other than 3.13 without a Rust 1.85+ toolchain: PyPI has only 0.9.1 with one cp313 manylinux_2_34 x86_64 wheel, and the 1.0.0 code in the repo (native scheduler, Jan 2026 benchmarks) is not published.
- Anything that needs production maturity: one author, 2 stars, no issues ever filed, and the CI Python test steps end in '|| echo ... skipping', so failing tests do not fail the build.

## How it is fast

Socket I/O is completion-based: recv, send, accept and connect go to the kernel as io_uring SQEs. It uses multishot recv and a provided-buffer ring on 5.19+, SEND_ZC on 6.0+, registered fixed files and IORING_OP_TIMEOUT timers, and it turns on SQPOLL by default so a kernel thread picks up submissions without io_uring_enter. Completions signal an eventfd registered with the ring, which the Python loop waits on with epoll; the ready queue, timer heap and futures live in Rust to cut per-callback interpreter work, and UDP sendto tries a direct non-blocking syscall first, using the ring only on EAGAIN. The headline single-op wins come from lower per-run_until_complete overhead, not from I/O; each task step still crosses the PyO3 boundary 8-12 times (ARCHITECTURE.md), which is why gather(100) is slower than uvloop.

## Compared with alternatives

Pick it over uvloop only on Linux when loop cost is dominated by short run_until_complete calls or uncontended asyncio primitives and you can accept beta TLS and pinned memory; for general servers uvloop is faster on fan-out and timers and far more mature. UCall also drives io_uring from Python but is its own RPC server API rather than an asyncio loop, and monoio or ringline are Rust runtimes that do not run asyncio code.

## Integration

| | |
|---|---|
| **Form** | module (Python package with a Rust PyO3 cdylib extension, built with maturin) |
| **Dependencies** | Runtime: typing-extensions. Build: maturin&gt;=1.4 and Rust crates pyo3 0.27, io-uring 0.7, libc, nix 0.30, parking_lot, crossbeam-queue, thiserror, tracing. |
| **Minimum toolchain** | Python 3.10+; Rust 1.85+ (Cargo edition 2024; the README badge 'rust 1.70+' is stale); Linux kernel 5.11+ (5.19+ for multishot recv and provided buffers, 6.0+ for SEND_ZC) |
| **Platforms** | Linux only. The only published wheel is CPython 3.13 x86_64 manylinux_2_34 (v0.9.1); other targets build from sdist or source. |
| **Thread safety** | One loop per thread, as with asyncio; call_soon_threadsafe wakes the loop through the eventfd. Fork is detected by a PID check, and generation IDs invalidate pre-fork buffers. Free-threaded (nogil) Python is untested (listed as future work). |
| **Drop-in for the baseline** | partial — same asyncio loop interface as uvloop (Runner loop_factory or policy), but ssl= on create_server/create_connection raises NotImplementedError, sendfile/sock_sendfile fall through to AbstractEventLoop (NotImplementedError), sock_recv_into/sock_recvfrom_into run in the thread-pool executor, and subprocess and start_tls are beta |

## Gotchas

- Each loop mmaps and mlocks its buffer pool with MAP_POPULATE. The code default is 4096 x 8 KiB = 32 MiB per loop; the README says 1024 x 64 KB and the package docstring 512 x 32 KB. A low RLIMIT_MEMLOCK makes loop creation fail with ENOMEM; tune URINGCORE_BUFFER_COUNT and URINGCORE_BUFFER_SIZE.
- SQPOLL is on by default (try_sqpoll=True, 1 s idle timeout), so every loop gets a kernel polling thread that spins for up to one second after each submission. The '0 io_uring_enter' strace result moves that cost to a kernel thread; it does not remove it.
- The README says 'pure io_uring, no epoll', but the Python loop blocks in select.epoll on the ring's eventfd and uses epoll for add_reader/add_writer. Its poll timeout is capped at 10 ms, so an idle loop wakes about 100 times per second.
- The committed benchmark outputs show uringcore failing mid-suite: sock_pair skipped with 'No buffers available for recv' (final_comparison.txt), and the run aborted with "'RuntimeError' object is not callable" (final_report.txt).

## Known shortcomings

- The 3x-over-uvloop claim measures loop start/stop overhead: each micro-benchmark wraps one await in its own run_until_complete, where uvloop (11-13 us) is slower than stock asyncio (4-5 us); against asyncio the gain is \~1.4x. Headline numbers disagree across README, final_comparison.txt and ARCHITECTURE.md. The committed run loses gather(100) (188 vs 116 us), sleep_conc_100 and call_later (186 vs 12.7 us), and crashed partway (sock_pair skipped, run aborted). 'Zero io_uring_enter' comes from SQPOLL moving work to a kernel polling thread. The TCP-echo run (Ryzen 7 9700X, WSL2) uses in-process client threads; the pinned run shows parity with uvloop (5,573 vs 5,551 req/s). 'Pure io_uring, no epoll' is false (waits in epoll on the eventfd, 10 ms cap). ssl= and sendfile raise NotImplementedError; sock_recv_into runs in a thread pool. PyPI stops at 0.9.1 with one wheel; needs Rust 1.85+ (badge says 1.70). Locks 32 MiB per loop (docs disagree), ENOMEM under low memlock. CI failures don't fail the build; one author, 2 stars, idle since 2026-01.

## Caveats and trade-offs

No CPU model; kernel given only as '6.x'. Loses to uvloop on gather(100) latency (README 139us vs 105us). The published figures disagree with each other: BENCHMARK.md lists uvloop sleep(0) at 105us and uringcore gather(100) at 156.9us, and the committed benchmarks/final_comparison.txt shows gather(100) at 188.11us for uringcore vs 116.15us for uvloop. Self-reported, dated Jan 2026.

Requires Linux kernel 5.11+ (5.19+ for best features); SQPOLL mode needs CAP_SYS_ADMIN or 5.12+ unprivileged SQPOLL.

## Maintenance

Single-author, Apache-2.0 project whose last commit was 2026-01-11 (quiet for \~8.5 months); PyPI stops at 0.9.1 from 2025-12-28, so using the benchmarked 1.0.0 means building the repo with maturin and Rust 1.85+.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README Benchmarks section compares against uvloop with the claimed numbers: sleep(0) 4.26us vs 12.53us, lock_acquire 3.90 vs 12.26, future_res 3.91 vs 12.81, and a strace total of 1,979 vs 52,587 syscalls. The code is public (benchmarks/benchmark_suite.py, benchmarks/syscall_bench.py) and the release flags are in Cargo.toml, but no CPU model or rustc version is given anywhere (BENCHMARK.md says only 'Linux kernel 6.x'), so tier C.
- **Verifier notes:** The claimed numbers match the README. The README Performance table also claims 15,394 vs 11,721 req/s against uvloop, about 1.31x (derived from page data), with no hardware stated. Metadata is correct: Apache-2.0, 2 stars, last commit 2026-01-11, active, not a fork.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/ankitkpandey1/uringcore>
  - <https://github.com/ankitkpandey1/uringcore#benchmarks>
  - <https://github.com/ankitkpandey1/uringcore/blob/main/BENCHMARK.md>
  - <https://github.com/ankitkpandey1/uringcore/blob/main/benchmarks/final_comparison.txt>
  - <https://github.com/ankitkpandey1/uringcore/blob/main/benchmarks/final_report.txt>
  - <https://github.com/ankitkpandey1/uringcore/blob/main/Cargo.toml>
- **Sources the enricher read:**
  - <https://github.com/ankitkpandey1/uringcore>
  - <https://github.com/ankitkpandey1/uringcore#benchmarks>
  - <https://raw.githubusercontent.com/ankitkpandey1/uringcore/main/README.md>
  - <https://raw.githubusercontent.com/ankitkpandey1/uringcore/main/BENCHMARK.md>
  - <https://raw.githubusercontent.com/ankitkpandey1/uringcore/main/ARCHITECTURE.md>
  - <https://raw.githubusercontent.com/ankitkpandey1/uringcore/main/VERIFY.md>
  - <https://raw.githubusercontent.com/ankitkpandey1/uringcore/main/CHANGELOG.md>
  - <https://raw.githubusercontent.com/ankitkpandey1/uringcore/main/WALKTHROUGH.md>
  - <https://raw.githubusercontent.com/ankitkpandey1/uringcore/main/Cargo.toml>
  - <https://raw.githubusercontent.com/ankitkpandey1/uringcore/main/pyproject.toml>
  - <https://raw.githubusercontent.com/ankitkpandey1/uringcore/main/.github/workflows/ci.yml>
  - <https://raw.githubusercontent.com/ankitkpandey1/uringcore/main/strace_log.txt>
  - <https://raw.githubusercontent.com/ankitkpandey1/uringcore/main/run_stdlib_tests.py>
  - <https://raw.githubusercontent.com/ankitkpandey1/uringcore/main/benchmarks/final_comparison.txt>
  - <https://raw.githubusercontent.com/ankitkpandey1/uringcore/main/benchmarks/final_report.txt>
  - <https://raw.githubusercontent.com/ankitkpandey1/uringcore/main/benchmarks/benchmark_suite.py>
  - <https://raw.githubusercontent.com/ankitkpandey1/uringcore/main/benchmarks/syscall_bench.py>
  - <https://raw.githubusercontent.com/ankitkpandey1/uringcore/main/benchmarks/server_benchmark.py>
  - <https://raw.githubusercontent.com/ankitkpandey1/uringcore/main/benchmarks/quick_bench.py>
  - <https://raw.githubusercontent.com/ankitkpandey1/uringcore/main/python/uringcore/loop.py>
  - <https://raw.githubusercontent.com/ankitkpandey1/uringcore/main/python/uringcore/__init__.py>
  - <https://raw.githubusercontent.com/ankitkpandey1/uringcore/main/python/uringcore/policy.py>
  - <https://raw.githubusercontent.com/ankitkpandey1/uringcore/main/src/lib.rs>
  - <https://raw.githubusercontent.com/ankitkpandey1/uringcore/main/src/ring.rs>
  - <https://raw.githubusercontent.com/ankitkpandey1/uringcore/main/src/buffer.rs>
  - <https://raw.githubusercontent.com/ankitkpandey1/uringcore/main/src/scheduler.rs>
  - <https://raw.githubusercontent.com/ankitkpandey1/uringcore/main/src/future.rs>
  - <https://raw.githubusercontent.com/ankitkpandey1/uringcore/main/src/buf_ring.rs>
  - <https://raw.githubusercontent.com/ankitkpandey1/uringcore/main/src/timer.rs>
  - <https://raw.githubusercontent.com/ankitkpandey1/uringcore/main/src/handle.rs>
  - <https://raw.githubusercontent.com/ankitkpandey1/uringcore/main/src/state.rs>
  - <https://raw.githubusercontent.com/ankitkpandey1/uringcore/main/src/fixed_fd.rs>
  - <https://github.com/ankitkpandey1/uringcore/tree/main/src>
  - <https://github.com/ankitkpandey1/uringcore/tree/main/python/uringcore>
  - <https://github.com/ankitkpandey1/uringcore/tree/main/benchmarks>
  - <https://github.com/ankitkpandey1/uringcore/tree/main/tests>
  - <https://github.com/ankitkpandey1/uringcore/tree/main/scripts>
  - <https://github.com/ankitkpandey1/uringcore/issues?q=is%3Aissue>
  - <https://github.com/ankitkpandey1/uringcore/pulls?q=is%3Apr>
  - <https://github.com/ankitkpandey1/uringcore/commits/main>
  - <https://pypi.org/pypi/uringcore/json>
  - <https://hn.algolia.com/api/v1/search?query=uringcore>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/ankitkpandey1/uringcore`) · [data/wave5/enrich/raw/github_com_ankitkpandey1_uringcore.json](../../../data/wave5/enrich/raw/github_com_ankitkpandey1_uringcore.json) (enrichment confidence 0.3)

</details>
