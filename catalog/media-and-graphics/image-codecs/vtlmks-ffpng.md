# ffpng

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `MIT` · 🟢 active

> Single-header C PNG decoder for x86-64-v3 (AVX2) that decodes 1.12-1.20x faster than image-png, the Rust png crate.

| | |
|---|---|
| **Beats** | image-rs/image-png v0.18.1 (commit 4ab5484; the Rust png crate, already listed) built with --features=unstable at target-cpu=x86-64-v3. The same harness also times libpng + zlib, libspng, stb_image and ldpng (ffpng's front end with libdeflate inflate), but the README publishes no libpng, libspng or stb_image numbers |
| **Claimed result** | Overall 1.115x faster than image-png on a Ryzen 7950X (356.3 vs 319.5 MP/s geomean) and 1.204x faster on a Ryzen 9950X3D (352.6 vs 292.8 MP/s); faster in all 13 categories, from 1.024x (photo_wikipedia, 9950X3D) to 1.827x (screenshot_web, 9950X3D). README says decode speed is about 3% ahead on dense photographs. |
| **Workload** | PNG decode of the whole QOI benchmark suite (2848 images in 13 categories), single core pinned at real-time priority with boost off, geometric mean MP/s and per-image ratio against image-png, output checked byte for byte. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 7950X and Ryzen 9 9950X3D, one isolated core (isolcpus, nohz_full), taskset plus chrt -f 99, CPU boost off |
| **Compiler and flags** | gcc 16.1 (7950X run) and gcc 16.2.1 (9950X3D run) with -std=c99 -O2 -march=x86-64-v3 -mbmi -mbmi2 -mpclmul -falign-functions=32 -falign-loops=64:47 -funroll-all-loops -fno-plt -fwrapv -fno-stack-protector -fno-pie -fcf-protection=none -ffunction-sections -fdata-sections -fno-unwind-tables -fno-asynchronous-unwind-tables (build.sh). image-png via cargo +nightly release build with opt-level=3, lto=true, codegen-units=1, panic=abort and rustflags target-cpu=x86-64-v3 (ext/shim/Cargo.toml, ext/shim/.cargo/config.toml); the nightly is named only for the follow-up (1.98.0-nightly c1b22f44c). README says clang builds of ffpng run about 10% slower |
| **Adoption** | 0 stars |
| **Last commit** | 2026-09-25 |
| **Links** | [repository](https://github.com/vtlmks/ffpng) · [benchmark](https://github.com/vtlmks/ffpng) |

## Verdict

bench.c times ffpng and unmodified image-png v0.18.1 (commit 4ab5484, nightly, unstable feature, x86-64-v3, LTO) in one process on the 2848-image QOI benchmark suite, on one isolated core with boost off, taking the per-image median and checking every output with memcmp. Geomean results are 356.3 vs 319.5 MP/s (1.115x) on a Ryzen 9 7950X with gcc 16.1, and 352.6 vs 292.8 MP/s (1.204x) on a Ryzen 9 9950X3D with gcc 16.2.1; the README ties only the 9950X3D run to the current header (2026-09-25). The timed region is not symmetric: image-png's shim zero-fills its output buffer (vec![0u8; size]) on every decode, while ffpng mallocs its output uninitialized and reuses a thread-local raw buffer (it does pay for copying all IDAT data). That cost is not measured separately, but it could be a sizeable part of the 2-4% margin on the dense photo sets; it is too small to account for the 1.115x/1.204x overall result.

## Use it when

- C or C++ code on x86-64-v3 machines (Intel Haswell and later, AMD Zen and later) that decodes many PNGs and is bound by decode throughput.
- Screenshot, UI, icon and texture-heavy workloads: the README shows 1.57-1.83x over image-png on screenshot_web, 1.14x on screenshot_game and 1.10-1.31x on texture sets.
- You want one vendorable header with no zlib or libpng dependency and pluggable FFPNG_MALLOC/REALLOC/FREE allocator hooks.
- Long-lived worker threads decoding batches, where the thread-local scratch buffer is reused instead of reallocated.
- You build with gcc, which is what the published numbers use.

## Skip it when

- ARM, RISC-V or pre-AVX2 x86: the header targets x86-64-v3 with AVX2, BMI2 and PCLMUL intrinsics and has no runtime CPU detection or scalar fallback.
- MSVC builds (it relies on __builtin_add_overflow, __builtin_expect, __attribute__ and _Thread_local), or clang builds, which the README says run about 10% slower; that would cut the 7950X margin to roughly 1.01x (derived from page data).
- Untrusted input without sandboxing: no fuzzing or malformed-file test suite is documented, there is no caller-set memory or dimension limit (IHDR sizes up to 2^31-1 per side drive the output and raw allocations before any inflate), and palette indices are not checked against the PLTE length.
- You need 16-bit output, color management, metadata, APNG frames, progressive row-by-row display, or an encoder.
- Memory-tight decoding of very large images: it holds a copy of all IDAT data, the whole filtered raw image and the output at once, and the raw scratch buffer stays allocated per thread until pd_free_thread_cache.

## How it is fast

A custom inflate modeled on fdeflate (image-png's backend): a 64-bit refill bit reader, a 12-bit combined Huffman table where one load yields one or two literals or a length, and a four-deep speculative literal cascade in which each lookup already carries the next shift (one shrx plus one L1 load per symbol); streams under 4 KB get a separate compact-table path, and match copies use 32-byte AVX2, 16-byte SSE or overlap-propagating stores over padded buffers. CRC-32 folds four PCLMULQDQ accumulators, unfiltering is SSE/AVX2 (Up as a flat 32-byte add, Sub/Average in 8-bit lanes, Paeth in 16-bit lanes), and for filtered data above 16 MB inflate, unfilter and pixel expansion are fused so each row is processed while still in cache once it is 32 KB behind the inflate frontier. The large intermediate buffer is a thread-local scratch reused across calls.

## Compared with alternatives

Pick ffpng over image-png only when you are in C/C++ on x86-64-v3 and the extra 12-20% decode throughput matters; image-png stays the better choice for Rust, ARM, memory safety, streaming and metadata. Over libspng or libpng it trades portability and features for speed (its libpng numbers are unpublished), and ptpng is the pick when you also need an encoder or ARM support.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (libc and immintrin.h); the benchmark suite additionally needs libpng, zlib, libdeflate, libspng and nightly Rust |
| **Minimum toolchain** | C99 plus GCC/Clang extensions (gcc 16.1 and 16.2 tested); compile with -march=x86-64-v3 and -mpclmul |
| **Platforms** | x86-64 only, x86-64-v3 required (AVX2, BMI2, PCLMUL) |
| **Thread safety** | Concurrent pd_decode calls are documented as safe; decode scratch is _Thread_local, so short-lived threads should call pd_free_thread_cache before exiting |
| **Drop-in for the baseline** | partial: output bytes match image-png's EXPAND \| STRIP_16 on all 2848 corpus images, but the interface is a C function (pd_decode), not the png crate's Rust API; Rust callers would need FFI |

## Gotchas

- Security bug: in 8-bit palette images, pal32 is filled from all 256 entries of an uninitialized 768-byte stack array (plte[256\*3]), and the sub-8-bit path indexes plte directly, so a pixel index at or beyond the PLTE entry count copies uninitialized stack bytes into the output instead of failing. It is not an out-of-bounds read, and it cannot occur on conforming files such as the benchmark corpus.
- Output layout varies with color type (1-4 channels, read pd_image.channels), and 16-bit samples are truncated, not rounded; there is no option for RGBA-always or 16-bit output.
- Validation is image-png-like but partial: critical-chunk CRCs are checked, ancillary CRC failures are ignored, Adler-32 is not verified, non-consecutive IDAT chunks are concatenated, and a truncated stream fails outright with no partial image.
- Public symbols are pd_decode/pd_free/pd_free_thread_cache (not ffpng_-prefixed). The benchmarked build turns off stack protector, _FORTIFY_SOURCE and CET (-fcf-protection=none), so a distro-hardened build is unmeasured.

## Known shortcomings

- The baseline is image-png (the Rust png crate), not libpng: no libpng numbers are published, so the 1.115x and 1.204x (7950X and 9950X3D, gcc 16.1 and 16.2.1, image-png shim at x86-64-v3) say nothing about the category incumbent. No LICENSE file, only SPDX MIT headers in sources; weeks-old single-author repo.
- Enricher (e124, 2026-10-05): A stands, no correctness bug behind the numbers. The timed region is uneven: the image-png shim zero-fills its output (vec![0u8; size]) on every decode while ffpng mallocs the output uninitialised and reuses a thread-local raw scratch buffer (though it copies all IDAT), which could be a sizeable part of the 2-4% photo margins but not of the 1.115x/1.204x overall. Only the 9950X3D table is tied to the current header. Security bug: the palette index is not checked against the PLTE length, so an out-of-range index copies uninitialised stack bytes (plte[768]) into the output; no fuzzing, no memory or dimension limit, x86-64-v3 only, no MSVC. Clang builds are about 10% slower per the README, so the 7950X margin is about 1.01x (derived). No LICENSE file.

## Caveats and trade-offs

The win is over image-png (the previous fastest decoder), not over libpng: the harness times libpng, libspng and stb_image but the README prints no numbers for them, so no libpng speedup is stated. Output semantics are image-png's EXPAND | STRIP_16 (16-bit truncated to 8 bits), not libpng default output; equivalence is checked byte for byte after conversion to RGBA8, outside the timed loop, and mismatching images are excluded from the aggregate (both README runs report all 2848 images passing). The timed region includes per-decode allocation for both decoders (image-png's shim allocates a zeroed Vec; ffpng mallocs). ffpng checks critical-chunk CRCs and, like image-png's default, does not verify the zlib Adler-32 (no Adler code in ffpng.h). The shim source comment still says target-cpu=native while .cargo/config.toml sets x86-64-v3 (stale comment). Corpus (QOI benchmark suite, about 1.1 GB) is downloaded, not vendored. Absolute throughput depends on core isolation and boost off; the ratio is the stable figure. Very new single-author repository (first commit 2026-06-23, 0 stars). Every source file carries an SPDX MIT tag and a copyright line, but the repository has no LICENSE file. x86-64-v3 only (AVX2, BMI2, PCLMUL); decode only, no encoder.

Single header ffpng.h, C99, libc plus immintrin.h only. Decode only (no encoder). Requires x86-64-v3 (AVX2, BMI2, PCLMUL; Intel since 2013, AMD since 2017); not portable to ARM. Output is fixed to 8-bit samples (EXPAND and STRIP_16: 16-bit truncated to the high byte). Handles all PNG color types, depths and interlacing.

## Maintenance

Active single-author project (27 commits from 2026-06-23 to 2026-09-25, 0 stars, no releases or tags); every file carries an SPDX MIT tag but there is no LICENSE file. It is one easily vendored header, but it is young and unfuzzed.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification A, tier now A.
- **Tier reason:** Public harness (bench.c, build.sh, ext/shim with image-png pinned as a submodule at 4ab5484, analyze.py) times ffpng and image-png in one process and memcmp-verifies every decoder's output against image-png as canonical RGBA8; compiler (gcc 16.1 / 16.2.1), full flags in build.sh and the shim's Cargo/rustflags, and CPUs (Ryzen 9 7950X, Ryzen 9 9950X3D, isolated core, boost off) are all stated. Both README tables (1.115x and 1.204x geomean, 13 categories) match the page exactly.
- **Verifier notes:** Strong, careful harness: same-process interleaved timing, per-image ratio, oracle check against image-png. The baseline is the already-listed image-png, so baseline_in_list is now true; the libpng comparison stays unpublished.
- **Fields the verifier corrected:** `baseline`, `baseline_in_list`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** first-party harness, public flags and CPU
- **Pages the verifier opened:**
  - <https://github.com/vtlmks/ffpng>
  - <https://github.com/vtlmks/ffpng/commits>
  - <https://raw.githubusercontent.com/vtlmks/ffpng/HEAD/README.md>
  - <https://raw.githubusercontent.com/vtlmks/ffpng/HEAD/bench.c>
  - <https://raw.githubusercontent.com/vtlmks/ffpng/HEAD/build.sh>
  - <https://raw.githubusercontent.com/vtlmks/ffpng/HEAD/analyze.py>
  - <https://raw.githubusercontent.com/vtlmks/ffpng/HEAD/ffpng.h>
  - <https://raw.githubusercontent.com/vtlmks/ffpng/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/vtlmks/ffpng/HEAD/ext/shim/Cargo.toml>
  - <https://raw.githubusercontent.com/vtlmks/ffpng/HEAD/ext/shim/.cargo/config.toml>
  - <https://raw.githubusercontent.com/vtlmks/ffpng/HEAD/ext/shim/src/lib.rs>
- **Sources the enricher read:**
  - <https://github.com/vtlmks/ffpng>
  - <https://github.com/vtlmks/ffpng/commits>
  - <https://github.com/vtlmks/ffpng/commits/main>
  - <https://raw.githubusercontent.com/vtlmks/ffpng/HEAD/README.md>
  - <https://raw.githubusercontent.com/vtlmks/ffpng/HEAD/ffpng.h>
  - <https://raw.githubusercontent.com/vtlmks/ffpng/HEAD/bench.c>
  - <https://raw.githubusercontent.com/vtlmks/ffpng/HEAD/build.sh>
  - <https://raw.githubusercontent.com/vtlmks/ffpng/HEAD/analyze.py>
  - <https://raw.githubusercontent.com/vtlmks/ffpng/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/vtlmks/ffpng/HEAD/ext/shim/Cargo.toml>
  - <https://raw.githubusercontent.com/vtlmks/ffpng/HEAD/ext/shim/.cargo/config.toml>
  - <https://raw.githubusercontent.com/vtlmks/ffpng/HEAD/ext/shim/src/lib.rs>
  - <https://raw.githubusercontent.com/vtlmks/ffpng/HEAD/LICENSE>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/vtlmks/ffpng`) · [data/wave10/enrich/raw/github_com_vtlmks_ffpng.json](../../../data/wave10/enrich/raw/github_com_vtlmks_ffpng.json) (enrichment confidence 0.85)

</details>
