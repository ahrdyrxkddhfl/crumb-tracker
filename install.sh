#!/usr/bin/env bash
# crumb-tracker 설치. 전용 venv를 만들고 훅을 등록한다.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOME_DIR="${CRUMB_HOME:-$HOME/.tracker}"
VENV="$HOME_DIR/venv"
CONFIG="$HOME_DIR/config.sh"
ZSHRC="$HOME/.zshrc"

echo "repo:  $REPO"
echo "data:  $HOME_DIR"

mkdir -p "$HOME_DIR"

# 시스템 파이썬으로 전용 venv를 만든다. 다른 프로젝트 venv에 오염되지 않게 하기 위함.
if [ ! -d "$VENV" ]; then
  echo "==> venv 생성"
  /usr/bin/env python3 -m venv "$VENV"
fi

echo "==> 패키지 설치 (editable)"
"$VENV/bin/pip" install --quiet --upgrade pip
"$VENV/bin/pip" install --quiet -e "$REPO"

# 훅이 쓸 절대경로를 파일로 박아둔다
cat > "$CONFIG" <<EOF
export CRUMB_REPO="$REPO"
export CRUMB_PY="$VENV/bin/python"
EOF
echo "==> config 기록: $CONFIG"

# .zshrc 등록 (중복 방지)
LINE="source \"$REPO/collectors/hook.zsh\""
if ! grep -qF "collectors/hook.zsh" "$ZSHRC" 2>/dev/null; then
  printf '\n# crumb-tracker\n%s\n' "$LINE" >> "$ZSHRC"
  echo "==> .zshrc 에 추가함"
else
  echo "==> .zshrc 이미 등록됨"
fi

cat <<EOF

설치 끝.

1) 새 터미널을 열고 아무 명령이나 쳐본 뒤:
     $VENV/bin/crumb status

2) Claude Code 훅은 ~/.claude/settings.json 에 직접 추가:

{
  "hooks": {
    "PostToolUse": [
      { "matcher": "*", "hooks": [
        { "type": "command",
          "command": "$VENV/bin/python $REPO/collectors/claude_hook.py",
          "async": true }
      ]}
    ]
  }
}

3) crumb 명령을 짧게 쓰려면 .zshrc 에:
     alias crumb="$VENV/bin/crumb"
EOF
