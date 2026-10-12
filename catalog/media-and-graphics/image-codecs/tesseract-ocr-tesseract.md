# Tesseract

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Classic CPU OCR engine (LSTM line recognizer); with one process per core it out-throughputs single-stream GPU EasyOCR.

| | |
|---|---|
| **Beats** | EasyOCR (PyTorch CRAFT+CRNN, run on GPU with batch_size 16) |
| **Claimed result** | kvenanzi/ocr leaderboard pages/s vs EasyOCR: 3.47 vs 1.11 on G4 (3.1x derived) is tail-dominated; per-track G4 books 7.39 vs 0.69 but stress 1.22 vs 1.26; EasyOCR faster per page on G4, A100 and L4; PaddleOCR 3 faster (4.13 pages/s on G4). |
| **Workload** | OCR throughput in pages per second (total pages divided by summed batch-pass wall time) over the standard profile (215 pages: 50 historical book pages, 50 olmOCR-bench document pages, 60 IAM handwriting lines, 5 synthetic stress pages at 11 degradation levels = 55) on five Colab runtime types. Tesseract 5.3.4 (distro package via pytesseract, LSTM --oem 1 --psm 3, eng+fra+deu+lat) runs one process per page across all vCPUs with OMP_THREAD_LIMIT=1; EasyOCR 1.7.2 (torch 2.11.0+cu130, CRAFT+CRNN, readtext batch_size=16) runs one page at a time in a single process, on the GPU on GPU runtimes and on the host CPU on the TPU VM. |
| **Metric** | throughput |
| **Hardware** | Google Colab runtimes, CPU models from each run's env.json: G4 = NVIDIA RTX PRO 6000 Blackwell Server Edition with AMD EPYC 9B45, 48 vCPU, 176.9 GB RAM; A100-40GB with Intel Xeon CPU @ 2.20GHz, 12 vCPU; L4 with Intel Xeon CPU @ 2.20GHz, 12 vCPU; T4 with Intel Xeon CPU @ 2.00GHz, 8 vCPU; TPU-v6e-1 VM host AMD EPYC 9B14, 44 vCPU (classic engines run on the host CPU). |
| **Adoption** | 76.9k stars |
| **Last commit** | 2026-10-10 |
| **Links** | [repository](https://github.com/tesseract-ocr/tesseract) · [benchmark](https://github.com/kvenanzi/ocr/blob/main/results/LEADERBOARD.md) |

## Verdict

In the single-author kvenanzi/ocr leaderboard (215-page standard profile, Google Colab), distro Tesseract 5.3.4 via pytesseract (LSTM, eng+fra+deu+lat, one process per page across all vCPUs) reached 3.47 pages/s on G4 (AMD EPYC 9B45, 48 vCPU) against 1.11 for EasyOCR 1.7.2 on the RTX PRO 6000 GPU, and 0.68-0.82 vs 0.34-0.49 on T4, L4 and A100, and 2.28 vs 0.20 on the TPU-v6e host CPU; compiler and build flags are not stated. Per track on G4 the win is books 7.39 vs 0.69 and docs 5.27 vs 0.66 pages/s, while EasyOCR is slightly faster on the stress track (1.26 vs 1.22).

## Use it when

- Bulk OCR of clean printed pages (books, reports) on CPU-only machines, run as one single-threaded process per core with OMP_THREAD_LIMIT=1
- Historical printed books in German, French or English, where it scored 0.4-3.7% CER in the same leaderboard, close to large OCR VLMs
- Deployments that cannot ship a GPU, PyTorch or a VLM runtime and need a small native C/C++ library with Apache-2.0 licensing
- Pipelines that need word boxes or hOCR/ALTO/PDF text layers rather than Markdown

## Skip it when

- Handwriting: 56.1% CER on the IAM handwriting track, against 2.0% for dots.mocr
- Noisy, rotated or phone-photo scans: on the stress ladder CER jumps to 55.5% under noise and 81.9% at 8 degrees of rotation, and stress pages dominated its wall time
- Multi-column layouts and tables: it reads in raster order and passed 0.0% of the olmOCR-bench table tests
- Single-page interactive latency on a GPU box: GPU EasyOCR had a lower median per-track latency on G4, A100 and L4 in the same runs
- Maximum CPU-or-GPU throughput: PaddleOCR 3 (4.13 pages/s) and PaddleOCR-VL 1.6 (5.84 pages/s) beat it on the same G4 runtime

## How it is fast

The LSTM forward pass runs on 8-bit integer weights through SIMD matrix-vector kernels (IntSimdMatrix: AVX2, SSE, NEON and RVV variants) and float dot products (AVX, AVX-512F, FMA, SSE, NEON), picked at runtime by simddetect.cpp (the dotproduct variable defaults to auto). The CMake build uses float rather than double for the LSTM by default (FAST_FLOAT ON). The measured win over EasyOCR comes mostly from the deployment pattern, not the kernels: one single-threaded Tesseract process per page across every vCPU (OMP_THREAD_LIMIT=1), which is the batch setup Tesseract's FAQ recommends, against EasyOCR reading one page at a time on one GPU.

## Compared with alternatives

No OCR entry is catalogued yet; the image-codecs siblings (libjpeg-turbo, QOI, fpng and others) decode or encode images rather than read text, so pick Tesseract only when the job is text extraction on CPU.

## Integration

| | |
|---|---|
| **Form** | shared lib (libtesseract) plus CLI; static build possible |
| **Dependencies** | Leptonica 1.80 or newer (image I/O); optional libarchive and libcurl; per-language traineddata files (tessdata, tessdata_fast or tessdata_best) |
| **Minimum toolchain** | C++17 (CMake 3.22+, switches to C++20 when the compiler supports it); autotools build also available |
| **Platforms** | x86/x86-64 with runtime-dispatched SSE4.1, AVX, AVX2, FMA and AVX-512F kernels; ARM NEON; RISC-V RVV; generic fallback elsewhere |
| **Thread safety** | Not documented in the repository. The FAQ recommends one Tesseract process per CPU core with OMP_THREAD_LIMIT=1 for batch work; wrappers such as iText pdfOCR document one engine instance per thread; reusing one TessBaseAPI object across images can give inconsistent results unless ClearAdaptiveClassifier() is called |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw behind the throughput numbers: each track (50-60 pages) is smaller than one Tesseract batch (2 x workers, 96 on G4), so each track is one parallel map whose wall time is set by the slowest page. The stress track alone took 44.9 of 62.0 s on G4 (stress 1.22 vs EasyOCR 1.26 pages/s, books 7.39 vs 0.69), 146.5 of 264.0 s on A100 and 70.4 of 94.1 s on the TPU host, so the headline pages/s mostly measures a few slow degraded pages (inferred from the per-track timing in status.json; per-page times are not recorded).
- Not like-for-like: Tesseract ran 8 to 48 processes in parallel against EasyOCR's single stream, and the Tesseract latency pass timed only the first 8 pages per track while EasyOCR's latency covers every page. Each pytesseract call also starts a fresh process that reloads eng+fra+deu+lat, which inflates Tesseract's single-page latency.
- Builds with OpenMP use up to four threads per page; running many processes without OMP_THREAD_LIMIT=1 oversubscribes cores (issue #1662 thread: removing OpenMP made one multithreaded app about 33% faster). CMake now defaults OPENMP_BUILD to OFF.
- Speed depends heavily on the model set: tessdoc Benchmarks.md shows tessdata_best 6.20 s vs tessdata_fast 2.12 s on one image with 5.0.1, and 4.1.3 without AVX at 37.6 s, so a distro build or model choice can swing results several-fold.

## Known shortcomings

- kvenanzi/ocr leaderboard (0-star single-author harness, distro Tesseract 5.3.4, flags unstated) compares unequal setups: Tesseract runs one page per process on every vCPU (48 on G4) while EasyOCR does one page at a time on one GPU; single-page latency favours EasyOCR on G4 (0.90 vs 1.38 s), A100 and L4, and EasyOCR is slightly faster on the stress track; TPU-host rows mix two runs. Slower than PaddleOCR 3 and PaddleOCR-VL; EasyOCR is not a real incumbent; OCR is a loose fit for image-codecs.
- Enricher: each leaderboard track has 50-60 pages, fewer than one batch (2 x workers = 96 on G4), so a track's wall time is set by its slowest pages; the stress track alone takes 44.9 of 62.0 s on G4, 146.5 of 264.0 s on A100 and 70.4 of 94.1 s on the TPU host, so the headline pages/s mostly measures a few slow degraded pages (per-track on G4: books 7.39 vs 0.69, stress 1.22 vs EasyOCR 1.26). The latency pass times only the first 8 pages per track for Tesseract vs all pages for EasyOCR; pytesseract reloads eng+fra+deu+lat on every page. PaddleOCR 3 is faster on the same leaderboard (4.13 vs 3.47 pages/s on G4).

## Caveats and trade-offs

Third-party, single-author harness (kvenanzi/ocr, 0 stars, 48 commits, no repository license shown, earliest runs dated 2026-10-02), not peer reviewed and not a well-known suite. The speed rows are not like-for-like: Tesseract OCRs pages in parallel across every vCPU (48 workers on G4, 44 on the TPU host, 12 on A100/L4, 8 on T4) while EasyOCR processes pages one at a time on one GPU, so the win comes from page-level process parallelism. On single-page latency (p50 from leaderboard hardware.csv) GPU EasyOCR is faster on three of four GPU runtimes: G4 0.90 s vs 1.38 s, A100 2.07 s vs 2.92 s, L4 2.27 s vs 2.92 s; Tesseract wins only on T4 (2.69 s vs 3.31 s) and the TPU host CPU (1.89 s vs 5.92 s). On G4 the per-track throughput win is concentrated in books (7.39 vs 0.69 pages/s) and docs (5.27 vs 0.66); on the degraded stress track EasyOCR is slightly faster (1.264 vs 1.224 pages/s). The TPU-host Tesseract and EasyOCR rows come from two different runs (20261004-205730 and 20261005-140416, same EPYC 9B14 host type). Tesseract tested is the distro 5.3.4 build, not current main; build flags and compiler are not stated, so this is not tier A. Standard profile is about 215 pages and the README notes small samples. Tesseract loses throughput to PaddleOCR 3 (4.13 vs 3.47 pages/s on G4, and also on T4, L4 and A100), PaddleOCR-VL 1.6 (5.84 on G4) and OvisOCR2 (3.66 on G4), and to docTR on A100 (1.03 vs 0.81). Accuracy context from the same page: Tesseract 67.8% overall vs EasyOCR 60.4%, but 56.1% CER on handwriting. The project's own tessdoc Benchmarks.md (https://github.com/tesseract-ocr/tessdoc/blob/main/Benchmarks.md) only compares Tesseract versions and build flags on one image on Windows 10, VS 2019, i7-10750H (e.g. tessdata_best: 4.1.3 without AVX 37.6052 s, with AVX 12.7300 s, 5.0.1 6.1981 s, 5.0.1 OpenMP 3.4590 s), and shows 3.05 with the legacy engine faster than 5.0.1 on the plain tessdata model (2.4713 s vs 2.9107 s), so it gives no external-baseline win. EasyOCR is not a recognized incumbent for Tesseract (Tesseract is itself the incumbent classic OCR engine). Category image-codecs is the closest wave-10 category; OCR is image analysis, not a codec. [retier] Track smaller than one batch (2 x workers = 96 on G4), stress track dominates wall time; 8-48 processes vs one GPU stream; latency pass times first 8 pages per track for Tesseract only; pytesseract reloads eng+fra+deu+lat per page; distro Tesseract 5.3.4, flags unstated; 0-star single-author harness.

CPU-only engine, no GPU needed. Much lower accuracy than modern OCR VLMs in the same leaderboard (67.8% mean accuracy vs 94.7% for the top engine; handwriting CER 56.1%, stress-track CER 19.0%). Classic engines read in raster order and interleave columns on multi-column pages. Needs per-language traineddata files; scales by running many single-threaded processes.

## Maintenance

Actively maintained (latest release 5.5.3, last commit 2026-10-10), Apache-2.0 and widely packaged, so copyable; the benchmarked 5.3.4 distro build is several releases behind current main.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** LEADERBOARD.md's 'Speed and cost by hardware' table shows Tesseract 5 vs EasyOCR pages/s exactly as claimed (3.47 vs 1.11 G4, 0.81 vs 0.49 A100-40GB, 0.82 vs 0.45 L4, 0.68 vs 0.34 T4, 2.28 vs 0.20 TPU-v6e-1). Harness code (ocrbench/engines/tesseract.py, easyocr_engine.py, worker.py) and CPU models (per-run env.json) are public, but Tesseract is an apt package (5.3.4 per status.json) with no compiler or flags stated, and the harness is a 0-star single-author repo rather than a well-known suite, so C, not A or B.
- **Verifier notes:** Numbers match the leaderboard exactly and the derived ratios (3.1x G4, 1.65x A100, 1.8x L4, 2.0x T4, 11.4x TPU host) are correct, so tier C stands. Main shortcomings to record: unequal parallelism (Tesseract multi-process across all vCPUs vs EasyOCR one page at a time on one GPU; EasyOCR has lower single-page latency on G4, A100 and L4), unknown 0-star harness, distro Tesseract 5.3.4 with unstated build flags, slower than PaddleOCR 3 and PaddleOCR-VL, and wrong category (OCR, not a codec). Metadata checked on github.com: Apache-2.0, 76.9k stars, not archived or a fork, last commit 2026-10-10.
- **Fields the verifier corrected:** `hardware`, `workload`, `caveats`, `claimed_speedup`
- **Shortcomings recorded by:** verifier batch-119 (wave 10); enricher w10 pair-032
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/kvenanzi/ocr/HEAD/results/LEADERBOARD.md>
  - <https://raw.githubusercontent.com/kvenanzi/ocr/HEAD/README.md>
  - <https://raw.githubusercontent.com/kvenanzi/ocr/HEAD/ocrbench/engines/tesseract.py>
  - <https://raw.githubusercontent.com/kvenanzi/ocr/HEAD/ocrbench/engines/easyocr_engine.py>
  - <https://raw.githubusercontent.com/kvenanzi/ocr/HEAD/ocrbench/engines/base.py>
  - <https://raw.githubusercontent.com/kvenanzi/ocr/HEAD/ocrbench/engines/_parallel.py>
  - <https://raw.githubusercontent.com/kvenanzi/ocr/HEAD/ocrbench/worker.py>
  - <https://raw.githubusercontent.com/kvenanzi/ocr/HEAD/configs/engines.yaml>
  - <https://raw.githubusercontent.com/kvenanzi/ocr/HEAD/results/hardware.csv>
  - <https://raw.githubusercontent.com/kvenanzi/ocr/HEAD/results/leaderboard.csv>
  - <https://raw.githubusercontent.com/kvenanzi/ocr/HEAD/results/runs/20261004-163611_G4_standard/env.json>
  - <https://raw.githubusercontent.com/kvenanzi/ocr/HEAD/results/runs/20261004-163611_G4_standard/tesseract/status.json>
  - <https://raw.githubusercontent.com/kvenanzi/ocr/HEAD/results/runs/20261004-163611_G4_standard/tesseract/job.json>
  - <https://raw.githubusercontent.com/kvenanzi/ocr/HEAD/results/runs/20261004-163611_G4_standard/easyocr/status.json>
  - <https://raw.githubusercontent.com/kvenanzi/ocr/HEAD/results/runs/20261004-205730_TPU-v6e-1_standard/env.json>
  - <https://raw.githubusercontent.com/kvenanzi/ocr/HEAD/results/runs/20261004-205730_TPU-v6e-1_standard/tesseract/status.json>
  - <https://raw.githubusercontent.com/kvenanzi/ocr/HEAD/results/runs/20261005-140416_TPU-v6e-1_standard/env.json>
  - <https://raw.githubusercontent.com/kvenanzi/ocr/HEAD/results/runs/20261002-195503_A100-40GB_standard/env.json>
  - <https://raw.githubusercontent.com/kvenanzi/ocr/HEAD/results/runs/20261002-195503_A100-40GB_standard/tesseract/status.json>
  - <https://raw.githubusercontent.com/kvenanzi/ocr/HEAD/results/runs/20261002-231955_L4_standard/env.json>
  - <https://raw.githubusercontent.com/kvenanzi/ocr/HEAD/results/runs/20261003-163357_T4_standard/env.json>
  - <https://raw.githubusercontent.com/kvenanzi/ocr/HEAD/results/runs/20261003-163357_T4_standard/tesseract/status.json>
  - <https://github.com/kvenanzi/ocr>
  - <https://github.com/kvenanzi/ocr/tree/main/results/runs/20261004-163611_G4_standard>
  - <https://github.com/kvenanzi/ocr/tree/main/results/runs/20261004-163611_G4_standard/tesseract>
  - <https://github.com/tesseract-ocr/tesseract>
  - <https://github.com/tesseract-ocr/tesseract/commits/main>
  - <https://raw.githubusercontent.com/tesseract-ocr/tessdoc/HEAD/Benchmarks.md>
- **Sources the enricher read:**
  - <https://github.com/tesseract-ocr/tesseract>
  - <https://raw.githubusercontent.com/tesseract-ocr/tesseract/HEAD/README.md>
  - <https://raw.githubusercontent.com/tesseract-ocr/tesseract/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/tesseract-ocr/tesseract/HEAD/configure.ac>
  - <https://raw.githubusercontent.com/tesseract-ocr/tesseract/HEAD/ChangeLog>
  - <https://raw.githubusercontent.com/tesseract-ocr/tesseract/HEAD/src/arch/intsimdmatrix.h>
  - <https://raw.githubusercontent.com/tesseract-ocr/tesseract/HEAD/src/arch/intsimdmatrixavx2.cpp>
  - <https://raw.githubusercontent.com/tesseract-ocr/tesseract/HEAD/src/arch/simddetect.cpp>
  - <https://github.com/tesseract-ocr/tesseract/tree/main/src/arch>
  - <https://github.com/tesseract-ocr/tesseract/releases>
  - <https://github.com/tesseract-ocr/tesseract/issues/1662>
  - <https://github.com/tesseract-ocr/tesseract/wiki/FAQ/24e1b8de97a465dc56609a5ad1accbb30f9ce28d>
  - <https://raw.githubusercontent.com/tesseract-ocr/tessdoc/HEAD/Benchmarks.md>
  - <https://raw.githubusercontent.com/kvenanzi/ocr/HEAD/README.md>
  - <https://raw.githubusercontent.com/kvenanzi/ocr/HEAD/results/LEADERBOARD.md>
  - <https://raw.githubusercontent.com/kvenanzi/ocr/HEAD/results/hardware.csv>
  - <https://raw.githubusercontent.com/kvenanzi/ocr/HEAD/configs/engines.yaml>
  - <https://raw.githubusercontent.com/kvenanzi/ocr/HEAD/ocrbench/worker.py>
  - <https://raw.githubusercontent.com/kvenanzi/ocr/HEAD/ocrbench/engines/tesseract.py>
  - <https://raw.githubusercontent.com/kvenanzi/ocr/HEAD/ocrbench/engines/easyocr_engine.py>
  - <https://raw.githubusercontent.com/kvenanzi/ocr/HEAD/ocrbench/engines/_parallel.py>
  - <https://raw.githubusercontent.com/kvenanzi/ocr/HEAD/ocrbench/engines/base.py>
  - <https://raw.githubusercontent.com/kvenanzi/ocr/HEAD/results/runs/20261004-163611_G4_standard/tesseract/status.json>
  - <https://raw.githubusercontent.com/kvenanzi/ocr/HEAD/results/runs/20261004-163611_G4_standard/tesseract/job.json>
  - <https://raw.githubusercontent.com/kvenanzi/ocr/HEAD/results/runs/20261004-163611_G4_standard/easyocr/status.json>
  - <https://raw.githubusercontent.com/kvenanzi/ocr/HEAD/results/runs/20261004-163611_G4_standard/easyocr/job.json>
  - <https://raw.githubusercontent.com/kvenanzi/ocr/HEAD/results/runs/20261004-163611_G4_standard/tesseract/stress/preds.jsonl>
  - <https://raw.githubusercontent.com/kvenanzi/ocr/HEAD/results/runs/20261002-195503_A100-40GB_standard/tesseract/status.json>
  - <https://raw.githubusercontent.com/kvenanzi/ocr/HEAD/results/runs/20261004-205730_TPU-v6e-1_standard/tesseract/status.json>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/tesseract-ocr/tesseract`) · [data/wave10/enrich/raw/github_com_tesseract_ocr_tesseract.json](../../../data/wave10/enrich/raw/github_com_tesseract_ocr_tesseract.json) (enrichment confidence 0.6)

</details>
