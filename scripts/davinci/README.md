# DaVinci köprü scriptleri

Resolve Studio 21.1.2 scripting API'si için dört script. Claude bunları DaVinci MCP aracındaki `run_script` ile çalıştırır.

## Nasıl çalıştırılır

1. Claude scriptin dosya metnini okur.
2. En başa tek satır `PARAMS = {...}` ekler.
3. Tümünü `run_script`'e gönderir. Sonuç `result` sözlüğüdür.

Sandbox'ta `os`, `sys`, `pathlib` ve dosya G/Ç yoktur. Scriptler bunları kullanmaz. Dosya yollarını yalnızca Resolve'a verirler. `resolve` ve `project` hazır gelir. Terminalden çalıştırılırsa `DaVinciResolveScript` ile bağlanmayı dener, bağlanamazsa `ok: False` ve açık bir hata döner. Hepsinde `result["ok"]`, `result["hatalar"]` vardır. Yazan scriptlerde `"kuru": True` hiçbir şeyi değiştirmeden planı döndürür.

## Scriptler

| Script | İş | Yazar mı |
|---|---|---|
| `ses_bul.py` | Timeline bilgisi ve A1'deki ses klipleri (ad, kare, saniye, kaynak dosya) | Hayır |
| `yerlestir.py` | Dosyaları bin'e alır, parça ekler, kelime zamanına yerleştirir, yavaş kliplere Optical Flow + AI Speed Warp Better uygular, ses dB ayarlar | Evet |
| `dikey_timeline.py` | Her kesit için 1080x1920 "<ad> (dikey)" timeline iskeleti kurar | Evet |
| `render.py` | Render işi ekler, isteğe bağlı başlatır ve bekler | Evet |

## PARAMS örnekleri

```python
# ses_bul
PARAMS = {"parca": "A1"}

# yerlestir (önce kuru dene)
PARAMS = {"kuru": True, "bin": "asaformn-edit", "ogeler": [
  {"dosya": "/Users/o/sahne01.mov", "parca": "V2", "bas_sn": 1.2, "sure_sn": 4.0},
  {"dosya": "/Users/o/kart.png", "parca": "V3", "bas_sn": 2.0, "sure_sn": 2.5},
  {"dosya": "/Users/o/klip.mov", "parca": "V2", "bas_sn": 8, "sure_sn": 4, "yavas": 50},
  {"dosya": "/Users/o/whoosh.wav", "parca": "A2", "bas_sn": 1.2, "ses_db": -20}]}

# dikey_timeline
PARAMS = {"kaynak_timeline": "Ana Video",
          "kesitler": [{"ad": "Kesit 1", "bas_sn": 30, "bit_sn": 68}]}

# render
PARAMS = {"hedef_klasor": "/Users/o/Videolar", "ad": "video_v1",
          "on_ayar": "youtube", "baslat": True, "bekle": True}
# bekleme 48 sn'yi geçmez; render sürerse sonra: PARAMS = {"sorgu_is_id": "<is_id>"}
```

Parça düzeni: V1 kâğıt, V2 sahneler, V3 kartlar, V4 altyazı, A1 ses, A2 sfx, A3 müzik.

## API ile doğrulananlar

Şu adlar `get_scripting_api` / `search_scripting_api` ile 21.1.2 stub'larına karşı kontrol edildi: `AppendToTimeline` (`mediaPoolItem`, `startFrame`, `endFrame`, `mediaType`, `trackIndex`, `recordFrame`), `ImportMedia([yol])`, `AddSubFolder`, `GetSubFolderList`, `GetClipList`, `AddTrack(trackType, subTrackType)`, `GetTrackCount`, `GetItemListInTrack`, `GetStartFrame`, `GetStartTimecode`, `Timeline.SetSettings/GetSettings` anahtarları (`useCustomSettings`, `timelineResolutionWidth/Height`, `timelineFrameRate`, `timelineOutput...`), `TimelineItem.SetSpeed({"Percentage","RippleTimeline"})`, `SetProperties` anahtarları `RetimeAndScalingEnabled`, `RetimeProcess`, `MotionEstimation`, `AudioVolumeEnabled`, `AudioVolume` (dB), sabitler `resolve.RETIME_OPTICAL_FLOW` ve `resolve.MOTION_EST_SPEED_WARP_BETTER`, render çağrıları ve `RenderSettings` anahtarları, `GetRenderJobStatus` (`JobStatus`).

## Canlı test (Resolve Studio 21.1.2, 30 fps) ve DOGRULA listesi

Dört script canlı denendi. Doğrulananlar (kodda `# DOGRULANDI 21.1.2`):

- `ImportMedia` düz yol listesi ister: `[yol]`. `[{"FilePath": yol}]` boş döner (kod önce düzünü, sonra sözlüğü dener).
- `AppendToTimeline` `endFrame` DAHİL DEĞİL: uzunluk = `endFrame - startFrame`.
- Still (PNG) için `startFrame/endFrame` yok sayılır (5 sn varsayılan). Süre, ekledikten sonra `SetRightOffset` ile ayarlanır (süre = tam - sağ ofset).
- Ses `startFrame/endFrame` birimi timeline fps (30 fps'te 2 sn = 60 doğrulandı).
- `AddTrack('audio','stereo')` çalışır.
- `SetSpeed({"Percentage": 50, "RippleTimeline": False})` süreyi DEĞİŞTİRMEZ (kaynak yarıya iner). `RippleTimeline: True` tüm parçalardaki sonraki klipleri kaydırır ve sesi böler, kullanılmaz. Script `sure_sn` varsa o süreyi, yoksa tüm kaynağı yavaşlatılmış uzunlukta (`yavas` 50 ile 2 sn klip 4 sn) `SetRightOffset` ile kurar.
- Retime: `RetimeProcess` 3 (= `resolve.RETIME_OPTICAL_FLOW`), `MotionEstimation` 5 (= `MOTION_EST_SPEED_WARP_BETTER`) geri okunarak doğrulandı.
- `dikey_timeline`: 1080x1920 ayarı tutar, fps kaynaktan gelir (`timelineFrameRate` ayarı False döner, eşitse atlanır), hızlı klip süresi korunur. Ses seviyesi kopyalanmaz; script elle taşır.
- `render.py`: `('mp4','H264')`, `SetCurrentRenderMode(1)`, `AudioCodec 'aac'` kabul edildi; `time.sleep` ile bekleme çalışır; 12 sn'lik 1080p render 19.7 sn'de "Complete" oldu, dosya yazıldı.

Hâlâ açık:

- 30 fps dışı timeline'larda ses/kaynak karesi birimi ve 23.976/29.97 yuvarlaması denenmedi.
- Kaynağı timeline fps'inden farklı (ör. 24 fps) kliplerde `startFrame` kaynak karesi sayılır varsayıldı; denenmedi.
- `GetSourceStartFrame` ses kliplerinde kaynak başlangıcı verir (hedef: 0'dan başlayan klip), kırpılmış ses klibi denenmedi.
- Hızlı klipte `sure_sn` kaynaktan uzunsa süre kaynakla sınırlı kalır.

Diğer sınırlar:

- Fusion başlık, generator, geçiş ve iç içe timeline klipleri dikeye kopyalanmaz; `kopyalanamayan` listesinde döner.
- Altyazı (subtitle) parçaları kopyalanmaz.
- Dikey scripti yalnızca iskelet kurar. Grafikler sonradan yeniden yerleştirilir.
- Aynı parçada çakışma önceden uyarıyla bildirilir. Resolve'un çakışmada ne yapacağı doğrulanmadı.
- Klip adı ve bin eşleşmesi dosya yoluna göre yapılır (büyük/küçük harf duyarsız).
