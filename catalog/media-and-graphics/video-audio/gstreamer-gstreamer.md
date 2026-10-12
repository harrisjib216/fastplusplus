# GStreamer (gst-vaapi VA-API pipelines)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Video and audio](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `LGPL-2.1-or-later` · 🟢 active

> Plugin-based C media framework; its VA-API pipelines decoded and encoded on an Intel iGPU 1.2-10x faster than OpenCV's software FFmpeg backend.

| | |
|---|---|
| **Beats** | FFmpeg (libavcodec through OpenCV's VideoCapture/VideoWriter FFmpeg backend, CPU software codecs) |
| **Claimed result** | OpenCV wiki (2018, i5-6600): gst-vaapi H.264 encode 193 vs 51 fps and VP8 10.3x over OpenCV's FFmpeg backend, with the FFmpeg side single-threaded for VP8 and MPEG-2 and no hardware path; gst-vaapi slower on every mkv decode. |
| **Workload** | OpenCV benchmark sample (samples/cpp/gstreamer_pipeline.cpp, now samples/cpp/videocapture_gstreamer_pipeline.cpp). Decode: frames per second of grab+retrieve to BGR over a full-HD 1920x1080 clip encoded with ffmpeg default settings, in mkv, mp4 and avi containers (mpeg2, h264, h265, vp8). Encode: 1000 frames from a synthetic GStreamer videotestsrc SMPTE colour-bar source (resolution set by -r, default 720p; the page does not say which was used), timing only the VideoWriter write call. GStreamer pipelines (gst-vaapi on the Intel iGPU, gst-libav on the CPU) versus OpenCV's FFmpeg backend (CPU software codecs). |
| **Metric** | throughput |
| **Hardware** | Intel Core i5-6600 @ 3.30GHz, Intel HD Graphics 530 (Skylake GT2), Ubuntu 17.10 |
| **Compiler and flags** | OpenCV built with cmake -DBUILD_EXAMPLES=ON -DWITH_GSTREAMER=ON -DWITH_FFMPEG=ON, make -j8 (build type not given); GStreamer, gstreamer1.0-vaapi, gstreamer1.0-libav and libavcodec are unversioned Ubuntu 17.10 apt packages per the page's install commands; compiler, optimisation flags, encoder settings and OpenCV/GStreamer/FFmpeg versions not stated |
| **Adoption** | 3.3k stars on the GitHub mirror; used in many Linux media stacks |
| **Last commit** | 2026-10-11 |
| **Links** | [repository](https://github.com/GStreamer/gstreamer) · [benchmark](https://github.com/opencv/opencv/wiki/Video-capture-and-write-benchmark) |

## Verdict

OpenCV's 2018 wiki benchmark (single runs, Ubuntu 17.10 packages, Core i5-6600 with HD Graphics 530) timed its gstreamer_pipeline sample: gst-vaapi encoded 1000 synthetic frames at 193/194/185 fps H.264 and 124 fps VP8 versus 51/51/50 and 12 fps through OpenCV's FFmpeg writer, and decoded 1080p mp4/avi H.264 at 376/373 fps versus 169/159 fps, but lost on every mkv input. It is iGPU fixed-function hardware against CPU software codecs with unequal conversion threading and encoder settings, not GStreamer's own code against FFmpeg's.

## Use it when

- Linux machines with an Intel or AMD GPU and a working VA-API driver that must encode H.264, HEVC or VP8 faster than software encoders can, e.g. writing many 720p/1080p streams from an OpenCV or camera application where the measured gap was 3.7-3.8x for H.264 and about 10x for VP8.
- Decoding H.264/HEVC from MP4 or AVI on such hardware while freeing CPU cores: the page measured 376 vs 169 fps (mp4/h264) and 391 vs 256 fps (mp4/h265) at 1080p to BGR.
- Applications that need a full pipeline (capture, RTSP/WebRTC, muxing, compositing) with swappable hardware backends (VA, NVCODEC, V4L2, MediaSDK/QSV) rather than a single codec library.
- OpenCV programs on Linux that already have WITH_GSTREAMER builds and can express their I/O as a pipeline string.

## Skip it when

- Matroska input on the measured stack: gst-vaapi decoded every mkv clip far slower than FFmpeg (h264 59 vs 158, h265 65 vs 255, vp8 68 vs 309 fps); the page gives no explanation, so test your container before switching.
- Pure CPU decoding: gst-libav wraps the same libavcodec and lost to OpenCV's FFmpeg backend on h264, h265 and vp8 decode and on mpeg2 encode (81 vs 106 fps).
- When compression efficiency or quality per bit matters: hardware encoders at VA-API defaults were compared with libx264 CRF 23 and libvpx good-quality output, with no bitrate or quality figures, so the speed buys an unmeasured quality loss.
- Machines without a supported GPU and VA driver (or non-Linux targets for the VA elements); the speedup does not exist there.
- As evidence against FFmpeg itself: FFmpeg's own VA-API path was never measured, and current OpenCV 4.x can enable VA-API in its FFmpeg backend (cap_ffmpeg_hw.hpp, VIDEO_ACCELERATION_VAAPI), removing the 2018 reason for the comparison.

## How it is fast

The headline wins are hardware offload, not faster software: vaapidecodebin and vaapih264enc/vaapivp8enc hand the bitstream to the Skylake GT2 media engine through libva, so the CPU only demuxes, copies surfaces back and colour-converts. The pipeline also overlaps work across threads (demuxer, decoder queue, converter and the application run concurrently), and in the OpenCV sample the GStreamer pipelines convert colour with videoconvert n-threads set to OpenCV's thread count, while the FFmpeg backend converts with a single sws_scale call (SWS_BICUBIC) on the calling thread.

## Compared with alternatives

Pick GStreamer when you need GPU-offloaded encode or decode inside a full streaming pipeline on Linux; for decoding straight into arrays from Python, Nelux (FFmpeg with NVDEC) or video_reader-rs (beats OpenCV VideoCapture) are simpler, and for a faster pure-software H.264 decoder edge264 or rivet-h26x target libavcodec directly.

## Integration

| | |
|---|---|
| **Form** | shared lib (libgstreamer-1.0 core plus dynamically loaded plugin libraries) |
| **Dependencies** | GLib/GObject, libintl, zlib, libffi (mandatory, bundled as meson subprojects); for this result libva plus a VA driver and the VA plugin, gst-libav needs FFmpeg; OpenCV built with -DWITH_GSTREAMER=ON to use it from OpenCV |
| **Minimum toolchain** | C compiler; building the monorepo needs Meson 1.4+, ninja and Python 3.8+ (README); measured with Ubuntu 17.10 packages (GStreamer 1.12 series) |
| **Platforms** | Linux, Windows, macOS, Android, iOS for the core; VA-API elements are Linux-oriented and need Intel/AMD hardware decode/encode support for the codec |
| **Thread safety** | Pipelines run on internal streaming threads; the thread-safety contract of the API was not read this session (not documented in the sources read) |
| **Drop-in for the baseline** | partial — in OpenCV you swap CAP_FFMPEG for CAP_GSTREAMER and pass a pipeline string (e.g. filesrc ! qtdemux ! vaapidecodebin ! videoconvert ! appsink); outside OpenCV it is a different framework API from libavcodec/libavformat |

## Gotchas

- Harness asymmetry in the OpenCV 3.4 sample and backends: GStreamer pipelines colour-convert with videoconvert n-threads=getNumThreads() (4 on the i5-6600) while the FFmpeg backend converts each 1080p frame to BGR24 with one single-threaded sws_scale inside the timed retrieve; and OpenCV's FFmpeg writer never sets thread_count, so libvpx (VP8, deadline good, cpu-used 1) and FFmpeg's mpeg2video encoder ran single-threaded (libx264 alone gets automatic threads from its codec defaults). The 10.3x VP8 and 1.2x MPEG-2 encode ratios are therefore hardware versus one CPU core, and part of the CPU-side gaps (including gst-libav's mpeg2 decode wins) is conversion threading, not codec speed.
- Encode timing covers only the VideoWriter write call: GStreamer's appsrc (block=1, default max-bytes) returns once the previous frame is dequeued, so encoding overlaps the untimed synthetic-frame grab; FFmpeg's x264 lookahead frames and GStreamer's in-flight frames are flushed in close(), also untimed. The input is 1000 identical videotestsrc SMPTE colour-bar frames (default 720p, 30 fps target), not real video, and the output files are never decoded or checked.
- The measured plugin is gone: gstreamer-vaapi was removed from the monorepo on 2025-06-10 ('gstreamer-vaapi: remove subproject', after 1.26.0); current code uses the va plugin in gst-plugins-bad (vah264enc since 1.22, plus vah265, vavp8, vavp9, av1 and jpeg elements), which this benchmark never measured. The OpenCV sample still names vaapi elements.
- Licensing: the core is LGPL-2.1-or-later, but some plugins with GPL dependencies (x265enc, mpeg2enc, the sample's 'gst-basic' MPEG-2 encoder) are only built with -Dgpl=enabled. Container parsers have had many CVEs (e.g. the December 2024 batch for matroskademux and qtdemux fixed in 1.24.10), so keep it updated when handling untrusted files.

## Known shortcomings

- OpenCV wiki tables (2018, Ubuntu 17.10, i5-6600) match, but they compare iGPU hardware codecs through gst-vaapi with CPU software codecs through OpenCV's FFmpeg wrapper, which had no VA-API path, so FFmpeg's own hardware path was never measured; unequal encoder settings; encode input is synthetic 720p SMPTE bars, not the 1080p clip; the encode timer covers only the write call (small bias for GStreamer's async appsrc); gst-vaapi is slower on every mkv decode; no compiler, flags, versions or run counts. gstreamer-vaapi has since been removed from the GStreamer main branch in favour of the va plugin (snippet only). Benchmark code exists: samples/cpp/gstreamer_pipeline.cpp at OpenCV tag 3.4.3.
- Enricher: OpenCV 3.4.2's FFmpeg writer (cap_ffmpeg_impl.hpp) never sets thread_count, so libvpx VP8 (deadline good, cpu-used 1) and mpeg2video ran single-threaded while only libx264 got auto threads, making the 10.3x VP8 and 1.2x MPEG-2 rows iGPU vs one CPU core; the GStreamer pipelines use videoconvert n-threads=4 while the FFmpeg path converts with single-threaded sws_scale inside the timed retrieve; encode input is 1000 identical SMPTE frames, output never checked, write-only timer with untimed flush tails on both sides. gstreamer-vaapi was removed from the monorepo 2025-06-10 (va plugin replaced it) and OpenCV 4.x's FFmpeg backend now has VAAPI (cap_ffmpeg_hw.hpp).

## Caveats and trade-offs

The win is hardware versus software: gst-vaapi drives the Skylake iGPU's fixed-function codecs, while OpenCV's FFmpeg wrapper had no hardware acceleration at the time (the page says so), so FFmpeg itself, which also supports VA-API, was not measured with hardware decode or encode; this is not GStreamer's own code being faster. Encoders differ (VA-API defaults versus libx264/libvpx defaults through OpenCV's FFmpeg writer), so output quality and bitrate are not equal. Encode input is a synthetic SMPTE colour-bar pattern (default 720p in the sample), not the 1080p clip, and the page does not state the encode resolution. The encode timer covers only the write call: GStreamer's appsrc (block=1) encodes in its own streaming thread, so encoding that overlaps the untimed synthetic-frame grab is hidden, a modest bias in GStreamer's favour; frames still queued at end of stream are not timed. The page's x multipliers are relative to the faster CPU column (gst-libav or FFmpeg), e.g. mp4/mpeg2 decode x1.06 is versus gst-libav 343 fps; versus FFmpeg 258 fps it is x1.41 (derived from page data). gst-vaapi decode was slower than FFmpeg for every mkv input (h264 59 vs 158, h265 65 vs 255, vp8 68 vs 309 fps) and CPU gst-libav lost to FFmpeg on h264, h265 and vp8 decode and on mpeg2 encode (81 vs 106 fps). Single undated-run results from 2018 on Ubuntu 17.10; no run counts or variance. The measured component, gstreamer-vaapi, is no longer in the GStreamer monorepo's main branch (subprojects/ has no gstreamer-vaapi; upstream replaced it with the va plugin in gst-plugins-bad according to forum and distro-packaging search snippets, and this page did not measure that plugin). The benchmark sample linked from the page 404s at master because it was renamed; it is reachable at OpenCV tag 3.4.3 (samples/cpp/gstreamer_pipeline.cpp) and as samples/cpp/videocapture_gstreamer_pipeline.cpp on 4.x. The GitHub repo is a read-only mirror of gitlab.freedesktop.org/gstreamer/gstreamer and carries no benchmarks itself. LICENSE file is LGPL v2.1 text; SPDX LGPL-2.1-or-later per GStreamer's source headers convention, not checked file by file. [retier] Hardware vs software codecs; baseline single-threaded by harness default; videoconvert n-threads=4 vs single-threaded sws_scale; 1000 identical SMPTE frames, output unchecked, write-only timer; gstreamer-vaapi removed 2025-06-10 in favour of the va plugin; OpenCV 4.x FFmpeg backend now has VAAPI.

Framework with plugin pipelines; speed here comes from the VA-API plugin offloading to the Intel iGPU, which needs Intel graphics, a VA-API driver and the gst-vaapi plugin. Hardware encoders trade compression efficiency and quality for speed; the page does not compare quality or bitrate. GStreamer's CPU path (gst-libav) wraps the same libavcodec as FFmpeg.

## Maintenance

Actively developed (GitHub read-only mirror of gitlab.freedesktop.org, 126k commits, last commit 2026-10-11) and LGPL-2.1-or-later, so linking is usable in closed products; the measured gstreamer-vaapi plugin was removed in June 2025 in favour of the va plugin, so the numbers describe a component you can no longer get from main.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now C.
- **Tier reason:** Independent measurement by the OpenCV project (wiki page last edited 2018-06-22) comparing GStreamer gst-vaapi and gst-libav pipelines against OpenCV's FFmpeg backend; the benchmark code is public (samples/cpp/gstreamer_pipeline.cpp at OpenCV tag 3.4.3, renamed samples/cpp/videocapture_gstreamer_pipeline.cpp in November 2018) and the CPU is stated (Core i5-6600, HD Graphics 530), but no compiler, flags, encoder settings, library versions or run counts are given, so it is not A.
- **Retiered** B to C: Lowered B to C: the independent OpenCV wiki numbers compare iGPU hardware codecs with a software baseline crippled by the harness (OpenCV 3.4.2's FFmpeg writer never set thread_count, so VP8 and MPEG-2 encoded on one core, and its colour conversion ran single-threaded inside the timer while the GStreamer pipeline used 4 convert threads); per the crippled-baseline rule the measurement is first-party-grade at best.
- **Verifier notes:** Every number in claimed_speedup matches the OpenCV wiki tables (encode h264 193/194/185 vs 51/51/50, vp8 124 vs 12, mpeg2 124 vs 106; decode mp4/h264 376 vs 169, avi/h264 373 vs 159, mp4/h265 391 vs 256, mp4/mpeg2 364 vs 258). Shortcomings to record: hardware iGPU versus CPU software codecs (FFmpeg's own VA-API path not used), unequal encoder settings, synthetic 720p-default encode input not the 1080p clip, write-only encode timer favouring GStreamer's async pipeline, mkv decode much slower with gst-vaapi, 2018 Ubuntu 17.10 run with no versions or flags, and gstreamer-vaapi since removed from GStreamer main in favour of the va plugin. Metadata checked: 3.3k stars, 774 forks, mirror (not a fork), last commit 2026-10-11, LGPL-2.1 LICENSE.
- **Fields the verifier corrected:** `workload`, `compiler_and_flags`, `caveats`, `claimed_speedup`
- **Shortcomings recorded by:** verifier batch-114 (wave 10); enricher w10 pair-028
- **Pages the verifier opened:**
  - <https://github.com/opencv/opencv/wiki/Video-capture-and-write-benchmark>
  - <https://raw.githubusercontent.com/opencv/opencv/master/samples/cpp/gstreamer_pipeline.cpp>
  - <https://raw.githubusercontent.com/opencv/opencv/3.4.3/samples/cpp/gstreamer_pipeline.cpp>
  - <https://raw.githubusercontent.com/opencv/opencv/4.x/samples/cpp/videocapture_gstreamer_pipeline.cpp>
  - <https://github.com/opencv/opencv/commits/4.x/samples/cpp/videocapture_gstreamer_pipeline.cpp>
  - <https://raw.githubusercontent.com/opencv/opencv/4.x/modules/videoio/src/cap_gstreamer.cpp>
  - <https://raw.githubusercontent.com/opencv/opencv/3.4/modules/videoio/src/cap_gstreamer.cpp>
  - <https://github.com/GStreamer/gstreamer>
  - <https://github.com/GStreamer/gstreamer/tree/main/subprojects>
  - <https://github.com/GStreamer/gstreamer/commits/main>
  - <https://raw.githubusercontent.com/GStreamer/gstreamer/main/LICENSE>
  - <https://raw.githubusercontent.com/GStreamer/gstreamer/main/README.md>
- **Sources the enricher read:**
  - <https://github.com/opencv/opencv/wiki/Video-capture-and-write-benchmark>
  - <https://raw.githubusercontent.com/opencv/opencv/3.4.3/samples/cpp/gstreamer_pipeline.cpp>
  - <https://raw.githubusercontent.com/opencv/opencv/3.4.2/modules/videoio/src/cap_gstreamer.cpp>
  - <https://raw.githubusercontent.com/opencv/opencv/3.4.2/modules/videoio/src/cap_ffmpeg_impl.hpp>
  - <https://raw.githubusercontent.com/opencv/opencv/4.x/modules/videoio/src/cap_ffmpeg_hw.hpp>
  - <https://raw.githubusercontent.com/GStreamer/gst-plugins-base/1.12/gst/videoconvert/gstvideoconvert.c>
  - <https://raw.githubusercontent.com/GStreamer/gst-plugins-base/1.14/gst/videoconvert/gstvideoconvert.c>
  - <https://raw.githubusercontent.com/FFmpeg/FFmpeg/release/3.3/libavcodec/libx264.c>
  - <https://raw.githubusercontent.com/FFmpeg/FFmpeg/release/3.3/libavcodec/options_table.h>
  - <https://raw.githubusercontent.com/FFmpeg/FFmpeg/release/3.3/libavcodec/options.c>
  - <https://raw.githubusercontent.com/FFmpeg/FFmpeg/release/3.3/libavcodec/libvpxenc.c>
  - <https://github.com/GStreamer/gstreamer>
  - <https://raw.githubusercontent.com/GStreamer/gstreamer/main/README.md>
  - <https://github.com/GStreamer/gstreamer/tree/main/subprojects>
  - <https://github.com/GStreamer/gstreamer/commits/main/subprojects/gstreamer-vaapi>
  - <https://raw.githubusercontent.com/GStreamer/gstreamer/main/subprojects/gst-plugins-bad/sys/va/meson.build>
  - <https://raw.githubusercontent.com/GStreamer/gstreamer/main/subprojects/gst-plugins-bad/sys/va/gstvah264enc.c>
  - WebSearch: GStreamer security advisories 2024 (gstreamer.freedesktop.org/security index, sa-2024-0030; snippets only)
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/gstreamer/gstreamer`) · [data/wave10/enrich/raw/github_com_gstreamer_gstreamer.json](../../../data/wave10/enrich/raw/github_com_gstreamer_gstreamer.json) (enrichment confidence 0.65)

</details>
