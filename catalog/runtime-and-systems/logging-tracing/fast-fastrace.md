# fastrace

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Logging and tracing](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0` · 🟢 active

> Rust timeline-tracing library (successor to minitrace) whose span creation costs 19-151x less than tokio-tracing in its own benchmark.

| | |
|---|---|
| **Beats** | tokio-tracing |
| **Claimed result** | At 100 spans: tokio-tracing 124x slower on Intel Broadwell (33x Skylake, 36x AMD Zen, 29x Graviton2), fastrace 3.4 us on Broadwell; by span count tokio-tracing is 19x slower at 1 span (fastrace 0.4 us) up to 151x at 1000 spans (fastrace 27.8 us). rustracing 9x to 55x slower. |
| **Workload** | Cost of creating and finishing traces with 1 to 1000 spans, on four architectures, versus tokio-tracing and rustracing. |
| **Metric** | latency |
| **Hardware** | Intel Broadwell, Intel Skylake, AMD Zen, AWS Graviton2 |
| **Adoption** | 1.1k stars |
| **Last commit** | 2026-07-31 |
| **Links** | [repository](https://github.com/fast/fastrace) · [benchmark](https://github.com/fast/fastrace) |

## Verdict

Per its results README, the authors ran cargo criterion on the compare bench on four 8-vCPU AWS EC2 instances (m4 Broadwell, m5 Skylake, m5a Zen, m6g Graviton2; Ubuntu 20.04) to time one root span plus N child spans. On m4.2xlarge fastrace took 0.44 us, 0.75 us, 3.4 us and 27.8 us for 1, 10, 100 and 1000 spans, against 8.2 us, 46 us, 423 us and 4.19 ms for tokio-tracing (19x to 151x) and 5.5 us to 1.52 ms for rustracing. The rustc version is not recorded, and in fastrace's case the span export cost lands on a background thread, not on the timed thread.

## Use it when

- Instrumenting hot paths in Rust libraries or servers (KV stores, query engines, storage layers) where tracing overhead per span must stay in the hundreds of nanoseconds or below.
- Library crates that want to ship tracing hooks that cost nothing unless the final application enables them.
- Request-scoped traces exported to OpenTelemetry backends via fastrace-opentelemetry, with axum, tonic, tower, reqwest or poem integrations.
- Workloads with many short child spans per request (100 to 1000 spans), where the README gap over tokio-tracing is widest.

## Skip it when

- C or C++ codebases: it is Rust-only with no C API; C++ users need a different tracer.
- You need per-span verbosity levels, tracing-subscriber's layer/filter ecosystem or structured event logging as the primary output: fastrace has no 'level' concept and no logging macros of its own.
- Long-lived or endless root spans: spans are reported when the root is dropped, so a root that never ends never reports.
- Toolchains older than Rust 1.91 (MSRV 1.91.0, edition 2024).

## How it is fast

LocalSpan keeps child spans in a thread-local stack with no locking or atomics when a local parent is set; spans that cross threads or await points use the heavier, thread-safe Span. Timestamps come from the fastant crate (TSC-based clock), and finished span batches go to a background collector thread that calls the reporter every report_interval (default 1 s), so the instrumented thread does not serialize or export anything. Without the 'enable' feature the macros compile away entirely.

## Compared with alternatives

The catalogued siblings (binlog, BqLog, fmtlog, lockfreelog) are C++ loggers compared against spdlog, so they solve a different problem. Pick fastrace only for span-based distributed tracing in Rust; for low-latency C++ logging use fmtlog or binlog.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | fastant, fastrace-macro, parking_lot, pin-project, rand, rtrb, serde (plus opentelemetry crates when fastrace-opentelemetry is used) |
| **Minimum toolchain** | Rust 1.91.0 (edition 2024) |
| **Platforms** | any Rust target; benchmarked on x86-64 (Intel Broadwell, Skylake, AMD Zen) and arm64 (AWS Graviton2) |
| **Thread safety** | Span is thread-safe and Send; LocalSpan is single-thread and must not cross threads or .await points; collection runs on one background thread |
| **Drop-in for the baseline** | partial: a different API from tokio-tracing; the fastrace-tracing compatibility layer captures existing tracing spans in two lines |

## Gotchas

- LocalSpan::enter_with_local_parent does nothing silently when no local parent is set, so a missing set_local_parent() call drops spans without an error.
- Span records created before set_reporter() are ignored, and flush() must be called before exit or buffered spans are lost.
- The README sells a tail-sampling design, but Config::tail_sampled, max_spans_per_trace and report_before_root_finish are deprecated no-ops in 0.7.x, so there is no per-trace span cap against runaway memory.
- The README tables come from an older criterion 'compare' bench (results/\*.txt from cargo-criterion on Ubuntu 20.04 EC2, including rustracing); the current benches/compare.rs is a divan harness against tokio-tracing with an OpenTelemetry layer only, so the rustracing column cannot be reproduced from HEAD.

## Known shortcomings

- README tables come from an old cargo-criterion bench on Ubuntu 20.04 EC2 with the rustc version unrecorded; the current benches/compare.rs is divan and covers tokio-tracing only, so the rustracing column is not reproducible from HEAD. Export runs on a background collector thread, outside the timed path. tail_sampled and max_spans_per_trace are now deprecated no-ops although the README still sells tail sampling; no per-trace span cap.

## Caveats and trade-offs

Baseline is tokio-tracing (and rustracing), not the OpenTelemetry SDK; first-party numbers; CPU families named but not exact models; rustc version and flags not stated; benches/results not opened; successor of tikv/minitrace-rust (not a GitHub fork). Rust library, not C++.

Library-level tracing with tail-sampling; no 'level' concept; compatible with OpenTelemetry export via fastrace-opentelemetry; MSRV 1.91.

## Maintenance

Actively maintained (0.7.19, commits into 2026, used by Databend and Apache OpenDAL); Apache-2.0, so it is safe to adopt in Rust projects, but it has no value for C++ code.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README tables vs tokio-tracing and rustracing across four CPU families and span counts; no compiler/rustc version or flags stated, and gains above 50x with unstated flags cap it at C.
- **Verifier notes:** README numbers match. Apache-2.0, 1.1k stars, last commit 2026-07-31.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** code reading by enricher
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/fast/fastrace/HEAD/README.md>
  - <https://github.com/fast/fastrace>
  - <https://github.com/fast/fastrace/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/fast/fastrace/HEAD/README.md>
  - <https://raw.githubusercontent.com/fast/fastrace/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/fast/fastrace/HEAD/crates/fastrace/Cargo.toml>
  - <https://raw.githubusercontent.com/fast/fastrace/HEAD/crates/fastrace/src/lib.rs>
  - <https://raw.githubusercontent.com/fast/fastrace/HEAD/crates/fastrace/src/collector/mod.rs>
  - <https://raw.githubusercontent.com/fast/fastrace/HEAD/crates/fastrace/src/collector/global_collector.rs>
  - <https://raw.githubusercontent.com/fast/fastrace/HEAD/benches/Cargo.toml>
  - <https://raw.githubusercontent.com/fast/fastrace/HEAD/benches/benches/compare.rs>
  - <https://raw.githubusercontent.com/fast/fastrace/HEAD/benches/results/README.md>
  - <https://raw.githubusercontent.com/fast/fastrace/HEAD/benches/results/compare-m4.2xlarge.txt>
  - <https://github.com/fast/fastrace/tree/main/benches>
  - <https://github.com/fast/fastrace/tree/main/benches/results>
  - <https://github.com/fast/fastrace/tree/main/benches/benches>
  - <https://github.com/fast/fastrace/tree/main/crates/fastrace/src>
  - <https://github.com/fast/fastrace/tree/main/crates/fastrace/src/collector>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/fast/fastrace`) · [data/wave11/enrich/raw/github_com_fast_fastrace.json](../../../data/wave11/enrich/raw/github_com_fast_fastrace.json) (enrichment confidence 0.75)

</details>
