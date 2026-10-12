# SeaHash

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Non-cryptographic hashes](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Rust` · `MIT` · 🟡 stale

> Portable, no_std Rust 64-bit non-crypto hash; \~11x FNV-1a and \~16% over MurmurHash3 bulk, but slower than xxHash64/XXH3.

| | |
|---|---|
| **Beats** | FNV-1a / FNV-64 and MurmurHash3 (large-buffer bulk throughput); NOT xxHash, MetroHash or CityHash, which the independent SMHasher run shows are faster |
| **Claimed result** | Author (docs.rs 2.0.0 / README): 'around 3-20% improvement' over xxHash and MetroHash with no xxHash/MetroHash numbers shown; 5.9-6.7 GB/s on a '2.5 GHz CPU' vs CityHash \~1 GB/s, MurmurHash \~2.6 GB/s, FNV \~0.5 GB/s. Independent SMHasher (C port, bulk MiB/s): SeaHash 8240.58 vs FNV1a 754.70 / FNV64 747.70 (\~11x, derived from page data) and Murmur3F 7104.08 (\~1.16x, derived from page data), but SLOWER than xxHash64 11176.72 (\~1.36x slower), metrohash64 14209.14, City64 14390.09 and xxh3 20853.74. Small keys: 58.61 cycles/hash vs FNV1a 75.28, Murmur3F 52.69, xxHash64 49.67. |
| **Workload** | SMHasher bulk speed test (262144-byte keys, alignments 0-7, averaged) plus small-key test (1-31 byte keys, cycles/hash); the author's docs.rs figures give no dataset or size |
| **Metric** | throughput |
| **Hardware** | SMHasher default table: AMD Ryzen 5 3350G 3.6GHz (label from SMHasher README); author's own figures: unspecified '2.5 GHz CPU' |
| **Adoption** | 4 GitLab stars; crates.io 153,332,761 total downloads, 192 reverse dependencies (checked 2026-09-26) |
| **Last commit** | 2023-10-25 |
| **Links** | [repository](https://gitlab.redox-os.org/redox-os/seahash) · [benchmark](https://github.com/rurban/smhasher) |

## Verdict

The only independent numbers are from rurban/SMHasher, which tests a C port (seahash.c, seed XORed into lane a) on its default AMD Ryzen 5 3350G table with no compiler or flags stated. Bulk speed on 256 KiB keys was 8,240.58 MiB/s versus 754.70 for FNV1a (\~11x) and 7,104.08 for Murmur3F (\~1.16x), but it lost to xxHash64 (11,176.72) and xxh3 (20,853.74). On small keys it averaged 58.61 cycles/hash, beating FNV1a (75.28) but not Murmur3F (52.69); the Rust crate's own criterion bench times SeaHash alone.

## Use it when

- You are replacing FNV-1a/FNV-64 or byte-at-a-time hashing of multi-KB buffers in Rust: SMHasher's bulk test puts it at about 8.2 GB/s versus about 0.75 GB/s for FNV.
- You need a hash value that is the same on little- and big-endian and on 32- and 64-bit targets (for example content checksums or dedup keys persisted to disk), and you can pin the crate's major version.
- no_std or embedded Rust where you want zero runtime dependencies, no unsafe SIMD paths, and a small auditable codebase.
- You already have data or file formats keyed by SeaHash values and need a maintained-enough Rust implementation to keep reading them.

## Skip it when

- Raw speed is the goal: in the same SMHasher table xxHash64 (11,177 MiB/s), MetroHash64, City64 and XXH3 (20,854 MiB/s) are all faster in bulk, which contradicts the README's '3-20% faster than xxHash/MetroHash' claim.
- Small keys: SMHasher averages 58.6 cycles/hash for 1-31 byte keys, worse than MurmurHash3F (52.7) and xxHash64 (49.7); keys whose length is not a multiple of 8 cost about 61 cycles versus 36-41 for 8/16/24/32-byte keys.
- Anything exposed to attacker-chosen keys: the doc comment says the seed can be extracted with some computational work and tells you to use it only with a fallback such as SipHash; SMHasher also flags a PerlinNoise failure (seed/key collisions).
- ARM targets without measuring first: open issue #7 reports it about 10% slower than SipHash on a Cortex-A55 (versus about 1.5x faster on an Intel Skylake), and the docs say non-ideal architectures lose up to 30-40%.
- Projects that need an actively maintained crate: the last code change was December 2020 (v4.1.0, January 2021), and later commits only added the license text.

## How it is fast

It reads 8 bytes per load and keeps four independent 64-bit lanes, consuming 32 bytes per loop iteration, so the four multiply chains can overlap through instruction-level parallelism; the lanes are only XOR-combined at the end with the length. Each lane update is XOR-then-diffuse, where the diffusion is a PCG-style permutation: multiply by 0x6eed0e9da4d94a4f, xor-shift by a data-dependent amount ((x &gt;&gt; 32) &gt;&gt; (x &gt;&gt; 60)), multiply again. The construction is a 4-lane, length-padded Merkle-Damgard scheme with no SIMD or hardware intrinsics, so its speed comes from scalar multiply throughput alone.

## Compared with alternatives

Pick it over xxHash, wyhash or the rapidhash Rust port only when you specifically need SeaHash-compatible or endian/width-independent persisted values from a dependency-free no_std Rust crate. Those siblings post roughly 1.4-2.7x its bulk throughput in the same SMHasher table, and for in-memory Rust HashMaps foldhash, rustc-hash or aHash are the catalogued choices.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | none (quickcheck and criterion are dev-dependencies only) |
| **Minimum toolchain** | not documented (no rust-version or edition key in Cargo.toml, so edition 2015; the code uses const fn with let bindings, which needs a Rust from roughly 2019 onward) |
| **Platforms** | any Rust target, no_std by default; tuned for 64-bit little-endian (32-bit targets split each 8-byte read into two u32 reads) |
| **Thread safety** | not documented; hash()/hash_seeded() are pure functions and SeaHasher is a plain Copy struct with no shared state |
| **Drop-in for the baseline** | partial — as a Rust Hasher it can replace an FNV hasher via BuildHasherDefault&lt;SeaHasher&gt;, but the crate ships no BuildHasher type (open issue #14), and C/C++ users need an unofficial port |

## Gotchas

- Output is only promised to be stable within a major version: the docs say values change only on major bumps, and 4.0 changed the streaming hasher to fix chunking sensitivity (issues #1, #5). Pin the major version for anything persisted.
- hash_seeded takes four u64 seeds that directly initialise the lanes. For inputs under 8 bytes, the input is XORed into lane a with the seed, so a key and a seed are interchangeable through XOR. Seeding is obfuscation, not DoS protection.
- The streaming SeaHasher implements write_u8/u32/u64 and similar by routing the bytes through the generic byte-buffer path. Hashing integer keys in a HashMap therefore pays tail-buffer bookkeeping on every call.
- The hot loops use unsafe raw-pointer reads (read_unaligned since the fix for issue #9). The benchmark tables in the docs (0.24 cycles/byte, CityHash 1.62 cpb, '2.5 GHz CPU') date from 2016 and give no compiler, flags or competitor code.

## Known shortcomings

- Not faster than xxHash: independent SMHasher (C port) has xxHash64 at 11,176 vs SeaHash 8,240 MiB/s, and MetroHash and CityHash64 also beat it; it only beats FNV (\~11x) and Murmur3F (\~1.16x bulk). Rust-only, stale since 2023-10-25 (though widely downloaded, \~153M on crates.io).
- Fails SMHasher's PerlinNoise seed/key test and its docs say the seed can be extracted (no HashDoS resistance); also loses to Murmur3F on small keys. Measured code is the C port, not the Rust crate. Keys not a multiple of 8 bytes cost \~61 cycles vs \~36-40; \~10% slower than SipHash on Cortex-A55 (#7). Unchanged since 2020 (v4.1.0); hash values stable only within a major version; no BuildHasher type (#14).

## Caveats and trade-offs

The headline claim (3-20% faster than xxHash/MetroHash, faster than CityHash \~1 GB/s) is first-party, 2016-era, has no xxHash numbers, and is contradicted by independent SMHasher, where xxHash64, MetroHash64 and City64 all beat SeaHash in bulk throughput (and XXH3 is \~2.5x faster). SeaHash beats only FNV (\~11x bulk) and MurmurHash3 (\~16% bulk; it loses to Murmur3F on small keys). SMHasher tests a C port (seahash.c), not this Rust crate. The repo's benches/bench.rs (criterion) times SeaHash alone with no competitor, and no compiler/flags are stated anywhere. No commits since 2023-10-25.

Canonical implementation is Rust; unofficial C/C++/Go ports exist (e.g. jroivas/seahash, briandowns/libseahash) but were not verified here. Not cryptographically secure. Scalar, portable design with no SIMD/hardware-intrinsic requirement, which is part of the pitch vs xxHash/MetroHash on platforms lacking those optimizations.

## Maintenance

Stale: code last changed in December 2020 and v4.1.0 (January 2021) is the latest crate, yet it still has about 153M crates.io downloads; the crate is MIT, dependency-free and a few hundred lines, so it is easy to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification C, tier now B.
- **Tier reason:** The docs.rs page makes the xxHash/MetroHash claim ('around 3-20% improvement') with no xxHash numbers and no methodology, and the repo's benches/bench.rs (criterion) times only SeaHash. The well-known independent SMHasher suite (rurban, C port seahash.c) contradicts the xxHash, MetroHash and CityHash claims but does show a bulk-throughput win over FNV-1a/FNV-64 and MurmurHash3. So for the corrected baseline this is B: independent suite, CPU named but compiler and flags not stated, so not A.
- **Verifier notes:** The claimed win over the listed baseline (xxHash) is refuted by SMHasher, so the entry survives only after re-baselining to FNV/MurmurHash3, which the docs.rs page also compares against. If the orchestrator wants only in-list baselines (xxHash, wyhash, CityHash, std::hash), treat this as reject not-faster. Metadata checked: MIT in Cargo.toml plus MIT LICENSE text (the GitLab API reports license null); last commit 2023-10-25, so stale is correct; not archived, not a fork; latest crate is 4.1.0 while benchmark docs are for 2.0.0.
- **Fields the verifier corrected:** `baseline`, `baseline_in_list`, `benchmark_url`, `workload`, `claimed_speedup`, `hardware`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** rurban/smhasher: SeaHash 8,240 vs xxHash64 11,176 MiB/s bulk.
- **Pages the verifier opened:**
  - <https://docs.rs/seahash/2.0.0/seahash/>
  - <https://gitlab.redox-os.org/api/v4/projects/redox-os%2Fseahash>
  - <https://gitlab.redox-os.org/api/v4/projects/redox-os%2Fseahash/repository/commits?per_page=3>
  - <https://gitlab.redox-os.org/api/v4/projects/redox-os%2Fseahash/repository/tree?per_page=100>
  - <https://gitlab.redox-os.org/redox-os/seahash/-/raw/master/LICENSE>
  - <https://gitlab.redox-os.org/redox-os/seahash/-/raw/master/Cargo.toml>
  - <https://gitlab.redox-os.org/redox-os/seahash/-/raw/master/README.md>
  - <https://gitlab.redox-os.org/redox-os/seahash/-/raw/master/benches/bench.rs>
  - <https://crates.io/api/v1/crates/seahash>
  - <https://crates.io/api/v1/crates/seahash/reverse_dependencies?per_page=1>
  - <https://github.com/rurban/smhasher>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/README.md>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/doc/seahash.txt>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/seahash.c>
- **Sources the enricher read:**
  - <https://gitlab.redox-os.org/redox-os/seahash/-/raw/master/README.md>
  - <https://gitlab.redox-os.org/redox-os/seahash/-/raw/master/Cargo.toml>
  - <https://gitlab.redox-os.org/redox-os/seahash/-/raw/master/src/lib.rs>
  - <https://gitlab.redox-os.org/redox-os/seahash/-/raw/master/src/buffer.rs>
  - <https://gitlab.redox-os.org/redox-os/seahash/-/raw/master/src/helper.rs>
  - <https://gitlab.redox-os.org/redox-os/seahash/-/raw/master/src/stream.rs>
  - <https://gitlab.redox-os.org/redox-os/seahash/-/raw/master/src/impl_std.rs>
  - <https://gitlab.redox-os.org/redox-os/seahash/-/raw/master/benches/bench.rs>
  - <https://gitlab.redox-os.org/redox-os/seahash/-/raw/master/.gitlab-ci.yml>
  - <https://gitlab.redox-os.org/redox-os/seahash/-/raw/master/tests/chunking.rs>
  - <https://gitlab.redox-os.org/api/v4/projects/redox-os%2Fseahash/repository/tree?per_page=100&recursive=true>
  - <https://gitlab.redox-os.org/api/v4/projects/redox-os%2Fseahash/repository/commits?per_page=6>
  - <https://gitlab.redox-os.org/api/v4/projects/redox-os%2Fseahash/issues?per_page=100&state=all>
  - <https://crates.io/api/v1/crates/seahash>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/README.md>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/doc/seahash.txt>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/seahash.c>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/Hashes.h>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/main.cpp>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://gitlab.redox-os.org/redox-os/seahash`) · [data/wave7/enrich/raw/gitlab_redox_os_org_redox_os_seahash.json](../../../data/wave7/enrich/raw/gitlab_redox_os_org_redox_os_seahash.json) (enrichment confidence 0.62)

</details>
