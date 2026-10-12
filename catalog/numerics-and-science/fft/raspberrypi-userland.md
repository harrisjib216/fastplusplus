# GPU_FFT (Raspberry Pi VideoCore IV, hello_fft in raspberrypi/userland)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [FFT](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C with VideoCore QPU assembly kernels` · `BSD-3-Clause` · 🔴 abandoned

> Andrew Holme's GPU_FFT: power-of-two complex FFTs on the Raspberry Pi VideoCore IV GPU, about 10x FFTW on the Pi 1 ARM.

| | |
|---|---|
| **Beats** | FFTW (FFTW_MEASURE) running on the Raspberry Pi 1 ARM CPU |
| **Claimed result** | Doc text: 'ten times more data throughput than is possible on the 700 MHz ARM of the Pi 1'. Per-transform milliseconds, GPU_FFT (batch 1) vs FFTW_MEASURE: 2^8 0.033 vs 0.092; 2^12 0.25 vs 3.0; 2^15 3.5 vs 31; 2^16 7.0 vs 83; 2^20 194 vs 1600; 2^22 786 vs 8800. That is 2.8x, 12x, 8.9x, 11.9x, 8.2x and 11.2x (derived from page data). |
| **Workload** | Single-precision complex power-of-two FFTs from 2^8 to 2^22 points: per-transform runtime on the BCM2835 GPU (batch of 1 and 10) against FFTW_MEASURE on the same Pi 1. |
| **Metric** | latency |
| **Hardware** | Raspberry Pi 1 (BCM2835, 700 MHz ARM, VideoCore IV GPU, L2 cache enabled) |
| **Compiler and flags** | GPU side: hello_fft makefile runs 'gcc -o hello_fft.bin &lt;sources&gt; -lrt -lm -ldl' with no -O flag; the transform runs in hand-written VideoCore IV QPU assembly (qasm/\*.qasm assembled to hex/\*.hex), so host flags matter little. FFTW side: version, compiler and flags not stated. |
| **Adoption** | 2.1k stars (raspberrypi/userland, archived 2025-08-27); shipped as the hello_fft demo with Raspbian |
| **Last commit** | 2022-06-16 |
| **Links** | [repository](https://github.com/raspberrypi/userland) · [benchmark](https://github.com/raspberrypi/userland/blob/master/host_applications/linux/apps/hello_pi/hello_fft/gpu_fft.txt) |

## Verdict

The library author's own gpu_fft.txt (release 3.0, 2015) gives per-transform times on a 700 MHz Pi 1 with VC4 L2 cache enabled: GPU_FFT at batch 1 takes 0.033 ms vs 0.092 ms for FFTW_MEASURE at 256 points, 0.25 vs 3.0 ms at 4K, 7.0 vs 83 ms at 64K and 786 vs 8800 ms at 4M (2.8x to 12x). The FFTW version, build flags and timing code are not published; hello_fft.c only times the GPU side with clock_gettime and reports rms error.

## Use it when

- Spectrum analysis, SDR or audio DSP on a Raspberry Pi 1, Zero or other VideoCore IV board where the ARM core is the bottleneck: the doc table shows 2.8x at 256 points and 8-12x from 4K to 4M points over FFTW_MEASURE on a 700 MHz Pi 1
- Many same-size power-of-two transforms that can be batched into one execute call (batch of 10 roughly halves per-transform time at 256-512 points)
- Applications that tolerate single precision with 0.33-1.5 ppm rms error
- Freeing the ARM CPU for other work while the GPU computes longer transforms (mailbox path for long jobs avoids 100% CPU busy-waiting)

## Skip it when

- Any non-VideoCore IV hardware: the kernels are QPU machine code and gpu_fft_base.c only has Pi 1 and 'Pi 2?' memory paths; support for Pi 4/5 is not documented
- Double precision, non-power-of-two lengths, real-input (r2c) transforms or lengths below 256 or above 4,194,304
- When accuracy matters: the doc says FFTW is still one order of magnitude more accurate
- Programs that cannot run as root: mailbox.c opens /dev/mem and /dev/vcio and maps the V3D registers
- New projects on current Raspberry Pi OS: the userland repo README calls itself ancient and deprecated, the repo is archived, and its code is no longer installed on Bookworm images

## How it is fast

Hand-written VideoCore IV QPU assembly (qasm/\*.qasm, assembled to hex/\*.hex and embedded) splits each transform into a few passes of radix-16, radix-32 or radix-64 butterflies (e.g. the 256-point kernel is two radix-16 passes, the 4M-point kernel two radix-64 passes plus radix-32 passes), loading the first pass bit-reversed and ping-ponging between two buffers, with writes through the VPM and VC4 L2 cache. Twiddles are advanced with a trig recurrence corrected by float-float (df64) subtraction to recover accuracy. For short batches the ARM pokes V3D registers directly and busy-waits instead of using the firmware mailbox, which removes about 100 us of overhead per call.

## Compared with alternatives

Pick GPU_FFT itself when you can change the code and want the full speed, batching and the 2D transpose; gpu_fftw (already catalogued) is an LD_PRELOAD shim over this same library that keeps the FFTW API but copies arrays, falls back to FFTW and supports only 1-D 2^8-2^21. On anything other than a VideoCore IV Pi, the CPU libraries in the list (FFTW itself, PocketFFT, PFFFT, Ne10 on ARM) are the options.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | Raspberry Pi firmware mailbox device (/dev/vcio), /dev/mem, libbcm_host.so (dlopen'd for SDRAM and peripheral addresses), librt, libm, libdl |
| **Minimum toolchain** | Plain C (gcc, no flags in the makefile); prebuilt shader hex files included, the QPU assembler is only needed to change kernels |
| **Platforms** | Raspberry Pi boards with the VideoCore IV GPU (BCM2835 Pi 1/Zero; gpu_fft_base.c also has a Pi 2 memory path); 32-bit Raspbian/Raspberry Pi OS era firmware |
| **Thread safety** | not documented; one process owns the V3D block per execute call, and on Pi 1 OpenGL can share it only with GPU_FFT_USE_VC4_L2_CACHE set to 0 and explicit glFinish() between uses |
| **Drop-in for the baseline** | no |

## Gotchas

- Input is destroyed and the result is out of place for log2_N 12-16 (odd pass count) but in place otherwise; always read fft-&gt;out.
- GPU memory is permanently lost until reboot if gpu_fft_release() is not called (doc and hello_fft.c comment), so crash handling matters.
- The direct-register path (batches up to about 1 ms of work) busy-waits on V3D_SRQCS with no timeout; only the mailbox path has the 2000 ms timeout.
- Buffers are separated by fft-&gt;step, which is larger than N because of guard space; index batches with step, not N.

## Known shortcomings

- Only the hello_fft component of the archived (2025-08-27) raspberrypi/userland repo. FFTW harness, version and flags not published; the hello_fft makefile runs gcc with no -O flag. The doc says FFTW is 10x more accurate. Runs only on the VideoCore IV GPU (Pi 1-3/Zero) and needs root.
- Needs root; only VideoCore IV Pis (Pi 4/5 support undocumented). The short-batch path busy-waits with no timeout. Repo archived and its README calls itself deprecated. The listed gpu_fftw is an LD_PRELOAD shim over this same GPU_FFT library.

## Caveats and trade-offs

First-party table from the library's own doc file (gpu_fft.txt, release 3.0, Andrew Holme, 2015), measured on a 700 MHz Pi 1 with VC4 L2 cache enabled. The baseline is FFTW_MEASURE on the same Pi 1 ARM11 CPU; FFTW version, build flags and the FFTW timing code are not published (hello_fft.c times only GPU_FFT). The doc says FFTW is still one order of magnitude more accurate (GPU_FFT rms error 0.33-1.5 ppm, single precision, output not scaled). Kernels are VideoCore IV QPU assembly, so they target the BCM2835-family GPU (Pi 1-3/Zero; gpu_fft_base.c has a Pi 2 memory path) and need root plus the mailbox device; they do not carry over to other GPUs. The repo was archived on 2025-08-27 and its README calls it 'ancient and deprecated'. Last commit date is for the hello_fft directory. The author's GPU_FFT web page was not opened.

Tied to the BCM2835 VideoCore IV 3D hardware and the Raspberry Pi mailbox device (the demo runs under sudo). Single-precision only, power-of-two lengths from 256 to 4,194,304, and a transpose helper for 2D. Per the doc, accuracy is 0.33 to 1.5 ppm rms and FFTW is still one order of magnitude more accurate. C API, so callable from C++.

## Maintenance

Abandoned: last hello_fft commit 2022-06-16 and raspberrypi/userland archived on 2025-08-27 with a README telling users to rethink solutions built on it; BSD-3-Clause and only a handful of C files plus shader hex, so it is easy to vendor for legacy Pi 1/Zero projects.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** gpu_fft.txt (release 3.0, 2015, by the library author) gives a per-transform table with GPU_FFT at batch 1 and 10 next to FFTW_MEASURE on a Pi 1 with L2 cache enabled; every number in the record matches, and the ratios are correctly marked as derived. The harness hello_fft.c times only the GPU side and its makefile runs plain gcc with no optimization flag; the FFTW harness, FFTW version and FFTW build flags are not published, so this is first-party and partly reproducible: tier C.
- **Verifier notes:** Judged only the hello_fft component. QPU assembly sources (qasm/) and C files carry Andrew Holme's BSD-3-Clause header; repo LICENCE is also BSD-3-Clause, so copyable holds. Archived 2025-08-27, 2.1k stars, not a fork; last hello_fft commit 2022-06-16 confirmed.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier; enrichment
- **Pages the verifier opened:**
  - <https://github.com/raspberrypi/userland>
  - <https://github.com/raspberrypi/userland/commits/master/host_applications/linux/apps/hello_pi/hello_fft>
  - <https://github.com/raspberrypi/userland/blob/master/host_applications/linux/apps/hello_pi/hello_fft/gpu_fft.txt>
  - <https://raw.githubusercontent.com/raspberrypi/userland/master/host_applications/linux/apps/hello_pi/hello_fft/gpu_fft.txt>
  - <https://raw.githubusercontent.com/raspberrypi/userland/master/host_applications/linux/apps/hello_pi/hello_fft/makefile>
  - <https://raw.githubusercontent.com/raspberrypi/userland/master/host_applications/linux/apps/hello_pi/hello_fft/hello_fft.c>
  - <https://raw.githubusercontent.com/raspberrypi/userland/master/host_applications/linux/apps/hello_pi/hello_fft/gpu_fft.c>
  - <https://raw.githubusercontent.com/raspberrypi/userland/master/host_applications/linux/apps/hello_pi/hello_fft/gpu_fft_base.c>
  - <https://raw.githubusercontent.com/raspberrypi/userland/master/host_applications/linux/apps/hello_pi/hello_fft/qasm/gpu_fft.qinc>
  - <https://raw.githubusercontent.com/raspberrypi/userland/master/LICENCE>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/raspberrypi/userland/master/README.md>
  - <https://raw.githubusercontent.com/raspberrypi/userland/master/LICENCE>
  - <https://raw.githubusercontent.com/raspberrypi/userland/master/host_applications/linux/apps/hello_pi/hello_fft/gpu_fft.txt>
  - <https://raw.githubusercontent.com/raspberrypi/userland/master/host_applications/linux/apps/hello_pi/hello_fft/gpu_fft.h>
  - <https://raw.githubusercontent.com/raspberrypi/userland/master/host_applications/linux/apps/hello_pi/hello_fft/gpu_fft.c>
  - <https://raw.githubusercontent.com/raspberrypi/userland/master/host_applications/linux/apps/hello_pi/hello_fft/gpu_fft_base.c>
  - <https://raw.githubusercontent.com/raspberrypi/userland/master/host_applications/linux/apps/hello_pi/hello_fft/gpu_fft_shaders.c>
  - <https://raw.githubusercontent.com/raspberrypi/userland/master/host_applications/linux/apps/hello_pi/hello_fft/gpu_fft_twiddles.c>
  - <https://raw.githubusercontent.com/raspberrypi/userland/master/host_applications/linux/apps/hello_pi/hello_fft/gpu_fft_trans.h>
  - <https://raw.githubusercontent.com/raspberrypi/userland/master/host_applications/linux/apps/hello_pi/hello_fft/hello_fft.c>
  - <https://raw.githubusercontent.com/raspberrypi/userland/master/host_applications/linux/apps/hello_pi/hello_fft/hello_fft_2d.c>
  - <https://raw.githubusercontent.com/raspberrypi/userland/master/host_applications/linux/apps/hello_pi/hello_fft/makefile>
  - <https://raw.githubusercontent.com/raspberrypi/userland/master/host_applications/linux/apps/hello_pi/hello_fft/mailbox.c>
  - <https://raw.githubusercontent.com/raspberrypi/userland/master/host_applications/linux/apps/hello_pi/hello_fft/mailbox.h>
  - <https://raw.githubusercontent.com/raspberrypi/userland/master/host_applications/linux/apps/hello_pi/hello_fft/qasm/gpu_fft.qinc>
  - <https://raw.githubusercontent.com/raspberrypi/userland/master/host_applications/linux/apps/hello_pi/hello_fft/qasm/gpu_fft_256.qasm>
  - <https://raw.githubusercontent.com/raspberrypi/userland/master/host_applications/linux/apps/hello_pi/hello_fft/qasm/gpu_fft_4096k.qasm>
  - <https://raw.githubusercontent.com/gpu-fftw/gpu_fftw/HEAD/README.md>
  - <https://github.com/raspberrypi/userland/issues?q=is%3Aissue+gpu_fft>
  - <https://github.com/raspberrypi/userland/issues?q=hello_fft>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/raspberrypi/userland`) · [data/wave8/enrich/raw/github_com_raspberrypi_userland.json](../../../data/wave8/enrich/raw/github_com_raspberrypi_userland.json) (enrichment confidence 0.75)

</details>
