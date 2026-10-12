# HALIC (High Availability Lossless Image Compression)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Study only · `unknown (binaries only; README says built with GCC and Clang)` · `MIT` · 🟡 stale

> Closed-source lossless RGB/gray image codec (CLI binaries) that encodes about 15-32x faster than Pillow PNG and WebP lossless at smaller size.

| | |
|---|---|
| **Beats** | libwebp lossless (Pillow 10.1.0, method 1) and PNG (Pillow 10.1.0, optimize=False) |
| **Claimed result** | CLIC2021: HALIC 1,473,481,803 bytes, 22.187 s compress, 28.447 s decompress versus WebP lossless m1 1,496,478,650 bytes, 720.160 s, 37.044 s (about 32x faster compress, 1.3x faster decompress, 1.5% smaller, derived) and PNG optimize=False 2,003,016,524 bytes, 334.791 s, 33.677 s (about 15x compress, 1.18x decompress, 26% smaller, derived). GDCC2020: HALIC 4.780 s compress and 5.426 s decompress versus PNG optimize=False 152.321 s and 11.545 s (about 32x and 2.1x, derived). |
| **Workload** | Total compress and decompress time and compressed size on CLIC2021 (585 RGB images, 4.1 GB) and GDCC2020 (100 RGB images, 1.0 GB) in the Image-Compression-Benchmark shootout, all codecs single-threaded. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-12700H, 16 GB DDR4-3200, Windows 10; every codec single-threaded, SIMD allowed |
| **Compiler and flags** | Not stated: most codecs are prebuilt Windows .exe files in the benchmark's codec folder, WebP and PNG run through Python 3.9 with Pillow 10.1.0; commands are listed in the README (PNG: Image.open('in.pnm').save('out.png', optimize=False)) |
| **Adoption** | 19 stars |
| **Last commit** | 2024-05-24 |
| **Links** | [repository](https://github.com/Hakan-Abbas/HALIC-High-Availability-Lossless-Image-Compression-) · [benchmark](https://raw.githubusercontent.com/WangXuan95/Image-Compression-Benchmark/HEAD/README.md) |

## Verdict

In WangXuan95's Image-Compression-Benchmark (Intel Core i7-12700H, Windows 10, every codec single-threaded, timed with time.time() over the whole set), HALIC 0.7.2 .exe compressed CLIC2021 (585 RGB images, 4.1 GB) to 1,473,481,803 bytes in 22.187 s and decompressed it in 28.447 s, versus Pillow 10.1.0 WebP lossless method 1 at 1,496,478,650 bytes, 720.160 s and 37.044 s, and Pillow PNG optimize=False (zlib default level; Pillow 10.1.0's Windows build script pins libwebp 1.3.2 and zlib 1.3) at 2,003,016,524 bytes, 334.791 s and 33.677 s; on GDCC2020 it took 4.780 s and 5.426 s versus PNG at 152.321 s and 11.545 s. The WebP baseline ran at quality=100, which in libwebp lossless mode means maximum compression effort, so the 32x encode gap is against a slow WebP setting, while HALIC's times include one process launch per image and the Pillow codecs ran in-process.

## Use it when

- Batch archiving of large 24-bit photographs (multi-megapixel PPM/PNM) where encode time dominates: on CLIC2021 it encoded 4.1 GB in 22.2 s versus 334.8 s for Pillow PNG and 720.2 s for Pillow WebP lossless m1, with output 26% smaller than that PNG.
- Research or comparison work that needs a fast-symmetric reference point between QOI/QOIR-class speed and WebP-lossless-class size.
- Closed environments (offline tools, internal storage) on x86-64 Windows or Linux where running a third-party binary is acceptable and interoperability with other software is not needed.

## Skip it when

- Anything that must be built, audited, fuzzed or embedded: there is no source in the repo, releases or the author's HALIC-Image-Converter, despite the MIT LICENSE file.
- Interchange or long-term storage: .halic is undocumented, single-vendor, and the project has had no release since 0.7.2 (March 2024) or commit since May 2024.
- Small images: process start-up per file dominates, and on UCID (1338 small images) HALIC decoded in 27.2 s versus 15.0 s for WebP lossless m1 and 15.2 s for Pillow PNG; on Kodak Pillow PNG decoded faster too (0.484 s versus 0.615 s).
- Best ratio: JPEG XL e3 and up, fNBLI, BMF, EMMA and other context-mixing codecs are 5-17% smaller on CLIC2021.
- Alpha channels, 16-bit samples, PNG input or other non-PNM formats: not supported or not documented.

## How it is fast

Per the README: simple prediction without context modelling or error correction, so many residuals remain, followed by an ANS entropy coder (FSE) over completely independent blocks and per-channel sub-streams; the measured build runs on one thread. Skipping context mixing is what keeps it near QOI-class speed while compressing close to WebP lossless. The predictor, block size and any SIMD use are not documented: the README says no SIMD or assembly, yet the 0.7.2 assets are labelled AVX and AVX2 builds (compiler target flags, presumably).

## Compared with alternatives

Pick HALIC over fNBLI (GPL-3.0 source, 9% smaller and about as fast to decode on CLIC2021, but 43.2 s versus 22.2 s to encode) only when encode speed matters more than having code; pick Zpng (BSD-3-Clause) or QOIR (Apache-2.0) when you need embeddable source at similar speed and can accept 19-45% larger files than HALIC.

## Integration

| | |
|---|---|
| **Form** | prebuilt command-line executables only (no library, no source) |
| **Dependencies** | none at run time (Linux builds are static) |
| **Minimum toolchain** | not applicable (no source); 0.7.2 Windows builds need an x86-64 CPU with AVX or AVX2, Linux builds AVX2 |
| **Platforms** | Windows x64 (.exe, AVX and AVX2 variants), Linux x64 static (AVX2); release 0.6.0 also shipped Windows ARM64 executables |
| **Thread safety** | not applicable (separate processes); 0.7.2 assets are all single-threaded 'ST' builds, 0.7.0 also had a multithreaded encoder (HALIC_ENCODE_V.0.7.0_MT.exe) |
| **Drop-in for the baseline** | no |

## Gotchas

- The 'FAST' variant (HALIC072fe/fd) is labelled trial in the 0.7.2 notes and failed to decompress zone_plate.pnm in the ImgInfoGray set of the benchmark.
- The benchmark's published RunBenchmark.py has CHECK_DISTORTION = False, so the run as published does not compare decoded pixels with the input; only non-zero exit codes are caught, which is how the FAST failure surfaced.
- The GitHub 'Source code' archives on each release are only the README-only tree; the codec itself is closed.
- The format has no spec or version-compatibility statement; keep the exact decoder binary that wrote your files.

## Known shortcomings

- Reference only: binaries, no source in any author repo; last release 2024-05-24 (stale). Tier B on WangXuan95's Image-Compression-Benchmark (i7-12700H, Windows 10, single thread; CLIC2021 and GDCC2020 numbers match).

## Caveats and trade-offs

The repository holds only README, LICENSE (MIT) and .gitignore; the releases (0.6.0 to 0.7.2) carry only Windows AVX/AVX2 .exe and static Linux binaries plus GitHub's automatic archives of that README-only tree, the author's HALIC-Image-Converter (GPL-3.0 Qt GUI) contains no codec source, and the benchmark's format table marks HALIC as not open source, so the code cannot be inspected or rebuilt and has_code is false even though the licence file says MIT. The measured binary is HALIC072e.exe/HALIC072d.exe from the benchmark's codec folder, with no compiler or flags. The PNG baseline is Pillow's zlib-based encoder (default level), not libpng, and WebP lossless also runs through Pillow 10.1.0 (method 1 and 5). The harness runs Pillow codecs in-process but launches HALIC as one process per image through os.system, so HALIC's times include process start-up and the comparison is conservative for HALIC. On tiny images PNG decodes faster (Kodak: PNG optimize=False 0.484 s versus HALIC 0.615 s), so the decode win shows only on large images. The benchmark author also wrote the competing NBLI/fNBLI codecs (fNBLI is smaller and decodes slightly faster than HALIC on CLIC2021). The author's own README charts carry no numbers.

Binary releases only (Windows and Linux executables), PPM and PNM input, ANS (FSE) entropy coder with independent blocks, multithreading only from version 0.7 on. Compression ratio is behind JPEG XL, EMMA and NBLI; the 'HALIC fast' variant trades size for speed and failed to decompress one gray test image (zone_plate.pnm) in the benchmark.

## Maintenance

Stale since 2024-05-24 (LICENSE added; last binaries 0.7.2 from 2024-03-13, no issues filed) and reference-only: the MIT licence covers a README, not inspectable code, so treat it as a benchmark point rather than something to ship.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now B.
- **Tier reason:** WangXuan95/Image-Compression-Benchmark is an independent third-party shootout (public RunBenchmark.py, Intel Core i7-12700H, Windows 10, every codec single-threaded) whose CLIC2021 and GDCC2020 tables hold HALIC v0.7.2 next to WebP lossless and PNG via Pillow 10.1.0; it cannot be A because HALIC is a prebuilt closed-source .exe with no compiler or flags.
- **Verifier notes:** All quoted numbers match the HALIC, WEBP (lossless m1) and PNG (optimize=False) rows of the CLIC2021, GDCC2020 and Kodak tables, and the derived ratios are correct. No HALIC source exists in any public repository of the author; WebSearch snippets claiming source availability refer to the README-only repo. Last commit 2024-05-24 (LICENSE added), so stale is right.
- **Fields the verifier corrected:** `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/WangXuan95/Image-Compression-Benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/WangXuan95/Image-Compression-Benchmark/HEAD/RunBenchmark.py>
  - <https://github.com/WangXuan95/Image-Compression-Benchmark>
  - <https://raw.githubusercontent.com/Hakan-Abbas/HALIC-High-Availability-Lossless-Image-Compression-/HEAD/README.md>
  - <https://github.com/Hakan-Abbas/HALIC-High-Availability-Lossless-Image-Compression->
  - <https://github.com/Hakan-Abbas/HALIC-High-Availability-Lossless-Image-Compression-/releases>
  - <https://github.com/Hakan-Abbas/HALIC-High-Availability-Lossless-Image-Compression-/commits>
  - <https://github.com/Hakan-Abbas/HALIC-Image-Converter>
  - <https://github.com/Hakan-Abbas>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/Hakan-Abbas/HALIC-High-Availability-Lossless-Image-Compression-/HEAD/README.md>
  - <https://raw.githubusercontent.com/Hakan-Abbas/HALIC-High-Availability-Lossless-Image-Compression-/HEAD/LICENSE>
  - <https://github.com/Hakan-Abbas/HALIC-High-Availability-Lossless-Image-Compression-/releases>
  - <https://github.com/Hakan-Abbas/HALIC-High-Availability-Lossless-Image-Compression-/releases/expanded_assets/0.7.0>
  - <https://github.com/Hakan-Abbas/HALIC-High-Availability-Lossless-Image-Compression-/releases/expanded_assets/0.6.0>
  - <https://github.com/Hakan-Abbas/HALIC-High-Availability-Lossless-Image-Compression-/issues?q=is%3Aissue>
  - <https://github.com/Hakan-Abbas/HALIC-High-Availability-Lossless-Image-Compression-/commits>
  - <https://github.com/Hakan-Abbas?tab=repositories>
  - <https://raw.githubusercontent.com/WangXuan95/Image-Compression-Benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/WangXuan95/Image-Compression-Benchmark/HEAD/RunBenchmark.py>
  - <https://github.com/WangXuan95/Image-Compression-Benchmark/tree/main/codec/HALIC>
  - <https://raw.githubusercontent.com/WangXuan95/Image-Compression-Benchmark/HEAD/codec/HALIC/source.txt>
  - <https://github.com/WangXuan95/Image-Compression-Benchmark/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/python-pillow/Pillow/10.1.0/winbuild/build_prepare.py>
  - <https://raw.githubusercontent.com/python-pillow/Pillow/10.1.0/src/PIL/PngImagePlugin.py>
  - <https://raw.githubusercontent.com/python-pillow/Pillow/10.1.0/src/PIL/WebPImagePlugin.py>
  - <https://raw.githubusercontent.com/webmproject/libwebp/v1.3.2/src/webp/encode.h>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/hakan-abbas/halic-high-availability-lossless-image-compression-`) · [data/wave10/enrich/raw/github_com_hakan_abbas_halic_high_availability_lossless_image_compression.json](../../../data/wave10/enrich/raw/github_com_hakan_abbas_halic_high_availability_lossless_image_compression.json) (enrichment confidence 0.6)

</details>
