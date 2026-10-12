# LibTorrent (rakshasa)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [Event loops and async I/O](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `GPL-2.0` · 🟢 active

> C++ BitTorrent engine behind rTorrent that writes mmap'ed file pages straight to sockets; old first-party claim of 3x the mainline client's seeding speed.

| | |
|---|---|
| **Beats** | official BitTorrent client (the original mainline client; not named more exactly in the claim) |
| **Claimed result** | 'On high-bandwidth connections it is able to seed at 3 times the speed of the official client.' (old first-party project description, verbatim in the SlackBuilds 14.1 libtorrent README for libtorrent 0.13.6; no methodology) |
| **Workload** | Seeding speed on high-bandwidth connections; no further workload description. |
| **Metric** | throughput |
| **Adoption** | 1k stars; the engine of the rTorrent client |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/rakshasa/libtorrent) · [benchmark](https://github.com/SlackBuildsOrg/slackbuilds/blob/14.1/libraries/libtorrent/README) |

## Verdict

The only claim is the project's old description sentence that it 'is able to seed at 3 times the speed of the official client' on high-bandwidth connections, preserved in distro package descriptions (SlackBuilds 14.1 for 0.13.6, openSUSE, OpenWrt, Salix) but in neither the current nor the v0.13.0 README. No benchmark code, hardware, compiler, client versions, torrent size or peer count exists anywhere, and the code it described has since been reworked into the multi-threaded 0.16.x series.

## Use it when

- You are building or extending a Linux/BSD seedbox, headless client or rTorrent frontend and want the engine rTorrent already ships on.
- Unencrypted seeding of many torrents from fast local disks where the page cache can hold the hot chunks; that is the case the mmap-to-socket path targets.
- 64-bit hosts with large address space, so many chunks can stay mapped (the default address-space budget is 32,768 MB on 64-bit builds).
- GPL-2.0 (with the per-file OpenSSL linking exception) is acceptable for your client.

## Skip it when

- You want a measured speed advantage: the only number is an old first-party 3x seeding sentence with no benchmark, no methodology and a baseline (the mainline BitTorrent client of the mid-2000s) nobody uses today.
- You need Windows, uTP (issue #33 open since 2013) or full BitTorrent v2/BEP52 support (issue #213 open since 2020).
- Storage that can fill up, be truncated or vanish under you (network mounts, full disks): writes and reads go through mmap, so these surface as SIGBUS rather than an I/O error (open issues #825 and #645).
- Encrypted peer connections dominate: the encrypt path (up_chunk_encrypt) copies each piece into an EncryptBuffer with Chunk::to_buffer and encrypts it there, so the direct page-to-socket write no longer applies.
- You need a documented, stable library API for a non-rTorrent client; arvidn's libtorrent-rasterbar (a different project with a similar name) is the usual choice there.

## How it is fast

Torrent data is accessed through mmap'ed file chunks: on upload, PeerConnectionBase::up_chunk walks a ChunkIterator over the mapped pages and calls write() on the socket directly from them, so there is no user-space read buffer or pread copy (it is not sendfile; the kernel still copies into socket buffers). Before uploading a chunk it can prefetch it with madvise(MADV_WILLNEED) or by touching each 4 KiB page, but only when the peer's upload rate exceeds preload_required_rate per MB and the chunk was not preloaded in the last 60 s; mincore() feeds instrumentation of page-cache hits. Downloads recv() directly into writable mapped chunks, and dirty chunks are queued and synced later by the disk thread. Socket readiness comes from an epoll (Linux) or kqueue (BSD, macOS) backend.

## Compared with alternatives

None of the event-loops-io siblings (libev, Asio's io_uring backend, PhotonLibOS, Seastar) is a BitTorrent engine, so pick libtorrent only when you need BitTorrent itself; if you only want a faster event loop or I/O backend, those siblings carry the measured evidence and this entry does not.

## Integration

| | |
|---|---|
| **Form** | shared lib (autotools; configure.ac sets disable-static by default) |
| **Dependencies** | libcurl, zlib, pthreads, OpenSSL (configure check TORRENT_CHECK_OPENSSL); cppunit only for the unit tests |
| **Minimum toolchain** | C++20 (configure uses AX_CXX_COMPILE_STDCXX(20, noext, mandatory)); CI includes gcc 14 on BSD jobs; autoconf/automake/libtool to bootstrap |
| **Platforms** | Unix-like only: configure refuses to build without epoll or kqueue; CI runs Ubuntu 22.04/24.04, macOS, FreeBSD, NetBSD, OpenBSD, DragonFlyBSD and OmniOS; open alignment issue on ARM (#462); no Windows |
| **Thread safety** | Not documented in detail; the library runs its own main, net, disk and tracker threads and expects client calls from the main thread after initialize_main_thread() (issue #954 asks which thread owns the HTTP setters) |
| **Drop-in for the baseline** | no |

## Gotchas

- SIGBUS is part of the failure model: a kernel-invalidated mapping (disk full, file truncated or removed) kills the process unless the client handles SIGBUS; #645 is a SIGBUS abort in Chunk::to_buffer during an encrypted upload, and #825 tracks recv() into mapped memory on a full disk.
- The address space reserved for mapped chunks defaults to 1,024 MB on 32-bit builds (32,768 MB on 64-bit), which caps how much torrent data can be mapped at once on small systems; change it with --with-address-space.
- The catalog record's notes are partly stale: the current tree has epoll and kqueue backends (no select backend) and requires C++20; the sigc++-era API mentioned in the record belongs to old releases.
- Name clash: 'libtorrent' also names arvidn/libtorrent (libtorrent-rasterbar, used by qBittorrent and Deluge); packages, headers and APIs are unrelated.

## Known shortcomings

- Tier C: the '3 times the speed of the official client' line is first-party marketing from the SlackBuilds 14.1 README (libtorrent 0.13.6; GitHub mirror SlackBuildsOrg/slackbuilds, slackbuilds.org blocked) with no methodology and a vague baseline, absent from the current README; the event-loops-io category is a stretch for a BitTorrent engine.
- Enricher: no harness exists; the 3x claim is a mid-2000s package-description sentence against the mainline client. Real technique: write() straight from mmap'ed chunk pages plus madvise WILLNEED or page-touch preload gated by upload rate; encrypted peers skip that path (up_chunk_encrypt copies into EncryptBuffer); SIGBUS on a full disk or truncated file (open issues #825, #645). Current tree has epoll and kqueue backends (no select) and needs C++20; missing uTP (#33) and BEP52 v2 (#213); open ARM alignment issue #462. event-loops-io fit is weak.

## Caveats and trade-offs

The 3x sentence was verified verbatim in the SlackBuilds 14.1 package README (GitHub mirror SlackBuildsOrg/slackbuilds, libtorrent 0.13.6). slackbuilds.org itself is egress-blocked, and the 14.0 path does not exist in the mirror. The sentence comes from the project's old description and is in neither the current README nor the v0.13.0 README. The current README keeps only the design point ('transferring directly from file pages to the network stack') and 'high performance' with no numbers. The baseline 'official client' is vague (the original mainline BitTorrent client of that era). No methodology, hardware, torrent size, peer count or versions are given, so the claim is old, first-party and unreproducible, and it predates the heavily reworked current 0.16.x code. Off-category for event-loops-io: this is a BitTorrent engine, and the baseline is a BitTorrent client, not libuv, libevent or epoll. GPL-2.0 is copyleft. [retier] No benchmark exists; the 3x line comes from the SlackBuilds 14.1 README (libtorrent 0.13.6) and is absent from the current README. Technique: write() from mmap'ed chunks with madvise preload; encrypted peers bypass it; SIGBUS on full disk or truncated files (#825, #645). Needs C++20; no uTP or BEP52 v2; BitTorrent engine, weak fit for event-loops-io.

C++ for \*nix only (epoll and select polling); transfers directly from file pages (mmap) to the network stack; GPL with an OpenSSL linking exception, sha_fast code triple-licensed MPL/LGPL/GPL; API is built for rTorrent and uses sigc++ signals in older releases.

## Maintenance

Very active (release 0.16.25 on 2026-10-05, commits through 2026-10-11) and copyable under GPL-2.0 with an OpenSSL exception, but the speed claim is decades-old marketing with no harness, and the category fit is a stretch since this is a BitTorrent engine rather than an event loop.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now D.
- **Tier reason:** The only number is a single first-party sentence, 'On high-bandwidth connections it is able to seed at 3 times the speed of the official client', from the project's old description. It comes with no methodology, hardware, versions, torrent size or peer count, so it is first-party numbers without methodology (C). It is not in the current README or the v0.13.0 README.
- **Retiered** C to D: The only speed statement is a mid-2000s package-description sentence ('seed at 3 times the speed of the official client') with no harness, numbers, methodology or named version; directional only.
- **Verifier notes:** Real, active project (last commit 2026-10-06, release 0.16.25 on 2026-10-05; GPL-2.0, about 1k stars, not a fork or archived; metadata correct). The 3x claim was confirmed verbatim in a reachable SlackBuilds mirror, so benchmark_url now points there. Shortcomings: a decades-old first-party marketing sentence with no methodology, a vague baseline, and a category fit (event-loops-io) that is a stretch.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-76 (wave 5); enricher (wave 5)
- **Pages the verifier opened:**
  - <https://github.com/rakshasa/libtorrent>
  - <https://github.com/rakshasa/libtorrent/commits>
  - <https://raw.githubusercontent.com/rakshasa/libtorrent/HEAD/README.md>
  - <https://raw.githubusercontent.com/rakshasa/libtorrent/v0.13.0/README>
  - <https://raw.githubusercontent.com/SlackBuildsOrg/slackbuilds/14.1/libraries/libtorrent/README>
  - <https://raw.githubusercontent.com/SlackBuildsOrg/slackbuilds/14.1/libraries/libtorrent/libtorrent.info>
  - <https://github.com/SlackBuildsOrg/slackbuilds/blob/14.1/libraries/libtorrent/README>
- **Sources the enricher read:**
  - <https://github.com/rakshasa/libtorrent>
  - <https://github.com/rakshasa/libtorrent/commits>
  - <https://github.com/rakshasa/libtorrent/issues>
  - <https://github.com/rakshasa/libtorrent/issues/825>
  - <https://github.com/rakshasa/libtorrent/issues/645>
  - <https://github.com/rakshasa/libtorrent/wiki>
  - <https://github.com/rakshasa/libtorrent/tree/master/src/data>
  - <https://github.com/rakshasa/libtorrent/tree/master/src/torrent>
  - <https://github.com/rakshasa/libtorrent/tree/master/src/torrent/net>
  - <https://github.com/rakshasa/libtorrent/tree/master/.github/workflows>
  - <https://raw.githubusercontent.com/rakshasa/libtorrent/HEAD/README.md>
  - <https://raw.githubusercontent.com/rakshasa/libtorrent/HEAD/configure.ac>
  - <https://raw.githubusercontent.com/rakshasa/libtorrent/HEAD/COPYING>
  - <https://raw.githubusercontent.com/rakshasa/libtorrent/HEAD/scripts/checks.m4>
  - <https://raw.githubusercontent.com/rakshasa/libtorrent/HEAD/scripts/common.m4>
  - <https://raw.githubusercontent.com/rakshasa/libtorrent/HEAD/.github/workflows/unit-tests.yml>
  - <https://raw.githubusercontent.com/rakshasa/libtorrent/HEAD/src/data/memory_chunk.cc>
  - <https://raw.githubusercontent.com/rakshasa/libtorrent/HEAD/src/data/chunk.cc>
  - <https://raw.githubusercontent.com/rakshasa/libtorrent/HEAD/src/data/chunk_list.cc>
  - <https://raw.githubusercontent.com/rakshasa/libtorrent/HEAD/src/data/socket_file.cc>
  - <https://raw.githubusercontent.com/rakshasa/libtorrent/HEAD/src/data/thread_disk.cc>
  - <https://raw.githubusercontent.com/rakshasa/libtorrent/HEAD/src/protocol/peer_connection_base.cc>
  - <https://raw.githubusercontent.com/rakshasa/libtorrent/HEAD/src/protocol/peer_connection_leech.cc>
  - <https://raw.githubusercontent.com/rakshasa/libtorrent/HEAD/src/net/socket_stream.cc>
  - <https://raw.githubusercontent.com/rakshasa/libtorrent/HEAD/src/net/thread_net.cc>
  - <https://raw.githubusercontent.com/rakshasa/libtorrent/HEAD/src/torrent/torrent.h>
  - <https://raw.githubusercontent.com/rakshasa/libtorrent/HEAD/src/torrent/torrent.cc>
  - <https://raw.githubusercontent.com/rakshasa/libtorrent/HEAD/src/torrent/system/poll.h>
  - <https://raw.githubusercontent.com/rakshasa/libtorrent/HEAD/src/torrent/system/poll_epoll.cc>
  - <https://raw.githubusercontent.com/rakshasa/libtorrent/HEAD/src/torrent/system/poll_kqueue.cc>
  - <https://raw.githubusercontent.com/SlackBuildsOrg/slackbuilds/14.1/libraries/libtorrent/README>
  - WebSearch: "seed at 3 times the speed of the official client" libtorrent rakshasa (result listings from mankier.com, git.openwrt.org, download.salixos.org, build.openbuildservice.org)
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/rakshasa/libtorrent`) · [data/wave5/enrich/raw/github_com_rakshasa_libtorrent.json](../../../data/wave5/enrich/raw/github_com_rakshasa_libtorrent.json) (enrichment confidence 0.6)

</details>
