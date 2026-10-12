# ZipNN (Huffman-based lossless compression of AI model weights)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [General-purpose lossless compression](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Python (C extension for Huffman)` · `MIT` · 🟢 active

> Lossless compressor for floating-point model weights; byte grouping plus Huffman beats plain zstd on bfloat16 speed and ratio.

| | |
|---|---|
| **Beats** | Zstandard (ZSTD v1.5.6, as written 'ZSTD v1.56' in the README table) |
| **Claimed result** | ZipNN v0.2.0 1120MB/s compression and 1660MB/s decompression at ratio 1.51 (66.3% output), versus ZSTD 785MB/s and 950MB/s at ratio 1.27 (78.3%); about 1.4x compress and 1.7x decompress speed (derived from page data). Multithreaded Xeon figure: up to 80GB/s decompression and 13GB/s compression with 16 workers. |
| **Workload** | Single-threaded compression and decompression of bfloat16 model weights in 256KB chunks: byte grouping then a C Huffman coder (the README says the bfloat16/float16 path is a C implementation with Huffman encoding), compared with plain ZSTD. |
| **Metric** | throughput |
| **Hardware** | Table: unstated. 80GB/s multithreaded figure: Intel Xeon Platinum 8480+ with 224 cores and two NUMA nodes. |
| **Compiler and flags** | setup.py builds the C extension with -O3 -Wall -Wextra (compiler unstated); flags for the README table run are not stated |
| **Adoption** | 337 stars, 39 forks; PyPI release 0.5.4 uploaded 2026-04-11 |
| **Last commit** | 2026-04-11 |
| **Links** | [repository](https://github.com/zipnn/zipnn) · [benchmark](https://github.com/zipnn/zipnn) |

## Verdict

The README table (single thread, 256 KB chunks, bfloat16 weights) gives ZipNN v0.2.0 1120 MB/s compress and 1660 MB/s decompress at ratio 1.51, against zstd (labelled 'v1.56', level and hardware unstated) at 785 and 950 MB/s and ratio 1.27, about 1.4x and 1.7x; the 80 GB/s decompression figure is 16 workers on a two-socket Xeon Platinum 8480+. No benchmark script, compiler or CPU is given for the single-thread table, and the measured version (0.2.0) predates the multithreaded C rewrite.

## Use it when

- Storing or shipping BF16/FP16/FP32/FP8 checkpoints where about 33% (BF16) or 17% (FP32) smaller files cut storage or download time
- Loading compressed safetensors into Hugging Face Transformers or vLLM on Linux x86-64 with spare CPU cores for multithreaded decompression
- Replacing zstd on raw weight tensors when you want both better ratio and higher single-thread throughput on that data
- Delta compression between two checkpoints of the same shape (XOR then compress), which the package supports

## Skip it when

- General data (text, logs, mixed binary): it has no LZ stage of its own for these; use zstd or lz4
- Windows with MSVC: issues 45 and 79 report the C extension failing there (79 worked around it with MinGW)
- Decompressing untrusted .znn files: the C decoder trusts the offsets and sizes in the input (see gotchas)
- C or C++ projects wanting a library: there is no C/C++ API; the core is a CPython extension module, so you would have to lift csrc/ and the FSE sources yourself
- Integer or already-quantised tensors other than FP8: uint32 is rejected in the current version

## How it is fast

Byte grouping: each 256 KB chunk is split into per-byte-position streams (high bytes holding the low-entropy exponent, low bytes holding near-random mantissa), after an optional bit reorder that moves the exponent into its own byte. Each stream is then coded with Huffman only (HUF_compress from Yann Collet's FiniteStateEntropy library, vendored as a git submodule), skipping LZ match finding that finds almost nothing in weights; streams that do not shrink below the threshold are stored raw. Chunks are processed in parallel by pthreads workers pulling from a mutex-protected counter.

## Compared with alternatives

Pick it over zstd or LZ4 only for floating-point model weights, where those reach about 1.27x and 1.0x ratio on BF16 versus ZipNN's 1.51x; Stenos (byte shuffle plus its own coder) is the closest catalogued alternative for typed numeric arrays in C++, and is the better fit if you need a C++ library rather than a Python package.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | numpy, torch (&gt;=2.0), safetensors; zstandard and lz4 Python packages for the non-Huffman methods; vendored FiniteStateEntropy (and zstd) git submodules for the C extension |
| **Minimum toolchain** | Python 3.6+ per setup.py; C compiler with pthreads and C99 VLAs (built with -O3) |
| **Platforms** | Linux x86-64 tested (README benchmark on Xeon Platinum 8480+); macOS not documented; Windows/MSVC broken per issues 45 and 79 |
| **Thread safety** | not documented; internally multithreaded (default min(cpu_count, 16) threads), and a ZipNN object keeps mutable header state between calls |
| **Drop-in for the baseline** | no |

## Gotchas

- compress() rewrites the caller's buffer in place: for float32 and bfloat16 the C code runs reorder_all_floats_dtype16/32 directly on the input (a torch tensor's storage via .numpy(), or even an immutable bytes object), and the project's own tests clone the tensor before compressing; copy your tensor first if you keep using it (per code reading, not run).
- The decoder (py_combine_dtype) reads chunk types and cumulative size_t offsets from the input without checking them against the buffer length, and sizes several stack VLAs by the chunk count from the header, so a crafted or truncated file can read out of bounds and a very large single buffer can exhaust the stack (per code reading).
- HUF_compress accepts at most 128 KB per call; FP8 is clamped to 128 KB chunks, but setting compression_chunk above 256 KB for 16-bit (or 512 KB for 32-bit) data makes every stream exceed that limit and fall back silently to raw storage (per code reading). split_bytearray_dtype16 also writes one byte past each output buffer when a 16-bit input has odd length.
- Memory leaks in the C extension were fixed only in v0.5.4 (issue 78, PR 77: about 608 MB growth over 100 iterations on 190 MB); earlier versions also had segfault/core-dump reports (issues 55, 75).

## Known shortcomings

- The Huffman coder is not ZipNN's own: it vendors Collet's FiniteStateEntropy HUF (huf_compress.c) and the speed win comes from byte grouping of bf16 weights. README table gives no CPU, compiler, zstd level or script. Paper (IEEE CLOUD 2025, arXiv 2411.05239) blocked here; possible B on a paper-access retier.
- Bugs found by reading code, not run: compress() changes the caller's buffer in place (reorder_all_floats_dtype16/32 runs on torch tensor storage or immutable bytes for bf16/fp32; the project's tests clone before compress). py_combine_dtype trusts chunk offsets in the input with no bounds check (a crafted .znn reads out of bounds); stack VLAs sized by chunk count. compression_chunk above 256 KB (16-bit) or 512 KB (32-bit) exceeds the 128 KB HUF_BLOCKSIZE_MAX and silently falls back to raw. Odd-length 16-bit input writes 1 byte past the heap buffer. C-extension leak fixed only in v0.5.4 (issue 78); segfault issues 55 and 75; Windows/MSVC broken (issues 45, 79). No C/C++ API, Python module only. setup.py omits zstandard although the README lists it.

## Caveats and trade-offs

First-party README table with no hardware, compiler, zstd level or benchmark script for the single-thread numbers; the table is for v0.2.0 (current 0.5.4) and labels zstd 'v1.56'. The C Huffman coder is not ZipNN's own: setup.py compiles Yann Collet's FiniteStateEntropy (huf_compress.c, huf_decompress.c, fse_\*.c vendored under include/FiniteStateEntropy) and csrc/zipnn_core.c calls HUF_compress/HUF_decompress, i.e. the same Huffman family zstd uses for literals. The win over zstd comes from byte grouping (separating bfloat16 exponent bytes) plus Huffman-only coding, so the entropy-coder contribution is not isolated; category fit for entropy-coders is weak (domain-specific lossless compressor for model weights). Default configuration is byte grouping of 4 with vanilla zstd; method 'auto' picks zstd, lz4 or huffman. The LICENSE.txt is MIT but its copyright line names IBM and 'the Drain3 project contributors' (boilerplate copied from another IBM project). Peer-reviewed paper (IEEE CLOUD 2025, arXiv 2411.05239) not opened: blocked here.

Only useful for floating-point model tensors (bfloat16, float16, float32, FP8); the speed and ratio win comes from byte grouping that separates the low-entropy exponent bytes, then Huffman, not from a faster general entropy coder. Python package with a C extension, so C++ use needs the C sources. Default configuration is ByteGrouping 4 with vanilla ZSTD.

## Maintenance

Active (v0.5.4 on PyPI, April 2026) and MIT-licensed, but it is a Python package with a C extension rather than a reusable C/C++ library, and its C code has unchecked-input and in-place-mutation hazards.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** README Results table (single-threaded, 256KB chunks, bfloat16) shows ZipNN v0.2.0 1120/1660 MB/s vs ZSTD 'v1.56' 785/950 MB/s, but gives no CPU model, compiler, flags, zstd level or benchmark script for those numbers, so first-party C. The authors' paper was accepted to IEEE CLOUD 2025 (WebSearch snippet only; arXiv, IEEE and the Dartmouth lab page are egress-blocked), which could support B on a later paper-access retier.
- **Verifier notes:** Numbers match README exactly; 1.4x/1.7x ratios check out (1120/785, 1660/950). Recommend a decision category override to general-lossless (baseline zstd, transform plus vendored FSE HUF), or keep in entropy-coders with the shortcoming recorded. Paper-access retier candidate (IEEE CLOUD 2025) for B.
- **Fields the verifier corrected:** `last_commit`, `stars_or_usage`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** first-party README table
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/zipnn/zipnn/HEAD/README.md>
  - <https://raw.githubusercontent.com/zipnn/zipnn/HEAD/LICENSE.txt>
  - <https://raw.githubusercontent.com/zipnn/zipnn/HEAD/setup.py>
  - <https://raw.githubusercontent.com/zipnn/zipnn/HEAD/csrc/zipnn_core.c>
  - <https://raw.githubusercontent.com/zipnn/zipnn/HEAD/csrc/data_manipulation_dtype16.c>
  - <https://github.com/zipnn/zipnn>
  - <https://github.com/zipnn/zipnn/commits>
  - <https://github.com/zipnn/zipnn/tree/main/csrc>
  - <https://pypi.org/pypi/zipnn/json>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/zipnn/zipnn/HEAD/README.md>
  - <https://raw.githubusercontent.com/zipnn/zipnn/HEAD/setup.py>
  - <https://raw.githubusercontent.com/zipnn/zipnn/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/zipnn/zipnn/HEAD/LICENSE.txt>
  - <https://raw.githubusercontent.com/zipnn/zipnn/HEAD/csrc/zipnn_core.c>
  - <https://raw.githubusercontent.com/zipnn/zipnn/HEAD/csrc/data_manipulation_dtype16.c>
  - <https://raw.githubusercontent.com/zipnn/zipnn/HEAD/csrc/data_manipulation_dtype32.c>
  - <https://raw.githubusercontent.com/zipnn/zipnn/HEAD/zipnn/zipnn.py>
  - <https://raw.githubusercontent.com/zipnn/zipnn/HEAD/tests/test_suit.py>
  - <https://raw.githubusercontent.com/zipnn/zipnn/HEAD/tests/simple_stress_tests.py>
  - <https://raw.githubusercontent.com/Cyan4973/FiniteStateEntropy/HEAD/lib/huf.h>
  - <https://github.com/zipnn/zipnn/issues?q=is%3Aissue>
  - <https://github.com/zipnn/zipnn/issues/55>
  - <https://github.com/zipnn/zipnn/issues/78>
  - <https://github.com/zipnn/zipnn/issues/79>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/zipnn/zipnn`) · [data/wave9/enrich/raw/github_com_zipnn_zipnn.json](../../../data/wave9/enrich/raw/github_com_zipnn_zipnn.json) (enrichment confidence 0.75)

</details>
