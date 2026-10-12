# Rewrite it in Rust: A Computational Physics Case Study (Veytsman, Zhai, Ding, Sefkow)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Systems and safety](README.md)</sub>

**Tier C** (first-party claim) · Study only · `Rust` · `no license` · ⚪ unknown

> University of Rochester preprint: a CBET laser-plasma simulation written in Rust ran up to 5.6x faster than the group's C++ version.

| | |
|---|---|
| **Beats** | The authors' C++ implementation of the same physics simulation (compiler and flags not seen) |
| **Claimed result** | Per search snippets of the arXiv paper (paper not opened): Rust was at least 1.6x as fast as the C++ version in the smaller cases, and up to 5.6x faster on the large mesh on the EPYC machine; a parallel Rust version improved performance further. No per-case runtimes were seen. |
| **Workload** | A re-implementation, from C++ to Rust, of a laser-plasma interaction simulation of Cross Beam Energy Transfer (CBET, energy transfer where high-intensity laser beams cross in a plasma), run on test cases with different mesh sizes on more than one machine (one is an AMD EPYC system), plus a parallel Rust version. A snippet also mentions a comparison with an interpreted-language (MATLAB) version. |
| **Metric** | throughput (program runtime) |
| **Hardware** | Includes an AMD EPYC machine (model not seen; snippet only) |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | not stated |
| **Same optimization level** | not stated |
| **Adoption** | arXiv 2410.19146 (submitted 24 October 2024, physics.comp-ph), University of Rochester; discussed on lobste.rs; no peer-reviewed venue found |
| **Links** | [benchmark](https://arxiv.org/abs/2410.19146) |

## Verdict

Per search snippets only, the Rust CBET simulation ran at least 1.6x as fast as the authors' C++ version on smaller meshes and up to 5.6x faster on a large mesh (2500 x 2500 is the mesh named in one figure caption) on an AMD EPYC machine of unknown model, with compilers and flags unknown; a parallel Rust version was faster still, and whether the 5.6x figure is sequential is disputed in discussion.

## Use it when

- As an anecdote when weighing a C++ to Rust port of a mesh-based scientific code: a small group reported the Rust version was not slower, and was at least 1.6x faster on smaller cases per snippets.
- As a pointer that safe parallel Rust (the paper's parallel version) can speed a sequential physics kernel up further with little effort, if you plan to parallelise during the port anyway.
- Not as a library: there is nothing to link or vendor, so it only informs a language decision.

## Skip it when

- As evidence that Rust is generally faster than C++: same-algorithm studies point the other way (ASE 2022 'Towards Understanding the Runtime Performance of Rust' found Rust about 1.77x slower than C on average; arXiv 2209.09127 'Is Rust C++-fast?' found near parity with a small Rust deficit).
- To predict the gain for your own code: compilers, flags, CPU model, per-case runtimes and the reason for the gap were not seen, and no code exists to rerun it.
- As peer-reviewed evidence: it is an arXiv preprint; no journal or conference version was found.
- As a comparison of tuned C++: the C++ version was the group's own and was changed to resemble the Rust code (Lobsters snippet), so a tuned C++ implementation with its own data layout was never the baseline.

## How it is fast

Not documented in anything readable here: the paper (arxiv.org abs, html, pdf), its ResearchGate copy and every mirror tried are unreachable, so the authors' explanation was not read. The only concrete design difference reported, through search snippets of the Lobsters discussion, is data layout: the C++ version uses struct-of-arrays and the Rust version array-of-structs, and the authors argue this alone does not explain the gap. The same discussion says both versions were fresh implementations and that the C++ code was modified to resemble the Rust code, so any speedup mixes language, compiler (rustc versus an unnamed C++ compiler) and implementation choices.

## Compared with alternatives

Cite it only as a scientific-computing anecdote; for reproducible Rust-versus-C++ evidence prefer ckmeans (vendored Ckmeans.1d.dp C++ baseline, Criterion runs) or ixy-languages (same driver design in C and Rust, cycle counts), whose code and baselines can be checked.

## Integration

| | |
|---|---|
| **Form** | source-drop (not available: paper only, no public code found) |
| **Dependencies** | not documented |
| **Minimum toolchain** | not documented (rustc and C++ compiler versions not seen) |
| **Platforms** | not documented beyond an AMD EPYC test machine (model not seen) and at least one other machine |
| **Thread safety** | not documented (the parallel Rust version's threading approach was not seen) |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw: the two versions do not share a data layout (C++ struct-of-arrays, Rust array-of-structs, per a Lobsters comment summarised in a search snippet), so the measured gap is partly an implementation effect rather than a language effect; the authors reportedly argue layout alone does not explain it.
- Unresolved: the abstract (search snippet) says some test cases showed up to a 5.6x increase and that parallel Rust 'can further improve' performance, but a Hacker News commenter (snippet) read the paper as about 1.6x from the near-identical sequential port with the larger gain coming from the parallel Rust version. If 5.6x compares parallel Rust with sequential C++, it is not a language comparison at all.
- A Lobsters commenter (snippet) found the paper unclear about who wrote which implementation and saw no code link; two earlier searches and this pass (github.com topics 'cbet' and 'laser-plasma', author user pages) found no repository.
- A 1.6x to 5.6x gap between equally optimised sequential C++ and Rust is unusual; without flags (for example -O2 versus -O3, -ffast-math, aliasing assumptions) it cannot be attributed.

## Known shortcomings

- Preprint seen as a search snippet only (arXiv 2410.19146 blocked; at least 1.6x on small cases, 5.6x on a large mesh on EPYC) with no code found, flags and algorithm match unknown, probably a rewrite effect.
- Snippet-only entry: arxiv.org, ar5iv, alphaxiv, ADS and the other mirrors are unreachable here and no code was found on github.com. Per a Lobsters snippet the C++ uses struct-of-arrays and the Rust array-of-structs, and the C++ was edited to resemble the Rust code, so this is a rewrite effect. Unresolved: a Hacker News commenter reads the sequential port as about 1.6x with the 5.6x needing parallel Rust, while the abstract implies 5.6x is sequential; a figure caption mentions a 2500 x 2500 mesh. Enricher confidence 0.3; paper-access retier pending.

## Caveats and trade-offs

Snippet only: arxiv.org (abs, html and pdf) is blocked here (ENOTFOUND) and two searches found no public code for either the C++ or the Rust version. Compiler versions, optimisation flags, algorithm equivalence and the reason for the speedup are unknown, so same_algorithm, same_opt_level and why_faster stay null. A rewrite by the same group can carry design changes (data layout, algorithm fixes) that make it a rewrite effect rather than a language effect, and a 1.6x-5.6x gap between equally optimised C++ and Rust is unusual. Contrast: the ASE 2022 study 'Towards Understanding the Runtime Performance of Rust' (Zhang et al.) reports Rust 1.77x slower than C on average for same-algorithm micro-benchmarks, and 'Is Rust C++-fast?' (arXiv 2209.09127) reports Rust similar to C++ with a minor disadvantage. The paper is an arXiv preprint, so it is not counted as peer-reviewed. [retier] Enricher: per a Lobsters snippet the C++ uses struct-of-arrays and the Rust array-of-structs, and the C++ was edited to resemble the Rust code, so the gap is partly a rewrite effect. Unresolved: a Hacker News commenter reads the sequential port as about 1.6x with the 5.6x needing parallel Rust, while the abstract implies 5.6x is sequential; a figure caption mentions a 2500 x 2500 mesh. No public code found on github.com; enricher confidence 0.3.

Unknown; the study also reports a parallel Rust version.

## Maintenance

Reference-only arXiv preprint (2024) with no public code; the paper, its ResearchGate copy, the Lobsters and Hacker News threads and the authors' pages were all unreachable here, so this entry rests on search snippets and stays a candidate for a paper-access retier.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The paper (arXiv 2410.19146, a preprint; no peer-reviewed venue seen) could not be opened: arxiv.org fails with ENOTFOUND here, and two searches found no code repository. The numbers come from search snippets only, so the wave-14 snippet-only rule caps it at C, with compiler, flags, algorithm equivalence and mechanism all unknown.
- **Verifier notes:** The record is accurate as a snippet-only lead and stays at C. I added the arXiv URL (not opened) and the snippet detail of at least 1.6x on small cases and 5.6x on the large mesh on EPYC. Shortcomings for the orchestrator: no code, paper unreadable here, flags and algorithm equivalence unknown, a likely rewrite effect, and a preprint only. Worth a paper-access retier from an environment where arxiv.org is reachable.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `hardware`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-15 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Sources the enricher read:**
  - <https://github.com/wveytsman>
  - <https://github.com/ShuangZhai>
  - <https://github.com/topics/cbet>
  - <https://github.com/topics/laser-plasma>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `paper:rewrite-it-in-rust-a-computational-physics-case-study-veytsman-zhai-ding-sefkow`) · [data/wave14/enrich/raw/paper_rewrite_it_in_rust_a_computational_physics_case_study_veytsman_zhai_ding_sefkow.json](../../../data/wave14/enrich/raw/paper_rewrite_it_in_rust_a_computational_physics_case_study_veytsman_zhai_ding_sefkow.json) (enrichment confidence 0.3)

</details>
