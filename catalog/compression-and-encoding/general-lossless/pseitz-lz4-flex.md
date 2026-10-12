# lz4_flex

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [General-purpose lossless compression](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `MIT` · 🟢 active

> Pure-Rust LZ4 block and frame codec that matches or slightly beats the C reference lz4 when built with its unsafe paths.

| | |
|---|---|
| **Beats** | lz4 (C reference 1.9.3, via the lzzzz Rust binding) |
| **Claimed result** | 66KB JSON: lz4_flex unsafe 1615 MiB/s compress and 5512 MiB/s decompress vs lzzz (lz4 1.9.3) 1469 and 5313 MiB/s; 10MB dickens: 347 MiB/s compress and 2734 MiB/s decompress vs 324 and 2759 MiB/s. About 1.10x and 1.07x compression, 1.04x and 0.99x decompression (derived from page data); 'unchecked_decode' variant decompresses at 5973 and 3168 MiB/s (1.12x and 1.15x, derived from page data). Safe build is slower than C lz4 (1272/4540 and 259/2338 MiB/s). |
| **Workload** | LZ4 block compression and decompression of a 66 KB JSON file and the 10 MB dickens text file, criterion benchmarks in the repo's benches folder |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 7 5900HX, Manjaro, CPU boost disabled, governor performance (README also says CPU 3GHZ) |
| **Compiler and flags** | rustc 1.69.0 (84c898d65 2023-04-16); cargo bench --no-default-features (safe-encode/safe-decode off) and cargo bench (safe on); Cargo.toml [profile.bench]: opt-level = 3, lto = true, codegen-units = 1. C compiler used by lzzzz to build lz4 1.9.3 not stated. |
| **Adoption** | 618 stars; crates.io lz4_flex |
| **Last commit** | 2026-08-11 |
| **Links** | [repository](https://github.com/PSeitz/lz4_flex) · [benchmark](https://github.com/PSeitz/lz4_flex#benchmarks) |

## Verdict

Author's criterion run of v0.11.0 (June 2023) with rustc 1.69.0 on a Ryzen 7 5900HX at 3 GHz with boost off: on a 66 KB JSON file the unsafe build compresses at 1615 vs 1469 MiB/s and decompresses at 5512 vs 5313 MiB/s against C lz4 1.9.3 via the lzzzz binding (about 1.10x and 1.04x), and on 10 MB dickens 347 vs 324 MiB/s compress but 2734 vs 2759 MiB/s decompress (a tie); the C compiler and flags used to build lzzzz's lz4 are not stated, and the numbers predate the 2025-2026 security fixes.

## Use it when

- Rust services that need LZ4 compatibility without a C toolchain or a -sys crate (no C build step, no_std block format, 32-bit and wasm targets).
- Small to medium blocks (tens of KB, e.g. per-message or per-page compression) where the README shows the unsafe build about 10% faster than C lz4 1.9.3 at compression.
- Projects that want a memory-safe default decoder for untrusted LZ4 input and accept a speed loss versus C lz4 for it.
- Interop with existing LZ4 frame data written by the C tool or library.

## Skip it when

- C++ codebases: the C reference lz4 is the same format, within a few percent on these benchmarks, and callable directly.
- When you need high-compression (LZ4 HC) modes: the README TODO still lists high compression as missing, so only the fast level exists.
- When the default safe build is all you can ship and speed is the reason: it is slower than C lz4 on both inputs (66 KB JSON 1272/4540 MiB/s vs 1469/5313).
- Large-file decompression where the margin matters: on 10 MB dickens the unsafe decoder is 2734 MiB/s vs C lz4 2759 MiB/s, i.e. no win.
- Versions before 0.11.6/0.12.1/0.13.0 on untrusted input: an invalid match offset (offset 0) could read uninitialized memory or leak a reused output buffer (advisory GHSA-vvp9-7p8x-rfvv, High, 2026-03-14).

## How it is fast

Standard LZ4 greedy matching with a 4K-entry multiplicative hash table (u16 positions for small inputs, hash5 over 5 bytes on 64-bit), plus a decoder hot loop that handles the common single-byte token case with fixed 16-byte literal copies and 18-byte match copies whenever the input and output pointers are a safe distance from the end, so most sequences skip per-byte bounds checks. Long matches use a 16-byte wild copy; overlapping matches use a deliberately lightly unrolled byte loop. With safe-encode/safe-decode disabled these run on raw pointers; the default safe build uses slice operations and pays roughly 15-25% (README tables).

## Compared with alternatives

Pick lz4_flex over the C LZ4 reference only when you are in Rust and want no C build or a safe-by-default decoder; from C++ use LZ4 itself. lzvolt and misa77 decode much faster but use their own formats, and lz4ultra targets better LZ4 ratio at slow compression, so lz4_flex is the choice only when LZ4 wire compatibility in pure Rust is the requirement.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | none for the block format; twox-hash 2 (xxhash32) with the default 'frame' feature |
| **Minimum toolchain** | Rust 1.81 (rust-version in Cargo.toml), edition 2021 |
| **Platforms** | any Rust target; 64-bit uses an 8-byte hash path, 32-bit supported (wasm32 had overflow bugs, one still open as issue #215) |
| **Thread safety** | not documented; the API is free functions plus per-instance FrameEncoder/FrameDecoder with no shared global state seen in the source |
| **Drop-in for the baseline** | partial: bit-compatible LZ4 block and frame format, so data interoperates with C lz4, but the API is Rust (no LZ4_compress_default-style C ABI) and there is no HC level |

## Gotchas

- The README's fastest row ('unsafe w. unchecked_decode', 5973 and 3168 MiB/s decompress) used a feature removed in 0.11.1 (2023-06-19); the 'checked-decode' feature still listed in Cargo.toml is not referenced by any cfg in src, so that row cannot be reproduced on current releases.
- The fast numbers need default-features = false; since 0.14.0 that also drops 'alloc' (Vec-returning compress/decompress) unless you add features = ["alloc"], and Cargo feature unification can silently turn safe-decode back on (or off) through another dependency.
- decompress_size_prepended trusts the 4-byte little-endian size header and allocates Vec::with_capacity of up to 4 GiB before decoding, so hostile input can force large allocations; check the size yourself for untrusted data. The block API keeps the whole payload in memory, the frame format is the streaming path.
- Recent bug history: offset-0 uninitialized-read advisory (fixed 0.11.6/0.12.1/0.13.0), u32 overflow on large block payloads (fixed 0.12.0), short-dictionary out-of-bounds read in unsafe compression (fixed 0.12.2/0.13.1), Max8MB frames rejected by its own decoder (fixed Aug 2026), try_finish panic on a second empty frame (issue #233, open). The GitHub default branch (master) still shows 0.11.5; current code is on main (0.14.0).

## Known shortcomings

- Rust, not C++. Win over C lz4 is only 4-10% and only in the unsafe build. README numbers come from an old criterion bench; HEAD uses benches/binggan_bench.rs.
- Security advisory GHSA-vvp9-7p8x-rfvv (High, 2026-03-14): an offset-0 match reads uninitialised memory or a reused buffer, fixed in 0.11.6/0.12.1/0.13.0. Other fixed bugs: short-dictionary out-of-bounds read in unsafe compress (0.12.2/0.13.1), u32 overflow on large blocks (0.12.0), Max8MB frame rejected by its own decoder (Aug 2026). Still open: #215 (32-bit overflow panic) and #233 (try_finish panic). The README 'unchecked_decode' row (5973/3168 MiB/s) used a feature removed in 0.11.1, so it cannot be reproduced; numbers are from v0.11.0 (2023) and predate the security fixes. Dickens decompress is a tie (2734 vs 2759 MiB/s). decompress_size_prepended trusts a 4-byte size header (allocates up to 4 GiB). Default branch master shows 0.11.5; the real code is on main (0.14.0). No HC mode; Rust only, no C ABI.

## Caveats and trade-offs

Own benchmark on two inputs; README numbers date from v0.11.0 (2023-06-02) with rustc 1.69 and were produced by the old criterion bench, while HEAD now uses a binggan bench (benches/binggan_bench.rs). The win over C lz4 is small (about 4-10%) and needs the unsafe configuration; the default safe build is slower than C lz4, and the fastest decompress row disables checked-decode, which the crate says must only be used on trusted input. C compiler and flags for the lzzzz-built lz4 baseline are not stated. The same README also lists lz-fear and snap.

Rust crate, not directly callable from C++ without FFI. Fastest numbers need the unsafe (non-default-safe) build; the safe build is slower than C lz4 (66KB JSON: 1272 MiB/s compress, 4540 MiB/s decompress vs 1469 and 5313).

## Maintenance

Actively maintained (0.14.0 released 2026-07-14, last commit 2026-08-11 on main) and MIT-licensed, but it is a Rust crate, so for C++ it is usable only through FFI or as a reference design; the published benchmark has not been refreshed since v0.11.0.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification A, tier now A.
- **Tier reason:** README tables compare lz4_flex against lzzzz (C lz4 1.9.3) on 66KB JSON and 10MB dickens with rustc 1.69.0, AMD Ryzen 7 5900HX (boost off, 3 GHz) and the cargo bench invocation; Cargo.toml [profile.bench] sets opt-level 3, lto = true, codegen-units = 1, and benches/ (now benches/binggan_bench.rs, which still benchmarks lzzzz on compression_66k_JSON.txt and dickens.txt) holds the code.
- **Verifier notes:** Numbers match the README exactly. Metadata checked on github.com: MIT, 618 stars, 61 forks, not archived, not a fork; last commit 2026-08-11 (PR #234). Tier A kept on the strength of public bench code, rustc version, Cargo bench profile and CPU, but the margin over C lz4 is small.
- **Fields the verifier corrected:** `compiler_and_flags`, `hardware`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** first-party benchmark (public bench code, profile opt-level 3, lto, codegen-units 1); first-party benchmark (public bench code)
- **Pages the verifier opened:**
  - <https://github.com/PSeitz/lz4_flex>
  - <https://github.com/PSeitz/lz4_flex/commits/main>
  - <https://raw.githubusercontent.com/PSeitz/lz4_flex/HEAD/README.md>
  - <https://raw.githubusercontent.com/PSeitz/lz4_flex/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/PSeitz/lz4_flex/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/PSeitz/lz4_flex/HEAD/benches/bench.rs>
  - <https://raw.githubusercontent.com/PSeitz/lz4_flex/HEAD/benches/binggan_bench.rs>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/PSeitz/lz4_flex/HEAD/README.md>
  - <https://raw.githubusercontent.com/PSeitz/lz4_flex/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/PSeitz/lz4_flex/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/PSeitz/lz4_flex/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/PSeitz/lz4_flex/HEAD/src/block/mod.rs>
  - <https://raw.githubusercontent.com/PSeitz/lz4_flex/HEAD/src/block/decompress.rs>
  - <https://raw.githubusercontent.com/PSeitz/lz4_flex/HEAD/src/block/decompress_safe.rs>
  - <https://raw.githubusercontent.com/PSeitz/lz4_flex/HEAD/src/block/compress.rs>
  - <https://raw.githubusercontent.com/PSeitz/lz4_flex/HEAD/src/block/hashtable.rs>
  - <https://raw.githubusercontent.com/PSeitz/lz4_flex/HEAD/src/frame/mod.rs>
  - <https://raw.githubusercontent.com/PSeitz/lz4_flex/HEAD/src/sink.rs>
  - <https://raw.githubusercontent.com/PSeitz/lz4_flex/HEAD/src/fastcpy_unsafe.rs>
  - <https://raw.githubusercontent.com/PSeitz/lz4_flex/main/README.md>
  - <https://raw.githubusercontent.com/PSeitz/lz4_flex/main/Cargo.toml>
  - <https://raw.githubusercontent.com/PSeitz/lz4_flex/main/CHANGELOG.md>
  - <https://raw.githubusercontent.com/PSeitz/lz4_flex/main/src/block/decompress.rs>
  - <https://raw.githubusercontent.com/PSeitz/lz4_flex/main/src/block/decompress_safe.rs>
  - <https://raw.githubusercontent.com/PSeitz/lz4_flex/main/src/block/mod.rs>
  - <https://github.com/PSeitz/lz4_flex/issues?q=is%3Aissue>
  - <https://github.com/PSeitz/lz4_flex/security>
  - <https://github.com/PSeitz/lz4_flex/commits/main>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/pseitz/lz4_flex`) · [data/wave9/enrich/raw/github_com_pseitz_lz4_flex.json](../../../data/wave9/enrich/raw/github_com_pseitz_lz4_flex.json) (enrichment confidence 0.8)

</details>
