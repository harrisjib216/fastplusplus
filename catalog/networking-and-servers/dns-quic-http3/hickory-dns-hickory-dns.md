# Hickory DNS (formerly Trust-DNS)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [DNS, QUIC and HTTP/3](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟢 active

> Memory-safe Rust DNS server, resolver and protocol crates; matches BIND 9.11 on single-query UDP latency, within noise.

| | |
|---|---|
| **Beats** | BIND |
| **Claimed result** | Single UDP A query for www.example.com: 68,173 ns/iter (+/- 11,699) for TRust-DNS vs 69,576 ns/iter (+/- 3,620) for BIND9 (9.11 per the linked config.log gist), about 2% lower median round-trip time (derived from page data), inside TRust-DNS's reported +/- spread. Starting point was 400us vs 100us; after the bench was fixed to launch a release instead of a debug binary it was 79,274 vs 69,960 ns/iter before the optimizations. |
| **Workload** | Single UDP DNS A-record query for www.example.com against a local authoritative server, round-trip time measured with identical zone config and test client for both servers. |
| **Metric** | latency |
| **Hardware** | Author's 'getting older laptop' on macOS (x86_64; BIND build host Darwin 16.1.0 per config.log gist); no CPU model |
| **Compiler and flags** | TRust-DNS: Rust nightly libtest bench (rustc version not stated), release build. BIND 9.11: default ./configure with Apple LLVM 7.3.0 (clang-703.0.29) as gcc, CFLAGS -g -O2 (from the linked config.log gist) |
| **Adoption** | 5.4k stars |
| **Last commit** | 2026-09-26 |
| **Links** | [repository](https://github.com/hickory-dns/hickory-dns) · [benchmark](https://bluejekyll.github.io/blog/posts/making-trust-dns-fast/) |

## Verdict

In the author's 2017 libtest bench, one client sent serial UDP A queries for www.example.com over loopback to a local authoritative server with the same zone. TRust-DNS took 68,173 ns/iter (+/- 11,699) and BIND 9.11 took 69,576 (+/- 3,620), which is about 2% lower and within TRust-DNS's spread. TRust-DNS was a release build on an unstated nightly rustc. BIND was built with default configure (Apple LLVM 7.3.0, -g -O2), and both ran on an aging x86_64 macOS laptop (Darwin 16.1.0) with no CPU model given.

## Use it when

- A Rust program needs an embedded authoritative DNS server or stub resolver as a library, instead of running and managing a separate BIND process.
- Small to medium authoritative zones served from memory, zone files or SQLite, where latency equal to BIND is enough and memory safety is the main reason to switch.
- In-process encrypted DNS transports (DoT, DoH, DoQ, DoH3) through rustls, using aws-lc-rs or ring as the crypto provider.
- Dynamic update with SIG(0)/TSIG and a SQLite journal, plus online DNSSEC signing (NSEC/NSEC3) that re-signs zones on each update.
- Replacing the OS resolver inside a Rust application with `hickory-resolver`, which also offers no_std support in `hickory-proto`.

## Skip it when

- You expect a speedup over BIND. The only evidence is one 2017 serial-latency microbench at about 2% (inside noise), with no qps or throughput numbers, and TCP, dynamic update and DNSSEC signing were not measured.
- High-QPS production serving. The binary's README says 'running in production is not recommended'. Issue #2613 (open) reports about 50% query loss under dnsperf with 100 clients, and scalability testing (#2643) is still an open TODO.
- Primary/secondary deployments that need IXFR (RFC 1995), NOTIFY (RFC 1996), offline zone signing or `named.conf` compatibility. The README lists all of these as not implemented.
- Validating recursive resolution. The recursor is marked experimental, and most of the 38 advisories fixed in v0.26.2 hit DNSSEC validation, the recursor or the cache.
- Stacks that cannot upgrade quickly. The project is pre-1.0 (main is 0.27.0-alpha.1), crates are regularly split, renamed or removed, and only the latest minor release gets security fixes.

## How it is fast

The 2017 work took allocations and copies off the UDP query hot path. `LowerName` stores names pre-lowercased, so case-insensitive comparison becomes a plain byte compare (the author's microbench fell from 255 to 7 ns for short names). `MessageResponse<'q, 'a>` borrows records from the zone instead of cloning them. The original query bytes are echoed rather than re-serialized, EDNS is streamed straight to the encoder, and the label-compression table was changed from `HashMap<Vec<String>, u16>` to buffer offsets. The server runs on a multi-threaded Tokio runtime (`--workers` defaults to the CPU core count) and spawns one task per UDP request.

## Compared with alternatives

Pick Hickory over Unbound (about 3.4x BIND cache-hit qps) when you need an embeddable Rust library or in-process DoQ/DoH3 rather than a standalone high-throughput C resolver. Pick it over Nail and the Bundy-DNS l1cache branch (about 2.9x and 4.4x BIND throughput claims) when a maintained, published crate matters more than raw qps, because those two are research or experimental code.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | tokio; rustls with aws-lc-rs or ring (crypto features only); optional quinn/h3 (DoQ/DoH3), h2/hyper (DoH), rusqlite with bundled SQLite (default `sqlite` feature in the binary), tikv-jemallocator (optional) |
| **Minimum toolchain** | Rust 1.88 (workspace rust-version; the MSRV is guaranteed only for `--no-default-features` builds). The comparison bench needs nightly (`#![feature(test)]`). |
| **Platforms** | CI runs on Linux, macOS and Windows (latest images). `hickory-proto` supports no_std and has a wasm-bindgen feature. |
| **Thread safety** | Server handlers must be `Send + Sync`. The server runs on a multi-threaded Tokio runtime with one spawned task per request. The in-memory zone store sits behind a `tokio::sync::RwLock`, so updates block readers. |
| **Drop-in for the baseline** | partial — it serves standard RFC 1035 zone files and speaks the same wire protocols, but configuration is TOML rather than named.conf, and IXFR, NOTIFY, offline signing and many BIND operational features are missing |

## Gotchas

- Always benchmark `--release` builds. The first 2017 result (400 us vs 100 us) came from a debug binary, and the #2613 report was built with plain `cargo run`.
- The in-repo `bin/benches/comparison.rs` is nightly-only and its BIND benches are `#[ignore]`d. They need `TDNS_BIND_PATH` pointing at a self-built named, and the named config path still points at the old `server/benches/` layout, so reproducing the BIND comparison probably needs path fixes.
- Use v0.26.3 or later. v0.26.2 (2026-09-03) fixed 38 advisories, including DNSSEC proof forgery, zone-parser panics and DoH/DoQ memory exhaustion, and v0.26.3 fixed regressions it introduced. hickory-proto before 0.26.1 also has an O(n^2) name-compression CPU DoS (GHSA-q2qq-hmj6-3wpp) in the encoder path the 2017 work optimized.
- Crypto features carry a provider suffix (`tls-ring` vs `tls-aws-lc-rs`, `dnssec-ring`, etc.). DNSSEC and encrypted transports are off until you enable one of them.

## Known shortcomings

- Parity, not a win: 68,173 vs 69,576 ns/iter (\~2%) is inside the reported +/-11,699 ns spread. Compared against BIND 9.11 built -g -O2 with Apple LLVM 7.3.0; no CPU or rustc version.
- Its own README says running the server in production is not recommended; an open issue reports \~50% query loss under dnsperf (#2613, possibly a debug build). The in-repo BIND comparison bench is stale (nightly-only, BIND benches ignored). Use &gt;= 0.26.3: 0.26.2 fixed 38 advisories and 0.26.1 fixed an O(n^2) name-compression DoS (GHSA-q2qq-hmj6-3wpp). Not a drop-in for BIND (TOML config; no IXFR, NOTIFY or offline signing; recursor experimental).

## Caveats and trade-offs

Author says 'I'm not being scientific here'. Hardware is only 'my getting older laptop' on macOS, with no CPU model; rustc nightly version not stated. BIND is 9.11 (linked config.log gist, default -g -O2). The \~1.4us win is inside TRust-DNS's +/-11,699 ns spread; the author notes macOS updates during the month cost both servers \~5us, and that BIND9 has more features and TRust-DNS may not be faster for TCP, dynamic update or DNSSEC signing. Post dated 2017-12-29, so it does not reflect current Hickory or BIND. Benchmark code is public: server/benches/comparison_benches.rs (PR #317, merged 2017-12-31); the current repo has bin/benches/comparison.rs.

The final result is closer to parity than a clear win (\~2%); the post itself frames the goal as 'making trust-dns fast [enough]' rather than definitively faster. BIND has far more production features (dynamic reconfiguration, extensive DNSSEC signing, etc.) not exercised in this microbenchmark.

## Maintenance

Actively maintained (pushed 2026-09-26; v0.26.3 released 2026-09-10) under MIT OR Apache-2.0 and published on crates.io. It is still pre-1.0, and its own server README advises against production use.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** Author's own blog post runs a public libtest benchmark (server/benches/comparison_benches.rs, PR #317; now bin/benches/comparison.rs) against BIND 9.11, and the linked config.log gist gives BIND's compiler and flags. No CPU model and no rustc version are stated, so it is not A; first-party, so C.
- **Verifier notes:** Numbers verified verbatim. Record said no BIND version was pinned, but the post links a config.log gist showing BIND 9.11 built with Apple LLVM 7.3.0 at -g -O2; compiler_and_flags, hardware and caveats updated. The 'win' is effectively parity within noise; metadata (MIT OR Apache-2.0 via Cargo.toml, 5,429 stars, last commit 2026-09-26) checks out.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://bluejekyll.github.io/blog/posts/making-trust-dns-fast/>
  - <https://github.com/hickory-dns/hickory-dns>
  - <https://github.com/hickory-dns/hickory-dns/blob/main/Cargo.toml>
  - <https://github.com/bluejekyll/trust-dns/blob/3c8dd8dbc333ab616ec2aef29b23e2805f64b479/server/benches/comparison_benches.rs>
  - <https://github.com/hickory-dns/hickory-dns/pull/317>
  - <https://gist.github.com/bluejekyll/fa890f3144025a5244c462ba7b69b060>
- **Sources the enricher read:**
  - <https://github.com/hickory-dns/hickory-dns>
  - <https://github.com/hickory-dns/hickory-dns/blob/main/README.md>
  - <https://github.com/hickory-dns/hickory-dns/blob/main/Cargo.toml>
  - <https://github.com/hickory-dns/hickory-dns/blob/main/bin/Cargo.toml>
  - <https://github.com/hickory-dns/hickory-dns/blob/main/bin/README.md>
  - <https://github.com/hickory-dns/hickory-dns/blob/main/bin/src/hickory-dns.rs>
  - <https://github.com/hickory-dns/hickory-dns/blob/main/bin/benches/comparison.rs>
  - <https://github.com/hickory-dns/hickory-dns/blob/main/ARCHITECTURE.md>
  - <https://github.com/hickory-dns/hickory-dns/blob/main/SECURITY.md>
  - <https://github.com/hickory-dns/hickory-dns/blob/main/CHANGELOG.md>
  - <https://github.com/hickory-dns/hickory-dns/blob/main/crates/server/README.md>
  - <https://github.com/hickory-dns/hickory-dns/blob/main/crates/server/src/server/mod.rs>
  - <https://github.com/hickory-dns/hickory-dns/blob/main/crates/server/src/zone_handler/message_response.rs>
  - <https://github.com/hickory-dns/hickory-dns/blob/main/crates/server/src/store/in_memory/mod.rs>
  - <https://github.com/hickory-dns/hickory-dns/blob/main/crates/server/src/store/in_memory/inner.rs>
  - <https://github.com/hickory-dns/hickory-dns/blob/main/crates/proto/src/rr/lower_name.rs>
  - <https://github.com/hickory-dns/hickory-dns/blob/main/crates/proto/Cargo.toml>
  - <https://github.com/hickory-dns/hickory-dns/blob/main/.github/workflows/test.yml>
  - <https://github.com/hickory-dns/hickory-dns/security/advisories>
  - <https://github.com/hickory-dns/hickory-dns/security/advisories/GHSA-q2qq-hmj6-3wpp>
  - <https://github.com/hickory-dns/hickory-dns/releases/tag/v0.26.2>
  - <https://github.com/hickory-dns/hickory-dns/releases/tag/v0.26.3>
  - <https://github.com/hickory-dns/hickory-dns/issues/2613>
  - <https://github.com/hickory-dns/hickory-dns/issues/2643>
  - <https://github.com/hickory-dns/hickory-dns/pull/317>
  - <https://bluejekyll.github.io/blog/posts/making-trust-dns-fast/>
  - <https://gist.github.com/bluejekyll/fa890f3144025a5244c462ba7b69b060>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/hickory-dns/hickory-dns`) · [data/wave5/enrich/raw/github_com_hickory_dns_hickory_dns.json](../../../data/wave5/enrich/raw/github_com_hickory_dns_hickory_dns.json) (enrichment confidence 0.75)

</details>
