"""起床・就寝時刻の選び方（references/sleep-time-source.md）の計算。"""
from datetime import datetime

from _common import need


def _at(s):
    """ISO日時を、タイムゾーンを落とした日時にする（材料の時刻はすべて同じ現地時刻）。"""
    return datetime.fromisoformat(s).replace(tzinfo=None)


def _sleep_sections(m):
    """目覚めた日ごとに、一番早い起床の区間を選ぶ。就寝も、その区間の開始を使う。"""
    chosen = {}
    for n in m.get("夜間睡眠") or []:
        if not n.get("終了"):
            continue
        day = n["終了"][:10]
        if day not in chosen or _at(n["終了"]) < _at(chosen[day]["終了"]):
            chosen[day] = n
    return chosen


def judge(m):
    need(m, "夜間睡眠", "sleep-time-source")
    return {"就寝・起床の時刻": {day: {"就寝": n.get("開始"), "起床": n["終了"]}
                          for day, n in sorted(_sleep_sections(m).items())}}
