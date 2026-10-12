# PZP (Portable Zipped PNM)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `GPL-3.0` · 🟢 active

> Zstd-compressed PNM container in a single C header; loads palette-friendly label maps about 2.3x faster than PNG via cv2.imread.

| | |
|---|---|
| **Beats** | libpng (PNG decode through OpenCV cv2.imread) |
| **Claimed result** | PNG total 1141.2 ms (2.282 ms per image) vs PZP 500.6 ms (1.001 ms per image): 2.28x faster load; files 4.1 MB as PNG vs 2.0 MB as PZP (52% smaller). |
| **Workload** | scripts/compare_load_speed.py on 500 matched COCO val2017 panoptic segmentation label maps (3-channel uint8 RGB, varying resolutions): one untimed warm-up pass over both sets (fills the page cache), then 3 timed passes, best pass reported. PNG column: cv2.imread(IMREAD_UNCHANGED) plus a BGR-to-RGB numpy view; PZP column: PZP.read, a ctypes call into libpzp.so plus one memcpy into a numpy array, files encoded with USE_COMPRESSION, USE_RLE and USE_PALETTE (zstd). Pixel identity is checked on the first 10 pairs only. |
| **Metric** | latency |
| **Compiler and flags** | gcc (version not stated); libpzp.so is built by the Makefile with -shared -fPIC -D_GNU_SOURCE -DINTEL_OPTIMIZATIONS -O3 -mavx2 -march=native -mtune=native, linked against system libzstd and liblz4 (versions not stated). OpenCV version and its PNG backend build not stated. |
| **Adoption** | 2 stars, 1 fork, 132 commits |
| **Last commit** | 2026-09-29 |
| **Links** | [repository](https://github.com/AmmarkoV/PZP) · [benchmark](https://github.com/AmmarkoV/PZP/blob/HEAD/doc/performance.md) |

## Verdict

First-party scripts/compare_load_speed.py run on 500 COCO val2017 panoptic label maps (3-channel uint8, files encoded with USE_COMPRESSION, USE_RLE and USE_PALETTE): best of 3 passes after one warm-up, PNG through cv2.imread (OpenCV's libpng, version unstated) took 1141.2 ms against PZP through ctypes and libpzp.so at 500.6 ms (2.28x), with files 4.1 MB versus 2.0 MB; libpzp.so used gcc -O3 -mavx2 -march=native, and no CPU model, OpenCV, libpng, zstd or gcc version is recorded.

## Use it when

- Training-data pipelines that re-read the same images many times (segmentation label maps, masks, depth maps) and can afford a one-time conversion from PNG.
- 8-bit or 16-bit grayscale/RGB images with few distinct values per channel, where USE_PALETTE plus USE_RLE gives both a smaller file and a faster load than PNG.
- Python data loaders on Linux x86-64 with AVX2 that today call cv2.imread on PNG and are bound by decode time; PZP.read returns a numpy array directly.
- Storing short image sequences or depth streams where the inter-frame delta and multi-frame container (with delays, metadata and audio) are useful.
- When LZ4 is acceptable for larger files in exchange for faster decode on a ramdisk or NVMe.

## Skip it when

- You need interoperability: no browser, image editor or standard library reads .pzp, and the format is at v0.03 with a layout change in 2026 (PZP0 to PZP1 frames).
- Photographs or high-entropy images: the only published number is for COCO panoptic label maps, the README's own best case; no photo, fpng, libspng, Wuffs or QOI comparison exists.
- Large frames: the decoder rejects any frame whose uncompressed payload exceeds 100,000,000 bytes (for example 16-bit RGB above about 16.7 megapixels or 8-bit RGB above about 33 megapixels), while the encoder has no such limit, so such files write but do not read back.
- Untrusted input with integrity needs: read-time checksum verification is off by default (PZP_VERIFY_CHECKSUM=0) and zstd frames are written without a content checksum, whereas PNG checks CRC32 and Adler-32.
- GPL-3.0 is incompatible with your product, or you need a portable prebuilt library: libpzp.so is built with -march=native and AVX2 with no runtime dispatch.

## How it is fast

Decoding is one zstd (or LZ4) call into a single buffer, using a per-thread reused ZSTD_DCtx, followed by an in-place left-delta prefix sum and a palette table lookup; there is no chunk parsing, no per-row filter selection and no zlib inflate. Under -DINTEL_OPTIMIZATIONS the prefix sum is an AVX2 Kogge-Stone scan with explicit cross-lane carry; since the 2026-03-29 commit 3-channel images are de-interleaved with SSSE3 shuffles, scanned per plane and re-interleaved (doc/performance.md still says 3-channel falls back to scalar, which was true of the code that produced the published numbers). Palette mode is compressed at zstd level 19, so label maps with few distinct values per channel shrink well and decode fast.

## Compared with alternatives

Pick PZP over Zpng or QOI when your data is palette-like label maps or 16-bit depth and you want a Python numpy reader, palette and inter-frame modes in one container; pick fpng, libspng or the PNG-compatible siblings when files must stay PNG, and QOI or QOIR when you want a permissively licensed format with third-party benchmark numbers.

## Integration

| | |
|---|---|
| **Form** | header-only (pzp.h, all functions static) plus an optional shared lib (libpzp.so) and a pip-installable Python ctypes package |
| **Dependencies** | libzstd and liblz4 (system packages); optional OpenZL v0.3.0 built from source with PZP_USE_OPENZL=1; Python bindings work without numpy (raw bytes) and return numpy arrays when it is installed; the CLI reads only binary PNM (P5/P6) input |
| **Minimum toolchain** | C11 (uses _Thread_local); built and documented with gcc only; toolchain version not documented |
| **Platforms** | Header: any little-endian target with zstd and lz4 (multi-byte header fields are copied in native byte order). libpzp.so as built by the Makefile: x86-64 with AVX2 and the build machine's -march=native; setup.py names .dylib/.dll but the Makefile only builds libpzp.so |
| **Thread safety** | Decoding is reentrant; each thread lazily gets its own _Thread_local ZSTD_DCtx (pzp_thread_init/pzp_thread_cleanup free it explicitly). Encoders modify the caller's planar buffers in place. |
| **Drop-in for the baseline** | no |

## Gotchas

- The 2.28x figure was published in the README by 2026-03-21 (commit bc7a2b8) and measured on that code, which verified a checksum on every read, created a fresh zstd context per call, ran 3-channel delta reconstruction as a scalar loop and did not bounds-check header fields; current code differs in all four respects, so the number is unmeasured for today's build (likely conservative for speed).
- Palette mode always compresses at zstd level 19 (non-palette at level 1), so encoding label maps is slow; plan for a write-once, read-many workflow.
- The palette is per channel (up to 256 values each), not per colour, so an RGB map with many distinct colours but few values per channel still benefits, while one with near-full channel ranges does not.
- doc/c-api.md lists pzp_compress_combined as returning void; it now returns int (1 on success, 0 on failure) and no longer exits the process on write errors.

## Known shortcomings

- A format comparison (zstd-compressed PNM against deflate PNG through cv2.imread), not a faster PNG decoder; harness scripts/compare_load_speed.py (best of 3, pixel check on 10 pairs) with libpzp.so built -O3 -mavx2 -march=native and no CPU model; 3-channel data skips the SIMD RLE path.
- Enricher (e97, 2026-10-04): the README's 2.28x load figure is stale: it was measured by 2026-03-21 (bc7a2b8) on code with checksum verification on every read, no ZSTD_DCtx reuse, scalar 3-channel reconstruction and no header bounds checks; since 2026-03-29 the 3-channel path is AVX2 de-interleaved, checksum verification is off by default (PZP_VERIFY_CHECKSUM=0) and zstd frames are written without a content checksum, so the measured code is not the current code. Bug outside the benchmark: the decoder rejects payloads above 100,000,000 bytes while the encoder has no cap, so 16-bit RGB above about 16.7 MP or 8-bit RGB above about 33 MP writes but never reads back. libpzp.so is built -march=native with no runtime dispatch. First commit 2025-02-01.

## Caveats and trade-offs

First-party numbers from one machine with no CPU model; the harness (scripts/compare_load_speed.py) is a Python loop comparing a ctypes call into libpzp.so against cv2.imread, so OpenCV's imread overhead sits in the PNG column. This compares two file formats (zstd with palette and RLE versus PNG's deflate), not a faster PNG decoder: the doc credits zstd decoding faster than zlib plus a flat layout. The dataset is segmentation label maps with few distinct colors, the README's own best case. libpzp.so is compiled with -DINTEL_OPTIMIZATIONS, but doc/performance.md says 3-channel images fall back to a scalar loop in the SSE2/AVX2 prefix-scan RLE decoder, so the SIMD path does not run on this dataset. Not compared with fpng, Wuffs, libspng or QOI. The output block in doc/performance.md is formatted slightly differently from what the current script prints, but the numbers agree (1141.2 / 500.6 ms = 2.28x). GPL-3.0.

Not PNG: a custom container (PNM pixel data wrapped in a compact binary header, ZSTD or LZ4, optional delta filter, palette indexing, inter-frame delta, multi-frame with audio) that needs libzstd and liblz4 and has no interoperability with PNG tools. Header-only C with Python ctypes bindings; 8-bit and 16-bit grayscale and RGB only. GPL-3.0.

## Maintenance

Active single-author project (initial commit February 2025, burst of work since March 2026, last commit 2026-09-29, 2 stars, 132 commits, one closed issue about the license); GPL-3.0, small enough to vendor, and the author vendors it into the DataLoader of the RGBToPoseDetect2D project.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party single run. The harness is public (scripts/compare_load_speed.py: 1 warm-up pass, best of 3 timed passes, pixel-identity check on the first 10 pairs) and libpzp.so's gcc flags are in the Makefile, but no CPU model, OpenCV version or libpng build is stated, and the 500-image COCO set is not in the repo.
- **Verifier notes:** Numbers match doc/performance.md (1141.2 ms vs 500.6 ms best of 3, 2.28x; 4.1 MB vs 2.0 MB). Baseline is cv2.imread (OpenCV's PNG decoder, which the doc names as libpng). Weeks-old single-author repo (2 stars); kept on evidence, tier C.
- **Fields the verifier corrected:** `workload`, `compiler_and_flags`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** first-party harness
- **Pages the verifier opened:**
  - <https://github.com/AmmarkoV/PZP>
  - <https://github.com/AmmarkoV/PZP/commits>
  - <https://github.com/AmmarkoV/PZP/tree/master/scripts>
  - <https://raw.githubusercontent.com/AmmarkoV/PZP/HEAD/README.md>
  - <https://raw.githubusercontent.com/AmmarkoV/PZP/HEAD/doc/performance.md>
  - <https://raw.githubusercontent.com/AmmarkoV/PZP/HEAD/doc/scripts.md>
  - <https://raw.githubusercontent.com/AmmarkoV/PZP/HEAD/scripts/compare_load_speed.py>
  - <https://raw.githubusercontent.com/AmmarkoV/PZP/HEAD/scripts/benchmark.py>
  - <https://raw.githubusercontent.com/AmmarkoV/PZP/HEAD/Makefile>
  - <https://raw.githubusercontent.com/AmmarkoV/PZP/HEAD/setup.py>
  - <https://raw.githubusercontent.com/AmmarkoV/PZP/HEAD/PZP.py>
- **Sources the enricher read:**
  - <https://github.com/AmmarkoV/PZP>
  - <https://github.com/AmmarkoV/PZP/commits>
  - <https://github.com/AmmarkoV/PZP/commits/main/doc/performance.md>
  - <https://github.com/AmmarkoV/PZP/commits/main/README.md>
  - <https://github.com/AmmarkoV/PZP/issues?q=is%3Aissue>
  - <https://github.com/AmmarkoV/PZP/pulls?q=is%3Apr>
  - <https://raw.githubusercontent.com/AmmarkoV/PZP/HEAD/README.md>
  - <https://raw.githubusercontent.com/AmmarkoV/PZP/HEAD/doc/performance.md>
  - <https://raw.githubusercontent.com/AmmarkoV/PZP/HEAD/doc/scripts.md>
  - <https://raw.githubusercontent.com/AmmarkoV/PZP/HEAD/doc/c-api.md>
  - <https://raw.githubusercontent.com/AmmarkoV/PZP/HEAD/doc/file-format.md>
  - <https://raw.githubusercontent.com/AmmarkoV/PZP/HEAD/doc/python-api.md>
  - <https://raw.githubusercontent.com/AmmarkoV/PZP/HEAD/scripts/compare_load_speed.py>
  - <https://raw.githubusercontent.com/AmmarkoV/PZP/HEAD/scripts/benchmark.py>
  - <https://raw.githubusercontent.com/AmmarkoV/PZP/HEAD/scripts/vendorIntoDataLoader.sh>
  - <https://raw.githubusercontent.com/AmmarkoV/PZP/HEAD/Makefile>
  - <https://raw.githubusercontent.com/AmmarkoV/PZP/HEAD/setup.py>
  - <https://raw.githubusercontent.com/AmmarkoV/PZP/HEAD/pyproject.toml>
  - <https://raw.githubusercontent.com/AmmarkoV/PZP/HEAD/PZP.py>
  - <https://raw.githubusercontent.com/AmmarkoV/PZP/HEAD/pzp.h>
  - <https://raw.githubusercontent.com/AmmarkoV/PZP/HEAD/pzp_lib.c>
  - <https://raw.githubusercontent.com/AmmarkoV/PZP/HEAD/pzp.c>
  - <https://raw.githubusercontent.com/AmmarkoV/PZP/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/AmmarkoV/PZP/bc7a2b8/README.md>
  - <https://raw.githubusercontent.com/AmmarkoV/PZP/8bc3e6a/README.md>
  - <https://raw.githubusercontent.com/AmmarkoV/PZP/8cc0f44/README.md>
  - <https://raw.githubusercontent.com/AmmarkoV/PZP/b8911e9/README.md>
  - <https://raw.githubusercontent.com/AmmarkoV/PZP/bc7a2b8/pzp.h>
  - <https://raw.githubusercontent.com/AmmarkoV/PZP/bc7a2b8/scripts/compare_load_speed.py>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/ammarkov/pzp`) · [data/wave10/enrich/raw/github_com_ammarkov_pzp.json](../../../data/wave10/enrich/raw/github_com_ammarkov_pzp.json) (enrichment confidence 0.72)

</details>
