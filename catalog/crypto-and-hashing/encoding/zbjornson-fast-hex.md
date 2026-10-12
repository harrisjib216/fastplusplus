# fast-hex (zbjornson)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Encoding (base64, hex, CRC)](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> AVX2 hex encoder/decoder for C++ and Node.js, self-reported \~11-12x faster than its own scalar lookup-table codec.

| | |
|---|---|
| **Beats** | hex (scalar hex string encode/decode) |
| **Claimed result** | C++: decoding about 12.5x and encoding about 11.5x over scalar. Node.js module: about 2.12x faster decoding for short string inputs (&lt; 1,031,913 chars), about 12x faster decoding for some long strings, Buffers and TypedArrays, and about 5.5x faster encoding. The README does not name the Node.js baseline. |
| **Workload** | AVX2 hex decode/encode of byte buffers. The C++ ratios are against the library's own scalar look-up-table codec (decodeHexLUT/encodeHex in src/hex.cc). The Node.js ratios come from benchmark/hex-\*.js. There, the encode baseline is Node's built-in Buffer#toString('hex'), but the decode baseline labelled 'node' is the addon's own scalar decodeHexLUT, not Buffer.from(str, 'hex'). |
| **Metric** | throughput |
| **Compiler and flags** | Requires AVX2 (-march=haswell on GCC/Clang/ICC, /arch:AVX2 or EnableAdvancedInstructionSet on MSVC); exact compiler version not stated |
| **Adoption** | 63 stars |
| **Last commit** | 2026-04-10 |
| **Links** | [repository](https://github.com/zbjornson/fast-hex) · [benchmark](https://github.com/zbjornson/fast-hex#readme) |

## Verdict

The README's \~12.5x decode and \~11.5x encode are ratios against the library's own scalar LUT functions. It gives no CPU, compiler, input size or raw throughput, and there is no C++ harness. The only raw figures are in Book1.xlsx (sheet 3, Node ops/s on the '1.6M' rows): 812 scalar LUT vs 1726 'vec8' on V8 strings (2.12x) and 1466 vs 18549 on Buffers (12.65x), while the plain 'vec' column shows 1.9x and 5.7x; 'vec8' matches no function in the published source.

## Use it when

- Bulk hex conversion of large, trusted buffers (KB to MB) on x86-64 CPUs with AVX2, e.g. ingesting or emitting hex-encoded blobs or large batches of digests.
- C/C++ projects that can vendor two source files and compile them with -mavx2 / -march=haswell (or /arch:AVX2 on MSVC) for a fixed, known-AVX2 deployment target.
- Decoding mixed-case hex (A-F and a-f both accepted) where the producer is trusted or the input was validated upstream.
- As a small, readable reference kernel (about 270 lines of intrinsics) to adapt into your own hex codec, e.g. adding validation or runtime dispatch.

## Skip it when

- Untrusted input: invalid characters silently become garbage bytes and there is no error return; the README says validation is not implemented.
- Portable binaries or non-x86 targets: there is no runtime CPU dispatch and no SSE, AVX-512 or NEON path; the AVX2 functions exist only when the whole file is compiled with AVX2 enabled, and only the scalar functions remain otherwise.
- Node.js from npm: the only release (fast-hex 1.0.0, 2017-10-30) ships the sign-extending byte2nib that issue #4 showed mis-encodes bytes &gt;= 0x80 (0x80 -&gt; "8f"), fixed in git only in 2019. The addon's binding.gyp also builds with -march=native and calls the AVX2 functions unconditionally, so it will not compile on a non-AVX2 build host.
- Short inputs: under 16 bytes (encode) or 64 characters (decode) everything runs on the scalar tail, so there is no gain. For V8 strings the README reports only \~2.12x, because copying the string out of V8 dominates.
- When you need upper-case hex output: both encoders emit lower-case only.

## How it is fast

The decoder loads 64 hex characters per iteration into two AVX2 registers, uses vpshufb to split high-nibble and low-nibble characters into 16-bit lanes, and converts ASCII to nibble values branchlessly as 9\*(c&gt;&gt;6) + (c & 0xF) (vpsraw + vpmaddubsw + vpaddw), then recombines with shift/or, vpackuswb and vpermq to store 32 bytes. The encoder zero-extends 16 bytes to 16-bit lanes (vpmovzxbw), splits nibbles with a shift plus a byte shuffle, and maps each nibble to its ASCII digit with one vpshufb against a 16-entry '0'-'f' table, writing 32 characters per iteration. Skipping validation keeps both loops branch-free; leftover bytes fall back to scalar code.

## Compared with alternatives

No other hex codec is catalogued; the siblings are base64 and CRC libraries, so pick this when the format must be hex. If you control the format, a base64 sibling such as aklomp/base64 expands data 4/3x instead of 2x and does runtime CPU feature detection on x86 with scalar and NEON codecs, none of which this library has.

## Integration

| | |
|---|---|
| **Form** | source-drop (src/hex.h + src/hex.cc); optional Node.js native addon built with node-gyp |
| **Dependencies** | none for C++ (compiler intrinsics headers only); the Node addon needs nan and node-gyp |
| **Minimum toolchain** | README lists GCC 4.8+, Clang 3.4+, MSVC 2015+ and ICC 16+, but hex.cc uses a C++14 digit separator (0b11'01'10'00), which GCC supports only from 4.9, so in practice C++14 mode and GCC 4.9+ |
| **Platforms** | x86-64 with AVX2 (Haswell or later) for the vector paths; the scalar functions compile anywhere |
| **Thread safety** | Not documented. The functions are stateless and only read static const tables, so concurrent calls on separate buffers look safe from the source. |
| **Drop-in for the baseline** | partial — same buffer-to-buffer shape as a scalar hex codec, but it does no validation, encodes lower-case only, takes len in bytes rather than characters, and requires non-overlapping src/dest (__restrict__), so in-place decoding is not allowed |

## Gotchas

- len is the byte count (half the hex-string length) for both encode and decode. Passing the character count to decodeHexVec over-reads src and over-writes dest; the author clarified this in 2019 after a user in issue #4 hit it.
- Invalid input is not rejected. The vector path computes 9\*(c&gt;&gt;6) + (c & 0xF) for any byte, and the LUT path ORs a 0xFF sentinel into the output, so non-hex characters decode to some byte without any error.
- Node addon: decodeHexVec writes inputLength/2 bytes into the destination typed array without checking its size, drops the last character of odd-length input, and for a two-byte (UTF-16) string or a non-string argument it leaves the source pointer uninitialized (it only prints a message).
- Tests are thin: test.js checks one 43-byte vector against the scalar paths. benchmark/hex-decode.js calls decodeHexBMI, which the addon no longer exports, and hex-encode.js benchmarks an all-zero buffer.

## Known shortcomings

- Decode 'node' baseline is the addon's own scalar lookup-table code, not Node's built-in Buffer hex; last code change 2022-09 (only dependabot commits since).
- Headline ratios (2.12x string / 12.65x buffer) come from a 'vec8' spreadsheet column that matches no shipped function; the shipped 'vec' path measures 1.9x / 5.7x. The only npm release (1.0.0, 2017) predates the #4 fix, so its encodeHexVec is wrong for bytes &gt;= 0x80. No input validation, no CPU dispatch (AVX2 only), lowercase-only encoding; addon lacks a destination size check. Needs GCC 4.9+, not 4.8.

## Caveats and trade-offs

The README gives ratios only: no CPU model, compiler version or raw throughput, so tier C is the cap. The README does not say what the Node.js figures are measured against. In the current scripts the decode 'node' baseline is the addon's own scalar LUT, and the decode script still references decodeHexBMI, which is no longer exported. The encode script's input buffer is all zeros because its fill loop discards Math.random(). There is no C++ benchmark harness; Book1.xlsx holds only hand-computed cycle and port estimates. The library does not validate input and needs AVX2. The last code change was 2022-09-19; the only 2026 commit (2026-01-22) is a Dependabot lodash bump in /benchmark.

Does not validate input by design (documented limitation, PR welcome to add it); requires AVX2 (Haswell or later), no documented fallback path for older CPUs

## Maintenance

Code last changed 2022-09-19 (outside-contributor AVX2 guards and a -Wnarrowing fix), and the only 2026 activity is Dependabot lodash bumps in /benchmark, so it is effectively dormant; it is MIT-licensed and small enough to vendor and audit, but use the git source, not npm 1.0.0.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README gives only ratios: about 12.5x decode and 11.5x encode over the library's own scalar LUT codec, plus Node.js module ratios. The Node benchmark scripts (benchmark/hex-decode.js, benchmark/hex-encode.js) are public, but there is no C++ harness and no CPU model, compiler or raw throughput, so these are first-party numbers without methodology: tier C.
- **Verifier notes:** The numbers match the README. Only the baseline attribution needed fixing: the decode ratios are not demonstrably against Node's built-in hex decoder. 'Active' status is correct under the 12-month rule, but it rests on a Dependabot-only commit, so real maintenance is closer to stale.
- **Fields the verifier corrected:** `workload`, `claimed_speedup`, `compared_against_cpp_std_directly`, `caveats`
- **Shortcomings recorded by:** Author's Book1.xlsx, shipped 'vec' path: 1.9x (string) / 5.7x (buffer) vs Node scalar.
- **Pages the verifier opened:**
  - <https://github.com/zbjornson/fast-hex>
  - <https://github.com/zbjornson/fast-hex#readme>
  - <https://github.com/zbjornson/fast-hex/tree/master/benchmark>
  - <https://github.com/zbjornson/fast-hex/blob/master/benchmark/hex-decode.js>
  - <https://github.com/zbjornson/fast-hex/blob/master/benchmark/hex-encode.js>
  - <https://github.com/zbjornson/fast-hex/blob/master/src/strdecode.cc>
  - <https://github.com/zbjornson/fast-hex/blob/master/src/hex.h>
  - <https://raw.githubusercontent.com/zbjornson/fast-hex/master/Book1.xlsx>
- **Sources the enricher read:**
  - <https://github.com/zbjornson/fast-hex>
  - <https://github.com/zbjornson/fast-hex#readme>
  - <https://github.com/zbjornson/fast-hex/tree/master>
  - <https://github.com/zbjornson/fast-hex/blob/master/src/hex.h>
  - <https://github.com/zbjornson/fast-hex/blob/master/src/hex.cc>
  - <https://github.com/zbjornson/fast-hex/blob/master/src/strdecode.cc>
  - <https://github.com/zbjornson/fast-hex/blob/master/binding.gyp>
  - <https://github.com/zbjornson/fast-hex/blob/master/package.json>
  - <https://github.com/zbjornson/fast-hex/blob/master/test.js>
  - <https://github.com/zbjornson/fast-hex/blob/master/benchmark/hex-decode.js>
  - <https://github.com/zbjornson/fast-hex/blob/master/benchmark/hex-encode.js>
  - <https://github.com/zbjornson/fast-hex/blob/master/benchmark/package.json>
  - <https://github.com/zbjornson/fast-hex/commits/master>
  - <https://github.com/zbjornson/fast-hex/commit/7b26210>
  - <https://github.com/zbjornson/fast-hex/issues?q=is%3Aissue+OR+is%3Apr>
  - <https://github.com/zbjornson/fast-hex/issues/2>
  - <https://github.com/zbjornson/fast-hex/issues/3>
  - <https://github.com/zbjornson/fast-hex/issues/4>
  - <https://github.com/zbjornson/fast-hex/issues/8>
  - <https://raw.githubusercontent.com/zbjornson/fast-hex/master/Book1.xlsx>
  - <https://registry.npmjs.org/fast-hex>
  - <https://registry.npmjs.org/fast-hex/-/fast-hex-1.0.0.tgz>
  - <https://gcc.gnu.org/projects/cxx-status.html>
  - <https://github.com/aklomp/base64#readme>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/zbjornson/fast-hex`) · [data/wave7/enrich/raw/github_com_zbjornson_fast_hex.json](../../../data/wave7/enrich/raw/github_com_zbjornson_fast_hex.json) (enrichment confidence 0.8)

</details>
