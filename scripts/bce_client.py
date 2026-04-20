#!/usr/bin/env python3
import argparse
import json
import os
import sqlite3
import ssl
import sys
import urllib.request
from pathlib import Path


def load_current_provider_id() -> str:
    settings_path = Path.home() / ".cc-switch" / "settings.json"
    data = json.loads(settings_path.read_text())
    provider_id = data.get("currentProviderClaude")
    if not provider_id:
        raise RuntimeError("CC Switch 未找到 currentProviderClaude")
    return provider_id


def load_provider_env(provider_id: str) -> dict:
    db_path = Path.home() / ".cc-switch" / "cc-switch.db"
    conn = sqlite3.connect(str(db_path))
    row = conn.execute(
        "select settings_config from providers where id=? and app_type='claude'",
        (provider_id,),
    ).fetchone()
    if not row:
        raise RuntimeError(f"未找到 Claude provider: {provider_id}")
    conf = json.loads(row[0])
    env = conf.get("env", {})
    if "ANTHROPIC_AUTH_TOKEN" not in env or "ANTHROPIC_BASE_URL" not in env:
        raise RuntimeError("当前 provider 缺少 BCE 所需环境变量")
    return env


def request_text(base_url: str, token: str, model: str, prompt: str, max_tokens: int) -> str:
    body = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
    }
    req = urllib.request.Request(
        base_url.rstrip("/") + "/v1/messages?beta=true",
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={
            "content-type": "application/json",
            "x-api-key": token,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, context=ssl.create_default_context(), timeout=240) as resp:
        data = json.loads(resp.read().decode("utf-8", "ignore"))
    parts = []
    for item in data.get("content", []):
        if item.get("type") == "text":
            parts.append(item.get("text", ""))
    return "\n".join(parts).strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="通过当前 CC Switch Claude provider 调用 BCE 模型。")
    parser.add_argument("--model", required=True, help="BCE 模型名")
    parser.add_argument("--prompt-file", required=True, help="提示词文件")
    parser.add_argument("--output-file", required=True, help="输出文件")
    parser.add_argument("--max-tokens", type=int, default=12000, help="max_tokens")
    parser.add_argument("--provider-id", help="可选，显式指定 Claude provider")
    args = parser.parse_args()

    prompt = Path(args.prompt_file).read_text()
    provider_id = args.provider_id or load_current_provider_id()
    env = load_provider_env(provider_id)
    text = request_text(
        env["ANTHROPIC_BASE_URL"],
        env["ANTHROPIC_AUTH_TOKEN"],
        args.model,
        prompt,
        args.max_tokens,
    )
    output_path = Path(args.output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text)
    print(output_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
