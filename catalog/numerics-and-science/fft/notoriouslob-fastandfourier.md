# FastAndFourier (FAF, JIT-compiled DSP/FFT library)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [FFT](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟢 active

> C11 DSP library (FFT, DCT/DST, DWT, CWT, STFT) with IR interpreter plus runtime gcc JIT; beats KissFFT only at some sizes.

| | |
|---|---|
| **Beats** | KissFFT (and FFTW3 FFTW_ESTIMATE/FFTW_MEASURE, which beat it); also NotoriousFFT |
| **Claimed result** | x86_64 macOS, 2.3 GHz AVX2: at N=65536 907 us vs KissFFT 3253 us (README: 3.2-3.6x faster; 3.6x derived from page data) but slower at N=64 (4.40 vs 1.11 us), 1024 (75.3 vs 27.1 us) and 16384 (1595 vs 634 us); FFTW3 measure is 3-10x faster than everything. Linux aarch64 6 x 1.73 GHz: 53.8 ns vs 95.3 ns at N=8, 0.778 vs 0.850 at N=64, 16.5 vs 21.7 at N=1024, 2238 vs 2735 at N=65536 (slightly slower at N=16: 0.161 vs 0.149). |
| **Workload** | Single-transform C2C latency in double precision at N=8 to 65536, first on macOS x86_64 (2026-02-22) and then Linux aarch64 interleaved FP64 (2026-09-03). |
| **Metric** | latency |
| **Hardware** | x86_64 macOS Ventura (Darwin 22.6.0), 16 x 2300 MHz, AVX2, no AVX-512, L3 16 MiB; Linux aarch64 6 x 1728 MHz, L1 64 KiB, L2 256 KiB x 6, L3 2 MiB, CPU frequency scaling on. CPU models not named. |
| **Compiler and flags** | x86 run: Release build -O3 -march=native -ffast-math, FP64 for all libraries (README and benchmarks/README.md; the README says Release builds also add -funroll-loops). aarch64 run: Release -O3 -march=native. Compiler name and version not stated. |
| **Adoption** | 0 stars |
| **Last commit** | 2026-09-25 |
| **Links** | [repository](https://github.com/NotoriousLOB/FastAndFourier) · [benchmark](https://raw.githubusercontent.com/NotoriousLOB/FastAndFourier/HEAD/README.md) |

## Verdict

First-party Google Benchmark runs, double-precision C2C: on an unnamed 2.3 GHz AVX2 x86_64 Mac (macOS Ventura, -O3 -march=native -ffast-math, 2026-02-22) FAF beat KissFFT only at N = 65,536 (907 vs 3,253 us, about 3.6x) and lost 2.5-4x at N = 64-16,384, with FFTW3 measure fastest everywhere; on an unnamed 6-core 1.73 GHz aarch64 Linux box (-O3 -march=native, frequency scaling on, 2026-09-03) it beat KissFFT by \~1.1-1.8x at N = 8 and N &gt;= 32 and lost slightly at N = 16. Compiler names and CPU models are not stated.

## Use it when

- You want a scriptable or config-driven DSP chain (filter banks, wavelet denoisers, matched filters) where FFT, DWT, CWT and STFT share one API and can be fused, more than raw FFT speed.
- Replacing KissFFT on AArch64 for double-precision C2C at N = 8 or N &gt;= 32 (author's run: 16.5 vs 21.7 us at N = 1024, 2238 vs 2735 us at N = 65536, \~1.1-1.8x).
- Large power-of-two transforms on x86 AVX2 where the JIT engages (author's Feb 2026 run: 907 vs 3253 us at N = 65536).
- Embedding into C projects that can tolerate a runtime C compiler, or builds with FASTANDFOURIER_SINGLE_HEADER=ON to stay VM-only.

## Skip it when

- Raw FFT speed: the README itself says FFTW3 FFTW_MEASURE wins at nearly every size (3-10x ahead on its x86 table), and the same author's Notorious-FFT is 1.2-2.15x faster than FAF on aarch64.
- Small and mid sizes on x86: the published x86 table has FAF 2.5-4x slower than KissFFT from N = 64 to 16,384 (e.g. 75.3 vs 27.1 us at N = 1024); it predates the 1.1 codelets and has not been re-run.
- Hardened, multi-user or sandboxed processes: the JIT writes generated C and .so files to predictable names in /tmp (faf_jit_&lt;pid&gt;_&lt;counter&gt;), shells out to gcc with system(), and dlopen()s the result and any jit_&lt;hash&gt;.so found in \$HOME/.cache/fastandfourier without integrity checks.
- Transforms longer than 2^16 points (the VM register file is sized for N &lt;= 65,536) or non-5-smooth lengths without opting into Bluestein (RFFT and DWT refuse it).
- Production dependencies needing maturity: 0 stars, no tagged releases on the repo page, and benchmark tables with internal inconsistencies.

## How it is fast

Transforms are lowered to a 34-opcode IR that either runs on a direct-threaded interpreter (VM) or is emitted as C with AVX2/AVX-512/NEON intrinsics, compiled at runtime by invoking gcc through system(), and dlopen'ed; the AUTO backend switches to the JIT at N &gt;= 128. Version 1.1 added hard-coded split-plane codelets for N = 2-12, recursive split-radix DIF for powers of two &gt;= 16, radix-2/3/4/5 mixed radix for 5-smooth sizes, Rader for primes with 7-smooth N-1, and optional Bluestein. Fused R2C -&gt; pointwise -&gt; C2R pipelines run as one generated kernel.

## Compared with alternatives

For plain FFTs prefer Notorious-FFT (same author, faster on aarch64), PocketFFT or PFFFT, which beat KissFFT more consistently without a runtime compiler; pick FastAndFourier only when you need its breadth (DCT/DST, DWT, CWT/CQT, STFT, MDCT) behind one API and the Chirp scripting/fusion layer, and can accept the JIT's runtime-compiler and /tmp file model.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | none at build time beyond libm, libdl and pthread on Linux; a system gcc at runtime for the JIT (otherwise VM only); tests and benchmarks fetch Google Test and Google Benchmark |
| **Minimum toolchain** | CMake 3.18+, C11 compiler (C++17 only for tests) |
| **Platforms** | x86-64 (SSE4.2/AVX2/AVX-512) and AArch64 (NEON/SVE) on Linux, macOS and Windows per README; CUDA backend experimental |
| **Thread safety** | faf_execute_jit_cached is documented thread-safe for concurrent first calls (compare-and-swap pins the kernel to the transform); error messages are thread-local; other guarantees not documented |
| **Drop-in for the baseline** | no |

## Gotchas

- Release builds compile the library with -O3 -march=native -ffast-math -funroll-loops, and the JIT also compiles kernels with -ffast-math and -march=native (or -march=armv8.2-a+fp16 on AArch64 with the SIMD flag), so binaries and cached kernels are not portable to older CPUs and IEEE NaN/Inf semantics are not guaranteed.
- The disk cache key is an FNV-1a hash of the IR, size, precision and flags only, not of the library version, compiler or CPU; a stale or foreign jit_&lt;hash&gt;.so in \$HOME/.cache/fastandfourier is loaded as-is. faf_jit_destroy also unlinks ctx-&gt;so_path, which after a cache hit is the cached file itself, so the cache entry is deleted after it is reused.
- The first JIT execution of each transform pays a full gcc invocation; non-power-of-two sizes and kernels that bake process pointers (FFT_STAGE, pipelines) are never disk-cached, so every process recompiles them.
- Benchmarks drive the interleaved faf_execute_f64 path, which the README calls the slower convenience path; split-plane buffers are the fast path and require explicit faf_deinterleave/faf_interleave conversion.

## Known shortcomings

- Benchmark README contradicts itself (two x86 tables disagree; a February run 'pinned' to the August v1.0.1); beats KissFFT on x86 only at N=65536.
- Security: the JIT writes .c/.so files to predictable /tmp/faf_jit_&lt;pid&gt;_&lt;n&gt; paths, runs gcc via system() and dlopens the result, and dlopens \~/.cache/fastandfourier/jit_&lt;hash&gt;.so with no integrity check (hash ignores library version, compiler and CPU); bug: faf_jit_destroy unlinks the cached .so after a cache hit; built with -ffast-math -march=native; benchmarks drive the slower interleaved path; x86 table predates v1.1.

## Caveats and trade-offs

The README says FFTW3 FFTW_MEASURE wins at nearly every size and that small N was not its race on x86. On x86 the win over KissFFT appears only at N=65536 (907 vs 3253 us); FAF is 2.5-4x slower than KissFFT from N=64 to 16384 (derived from page data). On aarch64 it beats KissFFT at N=8 and from N=32 upward but loses at N=16. The benchmarks README is inconsistent: its two x86 small-N tables disagree (N=16 FAF 1.72 us vs 1330 ns, KissFFT 0.210 us vs 72.6 ns); the 2026-02-22 run claims NotoriousFFT pinned to v1.0.1, a release made in August 2026; and the 'FAF vs FFTW3 3.01x' cell at N=65536 is FAF being 3x slower. The x86 run used -ffast-math. The aarch64 run had frequency scaling on. NotoriousFFT, by the same author, is 1.2-2.15x faster than FAF on aarch64. It is a separate JIT/VM codebase, not a duplicate of Notorious-FFT.

Runtime JIT: transforms are lowered to C and compiled by a system C compiler (falls back to a VM interpreter without one). Sizes up to 2^16, 5-smooth sizes plus codelets and Rader primes, optional Bluestein. Part of a larger DSP library with a scripting language, DWT and CWT.

## Maintenance

Actively developed by a single author (last commit 2026-09-25, v1.2.0 commit on 2026-09-04) and MIT-licensed, but young, unstarred and with a security-sensitive JIT design, so treat it as experimental.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party Google Benchmark harness (benchmarks/) with tables in the README and benchmarks/README.md against KissFFT and FFTW3. Flags are given, but no compiler name and no CPU model on either machine (only '16 x 2300 MHz x86_64 AVX2' and 'aarch64 6 x 1728 MHz'), so C.
- **Verifier notes:** All claimed numbers are on the README and benchmarks/README.md; MIT, 0 stars, last commit 2026-09-25 confirmed. Not a duplicate of Notorious-FFT (different engine, same author), but a weak entry: a win only at 65536 on x86 and modest wins on aarch64, with internal table inconsistencies.
- **Fields the verifier corrected:** `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/NotoriousLOB/FastAndFourier/HEAD/README.md>
  - <https://raw.githubusercontent.com/NotoriousLOB/FastAndFourier/HEAD/benchmarks/README.md>
  - <https://github.com/NotoriousLOB/FastAndFourier>
  - <https://github.com/NotoriousLOB/FastAndFourier/commits>
- **Sources the enricher read:**
  - <https://github.com/NotoriousLOB/FastAndFourier>
  - <https://github.com/NotoriousLOB/FastAndFourier/commits/master>
  - <https://github.com/NotoriousLOB/FastAndFourier/tree/master/src/jit>
  - <https://github.com/NotoriousLOB/FastAndFourier/tree/master/benchmarks>
  - <https://raw.githubusercontent.com/NotoriousLOB/FastAndFourier/HEAD/README.md>
  - <https://raw.githubusercontent.com/NotoriousLOB/FastAndFourier/HEAD/benchmarks/README.md>
  - <https://raw.githubusercontent.com/NotoriousLOB/FastAndFourier/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/NotoriousLOB/FastAndFourier/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/NotoriousLOB/FastAndFourier/HEAD/src/jit/faf_jit.c>
  - <https://raw.githubusercontent.com/NotoriousLOB/FastAndFourier/HEAD/include/fastandfourier.h>
  - <https://raw.githubusercontent.com/NotoriousLOB/FastAndFourier/HEAD/benchmarks/benchmark_comparison.cpp>
  - <https://raw.githubusercontent.com/NotoriousLOB/FastAndFourier/HEAD/benchmarks/bench_util.h>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/notoriouslob/fastandfourier`) · [data/wave8/enrich/raw/github_com_notoriouslob_fastandfourier.json](../../../data/wave8/enrich/raw/github_com_notoriouslob_fastandfourier.json) (enrichment confidence 0.7)

</details>
