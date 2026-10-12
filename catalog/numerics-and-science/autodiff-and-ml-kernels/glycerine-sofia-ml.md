# sofia-ml

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🔴 abandoned

> Stochastic pairwise-descent linear SVM and ranking trainer for sparse data; about 160x faster than SVM-perf RankSVM on RCV1.

| | |
|---|---|
| **Beats** | SVM-perf (SVM-perf-roc), SVM-light and SVM-struct-rank (Joachims' RankSVM solvers); for data parsing, Shalev-Shwartz's reference Pegasos and svm_perf |
| **Claimed result** | RCV1 E311, CPU seconds for training at equal ROC area 0.9992: SPD Pegasos 0.20 s and SPD SGD-SVM 0.20 s (Passive-Aggressive 0.22 s, ROC area 0.9990) vs SVM-perf-roc 31.92 s (about 160x, derived from page data; the paper says more than 150x) and SVM-struct-rank 30,716.33 s. LETOR tasks: 0.2 to 0.3 CPU s per task, up to 100 times faster than SVM-light RankSVM and up to 5 times faster than SVM-struct-rank. README: reads and parses data nearly 10 times faster than the reference Pegasos implementation and nearly 3 times faster than svm_perf. |
| **Workload** | Training a pairwise ranker equivalent to RankSVM by stochastic pairwise descent (100,000 stochastic steps): RCV1 E311 task with 781,265 training examples optimising ROC area, and LETOR 3.0 and 4.0 tasks of up to 70,000 examples; the README adds file read and parse speed. |
| **Metric** | throughput |
| **Hardware** | dual-core 2.8GHz laptop with 2G RAM (CPU model not stated) |
| **Adoption** | 63 stars on this GitHub import (15 on rrenaud/sofia-ml); cited in learning-to-rank papers (not verified here) |
| **Last commit** | 2016-02-13 |
| **Links** | [repository](https://github.com/glycerine/sofia-ml) · [benchmark](https://raw.githubusercontent.com/glycerine/sofia-ml/HEAD/papers/stochastic-rank.pdf) |

## Verdict

The author's NIPS 2009 workshop paper (checked into papers/stochastic-rank.pdf) timed 100,000 stochastic pairwise steps on RCV1 E311 (781,265 training examples) at 0.20 CPU s for SPD Pegasos and SGD-SVM vs 31.92 s for SVM-perf-roc and 30,716.33 s for SVM-struct-rank, all at ROC area 0.9992, and reports 0.2 to 0.3 CPU s per LETOR task, up to 100x faster than SVM-light and up to 5x faster than SVM-struct-rank. All runs were on an unnamed dual-core 2.8 GHz laptop with 2 GB RAM; the repo Makefile builds with g++ -O3 but the paper names no compiler, and the gain comes from an approximate SGD solver against exact solvers, not from faster code for the same algorithm.

## Use it when

- Linear pairwise ranking or ROC-area optimisation over large sparse data (text, click logs) in SVM-light format, where SVM-light or SVM-perf RankSVM takes minutes to hours.
- Heavily imbalanced binary problems (RCV1 E311 has 0.2% positives): the roc and balanced-stochastic loops sample a positive and a negative in O(1) per step.
- Cheap baselines and parameter sweeps: 100,000 steps took 0.2 to 0.3 CPU s per task in the paper, so many lambda values cost little.
- You want a small, dependency-free, Apache-2.0 C++ codebase (a few thousand lines in src/) to vendor and patch, and the data fits in RAM.

## Skip it when

- You need non-linear models or kernels, or LETOR-style dense features where gradient-boosted rankers are the norm: it trains linear models only.
- You need the exact RankSVM optimum: the timed runs used 100,000 steps, while the paper's own convergence trials show the Pegasos and SGD-SVM objectives settle only after about 10^6 steps; equal ROC area on RCV1 E311 is the only quality evidence for the speed claim.
- Production use without patching: abandoned since 2010 (GitHub copy is a 2016 Google Code export), with 14 imported issues still open, including memory-safety bugs in qid parsing, dimensionality handling and hashed models.
- Multi-threaded, multi-class or multi-label training: single-threaded with global rand(), no multi-class or multi-label support (issues #5 and #17).
- Windows/MSVC builds: sampling uses rand() % n, and with MSVC's RAND_MAX of 32767 only the first 32,768 examples can be drawn; modern compilers also need missing &lt;cstdlib&gt;/&lt;stdio.h&gt; includes (issue #15).

## How it is fast

Stochastic pairwise descent: instead of building the quadratic set of preference pairs or solving the RankSVM problem with SVM-light's QP or SVM-perf/SVM-struct cutting planes, each step samples one candidate pair in constant time from an index of examples grouped by (qid, label) and takes a hinge-loss gradient step, for a fixed step count (default 100,000) that does not grow with n. The weight vector is stored as a scalar times a dense float array, so the L2 shrink is an O(1) scale update and the Pegasos projection uses an incrementally tracked squared norm; each step therefore costs O(nnz) of the two sparse vectors. Data loading uses a 40 MB ifstream buffer and atoi/atof per token rather than stream extraction.

## Compared with alternatives

Among catalogued ML siblings, pick sofia-ml over XGBoost or CatBoost ranking objectives when you want a linear pairwise ranker on very sparse, high-dimensional features trained in seconds, and over mlpack when you specifically need ROC-area or RankSVM-style pairwise sampling; prefer those maintained libraries for non-linear accuracy, multi-class support or anything that must be memory-safe without patching.

## Integration

| | |
|---|---|
| **Form** | CLI binary built by a plain Makefile, or source-drop of the src/\*.cc files into your project |
| **Dependencies** | none (C++ standard library only) |
| **Minimum toolchain** | pre-C++11 C++ built with 'g++ -O3 -lm -Wall'; GCC 4.7 and later need the missing includes added (issue #15) |
| **Platforms** | any POSIX system with g++; Windows not supported or tested |
| **Thread safety** | Not thread-safe: training draws from the global rand()/srand state and mutates a shared weight vector; no concurrency support. |
| **Drop-in for the baseline** | partial — reads the same SVM-light/SVM-perf input format (including qid), but command-line flags, model format and solver (approximate SGD vs exact RankSVM) differ |

## Gotchas

- qid parsing bug (issue #7, reported 2012, author said a fix was ready in 2013 but none was uploaded): SfSparseVector::Init strncpy's the qid into an uninitialised char[1000] without a terminator, so group ids can pick up trailing bytes from earlier lines and the rank, query-norm-rank and combined-ranking loops may merge or split queries; a qid at end of line or longer than 999 characters overflows. The unit test that checks the group id fails (issues #7 and #19); one reporter's workaround was to comment that assertion out (issue #15). This affects qid-based runs such as the paper's LETOR tasks, not the RCV1 roc loop.
- Dimensionality off-by-one (issue #10): AddVector checks 'feature &gt; dimensions_' instead of '&gt;=', so a feature id equal to --dimensionality writes one float past the heap array, and InnerProduct has no bounds check, so test files with feature ids beyond the model size read out of bounds. Set --dimensionality to the largest feature id plus one or more.
- --hash_mask_bits is broken for reuse: SfHashWeightVector's destructor and the base destructor both delete[] weights_ (double free when --model_in replaces it; issue #4 'malloc error'), and LoadModelFromFile always rebuilds a plain SfWeightVector, so a hashed model loaded from a file predicts without hashing or cross-product features.
- Smaller logic errors: SingleMarginPerceptronRankStep adds eta\*(a-b) without the pair sign y, so margin-perceptron with the rank loops steps the wrong way whenever a ranks below b (the roc loop always samples the positive first and is unaffected); --training_objective passes CMD_LINE_BOOLS["--lambda"] (0) so the reported objective omits regularisation (issue #12); the README's basic eta 1000/(i+1000) is 10/(i+10) in code.

## Known shortcomings

- First-party NIPS 2009 workshop paper (0.20 s vs SVM-perf-roc 31.92 s at equal ROC area) with no CPU model, compiler or flags; the speedup is an approximate SGD learner against exact solvers, so an algorithm change. The original code.google.com repo is gone (record uses the GitHub import). Apache-2.0; abandoned since 2010-07-26.
- Enricher: the paper timed 1e5 SGD steps although its own convergence trials say the objective settles only near 1e6 steps; the qid strncpy has no NUL terminator (issue #7, open since 2012), so group ids can corrupt in rank loops, possibly touching the paper's LETOR runs (unverifiable; the RCV1 roc row is unaffected); AddVector checks &gt; instead of &gt;= (OOB write, #10); hashed weight vector double free plus unhashed reload (#4); margin-perceptron rank step lacks the pair sign; --training_objective passes a bool lambda (#12); README eta 1000/(i+1000) vs code 10/(i+10).

## Caveats and trade-offs

First-party numbers by the author (D. Sculley, Google) in the paper 'Large Scale Learning to Rank' checked into the repo (papers/stochastic-rank.pdf). The PDF prints no venue; the author's commit of 2009-12-09 ('Adding NIPS workshop paper on fast learning to rank') identifies it as a NIPS 2009 workshop paper, whose review process could not be checked here, so it is treated as first-party (tier C). Hardware is a dual-core 2.8GHz laptop with 2G RAM, no CPU model; compiler and flags are not stated and the repo ships no benchmark scripts. The timing covers 100,000 SGD steps of an approximate stochastic pairwise learner against exact RankSVM solvers (SVM-light, SVM-struct-rank, SVM-perf-roc) trained to the same ROC area, so the speedup comes from an algorithm change, not faster code for the same algorithm. On LETOR the RankSVM accuracy comparison uses previously published LETOR results, and the paper does not say whether the SVM-light and SVM-struct-rank training times were rerun on the same laptop. The README's 10x (reference Pegasos) and 3x (svm_perf) data-reading claims give no method, and its 0.1 CPU s figure for 100,000 Pegasos steps on RCV1 CCAT is from a different (2.4GHz) laptop. Not compared with liblinear, Vowpal Wabbit, TensorFlow or PyTorch. The original code.google.com/p/sofia-ml page was EGRESS_BLOCKED, so this record uses glycerine's GitHub import (described on GitHub as 'Automatically exported from code.google.com/p/sofia-ml'); the last commit 2016-02-13 is the import itself, and the author's last code commit is dated 2010-07-26 ('Adding combined-ranking and combined-roc, and logistic prediction option').

Approximate SGD solvers (Pegasos, SGD-SVM, passive-aggressive, margin perceptron, ROMMA, logistic regression) for linear models on sparse data; reaches the same ranking quality as exact RankSVM on the tested sets but gives no exact optimum or kernels. Command-line tool plus C++ API.

## Maintenance

Abandoned: the author's last code commit is 2010-07-26 and the GitHub repo is a 2016 Google Code export with 14 untouched issues; it is Apache-2.0 and small enough to vendor, but fix the qid parser, the dimensionality bounds check and the hashed-weight-vector destructor before relying on it.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The checked-in paper 'Large Scale Learning to Rank' (D. Sculley) has Table 1 with RCV1 E311 CPU training seconds (SVM-struct-rank 30,716.33 s, SVM-perf-roc 31.92 s, SPD Pass-Aggr .22 s, SPD SGD-SVM .20 s, SPD Pegasos .20 s) and the LETOR text (0.2-0.3 CPU s, up to 100x vs SVM-light, up to 5x vs SVM-struct-rank), all first-party; the author's 2009-12-09 commit calls it a NIPS workshop paper, but no CPU model, compiler, flags or benchmark scripts are given, so C.
- **Verifier notes:** Every number in claimed_speedup matches the paper (Table 1 and the LETOR Training Speed paragraph; 'more than 150 times faster' than SVM-perf-roc is the paper's own phrase, 160x is derived). Metadata checked on github.com: Apache-2.0 (COPYING is the Apache License 2.0 text), 63 stars, 20 forks, not a fork, not archived, abandoned. Shortcomings: first-party workshop paper, no CPU model, compiler or flags, algorithmic speedup of an approximate SGD learner vs exact solvers, README parse-speed claims without method.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** first-party paper (verifier); enricher w8 pair-030
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/glycerine/sofia-ml/HEAD/papers/stochastic-rank.pdf>
  - <https://raw.githubusercontent.com/glycerine/sofia-ml/HEAD/README>
  - <https://raw.githubusercontent.com/glycerine/sofia-ml/HEAD/COPYING>
  - <https://github.com/glycerine/sofia-ml>
  - <https://github.com/glycerine/sofia-ml/commits>
- **Sources the enricher read:**
  - <https://github.com/glycerine/sofia-ml>
  - <https://github.com/glycerine/sofia-ml/tree/master/src>
  - <https://github.com/glycerine/sofia-ml/issues>
  - <https://github.com/glycerine/sofia-ml/issues/7>
  - <https://github.com/glycerine/sofia-ml/issues/10>
  - <https://github.com/glycerine/sofia-ml/issues/15>
  - <https://raw.githubusercontent.com/glycerine/sofia-ml/HEAD/README>
  - <https://raw.githubusercontent.com/glycerine/sofia-ml/HEAD/eval.pl>
  - <https://raw.githubusercontent.com/glycerine/sofia-ml/HEAD/papers/stochastic-rank.pdf>
  - <https://raw.githubusercontent.com/glycerine/sofia-ml/HEAD/src/Makefile>
  - <https://raw.githubusercontent.com/glycerine/sofia-ml/HEAD/cluster-src/Makefile>
  - <https://raw.githubusercontent.com/glycerine/sofia-ml/HEAD/src/sofia-ml.cc>
  - <https://raw.githubusercontent.com/glycerine/sofia-ml/HEAD/src/sofia-ml-methods.cc>
  - <https://raw.githubusercontent.com/glycerine/sofia-ml/HEAD/src/sofia-ml-methods.h>
  - <https://raw.githubusercontent.com/glycerine/sofia-ml/HEAD/src/sf-weight-vector.cc>
  - <https://raw.githubusercontent.com/glycerine/sofia-ml/HEAD/src/sf-weight-vector.h>
  - <https://raw.githubusercontent.com/glycerine/sofia-ml/HEAD/src/sf-sparse-vector.cc>
  - <https://raw.githubusercontent.com/glycerine/sofia-ml/HEAD/src/sf-sparse-vector.h>
  - <https://raw.githubusercontent.com/glycerine/sofia-ml/HEAD/src/sf-data-set.cc>
  - <https://raw.githubusercontent.com/glycerine/sofia-ml/HEAD/src/sf-data-set.h>
  - <https://raw.githubusercontent.com/glycerine/sofia-ml/HEAD/src/sf-hash-weight-vector.cc>
  - <https://raw.githubusercontent.com/glycerine/sofia-ml/HEAD/src/sf-hash-inline.cc>
  - <https://github.com/npinto/bottou-sgd>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/glycerine/sofia-ml`) · [data/wave8/enrich/raw/github_com_glycerine_sofia_ml.json](../../../data/wave8/enrich/raw/github_com_glycerine_sofia_ml.json) (enrichment confidence 0.75)

</details>
