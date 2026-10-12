# TgCrypto (pyrogram/tgcrypto)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [AEAD and ciphers](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C` · `LGPL-3.0-or-later` · 🔴 abandoned

> Archived C extension for Python giving Pyrogram AES-256-IGE/CTR/CBC; replaces pure-Python pyaes, does not beat OpenSSL.

| | |
|---|---|
| **Beats** | OpenSSL AES-256-IGE / AES-256-CBC (no comparison found) |
| **Claimed result** | No numeric claim found. README says only 'designed to be portable, fast, easy to install and use' and 'Fast and Portable Cryptography Extension Library for Pyrogram'. The orchestrator's lead (41 vs 23 MB/s at 48-byte messages versus OpenSSL-based IGE) could not be located in any opened source. |
| **Workload** | No benchmark found: the README, the repository, the commit titles, the issue tracker and README revisions 95ff73c (v1.1.1), d6fbe3c (v1.0.2) and 5c2c7f3 contain no timing numbers and no OpenSSL comparison. |
| **Metric** | throughput |
| **Adoption** | 211 stars; archived by owner 2024-12-23; Pyrogram's optional accelerator (PyPI TgCrypto, fork pyrotgcrypto) |
| **Last commit** | 2024-12-23 |
| **Links** | [repository](https://github.com/pyrogram/tgcrypto) |

## Verdict

Nothing was measured: the repository, README, tests and commit history contain no timings and no OpenSSL or pyaes comparison. The only numbers are the third-party aesige PyPI README (no CPU named, x86_64, 1 KB per call): tgcrypto 14.8 us decrypt and 24.3 us encrypt against aesige's AES-NI IGE at 7.4 and 7.7 us, i.e. tgcrypto is 2-3.2x slower than hardware AES; aesige's GitHub homepage now returns 404.

## Use it when

- Maintaining an existing Pyrogram (or Pyrogram-fork) Telegram client on Python 3.7-3.11, where installing it replaces the pyaes fallback for MTProto IGE traffic and file transfers.
- You need AES-256-IGE as a single call from Python and accept LGPL-3.0-or-later linking terms.
- Platforms where prebuilt wheels exist for release 1.2.5 (Linux x86_64/i686, Windows, macOS x86_64/arm64/universal2, PyPy 3.7-3.9) and no compiler is available.

## Skip it when

- New projects: the repository was archived on 2024-12-23 and the README says it is no longer maintained or supported; the last PyPI release is 1.2.5 from 2022-11-11 with no cp312+ or Linux aarch64 wheels.
- Anything where side channels matter: T-table AES leaks key-dependent cache accesses, and the README says the implementations are 'for educational purposes only'.
- Bulk AES-CTR or AES-CBC: an AES-NI backed library will be faster; the third-party aesige package (Apache-2.0, AES-NI and ARM Crypto Extensions) reports tgcrypto 2-3.2x slower than itself on 1 KB IGE calls.
- Inputs of 4 GiB or more, or code that passes immutable or shared bytes objects as the CTR/CBC IV or state (see gotchas).
- Big-endian hosts: the block load/store macros byte-swap unconditionally with no endianness check, and CI only builds and tests little-endian targets.

## How it is fast

It moves AES out of Python into C: a portable 32-bit T-table AES (Te0-Te3/Td0-Td3 lookups, rounds written out inline) with the mode loops (IGE chaining, CTR counter increment, CBC) also in C. It releases the GIL around each call. There is no AES-NI, ARMv8 Crypto or bitsliced path, so the gain is only over interpreted Python, not over OpenSSL's hardware AES.

## Compared with alternatives

None of the catalogued aead-and-ciphers siblings (libaegis, chacha20poly1305-simd, Mbed TLS, Botan, intel-ipsec-mb) provide AES-IGE to Python; pick TgCrypto only when you are tied to Pyrogram's IGE/CTR/CBC API, and otherwise prefer an AES-NI backed library such as Botan or Mbed TLS for the same modes.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none at runtime (CPython or PyPy C API); building from the sdist needs setuptools, wheel and a C compiler |
| **Minimum toolchain** | Python 3.7+ (python_requires \~=3.7); wheels for CPython 3.7-3.11 and PyPy 3.7-3.9; no extra compiler flags are set in setup.py |
| **Platforms** | Little-endian targets (x86, x86-64, arm64); wheels for Linux x86_64/i686, Windows win32/amd64 and macOS x86_64/arm64/universal2; other platforms build from source |
| **Thread safety** | Each call expands its own key on the stack and releases the GIL during the C work, so concurrent calls with separate buffers are safe; CTR and CBC calls write into the IV (and CTR state) buffers you pass, so those must not be shared between threads. |
| **Drop-in for the baseline** | partial — it is a drop-in only for Pyrogram's own crypto layer (replacing pyaes); it is not an OpenSSL or pyca/cryptography API replacement, has no padding or AEAD, and supports only AES-256. |

## Gotchas

- Inputs of 4 GiB or more misbehave: the bindings pass the Py_ssize_t length to C functions that take uint32_t, so the C side allocates and processes length mod 2^32 bytes, while Py_BuildValue('y#', buf, data.len) then copies the full original length out of that smaller heap buffer (heap over-read or crash). malloc results are never checked for NULL either.
- CTR and CBC write the updated counter, stream position and chaining IV back into the caller's buffers through read-only 'y\*' views, including immutable bytes objects: the README and tests pass bytes(1) as the CTR state and rely on it being changed in place, so reusing a bytes constant as IV or state silently changes it.
- Py_buffer leaks: every argument-validation error path returns without PyBuffer_Release, and ctr256_encrypt/decrypt never release the state buffer even on success, so a bytearray passed there stays export-locked (resizing it raises BufferError) and its reference is leaked.
- Block input and output go through type-punned uint32_t loads and stores (GET/PUT) with an unconditional byte swap, so the code assumes a little-endian host and unaligned-access tolerance; the key is re-expanded on every call, so per-call cost dominates small messages.

## Known shortcomings

- No benchmark anywhere; it is a T-table AES with no AES-NI, and aesige's PyPI numbers show it 2-3.2x slower than AES-NI IGE; its real incumbent is pure-Python pyaes. Archived 2024-12-23.
- Enricher (code reading): tgcrypto.c truncates the Py_ssize_t length to uint32_t but Py_BuildValue copies the full length, a heap over-read at 4 GiB and above; malloc is unchecked; CTR and CBC write the IV and state back through read-only y\* buffer views; Py_buffer objects leak (CTR never releases state, error paths release nothing); GET/PUT byte-swap with no endian check.

## Caveats and trade-offs

No evidence that it beats OpenSSL. Lead not substantiated: no benchmark in README (checked current README and revisions 95ff73c, d6fbe3c, 5c2c7f3), commit titles, issues or source comments; a WebSearch for TgCrypto MB/s or OpenSSL comparisons found none. Its documented role (Pyrogram docs, WebSearch snippet only, readthedocs blocked) is to replace the much slower pure-Python PyAES fallback, so the realistic baseline is pyaes, not OpenSSL, and no numbers exist for that either. The source is a portable T-table AES, so beating OpenSSL's AES-NI based core on large buffers is implausible. Third-party package aesige (Apache-2.0, AES-NI / ARM Crypto Extensions, https://pypi.org/project/aesige/, read via the PyPI JSON API) reports tgcrypto at 14.8 us decrypt and 24.3 us encrypt for 1 KB versus 7.4 us and 7.7 us for aesige on x86_64, i.e. tgcrypto is 2-3.2x slower than a hardware-accelerated IGE (aesige author's own numbers, no CPU stated). Archived by the owner on 2024-12-23; README says the project is no longer maintained or supported. LGPL licence: the sidebar lists both LGPL-3.0 and GPL-3.0 texts; README says LGPLv3+.

Python C extension implementing AES-256-IGE (MTProto 2.0), AES-256-CTR and AES-256-CBC only. Inputs must be padded to a multiple of 16 bytes by the caller. Portable table-based AES (Te0/Td0 lookup tables in aes256.c, no AES-NI, ARM Crypto or other intrinsics found in the source), so it is not constant-time against cache attacks. README states the algorithm implementations are 'for educational purposes only'. Releases the GIL (commit 'Released the GIL', 2019-06-13).

## Maintenance

Archived 2024-12-23 and declared unmaintained, LGPL-3.0-or-later, with NIST and pyca vectors for CBC and CTR run by CI on Linux and macOS (tests skipped on Windows); usable as a legacy Pyrogram accelerator, but it carries an unfixed 4 GiB length-truncation over-read, in-place mutation of immutable IV/state buffers and buffer leaks, so it should not be adopted for new code.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification D, tier now D.
- **Tier reason:** No benchmark exists: the repo page and README give no timings and no OpenSSL comparison, and a WebSearch found no MB/s comparison; the only numbers anywhere are the third-party aesige PyPI page, which shows tgcrypto slower than an AES-NI IGE implementation.
- **Verifier notes:** Metadata confirmed: archived 2024-12-23 (last commit a8aee64 'Update README.md'), 211 stars, LGPL-3.0 plus GPL-3.0 texts. Shortcoming: no measurement at all; only third-party data (aesige) shows it 2-3.2x slower than an AES-NI IGE; real incumbent is pure-Python pyaes. Low notability; kept at D per keep-and-document rule.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-56 (wave 7 seed pass, 2026-10-13); enricher (seed pass, 2026-10-13)
- **Pages the verifier opened:**
  - <https://github.com/pyrogram/tgcrypto>
  - <https://github.com/pyrogram/tgcrypto/commits>
  - <https://pypi.org/pypi/aesige/json>
- **Sources the enricher read:**
  - <https://github.com/pyrogram/tgcrypto>
  - <https://raw.githubusercontent.com/pyrogram/tgcrypto/HEAD/README.md>
  - <https://raw.githubusercontent.com/pyrogram/tgcrypto/HEAD/setup.py>
  - <https://raw.githubusercontent.com/pyrogram/tgcrypto/HEAD/pyproject.toml>
  - <https://raw.githubusercontent.com/pyrogram/tgcrypto/HEAD/tox.ini>
  - <https://raw.githubusercontent.com/pyrogram/tgcrypto/HEAD/tgcrypto/tgcrypto.c>
  - <https://raw.githubusercontent.com/pyrogram/tgcrypto/HEAD/tgcrypto/aes256.c>
  - <https://raw.githubusercontent.com/pyrogram/tgcrypto/HEAD/tgcrypto/aes256.h>
  - <https://raw.githubusercontent.com/pyrogram/tgcrypto/HEAD/tgcrypto/ige256.c>
  - <https://raw.githubusercontent.com/pyrogram/tgcrypto/HEAD/tgcrypto/ctr256.c>
  - <https://raw.githubusercontent.com/pyrogram/tgcrypto/HEAD/tgcrypto/cbc256.c>
  - <https://github.com/pyrogram/tgcrypto/tree/master/.github/workflows>
  - <https://raw.githubusercontent.com/pyrogram/tgcrypto/HEAD/.github/workflows/wheels.yml>
  - <https://github.com/pyrogram/tgcrypto/tree/master/tests>
  - <https://raw.githubusercontent.com/pyrogram/tgcrypto/HEAD/tests/ige/test_ige.py>
  - <https://raw.githubusercontent.com/pyrogram/tgcrypto/HEAD/tests/ctr/test_ctr.py>
  - <https://raw.githubusercontent.com/pyrogram/tgcrypto/HEAD/tests/cbc/test_cbc.py>
  - <https://github.com/pyrogram/tgcrypto/issues?q=is%3Aissue>
  - <https://pypi.org/pypi/TgCrypto/json>
  - <https://pypi.org/pypi/aesige/json>
  - <https://github.com/xGaDinc/aesige>
  - WebSearch: tgcrypto pyaes speed benchmark Pyrogram (snippets from docs.pyrogram.org/topics/speedups and Pyrogram's crypto/aes.py fallback warning)
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/pyrogram/tgcrypto`) · [data/wave7/enrich/raw/github_com_pyrogram_tgcrypto.json](../../../data/wave7/enrich/raw/github_com_pyrogram_tgcrypto.json) (enrichment confidence 0.75)

</details>
