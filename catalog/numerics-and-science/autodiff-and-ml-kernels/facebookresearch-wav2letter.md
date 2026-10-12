# Wav2Letter++

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-3-Clause` · 🔴 abandoned

> FAIR's all-C++ end-to-end speech-recognition training toolkit; its 2018 paper claims faster training than ESPnet, Kaldi and OpenSeq2Seq.

| | |
|---|---|
| **Beats** | ESPnet, Kaldi and OpenSeq2Seq (other end-to-end ASR training frameworks; the paper compares training time per batch against these) |
| **Claimed result** | Paper abstract (snippet only): 'in some cases more than 2x faster than other optimized frameworks for training end-to-end neural networks for speech recognition', and training times scale linearly to 64 GPUs (the highest tested) for models with 100 million parameters. The comparison against ESPnet, Kaldi and OpenSeq2Seq is in the paper's Figure 4 (training time per batch for a 30M-parameter recurrent model and a 100M-parameter convolutional model across GPU counts). The search record's 'more than 15% faster than the next-best system on a single GPU' figure could not be confirmed in any snippet seen in this verification and should be treated as unverified until the paper is read. |
| **Workload** | Training time per batch (4 utterances per GPU) on the Wall Street Journal (WSJ) large-vocabulary task for a 30M-parameter recurrent acoustic model and a 100M-parameter purely convolutional acoustic model, scaled from one GPU up to 64 GPUs, against ESPnet, Kaldi and OpenSeq2Seq (paper Figure 4, snippet only). |
| **Metric** | throughput |
| **Hardware** | Machines with eight NVIDIA Tesla V100 Tensor Core GPUs (SXM2 modules, 16 GB each), per search-result summary of the paper; CPU model not seen. |
| **Adoption** | 6.4k stars |
| **Last commit** | 2026-08-28 |
| **Links** | [repository](https://github.com/flashlight/wav2letter) · [benchmark](https://arxiv.org/abs/1812.07625) |

## Verdict

First-party FAIR paper (arXiv 1812.07625, ICASSP 2019), seen only through search-result summaries: on WSJ with 4 utterances per GPU on machines with eight 16 GB V100s, wav2letter++ trained a 30M-parameter DeepSpeech-2-style RNN (2 conv, 5 BiLSTM, 2 linear layers) more than 15% faster than the next-best of ESPnet, Kaldi and OpenSeq2Seq (fp32 and mixed-precision fp16 runs) even on one GPU, was 'in some cases more than 2x faster', and scaled linearly to 64 GPUs on a 100M-parameter model of 18 temporal convolutions plus 1 linear layer. Framework versions, compiler flags, CPU model and the per-framework times per batch were not seen.

## Use it when

- Reproducing FAIR's 2016-2020 ASR papers and pretrained models (conv_glu, seq2seq_tds, lexicon_free, sota/2019, streaming_convnets, self_training, slimIPL, MLS) exactly; the README says this requires Flashlight &lt;= 0.3.2.
- Training CTC or ASG acoustic models from a pure C++ stack on Linux with NVIDIA GPUs and MPI-based multi-node data parallelism, with no Python runtime.
- Reusing the ASG criterion kernels (CUDA and CPU) or the KenLM-backed lexicon beam-search decoder on their own, via v0.2's libraries-only build (W2L_BUILD_LIBRARIES_ONLY) or its Python bindings.
- As a reference for how a 2018 C++ ASR system organised its loss kernels, decoder pruning and prefetching data loader.

## Skip it when

- New ASR projects: the README says development moved to Flashlight's ASR application, and every commit since 2023 is a Meta-internal lint, formatter or build sync; v0.2 is tied to Flashlight v0.2 and ArrayFire &gt;= 3.6.1, and main refuses to configure against Flashlight &gt;= 0.4.
- Expecting the speed claim to hold today: the only comparison is against 2018 versions of ESPnet, Kaldi and OpenSeq2Seq, and no comparison with any current toolkit was found.
- ASG with large output vocabularies: the CUDA ASG workspace holds two B x N x N double-precision buffers plus two B x T x N ones, so memory grows quadratically with the token set; issue #802 reports a 12.8 GB allocation failure on a V100 after switching a working CTC setup to ASG.
- Teams without time to tune: users report slow training (issue #621 conv_glu on a P40 at 2.10 sec/sec, #835 4x T4 at 67.79 sec/sec and 18 h per epoch on about 1,000 h of audio, #672 a Transformer on 1k h LibriSpeech taking over a week on one GPU) with no maintainer diagnosis visible.
- Non-Ubuntu or non-NVIDIA setups: the tested paths are the CPU and CUDA Dockerfiles; issue #800 is titled 'Cannot build wav2letter on non-ubuntu systems', and macOS and Windows are not documented.

## How it is fast

There is no Python interpreter in the training loop: models run on Flashlight's tape autograd over ArrayFire tensors (per the catalogued Flashlight entry, ArrayFire JIT-fuses element-wise ops and convolutions and RNNs go to cuDNN), and multi-GPU training is synchronous data-parallel through Flashlight's distributed backend, which the build requires. The ASG loss has hand-written CUDA kernels (one thread block per batch item and token per time step, CUB BlockReduce max and sum for a log-sum-exp forward/backward recursion, double-precision accumulators in a single preallocated workspace), CTC on GPU goes through the vendored Baidu warp-ctc, and feature loading is prefetched on a thread pool (--nthread futures cache). Decoding is a C++ beam search over a lexicon trie with a per-frame token beam (top-K partial sort), score-threshold pruning, hypothesis merging by sort plus optional log-add, and an LM-state cache.

## Compared with alternatives

Pick it over Flashlight, its catalogued successor that absorbed this code as the ASR app, only to reproduce the pre-2021 wav2letter recipes and models on a pinned Flashlight &lt;= 0.3.2 or v0.2 stack; for new C++ training use Flashlight, and for Python-first work PyTorch.

## Integration

| | |
|---|---|
| **Form** | CMake project building executables (Train, Test, Decode) and static libraries (wav2letter-libraries, with a libraries-only option); main builds only recipe tools against an installed Flashlight 0.3 |
| **Dependencies** | v0.2: Flashlight v0.2 built with distributed and contrib targets, ArrayFire &gt;= 3.6.1, KenLM, gflags, glog, FFTW3, libsndfile, a BLAS (ATLAS, OpenBLAS, Accelerate or MKL), optional OpenMP; on GPU CUDA &gt;= 9.2 with vendored warp-ctc and auto-downloaded CUB 1.8.0; inference platform: FBGEMM and cereal. main: Flashlight 0.3.x (&lt; 0.4) built with app/asr (flashlight::fl_pkg_speech) |
| **Minimum toolchain** | v0.2: C++11, g++ &gt;= 4.8, CMake &gt;= 3.5.1, CUDA &gt;= 9.2. main recipes: C++17 and CMake 3.10 (a stale CMakeLists comment says C++14) |
| **Platforms** | Linux x86-64 with NVIDIA CUDA GPUs (main path) or Flashlight's CPU backend; Dockerfiles for CPU, CUDA and inference; other platforms not documented |
| **Thread safety** | not documented for the libraries; W2lDataset::get() is marked thread-hostile when --nthread &gt; 0 (one caller thread, sequential indices) |
| **Drop-in for the baseline** | no |

## Gotchas

- No benchmark harness to check: neither the v0.2 tree nor main contains scripts or configs for the ESPnet/Kaldi/OpenSeq2Seq comparison, and an issue search for 'benchmark speed' returns nothing, so the paper's per-framework times cannot be reproduced from the repository.
- The CUDA CTC criterion (src/criterion/backend/cuda/ConnectionistTemporalClassificationCriterion.cpp, v0.2) passes an input length of T for every utterance, so padding frames are scored as speech, and silently clips each target so that length plus repeats fits in T ('A heuristic to modify target length'), truncating over-long transcripts without a warning; it also copies targets, target sizes and scales to the host on every batch.
- ASG kernels accumulate in double precision and preallocate B x T x N and B x N x N double buffers per call (FullConnectionCriterion.cu), which is what makes ASG memory-hungry for big token sets.
- Licence labels disagree: the main README and GitHub's sidebar say MIT, but the LICENSE file (and the v0.2 README) carry the BSD licence text for wav2letter++; both are permissive.

## Known shortcomings

- Numbers come only from search snippets of the first-party 2018 FAIR paper (arXiv 1812.07625, blocked): 'over 2x' faster than ESPnet, Kaldi and OpenSeq2Seq and linear scaling to 64 GPUs; the '15% faster on one GPU' figure was not found in any snippet. Baselines are speech toolkits, so filed under numerics-and-science/autodiff-and-ml-kernels. The repo redirects to flashlight/wav2letter and the README says the code moved into Flashlight (listed separately in wave 12); LICENSE is BSD-3-Clause although the README says MIT; the only recent commit is a bot lint commit (2026-08-28). Paper-access retier candidate.
- Enricher: no benchmark harness exists in v0.2 or main; the ESPnet/Kaldi/OpenSeq2Seq numbers live only in the blocked paper (a search summary adds 'more than 15% faster than the next-best, even on a single GPU' for the 30M RNN). The v0.2 CUDA CTC gives every utterance the full input length T, so padding frames are scored as speech, and over-long targets are clipped silently; the ASG CUDA workspace grows quadratically with the token set (issue #802, 12.8 GB OOM). Licence files disagree (README MIT, LICENSE BSD). Slow-training user issues #621, #835, #672 undiagnosed.

## Caveats and trade-offs

Snippet only for the numbers: the README links the paper (arXiv 1812.07625, titled 'wav2letter++: The Fastest Open-source Speech Recognition System' on arXiv; ICASSP 2019 version) but neither the README nor the repository contains benchmark code or numbers, and arxiv.org, ar5iv, sigport, neurohive and similar mirrors were EGRESS_BLOCKED, so the paper's per-framework milliseconds-per-batch figure was never read. The paper is first-party (FAIR authors), measured in late 2018 on 8x NVIDIA Tesla V100 SXM2 16 GB machines against 2018 versions of ESPnet, Kaldi and OpenSeq2Seq; GPU training throughput there is largely set by the ArrayFire/cuDNN kernels underneath. The baselines are ASR training frameworks, not the video-audio category incumbents (FFmpeg, x264/x265, Opus); the project fits the ML-framework category better. The repository now redirects to flashlight/wav2letter and its README says wav2letter has been moved and consolidated into Flashlight (ASR application); reproducing its recipes requires Flashlight &lt;= 0.3.2. Flashlight itself is already verified in wave 12 (autodiff-and-ml-kernels). Licence discrepancy: README says MIT, the LICENSE file is BSD 3-clause text (recorded as BSD-3-Clause). Recent commits (latest 2026-08-28, 'Fix B001: Replace bare except with except Exception') are automated or lint-formatting commits from the upstream monorepo sync, not feature development.

Training toolkit for speech-recognition research, not a drop-in library replacement: it needs the ArrayFire tensor library and Flashlight (v0.2/0.3 branches), and the README says results reproduction needs Flashlight &lt;= 0.3.2. Development moved into the Flashlight ASR application, so this repo is a frozen recipe and model collection. The category video-audio is the closest fit in this wave; the project is a machine-learning training system. The baselines are Python/TensorFlow/PyTorch/Kaldi systems, not C++ standard-library facilities.

## Maintenance

Effectively abandoned since the 2020-21 move into Flashlight (latest commit 2026-08-28 is an automated lint fix, 98 open issues) but BSD-licensed and usable as a reference or for recipe reproduction on a pinned Flashlight &lt;= 0.3.2 or v0.2 stack; the speed claim rests on a first-party 2018 paper read through snippets only.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The only numbers source is the first-party FAIR paper (arXiv 1812.07625, ICASSP 2019) linked from the README; arxiv.org was EGRESS_BLOCKED and no GitHub-hosted copy was found, so the claims come from search-result snippets of the abstract and experiment setup only (snippet only), which caps the record at C. The repository itself carries no benchmark code or numbers; a paper-access retier could move it to B (peer-reviewed), but A is unlikely because the competitor framework versions, compiler flags and CPU model are not known to be stated.
- **Verifier notes:** Record checked: repo exists (redirects to flashlight/wav2letter, 6.4k stars, 987 forks, not archived, not a fork), LICENSE is BSD-3-Clause text (README claims MIT), last commit 2026-08-28 confirmed; maintenance_status left at 'abandoned' although the 12-month rule would say 'active', because every recent commit is a bot or formatting sync and the README states development moved to Flashlight (orchestrator may prefer 'stale' or 'active' per the mechanical rule). Shortcomings to record: numbers snippet only from a first-party 2018 paper, unconfirmed '15% single GPU' figure, off-category baselines (ESPnet/Kaldi/OpenSeq2Seq rather than FFmpeg/x264/Opus; consider a category override to autodiff-and-ml-kernels), and overlap with the already-verified Flashlight entry (wave 12) into which wav2letter was consolidated; it is a distinct project with a distinct paper claim, so not marked as a duplicate here. Paper-access retier candidate (ICASSP 2019 peer-reviewed, possible B).
- **Fields the verifier corrected:** `benchmark_url`, `baseline_in_list`, `claimed_speedup`, `workload`, `caveats`
- **Shortcomings recorded by:** arXiv snippets (verifier); enricher code reading
- **Pages the verifier opened:**
  - <https://github.com/facebookresearch/wav2letter>
  - <https://github.com/flashlight/wav2letter/commits>
  - <https://raw.githubusercontent.com/facebookresearch/wav2letter/HEAD/README.md>
  - <https://raw.githubusercontent.com/facebookresearch/wav2letter/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/flashlight/wav2letter>
  - <https://raw.githubusercontent.com/flashlight/wav2letter/HEAD/README.md>
  - <https://raw.githubusercontent.com/flashlight/wav2letter/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/flashlight/wav2letter/HEAD/CMakeLists.txt>
  - <https://github.com/flashlight/wav2letter/commits>
  - <https://github.com/flashlight/wav2letter/tree/main/recipes>
  - <https://raw.githubusercontent.com/flashlight/wav2letter/main/recipes/CMakeLists.txt>
  - <https://raw.githubusercontent.com/flashlight/wav2letter/main/recipes/README.md>
  - <https://github.com/flashlight/wav2letter/tree/v0.2>
  - <https://raw.githubusercontent.com/flashlight/wav2letter/v0.2/README.md>
  - <https://raw.githubusercontent.com/flashlight/wav2letter/v0.2/CMakeLists.txt>
  - <https://raw.githubusercontent.com/flashlight/wav2letter/v0.2/LICENSE>
  - <https://github.com/flashlight/wav2letter/tree/v0.2/src>
  - <https://github.com/flashlight/wav2letter/tree/v0.2/src/libraries>
  - <https://github.com/flashlight/wav2letter/tree/v0.2/src/criterion>
  - <https://github.com/flashlight/wav2letter/tree/v0.2/src/criterion/backend>
  - <https://github.com/flashlight/wav2letter/tree/v0.2/src/criterion/backend/cuda>
  - <https://github.com/flashlight/wav2letter/tree/v0.2/src/libraries/criterion>
  - <https://github.com/flashlight/wav2letter/tree/v0.2/src/libraries/decoder>
  - <https://raw.githubusercontent.com/flashlight/wav2letter/v0.2/src/libraries/CMakeLists.txt>
  - <https://raw.githubusercontent.com/flashlight/wav2letter/v0.2/src/libraries/criterion/CMakeLists.txt>
  - <https://raw.githubusercontent.com/flashlight/wav2letter/v0.2/src/libraries/criterion/cuda/FullConnectionCriterion.cu>
  - <https://raw.githubusercontent.com/flashlight/wav2letter/v0.2/src/libraries/criterion/cuda/ForceAlignmentCriterion.cu>
  - <https://raw.githubusercontent.com/flashlight/wav2letter/v0.2/src/criterion/CMakeLists.txt>
  - <https://raw.githubusercontent.com/flashlight/wav2letter/v0.2/src/criterion/ConnectionistTemporalClassificationCriterion.cpp>
  - <https://raw.githubusercontent.com/flashlight/wav2letter/v0.2/src/criterion/backend/cuda/ConnectionistTemporalClassificationCriterion.cpp>
  - <https://raw.githubusercontent.com/flashlight/wav2letter/v0.2/src/libraries/decoder/LexiconDecoder.h>
  - <https://raw.githubusercontent.com/flashlight/wav2letter/v0.2/src/libraries/decoder/LexiconDecoder.cpp>
  - <https://raw.githubusercontent.com/flashlight/wav2letter/v0.2/src/libraries/decoder/Utils.h>
  - <https://raw.githubusercontent.com/flashlight/wav2letter/v0.2/src/data/W2lDataset.h>
  - <https://raw.githubusercontent.com/flashlight/wav2letter/v0.2/src/data/W2lDataset.cpp>
  - <https://raw.githubusercontent.com/flashlight/wav2letter/v0.2/inference/README.md>
  - <https://raw.githubusercontent.com/flashlight/wav2letter/v0.2/inference/CMakeLists.txt>
  - <https://raw.githubusercontent.com/flashlight/wav2letter/v0.2/bindings/python/README.md>
  - <https://github.com/flashlight/wav2letter/wiki>
  - <https://github.com/flashlight/wav2letter/wiki/Dependencies>
  - <https://github.com/flashlight/wav2letter/issues?q=is%3Aissue+benchmark+speed>
  - <https://github.com/flashlight/wav2letter/issues?q=espnet>
  - <https://github.com/flashlight/wav2letter/issues?q=slow>
  - <https://github.com/flashlight/wav2letter/issues/672>
  - <https://github.com/flashlight/wav2letter/issues/835>
  - <https://github.com/flashlight/wav2letter/issues/621>
  - <https://github.com/flashlight/wav2letter/issues/802>
  - WebSearch snippets for arXiv 1812.07625 (arxiv.org, deepai.org and hgpu.org were EGRESS_BLOCKED)
  - /home/user/fastpp/data/wave12/enrich/raw/github_com_flashlight_flashlight.json (catalogued Flashlight entry)
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/facebookresearch/wav2letter`) · [data/wave10/enrich/raw/github_com_facebookresearch_wav2letter.json](../../../data/wave10/enrich/raw/github_com_facebookresearch_wav2letter.json) (enrichment confidence 0.55)

</details>
