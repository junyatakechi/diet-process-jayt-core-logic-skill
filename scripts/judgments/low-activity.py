"""あまり動いていない週（references/low-activity.md）の計算。"""
from datetime import date, timedelta

from _common import MissingMaterial, _mean, need, val


def judge(m):
    name = "low-activity"
    steps = need(m, "歩数", name)
    period = need(m, "期間", name).get("評価") or {}
    if not (period.get("開始") and period.get("終了")):
        raise MissingMaterial(f"{name}: 必須の材料「期間」に評価の開始と終了が無い")
    first, last = date.fromisoformat(period["開始"]), date.fromisoformat(period["終了"])
    limit = val(name, "あまり動いていないとする平均歩数")
    by_day = {date.fromisoformat(x["日付"]): x["歩数"] for x in steps if x.get("歩数") is not None}
    weeks, end = [], last
    while end >= first:
        start = end - timedelta(days=6)
        ss = [v for d, v in by_day.items() if start <= d <= end]
        avg = round(_mean(ss)) if ss else None
        judged = start >= first and avg is not None
        weeks.append({"開始": start.isoformat(), "終了": end.isoformat(), "日数": len(ss), "平均歩数": avg,
                      "動いていない": avg < limit if judged else None})
        end = start - timedelta(days=1)
    return {"週ごと": weeks}
