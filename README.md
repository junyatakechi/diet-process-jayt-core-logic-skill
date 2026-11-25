# diet-process-jayt-core-logic-skill

ダイエットの進捗をどう読むかについて、作成者が下した中核判断を、理由とともに持つロジックスキル。
体重・体組成・スマートリングの指標・食事の記録を材料として受け取り、答えと理由を返す。

## 必要なもの

- [Claude Code](https://docs.claude.com/en/docs/claude-code/overview)
- Python 3.11以上と [uv](https://docs.astral.sh/uv/)（判断の計算に使う）

## インストール

```bash
git clone https://github.com/junyatakechi/diet-process-jayt-core-logic-skill.git ~/.claude/skills/diet-process-jayt-core-logic-skill
```

特定のプロジェクトだけで使うなら、`<プロジェクト>/.claude/skills/` の中でクローンする。

## セットアップ

なし。

## 使い方

主に、アプリケーションスキルから呼ばれる。
直接聞くときも、`/diet-process-jayt-core-logic-skill` で名前を指名する。指名しないと、このスキルは読み込まれない。

- 「/diet-process-jayt-core-logic-skill 7日分の体重で、停滞と言っていい？」
- 「/diet-process-jayt-core-logic-skill 体組成計の筋肉量は当てになる？」
