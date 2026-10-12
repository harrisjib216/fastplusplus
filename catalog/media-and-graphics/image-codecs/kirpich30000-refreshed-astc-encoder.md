# refreshed-astc-encoder

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `ARM End User Licence Agreement for the Mali ASTC Specification and Software Codec, version 1.3 (license.txt): non-OSI, use limited to the 'Authorised Purpose' of ASTC compression tools, no right to develop hardware; not Apache-2.0` · 🔴 abandoned

> 2016 fork of ARM's 2015 astcenc 1.x CLI that reuses scratch buffers per thread; 1.2x-2.2x faster on one image, superseded.

| | |
|---|---|
| **Beats** | Mali GPU Texture Compression Tool astcenc binary (32-bit) and ARM astc-encoder official repo build (64-bit, 2015 era) |
| **Claimed result** | README: 'about 2x faster than the Mali TCT binary and about 1.5x faster than the one from official repo'. Table for turret_diffuse_map.png on Intel Core i5 760 (seconds, Mali TCT 32-bit / official astcenc 64-bit / refreshed 64-bit): veryfast 0.41/0.39/0.19; fast 1.04/0.86/0.40; medium 6.11/4.36/3.20; thorough 22.90/14.98/11.54; exhaustive 52.56/30.99/25.23. Against the official 64-bit astcenc: 2.05x veryfast, 2.15x fast, 1.36x medium, 1.30x thorough, 1.23x exhaustive; against Mali TCT 1.91x-2.60x (derived from page data). The README's '1.5x' is about right only as an average: the slower, higher-quality presets gain 1.23x-1.36x. |
| **Workload** | ASTC compression time of turret_diffuse_map.png at five speed presets (veryfast to exhaustive). |
| **Metric** | throughput |
| **Hardware** | Intel Core i5 760 |
| **Adoption** | 1 star (fork chain: ARM-software/astc-encoder, then Kirpich30000, then abusenius) |
| **Last commit** | 2016-06-12 |
| **Links** | [repository](https://github.com/Kirpich30000/refreshed-astc-encoder) · [benchmark](https://github.com/Kirpich30000/refreshed-astc-encoder) |

## Verdict

One first-party table: wall-clock seconds to compress turret_diffuse_map.png on an Intel Core i5 760, at each 1.x preset. Against the official 64-bit astcenc of the time the fork is 2.05x (veryfast), 2.15x (fast), 1.36x (medium), 1.30x (thorough) and 1.23x (exhaustive) faster; against the 32-bit Mali TCT binary it is 1.91x-2.60x (derived from page data). Block size, thread count (the i5 760 has 4 cores, and the default is autodetect), compiler, flags and output PSNR are not given.

## Use it when

- Reproducing or patching a 2015-2016 Mali TCT / astcenc 1.x pipeline whose command line and output format you must keep, where a 1.2x-2x faster drop-in binary is the only change allowed.
- Studying how much of the old ARM reference encoder's time went to heap churn: the diff is small, and readable as a case study.

## Skip it when

- Any new ASTC work. ARM's own astcenc 2.0 (August 2020) changelog charts show astcenc-avx2 2.0 at roughly 2x-3x the speed of astcenc 1.7 at -thorough and roughly 1.3x-4x at -fast/-medium, with PSNR mostly within about 0.2 dB. That was measured on a Core i5-9600K with 6 threads (chart readings approximate), and the 3.x-5.x releases are faster still. ARM's current encoder is also a library, has SIMD paths and is Apache-2.0.
- Bit-exact reproduction of the original astcenc. Commit 00f9f3d moves 'separate_errors[best_partition] = 1e30f' ahead of the partition_sequence remapping in find_best_partitionings. That changes which dual-plane partition candidates are tried, so output can differ from the binary it claims to replace, and no PSNR comparison is published.
- Commercial or redistributed tooling without legal review. The code is under ARM's Mali ASTC EULA v1.3: use only for the 'Authorised Purpose' of ASTC compression and decompression tools, no hardware development, non-transferable, and the licence must be shipped with any distribution.
- Small textures on many cores. Work is handed out in 128-block batches per thread, so an image with fewer than threads x 128 blocks leaves threads idle unless you lower -batchsize (derived from encode_astc_image_threadfunc).

## How it is fast

There are no algorithmic or SIMD changes; the gains come from housekeeping in ARM's reference encoder. Commit b5a2d16 removed the new/delete of large scratch structures that compress_symbolic_block_fixed_partition_1_plane/2_planes did on every call, for every partition candidate of every block. Each thread now allocates these buffers once. Commit 4766689 wraps them in a SymbolicBatchCompressor, and each thread encodes runs of 128 consecutive blocks instead of ARM's one-block round-robin; compress_symbolic_batch is just a loop over compress_symbolic_block. Commit 991edf8 compiles out the DEBUG_PRINT_DIAGNOSTICS code that upstream enabled by default, removing runtime print_diagnostics branches from the hot path.

## Compared with alternatives

No other ASTC encoder is catalogued yet. The texture-codec siblings (bc7e, bc7enc, etcpak, Goofy, ICBC, Basis Universal) target BC1/BC7/ETC, not ASTC. For ASTC, current ARM astcenc 4.x/5.x beats this fork on speed, quality evidence, licence and API, so pick this fork only when you must stay on the 1.x CLI.

## Integration

| | |
|---|---|
| **Form** | command-line executable (prebuilt Win32/Win64 astcenc.exe in Binary/, or build Source/ with the Makefile or the VS2013 project); no library target |
| **Dependencies** | none beyond pthreads on POSIX (stb_image is vendored) |
| **Minimum toolchain** | Makefile uses g++ -O3 -msse2 -mfpmath=sse with no -std flag. The README says GCC &gt;= 4.6, but the batch code uses astc_decode_mode::DECODE_LDR (scoped access to an unscoped enum), which needs C++11, so use a compiler that defaults to C++11 or later or add -std=c++11. Visual Studio 2013 project for Windows. |
| **Platforms** | x86/x86-64 (Makefile forces -msse2 -mfpmath=sse); Windows binaries checked in; Linux/macOS from source |
| **Thread safety** | multi-threaded internally (-j, defaults to the logical CPU count); each thread owns its SymbolicBatchCompressor scratch buffers; there is no API to call concurrently |
| **Drop-in for the baseline** | partial: same 1.x command line and .astc output format as the Mali TCT/ARM 1.x astcenc, but -diag is removed, -batchsize is new, and dual-plane encodings can differ because of the partition-search fix |

## Gotchas

- The speed numbers are not at matched quality. The README claims 'some quality improvement' but reports no PSNR, even though the tool's own -t -showpsnr mode would have produced it.
- -diag is gone. It prints '-diag switch is unsupported in this version', and defining DEBUG_PRINT_DIAGNOSTICS now trips a static_assert because diagnostics are 'broken in batch mode'.
- The 'official astcenc (64-bit)' column is the October 2015 upstream code, not ARM's last 1.x release (1.7) and not 2.x or later. Its build (ARM's checked-in Win64 binary or the author's own) and compiler are not stated.

## Known shortcomings

- Licence is the ARM Mali ASTC codec EULA v1.3, not Apache-2.0: reference only. 1.23x-2.15x vs the official astcenc (slow presets 1.23-1.36x) with quality not matched (commit 00f9f3d's bug fix changes output; no PSNR); block size, thread count and compiler unstated. 2016 code.
- The speedup comes only from per-thread scratch-buffer reuse, 128-block batches and compiled-out diagnostics (no SIMD or algorithm change); only commit 00f9f3d changes output (dual-plane partition pick). The baseline is the October 2015 upstream code with build and compiler unstated; ARM's own astc-encoder 2.0 is roughly 2-4x over 1.7 at near-equal PSNR (changelog charts), so the incumbent has moved. Builds need C++11 despite the README's GCC 4.6.

## Caveats and trade-offs

Historical 2016 fork of the ARM 1.x evaluation codec; current ARM astc-encoder releases are a rewrite with SIMD and are far faster, so this is mainly an example of optimizing the old reference encoder. Quality is not matched or measured: the README claims 'some quality improvement' but gives no PSNR, and commit 00f9f3d ('Fix for finding best partitionings for 2planes mode') changes which partitions the dual-plane search excludes, so output differs from the baseline. The speedup otherwise comes from per-thread reuse of scratch buffers instead of per-block new/delete (b5a2d16) and batched block processing in encode_astc_image_threadfunc (4766689). One image, one CPU; block size, thread count, compiler and flags are not stated; the Mali TCT comparison is a 32-bit binary against a 64-bit one. Licence is ARM's custom EULA, so reference only. An identical README is in the abusenius/refreshed-astc-encoder fork.

Drop-in replacement for the Mali TCT astcenc binary; claims some quality improvement too. Based on the 2015 astcenc 1.x code line, so the speedup is relative to a very old reference encoder.

## Maintenance

Abandoned since 2016-06-12 (18 commits, 8 by the fork author; 1 star; one downstream fork, abusenius, with no extra commits; no PRs). Reference only: ARM's custom EULA, not Apache-2.0, and the code is the pre-2.0 reference encoder.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The README table times the refreshed binary against ARM's official 64-bit astcenc and the Mali TCT 32-bit binary on one image on an Intel Core i5 760, with no benchmark script, block size, thread count, compiler or flags. First-party, partial methodology: C.
- **Verifier notes:** Table numbers and derived ratios verified against the README. The licence is ARM's Mali ASTC codec EULA v1.3, not Apache-2.0, so usability stays reference. The speed claim is not at matched quality: a search bug fix changes output and no PSNR is reported. Last commit 2016-06-12 (abandoned), 1 star, fork of ARM-software/astc-encoder, all confirmed.
- **Fields the verifier corrected:** `license`, `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/Kirpich30000/refreshed-astc-encoder>
  - <https://github.com/Kirpich30000/refreshed-astc-encoder/commits/master>
  - <https://github.com/Kirpich30000/refreshed-astc-encoder/commit/00f9f3de2d1a5db1f5b06104b41fc6f8fc50b537>
  - <https://github.com/Kirpich30000/refreshed-astc-encoder/commit/44f4c638a75120ce422396c9593ff5e8624c7032>
  - <https://github.com/Kirpich30000/refreshed-astc-encoder/commit/b5a2d168027c8c71cd6814ae43c485b48aced53b>
  - <https://raw.githubusercontent.com/Kirpich30000/refreshed-astc-encoder/HEAD/README.md>
  - <https://raw.githubusercontent.com/Kirpich30000/refreshed-astc-encoder/HEAD/license.txt>
- **Sources the enricher read:**
  - <https://github.com/Kirpich30000/refreshed-astc-encoder>
  - <https://github.com/Kirpich30000/refreshed-astc-encoder/commits/master>
  - <https://github.com/Kirpich30000/refreshed-astc-encoder/commit/00f9f3de2d1a5db1f5b06104b41fc6f8fc50b537>
  - <https://github.com/Kirpich30000/refreshed-astc-encoder/commit/b5a2d168027c8c71cd6814ae43c485b48aced53b>
  - <https://github.com/Kirpich30000/refreshed-astc-encoder/commit/44f4c638a75120ce422396c9593ff5e8624c7032>
  - <https://github.com/Kirpich30000/refreshed-astc-encoder/commit/4766689>
  - <https://github.com/Kirpich30000/refreshed-astc-encoder/commit/991edf8>
  - <https://github.com/Kirpich30000/refreshed-astc-encoder/commit/a0d8c7b>
  - <https://github.com/Kirpich30000/refreshed-astc-encoder/tree/master/Source>
  - <https://github.com/Kirpich30000/refreshed-astc-encoder/tree/master/Binary>
  - <https://github.com/Kirpich30000/refreshed-astc-encoder/pulls?q=is%3Apr>
  - <https://raw.githubusercontent.com/Kirpich30000/refreshed-astc-encoder/HEAD/README.md>
  - <https://raw.githubusercontent.com/Kirpich30000/refreshed-astc-encoder/HEAD/license.txt>
  - <https://raw.githubusercontent.com/Kirpich30000/refreshed-astc-encoder/HEAD/Source/Makefile>
  - <https://raw.githubusercontent.com/Kirpich30000/refreshed-astc-encoder/HEAD/Source/astc_codec_batch.h>
  - <https://raw.githubusercontent.com/Kirpich30000/refreshed-astc-encoder/HEAD/Source/astc_codec_internals.h>
  - <https://raw.githubusercontent.com/Kirpich30000/refreshed-astc-encoder/HEAD/Source/astc_toplevel.cpp>
  - <https://raw.githubusercontent.com/Kirpich30000/refreshed-astc-encoder/HEAD/Source/astc_compress_symbolic.cpp>
  - <https://raw.githubusercontent.com/Kirpich30000/refreshed-astc-encoder/HEAD/Source/astc_find_best_partitioning.cpp>
  - <https://github.com/abusenius/refreshed-astc-encoder>
  - <https://github.com/ARM-software/astc-encoder/tree/main/Docs>
  - <https://raw.githubusercontent.com/ARM-software/astc-encoder/3.7/Docs/ChangeLog-2x.md>
  - <https://raw.githubusercontent.com/ARM-software/astc-encoder/3.7/Docs/ChangeLogImg/relative-1.7-to-2.0.png>
  - <https://raw.githubusercontent.com/daoo/astcrt/HEAD/README.md>
  - WebSearch: ASTC texture encoder faster than astcenc benchmark github (snippets: Phoronix on astcenc 4.0 being 1.2x-1.6x faster than 3.7; astcrt; UnityAstcGpuEncoder)
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/kirpich30000/refreshed-astc-encoder`) · [data/wave10/enrich/raw/github_com_kirpich30000_refreshed_astc_encoder.json](../../../data/wave10/enrich/raw/github_com_kirpich30000_refreshed_astc_encoder.json) (enrichment confidence 0.8)

</details>
