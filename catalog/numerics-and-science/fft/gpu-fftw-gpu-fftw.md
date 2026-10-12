# gpu_fftw

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [FFT](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C/C++` · `MIT` · 🔴 abandoned

> LD_PRELOAD shim that reroutes FFTW3 1-D power-of-two complex float FFTs to the original Raspberry Pi's VideoCore IV GPU.

| | |
|---|---|
| **Beats** | FFTW3 (running on the Raspberry Pi CPU) |
| **Claimed result** | Self-test output: 'GPU FFTW 7.11652 times faster (11523.3 ffts/sec, 86.781 usec/fft, fftw3: 1619.23 ffts/sec)'. README: 'They can be up to ten times faster than running fftw3 by itself.' |
| **Workload** | Binary-compatible FFTW3 replacement that offloads power-of-two complex float FFTs (log2 N from 8 to 21) to the Raspberry Pi VideoCore GPU via Andrew Holme's GPU_FFT; the README self-test (gpu_fftw -t, show_speed in gpu_fftw_main.cpp) times 1000 forward 1024-point complex float FFTs against CPU fftw3f with an FFTW_ESTIMATE plan, excluding plan creation. |
| **Metric** | throughput |
| **Hardware** | Raspberry Pi (model not stated in the README; the Makefile targets armv6, i.e. original Pi class) |
| **Compiler and flags** | Makefile: gcc/g++ (or armv6l cross gcc) with -march=armv6 -mfloat-abi=hard -mfpu=vfp -mtune=arm1176jzf-s -O3 -ffast-math -pipe -fstack-protector (-std=c99 / -std=c++11); the README sample run does not state the compiler version or FFTW build used |
| **Adoption** | 46 stars |
| **Last commit** | 2015-01-29 |
| **Links** | [repository](https://github.com/gpu-fftw/gpu_fftw) · [benchmark](https://github.com/gpu-fftw/gpu_fftw) |

## Verdict

The project's own self-test, on an unnamed Raspberry Pi (Makefile targets ARMv6, so Pi 1 class), timed 1,000 forward 1,024-point complex float FFTs: 11,523 FFT/s on the GPU versus 1,619 FFT/s for CPU fftw3f with an FFTW_ESTIMATE plan (7.1x); plan creation and the GPU path's one-time input copy are outside the timed loop, and the compiler/FFTW versions are not stated.

## Use it when

- Legacy Raspberry Pi 1 / Zero-class (BCM2835, ARMv6) systems running an existing FFTW3-linked program you cannot recompile, e.g. SDR or audio spectrum tools.
- 1-D complex single-precision FFTs of power-of-two length 2^8 to 2^21 where the plan is reused and the program fills the input before planning.
- Quick experiments to see whether GPU offload helps an FFT-bound Pi 1 workload before porting code to the GPU_FFT API directly.

## Skip it when

- Any program that plans once and then writes new data into the input array before each fftw_execute: the shim copies the input to GPU memory only at plan time, so later executes transform the stale plan-time data.
- Raspberry Pi 2/3/4/5 or any non-Pi hardware: the bundled GPU_FFT 2.0 hard-codes the BCM2835 peripheral base 0x20000000, and open issue #1 reports the self-test override check failing on a Pi 3 (GPU/FFTW difference 0 ppm, i.e. the GPU path apparently never ran).
- Double precision work: the -d 'double squashing' mode silently computes double requests in float.
- 2-D/3-D, real-to-complex, batched (plan_many), new-array execute (fftw_execute_dft) or threaded FFTW use: none are intercepted.
- Production or multi-user systems: requires root (/dev/mem mapping, mknod of /dev/gpu_mb), runs the target program as root with LD_PRELOAD, and the README calls it an early alpha.

## How it is fast

The work is done by Andrew Holme's GPU_FFT 2.0 (bundled as hello_fft/): per-size hand-written QPU shader binaries that compute the transform in 2 to 4 passes of radix-16/32/64 butterflies (N=1,024 is two radix-32 passes) spread over the 8 VideoCore IV QPUs, with twiddles and ping-pong buffers in GPU-shared memory. For small batches (N\*jobs &lt;= 20480) it launches the shaders by poking V3D registers directly through /dev/mem and busy-waits; larger jobs go through the firmware mailbox. The speedup is simply that the Pi 1's ARM11 CPU running FFTW is much slower than the QPUs.

## Compared with alternatives

No catalogued sibling targets the Raspberry Pi GPU; on a Pi 1/Zero with an unmodifiable FFTW binary this is the only drop-in, while for new code or newer Pis a NEON CPU library such as Ne10, or PFFFT/muFFT, is the safer choice.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | FFTW3 (libfftw3 and libfftw3f, called via dlsym RTLD_NEXT), libdl, bundled GPU_FFT 2.0 (hello_fft, BSD-3-Clause), root access to /dev/mem and the VideoCore mailbox |
| **Minimum toolchain** | C99 + C++11 (gcc/g++; Makefile tunes for -march=armv6 -mfpu=vfp -mtune=arm1176jzf-s) |
| **Platforms** | Raspberry Pi with BCM2835 / VideoCore IV (Pi 1, Zero); Linux only |
| **Thread safety** | Not thread-safe: plans live in a static 1024-slot array with an unlocked counter, the mailbox handle is a static, and the shim calls setenv/unsetenv on every plan to signal GPU use. |
| **Drop-in for the baseline** | partial — binary drop-in via LD_PRELOAD for fftw(f)_plan_dft_1d + execute + destroy_plan only; every 1-D DFT plan (even a fallback one) becomes a wrapper struct, so passing it to any other FFTW function (fftw_execute_dft, fftw_print_plan, fftw_flops) hands FFTW a foreign pointer |

## Gotchas

- Plan slots are taken as mplan_arr[mplan_n++] and freed by decrementing mplan_n, so destroying plans out of LIFO order lets the next plan overwrite a live one; past 1024 live plans the fallback path dereferences a NULL metaplan.
- The input array is copied to GPU memory inside fftw_plan_dft_1d and never again; FFTW_MEASURE-style 'plan first, fill later' code gets wrong results with no error.
- Planner flags (FFTW_MEASURE, FFTW_PATIENT, wisdom) are ignored on the GPU path; each GPU plan allocates and maps its own VideoCore memory, so many concurrent plans can exhaust GPU memory (then it falls back to FFTW).
- The launcher passes child arguments poorly (open issue #2: the child's flags are parsed as gpu_fftw options unless separated with --).

## Known shortcomings

- Security: needs sudo/root to reach the GPU mailbox (the 'drop root' TODO is open); FFTW baseline planned with FFTW_ESTIMATE and only N=1024 timed.
- Correctness bugs: input is copied to the GPU only at plan creation, so re-running a plan after writing new data returns the FFT of the old data (the self-test timing leaves that copy out); destroying plans out of creation order lets the next plan overwrite a live one, and past 1024 live plans it dereferences NULL; bundled GPU_FFT 2.0 hard-codes the BCM2835 base (Pi 1/Zero only) and issue #1 on a Pi 3 suggests the GPU path never ran; creates /dev/gpu_mb with mknod.

## Caveats and trade-offs

First-party numbers from one sample self-test output; Pi model and CPU clock not stated in the README (Makefile tunes for arm1176jzf-s, i.e. original BCM2835 Pi class). The FFTW baseline is planned with FFTW_ESTIMATE rather than FFTW_MEASURE, which handicaps FFTW, and only N=1024 is timed. Float precision only (optional 'double squashing' silently computes double requests in float); no 2-D, 3-D or real FFTs. Security: needs sudo/root to reach the GPU mailbox, and the README's 'Drop root permissions asap' TODO is unchecked; README calls it an early alpha. Bundled GPU_FFT (hello_fft/) is Andrew Holme's code under BSD-3-Clause, compatible with the project's MIT license. Repo is abandoned since January 2015.

Float only (double only through lossy 'double squashing'), power-of-two sizes 2^8 to 2^21, 1-D complex only (no 2-D/3-D/real), copies arrays to GPU memory, needs root, falls back to FFTW3 otherwise. Early alpha by the author's own words.

## Maintenance

Abandoned since January 2015 (two open, unanswered issues) and alpha quality; MIT-licensed and small, but only of historical or Pi-1-specific interest given its stale-input and plan-slot bugs.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party sample self-test output in the README (7.11652x, 11523.3 vs 1619.23 ffts/sec); the test code (gpu_fftw_main.cpp show_speed) and Makefile flags are public, but the Pi model/CPU is not stated and the baseline FFTW plan uses FFTW_ESTIMATE, so C.
- **Verifier notes:** MIT license (LICENSE file, copyright placeholder 'John Doe'), 46 stars, 7 forks, 44 commits, last commit 2015-01-29 confirmed on github.com. Numbers match README exactly; 'up to ten times faster' is the README's description of GPU_FFT generally.
- **Fields the verifier corrected:** `workload`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/gpu-fftw/gpu_fftw>
  - <https://github.com/gpu-fftw/gpu_fftw/commits>
  - <https://raw.githubusercontent.com/gpu-fftw/gpu_fftw/HEAD/README.md>
  - <https://raw.githubusercontent.com/gpu-fftw/gpu_fftw/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/gpu-fftw/gpu_fftw/HEAD/Makefile>
  - <https://raw.githubusercontent.com/gpu-fftw/gpu_fftw/HEAD/hello_fft/gpu_fft.c>
  - <https://raw.githubusercontent.com/gpu-fftw/gpu_fftw/HEAD/gpu_fftw_main.cpp>
- **Sources the enricher read:**
  - <https://github.com/gpu-fftw/gpu_fftw>
  - <https://github.com/gpu-fftw/gpu_fftw/issues?q=is%3Aissue>
  - <https://github.com/gpu-fftw/gpu_fftw/issues/1>
  - <https://github.com/gpu-fftw/gpu_fftw/issues/2>
  - <https://raw.githubusercontent.com/gpu-fftw/gpu_fftw/HEAD/README.md>
  - <https://raw.githubusercontent.com/gpu-fftw/gpu_fftw/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/gpu-fftw/gpu_fftw/HEAD/Makefile>
  - <https://raw.githubusercontent.com/gpu-fftw/gpu_fftw/HEAD/gpu_fftw.h>
  - <https://raw.githubusercontent.com/gpu-fftw/gpu_fftw/HEAD/gpu_fftw.c.template>
  - <https://raw.githubusercontent.com/gpu-fftw/gpu_fftw/HEAD/gpu_fftw_util.c>
  - <https://raw.githubusercontent.com/gpu-fftw/gpu_fftw/HEAD/gpu_fftw_main.cpp>
  - <https://raw.githubusercontent.com/gpu-fftw/gpu_fftw/HEAD/hello_fft/gpu_fft_base.c>
  - <https://raw.githubusercontent.com/gpu-fftw/gpu_fftw/HEAD/hello_fft/gpu_fft.c>
  - <https://raw.githubusercontent.com/gpu-fftw/gpu_fftw/HEAD/hello_fft/gpu_fft.h>
  - <https://raw.githubusercontent.com/gpu-fftw/gpu_fftw/HEAD/hello_fft/mailbox.c>
  - <https://raw.githubusercontent.com/gpu-fftw/gpu_fftw/HEAD/hello_fft/mailbox.h>
  - <https://raw.githubusercontent.com/gpu-fftw/gpu_fftw/HEAD/hello_fft/gpu_fft_twiddles.c>
  - <https://raw.githubusercontent.com/gpu-fftw/gpu_fftw/HEAD/hello_fft/gpu_fft_shaders.c>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/gpu-fftw/gpu_fftw`) · [data/wave8/enrich/raw/github_com_gpu_fftw_gpu_fftw.json](../../../data/wave8/enrich/raw/github_com_gpu_fftw_gpu_fftw.json) (enrichment confidence 0.8)

</details>
