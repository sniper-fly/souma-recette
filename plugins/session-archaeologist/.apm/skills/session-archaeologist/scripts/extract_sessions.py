#!/usr/bin/env python3
"""
Claude Codeのセッションログからトピックに関連するセッションを検索・抽出する。

Usage:
    # 関連セッションの検索
    python extract_sessions.py --project-path /path/to/project --keywords "keyword1,keyword2"

    # 特定セッションのメッセージ抽出
    python extract_sessions.py --project-path /path/to/project --keywords "" --session-id <uuid>

    # 検索 + メッセージ抽出を一括実行
    python extract_sessions.py --project-path /path/to/project --keywords "keyword1,keyword2" --extract
"""

import json
import os
import sys
import argparse
from pathlib import Path
from datetime import datetime


def find_session_dir(project_path: str) -> Path:
    """プロジェクトパスからClaude Codeのセッションディレクトリを特定する。

    Claude Code は ~/.claude/projects/ 配下に、プロジェクトの絶対パスの
    スラッシュをハイフンに置換した名前のディレクトリを作成する。
    例: /home/user/work/project -> -home-user-work-project
    """
    normalized = project_path.rstrip("/")
    dir_name = normalized.replace("/", "-")
    return Path.home() / ".claude" / "projects" / dir_name


def load_sessions_index(session_dir: Path) -> list[dict] | None:
    """sessions-index.json を読み込み、セッション情報のリストを返す。"""
    index_path = session_dir / "sessions-index.json"
    if not index_path.exists():
        return None
    try:
        with open(index_path, "r") as f:
            data = json.load(f)
        return data.get("entries", [])
    except (json.JSONDecodeError, IOError):
        return None


def search_sessions(
    session_dir: Path, keywords: list[str], max_sessions: int = 30
) -> list[dict]:
    """JONLファイルをキーワードで検索し、マッチするセッションを返す。"""
    results = []

    for jsonl_file in sorted(session_dir.glob("*.jsonl")):
        if jsonl_file.name == "sessions-index.json":
            continue

        try:
            with open(jsonl_file, "r") as f:
                content = f.read()

            if any(kw.lower() in content.lower() for kw in keywords):
                stat = jsonl_file.stat()
                # 最初の実質的なユーザーメッセージを取得
                first_prompt = ""
                with open(jsonl_file, "r") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            obj = json.loads(line)
                            if obj.get("type") == "user":
                                msg = obj.get("message", {})
                                content_field = msg.get("content", "")
                                if isinstance(content_field, list):
                                    for block in content_field:
                                        if (
                                            isinstance(block, dict)
                                            and block.get("type") == "text"
                                        ):
                                            first_prompt = block["text"][:300]
                                            break
                                elif isinstance(content_field, str):
                                    text = content_field.strip()
                                    # コマンド系やシステムメッセージはスキップ
                                    if (
                                        text
                                        and not text.startswith("<local-command")
                                        and not text.startswith("<command-name>")
                                        and len(text) > 10
                                    ):
                                        first_prompt = text[:300]
                                if first_prompt:
                                    break
                        except json.JSONDecodeError:
                            continue

                results.append(
                    {
                        "session_id": jsonl_file.stem,
                        "file": str(jsonl_file),
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        "first_prompt": first_prompt,
                    }
                )
        except (IOError, UnicodeDecodeError):
            continue

    results.sort(key=lambda x: x["modified"])
    return results[:max_sessions]


def extract_messages(
    jsonl_path: str, max_assistant_chars: int = 3000
) -> list[dict]:
    """JSONLファイルからhuman/assistantメッセージを抽出する。

    tool_use や tool_result の大きな出力はスキップし、
    ユーザーの指示とAIの主要な判断・応答のみを返す。
    """
    messages = []
    try:
        with open(jsonl_path, "r") as f:
            for line_num, line in enumerate(f):
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    msg_type = obj.get("type")

                    if msg_type == "user":
                        msg = obj.get("message", {})
                        content = msg.get("content", "")
                        if isinstance(content, list):
                            texts = []
                            for block in content:
                                if (
                                    isinstance(block, dict)
                                    and block.get("type") == "text"
                                ):
                                    texts.append(block["text"])
                            content = "\n".join(texts)
                        elif not isinstance(content, str):
                            content = ""
                        # システムメッセージやコマンドノイズを除去
                        stripped = content.strip()
                        noise_prefixes = (
                            "<local-command-caveat>",
                            "<local-command-stdout>",
                            "<command-name>/clear",
                            "<command-name>/compact",
                        )
                        if (
                            stripped
                            and len(stripped) > 5
                            and not any(
                                stripped.startswith(p) for p in noise_prefixes
                            )
                        ):
                            messages.append(
                                {
                                    "role": "user",
                                    "content": content[:5000],
                                    "line": line_num,
                                }
                            )

                    elif msg_type == "assistant":
                        msg = obj.get("message", {})
                        content = msg.get("content", [])
                        texts = []
                        tool_uses = []
                        if isinstance(content, list):
                            for block in content:
                                if isinstance(block, dict):
                                    if block.get("type") == "text":
                                        text = block["text"]
                                        if len(text) > 50:
                                            texts.append(
                                                text[:max_assistant_chars]
                                            )
                                    elif block.get("type") == "tool_use":
                                        tool_name = block.get("name", "")
                                        tool_uses.append(tool_name)

                        entry = {"role": "assistant", "line": line_num}
                        if texts:
                            entry["content"] = "\n---\n".join(texts)
                        if tool_uses:
                            entry["tools_used"] = tool_uses
                        if texts or tool_uses:
                            messages.append(entry)

                except json.JSONDecodeError:
                    continue
    except (IOError, UnicodeDecodeError) as e:
        return [{"role": "error", "content": str(e), "line": 0}]

    return messages


def main():
    parser = argparse.ArgumentParser(
        description="Claude Codeセッションログの検索・抽出"
    )
    parser.add_argument(
        "--project-path", required=True, help="プロジェクトディレクトリのパス"
    )
    parser.add_argument(
        "--keywords",
        required=True,
        help="カンマ区切りの検索キーワード",
    )
    parser.add_argument(
        "--max-sessions",
        type=int,
        default=30,
        help="最大セッション数 (default: 30)",
    )
    parser.add_argument(
        "--extract",
        action="store_true",
        help="マッチしたセッションのメッセージも抽出する",
    )
    parser.add_argument(
        "--session-id",
        help="特定セッションのメッセージを抽出する",
    )

    args = parser.parse_args()

    session_dir = find_session_dir(args.project_path)

    if not session_dir.exists():
        print(
            json.dumps(
                {
                    "error": f"Session directory not found: {session_dir}",
                    "hint": "プロジェクトパスが正しいか確認してください",
                }
            )
        )
        sys.exit(1)

    if args.session_id:
        jsonl_path = session_dir / f"{args.session_id}.jsonl"
        if not jsonl_path.exists():
            print(
                json.dumps(
                    {"error": f"Session file not found: {jsonl_path}"}
                )
            )
            sys.exit(1)
        messages = extract_messages(str(jsonl_path))
        print(
            json.dumps(
                {"session_id": args.session_id, "messages": messages},
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        keywords = [k.strip() for k in args.keywords.split(",") if k.strip()]
        if not keywords:
            print(json.dumps({"error": "キーワードを1つ以上指定してください"}))
            sys.exit(1)

        sessions = search_sessions(session_dir, keywords, args.max_sessions)

        output = {
            "project_path": args.project_path,
            "session_dir": str(session_dir),
            "keywords": keywords,
            "matching_sessions": len(sessions),
            "sessions": sessions,
        }

        if args.extract:
            for session in sessions:
                session["messages"] = extract_messages(session["file"])

        print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
