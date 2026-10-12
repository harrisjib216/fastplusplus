# GPU scanline path rendering (Li, Hou, Zhou 2016)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [2D rasterizers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++ (CUDA, OpenGL)` · `MIT` · 🔴 abandoned

> Research code for the SIGGRAPH Asia 2016 CUDA and OpenGL scanline path renderer; the abstract claims about 2.5x over prior GPU path renderers.

| | |
|---|---|
| **Beats** | state-of-the-art GPU path renderers (exact baselines not confirmed from an opened source) |
| **Claimed result** | Snippet only (abstract as returned by search for the ACM and ResearchGate pages): consistent 2.5x speedup over state-of-the-art alternatives for high-quality rendering at Ultra HD resolution, more than 30x in extreme cases, and a consistent 10x speedup on animated input. The compared systems and GPU model were not seen. |
| **Workload** | GPU path rendering of large vector scenes at Ultra HD resolution with high-quality anti-aliasing, parallelized over boundary fragments with non-boundary pixels filled as horizontal spans (SIGGRAPH Asia 2016, ACM TOG 35(6)). |
| **Metric** | throughput |
| **Hardware** | NVIDIA GPU with CUDA sm_50 and OpenGL 4.5; tested with NVIDIA driver 368.81 on 64-bit Windows 10 (per repo README) |
| **Compiler and flags** | Visual Studio 2013, CUDA 7.5 (per repo README; pre-built binary) |
| **Adoption** | 33 stars, 9 forks; cited as the basis of the sparse-strip path rendering work in linebender/vello (issue #670) |
| **Last commit** | 2017-07-03 |
| **Links** | [repository](https://github.com/Mochimazui/gpu-scanline-path-rendering) · [benchmark](https://dl.acm.org/doi/10.1145/2980179.2982434) |

## Verdict

The only numbers come from search-result text of the abstract (ACM TOG 35(6), 2016): a consistent 2.5x speedup over 'state-of-the-art alternatives' for high-quality rendering at Ultra HD, more than 30x in extreme cases, and 10x on animated input. The compared systems and the GPU were not readable here; search snippets only associate NVpr and MPVG with the paper. The repo can reproduce this renderer's own frame times but contains no baseline to compare against.

## Use it when

- Studying or porting a GPU path-filling algorithm. The kernels are a readable reference for the boundary-fragment plus span approach that linebender/vello's sparse-strip work (issue #670) cites as 'boundary fragment merge'.
- Reproducing the paper's GPU timings on the 13 MPVG scenes (boston, car, contour, embrace, hawaii, paper-1/2, paris-30k/50k/70k, tiger, reschart, chord) with working_directory/run.rb on an NVIDIA GPU under Windows.
- High-quality anti-aliasing (32 samples per pixel) of large static vector scenes at high resolution, where per-pixel winding work dominates other GPU methods.
- Scenes animated on the GPU: an --animation mode re-renders perturbed input every frame, the case behind the abstract's 10x claim for animated input.

## Skip it when

- Any production use. The code is a 4-commit research prototype last changed 2017-07-03, with no tests, no releases and no issue or PR activity.
- Non-NVIDIA, non-Windows or headless targets. It needs CUDA, OpenGL 4.5 and a 32-sample multisample texture, and it times with QueryPerformanceCounter/LARGE_INTEGER. The only build files are a Visual Studio 2013/2015 project importing the CUDA 7.5 build customization.
- General SVG. The README says only a subset of SVG features works (see the paper). The scene model in svg.cpp covers path fills with nonzero/evenodd rules, solid colours, linear and radial gradients, and strokes (with a --stroke-to-fill option).
- As a drop-in for Skia, Cairo or Blend2D. It has no drawing-context API, and none of those CPU renderers is compared in any source opened here.
- Very large scenes or resolutions without tuning. A fixed 256 MB CUDA scratch pool throws 'cuda_cached_allocator: reserved memory exhausted' when it overflows, and the fragment texture is a compile-time 4096x4096.

## How it is fast

The work runs over boundary fragments (pixels the path outline crosses), not over all covered pixels. Curves are cut into monotonic pieces at pixel rows, and each piece emits fragments with per-sample coverage masks (k_make_intersection_0/1, k_gen_fragment_and_stencil_mask). A segmented sort orders the fragments by (y, x) within each path (Modern GPU segmented sort), and a scan gives winding numbers. Fragments are then merged, and the interior runs between them become horizontal spans, as in a CPU scanline rasterizer. OpenGL finally draws the merged fragments, using gl_SampleMask from a precomputed mask table, and the spans as quads into a 32-sample multisample target. Interior pixels therefore need no per-pixel winding computation, which is where the abstract's speedup at Ultra HD resolution comes from.

## Compared with alternatives

Pick it over NV_path_rendering (driver extension, hardware MSAA) or vkvg only to study or port the scanline boundary-fragment algorithm on NVIDIA hardware. For shipping code, Vello (which builds its sparse-strip design on this paper) or a CPU renderer such as Blend2D is the practical choice.

## Integration

| | |
|---|---|
| **Form** | source-drop (Visual Studio solution building gpu-scanline.exe; a pre-built x64 binary is described in the README) |
| **Dependencies** | CUDA 7.5/8.0 with Thrust, Modern GPU (vendored), SDL 2.0.3 and Boost 1.60 (the README says to download them with test data from the project site), glm, stb, rapidxml, glLoadGen-generated GL loader |
| **Minimum toolchain** | Visual Studio 2013 (v120 toolset; v140 in one configuration), CUDA 7.5 build customization; device code is generated for compute_20/sm_20 and sm_52 |
| **Platforms** | 64-bit Windows 10 with an NVIDIA GPU (README: CUDA sm_50 and OpenGL 4.5; tested on driver 368.81) |
| **Thread safety** | Not thread-safe: there is one global rasterizer and one global bump allocator, the vendored allocator comment says it is not thread-safe, and all state is bound to one OpenGL context. |
| **Drop-in for the baseline** | no |

## Gotchas

- The README warns that the behaviour of gl_SampleMask changed around NVIDIA driver 368.22, so drivers on the other side of that change may render incorrectly. Output correctness depends on the driver version.
- The repo's benchmark (vg_main.cpp benchmark()) renders 16 warm-up frames, then reports the minimum and the mean wall-clock time over 256 frames of rasterize(), which ends in glFinish(). Scene data is already resident on the GPU, so parsing and upload are excluded and only the per-frame transform and rasterization are timed. No baseline renderer and no results are committed.
- Shader files are loaded at runtime from ./shader/R_cut_A_stencil/ relative to the working directory, so the exe must run from working_directory.
- Building with a current CUDA toolkit means editing the project's Code Generation setting (compute_20/sm_20 and sm_52); the README itself tells users to match it to their device.

## Known shortcomings

- Tier C on snippet-only numbers: the ACM TOG 35(6) 2016 paper (DOI 10.1145/2980179.2982434) is blocked here, so the 2.5x / &gt;30x / 10x figures come from search snippets of the abstract; the repo's run.rb driver times only this renderer with no baseline. Code last touched 2017-07-03 (research prototype). Retier to B once the paper's comparison tables (and whether Skia or Cairo appear in them) are read.
- Windows plus NVIDIA demo application with no library API. The repo harness runs 16 warm-up and 256 timed frames (min and mean wall clock with glFinish) with the scene resident on the GPU and no baseline; a fixed 256 MB CUDA pool throws when exhausted. The TOG paper remains unreachable here, so its baselines are unconfirmed.

## Caveats and trade-offs

Paper itself (dl.acm.org, kunzhou.net, researchgate, the IMPA thesis that discusses it) is blocked, so the compared systems, per-scene timings and GPU model were not seen; the numbers are from search summaries of the abstract. The named baselines are probably NV_path_rendering and MPVG (search results discuss both alongside this paper) but that is unconfirmed, so baseline_in_list stays false and none of the category baselines (Skia, Cairo, Blend2D) is confirmed as compared. The repo ships a Ruby benchmark driver (working_directory/run.rb) that times only this renderer on the 13 MPVG scenes and writes timing CSVs to ./result, but no results are committed and no baseline renderer is included; dependencies and test data must be downloaded from gaps-zju.org. Windows-only Visual Studio 2013/2015 + CUDA 7.5/8.0 project; README warns that NVIDIA drivers older than 368.22 handle gl_SampleMask differently and may render incorrectly. Four commits, last 2017-07-03; abandoned.

Windows plus NVIDIA only (CUDA, Thrust, Modern GPU segmented sort); research prototype with SDL, Boost and RapidXML dependencies; README warns gl_SampleMask behavior changed after driver 368.22.

## Maintenance

Abandoned research code (4 commits, last 2017-07-03) under the MIT licence (Zhejiang University). It is copyable, but it is tied to Windows, NVIDIA and a 2016 CUDA/Visual Studio toolchain, and its value now is mainly as a reference implementation of the algorithm.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The paper (Li, Hou, Zhou, ACM TOG 35(6), SIGGRAPH Asia 2016) is real and peer reviewed (ACM DOI 10.1145/2980179.2982434 and dblp entry seen in search results), but ACM, ResearchGate and kunzhou.net are blocked, so the 2.5x / &gt;30x / 10x figures were seen only as search snippets of the abstract; snippet-only numbers cap at C. The repo's benchmark driver working_directory/run.rb times only this renderer (13 MPVG scenes, 8/32 samples, 1x/2x size) and contains no baseline renderer or results, so it cannot lift the tier.
- **Verifier notes:** Real peer-reviewed paper with MIT code (LICENSE: MIT, Zhejiang University 2016-2017); tier stays C only because the paper is unreachable here. A paper-access retier could move it to B once the comparison tables (and whether Skia or Cairo appear in them) are read.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** paper tables (blocked)
- **Pages the verifier opened:**
  - <https://github.com/Mochimazui/gpu-scanline-path-rendering>
  - <https://github.com/Mochimazui/gpu-scanline-path-rendering/commits>
  - <https://github.com/Mochimazui/gpu-scanline-path-rendering/tree/master/working_directory>
  - <https://raw.githubusercontent.com/Mochimazui/gpu-scanline-path-rendering/HEAD/README.md>
  - <https://raw.githubusercontent.com/Mochimazui/gpu-scanline-path-rendering/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/Mochimazui/gpu-scanline-path-rendering/HEAD/working_directory/run.rb>
  - <https://raw.githubusercontent.com/Mochimazui/gpu-scanline-path-rendering/HEAD/working_directory/vg_default.cfg>
  - <https://github.com/linebender/vello/issues/670>
- **Sources the enricher read:**
  - <https://github.com/Mochimazui/gpu-scanline-path-rendering>
  - <https://github.com/Mochimazui/gpu-scanline-path-rendering/tree/master/gpu-scanline>
  - <https://raw.githubusercontent.com/Mochimazui/gpu-scanline-path-rendering/HEAD/README.md>
  - <https://raw.githubusercontent.com/Mochimazui/gpu-scanline-path-rendering/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/Mochimazui/gpu-scanline-path-rendering/HEAD/working_directory/run.rb>
  - <https://raw.githubusercontent.com/Mochimazui/gpu-scanline-path-rendering/HEAD/working_directory/vg_default.cfg>
  - <https://raw.githubusercontent.com/Mochimazui/gpu-scanline-path-rendering/HEAD/gpu-scanline/gpu-scanline.vcxproj>
  - <https://raw.githubusercontent.com/Mochimazui/gpu-scanline-path-rendering/HEAD/gpu-scanline/src/vg_main.cpp>
  - <https://raw.githubusercontent.com/Mochimazui/gpu-scanline-path-rendering/HEAD/gpu-scanline/src/vg_config.cpp>
  - <https://raw.githubusercontent.com/Mochimazui/gpu-scanline-path-rendering/HEAD/gpu-scanline/src/vg_container.cpp>
  - <https://raw.githubusercontent.com/Mochimazui/gpu-scanline-path-rendering/HEAD/gpu-scanline/src/svg.cpp>
  - <https://raw.githubusercontent.com/Mochimazui/gpu-scanline-path-rendering/HEAD/gpu-scanline/src/svg_loader.cpp>
  - <https://raw.githubusercontent.com/Mochimazui/gpu-scanline-path-rendering/HEAD/gpu-scanline/src/timer.h>
  - <https://raw.githubusercontent.com/Mochimazui/gpu-scanline-path-rendering/HEAD/gpu-scanline/src/rasterizer/R_cut_A_mask_comb_scanline/ras_cut_mask_comb_scanline.cpp>
  - <https://raw.githubusercontent.com/Mochimazui/gpu-scanline-path-rendering/HEAD/gpu-scanline/src/rasterizer/R_cut_A_mask_comb_scanline/ras_cut_mask_comb_scanline.cu>
  - <https://raw.githubusercontent.com/Mochimazui/gpu-scanline-path-rendering/HEAD/gpu-scanline/src/rasterizer/R_cut_A_mask_comb_scanline/ras_cut_mask_comb_scanline.h>
  - <https://raw.githubusercontent.com/Mochimazui/gpu-scanline-path-rendering/HEAD/gpu-scanline/src/rasterizer/shared/ras_base.cpp>
  - <https://raw.githubusercontent.com/Mochimazui/gpu-scanline-path-rendering/HEAD/gpu-scanline/src/rasterizer/shared/ras_base.h>
  - <https://raw.githubusercontent.com/Mochimazui/gpu-scanline-path-rendering/HEAD/gpu-scanline/src/rasterizer/shared/ras_define.h>
  - <https://raw.githubusercontent.com/Mochimazui/gpu-scanline-path-rendering/HEAD/gpu-scanline/src/rasterizer/shared/ras_qm_mask.cu>
  - <https://raw.githubusercontent.com/Mochimazui/gpu-scanline-path-rendering/HEAD/gpu-scanline/src/cuda/cuda_cached_allocator.cpp>
  - <https://raw.githubusercontent.com/Mochimazui/gpu-scanline-path-rendering/HEAD/gpu-scanline/src/cuda/cuda_cached_allocator.h>
  - <https://github.com/linebender/vello/issues/670>
  - <https://github.com/linebender/vello/issues/49>
  - WebSearch: "Efficient GPU path rendering using scanline rasterization" (result snippets for dl.acm.org/doi/10.1145/2980179.2982434, dblp, kunzhou.net/zjugaps/pathrendering, researchgate)
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/mochimazui/gpu-scanline-path-rendering`) · [data/wave10/enrich/raw/github_com_mochimazui_gpu_scanline_path_rendering.json](../../../data/wave10/enrich/raw/github_com_mochimazui_gpu_scanline_path_rendering.json) (enrichment confidence 0.6)

</details>
