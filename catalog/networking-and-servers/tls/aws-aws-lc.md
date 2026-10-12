# AWS-LC

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [TLS](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `Apache-2.0 OR ISC for new AWS-LC code; the LICENSE file lists BoringSSL-derived code as ISC/Apache-2.0, OpenSSL-derived code as Apache-2.0, and bundled parts as MIT, BSD-3-Clause and CC0 (GitHub reports NOASSERTION)` · 🟢 active

> BoringSSL-derived, OpenSSL-1.1.1-API-compatible TLS/crypto library from AWS; out-scales OpenSSL 3.x in HAProxy handshakes and resumption.

| | |
|---|---|
| **Beats** | OpenSSL |
| **Claimed result** | HAProxy 3.1-dev1 on a 64-core Graviton4, at 64 threads (bar charts on page). Full TLS handshake (RSA, new conn/s): AWS-LC v1.32.0+30 commits 63.1k (same with or without the C11 build) vs OpenSSL 1.1.1w 48.3k, OpenSSL 3.1.6-3.4.0-dev 42.6-43.2k, OpenSSL 3.0.2/3.0.14 21.2-21.3k (\~1.31x vs 1.1.1w, \~1.46-1.48x vs 3.1+, \~3.0x vs 3.0.x; derived from page data). The older AWS-LC 1.29.0 reached only 45.2k (45.7k with -DCMAKE_C_STANDARD=11), below OpenSSL 1.1.1w, because of a CPU-detection bug. TLS resumption (end-to-end conn/s): AWS-LC 1.29.0 built with -DCMAKE_C_STANDARD=11 186.3k (text: \~183k; v1.32+30-c11 183.7k) with either lock type, vs OpenSSL 1.1.1w 17.8k (pthread locks) / 124.1k (HAProxy locks), OpenSSL 3.1-3.4-dev 23.1-27.9k, OpenSSL 3.0.14 3.7k / 8.1k, OpenSSL 3.0.2 1.6k / 2.3k. The page text says '\~20% higher than WolfSSL and 50% higher than OpenSSL 1.1.1w'. The default C99 AWS-LC builds (1.29.0 and 1.32+30) collapsed to 8.4-8.5k with pthread locks and 38.4k with HAProxy locks. |
| **Workload** | HAProxy 3.1-dev1 (2024-06-26) server-only full TLS handshake (RSA, one HTTP request per new connection, no resumption) and end-to-end TLS session resumption from tickets on both the client and backend sides (10 daisy-chained proxy instances), connections/sec vs thread count up to 64, with pthread rwlocks and with HAProxy's lightweight locks (USE_PTHREAD_EMULATION); the TLS protocol version is not stated |
| **Metric** | throughput |
| **Hardware** | AWS r8g.16xlarge instance, 64 Graviton4 (ARM Neoverse V2) cores |
| **Compiler and flags** | gcc 11.4 (stated on page); AWS-LC's CMake config forced C99 (pthread-rwlock refcounting) unless -DCMAKE_C_STANDARD=11 was set; HAProxy built with and without USE_PTHREAD_EMULATION=1; optimization flags not stated |
| **Adoption** | 835 stars; used internally at AWS (s2n-tls, AWS SDKs, AWS-LC-rs) for TLS/crypto |
| **Last commit** | 2026-09-25 |
| **Links** | [repository](https://github.com/aws/aws-lc) · [benchmark](https://www.haproxy.com/blog/state-of-ssl-stacks) |

## Verdict

HAProxy Technologies ran HAProxy 3.1-dev1 (gcc 11.4) on a 64-core Graviton4 r8g.16xlarge at 64 threads. For full RSA handshakes, AWS-LC v1.32.0 plus 30 commits did 63.1k new conn/s, against 48.3k for OpenSSL 1.1.1w, about 43k for OpenSSL 3.1-3.4-dev and about 21k for 3.0.x. For end-to-end ticket resumption, AWS-LC built as C11 reached about 183-186k conn/s, against 124k for OpenSSL 1.1.1w (with HAProxy's lightweight locks) and at most 28k for OpenSSL 3.x. AWS-LC's default C99 build of the time dropped to about 8.5k conn/s with pthread locks.

## Use it when

- High-connection-rate TLS termination (load balancers, reverse proxies such as HAProxy) stuck on OpenSSL 3.x, where full handshakes or ticket resumption stop scaling past 16-32 threads
- Many-core AWS Graviton or other Neoverse V1/V2 servers: AWS tests ARM optimizations on Graviton, and the published numbers are for Graviton4
- OpenSSL-API codebases that need QUIC via the BoringSSL-style QUIC API without moving to BoringSSL's unstable API
- Deployments that need a FIPS-validated module (FIPS branches) or post-quantum key exchange and signatures in the same library
- Teams that can follow its live-at-head model and rebuild regularly

## Skip it when

- You need to replace the system OpenSSL under prebuilt binaries: AWS-LC is API-compatible but not ABI-compatible, so every consumer must be recompiled
- You depend on OpenSSL features it lacks: security levels (@SECLEVEL is parsed and ignored), TLS compression, DANE, FFDH/DHE and CCM cipher suites, server-side renegotiation, ENGINEs, or stateful session resumption on TLS 1.3
- You need a long-term-support branch: there is no general LTS, releases ship every 1-3 weeks, and only the FIPS branches have long support
- Short-lived processes or fast-startup CLIs: in open issue #3180, jitterentropy seeding raised per-process startup from about 0.4 ms (v1.39) to about 36 ms (v1.71); the workaround is -DDISABLE_CPU_JITTER_ENTROPY=ON
- Throughput-critical single primitives on some x86 CPUs: open issues report AES-GCM slower than BoringSSL on Zen3 (#2283) and SHA-2 slower than OpenSSL on Haswell and Zen3 (#3531, not reproduced by the maintainers)

## How it is fast

For resumption scaling, shared objects are reference-counted with lock-free C11 atomic compare-and-swap (crypto/refcount_c11.c), and since PR #2786 (v1.64.0) the ticket session-hit counters use C++11 atomics. The resumption fast path therefore takes no locks. HAProxy's profiles of OpenSSL 3.x showed contention from locks and heavy atomic use. Full RSA handshakes are bound by Montgomery multiplication, and AWS-LC picks a kernel per microarchitecture at runtime. Cores it flags as having wide multipliers (Neoverse V1/V2/V3, Apple M) get the armv8 bn_mul_mont assembly and 8x-unrolled AES-GCM; narrow-multiplier NEON cores get s2n-bignum's formally verified Karatsuba multiply with bignum_emontredc_8n reduction. HAProxy's Graviton4 gain came from adding Neoverse V2 detection, which took RSA-2048 signing on Graviton4 from 930 to 1,398 ops/s (per the commit's own numbers).

## Compared with alternatives

Pick it over wolfSSL when you want the fastest many-core result and an OpenSSL-1.1.1-style API to port to. In HAProxy's Graviton4 test, AWS-LC was about 6% ahead on full handshakes (63.1k vs 59.7k conn/s) and about 20% ahead on resumption once built as C11. wolfSSL was fast without any build tuning and offers support contracts. Pick it over Tempesta FW whenever you need a userspace library to link: Tempesta's TLS runs inside a Linux-kernel web accelerator and cannot be dropped into an application.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (CMake; separate libcrypto and libssl), with checked-in pre-generated sources for other build systems |
| **Dependencies** | Runtime: none beyond libc/pthreads. Build: CMake (CMakeLists requires 3.5+; BUILDING.md still says 3.0), Perl and Go 1.20+ unless you use the pre-generated sources, NASM on Windows |
| **Minimum toolchain** | C compiler with C11 atomics (a C99 fallback exists but uses rwlock refcounting) and a C++11 compiler for libssl; GCC 4.1.3+, Clang, MSVC 2015+; CMake warns against GCC versions affected by GCC bug 95189 |
| **Platforms** | CI-tested on Linux x86-64/aarch64/ppc/ppc64/ppc64le, macOS x86-64/aarch64, Windows x86-64, Android and iOS aarch64; best-effort on FreeBSD/OpenBSD/NetBSD, Linux arm32/x86/risc-v64/s390x/loongarch64, Windows aarch64, and experimental wasm32; assembly fast paths for x86-64 and aarch64 |
| **Thread safety** | SSL_CTX is thread-safe; an SSL connection must be used by one thread at a time. No locking callbacks are needed (OpenSSL's threading setup APIs are no-ops) because it calls pthreads or Windows primitives internally |
| **Drop-in for the baseline** | partial — source-compatible with most of the OpenSSL 1.1.1 API but not ABI-compatible; several OpenSSL features and flags are absent or no-ops (see PORTING.md). A separate aws-lc-provider module (needs OpenSSL 3.5+ and a shared build) can serve crypto to unmodified OpenSSL 3 apps, but that path keeps OpenSSL's libssl and was not benchmarked |

## Gotchas

- The lock-free refcounts only exist when compiled as C11 with lock-free atomics (crypto/internal.h). Releases before v1.34.0 (Aug 2024) forced -std=c99, and HAProxy saw resumption collapse to about 8.5k conn/s at 64 threads. CMake now try-compiles C11, but if you build from the pre-generated sources in your own build system, make sure C11 is on
- Use v1.64.0 or later for ticket-heavy servers: until PR #2786 (Nov 2025), the session-hit counters took a pthread rwlock, and v1.62.0 managed 49k TLS 1.2 resumptions/s against OpenSSL 1.1.1's 208k on a 64-core EPYC (issue #2776)
- ARM speedups depend on recognizing the core: Graviton4 (Neoverse V2) ran the slower kernels until July 2024 (commit d3fa1f2), so new or unlisted ARM cores may fall back the same way
- The default CMake build is Debug with no optimization (pass -DCMAKE_BUILD_TYPE=Release). Memory returned by the library must be freed with OPENSSL_free, which zeroes it

## Known shortcomings

- Default builds collapsed to about 8.5k resumptions/s in the HAProxy test (worse than OpenSSL 1.1.1w and 3.1+) until rebuilt for C11; the 63.1k full-handshake figure is for v1.32.0+ built for C11, not 1.29.0 (45.7k). Test scripts and flags unpublished.
- Use v1.64.0 or later: pre-v1.34 releases forced C99 (lock-based refcounts) and a session-counter rwlock capped TLS 1.2 resumptions until v1.64.0. Not ABI-compatible with OpenSSL (recompile consumers) and lacks security levels, DHE, CCM, renegotiation, ENGINEs and TLS 1.3 stateful resumption. jitterentropy seeding raised startup to \~36 ms (#3180). Five advisories in 2026-03 (PKCS7_verify, CRL, AES-CCM timing, name constraints).

## Caveats and trade-offs

Independent third-party benchmark (HAProxy Technologies; tests mid-2024, published 2025-05-06), although AWS supplied HAProxy's AWS-LC patches. The \~63k full-handshake figure is for AWS-LC v1.32.0 plus 30 commits, not 1.29.0; 1.29.0 (\~45k) trailed OpenSSL 1.1.1w in that test. Default builds at the time (C99, lock-based refcounting) collapsed in the resumption test to \~8.5k conn/s at 64 threads, worse than OpenSSL 1.1.1w and 3.1+ with pthread locks, until rebuilt with -DCMAKE_C_STANDARD=11 (the page says this was fixed upstream). Only one ARM platform (Graviton4) was tested; gcc 11.4 is stated but optimization flags and the test scripts are not published. Small CC0 parts carry no patent grant.

Code inherited from BoringSSL/OpenSSL retains original ISC/OpenSSL-era licensing alongside AWS-LC's own Apache-2.0/ISC files (mixed licensing across the tree); default build configuration silently underperforms until C11 is forced

## Maintenance

Very active and AWS-maintained: v5.10.0 shipped 2026-09-23, releases come every 1-3 weeks, and s2n-tls and aws-lc-rs build on it. All code is under permissive licenses (Apache-2.0/ISC plus OpenSSL/BoringSSL-lineage terms). AWS published five advisories in March 2026 (PKCS7_verify, CRL-scope and X.509 validation bypasses, AES-CCM timing), so track releases.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification B, tier now B.
- **Tier reason:** Independent, well-known third party (HAProxy Technologies, W. Tarreau / W. Lallemand) with detailed methodology, gcc-11.4 and AWS r8g.16xlarge Graviton4 (Neoverse V2) stated, comparing AWS-LC against OpenSSL 1.1.1w and 3.0.2-3.4-dev; not A because the test harness/HAProxy configs and optimization flags are not published.
- **Verifier notes:** The record attributed the 63k full-handshake result to AWS-LC 1.29.0-c11 (really 45.7k; 63.1k is v1.32+30). It also gave OpenSSL 3.0.2 \~7-8k in the lightweight-lock resumption test, where the chart shows 2.3k (only 3.0.14 reached 8.1k), and it omitted that the default AWS-LC builds collapsed in resumption. All parts of the LICENSE file are OSI or CC0, so usability changes from mixed to copyable. The AWS-internal usage in stars_or_usage (s2n-tls, SDKs, aws-lc-rs) was not checked.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `workload`, `usability`, `license`, `caveats`
- **Pages the verifier opened:**
  - <https://www.haproxy.com/blog/state-of-ssl-stacks>
  - <https://cdn.haproxy.com/img/containers/partner_integrations/ssl-library-tls-handshake-performance-depending-on-locking-model-graviton-4_64-threads-diagram-1.png>
  - <https://cdn.haproxy.com/img/containers/partner_integrations/ssl-library-tls-resumption-performance-depending-on-locking-model-graviton-4_64-threads-diagram.png>
  - <https://cdn.haproxy.com/img/containers/partner_integrations/ssl-library-performance-comparison-on-r8g-16xlarge-diagram-1.png>
  - <https://cdn.haproxy.com/img/containers/partner_integrations/ssl-library-performance-comparison-on-r8g-16xlarge-diagram-4.png>
  - <https://github.com/aws/aws-lc>
  - <https://github.com/aws/aws-lc/blob/main/LICENSE>
  - <https://github.com/aws/aws-lc/blob/main/README.md>
- **Sources the enricher read:**
  - <https://github.com/aws/aws-lc>
  - <https://github.com/aws/aws-lc/blob/main/README.md>
  - <https://github.com/aws/aws-lc/blob/main/BUILDING.md>
  - <https://github.com/aws/aws-lc/blob/main/PORTING.md>
  - <https://github.com/aws/aws-lc/blob/main/INCORPORATING.md>
  - <https://github.com/aws/aws-lc/blob/main/CMakeLists.txt>
  - <https://github.com/aws/aws-lc/blob/main/LICENSE>
  - <https://github.com/aws/aws-lc/blob/main/SECURITY.md>
  - <https://github.com/aws/aws-lc/blob/main/crypto/internal.h>
  - <https://github.com/aws/aws-lc/blob/main/crypto/refcount_c11.c>
  - <https://github.com/aws/aws-lc/blob/main/crypto/fipsmodule/cpucap/internal.h>
  - <https://github.com/aws/aws-lc/blob/main/crypto/fipsmodule/bn/montgomery.c>
  - <https://github.com/aws/aws-lc/blob/main/include/openssl/ssl.h>
  - <https://github.com/aws/aws-lc/blob/main/include/openssl/mem.h>
  - <https://github.com/aws/aws-lc/blob/main/docs/porting/functionality-differences.md>
  - <https://github.com/aws/aws-lc/blob/main/docs/porting/configuration-differences.md>
  - <https://github.com/aws/aws-lc/blob/main/docs/SymbolVersioning.md>
  - <https://github.com/aws/aws-lc/blob/main/provider/README.md>
  - <https://github.com/aws/aws-lc/commit/d3fa1f237b>
  - <https://github.com/aws/aws-lc/issues/1723>
  - <https://github.com/aws/aws-lc/pull/1729>
  - <https://github.com/aws/aws-lc/issues/2776>
  - <https://github.com/aws/aws-lc/pull/2786>
  - <https://github.com/aws/aws-lc/issues/3180>
  - <https://github.com/aws/aws-lc/issues/3531>
  - <https://github.com/aws/aws-lc/issues/2283>
  - <https://github.com/aws/aws-lc/security/advisories>
  - <https://github.com/aws/aws-lc/releases>
  - <https://www.haproxy.com/blog/state-of-ssl-stacks>
  - <https://github.com/aws/aws-lc-rs>
  - <https://github.com/aws/s2n-tls>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/aws/aws-lc`) · [data/wave5/enrich/raw/github_com_aws_aws_lc.json](../../../data/wave5/enrich/raw/github_com_aws_aws_lc.json) (enrichment confidence 0.8)

</details>
