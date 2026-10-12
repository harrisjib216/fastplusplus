# Zippy (Nim deflate/zlib/gzip)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [General-purpose lossless compression](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Nim` · `MIT` · 🟢 active

> Pure-Nim deflate/zlib/gzip codec (plus zip and tar readers) that the author times as faster than zlib on small files.

| | |
|---|---|
| **Beats** | zlib via the nim-lang/zip wrapper (zlib version and build unstated; tests/bench.nim comments say the zlib path 'Requires zlib1.dll' and the README command uses a Windows-style path, so the README's 'zlib found on a fresh Linux install' may not describe the run shown) |
| **Claimed result** | README: 'around 1.5x - 2x faster than zlib found on a fresh Linux install'. Min-time rows, Zippy vs nim-lang/zip: uncompress alice29.txt.gz 0.233 vs 0.397 ms (1.70x), tor-list.gz 27.297 vs 36.613 ms (1.34x); compress best speed alice29.txt 0.643 vs 1.236 ms (1.92x), tor-list 26.106 vs 178.197 ms (6.8x); compress default alice29.txt 2.361 vs 5.726 ms (2.43x), urls.10K 13.364 vs 13.049 ms (0.98x), tor-list 409.542 vs 244.424 ms (0.60x, Zippy slower). Ratios derived from page data. |
| **Workload** | Deflate/gzip decompression and raw-deflate compression (best speed and default levels) of small corpus files (alice29.txt, urls.10K, rfctest3, randtest3, paper-100k.pdf, geo.protodata, gzipfiletest.txt, tor-list) timed with the benchy timeIt macro in tests/bench.nim |
| **Metric** | throughput |
| **Hardware** | Ryzen 5 5600X |
| **Compiler and flags** | nim c --gc:arc -d:release -r tests/benchmark.nim (README; the file is now tests/bench.nim). Nim version, backend C compiler and C flags not stated. |
| **Adoption** | 283 stars |
| **Last commit** | 2026-09-30 |
| **Links** | [repository](https://github.com/guzba/zippy) · [benchmark](https://github.com/guzba/zippy#performance) |

## Verdict

Author-run benchy timings on a Ryzen 5 5600X compiled with nim c --gc:arc -d:release, against zlib through the nim-lang/zip wrapper (zlib version and build unstated; bench comments say it needs zlib1.dll, so likely a Windows run): Zippy decompresses the test files 1.15x to 1.85x faster (8x on the microsecond-scale randtest3) and compresses at BestSpeed 1.6x to 6.8x faster (15x on randtest3), derived from page data, but at the default level it is slower on tor-list (409.5 vs 244.4 ms) and tied on urls.10K; Nim version and C backend compiler are not stated, compressed sizes are not shown, and the timed code predates the Huffman overflow fix.

## Use it when

- Nim programs that need gzip/zlib/deflate (HTTP Content-Encoding, small payloads, embedded assets) without linking zlib or shipping zlib1.dll.
- Decompressing small to medium in-memory gzip/zlib payloads, where the README shows 1.15x to 1.85x lower min time than zlib via nim-lang/zip on the non-trivial files (e.g. alice29.txt.gz 0.233 vs 0.397 ms, tor-list.gz 27.3 vs 36.6 ms).
- BestSpeed compression where output size matters less than time (alice29.txt 0.643 vs 1.236 ms; tor-list 26.1 vs 178.2 ms against zlib level 1).
- Cross-compiling Nim to targets where a C zlib is awkward (the README lists nim c, nim cpp and --cc:vcc; recent releases added emscripten and Mac C++ backend fixes).

## Skip it when

- C++ projects: zlib-ng or libdeflate give the same formats with a C API, published third-party benchmarks and SIMD-tuned paths.
- Default-level compression of the largest test input: on tor-list zippy took 409.5 ms vs zlib's 244.4 ms, and urls.10K was a tie (13.36 vs 13.05 ms).
- Streaming, partial or very large data: everything is decompressed into one in-memory string, there is no output size limit for zlib/deflate input, and partial raw-deflate decoding is an open request (issue #96).
- Multi-member or extra-field gzip (pigz/bgzip-style output): uncompressGzip assumes one member and rejects FEXTRA, and the FHCRC header CRC is skipped, not checked.
- Data written by zippy 0.10.x at levels 8-9 before 2026-09-30: a Huffman histogram overflow could emit invalid deflate streams (see gotchas).

## How it is fast

Inflate uses a 9-bit fast Huffman lookup table with a canonical-code slow path, a 64-bit bit buffer refilled with 8-byte unaligned loads, and 8-byte (copy64) match copies with a 16-byte fast path for short non-overlapping matches. BestSpeed replaces zlib's LZ77 with Snappy's match finder (from the author's supersnappy), and other levels use zlib-style lazy matching with good/lazy/nice/chain parameters and a 2^17-entry hash. CRC-32 uses SSE4.1+PCLMULQDQ and Adler-32 uses SSSE3 on x86-64 (runtime CPUID dispatch) and NEON on arm64; release builds turn Nim's bounds and overflow checks off in the hot modules.

## Compared with alternatives

Pick Zippy only inside Nim when you want deflate/gzip with zero C dependencies; for C or C++ use zlib-ng (drop-in zlib API, broad speedups) or libdeflate (faster whole-buffer deflate and CRC-32), and miniz if you need a tiny single-file C library.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none (pure Nim; uses std/sysrand on Nim &gt;= 1.6) |
| **Minimum toolchain** | Nim &gt;= 1.0.10 per zippy.nimble; README says it works with --gc:arc, --gc:orc and the default GC, and with nim c, nim cpp and --cc:vcc |
| **Platforms** | any Nim target; SIMD checksums on amd64 (SSSE3, SSE4.1+PCLMUL with runtime detection) and arm64 (NEON); 32-bit targets have had overflow and RangeDefect bugs, and a DivByZeroDefect on i386 Windows gzip is still open (issue #94) |
| **Thread safety** | not documented; compress/uncompress are pure functions over their arguments with no shared state seen in the source |
| **Drop-in for the baseline** | partial: produces and reads standard deflate/zlib/gzip streams interoperable with zlib (tests/validate.nim checks both directions), but the API is Nim whole-buffer calls, not zlib's z_stream interface, and preset dictionaries are not supported |

## Gotchas

- Correctness bug behind the benchmarked code: until PR #111 (merged 2026-09-30, after the last tagged 0.10.20) huffmanCodes counted symbols per code length in a uint8, so blocks with 256+ symbols at one length got wrong canonical codes and produced invalid deflate data (reported on multi-MB binary inputs, about 1 in 10 failing at levels 8-9; all 0.10.x affected). Version 0.10.19 also had an inflate bug on macOS arm64 that returned one extra byte for a multi-MB BestCompression stream (issue #108, fixed in 0.10.20 by removing that path).
- Release builds run inflate, deflate and the bit reader with Nim checks off; fuzzing found an out-of-bounds read on 1-byte raw-deflate input (issue #102, fixed in 0.10.19 'fix for tiny src len'), and tarball extraction trusted gzip ISIZE for allocation (issue #104, a memory DoS, closed). Treat older versions as unsafe on untrusted input.
- gzip output is not deterministic: compress writes a random 0-25 character file name into the gzip header (Heal-the-BREACH mitigation, issue #61), so identical input gives different bytes.
- The benchmark compares speed only; compressed sizes are not reported, and BestSpeed uses a Snappy-style matcher, so its ratio versus zlib level 1 is unknown. The README still links tests/benchmark.nim, now tests/bench.nim.

## Known shortcomings

- Nim, not C++. Nim version, C backend compiler and baseline zlib build are not stated (bench.nim comment: Requires zlib1.dll). Linked tests/benchmark.nim gives 404; the real file is tests/bench.nim. Default-level compress of tor-list runs at 0.60x of zlib (slower).
- Correctness bug behind the timed code: PR #111 (2026-09-30, after the 0.10.20 tag) fixes a uint8 Huffman histogram overflow that made all 0.10.x emit invalid deflate data (about 1 in 10 multi-MB binary inputs at levels 8-9); #108: inflate returned one extra byte on macOS arm64, fixed in 0.10.20. Release builds turn Nim bounds and overflow checks off. #102 out-of-bounds read on 1-byte input fixed in 0.10.19; #104 tar.gz ISIZE memory DoS closed; #94 DivByZeroDefect on i386 Windows still open. No output size limit, whole-buffer API only. Single-member gzip only, FEXTRA rejected, FHCRC skipped; gzip output has a random header filename, so not deterministic. Compressed sizes not reported.

## Caveats and trade-offs

First-party numbers. The comparison library is nim-lang/zip, a wrapper over a zlib whose version and build are unstated (bench comment says 'Requires zlib1.dll', suggesting a Windows run despite the README's Linux framing). Default-level compression is slower than zlib on the largest file (tor-list: 409.542 vs 244.424 ms) and about equal on urls.10K, so the '1.5-2x' summary holds for decompression, best-speed mode and small files, not for default-level compression of large inputs. Compression ratios are not reported. README links tests/benchmark.nim, which is now 404; the bench lives at tests/bench.nim. Nim version and C backend compiler missing.

Nim only (callable from C++ only by porting or through Nim's C backend); pure Nim, no dependencies; handles deflate, zlib, gzip, zip and tar.

## Maintenance

Actively maintained (last commit 2026-09-30, tagged release 0.10.20 from 2026-08-20) and MIT-licensed, but Nim-only, so for C++ it is a reference design rather than something to link; take the post-0.10.20 master or the next release for the Huffman fix.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification A, tier now C.
- **Tier reason:** First-party README tables against nim-lang/zip (a zlib wrapper) with CPU (Ryzen 5 5600X) and the nim command line, and public bench code (tests/bench.nim), but the Nim version, the backend C compiler and the zlib version/build of the baseline are all unstated, so it falls short of A.
- **Verifier notes:** Numbers match the README. Downgraded A to C: compiler version, C backend and baseline zlib build are unstated. Metadata checked: MIT, 283 stars, not archived, not a fork; last commit 2026-09-30 (PR #111, a Huffman histogram overflow fix).
- **Fields the verifier corrected:** `baseline`, `compiler_and_flags`, `claimed_speedup`, `workload`, `caveats`
- **Shortcomings recorded by:** first-party benchmark
- **Pages the verifier opened:**
  - <https://github.com/guzba/zippy>
  - <https://github.com/guzba/zippy/commits/master>
  - <https://github.com/guzba/zippy/tree/master/tests>
  - <https://raw.githubusercontent.com/guzba/zippy/HEAD/README.md>
  - <https://raw.githubusercontent.com/guzba/zippy/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/guzba/zippy/HEAD/tests/bench.nim>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/guzba/zippy/HEAD/README.md>
  - <https://raw.githubusercontent.com/guzba/zippy/HEAD/zippy.nimble>
  - <https://raw.githubusercontent.com/guzba/zippy/HEAD/src/zippy.nim>
  - <https://raw.githubusercontent.com/guzba/zippy/HEAD/tests/bench.nim>
  - <https://github.com/guzba/zippy/tree/master/src/zippy>
  - <https://raw.githubusercontent.com/guzba/zippy/HEAD/src/zippy/common.nim>
  - <https://raw.githubusercontent.com/guzba/zippy/HEAD/src/zippy/deflate.nim>
  - <https://raw.githubusercontent.com/guzba/zippy/HEAD/src/zippy/inflate.nim>
  - <https://raw.githubusercontent.com/guzba/zippy/HEAD/src/zippy/bitstreams.nim>
  - <https://raw.githubusercontent.com/guzba/zippy/HEAD/src/zippy/gzip.nim>
  - <https://raw.githubusercontent.com/guzba/zippy/HEAD/src/zippy/lz77.nim>
  - <https://raw.githubusercontent.com/guzba/zippy/HEAD/src/zippy/snappy.nim>
  - <https://raw.githubusercontent.com/guzba/zippy/HEAD/src/zippy/internal.nim>
  - <https://raw.githubusercontent.com/guzba/zippy/HEAD/src/zippy/crc.nim>
  - <https://raw.githubusercontent.com/guzba/zippy/HEAD/src/zippy/crc32_simd.nim>
  - <https://raw.githubusercontent.com/guzba/zippy/HEAD/src/zippy/adler32.nim>
  - <https://raw.githubusercontent.com/guzba/zippy/HEAD/src/zippy/adler32_simd.nim>
  - <https://raw.githubusercontent.com/guzba/zippy/HEAD/src/zippy/ziparchives.nim>
  - <https://raw.githubusercontent.com/guzba/zippy/HEAD/src/zippy/tarballs.nim>
  - <https://github.com/guzba/zippy/issues?q=is%3Aissue>
  - <https://github.com/guzba/zippy/pull/111>
  - <https://github.com/guzba/zippy/issues/108>
  - <https://github.com/guzba/zippy/issues/102>
  - <https://github.com/guzba/zippy/commits/master>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/guzba/zippy`) · [data/wave9/enrich/raw/github_com_guzba_zippy.json](../../../data/wave9/enrich/raw/github_com_guzba_zippy.json) (enrichment confidence 0.75)

</details>
