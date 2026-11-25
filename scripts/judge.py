#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///
"""diet-process-jayt-core-logic-skill の計算の入口。判断に要る数値を、材料のJSONから出す。

Usage:
  uv run judge.py <判断> <材料.json>
  uv run judge.py all <材料.json>      # 材料がそろっている判断をすべて計算する

<判断> は references/ のファイル名（拡張子なし）。計算を持つのは、judgments/ に同じ名前の
ファイルがある判断だけ。入口はこの1本で、失敗の返し方と依存先の読み込みをここと
judgments/_common.py だけが持つ。頼まれた判断と、その依存先のファイルだけを読み込む。

**判断定数（窓の幅・しきい値）はスクリプトに書かない。** references/<判断>.md の「## 判断定数」の表を
実行時に読む。人が読む判断と、計算が使う値を1か所にそろえるため。

材料のJSONのキーと形は、各判断の「## 求める材料」の表にある。足りない材料は、
必須なら {"足りない材料": [...]} を標準出力に出して終了コード2で止まり、
必須でなければ計算できる範囲を返して、結果の "足りない材料" に名前を入れる。
使い方の誤りは標準エラーに出して終了コード1。他のスキルには依存しない（標準ライブラリだけで動く）。
"""
import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "judgments"))
from _common import MissingMaterial, available, load  # noqa: E402


def main():
    names = available()
    if len(sys.argv) != 3 or sys.argv[1] not in (*names, "all"):
        sys.exit(f"Usage: judge.py <{'|'.join(names)}|all> <材料.json>")
    with open(sys.argv[2], encoding="utf-8") as f:
        m = json.load(f)
    targets = names if sys.argv[1] == "all" else [sys.argv[1]]
    out = {}
    for key in targets:
        try:
            out[key] = load(key).judge(m)
        except MissingMaterial as e:
            if sys.argv[1] != "all":
                print(json.dumps({"足りない材料": [str(e)]}, ensure_ascii=False))
                sys.exit(2)
            out[key] = {"計算できない": str(e)}
    json.dump(out if sys.argv[1] == "all" else out[sys.argv[1]],
              sys.stdout, ensure_ascii=False, indent=2)
    print()


if __name__ == "__main__":
    main()
