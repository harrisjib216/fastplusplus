# zune-entropy

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Entropy coders](README.md)</sub>

**Tier C** (first-party claim) · Study only · `Rust` · `no license` · 🔴 abandoned

> Rust order-0 Huffman and tANS block coders that out-decode FSE/Huff0 on enwik8 at slightly worse ratio.

| | |
|---|---|
| **Beats** | FSE library (Huff0 Huffman and FSE tANS modes), Yann Collet's FiniteStateEntropy |
| **Claimed result** | enwik8 Huffman: 940.97 MB/s encode and 1310.28 MB/s decode versus FSE/Huff0 at 924.6 and 1049.5 MB/s. tANS: 602.56 MB/s encode and 1022.93 MB/s decode versus FSE/TANS at 457.7 and 572.8 MB/s. README says the tANS is faster because it interleaves more. |
| **Workload** | Order-0 Huffman and tANS encode and decode of enwik8 on an AMD Ryzen 5 4500U, compared with FSE/Huff0 and FSE/TANS. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 5 4500U with Radeon Graphics, 6 cores, 8 MiB L3 |
| **Adoption** | 14 stars |
| **Last commit** | 2022-08-05 |
| **Links** | [repository](https://github.com/etemesi254/zune-entropy) · [benchmark](https://raw.githubusercontent.com/etemesi254/zune-entropy/HEAD/Readme.md) |

## Verdict

The author's README reports enwik8 on an AMD Ryzen 5 4500U: Huffman 940.97 MB/s encode and 1310.28 MB/s decode versus FSE/Huff0 924.6 and 1049.5 MB/s (about 1.25x decode, derived from page data), and tANS 602.56/1022.93 MB/s versus FSE/TANS 457.7/572.8 MB/s (about 1.8x decode, derived). The FSE numbers come from a different tool than this library's zcif_bin driver, and no compiler version or flags are stated.

## Use it when

- Studying or porting a compact, readable Rust implementation of interleaved tANS and multi-stream Huffman decoding
- Prototyping an order-0 entropy stage on x86-64 or aarch64 where decode speed matters more than the last 1-2% of ratio
- Benchmarking your own entropy coder against another FSE-style design on text-like data such as enwik8

## Skip it when

- Decoding untrusted or possibly truncated input: the bit readers do unchecked 8-byte reads (see gotchas)
- Production use: no LICENSE file, not on crates.io, README calls it beta and says some files (silesia/mozilla) fail
- When ratio matters: FSE beats it in both modes on enwik8 (63.26% vs 65.00% Huffman, 63.12% vs 63.90% tANS)
- When you need FSE/zstd wire compatibility, streaming, a C API, or adaptive/order-1 models
- When peak decode speed is the goal: hypersonic-rANS and htscodecs SIMD rANS decode several times faster

## How it is fast

The tANS decoder runs five interleaved 11-bit states over one little-endian bit reader lifted from Eric Biggers' xpack, with the table capped at 2^10 states and a golden-ratio state spread, which the source comment says fits 55 bits per flush branchlessly and is 'how we get an edge on FSE'; it packs symbol, bit count, next-state base and mask into one u64 table entry. The Huffman coder length-limits codes to 11 bits with a Kraft-sum heuristic, splits each block into five independent bitstreams decoded round-robin with a single 2048-entry lookup table, and uses x86 inline asm (sub/shrx) to keep the bit buffer in registers. Branchless 56-63-bit refills follow Fabian Giesen's 'reading bits in far too many ways' variant 4.

## Compared with alternatives

Pick it over FiniteStateEntropy only if you want a Rust codebase to read and adapt and accept 1-2% worse ratio; for speed hypersonic-rANS or htscodecs decode several times faster, and for a maintained Rust entropy coder constriction is the safer choice.

## Integration

| | |
|---|---|
| **Form** | crate (git dependency only; not published) |
| **Dependencies** | log 0.4 (criterion and rand as dev-dependencies) |
| **Minimum toolchain** | Rust 2021 edition; uses std::arch::asm!, so Rust 1.59 or later (the README's companion bench says rustc 1.58) |
| **Platforms** | any Rust target; x86/x86-64 get inline-asm bit-buffer paths and a runtime-detected BMI2 wrapper, others use plain Rust |
| **Thread safety** | not documented; the functions are pure over their arguments with no shared state, so separate calls on separate buffers should be independent |
| **Drop-in for the baseline** | no |

## Gotchas

- Memory safety: BitStreamReader::refill_fast and FSEStreamReader::refill_fast copy 8 bytes from src.as_ptr().add(position) with no bounds check, and the decode loops refill every few symbols while trusting the block length from the header; over-read is only detected after decoding finishes. A corrupt or crafted stream (large declared block length, small payload) can read past the input buffer through the safe public functions, and the final stream of the last block can read up to 7 bytes past the end even when the caller's buffer has no padding (code comment: 'The buffer must be padded with fill bytes in the end, if not, this becomes UB in the refill phase').
- unsafe_utils::extend calls Vec::set_len over uninitialized memory before decoding; if decoding returns an error, dest is left with uninitialized bytes in its length.
- Malformed headers panic instead of returning errors (direct src[0] and slice indexing; a header table_log above 10 indexes past the 1024-entry state array); huff_decompress panics if handed a tANS stream and vice versa.
- Source comment says changing CHUNK_SIZE to 1 &lt;&lt; 19 causes a hard error on test files; the block size is a compile-time constant.

## Known shortcomings

- Tier C: decode 1310 vs FSE Huff0 1049 MB/s at a worse ratio, with the FSE numbers taken from a separate tool; no license (Cargo.toml, crates.io 404), so reference. Rust.
- Memory-safety bug: both bit readers' refill_fast do unchecked 8-byte copy_nonoverlapping reads, and the over-read is checked only after decode, so corrupt or crafted input (large header block_length) reads past the buffer through the safe public fse_decompress/huff_decompress. The final block can over-read up to 7 bytes even on valid input without padding. unsafe_utils::extend uses set_len over uninitialised memory and leaves it in dest on the error path. Malformed headers panic (tbl_log above 10 indexes past the 1024-entry table). No licence, not on crates.io, beta, abandoned 2022; needs Rust 1.59+ (asm!). FSE comparison numbers came from a different tool.

## Caveats and trade-offs

First-party numbers on one file (enwik8). The benchmark driver etemesi254/zcif_bin (MIT, 20 iterations per run, needs rustc 1.58 or later) only times this library's coders, so the FSE/Huff0 and FSE/TANS figures were measured with a different tool; no compiler flags stated. FSE beats this library on compression ratio in both modes (63.26% versus 65.00% for Huffman, 63.12% versus 63.90% for tANS), and the Huffman encode win is under 2%. The repo is declared beta and some files (silesia/mozilla) do not work. No LICENSE file and no license field in Cargo.toml, and the crate is not published on crates.io (404), so the code is reference only.

Worse compression ratio than FSE on the same file: Huffman 65.00% versus 63.26%, tANS 63.90% versus 63.12%. The README says the Huffman part is a simple illustration. Rust only; no C API.

## Maintenance

Abandoned since August 2022, unlicensed (all rights reserved by default) and unpublished, so treat it as reference code to learn from, not to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The README shows first-party enwik8 speeds on an AMD Ryzen 5 4500U: Huffman 940.97/1310.28 MB/s versus FSE/Huff0 924.6/1049.5, and TANS 602.56/1022.93 versus FSE/TANS 457.7/572.8. The benchmark driver (etemesi254/zcif_bin) only times this library, so the FSE figures come from a separate tool, and no compiler version or flags are stated.
- **Verifier notes:** All numbers match the README. License absence confirmed (no license on the GitHub page, none in Cargo.toml, crate not on crates.io). Metadata confirmed: 14 stars, last commit 2022-08-05 (abandoned), not archived or a fork.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier; first-party benchmark
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/etemesi254/zune-entropy/HEAD/Readme.md>
  - <https://github.com/etemesi254/zune-entropy>
  - <https://github.com/etemesi254/zune-entropy/commits>
  - <https://raw.githubusercontent.com/etemesi254/zune-entropy/HEAD/Cargo.toml>
  - <https://crates.io/api/v1/crates/zune-entropy>
  - <https://github.com/etemesi254/zcif_bin>
- **Sources the enricher read:**
  - <https://github.com/etemesi254/zune-entropy>
  - <https://github.com/etemesi254/zune-entropy/tree/master/src>
  - <https://raw.githubusercontent.com/etemesi254/zune-entropy/HEAD/Readme.md>
  - <https://raw.githubusercontent.com/etemesi254/zune-entropy/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/etemesi254/zune-entropy/master/src/lib.rs>
  - <https://raw.githubusercontent.com/etemesi254/zune-entropy/master/src/constants.rs>
  - <https://raw.githubusercontent.com/etemesi254/zune-entropy/master/src/errors.rs>
  - <https://raw.githubusercontent.com/etemesi254/zune-entropy/master/src/fse_bitstream.rs>
  - <https://raw.githubusercontent.com/etemesi254/zune-entropy/master/src/fse_compress.rs>
  - <https://raw.githubusercontent.com/etemesi254/zune-entropy/master/src/fse_decompress.rs>
  - <https://raw.githubusercontent.com/etemesi254/zune-entropy/master/src/huff_bitstream.rs>
  - <https://raw.githubusercontent.com/etemesi254/zune-entropy/master/src/huff_compress.rs>
  - <https://raw.githubusercontent.com/etemesi254/zune-entropy/master/src/huff_decompress.rs>
  - <https://raw.githubusercontent.com/etemesi254/zune-entropy/master/src/unsafe_utils.rs>
  - <https://raw.githubusercontent.com/etemesi254/zune-entropy/master/src/utils.rs>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/etemesi254/zune-entropy`) · [data/wave9/enrich/raw/github_com_etemesi254_zune_entropy.json](../../../data/wave9/enrich/raw/github_com_etemesi254_zune_entropy.json) (enrichment confidence 0.7)

</details>
