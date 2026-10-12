# Basis Universal (bc7f and etc1f real-time encoders)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Portable scalar C++ real-time BC7 (bc7f) and ETC1 (etc1f) block encoders; claimed several times faster than bc7e.ispc level 1, unmeasured.

| | |
|---|---|
| **Beats** | bc7e.ispc level 1 (BC7); etcpak and rg_etc1 (ETC1) |
| **Claimed result** | Directional only, no numbers. Wiki: 'Even without any SIMD, bc7f is several times faster than our bc7e.ispc encoder at level 1, with a slightly lower average PSNR' and 'bc7f is essentially like bc7e.ispc level \~.8'; 'etc1f is significantly faster and more portable than etcpak, with substantially higher visual quality' and 'significantly faster than ... rg_etc1'. v2.0 release notes: bc7f and etc1f are 'significantly faster than other SIMD encoders, including our own previous SIMD encoders such as bc7e.ispc'. |
| **Workload** | Analytical, non-SIMD real-time BC7 (bc7f) and ETC1 (etc1f) block encoders in the transcoder module; no benchmark figures given. |
| **Metric** | throughput |
| **Adoption** | 3.1k stars |
| **Last commit** | 2026-09-01 |
| **Links** | [repository](https://github.com/BinomialLLC/basis_universal) · [benchmark](https://raw.githubusercontent.com/wiki/BinomialLLC/basis_universal/Transcoder-Internals-Analytical-Real-Time-Encoders-and-Transcoders.md) |

## Verdict

No measurement exists. The wiki, which embeds the January 2026 bc7f blog post, and the v2.0 release notes state without numbers that bc7f is several times faster than bc7e.ispc level 1 at slightly lower average PSNR, and that etc1f beats etcpak and rg_etc1 on speed. No machine, compiler, image set or harness is named. The repo's basisu -benchmark_single/-benchmark_sweep modes can time XUBC7 encoding with bc7f against bc7e_scalar (the C++ port), but not against bc7e.ispc, etcpak or rg_etc1, and no results are checked in.

## Use it when

- You already ship Basis Universal's transcoder and need BC7 or ETC1 output at load time, for example XUASTC/ASTC to BC7, DDS to ETC1, or BC7 to ASTC 4x4 fallbacks.
- Real-time or per-frame BC7 encoding of runtime-generated textures (render targets, procedural or streamed content) where a bounded cost per block matters more than the last dB.
- Targets without x86 SIMD or ISPC, such as WebAssembly, ARM or consoles: bc7f is plain scalar C++, and its SSE4.1 path is compiled out by default.
- You want the whole BC7 mode set (2/3 subsets, dual plane, all partitions) from a fast encoder instead of a mode-6-only fast path, and can choose flags from fastest (mode 6 only) up to partially or non-analytical.

## Skip it when

- You need measured throughput: no Mpix/s, hardware or harness is published for bc7f or etc1f. Benchmark them against bc7e, etcpak or Goofy yourself before relying on 'several times faster'.
- Offline asset baking where quality matters: bc7f trades PSNR for speed (the wiki says it behaves like bc7e.ispc level \~0.8), and its fully analytical mode is lower quality than its own partially analytical mode. bc7e_scalar or bc7e.ispc give a higher quality ceiling.
- Perceptual or channel-weighted BC7: the XUBC7 guide says bc7f supports neither channel weights nor perceptual metrics.
- A stable public API: the encoders sit in the internal header, need the whole transcoder translation unit (about 46k lines) with BASISD_SUPPORT_XUASTC enabled, and the wiki says the signatures may change.
- Windows on 32-bit ARM with MSVC: open issue #465 reports unresolved __popcnt/__popcnt16 link errors, one of them in bc7f's pick_3subset_pat_index.

## How it is fast

bc7f predicts instead of searching. From the block's integer covariance, per-channel variances and pairwise Pearson correlations it estimates line-fit error (trace minus the largest eigenvalue) plus closed-form endpoint and weight quantisation error for each mode family (4/5, 0/2, 1/3/7, 6). In fully analytical mode it encodes only the single predicted configuration, with no trial decode. Early exits handle solid blocks (mode 5) and low-variance blocks (a trivial mode 6 path). It does not search partitions per pattern: it estimates 3-subset patterns with popcount over subset bitmasks. etc1f picks the flip orientation from per-half luma and chroma deviations, uses precomputed tables for solid colours, and sends near-grey blocks to a dedicated grayscale packer.

## Compared with alternatives

Pick bc7f over bc7e when you need BC7 without ISPC or SIMD (WASM, ARM, inside a transcoder) and can accept slightly lower PSNR. Pick bc7e when quality per second on x86 AVX2 matters and you can use its independently measured profiles. For ETC1, etcpak and Goofy have published throughput (QuickETC2 paper; Goofy's own table), while etc1f has only the claim that it is faster with better quality on smooth blocks.

## Integration

| | |
|---|---|
| **Form** | source-drop (single-file transcoder transcoder/basisu_transcoder.cpp plus headers) or the CMake-built basisu library |
| **Dependencies** | none for bc7f/etc1f; the transcoder optionally uses bundled Zstd for Zstd-based codecs |
| **Minimum toolchain** | C++17 (README: newer standards 'not supported by us yet'); compile with -fno-strict-aliasing as the CMakeLists.txt requires |
| **Platforms** | any (scalar C++); native, WASM/WASI and WASM64 builds are provided; MSVC ARM32 currently fails to link (issue #465) |
| **Thread safety** | Call basist::basisu_transcoder_init() once before starting threads: it fills global tables behind an unsynchronised bool. After that, bc7f calls are stateless and can run in parallel. etc1f needs one pack_etc1_state per thread (it caches the last solid block). |
| **Drop-in for the baseline** | no |

## Gotchas

- Encoding before basisu_transcoder_init() reads uninitialised tables: bc7f only assert()s, so in release builds the output is silently wrong.
- The default flags (cPackBC7FlagDefault) include cPackBC7FlagPBitOptMode6, whose own comment says opaque blocks may decode with alpha 254. Leave that flag out if exact 255 alpha matters.
- The solid-block checks compare whole RGBA words through uint32_t casts. Use fast_pack_bc7_auto_rgba, or guarantee A=255, before calling the RGB-only entry points.
- etc1f encodes blocks with very low chroma energy (sum of (r-g)^2+(b-g)^2 under 300 and every pixel under 32) as pure grey, which removes faint tints.

## Known shortcomings

- Tier D: the bc7f and etc1f real-time encoders have only directional claims ('several times faster' than bc7e.ispc level 1, 'significantly faster' than etcpak and rg_etc1) across the wiki, README, v2.0 release notes and issues, with no machine, timings or harness; the author's blog is blocked here. Internal API, slightly lower PSNR than the slow encoders; baselines are texture encoders outside the category list.
- No number anywhere for bc7f or etc1f (tier D). bc7f is scalar by default (the SSE4.1 path is compiled out), its APIs are internal, it has no perceptual metric or channel weights, and default flags allow alpha 254 on opaque blocks; the library must be compiled with -fno-strict-aliasing and its init is not thread-safe; open issue #465 (MSVC ARM32 link failure in bc7f pick_3subset_pat_index). basisu -benchmark_single can time bc7f against bc7e_scalar only, and no results are published.

## Caveats and trade-offs

First-party directional claim with no numbers, machine, compiler or benchmark harness anywhere reachable (README, wiki Transcoder Internals page with its embedded copy of the bc7f blog post, wiki Release Notes, GitHub releases, issues, and the bc7e and bc7enc_rdo READMEs that point to bc7f as 'an even faster alternative'). The original blog post on richg42.blogspot.com is blocked here; the wiki copy has no figures. bc7f trades slightly lower average PSNR than bc7e.ispc level 1 for speed, and its default XUBC7 use runs in partially analytical mode. The encoders are internal transcoder APIs (transcoder/basisu_transcoder.cpp) that the authors say may change at any time; they require basist::basisu_transcoder_init() first. Not a duplicate of bc7e or etcpak: bc7f and etc1f are separate, newer non-SIMD encoders. Texture encoders have baselines outside the category list.

bc7f is portable (no SIMD needed), strictly bounded O(1) per block and thread-safe, and uses the whole BC7 format; fully analytical mode gives a lower PSNR than the partially analytical mode. Encoders live in the single-file transcoder basisu_transcoder.cpp.

## Maintenance

Actively maintained (v2.5, last commit 2026-09-01, 3.1k stars, 87 open issues) under Apache-2.0 and copyable, but bc7f and etc1f are internal transcoder APIs that are about nine months old (added in v2.0, 2026-01-19).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification D, tier now D.
- **Tier reason:** The wiki page (which embeds a copy of the bc7f blog post) states directionally that bc7f is 'several times faster' than bc7e.ispc level 1 and that etc1f is 'significantly faster' than etcpak and rg_etc1, but gives no timings, machine or harness. The README, the wiki Release Notes (v2.0, 2026-01-19: 'significantly faster than other SIMD encoders, including ... bc7e.ispc'), the release pages, the issue tracker and the bc7e and bc7enc_rdo READMEs carry no numbers either, so the claim stays directional (tier D).
- **Verifier notes:** Kept at tier D as a notable project (3.1k stars, Apache-2.0, last commit 2026-09-01). License, stars, last commit and baseline_in_list false were confirmed; baseline extended to include rg_etc1, which the wiki also names. Tier B or better would need an independent timing (none found via 2 WebSearch queries).
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/wiki/BinomialLLC/basis_universal/Transcoder-Internals-Analytical-Real-Time-Encoders-and-Transcoders.md>
  - <https://raw.githubusercontent.com/wiki/BinomialLLC/basis_universal/Transcoder-Internals-Analytical-Real-Time-Encoders.md>
  - <https://raw.githubusercontent.com/wiki/BinomialLLC/basis_universal/Release-Notes.md>
  - <https://raw.githubusercontent.com/wiki/BinomialLLC/basis_universal/Home.md>
  - <https://raw.githubusercontent.com/wiki/BinomialLLC/basis_universal/XUBC7-Usage-Guide.md>
  - <https://raw.githubusercontent.com/wiki/BinomialLLC/basis_universal/DDS-Transcoder.md>
  - <https://raw.githubusercontent.com/BinomialLLC/basis_universal/HEAD/README.md>
  - <https://github.com/BinomialLLC/basis_universal>
  - <https://github.com/BinomialLLC/basis_universal/wiki>
  - <https://github.com/BinomialLLC/basis_universal/releases>
  - <https://github.com/BinomialLLC/basis_universal/commits/master>
  - <https://github.com/BinomialLLC/basis_universal/issues?q=bc7f>
  - <https://raw.githubusercontent.com/BinomialLLC/bc7e/HEAD/README>
  - <https://raw.githubusercontent.com/richgel999/bc7enc_rdo/HEAD/README.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/BinomialLLC/basis_universal/HEAD/README.md>
  - <https://raw.githubusercontent.com/BinomialLLC/basis_universal/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/BinomialLLC/basis_universal/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/BinomialLLC/basis_universal/HEAD/transcoder/basisu_transcoder.cpp>
  - <https://raw.githubusercontent.com/BinomialLLC/basis_universal/HEAD/transcoder/basisu_transcoder_internal.h>
  - <https://raw.githubusercontent.com/BinomialLLC/basis_universal/HEAD/transcoder/basisu_transcoder.h>
  - <https://raw.githubusercontent.com/BinomialLLC/basis_universal/HEAD/basisu_tool.cpp>
  - <https://raw.githubusercontent.com/BinomialLLC/basis_universal/HEAD/basisu_tool_test_codecs.inl>
  - <https://raw.githubusercontent.com/wiki/BinomialLLC/basis_universal/Transcoder-Internals-Analytical-Real-Time-Encoders-and-Transcoders.md>
  - <https://raw.githubusercontent.com/wiki/BinomialLLC/basis_universal/Release-Notes.md>
  - <https://raw.githubusercontent.com/wiki/BinomialLLC/basis_universal/Home.md>
  - <https://raw.githubusercontent.com/wiki/BinomialLLC/basis_universal/XUBC7-Usage-Guide.md>
  - <https://github.com/BinomialLLC/basis_universal>
  - <https://github.com/BinomialLLC/basis_universal/commits/master>
  - <https://github.com/BinomialLLC/basis_universal/issues?q=bc7f>
  - <https://github.com/BinomialLLC/basis_universal/issues/465>
  - <https://raw.githubusercontent.com/BinomialLLC/bc7e/HEAD/README>
  - <https://raw.githubusercontent.com/richgel999/bc7enc_rdo/HEAD/README.md>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/binomialllc/basis_universal`) · [data/wave10/enrich/raw/github_com_binomialllc_basis_universal.json](../../../data/wave10/enrich/raw/github_com_binomialllc_basis_universal.json) (enrichment confidence 0.6)

</details>
