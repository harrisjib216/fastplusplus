# rusty_h265

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Video and audio](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0` · 🟢 active

> Pure-Rust, memory-safe HEVC decoder: about 5% faster than FFmpeg's hevc decoder on one stream, 1.1-1.67x slower on three.

| | |
|---|---|
| **Beats** | FFmpeg 8.1.2 native hevc decoder (libavcodec, hand-written assembly) |
| **Claimed result** | Single core, FFmpeg 8.1.2 native hevc decoder at -threads 1, rusty_h265 0.6.0: weighted-prediction stream 703 ms vs FFmpeg 741 ms (1.05x faster, 21/21 pairs, z = +4.58); deblocking-heavy 744 vs 675 ms (0.91x, FFmpeg 1.10x faster, 1/20); 720p 8-bit mainstream inter 447 vs 267 ms (0.60x, FFmpeg 1.67x faster); 720p 10-bit 445 vs 308 ms (0.69x, FFmpeg 1.45x faster, derived from page data). The README sums this up as 'between 1.05x FASTER and 1.67x slower than ffmpeg'. FFmpeg measured against itself: 0.992x. Release 0.6.0 is 1.024-1.158x faster than 0.5.0 (all-intra to deblocking-heavy). |
| **Workload** | Single-core decode of four unpublished HEVC streams (720p 8-bit mainstream inter, the same content in 10-bit, a deblocking-heavy stream, a weighted-prediction stream) with tools/bench/codec-bench.ps1: both processes pinned to one core at High priority, FFmpeg run with -threads 1 -f null - (harness default), ABBA-alternated, 21 pairs, paired win rate with z-score, frame counts checked against ffprobe, output discarded by both arms. rusty_h265 built with the bench-alloc feature (its own rusty_alloc global allocator). Timing compares unlike scopes: rusty_h265's self-reported decode_ms covers Annex-B splitting and decoding after the whole file is read into memory, while FFmpeg's -benchmark rtime covers its whole transcode loop (demuxer and parser, decoder, null-muxer pipeline threads sharing the one pinned core). |
| **Metric** | throughput |
| **Hardware** | Not stated; Windows host (PowerShell harness, ffmpeg.exe), one pinned core (default core 4) |
| **Compiler and flags** | Release profile opt-level 3, codegen-units 1, panic = abort; the default build targets portable x86-64 (SSE2) with runtime-dispatched SSE4.1/AVX2 kernels, and tools/build-v3.sh builds an optional x86-64-v3 artifact (1.066x faster); the README does not say which build produced the FFmpeg table. rustc version not stated or pinned (MSRV 1.85). FFmpeg 8.1.2 build provenance and configure flags not stated (a 242 MB ffmpeg.exe on Windows per the CHANGELOG). |
| **Adoption** | 2 stars; 10 commits; crates.io 520 downloads (checked 2026-10-04); the README banner claims 561 active installs (unverified) |
| **Last commit** | 2026-09-20 |
| **Links** | [repository](https://github.com/Remade-With-Rust/rusty_h265) · [benchmark](https://raw.githubusercontent.com/Remade-With-Rust/rusty_h265/HEAD/README.md) |

## Verdict

First-party run on an unnamed Windows machine, one pinned core, 21 ABBA-alternated pairs on four unpublished 720p-class streams: rusty_h265 0.6.0 (rusty_alloc build; portable or x86-64-v3 not stated) took 703 ms against 741 ms for FFmpeg 8.1.2's hevc decoder at -threads 1 on a weighted-prediction stream (1.05x), but took 1.10x, 1.45x and 1.67x as long on the deblocking-heavy, 10-bit and 8-bit mainstream streams. The two timers differ in scope: rusty_h265's decode_ms starts after the file is in memory, while ffmpeg's -benchmark rtime spans its whole transcode() with demuxer, decoder, filter and null-muxer threads sharing the one pinned core, so a 5% margin is within that bias.

## Use it when

- A Rust program that must decode HEVC without C, FFI or libavcodec's LGPL/GPL licensing; the crate is Apache-2.0 with no required third-party dependencies.
- Untrusted HEVC input where memory safety matters more than speed: the decoder core is #![forbid(unsafe_code)], and --no-default-features builds with no unsafe code anywhere (at about 2.8x lower speed).
- Main or Main 10 4:2:0 content where single-threaded decoding at roughly 0.6x to 1.05x of FFmpeg's single-thread speed is enough, e.g. thumbnailing, inspection or offline 720p work.
- Content heavy in explicit weighted prediction (fades), the only stream class measured at or above FFmpeg's speed.

## Skip it when

- Throughput-bound decoding: the pipeline is single-threaded (tiles and wavefronts are parsed but not run in parallel), and even on one core it is 1.45x to 1.67x slower than FFmpeg on mainstream 8- and 10-bit inter content.
- Range Extensions (4:2:2, 4:4:4, 12-bit), screen content coding, or SHVC/MV-HEVC enhancement layers (only the base layer is decoded).
- Debug-profile builds: open issue #3 (2026-09-30) reports that a debug_assert in rusty_h265-accel's luma_edge fires on horizontal edges at x &lt; 4, so every HEVC stream panics in a dev build; release builds stay correct by falling back to the scalar edge filter.
- 8-bit pipelines that are bound by memory bandwidth: every plane is stored as u16 (frame.rs calls an 8-bit u8 plane domain a future 'speed brick'), and converting to 8-bit output cost 5.4% of decode per the README.
- Production use that needs a track record: 0.1.0 to 0.6.0 were all published 2026-09-06 to 2026-09-08 by one organisation, with no independent users or measurements found.

## How it is fast

The pixel kernels (motion compensation, intra prediction, inverse DCT/DST, deblocking, SAO) live in a separate rusty_h265-accel crate with runtime-dispatched SSE2/SSE4.1/AVX2 versions, each differential-tested bit-exact against a scalar twin; the CHANGELOG measures them at 2.81x over scalar, with AVX2 only 1.045x over SSE4.1. CABAC fuses the LPS-range and state-transition tables into one branchless step. Most of the remaining gains are removed allocations and copies, found with a stage profiler and an assembly-level memcpy census: a picture-buffer pool that zeroes only coding tree blocks no slice covered, per-4x4 maps reused without pre-filling, sequence-invariant scan tables cached, and short copies dispatched to constant widths so they inline. The non-kernel code (about 87% of the time) builds for baseline x86-64 SSE2 unless you build with -C target-cpu=x86-64-v3 (1.066x).

## Compared with alternatives

Pick it over FFmpeg's libavcodec only when a pure-Rust, Apache-2.0, memory-safe HEVC decoder matters more than speed. If you need multicore throughput, rivet-h26x (also pure Rust, with frame and wavefront threading and single-thread parity on wavefront streams) fits better, provided you accept its source-available attribution licence. remade_ffmpeg_rs ships this same decoder.

## Integration

| | |
|---|---|
| **Form** | crate (rusty_h265 on crates.io, with the companion rusty_h265-accel kernel crate) |
| **Dependencies** | rusty_h265-accel (default simd feature); rusty_alloc-api =1.1.6 only with the optional bench-alloc feature used by the bundled CLI |
| **Minimum toolchain** | Rust 1.85 (MSRV), edition 2021 |
| **Platforms** | any Rust target on the scalar path; SIMD kernels runtime-dispatched SSE2/SSE4.1/AVX2 on x86-64 (the README also lists a NEON baseline rung); the optional x86-64-v3 build needs AVX2, BMI1/2 and FMA (Haswell or later) |
| **Thread safety** | not documented; one Decoder per stream, decoding runs on the calling thread, and reference pictures are Arc-shared with the output queue |
| **Drop-in for the baseline** | no |

## Gotchas

- The top-level README's Quick start calls dec.decode_nal(nal) and annex_b_nal_units(), which do not exist in 0.6.0; use push_annexb/push_nal, flush and next_frame as shown in the crate README and lib.rs docs.
- The published numbers use the bench-alloc build (rusty_alloc, a pure-Rust mimalloc remake), which the harness notes was measured 1.133x apart from the system allocator; a library user gets whatever global allocator the application uses.
- Debug builds panic on every stream (issue #3); until it is fixed, set debug-assertions off for this dependency or build it with an optimized profile.
- Frames are u16 planes at the coded size with a separate crop rectangle, so callers must apply cropping and narrow 8-bit samples themselves.

## Known shortcomings

- Marginal mixed result: 1.05x over FFmpeg on the weighted-prediction stream only; FFmpeg is faster on the other three (1.10x, 1.45x, 1.67x). Timers differ (decode_ms versus FFmpeg -benchmark rtime, which includes the demux and mux pipeline); the bench binary uses rusty_alloc (1.133x per the CHANGELOG); streams unpublished; CPU, rustc and FFmpeg build unstated; frame counts only, no MD5 against FFmpeg on the bench streams (conformance from 147 of 147 JCT-VC MD5s).
- The harness default RefArgs uses -v error without -benchmark while ffmpeg logs its bench rtime line at AV_LOG_INFO, so the published table needs unpublished arguments; the 0.992x null arm is wall clock ffmpeg against ffmpeg and cannot catch the decode_ms-versus-rtime scope bias. Issue #3: a debug_assert in the accel luma_edge path panics on every stream in debug builds (release falls back to scalar); the README quick start calls nonexistent decode_nal and annex_b_nal_units; planes are always u16; the README banner's 2,634 installs against crates.io's 520 downloads.

## Caveats and trade-offs

A marginal, mixed result: faster than FFmpeg on one of four streams by 5%, slower on the other three (1.10x, 1.45x and 1.67x). The 5% win is about the size of the measurement asymmetries: rusty_h265 reports its own internal decode time while FFmpeg's rtime includes its demuxer, parser and null-muxer pipeline threads contending for the same pinned core, and the benchmarked binary uses the project's rusty_alloc allocator, which the CHANGELOG says is worth 1.133x on this decoder and which library users do not get by default. The four streams are not in the repo, the CPU model, rustc version and FFmpeg build are unstated, and the README does not say whether the portable or x86-64-v3 build was timed. Output equivalence with FFmpeg on the benchmark streams is not checked (the harness only compares frame counts); correctness rests on 147/147 JCT-VC HEVC_v1 conformance streams matched by MD5 against the reference output and per-picture SEI hashes (first-party). The README says its earlier 0.5.0 numbers did not reproduce on re-measurement, and earlier harness versions had timing bugs (15.625 ms tick accounting, process start-up charged to FFmpeg, a system-allocator reference arm). Single-threaded only, Main/Main 10 4:2:0, no Range Extensions. Rust, not C++. The HEVC decoder component of remade_ffmpeg_rs (listed for MP3/AAC/Vorbis numbers only). README opens with an install-count banner and an advert.

Pure-Rust HEVC decoder with #![forbid(unsafe_code)] in the core and SIMD kernels isolated in rusty_h265-accel; decodes all 147 JCT-VC HEVC_v1 conformance streams byte-exact. Rust only, no stated C API; decoder only. Part of the Remade With Rust effort and the HEVC decoder inside remade_ffmpeg_rs.

## Maintenance

Active but very new: six releases between 2026-09-06 and 2026-09-08, and later commits only edit the README (its banner now claims 2,634 active installs against 520 total crates.io downloads); Apache-2.0 and copyable.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party numbers from a public harness (tools/bench/codec-bench.ps1) against FFmpeg 8.1.2's native hevc decoder, but the four benchmark streams are not published, and the CPU model, rustc version, FFmpeg build and the exact command lines are not stated, so not A; no independent measurement found.
- **Verifier notes:** Confirmed at C as a flagged, marginal partial win, per the batch note. Harness read in full: FFmpeg gets -threads 1 and the same pinned core, which is fair on threading, but the two timers cover different scopes and the reference stream set is unpublished, so the 1.05x is within plausible measurement bias. Not a duplicate of remade_ffmpeg_rs because that entry carries no HEVC numbers; the orchestrator may still want to cross-reference the two.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `hardware`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_h265/HEAD/README.md>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_h265/HEAD/tools/bench/codec-bench.ps1>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_h265/HEAD/tools/build-v3.sh>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_h265/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_h265/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_h265/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_h265/HEAD/crates/rusty_h265/Cargo.toml>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_h265/HEAD/crates/rusty_h265/src/bin/rusty_h265.rs>
  - <https://github.com/Remade-With-Rust/rusty_h265>
  - <https://github.com/Remade-With-Rust/rusty_h265/commits>
  - <https://github.com/Remade-With-Rust/rusty_h265/tree/main/tools>
  - <https://github.com/Remade-With-Rust/rusty_h265/tree/main/tools/bench>
  - <https://github.com/Remade-With-Rust/rusty_h265/tree/main/tools/hevc>
  - <https://crates.io/api/v1/crates/rusty_h265>
- **Sources the enricher read:**
  - <https://github.com/Remade-With-Rust/rusty_h265/commits>
  - <https://github.com/Remade-With-Rust/rusty_h265/issues>
  - <https://github.com/Remade-With-Rust/rusty_h265/issues/3>
  - <https://github.com/Remade-With-Rust/rusty_h264>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_h265/HEAD/README.md>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_h265/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_h265/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_h265/HEAD/tools/bench/codec-bench.ps1>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_h265/HEAD/tools/build-v3.sh>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_h265/HEAD/crates/rusty_h265/Cargo.toml>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_h265/HEAD/crates/rusty_h265/README.md>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_h265/HEAD/crates/rusty_h265/src/lib.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_h265/HEAD/crates/rusty_h265/src/bin/rusty_h265.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_h265/HEAD/crates/rusty_h265/src/decoder.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_h265/HEAD/crates/rusty_h265/src/frame.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_h265/HEAD/crates/rusty_h265/src/error.rs>
  - <https://raw.githubusercontent.com/FFmpeg/FFmpeg/master/fftools/ffmpeg.c>
  - <https://crates.io/api/v1/crates/rusty_h265>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/remade-with-rust/rusty_h265`) · [data/wave10/enrich/raw/github_com_remade_with_rust_rusty_h265.json](../../../data/wave10/enrich/raw/github_com_remade_with_rust_rusty_h265.json) (enrichment confidence 0.7)

</details>
