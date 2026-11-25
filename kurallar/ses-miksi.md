# Ses miksi

Videolar seslendirme üstüne kurulur. Ses katmanları, önem sırasıyla:

1. **Seslendirme:** her zaman en önde, net ve anlaşılır.
2. **Ses efektleri:** konuşmanın altında, yumuşak; ses kütüphanesinden ve ton matrisinden seçilir (`kurallar/ton-matrisi.md`).
3. **Müzik:** belli belirsiz, çok az.

## Müzik

- **Sürekli çalmaz.** Sadece arada girer: açılışta, bölüm geçişlerinde, konuşmanın olmadığı kısa duraklamalarda ve kapanışta.
- **Çok kısık:** Konuşma varken müzik seslendirmenin en az ≈ 20 dB altında kalır, yani fark edilmez ama boşluğu doldurur. Konuşmasız anlarda biraz yükselebilir ama yine de arka planda kalır.
- Giriş ve çıkışlar yumuşak (en az 1–2 sn fade), müzik hiçbir zaman aniden başlamaz ya da kesilmez.
- Konuşma başladığında müzik zaten kısıksa ek bir kısma gerekmez; konuşmasız bir anda yükselmişse konuşma başlamadan yumuşakça iner.

## Son seviye (bütün platformlar için tek master)

- **-14 LUFS** entegre ses seviyesi, **-1 dBTP** tepe sınırı. Uzun video, YouTube Shorts, Instagram Reels ve TikTok için aynı.
- Dikey kesitlerde (telefon hoparlörü) müziğin basları biraz kesilir; seslendirme net kalır.
- Ölçüm ve düzeltme: ses seviyesi ölçer (4), otomatik mastering (7), efekt doğrulama (9), platform uygunluk kontrolü (24).
