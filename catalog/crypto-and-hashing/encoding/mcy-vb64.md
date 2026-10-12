# vb64 (Rust std::simd Base64 codec)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Encoding (base64, hex, CRC)](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0` · 🟡 stale

> Nightly-only std::simd Base64 codec that decodes 2-2.5x faster than the base64 crate on AVX2. It no longer builds.

| | |
|---|---|
| **Beats** | base64 (marshallpierce/rust-base64 crate) |
| **Claimed result** | Decoding 2-2.5x faster, encoding 1.2-1.5x faster than the `base64` crate with AVX2; roughly even/worse with only SSSE3 |
| **Workload** | Criterion benchmark (benches/bench.rs) on 256 test vectors of small inputs (graph covers \~0-500 bytes), vb64 vs base64 crate 0.21.5, AVX2 on an unspecified AMD Zen 2 machine |
| **Metric** | throughput |
| **Hardware** | unspecified AMD Zen 2 machine |
| **Compiler and flags** | rustc nightly (rust-toolchain.toml); README recommends -Ctarget-cpu=native -Zbuild-std for max performance but does not state these were the exact bench flags |
| **Adoption** | 90 stars; companion code to the 441-point HN thread 'Designing a SIMD Algorithm from Scratch' (mcyoung.xyz) |
| **Last commit** | 2023-11-26 |
| **Links** | [repository](https://github.com/mcy/vb64) · [benchmark](https://github.com/mcy/vb64#readme) |

## Verdict

The author's Criterion bench decodes and encodes 256 test vectors of up to about 500 B with vb64 and with base64 0.21.5 BASE64_STANDARD (which validates more strictly), allocating a fresh Vec each call. On an unnamed Zen 2 CPU with AVX2 on nightly rustc (flags not stated), the README graph shows decode at about 22 vs 55 ns for the smallest inputs and 135 vs 325 ns at 500 B (2-2.5x); encode is 1.2-1.5x with no graph. One HN commenter reported identical speedups on Zen 3 and 1.4-2x on an M1.

## Use it when

- As a reference design: a compact, heavily commented portable-SIMD Base64 codec (perfect-hash classify, nibble-LUT validation, u16 shift-pack) to port into your own Rust or C++ code.
- Decoding many short (under about 500 B) standard-alphabet Base64 strings, such as blobs inside JSON, where per-call latency matters and you can vendor the code and patch it for your nightly.
- x86-64 builds with AVX2 enabled at compile time (-Ctarget-cpu=native or +avx2) and -Zbuild-std, which is where the 2-2.5x decode gain was measured.
- Apple M-series/aarch64 only if you accept informal evidence: one HN commenter reported 1.4x decode gains rising to 2x at 110 B on an M1.

## Skip it when

- Any build on current Rust. It has failed to compile on nightly since about 2023-12-08 (issue #2: Swizzle2/Which removed), and the fix PR #3 has sat unmerged since Feb 2024. portable-simd PR #485 (Oct 2025) also removed the LaneCount/SupportedLaneCount types that vb64 imports, so PR #3 alone is no longer enough.
- You need the URL-safe alphabet, no-pad or strict-canonical modes, MIME line wrapping or whitespace skipping, or the position of the bad byte. None of these are implemented.
- Validating untrusted or signed data where canonical form matters. The decoder accepts input the base64 crate's STANDARD engine rejects: missing padding, non-zero trailing bits, and even length%4==1 (its own test asserts that 'A==' decodes OK).
- Portable x86-64 binaries without AVX2 at compile time. There is no runtime dispatch; the README says SSSE3-only decode merely ties the base64 crate and encode is 'much worse'. std's swizzle_dyn falls back to a scalar loop unless SSSE3/AVX2 are enabled when std is built.
- Large-buffer throughput or anything maintained. There are no numbers above about 500 B; base64-simd (Nugine/simd) picks SIMD at runtime and was last committed 2026-08-30.

## How it is fast

Decode classifies each ASCII byte with the perfect hash (c &gt;&gt; 4) - (c == '/') (credited to WojciechMula/base64simd issue #3). It then uses that hash as a swizzle_dyn (pshufb) index into an 8-entry offset table to get the sextets. Validity is checked with two 16-entry nibble lookup tables (the author calls it an exact bloom filter), and any error is reported only after the loop, so the hot loop is branchless. Four sextets are packed into three bytes by widening to u16, applying per-lane shifts [2,4,6,8], then a rotate/OR and one static shuffle (trick credited to Danila Kutenin); encode reverses these steps with a saturating-subtract perfect hash. Short tails are built into a padded vector from overlapping unaligned u64/u32 loads (Abseil style) instead of Simd::gather_or. Decode uses 32-byte vectors when compiled with AVX2 and 16 otherwise; encode always uses 16.

## Compared with alternatives

No siblings catalogued yet. Outside the catalog, base64-simd (Nugine/simd: runtime SIMD selection, about 155M crates.io downloads, active in 2026) is the maintained option; pick vb64 only as a reference design or for code you will vendor and maintain.

## Integration

| | |
|---|---|
| **Form** | crate (vb64 0.1.2) or source-drop |
| **Dependencies** | none at runtime (dev-only: base64 0.21.5, criterion 0.4) |
| **Minimum toolchain** | Rust nightly with #![feature(portable_simd)] from about Nov 2023 (rust-toolchain.toml says unpinned 'nightly'); broken on nightly from 2023-12-08 onward |
| **Platforms** | Any std::simd target in principle. Performance is documented only for x86-64 AVX2 (Zen 2) and SSSE3, plus an informal M1 report. The AVX2 decode path is chosen at compile time via cfg!(target_feature = "avx2"), with no runtime detection. |
| **Thread safety** | Stateless free functions on borrowed slices with no global state (from source); not otherwise documented |
| **Drop-in for the baseline** | partial — it does the same job for the standard alphabet with padded encode, but through free functions instead of base64's Engine trait (BASE64_STANDARD.encode/decode), with no alphabet or padding config, a unit Error type, and a more lenient decoder |

## Gotchas

- The decoder is lenient. It strips up to two trailing '=' and never checks length%4 or zeroes in the trailing bits, so several different strings decode to the same bytes, and some invalid lengths decode to an extra byte.
- Errors are deferred by design: invalid input is reported only after the whole buffer is processed, as a bare Error. To find the offending byte you have to rescan the input yourself.
- Output writes are full N-byte unaligned SIMD stores into reserved slack: each call reserves decoded/encoded length + 16 or 32 extra bytes, using raw pointers and unsafe set_len. The tree has no fuzz targets (tests are 256 random vectors, all-0xFF inputs of 0-500 bytes, and an alphabet sweep).
- Without -Zbuild-std and AVX2 at compile time you silently get a slower path, because std docs say swizzle_dyn's implementation is fixed when std is built. The author calls the near constant-time behaviour on valid input accidental, not a guarantee.

## Known shortcomings

- Stale since 2023-11-26. Benchmark graph covers decode only, inputs up to \~500 bytes, times in ns; target-cpu/build-std flags are only recommended in the README, not pinned. Nightly-Rust portable-SIMD crate.
- Does not build on nightly since Dec 2023 (issue #2); fix PR #3 is unmerged and portable-simd PR #485 (Oct 2025) removed LaneCount, which vb64 imports. Lax decoder accepts missing padding, nonzero trailing bits and len%4==1 inputs that the base64 crate's STANDARD engine rejects, so the benchmark is partly unfair. Standard alphabet only, no URL-safe/whitespace handling or error offsets. AVX2 chosen at compile time; needs -Zbuild-std for the fast swizzle. Maintained alternative: base64-simd (Nugine/simd).

## Caveats and trade-offs

No exact CPU model (only 'Zen 2 machine'); first-party benchmark; the README graph shows decode only (average ns per call vs input size up to \~500 bytes), so there are no large-buffer throughput numbers; with only SSSE3 the README says decode is even with base64 and encode is much worse; baseline base64 crate is scalar; requires nightly (std::simd)

Requires Rust nightly for std::simd; Rust-only, no C API

## Maintenance

Stale since 2023-11-26: the maintainer has not responded to the build-fix PR since Feb 2024, and the crate cannot compile on any recent nightly, so treat it as about 760 lines of Apache-2.0 reference code to vendor and patch, not as a dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README gives first-party ratios against the base64 crate: decode is 2-2.5x faster and encode 1.2-1.5x faster with AVX2 on Zen 2. It also has a decode graph in ns, and the criterion bench code (benches/bench.rs, base64 0.21.5 as 'baseline') is public. No CPU model is given and the exact bench flags are not stated, so it cannot be A.
- **Verifier notes:** The last commit on main is 2023-11-26. GitHub's pushed_at of 2024-02-08 is not a commit date, so maintenance_status changes from abandoned to stale (about 2.8 years). The HN thread 'Designing a SIMD Algorithm from Scratch' (441 points) is confirmed via Algolia, and the star count (90) and Apache-2.0 license are confirmed.
- **Fields the verifier corrected:** `last_commit`, `maintenance_status`, `compiler_and_flags`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/mcy/vb64>
  - <https://github.com/mcy/vb64#readme>
  - <https://raw.githubusercontent.com/mcy/vb64/main/Cargo.toml>
  - <https://raw.githubusercontent.com/mcy/vb64/main/benches/bench.rs>
  - <https://raw.githubusercontent.com/mcy/vb64/main/rust-toolchain.toml>
  - <https://raw.githubusercontent.com/mcy/vb64/main/images/graph.png>
  - <https://hn.algolia.com/api/v1/search?query=Designing%20a%20SIMD%20Algorithm%20from%20Scratch&tags=story>
- **Sources the enricher read:**
  - <https://github.com/mcy/vb64>
  - <https://github.com/mcy/vb64#readme>
  - <https://github.com/mcy/vb64/blob/main/Cargo.toml>
  - <https://github.com/mcy/vb64/blob/main/rust-toolchain.toml>
  - <https://github.com/mcy/vb64/blob/main/src/lib.rs>
  - <https://github.com/mcy/vb64/blob/main/src/simd.rs>
  - <https://github.com/mcy/vb64/blob/main/src/util.rs>
  - <https://github.com/mcy/vb64/blob/main/benches/bench.rs>
  - <https://raw.githubusercontent.com/mcy/vb64/main/images/graph.png>
  - <https://github.com/mcy/vb64/commits/main>
  - <https://github.com/mcy/vb64/pull/1>
  - <https://github.com/mcy/vb64/issues/2>
  - <https://github.com/mcy/vb64/pull/3>
  - <https://github.com/mcy/vb64/pull/4>
  - <https://crates.io/api/v1/crates/vb64>
  - <https://mcyoung.xyz/2023/11/27/simd-base64/>
  - <https://hn.algolia.com/api/v1/search?query=Designing%20a%20SIMD%20Algorithm%20from%20Scratch&tags=story>
  - <https://hn.algolia.com/api/v1/items/38443253>
  - <https://raw.githubusercontent.com/rust-lang/rust/master/library/portable-simd/crates/core_simd/src/swizzle_dyn.rs>
  - <https://raw.githubusercontent.com/rust-lang/rust/master/library/portable-simd/crates/core_simd/src/lane_count.rs>
  - <https://raw.githubusercontent.com/rust-lang/rust/master/library/portable-simd/crates/core_simd/src/mod.rs>
  - <https://raw.githubusercontent.com/rust-lang/rust/master/library/portable-simd/crates/core_simd/src/vector.rs>
  - <https://raw.githubusercontent.com/rust-lang/rust/master/library/portable-simd/crates/core_simd/src/swizzle.rs>
  - <https://github.com/rust-lang/portable-simd/pull/485>
  - <https://raw.githubusercontent.com/marshallpierce/rust-base64/master/src/engine/general_purpose/mod.rs>
  - <https://crates.io/api/v1/crates/base64-simd>
  - <https://github.com/Nugine/simd#readme>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/mcy/vb64`) · [data/wave7/enrich/raw/github_com_mcy_vb64.json](../../../data/wave7/enrich/raw/github_com_mcy_vb64.json) (enrichment confidence 0.8)

</details>
