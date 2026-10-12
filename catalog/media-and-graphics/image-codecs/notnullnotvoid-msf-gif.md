# msf_gif

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C (single header, compiles as C99 or C++98)` · `Dual: MIT or Unlicense-style public-domain dedication (text at the bottom of msf_gif.h)` · 🟡 stale

> Single-header C animated-GIF encoder with SSE2 frame quantization; first-party timings 5x to 30x faster than gif.h and jo_gif.

| | |
|---|---|
| **Beats** | gif.h (Charlie Tangora's single-header encoder, named gif_h in the timings file) and jo_gif |
| **Claimed result** | README: 'uses SSE where available to encode at hundreds of megabytes a second, several times faster than comparable gif libraries'. msf_gif-testing timings.txt (nine lines, first-party): jo_gif2 \~1160 s, jo_gif \~425 s, gif_h dithered \~315 s, gif_h dithered 7bpp \~240 s, gif_h \~75 s, msf_gif \~14 s, msf_gif simd \~8 s, msf_gif threaded \~4 s, msf_gif simd threaded \~2 s. Single-threaded scalar msf_gif vs gif_h: 5.4x undithered, 22.5x vs gif_h dithered (msf_gif always dithers, so the dithered line is the closer match); vs jo_gif 30x; single-threaded SSE build vs gif_h 9.4x (all derived from page data). The threaded lines compare multi-threaded msf_gif against single-threaded baselines and do not correspond to the shipped single-threaded library. No numbers against giflib, gifski or ffmpeg were found (gifski comparison is a TODO in notes.txt). |
| **Workload** | Encoding the author's sample animations (in/ directory of msf_gif-testing; test.cpp lists 13 clips such as bouncy 576x360x417 frames and tiles 384x240x625 frames, quality 16, alpha threshold 128). timings.txt itself does not state the input set, so it is not certain that these are the clips behind the totals. |
| **Metric** | throughput |
| **Compiler and flags** | msf_gif-testing build.sh / build.bat: clang -march=native -std=c++17 -Os (MSVC /Ox and /O2 configs commented out); timings.txt does not say which configuration produced it |
| **Adoption** | 239 stars |
| **Last commit** | 2025-09-10 |
| **Links** | [repository](https://github.com/notnullnotvoid/msf_gif) · [benchmark](https://raw.githubusercontent.com/notnullnotvoid/msf_gif-testing/HEAD/timings.txt) |

## Verdict

The comparison rests on first-party, undated timings.txt totals with no CPU, compiler or input set given: scalar msf_gif \~14 s and SSE \~8 s against gif_h \~75 s (undithered) or \~315 s (dithered) and jo_gif \~425 s. The code that timed gif_h and jo_gif is not published, though .gitignore lists gif-h/, gif-h2/, gif-h3/, jo_gif/, jo_gif2/ and alt/ output folders, so such a harness existed. The public test.cpp times only msf_gif (clang -march=native -Os, profiling trace compiled in, 13 clips, quality 16, alpha threshold 128). If the totals cover the 11 clips whose sizes notes.txt logs (about 2.0 GB of RGBA), that works out to roughly 136 MiB/s scalar and 239 MiB/s SSE (derived; the input set behind timings.txt is not stated).

## Use it when

- Recording GIFs inside a game or tool at interactive speed, where encode time matters more than palette quality.
- Flat-shaded or pixel-art content with mostly static backgrounds, where inter-frame delta coding and ordered dither work well (the author's test set includes clips named diwide and flip, matching the README's examples from his games DIWide and Escher).
- Projects that want a vendorable single header with no dependencies, under public domain or MIT, that compiles as C99 or C++98.
- Memory-limited targets: allocation is bounded by a documented formula, malloc/realloc/free can be replaced through macros, and the to-file API keeps memory to about one frame.

## Skip it when

- Photographic or gradient-heavy video where palette quality matters: colorful frames often end up with 128 colors (issue #8) at a coarse 2-3-2 bit split, with a visible dither pattern. An adaptive quantizer such as gifski produces better-looking output.
- When you need the smallest file: every frame is written full-size (no sub-rectangle cropping), and delta coding turns off for any frame with transparent pixels or a palette bit-depth change.
- Non-x86 targets that need SIMD speed: there is only an SSE2 path (NEON is a TODO), and SIMDe ports to ARM fail to compile because _mm_srli_epi32 is called with a runtime shift count (issue #11, open since February 2025).
- Multithreaded encoding of one GIF: the shipped v2.4 is single-threaded; the threaded rows in timings.txt come from a variant that was never released (notes.txt).
- High-entropy frames with many colors: from reading the code (not measured), each time the 4096-code LZW table fills it is reset with a memset of 4096 x palette-size x 2 bytes (up to 2 MB), so noisy content pays that cost often.

## How it is fast

There is no palette search: each frame is quantized to a fixed RGB bit split (up to 5-6-5 bits at quality 16) with a 4x4 ordered (Bayer-style) dither, done four pixels at a time with SSE2 integer intrinsics. If 256 or more colors end up in use, it drops one bit of depth and quantizes the frame again. The LZW coder uses a dense 4096 x palette-size int16 child table indexed directly by (prefix code, color) instead of a hash table. Pixels whose quantized value matches the previous frame are emitted as the transparent index 0, which gives long runs for LZW.

## Compared with alternatives

It is the only GIF encoder in this category. gif_load and giflib-turbo are GIF decoders and pair with it rather than compete, while fpng, fpnge and QOI encode still lossless frames. Pick msf_gif when the output has to be an animated GIF and capture speed matters more than palette quality.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (C standard library; emmintrin.h when SSE2 is available) |
| **Minimum toolchain** | C99 or C++98 (README); MSVC, GCC and clang paths in the source |
| **Platforms** | any; SSE2 fast path on x86/x86-64 (enabled automatically by __SSE2__ or _M_X64, disabled with MSF_GIF_NO_SSE2); scalar code elsewhere |
| **Thread safety** | One MsfGifState per thread is safe (all buffers live in the handle), but msf_gif_alpha_threshold and msf_gif_bgra_flag are process-wide globals read during every frame. |
| **Drop-in for the baseline** | partial: the begin/frame/end shape matches other single-header GIF writers, but the function names, arguments and the in-memory result buffer differ, so call sites must change |

## Gotchas

- Use v2.4 (commit f56d744, May 2025) or later. It fixed a potential heap buffer overflow on small images and added dimension checks (1 to 65535 per side, 1 GB of RGBA at most). The repository history was rewritten in January 2025 ('fresh initial commit'; tag v2.2 deleted, issue #14).
- msf_gif_begin checks only the lzw, frame and header allocations for failure. A failed 64 KB tlb or used allocation is not caught, despite the header's promise that allocation failures come back as return values (found by reading the v2.4 source).
- BGRA input and 1-bit transparency are switched on through the globals msf_gif_bgra_flag and msf_gif_alpha_threshold, not per handle. Set them before msf_gif_frame and do not change them while another thread is encoding.
- The in-memory API holds the whole GIF until msf_gif_end and then copies it into one buffer, so peak memory is about twice the output size. msf_gif_\*_to_file avoids this.

## Known shortcomings

- timings.txt (9 lines): single-thread 14 s vs gif_h 75 s (5.4x) and vs gif_h dithered 315 s (22.5x); threaded rows are not in the shipped single-thread v2.4, the gif_h and jo_gif timing code is not public, and there are no giflib, gifski or ffmpeg numbers nor any size or PSNR comparison. Licence MIT or public domain. The msfgif.handmade.network post (about 500 MB/s, no baseline) is blocked here.
- The baseline harness is unpublished (though .gitignore lists gif-h, gif-h2, gif-h3, jo_gif and jo_gif2 output dirs, so it existed); timings.txt is undated and was carried in a February 2025 history-rewrite commit after the history was wiped in January 2025. If the totals cover the 11 clips in notes.txt (about 2.0 GB RGBA) the throughput is about 136 MiB/s scalar and 239 MiB/s SSE (derived, assumed input). test.cpp calls encode inside assert(), so an NDEBUG build would time nothing (the shipped build.sh is fine). Colourful frames fall to 128 colours (issue #8); _mm_srli_epi32 with a runtime count breaks SIMDe and ARM builds (issue #11 open); msf_gif_begin skips the NULL check on the tlb and used allocations; the LZW reset memsets up to 2 MB; a pre-2.4 heap overflow was fixed in f56d744.

## Caveats and trade-offs

timings.txt is a nine-line first-party note with no hardware, date, compiler or input description, and the gif_h/jo_gif timing code is not in the public msf_gif-testing repo (test.cpp times msf_gif only). The label gif_h is presumably Charlie Tangora's gif.h, but the file does not say. The 'threaded' rows describe a multithreaded variant that the shipped msf_gif.h v2.4 does not contain (notes.txt says multithreading was left out), so only the \~14 s scalar and \~8 s SSE rows describe the library as published. Output size and quality differ between encoders (msf_gif uses a fixed constant-quality palette with ordered dithering and inter-frame delta encoding; the README's smaller-file and quality claims come with no size or PSNR numbers against gif.h or jo_gif). A Handmade Network post (blocked here, search snippet only) cites about 500 MB/s average and 300 MB/s worst case on an unnamed laptop, with no baseline. A gifski comparison is a TODO in notes.txt. The public-domain alternative has no patent grant.

Uses one fixed constant-quality palette-and-dither scheme per frame instead of adaptive quantization; delta encoding between frames for smaller files. SSE on x86 only (NEON listed as a TODO). Public domain, also available under MIT.

## Maintenance

Small and dual MIT / public-domain licensed, so it is easy to vendor. The last commit was 2025-09-10 (a compiler-compatibility PR), issues #8 and #11 are open with no maintainer reply, and the README still says 'actively maintained'; treat it as stable but slow-moving.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** timings.txt in msf_gif-testing lists first-party wall times for msf_gif, gif_h and jo_gif with no CPU model, date or input description; the public harness (test.cpp, built by build.sh with clang -march=native -Os) times only msf_gif, so the baseline side of the comparison has no public benchmark code. First-party, partial methodology: C.
- **Verifier notes:** Numbers match timings.txt, but the record omitted the gif_h dithered (\~315 s) and jo_gif2 (\~1160 s) lines; I added them and separated the single-threaded rows from the threaded ones. Last commit 2025-09-10 (stale), 239 stars, licence dual MIT / public domain, all confirmed.
- **Fields the verifier corrected:** `claimed_speedup`, `license`, `compiler_and_flags`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/notnullnotvoid/msf_gif>
  - <https://github.com/notnullnotvoid/msf_gif/commits/master>
  - <https://raw.githubusercontent.com/notnullnotvoid/msf_gif/HEAD/README.md>
  - <https://raw.githubusercontent.com/notnullnotvoid/msf_gif/HEAD/msf_gif.h>
  - <https://github.com/notnullnotvoid/msf_gif-testing>
  - <https://github.com/notnullnotvoid/msf_gif-testing/commits/master>
  - <https://raw.githubusercontent.com/notnullnotvoid/msf_gif-testing/HEAD/timings.txt>
  - <https://raw.githubusercontent.com/notnullnotvoid/msf_gif-testing/HEAD/README.md>
  - <https://raw.githubusercontent.com/notnullnotvoid/msf_gif-testing/HEAD/test.cpp>
  - <https://raw.githubusercontent.com/notnullnotvoid/msf_gif-testing/HEAD/build.sh>
  - <https://raw.githubusercontent.com/notnullnotvoid/msf_gif-testing/HEAD/build.bat>
  - <https://raw.githubusercontent.com/notnullnotvoid/msf_gif-testing/HEAD/oldbuild.bat>
  - <https://raw.githubusercontent.com/notnullnotvoid/msf_gif-testing/HEAD/notes.txt>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/notnullnotvoid/msf_gif/HEAD/README.md>
  - <https://raw.githubusercontent.com/notnullnotvoid/msf_gif/HEAD/msf_gif.h>
  - <https://github.com/notnullnotvoid/msf_gif/issues?q=is%3Aissue>
  - <https://github.com/notnullnotvoid/msf_gif/pulls?q=is%3Apr>
  - <https://github.com/notnullnotvoid/msf_gif/issues/8>
  - <https://github.com/notnullnotvoid/msf_gif/issues/10>
  - <https://github.com/notnullnotvoid/msf_gif/issues/11>
  - <https://github.com/notnullnotvoid/msf_gif/issues/15>
  - <https://github.com/notnullnotvoid/msf_gif/commits/master>
  - <https://github.com/notnullnotvoid/msf_gif/commit/f56d744e0962fdf66f89a8c2e1188c69579d1845>
  - <https://github.com/notnullnotvoid/msf_gif-testing>
  - <https://github.com/notnullnotvoid/msf_gif-testing/commits/master/timings.txt>
  - <https://raw.githubusercontent.com/notnullnotvoid/msf_gif-testing/HEAD/timings.txt>
  - <https://raw.githubusercontent.com/notnullnotvoid/msf_gif-testing/HEAD/README.md>
  - <https://raw.githubusercontent.com/notnullnotvoid/msf_gif-testing/HEAD/test.cpp>
  - <https://raw.githubusercontent.com/notnullnotvoid/msf_gif-testing/HEAD/build.sh>
  - <https://raw.githubusercontent.com/notnullnotvoid/msf_gif-testing/HEAD/build.bat>
  - <https://raw.githubusercontent.com/notnullnotvoid/msf_gif-testing/HEAD/oldbuild.bat>
  - <https://raw.githubusercontent.com/notnullnotvoid/msf_gif-testing/HEAD/notes.txt>
  - <https://raw.githubusercontent.com/notnullnotvoid/msf_gif-testing/HEAD/msf_gif.cpp>
  - <https://raw.githubusercontent.com/notnullnotvoid/msf_gif-testing/HEAD/msf_gif.c>
  - <https://raw.githubusercontent.com/notnullnotvoid/msf_gif-testing/HEAD/common.hpp>
  - <https://raw.githubusercontent.com/notnullnotvoid/msf_gif-testing/HEAD/.gitignore>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/notnullnotvoid/msf_gif`) · [data/wave10/enrich/raw/github_com_notnullnotvoid_msf_gif.json](../../../data/wave10/enrich/raw/github_com_notnullnotvoid_msf_gif.json) (enrichment confidence 0.8)

</details>
