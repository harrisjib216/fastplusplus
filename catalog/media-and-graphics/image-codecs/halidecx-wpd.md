# wpd (WebP decoder)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust and assembly, C ABI (wpd.h)` · `BSD-2-Clause` · 🟢 active

> Rust and hand-written assembly WebP decoder with a C ABI; 1.04-1.76x faster than libwebp 1.6.0 on one thread.

| | |
|---|---|
| **Beats** | libwebp at pinned revision 94d3c4a (decoder version 1.6.0), static libwebpdecoder plus libwebpdemux built through Meson's CMake subproject, single-threaded |
| **Claimed result** | README table (median ms per 48-decode run, libwebp / wpd): lossy.webp YUV420P 180.40/173.56 = 1.04x; simplelf-lossy.webp YUV420P 174.43/162.07 = 1.08x; anim_yuv.webp RGBA 190.90/169.18 = 1.13x; lossless.webp RGBA 195.75/111.27 = 1.76x; anim_rgb.webp RGBA 104.47/62.56 = 1.67x; a_lossy.webp YUVA420P 50.70/36.38 = 1.39x; anim_yuva.webp RGBA 494.37/374.46 = 1.32x. image-webp is slower than libwebp on every RGBA row (e.g. lossless 231.50 ms, anim_yuva 776.54 ms). With both decoders forced to RGBA on the same machine (AVX2_BENCHMARKS.md at commit 0a453d8) the lossy stills give 195.16/189.38 = 1.03x (lossy.webp), 188.91/179.66 = 1.05x (simplelf-lossy.webp) and 71.78/60.37 = 1.19x (a_lossy.webp). |
| **Workload** | Median wall-clock time of one process doing 48 decodes (hyperfine -N, 3 warmups, 20 runs; wpd --threads 1, libwebp use_threads off; output discarded to /dev/null but the requested format conversion still runs) on 7 files from halidecx/wpd-test-data. Both decoders request the same output format per row: planar YUV420P/YUVA420P for lossy stills, RGBA for lossless stills and composited animations. Decode defaults match libwebp's (loop filtering and fancy upsampling on). image-webp 0.2.4 appears only in RGBA rows. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-13700K, Linux x86-64, benchmark pinned to CPU 0 (named in the README at commit 64273a2 and in AVX2_BENCHMARKS.md at commit 0a453d8; the 2026-10-01 README reformat 85e77ee dropped the machine paragraph but kept the same table numbers) |
| **Compiler and flags** | Meson release build (default buildtype=release, assembly enabled, -Dtrim_dsp=false); Rust release profile with lto=fat, codegen-units=1 and opt-level 3 for dependencies (Cargo.toml); libwebp built through the Meson CMake subproject (libwebp's CMake default build type is Release); rustc, C compiler and NASM versions are not stated |
| **Adoption** | 12 stars |
| **Last commit** | 2026-10-03 |
| **Links** | [repository](https://github.com/halidecx/wpd) · [benchmark](https://github.com/halidecx/wpd) |

## Verdict

First-party: scripts/bench.sh runs hyperfine -N (3 warmups, 20 runs) on one process doing 48 decodes, on an Intel Core i7-13700K pinned to CPU 0, comparing wpd --threads 1 with tools/libwebpdec.c over a static libwebp 1.6.0 (pinned 94d3c4a, built through Meson's CMake subproject, use_threads off), both producing the same output format; medians were 173.56 versus 180.40 ms for a 1024x1024 lossy still to YUV420P (1.04x), 111.27 versus 195.75 ms for a 576x576 lossless still to RGBA (1.76x) and 62.56 versus 104.47 ms for a 400x400 12-frame animation (1.67x); rustc, C compiler and nasm versions are not stated. Reading both drivers: each iteration builds a fresh decoder, wpd still runs the requested conversion when output goes to /dev/null, wpd also copies the input on every open, and the YUV rows compare libwebp writing into a separately allocated output buffer with wpd handing out its own planes; I found no correctness bug behind the numbers.

## Use it when

- Decode-heavy services or apps whose WebP traffic is mostly lossless stills or animations: 1.76x on lossless.webp (576x576, to RGBA), 1.67x on anim_rgb.webp (12 frames, 400x400) and 1.32x on anim_yuva.webp versus single-threaded libwebp.
- Pipelines that want planar YUV420 or YUVA420 (video encoders, GPU texture upload), since wpd returns its internal planes without a copy.
- Decoding untrusted WebP where libwebp's C history (CVE-2023-4863) is a concern: Rust core, a fuzz target, frame_size_limit to cap memory before allocation, and an -Denable_asm=false build for full memory-safety guarantees at a speed cost.
- C or C++ projects on x86-64 or AArch64 that can add Cargo, Meson and nasm to the build and link a static or shared library through wpd.h.

## Skip it when

- Mostly lossy photos: the gain is 1.04x and 1.08x to YUV420P and 1.03x to 1.05x to RGBA, close to libwebp's speed.
- Palette (colour-indexed) lossless images: the whole-corpus run in AVX2_BENCHMARKS.md (commit 0a453d8) had wpd slower than libwebp on palette2bpp_rgb.webp (0.629x) and palette_rgb.webp (0.775x).
- You need encoding, or a crates.io release, a CMake or Bazel build, or a toolchain without Rust: wpd is decoder-only, version 0.2.0, consumed as a git dependency or through Meson.
- You need settled, audited code: the project is months old with fast churn (the AVX2 kernels landed 2026-10-01, the day after the table was measured), and a September 2026 audit fixed an out-of-bounds write in the AArch64 loop-filter assembly and an out-of-bounds read in the ARM32 one (PR #30).
- Large images: the published workload tops out at 1024x1024, so behaviour on multi-megapixel photos is not measured.

## How it is fast

The DSP kernels (VP8 IDCT, loop filters and intra predictors, VP8L predictors, colour transforms and palette mapping, alpha unfiltering, premultiply/blend, YUV-to-RGB with fancy upsampling) are hand-written NASM for x86 (C, SSE2, SSSE3, SSE4.1 and AVX2 variants chosen at run time) and assembly for AArch64 and 32-bit ARM, each checked against the reference by checkasm. AVX2_BENCHMARKS.md profiles about 74% of lossless cycles in VP8L entropy decoding (decode_pixels) and about 49% of lossy cycles in coefficient decoding, so most of the lossless and animation gain comes from the Rust entropy, compositing and output paths rather than SIMD. For YUV420P output wpd hands out its own decoded planes instead of copying them into a separate buffer. An optional thread pool (n_threads) runs parallel pipelines and decodes animation frames ahead; the published table uses one thread.

## Compared with alternatives

No other WebP decoder is catalogued: the pure-Rust image-webp 0.2.4, timed in the same harness, is slower than libwebp on every RGBA row (lossless 231.50 versus 195.75 ms, anim_yuva 776.54 versus 494.37 ms), so wpd is the pick when you want a Rust-based decoder that beats libwebp rather than trails it; @napi-rs/image is a Node.js binding over libwebp, not an alternative decoder.

## Integration

| | |
|---|---|
| **Form** | static lib + shared lib (C ABI, wpd.pc); Rust crate via git dependency |
| **Dependencies** | Build: Rust toolchain with Cargo, Meson &gt;= 1.4.0, nasm on x86 (crate build uses cc and nasm-rs); crate dependency zerocopy 0.8; runtime libm and pthreads |
| **Minimum toolchain** | Rust 1.82 (rust-version), C11 for the C parts, Meson 1.4.0; -Dnightly_size needs nightly Rust with rust-src |
| **Platforms** | x86 and x86-64 with NASM (ELF64, Win64 and Mach-O64 assemble; runtime checks ran on Linux only), AArch64 and 32-bit ARM assembly, portable Rust paths with -Denable_asm=false; Linux, macOS and Windows targets in the build files |
| **Thread safety** | One call at a time per decoder handle, including const queries (external synchronization); different handles can be used concurrently. With n_threads other than 1 the decoder starts worker threads and the process-global log callback may be called concurrently from them. |
| **Drop-in for the baseline** | partial — different API (wpd_decoder_\* / wpd_decode instead of WebPDecode and WebPAnimDecoder), but parity tests require byte-identical output to libwebp, so switching is a call-site rewrite rather than a behaviour change |

## Gotchas

- n_threads = 0, the default in both the Rust Options and the CLI, means every processor the process may use; set 1 to get libwebp-like single-threaded behaviour (a C decoder stays on one thread only until options are set).
- Decoder-owned frame memory, including the zero-copy YUV planes, is invalidated by the next call on that decoder; use wpd_decoder_set_output_buffer or wpd_decode_into for caller-owned memory. wpd_decoder_open copies the input; open_borrowed does not.
- Assembly is on by default, so the memory-safety claim holds fully only with -Denable_asm=false; the -Dnightly_size sealed library aborts the process on an internal panic instead of returning WPD_ERR_INTERNAL.
- Older README tables and the 'Introducing wpd' blog post (seen as a search snippet only: 1.61x-2.92x versus libwebp, 2.17x-4.56x versus image-webp) predate commit 0a453d8, which made both decoders emit the same pixel format; quote only the current table.

## Known shortcomings

- Rust plus hand-written assembly with a C ABI (wpd.h), not C++. README numbers match (1.04x-1.76x vs libwebp decoder 1.6.0 at pin 94d3c4a); the CPU (i7-13700K) is named only in README at 64273a2 and the deleted AVX2_BENCHMARKS.md, no rustc or cc versions. The earlier 2.38x-4.56x table (c91dc1e) was against image-webp, not libwebp, with wpd emitting native YUV against RGBA baselines on an Apple M5 Pro; 0a453d8 fixed the harness to matching formats.
- Test images are at most 1024x1024; in the AVX2_BENCHMARKS.md corpus wpd is slower than libwebp on palette2bpp_rgb.webp (0.629x) and palette_rgb.webp (0.775x). The YUV rows hand out wpd's own planes zero-copy while libwebp writes a separate output buffer (API difference). PR #30 audit fixed an aarch64 assembly out-of-bounds write and an arm32 out-of-bounds read. Not on crates.io. The author's blog figures (1.61-2.92x) predate the harness fix.

## Caveats and trade-offs

First-party numbers on very fresh code: measured 2026-09-30 on wpd 59a1c12 plus then-uncommitted AVX2 changes (landed as a78b2c4 on 2026-10-01). Lossy stills gain only 1.04x-1.08x (1.03x-1.05x when both output RGBA); the larger wins are lossless (1.76x) and animation (1.13x-1.67x). Earlier README tables showed much larger ratios: the 2.38x and 4.56x figures in the search snippet come from the c91dc1e table (2026-09-17) and are relative to image-webp, not libwebp (libwebp/wpd in that table is 1.10x-1.85x, derived from page data); the f5c5b33 table gave libwebp/wpd 1.26x-3.07x (derived from page data); the 54d03ee table, run before f5c5b33 pinned wpd to one thread, reached 17.19x versus image-webp. Those runs were on an Apple M5 Pro and the old scripts/bench.sh asked libwebp and image-webp for RGBA while wpd emitted its native output (planar YUV for lossy), so wpd skipped the YUV-to-RGB conversion the baselines performed. Commit 0a453d8 ('bench: compare matching formats and expose libwebp threading') fixed the harness, and AVX2_BENCHMARKS.md states that the corrected x86 numbers miss the old ARM ratios on six of seven images. The current README still says 'reproduce the CPU affinity above' although the machine line was removed. Test files live in a separate repo (halidecx/wpd-test-data). Language is Rust plus hand-written assembly (NASM on x86, ARM/AArch64 directories) with a C ABI (include/wpd.h); C appears only in headers, tools and test harnesses. It is not C++, so it falls outside the C++ language filter, but C++ code can call it through wpd.h. The LICENSE file (BSD-2-Clause) was only added on 2026-10-03; Cargo.toml declared BSD-2-Clause earlier.

Decoder only. Needs the Rust toolchain plus nasm on x86 (Meson build). Assembly is on by default; building with -Denable_asm=false gives memory-safety guarantees at the cost of speed. C API in include/wpd.h, installs static and shared libraries plus wpd.pc, so it is callable from C++. Streaming and cropping/scaling options exist.

## Maintenance

Active (last commit 2026-10-03, 34 pull requests, 12 stars, version 0.2.0, not on crates.io) and BSD-2-Clause (LICENSE file added 2026-10-03), so copyable, but young enough that you should pin a commit and run its parity, checkasm and testdata suites before shipping.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party table in README.md produced by the public harness scripts/bench.sh (hyperfine -N, 3 warmups, 20 runs, 48 decodes per invocation) with tools/libwebpdec.c driving libwebp at pinned revision 94d3c4a (decoder version 1.6.0). The CPU (Intel Core i7-13700K) is named only in the README at commit 64273a2 and in the since-deleted AVX2_BENCHMARKS.md, and no rustc, C compiler or NASM version is given anywhere, so it falls short of A.
- **Verifier notes:** Numbers match the current README exactly; the drop from the earlier 2.38x-4.56x table is explained by a harness fix (matching output formats, one thread) plus a move from Apple M5 Pro to i7-13700K, not by a regression. Please set language to 'Rust and assembly, C ABI (wpd.h)' via decisions (language is not a correctable field here); the record's current language string is accurate.
- **Fields the verifier corrected:** `baseline`, `hardware`, `compiler_and_flags`, `workload`, `claimed_speedup`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/halidecx/wpd/HEAD/README.md>
  - <https://raw.githubusercontent.com/halidecx/wpd/HEAD/scripts/bench.sh>
  - <https://raw.githubusercontent.com/halidecx/wpd/HEAD/meson.build>
  - <https://raw.githubusercontent.com/halidecx/wpd/HEAD/meson_options.txt>
  - <https://raw.githubusercontent.com/halidecx/wpd/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/halidecx/wpd/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/halidecx/wpd/HEAD/subprojects/libwebp.wrap>
  - <https://raw.githubusercontent.com/halidecx/wpd/HEAD/tools/libwebpdec.c>
  - <https://raw.githubusercontent.com/halidecx/wpd/HEAD/src/options.rs>
  - <https://raw.githubusercontent.com/halidecx/wpd/64273a2/README.md>
  - <https://raw.githubusercontent.com/halidecx/wpd/0a453d8/README.md>
  - <https://raw.githubusercontent.com/halidecx/wpd/0a453d8/AVX2_BENCHMARKS.md>
  - <https://raw.githubusercontent.com/halidecx/wpd/85e77ee/README.md>
  - <https://raw.githubusercontent.com/halidecx/wpd/9748ced/README.md>
  - <https://raw.githubusercontent.com/halidecx/wpd/f5c5b33/README.md>
  - <https://raw.githubusercontent.com/halidecx/wpd/54d03ee/README.md>
  - <https://raw.githubusercontent.com/halidecx/wpd/c91dc1e/README.md>
  - <https://raw.githubusercontent.com/halidecx/wpd/f5c5b33/scripts/bench.sh>
  - <https://raw.githubusercontent.com/halidecx/wpd/c91dc1e/scripts/bench.sh>
  - <https://github.com/halidecx/wpd>
  - <https://github.com/halidecx/wpd/commits>
  - <https://github.com/halidecx/wpd/commits/main/README.md>
  - <https://github.com/halidecx/wpd/tree/main/src>
  - <https://raw.githubusercontent.com/webmproject/libwebp/94d3c4a7b85aa34ca68963e3b3f00298f47c0bbb/src/dec/vp8i_dec.h>
  - <https://raw.githubusercontent.com/webmproject/libwebp/94d3c4a7b85aa34ca68963e3b3f00298f47c0bbb/CMakeLists.txt>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/halidecx/wpd/HEAD/README.md>
  - <https://raw.githubusercontent.com/halidecx/wpd/HEAD/scripts/bench.sh>
  - <https://raw.githubusercontent.com/halidecx/wpd/HEAD/meson.build>
  - <https://raw.githubusercontent.com/halidecx/wpd/HEAD/meson_options.txt>
  - <https://raw.githubusercontent.com/halidecx/wpd/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/halidecx/wpd/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/halidecx/wpd/HEAD/subprojects/libwebp.wrap>
  - <https://raw.githubusercontent.com/halidecx/wpd/HEAD/include/wpd.h>
  - <https://raw.githubusercontent.com/halidecx/wpd/HEAD/tools/libwebpdec.c>
  - <https://raw.githubusercontent.com/halidecx/wpd/HEAD/tools/wpd.rs>
  - <https://raw.githubusercontent.com/halidecx/wpd/HEAD/tools/output.rs>
  - <https://raw.githubusercontent.com/halidecx/wpd/HEAD/src/api.rs>
  - <https://raw.githubusercontent.com/halidecx/wpd/HEAD/src/options.rs>
  - <https://raw.githubusercontent.com/halidecx/wpd/HEAD/src/convert.rs>
  - <https://raw.githubusercontent.com/halidecx/wpd/HEAD/src/driver/mod.rs>
  - <https://raw.githubusercontent.com/halidecx/wpd/HEAD/src/driver/export.rs>
  - <https://raw.githubusercontent.com/halidecx/wpd/HEAD/src/driver/convert.rs>
  - <https://raw.githubusercontent.com/halidecx/wpd/HEAD/src/driver/lossy.rs>
  - <https://raw.githubusercontent.com/halidecx/wpd/HEAD/tests/parity.c>
  - <https://raw.githubusercontent.com/halidecx/wpd/0a453d8/AVX2_BENCHMARKS.md>
  - <https://github.com/halidecx/wpd/tree/main/tools>
  - <https://github.com/halidecx/wpd/tree/main/src>
  - <https://github.com/halidecx/wpd/tree/main/src/driver>
  - <https://github.com/halidecx/wpd/commits>
  - <https://github.com/halidecx/wpd/issues?q=is%3Aissue>
  - <https://github.com/halidecx/wpd/pulls?q=is%3Apr>
  - <https://github.com/halidecx/wpd/pull/30>
  - <https://github.com/halidecx/wpd/pull/31>
  - <https://github.com/halidecx/wpd-test-data>
  - <https://raw.githubusercontent.com/halidecx/wpd-test-data/HEAD/lossy.webp>
  - <https://raw.githubusercontent.com/halidecx/wpd-test-data/HEAD/simplelf-lossy.webp>
  - <https://raw.githubusercontent.com/halidecx/wpd-test-data/HEAD/lossless.webp>
  - <https://raw.githubusercontent.com/halidecx/wpd-test-data/HEAD/a_lossy.webp>
  - <https://raw.githubusercontent.com/halidecx/wpd-test-data/HEAD/anim_rgb.webp>
  - <https://raw.githubusercontent.com/halidecx/wpd-test-data/HEAD/anim_yuv.webp>
  - <https://raw.githubusercontent.com/halidecx/wpd-test-data/HEAD/anim_yuva.webp>
  - <https://raw.githubusercontent.com/halidecx/wpd-test-data/HEAD/palette2bpp_rgb.webp>
  - <https://raw.githubusercontent.com/halidecx/wpd-test-data/HEAD/palette_rgb.webp>
  - <https://raw.githubusercontent.com/webmproject/libwebp/94d3c4a7b85aa34ca68963e3b3f00298f47c0bbb/cmake/cpu.cmake>
  - <https://crates.io/api/v1/crates/wpd>
  - <https://github.com/mg-chao/turbo-webp>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/halidecx/wpd`) · [data/wave10/enrich/raw/github_com_halidecx_wpd.json](../../../data/wave10/enrich/raw/github_com_halidecx_wpd.json) (enrichment confidence 0.8)

</details>
