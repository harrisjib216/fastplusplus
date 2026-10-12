# NPB-Rust (NAS Parallel Benchmarks in Rust, sequential and Rayon)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Concurrency runtimes](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟢 active

> Rust port of the NAS Parallel Benchmarks; its paper reports the sequential suite 5.59% faster than C++ NPB-CPP.

| | |
|---|---|
| **Beats** | NPB-CPP, the group's C++ port of NAS Parallel Benchmarks 3.4.1 (sequential NPB-SER, and OpenMP NPB-OMP for the parallel comparison), plus the original Fortran NPB |
| **Claimed result** | From the paper abstract as shown in a search snippet (snippet only): Rust sequential is 5.59% faster than C++ and 1.23% slower than Fortran; Rust with Rayon is slower than both the Fortran and the C++ OpenMP versions. |
| **Workload** | NAS Parallel Benchmarks kernels EP, CG, MG, IS, FT and pseudo-applications BT, SP, LU in Rust (sequential NPB-RUST and Rayon-parallel NPB-RAYON), compared with the C++ and Fortran versions. |
| **Metric** | throughput |
| **Compiler and flags** | Paper-era Cargo.toml (April 2025): release profile with lto='fat', codegen-units=1 and panic='abort', removed in commit 2990a0b (September 2025); C++ baseline g++ -O3 -mcmodel=medium without LTO (enricher correction) |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | not stated |
| **Adoption** | 31 stars |
| **Last commit** | 2026-10-08 |
| **Links** | [repository](https://github.com/GMAP/NPB-Rust) · [benchmark](https://arxiv.org/abs/2502.15536) |

## Verdict

From the arXiv 2502.15536 abstract, seen only as search snippets: across the sequential suite NPB-RUST was 5.59% faster than NPB-CPP (g++ -O3 -mcmodel=medium per the repo's make.def) and 1.23% slower than Fortran NPB, and NPB-RAYON was slower than both OpenMP versions; hardware, compiler versions, classes and per-kernel numbers were not seen. CG's 24-iteration loop is worth about 4% on that kernel alone; its effect on the aggregate depends on how the paper aggregates (about 0.5 points if it is a mean over the eight programs).

## Use it when

- Comparing Rust toolchains, LLVM versions or CPUs on a standard HPC workload that carries its own correctness check (verification constants for classes S to E).
- Porting Fortran- or C-style array code to Rust and wanting worked examples of iterator-based bounds-check elision and of where the authors fell back to get_unchecked (FT transposes, IS bucket counting, MG stencils).
- Studying Rayon against OpenMP on identical kernels, including a pipelined LU wavefront built from raw pointers and AtomicBool flags.
- Sequential numerical loops where a few percent either way against g++ -O3 is acceptable and memory safety (with the safe="true" build) is worth having.

## Skip it when

- As proof that Rust out-runs C++ on HPC code: the 5.59% aggregate is first-party, comes from a paper not reachable here, mixes in a CG that runs 24 instead of 25 inner iterations, and compares a fat-LTO, codegen-units=1, panic=abort Rust build with a non-LTO g++ build.
- Parallel throughput: by the paper abstract the Rayon version is slower than both the C++ and Fortran OpenMP versions; there is no MPI version.
- Class F or IS class E runs: the README lists classes up to F, but no benchmark defines F and IS stops at D (compile_error otherwise).
- As a reusable library: each program is a single binary with compile-time constants and no public API.
- Memory-safety guarantees out of the box: the default build has UNSAFE = true and unchecked indexing in FT, IS and MG (MG alone has 152 unsafe or get_unchecked occurrences).

## How it is fast

There is no new algorithm: the code follows NPB-CPP loop for loop. Hot loops are written as iterator chains over zipped slices (for example the CG sparse matrix-vector product) so LLVM can drop bounds checks, and in the default build (UNSAFE = true unless --cfg safe="true" is passed) FT, IS and MG switch to get_unchecked inside unsafe blocks. The release profile in the April 2025 upload, the code closest to the February 2025 paper, set codegen-units = 1, lto = "fat" and panic = "abort" (removed in commit 2990a0b, September 2025), while the C++ baseline builds with g++ -O3 -mcmodel=medium and no LTO. The sequential CG also does about 4% less work than the C++ version (see gotchas).

## Compared with alternatives

Pick it over the CMU 15-618 Rayon-vs-OpenMP project when you need the standard, self-verifying NPB kernels in both sequential Rust and Rayon form; that project covers Mandelbrot, matmul, sort and reduction and is where Rayon actually wins cases, whereas NPB-RAYON loses to OpenMP. None of the async-runtime siblings (Tokio, Embassy, ScyllaDB driver) measure numerical loops.

## Integration

| | |
|---|---|
| **Form** | source-drop (two Cargo binary crates, NPB-RUST and NPB-RAYON) |
| **Dependencies** | none for NPB-RUST; rayon 1.10 for NPB-RAYON |
| **Minimum toolchain** | Rust 1.85 (edition 2024) |
| **Platforms** | any Rust target; no SIMD intrinsics, inline assembly or target_feature code in either crate |
| **Thread safety** | Sequential binaries are single-threaded; NPB-RAYON shares raw pointers across threads through unsafe impl Sync wrappers (BT, LU) and synchronises LU's wavefront with AtomicBool flag arrays |
| **Drop-in for the baseline** | partial: same benchmarks, classes, verification constants and output format as NPB-CPP and Fortran NPB, but built with cargo and RUSTFLAGS instead of make with CLASS= arguments, and with no MPI variant |

## Gotchas

- Harness flaw in CG (both NPB-RUST and NPB-RAYON, present since the first upload cd8b36d and still at HEAD): conj_grad runs `for _ in 1..cgitmax` with cgitmax = 25, which is 24 CG iterations, while NPB-CPP runs `for(cgit = 1; cgit <= cgitmax; cgit++)`, 25 iterations as in Fortran NPB. Verification still passes: an independent Python port of NPB-CPP's CG run here gave zeta relative errors of 1.0e-15 (class S), 3.4e-16 (W) and 5.2e-14 (A) for both 24 and 25 iterations against the 1e-10 tolerance. Rust CG therefore does 25 instead of 26 sparse matrix-vector products per call (about 4% less work, derived) while its Mop/s formula still credits 25 iterations, so any CG Rust-vs-C++ row is biased in Rust's favour by roughly that much.
- The code was uploaded on 2025-04-11 (commit cd8b36d), seven weeks after the arXiv paper (2025-02-21), so the measured code cannot be confirmed to match; the paper-era fat-LTO and panic=abort release profile was later deleted, so a fresh build of HEAD is not the configuration the paper timed.
- The default build sets UNSAFE = true; pass RUSTFLAGS='--cfg class="A" --cfg safe="true"' for bounds-checked FT, IS and MG. The paper does not say (in what could be seen) which mode it timed.
- Both NPB-RUST and NPB-CPP print one line per outer CG iteration inside the timed region, as Fortran NPB does, so console speed is part of every CG timing on both sides; the Rust timers use std::time::Instant and time only the benchmark loop, matching NPB-CPP's T_BENCH region.

## Known shortcomings

- The 5.59% sequential win over the same group's NPB-CPP (-O3 -mcmodel=medium) is seen only in a snippet (arXiv 2502.15536 blocked); Rayon is slower than OpenMP, so concurrency-runtimes is a poor category fit.
- Harness flaw in CG (NPB-RUST and NPB-RAYON, since the first upload cd8b36d and still at HEAD): conj_grad runs `for _ in 1..cgitmax`, 24 iterations, against NPB-CPP's `cgit <= cgitmax`, 25, so Rust CG does about 4% less work while its Mop/s still credits 25; verification passes either way (an independent Python port gives zeta errors of 1.0e-15 for S, 3.4e-16 for W and 5.2e-14 for A), so the bug is silent. Flags were asymmetric: the paper-era Cargo.toml (April 2025) had lto='fat', codegen-units=1 and panic='abort' (removed in 2990a0b, September 2025) while the C++ build is g++ -O3 -mcmodel=medium without LTO; the code was uploaded seven weeks after the paper; the default build is UNSAFE=true (get_unchecked in FT, IS and MG); there is no class F despite the README and IS stops at D.

## Caveats and trade-offs

The arXiv page (2502.15536) is blocked in this environment and was not opened; the numbers come from WebSearch snippets of arxiv.org/html/2502.15536v1 (snippet only), so venue, peer-review status, hardware, compiler versions and per-kernel results are unconfirmed; a verifier with paper access should retier. The GitHub repo has no performance numbers. The only win over C++ is the sequential aggregate (5.59%, a small margin); Rayon is slower than C++ OpenMP and Fortran OpenMP, so the concurrency-runtimes category fits poorly (the win is sequential codegen, closer to numerics). The C++ baseline is the same group's NPB-CPP port (FGCS 2021, https://github.com/GMAP/NPB-CPP). Public build defaults are equivalent in optimisation level (-O3 against cargo --release opt-level 3, neither with -march=native), but the C++ default adds -mcmodel=medium; whether that or anything else explains the 5.59% is untested. The latest commit (2026-10-08, 3bb2455 'fix: adjusted tolrsd constants in LU') only assigns the 1.0e-08 tolrsd constants that were previously left at zero; with zero tolerances the early-exit residual check never fired, so the measured LU did the full iteration count and the fix does not inflate the published numbers. NPB-Rust has a --cfg safe="true" switch whose default (unset) reports UNSAFE=true; which mode the paper timed is not stated. [retier] Enricher: harness flaw in CG (NPB-RUST and NPB-RAYON since the first upload cd8b36d, still at HEAD); conj_grad runs `for _ in 1..cgitmax` (24 iterations) against NPB-CPP's 25, so Rust CG does about 4% less work while its Mop/s still credits 25, and verification passes either way (independent Python port: zeta errors 1.0e-15 for S, 3.4e-16 for W, 5.2e-14 for A). The default build is UNSAFE=true (get_unchecked in FT, IS and MG); there is no class F despite the README and IS stops at D; the code was uploaded seven weeks after the paper.

Rust port of NPB with a sequential variant (NPB-RUST) and a Rayon variant (NPB-RAYON); safety and ergonomics trade-offs are not discussed on the pages that were opened.

## Maintenance

Active (8 commits; last on 2026-10-08 fixed LU's zero tolrsd constants), MIT-licensed, no issues filed and one closed pull request; usable as benchmark and porting reference, but the CG iteration-count bug is unfixed at HEAD, so CG timings are not like-for-like with NPB-CPP or Fortran NPB.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** arXiv 2502.15536 is unreachable here (DNS/egress blocked); the 5.59%-faster-than-C++ sequential aggregate and the Rayon-slower-than-OpenMP result were seen only in a WebSearch snippet of arxiv.org/html/2502.15536v1 (snippet only). The paper is by the same group that wrote both NPB-Rust and the NPB-CPP baseline, peer review is unconfirmed (README cites arXiv only), and hardware and compiler versions were not seen, so first-party tier C stands.
- **Verifier notes:** Confirm at C: repo, MIT licence, 31 stars and 2026-10-08 last commit check out; paper numbers seen only in a search snippet (arXiv blocked), first-party, small 5.59% aggregate sequential margin, Rayon loses to OpenMP. Shortcomings to record: snippet-only evidence, same-group C++ baseline, unknown hardware/compiler versions, weak category fit (sequential win filed under concurrency-runtimes).
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-01 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/GMAP/NPB-Rust>
  - <https://github.com/GMAP/NPB-Rust/commits/main>
  - <https://github.com/GMAP/NPB-Rust/commit/3bb24558f49af2028fda283e5e3b1b5ce05c5788>
  - <https://raw.githubusercontent.com/GMAP/NPB-Rust/HEAD/README.md>
  - <https://raw.githubusercontent.com/GMAP/NPB-Rust/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/GMAP/NPB-Rust/HEAD/NPB-RUST/Cargo.toml>
  - <https://raw.githubusercontent.com/GMAP/NPB-Rust/HEAD/NPB-RAYON/Cargo.toml>
  - <https://raw.githubusercontent.com/GMAP/NPB-Rust/HEAD/NPB-RUST/src/cg.rs>
  - <https://raw.githubusercontent.com/GMAP/NPB-Rust/HEAD/NPB-RUST/src/lu.rs>
  - <https://raw.githubusercontent.com/GMAP/NPB-CPP/HEAD/NPB-SER/config/make.def>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/GMAP/NPB-Rust/HEAD/README.md>
  - <https://raw.githubusercontent.com/GMAP/NPB-Rust/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/GMAP/NPB-Rust/HEAD/NPB-RUST/Cargo.toml>
  - <https://raw.githubusercontent.com/GMAP/NPB-Rust/HEAD/NPB-RAYON/Cargo.toml>
  - <https://raw.githubusercontent.com/GMAP/NPB-Rust/HEAD/NPB-RUST/src/{bt,cg,ep,ft,is,lu,mg,sp}.rs>
  - <https://raw.githubusercontent.com/GMAP/NPB-Rust/HEAD/NPB-RUST/src/common/{dcomplex,mod,print_results,randdp,timers}.rs>
  - <https://raw.githubusercontent.com/GMAP/NPB-Rust/HEAD/NPB-RAYON/src/{bt,cg,ep,ft,is,lu,mg,sp}.rs>
  - <https://raw.githubusercontent.com/GMAP/NPB-Rust/HEAD/NPB-RAYON/src/common/{dcomplex,mod,print_results,randdp,timers}.rs>
  - <https://raw.githubusercontent.com/GMAP/NPB-Rust/cd8b36d/NPB-RUST/Cargo.toml>
  - <https://raw.githubusercontent.com/GMAP/NPB-Rust/cd8b36d/NPB-RUST/src/cg.rs>
  - <https://github.com/GMAP/NPB-Rust/tree/main/NPB-RUST/src>
  - <https://github.com/GMAP/NPB-Rust/tree/main/NPB-RUST/src/common>
  - <https://github.com/GMAP/NPB-Rust/issues>
  - <https://github.com/GMAP/NPB-Rust/issues?q=is%3Aissue>
  - <https://github.com/GMAP/NPB-Rust/pulls?q=is%3Apr>
  - <https://github.com/GMAP/NPB-Rust/commits/main>
  - <https://github.com/GMAP/NPB-Rust/commit/98cbea0>
  - <https://github.com/GMAP/NPB-Rust/commit/2990a0b>
  - <https://raw.githubusercontent.com/GMAP/NPB-CPP/HEAD/NPB-SER/config/make.def>
  - <https://raw.githubusercontent.com/GMAP/NPB-CPP/HEAD/NPB-SER/CG/cg.cpp>
  - <https://raw.githubusercontent.com/GMAP/NPB-CPP/HEAD/NPB-SER/EP/ep.cpp>
  - <https://raw.githubusercontent.com/GMAP/NPB-CPP/HEAD/NPB-SER/IS/is.cpp>
  - <https://raw.githubusercontent.com/GMAP/NPB-CPP/HEAD/NPB-SER/BT/bt.cpp>
  - <https://raw.githubusercontent.com/GMAP/NPB-CPP/HEAD/NPB-SER/SP/sp.cpp>
  - <https://raw.githubusercontent.com/GMAP/NPB-CPP/HEAD/NPB-SER/LU/lu.cpp>
  - <https://raw.githubusercontent.com/GMAP/NPB-CPP/HEAD/NPB-SER/MG/mg.cpp>
  - <https://raw.githubusercontent.com/GMAP/NPB-CPP/HEAD/NPB-SER/FT/ft.cpp>
  - WebSearch snippets for arXiv 2502.15536 (arxiv.org/html/2502.15536v1 and www.themoonlight.io review: ENOTFOUND, blocked here)
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:rust/gmap/npb-rust#npb-sequential`) · [data/wave14/enrich/raw/lang_rust_gmap_npb_rust_npb_sequential.json](../../../data/wave14/enrich/raw/lang_rust_gmap_npb_rust_npb_sequential.json) (enrichment confidence 0.6)

</details>
