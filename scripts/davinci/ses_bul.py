"""ses_bul.py - Seslendirmeyi bul (SADECE OKUR, hicbir seyi degistirmez).

Aktif (ya da adi verilen) timeline'in bilgisini ve ses parcasindaki
(varsayilan A1) butun kliplerin adini, kare/saniye araligini ve kaynak dosya
yolunu dondurur.

PARAMS (hepsi istege bagli):
    "timeline": str   Timeline adi. Yoksa aktif timeline.
    "parca":    int | "A1"   Ses parcasi (varsayilan 1 = A1).
    "kuru":     bool  Bu script zaten salt okunur; kabul edilir, etkisi yok.

Ornek:
    PARAMS = {"parca": "A1"}

result sekli:
    {
      "ok": bool,
      "timeline": {"ad", "fps", "genislik", "yukseklik", "baslangic_kare",
                   "baslangic_tc", "bitis_kare", "sure_sn",
                   "parca_sayisi": {"video", "audio", "subtitle"}},
      "sesler": [{"ad", "parca", "bas_kare", "bit_kare",
                  "bas_sn", "bit_sn",           # timeline basindan itibaren
                  "sure_kare", "sure_sn", "dosya", "aktif"}],
      "hatalar": [str]
    }
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

result = {'ok': False, 'timeline': {}, 'sesler': [], 'hatalar': []}


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


def _timeline_bul(project, ad):
    if not ad:
        return project.GetCurrentTimeline()
    for i in range(1, (project.GetTimelineCount() or 0) + 1):
        t = project.GetTimelineByIndex(i)
        if t and t.GetName() == ad:
            return t
    return None


def _parca_no(v):
    if isinstance(v, int):
        return v
    s = str(v or 'A1').strip().upper()
    if s.startswith('A'):
        s = s[1:]
    return int(s)


def main():
    h = result['hatalar']
    resolve_, project_, hata = _baglan()
    if hata:
        h.append(hata)
        return
    tl = _timeline_bul(project_, PARAMS.get('timeline'))
    if not tl:
        h.append('Timeline bulunamadi: %r' % (PARAMS.get('timeline'),))
        return
    try:
        ayar = tl.GetSettings() or {}
    except Exception as e:
        ayar = {}
        h.append('GetSettings basarisiz: %r' % (e,))
    fps = _fps_duzelt(ayar.get('timelineFrameRate'))
    if not fps:
        h.append('Timeline fps okunamadi.')
        return
    bas = tl.GetStartFrame()
    bit = tl.GetEndFrame()
    sayilar = {}
    for tip in ('video', 'audio', 'subtitle'):
        try:
            sayilar[tip] = tl.GetTrackCount(tip)
        except Exception as e:
            sayilar[tip] = None
            h.append('GetTrackCount(%s): %r' % (tip, e))
    result['timeline'] = {
        'ad': tl.GetName(), 'fps': fps,
        'genislik': ayar.get('timelineResolutionWidth'),
        'yukseklik': ayar.get('timelineResolutionHeight'),
        'baslangic_kare': bas, 'baslangic_tc': tl.GetStartTimecode(),
        'bitis_kare': bit,
        'sure_sn': round((bit - bas) / fps, 3) if bit is not None and bas is not None else None,
        'parca_sayisi': sayilar,
    }
    try:
        no = _parca_no(PARAMS.get('parca', 1))
    except Exception:
        h.append('Gecersiz parca: %r' % (PARAMS.get('parca'),))
        return
    if not sayilar.get('audio') or no > sayilar['audio'] or no < 1:
        h.append('A%s parcasi yok (ses parcasi sayisi: %s).' % (no, sayilar.get('audio')))
        return
    items = tl.GetItemListInTrack('audio', no)
    if items is None:
        h.append('GetItemListInTrack None dondurdu.')
        return
    for it in items:
        try:
            s = it.GetStart()
            e = it.GetEnd()
            dosya = None
            mpi = it.GetMediaPoolItem()
            if mpi:
                dosya = mpi.GetClipProperty('File Path') or None
            else:
                h.append('Klibin MediaPoolItem yok (ic ice/nested olabilir): %s' % it.GetName())
            result['sesler'].append({
                'ad': it.GetName(), 'parca': 'A%d' % no,
                'bas_kare': s, 'bit_kare': e,
                'bas_sn': round((s - bas) / fps, 3), 'bit_sn': round((e - bas) / fps, 3),
                'sure_kare': e - s, 'sure_sn': round((e - s) / fps, 3),
                'dosya': dosya, 'aktif': it.GetClipEnabled() if hasattr(it, 'GetClipEnabled') else None,
            })
        except Exception as ex:
            h.append('Klip okunamadi: %r' % (ex,))
    result['sesler'].sort(key=lambda d: d['bas_kare'])
    if not result['sesler']:
        h.append('A%d parcasinda klip yok.' % no)


try:
    main()
except Exception as _e:
    result['hatalar'].append('Beklenmeyen hata: %r' % (_e,))
result['ok'] = not result['hatalar'] and bool(result['sesler'])
if _TERMINAL:
    print(result)
