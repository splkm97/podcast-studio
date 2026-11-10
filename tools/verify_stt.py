"""Gate: transcribe each synthesized segment and compare with its tts text.

Before comparing, English terms the recognizer writes in Latin script are
mapped back to Hangul via the glossary, and digits are read out, so only
real pronunciation drift raises the character error rate (CER).

usage: python3 -m tools.verify_stt episodes/<id> [--only s003,s010]
"""
import argparse
import re

from tools.common import episode_dir, finish_gate, load_config, load_glossary, read_json
from tools.stt import get_engine

DIGITS = "영일이삼사오육칠팔구"
UNITS = ["", "십", "백", "천"]


def read_int(n: int) -> str:
    if n == 0:
        return "영"
    out, groups = "", ["", "만", "억"]
    for gi, g in enumerate(groups):
        chunk = (n // 10 ** (4 * gi)) % 10000
        if not chunk:
            continue
        part = ""
        for i in range(3, -1, -1):
            d = (chunk // 10 ** i) % 10
            if d:
                part += ("" if d == 1 and i else DIGITS[d]) + UNITS[i]
        if gi and part == "일":
            part = ""  # 만, not 일만
        out = part + g + out
    return out


def read_numbers(text: str) -> str:
    def repl(m):
        whole, _, frac = m.group(0).partition(".")
        s = read_int(int(whole))
        return s + ("점" + read_int(int(frac)) if frac else "")
    return re.sub(r"\d+(?:\.\d+)?", repl, text)


NATIVE_ONES = ["", "한", "두", "세", "네", "다섯", "여섯", "일곱", "여덟", "아홉"]
NATIVE_TENS = ["", "열", "스물", "서른", "마흔", "쉰", "예순", "일흔", "여든", "아흔"]
# Counters read with native Korean numerals ("세 대", "두 가지"); the recognizer writes digits.
NATIVE_COUNTER = re.compile(r"(?<!\d)([1-9]\d?)\s*(대|개|명|곳|가지|표|번째|살|시간)")


def read_native(n: int) -> str:
    word = NATIVE_TENS[n // 10] + NATIVE_ONES[n % 10]
    return "스무" if n == 20 else word


def normalize(text: str, glossary: dict) -> str:
    text = NATIVE_COUNTER.sub(lambda m: read_native(int(m.group(1))) + m.group(2), text)
    # Recognizers sometimes dot acronyms ("H.A."); collapse so the glossary can match.
    text = re.sub(r"\b(?:[A-Za-z]\.){2,}", lambda m: m.group(0).replace(".", ""), text)
    for en in sorted(glossary, key=len, reverse=True):
        text = re.sub(rf"(?<![A-Za-z]){re.escape(en)}(?![A-Za-z])", glossary[en], text,
                      flags=re.IGNORECASE)
    text = read_numbers(text)
    return re.sub(r"[^가-힣a-z]", "", text.lower())


def cer(ref: str, hyp: str) -> float:
    if not ref:
        return 0.0 if not hyp else 1.0
    prev = list(range(len(hyp) + 1))
    for i, rc in enumerate(ref, 1):
        cur = [i]
        for j, hc in enumerate(hyp, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (rc != hc)))
        prev = cur
    return prev[-1] / len(ref)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("episode")
    ap.add_argument("--only", default="")
    a = ap.parse_args()

    ep = episode_dir(a.episode)
    cfg = load_config()["stt"]
    engine = get_engine(cfg)
    glossary = load_glossary(ep)
    only = set(filter(None, a.only.split(",")))
    segs = read_json(ep / "script.json")["segments"]

    prev_p = ep / "gates" / "stt.json"
    results = {r["id"]: r for r in read_json(prev_p).get("results", [])} if (only and prev_p.exists()) else {}
    for s in segs:
        if only and s["id"] not in only:
            continue
        heard = engine.transcribe(ep / "audio" / "segments" / f"{s['id']}.wav")
        score = cer(normalize(s["tts"], glossary), normalize(heard, glossary))
        results[s["id"]] = {"id": s["id"], "cer": round(score, 3), "expected": s["tts"], "heard": heard}

    ordered = [results[s["id"]] for s in segs if s["id"] in results]
    problems = [f"{r['id']}: CER {r['cer']}" for r in ordered if r["cer"] > cfg["max_cer"]]
    finish_gate(ep, "stt", problems, {"max_cer": cfg["max_cer"], "results": ordered})


if __name__ == "__main__":
    main()
