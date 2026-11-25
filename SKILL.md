---
name: diet-process-jayt-core-logic-skill
description: "文脈: ダイエット進捗。種類: 中核判断。使う場面: 名前で指名されたときだけ使い、会話の内容からは選ばない。"
metadata:
  skill-version: "0.19.5"
  design-name: "人の判断を切り出すAgent Skillsの設計"
  design-version: "6.0.1"
  design-url: "https://app.notion.com/p/3eaf2fd6925e8102b86fee3b6b3dd5a3"
---

# 索引

| 判断名 | 扱うこと | ファイル | 依存する判断 | 計算 |
|---|---|---|---|---|
| 起床・就寝時刻の選び方 | 就寝・起床の時刻を、複数ある睡眠の記録のどれから取るか | [sleep-time-source.md](references/sleep-time-source.md) | — | ○ |
| 採用する体重記録 | 1日に複数ある体重の記録のどれを採るか | [measurement.md](references/measurement.md) | `sleep-time-source.md` | ○ |
| 体重の増減 | 体重の増減をどう読むか | [weight-trend.md](references/weight-trend.md) | `measurement.md` | ○ |
| 目標達成までの見積もり | 目標体重まで、今の増減でどれくらいかかるか | [goal-estimate.md](references/goal-estimate.md) | `weight-trend.md` | ○ |
| 進捗の良し悪し | 体重の進捗が良いか、良くないか | [progress.md](references/progress.md) | `weight-trend.md` | ○ |
| 体組成 | 体組成の数値を判断に使うか | [body-composition.md](references/body-composition.md) | — | — |
| 筋トレと有酸素運動 | 筋トレや有酸素運動が、体重の減量にどう関わるか | [strength-training.md](references/strength-training.md) | — | — |
| 食生活の異常検知 | 食事の記録から、食生活の異常をどう検知するか | [meal-pattern.md](references/meal-pattern.md) | — | ○ |
| あまり動いていない週 | 日々の歩数から、あまり動いていない週をどう検知するか | [low-activity.md](references/low-activity.md) | — | ○ |

# このスキルの設計上の決まりごと

1. このスキルは判断を答えるだけで、判断の対象もデータも持たない。対象の値は、材料の写しとして受け取る。データを取りに行かず、保存もせず、IDも受け取らない。
2. 答える範囲は、聞きたい事を索引の「扱うこと」と照らして決める。索引の「依存する判断」にある判断を、先に出す。
3. 判断ファイルの「求める材料」がそろわなければ答えない。計算がある判断は、`uv run <skill-dir>/scripts/judge.py <判断> <材料.json>` で計算する。<判断> は `references/` のファイル名。依存する判断の材料も、一緒に渡す。
4. 答えは、指定された形にそろえ、理由と組にして返す。
5. 中核判断は、判断ファイルで答えられなければ、一般論で答えず「判断が無い」と返す。「未決」に当たったら、未決であることと、決めるまでの暫定の扱いを含める。一般的な業務知識は、判断ファイルに無いことを一般知識で補ってよい。
