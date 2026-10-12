# GraphicsMagick

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Color conversion and resampling](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `MIT` · 🟢 active

> ImageMagick-derived C image-processing library and gm CLI; about 2.2x faster than ImageMagick 7 on libvips's crop-shrink-sharpen test.

| | |
|---|---|
| **Beats** | ImageMagick 7.1.1 (convert) |
| **Claimed result** | libvips wiki table (quickest of five runs): gm 1.4 2.05 s, 1975.81 MB peak vs ImageMagick 7.1.1 convert 4.44 s, 1499.29 MB (magick 4.41 s), about 2.2x faster (derived from page data); ppm-gm 1.58 s; jpg-gm 2.49 s vs jpg-convert 4.38 s, about 1.76x (derived from page data). gm used about 32% more peak memory than convert (derived from page data). The SourceForge page quotes a 2023 user review, 'Faster and more secure than ImageMagick' (no numbers). |
| **Workload** | libvips vips-bench task: load a 10000x10000 8-bit RGB tiled TIFF, crop 100 px from each edge, shrink by 10% with -filter triangle -resize 90x90%, apply a 3x3 -convolve sharpen and save; quickest real time of five runs, no disc-cache clearing. gm.sh crops after loading with -shave 100x100, while im.sh crops on load (an advantage to ImageMagick); the resize and convolve arguments are identical. |
| **Metric** | latency and memory |
| **Hardware** | AMD Ryzen Threadripper PRO 3955WX 16-Cores, Ubuntu 25.04 (run 12 Aug 2025) |
| **Compiler and flags** | Ubuntu 25.04 distro packages ('systems as packaged for Ubuntu'); no compiler or flags stated; the vips-bench driver benchmark.sh sets OMP_NUM_THREADS=16, so gm and ImageMagick both ran with OpenMP threads |
| **Adoption** | Widely packaged (Debian/Ubuntu and others); SourceForge: 3,405 downloads this week and 21 reviews, project registered 2003-02-07 (page read 2026-10-03) |
| **Last commit** | 2026-10-03 |
| **Links** | [repository](https://sourceforge.net/projects/graphicsmagick/) · [benchmark](https://github.com/libvips/libvips/wiki/Speed-and-memory-use) |

## Verdict

In the libvips maintainers' vips-bench run (Threadripper PRO 3955WX, Ubuntu 25.04 distribution packages, 16 OpenMP threads, quickest of five runs, 12 Aug 2025), gm took 2.05 s against 4.44 s for ImageMagick 7.1.1 convert (about 2.2x) and 2.49 s against 4.38 s with JPEG input (about 1.76x), while using about 32% more peak memory (derived from page data). The 'gm 1.4' label is the Debian package string '1.4+really1.3.x', so the tested build was a 1.3.4x release (Ubuntu 24.04 shipped 1.3.42 and 25.10 ships 1.3.45+hg17696; the 25.04 build is no longer listed). GraphicsMagick's own benchmarks page (www/benchmarks.rst) gives only first-party hyperfine examples (rotate 92 degrees on a 3500x2300 PNM: gm 178.0 ms vs magick 785.3 ms, no CPU named).

## Use it when

- Batch command-line or server image pipelines (decode, resize, sharpen, encode) that use ImageMagick today and want lower latency on a multi-core machine.
- C or C++ programs that need ImageMagick-style format coverage with an MIT-style licence and a conservative, stable API (core C API, Wand or Magick++).
- Scripts written for ImageMagick 6 convert syntax that can be pointed at gm convert, or at the compatibility links from --enable-magick-compat, after checking each command.
- Q8 builds for 8-bit-only workloads where speed matters more than precision; the project's install guide says Q16 runs 15% to 50% slower and uses twice the memory.

## Skip it when

- Large-image or memory-limited jobs: on the libvips test gm peaked at about 1.98 GB against about 94 MB for libvips, which was also about 3.6x faster.
- When you need ImageMagick 7 features or exact ImageMagick 7 command semantics: the two projects have diverged, and GraphicsMagick's own benchmarks page says the same filter arguments now do different amounts of work in each.
- Processing untrusted uploads without sandboxing: the 2025-2026 releases still fix heap overflows in coders (MIFF, PCX, TIFF EXIF, MNG and others), and the project's security page tells users to run it in a container and keep up with releases rather than trust distribution packages.
- Single-image latency work dominated by file I/O or start-up: the project's OpenMP notes say decode and encode usually do not speed up with threads, and start-up can outweigh the operation itself.

## How it is fast

Pixel loops are parallelised across rows or columns with OpenMP, and the pixel cache was rewritten so several threads can work on one image. Resize is a classic two-pass separable filter (HorizontalFilter then VerticalFilter in magick/resize.c), with per-thread contribution tables and the pass order chosen to minimise work. Convolution (magick/effect.c) uses a float kernel normalised by its sum, with a fixed-size inner loop per channel. There are no hand-written SIMD intrinsics in these paths; speed depends on the compiler's auto-vectorisation and on the build's quantum depth.

## Compared with alternatives

Pick GraphicsMagick over libvips when you need ImageMagick-style command syntax, a broad set of formats and a whole-image API, and can accept far higher memory (2.05 s and about 1.98 GB against libvips's 0.57 s and 94 MB on the same test); pick it over OpenImageIO (3.46 s) or ImageMagick itself when the job is ImageMagick-style batch conversion. FFmpeg (2.06 s) is about equal on this test but is not a general still-image toolkit.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | none required for the core; optional delegate libraries per format (libjpeg or libjpeg-turbo, libpng, libtiff, zlib, bzip2, lcms2, FreeType, libwebp, JasPer, Ghostscript and others); optional tcmalloc |
| **Minimum toolchain** | C99 compiler with stdint.h and inttypes.h (required since 2025-06-17); C++ compiler for Magick++; OpenMP-capable compiler (GCC or Clang) for multi-threading |
| **Platforms** | Linux, BSD, macOS, Cygwin, MinGW/MSYS2 and Windows (Visual Studio); portable C, any CPU architecture |
| **Thread safety** | The library is built thread-safe by default (locking through thread APIs), and the pixel cache supports several threads working on one image; OpenMP thread count is set with OMP_NUM_THREADS or -limit threads. |
| **Drop-in for the baseline** | partial: gm convert accepts most ImageMagick 6-style convert options, and --enable-magick-compat installs convert-style links, but the APIs differ from ImageMagick 7's MagickCore and MagickWand and some options behave differently. |

## Gotchas

- Quantum depth is fixed at build time and defaults to 8 bits; distribution packages appear to use 16 bits (the measured 1.98 GB peak matches two 10000x10000 images at about 1 GB each under the install guide's QuantumDepth\*Rows\*Columns\*5/8 formula; derived, package flags not read). Q8 and Q16 builds differ in both speed and output precision.
- ConvolveImage divides a user kernel by its sum, so -convolve with the benchmark's sharpen kernel (sum 8) gives a mild sharpen; output can differ from an ImageMagick command that does not normalise. The libvips benchmark does not compare output images.
- Distribution version strings are misleading: Debian and Ubuntu package 1.3.x releases as '1.4+really1.3.x'. GraphicsMagick 1.4 is still an unreleased development branch (version.sh on the default branch: PACKAGE_VERSION '1.4', release date 'unreleased'); the latest release is 1.3.48 (2026-07-23).
- glibc malloc can limit OpenMP scaling on many cores; the install guide recommends --with-tcmalloc and reports up to 2x on some algorithms.

## Known shortcomings

- Tier B on the libvips maintainers' vips-bench (gm.sh and im.sh public; Threadripper PRO 3955WX, 12 August 2025): gm 2.05 s vs ImageMagick convert 4.44 s, Ubuntu packages with no flags. gm crops after load while ImageMagick crops on load, so the work differs. Hosted on SourceForge (hg), last commit 2026-10-03.
- The libvips table's 'gm 1.4' label is Debian's '1.4+really1.3.x' version string (1.4 is unreleased; the 25.04 build is probably 1.3.45), and the 1.98 GB peak fits a Q16 build (derived from the INSTALL formula). ConvolveImage normalises the sharpen kernel by its sum of 8 and the bench compares no outputs. The project's own benchmarks.rst declines GraphicsMagick-versus-ImageMagick numbers, offering only a hyperfine rotate of 178.0 against 785.3 ms with no CPU. Coder heap overflows were still being fixed in 2026, so sandbox untrusted input.

## Caveats and trade-offs

The evidence is a third-party table (the libvips project's wiki, run by the libvips maintainers with vips-bench) for one crop, shrink and sharpen task. The wiki itself says the task is file-I/O heavy with little processing, so it is not a pure resampling benchmark. GraphicsMagick 1.4 and ImageMagick 7.1.1 were Ubuntu 25.04 packages, so compiler flags and quantum-depth/HDRI settings are not stated, and both ran 16 OpenMP threads. The work is not quite identical: gm crops after a full load with -shave, while ImageMagick crops on load, which favours ImageMagick. GraphicsMagick is faster but used more peak memory (1975.81 MB vs 1499.29 MB). The project's own benchmark page (graphicsmagick.org/benchmarks.html) is unreachable here. The license is an MIT-style license; Copyright.txt also lists permissive licenses for inherited components (ImageMagick, du Pont, libtiff-derived code).

Fork-lineage sibling of ImageMagick with a smaller, stability-focused feature set and a more conservative API; uses more memory than libvips (about 2 GB on this test). Source is hosted in Mercurial on SourceForge, not GitHub.

## Maintenance

Actively maintained by one lead developer (Bob Friesenhahn; release 1.3.48 on 2026-07-23, Mercurial commits on 2026-10-03) and MIT-licensed, so it can be copied or linked freely; use the latest release because nearly every release carries security fixes.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now B.
- **Tier reason:** The libvips wiki 'Speed and memory use' table is the libvips maintainers' measurement with their public vips-bench repo (gm.sh, im.sh, benchmark.sh) on a named CPU (Threadripper PRO 3955WX, Ubuntu 25.04, run 12 Aug 2025). It is independent of both GraphicsMagick and ImageMagick and shows gm 1.4 at 2.05 s against ImageMagick 7.1.1 convert at 4.44 s. Both are Ubuntu packages with no compiler or flags stated, so the evidence is B, not A.
- **Verifier notes:** The measurement belongs to the libvips maintainers (wiki page edited 2026-04-12, tests last run 12 Aug 2025), not to GraphicsMagick or ImageMagick; all the numbers belong to the gm, ppm-gm, jpg-gm, convert and jpg-convert rows. last_commit is set from the primary Mercurial repo on SourceForge (commit 779423 by Bob Friesenhahn, 2026-10-03 20:33:53), so maintenance_status stays active.
- **Fields the verifier corrected:** `last_commit`, `stars_or_usage`, `compiler_and_flags`, `claimed_speedup`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/libvips/libvips/wiki/Speed-and-memory-use>
  - <https://raw.githubusercontent.com/wiki/libvips/libvips/Speed-and-memory-use.md>
  - <https://github.com/libvips/vips-bench>
  - <https://raw.githubusercontent.com/libvips/vips-bench/master/gm.sh>
  - <https://raw.githubusercontent.com/libvips/vips-bench/master/im.sh>
  - <https://raw.githubusercontent.com/libvips/vips-bench/master/im7.sh>
  - <https://raw.githubusercontent.com/libvips/vips-bench/master/benchmark.sh>
  - <https://sourceforge.net/projects/graphicsmagick/>
  - <https://sourceforge.net/p/graphicsmagick/code/ci/default/log/>
  - <https://sourceforge.net/p/graphicsmagick/code/ci/default/tree/Copyright.txt?format=raw>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/wiki/libvips/libvips/Speed-and-memory-use.md>
  - <https://raw.githubusercontent.com/libvips/vips-bench/master/gm.sh>
  - <https://raw.githubusercontent.com/libvips/vips-bench/master/im.sh>
  - <https://raw.githubusercontent.com/libvips/vips-bench/master/im7.sh>
  - <https://raw.githubusercontent.com/libvips/vips-bench/master/benchmark.sh>
  - <https://raw.githubusercontent.com/libvips/vips-bench/master/README.md>
  - <https://sourceforge.net/projects/graphicsmagick/>
  - <https://sourceforge.net/p/graphicsmagick/code/ci/default/log/>
  - <https://sourceforge.net/p/graphicsmagick/code/ci/default/tree/NEWS.txt?format=raw>
  - <https://sourceforge.net/p/graphicsmagick/code/ci/default/tree/README.txt?format=raw>
  - <https://sourceforge.net/p/graphicsmagick/code/ci/default/tree/Copyright.txt?format=raw>
  - <https://sourceforge.net/p/graphicsmagick/code/ci/default/tree/version.sh?format=raw>
  - <https://sourceforge.net/p/graphicsmagick/code/ci/default/tree/www/>
  - <https://sourceforge.net/p/graphicsmagick/code/ci/default/tree/www/benchmarks.rst?format=raw>
  - <https://sourceforge.net/p/graphicsmagick/code/ci/default/tree/www/OpenMP.rst?format=raw>
  - <https://sourceforge.net/p/graphicsmagick/code/ci/default/tree/www/INSTALL-unix.rst?format=raw>
  - <https://sourceforge.net/p/graphicsmagick/code/ci/default/tree/www/security.rst?format=raw>
  - <https://sourceforge.net/p/graphicsmagick/code/ci/default/tree/magick/effect.c?format=raw>
  - <https://sourceforge.net/p/graphicsmagick/code/ci/default/tree/magick/resize.c?format=raw>
  - <https://sourceforge.net/p/graphicsmagick/bugs/search/?q=slow+OR+performance+OR+openmp&limit=50>
  - <https://packages.ubuntu.com/search?keywords=graphicsmagick&searchon=names&suite=all&section=all>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://sourceforge.net/projects/graphicsmagick`) · [data/wave10/enrich/raw/sourceforge_net_projects_graphicsmagick.json](../../../data/wave10/enrich/raw/sourceforge_net_projects_graphicsmagick.json) (enrichment confidence 0.75)

</details>
