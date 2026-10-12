# tir (tiny image resize, in tinyexr)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Color conversion and resampling](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `BSD-3-Clause` · 🟢 active

> Pure-C11 separable float resizer in tinyexr's tools/resize; 2.2-3.6x tinyexr's own resizer, roughly level with SSE2-built stb_image_resize2.

| | |
|---|---|
| **Beats** | stb_image_resize2 (successor of stb_image_resize, matched filter, float32 path); also tinyexr's own exr_resize_float |
| **Claimed result** | README Performance tables (output MP/s of f32 pixels, one AVX2 core, Ryzen 9 3950X, Mitchell 4-tap), tir AVX2 / exr_v3 / stb2. 4-channel: 2x up 295 / 135 / 266; 2x down 78 / 30 / 73; 7.3x down 7.6 / 2.2 / 6.4. 1-channel: 2x up 1218 / 443 / 1279; 2x down 334 / 92 / 365; 7.3x down 27.3 / 8.2 / 25.4. Ratios vs stb2 (derived from page data): 4-channel 1.11x, 1.07x, 1.19x; 1-channel 0.95x (2x up), 0.92x (2x down, stb2 about 9% faster, more than the README's 'within \~5%'), 1.07x (7.3x down). Ratios vs tinyexr's own exr_resize_float (derived from page data): 2.2x to 3.6x. Author text: 'tir beats exr_resize_float 2-5x everywhere' and 'Against stb2 (matched filters) tir wins on every 4-channel case'; the triangle-filter rows the author also cites are not in the README table. |
| **Workload** | Separable float32 resampling with a Mitchell (4-tap) filter on random data, 1-channel and 4-channel, shapes 960x640 to 1920x1280 (2x up), 1920x1280 to 960x640 (2x down) and 4096x2560 to 561x350 (7.3x down); output megapixels per second on one thread, about 0.3 s per measurement (tools/resize/tests/tir_bench.c). |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 3950X (Zen 2), one AVX2 core |
| **Compiler and flags** | Makefile target resize-bench: \$(CC) -std=c11 -Wall -Wextra -O2 -g (CFLAGS is not used by this recipe), no -march/-mavx/-mavx2/-mfma; the Makefile line 'CC ?= gcc' does not override GNU make's built-in default CC=cc, so the compiler is the system cc, name and version not stated in the README. tir's AVX2/FMA kernels are compiled with __attribute__((target(...))) in tools/resize/src/tir_kernels_x86.c and selected at runtime by CPUID (tir_cpu.c); stb_image_resize2.h picks SIMD at compile time (AVX/AVX2 only when __AVX__/__AVX2__ or STBIR_AVX/STBIR_AVX2 are defined), so under this recipe stb2 runs its SSE2 path. stb2 is enabled with make resize-bench STB=1 (-DTIR_BENCH_STB) after dropping the header into tools/resize/tests/. |
| **Adoption** | 836 stars (tinyexr repository; tir lives in tools/resize) |
| **Last commit** | 2026-09-07 |
| **Links** | [repository](https://github.com/syoyo/tinyexr) · [benchmark](https://github.com/syoyo/tinyexr/blob/release/tools/resize/README.md) |

## Verdict

Author-run make resize-bench on one Zen 2 core (Ryzen 9 3950X), compiler unnamed (system cc, -O2 -g), Mitchell 4-tap, f32 random data, clamp edges, straight alpha: tir AVX2 reached 295/78/7.6 MP/s on 4-channel 2x up/2x down/7.3x down versus 266/73/6.4 for stb_image_resize2 built at SSE2 and 135/30/2.2 for tinyexr's exr_resize_float; on 1-channel stb2 led the two 2x cases (1279 vs 1218, 365 vs 334) and tir led 7.3x down (27.3 vs 25.4). The stb2 comparison is ISA-mismatched, so the solid result is the 2.2-3.6x gain over exr_resize_float; the win over stb2 is unproven against an AVX2 build of stb2.

## Use it when

- HDR / float32 or half-float texture pipelines in C or C++ that need resampling without clamping, with optional anti-ringing plus clamp_min = 0 for a hard no-negative-pixel guarantee
- Normal-map or height-map mip and LOD generation, where renormalization after filtering and endpoint-exact grid-vertex registration matter
- Distributing one portable x86-64 binary: tir dispatches AVX2+FMA at run time, while stb_image_resize2 only uses AVX/AVX2 when the including TU is compiled with -mavx2 (or STBIR_AVX2), so in a default -O2 build tir is 1.07-1.19x faster on 4-channel Mitchell (Ryzen 9 3950X, page data)
- Streaming or memory-bounded resizing (tiles, scanline EXR decode) through push_row/pull_row with a single arena allocation
- Replacing tinyexr's own exr_resize_float, which tir beats 2.2-3.6x on every measured Mitchell shape

## Skip it when

- If you can build stb_image_resize2 with -mavx2 -mfma: no published run compares against an AVX2 build of stb2, and stb2's header says AVX is 10-40% faster than SSE2 plus about 12% more for AVX2, which exceeds tir's 7-19% 4-channel lead
- 1-channel 2x Mitchell resizes, where the SSE2 stb2 build is already faster in the README table (0.95x up, 0.92x down)
- 8-bit sRGB photo thumbnailing at scale: tir always filters in f32, has no gamma-aware/linear-light conversion option in the header, and was only benchmarked on f32 random data; libvips, Pillow-SIMD or fast_image_resize target that workload
- Projects that need a stable, separately versioned dependency: tir is version 0.1.0, about three months old, lives inside the tinyexr tree rather than its own repository, and its tools/resize code last changed 2026-07-05
- MSVC-only or non-x86/non-ARM targets that want SIMD: x86 kernels rely on GCC/Clang target attributes (MSVC compiles intrinsics without them), NEON is compile-time on AArch64, and other ISAs get the scalar path

## How it is fast

Two-pass separable convolution over precomputed, edge-folded, zero-padded coefficient tables, so inner loops have no edge branches; pass order (horizontal-first or vertical-first) is chosen by a multiply-count cost model. The AVX2+FMA kernels use independent accumulator chains: the 1-channel horizontal pass computes 4 outputs at once and reduces them with one 4x4 transpose, and the 4-channel pass packs two RGBA output pixels per 256-bit register for narrow windows (commit fdf7b0d took 4-channel 2x up from 275 to 295 MP/s). Kernels are compiled with __attribute__((target)) and selected by CPUID at run time, so a baseline-ISA build still runs AVX2 on capable CPUs.

## Compared with alternatives

Pick tir over stb_image_resize2 (and the stb-image-resize-opt fork) when you need HDR, normal-map or height-map aware float resizing, streaming rows, or runtime AVX2 dispatch in a portable binary; pick zimg for C++ float resizing with colorspace conversion, and fast_image_resize or libvips for 8-bit photo resizing, where tir has no published numbers.

## Integration

| | |
|---|---|
| **Form** | source-drop (tools/resize/src: about 12 .c files plus include/tir.h; make resize-lib builds build/libtir.a) |
| **Dependencies** | none for the library (libm); the CLI and benchmark link libtinyexr3.a for EXR I/O; optional C11 &lt;threads.h&gt; or pthreads for -DTIR_ENABLE_THREADS |
| **Minimum toolchain** | C11 compiler (tested gcc/clang; header is C++-safe via extern "C"); AVX2 kernels need GCC/Clang target attributes for runtime dispatch |
| **Platforms** | x86-64 (SSE2/SSE4.1/AVX2+FMA+F16C runtime dispatch), AArch64 NEON, SVE behind an HWCAP gate on Linux, scalar fallback elsewhere |
| **Thread safety** | Separate samplers can run on separate threads; optional band parallelism (num_threads, built with -DTIR_ENABLE_THREADS) gives output byte-identical to serial. tir_simd_force is documented as not thread-safe; the global kernel table is also built lazily on first use without atomics (tir_cpu.c), so make one call before spawning threads (inferred from source, not documented). |
| **Drop-in for the baseline** | partial — same job and comparable filters (Mitchell, Catmull-Rom, box, triangle, B-spline), but a different API, options struct and enum set; default alpha mode is premultiply and default filter is Mitchell, so set alpha = TIR_ALPHA_STRAIGHT to match stb's STBIR_4CHANNEL |

## Gotchas

- The README's stb2 column comes from make resize-bench STB=1, which compiles stb_image_resize2.h at -O2 -g with no -m flags (the recipe ignores CFLAGS), so stb2 ran its SSE2 kernels while tir ran AVX2+FMA; the stb header is not vendored or version-pinned.
- SIMD kernels reassociate sums (multiple accumulators, FMA), so output differs from the scalar path by a few ULP; set deterministic = 1 for bit-identical output across ISAs and thread counts, at scalar speed.
- Defaults differ from stb2: premultiplied-alpha filtering for 4 channels and no clamping (Mitchell can undershoot below 0 on HDR edges unless antiring/clamp_min are set).
- EDGE_WRAP on the y axis buffers the whole image; a heap overflow on WRAP/REFLECT axes with trimmed windows (found by fuzzing, repro 28x10 to 26x2 heightmap) was fixed in 94405e1 on 2026-07-02, along with a threaded-band deadlock (8c631a7).

## Known shortcomings

- tir (tiny image resize inside tinyexr) downgraded A to C: the resize-bench recipe builds stb_image_resize2 at SSE2 (-O2 -g, no -mavx2/-mfma) while tir dispatches AVX2+FMA at runtime, so the 7-19% lead is smaller than the 10-40% plus about 12% that stb2's own docs attribute to AVX2; compiler unstated (\$(CC)) and the stb2 header version unpinned. Work matches (Mitchell B=C=1/3, clamped edges, straight alpha, f32); the 1-channel 2x downscale is 0.92x, not within 5%.
- The lead over stb_image_resize2 is unproven: resize-bench builds stb2 at -O2 -g with SSE2 only (CFLAGS ignored) while the stb2 header says its AVX2 build is 20-50% faster, more than tir's 7-19% lead; the solid result is 2.2-3.6x over tinyexr's own exr_resize_float. Fuzz-found WRAP heap overflow (94405e1) and a threaded-band deadlock (8c631a7) were fixed on 2026-07-02; the lazy global kernel table is set up without atomics, undocumented.

## Caveats and trade-offs

The win over the named baseline is small and not like-for-like: the bench recipe builds stb_image_resize2 without -mavx/-mavx2/-mfma, so stb2 ran its SSE2 kernels while tir used runtime-dispatched AVX2+FMA; stb_image_resize2's own header says AVX is 10-40% faster and AVX2 about another 12%, which exceeds tir's 7-19% 4-channel lead, so tir may not beat an AVX2 build of stb2. On 1-channel Mitchell stb2 is faster in the two 2x cases (0.95x and 0.92x, derived from page data). The workload does matched work: Mitchell B=C=1/3 on both sides, clamp edges on both sides (tir default TIR_EDGE_CLAMP, stb STBIR_EDGE_CLAMP), straight alpha on tir and STBIR_4CHANNEL (no alpha weighting) on stb, f32 in and out, random data, one-shot calls that build coefficients each time; the bench does not compare outputs, and tir's SIMD kernels may reassociate sums within a small ULP budget. The Lanczos3 row compares against a 4-tap Catmull-Rom on the stb side and is excluded. The 2-5x figure is against tinyexr's own exr_resize_float, not an outside incumbent. Author-run on a single Zen 2 machine; the stb2 header version used is not recorded (gitignored, fetched on demand). tir is new (first commit 2026-07-02, last change to tools/resize 2026-07-05), developed with an AI co-author, version 0.x.

Pure C11 with a header that is safe to include from C++. Internal float32 filtering with u8, u16, f16 and f32 pixel I/O; runtime SSE2, SSE4.1 and AVX2+FMA dispatch, NEON at compile time, SVE behind a runtime gate. One arena allocation, streaming push_row/pull_row API with O(support) memory, optional C11-threads band parallelism with output identical to serial. HDR-aware (antiring, no clamping), normal-map and height-map modes, premultiplied-alpha filtering. Filters: box, triangle, B-spline, Gaussian, Mitchell, Catmull-Rom, Lanczos-2/3. Not a standalone repository: the code sits under tools/resize in the tinyexr tree (no dependency on the EXR codec for the library itself).

## Maintenance

Active (tinyexr last commit 2026-09-07, tools/resize last changed 2026-07-05), BSD-3-Clause and copyable; tir itself is 0.1.0, written July 2026 with an AI co-author, with unit tests against an independent double-precision reference, ASan/UBSan/TSan targets and a libFuzzer corpus.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification A, tier now C.
- **Tier reason:** Benchmark code is public (tools/resize/tests/tir_bench.c, Makefile target resize-bench) and the CPU is named (Ryzen 9 3950X), but the README never states the compiler (the recipe uses \$(CC); GNU make's built-in CC=cc is not overridden by 'CC ?= gcc', version unknown), the stb_image_resize2 header is fetched on demand and not version-pinned, and the recipe compiles stb2 at baseline SSE2 (-O2 -g, no -mavx/-mavx2/-mfma) while tir dispatches AVX2+FMA at runtime, so the comparison with the named baseline is not like-for-like; first-party numbers with that methodology gap are C.
- **Verifier notes:** README numbers and the derived ratios match the page; the 'fair stb2 bench' commit d480dc7 fixed an earlier filter mismatch, but the ISA mismatch remains because the resize-bench recipe ignores CFLAGS and passes no -m flags. A rerun of stb2 with -mavx2 -mfma (or -DSTBIR_AVX2) would be needed before this can carry A or claim a win over stb_image_resize2.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/syoyo/tinyexr>
  - <https://github.com/syoyo/tinyexr/commits/release>
  - <https://github.com/syoyo/tinyexr/commits/release/tools/resize>
  - <https://github.com/syoyo/tinyexr/commit/d480dc7>
  - <https://github.com/syoyo/tinyexr/tree/release/tools/resize/src>
  - <https://raw.githubusercontent.com/syoyo/tinyexr/release/tools/resize/README.md>
  - <https://raw.githubusercontent.com/syoyo/tinyexr/release/tools/resize/tests/tir_bench.c>
  - <https://raw.githubusercontent.com/syoyo/tinyexr/release/tools/resize/include/tir.h>
  - <https://raw.githubusercontent.com/syoyo/tinyexr/release/tools/resize/src/tir_kernels_x86.c>
  - <https://raw.githubusercontent.com/syoyo/tinyexr/release/tools/resize/src/tir_cpu.c>
  - <https://raw.githubusercontent.com/syoyo/tinyexr/release/Makefile>
  - <https://raw.githubusercontent.com/syoyo/tinyexr/release/LICENSE>
  - <https://raw.githubusercontent.com/nothings/stb/master/stb_image_resize2.h>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/syoyo/tinyexr/release/tools/resize/README.md>
  - <https://raw.githubusercontent.com/syoyo/tinyexr/release/tools/resize/tests/tir_bench.c>
  - <https://raw.githubusercontent.com/syoyo/tinyexr/release/tools/resize/tests/tir_test.c>
  - <https://raw.githubusercontent.com/syoyo/tinyexr/release/tools/resize/include/tir.h>
  - <https://raw.githubusercontent.com/syoyo/tinyexr/release/tools/resize/src/tir_kernels_x86.c>
  - <https://raw.githubusercontent.com/syoyo/tinyexr/release/tools/resize/src/tir_cpu.c>
  - <https://raw.githubusercontent.com/syoyo/tinyexr/release/tools/resize/src/tir_core.c>
  - <https://raw.githubusercontent.com/syoyo/tinyexr/release/tools/resize/src/tir_pipeline.c>
  - <https://raw.githubusercontent.com/syoyo/tinyexr/release/tools/resize/src/tir_table.c>
  - <https://raw.githubusercontent.com/syoyo/tinyexr/release/tools/resize/src/tir_internal.h>
  - <https://raw.githubusercontent.com/syoyo/tinyexr/release/tools/resize/src/tir_thread.c>
  - <https://raw.githubusercontent.com/syoyo/tinyexr/release/Makefile>
  - <https://raw.githubusercontent.com/syoyo/tinyexr/release/LICENSE>
  - <https://raw.githubusercontent.com/syoyo/tinyexr/release/README.md>
  - <https://raw.githubusercontent.com/nothings/stb/master/stb_image_resize2.h>
  - <https://github.com/syoyo/tinyexr/tree/release/tools/resize/src>
  - <https://github.com/syoyo/tinyexr/commits/release/tools/resize>
  - <https://github.com/syoyo/tinyexr/commit/94405e1>
  - <https://github.com/syoyo/tinyexr/commit/f0b9160>
  - <https://github.com/syoyo/tinyexr/commit/fdf7b0d>
  - <https://github.com/syoyo/tinyexr/issues?q=resize>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/syoyo/tinyexr`) · [data/wave10/enrich/raw/github_com_syoyo_tinyexr.json](../../../data/wave10/enrich/raw/github_com_syoyo_tinyexr.json) (enrichment confidence 0.8)

</details>
