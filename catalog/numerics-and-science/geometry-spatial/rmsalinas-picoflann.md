# picoflann

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `no license` · 🟢 active

> Tiny single-header exact kd-tree (knn and radius search) claiming 1.25-4x over nanoflann; unlicensed, claim disputed.

| | |
|---|---|
| **Beats** | nanoflann (also OpenCV FLANN) |
| **Claimed result** | Index building: 1.46x faster than nanoflann, 1.73x faster than OpenCV FLANN. Knn: 4.14x faster than nanoflann, 1.8x faster than OpenCV FLANN. Radius search: 1.25x faster than nanoflann, 3.21x faster than OpenCV FLANN. |
| **Workload** | Exact kd-tree index build, knn and radius search on a small point set (README heading says 10,000 2D points, the speed-up block says 3D points). |
| **Metric** | throughput |
| **Adoption** | 22 stars; part of the ucoslam project |
| **Last commit** | 2026-04-27 |
| **Links** | [repository](https://github.com/rmsalinas/picoflann) · [benchmark](https://github.com/rmsalinas/picoflann) |

## Verdict

The README (2018) claims, on 10,000 points (heading says 2D, block says 3D), index build 1.46x, knn 4.14x and radius search 1.25x faster than nanoflann, with no k, hardware, compiler or nanoflann benchmark code; the repo's only benchmark (testperformance.cpp, 2026, -O3 -march=native, k=10) races picoflann v1/v2 against OpenCV FLANN, not nanoflann, and publishes no numbers. An independent PCL-wrapper comparison (OpenFLANN) found nanoflann faster at small k and picoflann faster only at very large k.

## Use it when

- Internal or research code (not redistributed) that needs exact knn/radius search over a few thousand to a few hundred thousand 2D/3D float points, e.g. SLAM map points or keypoint matching
- Large-k queries: the independent OpenFLANN comparison found picoflann much faster than nanoflann at K=5000 on 200,000 points (0.84 ms vs 8.36 ms)
- When you want a single small header with no dependencies and a functor adapter instead of nanoflann-style dataset adaptor classes
- Static datasets built once and queried many times, with the option to serialise the index next to the data

## Skip it when

- Anything you ship or redistribute: the repo has no LICENSE file and no licence header, so it is all-rights-reserved by default; the README also says academic users 'must cite' UcoSLAM
- Small-k queries (k=1 to 10), the common robotics case: OpenFLANN measured nanoflann faster (10,000 points, K=10: 0.00213 ms vs 0.00358 ms) and open issue #1 (2021, unanswered) reports picoflann 'about half as fast as nanoflann' on range-image data
- Dynamic data: there is no insert or erase; any change means a full rebuild
- Loading index files from untrusted sources: fromStream does no validation (see gotchas)
- Double-precision or large-magnitude coordinates with the defaults: v1 keeps bounding boxes and split bounds in float, and picoflann2 defaults to Scalar=float

## How it is fast

Classic FLANN/nanoflann-style single kd-tree: split dimension chosen by highest variance estimated from about 100 sampled points, split at the mean with a two-pass in-place plane partition, leaves of 10 points, and searches that keep per-dimension incremental distances to the cell (the 'dists' array) so the far child is pruned with mindistsq against the current k-th best held in a max-heap; distance accumulation exits early once it exceeds the worst. picoflann2 removes the per-leaf std::vector (indices stored inline so a float node is 64 bytes, one cache line), puts bounding boxes in std::array, unrolls distance loops on compile-time DIMS and defaults to float arithmetic.

## Compared with alternatives

Rarely: PicoTree (catalogued as beating nanoflann v1.7.1 on build about 2.6x and knn about 1.2x) or nanoflann itself, which the independent OpenFLANN test found faster at small k, are the safer picks; picoflann only stands out for very large k, and its missing licence rules it out of products. Janos95/kdtree is another small exact kd-tree with a modest 10-15% claimed edge over nanoflann.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none for picoflann.h / picoflann2.h; the repo's testperformance.cpp and test_accuracy.cpp need OpenCV |
| **Minimum toolchain** | not documented for the headers; the repo's CMakeLists builds its tests as C++14 with -O3 -march=native |
| **Platforms** | any (portable C++, no intrinsics) |
| **Thread safety** | not documented; in picoflann2 all search methods are const and keep state on the stack or in the returned vector, so concurrent queries on a built index look safe from the code; build() mutates the object |
| **Drop-in for the baseline** | partial — same job as nanoflann's KDTreeSingleIndexAdaptor (exact single kd-tree, knn and radius search) but a different interface: an adapter functor (element, dim) plus a container with size()/at() passed to every search call |

## Gotchas

- Security/robustness: fromStream trusts the stream. picoflann2 reads a per-node idx_count (uint8_t, up to 255) and then copies idx_count\*4 bytes into a fixed idx[MAX_LEAF=10] array, so a corrupt or crafted file overflows the node; child indices are never range-checked. v1 resizes vectors from unchecked 64-bit sizes and takes &idx[0] of empty vectors for internal nodes in both toStream and fromStream (undefined behaviour that debug STL assertions abort on)
- radiusSearch's maxNN parameter is ignored in both versions: in radius mode ResultSet::push appends every hit without checking maxSize, so a large radius returns everything inside it
- Radius is passed in linear units but returned distances are squared; the index does not copy the data, so the same container must be alive and unchanged at search time and after fromStream
- README's radiusSearch(data, res, point, r) example does not match the actual overload radiusSearch(res, data, point, r); point indices are 32-bit (v1 stores leaf indices as int)

## Known shortcomings

- No license; no nanoflann bench code in the repo (testperformance.cpp is only vs OpenCV FLANN); independent OpenFLANN tables show nanoflann faster at K=1/10, so the 4.14x claim holds only at large K.
- Security: fromStream trusts its input; in picoflann2 a corrupt or crafted file overflows a node (reads idx_count up to 255 into idx[10]); v1 resizes vectors from unchecked sizes and takes &idx[0] of empty vectors (UB). Correctness: radiusSearch ignores maxNN in both versions. Open issue #1 (2021, no reply) reports about half the speed of nanoflann on range-image data, matching the independent OpenFLANN small-k result. No licence.

## Caveats and trade-offs

First-party README numbers (2018) with no hardware, compiler, flags or k stated, and an internal inconsistency (heading says 10,000 2D points, block says 'Speed up in 3D points'). The repo has no nanoflann benchmark code: testperformance.cpp (added 2026-04-27, -O3 -march=native, KNN=10, 1,000 queries) compares picoflann v1/v2 only against OpenCV FLANN. An independent but small benchmark (LimHyungTae/OpenFLANN, 18 stars, PCL wrappers, 1,000 repeats, no hardware stated; numbers in its imgs/knn_\*.png tables) found nanoflann faster at small K: 10,000 points K=1 0.00104 ms vs 0.00149 ms and K=10 0.00213 vs 0.00358 ms; 200,000 points K=1 0.00215 vs 0.00242 ms. Picoflann is much faster only at large K (200,000 points, K=5000: 0.84 ms vs 8.36 ms). Its author concludes 'For robotics application, NanoFLANN is better'. So the 4.14x knn figure does not hold at the small K most users need. No LICENSE file (LICENSE, LICENSE.txt, LICENSE.md, COPYING all 404) and no licence header in picoflann.h, so reference only. nanoflann is not a listed incumbent here.

Minimal header-only exact kd-tree search with a small adapter API; picoflann2.h added in 2026; no license file in the repo.

## Maintenance

Dormant from 2018 until two commits on 2026-04-27 that added picoflann2.h and OpenCV benchmarks (19 commits total, 22 stars, one open unanswered issue); with no licence it is reference-only, not something to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** README gives the 1.46x/4.14x/1.25x vs nanoflann and 1.73x/1.8x/3.21x vs OpenCV FLANN figures with no hardware, compiler, flags, k or code for the nanoflann comparison; the repo's testperformance.cpp (added 2026-04-27) races only OpenCV FLANN, so first-party C.
- **Verifier notes:** README numbers match the record. I confirmed the independent OpenFLANN figures in the record's caveats from its knn_1.png and knn_3.png tables and added the 10,000-point rows. Metadata checked on github.com: 22 stars, no license, not a fork, last commit 2026-04-27 (active).
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://github.com/rmsalinas/picoflann>
  - <https://github.com/rmsalinas/picoflann/commits>
  - <https://raw.githubusercontent.com/rmsalinas/picoflann/HEAD/README.md>
  - <https://raw.githubusercontent.com/rmsalinas/picoflann/HEAD/picoflann.h>
  - <https://raw.githubusercontent.com/rmsalinas/picoflann/HEAD/picoflann2.h>
  - <https://raw.githubusercontent.com/rmsalinas/picoflann/HEAD/testperformance.cpp>
  - <https://raw.githubusercontent.com/rmsalinas/picoflann/HEAD/CMakeLists.txt>
  - <https://github.com/LimHyungTae/OpenFLANN>
  - <https://raw.githubusercontent.com/LimHyungTae/OpenFLANN/HEAD/README.md>
  - <https://raw.githubusercontent.com/LimHyungTae/OpenFLANN/HEAD/imgs/knn_1.png>
  - <https://raw.githubusercontent.com/LimHyungTae/OpenFLANN/HEAD/imgs/knn_3.png>
- **Sources the enricher read:**
  - <https://github.com/rmsalinas/picoflann>
  - <https://github.com/rmsalinas/picoflann/commits>
  - <https://github.com/rmsalinas/picoflann/issues?q=is%3Aissue>
  - <https://github.com/rmsalinas/picoflann/issues/1>
  - <https://raw.githubusercontent.com/rmsalinas/picoflann/HEAD/README.md>
  - <https://raw.githubusercontent.com/rmsalinas/picoflann/HEAD/picoflann.h>
  - <https://raw.githubusercontent.com/rmsalinas/picoflann/HEAD/picoflann2.h>
  - <https://raw.githubusercontent.com/rmsalinas/picoflann/HEAD/testperformance.cpp>
  - <https://raw.githubusercontent.com/rmsalinas/picoflann/HEAD/test_accuracy.cpp>
  - <https://raw.githubusercontent.com/rmsalinas/picoflann/HEAD/CMakeLists.txt>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/rmsalinas/picoflann`) · [data/wave8/enrich/raw/github_com_rmsalinas_picoflann.json](../../../data/wave8/enrich/raw/github_com_rmsalinas_picoflann.json) (enrichment confidence 0.75)

</details>
