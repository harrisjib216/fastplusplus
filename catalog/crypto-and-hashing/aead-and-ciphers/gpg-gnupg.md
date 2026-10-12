# GnuPG (gpg)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [AEAD and ciphers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `GPL-3.0-or-later` · 🟢 active

> The reference OpenPGP command-line tool; in 2021 runs it streamed public-key encryption 1.3-2.7x faster than Sequoia's sq.

| | |
|---|---|
| **Beats** | Sequoia-PGP sq (sq encrypt) |
| **Claimed result** | jgoerzen run: gpg 2.2.27 16.97 s vs sq 36.60 s (2.16x, derived from page data), CFB+MDC both sides; the Sequoia issue #771 armored row (2.70x) is dominated by armoring speed. |
| **Workload** | Public-key encryption of a 1 GiB stream of /dev/urandom (dd bs=1M count=1024) to one recipient, compression off, piped through bar to /dev/null, in ASCII-armored and in binary output mode: gpg --always-trust -er foo --compress-algo none [--armor] vs sq encrypt --recipient-cert foo.pub --compression none [--binary]. |
| **Metric** | throughput |
| **Adoption** | 991 stars on the GitHub mirror (maintainers do not track the mirror; canonical repo is git.gnupg.org, not opened) |
| **Last commit** | 2026-10-09 |
| **Links** | [repository](https://github.com/gpg/gnupg) · [benchmark](https://gitlab.com/sequoia-pgp/sequoia/-/issues/771) |

## Verdict

In sequoia-pgp/sequoia issue 771 (2021-11-01, filed by Sequoia developer Justus Winter), piping 1 GiB from /dev/urandom through each tool to one recipient with compression off gave gpg 170.7 MB/s vs sq 128.0 MB/s binary (1.33x) and 138.7 vs 51.4 MB/s armored (2.70x), on unstated versions and hardware; a commenter's run on an Intel Core i5-5200U with AES256 forced (gpg 2.2.27 vs sq 0.25.0, 3.3 GB file) took 16.97 s vs 36.60 s (2.16x, derived from page data). Sequoia then sped up its armor encoder and, in the same thread, overtook gpg on decryption; no newer encryption comparison was found.

## Use it when

- Encrypting or decrypting large files or streams in shell pipelines and backups where OpenPGP is the required format and the other side runs GnuPG.
- Recipients whose keys advertise the AEAD feature, so gpg 2.3+ picks OCB; GnuPG's own commit message reports 4.2 GB/s AES256.OCB encryption against 783 MB/s for AES256.CFB on the same Ryzen 5800X.
- Large keyrings where key listing and lookup speed matter: with keyboxd (SQLite) gpg 2.4.5 listed 9010 keys 4.9-8.1x faster than the Sequoia gpg-sq chameleon 0.9.0 in a 2024 hyperfine report (sequoia-chameleon-gnupg issue 83), though Sequoia attributes most of the gap to uncached trust evaluation.
- Smartcard, gpg-agent, ssh-agent or S/MIME workflows that need one mature, widely packaged toolchain.

## Skip it when

- Embedding OpenPGP inside a program: gpg is a process to spawn and parse (via GPGME), not an in-process library, and it is GPL-3.0-or-later, so its code cannot be copied into permissive projects.
- Decryption throughput: the same 2021 thread shows sq 9.264 s vs gpg 10.944 s on a 3 GB binary message once Sequoia fixed its buffering and switched to XXH3 body hashing, so GnuPG is not faster there.
- Interoperability with RFC 9580 implementations: gpg's AEAD output uses its LibrePGP OCB packet (PKT_ENCRYPTED_OCB); SEIPDv2 is emitted only with RFC-9980 keys in the --allow-9980 mode added in 2.5.23, so OCB messages may not be readable by RFC 9580 tools.
- When you need fast bulk encryption to recipients without the AEAD feature flag: CFB+MDC encryption cannot be parallelized and is several times slower than OCB.

## How it is fast

Data moves through a chain of iobuf filters (compression, cipher, armor) with 64 KiB default buffers, so a 10 MB encryption takes 2906 write and 2471 read syscalls where 2021 sq made 436918 writes in armor mode. Bulk crypto runs in libgcrypt's assembly (AES-NI, VAES AVX2/AVX-512 and ARMv8-CE AES, SHA-NI SHA-1, PCLMUL CRC24 for the armor checksum). Recent releases add a memcpy-free AEAD path (AES256.OCB encryption 2.2 to 4.2 GB/s on a Ryzen 5800X, commit 99e2c178c7) and skip redundant hash contexts during MDC decryption (about 3.4x faster, commit ab177eed51). Without AEAD, gpg uses CFB plus a SHA-1 MDC, and CFB encryption is inherently serial: libgcrypt has bulk VAES paths only for CFB decryption, CTR, CBC decryption, OCB, XTS and ECB.

## Compared with alternatives

The catalogued siblings (libaegis, HiAE, Botan, Mbed TLS, intel-ipsec-mb, Crypto++) are cipher or AEAD libraries you call in-process; pick GnuPG only when you need OpenPGP-format file encryption with key management, not raw AEAD speed. Note that the Crypto++ entry itself benchmarks faster CAST5 than libgcrypt, GnuPG's crypto backend.

## Integration

| | |
|---|---|
| **Form** | module (command-line executables gpg, gpg-agent, gpgsm and others; programmatic use through the separate LGPL GPGME library or --status-fd) |
| **Dependencies** | libgpg-error 1.56+, libgcrypt 1.12.0+, libassuan 3.0.0+, libksba 1.6.3+, npth 1.2+; optional ntbtls 0.2.0+ or GnuTLS 3.2+, SQLite 3.27+ (keyboxd), zlib/bzip2; Pinentry at runtime for passphrases |
| **Minimum toolchain** | Autotools build (configure; make) with a C99 compiler; not further documented in the README |
| **Platforms** | Unix-like systems and Windows (installer build documented in doc/HACKING); bulk-crypto acceleration comes from libgcrypt on x86-64 (AES-NI, VAES, SHA-NI, PCLMUL) and AArch64 (ARMv8 crypto extensions) |
| **Thread safety** | not applicable to the gpg process itself; concurrent gpg invocations share gpg-agent and the keyring, and GPGME documents its own threading rules (not read this session) |
| **Drop-in for the baseline** | partial — reads and writes standard OpenPGP that sq also handles (CFB+MDC, SEIPDv1), but the command-line syntax differs, and gpg's default OCB output for AEAD-capable keys uses a packet RFC 9580 tools may not accept. |

## Gotchas

- The armored comparison (2.70x) mostly measures Sequoia's 2021 armor writer, not the cipher: issue 772 (closed by commit aeacd64d on 2021-11-05) shows 'sq armor' alone at 60.3 MB/s vs 'gpg --enarmor' at 126.1 MB/s through the same dd|bar pipeline, the maintainer blamed Sequoia's slow CRC24, and sq made 43 write syscalls per KB in armor mode. gpg's armor-only rate is even below its 138.7 MB/s armored-encryption rate, so the armored rows are bounded by armoring and the pipe; bar also sat after the encryptor, so armored MB/s count base64 output bytes (about 1.4 GB for 1 GiB of input).
- Harness flaws in the opening post: single run per configuration, no gpg or sq version, key type, cipher or CPU, and no control run of 'dd if=/dev/urandom | bar' alone, so the pipeline's own ceiling is unknown. GnuPG's own commit ab177eed51 measured AES256.CFB encryption at 783 MB/s on a Ryzen 5800X, so the 170.7 MB/s binary figure is not a cipher-throughput ceiling for either tool.
- The cleaner data point is jgoerzen's CPU-bound file run (gpg 2.2.27 with --cipher-algo AES256 vs sq 0.25.0, i5-5200U, output to /dev/null, user time 15.5 s vs 35.4 s): both used CFB+MDC, since gpg 2.2 has no OCB, but it is still one machine and 2021 versions.
- Recent releases fixed memory-safety bugs (double free in import_revoke_cert in 2.5.22; an exploitable printf bug in gpgsm's --debug x509 and OOB reads in dirmngr and scd in 2.5.23); keep to current releases.

## Known shortcomings

- Numbers come from Sequoia issue #771 (filed by Sequoia developer Justus Winter, 2021, sq 0.25): no benchmark code or flags; Sequoia fixed its armor CRC24 slowness days later (#772); in the same thread decryption is reversed (sq 9.264 s vs gpg 10.944 s). A second run by jgoerzen (gpg 2.2.27 16.97 s vs sq 36.60 s, i5-5200U, 2.16x derived from page data) is also anecdotal.
- Enricher: the armored 2.70x row mostly measures armoring, not the cipher (issue 772: sq armor alone 60.3 MB/s vs gpg --enarmor 126.1 MB/s; gpg armor-only is even below its 138.7 MB/s armored encrypt); the opening post has no dd|bar control run, single runs, no versions; gpg commit ab177eed51 shows AES256.CFB encrypt at 783 MB/s on a Ryzen 5800X, so 170.7 MB/s is no cipher ceiling. The cleaner point is the jgoerzen run (2.16x, CFB+MDC both sides). CFB encrypt is serial in libgcrypt; OCB reaches 4.2 GB/s (commit 99e2c178c7) but gpg OCB uses the LibrePGP packet, not SEIPDv2. sequoia-chameleon-gnupg issue 83 (2024 hyperfine): gpg 2.4.5 lists keys 4.9-8.1x faster than gpg-sq 0.9.0.

## Caveats and trade-offs

The issue (gitlab.com sequoia-pgp/sequoia #771, opened 2021-11-01, still open, no labels) was filed by Sequoia developer Justus Winter (teythoon) against his own project, so the comparison comes from the baseline's maintainers, not from GnuPG; the opening post gives no gpg or sq version, key type, cipher or CPU and is a single run per configuration. The numbers are stale: the armored gap was traced to Sequoia's slow CRC24 in the armor encoder (issue #772, closed by commit aeacd64d on 2021-11-05), and a maintainer called binary encryption 'a bit slower, but in the same order of magnitude'. The same thread shows the decryption ranking reversed after Sequoia's buffer fixes and XXH3 body hashing (2021-11-04: gpg 10.944 s vs sq 9.264 s decrypting a 3 GB binary message), so GnuPG is not faster on decryption. No newer gpg-versus-sq throughput comparison was found (one WebSearch); whether current sq still trails gpg on encryption is unknown. The dd from /dev/urandom pipeline can itself cap throughput near the quoted figures, and the armored gap measures the armor encoder rather than the cipher. GnuPG's own NEWS lists only self-versus-earlier-release speedups (signature verification more than four times faster, detached signing doubled, threefold decryption speedup for large files, AES256.OCB encryption nearly doubled) with no external baseline. The GitHub repo is a mirror the maintainers do not track (canonical git.gnupg.org). Category aead-and-ciphers fits bulk public-key encryption throughput better than the suggested signatures-kem. [retier] No control run, single runs, no versions in #771; Sequoia fixed its armor CRC24 days later (#772); decryption reversed in the same thread; CFB encrypt serial in libgcrypt (AES256.CFB 783 MB/s on a 5800X per commit ab177eed51); gpg OCB uses the LibrePGP packet, not SEIPDv2; gpg 2.4.5 lists keys 4.9-8.1x faster than gpg-sq 0.9.0 (sequoia-chameleon-gnupg #83).

GPL-3.0-or-later (copyleft), so code cannot be copied into permissive projects; the evidence covers only streaming public-key encryption, not signing, verification or key management.

## Maintenance

Actively developed by g10 Code (2.5.24 released 2026-09-23; GitHub repo is an untracked mirror of git.gnupg.org), GPL-3.0-or-later so usable as a tool but not copyable into permissive code; the speed evidence is a 2021 single-run comparison against an early Sequoia release that has since been sped up.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The opening post of sequoia-pgp/sequoia issue #771 shows exactly the four quoted runs (sq 51.4 and 128.0 MB/s, gpg 138.7 and 170.7 MB/s) as one-shot terminal output with no versions, CPU or repetitions; a later comment adds an independent run with versions and CPU, but the numbers are from 2021, the baseline was sped up days later, and there is no benchmark code or build flags, so C.
- **Verifier notes:** Numbers verified verbatim in the GitLab issue (opened via the GitLab API and discussions JSON). Shortcomings: comparison filed by the baseline's own developer, single unversioned runs, November 2021 numbers on sq 0.25 that Sequoia fixed days later (armor CRC24 fix #772; decryption now faster than gpg in the same thread), no benchmark code or flags, and Sequoia is a challenger rather than an incumbent baseline. GitHub mirror metadata checked: 991 stars, GPL-3.0 plus other licence files, last commit 2026-10-09, not archived.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-55 (wave 7); enricher w7 pair-008
- **Pages the verifier opened:**
  - <https://gitlab.com/sequoia-pgp/sequoia/-/issues/771>
  - <https://gitlab.com/api/v4/projects/sequoia-pgp%2Fsequoia/issues/771>
  - <https://gitlab.com/sequoia-pgp/sequoia/-/issues/771/discussions.json>
  - <https://gitlab.com/api/v4/projects/sequoia-pgp%2Fsequoia/issues/772>
  - <https://gitlab.com/sequoia-pgp/sequoia/-/issues/772/discussions.json>
  - <https://gitlab.com/api/v4/projects/sequoia-pgp%2Fsequoia/issues/773>
  - <https://github.com/gpg/gnupg>
  - <https://github.com/gpg/gnupg/commits>
- **Sources the enricher read:**
  - <https://github.com/gpg/gnupg>
  - <https://raw.githubusercontent.com/gpg/gnupg/master/README>
  - <https://raw.githubusercontent.com/gpg/gnupg/master/NEWS>
  - <https://raw.githubusercontent.com/gpg/gnupg/master/configure.ac>
  - <https://raw.githubusercontent.com/gpg/gnupg/master/common/iobuf.c>
  - <https://raw.githubusercontent.com/gpg/gnupg/master/common/iobuf.h>
  - <https://raw.githubusercontent.com/gpg/gnupg/master/g10/cipher-cfb.c>
  - <https://raw.githubusercontent.com/gpg/gnupg/master/g10/cipher-aead.c>
  - <https://raw.githubusercontent.com/gpg/gnupg/master/g10/encrypt.c>
  - <https://raw.githubusercontent.com/gpg/gnupg/master/g10/armor.c>
  - <https://github.com/gpg/gnupg/commit/ab177eed51>
  - <https://github.com/gpg/gnupg/commit/99e2c178c7>
  - <https://raw.githubusercontent.com/gpg/libgcrypt/master/cipher/rijndael-vaes-avx512-amd64.S>
  - <https://gitlab.com/api/v4/projects/sequoia-pgp%2Fsequoia/issues/771>
  - <https://gitlab.com/sequoia-pgp/sequoia/-/issues/771/discussions.json>
  - <https://gitlab.com/sequoia-pgp/sequoia/-/issues/772/discussions.json>
  - <https://gitlab.com/api/v4/projects/sequoia-pgp%2Fsequoia/issues/772>
  - <https://gitlab.com/api/v4/projects/sequoia-pgp%2Fsequoia/issues?search=slow&in=title>
  - <https://gitlab.com/api/v4/projects/sequoia-pgp%2Fsequoia-chameleon-gnupg/issues/72>
  - <https://gitlab.com/sequoia-pgp/sequoia-chameleon-gnupg/-/issues/72/discussions.json>
  - <https://gitlab.com/api/v4/projects/sequoia-pgp%2Fsequoia-chameleon-gnupg/issues/83>
  - <https://gitlab.com/sequoia-pgp/sequoia-chameleon-gnupg/-/issues/83/discussions.json>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/gpg/gnupg`) · [data/wave7/enrich/raw/github_com_gpg_gnupg.json](../../../data/wave7/enrich/raw/github_com_gpg_gnupg.json) (enrichment confidence 0.6)

</details>
