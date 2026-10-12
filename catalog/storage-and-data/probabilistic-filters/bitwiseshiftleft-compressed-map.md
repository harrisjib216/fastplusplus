# compressed_map ApproxSet (frayed ribbon filter)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Probabilistic filters](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🔴 abandoned

> Research Rust crate: static approximate set built on frayed ribbon filters, about 30% smaller than Bloom at equal FPR.

| | |
|---|---|
| **Beats** | Bloom filter |
| **Claimed result** | "Compared to Bloom filters, ApproxSets take several times longer (and several times more memory) to construct; are faster to query; and take about 30% less space." (verbatim). Only the \~30% space figure is a concrete number; query/construction-speed differences are stated only qualitatively. |
| **Workload** | Author's own qualitative comparison (README) of ApproxSet, a frayed-ribbon-filter-based approximate set, against Bloom filters; no specific dataset size or key type given. |
| **Metric** | memory |
| **Adoption** | 51 stars; crates.io compressed_map 0.1.0 (2022-04-12), 1,644 downloads |
| **Last commit** | 2022-11-23 |
| **Links** | [repository](https://github.com/bitwiseshiftleft/compressed_map) · [benchmark](https://github.com/bitwiseshiftleft/compressed_map#approximate-sets) |

## Verdict

There is no measured Bloom comparison. The claims of \~30% less space, faster queries and a slower, memory-hungrier build are the author's qualitative README statements, and the repo's Criterion benches have no Bloom baseline. The 30% matches b bits/key at FPR 2^-b versus about 1.44·b for an optimal Bloom filter (derived). The only numbers are author-reported on Apple Silicon, with no compiler flags given: 100-200 cycles per in-cache query, and about 2 minutes and 8 GB to build 100M entries on an M1. In issue #2 the author also reports a 2^20-key, 64-bit-output CompressedRandomMap built in 686 ms (474 ms threaded) with 71 ns queries on an M1 Max.

## Use it when

- A static set built once offline (hourly or daily) and shipped to many clients, where download or storage size matters more than build cost. Examples: blocklists, or revocation data in the style of CRLite.
- Rust code that wants Bloom-style membership at about b bits per key for an FPR of 2^-b (8 bits for about 0.39%), about 30% less than a Bloom filter at the same FPR.
- Sets from roughly 100k up to a few hundred million keys, on a build host with enough RAM: the author reports that 100M entries take about 2 minutes and 8 GB on an Apple M1.
- You also need the crate's CompressedMap for low-entropy key-&gt;value data (for example key-&gt;bool with 1% true, which lands 0.1-11% above Shannon entropy), and the ApproxSet comes with it.
- Build machines are x86-64 with AVX2 or AArch64 with NEON. Only construction is vectorized; queries are portable.

## Skip it when

- Production or security-critical use. The author says 'research-grade... Don't deploy it in production', the serialization format was 'not finalized until v0.2.0' and v0.2.0 was never released, and there have been no commits since 2022-11-23.
- Sets that need inserts or deletes, or large sets rebuilt often. Construction is 'several times longer (and several times more memory)' than a Bloom filter, and the author says binary fuse filters build about 10x faster for about 10% more space.
- Small sets. Each output bit is padded separately (up to about 40 bytes for an 8-bit ApproxSet, per issue #3), and headers and the hash key are added on top, so the space win disappears at hundreds to a few thousand keys.
- Latency-critical membership checks. Every query runs a keyed SipHash-1-3. The author's own notes say frayed ribbons query about 2x slower than standard ribbon filters on Intel, and that 'Facebook's ribbon filters are typically faster' for set membership. A cache-line-blocked Bloom filter also needs only about one memory access.
- Billions of keys or limited build memory. Build memory tops out at 'a few hundred million to a billion rows on commodity hardware', and x86 hosts without AVX2 fall back to a scalar solver that is 'very slow'.

## How it is fast

Internally an ApproxSet is a CompressedRandomMap that maps every member to 0. A member satisfies M·encode(hash(k)) ^ hash(k) = 0 over GF(2), so a non-member matches with probability 2^-b while the structure stores only about b bits per key (0.1% overprovisioning). An optimal Bloom filter needs about 1.44·b bits for the same FPR, which is where the roughly 30% saving comes from (derived). The 'frayed ribbon' matrix gives each key two aligned 32-bit blocks that usually sit close together. A query therefore hashes the key once (keyed SipHash-1-3, 128-bit) and reads two small groups of words, taking the parity of AND+popcount for each output bit. That is 2 memory regions instead of the roughly b random probes a standard Bloom filter makes. Construction solves the sparse linear system hierarchically, using an M4RI-style 'Four Russians' tile solver with AVX2/NEON vector permutes. It costs Õ(n^1.5) time and O(n log n) memory.

## Compared with alternatives

For plain membership filtering, a sibling is usually the better choice: xorf (Rust binary fuse, about 9 bits/key at 2^-8, maintained, fast builds), pleat, or BuRR (ribbon filters near the space minimum with faster construction). Pick compressed_map when you want its CompressedMap static function for skewed, low-entropy values in Rust and ApproxSet's roughly b bits/key comes along. For the CRLite revocation use case, prefer Mozilla's Clubcard, which builds on Hamburg's two-level cascade idea with Ribbon filters.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | siphasher 0.3, rand 0.8, bincode ^2.0.0-RC.1 (bincode is flagged unmaintained in RUSTSEC-2025-0141), and cbindgen 0.21 as a non-optional build dependency. The default `cffi` feature also builds a cdylib. The optional `threading` feature uses std threads. |
| **Minimum toolchain** | No rust-version is declared; the crate uses edition 2021 (Rust 1.56+). The last known-good build was docs.rs on 2022-04-12 with rustc 1.62.0-nightly, which could only have resolved bincode 2.0.0-rc.1. |
| **Platforms** | Queries run on any target. Construction uses AVX2 on x86-64 (runtime-detected) and NEON on AArch64/armv7, with a slow scalar fallback. TODO.md says armv7, 32-bit x86, RISC-V and big-endian are untested. |
| **Thread safety** | Not documented. A built set is immutable, `probably_contains` takes &self, and the data is a Cow&lt;[u8]&gt; plus PhantomData, so concurrent read-only sharing looks safe (derived from the source). The `threading` feature parallelizes only the build. |
| **Drop-in for the baseline** | partial — it replaces a static Bloom filter only: you build once from a deduplicated collection, with no add, delete or union. The FPR can only be 2^-integer bits, the build can fail and returns Option, and the API and C FFI (build/probably_contains/encode/free for u64 and byte keys, with no decode) differ from any Bloom crate. |

## Gotchas

- The published 0.1.0 (and master, which has no Cargo.lock) does not compile against current bincode. The requirement ^2.0.0-RC.1 resolves to newer 2.0.x releases. The docs.rs rebuild on 2024-11-18 failed against bincode 2.0.0-rc.3 with E0412 `SkipFixedArrayLength` and E0599 `skip_fixed_array_length`, and bincode 2.0.1's BorrowDecode trait adds a Context parameter the crate does not implement. Pinning should fix it: `cargo update -p bincode --precise 2.0.0-rc.1`.
- Duplicate keys, or unequal keys whose Hash output is identical, make every attempt fail. The builder silently retries up to max_tries=256 before returning None, which 'may be extremely slow'. Pass a HashSet or BTreeSet, not a Vec.
- Building is probabilistic: each try succeeds about 90% of the time or more, and there is no proof of the failure probability. Each try draws a fresh random SipHash key from OsRng unless BuildOptions.key_gen is set, so the output bytes are nondeterministic by default. With `threading`, an out-of-memory thread can be treated as a failed try and trigger costly retries.
- Loading can be zero-copy: the types carry a lifetime so BorrowDecode can borrow from a buffer such as an mmap, and `take_ownership` copies the data out. `write_to_file` refuses to overwrite an existing file.

## Known shortcomings

- The \~30% space saving is the theoretical gap (8 bits/key vs Bloom's 1.44x overhead); there is no Bloom benchmark in the repo.
- The author calls it research-grade and advises against deploying it; no commits since 2022-11 and the format was never finalized. The published 0.1.0 does not compile against current bincode (pin 2.0.0-rc.1; bincode flagged unmaintained, RUSTSEC-2025-0141). Builds are several times slower and use more memory than Bloom (100M keys \~2 min / 8 GB on M1; x86 without AVX2 is very slow); small sets waste padding; FPR only in powers of 2^-n; duplicate keys cause up to 256 silent retries. The author notes plain ribbon queries faster and binary fuse builds \~10x faster.

## Caveats and trade-offs

There are no benchmark numbers, dataset or methodology behind the query-speed or construction-time claims. The repo's Criterion benches contain no Bloom filter baseline. The '\~30% less space' figure matches the theoretical gap between a static-function filter at log2(1/ε) bits per key and a Bloom filter at \~1.44·log2(1/ε). ApproxSet defaults to 8 bits per entry, so ε ≈ 2^-8 (derived, not stated on page). Ribbon and xor filters achieve similar savings. The crate docs add only that queries take 'typically around 100-200 cycles if the map is in cache', and that building 100M entries takes \~2 minutes and 8 GB on an Apple M1. The author calls it research-grade ('Don't deploy it in production'), and it depends on bincode 2.0.0-RC.1. There have been no commits since 2022-11-23.

Construction is explicitly slower and more memory-hungry than a Bloom filter for the same set; author labels the whole library 'research-grade... don't deploy it in production'; C FFI incomplete; depends on a pre-release bincode version.

## Maintenance

Abandoned: last commit 2022-11-23, a single 0.1.0 release in April 2022, and about 1.6k downloads. The author calls it experimental and research-grade. It is MIT-licensed and a few thousand lines of Rust, so it is vendorable, but it needs bincode pinned to 2.0.0-rc.1 to compile, and that bincode line is now unmaintained.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The only evidence is the author's own README and crate-doc statements: \~30% less space than Bloom filters and 'faster to query', with no dataset, hardware or measured Bloom comparison. The repo's benches (uniform.rs, nonuniform.rs, matrix_ops.rs) do not include a Bloom filter. These are numbers without methodology, so C.
- **Verifier notes:** The quote is verbatim in the README's Approximate sets section, and lib.rs repeats the \~30% space claim. The metadata is correct: MIT via LICENSE.txt, 51 stars, not a fork, not archived, and last commit 2022-11-23. pushed_at of 2023-03-30 is not a commit on master. The entry is metric=memory with only a qualitative speed claim, so it is borderline for a 'faster' catalog, but it is kept as tier C.
- **Fields the verifier corrected:** `caveats`, `stars_or_usage`
- **Pages the verifier opened:**
  - <https://github.com/bitwiseshiftleft/compressed_map>
  - <https://github.com/bitwiseshiftleft/compressed_map#approximate-sets>
  - <https://github.com/bitwiseshiftleft/compressed_map/blob/master/src/lib.rs>
  - <https://github.com/bitwiseshiftleft/compressed_map/blob/master/Cargo.toml>
  - <https://github.com/bitwiseshiftleft/compressed_map/blob/master/benches/uniform.rs>
  - <https://crates.io/api/v1/crates/compressed_map>
  - <https://api.crossref.org/works?query.bibliographic=frayed+ribbon+filter+Hamburg&rows=5>
- **Sources the enricher read:**
  - <https://github.com/bitwiseshiftleft/compressed_map>
  - <https://github.com/bitwiseshiftleft/compressed_map#approximate-sets>
  - <https://github.com/bitwiseshiftleft/compressed_map/blob/master/src/lib.rs>
  - <https://github.com/bitwiseshiftleft/compressed_map/blob/master/src/uniform.rs>
  - <https://github.com/bitwiseshiftleft/compressed_map/blob/master/src/tilematrix/tile.rs>
  - <https://github.com/bitwiseshiftleft/compressed_map/blob/master/src/cffi.rs>
  - <https://github.com/bitwiseshiftleft/compressed_map/blob/master/Cargo.toml>
  - <https://github.com/bitwiseshiftleft/compressed_map/blob/master/build.rs>
  - <https://github.com/bitwiseshiftleft/compressed_map/blob/master/benches/uniform.rs>
  - <https://github.com/bitwiseshiftleft/compressed_map/blob/master/TODO.md>
  - <https://github.com/bitwiseshiftleft/compressed_map/blob/master/OtherIdeas.md>
  - <https://github.com/bitwiseshiftleft/compressed_map/blob/master/attic_c/README.md>
  - <https://github.com/bitwiseshiftleft/compressed_map/issues/1>
  - <https://github.com/bitwiseshiftleft/compressed_map/issues/2>
  - <https://github.com/bitwiseshiftleft/compressed_map/issues/3>
  - <https://github.com/bitwiseshiftleft/compressed_map/issues/4>
  - <https://github.com/bitwiseshiftleft/compressed_map/issues/5>
  - <https://crates.io/api/v1/crates/compressed_map>
  - <https://crates.io/api/v1/crates/compressed_map/0.1.0/dependencies>
  - <https://crates.io/api/v1/crates/bincode/versions>
  - <https://docs.rs/crate/compressed_map/0.1.0>
  - <https://docs.rs/crate/compressed_map/0.1.0/builds>
  - <https://docs.rs/crate/compressed_map/0.1.0/builds/1555443>
  - <https://docs.rs/crate/compressed_map/0.1.0/builds/540841>
  - <https://docs.rs/bincode/2.0.1/bincode/de/trait.BorrowDecode.html>
  - <https://docs.rs/bincode/2.0.0-rc.1/bincode/de/trait.BorrowDecode.html>
  - <https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/bincode/RUSTSEC-2025-0141.md>
  - <https://github.com/mozilla/clubcard>
  - <https://rwc.iacr.org/2022/program.php>
  - <https://rwc.iacr.org/2022/json/program.json>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/bitwiseshiftleft/compressed_map`) · [data/wave6/enrich/raw/github_com_bitwiseshiftleft_compressed_map.json](../../../data/wave6/enrich/raw/github_com_bitwiseshiftleft_compressed_map.json) (enrichment confidence 0.85)

</details>
