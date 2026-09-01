# crumb-tracker zsh collector
# ~/.zshrc 맨 아래에 다음 한 줄을 추가한다:
#   source /path/to/crumb-tracker/collectors/hook.zsh

zmodload zsh/datetime 2>/dev/null
autoload -Uz add-zsh-hook

# install.sh 가 기록한 절대경로를 읽는다.
# python3 을 그냥 부르면 다른 프로젝트의 venv 가 활성화된 터미널에서 기록이 실패한다.
[[ -f "${CRUMB_HOME:-$HOME/.tracker}/config.sh" ]] && source "${CRUMB_HOME:-$HOME/.tracker}/config.sh"

: ${CRUMB_REPO:=${0:A:h:h}}
: ${CRUMB_PY:=/usr/bin/env python3}
export CRUMB_SESSION="${CRUMB_SESSION:-$(date +%s)-$$}"

_crumb_preexec() {
  _CRUMB_CMD="$1"
  _CRUMB_START=$EPOCHREALTIME
}

_crumb_precmd() {
  local code=$?
  [[ -z "$_CRUMB_CMD" ]] && return
  local cmd="$_CRUMB_CMD"
  _CRUMB_CMD=""

  # 트래커 자기 자신은 기록하지 않는다
  [[ "$cmd" == crumb* ]] && return

  local dur=0
  if [[ -n "$_CRUMB_START" ]]; then
    dur=$(( (EPOCHREALTIME - _CRUMB_START) * 1000 ))
  fi

  # 백그라운드로 던져서 프롬프트가 느려지지 않게 한다
  ( "$CRUMB_PY" "$CRUMB_REPO/crumb/record.py" shell \
      --cmd "$cmd" --exit "$code" --cwd "$PWD" \
      --duration "${dur%.*}" --session "$CRUMB_SESSION" >/dev/null 2>>"${CRUMB_HOME:-$HOME/.tracker}/hook-errors.log" & ) 
}

add-zsh-hook preexec _crumb_preexec
add-zsh-hook precmd  _crumb_precmd
