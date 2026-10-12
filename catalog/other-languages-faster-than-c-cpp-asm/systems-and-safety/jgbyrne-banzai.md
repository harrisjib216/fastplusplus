# banzai

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Systems and safety](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Rust` · `MIT` · 🟢 active

> Pure-Rust bzip2 encoder using linear-time SA-IS for the BWT; bounds bzip2's worst case but is slower on average.

| | |
|---|---|
| **Beats** | bzip2 reference implementation (C); lbzip2 and pbzip2 not compared |
| **Claimed result** | None. README: 'Compared to the reference implementation, banzai has worse average runtime but better worst-case runtime'; compression ratios 'very similar'; unchecked indexing 'could be approximately 10% faster' (no data). |
| **Workload** | bzip2 compression (encoder only; no decompressor) using a linear-time SA-IS suffix array for the Burrows-Wheeler transform; the README gives only a qualitative runtime comparison with no numbers. |
| **Metric** | throughput |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Why it wins** | Linear-time SA-IS suffix-array construction for the BWT removes the worst case of bzip2's block sorting; the author says average runtime is still worse. |
| **Adoption** | 30 stars; crates.io 0.3.2, about 28k downloads |
| **Last commit** | 2026-07-28 |
| **Links** | [repository](https://github.com/jgbyrne/banzai) · [benchmark](https://github.com/jgbyrne/banzai) |

## Verdict

There is no benchmark: the README compares banzai with the bzip2 C reference only qualitatively (similar compression ratios, worse average runtime, better worst-case runtime), with no hardware, compiler or data named, and an older README revision estimated the average runtime at about twice the reference's.

## Use it when

- Producing .bz2 output from Rust without linking libbz2 or another C toolchain dependency (the crate's only dependency is crc).
- Inputs that are highly repetitive or adversarial, where the reference encoder's fallback sort makes compression time spike and a linear-time bound on block sorting matters more than average speed.
- Memory-safety-sensitive tools that must write bzip2 and can accept slower typical compression.
- Small single-threaded jobs where compression speed is not the bottleneck (archiving logs or exports at level 9).

## Skip it when

- Throughput-sensitive compression of ordinary data: the author states average runtime is worse than the C reference, and an earlier README revision put it at roughly twice the reference runtime.
- Anything that needs decompression; there is no decoder.
- Multi-core compression: encoding is single-threaded, so lbzip2 or pbzip2 style block parallelism is not available.
- Production pipelines that need a hardened encoder: the README calls it alpha software that is not battle-hardened, there is no CI, and the code has not changed since September 2022.

## How it is fast

It is not faster on average; its advantage is a worst-case bound. The Burrows-Wheeler transform is computed with SA-IS (Nong, Zhang and Chan's induced-sorting suffix array construction), which is linear time on any input, run on the block concatenated with itself to obtain bzip2's wrap-around rotation order. The C reference sorts blocks with a comparison-based main sort and falls back to a slower algorithm on highly repetitive data, which is the case where banzai's linear bound helps; Huffman table selection follows the reference closely, so ratios are about the same.

## Compared with alternatives

Pick banzai over libbzip2-rs (a Rust port of libbzip2 with measured wins over C in both directions) only when you want an independent encoder with a linear-time worst case and no ported C code; for speed, libbzip2-rs, or the Zig bzip2z (also SA-IS-based, measured 1.79x faster than system bzip2 1.0.8 compression in its README), is the better choice.

## Integration

| | |
|---|---|
| **Form** | crate (library banzai plus binary crate bnz) |
| **Dependencies** | crc 3.0 |
| **Minimum toolchain** | Rust edition 2024 (Rust 1.85 or newer) as of 0.3.2; no rust-version field in the manifest |
| **Platforms** | any target with usize of at least 32 bits (bwt panics otherwise) |
| **Thread safety** | Not documented; encode is a single-threaded function over owned buffers with no global state in the code read |
| **Drop-in for the baseline** | partial — the output is a standard bzip2 stream readable by bzip2 -d, but the library is encoder-only with a Rust API, and bnz covers only the compression side of bzip2(1) |

## Gotchas

- The README says banzai is 'written entirely in safe Rust' (an earlier revision said it 'has no usage of unsafe'), but lib/bwt.rs Array::split contains an unsafe block that reinterprets the tail of the i32 suffix-array buffer as &mut [u32] via slice::from_raw_parts_mut; it is sound (same size and alignment, every bit pattern valid) but audits that require forbid(unsafe_code) will flag it.
- Invalid levels panic: encode and write_stream_header use assert!(1 &lt;= level && level &lt;= 9) instead of returning an io::Error.
- Memory per block: bwt appends a copy of the block to itself and allocates a 2n-entry i32 suffix array, about 1.8 MB plus 7.2 MB at level 9, plus the buckets and the output buffers.
- Performance evidence is a sentence, not a measurement: the 2022-09-20 README said runtime 'tends to be approximately twice as long' as the reference except for highly repetitive inputs; the 2022-09-26 'readme updates' commit replaced that with 'worse average runtime but better worst-case runtime', and the commit titles in between show no performance work, so the 2x figure probably still describes the current code. Correctness rests on unit tests and a cargo-fuzz round_trip target that decodes with the bzip2 0.4 crate (libbzip2); 0.3.0 was yanked on crates.io.

## Known shortcomings

- Not faster than the bzip2 C reference: the author says average runtime is worse, only the SA-IS worst case is better; encoder only and no numbers. The 2026-07-28 commit is only an edition bump; the code dates from 2022.
- Enricher: no measurement; the 2022-09-20 README said runtime was about 2x reference bzip2 and the text was later softened with no performance commits in between. The README says 'entirely safe Rust' but lib/bwt.rs's Array::split has an unsafe i32-to-u32 slice cast (sound); assert! panics on a bad level; no CI; 0.3.0 was yanked.

## Caveats and trade-offs

Not a faster-than-C claim: the author states the average runtime is worse than the C reference and only the worst case (pathological inputs) is better, with no measurements in the README, repo tree (bnz, debug, fuzz, lib) or crate docs. The newest commit (2026-07-28) only bumps the Rust edition; the previous commit is from 2022-09-26. Notable only by usage; recorded at D per the seed-record instruction.

Entirely safe Rust; alpha software ('not battle-hardened'); encoder only (use bzip2-rs to decompress); runs SA-IS on the input concatenated with itself because bzip2 uses a wrap-around BWT; level 1-9 block size as in bzip2; bnz command-line tool mimics bzip(1).

## Maintenance

Effectively dormant: the roughly 2,100-line library has been unchanged since 2022-09-26 apart from a 2026-07-28 edition-2024 bump (0.3.2); it is MIT-licensed, has about 28k crates.io downloads and three reverse dependencies (bnz, weavatrix-search, melodium-loader), and is small enough to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification D, tier now D.
- **Tier reason:** The README compares banzai with the bzip2 reference implementation only qualitatively (similar compression ratios, worse average runtime, better worst-case runtime) and gives no measurements; the repo tree (bnz, debug, fuzz, lib) holds no benchmark code or results.
- **Verifier notes:** The record is accurate: the README quotes, the MIT license, 30 stars, crates.io 0.3.2 with 28,436 downloads, and the 2026-07-28 edition-bump commit (previous commit 2022-09-26) all check out. Shortcoming: not faster than the C baseline. The author says the average runtime is worse than bzip2, the only advantage is the SA-IS worst case on pathological inputs, the build is encoder-only, and there are no numbers. 'Active' rests only on a Rust-edition bump; the code has been unchanged since 2022.
- **Shortcomings recorded by:** verifier batch-113 (wave 14 seed pass, 2026-10-13); enricher (seed pass, 2026-10-13)
- **Pages the verifier opened:**
  - <https://github.com/jgbyrne/banzai>
  - <https://raw.githubusercontent.com/jgbyrne/banzai/HEAD/README.md>
  - <https://github.com/jgbyrne/banzai/commits>
  - <https://crates.io/api/v1/crates/banzai>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/jgbyrne/banzai/HEAD/README.md>
  - <https://raw.githubusercontent.com/jgbyrne/banzai/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/jgbyrne/banzai/HEAD/bnz/Cargo.toml>
  - <https://raw.githubusercontent.com/jgbyrne/banzai/HEAD/bnz/src/main.rs>
  - <https://github.com/jgbyrne/banzai/tree/master/lib>
  - <https://raw.githubusercontent.com/jgbyrne/banzai/HEAD/lib/lib.rs>
  - <https://raw.githubusercontent.com/jgbyrne/banzai/HEAD/lib/bwt.rs>
  - <https://raw.githubusercontent.com/jgbyrne/banzai/HEAD/lib/rle.rs>
  - <https://raw.githubusercontent.com/jgbyrne/banzai/HEAD/lib/crc32.rs>
  - <https://raw.githubusercontent.com/jgbyrne/banzai/HEAD/lib/out.rs>
  - <https://raw.githubusercontent.com/jgbyrne/banzai/HEAD/lib/huffman.rs>
  - <https://raw.githubusercontent.com/jgbyrne/banzai/HEAD/lib/mtf.rs>
  - <https://github.com/jgbyrne/banzai/tree/master/fuzz>
  - <https://raw.githubusercontent.com/jgbyrne/banzai/HEAD/fuzz/Cargo.toml>
  - <https://github.com/jgbyrne/banzai/issues?q=is%3Aissue>
  - <https://github.com/jgbyrne/banzai/commits/master>
  - <https://github.com/jgbyrne/banzai/commits/master/README.md>
  - <https://github.com/jgbyrne/banzai/commit/be361f8f536653bbe13f8316d6d2a8110a074486>
  - <https://raw.githubusercontent.com/jgbyrne/banzai/40a1bbfb7ef35a182c94b82ae3d103b199dd79e4/README.md>
  - <https://raw.githubusercontent.com/jgbyrne/banzai/6f89a12dc3248f5f76a2b98f600829311002a0a7/README.md>
  - <https://crates.io/api/v1/crates/banzai>
  - <https://crates.io/api/v1/crates/banzai/reverse_dependencies>
  - WebSearch snippets: '"banzai" bzip2 encoder Rust SA-IS benchmark compression speed' (docs.rs crate pages, blocked here)
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/jgbyrne/banzai`) · [data/wave14/enrich/raw/github_com_jgbyrne_banzai.json](../../../data/wave14/enrich/raw/github_com_jgbyrne_banzai.json) (enrichment confidence 0.82)

</details>
