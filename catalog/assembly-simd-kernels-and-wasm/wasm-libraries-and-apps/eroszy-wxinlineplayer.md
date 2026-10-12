# WXInlinePlayer

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly libraries and apps](README.md)</sub>

**Tier D** (directional, no numbers) · Study only · `JavaScript with C/C++ FLV demuxer and H.264/H.265 decoders compiled by Emscripten to WebAssembly and asm.js` · `Anti-996 License 1.0 (draft; non-OSI); package.json says ISC` · 🔴 abandoned

> Browser FLV player that soft-decodes H.264/H.265 in WebAssembly/asm.js; claims lower CPU than FFmpeg-based wasm players.

| | |
|---|---|
| **Beats** | FFmpeg-based wasm/asm.js H.264/H.265 web players: WASMVideoPlayer and the Taobao (Shoutao) and Huajiao implementations |
| **Claimed result** | README (Chinese): on the developer's machine, for the same video, memory and CPU use differ little from the FFmpeg-based players of Taobao (Shoutao) and Huajiao, overall performance is about 5-10% better, and H.265 about 30% better because deblocking is reduced. The H.265 table image (images/benchmark.png) gives mean CPU / memory: WXInlinePlayer 64% / 162 MB, WASMVideoPlayer 102% / 197 MB, Taobao H265 91% / 174 MB, Huajiao H265 98% / 202 MB, i.e. about 30-37% less CPU (derived from page data). |
| **Workload** | Playing the same FLV video (H.265 for the table) in a browser on the developer's machine and recording mean CPU and memory use; clip, resolution, browser and hardware unstated. |
| **Metric** | throughput |
| **Hardware** | The developer's local machine (not specified) |
| **Compiler and flags** | Emscripten 1.38.45 (per README build note) |
| **Adoption** | 1.5k stars |
| **Last commit** | 2022-03-26 |
| **Links** | [repository](https://github.com/ErosZy/WXInlinePlayer) · [benchmark](https://github.com/ErosZy/WXInlinePlayer) |

## Verdict

First-party only: a README screenshot (images/benchmark.png) of H.265 FLV playback on the developer's own machine shows mean CPU 64% and memory 162 MB versus 91-102% and 174-202 MB for WASMVideoPlayer and the Taobao and Huajiao FFmpeg-based players, with clip, resolution, browser and hardware unstated and no benchmark code. The code shows the H.265 decoder skips deblocking and SAO, so the gain is partly from producing a lower-quality, non-conforming picture rather than from a faster equivalent decoder.

## Use it when

- Inline or autoplaying H.264 FLV clips in the WeChat WebView or other mobile browsers that hijack the native video element (ad, marketing or animation clips).
- Low-latency HTTP-FLV live streams at modest settings; the README reports smooth playback of 1280x720, 1024 kbps, 24 fps on mid- to high-end phones and 1-2 s lower latency than MSE-based video.
- Pages that are sensitive to decoder download size and only need Baseline-profile H.264 (the TinyH264 bundle).
- As reference code for wiring an Emscripten-built decoder, a C++ FLV demuxer and a WebGL YUV renderer together.

## Skip it when

- When picture fidelity matters for H.265: with deblocking and SAO disabled the decoder is not conforming, and because both are in-loop filters the errors propagate through inter-predicted frames until the next random-access picture.
- Untrusted or malformed FLV input: the demuxer does not validate NAL length fields, and open issue #118 (June 2026) reports a reproducible memory-safety bug in FLV video-tag parsing with no maintainer reply.
- 10-bit (Main10) HEVC or non-4:2:0 content: the H.265 output path sizes and copies frames as 8-bit 4:2:0.
- Projects that need an OSI licence: the code is under the draft 'Anti 996' License 1.0 (package.json still says ISC).
- Anything needing seek, MP4/HLS/DASH containers or active maintenance: seek is a stub (try2seek returns 0), the roadmap items after V1.4 never shipped, and the last commit was 2022-03-26.

## How it is fast

Instead of a slimmed FFmpeg build (the README cites about 2 MB, 600 KB gzipped), it links small single-purpose decoders (TinyH264 about 180 KB, OpenH264 about 260 KB, libde265 about 210 KB gzipped) behind its own C++ FLV demuxer, built with Emscripten -O3, Closure and --llvm-lto 3. The H.265 bundle's speed gain comes mainly from doing less work: lib/codec/src/codec/codec.h sets DE265_DECODER_PARAM_DISABLE_DEBLOCKING and DE265_DECODER_PARAM_DISABLE_SAO to true, so both HEVC in-loop filters are skipped. Rendering uses WebGL YUV-to-RGB on the main thread while decoding stays in a worker.

## Compared with alternatives

Among the catalogued wasm media entries, TurboRes targets ProRes decoding and Pare targets encoding against ffmpeg.wasm; pick WXInlinePlayer only when the job is playing H.264/H.265 FLV (especially live HTTP-FLV) inline inside WeChat or similar WebViews.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | Bundled third-party decoders (OpenH264, TinyH264, libde265) compiled to wasm/asm.js; JS deps eventemitter3, buffer, mobile-detect, promise-polyfill; building needs parcel, Emscripten 1.38.45 exactly, CMake 3.16+ and make on a Unix host |
| **Minimum toolchain** | Emscripten 1.38.45 (README warns other versions give wasm32 errors), C++11, CMake 3.16+ |
| **Platforms** | Browsers with Worker, fetch, ReadableStream, Web Audio, AAC support and WebGL (falls back to asm.js without WebAssembly); README lists Android 5+, iOS 10+, Chrome 25+, Firefox 57+, Edge 15+, Safari 10.1+; UC and Quark browsers explicitly refused |
| **Thread safety** | Not documented; the wasm module holds one global Codec instance (main.cpp), so each player needs its own worker |
| **Drop-in for the baseline** | no |

## Gotchas

- The H.265 build turns off both deblocking and SAO (codec.h: DE265_DECODER_PARAM_DISABLE_DEBLOCKING and DE265_DECODER_PARAM_DISABLE_SAO set true) and does not suppress faulty pictures; the README only says 'reduced deblock'. The 30% H.265 advantage over FFmpeg-based players therefore compares unequal work: FFmpeg's HEVC decoder runs both in-loop filters.
- FLV/NAL parsing trusts length fields: Buffer::slice has no bounds check, read_uint8 asserts offset &lt;= length (off by one), and the H.265 path slices each NAL by a 32-bit length read from the stream; issues #48 and #84 report 'memory access out of bounds' on real HTTP-FLV streams and #118 reports a sanitizer-reproducible memory-safety bug.
- H.265 frames are copied as width\*height\*3/2 bytes of 8-bit 4:2:0 and tagged with the FLV tag timestamp of the packet that released them, not the picture's own presentation time, so reordered or high-bit-depth streams can show wrong timing or garbage.
- Production builds keep Emscripten ASSERTIONS=1, and H.265 in FLV relies on the Kingsoft (ksvc) FLV extension, so standard FFmpeg cannot mux it without the ksvc patch.

## Known shortcomings

- The metric is CPU and memory use (H.265 CPU 64% vs 91-102%, memory 162 vs 174-202 MB from benchmark.png), not throughput, and the H.265 gain comes from reduced deblocking, so the output is not shown to be equal; Anti-996 licence (non-OSI, reference only).
- Enricher: the H.265 build sets DE265_DECODER_PARAM_DISABLE_DEBLOCKING and DISABLE_SAO (lib/codec/src/codec/codec.h), skipping both in-loop filters so the output is non-conforming with drift and the 30% CPU gain over FFmpeg players is unequal work (the README says only 'reduced deblock'); unchecked FLV/NAL lengths (Buffer::slice has no bounds check, read_uint8 has an off-by-one assert); open #118 memory-safety report unanswered, #48/#84 'memory access out of bounds'; 8-bit 4:2:0 only. Retiered to D.

## Caveats and trade-offs

First-party prose and one screenshot table; no hardware, browser, clip or benchmark code. The H.265 gain is attributed to reduced deblocking, so the decoder likely does less filtering than a conforming FFmpeg HEVC decoder (output not shown to be equivalent). Two of the three baselines are closed commercial players. Anti-996 License (non-OSI, conflicting ISC in package.json), so reference only; bundles OpenH264, TinyH264 and libde265 decoders. Last commit 2022-03-26. [retier] Deblocking and SAO disabled in the H.265 build (non-conforming output); unchecked FLV/NAL lengths; open memory-safety reports #118, #48, #84; 8-bit 4:2:0 only

License is 'Anti 996' Version 1.0 (Draft), a non-OSI licence; H.265 support extends the FLV format (Kingsoft spec); UC browser unsupported because it disables WebAssembly/asm.js; reduced deblocking trades some picture quality for speed.

## Maintenance

Abandoned since 2022-03-26 (231 commits, 1.5k stars, 14 open issues including an unanswered memory-safety report) and under the non-OSI draft Anti-996 licence, so reference only; pin Emscripten 1.38.45 if you must rebuild it.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now D.
- **Tier reason:** First-party README prose plus a table image (images/benchmark.png) of mean CPU and memory use during H.265 playback against three FFmpeg-based wasm players; no hardware, clip, browser, flags or benchmark code.
- **Retiered** C to D: Enricher (2026-10-12): unequal work behind the measured CPU gain. The H.265 build disables both in-loop filters (DE265_DECODER_PARAM_DISABLE_DEBLOCKING and DISABLE_SAO in lib/codec/src/codec/codec.h), so its output is non-conforming with drift while the FFmpeg-based players decode fully; the README discloses only 'reduced deblock'. No valid like-for-like measurement.
- **Verifier notes:** The benchmark image is readable via raw.githubusercontent.com and contains the numbers the record lacked (CPU 64% vs 91-102%, memory 162 vs 174-202 MB); the record's 'memory and CPU about the same' paraphrase applies to the general comparison, not the H.265 table. Metric is CPU and memory, not throughput; the orchestrator may want to change the metric field. 1.5k stars, abandoned (last commit 2022-03-26).
- **Fields the verifier corrected:** `claimed_speedup`, `baseline`, `license`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-90 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/ErosZy/WXInlinePlayer>
  - <https://github.com/ErosZy/WXInlinePlayer/commits>
  - <https://github.com/ErosZy/WXInlinePlayer/tree/master/lib/codec/src>
  - <https://github.com/ErosZy/WXInlinePlayer/tree/master/lib/codec/src/codec>
  - <https://github.com/ErosZy/WXInlinePlayer/tree/master/lib/codec/src/factor>
  - <https://raw.githubusercontent.com/ErosZy/WXInlinePlayer/HEAD/README.md>
  - <https://raw.githubusercontent.com/ErosZy/WXInlinePlayer/HEAD/images/benchmark.png>
  - <https://raw.githubusercontent.com/ErosZy/WXInlinePlayer/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/ErosZy/WXInlinePlayer/HEAD/package.json>
  - <https://raw.githubusercontent.com/ErosZy/WXInlinePlayer/HEAD/build.sh>
  - <https://raw.githubusercontent.com/ErosZy/WXInlinePlayer/HEAD/lib/codec/build.sh>
  - <https://raw.githubusercontent.com/ErosZy/WXInlinePlayer/HEAD/lib/codec/src/codec/codec.cpp>
  - <https://raw.githubusercontent.com/ErosZy/WXInlinePlayer/HEAD/lib/codec/src/factor/h265_codec_factor.cpp>
- **Sources the enricher read:**
  - <https://github.com/ErosZy/WXInlinePlayer>
  - <https://github.com/ErosZy/WXInlinePlayer/issues>
  - <https://github.com/ErosZy/WXInlinePlayer/issues?q=is%3Aissue+h265>
  - <https://github.com/ErosZy/WXInlinePlayer/issues?q=is%3Aissue+%E8%8A%B1%E5%B1%8F>
  - <https://github.com/ErosZy/WXInlinePlayer/issues/5>
  - <https://github.com/ErosZy/WXInlinePlayer/issues/118>
  - <https://github.com/ErosZy/WXInlinePlayer/tree/master/src>
  - <https://github.com/ErosZy/WXInlinePlayer/tree/master/src/processor>
  - <https://raw.githubusercontent.com/ErosZy/WXInlinePlayer/HEAD/README.md>
  - <https://raw.githubusercontent.com/ErosZy/WXInlinePlayer/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/ErosZy/WXInlinePlayer/HEAD/package.json>
  - <https://raw.githubusercontent.com/ErosZy/WXInlinePlayer/HEAD/build.sh>
  - <https://raw.githubusercontent.com/ErosZy/WXInlinePlayer/HEAD/lib/codec/build.sh>
  - <https://raw.githubusercontent.com/ErosZy/WXInlinePlayer/HEAD/lib/codec/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ErosZy/WXInlinePlayer/HEAD/lib/codec/tool/compile.js>
  - <https://raw.githubusercontent.com/ErosZy/WXInlinePlayer/HEAD/lib/codec/tool/wrapper.js>
  - <https://raw.githubusercontent.com/ErosZy/WXInlinePlayer/HEAD/lib/codec/src/main.cpp>
  - <https://raw.githubusercontent.com/ErosZy/WXInlinePlayer/HEAD/lib/codec/src/codec/codec.h>
  - <https://raw.githubusercontent.com/ErosZy/WXInlinePlayer/HEAD/lib/codec/src/codec/codec.cpp>
  - <https://raw.githubusercontent.com/ErosZy/WXInlinePlayer/HEAD/lib/codec/src/factor/h265_codec_factor.cpp>
  - <https://raw.githubusercontent.com/ErosZy/WXInlinePlayer/HEAD/lib/codec/src/factor/codec_factor.h>
  - <https://raw.githubusercontent.com/ErosZy/WXInlinePlayer/HEAD/lib/codec/src/demuxer/decoder.cpp>
  - <https://raw.githubusercontent.com/ErosZy/WXInlinePlayer/HEAD/lib/codec/src/stream/buffer.cpp>
  - <https://raw.githubusercontent.com/ErosZy/WXInlinePlayer/HEAD/lib/codec/3rdparty/de265/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ErosZy/WXInlinePlayer/HEAD/src/index.js>
  - <https://raw.githubusercontent.com/ErosZy/WXInlinePlayer/HEAD/src/processor/processor.js>
  - <https://raw.githubusercontent.com/ErosZy/WXInlinePlayer/HEAD/src/drawer/drawer.js>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/eroszy/wxinlineplayer`) · [data/wave13/enrich/raw/github_com_eroszy_wxinlineplayer.json](../../../data/wave13/enrich/raw/github_com_eroszy_wxinlineplayer.json) (enrichment confidence 0.4)

</details>
