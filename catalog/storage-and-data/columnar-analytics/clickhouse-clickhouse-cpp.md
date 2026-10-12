# clickhouse-cpp

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Columnar analytics](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Official C++17 native-protocol ClickHouse client; reads columnar blocks far faster than HTTP, JDBC, Python or reflection-based Go clients.

| | |
|---|---|
| **Beats** | ClickHouse HTTP interface via curl; official clickhouse-jdbc (Java, HTTP), ClickHouse/clickhouse-go and Python clickhouse-driver clients |
| **Claimed result** | ch-bench README table (best results, runs from January to June 2022): clickhouse-cpp 516ms / 6.9M RAM vs curl (C, HTTP) 3.7s, clickhouse-jdbc (Java, HTTP) 7.2s, clickhouse-driver (Python) 37s, ClickHouse/clickhouse-go (Go) 46.8s; the page's own ratio column gives clickhouse-cpp 1.47x, curl 9x, clickhouse-jdbc 18x, clickhouse-driver Python 106x, clickhouse-go 117x relative to the \~1x leaders (about 7.2x vs curl, 14x vs clickhouse-jdbc, 72x vs Python clickhouse-driver, 91x vs clickhouse-go, derived from page data). The repo's hyperfine exports give smaller Go gaps: RESULTS.md clickhouse-cpp 611.3 ms vs clickhouse-go 6529.0 ms (about 10.7x) and RESULTS.slow.md 579.5 ms vs 38253.9 ms (about 66x) (derived from page data). Not the fastest client: ch-go 401ms and the C++ clickhouse-client 387ms are faster, and the README's C++ hyperfine table puts clickhouse-cpp at 574.4 ms vs clickhouse-client 561.9 ms (parity). |
| **Workload** | Client overhead reading SELECT number FROM system.numbers_mt LIMIT 500000000 (500 million UInt64 rows, 4.0 GB) from a localhost ClickHouse server, wall time and client RAM per library. |
| **Metric** | throughput |
| **Adoption** | 385 stars (official ClickHouse C++ client) |
| **Last commit** | 2026-09-28 |
| **Links** | [repository](https://github.com/ClickHouse/clickhouse-cpp) · [benchmark](https://raw.githubusercontent.com/ClickHouse/ch-bench/HEAD/README.md) |

## Verdict

In the ClickHouse/ch-bench suite (written for ch-go), reading SELECT number FROM system.numbers_mt LIMIT 500000000 (4.0 GB) from a localhost server took 516 ms and 6.9 MB RAM with clickhouse-cpp vs 3.7 s for curl over HTTP, 7.2 s for clickhouse-jdbc, 37 s for Python clickhouse-driver and 46.8 s for clickhouse-go, but 387 ms for clickhouse-client and 401 ms for ch-go; these are 2022 best-of results with no CPU model, compiler, C++ build flags or server version, and the repo's own hyperfine exports give much smaller Go gaps (611.3 ms vs 6529.0 ms in RESULTS.md).

## Use it when

- A C++ service that already runs against a ClickHouse server and needs to pull or push large columnar result sets (millions of rows) with minimal client CPU and RAM (6.9 MB in ch-bench).
- Bulk ingestion from C++ where you can batch rows into Blocks and send them with Insert or BeginInsert/SendInsertBlock rather than issuing per-row SQL.
- Replacing a curl/HTTP or JDBC path in a C++ or mixed codebase when transport and row formatting dominate: ch-bench shows 516 ms vs 3.7 s for curl on 500M UInt64 rows.
- Linux, macOS or Windows (MSVC and MinGW) builds via CMake, or Bazel (experimental), when you want TLS via OpenSSL or BoringSSL and LZ4/ZSTD compression bundled.

## Skip it when

- When you want analytics in-process without a server: it is only a client, and it is not faster than ClickHouse's own clickhouse-client or the Go ch-go client (parity to about 1.3-1.5x slower in ch-bench).
- Small, frequent inserts sent as SQL text: issue #442 reports 1,600 rows/s over the native protocol vs 20,000 rows/s over HTTP for 100-row INSERT ... VALUES batches with async_insert settings (no maintainer analysis shown); the README notes SDK-side async inserts only work with SQL-text INSERTs, so batch rows into Blocks and use Insert or BeginInsert instead.
- Sharing one connection across threads: Client is documented as NOT thread-safe; you need one Client per thread or your own locking/pooling (no pool is provided).
- Projects that need a stable ABI or a recent tagged release: ABI compatibility is explicitly not guaranteed, and the newest tag (v2.6.2, June 2024 on the releases page) trails two years of master fixes.
- Code that wants row-at-a-time ORM-style access: the API is column-oriented and you index columns by position and cast with As/AsStrict.

## How it is fast

The native protocol ships data as columnar Blocks in ClickHouse's own little-endian layout, so fixed-width columns are loaded with one bulk read of rows\*sizeof(T) bytes straight into a std::vector&lt;T&gt; (ColumnVector::LoadBody calls WireFormat::ReadBytes); there is no per-row text or RowBinary parsing, reflection or per-value allocation. Socket I/O goes through a BufferedInput, and optional block compression uses LZ4 or ZSTD with a CityHash128 checksum per compressed frame. In ch-bench this puts it within about 1.0-1.5x of the fastest clients (ch-go, clickhouse-client) and far ahead of HTTP and row-oriented clients.

## Compared with alternatives

Pick it over chDB when you already run a ClickHouse server and need a lean C++ client rather than an embedded engine; it does not compete with the engine siblings (DataFusion, Velox, Databend, StarRocks), which execute queries themselves rather than fetch results from ClickHouse.

## Integration

| | |
|---|---|
| **Form** | static lib (shared optional on Linux; shared builds are rejected on macOS and MSVC) |
| **Dependencies** | Vendored LZ4, ZSTD and CityHash (system LZ4/ZSTD/Abseil selectable); vendored Abseil int128 unless CH_USE_ABSEIL_FOR_BIGNUM=OFF (the 3.x API setting); optional OpenSSL (WITH_OPENSSL) or BoringSSL under Bazel for TLS |
| **Minimum toolchain** | C++17, CMake 3.13+ (FetchContent example needs 3.14); Bazel via bzlmod (experimental) |
| **Platforms** | Linux, macOS, Windows MSVC and MinGW (CI workflows for each); little-endian hosts assumed (see gotchas) |
| **Thread safety** | Client is not thread-safe (README); use one Client per thread or external synchronization |
| **Drop-in for the baseline** | partial — it replaces the HTTP interface, JDBC or another driver only after rewriting data access to the Block/column API; SQL strings and server settings carry over |

## Gotchas

- The ch-bench numbers measure only block transfer and decoding: the C++ program sums block.GetRowCount() and never reads a value, the curl row pipes RowBinaryWithNamesAndTypes to /dev/null under time -v (no client deserialization, different timing method), and the table keeps the best of runs taken months apart in 2022 on unstated hardware with unstated compiler flags and server version.
- Default build flags differ from the API you probably want: without CH_USE_3X_API, Bool maps to ColumnUInt8, 128-bit integers need Abseil and GetCurrentEndpoint returns std::optional; the 3.x values change the API and CMAKE_BUILD_TYPE defaults to RelWithDebInfo when unset.
- Fixed-width values are copied raw from the wire (ReadFixed/ReadAll memcpy, ColumnVector::LoadBody) and no byte-swapping code appears in the sources read, so big-endian hosts are not handled; this is not documented.
- Open bug reports include a hang in recv during Insert when the server dies (#209), an Insert that does not always throw on server error (#406) and automatic reconnect dropping per-connection settings (#371); recv and compressed-block size validation fixes landed on master in September 2026 after the last tag.

## Known shortcomings

- Tier C, off-baseline: ClickHouse/ch-bench compares clients, not analytics engines (baseline_in_list false). Parity with the C++ clickhouse-client (574.4 vs 561.9 ms); the best-of 2022 numbers mix runs and the repo's hyperfine files give clickhouse-go 6529.0 ms, not 46.8 s; the curl row was timed with \time to /dev/null with no client deserialization; slower than ch-go (401 ms). No CPU, compiler or flags.
- Enricher: the ch-bench C++ program only sums GetRowCount and reads no values; the curl row times the HTTP transfer to /dev/null under time -v with no client decoding; 2022 best-of-runs with no CPU, compiler, flags or server version. Client is not thread-safe; no byte swap in the wire path, so big-endian hosts are unhandled (undocumented); last tag v2.6.2 (June 2024) trails master fixes; open bugs #209 (recv hang on Insert when the server dies), #406, #371; issue #442: small SQL-text inserts run 1,600 rows/s native vs 20,000 rows/s over HTTP.

## Caveats and trade-offs

Evidence lives in the separate ClickHouse/ch-bench repo (Apache-2.0, 36 stars, last commit 2023-08-31; README results table last edited June 2022, its C++ section January 2022), whose README calls it 'Totally unscientific and mostly unrealistic' and says the ClickHouse/ch-go project uses it to understand its own performance. The README table reports best results (not means) assembled from runs made months apart on unstated hardware, so every row reflects 2022-era client versions, and the repo's own hyperfine exports disagree on the Go rows (clickhouse-go 6529.0 ms in RESULTS.md and 38253.9 ms in RESULTS.slow.md vs 46.8s in the README). One synthetic query on localhost; CPU model, compiler and C++ build flags are not stated (the Makefile builds only the Go and Rust programs, Rust with -C target-cpu=native; ch-bench-cpp/bench.cpp has no build line) and the ClickHouse server version is not stated. The C++ program only sums block row counts (the library still decodes the UInt64 column); the curl row (curl/run.sh) pipes RowBinaryWithNamesAndTypes over HTTP to /dev/null under \time -v rather than hyperfine, so it measures HTTP transport and server-side row formatting with no client deserialization. The wins are native binary protocol vs HTTP and vs row-oriented or reflection-based Go/Java/Python clients; against the official C++ clickhouse-client (the natural C++ incumbent) and ch-go it is at parity or slower. Off-baseline for columnar-analytics: it is a client of ClickHouse compared with other ClickHouse clients, not faster than any listed engine. The repo's own bench/bench.cpp (Google Benchmark, SelectNumber over 1000 rows of three columns) has no baseline.

Native binary protocol client with a columnar Block API, so it avoids per-row parsing but the caller works with column blocks; C++17; built with CMake or Bazel.

## Maintenance

Actively maintained by ClickHouse (master commits through 2026-09-28, CI against server 26.3-26.9) and Apache-2.0, but the last tagged release is v2.6.2 from June 2024, so pin a master commit or expect to miss recent protocol-hardening fixes.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The ch-bench README table (ClickHouse org, written by the ch-go author) lists clickhouse-cpp 516ms vs curl 3.7s, clickhouse-jdbc 7.2s, Python clickhouse-driver 37s and clickhouse-go 46.8s with public programs (ch-bench-cpp/bench.cpp, curl/run.sh, Makefile), but no CPU model, no compiler or C++ build flags and no server version are stated, and the table reports best results gathered across runs, so it cannot reach A; not an independent suite, so C.
- **Verifier notes:** Numbers match the ch-bench README exactly; tier C stands. Shortcomings to record: off-baseline (client-vs-client comparison, not faster than ClickHouse/clickhouse-client; parity with clickhouse-client in the C++ hyperfine table), stale 2022 best-of numbers mixed across runs, curl row timed differently and without client deserialization, no CPU/compiler/flags; baseline_in_list set to false because none of the compared clients is a category baseline.
- **Fields the verifier corrected:** `baseline_in_list`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-87 (wave 6); enricher (wave 6)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/ClickHouse/ch-bench/HEAD/README.md>
  - <https://raw.githubusercontent.com/ClickHouse/ch-bench/HEAD/RESULTS.md>
  - <https://raw.githubusercontent.com/ClickHouse/ch-bench/HEAD/RESULTS.slow.md>
  - <https://raw.githubusercontent.com/ClickHouse/ch-bench/HEAD/Makefile>
  - <https://raw.githubusercontent.com/ClickHouse/ch-bench/HEAD/ch-bench-cpp/bench.cpp>
  - <https://raw.githubusercontent.com/ClickHouse/ch-bench/HEAD/curl/run.sh>
  - <https://raw.githubusercontent.com/ClickHouse/ch-bench/HEAD/ch-bench-faster/main.go>
  - <https://raw.githubusercontent.com/ClickHouse/ch-bench/HEAD/LICENSE>
  - <https://github.com/ClickHouse/ch-bench>
  - <https://github.com/ClickHouse/ch-bench/commits/main>
  - <https://github.com/ClickHouse/ch-bench/commits/main/RESULTS.md>
  - <https://github.com/ClickHouse/ch-bench/commits/main/README.md>
  - <https://github.com/ClickHouse/ch-bench/tree/main/curl>
  - <https://github.com/ClickHouse/clickhouse-cpp>
  - <https://github.com/ClickHouse/clickhouse-cpp/commits>
  - <https://raw.githubusercontent.com/ClickHouse/clickhouse-cpp/HEAD/bench/bench.cpp>
- **Sources the enricher read:**
  - <https://github.com/ClickHouse/clickhouse-cpp>
  - <https://github.com/ClickHouse/clickhouse-cpp/commits/master>
  - <https://github.com/ClickHouse/clickhouse-cpp/releases>
  - <https://github.com/ClickHouse/clickhouse-cpp/issues?q=is%3Aissue+performance>
  - <https://github.com/ClickHouse/clickhouse-cpp/issues?q=is%3Aissue+is%3Aopen+label%3Abug>
  - <https://github.com/ClickHouse/clickhouse-cpp/issues/442>
  - <https://raw.githubusercontent.com/ClickHouse/clickhouse-cpp/HEAD/README.md>
  - <https://raw.githubusercontent.com/ClickHouse/clickhouse-cpp/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ClickHouse/clickhouse-cpp/HEAD/clickhouse/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ClickHouse/clickhouse-cpp/HEAD/cmake/cpp17.cmake>
  - <https://raw.githubusercontent.com/ClickHouse/clickhouse-cpp/HEAD/clickhouse/client.h>
  - <https://raw.githubusercontent.com/ClickHouse/clickhouse-cpp/HEAD/clickhouse/client.cpp>
  - <https://raw.githubusercontent.com/ClickHouse/clickhouse-cpp/HEAD/clickhouse/columns/numeric.cpp>
  - <https://raw.githubusercontent.com/ClickHouse/clickhouse-cpp/HEAD/clickhouse/base/compressed.cpp>
  - <https://raw.githubusercontent.com/ClickHouse/clickhouse-cpp/HEAD/clickhouse/base/socket.cpp>
  - <https://raw.githubusercontent.com/ClickHouse/clickhouse-cpp/HEAD/clickhouse/base/wire_format.h>
  - <https://raw.githubusercontent.com/ClickHouse/clickhouse-cpp/HEAD/clickhouse/base/wire_format.cpp>
  - <https://raw.githubusercontent.com/ClickHouse/clickhouse-cpp/HEAD/clickhouse/base/platform.h>
  - <https://raw.githubusercontent.com/ClickHouse/clickhouse-cpp/HEAD/clickhouse/base/buffer.h>
  - <https://raw.githubusercontent.com/ClickHouse/clickhouse-cpp/HEAD/clickhouse/base/input.cpp>
  - <https://raw.githubusercontent.com/ClickHouse/clickhouse-cpp/HEAD/bench/bench.cpp>
  - <https://raw.githubusercontent.com/ClickHouse/ch-bench/HEAD/README.md>
  - <https://raw.githubusercontent.com/ClickHouse/ch-bench/HEAD/RESULTS.md>
  - <https://raw.githubusercontent.com/ClickHouse/ch-bench/HEAD/Makefile>
  - <https://raw.githubusercontent.com/ClickHouse/ch-bench/HEAD/ch-bench-cpp/bench.cpp>
  - <https://raw.githubusercontent.com/ClickHouse/ch-bench/HEAD/curl/run.sh>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/clickhouse/clickhouse-cpp`) · [data/wave6/enrich/raw/github_com_clickhouse_clickhouse_cpp.json](../../../data/wave6/enrich/raw/github_com_clickhouse_clickhouse_cpp.json) (enrichment confidence 0.75)

</details>
