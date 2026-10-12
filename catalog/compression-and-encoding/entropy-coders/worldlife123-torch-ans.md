# torch_ans

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Entropy coders](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> PyTorch C++/CUDA extension for batched parallel rANS coding, pitched as a faster replacement for torchac and CompressAI range coding.

| | |
|---|---|
| **Beats** | torchac and CompressAI range coding (named as replacement target, no head-to-head numbers) |
| **Claimed result** | README: up to 25.8 Gsymbol/s decode (\~29 GB/s payload at \~9 bits/symbol) for rans32_16 with num_interleaves=32 on an RTX 2080 Ti with rows &gt;= 2048. Example output of 'python -m torch_ans.benchmark -d cpu cuda --mode push' (rans64, encode/push mode, 50 MB, 256 symbols, freq precision 16) on i7-6800K / RTX 2080 Ti: CPU 1058.06 MB/s and GPU 6149.65 MB/s at batch 1024. Sparse inverse-CDF table: up to 2.8x on CPU and +80% on CUDA over its own default lookup. benchmark_status.md compares v0.3.0 to v0.2.1 only (CPU 1-way decode 1.27x-1.44x). No head-to-head numbers against torchac, CompressAI or dietgpu; the README only says 25.8 Gsymbol/s is 'the same order of magnitude as dietgpu's numbers'. |
| **Workload** | Parallel rANS encode and decode of batched streams (CPU interleaved, CUDA warp-level decoding with rans32_16 num_interleaves=32) for neural compression pipelines. |
| **Metric** | throughput |
| **Hardware** | Intel i7-6800K (6C12T) and NVIDIA RTX 2080 Ti |
| **Adoption** | 6 stars |
| **Last commit** | 2026-09-14 |
| **Links** | [repository](https://github.com/worldlife123/torch_ans) · [benchmark](https://github.com/worldlife123/torch_ans) |

## Verdict

First-party only: on an i7-6800K and RTX 2080 Ti (torch 2.11.0+cu130), raw rans32_16 32-way CUDA kernels reach 27.8 Gsymbol/s encode and 25.7-26.4 Gsymbol/s decode, CPU 4-way operators 0.4-0.9 Gsymbol/s, and v0.3.0 beats v0.2.1 by 1.27x-2.75x on CPU decode. Every comparison is against its own earlier release or its own lookup variants; no torchac, CompressAI or DietGPU numbers are given, and no compiler version is stated (setup.py uses -O3 -fopenmp -march=native).

## Use it when

- Learned image/video compression in PyTorch where many symbols each use a different, model-predicted distribution and you want entropy coding on the same device as the network
- Large GPU batches (about 2048+ rows on a 68-SM GPU) with freq_precision &lt;= 15, using rans32_16 + num_interleaves=32 + inverse_cdf_precision="auto" for the measured \~26 Gsymbol/s raw decode on an RTX 2080 Ti
- CPU coding of batched tensors where rans64/rans32 with num_interleaves=4 and the auto inverse-CDF table give several hundred Msymbol/s per operator (benchmark_status.md, i7-6800K)
- Research prototyping of rANS variants (state/stream/precision sizes, alias vs inverse-CDF lookup) behind one Python API

## Skip it when

- You need a proven win over torchac or CompressAI: the repo never benchmarks against either, nor against DietGPU, so the speedup over the named baseline is unmeasured
- Small or per-image calls through the high-level API on CUDA: the committed end-to-end numbers are only 1.7-8.7 Msymbol/s decode (256 x 8192 symbols, including stream/bytes conversion), thousands of times below the raw-kernel figures
- Non-PyTorch C++ projects: the coder is built as a torch extension (torch/extension.h, at::parallel_for) and needs a local compiler, plus a matching nvcc for CUDA
- Production or untrusted inputs: the README calls it research-purpose software where segfaults may occur with the low-level API, and out-of-range symbols beyond about 2^30 are silently mis-coded
- Interleaved coding of rans64/rans32 on GPU (CPU-only), or 32-way interleaving on CPU (slower than 4-way per the README)

## How it is fast

Each batch row is an independent rANS stream coded in parallel (OpenMP at::parallel_for on CPU, one thread or one warp per row on CUDA). The rans32_16 32-way path maps 32 interleaved states onto the lanes of a warp with a shared bitstream cursor placed by __ballot_sync/__popc/__shfl_sync accounting (technique credited to Recoil), and stages whole CDF rows plus a sparse inverse-CDF table in shared memory. The CPU coder uses branch-free renormalization, a pipelined floating-point divide with an integer fix-up, register-resident interleaved states, and a sparse 2^q inverse-CDF lookup table with a bounded branch-free walk.

## Compared with alternatives

Pick it over DietGPU or Recoil when you need per-symbol distribution indexes, bypass coding of out-of-range int32 values and a PyTorch tensor API rather than raw byte or fixed-width-symbol buffers; pick constriction instead for single-stream CPU coding with exact model control outside PyTorch, and DietGPU for maximum raw GB/s on data-center GPUs.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | PyTorch (&gt;= 1.10 recommended), pybind11, a C++17 compiler, ninja for the runtime build, OpenMP for CPU parallelism; CUDA toolkit matching torch.version.cuda for GPU |
| **Minimum toolchain** | C++17 (torch 2.x selects its own standard); Python &gt;= 3.7; nvcc &gt;= 12.2 or g++ &lt;= 10 host compiler when libstdc++ is from GCC &gt;= 11.4 |
| **Platforms** | Linux x86_64/aarch64, macOS x86_64/arm64, Windows x86_64; CUDA on NVIDIA GPUs; ROCm untested |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | partial: TorchANSInterface mimics CompressAI's entropy coder API, but the bitstream is its own format and torchac's API is not mirrored |

## Gotchas

- On x86_64 setup.py adds -march=native, so a built extension may not run on an older CPU than the build machine.
- CUDA support is opt-in at build time (WITH_CUDA=1); a CPU-only build asked to code CUDA tensors warns and compiles a CUDA extension on the spot, which takes minutes.
- Interleaved streams reserve one word of slack because renormalization stores speculatively past the cursor; the README warns that misuse of the low-level API can segfault.
- The 4-way CUDA interleaved path decoded wrong symbols in v0.2.1 (benchmark_status.md marks it 'broken'; fixed in v0.3.0), and a Known Issue says the rans64 CUDA test fails on some newer GPU architectures.

## Known shortcomings

- No baseline comparison: every number is a self-comparison (own lookup variants, v0.3.0 vs v0.2.1), none against torchac, CompressAI or dietgpu; the 1058/6149 MB/s figures are rans64 encode, not decode. Tier C.
- No benchmark against torchac, CompressAI or DietGPU anywhere. Raw 32-way CUDA kernels reach 25.7-26.4 Gsym/s decode, but the committed high-level API end-to-end numbers are only 1.7-8.7 Msym/s decode on CUDA (256x8192). setup.py adds -march=native on x86_64. README says research-only; the low-level API can segfault and symbols beyond about 2^30 are silently mis-coded. The 4-way CUDA interleave decoded wrong symbols in v0.2.1 (fixed in v0.3.0). The rans64 CUDA test fails on some newer GPUs.

## Caveats and trade-offs

No head-to-head against torchac, CompressAI, dietgpu or Huffman; all numbers are self-comparisons (own lookup variants, own releases), so it is evidence of speed, not of beating a named baseline. The 1058/6149 MB/s example figures are rans64 encode (push) throughput, not decode. No compiler or flags stated. Last commits (2026-09-14) include automated build-status-table updates. Warp-level technique credited to Recoil/dietgpu.

PyTorch extension with C++/CUDA backends; needs a torch install for use; interleaved CUDA only for rans32_16; compiles locally.

## Maintenance

Actively developed (v0.3.0 released 2026-09-14, 74 commits, 6 stars), MIT-licensed, but self-described as research software with no prebuilt wheels.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): reject; tier before verification C, tier now C.
- **Tier reason:** The README and benchmark_status.md give first-party throughput only (i7-6800K, RTX 2080 Ti; scripts/bench_sparse_invcdf.py, scripts/bench_interleaves_cpu.py, python -m torch_ans.benchmark) with no compiler flags; every comparison is against its own earlier versions or its own lookup variants, never against torchac, CompressAI or any other coder, so the numbers would be C but no baseline win exists.
- **Verifier notes:** Real, active, MIT-licensed project (6 stars) with honest first-party numbers, but no comparison against any baseline anywhere; per the keep-and-document rule the orchestrator may prefer keep at tier C with the no-baseline shortcoming.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier; first-party benchmark
- **Pages the verifier opened:**
  - <https://github.com/worldlife123/torch_ans>
  - <https://github.com/worldlife123/torch_ans/commits>
  - <https://raw.githubusercontent.com/worldlife123/torch_ans/HEAD/README.md>
  - <https://raw.githubusercontent.com/worldlife123/torch_ans/HEAD/benchmark_status.md>
  - <https://raw.githubusercontent.com/worldlife123/torch_ans/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/worldlife123/torch_ans>
  - <https://github.com/worldlife123/torch_ans/issues?q=is%3Aissue>
  - <https://github.com/worldlife123/torch_ans/tree/main/torch_ans>
  - <https://raw.githubusercontent.com/worldlife123/torch_ans/HEAD/README.md>
  - <https://raw.githubusercontent.com/worldlife123/torch_ans/HEAD/benchmark_status.md>
  - <https://raw.githubusercontent.com/worldlife123/torch_ans/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/worldlife123/torch_ans/HEAD/setup.py>
  - <https://raw.githubusercontent.com/worldlife123/torch_ans/HEAD/pyproject.toml>
  - <https://raw.githubusercontent.com/worldlife123/torch_ans/HEAD/torch_ans/rans_warp_cuda.cuh>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/worldlife123/torch_ans`) · [data/wave9/enrich/raw/github_com_worldlife123_torch_ans.json](../../../data/wave9/enrich/raw/github_com_worldlife123_torch_ans.json) (enrichment confidence 0.7)

</details>
