# Seastar

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [Event loops and async I/O](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Shard-per-core C++ futures framework with optional DPDK userspace TCP; its memcached beat libevent-based stock memcached 2-4x (2015).

| | |
|---|---|
| **Beats** | libevent |
| **Claimed result** | "SeaStar's Memcache server is 4X faster than the stock threaded memcache" and \~2x faster than the stock multi-process memcache; e.g. at 20 cores: Seastar+DPDK 4,426,457 ops/s vs stock multi-threaded 1,128,469 ops/s vs stock multi-process 2,281,064 ops/s |
| **Workload** | memaslap (libmemcached 1.0.18) GET/SET load against a Seastar-based, DPDK-backed memcached-protocol server vs stock Memcached 1.4.17 (libevent-based reactor, both multi-process and multi-threaded configurations), scaling from 2 to 20 CPU cores over a 40Gb NIC. |
| **Metric** | throughput |
| **Hardware** | 2x Intel Xeon E5-2695v3 (2.3GHz base, 35MB cache, 14 cores each = 28 physical/56 HT per host), 64GB DDR4, dual Intel XL710-QDA1 40Gb NICs (hardware shared with the project's HTTPD-benchmark wiki page) |
| **Adoption** | 9.4k stars; core reactor engine of ScyllaDB |
| **Last commit** | 2026-09-25 |
| **Links** | [repository](https://github.com/scylladb/seastar) · [benchmark](https://github.com/scylladb/seastar/wiki/Memcached-Benchmark) |

## Verdict

Seastar's own Feb 2015 wiki benchmark ran its sample memcached app on the native TCP stack over DPDK. At 20 cores it did 4.43M ops/s, against 1.13M for stock memcached 1.4.17 multi-threaded (libevent, kernel TCP) and 2.28M for one single-threaded memcached process per core. Load came from memaslap (libmemcached 1.0.18) over back-to-back 40GbE XL710 links; the hosts were 2x Xeon E5-2695v3 machines running Fedora 21 / Linux 3.17. Compiler and flags are not stated, the result mixes kernel bypass with the reactor design (no Seastar posix-stack throughput is given), and the page itself calls the 2x multi-process comparison unfair.

## Use it when

- You are writing a new, long-running C++ network or storage server on dedicated Linux machines and can give it every core and most of the RAM. ScyllaDB, Redpanda and Ceph Crimson are built this way.
- Throughput has to keep scaling across many cores and NUMA sockets. In the benchmark, threaded memcached (libevent) stayed between 0.44M and 1.13M ops/s from 8 to 20 cores, while Seastar went from 2.15M to 4.43M.
- Your data splits cleanly by key onto shards. The sample memcached hashes each key to an owning core and forwards requests with invoke_on.
- You need network I/O, direct (O_DIRECT) disk I/O and CPU/I/O isolation (scheduling groups, the I/O scheduler) in one runtime.
- You can dedicate DPDK-capable NICs with multiple hardware queues, plus hugepages, and want kernel networking out of the hot path.

## Skip it when

- You want to add an event loop to an existing app or library. Seastar owns main(), replaces malloc/operator new, and by default preallocates all RAM except max(1.5 GB, 7%). It is not embeddable the way libevent or libuv is.
- Shared hosts, containers or laptops. The reactor busy-polls, so you have to run with --overprovisioned, and open issue #3202 (2026) reports about 4-5x lower single-shard I/O throughput with --overprovisioned or short idle polling.
- Anything other than Linux. compatibility.md says only Linux is supported; there is no macOS, BSD or Windows support (Windows is an open feature request, #407).
- Code that blocks or does long CPU work without yielding. A single task stalls its whole shard (a 'reactor stall'), and there is no preemption check between chained .then() continuations.
- Expecting DPDK to be a free win. Open issue #192 (2016) measured Seastar memcached at 1.20M TPS with DPDK vs 1.23M with posix. Open issue #2622 (2025) saw 5-10 Gbit/s with DPDK vs 23 Gbit/s with the io_uring backend, and DPDK breaking above 16 connections. Open issue #383 (2018) reports 'sstring overflow' errors under load in the memcached app and half of stock memcached's throughput.

## How it is fast

Shared-nothing thread-per-core design: memory is split per core (NUMA-aware), refcounts and shared_ptr are non-atomic, and cores talk only through explicit message queues (smp::submit_to / sharded&lt;&gt;::invoke_on), so the hot path takes no locks. Each core runs a polling reactor whose kernel backend is io_uring when the build and kernel support it, falling back to linux-aio and then epoll; tasks yield after a 500 µs task quota. The optional native stack is a per-core TCP/IP stack on DPDK poll-mode drivers, with zero-copy buffers in both directions and NIC hardware queues keeping each connection on one core. In the wiki's perf profile of the DPDK build, no kernel functions appear and about 30 packets are handled per processing round under load.

## Compared with alternatives

Pick Seastar over libhv or Asio's io_uring backend when you are building the entire server and want per-core sharding of memory, CPU and disk I/O, not just a faster loop to embed; those two are the better fit for adding an event loop to an existing program. Pick it over F-Stack or mTCP when you want one framework API that runs on the kernel stack (io_uring/epoll) or a DPDK userspace stack, rather than a DPDK stack with a socket/epoll-style API.

## Integration

| | |
|---|---|
| **Form** | static lib (the default; shared libs via BUILD_SHARED_LIBS). Built with configure.py/CMake and consumed with find_package(Seastar) or pkg-config. |
| **Dependencies** | Boost &gt;=1.79 (filesystem, program_options, thread, unit_test_framework), c-ares &gt;=1.13, fmt &gt;=8.1.1, lz4 &gt;=1.7.3, yaml-cpp &gt;=0.5.1, protobuf &gt;=2.5.0, lksctp-tools, ragel 6.10, valgrind headers; liburing &gt;=2.0, hwloc &gt;=1.11.2 and LTTng-UST are on by default; GnuTLS/OpenSSL for TLS; DPDK is optional (a bundled, customized submodule) |
| **Minimum toolchain** | C++23 (or C++26). GCC or Clang, and only the last two major releases are supported (CI runs GCC 15/16 and Clang 21/22). CMake 3.13+. |
| **Platforms** | Linux only. CI covers x86-64 and aarch64. The io_uring, linux-aio and epoll reactor backends are chosen automatically; the DPDK native stack is optional (the README recommends 10G/40G NICs with multiple hardware queues). |
| **Thread safety** | Shared-nothing. Each shard is one thread, and Seastar objects (futures, seastar::shared_ptr, sockets) must stay on their owning shard. Work crosses shards through smp::submit_to, sharded&lt;&gt; and foreign_ptr; non-Seastar threads use alien::submit_to. |
| **Drop-in for the baseline** | no |

## Gotchas

- Memory: by default it takes almost all RAM at startup and splits it equally and statically across shards; limit it with -m or --reserve-memory. Freeing memory on a different shard works but is slow, so use foreign_ptr to return objects to their home shard.
- Build mode matters a lot. The README says release is about 2x faster than dev, 150x faster than sanitize and 300x faster than debug, and warns that Seastar is 'more sensitive to allocators and optimizations than usual'.
- Backend selection: the header comment says linux-aio is the default, but the code picks io_uring first when it is compiled in and detected. io_uring is skipped on kernels older than 5.17 with md RAID devices, and on kernels older than 5.12 when RLIMIT_MEMLOCK is under 8 MB. Open issue #2696 reports very poor write I/O with the default --poll-aio=1 on kernels up to 4.18 (RHEL 8).
- No link/ABI compatibility between Seastar versions. Breaking changes go through Seastar_API_LEVEL (level 10 arrived in 2026-04), and before C++23, lambda coroutines passed to continuation APIs can dangle (the 'lambda coroutine fiasco' doc).

## Known shortcomings

- The 2015 memcached comparison runs Seastar over DPDK with its own TCP stack, so it is not a pure reactor-vs-libevent result; the page calls its 2x multi-process comparison 'not a fair comparison', and the threaded memcached it beats 4x suffers lock contention. Requires applications written to Seastar's futures and shared-nothing model. No compiler or flags stated.
- Open issues contradict the DPDK advantage: memcached with DPDK ran slightly slower than on the kernel stack (#192), and DPDK gave 5-10 Gbit/s vs 23 with io_uring (#2622). 4-5x lower I/O throughput with --overprovisioned (needed on shared hosts, #3202). Linux-only, C++23, owns main(), replaces malloc and grabs almost all RAM at startup.

## Caveats and trade-offs

Benchmark is first-party (Seastar project's own GitHub wiki), not an independent third party; the page was created and last edited Feb 19 - Mar 1, 2015 (wiki history), so it is over 11 years old; compiler and build flags are not stated (only the build/release binary path); the Seastar side runs its own userspace TCP/IP stack over DPDK kernel bypass (--network-stack native --dpdk-pmd) while stock memcached uses the Linux kernel network stack, so the gain mixes kernel bypass with the reactor design and is not an isolated reactor-vs-libevent comparison; the 4x figure is against memcached's threaded mode, which the page says suffers from lock contention (mutex_trylock busy-wait), and the page itself calls the 2x multi-process comparison 'not a fair comparison'; the multi-threaded memcached configuration is not described in the setup section; the comparison is at the whole-application (memcached) level rather than a synthetic libevent-only microbenchmark, though memcached's own event loop is libevent-based.

Requires adopting Seastar's own future/promise async model and strict shard-per-core, share-nothing design (no implicit cross-core memory sharing); its highest numbers use a DPDK kernel-bypass network stack requiring hugepages and dedicated NICs, which is not a drop-in replacement for a plain epoll/libevent deployment; native TCP stack trades standard BSD-socket compatibility for speed.

## Maintenance

Actively maintained (last commit 2026-09-25, Apache-2.0, 9.4k stars, the runtime under ScyllaDB and Redpanda). It is a heavyweight framework you commit to, it needs the latest GCC/Clang and C++23, and the headline benchmark is 11 years old.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party wiki page (Seastar project, Feb 2015) with a raw-data table of Seastar+DPDK memcached vs stock Memcached 1.4.17 multi-process and multi-threaded at 2-20 cores. The CPU model (2x Xeon E5-2695v3, via the linked HTTPD-benchmark page), memaslap command lines and the Seastar app (apps/memcached/memcache.cc) are public, but the compiler and flags are never stated, so it cannot be A.
- **Verifier notes:** All of the claimed numbers match the 20-CPU row exactly, and both the '4X faster than the stock threaded memcache' and 'outperforms stock memcache by 2X' sentences are on the page. The hardware field matches the HTTPD-benchmark wiki's hardware section. Metadata checks out: Apache-2.0, 9,382 stars, not a fork or archived, last commit 2026-09-25.
- **Fields the verifier corrected:** `caveats`
- **Pages the verifier opened:**
  - <https://github.com/scylladb/seastar/wiki/Memcached-Benchmark>
  - <https://raw.githubusercontent.com/wiki/scylladb/seastar/Memcached-Benchmark.md>
  - <https://github.com/scylladb/seastar/wiki/Memcached-Benchmark/_history>
  - <https://raw.githubusercontent.com/wiki/scylladb/seastar/HTTPD-benchmark.md>
  - <https://github.com/scylladb/seastar>
  - <https://github.com/scylladb/seastar/tree/master/apps/memcached>
- **Sources the enricher read:**
  - <https://github.com/scylladb/seastar>
  - <https://github.com/scylladb/seastar/blob/master/README.md>
  - <https://github.com/scylladb/seastar/wiki/Memcached-Benchmark>
  - <https://raw.githubusercontent.com/wiki/scylladb/seastar/Memcached-Benchmark.md>
  - <https://raw.githubusercontent.com/wiki/scylladb/seastar/HTTPD-benchmark.md>
  - <https://github.com/scylladb/seastar/blob/master/doc/compatibility.md>
  - <https://github.com/scylladb/seastar/blob/master/doc/native-stack.md>
  - <https://github.com/scylladb/seastar/blob/master/doc/building-dpdk.md>
  - <https://github.com/scylladb/seastar/blob/master/doc/reactor_backend_asymmetric_uring.md>
  - <https://github.com/scylladb/seastar/blob/master/doc/tutorial.md>
  - <https://github.com/scylladb/seastar/blob/master/doc/lambda-coroutine-fiasco.md>
  - <https://github.com/scylladb/seastar/blob/master/src/core/reactor_backend.hh>
  - <https://github.com/scylladb/seastar/blob/master/src/core/reactor_backend.cc>
  - <https://github.com/scylladb/seastar/blob/master/include/seastar/core/reactor_config.hh>
  - <https://github.com/scylladb/seastar/blob/master/include/seastar/core/alien.hh>
  - <https://github.com/scylladb/seastar/blob/master/CMakeLists.txt>
  - <https://github.com/scylladb/seastar/blob/master/cmake/SeastarDependencies.cmake>
  - <https://github.com/scylladb/seastar/blob/master/.github/workflows/tests.yaml>
  - <https://github.com/scylladb/seastar/blob/master/apps/memcached/memcache.cc>
  - <https://github.com/scylladb/seastar/labels>
  - <https://github.com/scylladb/seastar/issues?q=performance>
  - <https://github.com/scylladb/seastar/issues/192>
  - <https://github.com/scylladb/seastar/issues/383>
  - <https://github.com/scylladb/seastar/issues/1017>
  - <https://github.com/scylladb/seastar/issues/2622>
  - <https://github.com/scylladb/seastar/issues/2696>
  - <https://github.com/scylladb/seastar/issues/3202>
  - <https://github.com/scylladb/seastar/security/advisories>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/scylladb/seastar`) · [data/wave5/enrich/raw/github_com_scylladb_seastar.json](../../../data/wave5/enrich/raw/github_com_scylladb_seastar.json) (enrichment confidence 0.85)

</details>
