# Zig (kostya/benchmarks base64)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Systems and safety](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Zig` · `MIT` · 🟢 active

> Zig std.base64 in kostya/benchmarks: 8192 rounds of 128 KiB encode plus decode 1.31x faster than a hand-written scalar C codec (clang), 1.59x (gcc).

| | |
|---|---|
| **Beats** | Hand-written scalar C base64 (no library), gcc and clang, -O3 -march=native -flto |
| **Claimed result** | kostya/benchmarks base64 table (median, Xeon E-2324G, README updated 2026-07-19): Zig 0.703 s vs C/clang 0.918 s and C/gcc 1.117 s, about 1.31x and 1.59x faster (derived from page data); Rust 0.842 s also beats both. The same table has C/clang (aklomp) 0.095 s and C/gcc (aklomp) 0.097 s, about 7.4x faster than Zig, and PHP 0.065 s (its C base64) fastest overall; C++ with libcrypto takes 3.664 s. |
| **Workload** | Base64 encode and decode of a 131072-byte string, 8192 tries, into newly allocated buffers; seconds. |
| **Metric** | latency |
| **Hardware** | Intel Xeon E-2324G, Debian forky/sid Docker image |
| **Compiler and flags** | Zig 0.16.0: zig build-exe -O ReleaseFast -lc (std.base64); C and C++: gcc/g++ 16.1.0 or clang/clang++ 22.1.8 with -O3 -march=native -flto=auto -std=c23 / c++23 -Wa,-mbranches-within-32B-boundaries (common/commands.mk) |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | not stated |
| **Same optimization level** | yes |
| **Adoption** | 2.9k stars, 262 forks (suite repo) |
| **Last commit** | 2026-07-19 |
| **Links** | [repository](https://github.com/kostya/benchmarks) · [benchmark](https://raw.githubusercontent.com/kostya/benchmarks/master/README.md) |

## Verdict

The kostya/benchmarks README (update 2026-07-19, Intel Xeon E-2324G, Debian forky/sid Docker image, medians with median absolute deviation) lists Base64 at 0.703 s for Zig 0.16.0 (-O ReleaseFast, std.base64) against 0.918 s for C/clang 22.1.8 and 1.117 s for C/gcc 16.1.0 (-O3 -march=native -flto=auto, hand-written scalar codec), about 1.31x and 1.59x (derived from page data), for 8192 encodes plus 8192 decodes of a 128 KiB buffer. Energy follows the same order (26.42 J vs 34.47 J and 41.76 J), and the SIMD aklomp builds (0.095 and 0.097 s) beat Zig by about 7x.

## Use it when

- You write Zig and need RFC 4648 base64 on in-memory buffers: std.base64 is built in, has no dependencies and beat both hand-written C builds and the Rust base64 0.22.1 crate (0.842 s) in this test.
- As a portable scalar reference to port to C or C++ when SIMD is not available (no AVX2, SSSE3 or NEON, or a small embedded target): the four pre-shifted decode tables cost 4 KiB and remove the per-character branch.
- Bulk strict decoding of clean, padded input such as API payloads or data URLs where line breaks never occur.

## Skip it when

- When throughput matters most: SIMD C libraries are about 7x faster in the same table (C/clang aklomp 0.095 s, C/gcc aklomp 0.097 s), and PHP's built-in C base64 (0.065 s) is faster still.
- MIME or PEM text with line breaks: the standard decoder returns error.InvalidCharacter on '\n' or '\r'; the slower Base64DecoderWithIgnore path is needed, while the C program skips them inline.
- Mixed-alphabet input: the C decoder accepts both '+'/'-' and '/'/'_', while std.base64.standard accepts only '+' and '/' and enforces padding strictly (error.InvalidPadding).
- As evidence that Zig beats C as a language: the two sides run different algorithms, and the fair C comparison (aklomp) is far ahead.

## How it is fast

The win comes from a better scalar algorithm in Zig's standard library, not from the language. The decoder uses four 256-entry u32 tables, one per position in a 4-character quantum, pre-shifted so that four lookups ORed together give the 3 output bytes in place, checks validity once per quantum with a single mask test (invalid characters map to 0xff000000), and in its fast loop handles 16 characters per step with one 16-byte u128 store. The encoder reads 16 input bytes as one big-endian u128 and emits 16 characters per 12 bytes. The C program decodes through one table with a sign test and branch on every character, scans for '\n' and '\r' before each quantum and stores byte by byte. SIMD codecs are far faster still: aklomp/base64 in the same table takes 0.095 s.

## Compared with alternatives

Among catalogued siblings, tachyon-rs is the entry to read for SIMD base64 and crypto in Rust, and the kostya/benchmarks Rust and V brainfuck rows are same-harness language rows of similar strength; pick this entry only as evidence that Zig's scalar standard-library codec beats a naive C loop, and use aklomp/base64 or another SIMD codec when you need speed in C or C++.

## Integration

| | |
|---|---|
| **Form** | module (std.base64 in the Zig standard library; the benchmark itself is one source file) |
| **Dependencies** | none beyond the Zig standard library; the test links libc (-lc) for std.heap.c_allocator and talks to the suite's runner on localhost:9001 when it is present |
| **Minimum toolchain** | Zig 0.16.0 as measured (test.zig uses the 0.16 std.Io, std.Io.Threaded and std.Io.net APIs); std.base64's encode and decode API is older |
| **Platforms** | Portable scalar code (any Zig target); measured on an Intel Xeon E-2324G in a Debian forky/sid Docker image |
| **Thread safety** | Not documented; the encoder and decoder are immutable structs with constant tables and encode and decode only write the caller's buffers, so concurrent use looks safe (inference from the source) |
| **Drop-in for the baseline** | partial: same RFC 4648 output for the standard alphabet, but a different API (caller-sized buffers via calcSize and calcSizeForSlice), stricter padding, and no inline skipping of line breaks or URL-safe characters |

## Gotchas

- Possible harness asymmetry (not verified, no disassembly): the timed Zig loop calls decode with `catch unreachable`, and in ReleaseFast the Zig language reference says the optimizer assumes unreachable code is never hit. If LLVM inlines decode into main, every `return error.InvalidCharacter` check in the decode loop can be deleted, so the Zig side may run without input validation, while the C side keeps a sign test and branch on every character because its failure path calls exit().
- Feature asymmetry on the C side: test-nolib.c scans for '\n' and '\r' before every 4-character quantum and accepts URL-safe '-' and '_' alongside '+' and '/', work std.base64.standard does not do; part of the gap is the cost of that leniency.
- Neither side really allocates in the timed loops: Zig takes the buffer from a FixedBufferAllocator that is reset every iteration and C uses stack VLAs, whatever the README's 'newly allocated buffers' says; the Rust row (base64 0.22.1) does allocate a fresh String and Vec per iteration and still takes only 0.842 s.
- Build-flag asymmetry: the C, C++, Nim and Rust builds add branch padding (-Wa,-mbranches-within-32B-boundaries or the LLVM equivalent) while Zig is built with plain -O ReleaseFast -lc; the effect on this test is not measured.

## Known shortcomings

- Zig std.base64 uses a four-table decode with u128 blocks while the C side is a naive per-character loop (0.703 s vs clang 0.918 s, gcc 1.117 s), so not the same algorithm; the aklomp C decoder is about 7x faster than Zig.
- The JSON3.jl enricher found that kostya/benchmarks' 2026-07-19 update re-measured only the Primes table and the environment table: the Json table rows kept their 2025-08-17 values (gcc 14.2.0, clang 19.1.7), so the compiler versions recorded here (gcc 16.1.0, clang 22.1.8) describe the current environment table and may not be the toolchain behind this table's rows; whether this table was re-run on 2026-07-19 was not checked.
- Possible harness asymmetry, not verified (no disassembly): the timed loop uses `decode(...) catch unreachable`, and in ReleaseFast the optimiser assumes unreachable is never hit, so if decode is inlined the Zig validity checks can be deleted while C keeps a branch on every character (its failure path calls exit). The C side also does extra work (skips '\n' and '\r' each quantum, accepts '-' and '_'), and the branch-padding flag is on the C, C++, Nim and Rust builds but not on Zig. aklomp's SIMD base64 is 7x faster than Zig.

## Caveats and trade-offs

Not the same algorithm: Zig uses std.base64 (checked in lib/std/base64.zig at the 0.15.2 tag and master on the GitHub mirror; the 0.16.0 tag is not on GitHub), whose decoder ORs four 256-entry u32 tables pre-shifted per character position, checks validity once per 4 characters and writes 16 bytes per u128 store, and whose encoder reads 16 bytes as a u128 and emits 16 characters per 12 input bytes; base64/test-nolib.c uses one decode table, branches on every character, scans for \n and \r before each quantum (MIME tolerance Zig's standard decoder does not provide) and stores byte by byte. So the win is a library implementation difference; the SIMD C library (aklomp) is about 7x faster than Zig, and the same four-table technique is available in C (e.g. Chromium modp_b64). Buffers: Zig uses a FixedBufferAllocator and C uses stack VLAs, so 'newly allocated buffers' cost nothing on either side; the Zig input is a comptime constant ("a" \*\* 131072) and the C input a memset stack array. Zig is built with zig build-exe -O ReleaseFast -lc (native CPU by default), C with -O3 -march=native -flto=auto. Medians with MAD from one machine; the README states no flags in prose (they are in common/commands.mk). [retier] Enricher: possible asymmetry, not verified (no disassembly); the timed loop uses `decode(...) catch unreachable`, and in ReleaseFast the optimiser assumes unreachable is never hit, so if decode is inlined the Zig validity checks can be deleted while C keeps a branch on every character. The C side also skips '\n' and '\r' each quantum and accepts '-' and '_', and the branch-padding flag is on the C, C++, Nim and Rust builds but not on Zig; aklomp's SIMD base64 is 7x faster than Zig.

Single task microbenchmark; Zig std.base64 is scalar.

## Maintenance

The suite is active and MIT-licensed (2.9k stars, 262 forks, 892 commits, results refreshed 2026-07-19; the Zig test was added in 2021 and updated in the July 2026 maintenance commit), and std.base64 ships with every Zig release, so the codec is usable now in Zig and easy to port; the benchmark row itself measures an algorithm gap, not a language gap.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The kostya/benchmarks README (UPDATE 2026-07-19, Intel Xeon E-2324G, Zig 0.16.0, gcc 16.1.0, clang 22.1.8) shows Zig 0.703 s vs C/clang 0.918 s and C/gcc 1.117 s, with code (base64/test.zig, base64/test-nolib.c) and flags (common/commands.mk, base64/Makefile) public, so the harness is A-grade; capped at C because it is not like for like: Zig calls std.base64, which decodes 16 characters per step through four pre-shifted lookup tables with one validity check and a 16-byte store and encodes 12 bytes per u128 load, while the C program is a hand-written per-character decoder with a branch per character and newline skipping (same asymmetric-kernel cap as the kostya matmul D entry in batch-02).
- **Verifier notes:** Numbers verified on the README; harness is reproducible (code, flags, CPU, versions) but the win comes from Zig's std.base64 algorithm against a naive hand-written C loop, so it stays C with same_algorithm false; the best C (aklomp/base64, SIMD) is about 7x faster than Zig. Record shortcoming: different algorithm on each side, not a language effect.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`, `stars_or_usage`
- **Shortcomings recorded by:** verifier batch-30 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/README.md>
  - <https://github.com/kostya/benchmarks/tree/master/base64>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/base64/Makefile>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/base64/test-nolib.c>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/base64/test.zig>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/common/commands.mk>
  - <https://raw.githubusercontent.com/ziglang/zig/0.15.2/lib/std/base64.zig>
  - <https://raw.githubusercontent.com/ziglang/zig/master/lib/std/base64.zig>
  - <https://github.com/kostya/benchmarks>
  - <https://github.com/kostya/benchmarks/commits/master>
- **Sources the enricher read:**
  - <https://github.com/kostya/benchmarks>
  - <https://github.com/kostya/benchmarks/commits/master/base64/test.zig>
  - <https://github.com/kostya/benchmarks/issues?q=is%3Aissue+base64>
  - <https://github.com/kostya/benchmarks/tree/master/base64/base64.rs>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/README.md>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/base64/Makefile>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/base64/test.zig>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/base64/test-nolib.c>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/base64/base64.rs/Cargo.toml>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/base64/base64.rs/src/bin/base64.rs>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/common/commands.mk>
  - <https://raw.githubusercontent.com/ziglang/zig/master/lib/std/base64.zig>
  - <https://raw.githubusercontent.com/ziglang/zig/master/doc/langref.html.in>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:zig/kostya/benchmarks#base64`) · [data/wave14/enrich/raw/lang_zig_kostya_benchmarks_base64.json](../../../data/wave14/enrich/raw/lang_zig_kostya_benchmarks_base64.json) (enrichment confidence 0.75)

</details>
