# sliceslice (Rust AVX2 substring search)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Assembly-level string and memory routines](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `MIT` · 🟡 stale

> Rust crate for SIMD substring-existence search (Mula's generic SIMD); beat Rust 1.46 String::find 4.2-9.8x in Cloudflare's benchmark.

| | |
|---|---|
| **Beats** | Rust std String::find (also memmem, twoway crates and WojciechMula/sse4-strstr in the same table); not libc |
| **Claimed result** | README table (criterion): short haystack String::find 335.56 ms vs sliceslice DynamicAvx2Searcher 79.416 ms (4.2x, mostly setup cost excluded; prebuilt scalar memmem 0.1.1 88.029 ms, 1.11x derived); long haystack 9.8x (real SIMD gain); rebar 2026-07-30: memchr::memmem prebuilt beats sliceslice on ports of these workloads (i386 8.57 vs 10.33 ms, short 6.20 vs 16.13 ms) |
| **Workload** | Criterion 'i386' benchmark (benches/i386.rs at tag v0.2.1; now bench/benches/i386.rs): short haystack: words of data/words.txt sorted by length, each searched in every later word; long haystack: every word searched in data/i386.txt (read with fs::read and from_utf8_lossy at v0.2.1, include_bytes in the current bench); single-pattern substring search returning a bool. sliceslice and memmem searchers are constructed outside the timed loop; String::find, twoway and sse4-strstr build per call. |
| **Metric** | throughput |
| **Hardware** | HP EliteDesk 800 G2 Tower PC, Intel Core i7-6700 @ 3.40GHz, 16GB RAM, Ubuntu 20.04.1 LTS |
| **Compiler and flags** | Rust 1.46.0 and gcc 9.3.0 (README). The published table was produced by the v0.2.1-era harness (benches/i386.rs at tag v0.2.1, criterion 0.3, no [profile.bench] override, so cargo bench defaults at opt-level 3; the sse4-strstr C++ wrapper is compiled by sse4-strstr/build.rs with -std=c++11 -march=native). The current bench/ crate (criterion 0.5, [profile.bench] lto = true, codegen-units = 1) came later and was not used for the README numbers. |
| **Adoption** | 106 stars; by Cloudflare |
| **Last commit** | 2024-09-20 |
| **Links** | [repository](https://github.com/cloudflare/sliceslice-rs) · [benchmark](https://raw.githubusercontent.com/cloudflare/sliceslice-rs/HEAD/README.md) |

## Verdict

Cloudflare's README reports the i386 Criterion benchmark on an Intel Core i7-6700 with Rust 1.46.0 and gcc 9.3.0. sliceslice 0.2.0 DynamicAvx2Searcher took 79.4 ms against 335.6 ms for Rust std String::find on the word-in-word workload, and 35.2 ms against 345.0 ms when searching every word in an i386 manual text (4.2x and 9.8x, derived from page data). Prebuilt searchers make the short-haystack comparison uneven. BurntSushi's rebar record (memchr repo, 2026-07-30, sliceslice 0.4.3, CPU not stated in the CSV) independently shows oneshot sliceslice 2.17x faster than libc memmem and 3.9x faster than Rust std memmem, but 0.96x against memchr::memmem oneshot and 0.90x against it prebuilt (geometric means, derived from the CSV).

## Use it when

- Rust code that tests the same fixed needle against many haystacks and needs only a yes or no answer, such as matching records or headers against a keyword list
- x86_64 machines with AVX2 (Haswell or later); aarch64 NEON and wasm32 simd128 searchers also exist
- Replacing str::find or str::contains in a hot loop: in BurntSushi's rebar record (2026-07-30, sliceslice 0.4.3), oneshot sliceslice is about 3.9x faster than Rust std memmem by geometric mean (faster on 34 of 38 benchmarks) and about 2.17x faster than libc memmem (faster on 30 of 39) (derived from the CSV)
- Inputs where rebar shows it ahead of memchr::memmem prebuilt: code search (rust-library-rare-fn-from-str, about 4.6x), random bytes (seemingly-random, 47.71 vs 70.87 us), and rare-repeated-small-tricky (about 1.5x) (derived from the CSV)

## Skip it when

- You need the match offset or an iterator over matches; the API returns only a bool
- You already use memchr::memmem: with prebuilt searchers on both sides, memchr 2.8.3 wins 27 of 42 rebar benchmarks (sliceslice geomean 0.90x), including rebar's ports of sliceslice's own workloads: i386 8.57 ms for memchr vs 10.33 ms, and short words 6.20 ms vs 16.13 ms (derived from the 2026-07-30 CSV)
- Adversarial or low-entropy inputs: it has no linear worst-case bound. On rebar's defeat-simple-vector-freq-alphabet it takes 201.94 us against 37.05 us for libc memmem and 25.52 us for memchr (about 5.5x and 7.9x slower), and on defeat-simple-vector-repeated-alphabet it runs at 0.43x of memchr. In issue #40 BurntSushi traced the repeated-alphabet case to sliceslice thrashing in memcmp on false candidates.
- C or C++ projects: it is a Rust crate with no C API
- Long-lived dependencies: the last release is 0.4.3 (2024-06-29), the last commit is 2024-09-20, and issues #25 (safety documentation), #39 (no_std), #40, #41 and #97 are open

## How it is fast

It implements Wojciech Mula's 'generic SIMD' strstr. The first needle byte and one other byte (by default the last, but any position can be chosen to resist worst-case inputs) are broadcast into vectors. Each step compares 32 haystack positions at once using two loads offset by that position, ANDs the two equality masks, and confirms each remaining candidate with memcmp. DynamicAvx2Searcher monomorphises needles of 2 to 16 bytes into fixed-size arrays so the confirming memcmp has a constant length, sends 1-byte needles to memchr, and uses 16-, 8-, 4- and 2-lane SSE variants for short haystacks. The tail is handled by an overlapping, masked final chunk instead of reading past the end of the haystack.

## Compared with alternatives

Pick it over memx-cdy (a Rust memmem with a C ABI) when you are in Rust, reuse a fixed needle many times and only need a bool; pick memx-cdy when you need a C ABI or match positions. WojciechMula's toys strstr and sse4-strstr implement the same algorithm for C++; use them from C++ but note that sse4-strstr reads past the end of the haystack, which sliceslice avoids.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | cfg-if, paste, memchr (&gt;= 2.3), seq-macro |
| **Minimum toolchain** | Rust edition 2021 (implies Rust 1.56 or later; no rust-version field); the stdsimd feature needs nightly (portable_simd) |
| **Platforms** | x86_64 with AVX2 required at run time (no automatic CPU dispatch); aarch64 NEON (built in CI but its tests are not run there); wasm32 simd128 (tested under wasmtime in CI); any target with nightly portable SIMD via StdSimdSearcher |
| **Thread safety** | not documented; search_in takes &self and a searcher holds only the needle and two broadcast vectors, so sharing a built searcher across threads should be safe by Rust's auto traits |
| **Drop-in for the baseline** | partial — it replaces only the existence check (str::contains or find(..).is_some()) and requires prebuilding an unsafe searcher per needle; it returns no position |

## Gotchas

- The 'Dynamic' in DynamicAvx2Searcher refers to choosing a specialisation by needle length; it does not detect the CPU. new and search_in are `unsafe` and marked #[target_feature(enable = "avx2")], so calling them on a CPU without AVX2 is undefined behaviour. Gate the calls with is_x86_feature_detected!("avx2"). The safety contract is undocumented (issue #25, open since 2020).
- Harness flaw behind the README's 4.2x short-haystack figure: the sliceslice and memmem rows build their searchers outside the timed loop, while String::find rebuilds its Two-Way searcher on every call (benches/i386.rs at v0.2.1). The scalar, prebuilt memmem 0.1.1 TwoWaySearcher measures 88.029 ms against sliceslice's 79.416 ms in the same table (1.11x, derived from page data), so most of the short-haystack gain is excluded setup cost, not SIMD. The 9.8x long-haystack figure is a real SIMD gain: prebuilt memmem is slower than String::find there (401.59 vs 345.01 ms).
- Issue #97 (January 2025, no reply, no reproducer) says Avx2Searcher reads past the haystack in vector_search_in_chunk. A reading of src/lib.rs and src/x86.rs at HEAD this session suggests the claim is unfounded: inlined_search_in passes end = haystack.len() - needle.size() + 1, only chunks below end are loaded, and with_position asserts position &lt; needle.size(), so start + position + LANES &lt;= haystack.len(). CI also runs the tests, which try every position for each needle, under AddressSanitizer. This was not tested here. The README's out-of-bounds footnote refers to sse4-strstr, not sliceslice.
- Docs have drifted: the x86.rs doc comment still describes a scalar Rabin-Karp fallback for very short haystacks, which 0.3.1 removed while fixing the Rust 1.52 regression (#47). The README table still shows 0.2.0 on Rust 1.46 and omits the memchr::memmem rows that the current bench runs.

## Known shortcomings

- README numbers exact (4.2x, 9.8x derived) but the baseline is Rust 1.46 std String::find, not libc, with prebuilt searchers vs oneshot std; the table came from the v0.2.1 harness (criterion 0.3, default bench profile), not the current LTO bench; rebar 2026-07-30: 2.17x over libc memmem but slower than memchr prebuilt on 27 of 42; open OOB-read issue #97.
- Enricher: the README 4.2x short-haystack row mostly excludes setup cost (sliceslice and memmem searchers are prebuilt outside the timed loop while String::find rebuilds Two-Way per call; prebuilt scalar memmem 0.1.1 gets 88.029 ms vs sliceslice 79.416 ms, 1.11x derived), the long-haystack 9.8x is a real SIMD gain; rebar's 2026-07-30 CSV has prebuilt memchr::memmem beating sliceslice on ports of sliceslice's own workloads (i386 8.57 vs 10.33 ms, short 6.20 vs 16.13 ms) and the pathological defeat-simple-vector-freq-alphabet case runs 201.94 us vs libc memmem 37.05 us; the issue #97 out-of-bounds read looks unfounded on code reading (CI runs tests under ASan); the crate also has aarch64 NEON, wasm32 simd128 and nightly stdsimd searchers; 'Dynamic' means needle-length specialisation, not CPU dispatch (UB without AVX2).

## Caveats and trade-offs

Baseline is Rust 1.46 std String::find (2020), not libc memmem or any C++ std; README numbers are for sliceslice 0.2.0 on 2020 toolchains with the v0.2.1 harness, and the README table omits the memchr::memmem rows the current bench now runs. The benchmark is asymmetric: sliceslice (and memmem) searchers are prebuilt outside the timed loop while String::find rebuilds its Two-Way searcher per call, so needle preprocessing is excluded only for the prebuilt rows. In BurntSushi's memchr rebar record (benchmarks/record/x86_64/2026-07-30.csv, sliceslice 0.4.3) sliceslice oneshot is about 2.17x faster than libc memmem by geomean of medians over 39 benchmarks (faster on 30) and about 3.9x faster than Rust std memmem oneshot (faster on 34 of 38), but prebuilt sliceslice beats memchr 2.8.3 prebuilt on only 15 of 42 benchmarks (geomean 0.90x) (derived from that CSV; older records 2023-12-29 and 2025-09-25 give 2.08x and 2.14x vs libc). Open issue #97 (January 2025, no maintainer reply) reports that Avx2Searcher can read past the end of the haystack (OOB read in vector_search_in_chunk); the API is unsafe and x86 AVX2 only; issue #47 recorded a performance regression with Rust 1.52. [retier] Setup cost excluded on the sliceslice side of the short-haystack row; memchr::memmem ahead in rebar; pathological defeat-simple-vector-freq-alphabet case 201.94 us vs libc memmem 37.05 us; also ships aarch64 NEON, wasm32 simd128 and nightly stdsimd searchers; 'Dynamic' is needle-length specialisation, not CPU dispatch (UB without AVX2); issue #97 OOB report unfounded on code reading

Rust crate (no C API); x86 AVX2 searcher built on Wojciech Mula's SIMD-friendly algorithm with the needle fixed at construction, and unlike sse4-strstr it never reads past the end of the haystack (README footnote).

## Maintenance

Stale (last release 0.4.3 on 2024-06-29, last commit 2024-09-20, issues unanswered since 2021) but MIT-licensed, about 2,000 lines of Rust and heavily downloaded (7.59M from crates.io, 1.65M recently); usable as is, though memchr::memmem is the maintained and usually faster default.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** README table compares sliceslice 0.2.0 against Rust std 1.46.0 String::find (plus memmem, twoway, sse4-strstr) with the i386 Criterion benchmark that is public at tag v0.2.1 (benches/i386.rs, now bench/benches/i386.rs), Rust 1.46.0 and gcc 9.3.0 stated, build flags public in the tagged Cargo.toml and sse4-strstr/build.rs (default cargo bench profile, -std=c++11 -march=native for the C++ row), and CPU Intel Core i7-6700 stated.
- **Verifier notes:** Numbers match the README exactly (335.56 vs 79.416 ms, 345.01 vs 35.181 ms; 4.2x and 9.8x derived). Record's flags described the current bench crate (criterion 0.5, LTO, codegen-units=1), which postdates the 2020 table; corrected to the v0.2.1 harness. Shortcomings: Rust-std baseline rather than libc/C++, prebuilt-vs-oneshot asymmetry, slower than memchr::memmem prebuilt on most rebar benchmarks, open OOB-read soundness issue #97; metadata (MIT, 106 stars, last commit 2024-09-20, stale) checked.
- **Fields the verifier corrected:** `compiler_and_flags`, `workload`, `caveats`, `claimed_speedup`
- **Shortcomings recorded by:** verifier batch-27 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/cloudflare/sliceslice-rs/HEAD/README.md>
  - <https://github.com/cloudflare/sliceslice-rs>
  - <https://github.com/cloudflare/sliceslice-rs/commits>
  - <https://github.com/cloudflare/sliceslice-rs/tags>
  - <https://github.com/cloudflare/sliceslice-rs/issues?q=is%3Aissue>
  - <https://github.com/cloudflare/sliceslice-rs/issues/97>
  - <https://github.com/cloudflare/sliceslice-rs/issues/40>
  - <https://raw.githubusercontent.com/cloudflare/sliceslice-rs/HEAD/bench/Cargo.toml>
  - <https://raw.githubusercontent.com/cloudflare/sliceslice-rs/HEAD/bench/benches/i386.rs>
  - <https://raw.githubusercontent.com/cloudflare/sliceslice-rs/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/cloudflare/sliceslice-rs/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/cloudflare/sliceslice-rs/v0.2.1/README.md>
  - <https://raw.githubusercontent.com/cloudflare/sliceslice-rs/v0.2.1/Cargo.toml>
  - <https://raw.githubusercontent.com/cloudflare/sliceslice-rs/v0.2.1/benches/i386.rs>
  - <https://raw.githubusercontent.com/cloudflare/sliceslice-rs/v0.2.1/sse4-strstr/build.rs>
  - <https://github.com/BurntSushi/memchr/tree/master/benchmarks/record/x86_64>
  - <https://raw.githubusercontent.com/BurntSushi/memchr/master/benchmarks/record/x86_64/2026-07-30.csv>
  - <https://raw.githubusercontent.com/BurntSushi/memchr/master/benchmarks/record/x86_64/2025-09-25.csv>
  - <https://raw.githubusercontent.com/BurntSushi/memchr/master/benchmarks/record/x86_64/2023-12-29.csv>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/cloudflare/sliceslice-rs/HEAD/README.md>
  - <https://raw.githubusercontent.com/cloudflare/sliceslice-rs/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/cloudflare/sliceslice-rs/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/cloudflare/sliceslice-rs/HEAD/src/x86.rs>
  - <https://raw.githubusercontent.com/cloudflare/sliceslice-rs/HEAD/src/aarch64.rs>
  - <https://raw.githubusercontent.com/cloudflare/sliceslice-rs/HEAD/src/wasm32.rs>
  - <https://raw.githubusercontent.com/cloudflare/sliceslice-rs/HEAD/src/stdsimd.rs>
  - <https://raw.githubusercontent.com/cloudflare/sliceslice-rs/HEAD/src/multiversion.rs>
  - <https://raw.githubusercontent.com/cloudflare/sliceslice-rs/HEAD/.github/workflows/check.yml>
  - <https://raw.githubusercontent.com/cloudflare/sliceslice-rs/HEAD/bench/Cargo.toml>
  - <https://raw.githubusercontent.com/cloudflare/sliceslice-rs/HEAD/bench/benches/i386.rs>
  - <https://raw.githubusercontent.com/cloudflare/sliceslice-rs/v0.2.1/README.md>
  - <https://raw.githubusercontent.com/cloudflare/sliceslice-rs/v0.2.1/Cargo.toml>
  - <https://raw.githubusercontent.com/cloudflare/sliceslice-rs/v0.2.1/benches/i386.rs>
  - <https://raw.githubusercontent.com/cloudflare/sliceslice-rs/v0.2.1/sse4-strstr/build.rs>
  - <https://github.com/cloudflare/sliceslice-rs/issues?q=is%3Aissue>
  - <https://github.com/cloudflare/sliceslice-rs/issues/97>
  - <https://github.com/cloudflare/sliceslice-rs/issues/40>
  - <https://github.com/cloudflare/sliceslice-rs/issues/47>
  - <https://crates.io/api/v1/crates/sliceslice>
  - <https://crates.io/api/v1/crates/sliceslice/reverse_dependencies>
  - <https://raw.githubusercontent.com/BurntSushi/memchr/master/benchmarks/record/x86_64/2026-07-30.csv>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/cloudflare/sliceslice-rs`) · [data/wave13/enrich/raw/github_com_cloudflare_sliceslice_rs.json](../../../data/wave13/enrich/raw/github_com_cloudflare_sliceslice_rs.json) (enrichment confidence 0.8)

</details>
