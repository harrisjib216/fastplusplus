# meshoptimizer (vertex codec used as a lossless float-image compressor)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🟢 active

> Mesh library whose lossless vertex codec, misused on float pixels, beat OpenEXR ZIP: 1.4x encode, 3.1x decode, 7% smaller.

| | |
|---|---|
| **Beats** | OpenEXR 3.4.0 ZIP compression at level 4 (deflate through OpenEXR's bundled libdeflate, OPENEXR_FORCE_INTERNAL_DEFLATE ON); the same harness also runs EXR RLE, PIZ, HTJ2K_32/HTJ2K_256 (OpenJPH inside OpenEXR) and libjxl lossless at efforts 1/3/4/7/8. No standalone zstd, fpzip or zfp baseline in this harness. |
| **Claimed result** | From img/win-ryzen5950x-20250908.html (Ryzen 9 5950X, 16 threads, 10 files 3122.4 MB, best of 3 runs): meshoptimizer vertex codec level 2 (Mop2) ratio 2.011 at 1.600 GB/s compress and 7.861 GB/s decompress versus EXR ZIP level 4 ratio 1.873 at 1.172 GB/s compress and 2.526 GB/s decompress, i.e. about 1.37x compression and 3.1x decompression throughput at a 7% better ratio (derived from page data). Mop1: 2.004 GB/s compress (1.71x, derived) and 8.016 GB/s decompress at ratio 1.966. Mop2 plus zstd level 1: ratio 2.248, 1.533 GB/s compress, 6.739 GB/s decompress. EXR HTJ2K_256: ratio 1.947, 0.709/1.045 GB/s; libjxl effort 7: ratio 2.180, 0.050/0.382 GB/s. On Apple M4 Max (img/mac-m4max-20250908.html): Mop2 3.104 GB/s compress and 14.808 GB/s decompress versus ZIP4 1.723 and 5.993 GB/s (1.80x and 2.47x, derived from page data). README conclusion: mesh optimizer is 'very far ahead of others towards top right of the chart'. |
| **Workload** | Lossless round trip of 10 floating-point EXR images (3122.4 MB raw; RGB/RGBA half and float, multi-layer renders with up to 37 channels, two Poly Haven HDRIs) into and out of an in-memory stream. The meshoptimizer path ('Mop') splits pixels into 16K-pixel chunks, encodes each with meshopt_encodeVertexBufferLevel (vertex codec, levels 0-3, encoding version 1; pixels treated as vertices padded to a multiple of 4 bytes; no meshopt filters), optionally followed by a zstd pass (levels 1/3/10/20), chunks run in parallel on 16 threads; OpenEXR uses setGlobalThreadCount(16). Save and load times include container writing; every codec's output is checked bit-exact with CompareImages; best of 3 runs. |
| **Metric** | throughput |
| **Hardware** | Windows: AMD Ryzen 9 5950X 16-Core Processor, 16 threads; Mac: Apple M4 Max, 16 threads |
| **Compiler and flags** | CMake Release config (CMakePresets.json x64-release, CMAKE_BUILD_TYPE Release; no extra flags in CMakeLists.txt, so CMake's Release defaults apply: /O2 /Ob2 /DNDEBUG for MSVC, -O3 -DNDEBUG for clang), C++17, static libs; Visual Studio 2022 v17.14 on Windows, Xcode clang 16 on Mac; OpenEXR 3.4.0, libjxl main pre-v0.12 (029cec4), meshoptimizer v0.25, zstd 1.5.7, all via FetchContent |
| **Adoption** | 8.5k stars |
| **Last commit** | 2026-09-28 |
| **Links** | [repository](https://github.com/zeux/meshoptimizer) · [benchmark](https://raw.githubusercontent.com/aras-p/test_exr_htj2k_jxl/HEAD/README.md) |

## Verdict

Aras Pranckevicius's public harness (aras-p/test_exr_htj2k_jxl) round-tripped ten float EXR images (3122 MB raw) in memory with a bit-exact check, best of 3 runs, 16 threads on both sides, Release builds with MSVC 2022 17.14 on a Ryzen 9 5950X and Xcode clang 16 on an M4 Max. meshoptimizer v0.25 level 2 reached ratio 2.011 at 1.600 GB/s encode and 7.861 GB/s decode versus OpenEXR 3.4.0 ZIP level 4 at 1.873, 1.172 and 2.526 GB/s on the Ryzen (1.37x and 3.1x, derived), and 3.104/14.808 versus 1.723/5.993 GB/s on the M4 Max (1.80x and 2.47x, derived).

## Use it when

- Internal caches or intermediate files of half/float render buffers, AOVs, lightmaps or simulation fields where you control both writer and reader and do not need interop (the harness author's own recommendation).
- Decode-bound pipelines: the decode stayed at 7.9-8.1 GB/s (Ryzen 9 5950X) and 14.7-14.8 GB/s (M4 Max) across levels 0-3, versus 2.5 and 6.0 GB/s for EXR ZIP level 4.
- Layered images with many interleaved channels (the test set had up to 37 channels per pixel), as long as one pixel fits in 256 bytes.
- When you want a better ratio and can afford a bit more encode time: stacking zstd level 1 on level 2 raised the ratio from 2.011 to 2.248 at 1.53 GB/s encode and 6.7 GB/s decode on the Ryzen.
- Code-size-sensitive builds: the harness measured +26 KB of executable for the codec (+431 KB with zstd) versus +308 KB for EXR HTJ2K and +6017 KB for libjxl.

## Skip it when

- Files other tools must read: there is no image format, and the 'MOP' container exists only in the benchmark repository. Use OpenEXR (ZIP, or HTJ2K via OpenJPH) for interchange.
- Maximum lossless ratio: libjxl effort 7 reached 2.180 and effort 8 2.434 on the same files (at 0.05 and 0.007 GB/s encode), and plain Mop2 stops at 2.011.
- Data without left-to-right correlation: the only predictor is the previous record in memory order (no vertical or 2D prediction), and the README warns that unordered input compresses poorly.
- Records over 256 bytes or not a multiple of 4: the API asserts on both, so callers must pad (the harness zero-pads, which costs a copy per chunk) or split wide pixels into several streams.
- Data that must stay readable by glTF EXT_meshopt_compression decoders or meshoptimizer older than v0.23: the benchmark used vertex format version 1, which those cannot decode; pin version 0 if needed (levels then have no effect).

## How it is fast

Records are processed in blocks of up to 256 (8 KB / record size). Each block is transposed into one byte stream per byte position and delta-coded against the previous record (byte delta, 16-bit delta or, at level 3, 32-bit XOR with a rotation, chosen once per 4-byte lane at levels 2-3) with zigzag mapping. Each 16-byte group of deltas is then bit-packed at 0, 1, 2, 4 or 8 bits with a sentinel-plus-literal escape for outliers, chosen per group with 2-bit headers. There is no entropy coder or match search, so decoding is table-driven shuffles: SSSE3 (picked by cpuid on MSVC x64), NEON on arm64, Wasm SIMD and an opt-in AVX-512 path, about 8 GB/s on a 16-thread Ryzen 9 5950X and 14.8 GB/s on an M4 Max in the measured run. Encoding is scalar C++.

## Compared with alternatives

Among the catalogued image codecs only OpenJPH (as OpenEXR HTJ2K) and LERC target float or raster data; pick meshoptimizer over HTJ2K when you do not need a standard file and want speed (HTJ2K_256 in the same run: ratio 1.947 at 0.709/1.045 GB/s on the Ryzen versus Mop2 2.011 at 1.600/7.861 GB/s). The 8-bit lossless codecs (QOI, fpng, fpnge, QOIR) do not handle half/float pixels at all.

## Integration

| | |
|---|---|
| **Form** | static lib by default (CMake, MESHOPT_BUILD_SHARED_LIBS option) or source-drop: the codec is src/vertexcodec.cpp plus the C-compatible header src/meshoptimizer.h |
| **Dependencies** | none (zstd only if you add the optional second pass yourself) |
| **Minimum toolchain** | any mainstream C++ compiler; CMake 3.5+ if using CMake; the README says the sources build without special options or warnings; the benchmark used MSVC 2022 17.14 and Xcode clang 16 |
| **Platforms** | any; SIMD decode on x86/x64 (SSSE3+POPCNT, runtime cpuid fallback on MSVC and GCC/clang), AVX-512 VBMI2 only when compiled in, NEON on ARM/AArch64, Wasm SIMD; scalar fallback elsewhere |
| **Thread safety** | Encode and decode use only stack buffers and can run concurrently on separate buffers (the harness runs 16 chunks at once); meshopt_encodeVertexVersion sets a global and must not race with encoders, so pass the version argument explicitly as the harness does. |
| **Drop-in for the baseline** | no |

## Gotchas

- Channel modes are chosen per 4-byte lane of the record, so a float channel straddling a 4-byte boundary (possible in mixed half/float layouts) or an odd count of half channels gets a worse delta mode; reorder channels so each 4-byte lane holds one float or two halves.
- The decoder does not store the record count or size: the caller must keep vertex_count and vertex_size next to the payload (the harness keeps them in its own header).
- The decoder is safe on untrusted input but 'may produce garbage data' on malformed streams; check the return code and add your own checksum if integrity matters.
- The measured build was v0.25. The v1.2 release notes say a new mostly branchless SSSE3 decoder is about 20-45% faster on Intel/AMD and AVX-512 adds about 10%, so the current v1.3 should decode faster on x86 than measured; this has not been re-benchmarked in the harness.

## Known shortcomings

- Off-label use: meshoptimizer's vertex codec (meshopt_encodeVertexBufferLevel levels 0-3, version 1, no filters, optional zstd stage) in a custom container as a lossless float-image compressor. Tier A on checked-in result files (img/win-ryzen5950x-20250908.html, img/mac-m4max-20250908.html; Ryzen 9 5950X, 16 threads, VS 2022 v17.14, CMake Release): ratio 2.011 at 1.600/7.861 GB/s vs OpenEXR ZIP4 1.873 at 1.172/2.526 GB/s (1.37x compress, 3.1x decompress, derived); baselines OpenEXR RLE/PIZ/ZIP/HTJ2K and libjxl. The fpzip, zfp and zstd comparisons live in aras-p/float_compr_tester with numbers only in the blocked blog.
- The vertex codec's only predictor is the previous pixel (left neighbour); records are at most 256 bytes and must be a multiple of 4, and the channel mode is chosen per 4-byte lane so misaligned half or float layouts compress worse; format v1 is not readable by EXT_meshopt_compression decoders. fp32 round-trip is compared by value, not bits; the encoder is scalar and the decoder SIMD; the numbers are from v0.25 and the v1.2 notes claim an SSSE3 decode 20-45% faster. The harness is not fully independent of the author: zeux sent harness PR #3 (per-thread padding buffers, about doubling decode performance on Windows) and the owner rewrote the same fix.

## Caveats and trade-offs

Off-label use: 'MOP' is not an image format but meshoptimizer's mesh vertex-buffer codec repurposed by the benchmark author to pack pixel chunks into a custom container with no interop, while the EXR baselines write standard OpenEXR files; both sides are lossless and both are multithreaded, but meshoptimizer offers no image API, so this is the vertex codec's general byte-delta/bit-packing scheme, not a supported image feature. The README's embedded charts are the 2025-06-30 PNGs; the exact numbers above come from the 2025-09-08 HTML result files, which match the library versions the README lists. fp16 subnormals are flushed to zero in the input before all codecs (for libjxl's sake), so 'lossless' applies to the sanitized data. Test images are mostly path-traced renders with noise; the author notes natural images may behave differently. The float-compression series in aras-p/float_compr_tester (meshoptimizer v0.18 versus zstd, lz4, fpzip, zfp and others) is a different harness whose results are only in blocked blog posts. meshoptimizer's own purpose is mesh optimization; it may belong in another category.

Not an image format: the benchmark wraps meshoptimizer's vertex-data compression (vertex size set to the pixel size, padded to a multiple of four) in a custom chunked container written by the benchmark author, so there is no interoperability. Code size +26 KB (+431 KB with zstd) versus +308 KB for EXR HTJ2K and +6017 KB for JPEG-XL.

## Maintenance

Very actively maintained (v1.3 released September 2026, last commit 2026-09-28, about 8.5k stars, 4 open issues), MIT-licensed and packaged by Debian, Ubuntu, Arch, FreeBSD, Nix, vcpkg and Conan; copyable, but the image use is off-label and the container format is yours to write.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now A.
- **Tier reason:** Upgraded B to A: Aras Pranckevicius's public harness (aras-p/test_exr_htj2k_jxl src/main.cpp, src/image_mop.cpp, src/image_exr.cpp) writes exact per-codec ratio and GB/s numbers to checked-in result files (img/win-ryzen5950x-20250908.html, img/mac-m4max-20250908.html) that print the CPU model and thread count; the README names the compilers (Visual Studio 2022 v17.14, Xcode clang 16) and the CMake Release config from CMakePresets.json/CMakeLists.txt fixes the flags, and the 10 test files are publicly downloadable. The run is independent of the meshoptimizer author.
- **Verifier notes:** Exact numbers found in checked-in HTML result files, so chart reading is no longer needed; upgraded to A. Codec is the vertex codec only (no filters), optionally stacked with zstd; baselines are OpenEXR ZIP/PIZ/RLE/HTJ2K and libjxl, not fpzip/zfp/zstd. zeux/meshoptimizer appears nowhere else in data/, so not a duplicate.
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/aras-p/test_exr_htj2k_jxl/HEAD/README.md>
  - <https://github.com/aras-p/test_exr_htj2k_jxl>
  - <https://github.com/aras-p/test_exr_htj2k_jxl/tree/main/src>
  - <https://github.com/aras-p/test_exr_htj2k_jxl/tree/main/img>
  - <https://raw.githubusercontent.com/aras-p/test_exr_htj2k_jxl/HEAD/src/image_mop.cpp>
  - <https://raw.githubusercontent.com/aras-p/test_exr_htj2k_jxl/HEAD/src/main.cpp>
  - <https://raw.githubusercontent.com/aras-p/test_exr_htj2k_jxl/HEAD/src/image_exr.cpp>
  - <https://raw.githubusercontent.com/aras-p/test_exr_htj2k_jxl/HEAD/src/image.cpp>
  - <https://raw.githubusercontent.com/aras-p/test_exr_htj2k_jxl/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/aras-p/test_exr_htj2k_jxl/HEAD/CMakePresets.json>
  - <https://raw.githubusercontent.com/aras-p/test_exr_htj2k_jxl/HEAD/run_mac.sh>
  - <https://raw.githubusercontent.com/aras-p/test_exr_htj2k_jxl/HEAD/img/win-ryzen5950x-20250908.html>
  - <https://raw.githubusercontent.com/aras-p/test_exr_htj2k_jxl/HEAD/img/win-ryzen5950x-20250708.html>
  - <https://raw.githubusercontent.com/aras-p/test_exr_htj2k_jxl/HEAD/img/win-ryzen5950x-20250630.html>
  - <https://raw.githubusercontent.com/aras-p/test_exr_htj2k_jxl/HEAD/img/mac-m4max-20250908.html>
  - <https://github.com/aras-p/float_compr_tester>
  - <https://raw.githubusercontent.com/aras-p/float_compr_tester/HEAD/readme.md>
  - <https://github.com/zeux/meshoptimizer>
  - <https://github.com/zeux/meshoptimizer/commits/master>
- **Sources the enricher read:**
  - <https://github.com/zeux/meshoptimizer>
  - <https://github.com/zeux/meshoptimizer/commits/master>
  - <https://github.com/zeux/meshoptimizer/releases>
  - <https://github.com/zeux/meshoptimizer/releases/tag/v1.0>
  - <https://github.com/zeux/meshoptimizer/releases/tag/v1.1>
  - <https://github.com/zeux/meshoptimizer/releases/tag/v1.2>
  - <https://github.com/zeux/meshoptimizer/issues?q=is%3Aissue+vertex+codec>
  - <https://raw.githubusercontent.com/zeux/meshoptimizer/HEAD/README.md>
  - <https://raw.githubusercontent.com/zeux/meshoptimizer/HEAD/src/meshoptimizer.h>
  - <https://raw.githubusercontent.com/zeux/meshoptimizer/HEAD/src/vertexcodec.cpp>
  - <https://raw.githubusercontent.com/zeux/meshoptimizer/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/aras-p/test_exr_htj2k_jxl/HEAD/README.md>
  - <https://raw.githubusercontent.com/aras-p/test_exr_htj2k_jxl/HEAD/src/main.cpp>
  - <https://raw.githubusercontent.com/aras-p/test_exr_htj2k_jxl/HEAD/src/image_mop.cpp>
  - <https://raw.githubusercontent.com/aras-p/test_exr_htj2k_jxl/HEAD/src/image_mop.h>
  - <https://raw.githubusercontent.com/aras-p/test_exr_htj2k_jxl/HEAD/src/image_exr.cpp>
  - <https://raw.githubusercontent.com/aras-p/test_exr_htj2k_jxl/HEAD/src/image.cpp>
  - <https://raw.githubusercontent.com/aras-p/test_exr_htj2k_jxl/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/aras-p/test_exr_htj2k_jxl/HEAD/CMakePresets.json>
  - <https://raw.githubusercontent.com/aras-p/test_exr_htj2k_jxl/HEAD/run_mac.sh>
  - <https://raw.githubusercontent.com/aras-p/test_exr_htj2k_jxl/HEAD/img/win-ryzen5950x-20250908.html>
  - <https://raw.githubusercontent.com/aras-p/test_exr_htj2k_jxl/HEAD/img/mac-m4max-20250908.html>
  - <https://github.com/aras-p/test_exr_htj2k_jxl/issues?q=is%3Aissue>
  - <https://github.com/aras-p/test_exr_htj2k_jxl/pulls?q=is%3Apr>
  - <https://github.com/aras-p/test_exr_htj2k_jxl/pull/3>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/zeux/meshoptimizer`) · [data/wave10/enrich/raw/github_com_zeux_meshoptimizer.json](../../../data/wave10/enrich/raw/github_com_zeux_meshoptimizer.json) (enrichment confidence 0.85)

</details>
