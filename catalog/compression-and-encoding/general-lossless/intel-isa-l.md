# ISA-L (igzip)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [General-purpose lossless compression](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C (with assembly)` · `BSD-3-Clause` · 🟢 active

> Intel's assembly-tuned deflate/gzip/zlib codec (igzip): about 4.8x zlib -1 compression speed and 2.3x its decompression speed.

| | |
|---|---|
| **Beats** | zlib |
| **Claimed result** | zlib-ng issue 1486 (powturbo, TurboBench, silesia.tar, Ryzen 6600HS): igzip 1 compresses at 615.11 MB/s and ratio 36.9% vs zlib 1 at 127.47 MB/s and 36.5% (4.8x, derived from page data), and decompresses at 1020.09 vs 448.95 MB/s (2.3x, derived from page data). igzip 2: 598.69 MB/s at 36.1%; igzip decode ranges 969-1081 MB/s vs zlib 449-484 MB/s across levels. At higher levels zlib reaches better ratios (zlib 9: 31.9% at 15.55 MB/s) that igzip does not offer. |
| **Workload** | Compress silesia.tar with igzip levels 0-3 vs zlib and libdeflate via TurboBench. |
| **Metric** | throughput |
| **Hardware** | Lenovo Ideapad 5 Pro, AMD Ryzen 6600HS |
| **Adoption** | 1.1k stars |
| **Last commit** | 2026-09-30 |
| **Links** | [repository](https://github.com/intel/isa-l) · [benchmark](https://github.com/zlib-ng/zlib-ng/issues/1486) |

## Verdict

An independent TurboBench run by its author in zlib-ng issue 1486 (May 2023, silesia.tar, AMD Ryzen 6600HS laptop, compiler not stated) measured igzip level 1 compressing at 615 MB/s with 36.9% ratio vs zlib level 1 at 127 MB/s with 36.5% (4.8x, derived from page data), and igzip decompressing at 969-1081 MB/s vs zlib's 449-484 MB/s (about 2.3x).

## Use it when

- High-throughput gzip/zlib production where output must stay deflate-compatible: storage, log shipping, HTTP responses, container image layers (containerd can call igzip -cd, per issue #255).
- Fast compression at ratios near zlib -1: in the TurboBench run igzip -1 reached 615 MB/s at 36.9% against zlib -1 at 127 MB/s and 36.5%.
- Decompressing gzip/deflate faster than zlib (about 970-1080 MB/s vs 449-484 MB/s for zlib in the same run) when you cannot switch formats.
- x86-64 servers, especially with AVX2 or AVX-512, where Intel tuned the assembly; aarch64 and riscv64 have their own kernels.
- Projects that also need ISA-L's CRC, erasure-code or RAID kernels and want a single dependency.

## Skip it when

- Archival or bandwidth-bound use where ratio matters: igzip's best level (3, 35.5%) is worse than zlib -6/-9 (zlib -9 31.9%) and libdeflate (-6 31.9%, -12 30.5%) in the same table.
- Decompression only: libdeflate decoded slightly faster (1075-1134 MB/s) than igzip in the same run, and has a simpler build.
- Builds without NASM 2.14.01+ (x86-64) or on 32-bit x86, which v2.32 dropped; other architectures fall back to portable C base functions without the speedup.
- Code that needs an exact zlib API or behaviour: the shim is marked experimental, Linux-only, intercepts a subset of functions and skips custom zlib headers and automatic gzip header detection; SYNC_FLUSH/FULL_FLUSH always emit a sync marker, unlike zlib.
- Untrusted inputs where you want a hardened API: the README says parameters are not fully validated (NULL or invalid inputs are undefined behaviour).

## How it is fast

The hot loops are hand-written assembly (igzip_body.asm, igzip_deflate_hash.asm, igzip_decode_block_stateless\*.asm) for SSE, AVX2 and AVX-512 on x86-64, with aarch64 and riscv64 ports, chosen at runtime by multibinary dispatchers. Compression trades ratio for speed: only four levels (0-3), small hash tables (8K entries at levels 0-1) and greedy matching; level 0 encodes in one pass with a default or user-trained Huffman table, while level 1 and up write an intermediate token stream and then build fully dynamic Huffman codes in a second pass (the '2-pass fully-dynamic' mode of v2.18). Decompression uses two-level Huffman lookup tables (12-bit primary for literal/length, 10-bit for distance) so most symbols decode in one table lookup.

## Compared with alternatives

Pick igzip over zlib-ng or libdeflate when you need the fastest deflate-compatible compression at low levels (in the TurboBench run, igzip -1 at 615 MB/s vs libdeflate -3 at 185 MB/s) and can accept a lower ratio; pick libdeflate for best deflate ratio or one-shot decompression, zlib-ng for a mature zlib-API drop-in, and LZ4 or zstd if you are free to leave the deflate format.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (autotools, Makefile.unx, nmake on Windows; CMake experimental and only verified on x86_64) |
| **Dependencies** | none at runtime; NASM 2.14.01+ to build on x86-64, gas 2.24+ and GCC 10.1+ on aarch64, gas 2.39+ and GCC 12.1+ for RISC-V vector |
| **Minimum toolchain** | C compiler (gcc, clang, icc or MSVC) plus an assembler as above; C API with extern "C" guards |
| **Platforms** | x86-64 (SSE through AVX-512, runtime dispatch), aarch64, riscv64 (RVV); Linux, Windows, macOS, FreeBSD; portable C base functions elsewhere; 32-bit x86 removed in v2.32 |
| **Thread safety** | not documented in the README; all compression and decompression state lives in caller-owned isal_zstream / inflate_state structs (plus level_buf), so one stream per thread is the natural pattern; issue #249 (July 2023) asked for thread-safety documentation |
| **Drop-in for the baseline** | partial — deflate/gzip/zlib output is compatible, but the native API differs from zlib; the experimental isal-shim.so LD_PRELOAD layer covers deflateInit/deflate/inflate and related calls, crc32 and adler32, falling back to system zlib for the rest |

## Gotchas

- Levels 1-3 fail with ISAL_INVALID_LEVEL_BUF unless you allocate level_buf yourself (suggested sizes ISAL_DEF_LVLx_DEFAULT); only levels 0-3 exist, so zlib levels 4-9 have no equivalent.
- v2.32.1 fixed several memory-safety bugs (integer-overflow out-of-bounds write in isal_write_gzip_header, use-after-free in generate_custom_hufftables, an internal buffer overrun in igzip, zlib DICTID byte order); stay on 2.32.1 or later.
- Open issue #405 (April 2026) reports that isal_inflate_stateless() can leave its loop early and skip the CRC check on a successful decode; check return codes and verify checksums yourself if this matters.
- Compile-time options IGZIP_HIST_SIZE (window, default 32K) and LONGER_HUFFTABLE change struct layouts, so the library and its users must be built with the same settings.

## Known shortcomings

- Tier B on zlib-ng discussion #2351 and issue #986: the record had misread the zlib-ng level 9 row (27.79 MB/s) as zlib 9 (15.55 MB/s); corrected claim is igzip 1 vs zlib 1 compress 615.11 vs 127.47 MB/s (4.8x) and decode 1020.09 vs 448.95 (2.3x), derived from page data. Compiler and flags unstated.
- Open issue #405 (Apr 2026): isal_inflate_stateless may exit early and skip the CRC check. v2.32.1 fixed an out-of-bounds write in isal_write_gzip_header, a use-after-free in generate_custom_hufftables and an igzip buffer overrun; the README says parameters are not validated. The zlib shim is experimental and Linux-only; 32-bit x86 was dropped in v2.32. Best ratio (level 3, 35.5%) is worse than zlib -6/-9 and libdeflate decodes faster (1075-1134 MB/s).

## Caveats and trade-offs

Ratios are only near-matched at level 1 (igzip 36.9% vs zlib 36.5%); igzip's best ratio (35.5%, level 3) is worse than zlib 6/9. The original record misread the zlib_ng 9 row (27.79 MB/s, 32.2%) as zlib 9; zlib 9 is 15.55 MB/s at 31.9%. libdeflate decodes slightly faster than igzip in the same table (1075-1134 MB/s). Compiler and flags unstated in the issue. Repo README lists features but gives no numbers.

Deflate-compatible output at lower ratio than zlib at comparable speeds; x86 and AArch64 assembly kernels; igzip CLI.

## Maintenance

Actively maintained by Intel (last commit 2026-09-30, release v2.32.1), BSD-3-Clause and packaged by distros and conda-forge, so it is easy to adopt as a system library, though building from source needs NASM on x86-64.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now B.
- **Tier reason:** Independent TurboBench run by its author (powturbo) in zlib-ng issue 1486 on a Ryzen 6600HS compares igzip levels 0-3 against zlib levels 1-9 on silesia.tar; compiler and flags are not stated, so not A.
- **Verifier notes:** Record's number for 'zlib level 9' was actually the zlib_ng 9 row; claimed_speedup rewritten with the level-1 near-matched pair and decode numbers that the record said were not seen. License BSD-3-Clause confirmed from LICENSE file; last commit 2026-09-30 confirmed.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/intel/isa-l>
  - <https://github.com/intel/isa-l/commits/master>
  - <https://raw.githubusercontent.com/intel/isa-l/HEAD/LICENSE>
  - <https://github.com/zlib-ng/zlib-ng/issues/1486>
- **Sources the enricher read:**
  - <https://github.com/intel/isa-l>
  - <https://raw.githubusercontent.com/intel/isa-l/HEAD/README.md>
  - <https://raw.githubusercontent.com/intel/isa-l/HEAD/include/igzip_lib.h>
  - <https://raw.githubusercontent.com/intel/isa-l/HEAD/Release_notes.txt>
  - <https://raw.githubusercontent.com/intel/isa-l/HEAD/SECURITY.md>
  - <https://raw.githubusercontent.com/intel/isa-l/HEAD/doc/build.md>
  - <https://raw.githubusercontent.com/intel/isa-l/HEAD/doc/test.md>
  - <https://raw.githubusercontent.com/intel/isa-l/HEAD/configure.ac>
  - <https://raw.githubusercontent.com/intel/isa-l/HEAD/Makefile.am>
  - <https://raw.githubusercontent.com/intel/isa-l/HEAD/igzip/shim/README.md>
  - <https://raw.githubusercontent.com/intel/isa-l/HEAD/cmake/README.md>
  - <https://github.com/intel/isa-l/tree/master/igzip>
  - <https://github.com/intel/isa-l/issues?q=is%3Aissue+igzip>
  - <https://github.com/intel/isa-l/issues/405>
  - <https://github.com/intel/isa-l/issues/249>
  - <https://github.com/intel/isa-l/issues/255>
  - <https://github.com/zlib-ng/zlib-ng/issues/1486>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/intel/isa-l`) · [data/wave9/enrich/raw/github_com_intel_isa_l.json](../../../data/wave9/enrich/raw/github_com_intel_isa_l.json) (enrichment confidence 0.8)

</details>
