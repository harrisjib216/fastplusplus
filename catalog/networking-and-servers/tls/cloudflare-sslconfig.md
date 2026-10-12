# Cloudflare ChaCha20-Poly1305 (sslconfig OpenSSL patch)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [TLS](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `BSD-3-Clause` · 🟡 stale

> Cloudflare's 2016 OpenSSL 1.0.2 patch adding x86-64 ChaCha20-Poly1305 TLS suites; about 7% faster seal than OpenSSL 1.1.0-pre on Haswell.

| | |
|---|---|
| **Beats** | OpenSSL 1.1.0-pre ChaCha20-Poly1305 implementation |
| **Claimed result** | Page: 'significantly outperforms OpenSSL [1.1.0-pre] for short records, and is slightly faster for longer records. The average performance advantage is 7%' (average across the 64 B to 16 KB record sizes graphed; cycles/byte for 'seal' with 13 bytes AAD on Haswell; graphs only, not tabulated). The page also says it gets 'below 2 cycles/byte' for large records. AES-128-GCM and AES-256-GCM still beat ChaCha20-Poly1305 for records larger than 320 bytes. |
| **Workload** | TLS AEAD 'seal' operation with 13 bytes of associated data (matching TLS record framing), plaintext sizes 64-16384 bytes, cycles/byte on a Haswell CPU with AVX2. |
| **Metric** | throughput |
| **Hardware** | Haswell CPU with AVX2 (exact model not stated) |
| **Adoption** | 1,313 stars |
| **Last commit** | 2024-09-16 |
| **Links** | [repository](https://github.com/cloudflare/sslconfig) · [benchmark](https://blog.cloudflare.com/it-takes-two-to-chacha-poly/) |

## Verdict

Cloudflare's 2016-04-04 post graphs cycles/byte for 'seal' with 13-byte AAD over 64 B-16 KB records on an unnamed Haswell (AVX2) against OpenSSL 1.1.0-pre: much lower at short records, slightly lower at long ones, 7% better on average, and under 2 cycles/byte at large sizes; it gives no compiler, flags or harness, and AES-GCM still wins above 320 bytes. For scale, OpenSSL's current asm headers list Haswell large-buffer costs of 1.23 cpb (ChaCha20, AVX2) plus 0.65 cpb (Poly1305, AVX2), about 1.9 cpb in two passes, so the long-record gap was always small.

## Use it when

- You maintain a TLS 1.2 server that is frozen on OpenSSL 1.0.2 (for example nginx built from source) and still need ChaCha20-Poly1305 suites, including the pre-RFC draft suites that 2016-era Chrome used.
- Traffic has many small TLS records (under \~1.5 KB, for example with dynamic record sizing). The post reports its largest gain over OpenSSL 1.1.0-pre at short records.
- You want ChaCha only for clients that rank it first (typically mobile clients without AES-NI), while AES-GCM clients keep AES-GCM. The patched ssl3_choose_cipher does exactly this.
- You are studying or porting a stitched ChaCha20-Poly1305. The 1.0.2j assembly is a readable ancestor of the code BoringSSL (added 2017-01-23) and ring ship today.

## Skip it when

- Any new deployment. OpenSSL 1.1.0+ has native RFC ChaCha20-Poly1305, BoringSSL and ring carry the maintained descendant of this assembly with proper CPU checks, and OpenSSL 1.0.2 itself is out of public support.
- x86-64 CPUs without SSE4.1 (Core 2 65nm such as Xeon X3220, AMD K8/K10). The 1.0.2j SSE path uses pshufb, pextrq and pinsrb with no CPUID check and dies with an illegal instruction (issues #51 and #57, confirmed by the author).
- Architectures other than x86-64. Only portable C is provided there. Users reported compile errors without the asm (#26, older patch) and ChaCha failures in no-asm and 32-bit builds (#57, unconfirmed).
- Bulk throughput on AES-NI hardware. The post's own graphs show AES-128-GCM and AES-256-GCM beating ChaCha20-Poly1305 on Haswell for records over 320 bytes.
- OpenSSL 1.1.x. The 1.1.0 patch only changes cipher preference, and the author declined to port the draft suites (#78).

## How it is fast

The 1.0.2j patch adds chacha20_poly1305_x86_64.pl by Vlad Krasnov. It is a 'stitched' one-pass seal/open with SSE and AVX2 paths. Poly1305 runs as 64-bit scalar multiplies (MULX on the AVX2 path) interleaved with the SIMD ChaCha20 rounds, so the MAC work overlaps the cipher work instead of taking a second pass over the data. It also has a special case for the 13-byte TLS AAD and hand-written tail code for remainders of 64 bytes or less, 65-128, 129-192 and 193-255 bytes, which targets short records. The earlier 1.0.2f/g patches (Feb 2016, current when the post appeared) used Intel's 2014 AVX/AVX2 ChaCha20 and Poly1305 kernels plus a Cloudflare scalar Poly1305 instead, and the post does not say which version it graphed.

## Compared with alternatives

Pick it only if you are pinned to a patched OpenSSL 1.0.2 build and need ChaCha20-Poly1305 suites. Otherwise ChaChaCha reports beating both OpenSSL's asm and BoringSSL's stitched AVX2 ChaCha20-Poly1305 (this code's descendant), and AWS-LC or wolfSSL are maintained whole-library alternatives to OpenSSL.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | The exact OpenSSL 1.0.2f, 1.0.2g or 1.0.2j source tree (one patch per version) and Perl for perlasm. nginx or the app must be rebuilt or relinked against the patched OpenSSL. |
| **Minimum toolchain** | The perlasm version checks emit the AVX2 path only with GNU as &gt;= 2.22, clang &gt;= 3.1, NASM &gt;= 2.10 or ml64 &gt;= 11. With older assemblers you get only the SSE path. On CentOS 6 binutils the 1.0.2g patch failed to assemble (#32). Compiler versions are not documented. |
| **Platforms** | The assembly is x86-64 only: SSE4.1 is assumed, and the AVX2+MULX path is chosen on the AVX2 bit. Other architectures fall back to portable C. Windows builds had link problems (#43). |
| **Thread safety** | Not documented. State lives in the per-connection EVP_CIPHER_CTX, as in stock OpenSSL. |
| **Drop-in for the baseline** | partial — for OpenSSL 1.0.2 it is a rebuild-time patch that adds suites and a TLS-record-only EVP_chacha20_poly1305(), and it also changes server cipher selection. It is not a replacement for OpenSSL 1.1.0's own ChaCha20-Poly1305 (the 1.1.0 patch is only the preference tweak). |

## Gotchas

- CPU dispatch is incomplete. There is no SSE4.1 check (author, #57: 'requires SSE4, but it does not actually perform a CPUID check'), and the AVX2 path uses MULX (BMI2) while testing only the AVX2 bit. BoringSSL's descendant requires SSE4.1 and checks AVX2 && BMI2.
- With server cipher preference on, ChaCha is chosen only when it is the client's first-listed suite (with a retry if nothing else matches). Earlier patch versions could refuse ChaCha entirely (#48). The author says to drop the ssl3_choose_cipher change if you want normal negotiation.
- Only the RFC suites use the stitched assembly. Draft-suite traffic goes through the C glue plus separate ChaCha20 and Poly1305 kernels. The EVP interface expects an 8-byte TLS seq_num prepended to the AAD, so RFC 7539 test vectors cannot be checked directly (#60).
- Licensing is mixed. The repo says BSD-3-Clause, but the assembly files carry Apache-2.0 headers (Cloudflare 2016, Intel 2014), and the patch edits OpenSSL-licensed files.

## Known shortcomings

- Correction: the stitched x86-64 ChaCha20-Poly1305 code was not merged into OpenSSL (OpenSSL still uses separate chacha/poly1305 modules); it went into BoringSSL (2017) and ring. Only the ossl102j patch (2016-10) contains the stitched code; the f/g patches current when the post appeared use Intel's 2014 separate kernels, and the post doesn't say which was graphed. Assembly files are Apache-2.0 (Cloudflare/Intel), not just BSD-3. The SSE path uses SSE4.1 instructions without a CPUID check (illegal-instruction crashes on Core 2 and AMD K8/K10, #51, #57, confirmed by the author); the AVX2 path uses MULX but only checks AVX2. With server cipher preference, ChaCha is chosen only as the client's first choice (#48). EVP expects an 8-byte sequence number prepended to the AAD, so RFC 7539 vectors can't be checked directly (#60). Portable C fallback reported broken in no-asm/32-bit builds (#26, #57). The long-record gain over OpenSSL's own asm (\~1.9 cycles/byte on Haswell) was always small; cycles/byte hides AVX2 downclocking. Abandoned: last updated 2017-03, Cloudflare moved to BoringSSL (#78), OpenSSL 1.0.2 unsupported, README links a missing patch file.

## Caveats and trade-offs

Numbers are read off graphs in a 2016-04-04 blog post, not tabulated. Compiler, flags and exact CPU model ('a Haswell CPU') are not stated, so tier is capped at C. The baseline was pre-release OpenSSL 1.1.0, and the page does not say whether that baseline was generic C or assembly. The repository is mainly Cloudflare's nginx cipher configuration. The speed code is patches/openssl__chacha20_poly1305_draft_and_rfc_ossl102{f,g,j}.patch (Vlad Krasnov; adds an AVX2 chacha20_poly1305_x86_64.pl) against OpenSSL 1.0.2. The openssl__1.1.0_chacha20_poly1305.patch only changes cipher-preference logic in ssl/s3_lib.c. The same stitched assembly (Copyright 2015 CloudFlare, author Vlad Krasnov) is in BoringSSL crypto/cipher_extra/asm/chacha20_poly1305_x86_64.pl. Inclusion in upstream OpenSSL was not verified. The patches modify OpenSSL-licensed files, so the repository's BSD-3-Clause license does not cover the whole patched tree. This is mainly a historical result, not a current 'faster than OpenSSL' claim.

x86-64 assembly only (Sandy Bridge+/AVX2 paths); this exact code (by Vlad Krasnov / Cloudflare, with Andy Polyakov) was subsequently merged upstream into OpenSSL itself, so modern OpenSSL/BoringSSL already ship an equivalent fast ChaCha20-Poly1305 path -- the speed advantage over \*current\* OpenSSL is likely gone.

## Maintenance

Stale historical reference, not a dependency. The ChaCha patches were last refreshed in Oct 2016 (1.0.2j) and Mar 2017 (1.1.0 preference tweak), later commits only touch config and CI, Cloudflare said in 2017 it had moved to BoringSSL, and the README still links to a patch file (openssl__chacha20_poly1305_cf.patch) that no longer exists.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The Cloudflare blog post (2016-04-04) gives first-party cycles/byte graphs against OpenSSL 1.1.0-pre on an unnamed Haswell CPU. It states 'the average performance advantage is 7%' and 'below 2 cycles/byte', but it names no compiler or flags, no exact CPU model, and no benchmark code, so tier C.
- **Verifier notes:** The record's '7% for short TLS records' misattributes the figure. The page gives 7% as the average over all sizes and calls the short-record gain 'significant'. The caveat's '2015' date is wrong: the post is dated 2016-04-04. Last commit is 2024-09-16, so status is stale, not finished. gh api was rate-limited, so metadata comes from the github.com pages (BSD-3-Clause, 1313 stars, not archived).
- **Fields the verifier corrected:** `claimed_speedup`, `baseline`, `last_commit`, `maintenance_status`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://blog.cloudflare.com/it-takes-two-to-chacha-poly/>
  - <https://github.com/cloudflare/sslconfig>
  - <https://github.com/cloudflare/sslconfig/commits/master>
  - <https://github.com/cloudflare/sslconfig/tree/master/patches>
  - <https://raw.githubusercontent.com/cloudflare/sslconfig/master/README.md>
  - <https://raw.githubusercontent.com/cloudflare/sslconfig/master/patches/openssl__1.1.0_chacha20_poly1305.patch>
  - <https://raw.githubusercontent.com/cloudflare/sslconfig/master/patches/openssl__chacha20_poly1305_draft_and_rfc_ossl102j.patch>
  - <https://raw.githubusercontent.com/google/boringssl/main/crypto/cipher_extra/asm/chacha20_poly1305_x86_64.pl>
- **Sources the enricher read:**
  - <https://github.com/cloudflare/sslconfig>
  - <https://github.com/cloudflare/sslconfig/commits/master>
  - <https://github.com/cloudflare/sslconfig/tree/master/patches>
  - <https://raw.githubusercontent.com/cloudflare/sslconfig/master/README.md>
  - <https://raw.githubusercontent.com/cloudflare/sslconfig/master/patches/openssl__1.1.0_chacha20_poly1305.patch>
  - <https://raw.githubusercontent.com/cloudflare/sslconfig/master/patches/openssl__chacha20_poly1305_draft_and_rfc_ossl102j.patch>
  - <https://raw.githubusercontent.com/cloudflare/sslconfig/master/patches/openssl__chacha20_poly1305_draft_and_rfc_ossl102g.patch>
  - <https://raw.githubusercontent.com/cloudflare/sslconfig/master/patches/openssl__chacha20_poly1305_draft_and_rfc_ossl102f.patch>
  - <https://github.com/cloudflare/sslconfig/issues/26>
  - <https://github.com/cloudflare/sslconfig/issues/32>
  - <https://github.com/cloudflare/sslconfig/issues/48>
  - <https://github.com/cloudflare/sslconfig/issues/51>
  - <https://github.com/cloudflare/sslconfig/issues/52>
  - <https://github.com/cloudflare/sslconfig/issues/57>
  - <https://github.com/cloudflare/sslconfig/issues/60>
  - <https://github.com/cloudflare/sslconfig/issues/78>
  - <https://blog.cloudflare.com/it-takes-two-to-chacha-poly/>
  - <https://news.ycombinator.com/item?id=11421114>
  - <https://raw.githubusercontent.com/google/boringssl/main/crypto/cipher/asm/chacha20_poly1305_x86_64.pl>
  - <https://raw.githubusercontent.com/google/boringssl/main/crypto/cipher/internal.h>
  - <https://raw.githubusercontent.com/google/boringssl/main/gen/crypto/chacha20_poly1305_x86_64-linux.S>
  - <https://github.com/google/boringssl/commits/main/crypto/cipher_extra/asm/chacha20_poly1305_x86_64.pl>
  - <https://github.com/openssl/openssl/tree/master/crypto/chacha/asm>
  - <https://github.com/openssl/openssl/tree/master/crypto/poly1305/asm>
  - <https://raw.githubusercontent.com/openssl/openssl/master/crypto/chacha/asm/chacha-x86_64.pl>
  - <https://raw.githubusercontent.com/openssl/openssl/master/crypto/poly1305/asm/poly1305-x86_64.pl>
  - <https://github.com/briansmith/ring/tree/main/crypto/cipher/asm>
  - <https://openssl-library.org/policies/releasestrat/index.html>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/cloudflare/sslconfig`) · [data/wave5/enrich/raw/github_com_cloudflare_sslconfig.json](../../../data/wave5/enrich/raw/github_com_cloudflare_sslconfig.json) (enrichment confidence 0.75)

</details>
