# astc-encoder (astcenc)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Arm's reference ASTC texture compressor (CLI plus C/C++ library); 2.x and later are 2-3.5x faster than its own 1.7 series.

| | |
|---|---|
| **Beats** | astcenc 1.7 (earlier major series of the same encoder; no third-party baseline opened) |
| **Claimed result** | Values read off first-party relative-performance chart images (approximate; the changelog text gives no numbers): astcenc-avx2 2.0 against astcenc 1.7: -thorough about 2.05-3.1x, -medium about 1.7-3.85x (most points 2.3-3.5x), -fast about 1.3-4.0x (most points 1.9-3.4x), with PSNR delta near 0 to -0.2 dB for most points. Outliers: a -fast grayscale 4x4 point at about 1.6x loses about 3.6 dB, and single points lose about 0.5-0.6 dB in each preset. Later series on the same CPU: astcenc-avx2 4.0 against 3.7, -thorough about 1.17-1.74x at near-equal PSNR (relative-3.7-to-4.0.png). Text claims: the current README says each step from SSE2 to SSE4.1 to AVX2 gains about 15%, and the 5.3.0 changelog says the reference C build (ASTCENC_ISA_NONE) is around 3.25 times slower than the SSE2 default. |
| **Workload** | Compression performance (MTex/s) versus PSNR across Arm's test image sets (LDR, HDR, normal map and grayscale images) at 4x4, 5x5, 6x6 and 8x8 block sizes for the -thorough, -medium and -fast presets, astcenc-avx2 2.0 versus astcenc 1.7 (relative-performance chart in the 2.x changelog). |
| **Metric** | throughput |
| **Hardware** | Intel Core i5-9600K at 4.2 GHz, 6 threads (stated at the top of each changelog page) |
| **Compiler and flags** | astcenc-avx2 binary (AVX2, SSE4.2, POPCNT, F16C); compiler and optimization flags are not stated on the changelog pages. Repo CMake uses -flto=auto for GCC and -ffp-model=precise with -ffp-contract=on for Clang in non-invariant builds. |
| **Adoption** | 1.3k stars, 286 forks; official Arm ASTC reference-quality encoder; latest series 5.7.0 (August 2026) |
| **Last commit** | 2026-08-29 |
| **Links** | [repository](https://github.com/ARM-software/astc-encoder) · [benchmark](https://raw.githubusercontent.com/ARM-software/astc-encoder/3.7/Docs/ChangeLog-2x.md) |

## Verdict

Arm's changelog charts (i5-9600K at 4.2 GHz, 6 threads) show astcenc-avx2 2.0 coding about 2-3x faster than astcenc 1.7 at -thorough and mostly 2-3.5x at -medium and -fast, with PSNR mostly within 0.2 dB and one -3.6 dB -fast grayscale outlier; 4.0 is about 1.17-1.74x over 3.7 at -thorough. The baseline is the project's own 1.7: its stock Makefile builds scalar code with -O3 -msse2, against 2.0's -O3 -flto -mavx2 -mpopcnt, so part of the gain is ISA and LTO. No compiler is stated for either side, and no rival encoder is timed.

## Use it when

- Offline asset pipelines that must produce ASTC for mobile or Apple GPUs, especially block sizes above 8x8, HDR (-ch/-cH) or 3D textures, which narrower ASTC encoders do not cover.
- Quality-sensitive content (normal maps, mask maps, UI) where -medium or -thorough quality matters more than encode time.
- Many-core build machines: one image can be split across N caller threads, and since 5.4.0 several contexts with the same config can share read-only tables when you run one image per thread.
- Builds that need identical output on every platform: invariant builds (the default) give bit-exact results across compilers and ISAs.
- Arm64 build hosts: NEON and SVE 128/256 backends are first-class, with prebuilt Linux Arm64 binaries since 5.2.0.

## Skip it when

- Latency-bound runtime encoding of 2D LDR photos: Arm's own astcenc 3.1 blog (search snippet only, page blocked) says ISPC TexComp can be up to 3x faster at quality similar to -fast, though worse on normal and mask maps. A Chalmers thesis snippet claims up to 44x for Intel's encoder at the same quality, against an unstated, probably older astcenc.
- Non-ASTC targets (BC1-BC7, ETC1/ETC2): astcenc encodes ASTC only.
- Distributing one binary for unknown x86 CPUs: the core library does no runtime ISA dispatch (issue #672, open, asks for it), so you ship SSE2/SSE4.1/AVX2 variants and choose one yourself. macOS gets a universal binary.
- Data that needs 1-bit punch-through alpha, signed values (as in BC6H signed) or two-plane .rg sampling like BC5: Encoding.md says ASTC has no direct equivalent.
- Choosing a speed winner over rival encoders: the only measured speedup is against astcenc's own 1.7 release, so this entry gives no evidence against ISPC, GPU or other ASTC encoders.

## How it is fast

The 2.0 rewrite added a SIMD abstraction (vfloat4/vint4/vfloat8) with SSE2, SSE4.1, AVX2 and later NEON, SVE and RISC-V V backends, replacing 1.7's scalar code. Partition search runs k-means on the block's texels, ranks all 1024 hash-generated partitionings by how many texels disagree with that clustering, and gives the detailed endpoint and weight search only the top N candidates. Per-preset tuning tables (astcenc_entry.cpp) cap block modes, partition indices and refinement passes, and dB-target and correlation early-outs skip 2-plane and 3/4-partition trials once a good enough encoding is found. 4.x added in-register SIMD permutes for small tables, deferred weight and color packing, and a narrower search for later trials.

## Compared with alternatives

Pick astcenc over refreshed-astc-encoder, a fork of the 2015-era code measured only against old Arm binaries, for anything current. Pick it over the ISPC kernels behind intel-tex-rs-2 when you need HDR, 3D, block sizes above 8x8 or the highest-quality presets; bc7e, bc7enc, etcpak, Goofy and ICBC target BCn/ETC, not ASTC.

## Integration

| | |
|---|---|
| **Form** | static lib (CMake core codec library, optional shared lib via ASTCENC_SHAREDLIB) plus CLI tool |
| **Dependencies** | none for the core codec; the CLI bundles stb_image, Wuffs and TinyEXR; unit tests use a googletest submodule |
| **Minimum toolchain** | C++14 (CMAKE_CXX_STANDARD 14), CMake 3.15+; tested with Clang 9+, Visual Studio 2019+ (ClangCL recommended) and Xcode 14+; astcenc.h is C-compatible since 5.4.0 |
| **Platforms** | x86-64 (SSE2; SSE4.1+POPCNT; AVX2+POPCNT+F16C), aarch64 (NEON, SVE 128-bit, SVE 256-bit), RISC-V V at VLEN=256 through the NONE/NATIVE build, portable reference C (big-endian with ASTCENC_BIG_ENDIAN=ON); Windows, Linux, macOS, Android unofficial |
| **Thread safety** | One context per image stream. To split one image across threads, allocate the context with thread_count N and call astcenc_compress_image once per thread with distinct thread_index; the caller creates the threads and calls compress_reset between images. Contexts with the same config can share read-only tables (5.4.0+). astcenc_compress_cancel (5.2.0+) stops an in-flight compression. |
| **Drop-in for the baseline** | partial — same ASTC output format as 1.7, but the 2.0 CLI is not command-line compatible with 1.7, and the library API broke between minor releases until 5.4.0 (semantic versioning since then) |

## Gotchas

- No runtime ISA check in the core library: an AVX2 or SVE-256 build on a CPU without that ISA faults, so the caller must check, as astcenccli_entry.cpp does. SVE builds must match the host vector length.
- Invariance is on by default and costs speed. ASTCENC_INVARIANCE=OFF enables -ffp-contract=fast (and -mfma on AVX2) for up to 5-20% more speed at up to 0.2 dB lower quality, but output then differs across compilers and platforms. Building.md also says Clang builds are about 15% faster than GCC builds.
- If textures are sampled with the decode_unorm8 extension, compress with -decode_unorm8 or ASTCENC_FLG_USE_DECODE_UNORM8 to get the right rounding. Contexts made with ASTCENC_FLG_SELF_DECOMPRESS_ONLY can return magenta error blocks when decoding images from other encoders or configurations.
- Preset names do not mean equal effort across major versions (4.2 retuned -exhaustive to 3x slower and added -verythorough; 4.6 pruned -medium and -thorough again), and 5.7.0 removed the -repeats benchmarking option. Re-measure on your content when upgrading.

## Known shortcomings

- A self-comparison of astcenc 2.0 against the project's own 1.7 (chart images on an i5-9600K with 6 threads, compiler unstated; 2.1-3.1x thorough, 1.7-3.8x medium, 1.3-4.0x fast) with no third-party incumbent; one -fast case loses 3.6 dB PSNR. The SPEC CPU2026 731.astcenc_r workload is snippet-only (spec.org blocked).
- Enricher (2026-10-04): the changelog charts compare against the project's own 1.7, whose stock Makefile builds scalar -O3 -msse2 code, against 2.0's -O3 -flto -mavx2 -mpopcnt, so part of the 2-3.5x is ISA and LTO; no compiler is stated and no rival encoder is timed. The 2.0 harness runs a 1.7 binary from an untracked Binaries/1.7 directory (build unrecorded) and parses different timer output lines; the 3.7 wrapper implies a locally modified 1.7 binary; every harness keeps the best of N repeats; Docs/Testing.md says 4.3 GHz where the changelogs say 4.2 GHz. No correctness bug behind the timings. No runtime ISA check in the core library (AVX2/SVE builds fault on other CPUs); invariance on by default costs 5-20% speed; preset effort changed across 4.2, 4.6 and 5.7 (removed -repeats), so re-measure when upgrading. Tier C stands.

## Caveats and trade-offs

The baseline is the project's own 1.7 release. The 2.0 changelog lists SSE2, SSE4.2 and AVX2 SIMD paths as new 2.x features, so most of the gain reflects that vectorization: a 2020 self-comparison, not a comparison with a rival ASTC encoder such as ISPC TexComp. The 1.7 to 2.0 comparison exists only on tag 3.7 and earlier (main's changelogs start at 4.x). The numbers are chart images, so the ranges above are visual readings with about 0.1x uncertainty. A few points lose PSNR, most visibly a -fast grayscale 4x4 point at about -3.6 dB. Compiler and flags are not stated for the charts; the 2.2 notes say Linux release binaries moved to Clang 9.0 for up to 15% more speed, so the 2.0 binary's compiler differed and is unknown. The charts are first-party, so tier C. Arm's public test harness (Test/astc_test_image.py, documented in Docs/Testing.md) can regenerate relative charts. WebSearch snippets point to Khronos and Samsung posts on astcenc 2.0, a 2020 third-party texture-compression survey by Aras Pranckevicius that includes astcenc, and a SPEC CPU2026 benchmark named 731.astcenc_r; khronos.org, spec.org and the blogs are blocked here, so no numbers were taken from them. The lead's '2-4x over 1.7' holds for -medium and -fast; -thorough is closer to 2-3x.

Quality presets (-fastest to -exhaustive) trade compression time against PSNR. Multiple prebuilt ISA variants (SSE2, SSE4.1, AVX2, NEON, SVE 128 and 256, RISC-V vector backend). Codec library API is not binary compatible across versions. Builds are bit-exact across platforms by default; the NO_INVARIANCE option gives up to 5-20% more speed for up to 0.2 dB lower quality (4.0 changelog). 2.0 changed the command line and added a library API.

## Maintenance

Actively maintained by Arm (5.7.0 in August 2026, last commit 2026-08-29), Apache-2.0, fuzzed in OSS-Fuzz; main is the development branch, so production users should pin a release tag.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party charts in Docs/ChangeLog-2x.md at tag 3.7 (relative-1.7-to-2.0.png) and ChangeLog-4x.md (relative-3.7-to-4.0.png) compare the project against its own earlier releases on an i5-9600K at 4.2 GHz with 6 threads. No compiler or flags are stated for those runs, and there is no rival encoder, so C.
- **Verifier notes:** I re-read both chart images: the ranges hold, with a -3.6 dB PSNR outlier on -fast added. It is a self-comparison against 1.7 with the compiler unstated, so C stays. Metadata is correct: Apache-2.0, 1.3k stars, 286 forks, last commit 2026-08-29, 5.7.0 released August 2026.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** first-party charts
- **Pages the verifier opened:**
  - <https://github.com/ARM-software/astc-encoder>
  - <https://github.com/ARM-software/astc-encoder/commits/main>
  - <https://raw.githubusercontent.com/ARM-software/astc-encoder/3.7/Docs/ChangeLog-2x.md>
  - <https://raw.githubusercontent.com/ARM-software/astc-encoder/3.7/Docs/ChangeLog-3x.md>
  - <https://raw.githubusercontent.com/ARM-software/astc-encoder/3.7/Docs/ChangeLogImg/relative-1.7-to-2.0.png>
  - <https://raw.githubusercontent.com/ARM-software/astc-encoder/main/README.md>
  - <https://raw.githubusercontent.com/ARM-software/astc-encoder/main/Docs/ChangeLog-4x.md>
  - <https://raw.githubusercontent.com/ARM-software/astc-encoder/main/Docs/ChangeLog-5x.md>
  - <https://raw.githubusercontent.com/ARM-software/astc-encoder/main/Docs/ChangeLogImg/relative-3.7-to-4.0.png>
  - <https://raw.githubusercontent.com/ARM-software/astc-encoder/main/Docs/Testing.md>
  - <https://raw.githubusercontent.com/ARM-software/astc-encoder/main/LICENSE.txt>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/ARM-software/astc-encoder/main/README.md>
  - <https://raw.githubusercontent.com/ARM-software/astc-encoder/main/Docs/ChangeLog-5x.md>
  - <https://raw.githubusercontent.com/ARM-software/astc-encoder/main/Docs/ChangeLog-4x.md>
  - <https://raw.githubusercontent.com/ARM-software/astc-encoder/main/Docs/Building.md>
  - <https://raw.githubusercontent.com/ARM-software/astc-encoder/main/Docs/Testing.md>
  - <https://raw.githubusercontent.com/ARM-software/astc-encoder/main/Docs/Encoding.md>
  - <https://raw.githubusercontent.com/ARM-software/astc-encoder/main/Source/astcenc.h>
  - <https://raw.githubusercontent.com/ARM-software/astc-encoder/main/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ARM-software/astc-encoder/main/Source/cmake_core.cmake>
  - <https://raw.githubusercontent.com/ARM-software/astc-encoder/main/Source/astcenc_entry.cpp>
  - <https://raw.githubusercontent.com/ARM-software/astc-encoder/main/Source/astcenc_find_best_partitioning.cpp>
  - <https://raw.githubusercontent.com/ARM-software/astc-encoder/main/Test/astc_test_image.py>
  - <https://raw.githubusercontent.com/ARM-software/astc-encoder/main/Test/testlib/encoder.py>
  - <https://raw.githubusercontent.com/ARM-software/astc-encoder/main/Test/testlib/resultset.py>
  - <https://raw.githubusercontent.com/ARM-software/astc-encoder/3.7/Docs/ChangeLog-2x.md>
  - <https://raw.githubusercontent.com/ARM-software/astc-encoder/3.7/Test/testlib/encoder.py>
  - <https://raw.githubusercontent.com/ARM-software/astc-encoder/2.0/Test/testlib/encoder.py>
  - <https://raw.githubusercontent.com/ARM-software/astc-encoder/2.0/Test/astc_test_image.py>
  - <https://raw.githubusercontent.com/ARM-software/astc-encoder/2.0/Source/Makefile>
  - <https://raw.githubusercontent.com/ARM-software/astc-encoder/1.7/Source/Makefile>
  - <https://github.com/ARM-software/astc-encoder/tree/main/Test>
  - <https://github.com/ARM-software/astc-encoder/issues?q=is%3Aissue+performance>
  - <https://github.com/ARM-software/astc-encoder/issues/501>
  - <https://github.com/ARM-software/astc-encoder/issues/672>
  - WebSearch: astcenc vs ISPCTextureCompressor ASTC encoder speed comparison (snippets of developer.arm.com 'astcenc 3.1' blog and cse.chalmers.se Daniel Oom thesis; pages not opened)
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/arm-software/astc-encoder`) · [data/wave10/enrich/raw/github_com_arm_software_astc_encoder.json](../../../data/wave10/enrich/raw/github_com_arm_software_astc_encoder.json) (enrichment confidence 0.8)

</details>
