# LSQUIC (LiteSpeed QUIC)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [DNS, QUIC and HTTP/3](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `MIT` · 🟢 active

> LiteSpeed's C QUIC + HTTP/3 client/server library; LSQUIC-to-LSQUIC bulk downloads beat quiche-to-quiche 1.2-1.5x at 10 Gbit/s.

| | |
|---|---|
| **Beats** | quiche |
| **Claimed result** | Fig. 3 (default builds, 8 GB HTTP/3 download, 10G link): LSQUIC-LSQUIC pair 3004 Mbit/s vs quiche-quiche pair 2506 Mbit/s (\~1.2x, derived from page data). Fig. 10 (UDP receive buffer raised 32x to 6815744 B, both libraries rebuilt for the host CPU): LSQUIC\*-LSQUIC\* 3882 Mbit/s vs quiche\*-quiche\* 2590 Mbit/s (\~1.5x, derived from page data). The heatmap values are per-pair means (checked against the artifact's processed.csv). The mixed pair of an LSQUIC server and a quiche client drops to 1186 Mbit/s (1616 in Fig. 10). |
| **Workload** | HTTP/3 download of an 8 GB file over a 10 Gbit/s link between two dedicated bare-metal hosts, using an extended QUIC Interop Runner. All client/server pairs of 6 QUIC libraries were measured with Cubic/Reno congestion control. The paper states 50 repetitions per pair for Fig. 3. The Fig. 10 rerun used 20 repetitions per pair (configs/configs/baseline-optimized.yml). |
| **Metric** | throughput |
| **Hardware** | Default: AMD EPYC 7543 (32-core), Broadcom BCM57416 NIC, Debian Bullseye, kernel 5.10.0-8-amd64. Also repeated on AMD EPYC 7551P, Intel Xeon D-1518, Intel Xeon E5-1650, Intel Xeon Gold 6312U (paper Table I). |
| **Compiler and flags** | From the artifact repo tumi8/quic-10g-paper. Fig. 3: LSQUIC commit f3657f1f is built by implementations/lsquic/build_default.sh with `cmake -DBORINGSSL_DIR=../boringssl .` and no CMAKE_BUILD_TYPE, so lsquic's CMakeLists.txt defaults to Debug (-O0 -g3). BoringSSL a9670a8b uses a plain `cmake .`. quiche commit 95af1427 is built with `cargo build --release`. Fig. 10: LSQUIC\* uses CMAKE_BUILD_TYPE=Release (-O3 -g0) plus patches/march.patch (-march=native, -DLSQUIC_LOWEST_LOG_LEVEL=LSQ_LOG_INFO). quiche\* uses RUSTFLAGS='-C target-cpu=native' cargo build --release. The C compiler is GCC from Debian build-essential and Rust is the unpinned 'stable' rustup toolchain. No versions are recorded. |
| **Adoption** | 1.9k stars |
| **Last commit** | 2026-09-20 |
| **Links** | [repository](https://github.com/litespeedtech/lsquic) · [benchmark](https://arxiv.org/pdf/2309.16395) |

## Verdict

A peer-reviewed TUM study (IFIP Networking 2023) ran 8 GB HTTP/3 downloads over a direct 10 Gbit/s link between AMD EPYC 7543 hosts (Debian Bullseye, kernel 5.10) with Cubic/Reno. LSQUIC-LSQUIC pairs averaged 3004 Mbit/s vs 2506 for quiche-quiche (about 1.2x), even though that LSQUIC was an unoptimized Debug (-O0) GCC build and quiche was built with cargo --release. With a 32x larger UDP receive buffer, LSQUIC built Release -O3 -march=native and quiche built with target-cpu=native, the numbers were 3882 vs 2590 (about 1.5x). GCC and Rust versions are not recorded, and TCP/TLS reached 8010 Mbit/s on the same link. A 2026 follow-up (LSQUIC v4.2.0 vs quiche 0.23.2, Xeon Gold 6421N) measured a smaller lead, 3605 vs 3241 Mbit/s.

## Use it when

- You need an HTTP/3 or raw QUIC server or client in C, with a production record behind it (it ships in LiteSpeed's web servers), and bulk transfer throughput matters.
- You control both ends. The measured win is for LSQUIC-LSQUIC pairs: about 3.0 Gbit/s with default settings and about 3.9 Gbit/s after tuning, on a 10G link.
- Your app runs a single-threaded event loop per engine (libevent/libev style) and wants to own its sockets, or plug in its own packet-buffer allocation. The tumi8 LSQUIC-DPDK fork, for example, rewrote LSQUIC's packet allocation to write into DPDK mbufs.
- You want broad protocol coverage in one library: QUIC v2, compatible version negotiation, unreliable datagrams, ACK frequency, HTTP priorities, and WebTransport (a build option).
- Receive-side CPU or ACK traffic is a concern. Its ACK policy sends far fewer ACKs than quiche's did in the paper.

## Skip it when

- Serving clients you don't control, especially quiche-based ones. An LSQUIC server with a quiche client reached only 1186 Mbit/s (1616 after tuning), under half of the reverse pairing. The authors blame how the two libraries' flow control interacts.
- You want the kernel's UDP segmentation or receive offloads (GSO/GRO) to do the heavy lifting. The same group's NOMS 2026 follow-up reports that LSQUIC uses neither, and there MsQuic reached 8250 Mbit/s vs LSQUIC's 3605. Code search finds no UDP_SEGMENT or UDP_GRO in the repo.
- You plan to run BBR on low-RTT links. The paper saw LSQUIC with BBR reach only 30-70% of its Cubic goodput, with extra retransmissions. The internals doc says BBRv1 'does not work well for very small RTTs', which is why the default adaptive mode picks Cubic below 1.5 ms RTT.
- Heavy packet loss (4% or more). A user reported LSQUIC falling behind Linux TCP there (issue #142). It was closed as stale with no fix.
- You want one engine shared across threads, a memory-safe implementation, or easy packaging. BoringSSL has to be built from source (it needs Go), and thread safety is not a documented guarantee.

## How it is fast

The internals doc states the rule outright: 'performance trumps everything else'. On the send path, the engine interleaves packets from every connection into one batch and hands it to ea_packets_out, which makes sendmmsg-style sending possible. The batch grows toward 1024 while sends succeed and shrinks after a partial send. On the receive path, ACK merging combines consecutive ACK frames and processes them once per tick (the docs say this cuts ACK-processing calls 10-20x), and the delayed-ACK extension uses a PID controller to set packet tolerance. As a result the LSQUIC client sends far fewer ACKs: in the paper, quiche's client sent more than 16x as many. Other hot-path choices: fixed-size 'malo' pool allocators on 4 KB-aligned pages (the docs measured them 2.7x faster than malloc for 64-byte objects), stream data written straight into outgoing packets that are repackaged rather than rebuilt on loss, min-heap connection queues, and small 'mini' connections that handle the handshake.

## Compared with alternatives

Pick LSQUIC when you want a mature C library with HTTP/3 built in, running over the normal kernel UDP stack, and you control both endpoints. Choose ngtcp2 or TQUIC if their catalogued wins over quiche on bulk transfer (ngtcp2, about 1.6x download) or request rate (TQUIC, about 2.4x) match your workload better. Choose the LSQUIC-DPDK fork if you can dedicate NICs to kernel bypass and need close to line rate (about 10.8 Gbit/s).

## Integration

| | |
|---|---|
| **Form** | static lib (default) or shared lib (-DLSQUIC_SHARED_LIB=1), built with CMake |
| **Dependencies** | A TLS library: BoringSSL, built by hand (the README suggests tag 0.20250807.0). Since 4.3.2, CMake also detects an OpenSSL that exposes SSL_set_quic_tls_cbs, but the README does not document it. Also zlib and the ls-qpack and ls-hpack git submodules. libevent is needed only for the demo programs. Links with -lstdc++. |
| **Minimum toolchain** | CMake 3.0+ for lsquic (current BoringSSL needs CMake 3.22 and Go). Builds with GCC, Clang or MSVC; no minimum C standard or compiler version is documented. |
| **Platforms** | README 'tested on' list: Linux (i386, x86_64, ARM), FreeBSD i386, macOS x86_64, iOS ARM, Android ARM, Windows x86_64. CI runs on Linux, macOS, Windows and FreeBSD. |
| **Thread safety** | The docs don't say. Each engine is driven from a single thread. Global variables were removed in 2.20.0 so that separate engines can run on separate threads (issues #167 and #267), but the maintainers say their own use 'does not require strict thread-safety', and one user reported crashes from sharing an SSL_CTX across threads. |
| **Drop-in for the baseline** | no |

## Gotchas

- If CMAKE_BUILD_TYPE is not set, CMake builds Debug (-O0 -g3, plus AddressSanitizer when compiling with clang), and the README's build commands don't set it. The paper's baseline LSQUIC binary was built this way. Pass -DCMAKE_BUILD_TYPE=Release. Debug log calls stay compiled in even in Release unless you add -DLSQUIC_LOWEST_LOG_LEVEL=LSQ_LOG_INFO, which the CMakeLists leaves commented out.
- Throughput depends on the UDP receive buffer size. With the 208 KiB Linux default the LSQUIC client dropped 11.4k packets. A larger SO_RCVBUF gave 8.7% more goodput and cut the client's ACKs from 180k to 46k.
- Memory trade-offs: the malo pools never return their 4 KB pages until the allocator is destroyed, and the cached ACK used for merging takes 4 KB+, more than half the size of each full connection object.
- The sendmmsg/recvmmsg paths in the sample programs (-g/-j), which people often copy, failed with EFAULT at the commit the paper used (issue #434, filed by the paper's authors). They were fixed only in 4.7.1 in May 2026 (PR #646). A separate sendmmsg buffer overrun for batches over 1024 was fixed in PR #607.

## Known shortcomings

- No compiler version stated. In the artifact, the Fig. 3 LSQUIC binary was a Debug -O0 build against release-built quiche, so the published margin (about 1.2-1.5x goodput) is conservative.
- CMake builds Debug (-O0, ASan under clang) unless CMAKE_BUILD_TYPE is set, and the README does not set it; Release still keeps debug logging unless LSQUIC_LOWEST_LOG_LEVEL is defined. No UDP GSO/GRO (MsQuic reached 8250 vs 3605 Mbit/s in the NOMS 2026 study). The win holds only LSQUIC-to-LSQUIC (1186 Mbit/s with a quiche client). BBR weak at low RTT; sample sendmmsg paths fixed only in 4.7.1 (2026-05).

## Caveats and trade-offs

Peer-reviewed at IFIP Networking 2023 (Barcelona; DOI 10.23919/IFIPNetworking57963.2023.10186365, ISBN 978-3-903176-57-7). The code, configs and raw results are public (github.com/tumi8/quic-10g-paper), but the compiler versions are not stated, so the record is capped at B. The artifact build scripts show that the Fig. 3 LSQUIC binary was a default-Debug (-O0) build competing against release-built quiche, so that comparison understates LSQUIC. The paper's 'compile flags to optimize for the architecture' step (LSQUIC\*) is really Debug to Release -O3 plus -march=native. The win holds only for LSQUIC on both ends: an LSQUIC server with a quiche client reaches just 1186 Mbit/s. The same group's 2026 NOMS follow-up (LSQUIC v4.2.0, quiche 0.23.2, Xeon Gold 6421N) shows a smaller lead of 3605 vs 3241 Mbit/s (\~1.11x, derived), with MsQuic at 8250 Mbit/s well ahead of both.

Goodput is highly asymmetric by client/server combination: in this same study the quiche-server/LSQUIC-client pair reaches more than 2x the goodput of the LSQUIC-server/quiche-client pair, so the 'LSQUIC beats quiche' result holds for matched same-vendor pairs, not universally across mixed pairs. LSQUIC showed unintended retransmission behavior with BBR congestion control in this study (paper forced Cubic/Reno for all libraries to keep the comparison fair).

## Maintenance

Actively maintained and MIT-licensed: 4.10.0 came out 2026-09-13, the last commit was 2026-09-20, and it has about 1.9k stars. Treat the source and headers as the reference, because the internals guide still describes v2.29.6 and the repo's contributor guidance warns the API reference can lag the headers.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed IFIP Networking 2023 paper (DOI 10.23919/IFIPNetworking57963.2023.10186365). Its Fig. 3 and Fig. 10 heatmaps show LSQUIC-LSQUIC 3004/3882 vs quiche-quiche 2506/2590 Mbit/s, and the values match the means in the artifact's results/baseline/client-timestamps/goracle\*/processed.csv. The artifact repo tumi8/quic-10g-paper (configs/configs/baseline.yml, implementations/{lsquic,quiche}/build_\*.sh, quic-interop-runner/) and the AMD EPYC 7543 CPU are public, and the flags can be derived from the build scripts. It is not A because no compiler version is stated: GCC comes from Debian build-essential and Rust from an unpinned 'stable' rustup.
- **Verifier notes:** All numbers check out against the paper and the published CSVs. The key new fact is that the baseline-figure LSQUIC was an unoptimized Debug build (lsquic's CMake defaults to Debug when no build type is given), which strengthens rather than weakens the claim against release-built quiche. The metadata is verified: MIT, 1876 stars, last commit 2026-09-20, not archived.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/pdf/2309.16395>
  - <https://github.com/litespeedtech/lsquic>
  - <https://github.com/litespeedtech/lsquic/blob/f3657f1f27e79dd56587e880abe95426469625b0/CMakeLists.txt>
  - <https://github.com/tumi8/quic-10g-paper>
  - <https://github.com/tumi8/quic-10g-paper/blob/main/README.md>
  - <https://github.com/tumi8/quic-10g-paper/blob/main/implementations/lsquic/build_default.sh>
  - <https://github.com/tumi8/quic-10g-paper/blob/main/implementations/lsquic/build_optimized_for_march.sh>
  - <https://github.com/tumi8/quic-10g-paper/blob/main/implementations/lsquic/patches/march.patch>
  - <https://github.com/tumi8/quic-10g-paper/blob/main/implementations/quiche/build_default.sh>
  - <https://github.com/tumi8/quic-10g-paper/blob/main/implementations/quiche/build_optimized_for_march.sh>
  - <https://github.com/tumi8/quic-10g-paper/blob/main/configs/configs/baseline.yml>
  - <https://github.com/tumi8/quic-10g-paper/blob/main/configs/configs/baseline-optimized.yml>
  - <https://github.com/tumi8/quic-10g-paper/blob/main/results/baseline/client-timestamps/goracle/processed.csv>
  - <https://github.com/tumi8/quic-10g-paper/blob/main/results/baseline/client-timestamps/goracle-optimized/processed.csv>
  - <https://github.com/tumi8/quic-10g-paper/blob/main/results/baseline/client-timestamps/goracle/run1/result.json>
  - <https://www.net.in.tum.de/publications/>
  - <https://www.net.in.tum.de/fileadmin/bibtex/publications/papers/spaethj-noms2026.pdf>
- **Sources the enricher read:**
  - <https://github.com/litespeedtech/lsquic>
  - <https://github.com/litespeedtech/lsquic/blob/master/README.md>
  - <https://github.com/litespeedtech/lsquic/blob/master/docs/internals.rst>
  - <https://github.com/litespeedtech/lsquic/blob/master/docs/gettingstarted.rst>
  - <https://github.com/litespeedtech/lsquic/blob/master/docs/faq.rst>
  - <https://github.com/litespeedtech/lsquic/blob/master/docs/apiref.rst>
  - <https://github.com/litespeedtech/lsquic/blob/master/docs/tutorial.rst>
  - <https://github.com/litespeedtech/lsquic/blob/master/include/lsquic.h>
  - <https://github.com/litespeedtech/lsquic/blob/master/CMakeLists.txt>
  - <https://github.com/litespeedtech/lsquic/blob/master/src/liblsquic/CMakeLists.txt>
  - <https://github.com/litespeedtech/lsquic/blob/master/CHANGELOG>
  - <https://github.com/litespeedtech/lsquic/blob/master/EXAMPLES.txt>
  - <https://github.com/litespeedtech/lsquic/blob/master/AGENTS.md>
  - <https://github.com/litespeedtech/lsquic/blob/master/bin/test_common.c>
  - <https://github.com/litespeedtech/lsquic/blob/f3657f1f27e79dd56587e880abe95426469625b0/CMakeLists.txt>
  - <https://github.com/litespeedtech/lsquic/issues/123>
  - <https://github.com/litespeedtech/lsquic/issues/142>
  - <https://github.com/litespeedtech/lsquic/issues/167>
  - <https://github.com/litespeedtech/lsquic/issues/267>
  - <https://github.com/litespeedtech/lsquic/issues/434>
  - <https://github.com/litespeedtech/lsquic/issues/522>
  - <https://github.com/litespeedtech/lsquic/issues/593>
  - <https://github.com/litespeedtech/lsquic/pull/646>
  - <https://github.com/litespeedtech/lsquic/pull/607>
  - <https://arxiv.org/pdf/2309.16395>
  - <https://www.net.in.tum.de/fileadmin/bibtex/publications/papers/spaethj-noms2026.pdf>
  - <https://github.com/tumi8/quic-10g-paper/blob/main/implementations/lsquic/build_default.sh>
  - <https://github.com/tumi8/quic-10g-paper/blob/main/implementations/lsquic/patches/march.patch>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/litespeedtech/lsquic`) · [data/wave5/enrich/raw/github_com_litespeedtech_lsquic.json](../../../data/wave5/enrich/raw/github_com_litespeedtech_lsquic.json) (enrichment confidence 0.85)

</details>
