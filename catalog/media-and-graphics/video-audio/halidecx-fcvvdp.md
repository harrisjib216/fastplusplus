# fcvvdp

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Video and audio](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `Apache-2.0` · 🟢 active

> C reimplementation of the CVVDP video-quality metric; first-party 1.28x (1 thread) and 3.22x (8 threads) faster than Python cvvdp.

| | |
|---|---|
| **Beats** | cvvdp reference implementation (gfxdisp/ColorVideoVDP, Python, multithreaded) |
| **Claimed result** | README: 'fcvvdp uses over 91% less memory. With one thread, it is over 28% faster; with multiple threads, fcvvdp is over 221% faster than the reference implementation.' Wall time 19.1 s (cvvdp) vs 14.9 s (fcvvdp -t 1, -21.7%) vs 5.94 s (fcvvdp -t 8, -68.9%); peak RSS 1.03 GB vs 90.4 MB vs 89.7 MB. |
| **Workload** | Computing the CVVDP perceptual video quality metric between a reference and an x264-encoded 360p video (302 frames), measured with the poop benchmark tool, 3 runs each. |
| **Metric** | throughput |
| **Hardware** | Linux, Intel Core i7-13700K |
| **Compiler and flags** | Not stated for the benchmark run. The README builds with `zig build --release=fast` (optional -Dflto=true) and now requires Zig 0.16.x, but the benchmark lines date from commit 6ce3696 (2026-03-10), before the 2026-04-22 move to Zig 0.16. |
| **Adoption** | 73 stars, 10 forks |
| **Last commit** | 2026-09-22 |
| **Links** | [repository](https://github.com/halidecx/fcvvdp) · [benchmark](https://github.com/halidecx/fcvvdp) |

## Verdict

One first-party poop run (3 runs each) on Linux with a Core i7-13700K scoring a 302-frame 360p clip against its x264 encode (fhd display): Python cvvdp (multithreaded, PyTorch version and device unstated, start-up and decoding included) took 19.1 s at 1.03 GB RSS, fcvvdp -t 1 14.9 s (1.28x) and -t 8 5.94 s (3.22x) at about 90 MB. The Zig/clang version and flags at the time are unstated, the clip is not shipped, and the measured commit predates the sRGB and PR #19 scoring fixes.

## Use it when

- Batch CVVDP scoring of encoder sweeps on CPU-only servers, where the Python reference's PyTorch dependency and about 1 GB RSS per process (at 360p in the README run) limit how many jobs fit on a machine.
- Embedding CVVDP in a C or C++ encoder, tuner or test harness: static libcvvdp.a plus cvvdp.h with extern "C", fed one frame pair at a time through cvvdp_process_frame.
- FFmpeg-based pipelines that can carry a patched FFmpeg n8.0 build (-lavfi fcvvdp, per-frame stats_file output).
- Still-image comparisons (PNG, QOI, PNM/PAM) across many display models, including HDR PQ/HLG presets and custom display parameters.
- Apple Silicon and other aarch64 machines, where the NEON kernels are always used (the PR #19 timings were taken on an Apple M5 Pro).

## Skip it when

- When your numbers must match the official Python ColorVideoVDP release: the repo validates score parity only against Vship/FFVship (PR #19: 0.000001-0.000002 JOD after the fix); no comparison against the Python package is published.
- Windows builds: README lists macOS, Linux and Unix-like systems, the code uses pthreads and sysconf, and issue #6 (Windows build fails) was closed as not planned.
- High-resolution, high-frame-rate video on memory-tight machines: each context keeps two float RGB ring buffers of 2\*ceil(fps/8)+1 frames, roughly 3.4 GB at 4K60 versus about 50 MB at 360p30 (derived from cvvdp.c), so the 91% memory saving measured at 360p is not a general figure.
- When you need difference heatmaps or other per-pixel output: cvvdp.h returns only a scalar JOD and raw quality value.
- When GPU throughput matters: there is no GPU path; Vship (GPU CVVDP, SSIMULACRA2, Butteraugli, now moved from GitHub to Codeberg) is the project fcvvdp was derived from.

## How it is fast

It runs the whole CVVDP pipeline (display model, RGB to XYZ to DKL, FIR temporal filtering over a ring buffer of about 0.25 s of frames, Gaussian/Laplacian pyramid, CSF LUT weighting, cross-channel masking, Minkowski pooling) as float32 C instead of PyTorch, with preallocated, reused pyramid scratch buffers, which is where the roughly 90 MB vs 1.03 GB RSS comes from. A pthread pool splits each stage into chunks within a frame (intra-frame data parallelism; frames stay sequential). Current code adds hand-written AVX2+FMA kernels chosen at run time by cpuid and NEON kernels on aarch64, built with -O3 -ffast-math. The README benchmark (commit 6ce3696, 2026-03-10) predates those SIMD kernels (PR #14, merged 2026-05-22), so the published speedup came from the plain C pipeline plus task threading.

## Compared with alternatives

None of the catalogued video-audio siblings is a quality metric: dav1d, Kvazaar, VVenC, SVT-AV1 and the resamplers are codecs and filters. Use fcvvdp to score their output on CPU (for example preset or bitrate sweeps) when CVVDP is the target metric and a Python/PyTorch stack is unwanted.

## Integration

| | |
|---|---|
| **Form** | static lib (libcvvdp.a + cvvdp.h) plus fcvvdp CLI; optional FFmpeg n8.0 filter patch |
| **Dependencies** | library: libc and pthreads only; CLI: libspng and simpleimgio fetched as Zig packages (build.zig.zon) |
| **Minimum toolchain** | Zig 0.16.0 (minimum_zig_version in build.zig.zon); C sources compiled -std=c23 -O3 -ffast-math by Zig's bundled clang. No CMake or Makefile is provided. |
| **Platforms** | x86-64 (AVX2+FMA kernels selected at run time, portable C fallback), aarch64 (NEON); macOS, Linux and Unix-like systems; Windows unsupported |
| **Thread safety** | not documented; each FcvvdpCtx owns its ring buffers, scratch buffers and worker pool (up to 32 threads), so use one context per concurrent stream; SIMD dispatch is initialized once via pthread_once |
| **Drop-in for the baseline** | partial — same metric, display presets and JOD scale, but a different CLI (-m fhd instead of --display standard_fhd) and a C API instead of the Python package; scalar JOD only, and parity is checked against Vship/FFVship, not the Python reference |

## Gotchas

- The README timings (commit 6ce3696, 2026-03-10) ran code with scoring bugs fixed later: plain gamma 2.4 instead of the piecewise sRGB curve (commit e123ffe, 2026-06-21, 'Incurs a small speed penalty (\~3-4% worst-case)'), and PR #19 (2026-09-22) fixes for an inverse-RFFT bug that erased half of each temporal kernel, reversed CSF interpolation weights, an inaccurate log approximation, RGB-to-XYZ coefficients and Y4M range handling (errors of 0.155 and 0.221 JOD against FFVship before). The same commit also predates AVX2/NEON, runtime dispatch and the 2026-07-13 '\~20% faster' CSF change, so the current speed against Python cvvdp has not been measured by anyone.
- build.zig passes no -mavx2/-mfma for cvvdp_avx2.c and cvvdp_avx2.h has no per-function target attributes, so the AVX2 kernels compile because Zig targets the native CPU by default; that also compiles the C fallback for the build host, so runtime cpuid dispatch does not by itself make a natively built binary portable, and a -Dcpu=baseline distribution build is not documented.
- Everything is built with -ffast-math, and cvvdp_compute_norm sums per-thread partials when a pool is active, so low-order digits of the score can differ between -t 1 and -t N or across compilers.
- The CLI decodes Y4M and converts YUV to RGB on the main thread between frames (threading covers only the metric stages), requires equal frame counts and dimensions, and reads no other video container; doc/cvvdp.md still describes the sRGB decode as 'approx. 2.4 power'.

## Known shortcomings

- Off-baseline (a video-quality metric, not a codec). The README poop run on an i7-13700K matches the record but there is no benchmark script or clip, and the 2026-03-10 numbers predate PR #19 (2026-09-22), which fixed scoring bugs of up to 0.22 JOD against FFVship.
- Enricher (e108, 2026-10-05): the README numbers (6ce3696, 2026-03-10) ran code with a second scoring bug the verifier missed: plain gamma 2.4 instead of the piecewise sRGB transfer, fixed by e123ffe (2026-06-21, about 3-4% slower worst case), plus the PR #19 bugs; the measured code also predates the AVX2/NEON kernels (PR #14), runtime dispatch (PR #17) and the 'about 20% faster' CSF, so current speed against Python cvvdp is unmeasured. build.zig sets no -mavx2/-mfma or target attributes and relies on Zig's native target (portable build undocumented); -ffast-math with per-thread partial sums, so the score varies with -t; Windows unsupported (#6 not planned); memory grows with resolution x fps (about 3.4 GB at 4K60, derived), so the 91% memory saving is a 360p figure; scalar JOD only. Tier C holds (numbers from code later fixed for correctness).

## Caveats and trade-offs

Off the category baselines: a perceptual quality metric compared with the Python ColorVideoVDP reference, not a codec. First-party single-clip benchmark (302 frames of 360p, fm360p.y4m not shipped, no benchmark script in the repo). The reference ran as 'cvvdp (multithreaded)' with PyTorch version and device unstated; 777G cycles over 19.1 s is about 40G cycles/s, consistent with several CPU cores busy (derived from page data), and its wall time includes Python/PyTorch start-up and video decoding, which the README does not separate. Output equivalence is not shown in the README: PR #19 ('vship parity fixes', 2026-09-22) fixed an inverse-RFFT initialization bug that erased half of each temporal kernel, CSF interpolation weights, RGB-to-XYZ coefficients and Y4M colour range, which had produced errors of 0.155064 and 0.220898 JOD against FFVship on two clips (about 0.000002 after the fix). The README timings (2026-03-10) were measured on the pre-fix code; the PR reports only 1-2% runtime change from the fix, and a 2026-07-13 commit claims about 20% faster CSF weighting, so current timings differ. Parity is checked against Vship/FFVship, not directly against the Python cvvdp baseline. The 8-thread run executes 21.6% more instructions than the reference. The README's '28% faster' and '221% faster' are wall-time ratios 19.1/14.9 = 1.28x and 19.1/5.94 = 3.22x. Derived from Vship (MIT). C core with Zig build and CLI; GitHub's language bar was not visible.

Library (libcvvdp with cvvdp.h) plus CLI and an FFmpeg filter patch, so usable from C++. It is a quality metric, not a codec, so it only replaces the reference CVVDP scorer. AVX2 and NEON kernels plus a portable C path; build needs the Zig toolchain (src has C files plus main.zig). Supports sRGB PNG, PNM/PAM, QOI and Y4M input.

## Maintenance

Active (82 commits, v0.4.0, last commit 2026-09-22) single-company project (Halide Compression) under Apache-2.0; the core is one 2,069-line cvvdp.c plus SIMD headers, small enough to vendor into a C/C++ build if you replace the Zig build.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The README poop run (3 runs each, Linux, Core i7-13700K) compares fcvvdp -t 1 and -t 8 against the Python cvvdp reference and all quoted numbers are on the page, but there is no benchmark script, the input clip is not shipped, the build toolchain at the time and the reference's PyTorch version and device are unstated, so it is first-party C. The numbers (commit 6ce3696, 2026-03-10) were measured on code that PR #19 (2026-09-22) later fixed for scoring bugs, which also keeps it at C.
- **Verifier notes:** Keep with the off-baseline shortcoming. Numbers predate the PR #19 correctness fixes (scores were off by up to 0.22 JOD against FFVship at benchmark time); no repo-level score comparison against the Python cvvdp reference exists. License Apache-2.0, 73 stars, 10 forks, last commit 2026-09-22 confirmed via github.com pages (gh/api not usable for other repos here).
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** first-party README timings
- **Pages the verifier opened:**
  - <https://github.com/halidecx/fcvvdp>
  - <https://raw.githubusercontent.com/halidecx/fcvvdp/HEAD/README.md>
  - <https://raw.githubusercontent.com/halidecx/fcvvdp/HEAD/doc/cvvdp.md>
  - <https://github.com/halidecx/fcvvdp/commits>
  - <https://github.com/halidecx/fcvvdp/commits/main/README.md>
  - <https://github.com/halidecx/fcvvdp/blame/main/README.md>
  - <https://github.com/halidecx/fcvvdp/pull/19>
  - <https://github.com/halidecx/fcvvdp/issues?q=is%3Aissue>
- **Sources the enricher read:**
  - <https://github.com/halidecx/fcvvdp>
  - <https://raw.githubusercontent.com/halidecx/fcvvdp/HEAD/README.md>
  - <https://raw.githubusercontent.com/halidecx/fcvvdp/HEAD/doc/cvvdp.md>
  - <https://raw.githubusercontent.com/halidecx/fcvvdp/HEAD/build.zig>
  - <https://raw.githubusercontent.com/halidecx/fcvvdp/HEAD/build.zig.zon>
  - <https://raw.githubusercontent.com/halidecx/fcvvdp/HEAD/src/cvvdp.h>
  - <https://raw.githubusercontent.com/halidecx/fcvvdp/HEAD/src/cvvdp.c>
  - <https://raw.githubusercontent.com/halidecx/fcvvdp/HEAD/src/internal.h>
  - <https://raw.githubusercontent.com/halidecx/fcvvdp/HEAD/src/util.h>
  - <https://raw.githubusercontent.com/halidecx/fcvvdp/HEAD/src/cvvdp_avx2.c>
  - <https://raw.githubusercontent.com/halidecx/fcvvdp/HEAD/src/cvvdp_avx2.h>
  - <https://raw.githubusercontent.com/halidecx/fcvvdp/HEAD/src/cvvdp_c.h>
  - <https://raw.githubusercontent.com/halidecx/fcvvdp/HEAD/src/main.zig>
  - <https://raw.githubusercontent.com/halidecx/fcvvdp/HEAD/patches/0001-feat-fcvvdp-support.patch>
  - <https://github.com/halidecx/fcvvdp/tree/main/src>
  - <https://github.com/halidecx/fcvvdp/pull/19>
  - <https://github.com/halidecx/fcvvdp/commits/main>
  - <https://github.com/halidecx/fcvvdp/commits/main?after=98bd21a7a876be29ba06a29325b03624047ee850+34>
  - <https://github.com/halidecx/fcvvdp/commit/e123ffe>
  - <https://github.com/halidecx/fcvvdp/commit/e123ffe.patch>
  - <https://github.com/halidecx/fcvvdp/issues?q=is%3Aissue>
  - <https://github.com/halidecx/fcvvdp/issues/16>
  - <https://github.com/halidecx/fcvvdp/issues/6>
  - <https://github.com/halidecx/fcvvdp/pulls?q=is%3Apr>
  - <https://github.com/Line-fr/Vship>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/halidecx/fcvvdp`) · [data/wave10/enrich/raw/github_com_halidecx_fcvvdp.json](../../../data/wave10/enrich/raw/github_com_halidecx_fcvvdp.json) (enrichment confidence 0.72)

</details>
