# AquaHash

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Non-cryptographic hashes](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `Apache-2.0` · 🔴 abandoned

> Single-header AES-NI 128-bit hash: about 4x XXH64 bulk throughput in SMHasher3, but fails 55/250 quality tests.

| | |
|---|---|
| **Beats** | xxHash (xxhash64) |
| **Claimed result** | SMHasher3 results summary: AquaHash bulk 15.84 bytes/cycle vs XXH-64 3.99 and wyhash 6.98 (about 4x and 2.3x, derived from page data). The margin over XXH3-64 (12.82) is only about 1.24x, derived from page data. On small keys (1-32 bytes, avg cycles) AquaHash scores 34.31, which beats XXH-64 (52.60) but is slower than wyhash (29.31). Own README: 'substantially outperforms most common hash functions at all key sizes', about 15 bytes/cycle bulk, and a cycles-per-hash graph up to 256-byte keys vs xxhash64 and FarmHash on Skylake. |
| **Workload** | Bulk hashing throughput (AES-intrinsics-based); README's own graph also covers small-key sizes vs xxhash64 and FarmHash on Skylake |
| **Metric** | throughput |
| **Hardware** | Intel Skylake (author's own graph); unstated in SMHasher3 summary table |
| **Adoption** | 85 stars |
| **Last commit** | 2019-03-06 |
| **Links** | [repository](https://github.com/jandrewrogers/AquaHash) · [benchmark](https://gitlab.com/fwojcik/smhasher3/-/blob/main/results/README.md) |

## Verdict

SMHasher3's results summary (CPU and compiler not stated; GiB/s figures are converted at a nominal 3.5 GHz) measures AquaHash at 15.84 bytes/cycle bulk against 3.99 for XXH-64 (about 4x) and 12.82 for XXH3-64 (about 1.24x), and at 34.31 cycles average on 1-32-byte keys against 52.60 for XXH-64 and 29.31 for wyhash. The author's Skylake graph against xxhash64 and FarmHash gives no compiler or flags, and a 2019 third-party fork benchmark (clang 8) timed its aquahash command at 131.6 ms against 163.2 ms for xxhsum on a 100 MB+ file, about 1.24x including I/O.

## Use it when

- Non-adversarial bulk checksums, deduplication or content fingerprinting of large buffers on x86-64 with AES-NI, when bytes/cycle is the bottleneck (SMHasher3: 15.84 bytes/cycle vs 12.82 for XXH3-64 and 3.99 for XXH-64).
- As a fast pre-filter where every hash match is confirmed by a byte comparison, so extra collisions cost time but never correctness.
- Clang-built, x86-only codebases that want a tiny Apache-2.0 header with no dependencies to vendor and patch.
- As a compact reference point when studying AES-round hash constructions next to Meow hash.

## Skip it when

- Hash tables, or any use that needs good distribution on structured keys. SMHasher3 finds full 128-bit collisions on the Sparse, Cyclic and Permutation keysets: for example, 405 collisions among 22.4M 64-byte keys with at most 3 bits set, where 0 are expected. An open 2019 issue (#7) reports 3,488,136 collisions in a brute-force test that should give about 312.
- Short keys: its 34.31 cycles average on 1-32 bytes is slower than wyhash (29.31), XXH3-64 (30.69) and a5hash (26.91) in the same SMHasher3 table.
- Untrusted input or HashDoS defence: the author says it is not suitable for cryptographic use, and it fails SMHasher3's Seed, SeedSparse and SeedBlockLen tests.
- ARM or any CPU without AES-NI: the code calls x86 intrinsics directly and has no fallback path.
- Anything that needs a maintained dependency or an unpatched GCC build: the upstream header does not compile with GCC (issue #1, open since 2019), issues are now disabled, and there have been no commits since 2019-03-06.

## How it is fast

Each 16-byte input block becomes the round key of a single AES round (_mm_aesenc_si128), so the whole per-block cost is one AES instruction. Keys of 64 bytes or more are spread across four independent 128-bit lanes (a 512-bit block), which keeps the AES units pipelined; the lanes are mixed and reduced with a few AES rounds only at the end. Keys under 64 bytes take a single-lane path: the 1-15-byte tail is XORed in with constant-padded vectors and three AES rounds finish the hash, with no cross-lane reduction. The author's blog gives 15 bytes/cycle bulk on Skylake and about 25 cycles per hash at the smallest key sizes.

## Compared with alternatives

Pick it over Meow hash or xxHash's XXH3 only when raw x86 bulk throughput on non-adversarial data matters more than hash quality: SMHasher3 puts AquaHash at 15.84 bytes/cycle against Meow's 12.43 and XXH3-64's 12.82, but Meow passes all 250 tests and XXH3 is portable and maintained. For short keys, wyhash and a5hash are both faster and better tested, so do not pick AquaHash there.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | None beyond the x86 intrinsic headers &lt;smmintrin.h&gt; and &lt;wmmintrin.h&gt;. |
| **Minimum toolchain** | Not documented. The features used (constexpr, brace-initialised member arrays) need C++11, and the author says the code came from a C++17 codebase. The author says it compiles cleanly with Clang in strict mode. Upstream fails on GCC (reported on 4.9 and 8.2.1) because LargeKeyAlgorithm declares `__m128 block[4]` where `__m128i` is needed. AES codegen must be enabled (-maes or a suitable -march). MSVC is not documented. |
| **Platforms** | x86/x86-64 with AES-NI only. There is no ARM or portable fallback. |
| **Thread safety** | Not documented. The static Hash/SmallKeyAlgorithm/LargeKeyAlgorithm functions keep no shared state (read from source). An incremental AquaHash object is unsynchronised. |
| **Drop-in for the baseline** | no |

## Gotchas

- The result is a by-value __m128i. Writing it through a cast pointer into an unaligned buffer can crash: issue #3 reports SMHasher's BulkSpeed test segfaulting this way. Store it with _mm_storeu_si128.
- Upstream has no std::hash-style adapter and no 64-bit output. For hash tables you must pull 64 bits out of the __m128i yourself (the hungptit fork adds such a wrapper).
- After Finalize() the incremental object is in an undefined state and must be re-Initialize()d. Only an assert guards against double finalization, so release builds get no check.
- Hash() switches from the small-key to the large-key algorithm at 64 bytes, and calling a component function directly outside its intended range gives values that differ from Hash(). Tail bytes are read through reinterpret_cast'ed uint64/32/16 pointers: these are unaligned, aliasing-violating loads that the author's x86 targets tolerate.

## Known shortcomings

- Unmaintained since 2019-03-06. Bulk lead over XXH3-64 is only \~1.24x (15.84 vs 12.82 bytes/cycle); on small keys it is slower than wyhash (34.31 vs 29.31 cycles). Needs AES-NI.
- Quality failures: SMHasher3 fails 55 of 250 tests, including full 128-bit collisions on Sparse/Cyclic/Permutation keys (405 in 22.4M 64-byte keys, 0 expected) and the Seed tests; issue #7 (open since 2019) reports 3,488,136 collisions vs \~312 expected. Header does not compile on GCC (__m128 vs __m128i, issue #1); Clang only. x86 AES-NI only, no fallback; returns __m128i and an unaligned store segfaults (#3); no 64-bit or std::hash adapter. Repo issues disabled; hungptit's fork has the GCC fix.

## Caveats and trade-offs

Fails 55 of 250 SMHasher3 tests (195/250 passed), a notable quality concern despite the speed; needs AES-NI; no commits since the 2019-03-06 v1.0 release; the README graph (Skylake) gives no compiler or flags and has no public bench harness; the bulk lead shrinks to about 1.24x against the modern XXH3-64

requires AES-NI intrinsics; header-only C++; same author as MetroHash (jandrewrogers, checked separately but had no usable numeric benchmark)

## Maintenance

Abandoned since the 2019-03-06 v1.0 commit: issues are disabled and the GCC-build and collision-rate reports were never answered with fixes. It is Apache-2.0 and one 440-line header, so it is easy to vendor and patch; the hungptit fork already fixes the GCC error.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** The SMHasher3 independent results summary lists AquaHash at 15.84 bytes/cycle bulk against XXH-64 3.99 and wyhash 6.98. No compiler or CPU model is stated there, so it cannot be A. The README graph against xxhash64/FarmHash on Skylake is first-party, has no flags, and has no public bench code.
- **Verifier notes:** The last commit is 2019-03-06; the record's 2019-08-12 was GitHub's pushed_at. The caveats 'predates wyhash' (the wyhash GitHub repo was created 2019-03-06, the same day) and 'never reached a stated v2.0' (no source mentions v2.0) were unsupported and have been removed. License Apache-2.0, 85 stars and abandoned status are confirmed.
- **Fields the verifier corrected:** `claimed_speedup`, `last_commit`, `caveats`
- **Shortcomings recorded by:** SMHasher3 summary: bulk 15.84 B/cycle vs XXH3-64 12.82, wyhash 6.98, XXH-64 3.99; small keys 34.31 cycles vs wyhash 29.31.
- **Pages the verifier opened:**
  - <https://gitlab.com/fwojcik/smhasher3/-/blob/main/results/README.md>
  - <https://gitlab.com/fwojcik/smhasher3/-/raw/main/results/README.md>
  - <https://gitlab.com/fwojcik/smhasher3/-/raw/main/results/raw/AquaHash.txt>
  - <https://github.com/jandrewrogers/AquaHash>
  - <https://raw.githubusercontent.com/jandrewrogers/AquaHash/master/aquahash.png>
  - <http://www.jandrewrogers.com/2019/03/06/aquahash/>
  - <https://github.com/wangyi-fudan/wyhash>
- **Sources the enricher read:**
  - <https://github.com/jandrewrogers/AquaHash>
  - <https://github.com/jandrewrogers/AquaHash/blob/master/aquahash.h>
  - <https://github.com/jandrewrogers/AquaHash/pull/5>
  - <https://github.com/jandrewrogers/AquaHash/pull/6>
  - <https://web.archive.org/web/20201125105502/https://github.com/jandrewrogers/AquaHash/issues/1>
  - <https://web.archive.org/web/20201125105503/https://github.com/jandrewrogers/AquaHash/issues/2>
  - <https://web.archive.org/web/20201125105504/https://github.com/jandrewrogers/AquaHash/issues/3>
  - <https://web.archive.org/web/20201125105504/https://github.com/jandrewrogers/AquaHash/issues/4>
  - <https://web.archive.org/web/20201125105505/https://github.com/jandrewrogers/AquaHash/issues/7>
  - <https://web.archive.org/cdx/search/cdx?url=github.com/jandrewrogers/AquaHash/issues*>
  - <http://www.jandrewrogers.com/2019/03/06/aquahash/>
  - <https://gitlab.com/fwojcik/smhasher3/-/raw/main/results/README.md>
  - <https://gitlab.com/fwojcik/smhasher3/-/raw/main/results/raw/AquaHash.txt>
  - <https://github.com/hungptit/AquaHash>
  - <https://github.com/hungptit/AquaHash/blob/master/benchmark.md>
  - <https://github.com/hungptit/AquaHash/blob/master/benchmark/benchmark.md>
  - <https://github.com/hungptit/AquaHash/blob/master/benchmark/CMakeLists.txt>
  - <https://github.com/hungptit/AquaHash/blob/master/src/aquahash.h>
  - <https://github.com/hungptit/AquaHash/blob/master/src/interface.h>
  - <https://github.com/hungptit/AquaHash/blob/master/docs/slides.md>
  - <https://hn.algolia.com/api/v1/search?query=aquahash>
  - <https://releases.llvm.org/10.0.0/tools/clang/docs/ReleaseNotes.html>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/jandrewrogers/aquahash`) · [data/wave7/enrich/raw/github_com_jandrewrogers_aquahash.json](../../../data/wave7/enrich/raw/github_com_jandrewrogers_aquahash.json) (enrichment confidence 0.8)

</details>
