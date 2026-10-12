# jpegli

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> Google's libjpeg62-compatible JPEG encoder/decoder tuned for quality per byte; not faster than libjpeg-turbo, and slower at decode.

| | |
|---|---|
| **Beats** | libjpeg-turbo |
| **Claimed result** | No speed advantage over libjpeg-turbo is claimed by the repository. Google's announcement blog post (blocked here; search snippet only) says Jpegli's coding speed is 'comparable to traditional approaches, such as libjpeg-turbo and MozJPEG', with no numbers. Third-party oximg issue #61 (Zen 4, 512 px, q80) states that jpegli decodes 1.6-2.0x slower than libjpeg-turbo. Its encode table has mozjpeg trellis at 10316 us against jpegli at 1812-1912 us (progressive 8-scan, 4:4:4, adaptive quantization on) and 534-546 us (upstream baseline, 4:2:0, AQ off), so jpegli encodes about 5.4-5.7x faster than mozjpeg trellis (derived from page data). The issue gives no jpegli versus libjpeg-turbo encode timing. |
| **Workload** | None in the project's own docs. The README lists quality and feature improvements only. Third-party measurement (oximg issue #61): JPEG to JPEG resize pipeline, fit 512 px, quality 80, single thread, Zen 4. |
| **Metric** | throughput |
| **Adoption** | 407 stars, 67 forks; libjpeg62 API and ABI compatible, tools cjpegli and djpegli |
| **Last commit** | 2026-06-01 |
| **Links** | [repository](https://github.com/google/jpegli) |

## Verdict

The repository publishes no speed numbers, and its benchmark doc is a leftover libjxl text about density metrics. The only measured numbers are third-party: oximg issue #61 (Zen 4, 512 px, q80, single-thread encode time on 1 logical CPU) kept libjpeg-turbo as its decoder because jpegli decoded 1.6-2.0x slower. It timed jpegli encodes at 1812-1912 us (jpegli-sys 0.10.2, progressive 4:4:4, AQ on), 960-976 us (baseline 4:4:4, AQ off), 615-630 us (baseline 4:2:0, AQ off) and 534-546 us (upstream 031a0077 with clang, baseline 4:2:0, AQ off), against mozjpeg trellis at 10316 us, with no libjpeg-turbo encode timing. A search snippet attributed to a libjpeg-turbo-users thread ('Jpegli', groups.google.com blocked here) says libjpeg-turbo was 2-8x faster than jpegli at baseline compression; this is unverified.

## Use it when

- New web or archive JPEGs where bytes at a given visual quality matter more than encode CPU, and the output must stay plain JPEG for every decoder.
- Linux services already linked against libjpeg62 that want jpegli's quality by swapping libjpeg.so.62 without code changes (libjpeg API only, not TurboJPEG).
- Replacing mozjpeg trellis encodes on a CPU budget: oximg issue #61 timed jpegli at 534-1912 us against mozjpeg trellis at 10316 us per 512 px q80 encode, about 5.4x to 19x faster depending on jpegli settings (derived from page data).
- Pipelines that need 16-bit or float input to the encoder or 16-bit/float output from the decoder, or XYB-ICC JPEGs.

## Skip it when

- Decode-throughput-bound workloads (thumbnailing, ML data loading): the only third-party number (oximg #61) puts jpegli decode 1.6-2.0x slower than libjpeg-turbo, with no methodology shown.
- Encode-throughput-bound workloads that are fine with libjpeg-turbo quality: no source shows jpegli encoding faster than libjpeg-turbo, and its default tool settings (progressive level 2, optimized Huffman, adaptive quantization, 4:4:4) do the most work.
- Code that uses the TurboJPEG API (tj\*), arithmetic-coded, 12-bit, lossless or hierarchical JPEGs: the decoder accepts only SOF0/SOF1/SOF2 at 8-bit precision and the encoder errors on arithmetic coding and CCIR601 sampling.
- Ingesting messy real-world files: issue #248 (open) reports djpegli rejecting progressive JPEGs with empty DHT segments ('DHT marker: no Huffman table found'), including 276 WhatsApp images from FODB that libjpeg-turbo-based decoders accept.
- Projects that need versioned releases or a drop-in shared library on macOS or Windows: there are no tags or releases (issue #44 unanswered), and lib/jpegli.cmake builds libjpeg.so only when not APPLE, WIN32 or EMSCRIPTEN.

## How it is fast

It is not built for speed: the design spends extra work on quality. The encoder does color conversion, subsampling and DCT in float (Highway SIMD, kernels capped at 8 float lanes) and adds adaptive dead-zone quantization driven by a masking field (fuzzy erosion over a pre-erosion image). The decoder gathers per-coefficient nonzero and abs-sum statistics and applies Price-Rabbani Laplacian dequantization biases, then runs float IDCT, upsampling and color conversion. Speed comes only from Highway runtime dispatch (SSE2 to AVX-512, NEON, SVE, RVV, WASM) and a streaming single-pass path for sequential fixed-Huffman encodes.

## Compared with alternatives

Pick jpegli over libjpeg-turbo only when smaller files at equal perceived quality matter more than CPU; keep libjpeg-turbo (or jpeg-nitro and zenjpeg for decode) when speed is the goal. Pick it over mozjpeg when you want a density-focused encoder at a fraction of trellis cost (oximg #61: 534-1912 us vs 10316 us), accepting that the density comparison rests on Google's own study ('Users prefer Jpegli over same-sized libjpeg-turbo or MozJPEG', not opened here).

## Integration

| | |
|---|---|
| **Form** | static lib (jpegli-static, jpegli_\* API) plus shared lib (libjpeg.so.62.3.0 drop-in on non-Apple, non-Windows targets) and CLI tools |
| **Dependencies** | Highway (third_party submodule or system libhwy), threads; libjpeg-turbo headers vendored for jpeglib.h/jmorecfg.h; tools add lcms2 or skcms, libpng, optional giflib, OpenEXR, sjpeg; tests need gtest and a system libjpeg |
| **Minimum toolchain** | CMake 3.16+; C++17 when the compiler offers it (CMake falls back to C++14 or C++11); build breakages reported on macOS Sonoma (#55) and Fedora 42 (#133) |
| **Platforms** | any Highway target with runtime dispatch: x86-64 SSE2 to AVX-512, aarch64 NEON/SVE, PPC8-10, RVV, s390x Z14/Z15, WASM, scalar fallback |
| **Thread safety** | not documented; libjpeg model of one compress/decompress object per thread, no internal multithreading found in lib/jpegli. decode_scan.cc writes edge-MCU padding blocks into a function-static sink_block shared by all decoder instances (a benign data race that thread sanitizers may flag). |
| **Drop-in for the baseline** | partial — libjpeg62 API/ABI (jpeg_\* symbols incl. jpeg_mem_src/dest, skip/crop scanlines, read/write_coefficients) but no TurboJPEG tj\* functions, no arithmetic/12-bit/lossless decode, output pixels differ from libjpeg-turbo, and the .so is not built on macOS or Windows |

## Gotchas

- Defaults depend on the entry point: through the libjpeg API, jpeg_set_defaults gives sequential mode with fixed Huffman codes (kDefaultProgressiveLevel = 0 since commit eca9351, April 2023), which takes the streaming single-pass path; cjpegli and the extras EncodeJpeg API default to progressive level 2, optimized codes, adaptive quantization and no chroma subsampling, which buffer the whole image's coefficients and tokens. In oximg #61, settings alone on the same jpegli-sys 0.10.2 build move encode time 2.9-3.1x (progressive 4:4:4 AQ on 1812-1912 us vs baseline 4:2:0 AQ off 615-630 us, derived from page data).
- Decoded pixels are not bit-exact with libjpeg-turbo: dequantization biases are computed from running statistics of the image's own coefficients and the pipeline is float, so golden-image tests written against libjpeg-turbo will fail.
- The in-repo harness (tools/benchmark/benchmark_codec_jpeg.cc) has comparison traps: the pN parameter means jpeg_simple_progression for the libjpeg codec at p0 but sequential mode for enc-jpegli at p0; the cjpeg/mozjpeg path times a subprocess including process start and file I/O while jpegli is timed in process; and the Q (libjpeg_quality) option times an extra libjpeg encode plus a distance search inside the jpegli measurement.
- Open, unreviewed PRs fix out-of-bounds bugs reachable through the library API with bad caller arguments: #242 (jpegli_crop_scanline 32-bit overflow leading to an out-of-bounds read) and #241 (jpegli_add_quant_table accepts which_tbl == 4 and writes 64 coefficients through a bogus pointer).

## Known shortcomings

- Tier D: the repo publishes no speed numbers although tools/benchmark/benchmark_codec_jpeg.cc can time jpegli against libjpeg; the third-party oximg issue #61 puts jpegli decode 1.6-2.0x slower than libjpeg-turbo and gives only a mozjpeg trellis encode comparison (10316 us against 1812-1912 us) with no libjpeg-turbo encode timing; Google's blog says speed is comparable (snippet only).
- Enricher (e106, 2026-10-05): no first-party speed numbers, D stands. The oximg issue #61 figures are single-thread encode times on 1 logical CPU; the record misses configuration N (jpegli 0.10.2 baseline 4:2:0 with adaptive quantization off, 615-630 us), and settings alone move encode time 2.9-3.1x on the same build; decode is 1.6-2.0x slower than libjpeg-turbo there with no methodology. A libjpeg-turbo-users thread (snippet only, groups.google.com blocked) says libjpeg-turbo is 2-8x faster at baseline encode. Harness traps in benchmark_codec_jpeg.cc: p0 means progressive (jpeg_simple_progression) for the libjpeg codec but sequential for enc-jpegli; the cjpeg/mozjpeg path times subprocess start plus file I/O; the Q option adds an extra libjpeg encode and distance search; defaults split (libjpeg API sequential fixed-Huffman since eca9351, cjpegli progressive 2 plus AQ plus 4:4:4). Compatibility: decoder accepts only SOF0/1/2 8-bit; no TurboJPEG API; libjpeg.so not built on Apple, Windows or Emscripten; output not bit-exact; issue #248 rejects empty DHT files; no releases (#44). Open unreviewed PRs fix library out-of-bounds accesses (#242 crop_scanline OOB read, #241 add_quant_table off-by-one OOB write).

## Caveats and trade-offs

No speed numbers in the repository, so tier D (notable: Google project, 407 stars, libjpeg62 API/ABI drop-in with cjpegli/djpegli tools). The repo has a harness that could produce numbers but publishes none: tools/benchmark/benchmark_xl with benchmark_codec_jpeg.cc times the linked libjpeg encoder and decoder by default and jpegli with the enc-jpegli/dec-jpegli options, and reports E MP/s and D MP/s. Google's announcement blog post (opensource.googleblog.com, blocked here) is known only from a search snippet ('coding speed comparable to traditional approaches, such as libjpeg-turbo and MozJPEG', no numbers). The arXiv paper 'Users prefer Jpegli over same-sized libjpeg-turbo or MozJPEG' (2403.18589, blocked) is a subjective-quality study. The only numbers are third-party and point the other way. oximg issue #61 (opened 2026-10-01, a proposal to change oximg's jpegli encoder defaults; Zen 4, 512 px, q80) says in its out-of-scope section that jpegli decodes 1.6-2.0x slower than libjpeg-turbo, with no methodology shown for that figure. Its encode table compares jpegli configurations with oximg's current jpegli setup (jpegli-sys 0.10.2, progressive 8-scan, 4:4:4, AQ on: 1812-1912 us; baseline 4:4:4 AQ off: 960-976 us, -12.1% server cycles; upstream commit 031a0077 baseline 4:2:0 AQ off: 534-546 us, -17.3%) plus mozjpeg trellis at 10316 us. It has no libjpeg-turbo encode timing. Being faster than mozjpeg's trellis mode is not a win over the category baseline (libjpeg-turbo), and trellis quantization does different, slower work. Encode cost depends heavily on settings (progressive scans, subsampling, adaptive quantization). The '+2.6% CPU and +10% bytes' figures in the search record were not found in this verifier's reading of issue #61; oximg issue #64 and sharp issue #4018 cited by the search agent were not rechecked. A PATENTS file adds a Google patent grant (JPEG XL wording). Treat as a density and quality reference, not a speed win.

API and ABI compatible with libjpeg62 (drop-in libjpeg.so.62.3.0). Encoder does color conversion, subsampling and DCT in floating point, uses a JPEG XL style distance parameter, adaptive dead-zone quantization and XYB ICC support; decoder dequantizes to the Laplacian expectation and does IDCT, upsampling and color conversion in floating point with optional 16-bit or float output. The design goal is quality per byte, not speed.

## Maintenance

Active but thinly maintained: the last merged change is a Dependabot bump (2026-06-01, #236) while about ten bug-fix PRs from May-October 2026 sit unreviewed; BSD-3-Clause with a Google patent grant and no tagged release, so it is copyable but should be treated as a quality tool, not a speed win.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification D, tier now D.
- **Tier reason:** The repository publishes no speed numbers (README and doc/benchmarking.md describe density and tooling only), and the only numbers found are third-party and show jpegli slower than libjpeg-turbo at decode (oximg issue #61), so there is no measured speed win and the entry stays D. The repo does ship a harness that could measure it (tools/benchmark/benchmark_xl with benchmark_codec_jpeg.cc), but it has no published results.
- **Verifier notes:** Keep per keep-and-document rule (not faster: decode 1.6-2.0x slower than libjpeg-turbo per third-party oximg #61; no encode speed claim). Metadata checked: BSD-3-Clause (LICENSE), 407 stars, 67 forks, not a fork, not archived, last commit 2026-06-01 (Bump the everything group, #236), active. I could not confirm the record's 'single thread' detail in the issue text as rendered.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** third-party issue figures (oximg #61)
- **Pages the verifier opened:**
  - <https://github.com/google/jpegli>
  - <https://github.com/google/jpegli/commits>
  - <https://raw.githubusercontent.com/google/jpegli/HEAD/README.md>
  - <https://raw.githubusercontent.com/google/jpegli/HEAD/doc/benchmarking.md>
  - <https://raw.githubusercontent.com/google/jpegli/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/google/jpegli/HEAD/PATENTS>
  - <https://github.com/google/jpegli/tree/main/tools>
  - <https://github.com/google/jpegli/tree/main/tools/benchmark>
  - <https://raw.githubusercontent.com/google/jpegli/HEAD/tools/benchmark/benchmark_codec_jpeg.cc>
  - <https://github.com/google/jpegli/issues?q=is%3Aissue+speed>
  - <https://github.com/oximg/oximg/issues/61>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/google/jpegli/HEAD/README.md>
  - <https://raw.githubusercontent.com/google/jpegli/HEAD/doc/benchmarking.md>
  - <https://raw.githubusercontent.com/google/jpegli/HEAD/doc/building_and_testing.md>
  - <https://raw.githubusercontent.com/google/jpegli/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/google/jpegli/HEAD/lib/jpegli.cmake>
  - <https://raw.githubusercontent.com/google/jpegli/HEAD/PATENTS>
  - <https://raw.githubusercontent.com/google/jpegli/HEAD/tools/benchmark/benchmark_codec_jpeg.cc>
  - <https://raw.githubusercontent.com/google/jpegli/HEAD/tools/cjpegli.cc>
  - <https://raw.githubusercontent.com/google/jpegli/HEAD/tools/djpegli.cc>
  - <https://github.com/google/jpegli/tree/main/lib/jpegli>
  - <https://raw.githubusercontent.com/google/jpegli/HEAD/lib/jpegli/dct-inl.h>
  - <https://raw.githubusercontent.com/google/jpegli/HEAD/lib/jpegli/idct.cc>
  - <https://raw.githubusercontent.com/google/jpegli/HEAD/lib/jpegli/encode.cc>
  - <https://raw.githubusercontent.com/google/jpegli/HEAD/lib/jpegli/encode_internal.h>
  - <https://raw.githubusercontent.com/google/jpegli/HEAD/lib/jpegli/encode_streaming.cc>
  - <https://raw.githubusercontent.com/google/jpegli/HEAD/lib/jpegli/entropy_coding.cc>
  - <https://raw.githubusercontent.com/google/jpegli/HEAD/lib/jpegli/adaptive_quantization.cc>
  - <https://raw.githubusercontent.com/google/jpegli/HEAD/lib/jpegli/decode.cc>
  - <https://raw.githubusercontent.com/google/jpegli/HEAD/lib/jpegli/decode_scan.cc>
  - <https://raw.githubusercontent.com/google/jpegli/HEAD/lib/jpegli/decode_marker.cc>
  - <https://raw.githubusercontent.com/google/jpegli/HEAD/lib/jpegli/render.cc>
  - <https://raw.githubusercontent.com/google/jpegli/HEAD/lib/jpegli/upsample.cc>
  - <https://raw.githubusercontent.com/google/jpegli/HEAD/lib/jpegli/libjpeg_wrapper.cc>
  - <https://raw.githubusercontent.com/google/jpegli/HEAD/lib/jpegli/jpeg.version.62>
  - <https://raw.githubusercontent.com/google/jpegli/HEAD/lib/extras/enc/jpegli.h>
  - <https://raw.githubusercontent.com/google/jpegli/HEAD/lib/extras/enc/jpegli.cc>
  - <https://raw.githubusercontent.com/google/jpegli/HEAD/lib/extras/enc/jpg.cc>
  - <https://raw.githubusercontent.com/google/jpegli/HEAD/lib/extras/dec/jpg.cc>
  - <https://raw.githubusercontent.com/google/jpegli/HEAD/lib/base/include_jpeglib.h>
  - <https://github.com/google/jpegli/commits/main/lib/jpegli/encode_internal.h>
  - <https://github.com/google/jpegli/issues?q=is%3Aissue+slow+OR+performance+OR+speed+OR+faster>
  - <https://github.com/google/jpegli/issues?q=is%3Aissue>
  - <https://github.com/google/jpegli/issues/248>
  - <https://github.com/google/jpegli/issues/45>
  - <https://github.com/google/jpegli/issues/44>
  - <https://github.com/google/jpegli/tags>
  - <https://github.com/google/jpegli/pulls?q=is%3Apr>
  - <https://github.com/google/jpegli/pull/242>
  - <https://github.com/google/jpegli/pull/241>
  - <https://github.com/google/jpegli/pull/249>
  - <https://github.com/oximg/oximg/issues/61>
  - <https://raw.githubusercontent.com/google/decoder-benchmarks-for-rust/HEAD/README.md>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/google/jpegli`) · [data/wave10/enrich/raw/github_com_google_jpegli.json](../../../data/wave10/enrich/raw/github_com_google_jpegli.json) (enrichment confidence 0.75)

</details>
