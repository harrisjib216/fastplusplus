# stb-image-opt

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `MIT OR Unlicense` · 🟢 active

> Drop-in stb_image.h v2.30 fork with AVX2 JPEG kernels and leaner PNG decode; about 1.10x upstream, partly from flags and PGO.

| | |
|---|---|
| **Beats** | upstream stb_image.h v2.30 (nothings/stb at 2c980bb), compiled the way consumers compile it (-O2) |
| **Claimed result** | Fork build (-O3 -march=x86-64-v2 -ffp-contract=off plus held-out PGO) against upstream stb_image v2.30 built at -O2, req_comp=0, 14 files: geomean 1.101x (results/summary.csv, range 0.986x for hdr_range.hdr to 1.289x for palette PNG). Per format (derived from page data): 7 PNG rows geomean 1.097x, 4 JPEG rows geomean 1.139x (progressive JPEG 1.194x). The GIF (1.214x), PSD (0.995x) and HDR (0.986x) decoders are unchanged in the fork (diff of src/stb_image.h against upstream/stb_image.h touches only the AVX2 dispatch, the JPEG IDCT and YCbCr paths, stbi__parse_huffman_block and the PNG row code), so the GIF +21% the README lists comes from compiler flags and PGO alone; those three unchanged rows give a geomean of 1.060x (derived from page data). JPEG to RGBA (req_comp=4, up4.csv against fork4.csv): JPEG rows geomean 1.128x and all 14 rows 1.090x (derived from page data), with plasma_512.png at 0.992x and basn0g16.png at 0.937x. The same-flag source-only A/B figures (PNG +8.6% geomean; IDCT +7.7% at req_comp=0 and +13.7% at req_comp=4) appear only as text in NOTES.md, with no committed results file. Isolated kernels against the fork's own SSE2 path (kernels.csv, built at -march=x86-64-v3): AVX2 YCbCr 0.132 against 0.216 ns/px (1.63x), AVX2 IDCT pair 0.163 against 0.274 ns/px (1.68x; the README rounds to 1.70x). |
| **Workload** | Image decode time in ns per pixel (minimum of 7 repeats, 0.1 s budget per repeat, pinned with taskset) over a 14-file mixed suite (7 PNG, 4 JPEG, 1 GIF, 1 PSD, 1 HDR; mostly small synthetic 512x512 and 640x480 images plus PNGSuite files) with req_comp=0, plus a req_comp=4 JPEG run. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-14700F (Raptor Lake), WSL2, benchmark process pinned to one core with taskset |
| **Compiler and flags** | clang 23.1.2. Baseline: upstream header at -O2. Fork: -O3 -march=x86-64-v2 -ffp-contract=off plus multi-workload PGO trained on a held-out corpus (harness/bench_vs_upstream.sh). AVX2 kernels are runtime-dispatched via CPUID and XGETBV. |
| **Adoption** | 0 stars, 0 forks, 0 watchers; 18 commits, all dated 2026-09-28; releases up to v1.3.0 |
| **Last commit** | 2026-09-28 |
| **Links** | [repository](https://github.com/aplghl/stb-image-opt) · [benchmark](https://github.com/aplghl/stb-image-opt) |

## Verdict

On an Intel i7-14700F under WSL2 with clang 23.1.2, the fork built at -O3 -march=x86-64-v2 -ffp-contract=off with PGO decoded a 14-file, mostly small synthetic suite 1.101x faster (geomean) than upstream stb_image v2.30 at -O2 (0.986x HDR to 1.289x palette PNG; JPEG rows 1.139x, PNG rows 1.097x), and 1.090x at req_comp=4. Unchanged decoders gain too (GIF 1.21x, 1.35x at req_comp=4), so flags and PGO carry a large share; the same-flag source-only gains (PNG +8.6%, IDCT +7.7% and +13.7%) exist only as NOTES.md text.

## Use it when

- You already vendor stb_image.h and decode JPEG on x86-64 CPUs with AVX2, especially to RGBA (req_comp=4; JPEG rows geomean 1.128x) or progressive JPEG (1.19x row at req_comp=0).
- You need byte-identical output to upstream so existing goldens stay valid: the repo's differential harness compares about 12,300 decodes against the pristine upstream oracle on every dispatch path with clang, gcc and zig cc.
- You decode palette or 8-bit PNGs at their native channel count (req_comp=0), where the direct-to-output unfilter and chunked LZ77 copy apply (palette PNG row 1.29x, which also includes flags and PGO).
- You are willing to build the library yourself with -O3 -march=x86-64-v2 and PGO (scripts/build_opt.sh with PGO=1), which is the configuration that was measured.

## Skip it when

- Raw decode speed is the goal: the baseline is stb_image, and no source compares this fork with libjpeg-turbo, libpng, libspng or Wuffs, so the 10% says nothing about those decoders.
- You only swap the header and keep -O2, or use the prebuilt release tarballs: release.yml builds them with zig build -Doptimize=ReleaseFast -Dtarget=&lt;triple&gt;, with no PGO and no -march=x86-64-v2, so the roughly 6% PGO share and the flag share are absent.
- Your build uses -march=x86-64-v3 or native: NOTES.md measured that flag slowing JPEG decode (2.53 vs 2.37 ns/px), and the recommended -march=x86-64-v2 itself needs SSE4.2-class CPUs.
- MSVC or non-x86 targets: the AVX2 path is compiled only for GCC or Clang on x86 (STBI_AVX2 guard), so MSVC and aarch64 builds get only the portable PNG changes.
- Untrusted input: outside the JPEG IDCT/color and PNG row code it runs upstream's v2.30 loaders unchanged, and the GHSL reports CVE-2023-45661..45667 (filed against v2.28, GIF and other loaders) are partly still open; the Debian tracker lists CVE-2023-45664 (GIF double free) as unfixed (search snippet only).

## How it is fast

For JPEG it adds a 16-pixel AVX2 YCbCr-to-RGBA kernel and a two-block AVX2 integer IDCT (two 8x8 blocks, one per 128-bit lane, a lane-wise widening of stb's SSE2 IDCT), picked at runtime with CPUID plus XGETBV; the non-interleaved, interleaved and progressive finish loops pair adjacent or same-stride blocks to feed it. For PNG, 8-bit rows with img_n == out_n are unfiltered directly into the output buffer (no scratch row and copy), and the inflate LZ77 copy uses memset for dist 1 and memcpy chunks for dist &gt;= 8 instead of a byte loop. A large part of the headline comes from building the fork at -O3 -march=x86-64-v2 with profile-guided optimization against upstream at -O2: the unchanged GIF decoder gains 1.21x at req_comp=0 and 1.35x at req_comp=4 (derived from up4.csv and fork4.csv).

## Compared with alternatives

Choose it over libspng, zune-png, ffpng or libjpeg-turbo only when you are tied to the stb_image API, a single-header build and upstream-identical output; those siblings are measured against libpng, image-png or libjpeg-turbo and none is compared with this fork, so benchmark them first if decode speed is what matters. Its encode-side counterpart from the same author is stb-image-write-opt.

## Integration

| | |
|---|---|
| **Form** | header-only (single-header drop-in), or static lib via scripts/build_opt.sh or build.zig |
| **Dependencies** | none beyond libc and libm; the AVX2 path includes immintrin.h and cpuid.h |
| **Minimum toolchain** | Same C dialect as upstream stb_image (compiles as C and C++ per README); AVX2 path needs GCC or Clang target attributes; tested with clang 23.1.2, gcc 13.3 and zig 0.16 zig cc |
| **Platforms** | x86-64 with AVX2 runtime dispatch and SSE2 or scalar fallback; aarch64 Linux and macOS and x86_64 Windows (MinGW) cross-compile without new SIMD |
| **Thread safety** | Same as upstream: each decode call is independent, and the failure reason and flip flag are thread-local where STBI_THREAD_LOCAL is available; the fork adds a static cached CPUID result written without synchronization (always the same value). |
| **Drop-in for the baseline** | partial — API, ABI and decoded bytes match upstream stb_image, but the measured speed needs -O3 -march=x86-64-v2 plus PGO; a plain header swap at -O2 gets only the source-change share |

## Gotchas

- The 'held-out' PGO set excludes only the measured file names: corpus/gen_corpus.py also emits the same plasma_512 and grad_640_480 images at other JPEG quality and subsampling settings plus RGBA, gray, BMP and TGA variants, and static.gif is frame 0 of the timed anim.gif, so the profile was trained on near-identical content (NOTES.md: in-sample +7% vs held-out +6.3%).
- The PNG gains apply only when img_n == out_n; asking for RGBA from RGB or 16-bit PNGs can be slower (req_comp=4: plasma_512.png 0.992x, basn0g16.png 0.937x).
- STBI_FORCE_AVX2 makes stbi__avx2_available() return 1 without a CPUID check, so a build with it crashes on CPUs without AVX2; keep it for testing only. The rejected AVX2 PNG unfilter is still in the header behind STBI_AVX2_PNG_FILTER and measured 0.44x-0.99x.
- Kernel figures (AVX2 YCbCr 1.63x, IDCT pair 1.68x in kernels.csv, rounded to 1.70x in the README) are against the fork's own SSE2 path built at -march=x86-64-v3, not end-to-end decode.

## Known shortcomings

- The baseline is upstream stb_image, not libjpeg-turbo or libpng, and the flags are asymmetric (fork at -O3 plus PGO against upstream -O2): the PSD and HDR decoders are unchanged in the header diff yet still gain (geomean 1.060x, derived from page data), so part of the 1.101x geomean is flags and PGO; the source-only A/B numbers are NOTES.md prose with no CSV.
- Enricher (2026-10-04): the 1.101x geomean mixes source changes with -O3 -march=x86-64-v2 and PGO against upstream at -O2; unchanged decoders gain too (GIF 1.21x, 1.35x at req_comp=4), so flags and PGO carry a large share, and the same-flag source-only gains (PNG +8.6%, IDCT +7.7%/+13.7%) exist only as NOTES.md text. The 'held-out' PGO set is near-identical content (same plasma_512 and grad_640_480 images at other settings; static.gif is frame 0 of the timed anim.gif). PNG gains apply only when img_n == out_n (req_comp=4 can be slower: 0.992x, 0.937x). STBI_FORCE_AVX2 skips the CPUID check and crashes on CPUs without AVX2; the rejected AVX2 PNG unfilter (0.44x-0.99x) is still in the header. Kernel figures (1.63x, 1.68x) are against the fork's own SSE2 path, not end-to-end. One author, 18 commits all on 2026-09-28, 0 stars; unofficial fork.

## Caveats and trade-offs

The baseline is upstream stb_image, not libjpeg-turbo, libpng, libwebp or libavif, so this says nothing about the listed incumbents. The headline compares the fork built with -O3 -march=x86-64-v2 and held-out PGO against upstream built with -O2 and no PGO; the harness commits no same-flag fork-versus-upstream run, so the source-change share cannot be recomputed from results files. NOTES.md says flags alone move little, -O3 helps the GIF decoder by about 9%, and held-out PGO is worth about +6.3% (in-sample about +7%); the GIF, PSD and HDR decoders are untouched by the fork, so their ratios (1.214x, 0.995x, 0.986x) measure only flags, PGO and layout. A consumer would get those gains by compiling upstream the same way. The source-only A/B figures (PNG +8.6%, IDCT +7.7%/+13.7%) are text-only in NOTES.md. The suite is PNG-heavy, uses small synthetic 512x512 and 640x480 images plus 32x32 PNGSuite files, and drops basn2c16.png, which the harness lists but the repository does not contain. Two req_comp=4 rows are slower than upstream (plasma_512.png 0.992x, basn0g16.png 0.937x). Single machine under WSL2; NOTES.md calls per-file ratios under about 3% noise. Kernel speedups are against the fork's own SSE2 path, not upstream, and the kernel bench is built at -march=x86-64-v3 rather than the recommended -v2. Unofficial fork not endorsed by the upstream author, single author, repository created 2026-09-28 with no outside users yet.

Only src/stb_image.h changes (+539/-10 lines, additive and guarded), so it stays a single drop-in header with unchanged API and ABI. AVX2 JPEG kernels (YCbCr to RGB, two-block IDCT) are selected at runtime and fall back to SSE2 or scalar on other CPUs; non-x86 targets cross-compile but get no SIMD gain. Output is bit-identical to upstream: README and NOTES.md report 12,306 differential checks (stbi_load req_comp 0-4, stbi_load_16, stbi_loadf, GIF frames, stbi_info) on every dispatch path with clang, gcc and zig cc, plus ASan/UBSan and libFuzzer runs. Prebuilt static libraries for Linux (glibc, musl, ARM64) and Windows are attached to releases. Scope is decode only.

## Maintenance

Active but brand new: one author, 18 commits all on 2026-09-28, releases v1.0.0 to v1.3.0, 0 stars and no issues or PRs; MIT OR Unlicense like upstream, so the single header is easy to vendor, but it is an unofficial fork not endorsed by the stb author.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification A, tier now A.
- **Tier reason:** Public harness (bench/bench.c, harness/bench.sh, harness/bench_vs_upstream.sh) builds upstream stb_image.h v2.30 at -O2 and the fork at -O3 -march=x86-64-v2 -ffp-contract=off with held-out PGO, with clang 23.1.2 on an Intel i7-14700F stated; results/summary.csv, upstream_o2.csv, fork_pgo.csv, up4.csv, fork4.csv and kernels.csv match the README figures. Tier A covers the build-versus-build comparison; the flags are asymmetric, so the source-only share is smaller (see caveats).
- **Verifier notes:** Numbers check out against the committed CSVs and harness. The README credits the GIF +21% to the fork, but the GIF decoder is unchanged, so that gain comes from flags and PGO; claimed_speedup now splits the flag and source shares as far as the committed data allows.
- **Fields the verifier corrected:** `claimed_speedup`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** first-party harness
- **Pages the verifier opened:**
  - <https://github.com/aplghl/stb-image-opt>
  - <https://github.com/aplghl/stb-image-opt/commits>
  - <https://raw.githubusercontent.com/aplghl/stb-image-opt/HEAD/README.md>
  - <https://raw.githubusercontent.com/aplghl/stb-image-opt/HEAD/NOTES.md>
  - <https://raw.githubusercontent.com/aplghl/stb-image-opt/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/aplghl/stb-image-opt/HEAD/Makefile>
  - <https://raw.githubusercontent.com/aplghl/stb-image-opt/HEAD/harness/bench_vs_upstream.sh>
  - <https://raw.githubusercontent.com/aplghl/stb-image-opt/HEAD/harness/bench.sh>
  - <https://raw.githubusercontent.com/aplghl/stb-image-opt/HEAD/harness/kernbench.sh>
  - <https://raw.githubusercontent.com/aplghl/stb-image-opt/HEAD/bench/bench.c>
  - <https://raw.githubusercontent.com/aplghl/stb-image-opt/HEAD/bench/kernbench.c>
  - <https://raw.githubusercontent.com/aplghl/stb-image-opt/HEAD/results/README.md>
  - <https://raw.githubusercontent.com/aplghl/stb-image-opt/HEAD/results/summary.csv>
  - <https://raw.githubusercontent.com/aplghl/stb-image-opt/HEAD/results/upstream_o2.csv>
  - <https://raw.githubusercontent.com/aplghl/stb-image-opt/HEAD/results/fork_pgo.csv>
  - <https://raw.githubusercontent.com/aplghl/stb-image-opt/HEAD/results/up4.csv>
  - <https://raw.githubusercontent.com/aplghl/stb-image-opt/HEAD/results/fork4.csv>
  - <https://raw.githubusercontent.com/aplghl/stb-image-opt/HEAD/results/kernels.csv>
  - <https://raw.githubusercontent.com/aplghl/stb-image-opt/HEAD/src/stb_image.h>
  - <https://raw.githubusercontent.com/aplghl/stb-image-opt/HEAD/upstream/stb_image.h>
- **Sources the enricher read:**
  - <https://github.com/aplghl/stb-image-opt>
  - <https://github.com/aplghl/stb-image-opt/tree/main/corpus>
  - <https://github.com/aplghl/stb-image-opt/tree/main/.github/workflows>
  - <https://github.com/aplghl/stb-image-opt/releases>
  - <https://github.com/aplghl/stb-image-opt/issues?q=is%3Aissue>
  - <https://github.com/aplghl/stb-image-opt/pulls?q=is%3Apr>
  - <https://raw.githubusercontent.com/aplghl/stb-image-opt/HEAD/README.md>
  - <https://raw.githubusercontent.com/aplghl/stb-image-opt/HEAD/NOTES.md>
  - <https://raw.githubusercontent.com/aplghl/stb-image-opt/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/aplghl/stb-image-opt/HEAD/CONTRIBUTING.md>
  - <https://raw.githubusercontent.com/aplghl/stb-image-opt/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/aplghl/stb-image-opt/HEAD/Makefile>
  - <https://raw.githubusercontent.com/aplghl/stb-image-opt/HEAD/build.zig>
  - <https://raw.githubusercontent.com/aplghl/stb-image-opt/HEAD/lib/stb_image.c>
  - <https://raw.githubusercontent.com/aplghl/stb-image-opt/HEAD/scripts/build_opt.sh>
  - <https://raw.githubusercontent.com/aplghl/stb-image-opt/HEAD/.github/workflows/ci.yml>
  - <https://raw.githubusercontent.com/aplghl/stb-image-opt/HEAD/.github/workflows/release.yml>
  - <https://raw.githubusercontent.com/aplghl/stb-image-opt/HEAD/harness/bench_vs_upstream.sh>
  - <https://raw.githubusercontent.com/aplghl/stb-image-opt/HEAD/harness/bench.sh>
  - <https://raw.githubusercontent.com/aplghl/stb-image-opt/HEAD/harness/kernbench.sh>
  - <https://raw.githubusercontent.com/aplghl/stb-image-opt/HEAD/harness/diff.sh>
  - <https://raw.githubusercontent.com/aplghl/stb-image-opt/HEAD/bench/bench.c>
  - <https://raw.githubusercontent.com/aplghl/stb-image-opt/HEAD/bench/kernbench.c>
  - <https://raw.githubusercontent.com/aplghl/stb-image-opt/HEAD/corpus/gen_corpus.py>
  - <https://raw.githubusercontent.com/aplghl/stb-image-opt/HEAD/results/README.md>
  - <https://raw.githubusercontent.com/aplghl/stb-image-opt/HEAD/results/summary.csv>
  - <https://raw.githubusercontent.com/aplghl/stb-image-opt/HEAD/results/upstream_o2.csv>
  - <https://raw.githubusercontent.com/aplghl/stb-image-opt/HEAD/results/fork_pgo.csv>
  - <https://raw.githubusercontent.com/aplghl/stb-image-opt/HEAD/results/up4.csv>
  - <https://raw.githubusercontent.com/aplghl/stb-image-opt/HEAD/results/fork4.csv>
  - <https://raw.githubusercontent.com/aplghl/stb-image-opt/HEAD/results/kernels.csv>
  - <https://raw.githubusercontent.com/aplghl/stb-image-opt/HEAD/src/stb_image.h>
  - <https://raw.githubusercontent.com/aplghl/stb-image-opt/HEAD/upstream/stb_image.h>
  - https://security-tracker.debian.org/tracker/CVE-2023-45664 (WebSearch snippet only)
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/aplghl/stb-image-opt`) · [data/wave10/enrich/raw/github_com_aplghl_stb_image_opt.json](../../../data/wave10/enrich/raw/github_com_aplghl_stb_image_opt.json) (enrichment confidence 0.8)

</details>
