# vapoursynth-nssfactory (CUDA BM3D)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Video and audio](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `GPL-2.0-only` · 🟢 active

> CUDA VapourSynth BM3D (plus NLM, WNNM and other NSS denoisers); first-party 1.15-1.25x spatial, 2.7-3.3x rolling temporal over bm3dcuda.

| | |
|---|---|
| **Beats** | VapourSynth-BM3DCUDA (bm3dcuda) |
| **Claimed result** | PR #23 description: 'bm3dcuda on the same harness: 636 fps; this branch 732 fps at the default 3 streams' (about 1.15x, derived from page data). The same PR reports its own before/after: Gray sigma 3 478 to 710 fps, Gray final 354 to 438 fps, YUV420 344 to 450 fps. |
| **Workload** | nss_cuda.BM3D at its default shape (block 8, group 8, sigma 3) on 1080p Gray float clips, 3 streams (the default at the time of PR #23; the current docs/api/bm3d.md gives num_streams default 1), RTX 5080, source frames served from VapourSynth's cache, A and B alternated, kernel times from Nsight Systems; bm3dcuda 'on the same harness'. The repo's docs/api/bm3d.md adds first-party figures for 1080p GRAYS, RTX 5080, one stream, measured 2026-10-06 against bm3dcuda with the same search: about 1.25x spatial with 32 VapourSynth threads (bounded by frame transfers; the kernels take the same time), rolling temporal 2.7x at radius 1 and 3.3x at radius 2 with 32 threads (1.4x with one thread; random access 1.15x with one thread and 2.2x with 32), and chroma=1 at YUV444 243, 238 and 229 fps (spatial, radius 1, radius 2) against bm3dcuda chroma=True 200, 94 and 65 fps. |
| **Metric** | throughput |
| **Hardware** | NVIDIA RTX 5080 (1080p); host CPU, driver and VapourSynth version not stated for these runs (the docs name an 'Emerald Rapids core' only for CPU-plugin timings) |
| **Compiler and flags** | CMake Release, C++20, nvcc from CUDA 12.4 or newer (release packages built with CUDA 12.9); native code for sm_75, sm_86, sm_89 and sm_120 plus compute_75 PTX; flags beyond Release not stated in the PR |
| **Adoption** | 1 star, 0 forks |
| **Last commit** | 2026-10-07 |
| **Links** | [repository](https://github.com/AmusementClub/vapoursynth-nssfactory) · [benchmark](https://github.com/AmusementClub/vapoursynth-nssfactory/pull/23) |

## Verdict

First-party only: PR #23 timed the default shape (block 8, group 8, sigma 3) on 1080p Gray float at 3 streams on an RTX 5080, A/B alternated in one process with source frames from VapourSynth's cache, reporting 732 fps against bm3dcuda's 636 fps 'on the same harness' (about 1.15x, derived from page data); docs/api/bm3d.md (2026-10-06, one stream, 1080p GRAYS) adds about 1.25x spatial and 2.7x/3.3x rolling temporal at radius 1/2 with 32 VS threads. Host CPU, driver, bm3dcuda build (cuda or rtc, BM3D or BM3Dv2) and bm3dcuda parameters are not stated and no timing harness is in the repository.

## Use it when

- Temporal BM3D (radius 1-2) on an NVIDIA Turing-or-newer GPU with frames rendered in order: first-party 2.7x (radius 1) and 3.3x (radius 2) over bm3dcuda at 1080p GRAYS with 32 VapourSynth threads.
- Two-stage BM3D in one call (final=1): the basic estimate stays on the device, first-party 303 to 730 fps at 1080p GRAYS spatial against the plugin's own two-call form.
- Colour BM3D (chroma=1) on YUV444 with a temporal radius: first-party 238 fps (radius 1) and 229 fps (radius 2) against bm3dcuda chroma=True at 94 and 65 fps.
- Pipelines that need GPU output identical from run to run (bm3dcuda is non-deterministic unless extractor_exp is set).
- Scripts that want NLM, WNNM, NCSR, NLH, TWSC or LSSC on the GPU from the same plugin and argument conventions as BM3D.

## Skip it when

- Spatial-only BM3D where bm3dcuda is already in place: the gain is about 1.15-1.25x and the docs say the kernels take the same time, the difference being frame-transfer pipelining.
- AMD, Intel or pre-Turing NVIDIA GPUs: CUDA only, sm_75 and newer (other sm_75+ archs run PTX through the driver JIT, untested); bm3dcuda also ships HIP builds and supports older NVIDIA parts.
- Anyone who needs a prebuilt CUDA binary or a stable API today: the only release (r0, a 2026-09-27 pre-release) has CPU builds only, and defaults changed within days (num_streams 3 to 1, temporal output from fat intermediate to finished frames).
- Memory-tight 4K temporal work: one stream needs about 1.1-1.8 GB at radius 1 and up to 3.4 GB for rolling final=1 at radius 2, and there is no default memory_limit_mb.
- Projects that cannot take GPL-2.0-only code (the FFTW-generated DCT codelets are GPL-2.0-or-later), or that need integer clip formats or bit-identical CPU/GPU output.

## How it is fast

For the default 8x8 block, group-of-8 shape one warp filters four groups with each lane holding a column of a group's patches in 64 registers, the 8x8 reference block sits in registers instead of shared memory, and the matcher keeps a single 64-bit (distance, index) key per candidate (PR #23: group filter 0.399 to 0.066 ms, matching 0.378 to 0.309 ms per frame in Nsight Systems). Aggregation happens inside the filter kernel with integer atomics on fixed-point sums, and host-device copies run outside the device stream. The bigger temporal gains come from a rolling mode that keeps a ring of window frames and the per-frame temporal sums on the device across chunks, so only finished frames are downloaded instead of a (2R+1)x2-plane intermediate; final=1 keeps the basic estimate on the device between the two BM3D stages.

## Compared with alternatives

Pick it over VapourSynth-BM3DCUDA on an NVIDIA RTX-class GPU when you run temporal or colour BM3D, want both stages in one call, or need deterministic output; keep bm3dcuda for AMD (HIP) or older NVIDIA GPUs, released binaries and a long track record. KNLMeansCL or av-denoise are the choice when NLMeans on any OpenCL/other GPU vendor is enough.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | VapourSynth API4 headers and runtime, CUDA toolkit (nvcc) 12.4 or newer, CMake 3.24+; the CPU plugin also fetches Highway 1.4.0 at configure time (skip with -DNSS_BUILD_CPU=OFF) |
| **Minimum toolchain** | C++20, CMake 3.24, nvcc 12.4+ (12.8+ for native sm_120 code); MSVC cl.exe as host compiler on Windows |
| **Platforms** | NVIDIA GPUs sm_75+ (native sm_75/86/89/120 cubins plus compute_75 PTX); Linux x86-64 and Windows hosts; prebuilt driver must support the CUDA release used to build (12.9 for release packages) |
| **Thread safety** | Runs as a VapourSynth filter under VS frame threading (the docs measure with 1 and 32 threads); each instance uses one device with num_streams (1-16) frames in flight and its own buffers; internal locking not documented |
| **Drop-in for the baseline** | partial: same filter concept and mostly the same argument names as bm3dcuda.BM3D, but a different namespace (nss_cuda), default bm_range 7 versus bm3dcuda's 9, sigma remapped through a BM3D effective-noise profile, chroma is an int, no fast or extractor_exp arguments, and radius &gt; 0 returns finished frames unless temporal_mode="legacy" |

## Gotchas

- Baseline mode is ambiguous for the temporal claims: bm3dcuda gained its own rolling temporal BM3Dv2 (temporal_mode, rolling_chunk 4, rolling_cache_chunks 1, rolling_cache_limit 16, the same names and defaults) in PR #35 of 2026-08-31 by the same developer (MysteryDove) and shipped it in R2.17 on 2026-09-26; the 2026-10-06 docs' 2.7x/3.3x figures do not say whether bm3dcuda ran BM3Dv2 rolling or the legacy BM3D + VAggregate path, so the record's caveat that bm3dcuda returns a fat intermediate holds only for its BM3D interface.
- Defaults are not equal work: nss_cuda.BM3D defaults to bm_range 7 (15x15 window) while bm3dcuda defaults to bm_range 9 (19x19, about 1.6x more candidates, derived); PR #23's 636 vs 732 fps line says only 'same harness', whereas the later docs say 'same search' and tests/cuda_compare.py passes bm_range explicitly for its PSNR column. No timing script for any bm3dcuda comparison is in the repo.
- Breaking behaviour changes land daily: since PR #26 (2026-10-05) nss_cuda.X(clip, radius=r) followed by VAggregate fails unless temporal_mode="legacy" is given, and PR #28 changed num_streams from 3 to 1 after the PR #23 measurement.
- Output agrees with the CPU plugin only to the 60 dB PSNR gate (not bit-identical) and rolling agrees with legacy + VAggregate to about 8 ulp for fused shapes; the worst reference case was at 73.5 dB before PR #23. nss_cuda is built with IEEE options (-O3 --fmad=true -prec-div=true -prec-sqrt=true -ftz=false), while bm3dcuda's documented build uses --use_fast_math.

## Known shortcomings

- First-party only: PR #23 numbers (636 vs 732 fps on an RTX 5080, about 1.15x derived) with no timing harness in the repo (cuda_compare.py checks PSNR only, stress_cuda.py is a memory soak); CPU, driver and the bm3dcuda build are unstated; the spatial gain comes from transfers while the kernels take the same time; the default stream count changed from 3 to 1 after the measurement and the README now quotes about 790 fps with no bm3dcuda figure. Work in progress, days old, 1 star, GPL-2.0-only.
- Enricher: since 2026-08-31 bm3dcuda has its own rolling temporal BM3Dv2 (PR #35 by the same developer, shipped in R2.17 on 2026-09-26) with the same parameter names and defaults, and the docs' 2.7x/3.3x temporal claim never says whether bm3dcuda ran BM3Dv2 rolling or the legacy BM3D plus VAggregate path, so the 'bm3dcuda returns a fat intermediate' caveat holds only for the old interface. nssfactory's default bm_range is 7 against bm3dcuda's 9 (about 1.6x fewer candidates, derived), PR #23's 'same harness' line names no bm3dcuda parameters, nss_cuda is built with IEEE flags while the bm3dcuda doc build uses --use_fast_math, no timing script, no released CUDA binary (r0 pre-release is CPU-only), and defaults changed within days (PR #26 temporal output, PR #28 streams 3 to 1).

## Caveats and trade-offs

First-party numbers in a PR body and in docs/api/bm3d.md; the timing harness that produced the 636 fps bm3dcuda figure is not in the repo (tests/cuda_compare.py runs bm3dcuda only for a clean-PSNR column, tests/cuda/stress_cuda.py is a device-memory soak, the tests/bench_\*.cpp files are CPU benchmarks, tools/ holds only a codelet generator), and host CPU, driver, bm3dcuda build (cuda or rtc variant) and bm3dcuda parameters are not stated, so tier C. The gain over bm3dcuda is modest at the default (about 1.15x, derived from page data) and the docs say the spatial case is bound by frame transfers while the kernels take the same time as bm3dcuda, so the spatial win comes from host-side pipelining rather than faster GPU work; the larger 2.7x and 3.3x wins are for the rolling temporal mode with 32 threads, which keeps the temporal sums on the device while bm3dcuda returns a fat intermediate for a separate aggregation step. The 732 fps bm3dcuda-comparison figure does not match the PR's own Gray sigma 3 after-figure (710 fps), so it was a separate run; the PR also reports its own before/after (478 to 710 fps Gray, 1.49x), so the bm3dcuda gap is recent: it was produced by PR #23, merged 2026-10-05. The stream default has since changed from 3 to 1 and the README now quotes about 790 fps for 1080p BM3D with one or three streams, with no bm3dcuda figure beside it. The 'final=1' gains (303 to 730 fps and so on) are against the plugin's own two-call form, not bm3dcuda. Repository is days old in its visible history (first visible commit 2026-10-04, 131 commits) and the README says the project is WIP and still calls CUDA a 'future route' although the CUDA plugin is documented, so numbers may change quickly. PSNR on its worst case improved from 73.5 to 138.9 dB after PR #23, so earlier output had larger numeric error; CUDA output is not bit-identical to the CPU plugin (60 dB gate). GPL-2.0-only per the CMakeLists SPDX header; the FFTW-generated DCT codelets are GPL-2.0-or-later. [retier] First-party PR #23 numbers on an RTX 5080 (636 vs 732 fps, about 1.15x derived) with no timing harness, CPU, driver or bm3dcuda build stated; bm3dcuda has shipped its own rolling temporal BM3Dv2 since R2.17 (2026-09-26, same developer) and the docs do not say which bm3dcuda path was timed; nssfactory defaults to bm_range 7 against bm3dcuda's 9 and is built with IEEE flags while bm3dcuda's doc build uses --use_fast_math. Days-old work in progress, defaults changed within days, no released CUDA binary, 1 star, GPL-2.0-only.

GPL-2.0 (the generated FFTW DCT codelets are GPLv2 or later), work in progress, GPU path needs a CUDA 12.9-capable driver and an NVIDIA GPU; constant Gray/YUV/RGB 32-bit float clips only. CUDA output matches the CPU plugin to 60 dB PSNR or better, not bit-for-bit. Default of 3 streams uses more device and pinned memory than one.

## Maintenance

Active single-author WIP (MysteryDove; 131 visible commits from 2026-10-04 to 2026-10-07, several merged PRs a day, 1 star, no issues filed) under GPL-2.0-only; copyable as source but there is no released CUDA build yet and defaults are still moving.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** PR #23 (merged 2026-10-05) states 'bm3dcuda on the same harness: 636 fps; this branch 732 fps at the default 3 streams' on an RTX 5080 at 1080p, and docs/api/bm3d.md adds first-party ratios against bm3dcuda (measured 2026-10-06); no timing harness is in the repo (tests/cuda_compare.py compares bm3dcuda PSNR only, tests/cuda/stress_cuda.py is a memory soak), and host CPU, driver, bm3dcuda build and bm3dcuda parameters are unstated, so first-party without methodology: C.
- **Verifier notes:** All PR #23 numbers (636 vs 732 fps, 478 to 710, 354 to 438, 344 to 450, PSNR 73.5 to 138.9 dB) and the docs/api/bm3d.md ratios appear as recorded. Shortcomings: first-party, no timing harness in the repo, CPU/driver/bm3dcuda build unstated, spatial gain from transfers not kernels, 1 star, WIP repo days old, stream default changed after the measurement.
- **Fields the verifier corrected:** `workload`, `caveats`
- **Shortcomings recorded by:** independent run with a published harness; same-parameter comparison against bm3dcuda BM3Dv2 rolling
- **Pages the verifier opened:**
  - <https://github.com/AmusementClub/vapoursynth-nssfactory/pull/23>
  - <https://github.com/AmusementClub/vapoursynth-nssfactory>
  - <https://github.com/AmusementClub/vapoursynth-nssfactory/commits>
  - <https://github.com/AmusementClub/vapoursynth-nssfactory/tree/master/tests>
  - <https://github.com/AmusementClub/vapoursynth-nssfactory/tree/master/tests/cuda>
  - <https://raw.githubusercontent.com/AmusementClub/vapoursynth-nssfactory/HEAD/docs/api/bm3d.md>
  - <https://raw.githubusercontent.com/AmusementClub/vapoursynth-nssfactory/HEAD/README.md>
  - <https://raw.githubusercontent.com/AmusementClub/vapoursynth-nssfactory/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/AmusementClub/vapoursynth-nssfactory/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/AmusementClub/vapoursynth-nssfactory/HEAD/tests/cuda_compare.py>
  - <https://raw.githubusercontent.com/AmusementClub/vapoursynth-nssfactory/HEAD/tests/cuda/stress_cuda.py>
- **Sources the enricher read:**
  - <https://github.com/AmusementClub/vapoursynth-nssfactory>
  - <https://raw.githubusercontent.com/AmusementClub/vapoursynth-nssfactory/HEAD/README.md>
  - <https://raw.githubusercontent.com/AmusementClub/vapoursynth-nssfactory/HEAD/docs/api/bm3d.md>
  - <https://raw.githubusercontent.com/AmusementClub/vapoursynth-nssfactory/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/AmusementClub/vapoursynth-nssfactory/HEAD/src/cuda/CMakeLists.txt>
  - <https://raw.githubusercontent.com/AmusementClub/vapoursynth-nssfactory/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/AmusementClub/vapoursynth-nssfactory/HEAD/tests/cuda_compare.py>
  - <https://github.com/AmusementClub/vapoursynth-nssfactory/pull/23>
  - <https://github.com/AmusementClub/vapoursynth-nssfactory/pull/26>
  - <https://github.com/AmusementClub/vapoursynth-nssfactory/pull/31>
  - <https://github.com/AmusementClub/vapoursynth-nssfactory/pull/32>
  - <https://github.com/AmusementClub/vapoursynth-nssfactory/pull/34>
  - <https://github.com/AmusementClub/vapoursynth-nssfactory/pull/40>
  - <https://github.com/AmusementClub/vapoursynth-nssfactory/commits/master>
  - <https://github.com/AmusementClub/vapoursynth-nssfactory/tree/master/tests>
  - <https://github.com/AmusementClub/vapoursynth-nssfactory/tree/master/tests/cuda>
  - <https://github.com/AmusementClub/vapoursynth-nssfactory/issues?q=is%3Aissue>
  - <https://github.com/AmusementClub/vapoursynth-nssfactory/releases>
  - <https://raw.githubusercontent.com/WolframRhodium/VapourSynth-BM3DCUDA/HEAD/README.md>
  - <https://github.com/WolframRhodium/VapourSynth-BM3DCUDA/commits>
  - <https://github.com/WolframRhodium/VapourSynth-BM3DCUDA/releases>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/amusementclub/vapoursynth-nssfactory`) · [data/wave10/enrich/raw/github_com_amusementclub_vapoursynth_nssfactory.json](../../../data/wave10/enrich/raw/github_com_amusementclub_vapoursynth_nssfactory.json) (enrichment confidence 0.6)

</details>
