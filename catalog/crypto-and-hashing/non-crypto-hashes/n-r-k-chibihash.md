# ChibiHash

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Non-cryptographic hashes](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `Unlicense` · 🟢 active

> 82-line public-domain C header 64-bit hash; about 1.5x XXH64 bulk throughput and a third fewer cycles on short keys.

| | |
|---|---|
| **Beats** | xxHash (xxhash64), CityHash (city64) |
| **Claimed result** | chibihash64: 24.20 GiB/s bulk vs xxhash64's 15.10 and city64's 18.30 (\~1.3-1.6x); 34 cycles/hash small-key vs xxhash64's 50 and spooky64's 70 (README benchmark table, made via smhasher3) |
| **Workload** | SMHasher3 speed test: large-buffer bulk hashing (GiB/sec) and small-key latency (cycles/hash) for 1-32 byte keys |
| **Metric** | throughput |
| **Adoption** | 147 stars |
| **Last commit** | 2026-04-21 |
| **Links** | [repository](https://github.com/N-R-K/ChibiHash) · [benchmark](https://github.com/N-R-K/ChibiHash) |

## Verdict

The README table is the author's own SMHasher3 run (CPU, compiler and flags not stated, cycles scaled to 3.5 GHz). It shows ChibiHash v2 at 24.20 GiB/s bulk against 15.10 for xxhash64 and 18.30 for city64, and 34 cycles per small key against 50 and 47. The independent SMHasher3 results page (tool releases from 2025-10 to 2026-08, hardware also unstated) supports the ordering. It has ChibiHash2 at 6.15 bytes/cycle and 34.53 cycles, against 3.99/52.60 for XXH-64 and 4.75/51.89 for CityHash-64: about 1.5x and 1.3x faster in bulk, and about a third fewer cycles on 1-32 byte keys.

## Use it when

- C or C++ code on legacy XXH64 or CityHash64 that wants a smaller, faster replacement. On the independent SMHasher3 results page it hashes bulk data at 6.15 bytes/cycle, against 3.99 for XXH-64 and 4.75 for CityHash-64. It averages 34.53 cycles on 1-32 byte keys, against about 52 for both.
- Hash tables, dedup or bloom filters over short string keys, as a drop-in upgrade from FNV-1a. On the same page FNV-1a-64 needs 73 cycles per short key and fails 230 of 235 tests; ChibiHash2 passes all 250.
- Code that must give the same hash on every host, including big-endian, strict-alignment, WASM or embedded targets. It uses no intrinsics, no SIMD and no 128-bit multiply.
- Projects that want to vendor a hash with no build system, no dependencies and no license paperwork. It is one public-domain header of about 80 lines.
- Incremental hashing of data that arrives in pieces (network buffers, file chunks) without allocating. The streaming header keeps a 32-byte buffer, and a test checks it against the one-shot function for every split of inputs up to 256 bytes and for chunk sizes 1-65.

## Skip it when

- Hash tables exposed to attacker-chosen keys. There is no secret per-process key (the caller passes a plain uint64 seed), and the README itself says to use SipHash against collision attacks.
- Maximum throughput on 64-bit CPUs. On the same SMHasher3 page, XXH3-64 does about 2.1x the bulk bytes/cycle (12.82 vs 6.15) and is a little faster on short keys (30.69 vs 34.53 cycles). rapidhash also passes all 250 tests and beats it on both (8.82 bytes/cycle, 30.41 cycles).
- Checksums or fingerprints that need strong collision bounds or 128-bit output. There is only a 64-bit variant, the README warns that its minimal mixing should give more collisions than xxhash64, and the author's article says the design has no mathematical foundation and was tuned until the tests passed.
- Persisted or cross-language hashes where the version can drift. v1 and v2 give different values and there are no tagged releases. The port list shows the Go, Python and constexpr-C++ ports still on v1, while the Rust, Zig, Haskell and Java (hash4j) ports are on v2.
- Organizations that need a LICENSE file or a patent grant. The repo has no LICENSE file; the only license is an Unlicense public-domain dedication in the header comments.

## How it is fast

The bulk loop keeps four 64-bit lanes and eats 32 bytes per iteration. Each lane does (stripe + h[i]) \* K, then adds a rotated copy of the stripe into the next lane, which breaks dependency chains so the four multiplies overlap. It uses only the low 64 bits of a 64x64 multiply, never a 128-bit product. Tails of fewer than 8 bytes are read with overlapping 4-byte loads, or first/middle/last bytes, in the style of wyhash, and the result goes through a short rotate-xor-multiply finalizer. Loads are shift-or byte assembly that GCC and Clang compile to one unaligned load on x86, so the output does not depend on endianness or alignment.

## Compared with alternatives

Pick ChibiHash over xxHash when you would otherwise ship XXH64: it is faster, much smaller and passes all 250 SMHasher3 tests where XXH-64 fails 9. Pick XXH3 when bulk speed matters most. Pick it over wyhash or rapidhash only when you need code that is portable, endian-neutral and free of 128-bit multiplies (the README footnotes that rapidhash needs the full 128-bit product), since rapidhash is faster on every SMHasher3 metric and wyhash fails 15 tests.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (stdint.h and stddef.h only) |
| **Minimum toolchain** | C99 (static inline, UINT64_C, for-loop declarations). It also compiles as C++: etc/test.cpp builds both headers with g++ -Wall -Wextra. |
| **Platforms** | any; output is endianness-independent. It needs a 64-bit integer multiply, which is emulated and slower on 32-bit CPUs. |
| **Thread safety** | Not documented. From the source, the one-shot function is pure with no global state, and the streaming ChibiHash64Ctx is a caller-owned value, so it is safe as long as each context stays on one thread. |
| **Drop-in for the baseline** | partial — the one-shot signature matches XXH64's (ptr, len, seed) -&gt; uint64 shape, so swapping call sites is trivial. The hash values differ, so stored XXH64 or City64 hashes must be recomputed, and the streaming API is not XXH64_state-compatible. |

## Gotchas

- chibihash64-stream.h uses uint64_t, uint8_t and ptrdiff_t but includes neither &lt;stdint.h&gt; nor &lt;stddef.h&gt;. Include those, or chibihash64.h, first, or the header will not compile on its own.
- chibihash64_append takes a non-const void \*keyIn, so passing const buffers needs a cast: an error in C++ and a discarded-qualifier warning in C. The header's own usage example passes string literals.
- The README's GiB/s numbers are SMHasher3 rdtsc cycles scaled to a nominal 3.5 GHz, not wall-clock time, and v1's article numbers came from the original SMHasher at 3 GHz (author, issue #6). The independent run shows 6.24 bytes/cycle, about 20.3 GiB/s, against the README's 24.20. Compare ratios, not absolute numbers.
- The seed is the caller's responsibility. Every call with the same seed gives the same hash, so randomizing it per process or per table is up to you.

## Known shortcomings

- Beats XXH64 and CityHash64 only; XXH3 is faster. Unlicense is declared in the source header only (no LICENSE file).
- README numbers are the author's own rdtsc run scaled to 3.5 GHz with no CPU or compiler named; independent SMHasher3 measures 20.3 GiB/s vs README 24.2. XXH3 is \~2.1x faster in bulk and rapidhash is faster everywhere. No seed randomization, no tags, v1 and v2 outputs differ. Streaming header lacks stdint/stddef includes.

## Caveats and trade-offs

There is no LICENSE file, so GitHub reports no license. The chibihash64.h header carries an Unlicense public-domain dedication, which has no patent grant. The README numbers come from the author's own smhasher3 run with no CPU, compiler or flags stated. The independent SMHasher3 results page (gitlab.com/fwojcik/smhasher3, results/README.md) confirms the win over XXH-64 and CityHash-64, and ChibiHash2 passes all 250 tests there. The baseline is legacy XXH64: on the same page XXH3-64 is about 2x faster in bulk (12.82 bytes/cycle) and slightly faster on short keys (30.69 cycles), and rapidhash beats ChibiHash2 on both measures.

minimal mixing means weaker collision resistance than xxhash64; not for adversarial/hash-flooding contexts; no SIMD/hardware-specific instructions so portability is a design goal, not raw peak speed

## Maintenance

Single-author and quiet: v2 landed in Nov 2024 and the next activity was the streaming header in Apr 2026 (last commit 2026-04-21). There are no tagged releases, no open issues and 147 stars. The public-domain header is small enough to copy into a tree and freeze.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** The README table (the author's own smhasher3 run, no CPU, compiler or flags given) matches the claim exactly; on its own that would be C. B holds because the independent SMHasher3 results page lists ChibiHash2 at 6.15 bytes/cycle bulk and 34.53 avg cycles (1-32 B), ahead of XXH-64 (3.99 / 52.60) and CityHash-64 (4.75 / 51.89). It is not A because that page does not state the compiler, flags or CPU.
- **Verifier notes:** The claimed numbers appear verbatim in the README (24.20 vs 15.10 / 18.30 GiB/s; 34 vs 50 cycles/hash). The license was confirmed from the source header, not a LICENSE file. The last commit (2026-04-21), stars (147) and not-a-fork status all check out.
- **Fields the verifier corrected:** `license`, `caveats`
- **Shortcomings recorded by:** SMHasher3: ChibiHash bulk 20.3 GiB/s (README claims 24.2).
- **Pages the verifier opened:**
  - <https://github.com/N-R-K/ChibiHash>
  - <https://github.com/N-R-K/ChibiHash#readme>
  - <https://github.com/N-R-K/ChibiHash/blob/master/chibihash64.h>
  - <https://gitlab.com/fwojcik/smhasher3/-/blob/main/results/README.md>
  - <https://gitlab.com/fwojcik/smhasher3/-/raw/main/results/README.md>
  - <https://gitlab.com/fwojcik/smhasher3/-/raw/main/results/SpeedAll.txt>
  - <https://gitlab.com/fwojcik/smhasher3/-/raw/main/results/raw/ChibiHash2.txt>
- **Sources the enricher read:**
  - <https://github.com/N-R-K/ChibiHash>
  - <https://github.com/N-R-K/ChibiHash#readme>
  - <https://github.com/N-R-K/ChibiHash/blob/master/chibihash64.h>
  - <https://github.com/N-R-K/ChibiHash/blob/master/chibihash64-stream.h>
  - <https://github.com/N-R-K/ChibiHash/blob/master/etc/test.cpp>
  - <https://github.com/N-R-K/ChibiHash/blob/master/etc/test_stream.c>
  - <https://github.com/N-R-K/ChibiHash/blob/master/old_versions/chibihash64-v1.h>
  - <https://api.github.com/repos/N-R-K/ChibiHash>
  - <https://api.github.com/repos/N-R-K/ChibiHash/git/trees/HEAD?recursive=1>
  - <https://api.github.com/repos/N-R-K/ChibiHash/commits?per_page=30>
  - <https://github.com/N-R-K/ChibiHash/issues?q=is%3Aissue>
  - <https://github.com/N-R-K/ChibiHash/issues/2>
  - <https://github.com/N-R-K/ChibiHash/issues/4>
  - <https://github.com/N-R-K/ChibiHash/issues/6>
  - <https://nrk.neocities.org/articles/chibihash>
  - <https://gitlab.com/fwojcik/smhasher3/-/raw/main/results/README.md>
  - <https://gitlab.com/fwojcik/smhasher3/-/raw/main/results/raw/ChibiHash2.txt>
  - <https://hn.algolia.com/api/v1/search?query=chibihash&tags=story>
  - <https://hn.algolia.com/api/v1/items/42168576>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/n-r-k/chibihash`) · [data/wave7/enrich/raw/github_com_n_r_k_chibihash.json](../../../data/wave7/enrich/raw/github_com_n_r_k_chibihash.json) (enrichment confidence 0.84)

</details>
