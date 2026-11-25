"""進捗の良し悪し（references/progress.md）の計算。"""
from _common import load, val


def _pace(gap, lo, hi):
    """減り幅が lo〜hi なら良い。小さければ（増えている場合を含む）遅い、大きければ速すぎ。"""
    if gap is None:
        return None
    loss = -gap
    return "遅い" if loss < lo else "速すぎ" if loss > hi else "良い"


def judge(m):
    name = "progress"
    wt = load("weight-trend").judge(m)
    lo, hi = val(name, "良いペースの減り幅の下限"), val(name, "良いペースの減り幅の上限")
    out = {}
    for label in ("短期", "中期", "長期"):
        trend = wt.get(f"{label}のトレンド") or {}
        scale = val("weight-trend", f"{label}の期間") / 30
        pace = _pace(trend.get("差"), lo * scale, hi * scale)
        out[label] = {"結果": "判断できない" if pace is None else "良い" if pace == "良い" else "良くない",
                      "ペース": pace, "トレンド": trend.get("差"), "単位": trend.get("単位"),
                      "良いペースの範囲": [round(-hi * scale, 2), round(-lo * scale, 2)]}
    return out
