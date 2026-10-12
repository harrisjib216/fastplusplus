# SPRK-tree (Sorted Projection Radius KD-tree)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Rust` · `MIT` · 🟢 active

> Rust SIMD kd-tree for fixed-radius queries with sorted LUT leaves; ESA 2026 paper reports fastest queries across 2-960 dimensions.

| | |
|---|---|
| **Beats** | Boost.Geometry R-tree (named among the paper's competitors in search snippets) plus KD-trees in several languages (Kiddo, nabo, Neighbourhood), a Rust VP-tree, scikit-learn BallTree, SNN and brute force. nanoflann and CGAL kd-tree are feature-gated backends in the rembed harness, but I could not confirm they appear in the paper. |
| **Claimed result** | No speedup numbers verified. The paper (Blaesius, von der Heydt, Kempf, Kobert, Maas, 'Benchmarking and Engineering Data Structures for Spherical Range Queries', arXiv 2607.07367, listed in search results as ESA 2026 LIPIcs) could not be opened, because arxiv.org and drops.dagstuhl.de are blocked. Neither the sprk nor the rembed README quotes results. According to its abstract, seen only in search snippets, the SPRK-tree achieves the fastest query times in almost all benchmarks and ranks second in the rest. |
| **Workload** | Radius queries (and nearest neighbor queries) on graph embeddings and other point sets, up to 10M points and 2 to 960 dimensions, from the ESA 2026 paper 'Benchmarking and Engineering Data Structures for Spherical Range Queries'. |
| **Metric** | throughput |
| **Compiler and flags** | The sprk README advises rustflags -Ctarget-cpu=native (AVX-512 compress when available). The rembed release profile is the Cargo default plus debug=true. The paper's compiler and flags were not read. |
| **Adoption** | 3 stars; crate published as sprk on crates.io |
| **Last commit** | 2026-04-07 |
| **Links** | [repository](https://github.com/wembed-pdf/sprk) · [benchmark](https://arxiv.org/abs/2607.07367) |

## Verdict

No numbers were verified. The ESA 2026 paper (LIPIcs ESA.2026.22, arXiv 2607.07367) could not be opened because arxiv.org, drops.dagstuhl.de and docs.rs are egress-blocked. Search snippets of its abstract say the SPRK-tree had the fastest query time in almost all benchmarks (graph embeddings plus real-world sets, up to 10M points, 2-960 dimensions), was second to SNN or brute force in the rest, and beat the Kiddo and Neighbourhood kd-trees. The public harness (wembed-pdf/rembed, a reproducibility CLI with Zenodo data and a nix flake) has feature-gated nanoflann, Boost R-tree and CGAL kd-tree backends, but which C++ baselines appear in the paper's figures, the CPU and the compiler were not seen.

## Use it when

- Repeated fixed-radius neighbour queries on points that move every iteration, with a full rebuild each step (graph-embedding force layouts, particle or agent simulations): update() reuses the buffers
- Moderate to high-dimensional Euclidean data (the paper covers 2-960 dimensions and up to 10M points). Search snippets of the abstract say it was fastest in almost all benchmarks, second only to SNN or brute force in a few high-dimensional cases, and an order of magnitude faster than brute force at 16 dimensions (paper not opened)
- Rust code bases (crate sprk 0.2.0), or C/C++ callers through sprk-ffi when f32 coordinates and 2-16 dimensions are enough
- x86-64 servers with AVX-512, built with -Ctarget-cpu=native as the README advises

## Skip it when

- k-nearest-neighbour search, box or range queries, or non-point geometry: it only does radius queries
- A few inserts or deletes at a time: update() rebuilds the whole tree
- Code that relies on the IdDist distance or on exact behaviour at the radius boundary when D &gt;= 6 (see gotchas), or that needs f64 through the C API (f32 only)
- Teams that cannot add a Rust toolchain (1.88+, edition 2024) to a C++ build
- Risk-averse production use: the project has 18 commits made between 2026-03-08 and 2026-04-07, 3 stars, no GitHub releases and no independent measurements, and the paper's numbers were not seen here

## How it is fast

The tree is an implicit, pointer-free balanced kd-tree: median splits on cycling axes are stored in a heap-indexed array, and leaves hold about 500-1000 points (LEAFSIZE 500, depth floor(log2(n/500))). During descent, it carries per-axis squared offsets so the radius left for a far subtree shrinks as planes are crossed. The paper calls this radius reduction; it prunes harder than a plain distance-to-plane test. Each leaf is sorted along one axis and indexed by a histogram lookup table (LUT), so two LUT reads turn the reduced radius into a contiguous slice of the leaf, in the style of SNN sorted buckets. Points are stored in W-wide (default 8) structure-of-arrays blocks. Distances are computed with SIMD FMAs (for D &gt;= 6 via precomputed half-norms minus a dot product), and hits are written out with AVX-512 vcompressps/vpcompressd when the CPU has them (runtime check) or with `wide` shuffle tables otherwise. With the svd feature enabled and D &gt; 16, the tree is built in SVD-rotated coordinates.

## Compared with alternatives

Pick SPRK over nanoflann when the workload is purely fixed-radius search in moderate or high dimensions and you can link Rust. nanoflann is the safer C++ choice for kNN, f64, mature packaging and no extra toolchain. ArborX fits GPU batched queries, and Pkd-tree fits many-core batch inserts and deletes.

## Integration

| | |
|---|---|
| **Form** | crate (Rust); C/C++ through the sprk-ffi static or shared library with sprk.h and the header-only sprk.hpp wrapper |
| **Dependencies** | num-traits. The default feature simd-compress adds wide and simd-lookup. Optional: rayon and sharded-vec-writer (feature parallel); faer-svd, faer-core and dyn-stack (feature svd) |
| **Minimum toolchain** | Rust 1.88, edition 2024 |
| **Platforms** | any Rust target: an AVX-512 compress path on x86-64 (runtime-detected) and a portable `wide`/scalar fallback elsewhere |
| **Thread safety** | Not stated in the docs. From the source, query_radius takes &self and uses a thread-local scratch buffer, so many threads can query one tree; update() needs &mut self |
| **Drop-in for the baseline** | no |

## Gotchas

- IdDist.dist is documented as the squared distance, but for D &gt;= 6 the leaf scan computes |p|^2/2 + |q|^2/2 - p.q (half the squared distance) and stores that value unchanged (src/query.rs snn, src/simd.rs dist_half_squared, src/output.rs); D &lt; 6 gets the true squared distance. The D &gt;= 6 test also compares against r^2/2 + DIST_EPS (an absolute 1e-4 for f32, 1e-8 for f64) with no exact recheck. Points near the boundary can therefore be wrongly included, or lost to cancellation when coordinates are large relative to r. This comes from reading the source; no issue has been filed
- Default features exclude svd and parallel (commit 2026-04-07, 'Disable svd and parallel construction features by default'), while the rembed benchmark builds sprk with svd, parallel and simd-compress. A plain `cargo add sprk` therefore gets neither the SVD projection for D &gt; 16 nor the parallel build the paper used
- C API limits: sprk_create returns NULL for any dimension outside 2-16, even though the FFI README advertises 18-24; every query heap-allocates its result array (free it with sprk_free_results), and the C++ wrapper then copies it into a new std::vector and only assert()s that creation succeeded; there is no update() and no batch query. The FFI's dynamic-dimension path builds DynSprk&lt;f32,u32&gt; but queries and frees it as DynSprk&lt;f32,u64&gt;. That path is unreachable today because of the dimension check, but it becomes a type-confusion bug if the check is relaxed
- Each leaf's LUT range is rounded to whole units (floor of the minimum, ceil of the maximum). Data whose per-leaf extent is far below 1 gets coarse buckets and scans more of each leaf, so rescale tiny coordinates (from the source)

## Known shortcomings

- ESA 2026 venue and abstract seen only in search snippets (paper unreadable here); no numbers seen; nanoflann/CGAL comparison in the paper unconfirmed (retier candidate).
- Correctness: for D&gt;=6, IdDist.dist holds half the squared distance though documented as squared; the radius test is r^2/2 plus an absolute 1e-4 slack (f32) with no exact recheck. FFI dynamic path frees/queries DynSprk&lt;f32,u64&gt; but creates &lt;f32,u32&gt; (unreachable now because sprk_create rejects dim&gt;16, though the FFI README advertises 18-24). Default features drop svd and parallel, which the paper harness enabled. Paper unopened here; no numbers verified. Rust.

## Caveats and trade-offs

Peer-reviewed (ESA 2026 LIPIcs) but numbers were not verified here: the paper and its tables were unreachable, and neither the sprk nor rembed README quotes speedups. Evidence tier B is on the strength of the paper plus public benchmark harness (rembed with reproducibility-cli). Verifier should open the paper for numbers, CPU and flags. Benchmarks target embeddings from graph drawing, with many high-dimensional cases. [retier] Peer review rests on search-result listings of the DROPS/LIPIcs ESA 2026 entry, whose page is blocked. The rembed README's own citation is still the arXiv preprint (@misc). The reproducibility CLI (rembed, reproducability branch) covers Figures 3, 4, 7, 9 and 11 and Tables 2-7, but it needs the Zenodo datasets and commits no results, CPU or compiler. A move to A, or a lower tier, needs the paper.

Radius queries in D-dimensional Euclidean space; SIMD leaf scans with lookup-table pruning, SVD projection for D &gt; 16, parallel construction, update() rebuild that reuses allocations. Not a general spatial index (no rectangles or nearest-neighbor guarantees in the README).

## Maintenance

A young research crate under MIT (crate 0.2.0, no commits since 2026-04-07) and small enough (about 3k lines of core Rust) to vendor; treat it as a paper artifact rather than a maintained library.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** B rests on the peer-reviewed paper 'Benchmarking and Engineering Data Structures for Spherical Range Queries' (arXiv 2607.07367). Search results list it as ESA 2026, LIPIcs DOI 10.4230/LIPIcs.ESA.2026.22. Its abstract (seen in search snippets) says the SPRK-tree is fastest in almost all benchmarks, and the snippets name Boost R-tree among the competitors. A public reproducibility CLI exists (wembed-pdf/rembed, reproducability branch, reproducibility-cli; Zenodo data, nix flake). The paper itself was unreachable, so its numbers, CPU and compiler were not seen and A cannot be assessed.
- **Verifier notes:** I confirmed B on the same basis as earlier batches that accepted a venue seen only in search results (auto-mpft, PowerInfer). A retier check that can open arXiv 2607.07367 should read the tables, CPU and flags (possible A, given the public reproducibility CLI) and confirm whether nanoflann, CGAL and Boost R-tree are in the results. Metadata checked on github.com: MIT, 3 stars, not a fork, 18 commits, last commit 2026-04-07. The repo has sprk-ffi and sprk-python directories, so C callers may be able to use it.
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://github.com/wembed-pdf/sprk>
  - <https://github.com/wembed-pdf/sprk/commits>
  - <https://raw.githubusercontent.com/wembed-pdf/sprk/HEAD/README.md>
  - <https://raw.githubusercontent.com/wembed-pdf/sprk/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/wembed-pdf/sprk/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/wembed-pdf/rembed/HEAD/README.md>
  - <https://raw.githubusercontent.com/wembed-pdf/rembed/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/wembed-pdf/rembed/reproducability/reproducibility-cli/README.md>
  - <https://github.com/wembed-pdf/rembed/tree/reproducability/reproducibility-cli>
- **Sources the enricher read:**
  - <https://github.com/wembed-pdf/sprk>
  - <https://github.com/wembed-pdf/sprk/commits>
  - <https://github.com/wembed-pdf/sprk/tree/main/src>
  - <https://github.com/wembed-pdf/sprk/tree/main/sprk-ffi>
  - <https://raw.githubusercontent.com/wembed-pdf/sprk/HEAD/README.md>
  - <https://raw.githubusercontent.com/wembed-pdf/sprk/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/wembed-pdf/sprk/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/wembed-pdf/sprk/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/wembed-pdf/sprk/HEAD/src/tree.rs>
  - <https://raw.githubusercontent.com/wembed-pdf/sprk/HEAD/src/query.rs>
  - <https://raw.githubusercontent.com/wembed-pdf/sprk/HEAD/src/simd.rs>
  - <https://raw.githubusercontent.com/wembed-pdf/sprk/HEAD/src/svd.rs>
  - <https://raw.githubusercontent.com/wembed-pdf/sprk/HEAD/src/dynamic.rs>
  - <https://raw.githubusercontent.com/wembed-pdf/sprk/HEAD/src/scalar.rs>
  - <https://raw.githubusercontent.com/wembed-pdf/sprk/HEAD/src/output.rs>
  - <https://raw.githubusercontent.com/wembed-pdf/sprk/HEAD/sprk-ffi/README.md>
  - <https://raw.githubusercontent.com/wembed-pdf/sprk/HEAD/sprk-ffi/Cargo.toml>
  - <https://raw.githubusercontent.com/wembed-pdf/sprk/HEAD/sprk-ffi/include/sprk.h>
  - <https://raw.githubusercontent.com/wembed-pdf/sprk/HEAD/sprk-ffi/include/sprk.hpp>
  - <https://raw.githubusercontent.com/wembed-pdf/sprk/HEAD/sprk-ffi/src/lib.rs>
  - <https://raw.githubusercontent.com/wembed-pdf/rembed/HEAD/README.md>
  - <https://raw.githubusercontent.com/wembed-pdf/rembed/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/wembed-pdf/rembed/reproducability/reproducibility-cli/README.md>
  - https://arxiv.org/html/2607.07367 (EGRESS_BLOCKED; abstract seen only in WebSearch snippets)
  - https://docs.rs/sprk/latest/sprk/ (EGRESS_BLOCKED)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/wembed-pdf/sprk`) · [data/wave8/enrich/raw/github_com_wembed_pdf_sprk.json](../../../data/wave8/enrich/raw/github_com_wembed_pdf_sprk.json) (enrichment confidence 0.65)

</details>
