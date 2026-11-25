"""目標達成までの見積もり（references/goal-estimate.md）の計算。"""
from datetime import date, timedelta

from _common import MissingMaterial, load, need, val


def judge(m):
    name = "goal-estimate"
    wt = load("weight-trend").judge(m)
    if "最新" not in wt:
        raise MissingMaterial(f"{name}: 体重の記録が2日分に満たない")
    goals = need(m, "目標体重", name)
    periods = {"短期": "短期の期間", "中期": "中期の期間", "長期": "長期の期間"}
    current = wt["短期のトレンド"]["直近"]["平均体重"]
    base = date.fromisoformat(wt["最新"]["日付"])
    out = {"起点の体重": current,
           "トレンド": {p: {"差": wt[f"{p}のトレンド"]["差"], "単位": wt[f"{p}のトレンド"]["単位"]} for p in periods},
           "到達見込み": {}}
    for label, t in goals.items():
        remain = round(current - t, 1)
        row = {"体重": t, "残り_kg": remain}
        if remain <= 0:
            row["見込み"] = "到達済み"
        else:
            for p, key in periods.items():
                pace = wt[f"{p}のトレンド"]["差"]
                if pace is None:
                    row[p] = {"見込み": "トレンドが出せないので出せない"}
                elif pace >= 0:
                    row[p] = {"見込み": "減っていないので出せない"}
                else:
                    days = remain / -pace * val("weight-trend", key)
                    row[p] = {"週数": round(days / 7, 1),
                              "見込み日": (base + timedelta(days=days)).isoformat()}
        out["到達見込み"][label] = row
    return out
