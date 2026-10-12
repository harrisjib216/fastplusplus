# MTS-1 (Lightweight Delta-Encoded Telemetry Format)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [Binary schemas](README.md)</sub>

**Tier C** (first-party claim) · Study only · `Rust` · `CC-BY-4.0` · ⚪ unknown

> Rust per-packet binary telemetry format (MTS-1/MWire) reporting \~5% smaller payloads than MessagePack on synthetic host metrics.

| | |
|---|---|
| **Beats** | MessagePack |
| **Claimed result** | Reported \~5.4% smaller than MessagePack and 74.6-74.7% smaller than JSON on the paper's synthetic S1 dataset (MTS-1 1.39 MB vs MessagePack 1.47 MB). Protocol Buffers was explicitly excluded from quantitative testing by the authors ('schema compilation requirements incompatible with dynamic monitoring scenarios'). |
| **Workload** | Synthetic telemetry payload size comparison (storage footprint) of MTS-1 against JSON, JSON Lines, CBOR, MessagePack, and Protocol Buffers for low-resource/offline-first system health monitoring. |
| **Metric** | memory |
| **Links** | [repository](https://github.com/ndourc/mwire) · [benchmark](https://arxiv.org/abs/2601.01602) |

## Verdict

The only claim is size: on a synthetic 10k-record set, per-packet MTS-1 totals 1,390,000 B vs 1,469,521 B for MessagePack (rmp-serde, structs as arrays) and 5,475,079 B for JSON (5.4% and 74.6% smaller), and the 20k and 50k sets scale linearly. Protobuf was not measured, and no compiler, hardware or timings are given. My arithmetic on the repo's generator reproduces the MessagePack and MTS-1 byte counts exactly for all three sizes.

## Use it when

- Reproducing or auditing the paper: the repo's generate_dataset binary and committed tele20k/tele50k files let you re-derive Table I byte counts.
- Rust host agents sending fixed host metrics (CPU %, temperature, frequency, memory, disk, network counters, uptime) where you own both ends and want a checksummed packet with timestamp, sequence number and a LAN-proxy flag.
- Slowly changing metric streams stored as JSON arrays, where the MTS1 stream mode stores field names once and writes only changed fields between snapshots (every 10th record by default).
- As a small reference design for a telemetry packet layout: the core crate is about 100 KB of Rust in 7 files, with no unsafe code.

## Skip it when

- You need speed numbers. No encode or decode timings are published. The README's \~65,000 encode / \~112,000 decode records/s gives no hardware, method or baseline, and no results from the criterion comparison bench are published.
- You want a fair size win over MessagePack. The 5.4% margin exists because the baseline stores the UUID as a 36-char hex string (38 B) while MTS-1 stores 16 raw bytes. By my arithmetic on the generator code (not a measurement), rmp-serde MessagePack with a binary UUID would be \~127 B per record vs MTS-1's 139 B.
- C++ codebases, or platforms without prebuilt artifacts. It is Rust only, with no C/C++ API. The only prebuilt artifacts are a Windows x86-64 mwire.exe and a single PyPI wheel (magenta-telemetry 0.1.0, CPython 3.11 win_amd64). Nothing is published on crates.io.
- Untrusted input. The decoders call `Vec::with_capacity` / `HashMap::with_capacity` with u32 counts read from the packet, and CRC32 is not authentication, so a crafted packet can request very large allocations.
- Production dependencies. It is single-author code (5 stars, 6 commits from 2026-02-15 to 2026-03-01, no issues filed) with no root LICENSE file. The packet format has a fixed field table (numbers 0-31). A lost snapshot breaks delta reconstruction, and an epsilon above 0 makes delta mode lossy.

## How it is fast

The win is in size, not speed. Each present field is a 1-byte tag (3-bit type, 5-bit field number) followed by a fixed-width little-endian value, absent fields are skipped, and the UUID is stored as 16 raw bytes. In the paper's generator this gives a constant 139 B per record: a 2 B length prefix, 15 B header, 18 B device ID, 16 B UUID, 84 B payload and 4 B CRC. The 'delta' mode is change suppression: a delta packet or frame carries the new values of fields that changed (optionally only past a per-field epsilon), not arithmetic differences. Per-packet LZ4 (lz4_flex block mode) is optional.

## Compared with alternatives

Pick it only if you want a ready-made, CRC-checked host-metrics packet in Rust. For compactness alone, JSON BinPack (smallest or tied-smallest across 27 documents) and qdf (IoT/OTLP batch fixtures) have broader size evidence, and fernBuffer's MessagePack comparison covers more data shapes.

## Integration

| | |
|---|---|
| **Form** | crate (Cargo workspace: magenta-telemetry-core lib, mwire CLI, pyo3 and wasm-bindgen bindings); not on crates.io, so use a git/path dependency or source-drop |
| **Dependencies** | core: lz4_flex 0.11, crc32fast 1.4, serde 1.0, serde_json 1.0; CLI adds clap 4.5, anyhow, rmp-serde 1.3, ciborium 0.2; bindings add pyo3 0.21 or wasm-bindgen 0.2 |
| **Minimum toolchain** | Rust 1.70+ (README badge and docs/README.md), edition 2021 |
| **Platforms** | Pure Rust with no unsafe in core/src, so it should build for any Rust target; prebuilt binaries exist only for Windows x86-64 |
| **Thread safety** | not documented (core encode/decode are stateless free functions; delta reconstruction state is held by the caller) |
| **Drop-in for the baseline** | no |

## Gotchas

- The paper's 'delta-encoded' results do not use delta mode. generate_dataset.rs calls `encode()` on full records with `is_delta` false, so Table I measures plain fixed-width packets. The constant 139 B per record is therefore the natural packet size, not evidence of computed numbers.
- The paper and the code describe different methods. The paper cites real Magenta samples at \~30 s intervals and deltas of c_i - c_(i-1). The generator uses sin/cos synthetic values at 1 s intervals with one device ID and UUID, and delta frames carry replacement values. The paper's 100-host example (1.95 GB vs 0.24 GB, '87.7%') also disagrees with its own 548 B vs 139 B per payload.
- The two spec documents disagree. docs/FORMAT.md's type-ID table (e.g. 0x01 = Null) and its legacy flag bits do not match core/src/types.rs and encoder.rs, which follow FORMAT_SPEC.md (0x06 = Null, delta = flag bit 4). Treat the code as the spec.
- Per-packet LZ4 makes these packets larger (2,794,270 vs 2,780,000 B on S2) because `compress_prepend_size` adds a 4-byte length and the \~84-byte payload barely compresses. Only the stream mode's whole-body LZ4 pays off: DISTRIBUTION_README reports 1,340,041 vs 4,440,224 B on a 25,957-record dataset.

## Known shortcomings

- Size-only claim, no speed numbers. The benchmark generator runs with delta encoding off on synthetic sin/cos data at 1 s intervals, so the 139 B/record is the fixed packet size. The MessagePack baseline stores the UUID as a 36-char string; with a binary UUID MessagePack would be about 127 B and win (derived from the generator, not measured). No root LICENSE file although the README says MIT.

## Caveats and trade-offs

No code repository or specification is published. The only reproducibility aid is the author's email. This is a January 2026 single-author arXiv preprint (not peer-reviewed) with synthetic datasets only (10k/20k/50k payloads generated from Magenta metric samples). The win over MessagePack is modest: 1,390,000 vs 1,469,521 bytes on S1 (5.4%). The MTS-1 sizes are exactly 139 B per payload on every dataset (1,390,000 / 2,780,000 / 6,950,000 bytes), which suggests computed rather than measured values. MTS-1+LZ4 is larger than plain MTS-1. MTS-1 drops changes below a threshold epsilon, so it is lossy by design, although the paper claims identical semantic information. The abstract says encoding cost was compared, but no encoding-time results are reported. Protocol Buffers was excluded from the quantitative tests.

No throughput/latency numbers at all, only payload size; Protobuf, one of the category's core baselines, was deliberately not benchmarked. No implementation language, code repository, or reference implementation could be found.

## Maintenance

Single-author research code behind a non-peer-reviewed January 2026 arXiv preprint: last commit 2026-03-01, one v1.0.0 Windows release, MIT according to the README and Cargo.toml but with no root LICENSE file; use it as a reference, not a maintained dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** The paper is a single-author arXiv preprint (cs.SE, v1 of 4 Jan 2026) with no journal reference, so it is not peer-reviewed. Table I gives byte sizes against MessagePack, but there is no code, hardware or implementation detail, so the evidence is first-party numbers with thin methodology.
- **Verifier notes:** The numbers match Table I and the abstract (74.6% vs JSON on S1, 74.7% on S2, 5.4% vs MessagePack). A web search and a GitHub search found no implementation. A related Medium post returned 403 and was not read. This stays a paper-only research entry at tier C.
- **Fields the verifier corrected:** `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/abs/2601.01602>
  - <https://arxiv.org/pdf/2601.01602>
  - <https://arxiv.org/html/2601.01602v1>
- **Sources the enricher read:**
  - <https://arxiv.org/abs/2601.01602>
  - <https://arxiv.org/pdf/2601.01602>
  - <https://arxiv.org/html/2601.01602v1>
  - <https://github.com/ndouhenry>
  - <https://github.com/ndourc>
  - <https://github.com/ndourc/mwire>
  - <https://github.com/ndourc/mwire/blob/main/README.md>
  - <https://github.com/ndourc/mwire/blob/main/FORMAT_SPEC.md>
  - <https://github.com/ndourc/mwire/blob/main/MWIRE.md>
  - <https://github.com/ndourc/mwire/blob/main/PRODUCTION_READY.md>
  - <https://github.com/ndourc/mwire/blob/main/DISTRIBUTION_README.txt>
  - <https://github.com/ndourc/mwire/blob/main/Cargo.toml>
  - <https://github.com/ndourc/mwire/blob/main/core/Cargo.toml>
  - <https://github.com/ndourc/mwire/blob/main/cli/Cargo.toml>
  - <https://github.com/ndourc/mwire/blob/main/benches/Cargo.toml>
  - <https://github.com/ndourc/mwire/blob/main/python/Cargo.toml>
  - <https://github.com/ndourc/mwire/blob/main/wasm/Cargo.toml>
  - <https://github.com/ndourc/mwire/blob/main/python/pyproject.toml>
  - <https://github.com/ndourc/mwire/blob/main/mwire-v1.0.0-windows/LICENSE.txt>
  - <https://github.com/ndourc/mwire/blob/main/.gitignore>
  - <https://github.com/ndourc/mwire/blob/main/core/src/lib.rs>
  - <https://github.com/ndourc/mwire/blob/main/core/src/compression.rs>
  - <https://github.com/ndourc/mwire/blob/main/core/src/delta.rs>
  - <https://github.com/ndourc/mwire/blob/main/core/src/encoder.rs>
  - <https://github.com/ndourc/mwire/blob/main/core/src/decoder.rs>
  - <https://github.com/ndourc/mwire/blob/main/core/src/types.rs>
  - <https://github.com/ndourc/mwire/blob/main/core/src/stream.rs>
  - <https://github.com/ndourc/mwire/blob/main/cli/src/bin/generate_dataset.rs>
  - <https://github.com/ndourc/mwire/blob/main/cli/src/encode.rs>
  - <https://github.com/ndourc/mwire/blob/main/cli/src/benchmark.rs>
  - <https://github.com/ndourc/mwire/blob/main/benches/benches/comparison.rs>
  - <https://github.com/ndourc/mwire/blob/main/docs/FORMAT.md>
  - <https://github.com/ndourc/mwire/blob/main/docs/README.md>
  - <https://github.com/ndourc/mwire/blob/main/docs/QUICKSTART.md>
  - <https://github.com/ndourc/mwire/releases>
  - <https://github.com/ndourc/mwire/issues>
  - <https://github.com/magenta/telemetry-format>
  - <https://pypi.org/pypi/magenta-telemetry/json>
  - <https://crates.io/api/v1/crates/magenta-telemetry-core>
  - <https://crates.io/api/v1/crates/mwire>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `paper:mts-1-lightweight-delta-encoded-telemetry-format`) · [data/wave4/enrich/raw/paper_mts_1_lightweight_delta_encoded_telemetry_format.json](../../../data/wave4/enrich/raw/paper_mts_1_lightweight_delta_encoded_telemetry_format.json) (enrichment confidence 0.75)

</details>
