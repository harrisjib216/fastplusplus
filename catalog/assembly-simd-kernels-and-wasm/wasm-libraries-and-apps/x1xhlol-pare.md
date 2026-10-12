# Pare

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly libraries and apps](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C (x264, SVT-AV1, libvmaf) compiled to WebAssembly SIMD128 with Emscripten, TypeScript web app` · `GPL-2.0-or-later` · 🟢 active

> In-browser video compressor: x264 with \~1,500 lines of WebAssembly SIMD128 kernels, 1.7-6.4x faster than ffmpeg.wasm end to end.

| | |
|---|---|
| **Beats** | ffmpeg.wasm 0.12 (x264 built without its assembly) single-threaded and multithreaded; native x264 as the ceiling |
| **Claimed result** | BENCHMARKS.md 'Speed in context' (Big Buck Bunny, 10 s, 30.7 MB): Pare 24.9 s from the click, including the size plan and Auto's test encodes (13.4 MB, VMAF NEG 93.1, worst frame 88.9), vs ffmpeg.wasm 0.12 single-threaded x264 `faster` CRF 19 158.9 s and multithreaded 42.4 s (both 12.2 MB, VMAF NEG 93.0, worst frame 89.8): 6.4x and 1.7x as fast per the page; native ffmpeg x264 with Pare's settings 6.4 s. Pare's encode alone took 12.9 s, about twice native x264 on the same cores. README/RESEARCH.md: about 1,500 lines of WebAssembly SIMD128 kernels make encoding 2.0-2.3x faster per core than the plain C build with byte-identical output, and the single-thread WebAssembly build runs at 54% of native x264 with the same settings (4.25 vs 7.85 fps on park). |
| **Workload** | Compress Big Buck Bunny (10 s, 30.7 MB) to at least 50% smaller at matching VMAF NEG in headless Chrome, including the size plan and test encodes, on a 4-core 8-thread cloud VM. |
| **Metric** | latency |
| **Hardware** | Xeon Platinum 8259CL 2.5 GHz (2019), 4 cores / 8 threads cloud VM shared with other work, no GPU |
| **Compiler and flags** | emcc -O3 -msimd128 (x264 configured with --extra-cflags=-O3; the threaded build adds -pthread), x264-wasm/build.sh; Emscripten version not pinned; browser is Playwright's Chromium build 1243 (playwright-core 1.63.0, research/benchmark.mjs); baseline ffmpeg.wasm is @ffmpeg/core and @ffmpeg/core-mt 0.12.10 with @ffmpeg/ffmpeg 0.12.15 (research/ffmpeg-wasm/package.json) |
| **Adoption** | 3 stars |
| **Last commit** | 2026-09-28 |
| **Links** | [repository](https://github.com/x1xhlol/pare) · [benchmark](https://github.com/x1xhlol/pare/blob/main/research/BENCHMARKS.md) |

## Verdict

On a shared 4-core/8-thread Xeon Platinum 8259CL VM in Playwright's headless Chromium (build 1243), Pare compressed a 10 s 1080p Big Buck Bunny clip (30.7 MB) in 24.9 s from the click, size plan and Auto's test encodes included, to 13.4 MB at VMAF NEG 93.1; stock ffmpeg.wasm 0.12.10 (x264 without assembly, handed 'faster' CRF 19, timed from exec after loading) took 158.9 s single-threaded and 42.4 s multithreaded for a 12.2 MB file at 93.0 (6.4x and 1.7x), and native ffmpeg with Pare's x264 settings took 6.4 s. Separately the author reports 2.0-2.3x per core for the SIMD128 kernels over the plain-C WebAssembly build with byte-identical output, and 54% of native x264 single-threaded (4.25 vs 7.85 fps on park), one run per row.

## Use it when

- Client-side H.264 or AV1 re-encoding in a web page where the file must not leave the device and ffmpeg.wasm is the current option.
- Building your own browser encoder: reuse the x264 SIMD128 patch series and the C binding instead of ffmpeg.wasm's assembly-less libx264 (an encoder module of about 830 KB against 32 MB).
- Size-targeted delivery ('at least 50% smaller' or 'under N MB') where a measured per-frame quality report matters.
- Multi-core desktops and laptops in Chrome on a cross-origin-isolated page (COOP/COEP), so the threaded build runs; time scales almost linearly with cores (Big Buck Bunny 46.4 s on 2 cores/4 threads against 23.9 s on 4/8).

## Skip it when

- Server-side or desktop encoding: native ffmpeg with Pare's x264 settings did the Big Buck Bunny clip in 6.4 s against Pare's 24.9 s (Pare's encode alone 12.9 s, about twice native); the single-thread WebAssembly build runs at 54% of native x264.
- When you need ffmpeg's general toolbox (filters, arbitrary containers and codecs, CLI arguments): Pare only encodes H.264 or AV1 through its own pipeline.
- Smallest file at a given quality on short clips: chunking costs 4-9% of the bytes, stock ffmpeg.wasm 'faster' CRF 19 made a 9% smaller Big Buck Bunny file at the same VMAF NEG, and Auto keeps H.264 there although AV1 needed 0.55x the bytes.
- Closed-source products: GPL-2.0-or-later (from x264) obliges offering the corresponding source to users, and x264's H.264 patent notes apply.
- Browsers without WebCodecs or WebAssembly SIMD128, pages that cannot be cross-origin isolated (each encoder then runs one thread), Safari on macOS (untested), memory-tight devices (about 400 MB per 1080p encoder), or anyone needing a mature dependency (3 stars, first commits late September 2026, one author, no releases).

## How it is fast

It replaces x264's x86/ARM assembly, which a browser cannot run, with WebAssembly SIMD128 intrinsics for SAD/SATD/SA8D motion-search costs, sub-pel interpolation and averaging, 4x4/8x8 DCT and IDCT, quantization, deblocking, SSIM and weighted prediction, each checked bit-exact against the C code with x264's checkasm; the author reports 2.0-2.3x per core over the plain-C WebAssembly build. Around the encoder, decoding moves to WebCodecs (the browser's native decoder, hardware where present), the video is split into equal-cost chunks encoded in parallel by one Web Worker per core with two x264 frame threads each, late chunks are cut and handed to idle encoders, and the shipped x264 settings (faster plus 40-frame lookahead and weightp 2, with diamond motion search, no 8x8-and-smaller inter partitions and 2 references) take about two thirds of the CPU time of its earlier setting at equal average BD-rate.

## Compared with alternatives

The closest siblings are TurboRes (ProRes encoding in WebAssembly, also measured against ffmpeg.wasm) and WXInlinePlayer (in-browser H.264/H.265 playback); pick Pare, or its x264 and SVT-AV1 SIMD128 builds, when the job is size-targeted H.264 or AV1 encoding in the browser rather than ProRes mastering or playback.

## Integration

| | |
|---|---|
| **Form** | module (Emscripten ES module plus .wasm inside a Vite/React web app; the x264 changes are a 7-patch source series) |
| **Dependencies** | x264 at pinned commit 0480cb05fa188d37ae87e8f4fd8f1aea3711f7ee plus the patches; SVT-AV1 and libvmaf in their own WebAssembly builds; mediabunny 1.59.1 (patched) and React 19 for the app |
| **Minimum toolchain** | Emscripten SDK (version not pinned) with -O3 -msimd128 (-pthread for the threaded build), Bun and Node to build and run the app; at runtime a browser with WebAssembly SIMD128 and WebCodecs, plus SharedArrayBuffer and COOP/COEP headers for threads |
| **Platforms** | Browsers: Chrome tested (Linux benchmark machine); Firefox 155 and WebKit 26.6 on Linux work with caveats (WebKit plans about 3x slower and cannot decode AV1; Firefox converts HDR to SDR); Safari on macOS untested; installable as a PWA on Android and desktop |
| **Thread safety** | One encoder instance per Web Worker; the threaded build runs x264 frame threads as Web Workers sharing the module's memory and needs a cross-origin-isolated page; thread safety of the C binding itself is not documented |
| **Drop-in for the baseline** | partial — the x264 module can replace ffmpeg.wasm's libx264 encode step, but you supply decoding (WebCodecs), muxing (e.g. Mediabunny) and calls to the enc_\* C API instead of ffmpeg command lines |

## Gotchas

- Harness asymmetry behind 6.4x/1.7x: research/ffmpeg-wasm/index.html starts its timer after ff.load() and writeFile, so ffmpeg.wasm's 32 MB core download and compile are excluded, and it times exec only; inside that, ffmpeg.wasm decodes H.264 in WebAssembly without ffmpeg's assembly, while Pare decodes with Chrome's native WebCodecs decoder, runs 4 chunk encoders with 2 threads each, uses cheaper x264 settings, and pays for its own size plan and test encodes (11.5 s of the Big Buck Bunny time in an earlier log). The comparison is whole-pipeline; only the 2.0-2.3x per-core figure isolates the SIMD kernels, and it is a sentence in RESEARCH.md without a per-kernel or per-clip table.
- 'Same quality' is not same bytes: ffmpeg.wasm's file was 12.2 MB against Pare's 13.4 MB at VMAF NEG 93.0 against 93.1, with a better worst frame (89.8 against 88.9); RESEARCH.md shows the shipped x264 settings cost animation 6.2% BD-rate and chunking costs 4-9%.
- Numbers move between builds and runs: the README's Big Buck Bunny row (14.3 MB, 24 s, VMAF NEG 93.3, worst 89.5, from the 2026-09-28 build) differs from the BENCHMARKS.md speed comparison (13.4 MB, 24.9 s, 93.1, worst 88.9); every row is one run on a shared VM where identical encodes varied by up to 25 s; the native reference is the unpinned ffmpeg-master-latest-linux64-gpl build and Emscripten is unpinned. benchmark.mjs clicks Compress 1 s after the file loads, and Pare starts planning while the settings are on screen, so up to about a second of planning can precede the timer.
- The patched x264_cpu_detect returns SIMD128 unconditionally and the module is built with -msimd128, so no scalar fallback module ships; the x264 build is 8-bit only, so HDR sent to H.264 loses two bits (AV1 keeps 10-bit).

## Known shortcomings

- Borderline A (emcc -O3 -msimd128 in build.sh, Xeon 8259CL, Playwright Chromium 1243, Emscripten version unpinned): the 6.4x/1.7x over ffmpeg.wasm is a whole-pipeline comparison (chunking, WebCodecs decode, cheaper x264 settings); the ffmpeg.wasm file is 9% smaller at the same VMAF NEG; shared noisy VM.
- Harness asymmetry behind the 6.4x/1.7x: research/ffmpeg-wasm/index.html starts its timer after ff.load() and writeFile, and inside that window ffmpeg.wasm decodes in WebAssembly while Pare decodes with native WebCodecs, runs 4 chunk workers with 2 threads each and uses cheaper x264 settings; ffmpeg.wasm's file is 9% smaller at the same VMAF NEG. The 2.0-2.3x per-core kernel claim has no table, the README BBB row (14.3 MB) disagrees with BENCHMARKS.md (13.4 MB), native ffmpeg and Emscripten versions are unpinned, and up to about 1 s of planning can run before Pare's timer. First-party and days old.

## Caveats and trade-offs

First-party and very new (94 commits, first in late September 2026, 3 stars). The headline 6.4x/1.7x over ffmpeg.wasm is a whole-pipeline comparison, not a kernel one: Pare adds chunked multi-worker encoding, WebCodecs decoding and its own x264 settings (diamond motion search and no 8x8-and-smaller inter partitions, about two thirds of the CPU time of the `faster`-based setting), while ffmpeg.wasm ran stock `faster` CRF 19; ffmpeg.wasm also produced a smaller file (12.2 MB vs 13.4 MB) at the same VMAF NEG with a better worst frame, and Pare's time includes finding its own rate factor. The cleanest kernel claim (2.0-2.3x per core over scalar C WebAssembly) is a sentence in RESEARCH.md without a per-kernel table. One run per row on a 4-core cloud VM shared with other work (the page reports up to 25 s variation between identical encodes in a busy session). Emscripten version unpinned. ffmpeg/ffmpeg is already catalogued; x264 itself was not in the known list. [retier] First-party and very new (94 commits, first in late September 2026, 3 stars). The headline 6.4x/1.7x over ffmpeg.wasm is a whole-pipeline comparison with asymmetric work: research/ffmpeg-wasm/index.html starts its timer after ff.load() and writeFile, and within that window ffmpeg.wasm decodes H.264 in WebAssembly without ffmpeg's assembly and encodes with stock x264 'faster' CRF 19, while Pare decodes with Chrome's native WebCodecs decoder, runs 4 chunk encoders with 2 threads each and uses cheaper x264 settings (diamond motion search, no small inter partitions), with up to about 1 s of planning before its timer; ffmpeg.wasm also produced a 9% smaller file (12.2 MB vs 13.4 MB) at the same VMAF NEG. The 2.0-2.3x per-core kernel claim has no table; the README BBB row (14.3 MB) and BENCHMARKS.md (13.4 MB) disagree; native ffmpeg and Emscripten versions are unpinned.

GPL because of x264; needs WebAssembly SIMD128 and Web Workers; chunked parallel encoding costs 4-9% more bytes than a single encode; the app picks its own rate factor to hit a size target; 

## Maintenance

Active single-author project (94 commits, all from late September 2026, last 2026-09-28; 3 stars, no releases, no issues), GPL-2.0-or-later: usable as a hosted app or as a source of the x264 SIMD128 patch series, but too new to treat as a stable dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now C.
- **Tier reason:** research/BENCHMARKS.md 'Speed in context' times Pare against ffmpeg.wasm 0.12 (single-threaded and multithreaded) and native ffmpeg x264 on Big Buck Bunny, using public scripts (research/benchmark.mjs, research/score.py, research/ffmpeg-wasm/run.mjs with @ffmpeg/core 0.12.10). Compiler and flags are in x264-wasm/build.sh (emcc -O3 -msimd128, x264 --extra-cflags=-O3), the CPU is named (Xeon Platinum 8259CL, 4 cores/8 threads) and the browser is pinned to Playwright Chromium build 1243; only the Emscripten version is unpinned, so A holds, borderline.
- **Retiered** A to C: Enricher: the 6.4x/1.7x is a whole-pipeline comparison with asymmetric work (native WebCodecs decode, 4x2 worker threads and cheaper x264 settings against ffmpeg.wasm decoding in WebAssembly with stock 'faster'), and the first-party research harness starts its timer after ff.load() and writeFile; the per-core kernel claim has no table and the toolchain is unpinned. Asymmetric-harness precedent (LC, TensorFlow DLPerf): A to C.
- **Verifier notes:** All claimed numbers appear verbatim in research/BENCHMARKS.md and README; repo metadata confirmed (GPL-2.0-or-later per README, LICENSE is GPL v2 text, 3 stars, 94 commits, latest commit 2026-09-28, not a fork). Main shortcoming: the ffmpeg.wasm gap mixes SIMD kernels with parallel chunking, browser decoding and cheaper encoder settings, and ffmpeg.wasm's output was 9% smaller at equal VMAF NEG; times come from a shared, noisy VM.
- **Fields the verifier corrected:** `compiler_and_flags`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-21 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/x1xhlol/pare>
  - <https://github.com/x1xhlol/pare/commits/main>
  - <https://github.com/x1xhlol/pare/tree/main/research>
  - <https://raw.githubusercontent.com/x1xhlol/pare/HEAD/README.md>
  - <https://raw.githubusercontent.com/x1xhlol/pare/HEAD/research/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/x1xhlol/pare/HEAD/research/RESEARCH.md>
  - <https://raw.githubusercontent.com/x1xhlol/pare/HEAD/research/benchmark.mjs>
  - <https://raw.githubusercontent.com/x1xhlol/pare/HEAD/research/ffmpeg-wasm/package.json>
  - <https://raw.githubusercontent.com/x1xhlol/pare/HEAD/research/ffmpeg-wasm/run.mjs>
  - <https://raw.githubusercontent.com/x1xhlol/pare/HEAD/x264-wasm/build.sh>
  - <https://raw.githubusercontent.com/x1xhlol/pare/HEAD/package.json>
  - <https://raw.githubusercontent.com/x1xhlol/pare/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/x1xhlol/pare>
  - <https://github.com/x1xhlol/pare/commits/main>
  - <https://github.com/x1xhlol/pare/issues?q=is%3Aissue>
  - <https://github.com/x1xhlol/pare/tree/main/research>
  - <https://github.com/x1xhlol/pare/tree/main/research/ffmpeg-wasm>
  - <https://github.com/x1xhlol/pare/tree/main/x264-wasm/patches>
  - <https://raw.githubusercontent.com/x1xhlol/pare/HEAD/README.md>
  - <https://raw.githubusercontent.com/x1xhlol/pare/HEAD/research/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/x1xhlol/pare/HEAD/research/RESEARCH.md>
  - <https://raw.githubusercontent.com/x1xhlol/pare/HEAD/research/benchmark.mjs>
  - <https://raw.githubusercontent.com/x1xhlol/pare/HEAD/research/score.py>
  - <https://raw.githubusercontent.com/x1xhlol/pare/HEAD/research/wasm-bench.mjs>
  - <https://raw.githubusercontent.com/x1xhlol/pare/HEAD/research/results.jsonl>
  - <https://raw.githubusercontent.com/x1xhlol/pare/HEAD/research/ffmpeg-wasm/run.mjs>
  - <https://raw.githubusercontent.com/x1xhlol/pare/HEAD/research/ffmpeg-wasm/index.html>
  - <https://raw.githubusercontent.com/x1xhlol/pare/HEAD/research/ffmpeg-wasm/serve.ts>
  - <https://raw.githubusercontent.com/x1xhlol/pare/HEAD/research/ffmpeg-wasm/package.json>
  - <https://raw.githubusercontent.com/x1xhlol/pare/HEAD/x264-wasm/build.sh>
  - <https://raw.githubusercontent.com/x1xhlol/pare/HEAD/x264-wasm/X264_COMMIT>
  - <https://raw.githubusercontent.com/x1xhlol/pare/HEAD/x264-wasm/pare_x264.c>
  - <https://raw.githubusercontent.com/x1xhlol/pare/HEAD/x264-wasm/patches/0001-Return-void-from-all-thread-pool-jobs.patch>
  - <https://raw.githubusercontent.com/x1xhlol/pare/HEAD/x264-wasm/patches/0002-wasm-Add-compile-support.patch>
  - <https://raw.githubusercontent.com/x1xhlol/pare/HEAD/x264-wasm/patches/0003-wasm-Add-SIMD128-pixel-functions.patch>
  - <https://raw.githubusercontent.com/x1xhlol/pare/HEAD/x264-wasm/patches/0006-wasm-Add-SIMD128-quant-functions.patch>
  - <https://raw.githubusercontent.com/x1xhlol/pare/HEAD/package.json>
  - <https://raw.githubusercontent.com/x1xhlol/pare/HEAD/LICENSE>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/x1xhlol/pare`) · [data/wave13/enrich/raw/github_com_x1xhlol_pare.json](../../../data/wave13/enrich/raw/github_com_x1xhlol_pare.json) (enrichment confidence 0.75)

</details>
