# GPUJPEG

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `BSD-2-Clause` · 🟢 active

> CUDA baseline-JPEG encoder/decoder doing DCT, quantization and restart-segmented Huffman coding on the GPU; no measured comparison against libjpeg-turbo or nvJPEG.

| | |
|---|---|
| **Beats** | none in the README; the only comparison found is against NVIDIA nvJPEG in two user issues (not libjpeg-turbo) |
| **Claimed result** | No comparative speedup is claimed. README timings only: encode 4K 1.65 ms on RTX 4080, 1.71 ms on RTX 3080, 2.89 ms on RTX 2080 Ti, 3.16 ms on AMD RX 7600 via ZLUDA; encode 8K 6.33 ms (RTX 4080) and 16K 24.92 ms; decode 4K 1.46 ms (RTX 4080) and 8K 5.78 ms; on RTX 3080 8K encode 6.21 ms at quality 70 and 2.28 ms without PCIe transfers. About 4.8 Gpix/s for 4K encode on RTX 4080 (derived from page data). |
| **Workload** | README: JPEG encode and decode time per frame for a 16K DCI source image cropped or downscaled to HD (2 Mpix), 4K (8 Mpix), 8K (33 Mpix) and 16K (132 Mpix), RGB input, quality 75, non-interleaved, restart interval 24-36, average of 99 runs excluding the first, gpujpegtool -n 100. |
| **Metric** | throughput |
| **Hardware** | NVIDIA RTX 4080, RTX 3080, RTX 2080 Ti, GTX 1060M, GTX 580 and AMD Radeon RX 7600 via ZLUDA; host CPU not stated |
| **Compiler and flags** | Recommended build cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_CUDA_ARCHITECTURES=native (optional -DUSE_NATIVE_CPU_ARCH=ON); the README says the RTX 4080 numbers were taken with cmake configured without those flags and that other measurements were made without a Release build type. CUDA toolkit and host compiler versions are not stated. |
| **Adoption** | 288 stars, 81 forks |
| **Last commit** | 2026-10-02 |
| **Links** | [repository](https://github.com/CESNET/GPUJPEG) · [benchmark](https://github.com/CESNET/GPUJPEG) |

## Verdict

Only absolute first-party times exist: gpujpegtool -n 100 on a 16K DCI frame scaled to HD-16K at quality 75, encode 4K 1.65 ms (RTX 4080) and 1.71 ms (RTX 3080), decode 4K 1.46 ms (RTX 4080), including PCIe copies and excluding the first iteration, with CUDA, driver and host CPU unstated and some rows built without Release flags; there is no CPU or nvJPEG baseline, hence tier D. One table cell looks wrong: RTX 2080 Ti decode is 1.02 ms at HD and 1.07 ms at 4K (four times the pixels) but 11.29 ms at 8K, and that 4K cell beats the RTX 4080's 1.46 ms.

## Use it when

- Real-time capture or streaming pipelines that encode many equal-sized HD to 16K frames per second on an NVIDIA GPU (README: about 1.7 ms per 4K frame and 6.2-6.3 ms per 8K frame on RTX 3080/4080 including PCIe copies).
- Frames already in CUDA or OpenGL memory, where skipping host transfers matters (8K q70 encode 2.28 ms without PCIe copies vs 6.21 ms with them on RTX 3080).
- Closed systems where GPUJPEG both writes and reads the JPEGs, so the restart markers and segment-info header that enable GPU Huffman decoding are always present (the UltraGrid-style use case).
- Batch tools that can keep one encoder or decoder alive across images to amortize the 28.6 ms (8K) to 87.1 ms (16K) first-frame initialization measured on RTX 3080.

## Skip it when

- Decoding arbitrary camera or web JPEGs: progressive and arithmetic-coded files are unsupported, and files without restart markers fall back to the CPU Huffman decoder (the FAQ shows a 600 ms foreign-JPEG decode dominated by a 543 ms stream reader).
- Choosing it as 'faster than libjpeg-turbo' or 'faster than nvJPEG' on the catalog's evidence: no such comparison exists in the repo, and the only cross-codec numbers (2020 issues #47/#48) are mixed (1.8x faster on a noise texture, 1.4x slower on a portrait) with unknown GPU and method.
- Single small images or one-shot command-line conversions: initialization and PCIe transfers dominate, and the README timings exclude the first iteration.
- Machines without an NVIDIA GPU (AMD only through ZLUDA), or very large images on small GPUs: about 20 bytes of GPU memory per pixel per component (1901 MiB for 8K 4:4:4).
- Needs beyond baseline 8-bit: no 12-bit (issue #13 open since 2018), no progressive, no lossless JPEG.

## How it is fast

Every stage except stream parsing and formatting runs on the GPU: color conversion, a fixed-point 8x8 forward/inverse DCT with quantization (the DCT file carries NVIDIA CUDA SDK sample code), and Huffman coding. Restart markers split the bitstream into thousands of independent segments: the library default is 8 MCUs, and gpujpegtool asks for RESTART_AUTO, which picks 4 to 12 MCUs by megapixel count, times the component count for non-interleaved streams (the README's 24-36); gpujpeg_huffman_encoder_encode_kernel_warp codes one segment per warp, using __ballot_sync bitmaps of nonzero coefficients and constant-memory codeword LUTs with in-kernel byte stuffing. The decoder parses segment offsets on the CPU (faster when the encoder wrote its APP13 segment-info header) and decodes segments in parallel with a 10-bit quick lookup table plus a JPEG-spec slow path.

## Compared with alternatives

Pick it over libjpeg-turbo, jpeg-nitro or zenjpeg when you control both ends and have an NVIDIA GPU with frames in GPU memory and need millisecond 4K/8K encode; pick oss-nvjpg only on Tegra/Switch hardware decoders, and look at the Weissenberger-Schmidt GPU decoder (catalogued as a paper) when you must decode JPEGs that lack restart markers, which GPUJPEG cannot parallelize.

## Integration

| | |
|---|---|
| **Form** | shared lib (static via BUILD_SHARED_LIBS=OFF) |
| **Dependencies** | CUDA toolkit and runtime (cudart); optional OpenGL/GLEW/GLFW/GLUT for texture interop; optional fpnge (C++, SSE4.1) for PNG output in the tool |
| **Minimum toolchain** | CMake 3.10 (3.18 for CMAKE_CUDA_ARCHITECTURES), C compiler plus nvcc; GPU compute capability 2.0 or newer per README |
| **Platforms** | Linux and Windows (MSW tool support since 2020) with an NVIDIA CUDA GPU; AMD Radeon via ZLUDA; host CPU architectures and macOS not documented |
| **Thread safety** | not documented; each encoder/decoder owns its buffers and takes its own CUDA stream, and NEWS 0.20.4 removed implicit synchronization between parallel encoders, so one instance per thread is the intended model |
| **Drop-in for the baseline** | no |

## Gotchas

- License: COPYING is BSD-2-Clause, but src/gpujpeg_dct_gpu.cu carries a 'Copyright 1993-2010 NVIDIA Corporation' header that refers to the NVIDIA end-user license agreement and says use outside that EULA 'is strictly prohibited'; check this before vendoring.
- Encoder defaults favour speed over compatibility: non-interleaved scans, restart markers, and SPIFF or Adobe headers when the internal color space is not full-range BT.601 (some third-party decoders ignore SPIFF color information).
- The README timings feed the encoder from cudaMallocHost pinned memory (gpujpeg_image_load_from_file); pageable user buffers will make the PCIe part slower. Reported numbers are gpujpegtool's 'Avg w/o 1st Iter' wall time from encode start to formatted stream, which includes host-device copies and CPU stream formatting.
- Open decoder bugs as of 2026-10-04: issue #108 (bug label, open) reports wrong colors on the second image when one decoder instance is reused; issue #107 (rows of odd-width images misaligned for OpenCV, width_padding always 0) got only an alignment option, GPUJPEG_DEC_OPT_ALIGNMENT_BYTES_INT, in 0.27.13.

## Known shortcomings

- Tier D: README numbers are GPU timings with no CPU or nvJPEG baseline on the page; issues #47 and #48 (same post) report a mixed result against nvJPEG (1.8x faster and 1.4x slower) with no GPU named; the FGCS 2013 paper is blocked here.
- Enricher (e103, 2026-10-04): still no CPU (libjpeg-turbo) or nvJPEG baseline, so D stands. README timing table has an inconsistent cell (RTX 2080 Ti 4K decode 1.07 ms vs HD 1.02 ms and 8K 11.29 ms, and faster than the RTX 4080's 1.46 ms), likely a typo. Benchmark input sits in cudaMallocHost pinned memory, so pageable user buffers transfer slower than shown. License caveat: src/gpujpeg_dct_gpu.cu carries a 1993-2010 NVIDIA EULA header ('strictly prohibited' outside the EULA), so the tree is not cleanly BSD-2-Clause. Open bug #108: wrong colors when a decoder instance is reused.

## Caveats and trade-offs

No numeric comparison against libjpeg-turbo, nvJPEG or any CPU codec in the README, FAQ.md or NEWS.md (NEWS only cites self-comparisons such as first-frame start-up 43 ms vs 810 ms, about 20x, and an IDCT kernel 43% faster). The only cross-codec numbers are one user's September 2020 post, filed twice as issues #47 and #48 with identical text and no maintainer reply visible: on an 8192x8192 random texture total time was 911.242 ms for GPUJPEG vs 1608.21 ms for nvJPEG (1.8x, derived), but on a portrait with a uniform background 620.884 ms vs 441.444 ms (nvJPEG 1.4x faster, derived); GPU, CUDA version and method are not given, times include I/O, and GPUJPEG's stream had 16384 restart segments against 1 for nvJPEG. Per the README, Huffman coding runs on the GPU only when restart markers are present; with restart interval 0 the CPU Huffman coder is used, so JPEGs from other encoders without restart markers do not get the GPU Huffman path. README timings: a hidden comment says the RTX 4080 rows came from a cmake build without Release or CUDA-architecture flags with 5 measurements averaged (the visible text says 99 measurements), and another hidden note says other measurements were done without CMAKE_BUILD_TYPE=Release. Host CPU, CUDA toolkit and driver versions are not stated. The peer-reviewed description (Holub et al., 'GPU-accelerated DXT and JPEG compression schemes for low-latency network transmissions of HD, 2K, and 4K video', Future Generation Computer Systems, 2013) could not be opened here (ScienceDirect, ACM and ics.muni.cz blocked), so any CPU comparison in it is unverified. A check against a CPU baseline is needed before listing it as faster than libjpeg-turbo.

Needs an NVIDIA CUDA GPU (AMD only through ZLUDA). Baseline sequential-Huffman JPEG only, 8-bit; GPU Huffman encode and decode require restart markers (with restart interval 0 the CPU Huffman coder is used, because the README says one GPU thread would be very slow), so arbitrary JPEGs from cameras decode without GPU parallelism. Default timings include host-device PCIe transfers (8K encode 6.21 ms versus 2.28 ms without them on RTX 3080). First call has initialization cost (about 28.6 ms for 8K on RTX 3080 in the README). Larger images can run out of memory on small GPUs. COPYING is BSD-2-Clause; the README also says the code contains source provided by NVIDIA Corporation and is based on SiGenGPU.

## Maintenance

Actively maintained by CESNET (release 0.27.13 in March 2026, commits into October 2026) and BSD-2-Clause apart from the NVIDIA-EULA header on the DCT file; usable as a library today, but its speed advantage over CPU or nvJPEG codecs is unmeasured.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification D, tier now D.
- **Tier reason:** The README gives absolute GPU encode and decode timings (gpujpegtool -n 100, 99-run averages) but no comparison against libjpeg-turbo, nvJPEG or any other codec, and FAQ.md and NEWS.md compare only against GPUJPEG's own earlier versions. The only cross-codec numbers are a user's 2020 nvJPEG comparison (issues #47 and #48, the same post twice), which is mixed and has no GPU, CUDA version or method, so there is no supported faster-than-baseline number: D.
- **Verifier notes:** All README timings quoted in the record match the page (4K encode 1.65 ms RTX 4080, 1.71 ms RTX 3080, 2.89 ms RTX 2080 Ti, 3.16 ms RX 7600 via ZLUDA; 8K 6.33 ms; 16K 24.92 ms; decode 4K 1.46 ms, 8K 5.78 ms; RTX 3080 8K q70 6.21 ms, 2.28 ms without PCIe). Metadata confirmed: BSD-2-Clause (COPYING), 288 stars, 81 forks, not archived, last commit 2026-10-02. Kept at D as a notable, actively maintained GPU codec; not rejected per batch instructions.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** first-party GPU timings only
- **Pages the verifier opened:**
  - <https://github.com/CESNET/GPUJPEG>
  - <https://github.com/CESNET/GPUJPEG/commits/master>
  - <https://raw.githubusercontent.com/CESNET/GPUJPEG/HEAD/README.md>
  - <https://raw.githubusercontent.com/CESNET/GPUJPEG/HEAD/FAQ.md>
  - <https://raw.githubusercontent.com/CESNET/GPUJPEG/HEAD/NEWS.md>
  - <https://raw.githubusercontent.com/CESNET/GPUJPEG/HEAD/COPYING>
  - <https://github.com/CESNET/GPUJPEG/issues/47>
  - <https://github.com/CESNET/GPUJPEG/issues/48>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/CESNET/GPUJPEG/HEAD/README.md>
  - <https://raw.githubusercontent.com/CESNET/GPUJPEG/HEAD/FAQ.md>
  - <https://raw.githubusercontent.com/CESNET/GPUJPEG/HEAD/NEWS.md>
  - <https://raw.githubusercontent.com/CESNET/GPUJPEG/HEAD/COPYING>
  - <https://raw.githubusercontent.com/CESNET/GPUJPEG/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/CESNET/GPUJPEG/HEAD/src/main.c>
  - <https://raw.githubusercontent.com/CESNET/GPUJPEG/HEAD/src/gpujpeg_common.c>
  - <https://raw.githubusercontent.com/CESNET/GPUJPEG/HEAD/src/gpujpeg_encoder.c>
  - <https://raw.githubusercontent.com/CESNET/GPUJPEG/HEAD/src/gpujpeg_decoder.c>
  - <https://raw.githubusercontent.com/CESNET/GPUJPEG/HEAD/src/gpujpeg_huffman_gpu_encoder.cu>
  - <https://raw.githubusercontent.com/CESNET/GPUJPEG/HEAD/src/gpujpeg_huffman_gpu_decoder.cu>
  - <https://raw.githubusercontent.com/CESNET/GPUJPEG/HEAD/src/gpujpeg_dct_gpu.cu>
  - <https://raw.githubusercontent.com/CESNET/GPUJPEG/HEAD/src/gpujpeg_reader.c>
  - <https://raw.githubusercontent.com/CESNET/GPUJPEG/HEAD/libgpujpeg/gpujpeg.h>
  - <https://raw.githubusercontent.com/CESNET/GPUJPEG/HEAD/libgpujpeg/gpujpeg_encoder.h>
  - <https://github.com/CESNET/GPUJPEG/tree/master/src>
  - <https://github.com/CESNET/GPUJPEG/issues>
  - <https://github.com/CESNET/GPUJPEG/issues/107>
  - <https://github.com/CESNET/GPUJPEG/issues/108>
  - <https://github.com/CESNET/GPUJPEG/issues?q=is%3Aissue+is%3Aclosed+label%3Abug>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/cesnet/gpujpeg`) · [data/wave10/enrich/raw/github_com_cesnet_gpujpeg.json](../../../data/wave10/enrich/raw/github_com_cesnet_gpujpeg.json) (enrichment confidence 0.8)

</details>
