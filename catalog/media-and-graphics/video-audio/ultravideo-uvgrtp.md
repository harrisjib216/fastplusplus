# uvgRTP

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Video and audio](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-2-Clause` · 🟢 active

> C++ RTP/SRTP/ZRTP library with built-in H.264/HEVC/VVC packetization; its authors report 4.4x FFmpeg's RTP goodput.

| | |
|---|---|
| **Beats** | FFmpeg (libavformat RTP) and Live555 as RTP senders/receivers for HEVC video |
| **Claimed result** | Paper abstract (search snippet only, IEEE MMSP 2020): on an Intel Core i7-4770 uvgRTP streams HEVC at 5.0 Gb/s over a local 10 Gb/s network, with 4.4 times the peak goodput and 92.1% lower latency than FFmpeg, and over double the goodput and 82.3% lower latency than Live555. |
| **Workload** | RTP streaming of 4K HEVC video over a 10 Gbps LAN: peak goodput (throughput without protocol overhead) and round-trip frame latency, measured with the public rtp-benchmarks framework. |
| **Metric** | throughput |
| **Hardware** | Core i7-4770 and AMD Threadripper 2990WX connected by 10 Gbps LAN (rtp-benchmarks README); the paper reports the i7-4770 result |
| **Compiler and flags** | rtp-benchmarks Makefile builds the sender/receiver harnesses with g++ -Wall -Wextra -O2 -std=c++17 -g and links the installed uvgRTP, libavformat/libavcodec and Live555; the library versions and their build flags used for the paper are not stated in the repository. |
| **Adoption** | 443 stars |
| **Last commit** | 2026-07-28 |
| **Links** | [repository](https://github.com/ultravideo/uvgRTP) · [benchmark](https://github.com/ultravideo/rtp-benchmarks) |

## Verdict

The only numbers are from the uvgRTP authors' MMSP 2020 abstract, seen as a search snippet: sending a Kvazaar-encoded 4K HEVC file from a Core i7-4770 over 10 GbE, uvgRTP reached 5.0 Gb/s, 4.4x FFmpeg libavformat's peak goodput with 92.1% lower round-trip latency, and over 2x Live555's goodput with 82.3% lower latency. The rtp-benchmarks harness (g++ -O2 -g) is public but has no result files, and the library versions and build flags are not stated. Reading that harness shows that FFmpeg's latency path was measured with its default HEVC parser buffering and with the intended low-latency options silently unset (see measurement_notes), so the latency gap mostly reflects configuration, not RTP stack speed.

## Use it when

- Streaming pre-encoded H.264, HEVC or VVC (or V3C atlas) bitstreams between endpoints you control, with your own signalling.
- 4K/8K or high-frame-rate video over a 10 GbE LAN, where per-packet CPU cost and kernel buffering limit the frame rate (larger socket buffers and RCE_PACE_FRAGMENT_SENDING are documented for bursts).
- Low-latency links where the receiver should get each NAL unit through a callback without demuxer or parser buffering.
- Encrypted point-to-point media (SRTP with ZRTP or user-managed keys) without pulling in a WebRTC stack.
- C++17 projects on Linux or Windows that need a BSD-2-Clause RTP stack, with an ABI-stable C-style Core API in shared builds.

## Skip it when

- You need RTSP/SDP signalling, container demuxing or decoding: FFmpeg, Live555 or GStreamer cover the whole pipeline, and uvgRTP covers only the RTP transport.
- WebRTC interop (ICE, DTLS-SRTP, congestion control): not provided. RTCP report blocks are exposed, but congestion control is left to the application.
- Strict RFC interop with third-party receivers: open issues report that the H26x marker bit is set per NAL unit rather than per access unit (#261) and that the RTP timestamp is incremented incorrectly by default (#246); the 4.0.0 release notes list both as known issues.
- Heavy RTCP use: open issues report a crash in rtcp::update_session_statistics (#235, labelled critical) and a segfault during RTCP teardown (#262).
- macOS (community-supported only), 32-bit targets (a 64-bit compiler is required), or access units that hold several large NAL units needing fragmentation (the docs warn this may lead to undefined behaviour).

## How it is fast

The NAL start-code lookup scans 8 bytes at a time with the SWAR 'has a zero byte' bit trick (haszero64/haszero32) instead of testing byte by byte. On the send side, RTP and FU headers sit in small separate buffers and are gathered with the caller's payload through iovecs into sendmmsg(2) (WSASendTo on Windows), so frame data is not copied unless RTP_COPY is set; RCE_SYSTEM_CALL_CLUSTERING batches up to 1024 packets per sendmmsg call. On the receive side a dedicated receiver thread (it requests SCHED_FIFO priority on Linux) fills a preallocated ring buffer and a separate processor thread reassembles fragments into frames allocated with the start code already in place. Each NAL unit reaches the callback as soon as it is complete, with no access-unit parser holding it back.

## Compared with alternatives

The only transport sibling is rustrtc (a Rust WebRTC stack measured against webrtc-rs and pion). Pick uvgRTP for plain RTP/SRTP in C++ with native HEVC/VVC/AVC packetization and no ICE/DTLS, and rustrtc when browsers must connect. Codec siblings such as Kvazaar (same group; the benchmark files are Kvazaar-encoded), dav1d or VVenC are complementary: uvgRTP carries their output.

## Integration

| | |
|---|---|
| **Form** | static lib (default; full Extended C++ API) or shared lib (UVGRTP_BUILD_SHARED, Core API only) |
| **Dependencies** | pthreads; Crypto++ optional (auto-detected with __has_include) for SRTP/ZRTP |
| **Minimum toolchain** | C++17 (CMAKE_CXX_STANDARD 17), CMake 3.14+, 64-bit GCC, MinGW or MSVC |
| **Platforms** | Linux and Windows (x86-64 builds documented); macOS community-supported |
| **Thread safety** | not documented; each reception flow runs its own receiver and processor threads, and receive hooks are called on library threads |
| **Drop-in for the baseline** | no |

## Gotchas

- push_frame() runs start-code lookup by default. Pass RTP_NO_H26X_SCL if your encoder hands over bare NAL units. The receiver prepends start codes unless RCE_H26X_DO_NOT_PREPEND_SC is set, and frames arrive per NAL unit, not per access unit.
- push_frame() does not take ownership and works in place: SRTP in-place encryption is the default, so the caller's buffer is modified unless RTP_COPY is passed. Every received frame must be released with uvgrtp::frame::dealloc_frame().
- Defaults are 4 MB socket and ring buffers. For bursty 4K60+ traffic the docs suggest 40-80 MB buffers and fragment pacing (RCE_PACE_FRAGMENT_SENDING, which sleeps inside push_frame), and the benchmark harness itself sets 40 MB. sendmmsg clustering is opt-in and the docs warn it can raise frame loss at high frame rates.
- Use 4.0.1 or later: that release adds protection against out-of-bounds memory access on invalid headers (extension header length checks), and 4.0.0 added checks for too-small payloads.

## Known shortcomings

- Downgraded to C: the only numbers (4.4x goodput, 92.1% lower latency vs FFmpeg and Live555) come from a search snippet of the authors' own MMSP 2020 abstract; the paper is blocked (IEEE, tuni.fi, ultravideo.fi) with no copy on GitHub. The rtp-benchmarks repo has harness code (-O2 -g) but no results, and its README says the FFmpeg and Live555 code is untested lately.
- The 92.1% lower-latency claim rests on a mis-set baseline: rtp-benchmarks (7151dba of 2020-06-10, before the paper, and HEAD) passes NULL to av_dict_set for 'nobuffer' and 'flush_packets', which deletes the keys, so FFmpeg's low-latency options were never applied, and FFmpeg's rtpdec_hevc uses AVSTREAM_PARSE_FULL so the HEVC parser holds each frame until the next access unit (about 33 ms per hop at the hard-coded 30 fps, two hops). FFmpeg latency is also matched FIFO per packet (598 against 602 counts) with an unlocked deque and unordered_map race and a duplicate-size skip that desyncs the file walk; both libraries floor latency to whole milliseconds; the 2020 uvgRTP used RCE_SYSTEM_CALL_DISPATCHER, since removed; HEAD-only harness bugs include a tid = thread_num/2 counter collision, a 604 against 602 frame mismatch and the SRTP salt written into the key. Transport only (no RTSP/SDP, ICE or congestion control); open issues #261 (marker bit), #246 (timestamp), #235 and #262 (RTCP crashes); use 4.0.1 or later for the out-of-bounds fix.

## Caveats and trade-offs

Numbers come only from a search-result snippet of the MMSP 2020 abstract (Altonen, Räsänen, Laitinen, Viitanen, Vanne); the paper is first-party (the uvgRTP authors) and could not be opened here (IEEE Xplore, researchportal.tuni.fi and ultravideo.fi are blocked), so the percentages, test configuration and library versions were not checked against its text. The rtp-benchmarks repository carries the harness code and the hardware (Core i7-4770 and Threadripper 2990WX over a 10 Gbps LAN) but no result files or CSVs, and its README says the FFmpeg and Live555 implementations have not been tested in a while and may not work out of the box, so the comparison is not currently reproducible as published. Harness flags are -O2 -g; library build flags are not stated. Results are from 2020 library versions (uvgRTP is now at 4.0.1). The workload is RTP packetization and transport of a pre-encoded HEVC file, not encoding or decoding.

RTP/SRTP/ZRTP library for HEVC, VVC, AVC and Opus transport; benchmarks cover RTP transport only, not codec speed. Linux benchmark scripts.

## Maintenance

Actively maintained (Release 4.0.1 on 2026-07-28, after the ABI-safe 4.0.0 in May 2026) and BSD-2-Clause, so it is copyable. The benchmark repository's last commit is 2024-01-23, and its README says the FFmpeg and Live555 harnesses may no longer work out of the box.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification B, tier now C.
- **Tier reason:** The public rtp-benchmarks framework (uvgrtp/, ffmpeg/, live555/ senders and receivers, benchmark.pl, parse.pl) does pit uvgRTP against FFmpeg libavformat and Live555, but it publishes no results; the 4.4x goodput and 92.1% lower latency figures exist only in the MMSP 2020 abstract as seen in a search snippet, written by the uvgRTP authors themselves, and the paper (IEEE Xplore, Tampere research portal, ultravideo.fi) could not be opened. Per the snippet-only rule this caps at C.
- **Verifier notes:** Real, maintained project (BSD-2-Clause, 443 stars, last commit 2026-07-28 'Release 4.0.1') with a genuine public comparison harness, but the only numbers are a blocked first-party paper abstract seen via search snippet, so B is not supportable; could move to B only if a copy of the paper (or later ICME 2021 / ISM 2021 papers) becomes readable and confirms the figures.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/ultravideo/uvgRTP>
  - <https://github.com/ultravideo/uvgRTP/commits/master>
  - <https://raw.githubusercontent.com/ultravideo/uvgRTP/HEAD/README.md>
  - <https://raw.githubusercontent.com/ultravideo/uvgRTP/HEAD/docs/README.md>
  - <https://github.com/ultravideo/rtp-benchmarks>
  - <https://raw.githubusercontent.com/ultravideo/rtp-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/ultravideo/rtp-benchmarks/HEAD/Makefile>
- **Sources the enricher read:**
  - <https://github.com/ultravideo/uvgRTP>
  - <https://raw.githubusercontent.com/ultravideo/uvgRTP/HEAD/README.md>
  - <https://raw.githubusercontent.com/ultravideo/uvgRTP/HEAD/docs/README.md>
  - <https://raw.githubusercontent.com/ultravideo/uvgRTP/HEAD/BUILDING.md>
  - <https://raw.githubusercontent.com/ultravideo/uvgRTP/HEAD/USAGE.md>
  - <https://raw.githubusercontent.com/ultravideo/uvgRTP/HEAD/CMakeLists.txt>
  - <https://github.com/ultravideo/uvgRTP/tree/master/src>
  - <https://raw.githubusercontent.com/ultravideo/uvgRTP/HEAD/src/formats/h26x.cc>
  - <https://raw.githubusercontent.com/ultravideo/uvgRTP/HEAD/src/reception_flow.cc>
  - <https://raw.githubusercontent.com/ultravideo/uvgRTP/HEAD/src/socket.cc>
  - <https://raw.githubusercontent.com/ultravideo/uvgRTP/HEAD/src/frame_queue.cc>
  - <https://github.com/ultravideo/uvgRTP/issues>
  - <https://github.com/ultravideo/uvgRTP/releases>
  - <https://github.com/ultravideo/uvgRTP/releases/tag/v4.0.1>
  - <https://github.com/ultravideo/uvgRTP/commits/master>
  - <https://github.com/ultravideo/rtp-benchmarks>
  - <https://github.com/ultravideo/rtp-benchmarks/tree/master/uvgrtp>
  - <https://github.com/ultravideo/rtp-benchmarks/commits/master>
  - <https://github.com/ultravideo/rtp-benchmarks/commits/master/ffmpeg/latency_sender.cc>
  - <https://raw.githubusercontent.com/ultravideo/rtp-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/ultravideo/rtp-benchmarks/HEAD/Makefile>
  - <https://raw.githubusercontent.com/ultravideo/rtp-benchmarks/HEAD/benchmark.pl>
  - <https://raw.githubusercontent.com/ultravideo/rtp-benchmarks/HEAD/parse.pl>
  - <https://raw.githubusercontent.com/ultravideo/rtp-benchmarks/HEAD/uvgrtp/sender.cc>
  - <https://raw.githubusercontent.com/ultravideo/rtp-benchmarks/HEAD/uvgrtp/receiver.cc>
  - <https://raw.githubusercontent.com/ultravideo/rtp-benchmarks/HEAD/uvgrtp/uvgrtp_util.hh>
  - <https://raw.githubusercontent.com/ultravideo/rtp-benchmarks/HEAD/uvgrtp/latency_sender.cc>
  - <https://raw.githubusercontent.com/ultravideo/rtp-benchmarks/HEAD/uvgrtp/latency_receiver.cc>
  - <https://raw.githubusercontent.com/ultravideo/rtp-benchmarks/HEAD/ffmpeg/sender.cc>
  - <https://raw.githubusercontent.com/ultravideo/rtp-benchmarks/HEAD/ffmpeg/receiver.cc>
  - <https://raw.githubusercontent.com/ultravideo/rtp-benchmarks/HEAD/ffmpeg/latency_sender.cc>
  - <https://raw.githubusercontent.com/ultravideo/rtp-benchmarks/HEAD/ffmpeg/latency_receiver.cc>
  - <https://raw.githubusercontent.com/ultravideo/rtp-benchmarks/HEAD/live555/sender.cc>
  - <https://raw.githubusercontent.com/ultravideo/rtp-benchmarks/HEAD/live555/receiver.cc>
  - <https://raw.githubusercontent.com/ultravideo/rtp-benchmarks/HEAD/util/util.cc>
  - <https://raw.githubusercontent.com/ultravideo/rtp-benchmarks/HEAD/util/util.hh>
  - <https://raw.githubusercontent.com/ultravideo/rtp-benchmarks/7151dba/README.md>
  - <https://raw.githubusercontent.com/ultravideo/rtp-benchmarks/7151dba/uvgrtp/sender.cc>
  - <https://raw.githubusercontent.com/ultravideo/rtp-benchmarks/7151dba/uvgrtp/receiver.cc>
  - <https://raw.githubusercontent.com/ultravideo/rtp-benchmarks/7151dba/uvgrtp/latency_sender.cc>
  - <https://raw.githubusercontent.com/ultravideo/rtp-benchmarks/7151dba/ffmpeg/sender.cc>
  - <https://raw.githubusercontent.com/ultravideo/rtp-benchmarks/7151dba/ffmpeg/receiver.cc>
  - <https://raw.githubusercontent.com/ultravideo/rtp-benchmarks/7151dba/ffmpeg/latency_sender.cc>
  - <https://raw.githubusercontent.com/FFmpeg/FFmpeg/master/libavformat/rtpdec_hevc.c>
  - <https://raw.githubusercontent.com/FFmpeg/FFmpeg/master/libavcodec/hevc/parser.c>
  - WebSearch snippet: "Open-Source RTP Library for High-Speed 4K HEVC Video Streaming" (ieeexplore.ieee.org/document/9287162, ultravideo.fi/uvgrtp.html; pages themselves not opened)
  - https://rc.signalprocessingsociety.org/workshops/mmsp-2020/mmsp20vid113 (EGRESS_BLOCKED)
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/ultravideo/uvgrtp`) · [data/wave10/enrich/raw/github_com_ultravideo_uvgrtp.json](../../../data/wave10/enrich/raw/github_com_ultravideo_uvgrtp.json) (enrichment confidence 0.75)

</details>
