# phuslu/log

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Logging and tracing](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Go` · `MIT` · 🟢 active

> Zero-allocation structured JSON logger for Go, faster than zerolog, zap and log/slog in its own benchmarks.

| | |
|---|---|
| **Beats** | zap, zerolog, log/slog |
| **Claimed result** | Simple: 214.2 ns/op vs zap 823.7, zerolog 337.6, slog 1274; with caller: 546.1 vs zap 2249, zerolog 1375, slog 2155; 50-100% faster as slog.JSONHandler replacement |
| **Workload** | Go structured JSON logging ns/op and allocations: simple message and with caller information. |
| **Metric** | latency |
| **Hardware** | AMD EPYC 7763 64-Core Processor, linux/amd64 (GitHub Actions ubuntu-latest), -cpu=4 |
| **Compiler and flags** | Go 1.27 (actions/setup-go in .github/workflows/benchmark.yml, check-latest); go test -v -cpu=4 -run=none -bench=. -benchtime=10s -benchmem (CI uses -benchtime=5s) |
| **Adoption** | 875 stars |
| **Last commit** | 2026-10-02 |
| **Links** | [repository](https://github.com/phuslu/log) · [benchmark](https://github.com/phuslu/log) |

## Verdict

The README's bench_test.go, re-run daily by a GitHub Actions workflow with Go 1.27 on an AMD EPYC 7763 runner (go test -cpu=4 -benchmem, writes to io.Discard), shows a simple JSON entry with three fields at 214.2 ns/op and 0 allocations vs zerolog 337.6, zap (sugared) 823.7 and slog 1274 ns/op, and with caller info 546.1 vs 1375, 2249 and 2155. As an slog handler at -cpu=1 it runs 590.5-702.8 ns/op vs 1282 for slog.JSONHandler.

## Use it when

- Go services that log structured JSON at high rates and want fewer allocations and less GC pressure than zap or slog's JSONHandler.
- Code already on slog that wants a faster backend without rewriting call sites: SlogNewJSONHandler measured 143.7 vs 351.5 ns/op on go-slog's Simple case.
- Logging with caller information on hot paths: 546.1 ns/op and 0 allocs vs zap 2249, zerolog 1375 and slog 2155.
- Projects that want rotation, async writing and syslog/journald in one dependency-free package.

## Skip it when

- C++ projects: use one of the C++ logging siblings instead; this is Go only.
- Heavy concurrent use of ConsoleWriter or mixing Logger with the async TSV logger: open issues report random crashes with ConsoleWriter across goroutines and interleaved, corrupted output.
- gccgo builds: an open issue reports it fails to build there.
- Workloads dominated by I/O rather than formatting: every published number writes to io.Discard, so disk or network costs are not measured.
- Code that needs zap's ecosystem (zapcore hooks, samplers, OpenTelemetry bridges) and its typed field API.

## How it is fast

Entries are appended into pooled byte buffers with hand-written JSON encoding, so the common paths do 0 allocations per call (the cpu=4 table shows 0 B/op for simple, printf, caller and any). Caller lookup and time formatting have custom fast paths, including an optional global timestamp cache (EnableTimeCache) that skips the clock read per entry, and AsyncWriter batches writes with writev under load.

## Compared with alternatives

The catalogued siblings (binlog, BqLog, fmtlog, lockfreelog) are C++ loggers measured against spdlog; pick phuslog only when the program is Go and the alternative is zap, zerolog or slog's JSONHandler.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none |
| **Minimum toolchain** | not documented in the README; benchmark CI uses Go 1.27 (latest patch) |
| **Platforms** | any Go platform; JournalWriter is Linux, EventlogWriter Windows; gccgo reported broken |
| **Thread safety** | Logger is used from many goroutines in the README examples; ConsoleWriter is documented as unsuitable for high-concurrency critical paths and has open crash reports |
| **Drop-in for the baseline** | partial — SlogNewJSONHandler is a drop-in slog.Handler (verified against the go-slog suite with duplicate-key warnings only); the native API is zerolog-like, not zap's |

## Gotchas

- EnableTimeCache is global and its timestamps can go stale beyond the interval when the refresh goroutine is delayed; every entry from one refresh shares the same time.
- AsyncWriter must be closed explicitly to flush; with DiscardOnFull=true entries are dropped when the channel fills.
- The zap rows use the SugaredLogger (Infow with loose key-value pairs), not zap's faster typed Logger, so the zap gap is larger than it would be against zap's best API.
- Leaving TimeFormat empty is recommended for speed; the benchmarks set RFC3339Nano on every logger for parity, and the README's result tables are snapshots that do not list every function in the embedded bench code (e.g. the SlogPhus\* rows).

## Known shortcomings

- Go, not C++. Harness flaw: the zap rows use SugaredLogger (Infow), not the typed Logger, which inflates the zap gap; every run writes to io.Discard. README tables are stale against the embedded bench code (SlogPhus\* rows missing; BenchmarkSlogPhusDisabled logs at Info, so it is not actually disabled). Open issues: ConsoleWriter crashes with many goroutines, async TSV interleave corruption, gccgo build failure.

## Caveats and trade-offs

Go library, not C++; baselines are Go loggers (zap, zerolog, log/slog), not spdlog, glog or OpenTelemetry; first-party; all loggers write to io.Discard; the README snapshot's exact Go version is not printed, the workflow currently pins 1.27; the 50-100% slog.JSONHandler claim is from a separate -cpu=1 table (e.g. 590.5-702.8 vs 1282 ns/op).

Zero allocation in common paths; Go only; zerolog-inspired API.

## Maintenance

Actively maintained (last commit 2026-10-02), MIT-licensed and dependency-free; several concurrency bug reports around ConsoleWriter and the async TSV logger are open.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now A.
- **Tier reason:** Benchmark code is public (bench_test.go embedded in README, extracted and run daily by .github/workflows/benchmark.yml), toolchain go-version 1.27 and command 'go test -v -cpu=4 -run=none -bench=. -benchtime=10s -benchmem' are stated, and the CPU is AMD EPYC 7763; upgraded from C to A.
- **Verifier notes:** All claimed ns/op figures appear in the README table (PhusLogSimple 214.2, ZapSimple 823.7, ZeroLogSimple 337.6, SlogSimple 1274; caller 546.1 vs 2249/1375/2155). Tier A rests on the CI workflow supplying the toolchain; downgrade to C if the orchestrator requires the version printed with the snapshot itself.
- **Fields the verifier corrected:** `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** public benchmark code
- **Pages the verifier opened:**
  - <https://github.com/phuslu/log>
  - <https://raw.githubusercontent.com/phuslu/log/HEAD/README.md>
  - <https://raw.githubusercontent.com/phuslu/log/HEAD/.github/workflows/benchmark.yml>
  - <https://raw.githubusercontent.com/phuslu/log/HEAD/LICENSE>
  - <https://github.com/phuslu/log/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/phuslu/log/HEAD/README.md>
  - <https://raw.githubusercontent.com/phuslu/log/HEAD/.github/workflows/benchmark.yml>
  - <https://github.com/phuslu/log/issues?q=is%3Aissue>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/phuslu/log`) · [data/wave11/enrich/raw/github_com_phuslu_log.json](../../../data/wave11/enrich/raw/github_com_phuslu_log.json) (enrichment confidence 0.75)

</details>
