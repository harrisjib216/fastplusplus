# Snappy

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [General-purpose lossless compression](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> Google's byte-oriented LZ77 codec: about 5x faster compression and 3x faster decompression than zlib -1, with larger output.

| | |
|---|---|
| **Beats** | zlib (fastest mode, level 1) |
| **Claimed result** | lzbench 2.4 (silesia.tar, one thread of an EPYC 9555P): snappy 1.3.1 compresses at 457 MB/s and decompresses at 976 MB/s at 47.85% size vs zlib 1.3.2 -1 at 89.0 / 297 MB/s, 36.45%: about 5.1x faster compression and 3.3x faster decompression than zlib's fastest level, with output about 31% larger (derived from page data). Against zlib-ng 2.3.3 -1 (196 / 466 MB/s, 44.41%) the margin is about 2.3x / 2.1x (derived from page data). README (first-party, Core i7, model not stated): 'an order of magnitude faster' than zlib's fastest mode for most inputs, about 250 MB/s compress and 500 MB/s decompress or more on the slowest inputs. |
| **Workload** | Single-thread in-memory compression and decompression of silesia.tar in lzbench 2.4; the README's numbers come from Snappy's own testdata suite. |
| **Metric** | throughput |
| **Hardware** | Independent: single thread of an AMD EPYC 9555P at 3.20 GHz, turbo off (lzbench 2.4). README: single core of a Core i7 in 64-bit mode (model not stated). |
| **Compiler and flags** | gcc 15.2.0 (lzbench 2.4 release binary lzbench24_x86_64-linux-gnu-gcc15); lzbench v2.4 Makefile OPT_FLAGS_O3: -fomit-frame-pointer -fstrict-aliasing -O3 -DNDEBUG (a few codecs use the -O2 variant); run options -eALL -t8,8 -o1c4 |
| **Adoption** | 6.6k stars; used in production at Google |
| **Last commit** | 2026-09-18 |
| **Links** | [repository](https://github.com/google/snappy) · [benchmark](https://github.com/inikep/lzbench) |

## Verdict

Independent lzbench 2.4 (gcc 15.2.0 release binary, single thread of an AMD EPYC 9555P at 3.20 GHz, turbo off, silesia.tar): snappy 1.3.1 compresses at 457 MB/s and decompresses at 976 MB/s at 47.85% size versus zlib 1.3.2 -1 at 89.0 and 297 MB/s at 36.45%, about 5.1x and 3.3x faster with larger output (derived from page data). The README's 'order of magnitude faster than zlib's fastest mode' is a first-party claim on an unnamed Core i7.

## Use it when

- RPC payloads, cache values, column blocks and log records where CPU per byte matters more than ratio, or where peers already speak the Snappy format (it has compressed petabytes in Google production, per the README).
- Mixed or partly incompressible data: the skip heuristic keeps throughput high on already-compressed content.
- Untrusted input: the README says the decompressor is designed not to crash on corrupted or malicious input, and IsValidCompressedBuffer checks a buffer at least about 4x faster than decoding it.
- Code that needs a zero-allocation compressor: v1.3.1 adds CompressionContext with a caller-provided workspace.

## Skip it when

- New designs free to choose a format: in the same lzbench 2.4 run, lz4 1.10.0 compresses faster (550 vs 457 MB/s) and decompresses about 3.9x faster (3832 vs 976 MB/s) at the same ratio, and zstd -1 gives much smaller output (34.53% vs 47.85%) at similar speed.
- When ratio matters: output is 20-100% larger than zlib's fastest mode per the README (47.85% vs 36.45% of input on silesia.tar).
- Inputs of 4 GiB or more in one call: Compress returns zero and writes nothing for inputs of 2^32 bytes or more; split the data or use the framing format.
- 32-bit targets on 1.3.x: issue #266 reports Snappy.LiteralLengthU32Overflow failing on i386 and armhf (corrupt input accepted as valid), a regression from 1.2.2 with no fix yet.
- Big-endian or strict-alignment CPUs: the README warns it assumes little-endian and cheap unaligned loads and may run slower elsewhere.

## How it is fast

Input is cut into 64 KiB blocks; each is matched with a single 4-byte hash table of 16-bit offsets (up to 2^15 entries, CRC32 instruction as hash where available) and emitted as byte-aligned literal and copy tags with no entropy coding. A 'heuristic match skipping' rule widens the stride after every 32 bytes without a match, so incompressible data such as JPEG passes through quickly. The decoder translates tags through a lookup table and copies with unaligned 64/128-bit loads, plus SSSE3/NEON shuffle masks to expand short repeating patterns; BMI2 and x86/ARM CRC32 paths are picked at build time.

## Compared with alternatives

Pick Snappy when the Snappy format is required for interoperability or you are already on Google's stack; for a new choice, LZ4 matches its ratio with much faster decompression, zstd -1 gives a far better ratio at similar speed, and LZAV claims to beat it on both speed and ratio (first-party numbers).

## Integration

| | |
|---|---|
| **Form** | static lib (default) or shared lib via CMake (BUILD_SHARED_LIBS); C++ with a C API |
| **Dependencies** | none at runtime; bundled GoogleTest and Google Benchmark only for tests and benchmarks |
| **Minimum toolchain** | C++11, CMake 3.10+; Clang is the supported compiler, GCC and MSVC best-effort |
| **Platforms** | x86, x86-64, ARMv7, AArch64 tuned (SSSE3, BMI2, CRC32, NEON paths); RISC-V improved in 1.3.1; other platforms portable but slower |
| **Thread safety** | Free functions with no shared state are documented only implicitly; the header says a CompressionContext may be reused for sequential calls but must not be used from multiple threads at once. |
| **Drop-in for the baseline** | no |

## Gotchas

- The CMake build compiles with -fno-rtti and -fno-exceptions, so code that subclasses snappy::Source/Sink against a shared libsnappy can fail to link with 'undefined symbol: typeinfo for snappy::Source' (open issue #184).
- Compression level 2 (added in 1.2.1) is marked EXPERIMENTAL in snappy.h and may fall back to level 1 later; levels 3 and up are not supported.
- MSVC builds older than /arch:AVX2 must set SNAPPY_HAVE_SSSE3, SNAPPY_HAVE_BMI2 and related macros by hand, or the fast paths stay off.
- Versions before 1.2.2 could corrupt data when compressed size exceeded 4 GB (for example near-4 GB incompressible input), per NEWS.

## Known shortcomings

- Raised C to B via lzbench 2.4: 457/976 MB/s vs zlib -1 89.0/297, about 5.1x compress and 3.3x decompress (derived from page data), not the README's 'order of magnitude'.
- In the same lzbench 2.4 run lz4 1.10.0 hits the same ratio and decompresses 3832 vs 976 MB/s. Open issue #266: 1.3.1 32-bit regression (i386/armhf, LiteralLengthU32Overflow, corrupt input accepted); CMake -fno-rtti breaks Source/Sink subclassing against the shared library (issue #184); Compress returns 0 for input of 2^32 bytes or more; level 2 is marked EXPERIMENTAL; pre-1.2.2 had a &gt;4 GB corruption bug.

## Caveats and trade-offs

The independent measurement shows about 5x (compress) and 3x (decompress) over zlib -1, not the README's 'order of magnitude'. Modern codecs beat it in the same table: lz4 1.10.0 at 550 / 3832 MB/s with a similar ratio (47.60%), and zstd 1.5.7 -1 at 411 / 1351 MB/s with a much better ratio (34.53%). README numbers are first-party with no CPU model, compiler or flags.

Much lower compression ratio than zlib (files 20-100% larger). Optimized for 64-bit little-endian x86 with cheap unaligned loads; may run slower elsewhere.

## Maintenance

Actively maintained by Google (v1.3.1, 2026-09-18) under BSD-3-Clause with a stable bitstream; Google says it will not accept build-system or platform changes outside its own configurations.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded from C: the independent lzbench 2.4 suite (public code, gcc 15.2.0 release binary, single thread of an AMD EPYC 9555P, silesia.tar) lists snappy 1.3.1 at 457 / 976 MB/s, 47.85% vs zlib 1.3.2 -1 at 89.0 / 297 MB/s, 36.45%. Flags are not on the results page, so B, not A. The README's own Core i7 numbers remain first-party.
- **Retiered** B to A: Raised B to A for tier consistency with FastLZ (batch verdict A on the same table): the evidence is the lzbench 2.4 README table, an independent public suite (inikep/lzbench, tag v2.4) whose release binary lzbench24_x86_64-linux-gnu-gcc15 is built with gcc 15.2.0 from the public Makefile (OPT_FLAGS_O3 = -fomit-frame-pointer -fstrict-aliasing -O3 -DNDEBUG, line 147; some codecs use the -O2 variant, line 146), run single-threaded on an AMD EPYC 9555P at 3.20 GHz with -eALL -t8,8 -o1c4 on silesia.tar. Compiler, flags, CPU model and harness are all public, so the run is reproducible and meets tier A; the earlier B verdicts counted the flags as unstated because they are not repeated on the results page.
- **Verifier notes:** README claims verified verbatim; lzbench gives the third-party numbers. Metadata OK: BSD-3-Clause, 6.6k stars, last commit 2026-09-18 (v1.3.1).
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `hardware`, `compiler_and_flags`, `workload`, `caveats`
- **Shortcomings recorded by:** independent: lzbench 2.4 README; enricher
- **Pages the verifier opened:**
  - <https://github.com/google/snappy>
  - <https://github.com/google/snappy/commits>
  - <https://raw.githubusercontent.com/google/snappy/HEAD/README.md>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/README.md>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/Makefile>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/google/snappy/HEAD/README.md>
  - <https://raw.githubusercontent.com/google/snappy/HEAD/NEWS>
  - <https://raw.githubusercontent.com/google/snappy/HEAD/snappy.h>
  - <https://raw.githubusercontent.com/google/snappy/HEAD/snappy.cc>
  - <https://raw.githubusercontent.com/google/snappy/HEAD/snappy-c.h>
  - <https://raw.githubusercontent.com/google/snappy/HEAD/snappy-sinksource.h>
  - <https://raw.githubusercontent.com/google/snappy/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/google/snappy/HEAD/framing_format.txt>
  - <https://github.com/google/snappy/issues>
  - <https://github.com/google/snappy/issues/266>
  - <https://github.com/google/snappy/issues/184>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/README.md>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/google/snappy`) · [data/wave9/enrich/raw/github_com_google_snappy.json](../../../data/wave9/enrich/raw/github_com_google_snappy.json) (enrichment confidence 0.85)

</details>
