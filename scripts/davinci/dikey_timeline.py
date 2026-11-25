"""dikey_timeline.py - Her kesit icin 1080x1920 bir timeline iskeleti kurar.

Kaynak timeline'daki [bas_sn, bit_sn] araligina denk gelen kliplerin kirpilmis
kopyalarini AYNI parca numaralarina koyar. Grafikler SONRADAN yeniden
yerlestirilir (kirpilmaz); bu script yalnizca iskelet kurar.
Kopyalanamayanlar (Fusion baslik, generator, gecis, ic ice timeline) raporlanir.

PARAMS:
    "kaynak_timeline": str   Zorunlu. Kaynak (yatay) timeline adi.
    "kesitler": [{"ad": "kesit1", "bas_sn": 12.0, "bit_sn": 50.0}]  (sn, timeline basindan)
    "kuru": bool             True ise hicbir sey olusturmaz, plani dondurur.
    "genislik": 1080, "yukseklik": 1920   (ops.)

Ornek:
    PARAMS = {"kaynak_timeline": "Ana Video",
              "kesitler": [{"ad": "Kesit 1", "bas_sn": 30, "bit_sn": 68}]}

result sekli:
    {"ok", "kuru", "kaynak_fps", "timeline_lar": [{"ad", "olusturuldu",
       "ayar_dogrulama": {...}, "kopyalanan": int,
       "kopyalanamayan": [{"parca", "ad", "bas_sn", "neden"}], "uyarilar": []}],
     "hatalar": []}
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

result = {'ok': False, 'kuru': bool(PARAMS.get('kuru', False)), 'kaynak_fps': None,
          'timeline_lar': [], 'hatalar': []}


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


def _fps_metin(v):
    """SetSettings fps degerini metne cevirir. DOGRULANDI 21.1.2: "25" kabul edilir, "25.0" REDDEDILIR (False);
    tam sayi ise ondaliksiz, degilse en kisa gosterim (23.976)."""
    try:
        return '%g' % float(v)
    except Exception:
        return str(v)


def _sure_ayarla(it, hedef):
    """Timeline suresini SetRightOffset ile hedef kareye getirir (DOGRULANDI 21.1.2: sure = tam - ro)."""
    try:
        cur = it.GetEnd() - it.GetStart()
        ro = it.GetRightOffset()
        yeni = max(0, ro + (cur - hedef))
        if yeni == ro:
            return True
        return bool(it.SetRightOffset(yeni))
    except Exception:
        return False


def _tl_bul(project, ad):
    for i in range(1, (project.GetTimelineCount() or 0) + 1):
        t = project.GetTimelineByIndex(i)
        if t and t.GetName() == ad:
            return t
    return None


def main():
    h = result['hatalar']
    resolve, project, hata = _baglan()
    if hata:
        h.append(hata)
        return
    kuru = result['kuru']
    kesitler = PARAMS.get('kesitler')
    kaynak_ad = PARAMS.get('kaynak_timeline')
    if not kaynak_ad or not isinstance(kesitler, list) or not kesitler:
        h.append('kaynak_timeline ve kesitler zorunlu.')
        return
    src = _tl_bul(project, kaynak_ad)
    if not src:
        h.append('Kaynak timeline bulunamadi: %r' % kaynak_ad)
        return
    ayar = src.GetSettings() or {}
    fps_ham = ayar.get('timelineFrameRate')
    fps = _fps_duzelt(fps_ham)
    if not fps:
        h.append('Kaynak fps okunamadi.')
        return
    result['kaynak_fps'] = fps
    s0 = src.GetStartFrame()
    W = str(int(PARAMS.get('genislik', 1080)))
    H = str(int(PARAMS.get('yukseklik', 1920)))

    # kaynak parcalardaki klipleri bir kez oku
    parcalar = {}
    for tip in ('video', 'audio'):
        for n in range(1, (src.GetTrackCount(tip) or 0) + 1):
            parcalar[(tip, n)] = src.GetItemListInTrack(tip, n) or []
    st = src.GetTrackCount('subtitle') or 0
    mp = project.GetMediaPool()
    onceki = project.GetCurrentTimeline()

    for k in kesitler:
        kayit = {'ad': None, 'olusturuldu': False, 'ayar_dogrulama': {}, 'kopyalanan': 0,
                 'kopyalanamayan': [], 'uyarilar': []}
        result['timeline_lar'].append(kayit)
        try:
            bas = float(k['bas_sn'])
            bit = float(k['bit_sn'])
            ad = '%s (dikey)' % k['ad']
        except Exception:
            h.append('Gecersiz kesit: %r' % (k,))
            continue
        kayit['ad'] = ad
        if bit <= bas or bas < 0:
            h.append('%s: bit_sn > bas_sn olmali' % ad)
            continue
        if _tl_bul(project, ad):
            h.append('%s: bu adda timeline zaten var, atlandi.' % ad)
            continue
        bas_f = int(round(s0 + bas * fps))
        bit_f = int(round(s0 + bit * fps))

        # kopyalanacaklari belirle
        plan = []
        for (tip, n), items in parcalar.items():
            for it in items:
                try:
                    s, e = it.GetStart(), it.GetEnd()
                    if not (s < bit_f and e > bas_f):
                        continue
                    mpi = it.GetMediaPoolItem()
                    ad_i = it.GetName()
                    tur = it.GetType() if hasattr(it, 'GetType') else ''
                    if tur in ('transition',):
                        kayit['kopyalanamayan'].append({'parca': '%s%d' % (tip[0].upper(), n), 'ad': ad_i, 'bas_sn': round((s - s0) / fps, 3), 'neden': 'gecis'})
                        continue
                    if not mpi or tur == 'generator':
                        kayit['kopyalanamayan'].append({'parca': '%s%d' % (tip[0].upper(), n), 'ad': ad_i, 'bas_sn': round((s - s0) / fps, 3), 'neden': 'MediaPoolItem yok (Fusion baslik/generator/ic ice klip)'})
                        continue
                    plan.append((tip, n, it, mpi, s, e))
                except Exception as ex:
                    kayit['uyarilar'].append('klip okunamadi: %r' % (ex,))
        if st:
            kayit['uyarilar'].append('Kaynakta %d altyazi parcasi var; kopyalanmaz (dikeyde kelime kelime yeniden kurulur).' % st)
        if kuru:
            kayit['kopyalanan'] = len(plan)
            continue

        yeni = mp.CreateEmptyTimeline(ad)
        if not yeni:
            h.append('%s: CreateEmptyTimeline basarisiz.' % ad)
            continue
        kayit['olusturuldu'] = True
        if not project.SetCurrentTimeline(yeni):
            h.append('%s: SetCurrentTimeline basarisiz.' % ad)
            continue
        # timeline'a ozel ayarlar, tek tek (hangisi tutmadi gorulsun)
        ayarlar = [('useCustomSettings', '1'), ('timelineResolutionWidth', W),
                   ('timelineResolutionHeight', H), ('timelineFrameRate', _fps_metin(fps_ham)),
                   ('timelineOutputResolutionWidth', W), ('timelineOutputResolutionHeight', H)]
        for a, v in ayarlar:
            # DOGRULANDI 21.1.2: timelineFrameRate bos timeline'da bile False doner; zaten esitse atla.
            if a == 'timelineFrameRate':
                m = _fps_duzelt((yeni.GetSettings() or {}).get(a))
                if m and abs(m - fps) < 0.01:
                    continue
            try:
                ok = yeni.SetSettings({a: v})
            except Exception as ex:
                ok = False
                kayit['uyarilar'].append('SetSettings(%s) hata %r' % (a, ex))
            if not ok:
                kayit['uyarilar'].append('SetSettings(%s=%s) basarisiz' % (a, v))
        g = yeni.GetSettings() or {}
        kayit['ayar_dogrulama'] = {a: g.get(a) for a in ('useCustomSettings', 'timelineResolutionWidth', 'timelineResolutionHeight', 'timelineFrameRate')}
        if str(g.get('timelineResolutionWidth')) != W or str(g.get('timelineResolutionHeight')) != H:
            h.append('%s: cozunurluk %sx%s olarak dogrulanamadi (%sx%s).' % (ad, W, H, g.get('timelineResolutionWidth'), g.get('timelineResolutionHeight')))
            continue
        fy = _fps_duzelt(g.get('timelineFrameRate'))
        if not fy or abs(fy - fps) > 0.01:
            kayit['uyarilar'].append('fps farkli: %s != %s (bos timeline icin fps degisimi kilitli olabilir)' % (fy, fps))

        # parcalari hazirla
        for tip in ('video', 'audio'):
            gerek = max([n for (t, n, *_r) in plan if t == tip] or [0])
            while (yeni.GetTrackCount(tip) or 0) < gerek:
                ok = yeni.AddTrack('audio', 'stereo') if tip == 'audio' else yeni.AddTrack(tip)
                if not ok and tip == 'audio':
                    ok = yeni.AddTrack('audio')
                if not ok:
                    h.append('%s: %s parcasi eklenemedi' % (ad, tip))
                    break
        n0 = yeni.GetStartFrame()
        for tip, n, it, mpi, s, e in sorted(plan, key=lambda x: (x[4], x[0], x[1])):
            cs, ce = max(s, bas_f), min(e, bit_f)
            try:
                pct = 100.0
                try:
                    sp = it.GetSpeed() or {}
                    pct = float(sp.get('Percentage', 100.0)) or 100.0
                except Exception:
                    pass
                kaynak_bas = it.GetSourceStartFrame()  # parca basindaki kaynak kare (ses dahil dogru calisiyor mu: README)
                a = kaynak_bas + int(round((cs - s) * pct / 100.0))
                hedef = ce - cs
                try:
                    tur_i = str(mpi.GetClipProperty('Type') or '').lower()
                except Exception:
                    tur_i = ''
                info = {'mediaPoolItem': mpi, 'trackIndex': n,
                        'recordFrame': n0 + (cs - bas_f), 'mediaType': 1 if tip == 'video' else 2}
                if not tur_i.startswith('still'):
                    # DOGRULANDI 21.1.2: endFrame DAHIL DEGIL. Hizli klipte SetSpeed (ripple kapali) suresi
                    # degistirmez, bu yuzden hedef kadar kaynak eklenir; hiz sonra verilir.
                    info['startFrame'] = a
                    info['endFrame'] = a + max(hedef, 1)
                r = mp.AppendToTimeline([info])
                if not r or not r[0]:
                    kayit['kopyalanamayan'].append({'parca': '%s%d' % (tip[0].upper(), n), 'ad': it.GetName(), 'bas_sn': round((s - s0) / fps, 3), 'neden': 'AppendToTimeline basarisiz'})
                    continue
                kayit['kopyalanan'] += 1
                if not _sure_ayarla(r[0], hedef):  # still ya da kaynak ucu: sure hedefe cekilir
                    kayit['uyarilar'].append('%s: sure ayarlanamadi' % it.GetName())
                if tip == 'audio':  # DOGRULANDI 21.1.2: AudioVolume kopyayla gelmiyor, elle tasinir
                    try:
                        vol = it.GetProperty('AudioVolume')
                        if vol not in (None, 0, 0.0):
                            r[0].SetProperties({'AudioVolumeEnabled': True, 'AudioVolume': vol})
                    except Exception:
                        kayit['uyarilar'].append('%s: ses seviyesi kopyalanamadi' % it.GetName())
                if abs(pct - 100.0) > 0.01 and tip == 'video':
                    r[0].SetSpeed({'Percentage': pct, 'RippleTimeline': False})
                    try:
                        r[0].SetProperties({'RetimeAndScalingEnabled': True,
                                            'RetimeProcess': resolve.RETIME_OPTICAL_FLOW,
                                            'MotionEstimation': resolve.MOTION_EST_SPEED_WARP_BETTER})
                    except Exception:
                        kayit['uyarilar'].append('%s: Optical Flow/Speed Warp Better elle ayarlanmali' % it.GetName())
            except Exception as ex:
                kayit['kopyalanamayan'].append({'parca': '%s%d' % (tip[0].upper(), n), 'ad': it.GetName(), 'bas_sn': round((s - s0) / fps, 3), 'neden': repr(ex)})
    if onceki and not kuru:
        project.SetCurrentTimeline(onceki)


try:
    main()
except Exception as _e:
    result['hatalar'].append('Beklenmeyen hata: %r' % (_e,))
result['ok'] = not result['hatalar']
if _TERMINAL:
    print(result)
