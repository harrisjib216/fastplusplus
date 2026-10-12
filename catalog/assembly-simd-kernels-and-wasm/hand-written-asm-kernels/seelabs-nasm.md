# seelabs/nasm (AVX2 hex encoder and decoder for 256-bit values in NASM)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Hand-written assembly kernels](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `no license` · 🔴 abandoned

> Learning-project NASM AVX2 kernels that hex-encode 32 bytes and hex-decode 64 digits 5.6x and 8.4x faster than rippled's scalar C++.

| | |
|---|---|
| **Beats** | reference C++ hex encode and decode routines taken from rippled (compiled with g++ -O3 according to build.sh) |
| **Claimed result** | README table: encoder 1790 ms (C reference) vs 319 ms (assembly), 5.6x (derived from page data); decoder 4694 ms vs 561 ms, 8.4x (derived from page data). README prose says 'about 10x faster than the reference C++ implementation'. |
| **Workload** | Encode a 32-byte binary value into 64 hex characters (encode_hex256) and decode 64 hex characters into 32 bytes (decode_hex256), 100 million iterations each, test driver src/main.cpp. |
| **Metric** | throughput |
| **Hardware** | Intel Xeon E3-1505M v6 at 3.00 GHz |
| **Compiler and flags** | Not stated in the README and no compiler version anywhere. build.sh uses nasm -felf64 and g++ -std=c++14 -O3 (no -march or -mavx2, so the C reference is scalar); CMakeLists.txt instead defaults to clang with CMAKE_BUILD_TYPE Debug plus -ggdb -fno-omit-frame-pointer. Which build produced the table is unknown. |
| **Adoption** | 1 star |
| **Last commit** | 2018-05-22 |
| **Links** | [repository](https://github.com/seelabs/nasm) · [benchmark](https://github.com/seelabs/nasm) |

## Verdict

Author's single run on a Xeon E3-1505M v6 at 3.00 GHz (Kaby Lake, AVX2), 100 million calls on one constant input, compiler and flags unrecorded (build.sh says g++ -O3 without -mavx2): encode 32 bytes 1790 ms for the scalar rippled-style C++ vs 319 ms for AVX2 assembly (5.6x; about 3.2 ns per call, roughly 10 GB/s of input, derived from page data), decode 64 digits 4694 vs 561 ms (8.4x; about 11.4 GB/s of hex input, derived from page data); the README's 'about 10x' rounds both up.

## Use it when

- Reading material: a compact, commented example of table-free AVX2 hex encoding and validating hex decoding, including the lane-crossing fix-up that vpshufb needs.
- As a design reference when writing your own fixed-width (32-byte hash, 64-digit) hex codec for transaction or block IDs on AVX2 x86-64 Linux, where the input length is always known.
- Comparing hand-written AVX2 against an intrinsics or auto-vectorised port of the same algorithm; the repo gives the algorithm, not a reusable library.

## Skip it when

- Anything you ship: there is no LICENSE file, so the code cannot legally be copied, and the author calls it a learning exercise that is 'not well tested'.
- Variable-length data: only exactly 32 bytes in and 64 digits out (or the reverse) are handled; use a general SIMD hex codec instead.
- Windows or non-AVX2 CPUs: there is no CPU-feature dispatch (SIGILL before Haswell) and the code uses the System V registers RDI/RSI; a Win64 port must also save xmm6-xmm11, which are callee-saved there and clobbered by decode.asm.
- Lowercase output or strict rippled semantics: the encoder emits uppercase only, and unlike rippled's SetHexExact the decoder does not require a NUL after the 64th digit.

## How it is fast

Both kernels replace per-character table lookups and branches with 32-lane AVX2 byte arithmetic. The encoder zero-extends each byte to a 16-bit word (vpmovzxbw), splits the nibbles with masks and shifts, then adds 48 or 55 per lane chosen by a vpcmpgtb/vpblendvb mask. The decoder upcases letters by clearing bit 5, rejects bad digits with two vptest checks, subtracts 48 or 55 by blend, merges nibble pairs with a 16-bit shift-by-12 and add, and compacts the odd bytes with vpshufb plus vextracti128/vinserti128 lane moves; each call is about 20-30 instructions with no loop.

## Compared with alternatives

Pick it only as a teaching reference: tmthrgd/go-hex (sibling, Go SSE/AVX assembly, any length, 25.6x encode and 24.8x decode at 1 KB vs encoding/hex) is a usable library, and for C or C++ the catalogued zbjornson/fast-hex (AVX2, any length, about 11.5x encode and 12.5x decode over scalar) covers the same job with a licence.

## Integration

| | |
|---|---|
| **Form** | source-drop (src/encode.asm and src/decode.asm, assembled with nasm -felf64 and linked as extern "C" functions) |
| **Dependencies** | none for the kernels; the test driver is C++14 and the CMake build also requires Boost (program_options, multiprecision for the base58 experiment) |
| **Minimum toolchain** | NASM with AVX2 support (version not documented); C++14 compiler for the driver |
| **Platforms** | x86-64 with AVX2 only, ELF64 System V calling convention (Linux) |
| **Thread safety** | Reentrant pure functions (constants are only read, though they sit in a writable .data section); not documented by the author |
| **Drop-in for the baseline** | partial: decode_hex256 matches rippled's SetHexExact for 64-digit inputs (verified by the driver's 1 million random cases with and without bad digits) but skips the terminator check and leaves the output untouched on error; encode_hex256 matches the uppercase table encoder for 32-byte inputs |

## Gotchas

- The committed driver cannot reproduce the README table: in the only commit (2018-05-22) main() returns right after test_base58(), so the hex tests and benchmarks are unreachable; build.sh (g++ -O3, no -mavx2) and CMakeLists.txt (clang, Debug default, -ggdb) disagree, and no compiler version is recorded.
- Harness detail: each benchmark loop reruns one constant input 100 million times and never reads the output; the scalar reference is inlined while the assembly is an out-of-line call, so dead-store elimination, perfect branch prediction and call overhead all favour the C side. The 5.6x and 8.4x look conservative, not inflated, but they compare a SIMD algorithm with scalar table-lookup C built without -mavx2, not hand assembly with the best compiler output.
- Correction to the record's caveat: the benchmark's reference loop is fixed at 32 iterations, just as rippled's SetHexExact is fixed by base_uint's size, so the gap is not from fixed-size specialisation; the harness copy even drops rippled's final terminator check, which slightly helps the C side.
- No correctness bug found on reading both kernels: the decoder's two error masks reject every byte outside 0-9, A-F and a-f (including bytes 0x80-0xFF), and the vpshufb compaction and lane merge place all 32 output bytes in order. The README's prose giving 87 as the letter offset does not match the code, which upcases first and subtracts 55. The separate base58 experiment (decode58.asm, vpgatherdd over a 256-dword alphabet table) gained only about 6% overall per the README.

## Known shortcomings

- README says 10x but its own table shows 5.6x/8.4x; the committed main.cpp returns before the hex benchmark and build.sh is out of sync with the sources; no compiler version; no licence (reference).
- Both kernels read: no correctness bug. Harness flaws favour the C side (inlined scalar reference, output never read, one constant input, the asm called out of line), so the 5.6x and 8.4x look conservative; the comparison is AVX2 SIMD against scalar C built without -mavx2, not hand assembly against the best compiler output. Record correction: rippled 1.0.0's SetHexExact is also fixed-size (base_uint) and the harness reference loop is a fixed 32 iterations, so the earlier 'specialisation' caveat was wrong; the harness drops rippled's terminator check. The README's '87' letter offset does not match the code (55); a Win64 port would clobber callee-saved xmm6-xmm11.

## Caveats and trade-offs

The kernels are specialised to one fixed size (32 bytes, 64 hex digits) while the rippled baseline handles any length, so part of the gain comes from specialisation rather than assembly itself. The README's 'about 10x faster' is not matched by its own table (5.6x encode, 8.4x decode). Single machine, single run, the same constant input every iteration, no compiler version. The table cannot be reproduced from the committed code without edits: in the repository's only commit (2018-05-22) src/main.cpp returns right after test_base58(), so the hex benchmarks are unreachable, and build.sh does not assemble decode58.asm although codec_base58.h declares base58_8_coeff, while CMakeLists.txt defaults to a clang Debug build. The reference loops write to a local buffer that is never read, so an optimising compiler could shrink the C side (this would understate, not inflate, the assembly gain). The driver does random-test both kernels against the reference (1 million inputs, including invalid digits for the decoder), but the author calls the code a learning exercise that is 'not well tested'. No licence file, so reference only. The README also reports an AVX base58 coefficient routine gave only about 6% overall, and its 10x base58 gain over rippled (2199 ms versus 231 ms, 1 million iterations) is plain C++, not assembly. [retier] The README's 'about 10x faster' is not matched by its own table (5.6x encode, 8.4x decode). Single machine, single run, the same constant input every iteration, no compiler version; the C reference is scalar table-lookup code built without -mavx2 (build.sh: g++ -std=c++14 -O3), so this compares an AVX2 SIMD algorithm with scalar C, not hand assembly with the best compiler output. Harness flaws favour the C side: each loop reruns one constant input 100 million times and never reads the output, the scalar reference is inlined while the assembly is an out-of-line call, and the harness copy drops rippled's final terminator check; the ratios therefore look conservative rather than inflated. The committed driver cannot reproduce the table: in the only commit (2018-05-22) main() returns right after test_base58(), so the hex benchmarks are unreachable, and build.sh and CMakeLists.txt (clang, Debug default) disagree. The kernels handle a fixed 32-byte/64-digit input, as does rippled's SetHexExact (base_uint is fixed-size) and the harness reference loop (32 iterations), so the gap is not from fixed-size specialisation. No correctness bug found on reading both kernels (the decoder's masks reject every byte outside 0-9, A-F and a-f); the README's '87' letter offset does not match the code (upcase then subtract 55); a Win64 port would clobber callee-saved xmm6-xmm11. The separate base58 experiment gained only about 6%.

x86-64 with AVX2 only, Linux System V calling convention only, fixed 32-byte (64 hex digit) inputs. No LICENSE file in the repository root, so the code must not be copied. Author states it is for learning and not well tested.

## Maintenance

Abandoned single-commit learning repo from May 2018 with 1 star and no licence, so it is reference-only: read the 73- and 165-line kernels for the technique but do not copy them.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README table (Xeon E3-1505M v6, 100 million iterations) against the rippled reference routines, with benchmark code in src/codec_hex.h, but no compiler version, an ambiguous build (build.sh g++ -O3 versus CMake clang Debug default), and a committed driver that cannot produce the table without edits; not raised to A.
- **Verifier notes:** Numbers 1790/319 ms and 4694/561 ms and the CPU are on the README; ratios 5.6x and 8.4x are correct as derived. Shortcomings to record: README 10x overstated versus own table, fixed-size specialisation versus general baseline, committed main.cpp returns before the hex benchmark and build.sh is out of sync with the sources, no compiler version, no licence, single-commit learning project with 1 star. Kept at C; the record's suggestion of tier A is not supported.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-115 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/seelabs/nasm>
  - <https://github.com/seelabs/nasm/commits/master>
  - <https://raw.githubusercontent.com/seelabs/nasm/master/readme.md>
  - <https://raw.githubusercontent.com/seelabs/nasm/master/build.sh>
  - <https://raw.githubusercontent.com/seelabs/nasm/master/CMakeLists.txt>
  - <https://raw.githubusercontent.com/seelabs/nasm/master/src/main.cpp>
  - <https://raw.githubusercontent.com/seelabs/nasm/master/src/codec_hex.h>
  - <https://raw.githubusercontent.com/seelabs/nasm/master/src/codec_base58.h>
- **Sources the enricher read:**
  - <https://github.com/seelabs/nasm>
  - <https://github.com/seelabs/nasm/commits/master>
  - <https://raw.githubusercontent.com/seelabs/nasm/master/readme.md>
  - <https://raw.githubusercontent.com/seelabs/nasm/master/build.sh>
  - <https://raw.githubusercontent.com/seelabs/nasm/master/CMakeLists.txt>
  - <https://raw.githubusercontent.com/seelabs/nasm/master/src/main.cpp>
  - <https://raw.githubusercontent.com/seelabs/nasm/master/src/codec_hex.h>
  - <https://raw.githubusercontent.com/seelabs/nasm/master/src/codec_base58.h>
  - <https://raw.githubusercontent.com/seelabs/nasm/master/src/encode.asm>
  - <https://raw.githubusercontent.com/seelabs/nasm/master/src/decode.asm>
  - <https://raw.githubusercontent.com/seelabs/nasm/master/src/decode58.asm>
  - <https://raw.githubusercontent.com/seelabs/nasm/master/.gdb>
  - <https://raw.githubusercontent.com/seelabs/nasm/master/.gitignore>
  - <https://raw.githubusercontent.com/XRPLF/rippled/1.0.0/src/ripple/basics/strHex.h>
  - <https://raw.githubusercontent.com/XRPLF/rippled/1.0.0/src/ripple/basics/base_uint.h>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/seelabs/nasm`) · [data/wave13/enrich/raw/github_com_seelabs_nasm.json](../../../data/wave13/enrich/raw/github_com_seelabs_nasm.json) (enrichment confidence 0.78)

</details>
