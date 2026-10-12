# libuv io_uring file backend

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Filesystems and I/O](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C` · `MIT` · 🟢 active

> libuv's optional Linux io_uring path for uv_fs_\* calls, replacing threadpool hand-off; off by default since 1.49.

| | |
|---|---|
| **Beats** | libuv threadpool file I/O |
| **Claimed result** | Commit message (#3952): 'Performance looks great; an 8x increase in throughput has been observed.' No methodology given. |
| **Workload** | Async read, write, fsync, fdatasync, stat via io_uring instead of the threadpool (libuv 1.45+). |
| **Metric** | throughput |
| **Adoption** | 27.2k stars |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/libuv/libuv) · [benchmark](https://github.com/libuv/libuv/commit/d2c31f429b87b476a7f1344d145dad4752a406d4) |

## Verdict

The only number is in the 1.45 commit d2c31f4 and PR #3952: a reviewer saw more than 8x throughput reading small chunks from /dev/zero versus libuv's own threadpool path; no hardware, kernel, compiler or harness is given. It measures dispatch overhead, not storage throughput.

## Use it when

- Linux servers (kernel 5.13+, ideally 6.1+) doing many small uv_fs_read/uv_fs_write/uv_fs_stat calls where threadpool hand-off overhead, not the device, is the bottleneck
- Programs that saturate libuv's default 4-thread pool with file requests and would otherwise raise UV_THREADPOOL_SIZE
- Embedders who control process start-up and can set both the loop option and the UV_USE_IO_URING=1 environment variable
- Processes that never change privileges (no setuid/setgid after loop start)

## Skip it when

- Default builds: since 1.49 file ops go to the threadpool unless the loop is configured with UV_LOOP_USE_IO_URING_SQPOLL and the env var is set, so there is nothing to gain without opting in
- Processes that drop privileges with setuid(): CVE-2024-22017 showed io_uring ops kept the old credentials when the ring existed before setuid()
- CPU-constrained or containerised hosts: SQPOLL runs a kernel polling thread per ring (idle timeout 10 ms) and older kernels (&lt;5.10.186) had a 100% CPU sqpoll bug
- Android, 32-bit ARM, ppc64/ppc64le and hppa below 6.1.51: io_uring is hard-disabled in source
- Large-block or device-bound I/O where the syscall path is not the bottleneck; the only published number is a /dev/zero microbenchmark

## How it is fast

Each request becomes one io_uring submission-queue entry on a 64-entry ring created with IORING_SETUP_SQPOLL, so a kernel polling thread picks it up without a syscall and without waking a userland worker thread; completions arrive through the ring's CQ, which is registered with the loop's epoll fd. This removes the threadpool's queue lock, thread wake-up and result hand-back per request, which dominates for small, cache-hot operations.

## Compared with alternatives

Pick it when the code is already on libuv (or Node.js) and you want io_uring for file ops without rewriting around liburing; use liburing directly for custom submission control, registered buffers or O_DIRECT, and SPDK when you need to bypass the kernel block layer entirely.

## Integration

| | |
|---|---|
| **Form** | static lib \| shared lib (CMake or autotools) |
| **Dependencies** | none (raw io_uring syscalls; no liburing) |
| **Minimum toolchain** | C11-capable compiler (uses _Atomic); CMake or autotools |
| **Platforms** | io_uring path: Linux x86-64/aarch64 and other 64-bit arches, kernel &gt;= 5.10.186 with IORING_FEAT_RSRC_TAGS (5.13+); libuv itself: Linux, macOS, Windows, BSDs, AIX, z/OS |
| **Thread safety** | Loop and handles are not thread-safe (design.rst); one ring per loop, used from the loop thread |
| **Drop-in for the baseline** | partial — same uv_fs_\* API and semantics, but must be enabled per loop with uv_loop_configure(loop, UV_LOOP_USE_IO_URING_SQPOLL) plus UV_USE_IO_URING=1 in the environment |

## Gotchas

- Docs (fs.rst) say the loop option alone enables io_uring, but uv__use_io_uring() in src/unix/linux.c returns false for SQPOLL when UV_USE_IO_URING is unset, and the code comment there claims the opposite ('unset or a positive number'); in practice both the option and UV_USE_IO_URING=1 are needed
- Fallback is silent: a full 64-entry ring, writes with nbufs &gt; IOV_MAX, an old kernel, or a failed ring setup all route to the threadpool with no error, so measure before assuming the fast path is active; reads with nbufs &gt; IOV_MAX are capped to IOV_MAX (short read)
- Per-op kernel gates: close needs &gt;= 6.1 (code constant 0x050A00 is labelled 5.16.0 but is 5.10.0, so 5.15.90+ longterm kernels also skip io_uring close), ftruncate needs 6.9, link/mkdir/rename/symlink/unlink need 5.15, cancel needs 6.0
- Node.js ships the same default (threadpool) and documents UV_USE_IO_URING=1 as the opt-in; the epoll_ctl batching ring is separate and always on since 1.50

## Known shortcomings

- The only number is a PR 3952 reviewer remark of more than 8x reading small chunks from /dev/zero against the threadpool, with no hardware or method; it measures dispatch overhead, not storage. In 1.53 file io_uring is off by default: the docs say UV_LOOP_USE_IO_URING_SQPOLL enables it, but src/unix/linux.c uv__use_io_uring() also needs UV_USE_IO_URING=1 (the code comment is wrong too). The uv__iou_fs_close constant 0x050A00 is labelled 5.16.0 but is 5.10.0, so io_uring close is skipped on 5.15.90+ longterm kernels. The entry is the whole libuv repo.

## Caveats and trade-offs

No workload, hardware or method is given; the baseline is libuv's own threadpool, not POSIX I/O. Per search results, libuv 1.49 made io_uring opt-in (UV_USE_IO_URING=1) after kernel and security problems (SQPOLL); in 1.50 io_uring is used for epoll batching, and the env var now affects only sqpoll. Default builds may therefore not use the io_uring file path at all. Node.js also patched io_uring off by default in its bundled libuv. Docs are CC-BY-4.0; code is MIT.

Linux only, kernel dependent, falls back to threadpool; some ops (access) have no io_uring path.

## Maintenance

libuv is actively maintained (1.53.0 released 2026-09-24, MIT); the io_uring file path is kept and still extended (cancel support in 1.53) but has been opt-in since 1.49 after CVE-2024-22017 and SQPOLL bugs.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification D, tier now D.
- **Tier reason:** The commit d2c31f4 ('linux: introduce io_uring support (#3952)') says only 'an 8x increase in throughput has been observed', with no workload, hardware or method. That is a directional claim, so it stays at D. The project is notable (27.2k stars).
- **Verifier notes:** The record's id is the whole libuv repo; if libuv is already listed elsewhere (event loops), consider filing this as a feature note or duplicate. I could not check the last commit date (left as is).
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** code reading by enricher
- **Pages the verifier opened:**
  - <https://github.com/libuv/libuv>
  - <https://github.com/libuv/libuv/commit/d2c31f429b87b476a7f1344d145dad4752a406d4>
- **Sources the enricher read:**
  - <https://github.com/libuv/libuv/commit/d2c31f429b87b476a7f1344d145dad4752a406d4>
  - <https://github.com/libuv/libuv/pull/3952>
  - <https://github.com/libuv/libuv/pull/2322>
  - <https://github.com/libuv/libuv/issues/4616>
  - <https://raw.githubusercontent.com/libuv/libuv/HEAD/README.md>
  - <https://raw.githubusercontent.com/libuv/libuv/HEAD/ChangeLog>
  - <https://raw.githubusercontent.com/libuv/libuv/HEAD/src/unix/linux.c>
  - <https://raw.githubusercontent.com/libuv/libuv/HEAD/src/unix/loop.c>
  - <https://raw.githubusercontent.com/libuv/libuv/HEAD/src/unix/fs.c>
  - <https://raw.githubusercontent.com/libuv/libuv/HEAD/docs/src/fs.rst>
  - <https://raw.githubusercontent.com/libuv/libuv/HEAD/docs/src/loop.rst>
  - <https://raw.githubusercontent.com/libuv/libuv/HEAD/docs/src/design.rst>
  - <https://raw.githubusercontent.com/libuv/libuv/HEAD/SUPPORTED_PLATFORMS.md>
  - WebSearch snippets: GHSA-vr4q-vx84-9g5x / libuv issue #4416 (CVE-2024-22017), nodejs/node PR #55114
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/libuv/libuv`) · [data/wave11/enrich/raw/github_com_libuv_libuv.json](../../../data/wave11/enrich/raw/github_com_libuv_libuv.json) (enrichment confidence 0.75)

</details>
