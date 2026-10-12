# Ripserer.jl (Julia persistent homology) vs Ripser and Cubical Ripser (C++)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Runtime JIT beats ahead-of-time](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Julia` · `MIT` · 🟢 active

> Pure-Julia reimplementation of the Ripser persistent-homology algorithm; matches C++ Ripser on thresholded Rips, beats it only on very sparse inputs.

| | |
|---|---|
| **Beats** | Ripser (C++, master commit 286d369) and Cubical Ripser (C++, commits 6edb9c5 for 2D and a063dac for 3D) |
| **Claimed result** | Docs: 'very close to Ripser, usually within around 30%' and 'on very sparse inputs ... can sometimes outperform Ripser'. Ripserer/Ripser time ratios from the page: Alpha-Rips 0.807 (636 ms vs 789 ms), 0.741 (872 ms vs 1.179 s), 0.744 (56 ms vs 76 ms), 0.942 (5.844 s vs 6.203 s) and 1.058 (49.431 s vs 46.707 s, slower); sparse=true mode 0.993 and 0.998 on o3_1024 and o3_4096, 0.932 on random16, but 1.267 on dragon2000 and 1.304 on fract-r; dense mode is slower on 5 of 6 sets (ratio 1.04 to 1.99, o3_4096 151.5 s vs 76.2 s) with random16 at 0.803. Versus Cubical Ripser: 0.96 on bonsai64 (2.875 s vs 2.996 s), slower elsewhere (up to 2.631). |
| **Workload** | Persistent homology of Vietoris-Rips filtrations (datasets from the Ripser paper and PH-roadmap, parsed as Float32, parse time included) and of cubical image filtrations; minimum of five runs. |
| **Metric** | latency |
| **Hardware** | Laptop with Intel Core i5-4200U @ 1.60GHz and 8 GB RAM |
| **Compiler and flags** | Ripserer v0.15 (Julia version not stated; the RipsererBenchmarks.jl Manifest.toml does not record it). Ripser (commit 286d369) built by the harness (RipsererBenchmarks.jl src/ripser.jl get_ripsers runs `make all`) from its Makefile line `c++ -std=c++11 -Wall ripser.cpp -o ripser -Ofast -D NDEBUG`; Cubical Ripser 2D (6edb9c5) and 3D (a063dac) Makefiles compile every file with `c++ -std=c++11 -Ofast`. The compiler behind `c++` and its version are not stated. Timing: BenchmarkTools, samples=5, minimum reported. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | not stated |
| **Adoption** | 82 stars; Julia General registry package |
| **Last commit** | 2026-06-29 |
| **Links** | [repository](https://github.com/mtsch/Ripserer.jl) · [benchmark](https://raw.githubusercontent.com/mtsch/Ripserer.jl/master/docs/src/benchmarks.md) |

## Verdict

On the author's laptop (Intel i5-4200U, 8 GB), Ripserer v0.15 with sparse=true took 0.93-1.30x of the time of C++ Ripser (commit 286d369, built -Ofast by its Makefile, compiler unstated) on six Rips datasets, and 0.74-1.06x on five Delaunay-skeleton sparse inputs, with parse time included and the minimum of five runs reported; in its default dense mode it was 1.04-1.99x slower on five of six sets. Against Cubical Ripser it was faster only on bonsai64 (0.96) and up to 2.6x slower elsewhere.

## Use it when

- You already work in Julia and need Rips persistent homology of point clouds or distance matrices with a threshold: with sparse=true it ran 0.993-0.998x of Ripser's time on o3_1024 and o3_4096.
- Very sparse inputs such as the 1-skeleton of a Delaunay triangulation (alpha-style graphs) passed as a SparseMatrixCSC: 0.74-0.94x of Ripser's time on four of five such sets.
- You need things Ripser does not give you: representative cycles (alg=:involuted or :homology), critical simplices, custom filtrations, or cubical homology of images with more than 4 dimensions.
- Representative-cycle work where the alternative is Eirene.jl: 0.07-0.92x of Eirene's time on five of six sets in the author's runs.

## Skip it when

- Dense Rips with sparse=false (the default) on thresholded data: 1.04-1.99x slower than Ripser on five of six sets (o3_4096 151.5 s vs 76.2 s).
- Cubical homology of 2-D or 3-D images: Cubical Ripser is faster on four of five sets (up to 2.6x on lena512, 2.1x on bonsai128), and Ripserer ran out of 8 GB on 256^3 volumes.
- Memory-tight or short-lived jobs: peak heap includes the Julia runtime (111 MiB vs 1.1 MiB for Ripser on random16), and a fresh Julia session pays JIT compilation before the first result, which the benchmarks exclude.
- Callers outside Julia (C++, Rust, a shell pipeline): there is no C ABI or CLI, so embedding Julia costs more than calling Ripser or ripser.py.
- Workloads that need multiple cores: the reduction is single-threaded; the maintainer reported mixed results from multithreading experiments (issue #168).

## How it is fast

It ports Ripser's tricks: an implicit coboundary matrix (simplices indexed by the combinatorial number system and generated on the fly instead of stored), cohomology with the clearing (twist) optimization, apparent-pair and emergent-pair shortcuts, union-find for dimension 0, and binary-heap column addition over a small prime field (Mod{2} has a bit-mask fast path). Julia's type specialisation compiles the reduction for each filtration and field type, which is what lets it land near the C++ code; nothing here is a new algorithm, so the speed is parity rather than an algorithmic win.

## Compared with alternatives

No sibling covers persistent homology. Like NonuniformFFTs.jl against FINUFFT, Ripserer is a parity-level pure-Julia rewrite of a C++ tool, so pick it to stay in Julia with generic filtrations and representatives, not for the large wins NativeMinuit.jl claims over Minuit2.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | Julia packages: Compat, DataStructures, Distances, Graphs, IterTools, MiniQhull (qhull, for Alpha), PersistenceDiagrams, ProgressMeter, RecipesBase, StaticArrays, TupleTools, MLJModelInterface; stdlib LinearAlgebra and SparseArrays |
| **Minimum toolchain** | Julia 1.6 (Project.toml compat; CI tests '1', 'lts' and nightly on Linux plus a Windows job). The docs still say Julia 1.0 onward, which is stale. |
| **Platforms** | any platform Julia runs on (CI: ubuntu-latest and windows-latest); Alpha filtrations need MiniQhull's qhull build |
| **Thread safety** | not documented; computation is single-threaded |
| **Drop-in for the baseline** | partial — same algorithm and the same barcodes as Ripser, but a Julia API returning PersistenceDiagram objects instead of the ripser CLI/text output; no C or C++ interface |

## Gotchas

- Default sparse=false keeps a dense matrix even when a threshold is set, while Ripser switches itself to a sparse distance matrix whenever the threshold (or enclosing radius) is below the maximum distance (ripser.cpp main at 286d369). The docs' 'dense' table therefore compares Ripserer's slower mode with Ripser's sparse mode; pass sparse=true to get Ripser-equivalent behaviour.
- Harness asymmetries in RipsererBenchmarks.jl: Ripser is timed as an external process (read(cmd): process launch, text parse, stdout capture), while Ripserer runs in-process after BenchmarkTools' warm-up call, so Julia JIT compile time is excluded; this favours Ripserer most on the ms-scale rows (random16 8 ms vs 10 ms, alpha_dragon_2000 56 ms vs 76 ms). Also, load_sparse in src/utils.jl adds 1.0 to every edge length it reads (V = table[:, 3] .+ 1), so on the Alpha-Rips rows Ripserer's filtration values differ from the file Ripser reads; the edge order and pairing are unchanged except for Float32 rounding ties, so the timings are probably unaffected, but the outputs were never cross-checked.
- Prime fields: Mod{M} arithmetic calls mod_prime, which runs is_prime(M) by trial division on every +, - and \* for any M other than 2, and moduli above 3037000499 are rejected after an overflow report (issue #170, open). Small primes are cheap; large moduli were never benchmarked. Custom filtrations with many vertices need Custom{Int128} to avoid an OverflowError in simplex indices (issue #175).
- The published numbers are from Ripserer v0.15 in 2020 on an i5-4200U laptop with unstated Julia and C++ compiler versions; the package is now v0.17.0 and has not re-run them.

## Known shortcomings

- Mostly parity or slower; wins only on very sparse Alpha-Rips and the tiny random16 set; Ripser is timed as a subprocess (launch plus stdout) against in-process Ripserer; Ripser flags -Ofast -D NDEBUG from its public Makefile, compiler and Julia versions unstated.
- Parity tool, not faster. The docs' 'dense' table pits Ripserer's dense mode against Ripser, which picks sparse mode itself below max distance (ripser.cpp 286d369 main); sparse=true is the like-for-like mode. Ripser is timed as a subprocess (launch, stdout capture) against in-process Ripserer after BenchmarkTools warm-up, so JIT is excluded. RipsererBenchmarks.jl's load_sparse adds 1.0 to every Alpha-Rips edge length (V = table[:, 3] .+ 1), so Ripserer gets different filtration values than Ripser (probably timing-neutral, outputs never cross-checked). Mod{M} reruns a trial-division is_prime on every operation for M != 2; the docs claim Julia 1.0+ while Project.toml needs 1.6.

## Caveats and trade-offs

Mostly parity or slower: dense mode is 1.04-1.99x slower on 5 of 6 Rips sets (o3_4096 151.5 s vs 76.2 s), so the docs' 'usually within around 30%' holds only with sparse=true; sparse mode is 0.993-1.304; wins of about 1.06-1.35x appear only on very sparse Alpha-Rips inputs and tiny random16. Ripser is timed as an external process (launch plus stdout text output) against in-process Ripserer, which favours Ripserer on short runs. Ripserer's heap is 3-5x Ripser's on Alpha-Rips (includes the Julia runtime). Against Cubical Ripser, which the docs say uses a more specialized algorithm, Ripserer wins only bonsai64 (0.96) and is up to 2.6x slower elsewhere. Single 2020-era run (Ripserer v0.15, 2020 Ripser commits) on an old dual-core laptop; compiler and Julia versions not stated. [retier] The docs' 'dense' table pits Ripserer's dense mode against Ripser, which picks sparse mode itself below max distance (ripser.cpp 286d369); sparse=true is the like-for-like mode. Ripser is timed as a subprocess (launch, stdout capture) against in-process Ripserer after BenchmarkTools warm-up. RipsererBenchmarks.jl's load_sparse adds 1.0 to every Alpha-Rips edge length, so Ripserer gets different filtration values than Ripser (probably timing-neutral; outputs never cross-checked). Mod{M} reruns a trial-division is_prime on every operation for M != 2; the docs claim Julia 1.0+ while Project.toml needs 1.6.

Uses more memory than Ripser on small inputs (heap includes the Julia runtime, for example 138 MiB vs 33 MiB on alpha_3_sphere_3000) but supports higher-dimensional cubical complexes, critical simplices and representative cycles.

## Maintenance

Maintained at a slow pace (v0.17.0, last commits 2026-06-29 fixing involuted homology generators), MIT-licensed and registered in Julia's General registry; useful as a Julia-native Ripser equivalent, not as a faster replacement for it.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** Author's own benchmark: code is public (mtsch/RipsererBenchmarks.jl src/ripser.jl, src/ripserer.jl, src/benchmarksuites.jl), the CPU is stated (i5-4200U) and the C++ flags follow from the harness's `make all` on Ripser's public Makefile (-Ofast -D NDEBUG), but the compiler behind `c++`, its version and the Julia version are not stated, so not A; first-party, so C.
- **Verifier notes:** All ratios on docs/src/benchmarks.md match the record; the 'within around 30%' and 'can sometimes outperform Ripser' quotes are from docs/src/index.md. Ripser is not in the catalog (baseline_in_list corrected to false). Build flags recovered from the harness and the baselines' public Makefiles (-Ofast); the main shortcoming is a subprocess-vs-in-process timing asymmetry and wins limited to very sparse inputs. Metadata checked: MIT, 82 stars, last commit 2026-06-29, not a fork.
- **Fields the verifier corrected:** `baseline_in_list`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-75 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/mtsch/Ripserer.jl/master/docs/src/benchmarks.md>
  - <https://raw.githubusercontent.com/mtsch/Ripserer.jl/master/docs/src/index.md>
  - <https://raw.githubusercontent.com/mtsch/Ripserer.jl/master/README.md>
  - <https://raw.githubusercontent.com/mtsch/Ripserer.jl/master/LICENSE>
  - <https://github.com/mtsch/Ripserer.jl>
  - <https://github.com/mtsch/Ripserer.jl/commits>
  - <https://github.com/mtsch/RipsererBenchmarks.jl>
  - <https://github.com/mtsch/RipsererBenchmarks.jl/tree/master/src>
  - <https://raw.githubusercontent.com/mtsch/RipsererBenchmarks.jl/master/run_everything.jl>
  - <https://raw.githubusercontent.com/mtsch/RipsererBenchmarks.jl/master/Manifest.toml>
  - <https://raw.githubusercontent.com/mtsch/RipsererBenchmarks.jl/master/src/ripser.jl>
  - <https://raw.githubusercontent.com/mtsch/RipsererBenchmarks.jl/master/src/ripserer.jl>
  - <https://raw.githubusercontent.com/mtsch/RipsererBenchmarks.jl/master/src/benchmarksuites.jl>
  - <https://raw.githubusercontent.com/Ripser/ripser/286d369/Makefile>
  - <https://raw.githubusercontent.com/CubicalRipser/CubicalRipser_2dim/6edb9c5/Makefile>
  - <https://raw.githubusercontent.com/CubicalRipser/CubicalRipser_3dim/a063dac/Makefile>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/mtsch/Ripserer.jl/master/README.md>
  - <https://raw.githubusercontent.com/mtsch/Ripserer.jl/master/docs/src/benchmarks.md>
  - <https://raw.githubusercontent.com/mtsch/Ripserer.jl/master/docs/src/index.md>
  - <https://raw.githubusercontent.com/mtsch/Ripserer.jl/master/Project.toml>
  - <https://github.com/mtsch/Ripserer.jl/tree/master/src>
  - <https://raw.githubusercontent.com/mtsch/Ripserer.jl/master/src/Ripserer.jl>
  - <https://raw.githubusercontent.com/mtsch/Ripserer.jl/master/src/filtrations/rips.jl>
  - <https://raw.githubusercontent.com/mtsch/Ripserer.jl/master/src/filtrations/utils.jl>
  - <https://raw.githubusercontent.com/mtsch/Ripserer.jl/master/src/computation/ripserer.jl>
  - <https://raw.githubusercontent.com/mtsch/Ripserer.jl/master/src/computation/cohomology.jl>
  - <https://raw.githubusercontent.com/mtsch/Ripserer.jl/master/src/computation/reducedmatrix.jl>
  - <https://raw.githubusercontent.com/mtsch/Ripserer.jl/master/src/computation/zerodimensional.jl>
  - <https://raw.githubusercontent.com/mtsch/Ripserer.jl/master/src/base/simplex.jl>
  - <https://raw.githubusercontent.com/mtsch/Ripserer.jl/master/src/base/primefield.jl>
  - <https://raw.githubusercontent.com/mtsch/Ripserer.jl/master/.github/workflows/Test.yml>
  - <https://github.com/mtsch/Ripserer.jl/issues?q=is%3Aissue>
  - <https://github.com/mtsch/Ripserer.jl/issues/170>
  - <https://github.com/mtsch/Ripserer.jl/issues/175>
  - <https://github.com/mtsch/Ripserer.jl/issues/168>
  - <https://github.com/mtsch/Ripserer.jl/issues/159>
  - <https://github.com/mtsch/Ripserer.jl/commits/master>
  - <https://github.com/mtsch/RipsererBenchmarks.jl/tree/master/src>
  - <https://raw.githubusercontent.com/mtsch/RipsererBenchmarks.jl/master/README.md>
  - <https://raw.githubusercontent.com/mtsch/RipsererBenchmarks.jl/master/run_everything.jl>
  - <https://raw.githubusercontent.com/mtsch/RipsererBenchmarks.jl/master/src/RipsererBenchmarks.jl>
  - <https://raw.githubusercontent.com/mtsch/RipsererBenchmarks.jl/master/src/benchmarks.jl>
  - <https://raw.githubusercontent.com/mtsch/RipsererBenchmarks.jl/master/src/benchmarksuites.jl>
  - <https://raw.githubusercontent.com/mtsch/RipsererBenchmarks.jl/master/src/ripser.jl>
  - <https://raw.githubusercontent.com/mtsch/RipsererBenchmarks.jl/master/src/ripserer.jl>
  - <https://raw.githubusercontent.com/mtsch/RipsererBenchmarks.jl/master/src/utils.jl>
  - <https://raw.githubusercontent.com/mtsch/RipsererBenchmarks.jl/master/src/report.jl>
  - <https://raw.githubusercontent.com/mtsch/RipsererBenchmarks.jl/master/datasets/alpha_torus_10_000.spdist>
  - <https://raw.githubusercontent.com/Ripser/ripser/286d369/ripser.cpp>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/mtsch/ripserer.jl`) · [data/wave14/enrich/raw/github_com_mtsch_ripserer_jl.json](../../../data/wave14/enrich/raw/github_com_mtsch_ripserer_jl.json) (enrichment confidence 0.75)

</details>
