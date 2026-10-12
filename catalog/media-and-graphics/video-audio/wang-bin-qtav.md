# QtAV

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Video and audio](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `LGPL-2.1 (library); the player example is GPL-3.0` · 🟡 stale

> Qt plus FFmpeg playback library with hardware decoding and GPU YUV rendering; one author anecdote claims 10% less CPU than VLC.

| | |
|---|---|
| **Beats** | VLC media player (CPU usage on Android, 10-bit H.264 playback) |
| **Claimed result** | About 10% less CPU usage than VLC for a 10-bit H.264 video on an HTC Butterfly S (snippet of a forum post, not opened). The repo wiki page 'The Most Efficient VDA Decoder on OSX' also says 'The performance is the best now. Better than any other players.' with no numbers. |
| **Workload** | Playback of a 10-bit H.264 video on an HTC Butterfly S phone, CPU usage compared with VLC. |
| **Metric** | other (CPU usage during playback; claimed lower) |
| **Hardware** | HTC Butterfly S (Android phone), per search snippet; CPU model not stated |
| **Adoption** | 4.3k stars; listed on the FFmpeg projects page per its README |
| **Last commit** | 2025-08-15 |
| **Links** | [repository](https://github.com/wang-bin/QtAV) · [benchmark](https://forum.qt.io/post/21312) |

## Verdict

The only number is the author's own 2014 Qt-forum report that QtAV used about 10% less CPU than VLC playing a 10-bit H.264 file on an HTC Butterfly S phone, with no VLC version, decoder path, video, build or methodology, read from search snippets because the forum is unreachable. The wiki's claims ('better than any other players' for VDA, CUDA DirectCopy 'faster than potplayer, lavfilters+mpc') carry no numbers.

## Use it when

- Maintaining an existing Qt 5 application that already embeds QtAV and runs against FFmpeg 4.x or older
- Qt 5 desktop or embedded players that need hardware decode with zero-copy OpenGL rendering on VA-API, VideoToolbox, DXVA or CUDA
- Rendering 10-bit (Hi10P) video through OpenGL ES2 shaders on Qt 5 targets
- Studying a compact, LGPL reference for GPU interop and SSE4.1 USWC frame readback inside a Qt pipeline

## Skip it when

- New projects: the author states he no longer develops QtAV; the last release is 1.13.0 (2019-07-11) and 2025 commits are a contributor's Vulkan renderer only
- FFmpeg 5 or newer: issue #1377 (open) reports removed APIs (av_bitstream_filter_\*, const AVCodec\*) break the build, and a community patch built but crashed after a few frames
- Qt 6: issue #1406 (open, no maintainer reply) reports QtAV does not build with Qt 6.2; the CMake build looks for Qt5 only
- When you need measured performance guarantees: the only number is a 2014 single-phone forum anecdote, and a user report says VLC plays full-HD more smoothly
- Closed-source static linking without LGPL compliance work: the library is LGPL-2.1, the player example GPL-3.0, and FFmpeg's licence applies on top

## How it is fast

The claimed savings come from keeping decoded frames on the GPU: zero-copy interop renders hardware-decoded surfaces directly (VDA via IOSurface with NV12 into GL_TEXTURE_RECTANGLE, VA-API via EGL dma-buf or GLX, DXVA and CUDA interop), and YUV-to-RGB conversion runs in OpenGL/ES2 shaders, including 16-bit textures for 10-bit (Hi10P) video. When frames must come back to system memory, an 'OptimizedCopy' path copies from write-combined GPU memory with SSE4.1 streaming loads (_mm_stream_load_si128 through a 4 KB cache block, CopyFrame_SSE4.cpp), with an SSE2 fallback. The 10-bit VLC anecdote most likely reflects shader-based 10-bit rendering versus a CPU conversion in VLC at the time, but the source does not say (inference).

## Compared with alternatives

None of the video-audio siblings is a player framework: dav1d, edge264, rivet-h26x and vvdec are decoders and GStreamer is a general pipeline framework; pick QtAV only when you need a ready Qt/QML playback widget and can stay on Qt 5 with FFmpeg 4.x, otherwise use GStreamer or an FFmpeg-based decoder directly.

## Integration

| | |
|---|---|
| **Form** | shared lib (QtAV, QtAVWidgets) plus QML plugin |
| **Dependencies** | Qt 4.8 or Qt 5 (CMake build: Qt 5 only), FFmpeg 1.0 to 4.x or Libav 9+ (libavcodec, libavformat, libavutil, libswscale, libswresample or libavresample), optional OpenAL, libass, VA-API, CUDA, Vulkan |
| **Minimum toolchain** | Not stated; CMake 2.8.11+ or qmake, compiler that builds Qt 5; no C++ standard is pinned in CMakeLists.txt |
| **Platforms** | Windows (DXVA2, D3D11, CUDA), Linux (VA-API, CUDA), macOS and iOS (VDA, VideoToolbox), Android, Raspberry Pi and Allwinner CedarX; OptimizedCopy needs SSE4.1 on x86 or NEON for CedarV |
| **Thread safety** | Not documented; AVPlayer is a QObject driven by Qt's event loop that runs its own demux, decode and output threads |
| **Drop-in for the baseline** | no |

## Gotchas

- Zero-copy is backend- and GPU-specific: the wiki says NVIDIA GPUs do not support EGL with VA-API, AMD is untested, DXVA 0-copy in desktop OpenGL works only on some newer Intel GPUs and is 'not stable', and VA-API zero-copy may not work on the vdpau backend.
- OptimizedCopy's SSE4.1 path is documented as not working on some GPUs (e.g. NVIDIA GS8400) and as crashing with VDA.
- Several advertised backends (VDPAU, some D3D11 and CUDA paths, RPI and Cedarv EGL) exist only in the author's successor mdk-sdk, which is binary-only and key-licensed, not in QtAV.
- The performance claim cannot be checked: forum.qt.io/post/21312 does not resolve here (getaddrinfo ENOTFOUND), so the 10% figure is from search snippets of a 2014 author post with no VLC version, decoder path, file or method.

## Known shortcomings

- Only number is the author's 2014 Qt forum anecdote (about 10% less CPU than VLC, 10-bit H.264, HTC Butterfly S), snippet only (forum.qt.io blocked): no VLC version, no method, single device, contested by a user report; wiki claims ('best performance', DirectCopy faster than potplayer) unquantified. Author stopped development; stale (last commit 2025-08-15). Licence LGPL-2.1 library, GPL-3.0 player example.
- Enricher: last release 1.13.0 (2019-07-11); does not build with FFmpeg 5+ (issue #1377 open, community patch crashes) or Qt 6 (#1406 open, CMake Qt5-only); zero-copy path is GPU-specific and the SSE4.1 OptimizedCopy fails on some GPUs; the successor mdk-sdk is binary-only and key-licensed.

## Caveats and trade-offs

Weak evidence, tier C at most. The only number is one anecdote from the QtAV 1.3.3 announcement thread on the Qt forum ('A video player based on Qt and FFmpeg', forum.qt.io/post/21312, 2014 era), posted by the project author: about 10% less CPU than VLC for a 10-bit H.264 video on an HTC Butterfly S. forum.qt.io does not resolve from this environment, so the page was NOT opened and the figure comes from WebSearch snippets only (snippet only, seen independently by the searcher and the verifier). No VLC version, decoder path (VLC's software vs QtAV's), build, video file, or CPU model is given, and it is a single-device test with no methodology. A search snippet also showed a user reporting that VLC plays full-HD video more smoothly than QtAV, so the claim is contested. The repo README makes no performance claim (only that it was the first player to render 10-bit in OpenGL ES2, which VLC, XBMC and mplayer did not support at the time). The wiki pages carry unquantified claims only: 'The Most Efficient VDA Decoder on OSX' (April 2015) says 'The performance is the best now. Better than any other players.', and 'Hardware Accelerated Decoding' says DirectCopy mode is 'faster than potplayer, lavfilters+mpc, and may be the fastest one'; neither has numbers. The README says the author is no longer developing QtAV and points users to his mdk-sdk; the 2025 commits are a contributor's Vulkan renderer.

Qt plus FFmpeg playback framework with hardware decoders (DXVA2, VAAPI, VideoToolbox, CedarX, CUDA) and OpenGL/ES2 rendering for Hi10P and other formats. The library is LGPL v2.1, the player example is GPL v3, and FFmpeg licensing applies on top. The author says he no longer develops QtAV and points to his newer mdk-sdk.

## Maintenance

Stale: the author stopped development (README points to his key-licensed mdk-sdk), last release 1.13.0 in 2019, last commit 2025-08-15 (contributor Vulkan renderer), and it does not build with FFmpeg 5+ or Qt 6 without third-party patches; LGPL-2.1 source remains copyable.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The only number (about 10% less CPU than VLC for a 10-bit H.264 video on an HTC Butterfly S) is a first-party anecdote by the author in the Qt forum QtAV 1.3.3 announcement thread (forum.qt.io/post/21312), with no VLC version, file, CPU model or method; the page is DNS-blocked here, so the figure is confirmed by WebSearch snippet only. The repo README and wiki carry only unquantified claims, so C is the ceiling and D would apply if snippet-only evidence is not accepted.
- **Verifier notes:** Real, notable project (4.3k stars, 1.5k forks, listed on the FFmpeg projects page) but the speed evidence is one unopened author forum anecdote (\~10% less CPU than VLC on one Android phone, 2014) plus unquantified wiki claims; kept at C on snippet-only evidence, with D the fallback if the orchestrator requires an opened numbers page. Shortcomings to record: snippet-only single-device anecdote, no methodology or VLC version, contested by a user report, author stopped development (stale, last commit 2025-08-15 by a contributor). Metadata checked on github.com: LGPL-2.1 library plus GPL-3.0 player example, not a fork, not shown as archived.
- **Fields the verifier corrected:** `benchmark_url`, `license`, `caveats`
- **Shortcomings recorded by:** verifier batch-117 (wave 10); enricher w10 pair-032
- **Pages the verifier opened:**
  - <https://github.com/wang-bin/QtAV>
  - <https://github.com/wang-bin/QtAV/commits>
  - <https://raw.githubusercontent.com/wang-bin/QtAV/HEAD/README.md>
  - <https://raw.githubusercontent.com/wang-bin/QtAV/HEAD/lgpl-2.1.txt>
  - <https://github.com/wang-bin/QtAV/wiki>
  - <https://github.com/wang-bin/QtAV/wiki/The-Most-Efficient-VDA-Decoder-on-OSX>
  - <https://github.com/wang-bin/QtAV/wiki/Hardware-Accelerated-Decoding>
- **Sources the enricher read:**
  - <https://github.com/wang-bin/QtAV>
  - <https://raw.githubusercontent.com/wang-bin/QtAV/HEAD/README.md>
  - <https://raw.githubusercontent.com/wang-bin/QtAV/HEAD/Changelog>
  - <https://raw.githubusercontent.com/wang-bin/QtAV/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/wang-bin/QtAV/HEAD/QtAV.pro>
  - <https://raw.githubusercontent.com/wang-bin/QtAV/HEAD/src/CMakeLists.txt>
  - <https://raw.githubusercontent.com/wang-bin/QtAV/HEAD/src/utils/GPUMemCopy.cpp>
  - <https://raw.githubusercontent.com/wang-bin/QtAV/HEAD/src/utils/CopyFrame_SSE4.cpp>
  - <https://github.com/wang-bin/QtAV/tree/master/src/utils>
  - <https://github.com/wang-bin/QtAV/commits>
  - <https://github.com/wang-bin/QtAV/wiki/Hardware-Accelerated-Decoding>
  - <https://github.com/wang-bin/QtAV/wiki/The-Most-Efficient-VDA-Decoder-on-OSX>
  - <https://github.com/wang-bin/QtAV/issues?q=is%3Aissue+ffmpeg+5>
  - <https://github.com/wang-bin/QtAV/issues/1377>
  - <https://github.com/wang-bin/QtAV/issues/1406>
  - <https://github.com/wang-bin/mdk-sdk>
  - https://forum.qt.io/post/21312 (attempted; getaddrinfo ENOTFOUND, content from WebSearch snippet only)
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/wang-bin/qtav`) · [data/wave10/enrich/raw/github_com_wang_bin_qtav.json](../../../data/wave10/enrich/raw/github_com_wang_bin_qtav.json) (enrichment confidence 0.5)

</details>
