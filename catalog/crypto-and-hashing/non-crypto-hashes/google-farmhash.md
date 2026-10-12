# FarmHash

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Non-cryptographic hashes](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `MIT` · 🟢 active

> Google's CityHash successor. Its SSE4.1 32-bit hash is 3.9x City32 and \~6% faster than XXH3 on large x86-64 inputs.

| | |
|---|---|
| **Beats** | CityHash, xxHash (xxh3) |
| **Claimed result** | FarmHash32 22136.14 MiB/s vs xxh3 20853.74 MiB/s (\~6% faster) and vs its own predecessor CityHash (City32 5745.83 MiB/s, \~285% faster) (derived from page data) |
| **Workload** | SMHasher bulk-hash speed test, 262144-byte keys; FarmHash32 uses the SSE4.1/AVX code path, run alongside CityHash and xxh3 on the same machine/build in rurban/smhasher. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 5 3350G 3.6GHz; requires x64 SSE4.1/AVX for the fast FarmHash32 path |
| **Compiler and flags** | CMake Release build, -march=native per rurban/smhasher; FarmHash's own build docs separately recommend -mavx -maes -O3 |
| **Adoption** | 659 stars; historically Google's successor to CityHash, widely vendored (e.g. in Abseil-adjacent and RocksDB-era codebases) |
| **Last commit** | 2026-06-05 |
| **Links** | [repository](https://github.com/google/farmhash) · [benchmark](https://github.com/rurban/smhasher/blob/master/README.md) |

## Verdict

rurban's SMHasher README table (AMD Ryzen 5 3350G, CMake Release with -march=native, compiler version not stated) measured rurban's vendored copy of Google FarmHash32WithSeed at 22,136 MiB/s on 262,144-byte keys. That compares with 20,854 MiB/s for xxh3 (\~1.06x, 32-bit vs 64-bit output) and 5,746 MiB/s for City32 (\~3.85x). The same run shows FarmHash32 slower than xxh3 on 1-32 byte keys (46.75 vs 29.46 cycles/hash) and the seeded 64/128-bit FarmHash variants slower than xxh3/xxh128. No C++ std hash was compared, and FarmHash's own README and NEWS give no numbers.

## Use it when

- You must reproduce existing FarmHash values, such as BigQuery's FARM_FINGERPRINT (documented as FarmHash Fingerprint64, 'will never change') or other Google/TensorFlow-derived data, where the Fingerprint\* functions are the portable contract.
- You are moving C++ code off CityHash and want the same one-shot API style: Fingerprint128/Hash128 keep CityHash128 v1.1.1 output, and Hash32 on an x86-64 SSE4.1 build is about 3.85x City32's bulk throughput in the same SMHasher run.
- In-process 32-bit hashing of large buffers (512 B and up) on x86-64 machines you build for with -msse4.1 or -mavx, where the hash is never persisted or sent across machines.
- You already vendor it, for example through TensorFlow, whose build files pull in farmhash, and a \~6% bulk edge over XXH3 is enough reason not to add another dependency.

## Skip it when

- Small keys: 46.75 cycles/hash on 1-32 byte keys vs 29.46 for xxh3, 28.91 for wyhash and 22.04 for rapidhash, and 258.73 vs 220.07 cycles in SMHasher's hash-map column against xxh3. It also compiles to 11,489 bytes of code vs 744 for xxh3.
- You need 64- or 128-bit seeded output: seeded FarmHash64 (12,930 MiB/s) and FarmHash128 (14,454 MiB/s) lose to xxh3 (20,854) and xxh128 (19,260) on the same run, and FarmHash64 even loses to City64 (14,390).
- Stored or cross-machine hashes built on Hash\*: output depends on CPU flags, pointer width, endianness and NDEBUG. Issue #37 (open) reports wrong Hash64/Hash128 values on FreeBSD, and rurban calls FarmHash 'not portable, too machine specific'.
- ARM/aarch64 or builds without SSE4.1: src/farmhash.cc has no NEON code and falls back to the scalar farmhashmk/farmhashxo paths, so the measured win does not apply. Big-endian is 'only lightly tested'.
- You need streaming/incremental hashing, hash-flooding resistance, or an actively developed library: there is no incremental API, the README disclaims cryptographic use, there is no tagged release (issue #31), and there have been no substantive code changes since 2019.

## How it is fast

On x86-64 builds with SSE4.1, Hash32 returns the low 32 bits of farmhashte::Hash64. For inputs of 512 bytes or more, its Hash64Long loop reads 256-byte blocks as sixteen unaligned 128-bit loads and mixes them across twelve SSE registers with 64-bit adds, XORs, _mm_mullo_epi32 multiplies and _mm_shuffle_epi8 byte shuffles. It then reduces the state with the scalar farmhashxo hash. Shorter inputs, and every seeded 64- or 128-bit call, run CityHash-lineage scalar code instead: farmhashxo/na use 64-bit multiply-rotate-xor mixing, farmhashcc is CityHash v1.1.1 and farmhashmk is Murmur3-style. The variant is chosen at compile time from the -msse4.1/-msse4.2/-maes/-mavx macros, and NEWS says AVX encoding makes the SIMD path slightly faster.

## Compared with alternatives

On the same rurban run, wyhash beats FarmHash32 on both bulk (22,641 MiB/s) and small keys (28.91 cycles), with 64-bit output and portable results. xxHash's XXH3 is much faster on small keys and portable, and gxhash, falkhash and CLHash are faster in bulk. Pick FarmHash only when you need FarmHash- or CityHash-compatible values (Fingerprint64 as in BigQuery, or Fingerprint128 = CityHash128 v1.1.1) or already vendor it.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (standard C/C++ headers; x86 intrinsic headers only when SSE/AES/AVX flags are enabled). An optional autoconf build can `make install` a library. |
| **Minimum toolchain** | Not documented. The code avoids C++11 requirements (it falls back to &lt;algorithm&gt; for std::swap) and assumes __builtin_expect unless FARMHASH_NO_BUILTIN_EXPECT is defined. Open issue #6 reports that gcc 4.3 and older lack &lt;immintrin.h&gt;. MinGW and clang+libc++ C++17 build fixes were merged in 2018-2019. |
| **Platforms** | Any 32/64-bit platform that allows unaligned reads (per the header). The fast path is x86-64 with SSE4.1, and AVX is slightly better. 32-bit x86 uses SSE4.2 (+AES-NI) variants. Other targets, including aarch64, get scalar code. Built mainly for little-endian. |
| **Thread safety** | Not documented. By inspection the hash functions are stateless: they read only const input and static const constants, so concurrent calls are safe. The optional FARMHASHSELFTEST self-test writes to stdout and calls std::exit(). |
| **Drop-in for the baseline** | partial — Fingerprint128/Hash128 equal CityHash128 v1.1.1 (rurban's FarmHash128 verification value 0x305C0D9A matches City128), and farmhashcc::Hash32 is 'equivalent to CityHash32 (v1.1.1)'. The fast Hash32 and the Hash64 variants produce different values from CityHash and XXH3, use different function names, and have no streaming API. |

## Gotchas

- Hash()/Hash32/Hash64/Hash128 values change with build flags and NDEBUG. Without NDEBUG, FARMHASH_DEBUG=1 and DebugTweak scrambles every Hash\* result, so debug and release binaries disagree. Persist only Fingerprint32/64/128.
- Seeded and unseeded entry points run different algorithms. On x86-64 with SSE4.1, Hash32 and Hash32WithSeed use the SIMD farmhashte core, but only for inputs of 512 bytes or more. Hash64 uses farmhashte only if SSE4.2 is also enabled, while Hash64WithSeed and Hash64WithSeeds always use scalar farmhashna, which is why SMHasher's seeded FarmHash64 has 42% lower bulk throughput than FarmHash32. rurban marks unseeded Hash64 POOR ('misses on final avalanche') and leaves it out of the table.
- CPU selection happens at compile time only: there is no cpuid check and no multiversioning in src/farmhash.cc, despite the README's hint. FARMHASH_ASSUME_\* forces a path, and a binary built with -mavx/-msse4.1 will fault on CPUs without them. Calling a variant namespace such as farmhashte:: when its features were not compiled in hits FARMHASH_DIE_IF_MISCONFIGURED, which deliberately writes to address len%17 and crashes.
- Hash32WithSeed has a known bad seed: SMHasher's BadSeeds test shows seed 0x2b091701 with a 16-byte all-zero key hashing to 0 (FAIL). Separately, the header's template Hash128WithSeed(const Str&, seed) calls a nonexistent 3-argument Hash128 and will not compile if instantiated, so use the (const char\*, size_t, uint128_t) overload.

## Known shortcomings

- Only FarmHash32 wins: FarmHash64/128 are slower than xxh3, CityHash64 and xxh128, and small keys are slower than xxh3. Real development stopped in 2019 (2026 commits only merge old PRs).
- Only FarmHash32 wins (low 32 bits of SSE4.1 farmhashte, SIMD only from 512 B); seeded Hash64 runs scalar farmhashna. Small keys lose (46.75 vs xxh3 29.46 cycles) and wyhash beats it in bulk and small keys in the same run. Hash\* output varies with flags/platform/NDEBUG; wrong hashes on FreeBSD (#37); only Fingerprint\* is stable. Compile-time dispatch only, no NEON; seed 0x2b091701 maps to 0; Hash128WithSeed template does not compile. Used by TensorFlow; BigQuery FARM_FINGERPRINT = Fingerprint64.

## Caveats and trade-offs

Only FarmHash32 (32-bit output, SSE4/AVX path) wins. FarmHash64 (12929.54 MiB/s) is slower than both xxh3 (20853.74) and City64 (14390.09) on bulk, and FarmHash128 (14454.12) is slower than xxh128 (19259.99). Even FarmHash32 is slower than xxh3 on small keys (46.75 vs 29.46 cycles/hash), and the xxh3 comparison is 32-bit vs 64-bit output. FarmHash's own README/NEWS make no quantified speed claim, so the win comes from the independent SMHasher table, where rurban lists FarmHash among the fastest x86_64 hashes without quality problems but notes 'not portable, too machine specific'. The 2026-06-05 last commit only merges old PRs (a README rename and a small fix); substantive development stopped in 2019.

Selects among many internal hash variants via conditional compilation/GCC multiversioning depending on target CPU features and endianness; implementation is described by its own README as 'fairly complex'; in this table only the 32-bit variant clears xxh3, and by a modest \~6% margin — FarmHash64/FarmHash128 are both slower than xxh3 on the same run.

## Maintenance

Marked active only because of the commit date: the 2026-06-05 commits merge a 2020 README rename (#39) and a 2018 'remove using namespace std' fix (#25). The last substantive code change was in 2019, there is no release tag and 15 issues are open. It is MIT-licensed and small enough to vendor as two files (farmhash.cc is 11,840 lines, mostly generated self-test tables).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** The rurban SMHasher README table (a well-known independent suite, public code, Ryzen 5 3350G) lists FarmHash32 at 22136.14 MiB/s against xxh3 20853.74 and City32 5745.83, matching the record and doc/FarmHash32.txt. It is not A because no compiler version is stated. FarmHash's own README gives no speed numbers.
- **Verifier notes:** Numbers and metadata verified (MIT, 659 stars, last commit 2026-06-05, not fork/archived, C++). The 'widely vendored (Abseil-adjacent, RocksDB-era)' wording in stars_or_usage was not checked and is left as-is. 'Active' is correct by the commit-date rule but is misleading in practice.
- **Fields the verifier corrected:** `caveats`
- **Pages the verifier opened:**
  - <https://github.com/rurban/smhasher/blob/master/README.md>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/README.md>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/doc/FarmHash32.txt>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/doc/xxh3.txt>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/doc/City32.txt>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/CMakeLists.txt>
  - <https://github.com/google/farmhash>
- **Sources the enricher read:**
  - <https://github.com/google/farmhash>
  - <https://github.com/google/farmhash/blob/master/README.md>
  - <https://github.com/google/farmhash/blob/master/NEWS>
  - <https://github.com/google/farmhash/blob/master/src/farmhash.h>
  - <https://github.com/google/farmhash/blob/master/src/farmhash.cc>
  - <https://github.com/google/farmhash/commits/master>
  - <https://github.com/google/farmhash/issues?q=is%3Aissue>
  - <https://github.com/google/farmhash/issues/37>
  - <https://github.com/google/farmhash/issues/35>
  - <https://github.com/google/farmhash/issues/24>
  - <https://github.com/google/farmhash/issues/12>
  - <https://github.com/google/farmhash/issues/6>
  - <https://github.com/google/farmhash/issues/2>
  - <https://github.com/google/farmhash/issues/20>
  - <https://github.com/google/farmhash/pull/39>
  - <https://github.com/google/farmhash/pull/25>
  - <https://github.com/rurban/smhasher/blob/master/README.md>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/README.md>
  - <https://github.com/rurban/smhasher/blob/master/main.cpp>
  - <https://github.com/rurban/smhasher/blob/master/FarmTest.cc>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/doc/FarmHash32.txt>
  - <https://docs.cloud.google.com/bigquery/docs/reference/standard-sql/hash_functions>
  - <https://github.com/search?q=repo%3Atensorflow%2Ftensorflow+farmhash&type=code>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/google/farmhash`) · [data/wave7/enrich/raw/github_com_google_farmhash.json](../../../data/wave7/enrich/raw/github_com_google_farmhash.json) (enrichment confidence 0.8)

</details>
