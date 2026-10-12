# cat-dog-asm-cnn

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Hand-written assembly kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Assembly (NASM x86-64, AVX-512)` · `MIT` · 🟢 active

> Educational cat/dog CNN, training and inference, hand-written in NASM AVX-512; claims \~10x over an unpublished NumPy CNN, slower than PyTorch.

| | |
|---|---|
| **Beats** | Equivalent NumPy-based CNN (and PyTorch, which it does not beat) |
| **Claimed result** | 'Approximately 10x faster performance than an equivalent NumPy-based CNN'; README says it does not reach PyTorch speed (an earlier, more specialized project is said to have exceeded PyTorch by about 1.4x). |
| **Workload** | Training/inference of a three-stage Conv2D+ReLU+MaxPool CNN with two dense layers on 25,000 128x128x3 cat/dog images (78% accuracy, same as the Python version). |
| **Metric** | throughput |
| **Hardware** | Not stated (container run with --cpus=4 --memory=4g; needs an AVX-512 CPU) |
| **Compiler and flags** | build.sh: nasm -f elf64 -g -F dwarf for each .asm file, linked with ld against libc and libm; no optimisation flags apply. The NumPy baseline's NumPy/BLAS versions are not stated. |
| **Adoption** | 181 stars |
| **Last commit** | 2026-02-08 |
| **Links** | [repository](https://github.com/mohammad-ghaderi/cat-dog-asm-cnn) · [benchmark](https://raw.githubusercontent.com/mohammad-ghaderi/cat-dog-asm-cnn/HEAD/README.md) |

## Verdict

The only performance statement is the README's 'approximately 10x faster than an equivalent NumPy-based CNN', for both training and inference. No timings, CPU, NumPy/BLAS version or NumPy code are published, so the ratio cannot be checked. The author also says it does not reach PyTorch speed. Reading the code confirms it is a single-threaded, per-sample, direct-convolution implementation that reaches the same 78% test accuracy as the author's Python version.

## Use it when

- Studying how a complete CNN forward and backward pass (conv, max-pool argmax masks, dense, BCE loss, SGD) maps onto AVX-512 instructions, in about 2,400 lines of commented NASM.
- Teaching or self-study of masked AVX-512 loads, k-mask logic and HWC layouts for convolution.
- A starting point for hand-writing a small fixed-shape conv kernel on an AVX-512 (F+BW+DQ) x86-64 Linux box, with the expectation of rewriting the inner loops.

## Skip it when

- Any production training or inference: PyTorch is faster by the author's own statement, and NumPy-based code is the only baseline it is claimed to beat.
- CPUs without AVX-512F/BW/DQ (most client Intel parts since Alder Lake, Zen 3 and earlier, Apple silicon): it uses vmovdqu8 and kmovd (BW) and vextractf32x8 (DQ) unconditionally, with no fallback.
- Reusing it as a kernel library: routines use ad-hoc register conventions (rbx and r12-r15 clobbered, inputs in rax/r14/k1) and global buffers, so they cannot be called from C/C++ without wrappers.
- Different shapes or datasets without editing assembly: image size, filter counts, the 19,998-train/5,000-test split and file paths are hard-coded.
- Workflows that need a trained model: _start never writes the learned weights out (write_floats exists only as a debug helper).

## How it is fast

Activations are stored channel-interleaved (HWC), so the three kernel rows of a 3x3 window are contiguous runs of 3\*C floats. Each row is loaded as masked 16-float ZMM chunks (9 lanes for the 3-channel first layer) and accumulated with vfmadd231ps. Dense layers are 16-wide FMA dot products, and max-pooling processes 16 channels per instruction, recording argmax as k-mask bitmaps. Every output scalar ends with a horizontal reduction (vextractf32x8, vextractf128, two haddps) and a call to relu. This is direct convolution with no im2col/GEMM, no register blocking across filters or pixels, no batching and no threads, which is consistent with the README's admission that it stays slower than PyTorch.

## Compared with alternatives

Pick it over CvsAssemblyBenchmark or FP-ASM only when you want a full end-to-end training loop (conv, pool, dense, backprop) to read; those siblings have measured, reproducible timings for their kernels, and this one has none. For real CNN inference on small targets, ESP-NN's measured int8 kernels are the catalogued option.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | NASM, GNU ld, glibc libc/libm (expf, logf); the dataset as raw files from the author's Google Drive links (no preprocessing script in the repo) and parameters/parameters.raw initial weights; Docker (debian:bookworm-slim) is the documented environment |
| **Minimum toolchain** | NASM (any version that assembles AVX-512; build.sh uses -f elf64 -g -F dwarf) plus ld with /lib64/ld-linux-x86-64.so.2 |
| **Platforms** | x86-64 Linux only (raw syscalls, ELF64), AVX-512F + AVX-512BW + AVX-512DQ required |
| **Thread safety** | Not thread-safe: single-threaded program, and all weights, activations and gradients live in global .bss buffers |
| **Drop-in for the baseline** | no |

## Gotchas

- No benchmark harness exists: the repo contains no timing code (no rdtsc, clock_gettime or time syscall), no NumPy reference, and no hardware or version notes. The \~10x figure was measured outside the repo. It was added to the README on 2026-02-08 (commit c775a12) without numbers.
- Silent failure on missing inputs: loader.asm and parameters.asm never check the return value of open() or read(). Running from the wrong directory, or without dataset/raw_files/\*.raw, leaves the buffers zero-filled and 'trains' on zeros. The program also needs about 1 GB of static .bss for the training images, plus about 35 MB of weights and gradients.
- Training visits samples in file order every epoch (no shuffling) and drops the last 14 of the 19,998 training images to fit whole batches of 16. The README's '25,000 images' is the train plus test total.
- The '1.4x faster than PyTorch' figure the README credits to the earlier mnist-asm-nn project is not in that project's own README, which instead claims about 7x over a NumPy implementation and does not mention PyTorch.

## Known shortcomings

- Bare 'about 10x vs NumPy' claim with no timings, hardware or NumPy code in the repo; slower than PyTorch (the 1.4x-over-PyTorch figure belongs to mnist-asm-nn).
- No timing code or NumPy reference exists in the repo; the '\~10x' was added to the README on 2026-02-08 (commit c775a12) with no numbers. The code reads correct (direct convolution, single thread, per sample); open() and read() are unchecked, so a missing dataset trains on zeros; no shuffling; weights are never saved; needs AVX-512F/BW/DQ. The '1.4x faster than PyTorch' credited to mnist-asm-nn is absent from that project's README (it claims about 7x over NumPy).

## Caveats and trade-offs

Only a bare '\~10x' ratio (README says it holds for both training and inference); no timings, epoch times, hardware, NumPy/BLAS versions or baseline code are given, and the repo contains no Python/NumPy implementation, so the figure cannot be checked. The author says it is slower than PyTorch; the 1.4x-over-PyTorch figure belongs to the earlier mnist-asm-nn project, not this one. Requires AVX-512; the Docker run uses --cpus=4 --memory=4g. Educational project (written with an academic advisor); accuracy 78%, same as the author's Python version.

Requires AVX-512; whole network in assembly makes changes costly; slower than PyTorch.

## Maintenance

A 2025-12 to 2026-02 educational project (last commit 2026-02-08, one open feature-idea issue). It is MIT-licensed and readable, but it is a fixed-shape training program rather than a reusable library, and its speed claim is first-party with no data behind it.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The README gives only a first-party '\~10x faster than an equivalent NumPy CNN' ratio with no timings, no NumPy code in the repo, no hardware and no methodology; that is a number without methodology, so C at best.
- **Verifier notes:** README matches the record; no benchmark artefacts exist in the repo (top level is .asm files, build.sh, Dockerfile, docs/, parameters/). Shortcoming: unverifiable 10x claim against an unpublished NumPy baseline, slower than PyTorch. MIT, 181 stars, 14 forks, last commit 2026-02-08 confirmed.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-31 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/mohammad-ghaderi/cat-dog-asm-cnn/HEAD/README.md>
  - <https://raw.githubusercontent.com/mohammad-ghaderi/cat-dog-asm-cnn/HEAD/build.sh>
  - <https://github.com/mohammad-ghaderi/cat-dog-asm-cnn>
  - <https://github.com/mohammad-ghaderi/cat-dog-asm-cnn/commits>
- **Sources the enricher read:**
  - <https://github.com/mohammad-ghaderi/cat-dog-asm-cnn>
  - <https://raw.githubusercontent.com/mohammad-ghaderi/cat-dog-asm-cnn/HEAD/README.md>
  - <https://raw.githubusercontent.com/mohammad-ghaderi/cat-dog-asm-cnn/HEAD/build.sh>
  - <https://raw.githubusercontent.com/mohammad-ghaderi/cat-dog-asm-cnn/HEAD/Dockerfile>
  - <https://raw.githubusercontent.com/mohammad-ghaderi/cat-dog-asm-cnn/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/mohammad-ghaderi/cat-dog-asm-cnn/HEAD/macros.inc>
  - <https://raw.githubusercontent.com/mohammad-ghaderi/cat-dog-asm-cnn/HEAD/_start.asm>
  - <https://raw.githubusercontent.com/mohammad-ghaderi/cat-dog-asm-cnn/HEAD/loader.asm>
  - <https://raw.githubusercontent.com/mohammad-ghaderi/cat-dog-asm-cnn/HEAD/buffer.asm>
  - <https://raw.githubusercontent.com/mohammad-ghaderi/cat-dog-asm-cnn/HEAD/parameters.asm>
  - <https://raw.githubusercontent.com/mohammad-ghaderi/cat-dog-asm-cnn/HEAD/padding.asm>
  - <https://raw.githubusercontent.com/mohammad-ghaderi/cat-dog-asm-cnn/HEAD/forward.asm>
  - <https://raw.githubusercontent.com/mohammad-ghaderi/cat-dog-asm-cnn/HEAD/convolution.asm>
  - <https://raw.githubusercontent.com/mohammad-ghaderi/cat-dog-asm-cnn/HEAD/maxpool.asm>
  - <https://raw.githubusercontent.com/mohammad-ghaderi/cat-dog-asm-cnn/HEAD/dense.asm>
  - <https://raw.githubusercontent.com/mohammad-ghaderi/cat-dog-asm-cnn/HEAD/dot_product.asm>
  - <https://raw.githubusercontent.com/mohammad-ghaderi/cat-dog-asm-cnn/HEAD/activation_functions.asm>
  - <https://raw.githubusercontent.com/mohammad-ghaderi/cat-dog-asm-cnn/HEAD/loss.asm>
  - <https://raw.githubusercontent.com/mohammad-ghaderi/cat-dog-asm-cnn/HEAD/backward.asm>
  - <https://raw.githubusercontent.com/mohammad-ghaderi/cat-dog-asm-cnn/HEAD/matrix_ops.asm>
  - <https://raw.githubusercontent.com/mohammad-ghaderi/cat-dog-asm-cnn/HEAD/update_weights.asm>
  - <https://raw.githubusercontent.com/mohammad-ghaderi/cat-dog-asm-cnn/HEAD/debug_tools.asm>
  - <https://raw.githubusercontent.com/mohammad-ghaderi/cat-dog-asm-cnn/HEAD/debug_buffer.asm>
  - <https://raw.githubusercontent.com/mohammad-ghaderi/cat-dog-asm-cnn/HEAD/print.asm>
  - <https://github.com/mohammad-ghaderi/cat-dog-asm-cnn/tree/main/parameters>
  - <https://github.com/mohammad-ghaderi/cat-dog-asm-cnn/commits/main>
  - <https://github.com/mohammad-ghaderi/cat-dog-asm-cnn/commit/c775a12>
  - <https://github.com/mohammad-ghaderi/cat-dog-asm-cnn/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/mohammad-ghaderi/mnist-asm-nn/HEAD/README.md>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/mohammad-ghaderi/cat-dog-asm-cnn`) · [data/wave13/enrich/raw/github_com_mohammad_ghaderi_cat_dog_asm_cnn.json](../../../data/wave13/enrich/raw/github_com_mohammad_ghaderi_cat_dog_asm_cnn.json) (enrichment confidence 0.6)

</details>
