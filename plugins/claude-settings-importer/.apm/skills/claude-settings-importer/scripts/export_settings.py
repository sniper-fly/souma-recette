#!/usr/bin/env python3
"""~/.claude/ または .claude/ の設定をAPM形式のパッケージへ変換して書き出す。

変換内容:
  skills/*          -> .apm/skills/            (symlink解決してそのままコピー)
  settings.json.hooks -> .apm/hooks/hooks.json (Claudeネイティブ形式のまま。参照スクリプトも同梱)
  rules/*.md         -> .apm/instructions/*.instructions.md (applyTo/description付与)
  それ以外のsettings.jsonキー(env/permissions/statusLine/model等)
                      -> apm.yml の x-claude-settings に構造化保持
  settings.json全体   -> raw/settings.json にバイト単位で保存(ロスレス保証の二重化)
"""

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

CLAUDE_ONLY_KEYS = {"hooks"}
PRESERVED_TOP_LEVEL_KEYS = set()  # 全キーをx-claude-settingsへ退避(hooksのみ別扱い)

HOOK_SCRIPT_PATTERN = re.compile(r"(?:^|[\s\"'])(\.?/?[\w./-]*\.sh)")


def copy_tree_resolving_symlinks(src: Path, dst: Path) -> None:
    if not src.exists():
        return
    dst.mkdir(parents=True, exist_ok=True)
    for entry in src.iterdir():
        target = dst / entry.name
        resolved = entry.resolve()
        if resolved.is_dir():
            copy_tree_resolving_symlinks(resolved, target)
        elif resolved.is_file():
            shutil.copy2(resolved, target)


def extract_hook_script_paths(hooks_config: dict) -> set:
    scripts = set()
    for hook_list in hooks_config.get("hooks", {}).values():
        for entry in hook_list:
            for hook in entry.get("hooks", []):
                command = hook.get("command", "")
                for match in HOOK_SCRIPT_PATTERN.finditer(command):
                    scripts.add(match.group(1).lstrip("./"))
    return scripts


def convert_hooks(settings: dict, claude_dir: Path, out_dir: Path) -> None:
    hooks_config = settings.get("hooks")
    if not hooks_config:
        return
    hooks_out = out_dir / ".apm" / "hooks"
    hooks_out.mkdir(parents=True, exist_ok=True)
    (hooks_out / "hooks.json").write_text(
        json.dumps({"hooks": hooks_config}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    script_names = extract_hook_script_paths({"hooks": hooks_config})
    if not script_names:
        return
    scripts_out = hooks_out / "scripts"
    scripts_out.mkdir(exist_ok=True)
    source_scripts_dir = claude_dir / "hooks"
    for name in script_names:
        candidate = source_scripts_dir / Path(name).name
        if candidate.exists():
            shutil.copy2(candidate.resolve(), scripts_out / Path(name).name)


def convert_rules_to_instructions(claude_dir: Path, out_dir: Path) -> None:
    rules_dir = claude_dir / "rules"
    if not rules_dir.is_dir():
        return
    instructions_out = out_dir / ".apm" / "instructions"
    instructions_out.mkdir(parents=True, exist_ok=True)
    for rule_file in sorted(rules_dir.glob("*.md")):
        body = rule_file.read_text(encoding="utf-8")
        first_line = next((l.strip("# ").strip() for l in body.splitlines() if l.strip()), rule_file.stem)
        frontmatter = (
            "---\n"
            f"description: \"{first_line}\"\n"
            "applyTo: \"**\"\n"
            "---\n\n"
        )
        dest = instructions_out / f"{rule_file.stem}.instructions.md"
        dest.write_text(frontmatter + body, encoding="utf-8")


def build_apm_yml(name: str, description: str, settings: dict, out_dir: Path) -> None:
    remaining = {k: v for k, v in settings.items() if k not in CLAUDE_ONLY_KEYS}
    manifest = {
        "name": name,
        "version": "1.0.0",
        "description": description,
    }
    if remaining:
        manifest["x-claude-settings"] = remaining
    # JSONはYAML 1.2のフロー構文の部分集合として妥当なので、
    # 追加の依存(PyYAML等)なしで有効なapm.ymlを生成できる。
    (out_dir / "apm.yml").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def export(claude_dir: Path, out_dir: Path, name: str, description: str) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    settings_path = claude_dir / "settings.json"
    settings = {}
    if settings_path.exists():
        settings = json.loads(settings_path.read_text(encoding="utf-8"))
        raw_out = out_dir / "raw"
        raw_out.mkdir(exist_ok=True)
        shutil.copy2(settings_path, raw_out / "settings.json")

    copy_tree_resolving_symlinks(claude_dir / "skills", out_dir / ".apm" / "skills")
    convert_hooks(settings, claude_dir, out_dir)
    convert_rules_to_instructions(claude_dir, out_dir)
    build_apm_yml(name, description, settings, out_dir)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--claude-dir", required=True, help="変換元の .claude ディレクトリ(例: ~/.claude または ./.claude)")
    parser.add_argument("--output", required=True, help="出力先ディレクトリ(APMパッケージのルート)")
    parser.add_argument("--name", required=True, help="生成するapm.ymlのパッケージ名")
    parser.add_argument("--description", default="Exported personal/project Claude Code settings (APM package)")
    args = parser.parse_args()

    claude_dir = Path(args.claude_dir).expanduser().resolve()
    if not claude_dir.is_dir():
        print(f"エラー: {claude_dir} が見つかりません", file=sys.stderr)
        sys.exit(1)

    out_dir = Path(args.output).expanduser().resolve()
    export(claude_dir, out_dir, args.name, args.description)
    print(f"書き出し完了: {out_dir}")


if __name__ == "__main__":
    main()
