# lodepng-turbo

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `Zlib` · 🔴 abandoned

> 2019 lodepng hack with libdeflate inflate and SSE2 PNG unfiltering; claims 2x libpng decode, unmeasured, and HEAD has decode bugs.

| | |
|---|---|
| **Beats** | libpng |
| **Claimed result** | README: 'twice as fast as libpng' on x86, x86-64 or ARM; no measurement, harness or baseline build exists in the repository (lodepng_benchmark.cpp never links libpng). |
| **Workload** | PNG decoding only (lodepng decoder with SIMD unfiltering from the simdtests/depng submodule and libdeflate inflate); the README describes no images, sizes or methodology. |
| **Metric** | throughput |
| **Adoption** | 21 stars |
| **Last commit** | 2019-01-22 |
| **Links** | [repository](https://github.com/kanryu/lodepng-turbo) · [benchmark](https://raw.githubusercontent.com/kanryu/lodepng-turbo/HEAD/README.md) |

## Verdict

Nothing was measured. The single README sentence, 'twice as fast as libpng' on x86/x86-64/ARM, has no CPU, compiler, libpng/zlib version, images or harness behind it, and nothing in the repository links libpng. The ARM part of the claim cannot have been measured on this tree, which has no ARM-capable unfilter.

## Use it when

- Only for experiments: a quick check of how much libdeflate plus SIMD unfiltering speeds up a lodepng-based tool on x86-64, with trusted, non-interlaced 8-bit or 16-bit-per-channel PNGs, where you compare the output pixel for pixel against stock lodepng first.
- As reading material on combining libdeflate with Kobalicek's depng SIMD reverse filter. For production, take the idea, not this code.

## Skip it when

- 1-, 2- or 4-bit greyscale or palette PNGs (icons, scans, many small UI assets). The final code commit (61f9f24, 2019-01-22) changed bytewidth to bpp/8, which is 0 for these formats, and depng_filter_sse2 has no case for 0. The rows are never unfiltered: output is all zeros, or still-filtered bytes when the row has padding bits (derived from reading lodepng-turbo.cpp and depng_sse2.cpp; not run).
- Adam7-interlaced PNGs with width or height of 4 pixels or less. These have an empty Adam7 pass, and depng's do { } while (--y != 0) loop called with h = 0 wraps to about 4 billion rows, with heap reads and writes far out of bounds. Original lodepng's for-loop handled h = 0 (derived from code reading).
- Untrusted input. An invalid filter-type byte (&gt;4) is silently ignored instead of returning lodepng's error 36. The row pointer is then not advanced, so later rows are misaligned; if the first row is the bad one, the next 'previous row' pointer lands before the buffer start. Interlaced decoding also memcpys between overlapping regions of the same buffer.
- Encoding. With LODEPNG_TURBO_COMPILE, addChunk_IDAT passes a NULL output buffer to libdeflate_zlib_compress, which writes the zlib header through it. The wrapper also never sets \*outsize and treats the returned byte count as an error enum, so lodepng_encode\* should crash (derived from code reading, including libdeflate cb7ee82's zlib_compress.c).
- ARM, 32-bit x86 without -msse2, or any non-x86 target. depng_sse2.cpp (SSE2 intrinsics via emmintrin.h) is the only unfilter compiled, and it is called unconditionally, so the README's 'ARM' and 'NEON' claims do not hold for this tree.

## How it is fast

Two swaps. IDAT data is inflated by libdeflate_zlib_decompress straight into a buffer sized from the IHDR prediction, replacing lodepng's bit-by-bit inflater. Then depng_filter_sse2 reverses Sub, Up, Avg and Paeth per row in place with 16-byte SSE2 vectors: Sub uses a log-step prefix sum (shift-and-PADDB), Up is a plain vector add, and Paeth is computed branch-free in 16-bit lanes with a divide-by-3 reciprocal trick, specialized by template for 1, 2, 3, 4, 6 and 8 bytes per pixel. Rows are then memcpy'd out of the filtered buffer. There is no MMX, AVX2 or NEON code in the build, despite the README.

## Compared with alternatives

Practically never. libspng (third-party measured 1.02x-1.07x over libpng, maintained, fuzzed) and ptpng (1.80x geometric mean over libpng with zlib-ng on Linux x64, published harness) are faster-than-libpng decoders with evidence. image-png or Wuffs-based decoders cover the safe-decoder case, and fpng only wins on its own files.

## Integration

| | |
|---|---|
| **Form** | static lib (liblodepngturbo.a plus libdeflate's static lib) or shared lib; git submodules libdeflate (cb7ee82) and kanryu/simdtests (1b8e25d) |
| **Dependencies** | libdeflate (2019 snapshot, submodule); kanryu/simdtests depng (public domain, submodule) |
| **Minimum toolchain** | C++11 (-std=c++11), GCC or Clang with GNU make; MSVC only through the vstudio project linking a libdeflate built with MSYS2 g++ |
| **Platforms** | x86-64 in practice (SSE2 intrinsics, no runtime dispatch); no NEON/AVX2/MMX code despite the README |
| **Thread safety** | not documented; each LodePNGState gets its own libdeflate decompressor and compressor, and no shared mutable state was seen in the decode path |
| **Drop-in for the baseline** | no |

## Gotchas

- Every lodepng_state_init (and so every lodepng_decode32/decode_memory call, which makes a temporary state) allocates a libdeflate decompressor and a level-6 libdeflate compressor, even for decode-only use. lodepng_state_cleanup frees neither, so each decode leaks both.
- The LodePNGState layout differs from stock lodepng: it adds an 'inspected' field and libdeflate pointers. After lodepng_inspect, decode skips re-reading the header and trusts the caller's w and h, so reusing a state for another file decodes it with the stale header unless you re-init the state.
- The default 'make' on Linux likely fails at the shared-library step. The Makefile hard-codes ./libdeflate/libdeflatestatic.lib, MinGW's name, while libdeflate's Makefile builds libdeflate.a on Linux. The static library target does not depend on it (derived from both Makefiles; not built).
- No turbo-specific tests exist. lodepng_unittest.cpp and lodepng_benchmark.cpp are upstream's files: the unit test uses the lodepng:: C++ API that the Makefile compiles out, and the benchmark needs SDL, round-trips through the broken encoder, and never links libpng.

## Known shortcomings

- README names libpng and says 'twice as fast' with no data; lodepng_benchmark.cpp is the stock lodepng benchmark and never links libpng. Output-correctness fixes of 2019-01-21/22 may postdate the claim. Fork of lvandeve/lodepng.
- Retiered C to D (retier-15): the only evidence is the README's 'twice as fast as libpng' with no measurement, and HEAD has correctness bugs by code reading: sub-8-bit grey and palette PNGs are never unfiltered after commit 61f9f24 (bytewidth = bpp/8, no case 0 in depng), Adam7 images with a dimension of 4 or less wrap the row loop out of bounds, the encoder passes a NULL output buffer to libdeflate_zlib_compress, two libdeflate objects leak per state, invalid filter bytes are not rejected. README MMX, AVX2, NEON and TurboPNG API claims match nothing in the tree (SSE2 only); the Linux Makefile hard-codes libdeflatestatic.lib.

## Caveats and trade-offs

The libpng baseline is named in the README, but the only evidence is the sentence 'twice as fast as libpng'; the repository's lodepng_benchmark.cpp times lodepng alone and never links libpng, and no CPU, compiler, images or libpng/zlib versions are given. The Makefile builds the library with -O2 -fomit-frame-pointer. Output-correctness fixes landed on 2019-01-21 ('average/paeth of first line') and 2019-01-22 ('If scanline is not a multiple of 4 bytes, the operation was not correct'), at the same time as the README edits, so the speed claim may predate those fixes. The last commit is 2019-01-22, so the comparison predates current libpng (which has its own SIMD filters) and current libdeflate. This is a code derivative of lodepng (its LICENSE carries Lode Vandevenne's copyright) rather than a GitHub fork. The predecessor kanryu/simd_lode_png states a 5x goal with no measurements. [retier] Directional claim only. Correctness bugs at HEAD (code reading, not run): sub-8-bit grey and palette PNGs are never unfiltered after commit 61f9f24 (bytewidth = bpp/8, no case 0 in depng); Adam7 images with a dimension of 4 or less wrap the row loop (out-of-bounds read and write); the encoder passes a NULL output buffer to libdeflate_zlib_compress; two libdeflate objects leak per state; invalid filter bytes are not rejected. README SIMD and API claims match nothing in the tree (SSE2 only); the Linux Makefile hard-codes libdeflatestatic.lib.

Hacked lodepng with libdeflate (git submodule, builds with gcc/clang and GNU make) plus 'depng' prediction routines for unfiltering; accelerates decoding only. Implements both the lodepng API and a TurboPNG API. README itself warns it 'may be slower elsewhere'.

## Maintenance

Abandoned since 2019-01-22 (35 commits over 11 days, 21 stars, 2 forks, no issues or releases). The zlib licence is copyable, but at HEAD sub-byte PNGs decode wrongly and small interlaced PNGs and encoding hit memory errors, so it needs fixes before any use.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now D.
- **Tier reason:** The README names libpng explicitly and states a single first-party ratio ('twice as fast as libpng' on x86/x86-64/ARM) with no data or method. The repository's lodepng_benchmark.cpp is the stock lodepng benchmark: it includes only lodepng.h and times lodepng encode/decode, so nothing in the repo measures libpng. A stated ratio without methodology is tier C.
- **Retiered** C to D: Lowered C to D: the only evidence is the README sentence 'twice as fast as libpng' with no measurement (lodepng_benchmark.cpp times lodepng alone and never links libpng), and the enricher's code reading shows the final commit 61f9f24 broke correctness: bytewidth = bpp/8 means 1-, 2- and 4-bit grey and palette PNGs are never unfiltered (depng has no case 0) and decode to zeros or garbage; an Adam7 image with width or height of 4 or less gives depng h = 0 and the do-while wraps about 4 billion rows (out-of-bounds read and write); the encoder passes a NULL output buffer to libdeflate_zlib_compress; two libdeflate objects leak per state; invalid filter bytes are not rejected. The README's MMX, AVX2, NEON and 'TurboPNG API' claims match nothing in the tree (SSE2 only).
- **Verifier notes:** Baseline libpng is stated, not inferred, but no measurement against it exists anywhere in the repository; the 2x figure is an unsupported README claim, kept at C under the numbers-without-methodology rule (it could equally be read as D). No third-party measurement was found.
- **Fields the verifier corrected:** `is_fork_of`, `workload`, `caveats`, `claimed_speedup`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/kanryu/lodepng-turbo/HEAD/README.md>
  - <https://github.com/kanryu/lodepng-turbo>
  - <https://github.com/kanryu/lodepng-turbo/commits>
  - <https://raw.githubusercontent.com/kanryu/lodepng-turbo/HEAD/lodepng_benchmark.cpp>
  - <https://raw.githubusercontent.com/kanryu/lodepng-turbo/HEAD/Makefile>
  - <https://raw.githubusercontent.com/kanryu/lodepng-turbo/HEAD/LICENSE>
  - <https://github.com/kanryu/lodepng-turbo/tree/master/examples>
- **Sources the enricher read:**
  - <https://github.com/kanryu/lodepng-turbo>
  - <https://github.com/kanryu/lodepng-turbo/commits>
  - <https://github.com/kanryu/lodepng-turbo/commits/master>
  - <https://github.com/kanryu/lodepng-turbo/commit/61f9f24>
  - <https://github.com/kanryu/lodepng-turbo/commit/f4f99a4>
  - <https://github.com/kanryu/lodepng-turbo/commit/ea92a0d>
  - <https://github.com/kanryu/lodepng-turbo/commit/18a0123>
  - <https://github.com/kanryu/lodepng-turbo/tree/master/examples>
  - <https://raw.githubusercontent.com/kanryu/lodepng-turbo/HEAD/README.md>
  - <https://raw.githubusercontent.com/kanryu/lodepng-turbo/HEAD/Makefile>
  - <https://raw.githubusercontent.com/kanryu/lodepng-turbo/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/kanryu/lodepng-turbo/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/kanryu/lodepng-turbo/HEAD/lodepng-turbo.cpp>
  - <https://raw.githubusercontent.com/kanryu/lodepng-turbo/HEAD/lodepng-turbo.h>
  - <https://raw.githubusercontent.com/kanryu/lodepng-turbo/HEAD/lodepng.h>
  - <https://raw.githubusercontent.com/kanryu/lodepng-turbo/HEAD/lodepng.cpp>
  - <https://raw.githubusercontent.com/kanryu/lodepng-turbo/HEAD/parng_emu.h>
  - <https://raw.githubusercontent.com/kanryu/lodepng-turbo/HEAD/lodepng_benchmark.cpp>
  - <https://raw.githubusercontent.com/kanryu/lodepng-turbo/HEAD/lodepng_unittest.cpp>
  - <https://github.com/kanryu/simdtests/tree/1b8e25d/depng>
  - <https://github.com/kanryu/simdtests/commits/master>
  - <https://raw.githubusercontent.com/kanryu/simdtests/1b8e25dce4a858081e4d86c8d0c6916979e9628e/README.md>
  - <https://raw.githubusercontent.com/kanryu/simdtests/1b8e25dce4a858081e4d86c8d0c6916979e9628e/simdglobals.h>
  - <https://raw.githubusercontent.com/kanryu/simdtests/1b8e25dce4a858081e4d86c8d0c6916979e9628e/depng/depng.h>
  - <https://raw.githubusercontent.com/kanryu/simdtests/1b8e25dce4a858081e4d86c8d0c6916979e9628e/depng/depng_ref.cpp>
  - <https://raw.githubusercontent.com/kanryu/simdtests/1b8e25dce4a858081e4d86c8d0c6916979e9628e/depng/depng_sse2.cpp>
  - <https://raw.githubusercontent.com/kanryu/simdtests/1b8e25dce4a858081e4d86c8d0c6916979e9628e/depng/depng_test.cpp>
  - <https://raw.githubusercontent.com/ebiggers/libdeflate/cb7ee82/Makefile>
  - <https://raw.githubusercontent.com/ebiggers/libdeflate/cb7ee82/lib/zlib_compress.c>
  - https://github.com/bojosos/libpng_turbo (redirects to bojosos/ptpng)
  - WebSearch: "lodepng-turbo" libpng benchmark (no third-party measurement found)
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/kanryu/lodepng-turbo`) · [data/wave10/enrich/raw/github_com_kanryu_lodepng_turbo.json](../../../data/wave10/enrich/raw/github_com_kanryu_lodepng_turbo.json) (enrichment confidence 0.8)

</details>
