#!/usr/bin/env python3
"""Claude Code PostToolUse 훅.

~/.claude/settings.json 에 등록하면 모든 툴 호출이 crumb DB에 쌓인다.

  {
    "hooks": {
      "PostToolUse": [
        {
          "matcher": "*",
          "hooks": [
            {
              "type": "command",
              "command": "python3 /path/to/crumb-tracker/collectors/claude_hook.py",
              "async": true
            }
          ]
        }
      ]
    }
  }

훅은 무슨 일이 있어도 exit 0 을 반환해야 한다. 안 그러면 Claude Code 작업을 막는다.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    from crumb.record import write_event
except Exception:
    sys.exit(0)


def main():
    try:
        event = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    tool_name = event.get("tool_name")
    tool_input = event.get("tool_input") or {}
    tool_response = event.get("tool_response") or {}

    # Bash 툴은 명령어를 command 컬럼에 따로 빼둔다. 나중에 셸 이벤트와 같이 다루기 위해서.
    command = tool_input.get("command") if tool_name == "Bash" else None

    is_error = bool(tool_response.get("is_error")) if isinstance(tool_response, dict) else False

    write_event(
        source="claude_code",
        kind="tool_use",
        command=command,
        exit_code=1 if is_error else 0,
        cwd=event.get("cwd"),
        session_id=event.get("session_id"),
        payload={
            "tool": tool_name,
            "input": tool_input,
            "transcript": event.get("transcript_path"),
        },
    )


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
