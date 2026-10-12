# Vector (Rust) vs Fluent Bit (C) in the Vector test harness

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Systems and safety](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MPL-2.0` · 🟢 active

> Rust log and metrics pipeline whose 2019 first-party tests beat Fluent Bit 1.1.0; the current-version regex run loses.

| | |
|---|---|
| **Beats** | Fluent Bit (C log forwarder): 1.1.0 in the TCP to Blackhole, File to TCP, TCP to HTTP and TCP to TCP rows, 3.2.7 in the Regex Parsing row. The same table lists Filebeat (Go), Fluentd and Logstash (Ruby/JVM) and the closed-source Splunk Universal and Heavy Forwarders, whose implementation language was not verified here. |
| **Claimed result** | README Comparisons table: TCP to Blackhole 86 MiB/s vs Fluent Bit 64.4 MiB/s (1.34x, derived from page data); File to TCP 76.7 vs 35 MiB/s (2.2x, derived); TCP to HTTP 26.7 vs 19.6 MiB/s (1.36x, derived); TCP to TCP 69.9 vs 67.1 MiB/s (parity, Splunk UF wins at 70.4); Regex Parsing 13.2 vs 20.5 MiB/s (Vector slower). |
| **Workload** | End-to-end log pipeline throughput in the vector-test-harness: TCP to blackhole, file to TCP, TCP to HTTP, TCP to TCP, and regex parsing, each run for 60 s on AWS instances with a separate producer instance. |
| **Metric** | throughput |
| **Hardware** | AWS c5.large subject with 10 c5.large producers for tcp_to_blackhole (cases/tcp_to_blackhole_performance/configurations/default/terraform.tfvars); other cases' tfvars not checked; CPU model not stated. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | not stated |
| **Same optimization level** | not stated |
| **Adoption** | 22.7k stars |
| **Last commit** | 2026-10-09 |
| **Links** | [repository](https://github.com/vectordotdev/vector) · [benchmark](https://github.com/vectordotdev/vector) |

## Verdict

In the first-party vector-test-harness (AWS c5.large subject, 10 c5.large producers for TCP to Blackhole and 5 for Regex Parsing, 60 s, one run per subject, dstat metrics, no compiler, flags or CPU model), vector 0.2.0 in 2019 beat Fluent Bit 1.1.0 on TCP to Blackhole (86 vs 64.4 MiB/s received) and TCP to HTTP (26.7 vs 19.6) and tied on TCP to TCP (69.9 vs 67.1). Its 'File to TCP' 76.7 vs 35 MiB/s is a disk-read rate, and on bytes sent that row is 2.3 vs 2.0 GiB (about 1.15x). The only current-version row has Vector 0.55.0 1.55x slower than Fluent Bit 3.2.7 at regex parsing. A third-party run by VictoriaMetrics (2026-09-17, Vector 0.58.0 vs Fluent Bit 5.0.9 on Kubernetes) found Vector using about 1.4x the CPU at about 10.8k logs/s. At peak load Vector sustained 32,057 logs/s with no loss, while Fluent Bit reached 41,222 logs/s before it was OOM-killed with 1,133,131 logs lost.

## Use it when

- A multi-core agent or aggregator ingesting many TCP or syslog connections or many tailed files, where you want throughput to scale over every vCPU with no worker tuning (the sizing guide suggests at least 2 vCPUs for agents and 4 for aggregators).
- Replacing Logstash or Fluentd (JVM or Ruby): in the same harness Vector moved 69.9 MiB/s TCP to TCP against Logstash's 10 and Fluentd's 3.9, at 171.6 MiB peak memory against 725.4 and 293.6 MiB.
- Pipelines that need heavy routing, enrichment and many sinks in one binary, with disk buffers and end-to-end delivery guarantees (the README's correctness table shows Vector passing disk-buffer persistence, copytruncate rotation and SIGHUP tests that Fluent Bit 1.1.0 failed).
- Memory-constrained hosts with spare cores: peak memory in the 2019 TCP rows was 171-233 MiB for Vector against 614.8 MiB to 1.1 GiB for Fluent Bit 1.1.0.

## Skip it when

- CPU-capped edge or sidecar agents limited to about one core: per core, Fluent Bit is ahead. In the only current-version harness row (regex parsing), Fluent Bit 3.2.7 moves 20.5 MiB/s at a 50.8 CPU usr peak and Vector 0.55.0 moves 13.2 MiB/s at 95, roughly 3x less throughput per unit of CPU (derived from page data).
- Regex-heavy parsing at line rate, where Vector 0.55.0 is 1.55x slower than Fluent Bit 3.2.7 on the same Apache-log regex.
- When CPU per event matters: VictoriaMetrics' public log-collectors-benchmark run of 2026-09-17 (Kubernetes, about 10.8k logs/s) measured Vector 0.58.0 at 0.288 cores and 111 MB average memory, against 0.204 cores and 56 MB for Fluent Bit 5.0.9 (about 1.4x more CPU, derived).
- Embedding log shipping inside a C or C++ program: Vector is a separate daemon with no C API.
- Many mostly idle TCP or TLS connections: open issues #26492 (idle connections starve busy ones because the RequestLimiter is capped at num_threads()) and #23230 (TLS source degrades once connections exceed CPU cores); #23546 reports kubernetes_logs capped near 30k events/s against 120k for the file source.

## How it is fast

Each DAG node is an async task on the multi-threaded Tokio runtime, connected by bounded channels with backpressure by default. Stateless transforms such as remap are inlined into the source task, and each source defines its own unit of concurrency (the socket source per open connection, the file source per tailed file), so throughput spreads over all vCPUs without tuning. In the harness the advantage is mostly that parallelism: on the 2-vCPU c5.large, Vector's system-wide CPU usr peaks at 93.5-96.5 while Fluent Bit 1.1.0 peaks at 49.8-53.2, about one core. The project's sizing guide also says VRL compiles to machine code; that claim was not checked here.

## Compared with alternatives

No sibling is a log or metrics router. Unlike the single-command replacements (fd, cpz, rmz, tac), whose wins are timed on one workload, Vector's figures are whole-product, mostly from 2019 and driven by parallelism, so pick it as a multi-core replacement for Logstash or Fluentd, or for its pipeline features, rather than for raw per-core speed over Fluent Bit.

## Integration

| | |
|---|---|
| **Form** | standalone daemon binary (.deb/.rpm packages and container images); not a linkable library |
| **Dependencies** | none at run time for the packaged binary as installed by the harness (vector_&lt;version&gt;-1_amd64.deb); building from source needs the Rust workspace's crate dependencies |
| **Minimum toolchain** | Rust 1.95 (Cargo.toml rust-version), edition 2024; rust-toolchain.toml pins 1.96.1 |
| **Platforms** | Linux x86-64 (harness packages); the sizing guide also recommends ARM64 (Graviton, Cobalt); other platforms not checked here |
| **Thread safety** | multi-threaded Tokio runtime that uses all vCPUs automatically; stateful task transforms (dedupe, aggregate) are not parallelized |
| **Drop-in for the baseline** | partial — it covers the same roles as Fluent Bit (TCP, file and HTTP sources and sinks, parsing), but the configuration format, transform language and plugin set differ, so a migration means rewriting configs |

## Gotchas

- Harness flaw behind the 2.2x File to TCP row: the winning metric 'Disk Thrpt (avg)' is the dstat block-device read rate on the subject (disk_read_avg in bin/compare), not bytes delivered. Vector read 4.6 GiB from disk but sent only 2.3 GiB over the network, while Fluent Bit read 2 GiB and sent 2 GiB. On bytes sent the gap is about 1.15x (derived from page data), and the checked-in configs have Fluent Bit emitting json_lines while Vector emits raw text, so even the byte counts are not like-for-like.
- Core-count asymmetry: CPU usr in the tables is system-wide on a 2-vCPU c5.large. Fluent Bit 1.1.0 peaks at 49.8-53.2 in every row (about one core) and Vector at 93.5-96.5 (both cores), so the TCP to Blackhole (1.34x) and TCP to HTTP (1.36x) wins come largely from using the second core.
- The published rows cannot be rerun as published. The harness README says it is under construction and that some performance tests may be broken. Current configs are YAML for modern Vector, and Fluent Bit now comes from the jammy apt repository, whereas the 2019 rows ran vector 0.2.0 (TOML configs; only tcp_to_blackhole keeps a vector.old.toml) against fluentbit 1.1.0. The multi_file configuration now creates 20 files of 250 MiB where the case README says 10. Each subject is one 60 s run with no variance (TCP to HTTP shows 'Test count 1'), and no compiler, flags or CPU model are given.
- The README tagline 'up to 10x faster than every alternative' is not supported against Fluent Bit by its own table: the best Fluent Bit row is 1.36x (or 2.2x on the disk-read metric above), there is a tie on TCP to TCP, and the current-version regex row is a loss.

## Known shortcomings

- Every winning row uses 2019 versions (Fluent Bit 1.1.0, Vector 0.2.0); the only current re-run (regex, Fluent Bit 3.2.7) has Vector 1.55x slower; Fluent Bit 1.1.0 likely ran on one core of a 2-vCPU c5.large; the harness is marked under construction.
- Harness flaw: the File to TCP 2.2x is 'Disk Thrpt', dstat's disk_read_avg (bin/compare), not bytes delivered: Vector read 4.6 GiB and sent 2.3 GiB while Fluent Bit read 2 GiB and sent 2 GiB, so on bytes sent the gap is about 1.15x (derived); the configs differ too (json_lines vs text). Fluent Bit 1.1.0 sits at about 50 CPU usr (one core) in every row while Vector uses about 95 (both cores); the 2019 rows cannot be rerun. Third-party data (VictoriaMetrics/log-collectors-benchmark, results/2026-09-17): at about 10.8k logs/s Vector 0.58.0 used 0.288 cores against Fluent Bit 5.0.9's 0.204; peak Vector 32,057 logs/s with 0 lost, Fluent Bit 41,222 then OOMKilled with 1,133,131 lost.
- Contradicting evidence (VictoriaMetrics log-collectors-benchmark, found by the vlagent enricher, 2026-10-13): in that harness Vector v0.58.0 does worse than Fluent Bit (0.288 cores at 10k logs/s, 32k logs/s peak), the opposite of Vector's own harness.

## Caveats and trade-offs

First-party harness, and the README says it is under construction and some performance tests may be broken. The rows mix vintages. TCP to Blackhole and TCP to HTTP compare fluentbit 1.1.0 with vector 0.2.0-6-g434bed8, and File to TCP (multi_file; the single_file results are empty) and TCP to TCP compare fluentbit 1.1.0 with vector 0.2.0, all from 2019. Only Regex Parsing was re-run with current versions (fluentbit 3.2.7, vector 0.55.0), and there Vector is 1.55x slower (13.2 vs 20.5 MiB/s, derived from page data). In TCP to Blackhole, Fluent Bit 1.1.0 peaks at 53.2 CPU usr against Vector's 96.5 on a 2-vCPU c5.large, which suggests Fluent Bit used about one core and Vector both (derived from page data). Splunk UF wins TCP to TCP (70.4 MiB/s). These are whole-product comparisons with different feature sets, and no compiler or flags are stated. [retier] Independent counter-evidence: VictoriaMetrics' log-collectors-benchmark measures Vector v0.58.0 worse than Fluent Bit (0.288 cores at 10k logs/s, 32k logs/s peak).

Full observability pipeline (agent and aggregator) with a transform language; heavier on CPU than the simple C forwarder in the TCP to Blackhole case (max user CPU 96.5 vs 53.2) but lighter on memory there (181 MiB vs 614.8 MiB).

## Maintenance

Actively maintained by Datadog (14,423 commits, last commit 2026-10-09 per the verifier, master at 0.60.0-dev), MPL-2.0 and 22.7k stars, so it is production-ready as a daemon. Its README performance table, however, dates from 2019 apart from the regex row, and the harness behind it describes itself as under construction.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** A first-party harness (vectordotdev/vector-test-harness) with public Terraform/Ansible configs. The tcp_to_blackhole default configuration pins c5.large instances, but no CPU model, compiler or build flags are given, and the harness README says it is under construction and some performance tests may be broken. That makes it C.
- **Verifier notes:** README numbers match the case READMEs in vector-test-harness for all five rows: 1.34x, 2.2x and 1.36x wins (derived), parity at TCP to TCP, a loss on regex parsing. Main shortcomings: 2019 versions behind every winning row, the only current-version re-run is a loss, Fluent Bit 1.1.0 was probably CPU-limited to one core, and there is no CPU model or flags. Metadata checked: MPL-2.0, 22.7k stars, last commit 2026-10-09, active.
- **Fields the verifier corrected:** `baseline`, `hardware`, `caveats`
- **Shortcomings recorded by:** verifier batch-69 (wave 14); enricher (wave 14 pass, 2026-10-12); enricher (seed pass, 2026-10-13)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/vectordotdev/vector/HEAD/README.md>
  - <https://github.com/vectordotdev/vector>
  - <https://github.com/vectordotdev/vector/commits>
  - <https://raw.githubusercontent.com/vectordotdev/vector-test-harness/master/README.md>
  - <https://raw.githubusercontent.com/vectordotdev/vector-test-harness/master/cases/tcp_to_blackhole_performance/README.md>
  - <https://raw.githubusercontent.com/vectordotdev/vector-test-harness/master/cases/file_to_tcp_performance/README.md>
  - <https://raw.githubusercontent.com/vectordotdev/vector-test-harness/master/cases/regex_parsing_performance/README.md>
  - <https://raw.githubusercontent.com/vectordotdev/vector-test-harness/master/cases/tcp_to_http_performance/README.md>
  - <https://raw.githubusercontent.com/vectordotdev/vector-test-harness/master/cases/tcp_to_tcp_performance/README.md>
  - <https://raw.githubusercontent.com/vectordotdev/vector-test-harness/master/cases/tcp_to_blackhole_performance/terraform/main.tf>
  - <https://raw.githubusercontent.com/vectordotdev/vector-test-harness/master/cases/tcp_to_blackhole_performance/terraform/variables.tf>
  - <https://github.com/vectordotdev/vector-test-harness/tree/master/cases/tcp_to_blackhole_performance>
  - <https://github.com/vectordotdev/vector-test-harness/tree/master/cases/tcp_to_blackhole_performance/configurations/default>
  - <https://raw.githubusercontent.com/vectordotdev/vector-test-harness/master/cases/tcp_to_blackhole_performance/configurations/default/terraform.tfvars>
  - <https://raw.githubusercontent.com/vectordotdev/vector-test-harness/master/cases/tcp_to_blackhole_performance/configurations/default/ansible.yml>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/vectordotdev/vector/HEAD/README.md>
  - <https://raw.githubusercontent.com/vectordotdev/vector/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/vectordotdev/vector/HEAD/rust-toolchain.toml>
  - <https://raw.githubusercontent.com/vectordotdev/vector/HEAD/website/content/en/docs/architecture/runtime-model.md>
  - <https://raw.githubusercontent.com/vectordotdev/vector/HEAD/website/content/en/docs/architecture/concurrency-model.md>
  - <https://raw.githubusercontent.com/vectordotdev/vector/HEAD/website/content/en/docs/architecture/pipeline-model.md>
  - <https://raw.githubusercontent.com/vectordotdev/vector/HEAD/website/content/en/docs/architecture/buffering-model.md>
  - <https://raw.githubusercontent.com/vectordotdev/vector/HEAD/website/content/en/docs/setup/going-to-prod/sizing.md>
  - <https://github.com/vectordotdev/vector>
  - <https://github.com/vectordotdev/vector/issues?q=is%3Aissue%20state%3Aopen%20label%3A%22domain%3A%20performance%22>
  - <https://raw.githubusercontent.com/vectordotdev/vector-test-harness/master/README.md>
  - <https://raw.githubusercontent.com/vectordotdev/vector-test-harness/master/bin/compare>
  - <https://raw.githubusercontent.com/vectordotdev/vector-test-harness/master/lib/vector-test-harness/init.sh>
  - <https://raw.githubusercontent.com/vectordotdev/vector-test-harness/master/lib/vector-test-harness/utils/print_compare_test>
  - <https://raw.githubusercontent.com/vectordotdev/vector-test-harness/master/cases/tcp_to_blackhole_performance/README.md>
  - <https://raw.githubusercontent.com/vectordotdev/vector-test-harness/master/cases/file_to_tcp_performance/README.md>
  - <https://raw.githubusercontent.com/vectordotdev/vector-test-harness/master/cases/regex_parsing_performance/README.md>
  - <https://raw.githubusercontent.com/vectordotdev/vector-test-harness/master/cases/tcp_to_http_performance/README.md>
  - <https://raw.githubusercontent.com/vectordotdev/vector-test-harness/master/cases/tcp_to_tcp_performance/README.md>
  - <https://github.com/vectordotdev/vector-test-harness/tree/master/cases/tcp_to_blackhole_performance/ansible>
  - <https://github.com/vectordotdev/vector-test-harness/tree/master/cases/file_to_tcp_performance>
  - <https://github.com/vectordotdev/vector-test-harness/tree/master/cases/file_to_tcp_performance/ansible/config_files>
  - <https://github.com/vectordotdev/vector-test-harness/tree/master/cases/tcp_to_blackhole_performance/ansible/config_files>
  - <https://raw.githubusercontent.com/vectordotdev/vector-test-harness/master/cases/file_to_tcp_performance/ansible/run.yml>
  - <https://raw.githubusercontent.com/vectordotdev/vector-test-harness/master/cases/file_to_tcp_performance/ansible/bootstrap.yml>
  - <https://raw.githubusercontent.com/vectordotdev/vector-test-harness/master/cases/file_to_tcp_performance/ansible/reset.yml>
  - <https://raw.githubusercontent.com/vectordotdev/vector-test-harness/master/cases/file_to_tcp_performance/configurations/multi_file/ansible.yml>
  - <https://raw.githubusercontent.com/vectordotdev/vector-test-harness/master/cases/file_to_tcp_performance/configurations/multi_file/terraform.tfvars>
  - <https://raw.githubusercontent.com/vectordotdev/vector-test-harness/master/cases/file_to_tcp_performance/ansible/config_files/td-agent-bit.conf>
  - <https://raw.githubusercontent.com/vectordotdev/vector-test-harness/master/cases/file_to_tcp_performance/ansible/config_files/vector.yaml>
  - <https://raw.githubusercontent.com/vectordotdev/vector-test-harness/master/cases/tcp_to_blackhole_performance/ansible/run.yml>
  - <https://raw.githubusercontent.com/vectordotdev/vector-test-harness/master/cases/tcp_to_blackhole_performance/ansible/bootstrap.yml>
  - <https://raw.githubusercontent.com/vectordotdev/vector-test-harness/master/cases/tcp_to_blackhole_performance/ansible/config_files/td-agent-bit.conf>
  - <https://raw.githubusercontent.com/vectordotdev/vector-test-harness/master/cases/tcp_to_blackhole_performance/ansible/config_files/vector.yaml>
  - <https://raw.githubusercontent.com/vectordotdev/vector-test-harness/master/cases/tcp_to_blackhole_performance/ansible/config_files/vector.old.toml>
  - <https://raw.githubusercontent.com/vectordotdev/vector-test-harness/master/cases/tcp_to_blackhole_performance/configurations/default/terraform.tfvars>
  - <https://raw.githubusercontent.com/vectordotdev/vector-test-harness/master/cases/regex_parsing_performance/ansible/run.yml>
  - <https://raw.githubusercontent.com/vectordotdev/vector-test-harness/master/cases/regex_parsing_performance/ansible/bootstrap.yml>
  - <https://raw.githubusercontent.com/vectordotdev/vector-test-harness/master/cases/regex_parsing_performance/configurations/default/ansible.yml>
  - <https://raw.githubusercontent.com/vectordotdev/vector-test-harness/master/cases/regex_parsing_performance/configurations/default/terraform.tfvars>
  - <https://raw.githubusercontent.com/vectordotdev/vector-test-harness/master/cases/regex_parsing_performance/ansible/config_files/td-agent-bit.conf>
  - <https://raw.githubusercontent.com/vectordotdev/vector-test-harness/master/cases/regex_parsing_performance/ansible/config_files/td-agent-bit.parsers.conf>
  - <https://raw.githubusercontent.com/vectordotdev/vector-test-harness/master/cases/regex_parsing_performance/ansible/config_files/vector.yaml>
  - <https://raw.githubusercontent.com/vectordotdev/vector-test-harness/master/ansible/roles/flog/tasks/create_test_file.yml>
  - <https://raw.githubusercontent.com/vectordotdev/vector-test-harness/master/ansible/roles/flog/defaults/main.yml>
  - <https://raw.githubusercontent.com/vectordotdev/vector-test-harness/master/ansible/roles/flog/tasks/install.yml>
  - <https://raw.githubusercontent.com/vectordotdev/vector-test-harness/master/ansible/roles/profiling/tasks/start.yml>
  - <https://raw.githubusercontent.com/vectordotdev/vector-test-harness/master/ansible/roles/vector/tasks/install.yml>
  - <https://raw.githubusercontent.com/vectordotdev/vector-test-harness/master/ansible/roles/fluentbit/tasks/install.yml>
  - <https://raw.githubusercontent.com/mingrammer/flog/v0.2.4/log.go>
  - <https://github.com/VictoriaMetrics/log-collectors-benchmark>
  - <https://raw.githubusercontent.com/VictoriaMetrics/log-collectors-benchmark/HEAD/README.md>
  - <https://github.com/VictoriaMetrics/log-collectors-benchmark/tree/main/results>
  - <https://github.com/VictoriaMetrics/log-collectors-benchmark/tree/master/results/2026-09-17>
  - <https://raw.githubusercontent.com/VictoriaMetrics/log-collectors-benchmark/master/results/2026-09-17/info.json>
  - <https://raw.githubusercontent.com/VictoriaMetrics/log-collectors-benchmark/master/results/2026-09-17/vector-throughput.json>
  - <https://raw.githubusercontent.com/VictoriaMetrics/log-collectors-benchmark/master/results/2026-09-17/vector-resources.json>
  - <https://raw.githubusercontent.com/VictoriaMetrics/log-collectors-benchmark/master/results/2026-09-17/fluent-bit-throughput.json>
  - <https://raw.githubusercontent.com/VictoriaMetrics/log-collectors-benchmark/master/results/2026-09-17/fluent-bit-resources.json>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/vectordotdev/vector`) · [data/wave14/enrich/raw/github_com_vectordotdev_vector.json](../../../data/wave14/enrich/raw/github_com_vectordotdev_vector.json) (enrichment confidence 0.75)

</details>
