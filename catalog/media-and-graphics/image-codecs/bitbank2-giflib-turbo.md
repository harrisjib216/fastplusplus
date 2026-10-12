# giflib-turbo

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `Apache-2.0` · 🟡 stale

> Single-file C rewrite of giflib's slurp-style API whose LZW decoder uses the output image as its dictionary; speed unmeasured.

| | |
|---|---|
| **Beats** | giflib |
| **Claimed result** | First-party source comment in gif_lib.c (DecodeLZW): 2.5x to 30x faster than giflib, with no harness, machine, test images or giflib version. The author's blocked blog post 'A Big Memory GIF Decoder' (2021-03) is summarised by search snippets as 2x/5x/20x. |
| **Workload** | GIF LZW decoding through the unchanged giflib API; the decoder uses the output image buffer as the LZW dictionary instead of a linked-list string table. |
| **Metric** | throughput |
| **Adoption** | 39 stars; drop-in for giflib, which is packaged in vcpkg and Conan |
| **Last commit** | 2024-03-22 |
| **Links** | [repository](https://github.com/bitbank2/giflib-turbo) · [benchmark](https://github.com/bitbank2/giflib-turbo/blob/master/gif_lib.c) |

## Verdict

Nothing has been measured. The only numbers are first-party prose: the DecodeLZW comment in gif_lib.c claims about 2.5x over giflib on poorly compressed images and up to 30x on well-compressed ones, and a search summary of the blocked 2021 blog post gives 2x/5x/20x. None of them names a CPU, compiler, giflib version or image set. The repo's A/B Makefile (gif_test_old against Homebrew -lgif vs gif_test_new, gcc -O3) builds a test.c that has no timer and only writes a generated wedge image.

## Use it when

- Trusted GIF files on Linux or macOS x86-64/arm64 when the code already uses only DGifOpenFileName/DGifOpenFileHandle + DGifSlurp + DGifCloseFile and you want to try a faster decoder without changing source.
- Batch or offline jobs (thumbnailing your own assets, tests) where you can confirm the output matches giflib's pixel for pixel on your own corpus, and where buffering the whole file plus each frame in memory is acceptable.
- Studying the output-as-dictionary LZW technique; the same author's maintained AnimatedGIF library uses it as its 'Turbo' mode.

## Skip it when

- Any untrusted input (browsers, upload services, chat clients). The decoder does not validate the LZW minimum code size, ignores the compressed-data length, does not bounds-check sub-block parsing, and leaves malloc results unchecked. Valid images can also overflow the heap (see gotchas). The README itself lists security vulnerabilities as an open risk.
- Code that uses DGifOpen with a read callback or in-memory buffer, the DGifGetRecordType/DGifGetImageDesc/DGifGetLine low-level decoder, the GraphicsControlBlock helpers (DGifSavedExtensionToGCB and others) or GifFreeSavedImages. These fail at runtime or at link time.
- Big-endian 64-bit CPUs, or 64-bit CPUs that trap on unaligned access. INTELLONG reads a native-endian uint64_t, and LZWCopyBytes does unaligned 8-byte stores.
- Windows or non-seekable input. The code includes unistd.h and sys/fcntl.h and uses open/read/lseek/close. On a pipe, lseek fails, no file buffer is allocated, and GIFPreprocess then dereferences a NULL file pointer.
- Production use where you need a maintained, measured option. There are 10 commits, the last core change was on 2023-01-16, there are no tests, and there is no benchmark. gif_load is the measured alternative.

## How it is fast

The LZW decoder stores each dictionary entry as an (offset, length) pair pointing into pixels already written to the frame buffer. Emitting a code is then a forward copy, done 8 bytes at a time with unaligned 64-bit loads and stores on 64-bit targets, instead of walking a prefix linked list backwards and reversing the result. The compressed data is first 'de-chunked' in place, with the 255-byte sub-block headers removed, so the inner loop refills a 64-bit bit buffer without checking block boundaries. The file is read with a single read() call, and there are no per-byte input bounds checks in the hot loop (see gotchas).

## Compared with alternatives

Only when you need giflib's exact SavedImage structures from a recompile and the input is trusted. Otherwise use gif_load (C tier, measured 1.28x-1.78x over giflib 5.2.2 in its own README tables, different callback API), or msf_gif if what you need is fast GIF encoding.

## Integration

| | |
|---|---|
| **Form** | source-drop (gif_lib.c + gif_lib.h), or a CMake library installed as 'gif' with giflib.pc and SOVERSION 7 |
| **Dependencies** | none beyond libc and POSIX file I/O |
| **Minimum toolchain** | C99 (Makefile uses -std=c99 -O3); CMake 3.11 for the CMake build |
| **Platforms** | POSIX (Linux, macOS, BSD); the fast path assumes a little-endian 64-bit CPU with cheap unaligned access (x86-64, arm64); 32-bit builds fall back to byte-by-byte copies; no Windows support in the source |
| **Thread safety** | not documented; decoder state (symbol table, file buffer) is allocated per GifFileType in DGifSlurp and no mutable globals are used in the decode path, so separate handles on separate threads look safe from the code |
| **Drop-in for the baseline** | partial: only the DGifOpenFileName/DGifOpenFileHandle + DGifSlurp and EGifSpew paths are implemented. DGifOpen returns NULL, and the DGifGet\* line API is absent. DGifExtensionToGCB, DGifSavedExtensionToGCB, EGifGCBToExtension, EGifGCBToSavedExtension, EGifPutExtension and GifFreeSavedImages are declared but undefined. Installing it as libgif.so.7 in place of giflib 5.2 would break dynamically linked programs that call any of these. |

## Gotchas

- Heap overflow on valid files. Each frame buffer is malloc'd as Width\*Height+8 rounded up to 64 KiB, but DecodeLZW writes the 2^codesize root dictionary bytes just past Width\*Height. With 8-bit LZW codes, any frame where Width\*Height mod 65536 falls in 65281-65528 overruns the buffer; for example, a 300x218 frame writes 120 bytes past it (derived from reading gif_lib.c). Separately, the 8-byte copy overshoot near the end of a frame can overwrite those root bytes before the last few pixels are decoded.
- Out-of-bounds reads on malformed or truncated files. The sub-block de-chunk loop and extension parsing never compare iOff with the file size. DecodeLZW never uses its iLZWSize argument, so a stream with no EOI keeps reading past the file buffer until the frame is full. The LZW code-size byte is never range-checked: a value of 13 or more gives memset a negative length, and 14 or more writes past the 12,288-entry symbol table. The decoder always returns GIF_OK, so pixels a short stream never writes stay as uninitialized heap memory.
- Ownership differs from giflib. Local ColorMap-&gt;Colors and every ExtensionBlock.Bytes point into the slurped file buffer, which DGifCloseFile frees. Copying decoded frames with GifMakeSavedImage and then calling EGifSpew/EGifCloseFile passes those pointers to free() in GifFreeExtensions, which is an invalid free. This is the decode-and-re-encode loop in test.c that is never reached.
- Each handle is closed twice: DGifSlurp and EGifSpew close the file descriptor, then DGifCloseFile and EGifCloseFile close the same number again. In a multithreaded program that fd number may already belong to another file. EGifSpew writes the LZW code-size byte from SColorResolution and dereferences SColorMap without a NULL check.

## Known shortcomings

- No reachable number: the README, repo page and AnimatedGIF wiki carry none; the 5x to 20x versus giflib exists only in search snippets of the author's blocked blogspot post. The Makefile builds old (Homebrew -lgif) and new (gcc -O3) targets, but test.c has no timer and its decode loop never runs (main returns after DoGifWedge), and no machine or test images are stated. Tier D on the keep-and-document rule.
- Security bugs from code reading (not run): the frame buffer is W\*H+8 rounded up to 64 KiB but 256 root-dictionary bytes are written after W\*H, so valid GIFs with W\*H mod 65536 in 65281-65528 (for example 300x218, 120 bytes past) overflow the heap; DecodeLZW ignores iLZWSize and reads past the file buffer; sub-block and extension parsing is unbounded; LZW code size unchecked; a descriptor closed twice; mallocs unchecked. Partial drop-in only: DGifOpen stub returns NULL, DGifGet\* absent, six declared functions undefined (GCB helpers, EGifPutExtension, GifFreeSavedImages). The only number is a 2.5x to 30x comment in gif_lib.c DecodeLZW with no harness or machine (retier-04, D to C).

## Caveats and trade-offs

Snippet only and unverified: the 2x/5x/20x figures come from a WebSearch summary of the blocked blog post 'A Big Memory GIF Decoder' (2021-03); the '2.5x to 30x' figure comes from a deepwiki machine summary (blocked). The README, repo page and the AnimatedGIF wiki (which describes the same Turbo-mode idea) contain no numbers. Repo harness: the Makefile builds gif_test_old (system giflib from /opt/homebrew, -lgif) and gif_test_new (this gif_lib.c), both with gcc -O3, but test.c has no timing code, its 100-iteration DGifSlurp/EGifSpew decode and re-encode loop is unreachable because main() returns right after DoGifWedge(), and the Makefile references gifwedge.c, gifsponge.c and getarg.c that are not in the repo. No CPU, compiler version, giflib version or test images are stated. The README itself names possible security vulnerabilities and CPU incompatibilities as open risks; the decoder parses untrusted GIF input and has only 10 commits (last 2024-03-22). Only decoding speed is claimed. [retier] Number is a source-code comment with no setup. Memory safety from code reading (not run): the frame buffer is W\*H+8 rounded up to 64 KiB but 256 root-dictionary bytes are written after W\*H, so valid GIFs whose W\*H mod 65536 falls in 65281-65528 (for example 300x218) overflow the heap; DecodeLZW ignores iLZWSize and reads past the file buffer; sub-block and extension parsing is unbounded; the LZW code size is unchecked; a file descriptor is closed twice; mallocs are unchecked. Partial drop-in only: DGifOpen is a stub returning NULL, the DGifGet\* functions are absent, and six declared functions (GCB helpers, EGifPutExtension, GifFreeSavedImages) are undefined.

Uses more RAM than giflib (the author's own description: 'It uses more RAM, but you get more speed'); the README lists possible security vulnerabilities and CPU incompatibilities as not yet tested, and says it may take a long time before big projects adopt it.

## Maintenance

Stale (last commit 2024-03-22, a BSD build fix; last code change 2023-01-16; 39 stars, no releases, no tests, no open issues). It is Apache-2.0 and small enough to vendor, but it is not safe for untrusted input without substantial hardening.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification C, tier now C.
- **Tier reason:** No page that could be opened carries a number: the README, repo root and the author's AnimatedGIF wiki only say giflib-turbo is faster, and the 5x/20x figures appear only in a WebSearch summary of the blocked blog post. The repo has an A/B build (Makefile targets gif_test_old against Homebrew -lgif and gif_test_new, gcc -O3) but test.c has no timer and its decode loop is unreachable, and no machine or test images are given.
- **Retiered** D to C: Raised D to C: the enricher found a first-party number in the repository itself, a comment in gif_lib.c DecodeLZW stating the decoder is 2.5x to 30x faster than giflib (opened via raw.githubusercontent.com), so the claim is no longer snippet-only; no harness, machine, images or giflib version accompany it (lodepng-turbo precedent for a source-comment number at C). The enricher's code reading also found memory-safety bugs on valid inputs, recorded as caveats and shortcomings.
- **Verifier notes:** Kept at tier D rather than rejected per the orchestrator's instruction (39 stars, below the notability bar, so a strict reading of the prompt would reject as not-notable-tier-d). If a later environment can open the blogspot post, re-check for a machine and image set and consider C. License Apache-2.0, last commit 2024-03-22 (stale) and 39 stars confirmed on github.com.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`, `benchmark_url`
- **Pages the verifier opened:**
  - <https://github.com/bitbank2/giflib-turbo>
  - <https://github.com/bitbank2/giflib-turbo/commits>
  - <https://raw.githubusercontent.com/bitbank2/giflib-turbo/HEAD/README.md>
  - <https://raw.githubusercontent.com/bitbank2/giflib-turbo/HEAD/test.c>
  - <https://raw.githubusercontent.com/bitbank2/giflib-turbo/HEAD/Makefile>
  - <https://github.com/bitbank2/AnimatedGIF/wiki>
- **Sources the enricher read:**
  - <https://github.com/bitbank2/giflib-turbo>
  - <https://github.com/bitbank2/giflib-turbo/commits>
  - <https://github.com/bitbank2/giflib-turbo/pulls?q=is%3Apr>
  - <https://raw.githubusercontent.com/bitbank2/giflib-turbo/HEAD/README.md>
  - <https://raw.githubusercontent.com/bitbank2/giflib-turbo/HEAD/gif_lib.c>
  - <https://raw.githubusercontent.com/bitbank2/giflib-turbo/HEAD/gif_lib.h>
  - <https://raw.githubusercontent.com/bitbank2/giflib-turbo/HEAD/test.c>
  - <https://raw.githubusercontent.com/bitbank2/giflib-turbo/HEAD/Makefile>
  - <https://raw.githubusercontent.com/bitbank2/giflib-turbo/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/bitbank2/giflib-turbo/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/bitbank2/AnimatedGIF/HEAD/README.md>
  - WebSearch: "Big Memory GIF Decoder" bitbank giflib faster (snippets only; blog post blocked)
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/bitbank2/giflib-turbo`) · [data/wave10/enrich/raw/github_com_bitbank2_giflib_turbo.json](../../../data/wave10/enrich/raw/github_com_bitbank2_giflib_turbo.json) (enrichment confidence 0.75)

</details>
