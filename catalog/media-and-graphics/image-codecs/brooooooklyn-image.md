# @napi-rs/image

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟢 active

> Rust napi-rs addon for Node.js image resize and WebP/AVIF/JPEG/PNG encoding; edges out sharp on small-thumbnail throughput.

| | |
|---|---|
| **Beats** | sharp (Node.js binding over libvips with libwebp and libavif) |
| **Claimed result** | Default thread pool: WebP 202 ops/s vs sharp 169 ops/s, AVIF 26 vs 24 ops/s. UV_THREADPOOL_SIZE=10: WebP 431 vs 238 ops/s (README: 'The 1.8x ratio applies only to the recorded WebP pipeline with a thread pool of 10'), AVIF 36 vs 32 ops/s. |
| **Workload** | bench/bench.mjs: one EXIF JPEG (with-exif.jpg, exif-samples portrait_5.jpg) is rotated by its EXIF orientation, resized to width 225 with the image crate's Lanczos3 resize, and encoded to WebP (quality 75) or AVIF (quality 70, 4:2:0). Up to 10,000 iterations or 20 s are submitted concurrently up to the CPU count, and throughput is iterations over wall time. sharp runs the same chain, ending in .toBuffer(). |
| **Metric** | throughput |
| **Hardware** | Apple M1 Max, macOS 12.3.1, arm64 |
| **Compiler and flags** | node bench/bench.mjs (benchmark script in the repo); Node.js and package versions were not recorded with the results. |
| **Adoption** | 417 stars |
| **Last commit** | 2026-09-30 |
| **Links** | [repository](https://github.com/Brooooooklyn/Image) · [benchmark](https://raw.githubusercontent.com/Brooooooklyn/Image/HEAD/README.md) |

## Verdict

bench/bench.mjs, run in April 2022 on an Apple M1 Max (macOS 12.3.1) with @napi-rs/image 1.1.0 and sharp 0.30.3, rotated, Lanczos3-resized and encoded one small JPEG: WebP 202 vs 169 ops/s and AVIF 26 vs 24 ops/s with the default libuv pool, and 431 vs 238 and 36 vs 32 ops/s with UV_THREADPOOL_SIZE=10 (1.08x to 1.81x, derived from page data). Node version, compiler and flags were not recorded; both sides encode with libwebp and libaom, so the gap is decode, resize and job scheduling, not a faster encoder.

## Use it when

- Node.js servers or build scripts that turn many small JPEGs into WebP or AVIF thumbnails and can raise UV_THREADPOOL_SIZE to the core count (the recorded 1.8x is WebP at UV_THREADPOOL_SIZE=10).
- You want one npm package with prebuilt binaries for macOS, Windows (x64, arm64, ia32), Linux glibc and musl, Android arm64 and FreeBSD, with no system libvips.
- In-browser processing through @napi-rs/image-wasm32-wasi when you can serve COOP/COEP headers for cross-origin isolation.
- Combined resize plus PNG/JPEG size optimization in one dependency (oxipng, palette quantization, mozjpeg re-encode).
- HEIC decode or encode on macOS or Windows through the OS codecs (ImageIO, WIC).

## Skip it when

- Large images or memory-tight services: every job decodes the whole image into memory and clones it before transforms, with no tiled streaming or JPEG shrink-on-load in the binding's decode path.
- Animated images (no animation pipeline; GIF, OpenEXR and farbfeld are disabled in the published build) or HEIC on Linux, Android, FreeBSD or WASM.
- With the default libuv pool of 4 threads the recorded edge is only 1.20x for WebP and 1.08x for AVIF (derived from page data), within what different encoder settings or images could erase.
- Long-running processes that call `Transformer.fromRgbaPixels(...).png()` in a loop: open issue #128 (v1.4.0, macOS 15.4.1, Node 23.11.0) reports about 16.8 MB retained per call even after GC.
- Migrations that need sharp's exact output: equal numeric quality does not give equal visual quality, and the defaults differ (here WebP quality 90, AVIF quality 80 at 4:4:4).

## How it is fast

There is no new codec: each job is one libuv task that decodes with the Rust image crate, runs the image crate's separable Lanczos3 resize, then calls libwebp's simple API (WebPEncodeRGB/RGBA, default method) or libavif with libaom (speed 5, libaom threads set to the core count). The measured edge over sharp comes from low per-call overhead on tiny images and from running many independent jobs side by side when UV_THREADPOOL_SIZE is raised, while sharp runs each job as its own multi-threaded libvips pipeline. Release builds use fat LTO with codegen-units=1, CI enables mozjpeg's NASM SIMD (`with_simd`), libwebp is compiled with its SSE4.1/AVX2/NEON paths, and a separate `fastResize` method uses the SIMD fast_image_resize crate, which the benchmark does not call.

## Compared with alternatives

The catalogued siblings are codecs (libjpeg-turbo, zenjpeg, wpd, fpng, oxipng, mozjpeg-rs); pick @napi-rs/image when you are in Node.js and want one prebuilt package for resize plus WebP/AVIF encode plus PNG/JPEG optimization. Pick the codec siblings when you own a native pipeline and need codec-level speed, since this package reuses libwebp, libaom, mozjpeg and oxipng rather than beating them.

## Integration

| | |
|---|---|
| **Form** | Prebuilt Node-API native addon on npm (Rust cdylib, one optional-dependency package per platform) plus a separate WASM package |
| **Dependencies** | None at runtime beyond Node.js; statically bundles the image crate 0.25, libwebp (libwebp-sys 0.14), libavif 0.14 with libaom, mozjpeg-sys 2, oxipng 10, fast_image_resize 6, resvg 0.48 and lodepng 3; HEIC needs the OS codec (ImageIO on macOS, HEIF/HEVC extensions for WIC on Windows) |
| **Minimum toolchain** | Node-API 3 (package.json engines: node &gt;= 10; the README asks for a current Node.js LTS); building from source needs Rust with edition 2024 and @napi-rs/cli 3 |
| **Platforms** | macOS x64/arm64; Windows x64/arm64/ia32; Linux glibc x64/arm64/armv7; Linux musl x64/arm64; Android arm64; FreeBSD x64; wasm32-wasip1-threads |
| **Thread safety** | Async methods run on the libuv thread pool and \*Sync methods block the JS thread. A Transformer caches its decoded image behind a raw pointer marked Send and Sync with no lock (ThreadsafeDynamicImage::get hands out &mut from &self), so concurrent async encodes on one Transformer are not documented as safe; use one Transformer per job, as the benchmark does. |
| **Drop-in for the baseline** | no |

## Gotchas

- The README table is from commit a09b74d (April 2022): @napi-rs/image 1.1.0 built on image 0.24 with jpeg-decoder 0.2 (jpeg_rayon), libwebp-sys 0.6 and a libavif-rs 0.10 fork, against sharp 0.30.3 per that commit's yarn.lock. The current 1.15.0 decodes JPEG with zune-jpeg through image 0.25 and has not been re-measured.
- The benchmark input is a single 600x450 4:2:0 JPEG with EXIF orientation 5, resized to 225x300, so per-call overhead and scheduling dominate; output sizes and quality are not compared, and AVIF also oversubscribes the CPU (up to core-count parallel jobs, each with libaom threads set to the core count).
- x86_64 Linux and Windows builds enable libwebp-sys's avx2 and sse41 features, which compile the vendored libwebp with -mavx2 -msse4.1 (libwebp-sys build.rs). Issue #165 reported 'Illegal instruction' on older Xeons from v1.10.0; it is closed and .cargo/config.toml now drops +avx2 rustflags for the quantizer, but whether the libwebp path is safe on pre-AVX2 CPUs is not documented.
- Releases around 1.1.0 linked imagequant 4.0.0, which is GPL-3.0-or-later; the current Cargo.toml no longer depends on imagequant, so pin a recent version if license matters.

## Known shortcomings

- Node binding over the image crate (zune-jpeg decode, Lanczos3 resize), libwebp and libavif/libaom, the same encoders sharp uses, so the gain is pipeline and concurrency rather than codec speed. Historical M1 Max run with Node and sharp versions unknown; prebuilt binary with no compiler or flags.
- The README table is from commit a09b74d (April 2022): @napi-rs/image 1.1.0 (image 0.24 with jpeg-decoder 0.2 jpeg_rayon, libwebp-sys 0.6, a libavif-rs 0.10 fork) against sharp 0.30.3 per yarn.lock, so the verifier's zune-jpeg caveat describes current code, not the measured build; the input is one 600x450 JPEG resized to 225x300 (overhead-dominated) and the run was never repeated. ThreadsafeDynamicImage is Send and Sync with no lock (concurrent async encodes on one Transformer are unsafe); x86_64 libwebp is built -mavx2 -msse4.1 (issue #165 SIGILL, closed); open leak #128; old releases linked the GPL imagequant 4.0.0.

## Caveats and trade-offs

A Node.js binding (napi-rs) over Rust and C codec libraries, not a codec of its own. In the benchmarked pipeline, JPEG decode (zune-jpeg) and the Lanczos3 resize run in the image crate 0.25. The bench calls resize, not the fast_image_resize path. WebP encode is libwebp via libwebp-sys (WebPEncodeRGB/RGBA), and AVIF encode is libavif with libaom (speed 5). sharp uses the same libwebp and libaom through libvips and libheif, so the measured 1.08x to 1.8x reflects decode, resize and scheduling differences, not a faster encoder. fast_image_resize and oxipng (both catalogued) are bound but not exercised by this bench. The table was recorded on macOS 12.3.1 (2022 era). The repo now pins sharp ^0.35.2 as a devDependency, but the sharp, Node and @napi-rs/image versions behind the numbers are unknown. The bench uses a single input image and makes no output-size or quality comparison; the README notes that equal numeric quality does not mean equal visual quality. The 1.8x applies only to WebP with UV_THREADPOOL_SIZE=10. The default-pool WebP row is 1.20x and the AVIF rows are 1.08x and 1.13x (derived from page data). The baseline sharp is itself recorded as a duplicate of libvips; libwebp and libavif are not compared directly.

Rust native addon for Node.js (plus a WebAssembly build) that resizes, converts and optimizes JPEG, PNG, WebP, AVIF; HEIC not available in WASM. API differs from sharp. It is a Node.js packaging of native image codecs rather than a new codec design (README: Rust-powered image processing), so it may fold into the libwebp/libavif entries.

## Maintenance

Actively maintained (release 1.15.0, last commit 2026-09-30, 417 stars, 4 open issues) and MIT-licensed with prebuilt binaries, but the performance table has not been re-run since 2022.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party evidence. bench/bench.mjs is public and the CPU is named (Apple M1 Max, macOS 12.3.1). The addon is a prebuilt binary with no compiler or flags, the Node, sharp and package versions were not recorded, and the README itself calls the table historical rather than a benchmark of 1.15.0.
- **Verifier notes:** Numbers match the README table exactly. Not folded as a duplicate: the benchmarked work runs in the image crate, libwebp and libaom, none of which is catalogued (only zune-image's workspace is), though the orchestrator may still treat it as a wrapper like @napi-rs/canvas. The encoders are the same C libraries sharp uses, so this is pipeline and concurrency evidence, not a faster codec. Metadata checked: MIT, 417 stars, last commit 2026-09-30, not a fork.
- **Fields the verifier corrected:** `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/Brooooooklyn/Image/HEAD/README.md>
  - <https://raw.githubusercontent.com/Brooooooklyn/Image/HEAD/bench/bench.mjs>
  - <https://raw.githubusercontent.com/Brooooooklyn/Image/HEAD/packages/binding/Cargo.toml>
  - <https://raw.githubusercontent.com/Brooooooklyn/Image/HEAD/packages/binding/src/transformer.rs>
  - <https://raw.githubusercontent.com/Brooooooklyn/Image/HEAD/packages/binding/src/webp.rs>
  - <https://raw.githubusercontent.com/Brooooooklyn/Image/HEAD/packages/binding/src/avif.rs>
  - <https://raw.githubusercontent.com/Brooooooklyn/Image/HEAD/package.json>
  - <https://raw.githubusercontent.com/Brooooooklyn/Image/HEAD/packages/binding/package.json>
  - <https://raw.githubusercontent.com/Brooooooklyn/Image/HEAD/LICENSE>
  - <https://github.com/Brooooooklyn/Image>
  - <https://github.com/Brooooooklyn/Image/commits>
  - <https://github.com/Brooooooklyn/Image/tree/main/packages/binding/src>
- **Sources the enricher read:**
  - <https://github.com/Brooooooklyn/Image>
  - <https://raw.githubusercontent.com/Brooooooklyn/Image/HEAD/README.md>
  - <https://raw.githubusercontent.com/Brooooooklyn/Image/HEAD/bench/bench.mjs>
  - <https://raw.githubusercontent.com/Brooooooklyn/Image/HEAD/with-exif.jpg>
  - <https://raw.githubusercontent.com/Brooooooklyn/Image/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/Brooooooklyn/Image/HEAD/packages/binding/Cargo.toml>
  - <https://raw.githubusercontent.com/Brooooooklyn/Image/HEAD/packages/binding/src/transformer.rs>
  - <https://raw.githubusercontent.com/Brooooooklyn/Image/HEAD/packages/binding/src/webp.rs>
  - <https://raw.githubusercontent.com/Brooooooklyn/Image/HEAD/packages/binding/src/avif.rs>
  - <https://raw.githubusercontent.com/Brooooooklyn/Image/HEAD/packages/binding/README.md>
  - <https://raw.githubusercontent.com/Brooooooklyn/Image/HEAD/package.json>
  - <https://raw.githubusercontent.com/Brooooooklyn/Image/HEAD/packages/binding/package.json>
  - <https://raw.githubusercontent.com/Brooooooklyn/Image/HEAD/.cargo/config.toml>
  - <https://raw.githubusercontent.com/Brooooooklyn/Image/HEAD/.github/workflows/CI.yml>
  - <https://github.com/Brooooooklyn/Image/commits/main/bench/bench.mjs>
  - <https://raw.githubusercontent.com/Brooooooklyn/Image/a09b74d/README.md>
  - <https://raw.githubusercontent.com/Brooooooklyn/Image/a09b74d/bench/bench.mjs>
  - <https://raw.githubusercontent.com/Brooooooklyn/Image/a09b74d/package.json>
  - <https://raw.githubusercontent.com/Brooooooklyn/Image/a09b74d/yarn.lock>
  - <https://raw.githubusercontent.com/Brooooooklyn/Image/a09b74d/packages/binding/package.json>
  - <https://raw.githubusercontent.com/Brooooooklyn/Image/a09b74d/packages/binding/Cargo.toml>
  - <https://raw.githubusercontent.com/Brooooooklyn/Image/a09b74d/packages/binding/src/avif.rs>
  - <https://raw.githubusercontent.com/Brooooooklyn/Image/7cd00d4/packages/binding/Cargo.toml>
  - <https://github.com/Brooooooklyn/Image/issues?q=is%3Aissue+performance+OR+slow+OR+memory+OR+leak+OR+crash>
  - <https://github.com/Brooooooklyn/Image/issues/128>
  - <https://github.com/Brooooooklyn/Image/issues/165>
  - <https://github.com/Brooooooklyn/Image/pulls?q=is%3Apr+avx2>
  - <https://raw.githubusercontent.com/NoXF/libwebp-sys/master/build.rs>
  - <https://crates.io/api/v1/crates/imagequant/4.0.0>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/brooooooklyn/image`) · [data/wave10/enrich/raw/github_com_brooooooklyn_image.json](../../../data/wave10/enrich/raw/github_com_brooooooklyn_image.json) (enrichment confidence 0.75)

</details>
