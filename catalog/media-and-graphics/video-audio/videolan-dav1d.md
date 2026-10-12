# dav1d

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Video and audio](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `BSD-2-Clause` · 🟢 active

> VideoLAN's BSD-2 AV1 decoder in C and assembly; about 3x the 4K60 decode rate of libaom at equal thread counts.

| | |
|---|---|
| **Beats** | libaom (AV1 reference decoder) |
| **Claimed result** | OvenMediaEngine PR #2336 (libaom 3.12.0 vs dav1d 1.5.4, max decode rate, 4K60 AV1): game clip 22.3 vs 74.7 fps at 4 threads (3.3x) and 26.0 vs 74.1 fps at 6 threads (2.9x); camera clip 20.2 vs 61.1 fps at 4 threads (3.0x) and 22.1 vs 67.6 fps at 6 threads (3.1x). The PR summarises 'about 3x faster at the same thread count'. Snippet only (blog/medium pages not opened): single-threaded 1.5-2.5x and multi-threaded 2.3-4.5x faster than libaom. |
| **Workload** | Decoding 3840x2160 60 fps AV1 (about 10 Mbps, low-delay P) clips, 'game' (1200 frames) and 'camera' (1094 frames), at 4 to 6 threads, measured by a third party in a pull request to OvenMediaEngine. |
| **Metric** | throughput |
| **Hardware** | 2x Intel Xeon Silver 4114 @ 2.20 GHz (20C/40T, AVX2/AVX-512), 48 GB DDR4-2400, Ubuntu 22.04.5, performance governor |
| **Adoption** | 807 stars on the GitHub mirror (canonical repo is code.videolan.org/videolan/dav1d); decoder widely used via FFmpeg (libdav1d) |
| **Last commit** | 2026-09-30 |
| **Links** | [repository](https://github.com/videolan/dav1d) · [benchmark](https://github.com/OvenMediaLabs/OvenMediaEngine/pull/2336) |

## Verdict

One independent run, in merged OvenMediaEngine PR #2336: FFmpeg 7.1.5 libavcodec wrappers around dav1d 1.5.4 and libaom 3.12.0, both release builds with nasm assembly, on 2x Xeon Silver 4114 (Skylake-SP, so dav1d used its AVX2 code), 48 GB DDR4-2400, Ubuntu 22.04.5, kernel 6.8, performance governor. On two private 3840x2160 60 fps, about 10 Mbps low-delay P clips, the maximum decode rate (median of 3 runs) was 2.9-3.3x libaom's at the same 4 and 6 threads (for example 74.7 vs 22.3 fps). Part of the gap is the threading model, since libaom gained only 22.3 to 26.0 fps going from 4 to 6 threads; no single-thread ratio was published.

## Use it when

- Software AV1 playback or transcoding on CPUs or devices without an AV1 hardware decoder, especially 4K or high frame rate: the measured run reached 61-77 fps at 4K60 on 4-6 threads of a 2017 Xeon Silver, where libaom stayed at 20-26 fps.
- Any FFmpeg-based pipeline that still decodes AV1 with libaom-av1: switching the decoder name to libdav1d is the whole change, as OvenMediaEngine's PR did.
- Live or low-latency ingest: cap max_frame_delay (1 or 2) to bound latency and still get most of the multithreaded throughput (the PR measured p50 33.4 ms and p99 70-115 ms at 6 threads with delay 2).
- Embedding in proprietary products, drivers or mobile apps where a permissive license and small stack (62 KB on x86-64, 58 KB on ARM per NEWS 1.5.1) matter.
- ARM phones and SBCs, where it has NEON assembly for both 8-bit and high bit depth.

## Skip it when

- Encoding: dav1d has no encoder. Use SVT-AV1, libaom or rav1e for that.
- When a hardware AV1 decoder is available and power draw or CPU budget matters more than portability: hardware decode beats any software decoder there.
- Old x86 CPUs without SSSE3: release 1.5.0 removed some SSE2 code paths, so they run more C code.
- Memory-safety requirements that rule out C and hand-written assembly in the media path: consider the Rust port rav1d, accepting that it is slower.
- Untrusted input without limits: past CVEs include a thread_task.c race (CVE-2023-32570, fixed in 1.2.0) and an integer overflow on very large frames with multiple threads (CVE-2024-1580, fixed in 1.4.0). Stay on current releases and set frame_size_limit.

## How it is fast

Every DSP stage (motion compensation, inverse transforms, intra prediction, deblocking, CDEF, loop restoration, film grain, palette, ref-MV projection) has hand-written assembly per ISA: x86 SSE2/SSSE3/SSE4.1, AVX2 and AVX-512 (Ice Lake feature set), ARMv7/ARMv8 NEON with DotProd, i8mm and SVE2 variants, plus RISC-V, LoongArch and Power9 paths, picked at runtime by CPU detection. The multi-symbol arithmetic decoder (msac) that reads every coefficient also has assembly versions (x86/msac.asm, arm/64/msac.S). Since 1.0 one worker pool runs a dependency-tracked task graph across several frames in flight (n_fc frame contexts), tiles and superblock rows, covering entropy decoding, reconstruction, deblock, CDEF, super-resolution, loop restoration and film grain as separate tasks (src/thread_task.c), so it can use more threads than a stream has tiles. libaom's decoder has a single frame worker with tile and row multithreading only.

## Compared with alternatives

Pick dav1d over rav1d-safe, the catalogued Rust port, whenever raw decode speed matters: rav1d-safe only beats rav1d with assembly disabled, and both trail dav1d's assembly build. SVT-AV1 and rusty-av1-toolkit are encoders, so they complement dav1d rather than compete with it.

## Integration

| | |
|---|---|
| **Form** | static or shared lib (Meson + Ninja) |
| **Dependencies** | none at run time (pthreads or Win32 threads); build needs Meson 0.54+, Ninja and nasm 2.14+ for x86 assembly |
| **Minimum toolchain** | C99 compiler (meson.build sets c_std=c99), Meson 0.54+, nasm 2.14+ on x86 |
| **Platforms** | x86 and x86-64 (SSE2 through AVX2; AVX-512 kernels only on x86-64 with Ice Lake-class extensions), ARMv7 and AArch64 (NEON, DotProd, i8mm, SVE2), RISC-V, LoongArch, ppc64le, wasm and generic C elsewhere; Linux, Windows, macOS, Android, iOS, BSDs, OS/2 |
| **Thread safety** | Not documented in dav1d.h. Each Dav1dContext runs its own worker threads internally, and the API is written for one caller per context. Separate contexts are independent. |
| **Drop-in for the baseline** | partial: through FFmpeg it is a decoder-name swap (libaom-av1 to libdav1d); the native API (dav1d_send_data/dav1d_get_picture, Dav1dPicture) differs from libaom's aom_codec_decode/aom_codec_get_frame |

## Gotchas

- max_frame_delay defaults to ceil(sqrt(n_threads)) (at most 8), which buffers that many frames of latency. FFmpeg's wrapper forces 1 under AV_CODEC_FLAG_LOW_DELAY, and with thread_count 0 it starts cpu_count\*3/2 threads.
- The AVX-512 kernels need the Ice Lake feature set (VBMI2, GFNI, VNNI, BITALG and others; see src/x86/cpu.c). Skylake-SP parts, including the Xeon Silver 4114 in the measured run, use the AVX2 paths.
- Film grain is applied by default (apply_grain=1). Calling dav1d_apply_grain() on such a picture applies the grain twice.
- Meson refuses MemorySanitizer builds with assembly enabled (false positives), so sanitize with -Denable_asm=false. Each worker thread gets a 1 MB stack plus TLS.

## Known shortcomings

- Tier B on an independent third-party measurement (OvenMediaEngine PR #2336, merged, no VideoLAN tie; CPU, versions and thread counts stated; 2.9x-3.3x over libaom across 4 rows). No script or compiler flags, the test clips are private, and dav1d ran with max_frame_delay=2 through FFmpeg. dav1d's own repo publishes no libaom numbers. B rests on the catalog's 'independent measurement' rule; the stricter reading (well-known suite) would keep C.
- The PR build recipe is public after all (dav1d meson --buildtype=release with nasm 2.15.05, libaom 3.12.0 CMake forced Release with ENABLE_NASM, FFmpeg 7.1.5; only the compiler version is unstated). The Xeon 4114 (Skylake-SP) lacks the AVX-512 features dav1d targets (Ice Lake), so the AVX2 paths ran; part of the 3x is the threading model (libaom tile and row multithreading only, 22.3 to 26.0 fps from 4 to 6 threads) with no single-thread ratio; the first table's frame delay is unstated and the delay-2 run (77.3/68.1 fps) is not slower. The record misread the PR's fallback: libaom-av1 is used only when FFmpeg lacks libdav1d. CVE-2023-32570 and CVE-2024-1580 fixed.

## Caveats and trade-offs

The numbers come from a third-party pull request description, not a benchmark suite: no script or exact command is linked, compiler flags and assembly settings are unstated, and the 'game' and 'camera' clips are not public. dav1d 1.5.4 was built with meson and used through FFmpeg (--enable-libdav1d) with max_frame_delay=2, a low-latency setting that limits frame threading; libaom's build options are not stated. Same thread counts (4 and 6) for both decoders. One old machine (2x Xeon Silver 4114, Skylake-SP). dav1d's README and NEWS carry no numbers against libaom; its checkasm --bench only compares its assembly against its own C code. The 1.5-2.5x / 2.3-4.5x figures are snippet only. Canonical repository is code.videolan.org/videolan/dav1d; the GitHub repo is a read-only mirror.

Decoder only. Hand-written assembly for x86 (SSSE3 and up, AVX2) and ARM (ARMv7, ARMv8); the README says it is written from scratch for speed, size and correctness. Snippet only: binary about one third the size of libaom's decoder.

## Maintenance

Very active: last commit 2026-09-30, with many SIMD optimization commits for x86 and AArch64 in September 2026; current release 1.5.4. It is BSD-2-Clause, the README calls it production-ready, and FFmpeg ships a libdav1d wrapper. The GitHub repo is a read-only mirror, and issues and merge requests live on code.videolan.org, which was unreachable from this session.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now B.
- **Tier reason:** Upgraded C to B: the numbers are an independent measurement (Keukhan of OvenMediaEngine, no VideoLAN affiliation; PR #2336 merged) against libaom 3.12.0's decoder with the CPU model, RAM, OS, governor, decoder versions, thread counts and clips stated. Not A: no benchmark script or command is public, compiler and flags are unstated, and the clips are not published; dav1d's own repo (README, NEWS) carries no numbers against libaom.
- **Verifier notes:** Opened the PR: all four rows and the hardware match (record listed two). Searched for a public dav1d-vs-libaom number with hardware in dav1d's repo (none) and elsewhere (Phoronix/OpenBenchmarking runs compare dav1d with libgav1 or alone, and medium/Phoronix are blocked); the PR is the only openable independent source, so B per the orchestrator's 'independent measurement' rule. Metadata confirmed: BSD-2-Clause, 807 stars, last commit 2026-09-30, mirror not fork.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/OvenMediaLabs/OvenMediaEngine/pull/2336>
  - <https://raw.githubusercontent.com/videolan/dav1d/HEAD/README.md>
  - <https://raw.githubusercontent.com/videolan/dav1d/HEAD/NEWS>
  - <https://raw.githubusercontent.com/videolan/dav1d/HEAD/COPYING>
  - <https://github.com/videolan/dav1d>
  - <https://github.com/videolan/dav1d/commits>
  - <https://github.com/meta-pytorch/torchcodec/pull/728>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/videolan/dav1d/HEAD/README.md>
  - <https://raw.githubusercontent.com/videolan/dav1d/HEAD/NEWS>
  - <https://raw.githubusercontent.com/videolan/dav1d/HEAD/meson.build>
  - <https://raw.githubusercontent.com/videolan/dav1d/HEAD/meson_options.txt>
  - <https://raw.githubusercontent.com/videolan/dav1d/HEAD/include/dav1d/dav1d.h>
  - <https://raw.githubusercontent.com/videolan/dav1d/HEAD/include/dav1d/picture.h>
  - <https://raw.githubusercontent.com/videolan/dav1d/HEAD/src/lib.c>
  - <https://raw.githubusercontent.com/videolan/dav1d/HEAD/src/thread_task.c>
  - <https://raw.githubusercontent.com/videolan/dav1d/HEAD/src/internal.h>
  - <https://raw.githubusercontent.com/videolan/dav1d/HEAD/src/msac.h>
  - <https://raw.githubusercontent.com/videolan/dav1d/HEAD/src/meson.build>
  - <https://raw.githubusercontent.com/videolan/dav1d/HEAD/src/x86/cpu.c>
  - <https://raw.githubusercontent.com/videolan/dav1d/HEAD/tools/dav1d_cli_parse.c>
  - <https://raw.githubusercontent.com/videolan/dav1d/HEAD/doc/PATENTS>
  - <https://github.com/videolan/dav1d/commits>
  - <https://github.com/advisories?query=dav1d>
  - <https://github.com/OvenMediaLabs/OvenMediaEngine/pull/2336>
  - <https://github.com/OvenMediaLabs/OvenMediaEngine/pull/2336/files>
  - <https://raw.githubusercontent.com/OvenMediaLabs/OvenMediaEngine/HEAD/cmake/InstallPrerequisites.cmake>
  - <https://raw.githubusercontent.com/OvenMediaLabs/OvenMediaEngine/HEAD/cmake/Versions.cmake>
  - <https://raw.githubusercontent.com/OvenMediaLabs/OvenMediaEngine/HEAD/src/transcoder/codec/decoder/decoder_avcodec_video.cpp>
  - <https://raw.githubusercontent.com/FFmpeg/FFmpeg/release/7.1/libavcodec/libdav1d.c>
  - <https://raw.githubusercontent.com/FFmpeg/FFmpeg/release/7.1/libavcodec/libaomdec.c>
  - <https://gitlab.com/webmproject/libaom/-/raw/v3.12.0/CMakeLists.txt>
  - <https://gitlab.com/webmproject/libaom/-/raw/v3.12.0/build/cmake/aom_configure.cmake>
  - <https://gitlab.com/webmproject/libaom/-/raw/v3.12.0/av1/av1_dx_iface.c>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/videolan/dav1d`) · [data/wave10/enrich/raw/github_com_videolan_dav1d.json](../../../data/wave10/enrich/raw/github_com_videolan_dav1d.json) (enrichment confidence 0.85)

</details>
