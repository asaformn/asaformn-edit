"""kelime_zamanlari.py - Seslendirmeden kelime kelime zaman çıkarır (faster-whisper).

Kullanım (Mac Terminal):
    pip3 install faster-whisper
    python3 scripts/kelime_zamanlari.py SES_DOSYASI [--model small] [--dil tr] [--cikti kelimeler.json]

Çıktı: [{"w": "kelime", "s": başlangıç_sn, "e": bitiş_sn}, ...]
İlk çalıştırmada model Hugging Face'ten iner (small ≈ 500 MB), sonra önbellekten gelir.
Bulutta çalışırken izinli alanlar: huggingface.co, us.aws.cdn.hf.co, cas-server.xethub.hf.co,
cas-bridge.xethub.hf.co. ffmpeg gerekir. Whisper özel adları yanlış duyabilir; metin elle düzeltilir, zamanlar kalır.
"""
import argparse
import json
import os

from faster_whisper import WhisperModel

ap = argparse.ArgumentParser()
ap.add_argument("ses")
ap.add_argument("--model", default="small")
ap.add_argument("--dil", default="tr")
ap.add_argument("--cikti", default=None)
a = ap.parse_args()

cikti = a.cikti or os.path.splitext(a.ses)[0] + "_kelimeler.json"
m = WhisperModel(a.model, device="cpu", compute_type="int8")
# Ses ffmpeg ile 16 kHz mono float32'ye çözülür (bazı PyAV sürümleri faster-whisper ile uyumsuz).
import subprocess
import numpy as np
ham = subprocess.run(["ffmpeg", "-v", "error", "-i", a.ses, "-f", "f32le", "-ac", "1", "-ar", "16000", "-"],
                     capture_output=True, check=True).stdout
ses = np.frombuffer(ham, np.float32)
segs, info = m.transcribe(ses, language=a.dil, word_timestamps=True, vad_filter=True)
out = []
for s in segs:
    for w in s.words or []:
        out.append({"w": w.word.strip(), "s": round(w.start, 3), "e": round(w.end, 3)})
with open(cikti, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=0)
print("%d kelime -> %s" % (len(out), cikti))
print(" ".join(x["w"] for x in out))
