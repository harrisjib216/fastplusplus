# CharLS

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> C++17 JPEG-LS (ISO 14495-1) lossless/near-lossless codec; encodes about 10x faster than libwebp lossless, decodes slower.

| | |
|---|---|
| **Beats** | WebP lossless via Pillow 10.1.0 (libwebp, quality=100, method 1 and 5), Pillow PNG plugin (zlib, not libpng) and Pillow JPEG 2000 plugin (OpenJPEG), all run in-process in Image-Compression-Benchmark; the CharLS README separately cites the original HP JPEG-LS code, JPEG-XR and JPEG 2000 |
| **Claimed result** | Image-Compression-Benchmark, CLIC2021 (585 RGB images, 4.1 GB; times in seconds, measured with time.time() in RunBenchmark.py): JPEG-LS (CharLS via pillow-jpls) compress 72.237 / decompress 66.567, size 1931584595 bytes. Versus WebP lossless m1 (libwebp) 720.160 / 37.044, 1496478650 bytes: about 10.0x faster compression but 1.8x slower decompression and 29% larger output (derived from page data); versus WebP lossless m5 1112.134 / 49.442: 15.4x faster compression, 1.35x slower decompression (derived from page data). Versus Pillow PNG (optimize=False, zlib) 334.791 / 33.677: 4.6x faster compression, about 2x slower decompression, slightly smaller output. Versus Pillow JPEG2000 (OpenJPEG) 319.912 / 275.398: 4.4x and 4.1x faster (derived from page data). CharLS README: 'about twice as fast as the original HP code, and beats both JPEG-XR and JPEG 2000 by a factor 3' (cites imagecompression.info, not opened). |
| **Workload** | Lossless compression and decompression of 585 CLIC2021 RGB 24-bit images (4.1 GB), single-threaded, total time and total size, using the CharLS-based pillow-jpls 1.3.2 plugin. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7 12700H, 16GB DDR4-3200, Windows 10 |
| **Compiler and flags** | Python 3.9, Pillow 10.1.0, pillow-jpls 1.3.2 wheel (links CharLS 2.4.2 statically via Conan per its conanfile.txt); wheel compiler and flags not stated |
| **Adoption** | 224 stars; used by GDCM (per README) |
| **Last commit** | 2026-10-02 |
| **Links** | [repository](https://github.com/team-charls/charls) · [benchmark](https://raw.githubusercontent.com/WangXuan95/Image-Compression-Benchmark/HEAD/README.md) |

## Verdict

In WangXuan95/Image-Compression-Benchmark (CLIC2021, 585 RGB images, 4.1 GB, single thread, Intel i7-12700H, Windows 10), CharLS 2.4.2 via the pillow-jpls 1.3.2 wheel took 72.2 s to encode and 66.6 s to decode versus 720.2 s / 37.0 s for libwebp lossless m1 and 334.8 s / 33.7 s for Pillow's zlib PNG, so it wins on encode only. The times include Python Image.open/save and PNM file I/O per image, the wheel's compiler flags are unstated, and RunBenchmark.py ships with CHECK_DISTORTION = False, so lossless round-trips are not checked by default.

## Use it when

- You must read or write JPEG-LS: DICOM transfer syntaxes 1.2.840.10008.1.2.4.80/.81, remote sensing or archives that mandate an ISO standard lossless codec.
- Lossless encoding of 8-bit RGB or grayscale at high volume where encode time matters more than file size: about 10x faster encode than libwebp lossless (quality=100) and 4.6x faster than Pillow's zlib PNG on CLIC2021.
- 12- to 16-bit medical, scientific or camera-raw-like single-channel images, which PNG handles poorly and QOI-family codecs do not support.
- Near-lossless coding with a hard per-pixel error bound (NEAR parameter), which the PNG/QOI siblings cannot do.
- You want a mature, standards-conformant library with a stable C ABI, vcpkg/Conan packages and .NET, WebAssembly and Python adapters.

## Skip it when

- Decode-heavy workloads of 8-bit RGB: in the CLIC2021 run CharLS decoded about 1.8x slower than libwebp lossless m1 and about 2x slower than Pillow's zlib PNG decoder.
- When ratio is the goal: its CLIC2021 output was 29% larger than WebP lossless m1 and larger than JPEG XL -e1, which also encoded faster (43.0 s vs 72.2 s).
- When raw speed with any format is acceptable: QOI, QOIR, fNBLI and HALIC beat it on both encode and decode in the same table.
- Web delivery: browsers do not decode JPEG-LS.
- Files using JPEG-LS Part 2 extensions, encoded restart markers, subsampled scans or point transform: the README lists these as unsupported (restart markers decode only, with no recovery for corrupted streams).

## How it is fast

The algorithm itself is light: per-pixel median edge detector (MED) prediction, gradient-quantized context modeling with bias correction, adaptive Golomb-Rice coding of residuals and a run mode for flat regions. CharLS compiles specialized codecs per sample type through C++ templates and traits (lossless_traits for 8/16-bit pair/triplet/quad pixels in sample-interleaved mode), uses precomputed gradient-quantization LUTs and per-k Golomb decode LUTs for codes of 8 bits or less, a 64-bit bit cache read with big-endian unaligned loads plus memchr to skip ahead to the next 0xFF stuffing byte, and countl_zero for unary prefixes. There is no SIMD; unreleased main-branch PRs by cl445 add more (#361 skips sample reconstruction in the lossless encoder: 473 to 452 ms on Ryzen 9 9950X/GCC 14, 428 to 370 ms on Apple Silicon for a 7680x4320 12-bit image; #376 PGO-derived branch hints and cold-path outlining: decode 8.5% and encode 3.6% faster on x86-64 Clang 20 for one 7216x5412 8-bit image), none of which the catalogued 2.4.2 numbers include.

## Compared with alternatives

Pick CharLS over QOI, QOIR, fNBLI or HALIC when you need an ISO/ITU standard format (DICOM) or more than 8 bits per sample; pick fpng/fpnge or libjxl fast_lossless instead when you need browser-readable output, and OpenJPH when the format is HTJ2K rather than JPEG-LS.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (CMake, vcpkg, Conan; source-only, no binary releases) |
| **Dependencies** | none |
| **Minimum toolchain** | main branch: C++17, CMake 3.22, GCC 9.1, Clang 7, MSVC 2019, Apple Clang 12; 2.x LTS branch: C++14 |
| **Platforms** | Windows, Linux, macOS on x86, x64, arm, arm64, mips, s390x, ppc64le (big-endian fixed in 2.3.3); portable C++, no SIMD |
| **Thread safety** | not documented; each encoder/decoder is a separate handle and the shared Golomb and quantization tables are immutable statics (read from source), so one instance per thread is the safe pattern |
| **Drop-in for the baseline** | no |

## Gotchas

- Releases 2.3.0 through 2.4.3 have GHSA-mqrg-gfc8-73ff (CVSS 5.3): a crafted oversize-dimension LSE marker wraps pixel_stride and causes out-of-bounds access; fixed in 2.4.4, which caps width and height at 100000. pillow-jpls 1.3.2, still the latest wheel on PyPI and the one benchmarked, statically links vulnerable CharLS 2.4.2.
- main is the unreleased 3.0 with breaking API changes (charls.h split into charls.h/charls.hpp, legacy 1.x API removed, include_pc_parameters_jai no longer default); 2.4.4 is the latest tagged release.
- Hewlett Packard claims JPEG-LS patents, licensed free for conformant implementations; the README tells commercial users to check hpl.hp.com/loco.
- The fast specialized paths cover lossless 8-bit and 16-bit data (sample-interleaved pairs, triplets and quads); near-lossless and other bit depths go through the generic default_traits path.

## Known shortcomings

- Tier B on the independent Image-Compression-Benchmark (RunBenchmark.py, i7-12700H, Python wheels with unstated flags; pillow-jpls 1.3.2 bundles CharLS 2.4.2). Against Pillow WebP (libwebp): encode 10x faster (720.160 vs 72.237 s total), decode 1.8x slower, files 29% larger. JPEG-LS is a different format from WebP or PNG.
- The measured pillow-jpls 1.3.2 (still the latest on PyPI) links CharLS 2.4.2, affected by GHSA-mqrg-gfc8-73ff (CVSS 5.3, pixel_stride wrap, out-of-bounds; fixed in 2.4.4); the harness RunBenchmark.py ships CHECK_DISTORTION = False so the lossless round trip is unchecked by default, and times include Python and PNM I/O. Unreleased main carries encoder and decoder speedups (#361: 4.4% on x86, 13.6% on ARM).

## Caveats and trade-offs

The page does compare against a listed baseline: Pillow's WebP plugin is libwebp. Against it CharLS wins only on encode (about 10x vs WebP lossless with quality=100, which is libwebp's maximum-effort lossless setting) and loses on decode (1.8x slower) and ratio (29% larger). Pillow's PNG codec uses zlib directly rather than libpng, and Pillow's JPEG 2000 plugin is OpenJPEG. All Pillow-based rows (PNG, WebP, JPEG 2000, JPEG-LS) run in-process through exec() with the same PNM read/write overhead, so they are comparable to each other, while EXE-based codecs include per-file process startup. JPEG-XL -e1 (43.0 s / 57.7 s, smaller files) and QOI/fNBLI beat JPEG-LS on the same table, so CharLS is not the fastest lossless codec here. The README's 'twice as fast as HP code' claim rests on an unopened, dated imagecompression.info page. The 'JPEG-LS-ext' row is a different codec (ImCvt) and is not counted.

JPEG-LS (ISO/IEC 14495-1) is a lossless/near-lossless codec with low complexity; decode is about twice as slow as Pillow's PNG decode in the cited suite. README notes Hewlett Packard patents on JPEG-LS (licensed free for conformant implementations; some may have expired). No SIMD: speed comes from templates and traits.

## Maintenance

Actively maintained (last commit 2026-10-02; 2.4.4 security release in June 2026, 3.0 encoder speedups merged on main), BSD-3-Clause and copyable, with libFuzzer/AFL harness options in the build.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now B.
- **Tier reason:** Independent third-party suite (WangXuan95/Image-Compression-Benchmark, RunBenchmark.py public, Intel Core i7-12700H stated) times CharLS via pillow-jpls against Pillow's WebP lossless (libwebp), PNG (zlib) and JPEG 2000 (OpenJPEG) plugins; the CharLS wheel's compiler and flags are not stated, so not A.
- **Verifier notes:** Numbers match the CLIC2021 table exactly; units confirmed as seconds from RunBenchmark.py. The record's caveat that no listed baseline is compared was wrong (libwebp via Pillow), so baseline_in_list is now true, but the win over libwebp is encode-only. Metadata checked: BSD-3-Clause, 224 stars, last commit 2026-10-02 (dependabot), GDCM listed as a user in the README.
- **Fields the verifier corrected:** `baseline`, `baseline_in_list`, `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/WangXuan95/Image-Compression-Benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/WangXuan95/Image-Compression-Benchmark/HEAD/RunBenchmark.py>
  - <https://pypi.org/pypi/pillow-jpls/1.3.2/json>
  - <https://raw.githubusercontent.com/planetmarshall/pillow-jpls/v1.3.2/conanfile.txt>
  - <https://raw.githubusercontent.com/planetmarshall/pillow-jpls/v1.3.2/CMakeLists.txt>
  - <https://raw.githubusercontent.com/team-charls/charls/HEAD/README.md>
  - <https://github.com/team-charls/charls>
  - <https://github.com/team-charls/charls/commits/main>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/team-charls/charls/HEAD/README.md>
  - <https://github.com/team-charls/charls/tree/main/src>
  - <https://github.com/team-charls/charls/issues>
  - <https://raw.githubusercontent.com/team-charls/charls/HEAD/src/scan_encoder_impl.hpp>
  - <https://raw.githubusercontent.com/team-charls/charls/HEAD/src/scan_decoder_impl.hpp>
  - <https://raw.githubusercontent.com/team-charls/charls/HEAD/src/scan_decoder.hpp>
  - <https://raw.githubusercontent.com/team-charls/charls/HEAD/src/scan_encoder.hpp>
  - <https://raw.githubusercontent.com/team-charls/charls/HEAD/src/jpegls_algorithm.hpp>
  - <https://raw.githubusercontent.com/team-charls/charls/HEAD/src/golomb_lut.cpp>
  - <https://raw.githubusercontent.com/team-charls/charls/HEAD/src/quantization_lut.cpp>
  - <https://raw.githubusercontent.com/team-charls/charls/HEAD/src/make_scan_codec.cpp>
  - <https://raw.githubusercontent.com/team-charls/charls/HEAD/src/CMakeLists.txt>
  - <https://raw.githubusercontent.com/team-charls/charls/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/team-charls/charls/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/team-charls/charls/HEAD/SECURITY.md>
  - <https://raw.githubusercontent.com/team-charls/charls/HEAD/include/charls/charls_jpegls_encoder.h>
  - <https://raw.githubusercontent.com/team-charls/charls/HEAD/include/charls/charls_jpegls_decoder.h>
  - <https://github.com/team-charls/charls/security/advisories/GHSA-mqrg-gfc8-73ff>
  - <https://github.com/team-charls/charls/pulls?q=is%3Apr+performance>
  - <https://github.com/team-charls/charls/pull/376>
  - <https://github.com/team-charls/charls/pull/361>
  - <https://github.com/team-charls/charls/releases>
  - <https://raw.githubusercontent.com/WangXuan95/Image-Compression-Benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/WangXuan95/Image-Compression-Benchmark/HEAD/RunBenchmark.py>
  - <https://github.com/planetmarshall/pillow-jpls/tree/v1.3.2/src>
  - <https://raw.githubusercontent.com/planetmarshall/pillow-jpls/v1.3.2/src/pycharls.cpp>
  - <https://raw.githubusercontent.com/planetmarshall/pillow-jpls/v1.3.2/conanfile.txt>
  - <https://pypi.org/pypi/pillow-jpls/json>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/team-charls/charls`) · [data/wave10/enrich/raw/github_com_team_charls_charls.json](../../../data/wave10/enrich/raw/github_com_team_charls_charls.json) (enrichment confidence 0.8)

</details>
