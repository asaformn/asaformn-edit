---
name: asaformn-edit
description: DaVinci Resolve'da timeline'daki seslendirmeye oturan kareleri, yazıları, fotoğrafları ve geçişleri seçilen stilde yerleştirir, kontrol eder ve dikey kesitler çıkarır.
---

# asaformn-edit

Kullanıcı bir DaVinci Resolve projesi açar, seslendirmeyi (AI sesi) timeline'a koyar ve "kanal stiliyle kareleri getir" gibi bir istek verir. Bu skill'in işi, seslendirmenin her kelimesine oturan görselleri kurmak, işi ölçerek kontrol etmek ve kullanıcı onayladıktan sonra dikey kesitleri çıkarmaktır.

Bu videolarda çekilmiş görüntü yoktur. Görseller şunlardan oluşur:

- Seçilen stilde animasyonlu kareler. Varsayılan stil `stiller/asaformn-edit` (sketchnote görünüşü, çöp adam hareketi, Kanal Tipi paleti, Shantell Sans fontu).
- Kullanıcının kendi verdiği fotoğraflar (`kutuphane/`). Bunlar sketchnote filtresinden geçirilir. İnternetten fotoğraf aranmaz.
- Bazen kullanıcının kendi kartları ve animasyonları (`kutuphane/`).

## Araçlar ve dosyalar

- DaVinci Resolve ile konuşma: DaVinci MCP aracındaki `run_script` (Resolve scripting API).
- Yardımcı scriptler (planlandı, henüz yazılmadı): `scripts/davinci/ses_bul.py`, `scripts/davinci/yerlestir.py`, `scripts/davinci/dikey_timeline.py`, `scripts/davinci/render.py`, `scripts/kontrol.py`.
- Kelime zamanlaması: `npx @veedstudio/openedit-cli transcribe --provider whisperx` (özellik 18).
- Stil motoru (planlandı): `motor/`. asaformn-edit sahneleri bu motorla şeffaf arka planlı (alpha) video olarak üretilir.
- Ton ve ses kuralları: `kurallar/ton-matrisi.md`, `kurallar/ses-miksi.md`, `sesler/kenney/` altındaki sfx analizi.
- Stil rehberi: `stiller/asaformn-edit/STYLE.md`.
- Kullanıcının kart kütüphanesi: `kutuphane/` (ayrıntı için `kutuphane/README.md` ve `kutuphane/katalog.md`).

Özellik numaraları (1–26) `README.md` tablosundaki numaralardır. Bu metinde her adımın yanında hangi özelliğin kullanıldığı yazılıdır.

## Kurallar

1. **Ekrana sayı yazılmaz,** seslendirmede söylenmeyen bir rakam hiçbir karede yer almaz.
2. **Yavaşlatılmış her klip** DaVinci'de Retime and Scaling ile işlenir: Retime Process = Optical Flow, Motion Estimation = AI Speed Warp Better. Kullanıcıya sormadan, her klipte uygulanır.
3. **Her yaratıcı karar** bir `DECISION:` satırıyla kaydedilir. Kullanıcı bu satırları geri çevirebilir (özellik 10).
4. **Müzik nadir ve çok kısıktır.** Seslendirme her zaman en önde kalır (`kurallar/ses-miksi.md`).
5. **Son ses seviyesi:** -14 LUFS entegre, -1 dBTP tepe. Uzun video ve dikey kesitler için aynı master (özellik 7).
6. **Tona uymayan sesler ve geçişler kullanılmaz.** Glitch, VHS, silme (wipe), sayfa çevirme, zoom-blur ve `casino/*` klasörü asaformn-edit stilinde yoktur (`kurallar/ton-matrisi.md`).
7. **Görünüş tondan bağımsızdır.** Renkler, font ve çizgi her zaman asaformn-edit stilidir. Ton yalnızca tempoyu, yayı, kamerayı ve sesi belirler.

## Adım 0: Başlamadan

Her video ve her bölüm için kayıt tutulur:

- **Brief kaydı:** video uzunluğu (dakika), platform (YouTube, dikey ya da ikisi) ve kullanıcının kendi cümleleri. Kullanıcının kelimeleri olduğu gibi saklanır.
- **Ton cümlesi,** videonun başında ve her bölümün başında bir kez yazılır (özellik 21):

  > "Şunu ___ tonda söylemek istiyorum, izleyici ___ hissetsin."

  Ton seçenekleri: sakin, güvenilir, sıcak/insani, oyunbaz, teknik, gizemli/açılış, kutlama, acil. Her tonun tempo, yay, kamera ve ses karşılığı `kurallar/ton-matrisi.md` dosyasındadır.

Ton cümlesi eksikse işe başlanmaz. Önce kullanıcıya sorulur.

## Adım 1: Sesi anlama (özellik 18, 8)

1. Seslendirme dosyası WhisperX ile yazıya dökülür:
   `npx @veedstudio/openedit-cli transcribe --provider whisperx`
2. Her kelimenin başlangıç ve bitiş zamanı alınır. Bu zamanlar timeline'ın kare ızgarasına yuvarlanır.
3. Cümle ve konuşma aralıkları çıkarılır. Duraklar, bölüm sınırları ve kelime anları buradan belirlenir.

Bu zamanlar bundan sonraki bütün yerleştirmelerin tek kaynağıdır.

## Adım 2: Plan (özellik 11, 20, 10)

Önce plan yapılır, sonra kurgu. Plan bir yönetmen planıdır, yani bir storyboard defteridir. Tablo `vendor/saas-motion-kit/STORYBOARD.md` biçimini izler ve en az şu sütunları içerir:

| id | start | end | words | visual | entrance | transition_out | tone | sound |
|---|---|---|---|---|---|---|---|---|

Sonra çeşitlilik denetimi çalışır:

```
python3 vendor/saas-motion-kit/variety_audit.py PLAN.md --history ~/.asaformn-edit/history.json
```

- Denetim tekrar eden geçiş, hareket, ses ve sahne uzunluklarını bulur. Son üç videoyu hatırlar.
- Tekrar varsa ya değiştirilir ya da bilinçli bir tekrar olduğu `motif:` etiketiyle işaretlenir.
- Her yaratıcı karar için bir `DECISION:` satırı yazılır.

**Onay kapısı:** Plandan 4 anahtar kare seçilir ve kullanıcıya gösterilir. Kullanıcı onaylamadan tüm timeline kurulmaz.

## Adım 3: Üretim

- **asaformn-edit sahneleri:** stil motoru ile şeffaf arka planlı video olarak üretilir. Kâğıt arka planı ayrı bir katman olarak sabit kalır (`stiller/asaformn-edit/STYLE.md`, bölüm 10).
- **Fotoğraflar:** internetten aranmaz (Pexels/Unsplash özelliği 25 Kasım'da çıkarıldı). Sadece kullanıcının `kutuphane/`ye koyduğu fotoğraflar kullanılır. Fotoğraf sketchnote filtresinden geçirilir. Kalabalık fotoğraflar filtreden temiz çıkmadığı için tek nesneli olanlar seçilir.
- **Kullanıcı kartları:** `kutuphane/katalog.md` içinden uygun olan seçilir (kütüphane açıklaması aşağıda).
- **Kartlar ve geçişler:** kinetik yazı kuralları ve geçiş kataloğuna göre kurulur (özellik 2, 12). asaformn-edit stilinde geçiş ya müzik vuruşunda kesim ya da bir şeyin içinden geçen kamera hareketidir.
- **Sesler:** `sesler/kenney/` klasöründen, sfx analiz dosyasındaki kullanım notlarına ve `kurallar/ton-matrisi.md` yasaklarına göre seçilir (özellik 13, 6). Ses seviyesi müziğe göre ayarlanır.

## Adım 4: Yerleştirme (DaVinci)

Yerleştirme kelime zamanlarına göre yapılır (özellik 8). Konuşmadaki kelime anında kart, şekil ya da yazı ekrana gelir.

Parça düzeni:

| Parça | İçerik |
|---|---|
| V1 | Kâğıt arka planı (sabit) |
| V2 | asaformn-edit sahneleri |
| V3 | Kartlar ve yazılar |
| V4 | Altyazılar (özellik 19) |
| A1 | Seslendirme |
| A2 | Ses efektleri (yumuşak, konuşmanın altında) |
| A3 | Müzik (arada, çok kısık) |

Yazılar ve kartlar seslendirmedeki kelimeyle aynı anda başlar. Giriş hareketi kısa olur (yazı 0,4 sn civarında belirir). Her yazı okunacak kadar ekranda kalır.

## Adım 5: Kontrol (özellik 1, 3, 4, 5, 7, 9, 15, 17, 24)

Her iş bitince kontrol döngüsü çalışır:

1. Timeline render edilir.
2. Ana kontrol:
   `python3 scripts/kontrol.py VIDEO --platform youtube --length N`
   Bu komut baştaki siyah ya da beyaz kareyi bulur (özellik 1), donmuş anları arar (özellik 5), ses seviyesini ölçer (özellik 4) ve platform kurallarına göre GEÇTİ / UYARI / KALDI sonucu verir (özellik 24).
3. Teslim öncesi tam kontrol:
   `npx @veedstudio/openedit-cli review VIDEO --transcript T`
   Rakam kontrolü, yazı boyutu ve kontrastı, ses boşlukları ve ölü kuyruk burada kontrol edilir (özellik 17).
4. Okuma süresi kontrolü: her yazı okunacak kadar kalıyor mu (özellik 15).
5. Efekt doğrulama: her ses efektinin son render'da duyulup duyulmadığı ölçülür (özellik 9).
6. Ses master: -14 LUFS, -1 dBTP (özellik 7).
7. Claude kontak sayfası görüntülerini kendisi açar ve bakar. Her sorun düzeltilir, sonra kontrol tekrarlanır. Bu adım bitmeden iş tamam sayılmaz.

## Adım 6: İnceleme sayfası (özellik 22)

Kullanıcıya bir yerel HTML inceleme sayfası verilir:

```
python3 vendor/ffmpeg-skill/scripts/_review.py
```

Sayfada adımlar, kontroller ve timeline görünür. Kullanıcı bir klibe ya da altyazıya tıklayıp not yazar. Bu notlar Claude'a talimat olarak döner. Talimatlar uygulanır, kontrol tekrar çalışır.

## Adım 7: YouTube bölümleri (özellik 25)

Duraklama ve sahne değişimlerinden bölüm önerileri çıkarılır. Her bölüm, transkripte bakılarak adlandırılır. Kullanıcı onaylayınca açıklamaya bölüm zaman damgaları eklenir.

## Adım 8: Dikey kesitler (özellik 26, 19, 23, 24, 7)

Uzun videodan dikey kesitler çıkarılır.

- **Sayı:** uzun videodan en vurucu 3–4 an seçilir (reels). Kullanıcıya ayrıca sorulmaz.
- **Seçim:** her kesit 30–45 saniye sürer ve tek başına anlaşılır olmalıdır.
- **Timeline:** her kesit için 1080×1920 ayrı bir timeline kurulur.
- **Grafikler:** yeniden yerleştirilir, kırpılmaz. Dikey düzen için her grafik baştan düzenlenir.
- **Altyazı:** kelime kelime (özellik 19).
- **Güvenli alan:** en katı platform sınırı esas alınır. Üst %10, alt %22, sol %5 ve sağ %14 boş kalır (Shorts, Reels ve TikTok arayüzü bu alanları kaplar).
- **Kontrol:** her kesit için `kontrol.py --platform shorts` (ve gerektiğinde `reels`, `tiktok`) çalışır.
- **Ses:** üç platform için tek master kullanılır (-14 LUFS, -1 dBTP). Dikey kesitlerde müziğin basları biraz kesilir, seslendirme net kalır.

## Adım 9: Bitiş raporu

Rapor kısa tutulur:

- Ne yapıldığı (kısa madde listesi).
- Tüm `DECISION:` satırları, kullanıcı geri çevirebilsin diye.
- Kontrol tablosu: her kontrolün GEÇTİ / UYARI / KALDI sonucu ve düzeltmeler.
- Oluşturulan dosyaların yolları.

---

## Notlar

- Planlanan scriptler (`scripts/davinci/*`, `scripts/kontrol.py`, `motor/`) yazılana kadar bu adımlar hedef akıştır. Eksik bir script varsa kullanıcıya söylenir, sessizce atlanmaz.
- `vendor/` altındaki dosyalar kopyalardır. Değişiklik `scripts/` altında yapılır.
- Lisans: stil rehberi ve Lemo-Opuscar kökenli kodlar CC BY-NC 4.0 / MIT'tir. Bu skill ile yapılan videolar kullanıcıya aittir (`README.md`, Lisans bölümü).
