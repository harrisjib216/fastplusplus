# MuseAir (C++ port)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Non-cryptographic hashes](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `GPL-3.0` · 🟢 active

> GPL-3.0 C++20 header port of deprecated MuseAir v0.4-rc4. Ties wyhash in bulk, slower on short keys.

| | |
|---|---|
| **Beats** | wyhash |
| **Claimed result** | Not faster than wyhash overall. On 1-31 byte keys the README chart shows MuseAir and MuseAir-BFast using more cycles per hash than wyhash and rapidhash at almost every length (about 18.6 vs 15.1 cycles at 1-4 bytes, about 35-45 vs 27 at 17-31 bytes). In bulk (262144-byte keys) standard MuseAir is on par with wyhash v4.2 at about 34 GiB/s @ 3.5 GHz. The BFast line appears to be about 42 GiB/s, roughly 1.2x wyhash (read from chart; line colours repeat, so approximate). The README text claims 'up to 33.2 GiB/s' for BFast and that MuseAir 'holds its own against' wyhash, which is a parity claim. |
| **Workload** | SMHasher3 small-key (1-31 byte) and bulk (262144-byte) speed tests, run on a 12th Gen Intel i7-12700K, comparing MuseAir/MuseAir-BFast against wyhash and rapidhash |
| **Metric** | throughput |
| **Hardware** | 12th Gen Intel Core i7-12700K (Windows/MSYS); GiB/s figures assume 3.5 GHz |
| **Compiler and flags** | GCC 11.3.0 (MSYS on Windows), from the SMHasher3 cmake log in the README; flags and build type not stated |
| **Adoption** | 7 stars |
| **Last commit** | 2026-02-23 |
| **Links** | [repository](https://github.com/Twilight-Dream-Of-Magic/museair-cpp) · [benchmark](https://github.com/Twilight-Dream-Of-Magic/museair-cpp) |

## Verdict

The only performance data is the author's own SMHasher3 speed runs, shown as PNG charts, on an i7-12700K under Windows/MSYS with GCC 11.3.0 (flags not stated; GiB/s at a nominal 3.5 GHz). They show MuseAir at parity with wyhash v4.2 in bulk (about 33-34 GiB/s), BFast at about 42 GiB/s (about 1.2x, colour-ambiguous), and both slower than wyhash and rapidhash on 1-31-byte keys. The charts predate the current code and may not be of this port at all. SMHasher3's public results (MuseAir v0.3 bfast 8.64 bytes/cycle vs wyhash 6.98) come from a different, CC0 implementation of an older algorithm version.

## Use it when

- You specifically want MuseAir v0.4-rc4 hash values in a C++20 codebase that can accept GPL-3.0, for example to match outputs from a system already pinned to that version.
- Bulk hashing of trusted, non-adversarial buffers of a few hundred bytes and up with the BFast variant. The author's i7-12700K chart shows about 42 GiB/s (at a nominal 3.5 GHz) against about 34 GiB/s for wyhash v4.2, though the chart's line colours are ambiguous and predate the current code.
- Portable scalar hashing on any 64-bit compiler with __uint128_t; there are no CPU-feature requirements such as AES-NI or AVX2.

## Skip it when

- Any new use. Upstream's CHANGELOG says a seed-independent trivial-collision flaw (eternal-io/museair#3, July 2026) means 'all previous versions of the algorithm are deprecated, and should be considered compromised'. The fixed algorithm is v2; this port is still on v0.4-rc4. The port's 17-32-byte short path has the flawed structure: the second 16 bytes pass through seed-free multiplies and are XORed into the state, so colliding pairs can be built for every seed.
- The 128-bit output. Upstream says the v0.4-rc4 128-bit variant 'had insufficient output diffusion and actually failed the SMHasher3 test suite', and the fix came in a later version.
- Hash-table keys and short strings (1-31 bytes). By the port's own chart, MuseAir and BFast take more cycles than wyhash and rapidhash at nearly every length: about 18.6 vs 15.1 at 1-4 bytes, 14.6 vs 11.0 at 12-16 bytes, and about 35-45 vs 27 at 17-31 bytes.
- Proprietary or permissively licensed products. The LICENSE file and the header are GPL-3.0, even though the README says MIT; upstream's own museair.cpp reference is CC0.
- Projects that need a maintained, tested dependency. The repo has 7 stars and 4 commits, no releases, no tests beyond a main.cpp verification-code check, and no CI (the README's CI badge points to a workflow that does not exist).

## How it is fast

The core is scalar 64x64-&gt;128-bit multiplication (__uint128_t, or _umul128 on MSVC x64) with no SIMD or assembly, despite the README's claims. Inputs over 96 bytes go through a six-word 'ring accumulator'. Each 16-byte step XORs two input words into adjacent state words, wide-multiplies them, and feeds the low/high halves into the next word, so the six multiplies per 96 bytes run in parallel through instruction-level parallelism. Standard mode adds the product into the state (+=); BFast overwrites it (=), which saves work but loses protection against 'blinding multiplication' (a zero multiplicand wiping state). Inputs of 32 bytes or less take a branchy short path with two to four wide multiplies, and 33-96 bytes take an unrolled partial-body path.

## Compared with alternatives

Rarely. For MuseAir itself, prefer the upstream eternal-io/museair (Rust crate 0.6.0 or its CC0 museair.cpp reference, both algorithm v2 with the collision fix). For short keys in C/C++, wyhash, rapidhash and a5hash are faster, and a5hash posts 26.91 SMHasher3 cycles against wyhash's 29.31. Pick this port only if you must reproduce v0.4-rc4 outputs from a C++20 header and GPL-3.0 is acceptable.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (standard library only; &lt;intrin.h&gt; on MSVC x64) |
| **Minimum toolchain** | C++20 (uses &lt;bit&gt; std::endian/std::rotl, [[likely]]); the demo CMakeLists needs CMake 3.10+. The repo topics say cpp17, but the code needs C++20. |
| **Platforms** | Any 64-bit target with __uint128_t (GCC/Clang) or MSVC x64 _umul128; a 32x32 fallback exists for others. Big-endian needs the caller to pass ByteSwap=true. Only x86-64 Windows/MSYS results are shown. |
| **Thread safety** | Not documented; the class has no data members and the hash functions touch only locals and constexpr constants, so concurrent calls are safe by inspection. |
| **Drop-in for the baseline** | false — different API (object + template flags, void\* output, single 64-bit seed, no secret) and different hash values from wyhash; a wrapper function is needed. |

## Gotchas

- The README contradicts the code in several places. It says MIT, but the LICENSE file is GPL-3.0. It mentions 'platform-specific assembly' and 'SIMD', but there is none. It describes BlindFast as trading 'accuracy'; in fact BFast gives up blinding-multiplication resistance, and upstream notes that 64-bit BFast has a fixed 8-byte prefix that makes bytes 9-16 irrelevant for 9-16-byte inputs.
- The benchmark charts were last updated in the June 2025 commit, before the February 2026 rewrite to 0.4-rc4. The SMHasher3 build log shown compiles SMHasher3's own hashes/museair.cpp, and nothing shows that this port's header was the code measured. The README's '33.2 GiB/s' also disagrees with the chart.
- ByteSwap is not auto-detected. The README example always uses hash&lt;false&gt;, so on big-endian hosts it produces different values from the little-endian reference unless you pass std::endian::native != std::endian::little, as main.cpp does.
- hash() and hash_128() are non-const, non-static member functions, so they cannot be called on a const MuseAir object. Correctness is checked only by self-generated verification codes in main.cpp, which the README does not cross-reference with upstream.

## Known shortcomings

- C++ port of eternal-io/museair (listed separately). Its own chart shows it slower than wyhash/rapidhash on 1-31 byte keys and only about equal to wyhash in bulk (BFast \~42 vs \~34 GiB/s, read from chart); README's 33.2 GiB/s does not match the chart. GCC 11.3 MSYS, flags not stated. License is inconsistent (badge GNU, README MIT, LICENSE file GPL-3.0): treat as GPL-3.0.
- Ports algorithm v0.4-rc4; the upstream CHANGELOG (Jul 2026) says all pre-v2 versions are compromised, and the port's 17-32 byte path has the same seed-free collision structure (code reading); v0.4-rc4 128-bit failed SMHasher3. Charts predate the 2026-02 rewrite and the log builds SMHasher3's own museair.cpp, so they may not measure this port. README claims asm/SIMD but the code has none. 7 stars, 4 commits, no CI or tests. Use eternal-io/museair v2 (CC0) instead.

## Caveats and trade-offs

This is a third-party C++20 port of eternal-io/museair (Rust), which is a separate catalog candidate. By the port's own charts it is slower than wyhash and rapidhash on small keys; only BFast bulk hashing looks faster. The README's 33.2 GiB/s text does not match its bulk chart (about 42 GiB/s). SMHasher3's upstream results (MuseAir.bfast 8.64 bytes/cycle bulk and 26.28 cycles for small keys, against wyhash's 6.98 and 29.31) come from SMHasher3's own CC0 MuseAir v0.3 code, not from this port. On licensing, the top badge says 'GNU' and the README License section says MIT, but the LICENSE file is GPL-3.0 (used here).

requires C++20; header-only but with platform-specific assembly on critical paths; this is a third-party reimplementation, not the canonical original (eternal-io/museair, Rust, no stated license)

## Maintenance

Nominally active (last commit 2026-02-23), but a one-person GPL-3.0 port stuck on algorithm v0.4-rc4, which upstream deprecated as compromised in July 2026; small enough to vendor, but the upstream CC0 v2 code is the better starting point.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification C, tier now C.
- **Tier reason:** These are the author's own SMHasher3 runs on an i7-12700K, shown only as PNG charts in the README. The SMHasher3 build log shows GCC 11.3.0 under MSYS, but no flags or build type are given. The MuseAir-BFast test names suggest a local SMHasher3 variant, not the public upstream code, so this is first-party with partial methodology (C).
- **Verifier notes:** I downgraded because the port's own README chart shows it slower than the wyhash baseline on 1-31 byte keys. Only BFast in bulk looks about 1.2x faster, and that reading is uncertain because the chart's line colours repeat. The tier stays C. Metadata matches the record: GPL-3.0, not a fork, 7 stars, last commit 2026-02-23 (active). The orchestrator should consider merging this into, or cross-referencing it with, the eternal-io/museair entry.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/Twilight-Dream-Of-Magic/museair-cpp>
  - <https://raw.githubusercontent.com/Twilight-Dream-Of-Magic/museair-cpp/main/images/Bulk%20Speed%20Test%20-%20GiBsec%20vs%20Alignment%20for%20wyhash%2C%20rapidhash%2C%20MuseAir%2C%20and%20MuseAir-BFast.png>
  - <https://raw.githubusercontent.com/Twilight-Dream-Of-Magic/museair-cpp/main/images/Small%20Key%20Speed%20Test%20-%20Cycles%20per%20Hash%20vs%20Key%20Size%20%5B1%2C%2031%5D-byte%20keys.png>
  - <https://gitlab.com/fwojcik/smhasher3/-/raw/main/hashes/museair.cpp>
  - <https://gitlab.com/fwojcik/smhasher3/-/raw/main/results/README.md>
- **Sources the enricher read:**
  - <https://github.com/Twilight-Dream-Of-Magic/museair-cpp>
  - <https://github.com/Twilight-Dream-Of-Magic/museair-cpp/blob/main/README.md>
  - <https://github.com/Twilight-Dream-Of-Magic/museair-cpp/blob/main/MuseAir.hpp>
  - <https://github.com/Twilight-Dream-Of-Magic/museair-cpp/blob/main/main.cpp>
  - <https://github.com/Twilight-Dream-Of-Magic/museair-cpp/blob/main/CMakeLists.txt>
  - <https://github.com/Twilight-Dream-Of-Magic/museair-cpp/blob/main/LICENSE>
  - <https://github.com/Twilight-Dream-Of-Magic/museair-cpp/commits/main>
  - <https://github.com/Twilight-Dream-Of-Magic/museair-cpp/commit/cb28d23>
  - <https://github.com/Twilight-Dream-Of-Magic/museair-cpp/commit/11b93d3>
  - <https://github.com/Twilight-Dream-Of-Magic/museair-cpp/commit/0c16a4a>
  - <https://github.com/Twilight-Dream-Of-Magic/museair-cpp/issues/1>
  - <https://raw.githubusercontent.com/Twilight-Dream-Of-Magic/museair-cpp/main/images/Bulk%20Speed%20Test%20-%20GiBsec%20vs%20Alignment%20for%20wyhash%2C%20rapidhash%2C%20MuseAir%2C%20and%20MuseAir-BFast.png>
  - <https://raw.githubusercontent.com/Twilight-Dream-Of-Magic/museair-cpp/main/images/Small%20Key%20Speed%20Test%20-%20Cycles%20per%20Hash%20vs%20Key%20Size%20%5B1%2C%2031%5D-byte%20keys.png>
  - <https://github.com/eternal-io/museair>
  - <https://github.com/eternal-io/museair/blob/master/README.md>
  - <https://github.com/eternal-io/museair/blob/master/CHANGELOG.md>
  - <https://github.com/eternal-io/museair/blob/master/museair.cpp>
  - <https://github.com/eternal-io/museair/issues/3>
  - <https://github.com/eternal-io/museair/commits/master>
  - <https://gitlab.com/fwojcik/smhasher3/-/raw/main/hashes/museair.cpp>
  - <https://gitlab.com/fwojcik/smhasher3/-/raw/main/results/README.md>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/twilight-dream-of-magic/museair-cpp`) · [data/wave7/enrich/raw/github_com_twilight_dream_of_magic_museair_cpp.json](../../../data/wave7/enrich/raw/github_com_twilight_dream_of_magic_museair_cpp.json) (enrichment confidence 0.75)

</details>
