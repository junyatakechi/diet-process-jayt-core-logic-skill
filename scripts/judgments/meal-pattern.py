"""食生活の異常検知（references/meal-pattern.md）の計算。"""
from datetime import date, timedelta

from _common import MissingMaterial, need, val


def _eat_day(x, boundary):
    """食事を数える日。境界（"HH:MM"）より前の記録は前日に数える。"""
    t = x.get("時刻")
    if t and t != "終日" and t < boundary:
        return (date.fromisoformat(x["日付"]) - timedelta(days=1)).isoformat()
    return x["日付"]


def _sittings(items):
    """時間帯が重なる食事を1回にまとめ、回ごとの記録の並びを返す。接する予定（終了==開始）は別の食事。"""
    groups = []
    for it in sorted(items, key=lambda c: (c.get("時刻") or "", c.get("終了") or "")):
        start, end = it.get("時刻"), it.get("終了") or it.get("時刻")
        if groups and start and groups[-1]["end"] and start < groups[-1]["end"]:
            groups[-1]["items"].append(it)
            groups[-1]["end"] = max(groups[-1]["end"], end or "")
        else:
            groups.append({"end": end, "items": [it]})
    return [g["items"] for g in groups]


def _merge_same_sitting(items):
    """時間帯が重なる食事を1件に畳む。"""
    return [" ＋ ".join(i["記録"] for i in g) for g in _sittings(items)]


def judge(m):
    name = "meal-pattern"
    meals = need(m, "食事", name)
    if not meals:
        raise MissingMaterial(f"{name}: 必須の材料「食事」に記録が1件も無い")
    markers = [x for x in (m.get("過食の表現") or []) if x]
    boundary = f"{int(val(name, '日付の境界')):02d}:00"
    meal_max, snack_max = val(name, "食事の回数の上限"), val(name, "間食の回数の上限")
    snack_words = [x for x in (m.get("間食の表現") or []) if x]

    def is_snack(x):
        return any(k in (x.get("記録") or "") for k in snack_words)

    by_day = {}
    for x in meals:
        by_day.setdefault(_eat_day(x, boundary), []).append(x)

    out = []
    for day in sorted(by_day):
        xs = by_day[day]
        main = _merge_same_sitting([x for x in xs if not is_snack(x)])
        snacks = [x["記録"] for x in xs if is_snack(x)]
        high = [x["記録"] for x in xs if any(k in x["記録"] for k in markers)]
        row = {"日付": day, "食事": main, "間食": snacks,
               "食事の回数の異常": len(main) > meal_max if snack_words else None,
               "間食の回数の異常": len(snacks) > snack_max if snack_words else None,
               "過食の表現がある記録": high}
        if not (row["食事の回数の異常"] or row["間食の回数の異常"] or high):
            continue
        out.append(row)
    result = {"当たる日": out,
              "外食": _eating_out(m, by_day, val(name, "異常とする外食の回数"), is_snack if snack_words else None),
              "間食": ({"週ごと": _weekly(by_day, is_snack, val(name, "異常とする間食の回数"))} if snack_words
                       else {"足りない材料": "間食の表現"}),
              "記録不足の日": _days_without_records(by_day)}
    if not snack_words:
        result["足りない材料"] = ["間食の表現"]
    return result


def _days_without_records(by_day):
    """最初の記録日から最新の記録日までで、食事・間食の記録が1回も無い日。"""
    first, last = date.fromisoformat(min(by_day)), date.fromisoformat(max(by_day))
    return [(first + timedelta(days=i)).isoformat() for i in range((last - first).days + 1)
            if (first + timedelta(days=i)).isoformat() not in by_day]


def _weekly(by_day, hit, limit):
    """最新の記録日から遡る7日間ごとに、hit に当たる記録を数え、limit 以上なら異常とする。"""
    first, last = date.fromisoformat(min(by_day)), date.fromisoformat(max(by_day))
    weeks, end = [], last
    while end >= first:
        start = end - timedelta(days=6)
        n = sum(hit(x) for d, xs in by_day.items()
                if start <= date.fromisoformat(d) <= end for x in xs)
        weeks.append({"開始": start.isoformat(), "終了": end.isoformat(), "回数": n, "異常": n >= limit})
        end = start - timedelta(days=1)
    return weeks


def _eating_out(m, by_day, limit, is_snack=None):
    """最新の記録日から遡る7日間ごとの外食の回数と、期間と7日間ごとの食事の、入手元ごとの回数。
    否定の表現がある記録は外食にしない。間食の表現が無ければ、期間の合計は出さない。"""
    yes = [x for x in (m.get("外食の表現") or []) if x]
    if not yes:
        return {"足りない材料": "外食の表現"}
    no = [x for x in (m.get("外食を否定する表現") or []) if x]

    def eating_out(x):
        r = x.get("記録") or ""
        return any(k in r for k in yes) and not any(k in r for k in no)
    out = {"週ごと": _weekly(by_day, eating_out, limit)}
    take_out = [x for x in (m.get("中食の表現") or []) if x]
    home = [x for x in (m.get("内食の表現") or []) if x]

    def has(x, words):
        return any(k in (x.get("記録") or "") for k in words)

    def source(sitting):
        """1回の食事の入手元。外食・中食・内食の順に、どれかの記録に当たれば、その入手元とする。"""
        if any(eating_out(x) for x in sitting):
            return "外食の食事"
        if take_out and any(has(x, take_out) for x in sitting):
            return "中食の食事"
        if home and any(has(x, home) for x in sitting):
            return "内食の食事"
        return "印の無い食事"

    if is_snack is not None:
        def count(days):
            sittings = [s for d in days for s in _sittings([x for x in by_day[d] if not is_snack(x)])]
            kinds = ["外食の食事"] + (["中食の食事"] if take_out else []) + (["内食の食事"] if home else [])
            if take_out and home:
                kinds.append("印の無い食事")
            got = [source(s) for s in sittings]
            return dict({"食事": len(sittings)}, **{k: got.count(k) for k in kinds})
        weeks = [dict(w_start_end, **count([d for d in by_day
                                             if w_start_end["開始"] <= d <= w_start_end["終了"]]))
                 for w_start_end in ({"開始": w["開始"], "終了": w["終了"]} for w in out["週ごと"])]
        out["期間の合計"] = dict(count(list(by_day)), 週ごと=weeks)
    if not no:
        out["足りない材料"] = "外食を否定する表現"
    return out
