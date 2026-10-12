# USearch

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Header-only C++11 HNSW vector-search engine with native bindings; first-party tables claim 2-10x faster index builds than FAISS.

| | |
|---|---|
| **Beats** | FAISS (HNSW index build; exact brute-force search via faiss.IndexFlatL2) |
| **Claimed result** | README: '10x faster HNSW implementation than FAISS'. Indexing time, 100 Million 96d f32/f16/i8 vectors: FAISS 2.6/2.6/2.6 h vs USearch 0.3/0.2/0.2 h (9.6/10.4/10.7x). 100 Million 1536d f32/f16/i8: FAISS 5.0/4.1/3.8 h vs USearch 2.1/1.1/0.8 h (2.3/3.6/4.4x). Exact search vs FAISS IndexFlatL2: 55.3 ms vs 2.54 ms ('up to a 20x performance improvement'). |
| **Workload** | HNSW index construction time for 100 million vectors (96-dimensional and 1536-dimensional; f32, f16 and i8 storage) with inner-product distance on Intel Sapphire Rapids at equal recall and memory; plus an exact brute-force k-NN search example against faiss.IndexFlatL2 in Google Colab. |
| **Metric** | build-time |
| **Hardware** | Intel Sapphire Rapids (exact CPU model, core count and RAM not stated in the README); the exact-search example ran on a Google Colab CPU instance (not further specified) |
| **Adoption** | 4.3k stars; integrated by ClickHouse, DuckDB, YugabyteDB and others (per README) |
| **Last commit** | 2026-10-05 |
| **Links** | [repository](https://github.com/unum-cloud/usearch) · [benchmark](https://github.com/unum-cloud/usearch) |

## Verdict

The README reports, first-party, that building HNSW indexes over 100M vectors on an unspecified Intel Sapphire Rapids machine took 0.2-0.3 h vs 2.6 h for FAISS at 96d and 0.8-2.1 h vs 3.8-5.0 h at 1536d, with no compiler, flags, threads or FAISS build level. The author's reproducible RetriEval suite (dual-socket Xeon 6, 192 threads, USearch main-dev vs FAISS 1.12.0 built at the generic SIMD level) shows 1.14x faster builds on Turing-ANNS 10M f32 and 1.34x on SIFT 10M u8 at equal M and ef, with search ranging from 2.1x faster (SIFT) to 1.34x slower (Turing f32).

## Use it when

- Embedding a small, dependency-light ANN index in a C++ or multi-language product (databases, services, mobile, WebAssembly), as ClickHouse, DuckDB and TiDB/TiFlash do per the README's integration list.
- Building HNSW graphs over 10M to 100M vectors with bf16, f16 or fp8 storage: the author's RetriEval tables show 2.8-4.3x higher add throughput than FAISS HNSW with SQbf16/SQfp16 on Turing-ANNS 10M (but see the FAISS build flaw in gotchas).
- Binary fingerprints with Tanimoto, Sorensen or Hamming distance (chemistry, genomics) at 100M scale, where FAISS IndexBinaryHNSW did not finish within 9 hours in RetriEval while USearch built PubChem MACCS 100M in 54.6 min.
- Serving indexes larger than RAM from a memory-mapped file (Index.restore(path, view=True)), or custom metrics compiled with Numba or another JIT.

## Skip it when

- Compressed billion-scale or GPU search that needs IVF, PQ or CAGRA: USearch offers only HNSW and exact scans on CPU.
- Plain f32 or binary workloads at FAISS-tuned settings: in RetriEval FAISS searched Turing-ANNS 10M f32 faster (16,486 vs 12,331 queries/s) and PubChem MACCS 10M binary much faster (293,795 vs 35,767 queries/s, 95,230 vs 36,347 adds/s, different M and ef), so the 10x headline is not a general result.
- Write-heavy concurrent ingestion that must stay fully searchable: open bug #735 (2026-03-24, labelled v3) reports concurrent add() leaving nodes stored but unreachable by search(), and open issues #396 and #354 report deadlocks in concurrent update() and Swift add().
- Workloads that delete heavily: remove() frees the key slot for reuse but graph links to removed entries stay until you call isolate() or compact(), and memory-mapped views are immutable (add and remove fail on a viewed file).
- Expecting a plain C++ include to be fast: the CMake defaults USEARCH_USE_NUMKONG and USEARCH_USE_OPENMP are OFF, so the header alone falls back to the generic metrics; the Python wheel and Rust crate enable NumKong by default.

## How it is fast

It implements HNSW (Malkov and Yashunin) with a flat tape allocator for nodes, 32- or 40-bit neighbour ids, and cache-line-padded striped spin locks (striped_locks_gt) so many caller threads can insert concurrently without spawning threads of its own. Distances come from NumKong (formerly SimSIMD) kernels with runtime dispatch to AVX2, AVX-512 or Arm SVE/NEON, which also cover f16, bf16, fp8 and i8 storage, so downcast vectors cut memory traffic during graph construction and search. The Rust and Python builds compile the core with -O3 -ffast-math.

## Compared with alternatives

Against FAISS, the only vector-search sibling, pick USearch for an embeddable header-only HNSW index with custom or binary metrics, half-precision or fp8 storage and many language bindings; pick FAISS for IVF/PQ compression, GPU search, or f32 HNSW search throughput, where the author's own suite does not show USearch ahead.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none for the core headers; optional NumKong (SIMD metrics), OpenMP and jemalloc via CMake options; the Python package (2.26.4) requires numpy, tqdm and numkong |
| **Minimum toolchain** | C++11 for the headers (C++17 and C++20 features used when available); CMake 3.11+; the Rust crate builds with C++17 and -O3 -ffast-math; Python 3.10+ |
| **Platforms** | Linux, macOS, Windows, iOS, Android and WebAssembly per the README; x86-64 and aarch64 with runtime-dispatched SIMD through NumKong |
| **Thread safety** | index_gt documents concurrent construction, search and updates as thread-safe and reuses the caller's threads; reserve() must run with no concurrent insertions, neighbour views must not outlive concurrent add/update/remove, and open issues #735, #396 and #354 report lost reachability and deadlocks under concurrent mutation |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw in the newer comparison the verifier relied on: RetriEval builds FAISS with `cargo install --features faiss-static`, which goes through faiss-sys's build.rs. That script sets only CMAKE_BUILD_TYPE Release, C API, shared-libs off and GPU off, never FAISS_OPT_LEVEL, so FAISS 1.12.0's default 'generic' target is built and linked (faiss/CMakeLists.txt leaves faiss_avx2, faiss_avx512 and faiss_avx512_spr out of the build unless that level is chosen). The FAISS baseline therefore ran without -mavx2/-mfma/-mf16c or AVX-512 on a Xeon 6, while USearch used NumKong with runtime dispatch. No CXXFLAGS are documented. This plausibly explains why FAISS's SQfp16 and SQbf16 builds are 2-3x slower than its own f32 build (2,545 and 3,800 vs 7,491 adds/s), so the 2.8-4.3x half-precision leads are against a crippled baseline.
- The README headline (9.6-10.7x on 100M 96d vectors) comes from a 2023 vendor blog that is egress-blocked here, with no CPU model, thread count, compiler, flags or FAISS build level stated. BENCHMARKS.md lists different HNSW defaults (FAISS M=32, efConstruction 40, ef 16; USearch M=16, 128, 64), and 'equivalent recall' is asserted, not shown.
- The 20x exact-search figure (FAISS IndexFlatL2 55.3 ms vs 2.54 ms) is a single Colab comment on issue #176, whose opening report had USearch at 94.7 ms vs FAISS 1.14 ms (500 x 1024d, k=50). The in-tree python/scripts/bench_exact.py times one unwarmed call per backend with 10 queries by default, so it is not a stable reproduction harness either.
- README claims of '3 K SLOC' and a 'single header' are stale: index.hpp alone is 5,066 lines and the dense API adds index_dense.hpp (2,457) and index_plugins.hpp (4,329). The 'no required dependencies' row holds only for the C++ headers: the Python package requires numkong, and open issue #767 reports the 2.25.x NuGet libusearch_c.so depending on libnumkong.so.

## Known shortcomings

- README table only (blog blocked): no CPU model or flags and FAISS default HNSW parameters differ; the author's newer RetriEval suite (Xeon 6, v2.25 vs FAISS 1.12.0) shows f32 builds only 1.14-1.34x faster at equal settings, FAISS faster at f32 search on Turing-ANNS (1.34x) and much faster on 10M MACCS binary, with FAISS killed at 9 h at 100M.
- Harness flaw: the RetriEval comparison builds FAISS through faiss-sys build.rs with no FAISS_OPT_LEVEL, so FAISS 1.12.0 ran its generic target (no AVX2/F16C/AVX-512) on a Xeon 6 while USearch got NumKong runtime dispatch; FAISS SQfp16/SQbf16 adds 2,545/3,800 vs its own f32 7,491/s, so the 2.8-4.3x half-precision leads are against a crippled baseline. Open bug #735: concurrent add() leaves nodes unreachable; deadlocks #396, #354. README '3K SLOC, single header' is stale (index.hpp 5,066 lines).

## Caveats and trade-offs

First-party README numbers only: the linked benchmark blog (unum.cloud, 2023-11-07) was EGRESS_BLOCKED, so the setup behind the indexing-time table could not be checked, and the README gives no exact CPU model, thread count, compiler or flags (hence tier C). The 10x headline holds only for 96d vectors; 1536d gains are 2.3-4.4x. Default HNSW hyper-parameters differ between the libraries (BENCHMARKS.md: FAISS M=32, efConstruction 40, ef 16; USearch M=16, 128, 64), and the README asserts but does not show 'equivalent recall'. The author's newer reproducible suite (ashvardanian/RetriEval, which BENCHMARKS.md now points to; USearch v2.25 vs FAISS v1.12.0 static via faiss-sys 0.7.0, dual-socket Intel Xeon 6 with 192 threads, compiler and flags not stated) does not reproduce 10x at equal settings: SIFT 10M u8 (M=16, ef 128/256, recall@10 0.9938 vs 0.9952) gives 35,405 vs 26,374 adds/s (1.34x) and 80,729 vs 38,278 searches/s (2.11x); Turing-ANNS 10M f32 (M=48) gives 8,532 vs 7,491 adds/s (1.14x) while FAISS searches faster, 16,486 vs 12,331/s (1.34x in FAISS's favour); with bf16/f16 storage USearch leads 2.76-4.31x on adds and 1.63-2.02x on search; on PubChem MACCS binary 10M FAISS (M=64, ef 40/16, a different config) is faster, 95,230 vs 36,347 adds/s and 293,795 vs 35,767 searches/s at similar recall, but FAISS was killed at 9 h at 100M on MACCS and SIFT while USearch finished in 54.6 and 48.7 min (all ratios derived from page data). The 55.3 ms vs 2.54 ms exact-search figures come from comment 1666650778 on issue #176 that the README links; the comment did not render here, and the issue's own original report (500 vectors x 1024d, k=50, Colab) measured USearch at 94.7 ms vs FAISS IndexFlatL2 at 1.14 ms (issue labelled bug, invalid, released), so the exact-search result is workload- and version-dependent. In-tree BENCHMARKS.md has USearch-only QPS tables (Graviton 3, c7g.metal) with no FAISS rows; python/scripts/bench_exact.py can run '--backend usearch,faiss' for reproduction. Category kept as autodiff-and-ml-kernels (FAISS sits there in the catalog); it is a vector-search/ANN library, off the category's listed baselines. [retier] RetriEval numbers compare USearch with NumKong runtime dispatch against FAISS built at the generic target (faiss-sys build.rs, no FAISS_OPT_LEVEL): FAISS SQfp16/SQbf16 adds 2,545/3,800 per s vs its own f32 7,491 per s, so the 2.8-4.3x half-precision leads are against a crippled baseline. First-party README table setup unverifiable (unum.cloud blocked). Open #735 concurrent add() leaves nodes unreachable; deadlocks #396, #354.

Single-header C++11 core with bindings for 10 languages, user-defined metrics with JIT, f16/bf16/i8 quantization, disk-viewed indexes and 40-bit IDs. Different defaults from FAISS (connectivity 16 vs 32, expansion at add 128 vs 40, expansion at search 64 vs 16, per BENCHMARKS.md), so recall/speed trade-offs are not identical to FAISS defaults.

## Maintenance

Actively maintained (commits through 2026-10-05, PyPI 2.26.4 released 2026-10-05) and Apache-2.0; the core is small enough to vendor as headers, but check the open concurrency bugs before relying on multi-threaded inserts.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now D.
- **Tier reason:** First-party README table against FAISS on unspecified Intel Sapphire Rapids hardware with no compiler, flags, thread count or published harness for the headline indexing table (the linked unum.cloud blog is EGRESS_BLOCKED); the newer first-party RetriEval suite has public code but states only 'dual socket Intel Xeon6' and no compiler or flags, so it is not A either.
- **Retiered** C to D: The only concrete comparison reachable (RetriEval, FAISS 1.12.0 on Xeon 6) builds FAISS via faiss-sys with no FAISS_OPT_LEVEL, so the baseline ran a generic target without AVX2/F16C/AVX-512 while USearch used runtime dispatch (crippled-baseline precedent); the first-party README table's setup is unverifiable (blog blocked). Directional only.
- **Verifier notes:** README numbers are quoted correctly (indexing table and 55.3 vs 2.54 ms). Main shortcomings: unverifiable first-party headline (blog blocked, no CPU model or flags), unequal default HNSW parameters, and the author's own newer RetriEval suite shows only 1.1-1.3x faster f32 builds at equal settings, FAISS faster f32 search on Turing-ANNS and much faster on binary MACCS at 10M.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** first-party README (verifier); enricher (wave 8)
- **Pages the verifier opened:**
  - <https://github.com/unum-cloud/usearch>
  - <https://raw.githubusercontent.com/unum-cloud/usearch/HEAD/README.md>
  - <https://raw.githubusercontent.com/unum-cloud/usearch/HEAD/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/unum-cloud/usearch/HEAD/python/scripts/bench_exact.py>
  - <https://github.com/unum-cloud/usearch/issues/176>
  - <https://github.com/unum-cloud/usearch/commits/main>
  - <https://github.com/ashvardanian/RetriEval>
  - <https://raw.githubusercontent.com/ashvardanian/RetriEval/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/unum-cloud/usearch>
  - <https://raw.githubusercontent.com/unum-cloud/usearch/main/README.md>
  - <https://raw.githubusercontent.com/unum-cloud/usearch/main/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/unum-cloud/usearch/main/python/scripts/bench_exact.py>
  - <https://raw.githubusercontent.com/unum-cloud/usearch/main/CMakeLists.txt>
  - <https://raw.githubusercontent.com/unum-cloud/usearch/main/Cargo.toml>
  - <https://raw.githubusercontent.com/unum-cloud/usearch/main/build.rs>
  - <https://raw.githubusercontent.com/unum-cloud/usearch/main/include/usearch/index.hpp>
  - <https://raw.githubusercontent.com/unum-cloud/usearch/main/include/usearch/index_dense.hpp>
  - <https://raw.githubusercontent.com/unum-cloud/usearch/main/include/usearch/index_plugins.hpp>
  - <https://github.com/unum-cloud/usearch/issues/176>
  - <https://github.com/unum-cloud/usearch/issues?q=is%3Aissue+is%3Aopen+label%3Abug>
  - <https://github.com/unum-cloud/usearch/issues/735>
  - <https://github.com/unum-cloud/usearch/issues/439>
  - <https://pypi.org/pypi/usearch/json>
  - <https://raw.githubusercontent.com/ashvardanian/RetriEval/HEAD/README.md>
  - <https://raw.githubusercontent.com/ashvardanian/RetriEval/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/ashvardanian/RetriEval/HEAD/src/faiss.rs>
  - <https://raw.githubusercontent.com/Enet4/faiss-rs/master/faiss-sys/build.rs>
  - <https://raw.githubusercontent.com/facebookresearch/faiss/v1.12.0/CMakeLists.txt>
  - <https://raw.githubusercontent.com/facebookresearch/faiss/v1.12.0/faiss/CMakeLists.txt>
  - <https://raw.githubusercontent.com/facebookresearch/faiss/main/CMakeLists.txt>
  - <https://raw.githubusercontent.com/facebookresearch/faiss/main/faiss/CMakeLists.txt>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/unum-cloud/usearch`) · [data/wave8/enrich/raw/github_com_unum_cloud_usearch.json](../../../data/wave8/enrich/raw/github_com_unum_cloud_usearch.json) (enrichment confidence 0.75)

</details>
