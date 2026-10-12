# fNBLI (NBLI lossless image codec)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `GPL-3.0` · 🟢 active

> Single-threaded AVX2 lossless codec for 8-bit gray and 24-bit RGB; 7.8x faster encode than Pillow PNG with 33% smaller files.

| | |
|---|---|
| **Beats** | PNG encoded and decoded through Pillow 10.1.0's own PNG codec (PngImagePlugin over Pillow's zlib-based 'zip' codec, not libpng), optipng 0.7.7 for optimized PNG encoding, and libwebp lossless via Pillow 10.1.0 |
| **Claimed result** | Image-Compression-Benchmark README, CLIC2021 totals (585 images, 4.1 GB, single-threaded): fNBLI 43.164 s compress, 27.450 s decompress, 1,337,587,020 bytes; Pillow PNG (optimize=False) 334.791 s, 33.677 s, 2,003,016,524 bytes; PNG optipng -o2 4395.069 s, 26.625 s, 1,905,215,734 bytes; Pillow WebP lossless m5 1112.134 s, 49.442 s, 1,475,908,700 bytes. That is 7.8x faster encode and 1.23x faster decode than Pillow PNG with 33% smaller files, and 25.8x faster encode and 1.80x faster decode than WebP lossless m5 with 9% smaller files (derived from page data); decoding is slightly slower than optipng-optimized PNG (27.450 s vs 26.625 s at -o2 and 25.799 s at -o5). NBLI README restates these as fNBLI 94.8 MB/s compress and 149.1 MB/s decompress, 29.79% smaller than optipng PNG, vs PNG 12.2 / 121.5 MB/s and WebP -5 3.7 / 82.8 MB/s. |
| **Workload** | Single-threaded lossless compression and decompression of the CLIC2021 training set (585 RGB 24-bit .pnm images, 4.1 GB) and six other datasets, timed per dataset with file I/O included, in the author's Image-Compression-Benchmark shootout (RunBenchmark.py, which checks the round trip is lossless). |
| **Metric** | throughput |
| **Hardware** | Intel Core i7 12700H, 16GB DDR4-3200, Windows 10, single-threaded with SIMD allowed |
| **Compiler and flags** | Prebuilt fNBLI.exe v0.4 (banner 'v0.4, 202409', needs AVX2); compiler and flags for that binary are not stated, and the README gives a build command (g++ -O3 -static) only for the NBLI prototype in src/NBLI, not for src/fNBLI. Baselines: Pillow 10.1.0 on Python 3.9, optipng 0.7.7. |
| **Adoption** | 98 stars |
| **Last commit** | 2026-07-18 |
| **Links** | [repository](https://github.com/WangXuan95/NBLI) · [benchmark](https://raw.githubusercontent.com/WangXuan95/Image-Compression-Benchmark/HEAD/README.md) |

## Verdict

The author's own Image-Compression-Benchmark ran the prebuilt fNBLI.exe v0.4 (compiler and flags unknown) once per image through os.system on an i7-12700H under Windows 10, single-threaded, with file I/O included and the round trip checked for losslessness. On CLIC2021 (585 RGB images, 4.09 GB) fNBLI took 43.164 s to compress and 27.450 s to decompress, producing 1,337,587,020 bytes. Pillow 10.1.0's in-process PNG took 334.791 s and 33.677 s for 2,003,016,524 bytes (7.8x faster encode, 1.23x faster decode, 33% smaller, derived), and Pillow WebP lossless method 5 took 1112.134 s and 49.442 s.

## Use it when

- Archiving or caching large photographic RGB or gray images that only your own software reads, where you want JPEG-XL-e7-class size (1,337.6 MB vs 1,337.1 MB on CLIC2021) at 62x the encode speed and 9x the decode speed (derived).
- Replacing PNG in an internal pipeline where PNG encode time dominates: 7.8x faster encode than Pillow's default PNG and 102x faster than optipng -o2 (derived), with 30-33% smaller files.
- Single-core x86-64 workers with AVX2 (Haswell or newer) processing images with at least 18 rows, 32 columns and 4,096 pixels, up to 32000x32000. Smaller images take the scalar path.
- Research or benchmarking of fast context-modelling lossless coders: the source is short (about 2,800 lines) and shows a vectorized wavefront plus interleaved rANS design.

## Skip it when

- Anything that must be read by browsers, OS image viewers or other tools: .fnbli is a private format with no spec, a 4-byte magic and no version field, and no alpha, palette or 16-bit support.
- Decode-bound workloads: decoding is no faster than optimized PNG (27.45 s vs 26.63 s for optipng -o2 output on CLIC2021). QOI, QOIR and Zpng decode faster still, at much larger sizes.
- Untrusted input: fNBLIdecompress takes no input length, and the rANS and histogram decoders read and write without bounds checks (a crafted repeat code or histogram can write past the 512-entry histogram or the 16,384-entry decode table), so treat it as unsafe on hostile files.
- Non-x86 or pre-AVX2 targets: the vector code is AVX2 intrinsics only. A file encoded on an AVX2 machine uses the 16-row layout, and fNBLIdecompress returns NULL on a CPU without AVX2. SupportAVX2.h static_asserts unless building for Linux or Windows, so macOS does not build.
- Closed-source or permissive-license products: GPL-3.0.

## How it is fast

It uses a CALIC-style pixel pipeline. A reversible lifting colour transform (G as luma, R-G and B-G as chroma) feeds a gradient-adjusted predictor that blends a 6-tap linear predictor with the left or upper neighbour depending on edge direction. An activity measure quantized to 12 levels, times an 8-bit texture pattern, indexes CALIC-style bias-correction contexts. Residuals go through a two-pass static rANS coder: the encoder collects every (context, symbol) pair, normalizes one 512-symbol 14-bit histogram per coding context (24 in total), then codes in reverse. The speed comes from processing 16 image rows at once in a diagonal wavefront (each row 2 pixels behind the row above), with the predictor, context lookups (AVX2 gathers) and 16 interleaved rANS states running in AVX2 lanes. That gives data parallelism in one thread without changing the model, which the README presents as a 'parallel entropy encoding method that does not affect the compression ratio'.

## Compared with alternatives

Pick fNBLI over HALIC (same harness: 22.2 s encode, 28.4 s decode, 1,473.5 MB) when about 9% smaller files are worth roughly 2x slower encoding at equal decode speed and you want source code (HALIC is closed). Pick it over QOI, QOIR or Zpng when size matters more than speed: those encode 1.7-2.3x faster and decode 1.1-1.45x faster, but their files are 31-70% larger (derived from CLIC2021). Pick the libjxl fast_lossless/JPEG-XL route or CharLS instead when you need a standard format.

## Integration

| | |
|---|---|
| **Form** | source-drop (no build system; compile src/fNBLI/\*.cpp with ../FileIO.h and src/imageio for the CLI), or the prebuilt fNBLI.exe / Linux fNBLI binaries |
| **Dependencies** | none for the codec; the CLI uses the bundled imageio (PNM, uPNG) sources |
| **Minimum toolchain** | C++17 (static_assert without message) with GCC or Clang; uses __attribute__((aligned(32))) and AVX2 intrinsics without target attributes, so it needs -mavx2. Exact compiler version not documented |
| **Platforms** | x86-64 with AVX2 (Haswell or later) on Linux or Windows; a scalar path exists for small images and non-AVX2 encoders, but a GCC/Clang build with -mavx2 is AVX2-only anyway |
| **Thread safety** | Not documented. Each call allocates its own model, histogram and rANS state, and the only statics are constant tables, so concurrent calls on different images look safe. Each call is single-threaded. |
| **Drop-in for the baseline** | no |

## Gotchas

- The bitstream depends on the encoding CPU: an image with at least 18 rows, 32 columns and 4,096 pixels, encoded where AVX2 is present, uses the 16-row wavefront layout and can only be decoded where AVX2 is present. Without AVX2 the encoder silently takes the slower serial path.
- Memory: the encoder allocates about 2.1x the raw image size plus 4 MB (output buffer and symbol stack share one uint16 buffer), and the decoder builds a 768 KB lookup table. The decompress input must be 2-byte aligned or it returns NULL.
- The AVX2 gathers read 4 bytes per element from uint8 and int16 tables and from the caller's pixel buffer, so they read up to 3 bytes past the end of the image and table allocations. This is harmless in practice, but AddressSanitizer or Valgrind will flag it unless buffers are padded.
- CRC32 is optional (-x; crc32 != 0 in the API), uses a slow 4-bit table, and is off in the benchmarked command, so corruption is otherwise undetected. The README's NBLI link points to ./src_NBLI, but the source lives in src/NBLI and src/fNBLI.

## Known shortcomings

- Author-run shootout (CLIC2021: 43.164 s vs 27.450 s) with fNBLI.exe's compiler and flags unstated; the fNBLI source was published 2026-07-18 (src/fNBLI, commit 6561fc8, GPL-3.0). The Pillow PNG baseline is Pillow's own zlib codec rather than libpng, and Pillow runs in-process while fNBLI pays a per-file os.system start. Decode is slower than optipng's PNG (27.450 vs 26.625 s).
- AVX2 and x86 only (intrinsics lack target attributes, so -mavx2 is required), and the bitstream depends on the encoder's CPU: AVX2-encoded files return NULL on non-AVX2 decoders; no macOS build (static_assert); no build recipe, and the shipped binary is not rebuilt from source. The decoder is unhardened: fNBLIdecompress takes no input length, crafted histogram codes can write past the 512-entry histogram and the 16,384-entry decode LUT (heap overflow), and the gathers over-read up to 3 bytes.

## Caveats and trade-offs

Author-run benchmark of the author's own codec. The timing harness is asymmetric: Pillow codecs run in-process through exec(), while fNBLI.exe is launched with os.system once per image, so fNBLI also pays process start-up per file (this handicaps fNBLI, not the baselines). The PNG baseline is Pillow's own zlib-based PNG codec, not libpng. Decoding is not faster than optipng-optimized PNG (27.450 s vs 26.625 s / 25.799 s on CLIC2021). The fNBLI source was published on 2026-07-18 (commit 6561fc8, 2,804 added lines under src/fNBLI including AVX2 and rANS code) and carries the same 'v0.4, 202409' banner as the benchmarked binary, but the binary predates the source, the README still links fNBLI.exe, the shootout's format table still marks fNBLI as not open source, and there is no build recipe for it, so binary-to-source correspondence is unverified. Single benchmark machine (i7-12700H, Windows 10).

Custom non-PNG format for 8-bit gray and 24-bit RGB; GPL-3.0 (copyleft); fNBLI needs AVX2. The slower prototype NBLI (-g, 14.7 MB/s compress, 17.0 MB/s decompress) compresses to -30.37% but decodes far slower than PNG. Includes PNG and PNM input.

## Maintenance

There are five commits in total: v0.4 dates from October 2024, and the source was opened on 2026-07-18 (commit 6561fc8, no binary rebuilt). The repo has 98 stars, no open issues or PRs and no releases, so it is effectively a finished research artifact under GPL-3.0. It is small enough to vendor, but with no build recipe, tests or format spec.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** Author-run shootout of the author's own codec with a public driver (RunBenchmark.py) and stated CPU (i7-12700H), but the measured fNBLI.exe is a prebuilt binary with no stated compiler or flags, so it falls short of A; first-party, so C.
- **Verifier notes:** The orchestrator's premise that fNBLI is binary-only is out of date: src/fNBLI source exists since 2026-07-18 under the repo's GPL-3.0, so has_code stays true and usability copyable. All shootout numbers and the README MB/s figures check out (94.8 MB/s = 4,091,841,959 bytes / 43.164 s); the record's claim that Pillow pays per-file process overhead was wrong and is corrected. No known correctness bug; the driver verifies losslessness.
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `compiler_and_flags`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/WangXuan95/Image-Compression-Benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/WangXuan95/Image-Compression-Benchmark/HEAD/RunBenchmark.py>
  - <https://raw.githubusercontent.com/WangXuan95/NBLI/HEAD/README.md>
  - <https://github.com/WangXuan95/NBLI>
  - <https://github.com/WangXuan95/NBLI/commits>
  - <https://github.com/WangXuan95/NBLI/tree/main/src>
  - <https://github.com/WangXuan95/NBLI/commit/6561fc8>
  - <https://raw.githubusercontent.com/WangXuan95/NBLI/HEAD/src/fNBLI/fNBLI.cpp>
  - <https://raw.githubusercontent.com/WangXuan95/NBLI/HEAD/src/fNBLI/main.cpp>
  - <https://raw.githubusercontent.com/WangXuan95/NBLI/HEAD/src/fNBLI/fNBLIcodec.h>
  - <https://raw.githubusercontent.com/WangXuan95/NBLI/HEAD/src/fNBLI/rANS.h>
  - <https://raw.githubusercontent.com/python-pillow/Pillow/10.1.0/src/PIL/PngImagePlugin.py>
  - <https://raw.githubusercontent.com/python-pillow/Pillow/10.1.0/src/libImaging/ZipDecode.c>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/WangXuan95/NBLI/HEAD/README.md>
  - <https://github.com/WangXuan95/NBLI>
  - <https://github.com/WangXuan95/NBLI/tree/main/src/fNBLI>
  - <https://github.com/WangXuan95/NBLI/commits/main>
  - <https://github.com/WangXuan95/NBLI/commit/6561fc8>
  - <https://raw.githubusercontent.com/WangXuan95/NBLI/HEAD/src/fNBLI/fNBLI.h>
  - <https://raw.githubusercontent.com/WangXuan95/NBLI/HEAD/src/fNBLI/fNBLI.cpp>
  - <https://raw.githubusercontent.com/WangXuan95/NBLI/HEAD/src/fNBLI/fNBLIcodec.h>
  - <https://raw.githubusercontent.com/WangXuan95/NBLI/HEAD/src/fNBLI/rANS.h>
  - <https://raw.githubusercontent.com/WangXuan95/NBLI/HEAD/src/fNBLI/PxCorrector.h>
  - <https://raw.githubusercontent.com/WangXuan95/NBLI/HEAD/src/fNBLI/ImageSampler.h>
  - <https://raw.githubusercontent.com/WangXuan95/NBLI/HEAD/src/fNBLI/ImageSampler_x16_AVX.h>
  - <https://raw.githubusercontent.com/WangXuan95/NBLI/HEAD/src/fNBLI/ModelingFunctions.h>
  - <https://raw.githubusercontent.com/WangXuan95/NBLI/HEAD/src/fNBLI/INTx16_AVX2.h>
  - <https://raw.githubusercontent.com/WangXuan95/NBLI/HEAD/src/fNBLI/RGB_YUV.h>
  - <https://raw.githubusercontent.com/WangXuan95/NBLI/HEAD/src/fNBLI/SupportAVX2.h>
  - <https://raw.githubusercontent.com/WangXuan95/NBLI/HEAD/src/fNBLI/Header.h>
  - <https://raw.githubusercontent.com/WangXuan95/NBLI/HEAD/src/fNBLI/CRC32.h>
  - <https://raw.githubusercontent.com/WangXuan95/NBLI/HEAD/src/fNBLI/main.cpp>
  - <https://raw.githubusercontent.com/WangXuan95/Image-Compression-Benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/WangXuan95/Image-Compression-Benchmark/HEAD/RunBenchmark.py>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/wangxuan95/nbli`) · [data/wave10/enrich/raw/github_com_wangxuan95_nbli.json](../../../data/wave10/enrich/raw/github_com_wangxuan95_nbli.json) (enrichment confidence 0.85)

</details>
