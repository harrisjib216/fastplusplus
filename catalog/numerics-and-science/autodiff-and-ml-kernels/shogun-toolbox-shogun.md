# SHOGUN (k-means)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-3-Clause` · 🟡 stale

> Large C++ machine-learning toolbox whose 2011 k-means beat scikit-learn 0.8 about 2x; that edge did not survive.

| | |
|---|---|
| **Beats** | scikit-learn 0.8 (scikits.learn KMeans) |
| **Claimed result** | 2011 ml-benchmarks k-means 0.68 vs 1.34 s and 0.19 vs 0.51 s against scikit-learn 0.8 (Core2 1.86 GHz) with unequal algorithms; Shogun 3.2.0 later 428.86 s vs scikit-learn 32.53 s at k=100, parity (27.01 vs 27.45 s) after the 2016 rewrite (issue #2987). |
| **Workload** | k-means clustering time in seconds on the Madelon (4400 instances, 500 attributes) and Arcene datasets, from the scikit-learn project's ml-benchmarks suite; each benchmark run 10 times with extreme values removed (July 2011 results). |
| **Metric** | latency |
| **Hardware** | Intel Core2 CPU @ 1.86GHz |
| **Adoption** | 3.1k stars |
| **Last commit** | 2023-12-19 |
| **Links** | [repository](https://github.com/shogun-toolbox/shogun) · [benchmark](https://raw.githubusercontent.com/scikit-learn/ml-benchmarks/HEAD/doc/index.rst) |

## Verdict

In the scikit-learn project's ml-benchmarks (July 2011, Intel Core2 1.86 GHz, compiler and BLAS not stated, timed through the Python bindings, 10 runs with min and max dropped), Shogun 0.10.0 k-means with 9 clusters took 0.68 s vs scikit-learn 0.8's 1.34 s on the Madelon training split and 0.19 s vs 0.51 s on Arcene, with matching Madelon inertia (7.3x10^8 vs 7.4x10^8) and no Shogun inertia reported for Arcene; Shogun's 0.10 algorithm skipped points per pass and stopped stochastically, so the work was not equal.

## Use it when

- You already depend on Shogun for its kernel machines or multi-language bindings and want k-means in the same toolbox without adding another library.
- You need one ML library callable from C++, Octave, Java or R with the same object model in each.
- Small dense datasets clustered from C++ where an OpenMP Lloyd loop with optional k-means++ is enough and you can build from source.

## Skip it when

- As a faster scikit-learn: the only k-means win is from 2011 (Shogun 0.10.0 vs scikit-learn 0.8); in a 2016 issue thread Shogun 3.2.0 took 428.86 s vs scikit-learn 32.53 s at k=100 on about 20,000 points, and after the rewrite the two were at parity (27.01 s vs 27.45 s).
- SVM or nearest-neighbour work expecting a speedup: in the same 2011 suite Shogun was slower than scikit-learn on SVM (Madelon 5.63 s vs 5.20 s) and kNN (Madelon 1.36 s vs 0.57 s).
- Projects that need a maintained dependency: develop has had a single commit since December 2020 (2023-12-19) and 413 open issues.
- Easy installation: the documented `pip install shogun-ml` package is not on PyPI (Not Found), the vcpkg port path returns 404, and a source build needs CMake, Eigen 3.3+, SWIG for interfaces and about 4 GB RAM.
- Large k or very large n: src/shogun/clustering holds only GMM, Hierarchical, KMeans, KMeansBase and KMeansMiniBatch, with no Elkan or Hamerly bound-based k-means (issue #3428 'Add elkan kmeans' was closed); use mlpack or oneDAL instead.

## How it is fast

The k-means that was timed in 2011 (Shogun 0.10.0 CKMeans::clustknb) was single-threaded C++ with a random-partition start and a cheap, stochastic iteration: each pass reassigns XSize points drawn at random with replacement and stops as soon as none of the sampled points changes cluster, so it does less work per run than scikit-learn's full Lloyd passes with k-means++ seeding. The current develop-branch KMeans was rewritten (2016) into a standard Lloyd loop with precomputed squared norms in EuclideanDistance, an OpenMP-parallel assignment step, optional k-means++ seeding and a mini-batch variant.

## Compared with alternatives

Pick mlpack over Shogun for fast C++ k-means or kNN (its paper beats both scikit-learn and Shogun, and it is maintained) and oneDAL/sklearnex when you want scikit-learn's API accelerated; choose Shogun only when you already use its kernel methods or need its Octave/Java/R bindings.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | Eigen 3.3+ (required); optional BLAS/LAPACK, OpenMP, SWIG plus language dev packages for interfaces; GPL3 components are optional and must be excluded for a BSD-only build |
| **Minimum toolchain** | C++17 (CMAKE_CXX_STANDARD 17 on develop), CMake 3.8+ |
| **Platforms** | GNU/Linux, macOS, FreeBSD, Windows (MSVC) per README; an AArch64 Fedora 33 build failure was reported (#5169, closed) |
| **Thread safety** | not documented (KMeans uses OpenMP internally in the assignment step and k-means++ seeding) |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw behind the measured numbers: Shogun 0.10.0's clustknb samples XSize points with replacement per iteration (about a third of points are never visited in a pass, as issue #2987 also notes) and stops when no sampled point changed, starting from a random partition; scikit-learn ran full Lloyd passes with k-means++ seeding and tol. The 2x and 2.7x timings therefore compare different amounts of work, the benchmark page itself says 'The shogun is failling' and leaves Shogun's Arcene inertia blank, and the code was later rewritten.
- Dead code with a sign error in 0.10.0: the online centre update for the gaining cluster uses `-=` where its own comment says `mu_old + (x - mu_old)/(n+1)`; it is masked because MUSRECALC recomputes all means at the start of each iteration and distances read a copy of the centres.
- Current Lloyd_KMeans logs with `if (iter%(max_iter/10) == 0)`: setting max_iter to 1-9 makes this an integer modulo by zero on the first non-converged iteration (a SIGFPE crash on x86), read from source and not tested.
- Default seeding is k random points (use_kmeanspp false); pass use_kmpp=true to match scikit-learn's k-means++ default. The 2011 harness timed only the training split loaded by misc.load_data (madelon_train / arcene_train), not all 4400 Madelon instances, and the Shogun timer also includes building RealFeatures and the distance object.

## Known shortcomings

- Numbers from the scikit-learn ml-benchmarks page (July 2011, Shogun 0.10 vs scikit-learn 0.8, Core2 1.86 GHz): the page itself notes 'shogun is failling' and leaves the Arcene inertia blank; k-means settings not equalised; HEAD benchmark code is newer than the run; Shogun is slower than scikit-learn on SVM and kNN. Stale (last commit 2023-12-19).
- Enricher: Shogun 0.10.0's clustknb (tag shogun_0.10.0) reassigns XSize random points with replacement each pass (about a third skipped, as issue #2987 also says), stops when no sampled point changed, and starts from a random partition, while scikit-learn ran full Lloyd passes with k-means++ seeding, so the 2011 work was unequal; the centre update has a sign error (-=) in dead code under MUSRECALC. The edge did not last: issue #2987 (2016) has Shogun 3.2.0 at 428.86 s vs scikit-learn 32.53 s at k=100 and parity (27.01 vs 27.45 s) after the rewrite. Current KMeans divides by zero in iter%(max_iter/10) when max_iter is 1-9 (read from code). Dormant (one commit since Dec 2020); pip install shogun-ml not on PyPI; vcpkg port 404.

## Caveats and trade-offs

Independent third-party suite (scikit-learn project's ml-benchmarks by Fabian Pedregosa, code public in benchmarks/), but from July 2011 with Shogun 0.10.0 and scikit-learn 0.8, both far out of date; scikit-learn's KMeans has since been rewritten, so the result says nothing about current versions. Compiler, flags and BLAS build are not stated, so B and not A. Timings go through the Python interfaces, so interface overhead is included. The page itself says 'Note: The shogun is failling ..' next to the k-means section and leaves the Shogun inertia for Arcene blank, so the Arcene win (0.19 s vs 0.51 s) is unconfirmed; Madelon inertia 7.3x10^8 (Shogun) vs 7.4x10^8 (scikit-learn) matches. Settings are not equalised: the harness passes n_init=1 to scikit-learn and runs Shogun's KMeans with its defaults. The bench_kmeans.py at HEAD imports 'sklearn' (the post-0.9 package name) while its inertia helper imports 'scikits.learn', so the public code is a later revision than the one that produced the July 2011 table. Shogun is not the fastest on Madelon k-means (milk 0.67 s) and is slower than scikit-learn on SVM (Madelon 5.63 s vs 5.20 s, Arcene 0.39 s vs 0.38 s) and nearest neighbours (Madelon 1.36 s vs 0.57 s, Arcene 0.22 s vs 0.09 s). The milk documentation page (pythonhosted.org/milk/benchmarks.html, Intel Core2 6600 2.40GHz, versions not stated, times normalised to the fastest) shows the same direction for k-means: Shogun 2.02, scikits.learn 6.74, milk 1.0. [retier] Sampled reassignment with replacement, early stop when no sampled point changed, random-partition start; page says 'shogun is failling' and leaves Arcene inertia blank; slower than scikit-learn on SVM and kNN; current KMeans divides by zero for max_iter 1-9; dormant since 2020; not on PyPI.

Large C++ toolbox with SWIG-generated Python, Octave, Java and other interfaces; the library core is BSD-3-Clause with some optional GPL3 components (check which components a build pulls in).

## Maintenance

Effectively dormant (last burst of commits December 2020, one commit on 2023-12-19, 413 open issues) and hard to install from binaries now; the BSD-3-Clause core is usable from source, but nothing here shows it is faster than current scikit-learn.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now C.
- **Tier reason:** Independent of Shogun: the scikit-learn project's public ml-benchmarks suite (benchmarks/bench_kmeans.py, benchmarks/misc.py, 10 runs with min and max dropped) shows k-means Madelon 0.68 s vs 1.34 s and Arcene 0.19 s vs 0.51 s on an 'Intel Core2 CPU @ 1.86GHz'. Compiler, flags and build of the compiled packages are not stated, so B and not A.
- **Retiered** B to C: Lowered B to C: the independent 2011 numbers were measured on a k-means that did unequal work (stochastic sampled reassignment with early stop and random-partition start vs scikit-learn's full Lloyd passes with k-means++), the page itself flags Shogun as failing, and the code was later rewritten to parity (issue #2987), so the measured code no longer exists and the comparison was never like for like.
- **Verifier notes:** Numbers and hardware match doc/index.rst exactly; repo metadata checked (BSD-3-Clause with optional GPL3 components, 3.1k stars, 1.0k forks, last commit 2023-12-19, so stale). Shortcomings to record: 2011-vintage versions, page flags Shogun as failing on k-means and Arcene inertia is blank, k-means settings not equalised, slower than scikit-learn on SVM and kNN in the same suite.
- **Fields the verifier corrected:** `caveats`, `claimed_speedup`
- **Shortcomings recorded by:** verifier batch-178 (wave 8); enricher w8 pair-040
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/scikit-learn/ml-benchmarks/HEAD/doc/index.rst>
  - <https://raw.githubusercontent.com/scikit-learn/ml-benchmarks/HEAD/README.rst>
  - <https://raw.githubusercontent.com/scikit-learn/ml-benchmarks/HEAD/benchmarks/bench_kmeans.py>
  - <https://raw.githubusercontent.com/scikit-learn/ml-benchmarks/HEAD/benchmarks/misc.py>
  - <https://pythonhosted.org/milk/benchmarks.html>
  - <https://github.com/shogun-toolbox/shogun>
  - <https://github.com/shogun-toolbox/shogun/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/scikit-learn/ml-benchmarks/HEAD/doc/index.rst>
  - <https://raw.githubusercontent.com/scikit-learn/ml-benchmarks/HEAD/README.rst>
  - <https://raw.githubusercontent.com/scikit-learn/ml-benchmarks/HEAD/benchmarks/bench_kmeans.py>
  - <https://raw.githubusercontent.com/scikit-learn/ml-benchmarks/HEAD/benchmarks/misc.py>
  - <https://raw.githubusercontent.com/shogun-toolbox/shogun/HEAD/README.md>
  - <https://raw.githubusercontent.com/shogun-toolbox/shogun/develop/src/shogun/clustering/KMeans.cpp>
  - <https://raw.githubusercontent.com/shogun-toolbox/shogun/develop/src/shogun/clustering/KMeans.h>
  - <https://raw.githubusercontent.com/shogun-toolbox/shogun/develop/src/shogun/clustering/KMeansBase.cpp>
  - <https://raw.githubusercontent.com/shogun-toolbox/shogun/develop/src/shogun/clustering/KMeansBase.h>
  - <https://raw.githubusercontent.com/shogun-toolbox/shogun/develop/src/shogun/clustering/KMeansMiniBatch.cpp>
  - <https://raw.githubusercontent.com/shogun-toolbox/shogun/develop/doc/readme/INSTALL.md>
  - <https://raw.githubusercontent.com/shogun-toolbox/shogun/develop/CMakeLists.txt>
  - <https://raw.githubusercontent.com/shogun-toolbox/shogun/shogun_0.10.0/src/libshogun/clustering/KMeans.cpp>
  - <https://github.com/shogun-toolbox/shogun>
  - <https://github.com/shogun-toolbox/shogun/commits/develop>
  - <https://github.com/shogun-toolbox/shogun/issues?q=is%3Aissue+kmeans>
  - <https://github.com/shogun-toolbox/shogun/issues/2987>
  - <https://github.com/shogun-toolbox/shogun/issues/2951>
  - <https://pypi.org/pypi/shogun-ml/json>
  - <https://pypi.org/pypi/shogun/json>
  - <https://raw.githubusercontent.com/microsoft/vcpkg/master/ports/shogun/vcpkg.json>
  - <https://github.com/shogun-toolbox/shogun/tree/develop/src/shogun/clustering>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/shogun-toolbox/shogun`) · [data/wave8/enrich/raw/github_com_shogun_toolbox_shogun.json](../../../data/wave8/enrich/raw/github_com_shogun_toolbox_shogun.json) (enrichment confidence 0.6)

</details>
