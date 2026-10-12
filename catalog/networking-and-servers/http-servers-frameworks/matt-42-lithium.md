# Lithium (HTTP server / web framework)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP servers and frameworks](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only C++ HTTP server and async SQL toolkit on fibers; beat actix-web on TechEmpower DB tests only in Round 20.

| | |
|---|---|
| **Beats** | actix-web (best TechEmpower actix implementation in Round 20, actix-core; also actix-pg). H2O is a secondary comparison from the author's own statement. |
| **Claimed result** | TechEmpower Round 20, the official run on Citrine physical hardware, completed 2021-01-04. Best responses/sec per test comes from the results JSON (derived from page data). lithium-postgres-batch vs actix-core: single query 833,811 vs 635,092 (1.31x); 20 queries 59,452 vs 34,956 (1.70x); updates at 20 queries 34,888 vs 24,301 (1.44x); Fortunes 618,610 vs 653,529 (0.95x, slower). JSON is 1,599,157 (lithium-postgres-beta) vs 1,563,587 (actix-raw), 1.02x. Plaintext is about 7.00M for both (network-bound tie). lithium-postgres-batch had the top single-query result of all implementations and was second in 20-query and updates. The earlier HN post (2020-08-29) only says in its title that Lithium 'ranked the highest performance web application platform' in a continuous run's composite view; it gives no rps numbers. On HN the author said non-batched Lithium is 'as fast (slighly faster on some tests, slighly slower on others)' as H2O. One commenter wrote '2x faster than the Actix Rust framework', which is unverified. |
| **Workload** | TechEmpower Framework Benchmarks (TFB) composite-score suite: JSON serialization, plaintext, single/multi-row DB queries, Fortunes template rendering, and DB updates, using non-blocking HTTP I/O and pipelined/batched PostgreSQL queries. |
| **Metric** | throughput |
| **Hardware** | TechEmpower Citrine (rounds 16-22): three Dell R440 servers (application, database, load generator), each with an Intel Xeon Gold 5120 CPU, 32 GB RAM and an enterprise SSD, on a dedicated Cisco 10-gigabit Ethernet switch. The August 2020 continuous run 57b25c85 also ran on Citrine. |
| **Compiler and flags** | TechEmpower Round-20-era build (FrameworkBenchmarks commit 68c13b5c, 2020-11-11): lithium-postgres-batch.dockerfile uses buildpack-deps:focal and apt clang (LLVM 10, called as llvm-profdata-10). compile-batch.sh builds lithium_batch.cc with clang++ -O3 -march=native -flto -std=c++17 -DNDEBUG -DN_SQL_CONNECTIONS=1 and two-pass PGO (-fprofile-instr-generate, then -fprofile-instr-use). It links a patched libpq (compile_libpq.sh batchmode), and the Lithium single headers are pinned at commit 10b72ad8. Baseline actix-core: FROM rust:1.44, RUSTFLAGS="-C target-cpu=native" cargo build --release. |
| **Adoption** | 1.4k stars |
| **Last commit** | 2026-07-31 |
| **Links** | [repository](https://github.com/matt-42/lithium) · [benchmark](https://www.techempower.com/benchmarks/results/round20/ph.json) |

## Verdict

TechEmpower Round 20 ran on Citrine: three Xeon Gold 5120 servers on 10 GbE. There lithium-postgres-batch (clang/LLVM 10, -O3 -march=native -flto, PGO, patched libpq) beat actix-core (Rust 1.44, target-cpu=native) by 1.31x on single query, about 1.7x on 20 queries and 1.44x on 20-query updates; Fortunes was a tie (0.95x-1.01x, depending on the time base) and JSON/plaintext were about equal. This is a historical result: the batch variant was withdrawn in 2022, and in Rounds 21-22 non-batched Lithium trails actix-http on every DB test.

## Use it when

- Linux HTTP/1.1 service where you want top-tier plaintext/JSON throughput from a small C++ code base you can vendor as one header (Round 20: about 7.0M plaintext and 1.6M JSON req/s, network-bound).
- Handlers that run simple PostgreSQL or MySQL queries, where you want async DB I/O written as straight-line code on fibers instead of callbacks or C++20 coroutines.
- Prototyping JSON REST APIs in C++ with compile-time, symbol-based JSON binding, sessions and a small ORM, if a one-maintainer project is acceptable.
- Studying HTTP and DB pipelining in C++: the TechEmpower code and the libpq batch experiments are public and short.

## Skip it when

- When DB-bound throughput against actix-web decides: in TechEmpower Rounds 21-22 Lithium reaches 0.66x-0.91x of actix-http on single query, 20 queries, Fortunes and updates, and it is below H2O on all DB tests in Rounds 22-23.
- Internet-facing services that need a hardened parser: a high-severity JSON stack-exhaustion DoS (GHSA-cv26-62rq-922g) was fixed only on 2026-04-21, more security fixes landed 2026-07-31, and a HashDoS report on hashmap_http_session (#138) is open.
- Workloads with one request per connection: open issue #122 (2022, no reply) reports slow responses and low CPU use once clients stop reusing keep-alive connections.
- Windows (README: not supported; only unsupported wepoll code paths exist), and PostgreSQL on macOS, where connection setup falls back to a blocking PQconnectdb on the reactor thread.
- Need for HTTP/2, HTTP/3 or WebSocket: there is no code or documentation for them in the repository.

## How it is fast

Each worker thread runs its own edge-triggered epoll reactor (kqueue on macOS) on one shared listening socket. Every connection is a boost::context continuation (stackful coroutine), so handlers read like blocking code while socket and libpq I/O yield to the reactor. Responses collect in a 50 KB output buffer that is flushed only when the input buffer is empty, so HTTP/1.1-pipelined responses leave in one send; a helper thread rebuilds the Date header once per second. PostgreSQL uses non-blocking libpq with a per-connection prepared-statement cache. The Round 20 winner also pipelined queries from many requests over one connection per thread, using the pre-release libpq batch patch (v22) and clang -O3 -march=native -flto with two-pass PGO.

## Compared with alternatives

Pick Lithium over Drogon or Crow when you want a single-header framework with synchronous-looking fiber handlers and compile-time JSON/ORM binding, and can accept a one-maintainer project. For DB-heavy work, current TechEmpower data puts H2O and actix-web ahead of it.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | Boost.Context and Boost.LexicalCast, OpenSSL; libpq for PostgreSQL, MariaDB client for MySQL, SQLite3, libcurl for the HTTP client; optional li_symbol_generator tool to declare s:: symbols |
| **Minimum toolchain** | C++17 (TechEmpower builds use -std=c++17; the repo's CMake now sets C++20); documented compilers G++ 9.2, Clang++ 9.0, Apple clang 12 |
| **Platforms** | Linux (epoll, primary target), macOS (kqueue); Windows not supported per README |
| **Thread safety** | One reactor per thread, each with its own fibers; handlers on different threads run concurrently, so shared state captured by handler lambdas needs your own locking. SQL connection pools are documented as thread-safe; async pools are per thread (max_async_connections_per_thread). |
| **Drop-in for the baseline** | no |

## Gotchas

- The docs name the thread-count option s::threads, but http_serve reads s::nthreads, so the documented option has no effect and the server uses hardware_concurrency threads.
- Fibers are cooperative: a blocking call in a handler (file read, synchronous DB connection, sleep) stalls every connection on that reactor thread.
- You must declare symbols (by hand or with li_symbol_generator), and programs with several translation units need #define LI_EXTERN_GLOBALS in all but one file to avoid duplicate SQL globals.
- The README and docs still claim '#1 on TechEmpower (composite score)'. That rests on the pipelined batch variant, which the author himself removed from TechEmpower in May 2022 to comply with the benchmark rules.

## Known shortcomings

- Historical result: the Round 20 win over actix-core (1.31-1.70x on single/multi-query and updates) came from the pipelined/batch database variant, which TechEmpower removed on 2022-05-31 (PR #7382) to comply with benchmark rules. It loses Fortunes (0.95x) and ties JSON/plaintext even in Round 20. Against actix-http it is slower on all database tests in Round 21 (0.66-0.75x) and Round 22 (0.80-0.91x), and below H2O in Rounds 22-23. The August 2020 continuous run behind the original claim is not archived.
- Correction: libpq pipeline mode did merge into PostgreSQL 14 (2021), co-credited to Lithium's author; the TechEmpower batch build used a pre-release patch and current Lithium master has no pipeline/batch code. The author removed the batch variant himself (PR #7382) to comply with rules that now require a Sync between pipelined queries; lithium_batch.cc pipelined many HTTP requests' queries on one PG connection per thread. Round 20 ratios depend on the time base (16 s vs 15 s windows): Fortunes is a tie at 0.95-1.01x, 20 queries 1.70-1.81x. Security: high-severity JSON stack-exhaustion DoS (GHSA-cv26-62rq-922g, fixed 2026-04-21), more fixes 2026-07-31, open HashDoS in hashmap_http_session (#138). Docs say s::threads but code reads s::nthreads. Blocking PQconnectdb on macOS/Windows; Windows unsupported; no HTTP/2 or WebSocket; no tagged releases; poor one-request-per-connection throughput (#122, unanswered); README still claims '#1 on TechEmpower'.

## Caveats and trade-offs

The Round 20 win depends on the libpq pipelining/batch variant (lithium-postgres-batch). On 2022-05-31 TechEmpower removed these tests (PR #7382) 'to comply with the benchmark rules'. In later official data Lithium is slower than actix on database tests. Round 21 vs actix-http: single query 377,722 vs 512,831 (0.74x); 20 queries 0.66x; Fortunes 0.75x; updates 0.73x. Round 22: 0.82x, 0.80x, 0.86x and 0.91x on the same tests (derived from page data). In Rounds 22-23 Lithium is also below H2O on all database tests. It is only equal to or slightly above actix on JSON and plaintext. Brian from TechEmpower cautioned on HN that the August 2020 continuous run (57b25c85, TFB commit 4a00589b) had not received official-round sanity checking and 'should be taken with a grain of salt'. That run's results data is not archived: tfb-status.techempower.com is unreachable, and Wayback holds only the status page, not results.json. The HN thread's remark about actix is from commenter The_rationalist, not the author, and says the opposite of the earlier record: actix-web DID benefit from query pipelining because tokio-postgres is its own implementation and does not use libpq. The README still says Lithium is 'ranked #1 on the TechEmpower benchmark (composite score)'; this is out of date. TechEmpower/FrameworkBenchmarks was archived on 2026-03-24. Linux-only (epoll).

Async/pipelined Postgres query batching depends on a non-upstream patched fork of libpq (dating to a 2016 patch that was never merged upstream), a dependency risk the author himself flagged and which is shared with drogon; Linux/macOS only (no Windows support); framework is effectively superseded/merged from the author's earlier 'silicon' project.

## Maintenance

Active (security and vcpkg fixes through 2026-07-31), MIT-licensed and header-only, so it is easy to vendor; it has one main maintainer and no tagged releases.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now A.
- **Tier reason:** Upgraded from B. The HN page has no numbers, so benchmark_url now points to the official TechEmpower Round 20 physical-environment results JSON. That file has per-test totals for lithium-postgres-batch, actix-core and actix-pg, all run on Citrine hardware (Intel Xeon Gold 5120). The benchmark code is public in TechEmpower/FrameworkBenchmarks: frameworks/C++/lithium/lithium_batch.cc and compile-batch.sh, plus frameworks/Rust/actix/actix-core.dockerfile. At Round-20-era commit 68c13b5c, the build files state clang from buildpack-deps:focal (LLVM 10, called as llvm-profdata-10) with -O3 -march=native -flto -std=c++17 plus two-pass PGO. The actix build states rust:1.44 with RUSTFLAGS="-C target-cpu=native" cargo build --release.
- **Verifier notes:** Metadata confirmed via gh GraphQL, because REST returned a 403 rate limit: MIT license, not a fork, not archived, 1,409 stars, last commit 2026-07-31 (active). Round 20 per-test numbers are best rps per implementation computed from the rawData totalRequests over the 15 s runs. The composite score could not be recomputed because TechEmpower sets per-round weights that are not published in the JSON. The entry is a real, notable win against actix-web, but only in 2020 to early 2021, with the pipelined database variant, and it did not last. Consider tagging it as a historical result.
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `compared_against_cpp_std_directly`, `caveats`
- **Pages the verifier opened:**
  - <https://news.ycombinator.com/item?id=24315285>
  - <https://hn.algolia.com/api/v1/items/24315285>
  - <https://github.com/matt-42/lithium>
  - <https://raw.githubusercontent.com/matt-42/lithium/master/README.md>
  - <https://www.techempower.com/benchmarks/>
  - <https://www.techempower.com/benchmarks/assets/index-rdjV3uRt.js>
  - <https://www.techempower.com/benchmarks/results/round20/ph.json>
  - <https://www.techempower.com/benchmarks/results/round21/ph.json>
  - <https://www.techempower.com/benchmarks/results/round22/ph.json>
  - <https://www.techempower.com/benchmarks/results/round23/ph.json>
  - <https://www.techempower.com/blog/2021/02/08/framework-benchmarks-round-20/>
  - <https://www.techempower.com/blog/2020/05/28/framework-benchmarks-round-19/>
  - <http://web.archive.org/web/20200829162026/https://tfb-status.techempower.com/results/57b25c85-082a-4013-b572-b0939006eaff>
  - <https://github.com/TechEmpower/FrameworkBenchmarks>
  - <https://github.com/TechEmpower/FrameworkBenchmarks/pull/7382>
  - <https://github.com/TechEmpower/FrameworkBenchmarks/wiki/Project-Information-Composite-Scores>
  - <https://raw.githubusercontent.com/wiki/TechEmpower/FrameworkBenchmarks/Composite-Scoring-for-Frameworks.md>
  - https://raw.githubusercontent.com/wiki/TechEmpower/FrameworkBenchmarks/TechEmpower-Performance-Rating-(TPR).md
  - <https://raw.githubusercontent.com/TechEmpower/FrameworkBenchmarks/master/frameworks/C%2B%2B/lithium/compile.sh>
  - <https://raw.githubusercontent.com/TechEmpower/FrameworkBenchmarks/master/frameworks/C%2B%2B/lithium/compile-batch.sh>
  - <https://raw.githubusercontent.com/TechEmpower/FrameworkBenchmarks/master/frameworks/C%2B%2B/lithium/lithium.dockerfile>
  - <https://raw.githubusercontent.com/TechEmpower/FrameworkBenchmarks/master/frameworks/C%2B%2B/lithium/lithium-postgres-batch.dockerfile>
  - <https://raw.githubusercontent.com/TechEmpower/FrameworkBenchmarks/68c13b5c94494b95388e05178c3dab2e19a352c2/frameworks/C%2B%2B/lithium/compile-batch.sh>
  - <https://raw.githubusercontent.com/TechEmpower/FrameworkBenchmarks/68c13b5c94494b95388e05178c3dab2e19a352c2/frameworks/C%2B%2B/lithium/lithium-postgres-batch.dockerfile>
  - <https://raw.githubusercontent.com/TechEmpower/FrameworkBenchmarks/68c13b5c94494b95388e05178c3dab2e19a352c2/frameworks/Rust/actix/actix-core.dockerfile>
- **Sources the enricher read:**
  - <https://github.com/matt-42/lithium>
  - <https://raw.githubusercontent.com/matt-42/lithium/master/README.md>
  - <https://github.com/matt-42/lithium/blob/master/INSTALL.md>
  - <https://github.com/matt-42/lithium/blob/master/SECURITY.md>
  - <https://github.com/matt-42/lithium/blob/master/vcpkg.json>
  - <https://github.com/matt-42/lithium/blob/master/CMakeLists.txt>
  - <https://github.com/matt-42/lithium/blob/master/libraries/http_server/README.md>
  - <https://github.com/matt-42/lithium/blob/master/libraries/sql/README.md>
  - <https://github.com/matt-42/lithium/blob/master/libraries/http_server/http_server/tcp_server.hh>
  - <https://github.com/matt-42/lithium/blob/master/libraries/http_server/http_server/http_serve.hh>
  - <https://github.com/matt-42/lithium/blob/master/libraries/http_server/http_server/http_ctx.hh>
  - <https://github.com/matt-42/lithium/blob/master/libraries/http_server/http_server/output_buffer.hh>
  - <https://github.com/matt-42/lithium/blob/master/libraries/http_server/http_server/input_buffer.hh>
  - <https://github.com/matt-42/lithium/blob/master/libraries/sql/sql/pgsql_connection.hh>
  - <https://github.com/matt-42/lithium/blob/master/libraries/sql/sql/pgsql_database.hh>
  - <https://github.com/matt-42/lithium/blob/master/libraries/sql/sql/pgsql_result.hpp>
  - <https://github.com/matt-42/lithium/blob/master/libraries/sql/sql/pgsql_statement.hpp>
  - <https://github.com/matt-42/lithium/blob/master/libraries/sql/sql/mysql_async_wrapper.hh>
  - <https://github.com/matt-42/lithium/blob/master/docs/introduction.md>
  - <https://github.com/matt-42/lithium/blob/master/docs/http_server.cc>
  - <https://github.com/matt-42/lithium/blob/master/docs/sql.cc>
  - <https://github.com/matt-42/lithium/commits/master>
  - <https://github.com/matt-42/lithium/security/advisories/GHSA-cv26-62rq-922g>
  - <https://github.com/matt-42/lithium/issues>
  - <https://github.com/matt-42/lithium/issues/72>
  - <https://github.com/matt-42/lithium/issues/109>
  - <https://github.com/matt-42/lithium/issues/122>
  - <https://github.com/matt-42/lithium/issues/123>
  - <https://github.com/matt-42/lithium/issues/134>
  - <https://github.com/matt-42/lithium/issues/138>
  - <https://github.com/matt-42/lithium/pull/133>
  - <https://github.com/matt-42>
  - <https://www.techempower.com/benchmarks/results/round20/ph.json>
  - <https://raw.githubusercontent.com/TechEmpower/FrameworkBenchmarks/68c13b5c94494b95388e05178c3dab2e19a352c2/frameworks/C%2B%2B/lithium/lithium_batch.cc>
  - <https://raw.githubusercontent.com/TechEmpower/FrameworkBenchmarks/68c13b5c94494b95388e05178c3dab2e19a352c2/frameworks/C%2B%2B/lithium/compile_libpq.sh>
  - <https://raw.githubusercontent.com/TechEmpower/FrameworkBenchmarks/68c13b5c94494b95388e05178c3dab2e19a352c2/frameworks/C%2B%2B/lithium/benchmark_config.json>
  - <https://raw.githubusercontent.com/TechEmpower/FrameworkBenchmarks/68c13b5c94494b95388e05178c3dab2e19a352c2/frameworks/C%2B%2B/lithium/lithium-postgres-batch.dockerfile>
  - <https://raw.githubusercontent.com/TechEmpower/FrameworkBenchmarks/master/frameworks/C%2B%2B/lithium/benchmark_config.json>
  - <https://raw.githubusercontent.com/TechEmpower/FrameworkBenchmarks/master/frameworks/C%2B%2B/lithium/lithium-postgres.dockerfile>
  - <https://raw.githubusercontent.com/TechEmpower/FrameworkBenchmarks/master/frameworks/C%2B%2B/lithium/compile.sh>
  - <https://github.com/TechEmpower/FrameworkBenchmarks/pull/7382>
  - <https://raw.githubusercontent.com/wiki/TechEmpower/FrameworkBenchmarks/Project-Information-Framework-Tests-Overview.md>
  - <https://www.postgresql.org/docs/release/14.0/>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/matt-42/lithium`) · [data/wave5/enrich/raw/github_com_matt_42_lithium.json](../../../data/wave5/enrich/raw/github_com_matt_42_lithium.json) (enrichment confidence 0.75)

</details>
