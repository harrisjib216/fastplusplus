# pngquant / libimagequant

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Color conversion and resampling](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `GPL-3.0-or-later` · 🟢 active

> Lossy PNG palette quantizer (CLI plus libimagequant library); author claims its fast setting is 2.5-6x ImageMagick's quantizer.

| | |
|---|---|
| **Beats** | ImageMagick's built-in colour quantization (an old ImageMagick 6-era version, not stated); no pngnq, Pillow quantize or other baseline numbers were found in the repo |
| **Claimed result** | Snippet only (search-result text, page blocked): a fast-and-rough speed setting 'that is 2.5 to 6 times faster than ImageMagick's current algorithm while still mostly winning in quality'. The search engine attributes this to the 'Use pngquant (libimagequant) for quantization to palette' thread on the legacy ImageMagick forum, the author's proposal to adopt libimagequant in ImageMagick, not to pngquant.org (a site:pngquant.org search returned no ImageMagick comparison). The second figure is a self-comparison from the man page pngquant.1: 'Speed 10 has 5% lower quality, but is about 8 times faster than the default' (the man page says the default is 3; the current CLI help in pngquant.c and the README say the default is 4). |
| **Workload** | Colour quantization of images to an 8-bit palette; the claim compares pngquant's fast-and-rough speed setting with ImageMagick's current quantization algorithm. |
| **Metric** | throughput |
| **Adoption** | 5.8k stars |
| **Last commit** | 2026-06-21 |
| **Links** | [repository](https://github.com/kornelski/pngquant) · [benchmark](https://jqmagick.imagemagick.org/discourse-server/viewtopic.php?t=23340) |

## Verdict

The only comparison with the baseline is first-party and snippet-only: a 'fast and rough' libimagequant setting said to be 2.5 to 6 times faster than ImageMagick's then-current quantizer 'while still mostly winning in quality', from the author's proposal thread on the legacy ImageMagick forum (blocked; no images, versions, settings, compiler or hardware). The repo's own figure, speed 10 being about 8x faster than the default at about 5% lower quality, is a self-comparison, and the repo's bench file (benches/bench.rs) times only libimagequant on a private image (/Users/kornel/Desktop/canvas.png) with no baseline.

## Use it when

- Shrinking PNG assets for the web or apps where 8-bit palette plus full alpha is acceptable (README: often 60-80% smaller than 24/32-bit PNG).
- Real-time palette generation (map tiles, GIF frames) with --speed 10/11 or liq_set_speed(10), where the author says quality drops about 5% for about 8x the speed of the default.
- Batch pipelines that need a quality gate: --quality min-max plus --skip-if-larger rejects images that would degrade too much.
- C or Rust code that needs a palette quantizer with alpha-aware dithering, fixed palette colours, importance maps or remapping onto a background (GIF animation).
- GPL-3.0-or-later projects, or closed-source ones willing to buy the commercial licence.

## Skip it when

- Permissive-licence products that cannot take GPL-3.0-or-later and will not pay for the commercial licence.
- Pure C/C++ toolchains that cannot add Rust: since libimagequant 4 / pngquant 3 the engine is Rust (C ABI kept), so building needs cargo; the C99 code lives only on the unmaintained 2.x branch.
- Pipelines that need bit-identical output across machines: open libimagequant issue #130 shows palettes of 111 vs 120 colours for the same image on x86_64 and aarch64 at speeds 1-7, and dithered remapping splits large images into chunks by core count (see gotchas).
- When you need a quality or speed comparison against ImageMagick, Pillow or libvips you can trust: none is published in either repo, and open issue #424 reports desaturated colours from pngquant --nofs where ImageMagick's PNG8 output looked right.
- Images that must keep more than 256 colours, or 16-bit precision: output is 8-bit palette (the large_palettes feature goes to 2048 colours but not for remapping).

## How it is fast

A histogram of 32-bit colours goes into a hash map (posterized to fewer bits at speeds 8-10 or past a million colours), then a variance-driven modified median cut builds the palette, refined by weighted k-means (Voronoi) iterations in a feedback loop. Nearest-colour search uses a vantage-point tree with a 'likely index' shortcut and a half-distance-to-nearest-neighbour early exit. The colour distance (premultiplied alpha, max of over-black and over-white error) is a 4-lane SSE, NEON or WASM simd128 routine. The speed knob trades work directly: speed 4 (default) runs 12 k-means iterations and 20 feedback trials over up to 1.7M histogram entries, speed 10 runs no k-means, no feedback loop, no dither or contrast maps and caps the histogram at 131,072 entries; k-means, remap and dithering run on rayon threads.

## Compared with alternatives

No catalogued sibling is a palette quantizer: the siblings resize, convert colour spaces or manage ICC profiles. Pillow can call libimagequant itself (its quantize method has a libimagequant option when Pillow is built against it), so use pngquant/libimagequant directly when you want the quality gate, the speed knob and alpha-aware dithering, and Pillow's own fast-octree mode only when speed matters more than colour fidelity.

## Integration

| | |
|---|---|
| **Form** | CLI binary (Rust main plus C rwpng.c/pngquant.c via the cc crate); library as Rust crate imagequant or static lib libimagequant_sys.a with libimagequant.h (cargo-c for a shared lib) |
| **Dependencies** | CLI: libpng (libpng-sys), zlib, optional Little CMS 2 (default feature) or Cocoa on macOS, getopts, rayon via imagequant. Library: arrayvec, rgb, rayon and thread_local (threads feature); no runtime deps for C users of the static lib. |
| **Minimum toolchain** | Rust 1.67 for pngquant 3.0.4 (Cargo.toml rust-version; libimagequant says 1.65 in Cargo.toml and 1.70+ in its README), plus a C99 compiler for the CLI's C files |
| **Platforms** | Any Rust target; SIMD colour distance on x86_64 (SSE), aarch64 (NEON) and wasm32 (simd128), scalar elsewhere; threads must be disabled for WASM; no_std build available without threads |
| **Thread safety** | Documented: separate liq_attr/liq_result objects can run in parallel threads; one object may move between threads but not be used concurrently. Internally multi-threaded via rayon (RAYON_NUM_THREADS), disable with --no-default-features. |
| **Drop-in for the baseline** | no |

## Gotchas

- Stale docs: the pngquant README still says C99, OpenMP and SSE, and pngquant.1 says the default speed is 3; the code (pngquant.c help, imagequant set_speed) uses 4, threading is rayon, and libimagequant's README says OpenMP 'has been dropped entirely'. The C file's version string still reads '(January 2022)'.
- Speed 11 exists only in the CLI: it maps to library speed 10 plus --nofs and fast PNG compression; liq_set_speed accepts 1-10.
- Dithered output depends on the machine: remap_to_palette_floyd splits images over about 1 MP into up to num_cpus() chunks (std::thread::available_parallelism, not RAYON_NUM_THREADS), and each chunk restarts error diffusion after two warm-up rows, so results can differ between machines with different core counts.
- The palette is refined during remapping (one more k-means pass), so read the palette after remap_into, not before; quality numbers can be -1 at high speeds unless a quality range is set.

## Known shortcomings

- The 'ImageMagick 2.5 to 6 times' claim is snippet-only, tracing to the author's legacy ImageMagick forum thread (t=23340, blocked here), and compares pngquant's fast setting with ImageMagick's quantizer at different quality and dithering work; no pngnq or Pillow numbers exist anywhere. The 8x figure is speed 10 against pngquant's own default. The engine (libimagequant) is now Rust (pngquant 3) with a C CLI.
- The ImageMagick 2.5-6x claim is snippet-only and first-party, measured on the old C libimagequant 2.x (the engine is now Rust) at speed 10 (no k-means, no feedback trials, no dither maps), so it is not equal work. Output is not deterministic (libimagequant #130: x86_64 versus aarch64 palettes of 111 versus 120 colours; dither chunk count follows available_parallelism); README and man page are stale (C99, OpenMP, default speed 3); open #424 (desaturated colours versus ImageMagick); benches/bench.rs has no baseline and uses a private image.

## Caveats and trade-offs

Snippet only: the ImageMagick ratio lives in a blocked, old forum thread written by the author, with no images, settings, versions or hardware visible, and it compares a fast-and-rough pngquant setting against ImageMagick's default quantizer, so speed and quality settings differ (different work: pngquant's adaptive dithering and perceptual quality model vs ImageMagick's own quantizer and dithering). The 8x figure compares pngquant against itself. pngquant 3 replaced the C libimagequant with the Rust imagequant crate (CHANGELOG 3.0), so the quantization engine is Rust and only the CLI is C. Dual-licensed GPL-3.0-or-later or commercial (Super Source); the GPL option makes it copyable but copyleft.

Dual-licensed: GPL-3.0-or-later or a commercial license (the library part, libimagequant, is GPL-3.0-or-later or commercial; v4 of libimagequant is Rust with a C API, earlier versions C99). Optional OpenMP and SSE paths.

## Maintenance

Active (pngquant last commit 2026-06-21, libimagequant 4.5.0 with commits on 2026-06-21 and a WASM SIMD path added 2026-02-11), dual-licensed GPL-3.0-or-later or commercial, so copyable under copyleft; the C 2.x branch is the only all-C option and is not maintained.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The only number against ImageMagick ('2.5 to 6 times faster than ImageMagick's current algorithm' for a fast-and-rough speed setting) is a first-party statement seen only in WebSearch result text, attributed to the author's libimagequant proposal thread on the legacy ImageMagick forum (blocked); no methodology, images, versions or hardware are reachable, and the repo (README, pngquant.1, CHANGELOG, pngquant.c) carries no comparison against ImageMagick, pngnq or Pillow. Snippet-only first-party numbers cap at C, matching wave 10 precedents (font-rs, blaze).
- **Verifier notes:** Speed claim is against ImageMagick's quantizer, not pngnq or Pillow; the record's source attribution (pngquant.org) looks wrong, the text comes from the ImageMagick forum thread t=23340 per search results, which I could not open (EGRESS_BLOCKED), so it is not in urls_opened. Language-filter note: the current engine (libimagequant 4 / imagequant crate) is Rust, the CLI is C. Metadata checked on github.com: GPL v3+ (dual commercial), 5.8k stars, not archived or a fork, last commit 2026-06-21 (active).
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/kornelski/pngquant>
  - <https://github.com/kornelski/pngquant/commits/main>
  - <https://raw.githubusercontent.com/kornelski/pngquant/HEAD/README.md>
  - <https://raw.githubusercontent.com/kornelski/pngquant/HEAD/pngquant.1>
  - <https://raw.githubusercontent.com/kornelski/pngquant/HEAD/CHANGELOG>
  - <https://raw.githubusercontent.com/kornelski/pngquant/HEAD/pngquant.c>
  - <https://raw.githubusercontent.com/ImageOptim/libimagequant/HEAD/README.md>
  - <https://raw.githubusercontent.com/saima/pngquant/HEAD/README.md>
  - <https://raw.githubusercontent.com/elaberge/pngquant/HEAD/README.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/kornelski/pngquant/HEAD/README.md>
  - <https://raw.githubusercontent.com/kornelski/pngquant/HEAD/CHANGELOG>
  - <https://raw.githubusercontent.com/kornelski/pngquant/HEAD/pngquant.1>
  - <https://raw.githubusercontent.com/kornelski/pngquant/HEAD/pngquant.c>
  - <https://raw.githubusercontent.com/kornelski/pngquant/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/kornelski/pngquant/HEAD/rwpng.c>
  - <https://raw.githubusercontent.com/kornelski/pngquant/HEAD/rwpng.h>
  - <https://raw.githubusercontent.com/kornelski/pngquant/HEAD/pngquant_opts.c>
  - <https://raw.githubusercontent.com/kornelski/pngquant/HEAD/pngquant_opts.h>
  - <https://raw.githubusercontent.com/kornelski/pngquant/HEAD/rust/build.rs>
  - <https://raw.githubusercontent.com/kornelski/pngquant/HEAD/rust/bin.rs>
  - <https://raw.githubusercontent.com/kornelski/pngquant/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/kornelski/pngquant/HEAD/.github/workflows/ci.yml>
  - <https://github.com/kornelski/pngquant/commits/main>
  - <https://github.com/kornelski/pngquant/issues?q=is%3Aissue+slow+OR+performance+OR+speed>
  - <https://github.com/kornelski/pngquant/issues/424>
  - <https://raw.githubusercontent.com/ImageOptim/libimagequant/HEAD/README.md>
  - <https://raw.githubusercontent.com/ImageOptim/libimagequant/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/ImageOptim/libimagequant/HEAD/CHANGELOG>
  - <https://raw.githubusercontent.com/ImageOptim/libimagequant/HEAD/benches/bench.rs>
  - <https://raw.githubusercontent.com/ImageOptim/libimagequant/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/ImageOptim/libimagequant/HEAD/src/attr.rs>
  - <https://raw.githubusercontent.com/ImageOptim/libimagequant/HEAD/src/mediancut.rs>
  - <https://raw.githubusercontent.com/ImageOptim/libimagequant/HEAD/src/kmeans.rs>
  - <https://raw.githubusercontent.com/ImageOptim/libimagequant/HEAD/src/nearest.rs>
  - <https://raw.githubusercontent.com/ImageOptim/libimagequant/HEAD/src/hist.rs>
  - <https://raw.githubusercontent.com/ImageOptim/libimagequant/HEAD/src/remap.rs>
  - <https://raw.githubusercontent.com/ImageOptim/libimagequant/HEAD/src/quant.rs>
  - <https://raw.githubusercontent.com/ImageOptim/libimagequant/HEAD/src/pal.rs>
  - <https://raw.githubusercontent.com/ImageOptim/libimagequant/HEAD/src/capi.rs>
  - <https://raw.githubusercontent.com/ImageOptim/libimagequant/HEAD/imagequant-sys/Cargo.toml>
  - <https://raw.githubusercontent.com/ImageOptim/libimagequant/HEAD/imagequant-sys/README.md>
  - <https://raw.githubusercontent.com/ImageOptim/libimagequant/HEAD/imagequant-sys/libimagequant.h>
  - <https://github.com/ImageOptim/libimagequant/issues>
  - <https://github.com/ImageOptim/libimagequant/issues/130>
  - <https://github.com/ImageOptim/libimagequant/commits/main>
  - <https://raw.githubusercontent.com/Chadys/QuantizeImageMethods/HEAD/README.md>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/kornelski/pngquant`) · [data/wave10/enrich/raw/github_com_kornelski_pngquant.json](../../../data/wave10/enrich/raw/github_com_kornelski_pngquant.json) (enrichment confidence 0.75)

</details>
