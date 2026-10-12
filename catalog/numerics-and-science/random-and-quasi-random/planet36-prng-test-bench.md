# prng-test-bench (aes_ctr_128 and clmulrand PRNG headers)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Random and quasi-random numbers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MPL-2.0` · 🟢 active

> Header PRNGs from an x86 test bench: 3-round AES counter and carry-less-multiply generators, about 4x std::mt19937 per call.

| | |
|---|---|
| **Beats** | std::mt19937 (also std::mt19937_64, pcg64, xoshiro256\*\*, wyrand in the same table) |
| **Claimed result** | Results file prng-next-benchmark.txt (per-thread GiB/s, 7 threads, median of 5): aes_ctr_128 37.22, aes_compress_ctr2_128 28.60, clmulrand 21.03, wyrand 16.88, xoshiro256starstar 8.53, xoshiro256plusplus 8.10, std::mt19937_64 5.24, pcg64 5.17, std::mt19937 4.67, pcg32 3.73, std::philox4x32 3.56. aes_ctr_128 vs std::mt19937 is about 8.0x in GiB/s, but aes_ctr_128 returns a 128-bit value per call and mt19937 a 32-bit one, so calls per second differ by about 2.0x (derived from page data and header). clmulrand returns uint64_t: about 4.5x mt19937 in GiB/s, about 2.25x per call vs std::mt19937 and about 4.0x per call vs std::mt19937_64 (derived from page data and header). |
| **Workload** | Google Benchmark loop calling next() once per iteration on a randomly seeded generator, 7 threads, per-thread average, 5 repetitions, reported as GiB/s of generator output. |
| **Metric** | throughput |
| **Hardware** | CPU model not stated in results/prng-next-benchmark.json: host arch-vm (a VM), 8 CPUs at 2419 MHz, L1D 32 KiB, L1I 64 KiB, L2 4 MiB, L3 36 MiB, run dated 2026-09-18. The PractRand summaries built from the same Makefile record -march=raptorlake, so the host is a Raptor Lake part (the author's randp page names an i9-13980HX), but the L1/L2 sizes look like the E-core clusters, not P-cores, so the exact core type is unconfirmed. |
| **Compiler and flags** | Makefile defaults: g++ -std=c++26 -O3 -flto=auto -march=native with Google Benchmark 1.9.5 (release build); g++ version not recorded in the results. |
| **Adoption** | 2 stars, 743 commits |
| **Last commit** | 2026-10-02 |
| **Links** | [repository](https://github.com/planet36/prng-test-bench) · [benchmark](https://raw.githubusercontent.com/planet36/prng-test-bench/HEAD/results/prng-next-benchmark.txt) |

## Verdict

One author-run Google Benchmark pass (2026-09-18, 7 threads on an 8-vCPU VM named arch-vm, likely a Raptor Lake host; g++ -O3 -flto=auto -march=native; median of 5) gives per-thread GiB/s of 37.22 for aes_ctr_128, 21.03 for clmulrand, 4.67 for std::mt19937 and 5.24 for std::mt19937_64. Corrected for std::mt19937's 8-byte result type, that is about 2.50 and 2.82 billion calls/s against 0.63 billion: about 4.0x and 4.5x per call, about 3.5x and 4.0x against std::mt19937_64 (derived from page data). These are first-party numbers on an unnamed CPU.

## Use it when

- Monte Carlo, simulation or randomized algorithms on x86-64 built with g++, where std::mt19937 or std::mt19937_64 shows up in profiles.
- Callers that can consume 128 bits per call (two doubles, or two 64-bit draws) and want the most bits per call: aes_ctr_128 needs AES-NI.
- 64-bit draws one at a time with a 16-byte state: clmulrand needs PCLMULQDQ and SSE4.1.
- One generator object per thread: the state is small (aes_ctr_128 32 bytes, clmulrand 16 bytes per the repo's prng-dump info table), so per-thread instances are cheap.

## Skip it when

- Anything that needs unpredictability (keys, tokens, nonces): aes_ctr_128 is 3 AES rounds with a fixed key on a Weyl counter, not AES-128-CTR, and clmulrand is a non-cryptographic mixer.
- clang++ or MSVC builds (README: clang++ is not supported), or non-x86 targets: the headers use x86 intrinsics and compile only when __AES__ or __PCLMUL__ is defined.
- Code that needs RandomNumberEngine features: seed(), discard/jump-ahead, operator==, stream I/O, or a fixed default-constructed sequence (urbg_base_class.hpp says it does not meet those requirements).
- Platforms without arc4random_buf and explicit_bzero (the base class calls both: default seeding and zeroing in the destructor), e.g. older glibc or Windows.
- Projects that want a packaged, versioned library: these are headers inside a test-bench repo with 2 stars, no releases and frequent commits.

## How it is fast

Both are counter-based: the state is a pair of 64-bit Weyl counters advanced with one _mm_add_epi64 per call, so there is no long dependency chain like the 624-word Mersenne Twister state. aes_ctr_128 mixes the counter with three _mm_aesenc_si128 rounds under one per-generator key and returns all 128 bits. clmulrand does one PCLMULQDQ of the counter's two lanes against each other and returns the high minus the low 64-bit half. Both are a handful of instructions with no branches or table lookups.

## Compared with alternatives

Pick aes_ctr_128 or clmulrand when you want a per-call std-compatible generator object on x86-64 with g++. lemire/testingRNG's aesctr and andanteyk's Culumi are the closest AES- and CLMUL-based relatives with their own timings. SHISHUA is the better fit when you fill large buffers in bulk. For unpredictable output use randp, an AES-CTR pool by the same author, not these.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none external; each header pulls sibling headers from include/ (urbg_base_class.hpp, wyprimes.hpp, plus mm_cast.hpp, simd_types.hpp and sha2_iv.h for aes_ctr_128, and clmum.hpp and mum.hpp for clmulrand); the benchmark itself needs Google Benchmark |
| **Minimum toolchain** | g++ only; the Makefile builds with -std=c++26 (the base class uses C++20 concepts); the lowest working GCC version is not documented |
| **Platforms** | x86-64 little-endian (simd_types.hpp static_asserts it) with SSE4.1 plus AES-NI and __int128 (aes_ctr_128) or PCLMULQDQ (clmulrand); a libc that provides arc4random_buf and explicit_bzero (glibc 2.36+ or BSD) |
| **Thread safety** | Not documented; each object mutates its own state without synchronization, so use one instance per thread (as the benchmark does). |
| **Drop-in for the baseline** | partial: usable wherever a std::uniform_random_bit_generator is accepted (std distributions, std::shuffle), but the seeding interface differs from std::mt19937 (no 32-bit seed or seed_seq constructor, no seed(), discard() or operator==), and aes_ctr_128's result_type is __uint128_t rather than a 32-bit value |

## Gotchas

- The benchmark's std::mt19937 baseline is skewed by type width. The repo's own prng-dump info table lists std::mt19937 (and std::philox4x32, minstd_rand) with a 64-bit result type (uint_fast32_t) and max 4294967295. So bytes_per_second credits mt19937 with 8 bytes per call, and prng-dump writes 32 zero bits per word into PractRand. Per call, aes_ctr_128 is about 4.0x and clmulrand about 4.5x std::mt19937 (derived from page data), not the 2.0x and 2.25x in the record. The 256 MB PractRand 'failures' of std::mt19937 and std::philox4x32 are harness artifacts, not properties of those engines.
- Results/prng-next-benchmark.json shows that wyrand, clmulrand and aes_ctr_128 all take 0.38 to 0.48 ns real time per call, inside a loop that stores every result to a volatile. Their GiB/s ranking is mostly output width (128 vs 64 bits), not per-call speed (derived from page data).
- aes_ctr_128 needs the key's two 64-bit lanes to differ: with equal lanes, swapping the counter lanes swaps the output lanes. init() has forced this (xor with SHA-512 IV words) only since the 2026-09-20 commits, two days after the published 2026-09-18 benchmark run; that change touches seeding, not next().
- Copying a generator duplicates its stream (copy constructors are defaulted), and default construction makes a syscall-backed arc4random_buf call, so construct per thread or task, not per draw.

## Known shortcomings

- aes_ctr_128 is 3 aesenc rounds with one key, so not cryptographic. CPU unnamed, ran in a VM, no compiler version. The 8x is in GiB/s; per call \~2x vs mt19937 (derived from page data). PractRand passes 256 MB on current code; the 512 GB run used older code.
- A harness bug skews the std::mt19937 baseline: the repo's own prng-dump info table shows std::mt19937, std::philox4x32 and minstd with a 64-bit result_type (uint_fast32_t, max 4294967295), so bytes_per_second credits mt19937 with 8 bytes per call and the PractRand dumps carry 32 zero bits per word. Per call, aes_ctr_128 is about 4.0x and clmulrand about 4.5x std::mt19937 (the record's 2.0x and 2.25x are per byte of inflated output), and the 'std::mt19937 fails PractRand at 256 MB' caveat is a harness artifact (std::philox4x32 too). The aes_ctr_128 key-lane fix landed 2026-09-20, after the 2026-09-18 run (init only). The top three generators all run 0.38-0.48 ns/call, so the GiB/s ranking mostly reflects output width.

## Caveats and trade-offs

Author-run, first-party numbers on an unnamed CPU inside a VM, so tier C. GiB/s favours generators with wide outputs (aes_ctr_128 returns 128 bits per call vs 32 for mt19937), so per-call gains are about 2x, not 8x. aes_ctr_128 is not AES-128-CTR: include/aes_ctr_128.hpp applies 3 _mm_aesenc_si128 rounds with one key to a Weyl-sequence counter, so it is a fast non-cryptographic generator and must not be used where unpredictability matters. The README does not itself claim to beat mt19937; the comparison is read from the results table. Statistical quality: aes_ctr_128 and clmulrand pass PractRand to 256 MB with all four seed types (results/prng-results.tlmax-256MB.summary.txt, GCC 16.2.1); clmulrand and an older 'aes128_ctr_128' pass to 512 GB in results/prng-results.tlmax-512GB.summary.txt, but that run predates the current code (GCC 15.2.1 build), while std::mt19937 fails at 256 MB. No LICENSE file; MPL-2.0 comes from SPDX headers in source files. Very active (several commits a week), so numbers change between runs.

AES-based generators need AES-NI (and __int128) and g++ (clang++ unsupported per README). The headers expose each generator as a std::uniform_random_bit_generator. aes_ctr_128 runs only 3 AES rounds and is not claimed to be a CSPRNG. The same table includes many other generators (romu, sfc64, wyrand, squares, biski64) that may be separately catalogued.

## Maintenance

Very actively maintained (743 commits; the last on 2026-10-02 is a formatting change) and MPL-2.0 per SPDX headers (there is no LICENSE file), so copying a header means keeping its MPL file-level notice; expect numbers to move between runs.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** results/prng-next-benchmark.txt lists the claimed GiB/s figures for aes_ctr_128, clmulrand and std::mt19937 from the public prng-next-benchmark.cpp, but the results JSON names no CPU model (8 CPUs at 2419 MHz on host arch-vm) and no compiler version, so it is first-party with partial methodology, not A.
- **Verifier notes:** Numbers match the results file exactly; the GiB/s headline overstates the per-call gain, already flagged by the search agent. The record's 'repo is two weeks old' was dropped: the repo has 743 commits and a PractRand summary built with GCC 15.2.1 (2025), so its history is older, though I could not see the creation date.
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/planet36/prng-test-bench/HEAD/results/prng-next-benchmark.txt>
  - <https://raw.githubusercontent.com/planet36/prng-test-bench/HEAD/results/prng-next-benchmark.json>
  - <https://raw.githubusercontent.com/planet36/prng-test-bench/HEAD/README.md>
  - <https://raw.githubusercontent.com/planet36/prng-test-bench/HEAD/Makefile>
  - <https://raw.githubusercontent.com/planet36/prng-test-bench/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/planet36/prng-test-bench/HEAD/include/aes_ctr_128.hpp>
  - <https://raw.githubusercontent.com/planet36/prng-test-bench/HEAD/include/clmulrand.hpp>
  - <https://raw.githubusercontent.com/planet36/prng-test-bench/HEAD/prng-next-benchmark.cpp>
  - <https://raw.githubusercontent.com/planet36/prng-test-bench/HEAD/run-benchmarks.bash>
  - <https://raw.githubusercontent.com/planet36/prng-test-bench/HEAD/results/prng-results.tlmax-512GB.summary.txt>
  - <https://raw.githubusercontent.com/planet36/prng-test-bench/HEAD/results/prng-results.tlmax-256MB.summary.txt>
  - <https://github.com/planet36/prng-test-bench>
  - <https://github.com/planet36/prng-test-bench/commits>
- **Sources the enricher read:**
  - <https://github.com/planet36/prng-test-bench>
  - <https://github.com/planet36/prng-test-bench/issues?q=is%3Aissue>
  - <https://github.com/planet36/prng-test-bench/commits/main>
  - <https://raw.githubusercontent.com/planet36/prng-test-bench/HEAD/README.md>
  - <https://raw.githubusercontent.com/planet36/prng-test-bench/HEAD/Makefile>
  - <https://raw.githubusercontent.com/planet36/prng-test-bench/HEAD/prng-next-benchmark.cpp>
  - <https://raw.githubusercontent.com/planet36/prng-test-bench/HEAD/prng-dump.cpp>
  - <https://raw.githubusercontent.com/planet36/prng-test-bench/HEAD/test-prng-dump.bash>
  - <https://raw.githubusercontent.com/planet36/prng-test-bench/HEAD/run-benchmarks.bash>
  - <https://raw.githubusercontent.com/planet36/prng-test-bench/HEAD/results/prng-next-benchmark.txt>
  - <https://raw.githubusercontent.com/planet36/prng-test-bench/HEAD/results/prng-next-benchmark.json>
  - <https://raw.githubusercontent.com/planet36/prng-test-bench/HEAD/results/prng-results.tlmax-256MB.summary.txt>
  - <https://raw.githubusercontent.com/planet36/prng-test-bench/HEAD/results/prng-results.tlmax-512GB.summary.txt>
  - <https://raw.githubusercontent.com/planet36/prng-test-bench/HEAD/include/aes_ctr_128.hpp>
  - <https://raw.githubusercontent.com/planet36/prng-test-bench/HEAD/include/clmulrand.hpp>
  - <https://raw.githubusercontent.com/planet36/prng-test-bench/HEAD/include/clmum.hpp>
  - <https://raw.githubusercontent.com/planet36/prng-test-bench/HEAD/include/urbg_base_class.hpp>
  - <https://raw.githubusercontent.com/planet36/prng-test-bench/HEAD/include/mm_cast.hpp>
  - <https://raw.githubusercontent.com/planet36/prng-test-bench/HEAD/include/simd_types.hpp>
  - <https://raw.githubusercontent.com/planet36/prng-test-bench/HEAD/include/wyprimes.hpp>
  - <https://raw.githubusercontent.com/planet36/prng-test-bench/HEAD/include/sha2_iv.h>
  - <https://raw.githubusercontent.com/planet36/prng-test-bench/HEAD/include/prng.hpp>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/planet36/prng-test-bench`) · [data/wave8/enrich/raw/github_com_planet36_prng_test_bench.json](../../../data/wave8/enrich/raw/github_com_planet36_prng_test_bench.json) (enrichment confidence 0.65)

</details>
