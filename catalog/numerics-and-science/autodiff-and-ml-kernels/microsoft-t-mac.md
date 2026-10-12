# T-MAC

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `MIT` · 🟡 stale

> Lookup-table CPU kernels for 1-4-bit LLM weights; 2-6x faster token generation than llama.cpp Q2_K/Q4_0 at low thread counts.

| | |
|---|---|
| **Beats** | llama.cpp low-bit dequantization kernels (Q2_K, Q4_0) |
| **Claimed result** | '4\~5x speedup compared to SOTA CPU low-bit framework (llama.cpp)' on Surface Laptop 7 (20 tok/s 1 core, 48 tok/s 4 cores for 3B BitNet); matches 40 tok/s with 2 cores vs 8 for llama.cpp |
| **Workload** | Low-bit LLM token generation and prefill on CPU using lookup tables instead of dequantize-multiply (BitNet-3B, Llama-2-7B W2/W4). |
| **Metric** | throughput |
| **Hardware** | Surface Laptop 7, Apple M2-Ultra, Jetson AGX Orin, Raspberry Pi 5, Surface Book 3 |
| **Compiler and flags** | Clang 17.0.6 is the documented build toolchain (Windows install notes); llama.cpp built with -DCMAKE_BUILD_TYPE=Release -DLLAMA_TMAC=ON; exact flags for the published runs not stated |
| **Adoption** | \~990 stars; EuroSys 2025 paper |
| **Last commit** | 2025-06-03 |
| **Links** | [repository](https://github.com/microsoft/T-MAC) · [benchmark](https://github.com/microsoft/T-MAC) |

## Verdict

Authors measured end-to-end token generation with T-MAC 2-bit vs llama.cpp Q2_K and T-MAC 4-bit vs llama.cpp Q4_0 (llama.cpp b2794) on Surface Laptop 7, M2-Ultra, AGX Orin, Raspberry Pi 5 and Surface Book 3; BitNet-3B on Surface Laptop 7 reached 20 tok/s on 1 core and 48 on 4 (README '4\~5x'), while the EuroSys'25 paper states 'up to 4x' throughput and 70% less energy. Per-run compiler flags are not given.

## Use it when

- Token generation (batch 1 GEMV) for 1-2-bit models such as BitNet b1.58 or W2 GPTQ/EfficientQAT models on ARM CPUs (Apple M-series, Snapdragon X, Jetson Orin, Raspberry Pi 5)
- Edge deployments where you want the same tokens/s with fewer cores or less energy (README: 40 tok/s with 2 cores vs 8 for llama.cpp on Surface Laptop 7)
- Low-thread-count inference: the gap is largest single-threaded (e.g. Raspberry Pi 5 BitNet-3B 8.03 vs 1.37 tok/s)
- Prefill of W2 models on CPU without AMX (Surface Laptop 7 Llama-2-7B W2, 8 threads: 94.4 vs 21.3 tok/s llama.cpp, 37.7 with OpenBLAS)

## Skip it when

- 4-bit models at full thread count: the authors' own data shows only 1.09x (AGX Orin, 12 threads) and 1.13x (M2-Ultra, 8 threads) over llama.cpp Q4_0
- Old-generation x86: the README warns it cannot guarantee meaningful speedup there, especially for 4-bit token generation
- You need current upstream llama.cpp: integration is via a fork rebased to a 2024 llama.cpp; some models are unsupported by its convert script
- Multi-batch GEMM on Apple M2-Ultra, where AMX-backed BLAS is comparable or faster
- Simple builds: requires Python 3.8, building TVM from source (downloads clang+LLVM) and a per-model kernel compile step

## How it is fast

Instead of dequantizing weights and doing multiply-add, it groups weight bits (e.g. 4 one-bit weights), precomputes all partial sums of the activations into a lookup table, and replaces MACs with table lookups (ARM tbl / x86 pshufb) plus shift-and-accumulate across bit planes. The table is halved (2^n to 2^(n-1)) using a sign bit. Cost scales linearly with weight bit-width, so 2-bit and 1.58-bit models gain far more than 4-bit ones.

## Compared with alternatives

Pick T-MAC over llamafile tinyBLAS when weights are 1-3 bit (tinyBLAS targets F16/Q8_0 prompt eval); pick MNN for general mobile model inference rather than low-bit LLM GEMV.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | TVM (built from source), Python 3.8 + virtualenv/conda, CMake &gt;= 3.22, clang/LLVM (17.0.6 on Windows), patched llama.cpp submodule |
| **Minimum toolchain** | C++17 (CMakeLists), CMake 3.22, Clang 17.0.6 on Windows |
| **Platforms** | aarch64 (macOS, Linux, Windows on ARM, Android cross-compile), x86-64 (Linux, Windows); T-MAN variant targets Qualcomm NPU |
| **Thread safety** | not documented (threading is through llama.cpp's -t threads) |
| **Drop-in for the baseline** | partial — runs inside its llama.cpp fork with the same CLI (main/llama-bench), but models must be re-converted to a T-MAC GGUF with tuned kernel configs |

## Gotchas

- Kernels are tuned per model shape and quantization config (kcfg.ini); a new model means re-running the compile step (prebuilt ARM kernels via -u)
- Published end-to-end numbers were measured on llama.cpp b2794 (May 2024) and without fast-aggregation; -fa adds 10-20% speed at some accuracy risk
- llama.cpp throughput on Surface Laptop 7 was thermally unstable in 'Better Performance' mode, so some comparisons depend on the power profile
- Open issues include a segfault (#98) and several build failures (missing t-mac-envs.sh, Windows CMake errors)

## Known shortcomings

- Peer-reviewed paper (EuroSys 2025) is by the project's own authors; baseline llama.cpp b2794 (May 2024) was thermally unstable in default mode; flags for published runs not stated; old x86 may see little speedup.
- At full thread count 4-bit beats llama.cpp Q4_0 by only 1.09x (AGX Orin) and 1.13x (M2 Ultra); 4-5x applies to 1-2-bit models at low thread counts. Not drop-in: needs TVM from source, per-model kernel compile, a 2024 llama.cpp fork; 46 open issues incl. segfault #98.

## Caveats and trade-offs

Numbers are from the authors (README and EuroSys'25 paper, arXiv 2407.00088; paper abstract says 'up to 4x' vs llama.cpp, README says 4\~5x) against llama.cpp b2794 (May 2024). README notes llama.cpp throughput was unstable under thermal limits in 'Better Performance' mode, so a 'Best Performance' re-profile was added; authors warn old x86 platforms may see little speedup, especially for 4-bit. Baseline not in the category list.

Needs TVM built from source and Python tooling; low-bit (1-4 bit) weights only.

## Maintenance

MIT-licensed Microsoft Research project, stale since mid-2025 (last commit 2025-06-03) with 46 open issues; its ideas live on in microsoft/BitNet (bitnet.cpp), which the README says is powered by T-MAC.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now B.
- **Tier reason:** README compares against llama.cpp Q2_K/Q4_0 kernels with the quoted 20/48 tok/s and '4\~5x' figures; the same comparison is published in the peer-reviewed EuroSys 2025 paper (arXiv 2407.00088), which claims up to 4x throughput over llama.cpp. Benchmark script (tools/bench_e2e.py) is public but per-run compiler flags are not stated, so not A.
- **Verifier notes:** Upgraded C-&gt;B on the peer-reviewed EuroSys 2025 paper (authors are the project team, so it is peer-reviewed but not independent). Metadata (MIT, last commit 2025-06-03, stale) checked and correct.
- **Fields the verifier corrected:** `compiler_and_flags`, `hardware`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/microsoft/T-MAC/HEAD/README.md>
  - <https://raw.githubusercontent.com/microsoft/T-MAC/HEAD/LICENSE>
  - <https://github.com/microsoft/T-MAC>
  - <https://github.com/microsoft/T-MAC/commits>
  - <https://arxiv.org/abs/2407.00088>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/microsoft/T-MAC/HEAD/README.md>
  - <https://raw.githubusercontent.com/microsoft/T-MAC/HEAD/docs/profiling_data.md>
  - <https://raw.githubusercontent.com/microsoft/T-MAC/HEAD/CMakeLists.txt>
  - <https://github.com/microsoft/T-MAC/issues>
  - <https://arxiv.org/abs/2407.00088>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/microsoft/t-mac`) · [data/wave8/enrich/raw/github_com_microsoft_t_mac.json](../../../data/wave8/enrich/raw/github_com_microsoft_t_mac.json) (enrichment confidence 0.8)

</details>
