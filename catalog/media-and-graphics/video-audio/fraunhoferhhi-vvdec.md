# vvdec (VVdeC)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Video and audio](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `BSD-3-Clause-Clear` · 🟢 active

> Fraunhofer's optimized H.266/VVC Main10 software decoder; claims to outrun FFmpeg's native VVC decoder, with no published ratio.

| | |
|---|---|
| **Beats** | FFmpeg native VVC decoder (FFVVC); also VTM and OpenVVC per the lead, but no numbers against them on opened pages |
| **Claimed result** | Wiki page 'Integration in FFmpeg' (opened): 'As VVdeC is still faster and realtime capable' than the VVC decoder built into FFmpeg; no ratio is given on that page. Wiki Home page performance chart (opened, values read off the plot so approximate, latest v2.2 points): about 299 fps RA ClassB, about 299 fps LBP ClassB, about 131 fps AI ClassB, about 79 fps RA ClassA, about 44 fps AI ClassA; the first release v0.1 started at about 233, 100, 65 and 32 fps for RA ClassB, AI ClassB, RA ClassA and AI ClassA. |
| **Workload** | Software H.266/VVC Main10 decoding of VTM-10.0 encoded JVET common-test-condition sequences (ClassA, ClassB; random access, all intra, low-delay P) on a Xeon workstation with 20 threads; the FFmpeg comparison is a qualitative statement on the wiki. |
| **Metric** | throughput |
| **Hardware** | Linux workstation with Xeon W-2155 @ 3.3 GHz, 20 threads (all cores) |
| **Adoption** | 563 stars; integrated into FFmpeg (community libvvdec patchset) and mpv via wiki guides |
| **Last commit** | 2026-10-02 |
| **Links** | [repository](https://github.com/fraunhoferhhi/vvdec) · [benchmark](https://github.com/fraunhoferhhi/vvdec/wiki) |

## Verdict

The only numbers are first-party: a wiki chart of VVdeC against its own earlier releases, read off the plot at about 299 fps (RA and LDP, ClassB 1080p), 131 fps (AI ClassB), 79 fps (RA ClassA 4K) and 44 fps (AI ClassA) for v2.2 on a Xeon W-2155 with 20 threads decoding VTM-10.0 JVET test streams, with compiler and flags not stated. Against FFmpeg's native decoder there is only the wiki sentence that VVdeC is 'still faster and realtime capable'; a FOSDEM 2024 handout by the FFmpeg VVC author (snippet only, blocked here) put VVdeC with SIMD about 90% faster single-threaded and 75% faster multi-threaded than FFmpeg's C-only decoder, before FFmpeg added its AVX2 VVC assembly, so the current gap is unmeasured.

## Use it when

- You need to decode VVC/H.266 Main10 in software today (players, transcoders, HEIF/VVC image paths) and want a decoder that covers every Main10 tool, including RPR, subpictures and film grain synthesis.
- Real-time 1080p and 4K playback on a multi-core x86-64 or AArch64 machine: the first-party chart shows roughly 299 fps random-access 1080p and 79 fps random-access 4K with 20 threads on a Xeon W-2155.
- Arm targets (Android, Apple Silicon, Linux aarch64), where 3.x adds native NEON, SVE and SVE2 kernels with runtime CPU feature detection.
- Browser playback in Chrome, Firefox or Edge through the WebAssembly build.
- Integrating into a C or C++ application through a stable, plain-C API with a custom frame allocator to avoid copies.

## Skip it when

- You want something that ships inside stock FFmpeg: the native FFmpeg VVC decoder is built in, while libvvdec needs an unmerged patch that the wiki itself says the VVdeC team has not checked.
- Untrusted input in a security-sensitive process without sandboxing: use-after-free bugs (issues 390, 391, 403) and fuzzer-found crashes were still being fixed in 2026, and SECURITY.md was only added on 2026-09-29.
- Safari or other WebKit browsers: the WASM build does not run there, and the -msimd128 build breaks running in Node.js.
- Profiles beyond Main10 (for example 4:4:4 or 12-bit range extensions); the README claims Main10 only.
- Memory-tight devices: several pictures are in flight because of parse delay and frame-level overlap; an OpenVVC paper (snippet only) reports about half of VVdeC's memory for OpenVVC.

## How it is fast

Hand-written SIMD intrinsics for interpolation, inter/intra prediction, transforms, deblocking, SAO and ALF, compiled once per ISA (SSE4.1, SSE4.2, AVX, AVX2 on x86; NEON, NEON-RDM, SVE, SVE2 on Arm since 3.2.0; LoongArch LSX) and chosen at run time through function pointers; other targets get the x86 kernels through SIMD Everywhere. Reconstruction runs as a per-CTU task state machine (motion derivation, inter, intra, LMCS reshaping, vertical and horizontal deblocking, SAO, ALF) on a shared thread pool, with neighbour-dependency checks so different CTUs of a picture, and several pictures, are in different stages at once; parsing of later pictures overlaps reconstruction (parseDelay, default about 1.5x the thread count). Release builds use LTO by default.

## Compared with alternatives

Pick VVdeC over OpenVVC when you want full Main10 conformance, ongoing fixes and Arm SVE kernels from an active Fraunhofer project; OpenVVC's claimed edge in thread scaling and memory over VVdeC rests on a paper abstract seen only as a search snippet. The other decoders in this category (dav1d, edge264, rivet-h26x, rusty_h265) handle AV1, H.264 or HEVC, not VVC.

## Integration

| | |
|---|---|
| **Form** | static lib \| shared lib (CMake, plus a convenience Makefile; optional vvdecapp tool) |
| **Dependencies** | none at run time (SIMD Everywhere headers are bundled for non-x86 builds) |
| **Minimum toolchain** | C++14; CMake 3.12 per CMakeLists.txt (wiki says 3.13); GCC 5+, Visual Studio 2017+, Xcode clang |
| **Platforms** | x86 and x86-64 (SSE4.1 baseline, AVX2 dispatched at run time; no AVX-512 kernels), armv7 and aarch64 (NEON, SVE, SVE2), LoongArch64, WASM; tested on Windows, Linux, macOS arm64 and Android, while macOS x64 and iOS are marked 'needs testing'; powerpc and riscv64 reported to build by outside testers |
| **Thread safety** | not documented for concurrent calls on one decoder instance; each instance owns its own thread pool (threads parameter, default -1 meaning all cores) |
| **Drop-in for the baseline** | partial — usable inside FFmpeg as -c:v libvvdec only through the community patch (v9 for FFmpeg master, v8 for 8.x); otherwise a separate C API |

## Gotchas

- On x86 Unix builds every source file is compiled with -msse4.1, and issue 182 (closed 2024-06-24) showed SSE4.1 instructions reached even when scalar mode was forced, crashing pre-SSE4.1 CPUs; treat SSE4.1 as a hard requirement.
- VVDEC_ENABLE_WERROR defaults to ON, so newer compilers can fail the build on new warnings; pass -DVVDEC_ENABLE_WERROR=OFF when packaging.
- 3.0.0 broke API and ABI compatibility with 1.x and 2.x and moved output upscaling from the library into vvdecapp, so applications that relied on library-side upscaling must scale pictures themselves.
- The Clear BSD license explicitly grants no patent rights; VVC patent licensing is left to the user.

## Known shortcomings

- Tier D: no reachable page gives a number against FFmpeg's native VVC decoder, VTM or OpenVVC; the wiki chart (version_history_240205.png) plots VVdeC fps only against its own releases (about 299 fps RA ClassB on a Xeon W-2155, 20 threads, compiler and flags unstated), and the FFmpeg-integration wiki page and mpv-build-vvc README say 'faster' in words only. FOSDEM 2024 ratios exist only as search snippets (archive.fosdem.org blocked).
- Enricher (2026-10-04): the FOSDEM 2024 handout by the FFmpeg VVC author (snippet only) put VVdeC with SIMD about 90% faster single-threaded and 75% faster multi-threaded than FFmpeg's then C-only decoder, before FFmpeg added AVX2 VVC assembly, so the current gap is unmeasured. Every x86 Unix source file is compiled with -msse4.1 and issue 182 showed SSE4.1 reached even in forced scalar mode (SSE4.1 is a hard requirement); VVDEC_ENABLE_WERROR defaults ON; 3.0.0 broke API/ABI and moved upscaling out of the library; the Clear BSD license grants no patent rights; recent run of memory-safety fixes. Very active (3.2.0 with SVE/SVE2 and libFuzzer, last commit 2026-10-02).

## Caveats and trade-offs

No benchmark against a named competitor on any reachable page. The wiki Home chart 'VVdeC Decoder Performance Over Time' (img/version_history_240205.png, read directly; values approximate) plots only VVdeC releases v0.1 to v2.2: about 299 fps RA ClassB, about 300 fps LBP ClassB, about 131 fps AI ClassB, about 79 fps RA ClassA and about 44 fps AI ClassA at v2.2, on VTM-10.0 encoded JVET CTC sequences, Xeon W-2155 @ 3.3 GHz, 20 threads; no compiler, flags or OS details beyond 'Linux'. The wiki 'Integration in FFmpeg' page says only 'As VVdeC is still faster and realtime capable'; gianni-rosato/mpv-build-vvc README says FFmpeg's native ffvvc 'is not nearly as performant as Fraunhofer's vvdec', also without numbers. The ffvvc/FFmpeg wiki gives FFVVC's own fps on i7-12700K, M1 and i7-11700K, which cannot be set against VVdeC's Xeon W-2155 chart. Snippet only, not opened (archive.fosdem.org and hhi.fraunhofer.de are EGRESS_BLOCKED): the FOSDEM 2024 handout by the FFVVC author reportedly says FFVVC C code is on par with VVdeC (VVdeC about 10 percent faster on Linux, about 10 percent slower on Windows) and that VVdeC with asm was about 90 percent faster single-threaded and 75 percent faster multi-threaded; that predates FFmpeg's x86 AVX2 VVC assembly, so the gap may have narrowed. OpenVVC paper (arXiv 2205.12217) claims are snippet only. Papers listed on the wiki Publications page (ICIP 2020, ACM MM'21, MHV '22/'23) are on blocked hosts. A retier from an environment that reaches archive.fosdem.org or arXiv could lift this to B.

Decoder only. Supports all VVC Main10 features. Based on the VTM reference software with SIMD (x86, ARM via SIMDe, native ARM SIMD since v2.1) and task-level multi-threading. Safari/WebKit cannot run the WASM build. The FFmpeg integration is a community patch, not merged into FFmpeg master. The Clear BSD license states that no patent rights are granted, which matters for VVC.

## Maintenance

Very active (several merges a day in late September 2026, latest 2026-10-02, release 3.2.0 adding Arm SVE/SVE2 and libFuzzer); Clear BSD licensed and copyable, but no patent grant and a recent run of memory-safety fixes.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification C, tier now D.
- **Tier reason:** No reachable page gives a number against FFmpeg's VVC decoder, VTM or OpenVVC: the wiki Home chart (img/version_history_240205.png) plots VVdeC fps only against its own releases (Xeon W-2155, 20 threads, compiler and flags unstated), and the 'Integration in FFmpeg' wiki page and a third-party mpv build README say 'faster' in words only. The FOSDEM 2024 ratios are search-snippet-only (archive.fosdem.org EGRESS_BLOCKED), so per batch guidance D.
- **Verifier notes:** Downgraded C to D per batch guidance (no reachable ratio). Metadata checked: BSD-3-Clause-Clear, 563 stars, not a fork, last commit 2026-10-02 (active). The wiki caption calls the chart 'encoder performance' but the chart title says decoder; the fps values in the record match the chart.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** first-party chart against own releases only; first-party chart; FOSDEM snippet
- **Pages the verifier opened:**
  - <https://github.com/fraunhoferhhi/vvdec/wiki>
  - <https://raw.githubusercontent.com/wiki/fraunhoferhhi/vvdec/Home.md>
  - <https://raw.githubusercontent.com/wiki/fraunhoferhhi/vvdec/img/version_history_240205.png>
  - <https://raw.githubusercontent.com/wiki/fraunhoferhhi/vvdec/Integration-in-FFmpeg.md>
  - <https://raw.githubusercontent.com/wiki/fraunhoferhhi/vvdec/Publications.md>
  - <https://github.com/fraunhoferhhi/vvdec>
  - <https://github.com/fraunhoferhhi/vvdec/commits/master>
  - <https://github.com/ffvvc/FFmpeg/wiki>
  - <https://github.com/gianni-rosato/mpv-build-vvc>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/fraunhoferhhi/vvdec/HEAD/README.md>
  - <https://raw.githubusercontent.com/fraunhoferhhi/vvdec/HEAD/LICENSE.txt>
  - <https://raw.githubusercontent.com/fraunhoferhhi/vvdec/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/fraunhoferhhi/vvdec/HEAD/include/vvdec/vvdec.h.in>
  - <https://raw.githubusercontent.com/fraunhoferhhi/vvdec/HEAD/source/Lib/CommonLib/x86/InitX86.cpp>
  - <https://raw.githubusercontent.com/fraunhoferhhi/vvdec/HEAD/source/Lib/CommonLib/x86/CommonDefX86.cpp>
  - <https://raw.githubusercontent.com/fraunhoferhhi/vvdec/HEAD/source/Lib/DecoderLib/DecLibRecon.cpp>
  - <https://raw.githubusercontent.com/fraunhoferhhi/vvdec/HEAD/source/Lib/vvdec/vvdecimpl.cpp>
  - <https://raw.githubusercontent.com/fraunhoferhhi/vvdec/HEAD/source/Lib/Utilities/ThreadPool.h>
  - <https://github.com/fraunhoferhhi/vvdec/tree/master/source/Lib/CommonLib/x86>
  - <https://github.com/fraunhoferhhi/vvdec/wiki>
  - <https://github.com/fraunhoferhhi/vvdec/wiki/Integration-in-FFmpeg>
  - <https://github.com/fraunhoferhhi/vvdec/wiki/Changelog>
  - <https://github.com/fraunhoferhhi/vvdec/wiki/Build>
  - <https://github.com/fraunhoferhhi/vvdec/releases>
  - <https://github.com/fraunhoferhhi/vvdec/commits/master>
  - <https://github.com/fraunhoferhhi/vvdec/issues?q=is%3Aissue+crash+OR+performance+OR+slow>
  - <https://github.com/fraunhoferhhi/vvdec/issues/182>
  - <https://github.com/fraunhoferhhi/vvdec/issues/132>
  - <https://github.com/ffvvc/FFmpeg/wiki>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/fraunhoferhhi/vvdec`) · [data/wave10/enrich/raw/github_com_fraunhoferhhi_vvdec.json](../../../data/wave10/enrich/raw/github_com_fraunhoferhhi_vvdec.json) (enrichment confidence 0.65)

</details>
