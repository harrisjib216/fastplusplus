# bcdec

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT OR Unlicense` · 🟢 active

> Single-header C BC1-BC7 block decoder; 1.3-11x DirectXTex's single-thread throughput in aras-p's 2022 decoder comparison.

| | |
|---|---|
| **Beats** | DirectXTex BCn decoders (also Compressonator and bc7enc_rdo decoders) |
| **Claimed result** | Independent (aras-p, 2022-06-23, derived from page data): against DirectXTex 679538e on a Ryzen 9 5950X with VS2022, bcdec e3ca0 BC1 1319 vs 272 Mpix/s (4.85x), BC3 704 vs 254 (2.77x), BC6H unsigned 85 vs 25 (3.40x), BC7 142 vs 93 (1.53x); with clang 14 on the same CPU BC1 1449 vs 223 (6.50x), BC3 621 vs 207 (3.00x), BC7 169 vs 127 (1.33x); on an M1 Max with clang 13 BC1 2088 vs 183 (11.4x), BC3 1093 vs 185 (5.91x), BC7 220 vs 140 (1.57x). Not the fastest everywhere: bc7enc_rdo's bc7decomp is 2.3-4.4x faster on BC7, etcpak 1.16-1.7x faster on BC1/BC3, and on the M1 bcdec's BC6H is behind ConvectionKernels, SwiftShader and Mesa. First-party PR #1 before/after: BC1 821 to 1327, BC3 516 to 694, BC6H 65 to 85, BC7 91 to 143 Mpix/s (VS2022, 5950X). |
| **Workload** | BC1, BC3, BC6H and BC7 block decompression speed in Mpix/s; the only numbers opened are before/after figures for bcdec's own optimization, not a cross-library table. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 5950X (Windows) and Apple M1 Max (macOS), single-threaded, 20 runs per file. |
| **Compiler and flags** | Windows: Visual Studio 2022 (cl) and clang 14 (clang-cl), bcn_decoder_tester preset RelWithDebInfo plus /Ob2; macOS: clang 13, flags not given in the presets. bcdec commit e3ca0 vs DirectXTex 679538e, submodules pinned in the harness. |
| **Adoption** | 192 stars, 26 forks |
| **Last commit** | 2026-09-02 |
| **Links** | [repository](https://github.com/iOrange/bcdec) · [benchmark](https://github.com/aras-p/bcn_decoder_tester) |

## Verdict

aras-p's 'Comparing BCn texture decoders' (2022-06-23) is a third-party, single-threaded Mpix/s comparison; the post's source and chart PNGs are readable in the public aras-p/aras-p.hugo repo. The harness is public (aras-p/bcn_decoder_tester: 20 runs per DDS file, pinned submodules, test_images in the repo; Windows preset RelWithDebInfo plus /Ob2 with cl or clang-cl). Against DirectXTex (679538e), bcdec (e3ca0) measured BC1 1319 vs 272 (4.85x), BC3 704 vs 254 (2.77x), BC6H unsigned 85 vs 25 (3.40x) and BC7 142 vs 93 (1.53x) on a Ryzen 9 5950X with VS2022. With clang 14 on the same CPU: BC1 1449 vs 223 (6.50x), BC3 621 vs 207 (3.00x), BC7 169 vs 127 (1.33x). On an M1 Max with clang 13: BC1 2088 vs 183 (11.4x), BC3 1093 vs 185 (5.91x), BC7 220 vs 140 (1.57x). All ratios are derived from page data. Two caveats: the harness only warns on output-hash mismatch, and the measured bcdec had small rounding differences (BC1 off by up to 1 per channel; alpha bias +1) that were fixed in 2024 with integer operations of the same cost. The Mac build flags are not given in the presets.

## Use it when

- CPU-side decoding of BCn textures (asset pipelines, texture viewers, compression-quality evaluation, software fallbacks for GPUs without BCn support) where you want every format, including BC6H signed and unsigned, from one 1,500-line header.
- Replacing DirectXTex's decoders outside Windows: no DirectXMath, DirectX-Headers or sal.h stubs needed, and it ran 4.85-11.4x faster on BC1 and 1.3-1.6x faster on BC7 in the 2022 single-thread comparison.
- Embedding in C or C++ projects with strict dependency or licence rules: one header, no runtime library calls, MIT or Unlicense.
- Multi-threaded decoding where you split the image into block ranges yourself: the functions keep no state between calls.

## Skip it when

- BC7-heavy workloads where decode speed matters: bc7enc_rdo's bc7decomp was 2.3-4.4x faster than bcdec on BC7 in the same 2022 charts (517 vs 220 Mpix/s on M1 Max, 621 vs 142 on a 5950X with VS2022).
- Maximum BC1/BC3 throughput: etcpak's decoder was 1.16-1.7x faster on BC1 and BC3 in the same charts. It is harder to extract, though.
- BC6H on Apple Silicon: in the 2022 M1 Max chart, bcdec (79 Mpix/s) trailed ConvectionKernels (149), SwiftShader (143) and Mesa (84). PR #8 (Sep 2022) sped BC6H up after those charts, and that change was not re-measured.
- When you need bit-exact agreement with an older bcdec build or with a float reference. BC1 interpolation was off by up to 1 per channel until the June 2024 fix (issue #15). BC3/BC4/BC5 alpha rounding was changed in November 2024 (issue #12): BC3 alpha now truncates, and float-matching rounding needs BCDEC_BC4BC5_PRECISE.
- Big-endian hosts, or when you need whole-image or DDS handling: the output stores pack 0xAABBGGRR as native 32-bit words, and edge blocks and padding are the caller's job.

## How it is fast

It is plain scalar C with no SIMD. The speed comes from doing the work at word level instead of byte level (aras-p's PR #1): each block is loaded as 16/32/64-bit little-endian words, BC1 builds a 4-entry 32-bit RGBA palette and writes each pixel with one 32-bit store, and BC4/BC5 alpha indices are pulled from a 64-bit word 3 bits at a time. BC6H and BC7 use a two-word (128-bit) bitstream reader instead of per-bit extraction, plus hard-coded partition and fix-up tables. BC6H endpoint unquantization was moved out of the per-pixel loop (PR #8). BC1 palette interpolation uses multiply-shift 'magic' constants on the 5/6-bit endpoints instead of division (issue #15). DirectXTex, by contrast, decodes every texel through float XMVECTOR math and then packs back to 8-bit.

## Compared with alternatives

None of the catalogued image-codecs siblings (ffpng, fpng, QOI, libspng and others) decodes GPU block formats. Among block-texture entries, pick bcdec over etcpak or bc7enc_rdo's decoders when you want every BCn format, including BC2, BC4/BC5 signed and BC6H, in one header, and use those two only for peak BC1/BC3 (etcpak) or BC7 (bc7decomp) speed.

## Integration

| | |
|---|---|
| **Form** | header-only (stb style: define BCDEC_IMPLEMENTATION in one translation unit; BCDEC_STATIC or BCDECDEF control linkage) |
| **Dependencies** | none (no C runtime calls) |
| **Minimum toolchain** | C with 64-bit unsigned long long (C99 or C++11 era compilers); built by MSVC 2022, clang 13/14 and GCC in the public harnesses |
| **Platforms** | any little-endian target; scalar code, no SIMD or intrinsics; since 2026-09-02 input blocks may be unaligned |
| **Thread safety** | Not documented. Functions keep no state; the static tables (partition sets, weights) are only read, so concurrent calls on different blocks are safe in practice. |
| **Drop-in for the baseline** | partial — same per-block job as DirectXTex's D3DXDecodeBC1..BC7, but different signatures (raw bytes out with a row pitch instead of 16 XMVECTOR floats), so call sites need small rewrites |

## Gotchas

- Pitch units differ by function: bytes for the 8-bit formats, but float or half elements for bcdec_bc6h_float and bcdec_bc6h_half (and for the BC4/BC5 float variants). The bcn_decoder_tester call passes width \* 3 for BC6H float.
- BCDEC_\*_COMPRESSED_SIZE(w, h) computes (w&gt;&gt;2)\*(h&gt;&gt;2) blocks, so it returns 0 for a 256x1 image and undercounts any size that is not a multiple of 4. Round dimensions up yourself. Issues #7 (tiny images) and #18 (256x1 BC3 crash) were in this area.
- Output pixels are written through unsigned int, unsigned short and float pointers, so destination rows should be naturally aligned. Unaligned input reads were only fixed on 2026-09-02 (commit 80859ed, prompted by PR #23): DX10-header DDS payloads start at byte 148 and are never 8-byte aligned. Older copies are formally undefined behaviour there and fault on strict-alignment CPUs.
- The maintainer rejects LLM-generated contributions (README; PR #23 was declined for that reason), so plan to carry local patches yourself if needed.

## Known shortcomings

- Tier D: the only numbers are a before-and-after of its own code in PR #1; the cross-decoder chart there sits on user-images.githubusercontent.com (blocked) and aras-p/bcn_decoder_tester has a harness (src/main.cpp) but no committed results, with search snippets conflicting on which decoder is fastest. Retier candidate when aras-p.info is reachable.
- Enricher (e109, 2026-10-05): aras-p's independent 2022 comparison is readable through the aras-p.hugo repo and its harness is public (bcn_decoder_tester, pinned submodules, RelWithDebInfo plus /Ob2, Ryzen 9 5950X VS2022/clang 14, M1 Max clang 13): bcdec 1.33-11.4x faster than DirectXTex, but bc7enc_rdo's decoder is 2.3-4.4x faster on BC7, etcpak 1.16-1.7x faster on BC1/BC3, and BC6H on the M1 is behind ConvectionKernels, SwiftShader and Mesa. The measured e3ca0 had rounding bugs fixed in 2024 with same-cost operations (BC1 off by up to 1 per channel, #15; alpha +1 bias, #12) and the harness only warns on hash mismatch, so the tier is capped at C by the measured-on-later-fixed-code rule (retier-32, D to C).

## Caveats and trade-offs

No cross-library figure could be opened. aras-p's independent 'Comparing BCn texture decoders' (2022-06-23) is blocked here; its code is public at https://github.com/aras-p/bcn_decoder_tester (src/main.cpp times each decoder over kRuns and checks output hashes; libraries amd_cmp, bc7enc_rdo, bcdec, convection, DirectXTex, icbc, etcpak, mesa, squish, swiftshader) but the repo carries no results table. PR #1 embeds a 'sneak peek' cross-decoder chart (bcdec vs bcdec_opt vs others) as an image on user-images.githubusercontent.com, which is egress-blocked; its text says only that the change 'makes it one of the fastest BCn decoders out there'. Search snippets of the blog disagree: one says bcdec is 'easiest to use and almost always the fastest one' with up to 20x spread between libraries, another says bc7enc_rdo's decoder is fastest for BC7 and etcpak for BC1/BC3 (possibly before and after the post's update); snippet only, no figures. Needs a re-check from an environment that reaches aras-p.info or the PR image: the table (Ryzen 5950X VS2022 and M1 Max Clang 13 per PR #1) with the public harness may support tier A or B against DirectXTex and Compressonator. The README disclaims speed as a goal ('never optimized specifically for speed but for the overall size'). Tier D here; kept because the seed list asked for it. [retier] Independent harness and post by aras-p (source readable at raw.githubusercontent.com/aras-p/aras-p.hugo, content/blog/2022/06-bcn-decode-libraries.md; chart PNGs under static/img/blog/2022/). The measured bcdec e3ca0 had small rounding bugs later fixed with same-cost operations (BC1 off by up to 1 per channel, issue #15; alpha +1 bias, issue #12), and the harness only warns on output-hash mismatch, so speed was not inflated but the numbers predate the fixes (tier capped at C by project rule). bcdec is not the fastest decoder for BC7 (bc7enc_rdo 2.3-4.4x faster) or BC1/BC3 (etcpak 1.16-1.7x faster). The README disclaims speed as a goal.

Single-header C, no allocation, no external dependencies, minimal stack; BC1-BC7 including BC6H (float or half output). README says it was 'never optimized specifically for speed but for the overall size'. Dual licensed MIT or Unlicense.

## Maintenance

Active (last commit 2026-09-02, alignment fix); single-header and MIT OR Unlicense, so it is trivially vendorable. Pin a version, because decoded values changed slightly in the 2024 rounding fixes.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification D, tier now C.
- **Tier reason:** PR #1's numbers are bcdec before and after aras-p's optimization (no external decoder figure in text); the cross-library chart embedded in PR #1 (user-images.githubusercontent.com) and the blog table are blocked, and aras-p/bcn_decoder_tester has the harness (src/main.cpp, kRuns loop with output-hash check) but no results file, so no number against DirectXTex or any other decoder could be read.
- **Retiered** D to C: Raised D to C. Enricher e109 (2026-10-05) reached aras-p's independent 'Comparing BCn texture decoders' (2022-06-23) through the public aras-p/aras-p.hugo repo (content/blog/2022/06-bcn-decode-libraries.md and static/img/blog/2022/bcn-decode-\*.png): a public harness (aras-p/bcn_decoder_tester, pinned submodules, 20 runs per DDS file, Windows preset RelWithDebInfo plus /Ob2), Ryzen 9 5950X with VS2022 and clang 14, M1 Max with clang 13, bcdec e3ca0 against DirectXTex 679538e and others. That would support A on Windows, but the measured bcdec e3ca0 had rounding bugs later fixed (BC1 off by up to 1 per channel, issue #15; alpha +1 bias, issue #12; fixed 2024 with same-cost integer operations) and the harness only warns on hash mismatch, so under the project rule for numbers measured on code later fixed for correctness it stays at C. A re-run of the public harness on current bcdec would make it A.
- **Verifier notes:** PR #1 numbers verified verbatim (merged 2022-06-23). Metadata matches: MIT OR Unlicense (LICENSE alternatives A and B; Unlicense is a public-domain dedication, no patent grant on that branch), 192 stars, 26 forks, 33 commits, last commit 2026-09-02, active. Best candidate for a later retier once aras-p.info or the PR #1 chart image is reachable.
- **Fields the verifier corrected:** `caveats`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `benchmark_url`
- **Shortcomings recorded by:** independent harness (aras-p)
- **Pages the verifier opened:**
  - <https://github.com/iOrange/bcdec>
  - <https://github.com/iOrange/bcdec/commits>
  - <https://github.com/iOrange/bcdec/pull/1>
  - <https://raw.githubusercontent.com/iOrange/bcdec/HEAD/README.md>
  - <https://raw.githubusercontent.com/iOrange/bcdec/HEAD/LICENSE>
  - <https://github.com/aras-p/bcn_decoder_tester>
  - <https://raw.githubusercontent.com/aras-p/bcn_decoder_tester/HEAD/readme.md>
  - <https://raw.githubusercontent.com/aras-p/bcn_decoder_tester/HEAD/src/main.cpp>
  - <https://raw.githubusercontent.com/aras-p/bcn_decoder_tester/HEAD/CMakeLists.txt>
- **Sources the enricher read:**
  - <https://github.com/iOrange/bcdec>
  - <https://raw.githubusercontent.com/iOrange/bcdec/HEAD/README.md>
  - <https://raw.githubusercontent.com/iOrange/bcdec/HEAD/bcdec.h>
  - <https://raw.githubusercontent.com/iOrange/bcdec/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/iOrange/bcdec/e3ca0/bcdec.h>
  - <https://raw.githubusercontent.com/iOrange/bcdec/026acf9/bcdec.h>
  - <https://github.com/iOrange/bcdec/commits>
  - <https://github.com/iOrange/bcdec/issues?q=is%3Aissue>
  - <https://github.com/iOrange/bcdec/pulls?q=is%3Apr>
  - <https://github.com/iOrange/bcdec/pull/1>
  - <https://github.com/iOrange/bcdec/pull/16>
  - <https://github.com/iOrange/bcdec/pull/23>
  - <https://github.com/iOrange/bcdec/issues/12>
  - <https://github.com/iOrange/bcdec/issues/15>
  - <https://github.com/iOrange/bcdec/issues/18>
  - <https://github.com/iOrange/bcdec/issues/19>
  - <https://github.com/aras-p/bcn_decoder_tester>
  - <https://raw.githubusercontent.com/aras-p/bcn_decoder_tester/HEAD/readme.md>
  - <https://raw.githubusercontent.com/aras-p/bcn_decoder_tester/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/aras-p/bcn_decoder_tester/HEAD/CMakePresets.json>
  - <https://raw.githubusercontent.com/aras-p/bcn_decoder_tester/HEAD/src/main.cpp>
  - <https://github.com/aras-p?tab=repositories&q=blog>
  - <https://github.com/aras-p/aras-p.hugo>
  - <https://github.com/aras-p/aras-p.hugo/tree/master/content>
  - <https://github.com/aras-p/aras-p.hugo/tree/master/content/blog>
  - <https://github.com/aras-p/aras-p.hugo/tree/master/content/blog/2022>
  - <https://raw.githubusercontent.com/aras-p/aras-p.hugo/master/content/blog/2022/06-bcn-decode-libraries.md>
  - <https://raw.githubusercontent.com/aras-p/aras-p.hugo/master/static/img/blog/2022/bcn-decode-mac.png>
  - <https://raw.githubusercontent.com/aras-p/aras-p.hugo/master/static/img/blog/2022/bcn-decode-win-vs2022.png>
  - <https://raw.githubusercontent.com/aras-p/aras-p.hugo/master/static/img/blog/2022/bcn-decode-win-clang14.png>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/iorange/bcdec`) · [data/wave10/enrich/raw/github_com_iorange_bcdec.json](../../../data/wave10/enrich/raw/github_com_iorange_bcdec.json) (enrichment confidence 0.85)

</details>
