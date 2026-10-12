# msgspec-serde

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [Binary schemas](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Python` · `Apache-2.0` · 🟢 active

> Rust-backed Python FlatBuffers codegen producing msgspec Structs; \~19-22x faster encode, \~11-12x faster decode than official Python FlatBuffers.

| | |
|---|---|
| **Beats** | FlatBuffers (official Python API) |
| **Claimed result** | benchmarks.md text: 'approximately 20–22 times faster to encode and 11–13 times faster to materialize', selected-field access 'about 1.2 times faster', full traversal '1.5 to 2.9 times faster' than the official Python FlatBuffers API. The chart on the same page (benchmarks/images/python-flatbuffers-comparison.png, small/medium/large profiles) shows slightly lower figures: encode 18.7x/21.8x/20.7x, decode-to-model 10.6x/11.8x/11.6x, selected fields 1.2x/1.2x/1.3x, full traversal 1.4x/2.5x/2.8x. |
| **Workload** | Official-API comparison: a FlatBuffers 'Monster'-style schema at three profiles (small 100, medium 5,408 and large 1,118,720 logical elements), measuring encode of a materialized model, decode to a materialized model, lazy-view selected-field reads and lazy-view full traversal, with pyperf (6 processes x 5 values) on one isolated core. The separate 1,000-object File/Directory graph benchmark (16- and 256-value NumPy vectors) compares msgspec/orjson/ormsgpack and msgspec-serde's own JSON, MessagePack and FlatBuffers codecs, not the official FlatBuffers API. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-8650U CPU, single isolated core, Linux |
| **Compiler and flags** | CPython 3.13.5; msgspec 0.21.1, NumPy 2.5.2, Python FlatBuffers 25.12.19, flatc 23.5.2, msgspec-serde 0.1.0. The speed-critical path is a Rust pyo3 extension built by maturin with profile=release (pyproject.toml, rust/Cargo.toml, edition 2024); the rustc version is not stated. |
| **Adoption** | 1 star (repo created 2026-08-25; v0.1.0 and v0.1.1 released 2026-08-30) |
| **Last commit** | 2026-09-10 |
| **Links** | [repository](https://github.com/ebrevdo/msgspec-serde) · [benchmark](https://github.com/ebrevdo/msgspec-serde/blob/main/benchmarks.md) |

## Verdict

First-party pyperf run (6 processes x 5 values, one isolated core of an Intel Core i7-8650U, Linux, CPython 3.13.5) on a Monster-style schema at 100, 5,408 and 1,118,720 logical elements, against the flatc 23.5.2-generated Python Object API on flatbuffers 25.12.19 fed NumPy arrays. The chart shows encode 18.7x/21.8x/20.7x and decode-to-model 10.6x/11.8x/11.6x faster, selected-field view reads 1.2-1.3x and full view traversal 1.4-2.8x faster (the prose rounds these to 20-22x, 11-13x, 1.2x and 1.5-2.9x). The speed comes from a release-mode Rust extension with no stated rustc version, and the baseline is pure-Python FlatBuffers, not the C++ library.

## Use it when

- A Python 3.12+ codebase that already uses msgspec Structs and must exchange FlatBuffers with C++/Rust/Go producers or consumers.
- The official Python Object API (Pack / InitFromPackedBuf) is your bottleneck for encoding or fully materializing FlatBuffers. The measured gains were \~19-22x on encode and \~11-12x on decode, from 100 to 1.1M logical elements.
- Payloads dominated by large numeric vectors: views expose them as zero-copy NumPy arrays, and with 256-value vectors its FlatBuffers codec beat its own JSON and MessagePack codecs in both directions.
- msgspec Structs with NumPy array fields sent over JSON or MessagePack. Its native codecs were \~1.2-4.5x faster than msgspec with enc/dec array hooks in the repo's 1,000-object benchmark.
- Free-threaded CPython 3.14t: the extension declares gil_used=false, and CI asserts that the GIL stays disabled after import.

## Skip it when

- Reading only a few fields from each buffer: views are pure Python and only \~1.2-1.3x faster than the official API.
- JSON or MessagePack with small vectors or plain Python lists. With 16-value vectors its codecs took 1.3-2.3x as long as plain msgspec on Python lists (also behind orjson and ormsgpack), and it won only at 256-value vectors.
- Schemas the generator rejects: unions with string or struct alternatives, duplicate-target union aliases, 64-bit offsets, or identical short names from different namespaces in one-file generation.
- Python &lt; 3.12, or platforms without prebuilt wheels. Wheels cover Linux and macOS on x86-64/aarch64 and Windows x86-64, with no Windows 3.14t wheel; building from the sdist needs a Rust toolchain.
- Anything needing API stability: v0.1.x with 1 star, created 2026-08-25, and the docs call generated-code backward compatibility 'a goal rather than a guarantee'.

## How it is fast

Each generated module embeds a schema 'plan', serialized as MessagePack, that a pyo3 Rust extension compiles once into a NativePlan. Encoding walks the Struct with the Rust `flatbuffers` 25.12.19 FlatBufferBuilder. It copies NumPy numeric vectors in bulk through the buffer protocol and sizes the output buffer up front from a stratified-sample estimate, so it skips the official Object API's per-field Python calls. Decoding to a model is a Rust walker with checked offset arithmetic that builds msgspec Structs and owning NumPy arrays directly. Lazy views are pure Python (struct.unpack_from with per-field caching, plus zero-copy read-only NumPy arrays for numeric vectors), which is why selected-field reads gain only \~1.2x.

## Compared with alternatives

Pick it over msgspec when you need FlatBuffers schemas and interop or large NumPy vectors inside msgspec Structs; plain msgspec stays faster for list-based JSON/MessagePack with small vectors. Karmem (Go, its own format) and flatcc (C) beat FlatBuffers outside Python; this is the only catalogued entry that speeds up standard-format FlatBuffers from Python.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | flatbuffers&gt;=24.3.25, msgspec&gt;=0.19, numpy&gt;=2; flatc only for generating modules from .fbs; building from source also needs Rust plus maturin&gt;=1.10 |
| **Minimum toolchain** | Python 3.12+ (abi3-py312 wheels plus cp314t free-threaded wheels); Rust edition 2024 for source builds (no rustc version pinned) |
| **Platforms** | Prebuilt wheels: Linux x86-64 and aarch64 (manylinux 2_17), macOS x86-64 (10.12+) and arm64 (11.0+), Windows x86-64; free-threaded 3.14t wheels on every platform except Windows |
| **Thread safety** | Views allow concurrent reads while the backing buffer is unchanged (two threads can both build the same cached field value). The extension is declared gil_used=false and CI checks that free-threaded builds keep the GIL off. Whether shared Encoder/Decoder instances are thread-safe is not documented. |
| **Drop-in for the baseline** | partial — the wire format is standard FlatBuffers (the benchmark decodes buffers across both implementations in both directions), but you must regenerate code with msgspec_flatc and rewrite call sites from Builder/GetRootAs/Pack to encode()/decode() with Struct models and View classes |

## Gotchas

- flatbuffer.encode() returns a read-only memoryview, not bytes; call bytes() when another API needs bytes.
- Views borrow the input buffer, so mutating a backing bytearray or mmap while a view is live is unsupported. View numeric vectors are read-only little-endian arrays; to_model() copies them into writable native-dtype arrays.
- Lazy views do not run __post_init__ validation. Only decoding into a model or subclass type, or calling to_model(), does.
- In the JSON/MessagePack codecs, fields with unsupported annotations (dict, bytes, custom types) fall back to msgspec one field at a time. array_like=True, forbid_unknown_fields=True or a non-string tag sends the whole document through msgspec, and enc_hook/dec_hook run only for fallback fields. Generated modules raise GeneratedCodeVersionError when the runtime's major version differs.

## Known shortcomings

- Speed comes from a Rust pyo3 extension with no rustc version stated. The page's chart shows lower figures than its text (encode 18.7-21.8x, decode 10.6-11.8x, full traversal only 1.4-2.8x) against the official Python FlatBuffers Object API, which is slow. Created 2026-08.
- Its JSON/MessagePack codecs are 1.3-2.3x slower than plain msgspec on 16-value vectors (orjson/ormsgpack also ahead) and win only at 256 values. Lazy views are pure Python (struct.unpack_from), so the \~1.2x selected-field gain is Python vs Python. Only v0.1.x on PyPI, no issues, no pinned rustc.

## Caveats and trade-offs

Baseline is the official pure-Python FlatBuffers binding (interpreted-language overhead), not FlatBuffers' native C++ core, so the win mostly reflects Python API overhead rather than a beat of the FlatBuffers C++ engine. The benchmarks.md prose rounds up slightly compared with its own chart (for example encode 18.7x-21.8x in the chart vs '20–22x' in the text). The measured speed comes from a Rust extension whose rustc version is not stated. The benchmark is first-party, on a single machine/CPU model. The project is brand new (1 star, created 2026-08-25). The 2026-09-23 push date is a Dependabot branch; the last commit on main is 2026-09-10.

Python-only; the speedup is specific to msgspec-serde's generated Struct/View codec path vs the stock Python flatbuffers package's Object API, not a change to the FlatBuffers wire format itself; at 256-value vectors the plain FlatBuffers decode path is fastest overall, not msgspec-serde; requires flatc for IDL codegen

## Maintenance

Active but brand new: created 2026-08-25, v0.1.1 on PyPI 2026-08-30, last main commit 2026-09-10, 1 star, no issues and only Dependabot PRs. It is Apache-2.0 and pip-installable from prebuilt wheels, but expect generated-code churn.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): downgrade; tier before verification A, tier now C.
- **Tier reason:** benchmarks.md compares the msgspec_serde generated API with the official Python FlatBuffers Object API using public pyperf code (benchmarks/benchmark.py, benchmarks/_suite.py, benchmarks/run_pinned.py) on a stated Intel Core i7-8650U with CPython 3.13.5 and pinned package versions. The measured speed comes from a Rust pyo3 extension (rust/, built by maturin with profile=release), and no rustc version is stated. That is first-party with partial methodology, so C, the same as the orjson precedent.
- **Verifier notes:** The benchmark code confirms the baseline really is the official flatc-generated Python Object API (Pack/InitFromPackedBuf). Record's last_commit 2026-09-23 was a Dependabot branch push, so it is corrected to the main-branch date 2026-09-10; maintenance stays active. Downgraded A to C for the unstated Rust toolchain, consistent with earlier Python-extension verdicts.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `last_commit`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/ebrevdo/msgspec-serde/blob/main/benchmarks.md>
  - <https://github.com/ebrevdo/msgspec-serde>
  - <https://github.com/ebrevdo/msgspec-serde/blob/main/benchmarks/images/python-flatbuffers-comparison.png>
  - <https://github.com/ebrevdo/msgspec-serde/blob/main/benchmarks/benchmark.py>
  - <https://github.com/ebrevdo/msgspec-serde/blob/main/benchmarks/_suite.py>
  - <https://github.com/ebrevdo/msgspec-serde/blob/main/benchmarks/run_pinned.py>
  - <https://github.com/ebrevdo/msgspec-serde/blob/main/pyproject.toml>
  - <https://github.com/ebrevdo/msgspec-serde/blob/main/rust/Cargo.toml>
  - <https://github.com/ebrevdo/msgspec-serde/blob/main/Justfile>
  - <https://github.com/ebrevdo/msgspec-serde/blob/main/README.md>
- **Sources the enricher read:**
  - <https://github.com/ebrevdo/msgspec-serde>
  - <https://github.com/ebrevdo/msgspec-serde/blob/main/README.md>
  - <https://github.com/ebrevdo/msgspec-serde/blob/main/benchmarks.md>
  - <https://github.com/ebrevdo/msgspec-serde/blob/main/TUTORIAL.md>
  - <https://github.com/ebrevdo/msgspec-serde/blob/main/AGENTS.md>
  - <https://github.com/ebrevdo/msgspec-serde/blob/main/pyproject.toml>
  - <https://github.com/ebrevdo/msgspec-serde/blob/main/rust/Cargo.toml>
  - <https://github.com/ebrevdo/msgspec-serde/blob/main/rust/src/lib.rs>
  - <https://github.com/ebrevdo/msgspec-serde/blob/main/rust/src/plan.rs>
  - <https://github.com/ebrevdo/msgspec-serde/blob/main/rust/src/plan/decoding.rs>
  - <https://github.com/ebrevdo/msgspec-serde/blob/main/rust/src/plan/encoding.rs>
  - <https://github.com/ebrevdo/msgspec-serde/blob/main/src/msgspec_serde/_runtime.py>
  - <https://github.com/ebrevdo/msgspec-serde/blob/main/src/msgspec_serde/_flatbuffer.py>
  - <https://github.com/ebrevdo/msgspec-serde/blob/main/src/msgspec_serde/flatbuffer.py>
  - <https://github.com/ebrevdo/msgspec-serde/blob/main/benchmarks/_suite.py>
  - <https://github.com/ebrevdo/msgspec-serde/blob/main/benchmarks/benchmark.py>
  - <https://github.com/ebrevdo/msgspec-serde/blob/main/benchmarks/images/python-flatbuffers-comparison.png>
  - <https://github.com/ebrevdo/msgspec-serde/blob/main/benchmarks/images/idl-codec-comparison.png>
  - <https://github.com/ebrevdo/msgspec-serde/blob/main/benchmarks/images/msgspec-extended.png>
  - <https://github.com/ebrevdo/msgspec-serde/blob/main/.github/workflows/ci.yml>
  - <https://github.com/ebrevdo/msgspec-serde/blob/main/.github/workflows/release.yml>
  - <https://github.com/ebrevdo/msgspec-serde/issues>
  - <https://github.com/ebrevdo/msgspec-serde/pulls>
  - <https://github.com/ebrevdo/msgspec-serde/releases>
  - <https://github.com/ebrevdo/msgspec-serde/commits/main>
  - <https://pypi.org/pypi/msgspec-serde/json>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/ebrevdo/msgspec-serde`) · [data/wave4/enrich/raw/github_com_ebrevdo_msgspec_serde.json](../../../data/wave4/enrich/raw/github_com_ebrevdo_msgspec_serde.json) (enrichment confidence 0.8)

</details>
