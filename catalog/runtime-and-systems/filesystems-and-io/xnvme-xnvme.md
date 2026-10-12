# xNVMe

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Filesystems and I/O](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `BSD-3-Clause` · 🟢 active

> Samsung's single C API for NVMe I/O over io_uring, io_uring_cmd, libaio, SPDK and more; DuckDB on it beats default sync I/O.

| | |
|---|---|
| **Beats** | DuckDB default synchronous file I/O (psync) |
| **Claimed result** | Paper (CIDR 2026), per search snippet: DuckDB with the xNVMe-based nvmefs extension reaches comparable performance on non-I/O-intensive queries and up to 50% lower query times on I/O-intensive queries (aggregation, TPC-H) than DuckDB's default synchronous file I/O. |
| **Workload** | Single C API over io_uring, io_uring_cmd, libaio, SPDK and others; DuckDB nvmefs extension on xNVMe running aggregation and TPC-H |
| **Metric** | throughput |
| **Adoption** | 318 stars |
| **Last commit** | 2026-10-01 |
| **Links** | [repository](https://github.com/xnvme/xnvme) · [benchmark](https://www.vldb.org/cidrdb/papers/2026/p6-houlborg.pdf) |

## Verdict

Per search snippets of the CIDR 2026 paper (Houlborg et al., not opened here), DuckDB with the xNVMe-based nvmefs extension had about the same query times as DuckDB's default synchronous file I/O on non-I/O-intensive queries and up to 50% lower query times (about 2x at best) on I/O-intensive aggregation and TPC-H queries. Hardware, compiler and which backend gave the best result are not known from this session.

## Use it when

- You want one code path that can switch between io_uring, libaio, NVMe passthrough and SPDK at runtime, for example to benchmark or ship a storage engine across kernels and drivers.
- Database or storage engines that manage raw NVMe namespaces as blocks and want queue-depth asynchronous I/O instead of synchronous pread.
- Using NVMe features that file APIs hide: Zoned Namespaces, KV command set, Flexible Data Placement, or admin and vendor commands through passthrough.
- GPU-initiated or peer-to-peer storage I/O (CUDA or HIP) through the uPCIe backend.
- Cross-platform NVMe tooling on Linux, FreeBSD, macOS and Windows from one C codebase.

## Skip it when

- Applications that work with ordinary files and the page cache: xNVMe works at block and command level, and its gains need raw devices or passthrough, so a filesystem user is better served by liburing directly.
- When you only target Linux io_uring: liburing gives the same mechanism with one less layer and much wider ecosystem use.
- Environments where you cannot unbind the device from the kernel or get raw device permissions; the SPDK and uPCIe backends need that, and they need hugepages.
- If you need verified independent throughput numbers: the only quantitative claim seen here is the CIDR 2026 DuckDB result, known from search snippets.
- Multi-threaded submission onto one queue: the queue helpers are documented as not thread safe.

## How it is fast

Speed comes from the backends it reaches, not from new I/O machinery: asynchronous queues of up to 4096 outstanding commands with optional IOPOLL and SQPOLL polling, NVMe passthrough through io_uring_cmd that skips the block layer, and kernel bypass through SPDK or uPCIe. The xNVMe paper (Lund et al., arXiv 2411.06980, per search snippet) puts the abstraction's own cost at about 54 ns per I/O. In the CIDR 2026 DuckDB work the gain is from replacing DuckDB's synchronous file I/O with these asynchronous block paths through the nvmefs extension.

## Compared with alternatives

Pick it over liburing or SPDK when you need one API that runs on both (and on libaio, FreeBSD, macOS and Windows) or need NVMe command sets such as ZNS, KV or FDP; for Linux-only file I/O, liburing is simpler, and for maximum single-backend IOPS, SPDK directly avoids the extra layer.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | optional and auto-detected: liburing, libaio, libvfn, ISA-L, SPDK, CUDA, HIP; pthreads |
| **Minimum toolchain** | C (gnu11), Meson 0.59 or later; built as both static and shared libraries with LTO by default on non-Windows |
| **Platforms** | Linux, FreeBSD, macOS, Windows |
| **Thread safety** | Per-queue: xnvme_queue_get_cmd_ctx and xnvme_queue_put_cmd_ctx are documented as not thread safe; use one queue per thread. |
| **Drop-in for the baseline** | no |

## Gotchas

- Queue capacity must be a power of two in the range 1 to 4096.
- The backend is chosen at runtime by options, so a wrong or missing backend build (for example no liburing or SPDK found by Meson's auto features) silently leaves you with slower paths such as psync or the thread-pool emulation.
- The benchmarked DuckDB gain uses the nvmefs extension, which stores data as blocks on a raw device instead of files, so the comparison is not just a different syscall.
- Recent bug reports include hugepage exhaustion in the uPCIe backend and controller reference counting (both closed in mid-2026) and an open Windows fio clock-source failure.

## Known shortcomings

- The claim is snippet only (CIDR paper on vldb.org blocked): up to 50% lower query time, about 2x at best, against DuckDB's default sync I/O, hardware unknown; an arXiv snippet gives about 54 ns overhead per I/O. Queue ctx get/put is documented as not thread safe; queue capacity must be a power of 2 between 1 and 4096; v0.7.5, pre-1.0.

## Caveats and trade-offs

Paper PDF (vldb.org) is egress-blocked; claim taken from search snippets only. 'Up to 50% lower query time' is about 2x at best, not '50% faster', and it is measured at DuckDB level against DuckDB's default sync I/O, not as a raw I/O microbenchmark against io_uring/libaio. A related benchmark repo, itu-rad/nvmefs-benchmark (an ITU master's thesis on FDP write amplification), exists but carries no results, CPU model or flags on its page. There is also a companion arXiv paper, 'DuckDB on xNVMe' (2512.01490), which is blocked here. The repo README names the xnvmeperf tool but gives no numbers. The LICENSE file is BSD-3-Clause; the repo also has a LICENSES directory for other parts.

Abstraction layer; best numbers need NVMe passthrough (io_uring_cmd) or SPDK backends and raw device access.

## Maintenance

Actively developed by Samsung (version 0.7.5 in meson.build, 318 stars, BSD-3-Clause, last commit 2026-10-01), with CI and Coverity; usable today, but the API is still pre-1.0.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The repo page has no numbers. The claim comes from a peer-reviewed CIDR 2026 paper (Houlborg et al., 'Flexible I/O for Database Management Systems with xNVMe'), but vldb.org is egress-blocked, so it is known only from search snippets. That holds it at C until the paper is opened (a B candidate).
- **Verifier notes:** This is a real, active Samsung-backed project. Retier to B if a session can open the CIDR paper and confirm the hardware and baselines. Last commit 2026-10-01; 318 stars.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `baseline`, `caveats`
- **Shortcomings recorded by:** snippet only
- **Pages the verifier opened:**
  - <https://github.com/xnvme/xnvme>
  - <https://github.com/xnvme/xnvme/commits>
  - <https://raw.githubusercontent.com/xnvme/xnvme/HEAD/README.md>
  - <https://raw.githubusercontent.com/xnvme/xnvme/HEAD/LICENSE>
  - <https://github.com/itu-rad/nvmefs-benchmark>
- **Sources the enricher read:**
  - <https://github.com/xnvme/xnvme/issues?q=is%3Aissue+label%3Abug>
  - <https://raw.githubusercontent.com/xnvme/xnvme/HEAD/README.md>
  - <https://raw.githubusercontent.com/xnvme/xnvme/HEAD/meson.build>
  - <https://raw.githubusercontent.com/xnvme/xnvme/HEAD/meson_options.txt>
  - <https://raw.githubusercontent.com/xnvme/xnvme/HEAD/include/libxnvme_queue.h>
  - https://www.vldb.org/cidrdb/papers/2026/p6-houlborg.pdf (EGRESS_BLOCKED; search snippets only)
  - https://arxiv.org/pdf/2411.06980 (search snippet only)
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/xnvme/xnvme`) · [data/wave11/enrich/raw/github_com_xnvme_xnvme.json](../../../data/wave11/enrich/raw/github_com_xnvme_xnvme.json) (enrichment confidence 0.6)

</details>
