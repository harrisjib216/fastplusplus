# av-denoise

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Video and audio](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0` · 🟢 active

> Rust GPU video denoiser (NLMeans, NLMeans-HQ, NL4D on CubeCL); first-party chart shows about 11x FFmpeg nlmeans_opencl at 1080p.

| | |
|---|---|
| **Beats** | FFmpeg libavfilter nlmeans_opencl (OpenCL NLMeans filter) at its defaults s=1, p=7, r=15; not hqdn3d or the CPU nlmeans filter. V-BM3D (vsdenoise, HIP) is a second, VapourSynth-only reference. |
| **Claimed result** | README text: around 2x FFmpeg's nlmeans_opencl at matched settings and about 1.3x faster than V-BM3DHIP. The 1080p 8-bit CLI chart (values read from the bars, approximate) shows av-denoise NLMeans at FFmpeg-matched settings about 116 fps, NLMeans-HQ defaults about 105 fps and NL4D defaults about 79.5 fps against FFmpeg NLMeans OpenCL about 10.6 fps, roughly 11x for the matched arm (derived from page data, chart reading). The 4K 10-bit CLI chart has no FFmpeg bar (ffmpeg's OpenCL NLMeans rejects 10-bit formats, per the config) and shows av-denoise at about 12.5-15.7 fps. In the VapourSynth-plugin charts NL4D is about 29 fps against V-BM3D FAST about 28 fps at 1080p and slightly slower than V-BM3D FAST at 4K (about 6.8 vs 7.6 fps), so the 1.3x V-BM3D claim is not visible in the charts. |
| **Workload** | End-to-end wall-clock throughput (fps = probed frame count / wall time, including startup and scene detection, one repeat after a warmup run) on an unpublished 1080p 8-bit clip and a 4K 10-bit clip, output discarded to /dev/null. FFmpeg arm: ffmpeg decode, format=yuv420p, hwupload, nlmeans_opencl, hwdownload, -f null. av-denoise arm: target/release/av-denoise -A vulkan nlmeans --preset veryfast --strength 1.0 --patch-radius 3 --search-radius 7 --workers 2 (FFMS2 decode, y4m out, luma and chroma planes by default). V-BM3D arms run through vspipe on three profiles. |
| **Metric** | throughput |
| **Hardware** | AMD GPU named RX9700 in the chart file names; host CPU, driver and Vulkan/OpenCL stack not stated |
| **Compiler and flags** | av-denoise built with cargo build --release --bin av-denoise --features vulkan,binary (Justfile _build-benchmark-bin); no custom release profile; rustc version not stated; GPU kernels are JIT-compiled at runtime by CubeCL. FFmpeg build and version not stated. |
| **Adoption** | 14 stars, 1 fork; crates.io av-denoise 0.5.0-alpha3 (395 downloads); VapourSynth plugin on PyPI as vsavd 0.4.1 |
| **Last commit** | 2026-10-03 |
| **Links** | [repository](https://github.com/ChillFish8/av-denoise) · [benchmark](https://github.com/ChillFish8/av-denoise) |

## Verdict

One end-to-end run per arm (repeats = 1 after a warm-up; fps = probed frame count / wall time) on an unpublished 1080p 8-bit clip with an AMD GPU named RX9700. The chart shows av-denoise NLMeans at FFmpeg-matched geometry at about 116 fps against FFmpeg nlmeans_opencl at about 10.6 fps (about 11x, read from the chart), while the README text says about 2x; host CPU, FFmpeg version, driver and rustc are not published. Part of the gap comes from a weak baseline (FFmpeg's serial row and column prefix sums, about 500 launches and a clFinish per frame, single filter chain against two scene workers). KNLMeansCL, the established GPU NLMeans, is not measured, and the V-BM3D claim holds only CLI-to-plugin: through the plugin on both sides NL4D is about 29 fps against V-BM3D FAST at about 28 fps at 1080p, and slower at 4K.

## Use it when

- Cleaning video before an encode on a machine with a GPU, where FFmpeg's nlmeans_opencl, CPU nlmeans or hqdn3d is the throughput bottleneck; the first-party 1080p 8-bit chart shows about 105-116 fps for the NLMeans arms on an AMD GPU named RX9700.
- 10 or 12-bit sources: depth is detected and kept, while FFmpeg's nlmeans_opencl rejects the 10-bit formats its hwupload path offers (per the benchmark config).
- Temporal denoising with motion compensation and automatic per-scene noise estimation (NLMeans-HQ, NL4D), where you would otherwise hand-tune sigma per source in KNLMeansCL or run V-BM3D.
- Cross-vendor GPU fleets: the same build runs on AMD, Intel and NVIDIA through Vulkan and on Apple Silicon through Metal, with no ROCm or CUDA SDK needed on the vulkan backend.
- Rust programs that want an embeddable GPU denoiser with a push/receive frame API.

## Skip it when

- Machines without a usable GPU: there is no software backend (CubeCL's CPU runtime lacks the atomics the collaborative filter needs); a lavapipe-style software Vulkan device is the only CPU fallback.
- C or C++ code, or an FFmpeg filter graph: there is no C API and no libavfilter filter, so integration means a separate process and a y4m pipe.
- Output that must match FFmpeg's nlmeans: the 'matched' arm is not equivalent. av-denoise weights exp(-SSD/(3 s^2 x 49)) over a 7x7 patch while nlmeans_opencl uses exp(-SSD/(10s)^2) over the 6x6 window its integral-image corners cover (derived from both sources), and no PSNR or SSIM comparison is published.
- Search windows wider than radius 8 (17x17) or patches wider than radius 16 (MAX_SEARCH_RADIUS, MAX_PATCH_RADIUS); FFmpeg's r goes up to 99.
- Speed-critical VapourSynth graphs: through the plugin NLMeans-HQ drops from about 105 fps (CLI) to about 35 fps and NL4D from about 80 to about 29 fps at 1080p (chart readings), where NL4D only ties V-BM3D FAST (about 28 fps). It is also an alpha (0.5.0-alpha3, 14 stars, one maintainer) that has shipped backend bugs: green output and crashes on CUDA on an RTX 4080 under Windows (#13), and a motion-compensation alignment error unless frame height was a multiple of 512 (#4), both closed.

## How it is fast

In the spatial pass one fused kernel launch covers the whole search window: patch distance, weight exp(-max(d - noise_offset, 0) \* h2_inv_norm) and accumulation, all in f32 out of a 32x8 shared-memory tile with a halo. CubeCL compiles that kernel at runtime with the search window unrolled ((2r+1)^2 iterations, per the Denoiser::create docs), and the weight's symmetry (pixel p against p+q equals p+q against p) lets each offset's distance serve both pixels. Two scene-parallel workers and two in-flight readbacks keep the GPU busy. The baseline is weak by comparison, derived from FFmpeg's vf_nlmeans_opencl.c and nlmeans.cl: for each group of 4 offsets per plane it launches a horizontal prefix-sum kernel with one work-item per row scanning the row serially, a vertical one with one work-item per column, and a weight-accumulate kernel. That is 56 groups x 3 planes, about 500 kernel launches per frame at its defaults, followed by a clFinish on every frame.

## Compared with alternatives

No other denoiser is catalogued in video-audio; the siblings are codecs, resamplers, RTP stacks and a VAD. av-denoise belongs before an encoder such as SVT-AV1, x265 or VVenC as a pre-encode cleanup step. The comparisons that would matter, KNLMeansCL (which the README names as its inspiration) and the BM3DCUDA/HIP filters, are not catalogued or benchmarked here.

## Integration

| | |
|---|---|
| **Form** | crate (av-denoise on crates.io: library plus the CLI behind the `binary` feature; av-denoise-core holds the kernels), VapourSynth plugin wheel vsavd on PyPI, GHCR container images per backend |
| **Dependencies** | cubecl 0.10 (GPU JIT) with one backend feature: vulkan (default), metal, cuda (needs CUDA headers and nvcc at runtime) or rocm (needs the HIP compiler and headers at runtime); the CLI needs FFMS2 and FFmpeg libraries (optional static build via vcpkg, `static-ffms2`); anyhow, thiserror, tracing, bon, strum, etcetera |
| **Minimum toolchain** | Rust edition 2024 (Rust 1.85+); no rust-version declared; CUDA and ROCm backends need the vendor SDK present at runtime for kernel JIT |
| **Platforms** | GPUs reachable through Vulkan (AMD, Intel, NVIDIA), Metal (Apple Silicon), CUDA or ROCm/HIP on Linux, macOS and Windows; published numbers cover one AMD GPU named RX9700 on the Vulkan backend |
| **Thread safety** | Denoiser methods take &mut self: one stream per instance, at most MAX_PENDING = 2 readbacks in flight (more would reuse an output handle and corrupt frames, per the source). Parallelism comes from scene workers, each with its own denoiser; CubeCL runs codegen on its own per-device thread. |
| **Drop-in for the baseline** | partial — `av-denoise nlmeans --preset veryfast --strength 1.0 --patch-radius 3 --search-radius 7` runs the same spatial NLMeans geometry as nlmeans_opencl's defaults, but as a y4m-in/y4m-out process rather than an FFmpeg filter, and with a different strength normalisation |

## Gotchas

- The first run JIT-compiles the kernels (about 10 s) and caches them on disk under a hash of the kernel source; set AV_DENOISE_COMPILATION_CACHE=off to measure the cold cost. The bundled e2e benchmark runs an untimed warm-up and leaves the cache on, so its timed pass excludes compilation, although the config comment says shader compilation counts.
- When embedding: the windowed NLM kernels unroll (2 x search_radius + 1)^2 times, and a search radius of about 5 or more can overflow the 2 MiB stack of CubeCL's codegen thread and abort the process. Call raise_codegen_stack_limit() at the top of main; the workspace sets RUST_MIN_STACK to 16 MiB for cargo runs.
- --strength is an absolute FFmpeg-style value only in the `fast` variant (preset veryfast). Every other preset picks `hq`, where it multiplies the measured noise level, and the default preset `base` also sets temporal radius 2, search radius 2 and patch radius 4, so the default run is not FFmpeg's geometry.
- The README's '\~2x FFmpeg nlmeans_opencl' and '\~1.3x V-BM3D' lines disagree with its own charts (about 11x and about 1.04x like-for-like through VapourSynth). The charts were committed 2026-09-06, the day 0.4.0 was released, and have not been re-run on later code.

## Known shortcomings

- Rust (language-filter mismatch). Public harness (scripts/src/benchmark_e2e.py, configs/benchmark_e2e.toml) against FFmpeg libavfilter's nlmeans_opencl at defaults (s=1 p=7 r=15; avd arm strength 1.0, patch 3, search 7) on a GPU known only as 'RX9700' from file names; host CPU, rustc, FFmpeg version and clips unpublished, no PSNR or SSIM. The README says about 2x while the chart shows about 11x (116 vs 10.6 fps), and the charts do not show the claimed 1.3x over V-BM3D (ties V-BM3D FAST at 1080p, trails it at 4K).
- Weak baseline: FFmpeg's nlmeans_opencl does serial row and column prefix sums with about 500 kernel launches plus clFinish per frame. Strength is not matched (exp(-SSD/147) over 7x7 versus exp(-SSD/100) over 6x6); 2 workers against 1 chain, repeats=1, warm kernel cache; charts from 2026-09-06 (0.4.0) and not re-run. The README's 2x and the chart's about 11x are unreconciled; the 1.3x over V-BM3D is not shown like-for-like (plugin NL4D about 29 versus V-BM3D FAST about 28 fps); KNLMeansCL was not measured.

## Caveats and trade-offs

The README text says about 2x at matched settings while the 1080p chart (added 2026-09-06 in commit 'Add benchmark graphics') shows roughly 11x; the two are not reconciled. Quality is not matched by any PSNR or SSIM measurement: the arms share the NLMeans algorithm and parameters, but output equivalence is not checked. The FFmpeg arm pays hwupload/hwdownload copies and runs one filter chain, while av-denoise runs two scene-parallel workers; both include decode and startup in wall time. Test clips, FFmpeg version, host CPU and drivers are unpublished, and the figures are images only. The 1.3x V-BM3D claim is not borne out by the VapourSynth-plugin charts (NL4D roughly ties V-BM3D FAST at 1080p and trails it at 4K). The baseline is a GPU OpenCL filter, not a CPU codec; there is no software backend. Rust crate outside the search's C++ language filter.

GPU-only (CubeCL kernels via ROCm, CUDA, Vulkan or Metal; no software backend); CLI, Rust library and VapourSynth plugin, no C API; kernels compile on first run (about 10 s, cached). NLMeans-HQ and NL4D are limited inside the VapourSynth plugin.

## Maintenance

Active (0.5.0-alpha3 published 2026-10-03, last commit 2026-10-03, 403 crates.io downloads) and Apache-2.0, so it is copyable as a Rust crate, CLI or VapourSynth plugin. It is an alpha with a single maintainer and 14 stars, and has no C/C++ interface.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party bar charts (assets/cli-bench-results-1080p-amd-rx9700.png and siblings) produced by a public harness, scripts/src/benchmark_e2e.py with scripts/configs/benchmark_e2e.toml, which runs ffmpeg's nlmeans_opencl at its defaults (s=1, p=7, r=15) against av-denoise nlmeans at matched strength 1.0, patch radius 3 and search radius 7. It falls short of A because the host CPU, rustc version, FFmpeg version, GPU driver/Vulkan stack and test clips are not published; only the GPU (named RX9700 in the asset file names) is given.
- **Verifier notes:** Real, public harness (scripts/src/benchmark_e2e.py + scripts/configs/benchmark_e2e.toml) with a matched-parameter FFmpeg nlmeans_opencl arm, but first-party, image-only results and missing host/toolchain details keep it at C. Rust crate found on crates.io, which does not fit the C++ language filter; language field set. Last commit 2026-10-03 confirmed on the commits page.
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `workload`, `compiler_and_flags`, `hardware`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/ChillFish8/av-denoise>
  - <https://github.com/ChillFish8/av-denoise/commits>
  - <https://github.com/ChillFish8/av-denoise/tree/main/scripts>
  - <https://github.com/ChillFish8/av-denoise/commits/main/assets/cli-bench-results-1080p-amd-rx9700.png>
  - <https://raw.githubusercontent.com/ChillFish8/av-denoise/HEAD/README.md>
  - <https://raw.githubusercontent.com/ChillFish8/av-denoise/HEAD/assets/cli-bench-results-1080p-amd-rx9700.png>
  - <https://raw.githubusercontent.com/ChillFish8/av-denoise/HEAD/assets/cli-bench-results-4k-amd-rx9700.png>
  - <https://raw.githubusercontent.com/ChillFish8/av-denoise/HEAD/assets/vs-plugin-bench-results-1080p-amd-rx9700.png>
  - <https://raw.githubusercontent.com/ChillFish8/av-denoise/HEAD/assets/vs-plugin-bench-results-4k-amd-rx9700.png>
  - <https://raw.githubusercontent.com/ChillFish8/av-denoise/HEAD/scripts/README.md>
  - <https://raw.githubusercontent.com/ChillFish8/av-denoise/HEAD/scripts/src/benchmark_e2e.py>
  - <https://raw.githubusercontent.com/ChillFish8/av-denoise/HEAD/scripts/configs/benchmark_e2e.toml>
  - <https://raw.githubusercontent.com/ChillFish8/av-denoise/HEAD/Justfile>
  - <https://raw.githubusercontent.com/ChillFish8/av-denoise/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/ChillFish8/av-denoise/HEAD/.cargo/config.toml>
  - <https://raw.githubusercontent.com/ChillFish8/av-denoise/HEAD/docs/TUTORIAL-CLI.md>
  - <https://raw.githubusercontent.com/ChillFish8/av-denoise/HEAD/docs/CHOOSING_AN_ALGORITHM.md>
  - <https://raw.githubusercontent.com/ChillFish8/av-denoise/HEAD/docs/DONT_DO_THIS.md>
  - <https://crates.io/api/v1/crates/av-denoise>
  - <https://pypi.org/pypi/vsavd/json>
- **Sources the enricher read:**
  - <https://github.com/ChillFish8/av-denoise/issues?q=is%3Aissue>
  - <https://github.com/ChillFish8/av-denoise/issues/13>
  - <https://github.com/ChillFish8/av-denoise/commits/main/README.md>
  - <https://github.com/ChillFish8/av-denoise/commits/main/scripts/src/benchmark_e2e.py>
  - <https://github.com/ChillFish8/av-denoise/commits/main/scripts/configs/benchmark_e2e.toml>
  - <https://github.com/ChillFish8/av-denoise/tree/main/av-denoise-core/src>
  - <https://github.com/ChillFish8/av-denoise/tree/main/av-denoise-core/src/nlmeans>
  - <https://github.com/ChillFish8/av-denoise/tree/main/av-denoise-core/src/nlmeans/kernels>
  - <https://github.com/ChillFish8/av-denoise/tree/main/av-denoise/src>
  - <https://github.com/ChillFish8/av-denoise/tree/main/av-denoise/src/bin>
  - <https://raw.githubusercontent.com/ChillFish8/av-denoise/HEAD/README.md>
  - <https://raw.githubusercontent.com/ChillFish8/av-denoise/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/ChillFish8/av-denoise/HEAD/.cargo/config.toml>
  - <https://raw.githubusercontent.com/ChillFish8/av-denoise/HEAD/Justfile>
  - <https://raw.githubusercontent.com/ChillFish8/av-denoise/HEAD/scripts/README.md>
  - <https://raw.githubusercontent.com/ChillFish8/av-denoise/HEAD/scripts/src/benchmark_e2e.py>
  - <https://raw.githubusercontent.com/ChillFish8/av-denoise/HEAD/scripts/configs/benchmark_e2e.toml>
  - <https://raw.githubusercontent.com/ChillFish8/av-denoise/HEAD/docs/TUTORIAL-CLI.md>
  - <https://raw.githubusercontent.com/ChillFish8/av-denoise/HEAD/docs/CHOOSING_AN_ALGORITHM.md>
  - <https://raw.githubusercontent.com/ChillFish8/av-denoise/HEAD/docs/DONT_DO_THIS.md>
  - <https://raw.githubusercontent.com/ChillFish8/av-denoise/HEAD/assets/cli-bench-results-1080p-amd-rx9700.png>
  - <https://raw.githubusercontent.com/ChillFish8/av-denoise/HEAD/assets/vs-plugin-bench-results-1080p-amd-rx9700.png>
  - <https://raw.githubusercontent.com/ChillFish8/av-denoise/HEAD/av-denoise-core/Cargo.toml>
  - <https://raw.githubusercontent.com/ChillFish8/av-denoise/HEAD/av-denoise-core/src/lib.rs>
  - <https://raw.githubusercontent.com/ChillFish8/av-denoise/HEAD/av-denoise-core/src/denoiser.rs>
  - <https://raw.githubusercontent.com/ChillFish8/av-denoise/HEAD/av-denoise-core/src/nlmeans/mod.rs>
  - <https://raw.githubusercontent.com/ChillFish8/av-denoise/HEAD/av-denoise-core/src/nlmeans/params.rs>
  - <https://raw.githubusercontent.com/ChillFish8/av-denoise/HEAD/av-denoise-core/src/nlmeans/dispatch.rs>
  - <https://raw.githubusercontent.com/ChillFish8/av-denoise/HEAD/av-denoise-core/src/nlmeans/denoiser.rs>
  - <https://raw.githubusercontent.com/ChillFish8/av-denoise/HEAD/av-denoise-core/src/nlmeans/kernels/fused.rs>
  - <https://raw.githubusercontent.com/ChillFish8/av-denoise/HEAD/av-denoise-core/src/nlmeans/kernels/helpers.rs>
  - <https://raw.githubusercontent.com/ChillFish8/av-denoise/HEAD/av-denoise-core/src/nlmeans/kernels/mod.rs>
  - <https://raw.githubusercontent.com/ChillFish8/av-denoise/HEAD/av-denoise/src/bin/main.rs>
  - <https://raw.githubusercontent.com/ChillFish8/av-denoise/HEAD/av-denoise/src/bin/progress.rs>
  - <https://raw.githubusercontent.com/ChillFish8/av-denoise/HEAD/av-denoise/src/bin/warm_start.rs>
  - <https://raw.githubusercontent.com/FFmpeg/FFmpeg/master/libavfilter/vf_nlmeans_opencl.c>
  - <https://raw.githubusercontent.com/FFmpeg/FFmpeg/master/libavfilter/opencl/nlmeans.cl>
  - <https://crates.io/api/v1/crates/av-denoise>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/chillfish8/av-denoise`) · [data/wave10/enrich/raw/github_com_chillfish8_av_denoise.json](../../../data/wave10/enrich/raw/github_com_chillfish8_av_denoise.json) (enrichment confidence 0.7)

</details>
