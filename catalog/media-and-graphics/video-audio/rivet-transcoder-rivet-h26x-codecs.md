# rivet-h26x (rivet-h26x-codecs)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Video and audio](README.md)</sub>

**Tier C** (first-party claim) · Study only · `Rust` · `Open Encoding Attribution License v1.0 (source-available, royalty-free with commercial attribution; not OSI-approved; no SPDX id confirmed)` · 🟢 active

> Pure-Rust H.264/H.265 decoders, conformance bit-exact; beats libavcodec only on all-thread WPP HEVC, at parity or behind elsewhere.

| | |
|---|---|
| **Beats** | libavcodec (FFmpeg) native H.264 and H.265 decoders |
| **Claimed result** | All threads on the wavefront H.265 clip wpp10.265: 1963 fps vs libavcodec 1774 fps (+10.7%); single-thread on that clip 1.938 CPU s vs 1.906 s (1.02x libavcodec's time, parity). Non-wavefront H.265 hevc6.265 all threads 1288 vs 1387 fps (-7.1%), single-thread 1.12x libavcodec's CPU time. H.264 single-thread costs 1.46-1.55x libavcodec's CPU time; H.264 all-thread fps 2169 vs 2119 (CABAC) and 3116 vs 3063 (CAVLC) are +2.4% and +1.7%, which the README says are within its 4% noise floor. |
| **Workload** | Decode of 720p Big Buck Bunny encodes (cabac3.264 and cavlc3.264, H.264 High from x264 CRF 20, 723 frames each; hevc6.265, H.265 Main from x265 without WPP, 1446 frames; wpp10.265, x265 with WPP, 1200 frames), clips repeated so a run lasts long enough for Windows' 15.6 ms CPU-time clock. Process-tree CPU seconds (Windows job object) and frames per wall second, best of 5. Single-thread rows pinned to one core for both decoders (ffmpeg -threads 1, H26X_THREADS=1); all-thread rows unpinned (ffmpeg with its default thread count, rivet with every core). libavcodec ran as 'ffmpeg -i clip -f rawvideo -y NUL' (rawvideo written to the null device); rivet ran examples/h26xdec with H26XDEC_NOMD5=1 (each picture packed and dropped). |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 9950X 16-Core Processor, 32 hardware threads, Windows (job-object CPU accounting), AVX-512 rung; machine 17% busy before the run; single-thread rows pinned to core 29, all-thread rows unpinned |
| **Compiler and flags** | Not stated for either decoder: the FFmpeg build was a scoop-installed ffmpeg of unstated version and configuration; rivet built with the default cargo release profile (no profile overrides in Cargo.toml), rustc version unstated. SIMD rung selected at run time (AVX-512 supplement on this CPU). The libavcodec rows came from tools/benchmark.py at commit cc9195a; the current tools/benchmark.py (since 6eb41d8, 2026-10-03) compares against the scalar rung only. |
| **Adoption** | 0 stars, 0 forks; 515 commits; not on crates.io (crates.io API on 2026-10-04: crate 'rivet-h26x' does not exist) despite the README badge; moved from the rivet-transcoder organisation to safewords on 2026-10-03 |
| **Last commit** | 2026-10-03 |
| **Links** | [repository](https://github.com/rivet-transcoder/rivet-h26x-codecs) · [benchmark](https://raw.githubusercontent.com/safewords/rivet-h26x-codecs/HEAD/README.md) |

## Verdict

First-party tables from tools/benchmark.py at cc9195a on an AMD Ryzen 9 9950X (32 threads, Windows, AVX-512 rung, machine 17% busy): the ffmpeg CLI of unstated version decoding to rawvideo on NUL against the h26xdec example, best of 5, process-tree CPU seconds and frames per wall second, on unpublished 720p Big Buck Bunny x264/x265 clips. Only the all-thread wpp10.265 cell is ahead (1963 vs 1774 fps, +10.7%), with 32 rivet threads and 1.75x the CPU seconds against libavcodec's frame-only auto threading; single-threaded rivet takes 1.02x and 1.12x libavcodec's CPU time on H.265 and 1.46-1.55x on H.264.

## Use it when

- You need an H.264 or H.265 software decoder in a pure-Rust build: no C toolchain, no system FFmpeg, no build script (cross-compiles, sandboxed CI, wasm32 probing).
- Correctness and coverage matter more than CPU cost: 204/204 JVT AVC streams plus 38 professional-profile streams against JM, 147/147 HEVC_v1 and 49/49 RExt streams against the suite MD5s, identical output on 1 and 12 threads.
- Throughput per wall second on a many-core box decoding x265 streams encoded with WPP (or tiles), with spare CPU to burn: the one measured cell ahead of libavcodec (1963 vs 1774 fps on a 32-thread Ryzen 9 9950X).
- Unusual formats that matter to you: H.264 MBAFF, FMO/ASO, SP/SI, High 4:4:4 up to 14-bit, HEVC RExt up to 16-bit with extended precision.

## Skip it when

- CPU cost, battery or density matters: single-threaded it costs 1.46-1.55x libavcodec's CPU time on H.264 and 1.02-1.12x on H.265, and its all-thread runs spend 1.02-1.75x libavcodec's CPU seconds (4.656 vs 2.656 s on the winning WPP clip).
- HEVC streams without WPP or tiles on many threads: 7.1% fewer frames per second than libavcodec on hevc6.265; H.264 all-thread gains (+1.7%, +2.4%) are inside the noise.
- You need an OSI licence, GPL compatibility or no attribution duty: the Open Encoding Attribution License v1.0 requires a visible credit in commercial products and for-profit services and states it is not open source.
- You want a published, versioned dependency: crates.io has no rivet-h26x crate (checked 2026-10-04) despite the README badge, rust-version is 1.99 with edition 2024, and the project is one author with 0 stars.
- You decode untrusted streams and need documented hardening: no fuzzing harness or security policy is documented, and the SIMD kernels are unsafe intrinsics (plus an asm! sdot wrapper on AArch64).

## How it is fast

Two threading layers on one FIFO worker pool: frame threading with per-row progress (motion compensation waits only on the reference rows it needs, deblocking and SAO trail the decode row by row) and, for H.265, wavefront (WPP) rows, tiles and slice segments run as separate tasks inside a picture. libavcodec picks frame threading exclusively whenever a codec supports it (validate_thread_parameters in libavcodec/pthread.c), so on a WPP stream rivet exploits intra-picture parallelism that ffmpeg's default does not, which is where its one win comes from. Pixel kernels are Rust intrinsics behind a run-time function table that climbs SSE2, SSSE3, SSE4.1, AVX, AVX2 with an AVX-512 (F+BW+VL) supplement for wide H.265 shapes, and NEON plus sdot on AArch64; per the README, SSE2 alone is 2.4-2.9x over scalar and everything above it adds only 1-2% on H.264 and 15-18% on H.265. Output buffers come from a pool, so steady-state decoding allocates nothing per frame.

## Compared with alternatives

Against edge264 (an H.264 decoder that beats libavcodec single-threaded in its own chart) and rusty_h265 (Rust HEVC, about 1.05x FFmpeg 8.1.2 single-core on one stream), pick rivet-h26x when you want both codecs in one pure-Rust crate with full JVT and JCT-VC conformance including RExt and MBAFF, not when you want the fastest single-thread decode; for raw speed on H.264 libavcodec itself or edge264 stays ahead.

## Integration

| | |
|---|---|
| **Form** | crate (Rust library imported as h26x; not on crates.io as of 2026-10-04, so a git dependency) |
| **Dependencies** | thiserror 2 (md5 0.7 for tests only) |
| **Minimum toolchain** | Rust 1.99 (rust-version in Cargo.toml), edition 2024 |
| **Platforms** | x86-64 (SSE2 baseline, run-time ladder up to AVX2 plus AVX-512 F+BW+VL supplement), AArch64 (NEON, dot product), wasm32 checked by tools/wasm.sh; scalar kernels exist as the reference; other targets not documented |
| **Thread safety** | Each decoder drives an internal worker pool sized by H26X_THREADS (default every core, up to 32) with up to H26X_INFLIGHT pictures in flight (default threads clamped to 2-16); output is deterministic across thread counts; Send/Sync guarantees for the decoder types are not documented |
| **Drop-in for the baseline** | false: different API (push NAL units, pull Picture), H.264 and H.265 only, no demuxer, no AVFrame, no hardware decode path |

## Gotchas

- Thread count, in-flight depth and SIMD caps are environment variables (H26X_THREADS, H26X_INFLIGHT, H26X_MAX_SIMD, H26X_NO_SIMD) per the README, and the default grabs every core up to 32, far more than libavcodec's auto setting (capped at 16); cap it on a shared machine.
- A dropped Picture returns its packed buffer to the decoder's OutputPool (bounded at 32 buffers); Picture::into_packed takes the buffer for good, so keeping frames that way costs a fresh allocation per frame.
- Picture data is already packed Y, Cb, Cr in one buffer (8-bit as bytes, 9-16-bit as little-endian 16-bit words, every plane at the wider depth when luma and chroma depths differ), not strided planes you can decode into.
- Some docs are stale: src/lib.rs still says verification uses MD5s against libavcodec while the README says none of it involves FFmpeg any more, and the h26xdec comment says H26XDEC_NOMD5 skips packing, although packing happens inside the decoder (picture.rs), so the benchmarked binary did materialise every frame.

## Known shortcomings

- Open Encoding Attribution License v1.0 (not OSI approved), so reference only. The single win (wpp10 clip, all threads, +10.7%) used 32 threads and 1.75x the CPU seconds against libavcodec's auto threads capped at 16 (MAX_AUTO_THREADS); FFmpeg version and flags unstated, clips unpublished; not on crates.io; repository moved to the safewords organisation.
- The single wpp10.265 all-thread win is weak: the harness since df463da prints a same-binary control per table but the README omits the H.265 controls and borrows the 4% noise floor from the H.264 pair; ladder inversions within the same fps column reach 6.3% (SSE4.1 1913 against AVX 1799) and 5.4% (cavlc3 SSE2 2985 against SSSE3 2831), and the +10.7% is about 65 ms of wall time on 0.6 s runs that include ffmpeg start-up and possibly a scoop shim; libavcodec ran frame-only threading. rust-version 1.99 with edition 2024; not on crates.io; no fuzzing documented; lib.rs and h26xdec docs stale.

## Caveats and trade-offs

Only one cell of four is ahead: all-threads on the wavefront H.265 clip wpp10.265 (1963 vs 1774 fps, +10.7%), and that cell is not equal work: rivet spent 4.656 CPU s against libavcodec's 2.656 (1.75x, per the README's own line) and used every hardware thread (32), while ffmpeg ran with libavcodec's automatic thread count, which libavcodec caps at min(logical CPUs + 1, 16) (MAX_AUTO_THREADS 16 in current FFmpeg master pthread_internal.h / pthread_frame.c; the FFmpeg version used is not stated), so most likely 16 threads on this machine. All-thread rows were unpinned on a machine 17% busy, with a byte-identical control spread of up to 4.0% in all-thread fps and a stated +-5% drift between sessions (wpp10.265 moved from 0.96x to 1.02x single-thread with no code change). Single-threaded, H.265 is at parity or slower (1.02x and 1.12x libavcodec's CPU time) and H.264 costs 1.46-1.55x; the H.264 all-thread gains (+2.4%, +1.7%) are inside the noise floor and the non-WPP H.265 clip is 7.1% slower. The comparison is ffmpeg CLI (demux plus rawvideo output to the null device) against the h26xdec example binary, not library against library. Output equivalence: both are normative decoders and rivet is bit-exact on the JVT and JCT-VC conformance suites and against JM/HM, so equal output is expected, but the benchmark itself did not compare outputs with libavcodec. The libavcodec rows are a 2026-09 record that the current tooling cannot regenerate, and the clips are not published. Open Encoding Attribution License v1.0 is source-available, not OSI (it says so itself: commercial attribution duty, field-of-use discrimination, not GPL-compatible), so usability is reference.

Pure-Rust H.264 and H.265 decoders (no C, no build script, one dependency) with frame and wavefront threading and a run-time SSE2-to-AVX-512 and NEON kernel ladder; bit-exact on 204 JVT and 196 JCT-VC conformance streams; also an in-progress encoder. Source-available licence with an attribution requirement, so it is not freely copyable under an OSI licence.

## Maintenance

Actively developed by one author (515 commits, last 2026-10-03, moved from rivet-transcoder to safewords), 0 stars and no crates.io release; source-available Open Encoding Attribution License, so reference only, and the libavcodec comparison can no longer be regenerated by the current tooling.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README tables (AMD Ryzen 9 9950X) generated by tools/benchmark.py as it stood at cc9195a, which ran the ffmpeg CLI against the h26xdec example; that code is public in history, but the FFmpeg version and build, rustc version and flags are not stated, the Big Buck Bunny benchmark clips are not in the repo, and the current benchmark.py (6eb41d8) no longer runs FFmpeg, so the libavcodec rows cannot be regenerated: C.
- **Verifier notes:** README numbers match the record; I corrected the frame count of hevc6.265 (1446, not 1200) and the repo's new home (safewords). The key addition is the thread asymmetry on the one winning cell (rivet 32 threads and 1.75x CPU vs libavcodec's capped auto threads), found by reading the pre-6eb41d8 tools/benchmark.py and FFmpeg's thread code.
- **Fields the verifier corrected:** `benchmark_url`, `workload`, `compiler_and_flags`, `hardware`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/rivet-transcoder/rivet-h26x-codecs/HEAD/README.md>
  - <https://github.com/rivet-transcoder/rivet-h26x-codecs>
  - <https://github.com/safewords/rivet-h26x-codecs/commits/develop>
  - <https://github.com/safewords/rivet-h26x-codecs/commits/develop/tools/benchmark.py>
  - <https://raw.githubusercontent.com/safewords/rivet-h26x-codecs/HEAD/tools/benchmark.py>
  - <https://raw.githubusercontent.com/safewords/rivet-h26x-codecs/cc9195a/tools/benchmark.py>
  - <https://raw.githubusercontent.com/safewords/rivet-h26x-codecs/HEAD/tools/README.md>
  - <https://raw.githubusercontent.com/safewords/rivet-h26x-codecs/HEAD/LICENSE.md>
  - <https://raw.githubusercontent.com/safewords/rivet-h26x-codecs/HEAD/Cargo.toml>
  - <https://crates.io/api/v1/crates/rivet-h26x>
  - <https://raw.githubusercontent.com/FFmpeg/FFmpeg/master/libavcodec/pthread_internal.h>
  - <https://raw.githubusercontent.com/FFmpeg/FFmpeg/master/libavcodec/pthread_frame.c>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/safewords/rivet-h26x-codecs/HEAD/README.md>
  - <https://raw.githubusercontent.com/safewords/rivet-h26x-codecs/cc9195a/README.md>
  - <https://raw.githubusercontent.com/safewords/rivet-h26x-codecs/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/safewords/rivet-h26x-codecs/HEAD/LICENSE.md>
  - <https://raw.githubusercontent.com/safewords/rivet-h26x-codecs/HEAD/tools/benchmark.py>
  - <https://raw.githubusercontent.com/safewords/rivet-h26x-codecs/cc9195a/tools/benchmark.py>
  - <https://raw.githubusercontent.com/safewords/rivet-h26x-codecs/HEAD/tools/README.md>
  - <https://raw.githubusercontent.com/safewords/rivet-h26x-codecs/HEAD/examples/h26xdec.rs>
  - <https://raw.githubusercontent.com/safewords/rivet-h26x-codecs/cc9195a/examples/h26xdec.rs>
  - <https://raw.githubusercontent.com/safewords/rivet-h26x-codecs/HEAD/src/picture.rs>
  - <https://raw.githubusercontent.com/safewords/rivet-h26x-codecs/cc9195a/src/picture.rs>
  - <https://raw.githubusercontent.com/safewords/rivet-h26x-codecs/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/safewords/rivet-h26x-codecs/HEAD/src/threading.rs>
  - <https://github.com/safewords/rivet-h26x-codecs>
  - <https://github.com/safewords/rivet-h26x-codecs/commits/develop/tools/benchmark.py>
  - <https://github.com/safewords/rivet-h26x-codecs/issues?q=is%3Aissue>
  - <https://github.com/safewords/rivet-h26x-codecs/pulls?q=is%3Apr>
  - <https://raw.githubusercontent.com/FFmpeg/FFmpeg/master/libavcodec/pthread.c>
  - <https://raw.githubusercontent.com/FFmpeg/FFmpeg/master/libavcodec/pthread_internal.h>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/rivet-transcoder/rivet-h26x-codecs`) · [data/wave10/enrich/raw/github_com_rivet_transcoder_rivet_h26x_codecs.json](../../../data/wave10/enrich/raw/github_com_rivet_transcoder_rivet_h26x_codecs.json) (enrichment confidence 0.75)

</details>
