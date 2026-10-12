# MANS (Multi-byte ANS compressor)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Entropy coders](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> ANS pipeline for 16/32-bit integer arrays on CPU, CUDA and HIP; reports 1.92x/2.04x faster than FSE on CPU.

| | |
|---|---|
| **Beats** | FSE-ANS (Finite State Entropy) on CPU; nvCOMP Huffman on GPU; 16-bit Huffman for ratio |
| **Claimed result** | CPU: 1.92x faster compression and 2.04x faster decompression vs FSE-ANS; 1.24x higher compression ratio than FSE-ANS in portable mode (README also lists 2.37x vs FSE-ANS in ratio mode). A100: 45.14x faster compression vs nvCOMP Huffman. |
| **Workload** | Compression and decompression of multi-byte (16/32-bit) integer scientific data; CPU run on an Intel Xeon Gold 5220S, GPU runs on NVIDIA A100 and AMD MI210; Adaptive Data Mapping converts multi-byte integers to 8-bit symbols before ANS. |
| **Metric** | throughput |
| **Hardware** | Intel Xeon Gold 5220S CPU; NVIDIA A100 GPU; AMD MI210 GPU |
| **Adoption** | 11 stars |
| **Last commit** | 2026-09-30 |
| **Links** | [repository](https://github.com/hpdps-group/MANS) · [benchmark](https://github.com/hpdps-group/MANS) |

## Verdict

First-party README figures (THR.png, no compiler flags or exact commands given) on a Xeon Gold 5220S show 1.92x faster compression and 2.04x faster decompression than FSE-ANS. On an A100, compression is 45.14x faster than nvCOMP Huffman (not nvCOMP ANS). The SC25 paper abstract (search snippet only, ACM blocked) confirms an average 1.24x ratio gain and 870.27 MB/s on CPU, but not the FSE throughput comparison.

## Use it when

- Lossless compression of uint16 or uint32 scientific arrays with locally narrow value ranges (photon-science detector frames, quantized simulation output), where generic byte coders do poorly.
- Pipelines that compress on GPU and decompress on CPU or the reverse: P-mode streams interoperate between the CPU and NVIDIA backends, with a cross-backend test.
- HDF5 datasets, through the H5Z-MANS filter plugin.
- Many small slices (kilobytes to a few MB), where the authors say it is more stable than 16-bit Huffman and the autotuner picks thread counts per size.

## Skip it when

- Generic byte streams, text, signed or floating-point data: only unsigned 16-bit and 32-bit integers are supported.
- Blocks whose value range is 3500 or more fall back to RAW, so high-entropy or noisy integer data gains little.
- When you need a proven speed comparison against nvCOMP's ANS codec: the GPU claim (45.14x) is against nvCOMP Huffman, and the 288.45x/135.86x figures compare the GPU to MANS's own CPU mode.
- Non-x86 CPUs without editing the build: MANS_CPU_ARCH_FLAGS defaults to -march=native -mavx2, and -march=native binaries do not move between machines.
- R-mode (best-ratio) streams on the GPU: the NVIDIA backend accepts P mode only.

## How it is fast

ADM works per block (512 elements in 1D, 16x16 tiles in 2D, 4096-element tiles in 3D): if the block's value range is under 3500 it stores the block mean as a center and emits each value as an 8-bit code of its signed offset within 126-wide bands, with the band index in a separate bit-signal stream; wider blocks go RAW. Byte symbols then compress far better and faster than coding 16/32-bit words directly. In P mode the bytes go to a 32-lane interleaved rANS whose GPU kernels are Meta's DietGPU code (files keep Meta's copyright header) and whose CPU port writes the same warp-state format, so CPU and GPU streams interoperate; R mode feeds the bytes to a vendored FSE (tANS) for the best ratio. CPU stages are OpenMP-parallel and built with -march=native -mavx2 by default.

## Compared with alternatives

Pick MANS over DietGPU when your data is 16/32-bit integers rather than bytes or float exponents, or when you need the same stream on CPU, NVIDIA and AMD; for plain byte streams on CPU, FiniteStateEntropy, hypersonic-rANS or htscodecs are simpler and benchmarked on standard corpora.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | OpenMP for the CPU backend; CUDA toolkit (12.6 named) for NVIDIA; hipcc/ROCm (or DTK for DCU) for AMD; HDF5 only for the optional plugin (on by default); FSE and DietGPU-derived ANS sources are vendored |
| **Minimum toolchain** | C++17, CMake 3.15+; CUDA 12.6 per README (Dockerfile uses nvidia/cuda:12.6.2-devel-ubuntu22.04) |
| **Platforms** | x86-64 CPUs (AVX2 by default flags), NVIDIA GPUs, AMD GPUs via HIP and Hygon DCUs; Ubuntu 22.04+ recommended |
| **Thread safety** | not documented; the CPU path reuses named scratch buffers from a buffer cache (cache.get_t), so concurrent calls from several threads should be treated as unsafe until checked |
| **Drop-in for the baseline** | no |

## Gotchas

- The license is inconsistent: README badge and GitHub sidebar say MIT, but the LICENSE file at HEAD is BSD 3-Clause; the vendored GPU ANS files carry Meta's MIT header.
- nv/ans/CMakeLists.txt hard-codes CMAKE_CUDA_COMPILER to /usr/local/cuda/bin/nvcc and defines _GLIBCXX_USE_CXX11_ABI=0, which can break linking against code built with the default libstdc++ ABI.
- The --dims product must equal the element count, and the HDF5 plugin builds unless you pass -DBUILD_HDF5_PLUGIN=OFF.
- The API reports errors by throwing std::runtime_error (for example when a backend was not compiled in), and the default build enables timing instrumentation (ENABLE_TIMING=ON).

## Known shortcomings

- Tier C: README numbers (1.92x/2.04x vs FSE-ANS, 45.14x vs nvCOMP Huffman on a Xeon Gold 5220S) are first-party; the SC25 paper and its SC25 Reproducibility Report (doi 10.1145/3712285.3769469) are both unopened (ACM blocked) and the report is a B candidate for a retier check.
- The 45.14x GPU claim is against nvCOMP Huffman, not nvCOMP ANS. nv/ans hard-codes /usr/local/cuda/bin/nvcc and _GLIBCXX_USE_CXX11_ABI=0. CPU flags default to -march=native -mavx2. Only uint16/uint32 inputs; the NVIDIA path supports P mode only. The GPU ANS (nv/ans/src/GpuANS.cu, Meta copyright header) derives from DietGPU; R mode is vendored FSE. LICENSE at HEAD is BSD 3-Clause although the README badge says MIT.

## Caveats and trade-offs

README numbers only: the figure images (THR.png, CR.png) carry the detail, and no compiler flags or exact benchmark commands are given for the published figures (the repo does ship cpu_mans_bench and an autotune tool). A peer-reviewed SC25 paper (doi 10.1145/3712285.3759825) and an SC25 Reproducibility Report for it (doi 10.1145/3712285.3769469) exist, but ACM is blocked here so neither was opened; a verifier with ACM access could raise the tier to B. The abstract (search snippet) mentions the 1.24x average ratio gain, 870.27 MB/s CPU throughput and the 288.45x/135.86x GPU-vs-CPU speedups, not the FSE throughput comparison. The README's 2.37x figure is attributed to 16-bit Huffman in Key Features but to FSE-ANS (-r mode) in the ratio section. The 288x and 135x figures compare GPU to the project's own CPU mode, not to a third-party baseline.

Targets multi-byte integer data (HPC and sensor slices), not generic byte streams. Needs OpenMP; GPU paths need CUDA 12.6 or ROCm. The portable CPU mode trades some ratio for consistency with the GPU format.

## Maintenance

Actively developed (27 commits, last 2026-09-30 adding DCU/AMD support, 11 stars), backed by a peer-reviewed SC25 paper with a reproducibility report; permissively licensed, though the MIT-versus-BSD-3 mismatch should be settled before vendoring.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The README gives first-party speedups vs FSE-ANS on a Xeon Gold 5220S (1.92x compression, 2.04x decompression) and vs nvCOMP Huffman on an A100 (45.14x), with no compiler flags or stated benchmark command for those figures. The SC25 paper's abstract (seen in a search snippet) confirms only the 1.24x ratio gain, 870.27 MB/s CPU throughput and the GPU-vs-own-CPU speedups, not the FSE throughput win, and the paper itself could not be opened (ACM blocked).
- **Verifier notes:** README numbers match the record; MIT, 11 stars, not archived, last commit 2026-09-30 ('dcu & amd version'). The SC25 reproducibility report is worth a retier check from an environment with ACM access, since an artifact-evaluation report is independent measurement.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier; first-party benchmark
- **Pages the verifier opened:**
  - <https://github.com/hpdps-group/MANS>
  - <https://raw.githubusercontent.com/hpdps-group/MANS/HEAD/README.md>
  - <https://github.com/hpdps-group/MANS/commits>
- **Sources the enricher read:**
  - <https://github.com/hpdps-group/MANS>
  - <https://raw.githubusercontent.com/hpdps-group/MANS/HEAD/README.md>
  - <https://raw.githubusercontent.com/hpdps-group/MANS/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/hpdps-group/MANS/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/hpdps-group/MANS/HEAD/mans_api.hpp>
  - <https://raw.githubusercontent.com/hpdps-group/MANS/HEAD/mans_api.cpp>
  - <https://raw.githubusercontent.com/hpdps-group/MANS/HEAD/mans_defs.h>
  - <https://raw.githubusercontent.com/hpdps-group/MANS/HEAD/bench.csv>
  - <https://raw.githubusercontent.com/hpdps-group/MANS/HEAD/Dockerfile>
  - <https://github.com/hpdps-group/MANS/tree/main/cpu>
  - <https://github.com/hpdps-group/MANS/tree/main/cpu/adm>
  - <https://raw.githubusercontent.com/hpdps-group/MANS/HEAD/cpu/mans_cpu.h>
  - <https://raw.githubusercontent.com/hpdps-group/MANS/HEAD/cpu/adm/adm.h>
  - <https://raw.githubusercontent.com/hpdps-group/MANS/HEAD/cpu/adm/adm_utils.cpp>
  - <https://raw.githubusercontent.com/hpdps-group/MANS/HEAD/cpu/pans/pans_utils.cpp>
  - <https://raw.githubusercontent.com/hpdps-group/MANS/HEAD/cpu/fse/CMakeLists.txt>
  - <https://raw.githubusercontent.com/hpdps-group/MANS/HEAD/nv/ans/CMakeLists.txt>
  - <https://raw.githubusercontent.com/hpdps-group/MANS/HEAD/nv/ans/src/GpuANS.cu>
  - WebSearch: MANS Multi-Byte Integer Data ANS SC25 (snippet of dl.acm.org/doi/10.1145/3712285.3759825; page blocked here)
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/hpdps-group/mans`) · [data/wave9/enrich/raw/github_com_hpdps_group_mans.json](../../../data/wave9/enrich/raw/github_com_hpdps_group_mans.json) (enrichment confidence 0.75)

</details>
