"""diet-process-jayt-core-logic-skill の計算の共通の部品。

足りない材料の返し方（MissingMaterial・need）、判断定数の読み方（values・val）、
依存先の読み込み（load）を、すべての判断の計算がここから使う。
判断ごとの計算は judgments/<判断>.py に置き、名前を references/<判断>.md とそろえる。
"""
import importlib.util
import os

JUDGMENTS_DIR = os.path.dirname(os.path.abspath(__file__))
REF_DIR = os.path.normpath(os.path.join(JUDGMENTS_DIR, "..", "..", "references"))


class MissingMaterial(Exception):
    """必須の材料が無い。呼び出し側に、何が足りないかを返す。"""


_values = {}


def values(name):
    """references/<name>.md の「## 判断定数」の表（| 名前 | 値 | 単位 |）を {名前: 値} で返す。"""
    if name in _values:
        return _values[name]
    out, in_section = {}, False
    with open(os.path.join(REF_DIR, f"{name}.md"), encoding="utf-8") as f:
        for line in f:
            if line.startswith("## "):
                in_section = line.strip() == "## 判断定数"
                continue
            if not in_section or not line.startswith("|"):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if cells[0] == "名前" or set(cells[0]) <= set("-: "):
                continue
            out[cells[0]] = _number(cells[1])
    _values[name] = out
    return out


def _number(s):
    for cast in (int, float):
        try:
            return cast(s)
        except ValueError:
            pass
    return s


def val(name, key):
    v = values(name)
    if key not in v:
        raise KeyError(f"references/{name}.md の「## 判断定数」の表に「{key}」が無い")
    return v[key]


def need(m, key, judgment):
    if m.get(key) is None:
        raise MissingMaterial(f"{judgment}: 必須の材料「{key}」が無い")
    return m[key]


def _mean(ws):
    """測定できた分だけの平均。欠測日は補完しない。"""
    return sum(ws) / len(ws) if ws else None


# --- 依存先の読み込み -------------------------------------------------------------
_loaded = {}


def available():
    """計算を持つ判断の名前（judgments/ のファイル名から拡張子を除いたもの）。"""
    return sorted(f[:-3] for f in os.listdir(JUDGMENTS_DIR) if f.endswith(".py") and not f.startswith("_"))


def load(name):
    """judgments/<name>.py を読み込む。頼まれた判断と、その依存先だけを読む。"""
    if name not in _loaded:
        path = os.path.join(JUDGMENTS_DIR, f"{name}.py")
        spec = importlib.util.spec_from_file_location(f"judgment_{name.replace('-', '_')}", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _loaded[name] = module
    return _loaded[name]
