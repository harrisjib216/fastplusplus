# CircleHash64f

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Non-cryptographic hashes](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `Apache-2.0` · 🟢 active

> Pure-Go seeded 64-bit hash from Abseil's wyhash-style design; beats seeded XXH3 5-13% at 4-128 B, 1.4-1.8x at 192-256 B.

| | |
|---|---|
| **Beats** | XXH3 (xxHash) |
| **Claimed result** | 1.05x-1.83x faster than XXH3 on 4-256-byte inputs with a 64-bit seed: 1.34 vs 1.21 GB/s at 4 B, 5.48 vs 5.21 at 16 B (smallest gain), 10.3 vs 9.33 at 64 B, 15.0 vs 8.19 GB/s at 256 B (ratios derived from page data) |
| **Workload** | Hashing short inputs (4-256 bytes) with a 64-bit seed, comparing CircleHash64f against XXH3, XXH64 and SipHash on one machine. |
| **Metric** | throughput |
| **Hardware** | darwin_amd64, Intel Core i7-1068NG7 (the README footnote writes 'i7-1068N7'; the repo description says i7-1068NG7) |
| **Compiler and flags** | Go 1.17.7 |
| **Adoption** | 24 stars |
| **Last commit** | 2026-08-16 |
| **Links** | [repository](https://github.com/fxamacker/circlehash) · [benchmark](https://github.com/fxamacker/circlehash/blob/main/README.md) |

## Verdict

The claim is the author's README table, repeated in the v0.2.0 release notes, which add that it came from `go test -bench=. -count=20` plus benchstat. It shows seeded CircleHash64f at 1.34-15.0 GB/s against an unnamed seeded XXH3 at 1.21-8.19 GB/s on 4-256-byte inputs, under Go 1.17.7 on darwin_amd64 with an Intel i7-1068NG7. That works out to 1.05-1.13x at 4-128 B and 1.44x/1.83x at 192/256 B. The benchmark code is not published, and the rurban/smhasher README has no CircleHash row, so the speed and SMHasher-pass claims are first-party only.

## Use it when

- Pure-Go code without cgo that hashes short keys (mostly &lt;=256 bytes) and needs a seeded 64-bit digest that is identical across processes, machines and library versions, for example on-disk hash-ordered maps or persistent indexes. onflow/atree, the Flow blockchain's storage layer, uses it this way and falls back to BLAKE3 on collisions.
- Replacing SipHash as the seeded hash in a Go hash structure: the README table shows 3.7-6.8x SipHash's throughput at 4-256 B.
- Hashing pairs of uint64 (composite IDs, slab/index pairs) with Hash64Uint64x2, without building a byte slice. The digest equals Hash64 of the 16-byte little-endian encoding.
- Teams that must audit their hash: about 200 lines of optimized Go plus a 129-line reference implementation, pi-derived constants, and compatibility tests over roughly 600,000 digests on 0-16384-byte inputs.

## Skip it when

- Hashes that never leave the process, such as in-memory Go maps and sets. The runtime map and hash/maphash already handle those with per-process random seeds. CircleHash's niche is the case maphash cannot cover, because maphash seeds cannot be serialized or recreated in another process.
- Keys an attacker can choose, or anywhere HashDoS resistance matters. The seed does not prevent seed-independent multicollisions (see gotchas). The CircleHash64fx variant meant to fix this, which also adds a 128-bit seed, has been an open, unpublished issue (#15) since March 2022.
- Bulk data or inputs well above 512 bytes. The author says CircleHash64 is ideal for &lt;=512 B and publishes no numbers above 256 B, and there is no SIMD path. XXH3's SIMD long-input code is the better fit there.
- Codebases outside Go. There is no official C, C++ or Rust port, and porters have asked for simple known-answer test vectors with data (issue #23, open since 2022) because the published tests only check SHA-512 checksums over thousands of digests.
- Anything that needs 128-bit digests: CircleHash128fx (issue #16) is also unpublished.

## How it is fast

Every mixing step is the wyhash/Abseil multiply-fold: a 64x64-&gt;128-bit multiply via math/bits.Mul64, with the high and low halves XORed together. Tails use overlapping unaligned reads (two 4-byte reads for 4-8 B, two 8-byte reads for 9-16 B, three single bytes for 1-3 B), so there are no per-byte loops. Inputs of 64 bytes or less go through a separate function that has only a 16-byte loop. Longer inputs run a 64-byte loop with four independent multiplies over two state lanes. It is plain Go with no assembly: the Go 1.17+ file reads words through unsafe pointers using little-endian byte shifts, and a build-tagged reference file covers older Go.

## Compared with alternatives

Pick it when you are in pure Go and need a stable, seeded, persistable 64-bit digest of short keys without cgo. wyhash and xxHash/XXH3 are the C originals of the same ideas; in C or C++ use them directly, or rapidhash, which has a Rust port. In Rust, foldhash, aHash and rapidhash are the in-language choices and are the better fits there.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none (Go standard library only: math/bits, unsafe) |
| **Minimum toolchain** | Go 1.17 for the optimized path (go.mod: go 1.17); a build-tagged reference implementation serves Go 1.16 and older. CI tests Go 1.17 and 1.22-1.25. |
| **Platforms** | Only linux_amd64 is officially supported per the README, though CI also runs macOS, Ubuntu and Windows. The code is pure Go and builds words from bytes in little-endian order, so digests should not depend on host endianness. |
| **Thread safety** | Not documented. The API is stateless pure functions with no mutable package-level state (from source), so concurrent calls should be safe. |
| **Drop-in for the baseline** | partial — the call shape matches a one-shot seeded 64-bit XXH3 call (bytes or string plus a uint64 seed returns a uint64), but digests differ, so every persisted hash changes. There is no streaming/hash.Hash64 interface and no 128-bit variant. |

## Gotchas

- Multiply-by-zero weakness, confirmed with a Python port of the source that matches the repo's 65,536-digest known-answer checksum: when an 8-byte little-endian word that is XORed with the constant pi1 (0x13198A2E03707344) equals pi1, the product is zero. Every 9-16-byte input whose first 8 bytes are pi1 hashes to 0 under every seed, including Hash64Uint64x2(pi1, x, seed). A 16-byte block that starts with pi1 also erases all earlier input and the seed, so same-length inputs that share everything after that block collide for all seeds. The README describes CircleHash64fx as the fix, but fx is not shipped.
- The README says CircleHash64fx 'will replace CircleHash64f as the default', and issue #25 plans an API refactor before v1.0. Hash64 is documented as CircleHash64f-compatible, so pin v0.3.0 and add a regression test on digests if they are persisted (onflow/atree does both).
- Methodology: no Benchmark functions are published. The README table's XXH3 implementation is unnamed; the author's earlier atree#103 evaluation used github.com/zeebo/xxh3. The table's XXH3 throughput falls from 11.6 GB/s at 128 B to 8.19 GB/s at 256 B, which accounts for most of the headline 1.83x. The author's atree write-up says such slowdowns at larger sizes 'are not a typo'.
- The Go 1.17+ file uses unsafe pointer arithmetic to read slice and string data. Hash64 on a nil or empty slice is safe because no bytes are read.

## Known shortcomings

- Real gain over XXH3 ranges 1.05x-1.83x (only 1.05x at 16 bytes); no benchmark code published, and the XXH3 implementation used is not named (i7-1068NG7). Go library.
- Gain is only 1.05-1.13x at 4-128 bytes; the 1.83x rests on the 256-byte row where XXH3 itself dips. Seed-independent multicollisions (from code reading, confirmed with a port against the repo's test vectors): a word equal to pi1 zeroes the multiply, so 9-16 byte inputs starting with pi1 hash to 0 under any seed, so it is not HashDoS-safe. The fx and 128-bit variants have been unpublished since 2022; code frozen at v0.3.0; only linux_amd64 officially supported; used in production by onflow/atree.

## Caveats and trade-offs

No Benchmark function exists in the repo (circlehash64_test.go has correctness tests only), so the README table cannot be reproduced from published code. It is a single machine and apparently a single run. The XXH3 implementation is not named; since the benchmark ran under Go 1.17.7 it is probably a Go port, but that is unconfirmed. The author notes CircleHash64 targets inputs &lt;= 512 bytes and gives no numbers above 256 bytes.

Go-only implementation (no C/C++ port located); CircleHash64fx variant trades some speed for a 128-bit seed and protection against multiply-by-zero state loss. Author explicitly says 'for best results, run your own benchmarks.'

## Maintenance

The algorithm and code are frozen since v0.3.0 (March 2022; the last source edit was lint in August 2024), and 2025-2026 commits are dependabot/CI bumps. Still, it is Apache-2.0 with zero dependencies, digests are declared stable, and it runs in production in onflow/atree and the wider Flow Go stack, so depending on or vendoring v0.3.0 is low-risk. The promised fx and 128-bit variants remain unpublished.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README 'Speed: Hash Short Inputs with 64-bit Seed' table compares CircleHash64f against XXH3, with Go version and CPU stated. No benchmark code is published (circlehash64_test.go has only Test functions, no Benchmark\*), and the XXH3 implementation is not named, so these are first-party numbers without methodology: C.
- **Verifier notes:** The numbers match the README, but at 16 bytes the gain is only 1.05x, so the low end was rounded up. Metadata checks out: Apache-2.0, 24 stars, last commit 2026-08-16, active, not a fork. This is a Go library; the XXH3 implementation used as the baseline is unnamed (probably a Go port, unconfirmed).
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/fxamacker/circlehash>
  - <https://github.com/fxamacker/circlehash/blob/main/README.md>
  - <https://github.com/fxamacker/circlehash/blob/main/circlehash64_test.go>
  - <https://github.com/fxamacker/circlehash/blob/main/LICENSE>
  - <https://github.com/fxamacker/circlehash/blob/main/go.mod>
- **Sources the enricher read:**
  - <https://github.com/fxamacker/circlehash>
  - <https://github.com/fxamacker/circlehash/blob/main/README.md>
  - <https://github.com/fxamacker/circlehash/blob/main/circlehash64.go>
  - <https://github.com/fxamacker/circlehash/blob/main/circlehash64_ref.go>
  - <https://github.com/fxamacker/circlehash/blob/main/utils.go>
  - <https://github.com/fxamacker/circlehash/blob/main/salts.go>
  - <https://github.com/fxamacker/circlehash/blob/main/go.mod>
  - <https://github.com/fxamacker/circlehash/blob/main/circlehash64_test.go>
  - <https://github.com/fxamacker/circlehash/blob/main/.github/workflows/ci.yml>
  - <https://github.com/fxamacker/circlehash/commits/main>
  - <https://github.com/fxamacker/circlehash/issues/15>
  - <https://github.com/fxamacker/circlehash/issues/16>
  - <https://github.com/fxamacker/circlehash/issues/17>
  - <https://github.com/fxamacker/circlehash/issues/23>
  - <https://github.com/fxamacker/circlehash/issues/25>
  - <https://github.com/fxamacker/circlehash/pull/8>
  - <https://github.com/fxamacker/circlehash/releases/tag/v0.3.0>
  - <https://github.com/fxamacker/circlehash/releases/tag/v0.2.0>
  - <https://github.com/fxamacker/circlehash/releases/tag/v0.1.0>
  - <https://github.com/onflow/atree/blob/main/go.mod>
  - <https://github.com/onflow/atree/blob/main/hash.go>
  - <https://github.com/onflow/atree/blob/main/map.go>
  - <https://github.com/onflow/atree/issues/103>
  - <https://github.com/onflow/atree/issues/199>
  - <https://github.com/onflow/atree/issues/243>
  - <https://github.com/zeebo/xxh3>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/README.md>
  - <https://raw.githubusercontent.com/golang/go/master/src/hash/maphash/maphash.go>
  - <https://hn.algolia.com/api/v1/search?query=circlehash>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/fxamacker/circlehash`) · [data/wave7/enrich/raw/github_com_fxamacker_circlehash.json](../../../data/wave7/enrich/raw/github_com_fxamacker_circlehash.json) (enrichment confidence 0.55)

</details>
