# ledbit/varint (PrefixVarint, leSQLite, leSQLite2 vs LEB128)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Integer compression and bit-packing](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🔴 abandoned

> Benchmark study of three byte-oriented varint formats (PrefixVarint, leSQLite, leSQLite2) that decode 2-2.9x faster than a naive LEB128 loop.

| | |
|---|---|
| **Beats** | LEB128 varint (as in protobuf and DWARF), implemented in the same repo (leb128.cpp) |
| **Claimed result** | Sample run in README: LEB128 1.165e-03 secs, PrefixVarint 5.693e-04 secs, leSQLite 4.043e-04 secs, leSQLite2 4.815e-04 secs; T(LEB128)/T(PrefixVarint) = 2.047, T(LEB128)/T(leSQLite) = 2.882, T(LEB128)/T(leSQLite2) = 2.420. Size: LEB128 5.076, PrefixVarint 5.060, leSQLite 5.285, leSQLite2 5.239 bytes per integer. |
| **Workload** | Decode time of 100000 log-uniform random integers encoded with each scheme; the repo is a WebAssembly design study (WebAssembly/design issue 601) to pick a faster varint than LEB128. |
| **Metric** | throughput |
| **Compiler and flags** | Makefile: CXXFLAGS -std=c++14 -O3; compiler not stated |
| **Adoption** | 8 stars |
| **Last commit** | 2018-01-22 |
| **Links** | [repository](https://github.com/ledbit/varint) · [benchmark](https://github.com/ledbit/varint) |

## Verdict

One README sample run (compiler and CPU not stated, -O3, decode only) on 100,000 log-uniform 64-bit integers timed LEB128 at 1.165 ms per pass, PrefixVarint 0.569 ms (2.05x), leSQLite 0.404 ms (2.88x) and leSQLite2 0.482 ms (2.42x), with sizes of 5.076, 5.060, 5.285 and 5.239 bytes per integer; the harness repeats each decode for about one second and checks the round trip with assert.

## Use it when

- Designing a new binary format (bytecode, RPC, log records) where you control both sides and want a varint with first-byte length and cheaper multi-byte decode than LEB128.
- Workloads with many multi-byte 64-bit integers, where LEB128's per-byte branch dominates; the measured data was log-uniform over 64 bits (about 5 bytes per integer).
- Pick leSQLite when decode speed matters most (2.88x LEB128 in the sample, 4% larger output); PrefixVarint when you must keep LEB128's size (5.060 vs 5.076 bytes per integer).
- As a reference to copy: each codec is 50-100 lines of Apache-2.0 C++.

## Skip it when

- Existing formats that mandate LEB128 (protobuf, DWARF, WebAssembly binaries); none of these encodings is wire-compatible.
- Untrusted input: the README says the code is not production quality and malformed input causes undefined behavior; there are no input or output bounds checks.
- Mostly small values: with integers under 128 every scheme takes a one-byte LIKELY fast path, and the 2x figures come from a log-uniform 64-bit distribution where most values need 4-9 bytes.
- When you need encode speed numbers, SIMD bulk decode, or a maintained library; encoding is not measured and the code has had no changes since January 2018.
- Big-endian hosts or non-GCC/Clang compilers: decoding relies on host little-endian memcpy loads and __builtin_clzll/__builtin_ctz.

## How it is fast

All three alternatives make the total length known from the first byte, so a multi-byte value is decoded with one unaligned 8-byte load plus a shift or mask instead of LEB128's byte-at-a-time loop with a continuation-bit test per byte. PrefixVarint moves all tag bits to the low bits of byte 0 (UTF-8-like) and finds the length with count-trailing-zeros; leSQLite and leSQLite2 are little-endian variants of the SQLite4 varint where byte 0 ranges select 1-, 2-, 3- or N-byte forms, so the 3-9 byte forms are a raw little-endian integer masked to length.

## Compared with alternatives

varint-simd, MaskedVByte and Stream VByte make LEB128-style or byte-oriented decoding fast with SIMD (Stream VByte with a separate control stream); pick these formats when you can change the wire format and want a simple scalar codec with first-byte length and 64-bit range. For bulk 32-bit integer arrays, Stream VByte or simdcomp will be much faster.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none |
| **Minimum toolchain** | Makefile uses -std=c++14 -O3; codec_descriptor uses C++20-style designated initializers, accepted as a GCC/Clang extension in C++14 but not by MSVC before C++20 |
| **Platforms** | little-endian targets with GCC or Clang builtins (x86-64 assumed for unaligned loads); not documented beyond that |
| **Thread safety** | Encoders and decoders are stateless free functions; thread safety not otherwise documented |
| **Drop-in for the baseline** | no |

## Gotchas

- The fast multi-byte decoders over-read: prefix_get and the leSQLite 3-9 byte path always load 8 bytes from the value start, and the leSQLite2 4-9 byte path does the same, so the final value can read up to 6 bytes past the end of the encoded buffer; the benchmark does not pad the std::vector. Pad any input buffer by at least 8 bytes.
- ledbit's 2018 commit 'fix crash due to stack smashing - read just 2 bytes instead of 8' changed one leSQLite2 path to a 2-byte load; the other 8-byte loads were left as they were.
- leb128_decode keeps shifting past 63 bits on over-long input (undefined behavior, acknowledged in a code comment), so the baseline is also unsafe on hostile data.
- The LEB128 baseline is a plain byte loop with a one-byte fast path, not an optimized decoder such as protobuf's or a SIMD one, so the 2-2.9x ratios overstate the gap to the best LEB128 decoders.

## Known shortcomings

- Compiler and CPU not stated (Makefile -std=c++14 -O3 only). 8 stars, last commit 2018-01-22, abandoned.
- The prefix and both leSQLite decoders do 8-byte unaligned loads and read up to 6 bytes past the end of an unpadded buffer (the benchmark does not pad); the 2018 commit fixed only one 2-byte path. Little-endian hosts only; designated initialisers are not valid C++14. The LEB128 baseline is a naive byte loop with shift UB. Log-uniform 64-bit data (about 5 bytes per int) favours the new formats. Code is by Jakob Stoklund Olesen (2016); the original stoklund/varint returns 404.

## Caveats and trade-offs

README says the C++ code is not production quality and can be driven into undefined behavior by maliciously formed input. Single 100000-integer run, compiler, flags and CPU not stated, so no repeat-run variance and not reproducible as stated. Decode only; encode speed not measured. Not a SIMD or bitpacking library; it is a scalar varint comparison. Found through the HN thread 'Another variable-length integer encoding (2021)' search and a follow-up WebSearch on prefix varint; the HN thread itself was not opened (news.ycombinator.com blocked).

PrefixVarint keeps the LEB128 size (5.060 vs 5.076 bytes per integer in the sample) but needs unaligned loads and count-trailing-zeros; leSQLite and leSQLite2 are larger (5.285 and 5.239 bytes per integer) and decode faster. Length of an encoded value is known from the first byte.

## Maintenance

Abandoned since January 2018 (15 commits, mostly 2016 by Jakob Stoklund Olesen; the original stoklund/varint URL now returns 404) but Apache-2.0 and tiny enough to copy once the over-reads and missing bounds checks are fixed.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** README 'Sample output' gives first-party decode times for LEB128 vs PrefixVarint/leSQLite/leSQLite2 from the repo's own benchmark code; Makefile shows -std=c++14 -O3 but compiler and CPU are not stated, so C.
- **Verifier notes:** Numbers match the README sample output exactly (LEB128 1.165e-03 s, PrefixVarint 5.693e-04, leSQLite 4.043e-04, leSQLite2 4.815e-04; ratios 2.047/2.882/2.420 printed by the program). README confirms 'not production quality' and UB on malicious input, and that encoding speed is not measured. 8 stars, Apache-2.0, not a fork, last commit 2018-01-22.
- **Fields the verifier corrected:** `compiler_and_flags`
- **Shortcomings recorded by:** first-party README sample output; first-party benchmark
- **Pages the verifier opened:**
  - <https://github.com/ledbit/varint>
  - <https://github.com/ledbit/varint/commits>
  - <https://raw.githubusercontent.com/ledbit/varint/HEAD/README.md>
  - <https://raw.githubusercontent.com/ledbit/varint/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/ledbit/varint/HEAD/Makefile>
- **Sources the enricher read:**
  - <https://github.com/ledbit/varint>
  - <https://github.com/ledbit/varint/commits>
  - <https://raw.githubusercontent.com/ledbit/varint/HEAD/README.md>
  - <https://raw.githubusercontent.com/ledbit/varint/HEAD/Makefile>
  - <https://raw.githubusercontent.com/ledbit/varint/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/ledbit/varint/HEAD/compiler.h>
  - <https://raw.githubusercontent.com/ledbit/varint/HEAD/varint.h>
  - <https://raw.githubusercontent.com/ledbit/varint/HEAD/varint.cpp>
  - <https://raw.githubusercontent.com/ledbit/varint/HEAD/leb128.cpp>
  - <https://raw.githubusercontent.com/ledbit/varint/HEAD/prefix_varint.cpp>
  - <https://raw.githubusercontent.com/ledbit/varint/HEAD/lesqlite.cpp>
  - <https://raw.githubusercontent.com/ledbit/varint/HEAD/lesqlite2.cpp>
  - <https://github.com/WebAssembly/design/issues/601>
  - <https://github.com/stoklund/varint>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/ledbit/varint`) · [data/wave9/enrich/raw/github_com_ledbit_varint.json](../../../data/wave9/enrich/raw/github_com_ledbit_varint.json) (enrichment confidence 0.8)

</details>
