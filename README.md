# asaformn-edit

Claude'un DaVinci Resolve'da kurgu yapması için bir skill. Seslendirmeyi timeline'a koyarsın, bir stil seçersin; Claude konuşmaya oturan kareleri, yazıları, fotoğrafları ve geçişleri o stilde timeline'a dizer, sonra işi ölçerek kontrol eder.

> Durum: yapım aşamasında.

## Özellikler ve kaynakları

| # | Özellik | Kaynak repo | Lisans |
|---|---|---|---|
| 1 | Baştaki siyah/beyaz kareyi bul, uyar, kes | [latent-spaces/brag](https://github.com/latent-spaces/brag) | MIT |
| 2 | Kinetik yazı stili rehberi (kalın yazılar, HUD yazıları, geçiş kataloğu) | [tuzhechen2005/opus-video-skills](https://github.com/tuzhechen2005/opus-video-skills) | MIT |
| 3 | Kontrol döngüsü (iş bitince timeline'dan kare alıp hataları kontrol etme) | [tuzhechen2005/opus-video-skills](https://github.com/tuzhechen2005/opus-video-skills) | MIT |
| 4 | Ses seviyesi ölçer (LUFS ve tepe seviyesi, YouTube -14 LUFS kontrolü) | [echris6/motion-video-kit](https://github.com/echris6/motion-video-kit) | MIT |
| 5 | Donmuş an bulucu (hiçbir şeyin kıpırdamadığı anları bulur) | [echris6/motion-video-kit](https://github.com/echris6/motion-video-kit) | MIT |
| 6 | Ses efekti araçları (puanlama, yumuşatma, müziğe göre seviye ayarı) | [echris6/motion-video-kit](https://github.com/echris6/motion-video-kit) | MIT |
| 7 | Otomatik ses mastering (-14 LUFS ve tepe sınırlayıcı) | [AbubakrChan/product-launch-motion](https://github.com/AbubakrChan/product-launch-motion) | MIT |
| 8 | Kelimeye kilitli senkron (seslendirmedeki kelime anında kartı ekrana getirme) | [AbubakrChan/product-launch-motion](https://github.com/AbubakrChan/product-launch-motion) | MIT |
| 9 | Efekt doğrulama (efektin son render'da duyulup duyulmadığını ölçme) | [AbubakrChan/product-launch-motion](https://github.com/AbubakrChan/product-launch-motion) | MIT |
| 10 | Karar kaydı (her yaratıcı karar bir `DECISION:` satırı) | [AbubakrChan/product-launch-motion](https://github.com/AbubakrChan/product-launch-motion) | MIT |
| 11 | Önce plan, sonra edit (yönetmen planı ve 4 kare onayı) | [howseen-ai/claude-motion-design](https://github.com/howseen-ai/claude-motion-design) | MIT |
| 12 | Kesmeden dönüşüm (ortak öğeyle geçiş, daire taşması, şekil morph'u) | [AbubakrChan/product-launch-motion](https://github.com/AbubakrChan/product-launch-motion), [howseen-ai/claude-motion-design](https://github.com/howseen-ai/claude-motion-design) | MIT |
| 13 | 260 ses efekti ve her sesin kullanımını söyleyen analiz dosyası | [latent-spaces/brag](https://github.com/latent-spaces/brag) | MIT (sesler: [Kenney](https://kenney.nl), CC0) |
| 14 | ~~Ücretsiz materyal bulucu (fotoğraf, logo, ses efekti)~~ — çıkarıldı (25 Kasım): fotoğraflar internetten aranmaz, sadece `kutuphane/` kullanılır | [howseen-ai/claude-motion-design](https://github.com/howseen-ai/claude-motion-design) | MIT |
| 15 | Okuma süresi kontrolü (her yazı okunacak kadar ekranda kalıyor mu) | [lemomo-ai/lemo-opuscar](https://github.com/lemomo-ai/lemo-opuscar) | MIT |
| 16 | **asaformn-edit** stili: No.17 Sketchnote görünüşü + No.18 Stick-figure Explainer hareketi ([`stiller/asaformn-edit`](stiller/asaformn-edit/STYLE.md)) | [lemomo-ai/lemo-opuscar](https://github.com/lemomo-ai/lemo-opuscar) | CC BY-NC 4.0 (stil rehberi), MIT (motor kodu) |
| 17 | Teslim öncesi tam kontrol: rakam kontrolü (ekrandaki sayı seslendirmede geçiyor mu), yazı boyutu ve kontrastı, ses boşlukları, ölü kuyruk | [veedstudio/open-edit](https://github.com/veedstudio/open-edit) | Apache-2.0 |
| 18 | Ücretsiz ve yerel yazıya dökme (WhisperX, kelime kelime zaman damgası) — 8 numaranın motoru | [veedstudio/open-edit](https://github.com/veedstudio/open-edit) | Apache-2.0 |
| 19 | Kelime kelime altyazı (konuşmanın kırıldığı yerden bölme, en fazla 7 sn ve 2×42 karakter, söylenen kelimeyi vurgulama) | [veedstudio/open-edit](https://github.com/veedstudio/open-edit) | Apache-2.0 |
| 20 | Çeşitlilik denetimi (plandaki tekrar eden geçiş, hareket, ses ve sahne uzunluklarını bulur; son 3 videoyu hatırlar) | [tugrawork-creator/saas-motion-kit](https://github.com/tugrawork-creator/saas-motion-kit) | MIT |
| 21 | Ton matrisi (tona göre tempo, yay, kamera ve ses; asaformn-edit stiline uyarlandı, glitch ve benzeri yok) ([`kurallar/ton-matrisi.md`](kurallar/ton-matrisi.md)) | [tugrawork-creator/saas-motion-kit](https://github.com/tugrawork-creator/saas-motion-kit) | MIT |
| 22 | İnceleme sayfası (yerel HTML: adımlar, kontroller, timeline; klibe ya da altyazıya tıklayıp yazılan notu Claude'a verilecek talimata çevirir) | [kajisho5/ffmpeg-skill](https://github.com/kajisho5/ffmpeg-skill) | MIT |
| 23 | Platform arayüzü gölgesi (Shorts, Reels ve TikTok'un kendi butonlarının kapladığı alanı kontrol karelerinde gösterir) | [kajisho5/ffmpeg-skill](https://github.com/kajisho5/ffmpeg-skill) | MIT |
| 24 | Platform uygunluk kontrolü (YouTube, Shorts, Reels, TikTok kuralları; GEÇTİ/UYARI/KALDI ve düzeltme; ses kesintisi taraması) | [kajisho5/ffmpeg-skill](https://github.com/kajisho5/ffmpeg-skill) | MIT |
| 25 | Otomatik YouTube bölümleri (duraklama ve sahne değişiminden öneri, transkriptle adlandırma) | [kajisho5/ffmpeg-skill](https://github.com/kajisho5/ffmpeg-skill) | MIT |
| 26 | **Uzun videodan dikey kesitler:** uzun videodan kendi başına ayakta duran anları seçer, her biri için 1080×1920 ayrı timeline kurar, grafikleri dikey düzene göre yeniden yerleştirir (kırpmaz), üç platformun da güvenli alanına uyan tek dikey video çıkarır; kesitler 30–45 sn, ses -14 LUFS / -1 dBTP (üç platform için tek master) | 22–24 + 19 numaraların birleşimi | MIT |

## Lisans

Bu repodaki kod MIT lisanslıdır; open-edit'ten alınan parçalar Apache-2.0 lisansını ve NOTICE dosyasını korur. `stiller/asaformn-edit/` altındaki stil rehberi, Lemo-Opuscar'ın ("Lemo-Opuscar by Lemomo (LemoLab)", https://github.com/lemomo-ai/lemo-opuscar) Sketchnote ve Stick-figure Explainer stillerinden uyarlanmış ve değiştirilmiştir; [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/) lisanslıdır. Bu skill ile yapılan videolar, ticari olanlar dahil, yapanındır.
