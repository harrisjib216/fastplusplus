# FAISS

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Meta's C++ library for approximate nearest-neighbour search over dense vectors on CPU and GPU; beat the 2016 billion-scale ANN papers 4-5x.

| | |
|---|---|
| **Beats** | Babenko et al. CVPR'16 inverted multi-index search on CPU (Deep1B); Wieschollek et al. CVPR'16 GPU product-quantization search (Bigann) |
| **Claimed result** | Deep1B at R@1 about 0.45: Faiss OPQ20_80,IMI2x14,PQ20 on 1 CPU thread 3.66 ms/vector (R@1 0.4561) vs Babenko et al. CVPR'16 on 1 CPU thread 20 ms/vector (R@1 0.45), about 5.5x (derived from page data). Bigann at R@10 about 0.35: Faiss CPU 20 threads 0.035 ms/vector (R@10 0.349) and Faiss on one Titan X 0.0340 ms/vector (R@10 0.376) vs Wieschollek et al. CVPR'16 on a Titan X 0.15 ms/vector (R@10 0.35), about 4.3x and 4.4x (derived from page data). |
| **Workload** | Approximate nearest-neighbour query time per vector on 1-billion-vector datasets with compressed codes: Deep1B (96-dim, 20-byte PQ codes, about 25 GB RAM, recall@1) and Bigann (128-dim SIFT, 8-byte codes, recall@10). |
| **Metric** | latency |
| **Hardware** | Archived comparison tables: Faiss rows on 'CPU (1 thread)', 'CPU (20 threads)', one Titan X, 4\*K40 and 8\*TitanX, CPU model not stated for these rows; baseline rows are the figures published in the 2016 papers on their own hardware (Titan X GPU; 1 CPU thread). The page's current bench_all_ivf experiments (no external baseline) ran on a 2.2 GHz Xeon E5-2698 (80 cores, 32 used). |
| **Adoption** | 41.1k stars |
| **Last commit** | 2026-09-15 |
| **Links** | [repository](https://github.com/facebookresearch/faiss) · [benchmark](https://github.com/facebookresearch/faiss/wiki/Indexing-1G-vectors) |

## Verdict

In the archived 'Older results' tables of Faiss's own wiki, a one-thread CPU index (OPQ20_80,IMI2x14,PQ20) answered Deep1B queries at R@1 0.456 in 3.66 ms each versus the 20 ms at R@1 0.45 that Babenko et al. (CVPR'16) published for one thread (about 5.5x), and on Bigann at R@10 about 0.35 Faiss took 0.035 ms per query on 20 CPU threads or 0.034 ms on one Titan X versus 0.15 ms published by Wieschollek et al. (CVPR'16) on a Titan X (about 4.3x and 4.4x). The baselines are figures copied from the papers' own hardware, the times are amortised over a 10k-query batch, and no compiler, flags or CPU model are given for the compared rows.

## Use it when

- Hundreds of millions to billions of 64-1000-dimensional embeddings that must live compressed in one machine's RAM (8-64 bytes per vector) with recall you can tune against speed.
- Batched query workloads (thousands of queries per call) where queries per second matters more than single-query latency; the wiki states batching and threading give the best QPS.
- GPU brute-force or IVF k-NN, k-means clustering and k-NN graph construction on NVIDIA GPUs, with the same index types available on CPU.
- You need many index families (Flat, IVF-Flat/PQ/SQ, HNSW, NSG, RaBitQ, 4-bit fast scan, binary) behind one API, with Python tooling for training, autotuning and serialization.

## Skip it when

- Low-latency single-query serving on CPU: the 1M wiki page says one thread is about 10x slower than 20 threads and query-at-a-time another 2-3x slower, and open issue #5700 shows IndexBinaryFlat single-query search getting slower with more threads (20.36 ms at 1 thread vs 27.36 ms at 4).
- Small (about 1M vector) high-recall in-memory search where memory is not the constraint: Faiss's own wiki says nmslib HNSW is faster on SIFT1M (0.081 s vs 0.538 s for IVF16384,Flat, different machines) at the cost of more memory.
- Low-dimensional (2-3D) geometric k-NN on point clouds: a kd-tree library is simpler and exact.
- Projects that cannot take a C++20 compiler, OpenMP and a BLAS dependency, or need a header-only drop-in.
- Concurrent multi-threaded use of GPU indexes from many CPU threads without a resource object per thread.

## How it is fast

Compressed-domain search: an inverted file (k-means coarse quantizer, or an inverted multi-index) restricts the scan to a few lists, and product quantization codes are scored with asymmetric distance computation through per-query lookup tables, optionally after an OPQ rotation. Polysemous codes order PQ centroids so a cheap Hamming-distance filter rejects most codes before the table lookup, and 4-bit PQ 'fast scan' (inspired by ScaNN) keeps the lookup tables in SIMD registers; exact search is cast as BLAS GEMM, and all search work is OpenMP-parallel over queries. The GPU side uses a k-selection design that the paper abstract says runs at up to 55% of peak and gives 8.5x over the prior GPU state of the art (abstract via search snippet only).

## Compared with alternatives

None of the autodiff-and-ml-kernels siblings does vector search (the category fit is loose); in the wider catalogue the k-NN entries are low-dimensional kd-trees (nanoflann, libnabo, SPRK-tree), so pick Faiss for high-dimensional embeddings, compressed billion-scale indexes or GPU k-NN, and a kd-tree library for exact 2-3D point-cloud queries.

## Integration

| | |
|---|---|
| **Form** | static lib (libfaiss.a) or shared lib built with CMake; prebuilt conda packages faiss-cpu, faiss-gpu, faiss-gpu-cuvs; Python via SWIG; optional C API |
| **Dependencies** | BLAS (Intel MKL recommended on x86, OpenBLAS on ARM) and OpenMP; optional CUDA toolkit or AMD ROCm for GPU indexes, NVIDIA cuVS 26.06, Intel SVS, and SWIG + numpy + Python 3 for the bindings |
| **Minimum toolchain** | C++20 compiler with OpenMP 2 or later (CMAKE_CXX_STANDARD 20 in CMakeLists.txt), CMake; nvcc for GPU builds |
| **Platforms** | x86-64 Linux, macOS and Windows officially (SIMD levels generic, avx2, avx512, avx512_spr selected with FAISS_OPT_LEVEL; default is generic); aarch64 generic and SVE; conda faiss-cpu for Linux x86-64/aarch64, macOS arm64 and Windows x86-64; GPU packages Linux x86-64 only |
| **Thread safety** | CPU indexes are safe for concurrent searches and other read-only calls; anything that modifies an index needs caller-side mutual exclusion. GPU indexes are not thread-safe even for reads: each CPU thread needs its own StandardGpuResources. Calling batched search from several threads oversubscribes OpenMP. |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness note on the catalogued numbers: bench_polysemous_1bn.py and ParameterSpace::explore time one batched index.search over all 10k queries (k=100, batchsize 1&lt;&lt;30, a single run because min_test_duration is 0) and divide by the query count, so 'ms per vector' is amortised batch throughput, not per-query latency; in autotune mode the operating points are picked against the same 10k queries and ground truth they are reported on, and the wiki's command line (OPQ8_64,IMI2x14,PQ8) does not match the table row it explains (IMI2x13).
- Open bug #2120: polysemous_ht resets to 0 when an index is loaded from disk, silently disabling the Hamming pre-filter that gives polysemous indexes their speed unless the parameter is set again after read_index.
- Build and BLAS choices change speed by large factors: a plain source build defaults to FAISS_OPT_LEVEL=generic (no AVX2 fast-scan kernels), issue #3306 reports a local build 4x slower than the release, and issue #4582 reports the MKL-linked conda package about 300x slower than the OpenBLAS pip wheel for clustering on an AMD Zen 4 under Windows (closed without a fix). With OpenBLAS the wiki recommends OMP_WAIT_POLICY=PASSIVE.
- Compressed indexes need a training set and tuned parameters (nprobe, quantizer efSearch, code size); results are deterministic for a fixed thread count except PCA/OPQ training (LAPACK eigen solver) and HNSW add order.

## Known shortcomings

- Numbers come from the archived tables of the wiki Indexing-1G-vectors page; baselines are figures copied from 2016 papers on other hardware. On SIFT1M nmslib is faster. The GPU paper (arXiv 1702.08734, 8.5x over Wieschollek) was seen as a snippet only and could raise it to B once reachable.
- Enricher: the wiki's 'ms/vector' is one batched search of 10k queries (k=100), one run, divided by 10k, so it is throughput, not latency (bench_polysemous_1bn.py, AutoTune.cpp ParameterSpace::explore); autotune picks operating points on the same queries it reports recall on; the wiki command says IMI2x14 while the table row says IMI2x13. Open bugs #2120 (polysemous_ht resets to 0 after read_index) and #5700 (single-query IndexBinaryFlat slower with more threads). The wiki admits nmslib is faster on SIFT1M. Now requires C++20.

## Caveats and trade-offs

The comparison sits in the wiki's archived 'Older results' section; the current results on that page compare only Faiss configurations with each other. The baselines are numbers copied from two 2016 papers, not rerun on the same machine, and are research code rather than a library, so the ratios compare across different hardware; the Bigann CPU rows compare Faiss on a CPU against a GPU baseline, and Faiss on 1 CPU thread (0.4852 ms/vector at R@10 0.349) is about 3.2x slower than Wieschollek et al. on a Titan X (0.15 ms) (derived from page data). The wiki's Titan X row (0.0340 ms at R@10 0.376) differs from the GPU paper's 17.7 microseconds at the same recall (snippet only), which is where the README's 8.5x 'fastest GPU kNN' claim comes from. Compiler and flags are not stated (last_commit is the v1.15.1 release date from CHANGELOG.md, which also has an Unreleased section; the commit-list page returned HTTP 429). The Indexing-1M-vectors wiki page shows a library baseline beating Faiss: on SIFT1M nmslib HNSW takes 0.081 s at 1-R@1 0.8195 vs Faiss IVF16384,Flat 0.538 s at 0.8980 on CPU (the page says nmslib is faster but uses more memory; machines differ between tables). The wiki's FastScan-vs-ScaNN 1.1.1 comparison (1 thread, Xeon E5-2698) is only plotted in images and says 'faster and more accurate for all operating points before re-ranking' on SIFT1M, so no numbers were read; its '280k vs 140k QPS' HNSW comparison is against Faiss's own HNSW. The GPU paper (arXiv 1702.08734) could not be opened here (arxiv.org, ar5iv and deepai blocked); a paper-access retier could move this entry to B.

Library of many index types (flat, IVF, PQ, HNSW, FastScan 4-bit PQ, GPU variants); approximate search trades recall for speed, and compressed indexes need training and tuned parameters (nprobe, code size).

## Maintenance

Actively maintained by Meta FAIR (v1.15.1 released 2026-09-15, MIT, about 41k stars, conda packages for CPU and GPU), but the catalogued comparison is a 2017-era archived table and the wiki's current benchmarks compare only Faiss configurations with each other.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The numbers are in the archived 'Older results' tables of the first-party wiki page Indexing-1G-vectors (Bigann run with benchs/bench_polysemous_1bn.py), which compare against figures copied from two CVPR'16 papers on other hardware and state no compiler, flags or CPU model, so C; the peer-reviewed GPU paper (arXiv 1702.08734) reports the 8.5x win over Wieschollek et al. but could only be read as a search snippet here.
- **Verifier notes:** Deep1B (3.66 vs 20 ms, 5.5x) and Bigann (0.035 / 0.0340 vs 0.15 ms, 4.3x / 4.4x) numbers verified in the archived tables of the 1G wiki page; nmslib caveat verified on the 1M page. Shortcomings: cross-hardware comparison against figures copied from 2016 papers, archived results, no compiler/flags/CPU model for the compared rows, nmslib faster on SIFT1M; candidate for a paper-access retier to B via the GPU paper (8.5x over Wieschollek et al., snippet only). Metadata (MIT, 41.1k stars, not archived) confirmed; last commit date not checkable (HTTP 429 twice).
- **Fields the verifier corrected:** `hardware`, `caveats`
- **Shortcomings recorded by:** wiki tables (verifier); enricher harness reading
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/wiki/facebookresearch/faiss/Indexing-1G-vectors.md>
  - <https://raw.githubusercontent.com/wiki/facebookresearch/faiss/Indexing-1M-vectors.md>
  - <https://github.com/facebookresearch/faiss>
  - <https://raw.githubusercontent.com/facebookresearch/faiss/main/CHANGELOG.md>
  - <https://raw.githubusercontent.com/facebookresearch/faiss/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/facebookresearch/faiss>
  - <https://raw.githubusercontent.com/facebookresearch/faiss/main/README.md>
  - <https://raw.githubusercontent.com/facebookresearch/faiss/main/INSTALL.md>
  - <https://raw.githubusercontent.com/facebookresearch/faiss/main/CHANGELOG.md>
  - <https://raw.githubusercontent.com/facebookresearch/faiss/main/CMakeLists.txt>
  - <https://raw.githubusercontent.com/facebookresearch/faiss/main/faiss/CMakeLists.txt>
  - <https://raw.githubusercontent.com/facebookresearch/faiss/main/benchs/bench_polysemous_1bn.py>
  - <https://raw.githubusercontent.com/facebookresearch/faiss/main/faiss/AutoTune.cpp>
  - <https://raw.githubusercontent.com/wiki/facebookresearch/faiss/Indexing-1G-vectors.md>
  - <https://raw.githubusercontent.com/wiki/facebookresearch/faiss/Indexing-1M-vectors.md>
  - <https://raw.githubusercontent.com/wiki/facebookresearch/faiss/Threads-and-asynchronous-calls.md>
  - <https://github.com/facebookresearch/faiss/issues?q=is%3Aissue+is%3Aopen+label%3Abug>
  - <https://github.com/facebookresearch/faiss/issues?q=is%3Aissue+slower+in%3Atitle>
  - <https://github.com/facebookresearch/faiss/issues/4582>
  - <https://github.com/facebookresearch/faiss/issues/5700>
  - WebSearch: "Billion-scale similarity search with GPUs" pdf site:github.com (abstract snippet only; arXiv blocked)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/facebookresearch/faiss`) · [data/wave8/enrich/raw/github_com_facebookresearch_faiss.json](../../../data/wave8/enrich/raw/github_com_facebookresearch_faiss.json) (enrichment confidence 0.8)

</details>
