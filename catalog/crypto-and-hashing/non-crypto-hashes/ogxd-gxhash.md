# gxhash

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Non-cryptographic hashes](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Rust` · `MIT` · 🟢 active

> AES-round Rust hash: about 1.5-2.35x XXH3's bulk throughput in SMHasher suites, but slower than XXH3 on keys under 32 bytes.

| | |
|---|---|
| **Beats** | xxHash (XXH3) |
| **Claimed result** | rurban SMHasher (AMD Ryzen 5 3350G): gxhash64 48919.73 MiB/s bulk vs xxh3 20853.74 MiB/s (\~2.35x, derived from page data), but 36.61 vs 29.46 cycles/hash for 1-31-byte keys, so it is slower than xxh3 on small keys. SMHasher3 results: gxhash-64 19.14 vs XXH3-64 12.82 bytes/cycle bulk (\~1.5x, derived from page data), and 37.35 vs 30.69 avg cycles for 1-32-byte keys (again slower). First-party x86_64 SVG vs the twox-hash XXH3 port: roughly 2.6-3.3x at 4-128 B and \~5x at 4-32 KiB (derived from page data by reading pixels off a log-scale chart, so approximate). |
| **Workload** | Bulk throughput (262144-byte keys, alignments 0-7) and small-key latency (1-31 bytes) in the independent rurban SMHasher and SMHasher3 suites. Also a first-party custom throughput bench (benches/throughput/main.rs, 4 B-32 KiB inputs) against XXH3 (pure-Rust twox-hash 1.6.3), AHash, FxHasher, T1ha0, FoldHash, FNV-1a and MetroHash. |
| **Metric** | throughput |
| **Hardware** | rurban SMHasher default table: AMD Ryzen 5 3350G 3.6GHz. First-party chart: BuildJet 2-vCPU Ubuntu 22.04 x86_64 and ARM runners per bench.yml (the CPU model appears only in CI logs, not in the repo). |
| **Adoption** | 1030 stars |
| **Last commit** | 2026-09-26 |
| **Links** | [repository](https://github.com/ogxd/gxhash) · [benchmark](https://github.com/rurban/smhasher) |

## Verdict

Independent suites tested the 3.x algorithm; neither states compiler or flags. rurban SMHasher on a Ryzen 5 3350G measured gxhash64 at 48,920 MiB/s bulk against 20,854 MiB/s for C xxh3 (about 2.35x), but 36.61 vs 29.46 cycles/hash on small keys. SMHasher3 (hardware not stated in its summary) measured 19.14 vs 12.82 bytes/cycle for XXH3-64 (about 1.5x) and 37.35 vs 30.69 cycles on 1-32 byte keys. The first-party chart (BuildJet 2-vCPU x86_64, last regenerated 2025-05-18) is against the pure-Rust twox-hash 1.6.3 XXH3 port. Read from pixels, it shows roughly 2.6-3.3x at 4-128 B and 5-7x from 256 B to 32 KiB, and on the same chart T1ha0 roughly ties gxhash above 4 KiB.

## Use it when

- Bulk hashing of buffers from a few hundred bytes up (dedup chunks, content keys, large string keys) on x86-64 with AES-NI or AArch64 with AES. rurban SMHasher has gxhash64 at 48.9 GB/s against 20.9 GB/s for xxh3 on a Ryzen 5 3350G.
- Rust applications (not libraries) built with target-cpu=native whose HashMap keys are mostly strings. In rapidhash's hash-table suite (target-cpu=native), gxhash beats foldhash-f on AMD EPYC 9R14 (geomean 5.01 vs 5.24) and Xeon 8488C (4.73 vs 4.88), and rapidhash's notes call it 'a great choice' for AES-guaranteed, string-heavy use.
- When you need a 128-bit hash at 64-bit cost: gxhash128 has the same construction and cost as gxhash64.
- Mixed x86/ARM fleets that need the same hash value on both (the stability tests cover aarch64, x86_64 and x86_64-hybrid), as long as everyone stays on one major version.

## Skip it when

- Workloads dominated by short keys (under about 32 bytes). SMHasher3 has gxhash-64 at 37.35 avg cycles for 1-32 bytes against 30.69 for XXH3-64, and rurban has 36.61 cycles/hash against 29.46 for xxh3 and 22.04 for rapidhash.
- Libraries, portable binaries, WASM or CPUs without AES. Without aes+sse2 (x86) or aes+neon (ARM) it is a compile_error; there is no fallback (issue #47, open since 2023), no WASM support (#7, open), and no runtime CPU detection.
- Tables keyed by attacker-controlled input. The released 3.x line (crates.io 3.5.0) has seed-independent multicollisions (#83, still open): explicit 24-byte and 15-vs-16-byte colliding pairs were posted 2026-09-18. The 4.0 rewrite says it fixes this, but it was merged 2026-09-26, is not on crates.io, and has no independent analysis yet.
- Safety-critical code, or code that must run clean under Miri. The README says the crate is not intended for safety-critical use. Miri reported UB on keys shorter than 16 bytes in 3.5.0 (#123, closed as intended), and #111 (open) reports a panic under debug-assertions in release builds on Apple Silicon.
- Quality-sensitive uses such as sketches or MinHash. The SMHasher3 port of 3.x passes 226/250 tests, failing Sparse, TwoBytes, SeedZeroes, SeedSparse and Seed; rurban's table flags it 'oob UB, AES only'.

## How it is fast

Each 16-byte block is absorbed into a 128-bit SIMD lane with a single keyless AES round (AESENC on x86, AESE+AESMC on ARM). Inputs over 128 bytes run 4, 8 or 16 independent lanes, so the AES units stay busy (instruction-level parallelism), and the lanes are then folded together in a tree. Inputs of 17-128 bytes are read with overlapping unaligned loads from both ends, which avoids masking. Inputs under 16 bytes use one 16-byte load that deliberately reads past the end of the slice when that stays inside the same 4 KiB page (the 'read beyond' trick), with the padding bytes set to the length. The large-input path is kept out of line (inline(never), extern "C" so vectors pass in registers), which keeps the inlined code at each call site small. The optional nightly 'hybrid' feature uses VAES+AVX2 to process two lanes per instruction.

## Compared with alternatives

Pick gxhash over xxHash (XXH3), wyhash or aHash when you are in Rust, can guarantee AES hardware, and mostly hash inputs of a few hundred bytes or more. There it is about 2.2-2.35x xxh3 and wyhash and about 5x ahash64 in rurban's bulk column. Prefer rapidhash or foldhash for libraries, portable builds and small-key or integer-heavy hash tables: rapidhash-f leads its native hash-table geomeans (e.g. 4.46 vs 4.73 on Xeon 8488C), and plain rapidhash passes all SMHasher3 tests.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | rustversion 1.0 (compile-time proc macro; the README nevertheless advertises 0 dependencies); std optional (default feature) |
| **Minimum toolchain** | Not declared (Cargo.toml has no rust-version). CI builds on Rust 1.65, 1.72 and 1.78. The hybrid feature requires nightly (feature(stdarch_x86_avx512)). |
| **Platforms** | x86/x86-64 with AES-NI+SSE2 (uses SSSE3 when enabled); ARM/AArch64 with AES+NEON; hybrid needs x86-64 VAES+AVX2 on nightly. Any other target fails to compile. |
| **Thread safety** | Not documented. GxHasher and GxBuildHasher are Clone value types holding one 128-bit vector, with no global or shared mutable state; GxBuildHasher::default takes its randomness from std's RandomState. |
| **Drop-in for the baseline** | partial — it is a drop-in BuildHasher for std HashMap/HashSet. It does not replace XXH3 as a content hash: the output differs, there is no XXH3-style streaming state for bytes (GxHasher::write chains per call, so chunking changes the value), and C access is only through the unpublished in-repo ffi crate. |

## Gotchas

- Version skew: GitHub main is 4.0.0, merged 2026-09-26 with a new construction and new hash values, but crates.io still serves 3.5.0 (2025-03-11). The independent SMHasher/SMHasher3 numbers and the published collision pairs all concern 3.x.
- The repo's .cargo/config.toml (target-cpu=native) applies only inside the repo. Dependents must set RUSTFLAGS themselves (-C target-feature=+aes,+sse2 or target-cpu=native), and native builds can SIGILL on older CPUs (closed #66 was a SIGILL report).
- For inputs under 16 bytes it reads up to 15 bytes past the end of the slice (page-checked, now via inline asm so Miri no longer sees it). Tools that audit memory reads, and code with guard-page tricks, should know this.
- Hashing through the Hasher trait gives different values from gxhash64/gxhash128 on the same bytes. Enabling the 'deterministic' feature anywhere in the dependency graph (Cargo unifies features) fixes GxBuildHasher's seed at 42 for every map.

## Known shortcomings

- 'Fastest at all sizes' is false: slower than XXH3 on short keys (rurban smhasher 36.61 vs 29.46 cycles; SMHasher3 37.35 vs 30.69). Wins in bulk only (rurban \~2.35x, SMHasher3 \~1.5x). First-party chart uses the Rust twox-hash XXH3 port, not C XXH3. Needs AES hardware instructions.
- Released 3.x (crates.io 3.5.0) has seed-independent multicollisions (#83 open, explicit pairs posted 2026-09-18); the 4.0 rewrite claiming a fix changes hash values and is not yet on crates.io, and all independent numbers are for 3.x. Needs AES instructions (no fallback or WASM). Deliberate out-of-bounds read (Miri UB, #123); debug-assertion panic (#111). T1ha0 about ties it above 4 KiB.

## Caveats and trade-offs

The README's 'fastest for all input sizes' claim is contradicted by independent suites, which show gxhash slower than XXH3 on short keys. The first-party chart compares against the pure-Rust twox-hash 1.6.3 XXH3 port rather than C xxHash, which inflates the gap (\~5x there vs \~1.5-2.35x in the C-based suites). That chart was last regenerated 2025-05-18 on BuildJet runners. gxhash requires AES-NI+SSE2 or ARM AES+NEON and has no portable fallback. It relies on an unsafe read-beyond-buffer trick, which rurban flags as 'oob UB'. It fails 24 of 250 SMHasher3 tests.

Requires AES-NI+SSE2 (x86) or AES+NEON (ARM); no fallback, will not build without hardware crypto extensions.

## Maintenance

Actively maintained by one author: the 4.0 rewrite (claimed 1.02-1.35x faster than 3.5.0 on an M5 Pro) landed on main 2026-09-26 but is not yet released. 3.5.0 has about 1.33M crates.io downloads; MIT-licensed, and the source is about 1,300 lines including tests, small enough to vendor, but 17 issues are open, including the DoS report #83.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification B, tier now B.
- **Tier reason:** The first-party bench (benches/throughput/main.rs) is public, but the repo states no CPU model, compiler or flags, and it compares against the twox-hash Rust port of XXH3; on its own that is C. B holds because two well-known independent suites show gxhash beating C XXH3 on bulk data: rurban SMHasher on a Ryzen 5 3350G (48919.73 vs 20853.74 MiB/s) and SMHasher3 (19.14 vs 12.82 bytes/cycle). Neither suite states the compiler or flags, so not A.
- **Verifier notes:** This is a real, notable entry (1030 stars, MIT, last commit 2026-09-26). The quoted README claim is overstated and the record's CI-based tier rationale only supports C, so I re-anchored benchmark_url to the independent rurban SMHasher table. The self-published Zenodo paper (not peer-reviewed) gives rustc 1.68.0, a Ryzen 5, a GCP n2 VM and an M1 Pro, but no flags.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `hardware`, `caveats`
- **Shortcomings recorded by:** rurban/smhasher: small keys 36.61 vs XXH3 29.46 cycles, bulk \~2.35x XXH3; SMHasher3: 37.35 vs 30.69 cycles, bulk \~1.5x.
- **Pages the verifier opened:**
  - <https://github.com/ogxd/gxhash>
  - <https://github.com/ogxd/gxhash/blob/main/benches/throughput/x86_64.svg>
  - <https://raw.githubusercontent.com/ogxd/gxhash/main/benches/throughput/x86_64.svg>
  - <https://github.com/ogxd/gxhash/blob/main/.github/workflows/bench.yml>
  - <https://github.com/ogxd/gxhash/blob/main/benches/throughput/main.rs>
  - <https://github.com/ogxd/gxhash/blob/main/Cargo.toml>
  - <https://github.com/ogxd/gxhash-rust/raw/main/article/article.pdf>
  - <https://github.com/rurban/smhasher>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/README.md>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/doc/gxhash64.txt>
  - <https://gitlab.com/fwojcik/smhasher3/-/raw/main/results/README.md>
  - <https://gitlab.com/fwojcik/smhasher3/-/raw/main/results/SpeedAll.txt>
  - <https://gitlab.com/fwojcik/smhasher3/-/raw/main/results/raw/gxhash-64.txt>
- **Sources the enricher read:**
  - <https://github.com/ogxd/gxhash>
  - <https://github.com/ogxd/gxhash/blob/main/README.md>
  - <https://github.com/ogxd/gxhash/blob/main/Cargo.toml>
  - <https://github.com/ogxd/gxhash/blob/main/build.rs>
  - <https://github.com/ogxd/gxhash/blob/main/.cargo/config.toml>
  - <https://github.com/ogxd/gxhash/blob/main/src/lib.rs>
  - <https://github.com/ogxd/gxhash/blob/main/src/hasher.rs>
  - <https://github.com/ogxd/gxhash/blob/main/src/gxhash/mod.rs>
  - <https://github.com/ogxd/gxhash/blob/main/src/gxhash/platform/mod.rs>
  - <https://github.com/ogxd/gxhash/blob/main/src/gxhash/platform/x86.rs>
  - <https://github.com/ogxd/gxhash/blob/main/src/gxhash/platform/arm.rs>
  - <https://github.com/ogxd/gxhash/blob/main/ffi/Cargo.toml>
  - <https://github.com/ogxd/gxhash/blob/main/ffi/src/lib.rs>
  - <https://github.com/ogxd/gxhash/blob/main/benches/throughput/main.rs>
  - <https://raw.githubusercontent.com/ogxd/gxhash/main/benches/throughput/x86_64.svg>
  - <https://github.com/ogxd/gxhash/blob/main/.github/workflows/bench.yml>
  - <https://github.com/ogxd/gxhash/blob/main/.github/workflows/build_test.yml>
  - <https://github.com/ogxd/gxhash/blob/main/.github/workflows/cross_compile.yml>
  - <https://github.com/ogxd/gxhash/blob/main/.github/workflows/rust_version.yml>
  - <https://github.com/ogxd/gxhash/commits/main>
  - <https://github.com/ogxd/gxhash/tags>
  - <https://github.com/ogxd/gxhash/pull/129>
  - <https://github.com/ogxd/gxhash/issues>
  - <https://github.com/ogxd/gxhash/issues/83>
  - <https://github.com/ogxd/gxhash/issues/111>
  - <https://github.com/ogxd/gxhash/issues/120>
  - <https://github.com/ogxd/gxhash/issues/122>
  - <https://github.com/ogxd/gxhash/issues/123>
  - <https://github.com/ogxd/gxhash/issues/124>
  - <https://crates.io/api/v1/crates/gxhash>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/README.md>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/doc/gxhash64.txt>
  - <https://gitlab.com/fwojcik/smhasher3/-/raw/main/results/README.md>
  - <https://gitlab.com/fwojcik/smhasher3/-/raw/main/results/raw/gxhash-64.txt>
  - <https://raw.githubusercontent.com/hoxxep/rapidhash/master/README.md>
  - <https://raw.githubusercontent.com/orlp/foldhash/master/README.md>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/ogxd/gxhash`) · [data/wave7/enrich/raw/github_com_ogxd_gxhash.json](../../../data/wave7/enrich/raw/github_com_ogxd_gxhash.json) (enrichment confidence 0.78)

</details>
