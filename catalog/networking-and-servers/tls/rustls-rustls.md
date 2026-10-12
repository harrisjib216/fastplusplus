# rustls

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [TLS](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `Apache-2.0 OR MIT OR ISC` · 🟢 active

> Memory-safe Rust TLS 1.2/1.3 library on AWS-LC crypto; beats OpenSSL 3.6.1 per core on handshakes, resumption and AES-GCM bulk.

| | |
|---|---|
| **Beats** | OpenSSL |
| **Claimed result** | 2026-03-07 report, rustls 0.23.37 vs OpenSSL 3.6.1: rustls is faster on every reported row. Full handshakes 1.32x-2.59x, e.g. TLS 1.2 RSA client 8,122.99 vs 3,186.87/s (2.55x), TLS 1.2 RSA server 2,835.45 vs 2,154.41/s (1.32x), TLS 1.2 ECDSA server 13,524.99 vs 5,226.96/s (2.59x), TLS 1.3 RSA server 2,357.36 vs 1,712.64/s (1.38x). Resumed handshakes 1.87x-3.20x (TLS 1.2 server 72,480.52 vs 22,647.1/s). Bulk transfer 1.11x-1.27x (TLS 1.2 AES-128-GCM receive 7,946.96 vs 7,129.43 MB/s; TLS 1.3 AES-256-GCM send 7,421.02 vs 5,844.35 MB/s). Ratios derived from page data. The older 2023 run (rustls 0.22.0 vs OpenSSL 3.2.0) was mixed: client full handshakes 1.93x (TLS 1.2, 4,991.73 vs 2,581.16/s) and 2.06x (TLS 1.3), resumed handshakes 1.56x-3.30x, but server full RSA handshakes 0.70x/0.73x, receive throughput 0.83x-0.93x, ChaCha20-Poly1305 0.56x-0.58x; peak memory 131,816 KiB vs 688,436 KiB for 10,000 TLS 1.3 sessions (-81%). |
| **Workload** | Single-core in-process TLS benchmark, rustls 0.23.37 (aws-lc-rs 1.16.0 provider) vs OpenSSL 3.6.1 and BoringSSL 30cd935: bulk transfer (TLS 1.2 AES-128-GCM, TLS 1.3 AES-256-GCM) send/receive MB/s, full handshakes (RSA and ECDSA, TLS 1.2/1.3, client and server) and resumed handshakes per second. Earlier 2023 run (aochagavia/rustls-bench-results, rustls 0.22.0 vs OpenSSL 3.2.0) adds ChaCha20 throughput and per-session memory. |
| **Metric** | throughput |
| **Hardware** | Intel Xeon E-2386G (AVX-512), 32GB, Debian 12 (Bookworm), bare metal, hyper-threading and dynamic frequency scaling disabled, performance governor |
| **Compiler and flags** | 2026 report: GCC 12.2.0 and Clang 14.0.6, Rust 1.94.0. OpenSSL 3.6.1 built with default './Configure ; make -j12'; BoringSSL with 'CC=clang CXX=clang++ cmake -DCMAKE_BUILD_TYPE=Release'; rustls-bench run from target/release via admin/bench-measure.mk; openssl-bench harness 82b86b22 built from its makefile. 2023 run: same C/C++ toolchains, rustls built with 'cargo build -p rustls --release --example bench' (aws_lc_rs feature), jemalloc, openssl-bench harness CXXFLAGS -O2. |
| **Adoption** | 7.6k stars; used in curl, AWS, Cloudflare and other production TLS stacks |
| **Last commit** | 2026-09-24 |
| **Links** | [repository](https://github.com/rustls/rustls) · [benchmark](https://rustls.dev/perf/2026-03-07-report/) |

## Verdict

The rustls maintainers ran single-threaded, in-memory client/server benchmarks on 2026-03-07. The machine was a bare-metal Xeon E-2386G (AVX-512, HT and frequency scaling off) on Debian 12. They compared rustls 0.23.37 with aws-lc-rs 1.16.0 (Rust 1.94.0) against OpenSSL 3.6.1 (default ./Configure; make, GCC 12.2 toolchain) driven by ctz/openssl-bench 82b86b22. rustls led on all 16 rows: AES-GCM bulk 1.11-1.27x, full handshakes 1.32-2.59x, resumptions 1.87-3.20x. The December 2023 run (0.22.0 vs 3.2.0) was mixed: rustls lost server RSA full handshakes (0.70-0.73x), receive throughput (0.83-0.93x) and ChaCha20 (0.56-0.58x), but used about 81% less memory at 10,000 sessions.

## Use it when

- Rust services that open or accept many TLS connections: per core on x86, full handshakes are 1.32-2.59x and resumptions 1.87-3.20x faster than OpenSSL 3.6.1
- Many-core servers (80-core Ampere Altra tested): full TLS 1.3 handshakes and ticket resumption scale per thread with the tightest latency distribution of rustls, BoringSSL and OpenSSL 3.0/3.4. Use 0.23.17 or later
- Servers that hold many concurrent sessions: 10,000 TLS 1.3 sessions peaked at 131,816 KiB against OpenSSL's 688,436 KiB (2023 run)
- AES-GCM bulk transfer on AVX-512 x86 with the aws-lc-rs provider: 1.11-1.27x of OpenSSL 3.6.1 send/receive MB/s
- ARM64 handshake-heavy loads: on an Ampere Altra, rustls 0.23.15 did 1.9-3.5x the full and resumed handshakes of OpenSSL 3.3.2

## Skip it when

- ChaCha20-Poly1305 bulk traffic: in the 2023 run rustls reached only 0.56-0.58x of OpenSSL 3.2.0 on AVX-512, because AWS-LC lacked OpenSSL's AVX-512 ChaCha path. The 2026 report drops the ChaCha row, although admin/bench-measure.mk still runs it
- Bulk-throughput-bound ARM64 servers: on Ampere Altra (2024), rustls moved 0.93-1.04x of OpenSSL 3.3.2's MB/s. On x86, BoringSSL still sends faster (8,291.9 vs 8,133.85 MB/s, TLS 1.2 AES-128-GCM)
- C/C++ code that needs an OpenSSL drop-in: rustls-libssl is experimental, covers only the libssl subset used by curl and nginx, and still needs OpenSSL's libcrypto. rustls-ffi has its own C API, gives no ABI-stability guarantee and recommends static linking
- Protocols or features it refuses or lacks: TLS 1.0/1.1, SSLv3, renegotiation, finite-field DHE, custom extensions (SSL_CTX_add_custom_ext), DTLS (issue #40 open), server-side ECH, and deferred or async private-key operations (roadmap item #850)
- High-churn servers with session-ID resumption on the default cache: ServerSessionMemoryCache is a Mutex around a HashMap and VecDeque. One quinn server spent 11% of accept-thread time in take() (#2972). The maintainers expect demanding users to supply their own store

## How it is fast

Primitive speed comes from AWS-LC through aws-lc-rs: its AVX-512F/VAES AES-GCM and AVX-512IFMA RSA (both contributed by Intel) explain the x86 bulk and server-RSA results. On ARM64, BoringSSL, AWS-LC and OpenSSL all run AES-256-GCM at 2264-2268 MB/s, so the lead over OpenSSL comes from the protocol layer. That layer is a sans-I/O design over caller buffers with a write-through "unbuffered" API, about 13 KiB per session against OpenSSL's 69 KiB. Tuning includes removing a receive-path memmove (PR #2155), packing several handshake messages into one record (#2041) and a cheaper extension representation (0.23.31). For many cores, configs are shared read-only in an Arc, and ticket-key rotation switched from a Mutex to a RwLock (TicketRotator, PR #2193, 0.23.17), which removes the lock contention the maintainers measured in OpenSSL 3.0/3.4. The reports do not name the component behind the handshake lead.

## Compared with alternatives

aws-lc-rs, ring and Graviola are crypto providers that plug into rustls, so they are not alternatives to it; aws-lc-rs is the default and the one benchmarked. Pick rustls over AWS-LC, wolfSSL, Fizz or picotls when you want a memory-safe TLS 1.2+1.3 stack in Rust (or through rustls-ffi) with top per-core handshake numbers. Pick those C/C++ libraries when you need an OpenSSL-style C API, and pick ztls only for Zig TLS 1.3 code that is bound by per-record latency.

## Integration

| | |
|---|---|
| **Form** | crate (Rust); C static or shared library via rustls-ffi; experimental libssl.so.3 shim via rustls-libssl |
| **Dependencies** | rustls itself: subtle, zeroize, rustls-pki-types, optional tracing and rustls-webpki (default) and optional brotli or zlib-rs for certificate compression. A crypto provider crate is required: rustls-aws-lc-rs (needs a C/C++ compiler to build aws-lc-sys, plus CMake and Go for FIPS) or rustls-ring. The benchmark binary also links tikv-jemallocator |
| **Minimum toolchain** | Stable 0.23.x: Rust 1.71 (rust-version on crates.io). 0.24.0-dev on main: Rust 1.85, edition 2024. Add a C/C++ compiler for the aws-lc-rs provider; rustls-ffi needs Rust 1.73+ and cargo-c |
| **Platforms** | The rustls core is platform-independent and no_std-capable. Real reach depends on the provider: aws-lc-rs runs on targets that both AWS-LC and Rust std support, and ring builds on more targets. Published benchmarks cover x86-64 (Xeon E-2386G, AVX-512) and aarch64 (Ampere Altra) |
| **Thread safety** | ClientConfig and ServerConfig are Send + Sync and meant to be shared in an Arc, one per process. ServerConnection is Send + Sync (docs.rs auto traits), but its methods take &mut self, so one thread drives a connection at a time |
| **Drop-in for the baseline** | partial — not for Rust or C code written against the OpenSSL API, which needs rewriting to the rustls or rustls-ffi API. rustls-libssl can stand in for libssl.so.3 under curl and nginx on some Ubuntu and Fedora releases, but it is experimental and keeps OpenSSL's libcrypto |

## Gotchas

- The published numbers come from a benchmark binary with jemalloc as its global allocator. In the 2023 run, glibc malloc cut rustls+aws-lc send throughput 2.2-2.4x (2,847 vs 6,712 MB/s) because of page faults. Benchmark your own allocator
- The benchmark is in-memory client-to-server with no sockets or syscalls. Since 0.23.31, TLS 1.3 uses X25519MLKEM768 by default, which cut rustls TLS 1.3 RSA client full handshakes 1.62x from 0.23.15 and sends larger messages
- API churn: from 0.24 you must pass a CryptoProvider explicitly, the providers move out into separate crates (rustls-aws-lc-rs, rustls-ring), and main has a new read_tls/MessageHandler I/O API. Stable is still 0.23.x
- Pin 0.23.45 or later. RUSTSEC-2026-0285 affects 0.23.13 through 0.23.44: TLS 1.3 handshake messages were accepted across key changes. The benchmarked 0.23.37 is affected. Earlier advisories: RUSTSEC-2024-0399 (panic in Acceptor::accept on a fragmented ClientHello, 0.23.13-0.23.17) and RUSTSEC-2024-0336 (complete_io infinite loop, before 0.23.5)

## Known shortcomings

- rustls is itself one of the tls category's baselines; this entry documents its standing against OpenSSL only and must not be read as beating rustls. In the 2023 aochagavia run rustls was slower than OpenSSL on server-side full RSA handshakes (0.70x and 0.73x).
- First-party, in-memory benchmark on one AVX-512 Xeon E-2386G (no sockets or syscalls, no memory numbers in 2026). The rustls benchmark binary uses jemalloc while OpenSSL uses the system allocator (glibc malloc cut rustls send throughput 2.2-2.4x in 2023). The 2026 report omits ChaCha20-Poly1305, where rustls reached only 0.56-0.58x of OpenSSL in 2023. On ARM64 (Ampere Altra, 2024) bulk throughput was only 0.93-1.04x; BoringSSL still sends faster on x86. AES-GCM and server-RSA wins come from AWS-LC's AVX-512 code. Which API (buffered or unbuffered) the report used is unstated. The benchmarked 0.23.37 is affected by RUSTSEC-2026-0285 (0.23.13-0.23.44; use 0.23.45+). The default server session cache (Mutex around HashMap) took 11% of accept-thread time under churn (#2972). Not an OpenSSL drop-in: rustls-libssl is experimental and needs libcrypto; rustls-ffi has no ABI guarantee. No DTLS, renegotiation, TLS 1.0/1.1, FFDHE, custom extensions, server-side ECH or async private-key operations; 0.24 breaks the API and raises MSRV to 1.85.

## Caveats and trade-offs

First-party numbers (rustls maintainers' own rustls.dev/perf reports) but fully pinned and reproducible. Single-core, single-machine benchmarks; ChaCha20 is absent from the 2026 table and was 0.56x-0.58x of OpenSSL in the 2023 run (OpenSSL AVX-512 path). rustls uses aws-lc-rs (AWS-LC) as its crypto provider, so primitive speed is largely AWS-LC's. BoringSSL still beats rustls on bulk send in the 2026 table (8,291.9 vs 8,133.85 MB/s TLS 1.2 AES-128-GCM). rustls is itself one of the three named baselines for this category (OpenSSL, BoringSSL, rustls), so this entry records rustls vs OpenSSL, not a project beating rustls. The original record's 2023 figures come from the aochagavia/rustls-bench-results README itself (not a bencher.dev summary), and its '131.8MB vs 688.4MB' is really 131,816 KiB vs 688,436 KiB.

Mixed results depending on cipher/direction: faster handshakes, resumption, and far lower memory use, but slower AES128-GCM receive throughput and notably slower ChaCha20-Poly1305 throughput than OpenSSL on this hardware; numbers are tied to the aws-lc crypto backend chosen for rustls, not rustls's own crypto code.

## Maintenance

Very active: 0.23.45 shipped 2026-09-14 after roughly monthly 0.23.x releases, and 0.24 is in development with breaking API changes. It has about 945M crates.io downloads, a founder funded full-time through Prossimo, and a permissive Apache-2.0/MIT/ISC license.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** Benchmark code is public and pinned: ctz/openssl-bench (82b86b22) for OpenSSL/BoringSSL and rustls admin/bench-measure.mk with the rustls-bench binary (target/release). The 2026-03-07 rustls.dev report states GCC 12.2.0, Clang 14.0.6, Rust 1.94.0, the build commands (OpenSSL ./Configure; make, BoringSSL cmake Release, rustls release build) and the CPU (Xeon E-2386G), so tier A holds; the 2023 aochagavia run also meets A.
- **Verifier notes:** Valid catalog entry: rustls is a measurably faster alternative to OpenSSL, since the current tier-A report shows rustls 0.23.37 ahead of OpenSSL 3.6.1 on all 16 rows (1.11x-3.20x). Tag it as a category baseline so it is never shown as beating rustls. benchmark_url was switched to the newer, stronger 2026-03-07 report; the original 2023 numbers were verified correct except the memory units and the omitted server-side full-handshake loss (0.70x/0.73x).
- **Fields the verifier corrected:** `benchmark_url`, `workload`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/aochagavia/rustls-bench-results>
  - <https://raw.githubusercontent.com/aochagavia/rustls-bench-results/main/README.md>
  - <https://raw.githubusercontent.com/ctz/openssl-bench/7bc3277b062c598463d60e6d821198ec5c7a4763/Makefile>
  - <https://rustls.dev/perf/>
  - <https://rustls.dev/perf/2026-03-07-report/>
  - <https://github.com/rustls/rustls>
  - <https://raw.githubusercontent.com/rustls/rustls/main/LICENSE>
  - <https://raw.githubusercontent.com/rustls/rustls/main/rustls/Cargo.toml>
  - <https://raw.githubusercontent.com/rustls/rustls/main/admin/bench-measure.mk>
- **Sources the enricher read:**
  - <https://github.com/rustls/rustls>
  - <https://raw.githubusercontent.com/rustls/rustls/main/README.md>
  - <https://raw.githubusercontent.com/rustls/rustls/main/Cargo.toml>
  - <https://raw.githubusercontent.com/rustls/rustls/main/rustls/Cargo.toml>
  - <https://raw.githubusercontent.com/rustls/rustls/main/rustls/src/lib.rs>
  - <https://raw.githubusercontent.com/rustls/rustls/main/BENCHMARKING.md>
  - <https://raw.githubusercontent.com/rustls/rustls/main/ROADMAP.md>
  - <https://raw.githubusercontent.com/rustls/rustls/main/SECURITY.md>
  - <https://raw.githubusercontent.com/rustls/rustls/main/admin/bench-measure.mk>
  - <https://raw.githubusercontent.com/rustls/rustls/main/rustls-bench/Cargo.toml>
  - <https://raw.githubusercontent.com/rustls/rustls/main/rustls-bench/src/main.rs>
  - <https://raw.githubusercontent.com/rustls/rustls/v/0.23.37/rustls-bench/Cargo.toml>
  - <https://raw.githubusercontent.com/rustls/rustls/v/0.23.37/rustls-bench/src/main.rs>
  - <https://rustls.dev/perf/>
  - <https://rustls.dev/perf/2026-03-07-report/>
  - <https://rustls.dev/perf/2025-07-31-report/>
  - <https://rustls.dev/perf/2024-12-17-pq-kx/>
  - <https://rustls.dev/perf/2024-11-28-threading/>
  - <https://rustls.dev/perf/2024-10-31-arm64/>
  - <https://rustls.dev/perf/2024-10-18-report/>
  - <https://raw.githubusercontent.com/aochagavia/rustls-bench-results/main/README.md>
  - <https://docs.rs/rustls/latest/rustls/manual/_04_features/index.html>
  - <https://docs.rs/rustls/latest/rustls/server/struct.ServerConnection.html>
  - <https://docs.rs/rustls/latest/rustls/server/struct.ServerConfig.html>
  - <https://crates.io/api/v1/crates/rustls>
  - https://api.osv.dev/v1/query (crates.io/rustls)
  - <https://api.osv.dev/v1/vulns/RUSTSEC-2026-0285>
  - <https://api.osv.dev/v1/vulns/RUSTSEC-2024-0399>
  - <https://raw.githubusercontent.com/rustls/rustls-ffi/main/README.md>
  - <https://raw.githubusercontent.com/rustls/rustls-openssl-compat/main/README.md>
  - <https://aws.github.io/aws-lc-rs/requirements/index.html>
  - <https://aws.github.io/aws-lc-rs/requirements/linux.html>
  - <https://aws.github.io/aws-lc-rs/faq.html>
  - <https://github.com/rustls/rustls/issues/2030>
  - <https://github.com/rustls/rustls/issues/1830>
  - <https://github.com/rustls/rustls/issues/1828>
  - <https://github.com/rustls/rustls/issues/2154>
  - <https://github.com/rustls/rustls/pull/2155>
  - <https://github.com/rustls/rustls/pull/2193>
  - <https://github.com/rustls/rustls/issues/2041>
  - <https://github.com/rustls/rustls/issues/1503>
  - <https://github.com/rustls/rustls/issues/2972>
  - <https://github.com/rustls/rustls/issues/2830>
  - <https://github.com/rustls/rustls/issues/2362>
  - <https://github.com/rustls/rustls/issues/2252>
  - <https://github.com/rustls/rustls/issues/2593>
  - <https://github.com/rustls/rustls/issues/1913>
  - <https://github.com/rustls/rustls/issues/850>
  - <https://github.com/rustls/rustls/issues/40>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/rustls/rustls`) · [data/wave5/enrich/raw/github_com_rustls_rustls.json](../../../data/wave5/enrich/raw/github_com_rustls_rustls.json) (enrichment confidence 0.82)

</details>
