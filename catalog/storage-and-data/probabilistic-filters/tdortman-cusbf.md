# cuSBF (GPU Minimizer-Aware Super Bloom Filter)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Probabilistic filters](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `CUDA/C++ (header-only)` · `BSL-1.0` · 🟢 active

> Header-only CUDA Super Bloom filter for DNA k-mers; 7.6-9.1x faster than cuCollections' GPU blocked Bloom on RTX PRO 6000.

| | |
|---|---|
| **Beats** | Bloom filter (NVIDIA cuCollections GPU Blocked Bloom Filter, GBBF) |
| **Claimed result** | Per the README tables (Config&lt;31,28,16,4&gt;, RTX PRO 6000 Blackwell): vs GPU Blocked Bloom Filter (cuCollections GBBF), 9.1x faster insert and 7.7x faster query on the \~100M k-mer C. elegans filter, and 8.2x insert and 7.6x query on the \~3.1B k-mer CHM13 filter. Other baselines: CPU Super Bloom 59-234x (92x/234x small, 59x/165x large); Cuckoo-GPU 7.8-3427x (80x/8.0x small, 3427x/7.8x large); Bulk TCF 12-67x; GQF 11-69x (69x/13x small, 42x/11x large). |
| **Workload** | Batch k-mer insertion and query throughput on genomic sequence data, Config&lt;31,28,16,4&gt;, on a smaller filter (C. elegans, \~100M k-mers) and a large filter (CHM13, \~3.1B k-mers) |
| **Metric** | throughput |
| **Hardware** | GPU runs: NVIDIA RTX PRO 6000 Blackwell (96 GB GDDR7) on an AMD EPYC 7713P (64-core) host, AlmaLinux 10.1 (paper System A); the paper also reports GH200 (System B). CPU Super Bloom baseline: Intel Xeon W9-3595X (60 cores, 120 threads, 256 GB DDR5). |
| **Compiler and flags** | CUDA 13.2 (nvcc, per the paper's experimental setup); meson.build default_options optimization=3 (-O3), cpp_std=c++20, warning_level=2; nvcc args -std=c++20 --expt-extended-lambda --expt-relaxed-constexpr --generate-line-info -gencode sm_80/sm_90/sm_120. GCC/Clang host compiler, version not stated. Meson/Ninja build, Google Benchmark. |
| **Adoption** | 7 stars; brand-new companion code for a 2026 arXiv paper |
| **Last commit** | 2026-09-26 |
| **Links** | [repository](https://github.com/tdortman/cuSBF) · [benchmark](https://github.com/tdortman/cuSBF#performance) |

## Verdict

On an RTX PRO 6000 Blackwell (96 GB GDDR7, AMD EPYC 7713P host, CUDA 13.2, -O3), Google Benchmark runs of Config&lt;31,28,16,4&gt; at 16 bits per k-mer (256 MiB filter for C. elegans, 8 GiB for CHM13), with device-resident input and transfers untimed, showed cuSBF inserting 9.1x/8.2x and querying 7.7x/7.6x faster than cuco::bloom_filter&lt;uint64_t&gt; on its default policy, which was fed pre-packed 64-bit k-mers. The same unreviewed, first-party preprint reports only 1.37-2.36x on GH200.

## Use it when

- GPU-resident genomic pipelines that need k-mer presence tests over whole reads or genomes (contamination or host-read screening, read-classification pre-filters) with the sequence bytes already in device memory
- DNA with k &lt;= 32, ideally the paper's Pareto point k=31, s=28, m=16, H=4, and filters from hundreds of MiB to several GiB (benchmarked at 256 MiB and 8 GiB, 16 bits per inserted k-mer)
- Append-only workloads that bulk-insert and then bulk-query, where throughput matters more than single-key latency
- Discrete Ampere-or-newer NVIDIA GPUs with many SMs (the largest lead was on an RTX PRO 6000 Blackwell), or cache-coherent CPU-GPU systems such as GH200 when the input starts in host memory
- When you want a lower false-positive rate than cuco's blocked Bloom at the same memory: README shows 0.848% vs 3.069% at 21.4 bits per k-mer

## Skip it when

- General keys (integers, strings, URLs): the API only indexes k-mers cut from sequences, with no per-key insert or contains
- You need deletions, counting, merging two filters, or saving and loading a filter: none exist (the only reset is clear())
- Host-resident input on a PCIe GPU: the paper measured an 87-94% throughput loss on the RTX PRO 6000 (6.3/7.1 GKmer/s host input vs 48.5/112 GKmer/s device-resident). On GH200 (HBM3), the lead over cuco shrinks to 1.37-2.36x, and cuSBF itself ran slower there than on the RTX PRO 6000
- Tight false-positive budgets: at 2^31 bits Cuckoo-GPU has about 24x fewer false positives and the CPU Super Bloom about 30x fewer. A k-mer one base away from an indexed k-mer falls back to the single-s-mer false-positive rate
- Non-Linux hosts, pre-Ampere GPUs, CUDA older than 13.1, or projects that need a mature dependency: v0.4.0, no git tags or releases, one main author, 7 stars

## How it is fast

It implements the Super Bloom filter: a minimizer hash picks one 256-bit shard per k-mer, so a super-k-mer (about 8.5 consecutive k-mers at k=31, m=16) hits the same shard, and the Findere scheme sets H bits for each of the k-s+1 overlapping s-mers. Each thread block loads a coalesced shared-memory tile of T+k-1 symbols; inserts OR together the masks of adjacent same-shard lanes with CUB HeadSegmentedReduce so only the run head issues four 64-bit atomicOr calls, and queries use __match_any_sync so one lane loads the shard (256-bit ld.global.nc on Blackwell) and shuffles it to its peers. Shards are split into four 64-bit sectors (hash i sets a bit in word i mod 4) using bit-slices of one 64-bit hash, with compile-time-unrolled loops. The paper's speed-of-light profile shows cuSBF compute-bound at about 85% SM throughput on insert, while cuco's blocked Bloom drops below 10% SM throughput once the filter outgrows L2.

## Compared with alternatives

Pick it over Cuckoo-GPU (same author) for insert-heavy, duplicate-heavy genomic k-mer streams where deletions don't matter (80x to 3427x faster inserts, about 8x faster queries on the RTX PRO 6000), and pick Cuckoo-GPU for deletions, arbitrary 64-bit keys, or lower FPR at mid-size budgets. The CPU filters (CQF, Xor, BuRR, Prefix) are the better fit unless you are on an NVIDIA GPU with sequence data.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | CUDA Toolkit 13.1+ (Thrust, CUB, libcu++ cuda::std::expected) and zlib (for gzip FASTX input; pulled in as a Meson subproject). Benchmarks and tests also pull cuCollections, Google Benchmark, GoogleTest, CLI11, saltsystemslab gpu-filters, Cuckoo-GPU and a vendored Rust CPU Super Bloom. |
| **Minimum toolchain** | CUDA 13.1+ nvcc (-std=c++20 --expt-extended-lambda --expt-relaxed-constexpr); GCC or Clang host compiler with C++20 including std::format, which the headers call; Meson &gt;= 1.3 plus Ninja for the bundled build |
| **Platforms** | Linux x86-64 or aarch64 with an NVIDIA GPU of compute capability 8.0+ (Ampere, Ada, Hopper, Blackwell; default gencode sm_80/sm_90/sm_120). WSL2 is described as a reasonable dev setup. Native Windows and macOS are not supported. |
| **Thread safety** | Not documented. Host APIs, including const queries, reuse a mutable per-filter staging buffer, so serialize host calls on one filter object. Device inserts use atomicOr. Host bulk APIs synchronize the stream; the \*_async device-span APIs leave ordering to the caller. |
| **Drop-in for the baseline** | partial — it replaces cuco::bloom_filter only when the keys are k-mers of sequences. It takes sequences, not uint64 keys, and has a different API (insert_sequence/contains_sequence, FASTX readers, Result&lt;T&gt;). It does not use cuco's filter format. |

## Gotchas

- Capacity is rounded up to a power-of-two number of 256-bit shards, so a 5 GiB request allocates 8 GiB. You size the filter in bits yourself (the paper used 16 bits per inserted k-mer); there is no sizing helper based on item count or target FPR.
- The headers have no canonical or reverse-complement k-mer handling, so the filter is strand-specific. Canonicalize yourself or insert both strands. Any non-ACGT byte (N, IUPAC codes) invalidates every k-mer spanning it, and those windows query as 0. A/C/G/T are case-insensitive.
- Config limits: HashCount must be 4, 8, 12 or 16; k times bits-per-symbol must be &lt;= 64 (k &lt;= 32 for DNA, 12 for 5-bit protein); s and m must be &lt;= k. Each Config is a separate type and kernel instantiation. The paper notes that larger alphabets force short minimizers and raise the FPR.
- The constructor throws std::runtime_error through CUSBF_UNWRAP(clear()) if clear() fails, and the thrust allocation can throw; other calls return Result. The CUSBF_TRY/CUSBF_UNWRAP macros use GNU statement expressions. Per-k-mer queries produce one output byte per k-mer, about 3 GB of device memory for a 3.1B k-mer genome.

## Known shortcomings

- GPU-only (CUDA 13.2); the headline ranges are vs other GPU filters (Cuckoo-GPU 7.8-3427x, GQF 11-69x) and vary widely by workload.
- The 9.1x lead holds only with input already on the GPU; with host input over PCIe 87-94% of throughput is lost (paper). On GH200 (HBM3) the lead over cuCollections is only 1.37-2.36x. Worse FPR than Cuckoo-GPU (\~24x) and the CPU Super Bloom (\~30x) at 2^31 bits; size rounds up to power-of-two shards (5 GiB becomes 8 GiB).
- Sequence-only API (k-mers of DNA sequences, no arbitrary keys), forward strand only (no canonical/reverse complement), any non-ACGT byte drops spanning k-mers; no delete/merge/save. Immature: v0.4.0, no tags, 7 stars; Linux, sm_80+, CUDA 13.1+ only.

## Caveats and trade-offs

Very new project (7 stars). The paper (arXiv:2606.24417, June 2026) is a preprint and not yet peer-reviewed. All benchmark numbers are first-party and not independently reproduced, though the benchmark code, build flags, CUDA version and hardware are all public. One comparison baseline, Cuckoo-GPU (tdortman/Cuckoo-GPU), is by the same author and already in the known list, so this entry's primary claim is the result against the cuCollections GBBF Bloom filter. The 3427x Cuckoo-GPU insert figure is a large-filter outlier; most other ratios are in the single or double digits.

GPU-only, requires NVIDIA compute capability 8.0+ and CUDA 13.1+; Linux-only build (uses mmap and GNU statement expressions); specialized for genomic minimizer/k-mer workloads rather than a general-purpose drop-in filter; needs the findere scheme tuned to match GBBF's false-positive rate at low bits/k-mer

## Maintenance

Active single-author research code (last commit 2026-09-26; versions 0.2.0 to 0.4.0 bumped in meson.build during Aug 2026 but never tagged), with 7 stars and no issues or PRs; BSL-1.0 and header-only, so it is easy to vendor at a pinned commit.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** Benchmark code is public (benchmarks/filter_comparison.cu, which includes cuco/bloom_filter.cuh and runs GBBF side by side under Google Benchmark). Flags are in meson.build (optimization=3, C++20, nvcc --expt-extended-lambda/--expt-relaxed-constexpr with sm_80/90/120 gencode). The arXiv paper's setup names CUDA 13.2 and the full hardware: RTX PRO 6000 Blackwell on an AMD EPYC 7713P host, plus a Xeon W9-3595X for the CPU baseline.
- **Verifier notes:** The README numbers match the record except two ranges: Cuckoo-GPU spans 7.8-3427x (not 8.0-3427x) and GQF spans 11-69x (not 13-69x). The CPU Super Bloom runs used an Intel Xeon, but the host CPU for the GPU runs was an AMD EPYC 7713P. I kept tier A because the code, flags, compiler (CUDA 13.2) and hardware are all public or stated.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/tdortman/cuSBF>
  - <https://github.com/tdortman/cuSBF#performance>
  - <https://github.com/tdortman/cuSBF/blob/main/meson.build>
  - <https://github.com/tdortman/cuSBF/blob/main/benchmarks/filter_comparison.cu>
  - <https://arxiv.org/abs/2606.24417>
  - <https://arxiv.org/pdf/2606.24417>
- **Sources the enricher read:**
  - <https://github.com/tdortman/cuSBF>
  - <https://github.com/tdortman/cuSBF#performance>
  - <https://github.com/tdortman/cuSBF/blob/main/include/cusbf/filter.cuh>
  - <https://github.com/tdortman/cuSBF/blob/main/include/cusbf/config.cuh>
  - <https://github.com/tdortman/cuSBF/blob/main/include/cusbf/filter_ref.cuh>
  - <https://github.com/tdortman/cuSBF/blob/main/include/cusbf/detail/kernels.cuh>
  - <https://github.com/tdortman/cuSBF/blob/main/include/cusbf/detail/filter_impl.cuh>
  - <https://github.com/tdortman/cuSBF/blob/main/include/cusbf/detail/filter_common.cuh>
  - <https://github.com/tdortman/cuSBF/blob/main/include/cusbf/detail/sequence_kmer.cuh>
  - <https://github.com/tdortman/cuSBF/blob/main/include/cusbf/Alphabet.cuh>
  - <https://github.com/tdortman/cuSBF/blob/main/include/cusbf/hashutil.cuh>
  - <https://github.com/tdortman/cuSBF/blob/main/include/cusbf/error.hpp>
  - <https://github.com/tdortman/cuSBF/blob/main/include/cusbf/cuda_error.hpp>
  - <https://github.com/tdortman/cuSBF/blob/main/include/cusbf/gzstreambuf.hpp>
  - <https://github.com/tdortman/cuSBF/blob/main/include/cusbf/superbloom_ffi.hpp>
  - <https://github.com/tdortman/cuSBF/blob/main/include/cusbf/detail/fastx_chunk.cuh>
  - <https://github.com/tdortman/cuSBF/blob/main/include/cusbf/detail/fastx_file_buffer.hpp>
  - <https://github.com/tdortman/cuSBF/blob/main/meson.build>
  - <https://github.com/tdortman/cuSBF/blob/main/meson.options>
  - <https://github.com/tdortman/cuSBF/blob/main/subprojects/cuco.wrap>
  - <https://github.com/tdortman/cuSBF/blob/main/.cargo/config.toml>
  - <https://github.com/tdortman/cuSBF/blob/main/benchmarks/filter_comparison.cu>
  - <https://github.com/tdortman/cuSBF/issues>
  - <https://github.com/tdortman/cuSBF/pulls>
  - <https://github.com/tdortman/cuSBF/commits/main>
  - <https://github.com/tdortman/cuSBF/tags>
  - <https://tdortman.github.io/cuSBF/>
  - <https://arxiv.org/abs/2606.24417>
  - <https://arxiv.org/pdf/2606.24417>
  - <https://hn.algolia.com/api/v1/search?query=cuSBF&restrictSearchableAttributes=url,title>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/tdortman/cusbf`) · [data/wave6/enrich/raw/github_com_tdortman_cusbf.json](../../../data/wave6/enrich/raw/github_com_tdortman_cusbf.json) (enrichment confidence 0.8)

</details>
