# video_reader-rs

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Video and audio](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust (Python module over FFmpeg bindings)` · `MIT` · 🟢 active

> Rust-built Python video reader over libavcodec for ML loading; its own table beats OpenCV VideoCapture and decord.

| | |
|---|---|
| **Beats** | OpenCV VideoCapture and decord |
| **Claimed result** | Seconds to decode a (2004, 1472, 1472, 3) video into a numpy array, OpenCV / decord / vr.decode / vr.decode_fast: f 1.0 65 / 18 / 9.3 / 6.2; f 0.5 33.96 / 14.6 / 5.5 / 4.2; f 0.25 7.16 / 14.03 / 4.2 / 3.8; f 0.25 r 512 6.5 / 13.3 / 3.92 / 3.5; f 0.25 g 20.2 / 25.7 / 6.6 / N/A. At f 1.0 decode_fast is about 10.5x faster than OpenCV and 2.9x faster than decord; at f 0.25 about 1.9x faster than OpenCV and 3.7x faster than decord (derived from page data). README: 'performing equally or better than decord, while using less memory.' |
| **Workload** | Decode a whole video of shape (2004, 1472, 1472, 3) into a numpy array on a 12-core laptop with 15 GB RAM under Ubuntu 22.04; options are compression factor f, resize of shorter side r, grayscale g. |
| **Metric** | throughput |
| **Hardware** | Laptop with 12-core Intel i7-9750H @ 2.60GHz, 15 GB RAM, Ubuntu 22.04; decord was run on a different machine with more RAM and cores |
| **Adoption** | 126 stars |
| **Last commit** | 2026-09-30 |
| **Links** | [repository](https://github.com/gcanat/video_reader-rs) · [benchmark](https://github.com/gcanat/video_reader-rs) |

## Verdict

First-party README table, decoding one 2004-frame 1472x1472 video to RGB uint8 on an i7-9750H laptop with 15 GB RAM under Ubuntu 22.04: decode_fast 6.2 s vs OpenCV VideoCapture 65 s and decord 18 s at full frame rate, and 3.8 s vs 7.16 s and 14.03 s at compression factor 0.25. FFmpeg, OpenCV and decord versions, the codec and the timing script are not published, decord ran on a different, larger machine, and the OpenCV and decord columns come from a single July 2024 run while the video_reader columns were re-measured at later commits.

## Use it when

- Python ML data loading that needs a whole clip or uniformly subsampled frames as RGB uint8 numpy arrays, especially where decord runs out of memory because it allocates for the whole video at open.
- High-resolution sources where YUV-to-RGB conversion is a large share of the time; decode_fast() spreads it over cores (6.2 s vs 9.3 s for decode() at full frame rate in the README table).
- Training inputs downscaled at read time: resize_shorter_side, resize_longer_side or target_width/target_height run in the FFmpeg filter before conversion, so conversion touches fewer pixels.
- Pipelines that already hold encoded video in memory (object storage, queues): v0.4.5 reads bytes, bytearray or BytesIO without a temp file.
- Projects that want prebuilt wheels: manylinux_2_34 x86-64/aarch64/riscv64, macOS 14 arm64 and 15 x86-64, Windows amd64, abi3 for CPython &gt;= 3.9, plus PyPy 3.11 and free-threaded 3.14.

## Skip it when

- Sparse random access into long videos: users who measured it found parity or a loss against decord (issue #94: one frame per second from a 2-hour HD video, decord 1:45 vs video_reader 1:55; issue #97 on a Ryzen 5 5600X under Windows 10: decord 12% faster on one 1080p file, video_reader 23% faster on two others). The constructor also demuxes every packet to build its frame and keyframe index.
- Workloads that need pixel-identical output to OpenCV or decord: conversion uses its own matrix and range choices (issue #51 reports arrays that differ from cv2), and the BT.2020 and filtered-range colour bugs in issue #152 were fixed on main on 2026-09-28, after the 0.4.5 wheel of 2026-09-25.
- 10-bit, 4:2:2 or 4:4:4 sources where precision matters: the default and required filter path forces 8-bit yuv420p before RGB24.
- GPU-resident tensors or audio: the CUDA path downloads NV12 frames to host and returns numpy (DLPack support is an open PR, #150), non-CUDA hardware acceleration needs a hand-written filter, and there is no audio reader (issue #49 open).
- Odd output sizes: from code reading, copy_image sizes the YUV420 buffer as width\*(height+height/2), so an odd width or height without a custom filter (native odd dimensions, or a resize that rounds to an odd value) fails with an InvalidData error; choose even resize targets.

## How it is fast

Decoding itself is FFmpeg's libavcodec through ffmpeg-next 9.0.0 with frame-level threading and an automatic thread count, so the gains are pipeline gains. With compression_factor below 1 every packet is still decoded, but only the selected frames go through the FFmpeg filter graph (format=yuv420p, scale with fast_bilinear by default) and the YUV420-to-RGB24 conversion, which uses the SIMD yuv crate (awxkee's yuvutils-rs) instead of swscale. decode() writes into one preallocated ndarray; decode_fast() hands each frame's conversion to tokio tasks on a multi-thread runtime so conversion overlaps decoding, and the GIL has been released during decode since v0.4.2. get_batch picks keyframe seeking or a sequential pass from a cost estimate (GOP size, codec, number of seeks).

## Compared with alternatives

The closest sibling is Nelux, whose own numbers are against FFmpeg CLI pipes and torchcodec on Windows with NVDEC; pick video_reader-rs for numpy output, decord-style get_batch with a frame-accurate sequential fallback, and wheels across Linux, macOS, Windows, aarch64 and riscv64. Decoder entries such as dav1d, edge264 or rivet-h26x speed up decoding itself and are complementary, since video_reader-rs uses whatever libavcodec decoder its FFmpeg build provides.

## Integration

| | |
|---|---|
| **Form** | module (Python extension built from a Rust cdylib with maturin; PyPI wheels; not published as a Rust library crate) |
| **Dependencies** | numpy; FFmpeg libraries (bundled in the wheels; source builds need FFmpeg development libraries, libclang, pkg-config and maturin, plus the ffmpeg_5 feature for FFmpeg &lt;= 5); Rust crates ffmpeg-next 9.0.0, yuv 0.8.13, ndarray 0.16, tokio 1.48, pyo3 0.27 |
| **Minimum toolchain** | Python &gt;= 3.9; Rust 1.88 for source builds |
| **Platforms** | Linux (glibc 2.34+) x86-64, aarch64, riscv64; macOS 14 arm64 and 15 x86-64; Windows amd64; CUDA decode only from a source build against a CUDA-enabled FFmpeg |
| **Thread safety** | Each PyVideoReader guards its reader with a Mutex, so concurrent calls on one object serialize; decode and get_batch release the GIL (v0.4.2, issue #111), so separate readers in separate threads run in parallel. The FFmpeg log level set by the constructor is process-global. |
| **Drop-in for the baseline** | partial — decord-like get_batch, len, indexing and slicing, but a different class, constructor and a subset of decord's API; no cv2.VideoCapture-style read/grab interface |

## Gotchas

- decode() preallocates the whole (N, H, W, 3) result: the README's full 2004-frame 1472x1472 decode is 13.0 GB (derived from page data), so chunk with start_frame/end_frame. Frame count is the demuxed packet count, and from code reading decode() returns the full preallocated array even if fewer frames come out, leaving trailing all-zero frames.
- decode_gray() decodes full RGB first and then applies luma weights 0.2125/0.7154/0.0721 in Rust: it is slower than RGB decode (6.6 s vs 4.2 s in the README table) and its values differ from OpenCV's BT.601 cvtColor gray and from the Y plane.
- When the stream has no colour-space tag the matrix is guessed from height (below 720 BT.601, above 1080 BT.2020, otherwise BT.709), so untagged high-resolution video such as the 1472-line benchmark clip is converted with BT.2020.
- Custom filter strings must start with format=yuv420p and cannot be combined with resize options or target sizes (a filter containing 'scale' counts as a resize); decode_fast() returns a list, not a stacked array.

## Known shortcomings

- Decoding is FFmpeg's libavcodec through ffmpeg-next 9.0.0 (Linux wheels ship FFmpeg 8.1.1; the table's FFmpeg version is unstated), and OpenCV and decord also decode with libavcodec, so the gain is pipeline (frame threading, a compression factor that converts only selected frames, the Rust yuv crate instead of swscale, tokio-parallel conversion), not codec speed. No script produces the table (scripts/bench_get_batch.py times get_batch only); the decord column ran on another machine; the table dates from 2024 code.
- Enricher (e105, 2026-10-05): no bug behind the timings; C stands. The OpenCV and decord columns were never re-run since 2024 while the video_reader cells were re-run later (the f=0.5 cell went from 26.76 s, slower than decord's 14.6 s, to 5.5 s); the f=1.0 output is 13.0 GB on a 15 GB laptop, so OpenCV's 65 s likely includes swapping (inference). decode_fast returns a list, not a stacked array. Third-party issues #94 and #97 show parity or loss against decord; the colour fix #153 landed after the 0.4.5 wheel; odd output dimensions error out. NevermindNilas/python-decoders-benchmarks fails VideoReaderRS on every CI run ("name 'PyVideoReader' is not defined"), so no independent number exists.

## Caveats and trade-offs

The decoding itself is FFmpeg's libavcodec through the ffmpeg-next 9.0.0 Rust bindings (current Linux wheels bundle the PyAV-Org pyav-ffmpeg 8.1.1-2 build, Windows builds use FFmpeg 7.0 and macOS Homebrew ffmpeg@7; the FFmpeg version behind the benchmark table is not stated). The baselines, OpenCV VideoCapture and decord, also decode with libavcodec, so the gains come from the pipeline rather than codec speed: libavcodec frame threading with an automatic thread count, a compression factor that still decodes every packet but colour-converts only the selected frames, YUV-to-RGB conversion with the Rust yuv crate instead of swscale, and (decode_fast) conversion spread over tokio tasks. First-party table with no script for it in the repo (scripts/bench_get_batch.py covers get_batch against decord only), no FFmpeg, OpenCV or decord versions, and no codec or container named for the test video. The decord column came from a different, unspecified machine with more RAM and cores because decord crashed on the 15 GB laptop, so it is not like for like. The table was created in July 2024 and last updated in October 2024 (decode_fast and grayscale rows), so it measures 2024 code, not the current 0.4.5 release after the January 2026 speed and get_batch correctness changes. The README 'Crash test' snippet calls bench_video_decode with two arguments although the function takes three, and prints 4.81 s for f 0.25 against 4.2 s in the table. Baselines are other FFmpeg-based readers, not the FFmpeg tools. The source is MIT; the Python wheels bundle (L)GPL FFmpeg binaries (pyproject declares 'MIT OR GPL-2.0 OR GPL-3.0').

Python module built from Rust with FFmpeg bindings, not a C or C++ library; decodes only the requested segments, supports resize during decode, CUDA and VAAPI paths, custom FFmpeg filter chains. Only part of decord's API is implemented.

## Maintenance

Active (v0.4.5 on PyPI 2026-09-25, last commit 2026-09-30) and MIT for the Rust source, with (L)GPL FFmpeg binaries inside the wheels; frame-accuracy and colour fixes keep landing (decode near GOP boundaries #78, get_batch frames #90 fixed in v0.4.0, colours #153 after the last release), so pin a version and spot-check frames against a reference.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The README 'Performance comparison' table gives first-party wall-clock seconds against OpenCV and decord on a named CPU (i7-9750H) and OS, but the script that produced the table is not in the repo (scripts/bench_get_batch.py only times get_batch against decord and publishes no results), and no FFmpeg, OpenCV or decord version, video codec or compiler is stated; the decord column ran on a different, unspecified machine. First-party with partial methodology is C.
- **Verifier notes:** Repo page and commit list confirm MIT, 126 stars, 9 forks, not a fork, last commit 2026-09-30, version 0.4.5; numbers match the README exactly. I judge it a pipeline library over libavcodec (its own frame selection, YUV-to-RGB conversion and batching), not a thin binding of the listed FFmpeg entry, so not a duplicate; the orchestrator may still fold it under FFmpeg if it prefers. The speedup is pipeline, threading and conversion against other libavcodec-based readers, not faster decoding.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** first-party README table, columns from different dates
- **Pages the verifier opened:**
  - <https://github.com/gcanat/video_reader-rs>
  - <https://github.com/gcanat/video_reader-rs/commits>
  - <https://github.com/gcanat/video_reader-rs/commits/main/README.md>
  - <https://github.com/gcanat/video_reader-rs/tree/main/scripts>
  - <https://github.com/gcanat/video_reader-rs/tree/main/.github/workflows>
  - <https://github.com/gcanat/video_reader-rs/tree/main/src>
  - <https://raw.githubusercontent.com/gcanat/video_reader-rs/HEAD/README.md>
  - <https://raw.githubusercontent.com/gcanat/video_reader-rs/HEAD/scripts/bench_get_batch.py>
  - <https://raw.githubusercontent.com/gcanat/video_reader-rs/HEAD/.github/workflows/build.yml>
  - <https://raw.githubusercontent.com/gcanat/video_reader-rs/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/gcanat/video_reader-rs/HEAD/pyproject.toml>
  - <https://raw.githubusercontent.com/gcanat/video_reader-rs/HEAD/license_notes.md>
  - <https://raw.githubusercontent.com/gcanat/video_reader-rs/HEAD/src/reader.rs>
  - <https://raw.githubusercontent.com/gcanat/video_reader-rs/HEAD/src/decoder.rs>
  - <https://raw.githubusercontent.com/gcanat/video_reader-rs/HEAD/src/convert.rs>
- **Sources the enricher read:**
  - <https://github.com/gcanat/video_reader-rs>
  - <https://raw.githubusercontent.com/gcanat/video_reader-rs/HEAD/README.md>
  - <https://raw.githubusercontent.com/gcanat/video_reader-rs/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/gcanat/video_reader-rs/HEAD/pyproject.toml>
  - <https://raw.githubusercontent.com/gcanat/video_reader-rs/HEAD/license_notes.md>
  - <https://raw.githubusercontent.com/gcanat/video_reader-rs/HEAD/scripts/bench_get_batch.py>
  - <https://raw.githubusercontent.com/gcanat/video_reader-rs/HEAD/src/reader.rs>
  - <https://raw.githubusercontent.com/gcanat/video_reader-rs/HEAD/src/decoder.rs>
  - <https://raw.githubusercontent.com/gcanat/video_reader-rs/HEAD/src/convert.rs>
  - <https://raw.githubusercontent.com/gcanat/video_reader-rs/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/gcanat/video_reader-rs/HEAD/src/info.rs>
  - <https://raw.githubusercontent.com/gcanat/video_reader-rs/HEAD/src/filter.rs>
  - <https://raw.githubusercontent.com/gcanat/video_reader-rs/HEAD/src/utils.rs>
  - <https://raw.githubusercontent.com/gcanat/video_reader-rs/322b492/README.md>
  - <https://raw.githubusercontent.com/gcanat/video_reader-rs/59b8b31/README.md>
  - <https://raw.githubusercontent.com/gcanat/video_reader-rs/639f3ad/README.md>
  - <https://raw.githubusercontent.com/gcanat/video_reader-rs/dd5f74f/README.md>
  - <https://raw.githubusercontent.com/gcanat/video_reader-rs/141bc05/README.md>
  - <https://pypi.org/pypi/video-reader-rs/json>
  - <https://github.com/gcanat/video_reader-rs/issues?q=is%3Aissue>
  - <https://github.com/gcanat/video_reader-rs/pulls?q=is%3Apr>
  - <https://github.com/gcanat/video_reader-rs/issues/94>
  - <https://github.com/gcanat/video_reader-rs/issues/97>
  - <https://github.com/gcanat/video_reader-rs/issues/78>
  - <https://github.com/gcanat/video_reader-rs/issues/90>
  - <https://github.com/gcanat/video_reader-rs/issues/100>
  - <https://github.com/gcanat/video_reader-rs/issues/51>
  - <https://github.com/gcanat/video_reader-rs/issues/152>
  - <https://github.com/gcanat/video_reader-rs/releases>
  - <https://raw.githubusercontent.com/NevermindNilas/python-decoders-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/NevermindNilas/python-decoders-benchmarks/HEAD/history/720p_history.json>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/gcanat/video_reader-rs`) · [data/wave10/enrich/raw/github_com_gcanat_video_reader_rs.json](../../../data/wave10/enrich/raw/github_com_gcanat_video_reader_rs.json) (enrichment confidence 0.75)

</details>
