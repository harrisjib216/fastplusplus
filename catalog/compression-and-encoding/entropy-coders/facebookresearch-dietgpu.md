# DietGPU (GPU rANS codec)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Entropy coders](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🔴 abandoned

> CUDA byte-wise rANS encoder/decoder at 250-410 GB/s on A100; open alternative to nvCOMP's proprietary ANS codec.

| | |
|---|---|
| **Beats** | nvCOMP ANS (NVIDIA proprietary GPU ANS codec); the README itself compares against nothing |
| **Claimed result** | README: ANS codec 'operates at throughputs around 250-410 GB/s for reasonable data sizes on an A100 GPU'. Third-party snippet (arXiv 2606.18900, not opened): 592.5 GB/s decode and 364.9 GB/s encode on H100, above the 480 GB/s the snippet attributes to nvcomp-ANS. |
| **Workload** | Batched GPU rANS encode and decode of byte arrays on an A100 (README) and on an H100 (third-party paper snippet), 4 KiB segments per warp, 9-11 bit probability precision. |
| **Metric** | throughput |
| **Hardware** | NVIDIA A100 (README); H100 (third-party snippet) |
| **Adoption** | 396 stars |
| **Last commit** | 2026-03-18 |
| **Links** | [repository](https://github.com/facebookresearch/dietgpu) · [benchmark](https://github.com/facebookresearch/dietgpu) |

## Verdict

The README reports first-party absolute rANS throughput of about 250-410 GB/s on one A100 at batch size 1 via the PyTorch API on torch.normal-derived data, with no baseline on the page. A third-party preprint (arXiv 2606.18900, seen only as a search snippet) measured 364.9 GB/s encode and 592.5 GB/s decode on H100 (256 MB, batch 4096 x 64 KB) against 480 GB/s for nvcomp-ANS; a 2025 user request for an nvCOMP comparison (issue #20) got no maintainer reply.

## Use it when

- Compressing data already resident in GPU memory before sending it over NVLink, PCIe or InfiniBand, where interconnect bandwidth rather than ratio is the bottleneck.
- Entropy-coding stage for a GPU compression pipeline (LZ or RLE literal/match streams) that needs an open-source rANS rather than proprietary nvCOMP ANS.
- ML tensors in bfloat16 or float16 whose exponents carry about 2.7 bits of entropy, giving roughly 0.67x (bfloat16) or 0.85x (float16) size per the README.
- Total inputs of at least about 512 KiB, ideally enough 4 KiB blocks to fill every SM; a batch size of 1 on large data performs best per the README.

## Skip it when

- Data whose redundancy lives above the byte level (text, structured records): byte-wise order-0 statistics compress it poorly; an LZ codec does better.
- Small buffers under about 512 KiB, or any CPU-only or non-NVIDIA deployment.
- Single arrays of 2 GiB or more: the ANS compressor fails a CHECK on rawSize &lt;= INT32_MAX (issue #19, closed as not planned).
- float32 or float64 tensors: the float codec supports only float16 and bfloat16 (float32 requests #11 and #15 never landed).
- Projects that need upstream support: the repository was archived on 2026-06-14 and was labelled a very early alpha.

## How it is fast

Input is split into 4 KiB blocks, each encoded by one warp as 32 interleaved rANS streams (one 31-bit state per lane, 16-bit renormalisation words). Lanes that need to emit or consume a word are compacted with __ballot_sync plus __popc on the lane mask, so a warp writes a dense output stream without serialising. Encoding replaces the division by pdf with constant multiply-and-shift (state is capped below 2^31 to avoid overflow), decoding uses a shared-memory lookup table packing cdf, pdf and symbol into one 32-bit word, and histogram, table build, encode and output coalescing all run on device with no host synchronisation when scratch memory is pre-sized.

## Compared with alternatives

Pick DietGPU over multians or Recoil when you need both a GPU encoder and decoder with per-array statistics (multians is decode-only), and over torch_ans when you want raw C++ device-pointer batches instead of PyTorch-only symbol tensors; for CPU entropy coding use hypersonic-rANS or htscodecs instead.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | CUDA toolkit, glog and googletest (git submodules); the top-level CMake also configures the PyTorch wrapper, so find_package(Torch) must succeed even if only gpu_ans is wanted |
| **Minimum toolchain** | CMake 3.10+, C++14 and CUDA C++14 (nvcc); a recent PyTorch build failed (issue #25, PyTorch 2.7.1+cu118) |
| **Platforms** | NVIDIA GPUs only; README says CC 3.5+ should work but only V100/A100 were tested by the author (a third-party paper reports runs on H100) |
| **Thread safety** | not documented; calls are stream-ordered and use a caller-owned StackDeviceMemory scratch object, so give each concurrent stream its own |
| **Drop-in for the baseline** | no |

## Gotchas

- Inputs must be 4-byte aligned (kANSRequiredAlignment = 4), and the output buffer must be sized with getMaxCompressedSize(), which is larger than the input.
- The compressed size is known only on the device; you copy the per-batch size array back to the host before you can move or trim the output.
- Only probability precisions of 9, 10 or 11 bits are accepted (default 10); any other value hits a CHECK failure.
- Decode trusts the stride you pass: a stride smaller than a member's compressed size can read out of bounds (header comment says it may segfault). The optional checksum is off by default.

## Known shortcomings

- Tier C: the README shows only its own 250-410 GB/s on an A100 with no baseline; the nvCOMP-ANS comparison (H100 592.5 decode / 364.9 encode vs 480 GB/s) is a snippet of arXiv 2606.18900, not opened. Archived 2026-06-14, abandoned.
- Archived 2026-06-14 with an alpha label. ANS CHECK fails for inputs over INT32_MAX (issue #19, closed not planned). Build needs PyTorch even for gpu_ans; PyTorch 2.7.1 build failure (issue #25). nvCOMP comparison request (issue #20) unanswered. Float codec handles fp16/bf16 only. An arXiv 2606.18900 snippet reports H100 decode 592.5 GB/s vs nvcomp-ANS 480 GB/s, a retier candidate once arXiv is reachable.

## Caveats and trade-offs

The README reports absolute throughput with no head-to-head baseline, so the 'faster than nvCOMP ANS' claim rests on a search-result snippet of a paper that could not be opened (arXiv blocked), and nvCOMP ANS is proprietary. Repository was archived by the owner on 2026-06-14 (read-only). Benchmarks use torch.normal-derived data, not real corpora. Tier D would apply if the paper claim is discounted; a verifier with arXiv access should open 2606.18900.

CUDA only, needs inputs of roughly 512 KiB or more to amortise overhead; per-array statistics; byte-wise symbols only; probability precision limited to 9, 10 or 11 bits. Python/PyTorch API plus a C++ raw-pointer API.

## Maintenance

Archived on 2026-06-14 after a last commit on 2026-03-18 and labelled an early alpha; MIT-licensed and small enough to vendor, but the build is tied to PyTorch and nobody fixes issues any more.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The README states first-party absolute throughput (ANS codec 250-410 GB/s on an A100, data from torch.normal) with no head-to-head baseline on the page. The only comparison against nvcomp-ANS is a third-party arXiv preprint (2606.18900) seen in a search snippet only, which cannot lift the tier above C without being opened.
- **Verifier notes:** README numbers match the record. A WebSearch snippet of arXiv 2606.18900 ('Compressed-Resident Genomics: Full-Pipeline Device-Resident GPU LZ77 Decode with Position-Invariant Random Access') repeats the H100 figures (364.9 GB/s encode, 592.5 GB/s decode, nvcomp-ANS measured at 480 GB/s), so the claim is corroborated but unopened (arXiv blocked); a retier to B is possible from an environment that reaches arXiv. Repo archived 2026-06-14, MIT, 396 stars, last commit 2026-03-18, so 'abandoned' is correct.
- **Shortcomings recorded by:** verifier; first-party benchmark
- **Pages the verifier opened:**
  - <https://github.com/facebookresearch/dietgpu>
  - <https://raw.githubusercontent.com/facebookresearch/dietgpu/HEAD/README.md>
  - <https://github.com/facebookresearch/dietgpu/commits>
- **Sources the enricher read:**
  - <https://github.com/facebookresearch/dietgpu>
  - <https://raw.githubusercontent.com/facebookresearch/dietgpu/HEAD/README.md>
  - <https://raw.githubusercontent.com/facebookresearch/dietgpu/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/facebookresearch/dietgpu/HEAD/dietgpu/CMakeLists.txt>
  - <https://raw.githubusercontent.com/facebookresearch/dietgpu/HEAD/dietgpu/ans/CMakeLists.txt>
  - <https://raw.githubusercontent.com/facebookresearch/dietgpu/HEAD/dietgpu/ans/GpuANSCodec.h>
  - <https://raw.githubusercontent.com/facebookresearch/dietgpu/HEAD/dietgpu/ans/GpuANSUtils.cuh>
  - <https://raw.githubusercontent.com/facebookresearch/dietgpu/HEAD/dietgpu/ans/GpuANSEncode.cuh>
  - <https://raw.githubusercontent.com/facebookresearch/dietgpu/HEAD/dietgpu/ans/GpuANSDecode.cuh>
  - <https://github.com/facebookresearch/dietgpu/issues?q=is%3Aissue>
  - <https://github.com/facebookresearch/dietgpu/issues/19>
  - <https://github.com/facebookresearch/dietgpu/issues/20>
  - <https://github.com/facebookresearch/dietgpu/issues/25>
  - WebSearch: dietgpu nvcomp ANS throughput H100 comparison GB/s (snippet of arXiv 2606.18900; the page itself is blocked here)
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/facebookresearch/dietgpu`) · [data/wave9/enrich/raw/github_com_facebookresearch_dietgpu.json](../../../data/wave9/enrich/raw/github_com_facebookresearch_dietgpu.json) (enrichment confidence 0.75)

</details>
