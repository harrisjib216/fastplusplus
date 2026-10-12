# bpftime

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Profilers and instrumentation](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `MIT` · 🟢 active

> Userspace eBPF runtime that runs unmodified libbpf/bpftrace uprobe programs with about 13-16x lower per-hit cost than kernel uprobes.

| | |
|---|---|
| **Beats** | Linux kernel uprobe/uretprobe (the in-kernel dynamic instrumentation path used by perf probe, bpftrace and bcc) |
| **Claimed result** | README: up to 10x lower uprobe overhead than kernel uprobe/uretprobe. Generated benchmark table: uprobe 2561.57 ns kernel vs 190.02 ns userspace (13.48x); uretprobe 3019.45 ns vs 187.10 ns (16.14x); uprobe+uretprobe 3119.28 ns vs 191.63 ns (16.28x). |
| **Workload** | Per-hit latency of an instrumented empty function (__bench_uprobe, __bench_uretprobe, both) with a uprobe/uretprobe attached, kernel eBPF uprobe versus bpftime userspace runtime. |
| **Metric** | latency |
| **Hardware** | Intel Core Ultra 7 258V (4 cores, 4 threads), 15.07 GB RAM, Linux 6.11.0-24-generic (results generated 2025-04-30) |
| **Adoption** | 1.6k stars |
| **Last commit** | 2026-10-03 |
| **Links** | [repository](https://github.com/eunomia-bpf/bpftime) · [benchmark](https://github.com/eunomia-bpf/bpftime/tree/master/benchmark) |

## Verdict

On an Intel Core Ultra 7 258V running Linux 6.11 (results generated 2025-04-30), an empty probed function costs 2561.57 ns per call with a kernel uprobe vs 190.02 ns under bpftime (13.48x), and 3019.45 vs 187.10 ns for uretprobe (16.14x); older runs on an i7-11800H (kernel 6.2) show 3224 vs 315 ns. The benchmark build is RelWithDebInfo with LLVM 15 JIT and LTO and the harness is gcc -O3, but compiler versions are not stated; the OSDI '25 paper (not opened, egress blocked; search snippet only) reports sslsniff overhead on nginx falling from 28% with kernel eBPF to 7.4%.

## Use it when

- Tracing hot userspace functions (malloc, SSL_read/SSL_write, request handlers) at rates where kernel uprobe cost of about 2.5-3 us per hit distorts the workload; bpftime measured about 190 ns per hit.
- Reusing an existing libbpf or bpftrace uprobe tool unchanged, but with lower overhead, on Linux x86-64.
- Environments without root or a modern eBPF-capable kernel (containers, older kernels), using the userspace PREVAIL verifier instead of the kernel one.
- Embedding a sandboxed eBPF extension mechanism into your own process (nginx plugin, Redis tuning examples), where the OSDI '25 paper reports about 2% overhead for an nginx extension (search snippet).

## Skip it when

- System-wide observability: it only sees processes it was injected into, and it cannot read kernel data structures such as task_struct or use kernel-only helpers and kfuncs.
- Map-heavy programs: in the same 2025 table userspace hash_map_lookup is 22152.81 ns vs 12375.69 ns kernel per 1000-op probe, and per-CPU hash and array maps are 1.3x to 4x slower; the older 2024 run shows syscall tracepoints slower in userspace (232.6 ns vs 151.8 ns).
- Untrusted or adversarial targets: the eBPF code shares the target's address space (MPK isolation is an optional build), and the measured read/write speedups were built with ENABLE_PROBE_READ_CHECK=0 and ENABLE_PROBE_WRITE_CHECK=0.
- Multi-threaded event streaming where loss matters: open bugs report ring-buffer data loss with multi-threaded apps (#429) and concurrent map access races on delete (#320).
- As a sampling profiler replacement for perf: it is an instrumentation runtime, not a profiler.

## How it is fast

Kernel uprobes plant an int3 breakpoint, so every hit costs a trap into the kernel and back; bpftime instead rewrites the function prologue with a frida-gum inline hook that jumps to a trampoline running JIT-compiled eBPF (LLVM-based llvmbpf, or ubpf) in the same address space, with no mode switch. Syscall hooks use zpoline/syscall_intercept-style binary rewriting of the text segment. bpf_probe_read/write_user become plain memory accesses (in the benchmark build the safety checks are compiled out), and maps live in Boost.Interprocess shared memory.

## Compared with alternatives

Pick it over funtrace or magic-trace when you want programmable eBPF probes (filters, maps, existing bcc/libbpf tools) on uninstrumented binaries without recompiling; pick funtrace for lowest per-call cost (under 10 ns) when you can recompile with instrumentation, and E9Patch when you need static binary rewriting rather than runtime injection.

## Integration

| | |
|---|---|
| **Form** | shared lib (LD_PRELOAD agent and syscall-server .so) plus CLI tools; VM also as a static library |
| **Dependencies** | libelf, zlib, libssl, Boost (1.74 recommended), yaml-cpp, binutils-dev, LLVM (15 in the benchmark build) for the LLVM JIT, frida-gum, libbpf, spdlog, optional PREVAIL verifier |
| **Minimum toolchain** | C++20 (CMAKE_CXX_STANDARD 20), CMake 3.15+, gcc 12+ or clang 16+ recommended; tested on Ubuntu 23.04 |
| **Platforms** | Linux (x86-64 is the benchmarked and documented target; CMake has arm32 handling and frida is unavailable on riscv64); macOS userspace-only build with libbpf disabled; no Windows |
| **Thread safety** | Probes fire on any thread of the target; maps are in shared memory with locking, but open issues report races on map element delete (#320) and ring-buffer loss with multi-threaded apps (#429). |
| **Drop-in for the baseline** | partial — the same eBPF objects and libbpf/bpftrace front ends run unmodified, but targets must be launched or attached via bpftime and kernel-only helpers are unavailable |

## Gotchas

- Run `bpftime load` before `bpftime start`, or the probe is not attached; stale shared memory gives 'boost::interprocess::interprocess_exception: File exists' and needs bpftimetool cleanup or sudo.
- Plain `cmake` defaults to a Debug build (CMAKE_BUILD_TYPE Debug, ubsan) and `make build` is Debug too; use `make release` or the benchmark target (RelWithDebInfo, LLVM JIT, LTO) before measuring.
- The headline microbenchmark times an empty noinline function called 100,000 times with CLOCK_MONOTONIC_RAW (benchmark/test.c, gcc -O3), averaged over 10 runs; the unhooked call costs about 2.4 ns, so these are pure probe-dispatch costs, not application overhead.
- LTO can strip symbols defined in inline assembly (open issue #83).

## Known shortcomings

- The read and write speedups are built with ENABLE_PROBE_READ_CHECK=0 and ENABLE_PROBE_WRITE_CHECK=0; map operations are slower than kernel eBPF. Build is RelWithDebInfo with an LLVM 15 JIT and LTO (test.c gcc -O3), compiler versions not stated. Open bugs: 429 (ring buffer loss) and 320 (map delete race). OSDI paper numbers are snippet only (sslsniff overhead 28% kernel vs 7.4% bpftime).

## Caveats and trade-offs

Compiler and flags are not stated on the benchmark page or in benchmark/uprobe (older runs in benchmark/uprobe list i7-11800H and Xeon Gold 5418Y, kernel 6.2). Kernel uprobe is not one of the listed baselines (perf, gprof, Valgrind), though perf probe and bpftrace use it. Microbenchmark of an empty probed function; the README says up to 10x, the generated table shows 13-16x. The same table shows bpftime slower than kernel eBPF on several map operations (hash_map_lookup 22152.81 vs 12375.69 ns; per-CPU hash/array map lookups and updates), so only probe entry/exit and memory read/write are faster. OSDI '25 paper (usenix.org) was not opened (egress blocked); its claims come from search snippets. Not a sampling profiler; it is an instrumentation runtime.

Runs eBPF programs in userspace via LD_PRELOAD or a daemon, so it only sees processes it is injected into; no kernel-wide view; needs its own verifier (PREVAIL) or the kernel verifier; kernel baseline requires root and a recent kernel.

## Maintenance

Actively developed (last commit 2026-10-03, 1.6k stars, MIT) with a peer-reviewed OSDI '25 paper, though about 98 open issues including 15 labelled bug.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now B.
- **Tier reason:** benchmark/README.md shows the uprobe table exactly as claimed (2561.57 vs 190.02 ns, 13.48x; 3019.45 vs 187.10, 16.14x; 3119.28 vs 191.63, 16.28x) on an Intel Core Ultra 7 258V, with code in benchmark/uprobe, but no compiler or flags are stated, so not A. The win over kernel uprobes is also the subject of the peer-reviewed OSDI '25 paper (seen only through search snippets: up to 10x lower uprobe overhead, \~2% vs up to \~30% throughput drop on OpenSSL), which supports B.
- **Verifier notes:** Metadata checked on github.com: MIT, 1.6k stars, not a fork, not archived, last commit 2026-10-03. The kept-B rests partly on the OSDI paper seen only via snippets; retier if the paper is later read.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** code reading by enricher
- **Pages the verifier opened:**
  - <https://github.com/eunomia-bpf/bpftime>
  - <https://github.com/eunomia-bpf/bpftime/commits/master>
  - <https://github.com/eunomia-bpf/bpftime/tree/master/benchmark/uprobe>
  - <https://raw.githubusercontent.com/eunomia-bpf/bpftime/HEAD/README.md>
  - <https://raw.githubusercontent.com/eunomia-bpf/bpftime/HEAD/benchmark/README.md>
  - <https://raw.githubusercontent.com/eunomia-bpf/bpftime/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/eunomia-bpf/bpftime>
  - <https://github.com/eunomia-bpf/bpftime/tree/master/attach>
  - <https://github.com/eunomia-bpf/bpftime/issues?q=is%3Aissue+is%3Aopen+label%3Abug>
  - <https://raw.githubusercontent.com/eunomia-bpf/bpftime/HEAD/README.md>
  - <https://raw.githubusercontent.com/eunomia-bpf/bpftime/HEAD/benchmark/README.md>
  - <https://raw.githubusercontent.com/eunomia-bpf/bpftime/HEAD/benchmark/uprobe/README.md>
  - <https://raw.githubusercontent.com/eunomia-bpf/bpftime/HEAD/benchmark/uprobe/benchmark.py>
  - <https://raw.githubusercontent.com/eunomia-bpf/bpftime/HEAD/benchmark/test.c>
  - <https://raw.githubusercontent.com/eunomia-bpf/bpftime/HEAD/benchmark/Makefile>
  - <https://raw.githubusercontent.com/eunomia-bpf/bpftime/HEAD/Makefile>
  - <https://raw.githubusercontent.com/eunomia-bpf/bpftime/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/eunomia-bpf/bpftime/HEAD/installation.md>
  - WebSearch snippet: https://www.usenix.org/system/files/osdi25-zheng-yusheng.pdf and https://eunomia.dev/others/miscellaneous/osdi-talk/ (pages not opened; people.cs.vt.edu PDF fetch returned 403)
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/eunomia-bpf/bpftime`) · [data/wave11/enrich/raw/github_com_eunomia_bpf_bpftime.json](../../../data/wave11/enrich/raw/github_com_eunomia_bpf_bpftime.json) (enrichment confidence 0.8)

</details>
