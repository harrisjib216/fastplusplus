# libjpeg-turbo

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `BSD-3-Clause AND IJG AND Zlib` · 🟢 active

> SIMD-accelerated, ABI-compatible replacement for IJG libjpeg; the vendor says 2-6x faster JPEG encode and decode.

| | |
|---|---|
| **Beats** | IJG libjpeg (libjpeg 6b reference) |
| **Claimed result** | README: 'generally 2-6x as fast as libjpeg, all else being equal' on systems with SIMD; on other systems it 'can still outperform libjpeg by a significant amount' thanks to optimized Huffman coding. ChangeLog.md (1.5 beta1, AltiVec SIMD): compression about 3-4x and decompression about 2-2.5x faster relative to libjpeg v6b on PowerPC. Search snippet only (libjpeg-turbo.org/About/Performance, blocked): 2.1-6.0x as fast as libjpeg across platforms; versus libjpeg v6b 3.47-6.00x for compression and 2.08-3.43x for decompression on x86-64 Linux, measured with tjbench (Mpixels/sec) using a TurboJPEG wrapper built against libjpeg v6b and v8d. |
| **Workload** | JPEG compression and decompression on systems with common CPU architectures, SIMD-accelerated Huffman and DCT paths. |
| **Metric** | throughput |
| **Adoption** | 4.4k stars |
| **Last commit** | 2026-09-25 |
| **Links** | [repository](https://github.com/libjpeg-turbo/libjpeg-turbo) · [benchmark](https://github.com/libjpeg-turbo/libjpeg-turbo) |

## Verdict

First-party only: the README says 'generally 2-6x as fast as libjpeg, all else being equal' with no machine, compiler or libjpeg version; the per-platform tables (libjpeg v6b and v8d baselines, tjbench Mpixels/s) live on libjpeg-turbo.org, which was not reachable, and tjbench itself times a 1 s warm-up and then at least 5 s of repeated compress/decompress calls and reports Mpixels/s. Third-party runs do not use IJG libjpeg as baseline: jpeg-nitro's README (Intel i9 13th gen) puts libjpeg-turbo 3.1.2 at parity with its own one-thread decoder, and google/decoder-benchmarks-for-rust (2.6 GHz 6-core Core i7, macOS) has turbojpeg at 84.25 ms versus 126.2 ms for the Rust jpeg-decoder crate on a 2000x3000 JPEG.

## Use it when

- Any C or C++ program that links IJG libjpeg (v6b, or v7/v8 through ABI emulation) and wants faster JPEG encode/decode with no code changes.
- Server-side thumbnailing, image proxies and photo pipelines that decode or encode many 8-bit baseline or progressive JPEGs, one image per thread.
- Decoding straight into RGBX/BGRA/XRGB buffers or planar YUV (TurboJPEG tj3DecompressToYUV8), or decoding at 1/2 and 1/4 scale (SIMD-accelerated IDCT scaling) for previews.
- Lossless JPEG transforms (rotate, flip, crop, drop) through jpegtran or tj3Transform without re-encoding.
- Portable deployments across x86-64, Arm64, PowerPC, Loongson and RISC-V, where one codebase gets SIMD on each.

## Skip it when

- Latency of a single large image on an idle many-core machine: libjpeg-turbo decodes one image on one thread; the catalogued jpeg-nitro decodes one baseline JPEG on all cores (about 9x lower wall time on 16 threads in its README).
- Smallest files per quality: it has no trellis quantization (mozjpeg, a libjpeg-turbo fork, adds it) and no adaptive quantization (google/jpegli, also libjpeg62 API/ABI-compatible, advertises it); when bytes matter more than encode speed, evaluate those instead.
- 12-bit lossy or 2-16-bit lossless JPEG and arithmetic-coded JPEG throughput: those paths run in C only (issue #199, 'Performance improvements (SIMD extensions) for 12-bit JPEGs', is open with 'funding needed').
- Code that needs the libjpeg v9 ABI, SmartScale, DCT scaling in the compressor or lossless RGB JPEG from IJG v9: not supported, and cinfo.scale_num/scale_denom and cinfo.block_size are silently ignored.
- Targets that need AVX-512, Arm SVE2 or WebAssembly SIMD paths: all are open 'funding needed' issues (#732, #860, #250), so wasm builds fall back to C.

## How it is fast

Hand-written SIMD modules (NASM for x86 SSE2/AVX2, intrinsics for Arm Neon, PowerPC AltiVec, Loongson MMI and RISC-V Vector) replace the libjpeg C paths for color conversion, chroma down/upsampling (including merged upsampling plus color conversion), integer sample conversion and quantization, accurate-integer forward and inverse DCT, and the baseline and progressive Huffman encoders. A runtime dispatcher picks the best instruction set per instance. Huffman decoding is not SIMD but uses an optimized table-lookup fast path in C, which is where most of the gain on non-SIMD systems comes from. Only 8-bit-per-sample lossy paths are vectorized (simd/README.md).

## Compared with alternatives

Pick libjpeg-turbo when you need the standard C libjpeg/TurboJPEG ABI, the widest set of SIMD architectures and full format coverage (progressive, arithmetic, 12-bit, lossless, transforms); libjpeg-turbo-rs and zenjpeg are Rust re-implementations that report slightly faster decode on their own x86 tests, and jpeg-nitro beats it only on single-image multi-core latency for baseline JPEGs to YCbCr planes.

## Integration

| | |
|---|---|
| **Form** | shared lib or static lib (libjpeg API library libjpeg.so/jpeg-static and TurboJPEG API library libturbojpeg.so/turbojpeg-static); built with CMake |
| **Dependencies** | none at runtime; build needs CMake 3.15+ and NASM 2.13+ or Yasm 1.2.0+ for the x86 SIMD code (libspng and zlib are bundled for cjpeg/djpeg and tj3LoadImage/tj3SaveImage PNG support) |
| **Minimum toolchain** | C compiler: GCC 4.1+ or Clang on Un\*x, Visual C++ 2005+ or MinGW on Windows; Arm builds need GCC 12+ or Clang for full Neon performance since 3.2 (the GAS Neon code was removed) |
| **Platforms** | x86 and x86-64 (SSE2, AVX2), Arm 32/64 (Neon), PowerPC (AltiVec), Loongson MIPS64 (MMI), RISC-V 64 (RVV); any other CPU through the C code |
| **Thread safety** | Per-instance: each jpeg_compress_struct/jpeg_decompress_struct or tjhandle must be used by one thread at a time (not stated as a rule in the files read, follows from the stateful API); since 3.2 the SIMD capability list is per instance, so no thread-local storage is needed, but tj3GetErrorStr(NULL) for global functions is thread-safe only where TLS exists (turbojpeg.h). |
| **Drop-in for the baseline** | yes |

## Gotchas

- Restart markers switch the decoder to the slow Huffman path for the whole image (README: up to 20% slower). Issue #910 showed a 1.08x decode gain on 25 restart-marker camera JPEGs (Ryzen 7 5800X) by limiting the slow path to restart boundaries; it was closed 'won't implement'.
- The fast integer forward DCT at quality 98-100 cannot use the SIMD quantizer and runs up to 40% slower; the ChangeLog (3.0 beta2) also says the fast DCT/IDCT fail the ISO compliance tests and are no faster than the accurate ones on modern x86, so TurboJPEG 3 defaults to the accurate algorithms.
- Valgrind and MemorySanitizer report false uninitialized reads in the SIMD code; set JSIMD_FORCENONE=1 at run time or build with -DZERO_BUFFERS=1 when running memory checkers.
- When decompressing to RGBX/BGRX/XBGR/XRGB the X byte is left undefined for speed; use the RGBA/BGRA/ABGR/ARGB colorspaces if you need 0xFF alpha. Decompressing 4:4:0 and the float IDCT can differ slightly from libjpeg v6b output.

## Known shortcomings

- The category's own incumbent, kept against IJG libjpeg (zlib-ng precedent): the README's '2-6x as fast as libjpeg' and ChangeLog AltiVec notes (3-4x and 2-2.5x vs v6b) are first-party, and the libjpeg-turbo.org performance page (3.47-6.00x compression, 2.08-3.43x decompression vs v6b) is blocked here, so C. Independent confirmation exists in jpeg-nitro's and Google's decoder benchmarks. IJG licence OSI status unchecked.
- The 2-6x claim is first-party and from the libjpeg v6b/v8 era. Restart markers force the slow Huffman decoder for the whole image (the #910 fix, 1.08x, was declined); the fast FDCT is up to 40% slower at quality 98-100; the 12-bit, lossless and arithmetic paths are C only (#199); no AVX-512, SVE2 or WebAssembly SIMD.

## Caveats and trade-offs

First-party claim. The detailed tables (machines, compilers, libjpeg v6b and v8d baselines measured with tjbench through a TurboJPEG wrapper) are on https://libjpeg-turbo.org/About/Performance, which is blocked from this environment, so the per-platform numbers come from a search snippet only and were not checked against the page. libjpeg-turbo is itself one of this category's listed baselines; it is recorded here against the IJG libjpeg incumbent it replaced (zlib-ng precedent). The 2-6x figure dates from the libjpeg v6b/v8 era and says nothing about how it compares with newer decoders. Independent runs that do not use IJG libjpeg as baseline: gereoffy/jpeg-nitro README table (Intel i9 13th gen) has libjpeg-turbo 3.1.2 (AVX2) at 124 ms per image versus stb_image 175 ms and Wuffs 159 ms; google/decoder-benchmarks-for-rust (2.6 GHz 6-core Intel Core i7, macOS) has turbojpeg at 84.25 ms versus the Rust jpeg-decoder crate at 126.2 ms on venice-2000x3000.jpg. LICENSE.md now describes two licenses (IJG for the libjpeg API library, Modified BSD for TurboJPEG) with SIMD code under Zlib and components under libpng-2.0 and BSD-2-Clause; the README still says three.

Drop-in libjpeg API and ABI plus the simpler TurboJPEG API; SIMD per architecture (x86, ARM and others); the README lists performance pitfalls: decompression can drop by as much as 20% (still far above libjpeg) for JPEGs with restart markers, and compression can drop by as much as 40% when the fast integer forward DCT is used at JPEG quality 98 to 100.

## Maintenance

Actively maintained (last commit 2026-09-25, release 3.2.0 on 2026-06-30 with 3.2.1 fixes in the ChangeLog, CVE fixes such as CVE-2026-75466 handled promptly) and permissively licensed (IJG plus Modified BSD, SIMD code under Zlib); it is the ISO/ITU-T JPEG reference implementation and the default system libjpeg on most platforms, so usability is copyable with no caveats beyond the usual BSD/IJG attribution.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The README (Background section) states libjpeg-turbo is 'generally 2-6x as fast as libjpeg, all else being equal' with no machine, compiler or libjpeg version; the measured tables live on libjpeg-turbo.org/About/Performance, which is blocked here and seen only as a search snippet, so the first-party claim stays C. The benchmark tool itself (src/tjbench.c) is public, but the methodology page could not be opened.
- **Verifier notes:** README claim confirmed verbatim; tier C kept because the methodology page (libjpeg-turbo.org) is blocked and no reachable mirror exists in the libjpeg-turbo GitHub organization. License left as recorded; the IJG license is permissive but its OSI status could not be checked (opensource.org blocked). Metadata confirmed: 4.4k stars, last commit 2026-09-25, not archived.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/libjpeg-turbo/libjpeg-turbo>
  - <https://raw.githubusercontent.com/libjpeg-turbo/libjpeg-turbo/HEAD/README.md>
  - <https://raw.githubusercontent.com/libjpeg-turbo/libjpeg-turbo/HEAD/LICENSE.md>
  - <https://raw.githubusercontent.com/libjpeg-turbo/libjpeg-turbo/HEAD/ChangeLog.md>
  - <https://raw.githubusercontent.com/libjpeg-turbo/libjpeg-turbo/HEAD/src/tjbench.c>
  - <https://github.com/libjpeg-turbo/libjpeg-turbo/commits>
  - <https://github.com/libjpeg-turbo>
  - <https://raw.githubusercontent.com/google/decoder-benchmarks-for-rust/HEAD/README.md>
  - <https://raw.githubusercontent.com/gereoffy/jpeg-nitro/HEAD/README.md>
  - <https://raw.githubusercontent.com/czirok/jpeg-nitro/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/libjpeg-turbo/libjpeg-turbo>
  - <https://raw.githubusercontent.com/libjpeg-turbo/libjpeg-turbo/HEAD/README.md>
  - <https://raw.githubusercontent.com/libjpeg-turbo/libjpeg-turbo/HEAD/LICENSE.md>
  - <https://raw.githubusercontent.com/libjpeg-turbo/libjpeg-turbo/HEAD/ChangeLog.md>
  - <https://raw.githubusercontent.com/libjpeg-turbo/libjpeg-turbo/HEAD/BUILDING.md>
  - <https://raw.githubusercontent.com/libjpeg-turbo/libjpeg-turbo/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/libjpeg-turbo/libjpeg-turbo/HEAD/src/tjbench.c>
  - <https://raw.githubusercontent.com/libjpeg-turbo/libjpeg-turbo/HEAD/src/turbojpeg.h>
  - <https://raw.githubusercontent.com/libjpeg-turbo/libjpeg-turbo/HEAD/simd/README.md>
  - <https://github.com/libjpeg-turbo/libjpeg-turbo/tree/main/simd>
  - <https://github.com/libjpeg-turbo/libjpeg-turbo/issues?q=is%3Aissue%20performance>
  - <https://github.com/libjpeg-turbo/libjpeg-turbo/issues?q=is%3Aissue%20state%3Aopen>
  - <https://github.com/libjpeg-turbo/libjpeg-turbo/issues/910>
  - <https://github.com/libjpeg-turbo/libjpeg-turbo/releases>
  - <https://raw.githubusercontent.com/google/decoder-benchmarks-for-rust/HEAD/README.md>
  - <https://github.com/google/jpegli>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/libjpeg-turbo/libjpeg-turbo`) · [data/wave10/enrich/raw/github_com_libjpeg_turbo_libjpeg_turbo.json](../../../data/wave10/enrich/raw/github_com_libjpeg_turbo_libjpeg_turbo.json) (enrichment confidence 0.8)

</details>
