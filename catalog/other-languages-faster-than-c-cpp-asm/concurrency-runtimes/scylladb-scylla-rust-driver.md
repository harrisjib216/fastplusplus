# ScyllaDB Rust driver (async Tokio CQL driver vs C++ driver)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Concurrency runtimes](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0 OR MIT` · 🟢 active

> Pure-Rust async Tokio CQL driver for ScyllaDB and Cassandra; the vendor's insert benchmark shows it level with the multi-threaded DataStax C++ driver.

| | |
|---|---|
| **Beats** | DataStax Cassandra C++ driver ('cpp-multi', v2.16.0 .deb per the current Dockerfile, run with I/O threads = hardware_concurrency), plus the Scylla C++ driver fork ('cpp'), which the harness ran with a single I/O thread until commit 'Bump Scylla cpp driver to 2.16.2, remove single thread limitation for it' (2022-08-01) |
| **Claimed result** | Published chart images/bench10to7-inserts.svg (10,000,000 inserts, time in seconds; values read from the SVG bar geometry, derived from page data): concurrency 512/1024/2048/4096/8192: scylla-rust-driver 12.8/9.3/7.4/6.6/6.5 s; cpp-multi (DataStax C++ driver, multi-threaded) 13.4/9.9/7.7/6.7/6.3 s, so Rust is about 1.05x/1.07x/1.05x/1.02x faster and 0.97x (slower) at 8192, i.e. parity; cpp (Scylla C++ driver on one I/O thread) 54.9/53.0/56.5/53.8/64.1 s, about 4.3x-9.9x slower than Rust, but that baseline was single-threaded. The cited generate_chart/config.py (1,000,000 inserts, concurrency 1024: scylla-rust-driver 3734 ms vs cpp-driver 5510 ms, about 1.48x, derived from page data) is the chart generator's input file, matches the harness defaults, and does not correspond to any published chart. A ScyllaDB blog post (2021-07-13) reportedly says the Rust driver was 'generally either just as fast or even slightly faster' than cpp-multi (snippet only). |
| **Workload** | 'Basic' benchmark, inserts workload: 10,000,000 prepared INSERTs (pk, 2\*pk, 3\*pk) into one local ScyllaDB node started by scylla.sh, with 512, 1024, 2048, 4096 and 8192 requests in flight; total wall time per driver, one run per cell. The harness default (and config.py title) is 1,000,000 tasks at concurrency 1024. |
| **Metric** | throughput |
| **Compiler and flags** | Benchmark harnesses: C++ main.cpp built with Ubuntu 18.04 g++ (7.x) as 'g++ main.cpp -std=c++17 -lcassandra -O3 -flto' against prebuilt driver .deb packages (DataStax 2.16.0; Scylla cpp-driver 2.16.2 at HEAD, earlier version at chart time; library build flags not stated); Rust built with 'cargo build --release', [profile.release] lto = true, latest rustup toolchain at image build time, scylla crate from the git main branch, tokio 1.x multi-threaded runtime (#[tokio::main]). |
| **Kind** | library or program |
| **Same algorithm as the baseline** | not stated |
| **Same optimization level** | not stated |
| **Adoption** | 689 stars (scylla-rust-driver); benchmark repo cvybhu/rust-driver-benchmarks has 84 commits, last 2022-08-05 |
| **Last commit** | 2026-10-10 |
| **Links** | [repository](https://github.com/scylladb/scylla-rust-driver) · [benchmark](https://raw.githubusercontent.com/cvybhu/rust-driver-benchmarks/HEAD/images/bench10to7-inserts.svg) |

## Verdict

Vendor chart images/bench10to7-inserts.svg (2021-06-20): 10,000,000 prepared INSERTs at 512/1024/2048/4096/8192 requests in flight, one run per cell, hardware unstated. Rust driver 12.8/9.3/7.4/6.6/6.5 s against the multi-threaded DataStax C++ driver 13.4/9.9/7.7/6.7/6.3 s (parity), and 53-64 s for the Scylla C++ fork on one I/O thread. The C++ harness was built with g++ -O3 -flto against prebuilt .deb driver packages, the Rust harness with cargo --release and lto = true.

## Use it when

- Rust services on Tokio that talk to ScyllaDB and benefit from shard-aware and tablet-aware routing.
- High-concurrency write or read loads (hundreds to thousands of requests in flight), the regime the benchmark exercised with 512-8192 concurrent requests.
- Rust code currently using cassandra-cpp (bindings over the DataStax C++ driver) that wants to drop the C++ library dependency without losing throughput.
- Apache Cassandra clusters from Rust, where it is compatible but loses the ScyllaDB-only shard routing.

## Skip it when

- Expecting a throughput gain over the multi-threaded C/C++ driver: the only like-for-like published chart shows parity (2-7% faster at 512-4096 requests in flight, about 3% slower at 8192).
- CPU-constrained clients: a later ScyllaDB write-up (search snippet only) reported the Rust driver using about twice the CPU of a cassandra-cpp backend in a loopback test, attributed to extra syscalls; write coalescing targets this, but no newer comparison was found.
- Low-rate, latency-sensitive callers on a busy Tokio executor: the SessionBuilder docs warn that write coalescing may worsen latency in that case.
- Programs not on Tokio, or C/C++ programs: Tokio is required, and C/C++ needs the separate cpp-rust-driver binding.

## How it is fast

On ScyllaDB the default pool keeps one connection per shard and routes each request to the shard that owns its token (shard-aware and tablet-aware routing), so the server skips cross-shard forwarding. Write coalescing, on by default, waits a small nondeterministic delay to batch several queued requests into one socket write syscall. Many requests are multiplexed per connection on a multi-threaded Tokio executor, and rows can be deserialized zero-copy from the response frame.

## Compared with alternatives

The Tokio sibling entries (1M-task memory, TCP echo against libuv) measure the runtime this driver is built on; pick this entry only when the job is speaking CQL to ScyllaDB or Cassandra from Rust. Do not pick it for a speed edge over C++.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | tokio 1.40+, futures; optional openssl 0.10 / tokio-openssl or rustls 0.23 / tokio-rustls for TLS; compression and other extras behind Cargo features |
| **Minimum toolchain** | Rust 1.88 for crate 1.9.0 (crates.io rust_version); the main-branch README states MSRV 1.89 |
| **Platforms** | not documented (any target Tokio supports) |
| **Thread safety** | not documented in the pages read; the benchmark shares one Session through Arc across 512-8192 spawned Tokio tasks |
| **Drop-in for the baseline** | no |

## Gotchas

- Shard-awareness asymmetry in the harness: scylla.sh starts ScyllaDB with --smp 4, the Rust driver keeps one connection per shard and routes to the owning shard, while the DataStax cpp-driver ('cpp-multi') is not shard-aware (ScyllaDB's fork advertises shard-awareness as its addition). So part of any Rust edge here is server-side routing rather than client efficiency, and the Rust driver still only reaches parity.
- The benchmark cannot be rebuilt: benchmarks/basic/scylla-rust-driver/source/Cargo.toml pins the driver to git branch main with no Cargo.lock, but main.rs imports scylla::prepared_statement, scylla::{IntoTypedRows, Session} and calls session.execute, none of which exist in today's lib.rs (Session moved to scylla::client::session, statements to scylla::statement, execute became execute_unpaged). build.sh therefore fails today, and the 2021-06-20 chart measured a pre-1.0 driver.
- Chart provenance is unclear: the repo's scylla.sh describes one local 4-shard node, while the 2021 ScyllaDB blog post (snippet only) describes a 3-node Scylla 4.4 cluster on i3.4xlarge with a c5.9xlarge loader. Nothing ties the chart to either setup, and each cell is one run with no hardware or variance stated.
- The headline 4.3-9.9x lead is over the Scylla C++ fork capped to one I/O thread, a limit removed from the harness on 2022-08-01 without a new chart. The 3734 vs 5510 ms figures in generate_chart/config.py are chart-generator input with no matching run.

## Known shortcomings

- Not faster: the published bench10to7-inserts.svg (10M inserts) has the Rust driver at parity with the multi-threaded DataStax C++ driver (1.02-1.07x at 512-4096, 0.97x at 8192); the 4.3-9.9x lead is only over the Scylla C++ driver on one I/O thread (crippled baseline, harness fixed 2022-08-01); the 3734 vs 5510 ms in config.py has no provenance.
- Shard asymmetry: scylla.sh runs --smp 4, the Rust driver is shard-aware and the DataStax cpp-multi driver is not, yet the result is still only parity. The benchmark is not rebuildable: Cargo.toml pins git main with no Cargo.lock, and main.rs uses removed APIs (scylla::prepared_statement, IntoTypedRows, execute). Chart provenance is unclear (a local node versus the blog's 3-node i3.4xlarge cluster, snippet only).

## Caveats and trade-offs

Vendor benchmark (ScyllaDB). Against the fair multi-threaded C++ baseline (DataStax cpp-driver, 'cpp-multi') the published 2021-06-20 chart shows parity: Rust 2-7% faster at concurrency 512-4096 and about 3% slower at 8192. The large lead (4.3x-9.9x) is only over the Scylla C++ driver fork run on a single I/O thread, a limitation the harness removed on 2022-08-01 with no re-published chart, so that comparison is a crippled baseline. The cited config.py numbers (3734 vs 5510 ms) are the generator's input with the harness's default title and cannot be tied to a published run. The README itself says the chart 'is pretty old' and driver names changed. No hardware, no run count, no variance; values were read from SVG bar geometry, so they are approximate. The C++ driver libraries are prebuilt .deb packages whose build flags are not stated. A ScyllaDB 2021 blog post (scylladb.com, not reachable here) reportedly ran a 3-node Scylla 4.4 cluster on i3.4xlarge and found the Rust driver 'just as fast or even slightly faster' than cpp-multi; a later ScyllaDB write-up reportedly found it used about twice the CPU of the cassandra-cpp backend in a loopback test (snippets only). The scylla-rust-driver README makes no speed claim. The driver is Apache-2.0 OR MIT; the benchmark repo has no LICENSE file. A database driver rather than a general concurrency runtime, so the category fit is loose. [retier] Shard asymmetry: scylla.sh runs --smp 4, the Rust driver is shard-aware and the DataStax cpp-multi driver is not, yet the result is only parity. The benchmark is not rebuildable: Cargo.toml pins git main with no Cargo.lock, and main.rs uses removed APIs (scylla::prepared_statement, IntoTypedRows, execute). Chart provenance is unclear (local node versus the blog's 3-node i3.4xlarge cluster).

Rust crate; C++ programs get it through the scylla-cpp-rust-driver bindings (ScyllaDB's C++ API over the Rust core), which the benchmark repo lists as a separate driver. Async Tokio runtime inside the driver.

## Maintenance

Actively maintained and production-ready by its own statement (crate 1.9.0 released 2026-09-15, about 9.5M crates.io downloads, 689 stars, 123 open issues of which 20 are labelled performance), dual MIT/Apache-2.0. The supporting benchmark repo has been idle since 2022-08-05 and no longer builds against the driver.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification C, tier now C.
- **Tier reason:** Vendor (ScyllaDB) benchmark repo cvybhu/rust-driver-benchmarks: the cited config.py does hold 3734 vs 5510 ms, but it is the chart generator's input with the harness's default title and no provenance; the published chart (images/bench10to7-inserts.svg, matplotlib, 2021-06-20) shows the Rust driver at parity with the multi-threaded DataStax C++ driver, and its large lead only over the Scylla C++ driver that the harness then limited to one I/O thread. Harness code and flags are public (g++ -O3 -flto; cargo --release with lto) but the drivers are prebuilt .deb packages and no hardware is stated, so not A; first-party vendor numbers, so C.
- **Verifier notes:** Downgrade of the claim, tier stays C: the fair C++ baseline in the published chart is at parity (flag as not faster), and the 1.48x figure is unprovenanced generator input while the big lead is over a single-threaded C++ driver (crippled baseline, since fixed in the harness). Usability corrected to copyable (driver is Apache-2.0 OR MIT).
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `claimed_speedup`, `compiler_and_flags`, `workload`, `usability`, `caveats`
- **Shortcomings recorded by:** verifier batch-33 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/cvybhu/rust-driver-benchmarks/HEAD/generate_chart/config.py>
  - <https://raw.githubusercontent.com/cvybhu/rust-driver-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/cvybhu/rust-driver-benchmarks/HEAD/images/bench10to7-inserts.svg>
  - <https://github.com/cvybhu/rust-driver-benchmarks>
  - <https://github.com/cvybhu/rust-driver-benchmarks/tree/master/benchmarks/basic>
  - <https://github.com/cvybhu/rust-driver-benchmarks/commits/main>
  - <https://raw.githubusercontent.com/cvybhu/rust-driver-benchmarks/HEAD/benchmarks/basic/README.md>
  - <https://raw.githubusercontent.com/cvybhu/rust-driver-benchmarks/HEAD/benchmarks/basic/build_all_dockers.sh>
  - <https://raw.githubusercontent.com/cvybhu/rust-driver-benchmarks/HEAD/benchmarks/basic/scylla-cpp-driver/Dockerfile>
  - <https://raw.githubusercontent.com/cvybhu/rust-driver-benchmarks/HEAD/benchmarks/basic/scylla-cpp-driver/build.sh>
  - <https://raw.githubusercontent.com/cvybhu/rust-driver-benchmarks/HEAD/benchmarks/basic/scylla-cpp-driver/run.sh>
  - <https://raw.githubusercontent.com/cvybhu/rust-driver-benchmarks/HEAD/benchmarks/basic/scylla-cpp-driver/source/main.cpp>
  - <https://raw.githubusercontent.com/cvybhu/rust-driver-benchmarks/HEAD/benchmarks/basic/datastax-cpp-driver/Dockerfile>
  - <https://raw.githubusercontent.com/cvybhu/rust-driver-benchmarks/HEAD/benchmarks/basic/datastax-cpp-driver/source/main.cpp>
  - <https://raw.githubusercontent.com/cvybhu/rust-driver-benchmarks/HEAD/benchmarks/basic/scylla-rust-driver/Dockerfile>
  - <https://raw.githubusercontent.com/cvybhu/rust-driver-benchmarks/HEAD/benchmarks/basic/scylla-rust-driver/run.sh>
  - <https://raw.githubusercontent.com/cvybhu/rust-driver-benchmarks/HEAD/benchmarks/basic/scylla-rust-driver/source/src/main.rs>
  - <https://raw.githubusercontent.com/cvybhu/rust-driver-benchmarks/HEAD/benchmarks/basic/scylla-rust-driver/source/Cargo.toml>
  - <https://github.com/scylladb/scylla-rust-driver>
  - <https://github.com/scylladb/scylla-rust-driver/commits/main>
- **Sources the enricher read:**
  - <https://github.com/scylladb/scylla-rust-driver>
  - <https://raw.githubusercontent.com/scylladb/scylla-rust-driver/main/README.md>
  - <https://raw.githubusercontent.com/scylladb/scylla-rust-driver/main/scylla/Cargo.toml>
  - <https://raw.githubusercontent.com/scylladb/scylla-rust-driver/main/scylla/src/lib.rs>
  - <https://raw.githubusercontent.com/scylladb/scylla-rust-driver/main/scylla/src/client/session_builder.rs>
  - <https://github.com/scylladb/scylla-rust-driver/issues?q=is%3Aissue+is%3Aopen+label%3Aperformance>
  - <https://crates.io/api/v1/crates/scylla>
  - <https://raw.githubusercontent.com/scylladb/cpp-driver/master/README.md>
  - <https://raw.githubusercontent.com/cvybhu/rust-driver-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/cvybhu/rust-driver-benchmarks/HEAD/scylla.sh>
  - <https://raw.githubusercontent.com/cvybhu/rust-driver-benchmarks/HEAD/images/bench10to7-inserts.svg>
  - <https://raw.githubusercontent.com/cvybhu/rust-driver-benchmarks/HEAD/generate_chart/config.py>
  - <https://raw.githubusercontent.com/cvybhu/rust-driver-benchmarks/HEAD/benchmarks/basic/README.md>
  - <https://raw.githubusercontent.com/cvybhu/rust-driver-benchmarks/HEAD/benchmarks/basic/scylla-rust-driver/source/src/main.rs>
  - <https://raw.githubusercontent.com/cvybhu/rust-driver-benchmarks/HEAD/benchmarks/basic/scylla-rust-driver/source/src/config.rs>
  - <https://raw.githubusercontent.com/cvybhu/rust-driver-benchmarks/HEAD/benchmarks/basic/scylla-rust-driver/source/Cargo.toml>
  - https://raw.githubusercontent.com/cvybhu/rust-driver-benchmarks/HEAD/benchmarks/basic/scylla-rust-driver/source/Cargo.lock (404, no lockfile)
  - <https://raw.githubusercontent.com/cvybhu/rust-driver-benchmarks/HEAD/benchmarks/basic/scylla-rust-driver/Dockerfile>
  - <https://raw.githubusercontent.com/cvybhu/rust-driver-benchmarks/HEAD/benchmarks/basic/datastax-cpp-driver/source/main.cpp>
  - <https://raw.githubusercontent.com/cvybhu/rust-driver-benchmarks/HEAD/benchmarks/basic/datastax-cpp-driver/source/config.hpp>
  - <https://raw.githubusercontent.com/cvybhu/rust-driver-benchmarks/HEAD/benchmarks/basic/scylla-cpp-driver/source/main.cpp>
  - https://thenewstack.io/async-rust-in-practice-performance-pitfalls-profiling/ (blocked, ENOTFOUND; WebSearch snippet only)
  - https://www.scylladb.com/2021/07/13/scylla-rust-driver-update-and-benchmarks/ (WebSearch snippet only)
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/scylladb/scylla-rust-driver`) · [data/wave14/enrich/raw/github_com_scylladb_scylla_rust_driver.json](../../../data/wave14/enrich/raw/github_com_scylladb_scylla_rust_driver.json) (enrichment confidence 0.6)

</details>
