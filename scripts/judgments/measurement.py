"""採用する体重記録（references/measurement.md）の計算。"""
from datetime import datetime

from _common import load, need, val


def judge(m):
    name = "measurement"
    window_h = val(name, "起床後の採用範囲")
    records = sorted([r for r in need(m, "体重の記録", name)
                      if r.get("日時") and r.get("体重") is not None], key=lambda r: r["日時"])
    nights = need(m, "夜間睡眠", name)
    wake = {day: n["終了"] for day, n in load("sleep-time-source")._sleep_sections(m).items()}

    series = []
    for day in sorted({r["日時"][:10] for r in records}):
        w = wake.get(day)
        if not w:
            continue
        todays = [r for r in records if r["日時"][:10] == day]
        picked = next((r for r in todays if 0 <= (
            datetime.fromisoformat(r["日時"]) - datetime.fromisoformat(w)
        ).total_seconds() <= window_h * 3600), None)
        if picked is None:
            picked = next((r for r in todays if any(
                n.get("開始") and n.get("終了") and n["開始"] < r["日時"] < n["終了"]
                for n in nights)), None)
        if picked:
            series.append({"日付": day, "体重": picked["体重"], "記録": picked})
    return {"日次系列": series}
