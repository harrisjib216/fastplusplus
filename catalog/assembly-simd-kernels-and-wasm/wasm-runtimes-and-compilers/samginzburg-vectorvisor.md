# VectorVisor (GPU binary translator for WebAssembly)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly runtimes and compilers](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Rust` · `Apache-2.0` · 🟡 stale

> Binary translator that runs thousands of copies of a single-threaded Wasm program on an OpenCL GPU; per dollar it beats native x86 CPU VMs only on some compute-bound workloads.

| | |
|---|---|
| **Beats** | Same Wasm modules on CPU with Wasmtime embedded in VectorVisor (--wasmtime=true) and native x86-64 Rust builds (cargo run --release --target x86_64-unknown-linux-gnu), on 4-vCPU AWS c5.xlarge (Intel) or c5a.xlarge (AMD) instances; hand-written CUDA versions (cuda-blockhash, cuda-blur) on the GPU for imagehash and imageblur. |
| **Claimed result** | USENIX ATC 2023 abstract: throughput-per-dollar up to 2.9x compared with Intel x86-64 VMs for certain compute-bound workloads. From the paper's raw data (benchmarks/2022-12-22-20:09:12, derived from page data): the 2.9x is Pbkdf2 on a T4 (2.93x) or A10G (2.94x) against native Rust on an Intel c5.xlarge; the same native Pbkdf2 binary on the AMD c5a.xlarge ran 1233.4 vs 149.3 RPS (8.3x faster, likely SHA-NI via the pinned sha2 0.9.3), against which the GPU gets 0.32x per dollar. Excluding Pbkdf2 the best row is 2.14x vs Intel and 1.79x vs the better CPU; the GPU beats the better native CPU on 4 of 10 benchmarks and loses on 6 (LZ4 0.08-0.15x). |
| **Workload** | Serverless-style benchmarks (scrypt, pbkdf2, imageblur, imagehash, genpdf, lz4 compression, nlp, average) run as thousands of concurrent Wasm instances on a GPU versus CPU instances. |
| **Metric** | throughput |
| **Hardware** | GPU side: AWS g4dn.xlarge (1 NVIDIA T4, 4 vCPU), g5.xlarge (1 NVIDIA A10G, 4 vCPU) or g4ad.xlarge (AMD Radeon Pro V520); CPU baseline: AWS c5.xlarge (Intel) or c5a.xlarge (AMD); load generator c5a.8xlarge, all in us-east-1b (benchmarks/run_benchmarks_aws.py). Exact CPU models not named on the pages opened. |
| **Compiler and flags** | cargo build --release; benchmark Wasm built in optimized and interleaved variants (scrypt-opt-\*.wasm) |
| **Adoption** | 160 stars |
| **Last commit** | 2024-09-26 |
| **Links** | [repository](https://github.com/SamGinzburg/VectorVisor) · [benchmark](https://raw.githubusercontent.com/SamGinzburg/VectorVisor/HEAD/benchmarks/run_benchmarks_aws.py) |

## Verdict

The paper's own data (benchmarks/2022-12-22-20:09:12, one 600 s run per configuration, AWS us-east-1b, rust 1.66 builds, prices \$0.526 T4 g4dn.xlarge, \$1.006 A10G g5.xlarge, \$0.3785 V520 g4ad.xlarge, \$0.154 c5a.xlarge, \$0.17 c5.xlarge) shows VectorVisor beating the better native x86 4-vCPU VM on throughput per dollar on 4 of 10 benchmarks: Scrypt 1.55-1.79x, PHash-Mod 1.37-1.65x, Blur-Bmp 1.02-1.60x and Bill-PDF 1.31x on T4. It loses on the other 6, down to 0.08x on LZ4 (derived from page data). The abstract's 2.9x is Pbkdf2 against the Intel c5.xlarge only, a VM on which native Pbkdf2 ran 8.3x slower than on the AMD c5a.xlarge.

## Use it when

- Many independent, identical, compute-bound requests (password hashing such as scrypt, image blur or perceptual hash on raw BMP input) that already compile to single-threaded Wasm
- You already rent NVIDIA GPU instances (T4, A10G, V100 and desktop RTX cards are listed as fully supported) and want to raise their utilisation without writing CUDA
- Research or prototyping of GPU offload for serverless functions written in Rust, Go (via Asyncify) or AssemblyScript
- Throughput per dollar matters more than per-request latency, and each instance fits the fixed per-VM budget readme.md describes (3-4 MiB heap, 128 KiB stack, 128-512 KiB hypercall buffer), with VM count bounded by GPU memory

## Skip it when

- Memory- or I/O-heavy workloads: in the paper's own data the GPU loses on throughput per dollar to a native x86 CPU VM on LZ4 (0.08-0.15x), Histogram (0.30-0.47x), Strings-Rust (0.27-0.37x), Blur-Jpeg (0.11-0.57x) and unmodified PHash (0.37-0.62x)
- Latency-sensitive services: requests are batched across thousands of VMs, and readme.md says the approach is 'less efficient than manual translation'
- Multi-threaded guests or VMs that must talk to each other: only single-threaded Wasm is supported and the maintainer says there is no inter-VM communication or synchronisation (issue #4)
- AMD or Intel GPUs: the AMD Radeon Pro V520 'sometimes crash[es]', Intel GPUs fail beyond smoke tests, Windows is unevaluated
- Production use: research artifact, last commit 2024-09-26, build breaks on Rust 1.76 (issue #5) and is pinned to 1.74.0

## How it is fast

Throughput comes from SIMT batching: thousands of identical Wasm instances run as GPU work-items, so a throughput-bound serverless workload (hashing, image filters) uses the GPU's thread count instead of 4 vCPUs. The translator adds memory interleaving (the --interleave 4/8 layouts) so that lockstep VMs make coalesced accesses, partitions functions into kernels, and supports profile-guided optimization through a separate vv-pgo-instrument tool plus wasm-opt -O3. The gain is economic (requests per second per dollar of a GPU instance), not lower latency.

## Compared with alternatives

The siblings DTVM, wasman, KinoWASM, WasmKit and Cage are CPU Wasm engines that cut startup or per-call latency. Pick VectorVisor only when you have many identical compute-bound requests and an idle NVIDIA GPU to fill; for any single request, or for memory-bound code, a CPU runtime (or native code) is faster and cheaper.

## Integration

| | |
|---|---|
| **Form** | standalone binary (Rust server built with cargo build --release); guest programs link the bundled wasm-serverless-invoke crate |
| **Dependencies** | OpenCL 1.2+ runtime, GPU driver and OpenCL headers; crates include wasmtime 1.0.0, wasmtime-wasi 1.0.0, ocl 0.19, tokio, warp; the benchmark pipeline also needs binaryen version_109 (wasm-opt), the author's wasm-snip fork and vv-pgo-instrument |
| **Minimum toolchain** | rust-toolchain pins Rust 1.74.0 (1.76.0 fails to compile cap-primitives, issue #5); the evaluation AMIs used Rust 1.66, Ubuntu 18.04, CUDA 12 with NVIDIA driver 525 |
| **Platforms** | Linux host with an OpenCL 1.2 GPU; full support on NVIDIA GTX 1080 Ti, RTX 2080 Ti, RTX 3080 Ti, T4, A10G, V100; partial on AMD Radeon Pro V520 (needs --nvidia=false --patch=true) and Intel Iris Pro (macOS); Windows not evaluated (TDR must be disabled) |
| **Thread safety** | not documented; guests must be single-threaded Wasm and VMs share no state |
| **Drop-in for the baseline** | partial — the same .wasm file runs, but it must use the wasm-serverless-invoke request interface, fit fixed heap, stack and hypercall-buffer sizes, and be driven by batched HTTP requests instead of a Wasmtime embedding API |

## Gotchas

- Headline harness finding: the abstract's 'up to 2.9x throughput-per-dollar compared with Intel x86-64 VMs' matches only Pbkdf2 against the Intel c5.xlarge native run (T4 2.93x, A10G 2.94x, derived from page data in benchmarks/2022-12-22-20:09:12). The same native Pbkdf2 binary on the AMD c5a.xlarge in the same dataset ran 1233.4 RPS versus 149.3 RPS on Intel (8.3x). Against that AMD VM the GPU gets 0.32x the throughput per dollar. The benchmark's lockfile pins sha2 0.9.3, whose x86 SHA-256 backend switches to SHA-extension intrinsics at run time when cpuid reports 'sha'. So the 8.3x gap is most likely SHA-NI present on the c5a's AMD CPU and absent on the c5's Intel CPU (inference). Excluding Pbkdf2, the best per-dollar result against the Intel VM is 2.14x (T4, PHash-Mod), and against the better of the two CPU VMs it is 1.79x (A10G, Scrypt).
- The GPU-favourable rows are partly GPU-tailored variants. Blur-Bmp wins (1.02-1.60x per dollar against the best CPU) while Blur-Jpeg loses (0.11-0.57x). PHash-Mod wins (1.37-1.65x) while unmodified PHash loses (0.37-0.62x). Each GPU figure is the best of up to four configurations (interleave 4 or 8, with or without PGO); each CPU figure is the best of two VMs. Every configuration ran once (NUM_REPEAT=1, 600 s), so there is no variance data. The GPU invoker waited 1200 s for OpenCL compilation before it started measuring.
- The CPU 'WASM' column comes from VectorVisor's embedded Wasmtime 1.0.0 with 4096 VMs on 4 vCPUs. It ran 2.6x to 26x slower than native (for example, Scrypt 5.3 against 33.9 RPS). Large ratios against that column therefore overstate the gain over a normal Wasm runtime; compare against the native x86 rows. The hand-written CUDA baselines were host-bound: g4dn.2xlarge, with twice the vCPUs, nearly doubled CUDA blur from 576 to 1119 RPS on the same T4. The 'matches CUDA' result therefore compares against an under-provisioned CUDA server.
- In the current run_benchmarks_aws.py, the native-x86 imagehash result is written only inside 'if run_modified:'. A fresh rerun therefore produces no cpu_x86_bench_imagehash_0.txt, and make_figures.py would silently normalise PHash against Strings-Rust x86 instead. The published dataset does contain the file. Separately, running with --partition=false also requires --maxdup=0; otherwise the generated OpenCL fails with function 'redefinition' errors (issue #2).

## Known shortcomings

- Up to 2.9x throughput per dollar vs Intel x86-64 VMs on compute-bound workloads only (abstract snippet; usenix.org and cs.princeton.edu blocked); repo pages have no numbers; baseline rows include native x86 and CUDA (c5.xlarge/c5a.xlarge vs g4dn/g5/g4ad).
- Harness flaw in the paper's data (benchmarks/2022-12-22-20:09:12): the abstract's 'up to 2.9x' throughput per dollar is Pbkdf2 against the Intel c5.xlarge native run only (T4 2.93x, A10G 2.94x, derived from page data); the same native Pbkdf2 binary on the AMD c5a.xlarge in the same dataset ran 1233.4 vs 149.3 RPS (8.3x, likely SHA-NI via the pinned sha2 0.9.3, inference), and against that VM the GPU gets 0.32x per dollar. Excluding Pbkdf2 the best is 2.14x vs Intel and 1.79x vs the better CPU; it beats the better native CPU on 4 of 10 benchmarks and loses 6 (LZ4 0.08-0.15x); winning rows are partly GPU-tailored variants (Blur-Bmp, PHash-Mod); NUM_REPEAT = 1; the GPU side is the best of 4 configurations; the CPU WASM baseline (embedded wasmtime 1.0.0) runs 2.6-26x slower than native; the CUDA baseline is host-bound; a rerun bug saves the x86 imagehash result only under run_modified.

## Caveats and trade-offs

Headline metric is throughput per dollar of a GPU instance versus a 4-vCPU CPU instance, not raw throughput or latency, and the 2.9x applies only to some compute-bound workloads (search snippet of the abstract; paper at https://www.usenix.org/conference/atc23/presentation/ginzburg not reachable here). The repo holds figures (latency_throughput.png, latency_breakdown.png), make_figures.py and raw result directories (2022-12-22-20:09:12 is the paper's data per benchmarks/README.md) but no text summary of results. The Wasmtime CPU baseline is VectorVisor's embedded --wasmtime mode with a pinned wasmtime version, not the standalone CLI. readme.md admits it is less efficient than manual GPU translation; AMD V520 support is partial and sometimes crashes. benchmarks/README.md says the end-to-end evaluation takes about 24 hours on AWS. Last commit 2024-09-26 (stale). [retier] Headline metric is throughput per dollar of a GPU instance versus a 4-vCPU CPU instance, not raw throughput or latency, and the 2.9x applies only to Pbkdf2 against the slower of the two CPU VMs in the paper's own dataset. The GPU-favourable rows are partly GPU-tailored variants (Blur-Bmp wins while Blur-Jpeg loses; PHash-Mod wins while unmodified PHash loses); each GPU figure is the best of up to four configurations (interleave 4 or 8, with or without PGO) and each CPU figure the best of two VMs; every configuration ran once (NUM_REPEAT = 1, 600 s), so there is no variance data. The CPU 'WASM' column comes from VectorVisor's embedded Wasmtime 1.0.0 with 4096 VMs on 4 vCPUs and ran 2.6-26x slower than native, so ratios against it overstate the gain over a normal Wasm runtime; the hand-written CUDA baselines were host-bound (g4dn.2xlarge with twice the vCPUs nearly doubled CUDA blur on the same T4). In the current run_benchmarks_aws.py the native-x86 imagehash result is written only inside 'if run_modified:', so a fresh rerun silently normalises PHash against the wrong row; --partition=false also requires --maxdup=0. The paper PDF itself was unreachable (usenix.org and the Princeton PDF); readme.md says the approach is 'less efficient than manual translation'.

Needs an OpenCL 1.2+ GPU; best on NVIDIA under Linux, AMD ROCm sometimes crashes and Intel fails beyond smoke tests; workloads must be throughput-oriented (many independent requests), single-threaded Wasm, with fixed heap and stack sizes; latency per request is higher than on CPU.

## Maintenance

Stale research artifact (last commit 2024-09-26, Apache-2.0, 5 closed issues) that builds only with Rust 1.74 and needs about 24 hours of AWS time to reproduce. It is usable for experiments on NVIDIA GPUs, but its headline 2.9x rests on an Intel CPU baseline that lacks the SHA extensions the AMD baseline used, and against the AMD VM the GPU loses on that benchmark.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed USENIX ATC 2023 paper whose abstract (search snippet only) reports up to 2.9x throughput-per-dollar versus Intel x86-64 cloud VMs; the public artifact (benchmarks/run_benchmarks_aws.py, make_figures.py, raw results in benchmarks/2022-12-22-20:09:12) runs the same Wasm on CPU via Wasmtime and natively. Not A: CPU models and Wasm build flags are not stated on opened pages and the paper itself could not be opened.
- **Verifier notes:** Record is accurate on metadata (Apache-2.0, 160 stars, last commit 2024-09-26, stale); baseline extended to the native x86 and CUDA rows the harness also runs. Only the abstract figure (2.9x throughput-per-dollar, snippet only) is available; a paper-access retier should extract per-benchmark ratios. Shortcoming: dollar-normalized metric, gains limited to compute-bound workloads.
- **Fields the verifier corrected:** `claimed_speedup`, `baseline`, `hardware`, `caveats`
- **Shortcomings recorded by:** verifier batch-16 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/SamGinzburg/VectorVisor/HEAD/benchmarks/run_benchmarks_aws.py>
  - <https://raw.githubusercontent.com/SamGinzburg/VectorVisor/HEAD/readme.md>
  - <https://github.com/SamGinzburg/VectorVisor>
  - <https://github.com/SamGinzburg/VectorVisor/commits>
  - <https://github.com/SamGinzburg/VectorVisor/tree/master/benchmarks>
  - <https://github.com/SamGinzburg/VectorVisor/tree/master/benchmarks/2022-12-22-20:09:12>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/SamGinzburg/VectorVisor/HEAD/readme.md>
  - <https://raw.githubusercontent.com/SamGinzburg/VectorVisor/HEAD/benchmarks/README.md>
  - <https://raw.githubusercontent.com/SamGinzburg/VectorVisor/HEAD/benchmarks/run_benchmarks_aws.py>
  - <https://raw.githubusercontent.com/SamGinzburg/VectorVisor/HEAD/benchmarks/make_figures.py>
  - <https://raw.githubusercontent.com/SamGinzburg/VectorVisor/HEAD/benchmarks/run_all.sh>
  - <https://raw.githubusercontent.com/SamGinzburg/VectorVisor/HEAD/benchmarks/run_all_nvidia.sh>
  - <https://raw.githubusercontent.com/SamGinzburg/VectorVisor/HEAD/benchmarks/make_image.py>
  - <https://raw.githubusercontent.com/SamGinzburg/VectorVisor/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/SamGinzburg/VectorVisor/HEAD/rust-toolchain>
  - <https://raw.githubusercontent.com/SamGinzburg/VectorVisor/HEAD/benchmarks/pbkdf2/Cargo.toml>
  - <https://raw.githubusercontent.com/SamGinzburg/VectorVisor/HEAD/benchmarks/pbkdf2/Cargo.lock>
  - <https://raw.githubusercontent.com/SamGinzburg/VectorVisor/HEAD/benchmarks/pbkdf2/src/main.rs>
  - <https://raw.githubusercontent.com/SamGinzburg/VectorVisor/HEAD/benchmarks/pbkdf2/run_pbkdf2.go>
  - <https://raw.githubusercontent.com/SamGinzburg/VectorVisor/HEAD/benchmarks/scrypt/Cargo.toml>
  - <https://github.com/SamGinzburg/VectorVisor/tree/master/benchmarks/2022-12-22-20:09:12>
  - <https://github.com/SamGinzburg/VectorVisor/tree/master/benchmarks/2022-12-22-20:09:12/t4_amd_4>
  - https://raw.githubusercontent.com/SamGinzburg/VectorVisor/HEAD/benchmarks/2022-12-22-20:09:12/t4_amd_4/ (gpu_bench_\*, cpu_bench_\*, cpu_x86_bench_\* for scrypt, pbkdf2, imageblur, imageblur_bmp, imagehash, imagehash_modified, genpdf, average, lz4, nlp)
  - https://raw.githubusercontent.com/SamGinzburg/VectorVisor/HEAD/benchmarks/2022-12-22-20:09:12/t4_amd_8/ (same file set)
  - <https://raw.githubusercontent.com/SamGinzburg/VectorVisor/HEAD/benchmarks/2022-12-22-20:09:12/{t4_amd_4_profile,t4_amd_8_profile,a10g_intel_4,a10g_intel_8,a10g_intel_4_profile,a10g_intel_8_profile,v520_4_profile,v520_8_profile}/gpu_bench_*_0.txt>
  - <https://raw.githubusercontent.com/SamGinzburg/VectorVisor/HEAD/benchmarks/2022-12-22-20:09:12/{t4_cuda,t4_cuda_2x,a10g_cuda,a10g_cuda_2x}/gpu_cuda_bench_*_0.txt>
  - <https://github.com/SamGinzburg/VectorVisor/issues?q=is%3Aissue>
  - <https://github.com/SamGinzburg/VectorVisor/issues/2>
  - <https://github.com/SamGinzburg/VectorVisor/issues/4>
  - <https://github.com/SamGinzburg/VectorVisor/issues/5>
  - https://crates.io/api/v1/crates/sha2/0.9.3/download (CHANGELOG.md, src/sha256.rs, src/sha256/x86.rs)
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/samginzburg/vectorvisor`) · [data/wave13/enrich/raw/github_com_samginzburg_vectorvisor.json](../../../data/wave13/enrich/raw/github_com_samginzburg_vectorvisor.json) (enrichment confidence 0.6)

</details>
