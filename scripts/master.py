"""master.py - Render edilmiş videonun sesini -14 LUFS / -1 dBTP'ye çeker (ffmpeg loudnorm, iki geçiş).

Kullanım:
    python3 scripts/master.py GIRDI.mp4 [--cikti GIRDI_master.mp4] [--lufs -14] [--tp -1]

- Görüntü yeniden kodlanmaz (-c:v copy); sadece ses işlenir (AAC 320k, 48 kHz).
- 1. geçiş ölçer, 2. geçiş ölçüme göre doğrusal (linear) normalize eder; dinamik bozulmaz.
- AAC kodlaması tepe değerini biraz yükselttiği için iç hedef 0,5 dB daha düşük tutulur,
  sonra sonuç tekrar ölçülür. Tepe hâlâ sınırın üstündeyse kazanç düşürülüp bir kez daha denenir.
- Bitince ölçülen değerleri yazar; kontrol.py ile ayrıca doğrulanabilir.
Kurallar: kurallar/ses-miksi.md (-14 LUFS entegre, -1 dBTP; uzun video, Shorts, Reels, TikTok için tek master).
"""
import argparse
import json
import os
import re
import subprocess
import sys


def calistir(komut):
    return subprocess.run(komut, capture_output=True, text=True)


def olc(dosya, lufs, tp):
    """loudnorm ile ölçer; I, TP, LRA, thresh, offset döner."""
    r = calistir(["ffmpeg", "-hide_banner", "-nostats", "-i", dosya, "-vn",
                  "-af", "loudnorm=I=%s:TP=%s:LRA=11:print_format=json" % (lufs, tp), "-f", "null", "-"])
    m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", r.stderr, re.S)
    if not m:
        sys.exit("Ölçüm okunamadı:\n" + r.stderr[-1500:])
    return json.loads(m.group(0))


def kanal_duzeni(dosya):
    r = calistir(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=channels",
                  "-of", "csv=p=0", dosya])
    try:
        return "mono" if int(r.stdout.strip()) == 1 else "stereo"
    except ValueError:
        return "stereo"


def uygula(girdi, cikti, o, lufs, tp, ek_kazanc_db=0.0):
    af = ("loudnorm=I={L}:TP={T}:LRA=11:measured_I={i}:measured_TP={t}:measured_LRA={l}:"
          "measured_thresh={th}:offset={of}:linear=true:print_format=summary").format(
        L=lufs, T=tp, i=o["input_i"], t=o["input_tp"], l=o["input_lra"], th=o["input_thresh"], of=o["target_offset"])
    if ek_kazanc_db:
        af += ",volume=%sdB" % ek_kazanc_db
    # Eski ffmpeg (4.4) loudnorm sonrasi kanal duzenini secemiyor; acikca belirtilir.
    af += ",aresample=48000,aformat=sample_fmts=fltp:channel_layouts=%s" % kanal_duzeni(girdi)
    r = calistir(["ffmpeg", "-hide_banner", "-y", "-i", girdi, "-map", "0:v?", "-map", "0:a:0",
                  "-c:v", "copy", "-af", af, "-c:a", "aac", "-b:a", "320k", "-ar", "48000",
                  "-movflags", "+faststart", cikti])
    if r.returncode != 0:
        sys.exit("Mastering başarısız:\n" + r.stderr[-1500:])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("girdi")
    ap.add_argument("--cikti")
    ap.add_argument("--lufs", type=float, default=-14.0)
    ap.add_argument("--tp", type=float, default=-1.0)
    a = ap.parse_args()
    kok, uz = os.path.splitext(a.girdi)
    cikti = a.cikti or kok + "_master" + (uz or ".mp4")
    ic_tp = a.tp - 0.5

    once = olc(a.girdi, a.lufs, ic_tp)
    print("Önce : %s LUFS, tepe %s dBTP" % (once["input_i"], once["input_tp"]))
    uygula(a.girdi, cikti, once, a.lufs, ic_tp)
    sonra = olc(cikti, a.lufs, ic_tp)
    if float(sonra["input_tp"]) > a.tp:
        fark = round(a.tp - float(sonra["input_tp"]) - 0.2, 2)
        print("Tepe %s dBTP, sınırın üstünde; %s dB düşürülüp tekrar yapılıyor." % (sonra["input_tp"], fark))
        uygula(a.girdi, cikti, once, a.lufs, ic_tp, ek_kazanc_db=fark)
        sonra = olc(cikti, a.lufs, ic_tp)
    print("Sonra: %s LUFS, tepe %s dBTP -> %s" % (sonra["input_i"], sonra["input_tp"], cikti))
    ok_l = abs(float(sonra["input_i"]) - a.lufs) <= 1.0
    ok_t = float(sonra["input_tp"]) <= a.tp
    print("LUFS %s, tepe %s" % ("GEÇTİ" if ok_l else "KALDI", "GEÇTİ" if ok_t else "KALDI"))
    sys.exit(0 if ok_l and ok_t else 1)


if __name__ == "__main__":
    main()
