# QWT (Rust quad wavelet tree)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Succinct data structures](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Rust` · `MIT` · 🟢 active

> Rust 4-ary wavelet matrix (rank/select/access over integer sequences), about 2x lower query latency than SDSL wavelet trees.

| | |
|---|---|
| **Beats** | SDSL 2.1.1 wavelet matrix/tree (also Pasta, sucds, simple-sds) |
| **Claimed result** | README table (4 GiB Big English, 10M dependent queries): SDSL 2.1.1 access 1178 / rank 1223 / select 2900 ns vs Qwt256 584 / 613 / 1623 ns (about 2.0x, 2.0x, 1.8x, derived from page data); Qwt256Pfs rank 434 ns; HQwt256Pfs rank 263 ns, select 952 ns; HQwt512Pfs select 906 ns. Space: SDSL 6089 MiB vs Qwt256 4616 MiB. |
| **Workload** | Access, rank and select latency on the 4 GiB prefix of Big English (Gutenberg ASCII text, 168 symbols), 10M dependent random queries, single thread. |
| **Metric** | latency |
| **Hardware** | Intel i9-9900KF 3.60 GHz, 64 GiB RAM, Ubuntu 23.04 kernel 6.2.0 |
| **Compiler and flags** | Rust 1.73.0, RUSTFLAGS='-C target-cpu=native', cargo run --release |
| **Adoption** | 58 stars; crates.io qwt |
| **Last commit** | 2026-07-08 |
| **Links** | [repository](https://github.com/rossanoventurini/qwt) · [benchmark](https://github.com/rossanoventurini/qwt) |

## Verdict

On a single thread of an Intel i9-9900KF (Rust 1.73.0, -C target-cpu=native) over the 4 GiB Big English prefix with 10M dependent random queries, Qwt256 measured 584/613/1623 ns for access/rank/select vs SDSL 2.1.1 at 1178/1223/2900 ns (about 2x, derived from page data), using 4616 vs 6089 MiB; the SDSL and Pasta rows come from author-run C++ harnesses whose code and flags are not in the repo.

## Use it when

- Rust FM-index or compressed text index where backward search issues chains of dependent rank queries over a sequence much larger than L3 (README benchmark: 4 GiB text, 168 symbols).
- Byte or small-integer alphabets with skewed frequencies: HQwt256Pfs reached 263 ns rank and 952 ns select vs SDSL 1223/2900 ns, at less than half the SDSL space.
- Latency-bound access/rank/select on large static sequences of u8..u64 symbols where 2 bits/symbol/level plus small overhead fits in RAM.
- Range symbol-distribution queries (occs_range) over a static sequence.

## Skip it when

- C++ projects: use the C++ companion (quad-wavelet-tree) or SDSL; calling this crate needs an FFI layer that does not exist.
- Dynamic sequences: the structure is built once and has no insert/delete/update.
- Small sequences that fit in cache: the speedup comes from fewer cache misses, and the README notes rare-symbol ranks perform about the same across implementations because their lower levels stay cached.
- Large sparse alphabets without remapping: space and depth follow the largest value, not the distinct count; values must be remapped to remove holes.
- Inputs over 2^43 symbols (documented panic) or projects needing a stable, settled API (open issues on API ergonomics and naming; 0.3.5 was yanked for a breaking change in a patch release).

## How it is fast

Each level stores a quad vector (2 bits per symbol) instead of a bitvector, so the tree has half as many levels and each query takes about half the cache misses on large inputs. Rank/select on the quad vector use block (256 or 512 symbols) and superblock counters with in-word popcount/select. The Pfs variants keep a sampled approximate-rank model (one sample per 2048 positions) to predict and prefetch (_mm_prefetch NTA on x86, prfm on aarch64) the cache lines of the next levels before they are needed; Huffman shaping (HQwt) shortens paths for frequent symbols.

## Compared with alternatives

Pick it over the C++ quad-wavelet-tree when you work in Rust or want the Huffman-shaped and prefetching variants (C++ port covers Qwt256/Qwt512 only per the README table); pick it over wavelet_forest or faster-minuter when you want a maintained, published library with reproducible QWT-side benchmarks rather than research code.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | num-traits, serde, serde-big-array, minimum_redundancy, mem_dbg, paste, generic-tests, rand, clap (clap and rand are regular, not dev, dependencies in Cargo.toml) |
| **Minimum toolchain** | Rust edition 2021; no rust-version declared. HEAD (0.5.0 in Cargo.toml) depends on rand 0.10.1, whose crates.io metadata says Rust 1.85; crates.io latest is 0.4.0. README benchmarks used Rust 1.73.0. |
| **Platforms** | any Rust target; explicit prefetch only on x86/x86_64 (_mm_prefetch) and aarch64 (inline prfm) behind the default 'prefetch' feature. A 32-bit panic (issue #11) was fixed via PR #12. |
| **Thread safety** | not documented; structures are immutable after construction and the quad wavelet tree code shows no interior mutability, so concurrent read-only queries through shared references look safe |
| **Drop-in for the baseline** | no |

## Gotchas

- QWaveletTree::new(&mut seq) destroys the input (stable partitioning in place); use From&lt;Vec&lt;T&gt;&gt; or collect() to keep your data.
- Faster rank on Pfs types needs rank_prefetch / rank_prefetch_unchecked; plain rank() does not use the prediction model.
- Open issue #3: public utils::prefetch_read_NTA is a safe fn doing raw pointer arithmetic (reported as possibly unsound); \*_unchecked methods are unsafe and UB on out-of-range input.
- Odd log2(sigma) wastes half of one level (TODO in source), and crates.io lags the repo (0.4.0 vs 0.5.0 in Cargo.toml, with deprecated RSNarrow/RSWide aliases renamed to narrow::RS / wide::RS).

## Known shortcomings

- Downgraded A to B: README numbers reproduce (SDSL 1178/1223/2900 ns vs Qwt256 584/613/1623) but the code that ran the SDSL and Pasta rows is not public; B on the DCC 2024 and SPE 2025 papers. Rust.
- Open issue #3: the public safe fn prefetch_read_NTA does raw pointer arithmetic (possibly unsound). crates.io latest is 0.4.0 while the repo Cargo.toml says 0.5.0 and 0.3.5 was yanked for a breaking change in a patch release; HEAD needs rand 0.10.1 (Rust 1.85) and pulls clap and rand as regular dependencies; QWaveletTree::new(&mut) destroys its input; 2^43-symbol limit.

## Caveats and trade-offs

SDSL and Pasta rows were measured by the authors with harness code not published in this repo and with unstated C++ compiler and flags; only the QWT/WT side is reproducible (examples/perf_wavelet_tree). Single machine in README; other machines are in the papers (arXiv 2302.09239 and SPE 2025, not opened here: arXiv and doi.org blocked). Rank results depend on frequency-weighted query symbols. Latency (dependent queries), not throughput. Rust crate; a C++ companion exists (MatteoCeregini/quad-wavelet-tree).

4-ary wavelet matrix halves cache misses. Rust library, not directly callable from C++ (a C++ port exists as a separate entry). Prefetch (Pfs) variants cost extra space. Huffman variants (HQwt) are smaller and faster but only for skewed alphabets.

## Maintenance

Active (last commit 2026-07-08, 0.5.0 bump in July 2026), MIT, 58 stars and about 189k crates.io downloads; usable today as a Rust dependency, with the API still shifting between minor versions.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification A, tier now B.
- **Tier reason:** README table shows SDSL 2.1.1 1178/1223/2900 ns vs Qwt256 584/613/1623 ns on an i9-9900KF with Rust 1.73.0 and -C target-cpu=native, and the QWT side is reproducible via examples/perf_wavelet_tree; but the code that produced the SDSL (and Pasta) rows is not in the repo (the 'benchmark' branch covers only Rust libraries) and the SDSL compiler/flags are unstated, so A fails. The comparison is published in peer-reviewed papers (DCC 2024; Software: Practice and Experience 2025, doi 10.1002/spe.70013), hence B.
- **Verifier notes:** Numbers verified exactly on the README; metadata (MIT, 58 stars, last commit 2026-07-08, not fork/archived) confirmed. Downgraded A to B only because the baseline benchmark code is not public.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/rossanoventurini/qwt>
  - <https://github.com/rossanoventurini/qwt/commits>
  - <https://github.com/rossanoventurini/qwt/tree/benchmark>
  - <https://raw.githubusercontent.com/rossanoventurini/qwt/HEAD/README.md>
  - <https://raw.githubusercontent.com/rossanoventurini/qwt/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/rossanoventurini/qwt/HEAD/README.md>
  - <https://raw.githubusercontent.com/rossanoventurini/qwt/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/rossanoventurini/qwt/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/rossanoventurini/qwt/HEAD/src/quadwt/mod.rs>
  - <https://raw.githubusercontent.com/rossanoventurini/qwt/HEAD/src/qvector/mod.rs>
  - <https://raw.githubusercontent.com/rossanoventurini/qwt/HEAD/src/qvector/rs_qvector.rs>
  - <https://raw.githubusercontent.com/rossanoventurini/qwt/HEAD/src/utils/mod.rs>
  - <https://github.com/rossanoventurini/qwt/issues?q=is%3Aissue>
  - <https://github.com/rossanoventurini/qwt/issues/3>
  - <https://github.com/rossanoventurini/qwt/issues/11>
  - <https://github.com/rossanoventurini/qwt/issues/19>
  - <https://crates.io/api/v1/crates/qwt>
  - <https://crates.io/api/v1/crates/rand/0.10.1>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/rossanoventurini/qwt`) · [data/wave9/enrich/raw/github_com_rossanoventurini_qwt.json](../../../data/wave9/enrich/raw/github_com_rossanoventurini_qwt.json) (enrichment confidence 0.85)

</details>
