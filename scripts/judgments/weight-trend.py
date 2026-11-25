"""体重の増減（references/weight-trend.md）の計算。"""
from datetime import date, timedelta

from _common import _mean, load, val


def _rounded(x):
    return round(x, 2) if x is not None else None


def _gap(latest, base):
    return round(latest - base, 2) if latest is not None and base is not None else None


def _period_change(s, days, unit, min_ratio):
    """直近の期間とその前の期間の平均体重を比べる。期間は最新の記録日から遡る。"""
    last = date.fromisoformat(s[-1]["日付"])

    def period(offset):
        end = last - timedelta(days=offset)
        start = end - timedelta(days=days - 1)
        ws = [x["体重"] for x in s if start <= date.fromisoformat(x["日付"]) <= end]
        return start, end, ws

    def row(p):
        return {"開始": p[0].isoformat(), "終了": p[1].isoformat(),
                "平均体重": _rounded(_mean(p[2])), "測定日数": len(p[2])}
    recent, before = period(0), period(days)
    enough = min(len(recent[2]), len(before[2])) > days * min_ratio
    return {"直近": row(recent), "その前": row(before),
            "差": _gap(_mean(recent[2]), _mean(before[2])) if enough else None, "単位": unit}


def judge(m):
    name = "weight-trend"
    s = load("measurement").judge(m)["日次系列"]
    if len(s) < 2:
        return {"計測日数": len(s)}
    min_ratio = val(name, "差を出さない測定日数の割合")
    return {
        "短期のトレンド": _period_change(s, val(name, "短期の期間"), "kg／2週間", min_ratio),
        "中期のトレンド": _period_change(s, val(name, "中期の期間"), "kg／1月間", min_ratio),
        "長期のトレンド": _period_change(s, val(name, "長期の期間"), "kg／2月間", min_ratio),
        "最新": {"日付": s[-1]["日付"], "体重": s[-1]["体重"]},
    }
