# kalcutter/bitshuffle

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Integer compression and bit-packing](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `Apache-2.0 OR MIT` · 🟡 stale

> C99 rewrite of the Bitshuffle bit-transpose filter with SSE2/AVX2/AVX-512/GFNI kernels; claims 1.3x-10x over classic bitshuffle.

| | |
|---|---|
| **Beats** | kiyo-masui/bitshuffle reference implementation (bshuf_trans_bit_elem / bshuf_untrans_bit_elem) |
| **Claimed result** | typical speedup between 1.3x and 10x depending on CPU architecture, function, and arguments |
| **Workload** | Bit-transpose (Bitshuffle) of typed data blocks, encode and decode, used as a pre-filter for compression; not a bit-width packer. |
| **Metric** | throughput |
| **Adoption** | 7 stars, 4 forks |
| **Last commit** | 2024-01-22 |
| **Links** | [repository](https://github.com/kalcutter/bitshuffle) · [benchmark](https://github.com/kalcutter/bitshuffle) |

## Verdict

The README claims a 1.3x to 10x speedup over classic bitshuffle 0.5.1's bshuf_trans_bit_elem/bshuf_untrans_bit_elem depending on CPU, function and arguments. The Google Benchmark harness (elem_size 1-18 and 63-66, blocks of 256 B to 256 MB, memcpy as reference) is public and CI runs it on self-hosted Ice Lake and arm64 machines at -O3 with GCC and Clang, but no result tables, CPU models or per-case numbers are published.

## Use it when

- You already bitshuffle typed numeric arrays (float32/float64/int16 sensor, image or simulation data) before LZ4/Zstd and the transpose shows up in profiles.
- x86-64 Linux with GCC 8+ or Clang 8+ servers, where IFUNC dispatch picks AVX2, AVX-512BW or AVX-512VBMI+GFNI (Ice Lake, Zen 4/5) at run time from one build.
- Hot loops over many small blocks (the benchmark covers 256 B to 16 KB), where avoiding the classic library's per-call malloc matters.
- You need a tiny dependency: one .c and one .h file, C89/C++-compatible header, dual MIT/Apache-2.0, easy to vendor.

## Skip it when

- aarch64/ARM: there is no NEON kernel, so non-x86 targets get the portable scalar Hacker's Delight transpose8, while classic bitshuffle 0.5.1 has a NEON path; it may be slower there (not documented, and CI runs the arm64 benchmark but publishes no numbers).
- Big-endian targets: the build stops with #error, and support is not planned.
- You need the full Bitshuffle format (blocked framing, built-in LZ4/Zstd, HDF5 filter 32008, Python bindings): use kiyo-masui/bitshuffle, c-blosc2 or hdf5plugin instead.
- You want maintained, widely used code: 5 commits, last one 2024-01-22, 7 stars, and no release tags.
- Integer bit-width packing (FOR, varint, PFor) is the actual need: this is a compression pre-filter, not a bit packer.

## How it is fast

Encode is a byte transpose (element bytes into byte planes, with specialised kernels for 2, 4 and 8 byte elements) followed by an 8x8 bit-matrix transpose on each plane; decode runs the same steps in reverse. The bit transpose uses movemask-style SIMD kernels for SSE2, AVX2 and AVX-512BW, plus an AVX-512VBMI+GFNI kernel that does the 8x8 bit transpose with a GF(2) affine instruction (vgf2p8affineqb) after a VBMI byte permute. Kernels are picked at load time with GNU IFUNC resolvers (__builtin_cpu_supports), so one binary uses the best ISA. The library never allocates; the classic implementation mallocs a temporary buffer of the full block size on every call, which also accounts for part of the measured gain on small blocks.

## Compared with alternatives

None of the integer-packing siblings (FastPFor, simdcomp, TurboPFor, Stream VByte) do bit transposition of arbitrary-width typed data. Pick this when you want a Bitshuffle pre-filter for float/int arrays ahead of a general compressor. Pick Sprintz or TurboPFor when you want a complete integer/time-series codec.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (Google Benchmark and GoogleTest only for the Bazel test and benchmark targets; the benchmark also pulls classic bitshuffle 0.5.1) |
| **Minimum toolchain** | C99 compiler; IFUNC dispatch is on for GCC 8+ or Clang 8+ with the ifunc/target attributes and off for ICC and MSVC. CI covers GCC, Clang (libstdc++ and libc++) and MSVC 2019/2022. Build files are Bazel only (WORKSPACE, no CMake). |
| **Platforms** | Little-endian only. x86/x86-64 with SSE2, AVX2, AVX-512BW+VL and AVX-512VBMI+VL+GFNI kernels; other architectures (arm64 is tested in CI) fall back to scalar C. Linux, macOS and Windows are tested; without IFUNC (MSVC, macOS) the ISA is fixed at compile time by -m/arch flags. |
| **Thread safety** | not documented; the functions keep no global state apart from IFUNC resolvers that run at load time, so concurrent calls with separate buffers look safe on reading the source |
| **Drop-in for the baseline** | partial: output is bit-identical to bshuf_trans_bit_elem/bshuf_untrans_bit_elem, but the signature differs (out first, explicit scratch buffer, int return) and there is no blocked bshuf_bitshuffle/compress wrapper |

## Gotchas

- Without IFUNC (MSVC, macOS, ICC, or BITSHUF_USE_IFUNC=0) the SIMD level is fixed by compiler flags; a default x86-64 build without -mavx2 or /arch:AVX2 uses only SSE2.
- elem_size &gt; 1 needs a scratch buffer of size\*elem_size bytes, or the call returns -1. Buffers are restrict, so overlapping out/in/scratch is undefined behaviour. size\*elem_size is not checked for overflow.
- The encode resolver skips the AVX-512VBMI+GFNI kernel on Intel CPUs (it checks !__builtin_cpu_is("intel")) and uses AVX-512BW there, but the decode resolver does not; this tuning choice is not explained.
- Benchmark fairness: the classic library in tests/bitshuffle_benchmark.cc is built with the same global copts, so it picks its ISA at compile time (AVX512/AVX2/SSE2/NEON macros), while this library dispatches at run time. A default -c opt build therefore compares AVX-512 or AVX2 kernels here with classic SSE2; also, classic allocates per call.

## Known shortcomings

- Tier C: tests/bitshuffle_benchmark.cc exists (the record said no bench code) but no CPU, compiler or flags are stated; 1.3x-10x vs kiyo-masui/bitshuffle, an off-list baseline, and it is a bit transpose rather than bit packing. License Apache-2.0 OR MIT.
- No published numbers. Baseline caveats: classic bitshuffle 0.5.1 picks its ISA at compile time while this library dispatches at run time via IFUNC, so a default build compares AVX-512/AVX2 here with classic SSE2; classic also mallocs a full-block temp buffer on every call. No NEON kernel (arm64 gets scalar; classic has NEON). The encode resolver skips the GFNI kernel on Intel while decode does not. Bazel only; 5 commits.

## Caveats and trade-offs

The README gives a single range (1.3x to 10x) with no per-CPU table, no compiler flags and no CPU model. The benchmark harness does exist: tests/bitshuffle_benchmark.cc runs bitshuf_encode_block/bitshuf_decode_block against the classic bshuf_trans_bit_elem/bshuf_untrans_bit_elem for element sizes 1-18 and 63-66 and block sizes from 256 B to 256 MB, plus a memcpy reference. It uses SSE2/AVX2/AVX-512 with runtime dispatch that needs GNU IFUNC, and it is little-endian only. The library is adjacent to rather than inside integer bit-packing (bit transposition of typed arrays used as a compression pre-filter), so the category fit may be wrong. The baseline is another bitshuffle implementation, not varint, Simple8b or FastPFor. The license is dual Apache-2.0 OR MIT (LICENSE-APACHE and LICENSE-MIT both present).

Only the core transpose is provided (no HDF5/Python filter, no compression). Little-endian only. Runtime CPU dispatch needs GNU IFUNC. Block size must be a multiple of 8 elements. Header is usable from C and C++.

## Maintenance

Stale since 2024-01-22 (5 commits, no releases), but it is a dual MIT/Apache-2.0 single-file C99 library with thorough CI (ASan/UBSan across SSE2-to-GFNI builds, MSVC, macOS, arm64) and exhaustive one-bit round-trip tests, so it is low-risk to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The README says that, compared with bshuf_trans_bit_elem/bshuf_untrans_bit_elem from the classic implementation, 'this code yields a typical speedup between 1.3x and 10x'. The benchmark code is public (tests/bitshuffle_benchmark.cc, Google Benchmark against the classic kiyo-masui functions, built via BUILD.bazel), but no results table, CPU model, compiler or flags are given, so it is first-party with partial methodology: C.
- **Verifier notes:** The claim matches the README. The record wrongly said there was no benchmark code: it is tests/bitshuffle_benchmark.cc. The license files are LICENSE-APACHE and LICENSE-MIT, which is why a plain LICENSE path returned 404. Last commit is 2024-01-22 (stale), 5 commits, and the repo is neither archived nor a fork.
- **Fields the verifier corrected:** `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier; no numbers; CI runs ASan/UBSan over SSE2-to-GFNI builds plus exhaustive one-bit round-trip tests
- **Pages the verifier opened:**
  - <https://github.com/kalcutter/bitshuffle>
  - <https://raw.githubusercontent.com/kalcutter/bitshuffle/HEAD/README.md>
  - <https://github.com/kalcutter/bitshuffle/commits/main>
  - <https://github.com/kalcutter/bitshuffle/tree/main/tests>
  - <https://raw.githubusercontent.com/kalcutter/bitshuffle/HEAD/tests/bitshuffle_benchmark.cc>
  - <https://raw.githubusercontent.com/kalcutter/bitshuffle/HEAD/BUILD.bazel>
  - <https://raw.githubusercontent.com/kalcutter/bitshuffle/HEAD/LICENSE-APACHE>
  - <https://raw.githubusercontent.com/kalcutter/bitshuffle/HEAD/LICENSE-MIT>
- **Sources the enricher read:**
  - <https://github.com/kalcutter/bitshuffle>
  - <https://github.com/kalcutter/bitshuffle/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/kalcutter/bitshuffle/HEAD/README.md>
  - <https://raw.githubusercontent.com/kalcutter/bitshuffle/HEAD/src/bitshuffle.c>
  - <https://raw.githubusercontent.com/kalcutter/bitshuffle/HEAD/src/bitshuffle.h>
  - <https://raw.githubusercontent.com/kalcutter/bitshuffle/HEAD/tests/bitshuffle_benchmark.cc>
  - <https://raw.githubusercontent.com/kalcutter/bitshuffle/HEAD/tests/bitshuffle_test.cc>
  - <https://raw.githubusercontent.com/kalcutter/bitshuffle/HEAD/BUILD.bazel>
  - <https://raw.githubusercontent.com/kalcutter/bitshuffle/HEAD/WORKSPACE>
  - <https://raw.githubusercontent.com/kalcutter/bitshuffle/HEAD/.bazelrc>
  - <https://raw.githubusercontent.com/kalcutter/bitshuffle/HEAD/third_party/bitshuffle.BUILD>
  - <https://raw.githubusercontent.com/kalcutter/bitshuffle/HEAD/.github/workflows/main.yml>
  - <https://raw.githubusercontent.com/kiyo-masui/bitshuffle/0.5.1/src/bitshuffle_core.c>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/kalcutter/bitshuffle`) · [data/wave9/enrich/raw/github_com_kalcutter_bitshuffle.json](../../../data/wave9/enrich/raw/github_com_kalcutter_bitshuffle.json) (enrichment confidence 0.8)

</details>
