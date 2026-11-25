# Ton matrisi (asaformn-edit stili için uyarlanmış)

> Kaynak: [saas-motion-kit](https://github.com/tugrawork-creator/saas-motion-kit) `creative/tone-matrix.md` (MIT). asaformn-edit stiline ve kanalın ses kütüphanesine göre değiştirildi: geçişler No.18'in kamera diline, sesler 260'lık Kenney kütüphanesine bağlandı; stile uymayan tonlar ve sesler çıkarıldı.

Her videonun ve her bölümün başına tek cümle yazılır:

> **"Şunu** ___ **tonda söylemek istiyorum, izleyici** ___ **hissetsin."**
> *Örnek: "Gece uyanık yatmanın sebebi beynindeki bir kimyasal" demeyi **sakin** tonda söylemek istiyorum, izleyici **anlaşılmış** hissetsin.*

Ton; tempoyu, sahne uzunluğunu, yay sertliğini, kamera hareketini ve sesi belirler. Görünüş (renkler, font, çizgi) tondan bağımsızdır, her zaman asaformn-edit stilidir.

## Tonlar

| Ton | Tempo ve sahne uzunluğu | Yay (hareket) | Kamera (No.18) | Ses (Kenney kütüphanesi) |
|---|---|---|---|---|
| **Sakin** | Uzun tutuşlar (2–4 sn), az kesim | Yumuşak yay, taşma çok az | Sabit kadraj, yavaş kayma | `impactSoft_medium`, tek `bong`; sessizliğe yer bırak |
| **Güvenilir** | Düzenli, tahmin edilebilir vuruşlar | Orta yay, küçük taşma | Sabit kadraj → net yaklaşma, eşleşen dönüşüm | `impactWood_light/medium`, onay için `bong` |
| **Sıcak / insani** | Doğal, hafif düzensiz | Gevşek yay, kalabalık nefes alır | Yavaş kayma, yaklaşma + odak kayması | `footstep_wood`, `impactSoft_medium` |
| **Oyunbaz** | Zıplayan, senkoplu ritim | Belirgin taşma (≈ %20), asla lastik gibi sallanma | Belirme ve dalga (ripple), hafif itme | `ui/rollover`, `interface/drop`, kısa `ui/click` |
| **Teknik** | Vuruşa oturan, ızgaraya kilitli zamanlama | Sert yay, taşma yok | Sabit kadraj, insanlardan çubuk grafik | `ui/click`, `keyboard` (yazı yazılırken), `impactPlate_light` |
| **Gizemli / açılış** | Önce beklet, sonra bırak | Önce yavaş, açılışta sert yay | Bir şeklin içinden geçme, geri çekilme ile ortaya çıkarma | Önce sessizlik, açılışta `impactSoft_heavy` |
| **Kutlama** | Hızlı varış, sonra uzun tutuş | Belirgin taşma | Geri çekilme, bütün şekil (halka kapanır) | Yükselen seri `bong` / `impactBell_heavy` (tek sefer) |
| **Acil** | Kısa sahneler (0.4–1 sn), hızlanan | Sert yay | Hızlı yaklaşma, katlanarak geri çekilme | `impactSoft_medium` seri, `impactWood_heavy` |

## asaformn-edit stilinde hiç kullanılmayanlar

**Sesler:** `interface/glitch_*`, `interface/error_*`, `casino/*` klasörünün tamamı, `impactPunch_*`, `impactMetal_*`, `impactGlass_*`, `impactMining`, `impactTin_*`. Ayrıca kaynak matristeki 8-bit bip, VHS/kaset bozulması, plak cızırtısı, kalabalık sesi ve davul vuruşları.

**Geçişler:** glitch, VHS, kromatik sapma, bozulma (distort), silme (wipe), sayfa çevirme, zoom-blur. Geçiş ya müzik vuruşunda kesimdir ya da bir şeyin içinden geçen kamera hareketidir (bkz. `stiller/asaformn-edit/STYLE.md`, Kamera).

**Tonlar:** Kaynak matristeki *Premium* (koyu zemin ister, paletle çelişir), *Nostaljik* (gren ve film yanığı ister) ve *Cesur* (renk taşması ister, renk oranını bozar) bu stilde yok.

## Tona uymayanlar (denetim uyarır)

- **Sakin** tonda saniyede 1.5'tan fazla kesim ya da belirgin taşmalı yay.
- **Acil** tonda 2 saniyeden uzun tutuş (ödülden önceki bir bilinçli duraklama hariç).
- **Güvenilir** tonda sert vuruş sesi (`impactSoft_heavy`, `impactWood_heavy`) art arda.
- Herhangi bir tonda aynı karede ikiden fazla vurgu rengi (Kanal Tipi kuralı).
- Herhangi bir tonda yukarıdaki yasak seslerden ya da geçişlerden biri.
