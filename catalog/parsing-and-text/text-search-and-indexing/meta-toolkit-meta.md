# MeTA

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [Text search and indexing](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT OR NCSA (repo carries LICENSE.mit and LICENSE.ncsa, both copyright 2016 Sean Massung and Chase Geigle; neither file states how they combine; both OSI-approved)` · 🔴 abandoned

> C++ text retrieval and analysis toolkit; its ACL 2016 demo paper reports faster indexing than Lucene and Indri and faster linear classification than LIBLINEAR.

| | |
|---|---|
| **Beats** | Lucene (indexing); Indri; LIBLINEAR (classification) |
| **Claimed result** | Snippet only (paper unreachable). Indexing, Blog06: MeTA 11m 23s vs Lucene 20m 23s vs Indri 55m 40s (about 1.8x vs Lucene, 4.9x vs Indri, derived from snippet data; these Blog06 and Lucene figures come only from the search agent's garbled snippet and were not corroborated by this verifier's searches). Gov2 (147 GB, 25.2M docs): MeTA 1h 12m 10s vs Lucene 1h 59m 42s vs Indri 8h 13m 43s (about 1.7x vs Lucene and 6.8x vs Indri, derived from snippet data; a second summary corroborates MeTA 1h12m vs Indri over eight hours). Classification, 20news: MeTA 80.1% accuracy in 0.648 s vs LIBLINEAR 79.4% in 2.58 s (about 4x, derived from snippet data; timing covers training plus testing and excludes IO). Webspam: MeTA 99.4% accuracy in 1m 16s; LIBLINEAR and SVMmulticlass could not run for lack of memory (a capability result, not a speed ratio). |
| **Workload** | Index build time on the Blog06 and Gov2 (147 GB) web collections against Lucene and Indri; linear classification time and accuracy on 20news and Webspam against LIBLINEAR, per the ACL 2016 system-demonstration paper (numbers read from search-result summaries only). |
| **Metric** | throughput |
| **Adoption** | 719 stars |
| **Last commit** | 2017-08-20 |
| **Links** | [repository](https://github.com/meta-toolkit/meta) · [benchmark](https://aclanthology.org/P16-4016.pdf) |

## Verdict

These are first-party figures from the authors' ACL 2016 system-demonstration paper, seen only through search snippets. Index build time was Gov2 about 1h12m vs about 2h vs about 8h14m and Blog06 11m23s vs 20m23s vs 55m40s for MeTA vs Lucene vs Indri (Blog06 uncorroborated). Linear classification on 20news reached 80.1% in 0.648 s vs LIBLINEAR's 79.4% in 2.58 s, and on Webspam MeTA finished in 1m16s where LIBLINEAR ran out of memory. Hardware, compiler, thread counts and baseline versions are unknown, and no benchmark code is public.

## Use it when

- Research or coursework that needs search, text analysis, classification and topic models over the same index in one C++ (or Python, via metapy) toolkit.
- Building an inverted index over a multi-gigabyte static collection on a multicore machine, where MeTA's parallel chunked indexer is reported to finish Gov2 in about 1h12m versus about 8h for Indri (snippet-only figures).
- Linear text classification (SVM or logistic loss via SGD) on sparse bag-of-words features where a few passes of online SGD are accurate enough and LIBLINEAR's exact solver is slower.
- Training on datasets larger than RAM: the project's tutorial trains an SGD SVM on about 1.2 GB of rcv1.binary data in mini-batches with a 128 MB maximum resident set.

## Skip it when

- Production search services: there is no query server, replication, near-real-time updates or a published query-throughput comparison. The snippets say retrieval speed was roughly even with Lucene and Indri.
- Anything needing maintenance: master was last changed 2017-08-20 (v3.0.2), develop in 2018, and 50 issues are open, including unanswered build failures and a segfault (#209).
- Modern toolchains out of the box: CMake requires exactly ICU 58.2 and otherwise tries to download it from download.icu-project.org, which no longer serves it (issue #216, open since 2020-05-13). Windows is documented only for MinGW-w64 under MSYS2 (no MSVC guide, and ICU auto-build refuses non-MinGW Windows).
- Exact (non-SGD) SVM or logistic-regression solutions: MeTA's speed advantage over LIBLINEAR comes from running a different, approximate algorithm.
- 32-bit targets: support is best-effort because the indexes rely heavily on memory mapping.

## How it is fast

Indexing tokenizes documents on all hardware threads by default (indexer-num-threads). Each thread fills a RAM-budgeted in-memory chunk (a hash probe_set of postings buffers) and flushes it to disk, with up to 8 concurrent writers. The chunks are then combined by an external multiway merge, and a compression pass writes gap-encoded postings in 7-bit variable-byte form plus a memory-mapped, B+-tree-like vocabulary map. Classification uses SGD with the normalized adaptive gradient (NAG) method of Ross, Mineiro and Langford, L2 regularization via the scalar-times-vector trick and L1 via Tsuruoka's cumulative penalty, and it can stream mini-batches from the index instead of loading the whole dataset like LIBLINEAR.

## Compared with alternatives

Pick MeTA over Tantivy, PISA, IResearch or SeekStorm only when you want search plus text mining (classifiers, topic models, language models, parsers) over one index for research or teaching. For query throughput or production indexing, those siblings are maintained and have current independent search-benchmark-game numbers against Lucene, while MeTA has none.

## Integration

| | |
|---|---|
| **Form** | libraries built with CMake (meta-index, meta-utf and others, plus command-line tools), or the metapy Python wheel |
| **Dependencies** | ICU (exactly 58.2, else built from source), zlib, threads; optional liblzma and jemalloc; git submodules (cpptoml, meta-cmake and others) |
| **Minimum toolchain** | C++14 as set in CMakeLists (the code claims C++11); Travis CI covered GCC 4.8 to 5 and Clang, README guides go up to GCC 5.3; the last fixes target GCC 7.1.1 (2017) |
| **Platforms** | Linux, macOS, Windows via MinGW-w64/MSYS2 only; 64-bit strongly recommended |
| **Thread safety** | not documented for concurrent use of an index; indexing and some algorithms are internally multithreaded |
| **Drop-in for the baseline** | no |

## Gotchas

- The only speed numbers come from the authors' ACL 2016 demo paper, which was never opened here (all ACL Anthology hosts are blocked). The Blog06/Lucene indexing figures rest on a single garbled search snippet. Hardware, compiler, thread counts and Lucene, Indri and LIBLINEAR versions are all unknown, and MeTA's indexer uses every hardware thread by default.
- The record's 'LIBLINEAR killed while loading' evidence is from the online-learning tutorial, which uses rcv1.binary with the splits reversed (about 1.2 GB of training data, run in mini-batches of 50,000 documents on a machine with about 200 MB of RAM), not Webspam. The tutorial itself says the dataset 'is not actually large enough to require an online learning algorithm'.
- The 20news comparison pits SGD (an approximate online method) against LIBLINEAR's exact solver. The roughly 4x time gap (0.648 s vs 2.58 s, IO excluded) reflects the algorithm choice, not a faster implementation of the same solver.
- Building from a clean checkout usually fails at the ICU step: FindOrBuildICU accepts only ICU 58.2, and any other system version triggers a download from a dead URL. Users report fixing it by pointing the URL in CMakeLists.txt at the unicode-org/icu GitHub release (issue #216, no maintainer reply).

## Known shortcomings

- Only numbers are the authors' ACL 2016 demo paper (P16-4016), unreachable here; snippets back Gov2 indexing 1h12m vs Indri over 8h, 20news 80.1% in 0.648 s vs LIBLINEAR 79.4% in 2.58 s, Webspam 99.4% in 1m16s with LIBLINEAR out of memory; Blog06 and Lucene timings unbacked. First-party, no harness, hardware or versions. Wrong wave-8 category (no autodiff-and-ml-kernels baseline compared); moved to text-search-and-indexing. Licence MIT OR NCSA. Abandoned (master 2017-08-20, develop 2018-12-16). Paper access could lift to B.
- Enricher: paper still blocked (aclanthology.org, aclweb.org 403); the LIBLINEAR-killed tutorial uses rcv1.binary (about 1.2 GB, reversed splits, 200 MB RAM machine), not Webspam, and the 20news 4x is SGD vs LIBLINEAR's exact solver (different algorithm); thread counts and versions unknown. Build breaks: CMake accepts only ICU 58.2, else downloads from a dead URL (issue #216).
- Domain set to parsing-and-text to match its text-search-and-indexing category.

## Caveats and trade-offs

Snippet only: aclanthology.org, preview.aclanthology.org, liner.com, lacuna.tiptreesystems.com and edutechwiki were unreachable, so the paper's tables were never opened by search agent or verifier; the Blog06/Lucene indexing figures rest on one garbled WebSearch extract, while the Gov2-vs-Indri, 20news and Webspam figures are corroborated by a second snippet source. The numbers are first-party (the MeTA authors' ACL 2016 demo paper); hardware, compiler, flags, Lucene/Indri/LIBLINEAR versions and query-speed results are unknown (one summary says retrieval performance across the three systems was roughly even; index sizes comparable, Lucene 2.06 GB vs MeTA 2.84 GB on Blog06 and 11.02 GB vs 10.24 GB on Gov2). The repo carries no benchmark code; the website's online-learning tutorial only says LIBLINEAR is killed while loading the 1.2 GB Webspam training set, whereas MeTA's online SGD runs in 128 MB RSS. Filed under autodiff-and-ml-kernels, but none of that category's baselines (oneDNN, cuDNN, XNNPACK, Eigen tensor) are compared; MeTA is a text-retrieval/indexing and text-classification toolkit, which fits text-search-and-indexing better. Last commit on master 2017-08-20 (hotfix-v3.0.2 merge); the develop branch was last touched 2018-12-16 (CI/build bumps); abandoned either way.

Index-based, out-of-core design: classification can stream data from the index (a 1.2 GB training set ran with a 128 MB resident set in the project tutorial) but the toolkit is a full framework (text analysis, retrieval, classification, topic models, parsers), so Lucene and Indri are only comparable on the retrieval/indexing part. Repo ships both LICENSE.mit and LICENSE.ncsa.

## Maintenance

Abandoned since 2017-08-20 (v3.0.2; develop last touched 2018) with 50 open issues and no maintainer replies on build breakages; MIT/NCSA-licensed and usable for teaching and research if you pin ICU 58.2 and an older GCC or Clang.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The only numbers are in the authors' own ACL 2016 demo paper (P16-4016), which could not be opened here (aclanthology.org and preview.aclanthology.org do not resolve; liner.com and lacuna review pages also blocked); WebSearch snippets corroborate the Gov2 (MeTA 1h12m vs Indri over 8h), 20news (80.1% in 0.648 s vs LIBLINEAR 79.4% in 2.58 s) and Webspam (99.4% in 1m16s, LIBLINEAR and SVMmulticlass fail on memory) figures, but no benchmark code, hardware, compiler or baseline versions are public. A peer-reviewed paper could support B once its tables are read; snippet-only evidence stays at C.
- **Verifier notes:** Real, peer-reviewed toolkit (719 stars, 240 forks) whose speed claims could not be checked against the PDF because every ACL Anthology host is blocked here; the Gov2/Indri, 20news and Webspam numbers are corroborated by independent snippets, the Blog06/Lucene numbers are not. Shortcomings: first-party numbers, no public benchmark harness or methodology, baselines not in list, wrong category (better text-search-and-indexing), abandoned since 2017-2018; a paper-access retier could lift it to B.
- **Fields the verifier corrected:** `license`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-172 (wave 8); enricher w8 pair-032; orchestrator domain fix 2026-10-11
- **Pages the verifier opened:**
  - <https://github.com/meta-toolkit/meta>
  - <https://github.com/meta-toolkit/meta/commits>
  - <https://github.com/meta-toolkit/meta/commits/develop>
  - <https://github.com/meta-toolkit>
  - <https://github.com/meta-toolkit/meta-toolkit.org>
  - <https://raw.githubusercontent.com/meta-toolkit/meta/HEAD/README.md>
  - <https://raw.githubusercontent.com/meta-toolkit/meta/HEAD/LICENSE.mit>
  - <https://raw.githubusercontent.com/meta-toolkit/meta/HEAD/LICENSE.ncsa>
  - <https://raw.githubusercontent.com/meta-toolkit/meta-toolkit.org/master/index.md>
  - <https://raw.githubusercontent.com/meta-toolkit/meta-toolkit.org/master/online-learning.md>
  - <https://raw.githubusercontent.com/meta-toolkit/meta-toolkit.org/master/classify-tutorial.md>
  - <https://raw.githubusercontent.com/meta-toolkit/meta-toolkit.org/master/search-tutorial.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/meta-toolkit/meta/master/README.md>
  - <https://raw.githubusercontent.com/meta-toolkit/meta/master/CMakeLists.txt>
  - <https://raw.githubusercontent.com/meta-toolkit/meta/master/CHANGELOG.md>
  - <https://raw.githubusercontent.com/meta-toolkit/meta/master/.travis.yml>
  - <https://raw.githubusercontent.com/meta-toolkit/meta/master/config.toml>
  - <https://raw.githubusercontent.com/meta-toolkit/meta/master/src/index/inverted_index.cpp>
  - <https://raw.githubusercontent.com/meta-toolkit/meta/master/include/meta/index/postings_inverter.h>
  - <https://raw.githubusercontent.com/meta-toolkit/meta/master/include/meta/index/postings_inverter.tcc>
  - <https://raw.githubusercontent.com/meta-toolkit/meta/master/include/meta/index/chunk_reader.h>
  - <https://raw.githubusercontent.com/meta-toolkit/meta/master/include/meta/io/packed.h>
  - <https://raw.githubusercontent.com/meta-toolkit/meta/master/include/meta/index/vocabulary_map.h>
  - <https://raw.githubusercontent.com/meta-toolkit/meta/master/include/meta/index/postings_data.tcc>
  - <https://raw.githubusercontent.com/meta-toolkit/meta/master/include/meta/index/postings_stream.h>
  - <https://raw.githubusercontent.com/meta-toolkit/meta/master/include/meta/classify/classifier/sgd.h>
  - <https://raw.githubusercontent.com/meta-toolkit/meta/master/include/meta/learn/sgd.h>
  - <https://raw.githubusercontent.com/meta-toolkit/meta/master/src/learn/sgd.cpp>
  - <https://raw.githubusercontent.com/meta-toolkit/meta-cmake/master/FindOrBuildICU.cmake>
  - <https://github.com/meta-toolkit/meta/issues>
  - <https://github.com/meta-toolkit/meta/issues/216>
  - <https://github.com/meta-toolkit/meta/commits/master>
  - <https://github.com/meta-toolkit/meta-toolkit.org>
  - <https://raw.githubusercontent.com/meta-toolkit/meta-toolkit.org/master/index.md>
  - <https://raw.githubusercontent.com/meta-toolkit/meta-toolkit.org/master/online-learning.md>
  - <https://raw.githubusercontent.com/meta-toolkit/meta-toolkit.org/master/overview-tutorial.md>
  - <https://raw.githubusercontent.com/meta-toolkit/meta-toolkit.org/master/classify-tutorial.md>
  - <https://raw.githubusercontent.com/meta-toolkit/meta-toolkit.org/master/search-tutorial.md>
  - <https://raw.githubusercontent.com/meta-toolkit/meta-toolkit.org/master/setup-guide.md>
  - <https://raw.githubusercontent.com/meta-toolkit/meta-toolkit.org/master/KDD2017.md>
  - <https://raw.githubusercontent.com/meta-toolkit/meta-toolkit.org/master/SIGIR18.md>
  - <https://raw.githubusercontent.com/meta-toolkit/meta-toolkit.org/master/sigir-keynote-zhai.pdf>
  - <https://pypi.org/pypi/metapy/json>
  - https://aclanthology.org/P16-4016.pdf (blocked, 403)
  - https://www.aclweb.org/anthology/P16-4016.pdf (blocked, 403)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/meta-toolkit/meta`) · [data/wave8/enrich/raw/github_com_meta_toolkit_meta.json](../../../data/wave8/enrich/raw/github_com_meta_toolkit_meta.json) (enrichment confidence 0.55)

</details>
