# opencodecs

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Python (Cython and C/C++ extensions)` · `BSD-3-Clause` · 🟢 active

> Python imaging-codec package over libdeflate, libspng, libjpeg-turbo, OpenJPEG and libjxl, with its own TIFF LZW decoder about 2x faster than imagecodecs'.

| | |
|---|---|
| **Beats** | imagecodecs (Python wrappers over libjpeg-turbo, libpng, libwebp, OpenJPEG, libjxl and others) and tifffile for TIFF reading |
| **Claimed result** | README 'Codecs against imagecodecs' (opencodecs 0.5.0 vs imagecodecs 2026.8.16; Mac / Linux / Windows): TIFF-flavor LZW decode 3.33x / 3.07x / 2.94x and LZW encode 1.33x / 1.32x / 1.49x (own kernels, single-threaded); the enricher's like-for-like re-run (imagecodecs given out=) gives LZW decode 2.15-2.17x. PackBits decode 3.32x / 2.81x / 1.52x is a harness artifact (1.02x like-for-like). PNG RGB uint8 level 6 encode 3.45x / 3.68x / 1.12x and deflate level 6 encode 2.69x / 2.58x / 2.61x compare libdeflate against imagecodecs' zlib path; against imagecodecs.deflate_encode (libdeflate) it is parity (519 vs 537 ms, identical bytes). JPEG quality 90 encode 2.68x / 3.91x / 0.97x and decode 1.56x / 1.80x / 1.01x: the Linux rows reflect imagecodecs' manylinux libjpeg-turbo being built without SIMD; Windows is at parity. Rows marked 'opencodecs threaded' (several threads vs one): JPEG 2000 lossless encode 8.05x / 4.66x / 2.73x and decode 7.64x / 4.57x / 2.71x; JPEG XL 2.30x to 10x; BC7 decode 11x / 5.47x / 4.09x and BC1 decode 4.45x / 1.79x / 2.27x (vendored bcdec plus threads, not own kernels; below 1x per core, JPEG 2000 Linux encode about 0.63x per core). Many rows are at 0.72x to 1.05x (zstd, lz4, brotli, blosc2, lzma, bz2, snappy, WebP, QOI, JPEG-LS, ZFP). README 'TIFF against tifffile' (4096x4096 uint16 tiled deflate+predictor): Linux 4.2x one reader at defaults, 1.4x forced single thread, 10.0x with 8 concurrent readers; Mac 3.3x / 1.1x / 3.9x; single-thread cells 0.95x to 2.4x. |
| **Workload** | Codec table: bench/bench_vs_imagecodecs.py, one codec operation per row at matched settings, opencodecs 0.5.0 against imagecodecs 2026.8.16. Each sample is a fresh Python process that imports one library and times one case (median of 5 to 40 calls after one warm-up); the driver alternates the two libraries in shuffled order for 5 rounds and the table cell is the ratio of round medians. Inputs are a synthetic 4096x4096 uint16 field (sin/cos plus Gaussian noise; 32 MB, 8 MB slice for lzma/bz2, 16 MB uint8 for LZW/PackBits) and 2048x2048 RGB uint8, uint16 and float32 views of it; BC1/BC7 decode random block bytes. Decode rows decode one imagecodecs-written bitstream and require identical output digests; lossless encode rows must round-trip. TIFF table: reads of tifffile-written files (4096x4096 uint16 tiled/striped, 3072x3072 uint8 with 144 tiles) against tifffile 2026.3.3 (Mac) and 2026.5.2 (Linux), median over fresh alternating processes, with both libraries at defaults, both forced to one thread, and 8 concurrent readers. |
| **Metric** | throughput |
| **Hardware** | 20-core Apple silicon Mac (arm64, macOS), 64-core x86-64 Linux workstation whose cores sit in 16 four-core L3 groups, each measured process pinned to CPUs 8-11,72-75 (one group, 8 hardware threads, per linux.json metadata), and a 4-core x86-64 Windows laptop; exact CPU models not stated anywhere checked. |
| **Compiler and flags** | Not stated with the tables beyond 'opencodecs 0.5.0 built as its CI wheels are' (TIFF table). README says vendored scientific compressors are source-built with -O3, LTO and hidden visibility; bench/README.md lists macOS 15.5 clang (Xcode) and Ubuntu gcc 13 for older regression baselines. imagecodecs 2026.8.16 from its own wheels. Python 3.12.13 (Linux), 3.12.9 (Mac), 3.12.6 (Windows) per result-file metadata. Harness: bench/bench_vs_imagecodecs.py. |
| **Adoption** | 3 stars, 0 forks, 463 commits; published on PyPI (0.5.0 on 2026-10-02, 0.6.0 on 2026-10-03, 0.7.0 on 2026-10-04) |
| **Last commit** | 2026-10-04 |
| **Links** | [repository](https://github.com/kevinjohncutler/opencodecs) · [benchmark](https://github.com/kevinjohncutler/opencodecs) |

## Verdict

Author's harness (bench/bench_vs_imagecodecs.py): opencodecs 0.5.0 against imagecodecs 2026.8.16 with Python 3.12, a fresh process per sample, medians over 5 shuffled rounds, identical decoded output required. Hosts were an unnamed 20-core Apple silicon Mac, a 64-core x86-64 Linux workstation pinned to one 4-core L3 group (source comments mention Zen 2) and a 4-core x86-64 Windows laptop (Kaby Lake per source comments); no CPU models or build flags are given. Reading the harness and imagecodecs' source turned up four measurement problems. (1) The harness passes the output size to opencodecs' LZW and PackBits decoders but calls imagecodecs.lzw_decode(b) and packbits_decode(b) without out=, which makes imagecodecs run a full size pre-pass (imcd_lzw_decode_size, imcd_packbits_decode_size) first. In an enricher rerun on the same PyPI wheels (opencodecs 0.5.0, imagecodecs 2026.8.16, Python 3.12, harness input, 4-vCPU Intel Xeon @ 2.80GHz container, three runs of 15 interleaved calls each), LZW decode went from 2.71-2.80x as harnessed to 2.15-2.17x with out=n. PackBits went from 1.79-1.85x to 1.02x: the README's PackBits decode win (3.32x/2.81x/1.52x) is a harness artifact, and its input expands under PackBits (16,908,288 bytes from 16,777,216). (2) The deflate and PNG rows use imagecodecs' zlib codecs, although imagecodecs ships libdeflate (deflate_encode), which matched opencodecs (519 vs 537 ms, byte-identical output). (3) The imagecodecs 2026.8.16 manylinux x86-64 wheel's libjpeg-turbo 3.2.0 has no SIMD: objdump shows 0 ymm and 0 pmaddwd instructions, against 4,133 and 565 in opencodecs' bundled copy. Rerun JPEG q90 encode was 24.8 vs 94.4 ms with identical 2,437,855-byte output, so the Linux JPEG rows (3.91x/1.80x) reflect the baseline's packaging. (4) The threaded rows compare thread counts, not per-core speed. The general compressor rows also use near-incompressible data: deflate and zstd reach about 91% of input, and lz4 and snappy output exceeds input, so their decode rows are mostly copies.

## Use it when

- Python pipelines that read LZW-compressed TIFF strips or tiles: the LZW decoder is about 2.2x faster than imagecodecs.lzw_decode like for like (enricher rerun, below) and 2.9-3.3x in the README's harness.
- Python scientific-imaging readers (TIFF, OME-TIFF, CZI, NDTiff, OME-Zarr, DICOM WSI) over NVMe, NAS or S3, where per-tile parallel decode and HTTP range reads matter more than single-codec speed. The README measures 1.3x-13.2x over tifffile, depending on threads and readers, but no harness for that table is in bench/.
- Getting libdeflate-backed PNG and zlib-stream encoding (about 2.6x faster than zlib level 6 on the README's data) without assembling the C libraries yourself, if you accept about 0.9% larger PNG output.
- Multi-threaded JPEG 2000 or JPEG XL encode and decode from a single Python call on an otherwise idle machine, where imagecodecs' default runs one thread.
- C or C++ projects that need a small, permissively licensed TIFF LZW encoder and decoder: vendor 3rdparty/oc_tifflzw/ (MIT, plain C).

## Skip it when

- As evidence that its codecs are faster per core: the JPEG 2000, JPEG XL, BC1 and BC7 rows compare several threads against one. Per CPU-second, derived from the result files, opencodecs is about 0.63x on Linux JPEG 2000 encode (703.76 / (151.07 x 7.4)), 0.82x on Mac BC1 decode and 1.05x on Mac BC7 decode.
- Expecting the README's JPEG gains on any machine. The Linux 3.91x encode and 1.80x decode rows measure an imagecodecs wheel whose libjpeg-turbo has no SIMD (see verified_claims_summary). On Windows, where that is not the case, the rows are 0.97x and 1.01x.
- When you already use imagecodecs' libdeflate codec (deflate_encode). In the enricher rerun it wrote byte-identical 30,524,176-byte output at level 6 in 519 ms against opencodecs' 537 ms, so the README's 2.6x deflate encode win disappears.
- Byte compressors (zstd, lz4, brotli, blosc2, lzma, bz2, snappy), WebP, QOI, JPEG-LS, LERC decode and ZFP: they wrap the same libraries as imagecodecs and land at 0.70x-1.26x. ZFP encode is 0.72x on the Mac and 0.70x on Windows.
- Risk-averse or C++-only projects: one author, 3 stars, six PyPI releases in seven days (0.3.1 on 2026-09-28 to 0.7.1 on 2026-10-04), and changelogs that keep fixing writer interoperability bugs (CZI files libCZI could not open, PlanarConfiguration=2 TIFFs, a TIFF predictor 3 codec that did not implement predictor 3).

## How it is fast

The TIFF LZW decoder (oc_tifflzw.c) gives each dictionary entry a pointer and a length into output it has already written, so a code decodes as one copy. Strings of up to 16 bytes move as one or two 8-byte chunks, and literals point into a padded constant table. imagecodecs instead walks each code's linked prefix chain backwards. This is the 'output buffer as dictionary' idea also used by the AnimatedGIF Turbo mode. The other gains come from backend and threading choices rather than new algorithms: PNG and deflate use libdeflate's whole-buffer compressor instead of zlib; JPEG uses a SIMD build of libjpeg-turbo; JPEG 2000, JPEG XL and BC1-BC7 decode run on several threads by default (BCn in row bands through a vendored bcdec with a BC7 fast path for modes without secondary indices). The TIFF reader decompresses a batch of tiles, undoes the predictor and places them in one native call that releases the GIL once.

## Compared with alternatives

Pick it when you work in Python and want one package that both decodes many formats and reads whole scientific containers in parallel (including over HTTP). From C or C++, use the underlying libraries directly instead: libspng plus libdeflate (or fpng/fpnge for speed over ratio) for PNG, libjpeg-turbo for JPEG, OpenJPH or Grok for JPEG 2000, bcdec for BCn. Vendor only oc_tifflzw, which applies to TIFF LZW the output-as-dictionary trick that AnimatedGIF and giflib-turbo use for GIF.

## Integration

| | |
|---|---|
| **Form** | module (Python package: PyPI wheels, about 40 compiled extensions); the TIFF LZW codec is also a C source-drop (3rdparty/oc_tifflzw/) |
| **Dependencies** | numpy and platformdirs at runtime (h5py, zarr optional). The wheels bundle libjxl, libavif, libheif, libwebp, libdeflate, libspng, libjpeg-turbo, OpenJPEG, OpenJPH 0.31.0, c-blosc2, CharLS, zstd, lz4, brotli and others. A source install uses the system libraries it finds and skips the missing ones. |
| **Minimum toolchain** | CPython 3.10-3.13 wheels; source builds need a C/C++17 compiler, Cython, and CMake 3.16+ for the source-built libjxl (bench/build_libjxl.sh). TurboJPEG v3 API (libjpeg-turbo 3.x) is required for the jpeg codec. |
| **Platforms** | Wheels for macOS 15+ arm64, Linux x86_64 and aarch64 (manylinux_2_28), and Windows amd64. Intel Macs and older macOS install from the sdist. |
| **Thread safety** | Codec calls release the GIL (nogil blocks), and the README benchmarks eight concurrent TIFF readers. JPEG 2000, JPEG XL and BCn spawn their own threads per call by default. No formal thread-safety statement found. |
| **Drop-in for the baseline** | partial — it reads and writes the same formats and bitstreams as imagecodecs/tifffile (parity tests against imagecodecs), but the API differs (oc.get_codec(name).encode/decode, oc.read, own Reader objects), so call sites must change. |

## Gotchas

- Defaults differ from imagecodecs: the PNG encoder tries only the NONE, SUB and UP filters ('fast'), where libpng tries all five for 8-bit RGB. AVIF uses a fast preset (bench/README.md: about 90x faster than imagecodecs' high-quality default), and brotli defaults to level 6, not 1. Equal-looking calls can therefore produce different bytes and speeds.
- The opencodecs 0.5.0 Linux wheel bundles libjxl 0.11.2 (the wheel workflow pins LIBJXL_VERSION v0.11.2), while imagecodecs 2026.8.16 bundles 0.12.0. The README footnote says both use 0.12.0. On Linux, lossy JPEG XL decodes differ from imagecodecs' by 1 in about a third of the values, and encode sizes differ.
- Do not load opencodecs and imagecodecs LERC in one process: each statically links libLerc and the second copy aborts (bench_vs_imagecodecs.py docstring and bench/README.md).
- Licensing provenance: CHANGES.rst calls the project a 'fork-then-divergence' of imagecodecs. Issue #1, opened 2026-05-22 by imagecodecs' author, asks for the BSD-3 per-file copyright notices in derived files to be restored and is still open; THIRD-PARTY.md says no imagecodecs code remains beyond .pxd declarations that resemble it.

## Known shortcomings

- The strongest like-for-like row is its own TIFF LZW decode kernel at 2.94-3.33x single-thread over imagecodecs; the threaded rows (JPEG 2000, JPEG XL, BC7) compare multi-thread against single-thread, and the JPEG encode 3.91x on Linux uses the same libjpeg-turbo with identical 2,437,855-byte output (0.97x on Windows). Harness bench/bench_vs_imagecodecs.py and the vs_imagecodecs result JSONs are public with identical-output checks but no CPU model; no harness exists for the TIFF-versus-tifffile table. Off-baseline (imagecodecs, Python).
- Enricher (e111, 2026-10-05) re-ran the harness on PyPI wheels (opencodecs 0.5.0, imagecodecs 2026.8.16, Python 3.12, 4-vCPU Xeon): the harness passes the output size to opencodecs' LZW/PackBits decoders but calls imagecodecs lzw_decode and packbits_decode without out=, so imagecodecs does an extra size pre-pass; LZW decode is 2.71-2.80x as harnessed but 2.15-2.17x like-for-like, and PackBits 1.79-1.85x vs 1.02x, so the PackBits row is an artifact. imagecodecs' manylinux libjpeg-turbo 3.2.0 is built without SIMD (0 ymm, 0 pmaddwd vs 4133/565 in opencodecs' copy), so the Linux JPEG 3.91x/1.80x rows measure baseline packaging (Windows parity). Deflate/PNG rows use imagecodecs' zlib path; imagecodecs.deflate_encode (libdeflate) is parity (519 vs 537 ms, identical bytes). The Linux 0.5.0 wheel bundles libjxl 0.11.2, not the 0.12.0 the README states. BC1/BC7 rows are vendored bcdec plus threads, not own kernels; threaded rows are below 1x per core. Tier C stays; corrections in retier-33.

## Caveats and trade-offs

A Python package (Cython and C/C++ extensions bundling libspng, libdeflate, libjpeg-turbo, OpenJPEG, libjxl and others), not a new codec library. Where both packages wrap the same C library the speedups come from build and binding differences or default threading, not new algorithms: JPEG encode writes byte-identical-size output on both sides (2,437,855 bytes on all three hosts) and is 3.91x on Linux but 0.97x on Windows; JPEG 2000, JPEG XL, BC1 and BC7 rows compare opencodecs' default multi-threaded call (process CPU/wall 4 to 12) against imagecodecs' single-threaded default, so they are not per-core wins. PNG and deflate gains come from libdeflate versus zlib; opencodecs' PNG output is 6,493,730 bytes versus 6,437,751 for imagecodecs (about 0.9% larger, derived from page data). Its own kernels (TIFF LZW, PackBits) are the clean single-thread wins at about 3x. Many rows are at parity or slower (zstd, brotli, blosc2, lzma, ZFP encode 0.70x to 0.72x on Mac and Windows, PNG decode 0.80x on Windows, packed-integer decode 0.82x on Linux). The README says both packages use libjxl 0.12.0 while its capability matrix and install notes say vendored libjxl 0.11.2; on Linux lossy JPEG XL decodes differ by 1 in about a third of values and the lossy encode sizes differ (2,150,106 versus 2,238,951 bytes). The TIFF-versus-tifffile table has no matching harness or result file under bench/ (bench/bench_parallel_tiff.py uses a different in-process method). CPU models not named, so tier stays C. GitHub page shows latest release v0.5.0; 0.6.0 and 0.7.0 are on PyPI.

Python package with 39 compiled codec extensions; most codecs wrap system or vendored C libraries (libjpeg-turbo, libwebp, OpenJPEG, vendored libjxl 0.11.2), so C++ users get the algorithmic parts only through the extension sources. Own kernels for LZW, PackBits, BC1 and BC7 decode. Parallel by default for JPEG 2000 and JPEG XL.

## Maintenance

Very active single-author project (about 470 commits; PyPI 0.3.1 through 0.7.1 between 2026-09-28 and 2026-10-04; last commit 2026-10-04), BSD-3-Clause with an open attribution issue from imagecodecs' author, 3 stars; usable today as a pip-installable Python package, and its LZW C code is small enough to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README tables. The imagecodecs table's harness (bench/bench_vs_imagecodecs.py) and per-run medians (bench/results/vs_imagecodecs/linux.json, mac.json, windows.json) are public and check identical decoded output, but no CPU model is named (only '20-core Apple silicon Mac', '64-core x86-64 Linux workstation', '4-core x86-64 Windows laptop') and the build flags behind the measured wheels are not stated, so not A.
- **Verifier notes:** Numbers in the record match the README. Strongest comparison: own TIFF LZW decode kernel at 2.94x to 3.33x single-threaded on all three hosts with identical output, then PNG encode on libspng+libdeflate (3.45x Mac, 3.68x Linux, 1.12x Windows) against imagecodecs (libpng+zlib); the large threaded rows compare different thread counts. Young single-author repo (3 stars) but very active and on PyPI.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `hardware`, `compiler_and_flags`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** first-party harness; enricher re-run on PyPI wheels
- **Pages the verifier opened:**
  - <https://github.com/kevinjohncutler/opencodecs>
  - <https://github.com/kevinjohncutler/opencodecs/commits/main>
  - <https://raw.githubusercontent.com/kevinjohncutler/opencodecs/HEAD/README.md>
  - <https://raw.githubusercontent.com/kevinjohncutler/opencodecs/HEAD/bench/bench_vs_imagecodecs.py>
  - <https://raw.githubusercontent.com/kevinjohncutler/opencodecs/HEAD/bench/results/vs_imagecodecs/linux.json>
  - <https://raw.githubusercontent.com/kevinjohncutler/opencodecs/HEAD/bench/results/vs_imagecodecs/mac.json>
  - <https://raw.githubusercontent.com/kevinjohncutler/opencodecs/HEAD/bench/results/vs_imagecodecs/windows.json>
  - <https://raw.githubusercontent.com/kevinjohncutler/opencodecs/HEAD/bench/README.md>
  - <https://raw.githubusercontent.com/kevinjohncutler/opencodecs/HEAD/bench/bench_parallel_tiff.py>
  - <https://raw.githubusercontent.com/kevinjohncutler/opencodecs/HEAD/bench/bench_readers.py>
  - <https://raw.githubusercontent.com/kevinjohncutler/opencodecs/HEAD/bench/profile_tifffile.py>
  - <https://raw.githubusercontent.com/kevinjohncutler/opencodecs/HEAD/bench/run_benchmarks.py>
  - <https://raw.githubusercontent.com/kevinjohncutler/opencodecs/HEAD/bench/sweep.py>
  - <https://raw.githubusercontent.com/kevinjohncutler/opencodecs/HEAD/CHANGES.rst>
  - <https://github.com/kevinjohncutler/opencodecs/tree/main/bench>
  - <https://github.com/kevinjohncutler/opencodecs/tree/main/bench/results>
  - <https://github.com/kevinjohncutler/opencodecs/tree/main/bench/results/vs_imagecodecs>
  - <https://github.com/kevinjohncutler/opencodecs/tree/main/bench/results/linux_x86_64>
  - <https://pypi.org/pypi/opencodecs/json>
- **Sources the enricher read:**
  - <https://github.com/kevinjohncutler/opencodecs>
  - <https://github.com/kevinjohncutler/opencodecs/commits/main>
  - <https://github.com/kevinjohncutler/opencodecs/tree/main/src/opencodecs/codecs>
  - <https://github.com/kevinjohncutler/opencodecs/issues?q=is%3Aissue>
  - <https://github.com/kevinjohncutler/opencodecs/issues/1>
  - <https://raw.githubusercontent.com/kevinjohncutler/opencodecs/HEAD/README.md>
  - <https://raw.githubusercontent.com/kevinjohncutler/opencodecs/HEAD/bench/bench_vs_imagecodecs.py>
  - <https://raw.githubusercontent.com/kevinjohncutler/opencodecs/HEAD/bench/results/vs_imagecodecs/linux.json>
  - <https://raw.githubusercontent.com/kevinjohncutler/opencodecs/HEAD/bench/results/vs_imagecodecs/mac.json>
  - <https://raw.githubusercontent.com/kevinjohncutler/opencodecs/HEAD/bench/results/vs_imagecodecs/windows.json>
  - <https://raw.githubusercontent.com/kevinjohncutler/opencodecs/HEAD/bench/README.md>
  - <https://raw.githubusercontent.com/kevinjohncutler/opencodecs/HEAD/CHANGES.rst>
  - <https://raw.githubusercontent.com/kevinjohncutler/opencodecs/HEAD/INSTALL.md>
  - <https://raw.githubusercontent.com/kevinjohncutler/opencodecs/HEAD/THIRD-PARTY.md>
  - <https://raw.githubusercontent.com/kevinjohncutler/opencodecs/HEAD/setup.py>
  - <https://raw.githubusercontent.com/kevinjohncutler/opencodecs/HEAD/pyproject.toml>
  - <https://raw.githubusercontent.com/kevinjohncutler/opencodecs/HEAD/.github/workflows/build_wheels.yml>
  - <https://raw.githubusercontent.com/kevinjohncutler/opencodecs/HEAD/src/opencodecs/codecs/_tiff.pyx>
  - <https://raw.githubusercontent.com/kevinjohncutler/opencodecs/HEAD/src/opencodecs/codecs/_bcdec.pyx>
  - <https://raw.githubusercontent.com/kevinjohncutler/opencodecs/HEAD/src/opencodecs/codecs/_jpeg.pyx>
  - <https://raw.githubusercontent.com/kevinjohncutler/opencodecs/HEAD/src/opencodecs/codecs/_png.pyx>
  - <https://raw.githubusercontent.com/kevinjohncutler/opencodecs/HEAD/src/opencodecs/codecs/_deflate.pyx>
  - <https://raw.githubusercontent.com/kevinjohncutler/opencodecs/HEAD/3rdparty/oc_tifflzw/oc_tifflzw.c>
  - <https://raw.githubusercontent.com/kevinjohncutler/opencodecs/HEAD/3rdparty/oc_tifflzw/oc_tifflzw.h>
  - <https://raw.githubusercontent.com/cgohlke/imagecodecs/HEAD/imagecodecs/_imcd.pyx>
  - <https://raw.githubusercontent.com/cgohlke/imagecodecs/HEAD/imagecodecs/imcd.c>
  - <https://raw.githubusercontent.com/cgohlke/imagecodecs/HEAD/imagecodecs/_shared.pyx>
  - <https://raw.githubusercontent.com/cgohlke/imagecodecs/HEAD/imagecodecs/_deflate.pyx>
  - <https://raw.githubusercontent.com/cgohlke/imagecodecs/HEAD/imagecodecs/_zlib.pyx>
  - <https://raw.githubusercontent.com/cgohlke/imagecodecs/HEAD/imagecodecs/_png.pyx>
  - <https://raw.githubusercontent.com/cgohlke/imagecodecs/HEAD/imagecodecs/_spng.pyx>
  - <https://raw.githubusercontent.com/cgohlke/imagecodecs/HEAD/imagecodecs/_bcn.pyx>
  - <https://raw.githubusercontent.com/cgohlke/imagecodecs/HEAD/imagecodecs/_jpeg8.pyx>
  - <https://raw.githubusercontent.com/pnggroup/libpng/libpng16/pngwutil.c>
  - <https://pypi.org/pypi/opencodecs/json>
  - <https://pypi.org/pypi/imagecodecs/2026.8.16/json>
  - https://pypi.org/project/opencodecs/0.5.0/ (wheel installed into a scratch venv for the rerun)
  - https://pypi.org/project/imagecodecs/2026.8.16/ (wheel installed into a scratch venv for the rerun)
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/kevinjohncutler/opencodecs`) · [data/wave10/enrich/raw/github_com_kevinjohncutler_opencodecs.json](../../../data/wave10/enrich/raw/github_com_kevinjohncutler_opencodecs.json) (enrichment confidence 0.8)

</details>
