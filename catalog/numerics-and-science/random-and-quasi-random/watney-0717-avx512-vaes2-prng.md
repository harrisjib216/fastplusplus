# AVX512-VAES2-PRNG (AVX-512/VAES/GFNI 8-way hybrid PRNG, proof of concept)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Random and quasi-random numbers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C/C++ (header AVX512-VAES2-PRNG.h)` · `MIT` · 🟢 active

> Single-header AVX-512/VAES/GFNI bulk PRNG proof of concept; author claims 0.093 cycles/byte versus about 4-6 for mt19937.

| | |
|---|---|
| **Beats** | Mersenne Twister (mt19937), PCG32 / XorShift128+, ChaCha8 and ChaCha20 AVX-512 (rows in the README table) |
| **Claimed result** | This implementation 0.0932 cpb (5.964 cycles per 64-byte output; best about 0.093) versus table rows ChaCha8 AVX-512 about 0.08-0.18 cpb, VAES about 0.16-0.20, ChaCha20 about 0.35-0.50, PCG32/XorShift128+ about 0.60-1.00, mt19937 about 4.00-6.00 cpb: roughly 43-64x versus mt19937 and 6-11x versus PCG32/XorShift128+ (derived from page data). |
| **Workload** | Cycles per byte of bulk output on an AMD EPYC machine with AVX-512, VAES and GFNI, generating 64-byte outputs from an 8-way pipeline with non-temporal stores. |
| **Metric** | throughput |
| **Hardware** | AMD EPYC (model not stated) with AVX-512, VAES and GFNI, shared server environment |
| **Adoption** | 0 stars |
| **Last commit** | 2026-09-15 |
| **Links** | [repository](https://github.com/Watney-0717/AVX512-VAES2-PRNG) · [benchmark](https://raw.githubusercontent.com/Watney-0717/AVX512-VAES2-PRNG/HEAD/README.md) |

## Verdict

The author's README reports 0.0932 cycles per byte (5.964 cycles per 64 bytes) for bulk output with non-temporal stores on an unnamed AMD EPYC with AVX-512/VAES/GFNI in a shared server environment, with no compiler, flags or harness published. The 43-64x figure against mt19937 compares that to an unmeasured 4-6 cpb range listed in the same table, and against PCG32/XorShift128+ the derived gap is 6-11x.

## Use it when

- Experiments and benchmarking on AVX-512 + VAES + GFNI hardware (the README names AMD Zen 4/Zen 5 and Intel Sapphire Rapids/Emerald Rapids as targets) where you want a very high-throughput bulk random stream
- Filling large buffers (many 512-byte blocks) that are not read back immediately, so the non-temporal stores help rather than hurt
- Non-cryptographic simulation or noise generation where you can validate the output quality yourself before relying on it

## Skip it when

- Anything security-sensitive: the author states it is not a proven CSPRNG, and its mixing is only two AES rounds per block; use ChaCha or AES-CTR based generators instead
- Production simulations that need well-tested statistical quality: the README shows only TestU01 SmallCrush and 0.962 GiB of PractRand plus home-grown statistics, and the state transition is not a bijection (see gotchas), so the period is unproven
- CPUs without all of AVX-512F, GFNI and VAES, and any non-x86 target: the header has no fallback path
- Small or immediately consumed outputs: generation is in 512-byte blocks with non-temporal stores, which evict the data from cache just before you read it
- C++ projects without a shim: the header uses the C99 'restrict' keyword and GCC attributes, so it needs '#define restrict __restrict' under g++/clang++ and does not build with MSVC as written

## How it is fast

The state is just two 512-bit vectors (a, b). Each block adds Weyl constants, applies a GFNI affine byte transform to a and a VPSHUFB nibble lookup combined with VPTERNLOGD to b, and expands the two vectors into eight via rotations and complements. The eight vectors then go through two VAESENC rounds with seed-derived round keys and a cross-vector rotate-XOR 'diagonal' between the rounds. The eight 64-byte vectors are written with non-temporal stores (_mm512_stream_si512), and a small add/rotate/XOR remix is placed between the sixth and seventh store. There are no multiplications in the generation loop, and eight independent vectors keep the VAES and store ports busy.

## Compared with alternatives

Rarely. SHISHUA (52.93 GB/s per its catalog record), testingRNG's aesctr and Google's Randen cover the same bulk-throughput niche with more scrutiny and without an AVX-512+VAES+GFNI requirement. Pick this one only to experiment with VAES/GFNI-based generator design on Zen 4+ or recent Xeon hardware.

## Integration

| | |
|---|---|
| **Form** | header-only (single C header) |
| **Dependencies** | none (immintrin.h; sys/mman.h or windows.h for the optional lock helpers) |
| **Minimum toolchain** | C99 compiler with AVX-512F/GFNI/VAES intrinsics and GCC-style __attribute__ and inline asm (GCC or Clang with -mavx512f -mgfni -mvaes or a suitable -march); exact versions not documented |
| **Platforms** | x86-64 only, requires AVX-512F + GFNI + VAES (the README tested an unnamed AMD EPYC in a shared server environment) |
| **Thread safety** | not documented; the state is a caller-owned struct with no globals, so one state per thread works |
| **Drop-in for the baseline** | no |

## Gotchas

- Output buffer must be 64-byte aligned and sized in 512-byte blocks (128 uint32 words per block): _mm512_stream_si512 faults on unaligned addresses, and the README does not mention this.
- The 'VPSHUFB + VPTERNLOGD' step uses ternlog immediate 0xFE, a three-input OR of two nibble-substituted values and the input. Computing it from the header's LUTs gives only 56 distinct outputs for the 256 byte inputs, with 77% one-bits. The b-lane update is therefore many-to-one and the output vectors 4-7 start from that biased value (v[7] is its bitwise complement), so the generator has no period guarantee and rests on two AES rounds to hide the bias.
- Seeding takes a 32-byte key that the comment says must already be uniformly distributed ('KDF boundary'). Passing a small integer padded with zeros is not supported by the design.
- The README speed table mixes this generator's measured 0.0932 cpb with approximate '\~' ranges for ChaCha8, VAES, PCG32/XorShift128+ and mt19937 that do not appear to come from the same run, and no harness, compiler or flags are published. By its own table, AVX-512 ChaCha8 (\~0.08-0.18 cpb) is in the same range.

## Known shortcomings

- Baseline rows are unmeasured ranges and there is no harness; proof of concept.
- Quality flaw: the 'VPSHUFB+VPTERNLOGD' step is ternlog 0xFE, a 3-input OR; from the header LUTs 256 byte inputs give only 56 outputs with 77% one-bits, so the b-lane update is many-to-one with no period guarantee, and output vectors 4-7 start from a biased value (v[7] = \~v[4]) hidden only by 2 AES rounds. Proof of concept. NT stores need an undocumented 64-byte-aligned buffer; C99 restrict blocks g++/MSVC builds without a shim; seed must be a pre-derived uniform 256-bit key.

## Caveats and trade-offs

Baseline rows are approximate ranges, not shown as measured in the same run. The repo has no benchmark source (only AVX512-VAES2-PRNG.h, README.md, LICENSE and throughput_chart.png, whose bars omit mt19937), and no CPU model, compiler or flags are given. The 43-64x figure versus mt19937 rests on an unmeasured 4-6 cpb range that looks pessimistic for a modern compiled mt19937. By the page's own table, ChaCha8 with AVX-512 (\~0.08-0.18 cpb, 'equivalent to the fastest range') matches or beats it, so the clear win is only over scalar non-cryptographic PRNGs. The README mentions 6.04 cycles per output in its prose and 5.964 in the table. Statistical testing is thin: home-grown 'SmallCrush/PractRand equivalent' statistics, plus a claimed TestU01 SmallCrush pass and 0.962 GiB of PractRand. It is not a vetted CSPRNG (the author invites cryptanalysis), needs AVX-512 + VAES + GFNI, and the repo was created on 2026-09-15 with 0 stars. Keep as a flagged proof-of-concept.

Needs AVX-512 plus VAES and GFNI (recent Intel server or AMD Zen 4+ cores); outputs 64 bytes at a time; the author states it is not proven as a CSPRNG; the code is a single header.

## Maintenance

A 0-star repo created on 2026-09-15 (all 11 commits that day), self-described as a preliminary proof of concept under a codename. MIT-licensed and small enough to vendor, but treat it as experimental.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README table gives this implementation's own 0.0932 cpb (5.964 cycles per 64-byte output) on an unnamed AMD EPYC. The baseline rows (ChaCha8/ChaCha20 AVX-512, VAES, PCG32/XorShift128+, mt19937) are approximate '\~' ranges with no sign they were measured in the same run. The repo holds only the header, README, LICENSE and a chart: no benchmark harness, compiler or flags. First-party, no methodology, so C, with the &gt;50x gap versus mt19937 also forcing the cap.
- **Verifier notes:** README numbers match the record. All 11 commits are dated 2026-09-15, so last_commit and active status are right. Nothing to measure the baseline ranges against.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/Watney-0717/AVX512-VAES2-PRNG/HEAD/README.md>
  - <https://raw.githubusercontent.com/Watney-0717/AVX512-VAES2-PRNG/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/Watney-0717/AVX512-VAES2-PRNG/HEAD/AVX512-VAES2-PRNG.h>
  - <https://raw.githubusercontent.com/Watney-0717/AVX512-VAES2-PRNG/HEAD/throughput_chart.png>
  - <https://github.com/Watney-0717/AVX512-VAES2-PRNG>
  - <https://github.com/Watney-0717/AVX512-VAES2-PRNG/commits/main>
- **Sources the enricher read:**
  - <https://github.com/Watney-0717/AVX512-VAES2-PRNG>
  - <https://github.com/Watney-0717/AVX512-VAES2-PRNG/commits/main>
  - <https://raw.githubusercontent.com/Watney-0717/AVX512-VAES2-PRNG/HEAD/README.md>
  - <https://raw.githubusercontent.com/Watney-0717/AVX512-VAES2-PRNG/HEAD/AVX512-VAES2-PRNG.h>
  - <https://raw.githubusercontent.com/Watney-0717/AVX512-VAES2-PRNG/HEAD/LICENSE>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/watney-0717/avx512-vaes2-prng`) · [data/wave8/enrich/raw/github_com_watney_0717_avx512_vaes2_prng.json](../../../data/wave8/enrich/raw/github_com_watney_0717_avx512_vaes2_prng.json) (enrichment confidence 0.65)

</details>
