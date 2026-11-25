"""render.py - Timeline'i render kuyruguna ekler, istenirse baslatir/bekler.

PARAMS:
    "hedef_klasor": str   Zorunlu. Mutlak klasor yolu.
    "ad":           str   Zorunlu. Dosya adi (uzantisiz da olur).
    "timeline":     str   (ops.) Yoksa aktif timeline.
    "on_ayar":      "youtube" | "dikey"   (varsayilan "youtube")
                    youtube: MP4 / H264, timeline cozunurlugu.
                    dikey:   MP4 / H264, 1080x1920 beklenir (uyari verir).
    "preset":       str   (ops.) Resolve render preset adi; verilirse LoadRenderPreset
                    kullanilir, format/kodek ayari yapilmaz (hedef ve ad yine yazilir).
    "baslat":       bool  True ise StartRendering([isId]).
    "bekle":        bool  True ise (baslat ile) en fazla "bekle_sn" saniye bekler.
    "bekle_sn":     int   Varsayilan 40, en fazla 48 (MCP zaman asimi 60 sn).
    "kuru":         bool  Hicbir sey degistirmez; ayarlari raporlar.

Ornek:
    PARAMS = {"hedef_klasor": "/Users/o/Videolar", "ad": "video_v1",
              "on_ayar": "youtube", "baslat": True, "bekle": False}

result sekli:
    {"ok", "kuru", "is_id", "beklenen_dosya", "durum": {JobStatus, ...},
     "ayarlar": {...}, "uyarilar": [], "hatalar": []}
Bekleme yetmezse durum "Rendering" kalir; sonra yeniden sorgulamak icin
PARAMS = {"sorgu_is_id": "<is_id>"} ile bu scripti calistir.
"""
try:
    PARAMS
except NameError:
    PARAMS = {}
PARAMS = PARAMS or {}
# run_script sandbox'inda globals ve eval yok; enjekte edilen adlar NameError ile kontrol edilir.
try:
    resolve
    _TERMINAL = False
except NameError:
    resolve = None
    _TERMINAL = True
try:
    project
except NameError:
    project = None

result = {'ok': False, 'kuru': bool(PARAMS.get('kuru', False)), 'is_id': None,
          'beklenen_dosya': None, 'durum': None, 'ayarlar': {}, 'uyarilar': [], 'hatalar': []}


def _baglan():
    r = resolve
    p = project
    if r is None:
        try:
            import DaVinciResolveScript as dvr
            r = dvr.scriptapp('Resolve')
        except Exception as e:
            return None, None, 'Resolve baglantisi kurulamadi: %r' % (e,)
    if r is None:
        return None, None, 'Resolve calismiyor ya da scripting kapali.'
    if p is None:
        try:
            p = r.GetProjectManager().GetCurrentProject()
        except Exception as e:
            return r, None, 'Proje alinamadi: %r' % (e,)
    if p is None:
        return r, None, 'Acik proje yok.'
    return r, p, None


def _fps_duzelt(v):
    try:
        v = float(v)
    except Exception:
        return None
    for a, b in ((23.976, 24000 / 1001), (29.97, 30000 / 1001),
                 (47.952, 48000 / 1001), (59.94, 60000 / 1001),
                 (119.88, 120000 / 1001)):
        if abs(v - a) < 0.01:
            return b
    return v


def main():
    h, uy = result['hatalar'], result['uyarilar']
    resolve, project, hata = _baglan()
    if hata:
        h.append(hata)
        return
    # yalnizca durum sorgusu
    sid = PARAMS.get('sorgu_is_id')
    if sid:
        result['is_id'] = sid
        result['durum'] = project.GetRenderJobStatus(sid)
        result['ayarlar']['render_devam_ediyor'] = project.IsRenderingInProgress()
        return

    kuru = result['kuru']
    hedef, ad = PARAMS.get('hedef_klasor'), PARAMS.get('ad')
    if not hedef or not ad:
        h.append('hedef_klasor ve ad zorunlu.')
        return
    on_ayar = PARAMS.get('on_ayar') or 'youtube'
    if on_ayar not in ('youtube', 'dikey'):
        h.append('on_ayar "youtube" ya da "dikey" olmali.')
        return
    # timeline
    tl = None
    tad = PARAMS.get('timeline')
    if tad:
        for i in range(1, (project.GetTimelineCount() or 0) + 1):
            t = project.GetTimelineByIndex(i)
            if t and t.GetName() == tad:
                tl = t
                break
        if not tl:
            h.append('Timeline bulunamadi: %r' % tad)
            return
    else:
        tl = project.GetCurrentTimeline()
        if not tl:
            h.append('Aktif timeline yok.')
            return
    if not kuru and project.GetCurrentTimeline() != tl:
        if not project.SetCurrentTimeline(tl):
            h.append('SetCurrentTimeline basarisiz.')
            return
    ts = tl.GetSettings() or {}
    if str(ts.get('timelineOutputResMatchTimelineRes', '1')) == '0':
        w = ts.get('timelineOutputResolutionWidth')
        hh = ts.get('timelineOutputResolutionHeight')
    else:
        w, hh = ts.get('timelineResolutionWidth'), ts.get('timelineResolutionHeight')
    try:
        w, hh = int(w), int(hh)
    except Exception:
        h.append('Cozunurluk okunamadi: %r x %r' % (w, hh))
        return
    fps = _fps_duzelt(ts.get('timelineFrameRate'))
    if on_ayar == 'dikey' and (w, hh) != (1080, 1920):
        uy.append('on_ayar=dikey ama timeline %dx%d (1080x1920 bekleniyor).' % (w, hh))
    if on_ayar == 'youtube' and w < hh:
        uy.append('on_ayar=youtube ama timeline dikey (%dx%d).' % (w, hh))

    govde = ad.rsplit('.', 1)[0] if ad.lower().endswith(('.mp4', '.mov')) else ad
    result['ayarlar'] = {'timeline': tl.GetName(), 'genislik': w, 'yukseklik': hh, 'fps': fps,
                         'hedef_klasor': hedef, 'ad': govde}
    result['beklenen_dosya'] = '%s/%s.mp4' % (hedef.rstrip('/\\'), govde)
    if kuru:
        result['ayarlar']['preset'] = PARAMS.get('preset')
        return

    preset = PARAMS.get('preset')
    if preset:
        if not project.LoadRenderPreset(preset):
            h.append('LoadRenderPreset basarisiz: %r. Mevcutlar: %r' % (preset, project.GetRenderPresetList()))
            return
    else:
        # DOGRULANDI 21.1.2: ('mp4','H264') kabul edilir; tutmazsa mevcutlar hata metnine yazilir
        if not project.SetCurrentRenderFormatAndCodec('mp4', 'H264'):
            try:
                kodekler = project.GetRenderCodecs('mp4')
            except Exception:
                kodekler = None
            h.append('SetCurrentRenderFormatAndCodec(mp4,H264) basarisiz. Formatlar: %r Kodekler(mp4): %r' % (project.GetRenderFormats(), kodekler))
            return
        if hasattr(project, 'SetCurrentRenderMode'):
            project.SetCurrentRenderMode(1)  # DOGRULANDI 21.1.2: 1 = Single clip, hata vermedi
    ayar = {'SelectAllFrames': True, 'TargetDir': hedef, 'CustomName': govde,
            'ExportVideo': True, 'ExportAudio': True}
    if not preset:
        ayar.update({'FormatWidth': w, 'FormatHeight': hh, 'VideoQuality': 0,
                     'AudioCodec': 'aac', 'AudioBitDepth': 16, 'AudioSampleRate': 48000})  # DOGRULANDI 21.1.2: AudioCodec 'aac' kabul edildi
        if fps:
            ayar['FrameRate'] = fps
    if not project.SetRenderSettings(ayar):
        # tek tek dene, hangisi sorunlu gorulsun
        kotu = []
        for a, v in ayar.items():
            if not project.SetRenderSettings({a: v}):
                kotu.append(a)
        if 'TargetDir' in kotu or 'CustomName' in kotu:
            h.append('SetRenderSettings: hedef/ad ayarlanamadi: %r' % kotu)
            return
        uy.append('SetRenderSettings su anahtarlar uygulanamadi: %r' % kotu)
    jid = project.AddRenderJob()
    if not jid:
        h.append('AddRenderJob basarisiz (hedef klasor gecersiz ya da timeline bos olabilir).')
        return
    result['is_id'] = jid
    result['durum'] = project.GetRenderJobStatus(jid)
    if not PARAMS.get('baslat'):
        return
    if not project.StartRendering([jid]):
        h.append('StartRendering basarisiz (is kuyrukta kaldi: %s).' % jid)
        return
    if PARAMS.get('bekle'):
        import time  # DOGRULANDI 21.1.2: sandbox'ta time.sleep calisir (19.7 sn'lik render beklendi)
        sn = min(float(PARAMS.get('bekle_sn', 40)), 48.0)
        bit = time.monotonic() + sn
        while time.monotonic() < bit and project.IsRenderingInProgress():
            time.sleep(1.0)
        result['durum'] = project.GetRenderJobStatus(jid)
        if project.IsRenderingInProgress():
            uy.append('Sure doldu, render suruyor. PARAMS={"sorgu_is_id": "%s"} ile sor.' % jid)
    else:
        result['durum'] = project.GetRenderJobStatus(jid)
    d = result['durum'] or {}
    if d.get('JobStatus') in ('Failed', 'Cancelled'):
        h.append('Render %s: %s' % (d.get('JobStatus'), d.get('Error')))


try:
    main()
except Exception as _e:
    result['hatalar'].append('Beklenmeyen hata: %r' % (_e,))
result['ok'] = not result['hatalar']
if _TERMINAL:
    print(result)
