# PcapPlusPlus

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [Event loops and async I/O](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Unlicense` · 🟢 active

> C++ packet capture, parsing and crafting library; parses pcap TCP/DNS traffic 1.06-1.26x faster than libtins in its maintainers' run.

| | |
|---|---|
| **Beats** | libtins v4.5 (C++ packet parsing and crafting library) |
| **Claimed result** | Versus libtins v4.5: TCP 0.197 s vs 0.209 s (2,538,071 vs 2,392,344 packets/s), TCP with options 0.202 s vs 0.241 s (2,475,247 vs 2,074,688 packets/s), DNS 0.208 s vs 0.263 s (2,403,846 vs 1,901,140 packets/s), about 1.06x, 1.19x and 1.26x (derived from page data). Not faster than libpcap v1.10.1 on the same page (0.120 s, 0.124 s, 0.031 s), whose loop only counts packets. |
| **Workload** | Reading and parsing a generated pcap file of 500,000 packets (payload size 742 bytes, three runs averaged) with each library's layer parser: TCP packets without options, TCP with options, and DNS packets (queries and answers counted), using Matias Fontanini's packet-capture-benchmarks suite. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-8700 3.2GHz, 16GB RAM, Windows 10 host running Ubuntu 22.04 in WSL2 |
| **Compiler and flags** | g++ 11.4.0 on Ubuntu 22.04 (WSL2); no flags stated on the page. In the suite, Makefile.in compiles pcapplusplus/benchmark.cpp with -g -O2 -std=c++11, and libtins/benchmark.cpp with @LIBTINS_CXXFLAGS@, which configure.ac sets after AC_PROG_CXX to the CXXFLAGS plus -std=c++11 (autoconf's default -g -O2 when CXXFLAGS is unset) but replaces with only -I&lt;path&gt; when --with-libtins-include-path is passed. The build flags of the PcapPlusPlus v24.09 and libtins v4.5 libraries themselves are not stated. |
| **Adoption** | 3.1k stars |
| **Last commit** | 2026-10-09 |
| **Links** | [repository](https://github.com/seladb/PcapPlusPlus) · [benchmark](https://raw.githubusercontent.com/PcapPlusPlus/pcapplusplus.github.io/HEAD/docs/benchmark.mdx) |

## Verdict

The PcapPlusPlus website's benchmark page (maintainers' run) used mfontanini/packet-capture-benchmarks with PcapPlusPlus v24.09, libtins v4.5 and libpcap 1.10.1, g++ 11.4.0, on Ubuntu 22.04 under WSL2 on an i7-8700: over a generated 500,000-packet pcap (742-byte payload, integer-millisecond average of 3 runs) PcapPlusPlus took 0.197/0.202/0.208 s for TCP, TCP-with-options and DNS against libtins's 0.209/0.241/0.263 s (1.06x, 1.19x, 1.26x, derived from page data), and was slower than a libpcap loop that only counts packets. The TCP-with-options and DNS rows do unequal work (deferred options; libtins re-parses and materialises DNS vectors), and library build flags are not stated (project defaults would be -O3 Release for PcapPlusPlus and -O2 RelWithDebInfo for libtins).

## Use it when

- Offline analysis of pcap/pcapng files where most packets are only classified or counted by layer type, so zero-copy layer views and on-demand option decoding pay off.
- Applications that need one C++ API across capture engines: libpcap on Linux/macOS/FreeBSD, Npcap on Windows, and DPDK, AF_XDP or PF_RING for line-rate capture.
- Tools that need protocol coverage libtins lacks (QUIC, TLS records, SSH, BGP, GTP, SOME/IP, Modbus, LDAP, X509) or built-in TCP reassembly, IP defragmentation and JA3/JA3S fingerprinting.
- Projects that want a permissive licence: the Unlicense places it in the public domain, so it can be vendored without attribution.

## Skip it when

- When you need every TCP option or DNS record decoded for every packet anyway: the libtins gap then shrinks toward the 1.06x TCP-without-options result, and libtins's owning PDU objects may suit your code better.
- When you only need to count or hash raw frames: plain libpcap was 1.6x (TCP) to 6.7x (DNS) faster in the same run because it skips parsing and the per-packet copy and allocations.
- Concurrent edits: the maintainer states a Packet or Layer must be parsed and edited on one thread; there is no internal locking.
- Builds pinned to unreleased master between the libpcap-free pcap reader change (commit 44e9085, after v25.05) and the fix in PR #2072 (March 2026): issue #2071 measured pcap file reading 22x slower than v25.05 (1.857 s vs 0.084 s for 485,760 packets).

## How it is fast

Each Layer is a typed view into the RawPacket's single buffer, so headers and payloads are read in place and no per-layer copy is made; libtins by contrast copies the payload into a RawPDU std::vector (742 bytes per packet in this benchmark) and decodes every TCP option into a vector when it builds the TCP PDU. PcapPlusPlus still allocates one object per layer at Packet construction (all layers are parsed eagerly unless you pass parseUntil), but TCP options are only walked on demand through a TLV reader (getTcpOption), and DNS answer data is decoded only when asked. Much of the measured margin is therefore copy avoidance and deferred option decoding, not a faster parser for the same work.

## Compared with alternatives

None of the catalogued event-loops-io siblings parses packets: F-Stack, mTCP and Seastar are DPDK-based TCP stacks or servers, and libuv/libevent-style loops (libev, libhv, picoev) move bytes over sockets. Pick PcapPlusPlus when the task is decoding or crafting captured frames, possibly on top of DPDK or AF_XDP, rather than serving connections.

## Integration

| | |
|---|---|
| **Form** | static lib by default (BUILD_SHARED_LIBS=OFF; shared optional): Common++, Packet++ and Pcap++; also packaged in vcpkg, Conan, Homebrew |
| **Dependencies** | Packet++/Common++: none beyond the standard library; Pcap++: libpcap (Linux, macOS, FreeBSD, Android) or Npcap/WinPcap (Windows), optional DPDK, PF_RING, libbpf/AF_XDP, WinDivert; can be built without Pcap++ (PCAPPP_BUILD_PCAPPP=OFF) |
| **Minimum toolchain** | C++14 and CMake 3.12 on current master (v24.09, the benchmarked release, required C++11); the project's CMake defaults to a Release build |
| **Platforms** | Linux, Windows, macOS, Android, FreeBSD; x86-64 and aarch64; DPDK, PF_RING and AF_XDP back-ends are Linux-only |
| **Thread safety** | Not thread-safe per object: per the maintainer (issue #703), a Packet or Layer is parsed/edited on one thread and may then be read from others; devices and reassembly objects are the application's job to synchronise. |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness asymmetry in the 'TCP with options' test (the 1.19x row): the callback only counts packets, so PcapPlusPlus never decodes the options (TcpLayer's constructor does nothing with them), while libtins's TCP constructor decodes all six generated options into a vector. PcapPlusPlus's time grows 5 ms over the no-options test, libtins's 32 ms; the row measures eager versus deferred option decoding, not equal work.
- pcpp::Packet(&rawPacket) parses every layer eagerly and allocates one object per layer (and one per DNS resource, with its name decoded into a std::string); pass parseUntil/parseUntilLayer to stop early when you only need the lower layers.
- Layer pointers and DnsQuery/DnsResource pointers are owned by the Packet and dangle once it (or the RawPacket buffer) is destroyed or edited in a way that reallocates the buffer.
- Parser hardening is still ongoing: recent master commits fix out-of-bounds reads in the WireGuard, ASN.1 and S7Comm layers found by OSS-Fuzz targets; no CVE or GitHub security advisory is published.

## Known shortcomings

- Downgraded B to C: the docs/benchmark.mdx run is first-party (maintainers' page) on the libtins author's mfontanini/packet-capture-benchmarks harness; the win over libtins is small (1.06x, 1.19x, 1.26x), single WSL2 box, library build flags unstated (the libtins autoconf default is -g -O2, so the old 'no -O' caveat was wrong); the DNS test does different work in each library; packet parsing, not an event loop, and libtins/libpcap are not listed baselines.
- Enricher: the TCP-with-options row (1.19x) only counts packets, and PcapPlusPlus's TcpLayer never decodes options (on-demand TLV reader) while libtins' TCP constructor decodes all 6 into a vector (cost over the no-options test: libtins +32 ms, PcapPlusPlus +5 ms); libtins also copies the 742-byte payload into a RawPDU where PcapPlusPlus uses zero-copy views, so the margin is mostly copy avoidance and deferred decoding. Project defaults differ (PcapPlusPlus Release -O3, libtins RelWithDebInfo -O2), actual flags unstated. The record's 'parsing lazy per layer' is wrong: every layer is parsed eagerly with one allocation per layer; only options and DNS rdata are deferred. Issue #2071: master pcap reader 22x regression (1.857 s vs 0.084 s), fixed in PR #2072.

## Caveats and trade-offs

First-party run: the page is on the PcapPlusPlus website and was produced by its maintainers, although the harness (mfontanini/packet-capture-benchmarks, 35 stars, 5 commits, no README or committed results) was written by libtins' author, who added PcapPlusPlus to it in November 2017; the PcapPlusPlus benchmark.cpp in the suite is copied from the PcapPlusPlus repo (Examples/PcapPlusPlus-benchmark). The win over libtins is small (1.06x, 1.19x and 1.26x, derived from page data) on a single virtualized machine (WSL2 on an i7-8700 Windows 10 host), versions PcapPlusPlus v24.09 and libtins v4.5. Timing is the integer-millisecond average of 3 runs over a 500,000-packet generated pcap (payload 742 bytes), so resolution is about 0.5 percent. The DNS test is not identical work: libtins re-parses the UDP RawPDU into a DNS object and materialises query and answer vectors, while PcapPlusPlus walks its already-parsed DnsLayer. PcapPlusPlus is slower than the libpcap loop in all three tests (about 1.6x, 1.6x and 6.7x, derived from page data), but that loop only counts packets without parsing, so it is not a like-for-like baseline. Library build flags are not stated (the earlier note that the libtins benchmark line has no -O flag is only true when --with-libtins-include-path overrides autoconf's -g -O2 default). Neither baseline is in the event-loops-io baseline list (libuv, libevent, epoll, io_uring); PcapPlusPlus is a packet capture and parsing library, so the category fit is weak. The rendered page (pcapplusplus.github.io) was not opened; numbers were read from its MDX source. [retier] Options decoding deferred vs eager (libtins +32 ms, PcapPlusPlus +5 ms over the no-options test); payload copied into RawPDU on the libtins side; every PcapPlusPlus layer is parsed eagerly with one allocation per layer; build defaults differ (Release -O3 vs RelWithDebInfo -O2), flags unstated; master pcap reader 22x regression #2071 fixed in #2072.

Wraps libpcap, Npcap, WinPcap, DPDK, AF_XDP and PF_RING capture engines and parses 60+ protocols into a layer object model; parsing is lazy per layer, packet objects allocate. Public domain (Unlicense) with no patent grant.

## Maintenance

Actively maintained (commits through 2026-10-09, 3.1k stars, 2,698 commits, frequent fuzz-driven fixes) and public domain under the Unlicense, which has no patent grant; the benchmark page is first-party and predates the master-branch pcap reader rewrite, so its numbers describe v24.09.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification B, tier now C.
- **Tier reason:** Every quoted number is in docs/benchmark.mdx of the PcapPlusPlus website repo, a run by PcapPlusPlus's own maintainers with mfontanini/packet-capture-benchmarks (public code: pcapplusplus/benchmark.cpp, libtins/benchmark.cpp, libpcap/benchmark.cpp, benchmark.sh, Makefile.in, configure.ac); g++ 11.4.0 and the i7-8700 are stated but no flags are, and the build flags of the PcapPlusPlus v24.09 and libtins v4.5 libraries (where the parsing happens) are unknown, so not A. The measurement is first-party, not independent, so C rather than B.
- **Verifier notes:** All six times and packets-per-second figures match the MDX constants exactly (500000/0.197 = 2,538,071 etc.). Downgraded B to C because the run is first-party (PcapPlusPlus maintainers) even though the harness is libtins' author's; no independent run including PcapPlusPlus was found (libtins.github.io blocked, one search found nothing). Consider a category override: this is packet parsing, not an event loop, and libtins/libpcap are off the category's baseline list.
- **Fields the verifier corrected:** `last_commit`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-79 (wave 5); enricher w5 pair-034
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/PcapPlusPlus/pcapplusplus.github.io/HEAD/docs/benchmark.mdx>
  - <https://github.com/seladb/PcapPlusPlus>
  - <https://github.com/seladb/PcapPlusPlus/commits/master>
  - <https://github.com/mfontanini/packet-capture-benchmarks>
  - <https://github.com/mfontanini/packet-capture-benchmarks/commits/master>
  - <https://raw.githubusercontent.com/mfontanini/packet-capture-benchmarks/HEAD/Makefile.in>
  - <https://raw.githubusercontent.com/mfontanini/packet-capture-benchmarks/HEAD/benchmark.sh>
  - <https://raw.githubusercontent.com/mfontanini/packet-capture-benchmarks/HEAD/configure.ac>
  - <https://raw.githubusercontent.com/mfontanini/packet-capture-benchmarks/HEAD/libtins/benchmark.cpp>
  - <https://raw.githubusercontent.com/mfontanini/packet-capture-benchmarks/HEAD/pcapplusplus/benchmark.cpp>
  - <https://raw.githubusercontent.com/mfontanini/packet-capture-benchmarks/HEAD/libpcap/benchmark.cpp>
- **Sources the enricher read:**
  - <https://github.com/seladb/PcapPlusPlus>
  - <https://github.com/seladb/PcapPlusPlus/commits/master>
  - <https://github.com/seladb/PcapPlusPlus/issues?q=is%3Aissue+performance>
  - <https://github.com/seladb/PcapPlusPlus/issues/2071>
  - <https://github.com/seladb/PcapPlusPlus/issues/703>
  - <https://github.com/seladb/PcapPlusPlus/security>
  - <https://raw.githubusercontent.com/seladb/PcapPlusPlus/HEAD/README.md>
  - <https://raw.githubusercontent.com/seladb/PcapPlusPlus/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/seladb/PcapPlusPlus/HEAD/Packet++/header/Packet.h>
  - <https://raw.githubusercontent.com/seladb/PcapPlusPlus/HEAD/Packet++/src/Packet.cpp>
  - <https://raw.githubusercontent.com/seladb/PcapPlusPlus/HEAD/Packet++/header/TcpLayer.h>
  - <https://raw.githubusercontent.com/seladb/PcapPlusPlus/HEAD/Packet++/src/TcpLayer.cpp>
  - <https://raw.githubusercontent.com/seladb/PcapPlusPlus/HEAD/Packet++/src/DnsLayer.cpp>
  - <https://raw.githubusercontent.com/seladb/PcapPlusPlus/HEAD/Packet++/src/DnsResource.cpp>
  - <https://raw.githubusercontent.com/seladb/PcapPlusPlus/HEAD/Packet++/src/UdpLayer.cpp>
  - <https://raw.githubusercontent.com/seladb/PcapPlusPlus/HEAD/Packet++/src/IPv4Layer.cpp>
  - <https://raw.githubusercontent.com/seladb/PcapPlusPlus/HEAD/Packet++/src/EthLayer.cpp>
  - <https://raw.githubusercontent.com/seladb/PcapPlusPlus/HEAD/Packet++/src/RawPacket.cpp>
  - <https://raw.githubusercontent.com/seladb/PcapPlusPlus/HEAD/Pcap++/src/PcapFileDevice.cpp>
  - <https://raw.githubusercontent.com/seladb/PcapPlusPlus/HEAD/Examples/PcapPlusPlus-benchmark/benchmark.cpp>
  - <https://raw.githubusercontent.com/seladb/PcapPlusPlus/HEAD/Examples/PcapPlusPlus-benchmark/benchmark-google.cpp>
  - <https://raw.githubusercontent.com/seladb/PcapPlusPlus/v24.09/Pcap++/src/PcapFileDevice.cpp>
  - <https://raw.githubusercontent.com/seladb/PcapPlusPlus/v24.09/Packet++/src/TcpLayer.cpp>
  - <https://raw.githubusercontent.com/seladb/PcapPlusPlus/v24.09/CMakeLists.txt>
  - <https://raw.githubusercontent.com/PcapPlusPlus/pcapplusplus.github.io/HEAD/docs/benchmark.mdx>
  - <https://raw.githubusercontent.com/mfontanini/packet-capture-benchmarks/HEAD/pcapplusplus/benchmark.cpp>
  - <https://raw.githubusercontent.com/mfontanini/packet-capture-benchmarks/HEAD/libtins/benchmark.cpp>
  - <https://raw.githubusercontent.com/mfontanini/packet-capture-benchmarks/HEAD/libpcap/benchmark.cpp>
  - <https://raw.githubusercontent.com/mfontanini/packet-capture-benchmarks/HEAD/benchmark.sh>
  - <https://raw.githubusercontent.com/mfontanini/packet-capture-benchmarks/HEAD/Makefile.in>
  - <https://raw.githubusercontent.com/mfontanini/packet-capture-benchmarks/HEAD/configure.ac>
  - <https://raw.githubusercontent.com/mfontanini/packet-capture-benchmarks/HEAD/pcap_generator/generator.cpp>
  - <https://raw.githubusercontent.com/mfontanini/libtins/HEAD/src/tcp.cpp>
  - <https://raw.githubusercontent.com/mfontanini/libtins/HEAD/src/rawpdu.cpp>
  - <https://raw.githubusercontent.com/mfontanini/libtins/HEAD/src/sniffer.cpp>
  - <https://raw.githubusercontent.com/mfontanini/libtins/HEAD/src/udp.cpp>
  - <https://raw.githubusercontent.com/mfontanini/libtins/v4.5/CMakeLists.txt>
  - <https://github.com/mfontanini/libtins/commits/master>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/seladb/pcapplusplus`) · [data/wave5/enrich/raw/github_com_seladb_pcapplusplus.json](../../../data/wave5/enrich/raw/github_com_seladb_pcapplusplus.json) (enrichment confidence 0.8)

</details>
