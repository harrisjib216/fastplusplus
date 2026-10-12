# libzbitmap

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [General-purpose lossless compression](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C` · `MIT` · 🔴 abandoned

> Clean-room C reimplementation of Apple's closed LZBITMAP codec; format compatibility only, self-described as much slower than Apple's.

| | |
|---|---|
| **Beats** | lzfse (Apple LZBITMAP reference implementation, not open source) |
| **Claimed result** | None. README: 'For now it's much slower than the original, but the ratios obtained are similar.' |
| **Workload** | None: the README gives no benchmark; it only states the reimplementation is slower than Apple's original with similar ratios. |
| **Metric** | throughput |
| **Adoption** | 58 stars |
| **Last commit** | 2023-01-18 |
| **Links** | [repository](https://github.com/eafer/libzbitmap) |

## Verdict

No measurement exists: the README's only statement is that the reimplementation is 'much slower than the original' Apple LZBITMAP with similar ratios, and test/test.c reports compression ratio and correctness only, with no timing.

## Use it when

- Reading LZBITMAP-compressed files or xattrs from APFS volumes or iOS 16+ images on non-Apple platforms, where Apple's libcompression is unavailable.
- Producing LZBITMAP output that must round-trip through this library's own decoder (for example in filesystem tooling tests).
- Embedding a small, dependency-free MIT decoder in a C or C++ tool; the decoder is about 440 lines and is already reused in the linux-apfs-rw kernel module.

## Skip it when

- As a general-purpose fast compressor: the README says it is much slower than Apple's original, and there is no benchmark at all against lz4, zstd or lzfse.
- When you control the format: LZ4 or zstd give better speed, ratio and tooling, and LZFSE has an open reference implementation from Apple.
- For untrusted input through the size query: a NULL-destination zbm_decompress call on a crafted header can hang (see gotchas).
- Where long-term maintenance matters: 11 commits between 2022-11-22 and 2023-01-18, no releases, no issues filed, no fuzzing or CI in the repo.
- If you need encoder output certified as decodable by Apple's own implementation: test/test.c only checks Apple-made files decode correctly and that its own output round-trips through its own decoder.

## How it is fast

It is not a speed play. Data is cut into 32 KiB chunks; each 8-byte group is coded as an 8-bit bitmap saying which bytes are literal and which are copied from a fixed back-distance ('period'), with the 12 most frequent bitmaps stored in a 17-byte trailer, the rest in a metadata area and runs of the same bitmap number nibble-coded. The decoder works one byte at a time with a bounds check per byte, and the encoder scans up to 255 earlier positions per 8-byte group, plus memchr-guided candidates up to 64 KiB back, so throughput is low; the only speed lever is zbm_compress_chunk, which lets callers compress chunks on several threads.

## Compared with alternatives

Pick it only when the data is already LZBITMAP (APFS/iOS); for anything you encode yourself, LZFSE (Apple's open-source codec) or LZ4 are faster and better documented, and zstd gives a better ratio.

## Integration

| | |
|---|---|
| **Form** | static lib (two source files: libzbitmap.c and libzbitmap.h; Makefile builds libzbitmap.a) |
| **Dependencies** | none (libc only; the test program uses pthreads) |
| **Minimum toolchain** | C99 with GNU extensions (Makefile uses gcc --std=gnu99 -O3 -fno-strict-aliasing) |
| **Platforms** | any with a C compiler; the encoder's unaligned uint64_t loads assume a target that tolerates them (x86-64, arm64), and its match-cost heuristic assumes little-endian byte order |
| **Thread safety** | Reentrant: no global state, each compress call callocs its own roughly 25 KB state; zbm_compress_chunk is designed to be called from several threads on the same source buffer. |
| **Drop-in for the baseline** | no |

## Gotchas

- Hang on crafted input: with dest == NULL, zbm_handle_chunk returns before checking that the chunk length is at least the 6-byte header, so a chunk with len 0 and a nonzero decompressed length makes the zbm_decompress loop add 0 to src forever. The kernel port in linux-apfs-rw carries the same loop; whether its callers use the NULL query was not checked. Size queries on untrusted data should be avoided or capped.
- The encoder reads candidate matches with \*(uint64_t \*) casts at unaligned addresses (undefined behaviour in ISO C; it relies on -fno-strict-aliasing and on hardware that tolerates unaligned loads). zbm_compress_chunk also leaks its calloc'd state when the index overflows (it returns ZBM_OVERFLOW before free).
- Chunks may reference data from earlier chunks (back-distances up to 0xffff across chunk boundaries), so zbm_compress_chunk must be given the whole source buffer and the full output must be decoded in order into one contiguous buffer.
- Compressed output from zbm_compress_chunk must be concatenated in index order by the caller, and the stream ends with a 6-byte empty chunk (ZBM_LAST_CHUNK_SIZE); out_len is not written on error.

## Known shortcomings

- Not faster: the README says it is much slower than Apple's original LZBITMAP, and no numbers exist. Kept as a seed record for the open reimplementation. Last commit 2023-01-18, abandoned.
- zbm_decompress with dest NULL (size query) skips the len &gt;= 6 check, so a crafted chunk with len 0 and decmp_len &gt; 0 loops forever (same code in the linux-apfs-rw port). The encoder does unaligned \*(uint64_t\*) loads (UB without -fno-strict-aliasing). zbm_compress_chunk leaks state on ZBM_OVERFLOW. Byte-at-a-time decoder; tests only round-trip its own output.

## Caveats and trade-offs

No numeric comparison against lzfse, lz4 or any listed baseline; the README says it is much slower than Apple's original (closed-source) LZBITMAP, so it is a format-compatibility reimplementation, not a speed win. Built by reverse engineering via black-box testing. The last commit (2023-01-18, 'Add a license') is more than 3 years old; 11 commits, 58 stars. lzfse issue #62 only asks Apple to open-source LZBITMAP and has no numbers.

Black-box reverse-engineered reimplementation of Apple LZBITMAP; open source path to decode/encode APFS-style data. Not a speed play.

## Maintenance

Abandoned since 2023-01-18 (last commit 'Add a license', MIT, 58 stars), but its decoder lives on, ported under GPL-2.0+ OR MIT, in linux-apfs-rw and in a 2025 staging RFC for an in-kernel APFS driver; small enough to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification D, tier now D.
- **Tier reason:** The README has no numbers and only says the reimplementation is 'much slower than the original' Apple LZBITMAP with similar ratios; no benchmark exists in the repo.
- **Verifier notes:** Under the verifier rules this would be reject (not-faster / not-notable-tier-d); kept as confirm at tier D per the seed-record keep-and-document instruction, but the orchestrator may want decision keep with the shortcoming 'self-described slower than the original'. Metadata checked on github.com: MIT, 58 stars, not a fork or archived, last commit 2023-01-18, so maintenance_status corrected from stale to abandoned (&gt;3 years before 2026-10-01).
- **Fields the verifier corrected:** `maintenance_status`, `caveats`
- **Shortcomings recorded by:** no numbers
- **Pages the verifier opened:**
  - <https://github.com/eafer/libzbitmap>
  - <https://github.com/eafer/libzbitmap/commits/master>
- **Sources the enricher read:**
  - <https://github.com/eafer/libzbitmap>
  - <https://github.com/eafer/libzbitmap/commits/master>
  - <https://github.com/eafer/libzbitmap/tree/master/test>
  - <https://raw.githubusercontent.com/eafer/libzbitmap/HEAD/README.rst>
  - <https://raw.githubusercontent.com/eafer/libzbitmap/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/eafer/libzbitmap/HEAD/Makefile>
  - <https://raw.githubusercontent.com/eafer/libzbitmap/HEAD/libzbitmap.h>
  - <https://raw.githubusercontent.com/eafer/libzbitmap/HEAD/libzbitmap.c>
  - <https://raw.githubusercontent.com/eafer/libzbitmap/HEAD/test/test.c>
  - <https://raw.githubusercontent.com/eafer/libzbitmap/HEAD/test/Makefile>
  - <https://raw.githubusercontent.com/linux-apfs/linux-apfs-rw/HEAD/libzbitmap.c>
  - WebSearch snippets: https://github.com/linux-apfs/linux-apfs-rw, https://lkml.iu.edu/hypermail/linux/kernel/2503.2/06165.html (staging RFC v2 'init libzbitmap.{c,h} for decompression'), https://github.com/sgan81/apfs-fuse/issues/168
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/eafer/libzbitmap`) · [data/wave9/enrich/raw/github_com_eafer_libzbitmap.json](../../../data/wave9/enrich/raw/github_com_eafer_libzbitmap.json) (enrichment confidence 0.85)

</details>
