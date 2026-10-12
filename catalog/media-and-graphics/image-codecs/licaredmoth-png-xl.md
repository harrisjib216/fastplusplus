# PNG XL (PXL)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `libpng-2.0 AND BSD-3-Clause (files under ffmpeg/ are FFmpeg patch material under LGPL-2.1-or-later)` · 🟢 active

> Lossless PNG-replacement format (.pxl) and C library: PNG row filters plus zstd, decoding about 2x faster than libpng.

| | |
|---|---|
| **Beats** | libpng (decode into raw RGBA pixels) |
| **Claimed result** | Raw-pixel decode of the 24 Kodak photographs (bench/rawdec, median of 15 runs per file, summed, single thread): libpng 333.6 ms vs PXL 143.2 ms, about 2.3x (README). PXL files are 85.5% of the PNG bytes. QOI is faster still at 120.7 ms, but its files are 103.5% of the PNG bytes. An earlier logged run measured libpng 347.5 ms vs PXL 163.7 ms (2.1x). In-process decode to RGBA8888 (bench/formatdec.c, BENCHMARKS.md 2026-09-16 correction): on 24 photographs libpng runs at 98.6 MB/s, against PXL level 1 at 275.8 MB/s (87.8% of PNG size), level 12 at 199.6 MB/s (88.6%) and level 19 at 226.7 MB/s (85.6%), i.e. 2.0x to 2.8x (derived from page data). On 30 synthetic stills libpng runs at 308.7 MB/s, against PXL at 449.8 to 536.7 MB/s (1.5x to 1.7x, derived from page data), while WebP is both faster (570.2 MB/s) and smaller (44.6% vs PXL's best 50.3%). On a real PSP-3008: none and delta beat libpng by 2.8x to 3.5x, and BCIF by 2.94x at 480x272. adaptive ties libpng (1.01x to 1.02x). BCIF loses at 512x512 texture size (0.54x). |
| **Workload** | bench/rawdec.c on the 24 Kodak photographs, single thread, median of 15 runs per file, summed over files. PXL decodes an in-memory .pxl encoded at zstd level 12 (the default level is 1). libpng decodes a PNG that pxl_save_png re-encoded with libpng's default write settings, read back through pxl_load_png. Both produce native 8-bit RGB. bench/formatdec.c decodes in process to RGBA8888 for the size-versus-speed charts (24 Kodak photographs and 30 synthetic stills) against libpng, QOI, WebP, JPEG XL and AVIF, all single-threaded. Separate libpng comparison on a real PSP-3008 with one synthetic pattern at 480x272 and 512x512. |
| **Metric** | throughput |
| **Hardware** | Intel Pentium B960 @ 2.20GHz, 2 cores, 15.2 GiB RAM (docs/BENCHMARKS.md); also a real PSP-3008 at 333 MHz. |
| **Compiler and flags** | gcc 16.1.1 (July 2026 log entries) and gcc 16.2.1 (from the 2026-09-15 README regeneration on). CMake Release with CMAKE_C_FLAGS_RELEASE -O3 (CMakeLists.txt; confirmed in flags.make per BENCHMARKS.md), no -march=native, no LTO. libpng 1.6.x is linked from the system by default, with zlib dynamic. VERSIONS.json pins libpng 1.6.59 and zstd 1.5.7 for the vendored CI build. The exact libpng/zlib build behind the README run is not recorded. |
| **Adoption** | 7 stars; used by the repo's own Qt image plugin, Dolphin thumbnailer and FFmpeg module |
| **Last commit** | 2026-09-29 |
| **Links** | [repository](https://github.com/LicaRedMoth/PNG-XL) · [benchmark](https://raw.githubusercontent.com/LicaRedMoth/PNG-XL/HEAD/README.md) |

## Verdict

bench/rawdec.c over the 24 Kodak photographs (median of 15 runs per file, single thread, Pentium B960, gcc 16.x -O3) times PXL decoding an in-memory level-12 .pxl at 143.2 ms total against 333.6 ms for system libpng 1.6.x decoding a default-settings PNG of the same pixels through pxl_load_png, about 2.3x, with PXL output memcmp-checked every repetition. bench/formatdec.c, with every decoder producing RGBA8888 in process, gives 199.6-275.8 MB/s for PXL levels 12 and 1 against 98.6 MB/s for libpng on photographs (about 2.0-2.8x), 449.8-536.7 against 308.7 MB/s on 30 synthetic stills, and on a real PSP-3008 none/delta are 2.8-3.5x libpng while adaptive ties and BCIF loses (0.54x) at 512x512.

## Use it when

- You control both ends of the pipeline (game assets, texture packs, thumbnail caches) and want lossless images that decode about 2x faster than libpng into RGBA on photographs and about 1.5x on synthetic stills, in files 12-15% smaller than default-settings PNG.
- Single-core or memory-tight targets (the design floor is a 32 MB PSP): the decode-only library is 174 KB of .text including zstd, and with -p the row-window streaming path decodes in about the memory of the output image.
- Progressive or row-at-a-time decode straight into GPU texture formats (RGB565, RGBA5551, RGBA4444, RGBA8888) without a separate conversion pass.
- Lossless photographs where QOI's files (about 103.5% of PNG) are too big but you still want decode speed close to QOI's (QOI is about 16% faster on the Kodak set).

## Skip it when

- You must read or serve existing .png files or deliver to browsers: nothing outside this repo (plus its own Qt/KDE plugins and FFmpeg patch) reads .pxl.
- Smallest files matter: JPEG XL (65.8% of PNG) and WebP (73.6%) beat PXL (85.6-88.6%) on photographs. On synthetic stills WebP is both smaller (44.6% vs 50.3%) and faster (570 vs 485-537 MB/s).
- Grayscale 8-bit content (100.3% of PNG, slightly worse) or texture-sized photographs on PSP-class CPUs: the BCIF filter the encoder picks for photos decoded at 0.54x libpng at 512x512 on a real PSP-3008. Encode with -s there.
- You need a frozen, interoperable format: the ROADMAP says the format is pre-release with no outside users and the spec can still change without a version bump until a freeze decision is made.
- You want encode speed at high levels or decode speed at high levels on photos: level 19 makes zstd decompression about 3x slower than level 1 on a Kodak photograph, and levels 6 and 12 can produce larger BCIF files than level 1.

## How it is fast

Pixels go through one of four exactly reversible filters (none, Zpng's left-delta, Zpng's BCIF colour transform y=b, u=g-b, v=g-r with a planar split, or PNG-style adaptive per-row None/Sub/Up/Average/Paeth), and the result is one Zstandard frame instead of DEFLATE. The encoder keeps whichever filter compresses smallest. zstd decompression is much cheaper than inflate, so for none/delta/BCIF decode time is mostly zstd, and the unfilter adds 2-12% (bench/stages.c measurements). The unfilter loops are specialised per filter type, and Paeth is branchless. LTO was measured to undo that specialisation and is deliberately off.

## Compared with alternatives

Pick PXL over Zpng, which it descends from, when you need a real container with palettes, 1- to 16-bit depths, metadata pass-through, streaming, animation and a written SPEC.md; pick it over QOI or QOIR when you want zstd-level compression (about 85-88% of PNG) at near-QOI decode speed. If you must keep standard .png files, use a faster PNG decoder instead (libspng, image-png, ptpng, or fpng for fpng-written PNGs).

## Integration

| | |
|---|---|
| **Form** | static lib \| shared lib (CMake; libpxlcore is PNG-free and needs only zstd, libpxl adds the libpng front end) |
| **Dependencies** | zstd (core); libpng and zlib for PNG/APNG interop; optional vendored submodules pinning libpng 1.6.59 and zstd 1.5.7 |
| **Minimum toolchain** | C99 compiler, CMake 3.10+; benchmarks used gcc 16.1.1/16.2.1 at -O3 |
| **Platforms** | Linux x86-64 (only platform in CI, ubuntu-latest); decoder also cross-compiled with psp-gcc and run on a real PSP-3008 (MIPS Allegrex); no SIMD required. Windows/macOS not documented as tested. |
| **Thread safety** | not documented; the decode path takes all state as arguments and no mutable globals were seen in the codec sources, but no guarantee is stated |
| **Drop-in for the baseline** | partial — pxl_load_png/pxl_save_png wrap libpng, but the speedup applies only to .pxl files: PNGs must be converted with pxl_encode or pxltool c first, and the API is PXL's own, not libpng's |

## Gotchas

- No integrity check: pxl_encode calls ZSTD_compress with default parameters (no zstd content checksum) and the container has no CRC, whereas libpng verifies chunk CRC-32 and zlib's Adler-32 on every decode. Part of the measured gap is libpng doing integrity work PXL skips, and a corrupted .pxl can decode to wrong pixels without an error.
- BCIF (picked for all 24 Kodak photographs) has no row window: it materialises the whole filtered image, roughly doubles decode memory, cannot stream, and delivers all rows only at pxl_stream_finish. -p excludes it at a 4-6.6% size cost on large images; -s keeps only none/delta.
- tRNS, bKGD, hIST and PLTE are not carried as chunks: transparency is canonicalised to a real alpha channel, so a PNG round-trip is pixel-exact but not always type-identical.
- Hard decode limits: width and height at most 1,000,000 and width x height at most 2^28 pixels. A 2026-09-15 heap overflow in the streaming DELTA path for sub-8-bit indexed images (fixed in cab6ccf) and two 32-bit integer-overflow out-of-bounds reads (fixed after the 2026-09-16 audit) show the decoders are young; CI runs an ASan/UBSan fuzz soak.

## Known shortcomings

- Format-versus-format comparison, not a faster PNG decoder: PXL is its own PXL1 container (delta and BCIF filters ported from Zpng plus zstd), so beating libpng decode is different work. BCIF wins all 24 Kodak files, so the photo path is the Zpng transform plus zstd. The libpng side is timed with the file read from page cache plus a metadata scan (small bias against libpng); the BCIF path loses 0.54x at texture sizes (PSP). Single machine (Pentium B960, gcc 16.x -O3).
- Pre-release format whose spec is not frozen (ROADMAP); no integrity check (ZSTD_compress default with no checksum or CRC) while libpng verifies CRC-32 and Adler-32, so libpng does extra work in the comparison; formatdec.c has no pixel check (rawdec does); the BCIF path needs a full-image buffer and cannot stream; an earlier heap overflow and two out-of-bounds reads were fixed; Linux-only CI.

## Caveats and trade-offs

A distinct codec, not a fork or port of Zpng as a whole: it has its own PXL1 container, palette and 1- to 16-bit support, adaptive PNG row filters, metadata pass-through, streaming and animation. Only the delta and BCIF colour-plane filters are ported from Zpng (catid/Zpng, already catalogued; its BSD-3 notice is retained). On the Kodak photographs BCIF wins all 24 files (BENCHMARKS.md 2026-07-29), so the headline photo decode path is Zpng's transform plus zstd in C. The comparison is format versus format: libpng decodes a PNG while PXL decodes a .pxl re-encoded from it. PXL is therefore not a faster PNG decoder, and existing PNGs must be converted first. In bench/rawdec.c the libpng side is timed through pxl_load_png. That function reads the file from disk (page cache) and scans its chunks for metadata before decoding, while PXL decodes from a memory buffer: a small bias against libpng. The README's raw-decode timings are not logged in BENCHMARKS.md, and the author says timing columns are not comparable across runs. The benchmark machine is a 2-core Pentium B960 that the author reports carries about 35% background load even when idle. QOI is about 16% faster than PXL on 24 of 24 files. Every decoder runs single-threaded, and libjxl and libavif get no worker threads. An earlier chart overstated PXL by 4/3 (3-channel output counted as 4) until all decoders were forced to RGBA8 on 2026-09-16. On synthetic stills WebP is smaller and faster. On the PSP the adaptive filter only ties libpng, and BCIF is 0.54x libpng at texture size (one synthetic pattern measured). 7 stars.

A new lossless format (.pxl, animated .apxl), not a PNG decoder: PNG row filters feeding Zstandard, with libpng used only to read and write real PNG files. Files are 85.5% of PNG on photographs but JPEG XL and WebP compress better; decoder is 174 KB .text versus libpng's 210 KB. Single-threaded decode; PNG files must be converted to PXL first.

## Maintenance

Very active single-author project (81 commits, last 2026-09-29, 7 stars, no open issues) with unusually candid append-only benchmark logs, but the format is pre-release and not yet frozen; libpng-2.0 AND BSD-3-Clause, small enough to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification A, tier now A.
- **Tier reason:** Benchmark code is public (bench/rawdec.c for the raw-decode table, bench/formatdec.c and bench/formats.sh for the charts), CMakeLists.txt sets Release -O3 without -march=native, and docs/BENCHMARKS.md names gcc 16.1.1/16.2.1 and an Intel Pentium B960; rawdec memcmp-checks PXL's output against the source pixels on every repetition and libpng returns the same 8-bit layout. It is a format-versus-format comparison, tiered A like the Zpng entry's qoir comparison.
- **Verifier notes:** Decided not a duplicate of Zpng: it is a new format and library that ports only Zpng's delta and BCIF filters, although on the Kodak photographs the decoded path is Zpng's BCIF in all 24 files. Numbers match the README and BENCHMARKS.md. Two corrections: the record paired the level-19 size (85.6%) with the 200-276 MB/s range across all levels, and its PSP summary left out BCIF's 0.54x loss at texture size.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `license`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/LicaRedMoth/PNG-XL/HEAD/README.md>
  - <https://raw.githubusercontent.com/LicaRedMoth/PNG-XL/HEAD/docs/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/LicaRedMoth/PNG-XL/HEAD/bench/rawdec.c>
  - <https://raw.githubusercontent.com/LicaRedMoth/PNG-XL/HEAD/bench/formatdec.c>
  - <https://raw.githubusercontent.com/LicaRedMoth/PNG-XL/HEAD/bench/formats.sh>
  - <https://raw.githubusercontent.com/LicaRedMoth/PNG-XL/HEAD/bench/bench.sh>
  - <https://raw.githubusercontent.com/LicaRedMoth/PNG-XL/HEAD/bench/README.md>
  - <https://raw.githubusercontent.com/LicaRedMoth/PNG-XL/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/LicaRedMoth/PNG-XL/HEAD/VERSIONS.json>
  - <https://raw.githubusercontent.com/LicaRedMoth/PNG-XL/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/LicaRedMoth/PNG-XL/HEAD/src/pxl_png.c>
  - <https://github.com/LicaRedMoth/PNG-XL>
  - <https://github.com/LicaRedMoth/PNG-XL/commits>
- **Sources the enricher read:**
  - <https://github.com/LicaRedMoth/PNG-XL>
  - <https://github.com/LicaRedMoth/PNG-XL/commits>
  - <https://github.com/LicaRedMoth/PNG-XL/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/LicaRedMoth/PNG-XL/HEAD/README.md>
  - <https://raw.githubusercontent.com/LicaRedMoth/PNG-XL/HEAD/docs/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/LicaRedMoth/PNG-XL/HEAD/docs/ROADMAP.md>
  - <https://raw.githubusercontent.com/LicaRedMoth/PNG-XL/HEAD/docs/RESEARCH.md>
  - <https://raw.githubusercontent.com/LicaRedMoth/PNG-XL/HEAD/SPEC.md>
  - <https://raw.githubusercontent.com/LicaRedMoth/PNG-XL/HEAD/bench/rawdec.c>
  - <https://raw.githubusercontent.com/LicaRedMoth/PNG-XL/HEAD/bench/formatdec.c>
  - <https://raw.githubusercontent.com/LicaRedMoth/PNG-XL/HEAD/bench/formats.sh>
  - <https://raw.githubusercontent.com/LicaRedMoth/PNG-XL/HEAD/bench/README.md>
  - <https://raw.githubusercontent.com/LicaRedMoth/PNG-XL/HEAD/bench/stages.c>
  - <https://raw.githubusercontent.com/LicaRedMoth/PNG-XL/HEAD/bench/mkpsptest.c>
  - <https://raw.githubusercontent.com/LicaRedMoth/PNG-XL/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/LicaRedMoth/PNG-XL/HEAD/VERSIONS.json>
  - <https://raw.githubusercontent.com/LicaRedMoth/PNG-XL/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/LicaRedMoth/PNG-XL/HEAD/src/pxl.h>
  - <https://raw.githubusercontent.com/LicaRedMoth/PNG-XL/HEAD/src/pxl_png.c>
  - <https://raw.githubusercontent.com/LicaRedMoth/PNG-XL/HEAD/src/pxl_codec_decode.c>
  - <https://raw.githubusercontent.com/LicaRedMoth/PNG-XL/HEAD/src/pxl_codec_encode.c>
  - <https://raw.githubusercontent.com/LicaRedMoth/PNG-XL/HEAD/src/pxl_codec_common.c>
  - <https://raw.githubusercontent.com/LicaRedMoth/PNG-XL/HEAD/psp/README.md>
  - <https://raw.githubusercontent.com/LicaRedMoth/PNG-XL/HEAD/psp/main.c>
  - <https://raw.githubusercontent.com/LicaRedMoth/PNG-XL/HEAD/.github/workflows/ci.yml>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/licaredmoth/png-xl`) · [data/wave10/enrich/raw/github_com_licaredmoth_png_xl.json](../../../data/wave10/enrich/raw/github_com_licaredmoth_png_xl.json) (enrichment confidence 0.8)

</details>
