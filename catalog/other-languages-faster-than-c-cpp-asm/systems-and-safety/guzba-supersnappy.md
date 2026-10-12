# Supersnappy

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Systems and safety](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Nim` · `MIT` · 🟢 active

> Pure-Nim raw Snappy codec; its 2022 README table beats snappy-c everywhere and a libsnappy build on text, loses three files.

| | |
|---|---|
| **Beats** | Google Snappy (C++), called through its C API (snappy_compress, snappy_uncompress, snappy_validate_compressed_buffer) from a prebuilt libsnappy.dll loaded by the nimsnappy wrapper (version and build flags unknown; the wrapper says it tracks 1.1.3). Also Andi Kleen's snappy-c (C), compiled from source into the benchmark through the nimsnappyc wrapper's {.compile.} pragma. The pure-Nim status-im/nim-snappy is the fourth column. |
| **Claimed result** | README: 'performs significantly better in all cases than alternatives'. Table, avg ms per compress-plus-uncompress round trip (derived ratios from page data). Against Google Snappy via nimsnappy: alice29.txt 0.513 vs 0.599 (1.17x), asyoulik.txt 0.451 vs 0.529 (1.17x), html_x_4 0.534 vs 0.559 (1.05x), kppkn.gtb 0.435 vs 0.523 (1.20x), lcet10.txt 1.380 vs 1.599 (1.16x), plrabn12.txt 1.898 vs 2.237 (1.18x), urls.10K 1.574 vs 1.842 (1.17x); slower on fireworks.jpg 0.015 vs 0.011, geo.protodata 0.106 vs 0.101 and paper-100k.pdf 0.041 vs 0.017, html 0.128 vs 0.127 (tie). Against snappy-c via nimsnappyc, faster on all 11 files by 1.10x (plrabn12.txt 1.898 vs 2.092) to 1.42x (geo.protodata 0.106 vs 0.150). Against status-im/nim-snappy it is slower on fireworks.jpg (0.015 vs 0.011) and paper-100k.pdf (0.041 vs 0.020). So 'all cases' holds only against snappy-c. |
| **Workload** | Snappy benchmark corpus (alice29.txt, asyoulik.txt, fireworks.jpg, geo.protodata, html, html_x_4, kppkn.gtb, lcet10.txt, paper-100k.pdf, plrabn12.txt, urls.10K). tests/bench.nim times one compress plus one uncompress of the whole file per benchy timeIt sample, with 1000 samples (x1000). The README header's '100 compress-uncompress cycles' does not match the current code. |
| **Metric** | throughput (100 compress-uncompress cycles) |
| **Hardware** | Not stated (a Windows machine, judging by the .\tests path and libsnappy.dll) |
| **Compiler and flags** | nim c --gc:arc -d:release -r tests/bench.nim (README still says tests/benchmark.nim, which is now 404). Nim's release config compiles both its generated C and the {.compile.}'d snappy-c with the same backend C compiler (gcc/clang -O3, vcc /O2 per Nim's config/nim.cfg), and supersnappy turns checks off in release builds. The backend compiler and version are not stated, and the build of the libsnappy.dll used for Google Snappy is unknown. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | not stated |
| **Adoption** | 94 stars |
| **Last commit** | 2025-12-15 |
| **Links** | [repository](https://github.com/guzba/supersnappy) · [benchmark](https://github.com/guzba/supersnappy/blob/master/tests/bench.nim) |

## Verdict

First-party README table: nim c --gc:arc -d:release on an unstated Windows machine and C compiler, last updated in June 2022, mean compress-plus-uncompress round trip per file of the 11-file Snappy corpus over 1,000 benchy samples. Supersnappy beat snappy-c (built by the same backend compiler through nimsnappyc) on all 11 files by 1.10-1.42x. Against Google Snappy, called through nimsnappy and a prebuilt libsnappy.dll of unknown version, it won by 1.05-1.20x on 7 files, tied on html and lost on fireworks.jpg, geo.protodata and paper-100k.pdf (2.4x slower), so the README's 'better in all cases' does not hold (ratios derived from page data).

## Use it when

- Nim programs that need raw Snappy without a C library or DLL: one MIT-licensed nimble package with no dependencies beyond std/bitops.
- Baking compressed assets into a Nim executable at compile time (const x = compress(readFile(...))), which C/C++ Snappy bindings cannot do.
- Text-like payloads such as the corpus's alice29, lcet10, plrabn12 and urls.10K, where the 2022 table showed round trips 1.16-1.18x shorter than the nimsnappy/libsnappy path and 1.10-1.21x shorter than snappy-c.
- Hot loops that can reuse output buffers through compress(dst, src) and uncompress(dst, src); the benchmark did not use this path, so its benefit is unmeasured.

## Skip it when

- Untrusted compressed input without your own checks: open issue #7 (2026-03-10) reports out-of-bounds reads on truncated tag trailers, and issue #8 (an attacker-chosen size prefix forces up to a 4 GiB allocation before validation) was closed by the maintainer with 'Not concerned about this.'
- Incompressible or binary-heavy data: in its own table it is slower than the libsnappy path on fireworks.jpg (0.015 vs 0.011 ms), geo.protodata (0.106 vs 0.101) and paper-100k.pdf (0.041 vs 0.017, 2.4x slower), and slower than status-im/nim-snappy on fireworks.jpg and paper-100k.pdf.
- If you need the Snappy framing format, streaming or CRC32C: only the raw block API exists; status-im/nim-snappy has framed and faststreams APIs, and C/C++ code should call google/snappy directly.
- If you expect to beat current Google Snappy: never measured. The baseline was a prebuilt libsnappy.dll of unknown version (the nimsnappy wrapper tracks 1.1.3), and status-im/nim-snappy's README, on the same corpus, shows current C++ Snappy decompressing 1.4-2.0x faster than nim-snappy, which supersnappy beat by only 1.15-1.27x on compressible files in 2022.

## How it is fast

It is a port of Andi Kleen's snappy-c: a multiplicative hash (0x1e35a7bd) of 4-byte windows into a uint16 table sized to the fragment (256 to 16,384 entries over 64 KiB fragments), Snappy's skip heuristic that hashes less often in incompressible runs, match extension with 64-bit XOR plus count-trailing-zeros, and literals and copies of up to 16 bytes done as two unaligned 8-byte moves. The decoder uses a 256-entry uint16 tag lookup table and an incremental 8-byte pattern copy for overlapping matches. Release builds turn off Nim's bounds and overflow checks for the whole module. Nim compiles to C, so any margin over snappy-c comes from code and wrapper differences, not the language; the README does not explain the margin.

## Compared with alternatives

No Snappy codec is among the catalogued siblings (zipir is a Zig DEFLATE codec for a different format). Pick supersnappy only inside Nim code that wants dependency-free raw Snappy, possibly at compile time. snap (BurntSushi/rust-snappy, filed in this category in the same wave) is the Rust counterpart and adds the frame format, and C/C++ code should call google/snappy (wave 9) directly.

## Integration

| | |
|---|---|
| **Form** | module (nimble package supersnappy, source only) |
| **Dependencies** | none (Nim standard library bitops) |
| **Minimum toolchain** | Nim 1.0.0 per supersnappy.nimble; README lists --gc:arc, --gc:orc and the default GC; an 'update for 2.0' commit (Aug 2023) covers Nim 2.0 |
| **Platforms** | any Nim backend target (C, C++, VCC; 32-bit fixed in issue #1; emscripten in 2.1.4), but the run-time path assumes little-endian byte order (not documented) |
| **Thread safety** | not documented; compress and uncompress are funcs with no global mutable state and compress allocates its own hash table, so concurrent calls on separate buffers should be safe |
| **Drop-in for the baseline** | partial: it writes and reads the standard raw Snappy format (tests/validate.nim round-trips against snappy-c and nim-snappy; the Google C++ check is commented out because it needs libsnappy.dll), but it is a Nim API, not a C/C++ library |

## Gotchas

- Benchmark harness: tests/bench.nim times compress plus uncompress through each wrapper's allocating string API and never checks the output (round trips are checked only in tests/test.nim). The Google Snappy path (nimsnappy) runs snappy_validate_compressed_buffer and snappy_uncompressed_length before every uncompress, an extra pass the others skip. The snappy-c path (nimsnappyc) calls snappy_init_env/snappy_free_env on every compress, but supersnappy also allocates and zero-fills a 16,384-entry uint16 table (32 KiB) on every compress, so that cost is on both sides. One unstated machine and C compiler; the last 'update benchmarks' commit is 2022-06-12; the README still cites tests/benchmark.nim and '100 compress-uncompress cycles', while the file is tests/bench.nim and the table shows x1000 samples.
- Out-of-bounds read on truncated input (issue #7, open since 2026-03-10, confirmed in src/supersnappy.nim): for long literals (len &gt;= 61) and for COPY tags, uncompress calls read32 before checking that the 1-4 trailer bytes exist (the copy path checks only ip + 1 &lt; srcLen), and release builds run with checks off. A truncated stream therefore reads up to 4 bytes past the input, and the reporter's truncated 5-byte input decoded to 'AA' instead of failing. tests/fuzz.nim flips one byte per run, 10,000 times, never truncates and runs without a sanitizer, so it cannot catch this.
- Unbounded allocation (issue #8, closed as 'Not concerned about this.'): uncompress does dst.setLen(uncompressedLen) from the varint header (up to 4 GiB - 1) before validating the body. Check the declared length against your own limit before calling it on untrusted data.
- Endianness: outside the compile-time (nimvm) branch, read32/read64 and the 2-byte copy offset use copyMem in native byte order, and trailers are masked as little-endian values, so on a big-endian host the output would not be standard Snappy. The README does not mention byte order.

## Known shortcomings

- Nim compiles to C, so there is no language effect; beats snappy-c on all 11 files (1.10-1.42x) but against Google Snappy wins only 16-20% on text and is slower on 3 files; the nimsnappy wrapper adds a validate pass, the libsnappy.dll build is unknown, no hardware; the README "all cases" is contradicted by its own table.
- Correctness bug: uncompress calls read32 before checking the trailer bytes, with checks off in release, so truncated input reads up to 4 bytes out of bounds and can decode instead of failing (issue #7, open); an untrusted varint prefix allocates up to 4 GiB first (issue #8, maintainer: not concerned). The fuzzer flips single bytes only with no sanitiser; the runtime path is little-endian only and undocumented; the bench never checks output; the Google path pays an extra validate pass, and Supersnappy itself allocates a 32 KiB table per compress, so the snappy-c init_env caveat cuts both ways. Table dates from 2022-06-12.

## Caveats and trade-offs

Weak entry. Nim compiles to C, so this is a C-versus-C comparison and no language effect. The cleanest comparison is against snappy-c, built by the same C compiler at the same flags, which supersnappy beats on all 11 files by 1.10-1.42x; but the nimsnappyc wrapper calls snappy_init_env/snappy_free_env (allocating the hash table) on every compress, which inflates small-file times. Against Google Snappy the nimsnappy wrapper runs a full snappy_validate_compressed_buffer pass before every uncompress, and newString zero-fills both output buffers, so the C++ baseline does extra work; even so supersnappy wins only 16-20 percent on text, ties html and loses on fireworks.jpg, geo.protodata and paper-100k.pdf (2.4x slower on paper-100k.pdf). The libsnappy.dll version and flags are unknown (the wrapper says it tracks snappy 1.1.3, a 2015 release), no hardware is stated, and the README's 'all cases' claim is contradicted by its own table. The code credits snappy-c as its main influence. [retier] uncompress calls read32 before checking the trailer bytes (checks off in release), so truncated input reads up to 4 bytes out of bounds and can decode instead of failing (issue #7, open); an untrusted varint prefix allocates up to 4 GiB first (issue #8). The fuzzer flips single bytes only; the runtime path is little-endian only; the bench never checks output; the Google path pays an extra validate pass, and Supersnappy allocates a 32 KiB table per compress, so the snappy-c init_env caveat cuts both ways. Table dates from 2022-06-12.

Pure Nim, dependency free, usable at compile time; outputs checked for compatibility with other Snappy implementations.

## Maintenance

Low-activity single-maintainer project (version 2.1.4 and the last commit on 2025-12-15, earlier commits in 2023, 94 stars, MIT) that is small enough to vendor. The open truncated-input out-of-bounds read (#7) and the size-prefix allocation the maintainer declined to fix (#8) make it unsafe for untrusted input without a wrapper, and its speed claim rests on a 2022 first-party table against an unknown libsnappy build.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README table produced by public code (tests/bench.nim, with benchy) and a stated Nim command line, but no CPU model, no C compiler or version, and an unknown build of the libsnappy.dll that serves as the Google Snappy baseline, so not A.
- **Verifier notes:** Confirmed at C with corrections. Google Snappy (wave 9 list) is the baseline, so baseline_in_list is now true. nimsnappy is confirmed to wrap Google's C++ snappy through its C API (snappy_validate_compressed_buffer, no env argument), not the C port. Shortcomings: wins only on text-like files against an extra-pass FFI wrapper of an old, unknown libsnappy.dll build; slower on 3 files; no hardware; Nim compiles to C, so no language effect; README's 'all cases' claim contradicted; benchmark path in README stale.
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `baseline_in_list`, `claimed_speedup`, `workload`, `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** verifier batch-15 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/guzba/supersnappy>
  - <https://raw.githubusercontent.com/guzba/supersnappy/HEAD/README.md>
  - <https://github.com/guzba/supersnappy/tree/master/tests>
  - <https://github.com/guzba/supersnappy/blob/master/tests/bench.nim>
  - <https://raw.githubusercontent.com/guzba/supersnappy/HEAD/tests/bench.nim>
  - <https://raw.githubusercontent.com/guzba/supersnappy/HEAD/tests/validate.nim>
  - <https://raw.githubusercontent.com/guzba/supersnappy/HEAD/src/supersnappy.nim>
  - <https://raw.githubusercontent.com/guzba/supersnappy/HEAD/supersnappy.nimble>
  - <https://raw.githubusercontent.com/guzba/supersnappy/HEAD/LICENSE>
  - <https://github.com/guzba/supersnappy/commits/master>
  - <https://github.com/dfdeshom/nimsnappy>
  - <https://raw.githubusercontent.com/dfdeshom/nimsnappy/HEAD/README.md>
  - <https://raw.githubusercontent.com/dfdeshom/nimsnappy/HEAD/snappy.nim>
  - <https://github.com/NimCompression/nimsnappyc>
  - <https://raw.githubusercontent.com/NimCompression/nimsnappyc/HEAD/README.md>
  - <https://raw.githubusercontent.com/NimCompression/nimsnappyc/HEAD/nimsnappyc.nim>
  - <https://raw.githubusercontent.com/NimCompression/nimsnappyc/HEAD/nimsnappyc/snappyc.nim>
  - <https://raw.githubusercontent.com/nim-lang/Nim/devel/config/nim.cfg>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/guzba/supersnappy/HEAD/README.md>
  - <https://raw.githubusercontent.com/guzba/supersnappy/HEAD/src/supersnappy.nim>
  - <https://raw.githubusercontent.com/guzba/supersnappy/HEAD/src/supersnappy/internal.nim>
  - <https://raw.githubusercontent.com/guzba/supersnappy/HEAD/tests/bench.nim>
  - <https://raw.githubusercontent.com/guzba/supersnappy/HEAD/tests/validate.nim>
  - <https://raw.githubusercontent.com/guzba/supersnappy/HEAD/tests/test.nim>
  - <https://raw.githubusercontent.com/guzba/supersnappy/HEAD/tests/fuzz.nim>
  - <https://raw.githubusercontent.com/guzba/supersnappy/HEAD/examples/compiletime.nim>
  - <https://raw.githubusercontent.com/guzba/supersnappy/HEAD/supersnappy.nimble>
  - <https://raw.githubusercontent.com/guzba/supersnappy/HEAD/LICENSE>
  - <https://github.com/guzba/supersnappy/commits/master>
  - <https://github.com/guzba/supersnappy/issues?q=is%3Aissue>
  - <https://github.com/guzba/supersnappy/issues/7>
  - <https://github.com/guzba/supersnappy/issues/8>
  - <https://raw.githubusercontent.com/dfdeshom/nimsnappy/HEAD/snappy.nim>
  - <https://raw.githubusercontent.com/NimCompression/nimsnappyc/HEAD/nimsnappyc.nim>
  - <https://raw.githubusercontent.com/NimCompression/nimsnappyc/HEAD/nimsnappyc/snappyc.nim>
  - <https://raw.githubusercontent.com/status-im/nim-snappy/HEAD/README.md>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/guzba/supersnappy`) · [data/wave14/enrich/raw/github_com_guzba_supersnappy.json](../../../data/wave14/enrich/raw/github_com_guzba_supersnappy.json) (enrichment confidence 0.75)

</details>
