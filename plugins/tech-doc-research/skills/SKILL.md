---
name: research-latest-docs
description: This skill should be used when the user asks to "generate technical documentation from requirements", "extract technologies from requirements document", "create tech research documents", "analyze requirements for tech stack", or needs to identify and document technologies specified in a requirements document.
version: 0.1.0
disable-model-invocation: true
---

# 技術ドキュメント生成スキル

要件定義書から実装に必要な技術を抽出し、各技術の調査ドキュメントを生成する。

## 入力

- 要件定義書のパス（第一引数）
- 出力先のディレクトリ（第二引数）

## 処理手順

### ステップ1: 要件定義書の読み込みと技術抽出

要件定義書を読み込み、以下のカテゴリに該当する技術を特定する：

- 外部ライブラリ・パッケージ
- フレームワーク
- 外部API・サービス
- データベース・ストレージ技術
- 認証・認可方式
- その他の専門的技術スタック

### ステップ2: 技術一覧の出力

抽出した技術を一覧化し、AskUserQuestionでユーザーに確認を求める。

### ステップ3: 技術ドキュメント生成

各技術について tech-docs-researcher エージェントを起動する：

- 第一引数: ライブラリ名または技術名
- 第二引数: 要件定義書のパス

## 出力

各技術のドキュメントは第二引数で指定されたディレクトリ配下に生成される。
