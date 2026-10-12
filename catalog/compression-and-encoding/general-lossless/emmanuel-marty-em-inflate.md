# em_inflate

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [General-purpose lossless compression](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `Zlib` · 🔴 abandoned

> Single-file, one-call memory-to-memory inflate for zlib, gzip and raw deflate; 11-16% faster than zlib 1.2.11 with checksums on.

| | |
|---|---|
| **Beats** | zlib (inflate 1.2.11) |
| **Claimed result** | enwik8: zlib inflate 1.2.11 426,167 us, em_inflate with checksum 358,118 us (84%), skipping checksum 275,847 us (64%); texture: 127,945 us vs 114,369 us (89%) vs 105,476 us (82%). Derived from page data: about 1.19x and 1.54x on enwik8, 1.12x and 1.21x on the texture file. |
| **Workload** | Memory-to-memory decompression of enwik8 (gzip -9 bitstream, 100,000,000 bytes to 36,445,248) and a 32,212,992-byte raw texture file (zlib bitstream, gzip -9 to 13,721,537). |
| **Metric** | throughput |
| **Hardware** | 'core i7' only, no model |
| **Compiler and flags** | clang 6.0.0 -O3 stated, but only for the code-size table (linux x86_64); the timing table gives no compiler or flags |
| **Adoption** | 80 stars, 13 forks |
| **Last commit** | 2022-10-12 |
| **Links** | [repository](https://github.com/emmanuel-marty/em_inflate) · [benchmark](https://raw.githubusercontent.com/emmanuel-marty/em_inflate/HEAD/README.md) |

## Verdict

Author's README timings on an unspecified 'core i7' with no stated compiler or flags for the timing run: enwik8 gzip -9 stream decodes in 358,118 us with checksum and 275,847 us without, versus 426,167 us for zlib inflate 1.2.11 (1.19x and 1.54x, derived from page data); a 32 MB texture zlib stream takes 114,369 / 105,476 us versus 127,945 us (1.12x / 1.21x). The repository contains no timing harness, only an example CLI with a fixed 200,000,000-byte output buffer.

## Use it when

- Decompressing whole gzip or zlib assets already in memory (game data, textures, embedded resources) where you know or can bound the output size.
- Embedded or size-sensitive builds: about 15 KB of code plus rodata with checksums and about 9 KB without, per the README (clang 6.0.0 -O3, x86-64).
- Replacing a zlib dependency in a read-only path with a single vendored .c/.h pair under the zlib license.
- Trusted input where you can afford to skip checksum verification for the extra speed (README: 64% of zlib's time on enwik8 without checksum).

## Skip it when

- Untrusted or possibly truncated input: stored blocks are memcpy'd without checking that the declared length is present in the input (heap over-read), and other edge cases are not hardened (see gotchas).
- Streaming or unknown-size output: there is no incremental API, and the output buffer must hold the whole result.
- When the fastest inflate is the goal: the baseline is zlib 1.2.11 from 2017, and libdeflate, zlib-ng and Wuffs are not compared.
- Multi-member gzip files, preset-dictionary zlib streams, or anything needing compression: none are supported.
- 64-bit targets other than x86-64 and aarch64 (for example ppc64 or RISC-V) fall back to the 32-bit bit-buffer path, which is not benchmarked.

## How it is fast

A 64-bit LSB bit buffer refilled 32 bits at a time with an unaligned load on x86-64 (byte loads on aarch64), and canonical Huffman decoding through a 10-bit fast lookup table (NFASTSYMBOLBITS) that returns symbol plus length in one load, falling back to a bit-by-bit canonical walk for longer codes. Length and distance bases plus extra-bit counts are folded into the decoded symbol values, and matches with offset &gt;= 16 away from the buffer end are copied with 16-byte memcpy chunks. Decoding a whole buffer in one call means matches read straight from the output buffer with no separate sliding window; checksums use Stephan Brumme's slicing-by-4 crc32 and Mark Adler's adler32.

## Compared with alternatives

Pick em_inflate over miniz when you only need one-shot decoding and want the smallest code; pick libdeflate (also whole-buffer, much faster and fuzzed) or Wuffs (memory-safe by construction) whenever input is untrusted or raw speed matters more than a 1,200-line single file.

## Integration

| | |
|---|---|
| **Form** | source-drop (lib/em_inflate.c and lib/em_inflate.h) |
| **Dependencies** | none (libc only: string.h, stdlib.h, sys/types.h) |
| **Minimum toolchain** | C99 (mixed declarations, inline); a Makefile with cc -O3 and a VS2017 project are provided |
| **Platforms** | any; fast 64-bit bit buffer on x86-64 and aarch64, unaligned 32-bit refill only on x86-64 |
| **Thread safety** | reentrant: all state is on the stack and tables are const (inferred from the code; not documented) |
| **Drop-in for the baseline** | partial — replaces zlib uncompress()-style one-shot use, not the inflate() stream API |

## Gotchas

- Stored blocks: em_inflate_copy_stored checks output room but not input room, so a truncated or crafted stream with a large LEN copies past the end of the input buffer.
- If the input runs out while reading a block header, get_bits returns (unsigned)-1, no switch case matches, and the uninitialized nBlockResult is used; the bit reader can also let its bit count go negative on truncated input.
- Invalid symbols are accepted: literal/length codes 286-287 decode as a literal 0 byte, and distance codes 30-31 decode as offset 0 (copying not-yet-written output bytes) instead of failing; with checksums on, the trailer check will usually reject these, but raw deflate has no trailer.
- Gzip header parsing skips the FHCRC field before FEXTRA/FNAME/FCOMMENT instead of after them, so headers that set FHCRC together with those fields are misparsed; the gzip ISIZE trailer is not checked. The x86-64 refill reads through an unsigned int\* cast (alignment and strict-aliasing UB, fine on mainstream compilers).

## Known shortcomings

- README numbers date from June 2019 and predate the 2019-2020 overflow and stack fixes (the 2022 commits are cosmetic). Baseline zlib 1.2.11 on a Core i7 with clang 6.0.0 -O3, model not stated.
- Safety bugs read in source: the stored-block memcpy skips the input-length check (heap over-read on truncated or crafted input); input running out at a block header leaves nBlockResult uninitialised; codes 286-287 decode as literal 0 and distance codes 30-31 as offset 0 instead of an error; gzip FHCRC is skipped before FEXTRA/FNAME, so combined headers misparse; ISIZE not checked; unaligned uint\* casts on x86-64. No timing harness in the repo; the example uses a fixed 200 MB output buffer.

## Caveats and trade-offs

First-party README numbers only. CPU model, compiler flags for the timing run, repeat counts and the benchmark harness are not given. Baseline is zlib 1.2.11 (2017), not a current zlib or zlib-ng/libdeflate, which are much faster than stock zlib at inflate. The README with these numbers was last updated in June 2019 ('Faster codeword reversal. Update README.'); robustness fixes followed (buffer overflow fix August 2020, merged October 2020), so the timings predate those fixes; the only 2022 commits are cosmetic (error-message style, commenting out unused code). The 'skip checksum' row does not verify integrity, so the like-for-like gain versus zlib (which verifies) is the 84%/89% row. License: zlib license, with the gzip crc32 code by Stephan Brumme under a zlib-like license, per README. Original that inflatecpp ports.

Single file em_inflate.c/.h, single function call, memory-to-memory only: no streaming API, so it is not a drop-in replacement for the zlib inflate stream interface. Needs the whole input and output buffers in memory. Under 1,200 lines including about 300 lines of checksum code. The headline 64% needs checksum verification skipped, which gives up integrity checking.

## Maintenance

Abandoned: last functional changes were a bounds-check fix in the Huffman table setup (August-October 2020), and 2022 commits are cosmetic; zlib-licensed and small enough to vendor, but fuzz it or add input-length checks before using it on untrusted data.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** README gives first-party timings against zlib inflate 1.2.11 on enwik8 and a texture file, but CPU is only 'core i7', the timing compiler/flags are not given (clang 6.0.0 -O3 is stated only for the code-size table), and no benchmark harness is published.
- **Verifier notes:** All six timings match the README. Corrected the caveat that called the post-2022 commits overflow/stack fixes: those fixes are 2019-2020 and the 2022 commits are cosmetic. Metadata (80 stars, 13 forks, last commit 2022-10-12, abandoned) confirmed.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** first-party benchmark
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/emmanuel-marty/em_inflate/HEAD/README.md>
  - <https://github.com/emmanuel-marty/em_inflate>
  - <https://github.com/emmanuel-marty/em_inflate/commits>
- **Sources the enricher read:**
  - <https://github.com/emmanuel-marty/em_inflate>
  - <https://github.com/emmanuel-marty/em_inflate/commits>
  - <https://github.com/emmanuel-marty/em_inflate/issues?q=is%3Aissue>
  - <https://github.com/emmanuel-marty/em_inflate/commit/e536ec7>
  - <https://github.com/emmanuel-marty/em_inflate/commit/0ea8a01>
  - <https://raw.githubusercontent.com/emmanuel-marty/em_inflate/HEAD/README.md>
  - <https://raw.githubusercontent.com/emmanuel-marty/em_inflate/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/emmanuel-marty/em_inflate/HEAD/Makefile>
  - <https://raw.githubusercontent.com/emmanuel-marty/em_inflate/HEAD/lib/em_inflate.c>
  - <https://raw.githubusercontent.com/emmanuel-marty/em_inflate/HEAD/lib/em_inflate.h>
  - <https://raw.githubusercontent.com/emmanuel-marty/em_inflate/HEAD/example/main.c>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/emmanuel-marty/em_inflate`) · [data/wave9/enrich/raw/github_com_emmanuel_marty_em_inflate.json](../../../data/wave9/enrich/raw/github_com_emmanuel_marty_em_inflate.json) (enrichment confidence 0.8)

</details>
