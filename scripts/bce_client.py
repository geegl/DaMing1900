#!/usr/bin/env python3
import argparse
import http.client
import json
import os
import sqlite3
import ssl
import time
import sys
from datetime import datetime
import urllib.error
import urllib.request
from pathlib import Path

import requests


def load_current_provider_id() -> str:
    settings_path = Path.home() / ".cc-switch" / "settings.json"
    data = json.loads(settings_path.read_text())
    provider_id = data.get("currentProviderClaude")
    if not provider_id:
        raise RuntimeError("CC Switch 未找到 currentProviderClaude")
    return provider_id


def load_provider_env(provider_id: str) -> tuple[str, dict]:
    db_path = Path.home() / ".cc-switch" / "cc-switch.db"
    conn = sqlite3.connect(str(db_path))
    row = conn.execute(
        "select name, settings_config from providers where id=? and app_type='claude'",
        (provider_id,),
    ).fetchone()
    if not row:
        raise RuntimeError(f"未找到 Claude provider: {provider_id}")
    provider_name = row[0]
    conf = json.loads(row[1])
    env = conf.get("env", {})
    if "ANTHROPIC_AUTH_TOKEN" not in env or "ANTHROPIC_BASE_URL" not in env:
        raise RuntimeError("当前 provider 缺少 BCE 所需环境变量")
    return provider_name, env


def request_text(base_url: str, token: str, model: str, prompt: str, max_tokens: int) -> str:
    body = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
    }
    url = base_url.rstrip("/") + "/v1/messages?beta=true"
    req = urllib.request.Request(
        url,
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={
            "content-type": "application/json",
            "x-api-key": token,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )
    last_error = None
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, context=ssl.create_default_context(), timeout=240) as resp:
                data = json.loads(resp.read().decode("utf-8", "ignore"))
            break
        except (
            http.client.RemoteDisconnected,
            TimeoutError,
            urllib.error.URLError,
            ssl.SSLError,
        ) as exc:
            last_error = exc
            if attempt == 5:
                data = None
                break
            time.sleep(min(12, 2 * (attempt + 1)))
    else:
        raise last_error

    if data is None:
        headers = {
            "content-type": "application/json",
            "x-api-key": token,
            "anthropic-version": "2023-06-01",
        }
        for attempt in range(3):
            try:
                resp = requests.post(url, headers=headers, json=body, timeout=240)
                resp.raise_for_status()
                data = resp.json()
                break
            except requests.RequestException as exc:
                last_error = exc
                if attempt == 2:
                    raise
                time.sleep(min(12, 3 * (attempt + 1)))

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
    parser.add_argument("--output-meta-file", help="输出元数据文件")
    parser.add_argument("--max-tokens", type=int, default=12000, help="max_tokens")
    parser.add_argument("--provider-id", help="可选，显式指定 Claude provider")
    parser.add_argument("--require-provider-name", default="BCE", help="要求的 provider 名称")
    args = parser.parse_args()

    prompt = Path(args.prompt_file).read_text()
    provider_id = args.provider_id or load_current_provider_id()
    provider_name, env = load_provider_env(provider_id)
    if args.require_provider_name and provider_name != args.require_provider_name:
        raise RuntimeError(
            f"当前 provider 不是 {args.require_provider_name}，而是 {provider_name}；禁止继续写作"
        )
    if os.environ.get("BCE_DEBUG_PROVIDER") == "1":
        print(
            json.dumps(
                {
                    "provider_id": provider_id,
                    "provider_name": provider_name,
                    "base_url": env["ANTHROPIC_BASE_URL"],
                    "model": args.model,
                },
                ensure_ascii=False,
            ),
            file=sys.stderr,
        )
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
    if args.output_meta_file:
        meta_path = Path(args.output_meta_file)
        meta_path.parent.mkdir(parents=True, exist_ok=True)
        meta_path.write_text(
            json.dumps(
                {
                    "provider_id": provider_id,
                    "provider_name": provider_name,
                    "base_url": env["ANTHROPIC_BASE_URL"],
                    "model": args.model,
                    "prompt_file": str(Path(args.prompt_file).resolve()),
                    "output_file": str(output_path.resolve()),
                    "output_chars": len(text),
                    "generated_at": datetime.now().isoformat(),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    print(output_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
