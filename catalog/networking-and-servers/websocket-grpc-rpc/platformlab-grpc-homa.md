# grpc_homa (Homa transport plugin for gRPC)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [WebSocket, gRPC and RPC](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `no license` · 🟡 stale

> gRPC C++ transport plugin that replaces HTTP/2-over-TCP with the Homa kernel RPC protocol; reports \~40% lower short-RPC round-trip time.

| | |
|---|---|
| **Beats** | gRPC (default TCP transport) |
| **Claimed result** | short RPCs complete about 40% faster with Homa than with TCP (about 55 us round trip for Homa, vs. 90 us for TCP) |
| **Workload** | gRPC round-trip time for short unary RPCs using an insecure channel, comparing the stock TCP transport against the Homa transport plugin (HomaClient/HomaListener) |
| **Metric** | latency |
| **Compiler and flags** | Not stated for the README numbers. The repo Makefile builds with g++ using -O3 -DNDEBUG (release) or -g (debug), against a gRPC 1.57.0 install. No compiler version is given. |
| **Adoption** | 32 stars |
| **Last commit** | 2025-08-04 |
| **Links** | [repository](https://github.com/PlatformLab/grpc_homa) · [benchmark](https://github.com/PlatformLab/grpc_homa) |

## Verdict

The README's 'initial performance measurements' put a short gRPC RPC at about 55 us round trip over Homa versus about 90 us over the stock TCP transport (\~40% faster), with no hardware, NIC, kernel, compiler, load level or method given; the repo's rtt test (a mean over 50,000 sequential unary Sum calls on one client thread) is not tied to those numbers. On the Homa wiki the author separately puts \~60 us of an unloaded small gRPC round trip in gRPC software and \~30 us in TCP plus the network, which suggests the remaining 55 us is mostly gRPC itself and that Homa's tail-latency-under-load advantage was not measured here.

## Use it when

- Research or prototyping on Linux clusters where you control the kernel and can load HomaModule on every client and server host.
- Unary gRPC C++ services with small messages inside one datacenter, where tens of microseconds per round trip matter.
- Measuring how much of gRPC's round-trip time comes from TCP. The bundled test_client 'rtt' test runs over Homa, or over TCP with --tcp.
- As a starting point for reviving Homa support in gRPC, if you can build gRPC 1.57.0 from source and are ready to own the code.

## Skip it when

- When you need TLS or per-call auth: only insecure channel and server credentials exist.
- In production. The author suspended work in late 2023, and in 2025 (issue #17) he wrote that he does not recommend anyone try to use it. Open issues include a release-build segfault in BuildAndStart (#15) and Homa RPC timeouts on a setup where TCP works (#16).
- Across data centers, on mixed or public networks, on non-Linux hosts, or on managed platforms where you cannot load a custom kernel module on both ends.
- For bursty servers with many outstanding RPCs. Issue #14 reports kernel memory exhaustion that hung the host, and the author said poor application behavior can exhaust Homa kernel resources.
- For Java or other gRPC languages: Java support is only partly done, and the C++ code compiles against gRPC 1.57.0 internals, so newer gRPC releases are untested.

## How it is fast

Homa is a connectionless, message-based datacenter transport. A sender transmits the first rtt_bytes of a message at once as 'unscheduled' bytes. After that, the receiver sends GRANT packets that pace the rest of the message and set its network priority, so a short RPC needs no handshake and has no byte-stream head-of-line blocking. The plugin drops HTTP/2 framing for a packed 21-byte header (stream id, sequence number, metadata and body lengths, flags), sends gRPC slices through one gathered sendmsg iovec, and hands gRPC received slices that point into a kernel-shared mmapped buffer (SO_HOMA_RCVBUF), so contiguous payloads are not copied.

## Compared with alternatives

Pick this only if you must keep the gRPC C++ API and want the transport itself to cut small-RPC latency. brpc, grpcxx and Kitex beat gRPC in user space over plain TCP, need no kernel module and are maintained, while this plugin is only the gRPC front end for the catalogued HomaModule, so every gain depends on that driver.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | gRPC 1.57.0 built from source (the code includes internal src/core headers and abseil), protobuf, and the HomaModule kernel driver with its homa.h. The Makefile links upb, c-ares, re2, zlib, OpenSSL and libsystemd. googletest is needed only for unit tests. |
| **Minimum toolchain** | C++17 with g++ (the Makefile uses -std=c++17 -O3 -DNDEBUG); no minimum compiler version is stated |
| **Platforms** | Linux only; x86-64 as written (time tracing uses rdtsc inline asm); HomaModule on every host, which lists Mellanox ConnectX-4/5/6 and Intel E810 as known-good NICs |
| **Thread safety** | Not documented. Internally, one shared HomaClient and Homa socket per process are guarded by grpc_core::Mutex, and each stream has its own mutex. |
| **Drop-in for the baseline** | partial — same gRPC C++ API and stubs, but you must change the channel and server credentials, rebuild against gRPC 1.57.0 internals, give up TLS, and install the Homa kernel module on both ends |

## Gotchas

- The Makefile hard-codes the author's paths (HOMA_DIR, GRPC_INSTALL_DIR), so you must edit it by hand; there is no CMake or Bazel build.
- It tracks two moving targets: gRPC internals (branches exist only for gRPC 1.41.0, 1.43.0 and 1.57.0) and the HomaModule API. The last commit (Aug 2025) says 'Homa API has gone through several incompatible changes', and HomaModule has changed since, including a protocol change in Sept 2026.
- Homa messages are capped at 1,000,000 bytes (HOMA_MAX_MESSAGE_LENGTH). Larger gRPC messages are split across several Homa messages, and initial or trailing metadata that does not fit in one Homa message fails the RPC.
- Each socket mmaps a 1000 x 64 KB (\~64 MB) receive-buffer region. A server that leaves many RPCs outstanding can exhaust Homa kernel memory (issue #14).

## Known shortcomings

- The \~40% (55 vs 90 us) claim gives no hardware or method; development was suspended in late 2023; insecure channels only; the C++ code has no licence (reference only).
- The author suspended work and does not recommend using it (#17, 2025). Open bugs: release-only segfault in BuildAndStart (#15), Homa RPC timeouts where TCP works (#16). A burst of outstanding RPCs exhausted kernel memory and hung a host (#14). Compiles against internal gRPC src/core headers with branches only for gRPC 1.41/1.43/1.57, and HomaModule has changed incompatibly since. Makefile hard-codes the author's paths; x86-64 only (rdtsc); insecure channels only. Homa messages capped at 1 MB, oversized metadata fails the RPC. The 55 vs 90 us figure has no hardware, kernel, NIC or load stated and is a mean over sequential unary calls; tail latency under load, Homa's main claim, is not measured. No licence for the C++ code.

## Caveats and trade-offs

The 55us-vs-90us figure appears in the README ('Initial performance measurements') with no hardware, CPU model, compiler flags or method disclosed. It is a rough first-party claim, not a reproducible benchmark. The README says development was suspended in late 2023: C++ support is functional, Java only partly done, only insecure channels are supported, and the head is based on gRPC 1.57.0. It requires the out-of-tree HomaModule kernel driver. There is no LICENSE file, and the C++ plugin sources have no license header; only the Java binding files carry an ISC-style Stanford permission notice.

Requires the PlatformLab/HomaModule Linux kernel module installed on every machine; only insecure gRPC channels are supported; C++ support is functional but Java support is only partially implemented; author states the project is no longer under active development.

## Maintenance

Stale: work stopped in late 2023 and the last commit (Aug 2025) only ported the code to the Homa API of that time; the C++ code has no LICENSE file or license headers, so treat it as reference only, not something to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README gives first-party 'initial performance measurements' of short-RPC round-trip time with Homa versus gRPC's stock TCP transport (about 55us vs 90us, about 40% faster). It states no hardware, CPU model or method. The repo has an RTT test (test_client.cc 'rtt', with a --tcp option) and a -O3 release Makefile, but these are not tied to the stated numbers, so this is C.
- **Verifier notes:** The README numbers match the record exactly, and the baseline (gRPC's default TCP transport) is recognisable. The perf sentence dates from 2020-2022 README edits, before the 2023 suspension. Metadata checked: 32 stars, not archived, not a fork, license null, last commit 2025-08-04 (about 13.7 months ago, so stale is correct). usability stays reference because the C++ core is unlicensed.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/PlatformLab/grpc_homa>
  - <https://github.com/PlatformLab/grpc_homa/blob/main/README.md>
  - <https://github.com/PlatformLab/grpc_homa/blob/main/Makefile>
  - <https://github.com/PlatformLab/grpc_homa/blob/main/test_client.cc>
  - <https://github.com/PlatformLab/grpc_homa/blob/main/tcp_test.cc>
  - <https://github.com/PlatformLab/grpc_homa/blob/main/notes>
  - <https://github.com/PlatformLab/grpc_homa/blob/main/homa_client.cc>
- **Sources the enricher read:**
  - <https://github.com/PlatformLab/grpc_homa>
  - <https://github.com/PlatformLab/grpc_homa/blob/main/README.md>
  - <https://github.com/PlatformLab/grpc_homa/blob/main/Makefile>
  - <https://github.com/PlatformLab/grpc_homa/blob/main/notes>
  - <https://github.com/PlatformLab/grpc_homa/blob/main/homa_client.h>
  - <https://github.com/PlatformLab/grpc_homa/blob/main/homa_listener.h>
  - <https://github.com/PlatformLab/grpc_homa/blob/main/homa_stream.h>
  - <https://github.com/PlatformLab/grpc_homa/blob/main/homa_stream.cc>
  - <https://github.com/PlatformLab/grpc_homa/blob/main/homa_socket.h>
  - <https://github.com/PlatformLab/grpc_homa/blob/main/homa_socket.cc>
  - <https://github.com/PlatformLab/grpc_homa/blob/main/homa_incoming.h>
  - <https://github.com/PlatformLab/grpc_homa/blob/main/homa_incoming.cc>
  - <https://github.com/PlatformLab/grpc_homa/blob/main/wire.h>
  - <https://github.com/PlatformLab/grpc_homa/blob/main/test_client.cc>
  - <https://github.com/PlatformLab/grpc_homa/blob/main/tcp_test.cc>
  - <https://github.com/PlatformLab/grpc_homa/blob/main/stress.cc>
  - <https://github.com/PlatformLab/grpc_homa/blob/main/time_trace.h>
  - <https://github.com/PlatformLab/grpc_homa/blob/main/java/README.md>
  - <https://github.com/PlatformLab/grpc_homa/commits/main>
  - <https://github.com/PlatformLab/grpc_homa/issues/1>
  - <https://github.com/PlatformLab/grpc_homa/issues/12>
  - <https://github.com/PlatformLab/grpc_homa/issues/14>
  - <https://github.com/PlatformLab/grpc_homa/issues/15>
  - <https://github.com/PlatformLab/grpc_homa/issues/16>
  - <https://github.com/PlatformLab/grpc_homa/issues/17>
  - <https://github.com/PlatformLab/HomaModule>
  - <https://github.com/PlatformLab/HomaModule/blob/main/homa.h>
  - <https://github.com/PlatformLab/HomaModule/blob/main/protocol.md>
  - <https://homa-transport.atlassian.net/wiki/spaces/HOMA/overview>
  - <https://homa-transport.atlassian.net/wiki/spaces/HOMA/pages/262178/Homa+Projects>
  - <https://homa-transport.atlassian.net/wiki/spaces/HOMA/pages/19922945/Response+to+Ivan+Pepelnjak+s+Blog+Post>
  - <https://arxiv.org/abs/2210.00714>
  - <https://hn.algolia.com/api/v1/search?query=grpc_homa&tags=comment>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/platformlab/grpc_homa`) · [data/wave5/enrich/raw/github_com_platformlab_grpc_homa.json](../../../data/wave5/enrich/raw/github_com_platformlab_grpc_homa.json) (enrichment confidence 0.62)

</details>
