# Imprint

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [Binary schemas](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟡 stale

> Rust row format with a sorted field-offset directory, so records merge or project without decoding; \~4x faster than prost merges.

| | |
|---|---|
| **Beats** | Protobuf (Rust prost 0.12 implementation, per the since-removed benches/Cargo.toml) |
| **Claimed result** | README: 'Imprint performs up to 76% better than protobuf at merging two records', with Imprint merge time roughly constant while protobuf grows with record size. Merge chart (approximate read-off): protobuf \~1000 / \~2140 / \~3450 vs Imprint \~785 / \~800 / \~800 at merge_size_1/5/10, so \~4.3x at the largest size (derived from page data, approximate). The projection chart has no ratio in the text. It shows Imprint SLOWER at project_size_1 (\~580 vs protobuf \~360) and faster only at size 5 (\~650 vs \~890) and size 10 (\~625 vs \~1530) (approximate read-off). The chart's y-axis unit is labeled ambiguously as 'ns/µs'. |
| **Workload** | Criterion micro-benchmarks on fake Product/Order records at sizes 1, 5 and 10. Merge: decode two records and write an enriched combined record (protobuf: prost decode of both, clone into an EnrichedOrder, re-encode; Imprint: read both, directory merge, write). Projection: read one record and write a field subset (protobuf: decode and re-encode a SimpleProduct; Imprint: project 6 fields and write). |
| **Metric** | latency |
| **Adoption** | 170 stars |
| **Last commit** | 2025-07-15 |
| **Links** | [repository](https://github.com/agavra/imprint) · [benchmark](https://github.com/agavra/imprint#composition-join--merge) |

## Verdict

In the author's Criterion run (PR #11, May 2025, Rust prost 0.12; CPU, compiler and flags not stated; the chart unit is ns), decoding a fake Product and Order, combining them and re-encoding took 3,454 ns with prost vs 797 ns with Imprint at the largest size (\~4.3x, the README's '76%') and 1,004 vs 784 ns at the smallest. A contributor's rerun in PR #27, after merges became order-deterministic, gave 2,848 vs 692 ns (\~4.1x) and 748 vs 642 ns (\~1.17x); the projection chart has Imprint slower at size 1 and \~2.4x faster at size 10, although the prost projection re-encodes 5 fields against Imprint's 6.

## Use it when

- Stream-join or enrichment stages that combine two rows with disjoint field ids and forward the result without reading most field values (the case the merge benchmark models).
- Routing or filtering stages that project a few fields out of wide rows with long string or array values; the published gap grows with value size (size 10 projection: \~625 ns vs \~1530 ns for prost).
- Pipelines that need a self-describing row that tools can inspect without generated code: every directory entry carries a type code, so a generic reader can print any record.
- Rust projects where you control both producer and consumer and are willing to vendor a small library (about 1,900 lines of safe Rust including tests); an early Java port exists at agavra/imprint-java for JVM consumers.

## Skip it when

- Plain whole-message encode/decode. The only protobuf numbers for that (PR #11: serialize 225 vs 356 ns, 'deserialize' 248 vs 769 ns) time Imprint without decoding any field values, so they do not show a full-decode win.
- Small records or small projections. At project_size_1 Imprint was slower than prost (\~580 vs \~360 ns), and merge at size 1 was only \~1.2-1.3x faster.
- Size-sensitive storage or network links. Each row carries a 15-byte header plus 7 bytes per field, and int32/int64 are always 4/8 fixed bytes with no varint or zigzag, so rows are larger than protobuf's \~1-byte tags plus varints.
- Untrusted input. Reads do not validate directory offsets or ordering. A truncated array or map, or a header whose payload size is too large, reaches `bytes` accessors (`get_u8`, `slice`) that panic instead of returning an error. There is also no schema or type validation (issue #8).
- Anything that needs a stable, published dependency. It is v0.1.0 with no releases or tags and is not on crates.io, where the `imprint` name belongs to an unrelated 2017 crate. The format was still changing in mid-2025 (2-byte ids and a mandatory directory landed in June 2025), and there have been no commits since 2025-07-15.

## How it is fast

Each row has a 15-byte header and a directory of 7-byte entries (u16 field id, u8 type code, u32 payload offset) sorted by field id. A field is found by binary search, and its byte length is the gap to the next entry's offset. Merge sort-merges the two directories, copies each chosen field's payload bytes unchanged and rebases the offsets; projection walks the directory and copies the selected byte ranges into one pre-sized buffer. Neither path decodes strings or arrays or re-encodes anything, but that is what the prost baseline has to do (decode both messages into owned structs, clone, re-encode), so Imprint's cost follows field count while prost's follows content size. Reading a record parses the header and directory eagerly but keeps the payload as a zero-copy `Bytes` slice.

## Compared with alternatives

Pick Imprint over rkyv or YaFF when the hot operation is combining or subsetting rows of different schemas and re-emitting bytes: their catalogued results measure serialize and field-read speed, not merging two records. For plain whole-message encode/decode against prost, rkyv or bilrost have wider numbers from the shared rust_serialization_benchmark log dataset.

## Integration

| | |
|---|---|
| **Form** | crate (git dependency only; not published on crates.io) |
| **Dependencies** | bytes 1.5, thiserror 1.0 (dev-only: criterion, fake, proptest) |
| **Minimum toolchain** | Rust edition 2024 (so Rust 1.85+); no rust-version declared |
| **Platforms** | any: pure safe Rust with no `unsafe`, SIMD or platform-specific code; the wire format is little-endian via explicit LE accessors |
| **Thread safety** | not documented; records are immutable once built (the payload is a `bytes::Bytes`, and src has no interior mutability or unsafe) |
| **Drop-in for the baseline** | no |

## Gotchas

- Map fields are written by iterating a std `HashMap`, so two equal maps can serialize to different bytes. The README's byte-for-byte determinism holds only for rows without maps; PR #27 fixed payload order for merges only.
- `project` sets the header's schema hash to the placeholder 0xdeadbeef (a TODO in ops.rs), and `merge` keeps the first record's schema id unchanged. The schema hash is wrong after either operation.
- When both records have the same field id, `merge` silently keeps the first record's value and drops the second without checking types, so `a.merge(b)` differs from `b.merge(a)`. `ImprintWriter::add_field` lets the last write win.
- The README type table lists date, time, timestamp, uuid and decimal (0xB-0xF), but the code implements only codes 0x0-0xA. The others are just reserved (PR #37), and reading one returns InvalidFieldType. The README's '3-5 bytes/field' directory overhead is also out of date: entries are 7 bytes.

## Known shortcomings

- Baseline is Rust prost 0.12, not Google protobuf, and the protobuf merge path adds clones. Slower than prost at the smallest projection size. The comparison harness was deleted in PR #31 and survives only in history (commit f42484cf).
- Deserialize (248 vs 769 ns) times Imprint without decoding field values (author: 'best case'). The projection comparison favours prost (5 fields re-encoded vs 6 projected). Not on crates.io (the name belongs to an unrelated crate); git dependency only. Malformed input can panic; map bytes are not deterministic despite the README; project writes a 0xdeadbeef placeholder schema hash.

## Caveats and trade-offs

The README shows only chart images plus one headline percentage. Compiler/toolchain, flags and CPU model are not stated. The baseline is Rust prost 0.12, not Google's C++ protobuf. The protobuf comparison harness (benches/src/serialization.rs, benches/Cargo.toml with prost 0.12) was removed from the repo in PR #31 (2025-05-28): the current benches/serde_bench.rs benchmarks Imprint alone, so the charted comparison is reproducible only from git history (commit f42484cf). The protobuf merge path also clones both decoded messages, which adds allocation to the baseline. Imprint is slower than protobuf for projection at the smallest record size. Last commit was 2025-07-15, over a year ago.

Field directory adds roughly 3-5 bytes/field of overhead versus protobuf's \~1-varint tag/field, so wire size is slightly larger; schema-less reads require scanning a directory; optimized for compose/project (stream-join) access patterns rather than raw sequential encode/decode throughput

## Maintenance

Stale (about 26 commits from 5 contributors, last commit 2025-07-15, no releases; open issues for lazy directory parsing, zero-copy merge/project views and validation), but MIT-licensed, small and with only two runtime dependencies, so it is easy to vendor if you treat the format as unstable.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** The README section gives one first-party headline ('up to 76% better than protobuf at merging two records') plus two bar charts for merge and projection at sizes 1/5/10, with no compiler, flags, CPU or protobuf version stated. The Criterion code that produced the charts (benches/src/serialization.rs vs prost 0.12, added in PRs #11/#16) was deleted from HEAD in PR #31 and survives only in git history, so C.
- **Verifier notes:** Headline 76% merge figure matches the README and the chart. Tier C stays, but the record's statement that serde_bench.rs is the public comparison code is wrong: that file has no protobuf path, and the prost-based harness exists only in history. Metadata (MIT, 170 stars, last commit 2025-07-15, stale, not a fork) checks out. baseline_in_list left unchanged; the orchestrator should note the baseline is prost, not Google protobuf.
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `workload`, `caveats`
- **Shortcomings recorded by:** PR #11 (author): merge at size 1/5/10 prost 1003.50/2140.10/3453.90 ns vs Imprint 784.04/798.71/797.41 ns; serialize 355.53 vs 224.99 ns. PR #27 rerun (contributor, after deterministic merge): size 10 prost 2848 vs Imprint 692 ns, size 1 748 vs 642 ns.
- **Pages the verifier opened:**
  - <https://github.com/agavra/imprint#composition-join--merge>
  - <https://github.com/agavra/imprint>
  - <https://github.com/agavra/imprint/blob/main/.github/images/imprint-merge_bench.png>
  - <https://github.com/agavra/imprint/blob/main/.github/images/imprint-project_bench.png>
  - <https://github.com/agavra/imprint/blob/main/benches/serde_bench.rs>
  - <https://github.com/agavra/imprint/blob/main/benches/data.rs>
  - <https://github.com/agavra/imprint/blob/main/Cargo.toml>
  - <https://github.com/agavra/imprint/blob/main/.github/workflows/bench.yml>
  - <https://github.com/agavra/imprint/blob/main/scripts/ci_bench.sh>
  - <https://github.com/agavra/imprint/commit/f42484cf263985032006ab2839a87a5ffab950fb>
  - <https://github.com/agavra/imprint/commit/0da23a03>
  - <https://github.com/agavra/imprint/blob/f42484cf263985032006ab2839a87a5ffab950fb/benches/Cargo.toml>
  - <https://github.com/agavra/imprint/blob/f42484cf263985032006ab2839a87a5ffab950fb/benches/src/serialization.rs>
  - <https://github.com/agavra/imprint/blob/f42484cf263985032006ab2839a87a5ffab950fb/Cargo.toml>
- **Sources the enricher read:**
  - <https://github.com/agavra/imprint>
  - <https://github.com/agavra/imprint#composition-join--merge>
  - <https://github.com/agavra/imprint/blob/main/README.md>
  - <https://github.com/agavra/imprint/blob/main/FORMAT.md>
  - <https://github.com/agavra/imprint/blob/main/Cargo.toml>
  - <https://github.com/agavra/imprint/blob/main/src/lib.rs>
  - <https://github.com/agavra/imprint/blob/main/src/error.rs>
  - <https://github.com/agavra/imprint/blob/main/src/writer.rs>
  - <https://github.com/agavra/imprint/blob/main/src/types.rs>
  - <https://github.com/agavra/imprint/blob/main/src/ops.rs>
  - <https://github.com/agavra/imprint/blob/main/src/serde.rs>
  - <https://github.com/agavra/imprint/blob/main/src/varint.rs>
  - <https://github.com/agavra/imprint/blob/main/benches/serde_bench.rs>
  - <https://github.com/agavra/imprint/blob/main/benches/data.rs>
  - <https://github.com/agavra/imprint/blob/main/.github/workflows/ci.yml>
  - <https://github.com/agavra/imprint/blob/main/.github/workflows/bench.yml>
  - <https://github.com/agavra/imprint/blob/main/scripts/ci_bench.sh>
  - <https://github.com/agavra/imprint/blob/main/.github/images/imprint-merge_bench.png>
  - <https://github.com/agavra/imprint/blob/main/.github/images/imprint-project_bench.png>
  - <https://github.com/agavra/imprint/tree/f42484cf263985032006ab2839a87a5ffab950fb>
  - <https://github.com/agavra/imprint/blob/f42484cf263985032006ab2839a87a5ffab950fb/benches/Cargo.toml>
  - <https://github.com/agavra/imprint/blob/f42484cf263985032006ab2839a87a5ffab950fb/benches/src/serialization.rs>
  - <https://github.com/agavra/imprint/blob/f42484cf263985032006ab2839a87a5ffab950fb/benches/src/mock_data.rs>
  - <https://github.com/agavra/imprint/blob/f42484cf263985032006ab2839a87a5ffab950fb/benches/src/types.rs>
  - <https://github.com/agavra/imprint/blob/f42484cf263985032006ab2839a87a5ffab950fb/benches/proto/test_record.proto>
  - <https://github.com/agavra/imprint/issues?q=is%3Aissue>
  - <https://github.com/agavra/imprint/issues/26>
  - <https://github.com/agavra/imprint/issues/30>
  - <https://github.com/agavra/imprint/issues/34>
  - <https://github.com/agavra/imprint/issues/10>
  - <https://github.com/agavra/imprint/issues/9>
  - <https://github.com/agavra/imprint/issues/4>
  - <https://github.com/agavra/imprint/issues/28>
  - <https://github.com/agavra/imprint/issues/8>
  - <https://github.com/agavra/imprint/issues/20>
  - <https://github.com/agavra/imprint/pulls?q=is%3Apr>
  - <https://github.com/agavra/imprint/pull/11>
  - <https://github.com/agavra/imprint/pull/12>
  - <https://github.com/agavra/imprint/pull/16>
  - <https://github.com/agavra/imprint/pull/27>
  - <https://github.com/agavra/imprint/pull/31>
  - <https://github.com/agavra/imprint/pull/32>
  - <https://github.com/agavra/imprint/pull/33>
  - <https://github.com/agavra/imprint/pull/35>
  - <https://github.com/agavra/imprint/pull/37>
  - <https://github.com/agavra/imprint/commits/main>
  - <https://github.com/agavra/imprint/releases>
  - <https://github.com/agavra/imprint/tags>
  - <https://github.com/agavra/imprint/graphs/contributors>
  - <https://github.com/agavra/imprint-java>
  - <https://crates.io/api/v1/crates/imprint>
  - <https://crates.io/api/v1/crates?q=imprint>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/agavra/imprint`) · [data/wave4/enrich/raw/github_com_agavra_imprint.json](../../../data/wave4/enrich/raw/github_com_agavra_imprint.json) (enrichment confidence 0.75)

</details>
