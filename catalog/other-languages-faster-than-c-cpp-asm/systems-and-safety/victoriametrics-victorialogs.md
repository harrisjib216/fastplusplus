# vlagent (Go log collector, VictoriaLogs): log-collectors-benchmark vs Fluent Bit

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Systems and safety](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `Apache-2.0` · 🟢 active

> Go Kubernetes log collector for VictoriaLogs; about 4x less CPU than Fluent Bit per log at 10k logs/s in a vendor-run benchmark.

| | |
|---|---|
| **Beats** | Fluent Bit (C), v5.0.9 in the 2026-09-17 run (v4.2.3 in the 2026-08-12 and 2026-09-16 runs), Helm chart fluent/fluent-bit 0.57.9, tail input with the kubernetes filter and an HTTP JSON-lines output with gzip, limited to 1 CPU and 1 GiB |
| **Claimed result** | results/2026-09-17 (vlagent v1.52.0 vs Fluent Bit v5.0.9): resources case average CPU 0.0476 vs 0.2040 cores (4.3x less, derived from page data), average memory 33152688 vs 56061519 bytes (1.7x less, derived from page data), max memory 46620672 vs 110538752 bytes, lost 0 vs 3; throughput case 177949 vs 41222 logs/s (4.3x, derived from page data), where the Fluent Bit run is marked Success false, FailReason OOMKilled, Lost 1133131, and the two collectors used 0.475 and 0.407 average cores, so neither reached its 1-CPU limit. The 2026-08-12 run (vlagent v1.48.0, Fluent Bit v4.2.3) gives 178274 vs 40218 logs/s and CPU 0.0479 vs 0.2116 cores; the 2026-09-16 run (same versions as 2026-08-12) gives 176712 vs 39734 logs/s and CPU 0.0478 vs 0.2131 cores. |
| **Workload** | Kubernetes log collection on a local kind cluster: (a) resources case, 10 log-generator Pods at 1000 JSON lines per second each (about 10k logs/s) for one hour, measuring average CPU and memory; (b) maximum-throughput case, 50 Pods starting at 50 logs/s each and adding 20 logs/s per Pod every 10 s until throughput stops growing; both ship to a log-verifier that counts lost lines; each collector limited to 1 CPU and 1 GiB |
| **Metric** | throughput |
| **Hardware** | GCP c2d-highcpu-8 VM shared with 50 log-generator pods, the verifier, VictoriaMetrics and Grafana; each collector limited to 1 CPU (enricher, from bench-runner/index.gohtml) |
| **Compiler and flags** | Prebuilt release images from Helm charts (vm/victoria-logs-collector 0.3.7 for vlagent, fluent/fluent-bit 0.57.9), no compiler flags. Fluent Bit config in values/fluent-bit.yml: tail input (Skip_Long_Lines On, docker and cri multiline parsers), kubernetes filter (Merge_Log On, Keep_Log Off), http output (json_lines, gzip). vlagent uses jsonline output with includeNodeLabels. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | not stated |
| **Why it wins** | Not given in the repo or README. The only related note is in values/vlagent.yml: vlagent's native VictoriaLogs format would use about 20% less CPU than the jsonline format chosen for a fair comparison with the other collectors. |
| **Adoption** | 2.4k stars (VictoriaLogs repo; vlagent lives in app/vlagent); benchmark repo 29 stars |
| **Last commit** | 2026-10-09 |
| **Links** | [repository](https://github.com/VictoriaMetrics/VictoriaLogs) · [benchmark](https://raw.githubusercontent.com/VictoriaMetrics/log-collectors-benchmark/HEAD/results/2026-09-17/vlagent-resources.json) |

## Verdict

In VictoriaMetrics' own log-collectors-benchmark (kind cluster on a c2d-highcpu-8 GCP VM per the results-page template, each collector capped at 1 CPU and 1 GiB, prebuilt Helm images), vlagent v1.52.0 shipping 10 Pods x 1000 JSON lines/s for one hour averaged 0.048 cores and 31.6 MiB RSS against Fluent Bit v5.0.9's 0.204 cores and 53.5 MiB with zero versus 3 lost lines; in the ramp-to-saturation case vlagent peaked at about 178k logs/s while Fluent Bit was OOM-killed at about 41k logs/s with a later-fixed buffer config.

## Use it when

- Collecting Kubernetes container logs into VictoriaLogs where per-node collector CPU and memory matter (about 0.05 cores and 32 MiB average RSS at 10k JSON lines per second in the vendor run).
- Log volumes per node in the tens to low hundreds of thousands of JSON lines per second on a 1-CPU budget (about 178k logs/s peak in the vendor throughput case).
- You need replication to several VictoriaLogs instances with on-disk buffering during outages, without adding a separate aggregation tier.
- Mostly JSON or klog-formatted container output, which vlagent parses and maps to _msg and _time automatically.

## Skip it when

- You need Fluent Bit's breadth: many inputs, filters, Lua or WASM processing, and outputs to Elasticsearch, Kafka, S3, Loki and so on; vlagent only writes VictoriaLogs native or jsonline over HTTP.
- Log files rotated with copytruncate or compressed .gz files: the docs say copytruncate is not fully supported and .gz files are not read.
- Syslog or CEF over TCP ingestion: open issues #1697 (CEF messages corrupted when several arrive in one TCP read) and #1365 (embedded newlines split into fragments).
- Non-Kubernetes edge or embedded hosts where a small C binary with a mature plugin ecosystem is the requirement; vlagent is young (bug-fix panics were still being closed in October 2026).

## How it is fast

The repo and docs give no explanation; the source shows a narrow, purpose-built pipeline: a hand-written CRI line parser with a fast path for unsplit lines (partial lines are joined only on the slow path, capped at 2 MiB), JSON parsing with VictoriaLogs' pooled logstorage JSON parser and valyala/fastjson, zero-copy byte-to-string conversion (bytesutil.ToUnsafeString), sync.Pool-recycled buffers and parsers, and Pod metadata computed once per log file as common fields instead of per record. Output batches are compressed with zstd in jsonline mode, while the Fluent Bit config in the same benchmark compresses with gzip, so part of the CPU gap is the codec. values/vlagent.yml says the native VictoriaLogs format would cut CPU by about another 20%.

## Compared with alternatives

Against the Vector-versus-Fluent-Bit sibling: pick vlagent when the sink is VictoriaLogs and node CPU is the constraint; in this same VictoriaMetrics harness on 2026-09-17, Vector v0.58.0 used 0.288 cores and 106 MiB average RSS at 10k logs/s and peaked at 32k logs/s, worse than Fluent Bit, so the Rust collector's win in its own harness does not carry over here. Pick Vector when you need its transform language and many sinks.

## Integration

| | |
|---|---|
| **Form** | Go binary (vlagent-prod in the vlutils release archive; Docker images victoriametrics/vlagent; Helm chart vm/victoria-logs-collector) |
| **Dependencies** | none at runtime beyond the Kubernetes API for Pod discovery; built from the VictoriaLogs Go module (VictoriaMetrics lib, valyala/fastjson) |
| **Minimum toolchain** | Go toolchain of the VictoriaLogs repo to build from source (version not documented in the files read); prebuilt binaries and images need none |
| **Platforms** | Linux amd64 and arm64 images (multiarch build directory); the file collector also runs outside Kubernetes |
| **Thread safety** | not applicable (standalone agent process) |
| **Drop-in for the baseline** | partial — replaces the Fluent Bit DaemonSet role for Kubernetes Pod logs bound for VictoriaLogs or a jsonline HTTP receiver, but uses its own flags and Helm values and has no Fluent Bit plugin compatibility |

## Gotchas

- Harness detail the record misreads: AvgCPUUsage in the throughput case is avg_over_time of the CPU rate across the whole ramp (bench start through saturation, then one idle minute), not CPU at the peak. Scaling the resources-case cost per log (about 4.5 microseconds of CPU for vlagent, 18.7 for Fluent Bit, derived from page data) puts vlagent near 0.8 cores at its 178k logs/s peak and Fluent Bit near 0.77 cores when it was OOM-killed at 41k, so both were approaching the 1-CPU limit; a Fluent Bit run that did not OOM would top out near 53k logs/s at 1 core by the same arithmetic, making the throughput gap closer to 3.3x than 4.3x (rough estimate, not a measurement).
- Throughput is max_over_time of a 1-minute receive rate sampled every 10 s, a peak rather than a sustained rate, and each case is one run on one c2d-highcpu-8 node (8 vCPUs) shared with the 50 generator Pods, log-verifier, VictoriaMetrics and Grafana; vlagent's nearly identical ceiling in all three rounds (176.7k to 178.3k) may partly reflect the node rather than the agent.
- The Fluent Bit throughput figure in all committed rounds is an OOM failure point: values/fluent-bit.yml gained Mem_Buf_Limit 512MB only after the results were produced, and no post-fix results are committed (results/ holds only 2026-08-12, 2026-09-16 and 2026-09-17). The Fluent Bit config also runs the docker and cri multiline parsers and gzip, versus zstd for vlagent.
- Panics on a deleted collected file ending without a newline (#1552) and on unreadable files during rotated-file lookup (#1796) were closed on 2026-10-01, after the benchmarked v1.52.0; use a later release.

## Known shortcomings

- Vendor-run with no hardware stated; the 4.3x throughput rests on Fluent Bit being OOM-killed in all rounds (the Mem_Buf_Limit fix c53524a postdates the results at bd89fd0), so only the resources case is usable (4.3x less CPU, 1.7x less memory); product against product, not a language-level comparison.
- Enricher: AvgCPUUsage is an average over the whole ramp plus one idle minute (bench-runner/report.go), not CPU at peak, so 'neither reached the 1-CPU limit' is wrong: scaling per-log CPU puts vlagent near 0.8 cores at 178k logs/s and Fluent Bit near 0.77 at its OOM, and a fair Fluent Bit 1-core ceiling of about 53k makes the throughput gap about 3.3x, not 4.3x (estimate). Throughput is a peak (max_over_time of a 1-minute rate) from one run per case on a shared c2d-highcpu-8 GCP VM that also hosts 50 generator pods, the verifier, VictoriaMetrics and Grafana. Codecs differ (vlagent jsonline zstd vs Fluent Bit gzip plus docker/cri multiline parsers). No post-fix Fluent Bit results; vlagent panics #1552 and #1796 were closed after the benchmarked v1.52.0.

## Caveats and trade-offs

First-party benchmark: VictoriaMetrics runs the suite and sells VictoriaLogs, so the tier is capped at C. Hardware is not stated (results/&lt;date&gt;/info.json records only the git hash, bd89fd0 for 2026-09-17). The Fluent Bit throughput run failed in all three committed rounds (OOMKilled, 252175 to 1133131 lines lost) while using about 0.41 to 0.43 cores, so the 41222 logs/s figure is a memory failure point caused by a missing Mem_Buf_Limit, not a CPU-bound capacity figure; the maintainers added Mem_Buf_Limit 512MB on 2026-09-23 (commit c53524a, 'Prevent FluentBit from OOMs') after these results were produced at bd89fd0, and no post-fix results are committed, so the throughput ratio rests on a crippled baseline and only the resources-case CPU and memory figures are a like-for-like comparison. vlagent itself peaked at 0.475 cores in the throughput case, so its 178k logs/s ceiling may be set by the generator or verifier rather than by vlagent. This is an application-against-application comparison of two different pipelines (Fluent Bit's tail input with kubernetes filter Merge_Log, vlagent's jsonline output with includeNodeLabels), not the same algorithm and not a Go-against-C language claim. Fluent Bit uses an untuned configuration close to the Helm chart defaults, and the README invites tuning PRs. Each collector is limited to 1 CPU and 1 GiB. The 2026-09-16 and 2026-09-17 rounds were committed together (commit 31266d0) to confirm node configuration did not change results. The published results page and blog post are on blocked hosts, so numbers here come from the committed JSON files only. One run per round per case. [retier] Enricher: AvgCPUUsage averages the whole ramp plus an idle minute, so both collectors were near the 1-CPU limit at peak; a fair Fluent Bit 1-core ceiling of about 53k logs/s makes the gap about 3.3x, not 4.3x (estimate). One run per case on a shared c2d-highcpu-8 GCP VM (also hosting 50 generator pods, the verifier, VictoriaMetrics and Grafana); codecs differ (zstd vs gzip with multiline parsers).

vlagent is a Go program that lives inside the VictoriaLogs repository (app/vlagent) and targets VictoriaLogs-compatible insert APIs; Fluent Bit supports many more inputs, filters and outputs. In the one-hour resources case vlagent also uses less memory (31.6 MiB average against 53.5 MiB, derived).

## Maintenance

Actively developed inside the Apache-2.0 VictoriaLogs repo (last commit 2026-10-09, 2.4k stars) with releases every few weeks and a steady flow of closed bug reports; the benchmark is first-party, single-run and vendor-published, so treat the 4x CPU figure as indicative and re-run the harness (go run ./bench-runner, about 10 hours) with your own Fluent Bit tuning before relying on it.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The committed results JSON files (results/2026-08-12, 2026-09-16, 2026-09-17) match every claimed number, but the suite is run by VictoriaMetrics, which sells VictoriaLogs, and no hardware is stated anywhere (info.json holds only the git hash), so first-party tier C.
- **Verifier notes:** All numbers match the committed JSON; keep at C with the throughput case flagged as a crippled (OOM-killed, later-fixed config) baseline and the resources case (4.3x less CPU, 1.7x less memory at about 10k logs/s) as the usable claim. Not a language-level win: two different products and pipelines. why_faster stays unexplained by the source beyond the 20% native-format note in values/vlagent.yml.
- **Fields the verifier corrected:** `claimed_speedup`, `last_commit`, `caveats`, `hardware`
- **Shortcomings recorded by:** verifier batch-118 (wave 14 seed pass, 2026-10-13); enricher (seed pass, 2026-10-13)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/VictoriaMetrics/log-collectors-benchmark/HEAD/results/2026-09-17/vlagent-resources.json>
  - <https://raw.githubusercontent.com/VictoriaMetrics/log-collectors-benchmark/HEAD/results/2026-09-17/fluent-bit-resources.json>
  - <https://raw.githubusercontent.com/VictoriaMetrics/log-collectors-benchmark/HEAD/results/2026-09-17/vlagent-throughput.json>
  - <https://raw.githubusercontent.com/VictoriaMetrics/log-collectors-benchmark/HEAD/results/2026-09-17/fluent-bit-throughput.json>
  - <https://raw.githubusercontent.com/VictoriaMetrics/log-collectors-benchmark/HEAD/results/2026-09-17/info.json>
  - <https://raw.githubusercontent.com/VictoriaMetrics/log-collectors-benchmark/HEAD/results/2026-08-12/vlagent-throughput.json>
  - <https://raw.githubusercontent.com/VictoriaMetrics/log-collectors-benchmark/HEAD/results/2026-08-12/fluent-bit-throughput.json>
  - <https://raw.githubusercontent.com/VictoriaMetrics/log-collectors-benchmark/HEAD/results/2026-09-16/vlagent-throughput.json>
  - <https://raw.githubusercontent.com/VictoriaMetrics/log-collectors-benchmark/HEAD/results/2026-09-16/fluent-bit-throughput.json>
  - <https://raw.githubusercontent.com/VictoriaMetrics/log-collectors-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/VictoriaMetrics/log-collectors-benchmark/HEAD/values/fluent-bit.yml>
  - <https://raw.githubusercontent.com/VictoriaMetrics/log-collectors-benchmark/HEAD/values/vlagent.yml>
  - <https://github.com/VictoriaMetrics/log-collectors-benchmark/commits>
  - <https://github.com/VictoriaMetrics/log-collectors-benchmark/commit/31266d0>
  - <https://github.com/VictoriaMetrics/VictoriaLogs>
  - <https://github.com/VictoriaMetrics/VictoriaLogs/commits>
  - <https://github.com/VictoriaMetrics/VictoriaLogs/tree/master/app>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/VictoriaMetrics/log-collectors-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/VictoriaMetrics/log-collectors-benchmark/HEAD/values/fluent-bit.yml>
  - <https://raw.githubusercontent.com/VictoriaMetrics/log-collectors-benchmark/HEAD/values/vlagent.yml>
  - <https://raw.githubusercontent.com/VictoriaMetrics/log-collectors-benchmark/HEAD/results/2026-09-17/vlagent-throughput.json>
  - <https://raw.githubusercontent.com/VictoriaMetrics/log-collectors-benchmark/HEAD/results/2026-09-17/fluent-bit-throughput.json>
  - <https://raw.githubusercontent.com/VictoriaMetrics/log-collectors-benchmark/HEAD/results/2026-09-17/vlagent-resources.json>
  - <https://raw.githubusercontent.com/VictoriaMetrics/log-collectors-benchmark/HEAD/results/2026-09-17/fluent-bit-resources.json>
  - <https://raw.githubusercontent.com/VictoriaMetrics/log-collectors-benchmark/HEAD/results/2026-09-17/vector-throughput.json>
  - <https://raw.githubusercontent.com/VictoriaMetrics/log-collectors-benchmark/HEAD/results/2026-09-17/vector-resources.json>
  - <https://github.com/VictoriaMetrics/log-collectors-benchmark/tree/main/bench-runner>
  - <https://raw.githubusercontent.com/VictoriaMetrics/log-collectors-benchmark/HEAD/bench-runner/main.go>
  - <https://raw.githubusercontent.com/VictoriaMetrics/log-collectors-benchmark/HEAD/bench-runner/report.go>
  - <https://raw.githubusercontent.com/VictoriaMetrics/log-collectors-benchmark/HEAD/bench-runner/exec.go>
  - <https://raw.githubusercontent.com/VictoriaMetrics/log-collectors-benchmark/HEAD/bench-runner/index.go>
  - <https://raw.githubusercontent.com/VictoriaMetrics/log-collectors-benchmark/HEAD/bench-runner/index.gohtml>
  - <https://github.com/VictoriaMetrics/log-collectors-benchmark/tree/master/results>
  - <https://github.com/VictoriaMetrics/VictoriaLogs/tree/master/app/vlagent>
  - <https://github.com/VictoriaMetrics/VictoriaLogs/tree/master/app/vlagent/kubernetescollector>
  - <https://raw.githubusercontent.com/VictoriaMetrics/VictoriaLogs/HEAD/app/vlagent/kubernetescollector/processor.go>
  - <https://raw.githubusercontent.com/VictoriaMetrics/VictoriaLogs/HEAD/app/vlagent/kubernetescollector/README.md>
  - <https://raw.githubusercontent.com/VictoriaMetrics/VictoriaLogs/HEAD/docs/victorialogs/vlagent.md>
  - <https://github.com/VictoriaMetrics/VictoriaLogs/issues?q=is%3Aissue+vlagent+label%3Abug>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/victoriametrics/victorialogs`) · [data/wave14/enrich/raw/github_com_victoriametrics_victorialogs.json](../../../data/wave14/enrich/raw/github_com_victoriametrics_victorialogs.json) (enrichment confidence 0.7)

</details>
