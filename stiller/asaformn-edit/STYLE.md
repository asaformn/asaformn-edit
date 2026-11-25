# asaformn-edit — stil rehberi

> **Durum:** taslak. Stilin adı onay bekliyor.
>
> **Kaynak ve lisans:** Bu stil, [Lemo-Opuscar](https://github.com/lemomo-ai/lemo-opuscar) (Lemomo / LemoLab) içindeki iki stilden uyarlandı ve değiştirildi: görünüş **Sketchnote**'tan (No.17), hareket **Stick-figure Explainer**'dan (No.18). Bu dosya, kaynak stillerin rehberleri gibi [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/) lisanslıdır. Bu stille yapılan videolar, ticari olanlar dahil, tamamen yapanındır.

Kısaca: **No.17 gibi görünür, No.18 gibi hareket eder.** Noktalı defter sayfası, titrek lacivert kalem çizgisi, marker gölgesi ve **Kanal Tipi** paletinin anlam taşıyan renkleri. Ama hiçbir şey kalemle çizilerek gelmez. Objeler ve çöp adamlar yaylanarak belirir, birbirine dönüşür, el ele tutuşur. Kamera da zoom in ve zoom out yaparak hikâyeyi anlatır.

---

## 1. Öz

- **İnsanlar diyagramın kendisidir.** Yüzsüz çöp adamlar, yuvarlak kafa ve tek kalınlıkta eğri çizgiler. Fikri onlar canlandırır: kim değişti, kim tepki verdi, kim kime bağlı.
- **Gövdeler kesintisizdir.** Kafa boyuna boşluksuz oturur. Her uzuv tek bir yumuşak eğridir, dirsek ya da dizde köşe olmaz.
- **El ele tutuşan eller tek çizgi olur.** İki el birleşince omuzdan omuza tek bir kesintisiz eğri oluşur. Sıra sıra insanlar bir çizgi, halka hâlindeki insanlar kapalı bir şekil olur.
- **Sayfa bir defter sayfasıdır.** Masa, defter kenarı, el ya da kalem görünmez.
- **Renk anlam taşır.** Mavi kanalın imzasıdır; mercan, hardal ve nane her zaman aynı anlamda kullanılır (bkz. 3. bölüm).
- **Mantık hareketle anlatılır.** Değişiklik yol alır: zemin çizgisinde ya da birleşmiş kollarda bir nabız ilerler, her adam nabız kendisine ulaşınca tepki verir.
- **Kalemle çizilme efekti yoktur.** Objeler yaylanarak belirir, çizilerek gelmez.

## 2. Görünüş (No.17'den)

- **Kâğıt:** düz, sıcak krem; sayfaya sabit, çok ince bir doku. Üstünde nokta ızgara var (26 px aralık, 1.3 px nokta). Izgara dünya koordinatında çizilir, kamerayla birlikte ölçeklenir.
- **Kalem çizgisi:** Siyah ince uç, hafif titrek. Çizgi üç katmanlı sinüsle kaydırılır (yavaş dalgalanma, orta dalgalanma, ince titreme). Çizgi iki kez çizilir; ikinci geçiş daha ince, daha açık ve daha titrek olur. Kalınlık kısa parçalarda hafifçe değişir.
- **Çöp adamlar da bu kalemle çizilmiş görünür:** aynı titrek çizgi, yuvarlak uçlar. Gövde çizgisi tek kalınlıktadır (380 px boyundaki adam için ≈ 8 px).
- **Marker gölgesi (yarı saydam `murekkep`):** Hacim, gölge ve dolgu vermenin tek yolu. Tek açıda, hafif yay çizen yarı saydam geniş darbeler; üst üste binen yerler koyulaşır (`multiply`). Kenarda ince bir mürekkep birikimi olur. Üç ton: açık (hacim), orta (gölge ve şerit uçları), koyu (kıvrımlar ve küçük koyu parçalar).
- **Gölge:** Her zaman aynı yöne düşer, sağ-alt; kutularda ≈ 9–10 px. Işığın uzak tarafında hilal gölge.
- **Kâğıt dolgusu:** Başka şeylerin üstüne gelen şekil (şerit, kutu, etiket) önce kâğıt rengiyle doldurulur, altındaki çizgiler kaybolur.
- **Titreşim (boil):** Sadece kalem çizgisinin dalgalanma fazı yaşar, her 2 karede bir, 3'lük döngüyle. Geri kalan her şey sabit tohumla çizilir, kare kare zıplamaz.
- **Parçalar:** başlık şeritleri, köşeleri yuvarlak kutular, kalın oklar, ikonlar, el yazısı. `meter`: el çizimi yatay gösterge, `hardal` marker ile ~1 sn içinde dolar, altında soluk etiket; üzerine rakam yazılmaz.

## 3. Renk (Kanal Tipi paleti)

Bütün renkler **Kanal Tipi** tasarım sisteminden gelir. Her rengin bir görevi var: renk süs için değil, anlam için kullanılır. İzleyici birkaç videodan sonra rengi görünce ne anlama geldiğini tahmin edebilmeli.

| Rol | Token | Hex | Ne zaman |
|---|---|---|---|
| Zemin | `kagit` | `#F7F3EC` | Her sahnenin zemini, defter kâğıdı. Saf beyaz yok |
| Kart zemini | `kagit-koyu` | `#EDE6DA` | Bilgi kartı, panel, şerit zemini; kâğıt dolgusu |
| Mürekkep | `murekkep` | `#1F2A44` | Bütün çizgiler, konturlar, çöp adamlar, yazılar |
| Soluk mürekkep | `murekkep-soluk` | `#5B6477` | Alt başlık, ince notlar, sönmüş şeyler |
| Ana renk | `mavi` | `#2F5D8A` | Kanalın imza rengi: ana karakter, başlık şeritleri, kalın oklar |
| Vurgu | `mercan` | `#D9533F` | Dikkat, yanlış bilinen, hata, aşk ve heyecan |
| Vurgu | `hardal` | `#F2B544` | İpucu, fikir, enerji, dopamin |
| Vurgu | `nane` | `#2E8A78` | Doğru yöntem, tik işareti, "sonra" karesi |

- **Defter noktaları:** `#D9D7D4` (%14 `murekkep`, %86 `kagit`).
- **Marker gölgesi:** yarı saydam `murekkep`, üç ton: açık `rgba(31,42,68,.14)`, orta `rgba(31,42,68,.26)`, koyu `rgba(31,42,68,.42)`. Hacim ve gölgenin tek aracı.
- **Renkli marker:** `mavi`, `mercan`, `hardal` ve `nane` de yarı saydam marker olarak basılır (`multiply`), düz opak boya olarak değil.
- **Oran:** Bir karenin yaklaşık %60'ı `kagit`, %25'i `mavi` ve `murekkep`, en fazla %15'i vurgu renkleri.
- **Aynı karede üç vurgu rengi birden yok,** ikisi yeterli. Bir vurgu rengi aynı videoda tek bir anlam taşır.
- **Okunabilirlik:** Küçük yazı her zaman `murekkep` ya da `murekkep-soluk`. `mercan` ve `nane` yazı olarak sadece 24 px ve üstü başlıkta. `hardal` asla yazı rengi olmaz; hardal dolgunun içindeki yazı `murekkep`. `mavi` dolgunun içindeki yazı `kagit` renginde.
- Doğru/yanlış karşılaştırmasında rengin yanına mutlaka ✓ / ✗ konur; sadece renge güvenilmez.
- **Yok:** saf beyaz zemin, siyah kontur, gökkuşağı renkler, gradyan, parlama.

## 4. Yazı

- **Tek font ailesi: Shantell Sans** (OFL, `fontlar/shantell-sans/`). Marker kalemle yazılmış gibi duran ama okunaklı bir el yazısı. Türkçe karakterlerin hepsi var (ğ, ş, ı, İ, ç, ö, ü). İki ayarı kullanılır: **Informal** (daha el yazısı harf biçimleri) ve **Bouncy** (her harf hafifçe aşağı yukarı oynar, defter hissi verir).
  - Başlık ve şerit: Informal Bouncy ExtraBold, 56–84 px
  - Kart başlığı: Informal Bouncy Bold, 44–48 px
  - Gövde yazısı: Informal Medium, 32–36 px
  - İnce notlar: Informal Regular, 26–30 px, `murekkep-soluk`
  - Neden bu font: Kanal Tipi'nin Nunito'su gibi yuvarlak ve okunaklı, ama Sketchnote'un el yazısı ruhunu taşıyor. Kalem çizgisinin yanında sırıtmıyor, Kanal Tipi kartlarının yanında da dağınık durmuyor.
- **✓ ve ✗ fonttan yazılmaz,** kalemle çizilmiş işaret olarak çizilir (✓ `nane`, ✗ `mercan`). Fontta bu işaretler yok.
- **Hiyerarşi:** şerit üstünde başlık, kalın anahtar kelimeler, ince `murekkep-soluk` notlar. Önemli rakamların altı anlamına uyan vurgu marker'ıyla çizilir ya da etrafına halka çekilir. Bir ekranda en fazla dört boyut.
- **Harflerin inip çıkması** fontun Bouncy ayarından gelir; ayrıca ek titreşim verilmez.
- **Yazı yerleşimi:** sola yaslı, 124 px kenar boşluğu. Kapalı bir şeklin (halka, küre) içindeki yazı ortalanır.
- **Giriş (No.18):** yazı 12–22 px yukarı kayarak ve belirerek gelir, ≈ 0.4 sn, satır satır sırayla. Büyük rakamlar daha uzun kayar. Çıkarken sadece solar.
- Ekrana gelen yazılar seslendirmedeki kelimeyle aynı anda gelir (bkz. kelimeye kilitli senkron).
- Her yazı okunacak kadar ekranda kalır (bkz. okuma süresi kontrolü).

## 5. Hareket (tamamı No.18'den)

- **Hiçbir şey zıplayarak yer değiştirmez.** Her poz değişikliği sönümlü yaylarla olur: kalça hızlı, üst kol orta, ön kol daha yavaş, kafa en gevşek. Ön kol geç gelir ve hafifçe taşar. Sabit adımla, ön-ısınmayla hesaplanır, her render aynı çıkar.
- **Önce hazırlık:** zıplamadan önce çömelme, uzanmadan önce eli geri çekme. Çömelme sığ kalır (boyun en fazla %2'si), yoksa bacaklar paranteze döner.
- **Belirme:** Obje ya da adam yerden yaylanarak büyür (≈ %20 taşma), çizgi kalınlığı da onunla büyür.
- **Tutuşma:** Eller değince birleşme noktası bir kez seker, iki gövde birbirine doğru hafifçe çekilip oturur.
- **Kaldırma:** Tutuşan eller zincir boyunca dalga gibi kalkar, her el bir öncekinden ≈ 0.06 sn sonra. Sert yay kullanılır (ω ≥ 19), kollar omuz hizasını hızlı geçer.
- **Kalabalık:** Herkes kendi fazında nefes alır ve sallanır. Kalabalık sadece bir işarette hep birlikte hareket eder.
- **Hiç kıpırdamayanlar:** kâğıt, kenar boşlukları, altyazılar.

## 6. Kamera (No.18'den)

Bütün sahne tek bir dünya koordinatında yaşar, tek bir kamerayla görülür (merkez ve zoom; zoom logaritmik ölçekte enterpolasyonla). Ekran koordinatında sadece başlıklar, sayaç sütunu, kaynaklar ve altyazılar durur.

| Hareket | Ne anlatır | Örnek |
|---|---|---|
| Sabit kadraj | Kural kuruluyor, okuma zamanı | Bir soru, bir gösterim, bir hüküm |
| Geri çekilme | Bir örnek çoğalıyor | Bir zincir → çok zincir; bir kişi → kalabalık |
| Yaklaşma + odak kayması | Birini öne çıkarma | "Şimdi sadece sana bakalım"; istisna |
| Katlanarak geri çekilme | Sabit oranla büyüme | Halkalar ×2.5, nesiller, bileşik büyüme |
| Bir şeklin içinden geçme | Başka bir yere ya da zamana atlama | Bir kafanın, bir düğümün, bir halkanın içine dalma |
| Eşleşen dönüşüm | Aynı şey yeni bir gözle | Bir çizginin yaya, bir sıranın halkaya dönüşmesi |
| Yavaş kayma / itme | Dikkati veride tutma | Bir sayım, bir karşılaştırma |

- Konu kadrajın üst %85'inde kalır. Yazı sütunları adamların yanında durur, üstünde değil.
- Kesim ya müzik vuruşunda ya da bir şeyin içinden geçerek olur. **Sayfa çevirme, silme (wipe) ve zoom-blur yoktur.**

## 7. Hazır hareket kalıpları (No.18'den)

- **El ele tutuşma:** İki kişi uzanır, tutuşur, tek eğri olur. *Uyar:* arkadaşlık, takas, anlaşma.
- **Zincir:** İki uç arasında adamlar birer birer belirir ve gittikçe hızlanarak tutuşur, çizgi kapanınca renk (genelde `mavi`) uçtan uca koşar. *Uyar:* tedarik zinciri, mesaj aktarımı, ispat adımları.
- **Dalga (ripple):** Bir adam değişir (çömelir, zıplar, anlamına uyan vurgu rengine döner); zemin çizgisinde bir nabız koşar, her adam nabız ulaşınca tepki verir; sonunda hepsi kaynağa döner. *Uyar:* söylenti, banka paniği, trafik sıkışması.
- **Bırakma:** Tutuşmanın tersi: el düşer, kol geri savrulur, taşınan şey düşer ve `murekkep-soluk` rengine döner. *Uyar:* kopan bağ, kaybolan mesaj.
- **Halkalar:** Adamlar bir çemberin üstünde, ayaklar içe, kafalar dışa durup el ele halkayı kapatır; halkalar iç içe, her biri sabit oranla büyük, katlanarak geri çekilmeyle. *Uyar:* bileşik büyüme, nesiller, viral yayılma.
- **İnsanlardan çubuk grafik:** Uzunluğu veri olan zincirler; kesirli değer son halkanın kısa çizilmesiyle gösterilir. *Uyar:* sıra uzunlukları, adım sayısı, sıralama.
- **Bütün şekil:** Bir çizgi yaya bükülür ve son iki el buluşana kadar bir kürenin ya da kapalı bir şeklin etrafını sarar. *Uyar:* "herkes", döngü, final.

## 8. Fotoğraflar

Fotoğraflar internetten aranmaz; sadece kullanıcının `kutuphane/`ye koyduğu fotoğraflar kullanılır. Bunlar olduğu gibi konmaz, **sketchnote filtresinden** geçirilir: kenarlar titrek kalem çizgisine çevrilir, hacim `murekkep` marker gölgesiyle verilir, önemli kısım anlamına uyan renkle boyanır, arka plan kâğıda karışır. Sade, tek nesneli fotoğraflar seçilir; kalabalık fotoğraflar filtreden temiz çıkmaz.

## 9. Tuzaklar

- **Kırık çubuk uzuvlar:** köşeli çizgi parçaları kırık sopa gibi okunur. Her uzuv tek eğri, eklem kontrol noktası.
- **Kopan kafa:** kafa yayı kafayı kaydırırsa kafa boyundan kopar. Gecikme sadece kafayı boyun etrafında döndürsün.
- **İki kolun açıyla birleşmesi:** tutuşan eller iki ayrı eğri olarak çizilirse kırık görünür. Kontrol noktaları birleşme noktasından hizalanmalı.
- **Gövdeden geçen eller:** yay taşması kolları gövdenin içinden geçirebilir. Ele kilit koy ya da o pozlardan kaçın.
- **Kaybolan kalabalık:** kamera çok geri çekilince çizgi kalınlığı kaybolur; zoom sırasında kalınlığı orantılı ölçekle.
- **Rengi süs yapmak:** bir vurgu rengini anlamı dışında kullanmak ya da aynı karede üç vurgu rengini birden kullanmak renklerin anlamını bozar. Mürekkep tonları ya da boyut kullan.
- **Slayt görünümü:** başlık çubukları, ortalanmış yazı yığınları ve sayfa çevirmeler videoyu sunuma çevirir. Kenar boşluğunu koru, kamerayı hareket ettir.
- **Ekrana fazla şey:** her ekranda tek fikir. Kalabalık bir dokudur, kişi listesi değil.
- **Titreme:** her karede yeni rastgele sayı her çizgiyi zıplatır. Her öğeye sabit tohum ver, sadece dalgalanma fazı yaşasın.
- **Kirli gölgeler:** büyük siyah dolgular ve farklı yönlere düşen gölgeler kâğıt hissini bozar.
- **Boş kare:** kamera hareketi boş kâğıtta bitmesin; kadrajda her zaman okunabilir bir şey olsun.

## 10. DaVinci'de üretim

- Çöp adamlar, belirme ve dönüşüm animasyonları kod motorunda (Lemo-Opuscar'ın MIT lisanslı motoru temel alınarak) **şeffaf arka planlı video** olarak render edilir ve DaVinci timeline'ına klip olarak konur.
- Kâğıt arka plan ayrı bir katmandır, bütün video boyunca sabittir.
- Yazılar ve kartlar seslendirmedeki kelime anlarına göre yerleştirilir.
- Her işin sonunda kontrol araçları çalışır: siyah/beyaz kare, tek kare hata, donmuş an, okuma süresi, ses seviyesi.
