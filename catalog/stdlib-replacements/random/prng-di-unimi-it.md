# xoshiro/xoroshiro generators

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Random numbers](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `0BSD (generator sources, e.g. xoshiro256plusplus.c, carry a public-domain dedication plus the 0BSD permission text; not CC0-1.0)` · 🟢 active

> Public-domain xoshiro/xoroshiro PRNG family, faster than std::mt19937_64, not cryptographically secure.

| | |
|---|---|
| **Beats** | std::mt19937_64 |
| **Claimed result** | xoshiro256++: 0.75 ns/64 bits, 0.34 cycles/byte vs MT19937-64: 1.36 ns/64 bits, 0.62 cycles/byte -- about 1.8x faster (derived from page data). |
| **Workload** | Shootout table (harness.c timing + PAPI cycle counts) measuring nanoseconds to emit 64 random bits and cycles/byte for each generator on a single core, including MT19937-64 and xoshiro256++/xoroshiro128++. |
| **Metric** | throughput |
| **Hardware** | 12th Gen Intel Core i7-12700KF @ 3.60GHz |
| **Compiler and flags** | gcc 12.2.1 with -fno-unroll-loops; -march=native deliberately not used (page: gains 'might not be possible when the generator is embedded in user code'); optimization level (-O) not stated on the page. |
| **Adoption** | Per the page's Adoption section: default PRNG in Julia (xoshiro256++), Lua and GNU Fortran (xoshiro256\*\*), .NET 6 (xoshiro256\*\*/xoshiro128\*\*); Rust rand SmallRng is xoshiro256++/xoshiro128++; Java 17 java.util.random ships xoroshiro128++/xoshiro256++; Mbed/Zephyr use xoroshiro128+. (JS engines/V8 use the older xorshift128+, and NumPy's default is PCG64, not xoshiro.) |
| **Links** | [repository](https://prng.di.unimi.it) · [benchmark](https://prng.di.unimi.it/) |

## Verdict

On the project's own shootout table (gcc 12.2.1, -fno-unroll-loops, no -march=native, i7-12700KF @3.6GHz), xoshiro256++ emits 64 random bits in 0.75ns/0.34 cycles-per-byte versus 1.36ns/0.62 cycles-per-byte for a reference Matsumoto-Nishimura MT19937-64 C implementation (not std::mt19937_64 itself), about 1.8x faster; per the record's verification notes this is corroborated by a peer-reviewed 2021 ACM TOMS paper (arXiv:1805.01407, whose title/authors/thesis I confirmed but whose Table 1 numbers were not visible on the abstract page I fetched) reporting 0.86ns vs 2.19ns on different hardware.

## Use it when

- Non-cryptographic Monte Carlo / simulation / scientific-computing code generating large volumes of 64-bit random values where throughput matters
- Need many independent parallel random streams (per-thread, per-worker) - jump()/long_jump() give cheap non-overlapping subsequences without reseeding
- Vendoring a tiny, public-domain, single-file generator into a codebase - already the default behind Julia's Random, Rust's SmallRng, Java 17+ java.util.random, .NET 6, Lua, and GNU Fortran
- Replacing std::mt19937_64 in hot loops where its large state and tempering overhead show up in profiles
- Constrained/embedded targets needing a very small generator - xoroshiro128+ is used in Mbed/Zephyr, and 32/16-bit variants exist for smaller word sizes

## Skip it when

- Any cryptographic use (keys, nonces, tokens) - explicitly not cryptographically secure; use a CSPRNG (ChaCha20, AES-CTR) instead
- Need a zero-effort drop-in C++ &lt;random&gt; UniformRandomBitGenerator - these are raw C source files, not a std::mt19937_64-compatible class; you wire up seeding and state ownership yourself
- Statistical-test purism: xoshiro/xoroshiro fail a handful of specialized tests despite passing BigCrush overall (e.g. xoroshiro128+ shows a detectable low-bit Hamming-weight dependency after \~5TB of output)
- Code that depends on MT19937's enormous 2^19937-1 period for theoretical guarantees - xoshiro256++'s 2^256-1 period is smaller, though still astronomically large for practical use
- Wanting a conventional maintained repo with issue tracker/CI - this is a hand-maintained personal website distributing source files, not a git project

## How it is fast

Each generator keeps 128-1024 bits of state and does a handful of XOR/shift/rotate ops plus one integer add or multiply per call ('scrambled linear' generators), versus MT19937-64's much larger \~2.5KB state array and heavier tempering step. On the project's own shootout (gcc 12.2.1, -fno-unroll-loops, i7-12700KF), xoshiro256++ produces 64 bits in 0.75ns/0.34 cycles-per-byte against 1.36ns/0.62 cycles-per-byte for a reference MT19937-64 C implementation, about 1.8x. The small register-sized state also lets AVX2-vectorized builds run several lanes in parallel (xoshiro256+ drops to 0.19ns/64 bits at 8-wide), though the shootout table itself deliberately avoids -march=native.

## Compared with alternatives

no siblings catalogued yet

## Integration

| | |
|---|---|
| **Form** | source-drop (single .c file per generator variant) |
| **Dependencies** | none for the core generator (stdint.h only); the separate f2x.c tool is only needed to compute custom/arbitrary jump distances |
| **Minimum toolchain** | any C compiler with stdint.h (C99-era); no build system - compile or #include the .c file directly |
| **Platforms** | any platform with the needed integer width (16/32/64-bit variants provided); the reference code has no SIMD/architecture-specific intrinsics, though hand-vectorized AVX2 builds are discussed on the page |
| **Thread safety** | not thread-safe as shipped - state is a plain global array (e.g. `static uint64_t s[4]`) with no locking; give each thread its own state instance, offset via jump()/long_jump() for non-overlapping streams |
| **Drop-in for the baseline** | partial — same 'call next() for the next block of random bits' shape as advancing std::mt19937_64, but not a C++ UniformRandomBitGenerator class; no built-in seeding routine or &lt;random&gt;-compatible wrapper is provided |

## Gotchas

- Must not seed the state directly from a plain counter/timestamp - guidance on the page is to expand the seed through a different-family generator (SplitMix64), or output quality suffers
- xoroshiro128+'s low output bits have a detectable linear dependency (fails specific tests after \~5TB of output) - use xoroshiro128++ or xoroshiro128\*\* if the low bits matter
- jump()/long_jump() only give fixed 2^128/2^192 strides; arbitrary jump distances require the separate f2x.c polynomial tool
- The all-zero state is a fixed point and invalid for these generators - any custom seeding routine must avoid it

## Caveats and trade-offs

Author-run first-party site (Sebastiano Vigna, co-author of the algorithms), not an independent benchmark. The optimization level is not stated (only -fno-unroll-loops, no -march=native). The MT19937-64 row times the Matsumoto-Nishimura reference C implementation, not std::mt19937_64 from libstdc++/libc++/MSVC STL, and the 32-bit MT19937/std::mt19937 is not in the table. Results are corroborated by the peer-reviewed ACM TOMS 47(4) 2021 paper (DOI 10.1145/3460772; arXiv:1805.01407 Table 1: xoshiro256++ 0.86 ns vs MT19937-64 2.19 ns, i7-8700B, gcc 8.3.0). harness.c is GPL-3.0-or-later (benchmark only). The generators are public domain/0BSD with no patent grant. This is a hand-maintained website, not a git repo; xoshiro256plusplus.c Last-Modified header is 2026-06-19.

Not cryptographically secure; xoshiro/xoroshiro fail a small number of specialized statistical tests (e.g. linear-complexity/binary-rank style tests) despite passing BigCrush overall; much shorter period than MT19937 (e.g. 2^256-1 vs 2^19937-1), which is a theoretical rather than practical concern for almost all uses.

## Maintenance

Hand-maintained personal website (not a git repo) rather than a conventional software release, marked 'active' with the xoshiro256plusplus.c file last modified June 2026; each generator is a single copy-pasteable public-domain/0BSD-licensed C file, consistent with its 'copyable' usability rating.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): downgrade; tier before verification A, tier now B.
- **Tier reason:** Shootout table on prng.di.unimi.it shows xoshiro256++ 0.75 ns/64b, 0.34 cycles/B vs MT19937-64 1.36 ns, 0.62 cycles/B. The harness (harness.c) and generator sources are public, and gcc 12.2.1 and the i7-12700KF are named. It is not A because the page never gives the optimization level (only -fno-unroll-loops) and it times the Matsumoto-Nishimura reference MT19937-64 C code, not std::mt19937_64. The peer-reviewed ACM TOMS 47(4) 2021 paper (arXiv:1805.01407, Table 1) independently shows the same win: xoshiro256++ 0.86 ns vs MT19937-64 2.19 ns (i7-8700B, gcc 8.3.0), which supports B.
- **Verifier notes:** Numbers match this project's row. Downgraded A-&gt;B: the -O level is unstated and the named std:: baseline is not what was timed. Fixed the stars_or_usage claims about NumPy and V8 (both wrong per the page itself) and the license (text is 0BSD + public-domain dedication, not CC0).
- **Fields the verifier corrected:** `baseline`, `compiler_and_flags`, `license`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://prng.di.unimi.it/>
  - <https://prng.di.unimi.it/harness.c>
  - <https://prng.di.unimi.it/xoshiro256plusplus.c>
  - <https://arxiv.org/abs/1805.01407>
  - <https://arxiv.org/pdf/1805.01407>
  - <https://api.crossref.org/works?query.bibliographic=Scrambled+Linear+Pseudorandom+Number+Generators+Blackman+Vigna&rows=3>
- **Sources the enricher read:**
  - <https://prng.di.unimi.it/>
  - <https://prng.di.unimi.it/xoshiro256plusplus.c>
  - <https://arxiv.org/abs/1805.01407>
- **Raw records:** [data/wave0-seed/verified.json](../../../data/wave0-seed/verified.json) (id `https://prng.di.unimi.it`) · [data/wave0-seed/enrich/raw/prng_di_unimi_it.json](../../../data/wave0-seed/enrich/raw/prng_di_unimi_it.json) (enrichment confidence 0.78)

</details>
