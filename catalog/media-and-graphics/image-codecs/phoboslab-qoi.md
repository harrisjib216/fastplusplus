# QOI (Quite OK Image format)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `MIT` · 🟢 active

> Reference C header for the QOI lossless RGB/RGBA format: about 27x faster encode and 3.4x faster decode than libpng, with files about 17% larger.

| | |
|---|---|
| **Beats** | libpng |
| **Claimed result** | QOIR benchmark: QOI encode 146.87 MPixels/s vs libpng 5.49 (about 27x, derived from page data) and decode 193.53 vs 56.18 (about 3.4x, derived from page data); CmpRatio 0.2823 vs libpng 0.2423 (about 16% larger files, derived). The QOI README says throughput is a lot higher than libpng and points to qoiformat.org/benchmark (host blocked here, not opened). |
| **Workload** | Lossless RGB/RGBA encode and decode of the QOI benchmark suite, single-threaded, in the QOIR harness (qoi.h reference implementation). |
| **Metric** | throughput |
| **Hardware** | Intel Core i5-10210U @ 1.60GHz (author's desktop machine), single-threaded |
| **Compiler and flags** | gcc (Debian 10.2.1-6) 10.2.1; script/run_full_benchmarks.sh defaults CFLAGS to '-Wall -O3' and compiles adapter/qoi_adapter.c (which builds the vendored third_party/qoi/qoi.h) with -march=native -Wall -O3; libpng and libwebp are Debian Bullseye system packages (their build flags are not stated) |
| **Adoption** | 7.5k stars |
| **Last commit** | 2026-09-27 |
| **Links** | [repository](https://github.com/phoboslab/qoi) · [benchmark](https://raw.githubusercontent.com/nigeltao/qoir/HEAD/doc/full_benchmarks.txt) |

## Verdict

In Nigel Tao's QOIR harness (test/benchmarks.c, gettimeofday around repeated in-memory encode and decode calls with allocation included, single-threaded, gcc 10.2.1 with -O3 -march=native for the QOI adapter, Intel i5-10210U), on the qoiformat.org benchmark image suite, qoi.h encoded at 146.87 MPixels/s and decoded at 193.53 against Debian Bullseye's libpng simplified API at default compression (5.49 and 56.18), about 27x and 3.4x (derived from page data), with CmpRatio 0.2823 vs 0.2423. QOI's decode lead shrinks to about 1.4x against the Wuffs PNG decoder in the same run (140.79). The record's caveat that QOI compresses worse than libpng on every subset needs one correction: on textures_pk QOI is smaller (0.5645 vs 0.5991).

## Use it when

- Writing lossless 8-bit RGB/RGBA frames where encode time dominates and you control the reader: screenshot capture, game or renderer frame dumps, intermediate pipeline images, asset caches. In the QOIR run it encoded 146.87 MPixels/s against libpng's 5.49 on one i5-10210U thread.
- UI screenshots, icons and flat-colour art, where runs and the colour cache work best: screenshot_web 271.61 MPixels/s encode and 358.64 decode at CmpRatio 0.0835 (libpng 0.0757), icon_512 277.20 / 341.29.
- Embedded, bootloader or freestanding code that needs a tiny auditable decoder: under 400 lines of C89-compatible implementation with only malloc/free/memset, endian-neutral byte I/O (the hash uses the r, g, b, a fields, not the packed word), and a frozen format with no version field.
- When a non-PNG format is acceptable but tool support matters: the README lists QOI support in ImageMagick 7.1.0-20+, ffmpeg 5.1+, GIMP 3.0, KDE KImageFormats, Microsoft PowerToys, IrfanView and XnView MP, plus Debian, Ubuntu, Fedora and AUR packages.

## Skip it when

- When the output must be PNG: the catalogued fpnge encodes real PNG at 312.59 MPixels/s with CmpRatio 0.2798 in the same QOIR run, which is both faster than and slightly smaller than QOI overall (146.87, 0.2823), and fpng also decodes its own PNGs at 148.19. On photo subsets, though, fpnge files are larger than QOI's (photo_kodak 0.6218 vs 0.5829).
- Photographs or anything where file size matters: QOI's ratio is about 17% worse than libpng's defaults overall and worse on photos (photo_wikipedia 0.6618 vs 0.5663, photo_tecnick 0.5992 vs 0.5011); Zpng gets 0.5190 on photo_wikipedia at similar speed, and WebP lossless reaches 0.1651 overall if encode time is not a concern.
- Decoding untrusted files without your own limits: the header alone decides the allocation, so a 22-byte file can make qoi_decode allocate 80 MB (issue #340, open since June 2026), and up to 1.6 GB for a 400-megapixel RGBA header. Truncated or chunk-less streams decode 'successfully' instead of returning NULL. Check width\*height against your own cap before calling it.
- Grayscale, palette, 16-bit, HDR/float, premultiplied alpha, animation, ICC/EXIF metadata, or images over 400 million pixels: none of these is supported. The colorspace byte is informative only, and the reference loads the whole file into RAM (the README points to streaming implementations for huge images).
- When you need the fastest QOI codec rather than the reference: the README says this implementation 'is not extensively optimized'. The catalogued qoixx (C++) and qoi-rust (Rust) produce the same format faster, and qoi-asm (x86-64 assembly, listed in the README in September 2026) claims 1.07x to 2.16x over qoi.h.

## How it is fast

QOI has no entropy coder and no match search: each pixel is emitted as one of six byte-aligned chunks chosen by a fixed priority. These are a run of the previous pixel (up to 62), a 6-bit index into a 64-entry cache of recently seen colours hashed as (r\*3 + g\*5 + b\*7 + a\*11) & 63, a 1-byte delta of -2..1 per channel, a 2-byte 'luma' delta (green -32..31, red and blue relative to green -8..7), or a literal RGB or RGBA chunk. Encode and decode are one linear pass with a small branch tree per pixel and a 256-byte state table on the stack. libpng instead tries PNG row filters and then runs zlib deflate (LZ77 match search plus Huffman coding), and the match search is what costs it most of its encode time. The reference code is deliberately plain scalar C (no SIMD, one pixel per loop iteration even inside runs); the README says performance pull requests will probably not be accepted.

## Compared with alternatives

Pick reference QOI when you want the most widely supported fast lossless format with a frozen spec and a vendorable header that reads like documentation. Use qoixx or qoi-rust for faster coding of the same files, fpnge or fpng when the output has to stay PNG, and QOIR or Zpng (custom formats too) when you want smaller files and faster decoding: QOIR_Lossless beat QOI on all three axes in the same run (0.2525, 168.90, 276.45).

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none beyond libc (malloc/free/memset; stdio for qoi_read/qoi_write unless QOI_NO_STDIO is defined). The qoibench tool also needs libpng, stb_image.h and stb_image_write.h, and qoiconv needs the two stb headers. |
| **Minimum toolchain** | C89 (commits 'make qoi.h build using c89 compilers' and 'Remove single line comments to conform to c89 -pedantic', Dec 2021) or any C++ compiler; the Makefile builds qoiconv with -std=c99 -O3 and qoibench with -std=gnu99 -O3 |
| **Platforms** | any; portable scalar C with no SIMD or intrinsics, and byte-wise big-endian header I/O, so endianness does not matter |
| **Thread safety** | Not documented; the functions keep all state (64-entry index, previous pixel) on the stack and have no mutable globals, so separate images can be coded on separate threads (inferred from the source). |
| **Drop-in for the baseline** | no |

## Gotchas

- qoi_encode mallocs a worst-case buffer of width\*height\*(channels+1)+22 bytes and returns it without shrinking (about 10 MB for a 1080p RGBA frame, whatever the output size). There is no way to pass a preallocated buffer (issue #285, open); allocation can only be swapped globally at compile time with QOI_MALLOC/QOI_FREE, and results must be freed with the matching function.
- qoi_decode never checks the 8-byte end marker or whether the chunks covered every pixel: when data runs out it fills the rest of the image with the last decoded colour and returns success (issue #340). Requesting channels=3 from an RGBA file silently drops alpha, and channels=4 from an RGB file yields alpha 255.
- Sizes are int: qoi_decode takes int size and qoi_encode writes int \*out_len, which is why the reference caps images at 400 million pixels (QOI_PIXELS_MAX) to stay under 2 GB.
- Delta computation stores channel differences in signed char, which depends on implementation-defined narrowing (issues #254 and #328, both open). The qoi_rgba_t union is read through its packed .v member, which C allows but ISO C++ does not sanction. Both behave as intended on mainstream two's-complement compilers, but strict-UB checkers will flag them. There are no tags or releases (issue #261 'Tag a release?' open since 2023), so pin a commit hash.

## Known shortcomings

- Tier A on qoir full_benchmarks.txt rows 65 and 68 (146.87 vs 5.49 MB/s encode, 193.53 vs 56.18 decode; gcc 10.2.1, i5-10210U, Debian libpng default level). Compression ratio 0.2823 vs libpng 0.2423 (about 17% larger, derived from page data) and worse than libpng on every subset. No round-trip pixel check in the harness.
- In the QOIR run fpnge is faster and smaller overall (312.59 MP/s, CmpRatio 0.2798) and Wuffs decodes at 140.79 MP/s, cutting QOI's decode lead to about 1.4x; the record's caveat that QOI never compresses better than libpng is wrong for textures_pk (0.5645 versus 0.5991). qoi_decode accepts truncated streams and a 22-byte file allocates 80 MB (#340 open); signed-char narrowing issues (#254, #328); the encoder returns an unshrunk worst-case buffer; no tags; qoi.h unchanged since April 2025.

## Caveats and trade-offs

QOI is a different file format from PNG (readers need QOI support) and trades compression for speed: overall CmpRatio 0.2823 vs libpng 0.2423 (QOI output about 17% larger, derived from page data) and vs WebP lossless 0.1651; QOI compresses worse than libpng on every subset row of doc/full_benchmarks.txt (for example photo_wikipedia 0.6618 vs 0.5663, photo_kodak 0.5829 vs 0.5630). The libpng baseline (PNG/libpng row, 'Debian Bullseye's libpng' per the file's Notes) is the distro package driven through the simplified API: adapter/png_libpng_adapter.c calls png_image_write_to_memory with image.flags = 0, so PNG_IMAGE_FLAG_FAST is not set and libpng runs at its defaults (zlib default compression level, all-filters heuristic), i.e. its default compression level, not a speed-tuned setting. Timing in test/benchmarks.c: 5 repetitions per image with gettimeofday, single-threaded, allocation included; the harness does not compare decoded pixels with the source (no round-trip check). The WebP_Lossless row uses libpng for images with a dimension above 16383 px, and the WebP decode adapter adds a full-image memcpy. The vendored qoi.h differs from current upstream only by the April 2025 modulo-to-mask change (about 1.4% faster encoding) and stricter qoi_read/qoi_write file-I/O error checks, so the numbers still represent current code. The phoboslab/qoi README itself has no numbers: it says compression is 'usually worse than libPNG' while 'throughput is a lot higher' and links qoiformat.org/benchmark (egress-blocked, not opened); its first-party qoibench.c benchmarks stbi, libpng and QOI. The fpng README (richgel999/fpng) measured QOI at 83.90 and 138.18 MP/s against stb_image and lodepng, not libpng. WangXuan95/Image-Compression-Benchmark (CLIC2021, i7-12700H, Windows 10, Pillow PNG rather than libpng, times include process startup) lists QOI at 19.061 compress and 18.970 decompress time vs PNG (optimize=False) 334.791 and 33.677 (lower is better, unit not stated).

Single-file C/C++ header library. Format is final and extremely simple but files are larger than libpng's (and much larger than WebP or JPEG XL). Not PNG-compatible. RGB and RGBA 8-bit only. Reference implementation is deliberately not heavily optimised and loads the whole file into RAM; limited to 400 million pixels.

## Maintenance

The format is final and qoi.h code last changed in April 2025 (the modulo-to-mask hash, merged May 2025; before that, stricter qoi_read/qoi_write error checks in June 2023). Commits since then, up to 2026-09-27, only add README links, so it is stable rather than actively developed. It is MIT-licensed, about 650 lines including the spec, and packaged by Debian, Ubuntu and Fedora, but has no tagged releases.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification A, tier now A.
- **Tier reason:** Independent third-party run (nigeltao/qoir, not the QOI author) with public benchmark code (test/benchmarks.c, adapter/qoi_adapter.c, adapter/png_libpng_adapter.c, script/run_full_benchmarks.sh), compiler gcc 10.2.1, flags -Wall -O3 plus -march=native for the adapters, and CPU i5-10210U stated; the QOI row (146.87 / 193.53 MPixels/s) and PNG/libpng row (5.49 / 56.18) of the top-level images/ block match the record.
- **Verifier notes:** Checked rows: images/ block lines 65 (PNG/libpng 0.2423, 5.49, 56.18) and 68 (QOI 0.2823, 146.87, 193.53); baseline is Debian Bullseye's libpng at its default compression settings. Metadata confirmed on github.com: MIT, 7.5k stars, not archived, not a fork, last commit 2026-09-27; the '40+ language ports' figure was not counted.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/doc/full_benchmarks.txt>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/script/run_full_benchmarks.sh>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/test/benchmarks.c>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/adapter/png_libpng_adapter.c>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/adapter/webp_adapter.c>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/README.md>
  - <https://raw.githubusercontent.com/pnggroup/libpng/v1.6.37/pngwrite.c>
  - <https://raw.githubusercontent.com/pnggroup/libpng/v1.6.37/pngwutil.c>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/adapter/qoi_adapter.c>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/third_party/qoi/qoi.h>
  - <https://raw.githubusercontent.com/phoboslab/qoi/HEAD/qoi.h>
  - <https://raw.githubusercontent.com/phoboslab/qoi/HEAD/README.md>
  - <https://raw.githubusercontent.com/phoboslab/qoi/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/phoboslab/qoi/HEAD/qoibench.c>
  - <https://github.com/phoboslab/qoi>
  - <https://github.com/phoboslab/qoi/commits>
  - <https://github.com/phoboslab/qoi/commits/master/qoi.h>
  - <https://raw.githubusercontent.com/richgel999/fpng/HEAD/README.md>
  - <https://raw.githubusercontent.com/WangXuan95/Image-Compression-Benchmark/HEAD/README.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/phoboslab/qoi/HEAD/README.md>
  - <https://raw.githubusercontent.com/phoboslab/qoi/HEAD/qoi.h>
  - <https://raw.githubusercontent.com/phoboslab/qoi/HEAD/qoibench.c>
  - <https://raw.githubusercontent.com/phoboslab/qoi/HEAD/qoiconv.c>
  - <https://raw.githubusercontent.com/phoboslab/qoi/HEAD/qoifuzz.c>
  - <https://raw.githubusercontent.com/phoboslab/qoi/HEAD/Makefile>
  - <https://raw.githubusercontent.com/phoboslab/qoi/HEAD/LICENSE>
  - <https://github.com/phoboslab/qoi/commits/master>
  - <https://github.com/phoboslab/qoi/commits/master/qoi.h>
  - <https://github.com/phoboslab/qoi/tags>
  - <https://github.com/phoboslab/qoi/issues?q=is%3Aissue+is%3Aopen>
  - <https://github.com/phoboslab/qoi/issues?q=is%3Aissue+overflow>
  - <https://github.com/phoboslab/qoi/issues/340>
  - <https://github.com/phoboslab/qoi/issues/328>
  - <https://github.com/phoboslab/qoi/issues/258>
  - <https://github.com/phoboslab/qoi/issues/317>
  - <https://github.com/phoboslab/qoi/issues/4>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/doc/full_benchmarks.txt>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/test/benchmarks.c>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/adapter/qoi_adapter.c>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/adapter/png_libpng_adapter.c>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/script/run_full_benchmarks.sh>
  - <https://github.com/aplghl/qoi-asm>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/phoboslab/qoi`) · [data/wave10/enrich/raw/github_com_phoboslab_qoi.json](../../../data/wave10/enrich/raw/github_com_phoboslab_qoi.json) (enrichment confidence 0.88)

</details>
