# mtpng (parallel PNG encoder with C API)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust (C API)` · `MIT` · 🟢 active

> Multithreaded Rust PNG encoder with a C API; chunked zlib deflate gives libpng-like file sizes, several times faster on many cores.

| | |
|---|---|
| **Beats** | libpng |
| **Claimed result** | docs/perf.md 'Old performance data' (2018-era), dual-4K screenshot at default options. Single-threaded vs libpng: MacBook Pro 2015 Linux x86_64 libpng gcc 850 ms vs mtpng 555 ms (1.53x); macOS libpng clang 943 ms vs 563 ms (1.67x); Xeon E5520 Linux libpng gcc 1695 ms vs 1124 ms (1.51x); Raspberry Pi 3B+ aarch64 4692 ms vs 4311 ms (1.09x); Raspberry Pi 3B+ armhf 5368 ms vs 6068 ms (mtpng 0.88x, slower). Multi-threaded vs single-threaded libpng: MacBook Linux 2 threads 302 ms (2.81x), 4 threads with HT 248 ms (3.43x); Xeon E5520 8 threads 165 ms (10.3x), 16 threads 155 ms (10.9x); Pi 3B+ armhf 4 threads 1875 ms (2.86x), aarch64 4 threads 1416 ms (3.31x). All ratios derived from page data; the 1.0x/1.8x/2.2x factors printed on the page are mtpng thread scaling relative to mtpng on one thread, not ratios against libpng. README: single-threaded \~30-40% faster than libpng (Rust 1.29.0, 26 Sept 2018). The '2026 data' section has mtpng times only (e.g. Apple M3 Max 237 ms on 1 thread, 23 ms on 16; Ryzen 9 5950X Linux 301 ms on 1 thread, 25 ms on 32) and no libpng column. |
| **Workload** | Re-encoding a dual-4K screenshot PNG at default options, single-threaded and multi-threaded, compared with libpng built by gcc and clang. |
| **Metric** | throughput |
| **Hardware** | MacBook Pro 13in 2015, 5th-gen Core i7 3.1 GHz, 2 cores plus Hyper-Threading (libpng comparison); several newer machines for mtpng-only timings |
| **Compiler and flags** | cargo run --release (Rust); libpng built with gcc or clang, versions and zlib not stated |
| **Adoption** | 228 stars |
| **Last commit** | 2026-06-08 |
| **Links** | [repository](https://github.com/bvibber/mtpng) · [benchmark](https://raw.githubusercontent.com/bvibber/mtpng/HEAD/docs/perf.md) |

## Verdict

The author re-encoded one 7680x2160 RGBA screenshot (samples/dual4k.png, 1.69 MB) with mtpngenc --repeat=10, keeping the fastest run. In 2018 on a 2015 MacBook Pro (Linux), one thread took 555 ms against 850 ms for libpng built with gcc (1.53x), and 4 threads took 248 ms (3.4x vs single-threaded libpng). On a Xeon E5520, 8 threads took 165 ms against libpng's 1695 ms. The libpng timings have no published harness, version or zlib build ('@fixme how did I measure those libpng times?'), no output sizes are reported for either side, and the 2026 reruns time mtpng only. Code read this session shows a like-for-like zlib configuration (level 6, Z_FILTERED, 32 KiB window), but mtpng skips None-filter scoring and the timed 2018 builds predate the 0.3.5 heuristic change. No correctness bug affects the timed image: its 30,720-byte rows are far below the 256 KiB chunk size involved in issue #30.

## Use it when

- Saving large images (screenshots, renders, frames of tens of megapixels) on a multi-core machine where PNG encode latency matters and output should stay close to libpng's default size (zlib level 6, adaptive filters, Z_FILTERED strategy).
- Many-core boxes: the author's 2026 runs on the 7680x2160 RGBA screenshot take 23 ms on 16 threads (Apple M3 Max) and 25 ms on 32 threads (Ryzen 9 5950X), against 237 ms and 301 ms on one thread.
- Rust or C/C++ programs that need palette, greyscale, 1/2/4-bit or 16-bit output, which fpng (24/32bpp only) does not cover.
- Streaming a big PNG to a socket or file as it is produced: Rust Options::set_streaming emits one IDAT per chunk so bytes leave before the image is finished (not exposed in the C API).

## Skip it when

- Small images: below 128 KiB of uncompressed data there is no threading gain (README), and the project says small-file support 'needs work'.
- Raw single-core speed: one-thread mtpng on the dual-4K screenshot runs at about 30 Mpx/s on a 2015 i7 and 55 Mpx/s on a Ryzen 9 5950X (derived from page data). fpnge and fpng are far faster per core if larger files are acceptable.
- 32-bit ARM single-threaded: on a Raspberry Pi 3B+ under armhf, mtpng took 6068 ms against libpng's 5368 ms.
- Projects that need a stable API or a current crates.io release: both APIs are documented as unstable before 1.0, and crates.io's latest is 0.4.1 (2024-04-26). That release predates the February 2026 fix (PR #31, issue #30) for rows wider than the chunk size, which failed with 'Incomplete image input'.
- Decoding, Adam7 interlacing, or writing gamma, ICC or text metadata without hand-building chunks.

## How it is fast

The pigz scheme applied to PNG. Rows are grouped into chunks of at least 256 KiB. Each chunk is filtered on its own thread, then deflated by stock zlib (through libz-sys) as an independent stream: a raw stream after the first chunk, primed with the previous chunk's last 32 KiB of filtered bytes through deflateSetDictionary, ended with Z_SYNC_FLUSH so the pieces concatenate into one valid IDAT stream. The Adler-32 values are merged with adler32_combine. Filtering runs all four predictive filters (Sub, Up, Average, Paeth) over each whole row and keeps the one with the smallest sum of absolute signed bytes. The loops are plain iterator code compiled several times under target_feature (AVX2, AVX, SSE4.2, SSE4.1) and picked at run time, so LLVM auto-vectorises them. That is where the single-thread gain over libpng comes from; deflate itself is the same zlib.

## Compared with alternatives

Pick mtpng over fpng or fpnge when you need libpng-like compression ratios or non-RGB formats (palette, greyscale, 16-bit), and over pngenc when you want a Rust crate or a maintained C API that reuses stock zlib. If single-core speed matters more than file size, fpnge (about 57x libpng encode in the QOIR benchmark, about 15% larger files) wins outright.

## Integration

| | |
|---|---|
| **Form** | crate (rlib), plus cdylib/staticlib with the C header c/mtpng.h when built with the 'capi' feature |
| **Dependencies** | rayon, crc, itertools, libz-sys (system zlib, or builds C zlib where none ships, e.g. Windows); libc for the C API; png, clap and time only for the mtpngenc CLI |
| **Minimum toolchain** | Rust 1.88 or newer for the repo's 0.5.0 (edition 2024, and encoder.rs uses an if-let chain; Cargo.toml declares no rust-version); the C header needs a C99 compiler (stdint.h, stdbool.h) |
| **Platforms** | any Rust target with zlib; README lists Linux x86/x86-64/arm/arm64, macOS x86-64, iOS arm64, Windows x86/x86-64/arm64; runtime-dispatched x86 SIMD paths, scalar elsewhere |
| **Thread safety** | One encoder per image, driven by the caller; work runs on the Rayon global pool or a supplied pool, and one pool may serve several encoders as long as it outlives them (c/mtpng.h). |
| **Drop-in for the baseline** | partial: same PNG output family as libpng's default write path (zlib level 6, filtered strategy, adaptive filters), but a different API (no png_struct/png_info, no transforms, no interlace), encode only |

## Gotchas

- Adaptive filtering never scores the None filter (libpng's default PNG_ALL_FILTERS does), so screenshot-style truecolor images, where None often wins, can come out larger. The README says the heuristic 'fails to correctly predict good performance of the none filter'. Palette images are forced to None.
- Speed depends on which zlib libz-sys links. Open PR #29 (zlib-rs backend) reports 128 ms down to 55 ms on one image, and open PR #17 adds zlib-ng, so the C zlib in use matters as much as the threading.
- Without streaming mode the whole compressed IDAT is buffered in memory and written at finish(); the C API offers no streaming toggle.
- The C API returns only OK or ERR, with no message. The Rust code still has internal panics (chunk bookkeeping), and a panic in a rayon::spawn job or across the extern "C" boundary aborts the process.

## Known shortcomings

- Rust core with a C API (language-filter mismatch). Single-thread 1.53x/1.51x vs libpng with gcc, slower on armhf (0.88x); multi-thread rows (up to 10.9x derived) run against single-thread libpng. The libpng harness is unknown (@fixme in the repo) and the filter heuristics differ (mtpng skips the None filter, libpng 1.6 scores it; mtpng's heuristic changed in 0.3.5 in 2021, after the 2018 timings). Repo moved to bvibber/mtpng.
- The libpng side of the harness is missing and the 2026 reruns time mtpng only; no output sizes are published although the adaptive filter skips None (zlib config matches libpng: level 6, Z_FILTERED, 32 KiB window). Speed depends on the linked zlib (open PR #29 moves to zlib-rs: 128 ms to 55 ms). crates.io 0.4.1 (2024-04-26) predates the fix for issue #30 ('Incomplete image input' on rows wider than a chunk, PR #31); building from the repo needs Rust 1.88+ (edition 2024, if-let chains). The C API has no streaming toggle and reports OK or ERR only.

## Caveats and trade-offs

perf.md says '@fixme how did I measure those libpng times? need to recreate that', so the libpng baseline has no published harness, version, zlib build or flags, and all libpng numbers date from 2018. The work differs from libpng: mtpng's adaptive filter scores only Sub/Up/Average/Paeth (src/filter.rs filter_adaptive), while libpng 1.6's default PNG_ALL_FILTERS selection also scores None (pngwutil.c png_write_find_filter); the README says a 0.3.5 change (crates.io 2021-04-22, after these timings) altered the heuristic to match libpng in some cases, so the timed builds chose filters differently from libpng on the screenshot input. Deflate runs in independent 256 KiB chunks, which the README says compresses a tiny fraction worse than libpng. Multi-threaded rows are many threads against single-threaded libpng. On 32-bit ARM mtpng is slower than libpng single-threaded. The repository now lives at github.com/bvibber/mtpng (brion/mtpng redirects); crates.io's latest published version is 0.4.1 while the repo is at 0.5.0.

Encoder only; input must be pre-packed pixels. Compression ratio is a tiny fraction worse than libpng at the default 256 KiB chunk size (closer with larger chunks). Files under 128 KiB uncompressed see no threading gain. Rust library with a C API that the README says is still unstable; pulls libz_sys. Small-file and ancillary-chunk support needs work.

## Maintenance

Active again in 2026 (last commit 2026-06-08: edition 2024, clippy cleanup, C-API build rework; chunk-row fix merged in February), MIT-licensed, 228 stars, about 95k crates.io downloads and 3 reverse dependencies. crates.io still ships 0.4.1 from 2024, and the README's CLI example link still points to src/bin/mtpng.rs, which was renamed to mtpngenc.rs.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** docs/perf.md gives the mtpng command line (cargo run --release, --repeat=10) and machines, but the libpng side has no published harness ('@fixme how did I measure those libpng times?'), libpng/zlib versions and flags are unstated, and the 2015 MacBook CPU is named only as '5th-gen Core i7 3.1 GHz'. First-party, partial methodology: C.
- **Verifier notes:** Numbers and derived ratios check out against docs/perf.md; I split single-thread from multi-thread and added the Xeon and Raspberry Pi rows, including the armhf case where mtpng is slower. language is not in verify.py's CORRECTABLE set, and the repo moved to bvibber/mtpng, so the language and repo_url changes need a decisions.json override. Last commit 2026-06-08 (active), 228 stars, MIT, all confirmed.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/brion/mtpng>
  - <https://github.com/bvibber/mtpng/commits/main>
  - <https://raw.githubusercontent.com/brion/mtpng/HEAD/docs/perf.md>
  - <https://raw.githubusercontent.com/bvibber/mtpng/HEAD/docs/perf.md>
  - <https://raw.githubusercontent.com/brion/mtpng/HEAD/readme.md>
  - <https://raw.githubusercontent.com/bvibber/mtpng/HEAD/readme.md>
  - <https://raw.githubusercontent.com/brion/mtpng/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/brion/mtpng/HEAD/c/mtpng.h>
  - <https://raw.githubusercontent.com/bvibber/mtpng/HEAD/src/filter.rs>
  - <https://raw.githubusercontent.com/bvibber/mtpng/HEAD/src/encoder.rs>
  - <https://raw.githubusercontent.com/bvibber/mtpng/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/bvibber/mtpng/HEAD/src/bin/mtpngenc.rs>
  - <https://crates.io/api/v1/crates/mtpng/versions>
  - <https://raw.githubusercontent.com/pnggroup/libpng/libpng16/pngwutil.c>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/bvibber/mtpng/HEAD/readme.md>
  - <https://raw.githubusercontent.com/bvibber/mtpng/HEAD/docs/perf.md>
  - <https://raw.githubusercontent.com/bvibber/mtpng/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/bvibber/mtpng/HEAD/Makefile>
  - <https://raw.githubusercontent.com/bvibber/mtpng/HEAD/c/mtpng.h>
  - <https://raw.githubusercontent.com/bvibber/mtpng/HEAD/c/sample.c>
  - <https://raw.githubusercontent.com/bvibber/mtpng/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/bvibber/mtpng/HEAD/src/encoder.rs>
  - <https://raw.githubusercontent.com/bvibber/mtpng/HEAD/src/filter.rs>
  - <https://raw.githubusercontent.com/bvibber/mtpng/HEAD/src/deflate.rs>
  - <https://raw.githubusercontent.com/bvibber/mtpng/HEAD/src/capi.rs>
  - <https://raw.githubusercontent.com/bvibber/mtpng/HEAD/src/writer.rs>
  - <https://raw.githubusercontent.com/bvibber/mtpng/HEAD/src/utils.rs>
  - <https://raw.githubusercontent.com/bvibber/mtpng/HEAD/src/bin/mtpngenc.rs>
  - https://raw.githubusercontent.com/bvibber/mtpng/HEAD/samples/dual4k.png (IHDR bytes only)
  - <https://github.com/bvibber/mtpng/issues?q=is%3Aissue>
  - <https://github.com/bvibber/mtpng/issues/30>
  - <https://github.com/bvibber/mtpng/pulls?q=is%3Apr>
  - <https://github.com/bvibber/mtpng/pull/29>
  - <https://github.com/bvibber/mtpng/commits/main>
  - <https://crates.io/api/v1/crates/mtpng>
  - <https://crates.io/api/v1/crates/mtpng/versions>
  - <https://crates.io/api/v1/crates/mtpng/reverse_dependencies>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/brion/mtpng`) · [data/wave10/enrich/raw/github_com_brion_mtpng.json](../../../data/wave10/enrich/raw/github_com_brion_mtpng.json) (enrichment confidence 0.75)

</details>
