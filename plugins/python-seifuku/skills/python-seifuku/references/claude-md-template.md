# CLAUDE.md テンプレート

以下の内容を `CLAUDE.md` として配置する。

```markdown
PostToolUse hookによって型、リンタ、フォーマッタ、テストのチェックが行われるので明示的な実行は検証手順には含めない
実装後の手動テストは不要
検証手順には臨機応変に設計レベル、統合レベルの観点を含める。例えば以下の観点を含めること:

- 依存方向の違反がないか（Domain→Application/Infrastructure方向のimportがないか）
- 設計ドキュメントとの整合性

以下はテスト観点に含めない

- 自明なこと
- Pydanticなど外部ライブラリで保証されている機能(frozen検証など)

プライベート関数は乱立させない。関心が異なるモジュールは別クラス、別モジュールにする。

ユーザーに迎合しない。反証できる点がある場合はAskUserQuestionなどを利用し、ユーザーに確認を求める

dataclassではなく、pydanticのBaseModelを利用する。

不明な点があればAskUserQuestionを利用し、ユーザーに確認を求める
```
