# oss-nvjpg

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `GPL-3.0` · 🟡 stale

> C++20 driver for the Tegra X1 NVJPG hardware JPEG decoder; README shows 3-4x lower latency than libjpeg-turbo on the A57 cores.

| | |
|---|---|
| **Beats** | libjpeg-turbo |
| **Claimed result** | NVJPG hardware decoder: 2.036 ms vs libjpeg-turbo 6.127 ms (70 KiB image) and 15.997 ms vs 66.341 ms (1.6 MiB image); ratios about 3.0x and 4.1x (derived from page data). Also listed: stb_image with NEON 16.512 and 158.474 ms, Python-pillow 11.688 and 114.918 ms, nanoJPEG 48.299 and 531.575 ms. |
| **Workload** | Baseline JPEG decode to an RGB surface, 720x1080 (70 KiB file) and 3200x1800 (1.6 MiB file), average of 1000 iterations, on a Tegra X1 (Aarch64 Cortex-A57 at 2.091 GHz). |
| **Metric** | latency |
| **Hardware** | Nvidia Tegra X1 SoC, Aarch64 Cortex-A57 at max 2.091 GHz, using the SoC's NVJPG hardware JPEG block for oss-nvjpg and the A57 CPU cores for libjpeg-turbo and the other software decoders. The Makefile targets Nintendo Switch homebrew (libnx, deko3d), so the board is likely a Switch, but the README does not say. |
| **Compiler and flags** | Not stated for the table. The repo builds with meson (buildtype=release, gnu++20) on Linux or a devkitA64 Makefile (-O2 -march=armv8-a+crc+crypto+simd -mtune=cortex-a57) for Switch homebrew; libjpeg-turbo, stb_image, Pillow and nanoJPEG versions and build options are not stated. |
| **Adoption** | 19 stars, 3 forks |
| **Last commit** | 2025-06-18 |
| **Links** | [repository](https://github.com/averne/oss-nvjpg) · [benchmark](https://github.com/averne/oss-nvjpg) |

## Verdict

First-party README table: one image decoded to an RGB surface, averaged over 1000 iterations, on a Tegra X1 with its Cortex-A57 at max 2.091 GHz; NVJPG 2.036 ms vs libjpeg-turbo 6.127 ms for a 70 KiB 720x1080 file and 15.997 vs 66.341 ms for a 1.6 MiB 3200x1800 file (about 3.0x and 4.1x, derived from page data). The table was already in the README by 2021-02-08, before the Horizon port (2021-03-08), the hardware-definition corrections and both 2025 fixes, so it was measured on the early Linux build and never re-run; the timing harness, libjpeg-turbo version and build, NVJPG clock rate and timed region are not published (the shipped examples time one render plus wait, i.e. scan copy plus hardware decode, after header parsing).

## Use it when

- Nintendo Switch homebrew (devkitA64, libnx) that loads many baseline JPEG icons, thumbnails or screenshots and wants the Cortex-A57 cores free; the Switch menu sphaira uses it (issue #1).
- Tegra X1 boards running NVIDIA's L4T kernel, where /dev/nvhost-nvjpg, /dev/nvhost-ctrl and /dev/nvmap exist and you need lower per-image decode latency than libjpeg-turbo on the A57 (README: about 3x on a 720x1080 file, about 4x on 3200x1800).
- Pipelines that hand the decoded image straight to the GPU: Surface::to_deko3d wraps the output buffer as a deko3d texture without a copy.
- Thumbnail generation where hardware downscale by 2, 4 or 8 and hardware YUV-to-RGB conversion replace CPU passes.

## Skip it when

- Any hardware other than the Tegra X1: it programs the NVJPG engine directly, and on Linux it needs NVIDIA's downstream nvhost/nvmap UAPI, not mainline host1x.
- Progressive, arithmetic-coded or lossless JPEGs, CMYK or other 4-component files, and files whose component ids are 4 or higher (Adobe-style 'R','G','B' ids) all return an error.
- Untrusted input: the header parser does not bound DHT symbol counts or table ids (see gotchas), so a malformed file can write past fixed-size arrays.
- Workloads that read decoded pixels back on the CPU: surfaces are allocated non-CPU-cacheable, which suits GPU consumers but makes CPU reads slow.
- Projects that cannot take GPL-3.0 code, or that need active maintenance: the only changes since 2022 are two 2025 fixes prompted by one downstream user.

## How it is fast

The CPU only parses the JPEG headers, copies the entropy-coded scan data into a DMA buffer and fills a 0xb2c-byte picture-info block (Huffman and quantization tables, sampling, pitches); Huffman decoding, IDCT, chroma upsampling, YUV-to-RGB conversion (fixed-point BT.601, BT.709 or full-range JFIF kernels) and power-of-two downscaling (1/2, 1/4, 1/8) all run in the NVJPG hardware. Work is submitted as a Host1x command buffer and completion is signalled by a syncpoint fence, and Decoder::initialize(num_ring_entries) keeps a ring of submission slots so the CPU can parse and queue the next image while the hardware decodes. The speedup comes from dedicated silicon, not from a better software algorithm.

## Compared with alternatives

Pick it over libjpeg-turbo, jpeg-nitro or zenjpeg only when you are on Tegra X1 (Switch or L4T) with trusted baseline JPEGs and want the decode off the CPU; those siblings are portable CPU decoders, and GPUJPEG targets CUDA GPUs, not the X1's NVJPG block.

## Integration

| | |
|---|---|
| **Form** | static lib (meson default_library=static, or libnvjpg.a from the devkitA64 Makefile) |
| **Dependencies** | Linux: NVIDIA L4T kernel device nodes /dev/nvmap, /dev/nvhost-ctrl, /dev/nvhost-nvjpg (SDL2 only for the examples). Switch: libnx (nvdrv and mmu services), deko3d optional for the texture-export path and examples. |
| **Minimum toolchain** | C++20 (gnu++20; uses concepts, requires-clauses and the GNU case-range extension), so GCC with GNU extensions; devkitA64 for Switch, meson for Linux |
| **Platforms** | aarch64 Tegra X1 only (Nintendo Switch under Horizon with libnx, or Tegra X1 under NVIDIA L4T Linux) |
| **Thread safety** | not documented; nvmap and nvhost-ctrl file descriptors are process-wide statics and a Decoder's ring iterator is unsynchronized, so use one Decoder per thread |
| **Drop-in for the baseline** | no |

## Gotchas

- Parser memory safety (lib/image.cpp): parse_dht reads sum(codes) symbols, up to 4080, into a 162-byte array and indexes 4-entry table arrays with a 4-bit id (up to 15); parse_dqt does the same for quantization ids; table ids from SOF and SOS are never range-checked. parse_dqt also computes precision as `info >> 8` on a uint8_t, which is always 0, so 16-bit quantization tables are misread. Image(path) opens a file descriptor that is never closed, and a short read() is not detected.
- History: component ids were assumed 1-based until commit 16c10a3 (2025-06-09, issue #1: a 4:4:4 Switch icon decoded to garbage), and parse() could loop forever on non-JPEG input until PR #2 (2025-06-18). In that PR the author says his FFmpeg 'envideo' hwaccel (averne/FFmpeg, envideo_mjpeg.c) 'handles surface formats correctly, aborts on some hardware issues', which this library does not.
- The scan-data buffer defaults to 5 MiB per ring entry (Decoder::initialize capacity 0x500000); larger scans fail with ENOMEM until Decoder::resize is called. Output pitch is aligned to 256 bytes, so rows are not tightly packed.
- On Switch, nj::initialize() temporarily sets __nx_applet_type to LibraryApplet to obtain nvdrv:a/s/t, and on Linux NJ_TRY_ERRNO tests errno without clearing it first, so a stale errno from an earlier unrelated call makes initialize fail.

## Known shortcomings

- Different hardware: the Tegra X1 NVJPG block (likely a Nintendo Switch per the Makefile) against software libjpeg-turbo on its Cortex-A57 cores; the README table is the only evidence, the examples time one NVJPG render and never call libjpeg-turbo, and no flags or libjpeg-turbo version are given. Stale since 2025-06-18.
- Enricher (2026-10-04): the README table (NVJPG 2.036 vs libjpeg-turbo 6.127 ms, 15.997 vs 66.341 ms, about 3.0x and 4.1x derived from page data) was in the README by 2021-02-08, before the Horizon port, hardware-definition corrections and both 2025 correctness fixes, and was never re-run; harness, libjpeg-turbo build, NVJPG clock and timed region are unpublished. Security: the parser (lib/image.cpp) is unsafe on untrusted files: parse_dht reads up to 4080 symbols into a 162-byte array and indexes 4-entry tables with a 4-bit id, parse_dqt likewise, table ids from SOF/SOS are never range-checked, parse_dqt computes precision as info &gt;&gt; 8 on a uint8_t (always 0, so 16-bit tables are misread), and Image(path) leaks the file descriptor. History: 1-based component-id assumption until 16c10a3 (2025-06-09, issue #1), infinite loop on non-JPEG input until PR #2. Tegra X1 only (libnx or L4T kernel); GPL-3.0; stale since 2025-06-18.

## Caveats and trade-offs

First-party README table only; the 1000-iteration averaging harness and the libjpeg-turbo, stb_image, Pillow and nanoJPEG runs are not in the repo. The shipped examples (examples/render-rgb.cpp, render-nx.cpp and others) time one decoder.render plus decoder.wait after the file is read and the JPEG headers are parsed, into an RGBA surface, so it is unknown whether the software timings cover the same steps. No compiler, flags or libjpeg-turbo version (or whether its NEON paths were enabled) are stated. Two test images only. This compares a fixed-function hardware decoder on the Tegra X1 against software decoders on its Cortex-A57 cores: the speedup (about 3.0x and 4.1x, derived from page data) comes from dedicated hardware, does not transfer to other SoCs, and frees the CPU rather than proving a faster algorithm. Baseline JPEGs only; progressive and arithmetic-coded files return an error. GPL-3.0.

Drives the Tegra X1 hardware JPEG block (NVJPG) through the Host1x interface, so it only runs on Tegra X1 class devices (for example Nintendo Switch homebrew with devkitA64). Baseline JPEG only: progressive and arithmetic coded files return an error. Hardware YUV to RGB conversion and downscaling by up to 8. Requires C++20. GPL-3.0 limits reuse in permissive projects.

## Maintenance

Stale since 2025-06-18 (23 commits, 19 stars, no open issues or PRs); about 1.5k lines of GPL-3.0 C++20 that can be vendored, but it only runs on Tegra X1 with libnx or NVIDIA's downstream L4T kernel, and its parser should not see untrusted files.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** Only a first-party README table (Tegra X1, Cortex-A57 at max 2.091 GHz, average of 1000 iterations). The repo ships no comparison harness: examples/render-\*.cpp time a single NVJPG render with std::chrono and never call libjpeg-turbo, and no compiler, flags or libjpeg-turbo version are given for the table.
- **Verifier notes:** README numbers match the record exactly (NVJPG 2.036 / 15.997 ms vs libjpeg-turbo 6.127 / 66.341 ms). Last commit 2025-06-18 (about 15 months), so stale is right.
- **Fields the verifier corrected:** `compiler_and_flags`, `hardware`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** first-party README table
- **Pages the verifier opened:**
  - <https://github.com/averne/oss-nvjpg>
  - <https://github.com/averne/oss-nvjpg/commits>
  - <https://github.com/averne/oss-nvjpg/tree/master/examples>
  - <https://raw.githubusercontent.com/averne/oss-nvjpg/HEAD/README.md>
  - <https://raw.githubusercontent.com/averne/oss-nvjpg/HEAD/meson.build>
  - <https://raw.githubusercontent.com/averne/oss-nvjpg/HEAD/Makefile>
  - <https://raw.githubusercontent.com/averne/oss-nvjpg/HEAD/examples/render-rgb.cpp>
  - <https://raw.githubusercontent.com/averne/oss-nvjpg/HEAD/examples/render-nx.cpp>
  - <https://raw.githubusercontent.com/averne/oss-nvjpg/HEAD/examples/render-yuv.cpp>
  - <https://raw.githubusercontent.com/averne/oss-nvjpg/HEAD/examples/render-rgb-downscale.cpp>
  - <https://raw.githubusercontent.com/averne/oss-nvjpg/HEAD/examples/render-icons.cpp>
  - <https://raw.githubusercontent.com/averne/oss-nvjpg/HEAD/examples/render-deko3d.cpp>
- **Sources the enricher read:**
  - <https://github.com/averne/oss-nvjpg>
  - <https://github.com/averne/oss-nvjpg/commits/master>
  - <https://github.com/averne/oss-nvjpg/tree/master/include/nvjpg>
  - <https://github.com/averne/oss-nvjpg/tree/master/include/nvjpg/nv>
  - <https://github.com/averne/oss-nvjpg/commit/16c10a3>
  - <https://github.com/averne/oss-nvjpg/commit/c0b3b8f>
  - <https://github.com/averne/oss-nvjpg/commit/4935f53>
  - <https://github.com/averne/oss-nvjpg/issues/1>
  - <https://github.com/averne/oss-nvjpg/pull/2>
  - <https://github.com/averne/FFmpeg/blob/envideo/libavcodec/envideo_mjpeg.c>
  - <https://raw.githubusercontent.com/averne/oss-nvjpg/HEAD/README.md>
  - <https://raw.githubusercontent.com/averne/oss-nvjpg/HEAD/meson.build>
  - <https://raw.githubusercontent.com/averne/oss-nvjpg/HEAD/Makefile>
  - <https://raw.githubusercontent.com/averne/oss-nvjpg/HEAD/include/nvjpg.hpp>
  - <https://raw.githubusercontent.com/averne/oss-nvjpg/HEAD/include/nvjpg/bitstream.hpp>
  - <https://raw.githubusercontent.com/averne/oss-nvjpg/HEAD/include/nvjpg/decoder.hpp>
  - <https://raw.githubusercontent.com/averne/oss-nvjpg/HEAD/include/nvjpg/image.hpp>
  - <https://raw.githubusercontent.com/averne/oss-nvjpg/HEAD/include/nvjpg/surface.hpp>
  - <https://raw.githubusercontent.com/averne/oss-nvjpg/HEAD/include/nvjpg/utils.hpp>
  - <https://raw.githubusercontent.com/averne/oss-nvjpg/HEAD/include/nvjpg/nv/channel.hpp>
  - <https://raw.githubusercontent.com/averne/oss-nvjpg/HEAD/include/nvjpg/nv/cmdbuf.hpp>
  - <https://raw.githubusercontent.com/averne/oss-nvjpg/HEAD/include/nvjpg/nv/ctrl.hpp>
  - <https://raw.githubusercontent.com/averne/oss-nvjpg/HEAD/include/nvjpg/nv/map.hpp>
  - <https://raw.githubusercontent.com/averne/oss-nvjpg/HEAD/include/nvjpg/nv/registers.hpp>
  - <https://raw.githubusercontent.com/averne/oss-nvjpg/HEAD/lib/decoder.cpp>
  - <https://raw.githubusercontent.com/averne/oss-nvjpg/HEAD/lib/image.cpp>
  - <https://raw.githubusercontent.com/averne/oss-nvjpg/HEAD/lib/surface.cpp>
  - <https://raw.githubusercontent.com/averne/oss-nvjpg/HEAD/examples/render-rgb.cpp>
  - <https://raw.githubusercontent.com/averne/oss-nvjpg/HEAD/examples/render-nx.cpp>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/averne/oss-nvjpg`) · [data/wave10/enrich/raw/github_com_averne_oss_nvjpg.json](../../../data/wave10/enrich/raw/github_com_averne_oss_nvjpg.json) (enrichment confidence 0.75)

</details>
