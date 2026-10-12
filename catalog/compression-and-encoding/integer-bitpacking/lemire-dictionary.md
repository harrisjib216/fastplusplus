# dictionary (AVX2/AVX-512 fused bit-unpack plus dictionary decode)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Integer compression and bit-packing](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🔴 abandoned

> Research demo that fuses bit-unpacking and dictionary lookup with AVX2/AVX-512 gathers; about 2x its own scalar decoder.

| | |
|---|---|
| **Beats** | Scalar binary-unpack-then-lookup dictionary decoder (scalarcodec) in the same repo; not a named external incumbent |
| **Claimed result** | Skylake, gcc 5.3.0: dictionary size 2 scalarcodec.uncompress 4.00 cycles per value vs AVXDictCODEC::fastuncompress 1.91 (2.1x derived from page data); size 4096 4.14 vs 2.12; size 1048576 11.85 vs 8.47. README: AVX2 decoder 'more than twice as fast as a good scalar decoder' for modest dictionary sizes. Knights Landing, size 2: scalar 7.75 vs AVX2 3.22 vs AVX512DictCODEC 1.48 cycles per value (5.2x derived from page data). |
| **Workload** | Decode 8388608 dictionary-coded 64-bit values (bit-packed indexes into a dictionary of 2 to 1048576 entries) to RAM, measured in cycles per decoded value; the fused AVX2 gather approach unpacks indexes and looks up dictionary values in one step. |
| **Metric** | throughput |
| **Hardware** | Intel Skylake (microarchitecture only, no exact model) and Intel Knights Landing (printed as UNKNOWN) |
| **Compiler and flags** | gcc 5.3.0 (printed in README benchmark output); Makefile sets -fPIC -O3 -march=native -std=c++11 (not stated next to the results) |
| **Adoption** | 112 stars |
| **Last commit** | 2017-04-05 |
| **Links** | [repository](https://github.com/fast-pack/dictionary) · [benchmark](https://github.com/lemire/dictionary) |

## Verdict

The repo's decodebenchmark (8,388,608 uniformly random indexes, best of 5 runs timed with rdtsc, i.e. TSC ticks) shows AVX2 fused decode at 1.91 cycles per value against 4.00 for the repo's own scalar unpack-then-lookup decoder on Skylake with GCC 5.3.0 for a 2-entry dictionary, 2.12 vs 4.14 at 4096 entries and 8.47 vs 11.85 at 1,048,576. On an unnamed Knights Landing part, AVX-512 reached 1.48 cycles per value against 3.22 (AVX2) and 7.75 (scalar) at size 2. No external codec was measured.

## Use it when

- Decoding long arrays of 64-bit values (or pointers) with few distinct values, such as Parquet- or ORC-style dictionary-encoded columns, on x86-64 with fast gathers (Skylake or later, AVX-512 parts).
- Small to medium dictionaries that stay in L1/L2: on Skylake the AVX2 path is about 1.9-2.1 cycles per value against about 4.0-4.1 for the scalar unpack-then-lookup loop up to 4096 entries.
- As a reference design when adding a fused unpack+gather decode kernel to your own column store; the per-bit-width kernels are generated code that can be lifted.
- Block-wise decoding into a cache-resident buffer (fastrangeuncompress), which on Skylake reached about 1.15-1.3 cycles per value for small dictionaries.

## Skip it when

- Production use: the README says it is a demo, uses its own format, and is not meant to plug into an existing framework.
- Untrusted compressed input: there are no bounds checks; any index at or above dictionary_size makes the gather read outside the dictionary array, and length/alignment preconditions are only assert()s.
- Large dictionaries that spill out of cache: the gain shrinks to 11.85 vs 8.47 cycles per value at 1,048,576 entries on Skylake and 21.93 vs 16.33 (AVX2) on Knights Landing.
- Non-x86 targets or CPUs without AVX2 (the headers #error out), or older Haswell/Broadwell parts where the README warns vpgather was slow.
- Arrays whose length is not a multiple of 256 (AVX2) or 512 (AVX-512), arrays over 2^32 values (uint32 counts), or value types other than 64-bit words.

## How it is fast

The fast path never materializes the index array: one generated, fully unrolled routine per bit width (0-32) loads 256 (AVX2) or 512 (AVX-512) packed indexes with vector loads, isolates each lane with shifts and masks, and feeds the 32-bit indexes straight into vpgatherdq (_mm256_i32gather_epi64 / _mm512_i32gather_epi64) to fetch the 64-bit dictionary words, which are stored directly to the output. The scalar baseline instead unpacks to a temporary uint32 buffer and then does a separate lookup loop. A blocked variant (fastrangeuncompress) decodes into a cache-sized buffer to avoid RAM round trips.

## Compared with alternatives

simdcomp, FastPFor and TurboPFor decode packed integers but leave the dictionary lookup to you; pick this when the end product is 64-bit dictionary values and you want the unpack and lookup fused in one pass, accepting a prototype. For a maintained bit-unpacking library in a real system, Apache ORC's AVX-512 RLE unpacking or simdcomp is the safer base.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (C++ standard library, x86 intrinsics) |
| **Minimum toolchain** | C++11; Makefile builds with -O3 -march=native; README results from GCC 5.3.0 |
| **Platforms** | x86-64 only: AVX2 required for the fast path, AVX-512F for the AVX-512 codec; scalar codec is portable C++ but uses __builtin_clz (GCC/Clang) |
| **Thread safety** | Codec objects hold a temporary buffer and are documented as not thread-safe (one instance per thread); the static fastuncompress/fastrangeuncompress functions keep no state. |
| **Drop-in for the baseline** | no |

## Gotchas

- dictionary_coded_t has a move constructor taking const&& that copies the raw dictionary/compressed_data pointers without nulling the source, so any real move (std::move, or a compiler that skips NRVO in compress()) leads to a double delete[]; the code relies on copy elision.
- bit_width is computed as 32 - __builtin_clz(dictionary_size), so power-of-two dictionaries (every size in the benchmark) use one more bit than needed (2 entries are packed at 2 bits), and an empty input calls __builtin_clz(0), which is undefined.
- The scalar (32-value blocks), AVX2 (256-value) and AVX-512 (512-value) codecs write different packed layouts; data compressed by one cannot be decoded by another.
- avxunpackdict, avxpack, avxunpack and the bpacking.h routines are non-inline, non-static functions defined in headers, so including the headers from two translation units gives multiple-definition link errors; the Makefile's test target covers only the scalar and AVX2 codecs (AVX-512 is exercised only by asserts inside the benchmark).

## Known shortcomings

- Baseline is the repo's own scalar decoder, not a listed codec. CPU given only as 'Skylake' and an unnamed Knights Landing, so not reproducible to the model. Last commit 2017-04-05; the repo now redirects to fast-pack/dictionary.
- dictionary_coded_t's move constructor (const&&) copies raw pointers without nulling the source, so a real move double-deletes (only NRVO avoids it). bit_width = 32-clz(size) wastes 1 bit at power-of-two sizes (every benchmark size); empty input calls clz(0), UB. No bounds check on indexes, so crafted input makes the gather read out of bounds. Header functions are not inline (multiple-definition link errors across TUs). Scalar, AVX2 and AVX-512 bitstream layouts are incompatible; the AVX-512 path has no unit test. Timings are rdtsc ticks, best of 5.

## Caveats and trade-offs

Baseline is the authors' own scalar decoder (scalarcodec), not a widely used external incumbent, so baseline_in_list is false. The gain shrinks as the dictionary outgrows cache: Skylake size 65536 scalar 7.14 vs AVX2 fast 5.18 cycles per value, size 1048576 11.85 vs 8.47; the AVX2 path stays faster at every listed size (the earlier note that it was slower at size 8192 was a misreading: size 8192 is 4.35 vs 2.28). README states the code is a demo not meant for production, uses its own format, assumes 64-bit dictionary words, uniform value distribution, and large arrays, and measures steady-state throughput only. 2016 results on gcc 5.3.0, CPU model not exact. Not rerun by anyone independent. The repo now redirects to github.com/fast-pack/dictionary.

Needs AVX2 (gather) or AVX-512; dictionary values are hard-coded to 64-bit words; research prototype, not a packaged library. The scalar baseline is the repo's own decoder, not FastPFor, simdcomp or Simple8b.

## Maintenance

Abandoned since April 2017 (25 commits, no issues filed) but Apache-2.0 and header-only; treat it as a reference kernel to copy and harden, not a dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** README prints first-party decodebenchmark output (benchmarks/decodebenchmark.cpp) for scalarcodec vs AVXDictCODEC/AVX512DictCODEC with gcc 5.3.0 and Makefile flags -O3 -march=native, but hardware is only 'Skylake' and an 'UNKNOWN' Knights Landing with no CPU model, so it falls short of A; baseline is the authors' own scalar decoder.
- **Verifier notes:** All claimed numbers match the README tables (Skylake size 2: 4.00 vs 1.91; size 4096: 4.14 vs 2.12; size 1048576: 11.85 vs 8.47; KNL size 2: 7.75 / 3.22 / 1.48). The record's caveat about size 8192 being slower for AVX2 was wrong and is corrected; 6.44 is the size-524288 figure. Repo moved to fast-pack/dictionary (github.com/lemire/dictionary redirects); 112 stars, Apache-2.0, last commit 2017-04-05.
- **Fields the verifier corrected:** `caveats`, `compiler_and_flags`
- **Shortcomings recorded by:** first-party benchmark
- **Pages the verifier opened:**
  - <https://github.com/lemire/dictionary>
  - <https://github.com/lemire/dictionary/commits>
  - <https://raw.githubusercontent.com/lemire/dictionary/HEAD/README.md>
  - <https://raw.githubusercontent.com/lemire/dictionary/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/lemire/dictionary/HEAD/Makefile>
- **Sources the enricher read:**
  - <https://github.com/fast-pack/dictionary>
  - <https://github.com/fast-pack/dictionary/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/fast-pack/dictionary/HEAD/README.md>
  - <https://raw.githubusercontent.com/fast-pack/dictionary/HEAD/Makefile>
  - <https://raw.githubusercontent.com/fast-pack/dictionary/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/fast-pack/dictionary/HEAD/src/dict.h>
  - <https://raw.githubusercontent.com/fast-pack/dictionary/HEAD/src/scalarcodec.h>
  - <https://raw.githubusercontent.com/fast-pack/dictionary/HEAD/src/avxcodec.h>
  - <https://raw.githubusercontent.com/fast-pack/dictionary/HEAD/src/avxdict.h>
  - <https://raw.githubusercontent.com/fast-pack/dictionary/HEAD/src/avx512codec.h>
  - <https://raw.githubusercontent.com/fast-pack/dictionary/HEAD/src/avx512dict.h>
  - <https://raw.githubusercontent.com/fast-pack/dictionary/HEAD/src/avxbpacking.h>
  - <https://raw.githubusercontent.com/fast-pack/dictionary/HEAD/src/bpacking.h>
  - <https://raw.githubusercontent.com/fast-pack/dictionary/HEAD/benchmarks/decodebenchmark.cpp>
  - <https://raw.githubusercontent.com/fast-pack/dictionary/HEAD/benchmarks/benchmark.h>
  - <https://raw.githubusercontent.com/fast-pack/dictionary/HEAD/tests/avxtest.cpp>
  - <https://raw.githubusercontent.com/fast-pack/dictionary/HEAD/tests/scalartest.cpp>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/lemire/dictionary`) · [data/wave9/enrich/raw/github_com_lemire_dictionary.json](../../../data/wave9/enrich/raw/github_com_lemire_dictionary.json) (enrichment confidence 0.8)

</details>
