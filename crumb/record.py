"""crumb-tracker 이벤트 기록 코어.

모든 수집기(zsh 훅, Claude Code 훅, git 훅)가 이 모듈을 통해 기록한다.
DB는 레포가 아니라 ~/.tracker/log.db 에 저장된다.
"""

import argparse
import json
import os
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path(os.environ.get("CRUMB_HOME", Path.home() / ".tracker"))
DB_PATH = DATA_DIR / "log.db"
SCHEMA = Path(__file__).resolve().parent.parent / "store" / "schema.sql"

# 저장 전에 지워야 하는 비밀값 패턴. 새 패턴이 보이면 여기에 추가한다.
SECRET_PATTERNS = [
    (re.compile(r"\bsk-[A-Za-z0-9_\-]{16,}"), "<REDACTED:openai>"),
    (re.compile(r"\bsk-ant-[A-Za-z0-9_\-]{16,}"), "<REDACTED:anthropic>"),
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}"), "<REDACTED:github>"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "<REDACTED:aws>"),
    (re.compile(r"\bAIza[A-Za-z0-9_\-]{30,}"), "<REDACTED:gcp>"),
    (re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._\-]{16,}"), "<REDACTED:bearer>"),
    (re.compile(r"(?i)\b(export\s+)?([A-Z_]*(?:TOKEN|SECRET|PASSWORD|APIKEY|API_KEY))\s*=\s*\S+"),
     r"\1\2=<REDACTED>"),
]


def redact(text):
    """비밀값으로 보이는 문자열을 치환한다. 수집 시점에 거르는 게 핵심."""
    if not text:
        return text
    for pattern, replacement in SECRET_PATTERNS:
        text = pattern.sub(replacement, text)
    return text


def connect():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=5.0)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.executescript(SCHEMA.read_text())
    return conn


def write_event(source, kind, command=None, exit_code=None, cwd=None,
                session_id=None, duration_ms=None, payload=None):
    conn = connect()
    with conn:
        conn.execute(
            "INSERT INTO events (ts, source, session_id, cwd, kind, command,"
            " exit_code, duration_ms, payload) VALUES (?,?,?,?,?,?,?,?,?)",
            (
                datetime.now(timezone.utc).isoformat(timespec="seconds"),
                source,
                session_id,
                cwd,
                kind,
                redact(command),
                exit_code,
                duration_ms,
                redact(json.dumps(payload, ensure_ascii=False)) if payload else None,
            ),
        )
    conn.close()


def main():
    parser = argparse.ArgumentParser(prog="crumb-record")
    parser.add_argument("source")
    parser.add_argument("--kind", default="command")
    parser.add_argument("--cmd")
    parser.add_argument("--exit", type=int, dest="exit_code")
    parser.add_argument("--cwd")
    parser.add_argument("--session")
    parser.add_argument("--duration", type=int)
    args = parser.parse_args()

    try:
        write_event(
            source=args.source,
            kind=args.kind,
            command=args.cmd,
            exit_code=args.exit_code,
            cwd=args.cwd,
            session_id=args.session,
            duration_ms=args.duration,
        )
    except Exception:
        # 기록 실패가 셸을 망가뜨리면 안 된다. 조용히 넘어간다.
        sys.exit(0)


if __name__ == "__main__":
    main()
