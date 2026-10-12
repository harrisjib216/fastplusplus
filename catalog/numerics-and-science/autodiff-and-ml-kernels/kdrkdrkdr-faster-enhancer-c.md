# faster-enhancer.c

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟢 active

> Dependency-free C int8 runtime for the FastEnhancer-Medium speech denoiser; paper reports 3.3x lower RTF than fp32 ONNX Runtime on M2.

| | |
|---|---|
| **Beats** | ONNX Runtime fp32 graph of the same FastEnhancer-Medium weights |
| **Claimed result** | Repository description: '3.3x faster than the ONNX Runtime graph, same quality'. README: real-time factor 0.069 on one Apple M2 core (I8MM) and 0.096 on Galaxy S23+ (Snapdragon 8 Gen 2); quality PESQ 3.054 vs 3.060 for the fp32 ONNX graph over 824 VoiceBank-DEMAND utterances. |
| **Workload** | Streaming 48 kHz speech enhancement with FastEnhancer-Medium, measured as per-frame real-time factor over 5569-frame clips on Apple M2 and Galaxy S23+ cores. |
| **Metric** | latency |
| **Hardware** | Apple M2 (one core) and Samsung Galaxy S23+ (Snapdragon 8 Gen 2) |
| **Compiler and flags** | CMakeLists.txt defaults to Release with -O3 -Wall -Wextra (no -ffast-math) and per-file tier flags (-march=armv8.2-a+dotprod, -march=armv8.6-a+dotprod+i8mm; x86 -mavx2 -mfma, plus -mavxvnni or -mavx512f/bw/vl/vnni), with optional PGO; the compiler and its version are not stated. |
| **Adoption** | 25 stars |
| **Last commit** | 2026-07-29 |
| **Links** | [repository](https://github.com/kdrkdrkdr/faster-enhancer.c) · [benchmark](https://github.com/kdrkdrkdr/faster-enhancer.c) |

## Verdict

The author's arXiv paper (2607.25350, seen only as a search snippet) reports 0.069 RTF for the int8 engine vs 0.230 for the fp32 ONNX Runtime graph on one Apple M2 core (3.3x); the README tables time only this engine (M2 and Galaxy S23+, 5569-frame clips, median of repeats) and give PESQ 3.054 vs 3.060 for fp32 ONNX over 824 VoiceBank-DEMAND utterances. The ORT version, threads and execution provider were not seen, the compiler is not named, and the ONNX benchmark artifacts the docs place under experiments/ are not in the public repo, so the comparison is int8 vs fp32 and cannot be reproduced from the repo.

## Use it when

- You need FastEnhancer-Medium noise suppression at 48 kHz in a native C/C++ app (voice chat, conferencing, recording) and want to drop the ONNX Runtime dependency.
- Hard real-time audio threads where allocation and allocator jitter are not acceptable: nothing is allocated after fe_init.
- ARMv8.2+ devices with DotProd or I8MM (Apple M-series, recent Snapdragon): README measures 0.069 RTF on one M2 core and 0.096 on a Galaxy S23+.
- Deployments that need bit-reproducible output across SIMD tiers of one architecture family (a SHA-256 regression gate enforces it).
- Small binary budgets: the static library is 162 KiB on macOS arm64 plus the 565 KB weight blob.

## Skip it when

- Any model other than FastEnhancer-Medium at 48 kHz: there is no graph loader, and the one open issue (#1) asks for GTCRN support.
- x86 deployments where you need measured latency: the README times ARM only, the x86 tiers were not re-measured under the current protocol, and the AVX-512 tier was checked only under Intel SDE.
- Older or non-mainstream CPUs: there is no scalar fallback, so fe_init fails on x86 hosts without AVX2+FMA3+F16C (SSE4.1-only parts are deliberately unsupported), and only arm64 and x86-64 build at all (no 32-bit ARM, RISC-V or MSVC).
- Plain ARMv8.0 NEON cores, where the floor tier is about 2.4x (M2) to 3.6x (S23+) slower than the I8MM tier (derived from the README table).
- Several independent streams in one process: the engine is a single global instance, so you cannot run two channels concurrently.

## How it is fast

W8A8 post-training quantization (per-row symmetric int8 weights, per-tensor asymmetric uint8 activations recomputed every frame) feeding six hand-written int8 GEMM microkernel tiers chosen at init: NEON vmull/vmlal/vpadalq, DOTPROD vdotq_laneq_s32 with A row-quad pre-pack, I8MM vmmlaq_s32 with KleidiAI-style row-pair pre-pack, AVX2 vpmovsxbw+vpmaddwd, AVX-VNNI and AVX-512-VNNI vpdpbusd. The k=3 convolutions run as Winograd F(2,3) (2/3 of the multiplies), the GRU (both matmuls, gates and state update) is fused into one kernel per tier, dequantization, residual adds, bias and requantize-scale tracking are fused into GEMM epilogues, and recurrent/skip state is kept in fp16. All state lives in one 432,384-byte struct with no heap allocation after init, and init page-locks buffers and runs a 128-frame warmup.

## Compared with alternatives

Pick it over RTNeural or a general engine such as MNN or OpenVINO only when the model is exactly FastEnhancer-Medium and you want an allocation-free, dependency-free C engine; RTNeural is the better choice for your own small LSTM/GRU/conv audio networks, and general runtimes cover arbitrary graphs.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | none at runtime; Python with ONNX tooling only to regenerate weights from the upstream export (the committed weights/fe.q8 blob avoids this) |
| **Minimum toolchain** | C11, CMake 3.20+, GCC or Clang with GNU-style target attributes (MSVC and clang-cl rejected; MinGW or GNU-driver Clang on Windows) |
| **Platforms** | arm64 (NEON baseline; DotProd/I8MM tiers) and x86-64 (AVX2+FMA3+F16C required; AVX-VNNI, AVX-512 VNNI tiers); macOS, Linux, Android, Windows via MinGW |
| **Thread safety** | Not thread-safe: fe.h states a single global engine instance with single-threaded calls only; fe_run is not reentrant and fe_init/run/reset/free must not be called concurrently. |
| **Drop-in for the baseline** | partial — reproduces the same FastEnhancer-Medium model as the ONNX graph, but you replace the ORT session with the fe_\* C API, a converted int8 blob and fixed 320-sample framing |

## Gotchas

- Global state: one engine per process; a second fe_init without fe_free is a no-op, so switching weight blobs needs fe_free first, and the blob memory must outlive the engine (weights are referenced zero-copy).
- Built with -ffinite-math-only and documented as a finite-input contract: feeding NaN or Inf samples is unsupported.
- Benchmarks race the core; a paced real-time callback on an M2 P-core costs 4.2x more per frame (0.286 RTF), and docs show E-cores on hybrid Intel parts run a frame 3.6x slower, so set thread priority/QoS yourself (the library does not).
- Output is delayed by a fixed 704 samples; comparing against an offline centered-STFT reference measures framing phase, not quantization error (the docs' own earlier fidelity table had this error and was corrected).

## Known shortcomings

- Docs say the ONNX benchmark artifacts are in experiments/, but that directory is a 404 in the public repo, so the 3.3x baseline timing cannot be reproduced; int8 compared against fp32.
- The 0.069 vs 0.230 RTF (3.3x) figure comes only from a search snippet (arXiv blocked); x86 tiers are not timed; one global engine, not thread-safe; built with -ffinite-math-only, so NaN/Inf input is unsupported.

## Caveats and trade-offs

The 3.3x figure is only in the repository description; the README tables time faster-enhancer.c alone and give no ONNX Runtime timing. A search-engine snippet of the arXiv abstract (2607.25350; arxiv.org could not be opened here) gives 0.069 RTF vs 0.230 for the fp32 ONNX Runtime graph on the same M2 core; the ORT version, thread count and execution provider were not seen. docs/optimizations.md says the ONNX benchmark logs and scripts are committed under experiments/, but the public repo has no experiments/ directory (404), so the baseline timing cannot be reproduced from the repo. The comparison is int8 W8A8 against an fp32 graph, so precision differs (PESQ 3.054 vs 3.060). The x86 tiers are not timed in the README, and the docs say the x86 rows of the paper's Table 1 have no artifact. A paced real-time callback costs 4.2x more per frame (0.286 RTF) than the racing benchmark. Single-model runtime, not a general kernel library.

One fixed model with W8A8 post-training quantization; six hand-written int8 GEMM kernel tiers (ARM NEON, DOTPROD, I8MM; x86 AVX2, AVX-VNNI, AVX-512 VNNI) chosen at init with no scalar fallback and no heap allocation after startup; draws on ggml, XNNPACK, oneDNN and Arm kernel patterns.

## Maintenance

Active but young (4 commits, last 2026-07-29, single author, 25 stars); MIT-licensed C with no dependencies, so it is easy to vendor if your model matches.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party: the repo description claims 3.3x over the ONNX Runtime graph and the README gives the runtime's own RTF tables (Apple M2, Galaxy S23+) and PESQ against fp32 ONNX, but the ONNX Runtime timing and its harness are not in the public repo, and the compiler is not named.
- **Verifier notes:** README numbers (0.069 / 0.096 RTF, PESQ 3.054 vs 3.060, 824 utterances, 4.2x paced cost) match the record. Metadata from github.com: MIT, 25 stars, 5 forks, not a fork or archived, 4 commits, last 2026-07-29. A docs claim of committed ONNX benchmark artifacts is not borne out by the public tree; worth recording as a reproducibility shortcoming.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/kdrkdrkdr/faster-enhancer.c>
  - <https://raw.githubusercontent.com/kdrkdrkdr/faster-enhancer.c/HEAD/README.md>
  - <https://raw.githubusercontent.com/kdrkdrkdr/faster-enhancer.c/HEAD/docs/optimizations.md>
  - <https://raw.githubusercontent.com/kdrkdrkdr/faster-enhancer.c/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/kdrkdrkdr/faster-enhancer.c/HEAD/LICENSE>
  - <https://github.com/kdrkdrkdr/faster-enhancer.c/commits>
  - <https://github.com/kdrkdrkdr/faster-enhancer.c/tree/main/experiments>
- **Sources the enricher read:**
  - <https://github.com/kdrkdrkdr/faster-enhancer.c>
  - <https://github.com/kdrkdrkdr/faster-enhancer.c/issues>
  - <https://raw.githubusercontent.com/kdrkdrkdr/faster-enhancer.c/HEAD/README.md>
  - <https://raw.githubusercontent.com/kdrkdrkdr/faster-enhancer.c/HEAD/docs/optimizations.md>
  - <https://raw.githubusercontent.com/kdrkdrkdr/faster-enhancer.c/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/kdrkdrkdr/faster-enhancer.c/HEAD/include/fe.h>
  - WebSearch snippet of https://arxiv.org/abs/2607.25350 (arxiv.org itself egress-blocked)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/kdrkdrkdr/faster-enhancer.c`) · [data/wave8/enrich/raw/github_com_kdrkdrkdr_faster_enhancer_c.json](../../../data/wave8/enrich/raw/github_com_kdrkdrkdr_faster_enhancer_c.json) (enrichment confidence 0.75)

</details>
