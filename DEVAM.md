# asaformn-edit — devam notu

Bu dosyayı yeni sohbete ver: "asaformn-edit reposunda kaldığımız yerden devam edelim, DEVAM.md'yi oku."

## Ne bu?
Ömer'in (edit adı: Asaf Orman) DaVinci Resolve'da kurgu yaptıran Claude skill'i. Ömer projeyi açar, seslendirmeyi timeline'a koyar; Claude seslendirmeye kelime kelime oturan kareleri, yazıları, fotoğrafları, sesleri seçilen stilde yerleştirir, ölçerek kontrol eder, dikey kesitleri çıkarır. Çekim görüntüsü yok.

- Yerel kopya: `/Volumes/SANDISK SSD/asaformn-edit` (git init yapıldı, henüz commit yok).
- GitHub: `asaformn/asaformn-edit` (public olacak, henüz push edilmedi). Ömer'in bilgisayarında skill adı **edit1** olacak (en son, kurulumda klasör ve `name` alanı edit1 yapılıp ZIP'lenecek).
- Önce oku: `README.md` (26 özellik ve kaynakları), `SKILL.md` (iş akışı), `stiller/asaformn-edit/STYLE.md`, `kurallar/ton-matrisi.md`, `kurallar/ses-miksi.md`, `vendor/README.md`.

## Kesinleşen kararlar
- Stil **asaformn-edit** (kalıcı ad, 25 Kasım): görünüş Lemo-Opuscar No.17 Sketchnote, hareketin tamamı No.18 Stick-figure Explainer; kalemle çizilme efekti yok. Renkler **Kanal Tipi** paleti (claude.ai'deki "Kanal Tipi" tasarım sistemi artifact'ı). Font **Shantell Sans** (Informal / Bouncy). ✓/✗ fonttan değil, çizilerek.
- Görseller: asaformn-edit animasyonları (şeffaf video), Ömer'in `kutuphane/` kartları ve fotoğrafları (sketchnote filtresiyle). İnternetten fotoğraf arama (Pexels/Unsplash) 25 Kasım'da çıkarıldı.
- Ses: seslendirme önde, efektler (sesler/kenney, glitch vb. yasak) altında, müzik sadece arada ve belli belirsiz. Tek master -14 LUFS / -1 dBTP (YouTube, Shorts, Reels, TikTok).
- Dikey kesitler 30–45 sn, kırpma yok (yeniden dizilir), en sıkı güvenli alan (üst %10, alt %22, sol %5, sağ %14). Kaç kesit: uzun videodan en vurucu 3–4 reels (Ömer'in kararı, 25 Kasım).
- Yavaşlatılan her klipte: Retime Process = Optical Flow, Motion Estimation = AI Speed Warp Better.
- Ömer tasarruf istiyor: işler mümkünse düşük modelli alt ajanlara (Haiku; zor işler Sonnet) verilsin.

## Durum
| # | Aşama | Durum |
|---|---|---|
| 1 | Repo iskeleti, vendor/ (9 repo, lisanslar) | ✅ |
| 2 | `scripts/kontrol.py` (siyah/beyaz başlangıç, flaş, donmuş an, LUFS, platform, güvenli alanlı kareler) | ✅ test edildi |
| 4 | `SKILL.md` iş akışı | ✅ (not: `_review.py` komutunun parametreleri düzeltilecek: `_review.py project.json --result run.json`) |
| 5 | asaformn-edit motoru (`motor/asaformn-edit/`: motor.js, render.mjs, sahneler/uyku-ornek.json) + `stiller/asaformn-edit/stil-karesi.png` | ✅ çalışıyor; stil karesini Ömer onayladı (bilinen eksikler aşağıda) |
| 3 | DaVinci köprüsü (`scripts/davinci/`: ses_bul, yerlestir, dikey_timeline, render + README) — Resolve 21.1.2 Studio, DaVinci MCP `run_script` ile (dosya metni + başa `PARAMS = {...}`) | ✅ (25 Kasım) Resolve'da "asaformn-edit TEST" projesinde (30 fps) canlı denendi: ses_bul, yerlestir (yavaş klipte Optical Flow + Speed Warp Better geri okundu), dikey_timeline (1080×1920), render (mp4 yazıldı) geçti. Not: run_script sandbox'ında `globals()`/`eval` yok. Hâlâ açık noktalar `scripts/davinci/README.md` sonunda (30 fps dışı timeline, farklı fps'li kaynak, kırpılmış ses). `dikey_timeline`'daki son iki küçük düzeltme (ses seviyesi taşıma, fps atlama) canlı yeniden denenmedi. Test medyası `test/` (gitignore'da). |
| 6 | Ömer'in Mac'inde kurulum (uçtan uca deneme ✅ 25 Kasım, aşağıda) (ffmpeg, WhisperX `npx @veedstudio/openedit-cli install-whisperx`, Node, Chrome), test projesinde uçtan uca deneme, GitHub push, edit1 ZIP | ⏳ |

## Motorla ilgili bilinen eksikler
- Kurulum: `cd motor/asaformn-edit && npm i playwright-core` (node_modules repoda yok); Chrome yolu render.mjs içinde, Mac için ayarlanacak.
- El ele tutuşma, zemin nabzı, ✓ işareti, oturma ve el sallama pozları yazıldı ama denenmedi.
- Şeffaf (alpha) modda marker gölgeleri kâğıt olmadığı için DaVinci'de daha açık görünür; düzeltilecek. (KYK denemesinde kâğıt üstünde göze batmadı.)
- Örnek sahnede ilk karelerde sahne küçük ve aşağıda kalıyor.
- ✅ (24 Kasım) Düzeltildi: `lookup` pozunda kollar dirsekten bükük; sağ alta yeni `meter` öğesi ("sleep pressure", hardal, %82 dolu); kahve mercan yerine koyu mürekkep (`C.m3`). Kalan küçük kusur: iki kol omuzda tek çizgi olarak çizildiği için orada üst üste biniyor; gösterge etiketi 9,4 sn civarında geliyor.

## Uçtan uca deneme (25 Kasım) — ✅ zincir çalışıyor
Ses: `/Volumes/SANDISK SSD/PROJECTS/KANLIDİVANE MERSİN/2-SOUND/1.BÖLÜM/Yenişehir Kyk Erkek Öğrenci Yurdu 2.m4a` (13,35 sn; o klasöre yazılmaz). Resolve: "asaformn-edit TEST" projesi, `KYK` timeline'ı. Sonuç: `test/render/kyk-render-2.mp4`.
1. Kelime zamanları: `scripts/kelime_zamanlari.py` (faster-whisper small, Türkçe) → `motor/asaformn-edit/sahneler/kyk-kelimeler.json`. Bulut için izinli alanlar: huggingface.co, cdn-lfs.hf.co, us.aws.cdn.hf.co, cas-server.xethub.hf.co, cas-bridge.xethub.hf.co (Ömer ekledi). Whisper özel adları yanlış duyuyor ("kanlı divane", "oburun"), metin elle düzeltilir.
2. Sahne: `sahneler/kanlidivane-kyk.json`, motorda yeni `D.obruk` ve `D.ev`. Öğeler kelime başlangıçlarına kilitli.
3. Render bulutta (Mac VM'de Chrome yok, indirilemiyor). Aktarım: PNG kareler → `tar | split -b 23M` → `device_commit_files` → Mac VM'de `cat | tar x` → ffmpeg ile PNG-MOV.
4. **ÖNEMLİ:** Resolve 21.1.2, ffmpeg'in ürettiği ProRes 4444'ün alfasını yok sayıyor (klip "Alpha mode" ne olursa olsun siyah). PNG-MOV ve QuickTime Animation (qtrle) alfayı doğru taşıyor. `render.mjs` artık `.mov` çıktısını PNG kodekiyle yazıyor.
5. `yerlestir.py`: V1 kâğıt (`test/kagit.png`) + V2 sahne → render 1080p mp4.
6. `kontrol.py` (Mac VM'de çalışır): flaş/donma GEÇTİ. KALDI: ses -18,8 LUFS ve -0,7 dBTP → mastering adımı (-14 LUFS / -1 dBTP) henüz yok. UYARI: baştaki 2 kare yalnız kâğıt (0,07 sn). Mac VM'deki ffmpeg 4.4 olduğu için `check.py` ve `look.py` çalışmıyor (6.1+ gerekiyor).

## Titreme düzeltmesi (25 Kasım) — ✅
- Ömer videonun çok titrediğini söyledi. Ölçüm: ardışık kareler arasındaki farkın ~%90'ı kalem boil'inden geliyordu (`BOIL` 60 fps'e göre yazılmıştı, 30 fps'te her karede değişiyordu, faz adımı da büyüktü).
- Düzeltme (`motor.js` başı): `BOIL_HZ=4` (fps'ten bağımsız, saniyede 4 değişim), `BOIL_STEP=.35` (eskisi 2.1). Ömer "çok çok az olsun" dedi, bu değerleri onayladı. STYLE.md'deki boil kuralı güncellendi.
- KYK sahnesi yeni ayarla yeniden render edildi (`test/kyk-sahne2-png.mov`), Resolve'da V2 klibi bununla değiştirildi.

## Sıradaki adım
- Ses mastering: render sonrası -14 LUFS / -1 dBTP (ffmpeg loudnorm iki geçiş ya da Fairlight). `kontrol.py` tekrar.
- Bu zinciri SKILL.md Adım 1–5'e işle (kelime_zamanlari.py, aktarım, PNG-MOV notu).
- Motor: Chrome yolunu Mac'e göre ayarla (render.mjs, şu an `/usr/bin/google-chrome`); sahne girişinde ilk karelerin boş kalmaması.
- Ömer `test/render/` altına "Yenişehir Kyk Erkek Öğrenci Yurdu.m4a" koymuştu (fark edilmedi, Kanlıdivane klasöründeki "…Yurdu 2.m4a" kullanıldı).
- TEST projesinde artık gereksiz olanlar: "TEST-eski" ve "ALFA-TEST" timeline'ları, `test/alfa/` ve `test/parca/` klasörleri (silme izni olmadan kaldırılmadı).

## Bekleyen sorular
- (Hepsi cevaplandı, 25 Kasım: stil adı **asaformn-edit**, reels sayısı 3–4, Pexels/Unsplash çıkarıldı. Klasörler `motor/asaformn-edit/` ve `stiller/asaformn-edit/` olarak yeniden adlandırıldı.)
