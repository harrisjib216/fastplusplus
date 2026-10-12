# rapidhash

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [String search and hashing](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `MIT` · 🟢 active

> Header-only, wyhash-derived 64-bit hash beating xxh3 on latency and throughput on most CPUs; ties or loses on AMD Ryzen.

| | |
|---|---|
| **Beats** | xxh3 (xxHash3) — not literally std::hash, but the widely-used fast non-cryptographic hash function developers use in place of std::hash |
| **Claimed result** | Latency on M1 Pro: 1.79ns vs xxh3's 1.92ns; on M3 Pro: 1.38ns vs 1.50ns; on Neoverse V2: 2.05ns vs 2.15ns; roughly on par on Ryzen 9700X (1.46ns vs 1.45ns). Peak throughput on M4: 71GB/s vs xxh3's 49GB/s (\~45% faster, derived from page data); on M3 Ultra 61GB/s vs 47GB/s; on Neoverse V2 38GB/s vs 34GB/s; xxh3 is faster on Ryzen 9700X (78GB/s vs rapidhash's 68GB/s). |
| **Workload** | Average per-hash latency hashing 4/8/16-byte keys, and peak throughput hashing 16KB-2MB files, measured on several CPUs. |
| **Metric** | throughput |
| **Hardware** | Apple M1 Pro, M3 Pro, M3 Ultra, M4; ARM Neoverse V2; AMD Turin; AMD Ryzen 9700X (per README tables; AMD Turin appears only in the latency table) |
| **Adoption** | 907 stars; used in Chromium, Node.js, Folly's F14, Fuchsia, Ninja, JuliaLang, and Zig |
| **Last commit** | 2026-08-19 |
| **Links** | [repository](https://github.com/Nicoshev/rapidhash) · [benchmark](https://github.com/Nicoshev/rapidhash#outstanding-performance) |

## Verdict

README benchmarks (bench/ harness adapted from xxHash's benchHash, compiler/flags unstated) show rapidhash beating xxh3 on average per-hash latency for 4/8/16-byte keys on Apple M1 Pro, M3 Pro, ARM Neoverse V2, and AMD Turin (roughly tied on Ryzen 9700X), and beating xxh3 on peak throughput hashing 16KB-2MB files on M1 Pro, M3 Pro, M3 Ultra, M4, and Neoverse V2 (xxh3 wins on Ryzen 9700X, 78 vs 68 GB/s). Independently, rurban/smhasher's default-build results table (AMD Ryzen 5 3350G) also shows rapidhash ahead of xxh3 on both bulk throughput and small-key cycles/hash, without stating compiler flags.

## Use it when

- General-purpose in-memory hash-table/hash-map keys needing a fast, SMHasher-passing 64-bit hash as an xxh3 or wyhash replacement.
- Mixed key-size workloads (roughly 4 bytes to 2MB) on x86-64 or aarch64 where one algorithm should cover both tiny keys and large buffers.
- Latency-sensitive small-key hashing (4/8/16 bytes) on Apple Silicon, ARM Neoverse V2, or AMD Turin, where README numbers show rapidhash \~5-9% faster than xxh3.
- Code-size-constrained embedded/mobile targets hashing keys up to \~48 bytes: use rapidhashNano (&lt;100 instructions, no stack usage).
- Cache-miss-sensitive HPC/server code hashing keys up to \~512 bytes: use rapidhashMicro (\~140 instructions, no stack usage).

## Skip it when

- Streaming/incremental hashing where input length isn't known upfront and can't be buffered whole: no streaming API ships despite the README's 'Streamable' framing (maintainer confirms in issue #39 that the C/C++ side has no streaming implementation and the hash targets short, whole-buffer runs).
- Adversarial or untrusted-input contexts needing DoS resistance: with the default secret, same-length inputs above 16 bytes admit a documented collision construction (issue #25); mitigate by generating a per-process secret with the bundled secret.h.
- Any context requiring cryptographic hashing or collision resistance guarantees: explicitly non-cryptographic.
- Need for a 128-bit or 32-bit hash output: not offered (open issues #26 and #46, no stated plans).
- Peak throughput on AMD Zen5 desktop parts (Ryzen 9700X): xxh3 leads there in the README's own table (78 vs 68 GB/s).

## How it is fast

The core is a wyhash-style multiply-mix: a 64x64-&gt;128-bit multiply (rapid_mum) folded with XOR (rapid_mix), deliberately avoiding AES-NI/CLMUL or other vectorized instructions so the same code path runs on x86-64 and aarch64. Clang 18+ compiles rapidhash to roughly 185 instructions on both architectures (rapidhashMicro \~140, rapidhashNano under 100, both stack-free). An optional RAPIDHASH_UNROLLED macro trades code size for large-input throughput; RAPIDHASH_PROTECTED trades speed for extra entropy protection against the multiply's zero-collapse cases.

## Compared with alternatives

Pick rapidhash over komihash or MUM/VMUM when you want the specific hash already vendored into Chromium, Node.js, Folly's F14, Fuchsia, Ninja, JuliaLang, and Zig, plus size-tuned Micro/Nano builds for cache- or code-size-constrained targets. Pick HighwayHash instead if AVX2-level throughput matters more than portability, since HighwayHash depends on vector instructions rapidhash deliberately avoids; pick t1ha or CityHash if a longer independent track record matters more than the newest peak-speed numbers.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (stdint.h, string.h; intrin.h + _umul128 intrinsic on MSVC) |
| **Minimum toolchain** | C99 or C++11; constexpr evaluation additionally needs C++14. README claims support for GCC, Clang, Intel icx, and MSVC; the \~185-instruction codegen figure is specifically for Clang 18+. |
| **Platforms** | x86-64 and aarch64 are the tested/optimized targets (no AVX/AES-NI/CLMUL required); the header compiles generically elsewhere via its endianness macros, consistent with the README's 'platform-independent' claim, but only x86-64/aarch64 numbers are published. |
| **Thread safety** | not documented explicitly; the hash functions are stateless, operating only on caller-supplied input and a read-only default secret table, so concurrent calls from multiple threads need no external synchronization |
| **Drop-in for the baseline** | partial — same call shape as xxh3 (pointer + length [+ seed] -&gt; 64-bit integer) but produces different, incompatible hash values; rapidhash/Micro/Nano are also not interchangeable with each other above 48-80 byte inputs |

## Gotchas

- README markets the family as 'Streamable,' but no streaming API exists for C/C++ (open issue #39) — it's designed for short, whole-buffer runs, not incremental hashing.
- Default secret permits a documented collision construction for same-length inputs over 16 bytes (issue #25); use secret.h to generate a custom secret for any adversarial-input exposure.
- rapidhash, rapidhashMicro, and rapidhashNano only produce matching output below 80 and 48 bytes respectively — swapping variants for larger keys silently changes hash values.
- An older header-only revision could produce 'multiple definition of rapid_secret' linker errors across translation units (issue #6, fixed via a static/const macro); the vendored old_version/rapidhashV1.h may not carry that fix.

## Caveats and trade-offs

The README performance tables name the CPUs tested but not the compiler version or flags; they note only that long-input measurements used the RAPIDHASH_UNROLLED macro. The bench/ harness (adapted from xxHash's benchHash, GPLv2-licensed Makefile) defaults to CFLAGS -O3, but nothing confirms that setting produced the published table. xxh3 wins peak throughput on Ryzen 9700X (78 vs 68 GB/s) and ties on latency there. Independent corroboration: rurban/smhasher's summary table (default AMD Ryzen 5 3350G) lists rapidhash at 21513.71 MiB/s and 22.04 cycles/hash vs xxh3 at 20853.74 MiB/s and 29.46 cycles/hash (compiler/flags not stated there either).

No cryptographic security guarantees; avoids CLMUL/AES-NI so it stays portable across x86-64 and aarch64; ships three variants (rapidhash/Micro/Nano) trading long-input throughput for small-input latency or code size.

## Maintenance

Actively maintained single header (last commit 2026-08-19, V3 released 2025), MIT-licensed and trivial to vendor; open issues (no 128-bit or 32-bit output, no streaming API) mark real feature gaps rather than signs of abandonment.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification B, tier now B.
- **Tier reason:** The README tables (first-party, bench/ harness adapted from xxHash benchHash, compiler/flags unstated) alone would be C, but the independent rurban/smhasher suite, which the README links, also shows rapidhash ahead of xxh3 (21513.71 vs 20853.74 MiB/s bulk; 22.04 vs 29.46 cycles/hash small keys on its default AMD Ryzen 5 3350G), without stating compiler/flags, so B holds.
- **Verifier notes:** All README numbers match the record, including the \~45% M4 derivation (71 vs 49 GB/s). The record omitted AMD Turin (latency 2.31ns vs xxh3 2.35ns); I fixed hardware and added the SMHasher corroboration to caveats. Metadata checks out: MIT, 907 stars, not a fork or archived, last commit 2026-08-19.
- **Fields the verifier corrected:** `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/Nicoshev/rapidhash>
  - <https://github.com/Nicoshev/rapidhash#outstanding-performance>
  - <https://github.com/Nicoshev/rapidhash/tree/master/bench>
  - <https://github.com/rurban/smhasher>
- **Sources the enricher read:**
  - <https://github.com/Nicoshev/rapidhash>
  - <https://github.com/Nicoshev/rapidhash#outstanding-performance>
  - <https://github.com/Nicoshev/rapidhash/blob/master/rapidhash.h>
  - <https://github.com/Nicoshev/rapidhash/issues>
  - <https://github.com/Nicoshev/rapidhash/issues/39>
  - <https://github.com/Nicoshev/rapidhash/issues/6>
  - <https://github.com/Nicoshev/rapidhash/issues/25>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/nicoshev/rapidhash`) · [data/wave1/enrich/raw/github_com_nicoshev_rapidhash.json](../../../data/wave1/enrich/raw/github_com_nicoshev_rapidhash.json) (enrichment confidence 0.6)

</details>
