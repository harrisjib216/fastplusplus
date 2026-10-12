# mozjpeg

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C` · `IJG AND BSD-3-Clause AND Zlib` · 🟡 stale

> libjpeg-turbo fork that trades much slower JPEG encoding for smaller files; it is not faster than libjpeg-turbo at anything.

| | |
|---|---|
| **Beats** | libjpeg-turbo |
| **Claimed result** | No speed advantage claimed. README-mozilla.txt: 'When the default settings are used, mozjpeg is considerably slower than libjpeg-turbo or even libjpeg at compressing images. Thus, it is not generally suitable for real-time compression.' Its performance is described as highly asymmetric (compression much slower than decompression). Third-party numbers also show it slower: sergejmueller's gist (mozjpeg 2.0, 'jpegtran -copy none -progressive', 7 images) has 0.389-0.846 s against libjpeg-turbo's 0.164-0.441 s, about 2.3x slower on average for files 1.18% smaller; oximg issue #61 (Zen 4, 512 px, q80) has mozjpeg trellis at 10316 us per encode against jpegli at 1812-1912 us. With its extensions disabled it behaves exactly like libjpeg-turbo (README.md), so its decoder is libjpeg-turbo's. |
| **Workload** | None. The project documents compression speed as a deliberate cost of smaller files (trellis quantization, optimized Huffman tables, progressive scans with jpegrescan). |
| **Metric** | throughput |
| **Adoption** | 5.7k stars, 435 forks; widely deployed in web image pipelines |
| **Last commit** | 2025-06-23 |
| **Links** | [repository](https://github.com/mozilla/mozjpeg) |

## Verdict

Nothing here measures a speed win. The project itself says it compresses considerably slower than libjpeg-turbo with default settings. Third-party figures agree but lack full methodology: the 2014-era sergejmueller gist has jpegtran -progressive about 2.3x slower; oximg issue #61 (Zen 4, 512 px, q80) has trellis at 10316 us per image. mozjpeg-rs's README (2048x2048, 30 iterations, AVX2, CPU not stated) shows C mozjpeg at 210 ms with trellis against 9 ms Huffman-optimized baseline. Search-result snippets, apparently from libjpeg-turbo.org/About/Mozjpeg (page blocked, not opened, source not certain), put jpgcrush plus trellis at about 4-7x the encoding time of plain progressive for 4-15% better compression.

## Use it when

- Offline or build-time compression of web images (static-site pipelines, CDN pre-processing, image optimizers), where encoding runs once and the smaller file is downloaded many times.
- Lossless recompression of existing JPEGs with jpegtran (progressive plus scan search), when you cannot re-encode from pixels.
- Programs already on the libjpeg API that want smaller output without code changes: relink and jpeg_set_defaults() turns on the max-compression profile.
- As the reference encoder when you evaluate size-for-quality JPEG encoders such as mozjpeg-rs, zenjpeg or jpegli, all of which benchmark against it.

## Skip it when

- Real-time or per-request encoding (thumbnail proxies, camera or video frames, screenshots). Its own README-mozilla.txt says it is considerably slower than libjpeg-turbo, and even than libjpeg, at default settings. In mozjpeg-rs's README, C mozjpeg needs 210 ms with trellis against 9 ms for Huffman-optimized baseline on a 2048x2048 image (about 23x, derived from page data; hardware not stated).
- As a speed upgrade for decoding: decoding is libjpeg-turbo's code. Its default progressive output also decodes slower than baseline in libjpeg-turbo: zenjpeg's README (Ryzen 9 7950X) lists 34 MiB/s for progressive against 78.1 MiB/s for baseline 4:2:0, possibly on different files.
- Memory-constrained encoding of large images: trellis keeps quantized and unquantized whole-image coefficient arrays (whole_image and whole_image_uq in jccoefct.c), and scan optimization buffers every candidate scan in memory.
- Processes or distro packages that also need stock libjpeg-turbo: both ship libjpeg/libturbojpeg with the same names and symbols. Issue #382, open since 2020, asks for a separately named libmozjpeg, and PR #383 has been open since then.
- Projects that track upstream security fixes through tagged releases: the latest tag is v4.1.1, built on libjpeg-turbo 2.1.3. The libjpeg-turbo 3.0.x merge on master (January 2025, CMake VERSION 5.0.0) is untagged.

## How it is fast

It is not; the work goes into file size. For 3-component YCbCr, jpeg_search_progression() sets up 64 candidate scans (23 for grayscale). Each candidate gets a Huffman-statistics pass and an output pass into an in-memory buffer, and select_scans() then keeps the smallest combination (jpgcrush-style). That makes at least 128 entropy passes before trellis. Trellis quantization (quantize_trellis in jcdctmgr.c) is a scalar float rate-distortion search per 8x8 block, with lambda = 2^14.75 / ((2^16.5 + n) \* q^2) by default. It runs 2 passes per component per trellis loop over the saved unquantized coefficients of the whole image. The speed it does have is libjpeg-turbo's: SIMD color conversion, downsampling, forward DCT and baseline Huffman.

## Compared with alternatives

Pick C mozjpeg over libjpeg-turbo only when file size matters more than encode time; over mozjpeg-rs when you need the C libjpeg ABI, jpegtran's lossless recompression or the fastest Huffman-only path (mozjpeg-rs's README has C at 9 ms vs Rust 42 ms for baseline); prefer mozjpeg-rs for memory-safe Rust or slightly faster trellis (197 vs 210 ms in its README), and look at jpegli or zenjpeg when you want better quality per byte at much lower encode cost.

## Integration

| | |
|---|---|
| **Form** | static lib and shared lib (libjpeg API library plus TurboJPEG library), CMake build; cjpeg, djpeg and jpegtran tools |
| **Dependencies** | none for the library; NASM 2.13+ or Yasm 1.2.0+ for x86 SIMD; cjpeg PNG input needs libpng 1.6 and zlib (PNG_SUPPORTED defaults to TRUE; turn it off if libpng is absent) |
| **Minimum toolchain** | C89-era C compiler (GCC 4.1+ or Clang recommended, Visual C++ 2005+), CMake 2.8.12+ |
| **Platforms** | Same as libjpeg-turbo: x86, x86-64, Arm/aarch64 (Neon), PowerPC (AltiVec), MIPS (MMI) SIMD, plus a C fallback anywhere; Linux, macOS, Windows |
| **Thread safety** | Same as libjpeg: one jpeg_compress_struct per thread. The library is not thread-safe on a shared object (libjpeg.txt), and the encoder itself is single-threaded. |
| **Drop-in for the baseline** | partial: libjpeg API and ABI drop-in with smaller, slower output under default settings. Through the TurboJPEG API it is not a size upgrade, because setCompDefaults() in turbojpeg.c forces JCP_FASTEST and so behaves like plain libjpeg-turbo. |

## Gotchas

- Default output can be corrupted by a SIMD FDCT overflow, open as of 2026-10-05. Overshoot deringing (on by default) can push level-shifted samples to +/-158. The 16-bit wrapping adds in the SIMD islow forward DCT (SSE2, AVX2, MMX, Neon, MMI, AltiVec) then overflow (8 x 5056 = 40448), which flips the sign of DC/low-AC coefficients and leaves inverted-brightness 8x8 blocks (issue #444). PR #453 switches these to saturating adds and reports 2 of 639 test encodes changed. The C DCT path is not affected; -noovershoot avoids the bug.
- TurboJPEG API callers (tjCompress2/tj3Compress8, and tjbench) get libjpeg-turbo behavior, because turbojpeg.c sets JCP_FASTEST before jpeg_set_defaults(). To get mozjpeg's gains, use the libjpeg API or set the extension parameters yourself.
- jpeg_set_defaults() resets every mozjpeg parameter from JINT_COMPRESS_PROFILE. Set the profile first, then quality and the extensions. mozjpeg-rs's README warns that the Rust mozjpeg crate's setters silently undo earlier settings for the same reason.
- Output size is not monotonic across releases: issue #433 (open) shows jpegtran in 4.1.1 producing larger files than 3.1 on some inputs (402,438 vs 400,769 bytes on lab.jpg). PNG input in cjpeg is broken in the current CMake build (issue #450, fix PR #455 unmerged).

## Known shortcomings

- Not faster: tier D with the project's own README-mozilla.txt saying compression is considerably slower than libjpeg-turbo; a sergejmueller gist puts mozjpeg 2.0 jpegtran about 2.3x slower for 1.18% smaller files with no hardware. Stale (last commit 2025-06-23).
- Enricher (e116, 2026-10-05): D stands, no speed win. The default profile runs 64 candidate scans (each a Huffman-optimisation pass plus output pass) plus two trellis passes per component; mozjpeg-rs's README puts C mozjpeg at 210 ms with trellis vs 9 ms baseline Huffman-opt for a 2048x2048 image (about 23x slower, CPU unstated). The TurboJPEG API forces JCP_FASTEST, so tj callers get plain libjpeg-turbo behaviour. Correctness bug in the default path: overshoot deringing plus the 16-bit wrapping SIMD islow FDCT overflows (8 x 5056 = 40448), flipping DC/low-AC signs and inverting 8x8 blocks (issue #444; fix PR #453 open, 2 of 639 test encodes changed); not behind any catalogued speed number. Latest tag v4.1.1 (libjpeg-turbo 2.1.3) while master carries an untagged 3.0.x merge; cjpeg PNG input broken (#450); libjpeg name clash with libjpeg-turbo (#382); jpegtran size regression (#433).

## Caveats and trade-offs

No speed-win numbers anywhere, so tier D (notable: 5.7k stars, 435 forks, widely deployed in web image pipelines). It is a size-efficiency encoder (trellis quantization, optimized Huffman tables, progressive scans with jpegrescan-style scan optimization), and its own docs say it is considerably slower than libjpeg-turbo at compression with default settings. Third-party numbers agree but lack methodology: the sergejmueller gist (jpegtran -progressive with mozjpeg 2.0, 7 images, no hardware or libjpeg-turbo version stated, last updated 2019-11-14) shows about 2.3x slower lossless transcoding for 1.18% smaller files; oximg issue #61 (Zen 4, 512 px, q80, no build details) shows mozjpeg trellis at 10316 us per image, about 5.4-5.7x jpegli's progressive encode (derived from page data). libjpeg-turbo's own mozjpeg comparison page (libjpeg-turbo.org/About/Mozjpeg) is blocked here and was not read. It is a fork of libjpeg-turbo, and with its extensions disabled it behaves exactly like libjpeg-turbo, so decode speed is libjpeg-turbo's. Versions: the GitHub releases page lists v4.1.1 ('Updated to libjpeg-turbo 2.1.3', 15 Aug, year not shown) as the latest tagged release, while master's ChangeLog.md tops out at the inherited libjpeg-turbo 3.0.5 entry (master merged libjpeg-turbo 3.0.x in January 2025); speed figures in that ChangeLog are libjpeg-turbo's, not mozjpeg's. Last commit 2025-06-23 (Fix PNG detection in CMake), so maintenance is stale. License: IJG for the libjpeg API library, BSD-3-Clause for TurboJPEG and the build system, zlib for SIMD code (LICENSE.md). Useful as the baseline of the listed mozjpeg-rs and as a reference for the speed cost of trellis quantization.

Speed and size trade-off versus libjpeg-turbo: slower compression by design in exchange for smaller files; decompression speed is the inherited libjpeg-turbo SIMD speed. Every mozjpeg improvement can be switched off at run time, in which case it behaves like libjpeg-turbo. Drop-in libjpeg API and ABI, strict superset of libjpeg-turbo features. Maintainers ask that non-mozjpeg-specific fixes go to libjpeg-turbo. Third-party estimates found (not measurements from this repo): libvips maintainer in https://github.com/libvips/libvips/discussions/2045 says libjpeg-turbo is perhaps 3x to 4x faster on x86 and mozjpeg can give up to perhaps 30% extra compression by adjusting parameters; a user report in https://github.com/mozilla/mozjpeg/issues/13 claims roughly 60% smaller output but almost 10 times longer compression than libjpeg-turbo, without versions, flags or machine.

## Maintenance

Stale: the last commit is 2025-06-23 and the last tag is v4.1.1 (libjpeg-turbo 2.1.3), and six PRs sit unreviewed or in review, including the FDCT overflow fix. Licensed IJG, BSD-3-Clause and zlib, and safe to use as an offline size optimizer, but not a performance pick.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification D, tier now D.
- **Tier reason:** The project claims no speed win and its own README-mozilla.txt says it is considerably slower than libjpeg-turbo at compressing with default settings; the only third-party numbers (a 2014-era gist, oximg issue #61) also show it slower, so there are no numbers for any speed advantage and the entry stays D.
- **Verifier notes:** Keep per keep-and-document rule (not faster than libjpeg-turbo by its own docs). Metadata checked: 5.7k stars, 435 forks, forked from libjpeg-turbo, not archived, last commit 2025-06-23 (stale), license IJG AND BSD-3-Clause AND Zlib per LICENSE.md. Removed the record's reference to 'third-party numbers above', which the record never listed; added the gist and oximg figures instead.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** none (slower by design)
- **Pages the verifier opened:**
  - <https://github.com/mozilla/mozjpeg>
  - <https://github.com/mozilla/mozjpeg/commits>
  - <https://github.com/mozilla/mozjpeg/releases>
  - <https://raw.githubusercontent.com/mozilla/mozjpeg/HEAD/README.md>
  - <https://raw.githubusercontent.com/mozilla/mozjpeg/HEAD/README-mozilla.txt>
  - <https://raw.githubusercontent.com/mozilla/mozjpeg/HEAD/LICENSE.md>
  - <https://raw.githubusercontent.com/mozilla/mozjpeg/HEAD/ChangeLog.md>
  - <https://gist.github.com/sergejmueller/088dce028b6dd120a16e>
  - <https://github.com/oximg/oximg/issues/61>
- **Sources the enricher read:**
  - <https://github.com/mozilla/mozjpeg>
  - <https://github.com/mozilla/mozjpeg/commits>
  - <https://github.com/mozilla/mozjpeg/releases>
  - <https://github.com/mozilla/mozjpeg/pulls>
  - <https://github.com/mozilla/mozjpeg/issues?q=is%3Aissue+slow+OR+speed+OR+performance>
  - <https://github.com/mozilla/mozjpeg/issues/256>
  - <https://github.com/mozilla/mozjpeg/issues/433>
  - <https://github.com/mozilla/mozjpeg/issues/444>
  - <https://github.com/mozilla/mozjpeg/issues/450>
  - <https://github.com/mozilla/mozjpeg/issues/176>
  - <https://github.com/mozilla/mozjpeg/issues/382>
  - <https://github.com/mozilla/mozjpeg/pull/452>
  - <https://github.com/mozilla/mozjpeg/pull/453>
  - <https://raw.githubusercontent.com/mozilla/mozjpeg/HEAD/README.md>
  - <https://raw.githubusercontent.com/mozilla/mozjpeg/HEAD/README-mozilla.txt>
  - <https://raw.githubusercontent.com/mozilla/mozjpeg/HEAD/LICENSE.md>
  - <https://raw.githubusercontent.com/mozilla/mozjpeg/HEAD/ChangeLog.md>
  - <https://raw.githubusercontent.com/mozilla/mozjpeg/HEAD/BUILDING.md>
  - <https://raw.githubusercontent.com/mozilla/mozjpeg/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/mozilla/mozjpeg/HEAD/libjpeg.txt>
  - <https://raw.githubusercontent.com/mozilla/mozjpeg/HEAD/usage.txt>
  - <https://raw.githubusercontent.com/mozilla/mozjpeg/HEAD/cjpeg.c>
  - <https://raw.githubusercontent.com/mozilla/mozjpeg/HEAD/jcparam.c>
  - <https://raw.githubusercontent.com/mozilla/mozjpeg/HEAD/jcmaster.c>
  - <https://raw.githubusercontent.com/mozilla/mozjpeg/HEAD/jcdctmgr.c>
  - <https://raw.githubusercontent.com/mozilla/mozjpeg/HEAD/jccoefct.c>
  - <https://raw.githubusercontent.com/mozilla/mozjpeg/HEAD/jcext.c>
  - <https://raw.githubusercontent.com/mozilla/mozjpeg/HEAD/turbojpeg.c>
  - <https://raw.githubusercontent.com/mozilla/mozjpeg/HEAD/tjbench.c>
  - <https://raw.githubusercontent.com/imazen/mozjpeg-rs/HEAD/README.md>
  - <https://raw.githubusercontent.com/imazen/zenjpeg/HEAD/README.md>
  - <https://raw.githubusercontent.com/imazen/zenjpeg/HEAD/benchmarks/README.md>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/mozilla/mozjpeg`) · [data/wave10/enrich/raw/github_com_mozilla_mozjpeg.json](../../../data/wave10/enrich/raw/github_com_mozilla_mozjpeg.json) (enrichment confidence 0.85)

</details>
