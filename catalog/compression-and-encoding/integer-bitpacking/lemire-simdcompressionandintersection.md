# SIMDCompressionAndIntersection

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Integer compression and bit-packing](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> C++ research library of SIMD codecs (S4-BP128, SIMD-FastPFOR) for sorted uint32 lists, plus SIMD sorted-list intersection.

| | |
|---|---|
| **Beats** | FastPFor (scalar) / varint-G8IU / VByte |
| **Claimed result** | Paper (WebSearch snippets only): SIMD-BP128 nearly twice as fast as the previously fastest schemes (varint-G8IU and PFOR) while saving up to 2 bits per integer; SIMD-BP128-D1-NI 38% faster than SIMD-FastPFOR; S4-BP128-D4 as little as 0.7 CPU cycles per decoded 32-bit integer; SIMD schemes 2-3x faster than FastPFOR and varint with comparable ratio. README: 15 GB/s decompression. |
| **Workload** | Compression and decoding of sorted 32-bit integer lists with differential coding (SIMD-BP128, S4-BP128, SIMD-FastPFOR) plus SIMD intersection of sorted lists. |
| **Metric** | throughput |
| **Compiler and flags** | g++ (version unstated); harness built with -Wall -O3 -std=c++11 per the shootout Makefile; the library is built with its own Makefile (make), whose release flags are -O3 plus optional SIMD flags; the CMake Release build in the README applies only to google/benchmark |
| **Last commit** | 2026-06-07 |
| **Links** | [repository](https://github.com/lemire/SIMDCompressionAndIntersection) |

## Verdict

A third-party harness (vteromero/integer-compression-benchmarks, g++ -O3 -std=c++11, compiler version unstated, Core i7-6700HQ) on gov2.sorted measured this library's scalar Delta+BinaryPacking at 2.30 G/s encode and 2.33 G/s decode vs its own Delta+VariableByte at 1.62/1.52 G/s and Delta+FastPFor128 at 615.66/615.64 M/s; all codecs in that run come from this library and the SIMD S4-BP128 path was not the one measured. The README's 15 GB/s (4 billion integers/s) decode figure and the papers' 2x-over-varint-G8IU claims have no reproducible table in the repo.

## Use it when

- Inverted-index or search-engine posting lists: sorted uint32 doc IDs where you decode whole lists and then intersect them.
- Read-heavy sorted integer columns where decode speed matters more than the last bit per integer, on x86 with SSE4.1/AVX or on AArch64 (NEON mapping added in 0.2.0).
- Benchmarking or prototyping: one factory exposes about 25 codecs (vbyte, varintgb, maskedvbyte, streamvbyte, fastpfor, bp32, s4-bp128-\*, s4-fastpfor-\*, for) behind one interface, so you can compare ratio and speed on your own data.
- Intersecting a short list against a much longer one (query AND processing): SIMD Galloping is built for skewed list lengths.

## Skip it when

- Unsorted integers: the codecs assume sorted input for differential coding; use FastPFor or simdcomp's non-delta routines instead.
- Untrusted compressed input or output buffers you cannot size generously: issue #19 (open since 2017) reports an access violation rather than a NotEnoughStorage exception when the decode buffer is too small, and there is no bounds checking on decode.
- 64-bit integers: the API is uint32_t only.
- Production code that needs a small, stable API: the README itself calls it a C++ research library and points to the C library simdcomp for something simpler.
- Best compression ratio: in the vteromero gov2 run FastPFor128 compressed better (6.21 vs 5.52) and Delta+VarIntGB decoded faster than the scalar BinaryPacking row.

## How it is fast

S4-BP128 is SIMD binary packing: blocks of 128 integers are bit-packed across four 32-bit SSE lanes at one bit width per block, so unpacking is shifts and masks with no branches per value. The delta (prefix-sum) step is vectorized and, in the non-'-ni' variants, integrated into the unpack loop; D2/D4/DM variants use coarser four-lane deltas to trade a little ratio for faster prefix sums. SIMD-FastPFOR adds patched exceptions to the same packers. Intersections use SIMD block comparison (v1/v3) and SIMD Galloping, which skips through the larger list with vector compares.

## Compared with alternatives

Pick it over FastPFor or simdcomp when your lists are sorted and you also need fast intersection, since FastPFor is not tuned for sorted lists (per this README) and simdcomp has no intersection or codec factory. Pick Stream VByte or MaskedVByte when you want byte-oriented codecs as a small C library, and TurboPFor when you want more codecs and are fine with GPL.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | none |
| **Minimum toolchain** | C++11 and C99; GCC 4.7+, Clang, Intel or Visual C++; CMake 3.10+ for the CMake build (Makefile and nmake makefile.vc also provided) |
| **Platforms** | x86/x64 (SSE2 required, SSE4.1 recommended; default build passes -mavx or /arch:AVX) and AArch64 (SSE intrinsics mapped to NEON via include/neon_sse.h); tested on Linux, macOS and Windows; uses POSIX headers such as sys/mman.h in common.h |
| **Thread safety** | not documented; the factory returns shared singleton codec objects, and some codecs (SIMDFastPFor) keep internal scratch buffers as members, so use one codec instance per thread rather than the shared factory instance |
| **Drop-in for the baseline** | no |

## Gotchas

- Some codecs do the delta coding in place and overwrite your input array (bp32, fastpfor, s4-bp128-\*-ni, s4-fastpfor-\*), per example.cpp; encodeArray takes a non-const pointer. Copy the input first if you need it.
- The caller allocates the output; nvalue is in/out and, per codecs.h, a value larger than what you passed means a buffer overrun already happened. Allocate generously (the example uses N + 1024 words).
- CODECFactory::getFromName returns a null shared_ptr (after printing to cerr) for an unknown name, so dereferencing it crashes; varintg8iu is only registered when compiled with SSSE3 and its header is marked 'warning: patented scheme', although the README says the work is patent-free as far as the authors know.
- Header names (codecfactory.h, codecs.h, fastpfor.h) overlap with the FastPFor library; since issue #2 the code is in namespace SIMDCompressionLib, but installed headers are added flat to the include path, so keep the two libraries' include directories separate.

## Known shortcomings

- Tier C: gov2 numbers come from the vteromero shootout (i7-6700HQ, g++ version unstated) where the BinaryPacking baseline is the scalar BinaryPacking&lt;BasicBlockPacker&gt; and all codecs come from the same library. Papers (SPE 2015, IPL 2018 arXiv 1709.08990, ADCS 2016) blocked; possible B later.
- Open issue #19 (since 2017): a too-small decode buffer gives an access violation instead of NotEnoughStorage (no decode bounds check). Some codecs overwrite the input during in-place delta (bp32, fastpfor, s4-bp128-\*-ni, s4-fastpfor-\*); the factory hands out shared singleton codecs and SIMDFastPFor keeps scratch buffers as members, so it is not thread-safe; uint32 only. The measured vteromero row is scalar BinaryPacking, not S4-BP128. Low maintenance cadence (0.2.0 on 2026-06-07).

## Caveats and trade-offs

The shootout's BinaryPacking row is the scalar variant: gov2.cc instantiates SIMDCompressionLib::BinaryPacking&lt;BasicBlockPacker&gt;, not the SIMD packer. All codecs in the comparison (VByte, VarIntGB, FastPFor, BinaryPacking) come from this same library, so the baseline is the library's own VByte/FastPFor implementation, not an outside incumbent. Delta+VarIntGB decodes faster on gov2 (2.97 G/s) than BinaryPacking, and FastPFor128 compresses better (ratio 6.21 vs 5.52). The shootout is by the author of a competing codec (VTEnc); compiler version unstated. The README's '4 billion integers per second / 15 GB/s' claim has no table or methodology. The library overlaps with FastPFor and simdcomp, which are listed separately.

Requires SSE2 (SSE4.1 for some schemes); includes patented varint-G8IU implementation (README warns); research code with a larger API than simdcomp.

## Maintenance

Maintained at low cadence (bursts in 2022, one commit in 2025, ARM/NEON support and version 0.2.0 on 2026-06-07; 4 open issues, 447 stars), Apache-2.0 and buildable with Make, CMake or nmake, so it is easy to vendor as a static library.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now C.
- **Tier reason:** The vteromero/integer-compression-benchmarks README gov2.sorted table shows Delta+BinaryPacking 2.30 G/s encode / 2.33 G/s decode vs Delta+VariableByte 1.62 / 1.52 and Delta+FastPFor128 615.66 / 615.64 M/s on a Core i7-6700HQ, with public harness code (gov2.cc, intbench.cc). The harness Makefile names g++ with -O3 -std=c++11 but no compiler version, so not A; it is a small (5-star) third-party repo by a competing codec's author, not a well-known suite, so C.
- **Verifier notes:** Numbers and ratios check out (derived ratios \~1.4x/\~1.5x vs VByte, \~3.7x vs FastPFor128 encode). The SPE papers cited in the README (Lemire and Boytsov 2015; SIMD compression and intersection) might support B but arXiv is blocked here; candidate for a paper-access retier. Metadata confirmed: 447 stars, Apache-2.0, last commit 2026-06-07 (version 0.2.0).
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/vteromero/integer-compression-benchmarks>
  - <https://raw.githubusercontent.com/vteromero/integer-compression-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/vteromero/integer-compression-benchmarks/HEAD/Makefile>
  - <https://raw.githubusercontent.com/vteromero/integer-compression-benchmarks/HEAD/gov2.cc>
  - <https://github.com/lemire/SIMDCompressionAndIntersection>
  - <https://github.com/lemire/SIMDCompressionAndIntersection/commits>
  - <https://raw.githubusercontent.com/lemire/SIMDCompressionAndIntersection/HEAD/README.md>
  - <https://raw.githubusercontent.com/lemire/SIMDCompressionAndIntersection/HEAD/Makefile>
- **Sources the enricher read:**
  - <https://github.com/lemire/SIMDCompressionAndIntersection>
  - <https://github.com/lemire/SIMDCompressionAndIntersection/commits>
  - <https://github.com/lemire/SIMDCompressionAndIntersection/issues>
  - <https://github.com/lemire/SIMDCompressionAndIntersection/issues?q=is%3Aissue+is%3Aclosed>
  - <https://github.com/lemire/SIMDCompressionAndIntersection/issues/19>
  - <https://github.com/lemire/SIMDCompressionAndIntersection/issues/24>
  - <https://github.com/lemire/SIMDCompressionAndIntersection/issues/2>
  - <https://raw.githubusercontent.com/lemire/SIMDCompressionAndIntersection/HEAD/README.md>
  - <https://raw.githubusercontent.com/lemire/SIMDCompressionAndIntersection/HEAD/Makefile>
  - <https://raw.githubusercontent.com/lemire/SIMDCompressionAndIntersection/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/lemire/SIMDCompressionAndIntersection/HEAD/example.cpp>
  - <https://raw.githubusercontent.com/lemire/SIMDCompressionAndIntersection/HEAD/include/codecfactory.h>
  - <https://raw.githubusercontent.com/lemire/SIMDCompressionAndIntersection/HEAD/include/codecs.h>
  - <https://raw.githubusercontent.com/lemire/SIMDCompressionAndIntersection/HEAD/include/intersection.h>
  - <https://raw.githubusercontent.com/lemire/SIMDCompressionAndIntersection/HEAD/include/common.h>
  - <https://raw.githubusercontent.com/lemire/SIMDCompressionAndIntersection/HEAD/include/platform.h>
  - <https://raw.githubusercontent.com/lemire/SIMDCompressionAndIntersection/HEAD/include/simdfastpfor.h>
  - <https://raw.githubusercontent.com/lemire/SIMDCompressionAndIntersection/HEAD/include/simdbinarypacking.h>
  - <https://raw.githubusercontent.com/lemire/SIMDCompressionAndIntersection/HEAD/src/codecfactory.cpp>
  - <https://raw.githubusercontent.com/lemire/SIMDCompressionAndIntersection/HEAD/src/intersection.cpp>
  - <https://raw.githubusercontent.com/vteromero/integer-compression-benchmarks/HEAD/README.md>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/lemire/simdcompressionandintersection`) · [data/wave9/enrich/raw/github_com_lemire_simdcompressionandintersection.json](../../../data/wave9/enrich/raw/github_com_lemire_simdcompressionandintersection.json) (enrichment confidence 0.7)

</details>
