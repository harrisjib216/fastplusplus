# BqLog

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Logging and tracing](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Tencent's C++ async logger with a real-time compressed binary format; much higher end-to-end throughput than spdlog async and glog.

| | |
|---|---|
| **Beats** | spdlog |
| **Claimed result** | BqLog Compress 95 ms vs spdlog async 560 ms at 1 thread; 507 ms vs 32939 ms at 10 threads; glog 4485 ms to 127550 ms. BENCHMARK.md summary: 7-16x faster than fmtlog, 9-22x faster than Log4j2, 6-65x faster than spdlog (async), 47-252x faster than glog; the 7-18x versus quill appears in the README (6.7-17.7x derived from page data). Quill README call-site latency: 125/190 ns (p50/p99.9) vs spdlog 271/360 ns at 1 thread (slower than Quill, XTR, fmtlog, BinLog there). |
| **Workload** | Total wall time for 1-10 threads each writing 2M four-parameter log entries, flushed to disk; compressed binary appender vs async spdlog, synchronous glog, fmtlog, quill, Log4j2. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 9950X, 96 GB, Windows 11 Pro |
| **Compiler and flags** | MSVC 14.51, Release x64 (per-library flags in the CMake project at the benchmark_2.5.0 tag) |
| **Adoption** | 645 stars (Tencent) |
| **Last commit** | 2026-10-05 |
| **Links** | [repository](https://github.com/Tencent/BqLog) · [benchmark](https://github.com/Tencent/BqLog/blob/main/docs/BENCHMARK.md) |

## Verdict

In the author's Windows 11 / MSVC 14.51 Release x64 run on a Ryzen 9 9950X, 1-10 threads each logging 2M four-argument entries and flushing to disk took BqLog's compressed appender 95-507 ms versus spdlog 1.17 async 560-32,939 ms, quill 11.1 639-7,812 ms, fmtlog 672-7,934 ms and glog 0.7.1 4,485-127,550 ms; the runnable CMake project is at the benchmark_2.5.0 tag. Quill's independent Linux harness confirms BqLog beats spdlog at call-site latency (125 vs 271 ns p50, 1 thread) but ranks it below several siblings.

## Use it when

- High-volume logging from many threads where total time to get everything on disk matters (10 threads x 2M entries: 507 ms vs spdlog async 32,939 ms in the author's run).
- Shipped client products (games, mobile) that want verbose logs with small files: compressed output is about 6.3x smaller than text, with optional RSA2048+AES256 encryption at near-zero measured cost.
- Mixed-language processes (C++ plus C#/Java/Python/TypeScript/Go) that want one log engine shared by every wrapper.
- Apps that must survive crashes without losing buffered async logs: mmap-backed buffers are checksum-verified and replayed on restart.
- Targets with tight toolchain constraints: depends only on the C library and platform APIs, builds with Android ANDROID_STL=none.

## Skip it when

- You need minimal call-site latency: Quill's third-party harness (i5-12600, GCC 14.2, Linux) puts BqLog at 125/190 ns p50/p99.9 for one thread, slower than Quill, XTR, fmtlog, MS BinLog and PlatformLab NanoLog (only spdlog among the common ones is slower).
- You want human-readable files at maximum speed: in Quill's throughput table BqLog text mode does 5.49M msg/s vs Quill 6.44M and XTR 7.73M, and its binary mode (12.86M) trails MS BinLog (61.79M); the author's 'text beats everyone' result is from its own Windows/MSVC run.
- Your logs must be grep-able or shipped to text pipelines without a decode step; the binary format may be incompatible across BqLog versions, so archives need the matching decoder.
- Pre-2.3.1 deployments where disks can fill: issue #67 reports SIGBUS crashes and hangs on a full disk in v2.3.0 and earlier (sparse mmap files), since closed.
- You need custom output patterns or prefixes; these were open feature requests (#47, #76) and are not documented as supported.

## How it is fast

The compressed appender writes a template-based binary format (format string stored once, arguments as VLQ-encoded values, mixed UTF encoding), about 12 bytes per entry versus 65-82 bytes for text loggers, so far less formatting work and I/O. Producers copy arguments into a lock-free adaptive ring buffer (fetch_add with rollback, MISO/SISO modes) backed by memory-mapped files, and a worker thread does fused copy+hash, template caching and batched writes. The author's three-part 'Why is BqLog so fast' series documents the design.

## Compared with alternatives

Pick BqLog over Quill, fmtlog or XTR when end-to-end throughput, small on-disk size, encryption, crash recovery or multi-language support matter more than per-call latency; pick MS BinLog if you want a binary format with higher measured throughput in Quill's harness, and Quill or XTR for the lowest call-site latency with readable text.

## Integration

| | |
|---|---|
| **Form** | static lib \| shared lib \| source-drop (prebuilt packages from Releases; repo no longer ships binaries) |
| **Dependencies** | none beyond the C standard library and platform APIs (optional JNI/NAPI for wrappers) |
| **Minimum toolchain** | C++11; CMake build; benchmark built with MSVC 14.51 |
| **Platforms** | Windows x64, macOS, Linux (incl. embedded), iOS, Android, HarmonyOS/OpenHarmony, FreeBSD/NetBSD/OpenBSD/Solaris; x86, x86_64, ARM32, ARM64. No prebuilt binaries for PS5/Switch. |
| **Thread safety** | Log calls are thread-safe in sync and async modes; arguments are copied into the ring buffer during the call, so the only rule is that no other thread may modify a parameter while the call is in progress. Calling a synchronous flush from a console callback deadlocks. |
| **Drop-in for the baseline** | partial — same {}-style format strings as spdlog/fmt, but a different logger API, config-string setup, no positional or time format specs, and binary output for the fast path |

## Gotchas

- The headline numbers are for CompressedFileAppender; the text appender is 2.7x slower than compressed at 1 thread in the author's own table (258 vs 95 ms).
- Full-buffer behavior is configurable (discard new entries, block producers, or auto-expand); pick explicitly, since discarding drops logs silently under load.
- buffer_size and thread_mode cannot be changed after a log is created; create_log with an existing name returns the existing object and only updates mutable fields.
- Issue #71 reports BqLog beats fmtlog on macOS but loses on Ubuntu with no maintainer reply; the published table is Windows-only, so benchmark on your OS.

## Known shortcomings

- Quill's independent Linux harness puts BqLog text mode at 5.49M msg/s, below Quill (6.44M) and XTR (7.73M), which contradicts BENCHMARK.md's claim that text mode beats every text logger; binary mode does 12.86M against Microsoft BinLog's 61.79M. The fast numbers come from the compressed appender only (text appender 258 vs 95 ms at 1 thread). Issue 67 (closed): SIGBUS on a full disk in v2.3.0 and earlier; issue 71 (closed, no maintainer reply): loses to fmtlog on Ubuntu.

## Caveats and trade-offs

First-party benchmark on Windows with MSVC; the compared libraries were run with the BqLog author's configurations (glog synchronous by design, spdlog async blocking). Quill's multi-GB memory in the memory table is from its unbounded queues. Third-party Quill harness shows BqLog slower at call-site latency, so throughput win is mostly the compressed binary format. Exact MSVC flags beyond Release not stated in the doc.

Fastest results are for the compressed binary appender (needs a decoder); text appender is 2.3-2.8x faster than fmtlog by its own numbers; Java/C#/Python/etc wrappers exist and are slower than the C++ API.

## Maintenance

Actively developed (v2.5.0, commits in October 2026), Apache-2.0, used in Tencent's Honor of Kings; copyable via prebuilt static/dynamic libraries or source, with recent crash and disk-full bugs (#62, #67, #46) closed.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification A, tier now A.
- **Tier reason:** docs/BENCHMARK.md gives a runnable CMake project for every library at the benchmark_2.5.0 tag (benchmark/cross), MSVC 14.51 Release x64, AMD Ryzen 9 9950X, Windows 11; throughput table shows BqLog Compress 95 ms vs spdlog async 560 ms (1 thread) and 507 vs 32939 ms (10 threads), glog 4485 to 127550 ms. Code, compiler, build type and CPU are all stated (first-party, which does not bar A).
- **Verifier notes:** All throughput numbers match the table. Quill README throughput table (4M messages, Linux) also lists BqLog binary log at 311 ms vs MS BinLog 64 ms, so BqLog is not fastest in third-party runs. Stars 645, Apache-2.0, not archived; last commit date not checked beyond 'recent' on the repo page.
- **Fields the verifier corrected:** `claimed_speedup`
- **Shortcomings recorded by:** public benchmark code and independent harness
- **Pages the verifier opened:**
  - <https://github.com/Tencent/BqLog>
  - <https://raw.githubusercontent.com/Tencent/BqLog/HEAD/README.md>
  - <https://raw.githubusercontent.com/Tencent/BqLog/HEAD/docs/BENCHMARK.md>
  - <https://raw.githubusercontent.com/odygrd/quill/HEAD/README.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/Tencent/BqLog/HEAD/README.md>
  - <https://raw.githubusercontent.com/Tencent/BqLog/HEAD/docs/BENCHMARK.md>
  - <https://raw.githubusercontent.com/Tencent/BqLog/HEAD/docs/FAQ.md>
  - <https://raw.githubusercontent.com/Tencent/BqLog/HEAD/docs/API_REFERENCE.md>
  - <https://raw.githubusercontent.com/Tencent/BqLog/HEAD/docs/INTEGRATION_GUIDE.md>
  - <https://raw.githubusercontent.com/Tencent/BqLog/HEAD/docs/PERFORMANCE_DESIGN.md>
  - <https://github.com/Tencent/BqLog/issues?q=is%3Aissue>
  - <https://github.com/Tencent/BqLog/issues/71>
  - <https://github.com/Tencent/BqLog/issues/67>
  - <https://raw.githubusercontent.com/odygrd/quill/HEAD/README.md>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/tencent/bqlog`) · [data/wave11/enrich/raw/github_com_tencent_bqlog.json](../../../data/wave11/enrich/raw/github_com_tencent_bqlog.json) (enrichment confidence 0.8)

</details>
