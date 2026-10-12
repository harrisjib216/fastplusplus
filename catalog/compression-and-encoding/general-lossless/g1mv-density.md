# Density (density-rs)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [General-purpose lossless compression](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟡 stale

> Pure-Rust block compressor using 4-byte hashed dictionary units; compresses faster than LZ4 at matching ratios, decompresses slower.

| | |
|---|---|
| **Beats** | lz4 (also Snappy) |
| **Claimed result** | Compression 1630 MB/s at ratio 62.77% (density 0.16.6 -1) versus lz4 1.10.0 --fast -17 at 924 MB/s and 62.15%, and lz4 default at 550 MB/s and 47.60%; Snappy 1.3.1 457 MB/s at 47.85%. Compression about 1.8x lz4 --fast -17 (derived from page data). Decompression 1617 MB/s versus lz4 3832-3977 MB/s, so slower than lz4 on decode. |
| **Workload** | In-memory compression and decompression of silesia.tar (211,947,520 bytes), single thread, lzbench 2.4. |
| **Metric** | throughput |
| **Hardware** | AMD EPYC 9555P 3.20 GHz, single thread, performance governor, turbo disabled, Ubuntu 26.04 |
| **Compiler and flags** | gcc 15.2.0 (lzbench 2.4 release binary lzbench24_x86_64-linux-gnu-gcc15); lzbench v2.4 Makefile OPT_FLAGS_O3: -fomit-frame-pointer -fstrict-aliasing -O3 -DNDEBUG (a few codecs use the -O2 variant); run options -eALL -t8,8 -o1c4 |
| **Adoption** | about 1k stars |
| **Last commit** | 2025-08-27 |
| **Links** | [repository](https://github.com/g1mv/density) · [benchmark](https://github.com/inikep/lzbench) |

## Verdict

In lzbench 2.4 (gcc 15.2.0 release binary, density built with cargo inside lzbench, one thread of an AMD EPYC 9555P with turbo off, silesia.tar), Density 0.16.6 -1 compresses at 1630 MB/s to 62.77% versus LZ4 1.10.0 --fast -17 at 924 MB/s and 62.15% (about 1.8x), and -2 at 767 MB/s to 47.94% versus LZ4 default at 550 MB/s and 47.60% (about 1.4x, derived from page data); decompression is 758-1617 MB/s versus LZ4's 3832-3977 MB/s. The repo's own cargo bench compares only against the Rust ports lz4_flex and snap, not the C libraries.

## Use it when

- Compression throughput is the bottleneck and decode volume is similar or lower, e.g. write-heavy logging, snapshotting or spill-to-disk where data is written once and read rarely.
- Large text-like or moderately redundant buffers (tens of MB), where the 4-byte dictionary has time to learn; Cheetah (-2) matches LZ4-default ratio while compressing about 1.4x faster in lzbench 2.4.
- Rust codebases wanting a dependency-free, bounds-checked codec with no unsafe code on the data path, or C/C++ code willing to link a Rust staticlib through the 0.16.6 C functions.
- Incompressible or mixed inputs, where the copy-mode protection keeps output at most 8 bytes per 256-byte block above the input size.

## Skip it when

- Read-heavy workloads: decompression is 1617 MB/s for Chameleon versus 3832-3977 MB/s for LZ4 on the same lzbench table, so LZ4, LZSSE or ZXC decode 2.4x or more faster.
- When interoperability matters: the format is not standardised, has no framing, length header or checksum, and changed across the C-to-Rust rewrite (0.14.x C streams are a different codebase).
- Small messages: the README says the algorithms 'are less performant on very small datasets' because the 4-byte dictionary learns slowly.
- Untrusted or corrupted input from C/C++: decode never returns an error; malformed data or a too-small output buffer hits a Rust slice bounds check and panics, which through the extern "C" functions aborts the process (Rust 1.81+ behavior).
- If you only need one fast-compress point: memlz 0.5 beta in the same lzbench table compresses at 4452 MB/s at 59.90% size, faster and smaller than Density -1 (1630 MB/s, 62.77%).

## How it is fast

It is not an LZ77 matcher: input is read 16 bytes at a time as a u128 and split into four 32-bit 'quads'; each quad is hashed (multiply by 0x9D6EF916, keep the top 16 bits) into a 64K-entry u32 dictionary, and a hit emits a 2-byte hash index while a miss emits the 4 literal bytes, with 1 flag bit per quad packed into a 64-bit signature word. Cheetah adds a second dictionary slot and a predictor, Lion five predictors. There is no match search, no variable-length offsets and no entropy coder, and a 'blowup protection' state machine switches blocks to plain copy when two consecutive blocks fail to shrink.

## Compared with alternatives

Pick Density over LZ4 or Snappy when compression speed matters more than decode speed: Cheetah gives LZ4-default ratio at 1.4x LZ4's compression speed, and Chameleon gives LZ4 --fast -17 ratio at 1.8x its speed. For fast decode pick LZ4, ZXC or LZSSE; for the fastest compress-only point at this ratio memlz is ahead.

## Integration

| | |
|---|---|
| **Form** | crate (Rust); C callers must build it as a staticlib/cdylib themselves (no header or C build files shipped) |
| **Dependencies** | none at runtime (dev-dependencies divan, snap, lz4_flex for benches only) |
| **Minimum toolchain** | Rust 1.85 (edition 2024); lzbench's wrapper crate states 1.85 as Density's minimum |
| **Platforms** | any Rust target; CI tests x86-64 Linux/macOS/Windows (MSVC and GNU), i686, aarch64, and big-endian powerpc64 and s390x; no SIMD or arch-specific code |
| **Thread safety** | not documented; each encode/decode call allocates its own 256 KiB dictionary state, so separate calls on separate threads share nothing |
| **Drop-in for the baseline** | no |

## Gotchas

- Errors are effectively panics: encode and decode always return Ok, and all bounds problems surface as slice-index panics; the C wrappers return 0 only for an Err that never occurs.
- Every static encode/decode call allocates and zeroes a 64K-entry u32 table (256 KiB); reuse a Chameleon::new() instance for many small buffers, or the setup dominates.
- The level-to-algorithm mapping in lzbench is -1 Chameleon, -2 Cheetah, -3 Lion; Lion compresses at only 442 MB/s with 578 MB/s decode, slower than LZ4 default on both sides.
- lzbench documents earlier bugs: its README carried a warning about density 0.14.2 producing shortened decompressed output (issues #92 and #94 asked about it and were closed without a written answer); fuzzing crashes (#60) and an encoder division by zero (#56) were fixed in the C era.

## Known shortcomings

- Tier B on lzbench 2.4 (1630 vs lz4 --fast -17 924 MB/s compress; decode 1617 vs 3977, so decode loses). Rust; stale since 2025-08-27.
- Decode never returns an error: corrupt input or a too-small output buffer panics, and through the 0.16.6 extern "C" functions that aborts the process. No framing, length header or checksum. memlz 0.5 beta beats density -1 on both speed and ratio in lzbench 2.4 (4452 MB/s, 59.90% vs 1630 MB/s, 62.77%). The repo's cargo bench compares against lz4_flex and snap (Rust ports), not C lz4. lzbench warned about shortened output in 0.14.2; issues #92 and #94 closed without answers.

## Caveats and trade-offs

Win is compression speed only; decompression is about 2.4x slower than lz4 on the same table. The README's own pareto-frontier claim points to a squash-benchmark page on github.io that could not be opened (egress blocked). Not-default lz4 level used for the like-for-like ratio comparison. Build flags for the Rust codec inside lzbench are not stated.

Ratio is far worse than lz4 default (62.77% versus 47.60% of original size at level 1); the three algorithms (chameleon, cheetah, lion) trade ratio for speed. Rewritten from the original C99 library into Rust; the page opened shows only Cargo usage, and the latest commits mention C bindings.

## Maintenance

Last commit and crate release 0.16.6 on 2025-08-27 (C bindings added), zero open issues, about 1k stars and 6.6k crate downloads; small, MIT OR Apache-2.0, and easy to vendor, but effectively single-maintainer and quiet for 13 months.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now A.
- **Tier reason:** The well-known independent lzbench 2.4 suite (public code, inikep/lzbench; gcc 15.2.0 release binary; single thread of an AMD EPYC 9555P, turbo off, silesia.tar) lists density 0.16.6 -1 at 1630 / 1617 MB/s, 62.77% vs lz4 1.10.0 --fast -17 at 924 / 3977 MB/s, 62.15% and lz4 1.10.0 at 550 / 3832 MB/s, 47.60%; all quoted rows match. Density is built through cargo --release inside lzbench and the release binary's exact build settings are not on the results page, so B rather than A, consistent with other lzbench-sourced entries.
- **Retiered** B to A: Raised B to A for tier consistency with FastLZ (batch verdict A on the same table): the evidence is the lzbench 2.4 README table, an independent public suite (inikep/lzbench, tag v2.4) whose release binary lzbench24_x86_64-linux-gnu-gcc15 is built with gcc 15.2.0 from the public Makefile (OPT_FLAGS_O3 = -fomit-frame-pointer -fstrict-aliasing -O3 -DNDEBUG, line 147; some codecs use the -O2 variant, line 146), run single-threaded on an AMD EPYC 9555P at 3.20 GHz with -eALL -t8,8 -o1c4 on silesia.tar. Compiler, flags, CPU model and harness are all public, so the run is reproducible and meets tier A; the earlier B verdicts counted the flags as unstated because they are not repeated on the results page.
- **Verifier notes:** All numbers verified on the lzbench README; last commit 2025-08-27 (stale, 13 months), MIT/Apache-2.0, about 1k stars. Implementation language is Rust, so the orchestrator may want to tag it as a non-C++ entry; the README itself has no numeric comparison against lz4/snappy (it only claims pareto-frontier and points to cargo bench).
- **Fields the verifier corrected:** `compiler_and_flags`
- **Shortcomings recorded by:** verifier; lzbench 2.4: density -2 767 MB/s at 47.94% vs lz4 default 550 MB/s at 47.60% (1.4x)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/README.md>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/Makefile>
  - <https://github.com/g1mv/density>
  - <https://github.com/g1mv/density/commits>
- **Sources the enricher read:**
  - <https://github.com/g1mv/density>
  - <https://raw.githubusercontent.com/g1mv/density/HEAD/README.md>
  - <https://raw.githubusercontent.com/g1mv/density/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/g1mv/density/HEAD/benchmark.log>
  - <https://raw.githubusercontent.com/g1mv/density/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/g1mv/density/HEAD/src/algorithms/chameleon/chameleon.rs>
  - <https://raw.githubusercontent.com/g1mv/density/HEAD/src/codec/codec.rs>
  - <https://raw.githubusercontent.com/g1mv/density/HEAD/src/codec/protection_state.rs>
  - <https://raw.githubusercontent.com/g1mv/density/HEAD/src/io/read_buffer.rs>
  - <https://raw.githubusercontent.com/g1mv/density/HEAD/src/io/write_buffer.rs>
  - <https://raw.githubusercontent.com/g1mv/density/HEAD/src/errors/decode_error.rs>
  - <https://raw.githubusercontent.com/g1mv/density/HEAD/.github/workflows/ci.yml>
  - <https://github.com/g1mv/density/commits>
  - <https://github.com/g1mv/density/issues?q=is%3Aissue>
  - <https://github.com/g1mv/density/issues/92>
  - <https://github.com/g1mv/density/issues/94>
  - <https://crates.io/api/v1/crates/density-rs>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/README.md>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/Makefile>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/misc/rust-codecs/lib.rs>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/misc/rust-codecs/Cargo.toml>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/g1mv/density`) · [data/wave9/enrich/raw/github_com_g1mv_density.json](../../../data/wave9/enrich/raw/github_com_g1mv_density.json) (enrichment confidence 0.8)

</details>
