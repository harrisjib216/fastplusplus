# constriction

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Entropy coders](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT OR Apache-2.0 OR BSL-1.0` · 🟢 active

> Rust/Python rANS and range coders with near-optimal bit rates; decodes 6-14x faster than the arcode arithmetic coder.

| | |
|---|---|
| **Beats** | arithmetic coding as implemented in the arcode crate (cgbur/arcode-rs) |
| **Claimed result** | Default ANS (24/32/64): 24.2 ns/symbol encode and 6.1 ns/symbol decode with 0.0015% bit-rate overhead. Default range coder (24/32/64): 16.6 / 14.3 ns/symbol with 0.0237% overhead. arcode arithmetic coding baseline: 43.2 / 85.6 ns/symbol with 0.0004% overhead. About 14x faster decode for ANS and 6x for RC, and 1.8x and 2.6x faster encode (all derived from page data). |
| **Workload** | Encode and decode of 3-million-symbol i.i.d. messages spanning 0.001 to 10 bits per symbol, from a real-world application, aggregated over all messages. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-7500U CPU (2.70 GHz) |
| **Compiler and flags** | rustc via 'cargo run --release' (default release profile, no custom RUSTFLAGS in benchmarks/Cargo.toml); rustc version not stated |
| **Adoption** | 108 stars |
| **Last commit** | 2026-07-17 |
| **Links** | [repository](https://github.com/bamler-lab/constriction) · [benchmark](https://github.com/bamler-lab/constriction) |

## Verdict

The author's benchmark (bamler-lab/understanding-ans, constriction 0.1.4 against the arcode 0.2.3 Rust crate, cargo run --release, rustc version not stated, Intel Core i7-7500U) encoded and decoded 3-million-symbol i.i.d. messages from 0.001 to 10 bits/symbol: default ANS took 24.2 / 6.1 ns per symbol and default range coding 16.6 / 14.3, against 43.2 / 85.6 for arcode arithmetic coding, all within 0.025% of the entropy. The baseline is a Rust arithmetic coder, not a C or C++ entropy coder, and the numbers predate the current 0.5.0 release.

## Use it when

- Learned or model-based compression (neural codecs, VAEs) where every symbol has its own probability model and you need about 0.002-0.02% bit-rate overhead with the default presets.
- Bits-back coding with latent-variable models: AnsCoder is a stack that allows encoding and decoding to be interleaved arbitrarily and is surjective, so decoding arbitrary bits and re-encoding restores them.
- Autoregressive models that decode in the same order they encode: use the range coder (FIFO) instead of ANS.
- Prototyping in Python and shipping in Rust or WebAssembly with bit-identical output across both.
- Low-entropy symbol streams (well below 1 bit/symbol) where Huffman and other symbol codes waste close to 1 bit per symbol.

## Skip it when

- Byte-oriented general-purpose entropy coding where you need GB/s throughput: the coders are single-stream and scalar (default ANS decode is 6.1 ns/symbol, roughly 160 M symbols/s on an i7-7500U), well below interleaved SIMD rANS or Huffman decoders such as hypersonic-rANS, htscodecs or Huff0.
- C or C++ projects that cannot take a Rust dependency: there is no C header or C ABI, so you need your own FFI layer.
- When the entropy model dominates: the docs warn that unless you use the lookup decoder models, evaluating the model, not the coder, is usually the bottleneck.
- Python on Linux aarch64: PyPI 0.5.0 ships wheels only for manylinux x86_64, macOS (x86_64 and arm64) and Windows amd64, so other platforms build from source.
- Bits-back coding with the range coder: the docs say it is not surjective, so it cannot be used reliably for that.

## How it is fast

Range variant of Asymmetric Numeral Systems (rANS, Duda) with a 64-bit state and 32-bit word renormalization, so decoding is a multiply, a CDF lookup and an occasional word read with few branches; the docs say ANS decoding is more than twice as fast as its range decoder, while ANS encoding pays for an integer division. Word size, state size and PRECISION are compile-time generics, so the inner loops monomorphize to fixed-width integer code. The 'small' presets (12-bit precision, 16/32-bit word/state) enable ContiguousLookupDecoderModel and NonContiguousLookupDecoderModel, which replace the CDF search with a direct table lookup. There is no SIMD or multi-stream interleaving.

## Compared with alternatives

Pick constriction over ryg_rans, htscodecs or hypersonic-rANS when you need per-symbol adaptive models from continuous distributions, bits-back coding or a Python API with matching Rust output, not raw byte throughput; for static byte histograms at GB/s those siblings (or FiniteStateEntropy/Huff0) are far faster. Against torch_ans it is the CPU option with exact fixed-point model quantization rather than a GPU batch decoder.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | hashbrown, num-traits, smallvec, libm, probability; optional pyo3 and numpy for the Python extension |
| **Minimum toolchain** | Rust 1.85 per Cargo.toml rust-version (the README still says 1.75); Python 3.10-3.14 for the 0.5.0 wheels |
| **Platforms** | any Rust target including no_std and WebAssembly; Python wheels for Linux x86_64, macOS x86_64/arm64, Windows amd64 |
| **Thread safety** | not documented; coders are plain owned structs (Vec-backed), so use one coder per thread |
| **Drop-in for the baseline** | no |

## Gotchas

- ANS is LIFO: you must encode symbols in reverse (encode_symbols_reverse / encode_iid_symbols_reverse) to decode them in forward order.
- Default presets (24-bit precision) must not be used with the lookup decoder models: the docs say the tables grow to about 67 MB; use the 12-bit 'small' presets for those, at about 4% bit-rate overhead in the README table.
- Model construction from floating point can differ across architectures: issue #38 reports a panic ('assertion failed: b &gt; 0.0' in the probability crate's Laplace distribution) on ARM for input that encoded fine on amd64; issue #20 reported an infinite loop in optimize_leaky_categorical for inputs like [0.15, 0.69, 0.15] (closed).
- Any change to encoder or decoder output is treated as a breaking change that bumps the leading nonzero version number, so pin the minor version (0.5.x) when compressed data must stay decodable.

## Known shortcomings

- Downgraded B to C: the paper (arXiv 2201.01741) is a preprint, not peer-reviewed; the bench code is public (understanding-ans/benchmarks, cargo --release pinning constriction 0.1.4) but no rustc version. Rust with no C or C++ API.
- No C/C++ API (Rust and Python only), FFI needed. Scalar single-stream coders, far below SIMD rANS on byte throughput. Cargo.toml rust-version 1.85 while README says 1.75. Issue #38: ARM panic 'assertion failed: b &gt; 0.0' with the Laplace model from float differences. The 24-bit default presets are unusable with lookup models (about 67 MB tables). The cited benchmark ran constriction 0.1.4; current is 0.5.0.

## Caveats and trade-offs

First-party benchmark from the author's arXiv preprint (arXiv:2201.01741, Section 5.2), not peer-reviewed. The benchmark code (bamler-lab/understanding-ans/benchmarks, 10 timed runs per message with cool-down pauses) is public but pins constriction 0.1.4 and arcode 0.2.3, so the README numbers describe an old library version. rustc version not stated. Baseline is a Rust arithmetic coder (arcode crate), not Huffman, rANS or Huff0, and nothing in C or C++; not compared against FSE, Huff0 or ryg_rans. The arcode coder has a slightly lower bit-rate overhead (0.0004% versus 0.0015% for default ANS).

Rust library with Python bindings; no C or C++ API, so use from C++ needs an FFI wrapper. ANS is last-in-first-out (suits bits-back coding), RC is first-in-first-out. Models are user-supplied (probability tables), so this measures the coder core, not a full compressor. Small-precision presets trade 4% bit-rate overhead for speed.

## Maintenance

Actively maintained (0.5.0 released to crates.io and PyPI on 2026-07-17, about 35k crate downloads) and triple-licensed MIT, Apache-2.0 or BSL-1.0, so it is easy to depend on from Rust; use from C++ needs a hand-written FFI shim.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification B, tier now C.
- **Tier reason:** The README Benchmarks table (Intel Core i7-7500U) shows ANS default 24.2/6.1 ns/symbol, RC default 16.6/14.3 and arcode AC 43.2/85.6, and the benchmark code is public (bamler-lab/understanding-ans/benchmarks, run with cargo run --release). But the numbers are first-party, no rustc version is stated, and the paper (arXiv:2201.01741) is an arXiv preprint, not peer-reviewed, so the B route does not apply.
- **Verifier notes:** All claimed numbers and derived ratios (14x/6x decode, 1.8x/2.6x encode) match the README table. Downgraded B to C because the paper is an arXiv-only preprint (WebSearch result) and the run is first-party; it is close to A apart from the missing rustc version. Metadata confirmed: MIT OR Apache-2.0 OR BSL-1.0, 108 stars, last commit 2026-07-17, not archived or a fork.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier; first-party benchmark
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/bamler-lab/constriction/HEAD/README.md>
  - <https://github.com/bamler-lab/constriction>
  - <https://github.com/bamler-lab/constriction/commits>
  - <https://raw.githubusercontent.com/bamler-lab/understanding-ans/HEAD/README.md>
  - <https://github.com/bamler-lab/understanding-ans/tree/main/benchmarks>
  - <https://raw.githubusercontent.com/bamler-lab/understanding-ans/HEAD/benchmarks/Cargo.toml>
  - <https://raw.githubusercontent.com/bamler-lab/understanding-ans/HEAD/benchmarks/README.md>
- **Sources the enricher read:**
  - <https://github.com/bamler-lab/constriction>
  - <https://raw.githubusercontent.com/bamler-lab/constriction/HEAD/README.md>
  - <https://raw.githubusercontent.com/bamler-lab/constriction/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/bamler-lab/constriction/HEAD/src/stream/stack.rs>
  - <https://raw.githubusercontent.com/bamler-lab/constriction/HEAD/src/stream/queue.rs>
  - <https://raw.githubusercontent.com/bamler-lab/constriction/HEAD/src/stream/mod.rs>
  - <https://raw.githubusercontent.com/bamler-lab/constriction/HEAD/src/lib.rs>
  - <https://github.com/bamler-lab/constriction/issues?q=is%3Aissue>
  - <https://github.com/bamler-lab/constriction/issues/38>
  - <https://github.com/bamler-lab/constriction/issues/20>
  - <https://pypi.org/pypi/constriction/json>
  - <https://crates.io/api/v1/crates/constriction>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/bamler-lab/constriction`) · [data/wave9/enrich/raw/github_com_bamler_lab_constriction.json](../../../data/wave9/enrich/raw/github_com_bamler_lab_constriction.json) (enrichment confidence 0.8)

</details>
