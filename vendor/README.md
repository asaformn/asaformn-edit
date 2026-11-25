# vendor/ — başka repolardan alınan parçalar

Bu klasördeki dosyalar aşağıdaki repolardan kopyalandı. Her alt klasörde kaynağın kendi lisans dosyası durur. asaformn-edit'in kendi scriptleri (`scripts/`) bunları çağırır ya da uyarlar; değişiklikler kendi dosyalarımızda yapılır, buradaki kopyalar mümkün olduğunca orijinal bırakılır.

| Klasör | Kaynak (kopyalanan sürüm) | Lisans | Kullanılan özellik (README numarası) |
|---|---|---|---|
| `brag/` | [latent-spaces/brag](https://github.com/latent-spaces/brag) @ `0637943` | MIT | 1 (fikir), 13 (ses kütüphanesi `sesler/kenney/` altında) |
| `opus-video-skills/` | [tuzhechen2005/opus-video-skills](https://github.com/tuzhechen2005/opus-video-skills) @ `dafed5b` | MIT | 2 (`kinetic-style-guide.md`), 3 (`render-review-loop.mjs`) |
| `motion-video-kit/` | [echris6/motion-video-kit](https://github.com/echris6/motion-video-kit) @ `e4b1c00` | MIT | 4 (`loudness.sh`), 5 (`frozen-time.sh`), 6 (`sfx-candidates.py`, `soften-sfx.sh`, `solve-sfx-gains.py`), 3 (`contact-sheet.sh`) |
| `product-launch-motion/` | [AbubakrChan/product-launch-motion](https://github.com/AbubakrChan/product-launch-motion) @ `edbfb10` | MIT (NOTICE'a bakınız) | 7 (`master.sh`), 8 (`word-timings.mjs`, `03-word-locked-sync.md`), 9 (`verify-cue.sh`), 6 (`level-sfx.mjs`) |
| `claude-motion-design/` | [howseen-ai/claude-motion-design](https://github.com/howseen-ai/claude-motion-design) @ `3d90d34` | MIT | 11, 12 (`motion-design-SKILL.md`), 14 (`mixkit_sfx_search.py`, `svgl_logos.py`) |
| `lemo-opuscar/` | [lemomo-ai/lemo-opuscar](https://github.com/lemomo-ai/lemo-opuscar) @ `8ca0dd8` | Kod MIT; stil rehberleri CC BY-NC 4.0 | 15 (`readcheck.mjs`), 16 (`engines/stick-explainer`, `engines/sketchnote`: Defter Adam motorunun temeli) |
| `open-edit/` | [veedstudio/open-edit](https://github.com/veedstudio/open-edit) @ `9dc3ca0` | Apache-2.0 | 17, 18, 19 (yayınlanmış CLI `npx @veedstudio/openedit-cli` ile çağrılır; kod kopyalanmadı) |
| `saas-motion-kit/` | [tugrawork-creator/saas-motion-kit](https://github.com/tugrawork-creator/saas-motion-kit) @ `bc7a414` | MIT | 20 (`variety_audit.py`, `history_report.py`, `variety-rules.md`, `STORYBOARD.md`), 21 (`tone-matrix.md`, uyarlaması `kurallar/ton-matrisi.md`) |
| `ffmpeg-skill/` | [kajisho5/ffmpeg-skill](https://github.com/kajisho5/ffmpeg-skill) @ `c7dad34` | MIT | 22 (`_review.py`), 23 (`look.py --safe`), 24 (`check.py`), 25 (`metadata.py --auto-chapters`) |

Lemo-Opuscar motorları yalnızca kod olarak alındı: demo seslendirmeleri, müzik örnekleri, Clawd ve demo filmler alınmadı. Lemo-Opuscar'ın stil rehberleri (`STYLE.md`) kopyalanmadı; Defter Adam rehberi kendi kelimelerimizle yazıldı (`stiller/defter-adam/STYLE.md`).
