# Fluent Bit

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Logging and tracing](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `Apache-2.0` · 🟢 active

> C telemetry agent that collects, parses and forwards logs, metrics and traces; about 8x Fluentd's regex-parsing throughput per core.

| | |
|---|---|
| **Beats** | Fluentd and Logstash |
| **Claimed result** | Regex parsing: Fluent Bit 3.2.7 20.5 MiB/s vs Fluentd 4.5.2-1 2.6 MiB/s (about 7.9x, derived from page data) and Logstash 8.17.3 4.6 MiB/s (about 4.5x, derived from page data). File to TCP, multi-file (older versions: Fluent Bit 1.1.0, Fluentd 3.3.0-1, Logstash 7.0.1): 35 MiB/s vs 26.1 MiB/s (about 1.3x, derived from page data) and 3.1 MiB/s (about 11x, derived from page data); peak memory there 370.3 MiB vs 890.6 MiB and 763.7 MiB. |
| **Workload** | Vector test harness, regex_parsing_performance: each agent receives Apache common-format log lines over TCP, extracts named fields with one regex, and forwards over TCP for 60 seconds, with producer and consumer on separate instances. Also file_to_tcp_performance (tail 10 files, send over TCP, 60 s). |
| **Metric** | throughput |
| **Hardware** | AWS EC2: subject c5.large (2 vCPU), five c5.large producers and a c5d.xlarge consumer for the regex case (cases/regex_parsing_performance/configurations/default/terraform.tfvars); subject c5.large and consumer c5.xlarge for file-to-TCP multi_file (cases/file_to_tcp_performance/configurations/multi_file/terraform.tfvars). Exact CPU model not stated. |
| **Adoption** | 8.2k stars; CNCF graduated (Fluentd ecosystem); README says it is deployed over 10 million times daily and has passed 15 billion downloads |
| **Last commit** | 2026-10-24 |
| **Links** | [repository](https://github.com/fluent/fluent-bit) · [benchmark](https://github.com/vectordotdev/vector-test-harness/blob/master/cases/regex_parsing_performance/README.md) |

## Verdict

In Vector's public test harness (a competitor's suite, AWS c5.large subject, 60-second TCP-in, regex-parse, TCP-out runs with prebuilt packages and default single-worker configs; run count not shown, bin/compare averages all runs of the latest version), Fluent Bit 3.2.7 ingested and parsed 20.5 MiB/s against Fluentd 4.5.2-1 at 2.6 MiB/s and Logstash 8.17.3 at 4.6 MiB/s, measured as network receive rate on the subject. A 2019 file-to-TCP run had Fluent Bit 1.1.0 at 35 MiB/s against 26.1 (Fluentd) and 3.1 (Logstash), with Vector fastest at 76.7.

## Use it when

- Node or sidecar log shipping where one core must parse and forward tens of MiB/s: in Vector's harness it parsed Apache lines at 20.5 MiB/s on one core of a c5.large, against 2.6 MiB/s for Fluentd at the same CPU use.
- Replacing Fluentd or Logstash collectors on hosts and Kubernetes nodes while keeping a Fluentd aggregator, since both belong to the Fluentd ecosystem and Fluent Bit has a forward output.
- Tailing many files and shipping over TCP with low CPU and disk-write overhead (35 MiB/s with 6.1 MiB disk writes in the 2019 multi-file run).
- Embedded, Windows, macOS or BSD hosts that need a single native agent binary with bundled dependencies.

## Skip it when

- If raw shipping throughput is the goal, Vector beat it in the same harness (76.7 vs 35 MiB/s file-to-TCP) and used less memory in the regex case (179.3 vs 584.5 MiB).
- Memory-capped hosts without limits configured: the harness config set no Mem_Buf_Limit, and Fluent Bit peaked at 584.5 MiB in the regex case, more than Fluentd's 246.1 MiB.
- Pipelines that depend on Fluentd's plugin ecosystem or Logstash grok and pipeline syntax; those must be rewritten as Fluent Bit plugins, Lua, Go or WASM.
- Running old releases: the benchmarked 3.2.x line is end-of-life per SECURITY policy, and critical advisories hit the Trace API (GHSA-5rjf-prwh-pp7q, 2024) and the out_forward Secure-Forward PONG handler (GHSA-jrp8-r9hx-gf73, 2026).

## How it is fast

The core is C with records kept as MessagePack (msgpack-c, mpack) end to end, network I/O on the bundled monkey event loop, and output flushes run as libco coroutines (flb_coro, fixed stacks of at least 64 KiB by default) so slow destinations do not block the pipeline. Regex parsing uses the bundled Onigmo engine from C, and filters run at ingest time inside input_chunk_append_raw before records are buffered, so parse cost is paid once per record on the input path. SIMD paths are enabled automatically on x86-64 and aarch64 (and riscv64 when the compiler supports RVV) through FLB_SIMD=Auto, with simdutf for UTF handling when a C++ compiler is available.

## Compared with alternatives

The catalogued siblings (Quill, fmtlog, BqLog, spdlog-style loggers) are in-process libraries that format and write log lines from your C++ code; Fluent Bit is the out-of-process agent that tails, parses and ships what those loggers write. Pick it to replace a Fluentd or Logstash collector, not to replace a logging call in a hot path.

## Integration

| | |
|---|---|
| **Form** | standalone agent binary (packages, Docker, Windows builds); optional shared library (FLB_SHARED_LIB) |
| **Dependencies** | Bundled: msgpack-c, mpack, monkey, libco, Onigmo, chunkio, LuaJIT, WAMR, simdutf, zstd, nghttp2, c-ares, librdkafka and others under lib/. Build needs Flex, Bison, YAML and OpenSSL headers |
| **Minimum toolchain** | C compiler and CMake 3.12+ (CMakeLists; README says 3.0); C++ compiler optional (enables simdutf) |
| **Platforms** | Linux, Windows, macOS, BSD and embedded per README; SIMD on x86-64, aarch64, riscv64 (RVV) |
| **Thread safety** | Not applicable to the agent; thread safety of the embedding library API is not documented |
| **Drop-in for the baseline** | partial — replaces a Fluentd or Logstash process in the pipeline and can forward to Fluentd, but configs, parsers and plugins must be rewritten in Fluent Bit's format |

## Gotchas

- The harness 'IO Thrpt' row is the subject host's network receive rate (net_recv_avg in bin/compare), not records delivered to the consumer. Fluent Bit runs filters at ingest, so the number does reflect regex-parse speed, but delivery is unmeasured, and its send/receive ratio (1.6 GiB / 1.2 GiB) is lower than Vector's (2 GiB / 804.8 MiB), which may mean a backlog was still in memory at the end of the run.
- With no Mem_Buf_Limit and memory storage, an input never pauses when an output lags (flb_input_chunk_is_mem_overlimit returns false when the limit is 0), so memory grows without bound. Set Mem_Buf_Limit or filesystem storage in production.
- Open 2026 issues report memory growth with storage.type filesystem (#12504, #12443) and a SIGSEGV with two Kubernetes filter instances (#12152).
- Benchmarked versions are 3.2.7 (regex) and 1.1.0 (file-to-TCP), while master tracks 5.2 and the stable line is 5.1; no newer independent numbers were found.

## Known shortcomings

- Vector's harness (c5.large, exact CPU unstated): Fluent Bit peaks at more memory than Fluentd in the regex case (584.5 vs 246.1 MiB); both run one default worker; Fluentd forwards msgpack while Fluent Bit sends json_lines.
- Enricher: throughput is ingest only (delivery unmeasured), buffering unbounded (no Mem_Buf_Limit), possible end-of-run backlog; 3.2.x is end of life with critical advisories GHSA-5rjf-prwh-pp7q and GHSA-jrp8-r9hx-gf73.

## Caveats and trade-offs

Measured by the Vector project (a competing log router) in its public test harness, not by Fluent Bit's authors; results are single runs without variance, and the same tables show Vector beating Fluent Bit on file-to-TCP (76.7 vs 35 MiB/s) and TCP-to-TCP. Instance types are public in the cases' configurations/\*/terraform.tfvars (c5.large subject), but the exact CPU model is not given and packages are prebuilt, so no compiler or flags exist, hence not tier A. Subject configs are public (cases/regex_parsing_performance/ansible/config_files): every tool runs its default single process/worker with the same regex; Fluent Bit and Fluentd both peak at about 50% CPU user on the 2-vCPU subject (one core), Logstash uses grok and reaches 90.5%. In the regex case Fluent Bit used more memory than Fluentd (584.5 MiB vs 246.1 MiB peak), and Fluentd forwards with its msgpack forward protocol while Fluent Bit sends json_lines over TCP. Versions differ per case: the file-to-TCP table is from 2019 releases, the regex table was refreshed in the harness' 2026 refresh commit (#101, 2026-06-18); the Fluentd version label (4.5.2-1) looks like a td-agent package version, not the Fluentd core version (not checked against the harness bootstrap). The harness README warns it is under construction and not fully validated against recent versions. Fluent Bit's own documentation claim of roughly 650 KB idle memory vs about 40 MB for Fluentd (seen only as a search-result paraphrase) could not be opened because docs.fluentbit.io did not resolve; no Fluent Bit-run benchmark was reachable. The harness' TCP-to-HTTP and TCP-to-blackhole case pages were not opened; their Fluent Bit vs Fluentd figures (19.6 vs &lt;1 MiB/s and 64.4 vs 27.7 MiB/s) were seen only in a copy of Vector's README performance table at https://github.com/appsignal/vector, which gives no hardware or versions. [retier] Enricher: 'IO Thrpt' is the subject's net_recv_avg (ingest) per bin/compare; filters run at ingest, so parse speed is real but delivery is unmeasured. The harness config sets no Mem_Buf_Limit, so buffering is unbounded (matching the 584.5 MiB peak); sent/received 1.6 GiB/1.2 GiB against Vector's 2 GiB/804.8 MiB suggests a backlog at the end of the run (derived from page data, unconfirmed). compare averages all runs of the latest version (run count not shown), not single runs. The 3.2.x line is end of life; critical advisories GHSA-5rjf-prwh-pp7q (2024) and GHSA-jrp8-r9hx-gf73 (2026).

In the regex test Fluent Bit peaked at 584.5 MiB of memory vs 246.1 MiB for Fluentd (743.8 MiB for Logstash), so the throughput win costs memory there; in the file-to-TCP case it used less memory than both. Written in C with plugins in C, Lua filters and Go outputs (per README).

## Maintenance

Very active CNCF graduated project with major releases every 3-4 months (master tracks 5.2, stable 5.1) and an Apache-2.0 license; only 5.0.x and 5.1.x get security fixes, so stay on a supported line.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now B.
- **Tier reason:** Independent third-party suite (Vector's public vector-test-harness, run by a competitor whose own product loses this case) shows Fluent Bit 20.5 MiB/s vs Fluentd 2.6 and Logstash 4.6 MiB/s with public configs and AWS instance types, but prebuilt packages mean no compiler/flags and no exact CPU model, so not A.
- **Verifier notes:** Regex table (20.5 / 2.6 / 4.6 MiB/s, versions 3.2.7 / 4.5.2-1 / 8.17.3) and file-to-TCP multi-file table (35 / 26.1 / 3.1 MiB/s, memory 370.3 / 890.6 / 763.7 MiB) match the harness READMEs. Record wrongly said instance types were not public: default tfvars name c5.large subjects, so hardware is filled in. Repo metadata (Apache-2.0, 8.2k stars, last commit 2026-10-24, not archived) checks out.
- **Fields the verifier corrected:** `hardware`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-65 (wave 11 book seed pass, 2026-10-24); enrichment (wave 11 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/vectordotdev/vector-test-harness/master/cases/regex_parsing_performance/README.md>
  - <https://raw.githubusercontent.com/vectordotdev/vector-test-harness/master/cases/file_to_tcp_performance/README.md>
  - <https://raw.githubusercontent.com/vectordotdev/vector-test-harness/master/README.md>
  - <https://github.com/vectordotdev/vector-test-harness/tree/master/cases/regex_parsing_performance>
  - <https://github.com/vectordotdev/vector-test-harness/commits/master/cases/regex_parsing_performance/README.md>
  - <https://raw.githubusercontent.com/vectordotdev/vector-test-harness/master/cases/regex_parsing_performance/terraform/main.tf>
  - <https://raw.githubusercontent.com/vectordotdev/vector-test-harness/master/cases/regex_parsing_performance/terraform/variables.tf>
  - <https://raw.githubusercontent.com/vectordotdev/vector-test-harness/master/bin/test>
  - <https://github.com/vectordotdev/vector-test-harness/tree/master/cases/regex_parsing_performance/configurations>
  - <https://raw.githubusercontent.com/vectordotdev/vector-test-harness/master/cases/regex_parsing_performance/configurations/default/terraform.tfvars>
  - <https://github.com/vectordotdev/vector-test-harness/tree/master/cases/regex_parsing_performance/ansible>
  - <https://github.com/vectordotdev/vector-test-harness/tree/master/cases/regex_parsing_performance/ansible/config_files>
  - <https://raw.githubusercontent.com/vectordotdev/vector-test-harness/master/cases/regex_parsing_performance/ansible/config_files/td-agent-bit.conf>
  - <https://raw.githubusercontent.com/vectordotdev/vector-test-harness/master/cases/regex_parsing_performance/ansible/config_files/td-agent-bit.parsers.conf>
  - <https://raw.githubusercontent.com/vectordotdev/vector-test-harness/master/cases/regex_parsing_performance/ansible/config_files/td-agent.conf>
  - <https://raw.githubusercontent.com/vectordotdev/vector-test-harness/master/cases/regex_parsing_performance/ansible/config_files/logstash.pipeline.conf>
  - <https://raw.githubusercontent.com/vectordotdev/vector-test-harness/master/cases/file_to_tcp_performance/configurations/multi_file/terraform.tfvars>
  - <https://github.com/fluent/fluent-bit>
  - <https://github.com/fluent/fluent-bit/commits/master>
- **Sources the enricher read:**
  - <https://github.com/fluent/fluent-bit>
  - <https://raw.githubusercontent.com/fluent/fluent-bit/master/README.md>
  - <https://raw.githubusercontent.com/fluent/fluent-bit/master/CMakeLists.txt>
  - <https://github.com/fluent/fluent-bit/tree/master/lib>
  - <https://raw.githubusercontent.com/fluent/fluent-bit/master/src/flb_input_chunk.c>
  - <https://raw.githubusercontent.com/fluent/fluent-bit/master/src/flb_regex.c>
  - <https://raw.githubusercontent.com/fluent/fluent-bit/master/include/fluent-bit/flb_coro.h>
  - <https://github.com/fluent/fluent-bit/security>
  - <https://github.com/fluent/fluent-bit/issues?q=is%3Aissue%20state%3Aopen%20memory%20leak>
  - <https://raw.githubusercontent.com/vectordotdev/vector-test-harness/master/README.md>
  - <https://raw.githubusercontent.com/vectordotdev/vector-test-harness/master/cases/regex_parsing_performance/README.md>
  - <https://raw.githubusercontent.com/vectordotdev/vector-test-harness/master/cases/file_to_tcp_performance/README.md>
  - <https://raw.githubusercontent.com/vectordotdev/vector-test-harness/master/bin/compare>
  - <https://github.com/vectordotdev/vector-test-harness/tree/master/bin>
  - <https://raw.githubusercontent.com/vectordotdev/vector-test-harness/master/lib/vector-test-harness/init.sh>
  - <https://raw.githubusercontent.com/vectordotdev/vector-test-harness/master/lib/vector-test-harness/utils/print_compare_test>
  - <https://raw.githubusercontent.com/vectordotdev/vector-test-harness/master/cases/regex_parsing_performance/ansible/config_files/td-agent-bit.conf>
  - <https://raw.githubusercontent.com/vectordotdev/vector-test-harness/master/cases/regex_parsing_performance/ansible/config_files/td-agent-bit.parsers.conf>
  - <https://raw.githubusercontent.com/vectordotdev/vector-test-harness/master/cases/regex_parsing_performance/ansible/config_files/td-agent.conf>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/fluent/fluent-bit`) · [data/wave11/enrich/raw/github_com_fluent_fluent_bit.json](../../../data/wave11/enrich/raw/github_com_fluent_fluent_bit.json) (enrichment confidence 0.75)

</details>
