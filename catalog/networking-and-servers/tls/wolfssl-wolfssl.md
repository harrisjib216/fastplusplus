# wolfSSL

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [TLS](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `GPL-3.0 (the LICENSING file lets certain listed projects, e.g. MariaDB and OpenVPN, use it under GPL-2.0 instead)` · 🟢 active

> Embedded-first C TLS 1.3 library, not an OpenSSL fork, that beat every OpenSSL version in HAProxy's 64-core Graviton4 tests.

| | |
|---|---|
| **Beats** | OpenSSL |
| **Claimed result** | HAProxy 3.1-dev1 on a 64-core Graviton4, at 64 threads (bar charts on page). Full TLS handshake (RSA, new conn/s): wolfSSL 5.7.0 59.7k (60.6k with HAProxy locks), second only to AWS-LC v1.32+30 (63.1k), vs OpenSSL 1.1.1w 48.3k, OpenSSL 3.1.6-3.4.0-dev 42.6-43.2k, OpenSSL 3.0.2/3.0.14 21.2-21.3k (\~1.24x vs 1.1.1w, \~1.38-1.40x vs 3.1+, \~2.8x vs 3.0.x; derived from page data). TLS resumption (end-to-end conn/s): wolfSSL scaled linearly to 149.6k at 64 threads with pthread locks (148.3k with HAProxy locks; text: '150000') vs OpenSSL 1.1.1w 17.8k (pthread) / 124.1k (HAProxy locks), OpenSSL 3.1-3.4-dev 23.1-27.9k, OpenSSL 3.0.14 3.7k ('2.5% of WolfSSL') / 8.1k, and OpenSSL 3.0.2 1.6k ('1500-1600 connections per second ... just 1% of WolfSSL') / 2.3k. AWS-LC 1.29.0 built for C11 was \~20% faster than wolfSSL on resumption. |
| **Workload** | HAProxy 3.1-dev1 (2024-06-26) server-only full TLS handshake (RSA, one HTTP request per new connection, no resumption) and end-to-end TLS session resumption from tickets on both the client and backend sides (10 daisy-chained proxy instances), connections/sec vs thread count up to 64, with pthread rwlocks and with HAProxy's lightweight locks (USE_PTHREAD_EMULATION); the TLS protocol version is not stated |
| **Metric** | throughput |
| **Hardware** | AWS r8g.16xlarge instance, 64 Graviton4 (ARM Neoverse V2) cores |
| **Compiler and flags** | gcc 11.4 (stated on page for the test builds); wolfSSL configure options and optimization flags not stated (the page notes distro packages lack the build options HAProxy needs and the CPU optimizations, so wolfSSL must be built manually) |
| **Adoption** | 2.9k stars; FIPS 140-2/140-3 validated, widely used in embedded/IoT/cloud TLS deployments |
| **Last commit** | 2026-09-25 |
| **Links** | [repository](https://github.com/wolfSSL/wolfssl) · [benchmark](https://www.haproxy.com/blog/state-of-ssl-stacks) |

## Verdict

HAProxy Technologies ran HAProxy 3.1-dev1 on a 64-core Graviton4 (AWS r8g.16xlarge, gcc 11.4, mid-2024) with wolfSSL 5.7.0 and with OpenSSL 1.1.1w, 3.0.x and 3.1-3.4-dev. At 64 threads wolfSSL handled 59.7k full RSA handshakes/s vs 48.3k for 1.1.1w, \~43k for 3.1+ and \~21k for 3.0.x, and \~150k end-to-end ticket resumptions/s vs 17.8k (1.1.1w with pthread locks), 23-28k (3.1+) and 1.6-3.7k (3.0.x). It was second to AWS-LC in both tests, and neither wolfSSL's build flags nor the test harness were published.

## Use it when

- HAProxy, or another OpenSSL-API server that already has a wolfSSL port, taking many short-lived TLS connections on many cores, where OpenSSL 3.x lock and atomic contention caps throughput. At 64 threads HAProxy measured 59.7k vs \~43k RSA full handshakes/s (OpenSSL 3.1-3.4-dev) and \~150k vs 23-28k ticket resumptions/s.
- Workloads heavy on ticket resumption, such as a proxy re-encrypting to backends or clients that reconnect often, where you want linear scaling to 64 cores without special lock builds.
- Embedded, RTOS or kernel-module targets that need TLS 1.3/DTLS 1.3 in tens of kB. The repo ships ports for Zephyr, ESP-IDF, STM32, Renesas, NXP and others, custom allocators (wolfSSL_SetAllocators) and a static memory pool (WOLFSSL_STATIC_MEMORY).
- You need a FIPS 140-3 validated module and a vendor that sells commercial licenses and support contracts (HAProxy notes an LTS period is 'probably negotiable').
- Post-quantum TLS work: ML-KEM/ML-DSA with AVX-512/AArch64 assembly plus native Falcon and FrodoKEM, with no liboqs dependency as of 5.9.4.

## Skip it when

- You need a binary drop-in for libssl/libcrypto or exact OpenSSL behavior. The compatibility layer is a macro mapping, and HAProxy reports 'minor differences' and says deploying it 'requires a lot of testing and feature validation'.
- Proprietary distribution without buying a commercial license: the code is GPL-3.0, and GPL-2.0 is allowed only for a named list of projects (MariaDB, OpenVPN, U-Boot from Cisco, ...).
- You want the absolute top numbers on Graviton. AWS-LC (v1.32.0+30) beat it on full RSA handshakes (63.1k vs 59.7k/s), and AWS-LC built with C11 beat it by \~20% on resumption (183k/s).
- You depend on distro packages and automatic OS security updates. HAProxy found that the Debian/Ubuntu wolfSSL packages lacked the HAProxy options and CPU optimizations it needed, so it had to build and maintain wolfSSL by hand.
- You can't upgrade quickly. 5.9.4 (2026-09-25) fixed three High-severity certificate-verification CVEs, and one of them (CVE-2026-93302, trusted-peer CA check) widens to all CA loading in OPENSSL_COMPATIBLE_DEFAULTS builds, which --enable-haproxy, --enable-nginx, --enable-all and --enable-distro all turn on.

## How it is fast

Public-key math runs on wolfCrypt's 'SP' (single-precision) backend. This is generated code with a fixed size per key length (2048-bit RSA is 32 x 64-bit words) that does Karatsuba multiplication and Montgomery reduction in inline AArch64/x86-64 assembly (sp_arm64.c alone is \~7 MB). It is paired with ARMv8 Crypto Extension/NEON and AES-NI/AVX2/AVX-512 code for AES-GCM, SHA-2, ChaCha20-Poly1305 and X25519. For multi-core scaling, the manual says the library is 'thread safe by design' because it 'avoids global data', and reference counts use C11 &lt;stdatomic.h&gt; or GCC __atomic builtins (wc_port.h). In HAProxy's profiles, wolfSSL's resumption curve did not change between pthread locks and HAProxy's lightweight locks ('it clearly doesn't need locks'), while OpenSSL 1.1.1w and 3.x spent most of their CPU in pthread_rwlock calls and atomics.

## Compared with alternatives

Pick wolfSSL over AWS-LC when you need a small, embeddable or FIPS 140-3 stack across many CPUs and RTOSes, a vendor support contract, or good multi-core scaling from a default build (the AWS-LC versions tested needed CMAKE_C_STANDARD=11 to avoid lock collapse, since fixed upstream); pick AWS-LC for the highest Graviton numbers and an API descended from BoringSSL/OpenSSL. Tempesta FW is a complete web accelerator and DDoS-protection proxy rather than a library, so wolfSSL is the choice when you link TLS into your own server.

## Integration

| | |
|---|---|
| **Form** | static lib \| shared lib (autotools ./configure or CMake; also source-drop with user_settings.h for IDE/RTOS builds) |
| **Dependencies** | none beyond libc (optional hardware or crypto-callback ports; the liboqs dependency was removed in 5.9.4) |
| **Minimum toolchain** | ANSI C (a C89 build is supported via --enable-c89); autoconf/automake/libtool for git checkouts or CMake 3.16+ (CMake support described as 'still under development'); asm is auto-enabled only for GNU-C-compatible compilers; the benchmark used gcc 11.4 |
| **Platforms** | any C target; assembly for x86-64 (AES-NI/AVX2/AVX-512), AArch64 (ARMv8 crypto extensions/NEON), ARM32/Thumb-2/Cortex-M, RISC-V 64 and PPC32/64; Linux, Windows, macOS/iOS, Android, many RTOSes and a Linux kernel module |
| **Thread safety** | The manual says it is 'thread safe by design'. A WOLFSSL_CTX can be shared once it is fully configured, but one WOLFSSL object must not be read and written from two threads at once. Refcounts use C11/GCC atomics, and the server session-ID cache is a process-global array under a single rwlock by default. SINGLE_THREADED builds remove locking. |
| **Drop-in for the baseline** | partial — source-level only: OpenSSL-named macros in wolfssl/openssl/\*.h map to wolfSSL_\* when built with --enable-opensslextra/--enable-opensslall. Apps must be recompiled against wolfSSL headers, not every API or behavior matches, and a client verifies the server by default, unlike OpenSSL. |

## Gotchas

- Speed depends on configure flags. The fixed-size SP assembly and the ARMv8/Intel assembly are off by default in a plain ./configure (--enable-sp, --enable-armasm and --enable-intelasm all default to disabled). You enable them with --enable-sp --enable-sp-asm, --enable-armasm/--enable-intelasm, or --enable-all-asm; configure.ac turns all-asm on automatically only under --enable-all/all-crypto on 64-bit GNU C. HAProxy did not publish the flags it used.
- The ABI depends on the build configuration. configure generates wolfssl/options.h, which you must include before any other wolfSSL header (or define WOLFSSL_USE_OPTIONS_H). Struct layouts vary with options and between releases (5.9.4 changed OcspRequest, so code that embeds it must be rebuilt).
- Unlike OpenSSL, a client verifies the server by default: without loaded CAs, connect fails with -188 (README Note 2). Static-key RSA/DH/PSK cipher suites are disabled unless you enable them with WOLFSSL_STATIC_\* defines.
- The benchmark only measured ticket resumption. Session-ID resumption goes through the process-global SessionCache under one rwlock unless ENABLE_SESSION_CACHE_ROW_LOCK is defined (ssl_sess.c). Issue #10123, still open, reports an ASAN use-after-free when HAProxy's vtest suite runs against wolfSSL master.

## Known shortcomings

- GPL-3.0 (commercial licence otherwise), so not freely copyable into proprietary code. Test scripts and flags for the HAProxy benchmark unpublished.
- Benchmarked on 5.7.0 (mid-2024) with unpublished configure flags; a plain ./configure leaves the SP and CPU assembly off, and --enable-haproxy is not implied by distro builds. Use &gt;= 5.9.4 for three High-severity certificate-verification CVEs (one widened in OpenSSL-compatible builds); open ASan use-after-free with HAProxy's test suite (#10123). Only ticket resumption was measured; session-ID resumption uses a global cache under one rwlock. AWS-LC beat it in both tests.

## Caveats and trade-offs

Independent third-party benchmark (HAProxy Technologies; tests mid-2024, published 2025-05-06); HAProxy was ported to wolfSSL with help from the wolfSSL team. Distro wolfSSL packages lack the build options HAProxy needs and the CPU optimizations, so a custom build is required, and the OpenSSL-compatibility layer shows occasional behavior differences. Only one ARM platform (Graviton4) was tested; gcc 11.4 is stated but wolfSSL's configure/optimization flags and the test scripts are not published. wolfSSL was not the top performer: AWS-LC v1.32+30 beat it on full handshakes and C11-built AWS-LC beat it by \~20% on resumption. The README separately claims 'dramatically better performance ... over OpenSSL' with no numbers. GPL-3.0 is copyleft.

GPLv3 licensing (commercial dual license available for proprietary use); embedded-focused footprint and API, with an OpenSSL compatibility layer for porting

## Maintenance

Actively maintained by wolfSSL Inc. (5.9.4 released and last commit 2026-09-25) under GPL-3.0 or a commercial license. It is production-usable, but you build it yourself with the right configure flags and must keep up with frequent security releases.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Independent, well-known third party (HAProxy Technologies) with detailed methodology, gcc-11.4 and AWS r8g.16xlarge Graviton4 stated, comparing wolfSSL 5.7.0 against OpenSSL 1.1.1w and 3.0.2-3.4-dev; not A because the test harness/configs and the wolfSSL build flags are not published.
- **Verifier notes:** The record's full-handshake figure was wrong in wolfSSL's disfavor: the chart shows 59.7k/60.6k conn/s, not \~48k (48.3k is OpenSSL 1.1.1w), so wolfSSL beat OpenSSL 1.1.1w by \~24% rather than matching it. The resumption figures (150k vs 17.8k and 1.5-1.6k) match the page. Metadata checks out (GPL-3.0, 2,944 stars, last commit 2026-09-25, not a fork).
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `workload`, `license`, `caveats`
- **Pages the verifier opened:**
  - <https://www.haproxy.com/blog/state-of-ssl-stacks>
  - <https://cdn.haproxy.com/img/containers/partner_integrations/ssl-library-tls-handshake-performance-depending-on-locking-model-graviton-4_64-threads-diagram-1.png>
  - <https://cdn.haproxy.com/img/containers/partner_integrations/ssl-library-tls-resumption-performance-depending-on-locking-model-graviton-4_64-threads-diagram.png>
  - <https://cdn.haproxy.com/img/containers/partner_integrations/ssl-library-performance-comparison-on-r8g-16xlarge-diagram-1.png>
  - <https://cdn.haproxy.com/img/containers/partner_integrations/ssl-library-performance-comparison-on-r8g-16xlarge-diagram-4.png>
  - <https://github.com/wolfSSL/wolfssl>
  - <https://github.com/wolfSSL/wolfssl/blob/master/LICENSING>
  - <https://github.com/wolfSSL/wolfssl/blob/master/README.md>
- **Sources the enricher read:**
  - <https://github.com/wolfSSL/wolfssl>
  - <https://github.com/wolfSSL/wolfssl/blob/master/README.md>
  - <https://www.haproxy.com/blog/state-of-ssl-stacks>
  - <https://github.com/wolfSSL/wolfssl/blob/master/configure.ac>
  - <https://github.com/wolfSSL/wolfssl/blob/master/INSTALL>
  - <https://github.com/wolfSSL/wolfssl/blob/master/LICENSING>
  - <https://github.com/wolfSSL/wolfssl/blob/master/CMakeLists.txt>
  - <https://github.com/wolfSSL/wolfssl/blob/master/src/ssl_sess.c>
  - <https://github.com/wolfSSL/wolfssl/blob/master/wolfssl/internal.h>
  - <https://github.com/wolfSSL/wolfssl/blob/master/wolfssl/wolfcrypt/wc_port.h>
  - <https://github.com/wolfSSL/wolfssl/blob/master/wolfssl/wolfcrypt/settings.h>
  - <https://github.com/wolfSSL/wolfssl/blob/master/wolfssl/wolfcrypt/memory.h>
  - <https://github.com/wolfSSL/wolfssl/blob/master/wolfssl/openssl/ssl.h>
  - <https://raw.githubusercontent.com/wolfSSL/wolfssl/master/wolfcrypt/src/sp_arm64.c>
  - <https://www.wolfssl.com/documentation/manuals/wolfssl/chapter09.html>
  - <https://github.com/wolfSSL/wolfssl/issues/6834>
  - <https://github.com/wolfSSL/wolfssl/issues/10123>
  - <https://github.com/wolfSSL/wolfssl/issues/10796>
  - <https://github.com/wolfSSL/wolfssl/issues?q=label%3Abug>
  - <https://github.com/tempesta-tech/tempesta>
  - <https://github.com/aws/aws-lc>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/wolfssl/wolfssl`) · [data/wave5/enrich/raw/github_com_wolfssl_wolfssl.json](../../../data/wave5/enrich/raw/github_com_wolfssl_wolfssl.json) (enrichment confidence 0.8)

</details>
