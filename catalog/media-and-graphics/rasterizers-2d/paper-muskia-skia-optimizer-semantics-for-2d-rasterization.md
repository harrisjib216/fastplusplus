# muSkia Skia optimizer (Semantics for 2D Rasterization)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [2D rasterizers](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Study only · `Lean (formal semantics); implementation language unknown` · `no license` · ⚪ unknown

> Lean-verified peephole optimizer for Skia command streams; 1.12x geomean raster speedup over Skia Graphite on Chrome-generated pictures.

| | |
|---|---|
| **Beats** | Skia (its most modern GPU backend) |
| **Claimed result** | Peer-reviewed (OOPSLA2 2026, final evaluation): 1.12x geomean (max 3.04x) on 139 SaveLayer-bearing Skia pictures captured from Chrome on the top 100 sites, Graphite/Metal backend on an Apple M2, nanobench median of 25 runs with bootstrap 95% CI; Ganesh on the M2 1.08x; Intel i7-8700K with CoffeeLake-S GT2 1.14x (Graphite) and 1.07x (Ganesh) on 143 recaptured pictures; the next 100 sites 1.18x on 144 pictures with the passes frozen; optimisation time at most 0.03 ms per picture. The arXiv v1 abstract's 18.7% over 99 programs and 32 us optimisation time are superseded. |
| **Workload** | Rasterization time of 99 Skia programs gathered from the top 100 websites, after an optimizer driven by a mechanized formal semantics of Skia (canvas state, layer stack, blending, color filters) rewrites them. |
| **Metric** | latency |
| **Hardware** | 8-core Apple M2 (16 GB), Graphite/Metal and Ganesh backends; Intel i7-8700K with CoffeeLake-S GT2 integrated GPU. |
| **Compiler and flags** | Skia f931a2e built with Clang 17.0.0 -O3 -flto=thin (M2); Clang 18.1.3 on the Intel machine; nanobench, median of 25 runs with bootstrap confidence intervals. |
| **Links** | [benchmark](https://github.com/bhargavkulk/skia-paper/blob/main/evaluation.tex) |

## Verdict

Peer-reviewed first-party measurement (PACMPL OOPSLA2 2026, article 339), read from the camera-ready LaTeX in the first author's public skia-paper repo. On an 8-core Apple M2 (16 GB) with Skia f931a2e built by Clang 17.0.0 -O3 -flto=thin, Graphite/Metal nanobench playback of 139 SaveLayer-bearing pictures from Chrome on the top 100 sites (median of 25 runs, bootstrap 95% CI) gives a 1.12x geomean (max 3.04x). The other runs: Ganesh on the M2 1.08x; Intel i7-8700K with CoffeeLake-S GT2 (Clang 18.1.3) 1.14x Graphite and 1.07x Ganesh on 143 recaptured pictures; the next 100 sites 1.18x on 144 pictures with the passes frozen.

## Use it when

- Skia clients that record SkPictures/SkRecords before playback (browser engines, compositors, picture-replay tools) and whose command streams nest SaveLayers for opacity, masks or filters.
- Web-content rendering where Chrome-style output uses SrcOver or DstIn layers for clipping and masking: the paper's largest gains were 3.04x on a vimeo.com layer (three rewrites chained) and 2.41x on dzen.ru (gradient-mask rewrite).
- Research or tooling that needs a machine-checked definition of Skia's layer, blend and clip semantics to prove a draw-list rewrite correct before shipping it.
- GPU backends, Graphite in particular: measured gains were higher there (1.12x on Apple M2 Metal, 1.14x on an Intel CoffeeLake-S GT2 integrated GPU) than on legacy Ganesh (1.08x and 1.07x).

## Skip it when

- As a faster rasterizer: it does not touch Skia's path filling, shaders or GPU pipeline, so pictures without SaveLayers gain nothing and pay the optimizer pass (the RQ3 total-time CDF shows more slowdowns for exactly those).
- Pixel-exact pipelines: the rewrites are proved over real-valued colours, so anti-aliasing and rounding may change. 25 of 139 benchmark pictures had pixels differing by more than 1% in a channel (judged anti-aliasing by eye).
- Programs that use mask filters, blurs, image filters, SkSL shaders or bitmap features: muSkia does not formalize these, the passes give up on unmodelled commands, and only 41 of 139 pictures could be converted for translation validation.
- Legacy Ganesh with complex clip paths: the DstIn-to-Clip rewrite slowed avast.com layer 0 significantly on Ganesh/Intel; Graphite/Intel showed three statistically significant slowdowns (intuit.com layer 15, two gravatar.com layers).
- Production use today: the code is a research fork of Skia (commit f931a2e, between milestones 143 and 144) shipped only as a Zenodo artifact, and per the first author Chrome and Skia had not agreed to upstream it as of June 2026.

## How it is fast

It removes or cheapens SaveLayer/Restore pairs, each of which costs an offscreen GPU surface plus a blend. The four rewrites are: drop opaque SrcOver SaveLayers that contain only SrcOver draws; turn a DstIn mask layer into a Clip; fold a luminance or colour filter into the draws it covers; and delete opaque gradient masks used by one Russian web framework (mail.ru, dzen.ru, yandex.ru). Each rewrite is a single linear pass driven by a stack of small state machines, one per open SaveLayer (SkOptPass&lt;MatchState&gt;, with an inline STArray&lt;8&gt; frame stack). Removed commands become NoOps, and insertions are buffered and merged in one scan, a technique the paper credits to WebKit B3's InsertionSet. Optimization took at most 0.03 ms per picture on the M2.

## Compared with alternatives

Pick it only when you are already on Skia and want fewer offscreen layers in recorded pictures without changing the rasterizer. Blend2D, ThorVG or Vello CPU replace the rasterizer and are the siblings to look at if raw fill speed is the problem, and the two approaches can stack.

## Integration

| | |
|---|---|
| **Form** | source-drop (patches in a research fork of Skia; Lean 4 proofs as a separate artifact) |
| **Dependencies** | Skia at commit f931a2e; Lean 4 for the semantics and translation validator; Python playwright scripts to capture .skp files from Chrome |
| **Minimum toolchain** | Built with Clang 17.0.0 (-O3 -flto=thin) on macOS and Clang 18.1.3 on Ubuntu 24.04.4 in the paper; a minimum is not documented |
| **Platforms** | Backend-agnostic, since it rewrites SkRecords before playback; evaluated on Graphite/Metal and Ganesh/OpenGL on an Apple M2, and on Graphite and Ganesh on Intel i7-8700K with CoffeeLake-S GT2 graphics |
| **Thread safety** | not documented (mutates an SkRecord in place) |
| **Drop-in for the baseline** | partial: it runs on Skia's own SkRecord type in front of unchanged backends, but only inside the authors' Skia fork, and it applies only to recorded pictures, not immediate-mode SkCanvas calls |

## Gotchas

- The catalogued 18.7% (99 programs, 32 us) is the March 2026 arXiv v1 abstract. The camera-ready paper re-ran with 25 nanobench runs per picture and reports a 1.12x geomean on 139 pictures, at most 0.03 ms to optimize, and up to 3.04x.
- The benchmark set keeps only Chrome layer pictures that contain SaveLayer. Only 51 of the 139 are rewritten at all, and 38 of those have 95% confidence intervals entirely above 1x. The geomean includes unrewritten pictures whose ratios (0.96x-1.09x) are noise.
- The numbers are per-layer .skp playback times in Skia's nanobench, with the optimization applied offline. They are not whole-page frame times inside Chrome, and Chrome's layer split differs by hardware, so each machine got its own capture.
- The SrcOver-SaveLayer rewrite requires the layer to be opaque, a side condition the Lean model tracks but the paper's simplified rules omit; removing a layer can also defeat Graphite's own first-draw clear optimization (intuit.com regression).

## Known shortcomings

- Paper-only entry (OOPSLA2 2026, ACM DOI 10.1145/3839471; arXiv 2603.23696) with no code found; arXiv, alphaXiv, the ACM DOI and Zenodo are all blocked here, so the 18.7% figure is snippet-only and the tier is D; reference only.
- Enricher (e127, 2026-10-05): the camera-ready paper (bhargavkulk/skia-paper, OOPSLA2 2026 article 339) supersedes the arXiv v1 abstract: 1.12x geomean on 139 SaveLayer-bearing Skia pictures (Graphite/Metal, Apple M2, Clang 17.0.0 -O3 -flto=thin, Skia f931a2e, nanobench median of 25 runs), Ganesh 1.08x, i7-8700K 1.14x/1.07x, next 100 sites 1.18x, max 3.04x, optimisation at most 0.03 ms; retiered D to B (retier-37). Only 51 of 139 pictures are rewritten (38 with CI above 1x) so the geomean includes unrewritten noise; per-layer skp playback, not page frame time; 25 of 139 pixel diffs above 1%; four significant slowdowns on Intel. Code only on Zenodo 21386615 (blocked); Skia fork not on GitHub and not upstreamed.

## Caveats and trade-offs

Snippet only: arXiv 2603.23696, alphaXiv, ResearchGate and the ACM DOI (10.1145/3839471, Proceedings of the ACM on Programming Languages vol. 10, OOPSLA2, October 2026, per search results) are egress-blocked, so only the abstract text from search results was seen; authors per search results are Bhargav Kulkarni, Henry Whiting and Pavel Panchekha (University of Utah). The 18.7% is an aggregate over 99 web-page Skia programs, not a per-scene range, and the optimizer is a rewrite pass in front of Skia rather than a rasterizer, so the speedup comes from removing redundant layers and state changes in Chrome's command streams. No code repository was found: Panchekha's GitHub only has skia and skia-python forks, and a GitHub-scoped WebSearch found nothing. A WebSearch answer summary (not a listed result) names a Zenodo artifact DOI 10.5281/zenodo.21386615; zenodo is blocked, so neither the DOI nor its contents were checked, and has_code stays false until someone opens it. The formal semantics is in Lean; the optimizer's implementation language is unknown. [retier] Final paper read from the camera-ready LaTeX (bhargavkulk/skia-paper); the ACM DOI 10.1145/3839471, arXiv 2603.23696 and Zenodo are egress-blocked here. Only 51 of the 139 pictures are rewritten at all (38 with a confidence interval above 1x), so the 1.12x geomean includes unrewritten noise; the benchmark is per-layer skp playback in nanobench, not page frame time; 25 of 139 outputs differ from Skia by more than 1% of pixels; four significant slowdowns on the Intel machine. The optimizer is a rewrite pass in front of Skia (removing redundant layers and state changes in Chrome's command streams), not a rasterizer; the formal semantics is in Lean. Code and the Skia fork are only in the Zenodo artifact 10.5281/zenodo.21386615 (not on GitHub, not upstreamed), so has_code stays false.

It is an optimizer over Skia programs plus a formal semantics, not a replacement rasterizer; the gain depends on Skia command streams containing rewritable layer and blend patterns.

## Maintenance

Research artifact (Zenodo record 21386615, not opened here because zenodo is blocked) accepted at OOPSLA 2026; no public GitHub repository for the Skia fork or the Lean code was found, and it is not upstreamed in Skia or Chrome, so treat it as a reference design rather than a library.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification C, tier now B.
- **Tier reason:** No reachable page carries a number: arXiv (2603.23696), alphaXiv, the ACM DOI, ResearchGate and zenodo are all egress-blocked, and the 18.7% over Skia's most modern GPU backend exists only in WebSearch snippets of the abstract. Per the batch rule this is a paper entry at D until the paper or its artifact can be read; the venue (PACMPL OOPSLA2 2026, per search results) would support B once the evaluation section is checked.
- **Retiered** D to B: Raised D to B. Enricher e127 (2026-10-05) read the camera-ready LaTeX of the peer-reviewed paper (PACMPL vol. 10, OOPSLA2, October 2026, article 339) in the first author's public repo github.com/bhargavkulk/skia-paper (evaluation.tex, macros.tex via raw.githubusercontent.com). The catalogued 18.7% / 99 programs / 32 us figures were the arXiv v1 abstract; the final evaluation reports a 1.12x geomean on 139 SaveLayer-bearing Skia pictures with stated hardware, compiler, flags, Skia commit and methodology. Not A: the optimizer code and Skia fork are only on Zenodo (10.5281/zenodo.21386615, blocked here) and not upstreamed, so the benchmark is not reproducible from public GitHub sources.
- **Verifier notes:** Real, peer-reviewed paper (OOPSLA 2026 per search results) kept as a reference paper entry at D per the batch note; not rejected for being unreachable. Retier candidate (likely B) once arXiv or the Zenodo artifact is reachable: check hardware, Skia backend (Graphite vs Ganesh) and whether the artifact carries the benchmark harness.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `caveats`, `hardware`, `compiler_and_flags`
- **Shortcomings recorded by:** peer-reviewed first-party (OOPSLA2 2026)
- **Pages the verifier opened:**
  - <https://github.com/pavpanchekha?tab=repositories&q=skia>
- **Sources the enricher read:**
  - <https://github.com/bhargavkulk?tab=repositories>
  - <https://github.com/bhargavkulk?tab=repositories&q=&type=fork>
  - <https://github.com/bhargavkulk/skia-paper>
  - <https://github.com/bhargavkulk/skia-paper/commits/main>
  - <https://raw.githubusercontent.com/bhargavkulk/skia-paper/main/main.tex>
  - <https://raw.githubusercontent.com/bhargavkulk/skia-paper/main/macros.tex>
  - <https://raw.githubusercontent.com/bhargavkulk/skia-paper/main/abstract.tex>
  - <https://raw.githubusercontent.com/bhargavkulk/skia-paper/main/introduction.tex>
  - <https://raw.githubusercontent.com/bhargavkulk/skia-paper/main/rewrites.tex>
  - <https://raw.githubusercontent.com/bhargavkulk/skia-paper/main/semantics.tex>
  - <https://raw.githubusercontent.com/bhargavkulk/skia-paper/main/compiler.tex>
  - <https://raw.githubusercontent.com/bhargavkulk/skia-paper/main/evaluation.tex>
  - <https://raw.githubusercontent.com/bhargavkulk/skia-paper/main/discussion.tex>
  - <https://raw.githubusercontent.com/bhargavkulk/skia-paper/main/references.bib>
  - <https://raw.githubusercontent.com/bhargavkulk/skia-paper/main/README.org>
  - <https://raw.githubusercontent.com/bhargavkulk/skia-paper/main/camera_ready_todos.org>
  - <https://raw.githubusercontent.com/bhargavkulk/skia-paper/main/Makefile>
  - <https://raw.githubusercontent.com/bhargavkulk/skia-paper/main/AGENTS.md>
  - <https://github.com/bhargavkulk/bhargavkulk.github.io>
  - <https://github.com/bhargavkulk/bhargavkulk.github.io/tree/main/content>
  - <https://raw.githubusercontent.com/bhargavkulk/bhargavkulk.github.io/main/content/index.org>
  - <https://raw.githubusercontent.com/bhargavkulk/bhargavkulk.github.io/main/content/blog/skia-retro.org>
  - <https://github.com/pavpanchekha/skia>
  - <https://github.com/droidkid/skia>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `paper:muskia-skia-optimizer-semantics-for-2d-rasterization`) · [data/wave10/enrich/raw/paper_muskia_skia_optimizer_semantics_for_2d_rasterization.json](../../../data/wave10/enrich/raw/paper_muskia_skia_optimizer_semantics_for_2d_rasterization.json) (enrichment confidence 0.8)

</details>
