"""yerlestir.py - Dosyalari timeline'a kelime zamanina gore yerlestirir.

Parca duzeni: V1 kagit arka plan, V2 sahneler, V3 kartlar/yazilar,
V4 altyazi, A1 seslendirme, A2 sfx, A3 muzik.

PARAMS:
    "timeline": str   (ops.) Timeline adi; yoksa aktif timeline.
    "bin":      str   (ops.) Medya havuzu klasoru, varsayilan "asaformn-edit".
    "kuru":      bool  (ops.) True ise hicbir sey degistirmez, plani dondurur.
    "ogeler": [
        {"dosya": "/mutlak/yol.mov",   # zorunlu
         "parca": "V2",                # zorunlu: V1..Vn veya A1..An
         "bas_sn": 12.48,              # zorunlu: timeline basindan saniye
         "sure_sn": 3.0,               # ops.: timeline'daki sure
         "kaynak_bas_sn": 0.0,         # ops.: kaynaktan baslama noktasi
         "ses_db": -18,                # ops.: ses parcasi seviyesi (dB)
         "yavas": 50}                  # ops.: hiz yuzdesi (<100)
                                       # sure_sn varsa timeline suresi o kadar; yoksa tum kaynak
                                       # yavaslatilmis uzunlukta (2 sn klip %50 -> 4 sn, sonraki klibe binebilir).
                                       # still icin sure_sn SetRightOffset ile uygulanir.
    ]

Ornek:
    PARAMS = {"bin": "asaformn-edit", "kuru": True, "ogeler": [
      {"dosya": "/Users/o/sahne01.mov", "parca": "V2", "bas_sn": 1.2, "sure_sn": 4},
      {"dosya": "/Users/o/whoosh.wav", "parca": "A2", "bas_sn": 1.2, "ses_db": -20}]}

result sekli:
    {"ok", "kuru", "timeline", "fps", "yerlestirilen": [{"i", "dosya", "parca",
      "bas_kare", "bit_kare", "bas_sn", "sure_sn", "yavas", "notlar": []}],
     "eklenen_parcalar": [...], "elle_yapilacak": [str], "uyarilar": [str],
     "hatalar": [str]}
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

result = {'ok': False, 'kuru': bool(PARAMS.get('kuru', False)), 'timeline': None,
          'fps': None, 'yerlestirilen': [], 'eklenen_parcalar': [],
          'elle_yapilacak': [], 'uyarilar': [], 'hatalar': []}


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


def _norm(p):
    return str(p or '').replace('\\', '/').rstrip('/').lower()


def _parca(s):
    """'V2' -> ('video', 2); 'A3' -> ('audio', 3); gecersizse None."""
    try:
        s = str(s).strip().upper()
        if s[0] == 'V':
            t = 'video'
        elif s[0] == 'A':
            t = 'audio'
        else:
            return None
        n = int(s[1:])
        return (t, n) if n >= 1 else None
    except Exception:
        return None


def _sayi(v):
    try:
        return float(v)
    except Exception:
        return None


def _sure_ayarla(it, hedef):
    """Klibin timeline suresini SetRightOffset ile hedef kareye getirir.
    hedef None ise kaynagin sonuna kadar uzatir (ro=0). DOGRULANDI 21.1.2: sure = tam - ro (timeline karesi)."""
    try:
        cur = it.GetEnd() - it.GetStart()
        ro = it.GetRightOffset()
        yeni = 0 if hedef is None else max(0, ro + (cur - hedef))
        if yeni == ro:
            return True
        return bool(it.SetRightOffset(yeni))
    except Exception:
        return False


def _klasorleri_gez(klasor, sonuc, derinlik=0):
    sonuc.append(klasor)
    if derinlik > 6:
        return
    for k in (klasor.GetSubFolderList() or []):
        _klasorleri_gez(k, sonuc, derinlik + 1)


def main():
    h, uy = result['hatalar'], result['uyarilar']
    kuru = result['kuru']
    resolve, project, hata = _baglan()
    if hata:
        h.append(hata)
        return
    ogeler = PARAMS.get('ogeler')
    if not isinstance(ogeler, list) or not ogeler:
        h.append('PARAMS["ogeler"] bos ya da liste degil.')
        return

    # --- timeline
    tl = None
    ad = PARAMS.get('timeline')
    if ad:
        for i in range(1, (project.GetTimelineCount() or 0) + 1):
            t = project.GetTimelineByIndex(i)
            if t and t.GetName() == ad:
                tl = t
                break
        if not tl:
            h.append('Timeline bulunamadi: %r' % ad)
            return
        if not kuru and not project.GetCurrentTimeline() == tl:
            if not project.SetCurrentTimeline(tl):
                h.append('SetCurrentTimeline basarisiz.')
                return
    else:
        tl = project.GetCurrentTimeline()
        if not tl:
            h.append('Aktif timeline yok.')
            return
    result['timeline'] = tl.GetName()
    fps = _fps_duzelt((tl.GetSettings() or {}).get('timelineFrameRate'))
    if not fps:
        h.append('Timeline fps okunamadi.')
        return
    result['fps'] = fps
    t0 = tl.GetStartFrame()

    # --- girdi dogrulama
    plan = []
    for i, o in enumerate(ogeler):
        if not isinstance(o, dict):
            h.append('oge %d: sozluk degil' % i)
            continue
        pr = _parca(o.get('parca'))
        bas = _sayi(o.get('bas_sn'))
        if not o.get('dosya') or not pr or bas is None or bas < 0:
            h.append('oge %d: dosya/parca/bas_sn gecersiz (%r)' % (i, o))
            continue
        sure = _sayi(o.get('sure_sn'))
        yavas = _sayi(o.get('yavas'))
        if yavas is not None and not (0 < yavas < 100):
            uy.append('oge %d: yavas=%s gecersiz (0-100 arasi bekleniyor), yok sayildi' % (i, yavas))
            yavas = None
        if yavas and pr[0] != 'video':
            uy.append('oge %d: yavas sadece video parcasinda uygulanir' % i)
            yavas = None
        bas_f = int(round(t0 + bas * fps))
        sure_f = int(round(sure * fps)) if sure and sure > 0 else None
        plan.append({'i': i, 'o': o, 'tip': pr[0], 'no': pr[1], 'bas_sn': bas,
                     'sure_sn': sure, 'yavas': yavas, 'bas_f': bas_f, 'sure_f': sure_f,
                     'kaynak_bas': _sayi(o.get('kaynak_bas_sn')) or 0.0,
                     'db': _sayi(o.get('ses_db')), 'notlar': []})
    if not plan:
        h.append('Yerlestirilecek gecerli oge yok.')
        return

    # --- ayni parcada cakisma uyarisi (planlanan + mevcut)
    for p in plan:
        if p['sure_f']:
            p['bit_f'] = p['bas_f'] + p['sure_f']
    for a in range(len(plan)):
        for b in range(a + 1, len(plan)):
            x, y = plan[a], plan[b]
            if x['tip'] == y['tip'] and x['no'] == y['no'] and x.get('bit_f') and y.get('bit_f'):
                if x['bas_f'] < y['bit_f'] and y['bas_f'] < x['bit_f']:
                    uy.append('oge %d ve %d ayni parcada cakisiyor (%s%d)' % (x['i'], y['i'], x['tip'][0].upper(), x['no']))
    for p in plan:
        try:
            n = tl.GetTrackCount(p['tip']) or 0
            if p['no'] <= n and p.get('bit_f'):
                for it in (tl.GetItemListInTrack(p['tip'], p['no']) or []):
                    if p['bas_f'] < it.GetEnd() and it.GetStart() < p['bit_f']:
                        uy.append('oge %d mevcut klibin ustune biner: %s' % (p['i'], it.GetName()))
                        break
        except Exception as e:
            uy.append('cakisma kontrolu atlandi: %r' % (e,))

    # --- parcalari hazirla
    for tip in ('video', 'audio'):
        gerek = max([p['no'] for p in plan if p['tip'] == tip] or [0])
        mevcut = tl.GetTrackCount(tip) or 0
        for n in range(mevcut + 1, gerek + 1):
            result['eklenen_parcalar'].append('%s%d' % (tip[0].upper(), n))
            if kuru:
                continue
            ok = False
            if tip == 'audio':
                ok = tl.AddTrack('audio', 'stereo')
            if not ok:
                ok = tl.AddTrack(tip)
            if not ok:
                h.append('%s%d parcasi eklenemedi.' % (tip[0].upper(), n))
        if not kuru and (tl.GetTrackCount(tip) or 0) < gerek:
            h.append('%s parca sayisi yetersiz: %s < %d' % (tip, tl.GetTrackCount(tip), gerek))
    if h:
        return

    mp = project.GetMediaPool()
    kok = mp.GetRootFolder()
    bin_ad = PARAMS.get('bin') or 'asaformn-edit'
    onceki_klasor = mp.GetCurrentFolder()

    # --- bin
    bin_k = None
    for k in (kok.GetSubFolderList() or []):
        if k.GetName() == bin_ad:
            bin_k = k
            break
    if not bin_k and not kuru:
        bin_k = mp.AddSubFolder(kok, bin_ad)
        if not bin_k:
            h.append('Bin olusturulamadi: %s' % bin_ad)
            return
    if not bin_k:
        uy.append('(kuru) "%s" bin\'i olusturulacak.' % bin_ad)

    # --- mevcut medya (yol -> MediaPoolItem), tum klasorlerde
    mevcut = {}
    klasorler = []
    _klasorleri_gez(kok, klasorler)
    for k in klasorler:
        for c in (k.GetClipList() or []):
            try:
                yol = c.GetClipProperty('File Path')
                if yol and _norm(yol) not in mevcut:
                    mevcut[_norm(yol)] = c
            except Exception:
                pass

    # --- tekil dosyalari iceri al
    yeni = []
    for p in plan:
        y = _norm(p['o']['dosya'])
        if y not in mevcut and y not in [_norm(x) for x in yeni]:
            yeni.append(p['o']['dosya'])
    if yeni:
        if kuru:
            uy.append('(kuru) iceri alinacak dosya sayisi: %d' % len(yeni))
        else:
            if not mp.SetCurrentFolder(bin_k):
                h.append('SetCurrentFolder basarisiz.')
                return
            for yol in yeni:
                r = mp.ImportMedia([yol])  # DOGRULANDI 21.1.2: duz yol listesi calisir, [{'FilePath'}] bos doner
                if not r:
                    r = mp.ImportMedia([{'FilePath': yol}])
                if not r:
                    h.append('Iceri alinamadi (yol yanlis/desteklenmiyor): %s' % yol)
                    continue
                mevcut[_norm(yol)] = r[0]
                try:  # Resolve yolu degistirmis olabilir (ornegin sembolik link)
                    gercek = r[0].GetClipProperty('File Path')
                    if gercek:
                        mevcut[_norm(gercek)] = r[0]
                except Exception:
                    pass
            if onceki_klasor:
                mp.SetCurrentFolder(onceki_klasor)

    # --- yerlestir
    rt = getattr(resolve, 'RETIME_OPTICAL_FLOW', None)
    me = getattr(resolve, 'MOTION_EST_SPEED_WARP_BETTER', None)
    for p in plan:
        o = p['o']
        kayit = {'i': p['i'], 'dosya': o['dosya'], 'parca': '%s%d' % (p['tip'][0].upper(), p['no']),
                 'bas_sn': p['bas_sn'], 'sure_sn': p['sure_sn'], 'yavas': p['yavas'],
                 'bas_kare': p['bas_f'], 'bit_kare': None, 'notlar': p['notlar']}
        result['yerlestirilen'].append(kayit)
        if kuru:
            continue
        mpi = mevcut.get(_norm(o['dosya']))
        if not mpi:
            h.append('oge %d: medya bulunamadi %s' % (p['i'], o['dosya']))
            continue
        prop = {}
        try:
            prop = mpi.GetClipProperty() or {}
        except Exception:
            pass
        tur = str(prop.get('Type', '')).lower()
        info = {'mediaPoolItem': mpi, 'trackIndex': p['no'], 'recordFrame': p['bas_f'],
                'mediaType': 1 if p['tip'] == 'video' else 2}
        # kaynak araligi
        cf = _sayi(prop.get('FPS')) if p['tip'] == 'video' else None
        cf = cf if cf else fps  # ses/still icin timeline fps varsayilir
        carpan = (p['yavas'] / 100.0) if p['yavas'] else 1.0
        still = tur.startswith('still') or (p['tip'] == 'video' and not _sayi(prop.get('FPS')) and 'audio' not in tur)
        if still:
            # DOGRULANDI 21.1.2: still icin startFrame/endFrame yok sayilir (varsayilan 5 sn);
            # sure, eklendikten sonra SetRightOffset ile ayarlanir.
            if not p['sure_f']:
                p['notlar'].append('still: sure_sn verilmedi, Resolve varsayilan suresi kullanildi')
        elif p['yavas']:
            # DOGRULANDI 21.1.2: SetSpeed (ripple kapali) suresi degistirmez; bu yuzden tum
            # kaynak eklenir, hiz verilir, sonra SetRightOffset ile sure ayarlanir.
            if p['kaynak_bas']:
                try:
                    info['startFrame'] = int(round(p['kaynak_bas'] * cf))
                    info['endFrame'] = int(float(prop.get('Frames')))
                except Exception:
                    h.append('oge %d: kaynak_bas_sn icin Frames okunamadi' % p['i'])
                    continue
        elif p['sure_f'] or p['kaynak_bas']:
            kb = int(round(p['kaynak_bas'] * cf))
            if p['sure_f']:
                uz = int(round(p['sure_f'] * (cf / fps)))
                info['startFrame'] = kb
                info['endFrame'] = kb + max(uz, 1)  # DOGRULANDI 21.1.2: endFrame DAHIL DEGIL (uzunluk = end - start)
            else:
                try:
                    toplam = int(float(prop.get('Frames')))
                    info['startFrame'] = kb
                    info['endFrame'] = toplam
                except Exception:
                    h.append('oge %d: kaynak_bas_sn icin sure_sn gerekli (Frames okunamadi)' % p['i'])
                    continue
        try:
            sonuc = mp.AppendToTimeline([info])
        except Exception as e:
            h.append('oge %d: AppendToTimeline hata %r' % (p['i'], e))
            continue
        if not sonuc or not sonuc[0]:
            h.append('oge %d: AppendToTimeline bos dondu (%s)' % (p['i'], o['dosya']))
            continue
        it = sonuc[0]
        if still and p['sure_f'] and not _sure_ayarla(it, p['sure_f']):
            p['notlar'].append('still suresi ayarlanamadi (SetRightOffset)')
        # yavaslatma
        if p['yavas']:
            ok = False
            try:
                ok = it.SetSpeed({'Percentage': p['yavas'], 'RippleTimeline': False})
            except Exception as e:
                p['notlar'].append('SetSpeed hata %r' % (e,))
            if not ok:
                result['elle_yapilacak'].append('oge %d (%s, %s): hiz %%%s elle ayarlanmali; sonra Retime Process=Optical Flow, Motion Estimation=AI Speed Warp Better' % (p['i'], it.GetName(), kayit['parca'], p['yavas']))
            else:
                # sure_sn varsa o kadar, yoksa tum kaynak yavaslatilmis halde (sonraki klibin ustune binebilir)
                if not _sure_ayarla(it, p['sure_f']):
                    p['notlar'].append('yavas klip suresi ayarlanamadi (SetRightOffset)')
                ok2 = False
                if rt is not None and me is not None:
                    try:
                        ok2 = it.SetProperties({'RetimeAndScalingEnabled': True, 'RetimeProcess': rt, 'MotionEstimation': me})
                        if not ok2:  # bazi surumler Enabled anahtarini istemeyebilir
                            ok2 = it.SetProperties({'RetimeProcess': rt, 'MotionEstimation': me})
                    except Exception as e:
                        p['notlar'].append('Retime ayar hata %r' % (e,))
                    if ok2:
                        try:
                            g = it.GetProperties() or {}
                            if g.get('RetimeProcess') != rt or g.get('MotionEstimation') != me:
                                ok2 = False
                                p['notlar'].append('Retime degerleri dogrulanamadi: %r/%r' % (g.get('RetimeProcess'), g.get('MotionEstimation')))
                        except Exception:
                            pass
                if not ok2:
                    result['elle_yapilacak'].append('oge %d (%s, %s): Retime and Scaling -> Retime Process=Optical Flow, Motion Estimation=AI Speed Warp Better elle ayarlanmali' % (p['i'], it.GetName(), kayit['parca']))
        # ses seviyesi
        if p['db'] is not None and p['tip'] == 'audio':
            ok = False
            try:
                ok = it.SetProperties({'AudioVolumeEnabled': True, 'AudioVolume': p['db']})
                if not ok:
                    ok = it.SetProperties({'AudioVolume': p['db']})
            except Exception as e:
                p['notlar'].append('AudioVolume hata %r' % (e,))
            if not ok:
                result['elle_yapilacak'].append('oge %d (%s): ses seviyesi %s dB elle ayarlanmali' % (p['i'], it.GetName(), p['db']))
        # dogrulama
        try:
            kayit['bas_kare'] = it.GetStart()
            kayit['bit_kare'] = it.GetEnd()
            kayit['sure_sn'] = round((kayit['bit_kare'] - kayit['bas_kare']) / fps, 3)
            if abs(kayit['bas_kare'] - p['bas_f']) > 1:
                uy.append('oge %d: baslangic %s beklenen %s' % (p['i'], kayit['bas_kare'], p['bas_f']))
            if p['sure_f'] and abs((kayit['bit_kare'] - kayit['bas_kare']) - p['sure_f']) > 1:
                uy.append('oge %d: sure %s kare, beklenen %s (hiz/endFrame/still)' % (p['i'], kayit['bit_kare'] - kayit['bas_kare'], p['sure_f']))
        except Exception as e:
            p['notlar'].append('dogrulama okunamadi %r' % (e,))


try:
    main()
except Exception as _e:
    result['hatalar'].append('Beklenmeyen hata: %r' % (_e,))
result['ok'] = not result['hatalar']
if _TERMINAL:
    print(result)
