# wyhash

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Non-cryptographic hashes](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `Unlicense` · 🟢 active

> Header-only 64-bit non-cryptographic hash + PRNG; about 9% faster bulk throughput than xxHash's XXH3.

| | |
|---|---|
| **Beats** | xxHash |
| **Claimed result** | wyhash 22,640.53 MiB/s vs xxh3 20,853.74 MiB/s (\~1.09x, derived from page data); vs City64 14,390.09 MiB/s (\~1.57x, derived from page data); vs Murmur3A 3,027.30 MiB/s (\~7.5x, derived from page data). |
| **Workload** | SMHasher bulk speed test: average MiB/sec across alignments 0-7 when hashing 262144-byte keys, plus small-key (1-31 byte) cycles/hash, on the suite's default reference machine. |
| **Metric** | throughput |
| **Hardware** | Default reference machine: AMD Ryzen 5 3350G 3.6GHz per the smhasher README (table.html says 'AMD Ryzen 5 PRO 3350G 3.6GHz workstation'); compiler/flags not stated |
| **Adoption** | 1.1k stars; default hash of Zig, V, Nim, and Go (since 1.17); used in abseil's low_level_hash.h and Windows Terminal |
| **Last commit** | 2026-03-23 |
| **Links** | [repository](https://github.com/wangyi-fudan/wyhash) · [benchmark](https://github.com/rurban/smhasher) |

## Verdict

On the rurban/smhasher bulk-speed test (262144-byte keys, averaged across alignments 0-7) on the suite's AMD Ryzen 5 3350G 3.6GHz reference machine (compiler/flags not stated), wyhash measured 22,640.53 MiB/s versus xxHash's XXH3 at 20,853.74 MiB/s (\~1.09x), City64 at 14,390.09 MiB/s (\~1.57x), and Murmur3A at 3,027.30 MiB/s (\~7.5x).

## Use it when

- Bulk hashing of large buffers (the benchmarked case is 256KB keys) where a \~9% throughput edge over XXH3 matters at scale, e.g. content-addressed storage or dedup
- Small/short keys (&lt;=16 bytes), which get a dedicated fast path — this is why Go (1.17+), Zig, V, and Nim use it as their default map hash
- C/C++ projects that want a single vendorable header with no build step, working on 32- or 64-bit, big- or little-endian, x86/aarch64
- Internal hash tables or checksums where non-adversarial input is acceptable and \~62-bit (not full 64-bit) collision resistance is fine
- Projects already comfortable adopting a library whose own maintainer is steering new users toward its successor (see status_note)

## Skip it when

- Hashing untrusted/adversarial input with the default secret — the built-in _wyp constant is public; use make_secret() to derive a per-process secret for hash-flood resistance, which the library does not do automatically
- Anywhere full 64-bit collision resistance or a security review is required — the author states wyhash/wyrand are only about 62-bit collision resistant, per outside reports cited in the README
- Generating very long random streams with wyrand — the author's own README says wyrand fails PractRand at 32TB/23 days, and issue #130 separately reported wyrand failing 64-bit 1-D collision tests
- Using the separate 32-bit variant (wyhash32.h) on 4-byte keys from sparse/bitflip keysets — open issue #153 (filed 2026-02-27, still open) reports SMHasher3 failures there; this does not affect the 64-bit wyhash() function that was benchmarked here
- Starting a brand-new project where you want the actively promoted state of the art — the wyhash README itself says the project 'has evolved into rapidhash' and points new adopters there

## How it is fast

The core primitive is a 128-bit multiply-and-xor-mix (_wymum/_wymix, "MUM"), implemented via __uint128_t on GCC/Clang or the _umul128 intrinsic on MSVC x64, so one multiply produces two mixed 64-bit halves per round. For inputs &gt;=48 bytes the main loop is unrolled to run three interleaved MUM mixes per 48-byte chunk (three independent accumulator states), overlapping multiply latency across chunks instead of serializing one mix per 16 bytes. Short inputs (&lt;=16 bytes) take a separate branch that reads overlapping 3/4/8-byte windows directly instead of looping, avoiding per-byte overhead on small keys.

## Compared with alternatives

Pick wyhash over xxHash when the \~9% bulk-throughput edge (22,640.53 vs 20,853.74 MiB/s on the cited single-CPU run) is worth taking on a Tier-B, single-reference-machine result with no stated compiler/flags; xxHash (XXH3) is the safer default when you want a widely adopted, spec-documented hash with results reproduced across more hardware.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none beyond the C standard library (stdint.h, string.h); &lt;intrin.h&gt; pulled in only for the MSVC x64 path |
| **Minimum toolchain** | C99 / C++11-ish (stdint.h, static inline); relies on GCC/Clang __uint128_t or MSVC's _umul128 intrinsic for the 128-bit multiply, with a portable 32x32 fallback for other compilers |
| **Platforms** | x86-64, aarch64, and 32-bit systems; both little- and big-endian (explicit byteswap paths); GCC, Clang, MSVC, Intel C++ |
| **Thread safety** | not explicitly documented in the README; from reading wyhash.h, wyhash()/wyhash64() are pure functions with no shared/global mutable state and are safe to call concurrently, while wyrand()/w1rand()/make_secret() mutate a uint64_t\* seed the caller owns, so they are only thread-safe if each thread uses its own seed |
| **Drop-in for the baseline** | partial — explain: wyhash() requires an explicit 4x uint64_t secret argument (xxHash's XXH3 functions take just data/len/seed), so callers must change the call site, not just relink |

## Gotchas

- Default secret (_wyp) is a fixed, publicly known constant baked into the header; generate your own with make_secret(seed, secret) if flood resistance matters
- Only \~62-bit, not full 64-bit, collision resistance per the README's own limitations section
- wyrand fails PractRand on very long streams (32TB, \~23 days) per the author's README
- wyhash32.h (a separate, distinct file from the benchmarked 64-bit wyhash.h) currently fails SMHasher3 Sparse/Bitflip tests on 4-byte keys — open issue #153, unresolved as of 2026-08

## Caveats and trade-offs

wyhash's own README/repo has no benchmark table (only benchmark.cpp). The numeric win over xxHash comes from the independent rurban/smhasher shootout, which names the CPU (AMD Ryzen 5 3350G) but not the compiler or flags, so this is capped at Tier B. The margin over xxh3 is narrow (\~9%) and depends on workload and CPU; other CPUs in the suite's linked tables may reorder the two. The wyhash README itself says wyhash 'has evolved into rapidhash', its faster successor. The Unlicense is OSI-approved but has no explicit patent grant.

No patent grant (Unlicense/public-domain dedication). Author states wyhash/wyrand are not fully 64-bit collision resistant (\~62 bits) and wyrand can fail PractRand on very long (32TB) streams. wyhash's own README states the project 'has evolved into rapidhash', its successor, so new adopters are steered elsewhere.

## Maintenance

Actively maintained (last commit 2026-03-23; 19 open issues, not archived), and public-domain (Unlicense) so it costs nothing to vendor, but the author's own README states wyhash 'has evolved into rapidhash,' its designated successor, so new adopters are explicitly pointed elsewhere.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): confirm; tier before verification B, tier now B.
- **Tier reason:** The rurban/smhasher README table and the linked table.html list wyhash 22640.53, xxh3 20853.74, City64 14390.09 and Murmur3A 3027.30 MiB/sec, and doc/wyhash.txt matches. The suite code is public and the CPU is named (Ryzen 5 3350G), but no compiler or flags are given, so B (well-known independent suite) and not A.
- **Verifier notes:** All four numbers match the correct rows on the smhasher README and table.html. Metadata checked: Unlicense, 1148 stars, last commit 2026-03-23, not archived or forked. The usage claims (Zig, V, Nim, Go 1.17, abseil, Windows Terminal) come from the wyhash README.
- **Fields the verifier corrected:** `workload`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/rurban/smhasher>
  - <https://rurban.github.io/smhasher/doc/table.html>
  - <https://github.com/rurban/smhasher/blob/master/doc/wyhash.txt>
  - <https://github.com/wangyi-fudan/wyhash>
- **Sources the enricher read:**
  - <https://github.com/wangyi-fudan/wyhash>
  - <https://github.com/wangyi-fudan/wyhash/blob/master/wyhash.h>
  - <https://github.com/wangyi-fudan/wyhash/blob/master/LICENSE>
  - <https://github.com/wangyi-fudan/wyhash/issues/153>
  - <https://github.com/wangyi-fudan/wyhash/issues/130>
- **Raw records:** [data/wave0-seed/verified.json](../../../data/wave0-seed/verified.json) (id `https://github.com/wangyi-fudan/wyhash`) · [data/wave0-seed/enrich/raw/github_com_wangyi_fudan_wyhash.json](../../../data/wave0-seed/enrich/raw/github_com_wangyi_fudan_wyhash.json) (enrichment confidence 0.8)

</details>
