#!/usr/bin/env python3
"""Delivery checks for a rendered video.

Runs blank-start, frozen-moment, loudness, platform compliance, contact sheet
and length checks, then writes rapor.json and rapor.md to an output folder.

Usage:
  python3 scripts/kontrol.py VIDEO --platform {youtube,shorts,reels,tiktok} [--out DIR] [--length SECONDS]

Standard library only. Vendor tools are called through subprocess.
Exit code 1 if any check is KALDI.
"""
import argparse
import datetime
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
VENDOR = REPO / "vendor"
CHECK_PY = VENDOR / "ffmpeg-skill" / "scripts" / "check.py"
LOOK_PY = VENDOR / "ffmpeg-skill" / "scripts" / "look.py"
FROZEN_SH = VENDOR / "motion-video-kit" / "frozen-time.sh"
LOUDNESS_SH = VENDOR / "motion-video-kit" / "loudness.sh"

PLATFORMS = ("youtube", "shorts", "reels", "tiktok")
VERTICAL_PLATFORMS = ("shorts", "reels", "tiktok")

BLANK_WARN_S = 0.04      # leading blank longer than this is a WARN
FLASH_MAX_S = 0.25       # middle blank shorter than this is a flash
FROZEN_MIN_S = 2.0       # frozen ranges at least this long are reported
SAMPLE_DT = 0.1          # frozen-time.sh samples at 10 fps
LOUD_TARGET = -14.0
LOUD_PASS_TOL = 1.0
LOUD_WARN_TOL = 2.0
TP_MAX = -1.0
FLAT_SPREAD = 3          # max min..max spread (8-bit) for a "flat" frame

SEVERITY = {"GEÇTİ": 0, "UYARI": 1, "KALDI": 2}
OK, WARN, FAIL = "GEÇTİ", "UYARI", "KALDI"
CHECK_MAP = {"PASS": OK, "WARN": WARN, "FAIL": FAIL}


def run(cmd, timeout=1800):
    p = subprocess.run(cmd, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=timeout)
    return p.returncode, p.stdout, p.stderr


def record(name, durum, ayrinti, veri=None, images=None):
    return {"kontrol": name, "durum": durum, "ayrinti": ayrinti,
            "veri": veri or {}, "images": images or []}


def probe_duration(video):
    rc, out, err = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=nw=1:nk=1", str(video)], timeout=120)
    if rc or not out.strip():
        raise RuntimeError(err.strip() or "ffprobe gave no duration")
    return float(out.strip())


# ---------- 1. blank start and flashes ----------

BLACK_RE = re.compile(r"black_start:(-?[\d.]+) black_end:([\d.]+) black_duration:([\d.]+)")


def blackdetect(video, negate=False):
    vf = ("negate," if negate else "") + "blackdetect=d=0.04:pix_th=0.10"
    rc, _, err = run(["ffmpeg", "-hide_banner", "-nostdin", "-i", str(video),
                      "-an", "-vf", vf, "-f", "null", "-"], timeout=900)
    if rc:
        raise RuntimeError(f"blackdetect failed: {err.strip()[-300:]}")
    return [(float(a), float(b)) for a, b, _ in BLACK_RE.findall(err)]


FRAME_RE = re.compile(r"frame:\d+\s+pts:\S+\s+pts_time:([\d.]+)")
STAT_RE = re.compile(r"lavfi\.signalstats\.(\w+)=(-?[\d.]+)")


def flat_start(video, seconds=5.0):
    """Length of the leading run of frames that are one flat colour (any colour)."""
    rc, _, err = run(["ffmpeg", "-hide_banner", "-nostdin", "-t", str(seconds), "-i", str(video),
                      "-an", "-vf", "signalstats,metadata=print", "-f", "null", "-"], timeout=300)
    if rc:
        raise RuntimeError(f"signalstats failed: {err.strip()[-300:]}")
    frames, cur = [], None
    for line in err.splitlines():
        m = FRAME_RE.search(line)
        if m:
            cur = {"t": float(m.group(1))}
            frames.append(cur)
            continue
        m = STAT_RE.search(line)
        if m and cur is not None:
            cur[m.group(1)] = float(m.group(2))
    if not frames:
        return 0.0, None
    colour = None
    last_end = 0.0
    for i, f in enumerate(frames):
        flat = all(k in f for k in ("YMIN", "YMAX", "UMIN", "UMAX", "VMIN", "VMAX")) and \
            f["YMAX"] - f["YMIN"] <= FLAT_SPREAD and \
            f["UMAX"] - f["UMIN"] <= FLAT_SPREAD and f["VMAX"] - f["VMIN"] <= FLAT_SPREAD
        if not flat:
            break
        colour = colour or (f.get("YAVG"), f.get("UAVG"), f.get("VAVG"))
        last_end = frames[i + 1]["t"] if i + 1 < len(frames) else seconds
    return last_end, colour


def check_blank(video, duration):
    veri = {}
    lead_black = [(a, b) for a, b in blackdetect(video) if a <= BLANK_WARN_S]
    lead_white = [(a, b) for a, b in blackdetect(video, negate=True) if a <= BLANK_WARN_S]
    if lead_black:
        colour, length = "siyah", lead_black[0][1]
    elif lead_white:
        colour, length = "beyaz", lead_white[0][1]
    else:
        length, flat_col = flat_start(video)
        colour = "tek renk" if length > 0 else None
        if flat_col and length > 0:
            veri["flat_yuv"] = [round(v, 1) if v is not None else None for v in flat_col]
    length = round(length, 2) if colour else 0.0
    veri["baslangic_bosluk_s"] = length
    veri["renk"] = colour
    if length > BLANK_WARN_S:
        durum = WARN
        ayrinti = f"Başta {colour} boşluk: {length:.2f} s (eşik {BLANK_WARN_S} s)"
    else:
        durum = OK
        ayrinti = "Başta boşluk yok"

    # flashes: short blanks after the start (black or white)
    flashes = []
    for negate, label in ((False, "siyah"), (True, "beyaz")):
        for a, b in blackdetect(video, negate=negate):
            if a > BLANK_WARN_S and (b - a) < FLASH_MAX_S:
                flashes.append({"t": round(a, 2), "sure_s": round(b - a, 2), "renk": label})
    flashes.sort(key=lambda x: x["t"])
    veri["flash"] = flashes
    rec_flash = None
    if flashes:
        detay = ", ".join(f"{f['t']:.2f} s ({f['renk']}, {f['sure_s']:.2f} s)" for f in flashes)
        rec_flash = record("Ortadaki flaş (kısa boşluk)", WARN,
                           f"{len(flashes)} adet: {detay}", {"flash": flashes})
    else:
        rec_flash = record("Ortadaki flaş (kısa boşluk)", OK, "Yok")
    return [record("Açılış boşluğu", durum, ayrinti, veri), rec_flash]


# ---------- 2. frozen moments ----------

def check_frozen(video):
    rc, out, err = run(["bash", str(FROZEN_SH), str(video)], timeout=1800)
    if rc:
        raise RuntimeError(f"frozen-time.sh failed: {err.strip()[-300:]}")
    times = []
    for line in out.splitlines():
        if line.startswith("near-frozen"):
            break
        times += [float(x) for x in line.split()]
    groups = []
    for t in times:
        if groups and t - groups[-1][1] <= SAMPLE_DT * 1.5:
            groups[-1][1] = t
        else:
            groups.append([t, t])
    ranges = [{"baslangic_s": round(a, 2), "bitis_s": round(b + SAMPLE_DT, 2),
               "sure_s": round(b + SAMPLE_DT - a, 2)} for a, b in groups]
    long_r = [r for r in ranges if r["sure_s"] >= FROZEN_MIN_S]
    if long_r:
        detay = "; ".join(f"{r['baslangic_s']:.1f}–{r['bitis_s']:.1f} s ({r['sure_s']:.1f} s)"
                          for r in long_r)
        return record("Donmuş kareler (≥2 s)", WARN, detay, {"ranges": ranges, "uzun": long_r})
    return record("Donmuş kareler (≥2 s)", OK, "Yok", {"ranges": ranges, "uzun": []})


# ---------- 3. loudness ----------

def check_loudness(video):
    rc, out, err = run(["bash", str(LOUDNESS_SH), str(video)], timeout=1800)
    i = re.search(r"I:\s*(-?[\d.]+)\s*LUFS", out)
    lra = re.search(r"LRA:\s*([\d.]+)", out)
    tp = re.search(r"Peak:\s*(-?[\d.]+)\s*dBFS", out)   # first Peak line is the true peak
    if not i or not tp:
        raise RuntimeError(f"loudness.sh gave no values: {(err or out).strip()[-300:]}")
    lufs, tpk = float(i.group(1)), float(tp.group(1))
    lra_v = float(lra.group(1)) if lra else None
    veri = {"lufs": lufs, "lra": lra_v, "true_peak_dbtp": tpk}

    d = abs(lufs - LOUD_TARGET)
    if d <= LOUD_PASS_TOL:
        lstat = OK
    elif d <= LOUD_WARN_TOL:
        lstat = WARN
    else:
        lstat = FAIL
    tstat = OK if tpk <= TP_MAX else FAIL
    return [
        record("Ses yüksekliği (hedef -14 LUFS)", lstat,
               f"{lufs:.1f} LUFS, sapma {lufs - LOUD_TARGET:+.1f} LU (PASS ±1, WARN ±2)", veri),
        record("Gerçek tepe (≤ -1 dBTP)", tstat,
               f"{tpk:.1f} dBTP" + (f", LRA {lra_v:.1f} LU" if lra_v is not None else ""), veri),
    ]


# ---------- 4. platform compliance ----------

def check_platform(video, platform):
    rc, out, err = run([sys.executable, str(CHECK_PY), str(video), "--platform", platform,
                        "--content", "--json"], timeout=1800)
    try:
        data = json.loads(out)
    except json.JSONDecodeError:
        raise RuntimeError(f"check.py gave no JSON (exit {rc}): {(err or out).strip()[-300:]}")
    if data.get("status") == "failed" and not data.get("checks"):
        msg = (data.get("error") or {}).get("message") or json.dumps(data.get("error"))[:300]
        return record(f"Platform uyumu ({platform})", WARN, f"check.py çalışmadı: {msg}",
                      {"error": data.get("error")})
    rows = data.get("checks", [])
    worst = OK
    problems = []
    for row in rows:
        st = CHECK_MAP.get(row.get("status"), OK)
        if st == FAIL:
            worst = FAIL
        elif st == WARN and worst == OK:
            worst = WARN
        if st != OK:
            problems.append(f"{row.get('status')} {row.get('check')}: {row.get('fix') or row.get('reason') or ''}".strip())
    ayrinti = "; ".join(problems) if problems else f"{len(rows)} satır, hepsi PASS"
    return record(f"Platform uyumu ({platform})", worst, ayrinti,
                  {"rows": [{"status": r.get("status"), "check": r.get("check"),
                             "value": r.get("value"), "fix": r.get("fix"),
                             "reason": r.get("reason")} for r in rows]})


# ---------- 5. contact sheet and safe frames ----------

def look(video, args, out_png):
    cmd = [sys.executable, str(LOOK_PY), str(video), *args, "-o", str(out_png), "--overwrite"]
    rc, out, err = run(cmd, timeout=900)
    if rc or not out_png.exists():
        raise RuntimeError(f"look.py failed (exit {rc}): {(err or out).strip()[-300:]}")
    return out_png


def check_images(video, platform, duration, outdir):
    recs, images = [], []
    try:
        sheet = look(video, ["--tiles", "4x3"], outdir / "sheet.png")
        images.append(sheet.name)
        recs.append(record("Kontak sayfası", OK, f"{sheet.name} (4x3 kare)", images=[sheet.name]))
    except Exception as e:  # keep going, report the failure
        recs.append(record("Kontak sayfası", WARN, f"Üretilemedi: {e}"))

    if platform in VERTICAL_PLATFORMS:
        shots = []
        for pct in (25, 50, 75):
            t = duration * pct / 100
            try:
                png = look(video, ["--at", f"{t:.3f}", "--safe", platform],
                           outdir / f"safe_{pct}.png")
                shots.append(png.name)
                images.append(png.name)
            except Exception as e:
                recs.append(record(f"Güvenli alan karesi {pct}%", WARN, f"Üretilemedi: {e}"))
        if shots:
            recs.append(record(f"Güvenli alan karesi ({platform})", OK,
                               f"{len(shots)} kare, {platform} arayüzü gölgeli: " + ", ".join(shots),
                               images=shots))
    return recs, images


# ---------- 6. length ----------

def check_length(duration, length):
    tol = max(1.0, 0.05 * length)
    diff = duration - length
    veri = {"sure_s": round(duration, 2), "hedef_s": length, "tolerans_s": round(tol, 2)}
    if abs(diff) > tol:
        return record("Süre", WARN, f"{duration:.2f} s, hedef {length:g} s (fark {diff:+.2f} s, tolerans ±{tol:.2f} s)", veri)
    return record("Süre", OK, f"{duration:.2f} s, hedef {length:g} s", veri)


# ---------- report ----------

def safe(fn, name):
    try:
        return fn()
    except Exception as e:
        return record(name, WARN, f"Kontrol çalışmadı: {e}")


def write_md(path, meta, checks, images):
    lines = [f"# Teslim kontrolü: {meta['video']}", "",
             f"Platform: {meta['platform']} | Süre: {meta['duration']:.2f} s | Tarih: {meta['created']}", "",
             "| Kontrol | Durum | Ayrıntı |", "|---|---|---|"]
    for c in checks:
        ayr = str(c["ayrinti"]).replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {c['kontrol']} | {c['durum']} | {ayr} |")
    lines += ["", "## Görseller", ""]
    lines += [f"- {img}" for img in images] or ["- (yok)"]
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Delivery checks for a rendered video.")
    ap.add_argument("video", help="rendered video file")
    ap.add_argument("--platform", required=True, choices=PLATFORMS)
    ap.add_argument("--out", help="output folder (default: <video-stem>_kontrol next to the video)")
    ap.add_argument("--length", type=float, help="expected duration in seconds")
    args = ap.parse_args(argv)

    video = Path(args.video).resolve()
    if not video.is_file():
        print(f"error: not a file: {video}", file=sys.stderr)
        return 2
    outdir = Path(args.out).resolve() if args.out else video.parent / f"{video.stem}_kontrol"
    outdir.mkdir(parents=True, exist_ok=True)

    duration = probe_duration(video)
    checks = []
    checks += safe(lambda: check_blank(video, duration), "Açılış boşluğu")
    checks.append(safe(lambda: check_frozen(video), "Donmuş kareler (≥2 s)"))
    loud = safe(lambda: check_loudness(video), "Ses yüksekliği (hedef -14 LUFS)")
    checks += loud if isinstance(loud, list) else [loud]
    checks.append(safe(lambda: check_platform(video, args.platform), f"Platform uyumu ({args.platform})"))
    img_recs, images = check_images(video, args.platform, duration, outdir)
    checks += img_recs
    if args.length is not None:
        checks.append(safe(lambda: check_length(duration, args.length), "Süre"))

    overall = max((SEVERITY[c["durum"]] for c in checks), default=0)
    exit_code = 1 if overall == SEVERITY[FAIL] else 0
    meta = {"video": str(video), "platform": args.platform, "duration": duration,
            "length_hedef": args.length, "created": datetime.datetime.now().isoformat(timespec="seconds"),
            "exit_code": exit_code}
    (outdir / "rapor.json").write_text(
        json.dumps({"meta": meta, "checks": checks, "images": images}, ensure_ascii=False, indent=2),
        encoding="utf-8")
    write_md(outdir / "rapor.md", meta, checks, images)

    for c in checks:
        print(f"{c['durum']:6} {c['kontrol']}: {c['ayrinti']}")
    print(f"rapor: {outdir / 'rapor.md'}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
