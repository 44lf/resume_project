from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


# 项目根目录：.../app/config/settings.py -> parents[2] = D:/git_bash
BASE_DIR = Path(__file__).resolve().parents[2]
ENV_PATH = BASE_DIR / ".env"

# 显式加载 .env（对 uvicorn / reload 子进程都稳定）
load_dotenv(dotenv_path=ENV_PATH)


def _required(name: str) -> str:
    value = os.getenv(name)
    if value is None or value == "":
        raise RuntimeError(f"Missing required env var: {name} (env file: {ENV_PATH})")
    return value


# 数据库
DB_URL: str = _required("DB_URL")

# 是否自动建表（允许有安全默认）
DB_GENERATE_SCHEMAS: bool = os.getenv("DB_GENERATE_SCHEMAS", "false").lower() == "true"
