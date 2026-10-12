# hilbert_curves (rawrunprotected)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `public domain (README statement, no LICENSE file)` · 🔴 abandoned

> Branchless public-domain 2D/3D Hilbert index encode/decode; a Rust port encodes about 5.4x faster than the classic rotation loop.

| | |
|---|---|
| **Beats** | classic iterative xy2d Hilbert index loop with per-level quadrant rotation (Wikipedia-style loop; measured as loop_rotation in the Rust port benchmark), not literally the Hacker's Delight code |
| **Claimed result** | Port benchmark: magic_bits 185 us per 100k points (541 Melem/s) against loop_rotation 998 us (100 Melem/s), about 5.4x (derived from page data); also 3.5x faster than the fast_hilbert crate (644 us, 155 Melem/s) and within a few percent of static_aabb2d_index's reference encoder (183 us). The repo itself only says 'the world's fastest implementations of 2D and 3D hilbert curve functions' with no numbers. |
| **Workload** | Evidence is for a Rust port, not this repo: the magic_bits encoder in Filyus/packed_spatial_index (a port of this repo's hilbertXYToIndex) against its loop_rotation encoder, encoding 100,000 random (u16, u16) points into an output buffer with Criterion, single pinned core. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen AI 7 350 (Zen 5 laptop), benchmark thread pinned to one performance core |
| **Compiler and flags** | Rust, Cargo bench profile with lto = true and codegen-units = 1 (from Cargo.toml); rustc version and RUSTFLAGS for this table not stated |
| **Adoption** | 82 stars; ported by Filyus/packed_spatial_index (Rust magic_bits, attributed in its source) and jbenison/hilbert (64-bit C++); the port's source says the same algorithm family is used inside static_aabb2d_index (the Rust Flatbush port) |
| **Last commit** | 2016-09-18 |
| **Links** | [repository](https://github.com/rawrunprotected/hilbert_curves) · [benchmark](https://raw.githubusercontent.com/Filyus/packed_spatial_index/HEAD/docs/performance.md) |

## Verdict

The repo has no numbers. The only measurement is of Filyus/packed_spatial_index's magic_bits, a line-for-line Rust port of hilbertXYToIndex fixed at order 16. It encoded 100,000 random (u16, u16) points in 185 us, against 998 us for the classic loop_rotation encoder (about 5.4x, derived from page data) and 644 us for fast_hilbert 2.1.0. The run used Criterion with LTO and codegen-units = 1, on a Ryzen AI 7 350 with the thread pinned to one core; the rustc version and target-cpu are not stated. The harness looks fair: all encoders run the same loop with black_box only on the buffers, and their outputs are identical. But the ratio mixes the algorithm with auto-vectorization, which the branchy baseline cannot get.

## Use it when

- Bulk-loading a packed Hilbert R-tree or sorting items by Hilbert key, with coordinates quantized to 16 bits per axis (the Flatbush and static_aabb2d_index approach; both embed ports of this exact function).
- Encoding large arrays of independent points, where the branchless body auto-vectorizes. In the port's benchmark this was 5.4x faster than the rotation loop and 3.5x faster than the fast_hilbert crate.
- When you need decode (index to x, y) as well as encode, with run time that does not depend on the data.
- 3D Hilbert ordering when you already have Morton codes of up to 30 bits (10 levels per axis), for example from a pdep- or magic-bits interleaver.
- When you want public-domain code to vendor; JS and Rust ports already exist.

## Skip it when

- Coordinates wider than 16 bits per axis in 2D, or 10 bits in 3D: every index is 32-bit, and nothing here produces 64-bit codes.
- Single calls in a dependent latency chain: the port's notes say its table-driven LUT encoder wins there. The 5.4x figure is batch throughput only.
- When Z-order is good enough: in the same port benchmark, Morton encoding took 47 us per 100k points against 185 us for this encoder.
- When you need a maintained, packaged library with tests, or more than three dimensions, or other curve variants: this is four commits from 2016 with none of these.
- 3D throughput-critical code: the 3D functions are a serial table walk, take Morton codes rather than x/y/z, and no one has benchmarked them.

## How it is fast

The 2D encoder runs the per-level quadrant-rotation state machine as a parallel prefix scan over all 16 levels at once, using log2(16) = 4 rounds of XOR/AND/shift on bit-sliced state words, then bit-interleaves the result. The decoder uses the same prefix-scan idea, so both directions run in constant time with no branches and no memory lookups. Because nothing depends on the data, a compiler can auto-vectorize a loop over many points. The 3D path is different: it walks multiplication tables of the alternating group A4 (pre-combined with the Morton-to-Hilbert mapping), one 3-bit digit per step.

## Compared with alternatives

Flatbush already contains a JS port of this exact function, credited in its index.js, for its packed Hilbert R-tree. Pick this repo when you want the raw encoder/decoder in C++ to build your own packed index or sort keys, not a finished spatial index such as Flatbush, KDBush or nanoflann.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (only &lt;cstdint&gt;) |
| **Minimum toolchain** | C++11 (uses &lt;cstdint&gt; fixed-width types; no intrinsics or other language features) |
| **Platforms** | any (portable 32-bit unsigned integer arithmetic, no SIMD intrinsics or platform code) |
| **Thread safety** | Not documented. From the code: pure functions plus read-only static tables, so concurrent calls are safe. |
| **Drop-in for the baseline** | partial — it computes the same index as the classic xy2d/d2xy rotation loop (checked against the port's loop_rotation), but it takes the curve order n in bits, not the grid side length, and it is capped at n = 16 |

## Gotchas

- No input checking. n must be 1 to 16: n = 0 shifts a uint32_t by 32, which is undefined behavior, and n &gt; 16 gives a negative shift count. Coordinates must also be below 2^n. They are not masked, so an out-of-range coordinate silently returns a different, in-range index. In a Python transcription at n = 4, (x=17, y=3) gave index 12, while (x=1, y=3) gave 6.
- The file defines external-linkage free functions with generic names (interleave, deinterleave, prefixScan, descan, transformCurve) in the global namespace, and there is no header. Compiling it into more than one translation unit, or next to other bit-twiddling helpers, causes duplicate-symbol link errors. Wrap it in a namespace and mark the functions inline or static when vendoring.
- The 3D functions convert between Morton and Hilbert codes, not x/y/z, so you need your own 3D bit interleaver. Use bits of 10 or less: at 11, the code needs 33 bits and the top digit is truncated.
- No correctness bug was found. A Python transcription of the C++ was checked exhaustively for 2D orders 1 to 8 and 3D levels 1 to 5, plus 200,000 random 2D points at order 16 and 100,000 random 3D codes at 10 levels. Results: bijective, consecutive indices are unit steps apart, encode/decode round-trips, and 2D output equals the classic rotation loop. The decoder and the 3D functions have never been benchmarked by anyone.

## Known shortcomings

- No numbers in the repo; the only evidence is a Rust port (Filyus packed_spatial_index magic_bits, attributed in src/hilbert2d.rs): 185 us vs loop_rotation 998 us per 100k, about 5.4x, rustc version unstated. Informal public-domain dedication with no patent grant; abandoned since 2016.
- Enricher: no correctness bug in the transcribed algorithm (2D orders 1-8 and 3D levels 1-5 exhaustive, plus random points), but no input checks: n=0 is undefined behaviour (32-bit shift by 32) and coordinates at or above 2^n silently give a wrong in-range index; global external-linkage names with no header clash in multi-TU links; 3D takes Morton codes (max 10 levels); decode and 3D were never benchmarked. The Rust port harness is fair but states no rustc version or target-cpu, and the 5.4x mixes the algorithm with auto-vectorisation the branchy baseline cannot get.

## Caveats and trade-offs

The repo has four commits, a README with no numbers, and a single hilbert_curves.cpp; the author's explanation posts (threadlocalmutex.com) were unreachable. The only numbers found are for a Rust port in another repo, so they support the algorithm, not this exact C++ file, and the hardware and Rust settings are not the C++ ones. The README dedication to the public domain is informal (no LICENSE file, no CC0 text) and carries no patent grant. The baseline loop is the port author's own Rust loop_rotation, not Hacker's Delight code, and libmorton was not part of any comparison found. Other Hilbert libraries found (becheran/fast-hilbert LUT, Wunkolo/qHilbert SIMD) benchmark against different baselines and do not measure this code; jbenison/hilbert (64-bit port) lists about 2 ns per call with no baseline. Treat as tier C by indirect evidence; if the verifier will not accept port evidence, the repo alone is tier D.

Branchless XOR/AND/shift arithmetic, constant time in curve order, 16 bits per axis in 2D (32-bit index) and a table-driven 3D conversion between Morton and Hilbert order that takes 3 index bits per level (a 32-bit code covers about 10 levels). Fastest when iterations are independent; the Rust port's own notes say a table-driven LUT wins in single-call dependent-accumulation latency loops.

## Maintenance

Abandoned since 2016-09-18 (4 commits, no pull requests, two closed 2018 issues), and the author's explanation posts on threadlocalmutex.com no longer resolve. Still copyable: about 150 lines released into the public domain by an informal README statement (no LICENSE file, no patent grant), with no correctness bug found and widely re-ported (Flatbush, static_aabb2d_index, packed_spatial_index).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The numbers are from a third-party Rust port (Filyus/packed_spatial_index src/hilbert2d.rs magic_bits, documented as 'a port of the rawrunprotected algorithm') measured with public Criterion code (benches/hilbert2d_bench.rs) on a named CPU, but the rustc version and RUSTFLAGS are not stated and the measured code is a port, not this C++ file; the repo itself has no numbers, so indirect evidence caps it at C.
- **Verifier notes:** Shortcoming: no numbers in this repo; evidence is a third-party Rust port (magic_bits 185 us vs loop_rotation 998 us per 100k points, about 5.4x derived from page data), rustc version not stated; informal public-domain dedication with no LICENSE file and no patent grant; abandoned since 2016-09-18. All performance.md numbers and the port attribution in src/hilbert2d.rs were confirmed.
- **Fields the verifier corrected:** `stars_or_usage`
- **Shortcomings recorded by:** verifier batch-180 (wave 8 seed pass, 2026-10-13); enricher (seed pass, 2026-10-13)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/Filyus/packed_spatial_index/HEAD/docs/performance.md>
  - <https://raw.githubusercontent.com/Filyus/packed_spatial_index/HEAD/src/hilbert2d.rs>
  - <https://raw.githubusercontent.com/Filyus/packed_spatial_index/HEAD/benches/hilbert2d_bench.rs>
  - <https://raw.githubusercontent.com/Filyus/packed_spatial_index/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/rawrunprotected/hilbert_curves/HEAD/README.md>
  - <https://github.com/rawrunprotected/hilbert_curves>
  - <https://github.com/rawrunprotected/hilbert_curves/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/rawrunprotected/hilbert_curves/HEAD/README.md>
  - <https://raw.githubusercontent.com/rawrunprotected/hilbert_curves/HEAD/hilbert_curves.cpp>
  - <https://github.com/rawrunprotected/hilbert_curves>
  - <https://github.com/rawrunprotected/hilbert_curves/commits>
  - <https://github.com/rawrunprotected/hilbert_curves/issues?q=is%3Aissue>
  - <https://github.com/rawrunprotected/hilbert_curves/pulls?q=is%3Apr>
  - <https://raw.githubusercontent.com/Filyus/packed_spatial_index/HEAD/docs/performance.md>
  - <https://raw.githubusercontent.com/Filyus/packed_spatial_index/HEAD/src/hilbert2d.rs>
  - <https://raw.githubusercontent.com/Filyus/packed_spatial_index/HEAD/benches/hilbert2d_bench.rs>
  - <https://raw.githubusercontent.com/Filyus/packed_spatial_index/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/Filyus/packed_spatial_index/HEAD/.cargo/config.toml>
  - <https://raw.githubusercontent.com/Filyus/packed_spatial_index/HEAD/README.md>
  - <https://raw.githubusercontent.com/mourner/flatbush/HEAD/index.js>
  - <https://raw.githubusercontent.com/jbuckmccready/static_aabb2d_index/HEAD/src/static_aabb2d_index.rs>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/rawrunprotected/hilbert_curves`) · [data/wave8/enrich/raw/github_com_rawrunprotected_hilbert_curves.json](../../../data/wave8/enrich/raw/github_com_rawrunprotected_hilbert_curves.json) (enrichment confidence 0.65)

</details>
