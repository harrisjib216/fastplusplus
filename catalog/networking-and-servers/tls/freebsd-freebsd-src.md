# FreeBSD in-kernel TLS (kTLS) with NIC TLS offload

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [TLS](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `BSD-2-Clause` · 🟢 active

> FreeBSD in-kernel TLS record encryption, optionally NIC-offloaded, keeping zero-copy sendfile for HTTPS; beats userspace OpenSSL SSL_write data paths.

| | |
|---|---|
| **Beats** | OpenSSL (conventional userspace TLS via SSL_write()/sendfile()) |
| **Claimed result** | Netflix AsiaBSDCon 2015 paper (early in-kernel TLS prototype, 'SSLsendfile'): the same OCA Rev D serving real Netflix traffic with AES-GCM did 'about 9Gps' with in-kernel bulk encryption versus 'about 8.5GPS' with userspace nginx+OpenSSL (\~1.06x, derived from page data). The authors call this 'a slight performance improvement'. The later EuroBSDCon 2019 FreeBSD 13 kTLS slides give only 90 Gb/s at 68% CPU (software kTLS) versus 35% CPU (Chelsio T6 NIC kTLS offload), with no userspace-OpenSSL number. |
| **Workload** | 2015 paper: Netflix OpenConnect Appliance serving real Netflix video traffic over TLS, nginx preferring AES-NI AES-GCM, with a sysctl toggling in-kernel TLS sendfile against plain userspace OpenSSL on the same firmware image, measured over a night of production traffic. 2019 slides: Netflix nginx video serving at 90 Gb/s, comparing CPU use of software kTLS against Chelsio T6 NIC kTLS offload. |
| **Metric** | throughput |
| **Hardware** | 2015 comparison: Netflix OCA 'Rev D', Intel Xeon E5-2650L (exact version not stated), 64 GB RAM, FreeBSD 10.1, nginx 1.5. 2019 slides: Intel Xeon E5-2697A v4 @ 2.60GHz (16 core/32 HTT), 128GB DDR4-2400, 1x100GbE (T6 NIC), 4x NVMe. |
| **Adoption** | GitHub mirror freebsd/freebsd-src has 9,335 stars; kernel kTLS support added in r351522 (FreeBSD 13); used in production at Netflix |
| **Last commit** | 2026-09-26 |
| **Links** | [repository](https://github.com/freebsd/freebsd-src) · [benchmark](https://people.freebsd.org/~rrs/asiabsd_2015_tls.pdf) |

## Verdict

Netflix's 2015 FreeBSD 10.1 prototype (Xeon E5-2650L appliance, nginx 1.5, AES-GCM, live traffic) served about 9 Gb/s versus about 8.5 Gb/s with nginx plus userspace OpenSSL (\~1.06x), while still paying an extra OCF copy. Gallatin's EuroBSDCon 2022 ablation of the current code (AMD EPYC 7502P, 2x ConnectX-6 Dx, FreeBSD-current, nginx) reports 90 Gb/s at 80% CPU for userspace TLS via nginx thread pools (library not named), 240 Gb/s at 80% CPU for sendfile plus software kTLS (180 Gb/s with aesni), and 375 Gb/s at 53% CPU with NIC kTLS; no harness, client or compiler details are published.

## Use it when

- Static-file HTTPS or video serving on FreeBSD 13+ with a server that uses SSL_sendfile() (nginx 1.21.4+ with OpenSSL 3.0, lighttpd mod_openssl), where the box is memory-bandwidth or CPU bound at tens to hundreds of Gb/s.
- Transmit-heavy AES-GCM TLS 1.2/1.3 traffic behind a NIC that does inline TLS: mlx5en (ConnectX-6 Dx class) or cxgbe (Chelsio T6/T7). Netflix measured 90 Gb/s at 68% CPU with software kTLS versus 35% CPU with T6 offload (2019), and 375 Gb/s at 53% CPU with ConnectX-6 Dx offload (2022).
- Existing OpenSSL apps that only use SSL_read/SSL_write: setting SSL_OP_ENABLE_KTLS moves record crypto into the kernel with no other code change, though the large gains need sendfile.
- Kernel consumers that must own TLS framing, such as FreeBSD NFS-over-TLS, and TLS receive offload on TOE or NIC hardware.

## Skip it when

- Workloads that cannot use sendfile. In Netflix's 2022 ablation, kTLS without sendfile served 75 Gb/s at 80% CPU, which is below the 90 Gb/s of plain userspace TLS on the same machine (NIC kTLS without sendfile: 95 Gb/s).
- Handshake-bound or short-connection workloads: kTLS does nothing for key exchange, which stays in OpenSSL. Also avoid it for connections that must rekey: keys can be set only once per direction, so applications must disable rekeying.
- Deployments that require FIPS-validated crypto through OpenSSL providers: with kTLS the kernel does the record crypto, bypassing providers (OpenSSL docs).
- Lossy paths with NIC offload: a TCP retransmit forces the NIC to re-DMA the whole TLS record. The kernel moves a connection back to software TLS after 2% of its bytes are retransmitted (kern.ipc.tls.ifnet_max_rexmit_pct), and Netflix saw 380 to 350 Gb/s when about a third of connections moved to software.
- Risk-averse or security-sensitive hosts, particularly with receive-side kTLS. 2026 brought FreeBSD-SA-26:26 (CVE-2026-45257, local file overwrite / privilege escalation via the RX path) and SA-26:46 (CVE-2026-49423, remote kernel panic via crafted TLS 1.2 CBC records). There is also an open report (bug 295942) of corrupted HTTPS downloads with lighttpd SSL_sendfile on FreeBSD 15.x.

## How it is fast

At sendfile()/sosend() time the kernel frames TLS records into unmapped (M_EXTPG) mbufs, one per 16 KB record, which shortens socket-buffer chains about 6:1. The records are marked M_NOTREADY until a per-core pool of kernel threads encrypts them through crypto(9)/OCF (aesni, ISA-L kmod or QAT backends). This keeps Netflix's async zero-copy sendfile pipeline intact: no copy out to nginx, no userspace crypto buffer and no copy back into the kernel. In NIC (ifnet) inline mode, plaintext records reach the NIC through mbuf send tags and are encrypted during transmit DMA, so the CPU never reads or writes the payload; Netflix says this halves memory bandwidth (about 200 GB/s to about 100 GB/s at 400 Gb/s). A Chelsio TOE mode also exists.

## Compared with alternatives

Siblings such as AWS-LC, wolfSSL, picotls fusion and ChaChaCha make the crypto or the handshake faster inside a userspace library, so every byte is still copied through userspace. kTLS removes those copies and can move bulk encryption onto the NIC while still using OpenSSL for the handshake. Pick it for high-bandwidth static-content serving on FreeBSD. Pick AWS-LC or wolfSSL for handshake-heavy load, and picotls fusion or ChaChaCha when you need a faster AEAD in portable userspace code.

## Integration

| | |
|---|---|
| **Form** | module (kernel feature: `options KERN_TLS`, already in GENERIC on amd64, arm64, riscv and powerpc64; used through a kTLS-aware TLS library or the TCP_TXTLS_ENABLE/TCP_RXTLS_ENABLE socket options) |
| **Dependencies** | FreeBSD kernel with KERN_TLS and unmapped mbufs enabled (kern.ipc.mb_use_ext_pgs); a userland TLS library for the handshake (OpenSSL 3.0+, base OpenSSL built WITH_OPENSSL_KTLS (default yes on amd64/aarch64/powerpc64/riscv64), or ports OpenSSL/GnuTLS with the KTLS option); optional crypto(9) driver (aesni, ISA-L kmod, QAT); optional offload NIC (cxgbe T6/T7, mlx5en ConnectX-6 Dx class) |
| **Minimum toolchain** | FreeBSD 13.0 (first release with kTLS); OpenSSL 3.0+ for library support; nginx 1.21.4+ for SSL_sendfile |
| **Platforms** | FreeBSD only, on architectures with a physical-memory direct map (ktls(4)): amd64, arm64, riscv64, powerpc64. i386 GENERIC does not include KERN_TLS. NIC offload needs Chelsio T6/T7 or Mellanox/NVIDIA ConnectX-6 Dx-class NICs with TXTLS4/TXTLS6 capability. |
| **Thread safety** | Per-socket state. Enabling is serialized with the socket I/O locks, and keys can be set once per direction. Encryption/decryption runs on a kernel worker pool (one thread per core, optionally bound to cores or NUMA domains via kern.ipc.tls.bind_threads). |
| **Drop-in for the baseline** | partial — it complements OpenSSL rather than replacing it: OpenSSL still does the handshake and hands keys to the kernel. SSL_read/SSL_write apps work unchanged once SSL_OP_ENABLE_KTLS is set and the cipher suite is supported (otherwise OpenSSL silently stays in userspace), but the big gains need SSL_sendfile() or a sendfile-based server. |

## Gotchas

- Cipher coverage differs by mode. Software kTLS takes AES-GCM (TLS 1.2/1.3), AES-CBC with HMAC (TLS 1.0-1.2, can be turned off with kern.ipc.tls.cbc_enable) and ChaCha20-Poly1305 (TLS 1.2/1.3). mlx5en offloads only AES-GCM-128/256 on TLS 1.2/1.3, and cxgbe T6 only TLS 1.1/1.2 (no TLS 1.3). Anything else quietly falls back to software kTLS or userspace.
- NIC offload performance depends on NIC firmware and the PCIe setup. The NIC keeps per-session state (about 400k sessions at 400 Gb/s) and pages it to host RAM. ConnectX-6 Dx pre-release firmware peaked at 125 Gb/s per NIC and sustained 75, and reached 190 only after firmware enabled Relaxed Ordering and TLS_OPTIMIZE. Ampere needed PCIe extended tags (240 to 320 Gb/s).
- The software crypto backend matters: in the same Netflix ablation, sendfile+kTLS with ISA-L crypto did 240 Gb/s and with the stock aesni path 180 Gb/s, both at 80% CPU.
- Security fixes have caused regressions. The June 2026 RX fix broke kTLS receive (EBADMSG) in 15.0-RELEASE-p10 (bug 296498, fixed in main on 2026-07-29 and merged to stable). Pin and test patch levels, and keep kern.ipc.tls.enable / rx_enable handy as kill switches.

## Known shortcomings

- The record's evidence is the 2015 prototype (\~1.06x); stronger current numbers are in Gallatin's EuroBSDCon 2022 slides (below), but the userspace TLS library is unnamed and part of the gain comes from sendfile, not kTLS; kTLS without sendfile is slower than userspace TLS (75 vs 90 Gb/s). 2026 security record on 15.x: local privilege escalation via the kTLS receive path (SA-26:26, CVE-2026-45257), remote kernel panic with crafted TLS 1.2 CBC records (SA-26:46, CVE-2026-49423); the SA-26:26 fix broke kTLS receive (bug 296498); open bugs: corrupted lighttpd SSL_sendfile downloads (295942), QAT panics (280037), 2021 memory leak (253281). NIC offload: mlx5en AES-GCM only, Chelsio T6 TLS 1.1/1.2 only, no ChaCha20 offload; retransmits refetch whole records and connections fall back to software past 2% retransmitted bytes (380 to 350 Gb/s at Netflix); early ConnectX-6 Dx firmware capped at 75 Gb/s. Keys set once per direction (rekeying must be off); kernel crypto bypasses OpenSSL providers (FIPS); FreeBSD only on direct-map architectures (not i386 GENERIC); no handshake speedup.

## Caveats and trade-offs

The only measured head-to-head against userspace OpenSSL (about 8.5 to about 9 Gbps, \~6%, read from the 2015 paper text) is for Netflix's early FreeBSD 10 prototype. That prototype still made an extra copy through the Open Crypto Framework, so it is not the FreeBSD 13 kTLS code now in freebsd-src (uipc_ktls.c, Copyright 2014-2019 Netflix). The 2019 slides compare software kTLS with NIC-offload kTLS only and argue the OpenSSL advantage qualitatively. The numbers are from live production traffic with no public benchmark harness or compiler details, so tier is capped at C. The kTLS files carry an SPDX BSD-2-Clause header. The repository-level license is NOASSERTION because FreeBSD mixes licenses.

FreeBSD/Linux kernel-specific (not portable to arbitrary C++ apps); NIC-offload path needs specific hardware (Chelsio T6, Mellanox ConnectX-6 DX); adds kernel attack surface for TLS handling; only covers the bulk-record encryption phase, handshake still uses userspace OpenSSL/rustls/etc.

## Maintenance

Actively maintained in freebsd-src main (uipc_ktls.c last changed 2026-09-23), BSD-2-Clause, shipped since FreeBSD 13.0, in GENERIC and base OpenSSL by default on amd64/arm64/riscv/powerpc64 on current main, and run in production at Netflix; it is an OS feature you turn on rather than code you vendor, and 2026 brought two security advisories plus open receive/sendfile bugs.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The EuroBSDCon 2019 slides only compare software kTLS (68% CPU) with T6 NIC kTLS (35% CPU) at 90 Gb/s. The Netflix AsiaBSDCon 2015 paper does compare against userspace nginx+OpenSSL on the same appliance with live traffic: about 8.5 Gbps versus about 9 Gbps with in-kernel TLS sendfile. These are first-party production numbers with no benchmark code or compiler details, so tier C.
- **Verifier notes:** The given benchmark_url has no numbers against the named OpenSSL baseline. I repointed benchmark_url to the Netflix AsiaBSDCon 2015 paper, which does measure against userspace nginx+OpenSSL, though only for a precursor prototype. The Netflix tech blog post on kTLS (Medium) returned 403 and was not read. gh api was rate-limited, so metadata comes from github.com pages (9335 stars, not archived, last commit on main 2026-09-26; uipc_ktls.c last changed 2026-09-23).
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `hardware`, `last_commit`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** Netflix/Gallatin EuroBSDCon 2022 (people.freebsd.org/\~gallatin/talks/euro2022.pdf; AMD EPYC 7502P, 2x ConnectX-6 Dx, nginx): userspace TLS via nginx thread pools without kTLS or sendfile 90 Gb/s at 80% CPU; sendfile + software kTLS 240 Gb/s at 80% CPU with ISA-L (180 Gb/s with aesni); NIC kTLS + sendfile 375 Gb/s at 53% CPU.
- **Pages the verifier opened:**
  - <https://people.freebsd.org/~gallatin/talks/euro2019-ktls.pdf>
  - <https://people.freebsd.org/~rrs/asiabsd_2015_tls.pdf>
  - <https://github.com/freebsd/freebsd-src>
  - <https://github.com/freebsd/freebsd-src/commits/main>
  - <https://github.com/freebsd/freebsd-src/commits/main/sys/kern/uipc_ktls.c>
  - <https://raw.githubusercontent.com/freebsd/freebsd-src/main/sys/kern/uipc_ktls.c>
- **Sources the enricher read:**
  - <https://people.freebsd.org/~rrs/asiabsd_2015_tls.pdf>
  - <https://people.freebsd.org/~gallatin/talks/euro2019-ktls.pdf>
  - <https://people.freebsd.org/~gallatin/talks/>
  - <https://people.freebsd.org/~gallatin/talks/euro2019.pdf>
  - <https://people.freebsd.org/~gallatin/talks/euro2021.pdf>
  - <https://people.freebsd.org/~gallatin/talks/euro2022.pdf>
  - <https://people.freebsd.org/~gallatin/talks/OpenFest2023.pdf>
  - <https://github.com/freebsd/freebsd-src>
  - <https://github.com/freebsd/freebsd-src/commits/main/sys/kern/uipc_ktls.c>
  - <https://raw.githubusercontent.com/freebsd/freebsd-src/main/share/man/man4/ktls.4>
  - <https://raw.githubusercontent.com/freebsd/freebsd-src/main/sys/sys/ktls.h>
  - <https://raw.githubusercontent.com/freebsd/freebsd-src/main/sys/kern/uipc_ktls.c>
  - <https://raw.githubusercontent.com/freebsd/freebsd-src/main/sys/opencrypto/ktls_ocf.c>
  - <https://raw.githubusercontent.com/freebsd/freebsd-src/main/sys/dev/mlx5/mlx5_en/mlx5_en_hw_tls.c>
  - <https://raw.githubusercontent.com/freebsd/freebsd-src/main/sys/dev/mlx5/mlx5_en/mlx5_en_hw_tls_rx.c>
  - <https://raw.githubusercontent.com/freebsd/freebsd-src/main/sys/dev/cxgbe/crypto/t6_kern_tls.c>
  - <https://raw.githubusercontent.com/freebsd/freebsd-src/main/sys/dev/cxgbe/crypto/t7_kern_tls.c>
  - <https://raw.githubusercontent.com/freebsd/freebsd-src/main/sys/amd64/conf/GENERIC>
  - <https://raw.githubusercontent.com/freebsd/freebsd-src/main/sys/arm64/conf/std.arm64>
  - <https://raw.githubusercontent.com/freebsd/freebsd-src/main/sys/i386/conf/GENERIC>
  - <https://raw.githubusercontent.com/freebsd/freebsd-src/main/sys/riscv/conf/GENERIC>
  - <https://raw.githubusercontent.com/freebsd/freebsd-src/main/sys/powerpc/conf/GENERIC64>
  - <https://raw.githubusercontent.com/freebsd/freebsd-src/main/share/mk/src.opts.mk>
  - <https://freebsdfoundation.org/wp-content/uploads/2020/07/TLS-Offload-in-the-Kernel.pdf>
  - <https://www.freebsd.org/security/advisories/>
  - <https://www.freebsd.org/security/advisories/FreeBSD-SA-26:26.ktls.asc>
  - <https://www.freebsd.org/security/advisories/FreeBSD-SA-26:46.ktls.asc>
  - <https://www.freebsd.org/security/notices/>
  - <https://bugs.freebsd.org/bugzilla/buglist.cgi?quicksearch=ktls>
  - <https://bugs.freebsd.org/bugzilla/show_bug.cgi?id=295942>
  - <https://bugs.freebsd.org/bugzilla/show_bug.cgi?id=296498>
  - <https://bugs.freebsd.org/bugzilla/show_bug.cgi?id=280037>
  - <https://nginx.org/en/CHANGES>
  - <https://raw.githubusercontent.com/openssl/openssl/master/doc/man3/SSL_CTX_set_options.pod>
  - <https://hn.algolia.com/api/v1/search?query=FreeBSD%20kTLS&tags=story>
  - <https://lists.freebsd.org/pipermail/freebsd-arch/2019-August/019690.html>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/freebsd/freebsd-src`) · [data/wave5/enrich/raw/github_com_freebsd_freebsd_src.json](../../../data/wave5/enrich/raw/github_com_freebsd_freebsd_src.json) (enrichment confidence 0.8)

</details>
