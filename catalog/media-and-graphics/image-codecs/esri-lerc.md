# LERC (Limited Error Raster Compression)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Esri's raster codec with a per-pixel error bound for 8- to 64-bit integer and float tiles; encodes far faster than zlib level 9.

| | |
|---|---|
| **Beats** | zlib deflate level 9 (labelled 'LZW' in the benchmark document; called through compress2) |
| **Claimed result** | From doc/LercBenchmarks_Feb_2016.pdf, times against zlib compress2 level 9 (labelled 'LZW'), tiled at 1024. Lossless (MaxZError 0) rows only: DTED-2 16-bit 3601x3601, average encode 231 ms vs 2484 ms and decode 51 ms vs 130 ms (about 10.8x and 2.5x, derived from page data); DTED-1 16-bit 1201x1201, encode 23 ms vs 274 ms and decode 7 ms vs 16 ms (about 11.9x and 2.3x, derived from page data); multispectral 11/16-bit images, encode 2.4 s vs 30.5 s and decode 0.7 s vs 1.8 s (about 12.7x and 2.6x, derived from page data; the document's prose says 'the much faster encoding speed of 5-10x'). Lossless compression-ratio averages are 5.1 vs 4.2, 6.2 vs 5.8 and 2.1 vs 1.8, but zlib compresses better on the flat Georgia tiles (4.9 vs 4.6 and 7.1 vs 5.3). Lossy rows (not the same work as lossless zlib): float scientific rasters at MaxZError 0.01 encode 0.3 s vs 8.1 s and decode 68 ms vs 424 ms; interpolated float DTED surfaces at 0.01 encode 0.4 s vs 4.3 s and 3.4 s vs 40.5 s. README: encode about 20-30 ms and decode about 5 ms per megapixel per band (no machine stated). |
| **Workload** | Tile-by-tile (max tile 1024) encode and decode of geospatial rasters with LERC against zlib compress2 level 9: four 4600x4300 float scientific rasters and two interpolated float DTED surfaces (3612x3612 and 10812x10812), lossy only (MaxZError 0.01 to 1.0); four DTED-1 (1201x1201) and four DTED-2/ASTER (3601x3601) 16-bit elevation tiles, lossless and at MaxZError 5; six multispectral 11/16-bit aerial and satellite images (UltraCam, QuickBird, RapidEye), lossless and at MaxZError 2 and 4. |
| **Metric** | throughput |
| **Adoption** | 215 stars; vcpkg port lerc and Conan recipe lerc; README says it is used in Esri software |
| **Last commit** | 2026-09-17 |
| **Links** | [repository](https://github.com/Esri/lerc) · [benchmark](https://raw.githubusercontent.com/Esri/lerc/master/doc/LercBenchmarks_Feb_2016.pdf) |

## Verdict

Esri's own 2016 PDF, which predates LERC 1.0 and runs zlib compress2 level 9 on raw samples without a predictor (mislabelled 'LZW'), reports lossless LERC encodes 16-bit DTED and multispectral tiles about 11-13x faster and decodes them about 2.3-2.6x faster (derived from page data), at a slightly better average ratio. The float rows are lossy only (MaxZError 0.01 and up). No CPU, OS, compiler or flags are given, and the driver and test rasters are not published.

## Use it when

- Elevation models, scientific float grids and 11-16-bit multispectral imagery where you can name a tolerable absolute error (e.g. 0.01 m), so lossy encoding gives several times the ratio of lossless deflate at a known bound.
- Tile servers and caches that encode on the fly: the 2016 PDF shows about 10-13x faster encode than zlib level 9 on lossless 16-bit tiles (231 vs 2484 ms per 3601x3601 DTED-2 tile).
- Rasters with void areas: the valid-pixel mask is RLE-coded and masked pixels cost nothing, and lerc_getDataRanges reads per-band min/max without decoding.
- GDAL GeoTIFF/COG or MRF pipelines (COMPRESS=LERC with MAX_Z_ERROR) and ArcGIS-compatible services, where readers already exist in C++, Python, JS and C#.

## Skip it when

- 8-bit RGB or photographic imagery: the README itself says PNG compresses 8-bit lossless better and recommends JPEG where it is good enough.
- Plain lossless speed against a modern compressor: one third-party GDAL test (gpxz.io, 3600x3600 float32 Copernicus DEM, 512x512 blocks; search snippet only, page blocked) measured zstd at 519 MB/s write and 957 MB/s read, against 315 and 473 for LERC at MAX_Z_ERROR 1e-5 (lossy) and 33 and 253 for DEFLATE. LERC's ratio there was 1.9, zstd's 1.5.
- Low-entropy integer tiles with small value ranges: zlib out-compressed lossless LERC on the flat Georgia DTED tiles in the vendor's own PDF (4.9 vs 4.6 and 7.1 vs 5.3).
- Big-endian hosts: Lerc2 encode, decode, header and range calls return failure unless the machine is little-endian with 4-byte int.
- Whole large images in one blob: since 4.2 a blob is capped at 2 GB per band and 4 GB overall, and the API notes say LERC is meant for tiles.

## How it is fast

Lerc2 splits the tile into 8x8 micro-blocks (retrying at 16x16 when that is smaller). For each block it stores min/max, quantizes n = (x - min)/(2\*MaxZError) + 0.5 to unsigned ints, and bit-stuffs them with ceil(log2(range+1)) bits, optionally through a lookup table of distinct values; constant and empty blocks cost only a header. That is one scalar pass with no match search, which is why encode is much faster than deflate's level-9 lazy matching. Lossless 8-bit data can switch to delta plus Huffman coding, and lossless float/double (since 4.0) to a delta-delta Huffman path kept only when it is at least 10% smaller. The encoder also detects floats that sit on a decimal grid (multiples of 0.1, 0.01 and so on) and raises MaxZError to half that step for free. There is no SIMD and no threading in the code.

## Compared with alternatives

Pick LERC when the data is float, double or 32-bit integer, or when you need a hard per-pixel error bound with masks. CharLS (JPEG-LS NEAR mode) bounds error only for integer samples up to 16 bits, and OpenJPH or Grok (JPEG 2000) fit 8-16-bit imagery that needs JPEG 2000 interoperability. For exact float storage, meshoptimizer's vertex codec is the catalogued lossless alternative.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (CMake; BUILD_SHARED_LIBS defaults to ON); vcpkg and Conan packages exist |
| **Dependencies** | none |
| **Minimum toolchain** | C++17, CMake 3.12 (Visual Studio, Code::Blocks and Xcode project files also provided) |
| **Platforms** | little-endian only (Windows, Linux, macOS; WASM decoder via Emscripten); no SIMD, so any little-endian CPU |
| **Thread safety** | Not documented. The C API entry points are static and build a local Lerc2 object per call with no global state (by code reading), so concurrent calls on separate buffers look safe. |
| **Drop-in for the baseline** | no |

## Gotchas

- MaxZError is a bound before the float cast: decode computes zMin + n\*2\*MaxZError in double and casts to T, and the sample program subtracts a 0.0001 'safety margin ... to account for finite floating point accuracy' from the wanted error.
- For integer types MaxZError is floored and clamped to at least 0.5, so 0 means exact and 0.7 behaves like 0.5. A negative MaxZError on integers switches to bit-plane noise compression, and the undocumented value 777 maps to -0.01.
- lerc_encode always runs a full sizing pass first (tiling, Huffman tries and a 16x16 retry) and then writes, so calling lerc_computeCompressedSize beforehand repeats that work; closed issue #197 notes lerc_encode can return fewer bytes than that estimate.
- NaNs are never returned: they are moved into the mask, or in the mixed nDepth case replaced by the noData value (encode fails if none is set). Release 4.1.1 (2026-07-02) 'fixed two security issues' with no published advisory, and 4.2.0 added size and overflow checks, so use 4.2.0 or later on untrusted blobs.

## Known shortcomings

- The numbers come from the first-party doc/LercBenchmarks_Feb_2016.pdf with no CPU, compiler or flags; the benchmark driver and ZLibAccess.h are not published and the data is not in testData/. Only the MaxZError 0 integer rows are like-for-like with lossless zlib-9 (encode 10.8-12.7x, decode 2.3-2.6x, derived from page data); the float rows are lossy-by-tolerance, different work, and zlib-9 compresses better on 2 tiles.
- The benchmark's zlib baseline is level 9 with no predictor and is mislabelled LZW in the PDF; encode and decode fail on big-endian hosts; 4.1.1 fixed two unpublished security issues.

## Caveats and trade-offs

LERC is lossy-by-tolerance: the caller sets MaxZError, and only MaxZError 0 is lossless, so only the DTED-1, DTED-2 and multispectral LERC (0) columns do the same work as lossless zlib. All float-raster rows were run lossy (0.01 to 1.0), since lossless float/double compression only arrived in LERC 4.0 (2022-07-15). The PDF dates from 2016-02-23, before LERC 1.0 (2016-11-30), so it measured a much older codec than the current Lerc2 v6. It states no CPU, OS, compiler or flags; the benchmark driver and the ZLibAccess.h wrapper are not in the repo, and the large test rasters (UltraCam, QuickBird, RapidEye, DTED and ASTER tiles) are not in testData/, so the run cannot be reproduced. The baseline is zlib level 9 (its slowest level) on raw samples with no TIFF predictor; the PDF says level 6 gave a similar overall picture but gives no level-6 numbers. Not a general photographic codec; for 8-bit data the README says PNG can compress better.

Special-purpose raster codec for 16-bit and larger or float data with a bounded per-pixel error (MaxZError); lossless only for integer types with MaxZError 0 and only slightly better ratio than zlib there. The README itself says PNG can compress 8-bit data better.

## Maintenance

Actively maintained (4.2.0 released 2026-07-23, last commit 2026-09-17), Apache-2.0 and dependency-free, so it is easy to vendor; it ships in Esri ArcGIS and GDAL.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** doc/LercBenchmarks_Feb_2016.pdf (Thomas Maurer, Esri, 2016-02-23) is checked into the repo and carries every quoted table against zlib compress2 level 9, but it states no CPU, OS, compiler or flags, the benchmark driver and its ZLibAccess.h wrapper are not published (src/LercTest/main.cpp times LERC alone), and the test rasters are not in testData/; first-party, so C.
- **Verifier notes:** The benchmark PDF is in the repo and every number in the record matches it; I added the DTED-1 and multispectral lossless rows, the zlib-wins rows and the lossy-only status of the float rows. Apache-2.0, 215 stars, 72 forks, last commit 2026-09-17 (active) confirmed on github.com.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `caveats`
- **Shortcomings recorded by:** Independent GDAL test (gpxz.io/blog/lerc-benchmarks, search snippet only; page blocked here), Copernicus DEM float32: LERC at 1e-5 tolerance writes 315 MB/s and reads 473 MB/s at ratio 1.9; DEFLATE 33/253 MB/s at ratio 1.6; zstd 519/957 MB/s at ratio 1.5, so zstd is faster than LERC on that data.
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/Esri/lerc/master/doc/LercBenchmarks_Feb_2016.pdf>
  - <https://raw.githubusercontent.com/Esri/lerc/HEAD/README.md>
  - <https://github.com/Esri/lerc>
  - <https://github.com/Esri/lerc/commits>
  - <https://github.com/Esri/lerc/tree/master/src/LercTest>
  - <https://github.com/Esri/lerc/tree/master/src/LercLib>
  - <https://raw.githubusercontent.com/Esri/lerc/master/src/LercTest/main.cpp>
  - <https://raw.githubusercontent.com/Esri/lerc/master/doc/MORE.md>
  - <https://raw.githubusercontent.com/Esri/lerc/master/CHANGELOG.md>
- **Sources the enricher read:**
  - <https://github.com/Esri/lerc>
  - <https://raw.githubusercontent.com/Esri/lerc/master/README.md>
  - <https://raw.githubusercontent.com/Esri/lerc/master/doc/MORE.md>
  - <https://raw.githubusercontent.com/Esri/lerc/master/CHANGELOG.md>
  - <https://raw.githubusercontent.com/Esri/lerc/master/doc/LercBenchmarks_Feb_2016.pdf>
  - <https://raw.githubusercontent.com/Esri/lerc/master/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Esri/lerc/master/src/LercLib/include/Lerc_c_api.h>
  - <https://raw.githubusercontent.com/Esri/lerc/master/src/LercLib/include/Lerc_types.h>
  - <https://raw.githubusercontent.com/Esri/lerc/master/src/LercLib/Lerc_c_api_impl.cpp>
  - <https://raw.githubusercontent.com/Esri/lerc/master/src/LercLib/Lerc.h>
  - <https://raw.githubusercontent.com/Esri/lerc/master/src/LercLib/Lerc.cpp>
  - <https://raw.githubusercontent.com/Esri/lerc/master/src/LercLib/Lerc2.h>
  - <https://raw.githubusercontent.com/Esri/lerc/master/src/LercLib/Lerc2.cpp>
  - <https://raw.githubusercontent.com/Esri/lerc/master/src/LercLib/BitStuffer2.cpp>
  - <https://raw.githubusercontent.com/Esri/lerc/master/src/LercLib/Huffman.cpp>
  - <https://raw.githubusercontent.com/Esri/lerc/master/src/LercLib/RLE.cpp>
  - <https://raw.githubusercontent.com/Esri/lerc/master/src/LercLib/fpl_Lerc2Ext.cpp>
  - <https://raw.githubusercontent.com/Esri/lerc/master/src/LercTest/main.cpp>
  - <https://github.com/Esri/lerc/issues?q=is%3Aissue>
  - <https://github.com/Esri/lerc/issues?q=is%3Aissue&page=2>
  - <https://github.com/Esri/lerc/issues/220>
  - <https://github.com/Esri/lerc/issues/138>
  - <https://github.com/Esri/lerc/security>
  - <https://github.com/kokoalberti/geotiff-benchmark>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/esri/lerc`) · [data/wave10/enrich/raw/github_com_esri_lerc.json](../../../data/wave10/enrich/raw/github_com_esri_lerc.json) (enrichment confidence 0.8)

</details>
